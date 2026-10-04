"""Synthetic Phase 17 official-template mapping and export tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.task2a.submission import SubmissionError, map_predictions_to_template, validate_submission, write_submission_atomic
from tests.test_task2a_final_inference import _config


def _inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    template = pd.DataFrame({"row_id": ["r2", "r1", "r3"], "pred_total_volume_m3": 0.0,
                             "pred_chilled_volume_m3": 0.0})
    grid = pd.DataFrame({"row_id": ["r2", "r1", "r3"], "brand": ["Fresh", "Style", "Tech"]})
    predictions = pd.DataFrame({"row_id": ["r3", "r2", "r1"], "pred_total_volume_m3": [3.0, 2.0, 1.0],
                                "pred_chilled_volume_m3": [0.0, 1.0, 0.0]})
    return template, grid, predictions


def test_mapping_is_by_row_id_and_atomic_export_round_trips(tmp_path: Path) -> None:
    template, grid, predictions = _inputs()
    submission = map_predictions_to_template(template, predictions)
    assert submission.row_id.tolist() == template.row_id.tolist()
    report = write_submission_atomic(tmp_path / "submission_task2a.csv", submission, template, grid, _config())
    assert report["status"] == "PASS"
    assert (tmp_path / "submission_task2a.csv").is_file()


def test_template_and_prediction_integrity_fail_closed() -> None:
    template, grid, predictions = _inputs()
    with pytest.raises(SubmissionError, match="row_id set"):
        map_predictions_to_template(template, predictions.iloc[:-1])
    broken = map_predictions_to_template(template, predictions)
    broken.loc[0, "pred_chilled_volume_m3"] = 4.0
    with pytest.raises(SubmissionError, match="exceeds"):
        validate_submission(broken, template, grid, _config())
    broken = map_predictions_to_template(template, predictions)
    broken.loc[1, "pred_chilled_volume_m3"] = 1.0
    with pytest.raises(SubmissionError, match="Style"):
        validate_submission(broken, template, grid, _config())
