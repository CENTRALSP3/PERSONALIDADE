"""
Persistência SQLite — respostas item-level e resultados compartilhados OCEAN.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "testepersonalidade.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    instrument_version TEXT,
    block TEXT,
    question_id TEXT,
    factor TEXT,
    likert_value INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS shared_results (
    hash TEXT PRIMARY KEY,
    display_scores TEXT,
    t_scores TEXT,
    inference TEXT,
    instrument_version TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_responses_session ON responses(session_id);
CREATE INDEX IF NOT EXISTS idx_responses_factor ON responses(factor);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def save_response(self, row: dict[str, Any]) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO responses (
                    session_id, instrument_version, block,
                    question_id, factor, likert_value, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id") or "anonymous",
                    row.get("instrument_version"),
                    row.get("block"),
                    row.get("question_id"),
                    row.get("factor"),
                    row.get("likert_value"),
                    utc_now(),
                ),
            )
            return int(cur.lastrowid)

    def save_responses_batch(self, session_id: str, items: list[dict[str, Any]], instrument_version: str | None = None) -> list[int]:
        ids = []
        for item in items:
            row = {**item, "session_id": session_id, "instrument_version": instrument_version}
            ids.append(self.save_response(row))
        return ids

    def save_shared_result(
        self,
        display_scores: dict[str, Any],
        t_scores: dict[str, Any],
        inference: dict[str, Any] | None = None,
        instrument_version: str | None = None,
        result_hash: str | None = None,
    ) -> str:
        result_hash = result_hash or uuid4().hex[:16]
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO shared_results (
                    hash, display_scores, t_scores, inference, instrument_version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    result_hash,
                    json.dumps(display_scores, ensure_ascii=False),
                    json.dumps(t_scores, ensure_ascii=False),
                    json.dumps(inference, ensure_ascii=False) if inference else None,
                    instrument_version,
                    utc_now(),
                ),
            )
        return result_hash

    def get_shared_result(self, result_hash: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM shared_results WHERE hash = ?",
                (result_hash,),
            ).fetchone()
        if not row:
            return None
        return {
            "hash": row["hash"],
            "instrument_version": row["instrument_version"],
            "display_scores": json.loads(row["display_scores"]) if row["display_scores"] else {},
            "t_scores": json.loads(row["t_scores"]) if row["t_scores"] else {},
            "inference": json.loads(row["inference"]) if row["inference"] else None,
            "created_at": row["created_at"],
        }

    def get_analytics(self) -> dict[str, Any]:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
            sessions = conn.execute(
                "SELECT COUNT(DISTINCT session_id) FROM responses"
            ).fetchone()[0]
            by_factor = {
                row["factor"]: row["cnt"]
                for row in conn.execute(
                    "SELECT factor, COUNT(*) AS cnt FROM responses GROUP BY factor"
                ).fetchall()
            }
            likert_hist = {
                str(row["likert_value"]): row["cnt"]
                for row in conn.execute(
                    "SELECT likert_value, COUNT(*) AS cnt FROM responses GROUP BY likert_value"
                ).fetchall()
            }
            high_acquiescence = 0
            if total > 0:
                high = conn.execute(
                    "SELECT COUNT(*) FROM responses WHERE likert_value >= 4"
                ).fetchone()[0]
                high_acquiescence = round(high / total * 100, 1)

        return {
            "total_responses": total,
            "sessions": sessions,
            "by_factor": by_factor,
            "likert_histogram": likert_hist,
            "acquiescence_4_5_pct": high_acquiescence,
        }