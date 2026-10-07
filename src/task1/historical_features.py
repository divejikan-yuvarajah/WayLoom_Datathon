from __future__ import annotations

from dataclasses import dataclass
import heapq
from typing import Any

import numpy as np
import pandas as pd


class Task1HistoricalFeatureError(ValueError):
    """Raised when historical target-stat features violate chronology safety."""


@dataclass(frozen=True)
class HistoricalFeatureSpec:
    feature_name: str
    key_columns: tuple[str, ...]
    target_kind: str  # "service_median" | "late_rate"


HISTORICAL_FEATURE_SPECS: tuple[HistoricalFeatureSpec, ...] = (
    HistoricalFeatureSpec("outlet_prior_service_median", ("outlet_id",), "service_median"),
    HistoricalFeatureSpec("outlet_prior_late_rate", ("outlet_id",), "late_rate"),
    HistoricalFeatureSpec(
        "brand_dock_prior_service_median",
        ("brand", "dock_type"),
        "service_median",
    ),
    HistoricalFeatureSpec(
        "brand_dock_prior_late_rate",
        ("brand", "dock_type"),
        "late_rate",
    ),
    HistoricalFeatureSpec("brand_prior_service_median", ("brand",), "service_median"),
    HistoricalFeatureSpec("brand_prior_late_rate", ("brand",), "late_rate"),
)


def _key_tuple(row: pd.Series, cols: tuple[str, ...]) -> tuple[Any, ...]:
    return tuple(row[c] for c in cols)


def _safe_late_rate(sum_late: float, count: int, fallback: float) -> float:
    if count <= 0:
        return float(fallback)
    return float(sum_late / count)


class _RunningMedian:
    """Maintain an exact median without repeatedly scanning all prior rows."""

    __slots__ = ("_lower", "_upper")

    def __init__(self) -> None:
        self._lower: list[float] = []
        self._upper: list[float] = []

    def add(self, value: float) -> None:
        if not self._lower or value <= -self._lower[0]:
            heapq.heappush(self._lower, -value)
        else:
            heapq.heappush(self._upper, value)

        if len(self._lower) > len(self._upper) + 1:
            heapq.heappush(self._upper, -heapq.heappop(self._lower))
        elif len(self._upper) > len(self._lower):
            heapq.heappush(self._lower, -heapq.heappop(self._upper))

    def median(self) -> float:
        if not self._lower:
            return np.nan
        if len(self._lower) == len(self._upper):
            return float((-self._lower[0] + self._upper[0]) / 2.0)
        return float(-self._lower[0])


_MISSING_KEY = object()


def _history_key(row: pd.Series, cols: tuple[str, ...]) -> tuple[Any, ...]:
    """Return a stable dictionary key, including for missing category values."""
    return tuple(_MISSING_KEY if pd.isna(row[c]) else row[c] for c in cols)


class Task1HistoricalFeatureTransformer:
    """Leakage-safe historical target aggregates with explicit fit/transform scope."""

    def __init__(self, *, date_col: str = "date") -> None:
        self.date_col = date_col
        self._fitted = False
        self.global_service_prior: float = 0.0
        self.global_late_prior: float = 0.0
        self._service_medians: dict[tuple[tuple[str, ...], tuple[Any, ...]], float] = {}
        self._late_rates: dict[tuple[tuple[str, ...], tuple[Any, ...]], float] = {}

    def fit(
        self,
        X: pd.DataFrame,
        y_service: pd.Series,
        y_late: pd.Series,
    ) -> "Task1HistoricalFeatureTransformer":
        required = {self.date_col, "outlet_id", "brand", "dock_type"}
        missing = sorted(required - set(X.columns))
        if missing:
            raise Task1HistoricalFeatureError(
                "Missing required columns for historical fit: " + ", ".join(missing)
            )
        if len(X) != len(y_service) or len(X) != len(y_late):
            raise Task1HistoricalFeatureError("X/y lengths do not match for historical fit.")

        service = pd.to_numeric(y_service, errors="coerce")
        late = pd.to_numeric(y_late, errors="coerce")
        if service.isna().any() or late.isna().any():
            raise Task1HistoricalFeatureError("Historical fit targets contain missing/non-numeric values.")

        self.global_service_prior = float(service.median())
        self.global_late_prior = float(late.mean())

        work = X.copy(deep=True)
        work["_service"] = service.to_numpy(dtype=float)
        work["_late"] = late.to_numpy(dtype=float)

        self._service_medians = {}
        self._late_rates = {}
        for spec in HISTORICAL_FEATURE_SPECS:
            grp = work.groupby(list(spec.key_columns), dropna=False)
            if spec.target_kind == "service_median":
                series = grp["_service"].median()
                for k, v in series.items():
                    kt = k if isinstance(k, tuple) else (k,)
                    self._service_medians[(spec.key_columns, tuple(kt))] = float(v)
            else:
                series = grp["_late"].mean()
                for k, v in series.items():
                    kt = k if isinstance(k, tuple) else (k,)
                    self._late_rates[(spec.key_columns, tuple(kt))] = float(v)

        self._fitted = True
        return self

    def _fallback_service(self, row: pd.Series) -> float:
        for keys in (("outlet_id",), ("brand", "dock_type"), ("brand",)):
            val = self._service_medians.get((keys, _key_tuple(row, keys)))
            if val is not None:
                return float(val)
        return float(self.global_service_prior)

    def _fallback_late(self, row: pd.Series) -> float:
        for keys in (("outlet_id",), ("brand", "dock_type"), ("brand",)):
            val = self._late_rates.get((keys, _key_tuple(row, keys)))
            if val is not None:
                return float(val)
        return float(self.global_late_prior)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if not self._fitted:
            raise Task1HistoricalFeatureError("Historical transformer must be fit before transform.")
        required = {"outlet_id", "brand", "dock_type"}
        missing = sorted(required - set(X.columns))
        if missing:
            raise Task1HistoricalFeatureError(
                "Missing required columns for historical transform: " + ", ".join(missing)
            )

        out = pd.DataFrame(index=X.index)
        out["outlet_prior_service_median"] = X.apply(self._fallback_service, axis=1).astype(float)
        out["brand_dock_prior_service_median"] = X.apply(
            lambda r: self._service_medians.get(
                (("brand", "dock_type"), _key_tuple(r, ("brand", "dock_type"))),
                self._fallback_service(r),
            ),
            axis=1,
        ).astype(float)
        out["brand_prior_service_median"] = X.apply(
            lambda r: self._service_medians.get(
                (("brand",), _key_tuple(r, ("brand",))),
                self._fallback_service(r),
            ),
            axis=1,
        ).astype(float)

        out["outlet_prior_late_rate"] = X.apply(self._fallback_late, axis=1).astype(float)
        out["brand_dock_prior_late_rate"] = X.apply(
            lambda r: self._late_rates.get(
                (("brand", "dock_type"), _key_tuple(r, ("brand", "dock_type"))),
                self._fallback_late(r),
            ),
            axis=1,
        ).astype(float)
        out["brand_prior_late_rate"] = X.apply(
            lambda r: self._late_rates.get(
                (("brand",), _key_tuple(r, ("brand",))),
                self._fallback_late(r),
            ),
            axis=1,
        ).astype(float)
        return out

    def fit_transform_training_chronological(
        self,
        X: pd.DataFrame,
        y_service: pd.Series,
        y_late: pd.Series,
    ) -> pd.DataFrame:
        """Create row-wise historical features using strictly earlier dates only."""
        required = {self.date_col, "outlet_id", "brand", "dock_type"}
        missing = sorted(required - set(X.columns))
        if missing:
            raise Task1HistoricalFeatureError(
                "Missing required columns for chronological historical features: "
                + ", ".join(missing)
            )
        if len(X) != len(y_service) or len(X) != len(y_late):
            raise Task1HistoricalFeatureError("X/y lengths do not match for chronological transform.")

        work = X.copy(deep=True)
        work["_service"] = pd.to_numeric(y_service, errors="coerce")
        work["_late"] = pd.to_numeric(y_late, errors="coerce")
        if work["_service"].isna().any() or work["_late"].isna().any():
            raise Task1HistoricalFeatureError("Historical chronological targets are invalid.")

        work[self.date_col] = pd.to_datetime(work[self.date_col], errors="raise")
        prior_service_values: dict[
            tuple[tuple[str, ...], tuple[Any, ...]], _RunningMedian
        ] = {}
        prior_late_sum_count: dict[tuple[tuple[str, ...], tuple[Any, ...]], tuple[float, int]] = {}
        prior_global_service = _RunningMedian()
        prior_global_late_sum = 0.0
        prior_global_count = 0

        feature_names = [spec.feature_name for spec in HISTORICAL_FEATURE_SPECS]
        feature_positions = {name: pos for pos, name in enumerate(feature_names)}
        values = np.full((len(work), len(feature_names)), np.nan, dtype=float)
        work = work.assign(_history_position=np.arange(len(work), dtype=int))

        for _, date_grp in work.groupby(self.date_col, sort=True):
            # Compute today's features from strictly earlier history (no same-date leakage).
            for _, row in date_grp.iterrows():
                position = int(row["_history_position"])
                # A cold-start date has no historical target information. Preserve
                # missing values rather than borrowing a full-period/global future
                # target statistic. Later model-phase imputation is fit-scoped.
                service_fb = (
                    prior_global_service.median()
                    if prior_global_count
                    else np.nan
                )
                for keys in (("outlet_id",), ("brand", "dock_type"), ("brand",)):
                    state = prior_service_values.get((keys, _history_key(row, keys)))
                    if state is not None:
                        service_fb = state.median()
                        break

                late_fb = (
                    float(prior_global_late_sum / prior_global_count)
                    if prior_global_count
                    else np.nan
                )
                for keys in (("outlet_id",), ("brand", "dock_type"), ("brand",)):
                    lc = prior_late_sum_count.get((keys, _history_key(row, keys)))
                    if lc is not None and lc[1] > 0:
                        late_fb = float(lc[0] / lc[1])
                        break

                outlet_service = prior_service_values.get(
                    (("outlet_id",), _history_key(row, ("outlet_id",)))
                )
                brand_dock_service = prior_service_values.get(
                    (("brand", "dock_type"), _history_key(row, ("brand", "dock_type")))
                )
                brand_service = prior_service_values.get(
                    (("brand",), _history_key(row, ("brand",)))
                )
                values[position, feature_positions["outlet_prior_service_median"]] = (
                    outlet_service.median() if outlet_service is not None else service_fb
                )
                values[position, feature_positions["brand_dock_prior_service_median"]] = (
                    brand_dock_service.median()
                    if brand_dock_service is not None
                    else service_fb
                )
                values[position, feature_positions["brand_prior_service_median"]] = (
                    brand_service.median() if brand_service is not None else service_fb
                )

                outlet_late = prior_late_sum_count.get(
                    (("outlet_id",), _history_key(row, ("outlet_id",))), (0.0, 0)
                )
                bd_late = prior_late_sum_count.get(
                    (("brand", "dock_type"), _history_key(row, ("brand", "dock_type"))),
                    (0.0, 0),
                )
                b_late = prior_late_sum_count.get(
                    (("brand",), _history_key(row, ("brand",))), (0.0, 0)
                )
                values[position, feature_positions["outlet_prior_late_rate"]] = float(
                    _safe_late_rate(outlet_late[0], outlet_late[1], late_fb)
                )
                values[position, feature_positions["brand_dock_prior_late_rate"]] = float(
                    _safe_late_rate(bd_late[0], bd_late[1], late_fb)
                )
                values[position, feature_positions["brand_prior_late_rate"]] = float(
                    _safe_late_rate(b_late[0], b_late[1], late_fb)
                )

            # Update history after computing all rows on this date.
            for _, row in date_grp.iterrows():
                prior_global_service.add(float(row["_service"]))
                prior_global_late_sum += float(row["_late"])
                prior_global_count += 1
                for keys in (("outlet_id",), ("brand", "dock_type"), ("brand",)):
                    k = (keys, _history_key(row, keys))
                    prior_service_values.setdefault(k, _RunningMedian()).add(
                        float(row["_service"])
                    )
                    s, c = prior_late_sum_count.get(k, (0.0, 0))
                    prior_late_sum_count[k] = (s + float(row["_late"]), c + 1)

        return pd.DataFrame(values, index=X.index, columns=feature_names)
