from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.task1.causal_language import has_noncausal_disclaimer
from src.task1.explainability import (
    ExplainabilityError,
    assert_hashes_unchanged,
    audit_explanation_schema,
    build_explanation_registry,
    hash_artifacts,
    prepare_frozen_model_frame,
)
from src.task1.explanation_reporting import build_business_drivers


def _schema(features: list[str]) -> dict:
    return {"feature_columns": features, "categorical_columns": [], "feature_profile": "test"}


def test_hash_guard_detects_change_and_accepts_unchanged(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"frozen")
    before = hash_artifacts([artifact], root=tmp_path)
    assert_hashes_unchanged(before, hash_artifacts([artifact], root=tmp_path))
    artifact.write_bytes(b"changed")
    with pytest.raises(ExplainabilityError, match="hash changed"):
        assert_hashes_unchanged(before, hash_artifacts([artifact], root=tmp_path))


@pytest.mark.parametrize("forbidden", ["actual_depart_time", "actual_travel_duration_min", "arrival_time", "leave_outlet_time", "service_minutes", "late_flag"])
def test_forbidden_actual_or_target_in_schema_is_hard_failure(forbidden: str) -> None:
    features = ["safe", forbidden]
    with pytest.raises(ExplainabilityError, match="Forbidden"):
        audit_explanation_schema(_schema(features), _schema(features), build_explanation_registry(features))


def test_schema_parity_and_registry_completeness_are_required() -> None:
    registry = build_explanation_registry(["a", "b"])
    with pytest.raises(ExplainabilityError, match="match exactly"):
        audit_explanation_schema(_schema(["a", "b"]), _schema(["b", "a"]), registry)
    with pytest.raises(Exception):
        audit_explanation_schema(_schema(["a", "b"]), _schema(["a", "b"]), registry.iloc[:1])


def test_explanation_frame_uses_saved_order_and_ignores_nonmodel_columns() -> None:
    bundle = {
        "schema": {
            "feature_columns": ["a", "b"],
            "categorical_columns": ["b"],
            "feature_profile": "test",
            "missing_category_token": "__MISSING__",
        },
        "metadata": {"model_family": "catboost"},
    }
    population = pd.DataFrame({
        "unused_context": [99],
        "b": [None],
        "a": [1.0],
    })
    aligned = prepare_frozen_model_frame(bundle, population)
    assert aligned.columns.tolist() == ["a", "b"]
    assert aligned.loc[0, "b"] == "__MISSING__"


def test_business_drivers_only_use_final_features_and_do_not_infer_direction() -> None:
    importance = pd.DataFrame({
        "feature_name": ["a", "b"], "rank": [1, 2], "importance": [0.8, 0.2],
        "importance_type": ["native", "native"], "semantic_group": ["other_prediction_time_context"] * 2,
    })
    shap = pd.DataFrame({
        "feature_name": ["a", "b"], "rank": [1, 2], "mean_abs_shap": [0.5, 0.1],
        "direction_statement": ["context-dependent/not inferred from mean absolute SHAP"] * 2,
        "semantic_group": ["other_prediction_time_context"] * 2,
    })
    drivers = build_business_drivers("service", importance, shap, top_n=2)
    assert {item["driver"] for item in drivers} == {"a", "b"}
    assert all("context-dependent" in item["interpretation"] for item in drivers)
    assert all("not evidence of a causal effect" in item["causal_caution"] for item in drivers)


def test_tracked_docs_have_disclaimer_and_config_forbids_external_api() -> None:
    text = Path("docs/task1_explainability.md").read_text(encoding="utf-8")
    assert has_noncausal_disclaimer(text)
    config = yaml.safe_load(Path("configs/task1_explainability.yaml").read_text(encoding="utf-8"))
    assert config["privacy"]["external_api_allowed"] is False
    assert config["feature_pipeline"]["prefer_frozen_materialized_features"] is True
    assert config["feature_pipeline"]["frozen_test_features"] == "data/interim/task1_features_test.csv"
    assert not any("phase26" in path.name.lower() for path in Path("src").rglob("*") if path.is_file())
