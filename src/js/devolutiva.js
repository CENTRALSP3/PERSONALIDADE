// ===== DEVOLUTIVA OCEAN — 12 seções =====

function hashScores(scores) {
  const s = FATORES_DISPLAY.map(f => scores[f]?.ui ?? 0).join('');
  let h = 0;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function pickFactorTemplate(fator, campo, seed, internal, display, offset = 0) {
  const key = selectTemplateKey(fator, internal[fator], display, campo);
  const tpl = DEVOLUTIVA_TEMPLATES?.fatores?.[fator]?.[campo];
  if (!tpl) return '';
  if (Array.isArray(tpl)) {
    return tpl[(seed + offset) % tpl.length] || '';
  }
  if (typeof tpl === 'object' && tpl[key]) {
    const arr = tpl[key];
    return Array.isArray(arr) ? arr[(seed + offset) % arr.length] : arr;
  }
  return '';
}

function formatParagrafos(texto) {
  if (!texto) return '';
  const t = Array.isArray(texto) ? texto.join(' ') : texto;
  return `<p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed mb-3">${t}</p>`;
}

function cardSecao(num, titulo, conteudo) {
  return `<div class="card bg-white dark:bg-gray-900 rounded-2xl shadow-sm p-5 sm:p-8 mb-6 fade-in">
    <div class="flex items-center gap-3 mb-4 pb-3 border-b border-gray-100 dark:border-gray-700">
      <span class="w-8 h-8 rounded-full bg-[#1a1a2e] text-white text-sm font-bold flex items-center justify-center">${num}</span>
      <h3 class="text-lg font-bold">${titulo}</h3>
    </div>${conteudo}</div>`;
}

function gerarSumario(nome, hoje, dominante, dual) {
  return `<div class="text-center mb-8 pb-6 border-b border-gray-200 dark:border-gray-700">
    <p class="text-xs uppercase tracking-widest text-gray-400 mb-2">Perfil de Personalidade</p>
    <h2 class="text-2xl font-bold">Big Five (OCEAN)</h2>
    <p class="text-gray-500 mt-1">${nome} · ${hoje}</p>
    <div class="flex flex-wrap justify-center gap-2 mt-4">
      <span class="px-4 py-1.5 rounded-full text-white text-sm font-bold" style="background:${CORES[dominante.primario]}">
        ${DISPLAY_LABELS[dominante.primario]}
      </span>
    </div>
    <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 mt-4 max-w-xl mx-auto text-xs">
      ${FATORES_DISPLAY.map(f => `<div class="p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
        <span class="font-bold" style="color:${CORES[f]}">${f}</span>
        <span class="text-gray-500 ml-1">${dual.natural.display[f].banda}</span>
      </div>`).join('')}
    </div>
  </div>`;
}

function gerarExplicacaoFatores(dual) {
  const explicacoes = FACTORES_INTERNOS.map((f, i) => {
    const info = FACTOR_INFO[f] || {};
    const displayF = f === 'N' ? 'SE' : f;
    const scores = dual.natural.display[displayF];
    const t = scores.tScore;
    const nivel = scores.banda;
    const ui = scores.ui;
    return `
      <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border-l-4" style="border-color:${CORES[displayF]}">
        <h4 class="font-bold text-base mb-1" style="color:${CORES[displayF]}">${info.nome || DISPLAY_LABELS[displayF]} <span class="text-xs font-normal text-gray-500">(${nivel} · T=${t} · UI=${ui > 0 ? '+' : ''}${ui})</span></h4>
        <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">${info.descricao || ''}</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div><strong class="text-green-600">Alto:</strong> ${info.altoComportamentos || ''}</div>
          <div><strong class="text-amber-600">Baixo:</strong> ${info.baixoComportamentos || ''}</div>
        </div>
        <div class="mt-2 text-xs text-gray-500">Trabalho: ${info.trabalho || ''} | Relações: ${info.relacoes || ''} | Sob pressão: ${info.sobPressao || ''}</div>
      </div>`;
  }).join('');
  return cardSecao(1, 'Entendendo os 5 Fatores do Big Five (OCEAN)', `
    <p class="text-sm text-gray-500 mb-4">O modelo Big Five é o padrão-ouro da psicologia científica da personalidade (validado em dezenas de culturas e >1000 estudos). Cada fator é um continuum. Suas pontuações são comparadas com normas da população brasileira (BFI adaptado). T-score 50 = média da população. Cada 10 pontos ≈ 1 desvio-padrão. A escala UI (-10 a +10) mostra o desvio normalizado da média (0 = exatamente na média).</p>
    ${explicacoes}
    <p class="text-xs italic text-gray-400 mt-3">Perfil Natural = quem você é no fundo. Perfil Adaptado = como você se ajusta no contexto profissional. Discrepâncias grandes podem indicar supressão ou hiperadaptação.</p>
  `);
}

function gerarFacetsSection(dual) {
  if (!dual.facetMeans) return '';
  let html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">';
  Object.keys(FACETS).forEach(domain => {
    const domLabel = DISPLAY_LABELS[domain === 'N' ? 'SE' : domain];
    html += `<div class="p-3 bg-white dark:bg-gray-900 rounded-lg border">
      <div class="font-bold mb-2" style="color:${CORES[domain==='N'?'SE':domain]}">${domLabel} - Facets</div>`;
    FACETS[domain].forEach(f => {
      const mean = dual.facetMeans[f.code] || 3;
      const ui = normalizeForUI(mean);
      const t = Math.round((mean - 3) * 10 + 50); // approx
      html += `<div class="text-xs mb-1 flex justify-between"><span>${f.name}</span> <span class="font-mono">UI ${ui>0?'+':''}${ui} · ~T${t}</span></div>`;
    });
    html += '</div>';
  });
  html += '</div>';
  return cardSecao(3, 'Detalhamento por Facets (30 subtraços)', `
    <p class="text-sm text-gray-500 mb-3">Cada domínio é composto por 6 facets mais específicos do modelo IPIP-NEO. Aqui estão seus scores aproximados (baseados na média das respostas relacionadas a cada facet).</p>
    ${html}
    <p class="text-xs text-gray-400 mt-2">Facets ajudam a entender nuances dentro de cada traço principal.</p>
  `);
}

function gerarAutoImagem(perfilCtx, seed, blocoLabel) {
  const { internal, display } = perfilCtx;
  const textos = FACTORES_INTERNOS.map((f, i) =>
    formatParagrafos(pickFactorTemplate(f, 'auto_imagem', seed, internal, display, i))
  ).join('');
  return cardSecao(2, `Autoimagem — Perfil ${blocoLabel}`, `
    <p class="text-xs text-gray-400 mb-3 uppercase">Comportamento ${blocoLabel.toLowerCase()}</p>${textos}`);
}

function gerarPalavrasDescritivas(dual, seed) {
  const palavras = [];
  FATORES_DISPLAY.forEach((f, i) => {
    const cod = f === 'SE' ? 'N' : f;
    const intens = dual.natural.display[f].ui > 2 ? 'alto' : 'baixo';
    const list = PALAVRAS_POR_FATOR?.[cod]?.[intens] || [];
    palavras.push(...list.slice(0, 2));
  });
  const unicas = [...new Set(palavras)].slice(0, 16);
  return cardSecao(3, 'Palavras Descritivas', `
    <div class="flex flex-wrap gap-2">${unicas.map(p =>
      `<span class="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-full text-sm">${p}</span>`).join('')}</div>`);
}

function gerarMotivacao(dual, seed) {
  const textos = FACTORES_INTERNOS.slice(0, 3).map((f, i) =>
    formatParagrafos(pickFactorTemplate(f, 'trabalho', seed, dual.natural.internal, dual.natural.display, i))
  ).join('');
  return cardSecao(4, 'Motivação e Energia', textos);
}

function gerarPontosFortes(dual, seed) {
  const top = determinarPerfilDominante(dual.natural.display);
  const items = [top.primario, top.secundario].map(f => {
    const cod = f === 'SE' ? 'N' : f;
    const tpl = DEVOLUTIVA_TEMPLATES?.fatores?.[cod]?.pontos_fortes || [];
    return tpl.slice(0, 2);
  }).flat();
  return cardSecao(5, 'Pontos Fortes', `
    <ul class="list-disc pl-5 text-sm text-gray-600 dark:text-gray-300 space-y-1">
      ${[...new Set(items)].map(i => `<li>${i}</li>`).join('')}
    </ul>`);
}

function gerarDesafios(dual, seed) {
  const bottom = dual.natural.display[determinarPerfilDominante(dual.natural.display).ordenacao[4]];
  const cod = 'N';
  const tpl = DEVOLUTIVA_TEMPLATES?.fatores?.[cod]?.desafios || ['Atenção a reações emocionais'];
  return cardSecao(6, 'Desafios e Pontos de Atenção', `
    <ul class="list-disc pl-5 text-sm text-gray-600 dark:text-gray-300 space-y-1">
      ${FACTORES_INTERNOS.map(f => {
        const d = DEVOLUTIVA_TEMPLATES?.fatores?.[f]?.desafios || [];
        return d.slice(0, 1).map(x => `<li>${x}</li>`).join('');
      }).join('')}
    </ul>`);
}

function gerarRelacionamentos(dual, seed) {
  const textos = ['E', 'A', 'O'].map((f, i) =>
    formatParagrafos(pickFactorTemplate(f, 'relacoes', seed, dual.natural.internal, dual.natural.display, i))
  ).join('');
  return cardSecao(7, 'Relacionamentos', textos);
}

function gerarCarreira(dual, seed) {
  const textos = ['C', 'E', 'O'].map((f, i) =>
    formatParagrafos(pickFactorTemplate(f, 'trabalho', seed, dual.adapted.internal, dual.adapted.display, i))
  ).join('');
  return cardSecao(8, 'Carreira e Trabalho', textos);
}

function gerarSobPressao(dual, seed) {
  const texto = pickFactorTemplate('N', 'sob_pressao', seed, dual.natural.internal, dual.natural.display);
  return cardSecao(9, 'Sob Pressão e Estresse', formatParagrafos(texto));
}

function gerarPercepcaoAdaptada(dual) {
  const alertas = analisarDiscrepanciaDisplay(dual);
  const tpl = DEVOLUTIVA_TEMPLATES?.discrepancia || {};
  let html = alertas.length
    ? `<ul class="space-y-2">${alertas.map(a => `<li class="text-sm text-amber-700 dark:text-amber-400">⚠ ${a.texto}</li>`).join('')}</ul>`
    : `<p class="text-sm text-gray-500">Sem discrepâncias significativas entre perfis natural e adaptado.</p>`;
  if (alertas.some(a => a.tipo === 'supressao')) {
    html += formatParagrafos((tpl.supressao || [])[0]);
  }
  if (alertas.some(a => a.tipo === 'hiperadaptacao')) {
    html += formatParagrafos((tpl.hiperadaptacao || [])[0]);
  }
  return cardSecao(10, 'Percepção Adaptada', html);
}

function gerarCrescimento(dual, seed) {
  const textos = FACTORES_INTERNOS.map((f, i) =>
    formatParagrafos(pickFactorTemplate(f, 'crescimento', seed, dual.natural.internal, dual.natural.display, i))
  ).join('');
  return cardSecao(11, 'Crescimento e Desenvolvimento', textos);
}

function gerarSintese(disclaimer) {
  return cardSecao(12, 'Síntese e Próximos Passos', `
    <p class="text-sm text-gray-600 dark:text-gray-300 mb-3">
      Este relatório oferece um panorama profundo do seu perfil Big Five. Os fatores são estáveis ao longo da vida adulta (herdabilidade ~40-60%), mas comportamentos podem ser desenvolvidos com consciência e prática.
    </p>
    <ul class="text-sm text-gray-600 dark:text-gray-300 list-disc pl-5 space-y-1 mb-4">
      <li><strong>Métricas usadas:</strong> Média por fator → T-score (população ref. brasileira) → Percentil + banda + UI (-10 a +10). Randomização completa das perguntas a cada sessão para maior validade.</li>
      <li><strong>Perfil Duplo:</strong> Natural reflete sua essência; Adaptado mostra ajustes no contexto profissional. Grandes deltas podem indicar oportunidades de alinhamento ou autoconhecimento.</li>
      <li><strong>Próximos passos:</strong> Reflita sobre 1-2 áreas de desenvolvimento. Experimente comportamentos de "alto" em fatores que deseja fortalecer. Considere feedback 360º ou coaching.</li>
    </ul>
    <p class="text-xs text-gray-400 italic">${disclaimer || 'Instrumento de autoconhecimento baseado em IPIP-NEO e pesquisas brasileiras. Não substitui avaliação psicológica profissional.'}</p>`);
}

function renderizarRelatorio(nome, dual, apiResult) {
  const hoje = new Date().toLocaleDateString('pt-BR');
  const dominante = determinarPerfilDominante(dual.natural.display);
  const seed = hashScores(dual.natural.display);
  const disclaimer = DEVOLUTIVA_TEMPLATES?.disclaimer || '';

  let html = gerarSumario(nome, hoje, dominante, dual);
  html += gerarExplicacaoFatores(dual);
  html += gerarFacetsSection(dual);
  html += gerarGraficosOCEAN(dual);
  html += gerarAutoImagem(dual.natural, seed, 'Natural');
  html += gerarPalavrasDescritivas(dual, seed);
  html += gerarMotivacao(dual, seed);
  html += gerarPontosFortes(dual, seed);
  html += gerarDesafios(dual, seed);
  html += gerarRelacionamentos(dual, seed);
  html += gerarCarreira(dual, seed);
  html += gerarSobPressao(dual, seed);
  html += gerarPercepcaoAdaptada(dual);
  html += gerarCrescimento(dual, seed);

  if (apiResult?.interpretation) {
    html += cardSecao('API', 'Interpretação Complementar', formatParagrafos(apiResult.interpretation));
  }

  html += gerarSintese(disclaimer);
  html += `<div class="flex flex-wrap justify-center gap-3 mt-6 no-print">
    <button onclick="exportarPDF()" class="bg-gray-200 px-6 py-2 rounded-full text-sm font-semibold">Exportar PDF</button>
    <button onclick="refazer()" class="bg-[#1a1a2e] text-white px-6 py-2 rounded-full text-sm font-semibold">Refazer Teste</button>
  </div>`;
  return html;
}

async function calcularERenderizar(nome, dualPrecomputed, apiDataPre) {
  const respostas = respostasLikertFromState();
  if (respostas.length < 70 && !dualPrecomputed) {
    alert('Respostas incompletas. Complete todas as ~90 afirmações.');
    return;
  }
  const dual = dualPrecomputed || calcularScoresDual(respostas);
  let apiResult = apiDataPre || null;

  if (FLAGS.enableAPI && !apiResult) {
    apiResult = await inferirViaAPI(dual);
    await salvarRespostasBatch(dual);
  }

  const container = document.getElementById('resultadoContainer');
  container.innerHTML = renderizarRelatorio(nome, dual, apiResult);
  document.getElementById('resultado').style.display = 'block';
  setTimeout(() => initGraficosOCEAN(dual), 100);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}