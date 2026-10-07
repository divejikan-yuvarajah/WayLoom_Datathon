import math

import pytest
from pydantic import ValidationError

from src.integration.models import (
    AllocationInsightResponse,
    DeferralExplanationResponse,
    DemandForecastResponse,
    Task1Response,
)
from src.integration.synthetic_data import LIMITATION


def task1(**prediction):
    values = {"pred_service_min": 18.4, "pred_late_prob": 0.27, **prediction}
    return Task1Response(
        source_mode="synthetic_demo",
        delivery_ref="DEMO_DELIVERY_001",
        prediction=values,
        model_status={"service_model": "synthetic", "late_model": "synthetic"},
    )


def test_task1_valid_and_numeric_bounds():
    assert task1().schema_version == "1.0"
    for invalid in (
        {"pred_service_min": -1},
        {"pred_late_prob": -0.01},
        {"pred_late_prob": 1.01},
        {"pred_service_min": math.inf},
    ):
        with pytest.raises(ValidationError):
            task1(**invalid)


@pytest.mark.parametrize("brand,chilled", [("Fresh", 4.0), ("Style", 0.0), ("Tech", 0.0)])
def test_demand_invariants(brand, chilled):
    result = DemandForecastResponse(
        source_mode="synthetic_demo", forecast_ref="DEMO_FORECAST_001",
        depot="Demo Depot", brand=brand, iso_year=2026, iso_week=42,
        forecast_horizon=1, pred_total_volume_m3=10, pred_chilled_volume_m3=chilled,
    )
    assert result.pred_chilled_volume_m3 <= result.pred_total_volume_m3


def test_demand_rejects_invalid_chilled_values():
    common = dict(
        source_mode="synthetic_demo", forecast_ref="DEMO_FORECAST_001",
        depot="Demo Depot", iso_year=2026, iso_week=42, forecast_horizon=1,
        pred_total_volume_m3=10,
    )
    with pytest.raises(ValidationError):
        DemandForecastResponse(brand="Fresh", pred_chilled_volume_m3=11, **common)
    with pytest.raises(ValidationError):
        DemandForecastResponse(brand="Style", pred_chilled_volume_m3=1, **common)
    with pytest.raises(ValidationError):
        DemandForecastResponse(brand="Tech", pred_chilled_volume_m3=-1, **common)


def test_allocation_counts_and_limits():
    valid = dict(
        source_mode="synthetic_demo", scenario_ref="DEMO_SCENARIO_01",
        summary={"orders_total": 4, "orders_served": 3, "orders_deferred": 1, "vehicles_used": 2, "trips_used": 2},
        constraint_summary={},
        reasoning={"policy_name": "WayLoom lexicographic allocation policy", "policy_origin": "WayLoom engineering policy", "hard_rules_precede_policy": True},
    )
    result = AllocationInsightResponse(**valid)
    assert result.constraint_summary.max_trips_per_vehicle == 2
    assert result.constraint_summary.fresh_vehicle_minutes_limit == 270
    assert result.constraint_summary.style_tech_vehicle_minutes_limit == 480
    valid["summary"] = {**valid["summary"], "orders_total": 5}
    with pytest.raises(ValidationError):
        AllocationInsightResponse(**valid)


def test_deferral_availability_and_version_contract():
    unavailable = DeferralExplanationResponse(
        source_mode="synthetic_demo", example_ref="DEFERRAL_EXAMPLE_A",
        availability="not_available", limitations=LIMITATION,
    )
    assert unavailable.reason_class is None
    with pytest.raises(ValidationError):
        DeferralExplanationResponse(
            source_mode="synthetic_demo", example_ref="DEFERRAL_EXAMPLE_A",
            availability="available", limitations=LIMITATION,
        )
    payload = task1().model_dump()
    payload["schema_version"] = "2.0"
    with pytest.raises(ValidationError):
        Task1Response.model_validate(payload)


def test_not_available_allows_only_safe_optional_summary_and_empty_secondary():
    result = DeferralExplanationResponse(
        source_mode="synthetic_demo", example_ref="DEFERRAL_EXAMPLE_A",
        availability="not_available", secondary_reason_codes=[],
        summary="A real explanation is not available in this mode.", limitations=LIMITATION,
    )
    assert result.reason_class is None and result.evidence is None
