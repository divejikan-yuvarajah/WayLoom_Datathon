# Task 1 Exploratory Data Analysis Methodology

## 1. Scope & Objective

Phase 05 investigates the historical Task 1 training dataset constructed by the canonical Phase 04 label pipeline (`build_task1_training_labels`). The objective is to understand target distributions, assess descriptive group relationships, and evaluate prediction-time candidate features without inducing data leakage or performing premature model selection.

---

## 2. Canonical Target Invariants

All analyses strictly ingest canonical targets from Phase 04:
- `service_minutes = (leave_outlet_dt - service_start_dt) / 60.0`, where `service_start_dt = max(arrival_dt, window_open_dt)`. Waiting before window opening is excluded.
- `late_flag = 1` strictly when `arrival_dt > window_close_dt`. Arrival exactly at close is `0`.

No target clipping, winsorization, or class resampling is performed in this phase.

---

## 3. Strict Leakage Boundary

Historical route execution actuals must never be treated as prediction-time explanatory features:
- `actual_depart_time`
- `actual_travel_duration_min`
- `arrival_time`
- `leave_outlet_time`

Target-derived fields (`service_start_dt`, `service_minutes`, `late_flag`) are analyzed as outputs only.
In the Phase 06 feature candidate table, all actual journey fields are assigned `phase06_recommendation = DISABLE`.

---

## 4. Analytical Methods & Safeguards

### Center, Spread & Tail Metrics
- For continuous targets, sample size `n`, `mean`, `std`, `min`, `p25`, `median`, `p75`, `p90`, `p95`, `p99`, `max`, and `IQR` are reported.
- For lateness, `n`, `late_count`, `not_late_count`, `late_rate`, and 95% Wilson score confidence intervals are calculated.

### Grouped & High-Cardinality Analyses
- Every grouped summary explicitly reports group sample size `n`.
- Outlets with `n < 20` trigger small-sample warnings.
- **No target encodings** are constructed in Phase 05.

### Continuous Predictors
- Continuous relationships (units, weight, volume) are evaluated via Spearman rank correlation and quantile-binned summaries.
- Repeated quantile edges fall back cleanly to adjusted cut bins.

### Planned Slack
- `planned_slack_min = window_close_planned_dt - planned_arrival_dt`.
- Constructed exclusively from planned timetable fields; actual arrival time is never accessed.
- Supports positive, zero, and negative slack values across midnight boundaries.

### Environmental Context
- Road disruption and traffic speed contexts require explicit coverage reporting.
- Missing road conditions are never assumed clear; missing traffic is never assumed free-flow.

---

## 5. Execution Workflow

The analysis CLI is designed for local operator execution:
```powershell
python scripts/run_task1_eda.py `
  --raw-root data/raw `
  --manifest configs/dataset_manifest.yaml `
  --labels data/interim/task1_training_labels.csv `
  --config configs/task1_eda.yaml `
  --output-dir reports/private/phase05_task1_eda
```

Aggregate reports, JSON metrics, and diagnostic charts are saved exclusively to the private directory (`reports/private/phase05_task1_eda/`), which is ignored by Git. No individual delivery identifiers or row records are output.
