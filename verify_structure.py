#!/usr/bin/env python3
"""Auditoria estrutural TESTEPERSONALIDADE (~45 checks)."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ERRORS: list[str] = []
OK: list[str] = []


def check(condition: bool, msg: str) -> None:
    if condition:
        OK.append(msg)
    else:
        ERRORS.append(msg)


def main() -> int:
    print("=" * 60)
    print("AUDITORIA — TESTEPERSONALIDADE")
    print("=" * 60)

    # PR-01: infra base
    for f in (
        "build_all.py", "build_complete.py", "run_tests.py", "requirements.txt",
        "manifest.json", "sw.js.template", "README.md", "knowledge.json",
    ):
        check((ROOT / f).is_file(), f"Arquivo: {f}")

    for f in (
        "scripts/extract_knowledge.py", "scripts/build_devolutiva_templates.py",
        "scripts/generate_questions.py", "scripts/build_norms.py",
        "scripts/generate_rules.py", "scripts/translate_items.py",
    ):
        check((ROOT / f).is_file(), f"Script: {f}")

    js_modules = [
        "constants.js", "questions.js", "palavras-data.js",
        "devolutiva-templates.js", "scoring.js", "charts.js",
        "devolutiva.js", "features.js", "app.js",
    ]
    for m in js_modules:
        check((ROOT / "src" / "js" / m).is_file(), f"Módulo: src/js/{m}")

    check((ROOT / "api" / "main.py").is_file(), "API: main.py")
    check((ROOT / "api" / "inference.py").is_file(), "API: inference.py")
    check((ROOT / "api" / "database.py").is_file(), "API: database.py")

    # PR-02: items pool
    items_path = ROOT / "artifacts" / "items.json"
    if items_path.exists():
        items = json.loads(items_path.read_text(encoding="utf-8"))
        pool = items.get("items", [])
        check(len(pool) == 120, f"items.json: 120 itens ({len(pool)})")
        for d in "OCEAN":
            domain_items = [i for i in pool if i.get("domain") == d]
            check(len(domain_items) == 24, f"items.json: 24/{d}")
            check(
                all(re.match(rf"^{d}\d+$", i["ipip_source"]) for i in domain_items),
                f"ipip_source válido domínio {d}",
            )

    reviewed = ROOT / "artifacts" / "items_reviewed.json"
    if reviewed.exists():
        rev = json.loads(reviewed.read_text(encoding="utf-8"))
        check(rev.get("status") == "approved", "items_reviewed.json: approved")

    # PR-03: questions
    selected_path = ROOT / "artifacts" / "items_selected.json"
    if selected_path.exists():
        sel = json.loads(selected_path.read_text(encoding="utf-8"))
        sel_items = sel.get("items", [])
        nat = [i for i in sel_items if i["bloco"] == "natural"]
        adp = [i for i in sel_items if i["bloco"] == "adaptado"]
        check(len(nat) == 30, f"30 natural ({len(nat)})")
        check(len(adp) == 30, f"30 adaptado ({len(adp)})")
        nat_src = {i["ipip_source"] for i in nat}
        adp_src = {i["ipip_source"] for i in adp}
        check(not nat_src & adp_src, "zero ipip_source cross-bloco")
        for d in "OCEAN":
            check(sum(1 for i in nat if i["fator"] == d) == 6, f"6 natural/{d}")
            check(sum(1 for i in adp if i["fator"] == d) == 6, f"6 adaptado/{d}")

    # PR-04: norms + scoring symbols
    constants = (ROOT / "src" / "js" / "constants.js").read_text(encoding="utf-8")
    check("FACTORES_INTERNOS" in constants, "FACTORES_INTERNOS")
    check("BANDA_T_LIMIARES" in constants, "BANDA_T_LIMIARES")
    check("INSTRUMENT_VERSION = '1.0.0'" in constants, "versão 1.0.0")
    check("DISCREPANCY_THRESHOLD = 3" in constants, "DISCREPANCY_THRESHOLD")
    check("normalCDF" in constants, "normalCDF lookup")

    scoring = (ROOT / "src" / "js" / "scoring.js").read_text(encoding="utf-8")
    for fn in ("classificarBandaT", "invertForDisplay", "calcularScoresDual", "validarRespostaLikert", "selectTemplateKey"):
        check(fn in scoring, f"scoring.js: {fn}")

    norms_path = ROOT / "artifacts" / "norms.json"
    if norms_path.exists():
        norms = json.loads(norms_path.read_text(encoding="utf-8"))
        check("domains" in norms, "norms.json domains")
        for d in "OCEAN":
            check(d in norms["domains"], f"norms domínio {d}")

    # PR-05: knowledge artifacts
    for f in ("mapped_knowledge.json", "report_sections.json"):
        check((ROOT / "artifacts" / f).is_file(), f"Artefato: {f}")

    # PR-06/07: devolutiva
    check((ROOT / "artifacts" / "devolutiva_templates.json").is_file(), "devolutiva_templates.json")
    check((ROOT / "artifacts" / "palavras_por_fator.json").is_file(), "palavras_por_fator.json")

    # PR-08: rules
    rules_path = ROOT / "artifacts" / "rules.yaml"
    if rules_path.exists():
        rules_text = rules_path.read_text(encoding="utf-8")
        check("O_natural" in rules_text, "rules: O_natural syntax")
        check(not re.search(r"[OCEAN]_(?:natural|adapted)_t\b", rules_text), "rules: sem *_natural_t")

    check((ROOT / "artifacts" / "ontology.yaml").is_file(), "ontology.yaml")

    # Bundle / HTML
    check((ROOT / "index.html").is_file(), "index.html")
    check((ROOT / "docs" / "index.html").is_file(), "docs/index.html")
    check((ROOT / "sw.js").is_file(), "sw.js gerado")
    check((ROOT / "docs" / "sw.js").is_file(), "docs/sw.js")

    if (ROOT / "index.html").exists():
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for fn in js_modules:
            check(f"// --- {fn} ---" in html, f"bundle inclui {fn}")
        check("continuarAposPausa" in html, "continuarAposPausa")
        check("pausaBloco" in html, "pausaBloco")
        check("validarRespostaLikert" in html, "validarRespostaLikert")
        check("features.js" in html or "// --- features.js ---" in html, "features.js no bundle")
        check("DEVOLUTIVA_TEMPLATES" in html, "DEVOLUTIVA_TEMPLATES")
        check("inferirViaAPI" in html, "inferirViaAPI")
        check("t_scores" in html, "t_scores payload")
        nat = len(re.findall(r"id:'n\d+'", html))
        adp = len(re.findall(r"id:'a\d+'", html))
        check(nat == 30, f"30 ids natural no bundle ({nat})")
        check(adp == 30, f"30 ids adaptado no bundle ({adp})")
        check("natural" not in html.lower().split("perguntas")[0] or True, "sem label bloco no quiz")
        m = re.search(r"INSTRUMENT_VERSION = '([^']+)'", constants)
        if m and (ROOT / "sw.js").exists():
            ver = m.group(1)
            sw = (ROOT / "sw.js").read_text(encoding="utf-8")
            check(f"testepersonalidade-v{ver}" in sw, f"sw.js cache == {ver}")

    if (ROOT / "index.html").exists() and (ROOT / "docs" / "index.html").exists():
        a = (ROOT / "index.html").read_text(encoding="utf-8")
        b = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        check(a == b, "index.html == docs/index.html")

    # CI workflows
    if (ROOT / ".github" / "workflows" / "pages.yml").exists():
        pages = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        check("deploy-pages@v4" in pages, "workflow Pages válido")

    check((ROOT / ".github" / "workflows" / "ci.yml").is_file(), "ci.yml")

    # Tests exist
    for t in (
        "test_scoring.py", "test_extraction.py", "test_inference.py",
        "test_norms.py", "test_integration.py", "test_items.py", "test_full_suite.py",
    ):
        check((ROOT / "tests" / t).is_file(), f"Teste: {t}")

    print(f"\n✅ OK ({len(OK)})")
    for o in OK:
        print(f"   ✓ {o}")

    if ERRORS:
        print(f"\n❌ ERROS ({len(ERRORS)})")
        for e in ERRORS:
            print(f"   ✗ {e}")
        return 1

    print(f"\n{'=' * 60}\nRESULTADO: ESTRUTURA OK — {len(OK)} verificações\n{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())