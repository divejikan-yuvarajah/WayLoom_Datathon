from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from src.task1.final_train import (
    Task1FinalTrainError,
    apply_frozen_calibrator,
    assert_no_phase10_model_search,
    feature_schema_hash,
    identify_positive_class_index,
    load_frozen_final_config,
    load_model_bundle,
    predict_positive_probability,
    prepare_model_frame,
    resolve_feature_columns,
    resolve_negative_service_policy,
    save_model_bundle,
    train_final_models,
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


def _y(n: int = 40) -> tuple[pd.Series, pd.Series]:
    service = pd.Series(np.linspace(10, 25, n), name="service_minutes")
    late = pd.Series(([0, 1] * ((n // 2) + 1))[:n], name="late_flag", dtype=float)
    return service, late


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
            "class_weight_policy": None,
            "resampling_policy": "none",
        },
    }


def _write_config(path: Path, payload: dict) -> Path:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_frozen_config_honored(tmp_path: Path) -> None:
    cfg = load_frozen_final_config(_write_config(tmp_path / "ok.yaml", _frozen_payload()))
    assert cfg["service_model"]["config_id"] == "svc_frozen_test"
    assert cfg["lateness_model"]["family"] == "catboost"
    assert int(cfg["service_model"]["final_iteration_policy"]["value"]) == 20


def test_unfrozen_contract_rejected(tmp_path: Path) -> None:
    payload = _frozen_payload()
    payload["status"] = "PLACEHOLDER_UNFROZEN"
    payload["development_selection_complete"] = False
    payload["final_holdout_confirmation_complete"] = False
    with pytest.raises(Task1FinalTrainError, match="not frozen"):
        load_frozen_final_config(_write_config(tmp_path / "unfrozen.yaml", payload))
    nested = {
        "version": 1,
        "seed": 42,
        "validation_contract": {
            "development_selection_complete": False,
            "final_holdout_confirmation_complete": False,
        },
        "features": {"profile": "safe_core_plus_history"},
        "service_model": {
            "family": None,
            "config_id": None,
            "parameters": {},
            "final_iteration_policy": {"method": None, "value": None},
        },
        "lateness_model": {
            "family": None,
            "config_id": None,
            "parameters": {},
            "final_iteration_policy": {"method": None, "value": None},
            "calibration": {"method": None, "fit_protocol": None},
        },
    }
    with pytest.raises(Task1FinalTrainError, match="not complete"):
        load_frozen_final_config(_write_config(tmp_path / "unfrozen_nested.yaml", nested))


def test_valid_frozen_contract_accepted(tmp_path: Path) -> None:
    payload = _frozen_payload()
    payload.pop("status", None)
    payload.pop("development_selection_complete", None)
    payload.pop("final_holdout_confirmation_complete", None)
    payload["validation_contract"] = {
        "development_selection_complete": True,
        "final_holdout_confirmation_complete": True,
    }
    payload["lateness_model"]["calibration"] = {"method": "raw", "fit_protocol": "chronological_oof"}
    cfg = load_frozen_final_config(_write_config(tmp_path / "phase09_shape.yaml", payload))
    assert cfg["service_model"]["family"] == "catboost"
    assert cfg["lateness_model"]["config_id"] == "late_frozen_test"


def test_current_tracked_final_contract_is_frozen_and_valid() -> None:
    path = Path("configs/task1_final_models.yaml")
    cfg = load_frozen_final_config(path)
    assert not isinstance(cfg["service_model"], list)
    assert not isinstance(cfg["lateness_model"], list)
    service = cfg["service_model"]
    late = cfg["lateness_model"]
    contract = cfg.get("validation_contract") or {}
    assert bool(contract.get("development_selection_complete")) is True
    assert bool(contract.get("final_holdout_confirmation_complete")) is True
    assert int(contract.get("final_holdout_access_count_per_target", 0)) >= 1
    assert service.get("family")
    assert service.get("config_id")
    assert late.get("family")
    assert late.get("config_id")
    assert cfg.get("seed") is not None
    features = cfg.get("features") or {}
    assert features.get("profile")
    assert features.get("registry")
    assert int((service.get("final_iteration_policy") or {}).get("value") or 0) > 0
    assert int((late.get("final_iteration_policy") or {}).get("value") or 0) > 0
    calib = late.get("calibration") or {}
    assert str(calib.get("method") or "").strip().lower() not in {"", "null", "none"}
    assert "candidates" not in cfg
    assert "search" not in cfg


def test_missing_config_rejected(tmp_path: Path) -> None:
    with pytest.raises(Task1FinalTrainError, match="not found"):
        load_frozen_final_config(tmp_path / "missing.yaml")


def test_multiple_final_configs_rejected(tmp_path: Path) -> None:
    payload = _frozen_payload()
    payload["service_model"] = [payload["service_model"], payload["service_model"]]
    with pytest.raises(Task1FinalTrainError, match="Multiple"):
        load_frozen_final_config(_write_config(tmp_path / "multi.yaml", payload))


def test_search_keys_rejected() -> None:
    with pytest.raises(Task1FinalTrainError, match="must not run model search"):
        assert_no_phase10_model_search({"search": {"enabled": True}})


def test_balanced_class_weight_rejected(tmp_path: Path) -> None:
    payload = _frozen_payload()
    payload["lateness_model"]["parameters"]["auto_class_weights"] = "Balanced"
    with pytest.raises(Task1FinalTrainError, match="forbids"):
        load_frozen_final_config(_write_config(tmp_path / "bal.yaml", payload))


def test_forbidden_and_target_features_rejected() -> None:
    frame = _X(8).assign(
        actual_depart_time=1.0,
        service_minutes=12.0,
        late_flag=0,
        arrival_time=3.0,
    )
    cols = resolve_feature_columns(frame, "safe_core_plus_history")
    assert "actual_depart_time" not in cols
    assert "arrival_time" not in cols
    assert "service_minutes" not in cols
    assert "late_flag" not in cols
    matrix = prepare_model_frame(frame, cols, [c for c in cols if not pd.api.types.is_numeric_dtype(frame[c])])
    assert "service_minutes" not in matrix.columns
    assert "late_flag" not in matrix.columns


def test_no_tuning_loop_in_train(tmp_path: Path) -> None:
    cfg = _frozen_payload()
    cfg["candidates"] = [{"id": "a"}, {"id": "b"}]
    x = _X(40)
    y_s, y_l = _y(40)
    with pytest.raises(Task1FinalTrainError, match="must not contain search key"):
        train_final_models(x, y_s, y_l, cfg)


def test_service_and_lateness_save_reload(tmp_path: Path) -> None:
    x = _X(40)
    y_s, y_l = _y(40)
    trained = train_final_models(x, y_s, y_l, _frozen_payload())
    schema = trained["schema"]
    frame = prepare_model_frame(x, schema["feature_columns"], schema["categorical_columns"])
    service_before = np.asarray(trained["service_model"].predict(frame), dtype=float)
    late_before = predict_positive_probability(trained["late_model"], frame)
    save_model_bundle(
        tmp_path / "service",
        model=trained["service_model"],
        metadata=trained["service_metadata"],
        schema=schema,
    )
    save_model_bundle(
        tmp_path / "late",
        model=trained["late_model"],
        metadata=trained["late_metadata"],
        schema=schema,
        calibration=trained["calibrator"],
    )
    del trained
    service_bundle = load_model_bundle(tmp_path / "service")
    late_bundle = load_model_bundle(tmp_path / "late")
    service_after = np.asarray(service_bundle["model"].predict(frame), dtype=float)
    late_after = predict_positive_probability(late_bundle["model"], frame)
    np.testing.assert_allclose(service_before, service_after, rtol=0, atol=1e-12)
    np.testing.assert_allclose(late_before, late_after, rtol=0, atol=1e-12)
    assert service_bundle["schema"]["feature_columns"] == schema["feature_columns"]
    assert identify_positive_class_index(late_bundle["model"]) == late_bundle["metadata"]["positive_class_index"]
    assert any(str(c).split(".")[0] == "1" for c in late_bundle["metadata"]["classes"])
    assert feature_schema_hash(service_bundle["schema"]) == service_bundle["metadata"]["feature_schema_hash"]
    assert "row" not in str(service_bundle["metadata"]).lower() or "training_row_count" in service_bundle["metadata"]


def test_calibration_save_reload(tmp_path: Path) -> None:
    x = _X(40)
    y_s, y_l = _y(40)
    trained = train_final_models(x, y_s, y_l, _frozen_payload(calibration="sigmoid"))
    assert trained["calibrator"] is not None
    frame = prepare_model_frame(x, trained["schema"]["feature_columns"], trained["schema"]["categorical_columns"])
    raw = predict_positive_probability(trained["late_model"], frame)
    before = apply_frozen_calibrator(trained["calibrator"], raw)
    save_model_bundle(
        tmp_path / "late",
        model=trained["late_model"],
        metadata=trained["late_metadata"],
        schema=trained["schema"],
        calibration=trained["calibrator"],
    )
    del trained
    bundle = load_model_bundle(tmp_path / "late", require_calibration=True)
    after = apply_frozen_calibrator(bundle["calibration"], raw)
    np.testing.assert_allclose(before, after, rtol=0, atol=1e-12)
    assert bundle["metadata"]["calibration_method"] == "sigmoid"


def test_missing_saved_model_fails(tmp_path: Path) -> None:
    with pytest.raises(Task1FinalTrainError, match="must not retrain"):
        load_model_bundle(tmp_path / "empty")


def test_negative_policy_from_frozen_clip_flag() -> None:
    assert resolve_negative_service_policy(_frozen_payload(clipping=True)) == "clip_to_zero"
    assert resolve_negative_service_policy(_frozen_payload(clipping=False)) == "fail"
