from pathlib import Path

import pandas as pd
import pytest

from src.task1.submission import Task1SubmissionError, validate_task1_submission
from src.task2a.submission import SubmissionError, validate_submission
from src.uncertainty.reporting import (ReportingError, TASK1_SCHEMA, TASK2A_SCHEMA,
    assert_points_unchanged, guard_official_schema, require_private_path, sha256_file,
    write_csv_atomic)


def task1():
    return pd.DataFrame({"delivery_id": ["d1"], "pred_service_min": [5.0], "pred_late_prob": [0.2]})


def task2a():
    return pd.DataFrame({"row_id": ["r1"], "pred_total_volume_m3": [5.0], "pred_chilled_volume_m3": [0.0]})


def test_exact_official_schemas():
    guard_official_schema(task1(), "task1")
    guard_official_schema(task2a(), "task2a")
    assert list(task1()) == TASK1_SCHEMA and list(task2a()) == TASK2A_SCHEMA


def test_task1_uncertainty_column_rejected_by_official_validator():
    frame = task1().assign(service_lower_90=1.0)
    with pytest.raises(Task1SubmissionError):
        validate_task1_submission(frame, frame.delivery_id)


def test_task2a_uncertainty_column_rejected_by_official_validator():
    frame = task2a().assign(total_upper_90=9.0)
    template = task2a()
    inputs = pd.DataFrame({"row_id": ["r1"], "brand": ["Style"]})
    with pytest.raises(SubmissionError):
        validate_submission(frame, template, inputs, {})


def test_hash_unchanged_and_points_unchanged(tmp_path):
    path = tmp_path / "submission_task1.csv"
    task1().to_csv(path, index=False)
    before = sha256_file(path)
    private = task1()[["delivery_id", "pred_service_min"]].assign(service_lower_90=0.0)
    private.to_csv(tmp_path / "private.csv", index=False)
    assert sha256_file(path) == before
    assert private.pred_service_min.tolist() == task1().pred_service_min.tolist()


def test_point_guard_accepts_equal_numeric_values_across_dtypes_but_rejects_change():
    official = task1()
    official["pred_service_min"] = official.pred_service_min.astype(int)
    private = pd.DataFrame({"delivery_id": ["d1"], "pred_service_min": [5.0]})
    assert_points_unchanged(private, official, task="task1")
    private.loc[0, "pred_service_min"] = 5.0000000001
    with pytest.raises(ReportingError):
        assert_points_unchanged(private, official, task="task1")


def test_private_csv_writer_preserves_float_points_exactly(tmp_path):
    values = ["0.1", "1.2345678901234567", "26.115000000000002"]
    frame = pd.DataFrame({"delivery_id": ["a", "b", "c"], "pred_service_min": values})
    path = tmp_path / "private.csv"
    write_csv_atomic(path, frame)
    restored = pd.read_csv(path, dtype={"delivery_id": "string", "pred_service_min": "string"}, keep_default_na=False)
    assert restored.pred_service_min.tolist() == frame.pred_service_min.tolist()


def test_uncertainty_writer_requires_reports_private(tmp_path):
    root = tmp_path
    allowed = root / "reports" / "private" / "phase27_uncertainty" / "x.csv"
    assert require_private_path(allowed, repository_root=root) == allowed.resolve()
    for forbidden in (root / "outputs" / "submission_task1_uncertainty.csv",
                      root / "outputs" / "submission_task2a_uncertainty.csv"):
        with pytest.raises(ReportingError):
            require_private_path(forbidden, repository_root=root)
