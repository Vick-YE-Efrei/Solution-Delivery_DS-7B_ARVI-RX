from __future__ import annotations

"""Regression tests for the end-to-end pipeline.

These checks ensure that a run produces a structured JSON artifact and persists
its result to the SQLite database.
"""

import json
from pathlib import Path

from src.pipeline import run_pipeline


def test_run_pipeline_persists_structured_output(tmp_path: Path) -> None:
    image_path = Path("data/sample_images/CXR_SYN_002_suspected_opacity.png")
    out_dir = tmp_path / "runs"
    db_path = tmp_path / "medical_ai_evidence.sqlite"

    result = run_pipeline(
        image_path=image_path,
        mode="baseline",
        prompt_mode="baseline",
        output_dir=out_dir,
        db_path=db_path,
    )

    assert result["predicted_class"] == "suspected_opacity"
    assert result["warning"]
    assert result["pipeline_status"] == "completed"
    assert result["run_id"]
    assert (out_dir / f"{result['run_id']}.json").exists()
    assert db_path.exists()

    persisted = json.loads((out_dir / f"{result['run_id']}.json").read_text(encoding="utf-8"))
    assert persisted["predicted_class"] == result["predicted_class"]
    assert persisted["metadata"]["prompt_mode"] == "baseline"
