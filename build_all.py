#!/usr/bin/env python3
"""Pipeline completo TESTEPERSONALIDADE — 8 etapas."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALLOW_INCOMPLETE = os.environ.get("ALLOW_INCOMPLETE") == "1"

STEPS = [
    ("scripts/extract_knowledge.py", "Extração PDFs MODELOS/"),
    ("scripts/build_devolutiva_templates.py", "Base devolutivas"),
    ("scripts/generate_questions.py", "Seleção 60 itens IPIP pt-BR"),
    ("scripts/build_norms.py", "Normas bootstrap T-score"),
    ("scripts/generate_rules.py", "Regras interpretação OCEAN"),
    ("build_complete.py", "Build index.html"),
    ("verify_structure.py", "Auditoria estrutural"),
    ("run_tests.py", "Testes pytest"),
]


def run_step(script: str, label: str) -> int:
    path = ROOT / script
    if ALLOW_INCOMPLETE and not path.exists():
        print(f"⏭ SKIP (stub ausente): {script}")
        return 0
    print(f"\n{'=' * 50}\n▶ {label}\n{'=' * 50}")
    result = subprocess.run([sys.executable, str(path)], cwd=str(ROOT))
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline TESTEPERSONALIDADE")
    parser.add_argument("--step", help="Executa apenas etapa cujo script contém este nome")
    args = parser.parse_args()

    steps = STEPS
    if args.step:
        steps = [(s, l) for s, l in STEPS if args.step in s]
        if not steps:
            print(f"Etapa não encontrada: {args.step}")
            return 1

    items_json = ROOT / "artifacts" / "items.json"
    if not items_json.exists() and (not args.step or "translate" in (args.step or "")):
        print("\n▶ Pool IPIP ausente — gerando items.json")
        if run_step("scripts/translate_items.py", "Pool IPIP-NEO-120") != 0:
            return 1

    for script, label in steps:
        if run_step(script, label) != 0:
            print(f"\n✗ Falhou em: {label}")
            return 1

    print("\n✓ Pipeline completo com sucesso!")
    print(f"  Abra: {ROOT / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())