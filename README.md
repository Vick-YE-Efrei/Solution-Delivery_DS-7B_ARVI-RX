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

## Installation et environnement

```bash
# Use Python 3.11
# Unix/macOS:
python3.11 -m venv .venv
# Windows (PowerShell):
py -3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-test.txt
```

## Tests

```bash
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"
python -m pytest -q
```

## Interface Streamlit (UI interactive)
```bash
$env:PYTHONPATH="."
streamlit run app/streamlit_app.py
```

## API FastAPI
```bash
# Lancer le serveur
uvicorn api.main:app --reload

# Dans un autre terminal, faire une requête
curl -X POST "http://localhost:8000/predict" \
  -F "file=@/chemin/vers/votre/image.png"
```

## Test Pipeline
```bash
python -m pytest tests/test_repository_smoke.py -v 2>&1 | Select-Object -Last 30
```

## Téléchargement du modèle VLM (requis une seule fois)

```bash
# Télécharger et mettre en cache medgemma-4b-pt localement (~4 GB)
python -c "from transformers import AutoProcessor, AutoModelForImageTextToText; \
  AutoProcessor.from_pretrained('google/medgemma-4b-pt'); \
  AutoModelForImageTextToText.from_pretrained('google/medgemma-4b-pt'); \
  print('✓ Model cached')"
```

## Comparaison baseline / améliorée

### Mode toy (rapide, déterministe, pas de VLM)
```bash
# ~2 secondes
python eval/run_evaluation.py --mode toy --out-dir results_json
# Sortie: eval/results_json/toy_metrics.json
```

### Modes baseline/improved (VLM medgemma-4b-pt - TRÈS LENT sur CPU)
```bash
# ⚠ Chaque image prend ~12 minutes sur CPU. --allow-remote-model-load charge depuis cache local.
python eval/run_evaluation.py --mode baseline --dataset data/chest_xray/chest_xray_train.csv --out-dir results_json --allow-remote-model-load
# Sortie: eval/results_json/baseline_predictions.csv, eval/results_json/baseline_metrics.json

python eval/run_evaluation.py --mode improved --dataset data/chest_xray/chest_xray_train.csv --out-dir results_json --allow-remote-model-load
# Sortie: eval/results_json/improved_predictions.csv, eval/results_json/improved_metrics.json
```

## Structure du dépôt

- [src](src) : cœur du système. Contient le prétraitement, l’inférence, les garde-fous, les métriques et la persistance SQLite.
- [api](api) : point d’entrée HTTP minimal avec FastAPI pour faire tourner le pipeline sur une image uploadée.
- [app](app) : interface de démonstration Streamlit pour tester l’application sans ligne de commande.
- [prompts](prompts) : prompts versionnés pour la baseline et la version améliorée.
- [eval](eval) : scripts d'évaluation batch (toy/baseline/improved), sorties CSV/JSON.
  - `run_evaluation.py` : orchestration des modes toy/baseline/improved, agrégation des métriques.
  - `comparison_outputs/` : résultats de référence (baseline_gemma4, medgemma, comparaisons).
- [tests](tests) : tests de smoke et de bout en bout pour verrouiller le comportement attendu.
- [data](data) : images et cas utilisés pour les validations et les démonstrations.
- [docs](docs) : documents de cadrage, architecture, éthique et protocole d’évaluation.
- [finetuning](finetuning) : pistes expérimentales, sans impact sur la chaîne de base.
- [requirements.txt](requirements.txt) : dépendances principales du pipeline.
- [requirements-test.txt](requirements-test.txt) : dépendances de test.
- [pyproject.toml](pyproject.toml) : configuration Python minimale du projet.

## Références

### Dépôt de référence
- Assistant radiologue virtuel (base du projet) — https://github.com/BTajini/assistant-radiologue-virtuel  

---

### Modèle utilisés comme backbones vision-langage multimodaux 

- MedGemma 4B (modèle vision-langage pré-entraîné) — https://huggingface.co/google/medgemma-4b-pt  

---

### Jeux de données publics utilisés

- RSNA Pneumonia Processed Dataset — https://www.kaggle.com/datasets/iamtapendu/rsna-pneumonia-processed-dataset  
- Chest X-Ray Pneumonia Dataset — https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia  