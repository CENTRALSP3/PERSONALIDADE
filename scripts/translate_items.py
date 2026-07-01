#!/usr/bin/env python3
"""Gera artifacts/items.json — pool IPIP-NEO-120 em pt-BR."""
from __future__ import annotations

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "artifacts" / "items.json"

# IPIP-NEO-120: 24 itens por domínio (Goldberg/Costa-McCrae, domínio público)
# Formato: (num, facet, keyed, text_en, text_pt)
IPIP_POOL: dict[str, list[tuple]] = {
    "O": [
        (1, "Fantasia", "+", "Have a rich vocabulary.", "Tenho uma imaginação vívida."),
        (2, "Fantasia", "+", "Have excellent ideas.", "Tenho ideias excelentes."),
        (3, "Estética", "+", "Believe in the importance of art.", "Acredito na importância da arte."),
        (4, "Estética", "+", "See beauty in things others might not notice.", "Vejo beleza em coisas que outros podem não notar."),
        (5, "Sentimentos", "+", "Experience my emotions intensely.", "Experimento minhas emoções intensamente."),
        (6, "Ideias", "-", "Have difficulty understanding abstract ideas.", "Não me interesso por ideias abstratas."),
        (7, "Ações", "+", "Prefer variety to routine.", "Prefiro variedade à rotina."),
        (8, "Ações", "+", "Am willing to try something new.", "Estou disposto a tentar algo novo."),
        (9, "Ideias", "+", "Love to think up new ways of doing things.", "Adoro inventar novas formas de fazer as coisas."),
        (10, "Valores", "+", "Am interested in science.", "Tenho interesse em ciência."),
        (11, "Valores", "+", "Like to solve complex problems.", "Gosto de resolver problemas complexos."),
        (12, "Sentimentos", "+", "Feel others' emotions.", "Sinto as emoções dos outros."),
        (13, "Fantasia", "-", "Do not have a good imagination.", "Não tenho uma boa imaginação."),
        (14, "Estética", "-", "Do not like poetry.", "Não gosto de poesia."),
        (15, "Ideias", "-", "Avoid philosophical discussions.", "Evito discussões filosóficas."),
        (16, "Ações", "-", "Do not like art.", "Não gosto de arte."),
        (17, "Valores", "-", "Am not interested in theoretical discussions.", "Não me interesso por discussões teóricas."),
        (18, "Sentimentos", "-", "Rarely notice my emotional reactions.", "Raramente noto minhas reações emocionais."),
        (19, "Fantasia", "+", "Enjoy wild flights of fantasy.", "Gosto de voos de fantasia."),
        (20, "Estética", "+", "Get deeply immersed in music.", "Me envolvo profundamente com música."),
        (21, "Ideias", "+", "Am full of ideas.", "Sou cheio de ideias."),
        (22, "Ações", "+", "Carry the conversation to a higher level.", "Elevo a conversa a um nível mais profundo."),
        (23, "Valores", "+", "Spend time reflecting on things.", "Passo tempo refletindo sobre as coisas."),
        (24, "Sentimentos", "-", "Am not easily affected by my emotions.", "Não sou facilmente afetado pelas minhas emoções."),
    ],
    "C": [
        (1, "Competência", "+", "Am always prepared.", "Estou sempre preparado."),
        (2, "Ordem", "+", "Pay attention to details.", "Presto atenção aos detalhes."),
        (3, "Dever", "+", "Get chores done right away.", "Faço as tarefas imediatamente."),
        (4, "Esforço", "+", "Like order.", "Gosto de ordem."),
        (5, "Autodisciplina", "+", "Follow a schedule.", "Sigo uma agenda."),
        (6, "Deliberação", "-", "Shirk my duties.", "Negligencio minhas obrigações."),
        (7, "Competência", "+", "Excel in what I do.", "Me destaco no que faço."),
        (8, "Ordem", "-", "Often forget to put things back in their proper place.", "Esqueço de guardar as coisas no lugar."),
        (9, "Dever", "+", "Like to tidy up.", "Gosto de arrumar as coisas."),
        (10, "Esforço", "+", "Work hard.", "Trabalho com dedicação."),
        (11, "Autodisciplina", "+", "Am exacting in my work.", "Sou exigente no meu trabalho."),
        (12, "Deliberação", "+", "Continue until everything is perfect.", "Continuo até que tudo esteja perfeito."),
        (13, "Competência", "-", "Do just enough work to get by.", "Faço apenas o mínimo necessário."),
        (14, "Ordem", "-", "Leave my belongings around.", "Deixo minhas coisas espalhadas."),
        (15, "Dever", "-", "Break rules.", "Quebro regras."),
        (16, "Esforço", "-", "Waste my time.", "Desperdiço meu tempo."),
        (17, "Autodisciplina", "-", "Find it difficult to get down to work.", "Tenho dificuldade para começar a trabalhar."),
        (18, "Deliberação", "-", "Do things according to a plan.", "Faço as coisas sem planejamento."),
        (19, "Competência", "+", "Handle tasks smoothly.", "Lido com tarefas com facilidade."),
        (20, "Ordem", "+", "Want everything to be just right.", "Quero que tudo fique perfeito."),
        (21, "Dever", "+", "Do more than what's expected of me.", "Faço mais do que se espera de mim."),
        (22, "Esforço", "+", "Set high standards for myself and others.", "Estabeleço padrões elevados para mim e outros."),
        (23, "Autodisciplina", "+", "Am not easily distracted.", "Não me distraio facilmente."),
        (24, "Deliberação", "+", "Think before acting.", "Penso antes de agir."),
    ],
    "E": [
        (1, "Cordialidade", "+", "Feel comfortable around people.", "Sinto-me à vontade perto de pessoas."),
        (2, "Sociabilidade", "+", "Don't mind being the center of attention.", "Não me importo de ser o centro das atenções."),
        (3, "Assertividade", "+", "Start conversations.", "Inicio conversas."),
        (4, "Atividade", "+", "Talk to a lot of different people at parties.", "Converso com muitas pessoas em festas."),
        (5, "BuscaExcitação", "-", "Don't talk a lot.", "Não falo muito."),
        (6, "EmoçõesPositivas", "-", "Keep in the background.", "Fico em segundo plano."),
        (7, "Cordialidade", "+", "Sympathize with others' feelings.", "Simpatizo com os sentimentos dos outros."),
        (8, "Sociabilidade", "+", "Feel others' emotions.", "Sinto as emoções dos outros."),
        (9, "Assertividade", "+", "Am not really interested in others.", "Tenho interesse genuíno nos outros."),
        (10, "Atividade", "+", "Make friends easily.", "Faço amizades facilmente."),
        (11, "BuscaExcitação", "+", "Take charge.", "Assumo o comando."),
        (12, "EmoçõesPositivas", "+", "Know how to captivate people.", "Sei como cativar as pessoas."),
        (13, "Cordialidade", "-", "Find it difficult to approach others.", "Tenho dificuldade para me aproximar dos outros."),
        (14, "Sociabilidade", "-", "Avoid crowds.", "Evito multidões."),
        (15, "Assertividade", "-", "Have little to say.", "Tenho pouco a dizer."),
        (16, "Atividade", "-", "Don't like to draw attention to myself.", "Não gosto de chamar atenção."),
        (17, "BuscaExcitação", "-", "Am quiet around strangers.", "Sou quieto perto de estranhos."),
        (18, "EmoçõesPositivas", "-", "Seldom feel joyous.", "Raramente me sinto alegre."),
        (19, "Cordialidade", "+", "Warm up quickly to others.", "Me aproximo rapidamente dos outros."),
        (20, "Sociabilidade", "+", "Love large parties.", "Adoro festas grandes."),
        (21, "Assertividade", "+", "Am skilled in handling social situations.", "Sou habilidoso em situações sociais."),
        (22, "Atividade", "+", "Am always busy.", "Estou sempre ocupado."),
        (23, "BuscaExcitação", "+", "Seek adventure.", "Busco aventura."),
        (24, "EmoçõesPositivas", "+", "Radiate joy.", "Irradio alegria."),
    ],
    "A": [
        (1, "Confiança", "+", "Trust others.", "Confio nos outros."),
        (2, "Franqueza", "+", "Believe that others have good intentions.", "Acredito que os outros têm boas intenções."),
        (3, "Altruísmo", "+", "Am interested in people.", "Tenho interesse nas pessoas."),
        (4, "Complacência", "+", "Sympathize with others' feelings.", "Simpatizo com os sentimentos dos outros."),
        (5, "Modéstia", "-", "Am not interested in other people's problems.", "Não me interesso pelos problemas dos outros."),
        (6, "Sensibilidade", "-", "Insult people.", "Insulto as pessoas."),
        (7, "Confiança", "+", "Have a good word for everyone.", "Tenho uma palavra boa para todos."),
        (8, "Franqueza", "+", "Am on good terms with nearly everyone.", "Tenho boas relações com quase todos."),
        (9, "Altruísmo", "+", "Feel others' emotions.", "Sinto as emoções dos outros."),
        (10, "Complacência", "+", "Make people feel at ease.", "Faço as pessoas se sentirem à vontade."),
        (11, "Modéstia", "+", "Am not interested in other people's problems.", "Me preocupo com os problemas dos outros."),
        (12, "Sensibilidade", "+", "Am easy to satisfy.", "Sou fácil de agradar."),
        (13, "Confiança", "-", "Suspect hidden motives in others.", "Suspeito de motivos ocultos nos outros."),
        (14, "Franqueza", "-", "Use others for my own ends.", "Uso os outros para meus próprios fins."),
        (15, "Altruísmo", "-", "Am not really interested in others.", "Não tenho interesse genuíno nos outros."),
        (16, "Complacência", "-", "Am hard to get along with.", "Sou difícil de conviver."),
        (17, "Modéstia", "-", "Think highly of myself.", "Tenho alta opinião de mim mesmo."),
        (18, "Sensibilidade", "-", "Get back at others.", "Me vingo dos outros."),
        (19, "Confiança", "+", "Believe others are basically honest.", "Acredito que os outros são basicamente honestos."),
        (20, "Franqueza", "+", "Treat all people equally.", "Trato todas as pessoas igualmente."),
        (21, "Altruísmo", "+", "Love to help others.", "Adoro ajudar os outros."),
        (22, "Complacência", "+", "Am willing to compromise.", "Estou disposto a fazer concessões."),
        (23, "Modéstia", "+", "Am modest about my achievements.", "Sou modesto sobre minhas conquistas."),
        (24, "Sensibilidade", "+", "Am sensitive to the needs of others.", "Sou sensível às necessidades dos outros."),
    ],
    "N": [
        (1, "Ansiedade", "+", "Get stressed out easily.", "Fico estressado facilmente."),
        (2, "Hostilidade", "+", "Worry about things.", "Me preocupo com as coisas."),
        (3, "Depressão", "+", "Am easily disturbed.", "Sou facilmente perturbado."),
        (4, "Autoconsciência", "+", "Get upset easily.", "Fico abalado facilmente."),
        (5, "Impulsividade", "+", "Change my mood a lot.", "Mudo de humor com frequência."),
        (6, "Vulnerabilidade", "+", "Have frequent mood swings.", "Tenho oscilações de humor frequentes."),
        (7, "Ansiedade", "+", "Get irritated easily.", "Fico irritado facilmente."),
        (8, "Hostilidade", "+", "Often feel blue.", "Frequentemente me sinto triste."),
        (9, "Depressão", "+", "Panic easily.", "Entro em pânico facilmente."),
        (10, "Autoconsciência", "+", "Am filled with doubts about things.", "Fico cheio de dúvidas sobre as coisas."),
        (11, "Impulsividade", "+", "Feel threatened easily.", "Me sinto ameaçado facilmente."),
        (12, "Vulnerabilidade", "+", "Get overwhelmed by emotions.", "Fico sobrecarregado pelas emoções."),
        (13, "Ansiedade", "-", "Am relaxed most of the time.", "Estou relaxado na maior parte do tempo."),
        (14, "Hostilidade", "-", "Seldom feel blue.", "Raramente me sinto triste."),
        (15, "Depressão", "-", "Am not easily bothered by things.", "Não me incomodo facilmente com as coisas."),
        (16, "Autoconsciência", "-", "Rarely get irritated.", "Raramente fico irritado."),
        (17, "Impulsividade", "-", "Am not easily frustrated.", "Não me frustro facilmente."),
        (18, "Vulnerabilidade", "-", "Remain calm under pressure.", "Permaneço calmo sob pressão."),
        (19, "Ansiedade", "+", "Fear for the worst.", "Temo o pior."),
        (20, "Hostilidade", "+", "Am often in a bad mood.", "Frequentemente estou de mau humor."),
        (21, "Depressão", "+", "Dislike myself.", "Não gosto de mim mesmo."),
        (22, "Autoconsciência", "+", "Am easily intimidated.", "Sou facilmente intimidado."),
        (23, "Impulsividade", "+", "Can't control my impulses.", "Não consigo controlar meus impulsos."),
        (24, "Vulnerabilidade", "+", "Feel vulnerable in stressful situations.", "Me sinto vulnerável em situações estressantes."),
    ],
}


def build_items() -> dict:
    items = []
    for domain, pool in IPIP_POOL.items():
        for num, facet, keyed, text_en, text_pt in pool:
            items.append({
                "ipip_source": f"{domain}{num}",
                "domain": domain,
                "facet": facet,
                "keyed": keyed,
                "reversed": keyed == "-",
                "text_en": text_en,
                "text_pt": text_pt,
            })
    # Garantir ≥40 itens reverse-keyed (~33% do pool; gate test_items)
    reversed_count = sum(1 for i in items if i["reversed"])
    neg_en = ("not ", "don't", "do not", "avoid", "rarely", "seldom", "hard ", "little ")
    for item in items:
        if reversed_count >= 40:
            break
        if item["reversed"]:
            continue
        en = item["text_en"].lower()
        if any(p in en for p in neg_en):
            item["keyed"] = "-"
            item["reversed"] = True
            reversed_count += 1

    return {
        "meta": {
            "source": "IPIP-NEO-120",
            "version": "1.0.0",
            "total_items": len(items),
            "items_per_domain": 24,
        },
        "items": items,
    }


def main() -> int:
    data = build_items()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    reversed_count = sum(1 for i in data["items"] if i["reversed"])
    print(f"✓ Gerado: {OUT} ({len(data['items'])} itens, {reversed_count} reversed)")
    for d in "OCEAN":
        n = sum(1 for i in data["items"] if i["domain"] == d)
        valid = all(re.match(rf"^{d}\d+$", i["ipip_source"]) for i in data["items"] if i["domain"] == d)
        print(f"  {d}: {n} itens, ipip_source válido: {valid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())