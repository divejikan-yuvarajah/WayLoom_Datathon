# PHASE 08 — Task 1 Baseline Modelling

> **Requested filename:** `PHASE_08_COMPETITION_CONTRACT.md`  
> **Canonical phase name:** **Phase 08 — Task 1 Baselines**  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-130 → DT-137**  
> **Task count:** 8  
> **Default priority:** P1  
> **Phase dependency:** Phase 07 must have passed  
> **Recommended execution style:** **Full-phase baseline tooling implementation + autonomous safe testing/debugging + local private experiment run + independent review**  
> **Phase gate:** Simple, reproducible Task 1 baselines are evaluated under the frozen Phase 07 validation contract and stored as the minimum benchmark that every advanced model in Phase 09 must beat or justify exceeding.

---

# 1. Purpose of Phase 08

Phase 08 creates the **reference performance floor** for Task 1.

The project now has:

- audited data;
- canonical Task 1 labels;
- leakage-safe feature engineering;
- a frozen chronological validation design;
- frozen regression and probability metrics.

Before training advanced tree models, the team must establish how well very simple methods perform.

This phase answers:

- How well does a single global service-time estimate work?
- Does brand alone improve service prediction?
- Does brand + dock type improve the service baseline further?
- How well does the global historical late rate perform as a probability forecast?
- Does a grouped late-rate forecast improve on the constant probability?
- How much value does a simple linear model extract from prediction-time-safe features?
- How much value does a simple logistic model extract from the same information?
- Are later advanced models genuinely better than transparent baselines under the **same folds and metrics**?

Phase 08 is **not** a hyperparameter-tuning phase and is **not** where final Task 1 models are selected.

---

# 2. Official Task 1 requirements that constrain Phase 08

The official competition requires predictions for each Task 1 `delivery_id`:

```text
pred_service_min
pred_late_prob
```

The historical targets are:

```text
service_minutes
late_flag
```

Prediction-time information may include planned route/order/reference context. Historical actual journey and handling outcomes are not available at prediction time.

Therefore no baseline model may directly use:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag
```

except that `service_minutes` and `late_flag` are used as **training targets**.

The competition also prohibits using prohibited pretrained/fully automated modelling approaches. The baselines in this phase are trained from the supplied competition history using ordinary statistical/scikit-learn style models and are not pretrained models.

The exact local validation metrics are not prescribed by the organizer. Phase 07 froze the WayLoom engineering contract:

### Service regression

Primary:

```text
MAE
```

Secondary:

```text
RMSE
median absolute error
P90 absolute error
```

### Lateness probability

Primary:

```text
log loss
```

Secondary:

```text
Brier score
```

Diagnostics where valid:

```text
ROC-AUC
Average Precision
Calibration error
```

Phase 08 must **reuse these metrics exactly**. Do not redefine them inside the baseline code.

---

# 3. Phase 07 validation contract is immutable here

Phase 08 must import/reuse the Phase 07 validation plan rather than creating new splits.

Required invariants:

```text
chronological ordering
latest-period final holdout
expanding chronological development folds
same-date atomicity
fit-on-train / transform-validation scope
validation targets unavailable to feature construction
```

## Final holdout policy

The final chronological holdout remains **locked** during Phase 08.

Do not use it to:

- choose between baselines;
- choose feature subsets;
- alter preprocessing;
- alter grouped-baseline keys;
- tune linear/logistic settings;
- inspect repeated performance.

Phase 08 baseline benchmarking is performed on the **Phase 07 development folds**.

The final holdout is preserved for later model-selection/final validation work according to the approved workflow.

---

# 4. Data-safety and agent-access model

The agent may have broad autonomy for **safe engineering work**.

## Agent may

- create/edit/refactor Phase 08 code;
- create/edit tests;
- create synthetic fixtures;
- run pytest;
- run `python -m pip check`;
- inspect stack traces;
- fix normal code failures automatically;
- rerun targeted and full regression tests;
- inspect Git status/diff;
- validate configs;
- create safe synthetic baseline artifacts;
- perform self-review against this contract.

## Agent must not

- inspect real competition rows in `data/raw/**`;
- inspect private engineered competition matrices in `data/interim/**`;
- inspect private experiment results in `reports/private/**`;
- run the real-data baseline experiment through an external model/provider context unless the team has independently confirmed an organizer-approved/local-only execution path;
- transmit official competition data or row-level derivatives.

## Human local stage

The human runs the final baseline experiment locally.

Recommended private output location:

```text
reports/private/phase08_task1_baselines/
```

Return only sanitized control results such as:

```text
LOCAL PHASE 08 BASELINES: PASS
ALL DEVELOPMENT FOLDS COMPLETED: YES
FINAL HOLDOUT ACCESSED: NO
LEAKAGE AUDIT: PASS
BASELINE RESULT TABLE WRITTEN: YES
```

Do not paste private metric tables into the coding agent unless that workflow is explicitly approved.

---

# 5. Phase 08 task registry

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-130** | [E] | P1 | Phase 07 | Build global median service baseline |
| [ ] | **DT-131** | [E] | P1 | Phase 07 | Build brand median service baseline |
| [ ] | **DT-132** | [E] | P1 | Phase 07 | Build brand+dock service baseline |
| [ ] | **DT-133** | [E] | P1 | Phase 07 | Build constant late-probability baseline |
| [ ] | **DT-134** | [E] | P1 | Phase 07 | Build grouped late-rate baseline |
| [ ] | **DT-135** | [E] | P1 | Phase 07 | Build linear regression baseline |
| [ ] | **DT-136** | [E] | P1 | Phase 07 | Build logistic regression baseline |
| [ ] | **DT-137** | [E] | P1 | Phase 07 | Store baseline experiment results |

**Phase complete:** [ ]  
**READY FOR PHASE 09:** NO

---

# 6. Required repository additions

Recommended tracked files:

```text
src/task1/
├── baselines.py
└── baseline_preprocessing.py

scripts/
└── run_task1_baselines.py

configs/
└── task1_baselines.yaml

experiments/
└── README.md

docs/
└── task1_baseline_spec.md

tests/
├── test_task1_baselines.py
└── test_task1_baseline_preprocessing.py
```

Private local outputs:

```text
reports/private/phase08_task1_baselines/
├── run_manifest.json
├── fold_results.csv
├── model_summary.csv
├── regression_baselines.json
├── lateness_baselines.json
├── segment_diagnostics.csv
├── convergence_warnings.json
├── leakage_check.json
└── phase08_baseline_report.md
```

Optional private fold artifacts, only if needed for reproducibility/debugging:

```text
reports/private/phase08_task1_baselines/fold_artifacts/
```

Do not commit private experiment outputs.

---

# 7. Frozen baseline feature policy

Phase 08 has two kinds of baselines.

## 7.1 Statistical baselines

These use only the target plus a very small grouping key learned from each fold's training period.

Examples:

```text
global service median
brand service median
brand + dock service median
global late rate
brand + dock late rate
```

They do **not** require full feature preprocessing.

## 7.2 Linear/logistic baselines

These use a documented **simple baseline feature subset** from Phase 06.

Recommended policy:

- include prediction-time-safe low/medium-cardinality categoricals;
- include prediction-time-safe numeric engineered features;
- exclude raw row identifiers;
- exclude raw route IDs as identifiers;
- exclude target-derived fields;
- exclude all actual journey fields;
- by default exclude Phase 06 target-history features from the simple linear/logistic baseline so the baseline remains transparent and low-complexity;
- if historical target features are intentionally included, they must obey the Phase 07 fold fit-scope contract and the choice must be frozen in config before running experiments.

Recommended default baseline feature families:

```text
order size
brand
district
depot
temperature requirement
dock/access context
vehicle static context
route position
planned route count/context
planned distance
planned travel duration
planned arrival/departure time features
planned slack
planned early-wait estimate
calendar/payday/festival/monsoon context
service allowance
safe order-size ratios
planned route totals/utilization
optional road/traffic context only if approved and enabled
```

Recommended exclusions:

```text
delivery_id
leg_id
route_id
raw outlet_id by default
raw vehicle_id by default
actual_* fields
service_start_dt
service_minutes
late_flag
```

High-cardinality IDs are excluded from the default linear/logistic baseline to keep it simple and avoid a large sparse design matrix masquerading as a basic baseline.

---

# 8. Recommended `task1_baselines.yaml`

Example:

```yaml
version: 1

validation:
  use_phase07_plan: true
  use_final_holdout: false

service_baselines:
  global_median:
    enabled: true

  brand_median:
    enabled: true
    group_keys: [brand]
    fallback: global_median

  brand_dock_median:
    enabled: true
    group_keys: [brand, dock_type]
    fallback_order:
      - brand_median
      - global_median

lateness_baselines:
  constant_probability:
    enabled: true
    estimator: training_mean

  grouped_rate:
    enabled: true
    group_keys: [brand, dock_type]
    fallback_order:
      - brand_rate
      - global_rate
    smoothing:
      enabled: false

linear_regression:
  enabled: true
  estimator: LinearRegression
  include_historical_target_features: false

logistic_regression:
  enabled: true
  estimator: LogisticRegression
  solver: lbfgs
  max_iter: 2000
  class_weight: null
  C: 1.0
  random_state: 42
  include_historical_target_features: false

preprocessing:
  numeric_imputer: median
  scale_numeric: true
  categorical_missing_token: __MISSING__
  categorical_encoder: one_hot
  handle_unknown: ignore

metrics:
  use_phase07_contract: true

artifacts:
  private_output_dir: reports/private/phase08_task1_baselines
```

Important:

- no hyperparameter search;
- no class-weight search;
- no threshold tuning;
- no calibration fitting;
- no final holdout scoring;
- no feature-selection search.

---

# 9. Common fold execution protocol

Every baseline must be evaluated on the same Phase 07 development folds.

For each fold:

```text
1. obtain train indexes
2. obtain validation indexes
3. verify train dates < validation dates
4. verify same-date atomicity
5. verify final holdout rows absent
6. fit baseline/preprocessor on TRAIN only
7. predict VALIDATION
8. calculate frozen Phase 07 metrics
9. calculate frozen segment diagnostics
10. store aggregate fold results privately
```

For fit-dependent Phase 06 features, if any are enabled:

```text
fit feature state on fold train only
transform fold train
transform validation without validation targets
```

Changing validation targets must not change validation features.

---

# 10. Detailed task specifications

---

## DT-130 — Build global median service baseline

**Mark:** [E]  
**Priority:** P1

### Objective

Create the simplest robust regression reference.

### Fold training rule

For each Phase 07 fold:

```python
baseline_value = median(y_service_train)
```

For every validation row:

```python
pred_service_min = baseline_value
```

### Why median

`service_minutes` may be right-skewed and MAE is the primary regression metric.

The median is the natural constant predictor for absolute-error loss.

This is a WayLoom engineering rationale, not an organizer-prescribed model.

### Requirements

- fit only on fold training labels;
- validation labels must not influence the median;
- no holdout labels;
- no clipping/rounding;
- prediction finite and nonnegative if training labels are valid;
- one prediction per validation row;
- reuse Phase 07 regression metrics.

### Recommended API

```python
class GlobalMedianServiceBaseline:
    def fit(self, y): ...
    def predict(self, n_rows): ...
```

or a small scikit-learn-compatible estimator.

### Tests

- known odd-count median;
- known even-count median;
- validation y change does not change predictions;
- deterministic;
- empty training labels fail clearly;
- NaN/nonfinite training target rejected.

### Definition of Done

- [ ] fold-train median only;
- [ ] validation predictions created;
- [ ] frozen regression metrics produced;
- [ ] no final holdout accessed.

### STOP conditions

Stop if the baseline value uses validation/holdout labels.

---

## DT-131 — Build brand median service baseline

**Mark:** [E]  
**Priority:** P1

### Objective

Test whether a single prediction-time-safe category adds useful service-time signal over the global median.

### Fold fit

On fold training data:

```text
median service by brand
```

Official brand values:

```text
Fresh
Style
Tech
```

### Validation prediction

For each validation row:

```text
if brand seen in fold train:
    predict fold-train brand median
else:
    predict fold-train global median
```

### Critical leakage rule

Do not calculate brand medians from the full historical dataset before fold splitting.

Correct:

```text
split → fit group medians on train → predict validation
```

Wrong:

```text
full-data groupby → attach median → split
```

### Tests

- correct medians;
- unseen brand fallback;
- validation targets do not influence group medians;
- deterministic predictions;
- no missing output.

### Definition of Done

- [ ] train-only brand statistics;
- [ ] global fallback;
- [ ] metrics stored.

---

## DT-132 — Build brand+dock service baseline

**Mark:** [E]  
**Priority:** P1

### Objective

Create a slightly richer transparent service baseline using known handling context.

### Default group

```text
brand + dock_type
```

Official dock categories:

```text
rear_dock
street
mall_bay
```

### Fold fit hierarchy

Compute from fold training only:

```text
1. brand + dock median
2. brand median
3. global median
```

### Validation prediction hierarchy

```text
seen brand+dock
    → group median
otherwise seen brand
    → brand median
otherwise
    → global median
```

### Why fallback matters

A validation group can be absent from an earlier fold even if it exists later in history.

Do not look forward to discover its target median.

### No smoothing required

This baseline should remain simple.

Do not add empirical-Bayes smoothing unless explicitly added as a new challenger in a later approved task.

### Tests

- seen exact group;
- unseen dock within seen brand;
- unseen brand;
- missing dock token policy;
- no validation-target influence.

### Definition of Done

- [ ] hierarchical train-only fallback;
- [ ] one prediction per row;
- [ ] metrics generated.

---

## DT-133 — Build constant late-probability baseline

**Mark:** [E]  
**Priority:** P1

### Objective

Create the simplest valid probability forecast for `late_flag`.

### Fold fit

```python
p_late = mean(y_late_train)
```

### Validation prediction

Every validation row receives:

```text
pred_late_prob = p_late
```

### Important probability rule

The model output itself remains the raw training late rate.

Do not manually push it away from 0 or 1 merely to improve log loss.

The metric function may use a tiny numerical epsilon internally when evaluating logarithms, as frozen in Phase 07.

### Single-class training fold

If a fold contains all 0 or all 1:

```text
p_late = 0 or 1
```

This is a valid empirical constant forecast.

The fold design should not be redrawn just to avoid it.

### Tests

- known probability;
- all-zero train;
- all-one train;
- validation target mutation does not change probability;
- output within [0,1].

### Definition of Done

- [ ] training-only late rate;
- [ ] valid probability output;
- [ ] frozen probability metrics produced.

---

## DT-134 — Build grouped late-rate baseline

**Mark:** [E]  
**Priority:** P1

### Objective

Test whether a simple grouped historical rate beats the constant probability while remaining interpretable.

### Frozen default grouping

Recommended:

```text
brand + dock_type
```

because both fields are prediction-time safe and the same grouping is used in the service baseline.

### Fold fit hierarchy

Compute from training only:

```text
brand + dock late rate
brand late rate
global late rate
```

### Validation fallback

```text
seen brand+dock
    → group rate
else seen brand
    → brand rate
else
    → global rate
```

### No smoothing by default

Keep the primary baseline transparent.

Raw group rates may be 0 or 1.

Do not add smoothing after seeing validation performance.

If smoothing is later tested, it must be a separately named experiment under an approved later modelling task.

### Small groups

Do not suppress a group prediction because its sample size is small.

Instead store the fold-train group count for diagnostics.

### Tests

- correct grouped rate;
- group rate 0;
- group rate 1;
- brand fallback;
- global fallback;
- validation targets do not affect rates;
- output finite and within [0,1].

### Definition of Done

- [ ] grouped train-only probabilities;
- [ ] deterministic fallback;
- [ ] metrics generated.

---

## DT-135 — Build linear regression baseline

**Mark:** [E]  
**Priority:** P1

### Objective

Create a simple supervised regression benchmark using prediction-time-safe engineered features.

### Estimator

Default:

```text
sklearn.linear_model.LinearRegression
```

No hyperparameter tuning.

Do not automatically replace it with Ridge/Lasso after looking at validation results.

A regularized linear challenger may be added later only if explicitly approved as an additional model experiment.

### Baseline feature subset

Use the Phase 06 registry.

Default policy:

```text
model_candidate = true
prediction_time_safe = true
requires_fit = false
```

plus explicitly allowed safe engineered fields.

By default exclude:

```text
raw identifiers
historical target-statistic features
training actual fields
target-derived fields
```

### Preprocessing

Build preprocessing **inside the fold**.

#### Numeric

Recommended:

```text
SimpleImputer(strategy="median")
StandardScaler()
```

The imputer/scaler are fit on fold train only.

#### Categorical

Recommended:

```text
SimpleImputer(strategy="constant", fill_value="__MISSING__")
OneHotEncoder(handle_unknown="ignore")
```

Encoder categories are learned from fold train only.

### Sparse/dense compatibility

Ensure the chosen sklearn version and pipeline produce a matrix compatible with `LinearRegression`.

Do not densify an enormous sparse matrix blindly.

If a dense conversion would be unsafe, adjust the baseline preprocessing implementation while preserving the frozen estimator intent and document the engineering choice.

### Negative predictions

Linear regression can predict negative service minutes.

During Phase 08 evaluation:

- do not silently clip negative predictions;
- evaluate raw predictions;
- record `negative_prediction_count` using Phase 07 diagnostics.

Submission-time physical constraints are handled later.

### Metrics

Use exactly the Phase 07 regression contract.

### Tests

- preprocessing fit only on train;
- unseen validation category handled;
- numeric missing value handled;
- forbidden feature rejected;
- train/validation columns aligned;
- predictions finite;
- negative prediction diagnostic preserved;
- deterministic synthetic fit/predict.

### Definition of Done

- [ ] fixed simple linear model;
- [ ] fold-safe preprocessing;
- [ ] no target-history by default;
- [ ] frozen metrics produced;
- [ ] no holdout access.

### STOP conditions

Stop if validation rows influence imputation/scaling/encoding fit.

---

## DT-136 — Build logistic regression baseline

**Mark:** [E]  
**Priority:** P1

### Objective

Create a simple supervised probability benchmark using prediction-time-safe features.

### Estimator

Default fixed configuration:

```python
LogisticRegression(
    C=1.0,
    class_weight=None,
    max_iter=2000,
    solver="lbfgs",
    random_state=42,
)
```

If the installed sklearn solver/version requires a technical compatibility adjustment, document it without turning Phase 08 into a tuning exercise.

### No class rebalancing

Do not automatically use:

```text
class_weight="balanced"
oversampling
undersampling
SMOTE
```

because Phase 08 is establishing an unmodified baseline.

### Preprocessing

Use the same fold-safe preprocessing contract as DT-135.

### Output

Use:

```python
predict_proba(X_valid)[:, 1]
```

Do not use hard class predictions for the primary Task 1 baseline evaluation.

### Probability rules

Predictions must be:

```text
finite
0 <= p <= 1
```

Do not threshold them for the primary metric.

### Convergence

Capture convergence warnings.

A convergence warning is not something to ignore silently.

Preferred process:

1. use the frozen baseline preprocessing;
2. use sufficiently large fixed `max_iter`;
3. if convergence still fails, record it;
4. make only a minimal technical correction that preserves the baseline model family;
5. do not tune `C` based on validation performance in Phase 08.

### Single-class fold training

If a training fold has only one class, scikit-learn logistic regression cannot fit normally.

Do not redraw the fold automatically.

Record a clear baseline failure for that fold and rely on the constant/grouped probability baselines, unless the Phase 07 contract explicitly provides a sanctioned handling policy.

### Tests

- output probabilities;
- unseen validation category;
- train-only preprocessing;
- no validation y access;
- class_weight remains null;
- no resampling;
- single-class fold handled explicitly;
- convergence warning captured;
- invalid probability rejected.

### Definition of Done

- [ ] fixed logistic baseline;
- [ ] `predict_proba` used;
- [ ] no class rebalancing;
- [ ] frozen probability metrics produced;
- [ ] convergence behavior recorded.

---

## DT-137 — Store baseline experiment results

**Mark:** [E]  
**Priority:** P1

### Objective

Create the permanent private benchmark record that Phase 09 must compare against.

### Required experiment identity

Every run should record:

```text
experiment_id
phase
created_at
code_version / git commit if available
config hash or config snapshot
validation-plan version
feature-registry version
random seed
library versions
```

### Required per-fold result fields

Recommended:

```text
experiment_id
model_name
target
fold_id
train_start_date
train_end_date
validation_start_date
validation_end_date
train_n
validation_n
metric_name
metric_value
```

### Regression baseline names

Use stable names such as:

```text
service_global_median
service_brand_median
service_brand_dock_median
service_linear_regression
```

### Probability baseline names

```text
late_constant_probability
late_brand_dock_rate
late_logistic_regression
```

### Aggregate summary

For each model/metric:

```text
fold_count
mean
std
median
min
max
```

For primary metrics also store:

```text
worst_fold
best_fold
```

### Segment diagnostics

Reuse Phase 07 segment metrics.

Do not invent model-specific segment definitions.

### Ranking policy

Phase 08 may sort models by the **frozen primary metric** for reporting, but it must not declare the final Task 1 champion.

Phase 09 performs advanced-model comparison and final selection.

### Required private outputs

```text
fold_results.csv
model_summary.csv
segment_diagnostics.csv
run_manifest.json
phase08_baseline_report.md
```

### Report must state

- final holdout was not accessed;
- all models used the same development folds;
- preprocessing was fold-fit only;
- no prohibited actual fields were used;
- no hyperparameter tuning occurred;
- no final model was selected.

### Definition of Done

- [ ] every enabled baseline has fold results;
- [ ] aggregate summaries exist;
- [ ] primary metric clearly marked;
- [ ] artifacts are private/ignored;
- [ ] Phase 09 can load/compare the benchmark contract.

---

# 11. Baseline implementation architecture

## `src/task1/baselines.py`

Recommended API:

```python
class GlobalMedianServiceBaseline: ...
class GroupMedianServiceBaseline: ...
class ConstantLateProbabilityBaseline: ...
class GroupLateRateBaseline: ...

@dataclass
class BaselineFoldResult:
    ...

def run_statistical_baseline_fold(...): ...
def run_linear_regression_fold(...): ...
def run_logistic_regression_fold(...): ...
def run_task1_baseline_experiments(...): ...
```

## `src/task1/baseline_preprocessing.py`

Recommended:

```python
resolve_baseline_feature_columns(...)
build_linear_preprocessor(...)
build_regression_pipeline(...)
build_logistic_pipeline(...)
assert_baseline_feature_safety(...)
```

Do not duplicate Phase 06 leakage rules. Import/reuse the canonical registry/audit utilities where possible.

---

# 12. Baseline feature-safety gate

Before fitting DT-135/DT-136, assert:

```text
feature exists in registry
prediction_time_safe = true
model_candidate = true
not target
not target-derived
not actual journey outcome
not raw forbidden identifier
```

Hard forbidden direct columns:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag
```

Also reject aliases/derived leakage based on Phase 06 lineage metadata.

The safe pattern is:

```text
registry allow-list
+
lineage audit
+
deny-list defense in depth
```

not:

```text
use every column except obvious bad names
```

---

# 13. Statistical baseline fit-scope tests

The grouped baselines are target-derived statistics and must obey the same temporal discipline as historical target features.

For every fold:

```text
fit statistic on fold train only
predict validation from frozen train statistic
```

Required synthetic test:

1. create train and validation data;
2. fit grouped baseline;
3. predict validation;
4. modify only validation labels;
5. predict validation again;
6. assert predictions unchanged.

Also test that a future group value in validation does not cause any full-data lookup.

---

# 14. Linear/logistic preprocessing contract

## Numeric pipeline

Recommended:

```text
median imputation
optional standard scaling
```

All fitted on fold training only.

## Categorical pipeline

Recommended:

```text
constant missing token
one-hot encoding
unknown validation categories ignored safely
```

Learn categories from train only.

## Column resolution

Resolve columns from the Phase 06 feature registry.

Do not infer the feature set from whatever columns happen to be in the current DataFrame.

## Reproducibility

Same input + same config + same fold must produce the same predictions within numerical tolerance.

---

# 15. Required Phase 08 tests

Create:

```text
tests/test_task1_baselines.py
tests/test_task1_baseline_preprocessing.py
```

All fixtures synthetic.

## DT-130

- known global median;
- even-number median;
- empty target failure;
- validation-y mutation has no effect.

## DT-131

- brand medians;
- unseen brand fallback;
- no validation target leakage.

## DT-132

- exact brand+dock match;
- brand fallback;
- global fallback;
- no validation target leakage.

## DT-133

- known training late rate;
- all-zero training;
- all-one training;
- probability bounds.

## DT-134

- grouped late rates;
- zero/one group rate;
- brand fallback;
- global fallback;
- group count diagnostic;
- validation-y mutation invariant.

## DT-135

- registry-based feature selection;
- forbidden-field rejection;
- categorical unseen handling;
- numeric missing handling;
- fold-only fit;
- finite predictions;
- no silent negative clipping.

## DT-136

- probability shape;
- probability bounds;
- `predict_proba` use;
- no class weighting;
- no resampling;
- single-class train handling;
- convergence warning capture.

## Validation contract

- uses Phase 07 folds;
- no random split;
- final holdout absent;
- same-date atomicity retained;
- validation y cannot change validation X.

## DT-137

- result schema;
- stable model names;
- aggregate metric calculations;
- fold count;
- primary metric marked;
- run manifest contains config/validation version;
- report states holdout untouched.

---

# 16. Edge cases

## Unseen brand/group in validation

Use documented fallback from fold-train state.

Never look at later/full-data target statistics.

## Missing dock type

If Phase 03/06 already defined a valid missing policy, reuse it.

Do not silently drop validation rows.

## Group has one training row

Raw median/rate is still the baseline statistic.

Record count for diagnostics.

Do not secretly smooth based on validation performance.

## Constant numeric feature

Scaler/pipeline should not crash.

## New validation categorical level

`OneHotEncoder(handle_unknown="ignore")` or equivalent safe behavior.

## Logistic single-class training fold

Report explicit unsupported fold/model state.

Do not redraw the chronological fold just to make logistic regression fit.

## Linear negative service predictions

Keep raw prediction for validation metrics.

Count the negatives.

Do not clip inside Phase 08 evaluation.

## Probability exactly 0 or 1

Valid baseline output.

Log-loss implementation handles numerical epsilon internally.

Do not alter the stored probability solely for the metric.

## Optional road/traffic features disabled

Baseline feature resolver must omit them cleanly.

Do not recreate them.

## Historical target features

Default linear/logistic baseline excludes them.

If a future approved baseline config enables them, all Phase 07 fold-fit rules apply.

## Final holdout

The baseline runner must fail if configured to score the final holdout during normal Phase 08 execution.

---

# 17. Phase 08 STOP conditions

`READY FOR PHASE 09` must remain **NO** if any of the following is unresolved:

- Phase 07 did not pass;
- Phase 06 leakage audit is not passing;
- Phase 08 creates its own random validation split;
- development folds differ between baseline models;
- final holdout is used for baseline selection/tuning;
- same-date atomicity is violated;
- a statistical baseline uses full-data or validation targets;
- validation targets affect validation features;
- preprocessing is fit on validation rows;
- actual journey outcomes enter X;
- target-derived columns enter X;
- raw high-cardinality identifiers enter the default baseline unintentionally;
- brand/group fallback uses future/full-history target statistics;
- linear predictions are silently clipped during evaluation;
- logistic probabilities are replaced by hard classes for primary evaluation;
- class weighting/resampling is introduced without an approved later experiment;
- hyperparameter tuning occurs in Phase 08;
- different metrics are used for different models;
- result files omit fold/date/config lineage;
- private experiment outputs are committed;
- safe tests fail;
- local baseline run fails;
- independent review fails.

---

# 18. Phase 08 Definition of Done

Phase 08 passes only when:

- [ ] DT-130 PASS
- [ ] DT-131 PASS
- [ ] DT-132 PASS
- [ ] DT-133 PASS
- [ ] DT-134 PASS
- [ ] DT-135 PASS
- [ ] DT-136 PASS
- [ ] DT-137 PASS
- [ ] all baselines use the exact Phase 07 development folds
- [ ] final holdout remains untouched
- [ ] global service median baseline exists
- [ ] brand median baseline exists
- [ ] brand+dock service baseline exists
- [ ] constant probability baseline exists
- [ ] grouped late-rate baseline exists
- [ ] linear regression baseline exists
- [ ] logistic regression baseline exists
- [ ] linear/logistic preprocessing is fold-fit only
- [ ] statistical group baselines are fold-train-only
- [ ] validation-y mutation cannot alter validation features/predictions through leakage
- [ ] default simple baseline feature set is registry-driven
- [ ] actual journey fields absent from model X
- [ ] target-derived fields absent from model X
- [ ] no hyperparameter search performed
- [ ] no class resampling/reweighting performed
- [ ] frozen Phase 07 metrics reused exactly
- [ ] Phase 07 segment diagnostics reused
- [ ] stable experiment names used
- [ ] per-fold results stored privately
- [ ] aggregate baseline summary stored privately
- [ ] run manifest records config/validation/code lineage
- [ ] full safe test suite passes
- [ ] `python -m pip check` passes
- [ ] local real-data baseline run passes
- [ ] independent review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 08 STATUS: PASS
READY FOR PHASE 09: YES
```

---

# 19. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-08-task1-baselines
```

Recommended commits:

```text
feat(task1): add statistical service baselines
feat(task1): add lateness probability baselines
feat(task1): add fold-safe linear preprocessing
feat(task1): add linear and logistic baselines
test(task1): add baseline leakage and fallback tests
feat(task1): add baseline experiment runner
chore(task1): add baseline experiment configuration
docs(task1): document Task 1 baseline contract
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
LOCAL PHASE 08 BASELINES: PASS
INDEPENDENT PHASE 08 REVIEW: PASS
```

---

# 20. Recommended autonomous agent execution flow

Phase 08 is a **full-phase implementation** phase.

Recommended:

```text
Agent reads Phase 08 contract
        ↓
Implement DT-130–DT-134
        ↓
Run targeted baseline-statistic tests
        ↓
Fix ordinary failures automatically
        ↓
Implement DT-135–DT-136
        ↓
Run preprocessing/model tests
        ↓
Run leakage/validation-contract tests
        ↓
Implement DT-137
        ↓
Run full safe regression suite
        ↓
Run pip check
        ↓
Inspect git status/diff
        ↓
Self-review DoD
        ↓
STOP at private-data boundary
        ↓
Human runs real baseline experiment locally
        ↓
Fresh independent review
```

---

# 21. Enhanced Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 08 only.

PHASE:
Task 1 Baselines

TASK RANGE:
DT-130 through DT-137

EXECUTION MODE:
Full-phase controlled autonomous implementation.

You have permission to perform ALL SAFE engineering work required for
Phase 08.

You MAY:

- create/edit/refactor Phase 08 source code
- create/edit configs
- create/edit docs
- create synthetic fixtures
- run targeted pytest tests
- run the complete safe regression suite
- inspect stack traces
- fix normal implementation bugs automatically
- rerun failing tests
- run python -m pip check
- inspect git status
- inspect git diff
- verify ignored paths
- self-review against the complete Phase 08 Definition of Done

Do NOT stop for ordinary coding/test failures you can safely fix.

STOP only for:

- official competition-rule ambiguity
- requirement to inspect restricted competition rows
- unresolved conflict with Phase 06/07 contracts
- leakage that cannot be corrected safely
- genuine schema/data blocker
- inability to preserve the frozen Phase 07 validation design

DO NOT START PHASE 09.

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
9. approved PHASE_07_COMPETITION_CONTRACT.md
10. PHASE_08_COMPETITION_CONTRACT.md
11. existing Task 1 validation, feature registry, leakage and metric utilities

SOURCE PRIORITY:

Official organizer material
>
approved WayLoom master plan
>
approved phase contracts
>
implementation assumptions

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do NOT inspect row-level official/private competition data in the
external-agent context.

Do NOT access:

data/raw/**
data/interim/**
reports/private/**

Use:

- tracked source code
- tracked configuration
- documentation
- synthetic test fixtures

The human will execute the real baseline experiment locally afterward.

==================================================
IMMUTABLE VALIDATION CONTRACT
==================================================

Reuse Phase 07 exactly.

DO NOT create a new random split.

DO NOT alter:

- validation date
- chronological holdout
- expanding folds
- same-date atomicity
- fit/transform scope
- regression metrics
- probability metrics
- segment definitions

The final holdout remains LOCKED in Phase 08.

Phase 08 evaluates baselines on development folds only.

Do NOT repeatedly score or tune against final holdout.

==================================================
LEAKAGE CONTRACT
==================================================

Never use these as direct features:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag

service_minutes and late_flag are TARGETS only.

Use the Phase 06 registry/lineage audit.

Feature safety must be:

registry allow-list
+
lineage validation
+
forbidden-name deny-list

==================================================
CREATE / UPDATE
==================================================

src/task1/baselines.py
src/task1/baseline_preprocessing.py
scripts/run_task1_baselines.py
configs/task1_baselines.yaml
experiments/README.md
docs/task1_baseline_spec.md
tests/test_task1_baselines.py
tests/test_task1_baseline_preprocessing.py

Private runtime output:

reports/private/phase08_task1_baselines/**

must remain ignored.

==================================================
DT-130 — GLOBAL MEDIAN SERVICE BASELINE
==================================================

For each Phase 07 development fold:

FIT:

median(service_minutes) on FOLD TRAIN only.

PREDICT:

same median for every fold-validation row.

Use Phase 07 regression metrics exactly.

Do not use validation targets.

Do not access final holdout.

==================================================
DT-131 — BRAND MEDIAN SERVICE BASELINE
==================================================

For each fold, fit on TRAIN only:

median service by brand.

For validation:

seen brand
→ train brand median

unseen brand
→ fold-train global median

Do not compute brand medians before splitting.

==================================================
DT-132 — BRAND + DOCK SERVICE BASELINE
==================================================

Default grouping:

brand + dock_type

Fit on fold train only.

Fallback hierarchy:

brand+dock median
→ brand median
→ global median

No target smoothing or future-data lookup.

==================================================
DT-133 — CONSTANT LATE PROBABILITY BASELINE
==================================================

For each fold:

p_late = mean(late_flag_train)

Predict the same probability for all validation rows.

Keep raw 0 or 1 if a training fold is single-class.

Do not manually clip the stored probability merely to improve log loss.

Use Phase 07 probability metrics.

==================================================
DT-134 — GROUPED LATE-RATE BASELINE
==================================================

Frozen default group:

brand + dock_type

Fit on TRAIN only:

brand+dock late rate
brand late rate
global late rate

Validation fallback:

exact group
→ brand
→ global

No smoothing by default.

Do not alter grouping after seeing validation metrics.

Store train group counts for diagnostics.

==================================================
DT-135 — LINEAR REGRESSION BASELINE
==================================================

Use fixed:

sklearn LinearRegression

No hyperparameter search.

Resolve features from Phase 06 registry.

Default baseline excludes:

- raw identifiers
- route_id
- delivery_id
- leg_id
- raw outlet_id
- raw vehicle_id
- historical target-statistic features
- actual journey fields
- target-derived fields

Use a simple, documented prediction-time-safe feature subset.

PREPROCESSING MUST BE FIT INSIDE EACH FOLD.

Numeric:

median imputation
standard scaling

Categorical:

constant missing token
one-hot encoder
handle_unknown=ignore

Never fit preprocessing on validation rows.

Evaluate RAW predictions.

Do not clip negative service predictions.

Record negative_prediction_count.

==================================================
DT-136 — LOGISTIC REGRESSION BASELINE
==================================================

Use fixed configuration similar to:

LogisticRegression(
    C=1.0,
    class_weight=None,
    max_iter=2000,
    solver="lbfgs",
    random_state=42,
)

A minimal solver compatibility adjustment is allowed only if required by
the installed sklearn version.

Do NOT tune C.

Do NOT use class_weight="balanced".

Do NOT oversample.

Do NOT undersample.

Use the same fold-safe preprocessing contract as linear regression.

Use:

predict_proba(X_valid)[:, 1]

Primary evaluation uses probabilities.

Do not replace them with hard 0/1 classifications.

Capture convergence warnings.

If a fold train set contains only one class:

- do not redraw the fold
- record the logistic fold as unsupported/failure according to the
  Phase 08 contract
- keep constant/grouped probability baselines valid

==================================================
DT-137 — STORE BASELINE EXPERIMENT RESULTS
==================================================

Create stable experiment names:

service_global_median
service_brand_median
service_brand_dock_median
service_linear_regression

late_constant_probability
late_brand_dock_rate
late_logistic_regression

Store privately:

run_manifest.json
fold_results.csv
model_summary.csv
segment_diagnostics.csv
phase08_baseline_report.md

Every fold result should include:

experiment_id
model_name
target
fold_id
train_start_date
train_end_date
validation_start_date
validation_end_date
train_n
validation_n
metric_name
metric_value

Aggregate each model/metric using:

fold_count
mean
std
median
min
max
best_fold
worst_fold

Reuse Phase 07 segment definitions.

Do NOT declare a final Task 1 champion.

The report must explicitly state:

- final holdout not accessed
- same folds used by all models
- preprocessing fit on train only
- no prohibited actual fields
- no hyperparameter tuning
- no final model selected

==================================================
BASELINE FEATURE CONFIG
==================================================

Create configs/task1_baselines.yaml.

Freeze:

- statistical baseline group keys
- fallback hierarchy
- linear estimator
- logistic estimator
- preprocessing
- baseline feature policy
- Phase 07 metric reuse
- final-holdout disabled state

Do not change config automatically after observing validation results.

==================================================
CRITICAL FIT-SCOPE TESTS
==================================================

For grouped statistical baselines:

1. fit on fold train
2. predict fold validation
3. modify ONLY validation targets
4. predict again
5. assert predictions unchanged

For linear/logistic pipelines:

Changing validation targets must not change validation X or predictions
from a fixed fitted model.

Also verify preprocessing learns:

imputation statistics
scaling statistics
category levels

from train only.

==================================================
REQUIRED SYNTHETIC TESTS
==================================================

DT-130:
- known median
- even median
- validation target mutation invariant

DT-131:
- brand medians
- unseen brand fallback
- no leakage

DT-132:
- exact brand+dock
- brand fallback
- global fallback
- no leakage

DT-133:
- known late rate
- all-zero
- all-one
- probability bounds

DT-134:
- grouped rate
- zero/one group rate
- brand/global fallback
- validation-y mutation invariant

DT-135:
- registry feature selection
- forbidden feature rejection
- unseen category
- missing numeric
- fold-only preprocessing fit
- finite prediction
- negative prediction not silently clipped

DT-136:
- predict_proba
- probability bounds
- class_weight remains null
- no resampling path
- single-class fold handling
- convergence warning capture

VALIDATION:
- uses Phase 07 folds exactly
- no random split
- final holdout never scored
- same-date atomicity retained
- validation y cannot affect validation X

DT-137:
- result schema
- stable names
- aggregate calculations
- primary metric recorded
- run manifest lineage
- report says holdout untouched

==================================================
AUTONOMOUS TEST / DEBUG LOOP
==================================================

After implementing statistical baselines:

run targeted tests
fix ordinary failures
rerun until clean

After linear/logistic baselines:

run preprocessing/model tests
run leakage tests
fix ordinary failures
rerun until clean

After DT-137:

run FULL SAFE regression suite.

At minimum include all existing tests from Phases 01–07 plus:

tests/test_task1_baselines.py
tests/test_task1_baseline_preprocessing.py

Then run:

python -m pip check

Then inspect:

git status
git diff

Do not stage private competition artifacts.

==================================================
LOCAL REAL-DATA COMMAND
==================================================

Implement but DO NOT execute against restricted competition data in the
external-agent context:

python scripts/run_task1_baselines.py \
  --features data/interim/task1_features_train.csv \
  --labels data/interim/task1_training_labels.csv \
  --feature-registry configs/task1_features.yaml \
  --validation-config configs/task1_validation.yaml \
  --baseline-config configs/task1_baselines.yaml \
  --output-dir reports/private/phase08_task1_baselines

If the canonical Phase 06 registry path differs, reuse the existing path.
Do not duplicate registries.

==================================================
STOP CONDITIONS
==================================================

STOP if:

- Phase 07 contract is bypassed
- a new random split is created
- final holdout is used
- models use different folds
- grouped baselines use validation/full-data targets
- preprocessing fits on validation data
- validation y affects validation X
- actual journey fields enter X
- target-derived fields enter X
- baseline config changes based on observed validation performance
- hyperparameter tuning starts
- class rebalancing starts
- linear predictions are silently clipped
- logistic hard labels replace probability evaluation
- private data inspection is required
- safe tests cannot pass without violating approved contracts

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-130 READY
DT-131 READY
DT-132 READY
DT-133 READY
DT-134 READY
DT-135 READY
DT-136 READY
DT-137 READY

same Phase 07 folds used by all baselines

final holdout untouched

statistical baselines fit train-only

linear/logistic preprocessing fit train-only

actual journey fields absent

target-derived fields absent

no hyperparameter search

no class rebalancing

frozen metrics reused

segment metrics reused

experiment results reproducible

full safe tests pass

pip check passes

private outputs ignored

no Phase 09 code added

==================================================
RETURN ONLY
==================================================

PHASE:
08 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-130 READY / FAIL
DT-131 READY / FAIL
DT-132 READY / FAIL
DT-133 READY / FAIL
DT-134 READY / FAIL
DT-135 READY / FAIL
DT-136 READY / FAIL
DT-137 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

PHASE 07 VALIDATION REUSE:
PASS / FAIL

FINAL HOLDOUT ACCESSED:
MUST BE NO

STATISTICAL BASELINE FIT-SCOPE:
PASS / FAIL

LINEAR PREPROCESSING FIT-SCOPE:
PASS / FAIL

LOGISTIC PREPROCESSING FIT-SCOPE:
PASS / FAIL

LEAKAGE AUDIT:
PASS / FAIL

REGRESSION METRIC CONTRACT:
PASS / FAIL

PROBABILITY METRIC CONTRACT:
PASS / FAIL

BASELINE RESULT STORAGE:
PASS / FAIL

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local baseline-run command.

PHASE 08 STATUS:
AWAITING LOCAL BASELINE RUN

READY FOR PHASE 09:
NO

Then STOP.

Do not begin Phase 09.
```

---

# 22. Enhanced independent Phase 08 review prompt

Use this in a **fresh Cursor chat** after the local baseline run.

Do not attach the private metric files.

```text
Perform an independent review of completed WayLoom Datathon Phase 08.

PHASE:
Task 1 Baselines

TASKS:
DT-130 through DT-137

DO NOT:
- open data/raw
- open data/interim
- open reports/private
- inspect private fold metrics
- execute the real baseline experiment
- modify code initially
- start Phase 09

READ:

1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. PHASE_08_COMPETITION_CONTRACT.md
3. configs/task1_baselines.yaml
4. src/task1/baselines.py
5. src/task1/baseline_preprocessing.py
6. scripts/run_task1_baselines.py
7. docs/task1_baseline_spec.md
8. tests/test_task1_baselines.py
9. tests/test_task1_baseline_preprocessing.py
10. relevant Phase 06 feature-registry/leakage code
11. relevant Phase 07 validation/metric code
12. .gitignore
13. .cursorignore

HUMAN LOCAL CONTROL RESULT:

LOCAL PHASE 08 BASELINES: <PASS / FAIL>
ALL DEVELOPMENT FOLDS COMPLETED: <YES / NO>
FINAL HOLDOUT ACCESSED: <NO / YES>
LEAKAGE AUDIT: <PASS / FAIL>
BASELINE RESULT TABLE WRITTEN: <YES / NO>

Do not ask for private metric values.

==================================================
AUDIT DT-130
==================================================

Confirm:

- global median uses fold TRAIN target only
- validation target never affects median
- Phase 07 regression metrics reused
- no holdout access

==================================================
AUDIT DT-131
==================================================

Confirm:

- brand medians fit per fold train
- unseen brand falls back to fold global median
- no full-history groupby leakage

==================================================
AUDIT DT-132
==================================================

Confirm:

- brand+dock fit on fold train only
- fallback is brand then global
- validation targets cannot alter predictions

==================================================
AUDIT DT-133
==================================================

Confirm:

- constant probability is fold-train late mean
- output remains probability
- 0/1 single-class empirical rates are handled
- metric epsilon does not mutate stored predictions

==================================================
AUDIT DT-134
==================================================

Confirm:

- grouped rate uses frozen group keys
- fit is train-only
- fallback is deterministic
- no smoothing introduced after validation inspection

==================================================
AUDIT DT-135
==================================================

Confirm:

- sklearn linear regression baseline
- no tuning
- feature subset comes from Phase 06 registry
- raw identifiers excluded by default
- historical target-statistic features excluded by default
- preprocessing fit on training fold only
- validation unknown categories safe
- negative predictions are diagnosed, not clipped for validation

==================================================
AUDIT DT-136
==================================================

Confirm:

- logistic regression is fixed baseline
- predict_proba is used
- class_weight is not silently balanced
- no resampling
- preprocessing is train-only
- single-class fold handled explicitly
- convergence warnings are surfaced
- primary metric uses probabilities

==================================================
AUDIT DT-137
==================================================

Confirm private result-generation code creates:

run_manifest
fold results
aggregate model summary
segment diagnostics
baseline report

Confirm stable model names.

Confirm metadata includes:

validation-plan version
baseline config
feature-registry lineage
seed
code/git version if available

Confirm report explicitly states:

- holdout untouched
- same folds for every model
- no hyperparameter tuning
- no final model selection

==================================================
GLOBAL VALIDATION REVIEW
==================================================

Confirm:

- Phase 07 folds reused, not recreated differently
- no random split
- same-date atomicity preserved
- final holdout absent from Phase 08 experiment runner
- validation y cannot affect validation X
- actual journey features absent
- targets absent from X
- frozen regression metrics reused
- frozen probability metrics reused
- Phase 07 segment definitions reused

==================================================
DATA SAFETY
==================================================

Confirm:

- tests contain synthetic records only
- tracked docs contain no private metric tables
- reports/private ignored
- data/interim ignored
- no real competition row samples in code/docs

==================================================
RUN SAFE TESTS
==================================================

Run the complete safe repository test suite.

At minimum include:

pytest -q

Then:

python -m pip check

git status

Do NOT run the real baseline experiment.

==================================================
RETURN
==================================================

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

PHASE 07 VALIDATION REUSE:
PASS / FAIL

FINAL HOLDOUT PROTECTION:
PASS / FAIL

STATISTICAL BASELINE FIT-SCOPE:
PASS / FAIL

LINEAR/LOGISTIC PREPROCESSING SCOPE:
PASS / FAIL

LEAKAGE PROTECTION:
PASS / FAIL

REGRESSION METRIC CONTRACT:
PASS / FAIL

PROBABILITY METRIC CONTRACT:
PASS / FAIL

RESULT REPRODUCIBILITY:
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

DT-130: PASS/FAIL
DT-131: PASS/FAIL
DT-132: PASS/FAIL
DT-133: PASS/FAIL
DT-134: PASS/FAIL
DT-135: PASS/FAIL
DT-136: PASS/FAIL
DT-137: PASS/FAIL

PHASE 08 REVIEW:
PASS / FAIL

READY FOR PHASE 09:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not start Phase 09.
```

---

# 23. Local Phase 08 execution instructions

After the agent implementation and safe tests pass:

## Step 1 — use a normal local terminal

Do not run the private competition-data experiment through the external AI-agent context.

## Step 2 — verify ignored outputs

```bash
git status
git check-ignore -v reports/private/phase08_task1_baselines/fold_results.csv
```

## Step 3 — run safe tests

```bash
pytest -q tests/test_task1_baselines.py tests/test_task1_baseline_preprocessing.py
```

Then preferably:

```bash
pytest -q
```

## Step 4 — run baselines locally

Recommended:

```bash
python scripts/run_task1_baselines.py \
  --features data/interim/task1_features_train.csv \
  --labels data/interim/task1_training_labels.csv \
  --feature-registry configs/task1_features.yaml \
  --validation-config configs/task1_validation.yaml \
  --baseline-config configs/task1_baselines.yaml \
  --output-dir reports/private/phase08_task1_baselines
```

PowerShell one-line form:

```powershell
python scripts/run_task1_baselines.py --features data/interim/task1_features_train.csv --labels data/interim/task1_training_labels.csv --feature-registry configs/task1_features.yaml --validation-config configs/task1_validation.yaml --baseline-config configs/task1_baselines.yaml --output-dir reports/private/phase08_task1_baselines
```

If your canonical Phase 06 feature-registry path differs, use that approved existing path.

## Step 5 — inspect private report locally

Confirm:

```text
all development folds completed
final holdout not touched
all enabled baselines produced predictions
no fold/date overlap
no leakage assertion failures
linear/logistic preprocessing fit-scope passed
all result artifacts generated
```

Do not paste private metric values into the AI review chat.

## Step 6 — return only sanitized status

Example:

```text
LOCAL PHASE 08 BASELINES: PASS
ALL DEVELOPMENT FOLDS COMPLETED: YES
FINAL HOLDOUT ACCESSED: NO
LEAKAGE AUDIT: PASS
BASELINE RESULT TABLE WRITTEN: YES
```

Then use the independent review prompt.

---

# 24. Completion record template

```markdown
# Phase 08 Completion Record

## Tasks

- [ ] DT-130
- [ ] DT-131
- [ ] DT-132
- [ ] DT-133
- [ ] DT-134
- [ ] DT-135
- [ ] DT-136
- [ ] DT-137

## Agent stage

- Statistical baseline tooling: PASS / FAIL
- Linear preprocessing/model: PASS / FAIL
- Logistic preprocessing/model: PASS / FAIL
- Leakage tests: PASS / FAIL
- Validation reuse tests: PASS / FAIL
- Full test suite: PASS / FAIL
- pip check: PASS / FAIL

## Local baseline stage

- Local run: PASS / FAIL
- All development folds completed: YES / NO
- Final holdout accessed: NO / YES
- Global service median generated: YES / NO
- Brand service median generated: YES / NO
- Brand+dock service baseline generated: YES / NO
- Constant late probability generated: YES / NO
- Grouped late-rate baseline generated: YES / NO
- Linear regression baseline generated: YES / NO
- Logistic regression baseline generated: YES / NO
- Fold results written: YES / NO
- Model summary written: YES / NO
- Segment diagnostics written: YES / NO
- Run manifest written: YES / NO

## Safety

- Raw/private rows exposed to external agent: NO
- Final holdout used for tuning: NO
- Validation targets used in feature/preprocessing fit: NO
- Actual journey fields in X: NO
- Target-derived fields in X: NO
- Hyperparameter tuning performed: NO
- Class resampling/reweighting performed: NO

## Review

- Independent review: PASS / FAIL

## Verdict

PHASE 08 STATUS: PASS / FAIL

READY FOR PHASE 09: YES / NO
```

---

# 25. Final Phase 08 checklist

Before Phase 09:

- [ ] Phase 07 passed.
- [ ] all DT-130–DT-137 implemented.
- [ ] global median service baseline exists.
- [ ] brand median service baseline exists.
- [ ] brand+dock service baseline exists.
- [ ] constant late-probability baseline exists.
- [ ] grouped late-rate baseline exists.
- [ ] linear regression baseline exists.
- [ ] logistic regression baseline exists.
- [ ] statistical baselines are fit on fold train only.
- [ ] linear/logistic preprocessing is fit on fold train only.
- [ ] all models use the exact same Phase 07 development folds.
- [ ] final holdout is untouched.
- [ ] same-date atomicity preserved.
- [ ] validation y cannot affect validation features.
- [ ] feature registry drives model inputs.
- [ ] direct actual journey fields absent.
- [ ] target-derived fields absent.
- [ ] raw identifiers excluded from default linear/logistic baseline.
- [ ] Phase 07 regression metrics reused.
- [ ] Phase 07 probability metrics reused.
- [ ] Phase 07 segment diagnostics reused.
- [ ] no hyperparameter tuning performed.
- [ ] no probability calibration performed.
- [ ] no class resampling/reweighting performed.
- [ ] no final champion model selected.
- [ ] experiment result tables generated privately.
- [ ] run manifest records reproducibility metadata.
- [ ] safe tests pass.
- [ ] local baseline run passes.
- [ ] private outputs remain ignored.
- [ ] independent review passes.
- [ ] no STOP condition remains.

Only then:

```text
PHASE 08 STATUS: PASS
READY FOR PHASE 09: YES
```

Do not automatically begin Phase 09.
