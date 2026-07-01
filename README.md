# TESTEPERSONALIDADE — Perfil Big Five (OCEAN)

Instrumento de autoconhecimento em português brasileiro baseado no modelo **Big Five (OCEAN)**, com perfis **Natural** e **Adaptado**, scoring T-score e relatório de 12 seções.

**Versão:** 1.0.0 | **Marca:** TeclaPonto | **Projeto irmão:** [TESTEDISC](../TESTEDISC)

## Quick Start

```bash
pip install -r requirements.txt
python scripts/translate_items.py    # gera artifacts/items.json (120 IPIP)
python build_all.py                  # pipeline completo (8 etapas)
```

Abra `index.html` no navegador ou publique via Vercel (recomendado para frontend + backend) ou GitHub Pages (`docs/`).

## Pipeline (8 etapas)

| # | Script | Saída |
|---|--------|-------|
| 1 | `extract_knowledge.py` | `knowledge.json`, `mapped_knowledge.json` |
| 2 | `build_devolutiva_templates.py` | `devolutiva_templates.json`, JS templates |
| 3 | `generate_questions.py` | 60 itens → `questions.js` |
| 4 | `build_norms.py` | `norms.json` |
| 5 | `generate_rules.py` | `rules.yaml`, `ontology.yaml` |
| 6 | `build_complete.py` | `index.html`, `sw.js`, `docs/` |
| 7 | `verify_structure.py` | ~45 checks |
| 8 | `run_tests.py` | pytest |

```bash
python build_all.py --step generate_questions  # etapa única
ALLOW_INCOMPLETE=1 python build_all.py         # dev parcial
```

## Estrutura

- `src/js/` — Frontend PWA (Likert 1–5, radar OCEAN, devolutiva 12 seções)
- `api/` — FastAPI (`/infer` com `t_scores`, `/responses` batch 60 itens)
- `artifacts/` — Itens IPIP, normas, regras, templates
- `MODELOS/` — PDFs de referência (corpus devolutiva)

## API

```bash
uvicorn api.main:app --reload
```

- `POST /infer` — `{ t_scores: { natural: {O,C,E,A,N}, adapted: {...} } }`
- `POST /responses` — batch 60 itens item-level
- `GET /result/{hash}` — resultado compartilhado (display_scores com SE)

## Testes

```bash
pytest tests/ -q
python verify_structure.py
```

## Deployment

### Vercel (recomendado)
1. Conecte o repositório GitHub no seu projeto Vercel (use o ID `prj_um9kVqtggku2ozLM6J3lVsrgsJS9` se for o do backend).
2. Build Command: `python build_complete.py`
3. Output Directory: `.`
4. Defina variável de ambiente `API_BASE` para a URL do seu backend no Vercel (ex: `https://seu-api.vercel.app`).
5. O frontend estática será servido, chamadas de API vão para o backend.

### GitHub Pages
Use `docs/` (configurado no workflow).

## Disclaimer

Instrumento de autoconhecimento. Não constitui diagnóstico psicológico ou avaliação clínica.