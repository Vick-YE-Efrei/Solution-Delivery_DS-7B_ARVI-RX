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


def read_cases(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def run(mode: str, db_path: Path):
    cases = read_cases(ROOT / "data" / "synthetic_cases.csv")
    rows = []
    init_db(db_path)

    if mode in ("toy", "baseline"):
        def predict_fn(img):
            return inference.toy_predict(img, mode="baseline")
    elif mode == "improved":
        def predict_fn(img):
            return inference.toy_predict(img, mode="improved")

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["toy", "baseline", "improved"], default="toy")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "eval" / "outputs")
    parser.add_argument("--db-path", type=Path, default=ROOT / "medical_ai_evidence.sqlite")
    args = parser.parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Le mode "toy" lance baseline + improved avec toy_predict
    # (comportement attendu par le smoke test)
    if args.mode == "toy":
        modes = ["baseline", "improved"]
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