"""Testes do motor de inferência OCEAN."""
from __future__ import annotations

import yaml
from fastapi.testclient import TestClient

from api.inference import build_context, evaluate_condition, infer_profile

ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent


def load_rules():
    with open(ROOT / "artifacts" / "rules.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_build_context():
    t_scores = {
        "natural": {"O": 60, "C": 50, "E": 45, "A": 55, "N": 40},
        "adapted": {"O": 55, "C": 58, "E": 48, "A": 52, "N": 42},
    }
    ctx = build_context(t_scores)
    assert ctx["O_natural"] == 60
    assert ctx["O_adapted"] == 55
    assert ctx["O_diff"] == -5
    assert ctx["O_t"] == 60
    assert ctx["O"] == 60


def test_condition_o_natural():
    ctx = build_context({
        "natural": {"O": 58, "C": 50, "E": 50, "A": 50, "N": 50},
        "adapted": {"O": 50, "C": 50, "E": 50, "A": 50, "N": 50},
    })
    assert evaluate_condition("O_natural >= 57", ctx)


def test_condition_o_t_alias():
    ctx = build_context({
        "natural": {"O": 58, "C": 50, "E": 50, "A": 50, "N": 50},
        "adapted": {"O": 50, "C": 50, "E": 50, "A": 50, "N": 50},
    })
    assert evaluate_condition("O_t >= 57", ctx)


def test_condition_o_fallback():
    ctx = build_context({
        "natural": {"O": 58, "C": 50, "E": 50, "A": 50, "N": 50},
        "adapted": {"O": 50, "C": 50, "E": 50, "A": 50, "N": 50},
    })
    assert evaluate_condition("O >= 57", ctx)


def test_n_natural_alto_neuroticismo():
    ctx = build_context({
        "natural": {"O": 50, "C": 50, "E": 50, "A": 50, "N": 60},
        "adapted": {"O": 50, "C": 50, "E": 50, "A": 50, "N": 50},
    })
    assert evaluate_condition("N_natural >= 57", ctx)


def test_infer_visionario():
    rules = load_rules()
    t_scores = {
        "natural": {"O": 60, "C": 60, "E": 40, "A": 50, "N": 50},
        "adapted": {"O": 55, "C": 55, "E": 45, "A": 50, "N": 50},
    }
    result = infer_profile(rules, t_scores)
    assert "RULE_VISIONARIO_DISCIPLINADO" in result["matched_rules"]


def test_api_infer_t_scores():
    from api.main import app
    client = TestClient(app)
    payload = {
        "t_scores": {
            "natural": {"O": 60, "C": 60, "E": 40, "A": 50, "N": 50},
            "adapted": {"O": 55, "C": 55, "E": 45, "A": 50, "N": 50},
        },
    }
    resp = client.post("/infer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "display_scores" in data
    assert "SE" in data["display_scores"]["natural"]


def test_api_reject_disc_payload():
    from api.main import app
    client = TestClient(app)
    payload = {
        "natural": {"D": 5, "I": 2, "S": 1, "C": 0},
        "adapted": {"D": 2, "I": 2, "S": 1, "C": 0},
    }
    resp = client.post("/infer", json=payload)
    assert resp.status_code == 422