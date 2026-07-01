// ===== SCORING OCEAN — Likert T-score + dual profile =====

function pontuarItem(item, respostaLikert) {
  const raw = item.reversed ? (6 - respostaLikert) : respostaLikert;
  return raw;
}

function calcularRaw(respostas, bloco) {
  const raw = { O: 0, C: 0, E: 0, A: 0, N: 0 };
  const counts = { O: 0, C: 0, E: 0, A: 0, N: 0 };
  respostas.filter(r => r.bloco === bloco).forEach(r => {
    const item = ITEM_MAP[r.id];
    if (!item) return;
    raw[item.fator] += pontuarItem(item, r.valor);
    counts[item.fator]++;
  });
  const means = {};
  FACTORES_INTERNOS.forEach(f => {
    means[f] = counts[f] > 0 ? raw[f] / counts[f] : 3;
  });
  return { raw, means, counts };
}

function toTScore(mean, fator) {
  const { mean: mu, sd } = NORMS.domains[fator];
  const z = (mean - mu) / sd;
  return Math.round((50 + 10 * z) * 10) / 10;
}

function toPercentile(tScore) {
  const z = (tScore - 50) / 10;
  return Math.round(normalCDF(z) * 100);
}

function normalizeForUI(mean) {
  const normalized = ((mean - 3) / 2) * 10;
  return Math.max(-10, Math.min(10, Math.round(normalized * 10) / 10));
}

function calcularPerfil(respostas, bloco) {
  const { means } = calcularRaw(respostas, bloco);
  const internal = {};
  FACTORES_INTERNOS.forEach(f => {
    const tScore = toTScore(means[f], f);
    internal[f] = {
      mean: means[f],
      tScore,
      percentil: toPercentile(tScore),
      ui: normalizeForUI(means[f]),
      banda: classificarBandaT(tScore),
    };
  });
  const display = {};
  FATORES_DISPLAY.forEach(df => {
    const f = df === 'SE' ? 'N' : df;
    display[df] = invertForDisplay(f, internal[f]);
    display[df].banda = classificarBandaDisplay(f, internal[f].tScore);
  });
  return { internal, display };
}

function respostasLikertFromState() {
  return state.shuffled.map(q => ({
    id: q.id,
    bloco: q.bloco,
    valor: state.likert[q.id],
  })).filter(r => r.valor !== undefined && r.valor >= 1 && r.valor <= 5);
}

function calcularScoresDual(respostas) {
  const natural = calcularPerfil(respostas, 'natural');
  const adapted = calcularPerfil(respostas, 'adaptado');
  const discrepancy = {};
  FATORES_DISPLAY.forEach(df => {
    discrepancy[df] = Math.round(
      (adapted.display[df].ui - natural.display[df].ui) * 10
    ) / 10;
  });
  const facetMeans = calcularFacetMeans(respostas);
  return { natural, adapted, discrepancy, facetMeans };
}

function analisarDiscrepanciaDisplay(dual) {
  const alertas = [];
  FATORES_DISPLAY.forEach(df => {
    const d = dual.discrepancy[df];
    const nat = dual.natural.display[df].ui;
    const adp = dual.adapted.display[df].ui;
    if (d <= -DISCREPANCY_THRESHOLD && nat > 2) {
      alertas.push({
        fator: df, tipo: 'supressao', delta: d,
        texto: `${DISPLAY_LABELS[df]}: possível supressão no trabalho (natural +${nat} → adaptado +${adp}).`,
      });
    } else if (d >= DISCREPANCY_THRESHOLD && adp > nat) {
      alertas.push({
        fator: df, tipo: 'hiperadaptacao', delta: d,
        texto: `${DISPLAY_LABELS[df]}: possível hiperadaptação (+${d}).`,
      });
    }
  });
  return alertas;
}

function calcularFacetMeans(respostas) {
  const facetRaw = {};
  const facetCounts = {};
  Object.keys(FACETS).forEach(d => {
    FACETS[d].forEach(f => {
      facetRaw[f.code] = 0;
      facetCounts[f.code] = 0;
    });
  });
  respostas.forEach(r => {
    const item = ITEM_MAP[r.id];
    if (!item || !item.facet) return;
    const val = pontuarItem(item, r.valor);
    facetRaw[item.facet] += val;
    facetCounts[item.facet]++;
  });
  const means = {};
  Object.keys(facetRaw).forEach(code => {
    means[code] = facetCounts[code] > 0 ? facetRaw[code] / facetCounts[code] : 3;
  });
  return means;
}

function calcularScoresDual(respostas) {
  const natural = calcularPerfil(respostas, 'natural');
  const adapted = calcularPerfil(respostas, 'adaptado');
  const discrepancy = {};
  FATORES_DISPLAY.forEach(df => {
    discrepancy[df] = Math.round(
      (adapted.display[df].ui - natural.display[df].ui) * 10
    ) / 10;
  });
  const facetMeans = calcularFacetMeans(respostas);
  return { natural, adapted, discrepancy, facetMeans };
}

function determinarPerfilDominante(displayScores) {
  const sorted = FATORES_DISPLAY.slice().sort((a, b) => displayScores[b].ui - displayScores[a].ui);
  return { primario: sorted[0], secundario: sorted[1], ordenacao: sorted };
}

function validarRespostaLikert(qid) {
  const val = state.likert[qid];
  if (val === undefined || val < 1 || val > 5) {
    return { ok: false, msg: 'Selecione uma opção de 1 a 5 antes de continuar.' };
  }
  return { ok: true };
}

const BANDA_TO_TEMPLATE_N = {
  'Muito Alto': 'muito_baixo_N',
  'Alto': 'baixo_N',
  'Médio': 'medio_N',
  'Baixo': 'alto_N',
  'Muito Baixo': 'muito_alto_N',
};

function selectTemplateKey(fator, internalScores, displayScores, campo) {
  if (fator !== 'N') {
    const banda = internalScores.banda;
    return banda.toLowerCase().replace(/ /g, '_');
  }
  const displayBanda = displayScores.SE.banda;
  return BANDA_TO_TEMPLATE_N[displayBanda] || 'medio_N';
}

function extractDisplayScores(dual) {
  const out = { natural: {}, adapted: {} };
  FATORES_DISPLAY.forEach(df => {
    out.natural[df] = dual.natural.display[df].ui;
    out.adapted[df] = dual.adapted.display[df].ui;
  });
  return out;
}

function extractTScores(internal) {
  return {
    O: internal.O.tScore,
    C: internal.C.tScore,
    E: internal.E.tScore,
    A: internal.A.tScore,
    N: internal.N.tScore,
  };
}