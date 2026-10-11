# PHASE 10 — Task 1 Final Training & Inference

> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks:** DT-157 → DT-173  
> **Task count:** 17  
> **Priority:** P0  
> **Dependency:** Phase 09 PASS  
> **Phase gate:** Saved Task 1 models and an exact, validated `submission_task1.csv` are produced by a deterministic inference pipeline.

---

# 1. Phase objective

Phase 10 converts the frozen Phase 09 Task 1 model choices into final reusable model artifacts and the actual Task 1 competition submission file.

This phase must:

- retrain the final service-time model using the allowed historical development/training data under the frozen Phase 09 configuration;
- retrain the final lateness-probability model under its frozen configuration;
- serialize both models and all required preprocessing/feature state;
- load `task1_test_inputs.csv` and `route_legs_test.csv`;
- reproduce the exact Phase 06 test-feature definitions;
- generate `pred_service_min` and `pred_late_prob`;
- preserve every official `delivery_id` and original Task 1 test row order;
- fill only the official Task 1 submission template;
- export `submission_task1.csv`;
- run hard structural and numerical validation before the file is considered complete.

Phase 10 is **not** a model-search phase. Phase 09 already froze the selected service and lateness configurations. Do not reopen tuning or compare new model families here.

---

# 2. Official Task 1 requirements preserved in this phase

The official Task 1 deliverable predicts, for each test `delivery_id`:

```text
pred_service_min
pred_late_prob
```

The test order input is `task1_test_inputs.csv`; planned route information is provided in `route_legs_test.csv`.

The historical training relationship was:

```text
deliveries_train.route_id + deliveries_train.seq_in_route
↔
route_legs_train.route_id + route_legs_train.seq
```

The equivalent Task 1 test relationship is:

```text
task1_test_inputs.route_id + task1_test_inputs.seq_in_route
↔
route_legs_test.route_id + route_legs_test.seq
```

At prediction time, planned departure/travel/arrival information may be available. Historical actual journey/handling outcomes are not valid Task 1 test features.

Never use as direct Task 1 inference inputs:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag
```

The final Task 1 file must preserve all official test identifiers and their original row ordering and must contain the required prediction columns only.

---

# 3. Frozen upstream contracts

Phase 10 must reuse, not redesign:

```text
Phase 04 — canonical Task 1 labels
Phase 06 — canonical feature pipeline and feature registry
Phase 07 — validation contract and metrics
Phase 08 — baseline reference results
Phase 09 — selected final model configurations
```

The canonical Phase 09 model configuration must be loaded from the approved tracked path, recommended:

```text
configs/task1_final_models.yaml
```

Phase 10 must fail if that file is missing, malformed, unfrozen, or identifies more than one final service or lateness configuration.

---

# 4. Competition-data handling boundary

The agent may fully implement, test, debug, refactor and self-review code using tracked source/config/docs and synthetic fixtures.

The agent must not inspect restricted row-level competition data or private derivatives in an external-model context unless the team has independently verified an organizer-compliant local execution path that does not transmit data externally.

Protected paths remain:

```text
data/raw/**
data/interim/**
reports/private/**
```

The human/operator performs the final real-data training/inference command locally.

---

# 5. Phase 10 task registry

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-157** | [E] | P0 | Phase 09 selected service config | Retrain final service model on allowed full history |
| [ ] | **DT-158** | [E] | P0 | Phase 09 selected lateness config | Retrain final late model |
| [ ] | **DT-159** | [O] | P0 | Phase 9 | Save service model |
| [ ] | **DT-160** | [O] | P0 | Phase 9 | Save lateness model |
| [ ] | **DT-161** | [E] | P0 | DT-157–DT-160 | Build Task 1 inference pipeline |
| [ ] | **DT-162** | [O] | P0 | Phase 9 | Load `task1_test_inputs.csv` |
| [ ] | **DT-163** | [O] | P0 | Phase 9 | Join `route_legs_test.csv` |
| [ ] | **DT-164** | [E] | P0 | Phase 9 | Generate identical test features |
| [ ] | **DT-165** | [O] | P0 | Phase 9 | Generate `pred_service_min` |
| [ ] | **DT-166** | [E] | P0 | Phase 9 | Reject/check impossible negative service predictions |
| [ ] | **DT-167** | [O] | P0 | Phase 9 | Generate `pred_late_prob` |
| [ ] | **DT-168** | [O] | P0 | Phase 9 | Ensure all probabilities are within `[0,1]` |
| [ ] | **DT-169** | [O] | P0 | Phase 9 | Restore official Task 1 row order |
| [ ] | **DT-170** | [O] | P0 | Phase 9 | Preserve every official `delivery_id` |
| [ ] | **DT-171** | [O] | P0 | Phase 9 | Fill official Task 1 template only |
| [ ] | **DT-172** | [O] | P0 | DT-161–DT-171 | Export `submission_task1.csv` |
| [ ] | **DT-173** | [O] | P0 | Phase 9 | Validate Task 1 final file |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO

---

# 6. Required repository additions

Recommended tracked files:

```text
src/task1/
├── final_train.py
├── inference.py
└── submission.py

scripts/
├── train_task1_final_models.py
├── run_task1_inference.py
└── validate_task1_submission.py

configs/
├── task1_final_models.yaml        # produced/frozen in Phase 09
└── task1_inference.yaml

docs/
└── task1_final_inference_spec.md

tests/
├── test_task1_final_train.py
├── test_task1_inference.py
└── test_task1_submission.py
```

Recommended private/generated outputs:

```text
models/
├── task1_service/
│   ├── model.*
│   ├── metadata.json
│   └── feature_schema.json
└── task1_late/
    ├── model.*
    ├── metadata.json
    ├── feature_schema.json
    └── calibration.*              # only if Phase 09 froze calibration

outputs/
└── submission_task1.csv

reports/private/phase10_task1_final/
├── training_summary.json
├── inference_summary.json
├── feature_parity.json
├── prediction_validation.json
└── submission_validation.json
```

If model artifacts are intentionally excluded from Git because of project size/policy, document the exact storage/reproduction method. The final competition package still needs the saved final models required by the challenge deliverables.

---

# 7. Recommended Phase 10 configuration

Create or update:

```text
configs/task1_inference.yaml
```

Recommended structure:

```yaml
version: 1

final_model_config:
  path: configs/task1_final_models.yaml
  require_frozen: true

feature_registry:
  path: configs/task1_features.yaml

inputs:
  task1_test_filename: task1_test_inputs.csv
  route_legs_test_filename: route_legs_test.csv
  submission_template_filename: submission_task1.csv

outputs:
  submission_path: outputs/submission_task1.csv
  service_model_dir: models/task1_service
  late_model_dir: models/task1_late

service_prediction:
  negative_policy: fail_or_apply_frozen_policy
  require_finite: true

late_prediction:
  require_probability: true
  min_probability: 0.0
  max_probability: 1.0

submission:
  preserve_original_order: true
  preserve_all_delivery_ids: true
  template_only: true
  exact_required_columns: true
```

`negative_policy` must be resolved by the frozen Phase 09/Phase 10 design before real inference. Do not decide it after seeing test predictions.

---

# 8. DT-157 — Retrain final service model on allowed full history

**Priority:** P0  
**Execution:** Critical task

## Objective

Train the exact Phase 09-selected service-time model configuration on the allowed final historical training population.

## Inputs

```text
canonical Task 1 training labels
canonical Phase 06 features
configs/task1_final_models.yaml
feature registry
```

## Required behavior

Load exactly one frozen service configuration. Validate:

```text
model family
hyperparameters
feature profile
iteration policy/value
seed
preprocessing policy
historical-feature policy
```

The final training population may use all historical rows permitted after the one-time Phase 09 holdout confirmation because Phase 09 has already finished model selection. Do not use Task 1 test rows as labelled training examples.

If the selected configuration uses fit-dependent historical target features, fit those features using historical training targets only according to the Phase 06 frozen final-training policy.

No further hyperparameter tuning is allowed.

## Recommended API

```python
def train_final_service_model(
    X_train,
    y_service,
    feature_registry,
    final_config,
):
    ...
```

## Required checks

```text
one row per delivery_id
no forbidden actual fields in X
no target-derived fields in X
feature ordering frozen
all required features available
no duplicate feature names
training target finite and >= 0
seed/config matches Phase 09
```

## Tests

Synthetic tests must prove:

```text
frozen config is honored
unknown model family rejected
missing feature rejected
forbidden feature rejected
target not present in X
seed propagated
training deterministic within supported tolerance
no tuning loop occurs
```

## STOP conditions

Stop if:

```text
Phase 09 final service config missing/unfrozen
multiple service configurations present
feature registry mismatch
forbidden fields present
training requires test labels
new tuning logic appears
```

## Definition of Done

```text
final service model trained using exact frozen config
training metadata generated
no search performed
all safety assertions pass
```

---

# 9. DT-158 — Retrain final lateness model

**Priority:** P0  
**Execution:** Critical task

## Objective

Train the exact frozen Phase 09 lateness-probability model configuration on the allowed final historical population.

## Inputs

```text
canonical Task 1 features
late_flag target
Phase 09 final lateness config
optional frozen calibration config
```

## Required behavior

Reuse exactly:

```text
classifier family
hyperparameters
feature profile
iteration policy
class-weight/resampling policy
seed
calibration method, if any
```

Do not introduce:

```text
new class weighting
oversampling
undersampling
new threshold tuning
new calibration method
new feature subset
```

If Phase 09 selected raw probabilities, do not add calibration now.

If Phase 09 selected a calibration method, refit the final calibrator using only the approved historical procedure specified in the frozen config. Do not use Task 1 test outcomes.

## Required checks

```text
late_flag ∈ {0,1}
no target in X
no actual journey features in X
classifier exposes probability output
positive-class index resolved deterministically
```

## Tests

Synthetic:

```text
probability-capable model required
predict_proba positive-class extraction correct
single-class invalid final training handled explicitly
frozen calibration setting honored
new calibration search absent
```

## STOP conditions

Stop if:

```text
final lateness config missing/unfrozen
classifier cannot produce probabilities
calibration protocol differs from Phase 09
forbidden feature present
new tuning begins
```

## Definition of Done

```text
final lateness model trained
probability pipeline finalized
calibration state finalized if applicable
all assertions pass
```

---

# 10. DT-159 — Save service model

**Mark:** [O]  
**Priority:** P0

## Objective

Persist the final service model and every state object required for deterministic inference.

## Required artifacts

Recommended:

```text
models/task1_service/model.*
models/task1_service/metadata.json
models/task1_service/feature_schema.json
```

If preprocessing is not embedded inside the serialized model pipeline, also save the exact preprocessor/state object.

## Metadata

Include:

```text
phase = 10
task = task1_service
model family
config ID
seed
feature schema/hash
feature registry version
library versions
training row count
training date range
created timestamp
git commit if available
```

Do not store private row-level training data in model metadata.

## Serialization verification

Immediately after save in synthetic/unit testing:

```text
save model
reload model
predict same synthetic X
assert equivalent predictions
```

Use the native recommended serializer for the selected model family when possible.

## STOP conditions

Stop if reload changes feature schema or predictions beyond expected numerical tolerance.

---

# 11. DT-160 — Save lateness model

**Mark:** [O]  
**Priority:** P0

## Objective

Persist the final lateness probability model, feature schema and calibration state.

Recommended artifacts:

```text
models/task1_late/model.*
models/task1_late/metadata.json
models/task1_late/feature_schema.json
models/task1_late/calibration.*
```

The calibration artifact is required only if the frozen Phase 09 configuration selected a calibrated probability pipeline.

## Required serialization test

```text
original raw probabilities
save
reload
recompute probabilities
apply calibration if configured
assert equivalent final probabilities
```

Verify the same positive-class mapping after reload.

## STOP conditions

Stop if:

```text
class ordering changes
calibration artifact missing when required
probability output differs materially after reload
```

---

# 12. DT-161 — Build Task 1 inference pipeline

**Priority:** P0  
**Execution:** Critical task

## Objective

Create a single deterministic inference entry point that converts official test inputs into the exact official Task 1 submission.

## Recommended API

```python
def run_task1_inference(
    task1_test_inputs,
    route_legs_test,
    submission_template,
    service_model_bundle,
    late_model_bundle,
    feature_registry,
    inference_config,
) -> pd.DataFrame:
    ...
```

## Required pipeline order

```text
1. capture original test row order
2. validate test identifiers/schema
3. join route_legs_test using official composite key
4. validate one-to-one join
5. generate canonical Phase 06 test features
6. validate exact feature schema/parity
7. load saved service model
8. generate service predictions
9. apply frozen service post-processing policy only
10. load saved lateness model
11. generate raw probability
12. apply frozen calibration only if selected
13. validate numerical predictions
14. restore official row order
15. fill official template
16. validate final submission
17. export
```

No training code should execute in normal inference mode.

## Separation requirement

The inference script must work from saved artifacts. It must not silently retrain models when a model file is missing.

## Determinism

Running inference twice against identical saved artifacts and inputs must produce byte-equivalent or numerically equivalent CSV content, apart from intentionally variable file metadata not included in the CSV.

## Tests

Synthetic end-to-end inference including:

```text
model load
join
feature generation
schema ordering
predictions
row restoration
template fill
submission validation
```

## STOP conditions

Stop if inference requires training targets or automatically retrains.

---

# 13. DT-162 — Load `task1_test_inputs.csv`

**Mark:** [O]  
**Priority:** P0

## Objective

Load the official Task 1 test input while preserving its exact identity and order.

## Required behavior

Before any joins/sorts, create an internal immutable row-order marker:

```python
__official_row_order = np.arange(len(test))
```

Do not write this marker to the submission.

Validate:

```text
delivery_id present
delivery_id nonblank
delivery_id unique
route_id present
seq_in_route present
expected required prediction-time columns present
```

Do not sort the original test input in place.

## Tests

Synthetic scrambled IDs and arbitrary order must survive through final restoration.

## STOP conditions

Any duplicate or missing official `delivery_id`.

---

# 14. DT-163 — Join `route_legs_test.csv`

**Mark:** [O]  
**Priority:** P0  
**Execution:** Critical join

## Official join

```text
task1_test_inputs.route_id + seq_in_route
↔
route_legs_test.route_id + seq
```

Use a left join for integrity checking with:

```text
validate = one_to_one
indicator = true
```

Every Task 1 test order should map to exactly one route leg.

Required semantic check:

```text
task1_test_inputs.outlet_id == route_legs_test.to_outlet
```

when both fields are available.

Do not use:

```text
delivery_id
outlet_id alone
route_id alone
```

as substitute join keys.

## Required invariants

```text
joined row count == original test row count
_merge == both for every row
no duplicate delivery_id after join
no join multiplication
outlet/destination consistency
```

## Tests

Synthetic:

```text
perfect one-to-one join
unmatched test order fails
duplicate route key fails
wrong destination fails
same seq on different route IDs valid
```

## STOP conditions

Any unmatched or duplicate test join.

---

# 15. DT-164 — Generate identical test features

**Priority:** P0  
**Execution:** Highest-risk inference task

## Objective

Generate test features using the **same feature definitions, registry and ordering used for final training**.

## Core rule

Do not write a separate ad hoc "test feature" implementation.

Reuse canonical Phase 06 feature-building functions.

## Required parity

For the selected model profile:

```text
training feature names == test feature names
training feature order == test feature order
semantic types compatible
categorical handling compatible
no target columns in test X
```

## Historical feature rule

If the final model uses leakage-safe historical target features:

```text
fit historical feature state on allowed full historical training data
freeze state
transform Task 1 test rows without test labels
```

Never update the historical state from one test row's unknown outcome to another test row.

The entire Task 1 test set is unseen.

## Optional context

Road/traffic features may be included only if they were enabled and frozen in the final selected feature profile and can be generated from legitimate prediction-time test context.

Do not silently introduce or remove features in Phase 10.

## Schema hash

Recommended:

```text
feature_schema.json
```

contains ordered feature names and semantic/dtype metadata.

Inference must compare generated test schema against saved training schema and fail on mismatch.

## Tests

Synthetic:

```text
same feature columns
same feature order
unseen categorical values handled by frozen pipeline
historical feature transform does not require test y
forbidden columns absent
schema mismatch fails
```

## STOP conditions

Any train/test feature drift blocks inference.

---

# 16. DT-165 — Generate `pred_service_min`

**Mark:** [O]  
**Priority:** P0

## Objective

Generate one service-time prediction for every official Task 1 test delivery.

## Required behavior

Use the saved final service model only.

Prediction output must be:

```text
numeric
finite
one value per test delivery
```

Do not round during model inference unless the official template or frozen configuration explicitly requires it.

Recommended storage dtype:

```text
float64 or stable numeric equivalent
```

## Tests

Synthetic:

```text
prediction length = input length
finite values
repeat inference stable
saved model used rather than retrained model
```

---

# 17. DT-166 — Reject/check impossible negative service predictions

**Priority:** P0

## Objective

Enforce a predeclared, auditable physical-output policy for service duration.

A service duration cannot be physically negative. However, the treatment of a negative model prediction must be frozen before examining the real test predictions.

## Preferred policy hierarchy

If the final selected model family inherently guarantees nonnegative outputs and all predictions are nonnegative:

```text
PASS with no transformation
```

If the frozen Phase 09/Phase 10 configuration explicitly defines:

```text
clip_to_zero
```

then apply:

```python
pred_service_min = np.maximum(raw_pred, 0.0)
```

and record the number clipped privately.

If no negative policy was frozen and negative predictions occur:

```text
FAIL
```

Do not invent a post-processing rule after looking at test outcomes.

Do not silently take absolute value.

Do not replace negative predictions with a target median unless that exact policy was predeclared.

## Required private diagnostics

```text
negative_raw_prediction_count
minimum_raw_prediction
postprocessing_policy
postprocessed_count
```

Do not expose row-level test predictions in tracked docs.

## Tests

Synthetic:

```text
no-negative pass
clip policy when frozen
fail policy when no clipping frozen
absolute-value hack rejected
NaN/Inf rejected
```

---

# 18. DT-167 — Generate `pred_late_prob`

**Mark:** [O]  
**Priority:** P0

## Objective

Generate one final lateness probability per Task 1 test delivery.

## Required pipeline

```text
saved classifier
→ positive-class probability
→ frozen calibration if selected
→ final pred_late_prob
```

Do not use:

```text
hard class predictions
thresholded 0/1 output
```

unless the probability itself legitimately equals 0 or 1.

## Positive-class identity

Explicitly confirm that the extracted probability corresponds to:

```text
late_flag = 1
```

Do not assume column index 1 without verifying saved class metadata.

## Tests

Synthetic:

```text
class order [0,1]
class order metadata validated
positive-class extraction
calibrated/raw path according to config
one probability per row
```

---

# 19. DT-168 — Ensure probabilities are within `[0,1]`

**Mark:** [O]  
**Priority:** P0

## Required assertions

```python
np.isfinite(pred_late_prob).all()
(pred_late_prob >= 0).all()
(pred_late_prob <= 1).all()
```

Do not silently clamp a broken probability pipeline to `[0,1]` unless the frozen selected calibration/model API mathematically expects tiny floating-point tolerance and that treatment is explicitly documented.

A genuine value below 0 or above 1 is a blocker.

## Tests

```text
0 valid
1 valid
0.5 valid
-0.001 invalid
1.001 invalid
NaN invalid
Inf invalid
```

---

# 20. DT-169 — Restore official Task 1 row order

**Mark:** [O]  
**Priority:** P0  
**Execution:** Critical submission task

## Objective

Restore exact original row order from `task1_test_inputs.csv` after joins, feature transformations and predictions.

## Required pattern

At initial load:

```text
__official_row_order
```

After predictions:

```text
sort by __official_row_order
```

Then remove the internal marker.

Do not sort the final submission by:

```text
delivery_id
route_id
planned arrival
prediction
```

unless that happens to be the original official ordering.

## Required proof

```text
final_submission.delivery_id sequence
==
original_task1_test_inputs.delivery_id sequence
```

Exact ordered sequence comparison, not set comparison.

## Tests

Use intentionally non-sorted synthetic IDs.

---

# 21. DT-170 — Preserve every official `delivery_id`

**Mark:** [O]  
**Priority:** P0

## Required invariants

```text
row count unchanged
no missing delivery_id
no added delivery_id
no duplicate delivery_id
no modified delivery_id
same ordered sequence as official input
```

Recommended checks:

```python
assert len(output) == len(test)
assert output["delivery_id"].is_unique
assert output["delivery_id"].tolist() == test["delivery_id"].tolist()
```

Do not regenerate IDs.

Do not normalize/strip IDs unless the official source itself is normalized upstream and proven identical.

---

# 22. DT-171 — Fill official Task 1 template only

**Mark:** [O]  
**Priority:** P0

## Objective

Use the organizer-provided `submission_task1.csv` as the structural authority for the final output.

## Required approach

Load the official template locally.

Validate its identifier sequence against the official test input where appropriate.

Fill only prediction fields:

```text
pred_service_min
pred_late_prob
```

Preserve template-defined identifier column(s).

Do not append debug columns such as:

```text
route_id
model_name
raw_probability
raw_service_prediction
row_order
feature_count
```

## Template-first strategy

Recommended:

```text
load template
verify identifier sequence
assign predictions by exact aligned order or delivery_id with explicit parity assertion
validate exact final column set/order
```

Do not hand-create the CSV schema if an official template exists.

## Tests

Synthetic official-template fixture:

```text
exact columns
exact column order
extra column fails
missing prediction column fails
identifier mismatch fails
```

---

# 23. DT-172 — Export `submission_task1.csv`

**Mark:** [O]  
**Priority:** P0

## Required output

```text
outputs/submission_task1.csv
```

The output must be deterministic and written without an unintended index column.

Recommended:

```python
submission.to_csv(path, index=False)
```

Write only after all in-memory validation passes.

Prefer atomic writing:

```text
write temporary file
validate/read-back
rename to final path
```

This reduces the risk of leaving a corrupt partial final output.

## Read-back verification

After export:

```text
read file again
check exact columns
check exact row count
check exact ordered IDs
check numerical finiteness
check probability bounds
```

## STOP conditions

Do not leave a file named `submission_task1.csv` as the official final artifact if read-back validation fails.

---

# 24. DT-173 — Validate Task 1 final file

**Mark:** [O]  
**Priority:** P0  
**Execution:** Final Phase 10 gate

## Objective

Prove the exported Task 1 file is structurally submission-ready.

## Hard validation checklist

Required:

```text
file exists
file readable
exact official filename
exact official template column names
exact official template column order
row count equals Task 1 test row count
all official delivery_id values preserved
ordered delivery_id sequence preserved
no duplicate delivery_id
no added IDs
no removed IDs
pred_service_min numeric
pred_service_min finite
pred_service_min obeys frozen nonnegative policy
pred_late_prob numeric
pred_late_prob finite
0 <= pred_late_prob <= 1
no NaN in required output
no Inf
no accidental CSV index column
no extra debug columns
```

## Inference reproducibility check

Recommended final gate:

```text
run inference twice using same saved artifacts
compare generated in-memory predictions / CSV content
```

They must match within exact or defined numerical tolerance.

## Saved-model inference requirement

Validation must prove the final submission was generated by **reloading the saved service and lateness model artifacts**, not by relying on model objects left in notebook/process memory after training.

This supports the later final-notebook competition requirement.

## Private validation output

```text
reports/private/phase10_task1_final/submission_validation.json
```

Recommended summary fields:

```text
status
row_count
id_integrity
row_order_integrity
service_finite
service_negative_count
probability_finite
probability_min
probability_max
exact_template_match
saved_model_reload_verified
repeat_inference_verified
```

Do not print row-level predictions.

## Definition of Done

DT-173 passes only when every hard final-file assertion succeeds.

---

# 25. Canonical training vs inference architecture

Recommended architecture:

```text
Phase 09 frozen config
        ↓
Phase 10 final training
        ↓
Saved model bundles
        ↓
Fresh process / reload
        ↓
Official Task 1 test inputs
        +
route_legs_test
        ↓
Canonical Phase 06 feature pipeline
        ↓
Saved feature schema validation
        ↓
Service model prediction
        +
Lateness probability prediction
        ↓
Frozen post-processing/calibration
        ↓
Restore official row order
        ↓
Fill official template
        ↓
Validate
        ↓
outputs/submission_task1.csv
```

Training code and inference code should share reusable transformation functions but remain operationally separable.

---

# 26. Saved model bundle contract

Each final model bundle should be self-describing enough for later notebook/reproduction phases.

Recommended service metadata:

```json
{
  "task": "task1_service",
  "model_family": "...",
  "config_id": "...",
  "feature_schema_file": "feature_schema.json",
  "prediction_column": "pred_service_min",
  "postprocessing_policy": "...",
  "seed": 42
}
```

Recommended lateness metadata:

```json
{
  "task": "task1_late",
  "model_family": "...",
  "config_id": "...",
  "feature_schema_file": "feature_schema.json",
  "prediction_column": "pred_late_prob",
  "positive_class": 1,
  "calibration": "raw|sigmoid|isotonic",
  "seed": 42
}
```

Do not hardcode example family names if Phase 09 selected something else.

---

# 27. Feature parity rules

The following must be identical between final training and test inference:

```text
feature names
feature order
categorical semantic definitions
numerical semantic definitions
missing-value policy
encoder/imputer/scaler state
historical feature definitions
optional feature enable/disable states
```

The following may differ only in values, not definitions:

```text
category levels encountered
road/traffic coverage
planned route values
calendar values
```

Unseen categories must be handled by the frozen preprocessing pipeline rather than by changing feature definitions.

---

# 28. Test strategy

Create comprehensive synthetic tests.

## Final training

```text
frozen service config honored
frozen late config honored
no tuning loops
forbidden fields rejected
target excluded from X
missing frozen config fails
```

## Serialization

```text
save/reload service model
save/reload lateness model
same predictions after reload
calibrator reload if applicable
feature schema reload
```

## Inference

```text
no training code called
one-to-one test route join
unmatched test order fails
duplicate test route key fails
destination mismatch fails
identical feature schema
identical feature ordering
historical features need no test labels
```

## Service prediction

```text
correct length
finite
negative policy frozen
negative policy behavior tested
```

## Lateness probability

```text
correct length
finite
positive class correct
probability within [0,1]
calibration path correct
```

## Row integrity

```text
original arbitrary order restored
all delivery IDs preserved
no duplicate IDs
no added IDs
no missing IDs
```

## Template

```text
exact columns
exact order
no debug columns
```

## Export

```text
index=False
read-back valid
atomic-write behavior
```

## End-to-end

```text
saved artifacts loaded in fresh synthetic path
inference run twice
same final output
```

---

# 29. Important edge cases

## Unseen categorical value in Task 1 test

Use the frozen preprocessing policy. Do not retrain an encoder on test data.

## Missing optional road/traffic value

Use the frozen Phase 06 missing/disabled policy. Do not invent a new Phase 10 fallback.

## Test route crosses midnight

Use the frozen planned-time feature logic from Phase 06. Do not use actual-event logic because actual events do not exist in test data.

## One-stop route

Respect the frozen route-position policy, e.g. normalized route fraction = 0 if that was the Phase 06 definition.

## Historical target features

Fit only from historical training data. Treat the whole test set as unlabeled unseen data.

## Service model predicts negative value

Apply only the predeclared Phase 10/Phase 09 policy. Never improvise after inspecting test outputs.

## Probability equals exactly 0 or 1

Valid if legitimately produced by the frozen pipeline. Do not alter it solely because it may affect log loss; no test labels exist anyway.

## Template identifier ordering differs unexpectedly

Stop and verify against official sources. Do not reorder blindly.

## Model artifact missing

Inference must fail. It must not silently retrain.

## Version mismatch during reload

Report clearly. Do not quietly deserialize with an incompatible fallback that changes model behavior.

---

# 30. Recommended execution checkpoints

Phase 10 should use controlled small batches.

```text
Checkpoint A
DT-157–DT-160
Final training + serialization
        ↓ STOP + tests

Checkpoint B
DT-161
Inference orchestrator
        ↓ STOP

Checkpoint C
DT-162–DT-164
Test loading + official join + exact features
        ↓ STOP + critical review

Checkpoint D
DT-165–DT-168
Predictions + numerical validity
        ↓ STOP

Checkpoint E
DT-169–DT-171
Official order + IDs + template
        ↓ STOP

Checkpoint F
DT-172–DT-173
Export + final validation
        ↓ STOP

Human local real-data run
        ↓
Independent Phase 10 review
```

Do not allow the agent to automatically start Phase 11.

---

# 31. Local commands

Recommended final training command:

```bash
python scripts/train_task1_final_models.py \
  --features data/interim/task1_features_train.csv \
  --labels data/interim/task1_training_labels.csv \
  --feature-registry configs/task1_features.yaml \
  --final-config configs/task1_final_models.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --report-dir reports/private/phase10_task1_final
```

Recommended inference command:

```bash
python scripts/run_task1_inference.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --feature-registry configs/task1_features.yaml \
  --final-config configs/task1_final_models.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --template submission_task1.csv \
  --output outputs/submission_task1.csv \
  --report-dir reports/private/phase10_task1_final
```

Recommended validation command:

```bash
python scripts/validate_task1_submission.py \
  --test-input data/raw/.../task1_test_inputs.csv \
  --template data/raw/.../submission_task1.csv \
  --submission outputs/submission_task1.csv \
  --report-dir reports/private/phase10_task1_final
```

Prefer manifest/path-resolution rather than hardcoding raw extraction subdirectories.

PowerShell may run the same commands on one line.

---

# 32. Local real-data success status

After the human local run, return only sanitized status to the review agent:

```text
LOCAL PHASE 10 FINAL TRAINING: PASS
SERVICE MODEL SAVED: YES
LATENESS MODEL SAVED: YES
SAVED-MODEL RELOAD: PASS
TASK 1 TEST JOIN: PASS
UNMATCHED TEST ORDERS: 0
FEATURE PARITY: PASS
FORBIDDEN TEST FEATURES: 0
SERVICE PREDICTIONS FINITE: YES
NEGATIVE SERVICE POLICY: PASS
LATE PROBABILITY RANGE: PASS
ROW ORDER: PASS
DELIVERY ID INTEGRITY: PASS
OFFICIAL TEMPLATE MATCH: PASS
SUBMISSION EXPORT: PASS
FINAL FILE VALIDATION: PASS
```

Do not paste the actual test predictions or private reports.

---

# 33. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-10-task1-final
```

Recommended commits:

```text
feat(task1): add final model training pipeline
feat(task1): persist final service and lateness models
feat(task1): add deterministic saved-model inference
feat(task1): add Task 1 test join and feature parity guards
feat(task1): add final prediction validation
feat(task1): add official template submission writer
test(task1): add final training and inference tests
docs(task1): document final Task 1 inference contract
```

Before every commit:

```bash
git status
git diff --cached --name-only
```

Never stage restricted/private data paths accidentally.

Before merge:

```bash
pytest -q
python -m pip check
git status
```

If full pytest contains explicitly documented private-data integration tests, exclude only those specific tests and report that fact.

Merge only when:

```text
LOCAL PHASE 10: PASS
INDEPENDENT PHASE 10 REVIEW: PASS
```

---

# 34. Global STOP conditions

Phase 10 must remain incomplete if any of the following is true:

```text
Phase 09 is not PASS
final model configuration is not frozen
new model tuning occurs
new feature selection occurs
final holdout is reopened for tuning
actual journey field enters inference X
target-derived field enters inference X
training/test feature schema differs
historical feature transform uses test labels
Task 1 test order has no matching route leg
a test order maps to multiple route legs
outlet destination mismatch exists
saved model cannot reload
inference silently retrains
service prediction is NaN/Inf
negative service output violates frozen policy
late probability is NaN/Inf
late probability outside [0,1]
positive class cannot be identified
original row order is not restored
delivery ID sequence differs
an official delivery_id is added/removed/duplicated
official template schema differs
extra debug columns exist
CSV read-back fails
repeat inference is not deterministic
private competition records are exposed to the agent
required synthetic/regression tests fail
independent review fails
```

---

# 35. Phase 10 Definition of Done

Phase 10 passes only when:

```text
DT-157 PASS
DT-158 PASS
DT-159 PASS
DT-160 PASS
DT-161 PASS
DT-162 PASS
DT-163 PASS
DT-164 PASS
DT-165 PASS
DT-166 PASS
DT-167 PASS
DT-168 PASS
DT-169 PASS
DT-170 PASS
DT-171 PASS
DT-172 PASS
DT-173 PASS
```

And all of the following are true:

```text
exact frozen service configuration used
exact frozen lateness configuration used
no Phase 10 tuning/search
final service model saved
final lateness model saved
calibration artifact saved if required
saved models reload successfully
inference runs from saved artifacts
Task 1 official test join is one-to-one
unmatched test orders = 0
feature parity passes
ordered feature schema matches
forbidden actual fields = 0
target-derived inference features = 0
service predictions finite
service negative-output policy passes
late probabilities finite
all late probabilities in [0,1]
original official row order restored
every delivery_id preserved exactly once
official template only
outputs/submission_task1.csv exists
CSV read-back passes
repeat inference passes
tests pass
pip check passes
private/restricted paths remain protected
independent review passes
```

Then:

```text
PHASE 10 STATUS: PASS
TASK 1 FINAL OUTPUT: READY
READY FOR NEXT PHASE: YES
```

The file is ready for later global submission validation, clean reproduction and packaging phases. Do not submit/package the overall Datathon yet.

---

# 36. Enhanced Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 10 only.

PHASE:
Task 1 Final Training & Inference

TASK RANGE:
DT-157 through DT-173

EXECUTION MODE:
High-risk controlled autonomous implementation with full SAFE engineering autonomy.

You MAY:

- create/edit/refactor Phase 10 code
- create/edit configuration
- create/edit docs
- create synthetic fixtures
- run targeted tests
- run the complete safe regression suite
- inspect stack traces
- debug ordinary failures
- fix ordinary bugs automatically
- rerun tests until clean
- run python -m pip check
- inspect git status/diff
- verify ignore rules
- self-review against Phase 10 Definition of Done

Do NOT stop for normal coding/test failures that can be safely fixed.

STOP only for:

- official competition-rule ambiguity
- need to inspect restricted competition rows externally
- Phase 09 not actually frozen/passed
- missing or ambiguous final model configuration
- leakage that cannot be corrected safely
- feature-schema conflict with Phase 06
- official template/schema conflict
- genuine environment incompatibility affecting deterministic model reload

DO NOT START PHASE 11.

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
11. approved PHASE_09_COMPETITION_CONTRACT.md
12. PHASE_10_COMPETITION_CONTRACT.md
13. existing Task 1 feature/validation/model-selection utilities

SOURCE PRIORITY:

Official organizer material
>
approved WayLoom master plan
>
approved phase contracts
>
implementation assumptions

==================================================
DATA BOUNDARY
==================================================

Do NOT inspect row-level official competition data inside the external-agent context.

Do NOT access:

data/raw/**
data/interim/**
reports/private/**

Use tracked source/config/docs and synthetic fixtures for agent-run implementation/testing.

The HUMAN will run real final training and inference locally.

==================================================
NO MODEL SEARCH IN PHASE 10
==================================================

Phase 09 has already selected and frozen:

- one service model configuration
- one lateness model configuration
- feature profile
- hyperparameters
- iteration rule
- calibration choice if applicable

Phase 10 MUST NOT:

- tune hyperparameters
- compare new model families
- reopen final holdout
- change features after observing test predictions
- search calibration methods
- add class weighting/resampling
- choose a different model because test predictions look unusual

Load exactly:

configs/task1_final_models.yaml

or the canonical approved equivalent path.

If it is not frozen or contains multiple final choices:
STOP.

==================================================
LEAKAGE / INFERENCE CONTRACT
==================================================

Never allow as direct inference features:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag

Task 1 test feature generation must reuse the canonical Phase 06 feature pipeline.

If historical target features are enabled:

fit historical state on historical training only

then transform the ENTIRE Task 1 test set without test labels.

Never update historical feature state using unknown test outcomes.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task1/final_train.py
src/task1/inference.py
src/task1/submission.py

scripts/train_task1_final_models.py
scripts/run_task1_inference.py
scripts/validate_task1_submission.py

configs/task1_inference.yaml

docs/task1_final_inference_spec.md

tests/test_task1_final_train.py
tests/test_task1_inference.py
tests/test_task1_submission.py

Use existing canonical paths/configs rather than duplicating approved components.

==================================================
CHECKPOINT A — DT-157 THROUGH DT-160
==================================================

DT-157:
Retrain final SERVICE model using exact Phase 09 frozen configuration.

Requirements:

- exact model family
- exact hyperparameters
- exact feature profile
- exact seed
- exact final iteration policy
- no tuning
- no test labels
- no forbidden X columns

DT-158:
Retrain final LATENESS model using exact frozen configuration.

Requirements:

- exact classifier family
- exact hyperparameters
- exact feature profile
- exact iteration rule
- exact class-weight/resampling policy
- exact calibration policy
- no threshold tuning

If calibration was not selected:
do not add calibration.

If calibration was selected:
fit it using only the frozen approved historical protocol.

DT-159:
Save final service model bundle.

Include:

model artifact
metadata.json
feature_schema.json
preprocessor/state if not embedded

DT-160:
Save final lateness model bundle.

Include:

model artifact
metadata.json
feature_schema.json
calibration artifact if required

SERIALIZATION TEST:

save
reload
predict synthetic data
assert equivalent predictions

For lateness:
verify positive class after reload.

Run targeted tests.
Fix ordinary failures automatically.

==================================================
CHECKPOINT B — DT-161
==================================================

Build one deterministic Task 1 saved-model inference pipeline.

Pipeline:

1. capture original test row order
2. validate Task 1 test identifiers/schema
3. join route_legs_test using official key
4. validate one-to-one relationship
5. generate canonical Phase 06 test features
6. validate feature schema/order
7. load SAVED service model
8. predict service
9. apply only frozen service postprocessing
10. load SAVED lateness model
11. predict positive-class probability
12. apply only frozen calibration
13. validate prediction values
14. restore original official row order
15. fill official template
16. validate
17. export

Normal inference MUST NOT train models.

If model artifact is missing:
FAIL.

Do not silently retrain.

==================================================
CHECKPOINT C — DT-162 THROUGH DT-164
==================================================

DT-162:
Load task1_test_inputs.csv.

Before transformation create internal:

__official_row_order

Validate:

delivery_id exists
nonblank
unique
route_id exists
seq_in_route exists

Do not sort original test input in place.

DT-163:
Join route_legs_test using EXACT official key:

task1_test_inputs:
route_id + seq_in_route

↔

route_legs_test:
route_id + seq

Use:

left join
one_to_one validation
merge indicator

Assert:

all rows matched
joined row count unchanged
delivery_id still unique
no join multiplication
outlet_id == to_outlet where available

Any unmatched test order:
STOP.

DT-164:
Generate IDENTICAL test features using canonical Phase 06 feature functions.

Do not write a separate ad hoc test feature system.

Assert:

training feature names == test feature names
training feature order == test feature order
semantic types compatible
feature registry status respected
forbidden fields absent

Load saved feature_schema.json and compare exactly.

Historical features must transform test without test y.

Road/traffic context only if frozen enabled and legitimate at prediction time.

Run critical synthetic join/feature parity tests.

==================================================
CHECKPOINT D — DT-165 THROUGH DT-168
==================================================

DT-165:
Generate pred_service_min from SAVED final service model.

Required:

one prediction per official test row
numeric
finite
stable across repeat inference

No rounding unless explicitly frozen.

DT-166:
Handle impossible negative service predictions using a PREDECLARED policy.

Preferred behavior:

if no negatives:
PASS

if frozen config explicitly says clip_to_zero:
apply max(pred, 0)
record count privately

if negatives occur and no policy was frozen:
FAIL

Never:

abs(pred)
replace by median ad hoc
invent a rule after seeing real test predictions

Record privately:

negative raw count
minimum raw prediction
policy
postprocessed count

DT-167:
Generate pred_late_prob.

Pipeline:

saved classifier
→ positive class probability for late_flag=1
→ frozen calibration if selected

Do NOT use hard class predict().

Verify class metadata.

DT-168:
Assert every probability:

finite
>= 0
<= 1

0 and 1 are valid.

Do not silently clamp genuinely invalid probability output.

==================================================
CHECKPOINT E — DT-169 THROUGH DT-171
==================================================

DT-169:
Restore exact original Task 1 row order using __official_row_order.

Do NOT final-sort by:

delivery_id
route_id
prediction
planned time

Prove:

final delivery_id sequence
==
original task1_test_inputs delivery_id sequence

DT-170:
Preserve every official delivery_id.

Assert:

same row count
no missing IDs
no new IDs
no duplicate IDs
no changed IDs
same ordered sequence

DT-171:
Fill the OFFICIAL submission_task1.csv template only.

Load official template locally at runtime.

Fill only required prediction columns:

pred_service_min
pred_late_prob

Preserve required identifier column(s).

No debug columns.

No internal row-order column.

No model metadata columns.

Final column names/order must exactly match official template.

==================================================
CHECKPOINT F — DT-172 THROUGH DT-173
==================================================

DT-172:
Export:

outputs/submission_task1.csv

Use index=False.

Prefer atomic writing:

write temp
read back
validate
rename to final

Do not leave a misleading final file if validation fails.

DT-173:
Perform hard final validation.

Verify:

file exists
readable
exact template columns
exact column order
row count correct
ordered delivery IDs exact
no duplicate IDs
no added/removed IDs
pred_service_min numeric
pred_service_min finite
service nonnegative policy passes
pred_late_prob numeric
pred_late_prob finite
0 <= probability <= 1
no NaN
no Inf
no accidental index column
no debug columns

Also prove final inference used RELOADED SAVED MODELS.

Run inference twice from saved artifacts and verify deterministic output.

==================================================
MODEL BUNDLE METADATA
==================================================

Each saved model bundle must record safely:

phase
task
model family
config ID
seed
feature schema/hash
feature registry version
library versions
training row count
training date range
git commit if available

Do not save row-level training data in metadata.

==================================================
REQUIRED TESTS
==================================================

Use synthetic fixtures only for agent-run tests.

Final training:

- frozen config honored
- multiple configs rejected
- forbidden feature rejected
- target not in X
- no tuning loop

Serialization:

- service save/reload equality
- late save/reload equality
- calibration save/reload when needed
- positive class preserved

Inference:

- no training in inference
- missing model fails
- official composite join
- unmatched test row fails
- duplicate route key fails
- destination mismatch fails
- feature schema exact
- feature order exact
- unseen category handling
- historical feature transform needs no test labels

Service:

- prediction length
- finite
- negative policy no-op path
- frozen clip path
- no-policy negative failure
- absolute-value hack rejected

Probability:

- positive class correct
- raw/calibrated path
- finite
- 0 valid
- 1 valid
- <0 invalid
- >1 invalid

Row/template:

- arbitrary official order restored
- every ID preserved
- exact template columns
- extra column fails
- accidental CSV index fails

End-to-end:

- load saved synthetic models in fresh inference path
- run twice
- identical final output

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After every checkpoint:

1. run targeted tests
2. inspect traceback
3. fix ordinary bug
4. rerun failing test
5. rerun Phase 10 targeted suite
6. continue only when clean

After DT-173 run complete safe regression suite.

Prefer:

pytest -q

If repo-wide pytest includes a documented test that requires private real data,
exclude only that specific test and report the exclusion.

Then:

python -m pip check

git status

git diff

Verify no restricted/private data was staged.

==================================================
LOCAL COMMANDS
==================================================

Implement but DO NOT execute against restricted official data in the external-agent context.

FINAL TRAINING:

python scripts/train_task1_final_models.py \
  --features data/interim/task1_features_train.csv \
  --labels data/interim/task1_training_labels.csv \
  --feature-registry configs/task1_features.yaml \
  --final-config configs/task1_final_models.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --report-dir reports/private/phase10_task1_final

INFERENCE:

python scripts/run_task1_inference.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --feature-registry configs/task1_features.yaml \
  --final-config configs/task1_final_models.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --output outputs/submission_task1.csv \
  --report-dir reports/private/phase10_task1_final

VALIDATION:

python scripts/validate_task1_submission.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --submission outputs/submission_task1.csv \
  --report-dir reports/private/phase10_task1_final

Prefer manifest-based official template resolution.

==================================================
STOP CONDITIONS
==================================================

STOP if:

- Phase 09 final config not frozen
- new tuning/search begins
- final holdout reopened for tuning
- actual journey field enters test X
- target-derived field enters test X
- training/test feature schema differs
- historical feature transform requires test labels
- test join not one-to-one
- destination mismatch exists
- model reload fails
- inference retrains silently
- service output NaN/Inf
- negative service violates frozen policy
- probability NaN/Inf
- probability outside [0,1]
- positive class ambiguous
- row order changes
- official ID sequence changes
- template mismatch
- final CSV contains extra columns
- final read-back fails
- repeat inference differs unexpectedly
- private data inspection becomes necessary
- tests cannot pass without violating approved contracts

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-157 READY
DT-158 READY
DT-159 READY
DT-160 READY
DT-161 READY
DT-162 READY
DT-163 READY
DT-164 READY
DT-165 READY
DT-166 READY
DT-167 READY
DT-168 READY
DT-169 READY
DT-170 READY
DT-171 READY
DT-172 READY
DT-173 READY

Phase 09 frozen configs reused exactly
no model search
service model save/reload passes
lateness model save/reload passes
calibrator reload passes if required
inference uses saved artifacts
Task 1 test join exact
feature parity exact
forbidden fields = 0
historical test features require no test labels
service predictions finite
negative service policy frozen
probabilities finite and bounded
original row order exact
delivery IDs exact
official template exact
submission export deterministic
full safe tests pass
pip check passes
private/restricted paths protected
no Phase 11 code added

==================================================
RETURN ONLY
==================================================

PHASE:
10 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-157 READY / FAIL
DT-158 READY / FAIL
DT-159 READY / FAIL
DT-160 READY / FAIL
DT-161 READY / FAIL
DT-162 READY / FAIL
DT-163 READY / FAIL
DT-164 READY / FAIL
DT-165 READY / FAIL
DT-166 READY / FAIL
DT-167 READY / FAIL
DT-168 READY / FAIL
DT-169 READY / FAIL
DT-170 READY / FAIL
DT-171 READY / FAIL
DT-172 READY / FAIL
DT-173 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

PHASE 09 CONFIG REUSE:
PASS / FAIL

MODEL SEARCH IN PHASE 10:
MUST BE NO

SERVICE MODEL RELOAD TEST:
PASS / FAIL

LATENESS MODEL RELOAD TEST:
PASS / FAIL

TASK 1 TEST JOIN:
PASS / FAIL

TRAIN/TEST FEATURE PARITY:
PASS / FAIL

FORBIDDEN INFERENCE FEATURES:
0 / nonzero

SERVICE OUTPUT VALIDATION:
PASS / FAIL

PROBABILITY OUTPUT VALIDATION:
PASS / FAIL

ROW ORDER GUARD:
PASS / FAIL

DELIVERY ID GUARD:
PASS / FAIL

OFFICIAL TEMPLATE GUARD:
PASS / FAIL

DETERMINISTIC REPEAT INFERENCE:
PASS / FAIL

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local final-training, inference and submission-validation commands.

PHASE 10 STATUS:
AWAITING LOCAL FINAL TRAINING + INFERENCE

TASK 1 FINAL OUTPUT READY:
NO

READY FOR NEXT PHASE:
NO

Then STOP.

Do not execute restricted-data inference.
Do not begin Phase 11.
```

---

# 37. Enhanced independent Phase 10 review prompt

Use a fresh agent chat after the human local run.

```text
Perform an independent review of completed WayLoom Datathon Phase 10.

DO NOT:

- open data/raw
- open data/interim
- open reports/private
- inspect Task 1 test predictions
- inspect private model-training results
- execute final training on real data
- execute real Task 1 inference
- modify code initially
- start Phase 11

READ:

1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. PHASE_10_COMPETITION_CONTRACT.md
3. configs/task1_final_models.yaml
4. configs/task1_inference.yaml
5. src/task1/final_train.py
6. src/task1/inference.py
7. src/task1/submission.py
8. scripts/train_task1_final_models.py
9. scripts/run_task1_inference.py
10. scripts/validate_task1_submission.py
11. docs/task1_final_inference_spec.md
12. tests/test_task1_final_train.py
13. tests/test_task1_inference.py
14. tests/test_task1_submission.py
15. relevant Phase 06 feature registry/pipeline
16. relevant Phase 09 frozen selection code/config
17. .gitignore
18. .cursorignore

HUMAN LOCAL CONTROL RESULT:

LOCAL PHASE 10 FINAL TRAINING: <PASS / FAIL>
SERVICE MODEL SAVED: <YES / NO>
LATENESS MODEL SAVED: <YES / NO>
SAVED-MODEL RELOAD: <PASS / FAIL>
TASK 1 TEST JOIN: <PASS / FAIL>
UNMATCHED TEST ORDERS: <0 / number>
FEATURE PARITY: <PASS / FAIL>
FORBIDDEN TEST FEATURES: <0 / number>
SERVICE PREDICTIONS FINITE: <YES / NO>
NEGATIVE SERVICE POLICY: <PASS / FAIL>
LATE PROBABILITY RANGE: <PASS / FAIL>
ROW ORDER: <PASS / FAIL>
DELIVERY ID INTEGRITY: <PASS / FAIL>
OFFICIAL TEMPLATE MATCH: <PASS / FAIL>
SUBMISSION EXPORT: <PASS / FAIL>
FINAL FILE VALIDATION: <PASS / FAIL>

Do not ask for private predictions or private reports.

AUDIT EVERY TASK:

DT-157:
exact frozen service config reused; no tuning.

DT-158:
exact frozen lateness config/calibration reused; no tuning.

DT-159:
service model bundle contains required model/state/schema metadata and reload is tested.

DT-160:
lateness bundle contains probability/calibration state and reload preserves class mapping.

DT-161:
inference works from saved artifacts and does not retrain.

DT-162:
original Task 1 test order captured before transformations; IDs validated.

DT-163:
exact official composite join:
route_id + seq_in_route
↔
route_id + seq
with one-to-one validation and destination consistency.

DT-164:
canonical Phase 06 features reused; exact train/test schema/order parity; test labels never required.

DT-165:
one finite service prediction per test row.

DT-166:
negative service policy is predeclared and no ad hoc absolute/median fix exists.

DT-167:
positive-class late probability generated from saved model and frozen calibration path.

DT-168:
all probabilities finite and within [0,1].

DT-169:
exact official row order restored.

DT-170:
every delivery_id preserved exactly once and sequence matches official test input.

DT-171:
o hand-built schema drift; official template only; no debug columns.

DT-172:
submission_task1.csv written without index and read-back validation exists.

DT-173:
full hard validation exists; saved-model reload and repeat-inference checks exist.

GLOBAL REVIEW:

- Phase 09 config is immutable in Phase 10
- no model search/tuning
- final holdout not reused for tuning
- no actual journey features in inference X
- no targets/target-derived features in inference X
- no test-label dependency
- historical target feature state frozen from history only
- model artifacts are reusable
- feature schema saved and checked
- private output is not committed
- no real predictions appear in tracked docs/tests

RUN SAFE TESTS ONLY:

pytest -q
python -m pip check
git status

If a documented test requires private official data, skip only that specific test and report it.

Do not execute real-data inference.

RETURN:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

PHASE 09 CONFIG FREEZE:
PASS / FAIL

NO-RETUNING CHECK:
PASS / FAIL

SAVED SERVICE MODEL:
PASS / FAIL

SAVED LATENESS MODEL:
PASS / FAIL

SAVED-MODEL INFERENCE:
PASS / FAIL

TEST JOIN INTEGRITY:
PASS / FAIL

FEATURE PARITY:
PASS / FAIL

LEAKAGE PROTECTION:
PASS / FAIL

SERVICE OUTPUT VALIDATION:
PASS / FAIL

PROBABILITY OUTPUT VALIDATION:
PASS / FAIL

ROW ORDER / ID INTEGRITY:
PASS / FAIL

OFFICIAL TEMPLATE INTEGRITY:
PASS / FAIL

DETERMINISTIC INFERENCE:
PASS / FAIL

SYNTHETIC TESTS:
PASS / FAIL

HUMAN LOCAL RUN:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

DT-157: PASS/FAIL
DT-158: PASS/FAIL
DT-159: PASS/FAIL
DT-160: PASS/FAIL
DT-161: PASS/FAIL
DT-162: PASS/FAIL
DT-163: PASS/FAIL
DT-164: PASS/FAIL
DT-165: PASS/FAIL
DT-166: PASS/FAIL
DT-167: PASS/FAIL
DT-168: PASS/FAIL
DT-169: PASS/FAIL
DT-170: PASS/FAIL
DT-171: PASS/FAIL
DT-172: PASS/FAIL
DT-173: PASS/FAIL

PHASE 10 REVIEW:
PASS / FAIL

TASK 1 FINAL OUTPUT READY:
YES / NO

READY FOR NEXT PHASE:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not start Phase 11.
```

---

# 38. Completion record template

```markdown
# Phase 10 Completion Record

## Task status

- [ ] DT-157
- [ ] DT-158
- [ ] DT-159
- [ ] DT-160
- [ ] DT-161
- [ ] DT-162
- [ ] DT-163
- [ ] DT-164
- [ ] DT-165
- [ ] DT-166
- [ ] DT-167
- [ ] DT-168
- [ ] DT-169
- [ ] DT-170
- [ ] DT-171
- [ ] DT-172
- [ ] DT-173

## Final training

- Phase 09 frozen service config reused: YES / NO
- Phase 09 frozen lateness config reused: YES / NO
- New tuning/search performed: NO / YES
- Service model saved: YES / NO
- Lateness model saved: YES / NO
- Calibrator saved if required: YES / NO / N/A
- Saved model reload: PASS / FAIL

## Inference

- Official test join: PASS / FAIL
- Unmatched test orders: 0 / number
- Duplicate matches: 0 / number
- Destination mismatches: 0 / number
- Train/test feature parity: PASS / FAIL
- Forbidden features: 0 / number
- Test labels required: NO / YES

## Predictions

- Service predictions finite: YES / NO
- Raw negative service predictions: count
- Negative policy: PASS / FAIL
- Late probabilities finite: YES / NO
- Late probabilities in [0,1]: YES / NO
- Positive-class mapping verified: YES / NO

## Submission integrity

- Official row order: PASS / FAIL
- delivery_id integrity: PASS / FAIL
- Official template: PASS / FAIL
- Exact columns/order: PASS / FAIL
- No extra columns: YES / NO
- Export read-back: PASS / FAIL
- Repeat inference: PASS / FAIL

## Final artifact

- `outputs/submission_task1.csv`: EXISTS / MISSING

## Review

- Independent Phase 10 review: PASS / FAIL

## Verdict

PHASE 10 STATUS: PASS / FAIL
TASK 1 FINAL OUTPUT READY: YES / NO
READY FOR NEXT PHASE: YES / NO
```

---

# 39. Final Phase 10 checklist

Before moving on:

```text
[ ] Phase 09 passed and final configs frozen
[ ] all DT-157–DT-173 implemented
[ ] no Phase 10 model search
[ ] final service model trained
[ ] final lateness model trained
[ ] both model bundles saved
[ ] saved models reload
[ ] calibration state reloads if required
[ ] inference uses saved artifacts only
[ ] official Task 1 test input loaded safely
[ ] exact route-leg test join used
[ ] unmatched test orders = 0
[ ] duplicate join matches = 0
[ ] outlet/destination mismatch = 0
[ ] canonical Phase 06 feature pipeline reused
[ ] train/test feature names match
[ ] train/test feature order matches
[ ] forbidden actual features = 0
[ ] target-derived inference features = 0
[ ] historical target features use historical state only
[ ] pred_service_min generated for every row
[ ] service outputs finite
[ ] negative service policy passes
[ ] pred_late_prob generated for every row
[ ] positive class verified
[ ] probabilities finite
[ ] probabilities in [0,1]
[ ] original row order restored
[ ] every delivery_id preserved exactly once
[ ] official submission template used
[ ] no extra columns
[ ] CSV written without index
[ ] CSV read-back passes
[ ] repeat saved-model inference passes
[ ] `outputs/submission_task1.csv` exists
[ ] safe tests pass
[ ] pip check passes
[ ] private/restricted paths protected
[ ] independent review passes
```

Only then:

```text
PHASE 10 STATUS: PASS
TASK 1 FINAL OUTPUT READY: YES
READY FOR NEXT PHASE: YES
```

Do not automatically start Phase 11.
