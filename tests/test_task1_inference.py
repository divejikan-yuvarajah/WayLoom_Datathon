from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.task1.final_train import (
    load_model_bundle,
    save_model_bundle,
    train_final_models,
)
from src.task1.historical_features import Task1HistoricalFeatureTransformer
from src.task1.inference import (
    OFFICIAL_ROW_ORDER,
    Task1InferenceError,
    apply_service_postprocessing,
    assert_delivery_id_integrity,
    assert_no_forbidden_inference_features,
    assert_probabilities_valid,
    assert_saved_models_present,
    assert_saved_feature_set_compatible,
    join_route_legs_test,
    load_task1_test_inputs,
    predict_late_from_bundle,
    predict_service_from_bundle,
    restore_official_row_order,
    run_saved_model_inference,
    transform_historical_features_for_unseen_test,
)


def _X(n: int = 40) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "brand": (["Fresh", "Style", "Tech", "Home"] * ((n // 4) + 1))[:n],
            "dock_type": (["rear", "street", "mall", "rear"] * ((n // 4) + 1))[:n],
            "depot": (["Peliyagoda", "Kandy"] * ((n // 2) + 1))[:n],
            "numeric_1": np.arange(n, dtype=float),
            "numeric_2": np.linspace(0, 1, n),
            "outlet_prior_service_median": np.linspace(8, 18, n),
            "outlet_prior_late_rate": np.linspace(0.1, 0.4, n),
            "route_id": [f"r{i}" for i in range(n)],
            "delivery_id": [f"d{i}" for i in range(n)],
            "validation_date": pd.date_range("2025-01-01", periods=n, freq="D"),
        }
    )


def _frozen_payload(*, clipping: bool = False, calibration: str = "raw") -> dict:
    return {
        "version": 1,
        "seed": 42,
        "status": "FROZEN",
        "development_selection_complete": True,
        "final_holdout_confirmation_complete": True,
        "features": {"profile": "safe_core_plus_history"},
        "service_model": {
            "family": "catboost",
            "config_id": "svc_frozen_test",
            "feature_profile": "safe_core_plus_history",
            "parameters": {
                "depth": 2,
                "learning_rate": 0.2,
                "loss_function": "MAE",
                "verbose": False,
                "allow_writing_files": False,
            },
            "final_iteration_policy": {"value": 20, "source": "frozen_synthetic"},
            "prediction_postprocessing": {"phase09_clipping": clipping},
        },
        "lateness_model": {
            "family": "catboost",
            "config_id": "late_frozen_test",
            "feature_profile": "safe_core_plus_history",
            "parameters": {
                "depth": 2,
                "learning_rate": 0.2,
                "loss_function": "Logloss",
                "verbose": False,
                "allow_writing_files": False,
            },
            "final_iteration_policy": {"value": 20, "source": "frozen_synthetic"},
            "calibration": {"method": calibration, "protocol": "chronological_oof"},
            "resampling_policy": "none",
        },
    }


def _save_trained(tmp_path: Path, *, clipping: bool = False, calibration: str = "raw") -> tuple[Path, Path, dict, pd.DataFrame]:
    x = _X(40)
    y_s = pd.Series(np.linspace(10, 25, 40))
    y_l = pd.Series(([0, 1] * 20), dtype=float)
    cfg = _frozen_payload(clipping=clipping, calibration=calibration)
    trained = train_final_models(x, y_s, y_l, cfg)
    service_dir = tmp_path / "service"
    late_dir = tmp_path / "late"
    save_model_bundle(service_dir, model=trained["service_model"], metadata=trained["service_metadata"], schema=trained["schema"])
    save_model_bundle(
        late_dir,
        model=trained["late_model"],
        metadata=trained["late_metadata"],
        schema=trained["schema"],
        calibration=trained["calibrator"],
    )
    return service_dir, late_dir, cfg, x


def test_missing_model_fails_without_training(tmp_path: Path) -> None:
    with pytest.raises(Task1InferenceError, match="must not retrain"):
        assert_saved_models_present(tmp_path / "svc", tmp_path / "late")
    assert not (tmp_path / "svc" / "model.joblib").exists()


def test_official_row_order_stamped_before_join(tmp_path: Path) -> None:
    path = tmp_path / "task1_test_inputs.csv"
    pd.DataFrame(
        {
            "delivery_id": ["z", "a", "m"],
            "route_id": ["r2", "r1", "r3"],
            "seq_in_route": [2, 1, 3],
            "outlet_id": ["O2", "O1", "O3"],
        }
    ).to_csv(path, index=False)
    loaded = load_task1_test_inputs(path)
    assert loaded[OFFICIAL_ROW_ORDER].tolist() == [0, 1, 2]
    assert loaded["delivery_id"].tolist() == ["z", "a", "m"]


def test_blank_and_duplicate_delivery_id_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    pd.DataFrame({"delivery_id": ["a", ""], "route_id": ["r", "r"], "seq_in_route": [1, 2]}).to_csv(path, index=False)
    with pytest.raises(Task1InferenceError, match="non-blank"):
        load_task1_test_inputs(path)
    pd.DataFrame({"delivery_id": ["a", "a"], "route_id": ["r", "r"], "seq_in_route": [1, 2]}).to_csv(path, index=False)
    with pytest.raises(Task1InferenceError, match="unique"):
        load_task1_test_inputs(path)


def test_official_route_join_one_to_one() -> None:
    test_inputs = pd.DataFrame(
        {
            OFFICIAL_ROW_ORDER: [0, 1, 2],
            "delivery_id": ["d1", "d2", "d3"],
            "route_id": ["r1", "r1", "r2"],
            "seq_in_route": [1, 2, 1],
            "outlet_id": ["A", "B", "C"],
        }
    )
    legs = pd.DataFrame(
        {
            "route_id": ["r1", "r1", "r2"],
            "seq": [1, 2, 1],
            "to_outlet": ["A", "B", "C"],
            "leg_distance_km": [1.0, 2.0, 3.0],
        }
    )
    joined = join_route_legs_test(test_inputs, legs)
    assert len(joined) == 3
    assert joined["delivery_id"].tolist() == ["d1", "d2", "d3"]


def test_unmatched_test_order_fails() -> None:
    test_inputs = pd.DataFrame(
        {
            "delivery_id": ["d1", "d2"],
            "route_id": ["r1", "r9"],
            "seq_in_route": [1, 1],
        }
    )
    legs = pd.DataFrame({"route_id": ["r1"], "seq": [1], "to_outlet": ["A"]})
    with pytest.raises(Task1InferenceError, match="Unmatched"):
        join_route_legs_test(test_inputs, legs)


def test_duplicate_route_key_fails() -> None:
    test_inputs = pd.DataFrame(
        {"delivery_id": ["d1", "d2"], "route_id": ["r1", "r1"], "seq_in_route": [1, 1]}
    )
    legs = pd.DataFrame({"route_id": ["r1"], "seq": [1]})
    with pytest.raises(Task1InferenceError, match="Duplicate official"):
        join_route_legs_test(test_inputs, legs)


def test_destination_mismatch_fails() -> None:
    test_inputs = pd.DataFrame(
        {"delivery_id": ["d1"], "route_id": ["r1"], "seq_in_route": [1], "outlet_id": ["A"]}
    )
    legs = pd.DataFrame({"route_id": ["r1"], "seq": [1], "to_outlet": ["Z"]})
    with pytest.raises(Task1InferenceError, match="Destination mismatch"):
        join_route_legs_test(test_inputs, legs)


def test_train_test_feature_schema_and_order(tmp_path: Path) -> None:
    service_dir, late_dir, cfg, x = _save_trained(tmp_path)
    preds = run_saved_model_inference(x, service_dir, late_dir, cfg)
    assert len(preds) == len(x)
    assert list(preds.columns) == ["pred_service_min", "pred_late_prob"]
    with pytest.raises(Task1InferenceError, match="missing saved training columns"):
        run_saved_model_inference(x.drop(columns=["numeric_1"]), service_dir, late_dir, cfg)


def test_unseen_test_category_uses_frozen_preprocessing(tmp_path: Path) -> None:
    service_dir, late_dir, cfg, x = _save_trained(tmp_path)
    unseen = x.copy()
    unseen.loc[0, "brand"] = "BrandNeverSeen"
    preds = run_saved_model_inference(unseen, service_dir, late_dir, cfg)
    assert np.isfinite(preds["pred_service_min"]).all()
    assert np.isfinite(preds["pred_late_prob"]).all()


def test_historical_transform_requires_no_test_labels() -> None:
    train = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
            "outlet_id": ["A", "A", "B"],
            "brand": ["Fresh", "Fresh", "Tech"],
            "dock_type": ["rear", "rear", "mall"],
        }
    )
    transformer = Task1HistoricalFeatureTransformer(date_col="date").fit(
        train,
        pd.Series([10.0, 12.0, 8.0]),
        pd.Series([0.0, 1.0, 0.0]),
    )
    test = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-02-01"]),
            "outlet_id": ["A"],
            "brand": ["Fresh"],
            "dock_type": ["rear"],
        }
    )
    out = transform_historical_features_for_unseen_test(transformer, test)
    assert "outlet_prior_service_median" in out.columns
    with pytest.raises(Task1InferenceError, match="must not receive test labels"):
        transform_historical_features_for_unseen_test(transformer, test.assign(service_minutes=99.0))


def test_forbidden_features_absent() -> None:
    with pytest.raises(Task1InferenceError, match="Forbidden"):
        assert_no_forbidden_inference_features(["numeric_1", "actual_depart_time", "late_flag"])


def test_saved_schema_owns_order_but_feature_set_must_match() -> None:
    schema = {"feature_columns": ["brand", "depot", "numeric_1"]}
    assert_saved_feature_set_compatible(schema, ["numeric_1", "brand", "depot"])
    with pytest.raises(Task1InferenceError, match="missing=.*depot.*unexpected=.*new_feature"):
        assert_saved_feature_set_compatible(schema, ["brand", "numeric_1", "new_feature"])
    with pytest.raises(Task1InferenceError, match="duplicate"):
        assert_saved_feature_set_compatible(schema, ["brand", "depot", "numeric_1", "numeric_1"])


def test_service_output_length_finite_and_repeatable(tmp_path: Path) -> None:
    service_dir, late_dir, cfg, x = _save_trained(tmp_path)
    first = run_saved_model_inference(x, service_dir, late_dir, cfg)
    second = run_saved_model_inference(x, service_dir, late_dir, cfg)
    assert len(first) == len(x)
    assert np.isfinite(first["pred_service_min"]).all()
    np.testing.assert_allclose(first["pred_service_min"], second["pred_service_min"], rtol=0, atol=1e-12)
    np.testing.assert_allclose(first["pred_late_prob"], second["pred_late_prob"], rtol=0, atol=1e-12)


def test_negative_service_policies() -> None:
    values, report = apply_service_postprocessing(np.array([1.0, 2.0]), "fail")
    assert report["postprocessing_policy"] == "noop_no_negatives"
    np.testing.assert_array_equal(values, [1.0, 2.0])
    clipped, clip_report = apply_service_postprocessing(np.array([-1.5, 2.0]), "clip_to_zero")
    np.testing.assert_allclose(clipped, [0.0, 2.0])
    assert clip_report["postprocessed_count"] == 1
    with pytest.raises(Task1InferenceError, match="no clip_to_zero"):
        apply_service_postprocessing(np.array([-0.1, 1.0]), "fail")
    with pytest.raises(Task1InferenceError, match="abs"):
        apply_service_postprocessing(np.array([-1.0]), "abs")


def test_late_probability_bounds_and_identity(tmp_path: Path) -> None:
    service_dir, late_dir, cfg, x = _save_trained(tmp_path, calibration="raw")
    bundle = load_model_bundle(late_dir)
    prob = predict_late_from_bundle(bundle, x)
    assert bundle["metadata"]["positive_class_index"] == 1
    assert ((prob >= 0) & (prob <= 1)).all()
    assert_probabilities_valid(np.array([0.0, 0.5, 1.0]))
    with pytest.raises(Task1InferenceError):
        assert_probabilities_valid(np.array([-0.001]))
    with pytest.raises(Task1InferenceError):
        assert_probabilities_valid(np.array([1.001]))
    with pytest.raises(Task1InferenceError):
        assert_probabilities_valid(np.array([np.nan]))
    with pytest.raises(Task1InferenceError):
        assert_probabilities_valid(np.array([np.inf]))


def test_calibrated_path_changes_only_via_saved_artifact(tmp_path: Path) -> None:
    service_dir, late_dir, cfg, x = _save_trained(tmp_path, calibration="sigmoid")
    preds = run_saved_model_inference(x, service_dir, late_dir, cfg)
    assert ((preds["pred_late_prob"] >= 0) & (preds["pred_late_prob"] <= 1)).all()


def test_restore_arbitrary_official_order() -> None:
    frame = pd.DataFrame(
        {
            OFFICIAL_ROW_ORDER: [2, 0, 1],
            "delivery_id": ["c", "a", "b"],
        }
    )
    restored = restore_official_row_order(frame)
    assert restored["delivery_id"].tolist() == ["a", "b", "c"]
    assert_delivery_id_integrity(pd.Series(["a", "b", "c"]), restored["delivery_id"])
    with pytest.raises(Task1InferenceError, match="ordered sequence"):
        assert_delivery_id_integrity(pd.Series(["a", "b", "c"]), pd.Series(["c", "b", "a"]))


def test_prepare_test_features_calls_phase06_canonical_kwargs(tmp_path: Path, monkeypatch) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    for name, frame in {
        "deliveries_train.csv": pd.DataFrame({"delivery_id": ["t1"], "route_id": ["r1"], "seq_in_route": [1]}),
        "task1_test_inputs.csv": pd.DataFrame({"delivery_id": ["x1"], "route_id": ["r9"], "seq_in_route": [1]}),
        "route_legs_train.csv": pd.DataFrame({"route_id": ["r1"], "seq": [1]}),
        "route_legs_test.csv": pd.DataFrame({"route_id": ["r9"], "seq": [1]}),
        "outlets.csv": pd.DataFrame({"outlet_id": ["A"]}),
        "vehicles.csv": pd.DataFrame({"vehicle_id": ["v1"]}),
        "calendar.csv": pd.DataFrame({"date": ["2025-01-01"]}),
        "district_travel.csv": pd.DataFrame({"from_district": ["a"], "to_district": ["b"]}),
        "service_allowance.csv": pd.DataFrame({"brand": ["Fresh"]}),
    }.items():
        frame.to_csv(raw / name, index=False)
    labels = pd.DataFrame({"delivery_id": ["t1"], "service_minutes": [10.0], "late_flag": [0]})
    captured: dict = {}

    def _fake_build(**kwargs):
        captured.update(kwargs)
        x = pd.DataFrame({"numeric_1": [1.0], "brand": ["Fresh"]})
        return {"X_train": x, "X_test": x.copy()}

    monkeypatch.setattr("src.task1.inference.build_task1_feature_tables", _fake_build)
    monkeypatch.setattr("src.task1.inference.load_task1_features_config", lambda path: {"history": {}})
    from src.task1.inference import prepare_test_features_from_raw

    X_test, trace = prepare_test_features_from_raw(
        raw,
        tmp_path / "features.yaml",
        historical_train_labels=labels,
    )
    assert set(captured) >= {
        "orders_train",
        "orders_test",
        "route_legs_train",
        "route_legs_test",
        "labels_train",
        "config",
    }
    assert "deliveries_train" not in captured
    assert "test_labels" not in captured
    assert captured["labels_train"] is labels
    assert X_test["delivery_id"].tolist() == ["x1"]
    assert trace["delivery_id"].tolist() == ["x1"]


def test_reload_then_infer_not_in_memory_object(tmp_path: Path) -> None:
    service_dir, late_dir, cfg, x = _save_trained(tmp_path)
    # Intentionally do not keep the trained objects; only saved paths are used.
    preds = run_saved_model_inference(x, service_dir, late_dir, cfg)
    assert len(preds) == len(x)
    service = predict_service_from_bundle(load_model_bundle(service_dir), x)
    np.testing.assert_allclose(preds["pred_service_min"].to_numpy(), service, rtol=0, atol=1e-12)
