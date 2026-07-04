from __future__ import annotations

"""FastAPI entry point for the demo pipeline.

The API accepts an uploaded chest X-ray image, runs the full pipeline and
returns a structured prediction payload that can be consumed by a frontend or a
test client.
"""

import re
import shutil
import sys
from pathlib import Path
from fastapi import FastAPI, File, UploadFile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.pipeline import run_pipeline

app = FastAPI(title="Assistant radiologue virtuel EFREI", version="0.1.0")
UPLOAD_DIR = Path("tmp_uploads")


@app.get("/")
def health() -> dict:
    return {"status": "ok", "scope": "educational prototype, not diagnosis"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> dict:
    UPLOAD_DIR.mkdir(exist_ok=True)
    filename = Path(file.filename or "image.png").name
    suffix = Path(filename).suffix or ".png"
    stem = Path(filename).stem or "image"
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)
    target = UPLOAD_DIR / f"uploaded_{safe_stem}{suffix}"
    # Persist the uploaded image on disk so the pipeline can process it
    # exactly as it would with a local file from the dataset.
    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    result = run_pipeline(
        image_path=target,
        mode="improved",
        prompt_mode="improved",
        output_dir=ROOT / "artifacts" / "runs",
        db_path=ROOT / "medical_ai_evidence.sqlite",
    )
    return result
