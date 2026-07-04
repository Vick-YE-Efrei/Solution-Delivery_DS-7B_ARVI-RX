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

_ROOT = Path(__file__).resolve().parents[1]

_processor_cache: dict[str, Any] = {}
_model_cache: dict[str, Any] = {}


def toy_predict(image_path: str | Path, mode: str = "baseline") -> dict[str, Any]:
    """Deterministic toy predictor — validates the pipeline without loading a real model."""
    start = time.perf_counter()
    name    = Path(image_path).name.lower()
    quality = basic_quality_flag(image_path)

    if "suspected_opacity" in name:
        pred          = "suspected_opacity"
        conf          = 0.78 if mode == "baseline" else 0.72
        evidence      = ["synthetic opacity-like area visible in the lung field"]
        justification = "The synthetic image contains a localized brighter region compatible with the toy opacity class."
    elif "normal" in name:
        pred          = "normal"
        conf          = 0.72 if mode == "baseline" else 0.68
        evidence      = ["no synthetic opacity marker detected"]
        justification = "The synthetic image does not contain the opacity marker used by the toy generator."
    else:
        pred          = "uncertain"
        conf          = 0.52
        evidence      = ["limited synthetic image quality"]
        justification = "The image is treated as limited quality in the toy catalog."

    return {
        "image_quality":   quality,
        "predicted_class": pred,
        "confidence":      round(float(conf), 3),
        "visual_evidence": evidence,
        "justification":   justification,
        "limitations":     ["synthetic toy image", "no clinical context", "not a validated medical model"],
        "warning":         WARNING,
        "model_name":      f"toy-rule-{mode}",
        "prompt_version":  f"{mode}_v1",
        "latency_ms":      int((time.perf_counter() - start) * 1000),
    }


def _load_model(model_id: str, lora_path: str) -> tuple[Any, Any]:
    """Load and cache processor + model for a given model_id/lora_path pair."""
    cache_key = f"{model_id}:{lora_path}"
    if cache_key not in _model_cache:
        processor = AutoProcessor.from_pretrained(model_id)

        has_gpu = torch.cuda.is_available()
        if has_gpu:
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            # Laisse 0.5 Go pour le système, déborde le reste sur RAM CPU
            gpu_alloc = f"{max(1, int(vram_gb - 0.5))}GiB"
            print(f"[INFO] GPU détecté ({vram_gb:.1f} Go VRAM) — allocation GPU: {gpu_alloc}, débordement CPU")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            base = AutoModelForImageTextToText.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                dtype=torch.bfloat16,
                device_map="cuda:0",
                low_cpu_mem_usage=True,
            )
        else:
            print("[INFO] Pas de GPU détecté — chargement du modèle en CPU (lent)")
            base = AutoModelForImageTextToText.from_pretrained(
                model_id,
                dtype=torch.float32,
                device_map="cpu",
                low_cpu_mem_usage=True,
            )

        model = PeftModel.from_pretrained(base, lora_path)
        model.eval()
        _processor_cache[cache_key] = processor
        _model_cache[cache_key]     = model

    return _processor_cache[cache_key], _model_cache[cache_key]


def vlm_predict_medgemma(
    image_path: str | Path,
    model_key: str = "medgemma_4b_pt",
    lora_path: str | None = None,
) -> dict[str, Any]:
    if lora_path is None:
        lora_path = str(_ROOT / "finetuning" / "lora_adapters" / "medgemma_4b_pt" / "medgemma_4b_pt")
    MODEL_IDS = {
        "gemma_4_E4B":    "google/gemma-4-E4B",
        "medgemma_4b_pt": "google/medgemma-4b-pt",
    }
    model_id = MODEL_IDS.get(model_key, "google/medgemma-4b-pt")

    processor, model = _load_model(model_id, lora_path)
    start = time.perf_counter()

    image  = Image.open(image_path).convert("RGB")
    prompt = (
        "Analyze this chest X-ray. Classify as exactly one of: normal, suspected_opacity, uncertain. "
        "Respond with the class, a confidence between 0 and 1, and a short justification."
    )

    inputs = processor(
        images=image,
        text=processor.tokenizer.boi_token + " " + prompt,
        return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=300, do_sample=False)

    text       = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    text_lower = text.lower()

    if "suspected_opacity" in text_lower or "opacity" in text_lower or "pneumonia" in text_lower:
        pred = "suspected_opacity"
        conf = 0.74
    elif "normal" in text_lower:
        pred = "normal"
        conf = 0.78
    else:
        pred = "uncertain"
        conf = 0.50

    return {
        "image_quality":   basic_quality_flag(image_path),
        "predicted_class": pred,
        "confidence":      round(conf, 3),
        "visual_evidence": [],
        "justification":   text.strip()[:400],
        "limitations":     [
            "VLM output is free text parsed heuristically",
            "not clinically validated",
            "prototype éducatif uniquement",
        ],
        "warning":         WARNING,
        "model_name":      model_key,
        "prompt_version":  "vlm_v1",
        "latency_ms":      int((time.perf_counter() - start) * 1000),
    }
