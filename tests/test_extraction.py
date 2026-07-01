"""Testes de extração de conhecimento."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_knowledge_json_exists():
    path = ROOT / "knowledge.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data.get("documents", [])) >= 5


def test_mapped_knowledge():
    path = ROOT / "artifacts" / "mapped_knowledge.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "fatores" in data


def test_report_sections():
    path = ROOT / "artifacts" / "report_sections.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data.get("sections", [])) >= 5