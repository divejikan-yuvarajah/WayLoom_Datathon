from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.common.artifact_registry import load_artifact_registry, load_task2a_bundle
from src.task2a.final_fit import predict_frozen_component


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "models/artifact_registry.json"


def _synthetic_features(rows: int = 3) -> tuple[pd.DataFrame, dict]:
    schema = json.loads((ROOT / "models/task2a/feature_schema.json").read_text(encoding="utf-8"))
    categorical = set(schema["categorical_columns"])
    frame = pd.DataFrame(
        {
            column: (["synthetic"] * rows if column in categorical else np.arange(rows, dtype=float))
            for column in schema["feature_columns"]
        }
    )
    frame.insert(0, "row_id", [f"synthetic-{index}" for index in range(rows)])
    profile = {
        "profile_id": schema["feature_profile_id"],
        "columns": schema["feature_columns"],
        "categorical": schema["categorical_columns"],
        "numeric": [c for c in schema["feature_columns"] if c not in categorical],
    }
    return frame, profile


def test_task2a_actual_ensemble_roundtrip_preserves_synthetic_predictions(tmp_path: Path) -> None:
    registry = load_artifact_registry(REGISTRY, ROOT)
    bundle = load_task2a_bundle(registry, ROOT)
    features, profile = _synthetic_features()
    empty_history = pd.DataFrame()
    origin = pd.Timestamp("2026-01-01")
    for target in ("total", "chilled"):
        component = bundle[target]
        expected = predict_frozen_component(component, features, empty_history, origin, profile)
        path = tmp_path / f"{target}.joblib"
        joblib.dump(component, path)
        loaded = joblib.load(path)
        actual = predict_frozen_component(loaded, features, empty_history, origin, profile)
        np.testing.assert_allclose(actual, expected, rtol=0.0, atol=1e-12)


def test_task2a_bundle_is_complete_fixed_ensemble() -> None:
    registry = load_artifact_registry(REGISTRY, ROOT)
    bundle = load_task2a_bundle(registry, ROOT)
    assert bundle["total_metadata"]["candidate_id"] == "ensemble_cb_lgb_total_equal_v1"
    assert bundle["chilled_metadata"]["candidate_id"] == "ensemble_cb_lgb_chilled_equal_v1"
    assert bundle["schema"]["feature_profile_id"] == "task2a_advanced_safe_v1"
    assert bundle["manifest"]["forecast_horizon_weeks"] == 10
    assert bundle["manifest"]["postprocessing"]["style_chilled_zero"] is True
    assert bundle["manifest"]["postprocessing"]["tech_chilled_zero"] is True
    for target in ("total", "chilled"):
        component = bundle[target]
        assert component.spec["component_weights"] == [0.5, 0.5]
        assert component.components is not None and len(component.components) == 2
