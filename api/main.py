from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.inference import toy_predict, vlm_predict_medgemma
from src.guardrails import apply_safety_guardrails

app = FastAPI(title="Assistant radiologue virtuel EFREI", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = ROOT / "tmp_uploads"
LORA_PATH_GEMMA    = str(ROOT / "finetuning" / "lora_adapters" / "gemma_4_E4B"    / "gemma_4_E4B"    / "gemma4_chestxray_lora_adapters")
LORA_PATH_MEDGEMMA = str(ROOT / "finetuning" / "lora_adapters" / "medgemma_4b_pt" / "medgemma_4b_pt")


@app.get("/")
def health() -> dict:
    return {"status": "ok", "scope": "educational prototype, not diagnosis"}


@app.get("/model-info")
def model_info() -> dict:
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
) -> dict:
    UPLOAD_DIR.mkdir(exist_ok=True)
    filename  = Path(file.filename or "image.png").name
    suffix    = Path(filename).suffix or ".png"
    stem      = Path(filename).stem or "image"
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)
    target    = UPLOAD_DIR / f"uploaded_{safe_stem}{suffix}"

    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    if mode == "toy" or mode == "baseline":
        pred = toy_predict(target, mode=mode if mode in ("baseline", "improved") else "baseline")
    else:
        # mode == "improved" → essaie le vrai modèle, fallback toy si GPU/modèle indisponible
        try:
            lora_path = LORA_PATH_GEMMA if model_key == "gemma_4_E4B" else LORA_PATH_MEDGEMMA
            pred = vlm_predict_medgemma(target, model_key=model_key, lora_path=lora_path)
        except Exception as exc:
            print(f"[WARN] VLM indisponible ({exc}), fallback toy")
            pred = toy_predict(target, mode="improved")
            pred["model_name"] = f"toy-fallback ({model_key} indisponible)"

    return apply_safety_guardrails(pred)
