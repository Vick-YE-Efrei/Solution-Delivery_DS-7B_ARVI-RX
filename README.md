# Assistant radiologue virtuel responsable

> **Auteur :** RaVI Corp.  
> **Solution Delivery - Filière Data**  
> **École :** EFREI  
> **Année académique :** 2025-2026

## Contexte

Prototype pédagogique d'IA médicale multimodalep à l'analyse de radiographies thoraciques frontales. Il reçoit une image, l'analyse via un modèle vision-langage et retourne une sortie JSON structurée, prudente et traçable limitée à trois classes : normal, suspected_opacity, uncertain. La classe uncertain est une décision de sécurité (image de qualité insuffisante, signes faibles, sortie invalide ou confiance trop basse), jamais un échec.

---

> **Position non clinique.** Ce dépôt n'est pas un dispositif médical. Il ne doit jamais être utilisé pour diagnostiquer, trier ou orienter un patient. Toute sortie doit rester un résultat expérimental, vérifié par un professionnel qualifié.

---

## Démarrage rapide

```bash
# Use Python 3.11 (recommended)
# Unix/macOS:
python3.11 -m venv .venv
# Windows (PowerShell):
py -3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python eval/run_evaluation.py --mode toy
PYTHONPATH=. streamlit run app/streamlit_app.py # chercher les modules depuis le dossier courant (la racine du projet)
```

## Smoke test du dépôt

```bash
pip install -r requirements-test.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
python -m compileall -q src api app eval finetuning tests
python eval/run_evaluation.py --mode toy \
  --out-dir /tmp/assistant-radio-eval \
  --db-path /tmp/assistant-radio-evidence.sqlite
```

Ce smoke test vérifie la structure du dépôt, le contrat du dataset synthétique, le schéma de sortie, les garde-fous, l'API de démonstration, la compilation Python et l'évaluation jouet.

## API de démonstration

```bash
uvicorn api.main:app --reload
```

Exemple :

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -F "file=@data/sample_images/CXR_SYN_002_suspected_opacity.png"
```

## Structure du dépôt

- [src](src) : cœur du système. Contient le prétraitement, l’inférence, les garde-fous, les métriques et la persistance SQLite.
- [api](api) : point d’entrée HTTP minimal avec FastAPI pour faire tourner le pipeline sur une image uploadée.
- [app](app) : interface de démonstration Streamlit pour tester l’application sans ligne de commande.
- [prompts](prompts) : prompts versionnés pour la baseline et la version améliorée.
- [eval](eval) : scripts d’évaluation, sorties CSV/JSON, rapports et artefacts de comparaison.
- [tests](tests) : tests de smoke et de bout en bout pour verrouiller le comportement attendu.
- [data](data) : images et cas utilisés pour les validations et les démonstrations.
- [docs](docs) : documents de cadrage, architecture, éthique et protocole d’évaluation.
- [finetuning](finetuning) : pistes expérimentales, sans impact sur la chaîne de base.
- [requirements.txt](requirements.txt) : dépendances principales du pipeline.
- [requirements-test.txt](requirements-test.txt) : dépendances de test.
- [pyproject.toml](pyproject.toml) : configuration Python minimale du projet.

## Références techniques

| Ressource | Usage possible | Référence à citer |
|---|---|---|
| Unsloth - Gemma 4 | Fine-tuning LoRA/QLoRA expérimental, uniquement après une baseline simple | [Guide Gemma 4](https://unsloth.ai/docs/models/gemma-4/train), [catalogue des modèles](https://unsloth.ai/docs/get-started/unsloth-model-catalog), [blog Unsloth](https://unsloth.ai/blog) |
| MedGemma | Baseline ou adaptation médicale image-texte, avec prudence sur les conditions d'accès | [Model card Hugging Face](https://huggingface.co/google/medgemma-4b-pt) |

## Références

### Dépôt de référence
- Assistant radiologue virtuel (base du projet) — https://github.com/BTajini/assistant-radiologue-virtuel  

---

### Modèle utilisés comme backbones vision-langage multimodaux 

- MedGemma 4B (modèle vision-langage pré-entraîné) — https://huggingface.co/google/medgemma-4b-pt  
- Gemma 4 E2B (modèle fondation multimodal) — https://huggingface.co/google/gemma-4-E2B  

---

### Jeux de données publics utilisés

- RSNA Pneumonia Processed Dataset — https://www.kaggle.com/datasets/iamtapendu/rsna-pneumonia-processed-dataset  
- Chest X-Ray Pneumonia Dataset — https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia  