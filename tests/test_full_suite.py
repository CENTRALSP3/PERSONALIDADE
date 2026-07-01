"""Smoke test — pipeline artifacts e estrutura mínima."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_verify_structure_passes():
    result = subprocess.run(
        [sys.executable, "verify_structure.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_items_selected_sync():
    sel = json.loads((ROOT / "artifacts" / "items_selected.json").read_text(encoding="utf-8"))
    qs = (ROOT / "src" / "js" / "questions.js").read_text(encoding="utf-8")
    for item in sel["items"]:
        assert item["id"] in qs


def test_rules_no_forbidden_tokens():
    import re
    text = (ROOT / "artifacts" / "rules.yaml").read_text(encoding="utf-8")
    assert not re.search(r"[OCEAN]_(?:natural|adapted)_t\b", text)