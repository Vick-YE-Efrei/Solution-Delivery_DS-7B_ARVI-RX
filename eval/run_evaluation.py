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
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def resolve_dataset(path: str | None) -> Path:
    if path is None:
        return SUPPORTED_DATASETS["chest_xray"]
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (ROOT / candidate).resolve()


def build_predictor(prompt_path: Path):
    import src.inference as inference

    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_version = "baseline" if prompt_path.name.startswith("baseline") else "improved"

    def predict_fn(img):
        pred = inference.vlm_predict_medgemma(img, prompt_text, allow_fallback=True)
        pred["prompt_version"] = prompt_version
        return pred

    return predict_fn


def run(mode: str, db_path: Path, dataset_path: Path | None = None, toy_prompt_mode: str | None = None) -> tuple[list[dict], dict, list[dict]]:
    cases = read_cases(dataset_path or SUPPORTED_DATASETS["chest_xray"])
    if mode == "toy":
        cases = cases[:20]
    rows: list[dict] = []
    init_db(db_path)
    if mode == "toy":
        prompt_mode = toy_prompt_mode or "baseline"

        def predict_fn(img):
            name = Path(img).name.lower()
            if "suspected_opacity" in name:
                predicted_class = "suspected_opacity"
                confidence = 0.78
            elif "normal" in name:
                predicted_class = "normal"
                confidence = 0.72
            else:
                predicted_class = "uncertain"
                confidence = 0.52
            return {
                "image_quality": "good",
                "predicted_class": predicted_class,
                "confidence": round(float(confidence), 3),
                "visual_evidence": ["synthetic toy image marker detected" if predicted_class != "uncertain" else "limited synthetic signal"],
                "justification": "Toy evaluation output for the educational prototype.",
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
            row = {
                "case_id": case["case_id"],
                "image_path": str(image_path),
                "label": case["label"],
                "model": pred.get("model_name", "unknown"),
                "prompt_version": pred.get("prompt_version", "unknown"),
                "predicted_class": pred["predicted_class"],
                "confidence": pred["confidence"],
                "image_quality": pred.get("image_quality", ""),
                "warning": pred.get("warning", ""),
                "latency_ms": pred.get("latency_ms", 0),
                "json_valid": pred.get("json_valid", True),
                "guardrail_errors": ";".join(pred.get("guardrail_errors", [])) if isinstance(pred.get("guardrail_errors", []), list) else pred.get("guardrail_errors", ""),
            }
            rows.append(row)
            insert_run(db_path, case["case_id"], str(image_path), pred)

        metrics = summarize_metrics(rows)
        return rows, metrics, [{"model": "toy", **metrics}]

    if mode in ("baseline", "improved"):
        prompt_path = ROOT / "prompts" / f"{mode}_prompt.txt"
        predict_fn = build_predictor(prompt_path)
        rows: list[dict] = []
        for case in cases:
            image_path = (ROOT / case["image_path"]).resolve()
            try:
                pred = predict_fn(image_path)
            except Exception as exc:
                import src.inference as inference
                msg = str(exc)
                print(f"[WARN] prediction failed on {image_path.name}: {msg}", file=sys.stderr)
                pred = inference.vlm_predict_medgemma(image_path, prompt_path.read_text(encoding="utf-8"), allow_fallback=True)
            pred = apply_safety_guardrails(pred)
            valid, errors = validate_prediction(pred)
            pred["json_valid"] = valid
            pred["guardrail_errors"] = errors
            row = {
                "case_id": case["case_id"],
                "image_path": str(image_path),
                "label": case["label"],
                "model": pred.get("model_name", "unknown"),
                "prompt_version": pred.get("prompt_version", "unknown"),
                "predicted_class": pred["predicted_class"],
                "confidence": pred["confidence"],
                "image_quality": pred.get("image_quality", ""),
                "warning": pred.get("warning", ""),
                "latency_ms": pred.get("latency_ms", 0),
                "json_valid": pred.get("json_valid", True),
                "guardrail_errors": ";".join(pred.get("guardrail_errors", [])) if isinstance(pred.get("guardrail_errors", []), list) else pred.get("guardrail_errors", ""),
            }
            rows.append(row)
            insert_run(db_path, case["case_id"], str(image_path), pred)
        metrics = summarize_metrics(rows)
        return rows, metrics, [{"model": "medgemma_4b_pt", "prompt_mode": mode, **metrics}]

    if mode == "compare":
        raise ValueError("compare mode must be handled separately")

    raise ValueError(f"Unsupported mode: {mode}")


def run_compare_baselines(db_path: Path, dataset_path: Path, max_cases: int | None = None) -> tuple[list[dict], list[dict], dict]:
    """Compare baseline vs improved prompts with medgemma model."""
    cases = read_cases(dataset_path)
    if max_cases is not None:
        cases = cases[:max_cases]
    init_db(db_path)
    
    results_by_mode: dict[str, list[dict]] = {}
    
    for mode in ("baseline", "improved"):
        prompt_path = ROOT / "prompts" / f"{mode}_prompt.txt"
        predict_fn = build_predictor(prompt_path)
        rows = []
        
        for case in cases:
            image_path = (ROOT / case["image_path"]).resolve()
            try:
                pred = predict_fn(image_path)
            except Exception as exc:
                import src.inference as inference
                msg = str(exc)
                print(f"[WARN] prediction failed for {mode} on {image_path.name}: {msg}", file=sys.stderr)
                prompt_text = prompt_path.read_text(encoding="utf-8")
                pred = inference.vlm_predict_medgemma(image_path, prompt_text, allow_fallback=True)
            
            pred = apply_safety_guardrails(pred)
            valid, errors = validate_prediction(pred)
            
            row = {
                "mode": mode,
                "case_id": case["case_id"],
                "image_path": str(image_path),
                "label": case["label"],
                "predicted_class": pred["predicted_class"],
                "confidence": pred["confidence"],
                "json_valid": valid,
                "warning": pred.get("warning", ""),
                "latency_ms": pred.get("latency_ms", 0),
                "guardrail_errors": ";".join(errors),
            }
            rows.append(row)
            insert_run(db_path, case["case_id"], str(image_path), pred)
        
        results_by_mode[mode] = rows
    
    baseline_rows = results_by_mode["baseline"]
    improved_rows = results_by_mode["improved"]
    
    comparison_metrics = {
        "baseline": summarize_metrics(baseline_rows),
        "improved": summarize_metrics(improved_rows),
    }
    
    return baseline_rows, improved_rows, comparison_metrics


def resolve_output_dir(path: Path | str | None) -> Path:
    if path is None:
        return ROOT / "eval" / "results_json"
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    # If it's just a basename like "results_json", put it in eval/
    if "/" not in str(candidate) and "\\" not in str(candidate):
        return (ROOT / "eval" / candidate).resolve()
    return (ROOT / candidate).resolve()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["toy", "baseline", "improved", "compare"], default="toy")
    parser.add_argument("--dataset", type=str, default=None)
    parser.add_argument("--max-cases", type=int, default=None, help="Limit the number of cases processed (useful for testing).")
    parser.add_argument("--allow-remote-model-load", action="store_true", help="Allow downloading base model weights from remote when not available locally.")
    parser.add_argument("--out-dir", type=str, default=None, help="Output directory for results (relative to project root or absolute path). Defaults to eval/results_json")
    parser.add_argument("--db-path", type=Path, default=ROOT / "medical_ai_evidence.sqlite")
    args = parser.parse_args()
    out_dir = resolve_output_dir(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.allow_remote_model_load:
        os.environ["ALLOW_REMOTE_MODEL_LOAD"] = "1"

    if args.mode == "compare":
        dataset_path = resolve_dataset(args.dataset)
        baseline_rows, improved_rows, comparison_metrics = run_compare_baselines(args.db_path, dataset_path, max_cases=args.max_cases)
        write_csv(out_dir / "baseline_predictions.csv", baseline_rows)
        write_csv(out_dir / "improved_predictions.csv", improved_rows)
        (out_dir / "baseline_metrics.json").write_text(json.dumps(comparison_metrics["baseline"], indent=2), encoding="utf-8")
        (out_dir / "improved_metrics.json").write_text(json.dumps(comparison_metrics["improved"], indent=2), encoding="utf-8")
        comparison_payload = {
            "dataset": str(dataset_path),
            "prompts": ["baseline", "improved"],
            "metrics": comparison_metrics,
        }
        (out_dir / "comparison_metrics.json").write_text(json.dumps(comparison_payload, indent=2), encoding="utf-8")
        print(json.dumps(comparison_payload, indent=2))
        return

    if args.mode == "toy":
        # Toy mode is independent: generate 20 toy predictions and output toy_metrics.json
        rows, metrics, metrics_by_model = run("toy", args.db_path, resolve_dataset(args.dataset), toy_prompt_mode="toy")
        aggregated_metrics = summarize_metrics(rows)
        output = {"mode": "toy", **aggregated_metrics}
        (out_dir / "toy_metrics.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(json.dumps(output, indent=2))
        return

    # Baseline or improved mode
    modes = [args.mode]

    all_rows = []
    for mode in modes:
        rows, metrics, metrics_by_model = run(mode, args.db_path, resolve_dataset(args.dataset))
        write_csv(out_dir / f"{mode}_predictions.csv", rows)
        (out_dir / f"{mode}_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        all_rows.extend(rows)

    # Output summary for baseline/improved modes
    summary = [{"mode": mode, **summarize_metrics([row for row in all_rows if row.get("prompt_version", mode) == mode])} for mode in modes]
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()