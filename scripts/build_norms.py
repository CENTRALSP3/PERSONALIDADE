#!/usr/bin/env python3
"""Gera artifacts/norms.json — bootstrap literatura ou empírico via DB."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "artifacts" / "norms.json"
DB_PATH = BASE / "data" / "testepersonalidade.db"

# Valores bootstrap de DESIGN.md (literatura OCEAN adultos Brasil)
BOOTSTRAP = {
    "O": {"mean": 3.35, "sd": 0.72},
    "C": {"mean": 3.52, "sd": 0.68},
    "E": {"mean": 3.18, "sd": 0.75},
    "A": {"mean": 3.61, "sd": 0.65},
    "N": {"mean": 2.89, "sd": 0.78},
}


def empirical_norms(min_n: int = 200) -> dict[str, dict] | None:
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(DB_PATH)
    try:
        count = conn.execute("SELECT COUNT(DISTINCT session_id) FROM responses").fetchone()[0]
        if count < min_n:
            return None
        domains: dict[str, dict] = {}
        for factor in "OCEAN":
            rows = conn.execute(
                """
                SELECT AVG(likert_value) AS mu,
                       COUNT(*) AS n
                FROM responses
                WHERE factor = ? AND likert_value BETWEEN 1 AND 5
                """,
                (factor,),
            ).fetchone()
            if not rows or rows[1] < 30:
                return None
            # Estimativa simplificada de DP
            vals = [r[0] for r in conn.execute(
                "SELECT likert_value FROM responses WHERE factor = ?", (factor,)
            ).fetchall()]
            mu = sum(vals) / len(vals)
            var = sum((v - mu) ** 2 for v in vals) / max(len(vals) - 1, 1)
            sd = max(var ** 0.5, 0.3)
            domains[factor] = {"mean": round(mu, 3), "sd": round(sd, 3)}
        return domains
    finally:
        conn.close()


def main() -> int:
    empirical = empirical_norms()
    source = "bootstrap_literature_2026"
    sample_size = 500
    domains = BOOTSTRAP

    if empirical:
        source = "empirical_responses"
        sample_size = 200
        domains = empirical

    data = {
        "meta": {
            "version": "1.0.0",
            "sample_size": sample_size,
            "source": source,
            "population": "adultos_brasil_18_65",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        "domains": domains,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ {OUT} (source={source})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())