r"""Human-local frozen Task 2B allocation charts. Never run via an AI agent.

Run from repository root:
  .\.venv\Scripts\python.exe scripts\plot_internal_task2b.py

Sources: configs/task2b_validation.yaml; Phase 22 freeze_manifest.json;
data/interim/task2b_final_{allocation,trip_summary}.csv; Phase 23
validation_summary.json, hard_rule_audit.json, trip_time_audit.csv and
vehicle_budget_audit.csv; Phase 33 official_checker_evidence.json; and the
unchanged outputs/submission_task2b.csv hash. No raw competition rows are read.
The official checker establishes feasibility only, not allocation optimality.

Outputs (private, no real identifiers on charts):
  reports/private/internal_results_charts/task2b_served_vs_deferred.png
  reports/private/internal_results_charts/task2b_trips_per_vehicle.png
  reports/private/internal_results_charts/task2b_trip_capacity_utilization.png
  reports/private/internal_results_charts/task2b_trip_time_components.png
  reports/private/internal_results_charts/task2b_vehicle_time_budget.png
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

import numpy as np
import pandas as pd

from internal_charts_common import (
    ACCENT, BLUE, ChartEvidenceError, ROOT, canvas, columns, csv_source,
    json_source, numeric, save, sha256, yaml_source,
)

VALIDATOR = "reports/private/phase23_task2b_validator"


def _canonical_trip_ids(values: pd.Series) -> pd.Series:
    """Accept only integer-equivalent official trip IDs 1/2, without float rounding."""
    normalized = []
    for raw in values:
        if pd.isna(raw):
            raise ChartEvidenceError("Served trip ID is missing.")
        try:
            trip_id = Decimal(str(raw))
        except InvalidOperation as exc:
            raise ChartEvidenceError("Trip ID is not a valid integer.") from exc
        if not trip_id.is_finite() or trip_id not in (Decimal(1), Decimal(2)):
            raise ChartEvidenceError("Trip ID is outside the allowed 1/2 domain.")
        normalized.append(str(int(trip_id)))
    return pd.Series(normalized, index=values.index, dtype="string")


def checked_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    config = yaml_source("configs/task2b_validation.yaml")
    allocation_path = config.get("allocation", {}).get("path")
    summary_path = config.get("allocation", {}).get("trip_summary_path")
    freeze_path = config.get("allocation", {}).get("phase22_freeze_manifest")
    if (allocation_path != "data/interim/task2b_final_allocation.csv"
            or summary_path != "data/interim/task2b_final_trip_summary.csv"
            or freeze_path != "reports/private/phase22_task2b_optimizer/freeze_manifest.json"
            or config.get("time", {}).get("fresh_budget_min") != 270
            or config.get("time", {}).get("style_tech_budget_min") != 480
            or config.get("time", {}).get("include_return_leg") is not False):
        raise ChartEvidenceError("Canonical Task 2B source/time configuration changed.")
    freeze = json_source(freeze_path, private=True)
    validation = json_source(f"{VALIDATOR}/validation_summary.json", private=True)
    hard = json_source(f"{VALIDATOR}/hard_rule_audit.json", private=True)
    checker = json_source("reports/private/phase33_final_submissions/official_checker_evidence.json", private=True)
    allocation_hash, trip_hash = sha256(ROOT / allocation_path), sha256(ROOT / summary_path)
    freeze_hash = sha256(ROOT / freeze_path)
    official_hash = sha256(ROOT / "outputs/submission_task2b.csv")
    if (freeze.get("phase") != 22 or freeze.get("state") != "FROZEN"
            or freeze.get("allocation_sha256") != allocation_hash
            or freeze.get("trip_summary_sha256") != trip_hash
            or validation.get("status") != "PASS"
            or validation.get("frozen_integrity_status") != "PASS"
            or validation.get("frozen_allocation_sha256") != allocation_hash
            or validation.get("trip_summary_sha256") != trip_hash
            or validation.get("phase22_freeze_manifest_sha256") != freeze_hash
            or validation.get("hard_rules_status") != "PASS"
            or validation.get("time_budget_status") != "PASS"
            or checker.get("status") != "PASS"
            or checker.get("exit_code") != 0
            or checker.get("pass_detected") is not True
            or checker.get("timed_out") is not False
            or checker.get("semantics") != "feasibility_only"
            or checker.get("final_submission_sha256") != official_hash):
        raise ChartEvidenceError("Frozen allocation, independent audit, or official checker disagree.")
    if (not isinstance(hard.get("rules"), dict) or not hard["rules"]
            or any(rule.get("status") != "PASS" or rule.get("violation_count") != 0
                   for rule in hard["rules"].values())
            or any(entries for entries in hard.get("violations", {}).values())
            or any(value != 0 for value in validation.get("violation_counts_by_rule", {}).values())):
        raise ChartEvidenceError("Hard-rule audit contains unverified rules or violations.")
    allocation = csv_source(allocation_path, dtype={"order_ref": "string", "vehicle_id": "string",
                                                   "trip_id": "string"})
    trips = csv_source(summary_path, dtype={"vehicle_id": "string", "trip_id": "string"})
    trip_audit = csv_source(f"{VALIDATOR}/trip_time_audit.csv", private=True,
                            dtype={"vehicle_id": "string", "trip_id": "string"})
    budget = csv_source(f"{VALIDATOR}/vehicle_budget_audit.csv", private=True,
                        dtype={"vehicle_id": "string"})
    columns(allocation, ("scenario", "order_ref", "decision", "vehicle_id", "trip_id"))
    columns(trips, ("vehicle_id", "trip_id", "order_count", "weight_kg", "volume_m3",
                    "weight_cap_kg", "volume_cap_m3", "outbound_minutes",
                    "inter_stop_minutes", "handling_minutes", "trip_minutes"))
    columns(trip_audit, ("vehicle_id", "trip_id", "outbound_minutes", "inter_stop_minutes",
                         "handling_minutes", "trip_minutes", "return_minutes_added",
                         "time_calculation_ok"))
    columns(budget, ("vehicle_id", "trip_count", "fresh_minutes", "fresh_budget_min",
                     "fresh_budget_ok", "style_tech_minutes", "style_tech_budget_min",
                     "style_tech_budget_ok", "overall_budget_ok"))
    if (allocation.order_ref.isna().any() or allocation.order_ref.duplicated().any()
            or not allocation.scenario.eq("S1").all()
            or not allocation.decision.isin(("served", "deferred")).all()
            or len(allocation) != validation.get("checked_order_count")
            or len(trips) != validation.get("checked_trip_count")):
        raise ChartEvidenceError("Allocation identity or trip counts do not match validator.")
    served = allocation.loc[allocation.decision.eq("served")].copy()
    deferred = allocation.loc[allocation.decision.eq("deferred")]
    if (served[["vehicle_id", "trip_id"]].isna().any().any()
            or deferred[["vehicle_id", "trip_id"]].notna().any().any()):
        raise ChartEvidenceError("Served/deferred assignment fields are invalid.")
    served["trip_id"] = _canonical_trip_ids(served["trip_id"])
    trips["trip_id"] = _canonical_trip_ids(trips["trip_id"])
    trip_audit["trip_id"] = _canonical_trip_ids(trip_audit["trip_id"])
    if (trips.duplicated(["vehicle_id", "trip_id"]).any()
            or trip_audit.duplicated(["vehicle_id", "trip_id"]).any()):
        raise ChartEvidenceError("Canonical trip keys are duplicated.")
    if (not set(zip(served.vehicle_id.astype(str), served.trip_id.astype(str)))
            == set(zip(trips.vehicle_id.astype(str), trips.trip_id.astype(str)))
            or len(served) != numeric(trips, "order_count").sum()):
        raise ChartEvidenceError("Served/deferred assignments do not match frozen trip summary.")
    counts = served.groupby(["vehicle_id", "trip_id"], dropna=False).size()
    expected = trips.set_index(["vehicle_id", "trip_id"]).order_count.astype(float)
    if not counts.sort_index().equals(expected.astype(int).sort_index()):
        raise ChartEvidenceError("Frozen trip order counts do not match allocation.")
    if len(trip_audit) != len(trips):
        raise ChartEvidenceError("Trip-time audit coverage differs from frozen trips.")
    paired = trips.merge(trip_audit, on=["vehicle_id", "trip_id"], how="outer",
                         validate="one_to_one", suffixes=("_frozen", "_audit"), indicator=True)
    if not paired._merge.eq("both").all():
        raise ChartEvidenceError("Trip audit keys differ from frozen trip keys.")
    for name in ("outbound_minutes", "inter_stop_minutes", "handling_minutes", "trip_minutes"):
        left = numeric(paired, f"{name}_frozen", nonnegative=True)
        right = numeric(paired, f"{name}_audit", nonnegative=True)
        if not np.allclose(left, right, rtol=0, atol=1e-8):
            raise ChartEvidenceError("Trip-time audit disagrees with frozen summary.")
    if (not numeric(trip_audit, "return_minutes_added").eq(0).all()
            or not trip_audit.time_calculation_ok.astype(str).str.lower().eq("true").all()
            or not np.allclose(numeric(trips, "trip_minutes"),
                               numeric(trips, "outbound_minutes")
                               + numeric(trips, "inter_stop_minutes")
                               + numeric(trips, "handling_minutes"), rtol=0, atol=1e-8)):
        raise ChartEvidenceError("Trip-time arithmetic/return-leg policy fails.")
    for flag in ("fresh_budget_ok", "style_tech_budget_ok", "overall_budget_ok"):
        if not budget[flag].astype(str).str.lower().eq("true").all():
            raise ChartEvidenceError("Vehicle budget audit is not all PASS.")
    active_trips = trips.groupby("vehicle_id").size()
    reported_trips = budget.set_index("vehicle_id").trip_count.astype(int)
    if (budget.vehicle_id.isna().any() or budget.vehicle_id.duplicated().any()
            or not set(trips.vehicle_id.astype(str)).issubset(set(budget.vehicle_id.astype(str)))
            or numeric(budget, "trip_count").gt(2).any()
            or not active_trips.eq(reported_trips.reindex(active_trips.index)).all()):
        raise ChartEvidenceError("Vehicle budget coverage/trip limit fails.")
    for used, limit, expected_limit in (("fresh_minutes", "fresh_budget_min", 270),
                                        ("style_tech_minutes", "style_tech_budget_min", 480)):
        if (not numeric(budget, limit).eq(expected_limit).all()
                or (numeric(budget, used, nonnegative=True) > numeric(budget, limit)).any()):
            raise ChartEvidenceError("Vehicle daily time budget fails.")
    return allocation, trips, trip_audit, budget


def decision_chart(allocation: pd.DataFrame) -> None:
    counts = allocation.decision.value_counts()
    fig, ax = canvas("Task 2B · served versus deferred",
                     "Frozen S1 allocation · independent validator PASS · official checker feasibility PASS",
                     "Orders (count)")
    ax.bar(["Served", "Deferred"], [counts.get("served", 0), counts.get("deferred", 0)],
           color=[BLUE, ACCENT], width=0.5)
    save(fig, "task2b_served_vs_deferred.png")


def capacity_chart(trips: pd.DataFrame) -> None:
    weight = numeric(trips, "weight_kg", nonnegative=True)
    volume = numeric(trips, "volume_m3", nonnegative=True)
    weight_cap = numeric(trips, "weight_cap_kg")
    volume_cap = numeric(trips, "volume_cap_m3")
    if ((weight_cap <= 0).any() or (volume_cap <= 0).any()
            or (weight > weight_cap).any() or (volume > volume_cap).any()):
        raise ChartEvidenceError("Frozen trip capacity utilization is invalid.")
    fig, ax = canvas("Task 2B · trip capacity utilization",
                     "Frozen feasible trips · each dot is one trip; vehicle/order identifiers hidden",
                     "Volume capacity used (%)")
    ax.scatter(100 * weight / weight_cap, 100 * volume / volume_cap,
               s=48, color=BLUE, alpha=0.5)
    ax.set(xlabel="Weight capacity used (%)", xlim=(0, 105), ylim=(0, 105))
    save(fig, "task2b_trip_capacity_utilization.png")


def trips_per_vehicle_chart(budget: pd.DataFrame) -> None:
    counts = numeric(budget, "trip_count")
    if not counts.isin([0, 1, 2]).all():
        raise ChartEvidenceError("Vehicle trip count is outside the allowed range.")
    histogram = counts.value_counts().reindex([0, 1, 2], fill_value=0)
    fig, ax = canvas("Task 2B · trips per available vehicle",
                     "Frozen S1 allocation · at most two trips per vehicle · no vehicle identifiers",
                     "Vehicles (count)")
    ax.bar(["0 trips", "1 trip", "2 trips"], histogram.to_numpy(), color=[ACCENT, BLUE, BLUE], width=0.55)
    save(fig, "task2b_trips_per_vehicle.png")


def trip_time_chart(trips: pd.DataFrame) -> None:
    ordered = trips.sort_values("trip_minutes", kind="stable").reset_index(drop=True)
    x = np.arange(1, len(ordered) + 1)
    outbound = numeric(ordered, "outbound_minutes")
    inter = numeric(ordered, "inter_stop_minutes")
    handling = numeric(ordered, "handling_minutes")
    fig, ax = canvas("Task 2B · feasible trip-time components",
                     "Frozen trip arithmetic: outbound + inter-stop + handling; no return leg",
                     "Trip time (minutes)")
    ax.bar(x, outbound, color=BLUE, label="Outbound")
    ax.bar(x, inter, bottom=outbound, color=ACCENT, label="Inter-stop")
    ax.bar(x, handling, bottom=outbound + inter, color="#94A3B8", label="Handling")
    ax.set_xlabel("Trip index, sorted by total time (anonymized)")
    ax.legend(frameon=False)
    save(fig, "task2b_trip_time_components.png")


def budget_chart(budget: pd.DataFrame) -> None:
    fresh = 100 * numeric(budget, "fresh_minutes") / 270
    style_tech = 100 * numeric(budget, "style_tech_minutes") / 480
    fig, ax = canvas("Task 2B · daily vehicle time budgets",
                     "Independent frozen-allocation audit PASS · Fresh 270 min, Style+Tech 480 min",
                     "Vehicles (count)")
    bins = np.linspace(0, 100, 11)
    ax.hist([fresh, style_tech], bins=bins, color=[BLUE, ACCENT],
            alpha=0.8, label=["Fresh budget used", "Style+Tech budget used"])
    ax.set(xlabel="Daily category time budget used (%)", xlim=(0, 100))
    ax.legend(frameon=False)
    save(fig, "task2b_vehicle_time_budget.png")


def main() -> int:
    try:
        allocation, trips, audit, budget = checked_sources()
        # Validate all chart-specific numeric evidence before writing any PNG.
        weight = numeric(trips, "weight_kg", nonnegative=True)
        volume = numeric(trips, "volume_m3", nonnegative=True)
        if ((weight > numeric(trips, "weight_cap_kg")).any()
                or (volume > numeric(trips, "volume_cap_m3")).any()):
            raise ChartEvidenceError("Capacity utilization fails.")
        decision_chart(allocation)
        trips_per_vehicle_chart(budget)
        capacity_chart(trips)
        trip_time_chart(trips)
        budget_chart(budget)
    except ChartEvidenceError as exc:
        # Every ChartEvidenceError message in this module/common helpers is fixed
        # text; no private values or identifiers are interpolated into it.
        print(f"SKIPPED: Task 2B charts — {exc}")
        return 1
    except (KeyError, ValueError):
        print("SKIPPED: Task 2B charts — frozen allocation/checker evidence is missing or inconsistent")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
