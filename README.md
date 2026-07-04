# Assistant radiologue virtuel responsable

> **Auteur :** Badr Tajini  
> **Solution Delivery - Filière Data**  
> **École :** EFREI  
> **Année académique :** 2025-2026

## Contexte

Prototype pédagogique d'IA médicale multimodale pour apprendre à construire une chaîne **prudente, traçable et évaluée** autour d'une radiographie thoracique frontale.

---

> **Position non clinique.** Ce dépôt n'est pas un dispositif médical. Il ne doit jamais être utilisé pour diagnostiquer, trier ou orienter un patient. Toute sortie doit rester un résultat expérimental, vérifié par un professionnel qualifié.

---

## Contrat du projet

| Élément | Cadrage |
|---|---|
| Entrée | Une radiographie thoracique frontale |
| Sorties | `normal`, `suspected_opacity`, `uncertain` |
| Preuve minimale | JSON valide, warning, logs, métriques, cas d'erreur |
| Données | Synthétiques ou publiques, autorisées et dé-identifiées |
| Finalité | Prototype éducatif de data/IA, pas aide au diagnostic réelle |

Le bon rendu ne cherche pas à impressionner par un modèle spectaculaire. Il démontre une méthode : périmètre limité, baseline reproductible, garde-fous, évaluation, analyse d'erreurs et limites explicites.

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

Avant une soutenance, un push ou une livraison, lancer le contrôle court :

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

La réponse doit contenir une classe, une confiance, des observations visuelles, une justification, des limites et l'avertissement non clinique.

## Structure du dépôt

Le dépôt est organisé pour séparer clairement les responsabilités du pipeline :

- [src](src) : cœur du système. Contient le prétraitement, l’inférence, les garde-fous, les métriques et la persistance SQLite.
- [api](api) : point d’entrée HTTP minimal avec FastAPI pour faire tourner le pipeline sur une image uploadée.
- [app](app) : interface de démonstration Streamlit pour tester l’application sans ligne de commande.
- [prompts](prompts) : prompts versionnés pour la baseline et la version améliorée.
- [eval](eval) : scripts d’évaluation, sorties CSV/JSON, rapports et artefacts de comparaison.
- [tests](tests) : tests de smoke et de bout en bout pour verrouiller le comportement attendu.
- [data](data) : images et cas synthétiques utilisés pour les validations et les démonstrations.
- [docs](docs) : documents de cadrage, architecture, éthique et protocole d’évaluation.
- [finetuning](finetuning) : stubs et pistes expérimentales, sans impact sur la chaîne de base.

### Fichiers racine utiles

- [README.md](README.md) : guide d’utilisation et cadrage du projet.
- [requirements.txt](requirements.txt) : dépendances principales du pipeline.
- [requirements-test.txt](requirements-test.txt) : dépendances de test.
- [pyproject.toml](pyproject.toml) : configuration Python minimale du projet.

## Références techniques

| Ressource | Usage possible | Référence à citer |
|---|---|---|
| Unsloth - Gemma 4 | Fine-tuning LoRA/QLoRA expérimental, uniquement après une baseline simple | [Guide Gemma 4](https://unsloth.ai/docs/models/gemma-4/train), [catalogue des modèles](https://unsloth.ai/docs/get-started/unsloth-model-catalog), [blog Unsloth](https://unsloth.ai/blog) |
| MedGemma | Baseline ou adaptation médicale image-texte, avec prudence sur les conditions d'accès | [Model card Hugging Face](https://huggingface.co/google/medgemma-4b-pt) |

## Points de vigilance

- Ne pas inventer d'information clinique absente de l'image.
- Ne pas supprimer la classe `uncertain`; elle est un garde-fou, pas un échec.
- Ne pas afficher uniquement des réussites en soutenance.
- Ne jamais commiter de données patient réelles, identifiantes ou ambiguës.
- Ne pas présenter le prototype comme validé médicalement.

## Licence et sources externes

Le code pédagogique du dépôt est publié sous licence MIT. **Les datasets externes, modèles et bibliothèques utilisés conservent leurs licences propres** : les étudiants doivent vérifier et documenter les droits d'usage avant toute expérimentation.

Exigence minimale : indiquer dans le rapport la source, la version, la licence ou les conditions d'accès, les restrictions de redistribution, les traitements d'anonymisation et les limites d'interprétation. Aucun fichier patient réel, même pseudonymisé, ne doit être ajouté au dépôt sans autorisation explicite et traçable.
