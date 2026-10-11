"""Private aggregate-only Phase 18 Task 2B scenario summaries."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _aggregate(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    grouped = frame.groupby(keys, dropna=False, as_index=False)
    return grouped.agg(order_count=("order_ref", "size"), total_weight_kg=("order_weight_kg", "sum"),
                       total_volume_m3=("order_volume_m3", "sum"),
                       chilled_order_count=("temp_requirement", lambda x: int(x.eq("chilled").sum())),
                       van_only_order_count=("parking_constraint", lambda x: int(x.eq("van_only").sum())),
                       deferred_yesterday_count=("deferred_yesterday", "sum"))


def _distribution(frame: pd.DataFrame, column: str, prefix: str) -> dict[str, float | int]:
    values = pd.to_numeric(frame[column], errors="raise").to_numpy(dtype=float)
    return {"order_count": int(len(values)), f"total_{prefix}": float(values.sum()), f"mean_{prefix}": float(values.mean()),
            f"median_{prefix}": float(np.median(values)), f"max_{prefix}": float(values.max()),
            f"p90_{prefix}": float(np.quantile(values, .90)), f"p95_{prefix}": float(np.quantile(values, .95))}


def build_scenario_summaries(orders: pd.DataFrame) -> dict[str, pd.DataFrame | dict]:
    """Return aggregate summaries only; never expose order-level rows."""
    overall = {"order_count": int(len(orders)), "total_weight_kg": float(orders.order_weight_kg.sum()),
               "total_volume_m3": float(orders.order_volume_m3.sum())}
    brand, district = _aggregate(orders, ["brand"]), _aggregate(orders, ["district"])
    district["brand_count"] = orders.groupby("district").brand.nunique().reindex(district.district).to_numpy()
    brand_district = _aggregate(orders, ["brand", "district"])[["brand", "district", "order_count", "total_weight_kg", "total_volume_m3"]]
    for table in (brand, district):
        if int(table.order_count.sum()) != overall["order_count"] or not np.isclose(table.total_weight_kg.sum(), overall["total_weight_kg"]) or not np.isclose(table.total_volume_m3.sum(), overall["total_volume_m3"]):
            raise ValueError("Phase 18 aggregate reconciliation failed.")
    chilled = orders.loc[orders.temp_requirement.eq("chilled")]
    van = orders.loc[orders.parking_constraint.eq("van_only")]
    deferred = orders.loc[orders.deferred_yesterday.eq(1)]
    chilled_summary = {"chilled_order_count": int(len(chilled)), "chilled_total_weight_kg": float(chilled.order_weight_kg.sum()),
                       "chilled_total_volume_m3": float(chilled.order_volume_m3.sum()),
                       "chilled_share_of_orders": float(len(chilled) / len(orders)),
                       "chilled_share_of_weight": float(chilled.order_weight_kg.sum() / overall["total_weight_kg"]) if overall["total_weight_kg"] else 0.0,
                       "chilled_share_of_volume": float(chilled.order_volume_m3.sum() / overall["total_volume_m3"]) if overall["total_volume_m3"] else 0.0}
    van_summary = {"van_only_order_count": int(len(van)), "van_only_total_weight_kg": float(van.order_weight_kg.sum()),
                   "van_only_total_volume_m3": float(van.order_volume_m3.sum()),
                   "van_only_chilled_order_count": int((van.temp_requirement == "chilled").sum())}
    days = orders.days_since_last_served.to_numpy(dtype=float)
    days_summary = {"count": int(len(days)), "missing": int(pd.isna(days).sum()), "min": float(days.min()), "mean": float(days.mean()),
                    "median": float(np.median(days)), "p75": float(np.quantile(days, .75)), "p90": float(np.quantile(days, .90)),
                    "p95": float(np.quantile(days, .95)), "max": float(days.max())}
    dimensions = {"brand": ["brand"], "district": ["district"], "brand_district": ["brand", "district"],
                  "temp_requirement": ["temp_requirement"], "parking_constraint": ["parking_constraint"]}
    result: dict[str, pd.DataFrame | dict] = {"overall": overall, "demand_by_brand": brand, "demand_by_district": district,
        "demand_by_brand_district": brand_district, "chilled": chilled_summary, "van_only": van_summary,
        "weight": _distribution(orders, "order_weight_kg", "weight_kg"), "volume": _distribution(orders, "order_volume_m3", "volume_m3"),
        "deferred_yesterday": {"count": int(len(deferred)), "share": float(len(deferred) / len(orders)),
            "total_weight_kg": float(deferred.order_weight_kg.sum()), "total_volume_m3": float(deferred.order_volume_m3.sum())},
        "days_since_last_served": days_summary}
    for name, keys in dimensions.items():
        result[f"weight_by_{name}"] = _aggregate(orders, keys)
        result[f"volume_by_{name}"] = _aggregate(orders, keys)
        result[f"deferred_by_{name}"] = _aggregate(deferred, keys)
    for name, keys in {key: dimensions[key] for key in ("brand", "district", "brand_district")}.items():
        result[f"chilled_by_{name}"] = _aggregate(chilled, keys)
        result[f"van_only_by_{name}"] = _aggregate(van, keys)
    result["van_only_by_temp_requirement"] = _aggregate(van, ["temp_requirement"])
    for name, keys in {"brand": ["brand"], "district": ["district"], "deferred_yesterday": ["deferred_yesterday"]}.items():
        result[f"days_by_{name}"] = orders.groupby(keys, as_index=False).days_since_last_served.agg(["count", "min", "mean", "median", "max"]).reset_index()
    return result
