"""Chronology-safe Task 1 validation plan construction (Phase 07)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.task1.historical_features import Task1HistoricalFeatureTransformer


class Task1ValidationError(ValueError):
    """Raised when a temporal split would violate the frozen validation contract."""


@dataclass(frozen=True)
class HoldoutSplit:
    development_index: pd.Index
    holdout_index: pd.Index
    development_dates: tuple[pd.Timestamp, ...]
    holdout_dates: tuple[pd.Timestamp, ...]


@dataclass(frozen=True)
class TemporalFold:
    fold: int
    train_index: pd.Index
    validation_index: pd.Index
    train_dates: tuple[pd.Timestamp, ...]
    validation_dates: tuple[pd.Timestamp, ...]


def load_task1_validation_config(path: Path | str) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def resolve_validation_date(
    frame: pd.DataFrame, *, column: str = "route_date", fallback_column: str = "dispatch_date",
    require_consistency_when_both_present: bool = True,
) -> pd.Series:
    """Resolve canonical route date; `date` is accepted as legacy Phase 04 route-date alias."""
    source = column if column in frame.columns else ("date" if column == "route_date" and "date" in frame.columns else None)
    if source is None:
        if fallback_column not in frame.columns:
            raise Task1ValidationError(f"Missing validation date column: {column}")
        source = fallback_column
    try:
        dates = pd.to_datetime(
            frame[source], format="%Y-%m-%d", errors="raise"
        ).dt.normalize()
    except Exception as exc:
        raise Task1ValidationError("Validation date contains invalid values.") from exc
    if dates.isna().any():
        raise Task1ValidationError("Validation date contains missing values.")
    if require_consistency_when_both_present and source == column and fallback_column in frame.columns:
        fallback = pd.to_datetime(frame[fallback_column], errors="coerce").dt.normalize()
        comparable = fallback.notna()
        # Dispatch date can differ for deferred orders, so it is consistency context, not equality constraint.
        # The canonical route date remains authoritative.
        if comparable.any() and fallback[comparable].isna().any():
            raise Task1ValidationError("dispatch_date contains invalid values when populated.")
    return dates


def sort_task1_history_chronologically(frame: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Sort by canonical date plus stable traceability tie-breakers without mutating input."""
    date_cfg = config["validation_date"]
    dates = resolve_validation_date(
        frame, column=date_cfg["column"], fallback_column=date_cfg["fallback_column"],
        require_consistency_when_both_present=date_cfg.get("require_consistency_when_both_present", True),
    )
    out = frame.copy(deep=True)
    out["_validation_date"] = dates
    tie_breakers = config["ordering"].get("tie_breakers", ["route_id", "seq_in_route", "delivery_id"])
    missing = [c for c in tie_breakers if c not in out.columns]
    if missing:
        raise Task1ValidationError("Missing chronological tie-breaker columns: " + ", ".join(missing))
    return out.sort_values(["_validation_date", *tie_breakers], kind="stable")


def _assert_disjoint(a: set[pd.Timestamp], b: set[pd.Timestamp], label: str) -> None:
    if a & b:
        raise Task1ValidationError(f"Date overlap violates same-date atomicity: {label}")


def make_final_chronological_holdout(sorted_frame: pd.DataFrame, config: dict[str, Any]) -> HoldoutSplit:
    if "_validation_date" not in sorted_frame:
        raise Task1ValidationError("Chronological sort must precede holdout construction.")
    dates = sorted(pd.Timestamp(d) for d in sorted_frame["_validation_date"].unique())
    days = int(config["final_holdout"]["calendar_days"])
    if len(dates) < 2:
        raise Task1ValidationError("Insufficient chronological history for a nonempty holdout.")
    end = dates[-1]
    cutoff = end - pd.Timedelta(days=days - 1)
    holdout_dates = tuple(d for d in dates if d >= cutoff)
    dev_dates = tuple(d for d in dates if d < cutoff)
    if not holdout_dates or not dev_dates:
        raise Task1ValidationError("Insufficient history for configured final holdout.")
    _assert_disjoint(set(dev_dates), set(holdout_dates), "development/holdout")
    dev_index = sorted_frame.index[sorted_frame["_validation_date"].isin(dev_dates)]
    holdout_index = sorted_frame.index[sorted_frame["_validation_date"].isin(holdout_dates)]
    if len(dev_index) == 0 or len(holdout_index) == 0 or set(dev_index) & set(holdout_index):
        raise Task1ValidationError("Development/holdout row integrity failed.")
    if max(dev_dates) >= min(holdout_dates):
        raise Task1ValidationError("Development must be strictly earlier than holdout.")
    return HoldoutSplit(dev_index, holdout_index, dev_dates, holdout_dates)


def make_expanding_date_folds(
    sorted_frame: pd.DataFrame, holdout: HoldoutSplit, config: dict[str, Any]
) -> list[TemporalFold]:
    """Create expanding folds using date blocks strictly inside development."""
    if "_validation_date" not in sorted_frame:
        raise Task1ValidationError("Chronological sort must precede fold construction.")
    cv = config["expanding_cv"]
    dev = sorted_frame.loc[holdout.development_index]
    dev_dates = sorted(pd.Timestamp(d) for d in dev["_validation_date"].unique())
    n_folds, val_days, gap_days, min_train_days = (
        int(cv["n_folds"]), int(cv["validation_calendar_days"]), int(cv.get("gap_calendar_days", 0)),
        int(cv["minimum_training_calendar_days"]),
    )
    latest = dev_dates[-1]
    windows: list[tuple[tuple[pd.Timestamp, ...], tuple[pd.Timestamp, ...]]] = []
    for reverse_fold in range(n_folds):
        val_end = latest - pd.Timedelta(days=reverse_fold * val_days)
        val_start = val_end - pd.Timedelta(days=val_days - 1)
        validation_dates = tuple(d for d in dev_dates if val_start <= d <= val_end)
        train_end = val_start - pd.Timedelta(days=gap_days + 1)
        train_dates = tuple(d for d in dev_dates if d <= train_end)
        if not validation_dates or not train_dates:
            raise Task1ValidationError("Insufficient history for configured expanding folds.")
        span = (max(train_dates) - min(train_dates)).days + 1
        if span < min_train_days:
            raise Task1ValidationError("Minimum training calendar history is not met.")
        _assert_disjoint(set(train_dates), set(validation_dates), "fold train/validation")
        if max(train_dates) >= min(validation_dates):
            raise Task1ValidationError("Fold training dates must be strictly earlier than validation.")
        windows.append((train_dates, validation_dates))
    windows.reverse()
    folds: list[TemporalFold] = []
    hold_dates = set(holdout.holdout_dates)
    last_train_n = -1
    for fold_num, (train_dates, validation_dates) in enumerate(windows, 1):
        _assert_disjoint(set(validation_dates), hold_dates, "validation/final holdout")
        tr_idx = sorted_frame.index[sorted_frame["_validation_date"].isin(train_dates)]
        va_idx = sorted_frame.index[sorted_frame["_validation_date"].isin(validation_dates)]
        if len(tr_idx) <= last_train_n:
            raise Task1ValidationError("Training history must expand monotonically.")
        last_train_n = len(tr_idx)
        folds.append(TemporalFold(fold_num, tr_idx, va_idx, train_dates, validation_dates))
    return folds


def assert_same_date_atomicity(frame: pd.DataFrame, left_index: pd.Index, right_index: pd.Index) -> None:
    left_dates = set(frame.loc[left_index, "_validation_date"])
    right_dates = set(frame.loc[right_index, "_validation_date"])
    _assert_disjoint(left_dates, right_dates, "split sides")


def transform_validation_historical_features(
    train_X: pd.DataFrame, train_service: pd.Series, train_late: pd.Series, validation_X: pd.DataFrame,
    *, date_col: str = "route_date",
) -> pd.DataFrame:
    """Frozen fit-scope protocol: fit train only; transform full validation with no validation y."""
    transformer = Task1HistoricalFeatureTransformer(date_col=date_col)
    transformer.fit(train_X, train_service, train_late)
    return transformer.transform(validation_X)


def build_task1_validation_plan(frame: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    sorted_frame = sort_task1_history_chronologically(frame, config)
    holdout = make_final_chronological_holdout(sorted_frame, config)
    folds = make_expanding_date_folds(sorted_frame, holdout, config)
    for fold in folds:
        assert_same_date_atomicity(sorted_frame, fold.train_index, fold.validation_index)
        assert_same_date_atomicity(sorted_frame, fold.validation_index, holdout.holdout_index)
    return {"sorted_history": sorted_frame, "holdout": holdout, "folds": folds}
