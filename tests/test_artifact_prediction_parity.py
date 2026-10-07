from __future__ import annotations

import pandas as pd
import pytest

from src.artifacts.final_inference import FinalArtifactError, assert_prediction_parity


def test_strict_prediction_parity_preserves_identity_order_and_tolerance() -> None:
    expected = pd.DataFrame({"row_id": ["a", "b"], "prediction": [1.0, 2.0]})
    actual = pd.DataFrame({"row_id": ["a", "b"], "prediction": [1.0 + 1e-10, 2.0]})
    assert_prediction_parity(
        actual,
        expected,
        key="row_id",
        prediction_columns=("prediction",),
        tolerance=1e-9,
        require_order=True,
    )
    with pytest.raises(FinalArtifactError, match="order"):
        assert_prediction_parity(
            actual.iloc[::-1].reset_index(drop=True),
            expected,
            key="row_id",
            prediction_columns=("prediction",),
            tolerance=1e-9,
            require_order=True,
        )


def test_prediction_parity_rejects_missing_duplicate_and_beyond_tolerance() -> None:
    expected = pd.DataFrame({"row_id": ["a", "b"], "prediction": [1.0, 2.0]})
    cases = [
        pd.DataFrame({"row_id": ["a"], "prediction": [1.0]}),
        pd.DataFrame({"row_id": ["a", "a"], "prediction": [1.0, 1.0]}),
        pd.DataFrame({"row_id": ["a", "b"], "prediction": [1.1, 2.0]}),
    ]
    for actual in cases:
        with pytest.raises(FinalArtifactError):
            assert_prediction_parity(
                actual,
                expected,
                key="row_id",
                prediction_columns=("prediction",),
                tolerance=1e-9,
                require_order=True,
            )
