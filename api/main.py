from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
import traceback
from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.inference import toy_predict, vlm_predict_medgemma
from src.guardrails import apply_safety_guardrails

app = FastAPI(title="Assistant radiologue virtuel EFREI", version="0.2.0")

# Le frontend Vue tourne sur un port différent (5173) de cette API (8001) : sans
# CORS ouvert, le navigateur bloquerait les requêtes cross-origin. On reste large
# ("*") ici parce que c'est un prototype pédagogique, pas un déploiement public.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = ROOT / "tmp_uploads"
# Chemins par défaut vers les adaptateurs LoRA livrés avec le repo (voir finetuning/lora_adapters/).
LORA_PATH_GEMMA    = str(ROOT / "finetuning" / "lora_adapters" / "gemma_4_E4B"    / "gemma_4_E4B"    / "gemma4_chestxray_lora_adapters")
LORA_PATH_MEDGEMMA = str(ROOT / "finetuning" / "lora_adapters" / "medgemma_4b_pt" / "medgemma_4b_pt")


@app.get("/")
def health():
    """Ping basique pour vérifier que l'API est en ligne (utilisé par le frontend au démarrage)."""
    return {"status": "ok", "scope": "educational prototype, not diagnosis"}


@app.get("/model-info")
def model_info():
    """Décrit les modèles disponibles pour le frontend (sélecteur de modèle, page à propos)."""
    return {
        "models": [
            {
                "key": "gemma_4_E4B",
                "name": "Gemma 4E4B (LoRA fine-tuné)",
                "base": "google/gemma-4-E4B",
                "type": "VLM multimodal",
                "adapter": "LoRA QLoRA NF4",
                "lora_path": LORA_PATH_GEMMA,
                "description": "Gemma 4E4B fine-tuné sur chest X-ray RSNA/ChestXray14",
            },
            {
                "key": "medgemma_4b_pt",
                "name": "MedGemma 4B PT (LoRA fine-tuné)",
                "base": "google/medgemma-4b-pt",
                "type": "VLM médical multimodal",
                "adapter": "LoRA QLoRA NF4",
                "lora_path": LORA_PATH_MEDGEMMA,
                "description": "MedGemma 4B pré-entraîné médical, fine-tuné radiologie thoracique",
            },
        ],
        "warning": "Prototype pédagogique. Non destiné au diagnostic.",
    }


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    mode: str = Query(default="toy", description="toy | baseline | improved"),
    model_key: str = Query(default="medgemma_4b_pt", description="gemma_4_E4B | medgemma_4b_pt"),
):
    """Reçoit une image, la sauvegarde, et renvoie une prédiction avec ses garde-fous.

    mode="toy"/"baseline" utilise le prédicteur jouet déterministe (rapide, pas de
    modèle à charger). Tout autre mode ("improved") tente l'inférence VLM réelle
    (MedGemma/Gemma + LoRA) ; si le modèle n'est pas disponible localement (pas de
    GPU, poids manquants...), on retombe automatiquement sur le prédicteur jouet
    plutôt que de faire planter la requête.
    """
    UPLOAD_DIR.mkdir(exist_ok=True)
    filename  = Path(file.filename or "image.png").name
    suffix    = Path(filename).suffix or ".png"
    stem      = Path(filename).stem or "image"
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)  # neutralise les caractères non sûrs pour un nom de fichier
    target    = UPLOAD_DIR / f"uploaded_{safe_stem}{suffix}"

    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        if mode == "toy" or mode == "baseline":
            pred = toy_predict(target, mode=mode if mode in ("baseline", "improved") else "baseline")
        else:
            try:
                lora_path = LORA_PATH_GEMMA if model_key == "gemma_4_E4B" else LORA_PATH_MEDGEMMA
                pred = vlm_predict_medgemma(target, model_key=model_key, lora_path=lora_path)
            except Exception as exc:
                # Le VLM peut échouer pour plein de raisons (pas de GPU, poids absents,
                # token HuggingFace manquant...) : on ne bloque pas l'utilisateur pour autant.
                print(f"[WARN] VLM indisponible ({exc}), fallback toy")
                pred = toy_predict(target, mode="improved")
                pred["model_name"] = f"toy-fallback ({model_key} indisponible)"

        return apply_safety_guardrails(pred)

    except Exception as exc:
        # Filet de sécurité générique : on log la stack trace côté serveur mais on
        # renvoie une erreur HTTP propre plutôt qu'un 500 opaque au client.
        tb = traceback.format_exc()
        print(f"[ERROR /predict] {exc}\n{tb}")
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")
