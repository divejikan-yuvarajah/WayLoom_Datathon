"""Direction-aware policy and allocation deltas for Phase 26 diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from src.task2b.priority import OBJECTIVE_LEVELS


class CounterfactualDeltaError(ValueError):
    """A counterfactual cannot be compared safely with the frozen solution."""


TIER_LABELS = {
    "served_order_count": "LEVEL 1 - total coverage",
    "served_previous_deferred_count": "LEVEL 2 - previously-deferred orders served",
    "served_waiting_days_sum": "LEVEL 3 - waiting-days served",
    "served_low_flexibility_count": "LEVEL 4 - low-flexibility orders served",
    "served_fresh_chilled_count": "LEVEL 5 - Fresh chilled orders served",
    "served_fresh_count": "LEVEL 6 - Fresh orders served",
    "avoidable_reefer_van_assignment_count": "LEVEL 7A - reefer-van stewardship",
    "avoidable_reefer_assignment_count": "LEVEL 7B - reefer stewardship",
    "avoidable_van_assignment_count": "LEVEL 7C - van stewardship",
}


def canonical_objective_vector(values: Mapping[str, int]) -> dict[str, int]:
    """Restore Phase 21 order after JSON serializers reorder mapping keys."""
    if not isinstance(values, Mapping) or set(values) != set(OBJECTIVE_LEVELS):
        raise CounterfactualDeltaError("Objective vector keys differ from Phase 21.")
    return {name: int(values[name]) for name in OBJECTIVE_LEVELS}


def compare_objective_vectors(forced: Mapping[str, int], baseline: Mapping[str, int]) -> str:
    """Return WORSE/EQUAL/BETTER using the mixed MAX/MIN frozen hierarchy."""
    if tuple(forced) != OBJECTIVE_LEVELS or tuple(baseline) != OBJECTIVE_LEVELS:
        raise CounterfactualDeltaError("Objective vector keys/order differ from Phase 21.")
    for name in OBJECTIVE_LEVELS:
        left, right = int(forced[name]), int(baseline[name])
        if left == right:
            continue
        if name.startswith("served_"):
            return "BETTER" if left > right else "WORSE"
        return "BETTER" if left < right else "WORSE"
    return "EQUAL"


def first_degraded_policy_tier(forced: Mapping[str, int],
                               baseline: Mapping[str, int]) -> str | None:
    relation = compare_objective_vectors(forced, baseline)
    if relation != "WORSE":
        return None
    for name in OBJECTIVE_LEVELS:
        if int(forced[name]) != int(baseline[name]):
            return TIER_LABELS[name]
    raise CounterfactualDeltaError("Worse vector has no differing tier.")


def objective_deltas(forced: Mapping[str, int], baseline: Mapping[str, int]) -> dict[str, int]:
    if tuple(forced) != OBJECTIVE_LEVELS or tuple(baseline) != OBJECTIVE_LEVELS:
        raise CounterfactualDeltaError("Objective vector keys/order differ from Phase 21.")
    return {name: int(forced[name]) - int(baseline[name]) for name in OBJECTIVE_LEVELS}


def allocation_change_rows(baseline: pd.DataFrame, counterfactual: pd.DataFrame) -> pd.DataFrame:
    """Compare decision plus exact vehicle/trip assignment at one-row-per-order grain."""
    required = {"order_ref", "decision", "vehicle_id", "trip_id"}
    if required.difference(baseline.columns) or required.difference(counterfactual.columns):
        raise CounterfactualDeltaError("Allocation comparison columns are incomplete.")
    if baseline.order_ref.duplicated().any() or counterfactual.order_ref.duplicated().any():
        raise CounterfactualDeltaError("Allocation comparison requires unique orders.")
    joined = baseline[list(required)].merge(
        counterfactual[list(required)], on="order_ref", how="outer",
        suffixes=("_baseline", "_counterfactual"), indicator=True, validate="one_to_one",
    )
    if not joined["_merge"].eq("both").all():
        raise CounterfactualDeltaError("Baseline and counterfactual order sets differ.")

    def clean(value: object) -> object:
        return None if pd.isna(value) or str(value).strip() == "" else str(value)

    rows = []
    for row in joined.to_dict("records"):
        before_served = row["decision_baseline"] == "served"
        after_served = row["decision_counterfactual"] == "served"
        before_assignment = (clean(row["vehicle_id_baseline"]), clean(row["trip_id_baseline"]))
        after_assignment = (clean(row["vehicle_id_counterfactual"]), clean(row["trip_id_counterfactual"]))
        changed = (before_served != after_served) or (before_served and before_assignment != after_assignment)
        rows.append({
            "order_ref": str(row["order_ref"]),
            "changed": bool(changed),
            "served_to_deferred": bool(before_served and not after_served),
            "deferred_to_served": bool(not before_served and after_served),
            "served_reassigned": bool(before_served and after_served and before_assignment != after_assignment),
            "baseline_vehicle_id": before_assignment[0],
            "baseline_trip_id": before_assignment[1],
            "counterfactual_vehicle_id": after_assignment[0],
            "counterfactual_trip_id": after_assignment[1],
        })
    return pd.DataFrame(rows)


def summarize_allocation_changes(changes: pd.DataFrame) -> dict[str, int]:
    changed = changes.loc[changes["changed"]]
    vehicles = set(changed["baseline_vehicle_id"].dropna()) | set(changed["counterfactual_vehicle_id"].dropna())
    before_trips = set(zip(changed["baseline_vehicle_id"].dropna(), changed.loc[changed["baseline_vehicle_id"].notna(), "baseline_trip_id"]))
    after_trips = set(zip(changed["counterfactual_vehicle_id"].dropna(), changed.loc[changed["counterfactual_vehicle_id"].notna(), "counterfactual_trip_id"]))
    return {
        "changed_order_count": int(changed.shape[0]),
        "served_to_deferred_count": int(changed["served_to_deferred"].sum()),
        "deferred_to_served_count": int(changed["deferred_to_served"].sum()),
        "served_reassigned_count": int(changed["served_reassigned"].sum()),
        "affected_vehicle_count": len(vehicles),
        "affected_trip_count": len(before_trips | after_trips),
    }
