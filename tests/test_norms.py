"""Testes de normas bootstrap."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_norms_structure():
    data = json.loads((ROOT / "artifacts" / "norms.json").read_text(encoding="utf-8"))
    assert data["meta"]["version"] == "1.0.0"
    for d in "OCEAN":
        assert "mean" in data["domains"][d]
        assert "sd" in data["domains"][d]
        assert data["domains"][d]["sd"] > 0


def test_bootstrap_values():
    data = json.loads((ROOT / "artifacts" / "norms.json").read_text(encoding="utf-8"))
    assert data["domains"]["O"]["mean"] == 3.35
    assert data["domains"]["N"]["mean"] == 2.89