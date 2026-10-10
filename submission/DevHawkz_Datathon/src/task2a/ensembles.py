"""Fixed, key-aligned Phase 16 forecast ensembles."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.task2a.advanced_models import KEYS


class EnsembleError(ValueError):
    """An ensemble component is incomplete or misaligned."""


def blend_equal_weight(left: pd.DataFrame, right: pd.DataFrame, candidate_id: str) -> pd.DataFrame:
    """Blend two complete prediction sets by exact frozen validation keys."""
    required = [*KEYS, "target_name", "y_true", "total_y_true", "y_pred", "phase14_backtest_signature"]
    if any(name not in frame for frame in (left, right) for name in required):
        raise EnsembleError("Ensemble component lacks required prediction fields.")
    join_keys = [*KEYS, "target_name"]
    if left.empty or right.empty or left.duplicated(join_keys).any() or right.duplicated(join_keys).any():
        raise EnsembleError("Ensemble component is empty or has duplicate prediction keys.")
    a, b = left[required].copy(), right[required].copy()
    for frame in (a, b):
        for column in ("origin_week_start_date", "target_week_start_date"):
            frame[column] = pd.to_datetime(frame[column], errors="raise").dt.normalize()
    joined = a.merge(b, on=join_keys, how="outer", suffixes=("_left", "_right"),
                     indicator=True, validate="one_to_one")
    if len(joined) != len(a) or len(joined) != len(b) or not joined._merge.eq("both").all():
        raise EnsembleError("Ensemble components do not cover identical frozen validation keys.")
    for column in ("y_true", "total_y_true"):
        if not np.isclose(joined[f"{column}_left"], joined[f"{column}_right"]).all():
            raise EnsembleError("Ensemble components disagree on validation labels.")
    if not joined.phase14_backtest_signature_left.eq(joined.phase14_backtest_signature_right).all():
        raise EnsembleError("Ensemble components have different Phase 14 signatures.")
    values = joined[["y_pred_left", "y_pred_right"]].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise EnsembleError("Ensemble component has nonfinite predictions.")
    result = joined[join_keys].copy()
    result["candidate_id"] = candidate_id
    result["y_true"] = joined.y_true_left.to_numpy(dtype=float)
    result["total_y_true"] = joined.total_y_true_left.to_numpy(dtype=float)
    result["y_pred"] = 0.5 * values[:, 0] + 0.5 * values[:, 1]
    result["phase14_backtest_signature"] = joined.phase14_backtest_signature_left
    return result.sort_values(join_keys, kind="stable").reset_index(drop=True)
