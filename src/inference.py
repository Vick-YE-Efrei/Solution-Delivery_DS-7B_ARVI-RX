from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any

os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")
os.environ.setdefault("HF_XET_HIGH_PERFORMANCE", "0")

from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

from .preprocessing import basic_quality_flag

WARNING = "Prototype pédagogique. Non destiné au diagnostic. Validation par un professionnel qualifié requise."
MODEL_CONFIGS = {
    "medgemma_4b_pt": {
        "model_id": "google/medgemma-4b-pt",
        "processor_id": "google/medgemma-4b-pt",
    },
}

# Amorce JSON injectée à la fin du tour "model". Force le modèle à COMPLETER
# un JSON déjà commencé plutôt qu'à décider seul du format de sa réponse :
# indispensable pour un modèle de base non instruction-tuned (ex: -pt), et
# sans effet négatif sur un modèle instruction-tuned.
JSON_PREFIX = '{\n  "image_quality": "'


def _build_priming_prompt(processor: Any, prompt_text: str) -> tuple[str, str]:
    """Construit un prompt au format chat Gemma se terminant par JSON_PREFIX.

    Si le processor n'expose pas les tokens spéciaux Gemma (boi_token), on
    revient au comportement d'origine (texte brut) pour ne rien casser.
    Retourne (texte_du_prompt, prefixe_json_utilisé).
    """
    boi = getattr(processor, "boi_token", None)
    if not boi:
        return prompt_text.strip(), ""
    full_prompt = (
        f"<start_of_turn>user\n{boi}\n{prompt_text.strip()}<end_of_turn>\n"
        f"<start_of_turn>model\n{JSON_PREFIX}"
    )
    return full_prompt, JSON_PREFIX

processors: dict[str, Any] = {}
models: dict[str, Any] = {}
load_failures: set[str] = set()


def toy_predict(image_path: str | Path, mode: str = "baseline") -> dict[str, Any]:
    """Deterministic toy predictor used to validate the repo pipeline."""
    start = time.perf_counter()
    name = Path(image_path).name.lower()
    quality = basic_quality_flag(image_path)

    if "suspected_opacity" in name:
        predicted_class = "suspected_opacity"
        confidence = 0.78 if mode == "baseline" else 0.72
        evidence = ["synthetic opacity-like area visible in the lung field"]
        justification = "The synthetic image contains a localized brighter region compatible with the toy opacity class."
    elif "normal" in name:
        predicted_class = "normal"
        confidence = 0.72 if mode == "baseline" else 0.68
        evidence = ["no synthetic opacity marker detected"]
        justification = "The synthetic image does not contain the opacity marker used by the toy generator."
    else:
        predicted_class = "uncertain"
        confidence = 0.52
        evidence = ["limited synthetic image quality"]
        justification = "The image is treated as limited quality in the toy catalog."

    latency_ms = int((time.perf_counter() - start) * 1000)
    return {
        "image_quality": quality,
        "predicted_class": predicted_class,
        "confidence": round(float(confidence), 3),
        "visual_evidence": evidence,
        "justification": justification,
        "limitations": ["synthetic toy image", "no clinical context", "not a validated medical model"],
        "warning": WARNING,
        "model_name": f"toy-rule-{mode}",
        "prompt_version": f"{mode}_v1",
        "latency_ms": latency_ms,
    }


def load_model(model_name: str) -> tuple[Any, Any] | None:
    if model_name in models and model_name in processors:
        return models[model_name], processors[model_name]
    if model_name in load_failures:
        return None

    config = MODEL_CONFIGS[model_name]
    allow_remote = os.getenv("ALLOW_REMOTE_MODEL_LOAD", "0") == "1"

    # Si le téléchargement distant est désactivé, on passe en mode offline :
    # transformers utilise alors le cache HF existant sans tenter de contacter
    # le Hub. Le cache est ~/.cache/huggingface/hub par défaut.
    if not allow_remote:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")

    try:
        processor = AutoProcessor.from_pretrained(config["processor_id"])
        model = AutoModelForImageTextToText.from_pretrained(
            config["model_id"],
            dtype=torch.bfloat16,
            device_map="cpu",
            low_cpu_mem_usage=True,
        )
        model.eval()
        processors[model_name] = processor
        models[model_name] = model
        return model, processor
    except Exception as exc:
        print(f"[WARN] Failed to load model {model_name}: {exc}", file=sys.stderr)
        load_failures.add(model_name)
        return None


def _extract_json_from_response(text: str) -> dict[str, Any] | None:
    """Extract JSON object from model response (may be wrapped in markdown or text)."""
    # Try to find JSON wrapped in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find raw JSON object
    json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    return None


def vlm_predict_medgemma(image_path: str | Path, prompt: str, allow_fallback: bool = True) -> dict[str, Any]:
    start = time.perf_counter()
    loaded = load_model("medgemma_4b_pt")
    if loaded is None:
        if not allow_fallback:
            raise RuntimeError("medgemma_4b_pt could not be loaded for inference; fallback is disabled in this mode.")
        mode = "improved" if isinstance(prompt, str) and "improved" in prompt else "baseline"
        pred = toy_predict(image_path, mode=mode)
        pred["latency_ms"] = int((time.perf_counter() - start) * 1000)
        return pred

    model, processor = loaded
    try:
        image = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        mode = "improved" if isinstance(prompt, str) and "improved" in prompt else "baseline"
        pred = toy_predict(image_path, mode=mode)
        pred["latency_ms"] = int((time.perf_counter() - start) * 1000)
        return pred
    full_prompt, json_prefix = _build_priming_prompt(processor, prompt)
    inputs = processor(images=image, text=full_prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=512, do_sample=False)
    generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
    continuation = processor.decode(generated_ids, skip_special_tokens=True)
    response_text = json_prefix + continuation
    latency_ms = int((time.perf_counter() - start) * 1000)

    # Try to extract structured JSON from model response
    extracted = _extract_json_from_response(response_text)
    if extracted and isinstance(extracted, dict):
        # Ensure all required fields are present
        result = {
            "image_quality": extracted.get("image_quality", basic_quality_flag(image_path)),
            "predicted_class": extracted.get("predicted_class", "uncertain"),
            "confidence": float(extracted.get("confidence", 0.5)),
            "visual_evidence": extracted.get("visual_evidence", []),
            "justification": extracted.get("justification", response_text[:300]),
            "limitations": extracted.get("limitations", ["model inference used"]),
            "warning": WARNING,
            "model_name": "medgemma_4b_pt",
            "latency_ms": latency_ms,
        }
        return result
    
    # Fallback to simple heuristic parsing if JSON extraction fails
    response_lower = response_text.lower()
    predicted_class = "suspected_opacity" if any(token in response_lower for token in ("suspected_opacity", "opacity", "pneumonia")) else "normal" if "normal" in response_lower else "uncertain"
    
    return {
        "image_quality": basic_quality_flag(image_path),
        "predicted_class": predicted_class,
        "confidence": 0.6 if predicted_class != "uncertain" else 0.5,
        "visual_evidence": [response_text[:100]],
        "justification": response_text[:300],
        "limitations": ["model inference used", "structured JSON output fallback"],
        "warning": WARNING,
        "model_name": "medgemma_4b_pt",
        "latency_ms": latency_ms,
    }