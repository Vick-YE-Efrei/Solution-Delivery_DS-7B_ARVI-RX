from __future__ import annotations

"""Persistence helpers for saving structured prediction runs in SQLite.

This module is responsible for creating the database schema and storing every
run so the evaluation and demo flows remain traceable.
"""

import json
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"

_DB_INIT_DONE: set[str] = set()


def connect(db_path: str | Path = "medical_ai_evidence.sqlite") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path = "medical_ai_evidence.sqlite") -> None:
    key = str(Path(db_path).resolve())
    if key in _DB_INIT_DONE:
        return
    conn = connect(db_path)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit(); conn.close()
    _DB_INIT_DONE.add(key)


def insert_run(db_path: str | Path, case_id: str, image_path: str, prediction: dict) -> None:
    init_db(db_path)
    conn = connect(db_path)
    conn.execute(
        """
        INSERT INTO runs(case_id, image_path, model_name, prompt_version, prediction_json, predicted_class, confidence, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case_id,
            image_path,
            prediction.get("model_name"),
            prediction.get("prompt_version"),
            json.dumps(prediction, ensure_ascii=False),
            prediction.get("predicted_class"),
            float(prediction.get("confidence", 0.0)),
            int(prediction.get("latency_ms", 0)),
        ),
    )
    conn.commit(); conn.close()
