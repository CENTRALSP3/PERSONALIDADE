// ===== APP — Quiz Likert OCEAN =====

const state = {
  passo: 0,
  likert: {},
  shuffled: [],
  pausaVista: false,
  sessionId: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36),
};

const TOTAL_QUESTOES = TOTAL_POR_BLOCO * 2;
const PAUSA_EM = TOTAL_POR_BLOCO;

const LIKERT_LABELS = [
  { val: 1, short: '1', label: 'Discordo totalmente' },
  { val: 2, short: '2', label: 'Discordo' },
  { val: 3, short: '3', label: 'Neutro' },
  { val: 4, short: '4', label: 'Concordo' },
  { val: 5, short: '5', label: 'Concordo totalmente' },
];

function shuffleArray(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function prepararQuestao(q) {
  return { ...q };
}

function perguntasEmbaralhadas() {
  const natural = shuffleArray(PERGUNTAS_NATURAL.map((q, i) => prepararQuestao(q, i)));
  const adaptado = shuffleArray(PERGUNTAS_ADAPTADO.map((q, i) => prepararQuestao(q, i)));
  const slots = shuffleArray([...Array(TOTAL_QUESTOES).keys()]);
  const natSlots = slots.slice(0, TOTAL_POR_BLOCO).sort((a, b) => a - b);
  const adpSlots = slots.slice(TOTAL_POR_BLOCO).sort((a, b) => a - b);
  const merged = new Array(TOTAL_QUESTOES);
  natural.forEach((q, i) => { merged[natSlots[i]] = q; });
  adaptado.forEach((q, i) => { merged[adpSlots[i]] = q; });
  return merged;
}

function shufflePerguntas() {
  state.shuffled = perguntasEmbaralhadas();
}

function iniciar() {
  document.getElementById('home').style.display = 'none';
  document.getElementById('quiz').style.display = 'block';
  state.passo = 0;
  state.likert = {};
  state.pausaVista = false;
  shufflePerguntas();
  atualizarPausaCopy();
  mostrarPergunta();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function atualizarPausaCopy() {
  const el = document.getElementById('pausaCopy');
  if (el) {
    el.textContent = `Você completou ${TOTAL_POR_BLOCO} de ${TOTAL_QUESTOES} afirmações. Faça uma pausa breve se precisar — suas respostas anteriores estão salvas.`;
  }
}

function mostrarPergunta() {
  const idx = state.passo;
  if (idx >= TOTAL_QUESTOES) {
    mostrarFormNome();
    return;
  }

  const q = state.shuffled[idx];
  document.getElementById('progressText').textContent = `${idx + 1} de ${TOTAL_QUESTOES}`;
  document.getElementById('progressBar').style.width = `${((idx + 1) / TOTAL_QUESTOES) * 100}%`;

  const container = document.getElementById('quizContainer');
  const selected = state.likert[q.id];

  const likertHtml = LIKERT_LABELS.map(opt => {
    const isSel = selected === opt.val;
    return `<button role="radio" aria-checked="${isSel}" data-val="${opt.val}"
      class="likert-btn flex-1 py-3 px-1 rounded-xl border-2 transition-all text-center
      ${isSel ? 'border-[#1a1a2e] bg-[#1a1a2e] text-white' : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800'}">
      <span class="font-bold text-lg">${opt.short}</span><br>
      <span class="text-xs opacity-80">${opt.label}</span>
    </button>`;
  }).join('');

  container.innerHTML = `
    <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-sm p-5 sm:p-8 fade-in card">
      <p class="text-base sm:text-lg font-semibold mb-6 leading-relaxed">${q.texto}</p>
      <p class="text-sm text-gray-500 mb-4">Indique o quanto esta afirmação descreve você.</p>
      <div class="likert-scale flex justify-between gap-1" role="radiogroup" aria-label="Escala Likert">
        ${likertHtml}
      </div>
    </div>
    <div class="flex justify-center gap-3 mt-4">
      ${idx > 0 ? '<button onclick="voltar()" class="bg-gray-200 text-gray-700 px-6 py-2.5 rounded-full font-semibold">Voltar</button>' : ''}
      <button onclick="avancar()" class="bg-[#1a1a2e] text-white px-8 py-2.5 rounded-full font-semibold shadow">
        ${idx < TOTAL_QUESTOES - 1 ? 'Próxima →' : 'Concluir →'}
      </button>
    </div>`;

  container.querySelectorAll('.likert-btn').forEach(btn => {
    btn.onclick = function() {
      state.likert[q.id] = parseInt(this.dataset.val, 10);
      mostrarPergunta();
    };
  });
}

function mostrarPausaBloco() {
  document.getElementById('quiz').style.display = 'none';
  document.getElementById('pausaBloco').style.display = 'block';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function continuarAposPausa() {
  state.pausaVista = true;
  document.getElementById('pausaBloco').style.display = 'none';
  document.getElementById('quiz').style.display = 'block';
  mostrarPergunta();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function voltar() {
  if (state.passo > 0) {
    if (state.passo === PAUSA_EM && state.pausaVista) {
      state.pausaVista = false;
      document.getElementById('pausaBloco').style.display = 'none';
      document.getElementById('quiz').style.display = 'block';
    }
    state.passo--;
    mostrarPergunta();
  }
}

function avancar() {
  const q = state.shuffled[state.passo];
  const v = validarRespostaLikert(q.id);
  if (!v.ok) { alert(v.msg); return; }
  state.passo++;
  if (state.passo === PAUSA_EM && !state.pausaVista) {
    mostrarPausaBloco();
    return;
  }
  mostrarPergunta();
}

function mostrarFormNome() {
  document.getElementById('progressBar').style.width = '100%';
  document.getElementById('quiz').style.display = 'none';
  document.getElementById('nameForm').style.display = 'block';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function gerarRelatorio() {
  const nome = document.getElementById('userName').value.trim();
  if (!nome) {
    document.getElementById('nameError').classList.remove('hidden');
    return;
  }
  document.getElementById('nameError').classList.add('hidden');
  document.getElementById('nameForm').style.display = 'none';
  calcularERenderizar(nome);
}

function refazer() {
  document.getElementById('resultado').style.display = 'none';
  document.getElementById('home').style.display = 'block';
  ['_chartRadar', '_chartBars'].forEach(k => {
    if (window[k]) { window[k].destroy(); window[k] = null; }
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
}