from __future__ import annotations

"""End-to-end orchestration for the educational chest-X-ray pipeline.

This module is the main entry point for running a complete inference cycle:
image loading, prompt selection, prediction, guardrails and artifact persistence.
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .database import insert_run
from .guardrails import apply_safety_guardrails
from .inference import toy_predict
from .preprocessing import basic_quality_flag, load_image

class PipelineError(RuntimeError):
    pass

def _load_prompt(prompt_mode: str) -> str:
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / f"{prompt_mode}_prompt.txt"
    if not prompt_path.exists():
        raise PipelineError(f"Prompt not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")

def run_pipeline(
    image_path: str | Path,
    mode: str = "baseline",
    prompt_mode: str = "baseline",
    output_dir: str | Path | None = None,
    db_path: str | Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Run a complete, traceable inference pipeline for the educational prototype."""
    image_path = Path(image_path)
    if not image_path.exists():
        raise PipelineError(f"Image not found: {image_path}")

    output_dir = Path(output_dir or Path("eval/results_json"))
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = Path(db_path or Path("medical_ai_evidence.sqlite"))

    start = time.perf_counter()
    image = load_image(image_path)
    prompt_text = _load_prompt(prompt_mode)
    raw_prediction = toy_predict(image_path, mode=mode)
    guarded_prediction = apply_safety_guardrails(raw_prediction)

    run_uuid = run_id or str(uuid.uuid4())
    latency_ms = int((time.perf_counter() - start) * 1000)
    guarded_prediction["latency_ms"] = latency_ms
    guarded_prediction["image_quality"] = basic_quality_flag(image_path)
    guarded_prediction["prompt_version"] = f"{prompt_mode}_v1"
    guarded_prediction["prompt_preview"] = prompt_text[:200]

    payload = {
        "run_id": run_uuid,
        "pipeline_status": "completed",
        "image_path": str(image_path),
        "image_size": list(image.size),
        "mode": mode,
        "prompt_mode": prompt_mode,
        "metadata": {
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "image_format": image_path.suffix.lower(),
            "prompt_mode": prompt_mode,
            "model_name": guarded_prediction.get("model_name", "toy-rule"),
            "prompt_version": guarded_prediction.get("prompt_version", f"{prompt_mode}_v1"),
        },
        **guarded_prediction,
    }

    output_path = output_dir / f"{run_uuid}.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    insert_run(
        db_path=db_path,
        case_id=run_uuid,
        image_path=str(image_path),
        prediction={
            **guarded_prediction,
            "model_name": guarded_prediction.get("model_name", "toy-rule"),
            "prompt_version": guarded_prediction.get("prompt_version", f"{prompt_mode}_v1"),
            "latency_ms": latency_ms,
        },
    )

    return payload
