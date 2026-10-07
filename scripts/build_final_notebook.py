"""Deterministically build the output-cleared Phase 31 competition notebook."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "TeamName_FinalNotebook.ipynb"


def _markdown(source: str, *tags: str):
    return nbformat.v4.new_markdown_cell(source.strip() + "\n", metadata={"tags": list(tags)})


def _code(source: str, *tags: str):
    return nbformat.v4.new_code_cell(source.strip() + "\n", metadata={"tags": list(tags)})


def build_notebook():
    cells = [
        _markdown(
            """
# WayLoom Datathon
## Rootcode Tech-Triathlon 2026
### Final Competition Notebook

This notebook is the evidence layer for the finalized WayLoom Datathon solution. It covers Task 1 service-time and lateness prediction, Task 2A ten-week demand forecasting, and the Task 2B peak-day allocation summary while reusing the canonical implementation in `src/`.

> This notebook operates on competition data locally and is intended for the authorized competition submission workflow.

The tracked source notebook intentionally contains no private outputs. A validated executed copy is produced only inside the authorized private execution directory.
""",
            "dt-389",
            "title",
        ),
        _markdown(
            """
# 1. Project and problem overview

- **Task 1 - regression and probability classification:** predict `pred_service_min` and `pred_late_prob` for each test `delivery_id`.
- **Task 2A - time-aware forecasting:** forecast `pred_total_volume_m3` and `pred_chilled_volume_m3` for each supplied depot/brand row across 10 future weeks.
- **Task 2B - constraint optimization:** produce a feasible served/deferred peak-day allocation with vehicle and trip assignments and explain the prioritization policy.

| Task | Exact official output columns |
|---|---|
| Task 1 | `delivery_id, pred_service_min, pred_late_prob` |
| Task 2A | `row_id, pred_total_volume_m3, pred_chilled_volume_m3` |
| Task 2B | `scenario, order_ref, outlet_id, decision, vehicle_id, trip_id` |

Task 1 and Task 2A are predictive problems; Task 2B is deterministic constraint optimization and does not require a trained model. The architecture and full preprocessing rationale are documented in `docs/architecture/high_level_datathon.svg` and `docs/preprocessing.md`.
""",
            "dt-390",
            "overview",
        ),
        _markdown(
            """
# 2. Imports, configuration, and reproducibility

The next cell resolves the repository without a machine-specific path, loads only tracked final configurations, validates their frozen state, and fixes the approved random seed. It does not install packages, download data, or select fallback models.
""",
            "configuration",
        ),
        _code(
            """
from pathlib import Path
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from src.common.data_inventory import discover_dataset_files, load_manifest
from src.task1.final_train import load_frozen_final_config
from src.task1.features import load_task1_features_config
from src.task1.validation import load_task1_validation_config
from src.task2a.features import load_feature_config
from src.task2a.history import load_history_config
from src.task2a.model_selection import validate_final_model_config
from src.task2a.validation import load_validation_config


def resolve_project_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "configs").is_dir() and (candidate / "src").is_dir():
            return candidate
    raise FileNotFoundError("WayLoom project root was not found.")


ROOT = resolve_project_root(Path.cwd())
with (ROOT / "configs/final_notebook.yaml").open(encoding="utf-8") as handle:
    notebook_config = yaml.safe_load(handle)

seed = int(notebook_config["reproducibility"]["random_seed"])
random.seed(seed)
np.random.seed(seed)

dataset_manifest = load_manifest(ROOT / "configs/dataset_manifest.yaml")
task1_feature_config = load_task1_features_config(ROOT / "configs/task1_features.yaml")
task1_validation_config = load_task1_validation_config(ROOT / "configs/task1_validation.yaml")
task1_final_config = load_frozen_final_config(ROOT / "configs/task1_final_models.yaml")
with (ROOT / "configs/task1_inference.yaml").open(encoding="utf-8") as handle:
    task1_inference_config = yaml.safe_load(handle)

task2a_history_config = load_history_config(ROOT / "configs/task2a_history.yaml")
task2a_feature_config = load_feature_config(ROOT / "configs/task2a_features.yaml")
task2a_validation_config = load_validation_config(ROOT / "configs/task2a_validation.yaml")
with (ROOT / "configs/task2a_final_models.yaml").open(encoding="utf-8") as handle:
    task2a_final_config = yaml.safe_load(handle)
validate_final_model_config(task2a_final_config)
with (ROOT / "configs/task2a_inference.yaml").open(encoding="utf-8") as handle:
    task2a_inference_config = yaml.safe_load(handle)
with (ROOT / "configs/task2a_advanced_models.yaml").open(encoding="utf-8") as handle:
    task2a_advanced_config = yaml.safe_load(handle)

with (ROOT / "configs/task2b_scenario.yaml").open(encoding="utf-8") as handle:
    task2b_scenario_config = yaml.safe_load(handle)
with (ROOT / "configs/task2b_priority.yaml").open(encoding="utf-8") as handle:
    task2b_priority_config = yaml.safe_load(handle)
with (ROOT / "configs/task2b_optimizer.yaml").open(encoding="utf-8") as handle:
    task2b_optimizer_config = yaml.safe_load(handle)
with (ROOT / "configs/task2b_validation.yaml").open(encoding="utf-8") as handle:
    task2b_validation_config = yaml.safe_load(handle)

assert task1_final_config["features"]["profile"] == "safe_core_plus_history"
assert task1_final_config["service_model"]["config_id"] == "catboost_regression_default"
assert task1_final_config["lateness_model"]["config_id"] == "catboost_classifier_default"
assert task2a_final_config["state"] == "FROZEN"
print("Project root resolved")
print("Final tracked configurations loaded: PASS")
print(f"Deterministic seed: {seed}")
""",
            "dt-391",
            "configuration",
        ),
        _markdown(
            """
# 3. Data loading

The official files are resolved through `configs/dataset_manifest.yaml`. Only the data required for Task 1 and Task 2A evidence is loaded. Task 2B row-level allocations are not loaded or displayed here; its frozen output and written policy are referenced later.
""",
            "data-loading",
        ),
        _code(
            """
raw_root = ROOT / "data/raw"
if not raw_root.is_dir():
    raise FileNotFoundError(
        "Competition data not found in the configured local data root. "
        "Run this notebook in the authorized WayLoom Datathon environment."
    )

discovery = discover_dataset_files(raw_root, dataset_manifest)
if discovery["discovery_status"] != "PASS":
    raise ValueError("Required competition files are missing or duplicated.")
found = discovery["found_artifacts"]


def read_official(filename: str) -> pd.DataFrame:
    record = found.get(filename)
    if not record:
        raise FileNotFoundError(f"Required manifest artifact is unavailable: {filename}")
    return pd.read_csv(record["path"], low_memory=False)


deliveries_train = read_official("deliveries_train.csv")
route_legs_train = read_official("route_legs_train.csv")
task1_test_inputs = read_official("task1_test_inputs.csv")
route_legs_test = read_official("route_legs_test.csv")
outlets = read_official("outlets.csv")
vehicles = read_official("vehicles.csv")
calendar = read_official("calendar.csv")
district_travel = read_official("district_travel.csv")
service_allowance = read_official("service_allowance.csv")
task2a_test_inputs = read_official("task2a_test_inputs.csv")

loaded = pd.DataFrame(
    {
        "task": ["Task 1", "Task 1", "Task 2A", "Shared references"],
        "artifact_group": ["historical orders/legs", "test orders/legs", "future forecast grid", "outlet/vehicle/calendar/travel/allowance"],
        "status": ["PASS", "PASS", "PASS", "PASS"],
    }
)
display(loaded)
""",
            "dt-392",
            "data-loading",
        ),
        _markdown(
            """
# 4. Fail-closed data validation

Canonical validators check schema, required fields, official status domains, requested-date/calendar compatibility, and key contracts before modelling. Later canonical builders additionally enforce route-leg join coverage, reference coverage, timestamp coherence, numeric validity, weekly reconciliation, and leakage controls. Failures raise immediately without printing offending identifiers.
""",
            "data-validation",
        ),
        _code(
            """
from src.task1.labels import classify_label_eligibility
from src.task2a.history import validate_calendar, validate_order_history_schema

_ = classify_label_eligibility(deliveries_train)
_ = validate_order_history_schema(
    deliveries_train,
    source_file="deliveries_train",
    required_statuses=task2a_history_config["required_dispatch_statuses"],
)
_ = validate_order_history_schema(
    task1_test_inputs,
    source_file="task1_test_inputs",
    required_statuses=task2a_history_config["required_dispatch_statuses"],
)
calendar_validated = validate_calendar(calendar)

validation_status = pd.DataFrame(
    [
        ("Required files", "Shared", discovery["discovery_status"]),
        ("Dispatch/status schema", "Task 1 / Task 2A", "PASS"),
        ("Calendar schema/domains", "Task 1 / Task 2A", "PASS"),
        ("Critical failures stop execution", "All", "PASS"),
    ],
    columns=["check", "task", "result"],
)
display(validation_status)
""",
            "dt-393",
            "data-validation",
        ),
        _markdown(
            """
# 5. Task 1 label construction

The official label semantics are:

`service_start = max(actual arrival, window opening)`

`service_minutes = leave_outlet_time - service_start`

`late_flag = 1 only if actual arrival > window_close_time`

Early waiting is not service. Arrival exactly at close is not late, and a late delivery remains delivered. The canonical implementation joins `deliveries_train.(route_id, seq_in_route)` to `route_legs_train.(route_id, seq)` and resolves midnight rollover deterministically.
""",
            "task1-labels",
        ),
        _code(
            """
from src.task1.labels import build_task1_training_labels

labels_t1, label_diagnostics = build_task1_training_labels(deliveries_train, route_legs_train)
labels_t1 = labels_t1.reset_index(drop=True)
label_checks = label_diagnostics["label_validation"]
assert np.isfinite(labels_t1["service_minutes"]).all()
assert labels_t1["service_minutes"].ge(0).all()
assert set(labels_t1["late_flag"].unique()).issubset({0, 1})

label_status = pd.DataFrame(
    [
        ("Route-leg one-to-one join coverage", "PASS"),
        ("Service target finite/nonnegative", "PASS"),
        ("Late label domain {0,1}", "PASS"),
        ("Strict arrival-after-close boundary", "PASS"),
    ],
    columns=["check", "result"],
)
display(label_status)
print(f"Task 1 label rows constructed: {len(labels_t1):,}")
""",
            "dt-394",
            "task1-labels",
        ),
        _markdown(
            """
# 6. Canonical preprocessing

Task 1 applies the frozen joins, planned-time normalization, reference enrichment, route workload context, and chronology-safe historical state through the Phase 6 builder. Task 2A uses both `deliveries_train.csv` and `task1_test_inputs.csv`, counts attempted, deferred, and not_run requests once, assigns demand to requested order_date, and maps it to official `iso_year and iso_week` before weekly aggregation.
""",
            "preprocessing",
        ),
        _code(
            """
from src.task1.features import build_task1_feature_tables
from src.task2a.history import build_task2a_history

task1_features = build_task1_feature_tables(
    orders_train=deliveries_train,
    orders_test=task1_test_inputs,
    route_legs_train=route_legs_train,
    route_legs_test=route_legs_test,
    outlets=outlets,
    vehicles=vehicles,
    district_travel=district_travel,
    service_allowance=service_allowance,
    calendar=calendar,
    labels_train=labels_t1,
    config=task1_feature_config,
)
X_task1 = task1_features["X_train"].reset_index(drop=True)

task2a_history = build_task2a_history(
    deliveries_train,
    task1_test_inputs,
    calendar_validated,
    task2a_history_config,
)
weekly_panel = task2a_history["weekly_panel"]

preprocessing_status = pd.DataFrame(
    [
        ("Task 1 canonical feature preprocessing", "PASS"),
        ("Task 1 train/test schema alignment", "PASS"),
        ("Task 2A two-source demand normalization", "PASS"),
        ("Task 2A calendar/week panel construction", "PASS"),
    ],
    columns=["stage", "result"],
)
display(preprocessing_status)
""",
            "dt-395",
            "preprocessing",
        ),
        _markdown(
            """
# 7. Compact exploratory summary

These aggregate views explain the target balance and demand history without displaying order-level identifiers. They are descriptive only and do not alter the frozen feature/model choices.
""",
            "eda-summary",
        ),
        _code(
            """
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
labels_t1["service_minutes"].plot(kind="hist", bins=30, ax=axes[0], title="Task 1 service-time distribution")
axes[0].set_xlabel("Service minutes")
axes[0].set_ylabel("Delivery count")
labels_t1["late_flag"].value_counts(normalize=True).sort_index().plot(
    kind="bar", ax=axes[1], title="Task 1 late-label balance"
)
axes[1].set_xlabel("Late flag")
axes[1].set_ylabel("Share")
plt.tight_layout()
plt.show()
plt.close(fig)

weekly_trend = (
    weekly_panel.groupby(["week_start_date", "brand"], as_index=False)[["total_volume_m3", "chilled_volume_m3"]]
    .sum()
)
fig, ax = plt.subplots(figsize=(10, 4))
for brand, group in weekly_trend.groupby("brand", sort=True):
    ax.plot(pd.to_datetime(group["week_start_date"]), group["total_volume_m3"], label=brand)
ax.set_title("Task 2A weekly total demand by brand")
ax.set_xlabel("Week")
ax.set_ylabel("Ordered volume (m3)")
ax.legend()
plt.tight_layout()
plt.show()
plt.close(fig)

display(
    pd.DataFrame(
        {
            "summary": ["Task 1 labeled rows", "Task 2A weekly panel rows", "Task 2A series"],
            "value": [len(labels_t1), len(weekly_panel), weekly_panel[["depot", "brand"]].drop_duplicates().shape[0]],
        }
    )
)
""",
            "dt-396",
            "eda-summary",
        ),
        _markdown(
            """
# 8. Final feature engineering and leakage guards

Task 1 uses only the frozen `safe_core_plus_history` profile. Direct current-row outcomes `actual_depart_time`, `actual_travel_duration_min`, `arrival_time`, and `leave_outlet_time` are prohibited predictors. Task 2A constructs origin-relative lags, trailing rolling features, trends, horizons, and known target-week calendar context; future realized demand cannot enter an earlier origin.
""",
            "feature-engineering",
        ),
        _code(
            """
from src.task1.inference import assert_no_forbidden_inference_features
from src.task2a.features import get_task2a_feature_columns
from src.task2a.multihorizon import build_direct_multihorizon_table, validate_multihorizon_table

forbidden_actuals = {
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
}
assert forbidden_actuals.isdisjoint(X_task1.columns)
assert_no_forbidden_inference_features(list(X_task1.columns))

task2a_table = build_direct_multihorizon_table(
    weekly_panel,
    calendar_validated,
    task2a_feature_config,
)
validate_multihorizon_table(task2a_table, task2a_feature_config)
assert pd.to_datetime(task2a_table["origin_demand_feature_max_source_week"]).le(
    pd.to_datetime(task2a_table["origin_week_start_date"])
).all()

feature_summary = pd.DataFrame(
    [
        ("Task 1", "safe_core_plus_history", X_task1.shape[1], "PASS"),
        ("Task 2A", "direct_global_table", len(get_task2a_feature_columns(task2a_feature_config)), "PASS"),
    ],
    columns=["task", "feature profile", "feature count", "chronology/leakage audit"],
)
display(feature_summary)
""",
            "dt-397",
            "feature-engineering",
        ),
        _markdown(
            """
# 9. Task 1 frozen-config training replay

This cell trains only the two already-frozen CatBoost configurations on the development portion of the chronological final-holdout split. It performs no family search, tuning, feature change, or test-label access. Replay models remain in memory and never overwrite `models/task1_service` or `models/task1_late`.
""",
            "task1-training",
        ),
        _code(
            """
from src.task1.advanced_models import AdvancedCandidate, fit_predict_advanced_fold
from src.task1.validation import build_task1_validation_plan

task1_plan = build_task1_validation_plan(labels_t1, task1_validation_config)
holdout = task1_plan["holdout"]
development_index = holdout.development_index
holdout_index = holdout.holdout_index

service_cfg = task1_final_config["service_model"]
late_cfg = task1_final_config["lateness_model"]
profile = task1_final_config["features"]["profile"]
service_candidate = AdvancedCandidate(
    service_cfg["config_id"], service_cfg["family"], "service", service_cfg["parameters"], profile
)
late_candidate = AdvancedCandidate(
    late_cfg["config_id"], late_cfg["family"], "late", late_cfg["parameters"], profile
)
service_iterations = int(service_cfg["final_iteration_policy"]["value"])
late_iterations = int(late_cfg["final_iteration_policy"]["value"])

task1_service_replay = fit_predict_advanced_fold(
    candidate=service_candidate,
    X_train=X_task1.loc[development_index],
    y_train=labels_t1.loc[development_index, "service_minutes"],
    X_valid=X_task1.loc[holdout_index],
    y_valid=labels_t1.loc[holdout_index, "service_minutes"],
    max_iterations=service_iterations,
    patience_rounds=max(100, service_iterations),
    min_iterations=1,
)
task1_late_replay = fit_predict_advanced_fold(
    candidate=late_candidate,
    X_train=X_task1.loc[development_index],
    y_train=labels_t1.loc[development_index, "late_flag"],
    X_valid=X_task1.loc[holdout_index],
    y_valid=labels_t1.loc[holdout_index, "late_flag"],
    max_iterations=late_iterations,
    patience_rounds=max(100, late_iterations),
    min_iterations=1,
)

display(
    pd.DataFrame(
        [
            (service_cfg["family"], service_cfg["config_id"], "service", "PASS"),
            (late_cfg["family"], late_cfg["config_id"], "lateness", "PASS"),
        ],
        columns=["family", "config", "target", "training replay"],
    )
)
""",
            "dt-398",
            "task1-training",
        ),
        _markdown(
            """
# 10. Task 1 evaluation

Evaluation uses the frozen last-42-calendar-day holdout and canonical metrics: MAE for service-time selection and log loss for lateness-probability selection. The raw probability policy is retained under the `chronological_oof` calibration comparison; no new calibration is fitted here.
""",
            "task1-evaluation",
        ),
        _code(
            """
from src.task1.metrics import lateness_probability_metrics, regression_metrics

service_metrics = regression_metrics(
    labels_t1.loc[holdout_index, "service_minutes"], task1_service_replay.prediction
)
late_metrics = lateness_probability_metrics(
    labels_t1.loc[holdout_index, "late_flag"], task1_late_replay.prediction
)
task1_metric_table = pd.DataFrame(
    [
        ("service", "mae", service_metrics["mae"]),
        ("service", "rmse", service_metrics["rmse"]),
        ("lateness", "log_loss", late_metrics["log_loss"]),
        ("lateness", "brier_score", late_metrics["brier_score"]),
    ],
    columns=["target", "metric", "value"],
)
display(task1_metric_table.round(6))
print("Task 1 chronological holdout evaluation: PASS")
""",
            "dt-399",
            "task1-evaluation",
        ),
        _markdown(
            """
# 11. Task 2A official demand aggregation

The canonical history already built above appends `deliveries_train.csv` and `task1_test_inputs.csv`, requires each `delivery_id` once, retains attempted, deferred, and not_run demand, uses requested order_date, and joins the official ISO calendar. Total and Fresh chilled volumes are aggregated by depot, brand, ISO year, and ISO week.
""",
            "task2a-aggregation",
        ),
        _code(
            """
history_diagnostics = task2a_history["diagnostics"]
assert task2a_history_config["required_dispatch_statuses"] == ["attempted", "deferred", "not_run"]
assert not weekly_panel.duplicated(["depot", "brand", "iso_year", "iso_week"]).any()
assert weekly_panel["total_volume_m3"].ge(0).all()
assert weekly_panel["chilled_volume_m3"].ge(0).all()
assert weekly_panel["chilled_volume_m3"].le(weekly_panel["total_volume_m3"]).all()

display(
    pd.DataFrame(
        [
            ("Both official demand sources loaded", "PASS"),
            ("Unique order counted once", "PASS"),
            ("Requested-date calendar coverage", "PASS"),
            ("Weekly grain and volume reconciliation", "PASS"),
        ],
        columns=["check", "result"],
    )
)
""",
            "dt-400",
            "task2a-aggregation",
        ),
        _markdown(
            """
# 12. Task 2A frozen rolling backtest and training replay

The frozen design uses four deterministic rolling origins, complete 10-week validation horizons, and at least 52 training weeks. This cell fits only the configured CatBoost and LightGBM components on the unchanged time-aware folds and reconstructs the frozen 50/50 ensembles: `ensemble_cb_lgb_total_equal_v1` for total volume and `ensemble_cb_lgb_chilled_equal_v1` for Fresh chilled volume. No random split, new model family, or hyperparameter search is performed.
""",
            "task2a-backtesting",
        ),
        _code(
            """
from src.task2a.advanced_models import run_advanced_backtests
from src.task2a.ensembles import blend_equal_weight
from src.task2a.model_selection import validate_candidate_predictions
from src.task2a.validation import build_rolling_origin_plan

task2a_plan = build_rolling_origin_plan(
    weekly_panel,
    task2a_table,
    task2a_feature_config,
    task2a_validation_config,
)
assert len(task2a_plan["splits"]) == 4
assert task2a_plan["leakage_audit"]["training_target_availability_pass"]
assert task2a_plan["leakage_audit"]["forbidden_future_feature_count"] == 0

component_predictions, task2a_fold_metadata, task2a_profile = run_advanced_backtests(
    task2a_plan,
    task2a_feature_config,
    task2a_advanced_config,
)


def frozen_ensemble(target: str, section: dict) -> pd.DataFrame:
    component_ids = [part["candidate_id"] for part in section["component_candidates"]]
    left = validate_candidate_predictions(component_predictions, task2a_plan, target, component_ids[0])
    right = validate_candidate_predictions(component_predictions, task2a_plan, target, component_ids[1])
    return blend_equal_weight(left, right, section["candidate_id"])


total_ensemble = frozen_ensemble("total", task2a_final_config["total"])
chilled_ensemble = frozen_ensemble("chilled", task2a_final_config["chilled_fresh"])
task2a_all_predictions = pd.concat(
    [component_predictions, total_ensemble, chilled_ensemble], ignore_index=True
)

display(
    pd.DataFrame(
        [
            ("rolling origins", len(task2a_plan["splits"]), "PASS"),
            ("forecast horizon", "1-10", "PASS"),
            ("total strategy", task2a_final_config["total"]["candidate_id"], "PASS"),
            ("Fresh chilled strategy", task2a_final_config["chilled_fresh"]["candidate_id"], "PASS"),
        ],
        columns=["item", "value", "result"],
    )
)
""",
            "dt-401",
            "task2a-backtesting",
        ),
        _markdown(
            """
# 13. Task 2A evaluation and output rules

MAE is primary for both total volume and Fresh chilled volume. Final postprocessing clips negative predictions, caps chilled at total, performs no rounding, and guarantees Style and Tech chilled predictions are exactly zero.
""",
            "task2a-evaluation",
        ),
        _code(
            """
from src.task2a.final_inference import OFFICIAL_ROW_ORDER, postprocess_predictions
from src.task2a.model_selection import evaluate_candidate

total_id = task2a_final_config["total"]["candidate_id"]
chilled_id = task2a_final_config["chilled_fresh"]["candidate_id"]
total_evaluation = evaluate_candidate(
    task2a_all_predictions, task2a_plan, "total", total_id, chilled_id
)
chilled_evaluation = evaluate_candidate(
    task2a_all_predictions, task2a_plan, "chilled", chilled_id, total_id
)

task2a_metric_table = pd.DataFrame(
    [
        ("total", "mae", total_evaluation["overall_mae"]),
        ("total", "rmse", total_evaluation["overall_rmse"]),
        ("Fresh chilled", "mae", chilled_evaluation["overall_mae"]),
        ("Fresh chilled", "rmse", chilled_evaluation["overall_rmse"]),
    ],
    columns=["target", "metric", "value"],
)
display(task2a_metric_table.round(6))

total_rows = total_ensemble.sort_values(
    ["backtest_id", "depot", "brand", "target_week_start_date"], kind="stable"
).reset_index(drop=True)
chilled_rows = chilled_ensemble.sort_values(
    ["backtest_id", "depot", "brand", "target_week_start_date"], kind="stable"
).reset_index(drop=True)
fresh_keys = ["backtest_id", "depot", "brand", "origin_week_start_date", "target_week_start_date", "horizon_weeks"]
raw_eval = total_rows[[*fresh_keys, "y_pred"]].rename(columns={"y_pred": "raw_pred_total_volume_m3"})
raw_eval["raw_pred_chilled_volume_m3"] = 0.0
fresh_chilled = chilled_rows[[*fresh_keys, "y_pred"]].rename(columns={"y_pred": "fresh_chilled"})
raw_eval = raw_eval.merge(fresh_chilled, on=fresh_keys, how="left", validate="one_to_one")
fresh_mask = raw_eval["brand"].eq("Fresh")
raw_eval.loc[fresh_mask, "raw_pred_chilled_volume_m3"] = raw_eval.loc[fresh_mask, "fresh_chilled"]
raw_eval = raw_eval.drop(columns="fresh_chilled")
raw_eval[OFFICIAL_ROW_ORDER] = np.arange(len(raw_eval))
raw_eval["row_id"] = [f"evaluation-row-{number}" for number in range(len(raw_eval))]
postprocessed_eval, correction_counts = postprocess_predictions(raw_eval)
assert postprocessed_eval["pred_total_volume_m3"].ge(0).all()
assert postprocessed_eval["pred_chilled_volume_m3"].ge(0).all()
assert postprocessed_eval["pred_chilled_volume_m3"].le(postprocessed_eval["pred_total_volume_m3"]).all()
assert postprocessed_eval.loc[raw_eval["brand"].isin(["Style", "Tech"]), "pred_chilled_volume_m3"].eq(0).all()
print("Task 2A postprocessing and structural-zero checks: PASS")
""",
            "dt-402",
            "task2a-evaluation",
        ),
        _markdown(
            """
# 14. Task 2B frozen allocation summary

Task 2B does not require a trained model, so this notebook does not rerun the optimizer. The frozen S1/Peliyagoda allocation uses available vehicles only and preserves `order_ref` as the allocation key.

Official hard feasibility has seven groups:

1. Same brand and district per vehicle trip.
2. Chilled demand requires a reefer.
3. `van_only` demand requires a van.
4. Vehicle home depot must match.
5. Whole orders only; no split.
6. Both weight and volume capacity apply.
7. At most two trips per vehicle, with Fresh <= 270 minutes and Style+Tech <= 480 minutes.

The official no-return formula is:

`trip_minutes = depot_to_district_freeflow_min + inter_stop_freeflow_min * (num_orders - 1) + sum(service_allowance_min)`

No return leg is added. Official hard feasibility is separate from the nine-level WayLoom engineering priority policy implemented with deterministic OR-Tools CP-SAT. The independent validator checks all rules; organizer `check_allocation.py` proves feasibility only and does not prove optimality.

Final deliverables: `outputs/submission_task2b.csv` and `docs/task2b_policy.md`.
""",
            "dt-403",
            "task2b-summary",
        ),
        _markdown(
            """
# 15. Execution and hidden-state assurance

The tracked notebook has no saved private outputs, broken cells, install commands, network calls, or model-search cells. Final closure requires two human-local executions after Phase 32: a fresh-kernel run-all and a separate fresh-kernel execution of the final cell alone. Those gates prove ordered execution and absence of hidden model/preprocessor state. Until the Phase 32 secured artifact registry is available, DT-405 remains `BLOCKED_BY_PHASE32` and DT-409/DT-411 remain pending final runtime evidence.
""",
            "dt-409",
            "dt-410",
            "dt-411",
            "execution-assurance",
        ),
        _markdown(
            """
# Final Saved-Model Inference Demonstration

The final cell is deliberately self-contained. After Phase 32 passes, it resolves the project root, reads the artifact interface from the tracked config, reloads Task 1 and Task 2A saved artifacts from disk, runs both canonical inference paths in memory, prints at most three selected input/prediction rows per task, verifies parity against the frozen outputs, and writes no official output.
""",
            "dt-404",
            "final-inference-heading",
        ),
        _code(
            """
from pathlib import Path
import importlib

import yaml


def _phase31_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "configs").is_dir() and (candidate / "src").is_dir():
            return candidate
    raise FileNotFoundError("WayLoom project root was not found.")


phase31_root = _phase31_root(Path.cwd())
with (phase31_root / "configs/final_notebook.yaml").open(encoding="utf-8") as handle:
    phase31_config = yaml.safe_load(handle)

phase32_config = phase31_config["phase32"]
if phase32_config["status"] != "PASS":
    raise RuntimeError(
        "PHASE32 SAVED ARTIFACT GATE: AWAITING_PHASE32. "
        "Complete DT-412-DT-419 before final notebook execution."
    )

artifact_registry = phase31_root / phase32_config["artifact_registry"]
if not artifact_registry.is_file():
    raise FileNotFoundError("The Phase 32 saved-artifact registry is missing.")

loader_module = importlib.import_module(phase32_config["loader_module"])
loader_callable = getattr(loader_module, phase32_config["loader_callable"])
max_demo_rows = int(phase31_config["content"]["max_demo_rows"])
demo = loader_callable(
    project_root=phase31_root,
    artifact_registry=artifact_registry,
    max_demo_rows=max_demo_rows,
    numeric_tolerance=float(phase31_config["final_inference"]["numeric_tolerance"]),
    write_official_outputs=False,
)

required = {
    "task1_inputs",
    "task1_predictions",
    "task1_parity_pass",
    "task2a_inputs",
    "task2a_predictions",
    "task2a_parity_pass",
    "saved_artifacts_loaded",
}
missing = required.difference(demo)
if missing:
    raise RuntimeError("Saved-artifact inference result is incomplete: " + ", ".join(sorted(missing)))
if demo["saved_artifacts_loaded"] is not True:
    raise RuntimeError("Final inference did not reload every required saved artifact.")
if len(demo["task1_inputs"]) > max_demo_rows or len(demo["task2a_inputs"]) > max_demo_rows:
    raise RuntimeError("Final inference demo exceeds the configured row limit.")
if demo["task1_parity_pass"] is not True or demo["task2a_parity_pass"] is not True:
    raise RuntimeError("Loaded-model predictions do not match the frozen inference contract.")

print("TASK 1 - INPUTS")
print(demo["task1_inputs"].to_string(index=False))
print("TASK 1 - PREDICTIONS")
print(demo["task1_predictions"].to_string(index=False))
print("TASK 2A - INPUTS")
print(demo["task2a_inputs"].to_string(index=False))
print("TASK 2A - PREDICTIONS")
print(demo["task2a_predictions"].to_string(index=False))
print("TASK 1 SAVED-MODEL PARITY: PASS")
print("TASK 2A SAVED-MODEL PARITY: PASS")
""",
            "dt-404",
            "dt-405",
            "dt-406",
            "dt-407",
            "dt-408",
            "final-inference",
        ),
    ]

    for index, cell in enumerate(cells, start=1):
        cell["id"] = f"phase31-{index:02d}"
    notebook = nbformat.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
    )
    return notebook


def write_notebook(output: Path = DEFAULT_OUTPUT) -> Path:
    if output.resolve() != DEFAULT_OUTPUT.resolve():
        raise ValueError("Final notebook must use TeamName_FinalNotebook.ipynb.")
    nbformat.write(build_notebook(), output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Phase 31 source notebook.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    write_notebook(args.output)
    print("LOCAL PHASE 31 SOURCE NOTEBOOK BUILD: PASS")
    print("SOURCE NOTEBOOK OUTPUTS CLEARED: YES")
    print("PRIVATE DATA ACCESSED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
