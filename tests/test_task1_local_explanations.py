from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src.task1.explainability import (
    build_explanation_registry,
    lateness_probability_bridge,
    local_contributors,
    select_late_example,
    select_service_example,
    service_prediction_bridge,
)
from src.task1.final_train import fit_frozen_calibrator
from src.task1.shap_adapter import ShapResult


class ProbabilityModel:
    classes_ = np.array([0, 1])

    def predict_proba(self, frame):
        p = np.clip(np.asarray(frame["x"], dtype=float), 0.01, 0.99)
        return np.column_stack([1.0 - p, p])


def test_local_selectors_are_deterministic_with_original_position_ties() -> None:
    assert select_service_example(np.array([1.0, 2.0, 2.0, 3.0])) == 1
    assert select_late_example(np.array([0.2, 0.9, 0.9, 0.4])) == 1


def test_local_contributors_split_positive_negative_without_identifier() -> None:
    frame = pd.DataFrame({"a": [1.0], "b": [2.0], "c": [3.0]})
    result = ShapResult(
        values=np.array([[0.4, -0.7, 0.0]]), base_values=np.array([1.0]),
        raw_predictions=np.array([0.7]), method="synthetic", output_space="raw_service_prediction",
        max_abs_reconstruction_error=0.0, reconstruction_pass=True,
    )
    output = local_contributors(
        result, frame, row_position=0, registry=build_explanation_registry(list(frame.columns)),
        top_positive=2, top_negative=2,
    )
    assert output["top_positive_contributors"][0]["feature_name"] == "a"
    assert output["top_negative_contributors"][0]["feature_name"] == "b"
    assert "delivery_id" not in str(output)


def test_service_postprocessing_bridge_keeps_raw_separate_from_final() -> None:
    final, report = service_prediction_bridge(np.array([-2.0, 4.0]), "clip_to_zero")
    np.testing.assert_allclose(final, [0.0, 4.0])
    assert report["postprocessed_count"] == 1
    unchanged, report = service_prediction_bridge(np.array([2.0]), "fail")
    np.testing.assert_allclose(unchanged, [2.0])
    assert report["postprocessing_policy"] == "noop_no_negatives"


def test_raw_and_calibrated_lateness_bridges() -> None:
    frame = pd.DataFrame({"x": [0.2, 0.8]})
    raw_bundle = {
        "model": ProbabilityModel(),
        "metadata": {"positive_class_index": 1, "calibration_method": "raw"},
        "calibration": None,
    }
    raw = lateness_probability_bridge(raw_bundle, frame)
    np.testing.assert_allclose(raw["base_probability"], raw["final_probability"])
    calibration_x = np.linspace(0.05, 0.95, 30)
    calibration_y = (calibration_x > 0.6).astype(float)
    calibrator = fit_frozen_calibrator("sigmoid", calibration_x, calibration_y)
    calibrated_bundle = {
        "model": ProbabilityModel(),
        "metadata": {"positive_class_index": 1, "calibration_method": "sigmoid"},
        "calibration": calibrator,
    }
    calibrated = lateness_probability_bridge(calibrated_bundle, frame)
    assert calibrated["calibration_applied"] is True
    assert not np.allclose(calibrated["base_probability"], calibrated["final_probability"])
    assert ((calibrated["final_probability"] >= 0) & (calibrated["final_probability"] <= 1)).all()
