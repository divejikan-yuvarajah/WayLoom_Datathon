from __future__ import annotations

from dataclasses import dataclass
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


def _safe_service_median(values: list[float], fallback: float) -> float:
    if not values:
        return float(fallback)
    return float(np.median(values))


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
        global_service_prior = float(work["_service"].median())
        global_late_prior = float(work["_late"].mean())

        prior_service_values: dict[tuple[tuple[str, ...], tuple[Any, ...]], list[float]] = {}
        prior_late_sum_count: dict[tuple[tuple[str, ...], tuple[Any, ...]], tuple[float, int]] = {}

        out = pd.DataFrame(index=X.index)
        for spec in HISTORICAL_FEATURE_SPECS:
            out[spec.feature_name] = np.nan

        for date_val, date_grp in work.groupby(self.date_col, sort=True):
            # Compute today's features from strictly earlier history (no same-date leakage).
            for idx, row in date_grp.iterrows():
                service_fb = global_service_prior
                for keys in (("outlet_id",), ("brand", "dock_type"), ("brand",)):
                    vals = prior_service_values.get((keys, _key_tuple(row, keys)))
                    if vals:
                        service_fb = float(np.median(vals))
                        break

                late_fb = global_late_prior
                for keys in (("outlet_id",), ("brand", "dock_type"), ("brand",)):
                    lc = prior_late_sum_count.get((keys, _key_tuple(row, keys)))
                    if lc is not None and lc[1] > 0:
                        late_fb = float(lc[0] / lc[1])
                        break

                out.at[idx, "outlet_prior_service_median"] = float(
                    _safe_service_median(
                        prior_service_values.get((("outlet_id",), _key_tuple(row, ("outlet_id",))), []),
                        service_fb,
                    )
                )
                out.at[idx, "brand_dock_prior_service_median"] = float(
                    _safe_service_median(
                        prior_service_values.get(
                            (("brand", "dock_type"), _key_tuple(row, ("brand", "dock_type"))),
                            [],
                        ),
                        service_fb,
                    )
                )
                out.at[idx, "brand_prior_service_median"] = float(
                    _safe_service_median(
                        prior_service_values.get((("brand",), _key_tuple(row, ("brand",))), []),
                        service_fb,
                    )
                )

                outlet_late = prior_late_sum_count.get(
                    (("outlet_id",), _key_tuple(row, ("outlet_id",))), (0.0, 0)
                )
                bd_late = prior_late_sum_count.get(
                    (("brand", "dock_type"), _key_tuple(row, ("brand", "dock_type"))),
                    (0.0, 0),
                )
                b_late = prior_late_sum_count.get(
                    (("brand",), _key_tuple(row, ("brand",))), (0.0, 0)
                )
                out.at[idx, "outlet_prior_late_rate"] = float(
                    _safe_late_rate(outlet_late[0], outlet_late[1], late_fb)
                )
                out.at[idx, "brand_dock_prior_late_rate"] = float(
                    _safe_late_rate(bd_late[0], bd_late[1], late_fb)
                )
                out.at[idx, "brand_prior_late_rate"] = float(
                    _safe_late_rate(b_late[0], b_late[1], late_fb)
                )

            # Update history after computing all rows on this date.
            for _, row in date_grp.iterrows():
                for keys in (("outlet_id",), ("brand", "dock_type"), ("brand",)):
                    k = (keys, _key_tuple(row, keys))
                    prior_service_values.setdefault(k, []).append(float(row["_service"]))
                    s, c = prior_late_sum_count.get(k, (0.0, 0))
                    prior_late_sum_count[k] = (s + float(row["_late"]), c + 1)

        return out.astype(float)
