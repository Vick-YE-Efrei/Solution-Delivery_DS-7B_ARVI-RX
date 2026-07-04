from __future__ import annotations

"""Evaluation script for running toy and comparison experiments.

This module produces predictions, metrics and artefacts that can be used for
reporting and comparing prompt variants or model backends.
"""

import argparse
import csv
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.guardrails import apply_safety_guardrails, validate_prediction
from src.metrics import summarize_metrics
from src.database import insert_run, init_db


SUPPORTED_DATASETS = {
    "chest_xray": ROOT / "data" / "chest_xray" / "chest_xray_train.csv",
}


def read_cases(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def resolve_dataset(path: str | None) -> Path:
    if path is None:
        return SUPPORTED_DATASETS["chest_xray"]
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (ROOT / candidate).resolve()


def build_predictor(model_name: str, prompt_path: Path):
    import src.inference as inference

    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_version = "baseline_v1" if prompt_path.name.startswith("baseline") else "improved"

    if model_name == "gemma4_e4b":
        def predict_fn(img):
            pred = inference.vlm_predict_gemma4(img, prompt_text, allow_fallback=True)
            pred["prompt_version"] = prompt_version
            return pred
    elif model_name == "medgemma_4b_pt":
        def predict_fn(img):
            pred = inference.vlm_predict_medgemma(img, prompt_text, allow_fallback=True)
            pred["prompt_version"] = prompt_version
            return pred
    else:
        raise ValueError(f"Unsupported model: {model_name}")

    return predict_fn


def format_prediction_row(case: dict, image_path: Path, pred: dict) -> dict:
    return {
        "case_id": case["case_id"],
        "image_path": str(image_path),
        "label": case["label"],
        "model": pred.get("model_name", "unknown"),
        "prompt_version": pred.get("prompt_version", "unknown"),
        "predicted_class": pred["predicted_class"],
        "confidence": pred["confidence"],
        "image_quality": pred.get("image_quality", ""),
        "visual_evidence": json.dumps(pred.get("visual_evidence", []), ensure_ascii=False),
        "justification": pred.get("justification", ""),
        "limitations": json.dumps(pred.get("limitations", []), ensure_ascii=False),
        "warning": pred.get("warning", ""),
        "latency_ms": pred.get("latency_ms", 0),
        "json_valid": pred.get("json_valid", True),
        "guardrail_errors": ";".join(pred.get("guardrail_errors", [])) if isinstance(pred.get("guardrail_errors", []), list) else pred.get("guardrail_errors", ""),
        "prediction_json": json.dumps(pred, ensure_ascii=False),
    }


def run(mode: str, db_path: Path, dataset_path: Path | None = None, model_names: list[str] | None = None, toy_prompt_mode: str | None = None) -> tuple[list[dict], dict, list[dict]]:
    cases = read_cases(dataset_path or SUPPORTED_DATASETS["chest_xray"])
    if mode == "toy":
        cases = cases[:20]
    rows: list[dict] = []
    init_db(db_path)
    model_names = model_names or ["gemma4_e4b", "medgemma_4b_pt"]

    if mode == "toy":
        # toy_prompt_mode selects whether this toy run simulates the 'baseline'
        # or 'improved' prompt; default to 'baseline' when not provided.
        prompt_mode = (toy_prompt_mode or "baseline")

        def predict_fn(img):
            name = Path(img).name.lower()
            if "suspected_opacity" in name:
                pred = "suspected_opacity"
                conf = 0.78
                evidence = ["synthetic opacity-like area visible in the lung field"]
                justification = "The synthetic image contains a localized brighter region compatible with the toy opacity class. This is a pipeline validation result, not a medical interpretation."
            elif "normal" in name:
                pred = "normal"
                conf = 0.72
                evidence = ["no synthetic opacity marker detected"]
                justification = "The synthetic image does not contain the opacity marker used by the toy generator. This conclusion is limited to the synthetic validation setting."
            else:
                pred = "uncertain"
                conf = 0.52
                evidence = ["limited synthetic image quality"]
                justification = "The image is treated as limited quality in the toy catalog. The safe output is uncertainty rather than a forced class."
            return {
                "image_quality": "good",
                "predicted_class": pred,
                "confidence": round(float(conf), 3),
                "visual_evidence": evidence,
                "justification": justification,
                "limitations": ["synthetic toy image", "no clinical context", "not a validated medical model"],
                "warning": "Prototype pédagogique. Non destiné au diagnostic. Validation par un professionnel qualifié requise.",
                "model_name": "toy-rule-baseline",
                "prompt_version": f"{prompt_mode}_v1",
                "latency_ms": 1,
            }

        for case in cases:
            image_path = (ROOT / case["image_path"]).resolve()
            pred = predict_fn(image_path)
            pred = apply_safety_guardrails(pred)
            valid, errors = validate_prediction(pred)
            pred["json_valid"] = valid
            pred["guardrail_errors"] = errors
            row = format_prediction_row(case, image_path, pred)
            rows.append(row)
            insert_run(db_path, case["case_id"], str(image_path), pred)

        metrics = summarize_metrics(rows)
        return rows, metrics, [{"model": "toy", **metrics}]

    if mode in ("baseline", "improved"):
        prompt_path = ROOT / "prompts" / f"{mode}_prompt.txt"
        metrics_by_model: list[dict] = []

        for model_name in model_names:
            predict_fn = build_predictor(model_name, prompt_path)
            model_rows: list[dict] = []
            for case in cases:
                image_path = (ROOT / case["image_path"]).resolve()
                try:
                    pred = predict_fn(image_path)
                except Exception as exc:
                    # If model loading failed (e.g. specialized processor missing or QLoRA issues),
                    # try an offline/relaxed fallback prediction so the run can continue.
                    import src.inference as inference  # local import to avoid startup cost
                    msg = str(exc)
                    print(f"[WARN] prediction failed for model {model_name} on {image_path.name}: {msg}", file=sys.stderr)
                    if model_name == "gemma4_e4b":
                        pred = inference.vlm_predict_gemma4(image_path, prompt_path.read_text(encoding="utf-8"), allow_fallback=True)
                    elif model_name == "medgemma_4b_pt":
                        pred = inference.vlm_predict_medgemma(image_path, prompt_path.read_text(encoding="utf-8"), allow_fallback=True)
                    else:
                        # Last resort: return a safe uncertain prediction
                        pred = {
                            "image_quality": "unknown",
                            "predicted_class": "uncertain",
                            "confidence": 0.5,
                            "visual_evidence": [],
                            "justification": "Prediction skipped due to model load error.",
                            "limitations": [f"Model {model_name} could not be loaded: {msg}"],
                            "warning": "Model unavailable; offline fallback used.",
                            "model_name": model_name,
                            "prompt_version": "unknown",
                            "latency_ms": 0,
                        }
                pred = apply_safety_guardrails(pred)
                valid, errors = validate_prediction(pred)
                pred["json_valid"] = valid
                pred["guardrail_errors"] = errors
                row = format_prediction_row(case, image_path, pred)
                model_rows.append(row)
                rows.append(row)
                insert_run(db_path, case["case_id"], str(image_path), pred)
            metrics_by_model.append({"model": model_name, "prompt_mode": mode, **summarize_metrics(model_rows)})

        metrics = summarize_metrics(rows)
        return rows, metrics, metrics_by_model

    if mode == "compare":
        raise ValueError("compare mode must be handled separately")

    raise ValueError(f"Unsupported mode: {mode}")


def run_compare_models(db_path: Path, dataset_path: Path) -> tuple[list[dict], dict, list[dict]]:
    cases = read_cases(dataset_path)
    init_db(db_path)
    prompt_path = ROOT / "prompts" / "improved_prompt.txt"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    predictions_by_model: dict[str, list[dict]] = {}
    metrics_by_model: list[dict] = []

    for model_name in ("gemma4_e4b", "medgemma_4b_pt"):
        rows = []
        if model_name == "gemma4_e4b":
            predict_fn = build_predictor(model_name, prompt_path)
        else:
            predict_fn = build_predictor(model_name, prompt_path)

        for case in cases:
            image_path = (ROOT / case["image_path"]).resolve()
            pred = predict_fn(image_path)
            pred = apply_safety_guardrails(pred)
            valid, errors = validate_prediction(pred)
            row = {
                "model": model_name,
                "case_id": case["case_id"],
                "image_path": str(image_path),
                "label": case["label"],
                "predicted_class": pred["predicted_class"],
                "confidence": pred["confidence"],
                "json_valid": valid,
                "warning": pred.get("warning", ""),
                "latency_ms": pred.get("latency_ms", 0),
                "guardrail_errors": ";".join(errors),
                "model_name": pred.get("model_name", model_name),
                "prompt_version": pred.get("prompt_version", "improved"),
            }
            rows.append(row)
            insert_run(db_path, case["case_id"], str(image_path), pred)

        predictions_by_model[model_name] = rows
        metrics_by_model.append({"model": model_name, **summarize_metrics(rows)})

    return predictions_by_model["gemma4_e4b"], metrics_by_model[0], predictions_by_model["medgemma_4b_pt"], metrics_by_model[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["toy", "baseline", "improved", "compare"], default="toy")
    parser.add_argument("--dataset", type=str, default=None)
    parser.add_argument("--models", type=str, default="gemma4_e4b,medgemma_4b_pt")
    parser.add_argument("--allow-remote-model-load", action="store_true", help="Allow downloading base model weights from remote when not available locally.")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "eval" / "comparison_comparison_outputs")
    parser.add_argument("--db-path", type=Path, default=ROOT / "medical_ai_evidence.sqlite")
    args = parser.parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    model_names = [m.strip() for m in args.models.split(",") if m.strip()]

    if args.allow_remote_model_load:
        os.environ["ALLOW_REMOTE_MODEL_LOAD"] = "1"

    if args.mode == "compare":
        dataset_path = resolve_dataset(args.dataset)
        gemma_rows, gemma_metrics, medgemma_rows, medgemma_metrics = run_compare_models(args.db_path, dataset_path)
        write_csv(out_dir / "gemma4_e4b_predictions.csv", gemma_rows)
        write_csv(out_dir / "medgemma_4b_pt_predictions.csv", medgemma_rows)
        (out_dir / "gemma4_e4b_metrics.json").write_text(json.dumps(gemma_metrics, indent=2), encoding="utf-8")
        (out_dir / "medgemma_4b_pt_metrics.json").write_text(json.dumps(medgemma_metrics, indent=2), encoding="utf-8")
        comparison_payload = {
            "dataset": str(dataset_path),
            "models": [gemma_metrics, medgemma_metrics],
        }
        (out_dir / "model_comparison_metrics.json").write_text(json.dumps(comparison_payload, indent=2), encoding="utf-8")
        print(json.dumps(comparison_payload, indent=2))
        return

    if args.mode == "toy":
        modes = ["baseline", "improved"]
    else:
        modes = [args.mode]

    summary = []
    for mode in modes:
        if args.mode == "toy":
            # run the toy pipeline but simulate the requested prompt mode
            rows, metrics, metrics_by_model = run("toy", args.db_path, resolve_dataset(args.dataset), model_names=model_names, toy_prompt_mode=mode)
        else:
            rows, metrics, metrics_by_model = run(mode, args.db_path, resolve_dataset(args.dataset), model_names=model_names)
        write_csv(out_dir / f"{mode}_predictions.csv", rows)
        (out_dir / f"{mode}_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

        for model_metrics in metrics_by_model:
            model = model_metrics["model"]
            model_rows = [row for row in rows if row["model"] == model]
            write_csv(out_dir / f"{mode}_{model}_predictions.csv", model_rows)
            (out_dir / f"{mode}_{model}_metrics.json").write_text(json.dumps(model_metrics, indent=2), encoding="utf-8")
            summary.append({"mode": mode, "model": model, **model_metrics})

    write_csv(out_dir / "before_after_summary.csv", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()