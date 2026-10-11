"""Strict public request and response models for the integration boundary."""

from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.integration import CONTRACT_VERSION, SCHEMA_VERSION
from src.task2b.reason_codes import REASON_CLASSES, REASON_TAXONOMY


SourceMode = Literal["synthetic_demo", "private_local"]
Brand = Literal["Fresh", "Style", "Tech"]
Availability = Literal["available", "not_available", "synthetic_demo"]
ReasonClass = Literal["UNAVOIDABLE_HARD", "POLICY_TRADEOFF", "ALTERNATIVE_OPTIMUM"]

DEMAND_SCHEMA_CONDITIONALS = {
    "allOf": [
        {
            "if": {
                "properties": {"brand": {"enum": ["Style", "Tech"]}},
                "required": ["brand"],
            },
            "then": {
                "properties": {"pred_chilled_volume_m3": {"const": 0}},
            },
        },
    ],
    "x-wayloom-semantic-rules": [
        "pred_chilled_volume_m3 <= pred_total_volume_m3",
    ],
}

ALLOCATION_SCHEMA_METADATA = {
    "x-wayloom-semantic-rules": [
        "orders_served + orders_deferred == orders_total",
    ],
}

DEFERRAL_SCHEMA_CONDITIONALS = {
    "allOf": [
        {
            "if": {
                "properties": {"availability": {"const": "not_available"}},
                "required": ["availability"],
            },
            "then": {
                "properties": {
                    "reason_class": {"type": "null"},
                    "primary_reason_code": {"type": "null"},
                    "secondary_reason_codes": {
                        "anyOf": [
                            {"type": "null"},
                            {"type": "array", "maxItems": 0},
                        ],
                    },
                    "evidence": {"type": "null"},
                },
            },
        },
        {
            "if": {
                "properties": {"availability": {"const": "available"}},
                "required": ["availability"],
            },
            "then": {
                "required": ["reason_class", "primary_reason_code", "summary", "evidence"],
                "properties": {
                    "reason_class": {"enum": list(REASON_CLASSES)},
                    "primary_reason_code": {"enum": list(REASON_TAXONOMY)},
                    "summary": {"type": "string", "minLength": 1},
                    "evidence": {"not": {"type": "null"}},
                },
            },
        },
        {
            "if": {
                "properties": {"availability": {"const": "synthetic_demo"}},
                "required": ["availability"],
            },
            "then": {
                "required": ["reason_class", "primary_reason_code", "summary", "evidence"],
                "properties": {
                    "source_mode": {"const": "synthetic_demo"},
                    "reason_class": {"enum": list(REASON_CLASSES)},
                    "primary_reason_code": {"enum": list(REASON_TAXONOMY)},
                    "summary": {"type": "string", "minLength": 1},
                    "evidence": {"not": {"type": "null"}},
                },
            },
        },
    ],
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DeliveryRiskRequest(StrictModel):
    delivery_ref: str = Field(pattern=r"^DEMO_DELIVERY_[0-9]{3}$")
    route_distance_km: float = Field(ge=0, le=1000)
    planned_arrival_hour: int = Field(ge=0, le=23)
    dock_type: Literal["standard", "restricted"] = "standard"

    @model_validator(mode="after")
    def finite_distance(self) -> "DeliveryRiskRequest":
        if not math.isfinite(self.route_distance_km):
            raise ValueError("route_distance_km must be finite")
        return self


class Task1Prediction(StrictModel):
    pred_service_min: float = Field(ge=0)
    pred_late_prob: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def finite_values(self) -> "Task1Prediction":
        if not math.isfinite(self.pred_service_min) or not math.isfinite(self.pred_late_prob):
            raise ValueError("prediction values must be finite")
        return self


class Task1ModelStatus(StrictModel):
    service_model: Literal["synthetic", "loaded"]
    late_model: Literal["synthetic", "loaded"]


class Task1Response(StrictModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    source_mode: SourceMode
    delivery_ref: str = Field(pattern=r"^DEMO_DELIVERY_[0-9]{3}$")
    prediction: Task1Prediction
    model_status: Task1ModelStatus


class DemandForecastRequest(StrictModel):
    depot: Literal["Demo Depot", "Demo North Hub"]
    brand: Brand
    iso_year: int = Field(ge=2020, le=2100)
    iso_week: int = Field(ge=1, le=53)
    forecast_horizon: int = Field(default=1, ge=1, le=10)


class ForecastUncertainty(StrictModel):
    status: Literal["unofficial"] = "unofficial"
    target_coverage: float = Field(gt=0, lt=1)
    total_lower_m3: float = Field(ge=0)
    total_upper_m3: float = Field(ge=0)

    @model_validator(mode="after")
    def ordered(self) -> "ForecastUncertainty":
        if not all(math.isfinite(v) for v in (self.target_coverage, self.total_lower_m3, self.total_upper_m3)):
            raise ValueError("uncertainty values must be finite")
        if self.total_lower_m3 > self.total_upper_m3:
            raise ValueError("uncertainty bounds are reversed")
        return self


class DemandForecastResponse(StrictModel):
    model_config = ConfigDict(json_schema_extra=DEMAND_SCHEMA_CONDITIONALS)

    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    source_mode: SourceMode
    forecast_ref: str = Field(pattern=r"^DEMO_FORECAST_[0-9]{3}$")
    depot: str = Field(min_length=1, max_length=80)
    brand: Brand
    iso_year: int = Field(ge=2020, le=2100)
    iso_week: int = Field(ge=1, le=53)
    forecast_horizon: int = Field(ge=1, le=10)
    pred_total_volume_m3: float = Field(ge=0)
    pred_chilled_volume_m3: float = Field(ge=0)
    uncertainty: ForecastUncertainty | None = None

    @model_validator(mode="after")
    def demand_invariants(self) -> "DemandForecastResponse":
        values = (self.pred_total_volume_m3, self.pred_chilled_volume_m3)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("forecast values must be finite")
        if self.pred_chilled_volume_m3 > self.pred_total_volume_m3:
            raise ValueError("chilled forecast cannot exceed total forecast")
        if self.brand in {"Style", "Tech"} and self.pred_chilled_volume_m3 != 0:
            raise ValueError("Style and Tech chilled forecasts must be zero")
        if self.uncertainty and self.uncertainty.total_upper_m3 < self.pred_total_volume_m3:
            raise ValueError("upper uncertainty bound cannot be below the point forecast")
        return self


class AllocationInsightRequest(StrictModel):
    scenario_ref: Literal["DEMO_SCENARIO_01"]


class AllocationSummary(StrictModel):
    orders_total: int = Field(ge=0)
    orders_served: int = Field(ge=0)
    orders_deferred: int = Field(ge=0)
    vehicles_used: int = Field(ge=0)
    trips_used: int = Field(ge=0)

    @model_validator(mode="after")
    def counts_balance(self) -> "AllocationSummary":
        if self.orders_served + self.orders_deferred != self.orders_total:
            raise ValueError("served and deferred counts must sum to total")
        return self


class ConstraintSummary(StrictModel):
    max_trips_per_vehicle: Literal[2] = 2
    fresh_vehicle_minutes_limit: Literal[270] = 270
    style_tech_vehicle_minutes_limit: Literal[480] = 480


class AllocationReasoning(StrictModel):
    policy_name: Literal["WayLoom lexicographic allocation policy"]
    policy_origin: Literal["WayLoom engineering policy"]
    hard_rules_precede_policy: Literal[True]


class AllocationInsightResponse(StrictModel):
    model_config = ConfigDict(json_schema_extra=ALLOCATION_SCHEMA_METADATA)

    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    source_mode: SourceMode
    scenario_ref: Literal["DEMO_SCENARIO_01"]
    summary: AllocationSummary
    constraint_summary: ConstraintSummary
    reasoning: AllocationReasoning
    deferral_example_refs: list[str] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def synthetic_refs(self) -> "AllocationInsightResponse":
        if any(not ref.startswith("DEFERRAL_EXAMPLE_") for ref in self.deferral_example_refs):
            raise ValueError("deferral references must be synthetic")
        return self


class DeferralEvidence(StrictModel):
    counterfactual_complete: bool
    first_degraded_policy_tier: str | None = Field(default=None, pattern=r"^LEVEL_[1-9][A-C]?$|^HARD_FEASIBILITY$")
    changed_order_count: int | None = Field(default=None, ge=0)


class DeferralExplanationResponse(StrictModel):
    model_config = ConfigDict(json_schema_extra=DEFERRAL_SCHEMA_CONDITIONALS)

    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    source_mode: SourceMode
    example_ref: str = Field(pattern=r"^DEFERRAL_EXAMPLE_[A-Z]$")
    availability: Availability
    reason_class: ReasonClass | None = None
    primary_reason_code: str | None = None
    secondary_reason_codes: list[str] | None = None
    summary: str | None = Field(default=None, max_length=500)
    evidence: DeferralEvidence | None = None
    limitations: str = Field(min_length=20, max_length=500)

    @model_validator(mode="after")
    def explanation_consistency(self) -> "DeferralExplanationResponse":
        if self.availability == "not_available":
            if any(value is not None for value in (
                self.reason_class, self.primary_reason_code, self.evidence,
            )):
                raise ValueError("unavailable explanations cannot contain fabricated reason evidence")
            if self.secondary_reason_codes not in (None, []):
                raise ValueError("unavailable explanations cannot contain secondary reasons")
            if self.summary is not None and not self.summary:
                raise ValueError("unavailable explanation summary cannot be blank")
            return self
        if not all((self.reason_class, self.primary_reason_code, self.summary, self.evidence)):
            raise ValueError("available explanations require structured reason evidence")
        if self.reason_class not in REASON_CLASSES:
            raise ValueError("unknown reason class")
        codes = [self.primary_reason_code, *(self.secondary_reason_codes or [])]
        if len(codes) != len(set(codes)) or any(code not in REASON_TAXONOMY for code in codes):
            raise ValueError("unknown or duplicate reason code")
        if any(self.reason_class not in REASON_TAXONOMY[code].allowed_classes for code in codes):
            raise ValueError("reason code is incompatible with reason class")
        return self


class ModelLoadRequest(StrictModel):
    load: Literal[True] = True


class ModelStates(StrictModel):
    task1_service: Literal["not_loaded", "loaded", "synthetic", "error"]
    task1_late: Literal["not_loaded", "loaded", "synthetic", "error"]
    task2a_total: Literal["not_loaded", "loaded", "synthetic", "error"]
    task2a_chilled_or_pipeline: Literal["not_loaded", "loaded", "synthetic", "error"]


class ModelLoadResponse(StrictModel):
    mode: SourceMode
    action: Literal["loaded", "already_loaded"]
    real_models_loaded: bool
    models: ModelStates


class HealthResponse(StrictModel):
    status: Literal["ok"] = "ok"
    service: Literal["wayloom-integration"] = "wayloom-integration"
    contract_version: Literal[CONTRACT_VERSION] = CONTRACT_VERSION
    mode: SourceMode


class ContractResponse(StrictModel):
    contract_version: Literal[CONTRACT_VERSION] = CONTRACT_VERSION
    schema_versions: dict[str, Literal[SCHEMA_VERSION]]
    available_endpoints: list[str]
    mode: SourceMode
    integration_status: Literal["optional_shared"] = "optional_shared"
    privacy_statement: str


class ErrorDetail(StrictModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(StrictModel):
    error: ErrorDetail
