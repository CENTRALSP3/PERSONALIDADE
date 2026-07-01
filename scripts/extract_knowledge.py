#!/usr/bin/env python3
"""Extrai conhecimento OCEAN de MODELOS/ ou gera corpus mínimo."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MODELOS = BASE / "MODELOS"
KNOWLEDGE_PATH = BASE / "knowledge.json"
ARTIFACTS = BASE / "artifacts"

FACTOR_KEYWORDS = {
    "O": {"criativ", "imagina", "curios", "abert", "novidade", "intelectual", "arte", "fantasia"},
    "C": {"organiz", "disciplin", "metódic", "planej", "responsável", "detalh", "confiável", "ordem"},
    "E": {"sociável", "extrovert", "energia", "assertiv", "grupo", "comunicativ", "animado"},
    "A": {"empát", "cooperativ", "amável", "gentil", "confiança", "altruísm", "harmonia"},
    "N": {"ansios", "preocup", "estress", "instável", "irritável", "vulnerável", "emocional"},
}

SECTION_PATTERNS = [
    ("auto_imagem_natural", r"(?:AUTOIMAGEM|AUTO-IMAGEM|PERFIL NATURAL)"),
    ("percepcao_adaptada", r"(?:PERCEPÇÃO ADAPTADA|COMPORTAMENTO NO TRABALHO)"),
    ("pontos_fortes", r"(?:PONTOS FORTES|FORÇAS)"),
    ("desafios", r"(?:DESAFIOS|PONTOS DE ATENÇÃO|ÁREAS DE DESENVOLVIMENTO)"),
    ("relacoes", r"(?:RELACIONAMENTOS|INTERPESSOAL)"),
    ("trabalho", r"(?:CARREIRA|AMBIENTE DE TRABALHO|DESEMPENHO)"),
    ("sob_pressao", r"(?:SOB PRESSÃO|ESTRESSE|ESTABILIDADE EMOCIONAL)"),
    ("crescimento", r"(?:DESENVOLVIMENTO|CRESCIMENTO|RECOMENDAÇÕES)"),
    ("comunicacao", r"COMUNICAÇÃO"),
    ("lideranca", r"LIDERANÇA"),
]

# Corpus mínimo quando não há PDFs
FALLBACK_DOCS = [
    {
        "id": "literatura_ocean_001",
        "title": "Big Five — Abertura à Experiência",
        "source": "literatura_bootstrap",
        "content": (
            "Pessoas com alta Abertura tendem a buscar novas experiências, ideias criativas "
            "e curiosidade intelectual. Valorizam arte, fantasia e inovação. "
            "Pontos fortes incluem criatividade e visão ampla. Desafios podem incluir dispersão."
        ),
    },
    {
        "id": "literatura_ocean_002",
        "title": "Big Five — Conscienciosidade",
        "source": "literatura_bootstrap",
        "content": (
            "Alta Conscienciosidade reflete organização, disciplina e responsabilidade. "
            "No trabalho, destacam-se pelo planejamento e confiabilidade. "
            "Sob pressão, mantêm foco. Crescimento: equilibrar perfeccionismo."
        ),
    },
    {
        "id": "literatura_ocean_003",
        "title": "Big Five — Extroversão",
        "source": "literatura_bootstrap",
        "content": (
            "Extroversão elevada indica energia social, assertividade e entusiasmo. "
            "Relacionamentos prosperam com comunicação ativa. "
            "Carreira: liderança e networking. Desafio: escutar mais."
        ),
    },
    {
        "id": "literatura_ocean_004",
        "title": "Big Five — Amabilidade",
        "source": "literatura_bootstrap",
        "content": (
            "Amabilidade alta manifesta empatia, cooperação e confiança interpessoal. "
            "Pontos fortes: harmonia em equipes. Relacionamentos: gentileza e altruísmo. "
            "Desafio: estabelecer limites saudáveis."
        ),
    },
    {
        "id": "literatura_ocean_005",
        "title": "Big Five — Estabilidade Emocional",
        "source": "literatura_bootstrap",
        "content": (
            "Neuroticismo elevado (baixa estabilidade emocional) associa-se a ansiedade, "
            "preocupação e vulnerabilidade sob estresse. Sob pressão, reações intensas. "
            "Crescimento: técnicas de regulação emocional e autoconsciência."
        ),
    },
]


def try_extract_pdf(path: Path) -> str:
    try:
        import pypdf  # type: ignore
        reader = pypdf.PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""


def map_factor(text: str) -> str | None:
    lower = text.lower()
    scores = {f: sum(1 for kw in kws if kw in lower) for f, kws in FACTOR_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def find_sections(content: str) -> dict[str, str]:
    matches: list[tuple[int, str, re.Match]] = []
    for key, pattern in SECTION_PATTERNS:
        for m in re.finditer(pattern, content, re.IGNORECASE):
            matches.append((m.start(), key, m))
    matches.sort(key=lambda x: x[0])
    sections: dict[str, str] = {}
    for i, (start, key, m) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(content)
        body = re.sub(r"\s+", " ", content[m.end():end]).strip()
        if len(body) > 20:
            sections[key] = (sections.get(key, "") + " " + body).strip()
    return sections


def main() -> int:
    documents = []
    pdfs = list(MODELOS.glob("*.pdf")) if MODELOS.exists() else []

    if pdfs:
        for pdf in pdfs:
            text = try_extract_pdf(pdf)
            if len(text) > 50:
                documents.append({
                    "id": pdf.stem,
                    "title": pdf.name,
                    "source": "MODELOS",
                    "content": text[:50000],
                    "sections": find_sections(text),
                })
    else:
        documents = FALLBACK_DOCS

    knowledge = {
        "meta": {"instrument": "TESTEPERSONALIDADE", "version": "1.0.0", "document_count": len(documents)},
        "documents": documents,
    }
    KNOWLEDGE_PATH.write_text(json.dumps(knowledge, ensure_ascii=False, indent=2), encoding="utf-8")

    mapped: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    report_sections: list[dict] = []

    for doc in documents:
        content = doc.get("content", "")
        factor = map_factor(content) or "O"
        sections = doc.get("sections") or {"geral": content[:2000]}
        for sec_key, sec_text in sections.items():
            mapped[factor][sec_key].append(sec_text[:1500])
            report_sections.append({
                "document_id": doc["id"],
                "factor": factor,
                "section": sec_key,
                "text": sec_text[:1500],
            })

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "mapped_knowledge.json").write_text(
        json.dumps({"fatores": {k: dict(v) for k, v in mapped.items()}}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (ARTIFACTS / "report_sections.json").write_text(
        json.dumps({"sections": report_sections}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✓ knowledge.json — {len(documents)} documentos")
    print(f"✓ mapped_knowledge.json, report_sections.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())