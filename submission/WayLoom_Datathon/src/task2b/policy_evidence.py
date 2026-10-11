"""Aggregate-only, provenance-bound evidence for the Phase 24 policy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.task2b.artifact_integrity import sha256_file
from src.task2b.checker_evidence import CheckerEvidenceError, require_successful_cross_validation


class PolicyEvidenceError(ValueError):
    """Policy evidence is incomplete, inconsistent, or privacy-unsafe."""


def load_phase23_pass_evidence(
    requested_path: Path,
    *,
    expected_frozen_allocation_sha256: str | None = None,
) -> tuple[dict[str, Any], Path]:
    """Load a PASS record, resolving the latest immutable run when needed."""
    requested_path = Path(requested_path)
    candidates = [requested_path] if requested_path.is_file() else []
    runs_dir = requested_path.parent / "checker_runs"
    if runs_dir.is_dir():
        candidates.extend(sorted(runs_dir.glob("*/checker_evidence.json"), reverse=True))
    if not candidates:
        raise PolicyEvidenceError("Phase 23 checker evidence is missing.")
    errors: list[str] = []
    for path in candidates:
        try:
            evidence = json.loads(path.read_text(encoding="utf-8"))
            require_successful_cross_validation(evidence)
            if (expected_frozen_allocation_sha256 is not None
                    and evidence.get("frozen_allocation_sha256") != expected_frozen_allocation_sha256):
                raise PolicyEvidenceError("Phase 23 evidence targets a different frozen allocation.")
            return evidence, path.resolve()
        except (OSError, json.JSONDecodeError, CheckerEvidenceError, PolicyEvidenceError) as exc:
            errors.append(type(exc).__name__)
    raise PolicyEvidenceError(f"No valid Phase 23 PASS evidence was found ({', '.join(errors)}).")


def phase23_report_root(evidence_path: Path) -> Path:
    evidence_path = Path(evidence_path).resolve()
    if evidence_path.parent.parent.name == "checker_runs":
        return evidence_path.parent.parent.parent
    return evidence_path.parent


def load_phase23_candidate_if_available(
    evidence_path: Path,
    evidence: dict[str, Any],
) -> tuple[pd.DataFrame | None, Path | None]:
    candidate = phase23_report_root(evidence_path) / "checker_workspace" / "submission_task2b.csv"
    if not candidate.is_file():
        return None, None
    if sha256_file(candidate) != evidence.get("checker_input_sha256"):
        raise PolicyEvidenceError("Phase 23 checker candidate hash differs from PASS evidence.")
    return pd.read_csv(candidate, dtype="string", keep_default_na=False), candidate


def _numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        raise PolicyEvidenceError(f"Policy source lacks {column}.")
    values = pd.to_numeric(frame[column], errors="raise")
    if not np.isfinite(values.to_numpy(dtype=float)).all() or values.lt(0).any():
        raise PolicyEvidenceError(f"Policy source {column} must be finite and nonnegative.")
    return values


def _counts_by_brand(frame: pd.DataFrame) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(frame.groupby("brand").size().items())}


def _sums_by_brand(frame: pd.DataFrame, column: str) -> dict[str, float]:
    return {
        str(key): float(value)
        for key, value in sorted(frame.groupby("brand")[column].sum().items())
    }


def _provenance(keys: list[str], source: str | list[str]) -> dict[str, list[str]]:
    sources = [source] if isinstance(source, str) else source
    return {key: list(sources) for key in keys}


def build_task2b_policy_evidence(
    orders: pd.DataFrame,
    frozen_allocation: pd.DataFrame,
    fleet: pd.DataFrame,
    vehicles: pd.DataFrame,
    compatibility_summary: pd.DataFrame,
    trip_summary: pd.DataFrame,
    phase23_evidence: dict[str, Any],
    *,
    trip_summary_sha256: str,
    expected_scenario: str = "S1",
    expected_depot: str = "Peliyagoda",
    fresh_budget_limit: int = 270,
    style_tech_budget_limit: int = 480,
) -> dict[str, Any]:
    """Build aggregate policy metrics without retaining row-level identifiers."""
    try:
        require_successful_cross_validation(phase23_evidence)
    except CheckerEvidenceError as exc:
        raise PolicyEvidenceError("Phase 23 cross-validation is not PASS.") from exc
    required_orders = {
        "scenario", "order_ref", "outlet_id", "brand", "temp_requirement",
        "order_units", "order_weight_kg", "order_volume_m3", "deferred_yesterday",
        "days_since_last_served",
    }
    if required_orders.difference(orders.columns):
        raise PolicyEvidenceError("Canonical policy order source is incomplete.")
    if {"scenario", "order_ref", "decision", "vehicle_id", "trip_id"}.difference(frozen_allocation.columns):
        raise PolicyEvidenceError("Frozen allocation is incomplete.")
    if orders.order_ref.isna().any() or orders.order_ref.duplicated().any():
        raise PolicyEvidenceError("Canonical policy order keys are invalid.")
    if frozen_allocation.order_ref.isna().any() or frozen_allocation.order_ref.duplicated().any():
        raise PolicyEvidenceError("Frozen allocation keys are invalid.")
    orders_s1 = orders.loc[orders.scenario.eq(expected_scenario)].copy(deep=True)
    allocation_s1 = frozen_allocation.loc[frozen_allocation.scenario.eq(expected_scenario)].copy(deep=True)
    if len(orders_s1) != len(orders) or len(allocation_s1) != len(frozen_allocation):
        raise PolicyEvidenceError("Policy evidence must contain only Scenario S1.")
    if set(orders_s1.order_ref.astype(str)) != set(allocation_s1.order_ref.astype(str)):
        raise PolicyEvidenceError("Policy orders and allocation order sets differ.")
    if not allocation_s1.decision.isin(["served", "deferred"]).all():
        raise PolicyEvidenceError("Policy allocation decision domain is invalid.")

    frame = orders_s1.merge(
        allocation_s1[["order_ref", "decision", "vehicle_id", "trip_id"]],
        on="order_ref",
        how="left",
        validate="one_to_one",
    )
    for column in ("order_units", "order_weight_kg", "order_volume_m3", "days_since_last_served"):
        frame[column] = _numeric(frame, column)
    deferred_signal = pd.to_numeric(frame["deferred_yesterday"], errors="raise")
    if not deferred_signal.isin([0, 1]).all():
        raise PolicyEvidenceError("deferred_yesterday must be binary.")
    frame["deferred_yesterday"] = deferred_signal.astype(int)
    if compatibility_summary.duplicated("order_ref").any() or {
        "order_ref", "compatible_vehicle_count"
    }.difference(compatibility_summary.columns):
        raise PolicyEvidenceError("Compatibility summary is invalid.")
    frame = frame.merge(
        compatibility_summary[["order_ref", "compatible_vehicle_count"]],
        on="order_ref",
        how="left",
        validate="one_to_one",
    )
    if frame.compatible_vehicle_count.isna().any():
        raise PolicyEvidenceError("Every order requires compatibility evidence.")
    frame["compatible_vehicle_count"] = pd.to_numeric(
        frame["compatible_vehicle_count"], errors="raise"
    ).astype(int)

    served = frame.loc[frame.decision.eq("served")].copy()
    deferred = frame.loc[frame.decision.eq("deferred")].copy()
    total = int(len(frame))
    served_count, deferred_count = int(len(served)), int(len(deferred))

    fleet_s1 = fleet.loc[fleet.scenario.eq(expected_scenario)].copy(deep=True)
    if fleet_s1.vehicle_id.duplicated().any() or not set(fleet_s1.status).issubset({"available", "in_workshop"}):
        raise PolicyEvidenceError("Scenario fleet evidence is invalid.")
    if vehicles.vehicle_id.duplicated().any() or {"vehicle_id", "type", "temp", "depot"}.difference(vehicles.columns):
        raise PolicyEvidenceError("Vehicle reference evidence is invalid.")
    joined_fleet = fleet_s1.merge(
        vehicles[["vehicle_id", "type", "temp", "depot"]],
        on="vehicle_id",
        how="left",
        validate="one_to_one",
    )
    if joined_fleet[["type", "temp", "depot"]].isna().any().any():
        raise PolicyEvidenceError("Scenario fleet lacks vehicle reference coverage.")
    usable = joined_fleet.loc[
        joined_fleet.status.eq("available") & joined_fleet.depot.eq(expected_depot)
    ].copy()

    required_trip = {"vehicle_id", "trip_id", "brand", "trip_minutes", "weight_kg", "volume_m3", "weight_cap_kg", "volume_cap_m3"}
    if required_trip.difference(trip_summary.columns):
        raise PolicyEvidenceError("Frozen trip summary is incomplete.")
    if trip_summary.duplicated(["vehicle_id", "trip_id"]).any():
        raise PolicyEvidenceError("Frozen trip summary has duplicate trip keys.")
    trip_frame = trip_summary.copy(deep=True)
    for column in ("trip_minutes", "weight_kg", "volume_m3", "weight_cap_kg", "volume_cap_m3"):
        trip_frame[column] = _numeric(trip_frame, column)
    served_trip_count = int(
        allocation_s1.loc[allocation_s1.decision.eq("served"), ["vehicle_id", "trip_id"]]
        .drop_duplicates().shape[0]
    )
    if served_trip_count != len(trip_frame):
        raise PolicyEvidenceError("Frozen allocation and trip-summary trip counts differ.")
    fresh_by_vehicle = (
        trip_frame.loc[trip_frame.brand.eq("Fresh")].groupby("vehicle_id")["trip_minutes"].sum()
    )
    other_by_vehicle = (
        trip_frame.loc[trip_frame.brand.isin(["Style", "Tech"])].groupby("vehicle_id")["trip_minutes"].sum()
    )
    weight_util = (trip_frame.weight_kg / trip_frame.weight_cap_kg.replace(0, np.nan)).fillna(0)
    volume_util = (trip_frame.volume_m3 / trip_frame.volume_cap_m3.replace(0, np.nan)).fillna(0)

    previous_total = int(frame.deferred_yesterday.sum())
    previous_served = int(served.deferred_yesterday.sum())
    previous_still = int(deferred.deferred_yesterday.sum())
    deferred_days = deferred.days_since_last_served
    impossible_deferred = deferred.compatible_vehicle_count.eq(0)
    low_flex_deferred = deferred.compatible_vehicle_count.between(1, 2)
    assigned_vehicle_ids = set(served.vehicle_id.dropna().astype(str))
    used_vehicle_ref = vehicles.loc[vehicles.vehicle_id.astype(str).isin(assigned_vehicle_ids)]
    if served.compatible_vehicle_count.eq(0).any():
        raise PolicyEvidenceError("An individually impossible order cannot be reported as served.")
    if assigned_vehicle_ids.difference(set(usable.vehicle_id.astype(str))) or len(used_vehicle_ref) != len(assigned_vehicle_ids):
        raise PolicyEvidenceError("Served assignments are not covered by the usable scenario fleet.")

    metrics: dict[str, Any] = {
        "total_orders": total,
        "served_orders": served_count,
        "deferred_orders": deferred_count,
        "served_share": float(served_count / total) if total else 0.0,
        "served_share_percent": round(100.0 * served_count / total, 1) if total else 0.0,
        "deferred_share_percent": round(100.0 * deferred_count / total, 1) if total else 0.0,
        "served_by_brand": _counts_by_brand(served),
        "deferred_by_brand": _counts_by_brand(deferred),
        "deferred_volume_by_brand_m3": _sums_by_brand(deferred, "order_volume_m3"),
        "served_units": float(served.order_units.sum()),
        "deferred_units": float(deferred.order_units.sum()),
        "served_weight_kg": float(served.order_weight_kg.sum()),
        "deferred_weight_kg": float(deferred.order_weight_kg.sum()),
        "served_volume_m3": float(served.order_volume_m3.sum()),
        "deferred_volume_m3": float(deferred.order_volume_m3.sum()),
        "deferred_chilled_orders": int(deferred.temp_requirement.eq("chilled").sum()),
        "deferred_chilled_volume_m3": float(
            deferred.loc[deferred.temp_requirement.eq("chilled"), "order_volume_m3"].sum()
        ),
        "previously_deferred_total": previous_total,
        "previously_deferred_served": previous_served,
        "previously_deferred_still_deferred": previous_still,
        "deferred_days_since_last_served_sum": float(deferred_days.sum()),
        "deferred_days_since_last_served_mean": round(float(deferred_days.mean()), 2) if len(deferred) else 0.0,
        "deferred_days_since_last_served_max": float(deferred_days.max()) if len(deferred) else 0.0,
        "individually_impossible_count": int(frame.compatible_vehicle_count.eq(0).sum()),
        "individually_impossible_deferred_count": int(impossible_deferred.sum()),
        "individually_feasible_deferred_count": int((deferred.compatible_vehicle_count.gt(0)).sum()),
        "low_flexibility_deferred_count": int(low_flex_deferred.sum()),
        "deferred_chilled_without_compatible_vehicle_count": int(
            (impossible_deferred & deferred.temp_requirement.eq("chilled")).sum()
        ),
        "unique_deferred_outlet_count": int(deferred.outlet_id.nunique()),
        "available_vehicle_count": int(len(usable)),
        "listed_available_vehicle_count": int(fleet_s1.status.eq("available").sum()),
        "workshop_vehicle_count": int(fleet_s1.status.eq("in_workshop").sum()),
        "available_reefer_count": int(usable.temp.eq("reefer").sum()),
        "available_reefer_van_count": int((usable.temp.eq("reefer") & usable.type.eq("van")).sum()),
        "used_vehicle_count": int(len(assigned_vehicle_ids)),
        "used_reefer_count": int(used_vehicle_ref.temp.eq("reefer").sum()),
        "used_reefer_van_count": int((used_vehicle_ref.temp.eq("reefer") & used_vehicle_ref.type.eq("van")).sum()),
        "used_trip_count": served_trip_count,
        "available_trip_slot_upper_bound": int(2 * len(usable)),
        "max_fresh_minutes_used_by_vehicle": float(fresh_by_vehicle.max()) if len(fresh_by_vehicle) else 0.0,
        "max_style_tech_minutes_used_by_vehicle": float(other_by_vehicle.max()) if len(other_by_vehicle) else 0.0,
        "fresh_budget_limit": int(fresh_budget_limit),
        "style_tech_budget_limit": int(style_tech_budget_limit),
        "max_trip_weight_utilization_percent": round(float(weight_util.max() * 100), 1) if len(weight_util) else 0.0,
        "max_trip_volume_utilization_percent": round(float(volume_util.max() * 100), 1) if len(volume_util) else 0.0,
        "own_validator_pass": phase23_evidence.get("own_validator_status") == "PASS",
        "official_checker_pass": phase23_evidence.get("official_checker_status") == "PASS",
    }

    provenance: dict[str, list[str]] = {}
    provenance.update(_provenance([
        "total_orders", "served_orders", "deferred_orders", "served_share", "served_share_percent",
        "deferred_share_percent", "served_by_brand", "deferred_by_brand", "deferred_volume_by_brand_m3",
        "served_units", "deferred_units", "served_weight_kg", "deferred_weight_kg", "served_volume_m3",
        "deferred_volume_m3", "deferred_chilled_orders", "deferred_chilled_volume_m3",
        "previously_deferred_total", "previously_deferred_served", "previously_deferred_still_deferred",
        "deferred_days_since_last_served_sum", "deferred_days_since_last_served_mean",
        "deferred_days_since_last_served_max", "unique_deferred_outlet_count",
    ], ["task2b_peak_day_scenarios.csv", "phase22_frozen_allocation"]))
    provenance.update(_provenance([
        "individually_impossible_count", "individually_impossible_deferred_count",
        "individually_feasible_deferred_count", "low_flexibility_deferred_count",
        "deferred_chilled_without_compatible_vehicle_count",
    ], ["task2b_peak_day_scenarios.csv", "phase19_compatibility_recomputation", "phase22_frozen_allocation"]))
    provenance.update(_provenance([
        "available_vehicle_count", "listed_available_vehicle_count", "workshop_vehicle_count",
        "available_reefer_count", "available_reefer_van_count", "used_vehicle_count",
        "used_reefer_count", "used_reefer_van_count", "available_trip_slot_upper_bound",
    ], ["task2b_peak_day_fleet.csv", "vehicles.csv", "phase22_frozen_allocation"]))
    provenance.update(_provenance([
        "used_trip_count", "max_fresh_minutes_used_by_vehicle", "max_style_tech_minutes_used_by_vehicle",
        "max_trip_weight_utilization_percent", "max_trip_volume_utilization_percent",
    ], "phase22_frozen_trip_summary"))
    provenance.update(_provenance(
        ["fresh_budget_limit", "style_tech_budget_limit"], "official_challenge_booklet_task2b"
    ))
    provenance.update(_provenance(
        ["own_validator_pass", "official_checker_pass"], "phase23_checker_evidence"
    ))
    result = {
        "phase": 24,
        "kind": "aggregate_policy_evidence",
        "bindings": {
            "phase22_frozen_allocation_sha256": phase23_evidence.get("frozen_allocation_sha256"),
            "phase23_checker_input_sha256": phase23_evidence.get("checker_input_sha256"),
            "trip_summary_sha256": trip_summary_sha256,
        },
        "metrics": metrics,
        "provenance": provenance,
    }
    validate_policy_evidence(result)
    return result


def validate_policy_evidence(evidence: dict[str, Any]) -> None:
    if evidence.get("phase") != 24 or evidence.get("kind") != "aggregate_policy_evidence":
        raise PolicyEvidenceError("Policy evidence identity is invalid.")
    metrics, provenance, bindings = (
        evidence.get("metrics"), evidence.get("provenance"), evidence.get("bindings")
    )
    if not isinstance(metrics, dict) or not isinstance(provenance, dict) or not isinstance(bindings, dict):
        raise PolicyEvidenceError("Policy evidence structure is invalid.")
    required_bindings = {
        "phase22_frozen_allocation_sha256", "phase23_checker_input_sha256", "trip_summary_sha256"
    }
    if set(bindings) != required_bindings or any(
        not isinstance(bindings[name], str)
        or len(bindings[name]) != 64
        or any(character not in "0123456789abcdef" for character in bindings[name].lower())
        for name in required_bindings
    ):
        raise PolicyEvidenceError("Policy evidence hash bindings are invalid.")
    if set(metrics) != set(provenance):
        raise PolicyEvidenceError("Every policy metric must have provenance.")
    if metrics["served_orders"] + metrics["deferred_orders"] != metrics["total_orders"]:
        raise PolicyEvidenceError("Served and deferred counts do not reconcile.")
    if sum(metrics["served_by_brand"].values()) != metrics["served_orders"]:
        raise PolicyEvidenceError("Served brand counts do not reconcile.")
    if sum(metrics["deferred_by_brand"].values()) != metrics["deferred_orders"]:
        raise PolicyEvidenceError("Deferred brand counts do not reconcile.")
    if (metrics["previously_deferred_served"] + metrics["previously_deferred_still_deferred"]
            != metrics["previously_deferred_total"]):
        raise PolicyEvidenceError("Previous-deferral outcomes do not reconcile.")
    if (metrics["individually_impossible_deferred_count"]
            + metrics["individually_feasible_deferred_count"] != metrics["deferred_orders"]):
        raise PolicyEvidenceError("Deferred compatibility categories do not reconcile.")
    if metrics["used_trip_count"] > metrics["available_trip_slot_upper_bound"]:
        raise PolicyEvidenceError("Used trips exceed the fleet trip-slot upper bound.")
    if metrics["own_validator_pass"] is not True or metrics["official_checker_pass"] is not True:
        raise PolicyEvidenceError("Phase 23 PASS evidence is required.")
    serialized = json.dumps(evidence, sort_keys=True).lower()
    for forbidden in ('"order_ref"', '"vehicle_id"', '"outlet_id"'):
        if forbidden in serialized:
            raise PolicyEvidenceError("Policy evidence contains a row-level identifier field.")
