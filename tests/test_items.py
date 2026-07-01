"""Testes do pool IPIP items.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "artifacts" / "items.json"


def test_items_count():
    data = json.loads(ITEMS.read_text(encoding="utf-8"))
    assert len(data["items"]) == 120


def test_items_per_domain():
    data = json.loads(ITEMS.read_text(encoding="utf-8"))
    for d in "OCEAN":
        items = [i for i in data["items"] if i["domain"] == d]
        assert len(items) == 24


def test_ipip_source_format():
    data = json.loads(ITEMS.read_text(encoding="utf-8"))
    for item in data["items"]:
        d = item["domain"]
        assert re.match(rf"^{d}(?:[1-9]|1\d|2[0-4])$", item["ipip_source"])


def test_reversed_ratio():
    data = json.loads(ITEMS.read_text(encoding="utf-8"))
    reversed_count = sum(1 for i in data["items"] if i["reversed"])
    assert reversed_count >= 40


def test_schema_fields():
    data = json.loads(ITEMS.read_text(encoding="utf-8"))
    required = {"ipip_source", "domain", "facet", "keyed", "text_en", "text_pt", "reversed"}
    for item in data["items"]:
        assert required.issubset(item.keys())