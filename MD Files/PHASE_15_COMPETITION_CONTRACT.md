# PHASE 15 — Task 2A Baseline Models

> **Canonical filename:** `PHASE_15_COMPETITION_CONTRACT.md`  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-228 → DT-233**  
> **Task count:** 6  
> **Default phase priority:** P1  
> **Phase dependency:** Phase 14 must have passed  
> **Phase gate:** **Seasonal/simple forecasting baselines exist for total and chilled demand, are evaluated on the exact frozen Phase 14 rolling-origin backtests, and are stored as the reference that Phase 16 advanced models must beat or justify themselves against.**

---

# 1. Purpose of Phase 15

Phase 15 establishes the simple, transparent Task 2A forecasting baselines that all advanced forecasting work must be compared against.

The phase answers six questions:

1. How strong is a naive persistence forecast using the most recently known week?
2. How strong is a recent trailing-average forecast?
3. How strong is a same-week-last-year seasonal forecast?
4. Does a fixed blend of recent and seasonal demand improve robustness?
5. What is the correct baseline treatment for chilled demand, including the official Style/Tech zero rule?
6. Which baseline is the strongest reference across the frozen Phase 14 rolling backtests?

Phase 15 is intentionally simple. A complex model that cannot materially justify itself against these baselines should not automatically become the Task 2A final approach.

This phase must **not**:

- change the Phase 11 demand history;
- change Phase 13 lag/rolling semantics;
- change Phase 14 rolling-origin splits or metrics;
- train CatBoost, LightGBM, XGBoost, neural networks, AutoML, or any other Phase 16 advanced model;
- tune baseline formulas after inspecting real backtest scores;
- use future actual demand when generating a baseline prediction;
- use target-week actual demand as a feature;
- clip negative forecasts as a post-hoc scoring trick;
- force Fresh chilled forecasts to be less than total during baseline evaluation;
- start final Task 2A inference.

---

# 2. Finalized master-inventory contract

The finalized WayLoom master task inventory defines Phase 15 exactly as follows.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-228** | [E] | P1 | DT-222–DT-227 | Last-week baseline |
| [ ] | **DT-229** | [E] | P1 | Phase 14 | Recent rolling-mean baseline |
| [ ] | **DT-230** | [E] | P1 | Phase 14 | Same-week-last-year baseline |
| [ ] | **DT-231** | [E] | P1 | Phase 14 | Seasonal/recent weighted baseline |
| [ ] | **DT-232** | [E] | P1 | Phase 14 | Build separate chilled-demand baseline |
| [ ] | **DT-233** | [E] | P1 | Phase 14 | Compare baseline results across backtests |

**Phase complete:** [ ]  
**READY FOR PHASE 16:** NO

---

# 3. Official Task 2A requirements that constrain Phase 15

The official Challenge Booklet asks WayLoom to forecast the volume ordered for each supplied depot, brand, and forecast week over **10 future weeks**.

Required predictions are:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

The official Task 2A history rules already implemented in Phase 11 remain binding:

```text
history source 1 = deliveries_train.csv
history source 2 = task1_test_inputs.csv
```

Each unique order is counted once, including:

```text
attempted
deferred
not_run
```

Demand belongs to the requested:

```text
order_date
```

Weekly grouping uses official:

```text
calendar.iso_year
calendar.iso_week
```

Only Fresh has chilled demand.

Therefore the official output rule is:

```text
Style chilled = 0
Tech chilled  = 0
```

The organizer does **not** prescribe these baseline formulas, their blending weights, or the team's internal model-selection rule. Those are WayLoom engineering decisions in this contract and must be frozen **before** looking at private Phase 15 scores.

---

# 4. Source hierarchy

Use this order of authority:

1. official Challenge Booklet and supplied competition files;
2. finalized `WAYLOOM_DATATHON_MASTER_PLAN.md`;
3. approved Phase 11 Task 2A history contract;
4. approved Phase 12 Task 2A EDA contract;
5. approved Phase 13 forecasting-feature contract;
6. approved Phase 14 forecast-validation contract;
7. this Phase 15 implementation contract;
8. explicitly documented engineering assumptions.

If a lower source conflicts with a higher source:

```text
STOP
```

Do not silently reinterpret the competition rule.

---

# 5. Frozen upstream contracts

Phase 15 assumes all of the following are already passing.

## 5.1 Phase 11 — canonical weekly history

Canonical weekly panel grain:

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

and no unresolved weekly-gap ambiguity.

## 5.2 Phase 13 — forecasting feature semantics

For a forecast origin `t`, all demand-derived predictors are based on demand from `t` or earlier.

## 5.3 Phase 14 — validation contract

Phase 15 must reuse the exact frozen Phase 14 rolling-origin plan.

For validation origin `t`:

```text
validation horizons = t+1 ... t+10
```

and every eligible training label must have been knowable by the origin.

Phase 14 metrics are frozen.

### Total-volume primary metric

```text
MAE
```

### Fresh chilled primary metric

```text
MAE
```

### Secondary metrics

```text
RMSE
WAPE
mean_bias_m3
P90 absolute error
```

Phase 15 must not define a new scoring system.

---

# 6. Baseline information boundary

Every baseline prediction must be generated **as if the model were standing at the historical forecast origin**.

For a backtest origin:

```text
t
```

allowed historical demand is:

```text
week <= t
```

not allowed:

```text
week > t
```

The safest implementation pattern is:

```python
history_at_origin = weekly_panel[
    weekly_panel["week_start_date"] <= origin_week_start_date
].copy()
```

Then every baseline is fitted/looked up from `history_at_origin` only.

Never pass the complete weekly panel into a baseline and rely on the baseline to "remember" not to look ahead unless that behavior is explicitly tested.

---

# 7. Canonical baseline definitions

The formulas below are WayLoom engineering definitions for Phase 15. They are intentionally simple and fixed before private results are inspected.

## 7.1 Baseline A — last week / persistence

For series `s` at origin `t`:

```text
forecast(s, t, h) = y(s, t)
```

for every:

```text
h = 1..10
```

This produces a flat ten-week persistence forecast.

## 7.2 Baseline B — recent rolling mean

Frozen default window:

```text
4 weeks
```

For series `s` at origin `t`:

```text
recent_mean_4 = mean(y[t-3], y[t-2], y[t-1], y[t])
```

Then:

```text
forecast(s, t, h) = recent_mean_4
```

for all horizons 1..10.

No centered or future-looking window is allowed.

## 7.3 Baseline C — same week last year

For target week:

```text
(target_iso_year, target_iso_week)
```

look up the same series at:

```text
(target_iso_year - 1, target_iso_week)
```

provided that source week:

- exists in the canonical historical panel; and
- occurs on or before the forecast origin.

If the exact prior-year ISO week does not exist, use the frozen fallback policy in Section 12.

Do **not** define "same week last year" as simply `shift(52)` because ISO week 53 can break the semantic meaning.

## 7.4 Baseline D — seasonal/recent weighted blend

Frozen default blend:

```text
0.50 × recent_mean_4
+
0.50 × same_week_last_year
```

The weights are not tuned in Phase 15.

If the seasonal component is unavailable, apply the frozen fallback hierarchy rather than changing the weight after seeing results.

---

# 8. Total versus chilled forecasting

Phase 15 treats total and chilled demand as separate forecasting targets.

## Total demand

Evaluate all official depot + brand series.

## Chilled demand

Only Fresh has chilled demand.

Therefore:

```text
Fresh → forecast chilled demand
Style → exactly 0.0
Tech  → exactly 0.0
```

For Fresh, run the same transparent baseline families on:

```text
chilled_volume_m3
```

so Phase 16 has a meaningful chilled benchmark.

For Style/Tech, do not fit a chilled forecasting rule. Their official baseline is structural zero.

Primary chilled model comparison uses **Fresh-only Phase 14 chilled metrics**.

---

# 9. Required repository additions

Create/update:

```text
src/task2a/
├── baselines.py
└── baseline_evaluation.py

scripts/
└── run_task2a_baselines.py

configs/
└── task2a_baselines.yaml

docs/
└── task2a_baseline_spec.md

tests/
├── test_task2a_baselines.py
└── test_task2a_baseline_evaluation.py
```

Reuse rather than duplicate:

```text
src/task2a/history.py
src/task2a/validation.py
src/task2a/metrics.py
configs/task2a_history.yaml
configs/task2a_validation.yaml
```

Private runtime outputs:

```text
reports/private/phase15_task2a_baselines/
```

must remain ignored.

---

# 10. Recommended private output package

```text
reports/private/phase15_task2a_baselines/
├── run_manifest.json
├── backtest_predictions.csv
├── backtest_metrics.csv
├── series_metrics.csv
├── horizon_metrics.csv
├── baseline_summary.csv
├── baseline_reference.json
├── warnings.json
└── phase15_baseline_report.md
```

Optional figures may live under:

```text
reports/private/phase15_task2a_baselines/figures/
```

Do not commit these files.

---

# 11. Recommended `task2a_baselines.yaml`

```yaml
version: 1

series_keys:
  - depot
  - brand

week:
  date_column: week_start_date
  iso_year_column: iso_year
  iso_week_column: iso_week

validation:
  reuse_phase14_plan: true
  require_exact_10_week_windows: true

baseline_families:
  last_week:
    enabled: true

  recent_mean:
    enabled: true
    window_weeks: 4
    minimum_history_weeks: 4

  same_week_last_year:
    enabled: true
    lookup: exact_prior_iso_year_same_iso_week
    unavailable_fallback: recent_mean

  seasonal_recent_weighted:
    enabled: true
    recent_weight: 0.50
    seasonal_weight: 0.50
    seasonal_unavailable_fallback: recent_mean

total_target:
  column: total_volume_m3

chilled_target:
  column: chilled_volume_m3
  fresh_brand: Fresh
  structural_zero_brands:
    - Style
    - Tech

postprocessing:
  clip_negative: false
  enforce_chilled_le_total: false

selection:
  total_primary_metric: mae
  chilled_primary_metric: mae
  tie_break_order:
    - rmse
    - p90_absolute_error
    - backtest_mae_std
    - simplicity

privacy:
  output_dir: reports/private/phase15_task2a_baselines
```

The numeric choices above are WayLoom engineering choices, not official competition rules.

Do not change them after observing private Phase 15 scores.

---

# 12. Frozen missing-history and fallback policy

Simple baselines need deterministic behavior when historical information is unavailable.

## 12.1 Last-week

Required source:

```text
y[t]
```

If it is unavailable for a required series/origin:

```text
FAIL
```

Phase 14 should already guarantee sufficient history and series coverage.

## 12.2 Recent mean

Require a complete trailing four-week window:

```text
t-3 .. t
```

If fewer than four weekly observations are available:

```text
BASELINE_UNAVAILABLE
```

Do not backfill from the future.

## 12.3 Same-week-last-year

Primary lookup:

```text
same series
iso_year = target_iso_year - 1
iso_week = target_iso_week
```

If unavailable or if the matched source week would be after origin:

```text
fallback = recent_mean_4
```

Record:

```text
seasonal_exact_used
seasonal_fallback_used
```

for diagnostics.

The fallback must be frozen before scores are examined.

## 12.4 Weighted seasonal/recent

If both components exist:

```text
0.5 recent + 0.5 seasonal
```

If seasonal is unavailable:

```text
forecast = recent_mean_4
```

If recent mean is unavailable:

```text
BASELINE_UNAVAILABLE
```

Do not choose a different fallback because it scores better on one backtest.

---

# 13. Common baseline API

Recommended `src/task2a/baselines.py` API:

```python
@dataclass(frozen=True)
class ForecastRequest:
    depot: str
    brand: str
    origin_week_start_date: pd.Timestamp
    target_week_start_date: pd.Timestamp
    target_iso_year: int
    target_iso_week: int
    forecast_horizon: int


def build_history_as_of_origin(...):
    ...


def predict_last_week(...):
    ...


def predict_recent_mean(...):
    ...


def predict_same_week_last_year(...):
    ...


def predict_seasonal_recent_weighted(...):
    ...


def generate_total_baseline_predictions(...):
    ...


def generate_chilled_baseline_predictions(...):
    ...
```

Recommended output columns:

```text
backtest_id
depot
brand
origin_week_start_date
target_week_start_date
forecast_horizon
baseline_name
target_name
y_true
y_pred
fallback_status
```

`y_true` is used only because historical backtesting has labels. It must never enter the prediction calculation.

---

# 14. DT-228 — Last-week baseline

**Mark:** [E]  
**Priority:** P1  
**Dependency:** DT-222–DT-227

## Objective

Implement the simplest persistence baseline for total demand.

For each Phase 14 backtest origin and each official depot + brand series:

```text
prediction = total_volume_m3 at origin week t
```

for all horizons:

```text
1..10
```

## Inputs

```text
canonical Phase 11 weekly panel
frozen Phase 14 rolling-origin plan
```

## Required behavior

For one series/origin:

```text
h1 prediction = y[t]
h2 prediction = y[t]
...
h10 prediction = y[t]
```

The ten predictions are identical unless the series itself changes, which it cannot within one origin.

## Leakage rule

The prediction must not reference:

```text
y[t+1]
...
y[t+10]
```

## Tests

Synthetic sequence:

```text
10, 20, 30, 40, 50
```

At origin with value `50`, every future horizon predicts:

```text
50
```

Changing all future actual values must not alter predictions.

Test:

- correct last value;
- all ten horizons identical;
- series isolation;
- origin isolation;
- no future mutation effect;
- missing origin value fails.

## Definition of Done

- [ ] last-week baseline exists;
- [ ] it uses origin-week demand only;
- [ ] it generates exactly ten predictions per series/backtest;
- [ ] it uses the Phase 14 plan exactly;
- [ ] leakage tests pass.

## STOP conditions

Stop if the code uses the validation target to determine the persistence value.

---

# 15. DT-229 — Recent rolling-mean baseline

**Mark:** [E]  
**Priority:** P1

## Objective

Implement a simple short-term smoothing baseline.

Frozen window:

```text
4 historical weeks ending at origin
```

Formula:

```text
recent_mean_4 = mean(y[t-3], y[t-2], y[t-1], y[t])
```

Then:

```text
forecast(h=1..10) = recent_mean_4
```

## Why four weeks

Phase 12 already analyzed recent four-, eight-, and thirteen-week windows. Phase 15 freezes a single simple rolling-mean baseline rather than tuning window size against the private backtests.

This is an engineering choice, not an organizer rule.

## Required behavior

- trailing only;
- no centered window;
- full four-week history required;
- confirmed zero-demand weeks remain valid zeros in the mean;
- each series computed independently;
- same prediction for all horizons from the same origin.

## Example

History through origin:

```text
[8, 12, 10, 14]
```

Prediction:

```text
11
```

for h=1..10.

## Tests

- exact mean;
- zero included correctly;
- no future demand included;
- separate depot/brand series;
- fewer than four observations becomes unavailable;
- future-demand mutation does not alter output;
- deterministic output.

## Definition of Done

- [ ] four-week baseline implemented;
- [ ] window ends at origin;
- [ ] window size is config-frozen;
- [ ] full-history requirement tested;
- [ ] no future leakage.

---

# 16. DT-230 — Same-week-last-year baseline

**Mark:** [E]  
**Priority:** P1

## Objective

Implement an interpretable seasonal baseline using the corresponding ISO week in the previous ISO year.

For a target row:

```text
target_iso_year = Y
target_iso_week = W
```

primary lookup is:

```text
series = same depot + brand
iso_year = Y - 1
iso_week = W
```

## Why use ISO keys

The official Task 2A contract uses:

```text
calendar.iso_year
calendar.iso_week
```

Therefore seasonal lookup should use the same supplied calendar semantics.

Do not substitute normal calendar year.

## Critical week-53 behavior

Some ISO years contain week 53 and others do not.

If:

```text
(Y-1, 53)
```

does not exist, do **not** invent it.

Use the frozen fallback:

```text
recent_mean_4
```

and record a fallback flag.

## Origin-availability guard

Even if a seasonal row exists, assert:

```text
seasonal_source_week_start_date <= origin_week_start_date
```

If not:

```text
reject seasonal source
→ use frozen fallback
```

## Tests

- exact same-week prior-year lookup;
- different series isolation;
- calendar-year / ISO-year boundary;
- week 53 exact match when available;
- week 53 missing fallback;
- source-after-origin rejected;
- target value never read by predictor;
- future mutation does not change prediction.

## Definition of Done

- [ ] lookup uses exact official ISO-year/week semantics;
- [ ] week 53 handled explicitly;
- [ ] source availability checked against origin;
- [ ] fallback is deterministic;
- [ ] fallback usage recorded.

---

# 17. DT-231 — Seasonal/recent weighted baseline

**Mark:** [E]  
**Priority:** P1

## Objective

Create one transparent blended baseline that balances current demand level and annual seasonality.

Frozen formula:

```text
prediction =
0.50 * recent_mean_4
+
0.50 * same_week_last_year
```

when both are available.

## Critical anti-tuning rule

Do not try:

```text
0.2/0.8
0.3/0.7
0.4/0.6
...
```

and select the best after seeing real validation scores.

That would turn a simple baseline into tuning and weaken the benchmark's interpretability.

Phase 16 is where more advanced model comparison belongs.

## Fallback

If seasonal component is unavailable:

```text
prediction = recent_mean_4
```

If recent mean is unavailable:

```text
BASELINE_UNAVAILABLE
```

## Nonnegativity

Because canonical historical demand is nonnegative and weights are nonnegative summing to one, valid component predictions should naturally be nonnegative.

Do not add a general clipping step in Phase 15.

## Tests

- exact 50/50 blend;
- weights sum to 1;
- seasonal missing fallback;
- recent missing unavailable;
- no future demand;
- deterministic output;
- config weight mutation test if invalid sum;
- no negative-weight config.

## Definition of Done

- [ ] blend formula exact;
- [ ] weights config-frozen;
- [ ] no data-driven weight search;
- [ ] fallback deterministic;
- [ ] leakage-safe.

---

# 18. DT-232 — Separate chilled-demand baseline

**Mark:** [E]  
**Priority:** P1

## Objective

Establish a legitimate chilled-demand benchmark separate from total demand.

## Official brand rule

```text
Fresh → chilled forecasting required
Style → chilled exactly 0
Tech  → chilled exactly 0
```

## Fresh chilled baseline candidates

Apply the same frozen families to Fresh historical:

```text
chilled_volume_m3
```

Candidate names:

```text
chilled_last_week
chilled_recent_mean_4
chilled_same_week_last_year
chilled_seasonal_recent_weighted
```

This gives Phase 16 a strong but interpretable chilled benchmark.

## Style/Tech

Do not fit any chilled baseline.

Generate:

```text
y_pred = 0.0
```

exactly.

## Evaluation rule

Primary chilled baseline ranking uses only:

```text
Fresh rows
```

with the frozen Phase 14 Fresh chilled metrics.

Style/Tech structural zero rows are still validated separately for exact compliance.

## Chilled <= total

Do **not** force:

```text
pred_chilled <= pred_total
```

inside Phase 15 scoring.

If an independently generated Fresh chilled baseline exceeds its corresponding total baseline, record:

```text
chilled_gt_total_count
```

as a diagnostic.

Final output enforcement belongs to Phase 17 (`DT-249`).

## Tests

- Fresh chilled last-week;
- Fresh chilled recent mean;
- Fresh seasonal lookup;
- Fresh weighted blend;
- Style exact zero;
- Tech exact zero;
- Fresh target is not replaced by total volume;
- chilled candidates use chilled history only;
- future chilled demand cannot affect origin prediction;
- Fresh chilled > total is diagnosed, not silently capped.

## Definition of Done

- [ ] Fresh chilled benchmark families implemented;
- [ ] Style chilled exact zero;
- [ ] Tech chilled exact zero;
- [ ] Fresh-only primary evaluation supported;
- [ ] no hidden chilled-to-total clipping.

---

# 19. DT-233 — Compare baseline results across backtests

**Mark:** [E]  
**Priority:** P1

## Objective

Evaluate every frozen baseline on the exact Phase 14 backtests and produce a stable reference benchmark for Phase 16.

## Required candidate set — total

```text
total_last_week
total_recent_mean_4
total_same_week_last_year
total_seasonal_recent_weighted
```

## Required candidate set — Fresh chilled

```text
chilled_last_week
chilled_recent_mean_4
chilled_same_week_last_year
chilled_seasonal_recent_weighted
```

## Required evaluation reuse

Use Phase 14 functions directly where possible:

```text
evaluate_forecast_per_series()
evaluate_forecast_by_horizon()
evaluate_forecast_overall()
summarize_backtest_stability()
```

Do not rewrite MAE/RMSE/WAPE differently in Phase 15.

## Required comparison levels

For each baseline report:

### Overall

```text
pooled MAE
RMSE
WAPE
mean bias
P90 absolute error
```

### Backtest stability

```text
backtest count
mean backtest MAE
std backtest MAE
median backtest MAE
worst backtest MAE
```

### Per series

```text
depot + brand metrics
```

### Per horizon

```text
horizon 1..10 metrics
```

## Reference-baseline ranking rule

Freeze one reference baseline for total and one for Fresh chilled.

### Primary

```text
lowest Phase 14 overall pooled MAE
```

### Tie-break order

1. lower overall RMSE;
2. lower P90 absolute error;
3. lower backtest MAE standard deviation;
4. simpler baseline.

Suggested simplicity ordering:

```text
last_week
recent_mean_4
same_week_last_year
seasonal_recent_weighted
```

A tiny score difference does not automatically justify a more complicated baseline. Record the exact ranking logic in code/config.

## Important naming

The selected baseline is:

```text
REFERENCE BASELINE
```

not:

```text
FINAL TASK 2A MODEL
```

Phase 16 must still compare advanced approaches against it.

## Required outputs

`baseline_summary.csv` should contain at least:

```text
target_name
baseline_name
eligible_backtest_count
overall_mae
overall_rmse
overall_wape
overall_bias_m3
p90_absolute_error
mean_backtest_mae
std_backtest_mae
worst_backtest_mae
unavailable_prediction_count
seasonal_fallback_count
negative_prediction_count
chilled_gt_total_count
rank
```

`baseline_reference.json` should contain safely:

```text
phase
validation_contract_version
best_total_baseline
best_chilled_baseline
selection_primary_metric
selection_tie_breaks
baseline_config_hash
```

Do not store private weekly predictions in tracked configuration.

## Definition of Done

- [ ] every required baseline evaluated on every eligible frozen backtest;
- [ ] no failed backtest silently dropped;
- [ ] Phase 14 metrics reused;
- [ ] series/horizon diagnostics produced;
- [ ] total reference baseline frozen;
- [ ] Fresh chilled reference baseline frozen;
- [ ] selection is development/backtest-based only;
- [ ] no final advanced model selected.

---

# 20. Baseline evaluation architecture

Recommended `src/task2a/baseline_evaluation.py` API:

```python
def validate_baseline_inputs(...):
    ...


def generate_backtest_baseline_predictions(...):
    ...


def evaluate_baseline_predictions(...):
    ...


def compare_total_baselines(...):
    ...


def compare_chilled_baselines(...):
    ...


def rank_reference_baselines(...):
    ...


def build_baseline_run_manifest(...):
    ...
```

Keep prediction generation separate from metric calculation.

This makes it possible to prove that changing `y_true` after predictions are generated cannot alter the prediction values.

---

# 21. Phase 14 validation reuse — mandatory

Do not generate new backtest origins in Phase 15.

Input should be the frozen Phase 14 validation plan or a deterministic representation of it.

For every baseline assert:

```text
same backtest_id
same origin_week_start_date
same depot + brand series
same target weeks
same horizons 1..10
```

No baseline may receive a more favorable validation period.

Required audit:

```text
BASELINE_BACKTEST_SIGNATURE
==
PHASE14_BACKTEST_SIGNATURE
```

The signature can be a deterministic hash over non-private split metadata.

---

# 22. Leakage and fit-scope contract

Although these baselines are simpler than ML models, leakage is still possible.

## 22.1 No full-history aggregate

Wrong:

```python
weekly_panel.groupby(["depot", "brand"])["total_volume_m3"].mean()
```

computed over all historical weeks before backtesting.

Right:

```text
for each origin:
    subset history to week <= origin
    derive baseline state from that subset only
```

## 22.2 Same-week seasonal lookup

Even prior-year lookup must pass:

```text
source_week <= origin
```

## 22.3 Validation y isolation

After baseline predictions have been generated:

1. copy validation rows;
2. change validation target values only;
3. regenerate predictions;
4. predictions must remain unchanged.

## 22.4 Future-demand mutation

For an origin `t`:

1. generate all horizon predictions;
2. change actual demand at `t+1..t+10`;
3. regenerate;
4. predictions must remain identical.

Any failure is a Phase 15 blocker.

---

# 23. Raw-prediction evaluation policy

Phase 14 froze metric behavior and Phase 17 owns final submission corrections.

Therefore Phase 15 evaluates raw baseline predictions.

Do not apply generic:

```text
negative clipping
chilled <= total enforcement
rounding
manual capping
```

before metric calculation.

Simple baselines built from nonnegative historical demand should naturally be nonnegative; if an implementation emits a negative value, treat it as a bug or diagnostic.

For Fresh chilled:

```text
chilled_gt_total_count
```

is diagnostic only in Phase 15.

---

# 24. Run manifest

Every private baseline run should include a manifest containing:

```text
phase = 15
created_at
Git commit/hash if available
baseline config identity/hash
Phase 14 validation config identity/hash
Phase 14 backtest-plan signature
weekly-panel schema/version
metric contract version
library versions
```

It should explicitly state:

```text
PHASE 14 SPLITS REUSED: YES
NEW SPLITS CREATED: NO
FUTURE DEMAND USED: NO
BASELINE WEIGHTS TUNED: NO
ADVANCED MODEL TRAINED: NO
TASK 1 ARTIFACTS CHANGED: NO
```

---

# 25. Required synthetic tests

Create comprehensive tests using synthetic data only.

## DT-228 — last week

- exact origin-week prediction;
- horizon 1..10 all identical;
- different series isolated;
- future-demand mutation invariant;
- validation-target mutation invariant;
- missing origin value fails;
- confirmed zero origin predicts zero.

## DT-229 — recent mean

- exact four-week mean;
- zeros included;
- trailing window ends at origin;
- no centered/future window;
- insufficient history unavailable;
- future mutation invariant;
- series isolation.

## DT-230 — same week last year

- exact previous ISO year/week lookup;
- ISO-year boundary;
- week 53 exact lookup;
- week 53 missing fallback;
- missing seasonal row fallback;
- source-after-origin rejected;
- future target mutation invariant.

## DT-231 — weighted

- exact 50/50 blend;
- config weights sum to one;
- negative weight rejected;
- seasonal missing → recent fallback;
- recent missing → unavailable;
- no score-driven weight selection path;
- deterministic output.

## DT-232 — chilled

- Fresh last-week baseline;
- Fresh recent mean baseline;
- Fresh seasonal baseline;
- Fresh weighted baseline;
- Style exact zero;
- Tech exact zero;
- Fresh chilled history independent of total history;
- future chilled mutation invariant;
- chilled>total diagnosed, not capped.

## DT-233 — evaluation

- exact Phase 14 split signature required;
- all candidates use same backtests;
- 10 horizons present;
- pooled metrics use Phase 14 metric functions;
- Fresh-only chilled primary metric;
- Style/Tech zero compliance recorded;
- ranking by MAE;
- RMSE tie-break;
- P90 tie-break;
- stability tie-break;
- simplicity final tie-break;
- failed/unavailable baseline not silently dropped;
- deterministic ranking;
- result schema stable;
- manifest complete.

## Global leakage tests

- validation y change does not change predictions;
- actual demand after origin does not change predictions;
- h=10 does not read h=1 actual demand;
- no target-week actual demand in baseline state;
- all seasonal source weeks <= origin;
- no future backfill.

## Privacy tests

- console summary does not print weekly volumes;
- no delivery/order IDs printed;
- private output root used;
- tracked docs contain no real predictions.

---

# 26. Edge cases

## Confirmed zero week

A zero historical week is real information.

Examples:

```text
last-week baseline = 0
```

or zero contributes normally to a recent mean.

Do not treat zero as missing.

## Week 53

Exact prior-year week 53 may not exist.

Use the frozen fallback.

Do not invent week 53.

## Cross-year ten-week horizon

Target weeks may cross an ISO-year boundary.

Always use official Phase 14 target metadata.

## Seasonal lookup exists but is after origin

Reject it.

The fact that a row exists in the complete historical dataset does not mean it would have been known at that historical forecast origin.

## Short history

If the rolling mean is unavailable, mark the relevant baseline unavailable rather than using future values.

The Phase 14 minimum-history policy should make this rare or impossible for accepted backtests.

## Brand/depot missing from historical context

This should already be blocked by Phase 14 required-series coverage.

Do not substitute another series.

## Fresh chilled all zeros in a short window

That is a valid history window.

The baseline may predict zero.

## WAPE denominator zero

Reuse Phase 14 behavior:

```text
WAPE = unavailable/null
```

Do not divide by epsilon.

## Raw chilled prediction above total prediction

Record the diagnostic.

Do not cap it in Phase 15.

## Equal baseline scores

Use frozen tie-break logic.

Do not manually choose the more sophisticated candidate.

---

# 27. Phase 15 STOP conditions

`READY FOR PHASE 16` must remain **NO** if any of the following occurs:

- Phase 14 did not pass;
- a new backtest split is created instead of reusing Phase 14;
- a baseline uses demand after the forecast origin;
- a last-week baseline reads a validation week;
- rolling mean is centered or future-looking;
- same-week-last-year lookup uses a source week after the origin;
- missing seasonal data is filled with future information;
- weighted baseline weights are tuned after seeing private scores;
- baseline formulas differ between backtests;
- total and chilled metrics differ from Phase 14 definitions;
- Style chilled is not exactly zero;
- Tech chilled is not exactly zero;
- Fresh chilled primary ranking includes Style/Tech structural zero rows;
- failed backtests are silently removed;
- unavailable baseline predictions are silently replaced with unapproved values;
- prediction outputs are clipped/capped before Phase 14 metric evaluation;
- Phase 16 advanced models are trained;
- Task 1 frozen artifacts are changed;
- private competition data is exposed to an external model context;
- synthetic tests fail;
- the local baseline run fails;
- independent review fails.

---

# 28. Phase 15 Definition of Done

Phase 15 passes only when:

- [ ] DT-228 PASS
- [ ] DT-229 PASS
- [ ] DT-230 PASS
- [ ] DT-231 PASS
- [ ] DT-232 PASS
- [ ] DT-233 PASS
- [ ] Phase 14 validation plan reused exactly
- [ ] no new validation origins created
- [ ] exact ten-week windows retained
- [ ] last-week baseline implemented
- [ ] recent mean uses frozen four-week window
- [ ] same-week-last-year uses official ISO-year/week semantics
- [ ] week-53 fallback tested
- [ ] weighted baseline uses frozen 50/50 formula
- [ ] no weight tuning performed
- [ ] all total baseline families evaluated
- [ ] Fresh chilled baseline families evaluated
- [ ] Style chilled exactly zero
- [ ] Tech chilled exactly zero
- [ ] validation-target mutation test passes
- [ ] future-demand mutation test passes
- [ ] seasonal source availability audit passes
- [ ] Phase 14 metrics reused exactly
- [ ] per-series metrics generated
- [ ] per-horizon metrics generated
- [ ] backtest stability generated
- [ ] total reference baseline frozen
- [ ] Fresh chilled reference baseline frozen
- [ ] no final Task 2A champion declared
- [ ] baseline results stored privately
- [ ] run manifest generated
- [ ] all synthetic tests pass
- [ ] full safe regression suite passes
- [ ] `python -m pip check` passes
- [ ] Task 1 frozen artifacts unchanged
- [ ] private paths remain ignored
- [ ] independent review passes
- [ ] no unresolved STOP condition remains

Then:

```text
PHASE 15 STATUS: PASS
READY FOR PHASE 16: YES
```

---

# 29. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-15-task2a-baselines
```

Recommended commits:

```text
feat(task2a): add deterministic forecast baselines
feat(task2a): add chilled baseline handling
feat(task2a): add baseline backtest evaluation
feat(task2a): add reference baseline selection
test(task2a): add Phase 15 baseline tests
docs(task2a): document baseline methodology
```

Before every commit:

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
pytest -q tests/test_task2a_history.py \
          tests/test_task2a_eda.py \
          tests/test_task2a_features.py \
          tests/test_task2a_multihorizon.py \
          tests/test_task2a_validation.py \
          tests/test_task2a_metrics.py \
          tests/test_task2a_baselines.py \
          tests/test_task2a_baseline_evaluation.py

pytest -q
python -m pip check
git status
```

Merge only after:

```text
LOCAL PHASE 15 BASELINE RUN: PASS
INDEPENDENT PHASE 15 REVIEW: PASS
```

---

# 30. Recommended Codex model and reasoning level

Phase 15 is mostly deterministic baseline logic and evaluation reuse.

Recommended low-token option:

```text
GPT-5.6 Terra — Medium reasoning
```

Escalate only if necessary:

```text
GPT-5.6 Sol — Medium reasoning
```

Use the stronger model only for a genuine split/leakage/debugging problem.

There is no reason to spend the highest-cost model on routine Phase 15 implementation if Phase 14 interfaces are already clean.

---

# 31. Local real-data execution

Codex should implement and synthetically test the command, but the human operator runs it against private competition-derived files.

Recommended command:

```bash
python scripts/run_task2a_baselines.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --multihorizon-table data/interim/task2a_multihorizon_train.csv \
  --validation-config configs/task2a_validation.yaml \
  --baseline-config configs/task2a_baselines.yaml \
  --output-dir reports/private/phase15_task2a_baselines
```

PowerShell one-line equivalent:

```powershell
python scripts/run_task2a_baselines.py --weekly-panel data/interim/task2a_weekly_panel.csv --multihorizon-table data/interim/task2a_multihorizon_train.csv --validation-config configs/task2a_validation.yaml --baseline-config configs/task2a_baselines.yaml --output-dir reports/private/phase15_task2a_baselines
```

Console output should be sanitized.

Recommended human-return summary:

```text
LOCAL PHASE 15 BASELINE RUN: PASS
PHASE 14 BACKTEST SIGNATURE MATCH: YES
ALL REQUIRED BACKTESTS COMPLETED: YES
TOTAL BASELINE CANDIDATES COMPLETE: YES
FRESH CHILLED BASELINE CANDIDATES COMPLETE: YES
STYLE CHILLED EXACT ZERO: YES
TECH CHILLED EXACT ZERO: YES
FUTURE-DEMAND LEAKAGE AUDIT: PASS
TOTAL REFERENCE BASELINE FROZEN: YES
CHILLED REFERENCE BASELINE FROZEN: YES
```

Do not paste private weekly prediction tables or detailed private metric values into the coding agent unless the competition data-handling policy is independently confirmed to permit that workflow.

---

# 32. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 15 only.

PHASE:
Task 2A Baseline Models

TASK RANGE:
DT-228 through DT-233

EXECUTION MODE:
Full-phase controlled autonomous implementation with SAFE synthetic tests.

RECOMMENDED MODEL:
GPT-5.6 Terra — Medium reasoning

Fallback for a genuine hard bug:
GPT-5.6 Sol — Medium reasoning

You MAY:

- create/edit/refactor Phase 15 tracked source code
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
- self-review against the Phase 15 Definition of Done

Do NOT stop for ordinary coding/test failures that can safely be fixed.

STOP only for:

- official competition-rule ambiguity
- requirement to inspect restricted competition row-level data
- Phase 14 contract inconsistency
- frozen split/metric mismatch
- future-demand leakage that cannot be safely removed
- genuine schema/data-quality blocker
- material cross-phase redesign

DO NOT START PHASE 16.

==================================================
READ FIRST
==================================================

Read with targeted context:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase 15 and Task 2A global rules
4. PHASE_11_COMPETITION_CONTRACT.md
   - canonical weekly history
5. PHASE_13_COMPETITION_CONTRACT.md
   - origin/horizon semantics
6. PHASE_14_COMPETITION_CONTRACT.md
   - frozen rolling-origin plan and metrics
7. PHASE_15_COMPETITION_CONTRACT.md
8. src/task2a/history.py
9. src/task2a/validation.py
10. src/task2a/metrics.py
11. configs/task2a_history.yaml
12. configs/task2a_validation.yaml
13. existing Task 2A tests

Use targeted reading.

Do not reread unrelated Phase 00–10 contracts unless a direct dependency
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

Do NOT inspect or print private competition rows from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for agent-run implementation/testing.

The human operator will execute the real Phase 15 backtest locally.

==================================================
OFFICIAL TASK 2A CONTEXT
==================================================

Task 2A forecasts 10 future weeks of:

pred_total_volume_m3
pred_chilled_volume_m3

for supplied depot + brand + week rows.

Official history remains:

deliveries_train.csv
+
task1_test_inputs.csv

Count every unique requested order once.

Include:

attempted
deferred
not_run

Demand date:

order_date

Weekly grouping:

calendar.iso_year
calendar.iso_week

Only Fresh has chilled demand.

Style chilled = exactly 0.
Tech chilled = exactly 0.

The organizer does not prescribe the baseline formulas below.
They are frozen WayLoom engineering baselines.

==================================================
IMMUTABLE PHASE 14 CONTRACT
==================================================

Reuse Phase 14 EXACTLY.

Do NOT:

- create new rolling origins
- random split
- change 10-week windows
- change series coverage
- change metric formulas
- change primary metrics

Every baseline must use the exact same:

backtest IDs
origins
series
target weeks
horizons 1..10
metric functions

Create/verify a deterministic Phase 14 backtest signature.

==================================================
CREATE / UPDATE
==================================================

src/task2a/baselines.py
src/task2a/baseline_evaluation.py

scripts/run_task2a_baselines.py

configs/task2a_baselines.yaml

docs/task2a_baseline_spec.md

tests/test_task2a_baselines.py
tests/test_task2a_baseline_evaluation.py

Private output:

reports/private/phase15_task2a_baselines/**

must remain ignored.

==================================================
COMMON INFORMATION BOUNDARY
==================================================

For every historical backtest origin t:

baseline history = weekly panel rows with week <= t

NEVER use demand after t.

Never compute baseline statistics from the complete panel before splitting.

For every baseline, implement:

future-demand mutation test
validation-target mutation test

Changing validation/future actual values must not change baseline predictions.

==================================================
DT-228 — LAST-WEEK BASELINE
==================================================

For each series and backtest origin:

prediction(h=1..10) = total_volume_m3 at origin week t

All ten horizon predictions are identical for one series/origin.

Use origin-week demand only.

Do not read t+1..t+10 actual values.

Tests:

- exact last value
- h1..h10 identical
- confirmed zero retained
- series isolation
- future-demand mutation invariant
- missing origin value fails

==================================================
DT-229 — RECENT ROLLING-MEAN BASELINE
==================================================

Frozen window:

4 weeks

Formula:

recent_mean_4 = mean(y[t-3], y[t-2], y[t-1], y[t])

Forecast h1..h10 with that same value.

Requirements:

- trailing only
- full 4-week window
- zero is valid
- no centered window
- no future demand
- no tuning window size after seeing scores

If <4 weeks available:

BASELINE_UNAVAILABLE

Do not backfill from the future.

==================================================
DT-230 — SAME-WEEK-LAST-YEAR BASELINE
==================================================

For each target week:

lookup same:

depot
brand

at:

target_iso_year - 1
target_iso_week

Use official ISO-year/week semantics.

Do NOT implement this as blind shift(52).

Critical:

seasonal source week must be <= forecast origin.

If exact prior-year week is unavailable:

fallback = recent_mean_4

This includes missing prior-year week 53.

Record fallback usage.

Tests:

- exact lookup
- ISO-year boundary
- week 53 exact
- week 53 fallback
- source-after-origin rejected
- no future leakage

==================================================
DT-231 — SEASONAL / RECENT WEIGHTED BASELINE
==================================================

Frozen formula:

prediction =
0.50 * recent_mean_4
+
0.50 * same_week_last_year

Do NOT tune weights.

Do NOT search 0.2/0.8, 0.3/0.7, etc.

If seasonal unavailable:

prediction = recent_mean_4

If recent mean unavailable:

BASELINE_UNAVAILABLE

Validate:

weights >= 0
sum(weights) == 1

==================================================
DT-232 — SEPARATE CHILLED BASELINE
==================================================

Fresh:

apply the same four baseline families to:

chilled_volume_m3

Create:

chilled_last_week
chilled_recent_mean_4
chilled_same_week_last_year
chilled_seasonal_recent_weighted

Style:

prediction = 0.0 exactly

Tech:

prediction = 0.0 exactly

Primary chilled ranking uses Fresh-only Phase 14 metrics.

Do NOT let structural Style/Tech zeros dominate chilled model selection.

Do NOT enforce chilled <= total in Phase 15.

If raw Fresh chilled > corresponding total prediction:

record chilled_gt_total_count

Do not cap it.

Phase 17 owns final output enforcement.

==================================================
DT-233 — COMPARE BASELINES ACROSS BACKTESTS
==================================================

TOTAL candidate set:

total_last_week
total_recent_mean_4
total_same_week_last_year
total_seasonal_recent_weighted

FRESH CHILLED candidate set:

chilled_last_week
chilled_recent_mean_4
chilled_same_week_last_year
chilled_seasonal_recent_weighted

Reuse Phase 14 evaluation functions.

Do not reimplement metrics differently.

For each candidate report:

OVERALL:

pooled MAE
RMSE
WAPE
mean bias
P90 absolute error

BACKTEST STABILITY:

backtest count
mean backtest MAE
std backtest MAE
median backtest MAE
worst backtest MAE

PER SERIES:

depot + brand

PER HORIZON:

1..10

==================================================
REFERENCE BASELINE SELECTION
==================================================

Freeze exactly one:

REFERENCE TOTAL BASELINE

and one:

REFERENCE FRESH CHILLED BASELINE

Primary criterion:

lowest Phase 14 overall pooled MAE

Tie-break:

1. lower RMSE
2. lower P90 absolute error
3. lower backtest MAE std
4. simpler baseline

Simplicity order:

last_week
recent_mean_4
same_week_last_year
seasonal_recent_weighted

These are REFERENCE BASELINES.

They are NOT the final Task 2A model.

Phase 16 must compare advanced models against them.

==================================================
PRIVATE OUTPUTS
==================================================

Generate:

run_manifest.json
backtest_predictions.csv
backtest_metrics.csv
series_metrics.csv
horizon_metrics.csv
baseline_summary.csv
baseline_reference.json
warnings.json
phase15_baseline_report.md

Store under:

reports/private/phase15_task2a_baselines/

Do not commit.

==================================================
NO PHASE 15 POSTPROCESSING
==================================================

Evaluate raw baseline predictions.

Do NOT add generic:

negative clipping
chilled <= total enforcement
rounding
manual caps

Phase 17 owns final submission constraints.

Simple baselines should naturally be nonnegative because their source
history is nonnegative.

If an unexpected negative baseline prediction appears:

FAIL / diagnose implementation.

==================================================
REQUIRED SYNTHETIC TESTS
==================================================

Test all of the following:

LAST WEEK
- exact origin value
- 10 identical horizons
- future mutation invariant
- validation-y mutation invariant
- zero demand valid

RECENT MEAN
- exact 4-week mean
- zero included
- origin-ended trailing window
- insufficient history unavailable
- no future leakage

SEASONAL
- exact prior ISO year/week
- year boundary
- week 53 exact
- week 53 fallback
- missing seasonal fallback
- source-after-origin rejected

WEIGHTED
- exact 50/50
- weight sum validation
- negative weight rejected
- seasonal fallback
- recent unavailable
- deterministic

CHILLED
- Fresh each baseline
- Style exact zero
- Tech exact zero
- future chilled mutation invariant
- chilled>total only diagnosed

EVALUATION
- exact Phase 14 split signature
- same backtests for all candidates
- horizons 1..10
- Phase 14 metric reuse
- Fresh-only chilled primary ranking
- ranking by MAE
- RMSE tie-break
- P90 tie-break
- stability tie-break
- simplicity tie-break
- unavailable prediction not silently replaced
- deterministic summary
- run manifest complete

PRIVACY
- no private values printed
- no private outputs tracked

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After DT-228–231:

run baseline unit tests
inspect failures
fix ordinary bugs
rerun until clean

After DT-232:

run chilled tests

After DT-233:

run evaluation/ranking tests

Then run:

pytest -q tests/test_task2a_history.py tests/test_task2a_eda.py tests/test_task2a_features.py tests/test_task2a_multihorizon.py tests/test_task2a_validation.py tests/test_task2a_metrics.py tests/test_task2a_baselines.py tests/test_task2a_baseline_evaluation.py

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

Implement but DO NOT execute against restricted private competition data:

python scripts/run_task2a_baselines.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --multihorizon-table data/interim/task2a_multihorizon_train.csv \
  --validation-config configs/task2a_validation.yaml \
  --baseline-config configs/task2a_baselines.yaml \
  --output-dir reports/private/phase15_task2a_baselines

Console output must be sanitized.

==================================================
STOP CONDITIONS
==================================================

STOP if:

- Phase 14 validation is bypassed
- a new backtest is created
- baseline candidates use different backtests
- actual demand after origin enters a baseline
- rolling window looks forward
- seasonal source is after origin
- future demand is used as fallback
- 50/50 weights are tuned after results
- metric formulas change
- Style chilled != 0
- Tech chilled != 0
- Fresh chilled primary ranking includes structural-zero brands
- failed backtests are dropped
- unapproved values replace unavailable forecasts
- generic clipping/capping is added before evaluation
- Phase 16 model training begins
- Task 1 artifacts change
- private competition data must be exposed
- tests cannot pass without violating approved contracts

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-228 READY
DT-229 READY
DT-230 READY
DT-231 READY
DT-232 READY
DT-233 READY

Phase 14 splits reused exactly

10-week windows unchanged

last-week baseline leakage-safe

recent mean fixed at 4 weeks

same-week-last-year uses ISO semantics

week-53 fallback deterministic

weighted baseline fixed at 50/50

no weight tuning

Fresh chilled baselines complete

Style chilled exact zero

Tech chilled exact zero

future-demand mutation passes

validation-y mutation passes

Phase 14 metrics reused

all backtests retained

per-series metrics complete

per-horizon metrics complete

total reference baseline frozen

Fresh chilled reference baseline frozen

reference != final Task 2A champion

safe tests pass

pip check passes

private outputs ignored

Task 1 unchanged

no Phase 16 implementation added

==================================================
RETURN ONLY
==================================================

PHASE:
15 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-228 READY / FAIL
DT-229 READY / FAIL
DT-230 READY / FAIL
DT-231 READY / FAIL
DT-232 READY / FAIL
DT-233 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

PHASE 14 VALIDATION REUSE:
PASS / FAIL

BACKTEST SIGNATURE MATCH:
PASS / FAIL

LAST-WEEK BASELINE:
PASS / FAIL

RECENT-MEAN BASELINE:
PASS / FAIL

SAME-WEEK-LAST-YEAR BASELINE:
PASS / FAIL

WEIGHTED BASELINE:
PASS / FAIL

FRESH CHILLED BASELINES:
PASS / FAIL

STYLE CHILLED ZERO:
PASS / FAIL

TECH CHILLED ZERO:
PASS / FAIL

FUTURE-DEMAND MUTATION TEST:
PASS / FAIL

VALIDATION-Y MUTATION TEST:
PASS / FAIL

BASELINE COMPARISON:
PASS / FAIL

TOTAL REFERENCE BASELINE:
READY / FAIL

CHILLED REFERENCE BASELINE:
READY / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 15 baseline command.

PHASE 15 STATUS:
AWAITING LOCAL BASELINE RUN

READY FOR PHASE 16:
NO

Then STOP.

Do not start Phase 16.
```

---

# 33. Independent Phase 15 review prompt

Use a **fresh Codex session** after the human local baseline run.

```text
Perform an independent review of completed WayLoom Datathon Phase 15.

PHASE:
Task 2A Baseline Models

TASKS:
DT-228 through DT-233

DO NOT:

- modify code initially
- access data/raw/**
- access data/interim/**
- access reports/private/**
- inspect private baseline predictions
- inspect private metric values
- create new backtests
- start Phase 16

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 15
4. PHASE_14_COMPETITION_CONTRACT.md
5. PHASE_15_COMPETITION_CONTRACT.md
6. src/task2a/baselines.py
7. src/task2a/baseline_evaluation.py
8. scripts/run_task2a_baselines.py
9. configs/task2a_baselines.yaml
10. configs/task2a_validation.yaml
11. src/task2a/validation.py
12. src/task2a/metrics.py
13. tests/test_task2a_baselines.py
14. tests/test_task2a_baseline_evaluation.py
15. .gitignore
16. .cursorignore if present

HUMAN LOCAL CONTROL RESULT:

LOCAL PHASE 15 BASELINE RUN: <PASS / FAIL>
PHASE 14 BACKTEST SIGNATURE MATCH: <YES / NO>
ALL REQUIRED BACKTESTS COMPLETED: <YES / NO>
TOTAL BASELINE CANDIDATES COMPLETE: <YES / NO>
FRESH CHILLED BASELINE CANDIDATES COMPLETE: <YES / NO>
STYLE CHILLED EXACT ZERO: <YES / NO>
TECH CHILLED EXACT ZERO: <YES / NO>
FUTURE-DEMAND LEAKAGE AUDIT: <PASS / FAIL>
TOTAL REFERENCE BASELINE FROZEN: <YES / NO>
CHILLED REFERENCE BASELINE FROZEN: <YES / NO>

Do not ask for private score values.

==================================================
AUDIT DT-228
==================================================

Verify:

- total last-week baseline exists
- origin-week demand only
- horizons 1..10 receive persistence prediction
- future demand cannot influence output
- confirmed zero handled correctly

==================================================
AUDIT DT-229
==================================================

Verify:

- recent mean is fixed at 4 weeks
- window is trailing and ends at origin
- full window required
- no future backfill
- no data-driven window tuning

==================================================
AUDIT DT-230
==================================================

Verify:

- exact official ISO-year/week prior-year lookup
- not blind shift(52)
- week 53 handled
- seasonal source <= origin
- fallback is recent_mean_4
- fallback is frozen and logged

==================================================
AUDIT DT-231
==================================================

Verify:

- exact 0.50 recent + 0.50 seasonal formula
- weights are fixed
- weights validated
- no tuning/search
- seasonal fallback deterministic

==================================================
AUDIT DT-232
==================================================

Verify:

- Fresh chilled baselines use chilled history
- Style predictions exactly 0
- Tech predictions exactly 0
- Fresh-only primary chilled comparison
- no hidden chilled<=total capping
- chilled_gt_total is diagnostic only

==================================================
AUDIT DT-233
==================================================

Verify:

- exact Phase 14 backtests reused
- exact Phase 14 metric functions reused
- all required baseline candidates evaluated
- failed backtests not silently dropped
- per-series metrics exist
- per-horizon metrics exist
- backtest stability exists
- reference total baseline frozen
- reference Fresh chilled baseline frozen
- primary ranking is pooled MAE
- tie-breaks match contract
- reference baseline is not mislabeled final model

==================================================
GLOBAL LEAKAGE AUDIT
==================================================

Verify synthetic tests prove:

- validation-y mutation cannot change predictions
- future-demand mutation cannot change predictions
- seasonal lookup cannot use future source week
- rolling mean cannot cross origin
- no future fallback

==================================================
RAW-PREDICTION POLICY
==================================================

Verify Phase 15 does NOT silently:

- clip negative values
- enforce chilled<=total
- round before metrics
- cap spikes

Final output corrections belong to Phase 17.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q tests/test_task2a_history.py tests/test_task2a_eda.py tests/test_task2a_features.py tests/test_task2a_multihorizon.py tests/test_task2a_validation.py tests/test_task2a_metrics.py tests/test_task2a_baselines.py tests/test_task2a_baseline_evaluation.py

Then if safe:

pytest -q

Then:

python -m pip check

git status

Do not run the private real-data baseline experiment.

==================================================
RETURN
==================================================

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

DT-228: PASS / FAIL
DT-229: PASS / FAIL
DT-230: PASS / FAIL
DT-231: PASS / FAIL
DT-232: PASS / FAIL
DT-233: PASS / FAIL

PHASE 14 VALIDATION REUSE:
PASS / FAIL

BACKTEST SIGNATURE:
PASS / FAIL

FUTURE-DEMAND LEAKAGE PROTECTION:
PASS / FAIL

BASELINE FORMULAS FROZEN:
PASS / FAIL

PHASE 14 METRIC REUSE:
PASS / FAIL

FRESH CHILLED POLICY:
PASS / FAIL

STYLE/TECH ZERO POLICY:
PASS / FAIL

REFERENCE BASELINE SELECTION:
PASS / FAIL

RAW-PREDICTION POLICY:
PASS / FAIL

SYNTHETIC TESTS:
PASS / FAIL

HUMAN LOCAL BASELINE RUN:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

PHASE 15 REVIEW:
PASS / FAIL

READY FOR PHASE 16:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not start Phase 16.
```

---

# 34. Completion record template

```markdown
# Phase 15 Completion Record

## Task status

- [ ] DT-228
- [ ] DT-229
- [ ] DT-230
- [ ] DT-231
- [ ] DT-232
- [ ] DT-233

## Validation reuse

- Phase 14 plan reused: YES / NO
- Backtest signature match: PASS / FAIL
- Exact 10-week windows: PASS / FAIL

## Baseline implementation

- Last week: PASS / FAIL
- Recent mean 4: PASS / FAIL
- Same week last year: PASS / FAIL
- Seasonal/recent weighted: PASS / FAIL

## Chilled

- Fresh baselines: PASS / FAIL
- Style exact zero: PASS / FAIL
- Tech exact zero: PASS / FAIL

## Leakage

- Future-demand mutation: PASS / FAIL
- Validation-y mutation: PASS / FAIL
- Seasonal source availability: PASS / FAIL

## Evaluation

- Phase 14 metrics reused: PASS / FAIL
- Per-series metrics: PASS / FAIL
- Per-horizon metrics: PASS / FAIL
- Backtest stability: PASS / FAIL
- Total reference frozen: YES / NO
- Fresh chilled reference frozen: YES / NO

## Safety

- Task 1 artifacts changed: NO
- Private data exposed to agent: NO
- Private outputs committed: NO

## Review

- Synthetic tests: PASS / FAIL
- Full safe suite: PASS / FAIL
- pip check: PASS / FAIL
- Local baseline run: PASS / FAIL
- Independent review: PASS / FAIL

## Verdict

PHASE 15 STATUS: PASS / FAIL
READY FOR PHASE 16: YES / NO
```

---

# 35. Final Phase 15 checklist

Before Phase 16:

- [ ] Phase 14 passed.
- [ ] DT-228–DT-233 all pass.
- [ ] No new backtest origins were created.
- [ ] Last-week persistence is origin-only.
- [ ] Recent mean is frozen at four trailing weeks.
- [ ] Same-week-last-year uses official ISO semantics.
- [ ] Week 53 fallback is deterministic.
- [ ] Seasonal/recent weights are frozen at 0.50/0.50.
- [ ] No weight/window tuning occurred after private scores.
- [ ] Total baselines evaluated across every frozen backtest.
- [ ] Fresh chilled baselines evaluated across every frozen backtest.
- [ ] Style chilled is exactly zero.
- [ ] Tech chilled is exactly zero.
- [ ] Future-demand mutation test passes.
- [ ] Validation-y mutation test passes.
- [ ] Seasonal source weeks are always known by origin.
- [ ] Phase 14 metric functions are reused.
- [ ] No failed backtest is silently dropped.
- [ ] Per-series diagnostics exist.
- [ ] Per-horizon diagnostics exist.
- [ ] Total reference baseline is frozen.
- [ ] Fresh chilled reference baseline is frozen.
- [ ] Reference baselines are not called final models.
- [ ] Phase 16 advanced modelling has not started.
- [ ] Task 1 frozen artifacts are unchanged.
- [ ] Private outputs remain ignored.
- [ ] Local baseline run passes.
- [ ] Independent review passes.

Only then:

```text
PHASE 15 STATUS: PASS
READY FOR PHASE 16: YES
```
