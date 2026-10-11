# Task 1 Feature Engineering Specification (Phase 06)

This document describes the tracked, leakage-safe Task 1 feature pipeline.

## Core Safety Contract

- Train/test feature logic is identical and deterministic.
- Final model matrices exclude direct actual journey and target-derived fields:
  - `actual_depart_time`
  - `actual_travel_duration_min`
  - `arrival_time`
  - `leave_outlet_time`
  - `service_start_dt`
  - `service_minutes`
  - `late_flag`
- Historical target aggregates are implemented only through fold-safe fit/transform logic in `Task1HistoricalFeatureTransformer`.

## Pipeline Modules

- `src/task1/features.py`
  - static/planned feature engineering
  - route/planned time/window features
  - calendar/environment/service-allowance features
  - ratio, route aggregate, and prior planned cumulative features
  - final train/test parity and leakage audit
- `src/task1/historical_features.py`
  - chronology-safe historical target features
  - strict earlier-date rule (`historical_date < row_date`)
  - same-day exclusion and fallback hierarchy
- `src/task1/feature_registry.py`
  - complete metadata registry for final feature columns
  - required metadata fields
  - safety/consistency validations

## Historical Target Features (DT-119)

- `outlet_prior_service_median`
- `outlet_prior_late_rate`
- `brand_dock_prior_service_median`
- `brand_dock_prior_late_rate`
- `brand_prior_service_median`
- `brand_prior_late_rate`

Fallback hierarchy:
`outlet -> brand+dock -> brand -> global`.

## Local Build Command

```powershell
python scripts/build_task1_features.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --labels data/interim/task1_training_labels.csv --config configs/task1_features.yaml --train-output data/interim/task1_features_train.csv --test-output data/interim/task1_features_test.csv --report-dir reports/private/phase06_task1_features
```

The command is for local human execution only; it writes private outputs and prints only high-level PASS/FAIL status.
