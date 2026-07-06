from __future__ import annotations

import json
import sqlite3
from pathlib import Path

# Le schéma SQL vit à la racine du dépôt (sql/schema.sql), pas à côté de ce fichier.
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"


def connect(db_path: str | Path = "medical_ai_evidence.sqlite") -> sqlite3.Connection:
    """Ouvre une connexion SQLite sur db_path, avec les lignes accessibles comme des dicts."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # permet de faire row["case_id"] plutôt que row[0]
    return conn


def init_db(db_path: str | Path = "medical_ai_evidence.sqlite") -> None:
    """Crée la base (et ses tables) si elle n'existe pas encore, à partir de sql/schema.sql.

    Rejouer le script est sans danger : le schéma utilise CREATE TABLE IF NOT EXISTS.
    """
    conn = connect(db_path)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit(); conn.close()


def insert_run(db_path: str | Path, case_id: str, image_path: str, prediction: dict) -> None:
    """Journalise une prédiction dans la table `runs`, comme preuve d'exécution.

    prediction est la sortie brute du prédicteur (toy ou VLM) ; on la stocke aussi
    telle quelle en JSON pour garder trace de tous les champs (evidence, limitations...),
    en plus des colonnes utiles pour les requêtes/metrics.
    """
    init_db(db_path)  # s'assure que la table existe même si init_db n'a pas été appelé avant
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
            json.dumps(prediction, ensure_ascii=False),  # ensure_ascii=False pour garder les accents lisibles
            prediction.get("predicted_class"),
            float(prediction.get("confidence", 0.0)),
            int(prediction.get("latency_ms", 0)),
        ),
    )
    conn.commit(); conn.close()
