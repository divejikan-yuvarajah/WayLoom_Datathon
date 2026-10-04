"""Exact Task 2A submission mapping, validation, and atomic export."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class SubmissionError(ValueError):
    """The official Task 2A output contract was violated."""


REQUIRED_PREDICTIONS = ("pred_total_volume_m3", "pred_chilled_volume_m3")


def map_predictions_to_template(template: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
    if "row_id" not in template or "row_id" not in predictions:
        raise SubmissionError("Official template and predictions must contain row_id.")
    if template.row_id.isna().any() or template.row_id.astype("string").str.strip().eq("").any() or template.row_id.duplicated().any():
        raise SubmissionError("Official template row_id must be nonblank and unique.")
    required = {"row_id", *REQUIRED_PREDICTIONS}
    if required.difference(predictions.columns):
        raise SubmissionError("Prediction mapping lacks required prediction columns.")
    if predictions.row_id.isna().any() or predictions.row_id.duplicated().any():
        raise SubmissionError("Predictions have missing or duplicate row_id values.")
    if set(predictions.row_id.astype(str)) != set(template.row_id.astype(str)):
        raise SubmissionError("Prediction row_id set differs from the official template.")
    mapped = template[["row_id"]].merge(predictions[list(required)], on="row_id", how="left", validate="one_to_one")
    if mapped[list(REQUIRED_PREDICTIONS)].isna().any().any():
        raise SubmissionError("A template row is missing its prediction.")
    for column in REQUIRED_PREDICTIONS:
        mapped[column] = pd.to_numeric(mapped[column], errors="raise")
    result = mapped.loc[:, list(template.columns)].copy()
    if list(result.columns) != list(template.columns):
        raise SubmissionError("Submission column order differs from the official template.")
    return result


def validate_submission(submission: pd.DataFrame, template: pd.DataFrame, test_inputs: pd.DataFrame,
                        final_config: dict[str, Any]) -> dict[str, Any]:
    if list(submission.columns) != list(template.columns):
        raise SubmissionError("Submission columns must exactly equal official template columns and order.")
    if any(column.startswith("Unnamed:") for column in submission.columns):
        raise SubmissionError("Submission contains an accidental CSV index column.")
    if len(submission) != len(template) or submission.row_id.astype(str).tolist() != template.row_id.astype(str).tolist():
        raise SubmissionError("Submission row count or official template row_id order changed.")
    if submission.row_id.isna().any() or submission.row_id.duplicated().any():
        raise SubmissionError("Submission row_id is missing or duplicated.")
    if set(test_inputs.row_id.astype(str)) != set(submission.row_id.astype(str)):
        raise SubmissionError("Submission row_id values do not equal Task 2A test inputs.")
    values = submission[list(REQUIRED_PREDICTIONS)].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise SubmissionError("Submission predictions contain NaN or Inf.")
    if (values < 0).any():
        raise SubmissionError("Submission predictions must be nonnegative.")
    if (submission.pred_chilled_volume_m3 > submission.pred_total_volume_m3).any():
        raise SubmissionError("Submission chilled prediction exceeds total prediction.")
    brands = test_inputs[["row_id", "brand"]].copy()
    merged = submission.merge(brands, on="row_id", how="left", validate="one_to_one")
    if merged.brand.isna().any() or not merged.loc[merged.brand.isin(["Style", "Tech"]), "pred_chilled_volume_m3"].eq(0.0).all():
        raise SubmissionError("Style and Tech chilled predictions must be exactly zero.")
    return {"status": "PASS", "row_count": int(len(submission)),
            "style_chilled_zero": True, "tech_chilled_zero": True,
            "nonnegative": True, "chilled_le_total": True}


def write_submission_atomic(path: Path, submission: pd.DataFrame, template: pd.DataFrame,
                            test_inputs: pd.DataFrame, final_config: dict[str, Any]) -> dict[str, Any]:
    path = Path(path)
    if path.name != "submission_task2a.csv":
        raise SubmissionError("Final Task 2A output filename must be submission_task2a.csv.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.csv")
    submission.to_csv(temporary, index=False)
    try:
        read_back = pd.read_csv(temporary)
        report = validate_submission(read_back, template, test_inputs, final_config)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return report
