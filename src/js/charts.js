// ===== GRÁFICOS OCEAN — Radar + Barras Natural/Adaptado =====

function gerarGraficosOCEAN(dual) {
  return `
    <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-sm p-5 sm:p-8 mb-6 fade-in card">
      <h3 class="text-lg font-bold mb-6 text-center">Perfil OCEAN — Natural · Adaptado</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <p class="text-xs font-bold text-center mb-2 text-purple-700">Radar OCEAN (Natural)</p>
          <div style="height:280px"><canvas id="chartRadar"></canvas></div>
        </div>
        <div>
          <p class="text-xs font-bold text-center mb-2 text-blue-700">Barras Natural vs Adaptado</p>
          <div style="height:280px"><canvas id="chartBars"></canvas></div>
        </div>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-6 text-center">
        ${FATORES_DISPLAY.map(f => `
          <div class="p-2 rounded-lg bg-gray-50 dark:bg-gray-800">
            <div class="font-bold text-xs" style="color:${CORES[f]}">${DISPLAY_LABELS[f]}</div>
            <div class="text-xs text-gray-500">Nat: ${dual.natural.display[f].ui > 0 ? '+' : ''}${dual.natural.display[f].ui}</div>
            <div class="text-xs text-gray-500">Adp: ${dual.adapted.display[f].ui > 0 ? '+' : ''}${dual.adapted.display[f].ui}</div>
            <div class="text-xs ${Math.abs(dual.discrepancy[f]) >= DISCREPANCY_THRESHOLD ? 'text-red-500 font-bold' : 'text-gray-400'}">Δ ${dual.discrepancy[f] > 0 ? '+' : ''}${dual.discrepancy[f]}</div>
          </div>`).join('')}
      </div>
    </div>`;
}

function initGraficosOCEAN(dual) {
  const labels = FATORES_DISPLAY.map(f => DISPLAY_LABELS[f]);
  const natData = FATORES_DISPLAY.map(f => dual.natural.display[f].ui);
  const adpData = FATORES_DISPLAY.map(f => dual.adapted.display[f].ui);
  const colors = FATORES_DISPLAY.map(f => CORES[f]);

  const radarCtx = document.getElementById('chartRadar');
  if (radarCtx) {
    if (window._chartRadar) window._chartRadar.destroy();
    window._chartRadar = new Chart(radarCtx, {
      type: 'radar',
      data: {
        labels,
        datasets: [{
          label: 'Natural',
          data: natData,
          backgroundColor: 'rgba(142, 68, 173, 0.2)',
          borderColor: '#8E44AD',
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { r: { min: -10, max: 10, ticks: { stepSize: 5 } } },
        plugins: { legend: { display: false } },
      },
    });
  }

  const barCtx = document.getElementById('chartBars');
  if (barCtx) {
    if (window._chartBars) window._chartBars.destroy();
    window._chartBars = new Chart(barCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          { label: 'Natural', data: natData, backgroundColor: colors.map(c => c + '99'), borderColor: colors, borderWidth: 1 },
          { label: 'Adaptado', data: adpData, backgroundColor: colors.map(c => c + '44'), borderColor: colors, borderWidth: 1 },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
        scales: { y: { min: -10, max: 10 } },
      },
    });
  }
}