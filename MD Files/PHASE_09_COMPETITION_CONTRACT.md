# PHASE 09 — Task 1 Advanced Modelling

> **Requested filename:** `PHASE_09_COMPETITION_CONTRACT.md`  
> **Canonical phase name:** **Phase 09 — Task 1 Advanced Modelling**  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-138 → DT-156**  
> **Task count:** 19  
> **Phase dependency:** **Phase 08 — Task 1 Baselines must be complete and independently reviewed**  
> **Default phase priority:** P1  
> **Recommended execution style:** **Hybrid advanced-modelling phase: autonomous tooling + safe synthetic tests, followed by local private experiments, one-time holdout confirmation, and independent review**  
> **Phase gate:** Champion Task 1 regression and lateness configurations are selected under the frozen Phase 07 validation contract, calibration is tested correctly, error/segment analysis is complete, and the exact final model configuration is frozen for Phase 10.

---

# 1. Phase objective

Phase 09 develops and compares stronger Task 1 models against the Phase 08 baselines without changing the rules after seeing performance.

The phase must answer:

- Can CatBoost materially improve service-time prediction over the frozen baselines?
- Can CatBoost improve late-event probability quality?
- Does LightGBM provide a competitive challenger under exactly the same validation folds?
- Is an XGBoost challenger worth running within time and package constraints?
- Which hyperparameters improve development-fold performance without creating unstable or obviously overfit models?
- What iteration count should be used through early stopping?
- Where do the models make their largest regression errors?
- Where does the lateness classifier make confident mistakes?
- Does performance remain acceptable across brand and depot segments?
- Are the raw late probabilities well calibrated?
- Does post-hoc calibration improve probability metrics under a leakage-safe chronological evaluation?
- Which exact regression model and lateness model should be frozen for final training/inference?

Phase 09 must **not**:

- alter the official Task 1 labels;
- redesign Phase 07 validation after seeing scores;
- use the final holdout repeatedly for tuning;
- import actual route outcomes into the feature matrix;
- tune against Task 1 test data;
- use pre-trained models;
- use proprietary API-based modelling/preprocessing;
- use low-code/no-code or fully automated end-to-end modelling tools;
- begin final test inference/submission generation;
- silently change the Phase 08 baseline definitions;
- claim that a complex model is better merely because it is more complex.

---

# 2. Official competition contract relevant to Phase 09

The official Task 1 prediction outputs are:

```text
pred_service_min
pred_late_prob
```

They represent two distinct modelling problems:

```text
service_minutes  → regression
late_flag        → probability estimation / binary classification
```

The official challenge states that:

- planned departure, planned travel duration, and planned arrival are available at prediction time;
- actual journey and handling times exist only in historical route records;
- the team may choose and justify its features;
- the challenge does not prescribe a specific feature set;
- final `pred_late_prob` must be a probability in `[0, 1]`;
- final Task 1 output must preserve every supplied `delivery_id` and original row order.

The competition also restricts:

```text
pre-trained models
proprietary API-based modelling/preprocessing
low-code/no-code AI modelling tools
fully automated end-to-end modelling tools
unauthorized sharing/transmission of competition data
```

Therefore all Phase 09 models are ordinary models trained locally from scratch on the supplied competition data.

CatBoost, LightGBM and optional XGBoost are **model families**, not pre-trained models. They are acceptable only when fitted locally from scratch and used consistently with the competition restrictions.

---

# 3. Source hierarchy

Use this authority order:

1. Official Challenge Booklet and official supplied files.
2. Approved `WAYLOOM_DATATHON_MASTER_PLAN.md`.
3. Approved Phase 00–08 contracts.
4. This Phase 09 implementation contract.
5. Engineering assumptions.

If a later implementation assumption conflicts with an approved earlier contract, stop rather than silently changing the earlier contract.

---

# 4. Required preconditions

Do not execute Phase 09 experiments unless all of the following are true:

```text
Phase 04 labels                         PASS
Phase 06 leakage audit                 PASS
Phase 06 train/test feature parity     PASS
Phase 07 temporal validation           PASS
Phase 07 same-date atomicity           PASS
Phase 07 fit-scope leakage test        PASS
Phase 08 baselines                     PASS
Phase 08 final holdout accessed        NO
Phase 08 independent review            PASS
```

If Phase 08 has not actually passed, Phase 09 may be implemented as code/tooling, but **real advanced model selection must not be performed yet**.

---

# 5. Frozen contracts inherited from earlier phases

## 5.1 Labels

Regression target:

```text
service_minutes
```

Probability target:

```text
late_flag
```

Do not recalculate either target in Phase 09.

## 5.2 Forbidden direct features

Never permit the final model matrix to include:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag
```

The first four are historical actual outcomes.

The final three are target/target-derived fields.

Renaming, hashing, encoding, aggregating the current row, or placing these fields inside a generic feature list does not make them valid.

## 5.3 Validation

Reuse Phase 07 exactly:

```text
canonical validation date
chronological ordering
same-date atomicity
final holdout definition
expanding development folds
fold train/validation dates
fit-dependent feature scope
regression metrics
probability metrics
segment diagnostics
```

No random split is allowed.

## 5.4 Baselines

Phase 08 results are the frozen benchmark.

Do not rerun baselines under a more favorable split to make advanced models look better.

---

# 6. Final-holdout policy

Phase 09 uses a two-stage selection policy.

## Stage 1 — development selection

Use **only Phase 07 development folds** for:

- model-family comparison;
- hyperparameter tuning;
- early-stopping policy;
- calibration experiments;
- error analysis;
- segment analysis;
- provisional model selection.

## Stage 2 — one-time holdout confirmation

After the regression and lateness configurations have been provisionally frozen from development results:

1. record their exact feature profile, parameters, random seed, calibration method and preprocessing;
2. evaluate **only those frozen provisional configurations** on the final holdout;
3. record holdout metrics once;
4. do not begin another tuning cycle using the holdout result.

The final holdout is a generalization confirmation, not another search set.

If the one-time holdout reveals a catastrophic implementation or distribution issue:

```text
STOP
```

Document that the holdout has been consumed before any redesign.

Do not repeatedly try alternative models on the same final holdout.

---

# 7. Data-safety execution model

The coding agent has broad autonomy for safe engineering/testing but competition data remains protected.

## Agent may

- edit source code;
- edit configuration;
- add tests;
- create synthetic fixtures;
- run synthetic/unit/integration tests;
- inspect stack traces;
- fix ordinary code failures;
- run `pytest`;
- run `python -m pip check`;
- inspect Git status/diff;
- validate tracked configuration;
- implement all model runners and selection logic.

## Agent must not

- inspect `data/raw/**`;
- inspect private row-level `data/interim/**` outputs;
- inspect `reports/private/**` competition-derived results;
- inspect actual model error rows;
- inspect competition-derived calibration curves;
- transmit private competition data to an external model/provider;
- run proprietary remote model APIs.

## Human/local stage

The human runs the real model experiments locally and inspects private results.

Only sanitized control results should be returned to an AI agent, for example:

```text
LOCAL PHASE 09 DEVELOPMENT EXPERIMENT: PASS
ALL FOLDS COMPLETED: YES
PROVISIONAL SERVICE CONFIG FROZEN: YES
PROVISIONAL LATENESS CONFIG FROZEN: YES
CALIBRATION DECISION FROZEN: YES
FINAL HOLDOUT ACCESSED: NO
```

After the one-time holdout confirmation:

```text
LOCAL PHASE 09 HOLDOUT CONFIRMATION: PASS
HOLDOUT EVALUATIONS PER TARGET: 1
CONFIG CHANGED AFTER HOLDOUT: NO
FINAL CONFIG WRITTEN: YES
```

Do not paste row-level errors, IDs, raw predictions, or private report files into the coding agent.

---

# 8. Phase 09 task registry

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---|---|---|---|
| [ ] | **DT-138** | [E] | P1 | Phase 08 baselines | Train CatBoost regression model |
| [ ] | **DT-139** | [E] | P1 | Phase 08 baselines | Train CatBoost late classifier |
| [ ] | **DT-140** | [C] | P2 | Phase 08 | Train LightGBM challenger |
| [ ] | **DT-141** | [C] | P2 | Phase 08 | Optionally train XGBoost challenger |
| [ ] | **DT-142** | [E] | P1 | Phase 08 | Compare models under same folds |
| [ ] | **DT-143** | [E] | P1 | Phase 08 | Tune regression hyperparameters |
| [ ] | **DT-144** | [E] | P1 | Phase 08 | Tune classifier hyperparameters |
| [ ] | **DT-145** | [E] | P1 | Phase 08 | Use early stopping |
| [ ] | **DT-146** | [E] | P1 | Phase 08 | Analyze overfitting |
| [ ] | **DT-147** | [E] | P1 | Phase 08 | Inspect worst regression errors |
| [ ] | **DT-148** | [E] | P1 | Phase 08 | Inspect high-confidence classification errors |
| [ ] | **DT-149** | [E] | P1 | Phase 08 | Check brand-specific model performance |
| [ ] | **DT-150** | [E] | P1 | Phase 08 | Check depot-specific model performance |
| [ ] | **DT-151** | [E] | P1 | Phase 08 | Generate calibration curve |
| [ ] | **DT-152** | [E] | P1 | Phase 08 | Test probability calibration |
| [ ] | **DT-153** | [E] | P1 | Phase 08 | Compare uncalibrated vs calibrated probability metrics |
| [ ] | **DT-154** | [E] | P1 | DT-142–DT-153 | Select final Task 1 regression model |
| [ ] | **DT-155** | [E] | P1 | DT-142–DT-153 | Select final Task 1 lateness model |
| [ ] | **DT-156** | [E] | P1 | Phase 08 | Freeze Task 1 model configuration |

Legend:

```text
[E]  WayLoom engineering task
[C]  Challenger/conditional task
```

**Phase complete:** [ ]  
**READY FOR PHASE 10:** NO

---

# 9. Required repository additions

Recommended tracked files:

```text
src/task1/
├── advanced_models.py
├── tuning.py
├── calibration.py
└── model_selection.py

scripts/
├── run_task1_advanced_models.py
├── confirm_task1_final_holdout.py
└── freeze_task1_model_config.py

configs/
├── task1_advanced_models.yaml
└── task1_final_models.yaml

docs/
└── task1_advanced_modeling_spec.md

tests/
├── test_task1_advanced_models.py
├── test_task1_tuning.py
├── test_task1_calibration.py
└── test_task1_model_selection.py
```

Private local outputs:

```text
reports/private/phase09_task1_models/
├── run_manifest.json
├── candidate_registry.json
├── service_cv_results.csv
├── late_cv_results.csv
├── tuning_service.csv
├── tuning_late.csv
├── early_stopping_summary.json
├── overfitting_summary.json
├── regression_error_summary.json
├── classification_error_summary.json
├── brand_metrics.csv
├── depot_metrics.csv
├── calibration_curve.csv
├── calibration_comparison.csv
├── provisional_selection.json
├── holdout_confirmation.json
└── phase09_model_report.md
```

Optional private temporary artifacts:

```text
reports/private/phase09_task1_models/artifacts/
```

Do not commit temporary trained models from Phase 09.

Final saved model files are a Phase 10 responsibility.

---

# 10. Recommended advanced-model configuration

Create:

```text
configs/task1_advanced_models.yaml
```

Recommended structure:

```yaml
version: 1

seed: 42

validation:
  use_phase07_plan: true
  use_final_holdout_during_search: false

features:
  registry_driven: true
  profile: safe_core_plus_history
  allow_historical_target_features: true
  require_fold_safe_history_transform: true

catboost:
  regression:
    enabled: true
    loss_function: MAE
    eval_metric: MAE
    random_seed: 42
    verbose: false
    allow_writing_files: false

  classification:
    enabled: true
    loss_function: Logloss
    eval_metric: Logloss
    random_seed: 42
    verbose: false
    allow_writing_files: false
    auto_class_weights: null

lightgbm:
  enabled: true
  random_state: 42
  verbosity: -1

xgboost:
  enabled: false
  optional: true
  random_state: 42

search:
  strategy: bounded_predeclared_grid
  prohibit_automl: true
  prohibit_bayesian_end_to_end_automl: true
  max_regression_candidates: 16
  max_classifier_candidates: 16

  regression_candidates:
    depth: [5, 7, 9]
    learning_rate: [0.03, 0.05]
    l2_leaf_reg: [3, 7]

  classifier_candidates:
    depth: [5, 7, 9]
    learning_rate: [0.03, 0.05]
    l2_leaf_reg: [3, 7]

early_stopping:
  enabled: true
  max_iterations: 2000
  patience_rounds: 100
  min_iterations: 50

error_analysis:
  worst_regression_n: 100
  confident_positive_threshold: 0.80
  confident_negative_threshold: 0.20

calibration:
  enabled: true
  methods:
    - sigmoid
    - isotonic
  oof_fit_fraction: 0.70
  minimum_calibration_rows: 200
  minimum_positive_rows: 20
  minimum_negative_rows: 20

selection:
  regression_primary: mae
  regression_secondary: rmse
  lateness_primary: log_loss
  lateness_secondary: brier_score
  use_segment_metrics_as_diagnostics_only: true
  one_time_holdout_confirmation: true

private_output_dir: reports/private/phase09_task1_models
```

The exact search grid is an engineering starting point, not an organizer requirement.

The implementation may make a **small, documented technical adjustment** for library compatibility, but must not silently expand into open-ended AutoML.

---

# 11. Feature profiles for advanced models

Phase 09 may use stronger feature profiles than the Phase 08 linear/logistic baseline, but every profile must be predeclared and registry-driven.

Recommended profiles:

## `safe_core`

All Phase 06 enabled prediction-time-safe features except historical target statistics.

## `safe_core_plus_history`

`safe_core` plus Phase 06 historical target-statistic features that passed:

```text
fold-scope tests
same-date exclusion tests
future-target exclusion tests
validation-y isolation tests
```

The default advanced-model profile may be:

```text
safe_core_plus_history
```

only if the Phase 06 and Phase 07 leakage tests passed.

Do not add an unregistered field just because CatBoost or LightGBM accepts it.

---

# 12. Model-specific preprocessing contract

Different model families may use different encodings while still receiving the same semantic source feature set.

That is allowed if:

- feature source lineage is identical;
- validation folds are identical;
- preprocessing is fitted on fold training only;
- test-time availability is identical;
- model-specific transformations are documented.

## CatBoost

Recommended:

- preserve approved categorical fields as categorical inputs;
- replace missing categorical values with a stable string token;
- keep numeric missing values as supported NaN values unless the approved pipeline requires an imputer;
- do not target-encode categoricals outside CatBoost using full-history labels;
- use CPU by default for reproducibility;
- `allow_writing_files=False` to avoid untracked `catboost_info` artifacts.

## LightGBM

Recommended:

- use a fold-safe preprocessing adapter;
- either use categorical dtype handling supported by the installed version or fold-fitted encoding;
- unknown validation/test categories must not cause failure;
- no target-aware encoding unless it obeys the same fold-scope contract.

## XGBoost

If enabled:

- use fold-safe encoding;
- preserve the exact feature registry;
- do not install/enable it in a way that destabilizes the environment shortly before submission;
- if unavailable or unnecessary, document `NOT_RUN_OPTIONAL`.

---

# 13. Detailed task specifications

---

## DT-138 — Train CatBoost regression model

**Mark:** [E]  
**Priority:** P1

### Objective

Create the primary advanced candidate for predicting:

```text
service_minutes
```

### Inputs

- Phase 06 feature definitions;
- Phase 06 feature registry;
- Phase 07 development folds;
- Phase 07 regression metrics;
- Phase 08 baseline results.

### Required estimator

Use a locally trained:

```python
CatBoostRegressor
```

No pre-trained model.

### Initial fixed candidate

Create one sensible untuned starting configuration before hyperparameter search, for example:

```text
loss_function = MAE
eval_metric = MAE
depth = 7
learning_rate = 0.05
l2_leaf_reg = 5
iterations = upper bound controlled by early stopping
random_seed = 42
allow_writing_files = false
verbose = false
```

This starting configuration is a WayLoom engineering baseline and may be adjusted within the bounded Phase 09 search.

### Fold protocol

For every Phase 07 development fold:

1. obtain fold train rows;
2. obtain validation rows;
3. fit all fit-dependent Phase 06 features using train only;
4. transform train;
5. transform validation without validation targets;
6. resolve categorical feature indexes/names from the registry;
7. fit CatBoost regression on fold train;
8. use validation only as eval set for early stopping;
9. predict validation;
10. calculate frozen Phase 07 regression metrics;
11. record best iteration;
12. record train/validation metric history privately.

### Important output behavior

During Phase 09 comparison:

- do not clip negative predictions;
- record `negative_prediction_count`;
- do not round predictions.

### Tests

Synthetic smoke tests:

- tiny categorical + numeric dataset fits;
- feature order preserved;
- forbidden field rejected;
- validation y not used for features;
- deterministic predictions under fixed seed within reasonable numeric tolerance;
- finite output;
- model does not create `catboost_info` in repository.

### Definition of Done

- [ ] CatBoost regressor adapter exists;
- [ ] uses Phase 07 folds;
- [ ] uses registry-safe features;
- [ ] early-stopping-compatible;
- [ ] produces frozen regression metrics;
- [ ] baseline comparison can consume its result.

### STOP conditions

Stop if CatBoost requires a leakage-prone preprocessing shortcut or if validation folds differ from Phase 08.

---

## DT-139 — Train CatBoost late classifier

**Mark:** [E]  
**Priority:** P1

### Objective

Create the primary advanced candidate for predicting:

```text
P(late_flag = 1)
```

### Estimator

Use locally trained:

```python
CatBoostClassifier
```

Recommended initial fixed configuration:

```text
loss_function = Logloss
eval_metric = Logloss
depth = 7
learning_rate = 0.05
l2_leaf_reg = 5
iterations = early-stopping upper bound
random_seed = 42
auto_class_weights = None
allow_writing_files = false
verbose = false
```

### Class weighting

Do not automatically enable:

```text
Balanced
SqrtBalanced
custom class weights
```

The official output is a probability, so calibration quality matters.

Class weighting may alter probability calibration and should not be introduced merely because the positive class is less common.

If later experimentation with weights is desired, it must be an explicit, predeclared candidate and must beat the unweighted model under frozen log loss/Brier without harming calibration. Default Phase 09 should remain unweighted.

### Fold protocol

Use the exact same development folds as every other classifier.

Prediction must use:

```python
predict_proba(...)[..., 1]
```

not hard class predictions.

### Tests

- probability shape correct;
- values finite;
- values in `[0,1]`;
- fixed seed reproducibility;
- no automatic class weighting;
- no resampling;
- validation y isolated;
- single-class fold handled explicitly if encountered.

### Definition of Done

- [ ] CatBoost classifier candidate runs under frozen folds;
- [ ] probability metrics calculated;
- [ ] raw probabilities available for calibration analysis.

---

## DT-140 — Train LightGBM challenger

**Mark:** [C]  
**Priority:** P2

### Objective

Create an independent gradient-boosting challenger to test whether CatBoost's result is model-family-specific.

### Scope

Implement both when practical:

```text
LGBMRegressor
LGBMClassifier
```

Both must use the same semantic feature profile and validation folds as their CatBoost counterparts.

### Fixed initial challenger

Use a conservative, non-tuned starting point such as:

```text
n_estimators = early-stopping upper bound
learning_rate = 0.05
num_leaves = 31
max_depth = -1
min_child_samples = 20
subsample = 0.9
colsample_bytree = 0.9
reg_lambda = 1.0
random_state = 42
```

This is not the final tuned configuration.

### Requirements

- local training only;
- no AutoML wrappers;
- train-only preprocessing;
- early stopping;
- same feature availability;
- same metrics;
- same folds;
- probability classifier returns positive-class probability.

### Tests

Use tiny synthetic smoke tests.

If LightGBM is unavailable despite being an approved project dependency:

```text
BLOCKER
```

unless the team deliberately removes the challenger and documents the reason before the real experiment.

### Definition of Done

- [ ] LightGBM challenger adapter exists;
- [ ] comparable fold outputs generated;
- [ ] no validation-contract changes required.

---

## DT-141 — Optionally train XGBoost challenger

**Mark:** [C]  
**Priority:** P2 / optional

### Objective

Provide a second independent tree-boosting challenger only if it adds useful evidence without consuming disproportionate time or destabilizing the environment.

### Conditions to run

Run only if:

```text
package already available or safely installable
Phase 08/09 core pipeline is stable
time budget permits
CatBoost/LightGBM comparison leaves meaningful uncertainty
```

### If run

Implement:

```text
XGBRegressor
XGBClassifier
```

with fixed-seed, bounded settings and the same folds/metrics.

### If not run

Record:

```text
DT-141 STATUS: NOT_RUN_OPTIONAL
reason: <documented engineering/time/environment reason>
```

Phase 09 may still pass.

### Do not

- delay Phase 10 to chase marginal challenger gains;
- introduce large dependency changes immediately before submission;
- use external/cloud XGBoost services.

### Definition of Done

One of:

- [ ] challenger implemented and evaluated; or
- [ ] optional skip explicitly documented.

---

## DT-142 — Compare models under the same folds

**Mark:** [E]  
**Priority:** P1

### Objective

Produce apples-to-apples model comparisons.

### Required comparison rule

All models for a target must use:

```text
same Phase 07 fold IDs
same train dates
same validation dates
same target definition
same metric implementation
same segment definitions
same approved semantic feature profile
```

Model-specific encoding is permitted only if train-only and documented.

### Compare against Phase 08 baselines

Regression table should include at minimum:

```text
service_global_median
service_brand_median
service_brand_dock_median
service_linear_regression
catboost_regression
lightgbm_regression
xgboost_regression if run
```

Probability table should include at minimum:

```text
late_constant_probability
late_brand_dock_rate
late_logistic_regression
catboost_classifier
lightgbm_classifier
xgboost_classifier if run
```

### Regression comparison

Primary:

```text
mean development-fold MAE
```

Secondary:

```text
RMSE
median absolute error
P90 absolute error
fold-to-fold MAE std
negative prediction count
```

### Probability comparison

Primary:

```text
mean development-fold log loss
```

Secondary:

```text
Brier score
calibration error
ROC-AUC diagnostic
average precision diagnostic
fold-to-fold log-loss std
```

### No hidden fold dropping

If a model fails a fold, do not compare its mean over fewer folds as if equivalent.

Mark the candidate incomplete until the issue is resolved or the model is excluded.

### Tests

- fold IDs match across candidates;
- row counts match;
- missing fold detected;
- primary metric calculation stable;
- candidate result schemas consistent.

### Definition of Done

- [ ] common comparison table exists;
- [ ] baseline rows included;
- [ ] no model uses a different validation population.

---

## DT-143 — Tune regression hyperparameters

**Mark:** [E]  
**Priority:** P1

### Objective

Improve the regression candidate without open-ended AutoML or holdout overfitting.

### Allowed search style

Use a:

```text
bounded, predeclared, reproducible candidate search
```

Examples:

- small grid;
- fixed hand-authored candidate list;
- deterministic random search with a predeclared maximum candidate count.

Preferred for this competition:

```text
small fixed grid / candidate list
```

### CatBoost regression parameters worth testing

Examples:

```text
depth
learning_rate
l2_leaf_reg
random_strength
bagging_temperature or subsample where compatible
```

Do not tune every available CatBoost parameter.

### Search budget

Keep the maximum candidate count bounded in configuration.

Recommended:

```text
<= 16 CatBoost regression candidates
```

Optional smaller LightGBM tuning may be performed only after CatBoost's bounded search is stable.

### Selection within development folds

Rank by:

```text
1. mean MAE
2. mean RMSE
3. MAE stability across folds
4. model simplicity when effectively tied
```

Do not inspect final holdout.

### Effective tie

Define a small engineering tolerance before the real search, for example:

```text
relative MAE difference <= 0.25%
```

If candidates are effectively tied, prefer the simpler/stabler configuration.

Do not invent a tolerance after seeing results.

### Tests

- grid candidate count bounded;
- no duplicate configs;
- stable config IDs;
- final holdout excluded;
- deterministic ranking from synthetic result table.

### Definition of Done

- [ ] regression search budget frozen;
- [ ] all candidates use same folds;
- [ ] provisional regression configuration selected from development folds only.

---

## DT-144 — Tune classifier hyperparameters

**Mark:** [E]  
**Priority:** P1

### Objective

Improve raw late probabilities under frozen probability metrics.

### Primary selection metric

```text
mean development-fold log loss
```

Secondary:

```text
Brier score
fold-to-fold log-loss stability
calibration error diagnostic
```

Do not optimize ROC-AUC as the primary target because Task 1 requires probability quality.

### Candidate parameters

For CatBoost classifier, examples:

```text
depth
learning_rate
l2_leaf_reg
random_strength
bagging/subsample setting where compatible
```

Keep:

```text
auto_class_weights = None
```

unless the team creates an explicitly justified candidate before seeing its score.

### Search budget

Recommended:

```text
<= 16 CatBoost classifier candidates
```

### Tests

- primary ranking uses log loss;
- Brier is secondary;
- AUC cannot become primary by configuration typo;
- no final holdout rows;
- no class rebalancing hidden inside candidate factory.

### Definition of Done

- [ ] bounded classifier search complete;
- [ ] provisional raw classifier config selected from development folds.

---

## DT-145 — Use early stopping

**Mark:** [E]  
**Priority:** P1

### Objective

Control boosting complexity and reduce overfitting without using the final holdout.

### Rules

For every outer development fold:

```text
fold training rows → fit model
fold validation rows → eval_set only
```

Validation labels may be used by the model's early-stopping mechanism because the fold is explicitly the validation set.

They must **not** be used to build features or preprocessing statistics.

### Recommended defaults

```text
max_iterations = 2000
patience_rounds = 100
minimum_useful_iterations = 50
```

These remain configurable.

### Record

Per fold/candidate:

```text
best_iteration
best_validation_metric
stopped_early yes/no
max_iterations
```

### Final training implication

Phase 10 will need a deterministic full-history iteration policy.

Recommended Phase 09 output:

```text
selected_final_iterations = robust summary of best_iteration across development folds
```

Examples:

```text
median best iteration
or
rounded conservative percentile
```

Freeze the chosen rule in DT-156.

Do not use the final holdout to determine final iterations.

### Tests

- early stopping uses development validation only;
- holdout never passed as eval_set;
- best iteration recorded;
- fallback exists when no early stop occurs.

### Definition of Done

- [ ] early stopping active for boosting candidates;
- [ ] iteration metadata recorded;
- [ ] final-iteration rule can be frozen.

---

## DT-146 — Analyze overfitting

**Mark:** [E]  
**Priority:** P1

### Objective

Identify candidates whose apparent development score is driven by excessive training fit, unstable folds, or overly complex boosting.

### Required diagnostics

For each serious candidate record:

```text
train metric
validation metric
train-validation gap
best iteration
fold metric std
worst fold metric
```

For regression:

```text
train MAE vs validation MAE
```

For classifier:

```text
train log loss vs validation log loss
```

### Optional learning curve

For selected CatBoost candidates, retain private train/validation metric histories.

### Warning flags

Examples:

```text
LARGE_GENERALIZATION_GAP
HIGH_FOLD_VARIANCE
EARLY_STOP_AT_VERY_LOW_ITERATION
NEVER_EARLY_STOPPED
UNSTABLE_SEGMENT
```

Thresholds must be configured/documented rather than invented after viewing results.

### Do not

Discard a model solely because its training score is very good.

Use validation performance and stability as the main evidence.

### Definition of Done

- [ ] overfitting diagnostics generated;
- [ ] selected candidate has no unexplained critical stability warning.

---

## DT-147 — Inspect worst regression errors

**Mark:** [E]  
**Priority:** P1

### Objective

Understand the failure modes of the strongest service-time candidate.

### Error definition

```text
absolute_error = abs(service_minutes - pred_service_min)
```

### Private local analysis

For each development fold, store the top configured number of errors privately.

Recommended columns for private investigation:

```text
delivery_id
validation_date
brand
depot
district
dock_type
order_units
order_weight_kg
order_volume_m3
seq_in_route
planned_slack_min
service_minutes
pred_service_min
absolute_error
```

Do not include forbidden actual journey fields unless necessary for a separate private debugging investigation of label integrity.

### Aggregate failure summaries

Generate private summaries by:

```text
brand
depot
dock_type
service-target quantile
order-size quantile
route-position bucket
planned-slack bucket
```

### Important rule

Do not remove worst-error rows simply because they hurt validation.

Possible actions are:

```text
feature hypothesis for future test
robustness note
label-integrity recheck if impossible
no action
```

### Agent boundary

The coding agent implements the report generator but does not inspect the real error rows.

### Tests

- error ordering correct;
- no leakage feature automatically added;
- top-N logic deterministic;
- ties handled deterministically.

### Definition of Done

- [ ] private regression error report generated locally;
- [ ] no validation rows deleted/relabelled based on model error.

---

## DT-148 — Inspect high-confidence classification errors

**Mark:** [E]  
**Priority:** P1

### Objective

Identify confident probability mistakes that may reveal missing structure, instability or calibration problems.

### Default thresholds

Configure before the real run:

```text
high_confidence_late = p >= 0.80
high_confidence_not_late = p <= 0.20
```

### Error types

False positive with high confidence:

```text
p >= 0.80
late_flag = 0
```

False negative with high confidence:

```text
p <= 0.20
late_flag = 1
```

### Private analysis fields

Examples:

```text
delivery_id
validation_date
brand
depot
district
dock_type
seq_in_route
planned_slack_min
pred_late_prob
late_flag
error_type
```

### Aggregate summaries

Report counts/rates by:

```text
brand
depot
district
planned-slack bucket
route position
```

### Do not

- change labels because the model was confident;
- introduce actual arrival into features because it explains the mistake;
- move the confidence threshold after viewing the errors merely to improve appearance.

### Tests

- threshold boundaries exact;
- false-positive/false-negative categorization correct;
- `0.80` counts as high-confidence positive;
- `0.20` counts as high-confidence negative.

### Definition of Done

- [ ] confident-error report generated privately;
- [ ] major failure patterns documented.

---

## DT-149 — Check brand-specific model performance

**Mark:** [E]  
**Priority:** P1

### Objective

Ensure overall gains do not conceal severe performance failures for Fresh, Style or Tech.

### Frozen segments

Use exactly the Phase 07 segment framework.

For:

```text
brand
```

report regression:

```text
n
MAE
RMSE
median_absolute_error
p90_absolute_error
```

and probability:

```text
n
positive_count
negative_count
log_loss
Brier
late_rate
AUC/AP when supported
```

### Comparison

Compare:

- best Phase 08 baseline;
- serious advanced candidates;
- provisional champion.

### Important rule

Brand metrics are diagnostic.

Do not create separate per-brand champion models inside Phase 09 unless that architecture was explicitly introduced, validated and approved before selection.

### Low-support handling

Use Phase 07 low-support flags.

### Definition of Done

- [ ] Fresh/Style/Tech metrics generated where present;
- [ ] no hidden collapse ignored.

---

## DT-150 — Check depot-specific model performance

**Mark:** [E]  
**Priority:** P1

### Objective

Check whether model performance is stable across:

```text
Peliyagoda
Kandy
```

### Metrics

Reuse Phase 07 segment metrics exactly.

### Comparison

Show baseline vs advanced candidate vs provisional champion.

### Do not

- select a different global champion solely because one depot has a tiny metric fluctuation;
- create depot-specific models without a separate validated architecture decision.

### Definition of Done

- [ ] both depots checked;
- [ ] sample counts present;
- [ ] major degradation explicitly flagged.

---

## DT-151 — Generate calibration curve

**Mark:** [E]  
**Priority:** P1

### Objective

Determine whether predicted late probabilities correspond to observed late frequencies.

### Input

Use development-fold out-of-fold probabilities from the provisional raw classifier.

Do not use in-sample training probabilities.

Do not use the final holdout for calibration fitting.

### Required curve

Generate a private reliability table/curve with bins containing:

```text
bin
n
mean_predicted_probability
observed_late_rate
absolute_gap
```

Recommended binning:

```text
quantile bins
```

with a configurable bin count, e.g. 10.

If repeated probabilities prevent 10 unique bins, reduce bins deterministically and report the actual count.

### Calibration metrics

At minimum:

```text
Brier score
ECE / calibration error
```

Log loss remains the primary classifier metric.

### Tests

- perfect calibration synthetic case;
- overconfident case;
- repeated probability handling;
- empty bin avoidance;
- probabilities bounded.

### Definition of Done

- [ ] raw classifier calibration curve produced;
- [ ] calibration quality quantified.

---

## DT-152 — Test probability calibration

**Mark:** [E]  
**Priority:** P1

### Objective

Test whether a post-hoc calibration layer improves the lateness probabilities without leakage.

### Allowed methods

Recommended:

```text
sigmoid
isotonic
```

No method is automatically adopted.

### Leakage-safe calibration evaluation

Use only development out-of-fold predictions.

Recommended chronology-safe procedure:

1. collect OOF raw probabilities from the frozen development folds;
2. attach each OOF prediction's validation date;
3. sort OOF records chronologically;
4. split OOF records by **unique date** into:
   - earlier calibration-fit period;
   - later calibration-evaluation period;
5. fit calibrator using earlier OOF raw probabilities + labels;
6. transform later OOF raw probabilities;
7. compare calibrated vs uncalibrated probabilities on later OOF rows.

Recommended default:

```text
70% earlier OOF dates → calibration fit
30% later OOF dates   → calibration evaluation
```

Same-date atomicity remains mandatory.

### Sigmoid method

Implement a simple local calibrator such as logistic calibration on the raw probability or logit-transformed probability.

If logit is used, clip **only internally for mathematical stability** using a tiny epsilon.

Do not alter stored raw model probabilities.

### Isotonic method

Use isotonic regression only when sample/class support is sufficient.

If the calibration-fit period lacks enough positive/negative examples:

```text
SKIP_ISOTONIC_INSUFFICIENT_SUPPORT
```

Do not force it.

### Final calibrator artifact policy

Phase 09 freezes the chosen calibration method/configuration.

Phase 10 will reconstruct/save the final calibration artifact according to the frozen policy.

### Tests

- chronology-safe split;
- same-date atomicity;
- calibrator fit never sees calibration-eval labels;
- output bounded `[0,1]`;
- isotonic insufficient-support path;
- deterministic result.

### Definition of Done

- [ ] sigmoid evaluated;
- [ ] isotonic evaluated or validly skipped;
- [ ] no holdout used;
- [ ] calibration fit/eval leakage impossible.

---

## DT-153 — Compare uncalibrated vs calibrated probability metrics

**Mark:** [E]  
**Priority:** P1

### Objective

Decide whether calibration is actually beneficial.

### Evaluation population

Use the same later OOF calibration-evaluation period for:

```text
raw probabilities
sigmoid probabilities
isotonic probabilities where available
```

### Metrics

Primary:

```text
log_loss
```

Secondary:

```text
Brier score
ECE
```

Diagnostics:

```text
ROC-AUC
average precision
```

A monotonic calibration transform may leave ranking metrics largely unchanged. That is expected.

### Adoption rule

Freeze the adoption rule **before inspecting the real comparison**.

Recommended:

```text
Adopt calibration only when it improves log loss on the chronological
calibration-evaluation period and does not materially worsen Brier score.
```

If two methods are effectively tied, prefer the simpler/stabler method:

```text
uncalibrated
→ sigmoid
→ isotonic
```

unless isotonic shows a clear, stable benefit.

### Do not

Choose a calibrator because its reliability plot merely looks smoother.

### Output

Private:

```text
calibration_comparison.csv
```

Tracked final configuration stores only:

```text
method name
fit protocol
required parameters
```

not private metrics.

### Definition of Done

- [ ] raw vs calibrated metrics directly comparable;
- [ ] calibration decision can be frozen reproducibly.

---

## DT-154 — Select final Task 1 regression model

**Mark:** [E]  
**Priority:** P1

### Objective

Select the exact service-time model configuration that Phase 10 will retrain.

### Eligibility gate

A candidate is eligible only if:

```text
all required development folds completed
leakage audit passed
feature registry passed
predictions finite
same validation folds used
no unresolved implementation warning
```

### Primary selection rule

Use:

```text
mean development-fold MAE
```

Lower is better.

### Tie-breakers

In order:

```text
1. mean RMSE
2. fold-to-fold MAE stability
3. P90 absolute error
4. simpler model/configuration if effectively tied
```

### Baseline requirement

The advanced model should be compared against the strongest Phase 08 regression baseline.

If an advanced model does not materially improve the baseline, a simpler baseline remains a valid final choice.

Complexity is not itself a reason to select the advanced model.

### Segment diagnostics

Brand/depot metrics may veto a candidate only for a clearly material, well-supported failure pattern.

Do not optimize the champion independently for every segment.

### Output

Private provisional selection:

```text
provisional_service_model_id
feature_profile
parameter_config_id
early_stopping_final_iteration_rule
selection_reason_code
```

### Final holdout

Do not evaluate alternative service candidates on the final holdout.

Only the provisionally frozen service configuration receives the one-time holdout confirmation.

### Definition of Done

- [ ] one provisional service configuration frozen from development results;
- [ ] selection rule documented;
- [ ] final holdout still untouched at development-selection time.

---

## DT-155 — Select final Task 1 lateness model

**Mark:** [E]  
**Priority:** P1

### Objective

Select the exact late-probability architecture/configuration for Phase 10.

### Candidate identity includes

```text
base classifier model family
base hyperparameters
feature profile
final iteration rule
calibration method: none/sigmoid/isotonic
calibration fit protocol
```

### Primary rule

Use development evidence with:

```text
log loss as primary
Brier as secondary
calibration error as diagnostic/tie-breaker
fold stability
```

Do not select by AUC alone.

### Baseline requirement

Compare against:

```text
late constant probability
late grouped rate
late logistic regression
```

from Phase 08.

A complex classifier must earn its complexity through probability-quality improvement.

### Calibration

Treat:

```text
raw classifier
raw + sigmoid
raw + isotonic
```

as distinct probability configurations only when calibration evaluation is valid.

### Final holdout

Only the provisionally selected lateness configuration receives the one-time holdout confirmation.

Do not use the holdout to try several calibrators.

### Definition of Done

- [ ] one provisional late-probability configuration selected;
- [ ] calibration choice frozen before holdout;
- [ ] final holdout still untouched during development selection.

---

## DT-156 — Freeze Task 1 model configuration

**Mark:** [E]  
**Priority:** P1

### Objective

Create the immutable model contract consumed by Phase 10.

### Output

Tracked:

```text
configs/task1_final_models.yaml
```

### Required contents

Example structure:

```yaml
version: 1
seed: 42

validation_contract:
  config: configs/task1_validation.yaml
  development_selection_complete: true
  final_holdout_confirmation_complete: true
  final_holdout_access_count_per_target: 1

features:
  registry: <canonical Phase 06 registry path>
  profile: safe_core_plus_history

service_model:
  family: catboost
  config_id: <frozen id>
  parameters:
    <exact frozen parameters>
  final_iteration_policy:
    method: median_best_iteration
    value: <frozen integer produced locally>
  prediction_postprocessing:
    phase09_clipping: false

lateness_model:
  family: catboost
  config_id: <frozen id>
  parameters:
    <exact frozen parameters>
  final_iteration_policy:
    method: median_best_iteration
    value: <frozen integer>
  calibration:
    method: none | sigmoid | isotonic
    fit_protocol: chronological_oof

selection:
  regression_primary_metric: mae
  lateness_primary_metric: log_loss
  baseline_comparison_completed: true
  brand_diagnostic_completed: true
  depot_diagnostic_completed: true
  calibration_comparison_completed: true
```

### Freeze semantics

After this file is approved:

```text
DO NOT change model family
DO NOT change feature profile
DO NOT change hyperparameters
DO NOT change calibration method
DO NOT change validation metrics
```

unless a genuine implementation blocker is found in Phase 10.

Any such change must be documented and Phase 09 selection evidence revisited.

### One-time holdout confirmation

Before setting:

```text
final_holdout_confirmation_complete: true
```

run the holdout confirmation exactly once for each provisional target configuration.

The local confirmation should verify:

```text
pipeline runs
metrics are finite
performance is not catastrophically inconsistent with development evidence
no feature/schema mismatch
no probability range problem
```

Do not use the holdout to search alternatives.

### Definition of Done

- [ ] service model config frozen;
- [ ] lateness model config frozen;
- [ ] calibration config frozen;
- [ ] final-iteration policy frozen;
- [ ] feature profile frozen;
- [ ] one-time holdout confirmation recorded;
- [ ] Phase 10 can train without making a modelling decision.

---

# 14. Bounded hyperparameter-search rules

The search implementation must be intentionally small and auditable.

## Allowed

```text
small predeclared grid
small manually defined candidate list
fixed-seed bounded random search
```

## Avoid

```text
AutoML frameworks
open-ended Bayesian search
hundreds/thousands of trials
provider-managed optimization services
external model-training APIs
```

## Search records

Every candidate must have a stable ID generated from its configuration, for example:

```text
catreg_d7_lr005_l2_5
catclf_d7_lr005_l2_5
lgbreg_leaves31_lr005
```

Do not use timestamp-only IDs that make comparison hard to reproduce.

---

# 15. Candidate result schema

Every private candidate/fold result should contain at minimum:

```text
experiment_id
candidate_id
model_family
target
feature_profile
fold_id
train_start_date
train_end_date
validation_start_date
validation_end_date
train_n
validation_n
best_iteration
metric_name
metric_value
training_seconds
status
```

Optional:

```text
warning_codes
train_metric
validation_metric
```

Never put row-level validation records into the tracked configuration or documentation.

---

# 16. Overfitting and stability rules

A model with the lowest mean metric may still require caution if:

```text
one fold is dramatically worse
best iteration is unstable
train/validation gap is extreme
segment performance collapses
calibration is poor
```

Recommended warning configuration:

```yaml
overfitting:
  large_relative_gap_warning: 0.25
  fold_cv_warning: 0.20
  very_low_best_iteration: 25
```

These values are engineering defaults and should be frozen before private performance is inspected.

They are warning thresholds, not automatic disqualification rules.

---

# 17. Regression error-analysis protocol

The local private report should distinguish:

```text
model error
label/data integrity issue
valid but difficult observation
rare segment
extreme target
```

Do not automatically modify the dataset based on model residuals.

If a worst-error row appears mathematically impossible:

1. re-run Phase 04 label invariants;
2. re-run Phase 06 feature lineage checks;
3. confirm no join/time corruption;
4. only then determine whether Phase 09 can continue.

---

# 18. Classification error-analysis protocol

For confident errors, inspect only prediction-time-safe explanatory context.

Useful context may include:

```text
brand
depot
district
dock_type
order size
route position
planned slack
monsoon
traffic/road context if enabled
```

Do not explain errors with:

```text
actual arrival
actual travel duration
leave time
```

as though those were usable model features.

They may explain what happened historically, but they are not valid prediction-time inputs.

---

# 19. Calibration protocol details

## Raw prediction source

Calibration experiments must use out-of-fold development predictions.

Never use:

```text
in-sample probabilities
final holdout labels
Task 1 test data
```

## Chronological calibration split

Create from unique OOF dates.

Example:

```text
OOF early dates 70% → calibrator fit
OOF later dates 30% → calibration evaluation
```

All rows from the same date stay together.

## Method selection

Primary:

```text
log loss
```

Secondary:

```text
Brier
```

Calibration error remains diagnostic.

## Probability range

Every calibrated probability must remain:

```text
0 <= p <= 1
```

Do not silently clip a faulty calibrator output except where the calibration algorithm mathematically guarantees/returns bounded outputs.

---

# 20. Development selection protocol

After all development experiments:

## Regression

1. filter to eligible complete candidates;
2. compare mean MAE;
3. inspect RMSE and stability;
4. compare strongest candidate against strongest Phase 08 baseline;
5. check brand/depot diagnostics;
6. freeze provisional service configuration.

## Lateness

1. filter to eligible complete probability candidates;
2. compare mean log loss;
3. inspect Brier and stability;
4. inspect raw calibration;
5. evaluate calibration options chronologically;
6. compare against Phase 08 probability baselines;
7. check brand/depot diagnostics;
8. freeze provisional lateness configuration.

No final holdout yet.

---

# 21. One-time final-holdout confirmation protocol

After provisional selections are frozen:

```text
SERVICE CONFIG FROZEN
LATE CONFIG FROZEN
CALIBRATION FROZEN
FEATURE PROFILE FROZEN
```

then run:

```text
scripts/confirm_task1_final_holdout.py
```

The script must reject execution if provisional selections are not frozen.

It should record locally:

```text
holdout evaluation timestamp
service config ID
lateness config ID
holdout access count
service frozen metrics
late frozen metrics
schema/leakage checks
```

The script should prevent accidental multi-candidate loops.

Recommended guard:

```text
--service-config-id exactly one
--late-config-id exactly one
```

If a previous successful holdout confirmation file exists, require an explicit dangerous override such as:

```text
--acknowledge-holdout-already-consumed
```

and document that Phase 09 no longer has a pristine holdout.

Normal workflow should never need that override.

---

# 22. Required automated tests

All agent-run tests use synthetic data only.

## CatBoost regression

- tiny fit/predict;
- categorical field handling;
- fixed seed;
- finite predictions;
- no forbidden fields;
- no repository artifact leakage.

## CatBoost classifier

- probability output;
- `[0,1]` bounds;
- positive-class column correct;
- no class balancing;
- no resampling.

## LightGBM

- regression smoke test;
- classifier smoke test;
- early stopping callback;
- fold-safe preprocessing;
- probability output.

## XGBoost optional

- optional package detection;
- clean NOT_RUN_OPTIONAL path;
- smoke tests if enabled.

## Model comparison

- identical fold IDs;
- same validation row count;
- missing fold detected;
- baseline/advanced schema compatibility;
- target-specific primary metrics correct.

## Tuning

- predeclared bounded search;
- candidate count cannot exceed config cap;
- config IDs stable;
- no final holdout indexes allowed;
- ranking deterministic.

## Early stopping

- validation fold used as eval set;
- final holdout rejected as eval set;
- best iteration recorded;
- max-iteration fallback handled.

## Overfitting

- train/validation gap calculation;
- warning thresholds deterministic;
- missing train metric handled.

## Regression errors

- absolute error calculation;
- top-N ordering;
- deterministic tie-break;
- no auto-removal.

## Classification errors

- `p >= 0.80 & y=0` confident false positive;
- `p <= 0.20 & y=1` confident false negative;
- exact threshold boundaries;
- normal correct high-confidence rows excluded from error list.

## Segment metrics

- brand segment reuse;
- depot segment reuse;
- low-support handling;
- no per-segment champion selection.

## Calibration curve

- bin counts;
- observed rate;
- mean predicted probability;
- perfect calibration synthetic case;
- overconfidence case;
- repeated probability fallback.

## Calibration testing

- chronological OOF calibration split;
- same-date atomicity;
- calibrator fit cannot access later calibration-eval labels;
- sigmoid output bounded;
- isotonic output bounded;
- insufficient support clean skip.

## Calibration comparison

- log loss is primary;
- Brier secondary;
- deterministic method choice from synthetic result table;
- AUC cannot accidentally become primary.

## Final selection

- incomplete candidates ineligible;
- baseline remains eligible;
- deterministic tie-break;
- holdout not used by development selector;
- calibration identity included in lateness candidate ID.

## Holdout guard

- exactly one service config accepted;
- exactly one late config accepted;
- repeated successful access blocked by default;
- configuration cannot change inside holdout script.

## Final freeze

- required YAML fields present;
- exact parameter serialization;
- feature profile recorded;
- validation contract path recorded;
- calibration policy recorded;
- final iteration values positive;
- no private metric rows embedded in tracked config.

---

# 23. Edge cases

## CatBoost unavailable

This is a blocker because CatBoost is the primary planned advanced model.

Resolve the local environment rather than silently replacing it.

## LightGBM unavailable

Because it is the planned challenger and project dependency, investigate the environment.

If removal is necessary, document the design change before model selection.

## XGBoost unavailable

Not a blocker because DT-141 is optional.

## Very small development fold

Do not change split boundaries ad hoc.

Return to the Phase 07 validation contract if the fold is genuinely unusable.

## Single-class classifier training fold

Do not create a random split to manufacture both classes.

Record the model as unsupported for that fold and investigate whether the Phase 07 design still represents the data appropriately.

## Unseen categorical value

Validation must not fail merely because a category did not occur in fold train.

Use model-safe unknown/missing handling.

## Historical target feature unavailable for unseen entity

Use the frozen Phase 06 fallback hierarchy.

Do not compute a fallback from validation targets.

## CatBoost reaches max iterations

Record:

```text
stopped_early = false
best_iteration = max iteration
```

and inspect overfitting/stability.

Do not automatically double iterations without bounded config revision.

## CatBoost stops almost immediately

Flag as a potential instability/data/preprocessing issue.

## Negative service prediction

During Phase 09:

- do not clip;
- record it;
- consider it in diagnostics.

Phase 10 owns final impossible-output handling.

## Probability exactly 0 or 1

Valid model output range.

Metric implementation may use epsilon internally for numerical log calculations.

Do not change stored probability merely to improve the score.

## Isotonic calibration with few positives

Skip with an explicit support reason.

## Calibrated probability improves Brier but worsens log loss

Because log loss is primary, do not automatically adopt calibration.

Use the frozen adoption rule.

## Strong overall model but weak one brand

Inspect support and materiality.

Do not immediately build brand-specific models.

## Advanced model fails to beat baseline

The baseline is allowed to remain the final choice.

Do not force an advanced model into Phase 10.

## Final holdout is unexpectedly much worse

Do not start trying alternatives on the holdout.

Stop and document that the holdout has been consumed.

Investigate implementation/distribution issues separately.

---

# 24. Phase 09 execution plan

Phase 09 is hybrid.

Recommended checkpoints:

## Checkpoint A — core candidates

```text
DT-138
DT-139
DT-140
DT-141 optional
```

Implement model adapters and synthetic smoke tests.

## Checkpoint B — fair comparison

```text
DT-142
```

Prove all candidates use identical folds/metrics.

## Checkpoint C — bounded tuning and early stopping

```text
DT-143
DT-144
DT-145
```

Implement tuning engine and stopping metadata.

## Checkpoint D — diagnostics

```text
DT-146
DT-147
DT-148
DT-149
DT-150
```

Implement private diagnostics.

## Checkpoint E — calibration

```text
DT-151
DT-152
DT-153
```

Implement raw reliability analysis and chronology-safe calibration evaluation.

## Checkpoint F — development selection

```text
DT-154
DT-155
```

Local experiment produces provisional target configs.

## Checkpoint G — one-time holdout + freeze

```text
DT-156
```

Human runs one-time holdout confirmation for the already frozen provisional configs, then writes/validates the final tracked configuration.

---

# 25. Local development experiment command

Recommended:

```bash
python scripts/run_task1_advanced_models.py \
  --features data/interim/task1_features_train.csv \
  --labels data/interim/task1_training_labels.csv \
  --feature-registry configs/task1_features.yaml \
  --validation-config configs/task1_validation.yaml \
  --baseline-results reports/private/phase08_task1_baselines \
  --model-config configs/task1_advanced_models.yaml \
  --output-dir reports/private/phase09_task1_models
```

The project may use a different canonical Phase 06 registry path. Reuse it rather than creating duplicate sources of truth.

### Safe console output

Example:

```text
PHASE 09 DEVELOPMENT EXPERIMENT: PASS
Development folds completed: YES
Baseline comparison loaded: YES
Advanced candidates completed: YES
Regression tuning completed: YES
Classifier tuning completed: YES
Calibration experiment completed: YES
Provisional service configuration available: YES
Provisional lateness configuration available: YES
Final holdout accessed: NO
Detailed results stored privately.
```

Do not print full metric tables if the command is being observed by an external AI agent.

---

# 26. Human development-selection gate

After running the private experiment, inspect locally:

```text
phase09_model_report.md
service_cv_results.csv
late_cv_results.csv
tuning_service.csv
tuning_late.csv
overfitting_summary.json
brand_metrics.csv
depot_metrics.csv
calibration_comparison.csv
```

Confirm:

```text
all expected folds present
no leakage warning
best candidates beat/compare appropriately with baselines
no unexplained stability failure
calibration decision follows frozen rule
```

Then record a sanitized control result:

```text
LOCAL PHASE 09 DEVELOPMENT EXPERIMENT: PASS
ALL FOLDS COMPLETED: YES
PROVISIONAL SERVICE CONFIG FROZEN: YES
PROVISIONAL LATENESS CONFIG FROZEN: YES
CALIBRATION DECISION FROZEN: YES
FINAL HOLDOUT ACCESSED: NO
```

Do not paste private scores if you do not want them exposed to the external agent.

---

# 27. One-time holdout confirmation command

Only after provisional configs are frozen:

```bash
python scripts/confirm_task1_final_holdout.py \
  --features data/interim/task1_features_train.csv \
  --labels data/interim/task1_training_labels.csv \
  --validation-config configs/task1_validation.yaml \
  --model-config configs/task1_advanced_models.yaml \
  --selection reports/private/phase09_task1_models/provisional_selection.json \
  --output reports/private/phase09_task1_models/holdout_confirmation.json
```

The script must reject multiple candidate lists.

It receives exactly one service config and one late config through the provisional-selection file.

### Expected sanitized result

```text
LOCAL PHASE 09 HOLDOUT CONFIRMATION: PASS
SERVICE CONFIGS EVALUATED ON HOLDOUT: 1
LATENESS CONFIGS EVALUATED ON HOLDOUT: 1
CONFIG CHANGED AFTER HOLDOUT: NO
```

---

# 28. Freeze command

After successful confirmation:

```bash
python scripts/freeze_task1_model_config.py \
  --selection reports/private/phase09_task1_models/provisional_selection.json \
  --holdout-confirmation reports/private/phase09_task1_models/holdout_confirmation.json \
  --advanced-config configs/task1_advanced_models.yaml \
  --output configs/task1_final_models.yaml
```

The freeze script may copy only safe configuration/identifiers into the tracked file.

Do not copy private row-level metrics or predictions.

---

# 29. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-09-task1-advanced-models
```

Recommended commits:

```text
feat(task1): add CatBoost advanced model adapters
feat(task1): add LightGBM and optional XGBoost challengers
feat(task1): add bounded advanced-model tuning
feat(task1): add boosting early-stopping controls
feat(task1): add model stability and error diagnostics
feat(task1): add probability calibration analysis
feat(task1): add deterministic Task 1 model selection
feat(task1): add one-time holdout guard and model freeze tooling
test(task1): add advanced-model and calibration tests
docs(task1): document advanced Task 1 model-selection contract
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
pytest -q
python -m pip check
git status
```

If repository-wide `pytest -q` contains an intentionally private-data integration test, exclude only that specifically documented test and record the exclusion.

Merge only after:

```text
LOCAL PHASE 09 DEVELOPMENT EXPERIMENT: PASS
LOCAL PHASE 09 HOLDOUT CONFIRMATION: PASS
FINAL CONFIG WRITTEN: YES
INDEPENDENT PHASE 09 REVIEW: PASS
```

---

# 30. Phase 09 global STOP conditions

`READY FOR PHASE 10` must remain **NO** if any of the following is unresolved:

- Phase 08 has not passed;
- Phase 07 validation contract is changed after viewing model results;
- different models use different development folds;
- final holdout is used during hyperparameter search;
- final holdout is used to compare multiple alternatives;
- final holdout is repeatedly accessed without explicit invalidation documentation;
- a candidate uses actual journey outcome fields;
- a candidate uses target-derived direct features;
- historical target features are not fold-safe;
- validation targets affect validation features;
- same-date target leakage appears;
- tuning search exceeds its predeclared bounded budget without an approved change;
- AutoML/end-to-end automated modelling is introduced;
- a proprietary remote modelling API is used;
- pre-trained models are used;
- classifier selection switches from log loss to AUC after seeing scores;
- class balancing/resampling is introduced without predeclared justification;
- early stopping uses the final holdout;
- model comparison silently drops failed folds;
- worst-error rows are removed to improve validation;
- high-confidence errors cause labels to be changed without label-integrity evidence;
- calibration is fit on the same rows used to evaluate it;
- calibration uses final holdout labels;
- probabilities leave `[0,1]`;
- final model configuration is not fully reproducible;
- final feature profile is not frozen;
- Phase 10 would still need to decide model family/hyperparameters/calibration;
- synthetic tests fail;
- real local development experiment fails;
- one-time holdout confirmation fails;
- private competition data becomes staged/committed;
- independent review fails.

---

# 31. Phase 09 Definition of Done

Phase 09 passes only when:

- [ ] DT-138 PASS
- [ ] DT-139 PASS
- [ ] DT-140 PASS
- [ ] DT-141 PASS or explicitly `NOT_RUN_OPTIONAL`
- [ ] DT-142 PASS
- [ ] DT-143 PASS
- [ ] DT-144 PASS
- [ ] DT-145 PASS
- [ ] DT-146 PASS
- [ ] DT-147 PASS
- [ ] DT-148 PASS
- [ ] DT-149 PASS
- [ ] DT-150 PASS
- [ ] DT-151 PASS
- [ ] DT-152 PASS
- [ ] DT-153 PASS
- [ ] DT-154 PASS
- [ ] DT-155 PASS
- [ ] DT-156 PASS
- [ ] Phase 08 baselines loaded as frozen benchmark
- [ ] Phase 07 folds reused exactly
- [ ] final holdout excluded from search/tuning
- [ ] CatBoost regression completed
- [ ] CatBoost classifier completed
- [ ] LightGBM challenger completed
- [ ] optional XGBoost decision documented
- [ ] all serious candidates use the same semantic feature profile
- [ ] historical target features obey fold fit-scope
- [ ] regression hyperparameter search bounded
- [ ] classifier hyperparameter search bounded
- [ ] early stopping metadata recorded
- [ ] overfitting diagnostics generated
- [ ] worst regression errors inspected locally
- [ ] high-confidence classification errors inspected locally
- [ ] brand performance checked
- [ ] depot performance checked
- [ ] raw probability calibration curve generated
- [ ] sigmoid calibration tested
- [ ] isotonic tested or validly skipped
- [ ] calibrated vs raw metrics compared chronologically
- [ ] provisional service configuration selected from development only
- [ ] provisional lateness configuration selected from development only
- [ ] calibration choice frozen before final holdout
- [ ] one-time service holdout confirmation completed
- [ ] one-time lateness holdout confirmation completed
- [ ] no configuration changed because of holdout score
- [ ] final iteration rules frozen
- [ ] `configs/task1_final_models.yaml` written
- [ ] full safe test suite passes
- [ ] `python -m pip check` passes
- [ ] private outputs ignored
- [ ] independent review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 09 STATUS: PASS
READY FOR PHASE 10: YES
```

Phase 10 must not perform another model search.

---

# 32. Enhanced Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 09 only.

PHASE:
Task 1 Advanced Modelling

TASK RANGE:
DT-138 through DT-156

EXECUTION MODE:
Hybrid advanced-modelling implementation with broad SAFE engineering autonomy.

You MAY:

- create/edit/refactor Phase 09 source code
- create/edit configs
- create/edit docs
- create synthetic fixtures
- run targeted tests
- run the complete safe regression suite
- inspect stack traces
- diagnose ordinary coding failures
- fix ordinary bugs automatically
- rerun failing tests
- run python -m pip check
- inspect git status/diff
- verify ignore rules
- self-review against Phase 09 Definition of Done

Do NOT stop for ordinary coding/test failures you can safely fix.

STOP only for:

- official competition-rule ambiguity
- need to inspect restricted competition rows
- Phase 08 not actually complete
- conflict with the frozen Phase 06/07/08 contracts
- leakage that cannot be removed safely
- a genuine environment/schema blocker
- a change that would require redesigning frozen validation after seeing private performance

DO NOT START PHASE 10.

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
10. approved PHASE_08_COMPETITION_CONTRACT.md
11. PHASE_09_COMPETITION_CONTRACT.md
12. existing Task 1 feature/validation/baseline utilities

SOURCE PRIORITY:

Official organizer material
>
approved master plan
>
approved phase contracts
>
implementation assumptions

==================================================
COMPETITION RESTRICTIONS
==================================================

Do NOT use:

- pre-trained models
- proprietary API-based modelling/preprocessing
- low-code/no-code AI modelling tools
- fully automated end-to-end modelling tools
- external upload of competition data

All CatBoost/LightGBM/XGBoost models must be trained locally from scratch.

Do NOT inspect in this external-agent context:

data/raw/**
data/interim/**
reports/private/**

Use tracked source/config/docs and synthetic fixtures for agent-run work.

The human will execute real model experiments locally.

==================================================
IMMUTABLE VALIDATION CONTRACT
==================================================

Reuse Phase 07 EXACTLY.

Do NOT create new splits.

Do NOT random split.

Do NOT change holdout boundaries.

Do NOT change primary metrics after observing scores.

Do NOT use the final holdout during:

- candidate comparison
- hyperparameter tuning
- early-stopping search
- calibration fitting
- calibration method selection

Development selection uses Phase 07 development folds only.

Only the already frozen provisional service config and already frozen provisional lateness config may receive one final one-time holdout confirmation.

==================================================
LEAKAGE CONTRACT
==================================================

Never allow direct model features:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag

Historical target-statistic features are allowed ONLY if they pass the existing Phase 06/07 fold-scope transformer contract.

For every validation fold:

fit historical state on fold TRAIN only
then transform validation WITHOUT validation y

Validation-window outcomes must never update later validation rows.

==================================================
CREATE / UPDATE
==================================================

src/task1/advanced_models.py

src/task1/tuning.py

src/task1/calibration.py

src/task1/model_selection.py

scripts/run_task1_advanced_models.py

scripts/confirm_task1_final_holdout.py

scripts/freeze_task1_model_config.py

configs/task1_advanced_models.yaml

configs/task1_final_models.yaml

docs/task1_advanced_modeling_spec.md

tests/test_task1_advanced_models.py

tests/test_task1_tuning.py

tests/test_task1_calibration.py

tests/test_task1_model_selection.py

Private outputs remain under:

reports/private/phase09_task1_models/**

Never commit them.

==================================================
DT-138 — CATBOOST REGRESSION
==================================================

Implement CatBoostRegressor trained locally from scratch.

Use Phase 07 development folds.

Use Phase 06 registry-safe feature profile.

Recommended initial candidate:

loss_function = MAE

eval_metric = MAE

depth = 7

learning_rate = 0.05

l2_leaf_reg = 5

random_seed = 42

allow_writing_files = false

verbose = false

Use early stopping.

Do not clip negative predictions during Phase 09.

Record negative prediction count.

==================================================
DT-139 — CATBOOST LATENESS CLASSIFIER
==================================================

Implement CatBoostClassifier trained locally from scratch.

Use:

loss_function = Logloss

eval_metric = Logloss

random_seed = 42

auto_class_weights = None

allow_writing_files = false

Predict probabilities using positive-class predict_proba output.

Do NOT use hard classes for Task 1 probability evaluation.

Do NOT oversample, undersample or automatically class-weight.

==================================================
DT-140 — LIGHTGBM CHALLENGER
==================================================

Implement LightGBM regression and classification challengers where practical.

Requirements:

- same semantic feature profile
- same Phase 07 folds
- train-only preprocessing
- early stopping
- same frozen metrics
- classifier outputs probability
- no AutoML wrapper

==================================================
DT-141 — OPTIONAL XGBOOST
==================================================

Implement XGBoost regression/classification only if:

- package/environment is already stable or safely installable
- core CatBoost/LightGBM pipeline is complete
- time budget permits

Otherwise return:

NOT_RUN_OPTIONAL

with a documented reason.

Do not let optional XGBoost delay core Task 1 completion.

==================================================
DT-142 — FAIR MODEL COMPARISON
==================================================

All candidates for the same target MUST use:

same fold IDs
same train dates
same validation dates
same target
same metric functions
same approved feature semantics
same segment definitions

Include Phase 08 baselines in comparison.

Regression primary:

mean development-fold MAE

Probability primary:

mean development-fold log loss

Do not hide failed folds.

A candidate missing a required fold is incomplete.

==================================================
DT-143 — REGRESSION TUNING
==================================================

Implement a bounded predeclared search.

NO open-ended AutoML.

Preferred:

small fixed grid / candidate list

Suggested CatBoost dimensions:

depth: 5, 7, 9

learning_rate: 0.03, 0.05

l2_leaf_reg: 3, 7

Keep a configured maximum candidate count, recommended <=16.

Rank development candidates by:

1. mean MAE
2. mean RMSE
3. fold MAE stability
4. simpler model if effectively tied

Do not access final holdout.

==================================================
DT-144 — CLASSIFIER TUNING
==================================================

Use bounded predeclared search.

Primary:

mean log loss

Secondary:

Brier score

Diagnostics:

calibration error
ROC-AUC
average precision

Do NOT optimize AUC as the primary Task 1 classifier criterion.

Keep automatic class weighting disabled by default.

Recommended max candidates <=16.

Do not access final holdout.

==================================================
DT-145 — EARLY STOPPING
==================================================

For each development fold:

fold train = training data
fold validation = eval_set

Do not use final holdout as eval_set.

Recommended:

max iterations = 2000
patience = 100
minimum useful iterations = 50

Record:

best_iteration
best_validation_metric
stopped_early
max_iterations

Freeze a deterministic final-iteration rule for Phase 10, such as median best iteration across development folds.

Do not derive final iteration from final holdout.

==================================================
DT-146 — OVERFITTING ANALYSIS
==================================================

Generate private candidate diagnostics:

train metric
validation metric
gap
best iteration
fold metric std
worst fold

For regression use train/validation MAE.

For classifier use train/validation log loss.

Support configured warnings such as:

LARGE_GENERALIZATION_GAP
HIGH_FOLD_VARIANCE
VERY_LOW_BEST_ITERATION
NEVER_EARLY_STOPPED

Warnings are diagnostic, not automatically disqualifying unless they reveal a genuine problem.

==================================================
DT-147 — WORST REGRESSION ERRORS
==================================================

Implement a PRIVATE local report generator.

absolute_error = abs(service_minutes - pred_service_min)

Store top-N errors privately.

Do not print or commit delivery IDs/error rows.

Generate aggregate failure summaries.

Do NOT remove/relabel rows merely because the model makes a large error.

==================================================
DT-148 — HIGH-CONFIDENCE CLASSIFICATION ERRORS
==================================================

Default frozen thresholds:

p >= 0.80 and y=0
→ high-confidence false positive

p <= 0.20 and y=1
→ high-confidence false negative

Implement private row-level report generation plus aggregate summaries.

Do not change labels because the model is confident.

Do not add actual arrival/travel fields as model predictors to explain errors.

==================================================
DT-149 — BRAND PERFORMANCE
==================================================

Reuse Phase 07 segment metrics for:

Fresh
Style
Tech

Compare baseline, serious advanced candidates and provisional champion.

Include sample counts.

Brand metrics are diagnostic.

Do not select separate brand-specific champions inside this phase.

==================================================
DT-150 — DEPOT PERFORMANCE
==================================================

Reuse frozen segment metrics for:

Peliyagoda
Kandy

Include n.

Use as stability/fairness diagnostic only.

Do not create depot-specific models without a separately validated design.

==================================================
DT-151 — CALIBRATION CURVE
==================================================

Use DEVELOPMENT out-of-fold probabilities from the provisional raw classifier.

Do not use in-sample predictions.

Do not use final holdout.

Generate private reliability table:

bin
n
mean predicted probability
observed late rate
absolute gap

Prefer quantile bins, default 10.

Handle repeated probabilities by reducing bin count deterministically.

Calculate:

Brier
ECE/calibration error

Log loss remains primary overall probability metric.

==================================================
DT-152 — TEST PROBABILITY CALIBRATION
==================================================

Test:

sigmoid
isotonic

Use chronology-safe DEVELOPMENT OOF predictions only.

Procedure:

1. collect OOF raw probabilities
2. attach validation date
3. sort by date
4. split UNIQUE OOF dates into earlier calibration-fit and later calibration-evaluation periods
5. keep same dates atomic
6. fit calibrator on earlier OOF predictions + labels
7. evaluate on later OOF predictions

Recommended split:

70% earlier OOF dates → fit
30% later OOF dates → evaluate

Do not fit calibrator on the same rows used to evaluate it.

Do not use final holdout labels.

If isotonic lacks support:

SKIP_ISOTONIC_INSUFFICIENT_SUPPORT

==================================================
DT-153 — COMPARE CALIBRATION
==================================================

Compare raw vs sigmoid vs isotonic where available on the SAME chronological calibration-evaluation population.

Primary:

log loss

Secondary:

Brier

Diagnostic:

ECE
ROC-AUC
average precision

Freeze adoption rule BEFORE real results:

Adopt calibration only when it improves log loss and does not materially worsen Brier.

If effectively tied prefer:

raw
then sigmoid
then isotonic

unless the more complex method shows a clear stable benefit.

==================================================
DT-154 — SELECT PROVISIONAL FINAL REGRESSION MODEL
==================================================

Eligible candidate must:

- complete all development folds
- pass leakage audit
- have finite predictions
- use frozen feature profile
- use frozen metrics
- have no unresolved implementation blocker

Primary:

mean development-fold MAE

Tie-break:

1. RMSE
2. fold MAE stability
3. P90 absolute error
4. simpler config when effectively tied

Compare against strongest Phase 08 baseline.

A baseline is allowed to remain final if advanced models do not justify their complexity.

Do NOT evaluate multiple service candidates on final holdout.

Freeze exactly one provisional service configuration.

==================================================
DT-155 — SELECT PROVISIONAL FINAL LATENESS MODEL
==================================================

Candidate identity includes:

base classifier
hyperparameters
feature profile
iteration rule
calibration method
calibration protocol

Primary:

log loss

Secondary:

Brier

Use calibration quality/stability as diagnostics.

Compare against Phase 08 probability baselines.

Do not select by AUC alone.

Do not evaluate multiple late configs/calibrators on final holdout.

Freeze exactly one provisional lateness configuration.

==================================================
DT-156 — ONE-TIME HOLDOUT + FREEZE FINAL CONFIG
==================================================

Implement:

scripts/confirm_task1_final_holdout.py

and:

scripts/freeze_task1_model_config.py

Holdout confirmation accepts EXACTLY:

one provisional service config
one provisional late config

No candidate list.

No tuning inside holdout script.

No alternative calibrator search.

If a successful holdout confirmation already exists, block normal rerun.

After one-time confirmation, create:

configs/task1_final_models.yaml

It must contain:

seed
validation contract reference
feature registry/profile
service family
service exact parameters
service final iteration rule/value
lateness family
lateness exact parameters
lateness final iteration rule/value
calibration method/protocol
selection metric names
holdout-confirmation status

Do NOT include private rows/predictions/metric tables in tracked config.

After this config is frozen, Phase 10 must not search models again.

==================================================
TEST REQUIREMENTS
==================================================

Use synthetic data only for agent-run tests.

Add comprehensive tests for:

CatBoost regression
CatBoost classifier
LightGBM regressor/classifier
optional XGBoost detection
same-fold comparison
bounded tuning
stable candidate IDs
early stopping
holdout exclusion
overfitting diagnostics
worst-error ordering
high-confidence error thresholds
brand metrics
depot metrics
calibration bins
chronological calibration split
same-date calibration atomicity
sigmoid calibration
isotonic support checks
raw vs calibrated comparison
regression selector
lateness selector
baseline eligibility
holdout single-config guard
repeated holdout block
final config schema
forbidden feature rejection
historical fit-scope
validation-y isolation

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

For every implementation batch:

1. run targeted tests
2. inspect failures
3. fix ordinary bugs
4. rerun failed tests
5. rerun Phase 09 tests
6. continue when clean

After all Phase 09 code:

run:

pytest -q

If repository-wide pytest contains an explicitly documented private-data integration test, exclude only that known test and report the exclusion.

Then run:

python -m pip check

Then inspect:

git status
git diff

Verify no files under:

data/raw/**
data/interim/**
reports/private/**

are staged.

==================================================
LOCAL DEVELOPMENT COMMAND
==================================================

Implement but DO NOT execute against restricted data in the external-agent context:

python scripts/run_task1_advanced_models.py \
  --features data/interim/task1_features_train.csv \
  --labels data/interim/task1_training_labels.csv \
  --feature-registry configs/task1_features.yaml \
  --validation-config configs/task1_validation.yaml \
  --baseline-results reports/private/phase08_task1_baselines \
  --model-config configs/task1_advanced_models.yaml \
  --output-dir reports/private/phase09_task1_models

If the canonical feature-registry path differs, reuse the existing approved path.

==================================================
DO NOT RUN FINAL HOLDOUT DURING AGENT IMPLEMENTATION
==================================================

The human first runs the local development experiment and inspects the private report.

Only after provisional configs are frozen should the human run:

python scripts/confirm_task1_final_holdout.py ...

The agent should only IMPLEMENT and TEST that guard script with synthetic fixtures.

==================================================
STOP CONDITIONS
==================================================

STOP if:

- Phase 08 is not complete
- Phase 07 validation is changed
- final holdout enters search/tuning/calibration
- different models use different folds
- validation y affects validation X
- same-date leakage appears
- actual journey features enter X
- target-derived fields enter X
- bounded search becomes open-ended AutoML
- proprietary model API is introduced
- pre-trained model is introduced
- class rebalancing appears without explicit predeclared design
- AUC replaces log loss as primary classifier metric
- failed folds are silently dropped
- error rows are removed to improve validation
- calibration fit/eval overlap
- private data access is required
- tests cannot pass without violating an approved contract

==================================================
FINAL SELF-REVIEW
==================================================

Before returning verify:

DT-138 READY
DT-139 READY
DT-140 READY
DT-141 READY or NOT_RUN_OPTIONAL-capable
DT-142 READY
DT-143 READY
DT-144 READY
DT-145 READY
DT-146 READY
DT-147 READY
DT-148 READY
DT-149 READY
DT-150 READY
DT-151 READY
DT-152 READY
DT-153 READY
DT-154 READY
DT-155 READY
DT-156 READY

Phase 07 folds reused exactly

Phase 08 baseline schema reusable

final holdout excluded from development code path

bounded search enforced

historical features fold-safe

raw actual fields absent

target-derived fields absent

classifier outputs probabilities

calibration chronology-safe

holdout guard accepts one config per target only

final config writer exists

all safe tests pass

pip check passes

private artifacts ignored

no Phase 10 implementation added

==================================================
RETURN ONLY
==================================================

PHASE:
09 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-138 READY / FAIL
DT-139 READY / FAIL
DT-140 READY / FAIL
DT-141 READY / FAIL / NOT_RUN_OPTIONAL
DT-142 READY / FAIL
DT-143 READY / FAIL
DT-144 READY / FAIL
DT-145 READY / FAIL
DT-146 READY / FAIL
DT-147 READY / FAIL
DT-148 READY / FAIL
DT-149 READY / FAIL
DT-150 READY / FAIL
DT-151 READY / FAIL
DT-152 READY / FAIL
DT-153 READY / FAIL
DT-154 READY / FAIL
DT-155 READY / FAIL
DT-156 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

PHASE 07 VALIDATION REUSE:
PASS / FAIL

PHASE 08 BASELINE COMPATIBILITY:
PASS / FAIL

BOUNDED SEARCH ENFORCED:
PASS / FAIL

FINAL HOLDOUT USED DURING DEVELOPMENT:
MUST BE NO

HISTORICAL FEATURE FIT-SCOPE:
PASS / FAIL

LEAKAGE AUDIT:
PASS / FAIL

CALIBRATION PROTOCOL:
PASS / FAIL

HOLDOUT SINGLE-CONFIG GUARD:
PASS / FAIL

FINAL CONFIG WRITER:
PASS / FAIL

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local development experiment command.

PHASE 09 STATUS:
AWAITING LOCAL DEVELOPMENT EXPERIMENT

READY FOR PHASE 10:
NO

Then STOP.

Do not run private experiments.
Do not access the final holdout.
Do not begin Phase 10.
```

---

# 33. Enhanced independent Phase 09 review prompt

Use a **fresh Cursor/Codex chat** after:

1. the agent implementation/tests pass;
2. the human local development experiment passes;
3. provisional configs are frozen locally;
4. the one-time holdout confirmation is complete;
5. `configs/task1_final_models.yaml` has been generated.

```text
Perform an independent review of completed WayLoom Datathon Phase 09.

DO NOT:

- open data/raw
- open data/interim
- open reports/private
- inspect private scores or error rows
- run real model experiments
- rerun the final holdout
- modify code initially
- start Phase 10

READ:

1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. PHASE_09_COMPETITION_CONTRACT.md
3. configs/task1_advanced_models.yaml
4. configs/task1_final_models.yaml
5. src/task1/advanced_models.py
6. src/task1/tuning.py
7. src/task1/calibration.py
8. src/task1/model_selection.py
9. scripts/run_task1_advanced_models.py
10. scripts/confirm_task1_final_holdout.py
11. scripts/freeze_task1_model_config.py
12. docs/task1_advanced_modeling_spec.md
13. tests/test_task1_advanced_models.py
14. tests/test_task1_tuning.py
15. tests/test_task1_calibration.py
16. tests/test_task1_model_selection.py
17. relevant tracked Phase 06–08 feature/validation/baseline code
18. .gitignore
19. .cursorignore

HUMAN LOCAL CONTROL RESULTS:

LOCAL PHASE 09 DEVELOPMENT EXPERIMENT: <PASS / FAIL>
ALL FOLDS COMPLETED: <YES / NO>
PROVISIONAL SERVICE CONFIG FROZEN BEFORE HOLDOUT: <YES / NO>
PROVISIONAL LATENESS CONFIG FROZEN BEFORE HOLDOUT: <YES / NO>
CALIBRATION DECISION FROZEN BEFORE HOLDOUT: <YES / NO>

LOCAL PHASE 09 HOLDOUT CONFIRMATION: <PASS / FAIL>
SERVICE CONFIGS EVALUATED ON HOLDOUT: <1 / other>
LATENESS CONFIGS EVALUATED ON HOLDOUT: <1 / other>
CONFIG CHANGED AFTER HOLDOUT: <NO / YES>
FINAL CONFIG WRITTEN: <YES / NO>

Do not ask for private metrics or row-level reports.

==================================================
AUDIT EVERY TASK
==================================================

DT-138:
CatBoost regression is local-from-scratch, registry-safe and uses frozen folds.

DT-139:
CatBoost classifier returns probabilities and does not auto-balance/resample.

DT-140:
LightGBM challenger uses equivalent folds/features/metrics.

DT-141:
XGBoost is either validly implemented or explicitly optional-skipped.

DT-142:
Comparison enforces identical folds and includes frozen Phase 08 baselines.

DT-143:
Regression tuning is bounded/predeclared and excludes final holdout.

DT-144:
Classifier tuning is bounded and uses log loss as primary.

DT-145:
Early stopping uses only development validation folds, never final holdout.

DT-146:
Overfitting/stability analysis exists.

DT-147:
Worst regression error reporting is private and does not delete/relabel rows.

DT-148:
High-confidence classification error logic is correct and private.

DT-149:
Brand performance uses frozen segment metrics and remains diagnostic.

DT-150:
Depot performance uses frozen segment metrics and remains diagnostic.

DT-151:
Calibration curve uses development OOF probabilities, not in-sample predictions.

DT-152:
Calibration fit/evaluation is chronological, same-date atomic and holdout-free.

DT-153:
Raw vs calibrated comparison uses log loss primary and Brier secondary.

DT-154:
Provisional service model selected using development evidence only.

DT-155:
Provisional late model/calibration selected using development evidence only.

DT-156:
One-time holdout guard exists and final model config is completely frozen.

==================================================
CRITICAL LEAKAGE AUDIT
==================================================

Confirm no model input can contain:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag

Confirm historical target features remain fold-train-only.

Confirm validation labels cannot alter validation X.

==================================================
VALIDATION/HOLDOUT AUDIT
==================================================

Confirm:

- Phase 07 folds reused
- no random split
- final holdout absent from tuning
- final holdout absent from calibration
- provisional configs frozen before holdout
- holdout script accepts exactly one config per target
- successful holdout rerun blocked by default
- final config not changed because another holdout candidate looked better

==================================================
COMPETITION RESTRICTION AUDIT
==================================================

Confirm code does not require:

- pre-trained models
- proprietary modelling APIs
- AutoML/end-to-end modelling services
- external competition-data upload

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q

If an explicitly documented private-data integration test exists, exclude only that known test and report it.

Then:

python -m pip check

git status

Do not run private model experiments.
Do not run final holdout.

==================================================
RETURN
==================================================

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

CATBOOST REGRESSION:
PASS / FAIL

CATBOOST CLASSIFIER:
PASS / FAIL

LIGHTGBM CHALLENGER:
PASS / FAIL

OPTIONAL XGBOOST:
PASS / NOT_RUN_OPTIONAL / FAIL

SAME-FOLD COMPARISON:
PASS / FAIL

REGRESSION TUNING:
PASS / FAIL

CLASSIFIER TUNING:
PASS / FAIL

EARLY STOPPING:
PASS / FAIL

OVERFITTING ANALYSIS:
PASS / FAIL

ERROR ANALYSIS:
PASS / FAIL

SEGMENT ANALYSIS:
PASS / FAIL

CALIBRATION ANALYSIS:
PASS / FAIL

DEVELOPMENT-ONLY SELECTION:
PASS / FAIL

ONE-TIME HOLDOUT POLICY:
PASS / FAIL

FINAL CONFIG FREEZE:
PASS / FAIL

LEAKAGE PROTECTION:
PASS / FAIL

COMPETITION RESTRICTION COMPLIANCE:
PASS / FAIL

SYNTHETIC TESTS:
PASS / FAIL

HUMAN DEVELOPMENT EXPERIMENT:
PASS / FAIL

HUMAN HOLDOUT CONFIRMATION:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-138: PASS/FAIL
DT-139: PASS/FAIL
DT-140: PASS/FAIL
DT-141: PASS/NOT_RUN_OPTIONAL/FAIL
DT-142: PASS/FAIL
DT-143: PASS/FAIL
DT-144: PASS/FAIL
DT-145: PASS/FAIL
DT-146: PASS/FAIL
DT-147: PASS/FAIL
DT-148: PASS/FAIL
DT-149: PASS/FAIL
DT-150: PASS/FAIL
DT-151: PASS/FAIL
DT-152: PASS/FAIL
DT-153: PASS/FAIL
DT-154: PASS/FAIL
DT-155: PASS/FAIL
DT-156: PASS/FAIL

PHASE 09 REVIEW:
PASS / FAIL

READY FOR PHASE 10:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not rerun final holdout.
Do not begin Phase 10.
```

---

# 34. Phase 09 completion record template

```markdown
# Phase 09 Completion Record

## Preconditions

- Phase 08 complete: YES / NO
- Phase 08 review: PASS / FAIL
- Phase 08 final holdout untouched: YES / NO

## Advanced candidates

- CatBoost regression: PASS / FAIL
- CatBoost classifier: PASS / FAIL
- LightGBM challenger: PASS / FAIL
- XGBoost: PASS / NOT_RUN_OPTIONAL / FAIL

## Validation integrity

- Phase 07 folds reused exactly: YES / NO
- Same-date atomicity preserved: YES / NO
- Historical target features train-only: YES / NO
- Validation y affects validation X: NO / YES
- Final holdout used during development: NO / YES

## Tuning

- Regression search bounded: YES / NO
- Classifier search bounded: YES / NO
- AutoML used: NO / YES
- Early stopping enabled: YES / NO
- Final iteration rule frozen: YES / NO

## Diagnostics

- Overfitting analysis: PASS / FAIL
- Regression error analysis: PASS / FAIL
- Classification error analysis: PASS / FAIL
- Brand diagnostics: PASS / FAIL
- Depot diagnostics: PASS / FAIL

## Calibration

- Raw reliability curve: PASS / FAIL
- Sigmoid tested: YES / NO
- Isotonic tested or validly skipped: YES / NO
- Calibration split chronological: YES / NO
- Calibration used holdout: NO / YES
- Calibration choice frozen before holdout: YES / NO

## Development selection

- Provisional service config frozen: YES / NO
- Provisional lateness config frozen: YES / NO
- Baselines compared: YES / NO

## One-time holdout

- Service configs evaluated: 1 / other
- Lateness configs evaluated: 1 / other
- Holdout confirmation: PASS / FAIL
- Config changed after holdout: NO / YES

## Freeze

- `configs/task1_final_models.yaml` exists: YES / NO
- Service config complete: YES / NO
- Lateness config complete: YES / NO
- Calibration config complete: YES / NO
- Feature profile frozen: YES / NO

## Tests

- Phase 09 tests: PASS / FAIL
- Full safe regression suite: PASS / FAIL
- `pip check`: PASS / FAIL

## Safety

- Raw/private data exposed to external agent: NO / YES
- Pre-trained model used: NO / YES
- Proprietary modelling API used: NO / YES
- AutoML/end-to-end modelling tool used: NO / YES
- Private reports committed: NO / YES

## Review

- Independent Phase 09 review: PASS / FAIL

## Verdict

PHASE 09 STATUS: PASS / FAIL
READY FOR PHASE 10: YES / NO
```

---

# 35. Final Phase 09 checklist

Before Phase 10:

- [ ] Phase 08 passed.
- [ ] all DT-138–DT-156 tasks are complete or validly optional-skipped where permitted.
- [ ] CatBoost regression candidate completed.
- [ ] CatBoost classifier candidate completed.
- [ ] LightGBM challenger completed.
- [ ] optional XGBoost decision documented.
- [ ] same Phase 07 development folds used by every candidate.
- [ ] Phase 08 baselines included in comparisons.
- [ ] regression search is bounded/reproducible.
- [ ] classifier search is bounded/reproducible.
- [ ] no AutoML/end-to-end modelling framework used.
- [ ] no proprietary modelling API used.
- [ ] no pre-trained model used.
- [ ] early stopping uses development validation only.
- [ ] best iteration metadata recorded.
- [ ] overfitting diagnostics complete.
- [ ] regression error analysis complete locally.
- [ ] classification error analysis complete locally.
- [ ] brand performance reviewed.
- [ ] depot performance reviewed.
- [ ] calibration curve generated from development OOF probabilities.
- [ ] calibration fit/evaluation is chronological.
- [ ] final holdout not used for calibration.
- [ ] calibration decision follows frozen metric rule.
- [ ] provisional service configuration selected on development only.
- [ ] provisional lateness configuration selected on development only.
- [ ] final holdout accessed exactly once per provisional target configuration.
- [ ] no alternative candidates tested after seeing holdout result.
- [ ] final service configuration frozen.
- [ ] final lateness configuration frozen.
- [ ] calibration method frozen.
- [ ] final iteration rule frozen.
- [ ] feature profile frozen.
- [ ] `configs/task1_final_models.yaml` exists and validates.
- [ ] forbidden actual fields absent from all model feature lists.
- [ ] target-derived fields absent from X.
- [ ] full safe test suite passes.
- [ ] `python -m pip check` passes.
- [ ] private outputs remain ignored.
- [ ] independent review passes.
- [ ] no unresolved STOP condition remains.

Only then:

```text
PHASE 09 STATUS: PASS
READY FOR PHASE 10: YES
```

Phase 10 should now perform **deterministic final retraining, model saving, test inference and `submission_task1.csv` generation** without reopening model selection.
