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
    <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
      Este relatório oferece um panorama do seu perfil de personalidade nos cinco grandes domínios.
      Use estas informações como ponto de partida para autoconhecimento e desenvolvimento.
    </p>
    <p class="text-xs text-gray-400 italic">${disclaimer}</p>`);
}

function renderizarRelatorio(nome, dual, apiResult) {
  const hoje = new Date().toLocaleDateString('pt-BR');
  const dominante = determinarPerfilDominante(dual.natural.display);
  const seed = hashScores(dual.natural.display);
  const disclaimer = DEVOLUTIVA_TEMPLATES?.disclaimer || '';

  let html = gerarSumario(nome, hoje, dominante, dual);
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
  if (respostas.length < TOTAL_POR_BLOCO * 2 && !dualPrecomputed) {
    alert('Respostas incompletas. Complete todas as 60 afirmações.');
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