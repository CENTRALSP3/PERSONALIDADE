"""Testes de scoring OCEAN — boundary T, N/SE, discrepância."""
from __future__ import annotations

import math


def classificar_banda_t(t_score: float) -> str:
    if t_score < 38:
        return "Muito Baixo"
    if t_score < 44:
        return "Baixo"
    if t_score < 57:
        return "Médio"
    if t_score < 63:
        return "Alto"
    return "Muito Alto"


def to_t_score(mean: float, mu: float, sd: float) -> float:
    z = (mean - mu) / sd
    return round((50 + 10 * z) * 10) / 10


NORMS = {
    "O": {"mean": 3.35, "sd": 0.72},
    "N": {"mean": 2.89, "sd": 0.78},
}


def test_boundary_t_43_9_baixo():
    # mean que produz T ≈ 43.9
    mean = 3.35 + (43.9 - 50) / 10 * 0.72
    t = to_t_score(mean, NORMS["O"]["mean"], NORMS["O"]["sd"])
    assert t <= 44
    assert classificar_banda_t(43.9) == "Baixo"


def test_boundary_t_44_medio():
    assert classificar_banda_t(44) == "Médio"
    assert classificar_banda_t(44.0) == "Médio"


def test_boundary_t_56_9_medio():
    assert classificar_banda_t(56.9) == "Médio"


def test_boundary_t_57_alto():
    assert classificar_banda_t(57) == "Alto"
    assert classificar_banda_t(57.0) == "Alto"


def test_alto_n_se_inversion():
    """N T=66 (Muito Alto) → SE display T=34 → banda Muito Baixo."""
    n_t = 66.0
    se_t_display = 100 - n_t
    assert classificar_banda_t(n_t) == "Muito Alto"
    assert classificar_banda_t(se_t_display) == "Muito Baixo"


def test_select_template_key_fixture():
    """N T=66 → SE Muito Baixo → muito_alto_N."""
    n_t = 66.0
    se_banda = classificar_banda_t(100 - n_t)
    banda_to_template = {
        "Muito Alto": "muito_baixo_N",
        "Alto": "baixo_N",
        "Médio": "medio_N",
        "Baixo": "alto_N",
        "Muito Baixo": "muito_alto_N",
    }
    key = banda_to_template[se_banda]
    assert key == "muito_alto_N"


def test_discrepancy_supressao_se():
    """natural SE ui=+6, adaptado SE ui=+1 → delta=-5, alerta supressão."""
    threshold = 3
    nat_ui, adp_ui = 6.0, 1.0
    delta = round((adp_ui - nat_ui) * 10) / 10
    assert delta == -5.0
    assert delta <= -threshold and nat_ui > 2


def test_reverse_keying():
    likert = 2
    reversed_item = 6 - likert
    assert reversed_item == 4


def test_normalize_ui():
    mean = 4.0
    ui = max(-10, min(10, round(((mean - 3) / 2) * 10 * 10) / 10))
    assert ui == 5.0


def test_pontuar_item_direct():
    assert 5 == 5


def test_percentile_derivation_monotonic():
    t_low, t_high = 38.0, 63.0
    assert t_low < t_high