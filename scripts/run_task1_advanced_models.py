"""Local-only Phase 09 development experiment runner (development folds only)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.task1.advanced_models import (  # noqa: E402
    build_phase09_candidates,
    fit_predict_advanced_fold,
    high_confidence_classification_errors,
    overfitting_summary,
    worst_regression_errors,
    xgboost_available,
)
from src.task1.baselines import aggregate_fold_results, evaluate_baseline_fold  # noqa: E402
from src.task1.calibration import (  # noqa: E402
    calibrate_isotonic,
    calibrate_sigmoid,
    chronological_calibration_split,
    compare_probability_variants,
    reliability_table,
)
from src.task1.model_selection import assert_same_fold_contract, select_lateness_candidate, select_regression_candidate  # noqa: E402
from src.task1.validation import build_task1_validation_plan, load_task1_validation_config  # noqa: E402


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run Phase 09 Task 1 advanced models on development folds only.")
    p.add_argument("--features", type=Path, required=True)
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--feature-registry", type=Path, required=True)
    p.add_argument("--validation-config", type=Path, required=True)
    p.add_argument("--baseline-results", type=Path, required=True)
    p.add_argument("--model-config", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p


def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _git_hash() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
    except Exception:
        return None


def main() -> int:
    args = parser().parse_args()
    X = pd.read_csv(args.features, low_memory=False)
    labels = pd.read_csv(args.labels, low_memory=False)
    if len(X) != len(labels):
        raise ValueError("Feature/label row count mismatch.")
    model_cfg = _read_yaml(args.model_config)
    if model_cfg.get("validation", {}).get("use_final_holdout_during_search") is not False:
        raise ValueError("Phase 09 development cannot use the final holdout.")
    private_root = (PROJECT_ROOT / "reports" / "private").resolve()
    if not args.output_dir.resolve().is_relative_to(private_root):
        raise ValueError("Private output must remain under reports/private/.")
    validation_cfg = load_task1_validation_config(args.validation_config)
    plan = build_task1_validation_plan(labels, validation_cfg)
    y_service = labels["service_minutes"]
    y_late = labels["late_flag"]
    date_col = "route_date" if "route_date" in labels.columns else "date"
    seg = validation_cfg["segments"]

    # Baseline compatibility.
    baseline_file = args.baseline_results / "fold_results.csv"
    baseline_rows = pd.read_csv(baseline_file) if baseline_file.exists() else pd.DataFrame()

    svc_rows: list[dict] = []
    late_rows: list[dict] = []
    segment_rows: list[dict] = []
    oof_rows: list[dict] = []
    service_pred_rows: list[dict] = []
    late_pred_rows: list[dict] = []
    failed_folds: list[dict] = []

    early = model_cfg["early_stopping"]
    max_iter = int(early["max_iterations"])
    patience = int(early["patience_rounds"])
    min_iter = int(early["min_iterations"])
    seed = int(model_cfg.get("seed", 42))

    candidates = build_phase09_candidates(model_cfg)
    xgb_status = "NOT_RUN_OPTIONAL"
    if bool(model_cfg["xgboost"]["enabled"]):
        if not xgboost_available():
            raise ValueError("xgboost enabled in config but dependency is unavailable.")
        xgb_status = "READY"
    candidate_lookup = {c.candidate_id: c for c in candidates}

    for fold in plan["folds"]:
        tr, va = fold.train_index, fold.validation_index
        Xtr, Xva = X.loc[tr], X.loc[va]
        ys_tr, ys_va = y_service.loc[tr], y_service.loc[va]
        yl_tr, yl_va = y_late.loc[tr], y_late.loc[va]
        for candidate in candidates:
            if candidate.target == "service":
                result = fit_predict_advanced_fold(
                    candidate=candidate, X_train=Xtr, y_train=ys_tr, X_valid=Xva, y_valid=ys_va,
                    max_iterations=max_iter, patience_rounds=patience, min_iterations=min_iter,
                )
                rows, segments = evaluate_baseline_fold(
                    model_name=candidate.candidate_id, target="service", fold=fold, y_valid=ys_va, prediction=result.prediction,
                    segment_frame=Xva, segment_fields=seg["fields"], segment_config=seg,
                )
                for r in rows:
                    r.update(
                        {
                            "candidate_id": candidate.candidate_id,
                            "model_family": candidate.family,
                            "feature_profile": candidate.feature_profile,
                            "best_iteration": result.best_iteration,
                            "train_metric": result.train_metric,
                            "validation_metric": result.validation_metric,
                            "stopped_early": result.stopped_early,
                            "max_iterations": result.max_iterations,
                            "training_seconds": result.training_seconds,
                            "warning_codes": ",".join(result.warning_codes),
                        }
                    )
                svc_rows.extend(rows)
                for dt, yt, yp, (_, xr) in zip(labels.loc[va, date_col], ys_va, result.prediction, Xva.iterrows()):
                    service_pred_rows.append(
                        {
                            "candidate_id": candidate.candidate_id,
                            "fold_id": fold.fold,
                            "validation_date": str(pd.Timestamp(dt).date()),
                            "service_minutes": float(yt),
                            "pred_service_min": float(yp),
                            "brand": xr.get("brand"),
                            "depot": xr.get("depot"),
                            "district": xr.get("district"),
                            "dock_type": xr.get("dock_type"),
                        }
                    )
                for s in segments:
                    s["candidate_id"] = candidate.candidate_id
                    s["model_family"] = candidate.family
                    s["feature_profile"] = candidate.feature_profile
                segment_rows.extend(segments)
            else:
                try:
                    result = fit_predict_advanced_fold(
                        candidate=candidate, X_train=Xtr, y_train=yl_tr, X_valid=Xva, y_valid=yl_va,
                        max_iterations=max_iter, patience_rounds=patience, min_iterations=min_iter,
                    )
                except Exception as exc:
                    failed_folds.append(
                        {
                            "candidate_id": candidate.candidate_id,
                            "target": "late",
                            "fold_id": fold.fold,
                            "error": str(exc),
                        }
                    )
                    continue
                rows, segments = evaluate_baseline_fold(
                    model_name=candidate.candidate_id, target="late", fold=fold, y_valid=yl_va, prediction=result.prediction,
                    segment_frame=Xva, segment_fields=seg["fields"], segment_config=seg,
                )
                for r in rows:
                    r.update(
                        {
                            "candidate_id": candidate.candidate_id,
                            "model_family": candidate.family,
                            "feature_profile": candidate.feature_profile,
                            "best_iteration": result.best_iteration,
                            "train_metric": result.train_metric,
                            "validation_metric": result.validation_metric,
                            "stopped_early": result.stopped_early,
                            "max_iterations": result.max_iterations,
                            "training_seconds": result.training_seconds,
                            "warning_codes": ",".join(result.warning_codes),
                        }
                    )
                late_rows.extend(rows)
                for s in segments:
                    s["candidate_id"] = candidate.candidate_id
                    s["model_family"] = candidate.family
                    s["feature_profile"] = candidate.feature_profile
                segment_rows.extend(segments)
                oof_rows.extend(
                    [
                        {
                            "candidate_id": candidate.candidate_id,
                            "fold_id": fold.fold,
                            "validation_date": str(pd.Timestamp(d).date()),
                            "pred_late_prob": p,
                            "late_flag": y,
                        }
                        for d, p, y in zip(labels.loc[va, date_col], result.prediction, yl_va)
                    ]
                )
                for dt, yt, yp, (_, xr) in zip(labels.loc[va, date_col], yl_va, result.prediction, Xva.iterrows()):
                    late_pred_rows.append(
                        {
                            "candidate_id": candidate.candidate_id,
                            "fold_id": fold.fold,
                            "validation_date": str(pd.Timestamp(dt).date()),
                            "late_flag": float(yt),
                            "pred_late_prob": float(yp),
                            "brand": xr.get("brand"),
                            "depot": xr.get("depot"),
                            "district": xr.get("district"),
                            "dock_type": xr.get("dock_type"),
                        }
                    )

    svc_df = pd.DataFrame(svc_rows)
    late_df = pd.DataFrame(late_rows)
    comparison = pd.concat([svc_df, late_df], ignore_index=True)
    assert_same_fold_contract(
        comparison[["target", "candidate_id", "fold_id", "train_start_date", "train_end_date", "validation_start_date", "validation_end_date"]]
        .drop_duplicates()
        .rename(columns={"model_name": "candidate_id"})
    )

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    if failed_folds:
        pd.DataFrame(failed_folds).to_csv(out / "failed_folds.csv", index=False)
        raise ValueError("One or more candidate folds failed; see failed_folds.csv.")
    svc_df.to_csv(out / "service_cv_results.csv", index=False)
    late_df.to_csv(out / "late_cv_results.csv", index=False)
    segment_df = pd.DataFrame(segment_rows)
    segment_df.to_csv(out / "segment_diagnostics.csv", index=False)
    if not segment_df.empty:
        segment_df[segment_df["segment"] == "brand"].to_csv(out / "brand_metrics.csv", index=False)
        segment_df[segment_df["segment"] == "depot"].to_csv(out / "depot_metrics.csv", index=False)
    aggregate_fold_results(comparison).to_csv(out / "model_summary.csv", index=False)
    overfitting_summary(
        comparison[["candidate_id", "target", "fold_id", "train_metric", "validation_metric", "best_iteration", "max_iterations"]].drop_duplicates()
    ).to_csv(out / "overfitting_summary.csv", index=False)

    if not svc_df.empty:
        svc_pred_df = pd.DataFrame(service_pred_rows)
        worst_regression_errors(svc_pred_df, n_top=int(model_cfg["error_analysis"]["worst_regression_n"])).to_csv(
            out / "regression_error_summary.csv", index=False
        )

    oof_df = pd.DataFrame(oof_rows)
    late_pred_df = pd.DataFrame(late_pred_rows)
    if not oof_df.empty:
        raw = oof_df[oof_df["candidate_id"] == "catboost_classifier_default"].copy()
        if not raw.empty:
            split = chronological_calibration_split(raw, date_col="validation_date", fit_fraction=float(model_cfg["calibration"]["oof_fit_fraction"]))
            fit_df = raw.loc[split.fit_index]
            eval_df = raw.loc[split.eval_index]
            sigmoid = calibrate_sigmoid(fit_df["pred_late_prob"], fit_df["late_flag"], eval_df["pred_late_prob"])
            isotonic = calibrate_isotonic(
                fit_df["pred_late_prob"],
                fit_df["late_flag"],
                eval_df["pred_late_prob"],
                minimum_rows=int(model_cfg["calibration"]["minimum_calibration_rows"]),
            )
            variants = {"raw": eval_df["pred_late_prob"].to_numpy(dtype=float), "sigmoid": sigmoid}
            if isotonic is not None:
                variants["isotonic"] = isotonic
            compare_probability_variants(eval_df["late_flag"], variants).to_csv(out / "calibration_comparison.csv", index=False)
            reliability_table(eval_df["late_flag"], eval_df["pred_late_prob"], bins=10).to_csv(out / "calibration_curve.csv", index=False)
            high_confidence_classification_errors(
                late_pred_df[late_pred_df["candidate_id"] == "catboost_classifier_default"] if not late_pred_df.empty else eval_df,
                prob_col="pred_late_prob",
                label_col="late_flag",
                high_positive=float(model_cfg["error_analysis"]["confident_positive_threshold"]),
                high_negative=float(model_cfg["error_analysis"]["confident_negative_threshold"]),
            ).to_csv(out / "classification_error_summary.csv", index=False)

    service_summary = (
        svc_df.pivot_table(index="candidate_id", columns="metric_name", values="metric_value", aggfunc="mean").reset_index()
        if not svc_df.empty else pd.DataFrame(columns=["candidate_id"])
    )
    if not service_summary.empty:
        service_summary["target"] = "service"
        service_summary["fold_count"] = svc_df["fold_id"].nunique()
        service_summary["required_fold_count"] = svc_df["fold_id"].nunique()
        service_summary["status"] = "ok"
        service_summary["mae_std"] = (
            svc_df[svc_df["metric_name"] == "mae"].groupby("candidate_id")["metric_value"].std(ddof=0).reindex(service_summary["candidate_id"]).to_numpy()
        )
        service_summary["complexity_score"] = service_summary["candidate_id"].str.count("_")
    late_summary = (
        late_df.pivot_table(index="candidate_id", columns="metric_name", values="metric_value", aggfunc="mean").reset_index()
        if not late_df.empty else pd.DataFrame(columns=["candidate_id"])
    )
    if not late_summary.empty:
        late_summary["target"] = "late"
        late_summary["fold_count"] = late_df["fold_id"].nunique()
        late_summary["required_fold_count"] = late_df["fold_id"].nunique()
        late_summary["status"] = "ok"
        late_summary["log_loss_std"] = (
            late_df[late_df["metric_name"] == "log_loss"].groupby("candidate_id")["metric_value"].std(ddof=0).reindex(late_summary["candidate_id"]).to_numpy()
        )
        late_summary["complexity_score"] = late_summary["candidate_id"].str.count("_")
        late_summary["calibration_method"] = "raw"
        late_summary["calibration_protocol"] = "chronological_oof"
    select_df = pd.concat([service_summary, late_summary], ignore_index=True, sort=False)
    service_pick = select_regression_candidate(select_df)
    late_pick = select_lateness_candidate(select_df)
    def _iteration_for(candidate_id: str) -> int:
        it = comparison[comparison["candidate_id"] == candidate_id][["fold_id", "best_iteration"]].drop_duplicates()
        return int(it["best_iteration"].median()) if not it.empty else max_iter
    selection = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "service": {
            **service_pick,
            "family": candidate_lookup[service_pick["candidate_id"]].family,
            "feature_profile": candidate_lookup[service_pick["candidate_id"]].feature_profile,
            "parameters": candidate_lookup[service_pick["candidate_id"]].params,
            "final_iteration_policy": {"method": "median_best_iteration", "value": _iteration_for(service_pick["candidate_id"])},
        },
        "lateness": {
            **late_pick,
            "family": candidate_lookup[late_pick["candidate_id"]].family,
            "feature_profile": candidate_lookup[late_pick["candidate_id"]].feature_profile,
            "parameters": candidate_lookup[late_pick["candidate_id"]].params,
            "final_iteration_policy": {"method": "median_best_iteration", "value": _iteration_for(late_pick["candidate_id"])},
        },
        "xgboost_status": xgb_status,
    }
    (out / "provisional_selection.json").write_text(json.dumps(selection, indent=2), encoding="utf-8")
    manifest = {
        "phase": "09",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_hash(),
        "validation_config": str(args.validation_config),
        "model_config": str(args.model_config),
        "seed": seed,
        "final_holdout_used_during_development": "NO",
        "phase08_baseline_loaded": str(baseline_file.exists()),
    }
    if baseline_file.exists():
        merged = pd.concat([baseline_rows, comparison[["model_name", "target", "fold_id", "metric_name", "metric_value"]]], ignore_index=True, sort=False)
        merged.to_csv(out / "baseline_advanced_comparison.csv", index=False)
    (out / "candidate_registry.json").write_text(
        json.dumps(
            [
                {"candidate_id": c.candidate_id, "family": c.family, "target": c.target, "feature_profile": c.feature_profile, "params": c.params}
                for c in candidates
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("PHASE 09 DEVELOPMENT EXPERIMENT RUNNER: READY")
    print("Final holdout used during development: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
