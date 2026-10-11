"""Bounded deterministic tuning helpers for Phase 09."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import json
import hashlib
from typing import Any

import pandas as pd


class Task1TuningError(ValueError):
    """Raised when tuning configuration violates bounded-search contracts."""


@dataclass(frozen=True)
class TuningCandidate:
    candidate_id: str
    params: dict[str, Any]


def stable_candidate_id(prefix: str, params: dict[str, Any]) -> str:
    serial = json.dumps(params, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(serial.encode("utf-8")).hexdigest()[:10]
    compact = "_".join(f"{k}{str(v).replace('.', 'p')}" for k, v in sorted(params.items()))
    return f"{prefix}_{compact}_{digest}"


def bounded_grid_candidates(
    *,
    prefix: str,
    grid: dict[str, list[Any]],
    max_candidates: int,
) -> list[TuningCandidate]:
    if max_candidates <= 0:
        raise Task1TuningError("max_candidates must be positive.")
    keys = sorted(grid.keys())
    values = [grid[k] for k in keys]
    candidates: list[TuningCandidate] = []
    for combo in product(*values):
        params = {k: v for k, v in zip(keys, combo)}
        candidates.append(TuningCandidate(stable_candidate_id(prefix, params), params))
    # Keep deterministic order and enforce hard cap.
    candidates = sorted(candidates, key=lambda c: c.candidate_id)
    if len(candidates) > max_candidates:
        candidates = candidates[:max_candidates]
    if len({c.candidate_id for c in candidates}) != len(candidates):
        raise Task1TuningError("Candidate IDs must be unique.")
    return candidates


def assert_bounded_search(candidates: list[TuningCandidate], *, max_candidates: int) -> None:
    if len(candidates) > max_candidates:
        raise Task1TuningError(f"Candidate count exceeds bound: {len(candidates)} > {max_candidates}")


def rank_regression_candidates(rows: pd.DataFrame, *, tie_tolerance: float = 0.0025) -> pd.DataFrame:
    """Rank by MAE then RMSE then MAE stability, preferring simpler config on ties."""
    needed = {"candidate_id", "metric_name", "metric_value", "fold_id"}
    if not needed <= set(rows.columns):
        raise Task1TuningError("Regression ranking requires per-fold metric rows.")
    work = rows.copy(deep=True)
    piv = work.pivot_table(index=["candidate_id"], columns="metric_name", values="metric_value", aggfunc="mean")
    mae_fold = work[work["metric_name"] == "mae"].groupby("candidate_id")["metric_value"]
    piv["mae_std"] = mae_fold.std(ddof=0)
    piv = piv.reset_index()
    if "mae" not in piv.columns or "rmse" not in piv.columns:
        raise Task1TuningError("Regression ranking requires MAE and RMSE metrics.")
    best_mae = float(piv["mae"].min())
    piv["effectively_tied"] = (piv["mae"] - best_mae).abs() / max(best_mae, 1e-12) <= tie_tolerance
    piv["complexity_score"] = piv["candidate_id"].str.count("_")
    return piv.sort_values(
        ["mae", "rmse", "mae_std", "complexity_score", "candidate_id"],
        ascending=[True, True, True, True, True],
        kind="stable",
    ).reset_index(drop=True)


def rank_classifier_candidates(rows: pd.DataFrame, *, tie_tolerance: float = 0.0025) -> pd.DataFrame:
    """Rank by log loss then Brier then log-loss stability."""
    needed = {"candidate_id", "metric_name", "metric_value", "fold_id"}
    if not needed <= set(rows.columns):
        raise Task1TuningError("Classifier ranking requires per-fold metric rows.")
    piv = rows.pivot_table(index=["candidate_id"], columns="metric_name", values="metric_value", aggfunc="mean")
    ll_fold = rows[rows["metric_name"] == "log_loss"].groupby("candidate_id")["metric_value"]
    piv["log_loss_std"] = ll_fold.std(ddof=0)
    piv = piv.reset_index()
    if "log_loss" not in piv.columns or "brier_score" not in piv.columns:
        raise Task1TuningError("Classifier ranking requires log_loss and brier_score.")
    best = float(piv["log_loss"].min())
    piv["effectively_tied"] = (piv["log_loss"] - best).abs() / max(best, 1e-12) <= tie_tolerance
    piv["complexity_score"] = piv["candidate_id"].str.count("_")
    return piv.sort_values(
        ["log_loss", "brier_score", "log_loss_std", "complexity_score", "candidate_id"],
        ascending=[True, True, True, True, True],
        kind="stable",
    ).reset_index(drop=True)

