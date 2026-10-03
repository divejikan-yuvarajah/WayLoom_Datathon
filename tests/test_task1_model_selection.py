from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

from src.task1.model_selection import (
    Task1ModelSelectionError,
    assert_same_fold_contract,
    select_lateness_candidate,
    select_regression_candidate,
)


def test_same_fold_contract_enforced() -> None:
    ok = pd.DataFrame(
        [
            {"target": "service", "candidate_id": "a", "fold_id": 1, "train_start_date": "2025-01-01", "train_end_date": "2025-01-10", "validation_start_date": "2025-01-11", "validation_end_date": "2025-01-15"},
            {"target": "service", "candidate_id": "b", "fold_id": 1, "train_start_date": "2025-01-01", "train_end_date": "2025-01-10", "validation_start_date": "2025-01-11", "validation_end_date": "2025-01-15"},
        ]
    )
    assert_same_fold_contract(ok)
    bad = ok.copy()
    bad.loc[1, "validation_end_date"] = "2025-01-16"
    with pytest.raises(Task1ModelSelectionError):
        assert_same_fold_contract(bad)


def test_selection_rules() -> None:
    summary = pd.DataFrame(
        [
            {"candidate_id": "svc_a", "target": "service", "fold_count": 4, "required_fold_count": 4, "status": "ok", "mae": 2.0, "rmse": 3.0, "mae_std": 0.2, "p90_absolute_error": 4.0, "complexity_score": 5},
            {"candidate_id": "svc_b", "target": "service", "fold_count": 4, "required_fold_count": 4, "status": "ok", "mae": 1.8, "rmse": 2.9, "mae_std": 0.1, "p90_absolute_error": 3.8, "complexity_score": 6},
            {"candidate_id": "late_a", "target": "late", "fold_count": 4, "required_fold_count": 4, "status": "ok", "log_loss": 0.41, "brier_score": 0.18, "log_loss_std": 0.02, "complexity_score": 5, "calibration_method": "raw", "calibration_protocol": "chronological_oof"},
            {"candidate_id": "late_b", "target": "late", "fold_count": 4, "required_fold_count": 4, "status": "ok", "log_loss": 0.35, "brier_score": 0.16, "log_loss_std": 0.01, "complexity_score": 6, "calibration_method": "sigmoid", "calibration_protocol": "chronological_oof"},
        ]
    )
    svc = select_regression_candidate(summary)
    late = select_lateness_candidate(summary)
    assert svc["candidate_id"] == "svc_b"
    assert late["candidate_id"] == "late_b"


def test_holdout_single_config_guard_and_repeat_block(tmp_path: Path) -> None:
    n = 450
    features = tmp_path / "features.csv"
    labels = tmp_path / "labels.csv"
    model_cfg = tmp_path / "advanced.yaml"
    validation_cfg = Path("configs/task1_validation.yaml")
    pd.DataFrame(
        {
            "delivery_id": [f"d{i}" for i in range(n)],
            "route_id": [f"r{i//2}" for i in range(n)],
            "seq_in_route": [(i % 5) + 1 for i in range(n)],
            "brand": (["Fresh", "Style", "Tech", "Fresh", "Style"] * (n // 5)) + ["Fresh"] * (n % 5),
            "dock_type": (["rear", "street", "mall", "rear", "street"] * (n // 5)) + ["rear"] * (n % 5),
            "depot": (["Peliyagoda", "Kandy"] * (n // 2)) + ["Peliyagoda"] * (n % 2),
            "planned_distance_km": [float(i % 17 + 1) for i in range(n)],
            "outlet_prior_service_median": [10.0 + (i % 3) for i in range(n)],
        }
    ).to_csv(features, index=False)
    dates = pd.date_range("2025-01-01", periods=n, freq="D")
    pd.DataFrame(
        {
            "delivery_id": [f"d{i}" for i in range(n)],
            "route_id": [f"r{i//2}" for i in range(n)],
            "seq_in_route": [(i % 5) + 1 for i in range(n)],
            "route_date": [d.strftime("%Y-%m-%d") for d in dates],
            "dispatch_date": [d.strftime("%Y-%m-%d") for d in dates],
            "service_minutes": [20.0 + (i % 4) for i in range(n)],
            "late_flag": [float(i % 2) for i in range(n)],
        }
    ).to_csv(labels, index=False)
    model_cfg.write_text(
        "seed: 42\nearly_stopping:\n  max_iterations: 20\n  patience_rounds: 5\n",
        encoding="utf-8",
    )
    selection = tmp_path / "selection.json"
    output = tmp_path / "holdout.json"
    selection.write_text(
        json.dumps(
            {
                "service": {
                    "candidate_id": "catboost_regression_default",
                    "family": "catboost",
                    "feature_profile": "safe_core_plus_history",
                    "parameters": {"depth": 2, "learning_rate": 0.1, "l2_leaf_reg": 3},
                    "final_iteration_policy": {"method": "median_best_iteration", "value": 10},
                },
                "lateness": {
                    "candidate_id": "catboost_classifier_default",
                    "family": "catboost",
                    "feature_profile": "safe_core_plus_history",
                    "parameters": {"depth": 2, "learning_rate": 0.1, "l2_leaf_reg": 3},
                    "final_iteration_policy": {"method": "median_best_iteration", "value": 10},
                    "calibration_method": "raw",
                    "calibration_protocol": "chronological_oof",
                },
            }
        ),
        encoding="utf-8",
    )
    script = Path("scripts/confirm_task1_final_holdout.py")
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--features",
            str(features),
            "--labels",
            str(labels),
            "--validation-config",
            str(validation_cfg),
            "--model-config",
            str(model_cfg),
            "--selection",
            str(selection),
            "--output",
            str(output),
        ],
        check=True,
    )
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["service_configs_evaluated_on_holdout"] == 1
    failed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--features",
            str(features),
            "--labels",
            str(labels),
            "--validation-config",
            str(validation_cfg),
            "--model-config",
            str(model_cfg),
            "--selection",
            str(selection),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert failed.returncode != 0


def test_final_config_writer_schema(tmp_path: Path) -> None:
    selection = tmp_path / "selection.json"
    holdout = tmp_path / "holdout.json"
    advanced = tmp_path / "advanced.yaml"
    output = tmp_path / "final.yaml"
    selection.write_text(
        json.dumps(
            {
                "service": {
                    "candidate_id": "catboost_regression_default",
                    "family": "catboost",
                    "parameters": {"depth": 5},
                    "final_iteration_policy": {"method": "median_best_iteration", "value": 123},
                },
                "lateness": {
                    "candidate_id": "catboost_classifier_default",
                    "calibration_method": "sigmoid",
                    "calibration_protocol": "chronological_oof",
                    "parameters": {"depth": 7},
                    "final_iteration_policy": {"method": "median_best_iteration", "value": 111},
                },
            }
        ),
        encoding="utf-8",
    )
    holdout.write_text(
        json.dumps(
            {
                "success": True,
                "service_configs_evaluated_on_holdout": 1,
                "lateness_configs_evaluated_on_holdout": 1,
            }
        ),
        encoding="utf-8",
    )
    advanced.write_text("seed: 42\nfeatures:\n  profile: safe_core_plus_history\n", encoding="utf-8")
    script = Path("scripts/freeze_task1_model_config.py")
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--selection",
            str(selection),
            "--holdout-confirmation",
            str(holdout),
            "--advanced-config",
            str(advanced),
            "--output",
            str(output),
        ],
        check=True,
    )
    text = output.read_text(encoding="utf-8")
    assert "final_holdout_confirmation_complete: true" in text
    assert "regression_primary_metric: mae" in text
    assert "value: 123" in text
    assert "value: 111" in text


def test_final_config_writer_accepts_selection_without_family(tmp_path: Path) -> None:
    selection = tmp_path / "selection.json"
    holdout = tmp_path / "holdout.json"
    advanced = tmp_path / "advanced.yaml"
    output = tmp_path / "final.yaml"
    selection.write_text(
        json.dumps(
            {
                "service": {
                    "candidate_id": "catboost_regression_default",
                    "final_iteration_policy": {"method": "median_best_iteration", "value": 80},
                },
                "lateness": {
                    "candidate_id": "catboost_classifier_default",
                    "calibration_method": "raw",
                    "final_iteration_policy": {"method": "median_best_iteration", "value": 90},
                },
            }
        ),
        encoding="utf-8",
    )
    holdout.write_text(
        json.dumps(
            {
                "success": True,
                "service_configs_evaluated_on_holdout": 1,
                "lateness_configs_evaluated_on_holdout": 1,
            }
        ),
        encoding="utf-8",
    )
    advanced.write_text(
        Path("configs/task1_advanced_models.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/freeze_task1_model_config.py",
            "--selection",
            str(selection),
            "--holdout-confirmation",
            str(holdout),
            "--advanced-config",
            str(advanced),
            "--output",
            str(output),
        ],
        check=True,
    )
    text = output.read_text(encoding="utf-8")
    assert "family: catboost" in text
    assert "config_id: catboost_regression_default" in text
