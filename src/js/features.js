// ===== FEATURES: Dark mode, Share, PDF, PWA, API =====

function initDarkMode() {
  const saved = localStorage.getItem('ocean-theme');
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
  }
}

function toggleDarkMode() {
  document.documentElement.classList.toggle('dark');
  localStorage.setItem('ocean-theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
}

async function salvarRespostasBatch(dual) {
  if (!API_BASE) return;
  try {
    await fetch(`${API_BASE}/responses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: state.sessionId,
        instrument_version: INSTRUMENT_VERSION,
        responses: state.shuffled.map(q => ({
          question_id: q.id,
          block: q.bloco,
          factor: ITEM_MAP[q.id].fator,
          likert_value: state.likert[q.id],
        })),
      }),
    });
  } catch (_) { /* offline ok */ }
}

async function inferirViaAPI(dual) {
  if (!API_BASE) return null;
  try {
    const t_scores = {
      natural: extractTScores(dual.natural.internal),
      adapted: extractTScores(dual.adapted.internal),
    };
    const resp = await fetch(`${API_BASE}/infer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ t_scores, share: true }),
    });
    if (!resp.ok) return null;
    return await resp.json();
  } catch (_) { return null; }
}

function gerarLinkCompartilhamento(hash) {
  if (!hash) return '';
  return `${window.location.origin}${window.location.pathname}?r=${hash}`;
}

async function copiarLink(hash) {
  const url = gerarLinkCompartilhamento(hash);
  if (!url) { alert('Link não disponível (modo offline).'); return; }
  try {
    await navigator.clipboard.writeText(url);
    alert('Link copiado!');
  } catch (_) {
    prompt('Copie o link:', url);
  }
}

function exportarPDF() {
  window.print();
}

async function carregarResultadoCompartilhado() {
  const params = new URLSearchParams(window.location.search);
  const hash = params.get('r');
  if (!hash || !API_BASE) return false;
  try {
    const resp = await fetch(`${API_BASE}/result/${hash}`);
    if (!resp.ok) return false;
    const data = await resp.json();
    const dual = {
      natural: {
        internal: Object.fromEntries(FACTORES_INTERNOS.map(f => [f, {
          tScore: data.t_scores?.natural?.[f] ?? 50,
          ui: data.display_scores?.natural?.[toDisplayFactor(f)] ?? 0,
          banda: classificarBandaT(data.t_scores?.natural?.[f] ?? 50),
          mean: 3, percentil: 50,
        }])),
        display: Object.fromEntries(FATORES_DISPLAY.map(f => {
          const cod = f === 'SE' ? 'N' : f;
          return [f, {
            ui: data.display_scores?.natural?.[f] ?? 0,
            banda: classificarBandaDisplay(cod, data.t_scores?.natural?.[cod] ?? 50),
            tScore: f === 'SE' ? 100 - (data.t_scores?.natural?.N ?? 50) : (data.t_scores?.natural?.[f] ?? 50),
            mean: 3, percentil: 50, displayFactor: f,
          }];
        })),
      },
      adapted: {
        internal: Object.fromEntries(FACTORES_INTERNOS.map(f => [f, {
          tScore: data.t_scores?.adapted?.[f] ?? 50,
          ui: data.display_scores?.adapted?.[toDisplayFactor(f)] ?? 0,
          banda: classificarBandaT(data.t_scores?.adapted?.[f] ?? 50),
          mean: 3, percentil: 50,
        }])),
        display: Object.fromEntries(FATORES_DISPLAY.map(f => {
          const cod = f === 'SE' ? 'N' : f;
          return [f, {
            ui: data.display_scores?.adapted?.[f] ?? 0,
            banda: classificarBandaDisplay(cod, data.t_scores?.adapted?.[cod] ?? 50),
            tScore: f === 'SE' ? 100 - (data.t_scores?.adapted?.N ?? 50) : (data.t_scores?.adapted?.[f] ?? 50),
            mean: 3, percentil: 50, displayFactor: f,
          }];
        })),
      },
      discrepancy: {},
    };
    FATORES_DISPLAY.forEach(f => {
      dual.discrepancy[f] = Math.round(
        (dual.adapted.display[f].ui - dual.natural.display[f].ui) * 10
      ) / 10;
    });
    document.getElementById('home').style.display = 'none';
    await calcularERenderizar('Resultado Compartilhado', dual, data.inference);
    return true;
  } catch (_) { return false; }
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initDarkMode();
  carregarResultadoCompartilhado();
});