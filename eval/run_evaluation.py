from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import src.inference as inference
from src.guardrails import apply_safety_guardrails, validate_prediction
from src.metrics import summarize_metrics
from src.database import insert_run, init_db


def read_cases(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def run(mode: str, db_path: Path) -> tuple[list[dict], dict]:
    cases = read_cases(ROOT / "data" / "chest_xray" / "chest_xray_train.csv")
    rows = []
    init_db(db_path)

    print("DEBUG mode:", mode)

    # if mode == "toy":
    #     def predict_fn(img):
    #         return inference.toy_predict(img, mode="baseline")
    # else:
    #     prompt_path = ROOT / "prompts" / "improved_prompt.txt"
    #     medgemma_prompt = prompt_path.read_text(encoding="utf-8")
    #     def predict_fn(img):
    #         return inference.vlm_predict_medgemma(img, medgemma_prompt)

    if mode == "toy":
        def predict_fn(img):
            return inference.toy_predict(img, mode="baseline")
    elif mode == "baseline":
        prompt_path = ROOT / "prompts" / "baseline_prompt.txt"
        medgemma_prompt = prompt_path.read_text(encoding="utf-8")
        def predict_fn(img):
            return inference.vlm_predict_medgemma(img, medgemma_prompt)
    elif mode == "improved":
        prompt_path = ROOT / "prompts" / "improved_prompt.txt"
        medgemma_prompt = prompt_path.read_text(encoding="utf-8")
        def predict_fn(img):
            return inference.vlm_predict_medgemma(img, medgemma_prompt)

    for case in cases:
        image_path = ROOT / case["image_path"]
        pred = predict_fn(image_path)
        pred = apply_safety_guardrails(pred)
        valid, errors = validate_prediction(pred)
        row = {
            "case_id":          case["case_id"],
            "label":            case["label"],
            "predicted_class":  pred["predicted_class"],
            "confidence":       pred["confidence"],
            "json_valid":       valid,
            "warning":          pred.get("warning", ""),
            "latency_ms":       pred.get("latency_ms", 0),
            "guardrail_errors": ";".join(errors),
        }
        rows.append(row)
        insert_run(db_path, case["case_id"], str(image_path), pred)

    metrics = summarize_metrics(rows)
    return rows, metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["toy", "baseline", "improved"], default="toy")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "eval" / "outputs")
    parser.add_argument("--db-path", type=Path, default=ROOT / "medical_ai_evidence.sqlite")
    args = parser.parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.mode == "toy":
        modes = ["toy"]
    else:
        modes = [args.mode]
    summary = []
    for mode in modes:
        rows, metrics = run(mode, args.db_path)
        write_csv(out_dir / f"{mode}_predictions.csv", rows)
        (out_dir / f"{mode}_metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8"
        )
        summary.append({"mode": mode, **metrics})
    write_csv(out_dir / "before_after_summary.csv", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()