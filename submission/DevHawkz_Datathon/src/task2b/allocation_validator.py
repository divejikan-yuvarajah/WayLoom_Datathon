"""Independent, read-only Phase 23 validator for a frozen Task 2B allocation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

from src.task2b.artifact_integrity import ALLOCATION_COLUMNS, sha256_file
from src.task2b.trip_time import calculate_trip_time


class AllocationValidationError(ValueError):
    """The validation contract, frozen evidence, or candidate is invalid."""


RULE_IDS = (
    "allocation_schema",
    "scenario_values",
    "order_ref_coverage",
    "decision_domain",
    "served_fields",
    "deferred_fields",
    "trip_id_domain",
    "same_brand_district",
    "refrigeration",
    "van_only",
    "home_depot_availability",
    "whole_order",
    "capacity",
    "trip_time_exact",
    "trip_count_time_budget",
)

TRIP_AUDIT_COLUMNS = (
    "vehicle_id", "trip_id", "brand", "district", "order_count",
    "outbound_minutes", "inter_stop_minutes", "handling_minutes",
    "trip_minutes", "return_minutes_added", "time_calculation_ok",
)

VEHICLE_BUDGET_COLUMNS = (
    "vehicle_id", "trip_count", "fresh_trip_count", "fresh_minutes",
    "fresh_budget_min", "fresh_budget_ok", "style_trip_count",
    "tech_trip_count", "style_tech_minutes", "style_tech_budget_min",
    "style_tech_budget_ok", "overall_budget_ok",
)


@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    task_id: str
    status: str
    violation_count: int
    summary: str


@dataclass
class AllocationValidationReport:
    overall_status: str
    rules: dict[str, RuleResult]
    violations: dict[str, list[dict[str, Any]]]
    trip_time_audit: pd.DataFrame
    vehicle_budget_audit: pd.DataFrame
    checked_order_count: int
    checked_vehicle_count: int
    checked_trip_count: int
    warnings: list[str]

    def summary(self) -> dict[str, Any]:
        return {
            "phase": 23,
            "status": self.overall_status,
            "frozen_integrity_status": "PASS",
            "identity_status": _combined_status(
                self.rules, "allocation_schema", "scenario_values", "order_ref_coverage"
            ),
            "decision_status": _combined_status(self.rules, "decision_domain"),
            "field_population_status": _combined_status(
                self.rules, "served_fields", "deferred_fields", "trip_id_domain"
            ),
            "hard_rules_status": _combined_status(
                self.rules, "same_brand_district", "refrigeration", "van_only",
                "home_depot_availability", "whole_order", "capacity",
                "trip_count_time_budget",
            ),
            "time_budget_status": _combined_status(
                self.rules, "trip_time_exact", "trip_count_time_budget"
            ),
            "violation_counts_by_rule": {
                name: result.violation_count for name, result in self.rules.items()
            },
            "checked_order_count": self.checked_order_count,
            "checked_vehicle_count": self.checked_vehicle_count,
            "checked_trip_count": self.checked_trip_count,
        }


def _combined_status(rules: dict[str, RuleResult], *names: str) -> str:
    return "PASS" if all(rules[name].status == "PASS" for name in names) else "FAIL"


def _blank(value: object) -> bool:
    return pd.isna(value) or (isinstance(value, str) and value.strip() == "")


def _key(value: object) -> str:
    return str(value)


def _decimal(value: object) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise AllocationValidationError("Validation numeric value is invalid.") from exc
    if not number.is_finite():
        raise AllocationValidationError("Validation numeric value must be finite.")
    return number


def _trip_id(value: object) -> int | None:
    if _blank(value) or isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not number.is_finite() or number != number.to_integral_value():
        return None
    result = int(number)
    return result if result in (1, 2) else None


def validate_validation_config(config: dict) -> None:
    if not isinstance(config, dict) or config.get("version") != 1:
        raise AllocationValidationError("Task 2B validation config is invalid.")
    if config.get("scenario") != {"expected_id": "S1", "expected_depot": "Peliyagoda"}:
        raise AllocationValidationError("Phase 23 is frozen to S1 at Peliyagoda.")
    if any(config.get("allocation", {}).get(name) is not True
           for name in ("require_frozen_state", "require_sha256_match")):
        raise AllocationValidationError("Frozen allocation integrity checks cannot be weakened.")
    expected_allocation_paths = {
        "path": "data/interim/task2b_final_allocation.csv",
        "phase22_freeze_manifest": "reports/private/phase22_task2b_optimizer/freeze_manifest.json",
        "trip_summary_path": "data/interim/task2b_final_trip_summary.csv",
    }
    if any(config.get("allocation", {}).get(name) != value
           for name, value in expected_allocation_paths.items()):
        raise AllocationValidationError("Canonical Phase 22 evidence paths changed.")
    if config.get("identity", {}).get("key") != "order_ref" or any(
        config.get("identity", {}).get(name) is not True
        for name in ("require_exact_order_set", "require_exact_outlet_id_match", "require_exact_scenario_match")
    ):
        raise AllocationValidationError("Allocation identity validation cannot be weakened.")
    if config.get("decision", {}).get("allowed_values") != ["served", "deferred"]:
        raise AllocationValidationError("Decision values must remain exact.")
    if (config.get("served", {}).get("require_vehicle_id") is not True
            or config.get("served", {}).get("allowed_trip_ids") != [1, 2]):
        raise AllocationValidationError("Official trip IDs must remain 1 and 2.")
    if any(config.get("deferred", {}).get(name) is not True
           for name in ("require_blank_vehicle_id", "require_blank_trip_id")):
        raise AllocationValidationError("Deferred assignment fields must remain blank.")
    time = config.get("time", {})
    if time.get("fresh_budget_min") != 270 or time.get("style_tech_budget_min") != 480:
        raise AllocationValidationError("Official time budgets changed.")
    if time.get("include_return_leg") is not False:
        raise AllocationValidationError("Return travel must not be added.")
    tolerance = config.get("numeric", {}).get("tolerance")
    if not isinstance(tolerance, (int, float)) or tolerance < 0 or tolerance > 1e-6:
        raise AllocationValidationError("Validation tolerance is invalid.")
    checker = config.get("official_checker", {})
    if checker.get("inspect_actual_interface") is not True or checker.get("do_not_guess_cli") is not True:
        raise AllocationValidationError("Official checker interface discovery cannot be disabled.")
    expected_checker_paths = {
        "source_manifest_filename": "check_allocation.py",
        "repository_path": "DataSet/check_allocation.py",
        "private_workspace": "reports/private/phase23_task2b_validator/checker_workspace",
        "evidence_runs_dir": "reports/private/phase23_task2b_validator/checker_runs",
    }
    if any(checker.get(name) != value for name, value in expected_checker_paths.items()):
        raise AllocationValidationError("Official checker or private evidence paths changed.")
    if config.get("reports", {}).get("private_output_dir") != "reports/private/phase23_task2b_validator":
        raise AllocationValidationError("Phase 23 report path must remain private.")


def verify_frozen_integrity(allocation_path: Path, freeze_manifest_path: Path,
                            trip_summary_path: Path | None = None) -> dict[str, str]:
    """Verify hashes without parsing or exposing private allocation rows."""
    allocation_path = Path(allocation_path)
    freeze_manifest_path = Path(freeze_manifest_path)
    if not allocation_path.is_file() or not freeze_manifest_path.is_file():
        raise AllocationValidationError("Frozen Phase 22 allocation evidence is missing.")
    manifest = json.loads(freeze_manifest_path.read_text(encoding="utf-8"))
    if manifest.get("phase") != 22 or manifest.get("state") != "FROZEN":
        raise AllocationValidationError("Phase 22 allocation is not frozen.")
    allocation_hash = sha256_file(allocation_path)
    if manifest.get("allocation_sha256") != allocation_hash:
        raise AllocationValidationError("Frozen allocation SHA256 mismatch.")
    result = {
        "status": "PASS",
        "allocation_sha256": allocation_hash,
        "freeze_manifest_sha256": sha256_file(freeze_manifest_path),
    }
    if trip_summary_path is not None:
        trip_summary_path = Path(trip_summary_path)
        if not trip_summary_path.is_file():
            raise AllocationValidationError("Frozen trip summary is missing.")
        trip_hash = sha256_file(trip_summary_path)
        if manifest.get("trip_summary_sha256") != trip_hash:
            raise AllocationValidationError("Frozen trip-summary SHA256 mismatch.")
        result["trip_summary_sha256"] = trip_hash
    return result


def validate_frozen_task2b_allocation(
    allocation: pd.DataFrame,
    orders_s1: pd.DataFrame,
    fleet_s1: pd.DataFrame,
    vehicles_ref: pd.DataFrame,
    district_travel_ref: pd.DataFrame,
    service_allowance_ref: pd.DataFrame,
    config: dict,
    frozen_trip_summary: pd.DataFrame | None = None,
) -> AllocationValidationReport:
    """Validate official feasibility from extracted tables, never optimizer variables."""
    validate_validation_config(config)
    allocation = allocation.copy(deep=True)
    orders_s1 = orders_s1.copy(deep=True)
    fleet_s1 = fleet_s1.copy(deep=True)
    vehicles_ref = vehicles_ref.copy(deep=True)
    district_travel_ref = district_travel_ref.copy(deep=True)
    service_allowance_ref = service_allowance_ref.copy(deep=True)
    violations: dict[str, list[dict[str, Any]]] = {name: [] for name in RULE_IDS}

    def add(rule: str, reason: str, **details: Any) -> None:
        violations[rule].append({"reason": reason, **details})

    expected_columns = set(ALLOCATION_COLUMNS)
    missing_columns = expected_columns.difference(allocation.columns)
    if missing_columns:
        add("allocation_schema", "missing_columns", columns=sorted(missing_columns))
    working = allocation.copy(deep=True)
    for column in ALLOCATION_COLUMNS:
        if column not in working:
            working[column] = pd.NA

    source_keys = [_key(value) for value in orders_s1.get("order_ref", pd.Series(dtype=object))]
    source_duplicates = pd.Series(source_keys).duplicated().any()
    if source_duplicates or any(_blank(value) for value in orders_s1.get("order_ref", [])):
        raise AllocationValidationError("Canonical S1 order keys are invalid.")
    source_map = {_key(row["order_ref"]): row for row in orders_s1.to_dict("records")}
    expected_keys = set(source_map)
    raw_keys = working["order_ref"].tolist()
    blank_key_rows = [index for index, value in enumerate(raw_keys) if _blank(value)]
    actual_nonblank = [_key(value) for value in raw_keys if not _blank(value)]
    if blank_key_rows:
        add("order_ref_coverage", "blank_order_ref", row_indexes=blank_key_rows)
    duplicates = pd.Series(actual_nonblank).duplicated(keep=False)
    if duplicates.any():
        add("order_ref_coverage", "duplicate_order_ref",
            order_refs=sorted(set(pd.Series(actual_nonblank)[duplicates].tolist())))
    actual_keys = set(actual_nonblank)
    if expected_keys - actual_keys:
        add("order_ref_coverage", "missing_order_ref", order_refs=sorted(expected_keys - actual_keys))
    if actual_keys - expected_keys:
        add("order_ref_coverage", "extra_order_ref", order_refs=sorted(actual_keys - expected_keys))
    if len(working) != len(expected_keys):
        add("order_ref_coverage", "row_count_mismatch", expected=len(expected_keys), actual=len(working))

    allocation_rows: dict[str, dict[str, Any]] = {}
    if not blank_key_rows and not duplicates.any():
        allocation_rows = {_key(row["order_ref"]): row for row in working.to_dict("records")}

    for index, row in enumerate(working.to_dict("records")):
        order_ref = None if _blank(row["order_ref"]) else _key(row["order_ref"])
        source = source_map.get(order_ref) if order_ref is not None else None
        if _blank(row["scenario"]) or row["scenario"] != "S1":
            add("scenario_values", "scenario_not_s1", row_index=index, order_ref=order_ref)
        if source is not None:
            if _blank(row["scenario"]) or row["scenario"] != source["scenario"]:
                add("scenario_values", "source_scenario_mismatch", order_ref=order_ref)
            if str(row["outlet_id"]) != str(source["outlet_id"]):
                add("scenario_values", "outlet_id_mismatch", order_ref=order_ref)
        decision = row["decision"]
        if _blank(decision) or decision not in ("served", "deferred"):
            add("decision_domain", "invalid_decision", row_index=index, order_ref=order_ref)
            continue
        if decision == "served":
            if _blank(row["vehicle_id"]):
                add("served_fields", "missing_vehicle_id", order_ref=order_ref)
            if _blank(row["trip_id"]):
                add("served_fields", "missing_trip_id", order_ref=order_ref)
            if _trip_id(row["trip_id"]) is None:
                add("trip_id_domain", "invalid_served_trip_id", order_ref=order_ref)
        else:
            if not _blank(row["vehicle_id"]):
                add("deferred_fields", "deferred_vehicle_populated", order_ref=order_ref)
            if not _blank(row["trip_id"]):
                add("deferred_fields", "deferred_trip_populated", order_ref=order_ref)

    fleet_rows = {_key(row["vehicle_id"]): row for row in fleet_s1.to_dict("records")}
    vehicle_rows = {_key(row["vehicle_id"]): row for row in vehicles_ref.to_dict("records")}
    served_records: list[dict[str, Any]] = []
    for row in working.loc[working["decision"].eq("served")].to_dict("records"):
        order_ref = None if _blank(row["order_ref"]) else _key(row["order_ref"])
        vehicle_id = None if _blank(row["vehicle_id"]) else _key(row["vehicle_id"])
        trip_id = _trip_id(row["trip_id"])
        source = source_map.get(order_ref) if order_ref is not None else None
        fleet = fleet_rows.get(vehicle_id) if vehicle_id is not None else None
        vehicle = vehicle_rows.get(vehicle_id) if vehicle_id is not None else None
        if vehicle_id is not None and fleet is None:
            add("served_fields", "vehicle_missing_from_scenario_fleet", order_ref=order_ref, vehicle_id=vehicle_id)
        if vehicle_id is not None and vehicle is None:
            add("served_fields", "vehicle_missing_from_reference", order_ref=order_ref, vehicle_id=vehicle_id)
        if source is None or vehicle is None or fleet is None or trip_id is None:
            continue
        if fleet.get("scenario") != "S1" or fleet.get("status") != "available":
            add("home_depot_availability", "vehicle_not_available", order_ref=order_ref, vehicle_id=vehicle_id)
        if source["depot"] != vehicle["depot"]:
            add("home_depot_availability", "home_depot_mismatch", order_ref=order_ref, vehicle_id=vehicle_id)
        if source["temp_requirement"] == "chilled" and vehicle["temp"] != "reefer":
            add("refrigeration", "chilled_on_non_reefer", order_ref=order_ref, vehicle_id=vehicle_id)
        if source["parking_constraint"] == "van_only" and vehicle["type"] != "van":
            add("van_only", "van_only_on_non_van", order_ref=order_ref, vehicle_id=vehicle_id)
        served_records.append({"order_ref": order_ref, "vehicle_id": vehicle_id,
                               "trip_id": trip_id, "source": source, "vehicle": vehicle})

    for order_ref, count in working.loc[working["decision"].eq("served"), "order_ref"].astype(str).value_counts().items():
        if count != 1:
            add("whole_order", "served_order_not_exactly_once", order_ref=order_ref, occurrences=int(count))
    if allocation_rows:
        for order_ref, row in allocation_rows.items():
            if row["decision"] == "served" and (_blank(row["vehicle_id"]) or _trip_id(row["trip_id"]) is None):
                add("whole_order", "served_order_missing_single_assignment", order_ref=order_ref)

    grouped: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for record in served_records:
        grouped.setdefault((record["vehicle_id"], record["trip_id"]), []).append(record)
    tolerance = Decimal(str(config["numeric"]["tolerance"]))
    trip_rows: list[dict[str, Any]] = []
    budget_accumulator: dict[str, dict[str, Any]] = {}
    for (vehicle_id, trip_id), records in sorted(grouped.items()):
        brands = {record["source"]["brand"] for record in records}
        districts = {record["source"]["district"] for record in records}
        if len(brands) != 1:
            add("same_brand_district", "mixed_brand", vehicle_id=vehicle_id, trip_id=trip_id)
        if len(districts) != 1:
            add("same_brand_district", "mixed_district", vehicle_id=vehicle_id, trip_id=trip_id)
        vehicle = records[0]["vehicle"]
        try:
            weight = sum((_decimal(record["source"]["order_weight_kg"]) for record in records), Decimal(0))
            volume = sum((_decimal(record["source"]["order_volume_m3"]) for record in records), Decimal(0))
            if weight > _decimal(vehicle["weight_cap_kg"]):
                add("capacity", "weight_exceeded", vehicle_id=vehicle_id, trip_id=trip_id)
            if volume > _decimal(vehicle["volume_cap_m3"]):
                add("capacity", "volume_exceeded", vehicle_id=vehicle_id, trip_id=trip_id)
        except AllocationValidationError:
            add("capacity", "invalid_numeric_capacity", vehicle_id=vehicle_id, trip_id=trip_id)
        if len(brands) != 1 or len(districts) != 1:
            continue
        brand = next(iter(brands))
        district = next(iter(districts))
        source_orders = pd.DataFrame([record["source"] for record in records])
        try:
            breakdown = calculate_trip_time(source_orders, district_travel_ref, service_allowance_ref)
            travel = district_travel_ref.loc[
                district_travel_ref["depot"].eq(source_orders["depot"].iloc[0])
                & district_travel_ref["district"].eq(district)
            ]
            if len(travel) != 1:
                raise AllocationValidationError("Trip travel reference is missing or duplicated.")
            outbound = _decimal(travel["depot_to_district_freeflow_min"].iloc[0])
            inter_stop = _decimal(travel["inter_stop_freeflow_min"].iloc[0]) * (len(records) - 1)
            handling = Decimal(0)
            for record in records:
                source = record["source"]
                allowance = service_allowance_ref.loc[
                    service_allowance_ref["brand"].eq(source["brand"])
                    & service_allowance_ref["dock_type"].eq(source["dock_type"])
                ]
                if len(allowance) != 1:
                    raise AllocationValidationError("Service allowance is missing or duplicated.")
                handling += _decimal(allowance["service_allowance_min"].iloc[0])
            exact_minutes = outbound + inter_stop + handling
            component_values = (
                (_decimal(breakdown.outbound_minutes), outbound),
                (_decimal(breakdown.inter_stop_minutes), inter_stop),
                (_decimal(breakdown.handling_minutes), handling),
                (_decimal(breakdown.trip_minutes), exact_minutes),
            )
            calculation_ok = breakdown.return_minutes_added == 0 and all(
                abs(actual - expected) <= tolerance for actual, expected in component_values
            )
            if not calculation_ok:
                add("trip_time_exact", "phase20_time_mismatch", vehicle_id=vehicle_id, trip_id=trip_id)
            trip_rows.append({
                "vehicle_id": vehicle_id, "trip_id": trip_id, "brand": brand,
                "district": district, "order_count": len(records),
                "outbound_minutes": str(outbound), "inter_stop_minutes": str(inter_stop),
                "handling_minutes": str(handling), "trip_minutes": str(exact_minutes),
                "return_minutes_added": str(breakdown.return_minutes_added),
                "time_calculation_ok": calculation_ok,
            })
            accumulator = budget_accumulator.setdefault(vehicle_id, {
                "trips": set(), "fresh_count": 0, "style_count": 0, "tech_count": 0,
                "fresh_minutes": Decimal(0), "style_tech_minutes": Decimal(0),
            })
            accumulator["trips"].add(trip_id)
            if brand == "Fresh":
                accumulator["fresh_count"] += 1
                accumulator["fresh_minutes"] += exact_minutes
            elif brand in ("Style", "Tech"):
                accumulator[f"{brand.lower()}_count"] += 1
                accumulator["style_tech_minutes"] += exact_minutes
            else:
                add("trip_count_time_budget", "unsupported_brand", vehicle_id=vehicle_id, trip_id=trip_id)
        except Exception as exc:
            add("trip_time_exact", "trip_time_calculation_failed", vehicle_id=vehicle_id,
                trip_id=trip_id, error_type=type(exc).__name__)

    budget_rows: list[dict[str, Any]] = []
    fresh_limit = Decimal(str(config["time"]["fresh_budget_min"]))
    style_tech_limit = Decimal(str(config["time"]["style_tech_budget_min"]))
    for vehicle_id, values in sorted(budget_accumulator.items()):
        trip_count = len(values["trips"])
        fresh_ok = values["fresh_minutes"] <= fresh_limit
        style_tech_ok = values["style_tech_minutes"] <= style_tech_limit
        if trip_count > 2:
            add("trip_count_time_budget", "more_than_two_trips", vehicle_id=vehicle_id)
        if not fresh_ok:
            add("trip_count_time_budget", "fresh_budget_exceeded", vehicle_id=vehicle_id)
        if not style_tech_ok:
            add("trip_count_time_budget", "style_tech_budget_exceeded", vehicle_id=vehicle_id)
        budget_rows.append({
            "vehicle_id": vehicle_id, "trip_count": trip_count,
            "fresh_trip_count": values["fresh_count"], "fresh_minutes": str(values["fresh_minutes"]),
            "fresh_budget_min": str(fresh_limit), "fresh_budget_ok": fresh_ok,
            "style_trip_count": values["style_count"], "tech_trip_count": values["tech_count"],
            "style_tech_minutes": str(values["style_tech_minutes"]),
            "style_tech_budget_min": str(style_tech_limit), "style_tech_budget_ok": style_tech_ok,
            "overall_budget_ok": trip_count <= 2 and fresh_ok and style_tech_ok,
        })

    if frozen_trip_summary is not None:
        stored = frozen_trip_summary.copy(deep=True)
        required = {"vehicle_id", "trip_id", "trip_minutes"}
        missing = required.difference(stored.columns)
        if missing:
            add("trip_time_exact", "stored_trip_summary_missing_columns", columns=sorted(missing))
        else:
            stored_values: dict[tuple[str, int], Decimal] = {}
            for index, row in enumerate(stored.to_dict("records")):
                vehicle_id = None if _blank(row["vehicle_id"]) else _key(row["vehicle_id"])
                trip_id = _trip_id(row["trip_id"])
                if vehicle_id is None or trip_id is None:
                    add("trip_time_exact", "stored_trip_summary_invalid_key", row_index=index)
                    continue
                key = (vehicle_id, trip_id)
                if key in stored_values:
                    add("trip_time_exact", "stored_trip_summary_duplicate_key",
                        vehicle_id=vehicle_id, trip_id=trip_id)
                    continue
                try:
                    stored_values[key] = _decimal(row["trip_minutes"])
                except AllocationValidationError:
                    add("trip_time_exact", "stored_trip_summary_invalid_minutes",
                        vehicle_id=vehicle_id, trip_id=trip_id)
            recomputed_values = {
                (_key(row["vehicle_id"]), int(row["trip_id"])): _decimal(row["trip_minutes"])
                for row in trip_rows
            }
            if set(stored_values) != set(recomputed_values):
                add("trip_time_exact", "stored_trip_summary_trip_set_mismatch",
                    stored_trip_count=len(stored_values), recomputed_trip_count=len(recomputed_values))
            for key in sorted(set(stored_values).intersection(recomputed_values)):
                if abs(stored_values[key] - recomputed_values[key]) > tolerance:
                    add("trip_time_exact", "stored_trip_minutes_mismatch",
                        vehicle_id=key[0], trip_id=key[1])

    task_ids = {
        "allocation_schema": "DT-320", "scenario_values": "DT-321",
        "order_ref_coverage": "DT-322", "decision_domain": "DT-323",
        "served_fields": "DT-324", "deferred_fields": "DT-325",
        "trip_id_domain": "DT-326", "same_brand_district": "DT-327",
        "refrigeration": "DT-327", "van_only": "DT-327",
        "home_depot_availability": "DT-327", "whole_order": "DT-327",
        "capacity": "DT-327", "trip_time_exact": "DT-328",
        "trip_count_time_budget": "DT-327/DT-328",
    }
    rules = {
        name: RuleResult(name, task_ids[name], "PASS" if not violations[name] else "FAIL",
                         len(violations[name]), "No violations." if not violations[name]
                         else f"{len(violations[name])} violation(s) detected.")
        for name in RULE_IDS
    }
    overall = "PASS" if all(result.status == "PASS" for result in rules.values()) else "FAIL"
    return AllocationValidationReport(
        overall, rules, violations,
        pd.DataFrame(trip_rows, columns=TRIP_AUDIT_COLUMNS),
        pd.DataFrame(budget_rows, columns=VEHICLE_BUDGET_COLUMNS),
        checked_order_count=len(working), checked_vehicle_count=len(budget_accumulator),
        checked_trip_count=len(grouped), warnings=[],
    )


def build_official_checker_candidate(allocation: pd.DataFrame,
                                     canonical_orders_s1: pd.DataFrame) -> pd.DataFrame:
    """Create the exact private six-column checker input without changing decisions."""
    missing_columns = set(ALLOCATION_COLUMNS).difference(allocation.columns)
    if missing_columns:
        raise AllocationValidationError("Frozen allocation is missing required official columns.")
    official = allocation.loc[:, ALLOCATION_COLUMNS].copy()
    if official["order_ref"].map(_blank).any() or official["order_ref"].duplicated().any():
        raise AllocationValidationError("Frozen allocation order keys are invalid.")
    source = canonical_orders_s1[["scenario", "order_ref", "outlet_id"]].copy()
    if source["order_ref"].map(_blank).any() or source["order_ref"].duplicated().any():
        raise AllocationValidationError("Canonical order keys are invalid.")
    merged = official.merge(source, on="order_ref", how="outer", suffixes=("", "_source"),
                            indicator=True, validate="one_to_one")
    if not merged["_merge"].eq("both").all():
        raise AllocationValidationError("Checker candidate order coverage is not exact.")
    if not merged["scenario"].eq(merged["scenario_source"]).all() or not merged["outlet_id"].astype(str).eq(
        merged["outlet_id_source"].astype(str)
    ).all():
        raise AllocationValidationError("Checker candidate identity differs from canonical S1.")
    if not merged["decision"].isin(["served", "deferred"]).all():
        raise AllocationValidationError("Checker candidate has an invalid decision.")
    rows = []
    for row in merged.to_dict("records"):
        if row["decision"] == "served":
            trip_id = _trip_id(row["trip_id"])
            if _blank(row["vehicle_id"]) or trip_id is None:
                raise AllocationValidationError("Served checker row is incomplete.")
            vehicle_id = row["vehicle_id"]
        else:
            if not _blank(row["vehicle_id"]) or not _blank(row["trip_id"]):
                raise AllocationValidationError("Deferred checker row is not blank.")
            vehicle_id, trip_id = "", ""
        rows.append({
            "scenario": row["scenario_source"], "order_ref": row["order_ref"],
            "outlet_id": row["outlet_id_source"], "decision": row["decision"],
            "vehicle_id": vehicle_id, "trip_id": trip_id,
        })
    candidate = pd.DataFrame(rows, columns=ALLOCATION_COLUMNS)
    return candidate.reset_index(drop=True)
