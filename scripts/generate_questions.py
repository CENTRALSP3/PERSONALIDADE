#!/usr/bin/env python3
"""Seleciona 60 itens (6/fator/contexto) e gera questions.js."""
from __future__ import annotations

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ITEMS_PATH = BASE / "artifacts" / "items.json"
REVIEWED_PATH = BASE / "artifacts" / "items_reviewed.json"
OUT_SELECTED = BASE / "artifacts" / "items_selected.json"
OUT_JS = BASE / "src" / "js" / "questions.js"

DOMAINS = ["O", "C", "E", "A", "N"]
ITEMS_PER_FACTOR = 6

# Textos adaptados profissionais (independentes do natural — D13)
ADAPTED_TEXTS: dict[str, list[str]] = {
    "O": [
        "No trabalho, busco abordagens criativas para resolver problemas.",
        "Valorizo inovação e novas perspectivas na equipe.",
        "Gosto de explorar métodos não convencionais no ambiente profissional.",
        "Prefiro rotinas estabelecidas no escritório.",
        "Evito experimentar novas ferramentas no trabalho.",
        "Não me interesso por tendências do setor.",
        "Proponho ideias originais em reuniões de equipe.",
        "Aprecio ambientes de trabalho esteticamente agradáveis.",
        "Busco aprender sobre diferentes áreas além da minha função.",
        "Sigo procedimentos tradicionais sem questionar.",
        "Considero reflexão estratégica parte importante do meu trabalho.",
        "Desinteresso-me por debates conceituais no ambiente profissional.",
    ],
    "C": [
        "Cumpro prazos e compromissos profissionais com rigor.",
        "Organizo minhas tarefas de forma sistemática no trabalho.",
        "Assumo responsabilidade pelos resultados da equipe.",
        "Negligencio detalhes quando estou sob pressão no trabalho.",
        "Mantenho minha área de trabalho arrumada e funcional.",
        "Deixo tarefas pendentes para depois no ambiente profissional.",
        "Planejo minha semana de trabalho com antecedência.",
        "Sou meticuloso com a qualidade das entregas.",
        "Persisto até concluir projetos com excelência.",
        "Faço apenas o mínimo exigido pela função.",
        "Evito distrações durante o horário de trabalho.",
        "Avalio riscos antes de tomar decisões profissionais.",
    ],
    "E": [
        "Sinto-me energizado em reuniões com muitas pessoas.",
        "Tomo a iniciativa de apresentar ideias em grupo.",
        "Construo redes de contato no ambiente profissional.",
        "Prefiro trabalhar sozinho a interagir com a equipe.",
        "Evito participar de eventos corporativos sociais.",
        "Mantenho-me reservado em reuniões de equipe.",
        "Facilito a integração de novos colegas.",
        "Gosto de liderar apresentações para o time.",
        "Busco interação frequente com colegas de trabalho.",
        "Mantenho ritmo acelerado de atividades profissionais.",
        "Procuro desafios estimulantes no trabalho.",
        "Transmito entusiasmo para a equipe no ambiente profissional.",
    ],
    "A": [
        "Confio nas intenções dos meus colegas de trabalho.",
        "Colaboro de forma harmoniosa com a equipe.",
        "Me preocupo com o bem-estar dos colegas.",
        "Priorizo meus interesses sobre os da equipe.",
        "Sou direto mesmo quando isso pode incomodar colegas.",
        "Tenho dificuldade em fazer concessões no trabalho.",
        "Busco entender o ponto de vista dos outros no trabalho.",
        "Mantenho relações cordiais com todos na empresa.",
        "Ofereço ajuda quando colegas precisam.",
        "Negocio de forma equilibrada em conflitos profissionais.",
        "Reconheço as contribuições dos outros na equipe.",
        "Sou atento às necessidades emocionais dos colegas.",
    ],
    "N": [
        "Fico ansioso com prazos apertados no trabalho.",
        "Me preocupo excessivamente com erros profissionais.",
        "Fico abalado com críticas no ambiente de trabalho.",
        "Mantenho calma mesmo em situações de alta pressão.",
        "Raramente me sinto estressado no trabalho.",
        "Lido bem com incertezas profissionais.",
        "Fico irritado facilmente com colegas difíceis.",
        "Me sinto desanimado quando projetos não saem como planejado.",
        "Entro em pânico diante de imprevistos no trabalho.",
        "Duvido das minhas capacidades profissionais com frequência.",
        "Me sinto vulnerável em apresentações importantes.",
        "Tenho dificuldade em controlar reações em reuniões tensas.",
    ],
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def load_pool() -> list[dict]:
    if not REVIEWED_PATH.exists():
        raise FileNotFoundError(f"Gate de revisão ausente: {REVIEWED_PATH}")
    reviewed = json.loads(REVIEWED_PATH.read_text(encoding="utf-8"))
    if reviewed.get("status") != "approved":
        raise ValueError("items_reviewed.json deve ter status: approved")
    data = json.loads(ITEMS_PATH.read_text(encoding="utf-8"))
    return data["items"]


def select_items(pool: list[dict]) -> tuple[list[dict], list[dict]]:
    by_domain: dict[str, list[dict]] = {d: [] for d in DOMAINS}
    for item in pool:
        by_domain[item["domain"]].append(item)

    natural_selected: list[dict] = []
    adapted_selected: list[dict] = []
    used_natural: set[str] = set()
    used_adapted: set[str] = set()
    used_stems: set[str] = set()

    for domain in DOMAINS:
        items = sorted(by_domain[domain], key=lambda x: x["ipip_source"])
        # Natural: ímpares primeiro (O1,O3..), depois pares reversos
        nat_candidates = [i for i in items if i["ipip_source"] not in used_natural]
        nat_picked: list[dict] = []
        reversed_count = 0
        for cand in nat_candidates:
            if len(nat_picked) >= ITEMS_PER_FACTOR:
                break
            stem = normalize(cand["text_pt"])
            if stem in used_stems:
                continue
            nat_picked.append(cand)
            used_natural.add(cand["ipip_source"])
            used_stems.add(stem)
            if cand["reversed"]:
                reversed_count += 1
        # Garantir ≥2 reversed
        if reversed_count < 2:
            for cand in nat_candidates:
                if cand in nat_picked:
                    continue
                if not cand["reversed"]:
                    continue
                if len(nat_picked) >= ITEMS_PER_FACTOR:
                    break
                # substituir último não-reversed
                for j in range(len(nat_picked) - 1, -1, -1):
                    if not nat_picked[j]["reversed"]:
                        old = nat_picked[j]
                        used_natural.discard(old["ipip_source"])
                        used_stems.discard(normalize(old["text_pt"]))
                        nat_picked[j] = cand
                        used_natural.add(cand["ipip_source"])
                        used_stems.add(normalize(cand["text_pt"]))
                        reversed_count += 1
                        break

        # Adapted: itens diferentes (O2,O4.. etc)
        adp_candidates = [i for i in items if i["ipip_source"] not in used_natural and i["ipip_source"] not in used_adapted]
        adp_picked: list[dict] = []
        adp_reversed = 0
        adp_texts = ADAPTED_TEXTS[domain]
        for idx, cand in enumerate(adp_candidates):
            if len(adp_picked) >= ITEMS_PER_FACTOR:
                break
            text = adp_texts[len(adp_picked)] if len(adp_picked) < len(adp_texts) else cand["text_pt"]
            stem = normalize(text)
            if stem in used_stems:
                continue
            adp_picked.append({**cand, "text_pt_adapted": text})
            used_adapted.add(cand["ipip_source"])
            used_stems.add(stem)
            if cand["reversed"]:
                adp_reversed += 1

        if len(nat_picked) < ITEMS_PER_FACTOR or len(adp_picked) < ITEMS_PER_FACTOR:
            raise ValueError(f"Seleção insuficiente para domínio {domain}")

        natural_selected.extend(nat_picked)
        adapted_selected.extend(adp_picked)

    return natural_selected, adapted_selected


def build_output(natural: list[dict], adapted: list[dict]) -> list[dict]:
    items = []
    for i, src in enumerate(natural, 1):
        items.append({
            "id": f"n{i:02d}",
            "bloco": "natural",
            "texto": src["text_pt"],
            "fator": src["domain"],
            "faceta": src["facet"],
            "reversed": src["reversed"],
            "ipip_source": src["ipip_source"],
            "theme": src["facet"].lower(),
        })
    for i, src in enumerate(adapted, 1):
        items.append({
            "id": f"a{i:02d}",
            "bloco": "adaptado",
            "texto": src.get("text_pt_adapted", src["text_pt"]),
            "fator": src["domain"],
            "faceta": src["facet"],
            "reversed": src["reversed"],
            "ipip_source": src["ipip_source"],
            "theme": f"{src['facet'].lower()}_profissional",
        })
    return items


def write_js(items: list[dict]) -> None:
    natural = [i for i in items if i["bloco"] == "natural"]
    adapted = [i for i in items if i["bloco"] == "adaptado"]

    def fmt_q(q: dict) -> str:
        return (
            f"{{id:'{q['id']}',texto:{json.dumps(q['texto'], ensure_ascii=False)},"
            f"fator:'{q['fator']}',bloco:'{q['bloco']}',reversed:{str(q['reversed']).lower()},"
            f"ipip_source:'{q['ipip_source']}'}}"
        )

    lines = [
        "// Gerado por scripts/generate_questions.py — NÃO editar manualmente",
        f"const PERGUNTAS_NATURAL = [{', '.join(fmt_q(q) for q in natural)}];",
        f"const PERGUNTAS_ADAPTADO = [{', '.join(fmt_q(q) for q in adapted)}];",
        "const PERGUNTAS_ALL = [...PERGUNTAS_NATURAL, ...PERGUNTAS_ADAPTADO];",
        "const ITEM_MAP = Object.fromEntries(PERGUNTAS_ALL.map(q => [q.id, {",
        "  id: q.id, fator: q.fator, bloco: q.bloco, reversed: q.reversed, ipip_source: q.ipip_source,",
        "} ]));",
        "const TOTAL_POR_BLOCO = 30;",
        "",
    ]
    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    OUT_JS.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    pool = load_pool()
    natural, adapted = select_items(pool)
    items = build_output(natural, adapted)

    # Validações
    nat_sources = {i["ipip_source"] for i in items if i["bloco"] == "natural"}
    adp_sources = {i["ipip_source"] for i in items if i["bloco"] == "adaptado"}
    assert not nat_sources & adp_sources, "ipip_source compartilhado entre blocos"
    stems = [normalize(i["texto"]) for i in items]
    assert len(stems) == len(set(stems)), "stems duplicados"

    selected = {
        "meta": {
            "instrument_version": "1.0.0",
            "source": "IPIP-NEO-120 + custom",
            "total_items": 60,
            "items_per_factor_per_context": 6,
        },
        "items": items,
    }
    OUT_SELECTED.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    write_js(items)
    print(f"✓ {OUT_SELECTED} — {len(items)} itens")
    print(f"✓ {OUT_JS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())