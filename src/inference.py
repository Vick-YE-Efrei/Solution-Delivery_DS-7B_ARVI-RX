from __future__ import annotations

import os
import sys
from pathlib import Path
import time
from typing import Any

# Disable fast HF transfer acceleration when the optional package is not available or when running in older environments.
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["HF_XET_HIGH_PERFORMANCE"] = "0"
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig
from peft import PeftModel

from .preprocessing import basic_quality_flag

WARNING = "Prototype pédagogique. Non destiné au diagnostic. Validation par un professionnel qualifié requise."
MODEL_CONFIGS = {
    "gemma4_e4b": {
        "model_id": "google/gemma-4-E2B",
        "processor_id": "google/gemma-4-E2B",
        "lora_path": "./finetuning/lora_adapters/gemma_4_E4B/gemma4_chestxray_lora_adapters",
    },
    "medgemma_4b_pt": {
        "model_id": "google/medgemma-4b-pt",
        "processor_id": "google/medgemma-4b-pt",
        "lora_path": "./finetuning/lora_adapters/medgemma_4b_pt",
    },
}
USE_QLORA = True  # True pour QLoRA, False pour le modèle de base

processors: dict[str, Any] = {}
models: dict[str, Any] = {}
load_failures: set[str] = set()


def bitsandbytes_available() -> bool:
    try:
        import bitsandbytes  # noqa: F401
        return True
    except Exception:
        return False


def ensure_hf_transfer_compatibility() -> None:
    if os.environ.get("HF_HUB_ENABLE_HF_TRANSFER", "0") in ("1", "true", "True"):
        try:
            import hf_transfer  # type: ignore
        except ImportError:
            os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

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

    ensure_hf_transfer_compatibility()

    if not adapter_path.exists():
        load_failures.add(model_name)
        return None

    # If remote model downloads are not allowed (tests/CI), avoid attempting
    # to load large remote base model weights. Return early so callers can
    # use the offline fallback prediction instead of triggering huge downloads
    # or crashes when base weights are not present locally.
    model_id_is_local = Path(config.get("model_id", "")).exists()
    if not allow_remote and not model_id_is_local:
        load_failures.add(model_name)
        return None

    def load_processor(local_only: bool) -> Any:
        sources = []
        if config.get("processor_id"):
            sources.append(config["processor_id"])
        if adapter_path.exists():
            sources.append(str(adapter_path))

        last_exc = None
        for src in sources:
            try:
                return AutoProcessor.from_pretrained(src, local_files_only=local_only)
            except Exception as exc:
                last_exc = exc
                if debug:
                    print(f"[DEBUG] processor load failed for source {src}: {type(exc).__name__}: {exc}")
                continue

        # If processor still fails, try a tokenizer+image_processor composition as fallback.
        if last_exc is not None:
            msg = str(last_exc)
            if "Unrecognized processing class" in msg or "Can't instantiate a processor" in msg or "AttributeError" in msg:
                from transformers import AutoTokenizer, AutoImageProcessor
                tokenizer = None
                image_processor = None
                for src in sources:
                    if tokenizer is None:
                        try:
                            tokenizer = AutoTokenizer.from_pretrained(src, local_files_only=local_only)
                        except Exception:
                            tokenizer = None
                    if image_processor is None:
                        try:
                            image_processor = AutoImageProcessor.from_pretrained(src, local_files_only=local_only)
                        except Exception:
                            image_processor = None
                if tokenizer is None and image_processor is None:
                    raise last_exc

                # Ensure tokenizer has expected multimodal attributes used by Gemma/MedGemma
                if tokenizer is not None:
                    if not hasattr(tokenizer, "image_token_id"):
                        vocab = getattr(tokenizer, "get_vocab", lambda: {})()
                        found = False
                        for candidate in ("<image>", "<img>", "<image0>"):
                            if candidate in vocab:
                                tokenizer.image_token_id = tokenizer.convert_tokens_to_ids(candidate)
                                found = True
                                break
                        if not found:
                            tokenizer.image_token_id = getattr(tokenizer, "bos_token_id", getattr(tokenizer, "cls_token_id", 0))
                    if not hasattr(tokenizer, "boi_token"):
                        tokenizer.boi_token = getattr(tokenizer, "boi_token", getattr(tokenizer, "bos_token", ""))

                class _SimpleProcessor:
                    def __init__(self, tokenizer, image_processor):
                        self.tokenizer = tokenizer
                        self.image_processor = image_processor

                    def __call__(self, images, text, return_tensors="pt"):
                        img_inputs = ({ } if self.image_processor is None else self.image_processor(images=images, return_tensors=return_tensors))
                        tok_inputs = ({ } if self.tokenizer is None else self.tokenizer(text, return_tensors=return_tensors))
                        combined = {}
                        combined.update(img_inputs)
                        combined.update(tok_inputs)
                        return combined

                    def batch_decode(self, outputs, skip_special_tokens=True):
                        if self.tokenizer is None:
                            raise RuntimeError("No tokenizer available for decoding")
                        return self.tokenizer.batch_decode(outputs, skip_special_tokens=skip_special_tokens)

                return _SimpleProcessor(tokenizer, image_processor)
        raise last_exc

    def load_base_model(local_only: bool, use_qlora: bool) -> Any:
        if use_qlora:
            if not bitsandbytes_available():
                raise RuntimeError(
                    "bitsandbytes is required for QLoRA model loading. "
                    "Install it in the current environment with `pip install bitsandbytes`."
                )
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
                local_files_only=local_only,
            )
            return PeftModel.from_pretrained(base_model, str(adapter_path))

        return AutoModelForImageTextToText.from_pretrained(
            config["model_id"],
            torch_dtype=torch.bfloat16,
            device_map="cpu",
            low_cpu_mem_usage=True,
            local_files_only=local_only,
        )

    # Attempt local-only loading first; only fall back to remote if explicitly permitted.
    debug = os.environ.get("DEBUG_MODEL_LOAD", "0") in ("1", "true", "True")
    for local_only in (True, False):
        if local_only is False and not allow_remote:
            break
        try:
            if debug:
                print(f"[DEBUG] load_model({model_name}) local_only={local_only}")
            processor = load_processor(local_only)
            if debug:
                print(f"[DEBUG] processor loaded for {model_name} local_only={local_only}")
            # Ensure tokenizer attached to processor has required multimodal attributes
            try:
                tokenizer = getattr(processor, "tokenizer", None)
                if tokenizer is not None:
                    try:
                        if not hasattr(tokenizer, "image_token_id"):
                            vocab = getattr(tokenizer, "get_vocab", lambda: {})()
                            found = False
                            for candidate in ("<image>", "<img>", "<image0>"):
                                if candidate in vocab:
                                    tokenizer.image_token_id = tokenizer.convert_tokens_to_ids(candidate)
                                    found = True
                                    break
                            if not found:
                                tokenizer.image_token_id = getattr(tokenizer, "bos_token_id", getattr(tokenizer, "cls_token_id", 0))
                        if not hasattr(tokenizer, "boi_token"):
                            tokenizer.boi_token = getattr(tokenizer, "boi_token", getattr(tokenizer, "bos_token", ""))
                    except Exception:
                        # Some tokenizer implementations are extension types that don't allow new attributes.
                        # Wrap in a proxy that delegates to the original tokenizer but supplies the missing attributes.
                        class _TokenizerProxy:
                            def __init__(self, tok, image_token_id, boi_token):
                                self._tok = tok
                                self.image_token_id = image_token_id
                                self.boi_token = boi_token

                            def __getattr__(self, name):
                                return getattr(self._tok, name)

                            def get_vocab(self):
                                return getattr(self._tok, "get_vocab", lambda: {})()

                            def convert_tokens_to_ids(self, *a, **k):
                                return self._tok.convert_tokens_to_ids(*a, **k)

                            def __call__(self, *a, **k):
                                return self._tok(*a, **k)

                            def batch_decode(self, *a, **k):
                                return getattr(self._tok, "batch_decode", lambda *x, **y: None)(*a, **k)

                        vocab = getattr(tokenizer, "get_vocab", lambda: {})()
                        found = False
                        for candidate in ("<image>", "<img>", "<image0>"):
                            if candidate in vocab:
                                image_token_id = tokenizer.convert_tokens_to_ids(candidate)
                                found = True
                                break
                        if not found:
                            image_token_id = getattr(tokenizer, "bos_token_id", getattr(tokenizer, "cls_token_id", 0))
                        boi_token = getattr(tokenizer, "bos_token", "")
                        tokenizer = _TokenizerProxy(tokenizer, image_token_id, boi_token)
                        # Attach proxy back to processor
                        try:
                            processor.tokenizer = tokenizer
                        except Exception:
                            pass
            except Exception:
                if debug:
                    import traceback
                    traceback.print_exc()
            # Determine whether QLoRA is usable in this environment
            effective_use_qlora = USE_QLORA
            if effective_use_qlora:
                if not bitsandbytes_available():
                    if debug:
                        print("[DEBUG] bitsandbytes not available; disabling QLoRA fallback")
                    effective_use_qlora = False
            model = None
            if effective_use_qlora:
                model = load_base_model(local_only, effective_use_qlora)
            else:
                # fallback to non-QLoRA base model loading path
                if debug:
                    print(f"[DEBUG] loading base model without QLoRA for {model_name}")
                model = load_base_model(local_only, False)
            model.eval()
            processors[model_name] = processor
            models[model_name] = model
            return model, processor
        except Exception as exc:
            if debug:
                print(f"[DEBUG] load_model({model_name}) failed local_only={local_only}: {type(exc).__name__}: {exc}")
            continue

    load_failures.add(model_name)
    return None


def vlm_predict_gemma4(image_path: str | Path, prompt: str, allow_fallback: bool = True) -> dict[str, Any]:
    start = time.perf_counter()
    loaded = load_model("gemma4_e4b")
    if loaded is None:
        if not allow_fallback:
            raise RuntimeError("gemma4_e4b could not be loaded for inference; fallback is disabled in this mode.")
        # Use deterministic toy predictor as the offline fallback for simplicity.
        mode = "improved" if isinstance(prompt, str) and "improved" in prompt else "baseline"
        pred = toy_predict(image_path, mode=mode)
        pred["latency_ms"] = int((time.perf_counter() - start) * 1000)
        return pred

    model, processor = loaded
    image = Image.open(image_path).convert("RGB")
    boi = getattr(getattr(processor, "tokenizer", None), "boi_token", None)
    if boi is None:
        # fallback to bos_token or start token if available
        boi = getattr(getattr(processor, "tokenizer", None), "bos_token", "")
    full_text = (boi + " " + prompt).strip()
    inputs = processor(
        images=image,
        text=full_text,
        return_tensors="pt",
    )
    # move tensors to model device if present
    try:
        inputs = {k: v.to(model.device) for k, v in inputs.items() if hasattr(v, "to")}
    except Exception:
        pass

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


def vlm_predict_medgemma(image_path: str | Path, prompt: str, allow_fallback: bool = True) -> dict[str, Any]:
    start = time.perf_counter()
    loaded = load_model("medgemma_4b_pt")
    if loaded is None:
        if not allow_fallback:
            raise RuntimeError("medgemma_4b_pt could not be loaded for inference; fallback is disabled in this mode.")
        # Use deterministic toy predictor as the offline fallback for simplicity.
        mode = "improved" if isinstance(prompt, str) and "improved" in prompt else "baseline"
        pred = toy_predict(image_path, mode=mode)
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