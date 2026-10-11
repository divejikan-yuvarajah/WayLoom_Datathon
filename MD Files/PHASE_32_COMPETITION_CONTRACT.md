# PHASE 32 — Model Artifact Management

> **Filename:** `PHASE_32_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 32 — Model artifact management  
> **Task range:** **DT-412 → DT-419**  
> **Task count:** **8**  
> **Phase dependency:** **Final selected models**  
> **Default phase priority:** **P0**  
> **Master phase gate:** All serialized model/preprocessing artifacts load successfully and reproduce intended predictions.  
> **Official deliverable link:** The Challenge Booklet requires final model file(s) to be saved alongside the final notebook.  
> **Critical cross-phase link:** Phase 31 DT-405 depends on Phase 32 DT-412–DT-419.  
> **Post-Phase32 action:** Return to Phase 31 final notebook closure before Phase 33.

---

# 1. Phase 32 purpose

Phase 32 formalizes the **final saved-model artifact layer** for WayLoom.

The official Challenge Booklet requires:

```text
Model file(s). Save your final model files alongside the notebook.
```

It also requires the final notebook to:

```text
Add a final cell that loads the saved models, demonstrates inference for
Task 1 and Task 2A, and clearly prints the inputs and predictions.
```

Therefore Phase 32 is not merely "save a pickle."

It must prove that the final Task 1 and Task 2A prediction systems are:

```text
persisted

self-describing

versioned

loadable

complete with required preprocessing/calibration state

safe to resolve by relative path

fresh-process compatible

prediction-equivalent to the frozen final predictions
```

The output of this phase becomes the artifact contract used by the Phase 31 final inference cell and later final packaging.

---

# 2. Finalized Phase 32 master inventory

The finalized master inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-412** | [O] | P0 | Final selected models | Save Task 1 service model |
| [ ] | **DT-413** | [O] | P0 | Final selected models | Save Task 1 lateness model |
| [ ] | **DT-414** | [O] | P0 | Final selected models | Save Task 2A model/artifacts if applicable |
| [ ] | **DT-415** | [E] | P0 | Final selected models | Save preprocessing objects if necessary |
| [ ] | **DT-416** | [E] | P0 | Final selected models | Record model versions |
| [ ] | **DT-417** | [O] | P0 | Final selected models | Test model serialization |
| [ ] | **DT-418** | [O] | P0 | Final selected models | Test model deserialization |
| [ ] | **DT-419** | [E] | P0 | Final selected models | Compare loaded-model predictions with original predictions |

**Expected Phase 32 tasks:** 8  
**Missing tasks allowed:** 0  
**Phase complete:** [ ]  
**READY FOR PHASE 33:** **NO until Phase 31 final closure passes**

---

# 3. Official source requirements

The official booklet states:

```text
Model file(s). Save your final model files alongside the notebook.
```

and:

```text
Final notebook (TeamName_FinalNotebook.ipynb).
Retain the cells used for label construction, preprocessing, training,
and evaluation.

Add a final cell that loads the saved models, demonstrates inference for
Task 1 and Task 2A, and clearly prints the inputs and predictions.
```

Phase 32 exists to make that final-cell requirement real.

The notebook must be able to load the final models from saved artifacts rather than reuse hidden in-memory objects from earlier notebook cells.

---

# 4. Official restrictions Phase 32 must respect

The booklet also states:

```text
Model Restrictions:
No pretrained models except the stated exceptions.

API Usage:
Proprietary API-based modelling/preprocessing is prohibited.

Low-code / no-code fully automated end-to-end modelling:
prohibited.

Competition data:
competition-only.

Data sharing:
no third-party sharing/distribution.

Publication:
datasets and derivatives must not be made publicly available unless authorized.

Confidentiality:
must be maintained.
```

Phase 32 therefore uses local artifact files and local loaders.

Do not introduce external model registries, hosted inference APIs or third-party artifact upload services.

---

# 5. Critical Phase 31 ↔ Phase 32 dependency

The finalized Phase 31 inventory explicitly defines:

```text
DT-405 — Load saved models in final cell
Dependency: DT-412–DT-419
```

Therefore the correct flow is:

```text
Phase31 core notebook
        ↓
DT-405 = BLOCKED_BY_PHASE32
        ↓
Phase32 artifact management
        ↓
DT-412–DT-419 PASS
        ↓
Return to Phase31
        ↓
final cell loads artifacts
clean-kernel Run All
fresh-kernel final-cell-only run
        ↓
Phase31 FINAL PASS
        ↓
Phase33
```

Do not skip the return to Phase 31.

---

# 6. Phase 10 / Phase 17 ownership boundary

## Task 1

Phase 10 already required final Task 1 model serialization.

Its canonical artifact pattern includes the equivalent of:

```text
models/task1_service/model.*
models/task1_service/metadata.json
models/task1_service/feature_schema.json

models/task1_late/model.*
models/task1_late/metadata.json
models/task1_late/feature_schema.json
models/task1_late/calibration.*     # only if required
```

Therefore Phase 32 should **register, validate and prove reloadability** of the frozen Task 1 artifacts.

It should not overwrite them.

## Task 2A

Phase 17 explicitly states that:

```text
Phase 32 formally owns final model/artifact management.
```

Phase 17 may have final runtime state/inference logic, but Phase 32 is responsible for the durable Task 2A artifact bundle.

---

# 7. Preconditions

Before Phase 32 can pass:

```text
Task1 final service model selection:
FROZEN

Task1 final late model selection:
FROZEN

Task1 official output:
FINAL

Task2A final strategy/model selection:
FROZEN

Task2A official output:
FINAL

Task2B output:
FINAL / unchanged
```

Require:

```text
configs/task1_final_models.yaml

configs/task2a_final_models.yaml

Task1 final feature schema/registry

Task2A final feature/inference schema

canonical Task1 inference code

canonical Task2A inference code
```

If actual final model family/strategy cannot be determined:

```text
STOP
```

---

# 8. Frozen artifact safety

Do not modify:

```text
outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv
```

Do not change final champion selections.

Do not retune.

Do not redo model selection.

Do not modify Task 2B frozen allocation/policy.

For Task 1:

if Phase 10 canonical model artifact hashes are already frozen/recorded, they must remain unchanged.

---

# 9. Recommended Phase 32 outputs

Create/update according to repository conventions:

```text
configs/model_artifacts.yaml

models/
├── artifact_registry.json
├── README.md
├── task1_service/
│   └── existing Phase10 canonical artifacts
├── task1_late/
│   └── existing Phase10 canonical artifacts
└── task2a/
    ├── artifact_manifest.json
    └── final required model/state components
```

Recommended supporting code:

```text
src/common/artifact_io.py
src/common/artifact_registry.py
src/common/versioning.py

scripts/finalize_model_artifacts.py
scripts/validate_model_artifacts.py
scripts/run_model_artifact_parity.py

docs/model_artifacts.md
```

Recommended tests:

```text
tests/test_artifact_registry.py
tests/test_task1_artifact_roundtrip.py
tests/test_task2a_artifact_roundtrip.py
tests/test_preprocessing_artifacts.py
tests/test_artifact_clean_process_load.py
tests/test_artifact_prediction_parity.py
tests/test_artifact_security.py
tests/test_phase31_artifact_bridge.py
```

Reuse existing canonical loaders where possible.

---

# 10. Final package path principle

Phase 40 will build the final submission package.

Phase 32 should make the artifact tree compatible with a package such as:

```text
TeamName_FinalNotebook.ipynb
models/
  artifact_registry.json
  README.md
  task1_service/
  task1_late/
  task2a/
```

The official phrase "alongside the notebook" should be satisfied through a self-contained submission folder.

Do not require workstation-specific model paths.

---

# 11. Artifact registry

Create:

```text
models/artifact_registry.json
```

This is the canonical index the final notebook/loaders can use.

Recommended top-level structure:

```json
{
  "artifact_schema_version": 1,
  "phase": 32,
  "task1_service": {},
  "task1_late": {},
  "task2a": {},
  "shared_preprocessing": {},
  "runtime_versions": {}
}
```

---

# 12. Artifact-entry fields

Each final component should record safe metadata such as:

```text
artifact_id

task

target

artifact_kind

model_family

strategy

config_id

serializer

format

relative_path

sha256

size_bytes

feature_schema_ref

preprocessor_mode

postprocessing_ref

required

runtime/library versions

load entrypoint

inference entrypoint
```

For Task 1 lateness also record:

```text
positive class mapping

class ordering where relevant

calibration mode

calibration artifact path when required
```

No private rows.

No absolute user paths.

---

# 13. Artifact schema version

Use a registry/artifact schema version such as:

```text
1
```

This version describes WayLoom's artifact-manifest format.

It is separate from:

```text
model library version

model binary format version

config version
```

Unknown future artifact schema versions must fail closed.

---

# 14. SHA256 integrity

For every required model/preprocessing artifact:

```text
compute SHA256

store expected SHA256 in registry

verify before deserialization
```

Correct loader order:

```text
resolve path
        ↓
verify path allowed
        ↓
verify file exists
        ↓
verify SHA256
        ↓
deserialize
```

Not:

```text
deserialize first
→ checksum later
```

---

# 15. Path safety

Registry paths should be:

```text
relative
```

to the project/package model root.

Reject:

```text
C:\Users\...

/home/<user>/...

../outside/models

HTTP URL

S3 URL

arbitrary network location
```

The final notebook should be movable with the submission folder.

---

# 16. Secure deserialization

Python pickle/joblib formats can execute code.

This phase is not a production security system, but it should avoid obvious unsafe patterns.

Rules:

```text
load only trusted registered artifacts

verify hash before loading

reject arbitrary caller-supplied paths

prefer native model formats where practical

do not support network model URLs

do not expose a generic load_any_pickle utility
```

---

# 17. Serializer choice

Use the selected model's appropriate serializer.

Examples are engineering guidance only:

```text
CatBoost:
native .cbm

LightGBM:
native booster/model format

XGBoost:
JSON/UBJ/native format

scikit-learn pipeline:
joblib where required

custom baseline:
versioned JSON/typed state

ensemble:
component files + manifest
```

Do not change the model family because another serializer is easier.

---

# 18. Native format preference

When the final library provides a stable native format:

prefer it.

Reasons:

```text
clearer compatibility

less arbitrary Python object execution

better portability

more explicit model-family ownership
```

If the final pipeline is a scikit-learn composite object and joblib is the correct native project convention, use it safely.

---

# 19. DT-412 — Save Task 1 service model

Task 1 service was already saved/frozen in Phase 10.

Phase 32 should satisfy DT-412 through **canonical artifact registration and validation**.

Do not blindly save a new copy over the canonical model.

---

# 20. DT-412 procedure

1. Resolve final service configuration from:

```text
configs/task1_final_models.yaml
```

2. Resolve canonical Phase 10 service artifact directory.

3. Verify:

```text
model file

metadata

feature schema

required preprocessing state
```

4. Check model family/config ID.

5. Check feature schema.

6. Check Phase 10 freeze/integrity evidence where available.

7. Compute/register SHA256.

8. Load via canonical loader.

9. Run synthetic prediction smoke.

10. Add to global artifact registry.

---

# 21. Task 1 service preprocessor modes

Valid examples:

```text
embedded

external_serialized

deterministic_code

not_required
```

Do not create a new preprocessor file merely because DT-415 exists.

DT-415 says:

```text
if necessary
```

---

# 22. Task 1 service metadata

At minimum registry/metadata should resolve:

```text
task = task1_service

model family

final config ID

serializer

artifact path

feature schema

feature order

categorical handling if relevant

service postprocessing

runtime version(s)

SHA256
```

---

# 23. Task 1 service artifact immutability

If canonical service artifact existed before Phase 32:

record pre-hash.

After Phase 32:

require the same hash.

If changed:

```text
FAIL
```

Prediction equivalence does not excuse an unauthorized change to a frozen artifact.

---

# 24. Task 1 service STOP conditions

Stop if:

```text
artifact missing

metadata missing

feature schema missing

model family differs from final config

feature schema differs from final inference

checksum differs from known freeze

loader requires retraining

synthetic load/predict fails
```

---

# 25. DT-413 — Save Task 1 lateness model

Task 1 lateness was also already saved/frozen in Phase 10.

Phase 32 registers and validates:

```text
classifier

feature schema

calibration state if used

positive class mapping

probability semantics
```

---

# 26. Lateness artifact structure

Expected equivalent:

```text
models/task1_late/model.*
models/task1_late/metadata.json
models/task1_late/feature_schema.json
models/task1_late/calibration.*
```

Calibration file only when frozen configuration uses one.

---

# 27. Positive class mapping

The final prediction is:

```text
pred_late_prob
```

which must refer to the probability of:

```text
late_flag = 1
```

After deserialization:

class order/positive-class index must be identical.

Do not assume column index 1 without validating model/class metadata.

---

# 28. Lateness calibration

If the final late pipeline is calibrated:

save/register the exact calibration object/state.

If the final pipeline is uncalibrated:

record:

```text
calibration_mode = none
```

Do not create a fake calibrator.

---

# 29. Lateness parity invariants

After load:

```text
pred_late_prob finite

0 <= pred_late_prob <= 1

positive-class mapping preserved

calibration preserved

feature schema preserved
```

Any material change:

FAIL.

---

# 30. DT-414 — Save Task 2A model/artifacts if applicable

Task 2A is the main new artifact-finalization responsibility of Phase 32.

First read the actual frozen final strategy from:

```text
configs/task2a_final_models.yaml
```

and final inference/runtime metadata.

Do not assume one model.

---

# 31. Task 2A supported artifact shapes

The artifact system should honestly represent the actual final design.

Possible actual kinds:

```text
trained_model

baseline_strategy

ensemble

multi_model_bundle

derived_target_strategy
```

Use only the type(s) needed by the final frozen pipeline.

---

# 32. Task 2A trained model case

If the final strategy contains trained model components:

save every required component.

Possible examples:

```text
total-volume model

Fresh chilled model

horizon-specific models

brand-specific components
```

Only the actual selected components.

Do not serialize obsolete challengers.

---

# 33. Task 2A direct/multi-horizon case

If final strategy uses multiple direct horizons:

manifest must map:

```text
target
forecast horizon
artifact component
```

unambiguously.

Use stable IDs, for example:

```text
total_h01
...
total_h10
```

only if this reflects actual architecture.

Do not infer component by filesystem ordering.

---

# 34. Task 2A ensemble case

If final strategy is an ensemble:

save/register:

```text
all component artifacts

component IDs

weights

target mapping

horizon mapping where applicable

combination rule

postprocessing
```

Do not drop a component after serialization.

Do not retune weights.

---

# 35. Task 2A baseline champion case

Phase 17 allows a baseline to be champion.

If the frozen final champion is a deterministic baseline:

do not create a fake trained model file.

Save a versioned baseline artifact such as:

```text
models/task2a/baseline_strategy.json
```

containing the fixed final parameters/state needed for inference.

Registry:

```text
artifact_kind = baseline_strategy
```

The final notebook still "loads" the saved final predictor artifact.

---

# 36. Task 2A derived chilled strategy

If chilled output is derived rather than independently modelled:

document/register the derivation strategy.

Do not invent a separate chilled model.

Phase 32 must match the exact Phase 17 final inference architecture.

---

# 37. Task 2A private history boundary

Do not add raw demand history to the saved model package merely for convenience.

If inference needs the historical panel:

the inference code may load/rebuild it locally from authorized competition data.

The model bundle should contain:

```text
learned model state

fixed strategy/config

required preprocessing state

feature schema

postprocessing logic references
```

not a copy of the competition dataset.

---

# 38. Task 2A artifact manifest

Create:

```text
models/task2a/artifact_manifest.json
```

Recommended fields:

```text
artifact_schema_version

task = task2a

final_strategy

forecast_horizon_weeks = 10

targets

components

component roles

feature schema refs

preprocessing refs/modes

postprocessing

runtime versions

component SHA256 values
```

No real row IDs.

---

# 39. Task 2A atomic finalization

Do not write an unvalidated model directly into the final directory.

Recommended:

```text
temporary candidate directory
        ↓
save candidate
        ↓
load candidate
        ↓
synthetic prediction parity
        ↓
manifest/checksum validation
        ↓
atomic promotion to models/task2a/
```

Failure before promotion:

leave canonical path untouched.

---

# 40. Task 2A overwrite protection

Default:

```text
overwrite_existing = false
```

If a valid final Task 2A artifact bundle already exists:

register/validate it.

Do not replace it merely because the script ran twice.

A controlled re-finalization should require an explicit flag/reason and unchanged frozen final config.

---

# 41. DT-415 — Save preprocessing objects if necessary

This task is conditional.

The correct answer may be:

```text
saved external object
```

or:

```text
not required
```

depending on the final pipeline.

---

# 42. Preprocessor mode taxonomy

For each final component record one of:

```text
embedded
external_serialized
deterministic_code
not_required
```

---

# 43. External learned preprocessing

If inference depends on learned preprocessing state not contained in the model:

save it.

Examples:

```text
encoder

imputer

scaler

learned feature selector

learned categorical mapping
```

Then register:

```text
path

serializer

hash

version

feature relation
```

---

# 44. Embedded preprocessing

If the final model artifact contains preprocessing internally:

record:

```text
preprocessor_mode = embedded
```

No duplicate external object.

Fresh-process prediction must prove it works.

---

# 45. Deterministic code preprocessing

If feature generation is pure canonical code plus frozen configuration:

record:

```text
preprocessor_mode = deterministic_code
```

Preserve:

```text
feature schema

feature registry/version

config reference
```

No fake serialized transformer is needed.

---

# 46. Not-required case

Use:

```text
preprocessor_mode = not_required
```

only when inference truly needs no external preprocessing state beyond direct model input.

The validator should reject `not_required` when a loader expects an external state object.

---

# 47. Feature schema as artifact state

Regardless of preprocessing mode, every final model should have a reproducible feature contract.

Preserve/reference:

```text
feature names

feature order

expected types

categorical features where relevant

registry/schema version
```

A loaded model with the wrong feature order is not valid.

---

# 48. Do not serialize dataframes as "preprocessing"

Do not package:

```text
training DataFrame

test DataFrame

validation predictions

EDA output

raw reference tables
```

as preprocessing objects unless an object is genuinely part of fitted model state.

This phase is not a data archive.

---

# 49. DT-416 — Record model versions

The official booklet does not prescribe a version-manifest format.

This is a WayLoom engineering control for reproducibility.

Record only relevant runtime packages.

---

# 50. Required runtime versions

At minimum:

```text
Python

numpy

pandas

actual final model library/libraries

scikit-learn if used

joblib if used

other serializer library if used
```

Task2A may use a different library from Task1.

Record both.

---

# 51. Version capture implementation

Prefer:

```python
importlib.metadata.version(...)
```

and:

```python
sys.version_info
```

Do not store:

```text
username

home path

machine serial

environment secrets
```

---

# 52. Artifact format metadata

Also record:

```text
artifact schema version

serializer

model binary format

config ID/version

feature schema version

git commit if available
```

The artifact registry itself should be versioned.

---

# 53. Runtime compatibility policy

Recommended:

```text
exact version:
PASS

minor/patch difference:
WARN or PASS according to library policy + load/parity evidence

major model/serializer-library difference:
BLOCK by default
```

The clean-load and prediction-parity tests are authoritative.

Do not silently migrate/resave an artifact because the environment changed.

---

# 54. Model version README

Create:

```text
models/README.md
```

Include:

```text
artifact structure

how registry works

how hashes are checked

runtime versions

how Task1 is loaded

how Task2A is loaded

preprocessing mode definitions

Phase31 final-cell relationship

security note about trusted local artifacts
```

No private data.

---

# 55. DT-417 — Test model serialization

Serialization is the save half of the round-trip.

The test must demonstrate that the canonical saver writes complete model state.

---

# 56. Task 1 serialization test

Because the canonical Task 1 artifacts are already frozen:

do not overwrite them.

Allowed evidence:

```text
Phase10 save/reload evidence

plus current load validation

plus temporary reserialization/reload when safe
```

If temporary reserialization is supported:

```text
load canonical artifact
predict synthetic X
save temp artifact
reload temp
predict synthetic X
compare
```

Delete temp output after test.

---

# 57. Task 2A serialization test

For newly finalized Task 2A artifact:

```text
original final predictor/state
        ↓
predict deterministic fixture
        ↓
save candidate to temp
        ↓
reload candidate
        ↓
predict same fixture
        ↓
compare
        ↓
promote only if PASS
```

This is required before canonical promotion.

---

# 58. Serialization fixture rules

Synthetic fixtures should exercise the final contract.

Possible dimensions:

```text
multiple feature columns

categoricals if used

missing values if supported

more than one horizon if final strategy uses horizon

total/chilled paths
```

No private rows.

---

# 59. Serialization completeness

Saving only the core estimator is insufficient if inference also requires:

```text
calibrator

encoder

feature schema

ensemble weights

target/horizon mapping

postprocessing configuration
```

The bundle must be complete.

---

# 60. DT-418 — Test model deserialization

A deserialization test must run in a fresh Python process.

This is stronger than loading immediately after saving in the same interpreter.

---

# 61. Fresh-process load sequence

The clean process should:

```text
load config

load registry

validate registry schema

resolve safe paths

verify hashes

validate versions

load Task1 service

load Task1 late/calibration

load Task2A bundle

load external preprocessors if required

validate feature schemas

run small synthetic smoke predictions
```

It must not train.

---

# 62. Clean-process command

Recommended abstraction:

```bash
python scripts/validate_model_artifacts.py   --config configs/model_artifacts.yaml   --registry models/artifact_registry.json   --mode load-only
```

This command should succeed without previous notebook state.

---

# 63. Deserialization negative tests

Require failures for:

```text
missing artifact

corrupt artifact

SHA256 mismatch

unsupported artifact schema version

unknown serializer

path outside models/

missing calibration

wrong positive class

feature-schema mismatch

missing Task2A component

ensemble weight/component inconsistency
```

---

# 64. No import-time training

Importing artifact loader modules must not:

```text
load raw training data

fit a model

run validation

rewrite an artifact
```

Load should occur only when explicitly requested.

---

# 65. DT-419 — Compare loaded-model predictions with original predictions

This is the final correctness proof for the artifacts.

Use:

```text
Level A:
synthetic round-trip

Level B:
human-local frozen-output parity
```

Both required.

---

# 66. Level A — synthetic parity

Safe for the agent.

Compare:

```text
canonical/original predictor

vs

deserialized predictor
```

on deterministic synthetic fixtures.

Require tight numerical parity.

---

# 67. Level B — Task 1 private parity

Human-local only.

Reload saved artifacts from the Phase 32 registry.

Run canonical Task1 inference against the official private test inputs.

Compare to frozen:

```text
outputs/submission_task1.csv
```

Do not overwrite it.

---

# 68. Task 1 parity checks

Require:

```text
same delivery_id set

same row count

same row order

pred_service_min parity

pred_late_prob parity

same service postprocessing

same late calibration/positive class
```

ID/order mismatch is always a failure.

---

# 69. Level B — Task 2A private parity

Human-local only.

Reload the final Task2A artifact bundle.

Run the frozen canonical Task2A inference pipeline.

Compare to:

```text
outputs/submission_task2a.csv
```

Do not overwrite it.

---

# 70. Task 2A parity checks

Require:

```text
same row_id set

same row count

same row order

pred_total_volume_m3 parity

pred_chilled_volume_m3 parity

Style/Tech chilled = 0

chilled <= total

same final postprocessing
```

---

# 71. Frozen official output as parity oracle

The final official predictions are already frozen.

They are therefore an excellent end-to-end reference for Phase 32.

Phase 32 must reproduce them from the loaded artifacts.

It must not regenerate/replace them.

---

# 72. Parity tolerance

Make tolerance explicit in config.

Recommended starting values for same-environment comparisons:

```yaml
raw_atol: 1.0e-12
raw_rtol: 1.0e-10
final_atol: 1.0e-10
final_rtol: 1.0e-10
```

Exact comparison is preferable where feasible.

Do not loosen tolerance merely to pass.

---

# 73. Final-format parity

If the canonical submission writer:

```text
clips

calibrates

enforces chilled<=total

sets Style/Tech chilled=0

rounds/formats
```

parity must be checked after the same frozen logic.

A raw model match is not enough if final output logic differs.

---

# 74. Row identity/order

For official-output parity:

```text
sorting both files before comparison
```

is not acceptable as the primary test.

The loaded inference pipeline itself should preserve canonical official order.

---

# 75. Private parity report

Create:

```text
reports/private/phase32_model_artifacts/parity_report.json
```

Safe aggregate fields:

```text
task1_service_status

task1_late_status

task2a_total_status

task2a_chilled_status

id_set_status

row_order_status

max_abs_diff

max_rel_diff

tolerances

registry hash

runtime compatibility
```

No real row IDs.

---

# 76. Phase 32 private evidence directory

Recommended:

```text
reports/private/phase32_model_artifacts/
├── run_manifest.json
├── artifact_integrity.json
├── serialization_report.json
├── deserialization_report.json
├── parity_report.json
└── phase32_gate.json
```

These should remain ignored/untracked.

---

# 77. Phase 32 gate file

Private:

```text
phase32_gate.json
```

Recommended:

```json
{
  "phase": 32,
  "status": "PASS",
  "dt412": "PASS",
  "dt413": "PASS",
  "dt414": "PASS",
  "dt415": "PASS",
  "dt416": "PASS",
  "dt417": "PASS",
  "dt418": "PASS",
  "dt419": "PASS",
  "task1_artifacts_unchanged": true,
  "official_outputs_unchanged": true,
  "fresh_process_load": "PASS",
  "task1_parity": "PASS",
  "task2a_parity": "PASS"
}
```

No private IDs.

---

# 78. Artifact registry integrity report

Create private summary containing:

```text
registered artifact count

required artifact count

missing = 0

hash mismatch = 0

path violations = 0

schema mismatch = 0

version blockers = 0
```

Avoid row-level information.

---

# 79. Config

Create:

```text
configs/model_artifacts.yaml
```

Recommended structure:

```yaml
version: 1

model_root: models
registry: models/artifact_registry.json

task1:
  service:
    mode: register_existing
    final_config: configs/task1_final_models.yaml

  late:
    mode: register_existing
    final_config: configs/task1_final_models.yaml

task2a:
  mode: finalize_or_register
  final_config: configs/task2a_final_models.yaml

integrity:
  verify_sha256_before_load: true
  allow_absolute_paths: false
  allow_paths_outside_model_root: false
  overwrite_existing: false

versions:
  record_python: true
  record_runtime_packages: true

parity:
  raw_atol: 1.0e-12
  raw_rtol: 1.0e-10
  final_atol: 1.0e-10
  final_rtol: 1.0e-10
  require_id_order_exact: true

security:
  allow_network_artifacts: false
  allow_unregistered_pickle: false
```

Adapt only to actual repository conventions.

---

# 80. Finalization script

Create:

```text
scripts/finalize_model_artifacts.py
```

Required responsibilities:

```text
resolve final configs

verify/register Task1 frozen artifacts

discover Task2A final strategy

serialize Task2A candidate if needed

save required preprocessing state

capture runtime versions

compute hashes

validate candidate bundle

atomically publish Task2A

write/update registry

write private run report
```

No tuning.

No Task1 training.

---

# 81. Safe validation script

Create:

```text
scripts/validate_model_artifacts.py
```

Recommended modes:

```text
integrity

load-only

synthetic-roundtrip

all-safe
```

It should not require private data for these modes.

---

# 82. Private parity script

Create:

```text
scripts/run_model_artifact_parity.py
```

This is the only Phase 32 script expected to require private real input data.

It should:

```text
reload artifacts from registry

run canonical Task1 inference

compare to frozen Task1 output

run canonical Task2A inference

compare to frozen Task2A output

write private aggregate report

print aggregate PASS/FAIL only
```

No official CSV writing.

---

# 83. Task 1 hash guard

Before human-local Phase 32 finalization:

hash all canonical Task1 artifact files.

After:

require identical hashes.

Task1 Phase10 artifacts should not change.

---

# 84. Official CSV hash guard

Before/after:

```text
outputs/submission_task1.csv

outputs/submission_task2a.csv

outputs/submission_task2b.csv
```

must remain byte-identical.

If any changes:

```text
PHASE32 FAIL
```

---

# 85. Task 2B isolation

Phase 32 does not manage Task2B model artifacts because Task2B is an optimizer and its frozen optimization/config artifacts were already managed in earlier phases.

Do not modify:

```text
Task2B allocation

Task2B policy

Task2B submission
```

Phase 32 model-file requirements focus on Task1 and Task2A.

---

# 86. Models README

Create:

```text
models/README.md
```

Recommended sections:

```text
Official requirement

Artifact layout

Registry

Task1 service

Task1 lateness/calibration

Task2A strategy

Preprocessing state

Version metadata

Checksum verification

Fresh-process loading

Phase31 final notebook usage

Security/trusted-local-artifact note
```

---

# 87. Phase 31 loader bridge

Phase 31 should be able to import canonical loaders rather than know serializer internals.

Recommended interfaces:

```python
load_task1_service_bundle(...)
load_task1_late_bundle(...)
load_task2a_bundle(...)
```

or existing repository equivalents.

Prediction interfaces:

```python
predict_task1_from_saved_artifacts(...)
predict_task2a_from_saved_artifacts(...)
```

The final notebook cell should use these.

---

# 88. Loader abstraction requirement

The notebook should not contain:

```text
if catboost then...
if lightgbm then...
if baseline then...
```

artifact-format branching.

Phase 32 should centralize that in canonical loader code.

The final cell should operate at the task/bundle level.

---

# 89. Phase 31 fresh-kernel compatibility

A fresh Python kernel should be able to:

```text
import canonical loader

load artifact registry

load all required models/state

run inference
```

without:

```text
training cells

model-selection objects

earlier notebook variables
```

Phase 32 must make that possible.

---

# 90. Test suite — artifact registry

Create:

```text
tests/test_artifact_registry.py
```

Cover:

```text
supported registry version

all required tasks represented

relative paths only

path containment

files exist

hash verification

config ID parity

model-family parity

artifact kind validation

preprocessor mode validation

runtime versions

no private path
```

---

# 91. Test suite — Task 1 roundtrip

Create:

```text
tests/test_task1_artifact_roundtrip.py
```

Synthetic checks:

```text
service load

service prediction

temporary service reserialization when supported

late load

late probability

calibration load if applicable

positive class

class order

feature schema

canonical artifact bytes unchanged
```

---

# 92. Test suite — Task 2A roundtrip

Create:

```text
tests/test_task2a_artifact_roundtrip.py
```

Must cover the actual selected strategy.

Require:

```text
save

reload

predict

component completeness

target/horizon mapping

weights where applicable

postprocessing metadata

feature schema
```

Do not overbuild unused architecture branches.

---

# 93. Test suite — preprocessing state

Create:

```text
tests/test_preprocessing_artifacts.py
```

Cover:

```text
external preprocessor required -> file required

embedded -> external duplicate not required

deterministic_code -> no binary object needed

not_required -> only if valid

feature schema always present/referenced

missing required state -> fail
```

---

# 94. Test suite — clean process

Create:

```text
tests/test_artifact_clean_process_load.py
```

Launch a subprocess.

Require:

```text
registry load

hash validation

Task1 service load

Task1 late/calibrator load

Task2A load

synthetic smoke predictions

zero training calls
```

---

# 95. Test suite — parity

Create:

```text
tests/test_artifact_prediction_parity.py
```

Synthetic:

```text
tight numeric equality

probability equality

postprocessing equality

ID/key equality

row-order mismatch failure

missing-row failure

beyond-tolerance failure
```

Human-private real parity remains separate.

---

# 96. Test suite — artifact security

Create:

```text
tests/test_artifact_security.py
```

Cover:

```text
absolute path rejected

path traversal rejected

outside-model-root rejected

network URL rejected

checksum mismatch fails before deserialize

unknown serializer rejected

unregistered pickle/joblib rejected

corrupt file handled safely
```

---

# 97. Test suite — Phase 31 bridge

Create:

```text
tests/test_phase31_artifact_bridge.py
```

Require:

```text
Task1 service bundle resolvable

Task1 late bundle resolvable

Task2A bundle resolvable

canonical loader importable

fresh-process import/load

no training required

package-relative paths

final-cell loader functions available
```

---

# 98. Edge case — Task 1 artifacts already exist

This is the expected state.

Correct Phase32 behavior:

```text
verify
register
test
do not overwrite
```

This satisfies DT-412/DT-413 in the finalized workflow.

---

# 99. Edge case — Task 1 artifact missing

Do not silently retrain.

Return:

```text
UPSTREAM TASK1 ARTIFACT BLOCKER
```

The relevant Task1 finalization phase must be reopened intentionally.

---

# 100. Edge case — Task 1 calibrator absent

If final config says no calibrator:

```text
calibration_mode = none
```

PASS.

Do not create one.

---

# 101. Edge case — Task 1 calibrator required but missing

FAIL.

Do not use raw probability as a fallback.

That changes final predictions.

---

# 102. Edge case — preprocessing object not required

DT-415 can still PASS.

Record:

```text
NOT_REQUIRED
```

with explicit reason.

The master task intentionally says:

```text
if necessary
```

---

# 103. Edge case — baseline Task2A champion

Save fixed strategy parameters/state.

Do not fabricate a trained estimator.

The loader should return a predictor object using the saved baseline artifact.

---

# 104. Edge case — Task2A ensemble

Every component/weight required.

No partial ensemble.

No silent fallback.

---

# 105. Edge case — Task2A multiple horizons

Use explicit component mapping.

Do not depend on:

```text
directory listing order
```

or:

```text
row position
```

---

# 106. Edge case — derived chilled target

If Task2A chilled forecast is derived by final logic:

store the strategy/postprocessing reference.

Do not create a fake `chilled_model.bin`.

---

# 107. Edge case — library version drift

If current runtime differs from recorded artifact version:

report it.

If load + parity succeeds under allowed compatibility policy:

may WARN.

If major incompatibility or parity failure:

BLOCK.

Do not auto-migrate model bytes.

---

# 108. Edge case — artifact checksum changed

Do not update the manifest hash to make it pass.

Investigate the artifact mutation.

Hash mismatch is an integrity failure.

---

# 109. Edge case — feature schema changed

Do not reorder or drop features opportunistically.

The final saved model must use the frozen inference schema.

Mismatch:

FAIL.

---

# 110. Edge case — row-order-only parity failure

Still FAIL.

Official output preservation includes row order.

Fix inference/template handling.

Do not sort the frozen reference.

---

# 111. Edge case — very small floating difference

Check:

```text
library version

serializer

postprocessing

dtype

feature order
```

Use the predefined tolerance.

Do not increase tolerance before root-cause analysis.

---

# 112. Edge case — artifact bytes differ after temporary resave

This may be acceptable for a TEMPORARY serialization test if the serializer embeds timestamps or nonsemantic metadata.

Required:

prediction parity.

However canonical frozen artifact hashes remain immutable.

---

# 113. Edge case — raw rows embedded in custom bundle

If a custom artifact includes raw training rows unnecessarily:

remove them.

Do not package a training dataframe as model state.

This is both confidentiality and artifact-size hygiene.

---

# 114. Edge case — absolute artifact path

Final registry must use relative paths.

The final notebook should work after moving the whole submission directory.

No:

```text
C:\Users\ASUS\Desktop\...
```

---

# 115. Edge case — Phase 31 core pending

Phase 32 can complete.

But after PASS:

```text
AUTHORIZED NEXT ACTION:
RETURN TO PHASE31 FINAL CLOSURE
```

Do not jump to Phase33.

---

# 116. Local human finalization command

Recommended shape:

```bash
python scripts/finalize_model_artifacts.py   --config configs/model_artifacts.yaml   --task1-config configs/task1_final_models.yaml   --task2a-config configs/task2a_final_models.yaml   --registry models/artifact_registry.json   --report-dir reports/private/phase32_model_artifacts
```

If Task2A finalization needs private data to reconstruct the frozen final fit, use the existing final Phase17 interfaces.

Do not invent a second training path.

---

# 117. Safe validation command

```bash
python scripts/validate_model_artifacts.py   --config configs/model_artifacts.yaml   --registry models/artifact_registry.json   --mode all-safe   --report-dir reports/private/phase32_model_artifacts
```

No raw data should be needed.

---

# 118. Private parity command

Recommended shape:

```bash
python scripts/run_model_artifact_parity.py   --artifact-config configs/model_artifacts.yaml   --registry models/artifact_registry.json   --raw-root data/raw   --dataset-manifest configs/dataset_manifest.yaml   --task1-frozen-output outputs/submission_task1.csv   --task2a-frozen-output outputs/submission_task2a.csv   --report-dir reports/private/phase32_model_artifacts
```

Run locally.

Do not send private rows to external agents.

---

# 119. Sanitized private-parity output

Expected:

```text
TASK1 SERVICE LOADED-PREDICTION PARITY    : PASS

TASK1 LATE LOADED-PREDICTION PARITY       : PASS

TASK1 ID SET                              : PASS
TASK1 ROW ORDER                           : PASS

TASK2A TOTAL LOADED-PREDICTION PARITY     : PASS

TASK2A CHILLED LOADED-PREDICTION PARITY   : PASS

TASK2A ID SET                             : PASS
TASK2A ROW ORDER                          : PASS

MAX DIFFS                                 : WITHIN CONFIGURED TOLERANCE

OFFICIAL OUTPUTS CHANGED                  : NO
```

Do not print real IDs.

---

# 120. Recommended full Phase32 local result

```text
WAYLOOM — PHASE 32 MODEL ARTIFACT MANAGEMENT

DT-412 TASK1 SERVICE ARTIFACT             : PASS
DT-413 TASK1 LATENESS ARTIFACT            : PASS
DT-414 TASK2A ARTIFACT BUNDLE             : PASS
DT-415 PREPROCESSING STATE                : PASS / NOT_REQUIRED
DT-416 MODEL/RUNTIME VERSIONS             : PASS
DT-417 SERIALIZATION                      : PASS
DT-418 FRESH-PROCESS DESERIALIZATION      : PASS
DT-419 LOADED-PREDICTION PARITY           : PASS

ARTIFACT REGISTRY                         : PASS
CHECKSUMS                                 : PASS
FEATURE SCHEMAS                           : PASS
PACKAGE-RELATIVE PATHS                    : PASS
PHASE31 LOADER BRIDGE                     : PASS

TASK1 CANONICAL ARTIFACTS CHANGED         : NO

OFFICIAL TASK1 CSV CHANGED                : NO
OFFICIAL TASK2A CSV CHANGED               : NO
OFFICIAL TASK2B CSV CHANGED               : NO

PHASE 32                                  : PASS

AUTHORIZED NEXT ACTION:
RETURN TO PHASE31 FINAL CLOSURE

READY FOR PHASE33:
NO
```

---

# 121. STOP conditions

`PHASE 32 PASS` is blocked if:

- any DT-412–DT-419 task incomplete;
- Task1 canonical artifact changed;
- Task1 canonical model missing;
- Task1 model/config mismatch;
- Task1 feature schema mismatch;
- Task1 lateness positive class ambiguous;
- required calibrator missing;
- Task2A final strategy unresolved;
- Task2A required component missing;
- Task2A weights/config differ from frozen final;
- Task2A serialization requires new model selection;
- required learned preprocessing state missing;
- registry contains absolute path;
- registry path escapes model root;
- checksum mismatch;
- loader deserializes before integrity check;
- arbitrary untrusted pickle path allowed;
- runtime version metadata missing;
- serialization round-trip fails;
- fresh-process load fails;
- loaded predictions do not reproduce frozen outputs;
- ID set changes;
- row order changes;
- official CSV changes;
- Task2B final artifacts change;
- private real rows are exposed;
- Phase33 work introduced;
- tests fail;
- `pip check` fails;
- independent review fails.

---

# 122. Definition of Done

Phase 32 is complete only when:

- [ ] DT-412 PASS
- [ ] DT-413 PASS
- [ ] DT-414 PASS
- [ ] DT-415 PASS
- [ ] DT-416 PASS
- [ ] DT-417 PASS
- [ ] DT-418 PASS
- [ ] DT-419 PASS
- [ ] official model-file deliverable is satisfiable from final package
- [ ] Task1 service canonical artifact registered
- [ ] Task1 service artifact loadable
- [ ] Task1 service artifact unchanged
- [ ] Task1 lateness canonical artifact registered
- [ ] Task1 lateness artifact loadable
- [ ] Task1 lateness artifact unchanged
- [ ] late positive class recorded
- [ ] calibration state correct
- [ ] Task2A final artifact representation matches frozen strategy
- [ ] all Task2A required components saved
- [ ] Task2A artifact manifest complete
- [ ] preprocessing mode recorded for every final component
- [ ] external preprocessing objects saved if required
- [ ] no unnecessary raw training data packaged
- [ ] feature schemas preserved
- [ ] Python/runtime model-library versions recorded
- [ ] artifact registry schema version recorded
- [ ] all required artifact SHA256 hashes recorded
- [ ] all artifact paths package-relative
- [ ] path-containment guard passes
- [ ] hash-before-deserialize guard passes
- [ ] serialization round-trip passes
- [ ] fresh-process deserialization passes
- [ ] synthetic round-trip parity passes
- [ ] Task1 service private end-to-end parity passes
- [ ] Task1 late private end-to-end parity passes
- [ ] Task2A total private end-to-end parity passes
- [ ] Task2A chilled private end-to-end parity passes
- [ ] Task1 ID set/order exact
- [ ] Task2A ID set/order exact
- [ ] official Task1 CSV unchanged
- [ ] official Task2A CSV unchanged
- [ ] official Task2B CSV unchanged
- [ ] Phase31 loader bridge passes
- [ ] targeted artifact tests pass
- [ ] relevant Phase10/17 regression tests pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] `git diff --check` passes
- [ ] private reports ignored
- [ ] fresh independent Phase32 review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 32 STATUS: PASS
MODEL ARTIFACT BUNDLE: FINAL
FROZEN PREDICTIONS: REPRODUCED
TASK1 CANONICAL ARTIFACTS: UNCHANGED
OFFICIAL SUBMISSIONS: UNCHANGED
AUTHORIZED NEXT ACTION: RETURN TO PHASE31 FINAL CLOSURE
READY FOR PHASE33: NO
```

---

# 123. Git workflow

Recommended:

```bash
git checkout main
git pull
git checkout -b feature/phase-32-model-artifacts
```

If Phase 31 changes are still on an unmerged branch and Phase 32 loader work depends on them, branch from the validated Phase 31 commit according to the team's Git workflow.

Do not lose current work just to force a branch name.

Recommended commits:

```text
feat(artifacts): add final model artifact registry and integrity checks

feat(task2a): serialize final forecast artifact bundle

feat(artifacts): save required preprocessing and runtime metadata

test(artifacts): add serialization deserialization and parity guards

docs(artifacts): document saved-model loading contract
```

Before commit:

```bash
git status
git diff
git diff --check
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

Do not stage temporary serialization candidates.

---

# 124. Recommended safe tests

```bash
pytest -q   tests/test_artifact_registry.py   tests/test_task1_artifact_roundtrip.py   tests/test_task2a_artifact_roundtrip.py   tests/test_preprocessing_artifacts.py   tests/test_artifact_clean_process_load.py   tests/test_artifact_prediction_parity.py   tests/test_artifact_security.py   tests/test_phase31_artifact_bridge.py
```

Then relevant Phase 10 / Phase 17 inference regressions.

Then:

```bash
pytest -q

python -m pip check

git diff --check

git status
```

---

# 125. Human local gate

After the agent implementation passes safe tests:

1. run finalization locally;
2. run safe artifact validation;
3. run private real-data parity;
4. confirm official output hashes unchanged;
5. provide only the sanitized PASS/FAIL summary;
6. run a fresh independent Phase 32 review.

Do not send private row-level predictions to an external agent.

---

# 126. Phase 32 completion does not finish Phase 31

This must be explicit.

After Phase 32 review PASS:

```text
return to Phase31
```

Complete:

```text
DT-405 — final cell loads saved artifacts

DT-409 — clean-kernel Run All

DT-411 — no hidden state / final-cell-only fresh-kernel run
```

Then conduct the final Phase 31 independent review.

Only after that should Phase 33 begin.

---

# 127. Recommended model

Phase 32 is high-risk because a serialization bug can silently change final predictions while all model-selection work remains correct.

Recommended:

```text
GPT-5.6 Sol
Reasoning: High
```

for implementation.

Use a fresh session with the same level for independent review.

---

# 128. Ready-to-copy Cursor/Codex implementation prompt

```text
You are implementing WayLoom Datathon PHASE 32 only.

PHASE:
Model Artifact Management

TASK RANGE:
DT-412 through DT-419

EXECUTION MODE:
ARTIFACT-FINALIZATION + LOADABILITY + ROUND-TRIP/PARITY VALIDATION.
NO MODEL RETUNING.
NO CHAMPION CHANGES.
NO OFFICIAL SUBMISSION CHANGES.
PRIVATE REAL-DATA PARITY RUNS ARE HUMAN-LOCAL ONLY.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 33.
AFTER PHASE32 PASS, RETURN TO PHASE31 FINAL CLOSURE.

==================================================
MISSION
==================================================

Complete every Phase32 task:

DT-412 Save Task 1 service model
DT-413 Save Task 1 lateness model
DT-414 Save Task 2A model/artifacts if applicable
DT-415 Save preprocessing objects if necessary
DT-416 Record model versions
DT-417 Test model serialization
DT-418 Test model deserialization
DT-419 Compare loaded-model predictions with original predictions

Official booklet requirement:

"Model file(s). Save your final model files alongside the notebook."

The final notebook must also:

"Add a final cell that loads the saved models, demonstrates inference for
Task 1 and Task 2A, and clearly prints the inputs and predictions."

Therefore Phase32 must produce a self-describing, loadable, versioned artifact
bundle that Phase31 can load in a completely fresh kernel/process.

==================================================
IMPORTANT CROSS-PHASE STATE
==================================================

Task1 final model artifacts were already created/frozen in Phase10.

Phase32 must NOT blindly overwrite them.

For DT-412 / DT-413:

if canonical Phase10 artifacts exist and pass integrity:
REGISTER + VALIDATE them.

Do not re-save/retrain merely to satisfy the task.

If canonical Phase10 artifacts are missing or corrupted:
STOP and report an upstream Task1 artifact blocker.

Task2A Phase17 explicitly deferred formal artifact management to Phase32.

For DT-414:

discover the ACTUAL frozen Task2A champion strategy and serialize/register
everything required for inference.

After Phase32 passes:

return to Phase31.

Phase31 must then close:

DT-405
DT-409
DT-411

with clean-kernel and final-cell-only tests.

Phase32 PASS alone does NOT authorize Phase33.

==================================================
SOURCE AUTHORITY
==================================================

Read in this order:

1. Official Challenge Booklet
   - Rules and Regulations
   - Deliverables
   - "Model file(s)"
   - "Final notebook"

2. WAYLOOM_DATATHON_MASTER_PLAN.md
   - Phase32 DT-412–DT-419

3. PHASE_10_COMPETITION_CONTRACT.md
   - final Task1 model artifacts/inference

4. PHASE_17_COMPETITION_CONTRACT.md
   - final Task2A model/inference
   - explicit Phase32 artifact ownership

5. PHASE_31_COMPETITION_CONTRACT.md
   - DT-405 dependency on DT-412–DT-419
   - clean-kernel/final-cell-only requirements

6. Final configs, safe metadata and tracked implementation.

Do NOT resolve conflicts with generic ML knowledge.

If a final model family/strategy cannot be resolved from tracked final state:
STOP.

==================================================
OFFICIAL RESTRICTIONS
==================================================

Preserve official restrictions:

- no prohibited pretrained models
- no proprietary API-based modelling/preprocessing
- no fully automated end-to-end low/no-code modelling
- competition data remains confidential
- datasets/derivatives are not shared with third parties

Artifact creation/loading must remain local.

Do not download models from external services.

Do not upload model bundles or data to third-party artifact stores.

==================================================
FROZEN ARTIFACTS — MUST NOT CHANGE
==================================================

Do NOT modify or regenerate:

outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv

Task2B frozen allocation/policy

Task1 final champion selection/config

Task2A final champion selection/config

Task1 final predictions

Task2A final predictions

Task1 Phase10 canonical model artifacts, if already frozen and valid

If Task1 Phase10 artifact bytes must change:
STOP.
That is an upstream reopen, not routine Phase32 work.

==================================================
READ FIRST — REPOSITORY
==================================================

Read:

AGENTS.md
CODEX_HANDOFF_PHASE_11_ONWARDS.md
WAYLOOM_DATATHON_MASTER_PLAN.md
PHASE_10_COMPETITION_CONTRACT.md
PHASE_17_COMPETITION_CONTRACT.md
PHASE_31_COMPETITION_CONTRACT.md
PHASE_32_COMPETITION_CONTRACT.md

Inspect:

configs/task1_final_models.yaml
configs/task2a_final_models.yaml

models/task1_service/**
models/task1_late/**

Task1 saved-artifact loaders / inference code

Task2A final training/inference code
Task2A runtime state / final model metadata if present

final feature registries / feature schemas

requirements.txt
pyproject.toml / lockfile if present

tests for final Task1/Task2A inference.

Do not inspect private row values.

==================================================
CREATE / UPDATE
==================================================

Use repository conventions where existing interfaces already exist.

Recommended additions:

configs/model_artifacts.yaml

models/artifact_registry.json
models/README.md

models/task2a/
  artifact_manifest.json
  ... actual final Task2A component artifacts ...

src/common/artifact_io.py
src/common/artifact_registry.py
src/common/versioning.py

scripts/finalize_model_artifacts.py
scripts/validate_model_artifacts.py
scripts/run_model_artifact_parity.py

docs/model_artifacts.md

tests/test_artifact_registry.py
tests/test_task1_artifact_roundtrip.py
tests/test_task2a_artifact_roundtrip.py
tests/test_preprocessing_artifacts.py
tests/test_artifact_clean_process_load.py
tests/test_artifact_prediction_parity.py
tests/test_artifact_security.py
tests/test_phase31_artifact_bridge.py

If equivalent modules already exist:
extend/reuse them rather than creating duplicate loaders.

Do NOT create Phase33 submission-file testing.

==================================================
RECOMMENDED FINAL PACKAGE LAYOUT
==================================================

Phase40 will own final packaging, but Phase32 should make artifacts compatible
with a package such as:

TeamName_FinalNotebook.ipynb
models/
  artifact_registry.json
  README.md
  task1_service/
  task1_late/
  task2a/

All paths in artifact/config metadata should be package-relative.

Do not store absolute workstation paths.

==================================================
ARTIFACT REGISTRY
==================================================

Create:

models/artifact_registry.json

Recommended top-level fields:

artifact_schema_version
phase
created_with
task1_service
task1_late
task2a
shared_preprocessing
runtime_versions

Each artifact entry should include safe metadata:

artifact_id
task
target
artifact_kind
model_family
strategy/config_id
serializer
format
relative_path
sha256
size_bytes
feature_schema_ref
preprocessor_mode
postprocessing_ref
required
library_versions
load_entrypoint
inference_entrypoint

Task1 lateness should also record:

positive_class mapping
calibration mode
calibration artifact reference if applicable

Do not store private rows.

Do not store absolute paths.

Do not store raw training data fingerprints unless already required and safe.

==================================================
ARTIFACT FILE HASHING
==================================================

Compute SHA256 for every required model/preprocessing artifact.

The registry should list artifact hashes.

Do not hash the registry into itself.

Loader behavior:

resolve relative path
verify it remains inside approved model root
verify file exists
verify SHA256
THEN deserialize

Checksum mismatch:
hard failure.

Do not deserialize first and check later.

==================================================
SECURE DESERIALIZATION
==================================================

Pickle/joblib-style formats can execute code during deserialization.

Rules:

- only load trusted local artifacts from the Phase32 registry
- reject arbitrary user-supplied paths
- require hash verification first
- prefer model-family native formats where practical
- no network URLs
- no untrusted pickle uploads

Do not create a generic:
load_any_pickle(path_from_user)

API.

==================================================
SERIALIZER SELECTION
==================================================

Use the selected final model's appropriate serializer.

Examples only:

CatBoost:
native .cbm

LightGBM Booster:
native model text/string format

XGBoost:
JSON/UBJ/native model format

scikit-learn / custom sklearn pipeline:
joblib only when needed

custom deterministic baseline:
versioned JSON/typed state artifact

fixed ensemble:
component artifacts + ensemble manifest/weights

Do NOT switch model family merely for easier serialization.

Do NOT assume any example family is the actual final model.

Discover the actual family from frozen config/metadata.

==================================================
DT-412 — SAVE TASK1 SERVICE MODEL
==================================================

Canonical Phase10 location is expected to be similar to:

models/task1_service/model.*
models/task1_service/metadata.json
models/task1_service/feature_schema.json

If the canonical Phase10 service artifact already exists:

1. do not overwrite it
2. verify required files
3. verify metadata matches final config
4. verify feature schema
5. verify current loader can load it
6. verify checksum
7. register it in models/artifact_registry.json

If a required external preprocessing object belongs to service inference:
register it under DT-415.

If service preprocessing is embedded:
record:
preprocessor_mode = embedded

If deterministic code only:
record:
preprocessor_mode = deterministic_code

==================================================
TASK1 SERVICE REQUIRED METADATA
==================================================

At minimum resolve:

task = task1_service

final model family

config ID

feature schema/version

serializer/format

service postprocessing

library version(s)

relative artifact path(s)

SHA256

canonical loader

Do not invent the model family.

==================================================
TASK1 SERVICE STOP CONDITIONS
==================================================

STOP if:

canonical Phase10 model missing

metadata does not match final config

feature schema differs from frozen inference schema

artifact checksum mismatches established freeze evidence

loading requires retraining

loaded service predictions violate nonnegative final postprocessing semantics

==================================================
DT-413 — SAVE TASK1 LATENESS MODEL
==================================================

Expected canonical Phase10 bundle may include:

models/task1_late/model.*
models/task1_late/metadata.json
models/task1_late/feature_schema.json
models/task1_late/calibration.*

Calibration artifact exists only if frozen final configuration uses one.

If canonical artifacts already exist:
REGISTER + VALIDATE.
Do not overwrite.

==================================================
TASK1 LATENESS REQUIRED METADATA
==================================================

Record:

model family

config ID

feature schema

serializer

probability output method

positive class mapping

class ordering if relevant

calibration mode:
none / isotonic / sigmoid / other actual frozen method

calibration artifact path if required

library versions

artifact hashes

canonical loader

==================================================
TASK1 LATENESS PARITY RISKS
==================================================

Deserialization must preserve:

class ordering

positive-class index

raw probability semantics

calibration

final probability range [0,1]

If class ordering changes after reload:
FAIL.

If a required calibrator is missing:
FAIL.

If final probability differs beyond parity tolerance:
FAIL.

==================================================
DT-414 — SAVE TASK2A MODEL / ARTIFACTS
==================================================

Phase17 deliberately leaves formal artifact management to Phase32.

First discover:

final_strategy

total champion

chilled champion / derived strategy

number of model components

horizon strategy

ensemble weights/components if applicable

baseline configuration if applicable

postprocessing

Do not assume one single model file.

==================================================
TASK2A ARTIFACT KIND
==================================================

Registry should support explicit kinds such as:

trained_model

baseline_strategy

ensemble

multi_model_bundle

derived_target_strategy

The exact value must reflect implementation.

Do not pretend a baseline is a trained model.

Do not pretend a derived chilled target has a separate model.

==================================================
TASK2A TRAINED MODEL CASE
==================================================

If final Task2A uses trained model(s):

serialize every component required for final inference.

Examples:

total model

Fresh chilled model

horizon-specific models h=1..10

brand-specific models

ensemble components

Only actual final components.

Use stable component IDs.

==================================================
TASK2A ENSEMBLE CASE
==================================================

Save:

each required component model/artifact

ensemble manifest

component IDs

weights

target/horizon mapping

postprocessing

The loader must reconstruct the exact frozen ensemble.

Do not recompute/retune weights.

==================================================
TASK2A BASELINE CHAMPION CASE
==================================================

If the frozen champion is a deterministic baseline:

no fake trained model binary is required.

Save a versioned strategy artifact containing the fixed parameters/state
required to instantiate the predictor.

Examples may include:

window
weights
fallback
seasonal offset

ONLY actual frozen settings.

Registry:

artifact_kind = baseline_strategy

The Phase31 final cell must be able to load this saved artifact and instantiate
the predictor without model selection/retraining.

==================================================
TASK2A PRIVATE HISTORY
==================================================

Do not package raw historical training rows into the model bundle merely for
convenience.

If inference requires demand history:
the final inference pipeline may rebuild/load authorized local history using
the canonical data pipeline.

The saved model artifact should contain learned/frozen model state and
configuration, not a copy of the competition dataset.

If a model inherently stores fitted state internally:
that is acceptable as model state.

Do not add an exported training dataframe.

==================================================
TASK2A MANIFEST
==================================================

Create:

models/task2a/artifact_manifest.json

Recommended:

artifact_schema_version
task = task2a
final_strategy
targets
forecast_horizon_weeks = 10
components
preprocessing
postprocessing
library_versions
feature_schema_refs
component hashes

All component paths relative.

No private IDs.

==================================================
TASK2A FINALIZATION
==================================================

External agent may implement finalization code/tests using synthetic fixtures.

Do NOT run real private Task2A final training in agent context.

Human-local finalization may:

reconstruct the frozen final fit if needed

using the existing Phase17 final training path

with the exact frozen config

solely to obtain the final saved artifact

No hyperparameter search.
No champion change.
No new validation selection.

If Phase17 already preserved the final runtime object safely:
serialize that through the canonical finalization path.

==================================================
DT-415 — SAVE PREPROCESSING OBJECTS IF NECESSARY
==================================================

For each final model/component determine:

preprocessor_mode:

embedded

external_serialized

deterministic_code

not_required

If external learned preprocessing state is required for correct inference:

save it.

Examples:

encoder
scaler
imputer
categorical mapping
feature selector
learned transformation state

Only actual final objects.

==================================================
DO NOT SERIALIZE UNNECESSARY DATA
==================================================

Do not serialize:

entire training DataFrame

test DataFrame

private row examples

EDA tables

validation predictions

temporary experiment caches

unless they are genuinely model state required for inference.

Phase32 is model-artifact management, not data archiving.

==================================================
FEATURE SCHEMA IS REQUIRED STATE
==================================================

Even if no learned preprocessor exists, preserve/point to:

exact feature names

feature order

dtypes/categories where required

registry version

categorical feature positions/names where model family needs them

This prevents silent inference drift.

==================================================
PREPROCESSOR EMBEDDED CASE
==================================================

If model artifact already contains the full preprocessing pipeline:

do not save a duplicate preprocessor.

Record:

preprocessor_mode = embedded

and test fresh-process inference through the embedded pipeline.

==================================================
DETERMINISTIC-CODE PREPROCESSING
==================================================

If features are computed by canonical deterministic code with no learned
state:

record:

preprocessor_mode = deterministic_code

feature builder version/ref

feature schema/hash

No fake serialized preprocessor file is needed.

==================================================
DT-416 — RECORD MODEL VERSIONS
==================================================

Record a targeted runtime/version snapshot.

At minimum:

Python version

numpy

pandas

model-family library for each final model

scikit-learn/joblib if used

other serializer/runtime library actually required

OR-Tools is not required for Task1/Task2A loading unless a shared environment
manifest intentionally includes it.

Do not dump unrelated packages just for volume.

==================================================
VERSION CAPTURE
==================================================

Use:

importlib.metadata.version(...)

where possible.

Record:

package name
installed version

For Python:
sys.version_info normalized

Also record:

artifact format version

artifact schema version

config ID

feature schema version

git commit if available

Do not record machine username/home directory.

==================================================
VERSION COMPATIBILITY POLICY
==================================================

Exact environment recreation is preferred.

Loader validator should compare current runtime to recorded versions.

Recommended severity:

same exact version:
PASS

patch/minor difference:
WARN unless model library is known incompatible or round-trip fails

major-version difference:
BLOCK by default for model/serializer libraries

But prediction/load tests are authoritative.

Do not silently load an artifact under an obviously incompatible runtime.

==================================================
MODELS README
==================================================

Create:

models/README.md

Explain:

official requirement

artifact layout

registry

how to load

version requirements

checksum verification

Task2A strategy type

preprocessing-state handling

Phase31 final-cell relationship

No private data.

==================================================
DT-417 — TEST MODEL SERIALIZATION
==================================================

Serialization test means:

the canonical saver can persist the selected model/state correctly.

Do not prove this by overwriting canonical artifacts.

Use:

temporary directory

or controlled Task2A finalization output before atomic promotion.

==================================================
SERIALIZATION TEST — TASK1
==================================================

Because Task1 artifacts are already frozen:

load canonical trusted artifact

serialize a temporary copy using canonical save interface when supported

reload temp copy

predict on synthetic fixture

compare to prediction from canonical loaded artifact

Do NOT rewrite canonical Task1 artifact.

If model-family native serializer cannot safely re-save without changes:
the existing Phase10 save/reload evidence plus current load test may satisfy
the serialization proof, but document this explicitly.

==================================================
SERIALIZATION TEST — TASK2A
==================================================

For new Phase32 Task2A artifacts:

before atomic promotion:

original final in-memory/state predictor

predict deterministic validation fixture

save candidate artifact to temp

reload candidate

predict same fixture

compare

only then atomically move/copy into canonical models/task2a path

Do not promote a candidate that fails parity.

==================================================
SYNTHETIC SERIALIZATION FIXTURES
==================================================

Agent-run tests must use synthetic input fixtures.

They should exercise:

feature ordering

categoricals if applicable

missing handling if applicable

multiple horizons if applicable

total/chilled output path

ensemble/baseline strategy if applicable

No private row values.

==================================================
DT-418 — TEST MODEL DESERIALIZATION
==================================================

Deserialization must be tested in a FRESH process.

This proves:

no hidden model object

no notebook state

no training code side effect

no import-time retraining

Recommended subprocess:

python scripts/validate_model_artifacts.py --load-only ...

or a dedicated clean-process test.

==================================================
CLEAN-PROCESS LOAD CONTRACT
==================================================

Fresh process must:

read registry

verify checksums

verify version compatibility

load service model

load late model/calibrator

load Task2A artifact bundle

load external preprocessing if required

validate feature schemas

construct predictor interfaces

exit PASS

No training data required for load-only smoke test.

No optimizer required.

==================================================
DESERIALIZATION NEGATIVE TESTS
==================================================

Test:

missing artifact

checksum mismatch

wrong feature schema

missing calibrator

unknown serializer

unsupported artifact schema version

path traversal / path outside model root

corrupt file

wrong positive-class metadata

missing Task2A component

ensemble weight/component mismatch

Each must fail clearly.

==================================================
DT-419 — COMPARE LOADED PREDICTIONS WITH ORIGINAL
==================================================

This is the strongest Phase32 gate.

Use two levels:

LEVEL A:
synthetic round-trip parity

LEVEL B:
human-local end-to-end parity against frozen final official predictions

Both required for final Phase32 PASS.

==================================================
LEVEL A — SYNTHETIC ROUND-TRIP
==================================================

Agent can run this.

For each relevant final artifact type:

original/canonical predictor
vs
freshly loaded predictor

on deterministic synthetic features/requests.

Require numerical parity under explicit tight tolerances.

No private data.

==================================================
LEVEL B — TASK1 FROZEN OUTPUT PARITY
==================================================

Human-local only.

Reload ONLY saved Task1 artifacts from registry.

Run canonical Task1 inference on official private inputs.

Compare to frozen:

outputs/submission_task1.csv

Require:

same delivery_id set

same row order

same number of rows

service predictions equivalent

late probabilities equivalent

same final postprocessing/calibration

No official output rewrite.

Do not save a replacement submission.

==================================================
LEVEL B — TASK2A FROZEN OUTPUT PARITY
==================================================

Human-local only.

Reload ONLY saved Task2A artifact bundle.

Run canonical Task2A inference with authorized local history/test inputs.

Compare to frozen:

outputs/submission_task2a.csv

Require:

same row_id set

same row order

same row count

total predictions equivalent

chilled predictions equivalent

Style/Tech chilled rule unchanged

same final postprocessing

Do not rewrite the official submission.

==================================================
PARITY TOLERANCES
==================================================

Create explicit config values.

Recommended starting point for same-environment floating predictions:

raw_atol: 1e-12
raw_rtol: 1e-10

final_output_atol: 1e-10
final_output_rtol: 1e-10

But use tighter/exact comparison when the canonical implementation supports it.

Do not loosen tolerance simply to make a failed artifact pass.

If official output applies rounding/formatting:
compare through the canonical final postprocessing/formatting semantics.

ID/order mismatches have ZERO tolerance.

==================================================
PARITY REPORT
==================================================

Create private:

reports/private/phase32_model_artifacts/parity_report.json

Store:

Task1 service parity PASS/FAIL

Task1 late parity PASS/FAIL

Task2A total parity PASS/FAIL

Task2A chilled parity PASS/FAIL

row/ID/order parity

max_abs_diff aggregate

max_rel_diff aggregate where useful

tolerance

artifact registry SHA256

runtime version result

Do NOT store mismatching real IDs in the report intended for sharing.

Detailed local debugging IDs, if absolutely needed:
keep in a separate untracked private debug file.

==================================================
PHASE32 PRIVATE REPORTS
==================================================

Recommended:

reports/private/phase32_model_artifacts/
  run_manifest.json
  artifact_integrity.json
  serialization_report.json
  deserialization_report.json
  parity_report.json
  phase32_gate.json

All private reports ignored/untracked.

The tracked registry under models/ should contain artifact metadata only.

==================================================
ATOMIC ARTIFACT FINALIZATION
==================================================

For Task2A new artifacts:

write to temporary staging directory

validate files

compute hashes

run round-trip

verify registry candidate

then atomically promote to canonical models/task2a/

Never leave half-written canonical bundle.

If canonical Task2A bundle already exists:
require explicit overwrite protection.

Do not overwrite without a controlled re-finalization reason.

==================================================
ARTIFACT OVERWRITE POLICY
==================================================

Task1 canonical:
overwrite forbidden in Phase32.

Task2A canonical:
if absent, create once after candidate validation.

If present and registered:
default overwrite forbidden.

A controlled refinalization must require explicit flag and prove final config
has not changed.

Do not silently replace.

==================================================
ARTIFACT REGISTRY VALIDATION
==================================================

Validate:

all required entries present

relative paths only

paths remain inside models/

every required file exists

SHA256 matches

size matches if recorded

artifact schema version supported

model family matches final config

config ID matches final config

feature schema matches final config

preprocessing mode complete

Task1 late positive class/calibration complete

Task2A component set complete

runtime versions recorded

no private data/path

==================================================
CONFIG
==================================================

Create:

configs/model_artifacts.yaml

Recommended shape:

version: 1

model_root: models
registry: models/artifact_registry.json

task1:
  service:
    mode: register_existing
    config: configs/task1_final_models.yaml
  late:
    mode: register_existing
    config: configs/task1_final_models.yaml

task2a:
  mode: finalize_or_register
  config: configs/task2a_final_models.yaml

integrity:
  verify_sha256_before_load: true
  allow_absolute_paths: false
  allow_paths_outside_model_root: false
  overwrite_existing: false

versions:
  record_python: true
  record_runtime_packages: true

parity:
  raw_atol: 1.0e-12
  raw_rtol: 1.0e-10
  final_atol: 1.0e-10
  final_rtol: 1.0e-10
  require_id_order_exact: true

security:
  allow_network_artifacts: false
  allow_unregistered_pickle: false

Adapt names to existing repository conventions.

==================================================
FINALIZATION SCRIPT
==================================================

Create:

scripts/finalize_model_artifacts.py

Responsibilities:

load configs

discover final model strategies

register existing Task1 artifacts without overwrite

finalize Task2A artifacts if necessary

save required preprocessing objects if necessary

capture versions

compute hashes

write candidate registry

validate candidate

atomically publish Task2A/registry

write private run report

Do not run hyperparameter search.

Do not train Task1.

==================================================
VALIDATION SCRIPT
==================================================

Create:

scripts/validate_model_artifacts.py

Modes:

--load-only
--integrity
--synthetic-roundtrip
--all-safe

No private raw data required for safe validation.

It should print aggregate PASS/FAIL only.

==================================================
PRIVATE PARITY SCRIPT
==================================================

Create:

scripts/run_model_artifact_parity.py

This is human-local only.

Expected inputs:

raw root / manifest as required by canonical inference

artifact config/registry

frozen Task1 output

frozen Task2A output

private report dir

It must:

reload artifacts fresh

run canonical inference

compare

print only aggregate results

never overwrite official CSVs

==================================================
TASK1 FROZEN HASH GUARD
==================================================

Before Phase32 local finalization:

hash canonical Task1 artifact files.

After Phase32:

require exact match.

If changed:
FAIL.

Phase32 should register Task1 artifacts, not mutate them.

==================================================
OFFICIAL OUTPUT HASH GUARD
==================================================

Before/after Phase32:

outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv

must be byte-identical.

Phase32 must not regenerate them.

==================================================
TASK2A OUTPUT PARITY VS BYTE HASH
==================================================

Task2A new model artifact may be created in Phase32.

But:

outputs/submission_task2a.csv

must remain unchanged.

Loaded-artifact inference must reproduce its predictions.

This is the acceptance oracle.

==================================================
MODEL FILE "ALONGSIDE NOTEBOOK"
==================================================

Official wording:

"Save your final model files alongside the notebook."

Phase32 should ensure:

the notebook can resolve models using relative/package paths

the artifact registry uses package-relative paths

no workstation-specific path required

Phase40 will assemble the final submission folder.

Do not copy model files into arbitrary notebook cell attachments.

==================================================
PHASE31 BRIDGE
==================================================

Create/maintain a stable loader interface Phase31 can use.

Recommended:

load_task1_service_bundle(registry)
load_task1_late_bundle(registry)
load_task2a_bundle(registry)

and task-level predictors:

predict_task1_from_saved_artifacts(...)
predict_task2a_from_saved_artifacts(...)

Use existing canonical names if already present.

After Phase32 PASS:
return to Phase31.

Do not edit Phase31 notebook here unless the loader contract must be repaired
for compatibility and the change is clearly Phase32-related.

Preferred:
finish loader interface,
then Phase31 closure updates/executes the final cell.

==================================================
PHASE31 GATE ARTIFACT
==================================================

Private local:

reports/private/phase32_model_artifacts/phase32_gate.json

Recommended:

phase: 32
status: PASS
dt412: PASS
...
dt419: PASS
task1_artifacts_unchanged: true
official_outputs_unchanged: true
task1_parity: PASS
task2a_parity: PASS
fresh_process_load: PASS

No private IDs.

Phase31 may use the sanitized status, not private row contents.

==================================================
TESTS — REGISTRY
==================================================

Create:

tests/test_artifact_registry.py

Test:

supported schema version

all final tasks represented

relative paths

path containment

required files

checksum verification

config ID parity

model-family parity

preprocessing mode enum

version metadata

no absolute paths

no private row fields

unknown artifact kind rejected

==================================================
TESTS — TASK1 ROUNDTRIP
==================================================

Create:

tests/test_task1_artifact_roundtrip.py

Using synthetic fixtures:

service canonical load works

service temporary reserialize/reload parity where supported

late canonical load works

late temporary reserialize/reload parity where supported

positive class preserved

calibrator preserved if applicable

probability bounds

feature order/schema enforced

canonical Task1 files not modified

==================================================
TESTS — TASK2A ROUNDTRIP
==================================================

Create:

tests/test_task2a_artifact_roundtrip.py

Test synthetic representations for actual supported final strategy.

At minimum cover the selected strategy.

Also unit-test loader branch behavior for:

trained model

baseline strategy

ensemble/multi-model only if repository actually supports them.

Do not create dead complexity unrelated to final code.

Require:

component completeness

target/horizon mapping

weights preserved

feature schema

postprocessing metadata

save/reload parity

==================================================
TESTS — PREPROCESSING
==================================================

Create:

tests/test_preprocessing_artifacts.py

Test:

external learned preprocessor required -> must be registered

embedded -> no duplicate required

deterministic_code -> no fake serialized object

not_required -> valid only when inference truly has no state

feature schema always present/referenced

missing required preprocessor -> fail

==================================================
TESTS — CLEAN PROCESS
==================================================

Create:

tests/test_artifact_clean_process_load.py

Launch subprocess with:

fresh Python process

no preexisting model objects

load registry

load all final artifacts

run synthetic inference smoke

return zero

Test that loader does not call training functions.

==================================================
TESTS — PREDICTION PARITY
==================================================

Create:

tests/test_artifact_prediction_parity.py

Synthetic:

exact IDs/keys

numerical tolerances

postprocessing parity

class mapping

Style/Tech chilled if Task2A fixture covers them

negative test beyond tolerance -> fail

row order mismatch -> fail

missing row -> fail

duplicate row -> fail

==================================================
TESTS — SECURITY
==================================================

Create:

tests/test_artifact_security.py

Test:

absolute path rejected

../ traversal rejected

path outside models root rejected

checksum mismatch fails before load

unknown serializer rejected

unregistered pickle/joblib path rejected

network URL rejected

corrupt file fails safely

error message sanitized

==================================================
TESTS — PHASE31 BRIDGE
==================================================

Create:

tests/test_phase31_artifact_bridge.py

Test:

registry resolves Task1 service

registry resolves Task1 late/calibrator

registry resolves Task2A

loader functions import in a fresh process

no training required to load

paths relative/package-safe

final-cell loader interface can be called without earlier notebook state

Do not execute the private notebook.

==================================================
EDGE CASE — TASK1 ALREADY SAVED
==================================================

Expected.

DT-412/413 are satisfied by:

canonical file exists
+
integrity
+
registry
+
load test
+
parity

Do not resave.

==================================================
EDGE CASE — TASK1 ARTIFACT MISSING
==================================================

STOP.

Do not retrain Task1 under Phase32 without explicitly reopening the upstream
final-training phase.

Report:

UPSTREAM TASK1 ARTIFACT BLOCKER.

==================================================
EDGE CASE — TASK1 CALIBRATION NONE
==================================================

Registry:

calibration_mode = none

No fake calibration file.

Loader must still identify positive class correctly.

==================================================
EDGE CASE — PREPROCESSOR NOT REQUIRED
==================================================

DT-415 may PASS with:

preprocessor_mode = not_required

when proven by the canonical inference path.

The task says:
"if necessary."

Do not create useless serialized objects.

==================================================
EDGE CASE — PREPROCESSOR EMBEDDED
==================================================

Record embedded.

Round-trip test the whole pipeline/model.

No duplicate separate state.

==================================================
EDGE CASE — TASK2A BASELINE
==================================================

Save:

versioned baseline strategy/state

not a fake ML binary.

Fresh-process loader instantiates exact baseline predictor.

End-to-end parity must match frozen Task2A output.

==================================================
EDGE CASE — TASK2A ENSEMBLE
==================================================

All components and weights required.

One missing component:
FAIL.

One changed weight:
FAIL.

Do not fallback silently to a partial ensemble.

==================================================
EDGE CASE — TASK2A MULTI-HORIZON
==================================================

Manifest must map:

target
horizon
component artifact

unambiguously.

No row-position-based model selection.

==================================================
EDGE CASE — MODEL LIBRARY VERSION CHANGED
==================================================

If recorded/current version differs:

attempt safe load only according to compatibility policy.

If load/parity fails:
BLOCK.

Do not reserialize under a newer version merely to silence the warning unless
a controlled migration is explicitly approved.

==================================================
EDGE CASE — CHECKSUM MISMATCH
==================================================

STOP before deserialization.

Do not regenerate hash to match the changed file.

Investigate why artifact changed.

==================================================
EDGE CASE — FEATURE SCHEMA MISMATCH
==================================================

STOP.

Do not reorder/drop/add features silently to make predictions run.

The correct schema is the frozen final inference schema.

==================================================
EDGE CASE — PARITY FAILS ONLY AFTER POSTPROCESSING
==================================================

Investigate:

calibrator

clipping

chilled <= total constraint

Style/Tech chilled-zero rule

ensemble combination

formatting

Do not loosen tolerance before identifying the difference.

==================================================
EDGE CASE — PARITY FAILS BY ROW ORDER ONLY
==================================================

Official outputs require identity/order preservation.

Row order mismatch:
FAIL.

Do not sort the frozen official CSV to make comparison pass.

Make loaded inference preserve canonical template order.

==================================================
EDGE CASE — SERIALIZER BYTE OUTPUT CHANGES
==================================================

Prediction parity matters more than identical serialized bytes when testing
a temporary resave.

Canonical frozen artifact hashes still matter.

Do not require a temp reserialization to be byte-identical if serializer
metadata is nondeterministic.

==================================================
EDGE CASE — ARTIFACT HAS PRIVATE TRAINING DATA
==================================================

Some model formats naturally contain learned state.

That is acceptable.

But if a custom bundle explicitly includes raw training rows/dataframe:
STOP and remove unnecessary raw data from the bundle.

Do not expose artifact internals publicly beyond competition package.

==================================================
EDGE CASE — FINAL CONFIG REFERENCES ABSOLUTE PATH
==================================================

Phase32 registry must use relative package paths.

Do not make final notebook depend on:

C:\Users\...

/home/user/...

Convert path resolution to project/package-relative logic without changing
model semantics.

==================================================
EDGE CASE — PHASE31 CORE NOT READY
==================================================

Phase32 can still complete artifact management.

But after Phase32:
return to Phase31 final closure.

Do not skip the Phase31 clean-kernel and final-cell-only tests.

==================================================
SAFE AGENT TEST LOOP
==================================================

Run:

pytest -q \
  tests/test_artifact_registry.py \
  tests/test_task1_artifact_roundtrip.py \
  tests/test_task2a_artifact_roundtrip.py \
  tests/test_preprocessing_artifacts.py \
  tests/test_artifact_clean_process_load.py \
  tests/test_artifact_prediction_parity.py \
  tests/test_artifact_security.py \
  tests/test_phase31_artifact_bridge.py

Then relevant Phase10/17 inference tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run private real-data parity in external agent context.

==================================================
LOCAL HUMAN COMMAND — FINALIZATION
==================================================

Expected shape:

python scripts/finalize_model_artifacts.py \
  --config configs/model_artifacts.yaml \
  --task1-config configs/task1_final_models.yaml \
  --task2a-config configs/task2a_final_models.yaml \
  --registry models/artifact_registry.json \
  --report-dir reports/private/phase32_model_artifacts

If Task2A finalization requires authorized local data/runtime reconstruction,
use the actual repository's frozen Phase17 finalization CLI/arguments.

Do not invent paths if repository differs.

==================================================
LOCAL HUMAN COMMAND — SAFE VALIDATION
==================================================

Expected:

python scripts/validate_model_artifacts.py \
  --config configs/model_artifacts.yaml \
  --registry models/artifact_registry.json \
  --mode all-safe \
  --report-dir reports/private/phase32_model_artifacts

==================================================
LOCAL HUMAN COMMAND — PRIVATE PARITY
==================================================

Expected shape:

python scripts/run_model_artifact_parity.py \
  --artifact-config configs/model_artifacts.yaml \
  --registry models/artifact_registry.json \
  --raw-root data/raw \
  --dataset-manifest configs/dataset_manifest.yaml \
  --task1-frozen-output outputs/submission_task1.csv \
  --task2a-frozen-output outputs/submission_task2a.csv \
  --report-dir reports/private/phase32_model_artifacts

Use actual repository CLI.

Console must print aggregate PASS/FAIL only.

Do not print private row IDs.

==================================================
EXPECTED LOCAL SANITIZED RESULT
==================================================

WAYLOOM — PHASE 32 MODEL ARTIFACT MANAGEMENT

DT-412 TASK1 SERVICE ARTIFACT          : PASS
DT-413 TASK1 LATE ARTIFACT             : PASS
DT-414 TASK2A ARTIFACT BUNDLE          : PASS
DT-415 PREPROCESSING STATE              : PASS
DT-416 VERSION METADATA                 : PASS
DT-417 SERIALIZATION                     : PASS
DT-418 CLEAN DESERIALIZATION             : PASS
DT-419 LOADED-PREDICTION PARITY          : PASS

TASK1 CANONICAL ARTIFACTS CHANGED        : NO

TASK1 SERVICE PARITY                      : PASS
TASK1 LATE PARITY                         : PASS
TASK2A TOTAL PARITY                       : PASS
TASK2A CHILLED PARITY                     : PASS

TASK1 ID/ORDER PARITY                     : PASS
TASK2A ID/ORDER PARITY                    : PASS

ARTIFACT CHECKSUMS                        : PASS
FEATURE SCHEMAS                           : PASS
PREPROCESSOR COMPLETENESS                 : PASS
RUNTIME VERSION RECORD                    : PASS

FRESH-PROCESS LOAD                        : PASS

OFFICIAL TASK1 CSV CHANGED                : NO
OFFICIAL TASK2A CSV CHANGED               : NO
OFFICIAL TASK2B CSV CHANGED               : NO

PHASE 32                                  : PASS

AUTHORIZED NEXT ACTION:
RETURN TO PHASE31 FINAL CLOSURE

READY FOR PHASE33:
NO — UNTIL PHASE31 FINAL CLOSURE PASSES

==================================================
STOP CONDITIONS
==================================================

STOP if:

DT-412–DT-419 incomplete

Task1 canonical artifact modified

Task1 artifact missing/corrupt

Task1 final config/model family mismatch

Task1 feature schema mismatch

Task1 late positive-class mapping ambiguous

required Task1 calibrator missing

Task2A final strategy unresolved

Task2A component missing

Task2A ensemble weight mismatch

Task2A artifact requires retraining/model reselection

required preprocessing state missing

unnecessary raw training rows embedded in custom bundle

model version metadata absent

absolute model path required

artifact path escapes model root

checksum mismatch

deserialization occurs before checksum verification

untrusted arbitrary pickle allowed

fresh-process loading fails

loaded-model prediction parity fails

ID/order parity fails

official submission file changes

Task2B frozen artifact changes

Phase33 work introduced

==================================================
DEFINITION OF DONE
==================================================

Require:

DT-412 PASS
DT-413 PASS
DT-414 PASS
DT-415 PASS
DT-416 PASS
DT-417 PASS
DT-418 PASS
DT-419 PASS

Task1 service artifact registered and loadable

Task1 lateness artifact registered and loadable

Task1 canonical artifacts unchanged

Task2A artifact bundle finalized

Task2A final strategy represented honestly

all required preprocessing state saved/referenced

feature schemas preserved

model versions recorded

artifact hashes recorded

paths package-relative

serialization round-trip PASS

fresh-process deserialization PASS

Task1 service parity PASS

Task1 late parity PASS

Task2A total parity PASS

Task2A chilled parity PASS

ID/order exact parity PASS

official CSV hashes unchanged

Task2B unchanged

security/path guards PASS

targeted tests PASS

full safe suite PASS

pip check PASS

git diff check PASS

fresh independent Phase32 review PASS

Then:

PHASE 32 STATUS: PASS
MODEL ARTIFACT BUNDLE: FINAL
FROZEN PREDICTIONS: REPRODUCED
AUTHORIZED NEXT ACTION: RETURN TO PHASE31 FINAL CLOSURE
READY FOR PHASE33: NO

==================================================
GIT WORKFLOW
==================================================

Recommended branch:

git checkout main
git pull
git checkout -b feature/phase-32-model-artifacts

If Phase31 work is not merged and Phase32 depends on it:
branch from the validated Phase31 working branch/commit according to team
workflow, without losing work.

Recommended commits:

feat(artifacts): add final model artifact registry and integrity checks
feat(task2a): serialize final forecast artifact bundle
feat(artifacts): save required preprocessing and runtime metadata
test(artifacts): add serialization deserialization and parity guards
docs(artifacts): document final saved-model loading contract

Before commit:

git status
git diff
git diff --check

Never stage:

data/raw/**
data/interim/**
reports/private/**

Do not stage temporary artifact candidates.

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-412 READY
DT-413 READY
DT-414 READY
DT-415 READY
DT-416 READY
DT-417 READY
DT-418 READY
DT-419 READY

Task1 artifacts unchanged

Task2A artifacts complete

preprocessor state complete

registry complete

versions complete

serialization PASS

fresh-process deserialization PASS

parity code ready

private parity human-local only

no official output writes

Phase31 loader bridge ready

no Phase33 implementation

==================================================
RETURN ONLY
==================================================

PHASE:
32 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-412 READY / FAIL
DT-413 READY / FAIL
DT-414 READY / FAIL
DT-415 READY / FAIL
DT-416 READY / FAIL
DT-417 READY / FAIL
DT-418 READY / FAIL
DT-419 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TASK1 SERVICE ARTIFACT:
PASS / FAIL

TASK1 LATE ARTIFACT:
PASS / FAIL

TASK2A ARTIFACT BUNDLE:
PASS / FAIL

PREPROCESSING OBJECTS:
PASS / NOT_REQUIRED / FAIL

MODEL VERSIONS:
PASS / FAIL

SERIALIZATION TEST:
PASS / FAIL

FRESH-PROCESS DESERIALIZATION:
PASS / FAIL

SYNTHETIC ROUNDTRIP PARITY:
PASS / FAIL

ARTIFACT REGISTRY:
PASS / FAIL

CHECKSUM VALIDATION:
PASS / FAIL

PACKAGE-RELATIVE PATHS:
PASS / FAIL

PHASE31 LOADER BRIDGE:
PASS / FAIL

TASK1 CANONICAL ARTIFACTS CHANGED:
MUST BE NO

OFFICIAL TASK1 CSV CHANGED:
MUST BE NO

OFFICIAL TASK2A CSV CHANGED:
MUST BE NO

OFFICIAL TASK2B CSV CHANGED:
MUST BE NO

PRIVATE REAL DATA ACCESSED:
NO

TARGETED TESTS:
...

FULL SAFE SUITE:
...

PIP CHECK:
PASS / FAIL

GIT DIFF CHECK:
PASS / FAIL

HUMAN LOCAL ACTION REQUIRED:
YES

Print exact:

1. artifact finalization command
2. safe artifact validation command
3. private Task1/Task2A parity command

PHASE32 AGENT STATUS:
AWAITING LOCAL FINALIZATION/PARITY

READY FOR FRESH PHASE32 INDEPENDENT REVIEW:
NO

READY FOR PHASE33:
NO

Then STOP.

Do not start Phase33.

```

---

# 129. Fresh independent Phase 32 review prompt

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon PHASE 32.

PHASE:
Model Artifact Management

TASK RANGE:
DT-412 through DT-419

REVIEW MODE:
FRESH SESSION
READ-ONLY
ARTIFACT-INTEGRITY FIRST

Do NOT implement Phase33.
Do NOT retrain/retune models.
Do NOT modify canonical artifacts.
Do NOT inspect private row-level competition data.
Use sanitized human-local parity evidence for private runs.

==================================================
SOURCE OF TRUTH
==================================================

Read:

1. Official Challenge Booklet
   - Model file(s)
   - Final notebook
   - rules/restrictions

2. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase32

3. PHASE_10_COMPETITION_CONTRACT.md

4. PHASE_17_COMPETITION_CONTRACT.md

5. PHASE_31_COMPETITION_CONTRACT.md

6. PHASE_32_COMPETITION_CONTRACT.md

Inspect:

configs/model_artifacts.yaml
models/artifact_registry.json
models/README.md

models/task1_service/**
models/task1_late/**
models/task2a/**

src/common/artifact_io.py
src/common/artifact_registry.py
src/common/versioning.py
or actual equivalents

scripts/finalize_model_artifacts.py
scripts/validate_model_artifacts.py
scripts/run_model_artifact_parity.py

docs/model_artifacts.md

tests/test_artifact_registry.py
tests/test_task1_artifact_roundtrip.py
tests/test_task2a_artifact_roundtrip.py
tests/test_preprocessing_artifacts.py
tests/test_artifact_clean_process_load.py
tests/test_artifact_prediction_parity.py
tests/test_artifact_security.py
tests/test_phase31_artifact_bridge.py

Inspect final safe configs/metadata.

Do not open private parity row files.

==================================================
HUMAN SANITIZED LOCAL EVIDENCE
==================================================

TASK1 CANONICAL PRE/POST HASH:
<UNCHANGED/FAIL>

TASK1 SERVICE ARTIFACT:
<PASS/FAIL>

TASK1 LATE ARTIFACT:
<PASS/FAIL>

TASK2A ARTIFACT FINALIZATION:
<PASS/FAIL>

PREPROCESSING STATE:
<PASS/NOT_REQUIRED/FAIL>

ARTIFACT CHECKSUMS:
<PASS/FAIL>

FRESH-PROCESS LOAD:
<PASS/FAIL>

TASK1 SERVICE PARITY:
<PASS/FAIL>

TASK1 LATE PARITY:
<PASS/FAIL>

TASK2A TOTAL PARITY:
<PASS/FAIL>

TASK2A CHILLED PARITY:
<PASS/FAIL>

TASK1 ID/ORDER PARITY:
<PASS/FAIL>

TASK2A ID/ORDER PARITY:
<PASS/FAIL>

OFFICIAL TASK1 CSV HASH:
<UNCHANGED/FAIL>

OFFICIAL TASK2A CSV HASH:
<UNCHANGED/FAIL>

OFFICIAL TASK2B CSV HASH:
<UNCHANGED/FAIL>

No real IDs should be supplied.

==================================================
AUDIT DT-412
==================================================

Confirm Task1 service model is a canonical saved final artifact.

Because Phase10 already froze it:

Phase32 should register/validate it, not mutate it.

Check:

family/config parity

feature schema

serializer

hash

loader

postprocessing

No overwrite.

==================================================
AUDIT DT-413
==================================================

Confirm Task1 lateness bundle contains all required state.

Check:

classifier family/config

feature schema

positive-class mapping

class ordering if relevant

calibration mode

calibration artifact if required

probability output semantics

hash/loadability

No overwrite.

==================================================
AUDIT DT-414
==================================================

Confirm Task2A artifact representation matches ACTUAL final strategy.

Possible valid forms:

trained model

baseline strategy artifact

ensemble bundle

multi-horizon bundle

derived target strategy

Do not accept a fake single model if actual pipeline needs multiple
components.

Check:

all components

target/horizon mapping

weights

postprocessing

feature schema

fresh loader

==================================================
AUDIT DT-415
==================================================

Determine whether preprocessing state is actually required.

Valid statuses:

external_serialized

embedded

deterministic_code

not_required

If external learned state is required:
artifact must exist and be registered.

Do not require a fake preprocessor when not necessary.

Do not accept missing learned state.

==================================================
AUDIT DT-416
==================================================

Require:

Python version

relevant model runtime/library versions

serializer/runtime versions

artifact schema/format versions

final config IDs

feature schema refs

No absolute machine path.

No username.

No private data.

==================================================
AUDIT DT-417
==================================================

Serialization must be genuinely tested.

Task1:
must not overwrite frozen canonical artifacts.

Temporary roundtrip / Phase10 evidence + current validation acceptable,
depending on serializer.

Task2A:
candidate save -> reload -> parity before canonical promotion.

Check atomic finalization/overwrite protection.

==================================================
AUDIT DT-418
==================================================

Require a true fresh-process deserialization test.

Fresh process:

loads registry

verifies checksum first

loads service

loads late/calibrator

loads Task2A

loads external preprocessing if required

runs synthetic smoke inference

does NOT train

does NOT depend on notebook state

==================================================
AUDIT DT-419
==================================================

Require:

synthetic roundtrip parity

AND

human-local final-output parity.

Task1:
saved artifacts reproduce frozen submission_task1 predictions.

Task2A:
saved artifacts reproduce frozen submission_task2a predictions.

Check:

IDs exact

row order exact

row count exact

postprocessing exact

numeric tolerance explicit/tight

No official CSV overwritten.

==================================================
OFFICIAL REQUIREMENT AUDIT
==================================================

Confirm Phase32 makes it feasible to satisfy:

"Model file(s). Save your final model files alongside the notebook."

And Phase31:

final cell loads saved models for Task1 and Task2A.

Check:

package-relative paths

registry

no workstation-specific absolute path

loader bridge importable from fresh process.

==================================================
SECURITY AUDIT
==================================================

Verify:

hash before deserialize

arbitrary path rejected

path traversal rejected

path outside model root rejected

network artifact rejected

unregistered pickle/joblib rejected

unknown serializer rejected

corrupt artifact fails

no generic unsafe load-anything API

Do not overstate this as production security.

==================================================
TASK1 FROZEN INTEGRITY
==================================================

Phase32 must not mutate already-frozen Phase10 Task1 artifacts.

Use sanitized pre/post hash evidence.

If changed:
FAIL.

Do not accept:
"equivalent predictions" as permission to mutate frozen bytes.

==================================================
OFFICIAL OUTPUT INTEGRITY
==================================================

Require all unchanged:

submission_task1.csv

submission_task2a.csv

submission_task2b.csv

Phase32 is artifact management, not submission regeneration.

==================================================
TASK2A ARTIFACT HONESTY
==================================================

If baseline champion:

artifact should honestly be baseline strategy/state.

If ensemble:

all components/weights.

If separate models:

all required targets/components.

If preprocessing deterministic:
no fake binary object.

Reject architectural misrepresentation.

==================================================
VERSION COMPATIBILITY AUDIT
==================================================

Check registry records relevant versions.

Version validation should:

PASS exact

WARN reasonable nonbreaking deviation where policy allows

FAIL major/incompatible or load/parity failure

Do not silently resave under new version to make warning disappear.

==================================================
REGISTRY AUDIT
==================================================

Require:

schema version

relative paths

all required files

hashes

sizes if recorded

artifact roles

task/target

family/strategy

config IDs

feature schema refs

preprocessor mode

runtime versions

load entrypoint

No private rows.

==================================================
PRIVATE REPORT AUDIT
==================================================

Private reports may exist under:

reports/private/phase32_model_artifacts/

They must remain ignored/untracked.

Do not require row-level private details in review.

Sanitized aggregate PASS/FAIL evidence is enough.

==================================================
PHASE31 BRIDGE AUDIT
==================================================

Confirm a fresh process can import/use the same loader interface that the
Phase31 final cell will call.

Phase32 PASS should authorize:

RETURN TO PHASE31 FINAL CLOSURE

It should NOT directly authorize Phase33.

Phase31 must still complete:

DT-405
DT-409
DT-411

and final independent review.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_artifact_registry.py \
  tests/test_task1_artifact_roundtrip.py \
  tests/test_task2a_artifact_roundtrip.py \
  tests/test_preprocessing_artifacts.py \
  tests/test_artifact_clean_process_load.py \
  tests/test_artifact_prediction_parity.py \
  tests/test_artifact_security.py \
  tests/test_phase31_artifact_bridge.py

Then relevant Phase10/17 inference regressions.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run private real-data parity.

==================================================
RETURN FORMAT
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

OFFICIAL MODEL-FILE DELIVERABLE:
PASS / FAIL

TASK1 SERVICE ARTIFACT:
PASS / FAIL

TASK1 LATE ARTIFACT:
PASS / FAIL

TASK2A ARTIFACT BUNDLE:
PASS / FAIL

PREPROCESSING STATE:
PASS / NOT_REQUIRED / FAIL

MODEL VERSION RECORD:
PASS / FAIL

ARTIFACT REGISTRY:
PASS / FAIL

CHECKSUM-INTEGRITY GATE:
PASS / FAIL

SERIALIZATION:
PASS / FAIL

FRESH-PROCESS DESERIALIZATION:
PASS / FAIL

SYNTHETIC ROUNDTRIP:
PASS / FAIL

TASK1 SERVICE FINAL PARITY:
PASS / FAIL

TASK1 LATE FINAL PARITY:
PASS / FAIL

TASK2A TOTAL FINAL PARITY:
PASS / FAIL

TASK2A CHILLED FINAL PARITY:
PASS / FAIL

TASK1 ID/ORDER:
PASS / FAIL

TASK2A ID/ORDER:
PASS / FAIL

TASK1 CANONICAL ARTIFACTS:
UNCHANGED / CHANGED

OFFICIAL TASK1 CSV:
UNCHANGED / CHANGED

OFFICIAL TASK2A CSV:
UNCHANGED / CHANGED

OFFICIAL TASK2B CSV:
UNCHANGED / CHANGED

PACKAGE-RELATIVE PATHS:
PASS / FAIL

PHASE31 LOADER BRIDGE:
PASS / FAIL

ARTIFACT SECURITY:
PASS / FAIL

PRIVACY:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

PIP CHECK:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
None / exact blockers

NON-BLOCKING IMPROVEMENTS:
...

DT-412: PASS/FAIL
DT-413: PASS/FAIL
DT-414: PASS/FAIL
DT-415: PASS/FAIL
DT-416: PASS/FAIL
DT-417: PASS/FAIL
DT-418: PASS/FAIL
DT-419: PASS/FAIL

PHASE 32 INDEPENDENT REVIEW:
PASS / FAIL

MODEL ARTIFACT BUNDLE:
FINAL / INCOMPLETE

FROZEN PREDICTIONS:
REPRODUCED / NOT REPRODUCED

AUTHORIZED NEXT ACTION:
RETURN TO PHASE31 FINAL CLOSURE / BLOCKED

READY FOR PHASE33:
NO

If PASS:

PHASE 32 INDEPENDENT REVIEW: PASS
MODEL ARTIFACT BUNDLE: FINAL
FROZEN PREDICTIONS: REPRODUCED
TASK1 CANONICAL ARTIFACTS: UNCHANGED
OFFICIAL SUBMISSIONS: UNCHANGED
BLOCKERS: None
AUTHORIZED NEXT ACTION: RETURN TO PHASE31 FINAL CLOSURE
READY FOR PHASE33: NO

Then STOP.

Do not start Phase33.

```

---

# 130. Completion record

```markdown
# Phase 32 Completion Record

## Tasks

- [ ] DT-412
- [ ] DT-413
- [ ] DT-414
- [ ] DT-415
- [ ] DT-416
- [ ] DT-417
- [ ] DT-418
- [ ] DT-419

## Task1

- [ ] service artifact registered
- [ ] service artifact unchanged
- [ ] service load PASS
- [ ] late artifact registered
- [ ] late artifact unchanged
- [ ] positive class PASS
- [ ] calibration PASS

## Task2A

- [ ] final strategy resolved
- [ ] artifact kind correct
- [ ] all components saved
- [ ] manifest complete
- [ ] postprocessing preserved
- [ ] clean loader PASS

## Preprocessing / versions

- [ ] preprocessor mode complete
- [ ] external objects saved if required
- [ ] feature schema complete
- [ ] Python version
- [ ] model library versions
- [ ] serializer versions

## Integrity

- [ ] registry PASS
- [ ] relative paths
- [ ] SHA256 PASS
- [ ] checksum-before-load
- [ ] path traversal blocked
- [ ] arbitrary unregistered pickle blocked

## Round-trip

- [ ] serialization PASS
- [ ] fresh-process deserialization PASS
- [ ] synthetic parity PASS
- [ ] Task1 private parity PASS
- [ ] Task2A private parity PASS
- [ ] ID/order parity PASS

## Frozen outputs

- Task1 canonical artifacts changed: NO
- submission_task1.csv changed: NO
- submission_task2a.csv changed: NO
- submission_task2b.csv changed: NO

## Phase31 bridge

- [ ] canonical loaders available
- [ ] final-cell interface available
- [ ] return-to-Phase31 handoff ready

## Review

- independent Phase32 review: PASS / FAIL

## Verdict

PHASE 32 STATUS: PASS / FAIL
MODEL ARTIFACT BUNDLE: FINAL / INCOMPLETE
FROZEN PREDICTIONS: REPRODUCED / NOT REPRODUCED
AUTHORIZED NEXT ACTION: RETURN TO PHASE31 FINAL CLOSURE / BLOCKED
READY FOR PHASE33: NO
```

---

# 131. Final checklist

Before returning to Phase 31:

- [ ] Exact DT-412–DT-419 coverage.
- [ ] Task1 service artifact unchanged.
- [ ] Task1 late artifact unchanged.
- [ ] Task1 positive-class/calibration complete.
- [ ] Task2A final strategy honestly represented.
- [ ] All required Task2A components saved.
- [ ] Preprocessing state complete.
- [ ] Feature schemas complete.
- [ ] Model/runtime versions complete.
- [ ] Artifact registry complete.
- [ ] Relative paths only.
- [ ] SHA256 verified before deserialize.
- [ ] Serialization PASS.
- [ ] Fresh-process deserialization PASS.
- [ ] Synthetic round-trip parity PASS.
- [ ] Task1 loaded-artifact final parity PASS.
- [ ] Task2A loaded-artifact final parity PASS.
- [ ] Task1 IDs/order exact.
- [ ] Task2A IDs/order exact.
- [ ] Official Task1 CSV unchanged.
- [ ] Official Task2A CSV unchanged.
- [ ] Official Task2B CSV unchanged.
- [ ] Phase31 loader bridge PASS.
- [ ] Targeted tests PASS.
- [ ] Full safe suite PASS.
- [ ] `pip check` PASS.
- [ ] `git diff --check` PASS.
- [ ] Independent Phase32 review PASS.

Only then:

```text
PHASE 32 STATUS: PASS
MODEL ARTIFACT BUNDLE: FINAL
FROZEN PREDICTIONS: REPRODUCED
AUTHORIZED NEXT ACTION: RETURN TO PHASE31 FINAL CLOSURE
READY FOR PHASE33: NO
```
