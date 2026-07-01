"""
API FastAPI do TESTEPERSONALIDADE — inferência OCEAN, coleta item-level, share.
"""
from __future__ import annotations

import json
import os
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from api.database import Database
from api.inference import FACTORS, infer_profile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "knowledge.json")
ONTOLOGY_PATH = os.path.join(BASE_DIR, "artifacts", "ontology.yaml")
RULES_PATH = os.path.join(BASE_DIR, "artifacts", "rules.yaml")
NORMS_PATH = os.path.join(BASE_DIR, "artifacts", "norms.json")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
INDEX_PATH = os.path.join(DOCS_DIR, "index.html")


def load_yaml_rules(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        for doc in yaml.safe_load_all(f):
            if isinstance(doc, list):
                return doc
    return []


def load_yaml_ontology(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)
ONTOLOGY = load_yaml_ontology(ONTOLOGY_PATH)
RULES = load_yaml_rules(RULES_PATH)
with open(NORMS_PATH, "r", encoding="utf-8") as f:
    NORMS = json.load(f)

db = Database()
app = FastAPI(title="TESTEPERSONALIDADE API", version="1.0.0")


class TScores(BaseModel):
    O: float
    C: float
    E: float
    A: float
    N: float


class InferRequest(BaseModel):
    t_scores: dict[str, TScores]
    ui_scores: dict[str, dict] | None = None
    share: bool = False


class ResponseItem(BaseModel):
    session_id: str | None = None
    instrument_version: str | None = None
    block: str | None = None
    question_id: str | None = None
    likert_value: int | None = Field(None, ge=1, le=5)
    factor: str | None = None
    responses: list[dict[str, Any]] | None = None


def build_display_scores(t_scores: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """UI scores cosméticos com slot SE."""
    display: dict[str, dict[str, float]] = {"natural": {}, "adapted": {}}
    for ctx in ("natural", "adapted"):
        for f in FACTORS:
            mean_proxy = (t_scores[ctx][f] - 50) / 10 * 0.2 + 3
            ui = max(-10, min(10, round(((mean_proxy - 3) / 2) * 10 * 10) / 10))
            key = "SE" if f == "N" else f
            if f == "N":
                ui = -ui
            display[ctx][key] = ui
    return display


@app.get("/", response_class=FileResponse)
def serve_ui():
    if not os.path.isfile(INDEX_PATH):
        raise HTTPException(status_code=404, detail="UI not found")
    return FileResponse(INDEX_PATH)


if os.path.isdir(DOCS_DIR):
    app.mount("/static", StaticFiles(directory=DOCS_DIR), name="static")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "rules_loaded": len(RULES),
        "norms_version": NORMS.get("meta", {}).get("version"),
    }


@app.get("/ontology")
def get_ontology():
    return ONTOLOGY


@app.get("/norms")
def get_norms():
    return NORMS


@app.get("/rules/meta")
def rules_meta():
    return {"count": len(RULES), "ids": [r.get("id") for r in RULES]}


@app.post("/infer")
def infer(payload: InferRequest):
    t_raw = {
        "natural": payload.t_scores["natural"].model_dump(),
        "adapted": payload.t_scores["adapted"].model_dump(),
    }
    result = infer_profile(RULES, t_raw)
    if not result.get("profile"):
        raise HTTPException(status_code=404, detail="No matching rule found")

    display_scores = build_display_scores(t_raw)
    response: dict[str, Any] = {
        "profile": result["profile"],
        "interpretation": result["interpretation"],
        "confidence": result["confidence"],
        "evidence": result.get("evidence", []),
        "matched_rules": result.get("matched_rules", []),
        "category": result.get("category"),
        "display_scores": display_scores,
        "t_scores": t_raw,
    }

    if payload.share:
        result_hash = db.save_shared_result(
            display_scores, t_raw, inference=response,
            instrument_version=NORMS.get("meta", {}).get("version"),
        )
        response["share_hash"] = result_hash
        response["share_url"] = f"/result/{result_hash}"

    return response


@app.post("/responses")
def collect_responses(payload: ResponseItem):
    saved_ids: list[int] = []
    if payload.responses:
        for item in payload.responses:
            row = {**item}
            if payload.session_id and "session_id" not in row:
                row["session_id"] = payload.session_id
            if payload.instrument_version:
                row["instrument_version"] = payload.instrument_version
            saved_ids.append(db.save_response(row))
    else:
        saved_ids.append(db.save_response(payload.model_dump(exclude_none=True)))
    return {"saved": len(saved_ids), "ids": saved_ids}


@app.get("/analytics")
def analytics():
    return db.get_analytics()


@app.get("/result/{result_hash}")
def get_result(result_hash: str):
    row = db.get_shared_result(result_hash)
    if not row:
        raise HTTPException(status_code=404, detail="Result not found")
    return row