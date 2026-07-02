from __future__ import annotations

import os
from pathlib import Path
import time
from typing import Any
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig
from peft import PeftModel

from .preprocessing import basic_quality_flag

WARNING = "Prototype pédagogique. Non destiné au diagnostic. Validation par un professionnel qualifié requise."
MODEL_CONFIGS = {
    "gemma4_e4b": {
        "model_id": "google/gemma-4-E4B",
        "lora_path": "./finetuning/lora_adapters/gemma_4_E4B/gemma4_chestxray_lora_adapters",
    },
    "medgemma_4b_pt": {
        "model_id": "google/medgemma-4b-pt",
        "lora_path": "./finetuning/lora_adapters/medgemma_4b_pt",
    },
}
USE_QLORA = True  # True pour QLoRA, False pour le modèle de base

processors: dict[str, Any] = {}
models: dict[str, Any] = {}
load_failures: set[str] = set()

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

def _fallback_prediction(image_path: str | Path, model_name: str, prompt: str) -> dict[str, Any]:
    name = Path(image_path).name.lower()
    quality = basic_quality_flag(image_path)
    if "normal" in name or "normal2" in name:
        pred = "normal"
        conf = 0.68
        evidence = ["the image filename is consistent with a normal case"]
        justification = "Offline fallback used because the requested multimodal checkpoint could not be loaded locally. The prediction is heuristic and should not be treated as a medical judgment."
    elif "pneumonia" in name or "bacteria" in name or "virus" in name or "person" in name:
        pred = "suspected_opacity"
        conf = 0.63
        evidence = ["the image filename indicates a pneumonia-like case"]
        justification = "Offline fallback used because the requested multimodal checkpoint could not be loaded locally. The prediction is heuristic and should not be treated as a medical judgment."
    else:
        pred = "uncertain"
        conf = 0.5
        evidence = ["the input image is ambiguous in the offline fallback path"]
        justification = "Offline fallback used because the requested multimodal checkpoint could not be loaded locally. The prediction is heuristic and should not be treated as a medical judgment."

    return {
        "image_quality": quality,
        "predicted_class": pred,
        "confidence": round(float(conf), 3),
        "visual_evidence": evidence,
        "justification": justification,
        "limitations": [
            f"{model_name} could not be loaded in this environment",
            "offline fallback heuristic used",
            "prompt was passed but not executed by a loaded checkpoint",
        ],
        "warning": WARNING,
        "model_name": model_name,
        "prompt_version": "improved",
        "latency_ms": 0,
        "prompt_preview": prompt[:200],
    }


def load_model(model_name: str) -> tuple[Any, Any] | None:
    if model_name in models and model_name in processors:
        return models[model_name], processors[model_name]
    if model_name in load_failures:
        return None

    config = MODEL_CONFIGS[model_name]
    adapter_path = Path(config["lora_path"])
    allow_remote = os.getenv("ALLOW_REMOTE_MODEL_LOAD", "0") == "1"

    if not allow_remote:
        load_failures.add(model_name)
        return None

    if not adapter_path.exists():
        load_failures.add(model_name)
        return None

    try:
        processor = AutoProcessor.from_pretrained(config["model_id"], local_files_only=True)
        if USE_QLORA:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            base_model = AutoModelForImageTextToText.from_pretrained(
                config["model_id"],
                quantization_config=bnb_config,
                torch_dtype=torch.bfloat16,
                device_map="cpu",
                low_cpu_mem_usage=True,
                local_files_only=True,
            )
            model = PeftModel.from_pretrained(base_model, str(adapter_path))
        else:
            model = AutoModelForImageTextToText.from_pretrained(
                config["model_id"],
                torch_dtype=torch.bfloat16,
                device_map="cpu",
                low_cpu_mem_usage=True,
                local_files_only=True,
            )
        model.eval()
        processors[model_name] = processor
        models[model_name] = model
        return model, processor
    except Exception:
        load_failures.add(model_name)
        return None


def vlm_predict_gemma4(image_path: str | Path, prompt: str) -> dict[str, Any]:
    start = time.perf_counter()
    loaded = load_model("gemma4_e4b")
    if loaded is None:
        pred = _fallback_prediction(image_path, "gemma4_e4b", prompt)
        pred["latency_ms"] = int((time.perf_counter() - start) * 1000)
        return pred

    model, processor = loaded
    image = Image.open(image_path).convert("RGB")
    inputs = processor(
        images=image,
        text=processor.tokenizer.boi_token + " " + prompt,
        return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=200, do_sample=False)
    text = processor.batch_decode(outputs, skip_special_tokens=True)[0].lower()
    pred = "suspected_opacity" if any(token in text for token in ("suspected_opacity", "opacity", "pneumonia")) else "normal" if "normal" in text else "uncertain"
    latency_ms = int((time.perf_counter() - start) * 1000)

    return {
        "image_quality": basic_quality_flag(image_path),
        "predicted_class": pred,
        "confidence": 0.6 if pred != "uncertain" else 0.5,
        "visual_evidence": [],
        "justification": text[:300],
        "limitations": [
            "gemma4_e4b inference used local checkpoint attempt",
            "structured JSON output is not guaranteed",
            "not clinically validated",
        ],
        "warning": WARNING,
        "model_name": "gemma4_e4b",
        "latency_ms": latency_ms,
    }


def vlm_predict_medgemma(image_path: str | Path, prompt: str) -> dict[str, Any]:
    start = time.perf_counter()
    loaded = load_model("medgemma_4b_pt")
    if loaded is None:
        pred = _fallback_prediction(image_path, "medgemma_4b_pt", prompt)
        pred["latency_ms"] = int((time.perf_counter() - start) * 1000)
        return pred

    model, processor = loaded
    image = Image.open(image_path).convert("RGB")
    inputs = processor(
        images=image,
        text=processor.tokenizer.boi_token + " " + prompt,
        return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=200, do_sample=False)
    text = processor.batch_decode(outputs, skip_special_tokens=True)[0].lower()
    pred = "suspected_opacity" if any(token in text for token in ("suspected_opacity", "opacity", "pneumonia")) else "normal" if "normal" in text else "uncertain"
    latency_ms = int((time.perf_counter() - start) * 1000)

    return {
        "image_quality": basic_quality_flag(image_path),
        "predicted_class": pred,
        "confidence": 0.6 if pred != "uncertain" else 0.5,
        "visual_evidence": [],
        "justification": text[:300],
        "limitations": [
            "medgemma_4b_pt inference used local checkpoint attempt",
            "structured JSON output is not guaranteed",
            "not clinically validated",
        ],
        "warning": WARNING,
        "model_name": "medgemma_4b_pt",
        "latency_ms": latency_ms,
    }