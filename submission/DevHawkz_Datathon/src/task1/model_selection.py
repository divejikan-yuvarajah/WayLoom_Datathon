"""Deterministic development-only selection rules for Phase 09."""

from __future__ import annotations

from typing import Any

import pandas as pd


class Task1ModelSelectionError(ValueError):
    """Raised when selection inputs violate frozen eligibility rules."""


def assert_same_fold_contract(rows: pd.DataFrame) -> None:
    needed = {"target", "candidate_id", "fold_id", "train_start_date", "train_end_date", "validation_start_date", "validation_end_date"}
    if not needed <= set(rows.columns):
        raise Task1ModelSelectionError("Missing fold contract columns.")
    for target, grp in rows.groupby("target"):
        baseline = None
        for cid, cgrp in grp.groupby("candidate_id"):
            sig = tuple(
                cgrp.sort_values("fold_id")[["fold_id", "train_start_date", "train_end_date", "validation_start_date", "validation_end_date"]]
                .itertuples(index=False, name=None)
            )
            if baseline is None:
                baseline = sig
            elif sig != baseline:
                raise Task1ModelSelectionError(f"Candidate {cid} violates same-fold contract for target={target}.")


def eligible_candidates(summary: pd.DataFrame, *, target: str) -> pd.DataFrame:
    needed = {"candidate_id", "target", "fold_count", "required_fold_count", "status"}
    if not needed <= set(summary.columns):
        raise Task1ModelSelectionError("Candidate summary missing eligibility fields.")
    work = summary[(summary["target"] == target) & (summary["status"] == "ok")].copy()
    work = work[work["fold_count"] == work["required_fold_count"]]
    if work.empty:
        raise Task1ModelSelectionError(f"No eligible candidates for target={target}.")
    return work


def select_regression_candidate(summary: pd.DataFrame) -> dict[str, Any]:
    work = eligible_candidates(summary, target="service")
    needed = {"mae", "rmse", "mae_std", "p90_absolute_error", "complexity_score"}
    if not needed <= set(work.columns):
        raise Task1ModelSelectionError("Regression summary missing required metric columns.")
    best = work.sort_values(
        ["mae", "rmse", "mae_std", "p90_absolute_error", "complexity_score", "candidate_id"],
        ascending=[True, True, True, True, True, True],
        kind="stable",
    ).iloc[0]
    return {"candidate_id": str(best["candidate_id"]), "target": "service", "selection_metric": "mae"}


def select_lateness_candidate(summary: pd.DataFrame) -> dict[str, Any]:
    work = eligible_candidates(summary, target="late")
    needed = {"log_loss", "brier_score", "log_loss_std", "complexity_score", "calibration_method", "calibration_protocol"}
    if not needed <= set(work.columns):
        raise Task1ModelSelectionError("Lateness summary missing required metric columns.")
    best = work.sort_values(
        ["log_loss", "brier_score", "log_loss_std", "complexity_score", "candidate_id"],
        ascending=[True, True, True, True, True],
        kind="stable",
    ).iloc[0]
    return {
        "candidate_id": str(best["candidate_id"]),
        "target": "late",
        "selection_metric": "log_loss",
        "calibration_method": str(best["calibration_method"]),
        "calibration_protocol": str(best["calibration_protocol"]),
    }

