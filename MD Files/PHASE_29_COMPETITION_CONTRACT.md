# PHASE 29 — Architecture Documentation

> **Filename:** `PHASE_29_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 29 — Architecture Documentation  
> **Task range:** **DT-374 → DT-378**  
> **Task count:** **5**  
> **Phase dependency:** **Stable architecture from Phases 4–24**  
> **Default phase priority:** **P0**  
> **Master phase gate:** Required architecture diagrams accurately match the final implemented pipelines and proposed deployment.  
> **Execution mode:** Documentation-only, read-only against frozen model/optimizer pipelines.  
> **Critical rule:** Draw the system that actually exists; do not redesign or retune it while documenting it.

---

# 1. Phase 29 purpose

Phase 29 creates the **competition-required architecture diagrams** for the WayLoom Datathon submission.

The official Challenge Booklet requires:

> Architecture diagrams showing the models, preprocessing pipeline, and proposed deployment approach. High-level diagrams are sufficient.

This phase therefore converts the already-implemented work from Phases 4–24 into a clear visual explanation that judges can understand quickly.

The diagrams must support later work in:

```text
final notebook

preprocessing/documentation package

demo video

evidence appendix

final submission folder
```

They are not decorative diagrams.

They are a visual representation of the final system contract.

---

# 2. Finalized Phase 29 master inventory

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-374** | [O] | P0 | Core pipeline architecture stable | Create high-level Datathon architecture |
| [ ] | **DT-375** | [E] | P0 | Stable architecture from Phases 4–24 | Create Task 1 pipeline diagram |
| [ ] | **DT-376** | [E] | P0 | Stable architecture from Phases 4–24 | Create Task 2A forecasting diagram |
| [ ] | **DT-377** | [E] | P0 | Stable architecture from Phases 4–24 | Create Task 2B optimization diagram |
| [ ] | **DT-378** | [O] | P0 | Stable architecture from Phases 4–24 | Show proposed deployment approach |

**Expected Phase 29 tasks:** 5  
**Missing tasks allowed:** 0  
**Phase complete:** [ ]  
**READY FOR PHASE 30:** NO

---

# 3. Official competition requirements

The official Datathon deliverables require architecture diagrams that:

```text
show models

show preprocessing pipeline

show proposed deployment approach
```

The booklet explicitly says:

```text
high-level diagrams are sufficient
```

The final demo also asks the team to explain:

```text
model architecture

preprocessing

label construction

challenges encountered
```

The Datathon judging rubric includes:

```text
Model and architecture implementation: 25%
```

Therefore the diagrams should optimize for:

```text
accuracy

clarity

traceability

readability

judge comprehension
```

not diagram complexity.

---

# 4. Source-of-truth hierarchy

Use:

```text
Official Challenge Booklet
        ↓
WAYLOOM_DATATHON_MASTER_PLAN.md
        ↓
frozen Task1 / Task2A / Task2B contracts
        ↓
final configs + safe model metadata
        ↓
tracked implementation
        ↓
architecture presentation
```

If an older design document names a model that differs from the final config:

```text
the final config wins
```

Do not preserve stale architecture for visual consistency.

---

# 5. Phase scope

Phase 29 covers the **core required Datathon architecture** implemented by Phases 4–24.

Required diagrams:

```text
1. High-level Datathon architecture
2. Task1 service/lateness pipeline
3. Task2A demand forecasting pipeline
4. Task2B optimization pipeline
5. Proposed deployment approach
```

Phases 25–28 are optional/later relative to the Phase 29 master dependency.

They may be shown as dashed optional extensions only when useful.

They are not required to complete the core Phase 29 diagrams.

---

# 6. Preconditions

Before Phase 29 can pass, require:

```text
Phase10 Task1 final pipeline frozen

Phase17 Task2A final pipeline frozen

Phase24 Task2B final output/policy complete

final Task1 model config exists

final Task2A model config exists

Task2B optimizer/policy configs exist

safe model/runtime metadata can resolve actual final architecture
```

If actual final model names/strategy cannot be identified:

```text
STOP
```

Do not draw guessed model families.

---

# 7. Frozen-artifact rule

This is a documentation phase.

Do not modify:

```text
Task1 final model/config/submission

Task2A final model/config/submission

Task2B final allocation/config/submission/policy

Phase22/23 freeze/checker evidence
```

Architecture code/scripts may read safe configs/metadata.

They must not rewrite frozen artifacts.

---

# 8. Recommended Phase 29 files

Create/update:

```text
docs/architecture/
├── README.md
├── architecture_manifest.yaml
├── high_level_datathon.mmd
├── high_level_datathon.svg
├── task1_pipeline.mmd
├── task1_pipeline.svg
├── task2a_forecasting.mmd
├── task2a_forecasting.svg
├── task2b_optimization.mmd
├── task2b_optimization.svg
├── proposed_deployment.mmd
├── proposed_deployment.svg
└── png/                         # optional
    ├── high_level_datathon.png
    ├── task1_pipeline.png
    ├── task2a_forecasting.png
    ├── task2b_optimization.png
    └── proposed_deployment.png

scripts/
├── build_architecture_manifest.py
├── validate_architecture_docs.py
└── render_architecture_diagrams.py   # optional if renderer available

tests/
├── test_architecture_manifest.py
├── test_architecture_contract.py
├── test_architecture_privacy.py
└── test_architecture_exports.py
```

Do not create Phase 30 preprocessing-document implementation.

---

# 9. Diagram source format

Recommended source:

```text
Mermaid .mmd
```

Reasons:

- text-based;
- diffable in Git;
- easy to maintain;
- supports subgraphs;
- supports SVG export;
- can be embedded in documentation.

Static submission assets:

```text
SVG
```

are required for Phase 29 completion.

PNG is optional.

---

# 10. Static export requirement

Do not rely on judges having a Mermaid renderer.

Every required diagram should have a static:

```text
.svg
```

export.

SVG is preferred because:

- text stays sharp;
- it scales in the final notebook/PDF/video;
- small file size;
- easy to inspect.

If static export cannot be generated automatically:

return:

```text
STATIC EXPORT PENDING
```

and give the human the exact render steps.

---

# 11. Rendering dependency safety

If `mmdc` or another local renderer already exists:

use it.

If no renderer exists:

do not make broad dependency changes that could destabilize the frozen ML environment.

Preferred options:

```text
use an isolated renderer dependency

or

human-export SVG from the committed Mermaid source
```

Do not upgrade core ML dependencies for a diagram renderer.

---

# 12. Architecture manifest

Create:

```text
docs/architecture/architecture_manifest.yaml
```

Its role is to make the diagrams testable against the frozen implementation.

It should contain only safe architecture metadata.

---

# 13. Architecture manifest — Task 1

Recommended fields:

```yaml
task1:
  service_model_family: <actual frozen value>
  service_config_id: <safe tracked id>

  late_model_family: <actual frozen value>
  late_config_id: <safe tracked id>

  late_calibration: <actual frozen value>
  service_postprocessing: <actual frozen value>

  prediction_time_actual_fields_forbidden:
    - actual_depart_time
    - actual_travel_duration_min
    - arrival_time
    - leave_outlet_time

  output_columns:
    - delivery_id
    - pred_service_min
    - pred_late_prob
```

Do not infer family names from old documentation.

Read them from final metadata.

---

# 14. Architecture manifest — Task 2A

Recommended:

```yaml
task2a:
  forecast_horizon_weeks: 10
  final_strategy: <actual frozen value>
  total_model_family: <actual frozen value>
  chilled_model_family_or_strategy: <actual frozen value>

  history_sources:
    - deliveries_train
    - task1_test_inputs

  output_columns:
    - row_id
    - pred_total_volume_m3
    - pred_chilled_volume_m3
```

If one model produces both targets, represent that accurately.

If chilled is derived rather than separately modelled, say so.

---

# 15. Architecture manifest — Task 2B

Recommended:

```yaml
task2b:
  solver: OR-Tools CP-SAT

  max_trips_per_vehicle: 2
  fresh_minutes_limit: 270
  style_tech_minutes_limit: 480

  objective_levels:
    - MAX served_order_count
    - MAX served_previous_deferred_count
    - MAX served_waiting_days_sum
    - MAX served_low_flexibility_count
    - MAX served_fresh_chilled_count
    - MAX served_fresh_count
    - MIN avoidable_reefer_van_assignment_count
    - MIN avoidable_reefer_assignment_count
    - MIN avoidable_van_assignment_count

  output_columns:
    - scenario
    - order_ref
    - outlet_id
    - decision
    - vehicle_id
    - trip_id
```

---

# 16. Architecture manifest — deployment

Recommended:

```yaml
deployment:
  status: proposed
  default_execution: private_local_batch
  external_proprietary_modelling_api: false
  hackathon_integration_required: false
```

Do not claim a real production environment exists unless it has actually been built and is intentionally part of the Datathon architecture.

---

# 17. Manifest privacy

Do not store:

```text
real delivery/order/vehicle IDs

row-level counts tied to private outputs

absolute C:\Users\... paths

private report hashes

credentials

API tokens
```

The manifest should be safe to include with documentation.

---

# 18. Manifest builder

Create:

```text
scripts/build_architecture_manifest.py
```

It should read only safe tracked configuration/metadata such as:

```text
configs/task1_final_models.yaml

safe Task1 model metadata

configs/task2a_final_models.yaml

safe Task2A runtime metadata

configs/task2b_optimizer.yaml

configs/task2b_priority.yaml
```

Do not read private competition rows.

---

# 19. No stale placeholders

Phase 29 must reject:

```text
<MODEL>

TBD

TODO

TODO_MODEL

FINAL_MODEL_HERE

replace me
```

in final diagram files.

If a model field cannot be resolved:

stop.

---

# 20. DT-374 — High-level Datathon architecture

Create:

```text
high_level_datathon.mmd
high_level_datathon.svg
```

Purpose:

show the whole Datathon in one view.

A judge should understand the system within roughly 20–30 seconds.

---

# 21. High-level architecture — top flow

Required conceptual flow:

```text
Private competition data
        ↓
Data validation + preprocessing
        ↓
┌──────────────────────────────────────────┐
│ Task1 │ Task2A │ Task2B                  │
│ ML    │ ML     │ Optimization            │
└──────────────────────────────────────────┘
        ↓
Validation / quality gates
        ↓
Final models + CSVs + policy + docs
        ↓
Competition submission / Waypoint planning support
```

---

# 22. High-level — input layer

Use conceptual data groups:

```text
Historical deliveries/orders

Historical route legs

Planned Task1 test inputs

Calendar/reference tables

Vehicle/fleet references

Task2B S1 scenario
```

Avoid showing every raw column.

Do not expose real sample records.

---

# 23. High-level — shared processing

Show a small shared layer for:

```text
schema validation

time/calendar parsing

reference joins

data-quality checks

private-data boundary
```

Do not falsely imply all tasks use identical feature engineering.

---

# 24. High-level — Task 1 branch

Show:

```text
label construction
→ feature engineering
→ final service model
→ final late-risk model/calibration
→ submission_task1.csv
```

Model labels must be actual frozen names.

---

# 25. High-level — Task 2A branch

Show:

```text
demand-history construction
→ weekly aggregation
→ time-aware features
→ final 10-week forecasting model(s)
→ submission_task2a.csv
```

---

# 26. High-level — Task 2B branch

Show:

```text
scenario/fleet
→ compatibility
→ trip-time calculation
→ hard constraints + WayLoom priority
→ CP-SAT
→ validator/checker
→ submission_task2b.csv + policy
```

---

# 27. High-level — final deliverables

Include:

```text
saved final models

TeamName_FinalNotebook.ipynb

architecture diagrams

preprocessing document

submission_task1.csv

submission_task2a.csv

submission_task2b.csv

Task2B written policy

demo video

AI-tool disclosure
```

Do not show unfinished Phase30+ outputs as completed if they do not yet exist.

The diagram may label:

```text
final submission package
```

as the downstream target.

---

# 28. High-level — optional extensions

Optional later capabilities may appear as dashed boxes only:

```text
Explainability

Deferral reasoner

Uncertainty

Synthetic integration contract
```

Do not place them on the required path from data to official submissions.

---

# 29. DT-375 — Task 1 pipeline diagram

Create:

```text
task1_pipeline.mmd
task1_pipeline.svg
```

The diagram must accurately explain:

```text
label construction

prediction-time feature boundary

validation

two final prediction outputs

saved-model inference
```

---

# 30. Task 1 — historical label flow

Required:

```text
deliveries_train
+
route_legs_train

join:
(route_id, seq_in_route)
↔
(route_id, seq)
```

Then:

```text
actual historical route events
→ label construction
```

Use high-level labels rather than every column.

---

# 31. Task 1 — service label

Show:

```text
service_start
=
max(actual arrival, window_open)
```

Then:

```text
service_minutes
=
leave_outlet_time - service_start
```

Add concise note:

```text
early waiting is not service
```

---

# 32. Task 1 — late label

Show:

```text
late_flag = 1
only if
arrival_time > window_close_time
```

Add:

```text
arrival exactly at close = on time
```

This boundary is important.

---

# 33. Task 1 — prediction-time boundary

Show a clear boundary:

```text
Available for prediction:
planned context + static/reference + valid historical aggregates

Training-only actual outcome fields:
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

Training-only fields must not point into the final feature/model node.

---

# 34. Task 1 — feature layer

Use the ACTUAL final feature-registry groups.

Possible examples only:

```text
planned timing/slack

planned travel/distance

order size

outlet/brand/district

dock/access/reference service allowance

route position/workload

calendar context

chronology-safe history
```

Do not include a group unless final model schema actually uses it.

---

# 35. Task 1 — validation layer

Show frozen validation concept:

```text
time/leakage-safe validation contract
```

Do not draw random split if the frozen implementation is time-aware.

Do not add test-set tuning.

---

# 36. Task 1 — final model nodes

Use actual manifest values.

Example formatting:

```text
Service-time model
<actual family>
<actual config id>
```

```text
Late-risk classifier
<actual family>
<actual config id>
```

Then actual:

```text
calibration
```

if present.

No imaginary calibrator.

---

# 37. Task 1 — service post-processing

If final service inference uses:

```text
nonnegative clipping
```

or another frozen rule:

show it after the raw model.

If no postprocessing:

do not add it.

---

# 38. Task 1 — output

Show exact official output:

```text
submission_task1.csv

delivery_id
pred_service_min
pred_late_prob
```

Do not include:

```text
SHAP
uncertainty bands
raw margins
```

inside the official CSV.

---

# 39. Task 1 — optional post-hoc branch

If Phase25 exists and is complete:

may show dashed:

```text
Post-hoc explainability
```

If Phase27 exists:

may show dashed:

```text
Unofficial service uncertainty
```

These branches must not feed back into the frozen model.

---

# 40. DT-376 — Task 2A forecasting diagram

Create:

```text
task2a_forecasting.mmd
task2a_forecasting.svg
```

Required story:

```text
construct demand history
→ aggregate weekly
→ engineer chronological features
→ validate across 10-week forecasting horizon
→ fit frozen final models
→ forecast future 10 weeks
→ apply frozen output constraints
→ official CSV
```

---

# 41. Task 2A — demand history inputs

Show both official sources:

```text
deliveries_train

task1_test_inputs
```

This is non-negotiable.

Do not show Task1 model predictions as Task2A history.

---

# 42. Task 2A — unique-order demand rule

Show:

```text
each unique order counted once
```

including:

```text
deferred

not_run / never dispatched
```

because they still represent demand.

---

# 43. Task 2A — requested week

Show:

```text
requested order_date
→ calendar
→ ISO year/week
```

Do not aggregate by actual delivery completion week.

---

# 44. Task 2A — weekly grain

Show:

```text
depot + brand + ISO week
```

with target:

```text
total_volume_m3
chilled_volume_m3
```

Only Fresh has chilled demand.

---

# 45. Task 2A — feature layer

Read actual final feature config.

Possible high-level groups:

```text
lags
rolling history
calendar/week
depot/brand
forecast horizon
trend/seasonality proxies
```

Only show implemented feature families.

Do not add deep learning/Prophet/ARIMA simply because they are common forecasting methods.

---

# 46. Task 2A — validation

Show:

```text
rolling time-aware validation
10-week horizon
no future leakage
```

This differentiates the forecasting pipeline from a random ML split.

---

# 47. Task 2A — final architecture

Read the exact frozen strategy.

Diagram must say whether final inference is:

```text
global model

direct horizon models

separate target models

brand-specific models

or other frozen strategy
```

Do not simplify in a way that changes semantics.

High-level is fine, but must still be true.

---

# 48. Task 2A — post-processing

Show frozen constraints:

```text
volumes >= 0

chilled <= total

Style chilled = 0

Tech chilled = 0
```

Do not add a capacity-conversion step.

Official Task2A asks for volume forecasts only.

---

# 49. Task 2A — output

Show:

```text
submission_task2a.csv

row_id
pred_total_volume_m3
pred_chilled_volume_m3
```

No unofficial uncertainty fields.

---

# 50. Task 2A — optional uncertainty

If Phase27 is complete:

may show dashed:

```text
unofficial forecast uncertainty
```

It must branch from the frozen point forecast and remain outside the official CSV.

---

# 51. DT-377 — Task 2B optimization diagram

Create:

```text
task2b_optimization.mmd
task2b_optimization.svg
```

This diagram must clearly communicate:

```text
official feasibility
vs
WayLoom prioritization
```

They must not be visually merged into one rule list.

---

# 52. Task 2B — inputs

Show:

```text
S1 peak-day orders

S1 fleet status

vehicle reference

district travel reference

service allowance reference
```

Then:

```text
available Peliyagoda fleet
```

Workshop vehicles excluded.

---

# 53. Task 2B — compatibility

Show order×vehicle compatibility for:

```text
reefer requirement

van_only

home depot

whole-order weight fit

whole-order volume fit
```

Do not imply compatibility itself allocates an order.

---

# 54. Task 2B — exact trip time

Show:

```text
trip minutes
=
outbound district travel
+
inter-stop travel × (number_of_orders - 1)
+
sum(service allowance by brand+dock_type)
```

and:

```text
no return leg
```

---

# 55. Task 2B — seven official hard rule groups

Show all:

```text
1. same brand + district per trip

2. chilled -> reefer

3. van_only -> van

4. home depot match

5. whole order / no split

6. both weight + volume capacity

7. max two trips per vehicle
   + Fresh <=270 min
   + Style+Tech <=480 min
```

Do not invent an eighth hard rule.

---

# 56. Task 2B — WayLoom priority

Separate box:

```text
WayLoom lexicographic policy
```

with the nine stages:

```text
1 MAX served orders
2 MAX previous-deferred served
3 MAX waiting-days served
4 MAX low-flexibility served
5 MAX Fresh chilled served
6 MAX Fresh served
7A MIN avoidable reefer-van use
7B MIN avoidable reefer use
7C MIN avoidable van use
```

Label:

```text
engineering policy
not organizer rule
```

---

# 57. Task 2B — solver

Show actual:

```text
OR-Tools CP-SAT
```

and:

```text
sequential lexicographic solve
```

All nine stages must have been proven optimal before freeze.

Do not draw a weighted single-objective solver if implementation is sequential lexicographic.

---

# 58. Task 2B — freeze gate

Show:

```text
solution audit

determinism evidence

config hashes

allocation/trip-summary hashes

FROZEN allocation
```

Keep high-level.

Do not expose private hashes themselves.

---

# 59. Task 2B — independent validation

Show two validation layers:

```text
WayLoom independent validator
```

and:

```text
organizer check_allocation.py
```

Label organizer checker:

```text
feasibility only
```

Do not say:

```text
optimality validated by organizer
```

---

# 60. Task 2B — final output

Show:

```text
submission_task2b.csv
```

with:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

Also:

```text
written prioritization policy
```

as a separate output.

---

# 61. Task 2B — optional reasoner

If Phase26 is complete:

may show dashed:

```text
Post-hoc Explainable Deferral Reasoner
```

It must branch from the frozen allocation.

It must not point into the optimizer as if it generated the official allocation.

---

# 62. DT-378 — Proposed deployment approach

Create:

```text
proposed_deployment.mmd
proposed_deployment.svg
```

This must be labelled:

```text
PROPOSED DEPLOYMENT
```

not:

```text
current production deployment
```

---

# 63. Recommended proposed deployment

Use a conservative architecture that matches the project:

```text
Secure internal data source
        ↓
Scheduled batch orchestration
        ↓
Validated preprocessing / feature pipelines
        ↓
┌──────────────────────────────┐
│ Task1 saved-model inference  │
│ Task2A saved-model inference │
│ Task2B CP-SAT optimization   │
└──────────────────────────────┘
        ↓
Validation gates
        ↓
Versioned artifacts
        ↓
Internal planning / decision support
```

---

# 64. Deployment — model artifact layer

Show a controlled model-artifact location containing:

```text
Task1 service model

Task1 late model/calibrator

Task2A final model(s)
```

Task2B is an optimizer/config artifact, not a trained model.

Do not depict Task2B as a neural network/model if it is CP-SAT.

---

# 65. Deployment — validation gates

Show:

```text
schema validation

inference contract validation

Task2B independent feasibility validator

organizer checker for competition export

hash/version checks
```

Do not claim organizer checker is a production service.

It is a competition validation tool.

---

# 66. Deployment — data/privacy boundary

Show a secure boundary around:

```text
raw/internal data

intermediate derivatives

model execution

optimizer execution
```

Outputs may be:

```text
internal planning views

controlled submission artifacts

aggregate documentation
```

No public row-level competition data.

---

# 67. Deployment — external services

Official rules prohibit proprietary API-based modelling/preprocessing.

Therefore proposed deployment should show:

```text
local/internal model inference
```

not:

```text
external prediction API
```

unless describing a future internal wrapper around the locally owned model.

Even then:
label it optional internal serving.

---

# 68. Deployment — optional integration

If Phase28 is implemented:

show dashed:

```text
Optional synthetic/internal integration contract
```

Do not connect:

```text
public internet
→ private competition records
```

Do not make FastAPI required for Datathon scoring.

---

# 69. Deployment — scheduling

Recommended label:

```text
Batch scheduler / orchestrator
```

Do not claim:

```text
Airflow
Prefect
Kubernetes CronJob
AWS Step Functions
```

unless actually proposed/implemented deliberately.

Generic proposed component is safer.

---

# 70. Deployment — storage

Recommended generic labels:

```text
secure data store

versioned model/artifact store

validated output store
```

Do not name a cloud vendor unless there is a concrete project decision.

The official requirement is proposed deployment approach, not vendor selection.

---

# 71. Diagram visual language

Use consistent shapes:

```text
cylinder:
data/storage

rectangle:
processing

rounded rectangle:
model/solver

diamond:
validation/gate only if useful

document:
output

dashed border:
optional/future
```

Mermaid shape syntax may vary.

Consistency matters more than decorative complexity.

---

# 72. Diagram color semantics

If colors are used, recommended categories:

```text
Data
Processing
Models
Optimization
Validation
Outputs
Optional
```

Do not use color alone to communicate privacy or optionality.

Also use labels/borders.

---

# 73. Readability requirements

Every diagram should be readable:

```text
on laptop at normal zoom

inside final notebook

inside a PDF/page

in a demo video
```

Avoid more than ~2 lines of text per node where possible.

Use a legend rather than repeating long explanations.

---

# 74. Text density rule

The architecture diagrams are not the preprocessing document.

Detailed cleaning rationale belongs in Phase 30.

Phase 29 should show:

```text
what flows where

what is transformed

what final components exist

what constraints/gates apply
```

not every transformation expression.

Exceptions:

Task1 label boundaries
Task2B trip-time formula
Task2B hard-rule summary

because these are central architectural semantics.

---

# 75. Architecture README

Create:

```text
docs/architecture/README.md
```

Required sections:

```text
Purpose

Official requirement

Diagram index

Architecture source of truth

Legend

Required core vs optional extensions

Rendering

Privacy

Validation status
```

Link/mention the five stable SVG filenames.

---

# 76. Diagram source metadata

At the top of each Mermaid source, add comments such as:

```text
%% diagram_id: task1_pipeline
%% phase: 29
%% status: final
%% private_data: false
```

Optional:

```text
%% source_contracts: Phase04,06,07,09,10
```

Do not include local paths.

---

# 77. Diagram validation script

Create:

```text
scripts/validate_architecture_docs.py
```

It should be deterministic and read-only.

Return nonzero exit code on blocking mismatch.

---

# 78. Validation — required files

Require exactly the five core diagram sources and five core SVGs.

Do not silently skip a diagram because its renderer failed.

---

# 79. Validation — placeholders

Reject case-insensitive:

```text
TODO
TBD
PLACEHOLDER
<MODEL>
<ACTUAL MODEL>
FINAL_MODEL_HERE
```

Allow only if they appear inside a test fixture explicitly marked as such.

---

# 80. Validation — official output schemas

Verify diagrams/docs contain exact final output fields.

Task1:

```text
delivery_id
pred_service_min
pred_late_prob
```

Task2A:

```text
row_id
pred_total_volume_m3
pred_chilled_volume_m3
```

Task2B:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

---

# 81. Validation — Task1 semantics

Require Task1 architecture to express:

```text
service_start max(arrival, open)

service minutes = leave - service_start

late uses strict >
```

The validator can use normalized semantic tokens rather than exact prose.

---

# 82. Validation — Task1 leakage boundary

Require:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

to be labelled training-only/label-only, not prediction inputs.

If diagram arrows route them into final inference features:

manual review must fail.

Automated tests can at least require a leakage-boundary statement.

---

# 83. Validation — Task2A history

Require mention of:

```text
deliveries_train

task1_test_inputs

unique order once

deferred/not_run demand included

requested order date/week

ISO year/week

10 weeks
```

---

# 84. Validation — Task2B semantics

Require:

```text
same brand + district

reefer

van_only

home depot

whole order

weight + volume

two trips

270

480

CP-SAT

feasibility-only checker
```

Require policy and hard-rule concepts to appear separately.

---

# 85. Validation — deployment claims

Require:

```text
proposed
```

in title/body.

Reject claims such as:

```text
live production

deployed to AWS

production Kubernetes
```

unless an explicit safe project record supports them.

Reject:

```text
Hackathon integration required
```

---

# 86. Privacy validator

Scan:

```text
*.mmd
*.svg
README.md
architecture_manifest.yaml
```

for:

```text
C:\Users\

/home/<username>/

real ID-like strings from known private identifier sets if a safe pattern
validator exists

secrets/API keys

reports/private row-level text
```

No private rows are needed to validate general path leakage.

---

# 87. SVG export validation

For every required SVG:

```text
exists

size > 0

contains <svg

contains viewBox or explicit dimensions

contains no remote asset dependency

contains no unrendered Mermaid source

contains no placeholder text
```

---

# 88. Source/export freshness

If feasible, `render_architecture_diagrams.py` should render deterministically and compare/update exports.

A validation hash map may record:

```text
source SHA256
SVG SHA256
renderer version
```

in a build manifest.

Do not require identical SVG bytes across different renderer versions if the renderer injects metadata.

Instead require source/export build metadata from the current run.

---

# 89. Human visual review

Automated tests cannot fully guarantee diagram quality.

Required human checklist:

```text
all text readable

no clipping

no overlapping nodes

arrows point correctly

diagram can be explained in <60 seconds

Task1/2A/2B have distinct logic

no unexplained acronyms

proposed deployment clearly future-facing

privacy boundary visible
```

---

# 90. Test — architecture manifest

Create:

```text
tests/test_architecture_manifest.py
```

Required assertions:

```text
actual final Task1 families resolved

actual late calibration resolved

actual service postprocess resolved

actual Task2A strategy resolved

actual Task2A model family/families resolved

Task2A horizon = 10

Task2B solver correct

Task2B 9 objective levels exact

deployment status = proposed

Hackathon integration required = false

no private paths
```

---

# 91. Test — architecture contract

Create:

```text
tests/test_architecture_contract.py
```

Test semantic requirements per diagram.

Do not test only file existence.

Fail if critical official semantics are absent.

---

# 92. Test — privacy

Create:

```text
tests/test_architecture_privacy.py
```

Scan all tracked Phase29 assets.

Require:

```text
no real IDs

no local user paths

no secrets

no raw row dumps

no public private report content
```

---

# 93. Test — exports

Create:

```text
tests/test_architecture_exports.py
```

Require five valid SVGs.

If PNGs exist:

validate dimensions > sensible minimum, for example:

```text
width >= 1200
```

or repository-approved equivalent.

Do not make optional PNG presence a blocker unless final packaging explicitly requires it.

---

# 94. Edge case — final model differs from earlier plan

Diagram follows:

```text
final frozen config
```

not:

```text
old master-plan example
```

If the contract narrative is stale:

note it for documentation cleanup later.

Do not alter the model.

---

# 95. Edge case — ensemble

If final model is an ensemble:

show:

```text
Final service ensemble
```

and optionally list component families.

Do not draw every component if it makes the diagram unreadable.

Manifest should still resolve the actual strategy.

---

# 96. Edge case — many horizon models

If Task2A uses 10 direct horizon models:

show:

```text
Direct horizon models h=1…10
```

rather than ten separate model boxes.

---

# 97. Edge case — no lateness calibrator

If frozen final calibration is:

```text
none/raw
```

do not draw a calibrator.

Use:

```text
probability output
```

or omit the extra node.

---

# 98. Edge case — derived chilled forecast

If chilled output is constrained/derived from another model:

draw the derivation/postprocessing accurately.

Do not invent a separate model.

---

# 99. Edge case — Phase25/26/27/28 not done

Core architecture remains complete.

Do not show optional work as completed.

The required architecture depends on Phases 4–24.

---

# 100. Edge case — optional phases complete later

If optional phases are completed after Phase29:

do not automatically rewrite the required five diagrams.

Only add dashed optional extensions if they materially help the final story and do not create clutter.

Any edit requires rerunning Phase29 validation.

---

# 101. Edge case — renderer unavailable

Required response:

```text
MERMAID SOURCES: PASS
STATIC SVG EXPORTS: PENDING
PHASE29 STATUS: NOT YET PASS
```

Provide exact render command.

Do not mark final until SVGs exist and are visually checked.

---

# 102. Edge case — SVG stale

If Mermaid source changes after SVG generation:

regenerate SVG.

Do not ship a diagram whose source and static export describe different architectures.

---

# 103. Edge case — architecture exposes private path

If SVG embeds a source tooltip/path:

remove/redact it before finalization.

Do not accept because "it's only metadata."

---

# 104. Edge case — over-dense Task2B diagram

Use Mermaid subgraphs:

```text
Inputs
Feasibility
Priority
Solver
Validation
Outputs
```

Do not reduce font to unreadable size.

High-level readability beats showing every solver variable.

---

# 105. Edge case — deployment architecture overclaims

If only local scripts exist:

show:

```text
Proposed scheduled internal batch execution
```

not:

```text
Production microservices cluster
```

The official requirement asks for proposed deployment, so future-facing generic components are acceptable if clearly proposed.

---

# 106. Definition of Done

Phase 29 is complete only when:

- [ ] DT-374 PASS
- [ ] DT-375 PASS
- [ ] DT-376 PASS
- [ ] DT-377 PASS
- [ ] DT-378 PASS
- [ ] official architecture deliverable requirement documented
- [ ] architecture manifest generated from final safe configs/metadata
- [ ] no model-family placeholders
- [ ] high-level Mermaid exists
- [ ] high-level SVG exists
- [ ] Task1 Mermaid exists
- [ ] Task1 SVG exists
- [ ] Task2A Mermaid exists
- [ ] Task2A SVG exists
- [ ] Task2B Mermaid exists
- [ ] Task2B SVG exists
- [ ] proposed-deployment Mermaid exists
- [ ] proposed-deployment SVG exists
- [ ] Task1 label formulas accurate
- [ ] Task1 leakage boundary accurate
- [ ] Task1 final models/calibration/postprocessing accurate
- [ ] Task1 output schema exact
- [ ] Task2A history uses both required sources
- [ ] Task2A includes deferred/not_run demand
- [ ] Task2A requested-week/ISO logic accurate
- [ ] Task2A 10-week time-aware validation accurate
- [ ] Task2A final model strategy accurate
- [ ] Task2A postprocessing accurate
- [ ] Task2A output schema exact
- [ ] Task2B inputs accurate
- [ ] Task2B trip formula accurate
- [ ] Task2B no-return rule accurate
- [ ] all seven Task2B hard rule groups present
- [ ] Phase21 policy exact and labelled WayLoom policy
- [ ] CP-SAT / lexicographic architecture accurate
- [ ] freeze/audit/validator/checker flow accurate
- [ ] organizer checker labelled feasibility-only
- [ ] Task2B output schema exact
- [ ] deployment labelled proposed
- [ ] deployment keeps data/model execution private/internal
- [ ] no proprietary external modelling/preprocessing API shown
- [ ] Hackathon integration not required
- [ ] optional phases shown only as optional
- [ ] no private identifiers/rows/paths
- [ ] no placeholders
- [ ] diagrams visually readable
- [ ] targeted Phase29 tests pass
- [ ] relevant frozen-pipeline regressions pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] `git diff --check` passes
- [ ] frozen Datathon artifacts unchanged
- [ ] independent Phase29 review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 29 STATUS: PASS
ARCHITECTURE DIAGRAMS: FINAL
FROZEN DATATHON PIPELINES: UNCHANGED
READY FOR PHASE 30: YES
```

---

# 107. Git workflow

Recommended:

```bash
git checkout main
git pull
git checkout -b docs/phase-29-architecture
```

Recommended commits:

```text
docs(architecture): add final architecture manifest
docs(architecture): add Datathon and Task1 diagrams
docs(architecture): add Task2A and Task2B diagrams
docs(architecture): add proposed deployment diagram
test(architecture): validate architecture accuracy and privacy
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run:

```bash
pytest -q   tests/test_architecture_manifest.py   tests/test_architecture_contract.py   tests/test_architecture_privacy.py   tests/test_architecture_exports.py

pytest -q

python -m pip check
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

---

# 108. Recommended local commands

Build safe manifest:

```bash
python scripts/build_architecture_manifest.py
```

Render if the implementation provides the renderer wrapper:

```bash
python scripts/render_architecture_diagrams.py   --source-dir docs/architecture   --output-dir docs/architecture
```

Validate:

```bash
python scripts/validate_architecture_docs.py   --architecture-dir docs/architecture   --manifest docs/architecture/architecture_manifest.yaml
```

Use the actual implemented CLI if different.

---

# 109. Recommended sanitized validation output

Target:

```text
WAYLOOM — PHASE 29 ARCHITECTURE DOCUMENTATION

ARCHITECTURE MANIFEST                   : PASS

DT-374 HIGH-LEVEL DATATHON             : PASS
DT-375 TASK1 PIPELINE                   : PASS
DT-376 TASK2A FORECASTING               : PASS
DT-377 TASK2B OPTIMIZATION              : PASS
DT-378 PROPOSED DEPLOYMENT              : PASS

FINAL TASK1 MODEL LABELS                : PASS
FINAL TASK2A MODEL LABELS               : PASS
TASK2B CP-SAT/POLICY                    : PASS

TASK1 LABEL/LEAKAGE SEMANTICS           : PASS
TASK2A HISTORY/10-WEEK SEMANTICS        : PASS
TASK2B HARD-RULE SEMANTICS              : PASS

ORGANIZER CHECKER = FEASIBILITY ONLY    : PASS
DEPLOYMENT STATUS = PROPOSED            : PASS
HACKATHON INTEGRATION REQUIRED          : NO

SVG EXPORTS                             : 5/5 PASS
VISUAL READABILITY                      : PASS
PRIVATE DATA IN DIAGRAMS                : NO

FROZEN DATATHON ARTIFACTS CHANGED       : NO

PHASE 29                                : PASS
READY FOR PHASE 30                      : YES
```

---

# 110. Recommended model

Phase 29 is documentation-heavy but cross-phase critical.

A wrong diagram can misrepresent:

- final model family;
- label construction;
- leakage boundary;
- forecast history;
- Task2B official constraints;
- policy semantics;
- deployment status.

Recommended:

```text
GPT-5.6 Sol
Reasoning: High
```

for implementation.

Use the same for the fresh independent review.

---

# 111. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 29 only.

PHASE:
Architecture Documentation

TASK RANGE:
DT-374 through DT-378

EXECUTION MODE:
DOCUMENTATION-FIRST.
READ-ONLY AGAINST FROZEN PIPELINES.
DIAGRAMS MUST MATCH IMPLEMENTATION.
NO MODEL/OUTPUT CHANGES.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 30.

==================================================
MISSION
==================================================

Produce the competition-required architecture diagrams for the finalized
WayLoom Datathon implementation.

Required tasks:

DT-374 Create high-level Datathon architecture
DT-375 Create Task 1 pipeline diagram
DT-376 Create Task 2A forecasting diagram
DT-377 Create Task 2B optimization diagram
DT-378 Show proposed deployment approach

The official Challenge Booklet requires architecture diagrams that show:

- models
- preprocessing pipeline
- proposed deployment approach

and says high-level diagrams are sufficient.

The diagrams must reflect the actual frozen implementation from Phases 4–24.

Do NOT redesign the project while documenting it.

==================================================
SOURCE AUTHORITY
==================================================

Use this hierarchy:

1. Official Challenge Booklet
2. WAYLOOM_DATATHON_MASTER_PLAN.md
3. Frozen phase contracts and final configs/artifacts
4. Tracked implementation
5. Tests/evidence
6. Engineering presentation choices

If a diagram conflicts with the implementation:
IMPLEMENTATION/FROZEN CONTRACT WINS.

If implementation conflicts with official rules:
STOP and report the upstream blocker.

Do not silently "fix" architecture by drawing what should have been built.

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - Phase 29
4. Official Challenge Booklet
   - Datathon tasks
   - Datathon deliverables
   - judging criteria
5. PHASE_04_COMPETITION_CONTRACT.md
6. PHASE_06_COMPETITION_CONTRACT.md
7. PHASE_07_COMPETITION_CONTRACT.md
8. PHASE_09_COMPETITION_CONTRACT.md
9. PHASE_10_COMPETITION_CONTRACT.md
10. PHASE_11_COMPETITION_CONTRACT.md
11. PHASE_13_COMPETITION_CONTRACT.md
12. PHASE_14_COMPETITION_CONTRACT.md
13. PHASE_16_COMPETITION_CONTRACT.md
14. PHASE_17_COMPETITION_CONTRACT.md
15. PHASE_18_COMPETITION_CONTRACT.md
16. PHASE_19_COMPETITION_CONTRACT.md
17. PHASE_20_COMPETITION_CONTRACT.md
18. PHASE_21_COMPETITION_CONTRACT.md
19. PHASE_22_COMPETITION_CONTRACT.md
20. PHASE_23_COMPETITION_CONTRACT.md
21. PHASE_24_COMPETITION_CONTRACT.md
22. PHASE_29_COMPETITION_CONTRACT.md

Inspect actual repository source/configs needed to determine:

Task1 final model family/config
Task1 late calibration
Task1 service postprocessing
Task1 frozen feature/inference pipeline

Task2A final model family/config
Task2A direct/multi-horizon strategy
Task2A frozen postprocessing

Task2B solver engine
Task2B hard constraints
Task2B frozen objective hierarchy
Task2B validator/checker/export flow

Do NOT inspect private row-level competition data.

==================================================
OFFICIAL DELIVERABLE REQUIREMENT
==================================================

The official Datathon deliverables require:

"Architecture diagrams. Show your models, preprocessing pipeline, and proposed
deployment approach. High-level diagrams are sufficient."

The official demo also asks teams to explain:

model architecture
preprocessing
label construction
challenges encountered

Judging includes:

Model and architecture implementation: 25%

Therefore Phase29 diagrams must be:

accurate
readable
high-level
submission-ready
reusable in the final notebook/demo/package

Do not overload diagrams with implementation trivia.

==================================================
PRECONDITIONS
==================================================

Require:

Phase 10 Task1 final pipeline:
FROZEN / validated

Phase 17 Task2A final pipeline:
FROZEN / validated

Phase 24 Task2B final output/policy:
FINAL / validated

Final model configs available.

Task2B frozen optimizer/validator architecture available.

If the actual final model family cannot be resolved from tracked metadata:
STOP.

If any diagram would require guessing a model name:
STOP.

==================================================
FROZEN ARTIFACTS — MUST NOT CHANGE
==================================================

Do NOT modify:

Task1 models/configs/submission

Task2A models/configs/submission

Task2B frozen allocation/configs/submission/policy

Phase22/23 evidence

Phase24 final outputs

Architecture work is documentation only.

==================================================
CREATE / UPDATE
==================================================

Create/update:

docs/architecture/README.md

docs/architecture/architecture_manifest.yaml

docs/architecture/high_level_datathon.mmd
docs/architecture/task1_pipeline.mmd
docs/architecture/task2a_forecasting.mmd
docs/architecture/task2b_optimization.mmd
docs/architecture/proposed_deployment.mmd

docs/architecture/high_level_datathon.svg
docs/architecture/task1_pipeline.svg
docs/architecture/task2a_forecasting.svg
docs/architecture/task2b_optimization.svg
docs/architecture/proposed_deployment.svg

Optional PNG exports if required for notebook/video use:

docs/architecture/png/high_level_datathon.png
docs/architecture/png/task1_pipeline.png
docs/architecture/png/task2a_forecasting.png
docs/architecture/png/task2b_optimization.png
docs/architecture/png/proposed_deployment.png

Create:

scripts/build_architecture_manifest.py
scripts/validate_architecture_docs.py

Optional if a renderer is available:

scripts/render_architecture_diagrams.py

Create tests:

tests/test_architecture_manifest.py
tests/test_architecture_contract.py
tests/test_architecture_privacy.py
tests/test_architecture_exports.py

Do NOT start Phase30 preprocessing documentation.

==================================================
DIAGRAM FORMAT
==================================================

Use Mermaid source files as the version-controlled diagram source.

Preferred:

flowchart LR
or
flowchart TD

depending on readability.

Static SVG exports are required for final Phase29 PASS because they are
portable and readable outside a Mermaid-aware editor.

PNG exports are optional.

Do NOT embed external images, web fonts or remote resources.

Do NOT include proprietary font files.

==================================================
RENDERER RULE
==================================================

If Mermaid CLI or another approved local renderer is already available:
render SVG automatically.

If no renderer is available:

do NOT make broad dependency upgrades that risk the ML environment.

Return:
STATIC EXPORT PENDING

and give the human the exact local rendering step.

Phase29 cannot be marked fully complete until readable static diagrams exist.

==================================================
ARCHITECTURE MANIFEST
==================================================

Create:

docs/architecture/architecture_manifest.yaml

This is the machine-checkable source of diagram facts.

Record safe metadata only.

Recommended structure:

version: 1

task1:
  service_model_family: <read from frozen config/metadata>
  service_config_id: <safe tracked id>
  late_model_family: <read from frozen config/metadata>
  late_config_id: <safe tracked id>
  late_calibration: <frozen value>
  service_postprocessing: <frozen value>
  output_columns:
    - delivery_id
    - pred_service_min
    - pred_late_prob

task2a:
  final_strategy: <read from frozen config>
  total_model_family: <actual value>
  chilled_model_family_or_strategy: <actual value>
  horizon_weeks: 10
  output_columns:
    - row_id
    - pred_total_volume_m3
    - pred_chilled_volume_m3

task2b:
  solver: OR-Tools CP-SAT
  max_trips_per_vehicle: 2
  fresh_minutes_limit: 270
  style_tech_minutes_limit: 480
  objective_levels:
    - ...
  output_columns:
    - scenario
    - order_ref
    - outlet_id
    - decision
    - vehicle_id
    - trip_id

deployment:
  status: proposed
  default_mode: private_local_batch
  hackathon_integration_required: false

Do not include private row counts/IDs or absolute local paths.

==================================================
NO HARDCODED STALE MODEL FAMILY
==================================================

Never assume:

CatBoost
LightGBM
XGBoost
RandomForest

unless the frozen final config actually says so.

Architecture labels must be populated from final config/metadata.

Tests should catch generic placeholders such as:

<MODEL>
TODO
TBD
FINAL_MODEL_HERE

and fail.

==================================================
DT-374 — HIGH-LEVEL DATATHON ARCHITECTURE
==================================================

Create:

docs/architecture/high_level_datathon.mmd
docs/architecture/high_level_datathon.svg

Goal:

show the entire Datathon as one understandable system.

Required top-level flow:

PRIVATE COMPETITION DATA
        ↓
DATA CONTRACT / VALIDATION
        ↓
THREE ANALYTICAL BRANCHES
        ├── Task1 service + lateness prediction
        ├── Task2A 10-week demand forecasting
        └── Task2B peak-day optimization
        ↓
VALIDATED FINAL ARTIFACTS
        ↓
COMPETITION DELIVERABLES / DECISION SUPPORT

==================================================
HIGH-LEVEL REQUIRED COMPONENTS
==================================================

Show:

Data sources / references

Shared:
schema validation
time/calendar/reference preparation
privacy boundary

Task1:
label construction
feature pipeline
service model
late classifier/calibration
submission_task1.csv

Task2A:
demand history construction
weekly aggregation/features
10-week forecast model(s)
submission_task2a.csv

Task2B:
scenario/fleet inputs
compatibility
trip-time calculation
priority policy
CP-SAT optimizer
independent validator + organizer checker
submission_task2b.csv + policy

Final deliverables:
saved models
final notebook
architecture/preprocessing docs
three submissions
Task2B policy
demo
AI disclosure

Keep optional Phase25–28 extensions outside the required core.

If shown:
use dashed "optional" boxes.

==================================================
HIGH-LEVEL PRIVACY BOUNDARY
==================================================

Visually distinguish:

private competition data / derivatives

from:

safe submission/docs outputs

Do not show:
real IDs
private report filenames if unnecessary
local user directories

A small lock/boundary label is sufficient.

==================================================
DT-375 — TASK 1 PIPELINE DIAGRAM
==================================================

Create:

docs/architecture/task1_pipeline.mmd
docs/architecture/task1_pipeline.svg

Required flow:

HISTORICAL INPUTS
        ↓
TRAIN LABEL CONSTRUCTION
        ↓
PREDICTION-TIME FEATURE PIPELINE
        ↓
FROZEN VALIDATION
        ↓
FINAL SERVICE MODEL
        +
FINAL LATE CLASSIFIER
        ↓
CALIBRATION / POSTPROCESSING AS ACTUALLY IMPLEMENTED
        ↓
SAVED MODELS
        ↓
TEST INFERENCE
        ↓
submission_task1.csv

==================================================
TASK1 LABEL LOGIC — MUST APPEAR
==================================================

Show concise official label formulas:

service_start
=
max(actual arrival, window opening)

service_minutes
=
leave_outlet_time - service_start

late_flag
=
1 only when actual arrival > window_close_time

Add:

early waiting ≠ service

arrival exactly at close ≠ late

Do not turn the diagram into a full preprocessing document.

==================================================
TASK1 PREDICTION-TIME BOUNDARY
==================================================

Show:

planned departure/travel/arrival context available

actual journey/handling fields:
training-label/history only

Explicitly mark leakage boundary.

At minimum exclude direct current predictors:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

Do not list every feature.

Show semantic groups instead.

==================================================
TASK1 FEATURE LAYER
==================================================

Use high-level feature groups based on the ACTUAL frozen registry, such as:

planned timing/slack

planned travel/distance

order size

brand/outlet/district context

dock/access/reference allowance

route position/workload

calendar context

chronology-safe historical aggregates

Only include groups actually enabled in the final feature set.

Do not draw unused feature groups.

==================================================
TASK1 FINAL MODELS
==================================================

Diagram labels must include actual final model family/config from frozen metadata.

For example:

Service model:
<actual family>

Late classifier:
<actual family>

Calibration:
<actual method or none>

Service postprocess:
<actual method or none>

Never guess.

==================================================
TASK1 OUTPUT
==================================================

Show exact official columns:

delivery_id
pred_service_min
pred_late_prob

No Phase25 SHAP or Phase27 uncertainty field in the official output.

Optional explainability may be shown as a dashed post-hoc branch only if implemented.

==================================================
DT-376 — TASK 2A FORECASTING DIAGRAM
==================================================

Create:

docs/architecture/task2a_forecasting.mmd
docs/architecture/task2a_forecasting.svg

Required flow:

deliveries_train
+
task1_test_inputs
        ↓
UNIQUE ORDER DEMAND HISTORY
        ↓
requested order_date
        ↓
calendar ISO year/week
        ↓
depot + brand + week aggregation
        ↓
forecast features
        ↓
10-week rolling validation
        ↓
frozen final model(s)
        ↓
10-week inference
        ↓
business-rule postprocessing
        ↓
submission_task2a.csv

==================================================
TASK2A HISTORY RULES — MUST APPEAR
==================================================

Show concise official rules:

count each unique order once

include deferred/not_run demand

assign to requested order week

use calendar ISO year/week

only Fresh has chilled demand

These are important because they define demand, not service execution.

==================================================
TASK2A FEATURE LAYER
==================================================

Show actual final feature families only.

Possible examples:

lags

rolling history

calendar/week features

brand/depot context

direct horizon feature

Only include if actually in frozen final schema.

Do not draw unimplemented deep learning/Prophet/etc.

==================================================
TASK2A VALIDATION
==================================================

Diagram must show:

rolling / time-aware validation

10-week horizon

no future leakage

Do not depict random train/test splitting if not used.

==================================================
TASK2A FINAL MODELS
==================================================

Read actual final strategy from:

configs/task2a_final_models.yaml
and associated runtime metadata.

Diagram must accurately state whether the implementation uses:

separate total/chilled models
per-horizon/direct model strategy
one global model with horizon feature
brand-specific model(s)
or another frozen architecture

Do not guess.

==================================================
TASK2A POSTPROCESSING
==================================================

Show frozen rules:

nonnegative volumes

pred_chilled_volume_m3 <= pred_total_volume_m3

Style chilled = 0

Tech chilled = 0

Only if these are actually implemented exactly as frozen.

==================================================
TASK2A OUTPUT
==================================================

Exact columns:

row_id
pred_total_volume_m3
pred_chilled_volume_m3

Optional Phase27 uncertainty:
dashed diagnostic branch only if implemented.

Never place uncertainty columns inside official CSV node.

==================================================
DT-377 — TASK 2B OPTIMIZATION DIAGRAM
==================================================

Create:

docs/architecture/task2b_optimization.mmd
docs/architecture/task2b_optimization.svg

Required flow:

S1 orders
+
scenario fleet status
+
vehicle reference
+
district travel
+
service allowance
        ↓
SCENARIO / USABLE FLEET
        ↓
ORDER × VEHICLE COMPATIBILITY
        ↓
EXACT TRIP-TIME MODEL
        ↓
HARD CONSTRAINT MODEL
        +
FROZEN WAYLOOM PRIORITY
        ↓
LEXICOGRAPHIC CP-SAT OPTIMIZATION
        ↓
SOLUTION AUDIT / FREEZE
        ↓
INDEPENDENT PHASE23 VALIDATOR
        ↓
ORGANIZER check_allocation.py
        ↓
OFFICIAL TEMPLATE EXPORT
        ↓
submission_task2b.csv
+
written policy

==================================================
TASK2B HARD RULES — MUST APPEAR
==================================================

Show the seven official rule groups:

1. same brand + district per trip

2. chilled -> reefer

3. van_only -> van

4. home depot match

5. whole order / no split

6. weight + volume capacity

7. max 2 trips per vehicle and:
   Fresh <=270 minutes
   Style+Tech <=480 minutes

Do not add:

delivery-window rule
fuel rule
return journey
Task1 late probability
Task2A forecast dependency

These are not Task2B hard constraints.

==================================================
TASK2B TRIP TIME — MUST APPEAR
==================================================

Show concise formula:

trip minutes
=
depot-to-district outbound
+
inter-stop × (orders - 1)
+
sum service allowance

No return leg.

Service allowance:
brand + dock_type

Do not overfill diagram with examples.

==================================================
TASK2B POLICY — MUST APPEAR
==================================================

Clearly separate:

OFFICIAL HARD FEASIBILITY

from:

WAYLOOM SOFT PRIORITY

Show the frozen lexicographic order:

1 MAX served orders
2 MAX previous-deferred served
3 MAX waiting-days served
4 MAX low-flexibility served
5 MAX Fresh chilled served
6 MAX Fresh served
7A MIN avoidable reefer-van
7B MIN avoidable reefer
7C MIN avoidable van

Label:
WayLoom policy — not organizer priority.

==================================================
TASK2B VALIDATION / FREEZE
==================================================

Show:

all objective stages must be OPTIMAL

deterministic freeze evidence

independent solution audit

Phase23 solver-neutral validator

organizer checker:
feasibility only

Do not label organizer checker as:
optimality checker.

==================================================
TASK2B OUTPUT
==================================================

Exact official columns:

scenario
order_ref
outlet_id
decision
vehicle_id
trip_id

Written policy:
separate document

Optional Phase26 deferral reasoner:
dashed post-hoc branch only if implemented.

It must not appear inside the official optimizer path as if it decided the
frozen allocation.

==================================================
DT-378 — PROPOSED DEPLOYMENT APPROACH
==================================================

Create:

docs/architecture/proposed_deployment.mmd
docs/architecture/proposed_deployment.svg

This is a PROPOSED deployment, not a claim of production deployment.

Preferred baseline architecture:

SECURE INTERNAL DATA SOURCES
        ↓
SCHEDULED / BATCH LOCAL PIPELINE
        ↓
VALIDATION + FEATURE BUILD
        ↓
TASK1 + TASK2A SAVED MODEL INFERENCE
        +
TASK2B LOCAL OPTIMIZER
        ↓
VALIDATION / CHECKER GATES
        ↓
VERSIONED OUTPUT ARTIFACTS
        ↓
WAYPOINT PLANNING / DECISION SUPPORT

==================================================
DEPLOYMENT COMPONENTS
==================================================

Show:

Private data store / warehouse

Batch orchestration

Preprocessing/feature layer

Model artifact store

Task1 inference worker

Task2A forecast worker

Task2B optimizer worker

Validation gates

Artifact/report store

Internal decision-support consumer

Monitoring/logging:
aggregate technical status only

Optional internal API:
only if clearly marked proposed/optional

==================================================
DEPLOYMENT PRIVACY
==================================================

Show:

competition/private data remains in a secure environment

no proprietary external modelling/preprocessing API

no public publication of private rows

model/solver execution local/internal

official competition submissions generated as controlled artifacts

Do not claim:
cloud service actually exists
production monitoring actually deployed
Kubernetes/AWS/Azure/GCP components exist
unless tracked implementation confirms them.

Generic "internal scheduler" / "secure object store" is acceptable as a
proposed future deployment concept if labelled proposed.

==================================================
PHASE28 RELATIONSHIP
==================================================

The master Phase29 dependency is Phases4–24.

Therefore proposed deployment must not depend on Phase28.

If Phase28 is implemented, you may show:

OPTIONAL SYNTHETIC / INTERNAL INTEGRATION CONTRACT

as a dashed extension.

Do not make FastAPI part of the required competition architecture.

==================================================
DIAGRAM VISUAL STYLE
==================================================

Use one consistent visual grammar.

Recommended semantic classes:

DATA
PROCESS
MODEL
OPTIMIZER
VALIDATION
OUTPUT
OPTIONAL
PRIVACY_BOUNDARY

Keep:

short labels
limited text
clear arrows
left-to-right or top-to-bottom flow

Avoid:
dense paragraphs
tiny fonts
crossing arrows
decorative icons that add no information

High-level diagrams are sufficient.

==================================================
COLOR / ACCESSIBILITY
==================================================

If Mermaid theme/colors are used:

ensure readable contrast.

Do not rely on color alone.

Use labels/shapes in addition to color.

SVG must remain understandable in grayscale.

Do not embed a dark-only diagram unless final package background is known.

==================================================
PRIVATE DATA SAFETY
==================================================

Architecture docs must not contain:

real delivery_id
real order_ref
real outlet_id
real vehicle_id
raw row values
private output counts not already approved for public documentation
absolute C:\Users\... paths
reports/private row-level references
secrets
API keys

File/path names that are part of repository architecture are acceptable when
needed, but prefer conceptual labels over local filesystem details.

==================================================
ARCHITECTURE README
==================================================

Create:

docs/architecture/README.md

Required sections:

1. Purpose
2. Official requirement
3. Diagram index
4. Source-of-truth policy
5. Diagram legend
6. Required vs optional architecture
7. Rendering instructions
8. Privacy note
9. Validation status

Index all five diagrams.

==================================================
DIAGRAM METADATA
==================================================

For every .mmd, include comments or companion manifest metadata with:

diagram_id
title
phase
source contracts
status = final
contains_private_data = false
last_validated_commit if available

Do not include private hashes.

==================================================
VALIDATION SCRIPT
==================================================

Create:

scripts/validate_architecture_docs.py

It must fail closed on:

missing diagram source

missing SVG export

zero-byte SVG

unrendered Mermaid syntax error where renderer validation is available

placeholder tokens

stale/unsupported model names

missing exact official output columns

missing Task1 label boundary

missing Task2A demand-history rules

missing Task2B seven rules

missing Task2B policy separation

missing proposed deployment status

private identifier patterns

absolute user path leakage

claim that Datathon-Hackathon integration is required

claim that organizer checker proves optimality

==================================================
ARCHITECTURE MANIFEST BUILDER
==================================================

Create:

scripts/build_architecture_manifest.py

It should read SAFE tracked config/metadata only.

Do not access:
raw rows
interim private rows
reports/private rows

Use:

configs/task1_final_models.yaml

safe Task1 model metadata

configs/task2a_final_models.yaml

safe Task2A model metadata

configs/task2b_optimizer.yaml

configs/task2b_priority.yaml

safe public/task config constants

If safe model metadata files contain no private rows, they may be read.

Output:

docs/architecture/architecture_manifest.yaml

Do not include:
absolute paths
private hashes
private record counts

==================================================
TESTS — MANIFEST
==================================================

Create:

tests/test_architecture_manifest.py

Test:

Task1 final model family resolved

Task1 calibration resolved

Task1 output columns exact

Task2A strategy resolved

Task2A output columns exact

Task2B solver is CP-SAT / actual frozen solver

Task2B objective tier count/order exact

deployment status == proposed

hackathon_integration_required == false

no absolute local path

no private row IDs

==================================================
TESTS — ARCHITECTURE CONTRACT
==================================================

Create:

tests/test_architecture_contract.py

Test every diagram source contains required semantic elements.

Task1:
label formulas/boundaries
prediction-time boundary
actual final model labels
exact output columns

Task2A:
both demand sources
unique-order history
requested-week aggregation
10-week validation
actual model strategy
postprocessing
exact output columns

Task2B:
input references
compatibility
trip formula/no return
seven rules
WayLoom priority
CP-SAT
freeze
independent validator
organizer checker feasibility-only
official output columns

Deployment:
status proposed
private/local
no required Hackathon dependency

High-level:
all three branches
deliverables

==================================================
TESTS — PRIVACY
==================================================

Create:

tests/test_architecture_privacy.py

Scan:

.mmd
.svg
README
manifest

Reject:

absolute Windows user path regex

/home/<user> style local path where inappropriate

real/private ID pattern list if known safely

data row dumps

reports/private content snippets

secrets

URLs to external private storage

"No private data" should be testable without opening private datasets.

==================================================
TESTS — EXPORTS
==================================================

Create:

tests/test_architecture_exports.py

Require:

all 5 SVGs exist

all nonempty

contain <svg

contain viewBox or width/height

no external http(s) asset refs except safe SVG namespace declarations

no embedded raster/base64 unless intentionally approved

no placeholder text

consistent titles

Optional PNG:
if produced, file exists and has sensible dimensions.

==================================================
RENDERING
==================================================

If Mermaid CLI exists:

render:

mmdc -i source.mmd -o output.svg

Use a deterministic theme/config where practical.

If CLI interface differs:
use actual installed interface.

Do not download remote fonts/assets.

If no mmdc:
return exact manual/local render instructions.

==================================================
READABILITY GATE
==================================================

Human should visually inspect SVGs at:

100% desktop

fit-to-page

projected/video scale

Check:

text readable

arrows unambiguous

no clipped labels

no overlapping nodes

no tiny footnotes

Task2B diagram not excessively dense

If one diagram is too dense:
split internally with subgraphs,
but still produce one required Task2B architecture diagram file.

==================================================
FINAL DIAGRAM NAMING
==================================================

Use stable names:

high_level_datathon.svg
task1_pipeline.svg
task2a_forecasting.svg
task2b_optimization.svg
proposed_deployment.svg

Do not rename late in packaging.

==================================================
DOWNSTREAM REUSE
==================================================

Phase29 outputs will later support:

Phase31 final notebook

Phase37 evidence

Phase38 demo video

Phase40 final folder

Phase41 final validation

Therefore diagrams should be final enough to reuse without rewriting.

Do not include ephemeral experiment numbers.

==================================================
EDGE CASE — MODEL FAMILY CHANGED
==================================================

If final config differs from an older contract:

diagram follows FINAL CONFIG.

Record a non-blocking note:
older contract examples are historical.

Do not edit frozen model selection.

==================================================
EDGE CASE — MULTIPLE MODEL FILES
==================================================

If final Task1/Task2A uses an ensemble or multiple horizon models:

diagram should show the architecture accurately at a high level:

"10 direct horizon models"

or:

"ensemble"

rather than drawing dozens of individual files.

Manifest may store safe model count.

==================================================
EDGE CASE — CALIBRATOR ABSENT
==================================================

If lateness calibration is none/raw:

do not draw a calibration box suggesting one exists.

Use:

"Probability output / no additional calibrator"

or omit calibrator box according to actual implementation.

==================================================
EDGE CASE — TASK2A CHILLED STRATEGY
==================================================

If chilled is derived rather than produced by a separate model:

diagram must say so.

Do not draw a separate chilled model unless it exists.

==================================================
EDGE CASE — OPTIONAL PHASES NOT COMPLETE
==================================================

Do not block Phase29 because Phase25–28 are optional/later relative to its
master dependency.

Do not show them as required.

Optional extension boxes may be omitted entirely.

==================================================
EDGE CASE — PHASE28 IMPLEMENTED
==================================================

If a synthetic integration contract exists:

deployment diagram may add a dashed box:

"Optional synthetic/internal integration contract"

Do not show:
public real-data API
required Hackathon dependency

==================================================
EDGE CASE — NO STATIC RENDERER
==================================================

Do not claim Phase29 PASS with only Mermaid sources if final judges cannot
reliably render Mermaid.

Return:

STATIC EXPORT PENDING

and ask human to export SVG locally.

After static files exist:
rerun validation.

==================================================
EDGE CASE — ARCHITECTURE DISCOVERS CONTRADICTION
==================================================

Examples:

Task1 final config references a model artifact that does not exist

Task2A diagram facts conflict with final config

Task2B policy config order differs from Phase21 frozen policy

Do NOT "fix the diagram."

STOP and report the upstream phase mismatch.

==================================================
SAFE TEST LOOP
==================================================

Run:

pytest -q \
  tests/test_architecture_manifest.py \
  tests/test_architecture_contract.py \
  tests/test_architecture_privacy.py \
  tests/test_architecture_exports.py

Then relevant frozen Task1/Task2A/Task2B config/inference tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run training.
Do not rerun Task2B optimizer.
Do not inspect private rows.

==================================================
LOCAL BUILD COMMANDS
==================================================

Expected:

python scripts/build_architecture_manifest.py

Then render if supported:

python scripts/render_architecture_diagrams.py \
  --source-dir docs/architecture \
  --output-dir docs/architecture

Then:

python scripts/validate_architecture_docs.py \
  --architecture-dir docs/architecture \
  --manifest docs/architecture/architecture_manifest.yaml

Use the actual implemented CLI if it differs.

==================================================
STOP CONDITIONS
==================================================

STOP if:

final Task1 model family cannot be resolved

final Task2A architecture cannot be resolved

Task2B solver/policy facts cannot be resolved

diagram would require guessing

diagram contradicts official Task1 labels

diagram includes actual fields as Task1 predictors

diagram counts Task2A demand incorrectly

diagram omits deferred/not_run demand rule

diagram shows random Task2A validation when frozen validation is time-aware

diagram imports Task1/Task2A predictions as Task2B hard constraints

diagram adds Task2B return journey

diagram labels WayLoom priority as official

diagram says organizer checker proves optimality

deployment diagram claims unimplemented production infrastructure as live

deployment makes Hackathon integration required

private row IDs/data appear

official frozen artifacts change

static diagrams are unreadable

SVGs are missing for final completion

tests fail

pip check fails

Phase30 work introduced

==================================================
DEFINITION OF DONE
==================================================

Require:

DT-374 PASS
DT-375 PASS
DT-376 PASS
DT-377 PASS
DT-378 PASS

All 5 Mermaid sources exist.

All 5 SVG exports exist.

Architecture manifest matches final configs.

High-level diagram shows all three tasks and final deliverables.

Task1 diagram shows correct label construction and leakage boundary.

Task1 diagram uses actual final model names/config.

Task2A diagram shows exact demand-history construction and 10-week workflow.

Task2A diagram uses actual final strategy.

Task2B diagram shows exact trip formula, 7 hard rules, frozen policy,
optimizer, validator/checker, final output.

Proposed deployment is clearly proposed.

Deployment remains private/internal.

Hackathon integration marked optional/not required.

No private identifiers.

No unsupported production claims.

No placeholders.

All diagrams readable.

Architecture validation script PASS.

Targeted tests PASS.

Full safe suite PASS.

pip check PASS.

Independent fresh review PASS.

==================================================
GIT WORKFLOW
==================================================

Recommended branch:

git checkout main
git pull
git checkout -b docs/phase-29-architecture

Recommended commits:

docs(architecture): add final Datathon architecture manifest
docs(architecture): add high-level and Task1 diagrams
docs(architecture): add Task2A and Task2B diagrams
docs(architecture): add proposed deployment diagram
test(architecture): validate diagram accuracy and privacy

Before commit:

git status
git diff
git diff --check

Run tests.

Do not stage private data/reports.

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-374 READY
DT-375 READY
DT-376 READY
DT-377 READY
DT-378 READY

Official architecture deliverable satisfied.

Actual final models named correctly.

No stale model names.

Task1 label formula exact.

Task1 leakage boundary correct.

Task2A demand history exact.

Task2A horizon = 10 weeks.

Task2B exact 7 rule groups.

Task2B policy exact.

Organizer checker feasibility-only.

Deployment proposed/not live.

Hackathon integration not required.

All SVGs readable.

No private data.

Frozen outputs unchanged.

No Phase30 work.

==================================================
RETURN ONLY
==================================================

PHASE:
29 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-374 READY / FAIL
DT-375 READY / FAIL
DT-376 READY / FAIL
DT-377 READY / FAIL
DT-378 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

ARCHITECTURE MANIFEST:
PASS / FAIL

HIGH-LEVEL DATATHON DIAGRAM:
PASS / FAIL

TASK1 PIPELINE DIAGRAM:
PASS / FAIL

TASK2A FORECASTING DIAGRAM:
PASS / FAIL

TASK2B OPTIMIZATION DIAGRAM:
PASS / FAIL

PROPOSED DEPLOYMENT DIAGRAM:
PASS / FAIL

ACTUAL FINAL MODEL NAMES VERIFIED:
PASS / FAIL

OFFICIAL OUTPUT SCHEMAS VERIFIED:
PASS / FAIL

TASK1 LABEL/LEAKAGE ACCURACY:
PASS / FAIL

TASK2A HISTORY/VALIDATION ACCURACY:
PASS / FAIL

TASK2B HARD RULE/POLICY ACCURACY:
PASS / FAIL

ORGANIZER CHECKER LABELLED FEASIBILITY-ONLY:
PASS / FAIL

DEPLOYMENT CLEARLY PROPOSED:
PASS / FAIL

HACKATHON INTEGRATION OPTIONAL:
PASS / FAIL

STATIC SVG EXPORTS:
PASS / PENDING / FAIL

PRIVATE DATA IN DIAGRAMS:
MUST BE NO

FROZEN DATATHON ARTIFACTS CHANGED:
MUST BE NO

TEST RESULTS:
...

PIP CHECK:
PASS / FAIL

GIT DIFF CHECK:
PASS / FAIL

HUMAN VISUAL REVIEW REQUIRED:
YES

Print exact visual-review checklist and any rendering command.

PHASE 29 STATUS:
AWAITING VISUAL/INDEPENDENT REVIEW

READY FOR PHASE 30:
NO

Then STOP.

Do not start Phase30.

```

---

# 112. Independent Phase 29 review prompt

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon PHASE 29.

PHASE:
Architecture Documentation

TASK RANGE:
DT-374 through DT-378

REVIEW TYPE:
FRESH SESSION
READ-ONLY
CROSS-PHASE CONSISTENCY AUDIT

Do NOT implement Phase30.
Do NOT modify diagrams initially.
Do NOT retrain models.
Do NOT rerun Task2B optimization.
Do NOT inspect private row-level competition data.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase29
4. Official Challenge Booklet — Datathon tasks/deliverables/judging
5. PHASE_04_COMPETITION_CONTRACT.md
6. PHASE_06_COMPETITION_CONTRACT.md
7. PHASE_07_COMPETITION_CONTRACT.md
8. PHASE_09_COMPETITION_CONTRACT.md
9. PHASE_10_COMPETITION_CONTRACT.md
10. PHASE_11_COMPETITION_CONTRACT.md
11. PHASE_13_COMPETITION_CONTRACT.md
12. PHASE_14_COMPETITION_CONTRACT.md
13. PHASE_16_COMPETITION_CONTRACT.md
14. PHASE_17_COMPETITION_CONTRACT.md
15. PHASE_18_COMPETITION_CONTRACT.md
16. PHASE_19_COMPETITION_CONTRACT.md
17. PHASE_20_COMPETITION_CONTRACT.md
18. PHASE_21_COMPETITION_CONTRACT.md
19. PHASE_22_COMPETITION_CONTRACT.md
20. PHASE_23_COMPETITION_CONTRACT.md
21. PHASE_24_COMPETITION_CONTRACT.md
22. PHASE_29_COMPETITION_CONTRACT.md

Inspect actual final safe configs/metadata and implementation.

Inspect:

docs/architecture/README.md
docs/architecture/architecture_manifest.yaml

docs/architecture/high_level_datathon.mmd
docs/architecture/task1_pipeline.mmd
docs/architecture/task2a_forecasting.mmd
docs/architecture/task2b_optimization.mmd
docs/architecture/proposed_deployment.mmd

all corresponding SVGs

scripts/build_architecture_manifest.py
scripts/validate_architecture_docs.py
scripts/render_architecture_diagrams.py if present

tests/test_architecture_manifest.py
tests/test_architecture_contract.py
tests/test_architecture_privacy.py
tests/test_architecture_exports.py

==================================================
OFFICIAL REQUIREMENT
==================================================

Confirm Phase29 satisfies the official deliverable:

Architecture diagrams showing:
models
preprocessing pipeline
proposed deployment approach

High-level diagrams are sufficient.

Confirm diagrams are appropriate for final submission/demo reuse.

==================================================
AUDIT DT-374
==================================================

High-level architecture must show:

private data boundary
shared validation/preparation
Task1 branch
Task2A branch
Task2B branch
validated final outputs
competition deliverables

It must not imply Task2B depends on Task1/Task2A predictions unless the actual
implementation does.

Optional phases must be visually optional.

==================================================
AUDIT DT-375
==================================================

Task1 diagram:

correct historical join/label context

service_start = max(actual arrival, window open)

service_minutes = leave - service_start

late = arrival > window_close

arrival exactly at close not late

early waiting not service

planned prediction-time context separate from actual training-only fields

actual final service model name/family

actual final late model name/family

actual calibration

actual service postprocessing

exact official output columns

No forbidden actual feature drawn as predictor.

==================================================
AUDIT DT-376
==================================================

Task2A diagram:

uses BOTH deliveries_train and task1_test_inputs

each unique order once

deferred/not_run demand included

requested order_date -> ISO year/week

depot+brand+week aggregation

actual frozen features/strategy

time-aware 10-week validation

actual final model strategy

nonnegative/postprocessing rules

Fresh-only chilled

Style/Tech chilled zero

exact official output columns

No future leakage.

==================================================
AUDIT DT-377
==================================================

Task2B diagram:

S1 + available fleet inputs

Phase19 compatibility

Phase20 exact trip formula

no return leg

service allowance brand+dock

seven official hard rule groups

Phase21 WayLoom policy separate from hard rules

exact nine objective levels

CP-SAT actual solver

all stages optimal/freeze concept

independent validator

organizer checker feasibility-only

official template export

written policy

No:
fuel rule
delivery-window hard constraint
Task1 lateness constraint
Task2A forecast constraint

==================================================
AUDIT DT-378
==================================================

Proposed deployment:

must be labelled PROPOSED.

Should show secure/private/internal processing.

Models/optimizer deployed as internal batch/local workers or the actual
proposed equivalent.

No claim of live production infrastructure not implemented.

No claim Hackathon integration required.

No proprietary external modelling/preprocessing API.

Optional Phase28 only as dashed/optional if shown.

==================================================
ACTUAL MODEL NAME AUDIT
==================================================

Compare diagram labels and manifest against:

configs/task1_final_models.yaml
safe Task1 metadata

configs/task2a_final_models.yaml
safe Task2A metadata

Task2B optimizer config

Do not accept stale model-family names from old design documents.

==================================================
PRIVACY AUDIT
==================================================

Scan architecture files for:

real IDs

absolute local paths

private row snippets

secrets

private report contents

external private URLs

Require:
none.

==================================================
VISUAL QUALITY AUDIT
==================================================

Inspect rendered SVGs.

Verify:

all 5 open successfully

no clipping

no overlapping labels

font readable

arrows clear

consistent layout

not overly dense

works at reasonable presentation scale

high-level diagram understandable in under ~30 seconds

Task diagrams understandable without reading code

proposed vs implemented distinction visible

Do not fail solely for aesthetic preference.

Fail if readability materially harms the official deliverable.

==================================================
STATIC EXPORT AUDIT
==================================================

Require:

all 5 SVGs present

nonempty

valid SVG structure

no remote asset dependencies

titles match diagram purpose

Mermaid source and export correspond.

If source changed after export:
FAIL / stale export.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_architecture_manifest.py \
  tests/test_architecture_contract.py \
  tests/test_architecture_privacy.py \
  tests/test_architecture_exports.py

Then relevant Task1/Task2A/Task2B frozen config/inference tests.

Then:

pytest -q
python -m pip check
git diff --check
git status

Do not run training/optimization/private row processing.

==================================================
RETURN
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

OFFICIAL ARCHITECTURE DELIVERABLE:
PASS / FAIL

ARCHITECTURE MANIFEST:
PASS / FAIL

HIGH-LEVEL DATATHON:
PASS / FAIL

TASK1 PIPELINE:
PASS / FAIL

TASK2A FORECASTING:
PASS / FAIL

TASK2B OPTIMIZATION:
PASS / FAIL

PROPOSED DEPLOYMENT:
PASS / FAIL

FINAL MODEL NAME PARITY:
PASS / FAIL

TASK1 LABEL PARITY:
PASS / FAIL

TASK1 LEAKAGE BOUNDARY:
PASS / FAIL

TASK2A HISTORY PARITY:
PASS / FAIL

TASK2A VALIDATION PARITY:
PASS / FAIL

TASK2B HARD RULE PARITY:
PASS / FAIL

TASK2B POLICY PARITY:
PASS / FAIL

ORGANIZER CHECKER SEMANTICS:
PASS / FAIL

DEPLOYMENT CLAIM ACCURACY:
PASS / FAIL

HACKATHON INTEGRATION OPTIONAL:
PASS / FAIL

STATIC SVG EXPORTS:
PASS / FAIL

VISUAL READABILITY:
PASS / FAIL

PRIVACY:
PASS / FAIL

FROZEN ARTIFACTS:
UNCHANGED / CHANGED

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

DT-374: PASS/FAIL
DT-375: PASS/FAIL
DT-376: PASS/FAIL
DT-377: PASS/FAIL
DT-378: PASS/FAIL

PHASE 29 INDEPENDENT REVIEW:
PASS / FAIL

ARCHITECTURE DIAGRAMS:
FINAL / INCOMPLETE

FROZEN DATATHON PIPELINES:
UNCHANGED / CHANGED

READY FOR PHASE 30:
YES / NO

If PASS:

PHASE 29 INDEPENDENT REVIEW: PASS
ARCHITECTURE DIAGRAMS: FINAL
FROZEN DATATHON PIPELINES: UNCHANGED
BLOCKERS: None
READY FOR PHASE 30: YES

Then STOP.

Do not start Phase30.

```

---

# 113. Completion record

```markdown
# Phase 29 Completion Record

## Tasks

- [ ] DT-374
- [ ] DT-375
- [ ] DT-376
- [ ] DT-377
- [ ] DT-378

## Files

- [ ] architecture_manifest.yaml
- [ ] high_level_datathon.mmd
- [ ] high_level_datathon.svg
- [ ] task1_pipeline.mmd
- [ ] task1_pipeline.svg
- [ ] task2a_forecasting.mmd
- [ ] task2a_forecasting.svg
- [ ] task2b_optimization.mmd
- [ ] task2b_optimization.svg
- [ ] proposed_deployment.mmd
- [ ] proposed_deployment.svg
- [ ] architecture README

## Accuracy

- [ ] Task1 actual final models
- [ ] Task1 labels
- [ ] Task1 leakage boundary
- [ ] Task2A actual final models/strategy
- [ ] Task2A history/10-week validation
- [ ] Task2B exact hard rules
- [ ] Task2B exact policy
- [ ] checker feasibility-only
- [ ] deployment proposed
- [ ] Hackathon integration optional

## Safety

- private IDs present: NO
- local private paths present: NO
- frozen artifact changes: NO

## Visual

- [ ] 5/5 SVGs
- [ ] no clipping
- [ ] readable
- [ ] consistent
- [ ] presentation-ready

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 29 STATUS: PASS / FAIL
ARCHITECTURE DIAGRAMS: FINAL / INCOMPLETE
FROZEN DATATHON PIPELINES: UNCHANGED / CHANGED
READY FOR PHASE 30: YES / NO
```

---

# 114. Final checklist

Before Phase 30:

- [ ] Exact DT-374–DT-378 coverage.
- [ ] Official architecture requirement satisfied.
- [ ] Architecture manifest generated from final configs.
- [ ] No guessed/stale model family.
- [ ] High-level Datathon diagram final.
- [ ] Task1 pipeline final.
- [ ] Task2A pipeline final.
- [ ] Task2B pipeline final.
- [ ] Proposed deployment final.
- [ ] Five static SVGs present.
- [ ] Task1 formulas exact.
- [ ] Task1 actual/prediction boundary exact.
- [ ] Task2A demand sources/rules exact.
- [ ] Task2A 10-week validation exact.
- [ ] Task2B trip-time/no-return exact.
- [ ] Task2B seven hard-rule groups exact.
- [ ] Task2B WayLoom policy exact.
- [ ] Organizer checker shown as feasibility-only.
- [ ] Deployment is clearly proposed.
- [ ] Hackathon integration is not required.
- [ ] Optional phases not shown as required.
- [ ] No private data/paths.
- [ ] No placeholder labels.
- [ ] Diagrams visually readable.
- [ ] Targeted tests pass.
- [ ] Full safe suite passes.
- [ ] `pip check` passes.
- [ ] `git diff --check` passes.
- [ ] Frozen artifacts unchanged.
- [ ] Fresh independent review passes.

Only then:

```text
PHASE 29 STATUS: PASS
ARCHITECTURE DIAGRAMS: FINAL
FROZEN DATATHON PIPELINES: UNCHANGED
READY FOR PHASE 30: YES
```
