r"""Human-local, selected-frozen-ensemble Task 2A charts. Never run via an AI agent.

Run from repository root:
  .\.venv\Scripts\python.exe scripts\plot_internal_task2a.py

Inputs: configs/task2a_final_models.yaml, configs/task2a_validation.yaml,
reports/private/phase16_task2a_advanced/{selection_decisions.json,
run_manifest.json,candidate_predictions.csv,<selected>_per_horizon.csv},
data/interim/task2a_weekly_observed.csv. No baseline or unselected candidate is
ever plotted. Raw rolling-origin backtests are distinct from the final 10-week
submission forecast and may contain negatives before Phase 17 postprocessing.

Outputs: reports/private/internal_results_charts/
  task2a_backtest_actual_vs_predicted.png
  task2a_historical_total_vs_chilled.png
  task2a_selected_ensemble_horizon_mae.png
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from internal_charts_common import (
    ACCENT, BLUE, ChartEvidenceError, canvas, columns, csv_source,
    json_source, numeric, save, skip, yaml_source,
)

BASE = "reports/private/phase16_task2a_advanced"
KEYS = ("backtest_id", "depot", "brand", "origin_week_start_date",
        "target_week_start_date", "horizon_weeks")


def selected_rows() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    frozen = yaml_source("configs/task2a_final_models.yaml")
    validation = yaml_source("configs/task2a_validation.yaml")
    selection = json_source(f"{BASE}/selection_decisions.json", private=True)
    run = json_source(f"{BASE}/run_manifest.json", private=True)
    signature = frozen.get("validation", {}).get("backtest_signature")
    registry = frozen.get("feature_profile", {}).get("registry_hash")
    total_id = frozen.get("total", {}).get("candidate_id")
    chilled_id = frozen.get("chilled_fresh", {}).get("candidate_id")
    if (frozen.get("state") != "FROZEN" or frozen.get("selection_complete") is not True
            or not signature or not registry
            or selection.get("selection_complete") is not True
            or selection.get("total", {}).get("candidate_id") != total_id
            or selection.get("chilled_fresh", {}).get("candidate_id") != chilled_id
            or selection.get("phase14_backtest_signature") != signature
            or selection.get("feature_registry_hash") != registry
            or run.get("phase") != 16
            or run.get("phase14_backtest_signature") != signature
            or run.get("feature_registry_hash") != registry
            or run.get("phase15_references_verified") is not True
            or run.get("required_backtest_count") != 4
            or validation.get("backtesting", {}).get("n_backtests") != 4
            or validation.get("backtesting", {}).get("validation_horizon_weeks") != 10
            or validation.get("prediction_diagnostics", {}).get("apply_phase17_postprocessing") is not False):
        raise ChartEvidenceError("Frozen Task 2A selection/backtest metadata disagree.")
    frame = csv_source(f"{BASE}/candidate_predictions.csv", private=True)
    columns(frame, (*KEYS, "target_name", "candidate_id", "y_true", "y_pred",
                    "phase14_backtest_signature"))
    if frame.phase14_backtest_signature.isna().any() or not frame.phase14_backtest_signature.eq(signature).all():
        raise ChartEvidenceError("Candidate table contains another backtest signature.")
    selected = {}
    for target, candidate in (("total", total_id), ("chilled", chilled_id)):
        part = frame.loc[frame.target_name.eq(target) & frame.candidate_id.eq(candidate)].copy()
        if (part.empty or part[list(KEYS)].isna().any().any()
                or part.duplicated(list(KEYS)).any()
                or part.backtest_id.nunique() != 4
                or (target == "chilled" and not part.brand.eq("Fresh").all())):
            raise ChartEvidenceError("Selected candidate has incomplete or duplicate backtest keys.")
        part["horizon_weeks"] = numeric(part, "horizon_weeks")
        part["y_true"] = numeric(part, "y_true", nonnegative=True)
        part["y_pred"] = numeric(part, "y_pred")
        for _, group in part.groupby(["backtest_id", "depot", "brand"], dropna=False):
            if sorted(group.horizon_weeks.tolist()) != list(range(1, 11)):
                raise ChartEvidenceError("Selected series lacks exact horizons 1..10.")
        selected[target] = part
    total, chilled = selected["total"], selected["chilled"]
    if set(chilled.backtest_id) != set(total.backtest_id):
        raise ChartEvidenceError("Total and chilled backtest populations differ.")
    paired = chilled[list(KEYS)].merge(
        total.loc[total.brand.eq("Fresh"), list(KEYS)],
        on=list(KEYS), how="outer", indicator=True, validate="one_to_one")
    if not paired._merge.eq("both").all():
        raise ChartEvidenceError("Fresh total and chilled validation keys differ.")
    return total, chilled, {"total": total_id, "chilled": chilled_id}


def actual_vs_predicted(total: pd.DataFrame, chilled: pd.DataFrame) -> None:
    fig, ax = canvas("Task 2A · actual vs predicted backtest demand",
                     "Four rolling origins · frozen selected ensembles · raw pre-Phase-17 predictions",
                     "Predicted weekly requested demand (m³)")
    ax.scatter(total.y_true, total.y_pred, s=13, alpha=0.28, color=BLUE, label="Total")
    ax.scatter(chilled.y_true, chilled.y_pred, s=13, alpha=0.38, color=ACCENT, label="Fresh chilled")
    low = min(float(total.y_true.min()), float(total.y_pred.min()),
              float(chilled.y_true.min()), float(chilled.y_pred.min()))
    high = max(float(total.y_true.max()), float(total.y_pred.max()),
               float(chilled.y_true.max()), float(chilled.y_pred.max()))
    ax.plot([low, high], [low, high], color="#94A3B8", label="Perfect agreement")
    ax.set_xlabel("Actual weekly requested demand (m³)")
    ax.legend(frameon=False)
    save(fig, "task2a_backtest_actual_vs_predicted.png")


def history() -> None:
    frame = csv_source("data/interim/task2a_weekly_observed.csv")
    columns(frame, ("depot", "brand", "iso_year", "iso_week", "total_volume_m3", "chilled_volume_m3"))
    if frame[["depot", "brand", "iso_year", "iso_week"]].isna().any().any() or frame.duplicated(
            ["depot", "brand", "iso_year", "iso_week"]).any():
        raise ChartEvidenceError("Observed weekly series keys are invalid.")
    for name in ("total_volume_m3", "chilled_volume_m3"):
        frame[name] = numeric(frame, name, nonnegative=True)
    if (frame.chilled_volume_m3 > frame.total_volume_m3).any():
        raise ChartEvidenceError("Observed chilled demand exceeds total.")
    fresh = frame.loc[frame.brand.eq("Fresh")].copy()
    if fresh.empty:
        raise ChartEvidenceError("Fresh observed weekly history is absent.")
    years = numeric(fresh, "iso_year")
    weeks = numeric(fresh, "iso_week")
    if (weeks < 1).any() or (weeks > 53).any() or not np.equal(weeks, np.floor(weeks)).all():
        raise ChartEvidenceError("Observed ISO weeks are invalid.")
    fresh["week"] = pd.to_datetime(
        years.astype(int).astype(str) + "-W" + weeks.astype(int).astype(str).str.zfill(2) + "-1",
        format="%G-W%V-%u", errors="coerce")
    if fresh.week.isna().any():
        raise ChartEvidenceError("Observed ISO week rollover is invalid.")
    weekly = fresh.groupby("week", sort=True)[["total_volume_m3", "chilled_volume_m3"]].sum()
    fig, ax = canvas("Task 2A · historical Fresh demand",
                     "Observed requested-demand weeks · summed across depots · includes deferred demand",
                     "Weekly requested demand (m³)")
    ax.plot(weekly.index, weekly.total_volume_m3, color=BLUE, linewidth=2.2, label="Total")
    ax.plot(weekly.index, weekly.chilled_volume_m3, color=ACCENT, linewidth=2.2, label="Chilled")
    ax.set_xlabel("Official ISO week start")
    ax.legend(frameon=False)
    save(fig, "task2a_historical_total_vs_chilled.png")


def horizon(total: pd.DataFrame, chilled: pd.DataFrame, ids: dict) -> None:
    curves = {}
    for target, frame in (("total", total), ("chilled", chilled)):
        report = csv_source(f"{BASE}/{ids[target]}_per_horizon.csv", private=True)
        columns(report, ("target", "horizon_weeks", "n", "mae"))
        if len(report) != 10 or not report.target.eq(target).all():
            raise ChartEvidenceError("Selected horizon report has wrong target/coverage.")
        report["horizon_weeks"] = numeric(report, "horizon_weeks")
        report["n"] = numeric(report, "n", nonnegative=True)
        report["mae"] = numeric(report, "mae", nonnegative=True)
        report = report.sort_values("horizon_weeks")
        if not np.array_equal(report.horizon_weeks, np.arange(1, 11)):
            raise ChartEvidenceError("Selected horizon report lacks horizons 1..10.")
        check = frame.assign(abs_error=(frame.y_pred - frame.y_true).abs()).groupby(
            "horizon_weeks", sort=True).agg(n=("abs_error", "size"), mae=("abs_error", "mean"))
        if (not np.array_equal(report.n.to_numpy(), check.n.to_numpy())
                or not np.allclose(report.mae, check.mae, atol=1e-8, rtol=1e-8)):
            raise ChartEvidenceError("Horizon diagnostics do not match selected prediction rows.")
        curves[target] = report
    fig, ax = canvas("Task 2A · selected-ensemble horizon diagnostics",
                     "Raw rolling-origin backtest MAE · selected total and Fresh chilled only; not future actuals",
                     "Mean absolute error (m³)")
    ax.plot(curves["total"].horizon_weeks, curves["total"].mae, marker="o", color=BLUE, label="Total")
    ax.plot(curves["chilled"].horizon_weeks, curves["chilled"].mae, marker="o", color=ACCENT, label="Fresh chilled")
    ax.set(xlabel="Forecast horizon (weeks)", xticks=range(1, 11))
    ax.legend(frameon=False)
    save(fig, "task2a_selected_ensemble_horizon_mae.png")


def main() -> int:
    try:
        total, chilled, ids = selected_rows()
    except (ChartEvidenceError, KeyError, ValueError):
        print("SKIPPED: Task 2A selected-model charts — frozen selection evidence is incomplete")
        return 1
    for job, name in (
        (lambda: actual_vs_predicted(total, chilled), "task2a_backtest_actual_vs_predicted.png"),
        (history, "task2a_historical_total_vs_chilled.png"),
        (lambda: horizon(total, chilled, ids), "task2a_selected_ensemble_horizon_mae.png"),
    ):
        try:
            job()
        except (ChartEvidenceError, KeyError, ValueError):
            skip(name, "source is missing or fails validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
