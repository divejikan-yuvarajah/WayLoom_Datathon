# PHASE 07 — Task 1 Validation Design

> **Requested filename:** `PHASE_07_COMPETITION_CONTRACT.md`  
> **Canonical phase name:** **Phase 07 — Task 1 Validation Design**  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-123 → DT-129**  
> **Task count:** 7  
> **Phase dependency:** Phases 04–06 must have passed  
> **Default priority:** P1, but validation mistakes are competition-critical  
> **Recommended execution style:** **High-risk validation phase — implement the framework as one controlled phase, but independently gate the chronological holdout, expanding folds, same-date protection, and frozen metrics before any model comparison**  
> **Phase gate:** **Chronological validation and metrics are frozen before Phase 08 baselines or Phase 09 model comparison begins.**

---

# 1. Purpose of Phase 07

Phase 07 freezes **how Task 1 models will be judged locally** before the team trains and compares baselines or advanced models.

This phase exists to prevent three common competition failures:

1. **random-split optimism** — future-like rows leak into training;
2. **same-day leakage** — deliveries from the same operational day appear in both train and validation;
3. **moving evaluation rules** — metrics/splits change after seeing which model looks best.

The validation design must simulate the real Task 1 situation:

```text
historical earlier deliveries
        ↓
fit preprocessing / fit-dependent features / model
        ↓
later unseen delivery plans
        ↓
predict service minutes + late probability
        ↓
score without using later outcomes during fitting
```

Phase 07 does **not** train the final Task 1 models. It creates the immutable evaluation contract that Phases 08–10 must obey.

---

# 2. Official requirements versus WayLoom engineering choices

## 2.1 Official Task 1 facts that constrain validation

The official booklet requires Task 1 to predict, for each planned test `delivery_id`:

```text
pred_service_min
pred_late_prob
```

The first is a regression output and the second is a probability in `[0,1]`.

The official booklet also states:

- planned departure, planned travel duration and planned arrival are available at prediction time;
- actual journey and handling times are available only in historical route records;
- teams may choose and justify their feature set;
- correct label construction is part of assessment;
- the exact hidden evaluation metric is **not specified in the booklet**.

Therefore validation must never allow later actual journey/target information into model fitting.

## 2.2 WayLoom engineering choices in this phase

The following are **team validation decisions**, not organizer-mandated formulas:

- use later historical dates for validation;
- keep all rows from the same date in the same split;
- reserve one final chronological holdout;
- use expanding time folds inside the earlier development history;
- use **MAE** as the primary service-time metric and **RMSE** as a secondary metric;
- use **log loss** as the primary lateness-probability metric and **Brier score** as a secondary metric;
- use ROC-AUC / PR-AUC and calibration diagnostics as secondary descriptive metrics, not as the primary probability-quality objective;
- compute segment metrics by business-relevant groups without using them as separate hidden objectives.

These choices must be frozen in this phase before model results are compared.

---

# 3. Critical leakage boundary carried forward from Phase 06

The final Task 1 validation pipeline must never directly use the following as model features:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag
```

The first four are historical actual outcomes. The final three are target/target-derived.

## 3.1 Special rule for fit-dependent historical features

Phase 06 may define safe historical target statistics such as prior outlet service median or prior late rate.

During validation these features **must be fitted only on the training portion of each split**.

For a validation fold:

```text
fit historical-statistic transformer on fold-train only
        ↓
transform fold-train if needed
        ↓
transform entire fold-validation using frozen fold-train statistics
```

Do **not** allow labels from earlier dates inside the same validation window to update features for later validation dates unless that behavior is explicitly part of the frozen real-world inference protocol. For the WayLoom competition submission, treat each validation window as fully unseen and use **training-fold outcomes only**.

This is stricter and safer for an offline test submission.

---

# 4. Phase 07 data-safety and agent autonomy model

The agent has broad autonomy for safe engineering work.

## Agent MAY

- read tracked code/configuration/contracts;
- edit/refactor Phase 07 source code;
- create synthetic fixtures;
- run unit/integration/regression tests;
- inspect stack traces;
- fix ordinary implementation failures;
- rerun tests automatically until passing;
- run `python -m pip check`;
- inspect `git status` and `git diff`;
- create safe tracked validation documentation;
- self-review against this Definition of Done.

## Agent MUST NOT

- inspect `data/raw/**`;
- inspect private row-level `data/interim/**` competition-derived tables;
- inspect `reports/private/**`;
- transmit real competition rows or private derived records to the model/provider;
- run model comparison using private competition rows inside an external-agent context;
- start Phase 08 automatically.

The human performs the real local validation-plan generation and returns only sanitized status.

---

# 5. Phase 07 task registry

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-123** | [E] | P1 | Phases 04–06 | Sort historical data chronologically |
| [ ] | **DT-124** | [E] | P1 | Phases 04–06 | Define chronological holdout |
| [ ] | **DT-125** | [E] | P1 | Phases 04–06 | Define expanding time folds |
| [ ] | **DT-126** | [E] | P1 | Phases 04–06 | Keep same-date records in the same split |
| [ ] | **DT-127** | [E] | P1 | Phases 04–06 | Freeze regression metrics |
| [ ] | **DT-128** | [E] | P1 | Phases 04–06 | Freeze lateness probability metrics |
| [ ] | **DT-129** | [E] | P1 | Phases 04–06 | Define segment-level metrics |

**Phase complete:** [ ]  
**READY FOR PHASE 08:** NO

---

# 6. Required repository additions

Recommended tracked files:

```text
configs/
└── task1_validation.yaml

src/task1/
├── validation.py
└── metrics.py

scripts/
└── build_task1_validation_plan.py

docs/
└── task1_validation_spec.md

tests/
├── test_task1_validation.py
└── test_task1_metrics.py
```

If Phase 06 already has a feature-transformer abstraction, reuse it rather than duplicating logic.

Private local outputs:

```text
reports/private/phase07_task1_validation/
├── validation_summary.json
├── chronological_sort.json
├── final_holdout.json
├── expanding_folds.json
├── same_date_integrity.json
├── metric_contract.json
├── segment_contract.json
└── phase07_validation_report.md
```

Optional private serialized split boundaries:

```text
reports/private/phase07_task1_validation/split_boundaries.json
```

Prefer storing **date boundaries and counts**, not row-level IDs, whenever practical.

---

# 7. Recommended frozen validation configuration

The competition does not prescribe exact local splits. The following is the recommended WayLoom contract.

```yaml
version: 1

validation_date:
  column: route_date
  fallback_column: dispatch_date
  require_consistency_when_both_present: true

ordering:
  stable_sort: true
  tie_breakers:
    - route_id
    - seq_in_route
    - delivery_id

final_holdout:
  strategy: last_calendar_days
  calendar_days: 42
  same_date_atomic: true

expanding_cv:
  n_folds: 4
  validation_calendar_days: 42
  gap_calendar_days: 0
  same_date_atomic: true
  require_expanding_train: true
  minimum_training_calendar_days: 180

fit_dependent_features:
  validation_policy: fit_on_train_transform_validation
  allow_validation_targets_during_transform: false

metrics:
  regression:
    primary: mae
    secondary:
      - rmse
      - median_absolute_error
      - p90_absolute_error
    diagnostics:
      - negative_prediction_count
  lateness_probability:
    primary: log_loss
    secondary:
      - brier_score
    diagnostics:
      - roc_auc
      - average_precision
      - calibration_error

segments:
  fields:
    - brand
    - depot
    - district
    - dock_type
    - temp_requirement
    - is_first_stop
    - monsoon
    - planned_slack_bin
  minimum_n: 30
  minimum_positive_for_auc: 5
  minimum_negative_for_auc: 5
```

### Important note on the suggested 42-day windows

`42` calendar days is a **WayLoom engineering choice intended to approximate a six-week future-like evaluation window**. It is not an organizer-mandated value.

If the local history cannot support the required number of folds with sufficient training history, the team may change this configuration **before running Phase 08 models**. Once Phase 07 passes and model comparison begins, split rules are frozen.

Do not tune the split window after seeing which model wins.

---

# 8. Canonical validation date

## Recommended choice

Use:

```text
route_date
```

from the matched historical route leg as the canonical Task 1 validation date.

Rationale:

- the historical service/lateness event occurs on the delivery route date;
- deferred orders may have an `order_date` earlier than the actual dispatch/service date;
- validation should simulate predicting a **future planned delivery**, not a future order request.

If `dispatch_date` is also present for the matched order, locally validate that the two fields are consistent for dispatched rows.

If the project does not currently expose a canonical `route_date`, add it to the safe labelled/feature metadata without changing the target definition.

Do not split Task 1 history using `order_date` merely because it is easy to access.

---

# 9. Detailed task specifications

---

## DT-123 — Sort historical data chronologically

**Mark:** [E]  
**Priority:** P1  
**Execution:** Individual foundation task

### Objective

Create a deterministic chronological ordering for Task 1 historical rows.

### Inputs

At minimum:

```text
delivery_id
route_date
route_id
seq_in_route
service_minutes
late_flag
```

plus safe feature metadata.

### Required behavior

1. parse `route_date` to a real date type;
2. reject missing/invalid validation dates;
3. stable-sort by:
   ```text
   route_date ascending
   ```
4. use deterministic tie-breakers only for stable row order;
5. preserve original source index for traceability;
6. assert sorted dates are nondecreasing;
7. never sort using target magnitude.

### Recommended function

```python
def sort_task1_history_chronologically(
    frame: pd.DataFrame,
    *,
    date_col: str = "route_date",
) -> pd.DataFrame:
    ...
```

### Why same-date tie ordering does not create validation sequence

All rows on a date will later be atomic for split assignment.

The row order inside a date is only deterministic bookkeeping. It must not be interpreted as information that one stop's target is known before another same-date validation row.

### Tests

Synthetic cases:

- unsorted dates become sorted;
- same date with multiple rows remains together;
- tie-break ordering deterministic;
- missing date fails;
- invalid date fails;
- original input not mutated;
- duplicate delivery ID rejected by upstream contract or validation check.

### Definition of Done

- [ ] canonical date chosen and documented;
- [ ] chronological sort deterministic;
- [ ] same-date row order not used as target chronology;
- [ ] invalid dates fail loudly.

### STOP conditions

Stop if no trustworthy service/delivery date can be identified.

---

## DT-124 — Define chronological holdout

**Mark:** [E]  
**Priority:** P1  
**Execution:** **Critical individual gate**

### Objective

Reserve the newest historical period as an untouched final local holdout.

### Recommended WayLoom design

```text
all historical Task 1 dates
        ↓
older development period
        ↓
latest 42 calendar days = final holdout
```

All rows from a boundary date must be assigned together.

### Key rules

- choose boundaries by **date**, not row count;
- final holdout must contain only dates later than all development dates;
- no date may appear in both development and holdout;
- no random shuffling;
- final holdout must not be used to tune hyperparameters or feature choices after Phase 07;
- fit-dependent transformations must be fit on development history only before transforming final holdout;
- final holdout target values are only used for scoring.

### Recommended result object

```python
@dataclass(frozen=True)
class HoldoutSplit:
    development_index: np.ndarray
    holdout_index: np.ndarray
    development_start: date
    development_end: date
    holdout_start: date
    holdout_end: date
```

### Validation assertions

```text
max(development_date) < min(holdout_date)
intersection(development_dates, holdout_dates) = empty
holdout row count > 0
development row count > 0
```

### Edge cases

#### Boundary date contains many rows

All belong to one side.

#### Dataset has too little history

Do not silently shrink to an unusable holdout.

Fail with a configuration error or require a deliberate config change before model comparison.

#### Missing dates near boundary

Chronological boundary still follows calendar date, not row positions.

### Tests

- latest dates selected;
- no overlap;
- same-date atomicity;
- deterministic split;
- no random seed affects boundaries;
- insufficient history raises;
- holdout not included in development folds later.

### Definition of Done

- [ ] final holdout boundary frozen;
- [ ] latest-period logic correct;
- [ ] holdout isolated from model development;
- [ ] split reproducible.

### STOP conditions

Any row/date overlap between development and holdout blocks Phase 08.

---

## DT-125 — Define expanding time folds

**Mark:** [E]  
**Priority:** P1  
**Execution:** **Critical individual gate**

### Objective

Create multiple future-like validation folds within the development period for reproducible baseline/model comparison.

### Required structure

Use expanding training history:

```text
Fold 1:
[TRAIN ----------------] [VALID]

Fold 2:
[TRAIN ----------------------] [VALID]

Fold 3:
[TRAIN ----------------------------] [VALID]

Fold 4:
[TRAIN ----------------------------------] [VALID]

Final holdout:
                                              [HOLDOUT]
```

The final holdout must never become a cross-validation fold.

### Recommended WayLoom defaults

```text
number of folds: 4
validation window: 42 calendar days
gap: 0 calendar days
minimum initial training history: 180 calendar days
```

These values are engineering choices and remain configurable until the Phase 07 contract is frozen.

### Fold invariants

For every fold:

```text
max(train_date) < min(validation_date)
train_dates ∩ validation_dates = ∅
validation_dates ∩ final_holdout_dates = ∅
```

Across folds:

```text
train_end(fold k+1) >= train_end(fold k)
training row/date set expands monotonically
validation periods move forward in time
```

### Fit-dependent feature rule

For each fold:

```text
fit feature transformer / categorical preprocessing / target-history statistics
ON fold training data only
```

Then:

```text
transform fold validation without reading validation targets
```

A precomputed full-history target statistic must not bypass this rule.

### Recommended splitter API

```python
class ExpandingDateSplitter:
    def split(self, dates: pd.Series) -> list[TemporalFold]:
        ...
```

with:

```python
@dataclass(frozen=True)
class TemporalFold:
    fold_id: int
    train_index: np.ndarray
    validation_index: np.ndarray
    train_start: date
    train_end: date
    validation_start: date
    validation_end: date
```

### Tests

- expected fold count;
- folds are chronological;
- training grows;
- validation windows do not overlap holdout;
- same-date atomicity;
- no train/validation date overlap;
- deterministic output;
- insufficient development history fails clearly;
- fit-dependent feature transformer receives validation `y=None` / cannot read validation target;
- a deliberately leaky transformer test is rejected.

### Definition of Done

- [ ] expanding folds deterministic;
- [ ] holdout excluded;
- [ ] feature fit scope explicit;
- [ ] no later target can influence earlier fit.

### STOP conditions

Any fold with future-to-past contamination blocks all modelling.

---

## DT-126 — Keep same-date records in the same split

**Mark:** [E]  
**Priority:** P1  
**Execution:** **Critical individual gate**

### Objective

Prevent rows from the same delivery day appearing on both sides of a train/validation or development/holdout boundary.

### Why this matters

Deliveries on one date can share:

- calendar conditions;
- route plans;
- traffic/road context;
- depot conditions;
- fleet patterns;
- operational shocks.

A row-level random or naive index split can make validation artificially easy.

### Required assertion

For every split pair:

```python
assert set(train_dates).isdisjoint(set(validation_dates))
```

Also for final holdout:

```python
assert development_dates.isdisjoint(holdout_dates)
```

### Boundary assignment rule

If the theoretical row-count boundary lands inside a date:

```text
ignore the row boundary
use a date boundary
```

The split should be based on unique sorted dates from the beginning.

### Same-date target-history rule

Historical target-statistic features must not use another row from the same date as target history.

Training-time historical feature rule remains:

```text
historical_date < current_date
```

not:

```text
historical_date <= current_date
```

### Tests

- many rows on boundary date;
- same date across routes;
- same date across brands/depots;
- no split contains date overlap;
- historical stats ignore same-date target values.

### Definition of Done

- [ ] same-date atomicity enforced in holdout and every fold;
- [ ] same-date target-history leakage test passes.

### STOP conditions

Even one shared date between training and validation is a hard failure.

---

## DT-127 — Freeze regression metrics

**Mark:** [E]  
**Priority:** P1

### Objective

Freeze how service-time prediction quality is measured before baseline/model results are compared.

### Official context

The submission requires predicted service minutes, but the booklet does not prescribe the exact hidden score.

Therefore these local metrics are WayLoom engineering choices.

### Frozen service metric contract

#### Primary metric — MAE

```text
MAE = mean(abs(y_true - y_pred))
```

Why primary:

- directly interpretable in minutes;
- robust relative to squared-error metrics;
- appropriate for operational handling-time error.

Lower is better.

#### Secondary metric — RMSE

```text
RMSE = sqrt(mean((y_true - y_pred)^2))
```

Why secondary:

- penalizes large misses strongly;
- useful because long-service failures matter operationally.

Lower is better.

#### Secondary robust diagnostic — Median Absolute Error

```text
median(abs(y_true - y_pred))
```

#### Tail diagnostic — P90 absolute error

```text
90th percentile of abs error
```

### Prediction-validity diagnostics

Report:

```text
n
negative_prediction_count
nonfinite_prediction_count
```

Do not silently clip negative model predictions before local comparison unless a later model-specific postprocessing rule is explicitly frozen and applied to every comparable model.

### Metric API

Recommended:

```python
def regression_metrics(
    y_true: ArrayLike,
    y_pred: ArrayLike,
) -> dict[str, float | int]:
    ...
```

### Required behavior

- same length;
- finite true labels;
- reject nonfinite predictions;
- preserve raw predictions for scoring;
- return deterministic float values;
- no rounding inside metric computation.

### Tests

- perfect predictions → all error metrics 0;
- hand-calculated MAE;
- hand-calculated RMSE;
- hand-calculated median AE;
- p90 behavior;
- nonfinite prediction rejected;
- length mismatch rejected;
- negative prediction counted rather than silently fixed.

### Definition of Done

- [ ] MAE frozen as primary;
- [ ] RMSE frozen as secondary;
- [ ] robust/tail diagnostics defined;
- [ ] metric implementation tested;
- [ ] no model-specific metric switching allowed after results.

### STOP conditions

Do not begin Phase 08 if regression metric definitions are still changing.

---

## DT-128 — Freeze lateness probability metrics

**Mark:** [E]  
**Priority:** P1

### Objective

Freeze metrics that evaluate the quality of **probabilities**, not merely hard late/not-late labels.

### Official context

The submission requires:

```text
pred_late_prob ∈ [0,1]
```

Therefore probability quality must be central to local validation.

### Frozen classification metric contract

#### Primary — Log Loss

```text
-log probability assigned to the observed outcome, averaged across rows
```

Lower is better.

Use a tiny numerical epsilon only inside the log operation if necessary for stability.

Do not convert probabilities to 0/1 decisions before scoring.

#### Secondary — Brier Score

```text
mean((predicted_probability - actual_binary_outcome)^2)
```

Lower is better.

This measures probability accuracy and calibration jointly.

#### Diagnostic — ROC-AUC

Use only when both classes are present.

Higher is better.

It measures ranking, not probability calibration.

#### Diagnostic — Average Precision / PR-AUC-style score

Use when both classes exist.

Useful when lateness is imbalanced.

Higher is better.

#### Calibration diagnostic

Recommended:

```text
Expected Calibration Error (ECE)
```

or another clearly documented calibration summary.

Calibration curves and calibration-model experiments belong primarily to Phase 09, but the metric contract should reserve a consistent diagnostic now.

### Do not use as primary

Avoid choosing models mainly by:

```text
accuracy
F1
precision at arbitrary 0.5 threshold
recall at arbitrary 0.5 threshold
```

because the official output is a probability, not a hard decision.

Threshold metrics may be descriptive later if useful, but they are not frozen primary objectives.

### Probability validity

Require:

```text
0 <= p <= 1
finite
```

Do not silently repair probabilities outside `[0,1]` inside the evaluator.

### Single-class fold behavior

Log loss and Brier can still be calculated with careful binary-label handling.

ROC-AUC and Average Precision diagnostics may be undefined or uninformative.

The metric function must:

- not crash;
- return `None`/`NaN` with an explicit reason flag for undefined ranking metrics;
- keep the primary/secondary probability metrics available.

### Tests

- perfect probabilities;
- known Brier calculation;
- known log-loss calculation;
- probability outside `[0,1]` fails;
- NaN probability fails;
- single-class fold handled cleanly;
- AUC undefined status explicit;
- raw probabilities retained.

### Definition of Done

- [ ] log loss frozen as primary;
- [ ] Brier frozen as secondary;
- [ ] ranking/calibration diagnostics documented;
- [ ] probability bounds enforced;
- [ ] single-class behavior tested.

### STOP conditions

Do not compare classifiers while the primary probability metric is still negotiable.

---

## DT-129 — Define segment-level metrics

**Mark:** [E]  
**Priority:** P1

### Objective

Ensure a model that looks good overall is also inspected across important operational groups.

Segment analysis is diagnostic. It does **not** create separate hidden objectives or criteria-specific model winners.

### Recommended frozen segments

Use prediction-time-safe groups already validated in Phase 06:

```text
brand
depot
district
dock_type
temp_requirement
is_first_stop
monsoon
planned_slack_bin
```

Optional later additions may be allowed only if added **before** model comparison and recorded in the frozen config.

### Regression segment metrics

For each segment value:

```text
n
MAE
RMSE
median_absolute_error
p90_absolute_error
```

### Lateness segment metrics

For each segment value:

```text
n
positive_count
negative_count
observed_late_rate
log_loss
brier_score
```

Where class counts permit:

```text
roc_auc
average_precision
```

### Minimum sample rules

Default WayLoom engineering thresholds:

```text
minimum_n = 30
minimum_positive_for_auc = 5
minimum_negative_for_auc = 5
```

Groups below thresholds are still reported but flagged:

```text
LOW_SUPPORT
```

Do not hide them.

### Overall versus segment metrics

Overall metrics remain the primary model-comparison contract.

Segment metrics answer:

- where errors are concentrated;
- whether one brand/depot is systematically weak;
- whether a model is unstable on small or scarce groups;
- whether later error analysis is needed.

Do not choose a model solely because it wins one segment.

### Aggregation rules

Never average segment metrics without documenting weighting.

If a macro diagnostic is produced:

```text
macro mean = equal weight per eligible segment value
```

If a weighted diagnostic is produced:

```text
weighted mean = weight by segment row count
```

Label them clearly.

### Tests

- segment counts sum appropriately;
- service metrics per group known;
- late metrics per group known;
- low-support flag;
- single-class segment AUC handled;
- missing segment value policy explicit;
- no target-derived grouping field accepted;
- forbidden actual field cannot be used as a segment.

### Definition of Done

- [ ] segment fields frozen;
- [ ] minimum support policy frozen;
- [ ] service and probability segment metrics implemented;
- [ ] low-support groups retained and flagged;
- [ ] diagnostic role documented.

### STOP conditions

Do not allow segment definitions to change opportunistically after model results are seen.

---

# 10. Frozen holdout and cross-validation relationship

Recommended hierarchy:

```text
FULL HISTORICAL TASK 1 TRAINING POPULATION
│
├── DEVELOPMENT PERIOD
│   │
│   ├── expanding fold 1
│   ├── expanding fold 2
│   ├── expanding fold 3
│   └── expanding fold 4
│
└── FINAL CHRONOLOGICAL HOLDOUT
```

## Phase 08–09 usage

### Baselines / model development

Use expanding folds for reproducible comparison and tuning.

### Final local confirmation

Use the frozen final holdout as a later-period check after development decisions are substantially fixed.

Do not repeatedly tune against the final holdout until it becomes another training signal.

If the team decides a different holdout usage protocol, that protocol must be documented and frozen **before** model comparison.

---

# 11. Fit/transform protocol for every fold

For each fold:

```text
1. Obtain fold train row IDs/indexes.
2. Obtain fold validation row IDs/indexes.
3. Build/fit training-only preprocessing state.
4. Fit any historical target-statistic transformer on fold train only.
5. Transform fold train.
6. Transform fold validation WITHOUT validation y.
7. Fit model on fold train transformed features.
8. Predict fold validation.
9. Calculate frozen overall metrics.
10. Calculate frozen segment metrics.
11. Store results with fold ID and date boundaries.
```

Anything that learns from data must obey fit scope, including:

- imputation statistics;
- category encodings that learn frequencies/targets;
- scalers;
- historical target aggregates;
- probability calibration when later tested;
- model fitting.

Pure deterministic transformations based on known row fields may be applied consistently without fitting.

---

# 12. Recommended implementation architecture

## `src/task1/validation.py`

Recommended components:

```python
@dataclass(frozen=True)
class HoldoutSplit:
    ...

@dataclass(frozen=True)
class TemporalFold:
    ...

class ExpandingDateSplitter:
    ...


def resolve_validation_date(...):
    ...


def sort_task1_history_chronologically(...):
    ...


def make_final_chronological_holdout(...):
    ...


def make_expanding_date_folds(...):
    ...


def assert_same_date_atomicity(...):
    ...


def validate_fold_feature_fit_scope(...):
    ...


def build_task1_validation_plan(...):
    ...
```

## `src/task1/metrics.py`

Recommended:

```python
def regression_metrics(...):
    ...


def lateness_probability_metrics(...):
    ...


def regression_segment_metrics(...):
    ...


def lateness_segment_metrics(...):
    ...


def expected_calibration_error(...):
    ...
```

Keep metric functions pure and model-agnostic.

---

# 13. Validation plan artifact

The local Phase 07 run should generate a private plan containing:

```text
validation_date source
history start/end
number of unique dates
development start/end
holdout start/end
holdout date count
holdout row count
fold count
for each fold:
    train start/end
    validation start/end
    train date count
    validation date count
    train row count
    validation row count
same-date integrity result
metric contract
segment contract
fit-dependent feature policy
```

Do not store model scores in Phase 07 because models are not yet being compared.

---

# 14. Tests — minimum required coverage

Create:

```text
tests/test_task1_validation.py
tests/test_task1_metrics.py
```

Use synthetic data only.

## DT-123 tests

- chronological sort;
- deterministic same-date tie behavior;
- invalid date failure;
- missing date failure.

## DT-124 tests

- latest period is holdout;
- development strictly earlier;
- same-date boundary atomicity;
- deterministic split;
- insufficient history failure.

## DT-125 tests

- exact configured fold count;
- expanding training period;
- validation moves forward;
- fold validation does not touch holdout;
- no train-validation date overlap;
- minimum training history enforced;
- deterministic result.

## DT-126 tests

- boundary date with many rows never split;
- all dates disjoint across each train/validation pair;
- same-date historical-target leakage rejected.

## Fit-scope leakage tests

Create a synthetic transformer that would leak if validation targets were supplied.

Prove the validation orchestration never passes validation targets into transform-time historical feature construction.

Test:

```text
train target changes → validation historical feature may change
validation target changes → validation historical feature MUST NOT change
```

This is a critical regression test.

## DT-127 regression metric tests

- perfect prediction;
- MAE hand calculation;
- RMSE hand calculation;
- median AE;
- p90 AE;
- negative prediction diagnostic;
- nonfinite rejected;
- length mismatch rejected.

## DT-128 probability metric tests

- perfect probability predictions;
- known log loss;
- known Brier;
- bounds enforced;
- NaN rejected;
- single-class fold does not crash;
- ROC-AUC unavailable flag when invalid;
- average precision handling;
- calibration error deterministic.

## DT-129 segment tests

- brand segments;
- depot segments;
- counts;
- low-support flag;
- single-class segment;
- missing group policy;
- forbidden target-derived segment rejected.

---

# 15. Edge cases and required handling

## 15.1 Date boundary on a busy day

Never split the day.

## 15.2 Sparse late events in one fold

Do not redraw the fold just to force class balance unless the frozen design itself is impossible.

Log loss/Brier remain primary.

Ranking metrics may be unavailable and must be marked clearly.

## 15.3 One class in a segment

Keep the segment.

Return valid probability metrics and mark AUC-style metrics unavailable.

## 15.4 Fold with too little initial history

Fail configuration validation or revise the split design **before** Phase 08.

Do not silently reduce fold count after seeing model results.

## 15.5 Missing optional segment field

If a segment such as road/traffic-derived context was disabled in prior phases, do not recreate it here.

Remove/disable that segment in config before freezing the phase.

## 15.6 Historical target features

A globally precomputed causal feature can still be unsafe for a multi-day validation window if it uses earlier validation labels.

Validation must fit the historical-statistic state on fold training only and transform all validation rows from that fixed state.

## 15.7 Categorical levels unseen in a fold train

The validation framework must permit later model/preprocessor code to encounter unseen validation categories without reading validation targets.

Do not merge train and validation merely to discover categories.

## 15.8 Final holdout peeking

Do not use final holdout scores to repeatedly tune feature definitions.

If a serious bug is discovered, fix the bug, document that the holdout was invalidated by the bug, and regenerate only under a transparent revised protocol.

## 15.9 Row order

Validation metrics should align by `delivery_id`/index, not rely on accidental DataFrame order after sorting or transformation.

## 15.10 Negative service prediction

Do not silently clip inside the metric function.

Report negative prediction count.

A later universally applied postprocessing rule may be evaluated, but it must be explicit and comparable across models.

---

# 16. Phase 07 global STOP conditions

`READY FOR PHASE 08` must remain **NO** if any of the following is unresolved:

- Phase 04 labels are not canonical;
- Phase 06 feature/leakage audit did not pass;
- validation date is ambiguous;
- any final holdout date also appears in development;
- any train date appears in its validation set;
- same-date rows are split across train/validation;
- expanding training history is not strictly past relative to validation;
- final holdout is used as a CV fold;
- fit-dependent preprocessing is learned from validation rows;
- historical target features can read validation labels;
- earlier validation labels are used to create later rows inside the same frozen validation window;
- regression metric contract is not frozen;
- probability metric contract is not frozen;
- model selection would rely primarily on threshold accuracy/F1 rather than probability quality;
- segment metrics omit sample support;
- a target/actual-outcome field is used as a segment or predictor input;
- tests fail;
- private split reports are tracked by Git;
- agent accesses restricted competition rows;
- local validation-plan build fails;
- independent review fails.

---

# 17. Phase 07 Definition of Done

Phase 07 passes only when:

- [ ] DT-123 PASS
- [ ] DT-124 PASS
- [ ] DT-125 PASS
- [ ] DT-126 PASS
- [ ] DT-127 PASS
- [ ] DT-128 PASS
- [ ] DT-129 PASS
- [ ] canonical validation date frozen
- [ ] chronological sort deterministic
- [ ] final holdout frozen
- [ ] final holdout uses latest dates
- [ ] final holdout excluded from expanding folds
- [ ] expanding folds frozen
- [ ] every fold trains only on earlier dates
- [ ] same-date atomicity passes everywhere
- [ ] fit-dependent feature policy frozen
- [ ] historical target features cannot use validation targets
- [ ] regression primary metric = MAE
- [ ] regression secondary metric includes RMSE
- [ ] lateness primary metric = log loss
- [ ] lateness secondary metric = Brier score
- [ ] ranking/calibration diagnostics documented
- [ ] segment fields frozen
- [ ] low-support segment policy frozen
- [ ] metric functions tested
- [ ] split functions tested
- [ ] full safe regression suite passes
- [ ] local validation plan generated successfully
- [ ] private outputs remain ignored
- [ ] independent review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 07 STATUS: PASS
READY FOR PHASE 08: YES
```

Do not automatically start Phase 08.

---

# 18. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-07-task1-validation
```

Recommended commits:

```text
feat(task1): add chronological validation date and ordering
feat(task1): add frozen chronological holdout splitter
feat(task1): add expanding date folds
fix(task1): enforce same-date split atomicity
test(task1): add validation leakage and fit-scope tests
feat(task1): freeze service regression metrics
feat(task1): freeze lateness probability metrics
feat(task1): add segment metric contract
docs(task1): document frozen validation protocol
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
python -m pip check
pytest -q

git status
```

Merge only after:

```text
LOCAL PHASE 07 VALIDATION PLAN: PASS
INDEPENDENT PHASE 07 REVIEW: PASS
```

---

# 19. Local execution contract

Recommended command:

```bash
python scripts/build_task1_validation_plan.py \
  --labels data/interim/task1_training_labels.csv \
  --features data/interim/task1_features_train.csv \
  --feature-registry configs/task1_features.yaml \
  --config configs/task1_validation.yaml \
  --output-dir reports/private/phase07_task1_validation
```

If the Phase 06 feature registry is stored elsewhere, use the actual tracked path rather than duplicating it.

### Safe console output

Success:

```text
PHASE 07 TASK 1 VALIDATION PLAN: PASS
Chronological ordering: PASS
Final holdout: PASS
Expanding folds: PASS
Same-date atomicity: PASS
Fit-dependent feature policy: PASS
Regression metric contract: PASS
Probability metric contract: PASS
Segment metric contract: PASS
Detailed validation plan written locally.
```

Failure:

```text
PHASE 07 TASK 1 VALIDATION PLAN: FAIL
Blocker codes:
- <RULE_CODE>
Detailed private report written locally.
```

Do not print private delivery IDs or row-level labels.

---

# 20. Enhanced Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 07 only.

PHASE:
Task 1 Validation Design

TASK RANGE:
DT-123 through DT-129

EXECUTION MODE:
High-risk controlled autonomous implementation.

You have permission to perform all SAFE engineering work required for Phase 07.

You MAY:
- edit/refactor Phase 07 code
- create configuration/docs/tests
- run targeted tests
- run the complete regression suite
- inspect stack traces
- fix ordinary implementation bugs automatically
- rerun tests until passing
- run python -m pip check
- inspect git status/diff
- self-review against the Definition of Done

Do NOT stop for ordinary coding errors that can be safely fixed.

STOP only for:
- official competition-rule ambiguity
- private/raw competition-data requirement
- unresolved cross-phase contract conflict
- validation leakage that cannot be removed safely
- a genuinely insufficient/invalid validation design
- a schema issue requiring human investigation

DO NOT START PHASE 08.

==================================================
READ FIRST
==================================================

Read completely:

1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. approved PHASE_00_COMPETITION_CONTRACT.md
3. approved PHASE_01_COMPETITION_CONTRACT.md
4. approved PHASE_02_COMPETITION_CONTRACT.md
5. approved PHASE_03_COMPETITION_CONTRACT.md
6. approved PHASE_04_COMPETITION_CONTRACT.md
7. approved PHASE_05_COMPETITION_CONTRACT.md
8. approved PHASE_06_COMPETITION_CONTRACT.md
9. PHASE_07_COMPETITION_CONTRACT.md
10. existing tracked Task 1 label/feature/leakage utilities

SOURCE PRIORITY:

Official organizer material
>
approved WayLoom master plan
>
approved phase contracts
>
implementation assumptions

==================================================
DATA SAFETY
==================================================

Do NOT inspect real competition rows inside the external-agent context.

Do NOT access:

data/raw/**
data/interim/**
reports/private/**

Use tracked code/config/docs and synthetic fixtures only.

The human will generate the real validation plan locally after implementation.

==================================================
OFFICIAL TASK 1 CONTEXT
==================================================

Task 1 predicts:

pred_service_min
pred_late_prob

Planned departure/travel/arrival are prediction-time information.
Actual journey/handling outcomes are historical-only.

The booklet does not prescribe the exact hidden evaluation metric.
Therefore the validation metrics in this phase are WayLoom engineering choices and MUST be frozen before model comparison.

Never allow direct model features:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag

==================================================
CREATE / UPDATE
==================================================

configs/task1_validation.yaml

src/task1/validation.py
src/task1/metrics.py

scripts/build_task1_validation_plan.py

docs/task1_validation_spec.md

tests/test_task1_validation.py
tests/test_task1_metrics.py

Keep private outputs under:

reports/private/phase07_task1_validation/**

==================================================
DT-123 — CHRONOLOGICAL SORT
==================================================

Use canonical validation date:

route_date

Use dispatch_date only as a fallback/consistency check if needed by existing code.

Rationale:
Task 1 validation should reflect the date the planned delivery/service occurs, especially for deferred orders.

Implement deterministic chronological sorting.

Requirements:
- parse date strictly
- reject missing/invalid validation date
- sort ascending by route_date
- deterministic tie-breakers only for reproducibility
- preserve source traceability
- do not use target values for sorting
- same-date row ordering must not be interpreted as within-day target availability

Run targeted synthetic tests.

==================================================
DT-124 — FINAL CHRONOLOGICAL HOLDOUT
CRITICAL GATE
==================================================

Implement a final latest-period holdout.

Recommended frozen default:

strategy = last_calendar_days
calendar_days = 42
same_date_atomic = true

This 42-day value is a WayLoom engineering choice, not an organizer requirement.

Requirements:
- split by dates, not rows
- development dates strictly earlier than holdout dates
- no date overlap
- no random shuffle
- holdout not used to fit preprocessing/features/models
- fit-dependent transformations fit on development only
- deterministic boundaries
- clear insufficient-history error

Do not use holdout as part of expanding CV.

Run tests.

If overlap occurs:
STOP.

==================================================
DT-125 — EXPANDING TIME FOLDS
CRITICAL GATE
==================================================

Implement expanding chronological folds inside the DEVELOPMENT period only.

Recommended default:

n_folds = 4
validation_calendar_days = 42
gap_calendar_days = 0
minimum_training_calendar_days = 180
same_date_atomic = true

These are configurable engineering choices.

For every fold require:

max(train_date) < min(validation_date)
train_dates ∩ validation_dates = empty
validation_dates ∩ final_holdout_dates = empty

Across folds:
- training history expands
- validation windows move forward
- result deterministic

CRITICAL FIT-SCOPE RULE:

Any fit-dependent preprocessing or historical target-statistic feature must be FIT on fold training only.

Validation targets must never be passed into feature transform.

Do not let earlier rows inside the validation window update historical target features for later validation rows.
Treat the full validation window as unseen.

Add dedicated synthetic leakage tests.

==================================================
DT-126 — SAME-DATE ATOMICITY
CRITICAL GATE
==================================================

Ensure ALL rows from one route_date belong to one side of every split.

Never split by row index if it divides a date.

Assertions:

train_dates.isdisjoint(validation_dates)
development_dates.isdisjoint(holdout_dates)

Historical target statistics must use:

historical_date < current_date

never:

historical_date <= current_date

Add tests with many rows on boundary dates.

Any date overlap = HARD FAILURE.

==================================================
DT-127 — FREEZE SERVICE REGRESSION METRICS
==================================================

Freeze:

PRIMARY:
MAE

SECONDARY:
RMSE
median_absolute_error
p90_absolute_error

DIAGNOSTIC:
negative_prediction_count
nonfinite_prediction_count

Metric functions must:
- not round internally
- reject nonfinite predictions
- not silently clip negative service predictions
- report negative count
- be deterministic

Do not change metrics per model.

Implement tests using hand-calculated examples.

==================================================
DT-128 — FREEZE LATENESS PROBABILITY METRICS
==================================================

Because official output is a probability, freeze probability-quality metrics.

PRIMARY:
log_loss

SECONDARY:
brier_score

DIAGNOSTICS:
roc_auc
average_precision
calibration_error / ECE

Do NOT use accuracy/F1 at threshold 0.5 as primary model-selection metrics.

Probability rules:
- finite
- 0 <= p <= 1
- do not silently repair invalid probabilities

Use epsilon only internally for stable logarithm where necessary.

Single-class fold:
- log loss / Brier should still be handled correctly
- AUC-style diagnostics may be unavailable
- do not crash
- return explicit unavailable status

Add hand-calculated tests.

==================================================
DT-129 — SEGMENT METRICS
==================================================

Freeze segment fields before modelling.

Recommended:

brand
depot
district
dock_type
temp_requirement
is_first_stop
monsoon
planned_slack_bin

Regression per segment:

n
MAE
RMSE
median_absolute_error
p90_absolute_error

Probability per segment:

n
positive_count
negative_count
observed_late_rate
log_loss
brier_score

When support permits:

roc_auc
average_precision

Default support policy:

minimum_n = 30
minimum_positive_for_auc = 5
minimum_negative_for_auc = 5

Small groups are NOT hidden.
Flag:
LOW_SUPPORT

Segment metrics are diagnostics.
Overall metrics remain the primary comparison contract.

Do not create model-selection rules such as:
"winner on brand Fresh = overall winner".

==================================================
VALIDATION/FIT PROTOCOL
==================================================

Encode/document this protocol for every future fold:

1. create train/validation indexes from dates
2. fit preprocessing on train only
3. fit historical target-statistic transformer on train only
4. transform train
5. transform validation WITHOUT validation y
6. fit model on train
7. predict validation
8. score frozen overall metrics
9. score frozen segment metrics
10. store fold/date metadata

Anything that learns statistics must obey fold fit scope.

==================================================
CRITICAL LEAKAGE TEST
==================================================

Create a synthetic test proving:

changing TRAIN targets may legitimately change validation historical features

BUT

changing VALIDATION targets MUST NOT change validation features

Also prove:

same-date validation target values never influence one another.

If this test fails:
STOP.

==================================================
TESTING AUTONOMY
==================================================

After each critical gate:
1. run targeted tests
2. inspect failure
3. fix ordinary implementation bug
4. rerun failing test
5. rerun Phase 07 tests

After all tasks:
run the full safe regression suite.

At minimum include:

tests/test_project_setup.py
tests/test_data_inventory.py
tests/test_data_quality.py
tests/test_schema_assertions.py
tests/test_task1_labels.py
tests/test_task1_eda.py
tests/test_task1_features.py
tests/test_task1_historical_features.py
tests/test_task1_feature_leakage.py
tests/test_task1_validation.py
tests/test_task1_metrics.py

Then:

python -m pip check

git status
git diff

Ensure no private competition artifacts are staged.

==================================================
LOCAL REAL-DATA PLAN COMMAND
==================================================

Implement but do not execute against private competition data in the external-agent context:

python scripts/build_task1_validation_plan.py \
  --labels data/interim/task1_training_labels.csv \
  --features data/interim/task1_features_train.csv \
  --feature-registry configs/task1_features.yaml \
  --config configs/task1_validation.yaml \
  --output-dir reports/private/phase07_task1_validation

If the actual Phase 06 registry path differs, use the existing canonical tracked path.

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-123 through DT-129 all implemented
validation date frozen
holdout frozen
holdout latest-period only
holdout excluded from CV
expanding folds chronological
same-date atomicity zero violations
fit-dependent features train-only
validation targets inaccessible during transform
same-date target leakage impossible
MAE primary regression metric
RMSE secondary regression metric
log loss primary probability metric
Brier secondary probability metric
segment metrics frozen
single-class handling tested
full regression suite passes
pip check passes
private paths not staged

==================================================
RETURN ONLY
==================================================

PHASE:
07 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-123 READY / FAIL
DT-124 READY / FAIL
DT-125 READY / FAIL
DT-126 READY / FAIL
DT-127 READY / FAIL
DT-128 READY / FAIL
DT-129 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

FINAL HOLDOUT INTEGRITY:
PASS / FAIL

EXPANDING FOLD INTEGRITY:
PASS / FAIL

SAME-DATE ATOMICITY:
PASS / FAIL

HISTORICAL FEATURE FIT-SCOPE:
PASS / FAIL

REGRESSION METRIC CONTRACT:
PASS / FAIL

PROBABILITY METRIC CONTRACT:
PASS / FAIL

SEGMENT METRIC CONTRACT:
PASS / FAIL

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local validation-plan command.

PHASE 07 STATUS:
AWAITING LOCAL VALIDATION PLAN

READY FOR PHASE 08:
NO

Then STOP.
Do not begin Phase 08.
```

---

# 21. Enhanced independent Phase 07 review prompt

Use this in a **fresh Cursor chat** after the human local validation-plan run passes.

```text
Perform an independent review of completed WayLoom Datathon Phase 07.

DO NOT:
- open data/raw
- open data/interim
- open reports/private
- inspect private row-level split data
- run models
- start Phase 08
- modify code initially

READ:

1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. PHASE_07_COMPETITION_CONTRACT.md
3. configs/task1_validation.yaml
4. src/task1/validation.py
5. src/task1/metrics.py
6. scripts/build_task1_validation_plan.py
7. docs/task1_validation_spec.md
8. tests/test_task1_validation.py
9. tests/test_task1_metrics.py
10. relevant tracked Phase 06 feature/leakage code
11. .gitignore
12. .cursorignore

HUMAN LOCAL CONTROL RESULT:

LOCAL PHASE 07 VALIDATION PLAN: <PASS / FAIL>
FINAL HOLDOUT INTEGRITY: <PASS / FAIL>
EXPANDING FOLDS: <PASS / FAIL>
SAME-DATE VIOLATIONS: <0 / number>
FIT-SCOPE LEAKAGE TEST: <PASS / FAIL>

Do not ask for private split manifests or delivery IDs.

AUDIT EVERY TASK:

DT-123
- canonical date is appropriate for future delivery prediction
- sort is chronological and deterministic
- same-date tie order is only bookkeeping

DT-124
- latest-period holdout
- date-based boundary
- zero date overlap
- holdout isolated from development
- no random split

DT-125
- expanding folds only inside development
- train strictly earlier than validation
- training grows
- validation moves forward
- holdout excluded
- deterministic

DT-126
- same-date atomicity enforced everywhere
- historical target features use strict earlier-date logic

DT-127
- MAE primary
- RMSE secondary
- robust/tail diagnostics implemented
- negative predictions not silently clipped by metric layer

DT-128
- log loss primary
- Brier secondary
- probability bounds enforced
- ROC-AUC/AP diagnostic only
- single-class folds handled safely
- no threshold accuracy/F1 as primary metric

DT-129
- frozen business-relevant segments
- support counts included
- low-support flags
- single-class segment handling
- segment metrics remain diagnostic

CRITICAL FIT-SCOPE AUDIT:

Confirm validation orchestration cannot pass validation labels into:
- historical target-statistic fitting
- preprocessing fitting
- category statistics
- calibration fitting
- any fit-dependent transformer

Confirm the synthetic test proves:
changing validation y does not change validation X.

DATA SAFETY:
- no raw records in tests/docs
- no private split output tracked
- no real delivery IDs in source fixtures

RUN SAFE TESTS ONLY:

pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py tests/test_task1_labels.py tests/test_task1_eda.py tests/test_task1_features.py tests/test_task1_historical_features.py tests/test_task1_feature_leakage.py tests/test_task1_validation.py tests/test_task1_metrics.py

python -m pip check

git status

Do not run real model training.

RETURN:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

CHRONOLOGICAL DESIGN:
PASS / FAIL

FINAL HOLDOUT:
PASS / FAIL

EXPANDING FOLDS:
PASS / FAIL

SAME-DATE PROTECTION:
PASS / FAIL

FIT-SCOPE / LEAKAGE:
PASS / FAIL

REGRESSION METRICS:
PASS / FAIL

PROBABILITY METRICS:
PASS / FAIL

SEGMENT METRICS:
PASS / FAIL

SYNTHETIC TESTS:
PASS / FAIL

HUMAN LOCAL PLAN:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-123: PASS/FAIL
DT-124: PASS/FAIL
DT-125: PASS/FAIL
DT-126: PASS/FAIL
DT-127: PASS/FAIL
DT-128: PASS/FAIL
DT-129: PASS/FAIL

PHASE 07 REVIEW:
PASS / FAIL

READY FOR PHASE 08:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not start Phase 08.
```

---

# 22. Local execution instructions

After Cursor finishes implementation and all safe tests:

## Step 1 — verify protected outputs

```bash
git status
git check-ignore -v reports/private/phase07_task1_validation/validation_summary.json
```

## Step 2 — run Phase 07 tests locally

```bash
pytest -q tests/test_task1_validation.py tests/test_task1_metrics.py
```

Optionally run the full suite:

```bash
pytest -q
```

## Step 3 — generate the validation plan locally

```bash
python scripts/build_task1_validation_plan.py \
  --labels data/interim/task1_training_labels.csv \
  --features data/interim/task1_features_train.csv \
  --feature-registry configs/task1_features.yaml \
  --config configs/task1_validation.yaml \
  --output-dir reports/private/phase07_task1_validation
```

PowerShell one-line version:

```powershell
python scripts/build_task1_validation_plan.py --labels data/interim/task1_training_labels.csv --features data/interim/task1_features_train.csv --feature-registry configs/task1_features.yaml --config configs/task1_validation.yaml --output-dir reports/private/phase07_task1_validation
```

## Step 4 — inspect the private report locally

Confirm:

```text
chronological order valid
final holdout nonempty
holdout latest period
holdout overlap = 0
expanding folds expected count
train/validation date overlap = 0
same-date violations = 0
holdout contamination = 0
fit-dependent feature policy = PASS
metric contract frozen
segment contract frozen
```

## Step 5 — return sanitized result only

```text
LOCAL PHASE 07 VALIDATION PLAN: PASS
FINAL HOLDOUT INTEGRITY: PASS
EXPANDING FOLDS: PASS
SAME-DATE VIOLATIONS: 0
FIT-SCOPE LEAKAGE TEST: PASS
```

Then run the independent review prompt.

---

# 23. Phase 07 completion record template

```markdown
# Phase 07 Completion Record

## Tasks

- [ ] DT-123
- [ ] DT-124
- [ ] DT-125
- [ ] DT-126
- [ ] DT-127
- [ ] DT-128
- [ ] DT-129

## Split contract

- Canonical validation date: __________________
- Final holdout strategy: _____________________
- Final holdout window: _______________________
- Expanding folds: ____________________________
- Fold validation window: _____________________
- Same-date atomicity: PASS / FAIL

## Metric contract

Regression primary:
- MAE

Regression secondary:
- RMSE
- Median AE
- P90 absolute error

Lateness primary:
- Log loss

Lateness secondary:
- Brier score

Diagnostics:
- ROC-AUC
- Average precision
- Calibration error

## Safety

- Validation labels used in feature fitting: NO
- Same-date target statistics used: NO
- Final holdout used during CV fitting: NO
- Actual journey fields used as model inputs: NO
- Private split outputs committed: NO

## Tests

- Phase 07 tests: PASS / FAIL
- Full regression suite: PASS / FAIL
- pip check: PASS / FAIL

## Local plan

- Local validation-plan generation: PASS / FAIL
- Holdout overlap: 0 / nonzero
- Same-date violations: 0 / nonzero
- Fold chronology: PASS / FAIL

## Review

- Independent review: PASS / FAIL

## Verdict

PHASE 07 STATUS: PASS / FAIL
READY FOR PHASE 08: YES / NO
```

---

# 24. Final Phase 07 checklist

Before Phase 08:

- [ ] Phase 04 labels passed.
- [ ] Phase 06 feature/leakage gate passed.
- [ ] all DT-123–DT-129 implemented.
- [ ] route/service date is the frozen validation date.
- [ ] history sorted chronologically.
- [ ] final latest-period holdout frozen.
- [ ] final holdout never appears in expanding folds.
- [ ] expanding folds use earlier training and later validation.
- [ ] same-date rows never cross split boundaries.
- [ ] historical target statistics are fold-fit only.
- [ ] validation targets cannot affect validation feature values.
- [ ] preprocessing fit scope is training-only.
- [ ] MAE frozen as primary regression metric.
- [ ] RMSE frozen as secondary regression metric.
- [ ] log loss frozen as primary lateness metric.
- [ ] Brier frozen as secondary lateness metric.
- [ ] ranking/calibration metrics are diagnostics.
- [ ] segment fields frozen.
- [ ] segment sample support rules frozen.
- [ ] single-class segment/fold behavior tested.
- [ ] tests pass.
- [ ] local validation plan passes.
- [ ] private outputs ignored.
- [ ] independent review passes.
- [ ] no unresolved STOP condition remains.

Only then:

```text
PHASE 07 STATUS: PASS
READY FOR PHASE 08: YES
```

Do not automatically begin Phase 08.
