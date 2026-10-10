# PHASE 25 — Task 1 Explainability

> **Filename:** `PHASE_25_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 25 — Explainability  
> **Task range:** **DT-343 → DT-349**  
> **Task count:** **7**  
> **Master dependency:** Final/near-final Task 1 models from Phases 9–10  
> **Default phase priority:** **P1**  
> **Master task priority:** **P2** for each Phase 25 work item  
> **Phase gate:** Selected model explanations are accurate, useful and do not make causal claims unsupported by the data.  
> **Execution mode:** Read-only post-hoc explanation of the frozen final Task 1 models.  
> **Do not retrain, retune, reselect or modify the frozen Task 1 models in this phase.**

---

# 1. Phase 25 purpose

Phase 25 explains **why the frozen Task 1 models produce the predictions they produce**.

Task 1 has two final outputs:

```text
pred_service_min
```

and:

```text
pred_late_prob
```

The official challenge defines them as:

```text
pred_service_min
=
predicted outlet handling/service time, in minutes
```

and:

```text
pred_late_prob
=
probability that arrival occurs after the outlet delivery window closes
```

Phase 25 must create explanations for both frozen models without changing their predictions.

The phase must answer:

```text
Which features does the final service model rely on most?

Which features does the final late-risk model rely on most?

What does SHAP say globally about model behavior?

For one specific service prediction, what pushed the model up/down?

For one high-risk lateness prediction, what pushed the base risk score
up/down?

Which patterns can be translated into useful business language?

Which statements would overreach into unsupported causal claims?
```

This is **model explainability**, not causal inference.

---

# 2. Finalized Phase 25 master inventory

The finalized WayLoom task inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-343** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate service-model feature importance |
| [ ] | **DT-344** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate lateness-model feature importance |
| [ ] | **DT-345** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate SHAP global explanation |
| [ ] | **DT-346** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate local service prediction explanation |
| [ ] | **DT-347** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate local late-risk explanation |
| [ ] | **DT-348** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Identify meaningful business drivers |
| [ ] | **DT-349** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Avoid unsupported causal claims |

**Expected Phase 25 tasks:** 7  
**Missing tasks allowed:** 0  
**Phase complete:** [ ]  
**READY FOR PHASE 26:** NO

---

# 3. Official-source requirements relevant to Phase 25

The official booklet does **not** mandate SHAP specifically.

SHAP is a **WayLoom engineering requirement from the finalized master inventory**.

The official Task 1 source does require teams to:

```text
choose and justify features
```

and states that the challenge:

```text
does not prescribe a feature set
```

The official deliverables also require:

```text
architecture diagrams

a preprocessing document

saved final models

a final notebook retaining label/preprocessing/training/evaluation work

a 3–5 minute demo explaining model architecture, preprocessing,
label construction and challenges encountered
```

The judging criteria include:

```text
Model and architecture implementation: 25%

Creativity of the solution: 10%

Demo video: 10%
```

Phase 25 therefore supports the team's ability to **justify the frozen model and communicate it clearly**, but no claim should imply that the organizer required SHAP.

---

# 4. Official Task 1 prediction-time boundary

The booklet states that prediction-time information includes planned:

```text
departure
travel duration
arrival
```

while actual journey/handling information is available only in historical training route records.

Therefore Phase 25 must preserve the Phase 06/10 leakage boundary.

Forbidden current-row direct prediction features include:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

and direct current target fields.

Chronology-safe historical features are allowed only if:

- already included in the frozen final model;
- already passed Phase 06 leakage controls;
- use only valid past information under the frozen transformation.

If a forbidden actual/current-outcome field appears in a feature-importance or SHAP artifact:

```text
STOP
```

This is not an explainability issue to hide.

It is a Task 1 leakage blocker requiring upstream review.

---

# 5. Competition restrictions remain active

The official competition restrictions still apply.

Do not use Phase 25 to:

```text
send competition rows to a proprietary external API

upload the dataset to an external explainer service

use a prohibited pre-trained modelling service

introduce a new externally trained prediction model

share competition data or derivatives publicly
```

All explainability should run locally.

A SHAP/plotting Python library running locally is an engineering library, not a pre-trained prediction model.

---

# 6. Explainability must be post-hoc and read-only

Phase 25 is downstream of a frozen Task 1 model-selection/inference process.

It must **not**:

- retrain a model because an importance plot looks unattractive;
- remove a feature because SHAP says it is important;
- add a feature because a local example is confusing;
- change hyperparameters;
- change class weighting;
- change calibration;
- change final feature ordering;
- change the service post-processing rule;
- edit `submission_task1.csv`;
- create a new "explainable champion."

If explainability reveals a genuine bug/leakage problem:

```text
STOP AND REOPEN THE RELEVANT UPSTREAM PHASE
```

Do not silently repair model semantics inside Phase 25.

---

# 7. Frozen Task 1 artifacts

At minimum, Phase 25 must treat these as frozen:

```text
configs/task1_final_models.yaml

models/task1_service/**

models/task1_late/**

outputs/submission_task1.csv
```

The model bundles should already contain metadata such as:

```text
model family

config ID

feature schema

prediction column

seed
```

For lateness, the saved metadata should also preserve:

```text
positive_class = 1

calibration = raw | sigmoid | isotonic | other frozen approved method
```

For service, metadata should preserve the frozen final:

```text
post-processing policy
```

if any.

---

# 8. Frozen-artifact hash guard

Before the real explainability run, calculate SHA256 values for:

```text
configs/task1_final_models.yaml

service model bundle files

late model bundle files

feature schema files

calibration artifact if present

outputs/submission_task1.csv
```

After Phase 25 generation:

recompute the same hashes.

Require:

```text
before == after
```

for every frozen artifact.

If any differs:

```text
PHASE 25 FAIL
```

Explainability must be demonstrably read-only.

---

# 9. Recommended Phase 25 files

Create/update:

```text
src/task1/explainability.py
src/task1/shap_adapter.py
src/task1/explanation_reporting.py
src/task1/causal_language.py

scripts/build_task1_explainability.py
scripts/validate_task1_explainability.py

configs/task1_explainability.yaml

docs/task1_explainability.md
docs/task1_explainability_spec.md

tests/test_task1_explainability_importance.py
tests/test_task1_shap.py
tests/test_task1_local_explanations.py
tests/test_task1_causal_language.py
tests/test_task1_explainability_contract.py
```

Do not create Phase 26 hero-feature implementation.

---

# 10. Recommended private output directory

Real model-derived explanation data should default to:

```text
reports/private/phase25_task1_explainability/
```

Recommended files:

```text
run_manifest.json

service_feature_importance.csv
late_feature_importance.csv

service_shap_global.csv
late_shap_global.csv

service_local_explanation.json
late_local_explanation.json

business_drivers.json

shap_reconstruction_audit.json
feature_leakage_audit.json
causal_language_audit.json
frozen_artifact_hash_audit.json

phase25_explainability_report.md

figures/
├── service_feature_importance.png
├── late_feature_importance.png
├── service_shap_bar.png
├── service_shap_distribution.png
├── late_shap_bar.png
├── late_shap_distribution.png
├── service_local_waterfall.png
└── late_local_waterfall.png
```

Detailed row-level SHAP matrices, if temporarily required, must remain private.

---

# 11. Competition-facing explanation summary

Create:

```text
docs/task1_explainability.md
```

This should be:

- concise;
- model-specific;
- source-grounded;
- free of row IDs;
- free of unsupported causal statements;
- suitable for later architecture/demo/notebook use.

If the repository is public or accessible outside the authorized competition context:

```text
DO NOT COMMIT REAL-DATA-DERIVED EXPLANATION RESULTS
```

Keep them local for the authorized competition submission package.

The tracked source can contain the writer/template/spec.

---

# 12. Recommended explainability configuration

Create:

```text
configs/task1_explainability.yaml
```

Recommended structure:

```yaml
version: 1

frozen:
  final_model_config: configs/task1_final_models.yaml
  service_model_dir: models/task1_service
  late_model_dir: models/task1_late
  task1_submission: outputs/submission_task1.csv
  require_hash_stability: true

population:
  source: task1_test_features
  max_rows: 2000
  min_rows_if_available: 200
  random_seed: 42
  deterministic_sampling: true

importance:
  top_n: 20
  prefer_native: true
  fallback: mean_abs_shap

shap:
  strategy: auto_verified
  reconstruction_tolerance: 1.0e-6
  require_output_space_metadata: true
  require_positive_class: 1

local:
  service_selector: median_prediction
  late_selector: highest_predicted_probability
  anonymize_identifiers: true
  top_positive: 8
  top_negative: 8

business_drivers:
  top_n_per_model: 10
  require_feature_registry_match: true
  require_leakage_safe: true
  report_method_disagreement: true

language:
  require_noncausal_disclaimer: true
  run_causal_phrase_audit: true

privacy:
  private_report_dir: reports/private/phase25_task1_explainability
  expose_delivery_ids_in_docs: false
```

These sampling/plotting choices are WayLoom engineering decisions, not official rules.

---

# 13. Explanation population

Recommended default explanation population:

```text
the exact Task 1 test feature matrix used by the frozen final inference pipeline
```

Why:

- it represents the final submission/deployment context;
- no Task 1 test labels are required;
- it explains what the final models are doing on the actual prediction population.

Do not rebuild a special explainability matrix with different semantics.

---

# 14. Deterministic SHAP sampling

For expensive SHAP computation:

```text
max_rows = 2000
```

Use all rows when smaller.

When larger:

select rows deterministically.

Recommended:

```text
stable hash / seeded deterministic sample
```

with:

```text
random_seed = 42
```

Do not use an unseeded sample.

Record:

```text
population row count
sample row count
selection method
seed
```

in the run manifest.

Do not expose selected `delivery_id` values in public-facing outputs.

---

# 15. Feature-schema parity

Before explanation, require exact parity with the frozen model:

```text
feature names

feature ordering

categorical definitions

numeric definitions

missing policy

encoding/imputation/scaling state

historical-feature state

optional feature switches
```

Do not call the model with a DataFrame whose columns have merely been sorted alphabetically.

Use the saved feature schema.

---

# 16. Feature registry integration

Join explanation results to the Phase 06 feature metadata/registry.

Useful fields include:

```text
feature_name

semantic group

source columns

feature type

prediction-time availability

lineage

historical/derived/static indicator
```

If a final feature cannot be found in the registry:

```text
STOP OR REPORT A CONTRACT MISMATCH
```

Do not invent a human interpretation for an unknown feature.

---

# 17. DT-343 — Generate service-model feature importance

## Objective

Produce a ranked global importance table for the **exact saved final service model**.

## Preferred method hierarchy

1. valid model-native importance;
2. otherwise mean absolute SHAP as explicitly labelled fallback.

## Output

Recommended:

```text
service_feature_importance.csv
```

Columns:

```text
feature_name
importance
importance_type
rank
semantic_group
feature_registry_status
```

Optional:

```text
source_columns
```

Do not include row IDs.

---

# 18. Service importance — model-family handling

Do not assume the final model family.

Read:

```text
models/task1_service/metadata.json
```

or equivalent frozen metadata.

Recommended native importance behavior:

## CatBoost

Use a stable documented native importance such as:

```text
PredictionValuesChange
```

and record the exact type.

## LightGBM

Prefer:

```text
gain
```

over split-count when the saved model API supports it.

## XGBoost

Prefer gain-based importance with careful feature-name mapping.

## sklearn tree

Use:

```text
feature_importances_
```

## Linear model

Use absolute coefficients only when preprocessing/scaling makes that interpretation defensible.

If not:

use SHAP-based fallback.

---

# 19. Native importance limitations

Native importance is:

```text
model-specific
directionless in many implementations
not a causal measure
not necessarily comparable across model families
```

Do not:

- interpret 30% native importance as "30% of service time";
- infer sign from a non-signed importance measure;
- compare CatBoost and LightGBM importance values as if the scale is identical.

The report must state the actual method.

---

# 20. DT-344 — Generate lateness-model feature importance

Generate the corresponding importance for the exact frozen **base late classifier**.

If the final lateness pipeline includes calibration:

```text
base classifier
→ calibration
→ final pred_late_prob
```

Feature importance belongs to the base classifier.

Do not present the calibrator as a feature-importance model.

The positive class is:

```text
late_flag = 1
```

meaning:

```text
arrival after window close
```

Verify class ordering before any explanation.

---

# 21. Lateness importance output

Recommended:

```text
late_feature_importance.csv
```

Columns:

```text
feature_name
importance
importance_type
rank
semantic_group
positive_class
feature_registry_status
```

Require:

```text
positive_class == 1
```

in metadata/audit.

---

# 22. DT-345 — Generate SHAP global explanation

Generate global SHAP for:

```text
service model

late base classifier
```

even though the master inventory lists one SHAP task.

This fulfills the phase goal for both Task 1 outputs.

Recommended aggregate output:

```text
feature_name
mean_abs_shap
mean_shap
rank
sample_count
semantic_group
output_space
```

---

# 23. SHAP is local attribution, not causal proof

A SHAP value answers approximately:

> Given this trained model and the explainer's reference/background assumptions, how did this feature contribute to the model output for this observation?

It does **not** prove:

```text
the feature caused the real-world outcome
```

Global mean absolute SHAP answers:

```text
how strongly the model relied on the feature across the explained sample
```

It does not by itself answer:

```text
whether higher feature values increase or decrease outcomes
```

---

# 24. Model-native SHAP adapter

Prefer verified native contribution APIs when they represent SHAP values faithfully.

Benefits:

- lower runtime;
- better categorical compatibility;
- exact frozen-model behavior;
- less need to wrap preprocessing incorrectly.

Implement a common adapter contract:

```python
compute_shap_values(
    model,
    X,
    model_metadata,
    feature_schema,
) -> ShapResult
```

`ShapResult` should include:

```text
values
expected_values
feature_names
output_space
positive_class if applicable
method
```

---

# 25. CatBoost SHAP contract

If service/late model is CatBoost:

use:

```text
get_feature_importance(..., type="ShapValues")
```

with the exact feature layout and categorical handling required by the frozen model.

Typical CatBoost SHAP output includes:

```text
one contribution per feature
+
expected/base value
```

For regression:

reconstruct:

```text
raw service prediction
```

For binary classification:

reconstruct:

```text
RawFormulaVal / margin
```

unless the frozen API explicitly returns another verified space.

Record the output space.

---

# 26. LightGBM SHAP contract

If selected final model is LightGBM:

a verified local contribution path may use:

```text
pred_contrib=True
```

or a tested SHAP TreeExplainer.

Require:

```text
sum contributions
```

plus the expected/base term to reconstruct the correct raw output.

For binary classification:

do not assume probability-space contributions.

Record:

```text
raw margin/log-odds
```

when appropriate.

---

# 27. XGBoost SHAP contract

If selected final model is XGBoost:

a verified local path may use:

```text
pred_contribs=True
```

through the exact final booster/input representation.

Require feature-name parity.

Require reconstruction.

Record output space.

---

# 28. Other final model families

If the selected model is not covered by a native SHAP path:

use a verified local SHAP library explainer appropriate to the model.

Examples:

```text
TreeExplainer
LinearExplainer
shap.Explainer
```

Do not use remote services.

Do not silently choose:

```text
an approximate explanation that cannot be reconstructed
```

If no trustworthy explanation can be produced:

```text
STOP
```

---

# 29. SHAP output-shape normalization

Different libraries/versions may return:

```text
[n_rows, n_features]

[n_rows, n_features + 1]

list per class

[n_rows, n_classes, n_features]

Explanation object
```

Implement one tested normalization layer.

For binary classification:

explicitly select the positive class corresponding to:

```text
late_flag = 1
```

Do not depend on assumed array index without checking model class ordering.

---

# 30. Service SHAP reconstruction

For every explained service row:

```text
expected_value
+
sum(shap_values)
≈
raw_model_prediction
```

Use an engineering tolerance appropriate to model/library precision.

Recommended initial:

```text
1e-6
```

but make it configurable.

If the final service model applies frozen post-processing:

```text
raw model output
→ frozen postprocessing
→ pred_service_min
```

the explanation must show that bridge.

---

# 31. Service post-processing caution

Suppose a frozen service model uses:

```text
clip_to_zero
```

and raw output is negative.

Then SHAP explains the raw model output.

It does **not** directly decompose the clipped zero result.

The local explanation must say:

```text
SHAP reconstruction applies to raw model output.
The final submission applies the already-frozen post-processing rule.
```

Do not hide the distinction.

---

# 32. Lateness SHAP reconstruction

For every explained late-risk row:

```text
expected_value
+
sum(shap_values)
≈
base classifier output
```

in the adapter's documented output space.

Examples:

```text
raw margin
log-odds
probability
```

Then reproduce the frozen final inference path.

---

# 33. Calibration bridge

If lateness is calibrated:

```text
SHAP explains base classifier behavior
```

and then:

```text
base output
→ exact frozen calibration input
→ frozen calibrator
→ final pred_late_prob
```

The calibration input depends on the frozen Phase 09/10 implementation.

Do not assume it always consumes:

```text
raw margin
```

or:

```text
uncalibrated probability
```

Read the actual inference code.

---

# 34. Never misstate log-odds SHAP as probability points

If the lateness SHAP output space is:

```text
raw margin / log-odds
```

a feature contribution such as:

```text
+0.4
```

does **not** mean:

```text
+40 percentage points
```

The local explanation must label the scale correctly.

This is a hard quality check.

---

# 35. Global SHAP outputs

Generate for both models:

```text
service_shap_global.csv
late_shap_global.csv
```

Recommended columns:

```text
feature_name
mean_abs_shap
mean_shap
rank
sample_count
semantic_group
output_space
method
```

Keep detailed per-row SHAP private.

---

# 36. Global SHAP plots

Recommended local/competition-use plots:

```text
service SHAP importance bar

service SHAP distribution/beeswarm

late SHAP importance bar

late SHAP distribution/beeswarm
```

Plot titles must identify:

```text
Service model

Lateness base model
```

For lateness, subtitle/caption should identify the SHAP output space.

Avoid row IDs in plots.

---

# 37. DT-346 — Generate local service prediction explanation

Generate one deterministic representative service explanation.

Recommended selection:

```text
row whose final pred_service_min is closest to the median final service prediction
```

Tie-break:

```text
original template/test row position
```

This makes the example reproducible and avoids cherry-picking.

Use generic label:

```text
SERVICE_EXAMPLE_A
```

---

# 38. Local service explanation content

Private JSON should include:

```text
example_label

selection_rule

final_pred_service_min

raw_model_prediction

postprocessing_policy

expected_value

top_positive_contributors

top_negative_contributors

reconstructed_raw_prediction

reconstruction_error

model_family

shap_output_space
```

For each top feature:

```text
feature_name
display_name
feature_value
shap_value
semantic_group
```

Do not expose `delivery_id` in the competition-facing summary by default.

---

# 39. Local service wording

Use:

```text
"Feature X pushed the model's predicted service time upward relative to
the model baseline."
```

or:

```text
"Feature Y pulled the model prediction downward."
```

Do not write:

```text
"Feature X caused the outlet to take longer."
```

---

# 40. DT-347 — Generate local late-risk explanation

Generate one deterministic high-risk lateness example.

Recommended selection:

```text
highest final pred_late_prob
```

Tie-break:

```text
original template/test row position
```

Use generic label:

```text
LATE_EXAMPLE_A
```

This is deliberately a high-risk example.

Do not describe it as representative of all deliveries.

---

# 41. Local late-risk explanation content

Private JSON should include:

```text
example_label

selection_rule

final_pred_late_prob

base_raw_score

base_probability if applicable

calibration_method

calibration_input

expected_value

top_positive_risk_contributors

top_negative_risk_contributors

reconstructed_base_output

reconstruction_error

model_family

shap_output_space
```

When calibration is active:

include a clear note:

```text
SHAP explains the base classifier;
the calibrator transforms that base output into the submitted probability.
```

---

# 42. Local example privacy

Local explanations are more revealing than global plots.

Therefore detailed versions belong in:

```text
reports/private/phase25_task1_explainability/
```

For competition-facing narrative/figures:

- anonymize the identifier;
- show only the necessary top features;
- avoid displaying a full raw input row;
- avoid publishing externally.

---

# 43. DT-348 — Identify meaningful business drivers

Build:

```text
business_drivers.json
```

and a concise summary in:

```text
docs/task1_explainability.md
```

A "business driver" here means:

```text
a model feature or semantic feature group with meaningful predictive
influence in the frozen model
```

It does **not** mean:

```text
a proven causal driver of real-world outcomes
```

Define that distinction explicitly.

---

# 44. Potential semantic groups

Examples of legitimate semantic groups from the existing feature system may include:

```text
planned delivery timing/slack

planned early-wait context

planned travel/distance

order size

brand/outlet/district context

dock/access context

planning/reference service allowance

route position

planned route workload

vehicle/static context

calendar/festival context

chronology-safe historical behavior
```

These are examples only.

Do **not** predeclare them as actual top drivers.

The final list must come from model evidence.

---

# 45. Driver evidence standard

A feature/group may be called meaningful only when:

1. it is enabled in the frozen final feature schema;
2. its registry/lineage is valid;
3. it passes leakage checks;
4. it has material native importance or SHAP evidence;
5. it can be described in understandable business terms;
6. the language remains predictive/noncausal.

Recommended summary fields:

```text
driver
model
native_importance_rank
shap_rank
evidence_strength
business_interpretation
prediction_time_source
causal_caution
```

---

# 46. Importance/SHAP disagreement

If:

```text
native importance ranks feature very highly
```

but:

```text
mean absolute SHAP ranks it low
```

do not hide the inconsistency.

Report:

```text
method disagreement
```

Possible reasons include:

- importance definitions differ;
- correlated features;
- split-based bias;
- interaction effects;
- explanation population.

Do not choose whichever ranking tells the better story.

---

# 47. Directional interpretation

Do **not** use:

```text
mean_abs_shap
```

to claim direction.

It measures magnitude.

Directional claims require evidence from:

```text
signed SHAP distribution

dependence behavior

stable repeated local behavior
```

If the pattern is mixed:

say:

```text
context-dependent / non-monotonic
```

Do not simplify it into a false rule.

---

# 48. Correlated-feature warning

The explanation summary must note that:

```text
correlated or redundant features can share/reallocate attribution
```

Therefore:

```text
top SHAP feature ≠ isolated causal mechanism
```

and:

```text
low attribution ≠ operational irrelevance
```

This is especially important for:

- planned time variables;
- slack-derived variables;
- distance/travel measures;
- route workload features;
- historical aggregate features.

---

# 49. DT-349 — Avoid unsupported causal claims

Every Phase 25 narrative artifact must include a noncausal disclaimer.

Recommended:

> These explanations describe how the trained model uses observed features. They reflect model associations and attribution, not causal effects.

Avoid:

```text
X causes late arrival

X causes longer service

X guarantees delay

increasing X will reduce risk

changing X will improve service

X is the reason the order was late
```

Preferred:

```text
the model relies on X

X is associated with a higher/lower model output

X contributed positively/negatively to this prediction

the model learned a pattern involving X

X is an important predictive feature
```

---

# 50. Causal-language static audit

Implement:

```text
src/task1/causal_language.py
```

It should scan generated Markdown/text for high-risk phrases such as:

```text
causes
caused by
guarantees
will reduce
will increase
the reason for
results in
```

The word:

```text
driver
```

must not be banned globally.

Instead:

```text
business/model driver
```

should be explicitly defined as predictive, not causal.

Static scanning is not sufficient by itself.

Also require a manual review checklist.

---

# 51. Feature leakage audit for explanations

Create:

```text
feature_leakage_audit.json
```

Require:

```text
all explained features ⊆ final frozen feature schema

all explained features exist in registry

no forbidden actual field

no direct target

no current-outcome lineage

historical target features only if already chronology-safe/frozen
```

Any failure:

```text
PHASE 25 STOP
```

---

# 52. Run manifest

Create:

```text
run_manifest.json
```

Recommended contents:

```text
phase = 25

service model family
service config ID

late model family
late config ID

late positive class
calibration method

service postprocessing policy

service feature schema hash
late feature schema hash

service model hashes
late model hashes

submission_task1 SHA256

explanation population

population row count
SHAP sample size

sampling method
seed

service importance method
late importance method

service SHAP method/output space
late SHAP method/output space

library versions

git commit

created timestamp
```

No row IDs.

---

# 53. SHAP reconstruction audit

Create:

```text
shap_reconstruction_audit.json
```

Recommended fields:

```text
service:
  method
  output_space
  rows_checked
  max_abs_reconstruction_error
  tolerance
  pass

late:
  method
  output_space
  positive_class
  rows_checked
  max_abs_reconstruction_error
  tolerance
  base_output_pass
  calibration_bridge_pass
```

Do not claim PASS without numeric verification.

---

# 54. Service importance figure

Recommended:

```text
service_feature_importance.png
```

Requirements:

- top N only;
- descending rank;
- readable display names;
- method named in caption;
- no row-level information;
- no causal wording.

---

# 55. Lateness importance figure

Recommended:

```text
late_feature_importance.png
```

Caption should make clear:

```text
importance refers to the base classifier
```

when a calibrator exists.

Do not label calibrated probability itself as a feature-importance model.

---

# 56. Explainability summary document

Recommended sections for:

```text
docs/task1_explainability.md
```

```text
1. What is being explained
2. Service-time model — global drivers
3. Late-risk model — global drivers
4. Example service prediction
5. Example late-risk prediction
6. Business interpretation
7. Important limitations / noncausal disclaimer
```

Keep it concise.

Later phases can reuse it for:

- architecture diagrams;
- notebook narrative;
- demo script;
- evidence appendix.

---

# 57. Explainability quality rules

A useful explanation must be:

```text
faithful

reproducible

model-specific

feature-schema consistent

leakage-safe

privacy-safe

noncausal

understandable
```

An attractive SHAP chart is not enough.

---

# 58. Tests — feature importance

Create:

```text
tests/test_task1_explainability_importance.py
```

Synthetic cases should cover:

- valid tree native importance;
- feature-name mapping;
- sorted deterministic ranking;
- equal-importance tie handling;
- fallback to mean absolute SHAP;
- no fabricated native importance;
- unknown feature mapping failure;
- late positive-class metadata preserved.

---

# 59. Tests — SHAP

Create:

```text
tests/test_task1_shap.py
```

Cover:

- regression SHAP reconstruction;
- binary classification raw-margin reconstruction;
- positive-class array selection;
- expected/base value extraction;
- model-native adapter normalization;
- generic SHAP fallback where available;
- deterministic sample;
- unsupported model fails cleanly;
- output-space metadata required.

---

# 60. Tests — calibration bridge

Synthetic calibrated classifier:

```text
base classifier
+
calibrator
```

Test:

```text
SHAP reconstructs base output

frozen calibration path reproduces final probability

final probability ∈ [0,1]

SHAP output is not mislabeled as calibrated-probability points
```

Cover:

```text
raw/no calibration

sigmoid-style calibration

isotonic-style calibration
```

only to the extent supported by the project's frozen inference abstractions.

---

# 61. Tests — service post-processing bridge

Synthetic service model should cover:

```text
raw positive prediction

raw negative prediction if frozen postprocessing can clip

identity postprocessing
```

Require:

```text
SHAP reconstruction matches raw model output

postprocessing separately matches final service output
```

---

# 62. Tests — local explanations

Create:

```text
tests/test_task1_local_explanations.py
```

Service:

- deterministic median selector;
- tie by stable row order;
- correct top positive/negative features;
- no `delivery_id` in public summary.

Late:

- deterministic max-probability selector;
- correct positive class;
- calibration bridge;
- no probability-point misstatement.

---

# 63. Tests — causal language

Create:

```text
tests/test_task1_causal_language.py
```

Require flags for:

```text
"X causes lateness"

"X will reduce late risk"

"X guarantees faster service"

"X is the reason the delivery was late"
```

Allow properly qualified:

```text
"X is associated with higher model risk."

"X contributed positively to the model score."

"X is a model driver, not a proven causal driver."
```

---

# 64. Tests — contract/integrity

Create:

```text
tests/test_task1_explainability_contract.py
```

Cover:

- frozen artifact pre/post hashes identical;
- final feature schema exact;
- forbidden actual field hard-fails;
- direct target feature hard-fails;
- explained feature absent from registry hard-fails;
- business-driver features are all enabled/frozen;
- docs include noncausal disclaimer;
- no external API config;
- no Phase 26 outputs.

---

# 65. Categorical feature edge cases

Handle model-native categorical features safely.

Do not:

- convert categories to arbitrary integers solely for SHAP;
- refit an encoder;
- reorder category codes;
- expose high-cardinality private category lists in public docs.

Use the frozen model's own representation.

For figures:

display only the feature name unless category-level detail is genuinely required and privacy-safe.

---

# 66. Missing-value edge cases

Missing values must be processed exactly as during final inference.

Do not:

```text
fill missing values differently for explanation
```

If the model's explainer cannot handle the frozen missing-value representation:

```text
STOP OR USE A VERIFIED MODEL-COMPATIBLE EXPLAINER
```

Do not mutate inputs to make the plot work.

---

# 67. Constant/zero-importance features

A constant feature may have:

```text
zero native importance
zero SHAP
```

Keep it valid.

Do not drop it from the frozen model.

The explanation output may rank it low or omit it from top-N display.

---

# 68. Very confident late probabilities

For final probabilities close to:

```text
0
1
```

raw margins/log-odds may be large.

Do not clip the explanation solely for visual convenience.

Plots may cap axis display only if the underlying numerical value is preserved and the caption makes this clear.

---

# 69. Small explanation population

If the Task 1 test set has fewer than the configured minimum:

```text
use all rows
```

Do not duplicate rows to hit a sample target.

Record actual sample count.

---

# 70. SHAP runtime limits

If exact SHAP is too slow:

1. prefer model-native exact tree contributions;
2. reduce deterministic explanation sample size;
3. preserve a reasonable global sample;
4. record the sample size.

Do not switch to an unverified approximate explainer silently.

Do not change the model.

---

# 71. Determinism

Require:

```text
same model hashes

same sample-selection indices internally

same global importance ordering subject to deterministic tie policy

same local selected example labels

same aggregate SHAP values within tolerance
```

on repeated safe/synthetic runs.

Local real runs should also be reproducible under fixed software/config.

---

# 72. Privacy handling

Competition data and derivatives are confidential under the official terms.

Therefore:

- raw SHAP row matrices remain private;
- local detailed examples remain private by default;
- public repository must not contain real-data-derived figures/text unless explicitly authorized;
- competition submission package may include selected explainability artifacts as authorized deliverables/support;
- do not paste private explanation rows into external AI chats.

---

# 73. Recommended sanitized local console output

Target:

```text
WAYLOOM — PHASE 25 TASK 1 EXPLAINABILITY

FROZEN MODEL CONFIG                     : PASS
SERVICE MODEL RELOAD                    : PASS
LATENESS MODEL RELOAD                   : PASS
TASK1 SUBMISSION HASH                   : PASS

FEATURE SCHEMA PARITY                   : PASS
FEATURE LEAKAGE AUDIT                   : PASS

SERVICE FEATURE IMPORTANCE              : PASS
LATENESS FEATURE IMPORTANCE             : PASS

GLOBAL SHAP — SERVICE                   : PASS
GLOBAL SHAP — LATENESS                  : PASS

SERVICE SHAP RECONSTRUCTION             : PASS
LATENESS SHAP RECONSTRUCTION            : PASS

SERVICE POSTPROCESSING BRIDGE           : PASS
LATENESS CALIBRATION BRIDGE             : PASS

LOCAL SERVICE EXPLANATION               : PASS
LOCAL LATE-RISK EXPLANATION             : PASS

BUSINESS DRIVER SUMMARY                 : PASS
CAUSAL-LANGUAGE AUDIT                   : PASS

FROZEN MODEL HASHES UNCHANGED           : PASS
submission_task1.csv UNCHANGED          : PASS

PHASE 25                                : PASS
READY FOR PHASE 26                      : YES
```

No private row IDs.

---

# 74. Local build command

Recommended shape:

```bash
python scripts/build_task1_explainability.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --final-model-config configs/task1_final_models.yaml \
  --explainability-config configs/task1_explainability.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --submission outputs/submission_task1.csv \
  --report-dir reports/private/phase25_task1_explainability \
  --summary-output docs/task1_explainability.md
```

Use actual repository arguments if different.

Do not invent duplicate model paths outside the existing project convention.

---

# 75. Local validation command

Recommended shape:

```bash
python scripts/validate_task1_explainability.py \
  --config configs/task1_explainability.yaml \
  --final-model-config configs/task1_final_models.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --submission outputs/submission_task1.csv \
  --report-dir reports/private/phase25_task1_explainability \
  --summary docs/task1_explainability.md
```

---

# 76. STOP conditions

`READY FOR PHASE 26` remains **NO** if:

- Phase 09/10 final Task 1 config is not frozen;
- service model missing;
- late model missing;
- feature schema missing;
- model reload fails;
- `submission_task1.csv` missing;
- frozen artifact hash changes;
- explainability changes predictions;
- explanation uses a different feature pipeline;
- direct actual journey field appears;
- direct target/current outcome appears;
- explained feature has invalid lineage;
- final model positive class is ambiguous;
- native/fallback importance cannot map to feature names;
- SHAP reconstruction fails;
- service post-processing bridge fails;
- calibration bridge fails;
- calibrated probability is misrepresented as raw SHAP probability contribution;
- local example selection is nondeterministic;
- public-facing explanation contains row IDs;
- business driver lacks model evidence;
- mean absolute SHAP is incorrectly used to infer direction;
- causal statements remain;
- external proprietary API is required;
- competition data would leave the machine;
- Task 1 final model/config/submission changes;
- Task 2 final outputs change;
- Phase 26 is introduced early;
- tests fail;
- `pip check` fails;
- independent Phase 25 review fails.

---

# 77. Definition of Done

Phase 25 is complete only when:

- [ ] DT-343 PASS
- [ ] DT-344 PASS
- [ ] DT-345 PASS
- [ ] DT-346 PASS
- [ ] DT-347 PASS
- [ ] DT-348 PASS
- [ ] DT-349 PASS
- [ ] final service model identified from frozen metadata
- [ ] final late model identified from frozen metadata
- [ ] positive late class verified as `1`
- [ ] calibration method identified
- [ ] service post-processing method identified
- [ ] frozen model hashes recorded pre-run
- [ ] `submission_task1.csv` hash recorded pre-run
- [ ] exact frozen feature schema used
- [ ] feature registry joined successfully
- [ ] leakage audit passes
- [ ] service native/SHAP feature importance generated
- [ ] lateness native/SHAP feature importance generated
- [ ] service global SHAP generated
- [ ] late global SHAP generated
- [ ] SHAP method documented per model
- [ ] SHAP output space documented per model
- [ ] service SHAP reconstructs raw prediction
- [ ] late SHAP reconstructs base model output
- [ ] service post-processing bridge reproduces final output
- [ ] late calibration bridge reproduces final probability
- [ ] deterministic local service example generated
- [ ] deterministic local late-risk example generated
- [ ] local examples anonymized in public-facing summary
- [ ] meaningful business-driver summary generated
- [ ] importance-vs-SHAP disagreement reported where relevant
- [ ] no unsupported directional claims
- [ ] noncausal disclaimer included
- [ ] causal-language audit passes
- [ ] correlated-feature caution included
- [ ] no external API used
- [ ] competition derivatives remain private
- [ ] post-run frozen model hashes equal pre-run
- [ ] post-run `submission_task1.csv` hash equals pre-run
- [ ] synthetic explainability tests pass
- [ ] relevant Task 1 leakage/final-inference tests pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] private outputs ignored
- [ ] Task 2 final outputs unchanged
- [ ] independent Phase 25 review passes
- [ ] no unresolved STOP condition remains

Then:

```text
PHASE 25 STATUS: PASS
TASK 1 EXPLAINABILITY: COMPLETE
FROZEN TASK 1 MODELS: UNCHANGED
READY FOR PHASE 26: YES
```

---

# 78. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-25-task1-explainability
```

Recommended commits:

```text
feat(task1): add model-agnostic explanation adapters
feat(task1): add Task 1 global and local SHAP explanations
feat(task1): add business-driver and causal-language reporting
test(task1): add explainability faithfulness and leakage tests
docs(task1): document Task 1 model explanations
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run targeted tests.

Then:

```bash
pytest -q

python -m pip check
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

If generated real-data explanation figures/docs contain competition-data derivatives and the repository is public:

```text
DO NOT COMMIT THEM
```

Keep them for the authorized final submission package.

---

# 79. Recommended model

Phase 25 includes subtle technical risks:

- model-family-specific SHAP behavior;
- binary-class output-space interpretation;
- calibration;
- service post-processing;
- feature-schema mapping;
- leakage checks;
- causal-language correctness.

Recommended implementation:

```text
GPT-5.6 Sol
Reasoning: High
```

Recommended independent review:

```text
GPT-5.6 Sol
Reasoning: High
```

A lower reasoning setting is not recommended for the first SHAP/calibration implementation.

---

# 80. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 25 only.

PHASE:
Task 1 Explainability

TASK RANGE:
DT-343 through DT-349

EXECUTION MODE:
POST-HOC EXPLAINABILITY ONLY.
The final Task 1 models are already frozen.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 26.

==================================================
MISSION
==================================================

Build trustworthy, reproducible explainability for the FINAL Task 1
service-time and lateness models without changing model behavior.

Required work:

DT-343 Generate service-model feature importance
DT-344 Generate lateness-model feature importance
DT-345 Generate SHAP global explanation
DT-346 Generate local service prediction explanation
DT-347 Generate local late-risk explanation
DT-348 Identify meaningful business drivers
DT-349 Avoid unsupported causal claims

This phase must explain the frozen models.

It must NOT:
- retrain them
- tune them
- reselect features
- change calibration
- alter predictions
- change submission_task1.csv
- send competition data to external APIs

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - Phase 25
4. PHASE_06_COMPETITION_CONTRACT.md
   - feature registry / leakage rules
5. PHASE_07_COMPETITION_CONTRACT.md
   - frozen validation contract
6. PHASE_09_COMPETITION_CONTRACT.md
   - final Task 1 model selection
7. PHASE_10_COMPETITION_CONTRACT.md
   - frozen final models / inference contract
8. PHASE_25_COMPETITION_CONTRACT.md

Inspect existing Task 1 implementation:

9. final Task 1 model-loading code
10. final Task 1 inference pipeline
11. feature registry / feature schema code
12. leakage-audit code
13. frozen final model config
14. existing Task 1 tests

Do not assume model family.
Read the frozen metadata.

==================================================
OFFICIAL SOURCE BOUNDARY
==================================================

Official Task 1 predicts:

pred_service_min
=
predicted outlet handling time in minutes

pred_late_prob
=
probability arrival occurs after the outlet delivery window closes

The official challenge:

- requires teams to choose and justify features
- allows planned departure/travel/arrival context at prediction time
- does NOT allow actual journey/handling values as prediction-time inputs
- requires architecture/preprocessing/model deliverables
- requires a demo explaining model architecture, preprocessing, labels and
  challenges

SHAP itself is NOT an organizer-mandated method.
It is a finalized WayLoom Phase 25 engineering requirement.

Competition restrictions remain active:

- no prohibited pretrained modelling system
- no proprietary API modelling/preprocessing
- no external competition-data sharing

Run explanation locally.

==================================================
FROZEN ARTIFACTS — DO NOT MODIFY
==================================================

Do NOT modify:

configs/task1_final_models.yaml

models/task1_service/**

models/task1_late/**

outputs/submission_task1.csv

Task 1 feature semantics

Task 1 calibration policy

Task 1 post-processing policy

Also do NOT modify finalized Task2 outputs/policy.

Compute pre/post hashes where feasible to prove explanation generation is
read-only.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task1/explainability.py
src/task1/shap_adapter.py
src/task1/explanation_reporting.py
src/task1/causal_language.py

scripts/build_task1_explainability.py
scripts/validate_task1_explainability.py

configs/task1_explainability.yaml

docs/task1_explainability.md
docs/task1_explainability_spec.md

tests/test_task1_explainability_importance.py
tests/test_task1_shap.py
tests/test_task1_local_explanations.py
tests/test_task1_causal_language.py
tests/test_task1_explainability_contract.py

Private generated outputs should go under:

reports/private/phase25_task1_explainability/

Selected competition-facing plots may be generated under a controlled
figures path only if the repository/data-confidentiality policy permits.

Do not publish real competition derivatives publicly.

==================================================
PRECONDITIONS
==================================================

Require:

Phase 09 final Task 1 model choices frozen

Phase 10 final Task 1 model bundles exist

service metadata exists

late metadata exists

feature schemas exist

saved models reload successfully

submission_task1.csv exists and is already validated

final Task 1 config identifies exactly one service model and one late model

If any precondition is missing:
STOP.

==================================================
READ-ONLY HASH GUARD
==================================================

Before explainability generation, hash:

Task 1 final model artifacts

Task 1 metadata/schema artifacts

configs/task1_final_models.yaml

outputs/submission_task1.csv

After explainability generation, recompute them.

Require identical hashes.

If any frozen artifact changes:
FAIL.

==================================================
FEATURE MATRIX CONTRACT
==================================================

Use the exact frozen Task 1 inference feature pipeline.

Require:

same feature names

same feature order

same categorical semantics

same numerical semantics

same imputer/encoder/scaler state

same historical-feature state

same missing-value rules

same feature enable/disable profile

Do NOT create a separate "explainability feature pipeline."

Do NOT refit preprocessors on Task 1 test data.

==================================================
LEAKAGE SAFETY
==================================================

Before explaining any model, rerun/consume the existing feature leakage
audit.

Explanation features must contain zero direct current-outcome fields such
as:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

and zero direct labels/targets.

Chronology-safe historical aggregates are allowed only if they were part of
the frozen model feature set and already passed Phase 06/10 leakage rules.

If any forbidden actual/outcome feature appears in:

model schema
importance output
SHAP output
business-driver output

STOP.

This is a serious cross-phase blocker.

==================================================
EXPLANATION POPULATION
==================================================

Default explanation population:

the frozen Task 1 TEST feature matrix used by final inference.

Reason:

it explains the model on the actual deployment/submission distribution and
requires no test labels.

Use a deterministic bounded sample for expensive SHAP work.

Recommended:

max_rows: 2000
min_rows_if_available: 200
random_seed: 42

Select deterministically using a stable hash/order mechanism.

Do not expose delivery_id values in generated public-facing reports.

If the test set is smaller:
use all rows.

==================================================
MODEL FAMILY SUPPORT
==================================================

Do not assume CatBoost.

Detect model family from frozen metadata.

Support, where actually selected:

CatBoost

LightGBM

XGBoost

supported sklearn tree models

supported linear models

other selected family only through a verified local SHAP adapter

Never switch to a different model just because it is easier to explain.

==================================================
DT-343 — SERVICE FEATURE IMPORTANCE
==================================================

Generate feature importance for the exact saved final service model.

Preferred source:

model-native importance when the selected family supports a trustworthy
native importance API.

Record:

feature_name

importance

importance_type

rank

semantic_group if available

source lineage metadata if available

Recommended model-family native importance:

CatBoost:
PredictionValuesChange or the frozen/documented native importance type

LightGBM:
gain-based importance preferred over split-count when available

XGBoost:
gain-based importance preferred when available

sklearn tree:
feature_importances_

linear model:
absolute coefficient magnitude only if preprocessing/scaling semantics make
the interpretation valid and clearly labelled

If no valid native importance exists:
use mean absolute SHAP as the feature-importance fallback and label it:

importance_type = mean_abs_shap_fallback

Do NOT fabricate a native importance.

Do not compare numeric importance scales across model families as if they
mean the same thing.

==================================================
DT-344 — LATENESS FEATURE IMPORTANCE
==================================================

Generate importance for the BASE lateness classifier used by the frozen
final probability pipeline.

If the final pipeline has calibration:

the calibrator itself has no feature-level importance.

Explain the underlying classifier.

Keep the frozen calibration step separate and documented.

Record the same fields as the service importance.

Positive class must remain:

late_flag = 1

corresponding to arrival after window close.

Do not accidentally explain class 0.

==================================================
DT-345 — GLOBAL SHAP EXPLANATION
==================================================

Generate SHAP values for BOTH final Task 1 models.

Minimum outputs:

service global SHAP summary

lateness global SHAP summary

For each feature calculate at least:

mean_abs_shap

mean_shap

rank

sample_count

semantic_group if available

Also generate local/private plot-ready SHAP arrays only where required.

Do not store row identifiers in aggregate SHAP summaries.

==================================================
SHAP ADAPTER — CATBOOST
==================================================

If selected final model is CatBoost:

use model-native SHAP values where practical:

get_feature_importance(..., type="ShapValues")

for the exact frozen model/input schema.

For regression:

SHAP contribution sum + expected value must reconstruct the RAW model
service prediction.

For binary classification:

SHAP values normally explain CatBoost raw formula value / margin.

Verify against:

prediction_type="RawFormulaVal"

Then map through the same base-probability link/inference path.

Do not claim raw-margin SHAP contributions are probability-point changes.

==================================================
SHAP ADAPTER — LIGHTGBM
==================================================

If selected model is LightGBM:

use verified contribution prediction such as:

pred_contrib=True

or a verified local SHAP TreeExplainer.

Require the contribution sum to reconstruct the appropriate raw prediction
space.

For binary classification, explicitly record whether contributions are in
raw margin/log-odds or probability space.

==================================================
SHAP ADAPTER — XGBOOST
==================================================

If selected model is XGBoost:

use verified contribution prediction such as:

pred_contribs=True

with the exact booster/input matrix.

Verify reconstruction.

Document output space.

==================================================
SHAP ADAPTER — OTHER MODELS
==================================================

If no native tree-contribution path exists:

use the locally installed SHAP package with the most appropriate verified
explainer.

Examples:

TreeExplainer
LinearExplainer
generic shap.Explainer

Do NOT use a remote API.

Do NOT silently use an approximate explainer whose reconstruction cannot be
validated.

If the selected final model cannot be explained reliably under the frozen
pipeline:

STOP.

==================================================
SHAP RECONSTRUCTION TEST — SERVICE
==================================================

For each explained service sample:

expected_value
+
sum(feature SHAP contributions)
≈
raw service model prediction

Use tight numerical tolerance appropriate to the model family.

Then separately apply the frozen Phase 10 service post-processing.

If the frozen pipeline clips or otherwise post-processes service output:

show:

raw_model_prediction

postprocessing_policy

final_pred_service_min

Do NOT claim SHAP sums directly to the post-processed value when it does
not.

==================================================
SHAP RECONSTRUCTION TEST — LATENESS
==================================================

For lateness:

SHAP reconstruction must match the BASE model output in its documented
output space.

Then reproduce the exact frozen inference chain:

base raw score
→ base probability/link as required
→ frozen calibration input
→ frozen calibrator if present
→ final pred_late_prob

Do not assume calibration consumes a particular quantity.
Read the frozen inference implementation.

If calibration is enabled:

do NOT claim SHAP feature contributions sum to the final calibrated
probability unless a probability-space explainer has been explicitly
verified.

Instead say:

SHAP explains the base classifier score;
the frozen calibrator maps the base output to the submitted probability.

==================================================
GLOBAL SHAP PLOTS
==================================================

Generate privacy-safe, competition-use plots locally:

service SHAP bar

service SHAP distribution/beeswarm if supported

late SHAP bar

late SHAP distribution/beeswarm if supported

Use feature display names from the registry when possible.

Do not expose:

delivery_id

raw private row identifiers

unnecessary row-level values in figure labels

Keep figures deterministic.

Do not use a decorative plot style that obscures interpretation.

==================================================
DT-346 — LOCAL SERVICE PREDICTION EXPLANATION
==================================================

Generate one deterministic local explanation.

Recommended selector:

final service prediction closest to the median final service prediction

Tie break:

stable original/template row position

Label it generically:

SERVICE_EXAMPLE_A

Do NOT expose delivery_id in competition-facing narrative by default.

Show:

final pred_service_min

raw service model prediction

post-processing step if any

expected/baseline value

top positive SHAP contributors

top negative SHAP contributors

feature values where safe

SHAP reconstruction check

Use language such as:

"this feature increased the model's prediction relative to its baseline"

not:

"this feature caused service to take longer"

==================================================
DT-347 — LOCAL LATE-RISK EXPLANATION
==================================================

Generate one deterministic high-risk local example.

Recommended selector:

highest final pred_late_prob

Tie break:

stable original/template row position

Label:

LATE_EXAMPLE_A

Explain:

final pred_late_prob

base raw classifier score

base probability where applicable

calibration method

expected/base SHAP value

top positive risk-score contributors

top negative risk-score contributors

SHAP reconstruction

calibration bridge to final probability

If SHAP is raw-margin/log-odds:

say so prominently.

Do not say a SHAP value of +0.4 means +40 percentage points.

==================================================
LOCAL EXPLANATION PRIVACY
==================================================

Generated local examples are competition-data derivatives.

Store detailed versions under private reports.

For competition-facing/demo assets:

anonymize delivery identifiers

show only a small necessary set of feature values

avoid revealing raw rows

Do not publish outside the authorized competition submission context.

==================================================
DT-348 — IDENTIFY MEANINGFUL BUSINESS DRIVERS
==================================================

Create an evidence-based driver summary from:

model-native importance

global mean absolute SHAP

feature registry semantics

source lineage

local explanation consistency

Potential feature categories may include:

planned time/slack context

planned travel/distance

order size

dock/access/reference service allowance

route position/planned workload

vehicle/static context

calendar/festival context

chronology-safe historical behavior

BUT:

do not predeclare any of these as actual top drivers.

Use the computed results.

For each reported business driver record:

driver / feature or semantic group

model:
service / lateness

global rank / SHAP strength

business meaning

source/prediction-time availability

interpretation

causal caution

==================================================
BUSINESS DRIVER FILTER
==================================================

A feature/semantic group should be called a meaningful model driver only if:

it exists in the final frozen schema

it passes leakage lineage checks

it has material model importance / SHAP evidence

it has an interpretable business meaning

and the claim can be phrased as model behavior, not causal fact.

If importance and SHAP strongly disagree:

report the disagreement.

Do not cherry-pick whichever method tells the nicer story.

==================================================
DIRECTION LANGUAGE
==================================================

Do not infer a global monotonic direction from mean absolute SHAP alone.

Mean absolute SHAP tells strength, not direction.

Only state directional behavior if supported by:

SHAP distribution/dependence evidence

or repeated local/global pattern

and phrase it:

"in this model/sample, higher X tended to be associated with higher/lower
model output"

If direction is mixed/nonlinear:

say:

"context-dependent/non-monotonic"

Do not simplify it into a false monotonic rule.

==================================================
DT-349 — AVOID UNSUPPORTED CAUSAL CLAIMS
==================================================

Every explanation artifact must include a disclaimer equivalent to:

"These explanations describe how the trained model uses observed features.
They show model associations/attributions, not causal effects."

Avoid phrases such as:

X causes lateness

X causes long service time

increasing X will reduce lateness

changing X will definitely improve service

X is the reason the delivery was late

unless a causal design supports that claim.
Phase25 does not provide such a causal design.

Preferred language:

the model relies on

is associated with

contributes to the model score

pushes the prediction higher/lower

is an important model feature

the model learned a pattern involving

==================================================
CORRELATED-FEATURE CAUTION
==================================================

Document:

SHAP attribution can be distributed among correlated/redundant features.

Feature importance is model-specific.

A highly ranked feature is not necessarily actionable.

A low-ranked feature is not necessarily operationally unimportant.

Categorical effects can depend on interactions/context.

==================================================
CAUSAL LANGUAGE AUDIT
==================================================

Implement a lightweight automated audit over generated explainability
Markdown/text.

Flag high-risk phrases such as:

causes
caused by
guarantees
will reduce
will increase
the reason for
results in

Do not blindly ban the word:

driver

because the Phase25 task uses "business drivers."

Instead require the report to define:

driver = model driver / predictive association, not causal driver.

The audit should combine:

regex/static checks
+
manual review checklist

==================================================
OUTPUTS
==================================================

Private report directory:

reports/private/phase25_task1_explainability/

Recommended files:

run_manifest.json

service_feature_importance.csv

late_feature_importance.csv

service_shap_global.csv

late_shap_global.csv

service_local_explanation.json

late_local_explanation.json

business_drivers.json

shap_reconstruction_audit.json

feature_leakage_audit.json

causal_language_audit.json

frozen_artifact_hash_audit.json

phase25_explainability_report.md

Plot files may also be stored here.

docs/task1_explainability.md must contain only concise, privacy-safe,
competition-appropriate explanation summary.

==================================================
RUN MANIFEST
==================================================

Record:

phase = 25

service model family/config ID

late model family/config ID

calibration method

service postprocessing policy

feature schema hashes

model artifact hashes

submission_task1 SHA256

explanation population

sample selection rule

sample size

SHAP method per model

SHAP output space per model

positive class

random seed

library versions

git commit

No row IDs.

==================================================
VALIDATION
==================================================

Create scripts/validate_task1_explainability.py.

Require:

frozen model hashes unchanged

submission_task1 hash unchanged

service importance complete

late importance complete

global SHAP both models

SHAP reconstruction PASS

positive class correct

service postprocessing bridge correct

late calibration bridge correct

local service explanation complete

local late explanation complete

business-driver summary complete

feature leakage audit PASS

causal-language audit PASS

no private IDs in competition-facing docs/plots

No Phase26 output.

==================================================
TESTS
==================================================

Use synthetic models/data only for agent-run tests.

Test model-native/fallback importance.

Test SHAP shape normalization.

Test binary positive-class selection.

Test regression SHAP reconstruction.

Test classification raw-margin SHAP reconstruction.

Test calibrated classifier explanation bridge.

Test uncalibrated classifier.

Test service clipping/postprocessing bridge.

Test deterministic SHAP sample selection.

Test deterministic local service selector.

Test deterministic local late selector.

Test extra categorical features.

Test missing/unseen categories through frozen preprocessing interface.

Test one-hot/transformed feature naming where relevant.

Test unsupported model family fails cleanly.

Test actual/outcome feature in explained schema => hard fail.

Test current target column in schema => hard fail.

Test business-driver output contains only final enabled features.

Test mean_abs_shap not treated as direction.

Test causal-language phrases flagged.

Test anonymized local IDs.

Test model/submission hashes unchanged.

==================================================
SHAP NUMERICAL EDGE CASES
==================================================

Handle:

constant feature

all-zero SHAP feature

single-row explanation

small explanation population

NaN/missing feature values handled by frozen model

categorical model features

very large/small raw margins

late probability near 0 or 1

service postprocessing changes raw prediction

calibrator changes base probability materially

ties in local example selector

multiple output arrays from SHAP library

Different model libraries may return SHAP shapes differently.

Normalize carefully and test.

==================================================
STOP CONDITIONS
==================================================

STOP if:

final model config is not frozen

saved model missing

feature schema missing

model reload fails

Task1 submission missing

explanation pipeline requires retraining

explanation pipeline changes predictions

frozen artifact hash changes

forbidden actual/current outcome feature appears

target leakage appears

SHAP reconstruction fails beyond tolerance

late positive class is ambiguous

calibration bridge cannot be reproduced

service postprocessing bridge cannot be reproduced

unsupported model cannot be reliably explained

global SHAP uses external API

competition data would need to leave local machine

business-driver claims are unsupported

causal language cannot be corrected without changing claims

Phase26 work would be introduced

==================================================
LOCAL HUMAN COMMAND
==================================================

Implement but do not execute private real Task1 data inside the external
agent context.

Expected command shape:

python scripts/build_task1_explainability.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --final-model-config configs/task1_final_models.yaml \
  --explainability-config configs/task1_explainability.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --submission outputs/submission_task1.csv \
  --report-dir reports/private/phase25_task1_explainability \
  --summary-output docs/task1_explainability.md

Use the actual repository CLI if it differs.

Then:

python scripts/validate_task1_explainability.py \
  --config configs/task1_explainability.yaml \
  --final-model-config configs/task1_final_models.yaml \
  --service-model-dir models/task1_service \
  --late-model-dir models/task1_late \
  --submission outputs/submission_task1.csv \
  --report-dir reports/private/phase25_task1_explainability \
  --summary docs/task1_explainability.md

==================================================
SAFE TEST LOOP
==================================================

Run:

pytest -q \
  tests/test_task1_explainability_importance.py \
  tests/test_task1_shap.py \
  tests/test_task1_local_explanations.py \
  tests/test_task1_causal_language.py \
  tests/test_task1_explainability_contract.py

Then relevant existing Task1 tests, including leakage and final inference
tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run private real-data explainability in agent context.

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-343 READY
DT-344 READY
DT-345 READY
DT-346 READY
DT-347 READY
DT-348 READY
DT-349 READY

service importance exact final model

late importance exact final base classifier

global SHAP service

global SHAP lateness

SHAP output spaces documented

SHAP reconstruction verified

service postprocessing bridge verified

late calibration bridge verified

local service deterministic

local late deterministic

business drivers evidence-based

feature registry lineage attached

no actual/outcome leakage

no unsupported causal language

frozen model hashes unchanged

submission_task1 unchanged

no external API/data sharing

no Phase26 implementation

==================================================
RETURN ONLY
==================================================

PHASE:
25 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-343 READY / FAIL
DT-344 READY / FAIL
DT-345 READY / FAIL
DT-346 READY / FAIL
DT-347 READY / FAIL
DT-348 READY / FAIL
DT-349 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

SERVICE FEATURE IMPORTANCE:
PASS / FAIL

LATENESS FEATURE IMPORTANCE:
PASS / FAIL

GLOBAL SHAP — SERVICE:
PASS / FAIL

GLOBAL SHAP — LATENESS:
PASS / FAIL

SERVICE SHAP RECONSTRUCTION:
PASS / FAIL

LATENESS SHAP RECONSTRUCTION:
PASS / FAIL

SERVICE POSTPROCESSING BRIDGE:
PASS / FAIL

LATENESS CALIBRATION BRIDGE:
PASS / FAIL

LOCAL SERVICE EXPLANATION:
PASS / FAIL

LOCAL LATE-RISK EXPLANATION:
PASS / FAIL

BUSINESS DRIVERS:
PASS / FAIL

FEATURE LEAKAGE AUDIT:
PASS / FAIL

CAUSAL-LANGUAGE AUDIT:
PASS / FAIL

FROZEN TASK1 MODEL ARTIFACTS CHANGED:
MUST BE NO

submission_task1.csv CHANGED:
MUST BE NO

PRIVATE REAL DATA ACCESSED:
NO

EXTERNAL API USED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print:

1. exact local explainability command
2. exact local validation command

PHASE 25 STATUS:
AWAITING LOCAL EXPLAINABILITY RUN

READY FOR PHASE 26:
NO

Then STOP.

Do not start Phase26.

```

---

# 81. Independent Phase 25 review prompt

Use a completely fresh Codex/Cursor session after local explainability generation and validation pass.

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon PHASE 25.

PHASE:
Task 1 Explainability

TASK RANGE:
DT-343 through DT-349

Do NOT implement Phase26.
Do NOT modify code initially.
Do NOT run private real-data explainability.
Do NOT inspect private row-level SHAP values.
Do NOT modify frozen Task1 models or submission.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase25
4. PHASE_06_COMPETITION_CONTRACT.md
5. PHASE_09_COMPETITION_CONTRACT.md
6. PHASE_10_COMPETITION_CONTRACT.md
7. PHASE_25_COMPETITION_CONTRACT.md

Inspect:

8. src/task1/explainability.py
9. src/task1/shap_adapter.py
10. src/task1/explanation_reporting.py
11. src/task1/causal_language.py

12. scripts/build_task1_explainability.py
13. scripts/validate_task1_explainability.py

14. configs/task1_explainability.yaml
15. configs/task1_final_models.yaml

16. docs/task1_explainability_spec.md
17. docs/task1_explainability.md where safe

18. tests/test_task1_explainability_importance.py
19. tests/test_task1_shap.py
20. tests/test_task1_local_explanations.py
21. tests/test_task1_causal_language.py
22. tests/test_task1_explainability_contract.py

Also inspect relevant final Task1 inference/leakage tests.

HUMAN SANITIZED LOCAL RESULT:

FROZEN MODEL CONFIG: <PASS/FAIL>
SERVICE MODEL RELOAD: <PASS/FAIL>
LATENESS MODEL RELOAD: <PASS/FAIL>
TASK1 SUBMISSION HASH: <PASS/FAIL>

FEATURE SCHEMA PARITY: <PASS/FAIL>
FEATURE LEAKAGE AUDIT: <PASS/FAIL>

SERVICE FEATURE IMPORTANCE: <PASS/FAIL>
LATENESS FEATURE IMPORTANCE: <PASS/FAIL>

GLOBAL SHAP — SERVICE: <PASS/FAIL>
GLOBAL SHAP — LATENESS: <PASS/FAIL>

SERVICE SHAP RECONSTRUCTION: <PASS/FAIL>
LATENESS SHAP RECONSTRUCTION: <PASS/FAIL>

SERVICE POSTPROCESSING BRIDGE: <PASS/FAIL>
LATENESS CALIBRATION BRIDGE: <PASS/FAIL>

LOCAL SERVICE EXPLANATION: <PASS/FAIL>
LOCAL LATE-RISK EXPLANATION: <PASS/FAIL>

BUSINESS DRIVER SUMMARY: <PASS/FAIL>
CAUSAL-LANGUAGE AUDIT: <PASS/FAIL>

FROZEN MODEL HASHES UNCHANGED: <PASS/FAIL>
submission_task1.csv UNCHANGED: <PASS/FAIL>

Do not request private row IDs or SHAP matrices.

==================================================
AUDIT TASKS
==================================================

DT-343:
service importance is for exact final service model.

DT-344:
late importance is for exact final base classifier and correct positive class.

DT-345:
global SHAP exists for both Task1 models and is faithful.

DT-346:
local service explanation deterministic and reconstructs raw model output.

DT-347:
local late explanation deterministic, correct output space, and calibration bridge.

DT-348:
business drivers evidence-based and feature-registry grounded.

DT-349:
noncausal language enforced.

==================================================
CRITICAL SHAP AUDIT
==================================================

Verify:

service SHAP sum reconstructs RAW model output.

If service postprocessing exists:
it is shown separately.

Late SHAP reconstructs base classifier output.

If late SHAP is raw margin/log-odds:
it is not described as probability points.

If calibration exists:
SHAP explains base classifier and the exact frozen calibration bridge is separate.

Positive late class:
1.

No class-index guessing.

==================================================
CRITICAL FEATURE AUDIT
==================================================

Every explained feature must:

exist in frozen feature schema

exist in feature registry

pass leakage lineage

be prediction-time valid under frozen contract

No:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
direct target/current outcome

unless appearing only in an explicit prohibited-feature test fixture.

==================================================
CRITICAL LANGUAGE AUDIT
==================================================

Review generated explanation prose.

Reject unsupported causal phrases.

Require disclaimer that explanations are model associations/attributions,
not causal effects.

Verify mean_abs_shap is not used to claim directional effects.

Verify correlated-feature limitation is disclosed.

==================================================
PRIVACY AUDIT
==================================================

Verify competition-facing docs/figures do not expose:

delivery_id

raw row dumps

private SHAP matrices

unnecessary category lists

Private explanation artifacts remain ignored/unstaged.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_task1_explainability_importance.py \
  tests/test_task1_shap.py \
  tests/test_task1_local_explanations.py \
  tests/test_task1_causal_language.py \
  tests/test_task1_explainability_contract.py

Then relevant Task1 feature-leakage/final-inference tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run real private explainability.

==================================================
RETURN
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

SERVICE FEATURE IMPORTANCE:
PASS / FAIL

LATENESS FEATURE IMPORTANCE:
PASS / FAIL

GLOBAL SHAP SERVICE:
PASS / FAIL

GLOBAL SHAP LATENESS:
PASS / FAIL

SERVICE SHAP FAITHFULNESS:
PASS / FAIL

LATENESS SHAP FAITHFULNESS:
PASS / FAIL

SERVICE POSTPROCESSING BRIDGE:
PASS / FAIL

LATENESS CALIBRATION BRIDGE:
PASS / FAIL

POSITIVE CLASS:
PASS / FAIL

FEATURE SCHEMA PARITY:
PASS / FAIL

FEATURE LEAKAGE:
PASS / FAIL

BUSINESS DRIVER QUALITY:
PASS / FAIL

CAUSAL LANGUAGE:
PASS / FAIL

CORRELATED-FEATURE CAUTION:
PASS / FAIL

PRIVACY:
PASS / FAIL

FROZEN MODEL HASHES:
PASS / FAIL

TASK1 SUBMISSION UNCHANGED:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
None / list exact blockers

NON-BLOCKING IMPROVEMENTS:
...

DT-343: PASS/FAIL
DT-344: PASS/FAIL
DT-345: PASS/FAIL
DT-346: PASS/FAIL
DT-347: PASS/FAIL
DT-348: PASS/FAIL
DT-349: PASS/FAIL

PHASE 25 INDEPENDENT REVIEW:
PASS / FAIL

TASK 1 EXPLAINABILITY:
COMPLETE / INCOMPLETE

FROZEN TASK 1 MODELS:
UNCHANGED / CHANGED

READY FOR PHASE 26:
YES / NO

If PASS, final lines:

PHASE 25 INDEPENDENT REVIEW: PASS
TASK 1 EXPLAINABILITY: COMPLETE
FROZEN TASK 1 MODELS: UNCHANGED
BLOCKERS: None
READY FOR PHASE 26: YES

Then STOP.

Do not start Phase26.
```

---

# 82. Completion record

```markdown
# Phase 25 Completion Record

## Tasks

- [ ] DT-343
- [ ] DT-344
- [ ] DT-345
- [ ] DT-346
- [ ] DT-347
- [ ] DT-348
- [ ] DT-349

## Frozen model integrity

- [ ] service model hashes unchanged
- [ ] late model hashes unchanged
- [ ] calibration artifact unchanged
- [ ] final model config unchanged
- [ ] submission_task1.csv unchanged

## Global explanation

- [ ] service feature importance
- [ ] late feature importance
- [ ] service global SHAP
- [ ] late global SHAP
- [ ] output spaces documented
- [ ] SHAP reconstruction PASS

## Local explanation

- [ ] service local example
- [ ] service raw→postprocessed bridge
- [ ] late local example
- [ ] late base→calibrated bridge
- [ ] identifiers anonymized

## Interpretation

- [ ] business drivers evidence-based
- [ ] feature registry/lineage joined
- [ ] importance/SHAP disagreement disclosed where relevant
- [ ] noncausal disclaimer
- [ ] correlated-feature caution
- [ ] causal-language audit PASS

## Safety

- external API used: NO
- private real rows exposed: NO
- Phase26 started: NO

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 25 STATUS: PASS / FAIL
TASK 1 EXPLAINABILITY: COMPLETE / INCOMPLETE
FROZEN TASK 1 MODELS: UNCHANGED / CHANGED
READY FOR PHASE 26: YES / NO
```

---

# 83. Final checklist

Before Phase 26:

- [ ] DT-343–DT-349 all PASS.
- [ ] explanation uses exact frozen service model.
- [ ] explanation uses exact frozen late base classifier.
- [ ] positive late class verified.
- [ ] calibration identified.
- [ ] service postprocessing identified.
- [ ] exact frozen feature matrix used.
- [ ] no actual/current-outcome leakage.
- [ ] service feature importance generated.
- [ ] late feature importance generated.
- [ ] global SHAP generated for both.
- [ ] SHAP output spaces documented.
- [ ] service SHAP reconstructs raw prediction.
- [ ] late SHAP reconstructs base output.
- [ ] service final-output bridge passes.
- [ ] late calibration bridge passes.
- [ ] local service example deterministic.
- [ ] local late example deterministic.
- [ ] business-driver summary evidence-based.
- [ ] no false monotonic direction from mean absolute SHAP.
- [ ] no unsupported causal claims.
- [ ] correlated-feature warning included.
- [ ] no row IDs in competition-facing explanation.
- [ ] no external API/data sharing.
- [ ] frozen Task 1 model/config hashes unchanged.
- [ ] `submission_task1.csv` unchanged.
- [ ] Task 2 final outputs unchanged.
- [ ] safe tests pass.
- [ ] full suite passes.
- [ ] independent review passes.

Only then:

```text
PHASE 25 STATUS: PASS
TASK 1 EXPLAINABILITY: COMPLETE
FROZEN TASK 1 MODELS: UNCHANGED
READY FOR PHASE 26: YES
```
