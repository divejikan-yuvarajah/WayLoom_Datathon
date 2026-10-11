# PHASE 16 — Task 2A Advanced Forecasting

> **Canonical filename:** `PHASE_16_COMPETITION_CONTRACT.md`  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-234 → DT-241**  
> **Task count:** 8  
> **Default phase priority:** P1  
> **Phase dependency:** Phase 15 must have passed  
> **Phase gate:** **A Task 2A champion is selected only if an advanced or ensemble approach genuinely beats/justifies itself against the frozen Phase 15 reference baselines across the exact Phase 14 rolling-origin backtests. If not, the simpler baseline remains the champion.**

---

# 1. Purpose of Phase 16

Phase 16 is the model-selection phase for Task 2A.

Phases 11–15 already established:

- the official requested-demand history;
- the complete weekly panel;
- descriptive demand behavior;
- leakage-safe forecasting features;
- exact rolling-origin validation;
- simple seasonal/recent reference baselines.

Phase 16 now asks whether locally trained machine-learning forecasts improve enough over those simple baselines to justify their additional complexity.

The phase must answer eight questions:

1. Can one global CatBoost model improve total-volume forecasts across depot/brand/horizon combinations?
2. Can a separate Fresh-only CatBoost model improve chilled-volume forecasts?
3. Does LightGBM provide a credible challenger using the same semantic feature information and backtests?
4. Do the ML candidates actually beat the frozen Phase 15 seasonal/simple references?
5. If they do not, should the simpler baseline remain the official WayLoom approach?
6. Can a fixed, predeclared ensemble improve robustness without post-hoc weight tuning?
7. Which approach should be frozen separately for total volume and Fresh chilled volume?
8. Can all final Task 2A choices be serialized into a deterministic configuration that Phase 17 can execute without reopening model search?

Phase 16 is **not** final Task 2A inference.

This phase must **not**:

- change Phase 11 demand-history semantics;
- change Phase 13 feature semantics;
- change Phase 14 rolling origins or metrics;
- change Phase 15 baseline definitions after seeing ML scores;
- use future actual demand;
- use the official Task 2A test rows to choose a model based on predicted values;
- use pre-trained models;
- use proprietary API-based modelling or preprocessing;
- use low-code/no-code AutoML or fully automated end-to-end modelling;
- perform open-ended hyperparameter search;
- silently remove weak backtests;
- clip negative forecasts during Phase 16 scoring;
- force chilled forecasts below total during Phase 16 scoring;
- start Phase 17 output generation.

---

# 2. Finalized master-inventory contract

The finalized WayLoom master task inventory defines Phase 16 exactly as follows.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-234** | [E] | P1 | DT-228–DT-233 | Train global CatBoost forecast model |
| [ ] | **DT-235** | [E] | P2 | Phase 15 | Train LightGBM challenger |
| [ ] | **DT-236** | [E] | P1 | Phase 15 | Compare ML against seasonal baselines |
| [ ] | **DT-237** | [E] | P1 | Phase 15 | Reject advanced model if it does not beat simpler approach |
| [ ] | **DT-238** | [E] | P1 | Phase 15 | Test forecast ensemble |
| [ ] | **DT-239** | [E] | P1 | DT-236–DT-238 | Select best total-volume forecast approach |
| [ ] | **DT-240** | [E] | P1 | DT-236–DT-238 | Select best chilled-volume forecast approach |
| [ ] | **DT-241** | [E] | P1 | Phase 15 | Freeze Task 2A model/configuration |

**Phase complete:** [ ]  
**READY FOR PHASE 17:** NO

---

# 3. Official Task 2A requirements that constrain Phase 16

The official Challenge Booklet asks WayLoom to forecast ordered demand volume for each supplied depot, brand and future forecast week over **10 future weeks**.

The two required predictions are:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

The organizer explicitly states:

- only volumes must be predicted;
- the team does not need to convert Task 2A forecasts to vehicles or drivers;
- Task 2A history is built from both `deliveries_train.csv` and `task1_test_inputs.csv`;
- every order counts once, including deferred and never-dispatched orders;
- demand is assigned to the week the store requested it;
- official `calendar.csv` `iso_year` and `iso_week` define forecast periods;
- only Fresh has chilled demand;
- Style and Tech chilled forecasts must be exactly zero in the official output;
- the official submission must preserve supplied `row_id` values.

The organizer does **not** prescribe CatBoost, LightGBM, ensemble weights, feature subsets, local backtesting metrics or the model-selection rule. Those are WayLoom engineering decisions and must remain transparent and reproducible.

## 3.1 Competition modelling restrictions

The official rules also constrain Phase 16:

```text
No pre-trained models,
except the organizer-stated exceptions for synthetic data generation/pre-processing.

No proprietary API-based modelling/preprocessing.

No low-code/no-code AI or fully automated end-to-end modelling tools.
```

Therefore Phase 16 uses locally trained, auditable models only.

---

# 4. Source hierarchy

Use this order of authority:

1. official Challenge Booklet and supplied competition artifacts;
2. finalized `WAYLOOM_DATATHON_MASTER_PLAN.md`;
3. approved Phase 11 Task 2A history contract;
4. approved Phase 13 forecasting-feature contract;
5. approved Phase 14 validation contract;
6. approved Phase 15 baseline contract/results schema;
7. this Phase 16 contract;
8. explicitly documented engineering assumptions.

If a lower-level source conflicts with a higher-level source:

```text
STOP
```

Do not silently reinterpret the official rules.

---

# 5. Frozen upstream contracts

Phase 16 assumes Phases 11–15 are complete and passing.

## 5.1 Phase 11 — weekly history

Canonical series grain:

```text
depot
brand
iso_year
iso_week
```

with at least:

```text
week_start_date
total_volume_m3
chilled_volume_m3
```

Required invariants remain:

```text
Fresh: 0 <= chilled <= total
Style: chilled == 0 exactly
Tech: chilled == 0 exactly
```

No unresolved weekly gaps may remain.

## 5.2 Phase 13 — direct multi-horizon features

For forecast origin week `t` and horizon `h`:

```text
h ∈ {1,...,10}
target week = t + h
```

All demand-derived predictors use only demand from week `t` or earlier.

Target-week calendar features may use official calendar information known in advance.

No `t+1 ... t+9` actual demand may enter a horizon-10 predictor.

## 5.3 Phase 14 — validation contract

Phase 16 must use the **exact frozen Phase 14 rolling-origin plan**.

For every backtest origin `t`:

```text
validation = t+1 ... t+10
```

Training rows are eligible only when their target week was already known by `t`.

Phase 14 metrics remain frozen.

### Total-volume primary metric

```text
MAE
```

Secondary:

```text
RMSE
WAPE
mean_bias_m3
P90_absolute_error
```

### Chilled primary evaluation population

```text
Fresh only
```

Primary chilled metric:

```text
MAE
```

Style/Tech chilled remain structural zeros and must not dominate chilled-model selection.

## 5.4 Phase 15 — reference baselines

Phase 16 must load the exact frozen Phase 15 reference baseline identities and results.

Expected reference concept:

```text
one reference total-volume baseline
one reference Fresh-chilled baseline
```

The specific winning baseline name is private run output and must not be hard-coded into source code.

Phase 16 compares advanced candidates against those frozen references.

---

# 6. Data-safety and Codex execution model

The repository may contain competition data that must remain private.

## Agent/Codex may autonomously

- read tracked source code;
- read tracked configs and phase contracts;
- create/refactor Phase 16 code;
- create synthetic fixtures;
- run synthetic/unit/integration tests;
- run dependency checks;
- inspect stack traces;
- fix ordinary implementation bugs;
- rerun tests;
- inspect Git status/diff;
- review tracked model configuration schemas;
- create safe documentation.

## Agent/Codex must not inspect

```text
data/raw/**
data/interim/**
reports/private/**
```

when those paths contain real competition-derived data.

The human operator executes real Phase 16 backtests locally and returns a sanitized PASS/FAIL summary.

## Do not print

- real weekly demand values;
- private fold metrics;
- row-level future forecasts;
- real order/delivery identifiers;
- private candidate ranking tables.

---

# 7. Recommended Codex model for Phase 16

Phase 16 is more reasoning-intensive than Phase 15 because it combines modelling wrappers, backtest orchestration, early stopping, model comparison, ensembles and final selection logic.

Recommended:

```text
GPT-5.6 Sol
Reasoning: High
```

Lower-cost fallback:

```text
GPT-5.6 Terra
Reasoning: High
```

Use the stronger model primarily for DT-236–DT-241 if credits are limited. Straightforward wrapper/tests can be implemented with the cheaper model.

---

# 8. Phase 16 execution strategy

Recommended checkpoint sequence:

```text
Checkpoint A
DT-234
CatBoost total + Fresh chilled
        ↓
Checkpoint B
DT-235
LightGBM challengers
        ↓
Checkpoint C
DT-236
Same-backtest comparison
        ↓
Checkpoint D
DT-237
Advanced-vs-simple rejection gate
        ↓
Checkpoint E
DT-238
Fixed ensemble tests
        ↓
Checkpoint F
DT-239 + DT-240
Select total and chilled champions
        ↓
Checkpoint G
DT-241
Freeze Task 2A final config
        ↓
Full safe regression suite
        ↓
Human runs private Phase 16 experiment
        ↓
Fresh independent Codex review
```

The agent may implement all tooling in one session, but the code must preserve these logical gates.

---

# 9. Repository additions

Create or update:

```text
src/task2a/
├── advanced_models.py
├── model_preprocessing.py
├── ensembles.py
└── model_selection.py

scripts/
├── run_task2a_advanced_models.py
└── freeze_task2a_model_config.py

configs/
├── task2a_advanced_models.yaml
└── task2a_final_models.yaml

docs/
└── task2a_advanced_modeling_spec.md

tests/
├── test_task2a_advanced_models.py
├── test_task2a_model_preprocessing.py
├── test_task2a_ensembles.py
└── test_task2a_model_selection.py
```

Do not duplicate mature Phase 14 metric/split functions or Phase 13 feature builders.

Reuse them.

---

# 10. Private runtime outputs

Real experiment outputs should live only under:

```text
reports/private/phase16_task2a_advanced/
```

Recommended files:

```text
run_manifest.json
candidate_registry.json
fold_predictions.csv
fold_metrics.csv
series_metrics.csv
horizon_metrics.csv
candidate_summary.csv
baseline_comparison.csv
ensemble_summary.csv
selection_decisions.json
warnings.json
phase16_advanced_report.md
```

Optional private candidate model artifacts:

```text
reports/private/phase16_task2a_advanced/models/
```

These are experimentation artifacts, not yet the final production Task 2A models.

Final production training/inference belongs to Phase 17.

---

# 11. `configs/task2a_advanced_models.yaml`

Use a small, predeclared configuration.

The purpose is **not** an open-ended hyperparameter search.

Recommended starting contract:

```yaml
version: 1

validation:
  reuse_phase14_plan: true
  allow_new_splits: false

feature_profile:
  use_phase13_registry: true
  include_prediction_time_safe_only: true
  exclude_metadata_columns: true
  exclude_target_columns: true

catboost:
  enabled: true
  total:
    candidate_id: catboost_total_v1
    loss_function: MAE
    eval_metric: MAE
    iterations: 2000
    learning_rate: 0.03
    depth: 6
    l2_leaf_reg: 5.0
    random_seed: 42
    early_stopping_rounds: 100
    allow_writing_files: false
    verbose: false
  chilled:
    candidate_id: catboost_chilled_v1
    loss_function: MAE
    eval_metric: MAE
    iterations: 2000
    learning_rate: 0.03
    depth: 6
    l2_leaf_reg: 5.0
    random_seed: 42
    early_stopping_rounds: 100
    allow_writing_files: false
    verbose: false

lightgbm:
  enabled: true
  total:
    candidate_id: lightgbm_total_v1
    objective: regression_l1
    metric: l1
    n_estimators: 2000
    learning_rate: 0.03
    num_leaves: 31
    min_child_samples: 20
    reg_lambda: 1.0
    random_state: 42
    n_jobs: 1
    early_stopping_rounds: 100
  chilled:
    candidate_id: lightgbm_chilled_v1
    objective: regression_l1
    metric: l1
    n_estimators: 2000
    learning_rate: 0.03
    num_leaves: 31
    min_child_samples: 20
    reg_lambda: 1.0
    random_state: 42
    n_jobs: 1
    early_stopping_rounds: 100

ensembles:
  catboost_lightgbm_equal_weight:
    enabled: true
    weight_catboost: 0.5
    weight_lightgbm: 0.5

  advanced_reference_equal_weight:
    enabled: true
    weight_advanced: 0.5
    weight_reference_baseline: 0.5

selection:
  primary_metric: mae
  lower_is_better: true
  relative_tie_tolerance_pct: 0.5
  prefer_simpler_within_tolerance: true
  tie_breakers:
    - rmse
    - p90_absolute_error
    - backtest_mae_std
    - simplicity

final_iteration_policy:
  method: median_best_iteration
  minimum_iteration: 1

prediction_policy:
  evaluate_raw_predictions: true
  clip_negative_in_phase16: false
  enforce_chilled_le_total_in_phase16: false

artifacts:
  private_output_dir: reports/private/phase16_task2a_advanced
```

These exact numeric values are WayLoom engineering defaults, not organizer rules.

If the repository already contains an explicitly approved different value from an earlier phase, preserve the approved value rather than silently replacing it.

---

# 12. Common model feature contract

Every advanced candidate must use the same **semantic prediction-time-safe feature profile**.

Use the canonical Phase 13 feature registry/allow-list.

Typical eligible groups include:

```text
PAST_DEMAND
TARGET_WEEK_CALENDAR
STATIC_SERIES
FORECAST_HORIZON
```

Examples:

```text
total_lag_1
total_lag_2
total_lag_4
total_lag_13
total_lag_52

total_roll_mean_4
total_roll_mean_8
total_roll_mean_13

total_trend_short_long

chilled lag/rolling/trend features where applicable

target_operating_days
target_payday_days
target_has_payday
target_holiday_days
target_has_holiday
target_festival_days
target_has_festival
target_max_festival_ramp
target_mean_festival_ramp
target_monsoon_days
target_monsoon_day_fraction

depot
brand
forecast_horizon
```

Do not enable a feature only for CatBoost because it scores better unless the same semantic source information is also available to LightGBM.

Representation may differ by model family, but semantic information should remain comparable.

## Forbidden

Never put these in `X`:

```text
target_total_volume_m3
target_chilled_volume_m3
```

Never use any actual future demand beyond the forecast origin as a predictor.

Never use official Task 2A test output values because they do not exist.

---

# 13. Model preprocessing

## 13.1 CatBoost

Preferred CatBoost representation:

- numerical columns as numeric values;
- missing numerical values left as CatBoost-supported missing values;
- `depot` and `brand` treated as categorical;
- any categorical missing value converted to a fixed token such as `__MISSING__`;
- no target encoding outside CatBoost's internal train-only behavior;
- categorical feature indexes/names frozen from the training schema.

Do not compute any category target statistic on the full fold including validation.

## 13.2 LightGBM

Use a deterministic, fold-fitted preprocessing adapter.

Recommended:

Numerical:

```text
SimpleImputer(strategy="median")
```

Categorical:

```text
SimpleImputer(strategy="constant", fill_value="__MISSING__")
OneHotEncoder(handle_unknown="ignore")
```

Fit all preprocessing on the fold training set only.

Do not fit:

- median values;
- category vocabulary;
- any learned encoder;

on validation rows.

LightGBM must see the same semantic feature set as CatBoost, although one-hot representation may expand columns.

---

# 14. Common backtest protocol

For every candidate and every target:

1. load the exact Phase 14 backtest plan;
2. verify its signature/hash;
3. obtain the Phase 14 training rows;
4. obtain the exact 10-week validation rows;
5. fit preprocessing on training only;
6. fit model on training only;
7. use Phase 14 validation rows only as evaluation/early-stopping set;
8. generate raw validation predictions;
9. evaluate using the exact Phase 14 metric functions;
10. store backtest/series/horizon diagnostics privately.

Candidates must not create their own backtests.

## 14.1 Training-target availability

The Phase 14 rule remains binding:

```text
training_row.target_week_start_date <= validation_origin
```

An earlier forecast origin does not automatically make a row train-eligible if its label occurs after the current validation origin.

## 14.2 Validation outcomes never update later horizons

For a backtest origin `t`, the model predicts all horizons `1..10` from the information available at `t`.

Do not reveal actual `t+1` demand before predicting `t+2`.

Do not retrain within the ten-week validation window.

---

# 15. DT-234 — Train global CatBoost forecast model

**Mark:** [E]  
**Priority:** P1  
**Dependency:** DT-228–DT-233

## 15.1 Objective

Train locally from scratch:

```text
CatBoost total-volume global model
CatBoost Fresh-chilled global model
```

The model is "global" because one model is trained across the relevant depot/brand/horizon training rows rather than training one independent model per series/horizon.

## 15.2 Total model population

Use all eligible Task 2A direct multi-horizon training rows from the Phase 14 fold-train partition.

Target:

```text
target_total_volume_m3
```

Use all official depot/brand series.

## 15.3 Chilled model population

Use only:

```text
brand == Fresh
```

Target:

```text
target_chilled_volume_m3
```

Do not train the chilled model on Style/Tech structural zeros simply to improve apparent accuracy.

## 15.4 Loss/evaluation

Recommended CatBoost objective:

```text
MAE
```

Recommended eval metric:

```text
MAE
```

Phase 14 metric functions remain authoritative for final candidate comparison.

## 15.5 Early stopping

Each fold may use its validation set as CatBoost `eval_set` for early stopping.

The validation set may determine:

```text
best_iteration
```

for that backtest candidate.

It may not alter:

- Phase 14 split;
- feature semantics;
- baseline definition;
- model family after seeing private scores.

Record per fold:

```text
best_iteration
best_validation_metric
stopped_early
configured_max_iterations
```

## 15.6 Final iteration policy for Phase 17

After all valid development/backtest folds, derive a deterministic final iteration count:

```text
median(best_iteration values)
```

Round deterministically to integer.

Do not derive the final iteration count from official Task 2A test predictions.

## 15.7 Required diagnostics

For each backtest:

```text
MAE
RMSE
WAPE
bias
P90 AE
negative_prediction_count
```

For Fresh chilled additionally:

```text
chilled_gt_total_count
```

The last diagnostic compares corresponding raw chilled/total predictions if available.

Do not correct it during Phase 16.

## 15.8 Required tests

Synthetic tests must prove:

- CatBoost wrapper fits total target;
- CatBoost wrapper fits Fresh chilled target;
- Style/Tech do not enter chilled training population;
- target columns are absent from `X`;
- Phase 14 split indexes are respected;
- validation y is not used to construct validation X;
- early stopping metadata is captured;
- predictions are finite;
- deterministic seed/config is used;
- raw negative predictions are not silently clipped;
- best-iteration aggregation is deterministic.

## 15.9 STOP conditions

Stop if:

- CatBoost training requires prohibited API access;
- feature leakage is detected;
- Phase 14 splits are changed;
- target column enters `X`;
- Fresh chilled model includes Style/Tech solely as zero-label training rows;
- failed folds are silently omitted.

## 15.10 Definition of Done

- [ ] total CatBoost candidate implemented;
- [ ] Fresh chilled CatBoost candidate implemented;
- [ ] all required backtests supported;
- [ ] early stopping implemented;
- [ ] best iterations recorded;
- [ ] raw predictions retained;
- [ ] tests pass.

---

# 16. DT-235 — Train LightGBM challenger

**Mark:** [E]  
**Priority:** P2

## 16.1 Objective

Train locally from scratch:

```text
LightGBM total-volume challenger
LightGBM Fresh-chilled challenger
```

Use the exact same Phase 14 backtests and the same semantic feature profile as CatBoost.

## 16.2 Objective

Recommended LightGBM objective:

```text
regression_l1
```

Recommended evaluation metric:

```text
l1
```

Final comparison still uses Phase 14 metric functions.

## 16.3 Preprocessing

Fit preprocessing separately inside each fold using fold-train rows only.

Unseen validation categories must not crash prediction.

## 16.4 Early stopping

Use validation fold only for early-stopping evaluation.

Do not use any future official Task 2A test data for early stopping.

Capture:

```text
best_iteration
stopped_early
```

## 16.5 Determinism

Recommended:

```text
random_state = 42
n_jobs = 1
```

If the installed LightGBM version supports deterministic flags, set them explicitly and document them.

## 16.6 Tests

Synthetic tests:

- total LightGBM fit/predict;
- Fresh chilled fit/predict;
- categorical preprocessing train-only;
- unseen validation category;
- missing numerical feature;
- exact semantic feature profile;
- Phase 14 split reuse;
- early stopping metadata;
- finite predictions;
- deterministic behavior within tolerance;
- no clipping/capping.

## 16.7 Environment handling

`DT-235` is part of the finalized inventory and should not be silently skipped.

If LightGBM is missing:

1. add the approved dependency/version to project requirements;
2. install it locally if permitted by the development environment;
3. run a minimal synthetic smoke test;
4. continue.

If the environment genuinely cannot support it:

```text
DT-235 = BLOCKED
PHASE 16 = NOT COMPLETE
```

Do not pretend it passed.

---

# 17. DT-236 — Compare ML against seasonal baselines

**Mark:** [E]  
**Priority:** P1

## 17.1 Objective

Compare advanced candidates fairly against the frozen Phase 15 references.

Total candidate comparison must include at least:

```text
Phase 15 reference total baseline
CatBoost total
LightGBM total
```

Fresh chilled comparison must include at least:

```text
Phase 15 reference chilled baseline
CatBoost Fresh chilled
LightGBM Fresh chilled
```

Ensembles are added after DT-238.

## 17.2 Same-backtest requirement

Every compared candidate must use the identical:

```text
backtest_id
forecast_origin
series set
forecast horizons 1..10
validation target rows
metric implementation
```

Verify a frozen Phase 14 backtest signature/hash before comparison.

## 17.3 Candidate eligibility

A candidate is eligible only if:

- all required backtests completed;
- every required validation row has one prediction;
- no prediction is NaN/Inf;
- no leakage test failed;
- no forbidden feature was used;
- metric calculation completed on the frozen evaluation population.

Do not silently rank a candidate that completed only easier backtests.

## 17.4 Comparison metrics

Primary:

```text
overall pooled MAE
```

Secondary:

```text
overall RMSE
P90 absolute error
backtest MAE standard deviation
worst backtest MAE
WAPE where defined
bias
```

Diagnostics:

```text
per-series MAE
per-horizon MAE
negative_prediction_count
Fresh chilled_gt_total_count
```

## 17.5 Report

Generate a private comparison table with at least:

```text
target_name
candidate_id
approach_family
eligible
backtest_count
prediction_row_count
overall_mae
overall_rmse
overall_wape
overall_bias_m3
p90_absolute_error
mean_backtest_mae
std_backtest_mae
worst_backtest_mae
negative_prediction_count
chilled_gt_total_count
```

---

# 18. DT-237 — Reject advanced model if it does not beat simpler approach

**Mark:** [E]  
**Priority:** P1

This is a critical complexity-control gate.

Advanced modelling is not automatically preferred.

## 18.1 Frozen rejection rule

Use a predeclared relative tie tolerance.

Recommended engineering default:

```text
relative_tie_tolerance_pct = 0.5
```

For a baseline with MAE `B` and advanced candidate MAE `A`:

```text
relative_improvement_pct = 100 * (B - A) / B
```

when `B > 0`.

### Rule

If:

```text
relative_improvement_pct > 0.5
```

then the advanced candidate has a material primary-metric improvement and may remain eligible.

If:

```text
relative_improvement_pct <= 0.5
```

prefer the simpler reference baseline unless a separately predeclared secondary criterion provides a compelling reason.

For `B == 0`:

- baseline is already perfect on MAE;
- an advanced model cannot beat it;
- keep the baseline.

The 0.5% threshold is a WayLoom engineering choice, not an organizer rule.

## 18.2 Do not change the tolerance after seeing scores

Do not change:

```text
0.5%
```

to make a preferred model win.

If the value is changed before the real run for a documented engineering reason, commit/configure the change first.

## 18.3 Secondary tie-breaks

When candidates are within the tie tolerance, prefer the approach with:

1. lower RMSE;
2. lower P90 absolute error;
3. lower backtest MAE standard deviation;
4. lower complexity.

But the baseline gets explicit simplicity preference when performance is effectively tied.

## 18.4 Complexity order

Recommended from simplest to more complex:

```text
Phase 15 reference baseline
fixed simple ensemble with baseline
single LightGBM/CatBoost model
advanced-model ensemble
```

The exact order may be encoded in config.

## 18.5 Tests

Test:

- advanced materially better → eligible;
- advanced worse → rejected;
- advanced within tolerance → baseline preferred;
- baseline MAE zero → baseline wins;
- exact tolerance boundary deterministic;
- no private-score-driven threshold mutation path.

---

# 19. DT-238 — Test forecast ensemble

**Mark:** [E]  
**Priority:** P1

## 19.1 Objective

Test simple, predeclared blends without learning weights from the same validation scores.

Do not implement a stacking model in Phase 16.

Do not optimize ensemble weights.

## 19.2 Ensemble A — CatBoost + LightGBM

If both component candidates are eligible and cover exactly the same rows:

```text
pred_ensemble =
0.5 * pred_catboost
+
0.5 * pred_lightgbm
```

Build separately for:

```text
total volume
Fresh chilled volume
```

## 19.3 Ensemble B — best advanced + reference baseline

If at least one advanced candidate is eligible:

```text
pred_ensemble =
0.5 * pred_best_advanced
+
0.5 * pred_reference_baseline
```

Again evaluate separately for total and Fresh chilled.

This is useful when the simple baseline captures seasonal structure that complements a nonlinear ML model.

## 19.4 Alignment requirement

Before averaging assert exact equality of:

```text
backtest_id
depot
brand
origin_week_start_date
target_week_start_date
forecast_horizon
```

Do not align by row position without key validation.

## 19.5 Missing component

If any required component prediction is missing:

```text
ensemble candidate = INELIGIBLE
```

Do not silently fall back to one component under the ensemble name.

## 19.6 Raw prediction policy

Do not clip component predictions before blending.

Do not clip ensemble output in Phase 16.

Do not enforce chilled <= total in Phase 16.

## 19.7 Tests

- exact 50/50 arithmetic;
- keyed alignment;
- reordered input rows still align correctly;
- missing component makes ensemble ineligible;
- duplicate keys rejected;
- no learned-weight code path;
- total and chilled handled separately;
- deterministic output.

---

# 20. DT-239 — Select best total-volume forecast approach

**Mark:** [E]  
**Priority:** P1

## 20.1 Eligible candidate set

May include:

```text
Phase 15 reference total baseline
CatBoost total
LightGBM total
CatBoost+LightGBM total ensemble
best-advanced+baseline total ensemble
```

Only candidates passing all leakage/completeness gates are eligible.

## 20.2 Selection hierarchy

1. apply DT-237 advanced-vs-simple rejection rule;
2. rank eligible materially distinct candidates by overall pooled MAE;
3. use RMSE as first tie-break;
4. use P90 absolute error as second tie-break;
5. use backtest MAE stability as third tie-break;
6. prefer simpler approach within configured tie tolerance.

## 20.3 Diagnostic review

Before freezing, privately review:

```text
per-series performance
per-horizon performance
worst backtest
bias
negative prediction rate/count
```

Diagnostics may identify a blocker but must not be used to cherry-pick a different validation subset.

## 20.4 Champion object

Freeze one total champion description:

```text
target: total_volume_m3
approach_type: baseline | model | ensemble
candidate_id
components if ensemble
feature_profile_id if model-based
model parameters if model-based
final iteration policy if model-based
```

Exactly one total champion must exist.

---

# 21. DT-240 — Select best chilled-volume forecast approach

**Mark:** [E]  
**Priority:** P1

## 21.1 Selection population

Primary chilled model selection uses:

```text
Fresh only
```

Style and Tech are not modelled chilled targets.

Their final Phase 17 outputs remain:

```text
0.0
```

## 21.2 Eligible candidates

May include:

```text
Phase 15 reference Fresh chilled baseline
CatBoost Fresh chilled
LightGBM Fresh chilled
CatBoost+LightGBM chilled ensemble
best-advanced+baseline chilled ensemble
```

## 21.3 Selection hierarchy

Use the same frozen hierarchy as total:

1. advanced-vs-simple rejection rule;
2. Fresh pooled MAE;
3. RMSE;
4. P90 AE;
5. backtest MAE stability;
6. simplicity within tolerance.

## 21.4 Chilled/total diagnostic

Report:

```text
raw Fresh chilled prediction > corresponding raw total prediction
```

count privately.

Do not correct those predictions in Phase 16.

Phase 17 owns:

```text
negative clipping
chilled <= total enforcement
```

## 21.5 Exactly one chilled champion

Freeze one Fresh chilled champion configuration.

Style/Tech zero rule is frozen separately as an output rule, not a model.

---

# 22. DT-241 — Freeze Task 2A model/configuration

**Mark:** [E]  
**Priority:** P1

This is the handoff contract to Phase 17.

Create:

```text
configs/task2a_final_models.yaml
```

Only after DT-239 and DT-240 are complete.

## 22.1 Required schema

Recommended:

```yaml
version: 1
state: FROZEN

source_contracts:
  history: phase11
  features: phase13
  validation: phase14
  baselines: phase15
  selection: phase16

feature_profile:
  registry_path: configs/task2a_features.yaml
  profile_id: task2a_advanced_safe_v1
  registry_hash: null

validation:
  config_path: configs/task2a_validation.yaml
  backtest_signature: null

selection_policy:
  primary_metric: mae
  relative_tie_tolerance_pct: 0.5
  prefer_simpler_within_tolerance: true

total:
  approach_type: null
  candidate_id: null
  family: null
  parameters: {}
  component_candidates: []
  final_iteration_policy:
    method: null
    value: null

chilled_fresh:
  approach_type: null
  candidate_id: null
  family: null
  parameters: {}
  component_candidates: []
  final_iteration_policy:
    method: null
    value: null

structural_output_rules:
  style_chilled_zero: true
  tech_chilled_zero: true

phase17_postprocessing:
  clip_negative: true
  enforce_chilled_le_total: true
  rounding: none

seeds:
  default: 42

selection_complete: true
```

Do not place private backtest metric values in the tracked config.

## 22.2 Approach-specific requirements

### If champion is a baseline

Store:

```text
baseline name
baseline parameters/window/weights
fallback policy
```

Do not create a fake ML model family.

### If champion is CatBoost/LightGBM

Store:

```text
model family
exact parameters
semantic feature profile
categorical/preprocessing policy
seed
final iteration count/policy
```

### If champion is an ensemble

Store:

```text
component IDs
component weights
component model/baseline configs
```

Weights must match the frozen predeclared ensemble.

## 22.3 Freeze guard

After the config is frozen:

Phase 17 must not:

- compare new model families;
- change ensemble weights;
- tune hyperparameters;
- change features because predictions look strange;
- change Phase 14 metrics;
- reopen Phase 15/16 selection.

## 22.4 Config validation

Implement a validator that rejects:

- state not `FROZEN`;
- more than one total champion;
- more than one Fresh chilled champion;
- missing component weight for ensemble;
- ensemble weights not summing to 1;
- missing model parameters;
- missing final iteration value for model-based champion;
- disabled Style/Tech zero rule;
- unexpected output postprocessing policy;
- missing source contract references.

## 22.5 Tests

- valid baseline total/chilled config;
- valid model config;
- valid ensemble config;
- unfrozen config rejected by Phase 17 validator;
- missing champion rejected;
- multiple champions rejected;
- bad ensemble weights rejected;
- missing iteration policy rejected for model;
- structural zero rules required;
- no private metrics written to tracked config.

---

# 23. Model candidate identifiers

Use stable IDs.

Recommended:

```text
catboost_total_v1
catboost_chilled_v1
lightgbm_total_v1
lightgbm_chilled_v1
ensemble_cb_lgb_total_equal_v1
ensemble_cb_lgb_chilled_equal_v1
ensemble_advanced_baseline_total_equal_v1
ensemble_advanced_baseline_chilled_equal_v1
```

Phase 15 baseline IDs must be reused exactly rather than renamed.

---

# 24. Candidate result schema

Recommended private candidate summary:

```text
target_name
candidate_id
approach_type
family
eligible
ineligibility_reason
backtest_count
prediction_row_count
overall_mae
overall_rmse
overall_wape
overall_bias_m3
p90_absolute_error
mean_backtest_mae
std_backtest_mae
worst_backtest_mae
negative_prediction_count
chilled_gt_total_count
relative_improvement_vs_reference_pct
selection_status
```

Allowed `selection_status` values:

```text
REFERENCE
ELIGIBLE
REJECTED_NO_IMPROVEMENT
REJECTED_INCOMPLETE
REJECTED_LEAKAGE
SELECTED
NOT_APPLICABLE
```

---

# 25. Early-stopping and final-iteration details

Early stopping may produce different best iterations across backtests.

Store per-fold values.

For Phase 17 final training, recommended deterministic policy:

```text
final_iteration = median(valid_fold_best_iterations)
```

Then apply bounds:

```text
>= 1
<= configured maximum
```

Do not use the maximum simply because it might improve the final in-sample fit.

Do not choose the iteration count by testing the official Task 2A submission predictions.

If the selected final approach is a baseline, this section is `NOT_APPLICABLE`.

---

# 26. Raw-prediction policy in Phase 16

Phase 16 evaluates candidates before final output postprocessing.

Do not apply:

```text
max(pred, 0)
min(chilled, total)
rounding
manual upper caps
```

when calculating Phase 16 candidate metrics.

Instead record diagnostics:

```text
negative_prediction_count
chilled_gt_total_count
```

The finalized master inventory explicitly assigns final constraints to Phase 17:

```text
DT-248 Clip negative forecasts
DT-249 Enforce chilled ≤ total
```

Do not move those tasks earlier.

---

# 27. Edge cases

## 27.1 Missing long lags

Early historical origins may contain missing `lag_52` or other long-history features.

Do not backfill from future observations.

Model preprocessing must handle missing values without leakage.

## 27.2 All-zero target in a fold

A Fresh chilled training window could theoretically be all zero.

The regressor should still produce a deterministic valid prediction or a clear unsupported status.

Do not redraw the backtest.

## 27.3 Unseen category in validation

LightGBM preprocessing must tolerate unseen categories using the frozen unknown-category policy.

CatBoost category representation must remain valid.

## 27.4 Zero-volume validation population

Phase 14 WAPE may be unavailable if the sum of actual values is zero.

Do not invent an epsilon denominator.

MAE remains valid.

## 27.5 Negative advanced predictions

Record them.

Do not clip in Phase 16.

## 27.6 Fresh chilled exceeds total prediction

Record it.

Do not cap in Phase 16.

## 27.7 Candidate fails one backtest

Candidate becomes ineligible unless the failure is a deterministic technical issue that is fixed and all backtests are rerun.

Do not rank using only successful folds.

## 27.8 Ensemble component ordering

Never average row-position arrays without verifying key alignment.

## 27.9 Baseline wins

This is a valid successful Phase 16 outcome.

Do not force an ML champion just because Phase 16 is named "advanced forecasting".

## 27.10 LightGBM beats CatBoost

Also valid.

Do not assume CatBoost must win.

---

# 28. Required synthetic tests

Create comprehensive synthetic tests.

## DT-234 CatBoost

- total model fit/predict;
- Fresh chilled fit/predict;
- Style/Tech excluded from chilled training;
- safe feature profile only;
- target columns absent;
- exact Phase 14 fold indexes;
- early-stopping metadata;
- best-iteration collection;
- finite predictions;
- no clipping;
- deterministic seed.

## DT-235 LightGBM

- total fit/predict;
- Fresh chilled fit/predict;
- preprocessing fit on train only;
- unseen category;
- missing numerical values;
- exact semantic feature profile;
- exact Phase 14 fold indexes;
- early-stopping metadata;
- deterministic output within tolerance.

## DT-236 comparison

- same backtest signature required;
- missing backtest makes candidate ineligible;
- missing prediction row makes candidate ineligible;
- NaN/Inf prediction rejected;
- Phase 14 metric functions reused;
- relative improvement calculated correctly;
- per-series/per-horizon diagnostics generated.

## DT-237 rejection gate

- material improvement accepted;
- worse advanced model rejected;
- within tolerance simpler model preferred;
- exact tolerance boundary deterministic;
- reference MAE zero handling;
- threshold not derived from private scores.

## DT-238 ensemble

- exact 50/50 advanced ensemble;
- exact 50/50 advanced+baseline ensemble;
- keyed alignment;
- reordered rows align correctly;
- duplicate keys rejected;
- missing component makes ensemble ineligible;
- no learned weights;
- raw predictions preserved.

## DT-239 total selection

- baseline can win;
- CatBoost can win;
- LightGBM can win;
- ensemble can win;
- MAE primary;
- RMSE tie-break;
- P90 tie-break;
- stability tie-break;
- simplicity tie-break;
- exactly one total champion.

## DT-240 chilled selection

- Fresh-only selection population;
- Style/Tech zero rows excluded from primary chilled ranking;
- baseline can win;
- ML can win;
- ensemble can win;
- chilled>total diagnostic does not mutate prediction;
- exactly one Fresh chilled champion.

## DT-241 final config

- baseline champion config valid;
- model champion config valid;
- ensemble champion config valid;
- unfrozen config rejected;
- missing total champion rejected;
- missing chilled champion rejected;
- invalid ensemble weights rejected;
- Style zero rule required;
- Tech zero rule required;
- Phase 17 postprocessing contract frozen;
- no private metrics embedded.

## Leakage and temporal integrity

- future-demand mutation invariant;
- horizon-10 intermediate-demand mutation invariant;
- training target date <= validation origin;
- validation target cannot affect validation predictors;
- no retraining within validation horizon;
- exact Phase 14 backtest signature.

## Privacy

- no private data printed;
- private result paths ignored;
- Task 1 artifacts unchanged.

---

# 29. Stop conditions

`READY FOR PHASE 17` must remain **NO** if any of the following occurs:

- Phase 15 reference baselines are not frozen;
- Phase 14 validation plan is bypassed;
- candidate models create new backtests;
- candidates use different validation populations;
- future actual demand enters a predictor;
- an ineligible training label occurs after the validation origin;
- validation results are used to update later validation-horizon predictors;
- target columns enter model features;
- CatBoost or LightGBM uses a prohibited pre-trained model/API service;
- open-ended AutoML/tuning is introduced;
- LightGBM challenger is silently skipped;
- failed folds are silently removed;
- advanced model is selected even though the frozen rejection rule says baseline should remain;
- ensemble weights are optimized after seeing backtest scores;
- ensemble keys do not align exactly;
- Style/Tech structural-zero semantics are lost;
- raw Phase 16 metrics are computed after clipping/capping;
- more than one total champion remains;
- more than one Fresh chilled champion remains;
- final config is not frozen;
- final config lacks Phase 17 execution information;
- Task 1 frozen artifacts are changed;
- private competition data must be exposed to complete the implementation;
- synthetic/safe tests fail.

---

# 30. Definition of Done

Phase 16 passes only when:

- [ ] DT-234 PASS
- [ ] DT-235 PASS
- [ ] DT-236 PASS
- [ ] DT-237 PASS
- [ ] DT-238 PASS
- [ ] DT-239 PASS
- [ ] DT-240 PASS
- [ ] DT-241 PASS
- [ ] CatBoost total candidate complete
- [ ] CatBoost Fresh chilled candidate complete
- [ ] LightGBM total challenger complete
- [ ] LightGBM Fresh chilled challenger complete
- [ ] exact Phase 14 backtests reused
- [ ] Phase 14 backtest signature matches
- [ ] Phase 15 reference baselines reused
- [ ] future-demand leakage tests pass
- [ ] training-target availability tests pass
- [ ] all candidates use the same semantic feature profile
- [ ] early stopping is fold-safe
- [ ] raw predictions are evaluated
- [ ] advanced-vs-simple rejection rule applied
- [ ] fixed ensemble candidates tested
- [ ] no ensemble weight search
- [ ] exactly one total champion selected
- [ ] exactly one Fresh chilled champion selected
- [ ] baseline is allowed to remain champion
- [ ] Style chilled zero rule preserved
- [ ] Tech chilled zero rule preserved
- [ ] `configs/task2a_final_models.yaml` frozen and valid
- [ ] no private metrics written into tracked config
- [ ] all Phase 16 synthetic tests pass
- [ ] full safe repository suite passes
- [ ] `python -m pip check` passes
- [ ] private outputs remain ignored
- [ ] Task 1 frozen artifacts unchanged
- [ ] independent Phase 16 review passes
- [ ] no unresolved STOP condition remains

Then:

```text
PHASE 16 STATUS: PASS
READY FOR PHASE 17: YES
```

---

# 31. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-16-task2a-advanced
```

Recommended commit sequence:

```text
feat(task2a): add CatBoost advanced forecasting wrapper
feat(task2a): add LightGBM forecast challenger
feat(task2a): add advanced baseline comparison gate
feat(task2a): add fixed forecast ensembles
feat(task2a): add Task 2A champion selection
feat(task2a): add final Task 2A config freeze
 test(task2a): add Phase 16 synthetic model-selection tests
 docs(task2a): document advanced forecasting methodology
```

Before each commit:

```bash
git status
git diff --cached --name-only
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

Before merge:

```bash
pytest -q
python -m pip check
git status
```

Also verify Task 1 artifacts are unchanged:

```text
configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv
```

---

# 32. Local real-data experiment command

Codex should implement but **not execute** this against restricted private competition data.

Recommended:

```bash
python scripts/run_task2a_advanced_models.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --multihorizon-table data/interim/task2a_multihorizon_train.csv \
  --feature-config configs/task2a_features.yaml \
  --validation-config configs/task2a_validation.yaml \
  --baseline-results reports/private/phase15_task2a_baselines \
  --model-config configs/task2a_advanced_models.yaml \
  --output-dir reports/private/phase16_task2a_advanced
```

One-line PowerShell equivalent:

```powershell
python scripts/run_task2a_advanced_models.py --weekly-panel data/interim/task2a_weekly_panel.csv --multihorizon-table data/interim/task2a_multihorizon_train.csv --feature-config configs/task2a_features.yaml --validation-config configs/task2a_validation.yaml --baseline-results reports/private/phase15_task2a_baselines --model-config configs/task2a_advanced_models.yaml --output-dir reports/private/phase16_task2a_advanced
```

After selection, freeze the tracked config with a dedicated script that reads only the private selection decision locally and writes non-private configuration metadata:

```bash
python scripts/freeze_task2a_model_config.py \
  --advanced-config configs/task2a_advanced_models.yaml \
  --validation-config configs/task2a_validation.yaml \
  --feature-config configs/task2a_features.yaml \
  --selection reports/private/phase16_task2a_advanced/selection_decisions.json \
  --output configs/task2a_final_models.yaml
```

The freeze script must not copy private metric values into the tracked YAML.

---

# 33. Sanitized local completion summary

After the human real-data run, return only a summary such as:

```text
LOCAL PHASE 16 ADVANCED MODELLING: PASS
PHASE 14 BACKTEST SIGNATURE MATCH: YES
PHASE 15 REFERENCES LOADED: YES
CATBOOST TOTAL: COMPLETE
CATBOOST FRESH CHILLED: COMPLETE
LIGHTGBM TOTAL: COMPLETE
LIGHTGBM FRESH CHILLED: COMPLETE
FUTURE-DEMAND LEAKAGE AUDIT: PASS
ALL REQUIRED BACKTESTS COMPLETE: YES
ENSEMBLES TESTED: YES
TOTAL CHAMPION FROZEN: YES
FRESH CHILLED CHAMPION FROZEN: YES
TASK2A FINAL CONFIG VALID: YES
TASK 1 ARTIFACTS CHANGED: NO
```

Do not paste private score tables into the agent chat.

---

# 34. Enhanced Codex/Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 16 only.

PHASE:
Task 2A Advanced Forecasting

TASK RANGE:
DT-234 through DT-241

EXECUTION MODE:
High-risk controlled autonomous implementation with full SAFE engineering autonomy.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

LOWER-COST FALLBACK:
GPT-5.6 Terra — High reasoning

You MAY:

- create/edit/refactor Phase 16 tracked code
- create/edit configuration
- create/edit documentation
- create synthetic fixtures
- add approved local Python ML dependencies
- run targeted pytest tests
- run the complete safe regression suite
- inspect tracebacks
- diagnose normal implementation failures
- fix ordinary implementation bugs automatically
- rerun failed tests
- run python -m pip check
- inspect git status/diff
- verify ignore rules
- self-review against the Phase 16 Definition of Done

Do NOT stop for routine coding/test failures that can safely be fixed.

STOP only for:

- official competition-rule ambiguity
- requirement to inspect restricted competition row-level data
- conflict with approved Phase 11–15 contracts
- Phase 14 split/signature mismatch
- future-demand leakage that cannot be fixed safely
- inability to implement the required LightGBM challenger
- genuine schema/environment blocker
- a design change that would reopen frozen earlier phases

DO NOT START PHASE 17.

==================================================
READ FIRST
==================================================

Read with targeted context:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase 16 and Task 2A global rules
4. PHASE_11_COMPETITION_CONTRACT.md
   - canonical demand history
5. PHASE_13_COMPETITION_CONTRACT.md
   - features/direct multi-horizon semantics
6. PHASE_14_COMPETITION_CONTRACT.md
   - exact backtests + metrics
7. PHASE_15_COMPETITION_CONTRACT.md
   - frozen baseline definitions/references
8. PHASE_16_COMPETITION_CONTRACT.md
9. src/task2a/history.py
10. src/task2a/features.py
11. src/task2a/multihorizon.py
12. src/task2a/validation.py
13. src/task2a/metrics.py
14. src/task2a/baselines.py
15. configs/task2a_features.yaml
16. configs/task2a_validation.yaml
17. configs/task2a_baselines.yaml
18. existing Task 2A tests

Use targeted reading.

Do not reread unrelated old contracts unless required by a direct dependency.

TASK 1 IS FROZEN.

Do not modify:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

==================================================
OFFICIAL RESTRICTIONS
==================================================

Do NOT use:

- pre-trained models
- proprietary API-based modelling/preprocessing
- low-code/no-code AI modelling systems
- fully automated end-to-end AutoML
- external upload of competition data

CatBoost and LightGBM must be trained locally from scratch.

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do NOT inspect or print real competition rows from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for agent-run development/testing.

The human runs the real Phase 16 experiment locally.

==================================================
IMMUTABLE UPSTREAM CONTRACTS
==================================================

Reuse Phase 11 history exactly.

Reuse Phase 13 feature semantics exactly.

Reuse Phase 14 rolling-origin plan EXACTLY.

Reuse Phase 14 metric functions EXACTLY.

Reuse Phase 15 reference baselines EXACTLY.

Do NOT create:

- new random splits
- new rolling origins
- different validation windows per model
- new baseline definitions after seeing scores

Every candidate must use the exact Phase 14 backtest signature.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2a/advanced_models.py
src/task2a/model_preprocessing.py
src/task2a/ensembles.py
src/task2a/model_selection.py

scripts/run_task2a_advanced_models.py
scripts/freeze_task2a_model_config.py

configs/task2a_advanced_models.yaml
configs/task2a_final_models.yaml

docs/task2a_advanced_modeling_spec.md

tests/test_task2a_advanced_models.py
tests/test_task2a_model_preprocessing.py
tests/test_task2a_ensembles.py
tests/test_task2a_model_selection.py

Private experiment outputs:

reports/private/phase16_task2a_advanced/**

must remain ignored.

==================================================
COMMON FEATURE CONTRACT
==================================================

Use the Phase 13 prediction-time-safe feature registry/allow-list.

Use the same semantic feature profile for CatBoost and LightGBM.

Representation may differ by model family.

Do NOT include:

target_total_volume_m3
target_chilled_volume_m3

Do NOT use actual future demand after the forecast origin.

For every validation origin t:

all demand-derived predictor source weeks <= t

and every train row must satisfy:

training target week <= t

Validation outcomes from h=1 must not update h=2..10 predictions.

==================================================
DT-234 — GLOBAL CATBOOST
==================================================

Implement two locally trained CatBoost regressors:

1. total-volume global model
2. Fresh-only chilled-volume global model

Total target:

target_total_volume_m3

Chilled target:

target_chilled_volume_m3

Chilled training population:

brand == Fresh only

Do NOT train Style/Tech chilled zeros into the chilled model simply to
improve apparent score.

Recommended fixed CatBoost config:

loss_function = MAE
eval_metric = MAE
iterations = 2000
learning_rate = 0.03
depth = 6
l2_leaf_reg = 5
random_seed = 42
early_stopping_rounds = 100
allow_writing_files = false
verbose = false

Use CatBoost native categorical handling for approved categorical
features such as depot/brand.

Each backtest:

fit on Phase 14 train only
use Phase 14 validation only as eval_set
predict all 10 validation horizons
record best_iteration
record raw predictions

Do NOT clip negative predictions.

Do NOT enforce chilled <= total.

Store fold metadata privately.

==================================================
DT-235 — LIGHTGBM CHALLENGER
==================================================

Implement:

1. LightGBM total challenger
2. LightGBM Fresh chilled challenger

Use identical Phase 14 backtests and the same semantic feature profile.

Recommended fixed config:

objective = regression_l1
metric = l1
n_estimators = 2000
learning_rate = 0.03
num_leaves = 31
min_child_samples = 20
reg_lambda = 1.0
random_state = 42
n_jobs = 1
early_stopping_rounds = 100

Recommended preprocessing:

NUMERIC:
SimpleImputer(strategy="median")

CATEGORICAL:
SimpleImputer(strategy="constant", fill_value="__MISSING__")
OneHotEncoder(handle_unknown="ignore")

Fit preprocessing on FOLD TRAIN only.

If LightGBM is not installed:
add/update the approved dependency and run a synthetic smoke test.

Do not silently skip DT-235.

==================================================
EARLY STOPPING / FINAL ITERATION POLICY
==================================================

For both model families record:

best_iteration
best_validation_metric
stopped_early
configured_max_iterations

Recommended Phase 17 iteration rule:

median valid backtest best_iteration

Do not derive final iterations from Task 2A test predictions.

==================================================
DT-236 — COMPARE ML VS PHASE 15 REFERENCES
==================================================

For total compare at minimum:

Phase 15 reference total baseline
CatBoost total
LightGBM total

For chilled compare at minimum:

Phase 15 reference Fresh chilled baseline
CatBoost Fresh chilled
LightGBM Fresh chilled

Every candidate must use exactly the same:

backtest IDs
origins
series
horizons
validation rows
metric functions

Candidate eligibility requires:

all required backtests completed
all required validation predictions present
finite predictions
no leakage failure
matching Phase 14 signature

Primary comparison:

overall pooled MAE

Secondary:

RMSE
P90 absolute error
backtest MAE standard deviation
worst backtest MAE
WAPE where defined
bias

Diagnostics:

per-series
per-horizon
negative_prediction_count
Fresh chilled_gt_total_count

==================================================
DT-237 — REJECT ADVANCED MODEL WHEN NOT JUSTIFIED
==================================================

Freeze before real private scores:

relative_tie_tolerance_pct = 0.5

For baseline MAE B > 0 and advanced MAE A:

relative_improvement_pct = 100 * (B - A) / B

If improvement > 0.5%:
advanced candidate may remain eligible.

If improvement <= 0.5%:
prefer the simpler reference baseline unless a predeclared tie-break
clearly supports another simpler-equivalent choice.

If baseline MAE == 0:
baseline wins.

Do not modify the tolerance after seeing real scores.

Tie-break order:

1. RMSE
2. P90 AE
3. backtest MAE std
4. simplicity

A baseline winner is a VALID successful Phase 16 result.

==================================================
DT-238 — TEST FIXED ENSEMBLES
==================================================

Do NOT learn ensemble weights.

Do NOT grid-search weights.

Test fixed candidate A:

0.5 * CatBoost
+
0.5 * LightGBM

Test fixed candidate B:

0.5 * best eligible advanced
+
0.5 * Phase 15 reference baseline

Do separately for:

total
Fresh chilled

Before averaging align exactly on:

backtest_id
depot
brand
origin_week_start_date
target_week_start_date
forecast_horizon

Duplicate/missing component keys:
ensemble ineligible.

Do not silently degrade an ensemble to one component.

==================================================
DT-239 — SELECT TOTAL CHAMPION
==================================================

Eligible set may contain:

Phase 15 total reference
CatBoost total
LightGBM total
fixed ensembles

Apply:

DT-237 complexity/rejection rule
then overall MAE
then RMSE
then P90 AE
then backtest MAE stability
then simplicity within tie tolerance

Review privately:

per-series performance
per-horizon performance
worst backtest
bias
negative predictions

Exactly ONE total champion must be frozen.

==================================================
DT-240 — SELECT FRESH CHILLED CHAMPION
==================================================

Selection population:

Fresh only

Eligible set may contain:

Phase 15 Fresh chilled reference
CatBoost chilled
LightGBM chilled
fixed chilled ensembles

Use same selection hierarchy.

Do NOT use Style/Tech zero rows to make chilled ML look better.

Style final chilled:
0 exactly

Tech final chilled:
0 exactly

Record raw chilled>total diagnostic only.
Do not correct in Phase 16.

Exactly ONE Fresh chilled champion must be frozen.

==================================================
DT-241 — FREEZE TASK 2A FINAL CONFIG
==================================================

Create/finalize:

configs/task2a_final_models.yaml

It must contain:

state: FROZEN

source contract references:
Phase 11
Phase 13
Phase 14
Phase 15
Phase 16

feature registry/profile identity
Phase 14 backtest signature
selection policy/tolerance

TOTAL champion:
- approach type
- candidate ID
- family/baseline identity
- exact parameters
- ensemble components/weights when applicable
- final iteration rule/value when model-based

FRESH CHILLED champion:
- same information

structural rules:
Style chilled zero = true
Tech chilled zero = true

Phase 17 postprocessing ownership:
clip negative = true
enforce chilled <= total = true
rounding = none

Do NOT write private backtest metric values to this tracked config.

Implement strict config validation.

Phase 17 must refuse an unfrozen/ambiguous config.

==================================================
RAW PREDICTION POLICY
==================================================

During Phase 16 scoring DO NOT:

clip negative predictions
cap chilled at total
round predictions
apply manual upper caps

Record diagnostics only.

The finalized inventory assigns final constraints to:

DT-248 clip negative forecasts
DT-249 enforce chilled <= total

Those belong to Phase 17.

==================================================
REQUIRED SYNTHETIC TESTS
==================================================

CATBOOST:
- total fit/predict
- Fresh chilled fit/predict
- no Style/Tech chilled training rows
- target absent from X
- exact Phase 14 split reuse
- early stopping metadata
- best iteration collection
- finite raw predictions
- no silent clipping

LIGHTGBM:
- total fit/predict
- Fresh chilled fit/predict
- train-only preprocessing
- unseen validation category
- missing numeric
- same semantic feature profile
- early stopping metadata
- deterministic behavior

COMPARISON:
- backtest signature mismatch rejected
- incomplete fold candidate ineligible
- missing prediction ineligible
- NaN/Inf rejected
- Phase 14 metric reuse
- correct relative improvement

REJECTION GATE:
- materially better advanced eligible
- worse advanced rejected
- within 0.5% baseline preferred
- baseline MAE zero
- exact boundary deterministic

ENSEMBLE:
- exact 50/50
- keyed alignment
- reordered rows handled
- duplicates rejected
- missing component rejected
- no learned weights

TOTAL SELECTION:
- baseline can win
- CatBoost can win
- LightGBM can win
- ensemble can win
- correct tie-break hierarchy
- exactly one champion

CHILLED SELECTION:
- Fresh only
- Style/Tech excluded from ranking
- baseline/ML/ensemble can win
- chilled>total only diagnostic
- exactly one champion

FINAL CONFIG:
- valid baseline config
- valid model config
- valid ensemble config
- unfrozen rejected
- ambiguous champion rejected
- bad ensemble weights rejected
- model iteration policy required
- Style zero required
- Tech zero required
- no private metrics

LEAKAGE:
- future-demand mutation invariant
- h10 does not use intermediate future demand
- training target known by origin
- validation-y mutation invariant
- no within-window outcome updates

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After DT-234:
run CatBoost tests.

After DT-235:
run LightGBM/preprocessing tests.

After DT-236–DT-238:
run comparison/rejection/ensemble tests.

After DT-239–DT-241:
run model-selection/config tests.

Fix ordinary code/test failures automatically.

Then run the full Task 2A suite including at least:

tests/test_task2a_history.py
tests/test_task2a_eda.py
tests/test_task2a_features.py
tests/test_task2a_multihorizon.py
tests/test_task2a_validation.py
tests/test_task2a_metrics.py
tests/test_task2a_baselines.py
tests/test_task2a_baseline_evaluation.py
tests/test_task2a_advanced_models.py
tests/test_task2a_model_preprocessing.py
tests/test_task2a_ensembles.py
tests/test_task2a_model_selection.py

Then:

pytest -q
python -m pip check

git status
git diff

If a documented test requires private real competition data:
do NOT run it in Codex.
Report the local command for the human.

Ensure these are not staged:

data/raw/**
data/interim/**
reports/private/**

==================================================
LOCAL REAL-DATA COMMAND
==================================================

Implement but DO NOT execute against restricted private competition data:

python scripts/run_task2a_advanced_models.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --multihorizon-table data/interim/task2a_multihorizon_train.csv \
  --feature-config configs/task2a_features.yaml \
  --validation-config configs/task2a_validation.yaml \
  --baseline-results reports/private/phase15_task2a_baselines \
  --model-config configs/task2a_advanced_models.yaml \
  --output-dir reports/private/phase16_task2a_advanced

Then local freeze command:

python scripts/freeze_task2a_model_config.py \
  --advanced-config configs/task2a_advanced_models.yaml \
  --validation-config configs/task2a_validation.yaml \
  --feature-config configs/task2a_features.yaml \
  --selection reports/private/phase16_task2a_advanced/selection_decisions.json \
  --output configs/task2a_final_models.yaml

Do not copy private score values into tracked config.

==================================================
STOP CONDITIONS
==================================================

STOP if:

- Phase 14 validation is changed
- Phase 15 baseline identity is changed
- models use different backtests
- future demand enters a predictor
- a training label occurs after validation origin
- validation outcomes update later horizons
- targets enter X
- a pre-trained/proprietary API model is used
- AutoML/open-ended tuning is introduced
- LightGBM is silently skipped
- failed folds are silently removed
- advanced model wins despite failing frozen rejection rule
- ensemble weights are optimized from private backtest scores
- ensemble keys do not align
- Style/Tech chilled semantics change
- clipping/capping occurs before Phase 16 metrics
- more than one champion remains
- final config is not FROZEN
- Task 1 frozen artifacts change
- private data must be exposed
- safe tests cannot pass without breaking approved contracts

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-234 READY
DT-235 READY
DT-236 READY
DT-237 READY
DT-238 READY
DT-239 READY
DT-240 READY
DT-241 READY

Phase 14 backtests reused exactly
Phase 15 references reused exactly
CatBoost total/Fresh chilled complete
LightGBM total/Fresh chilled complete
same semantic features
fold-safe preprocessing
future-demand leakage tests pass
raw predictions evaluated
advanced rejection gate implemented
fixed ensembles implemented
no weight tuning
exactly one total champion
exactly one Fresh chilled champion
baseline allowed to win
Style chilled zero preserved
Tech chilled zero preserved
final config validator passes
all synthetic tests pass
full safe suite passes
pip check passes
private outputs ignored
Task 1 unchanged
no Phase 17 code added

==================================================
RETURN ONLY
==================================================

PHASE:
16 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-234 READY / FAIL
DT-235 READY / FAIL
DT-236 READY / FAIL
DT-237 READY / FAIL
DT-238 READY / FAIL
DT-239 READY / FAIL
DT-240 READY / FAIL
DT-241 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

PHASE 14 BACKTEST SIGNATURE:
PASS / FAIL

PHASE 15 REFERENCE BASELINES:
PASS / FAIL

CATBOOST TOTAL:
READY / FAIL

CATBOOST FRESH CHILLED:
READY / FAIL

LIGHTGBM TOTAL:
READY / FAIL

LIGHTGBM FRESH CHILLED:
READY / FAIL

FUTURE-DEMAND LEAKAGE AUDIT:
PASS / FAIL

ADVANCED-VS-SIMPLE REJECTION GATE:
PASS / FAIL

ENSEMBLE TESTS:
PASS / FAIL

TOTAL CHAMPION SELECTION:
READY / FAIL

FRESH CHILLED CHAMPION SELECTION:
READY / FAIL

FINAL TASK2A CONFIG VALIDATOR:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 16 experiment command and freeze command.

PHASE 16 STATUS:
AWAITING LOCAL ADVANCED MODELLING RUN

READY FOR PHASE 17:
NO

Then STOP.

Do not start Phase 17.
```

---

# 35. Independent Phase 16 review prompt

Use this in a **fresh Codex session** after the human local Phase 16 run and config freeze.

```text
Perform an independent review of completed WayLoom Datathon Phase 16.

REVIEW ONLY.

Do NOT:

- inspect data/raw/**
- inspect data/interim/**
- inspect reports/private/**
- run real modelling experiments
- modify code initially
- modify configs initially
- reopen model selection
- start Phase 17

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 16
4. PHASE_14_COMPETITION_CONTRACT.md
5. PHASE_15_COMPETITION_CONTRACT.md
6. PHASE_16_COMPETITION_CONTRACT.md
7. src/task2a/advanced_models.py
8. src/task2a/model_preprocessing.py
9. src/task2a/ensembles.py
10. src/task2a/model_selection.py
11. scripts/run_task2a_advanced_models.py
12. scripts/freeze_task2a_model_config.py
13. configs/task2a_advanced_models.yaml
14. configs/task2a_final_models.yaml
15. docs/task2a_advanced_modeling_spec.md
16. Phase 16 test files
17. .gitignore / .cursorignore / relevant ignore config

HUMAN SANITIZED LOCAL RESULT:

LOCAL PHASE 16 ADVANCED MODELLING: <PASS/FAIL>
PHASE 14 BACKTEST SIGNATURE MATCH: <YES/NO>
PHASE 15 REFERENCES LOADED: <YES/NO>
CATBOOST TOTAL: <COMPLETE/FAIL>
CATBOOST FRESH CHILLED: <COMPLETE/FAIL>
LIGHTGBM TOTAL: <COMPLETE/FAIL>
LIGHTGBM FRESH CHILLED: <COMPLETE/FAIL>
FUTURE-DEMAND LEAKAGE AUDIT: <PASS/FAIL>
ALL REQUIRED BACKTESTS COMPLETE: <YES/NO>
ENSEMBLES TESTED: <YES/NO>
TOTAL CHAMPION FROZEN: <YES/NO>
FRESH CHILLED CHAMPION FROZEN: <YES/NO>
TASK2A FINAL CONFIG VALID: <YES/NO>
TASK 1 ARTIFACTS CHANGED: <NO/YES>

Do NOT ask for private metric values.

==================================================
AUDIT DT-234
==================================================

Verify CatBoost:

- locally trained from scratch
- total model uses all eligible series
- chilled model trains Fresh only
- Phase 14 splits exact
- target absent from X
- early stopping fold-safe
- raw predictions retained
- no clipping
- best iteration captured

==================================================
AUDIT DT-235
==================================================

Verify LightGBM:

- challenger exists, not silently skipped
- same semantic features
- same Phase 14 splits
- preprocessing fit train-only
- unseen validation category safe
- early stopping fold-safe
- raw predictions retained

==================================================
AUDIT DT-236
==================================================

Verify comparison:

- Phase 15 reference identities reused
- same backtest population
- Phase 14 metrics reused
- incomplete candidates cannot rank
- private failures not silently dropped

==================================================
AUDIT DT-237
==================================================

Verify:

- relative tie tolerance is predeclared
- simpler baseline preferred within tolerance
- baseline can legitimately remain champion
- threshold not adapted based on private score

==================================================
AUDIT DT-238
==================================================

Verify ensembles:

- weights fixed before real scores
- exact key alignment
- no learned/optimized weights
- missing component makes ensemble ineligible
- no pre-evaluation clipping/capping

==================================================
AUDIT DT-239 / DT-240
==================================================

Verify:

- exactly one total champion
- exactly one Fresh chilled champion
- total primary metric = Phase 14 pooled MAE
- chilled primary population = Fresh only
- frozen tie-break order used
- Style/Tech zero rows do not distort chilled ranking

==================================================
AUDIT DT-241
==================================================

Verify configs/task2a_final_models.yaml:

- state FROZEN
- source contracts referenced
- feature profile identified
- validation signature identified
- total champion unambiguous
- Fresh chilled champion unambiguous
- baseline/model/ensemble metadata complete
- ensemble weights sum to one when applicable
- iteration policy complete when model-based
- Style chilled zero = true
- Tech chilled zero = true
- Phase 17 clipping ownership explicit
- Phase 17 chilled<=total ownership explicit
- no private metric tables/values embedded

==================================================
LEAKAGE / SAFETY
==================================================

Verify tests prove:

- future demand cannot affect origin features
- horizon 10 cannot use intermediate actual future demand
- training label is known by validation origin
- validation y cannot change validation X
- no within-window outcome update
- target columns absent

Verify competition modelling rules:

- no pre-trained model
- no proprietary modelling API
- no AutoML/end-to-end modelling system

==================================================
RUN SAFE TESTS
==================================================

Run relevant Phase 16 tests and full safe Task 2A regression tests.

Then:

pytest -q
python -m pip check
git status

Do not run real private-data experiments.

==================================================
RETURN
==================================================

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

DT-234: PASS / FAIL
DT-235: PASS / FAIL
DT-236: PASS / FAIL
DT-237: PASS / FAIL
DT-238: PASS / FAIL
DT-239: PASS / FAIL
DT-240: PASS / FAIL
DT-241: PASS / FAIL

PHASE 14 VALIDATION REUSE:
PASS / FAIL

PHASE 15 BASELINE REUSE:
PASS / FAIL

CATBOOST IMPLEMENTATION:
PASS / FAIL

LIGHTGBM IMPLEMENTATION:
PASS / FAIL

LEAKAGE PROTECTION:
PASS / FAIL

ENSEMBLE POLICY:
PASS / FAIL

COMPLEXITY REJECTION RULE:
PASS / FAIL

TOTAL CHAMPION FREEZE:
PASS / FAIL

CHILLED CHAMPION FREEZE:
PASS / FAIL

FINAL CONFIG:
PASS / FAIL

SYNTHETIC/SAFE TESTS:
PASS / FAIL

HUMAN LOCAL RUN:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

TASK 1 FROZEN STATE:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

PHASE 16 REVIEW:
PASS / FAIL

READY FOR PHASE 17:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not start Phase 17.
```

---

# 36. Phase 16 completion record template

```markdown
# Phase 16 Completion Record

## Tasks

- [ ] DT-234
- [ ] DT-235
- [ ] DT-236
- [ ] DT-237
- [ ] DT-238
- [ ] DT-239
- [ ] DT-240
- [ ] DT-241

## Agent implementation

- CatBoost total: READY / FAIL
- CatBoost Fresh chilled: READY / FAIL
- LightGBM total: READY / FAIL
- LightGBM Fresh chilled: READY / FAIL
- Comparison layer: READY / FAIL
- Rejection gate: READY / FAIL
- Ensembles: READY / FAIL
- Selection logic: READY / FAIL
- Final config validator: READY / FAIL
- Synthetic tests: PASS / FAIL
- Full safe suite: PASS / FAIL
- pip check: PASS / FAIL

## Local private run

- Advanced experiment: PASS / FAIL
- Phase 14 signature match: YES / NO
- Phase 15 references loaded: YES / NO
- Required backtests complete: YES / NO
- Leakage audit: PASS / FAIL
- Ensembles tested: YES / NO
- Total champion selected: YES / NO
- Fresh chilled champion selected: YES / NO
- Final config frozen: YES / NO

## Safety

- Future demand used: NO / YES
- Target fields in X: 0 / nonzero
- Pre-trained model used: NO / YES
- Proprietary modelling API used: NO / YES
- AutoML used: NO / YES
- Private data exposed to agent: NO / YES
- Task 1 artifacts changed: NO / YES

## Independent review

- Phase 16 review: PASS / FAIL

## Verdict

PHASE 16 STATUS: PASS / FAIL
READY FOR PHASE 17: YES / NO
```

---

# 37. Final Phase 16 checklist

Before Phase 17:

- [ ] Phase 15 passed.
- [ ] Phase 14 backtest signature matches.
- [ ] Phase 15 total reference baseline exists.
- [ ] Phase 15 Fresh chilled reference exists.
- [ ] CatBoost total candidate complete.
- [ ] CatBoost Fresh chilled candidate complete.
- [ ] LightGBM total challenger complete.
- [ ] LightGBM Fresh chilled challenger complete.
- [ ] Same semantic feature profile used.
- [ ] Fold preprocessing is train-only.
- [ ] Future-demand leakage tests pass.
- [ ] Training-target availability tests pass.
- [ ] Raw predictions evaluated.
- [ ] Negative prediction diagnostics captured.
- [ ] Fresh chilled>total diagnostics captured.
- [ ] Advanced candidates compared fairly with baselines.
- [ ] Frozen rejection rule applied.
- [ ] Baseline allowed to remain champion.
- [ ] Fixed ensembles tested.
- [ ] No ensemble weight search performed.
- [ ] Exactly one total champion selected.
- [ ] Exactly one Fresh chilled champion selected.
- [ ] Style/Tech chilled-zero output rule frozen.
- [ ] Final iteration rule frozen where applicable.
- [ ] `configs/task2a_final_models.yaml` state is `FROZEN`.
- [ ] No private metrics embedded in tracked config.
- [ ] Phase 16 tests pass.
- [ ] Full safe suite passes.
- [ ] `pip check` passes.
- [ ] Private artifacts remain ignored.
- [ ] Task 1 frozen artifacts unchanged.
- [ ] Independent review passes.
- [ ] No Phase 17 code was prematurely implemented.

Only then:

```text
PHASE 16 STATUS: PASS
READY FOR PHASE 17: YES
```
