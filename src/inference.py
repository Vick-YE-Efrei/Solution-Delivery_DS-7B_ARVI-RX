from __future__ import annotations

from pathlib import Path
import time
from typing import Any
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig
from peft import PeftModel

from .preprocessing import basic_quality_flag

WARNING = "Prototype pédagogique. Non destiné au diagnostic. Validation par un professionnel qualifié requise."
MODEL_ID = "google/medgemma-4b-pt"
USE_QLORA = False
LORA_PATH = "./medgemma-qlora-adapter"

processor = None
model = None

def toy_predict(image_path: str | Path, mode: str = "baseline") -> dict[str, Any]:
    """Deterministic toy predictor used to validate the repo pipeline.

    It reads synthetic labels from filenames. This is not medical inference.
    """
    start = time.perf_counter()
    name = Path(image_path).name.lower()
    quality = basic_quality_flag(image_path)

    if "suspected_opacity" in name:
        pred = "suspected_opacity"
        conf = 0.78 if mode == "baseline" else 0.72
        evidence = ["synthetic opacity-like area visible in the lung field"]
        justification = "The synthetic image contains a localized brighter region compatible with the toy opacity class. This is a pipeline validation result, not a medical interpretation."
    elif "normal" in name:
        pred = "normal"
        conf = 0.72 if mode == "baseline" else 0.68
        evidence = ["no synthetic opacity marker detected"]
        justification = "The synthetic image does not contain the opacity marker used by the toy generator. This conclusion is limited to the synthetic validation setting."
    else:
        pred = "uncertain"
        conf = 0.52
        evidence = ["limited synthetic image quality"]
        justification = "The image is treated as limited quality in the toy catalog. The safe output is uncertainty rather than a forced class."

    latency_ms = int((time.perf_counter() - start) * 1000)
    return {
        "image_quality": quality,
        "predicted_class": pred,
        "confidence": round(float(conf), 3),
        "visual_evidence": evidence,
        "justification": justification,
        "limitations": ["synthetic toy image", "no clinical context", "not a validated medical model"],
        "warning": WARNING,
        "model_name": f"toy-rule-{mode}",
        "prompt_version": f"{mode}_v1",
        "latency_ms": latency_ms,
    }

def load_medgemma():
    global processor, model

    if processor is None:
        processor = AutoProcessor.from_pretrained(MODEL_ID)

    if model is None:
        if USE_QLORA:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )

            base_model = AutoModelForImageTextToText.from_pretrained(
                MODEL_ID,
                quantization_config=bnb_config,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                low_cpu_mem_usage=True,
            )

            model = PeftModel.from_pretrained(base_model, LORA_PATH)
        else:
            model = AutoModelForImageTextToText.from_pretrained(
                MODEL_ID,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                low_cpu_mem_usage=True,
            )

        model.eval()

def vlm_predict_medgemma(image_path: str | Path, prompt: str) -> dict[str, Any]:
    load_medgemma()

    start = time.perf_counter()
    image = Image.open(image_path).convert("RGB")

    # 4b-pt : pas de chat template — on construit l'input directement
    inputs = processor(
        images=image,
        text=processor.tokenizer.boi_token + " " + prompt,
        return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=False,
        )

    text = processor.batch_decode(outputs, skip_special_tokens=True)[0].lower()

    # Parsing de la sortie texte libre
    if "suspected_opacity" in text or "opacity" in text or "pneumonia" in text:
        pred = "suspected_opacity"
    elif "normal" in text:
        pred = "normal"
    else:
        pred = "uncertain"

    latency_ms = int((time.perf_counter() - start) * 1000)

    return {
        "image_quality": basic_quality_flag(image_path),
        "predicted_class": pred,
        "confidence": 0.6 if pred != "uncertain" else 0.5,
        "visual_evidence": [],
        "justification": text[:300],
        "limitations": [
            "4b-pt is a pretrained base model — not instruction-tuned",
            "output is free text, not structured JSON",
            "not clinically validated",
        ],
        "warning": WARNING,
        "model_name": "medgemma-4b-pt",
        "latency_ms": latency_ms,
    }