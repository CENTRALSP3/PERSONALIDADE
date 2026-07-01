"""Testes de integração API — batch responses, shared results."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from api.database import Database, DEFAULT_DB_PATH

client = TestClient(app)


def test_batch_responses_60():
    import uuid
    session_id = f"test-batch-{uuid.uuid4().hex[:12]}"
    responses = [
        {
            "question_id": f"n{i:02d}" if i <= 30 else f"a{i-30:02d}",
            "block": "natural" if i <= 30 else "adaptado",
            "factor": ["O", "C", "E", "A", "N"][(i - 1) % 5],
            "likert_value": (i % 5) + 1,
        }
        for i in range(1, 61)
    ]
    resp = client.post("/responses", json={
        "session_id": session_id,
        "instrument_version": "1.0.0",
        "responses": responses,
    })
    assert resp.status_code == 200
    assert resp.json()["saved"] == 60

    db = Database()
    with db._connect() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM responses WHERE session_id = ?",
            (session_id,),
        ).fetchone()[0]
    assert count == 60


def test_infer_share_hash():
    payload = {
        "t_scores": {
            "natural": {"O": 60, "C": 60, "E": 40, "A": 50, "N": 50},
            "adapted": {"O": 55, "C": 55, "E": 45, "A": 50, "N": 50},
        },
        "share": True,
    }
    resp = client.post("/infer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "share_hash" in data
    hash_val = data["share_hash"]
    get_resp = client.get(f"/result/{hash_val}")
    assert get_resp.status_code == 200
    result = get_resp.json()
    assert "display_scores" in result
    assert "SE" in result["display_scores"]["natural"]
    assert "N" in result["t_scores"]["natural"]


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_analytics():
    resp = client.get("/analytics")
    assert resp.status_code == 200
    assert "total_responses" in resp.json()