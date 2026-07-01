#!/usr/bin/env python3
"""Gera devolutiva_templates.json e módulos JS derivados."""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MAPPED = BASE / "artifacts" / "mapped_knowledge.json"
OUT_JSON = BASE / "artifacts" / "devolutiva_templates.json"
OUT_PALAVRAS = BASE / "artifacts" / "palavras_por_fator.json"
OUT_JS_TPL = BASE / "src" / "js" / "devolutiva-templates.js"
OUT_JS_PAL = BASE / "src" / "js" / "palavras-data.js"

FACTOR_LABELS = {
    "O": "Abertura à Experiência",
    "C": "Conscienciosidade",
    "E": "Extroversão",
    "A": "Amabilidade",
    "N": "Estabilidade Emocional",
}

BANDA_KEYS = ["muito_alto", "alto", "medio", "baixo", "muito_baixo"]
N_KEYS = ["muito_alto_N", "alto_N", "medio_N", "baixo_N", "muito_baixo_N"]

TEMPLATES_BASE = {
    "O": {
        "auto_imagem": {
            "muito_alto": ["Você tende a buscar novas experiências e ideias com intensidade notável."],
            "alto": ["Você valoriza criatividade, curiosidade e abertura a perspectivas diferentes."],
            "medio": ["Você equilibra tradição e inovação de forma flexível."],
            "baixo": ["Você prefere o familiar e prático, valorizando estabilidade sobre novidade."],
            "muito_baixo": ["Você tende a ser conservador em suas preferências e abordagens."],
        },
        "pontos_fortes": ["Criatividade", "Curiosidade intelectual", "Flexibilidade mental"],
        "desafios": ["Pode dispersar-se com excesso de opções", "Dificuldade com rotinas rígidas"],
        "relacoes": ["Traz perspectivas originais às conversas e valoriza diálogo profundo."],
        "trabalho": ["Prospera em ambientes que valorizam inovação e aprendizado contínuo."],
        "sob_pressao": ["Busca soluções criativas, mas pode perder foco com muitas alternativas."],
        "crescimento": ["Canalizar criatividade em projetos concretos com prazos definidos."],
    },
    "C": {
        "auto_imagem": {
            "muito_alto": ["Você se define pela organização, disciplina e compromisso com resultados."],
            "alto": ["Você valoriza planejamento, responsabilidade e execução confiável."],
            "medio": ["Você equilibra estrutura e flexibilidade conforme a situação."],
            "baixo": ["Você prefere abordagens espontâneas e menos estruturadas."],
            "muito_baixo": ["Você tende a ser flexível com prazos e procedimentos formais."],
        },
        "pontos_fortes": ["Organização", "Confiabilidade", "Persistência"],
        "desafios": ["Perfeccionismo excessivo", "Rigidez com mudanças"],
        "relacoes": ["É visto como pessoa confiável que cumpre compromissos."],
        "trabalho": ["Destaca-se em funções que exigem planejamento e atenção a detalhes."],
        "sob_pressao": ["Mantém foco e busca soluções estruturadas."],
        "crescimento": ["Delegar e aceitar que 'bom o suficiente' às vezes é adequado."],
    },
    "E": {
        "auto_imagem": {
            "muito_alto": ["Você se energiza com interação social e busca o centro das atividades."],
            "alto": ["Você é sociável, assertivo e traz entusiasmo aos grupos."],
            "medio": ["Você equilibra momentos sociais e de introspecção."],
            "baixo": ["Você prefere ambientes tranquilos e interações em menor escala."],
            "muito_baixo": ["Você tende a ser reservado e valoriza tempo a sós."],
        },
        "pontos_fortes": ["Comunicação", "Energia social", "Liderança interpessoal"],
        "desafios": ["Pode dominar conversas", "Dificuldade com tarefas solitárias"],
        "relacoes": ["Constrói redes amplas e mantém contatos ativos."],
        "trabalho": ["Prospera em funções com interação frequente e apresentações."],
        "sob_pressao": ["Busca apoio social e pode agir impulsivamente."],
        "crescimento": ["Desenvolver escuta ativa e momentos de reflexão solitária."],
    },
    "A": {
        "auto_imagem": {
            "muito_alto": ["Você prioriza harmonia, empatia e cooperação nas relações."],
            "alto": ["Você valoriza gentileza, confiança e trabalho em equipe."],
            "medio": ["Você equilibra assertividade e consideração pelos outros."],
            "baixo": ["Você tende a ser direto e prioriza resultados sobre harmonia."],
            "muito_baixo": ["Você pode ser competitivo e menos inclinado a concessões."],
        },
        "pontos_fortes": ["Empatia", "Cooperação", "Confiança interpessoal"],
        "desafios": ["Dificuldade em dizer não", "Evitar conflitos necessários"],
        "relacoes": ["Cria ambientes acolhedores e de suporte mútuo."],
        "trabalho": ["Excelente em equipes colaborativas e mediação."],
        "sob_pressao": ["Pode absorver estresse dos outros ou evitar confrontos."],
        "crescimento": ["Estabelecer limites saudáveis e praticar assertividade."],
    },
    "N": {
        "_note": "Chaves em escala neuroticismo-interna; devolutiva.js usa selectTemplateKey()",
        "display_name": "Estabilidade Emocional",
        "auto_imagem": {
            "muito_alto_N": ["Tende a reagir com intensidade emocional a situações estressantes."],
            "alto_N": ["Pode experimentar ansiedade ou preocupação sob pressão."],
            "medio_N": ["Reações emocionais dentro da média populacional."],
            "baixo_N": ["Mantém equilíbrio em situações de pressão moderada."],
            "muito_baixo_N": ["Demonstra notável estabilidade emocional mesmo sob estresse intenso."],
        },
        "pontos_fortes": ["Autoconsciência emocional", "Sensibilidade a nuances"],
        "desafios": ["Ansiedade em incertezas", "Reações intensas sob pressão"],
        "relacoes": ["Pode ser muito sensível a dinâmicas interpessoais."],
        "trabalho": ["Funciona melhor com previsibilidade e suporte claro."],
        "sob_pressao": ["Reações emocionais podem intensificar-se em crises."],
        "crescimento": ["Técnicas de regulação emocional e mindfulness."],
    },
}

PALAVRAS = {
    "O": {"alto": ["Criativo", "Curioso", "Imaginativo", "Inovador"], "baixo": ["Prático", "Convencional", "Tradicional"]},
    "C": {"alto": ["Organizado", "Disciplinado", "Confiável", "Metódico"], "baixo": ["Flexível", "Espontâneo", "Descontraído"]},
    "E": {"alto": ["Sociável", "Energético", "Assertivo", "Comunicativo"], "baixo": ["Reservado", "Reflexivo", "Independente"]},
    "A": {"alto": ["Empático", "Cooperativo", "Gentil", "Altruísta"], "baixo": ["Direto", "Competitivo", "Objetivo"]},
    "N": {"alto": ["Sensível", "Vigilante", "Intenso"], "baixo": ["Calmo", "Estável", "Resiliente"]},
}


def enrich_from_mapped(templates: dict) -> dict:
    if not MAPPED.exists():
        return templates
    mapped = json.loads(MAPPED.read_text(encoding="utf-8"))
    for factor, sections in mapped.get("fatores", {}).items():
        if factor not in templates:
            continue
        for sec_key, texts in sections.items():
            if texts and sec_key in templates[factor]:
                if isinstance(templates[factor][sec_key], list):
                    templates[factor][sec_key].extend(texts[:2])
    return templates


def main() -> int:
    templates = enrich_from_mapped(json.loads(json.dumps(TEMPLATES_BASE)))
    doc_count = 5
    if (BASE / "knowledge.json").exists():
        kb = json.loads((BASE / "knowledge.json").read_text(encoding="utf-8"))
        doc_count = len(kb.get("documents", []))

    output = {
        "meta": {
            "source_documents": doc_count,
            "version": "1.0.0",
            "instrument": "TESTEPERSONALIDADE",
            "sections": 12,
        },
        "fatores": templates,
        "combinacoes": {
            "O_alto_C_alto": {
                "titulo": "Visionário Disciplinado",
                "texto": "Combina criatividade com execução estruturada.",
            },
            "E_alto_A_alto": {
                "titulo": "Líder Relacional",
                "texto": "Une carisma social com empatia genuína.",
            },
        },
        "discrepancia": {
            "supressao": ["No ambiente profissional, você pode estar moderando traços naturais."],
            "hiperadaptacao": ["Você pode estar exibindo comportamentos que exigem esforço consciente."],
        },
        "disclaimer": (
            "Este relatório é um instrumento de autoconhecimento e desenvolvimento pessoal. "
            "Não constitui diagnóstico psicológico, psiquiátrico ou avaliação clínica."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_PALAVRAS.write_text(json.dumps(PALAVRAS, ensure_ascii=False, indent=2), encoding="utf-8")

    OUT_JS_TPL.parent.mkdir(parents=True, exist_ok=True)
    OUT_JS_TPL.write_text(
        f"// Gerado por build_devolutiva_templates.py\n"
        f"const DEVOLUTIVA_TEMPLATES = {json.dumps(output, ensure_ascii=False)};\n",
        encoding="utf-8",
    )
    OUT_JS_PAL.write_text(
        f"// Gerado por build_devolutiva_templates.py\n"
        f"const PALAVRAS_POR_FATOR = {json.dumps(PALAVRAS, ensure_ascii=False)};\n",
        encoding="utf-8",
    )
    print(f"✓ {OUT_JSON}")
    print(f"✓ {OUT_JS_TPL}, {OUT_JS_PAL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())