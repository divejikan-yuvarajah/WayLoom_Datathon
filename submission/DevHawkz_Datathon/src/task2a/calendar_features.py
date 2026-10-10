"""Target-week official-calendar predictors, reusing Phase 12 aggregation."""

from __future__ import annotations

import pandas as pd

from src.task2a.eda import CALENDAR_CONTEXT_COLUMNS, EDAValidationError, WEEK_KEYS, build_weekly_calendar_context


TARGET_CALENDAR_COLUMNS = tuple(f"target_{column}" for column in CALENDAR_CONTEXT_COLUMNS if column != "calendar_days")


def build_target_week_calendar_features(calendar: pd.DataFrame) -> pd.DataFrame:
    """Rename the Phase 12 weekly context for a direct-model target week.

    This intentionally calls the one canonical official-calendar aggregation;
    Phase 13 adds no duplicate day-level grouping logic.
    """
    context = build_weekly_calendar_context(calendar)
    return context.rename(columns={column: f"target_{column}" for column in CALENDAR_CONTEXT_COLUMNS}).copy()


def validate_target_calendar_coverage(features: pd.DataFrame) -> pd.DataFrame:
    required = [*WEEK_KEYS, "target_calendar_days", *TARGET_CALENDAR_COLUMNS]
    missing = [column for column in required if column not in features]
    if missing:
        raise EDAValidationError(f"target calendar features missing columns: {', '.join(missing)}")
    if features.duplicated(WEEK_KEYS).any():
        raise EDAValidationError("target calendar features contain duplicate ISO-week keys.")
    return features.copy(deep=True)
