#!/usr/bin/env python3
"""Gera rules.yaml e ontology.yaml — lint sem *_natural_t tokens."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent.parent
RULES_OUT = BASE / "artifacts" / "rules.yaml"
ONTOLOGY_OUT = BASE / "artifacts" / "ontology.yaml"
PHRASES_OUT = BASE / "artifacts" / "phrases.json"

FORBIDDEN_TOKEN = re.compile(r"[OCEAN]_(?:natural|adapted|diff|t)_t\b")

RULES = [
    {
        "id": "RULE_VISIONARIO_DISCIPLINADO",
        "category": "combinacao",
        "when": ["O_natural >= 57", "C_natural >= 57", "E_natural < 44"],
        "interpretation": (
            "Perfil de alta abertura e conscienciosidade com introversão moderada — "
            "combina visão criativa com capacidade de execução estruturada."
        ),
        "confidence": 0.82,
        "evidence": ["literatura_ocean_001", "literatura_ocean_002"],
    },
    {
        "id": "RULE_LIDER_RELACIONAL",
        "category": "combinacao",
        "when": ["E_natural >= 57", "A_natural >= 57"],
        "interpretation": "Perfil socialmente carismático com forte orientação cooperativa.",
        "confidence": 0.78,
        "evidence": ["literatura_ocean_003", "literatura_ocean_004"],
    },
    {
        "id": "RULE_ALTO_N_ESTRESSE",
        "category": "estresse",
        "when": ["N_natural >= 57"],
        "interpretation": "Tendência a reações emocionais intensas sob pressão (neuroticismo elevado).",
        "confidence": 0.80,
        "evidence": ["literatura_ocean_005"],
    },
    {
        "id": "RULE_SUPPRESS_O",
        "category": "discrepancia",
        "when": ["O_natural >= 57", "O_adapted < 44", "O_diff <= -10"],
        "interpretation": "Possível supressão de criatividade no ambiente profissional.",
        "confidence": 0.75,
        "evidence": [],
    },
    {
        "id": "RULE_HIPERADAPT_C",
        "category": "discrepancia",
        "when": ["C_adapted >= 57", "C_natural < 44", "C_diff >= 10"],
        "interpretation": "Possível hiperadaptação de conscienciosidade no trabalho.",
        "confidence": 0.73,
        "evidence": [],
    },
    {
        "id": "RULE_ESTAVEL_EMOCIONAL",
        "category": "perfil",
        "when": ["N_natural < 38"],
        "interpretation": "Estabilidade emocional elevada (baixo neuroticismo canônico).",
        "confidence": 0.85,
        "evidence": ["literatura_ocean_005"],
    },
    {
        "id": "RULE_O_T_ALIAS",
        "category": "perfil",
        "when": ["O_t >= 57"],
        "interpretation": "Alta abertura no contexto natural (via alias O_t).",
        "confidence": 0.70,
        "evidence": [],
    },
    {
        "id": "RULE_O_FALLBACK",
        "category": "perfil",
        "when": ["O >= 57"],
        "interpretation": "Alta abertura (alias O ≡ O_natural).",
        "confidence": 0.70,
        "evidence": [],
    },
]

ONTOLOGY = {
    "Abertura": {
        "codigo": "O",
        "facetas": ["Fantasia", "Estética", "Sentimentos", "Ações", "Ideias", "Valores"],
    },
    "Conscienciosidade": {
        "codigo": "C",
        "facetas": ["Competência", "Ordem", "Dever", "Esforço", "Autodisciplina", "Deliberação"],
    },
    "Extroversão": {
        "codigo": "E",
        "facetas": ["Cordialidade", "Sociabilidade", "Assertividade", "Atividade", "BuscaExcitação", "EmoçõesPositivas"],
    },
    "Amabilidade": {
        "codigo": "A",
        "facetas": ["Confiança", "Franqueza", "Altruísmo", "Complacência", "Modéstia", "Sensibilidade"],
    },
    "Neuroticismo": {
        "codigo": "N",
        "display": "Estabilidade Emocional",
        "facetas": ["Ansiedade", "Hostilidade", "Depressão", "Autoconsciência", "Impulsividade", "Vulnerabilidade"],
    },
}


def lint_rules(rules: list[dict]) -> list[str]:
    errors = []
    for rule in rules:
        for cond in rule.get("when", []):
            if FORBIDDEN_TOKEN.search(cond):
                errors.append(f"{rule['id']}: token proibido em '{cond}'")
    return errors


def main() -> int:
    errors = lint_rules(RULES)
    if errors:
        for e in errors:
            print(f"✗ LINT: {e}", file=sys.stderr)
        return 1

    RULES_OUT.parent.mkdir(parents=True, exist_ok=True)
    with RULES_OUT.open("w", encoding="utf-8") as f:
        yaml.dump(RULES, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    with ONTOLOGY_OUT.open("w", encoding="utf-8") as f:
        yaml.dump(ONTOLOGY, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    PHRASES_OUT.write_text(
        json.dumps({"meta": {"version": "1.0.0"}, "phrases": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✓ {RULES_OUT} ({len(RULES)} regras, lint OK)")
    print(f"✓ {ONTOLOGY_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())