"""Optional local FastAPI service for the synthetic integration contract."""

from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.integration import CONTRACT_VERSION, SCHEMA_VERSION
from src.integration.model_registry import ModelRegistry, ModelRegistryError
from src.integration.models import (
    AllocationInsightRequest,
    AllocationInsightResponse,
    ContractResponse,
    DeliveryRiskRequest,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    ModelLoadRequest,
    ModelLoadResponse,
    Task1Response,
    DemandForecastRequest,
    DemandForecastResponse,
    DeferralExplanationResponse,
)
from src.integration.synthetic_data import (
    allocation_insight,
    deferral_explanations,
    delivery_risk,
    demand_forecast,
)


LOGGER = logging.getLogger("wayloom.integration")
DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "integration.yaml"
ROUTES = (
    "GET /health",
    "GET /v1/contract",
    "POST /v1/models/load",
    "POST /v1/delivery-risk",
    "POST /v1/demand-forecast",
    "POST /v1/allocation-insight",
    "GET /v1/demo/deferral-explanations",
)


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    if config.get("version") != 1 or config.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("Unsupported integration configuration version.")
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported integration schema version.")
    if config.get("mode") not in {"synthetic_demo", "private_local"}:
        raise ValueError("Unsupported integration mode.")
    privacy = config.get("privacy") or {}
    if config.get("mode") == "synthetic_demo" and (
        privacy.get("allow_competition_records") is not False
        or privacy.get("allow_private_paths") is not False
        or privacy.get("log_request_bodies") is not False
        or privacy.get("log_response_bodies") is not False
    ):
        raise ValueError("Synthetic mode must use the fail-closed privacy configuration.")
    origins = (config.get("network") or {}).get("cors_allow_origins")
    if not isinstance(origins, list) or "*" in origins:
        raise ValueError("CORS origins must be an explicit non-wildcard list.")


def _error(status: int, code: str, request_id: str) -> JSONResponse:
    payload = ErrorResponse(error=ErrorDetail(
        code=code,
        message="Request does not match the integration contract." if status < 500
        else "The request could not be completed safely.",
        request_id=request_id,
    ))
    return JSONResponse(status_code=status, content=payload.model_dump(mode="json"))


def create_app(config: dict[str, Any] | None = None) -> FastAPI:
    active = dict(config) if config is not None else load_config()
    validate_config(active)
    mode = active["mode"]
    seed = int((active.get("synthetic") or {}).get("seed", 42))
    registry = ModelRegistry(active)

    app = FastAPI(
        title="WayLoom Synthetic Integration",
        version=CONTRACT_VERSION,
        description="Optional, synthetic-only local engineering contract; not an official submission interface.",
    )
    app.state.integration_config = active
    app.state.model_registry = registry

    origins = (active.get("network") or {}).get("cors_allow_origins", [])
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "X-Request-ID"],
        )

    @app.middleware("http")
    async def safe_metadata_logging(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id
        started = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        LOGGER.info(
            "method=%s route=%s status=%s latency_ms=%s mode=%s request_id=%s",
            request.method, request.url.path, response.status_code, latency_ms, mode, request_id,
        )
        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def request_validation_error(request: Request, _error_value: RequestValidationError):
        return _error(422, "INVALID_REQUEST", request.state.request_id)

    @app.exception_handler(ModelRegistryError)
    async def registry_error(request: Request, _error_value: ModelRegistryError):
        return _error(503, "MODEL_UNAVAILABLE", request.state.request_id)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, _error_value: Exception):
        return _error(500, "INTERNAL_ERROR", getattr(request.state, "request_id", uuid.uuid4().hex))

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(mode=mode)

    @app.get("/v1/contract", response_model=ContractResponse)
    def contract() -> ContractResponse:
        return ContractResponse(
            schema_versions={
                "task1": SCHEMA_VERSION,
                "demand_forecast": SCHEMA_VERSION,
                "allocation_insight": SCHEMA_VERSION,
                "deferral_explanation": SCHEMA_VERSION,
            },
            available_endpoints=list(ROUTES),
            mode=mode,
            privacy_statement="Synthetic responses only; official competition records are never served.",
        )

    @app.post("/v1/models/load", response_model=ModelLoadResponse)
    def load_models(_request: ModelLoadRequest) -> ModelLoadResponse:
        return registry.load()

    @app.post("/v1/delivery-risk", response_model=Task1Response)
    def delivery_endpoint(request: DeliveryRiskRequest) -> Task1Response:
        if mode != "synthetic_demo":
            raise ModelRegistryError("Private prediction adapter is unavailable.")
        return delivery_risk(request, seed=seed)

    @app.post("/v1/demand-forecast", response_model=DemandForecastResponse)
    def demand_endpoint(request: DemandForecastRequest) -> DemandForecastResponse:
        if mode != "synthetic_demo":
            raise ModelRegistryError("Private forecast adapter is unavailable.")
        return demand_forecast(request, seed=seed)

    @app.post("/v1/allocation-insight", response_model=AllocationInsightResponse)
    def allocation_endpoint(request: AllocationInsightRequest) -> AllocationInsightResponse:
        if mode != "synthetic_demo":
            raise ModelRegistryError("Private allocation adapter is unavailable.")
        return allocation_insight(request)

    @app.get("/v1/demo/deferral-explanations", response_model=list[DeferralExplanationResponse])
    def deferral_endpoint() -> list[DeferralExplanationResponse]:
        return deferral_explanations()

    return app
