#!/usr/bin/env python3
"""Bundle index.html self-contained + injeta sw.js + copia docs/."""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
JS_DIR = BASE / "src" / "js"
OUTPUT = BASE / "index.html"

JS_ORDER = [
    "constants.js",
    "questions.js",
    "palavras-data.js",
    "devolutiva-templates.js",
    "scoring.js",
    "charts.js",
    "devolutiva.js",
    "features.js",
    "app.js",
]

HTML_HEAD = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Perfil de Personalidade OCEAN - Big Five</title>
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#1a1a2e">
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config={darkMode:'class'}</script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*{font-family:'Inter',system-ui,sans-serif;scroll-behavior:smooth}
.ocean-o{color:#8E44AD}.ocean-c{color:#2980B9}.ocean-e{color:#F39C12}.ocean-a{color:#27AE60}.ocean-se{color:#E74C3C}
@keyframes fIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.fade-in{animation:fIn .35s ease}
.progress-bar{transition:width .5s ease}
html.dark body{background:#111827;color:#f3f4f6}
html.dark .card{background:#1f2937!important}
.likert-btn{cursor:pointer}
@media print{.no-print{display:none!important}}
</style>
</head>
<body class="bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100 min-h-screen flex flex-col">

<header class="bg-gradient-to-r from-[#1a1a2e] to-[#16213e] text-white py-6 px-4 text-center">
  <h1 class="text-xl font-bold tracking-wider">Perfil de <span class="text-purple-400">Personalidade</span></h1>
  <p class="text-sm text-white/60 mt-1">Big Five (OCEAN) | TeclaPonto</p>
</header>

<main class="flex-1" id="app">

<section id="home" class="py-12 px-4">
  <div class="max-w-2xl mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 text-center">
    <h2 class="text-2xl font-bold mb-3">Descubra seu Perfil de Personalidade</h2>
    <p class="text-gray-500 text-sm leading-relaxed mb-2">O modelo <strong>Big Five (OCEAN)</strong> mapeia cinco dimensões estáveis da personalidade.</p>
    <p class="text-gray-500 dark:text-gray-400 text-sm leading-relaxed mb-4">São <strong>60 afirmações</strong> em escala de 1 a 5. Responda com sinceridade — não há respostas certas ou erradas.</p>
    <div class="grid grid-cols-5 gap-2 max-w-md mx-auto mb-6 text-xs">
      <div class="rounded-xl p-2 text-white font-bold" style="background:#8E44AD">O</div>
      <div class="rounded-xl p-2 text-white font-bold" style="background:#2980B9">C</div>
      <div class="rounded-xl p-2 text-white font-bold" style="background:#F39C12">E</div>
      <div class="rounded-xl p-2 text-white font-bold" style="background:#27AE60">A</div>
      <div class="rounded-xl p-2 text-white font-bold" style="background:#E74C3C">SE</div>
    </div>
    <button onclick="iniciar()" class="bg-[#1a1a2e] text-white px-12 py-3.5 rounded-full font-semibold shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all">Iniciar Teste</button>
    <div class="flex justify-center gap-3 mt-5 flex-wrap">
      <span class="bg-white dark:bg-gray-800 border rounded-full px-4 py-1.5 text-xs text-gray-500"><strong>60</strong> afirmações</span>
      <span class="bg-white dark:bg-gray-800 border rounded-full px-4 py-1.5 text-xs text-gray-500"><strong>~12</strong> min</span>
      <span class="bg-white dark:bg-gray-800 border rounded-full px-4 py-1.5 text-xs text-gray-500">v<strong>1.0</strong></span>
    </div>
    <button onclick="toggleDarkMode()" class="mt-4 text-xs text-gray-400 underline">Alternar modo escuro</button>
    <div class="mt-8 pt-6 border-t border-gray-100 dark:border-gray-700">
      <p class="text-xs text-gray-400 mb-3 uppercase tracking-wider">Instrumentos TeclaPonto</p>
      <div class="flex flex-col sm:flex-row gap-3 justify-center max-w-lg mx-auto">
        <a href="https://centralsp3.github.io/TESTEDISC/" class="flex-1 px-6 py-3 rounded-full font-semibold text-sm bg-white dark:bg-gray-700 border-2 border-amber-400 text-amber-700 dark:text-amber-300 hover:bg-amber-50 dark:hover:bg-gray-600 text-center transition-all">Perfil DISC</a>
        <a href="https://centralsp3.github.io/PERSONALIDADE/" class="flex-1 px-6 py-3 rounded-full font-semibold text-sm bg-[#1a1a2e] text-white shadow-lg text-center transition-all ring-2 ring-purple-400 ring-offset-2 dark:ring-offset-gray-800">Personalidade OCEAN</a>
      </div>
      <a href="https://centralsp3.github.io/central/" class="inline-block mt-4 text-xs text-gray-400 underline hover:text-gray-600">← Hub CENTRAL SP3</a>
    </div>
  </div>
</section>

<section id="quiz" class="py-8 px-4" style="display:none">
  <div class="max-w-2xl mx-auto">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 mb-5">
      <div class="flex justify-end items-center mb-3">
        <span id="progressText" class="text-sm font-semibold text-gray-400">1 de 60</span>
      </div>
      <div class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div id="progressBar" class="progress-bar h-full bg-gradient-to-r from-purple-400 to-blue-500 rounded-full" style="width:0%"></div>
      </div>
    </div>
    <div id="quizContainer" class="min-h-[300px]"></div>
  </div>
</section>

<section id="pausaBloco" class="py-12 px-4" style="display:none">
  <div class="max-w-lg mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 text-center fade-in card">
    <h2 class="text-xl font-bold mb-2">Metade do questionário!</h2>
    <p id="pausaCopy" class="text-gray-500 dark:text-gray-400 text-sm mb-6">Você completou 30 de 60 afirmações. Faça uma pausa breve se precisar — suas respostas anteriores estão salvas.</p>
    <button onclick="continuarAposPausa()" class="bg-[#1a1a2e] text-white px-10 py-3 rounded-full font-semibold shadow-lg">Continuar →</button>
  </div>
</section>

<section id="nameForm" class="py-8 px-4" style="display:none">
  <div class="max-w-lg mx-auto bg-white dark:bg-gray-800 rounded-2xl shadow-sm p-8 text-center fade-in">
    <h2 class="text-xl font-bold mb-2">Teste Concluído!</h2>
    <p class="text-gray-500 text-sm mb-6">Insira seu nome para gerar o relatório personalizado.</p>
    <input id="userName" type="text" placeholder="Seu nome" class="w-full border rounded-xl px-4 py-3 text-center text-lg font-medium outline-none focus:border-[#1a1a2e] transition-colors mb-4 dark:bg-gray-700 dark:border-gray-600">
    <div id="nameError" class="text-red-500 text-sm mb-3 hidden">Por favor, digite seu nome.</div>
    <button onclick="gerarRelatorio()" class="bg-[#1a1a2e] text-white px-10 py-3 rounded-full font-semibold shadow-lg">Gerar meu Relatório</button>
  </div>
</section>

<section id="resultado" class="py-8 px-4" style="display:none">
  <div class="max-w-3xl mx-auto" id="resultadoContainer"></div>
</section>

</main>

<footer class="bg-[#1a1a2e] text-white/60 text-center py-4 text-xs mt-auto">
  <p>TeclaPonto — Perfil de Personalidade OCEAN. Instrumento de autoconhecimento. Não substitui avaliação psicológica profissional.</p>
</footer>

<script>
"""

HTML_TAIL = """
</script>
</body>
</html>
"""


def inject_sw(version: str) -> None:
    template = (BASE / "sw.js.template").read_text(encoding="utf-8")
    content = template.replace("{{INSTRUMENT_VERSION}}", version)
    (BASE / "sw.js").write_text(content, encoding="utf-8")
    docs = BASE / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "sw.js").write_text(content, encoding="utf-8")


def build() -> None:
    constants = (JS_DIR / "constants.js").read_text(encoding="utf-8")
    m = re.search(r"INSTRUMENT_VERSION = '([^']+)'", constants)
    version = m.group(1) if m else "1.0.0"

    parts = [HTML_HEAD]
    for fname in JS_ORDER:
        path = JS_DIR / fname
        if not path.exists():
            raise FileNotFoundError(f"Módulo ausente: {path}")
        parts.append(f"\n// --- {fname} ---\n")
        parts.append(path.read_text(encoding="utf-8"))
    parts.append(HTML_TAIL)
    content = "".join(parts)
    OUTPUT.write_text(content, encoding="utf-8")

    docs_dir = BASE / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "index.html").write_text(content, encoding="utf-8")
    inject_sw(version)

    for asset in ("manifest.json",):
        src = BASE / asset
        if src.exists():
            (docs_dir / asset).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"✓ Gerado: {OUTPUT} ({len(content) // 1024} KB, {len(JS_ORDER)} módulos)")
    print(f"✓ sw.js cache: testepersonalidade-v{version}")
    print(f"✓ Copiado para: {docs_dir / 'index.html'}")


if __name__ == "__main__":
    build()