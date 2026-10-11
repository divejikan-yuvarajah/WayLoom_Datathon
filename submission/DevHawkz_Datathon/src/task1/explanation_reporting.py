"""Privacy-safe reporting for Task 1 model explanations."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.task1.explainability import NONCAUSAL_DISCLAIMER


class ExplanationReportingError(ValueError):
    """Raised when an explanation report is incomplete or unsafe."""


GROUP_MEANINGS = {
    "chronology_safe_historical_behavior": "Patterns summarized only from strictly earlier historical outcomes.",
    "planned_time_and_slack": "Planned timing and delivery-window context available before execution.",
    "order_size_and_composition": "Planned order quantity, weight, volume, or composition context.",
    "route_position_and_planned_workload": "Planned route position and accumulated or total route workload.",
    "access_and_reference_service_context": "Outlet access constraints and reference handling allowances.",
    "vehicle_and_capacity_context": "Static vehicle attributes and planned capacity utilization.",
    "calendar_and_environment_context": "Calendar and pre-observed operating context.",
    "commercial_and_location_context": "Brand, depot, district, temperature, or location context.",
    "planned_travel_and_distance": "Planned distance, free-flow duration, or speed context.",
    "other_prediction_time_context": "Other feature context available at prediction time.",
}


def atomic_write_text(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(Path(path), json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def atomic_write_csv(path: Path, frame: pd.DataFrame) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        os.close(descriptor)
        frame.to_csv(temporary, index=False)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def build_business_drivers(model_name: str, importance: pd.DataFrame, shap_summary: pd.DataFrame,
                           *, top_n: int) -> list[dict[str, Any]]:
    if top_n <= 0:
        raise ExplanationReportingError("Business-driver top_n must be positive.")
    required_importance = {"feature_name", "rank", "importance", "semantic_group"}
    required_shap = {"feature_name", "rank", "mean_abs_shap", "direction_statement"}
    if not required_importance.issubset(importance.columns) or not required_shap.issubset(shap_summary.columns):
        raise ExplanationReportingError("Business-driver inputs are incomplete.")
    merged = shap_summary.merge(
        importance[["feature_name", "rank", "importance", "importance_type", "semantic_group"]],
        on="feature_name",
        how="left",
        validate="one_to_one",
        suffixes=("_shap", "_importance"),
    )
    if merged[["rank_importance", "importance"]].isna().any().any():
        raise ExplanationReportingError("Importance and SHAP features do not align.")
    rows: list[dict[str, Any]] = []
    disagreement_limit = max(5, int(np.ceil(len(merged) * 0.20)))
    for row in merged.sort_values(["rank_shap", "feature_name"], kind="stable").head(top_n).itertuples():
        group = str(row.semantic_group_shap)
        gap = abs(int(row.rank_shap) - int(row.rank_importance))
        rows.append({
            "driver": str(row.feature_name),
            "model": model_name,
            "global_shap_rank": int(row.rank_shap),
            "mean_abs_shap": float(row.mean_abs_shap),
            "native_importance_rank": int(row.rank_importance),
            "native_importance": float(row.importance),
            "importance_type": str(row.importance_type),
            "semantic_group": group,
            "business_meaning": GROUP_MEANINGS.get(group, GROUP_MEANINGS["other_prediction_time_context"]),
            "source_prediction_time_availability": "available under the frozen Phase 06/10 feature contract",
            "interpretation": (
                "The frozen model assigns material attribution to this feature on the explained population; "
                "direction is context-dependent unless separate distribution evidence is reviewed."
            ),
            "importance_shap_agreement": "DISAGREEMENT_REPORTED" if gap > disagreement_limit else "BROADLY_ALIGNED",
            "causal_caution": "This is a predictive model association, not evidence of a causal effect or guaranteed actionability.",
        })
    return rows


def _top_names(frame: pd.DataFrame, count: int = 5) -> str:
    return ", ".join(f"`{name}`" for name in frame.sort_values("rank").head(count)["feature_name"])


def render_public_summary(*, service_metadata: dict[str, Any], late_metadata: dict[str, Any],
                          service_shap: pd.DataFrame, late_shap: pd.DataFrame,
                          service_local: dict[str, Any], late_local: dict[str, Any],
                          sample_size: int) -> str:
    text = f"""# Task 1 Explainability

## What is explained

This summary describes the frozen `{service_metadata['model_family']}` service-time model and the frozen `{late_metadata['model_family']}` lateness classifier. Explanations use a deterministic local sample of {sample_size} Task 1 inference rows and the exact saved feature schema. No model was retrained or changed.

## Service-time model

The highest global mean-absolute-SHAP features were {_top_names(service_shap)}. Mean absolute SHAP measures attribution strength; it does not establish a universal direction. The private `{service_local['example_label']}` record reconstructs the raw model prediction before the frozen service post-processing policy.

## Late-risk model

The highest global mean-absolute-SHAP features were {_top_names(late_shap)}. Lateness SHAP values are reported in `{late_local['shap_output_space']}` for the base classifier and must not be read as probability-point changes. The private `{late_local['example_label']}` record separately verifies the bridge from the base classifier probability through calibration `{late_local['calibration_method']}` to the submitted probability.

## Business interpretation

“Driver” means a model driver or predictive association, not a causal driver. Feature rankings describe how the frozen models use the observed prediction-time information. Direction can be mixed or interaction-dependent, and operational actionability cannot be inferred from rank alone.

## Limitations

SHAP attribution can be distributed among correlated or redundant features. Feature importance is model-specific. A highly ranked feature is not necessarily actionable, and a low-ranked feature is not necessarily operationally unimportant. Categorical effects can depend on interactions and context.

{NONCAUSAL_DISCLAIMER}
"""
    assert_public_summary_private_id_free(text)
    return text


def render_private_report(*, manifest: dict[str, Any], service_importance: pd.DataFrame,
                          late_importance: pd.DataFrame, service_shap: pd.DataFrame,
                          late_shap: pd.DataFrame) -> str:
    return f"""# Phase 25 Task 1 Explainability Report

- Phase: {manifest['phase']}
- Service model: {manifest['service_model']['family']} / {manifest['service_model']['config_id']}
- Lateness model: {manifest['late_model']['family']} / {manifest['late_model']['config_id']}
- Explanation population: {manifest['explanation_population']['source']}
- SHAP sample size: {manifest['explanation_population']['sample_size']}
- Service SHAP space: {manifest['service_shap']['output_space']}
- Lateness SHAP space: {manifest['late_shap']['output_space']}
- Service top feature: {service_importance.iloc[0]['feature_name']}
- Lateness top feature: {late_importance.iloc[0]['feature_name']}
- Service top SHAP feature: {service_shap.iloc[0]['feature_name']}
- Lateness top SHAP feature: {late_shap.iloc[0]['feature_name']}

The detailed local explanation records use anonymous example labels and remain private.

{NONCAUSAL_DISCLAIMER}
"""


def assert_public_summary_private_id_free(text: str) -> None:
    forbidden = ("delivery_id=", "delivery_id:", "route_id=", "route_id:", "vehicle_id=", "vehicle_id:")
    lowered = str(text).lower()
    hits = [token for token in forbidden if token in lowered]
    if hits:
        raise ExplanationReportingError("Competition-facing summary exposes a private identifier field.")


def _plot_setup() -> Any:
    import matplotlib
    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt
    return plt


def plot_importance(frame: pd.DataFrame, path: Path, *, title: str, top_n: int) -> None:
    plt = _plot_setup()
    shown = frame.sort_values("rank").head(top_n).iloc[::-1]
    figure, axis = plt.subplots(figsize=(9, max(4, 0.32 * len(shown))))
    axis.barh(shown["feature_name"], shown["importance"], color="#3465a4")
    axis.set_title(title)
    axis.set_xlabel(str(shown["importance_type"].iloc[0]))
    figure.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=150)
    plt.close(figure)


def plot_shap_bar(summary: pd.DataFrame, path: Path, *, title: str, top_n: int) -> None:
    plt = _plot_setup()
    shown = summary.sort_values("rank").head(top_n).iloc[::-1]
    figure, axis = plt.subplots(figsize=(9, max(4, 0.32 * len(shown))))
    axis.barh(shown["feature_name"], shown["mean_abs_shap"], color="#75507b")
    axis.set_title(title)
    axis.set_xlabel("mean absolute SHAP")
    figure.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=150)
    plt.close(figure)


def plot_shap_distribution(values: np.ndarray, feature_names: list[str], summary: pd.DataFrame,
                           path: Path, *, title: str, top_n: int, seed: int) -> None:
    plt = _plot_setup()
    top = summary.sort_values("rank").head(top_n)["feature_name"].tolist()
    lookup = {name: index for index, name in enumerate(feature_names)}
    rng = np.random.default_rng(seed)
    figure, axis = plt.subplots(figsize=(9, max(4, 0.4 * len(top))))
    for display_position, name in enumerate(reversed(top)):
        shap_values = values[:, lookup[name]]
        jitter = rng.uniform(-0.14, 0.14, size=len(shap_values))
        axis.scatter(shap_values, display_position + jitter, s=10, alpha=0.55, color="#204a87")
    axis.axvline(0.0, color="black", linewidth=0.8)
    axis.set_yticks(range(len(top)), labels=list(reversed(top)))
    axis.set_xlabel("SHAP contribution in documented model-output space")
    axis.set_title(title)
    figure.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=150)
    plt.close(figure)


def plot_local_waterfall(local: dict[str, Any], path: Path, *, title: str) -> None:
    plt = _plot_setup()
    entries = list(local.get("top_positive_contributors", [])) + list(local.get("top_negative_contributors", []))
    entries = sorted(entries, key=lambda item: (abs(float(item["shap_value"])), item["feature_name"]))
    names = [item["feature_name"] for item in entries]
    values = [float(item["shap_value"]) for item in entries]
    colors = ["#4e9a06" if value >= 0 else "#cc0000" for value in values]
    figure, axis = plt.subplots(figsize=(9, max(4, 0.34 * len(entries))))
    axis.barh(names, values, color=colors)
    axis.axvline(0.0, color="black", linewidth=0.8)
    axis.set_xlabel("SHAP contribution in documented model-output space")
    axis.set_title(title)
    figure.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=150)
    plt.close(figure)
