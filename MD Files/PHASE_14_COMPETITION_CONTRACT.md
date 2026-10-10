# PHASE 14 — Task 2A Forecast Validation

> **Canonical filename:** `PHASE_14_COMPETITION_CONTRACT.md`  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-222 → DT-227**  
> **Task count:** 6  
> **Default phase priority:** P0  
> **Phase dependency:** Phases 11–13 must have passed  
> **Phase gate:** **Rolling-origin, ten-week backtesting is frozen, leakage-safe, deterministic, and reproducible before any Task 2A baseline or advanced model is compared.**

---

# 1. Purpose of Phase 14

Phase 14 freezes the validation contract for Task 2A before Phase 15 baseline models and Phase 16 advanced forecasting are evaluated.

Task 2A asks WayLoom to forecast weekly ordered volume for future depot + brand + week combinations. The official test horizon is ten future weeks. Therefore a trustworthy historical evaluation must reproduce the information boundary that exists when making a real ten-week forecast.

This phase must answer six questions before modelling continues:

1. **Where are historical forecast origins placed?**
2. **Does every backtest evaluate the full ten-week horizon?**
3. **Can any training row or feature borrow actual demand that would not yet be known at the forecast origin?**
4. **Which metrics are frozen before models are compared?**
5. **How is each depot + brand series evaluated?**
6. **How are all backtest predictions summarized overall?**

Phase 14 is primarily **validation infrastructure**, not modelling.

It must not:

- train the Phase 15 baselines;
- train CatBoost, LightGBM, XGBoost or other Phase 16 models;
- change the Phase 13 feature definitions;
- rebuild Task 2A history differently from Phase 11;
- use future actual demand to generate historical validation features;
- choose backtest origins based on which dates give better scores;
- choose metrics after seeing model performance;
- use Task 2A future targets, because none are supplied;
- begin final Task 2A inference.

---

# 2. Finalized master-inventory contract

The finalized WayLoom master task inventory defines Phase 14 exactly as follows.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-222** | [O] | P0 | DT-204–DT-221 | Define rolling-origin validation |
| [ ] | **DT-223** | [O] | P0 | Phases 11–13 | Use 10-week validation windows |
| [ ] | **DT-224** | [O] | P0 | Phases 11–13 | Prevent future-demand leakage |
| [ ] | **DT-225** | [E] | P0 | Phases 11–13 | Define forecast metrics |
| [ ] | **DT-226** | [E] | P0 | Phases 11–13 | Evaluate per series |
| [ ] | **DT-227** | [E] | P0 | Phases 11–13 | Evaluate overall |

**Phase complete:** [ ]  
**READY FOR PHASE 15:** NO

---

# 3. Official Task 2A requirements that constrain validation

The official Challenge Booklet requires Task 2A to forecast ordered volume for each supplied depot, brand, and forecast week over **10 future weeks**.

Required output fields are:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

The official historical demand construction rules already implemented in Phase 11 remain binding:

```text
history source 1 = deliveries_train.csv
history source 2 = task1_test_inputs.csv
```

Every unique order counts once, including:

```text
attempted
deferred
not_run
```

Demand belongs to the requested:

```text
order_date
```

and weekly grouping uses official:

```text
calendar.iso_year
calendar.iso_week
```

Only Fresh has chilled demand.

Therefore:

```text
Style chilled = 0
Tech chilled  = 0
```

The booklet does **not** prescribe the exact historical backtesting algorithm or scoring metric used internally by the team. Rolling-origin design and metric selection in this contract are WayLoom engineering choices that must be frozen before model comparison.

---

# 4. Source hierarchy

For Phase 14 use this authority order:

1. official Challenge Booklet and official supplied files;
2. finalized `WAYLOOM_DATATHON_MASTER_PLAN.md`;
3. approved Phase 11 history contract;
4. approved Phase 12 EDA contract;
5. approved Phase 13 forecasting-feature contract;
6. this Phase 14 implementation contract;
7. engineering assumptions explicitly documented as such.

If a lower source conflicts with a higher source:

```text
STOP
```

Do not silently reconcile the conflict.

---

# 5. Frozen upstream assumptions

Phase 14 assumes the following have already passed.

## Phase 11

Canonical historical panel exists with unique:

```text
depot
brand
iso_year
iso_week
```

and:

```text
total_volume_m3
chilled_volume_m3
```

No unresolved missing-week ambiguity remains.

## Phase 12

Calendar and seasonal context were analyzed but historical targets were not altered.

## Phase 13

The direct multi-horizon modelling table exists.

Canonical row grain:

```text
depot
brand
origin_week_start_date
forecast_horizon
```

with:

```text
forecast_horizon ∈ {1,2,...,10}
```

and target metadata such as:

```text
target_week_start_date
target_iso_year
target_iso_week
```

Training labels:

```text
target_total_volume_m3
target_chilled_volume_m3
```

Phase 13 already proved that a row at origin `t` uses demand-derived predictors from week `t` or earlier only.

Phase 14 must **re-audit**, not assume, that this property remains true after split construction.

---

# 6. Critical time semantics

This section is the core of Phase 14.

## 6.1 Forecast origin

A historical forecast origin is the last weekly point whose demand is treated as known when creating a backtest forecast.

Let:

```text
origin = t
```

Then the historical validation window is:

```text
t+1
t+2
...
t+10
```

These correspond to:

```text
forecast_horizon = 1..10
```

## 6.2 What is known at origin t

Allowed:

```text
historical demand through week t
static series identity
calendar information known for target weeks
forecast horizon
```

Not allowed:

```text
actual demand at t+1 .. t+10
actual demand from any later week
features fitted using validation target values
```

## 6.3 Direct multi-horizon training eligibility

A subtle leakage risk exists in the Phase 13 direct table.

Suppose validation origin is week `t`.

A historical training row may have an earlier origin, but if that row's target occurs after `t`, its label would not have been known at forecast time `t`.

Therefore the training eligibility rule is:

```text
training_row.target_week_start_date <= validation_origin_week_start_date
```

NOT merely:

```text
training_row.origin_week_start_date < validation_origin_week_start_date
```

The second rule is insufficient.

Example:

```text
validation origin = week 60

candidate training row:
origin  = week 55
horizon = 10
target  = week 65
```

At week 60, the actual label for week 65 is unknown.

Therefore that row must NOT be in training for the week-60 backtest.

This exact condition requires synthetic tests.

---

# 7. Phase 14 execution strategy

Phase 14 is a **task/small-batch validation phase** because DT-222–DT-224 define the information boundary used by every forecast model later.

Recommended order:

```text
Checkpoint A
DT-222
Rolling-origin splitter
      ↓
STOP + targeted tests
      ↓
Checkpoint B
DT-223
Exact 10-week validation windows
      ↓
STOP + targeted tests
      ↓
Checkpoint C
DT-224
Future-demand leakage audit
      ↓
STOP + full split/leakage tests
      ↓
Checkpoint D
DT-225
Freeze metric contract
      ↓
Checkpoint E
DT-226
Per-series evaluation
      ↓
Checkpoint F
DT-227
Overall evaluation
      ↓
Full safe regression suite
      ↓
Human local validation-plan build
      ↓
Independent Codex review
```

Do not allow the agent to continue into Phase 15 in the same run.

---

# 8. Required repository additions

Create or update:

```text
src/task2a/
├── validation.py
└── metrics.py

scripts/
└── build_task2a_validation_plan.py

configs/
└── task2a_validation.yaml

docs/
└── task2a_validation_spec.md

tests/
├── test_task2a_validation.py
└── test_task2a_metrics.py
```

Recommended private runtime outputs:

```text
reports/private/phase14_task2a_validation/
├── validation_plan.json
├── backtest_origins.csv
├── backtest_assignments.csv
├── horizon_coverage.csv
├── leakage_audit.json
├── metric_contract.json
├── series_coverage.csv
├── validation_summary.json
└── phase14_validation_report.md
```

Do not commit private output files.

---

# 9. Recommended validation configuration

Create:

```text
configs/task2a_validation.yaml
```

Recommended initial WayLoom engineering contract:

```yaml
version: 1

series_key:
  - depot
  - brand

origin_column: origin_week_start_date
target_week_column: target_week_start_date
horizon_column: forecast_horizon

backtesting:
  strategy: rolling_origin
  validation_horizon_weeks: 10
  n_backtests: 4
  step_weeks: 10
  minimum_training_weeks: 52
  require_full_horizon: true
  require_same_origins_across_series: true
  choose_origins_from_date_coverage_only: true

training_eligibility:
  require_target_week_on_or_before_origin: true
  require_feature_source_week_on_or_before_origin: true

metrics:
  total_volume:
    primary: mae
    secondary:
      - rmse
      - wape
      - mean_bias_m3
      - p90_absolute_error

  chilled_volume:
    primary: mae
    secondary:
      - rmse
      - wape
      - mean_bias_m3
      - p90_absolute_error
    primary_population: Fresh

  structural_zero_chilled:
    brands:
      - Style
      - Tech
    required_value: 0.0

  wape_zero_denominator: null

prediction_diagnostics:
  evaluate_raw_predictions: true
  count_negative_predictions: true
  count_nonfinite_predictions: true
  count_chilled_gt_total: true
  apply_phase17_postprocessing: false

series_evaluation:
  minimum_points: 10
  report_macro_average: true
  report_micro_average: true

horizon_diagnostics:
  enabled: true
  horizons:
    - 1
    - 2
    - 3
    - 4
    - 5
    - 6
    - 7
    - 8
    - 9
    - 10

privacy:
  private_output_dir: reports/private/phase14_task2a_validation
```

## Important status of these numbers

The following are WayLoom engineering choices, not organizer rules:

```text
n_backtests = 4
step_weeks = 10
minimum_training_weeks = 52
MAE as primary metric
RMSE/WAPE/bias/P90-AE as secondary metrics
```

They must be frozen **before Phase 15 model scores are observed**.

If the real historical date coverage cannot support this exact configuration, the local Phase 14 coverage report must stop with an explicit insufficiency message. A revised configuration may be chosen based only on available date coverage, never based on model performance.

---

# 10. Backtest origin-selection rules

Origin selection must be deterministic and target-value independent.

## 10.1 Eligible origin

An origin `t` is eligible only when:

1. every required series has a row for origin `t`;
2. every required series has all horizons 1 through 10 available historically;
3. all ten target weeks exist in the canonical weekly panel;
4. the training history before/through `t` satisfies `minimum_training_weeks`;
5. there are no unresolved weekly gaps;
6. Phase 13 leakage invariants hold.

## 10.2 Same origins across series

Prefer the same backtest origins for every series.

Why:

```text
Fresh/Kandy and Tech/Peliyagoda should not be compared on different historical periods merely because one series is easier to score.
```

If one required series cannot support an origin, that origin is not globally eligible unless the contract explicitly defines otherwise.

## 10.3 Choosing the final set of origins

Recommended deterministic algorithm:

1. list all globally eligible origins in chronological order;
2. select the latest eligible origin;
3. move backward by at least `step_weeks`;
4. select the latest eligible origin on/before that date;
5. repeat until `n_backtests` origins are chosen;
6. return selected origins in chronological order for reporting.

Do not choose origins because they have low/high/spiky demand.

Do not choose origins after seeing forecast scores.

---

# 11. DT-222 — Define rolling-origin validation

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-204–DT-221

## Objective

Implement deterministic rolling-origin backtesting that mimics repeated historical forecast creation.

## Input

Canonical Phase 13 direct multi-horizon table:

```text
data/interim/task2a_multihorizon_train.csv
```

and canonical Phase 11 weekly panel for coverage verification:

```text
data/interim/task2a_weekly_panel.csv
```

## Required output structure

Recommended dataclass:

```python
@dataclass(frozen=True)
class ForecastBacktestSplit:
    backtest_id: str
    origin_week_start_date: pd.Timestamp
    train_indices: np.ndarray
    validation_indices: np.ndarray
    validation_target_start_date: pd.Timestamp
    validation_target_end_date: pd.Timestamp
```

Recommended functions:

```python
resolve_required_series(...)
find_eligible_forecast_origins(...)
select_rolling_origins(...)
build_backtest_split(...)
build_rolling_origin_plan(...)
validate_backtest_plan(...)
```

## Training-row eligibility

For validation origin `t`:

```text
training target week <= t
```

Every training label must have existed by the forecast origin.

Training origins will therefore normally be earlier than `t`, but the target-date condition is the authoritative leakage boundary.

## Validation-row eligibility

Validation rows must have:

```text
origin_week_start_date == t
forecast_horizon in 1..10
```

for every required series.

## Required assertions

Per split:

```text
train nonempty
validation nonempty
```

```text
max(training target week) <= validation origin
```

```text
min(validation target week) > validation origin
```

```text
no training row target occurs inside or after an unknown future period relative to origin
```

```text
train row IDs/indexes and validation row IDs/indexes disjoint
```

Across backtests:

```text
origins strictly increasing
```

Training information expands over time.

## Tests

Synthetic tests must prove:

- first valid origin;
- multiple origins;
- deterministic selection;
- no random shuffling;
- train set expands for later origin;
- training row with early origin but future target is excluded;
- origin choice independent of target values;
- insufficient history fails clearly.

## STOP conditions

Stop if:

- an origin is selected using target magnitude;
- training eligibility uses origin date only and ignores target date;
- unresolved gaps exist;
- required series are silently dropped.

## Definition of Done

- [ ] rolling origin implementation exists;
- [ ] origin-selection algorithm deterministic;
- [ ] training label availability enforced;
- [ ] synthetic tests pass.

---

# 12. DT-223 — Use 10-week validation windows

**Mark:** [O]  
**Priority:** P0

## Objective

Make every historical validation episode mirror the official ten-week Task 2A forecast horizon.

## Required validation shape

For each origin `t` and series:

```text
horizon 1  → target t+1
horizon 2  → target t+2
...
horizon 10 → target t+10
```

Required horizon set:

```text
{1,2,3,4,5,6,7,8,9,10}
```

Exactly once per required series per backtest.

## Required coverage checks

For every:

```text
backtest_id + depot + brand
```

assert:

```text
row_count == 10
```

and:

```text
sorted(forecast_horizon) == [1,2,3,4,5,6,7,8,9,10]
```

and:

```text
target week sequence is ten consecutive weekly steps
```

No duplicated horizon.

No missing horizon.

No horizon 0.

No horizon 11.

## Why exact ten-week windows matter

Do not validate only horizon 1 and call it a Task 2A forecast validation.

A recursive or direct model can behave very differently at:

```text
h=1
vs
h=10
```

The competition requires ten future weeks, so the full range must be tested.

## Non-overlapping backtest windows

The recommended default `step_weeks = 10` creates non-overlapping validation target windows.

This is an engineering design that simplifies interpretation and prevents one actual week from dominating several adjacent backtests.

If a different step is later chosen due coverage, document it before model scoring.

## Tests

Required synthetic tests:

- full horizons 1..10 pass;
- missing horizon fails;
- duplicate horizon fails;
- horizon 0 fails;
- horizon 11 fails;
- target week misaligned with horizon fails;
- cross-year window passes;
- ISO week 53 transition passes;
- one series missing h=10 makes origin ineligible.

## STOP conditions

Stop if any accepted backtest lacks a complete ten-week evaluation window.

## Definition of Done

- [ ] all selected origins have exact 10-week windows;
- [ ] all required series have h=1..10;
- [ ] horizon/date alignment tested.

---

# 13. DT-224 — Prevent future-demand leakage

**Mark:** [O]  
**Priority:** P0  
**This is the critical Phase 14 gate.**

## Objective

Prove that historical backtests reproduce the real information boundary of Task 2A.

## Leakage layers

### Layer 1 — Predictor source-time leakage

Every demand-derived predictor must use source demand weeks:

```text
<= forecast origin
```

Use the Phase 13 feature registry/source-lineage metadata where available.

### Layer 2 — Training-label availability leakage

Every training row used at validation origin `t` must have:

```text
target_week <= t
```

This prevents earlier-origin rows with still-future labels from leaking.

### Layer 3 — Validation-feature leakage

Validation features for origin `t` must not depend on:

```text
actual t+1..t+10 demand
```

### Layer 4 — Validation fitting leakage

Any fit-dependent preprocessing/model component later used in Phases 15–16 must be fitted on backtest training data only.

Validation target rows must never be used to fit:

```text
imputers
encoders
scalers
models
learned target statistics
ensembles
```

### Layer 5 — Cross-horizon leakage

Within a single backtest, actual demand at horizon 1 must not update predictors for horizon 2..10.

The ten-week forecast is generated as one unseen future block unless a later model is explicitly designed as a recursive forecast using only its own prior predictions.

Actual validation outcomes can never be fed back.

## Critical mutation tests

### Test A — Future-target mutation invariance

1. select validation origin `t`;
2. build validation X;
3. change actual historical demand at `t+1..t+10` in a synthetic copy;
4. rebuild validation X;
5. assert X is unchanged.

### Test B — Horizon-10 intermediate-week isolation

1. build h=10 predictors for origin `t`;
2. change actual demand at `t+1`;
3. h=10 predictors must remain unchanged.

### Test C — Training-label availability

Create:

```text
row A: origin t-5, horizon 10, target t+5
```

At validation origin `t`, row A must be excluded from training.

### Test D — Same-origin future block

Changing validation labels must not change any validation feature matrix.

## Leakage audit output

Recommended private JSON:

```text
reports/private/phase14_task2a_validation/leakage_audit.json
```

Fields:

```text
predictor_source_time_pass
training_target_availability_pass
future_target_mutation_pass
cross_horizon_isolation_pass
validation_fit_scope_contract_pass
forbidden_future_feature_count
```

## STOP conditions

Any one of these means Phase 14 fails:

```text
future actual demand influences X
training label occurs after validation origin
validation target values influence preprocessing
h=10 sees actual h=1..h=9 demand
```

## Definition of Done

- [ ] all leakage layers enforced;
- [ ] mutation tests pass;
- [ ] training-target availability test passes;
- [ ] leakage audit is reusable by later phases.

---

# 14. DT-225 — Define forecast metrics

**Mark:** [E]  
**Priority:** P0

## Objective

Freeze Task 2A evaluation metrics before baseline/model comparison begins.

The official booklet does not prescribe the team's local backtesting metric, so the following is a WayLoom engineering contract.

## 14.1 Total-volume forecast metrics

### Primary

```text
MAE
```

Formula:

```text
mean(abs(y_true - y_pred))
```

Reasons:

- directly interpretable in cubic metres;
- robust compared with squared-error-only selection;
- valid with zero-volume weeks;
- simple enough for fair comparison across model families.

### Secondary

```text
RMSE
WAPE
mean_bias_m3
P90 absolute error
```

RMSE:

```text
sqrt(mean((y_true - y_pred)^2))
```

WAPE:

```text
100 * sum(abs(y_true - y_pred)) / sum(y_true)
```

If:

```text
sum(y_true) == 0
```

return:

```text
WAPE = unavailable / null
```

Do not divide by epsilon and pretend the percentage is meaningful.

Mean bias:

```text
mean(y_pred - y_true)
```

Interpretation:

```text
positive → overforecast tendency
negative → underforecast tendency
```

P90 absolute error captures upper-tail misses.

## 14.2 Chilled-volume metrics

Primary chilled performance population:

```text
Fresh only
```

Use the same:

```text
MAE
RMSE
WAPE
mean_bias_m3
P90 absolute error
```

Why Fresh only for primary chilled metrics:

```text
Style and Tech are structural zeros by official rule.
```

Including their guaranteed zero rows in primary chilled accuracy can artificially make a chilled forecasting approach look better.

For Style and Tech, validation is instead an exact structural invariant:

```text
predicted chilled must be 0 in final inference
```

Phase 17 implements this final-output rule.

## 14.3 Do not use MAPE as primary

Weekly demand may be zero.

Therefore ordinary MAPE can be undefined or unstable.

It may be omitted entirely.

Do not use ad-hoc epsilon MAPE for model selection.

## 14.4 Prediction diagnostics

For every evaluated prediction set also report:

```text
n
nonfinite_prediction_count
negative_prediction_count
chilled_gt_total_count
```

Important:

Phase 14 does not implement Phase 17 output correction.

The master inventory explicitly assigns:

```text
negative clipping → DT-248
chilled <= total enforcement → DT-249
```

Therefore Phase 14 evaluates raw model predictions and records violations rather than silently correcting them.

## 14.5 No rounding during metrics

Do not round forecasts before scoring.

## Metric helper API

Recommended:

```python
forecast_regression_metrics(y_true, y_pred) -> dict
forecast_prediction_diagnostics(total_pred, chilled_pred=None) -> dict
```

## Tests

Hand-calculated synthetic tests for:

- perfect MAE = 0;
- known MAE;
- known RMSE;
- WAPE known value;
- WAPE zero denominator returns null;
- positive bias;
- negative bias;
- known P90 AE;
- negative prediction counted, not clipped;
- NaN prediction rejected;
- Inf prediction rejected;
- length mismatch rejected;
- target NaN rejected.

## Definition of Done

- [ ] primary/secondary metrics frozen;
- [ ] zero-denominator policy explicit;
- [ ] raw-prediction diagnostics explicit;
- [ ] tests match hand calculations.

---

# 15. DT-226 — Evaluate per series

**Mark:** [E]  
**Priority:** P0

## Objective

Measure forecast performance separately for each operational demand series so a good overall score cannot hide a weak depot/brand combination.

## Canonical Task 2A series key

```text
depot + brand
```

Do not invent a different grouping per model.

## Per-series total metrics

For every:

```text
backtest_id + depot + brand
```

report across horizons 1..10:

```text
n
MAE
RMSE
WAPE
mean_bias_m3
P90_absolute_error
negative_prediction_count
```

Expected:

```text
n = 10
```

for every accepted backtest-series group.

## Per-series chilled metrics

For:

```text
brand == Fresh
```

report the same chilled metrics.

For Style and Tech:

```text
actual chilled == 0 exactly
```

and report structural-zero status instead of treating them as meaningful forecast series.

## Across-backtest per-series summary

For each depot + brand across all backtests, report:

```text
backtest_count
mean_MAE
std_MAE
median_MAE
worst_backtest_MAE
mean_RMSE
mean_WAPE where available
mean_bias_m3
```

Fresh chilled gets a separate corresponding summary.

## Horizon diagnostic within each series

Optional but strongly recommended:

```text
horizon 1..10
```

This helps identify whether errors systematically grow at longer horizons.

Do not change the model based on one lucky segment without considering the frozen primary overall contract.

## Required coverage status

Each series/backtest must be marked:

```text
COMPLETE_10_WEEK
```

Anything else is a Phase 14 validation-plan failure rather than a model-score row.

## Tests

Synthetic tests:

- two depots remain separate;
- three brands remain separate;
- 10 rows per series/backtest;
- Fresh chilled evaluated;
- Style/Tech chilled structural zero handled separately;
- zero-denominator WAPE handled;
- worst backtest chosen correctly;
- series with missing horizon fails coverage.

## Definition of Done

- [ ] all total series individually measurable;
- [ ] Fresh chilled individually measurable;
- [ ] structural-zero brands handled correctly;
- [ ] support counts explicit.

---

# 16. DT-227 — Evaluate overall

**Mark:** [E]  
**Priority:** P0

## Objective

Create one reproducible aggregate evaluation contract used by Phases 15 and 16 to compare forecasting approaches fairly.

## Overall total-volume metrics

### Micro aggregation

Pool all Task 2A total-volume validation rows across:

```text
backtests
series
horizons
```

and compute:

```text
MAE
RMSE
WAPE
mean_bias_m3
P90_absolute_error
```

This is the primary overall total-volume summary.

### Macro per-series aggregation

First calculate each series metric, then average eligible series equally.

Report explicitly as:

```text
macro_series_mae
macro_series_rmse
```

Do not confuse this with micro pooling.

## Overall Fresh chilled metrics

Pool only:

```text
brand == Fresh
```

for primary chilled metrics.

Report:

```text
Fresh chilled micro MAE
Fresh chilled micro RMSE
Fresh chilled WAPE
Fresh chilled bias
Fresh chilled P90 AE
```

Also report macro by Fresh depot series where applicable.

## Backtest stability

For each model later, overall report must include metrics by backtest plus:

```text
backtest_count
mean backtest MAE
std backtest MAE
best backtest
worst backtest
```

Do not silently drop a difficult backtest.

## Horizon diagnostics

Aggregate by:

```text
forecast_horizon = 1..10
```

Report at least:

```text
n
MAE
RMSE
bias
```

for total volume.

For Fresh chilled, the same horizon table is recommended.

This is diagnostic and does not replace the frozen overall primary metric.

## Model-comparison rule for future phases

Phase 15 and Phase 16 must compare models on the exact same backtest plan.

Total-volume approach selection:

```text
primary = overall pooled MAE
```

Then consider:

```text
RMSE
WAPE
backtest stability
per-series performance
horizon degradation
complexity
```

Fresh chilled approach selection:

```text
primary = Fresh-only overall pooled MAE
```

Then consider corresponding secondary metrics.

Do not combine total and chilled into an undocumented single score.

If a composite score is ever proposed later, it requires an explicit new documented decision before seeing results.

## Results schema for later phases

Recommended reusable evaluator output:

```text
model_name
target
backtest_id
scope
series_depot
series_brand
forecast_horizon
n
mae
rmse
wape
mean_bias_m3
p90_absolute_error
negative_prediction_count
nonfinite_prediction_count
chilled_gt_total_count
```

`scope` examples:

```text
overall_micro
series
horizon
backtest_overall
```

## Tests

Synthetic tests:

- pooled MAE exact;
- pooled RMSE exact;
- micro differs correctly from macro on unbalanced synthetic data;
- macro series weighting equal;
- all backtests included;
- best/worst backtest correct;
- horizon summaries 1..10;
- Fresh-only chilled aggregate;
- Style/Tech zero rows excluded from primary chilled score;
- deterministic output ordering.

## Definition of Done

- [ ] overall total contract frozen;
- [ ] overall Fresh chilled contract frozen;
- [ ] micro/macro labels unambiguous;
- [ ] backtest stability and horizon diagnostics supported;
- [ ] reusable evaluator available for Phases 15–16.

---

# 17. Recommended implementation architecture

## `src/task2a/validation.py`

Recommended public API:

```python
@dataclass(frozen=True)
class ForecastBacktestSplit:
    ...


def validate_phase13_multihorizon_table(...):
    ...


def find_eligible_forecast_origins(...):
    ...


def select_rolling_origins(...):
    ...


def make_forecast_backtest_split(...):
    ...


def build_rolling_origin_plan(...):
    ...


def validate_ten_week_window(...):
    ...


def audit_future_demand_leakage(...):
    ...
```

## `src/task2a/metrics.py`

Recommended:

```python
forecast_regression_metrics(...)
forecast_prediction_diagnostics(...)
evaluate_forecast_per_series(...)
evaluate_forecast_by_horizon(...)
evaluate_forecast_overall(...)
summarize_backtest_stability(...)
```

Metric functions should be:

```text
pure
model-agnostic
deterministic
```

They must not fit models.

---

# 18. Validation-plan outputs

The local Phase 14 command should produce a private plan with enough metadata for Phases 15–16 to reuse splits exactly.

Recommended `validation_plan.json` structure:

```json
{
  "version": 1,
  "validation_horizon_weeks": 10,
  "backtests": [
    {
      "backtest_id": "BT01",
      "origin_week_start_date": "...",
      "validation_target_start_date": "...",
      "validation_target_end_date": "..."
    }
  ],
  "metric_contract": {
    "total_primary": "mae",
    "chilled_primary": "mae",
    "chilled_primary_population": "Fresh"
  }
}
```

Do not store private target values in tracked configuration.

Backtest IDs must be deterministic.

Example:

```text
BT01
BT02
BT03
BT04
```

ordered chronologically.

---

# 19. Required synthetic tests

Create:

```text
tests/test_task2a_validation.py
tests/test_task2a_metrics.py
```

Use synthetic weekly panels and Phase 13-style direct tables only.

## DT-222 tests

- valid rolling-origin split;
- deterministic origin choice;
- target values do not affect origin choice;
- train target dates <= origin;
- early-origin/future-target row excluded;
- train/validation row disjointness;
- expanding historical availability;
- minimum history requirement;
- insufficient backtests fails clearly;
- required series cannot be silently dropped.

## DT-223 tests

- exactly h=1..10;
- exactly ten rows per series/backtest;
- missing h=5 fails;
- duplicate h=5 fails;
- h=0 fails;
- h=11 fails;
- target date = origin+h;
- cross-year window;
- ISO week 53 transition;
- globally incomplete origin rejected.

## DT-224 tests

- future target mutation does not alter X;
- h=10 does not consume h=1 actual demand;
- training row target after origin excluded;
- validation y unavailable to transform;
- future-demand feature lineage rejected;
- validation actual outcomes cannot update later horizons;
- same synthetic data shuffled gives same split after stable ordering.

## DT-225 tests

- perfect MAE/RMSE;
- known MAE;
- known RMSE;
- WAPE known value;
- WAPE zero denominator = null;
- known bias;
- known P90 AE;
- negative prediction counted;
- negative prediction not clipped;
- nonfinite prediction rejected;
- mismatched lengths rejected.

## DT-226 tests

- per-series isolation;
- per-depot isolation;
- per-brand isolation;
- exactly 10-point evaluation;
- Fresh chilled metrics;
- Style chilled structural-zero handling;
- Tech chilled structural-zero handling;
- per-series backtest stability;
- missing-horizon series rejected.

## DT-227 tests

- overall pooled metrics;
- micro vs macro distinction;
- equal-weight macro behavior;
- all backtests included;
- no failed-backtest dropping;
- horizon diagnostics;
- Fresh-only chilled overall;
- deterministic results schema/order.

---

# 20. Edge cases

## 20.1 ISO year boundary

A validation window may span December/January.

Use continuous weekly dates from the canonical panel.

Do not perform arithmetic by simply adding to ISO week number.

## 20.2 ISO week 53

Must work correctly.

Do not assume every ISO year has exactly 52 weeks.

## 20.3 Zero-demand week

Valid target.

Keep it.

Do not remove it to make WAPE easier.

## 20.4 WAPE denominator zero

Return unavailable/null for that scope.

MAE/RMSE remain valid.

## 20.5 One series lacks full ten weeks

If `require_same_origins_across_series = true`, reject that backtest origin globally.

Do not silently evaluate the easier series only.

## 20.6 Short history

Do not shrink the validation horizon below 10.

Instead:

```text
INSUFFICIENT_BACKTEST_HISTORY
```

and stop for a coverage-based config decision.

## 20.7 Overlapping windows

Default design uses 10-week step and non-overlapping validation windows.

If overlap is later intentionally enabled, document it before model scores and explain that the same actual week may influence several backtest metrics.

## 20.8 Negative model forecast

Phase 14 metric code records it.

Do not clip it here.

## 20.9 Chilled forecast greater than total

Record diagnostic count.

Do not enforce the Phase 17 cap during Phase 14 evaluation.

## 20.10 Structural-zero brands

Style/Tech chilled actuals must remain exactly zero.

Do not let these guaranteed zeros dominate primary chilled model selection.

## 20.11 Missing target-week calendar feature

This should already have failed Phase 13.

If detected here:

```text
STOP
```

## 20.12 Reordered input

Validation split and metric results must be deterministic after canonical sorting.

---

# 21. Phase 14 hard STOP conditions

`READY FOR PHASE 15` remains **NO** if any of the following occurs:

- Phase 11 weekly panel is not canonical;
- Phase 13 direct multi-horizon table is not canonical;
- unresolved historical gaps remain;
- weekly keys duplicate;
- backtest origins are chosen using target values;
- any accepted origin lacks horizon 1..10;
- required series use different origins without an explicit frozen policy;
- training row target week is later than the backtest origin;
- validation X changes when future validation actual demand changes;
- h=10 predictors use actual h=1..h=9 demand;
- validation outcomes update later horizons;
- a future-demand-derived feature enters X;
- metric definitions are not frozen;
- metrics silently clip predictions;
- MAPE with arbitrary epsilon becomes primary;
- failed backtests are dropped from overall evaluation;
- per-series coverage is hidden;
- Style/Tech structural chilled-zero logic is lost;
- private competition data must be exposed to the external coding agent;
- synthetic tests fail;
- local validation-plan build fails;
- independent review fails.

---

# 22. Phase 14 Definition of Done

Phase 14 passes only when:

- [ ] **DT-222 PASS** — deterministic rolling-origin validation exists;
- [ ] **DT-223 PASS** — every accepted backtest uses an exact ten-week horizon;
- [ ] **DT-224 PASS** — future-demand leakage controls and mutation tests pass;
- [ ] **DT-225 PASS** — metric contract is frozen and unit-tested;
- [ ] **DT-226 PASS** — per-series evaluation is reproducible;
- [ ] **DT-227 PASS** — overall evaluation is reproducible;
- [ ] validation origins are selected from date coverage only;
- [ ] training rows satisfy target-week <= origin;
- [ ] horizon set is exactly 1..10;
- [ ] all required series share the frozen backtest origins;
- [ ] total-volume primary metric is frozen;
- [ ] Fresh chilled primary metric is frozen;
- [ ] Style/Tech structural chilled-zero handling is explicit;
- [ ] WAPE zero-denominator behavior is explicit;
- [ ] prediction-invalidity diagnostics exist;
- [ ] no Phase 17 clipping/capping is silently applied;
- [ ] horizon diagnostics exist;
- [ ] backtest stability summary exists;
- [ ] metric functions are model-agnostic;
- [ ] Phase 15/16 can reuse exact split IDs;
- [ ] all synthetic tests pass;
- [ ] full safe regression suite passes;
- [ ] local private validation-plan generation passes;
- [ ] Task 1 frozen artifacts remain untouched;
- [ ] private artifacts remain ignored;
- [ ] independent review passes;
- [ ] no unresolved STOP condition remains.

Then:

```text
PHASE 14 STATUS: PASS
READY FOR PHASE 15: YES
```

---

# 23. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-14-task2a-validation
```

Recommended commits:

```text
feat(task2a): add rolling-origin validation planner
feat(task2a): enforce ten-week backtest windows
feat(task2a): add future-demand leakage audit
feat(task2a): freeze forecast metric contract
feat(task2a): add per-series and overall evaluators
test(task2a): add forecast validation and metric tests
docs(task2a): document rolling-origin validation contract
```

Before commit:

```bash
git status
git diff
git diff --cached --name-only
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

Recommended safe test sequence:

```bash
pytest -q tests/test_task2a_history.py \
          tests/test_task2a_eda.py \
          tests/test_task2a_features.py \
          tests/test_task2a_multihorizon.py \
          tests/test_task2a_validation.py \
          tests/test_task2a_metrics.py

pytest -q
python -m pip check
```

Merge only after:

```text
LOCAL PHASE 14 VALIDATION PLAN: PASS
INDEPENDENT PHASE 14 REVIEW: PASS
```

---

# 24. Local execution contract

Recommended script:

```text
scripts/build_task2a_validation_plan.py
```

Recommended local command:

```bash
python scripts/build_task2a_validation_plan.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --multihorizon-table data/interim/task2a_multihorizon_train.csv \
  --feature-config configs/task2a_features.yaml \
  --validation-config configs/task2a_validation.yaml \
  --output-dir reports/private/phase14_task2a_validation
```

PowerShell one-line version:

```powershell
python scripts/build_task2a_validation_plan.py --weekly-panel data/interim/task2a_weekly_panel.csv --multihorizon-table data/interim/task2a_multihorizon_train.csv --feature-config configs/task2a_features.yaml --validation-config configs/task2a_validation.yaml --output-dir reports/private/phase14_task2a_validation
```

The local command should print only sanitized status.

Recommended successful output:

```text
LOCAL PHASE 14 VALIDATION PLAN: PASS
ROLLING ORIGINS: PASS
10-WEEK WINDOWS: PASS
REQUIRED SERIES COVERAGE: PASS
TRAINING TARGET AVAILABILITY: PASS
FUTURE-DEMAND MUTATION TEST: PASS
HORIZON-10 LEAKAGE TEST: PASS
METRIC CONTRACT: PASS
PER-SERIES EVALUATOR: PASS
OVERALL EVALUATOR: PASS
```

Do not print:

```text
private weekly target values
real per-series volume tables
row-level competition data
```

---

# 25. Suggested model for Codex VS Code

Phase 14 is validation-critical. A subtle date-split bug can invalidate every Task 2A score later.

Recommended:

```text
GPT-5.6 Sol — High reasoning
```

Lower-token fallback:

```text
GPT-5.6 Terra — High reasoning
```

Use the stronger option for DT-222–DT-224 if available. The metric/reporting tasks DT-225–DT-227 are comparatively straightforward.

---

# 26. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 14 only.

PHASE:
Task 2A Forecast Validation

TASK RANGE:
DT-222 through DT-227

EXECUTION MODE:
High-risk controlled autonomous implementation.

You have permission to perform all SAFE engineering work required for
Phase 14.

You MAY:

- create/edit/refactor Phase 14 tracked code
- create/edit configuration
- create/edit documentation
- create synthetic fixtures
- run targeted pytest tests
- run the complete safe regression suite
- inspect tracebacks
- diagnose ordinary implementation failures
- fix ordinary bugs automatically
- rerun failing tests
- run python -m pip check
- inspect git status/diff
- verify ignored paths
- self-review against the complete Phase 14 Definition of Done

Do NOT stop for ordinary coding/test failures that can safely be fixed.

STOP only for:

- official competition-rule ambiguity
- requirement to inspect restricted competition row-level data
- conflict with approved Phase 11–13 contracts
- unresolved weekly-history gap
- inability to create exact ten-week windows
- future-demand leakage that cannot be safely removed
- genuine schema/data-quality blocker
- a change requiring redesign outside Phase 14

DO NOT START PHASE 15.

==================================================
READ FIRST
==================================================

Read with targeted context:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase 14 and global Task 2A rules
4. PHASE_11_COMPETITION_CONTRACT.md
   - canonical weekly history semantics
5. PHASE_13_COMPETITION_CONTRACT.md
   - origin-relative features and direct multi-horizon table
6. PHASE_14_COMPETITION_CONTRACT.md
7. src/task2a/history.py
8. src/task2a/features.py
9. src/task2a/multihorizon.py
10. configs/task2a_history.yaml
11. configs/task2a_features.yaml
12. existing Task 2A tests

Use targeted reading.

Do not reread unrelated earlier contracts unless a direct dependency
requires it.

TASK 1 IS FROZEN.

Do not modify:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do NOT inspect or print real competition rows from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for agent-run implementation/testing.

The human operator will execute the real validation-plan build locally.

==================================================
OFFICIAL TASK 2A CONTEXT
==================================================

Official Task 2A predicts 10 future weeks of:

pred_total_volume_m3
pred_chilled_volume_m3

for supplied depot + brand + forecast-week combinations.

Phase 11 history rules remain frozen:

- use deliveries_train AND task1_test_inputs
- count every unique order once
- include attempted/deferred/not_run
- demand date = requested order_date
- week = official calendar iso_year + iso_week
- only Fresh has chilled demand
- Style chilled = 0
- Tech chilled = 0

The official booklet does not prescribe the exact internal rolling-origin
algorithm or local metric.

This Phase 14 contract freezes those WayLoom engineering choices BEFORE
models are compared.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2a/validation.py
src/task2a/metrics.py

scripts/build_task2a_validation_plan.py

configs/task2a_validation.yaml

docs/task2a_validation_spec.md

tests/test_task2a_validation.py
tests/test_task2a_metrics.py

Private runtime outputs belong under:

reports/private/phase14_task2a_validation/**

Ensure they remain ignored.

==================================================
DT-222 — ROLLING-ORIGIN VALIDATION
==================================================

Canonical validation origin:

week t = latest known historical demand week at forecast time.

Validation targets:

t+1 through t+10

Use the canonical Phase 13 direct multi-horizon table.

CRITICAL TRAINING RULE:

For validation origin t, a training row is eligible only if:

training_row.target_week_start_date <= t

Do NOT merely require:

training_row.origin_week_start_date < t

because an earlier-origin row can have a future target label that would
not yet be known at t.

Example:

validation origin = week 60
training candidate origin = week 55
candidate horizon = 10
candidate target = week 65

This candidate MUST be excluded.

Implement deterministic rolling-origin split generation.

Recommended default configuration:

strategy = rolling_origin
validation_horizon_weeks = 10
n_backtests = 4
step_weeks = 10
minimum_training_weeks = 52
require_full_horizon = true
require_same_origins_across_series = true

These numeric settings are WayLoom engineering defaults, not official
organizer requirements.

Origin selection MUST depend on date/coverage only, never target magnitude.

Recommended selection:

1. find every globally eligible origin
2. select latest eligible origin
3. move back at least step_weeks
4. select next eligible origin
5. repeat until n_backtests
6. report selected origins chronologically

Required assertions per split:

train nonempty
validation nonempty
max(train target week) <= validation origin
min(validation target week) > validation origin
train and validation rows disjoint

Required series should not be silently dropped.

==================================================
DT-223 — EXACT 10-WEEK WINDOWS
==================================================

For every accepted:

backtest_id + depot + brand

require exactly:

forecast_horizon = 1,2,3,4,5,6,7,8,9,10

exactly once each.

Assert:

row count = 10
no missing horizon
no duplicate horizon
no horizon 0
no horizon >10

target_week = origin + horizon weekly steps

Support:

cross-year windows
ISO week 53

If one required series lacks any horizon:

reject that origin globally under the default same-origin policy.

Do NOT shrink the evaluation horizon below 10.

==================================================
DT-224 — FUTURE-DEMAND LEAKAGE
==================================================

Implement a multi-layer leakage audit.

LAYER 1:
Every demand-derived predictor source week <= origin.

LAYER 2:
Every training label target week <= validation origin.

LAYER 3:
Validation predictors must not depend on actual t+1..t+10 demand.

LAYER 4:
Later model/preprocessor fitting must use training split only.

LAYER 5:
Actual validation result from h=1 must NEVER update h=2..10 predictors.

Required synthetic mutation tests:

A. Build X at origin t.
Change actual demand at t+1..t+10.
Rebuild X.
Assert X unchanged.

B. Build h=10 predictor at origin t.
Change actual demand at t+1.
Assert h=10 predictor unchanged.

C. Create an earlier-origin training row whose target is after t.
Assert excluded from training.

D. Change validation y only.
Assert validation X unchanged.

If any leakage test fails:

STOP.

==================================================
DT-225 — FREEZE FORECAST METRICS
==================================================

Freeze BEFORE Phase 15 model scores.

TOTAL VOLUME PRIMARY:

MAE

TOTAL SECONDARY:

RMSE
WAPE
mean_bias_m3
P90 absolute error

WAPE:

100 * sum(abs(y_true - y_pred)) / sum(y_true)

If sum(y_true) == 0:

WAPE = null/unavailable

Do NOT divide by arbitrary epsilon.

CHILLED PRIMARY POPULATION:

Fresh only

CHILLED PRIMARY:

MAE

CHILLED SECONDARY:

RMSE
WAPE
mean_bias_m3
P90 absolute error

Style/Tech chilled are structural official zeros.
Do not let those guaranteed zero rows dominate primary chilled score.

Do NOT use ordinary MAPE as primary because zero-demand weeks are valid.

Also record prediction diagnostics:

n
nonfinite_prediction_count
negative_prediction_count
chilled_gt_total_count

IMPORTANT:

Evaluate raw model predictions in Phase 14.

Do NOT silently implement Phase 17 corrections here.

Master-plan later tasks own:

negative clipping → DT-248
chilled <= total enforcement → DT-249

No rounding before metrics.

==================================================
DT-226 — PER-SERIES EVALUATION
==================================================

Canonical series:

depot + brand

For every:

backtest_id + depot + brand

TOTAL metrics:

n
MAE
RMSE
WAPE
mean_bias_m3
P90_absolute_error
negative_prediction_count

Expected n = 10.

For Fresh chilled:
compute same metrics.

For Style/Tech chilled:
report structural-zero status rather than using them as meaningful primary
chilled forecast series.

Across backtests for each series report:

backtest_count
mean_MAE
std_MAE
median_MAE
worst_backtest_MAE
mean_RMSE
mean_WAPE where defined
mean_bias_m3

==================================================
DT-227 — OVERALL EVALUATION
==================================================

TOTAL overall primary:

pool all total-volume validation rows across backtests/series/horizons
and calculate MAE.

Also report:

RMSE
WAPE
mean_bias_m3
P90 absolute error

Report both:

micro pooled metrics
macro equal-weight per-series metrics

Label them explicitly.

FRESH CHILLED overall:

pool Fresh validation rows only.

Calculate:

MAE
RMSE
WAPE
bias
P90 AE

Also summarize metrics by:

backtest
forecast_horizon 1..10

Do NOT silently drop bad backtests.

For future Phase 15/16 selection:

Total primary = overall pooled MAE
Fresh chilled primary = Fresh-only overall pooled MAE

Secondary metrics and stability are tie-break/diagnostic context.

Do NOT invent an undocumented combined total+chilled score.

==================================================
CONFIG
==================================================

Create configs/task2a_validation.yaml containing at least:

series key
origin column
target-week column
horizon column
rolling-origin settings
10-week horizon requirement
backtest count
step size
minimum training history
same-origin policy
training target-availability rule
metric contract
WAPE zero-denominator policy
raw prediction diagnostic policy
per-series policy
horizon diagnostic policy
private output directory

The config must be deterministic and versioned.

==================================================
IMPLEMENTATION API
==================================================

Recommended src/task2a/validation.py API:

ForecastBacktestSplit dataclass
validate_phase13_multihorizon_table()
resolve_required_series()
find_eligible_forecast_origins()
select_rolling_origins()
make_forecast_backtest_split()
build_rolling_origin_plan()
validate_ten_week_window()
audit_future_demand_leakage()

Recommended src/task2a/metrics.py API:

forecast_regression_metrics()
forecast_prediction_diagnostics()
evaluate_forecast_per_series()
evaluate_forecast_by_horizon()
evaluate_forecast_overall()
summarize_backtest_stability()

Keep metrics pure and model-agnostic.

==================================================
SYNTHETIC TESTS
==================================================

Use synthetic data only.

DT-222:

- deterministic rolling origins
- no random split
- target values cannot affect origins
- expanding information over time
- training target date <= origin
- early-origin future-target row rejected
- insufficient history handled
- required series cannot silently disappear

DT-223:

- exact horizons 1..10
- exactly 10 rows per series/backtest
- missing horizon fails
- duplicate horizon fails
- h=0 fails
- h=11 fails
- target date alignment
- cross-year
- ISO week 53

DT-224:

- future-demand mutation invariant
- h=10 does not use h=1 actual demand
- future training label excluded
- validation-y mutation invariant
- future source lineage rejected
- validation outcome cannot update later horizon

DT-225:

- perfect metrics
- known MAE
- known RMSE
- known WAPE
- zero-denominator WAPE
- bias positive/negative
- P90 AE
- negative prediction counted but not clipped
- NaN/Inf rejection
- length mismatch

DT-226:

- series isolation
- depot isolation
- brand isolation
- 10-point support
- Fresh chilled evaluation
- Style/Tech structural zero
- per-series stability

DT-227:

- micro overall
- macro series average
- micro != macro where expected
- all backtests retained
- best/worst backtest
- horizon summaries 1..10
- Fresh-only chilled overall
- deterministic schema/order

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After DT-222:
run targeted split tests and fix normal bugs.

After DT-223:
run ten-week coverage tests.

After DT-224:
run ALL leakage tests.
Do not continue if leakage remains.

After DT-225–227:
run metric/evaluator tests.

Then run:

pytest -q tests/test_task2a_history.py tests/test_task2a_eda.py tests/test_task2a_features.py tests/test_task2a_multihorizon.py tests/test_task2a_validation.py tests/test_task2a_metrics.py

Then:

pytest -q

Then:

python -m pip check

Then inspect:

git status
git diff

If a documented test requires private real competition data:

do NOT run it in Codex.
Report the local human command.

Ensure none of these are staged:

data/raw/**
data/interim/**
reports/private/**

==================================================
LOCAL REAL-DATA COMMAND
==================================================

Implement but DO NOT execute against restricted private competition data
inside the external-agent context:

python scripts/build_task2a_validation_plan.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --multihorizon-table data/interim/task2a_multihorizon_train.csv \
  --feature-config configs/task2a_features.yaml \
  --validation-config configs/task2a_validation.yaml \
  --output-dir reports/private/phase14_task2a_validation

Console output must be sanitized.

Do not print private demand values.

==================================================
STOP CONDITIONS
==================================================

STOP if:

- Phase 11/13 canonical data is bypassed
- unresolved weekly gaps exist
- rolling origins use target values
- accepted origin lacks h=1..10
- required series silently use different periods
- training target occurs after validation origin
- validation X depends on future actual demand
- h=10 uses actual intermediate future demand
- validation labels affect feature generation
- metric contract is changed after model results
- prediction metrics silently clip/cap forecasts
- failed backtests are dropped
- Style/Tech chilled-zero semantics are lost
- private data must be exposed
- tests cannot pass without violating prior contracts

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-222 READY
DT-223 READY
DT-224 READY
DT-225 READY
DT-226 READY
DT-227 READY

rolling origin deterministic
10-week window exact
training labels known by origin
future-demand mutation passes
cross-horizon leakage impossible
metric contract frozen
MAE total primary
MAE Fresh chilled primary
WAPE zero denominator explicit
negative predictions diagnostic only
per-series evaluator complete
overall evaluator complete
horizon diagnostics complete
all backtests retained
synthetic tests pass
full safe tests pass
pip check passes
Task 1 frozen artifacts unchanged
private outputs ignored
no Phase 15 implementation added

==================================================
RETURN ONLY
==================================================

PHASE:
14 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-222 READY / FAIL
DT-223 READY / FAIL
DT-224 READY / FAIL
DT-225 READY / FAIL
DT-226 READY / FAIL
DT-227 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

ROLLING-ORIGIN PLAN:
PASS / FAIL

EXACT 10-WEEK WINDOWS:
PASS / FAIL

TRAINING TARGET AVAILABILITY:
PASS / FAIL

FUTURE-DEMAND MUTATION TEST:
PASS / FAIL

HORIZON-10 INTERMEDIATE-DEMAND LEAKAGE:
PASS / FAIL

METRIC CONTRACT:
PASS / FAIL

PER-SERIES EVALUATOR:
PASS / FAIL

OVERALL EVALUATOR:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 14 validation-plan command.

PHASE 14 STATUS:
AWAITING LOCAL VALIDATION PLAN

READY FOR PHASE 15:
NO

Then STOP.

Do not start Phase 15.
```

---

# 27. Independent Phase 14 review prompt

Use a **fresh Codex session** after the local Phase 14 validation-plan build.

```text
Perform an independent review of completed WayLoom Datathon Phase 14.

PHASE:
Task 2A Forecast Validation

TASK RANGE:
DT-222 through DT-227

This is REVIEW ONLY.

DO NOT:

- modify code initially
- access private competition rows
- inspect private demand values
- run real-data backtesting
- start Phase 15

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 14 only
4. PHASE_13_COMPETITION_CONTRACT.md — feature/leakage semantics
5. PHASE_14_COMPETITION_CONTRACT.md
6. src/task2a/validation.py
7. src/task2a/metrics.py
8. scripts/build_task2a_validation_plan.py
9. configs/task2a_validation.yaml
10. docs/task2a_validation_spec.md
11. tests/test_task2a_validation.py
12. tests/test_task2a_metrics.py
13. relevant Phase 13 feature registry/tests
14. .gitignore
15. AGENTS.md / relevant ignore configuration

HUMAN LOCAL RESULT:

LOCAL PHASE 14 VALIDATION PLAN: <PASS / FAIL>
ROLLING ORIGINS: <PASS / FAIL>
10-WEEK WINDOWS: <PASS / FAIL>
REQUIRED SERIES COVERAGE: <PASS / FAIL>
TRAINING TARGET AVAILABILITY: <PASS / FAIL>
FUTURE-DEMAND MUTATION TEST: <PASS / FAIL>
HORIZON-10 LEAKAGE TEST: <PASS / FAIL>
METRIC CONTRACT: <PASS / FAIL>
PER-SERIES EVALUATOR: <PASS / FAIL>
OVERALL EVALUATOR: <PASS / FAIL>

Do not ask for private metric values.

==================================================
AUDIT DT-222
==================================================

Verify:

- rolling-origin strategy implemented
- origins selected from chronology/coverage only
- no random split
- exact configuration versioned
- required series not silently dropped
- training eligibility checks target_week <= validation origin
- earlier-origin/future-target training rows are excluded
- deterministic IDs/order

==================================================
AUDIT DT-223
==================================================

Verify every accepted backtest requires:

horizon exactly 1..10
10 rows per series
consecutive weekly target dates
cross-year safety
ISO week 53 safety

No shrinking to shorter horizon.

==================================================
AUDIT DT-224
==================================================

Verify:

- demand-derived feature source week <= origin
- training labels known by origin
- future-target mutation test exists
- h=10 intermediate-demand isolation test exists
- validation y cannot influence X
- actual validation h=1 cannot update later-horizon predictors
- Phase 13 leakage contract reused

Any failure here is BLOCKING.

==================================================
AUDIT DT-225
==================================================

Verify frozen metric contract:

Total primary:
MAE

Fresh chilled primary:
MAE

Secondary:
RMSE
WAPE
bias
P90 AE

Verify:

- WAPE zero denominator returns unavailable/null
- no arbitrary epsilon MAPE
- no pre-score rounding
- negative predictions counted, not clipped
- chilled>total counted, not corrected here
- Phase 17 clipping/capping not moved into Phase 14

==================================================
AUDIT DT-226
==================================================

Verify canonical series key:

depot + brand

Verify:

- total metrics per series
- Fresh chilled per-series metrics
- Style/Tech chilled handled as structural zeros
- exact support counts
- all backtests represented

==================================================
AUDIT DT-227
==================================================

Verify:

- pooled/micro total metrics
- macro series metrics distinctly labelled
- Fresh-only chilled overall metrics
- backtest stability
- horizon 1..10 diagnostics
- failed backtests cannot be silently discarded
- total and chilled are not combined into undocumented score

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q tests/test_task2a_history.py tests/test_task2a_eda.py tests/test_task2a_features.py tests/test_task2a_multihorizon.py tests/test_task2a_validation.py tests/test_task2a_metrics.py

Then if safe:

pytest -q

Then:

python -m pip check

git status

git diff

Do NOT run the private real-data command.

==================================================
RETURN
==================================================

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then report:

ROLLING-ORIGIN DESIGN:
PASS / FAIL

TEN-WEEK WINDOW CONTRACT:
PASS / FAIL

TRAINING-LABEL AVAILABILITY:
PASS / FAIL

FUTURE-DEMAND LEAKAGE PROTECTION:
PASS / FAIL

CROSS-HORIZON LEAKAGE PROTECTION:
PASS / FAIL

FORECAST METRIC CONTRACT:
PASS / FAIL

PER-SERIES EVALUATION:
PASS / FAIL

OVERALL EVALUATION:
PASS / FAIL

SYNTHETIC TESTS:
PASS / FAIL

HUMAN LOCAL VALIDATION PLAN:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS:
UNCHANGED / CHANGED

DT-222: PASS / FAIL
DT-223: PASS / FAIL
DT-224: PASS / FAIL
DT-225: PASS / FAIL
DT-226: PASS / FAIL
DT-227: PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

PHASE 14 REVIEW:
PASS / FAIL

READY FOR PHASE 15:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not start Phase 15.
```

---

# 28. Human completion record

```markdown
# Phase 14 Completion Record

## Task status

- [ ] DT-222 Rolling-origin validation
- [ ] DT-223 Exact 10-week windows
- [ ] DT-224 Future-demand leakage prevention
- [ ] DT-225 Forecast metric contract
- [ ] DT-226 Per-series evaluation
- [ ] DT-227 Overall evaluation

## Agent stage

- Rolling-origin implementation: PASS / FAIL
- Ten-week coverage tests: PASS / FAIL
- Leakage tests: PASS / FAIL
- Metric tests: PASS / FAIL
- Full safe suite: PASS / FAIL
- pip check: PASS / FAIL

## Local stage

- Local validation-plan build: PASS / FAIL
- Rolling origins: PASS / FAIL
- Full 10-week windows: PASS / FAIL
- Required series coverage: PASS / FAIL
- Training target availability: PASS / FAIL
- Future-demand mutation: PASS / FAIL
- Horizon-10 leakage: PASS / FAIL
- Metric contract: PASS / FAIL
- Per-series evaluator: PASS / FAIL
- Overall evaluator: PASS / FAIL

## Safety

- Raw/private rows exposed to AI: NO
- Future actual demand used in features: NO
- Future target labels used in training: NO
- Task 1 artifacts modified: NO
- Phase 15 started early: NO

## Independent review

- Phase 14 review: PASS / FAIL

## Verdict

PHASE 14 STATUS: PASS / FAIL
READY FOR PHASE 15: YES / NO
```

---

# 29. Final Phase 14 checklist

Before Phase 15 begins:

- [ ] Phase 11 passed.
- [ ] Phase 12 passed.
- [ ] Phase 13 passed.
- [ ] DT-222 through DT-227 all pass.
- [ ] rolling-origin strategy is deterministic.
- [ ] origins were chosen from coverage, not target values.
- [ ] exact 10-week historical validation blocks exist.
- [ ] all required series use the frozen origins.
- [ ] training labels are available by forecast origin.
- [ ] future-demand feature mutation cannot change validation X.
- [ ] h=10 cannot see actual h=1..9 demand.
- [ ] MAE is frozen as total primary metric.
- [ ] MAE is frozen as Fresh chilled primary metric.
- [ ] RMSE/WAPE/bias/P90 AE are secondary.
- [ ] WAPE zero denominator is explicit.
- [ ] raw prediction invalidity diagnostics exist.
- [ ] Phase 17 clipping/capping is not silently applied here.
- [ ] per-series evaluator exists.
- [ ] overall micro evaluator exists.
- [ ] macro per-series evaluator exists.
- [ ] horizon diagnostics exist.
- [ ] failed backtests cannot disappear.
- [ ] all tests pass.
- [ ] local validation-plan command passes.
- [ ] private outputs remain ignored.
- [ ] Task 1 remains unchanged.
- [ ] independent review passes.

Only then:

```text
PHASE 14 STATUS: PASS
READY FOR PHASE 15: YES
```

Do not automatically begin Phase 15.
