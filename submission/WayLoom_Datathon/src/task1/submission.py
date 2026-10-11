"""Official Task 1 template fill, hard validation, and atomic export."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.task1.inference import (
    Task1InferenceError,
    apply_service_postprocessing,
    assert_delivery_id_integrity,
    assert_probabilities_valid,
)

OFFICIAL_TASK1_COLUMNS = ["delivery_id", "pred_service_min", "pred_late_prob"]


class Task1SubmissionError(ValueError):
    """Raised when the official Task 1 submission contract is violated."""


def official_template_columns(template: pd.DataFrame) -> list[str]:
    cols = list(template.columns)
    if not cols:
        raise Task1SubmissionError("Official Task 1 template has no columns.")
    if cols[0].startswith("Unnamed:") or cols[0] == "":
        raise Task1SubmissionError("Official template appears to contain an accidental index column.")
    return cols


def fill_official_task1_template(template: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
    columns = official_template_columns(template)
    if "delivery_id" not in columns:
        raise Task1SubmissionError("Official template is missing delivery_id.")
    needed = {"pred_service_min", "pred_late_prob"}
    if not needed.issubset(columns):
        raise Task1SubmissionError(f"Official template missing prediction columns: {sorted(needed - set(columns))}")
    pred = predictions[["delivery_id", "pred_service_min", "pred_late_prob"]].copy()
    if pred["delivery_id"].astype("string").duplicated().any():
        raise Task1SubmissionError("Prediction delivery_id values are not unique.")
    lookup = pred.copy()
    lookup["delivery_id"] = lookup["delivery_id"].astype("string")
    lookup = lookup.set_index("delivery_id")
    out = template.copy()
    keys = out["delivery_id"].astype("string")
    out["pred_service_min"] = pd.to_numeric(keys.map(lookup["pred_service_min"]), errors="raise")
    out["pred_late_prob"] = pd.to_numeric(keys.map(lookup["pred_late_prob"]), errors="raise")
    if len(out) != len(template):
        raise Task1SubmissionError("Filling the official template changed the row count.")
    if out[["pred_service_min", "pred_late_prob"]].isna().any().any():
        raise Task1SubmissionError("Official template is missing predictions after fill.")
    return out.loc[:, columns]


def validate_task1_submission(
    submission: pd.DataFrame,
    official_ids: pd.Series,
    *,
    template_columns: list[str] | None = None,
    negative_policy: str = "fail",
) -> dict[str, Any]:
    expected_cols = list(template_columns or OFFICIAL_TASK1_COLUMNS)
    cols = list(submission.columns)
    if any(str(c).startswith("Unnamed:") or str(c) == "" for c in cols):
        raise Task1SubmissionError("Submission contains an accidental CSV index column.")
    extra = [c for c in cols if c not in expected_cols]
    if extra:
        raise Task1SubmissionError(f"Submission contains extra columns: {extra}")
    if cols != expected_cols:
        raise Task1SubmissionError(
            f"Submission columns/order differ from official template. expected={expected_cols} actual={cols}"
        )
    if len(submission) != len(official_ids):
        raise Task1SubmissionError("Submission row count differs from official Task 1 IDs.")
    assert_delivery_id_integrity(official_ids, submission["delivery_id"])
    if submission["delivery_id"].astype("string").duplicated().any():
        raise Task1SubmissionError("Submission delivery_id values are not unique.")
    service = pd.to_numeric(submission["pred_service_min"], errors="coerce").to_numpy(dtype=float)
    late = pd.to_numeric(submission["pred_late_prob"], errors="coerce").to_numpy(dtype=float)
    apply_service_postprocessing(service, negative_policy)
    try:
        assert_probabilities_valid(late)
    except Task1InferenceError as exc:
        raise Task1SubmissionError(str(exc)) from exc
    return {
        "ok": True,
        "n_rows": int(len(submission)),
        "columns": cols,
        "negative_policy": negative_policy,
    }


def export_task1_submission(
    submission: pd.DataFrame,
    path: Path,
    official_ids: pd.Series,
    *,
    template_columns: list[str] | None = None,
    negative_policy: str = "fail",
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    validate_task1_submission(
        submission,
        official_ids,
        template_columns=template_columns,
        negative_policy=negative_policy,
    )
    tmp = path.with_name(path.name + ".tmp")
    submission.to_csv(tmp, index=False)
    readback = pd.read_csv(tmp)
    validate_task1_submission(
        readback,
        official_ids,
        template_columns=template_columns or list(submission.columns),
        negative_policy=negative_policy,
    )
    tmp.replace(path)
    return path


def load_official_task1_ids(test_inputs_path: Path) -> pd.Series:
    frame = pd.read_csv(test_inputs_path)
    if "delivery_id" not in frame.columns:
        raise Task1SubmissionError("Official test inputs missing delivery_id.")
    return frame["delivery_id"]
