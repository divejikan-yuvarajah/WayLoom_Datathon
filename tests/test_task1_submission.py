from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.task1.final_train import save_model_bundle, train_final_models
from src.task1.inference import assemble_official_predictions, load_task1_test_inputs, run_saved_model_inference
from src.task1.submission import (
    OFFICIAL_TASK1_COLUMNS,
    Task1SubmissionError,
    export_task1_submission,
    fill_official_task1_template,
    validate_task1_submission,
)


def _template(ids: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "delivery_id": ids,
            "pred_service_min": [np.nan] * len(ids),
            "pred_late_prob": [np.nan] * len(ids),
        }
    )


def test_fill_preserves_official_order_and_ids() -> None:
    template = _template(["z", "a", "m"])
    preds = pd.DataFrame(
        {
            "delivery_id": ["m", "z", "a"],
            "pred_service_min": [3.0, 1.0, 2.0],
            "pred_late_prob": [0.3, 0.1, 0.2],
        }
    )
    filled = fill_official_task1_template(template, preds)
    assert filled["delivery_id"].tolist() == ["z", "a", "m"]
    assert filled["pred_service_min"].tolist() == [1.0, 2.0, 3.0]
    assert list(filled.columns) == OFFICIAL_TASK1_COLUMNS


def test_extra_columns_fail() -> None:
    official = pd.Series(["a", "b"])
    bad = pd.DataFrame(
        {
            "delivery_id": ["a", "b"],
            "pred_service_min": [1.0, 2.0],
            "pred_late_prob": [0.1, 0.2],
            "model_name": ["x", "y"],
        }
    )
    with pytest.raises(Task1SubmissionError, match="extra columns"):
        validate_task1_submission(bad, official)


def test_accidental_index_column_fails() -> None:
    official = pd.Series(["a", "b"])
    bad = pd.DataFrame(
        {
            "Unnamed: 0": [0, 1],
            "delivery_id": ["a", "b"],
            "pred_service_min": [1.0, 2.0],
            "pred_late_prob": [0.1, 0.2],
        }
    )
    with pytest.raises(Task1SubmissionError, match="index column"):
        validate_task1_submission(bad, official)


def test_wrong_column_order_fails() -> None:
    official = pd.Series(["a", "b"])
    bad = pd.DataFrame(
        {
            "pred_service_min": [1.0, 2.0],
            "delivery_id": ["a", "b"],
            "pred_late_prob": [0.1, 0.2],
        }
    )
    with pytest.raises(Task1SubmissionError, match="columns/order"):
        validate_task1_submission(bad, official)


def test_atomic_export_and_readback(tmp_path: Path) -> None:
    official = pd.Series(["a", "b"])
    submission = pd.DataFrame(
        {
            "delivery_id": ["a", "b"],
            "pred_service_min": [1.5, 2.5],
            "pred_late_prob": [0.0, 1.0],
        }
    )
    path = tmp_path / "submission_task1.csv"
    export_task1_submission(submission, path, official)
    assert path.is_file()
    assert not (tmp_path / "submission_task1.csv.tmp").exists()
    readback = pd.read_csv(path)
    assert list(readback.columns) == OFFICIAL_TASK1_COLUMNS
    validate_task1_submission(readback, official)


def test_end_to_end_reload_and_repeat_inference(tmp_path: Path) -> None:
    n = 40
    x = pd.DataFrame(
        {
            "brand": (["Fresh", "Style", "Tech", "Home"] * 10)[:n],
            "dock_type": (["rear", "street", "mall", "rear"] * 10)[:n],
            "depot": (["Peliyagoda", "Kandy"] * 20)[:n],
            "numeric_1": np.arange(n, dtype=float),
            "numeric_2": np.linspace(0, 1, n),
            "outlet_prior_service_median": np.linspace(8, 18, n),
            "outlet_prior_late_rate": np.linspace(0.1, 0.4, n),
            "route_id": [f"r{i}" for i in range(n)],
            "delivery_id": [f"d{i:03d}" for i in range(n)],
            "validation_date": pd.date_range("2025-01-01", periods=n, freq="D"),
        }
    )
    cfg = {
        "version": 1,
        "seed": 42,
        "status": "FROZEN",
        "development_selection_complete": True,
        "final_holdout_confirmation_complete": True,
        "features": {"profile": "safe_core_plus_history"},
        "service_model": {
            "family": "catboost",
            "config_id": "svc_e2e",
            "feature_profile": "safe_core_plus_history",
            "parameters": {"depth": 2, "learning_rate": 0.2, "loss_function": "MAE"},
            "final_iteration_policy": {"value": 20},
            "prediction_postprocessing": {"phase09_clipping": False},
        },
        "lateness_model": {
            "family": "catboost",
            "config_id": "late_e2e",
            "feature_profile": "safe_core_plus_history",
            "parameters": {"depth": 2, "learning_rate": 0.2, "loss_function": "Logloss"},
            "final_iteration_policy": {"value": 20},
            "calibration": {"method": "raw", "protocol": "chronological_oof"},
            "resampling_policy": "none",
        },
    }
    trained = train_final_models(
        x,
        pd.Series(np.linspace(10, 25, n)),
        pd.Series(([0, 1] * 20)[:n], dtype=float),
        cfg,
    )
    service_dir = tmp_path / "service"
    late_dir = tmp_path / "late"
    save_model_bundle(service_dir, model=trained["service_model"], metadata=trained["service_metadata"], schema=trained["schema"])
    save_model_bundle(late_dir, model=trained["late_model"], metadata=trained["late_metadata"], schema=trained["schema"])
    del trained

    official_ids = list(reversed(x["delivery_id"].tolist()))
    inputs_path = tmp_path / "task1_test_inputs.csv"
    pd.DataFrame(
        {
            "delivery_id": official_ids,
            "route_id": ["r0"] * n,
            "seq_in_route": list(range(n)),
        }
    ).to_csv(inputs_path, index=False)
    test_inputs = load_task1_test_inputs(inputs_path)
    x_scrambled = x.set_index("delivery_id").loc[official_ids].reset_index()
    first = run_saved_model_inference(x_scrambled, service_dir, late_dir, cfg)
    first = first.copy()
    first["delivery_id"] = x_scrambled["delivery_id"].to_numpy()
    assembled = assemble_official_predictions(test_inputs, first)
    template = _template(official_ids)
    submission = fill_official_task1_template(template, assembled)
    out_a = tmp_path / "run_a" / "submission_task1.csv"
    out_b = tmp_path / "run_b" / "submission_task1.csv"
    export_task1_submission(submission, out_a, pd.Series(official_ids))

    second = run_saved_model_inference(x_scrambled, service_dir, late_dir, cfg)
    second = second.copy()
    second["delivery_id"] = x_scrambled["delivery_id"].to_numpy()
    submission_b = fill_official_task1_template(template, assemble_official_predictions(test_inputs, second))
    export_task1_submission(submission_b, out_b, pd.Series(official_ids))

    a = pd.read_csv(out_a)
    b = pd.read_csv(out_b)
    assert a["delivery_id"].tolist() == official_ids
    assert list(a.columns) == OFFICIAL_TASK1_COLUMNS
    np.testing.assert_allclose(a["pred_service_min"], b["pred_service_min"], rtol=0, atol=1e-12)
    np.testing.assert_allclose(a["pred_late_prob"], b["pred_late_prob"], rtol=0, atol=1e-12)
    validate_task1_submission(a, pd.Series(official_ids))
