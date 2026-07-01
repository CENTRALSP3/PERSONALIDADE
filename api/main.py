"""
API FastAPI do TESTEPERSONALIDADE — inferência OCEAN, coleta item-level, share.
"""
from __future__ import annotations

import json
import os
from typing import Any

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from fpdf import FPDF
import io

try:
    from .database import Database
    from .inference import FACTORS, infer_profile
except ImportError:
    from database import Database
    from inference import FACTORS, infer_profile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "knowledge.json")
ONTOLOGY_PATH = os.path.join(BASE_DIR, "artifacts", "ontology.yaml")
RULES_PATH = os.path.join(BASE_DIR, "artifacts", "rules.yaml")
NORMS_PATH = os.path.join(BASE_DIR, "artifacts", "norms.json")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
INDEX_PATH = os.path.join(DOCS_DIR, "index.html")


def load_yaml_rules(path: str) -> list[dict[str, Any]]:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        for doc in yaml.safe_load_all(f):
            if isinstance(doc, list):
                return doc
    return []


def load_yaml_ontology(path: str) -> dict[str, Any]:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


try:
    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
        KNOWLEDGE = json.load(f)
except Exception:
    KNOWLEDGE = {}
try:
    ONTOLOGY = load_yaml_ontology(ONTOLOGY_PATH)
except Exception:
    ONTOLOGY = {}
try:
    RULES = load_yaml_rules(RULES_PATH)
except Exception:
    RULES = []
try:
    with open(NORMS_PATH, "r", encoding="utf-8") as f:
        NORMS = json.load(f)
except Exception:
    NORMS = {"meta": {"version": "fallback"}, "domains": {}}

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
    try:
        dyn = db.get_dynamic_norms()
        if dyn and dyn.get("domains"):
            # merge or prefer dynamic if has data
            if dyn["meta"].get("sample_size", 0) > 10:
                return dyn
    except Exception:
        pass
    return NORMS

@app.get("/norms/dynamic")
def get_dynamic_norms():
    return db.get_dynamic_norms()


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
        # Graceful fallback instead of 404 error for client
        result["profile"] = "PERFIL_GENERICO"
        result["interpretation"] = "Perfil com pontuações fora dos padrões específicos das regras atuais. Analise as pontuações T, UI e descrições dos 5 domínios + 30 facets no relatório completo para insights personalizados."
        result["confidence"] = 0.5
        result["category"] = "generico"
        result["matched_rules"] = result.get("matched_rules", [])
        result["evidence"] = []

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


# ==================== PDF Generation on Server ====================
class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Relatório de Personalidade OCEAN - Big Five", 0, 1, "C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")


def generate_pdf_bytes(dual: dict, name: str = "Usuário", t_scores: dict | None = None) -> bytes:
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, f"Perfil OCEAN para {name}", ln=True, align="C")
    pdf.ln(8)

    # Scores
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Scores (UI -10 a +10 | T-score)", ln=True)
    pdf.set_font("Helvetica", "", 10)

    for ctx_name, ctx_key in [("Natural", "natural"), ("Adaptado", "adapted")]:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, ctx_name, ln=True)
        pdf.set_font("Helvetica", "", 10)
        scores = dual.get(ctx_key, {})
        for f in ["O", "C", "E", "A", "SE"]:
            val = scores.get(f, {})
            if isinstance(val, dict):
                ui = val.get("ui", 0)
                t = val.get("tScore", 50)
            else:
                ui = val
                t = 50
            pdf.cell(0, 6, f"  {f}: UI={ui:+.1f}  T={t:.1f}", ln=True)
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Interpretação", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, "Este relatório foi gerado no servidor com dados do teste. Consulte o relatório completo no navegador para descrições detalhadas por domínio e facets (30 subtraços).")

    # Add more text if space
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5, "Instrumento baseado em IPIP-NEO. Não substitui avaliação psicológica profissional.")

    return pdf.output(dest="S")  # fpdf2 returns bytearray


@app.post("/pdf")
async def generate_pdf(payload: dict = Body(...)):
    name = payload.get("name", "Usuário")
    dual = payload.get("dual", payload.get("display_scores", {}))  # support different shapes
    t_scores = payload.get("t_scores")
    pdf_bytes = generate_pdf_bytes(dual, name, t_scores)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=relatorio_ocean_{name.replace(' ', '_')}.pdf"},
    )


# ==================== Serverless handler for Vercel (Mangum) ====================
# Ensures FastAPI app works reliably under @vercel/python + serverless
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    # Fallback for local uvicorn run
    handler = None
