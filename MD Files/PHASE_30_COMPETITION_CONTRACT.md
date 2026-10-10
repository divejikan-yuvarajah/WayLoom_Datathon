# PHASE 30 — Data Preprocessing Document

> **Filename:** `PHASE_30_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 30 — Preprocessing document  
> **Task range:** **DT-379 → DT-388**  
> **Task count:** **10**  
> **Phase dependency:** **Stable pipelines from Phases 4–24**  
> **Default phase priority:** **P0**  
> **Master phase gate:** Required preprocessing document accurately explains preparation, labels, cleaning, features and rationale.  
> **Execution mode:** Documentation-first and read-only against frozen pipelines.  
> **Primary deliverable:** `docs/preprocessing.md`

---

# 1. Phase 30 purpose

Phase 30 creates the official WayLoom **Data Preprocessing Document** required by the Rootcode Tech-Triathlon Datathon.

The official Challenge Booklet requires:

> **Data preprocessing document.** A brief write-up of your data preparation, label construction, data cleaning, feature engineering, and rationale.

The final notebook separately retains the executable cells used for label construction, preprocessing, training and evaluation. Therefore this document should explain the final methodology clearly without duplicating the entire notebook or codebase.

The document must answer:

```text
What data did we use?

How did we connect the datasets?

How were the Task 1 labels constructed?

What cleaning and validation rules were applied?

Which final features were used and why?

How did we prevent leakage?

How were the models validated?

Why were the final models/strategies selected?

How was Task 2A demand history and forecasting prepared?

How was Task 2B converted into a legal optimization problem?
```

---

# 2. Finalized Phase 30 master inventory

The finalized WayLoom master task inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-379** | [O] | P0 | Core data/model pipelines stable | Document all input datasets |
| [ ] | **DT-380** | [O] | P0 | Stable pipelines from Phases 4–24 | Document joins |
| [ ] | **DT-381** | [O] | P0 | Stable pipelines from Phases 4–24 | Document Task 1 labels |
| [ ] | **DT-382** | [O] | P0 | Stable pipelines from Phases 4–24 | Document cleaning decisions |
| [ ] | **DT-383** | [O] | P0 | Stable pipelines from Phases 4–24 | Document feature engineering |
| [ ] | **DT-384** | [O] | P0 | Stable pipelines from Phases 4–24 | Document leakage prevention |
| [ ] | **DT-385** | [O] | P0 | Stable pipelines from Phases 4–24 | Document validation strategy |
| [ ] | **DT-386** | [O] | P0 | Stable pipelines from Phases 4–24 | Document model choice rationale |
| [ ] | **DT-387** | [O] | P0 | Stable pipelines from Phases 4–24 | Document forecasting methodology |
| [ ] | **DT-388** | [O] | P0 | Stable pipelines from Phases 4–24 | Document Task 2B preparation |

**Expected Phase 30 tasks:** 10  
**Missing tasks allowed:** 0  
**Phase complete:** [ ]  
**READY FOR PHASE 31:** NO

---

# 3. Official requirements relevant to Phase 30

The official Datathon deliverables require:

```text
Architecture diagrams

Data preprocessing document

Saved final model files

Final notebook retaining:
label construction
preprocessing
training
evaluation

Peak-day allocation + written policy

Task1 and Task2A prediction CSVs

3–5 minute demo

AI tool disclosure
```

The demo is expected to explain:

```text
model architecture

preprocessing

label construction

challenges encountered
```

The judging criteria allocate:

```text
20%:
Data wrangling and label construction

25%:
Model and architecture implementation
```

Phase 30 directly supports both.

---

# 4. What the official document must contain

The booklet explicitly names:

```text
data preparation

label construction

data cleaning

feature engineering

rationale
```

The finalized WayLoom master inventory expands that into ten concrete Phase 30 tasks:

```text
datasets

joins

labels

cleaning

features

leakage

validation

model rationale

forecast methodology

Task2B preparation
```

Phase 30 must cover all ten without inventing content beyond the implemented solution.

---

# 5. Source-of-truth hierarchy

Use this order:

```text
Official Challenge Booklet
        ↓
WAYLOOM_DATATHON_MASTER_PLAN.md
        ↓
final/frozen phase contracts
        ↓
final configs and safe model metadata
        ↓
feature registries / schema definitions
        ↓
tracked implementation
        ↓
tests / sanitized evidence
        ↓
competition-facing prose
```

If an old design note differs from final implementation:

```text
final implementation wins
```

If final implementation conflicts with an official rule:

```text
STOP
```

Do not solve implementation bugs with prose.

---

# 6. Preconditions

Before Phase 30 passes, require:

```text
Phase10:
Task1 final models/inference frozen

Phase17:
Task2A final models/inference frozen

Phase24:
Task2B allocation/output/policy final

Phase29:
architecture ideally final and available for cross-reference
```

Require final safe metadata for:

```text
Task1 feature set

Task1 service model

Task1 late model

Task1 calibration

Task1 post-processing

Task2A final feature strategy

Task2A final model strategy

Task2A post-processing

Task2B scenario/compatibility/trip/policy/solver
```

If these cannot be resolved:

do not guess.

---

# 7. Frozen artifact rule

This is a documentation phase.

Do not modify:

```text
configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

configs/task2a_final_models.yaml
Task2A final runtime/model artifacts
outputs/submission_task2a.csv

data/interim/task2b_final_allocation.csv
data/interim/task2b_final_trip_summary.csv
configs/task2b_priority.yaml
configs/task2b_optimizer.yaml
outputs/submission_task2b.csv
docs/task2b_policy.md
```

Phase 30 may read safe configs/metadata.

It must not regenerate predictions or allocations.

---

# 8. Primary outputs

Create/update:

```text
docs/preprocessing.md
```

Create machine-checkable support:

```text
docs/preprocessing_manifest.yaml

scripts/build_preprocessing_manifest.py

scripts/validate_preprocessing_doc.py

tests/test_preprocessing_manifest.py
tests/test_preprocessing_document.py
tests/test_preprocessing_privacy.py
tests/test_preprocessing_contract.py
```

Optional only if needed:

```text
docs/preprocessing_appendix.md
```

Do not create a new final notebook in Phase 30.

That is Phase 31.

---

# 9. Final document length

The official wording says:

```text
brief write-up
```

Recommended engineering target:

```text
2,500–4,500 words
```

excluding small tables, headings and optional appendix.

This is not an organizer-prescribed word limit.

Guidance:

```text
<1,500:
likely too shallow

>5,500:
likely too long for a brief competition document
```

Accuracy and completeness take priority over the exact count.

---

# 10. Recommended document structure

Use:

```text
# WayLoom Datathon — Data Preprocessing and Methodology

## 1. Purpose and scope

## 2. Input datasets

## 3. Shared data preparation and quality controls

## 4. Task 1 — Service time and lateness
### 4.1 Dataset joins
### 4.2 Label construction
### 4.3 Cleaning
### 4.4 Feature engineering
### 4.5 Leakage prevention
### 4.6 Validation
### 4.7 Final model rationale

## 5. Task 2A — Depot demand forecasting
### 5.1 Demand-history construction
### 5.2 Weekly aggregation
### 5.3 Cleaning
### 5.4 Forecast features
### 5.5 Leakage prevention
### 5.6 Rolling validation
### 5.7 Final forecasting methodology and model rationale

## 6. Task 2B — Peak-day allocation preparation
### 6.1 Scenario inputs
### 6.2 Compatibility preparation
### 6.3 Trip-time calculation
### 6.4 Hard constraints
### 6.5 WayLoom priority policy
### 6.6 Optimization, validation and export

## 7. Reproducibility and data-safety controls

## 8. Final preprocessing summary
```

Optional appendix:

```text
Final feature inventory
```

only if it improves clarity.

---

# 11. Writing standard

The document should be:

```text
brief

technical but readable

specific to WayLoom

source-grounded

final-state only

judge-friendly
```

Avoid:

```text
generic ML textbook paragraphs

long code snippets

raw DataFrame dumps

experiment diary

every rejected feature

every hyperparameter

private identifiers
```

---

# 12. Preprocessing manifest

Create:

```text
docs/preprocessing_manifest.yaml
```

It should be generated from safe tracked config/metadata.

Purpose:

- reduce documentation drift;
- make final model names/features testable;
- map each master task to a document section;
- make Phase 31 notebook documentation easier.

---

# 13. Recommended manifest structure

```yaml
version: 1

official_requirement:
  preprocessing_document: true

inputs:
  ...

joins:
  ...

task1_labels:
  ...

cleaning:
  ...

task1_features:
  ...

task1_leakage:
  ...

task1_validation:
  ...

task1_models:
  ...

task2a_history:
  ...

task2a_features:
  ...

task2a_validation:
  ...

task2a_models:
  ...

task2a_postprocessing:
  ...

task2b_inputs:
  ...

task2b_compatibility:
  ...

task2b_trip_time:
  ...

task2b_hard_rules:
  ...

task2b_priority:
  ...

task2b_validation:
  ...

outputs:
  ...

privacy:
  ...

task_mapping:
  DT-379: [...]
  ...
  DT-388: [...]
```

No private rows.

---

# 14. Manifest builder

Create:

```text
scripts/build_preprocessing_manifest.py
```

It should use only safe tracked files.

Examples:

```text
configs/dataset_manifest.yaml

Task1 feature registry/schema

configs/task1_final_models.yaml

safe Task1 metadata

configs/task2a_final_models.yaml

safe Task2A runtime/feature metadata

configs/task2b_scenario.yaml

configs/task2b_compatibility.yaml

configs/task2b_trip_time.yaml

configs/task2b_priority.yaml

configs/task2b_optimizer.yaml
```

Do not read:

```text
data/raw/**
data/interim/**
data/processed/**
reports/private/**
```

for normal manifest generation.

---

# 15. DT-379 — Document all input datasets

Create one compact source inventory.

For each actual final source, document:

```text
logical name

competition folder/type

row grain

primary/key fields

task(s)

role:
label / feature / history / reference / scenario / template

important semantic fields
```

Do not dump entire schemas.

---

# 16. Task 1 official input coverage

Official Task 1 references:

```text
Test Data/task1_test_inputs.csv
```

One row per delivery plan/order (`delivery_id`).

```text
Test Data/route_legs_test.csv
```

Matching route legs with origin/distance/planned departure/arrival context.

The final training pipeline also uses the corresponding historical Training Data sources.

Document the actual final training sources by filename from the dataset manifest.

Do not invent filenames that are not in the repository/official package.

---

# 17. Task 1 input semantics

Document the distinction:

```text
delivery/order-level data

route-leg data

general reference data

calendar/reference context where used
```

Actual historical journey fields may be used to construct training labels.

Planned route information is available for prediction-time features.

This distinction must be explicit.

---

# 18. Task 2A official input coverage

Document:

```text
deliveries_train.csv

task1_test_inputs.csv

calendar.csv

task2a_test_inputs.csv
```

Explain:

`deliveries_train` + `task1_test_inputs` form historical demand.

`task2a_test_inputs` defines the required future depot/brand/week rows.

`calendar.csv` supplies official ISO year/week mapping.

---

# 19. Task 2B official input coverage

Document:

```text
task2b_peak_day_scenarios.csv

task2b_peak_day_fleet.csv

vehicles.csv

district_travel.csv

service_allowance.csv

submission_task2b.csv template
```

Explain each source.

---

# 20. Submission templates

Document all three official templates as identity/output contracts:

```text
submission_task1.csv

submission_task2a.csv

submission_task2b.csv
```

Do not call them training data.

Explain that identifiers/order are preserved according to each task's contract.

---

# 21. Dataset inventory table

Recommended columns:

| Source | Grain | Key | Used by | Role | Important note |
|---|---|---|---|---|---|

Keep descriptions concise.

No real sample rows.

---

# 22. DT-380 — Document joins

Create a join/lookup section.

For every important join, state:

```text
left source

right source

join key

expected cardinality

purpose

guard/check
```

---

# 23. Task 1 official training join

Document exactly:

```text
deliveries_train.(route_id, seq_in_route)

↔

route_legs_train.(route_id, seq)
```

This connects each delivery/order record to its route leg.

The official Task 1 test source states that every `delivery_id` matches exactly one route leg.

Document the actual test join used by the final pipeline.

---

# 24. Task 1 join guards

Document actual safeguards such as:

```text
duplicate key rejection

missing route-leg rejection

unexpected row-count change

one-row-per-delivery preservation
```

Only include guards that exist.

Do not invent perfect-match statistics.

---

# 25. Task 2A history union

This is not merely a SQL join.

Document how:

```text
deliveries_train

+

task1_test_inputs
```

are normalized into one order-demand history.

Important:

```text
each delivery_id/order counted once
```

Do not double-count an order after combining sources.

---

# 26. Task 2A calendar mapping

Document:

```text
requested order_date
→ calendar.csv
→ iso_year / iso_week
```

This mapping defines the demand week.

Do not use actual service/completion week.

---

# 27. Task 2A reference joins

If the final implementation joins additional reference data for features:

document actual joins.

Do not add generic references that the frozen model did not use.

---

# 28. Task 2B lookups

Document:

```text
scenario fleet vehicle_id
→ vehicles.csv

order district
→ district_travel.csv

brand + dock_type
→ service_allowance.csv
```

And any actual safe scenario/reference joins.

Allocation key:

```text
order_ref
```

not `outlet_id`.

---

# 29. Join-cardinality language

Use accurate terms:

```text
one-to-one

many-to-one

lookup

union/concatenation
```

Avoid calling every relationship a join.

This improves technical clarity.

---

# 30. DT-381 — Document Task 1 labels

This is one of the most important sections because the official challenge explicitly says teams must construct the labels and document their reasoning.

---

# 31. Service label

Document:

```text
service_start
=
max(actual arrival, window opening)
```

Then:

```text
service_minutes
=
leave_outlet_time - service_start
```

Interpretation:

```text
If a vehicle arrives early, it waits.

The wait before the delivery window opens is not outlet service time.
```

---

# 32. Lateness label

Document:

```text
late_flag = 1
```

only when:

```text
actual arrival > window_close_time
```

Therefore:

```text
arrival exactly at window_close_time is not late
```

Late orders are still delivered in the supplied scenario.

---

# 33. Label boundary examples

Use synthetic/booklet-safe conceptual examples only.

Example:

```text
Window opens 07:00.
Arrival 06:50.
Unload leaves 07:18.

service_start = 07:00
service_minutes = 18
```

This is a generic constructed example, not a private competition row.

For lateness:

```text
arrival == close
→ late_flag = 0

arrival one minute after close
→ late_flag = 1
```

No real delivery IDs.

---

# 34. Label chronology

Document which fields are historical-only:

```text
actual_depart_time

actual_travel_duration_min

arrival_time

leave_outlet_time
```

They may support historical label construction/auditing.

They are not direct current prediction-time features.

---

# 35. Midnight/time normalization

The official booklet does not prescribe an exact rollover algorithm.

Document the real WayLoom implementation from Phase 4.

Use wording:

```text
WayLoom engineering decision
```

Do not call it an organizer formula.

If timestamps are date-aware:
say so.

If HH:MM normalization is used:
describe the exact logic.

---

# 36. Label validation

Document actual tests/guards:

```text
strict close boundary

early wait

nonnegative service duration

join completeness

timestamp parsing

binary late label
```

Do not report counts unless safely available and useful.

---

# 37. DT-382 — Document cleaning decisions

This section should answer:

```text
What could be wrong or inconsistent?

What did the pipeline do?

Why?
```

---

# 38. Cleaning categories

At minimum consider/document actual decisions for:

```text
schema/types

timestamps

missing values

duplicate keys

categorical domains

numeric sanity

reference coverage

invalid chronology

template identity

model-specific missing handling
```

Only include what applies.

---

# 39. Recommended cleaning table

| Risk | Task | Final behavior | Rationale | Official vs engineering |
|---|---|---|---|---|

Examples must be based on implementation.

---

# 40. Fail-closed rules

Clearly identify fields that cause the pipeline to fail when invalid.

Examples may include:

```text
missing join key

duplicate unique ID

unknown required reference

invalid official domain

missing final feature
```

Only if implemented.

---

# 41. Imputation / missing handling

Document actual behavior.

Possible cases:

```text
native model missing handling

numeric median/imputer

explicit missing category

hard failure

not applicable
```

Do not write:

"missing values were imputed"

without identifying the actual method.

---

# 42. Outlier handling

If no special outlier removal/winsorization was used:

say:

```text
No ad-hoc outlier deletion was introduced beyond the documented data-contract
checks.
```

only if true.

Do not invent outlier processing for sophistication.

---

# 43. Row dropping

If official identities must be preserved:

explain that test/template rows are not dropped.

If training rows may be excluded for documented invalid label reasons:

state actual rule.

Do not write generic:

```text
invalid rows were removed
```

without source.

---

# 44. Categorical normalization

Document actual:

```text
case normalization

whitespace handling

domain checks

unknown-category handling

native categorical model behavior

encoder behavior
```

as applicable.

---

# 45. Numeric validation

Document actual checks for:

```text
volume

weight

time durations

distance

probabilities

forecast volumes
```

Do not mix prediction-output clipping with raw data cleaning.

Separate:

```text
input preparation

model post-processing
```

---

# 46. DT-383 — Document feature engineering

Document only the **final enabled feature set** at the semantic-group level.

Use the final feature registry and model schema.

Do not present experimental/disabled features as final.

---

# 47. Task 1 feature groups

Potential groups, only if actually enabled:

```text
planned timing and window slack

planned travel / distance

order size

brand / outlet / district context

dock / parking / access context

reference service allowance

route sequence / workload

calendar / festival context

chronology-safe historical aggregates
```

The final document should use the actual groups.

---

# 48. Task 1 feature table

Recommended:

| Feature group | Final examples | Source | Prediction-time available? | Rationale |
|---|---|---|---|---|

Do not list transformed one-hot columns one by one unless necessary.

---

# 49. Task 1 important formulas

For important derived features, include formulas when they improve understanding.

Examples only if actually used:

```text
planned slack to close

planned early wait

route stop count

prior rolling service statistic
```

Use exact implementation names/formulas.

---

# 50. Historical feature rule

Any target-derived historical feature must be:

```text
chronology-safe
```

Document:

```text
past rows only
```

under the frozen training/validation construction.

Do not imply the current target is available.

---

# 51. Task 2A feature groups

Document actual final forecast features.

Potential examples:

```text
weekly lags

rolling means / sums

calendar / week-of-year

depot / brand context

forecast horizon

trend features
```

Only include enabled features.

---

# 52. Task 2A lag semantics

For each class of lag/rolling feature, explain:

```text
uses only historical weeks available before the forecast origin
```

This is central to leakage prevention.

Do not list future-looking centered rolling statistics unless they actually exist and are valid.

---

# 53. Task 2B derived optimization inputs

Do not call Task2B a feature-engineering ML pipeline.

Document derived inputs:

```text
compatibility matrix

capacity eligibility

trip grouping candidates

exact trip-time coefficients

scarcity/priority metadata

solver variable indexing
```

These prepare the constraint model.

---

# 54. DT-384 — Document leakage prevention

Create a dedicated section.

Leakage prevention is not an implied property.

It must be stated.

---

# 55. Task 1 leakage boundary

Prediction-time inputs may use:

```text
planned departure

planned travel

planned arrival

static/reference context

valid past historical aggregates
```

Current actual journey/handling fields are training-only.

Explicitly prohibit direct current:

```text
actual_depart_time

actual_travel_duration_min

arrival_time

leave_outlet_time
```

as predictors.

---

# 56. Task 1 preprocessing leakage

Where preprocessing learns state:

```text
imputer

encoder

scaler

category mapping
```

document whether it is fitted within the training split/pipeline.

Only state actual implementation.

---

# 57. Task 2A leakage boundary

Document:

```text
rolling validation respects time

future weeks do not feed earlier forecasts

lags/rolling values use past history

forecast test rows do not supply target volumes
```

---

# 58. Why task1_test_inputs is allowed in Task 2A history

Explain official logic:

```text
Each row is an order.

It contributes to known historical demand.

The demand history uses the requested order itself, not its unavailable future
delivery outcome.
```

This is an important subtlety.

---

# 59. Task 2B leakage framing

Task2B is deterministic scenario optimization.

There is no predictive train/test leakage in the same sense.

Document integrity instead:

```text
only official S1 scenario/reference inputs

no hidden future outcome

no Task1/Task2A predictions imported as hard constraints

frozen output not manually edited after optimization
```

---

# 60. DT-385 — Document validation strategy

Create a compact validation summary table:

| Task | Validation design | Key metrics/checks | Why |
|---|---|---|---|

Then explain each.

---

# 61. Task 1 validation

Read final implementation.

Document actual:

```text
split design

chronology/group controls

regression metric(s)

late-probability metric(s)

classification metric(s) if used

calibration evaluation

baseline vs advanced comparison
```

Do not invent metrics.

---

# 62. Task 1 final model selection

Document:

```text
model selection performed on the frozen validation contract
```

not test labels.

If calibration was selected:
explain the validation basis.

If service post-processing was frozen:
explain its validation/safety rationale.

---

# 63. Task 2A validation

Document:

```text
rolling / time-aware backtesting

10-week horizon

forecast origin

per-horizon/direct evaluation if applicable

total and chilled targets
```

No random CV unless truly implemented.

---

# 64. Task 2A model comparison

Briefly mention:

```text
baselines
challengers
final selection
```

No need to list all experiments.

Rationale should show why the final forecast method was selected.

---

# 65. Task 2B validation

Document three levels:

```text
solver/post-solve audit

independent Phase23 validator

organizer check_allocation.py
```

Organizer checker:

```text
feasibility only
```

not optimality.

---

# 66. DT-386 — Document model choice rationale

This section should identify actual final models.

Read them from final configs/metadata.

Do not use old plan names.

---

# 67. Task 1 service-model rationale

Explain:

```text
final model family/config

what it improved or balanced on frozen validation

why it was chosen over baseline/challengers

reproducibility considerations
```

Use only evidence that exists.

---

# 68. Task 1 lateness-model rationale

Explain:

```text
final classifier family/config

probability quality

class imbalance handling if actually used

calibration if actually used

why final probability pipeline was selected
```

Do not claim calibration if none exists.

---

# 69. Task 2A model rationale

Explain actual frozen strategy:

```text
model family/families

global/direct/horizon architecture

target-specific logic

brand logic if any

post-processing
```

Tie rationale to rolling validation.

---

# 70. Model performance wording

Preferred:

```text
selected final candidate

strongest frozen validation result

improved over baseline on the selected validation metric
```

when supported.

Avoid:

```text
best possible

state of the art

perfect

production proven
```

---

# 71. Competition restriction compliance

Briefly note:

```text
modelling/preprocessing was executed locally

no proprietary API-based modelling/preprocessing was used

competition data remained within the authorized local workflow
```

Do not overtake the separate AI disclosure.

---

# 72. DT-387 — Document forecasting methodology

This should be a self-contained Task2A methodology summary.

---

# 73. Task 2A demand history

Official:

```text
deliveries_train
+
task1_test_inputs
```

Each row/order counted once.

Include:

```text
deferred

never dispatched / not_run
```

because they still represent demand.

---

# 74. Requested order week

Official:

```text
assign demand to the week the store requested the order
```

Use:

```text
order_date
→ calendar.csv
→ iso_year
→ iso_week
```

Do not describe actual delivery week as the demand period.

---

# 75. Task 2A aggregation grain

Final weekly target grain:

```text
depot
+
brand
+
iso_year
+
iso_week
```

Forecast test requires:

```text
10 future weeks
```

for supplied depot+brand+week combinations.

---

# 76. Volume targets

Document actual target construction.

Official targets:

```text
total ordered volume in m3

chilled portion in m3
```

Only Fresh chilled.

Do not invent vehicle-capacity conversion.

---

# 77. Task 2A final feature methodology

Explain actual:

```text
lags

rolling windows

calendar features

brand/depot encoding

horizon representation
```

as applicable.

Mention deterministic feature availability at forecast origin.

---

# 78. Task 2A final model strategy

Read final configs.

Possible forms include:

```text
single global model

per-horizon/direct models

separate total/chilled models

Fresh-only chilled model

brand-specific models
```

Document actual only.

---

# 79. Task 2A post-processing

If frozen final pipeline includes:

```text
nonnegative clipping

chilled <= total

Style chilled = 0

Tech chilled = 0
```

document it.

These preserve official output semantics.

---

# 80. Task 2A output contract

Document exact official columns:

```text
row_id

pred_total_volume_m3

pred_chilled_volume_m3
```

Preserve supplied `row_id`.

Do not add uncertainty columns.

---

# 81. DT-388 — Document Task 2B preparation

Task2B is a constraint-allocation problem.

Official:

```text
no trained model required
```

State this clearly.

---

# 82. Task 2B scenario

Document:

```text
Scenario S1

Peliyagoda

festival one week away

Fresh demand rising

not payday

no monsoon

some vehicles in workshop
```

Only if useful to the method.

Do not overfocus on narrative context.

---

# 83. Task 2B usable fleet

Official:

```text
status = available
```

vehicles only.

Workshop vehicles cannot be allocated.

Document home-depot filtering.

---

# 84. Task 2B allocation key

Official:

```text
order_ref
```

because:

```text
outlet_id may appear more than once
```

This must be explicit.

---

# 85. Task 2B compatibility preparation

Document static order-vehicle feasibility:

```text
chilled -> reefer

reefer may carry ambient

van_only -> van

home depot match

whole-order weight fit

whole-order volume fit
```

This creates candidate assignments.

It does not decide final allocation.

---

# 86. Task 2B trip time

Document exact official formula:

```text
trip_minutes
=
depot_to_district_freeflow_min
+
inter_stop_freeflow_min * (number_of_orders - 1)
+
sum(service_allowance_min)
```

Where:

```text
service_allowance_min
```

is looked up by:

```text
brand + dock_type
```

Do not add return journey.

---

# 87. Task 2B official examples

Allowed because they are from the booklet:

```text
Fresh Gampaha, 3 orders:
37 + 9×2 + 15 + 15 + 16 = 101 minutes
```

Optional:

```text
Fresh Colombo, 4 street stops:
24 + 8×3 + 16×4 = 112 minutes
```

Combined:

```text
101 + 112 = 213 Fresh minutes
```

Do not replace these with private examples.

---

# 88. Task 2B seven hard rules

Document exactly:

```text
1. same brand + district per trip

2. chilled -> reefer

3. van_only -> van

4. home depot match

5. whole order / no split

6. both weight and volume capacity

7. at most two trips per vehicle
   and:
   Fresh <=270 minutes
   Style+Tech combined <=480 minutes
```

---

# 89. Task 2B no extra hard rules

Explicitly avoid/import no:

```text
fuel budget

Task1 lateness probability

delivery-window hard constraint

return journey

Task2A forecast dependency
```

unless official source says otherwise.

It does not.

---

# 90. Task 2B WayLoom priority

Separate the official rules from WayLoom's engineering policy.

Frozen order:

```text
1 MAX served_order_count

2 MAX served_previous_deferred_count

3 MAX served_waiting_days_sum

4 MAX served_low_flexibility_count

5 MAX served_fresh_chilled_count

6 MAX served_fresh_count

7A MIN avoidable_reefer_van_assignment_count

7B MIN avoidable_reefer_assignment_count

7C MIN avoidable_van_assignment_count
```

Label:

```text
WayLoom engineering policy
```

not organizer rule.

---

# 91. Task 2B optimizer preparation

Document at a high level:

```text
OR-Tools CP-SAT

binary serve/defer/assignment variables

trip-use/group constraints

capacity/time constraints

sequential lexicographic optimization

each stage proven optimal before fixing it and moving to the next
```

No need for full solver algebra in the brief preprocessing document.

---

# 92. Task 2B freeze and validation

Document:

```text
independent post-solve audit

deterministic controls

hash-bound frozen allocation

independent Phase23 validator

official check_allocation.py

final template export
```

Organizer checker:

```text
feasibility only
```

---

# 93. Task 2B output contract

Exact official fields:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

Deferred:

```text
vehicle_id blank
trip_id blank
```

Served:

```text
vehicle_id populated
trip_id 1 or 2
```

Written priority policy is a separate deliverable.

---

# 94. Shared reproducibility section

Document the controls that make the pipelines repeatable:

```text
fixed seeds where used

saved model files

frozen final configs

feature schemas

deterministic inference

schema validation

artifact hashing/freeze

official template identity preservation
```

Do not overclaim exact byte determinism for libraries/components where it was not established.

Use actual evidence.

---

# 95. Data confidentiality section

Official competition data must remain confidential.

The preprocessing document should contain methodology, not raw rows.

Do not include:

```text
real delivery_id

real order_ref

real private vehicle allocation

full test rows

private diagnostics

absolute workstation paths

secrets
```

Official booklet examples are safe to quote/paraphrase.

---

# 96. Official vs WayLoom decisions

Mark decisions clearly.

Examples of official rules:

```text
strict late boundary

Task2A history sources

Style/Tech chilled zero

Task2B trip formula

Task2B hard constraints
```

Examples of WayLoom engineering choices:

```text
feature set

midnight/time normalization

validation implementation

model family

calibration

Task2B lexicographic priority

deterministic freeze process
```

This distinction improves credibility.

---

# 97. Rationale format

For every important engineering decision, answer:

```text
Decision

Reason

Risk controlled

Validation / evidence
```

Example structure:

> **Decision:** Use rolling-origin validation for Task2A.  
> **Reason:** The task forecasts future weeks, so chronology must be preserved.  
> **Risk controlled:** Future leakage.  
> **Validation:** Final candidates were compared under the same 10-week time-aware contract.

Use actual project facts.

---

# 98. Phase 29 architecture references

If Phase 29 is final, link to:

```text
docs/architecture/high_level_datathon.svg

docs/architecture/task1_pipeline.svg

docs/architecture/task2a_forecasting.svg

docs/architecture/task2b_optimization.svg
```

The preprocessing document should not duplicate every diagram.

Use diagrams to reinforce prose.

---

# 99. Document consistency with architecture

Phase 29 and Phase 30 must agree on:

```text
final model names

Task1 label logic

Task1 leakage boundary

Task2A history

Task2A validation

Task2A final strategy

Task2B hard rules

Task2B policy

Task2B checker semantics
```

Any mismatch is blocking.

---

# 100. Preprocessing validator

Create:

```text
scripts/validate_preprocessing_doc.py
```

It should fail closed on:

```text
missing primary document

missing manifest

missing Phase30 task mapping

missing Task1 strict-late semantics

missing Task2A history rule

missing Task2B trip formula

wrong hard-rule text

stale model name

placeholder

private path/ID leakage

unsupported official claim
```

---

# 101. Placeholder scan

Reject final document strings such as:

```text
TODO

TBD

[fill here]

[MODEL NAME]

<model>

placeholder

insert metric
```

unless inside an explicit code example demonstrating the validator.

---

# 102. Final model name parity

Read:

```text
configs/task1_final_models.yaml

configs/task2a_final_models.yaml
```

and safe model metadata.

The preprocessing manifest stores final model identities.

The document must match.

Do not depend only on prose tests.

---

# 103. Feature parity validation

Compare documented final feature groups/names to:

```text
final feature registry

final model feature schema
```

All documented exact feature names must exist.

All critical enabled feature groups should be represented.

Do not require every encoded dummy column in prose.

---

# 104. Output-schema validation

Document should correctly state:

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

# 105. Test: manifest

Create:

```text
tests/test_preprocessing_manifest.py
```

Require:

```text
manifest exists

all required sections

all ten task mappings

final Task1 models resolved

final Task2A strategy resolved

Task2B solver resolved

Task2B priority order exact

no private paths

no placeholders
```

---

# 106. Test: document semantics

Create:

```text
tests/test_preprocessing_document.py
```

Test semantic coverage, not only headings.

At minimum:

```text
input inventory

joins

Task1 service label

Task1 late strict >

early wait

cleaning

features

leakage

validation

model rationale

Task2A methodology

Task2B preparation
```

---

# 107. Test: privacy

Create:

```text
tests/test_preprocessing_privacy.py
```

Scan:

```text
docs/preprocessing.md

docs/preprocessing_manifest.yaml
```

Reject:

```text
absolute local user paths

secrets

private report text

real private identifiers if safely detectable

raw row-like dumps
```

No private dataset access should be required.

---

# 108. Test: cross-contract consistency

Create:

```text
tests/test_preprocessing_contract.py
```

Compare against frozen config/constants.

Require:

```text
Task1 final model parity

Task1 calibration parity

Task2A final strategy parity

Task2B CP-SAT parity

Task2B priority order parity

official checker feasibility-only

official output schemas exact

no actual field shown as Task1 current predictor
```

---

# 109. Edge case — final feature not in registry

If final model schema contains a feature missing from the registry:

```text
STOP
```

This is a lineage/documentation defect.

Do not invent a feature description.

---

# 110. Edge case — stale contract model name

If an old Phase 9/16 contract mentions a candidate model but final config differs:

document:

```text
final config
```

Do not preserve stale candidate.

---

# 111. Edge case — no numerical metric allowed/safe

Model rationale does not require publishing exact metric values.

If values are not safely available in tracked/sanitized evidence:

use qualitative frozen-validation rationale.

Do not invent numbers.

---

# 112. Edge case — real-data cleaning counts private

Do not include counts.

Example:

```text
"The pipeline checks for duplicate delivery_id values and fails if found."
```

instead of:

```text
"0 duplicates were found"
```

unless that aggregate fact is intentionally approved for the competition document.

---

# 113. Edge case — no imputation

If the selected model natively handles missing values:

document that.

Do not add fictional median imputation.

---

# 114. Edge case — native categoricals

If final model uses native categorical handling:

document that.

Do not say:

```text
one-hot encoded
```

unless true.

---

# 115. Edge case — Task2A model strategy complex

Keep high-level but accurate.

Example:

```text
"Separate direct models were fit for each forecast horizon"
```

instead of listing each model filename.

---

# 116. Edge case — Task2B policy changed upstream

If `configs/task2b_priority.yaml` differs from the frozen Phase21 policy:

```text
STOP
```

Do not decide which is correct inside Phase30.

---

# 117. Edge case — Phase29 diagram mismatch

If architecture says one model but final config/preprocessing doc says another:

```text
STOP
```

Resolve Phase29 or upstream evidence first.

Do not let final submission contain contradictions.

---

# 118. Edge case — optional phases

Phase 25 explainability:
optional.

Phase 26 deferral reasoner:
optional.

Phase 27 uncertainty:
optional/unofficial.

Phase 28 integration:
optional / Hackathon integration not required.

Do not let them dominate the required preprocessing document.

---

# 119. Word-count quality gate

Validator should report:

```text
word_count
```

Warnings:

```text
<1500:
LIKELY TOO SHALLOW

>5500:
LIKELY TOO LONG
```

Do not automatically fail solely on the warning if completeness/briefness are acceptable.

---

# 120. Human proofread gate

After automated PASS, human must review:

```text
technical accuracy

grammar

section flow

duplicate content

table readability

official vs engineering distinctions

final model names

no unsupported claims

no private examples
```

Phase30 independent review follows after proofreading.

---

# 121. Safe execution commands

Build manifest:

```bash
python scripts/build_preprocessing_manifest.py   --output docs/preprocessing_manifest.yaml
```

Validate document:

```bash
python scripts/validate_preprocessing_doc.py   --document docs/preprocessing.md   --manifest docs/preprocessing_manifest.yaml
```

Use actual repository CLI if implemented differently.

No raw data path should be required.

---

# 122. Targeted test command

```bash
pytest -q   tests/test_preprocessing_manifest.py   tests/test_preprocessing_document.py   tests/test_preprocessing_privacy.py   tests/test_preprocessing_contract.py
```

Then:

```bash
pytest -q

python -m pip check

git diff --check

git status
```

Do not run training.

Do not rerun Task2B optimization.

---

# 123. Recommended sanitized validation output

Target:

```text
WAYLOOM — PHASE 30 PREPROCESSING DOCUMENT

PREPROCESSING MANIFEST                   : PASS

DT-379 INPUT DATASETS                    : PASS
DT-380 JOINS                             : PASS
DT-381 TASK1 LABELS                      : PASS
DT-382 CLEANING DECISIONS                : PASS
DT-383 FEATURE ENGINEERING               : PASS
DT-384 LEAKAGE PREVENTION                : PASS
DT-385 VALIDATION STRATEGY               : PASS
DT-386 MODEL CHOICE RATIONALE             : PASS
DT-387 FORECASTING METHODOLOGY           : PASS
DT-388 TASK2B PREPARATION                : PASS

TASK1 LABEL SEMANTICS                    : PASS
TASK1 LEAKAGE BOUNDARY                   : PASS
TASK2A HISTORY / 10-WEEK METHOD          : PASS
TASK2B HARD RULES / TRIP TIME            : PASS

FINAL MODEL CONFIG PARITY                : PASS
PHASE29 ARCHITECTURE CONSISTENCY         : PASS

PRIVATE DATA IN DOCUMENT                 : NO
PLACEHOLDERS                             : 0

DOCUMENT WORD COUNT                      : <n>
BRIEFNESS / READABILITY                  : PASS

FROZEN DATATHON ARTIFACTS CHANGED        : NO

PHASE 30                                 : PASS
READY FOR PHASE 31                       : YES
```

---

# 124. STOP conditions

`READY FOR PHASE 31` remains **NO** if:

- any DT-379–DT-388 requirement missing;
- official deliverable scope incomplete;
- Task1 training join wrong;
- Task1 service formula wrong;
- Task1 late boundary uses `>=`;
- early wait counted as service;
- actual journey/handling described as current direct features;
- Task2A history misses `task1_test_inputs`;
- deferred/not_run demand omitted;
- demand assigned to actual delivery week instead of requested order week;
- Task2A final model strategy guessed;
- Task2A future leakage implied;
- Task2B described as requiring trained model;
- Task2B allocation key described as outlet_id;
- Task2B return leg added;
- Task2B hard rules changed;
- Style+Tech budget separated incorrectly;
- WayLoom priority described as official;
- organizer checker described as optimality checker;
- final model names differ from config;
- feature registry mismatch;
- cleaning step invented;
- metric/performance claim invented;
- private data/path appears;
- Phase29/Phase30 contradiction unresolved;
- frozen artifact changes;
- tests fail;
- `pip check` fails;
- Phase31 work introduced.

---

# 125. Definition of Done

Phase 30 is complete only when:

- [ ] DT-379 PASS
- [ ] DT-380 PASS
- [ ] DT-381 PASS
- [ ] DT-382 PASS
- [ ] DT-383 PASS
- [ ] DT-384 PASS
- [ ] DT-385 PASS
- [ ] DT-386 PASS
- [ ] DT-387 PASS
- [ ] DT-388 PASS
- [ ] official preprocessing deliverable requirement cited accurately
- [ ] `docs/preprocessing.md` complete
- [ ] `docs/preprocessing_manifest.yaml` generated
- [ ] all final input datasets documented
- [ ] critical joins documented
- [ ] Task1 labels exact
- [ ] early-wait semantics exact
- [ ] strict late boundary exact
- [ ] time/midnight engineering handling described accurately
- [ ] cleaning rules match implementation
- [ ] no invented row dropping/imputation/outlier handling
- [ ] final Task1 feature families match registry
- [ ] final Task2A features match frozen schema
- [ ] Task2B derived optimization inputs described correctly
- [ ] Task1 leakage prevention explicit
- [ ] Task2A future leakage prevention explicit
- [ ] Task1 validation matches frozen pipeline
- [ ] Task2A rolling 10-week validation matches frozen pipeline
- [ ] Task2B validator/checker semantics correct
- [ ] final model families/configs accurate
- [ ] model rationale evidence-grounded
- [ ] Task2A history uses both official sources
- [ ] unique order once
- [ ] deferred/not_run demand included
- [ ] requested order week + ISO calendar correct
- [ ] Style/Tech chilled zero documented
- [ ] Task2B explicitly no trained model required
- [ ] Task2B `order_ref` key documented
- [ ] Task2B compatibility exact
- [ ] trip-time formula exact
- [ ] no return journey
- [ ] seven hard rule groups exact
- [ ] frozen WayLoom priority exact and labelled engineering policy
- [ ] CP-SAT / lexicographic preparation accurate
- [ ] independent validator + official checker accurate
- [ ] official checker labelled feasibility-only
- [ ] official output schemas exact
- [ ] official vs engineering decisions clearly distinguished
- [ ] no unsupported causal/performance claims
- [ ] no placeholders
- [ ] no private identifiers/rows/paths
- [ ] word count reviewed
- [ ] document readable/brief
- [ ] Phase29 architecture consistent
- [ ] targeted Phase30 tests pass
- [ ] relevant final-pipeline regression tests pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] `git diff --check` passes
- [ ] frozen artifacts unchanged
- [ ] independent Phase30 review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 30 STATUS: PASS
PREPROCESSING DOCUMENT: FINAL
FROZEN DATATHON PIPELINES: UNCHANGED
READY FOR PHASE 31: YES
```

---

# 126. Git workflow

Recommended:

```bash
git checkout main
git pull
git checkout -b docs/phase-30-preprocessing
```

Recommended commits:

```text
docs(preprocessing): add source and join inventory
docs(preprocessing): document Task1 labels features and leakage
docs(preprocessing): document Task2A forecasting methodology
docs(preprocessing): document Task2B preparation and validation
test(preprocessing): add documentation contract checks
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run:

```bash
pytest -q   tests/test_preprocessing_manifest.py   tests/test_preprocessing_document.py   tests/test_preprocessing_privacy.py   tests/test_preprocessing_contract.py

pytest -q

python -m pip check
```

Never stage:

```text
data/raw/**
data/interim/**
data/processed/**
reports/private/**
```

---

# 127. Recommended model

Phase 30 is documentation, but it is a **cross-phase factual consolidation** task.

Risks include:

- wrong Task1 label boundary;
- leakage misstatement;
- stale model names;
- incorrect Task2A history;
- undocumented future leakage;
- incorrect Task2B trip-time/rules;
- presenting WayLoom policy as official;
- inventing data-cleaning steps.

Recommended implementation:

```text
GPT-5.6 Sol
Reasoning: High
```

Recommended fresh independent review:

```text
GPT-5.6 Sol
Reasoning: High
```

---

# 128. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 30 only.

PHASE:
Data Preprocessing Document

TASK RANGE:
DT-379 through DT-388

EXECUTION MODE:
DOCUMENTATION-FIRST.
READ-ONLY AGAINST FROZEN PIPELINES.
SOURCE-GROUNDED.
NO MODEL / DATA / SUBMISSION CHANGES.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 31.

==================================================
MISSION
==================================================

Create the competition-required WayLoom Datathon data preprocessing document.

Required master tasks:

DT-379 Document all input datasets
DT-380 Document joins
DT-381 Document Task 1 labels
DT-382 Document cleaning decisions
DT-383 Document feature engineering
DT-384 Document leakage prevention
DT-385 Document validation strategy
DT-386 Document model choice rationale
DT-387 Document forecasting methodology
DT-388 Document Task 2B preparation

The official Challenge Booklet requires:

"A brief write-up of your data preparation, label construction,
data cleaning, feature engineering, and rationale."

The document must reflect the FINAL implemented pipelines.

Do not rewrite history.
Do not invent steps.
Do not document proposed transformations as if they were used.
Do not expose private row-level competition data.

==================================================
SOURCE AUTHORITY
==================================================

Use:

1. Official Challenge Booklet
2. WAYLOOM_DATATHON_MASTER_PLAN.md
3. Frozen phase contracts
4. Final configs / safe metadata / feature registries
5. Tracked implementation
6. Tests / safe validation evidence
7. Engineering prose choices

If an older contract conflicts with the final frozen config:
FINAL CONFIG / IMPLEMENTATION WINS.

If final implementation conflicts with an official rule:
STOP and report the upstream blocker.

Do not silently correct the implementation inside the document.

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - Phase 30
4. Official Challenge Booklet
   - Datathon Task 1
   - Task 2A
   - Task 2B
   - Rules / restrictions
   - Deliverables
   - judging criteria

Read the relevant phase contracts:

5. PHASE_02_COMPETITION_CONTRACT.md
6. PHASE_03_COMPETITION_CONTRACT.md
7. PHASE_04_COMPETITION_CONTRACT.md
8. PHASE_05_COMPETITION_CONTRACT.md
9. PHASE_06_COMPETITION_CONTRACT.md
10. PHASE_07_COMPETITION_CONTRACT.md
11. PHASE_08_COMPETITION_CONTRACT.md
12. PHASE_09_COMPETITION_CONTRACT.md
13. PHASE_10_COMPETITION_CONTRACT.md

14. PHASE_11_COMPETITION_CONTRACT.md
15. PHASE_12_COMPETITION_CONTRACT.md
16. PHASE_13_COMPETITION_CONTRACT.md
17. PHASE_14_COMPETITION_CONTRACT.md
18. PHASE_15_COMPETITION_CONTRACT.md
19. PHASE_16_COMPETITION_CONTRACT.md
20. PHASE_17_COMPETITION_CONTRACT.md

21. PHASE_18_COMPETITION_CONTRACT.md
22. PHASE_19_COMPETITION_CONTRACT.md
23. PHASE_20_COMPETITION_CONTRACT.md
24. PHASE_21_COMPETITION_CONTRACT.md
25. PHASE_22_COMPETITION_CONTRACT.md
26. PHASE_23_COMPETITION_CONTRACT.md
27. PHASE_24_COMPETITION_CONTRACT.md

28. PHASE_29_COMPETITION_CONTRACT.md

Inspect safe tracked implementation/configs needed to document the FINAL state.

Do NOT inspect private real rows.

==================================================
OFFICIAL REQUIREMENT — EXACT SCOPE
==================================================

The official deliverable is:

"Data preprocessing document. A brief write-up of your data preparation,
label construction, data cleaning, feature engineering, and rationale."

The official final notebook separately retains the executable cells used for:

label construction
preprocessing
training
evaluation

Therefore Phase30 should be:

concise but complete
method-focused
source-grounded
judge-readable
traceable to the final implementation

It should NOT be a dump of source code.

It should NOT duplicate the full final notebook.

==================================================
FINAL OUTPUT
==================================================

Primary deliverable:

docs/preprocessing.md

This is the canonical Phase30 source document.

Also create:

docs/preprocessing_manifest.yaml

scripts/build_preprocessing_manifest.py

scripts/validate_preprocessing_doc.py

tests/test_preprocessing_manifest.py
tests/test_preprocessing_document.py
tests/test_preprocessing_privacy.py
tests/test_preprocessing_contract.py

Optional helper:

docs/preprocessing_appendix.md

ONLY if the main document would otherwise become too long.

Do not create a PDF in Phase30 unless the repository/final packaging
workflow explicitly requires one later.

==================================================
DOCUMENT LENGTH / STYLE
==================================================

Official wording says "brief write-up".

Engineering target:

approximately 2,500–4,500 words

excluding:
table of contents
small tables
references / appendix

This is guidance, not an organizer rule.

Prefer:

short paragraphs
compact tables
clear formulas
final-state language
rationale immediately after each major decision

Avoid:

long experiment logs
full hyperparameter dumps
full schema dumps
full code listings
row-level examples from private data

==================================================
DOCUMENT STRUCTURE
==================================================

Use this top-level structure:

# WayLoom Datathon — Data Preprocessing and Methodology

## 1. Purpose and scope

## 2. Input datasets

## 3. Shared data preparation and quality controls

## 4. Task 1 — service-time and lateness preparation
### 4.1 joins
### 4.2 label construction
### 4.3 cleaning
### 4.4 feature engineering
### 4.5 leakage prevention
### 4.6 validation
### 4.7 final model rationale

## 5. Task 2A — depot demand forecasting
### 5.1 demand-history construction
### 5.2 weekly aggregation
### 5.3 cleaning
### 5.4 forecasting features
### 5.5 leakage prevention
### 5.6 rolling validation
### 5.7 final forecasting methodology and model rationale

## 6. Task 2B — peak-day allocation preparation
### 6.1 scenario inputs
### 6.2 compatibility preparation
### 6.3 trip-time calculation
### 6.4 hard-feasibility preparation
### 6.5 WayLoom priority preparation
### 6.6 optimizer / independent validation / official export

## 7. Reproducibility and data-safety controls

## 8. Final preprocessing summary

Optional:

## Appendix — compact final feature inventory

Do not create different structure unless repository conventions strongly
justify it.

==================================================
PREPROCESSING MANIFEST
==================================================

Create:

docs/preprocessing_manifest.yaml

This is a SAFE machine-checkable summary of what the document must say.

It should be populated from safe tracked configs/metadata.

Recommended sections:

version

official_requirement

inputs

joins

task1_labels

cleaning

task1_features

task1_leakage

task1_validation

task1_models

task2a_history

task2a_features

task2a_validation

task2a_models

task2a_postprocessing

task2b_inputs

task2b_compatibility

task2b_trip_time

task2b_hard_rules

task2b_priority

task2b_validation

outputs

privacy

No real identifiers.
No private row values.
No absolute user paths.

==================================================
MANIFEST BUILDER
==================================================

Create:

scripts/build_preprocessing_manifest.py

Read SAFE tracked sources only.

Examples:

configs/dataset_manifest.yaml

Task1 feature registry / final feature schema

configs/task1_final_models.yaml

safe Task1 model metadata

configs/task2a_final_models.yaml

safe Task2A feature/runtime metadata

configs/task2b_scenario.yaml

configs/task2b_compatibility.yaml

configs/task2b_trip_time.yaml

configs/task2b_priority.yaml

configs/task2b_optimizer.yaml

safe official output schema constants

Do NOT read:

data/raw/**
data/interim/**
data/processed/**
reports/private/**

The Phase30 manifest should document METHOD, not private contents.

==================================================
DT-379 — DOCUMENT ALL INPUT DATASETS
==================================================

Create a compact source inventory.

For every dataset actually used in the final pipelines, document:

logical name

competition area:
Training Data / Test Data / General Data / Submission Template

task(s) using it

row grain

key fields

role

important fields/categories

whether it contributes:
labels
features
history
constraints
validation/output identity

Do not invent dataset columns.

Use the official booklet and actual dataset manifest/schema registry.

==================================================
MINIMUM OFFICIAL INPUTS TO COVER
==================================================

Task1 official inputs:

task1_test_inputs.csv

route_legs_test.csv

relevant Training Data/

relevant General Data/

Task1 training relationship must include the actual training delivery and
route-leg sources used by the implementation.

Task2A official inputs:

deliveries_train.csv

task1_test_inputs.csv

calendar.csv

task2a_test_inputs.csv

Task2B official inputs:

task2b_peak_day_scenarios.csv

task2b_peak_day_fleet.csv

vehicles.csv

district_travel.csv

service_allowance.csv

Official templates:

submission_task1.csv

submission_task2a.csv

submission_task2b.csv

Only list additional files if the final implementation actually uses them.

==================================================
DATASET DOCUMENTATION RULE
==================================================

Do not publish:

private row counts
real IDs
real sample rows

unless those aggregate facts are already approved for the competition
document and necessary.

Dataset descriptions should be structural.

Example:

"One row per planned delivery"

not:

"Delivery ABC123 had 14.8 m3..."

==================================================
DT-380 — DOCUMENT JOINS
==================================================

Create a compact join table.

For every important final join, document:

left source

right source

join key

cardinality expectation

validation guard

purpose

Include Task1 official join:

deliveries_train.(route_id, seq_in_route)

↔

route_legs_train.(route_id, seq)

and equivalent frozen test-time route-leg join if used.

Document that:

each task1_test_inputs delivery_id matches exactly one test route leg

according to the official source contract.

==================================================
JOIN INTEGRITY
==================================================

Document safeguards such as:

unique join keys

many-to-one vs one-to-one expectations

row-count preservation

missing reference checks

duplicate-key checks

order/template identity preservation

Only mention guards actually implemented.

Do not claim:
"all joins were perfect"
unless evidence exists.

Preferred:
"the pipeline fails closed when..."

==================================================
TASK2A JOINS
==================================================

Document how:

deliveries_train

and

task1_test_inputs

are normalized into one demand-history contract.

Document calendar mapping:

requested order_date
→ calendar date
→ iso_year / iso_week

If depot/brand/reference enrichment exists:
document actual joins.

Do not confuse Task1 route outcomes with Task2A demand history.

==================================================
TASK2B JOINS / LOOKUPS
==================================================

Document:

scenario orders
→ scenario fleet availability

order depot/access/temp/size
→ vehicle reference capability/capacity/home depot

district
→ district travel values

brand + dock_type
→ service allowance

Use lookup terminology where appropriate.

Do not imply a join on outlet_id is the allocation key.

Official Task2B allocation key is:

order_ref

==================================================
DT-381 — DOCUMENT TASK 1 LABELS
==================================================

This section is P0 critical.

Document exact official label reasoning.

Define:

service_start
=
max(actual arrival, window opening)

service_minutes
=
leave_outlet_time - service_start

late_flag
=
1 only if actual arrival > window_close_time

Explicitly state:

early arrival waits until opening

waiting before opening is NOT service time

arrival exactly at closing time is NOT late

late delivery is still delivered in the supplied scenario

==================================================
TASK1 LABEL SOURCE BOUNDARY
==================================================

Document:

actual route/journey/handling fields are used for historical label
construction

but not as direct current prediction-time features

At minimum mention:

actual_depart_time

actual_travel_duration_min

arrival_time

leave_outlet_time

Do not write:

"actual arrival is a feature"

unless referring to a chronology-safe historical aggregate with a completely
different row/time context and clearly explaining that distinction.

==================================================
MIDNIGHT / TIME HANDLING
==================================================

The official booklet does not prescribe a specific midnight algorithm.

Document the ACTUAL validated engineering implementation.

Examples might include:

date-aware timestamps

day-rollover normalization

duration correction using service day context

Use the real Phase4 implementation.

Label it:

WayLoom engineering handling

not:

official formula

Do not invent a midnight rule if none was implemented.

==================================================
LABEL QUALITY CHECKS
==================================================

Document actual checks such as:

service_minutes finite

nonnegative service time under valid source chronology

late_flag binary

strict-close boundary regression

early-wait regression

join coverage

timestamp parse validation

Do not invent dataset-specific correction counts.

==================================================
DT-382 — DOCUMENT CLEANING DECISIONS
==================================================

Document cleaning by category.

Recommended categories:

schema/type normalization

timestamp parsing

missing values

duplicate/key handling

categorical normalization

numeric sanity checks

reference coverage

invalid/impossible records

output/template identity protection

Do not use vague wording such as:
"we cleaned the data."

Explain the rule and rationale.

==================================================
CLEANING DECISION FORMAT
==================================================

Recommended table:

Issue / risk

Affected task(s)

Decision

Why

Fail/repair behavior

Source of rule:
official / WayLoom engineering

Examples must come from actual implementation.

==================================================
FAIL-CLOSED VS IMPUTATION
==================================================

Distinguish:

hard schema/data-contract failures

from:

model feature missing-value handling

Do not say all missing data were imputed if some fields cause hard failure.

Do not say rows were dropped unless the final pipeline actually drops them.

For official submission identities:
document row preservation where required.

==================================================
NUMERIC CLEANING
==================================================

Document actual checks for fields such as:

weight

volume

distance/travel

service allowances

prediction outputs

Only include checks implemented in final pipelines.

Do not invent winsorization/clipping unless present.

==================================================
CATEGORICAL CLEANING
==================================================

Document:

normalization/validation

unknown category behavior

frozen encoder/model handling

reference-domain checks

for the final models.

Do not claim one-hot encoding if final model uses native categoricals.

Read actual final pipeline.

==================================================
DT-383 — DOCUMENT FEATURE ENGINEERING
==================================================

Document final enabled feature families.

Do NOT document all experiments as if final.

Use:

final feature registry

final feature schema

final model metadata

For Task1, organize into semantic groups.

Possible examples only if actually enabled:

planned timing/slack

planned travel/distance

order size

brand/outlet/district

dock/access context

reference service allowance

route position/workload

calendar context

chronology-safe historical aggregates

==================================================
FEATURE TABLE
==================================================

Recommended compact table:

Feature group

Examples of final features

Source

Available at prediction time?

Transformation

Rationale

Do not list hundreds of encoded dummy columns.

Show business-level feature families.

Optional appendix may contain exact final feature names if concise.

==================================================
TASK1 DERIVED FEATURE FORMULAS
==================================================

For important engineered features, show exact formula when useful.

Examples:

planned slack

planned early wait

route workload

historical rolling aggregate

Only if they actually exist.

Do not create formulas from memory.

Read implementation.

==================================================
TASK2A FEATURE ENGINEERING
==================================================

Document final forecasting feature families only.

Possible:

lagged weekly demand

rolling statistics

calendar/week signals

depot/brand context

forecast horizon

trend/seasonality proxies

Only list actual frozen features.

For every lag/rolling feature:
state it uses only information available before the forecast origin.

==================================================
TASK2B "FEATURES"
==================================================

Task2B is not a trained prediction model.

Do not call compatibility/time/capacity values "ML features" without context.

Document them as:

derived optimization inputs

compatibility indicators

trip-time coefficients

policy metadata

capacity/time constraints

==================================================
DT-384 — DOCUMENT LEAKAGE PREVENTION
==================================================

Create a dedicated leakage section.

This must be explicit.

Task1:

planned information available at prediction time

vs

actual journey/handling training-only data

Direct current actual fields prohibited as predictors.

Chronology-safe historical aggregates only.

==================================================
TASK1 LEAKAGE PREVENTION
==================================================

At minimum explain:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

are not direct current-row predictors.

Targets/labels are excluded.

Historical target-derived features, if used, are computed only from prior
eligible records.

Feature preprocessing is fit only on training portion under the frozen
validation contract where applicable.

Do not overstate if implementation differs.

==================================================
TASK2A LEAKAGE PREVENTION
==================================================

Document:

future forecast weeks are not used as training targets/features for earlier
origins

lags/rolling statistics are shifted/constructed from past data only

rolling validation preserves chronology

task1_test_inputs contributes DEMAND HISTORY because each row represents an
order, not because its future delivery outcome is known

Do not use Task1 actual outcomes to create Task2A future-demand labels.

==================================================
TASK2B LEAKAGE CONCEPT
==================================================

Task2B is scenario optimization, not predictive model training.

Leakage framing is different.

Document instead:

only supplied S1 scenario/reference inputs are used

no hidden Task1/Task2A prediction is imported as a hard constraint

no post-hoc manual edits are introduced after freeze

==================================================
DT-385 — DOCUMENT VALIDATION STRATEGY
==================================================

Document final validation separately for each task.

==================================================
TASK1 VALIDATION
==================================================

Read Phase7/9/10 implementation.

Document:

split design

time/group constraints if any

service regression metrics

late-probability/classification metrics

calibration evaluation

baseline vs challenger fairness

final model selection on validation only

no test-label tuning

Do not invent metric names.

Use actual final metric set.

==================================================
TASK2A VALIDATION
==================================================

Document:

rolling/time-aware validation

10-week horizon

forecast origin logic

how direct horizon predictions are evaluated if applicable

actual forecast metrics

total/chilled evaluation

baseline vs advanced comparison

no future leakage

Do not say:
random cross-validation
unless that is truly implemented.

==================================================
TASK2B VALIDATION
==================================================

Document:

independent allocation audit

Phase23 solver-neutral validator

organizer check_allocation.py

hash/freeze evidence

official checker proves feasibility, not optimality

Do not frame CP-SAT objective score as organizer scoring.

==================================================
DT-386 — DOCUMENT MODEL CHOICE RATIONALE
==================================================

Use ACTUAL final model family/config names.

Do not guess.

For Task1:

service final model rationale

lateness final model rationale

calibration rationale if used

service post-processing rationale

For Task2A:

final total/chilled strategy

model family/families

direct/global/horizon design rationale

post-processing rationale

==================================================
MODEL RATIONALE EVIDENCE
==================================================

Rationale should be based on frozen validation evidence.

Allowed:

"selected because it gave the strongest frozen validation performance while
remaining reproducible"

"chosen over the baseline based on lower validation error"

"calibration was retained because it improved probability quality under the
frozen validation contract"

Only say these if supported by final evidence.

If aggregate metric values are safe and already part of competition docs:
include compact values.

If not:
use qualitative validated comparison.

Do not expose row-level examples.

Do not choose based on Task1/Task2A test outcomes.

==================================================
MODEL RESTRICTION COMPLIANCE
==================================================

Document:

models trained locally under competition restrictions

no proprietary API-based modelling/preprocessing

no prohibited end-to-end low/no-code modelling

Do not claim "no AI used" if AI assistance exists; AI disclosure is a
separate deliverable.

==================================================
BASELINE RATIONALE
==================================================

Briefly mention baseline models were used to establish a reference point.

Do not turn the preprocessing document into a full experiment report.

One compact sentence/table is enough.

==================================================
DT-387 — DOCUMENT FORECASTING METHODOLOGY
==================================================

This section must independently explain Task2A end-to-end.

Official demand-history rules:

build from:
deliveries_train
+
task1_test_inputs

count each unique order once

include deferred or never-dispatched orders

assign each order to requested order week

use calendar ISO year/week

forecast:
10 future weeks
per depot + brand + week

Only Fresh chilled

Style/Tech chilled = 0

==================================================
TASK2A VOLUME TARGET CONSTRUCTION
==================================================

Document the ACTUAL source fields/calculation used to derive:

total_volume_m3

chilled_volume_m3

at weekly grain.

Do not invent a volume formula.

Read implementation/schema.

If order_volume_m3 already exists:
say it is aggregated.

If volume is derived from item/order fields:
document the actual derivation.

==================================================
TASK2A FORECAST STRATEGY
==================================================

Read:

configs/task2a_final_models.yaml

and final inference code.

Explain:

global vs brand-specific

direct vs recursive vs horizon-feature

separate total/chilled models or derived chilled

feature construction

forecast horizon mapping

post-processing

Do not use generic forecasting theory to fill gaps.

==================================================
TASK2A POSTPROCESSING
==================================================

Document actual frozen output rules.

At minimum if implemented:

nonnegative forecasts

chilled <= total

Style/Tech chilled = 0

Do not claim uncertainty intervals are official.

Phase27, if implemented, is optional/unofficial and should be at most a
short note outside the official forecasting method.

==================================================
DT-388 — DOCUMENT TASK 2B PREPARATION
==================================================

Task2B does NOT require a trained model.

State that explicitly.

Document how raw scenario/reference inputs are transformed into a legal
optimization problem.

==================================================
TASK2B INPUTS
==================================================

Document:

S1 scenario orders

S1 fleet availability

vehicles reference

district travel

service allowance

Use:

order_ref

as the allocation key.

outlet_id may repeat.

Only:

status = available

vehicles may be allocated.

==================================================
TASK2B COMPATIBILITY PREPARATION
==================================================

Document static compatibility rules:

chilled -> reefer

reefer may carry ambient

van_only -> van

home depot match

whole order must fit individual vehicle weight

whole order must fit individual vehicle volume

Zero-compatible orders retained for deferral reasoning.

Do not call a compatibility matrix the final allocation.

==================================================
TASK2B TRIP-TIME PREPARATION
==================================================

Document exact formula:

trip_minutes
=
depot_to_district_freeflow_min
+
inter_stop_freeflow_min * (num_orders - 1)
+
sum(service_allowance_min)

No return journey.

Service allowance lookup:

brand + dock_type

Mention official regression example:

Fresh Gampaha 3 orders
=
101 minutes

Optionally:
Fresh Colombo 4 street stops
=
112 minutes

and combined:
213 Fresh minutes

Use these because they are official booklet examples.

==================================================
TASK2B HARD RULES
==================================================

Document all seven groups:

1 same brand + district per trip

2 chilled -> reefer

3 van_only -> van

4 home depot

5 whole order / no split

6 both weight + volume capacity

7 max two trips + daily time budgets

Fresh <=270

Style+Tech combined <=480

No return-leg addition.

No fuel/window hard rule.

==================================================
TASK2B PRIORITY PREPARATION
==================================================

Clearly separate:

official hard feasibility

from:

WayLoom engineering priority policy

Document the frozen lexicographic hierarchy:

1 MAX served orders
2 MAX served previous-deferred
3 MAX served waiting-days
4 MAX served low-flexibility
5 MAX Fresh chilled
6 MAX Fresh
7A MIN avoidable reefer-van
7B MIN avoidable reefer
7C MIN avoidable van

Do not call it official organizer priority.

==================================================
TASK2B SOLVER PREPARATION
==================================================

Document high-level optimizer preparation:

binary serve/defer/assignment variables

trip use/group structure

capacity/time constraints

sequential lexicographic solve

all objective stages OPTIMAL before freeze

deterministic seed/workers

independent post-solve audit

Do not include full mathematical formulation unless needed.

This is a brief preprocessing/methodology document.

==================================================
TASK2B VALIDATION / EXPORT
==================================================

Document:

frozen allocation

independent solver-neutral validator

official checker

official checker validates feasibility only

final template export exact six columns

written policy separate

Do not claim:
official checker proves optimum.

==================================================
SHARED REPRODUCIBILITY SECTION
==================================================

Document:

deterministic seeds where used

saved final model artifacts

frozen configs

schema validation

hash/freeze safeguards

template identity preservation

local execution

no proprietary prediction API

Do not expose actual hashes unless necessary.

==================================================
DATA SAFETY / PRIVACY
==================================================

The preprocessing document itself is a competition-data derivative.

It must not include:

real delivery_id

real order_ref

real outlet_id

real vehicle_id tied to private allocation

private row dumps

absolute user paths

private report contents

secrets

unapproved private aggregate tables

Official booklet illustrative examples are allowed because they are already
public within the competition material.

==================================================
OFFICIAL VS ENGINEERING LABELS
==================================================

Throughout the document distinguish:

OFFICIAL REQUIREMENT

from:

WAYLOOM ENGINEERING DECISION

Examples of engineering decisions:

midnight handling algorithm

feature set

validation implementation

model family

lexicographic Task2B policy

determinism controls

hash guards

Do not present engineering choices as official rules.

==================================================
RATIONALE STANDARD
==================================================

For each major engineering decision, answer:

What did we do?

Why?

What official constraint did it protect or what modelling risk did it solve?

How did we validate it?

Avoid vague claims:

"to improve accuracy"

Prefer:

"to prevent future leakage in rolling forecasts"

"to preserve early-arrival waiting semantics"

"to keep official template identity/order unchanged"

==================================================
NO UNSUPPORTED PERFORMANCE CLAIMS
==================================================

Do not write:

best model
state of the art
highly accurate
production ready

without evidence.

Prefer:

final selected model
strongest frozen validation candidate
competition-ready pipeline

when supported.

==================================================
NO UNSUPPORTED CAUSAL CLAIMS
==================================================

Feature rationale should not claim:

X causes lateness

X causes service delay

Use:

predictive context

associated with

available at prediction time

captures operational variation

Phase25 explainability, if available, may be referenced cautiously but is not
required for Phase30.

==================================================
CROSS-PHASE CONSISTENCY
==================================================

Before writing final prose, compare:

Task1 labels
against Phase4 + final tests

Task1 final features
against Phase6 registry + final config

Task1 validation
against Phase7/9/10

Task1 model names
against final model config

Task2A history
against Phase11

Task2A features
against Phase13/final config

Task2A validation
against Phase14

Task2A models
against Phase17 config

Task2B compatibility
against Phase19

Task2B trip time
against Phase20

Task2B policy
against Phase21

Task2B optimizer/freeze
against Phase22

Task2B validator/checker
against Phase23

Task2B final output/policy
against Phase24

If mismatch:
STOP.

Do not resolve by prose.

==================================================
LINK TO PHASE29 ARCHITECTURE
==================================================

If Phase29 diagrams are final:

reference them from docs/preprocessing.md using relative links.

Example:

Architecture overview:
docs/architecture/high_level_datathon.svg

Task sections may reference the corresponding diagrams.

Do not duplicate all diagram content in prose.

If Phase29 is not final:
document without broken links and add no placeholder.

==================================================
DOCUMENT TABLES
==================================================

Recommended compact tables:

Input dataset inventory

Join map

Cleaning decisions

Task1 feature families

Task2A feature families

Validation summary

Final model rationale summary

Task2B preparation summary

Keep tables readable.

Do not create extremely wide 20-column tables.

==================================================
PREPROCESSING DOCUMENT VALIDATOR
==================================================

Create:

scripts/validate_preprocessing_doc.py

It should validate:

file exists

nonempty

all DT-379–DT-388 mapped to sections

required official Task1 formulas present semantically

strict late boundary present

Task2A both-history-source rule present

deferred/not_run demand included

requested date -> ISO week rule present

Style/Tech chilled zero present

Task2B no-model statement present

Task2B trip formula present

Task2B no-return rule present

seven hard rules present

WayLoom policy labelled engineering policy

validation strategies present

actual final model names/configs match manifest

no TODO/TBD/placeholders

no stale model name

no private path leakage

no real/private ID examples

word-count guidance reported

official vs engineering distinction present

==================================================
TASK COMPLETENESS MATRIX
==================================================

At the end of docs/preprocessing_manifest.yaml, include mapping:

DT-379 -> document section(s)
DT-380 -> section(s)
...
DT-388 -> section(s)

Validator requires all 10 tasks mapped.

Do NOT show DT IDs in the competition-facing prose unless helpful.

The manifest can carry them.

==================================================
TESTS — MANIFEST
==================================================

Create:

tests/test_preprocessing_manifest.py

Test:

all required manifest sections exist

all 10 Phase30 tasks mapped

Task1 final model names resolved

Task2A final strategy resolved

Task2B policy tier order exact

official output schemas exact

no absolute private paths

no placeholder value

==================================================
TESTS — DOCUMENT
==================================================

Create:

tests/test_preprocessing_document.py

Test semantic presence:

all source categories

Task1 join

Task1 service label formula

late strict >

early waiting not service

arrival == close not late

cleaning rationale

feature engineering Task1

feature engineering Task2A

leakage Task1

leakage Task2A

Task1 validation

Task2A rolling validation

Task2B validator/checker

model rationale

forecast methodology

Task2B preparation

official/engineering distinction

==================================================
TESTS — PRIVACY
==================================================

Create:

tests/test_preprocessing_privacy.py

Scan:

docs/preprocessing.md

docs/preprocessing_manifest.yaml

Reject:

C:\Users\...

/home/<specific-user>/...

real/private identifier patterns if safely detectable

private row dumps

reports/private excerpts

secrets

API keys

private raw CSV snippets

Do not need to inspect private rows to enforce general privacy.

==================================================
TESTS — CONTRACT CONSISTENCY
==================================================

Create:

tests/test_preprocessing_contract.py

Compare manifest/document against final tracked config/constants.

Test:

Task1 output schema exact

Task2A output schema exact

Task2B output schema exact

Task1 final model family/config accurate

Task1 calibration accurate

Task2A final strategy accurate

Task2B solver = actual frozen solver

Task2B objective order exact

Task2B official checker labelled feasibility-only

No future/actual leakage field shown as current Task1 predictor

No Task1 prediction used as Task2B hard rule

No Task2A forecast used as Task2B hard rule

==================================================
EDGE CASE — FINAL MODEL CHANGED
==================================================

If docs mention a model family different from final config:

FAIL.

Update documentation to final config.

Do not change model.

==================================================
EDGE CASE — OPTIONAL FEATURES DISABLED
==================================================

Do not document a feature group merely because code supports it.

Document only final enabled features.

If helpful:

"Candidate features were evaluated, but only the frozen final feature set is
described here."

==================================================
EDGE CASE — UNKNOWN/MISSING FEATURE NAME
==================================================

If final schema contains a feature missing from the feature registry:

STOP.

This is a documentation/lineage blocker.

Do not invent a rationale for an unknown feature.

==================================================
EDGE CASE — CLEANING COUNT UNAVAILABLE
==================================================

Do not invent:

"N rows were dropped"

If exact sanitized counts are unavailable.

Describe the deterministic rule without a count.

==================================================
EDGE CASE — NO ROW DROPPING
==================================================

If pipeline fails on invalid records rather than drops them:

say so.

Do not write generic:
"invalid rows were removed."

==================================================
EDGE CASE — TASK1 CALIBRATION NONE
==================================================

If no extra lateness calibrator:

document:

no additional calibrator

or actual probability output logic.

Do not claim Platt/isotonic calibration.

==================================================
EDGE CASE — TASK2A CHILLED DERIVED
==================================================

If chilled forecast is derived rather than independently modelled:

document exact final method.

Do not write:
"we trained a chilled model"
unless true.

==================================================
EDGE CASE — TASK2B OPTIONAL REASONER
==================================================

Phase26 is optional.

Do not make the preprocessing document depend on it.

At most one short note:

"An optional post-hoc deferral reasoner was built later"

only if true and useful.

Core Task2B prep is Phases18–24.

==================================================
EDGE CASE — PHASE27 UNCERTAINTY
==================================================

Uncertainty is unofficial.

Do not put intervals into official forecasting methodology/output contract.

Optional one-sentence note is acceptable if implemented.

==================================================
EDGE CASE — PHASE28 INTEGRATION
==================================================

Hackathon integration is not required.

Do not make FastAPI part of the core preprocessing method.

==================================================
EDGE CASE — PHASE29 ARCHITECTURE NOT FINAL
==================================================

Do not create broken image links.

Phase30 can still document methods.

But Phase29 should normally be complete first.

==================================================
EDGE CASE — OFFICIAL VS WAYLOOM MISMATCH
==================================================

If document validator finds:

Task1 late uses >=

Task2A excludes deferred demand

Task2B adds return leg

Task2B adds fuel/window rule

WayLoom policy described as official

STOP.

These are factual blockers.

==================================================
WORD COUNT / BRIEFNESS GATE
==================================================

Report word count.

Recommended:

2,500–4,500

If >5,500:
flag:
TOO LONG FOR "BRIEF WRITE-UP"

unless justified.

If <1,500:
flag:
LIKELY TOO SHALLOW

These are engineering quality warnings, not automatic official-rule failures.

Completeness/accuracy beats exact word count.

==================================================
GIT WORKFLOW
==================================================

Recommended branch:

git checkout main
git pull
git checkout -b docs/phase-30-preprocessing

Recommended commits:

docs(preprocessing): add source and join inventory
docs(preprocessing): document Task1 labels features and leakage
docs(preprocessing): document Task2A forecasting methodology
docs(preprocessing): document Task2B preparation and validation
test(preprocessing): add documentation contract checks

Before commit:

git status
git diff
git diff --check

Then:

pytest -q \
  tests/test_preprocessing_manifest.py \
  tests/test_preprocessing_document.py \
  tests/test_preprocessing_privacy.py \
  tests/test_preprocessing_contract.py

pytest -q

python -m pip check

Do not stage private data or reports.

==================================================
SAFE LOCAL COMMANDS
==================================================

Expected:

python scripts/build_preprocessing_manifest.py \
  --output docs/preprocessing_manifest.yaml

Then:

python scripts/validate_preprocessing_doc.py \
  --document docs/preprocessing.md \
  --manifest docs/preprocessing_manifest.yaml

Use actual CLI implemented in repository.

No raw-root should be needed for normal Phase30 documentation validation.

==================================================
HUMAN QUALITY REVIEW
==================================================

Human should review:

Does a judge understand how each task's data was prepared?

Are official formulas correct?

Is every engineering decision clearly labelled?

Does the document explain why choices were made?

Is it brief enough?

Are final model names accurate?

Does it avoid unsupported claims?

Does it avoid private row details?

Can it be reused in the final notebook/demo?

==================================================
STOP CONDITIONS
==================================================

STOP if:

any Phase30 task is missing

official preprocessing deliverable scope is not covered

Task1 join cannot be resolved

Task1 label formula differs from official rule

late boundary uses >= instead of >

early waiting counted as service

actual journey/handling used as direct current predictors

Task2A history omits task1_test_inputs

Task2A history excludes deferred/not_run demand

Task2A uses actual delivery week instead of requested order week

Task2A forecast method cannot be resolved

Task2B allocation key described as outlet_id instead of order_ref

Task2B return leg added

Task2B hard rules altered

Task2B priority called organizer priority

Task2B checker called optimality checker

final model family/config is guessed

feature registry mismatch

document invents cleaning steps

document invents performance claims

private row/ID/path leakage

frozen artifacts change

tests fail

pip check fails

Phase31 work introduced

==================================================
DEFINITION OF DONE
==================================================

Require:

DT-379 PASS
DT-380 PASS
DT-381 PASS
DT-382 PASS
DT-383 PASS
DT-384 PASS
DT-385 PASS
DT-386 PASS
DT-387 PASS
DT-388 PASS

docs/preprocessing.md complete

preprocessing manifest generated

all official input datasets documented

all major joins documented

Task1 labels exact

cleaning decisions explicit

final feature engineering documented

leakage prevention explicit

validation strategies accurate

model rationale evidence-grounded

forecast methodology exact

Task2B preparation exact

official vs engineering distinction explicit

actual final model names/configs accurate

no stale placeholders

no private row-level data

word count reviewed

targeted tests pass

full safe suite passes

pip check passes

git diff check passes

independent review passes

frozen artifacts unchanged

Then:

PHASE 30 STATUS: PASS
PREPROCESSING DOCUMENT: FINAL
FROZEN DATATHON PIPELINES: UNCHANGED
READY FOR PHASE 31: YES

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-379 READY
DT-380 READY
DT-381 READY
DT-382 READY
DT-383 READY
DT-384 READY
DT-385 READY
DT-386 READY
DT-387 READY
DT-388 READY

No official requirement omitted.

No generic/fake preprocessing prose.

All final model choices match configs.

All Task1 labels exact.

Task1 leakage boundary exact.

Task2A demand history exact.

Task2A 10-week method exact.

Task2B preparation exact.

Policy vs hard rules separate.

No private data.

No Phase31 implementation.

==================================================
RETURN ONLY
==================================================

PHASE:
30 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-379 READY / FAIL
DT-380 READY / FAIL
DT-381 READY / FAIL
DT-382 READY / FAIL
DT-383 READY / FAIL
DT-384 READY / FAIL
DT-385 READY / FAIL
DT-386 READY / FAIL
DT-387 READY / FAIL
DT-388 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

PREPROCESSING MANIFEST:
PASS / FAIL

INPUT DATASET DOCUMENTATION:
PASS / FAIL

JOINS:
PASS / FAIL

TASK1 LABELS:
PASS / FAIL

CLEANING DECISIONS:
PASS / FAIL

FEATURE ENGINEERING:
PASS / FAIL

LEAKAGE PREVENTION:
PASS / FAIL

VALIDATION STRATEGY:
PASS / FAIL

MODEL CHOICE RATIONALE:
PASS / FAIL

FORECASTING METHODOLOGY:
PASS / FAIL

TASK2B PREPARATION:
PASS / FAIL

OFFICIAL VS ENGINEERING DISTINCTION:
PASS / FAIL

FINAL MODEL CONFIG PARITY:
PASS / FAIL

PRIVATE DATA IN DOCUMENT:
MUST BE NO

FROZEN DATATHON ARTIFACTS CHANGED:
MUST BE NO

DOCUMENT WORD COUNT:
<number>

TARGETED TESTS:
...

FULL SAFE SUITE:
...

PIP CHECK:
PASS / FAIL

GIT DIFF CHECK:
PASS / FAIL

HUMAN PROOFREAD REQUIRED:
YES

PHASE 30 STATUS:
AWAITING INDEPENDENT REVIEW

READY FOR PHASE 31:
NO

Then STOP.

Do not start Phase31.

```

---

# 129. Independent Phase 30 review prompt

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon PHASE 30.

PHASE:
Data Preprocessing Document

TASK RANGE:
DT-379 through DT-388

REVIEW MODE:
FRESH SESSION
READ-ONLY
SOURCE-GROUNDED
CROSS-PHASE CONSISTENCY CHECK

Do NOT implement Phase31.
Do NOT modify frozen pipelines.
Do NOT inspect private row-level competition data.
Do NOT invent missing rationale.

==================================================
READ SOURCE OF TRUTH
==================================================

Read:

1. Official Challenge Booklet
   - Task1
   - Task2A
   - Task2B
   - rules/restrictions
   - deliverables
   - judging

2. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase30

3. PHASE_02 through PHASE_24 contracts relevant to final pipelines

4. PHASE_29_COMPETITION_CONTRACT.md

Then inspect:

docs/preprocessing.md
docs/preprocessing_manifest.yaml

scripts/build_preprocessing_manifest.py
scripts/validate_preprocessing_doc.py

tests/test_preprocessing_manifest.py
tests/test_preprocessing_document.py
tests/test_preprocessing_privacy.py
tests/test_preprocessing_contract.py

Inspect final SAFE configs/metadata:

Task1 final config/schema/feature registry

Task2A final config/schema/feature metadata

Task2B scenario/compatibility/trip/priority/optimizer configs

Do not inspect private real rows.

==================================================
OFFICIAL DELIVERABLE AUDIT
==================================================

Verify the document satisfies:

"A brief write-up of your data preparation, label construction, data
cleaning, feature engineering, and rationale."

It should be concise, complete and competition-facing.

Do not fail simply because it does not reproduce code.

==================================================
AUDIT EVERY TASK
==================================================

DT-379:
all actual input datasets documented correctly.

DT-380:
critical joins and cardinality/identity safeguards documented.

DT-381:
Task1 labels exact.

DT-382:
cleaning decisions describe actual behavior and rationale.

DT-383:
final feature engineering documented, not experiments.

DT-384:
Task1/Task2A leakage prevention explicit and correct.

DT-385:
validation strategy matches frozen Task1/Task2A/Task2B workflows.

DT-386:
final model choice rationale matches validation evidence/configs.

DT-387:
Task2A forecasting methodology exact.

DT-388:
Task2B preparation exact.

==================================================
CRITICAL TASK1 AUDIT
==================================================

Require:

deliveries_train ↔ route_legs_train join uses:

(route_id, seq_in_route)
↔
(route_id, seq)

service_start =
max(actual arrival, window opening)

service_minutes =
leave_outlet_time - service_start

late_flag = 1 only when:

arrival_time > window_close_time

Early waiting is not service.

Arrival exactly at close is not late.

Prediction-time planned context is distinguished from actual journey/handling
training-only fields.

Actual current:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

must not be documented as direct current predictors.

==================================================
CRITICAL TASK2A AUDIT
==================================================

Require:

history from BOTH:
deliveries_train
task1_test_inputs

each unique order once

deferred/not_run orders included

requested order_date

calendar ISO year/week

depot + brand + week

10-week forecast

only Fresh chilled

Style/Tech chilled zero

actual final forecast strategy

time-aware/rolling validation

no future leakage

Do not accept generic "time-series model" prose if the frozen architecture is
more specific.

==================================================
CRITICAL TASK2B AUDIT
==================================================

Require:

Task2B no trained model required

S1 Peliyagoda

only available fleet

order_ref is allocation key

compatibility:
reefer
van_only
depot
weight
volume

trip formula:

outbound
+
inter-stop*(n-1)
+
service allowance

no return

seven official hard-rule groups

Fresh <=270

Style+Tech <=480

WayLoom priority separated from official rules

exact frozen lexicographic order

CP-SAT actual solver

independent validator

organizer checker feasibility-only

official template export

No Hackathon fuel/window rules.

==================================================
CLEANING AUDIT
==================================================

For every cleaning claim ask:

Is this actually implemented?

Is the action:
fail
normalize
impute
clip
preserve
drop
derive

accurately described?

Reject boilerplate such as:

"we removed all missing rows"

unless true.

Reject invented outlier/winsorization statements.

==================================================
FEATURE AUDIT
==================================================

Compare documented feature groups against FINAL frozen feature registries.

Reject:

disabled candidate features described as final

unknown feature names

future/actual outcome features

incorrect encoder description

incorrect categorical handling

For Task2A:
lags/rolling must be past-only.

==================================================
VALIDATION AUDIT
==================================================

Verify:

Task1 validation matches Phase7/9/10.

Task2A validation matches Phase14/16/17.

No test-set selection/tuning.

Task2B validation described as feasibility/audit rather than predictive CV.

No organizer checker optimality claim.

==================================================
MODEL RATIONALE AUDIT
==================================================

Compare model family/config names to frozen configs.

Every rationale claim must be supported by frozen validation evidence.

Reject:

"best on test set"

state-of-the-art

production-grade

guaranteed accuracy

unless explicitly supported.

No stale model-family names.

==================================================
PRIVACY AUDIT
==================================================

Scan preprocessing doc and manifest.

Reject:

real delivery_id

real order_ref

real private vehicle assignment

private row dump

absolute local user path

private report excerpt

secret/token

Official booklet illustrative examples are allowed.

==================================================
BRIEFNESS / QUALITY AUDIT
==================================================

Report word count.

Assess:

judge readability

section flow

redundancy

tables readability

rationale quality

official-vs-engineering clarity

If slightly outside recommended word target but excellent:
non-blocking note.

Only fail if length makes the official "brief write-up" materially unusable
or if critical content is missing.

==================================================
CROSS-PHASE AUDIT
==================================================

Compare:

doc ↔ Phase29 architecture

doc ↔ Task1 final config

doc ↔ Task2A final config

doc ↔ Task2B final config/policy

No contradictions.

If Phase29 diagram and Phase30 prose disagree:
identify exact source-of-truth and block until resolved.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_preprocessing_manifest.py \
  tests/test_preprocessing_document.py \
  tests/test_preprocessing_privacy.py \
  tests/test_preprocessing_contract.py

Then relevant final Task1/Task2A/Task2B regression tests.

Then:

pytest -q
python -m pip check
git diff --check
git status

Do not run training or private row processing.

==================================================
RETURN FORMAT
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

OFFICIAL PREPROCESSING DELIVERABLE:
PASS / FAIL

PREPROCESSING MANIFEST:
PASS / FAIL

INPUT DATASETS:
PASS / FAIL

JOINS:
PASS / FAIL

TASK1 LABEL CONSTRUCTION:
PASS / FAIL

TASK1 STRICT-LATE BOUNDARY:
PASS / FAIL

CLEANING ACCURACY:
PASS / FAIL

TASK1 FEATURE ACCURACY:
PASS / FAIL

TASK2A FEATURE ACCURACY:
PASS / FAIL

LEAKAGE PREVENTION:
PASS / FAIL

TASK1 VALIDATION PARITY:
PASS / FAIL

TASK2A VALIDATION PARITY:
PASS / FAIL

TASK2B VALIDATION PARITY:
PASS / FAIL

FINAL MODEL NAME/CONFIG PARITY:
PASS / FAIL

MODEL RATIONALE:
PASS / FAIL

FORECASTING METHODOLOGY:
PASS / FAIL

TASK2B PREPARATION:
PASS / FAIL

OFFICIAL VS ENGINEERING DISTINCTION:
PASS / FAIL

PHASE29 ARCHITECTURE CONSISTENCY:
PASS / FAIL

PRIVACY:
PASS / FAIL

DOCUMENT WORD COUNT:
<number>

BRIEFNESS / READABILITY:
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

DT-379: PASS/FAIL
DT-380: PASS/FAIL
DT-381: PASS/FAIL
DT-382: PASS/FAIL
DT-383: PASS/FAIL
DT-384: PASS/FAIL
DT-385: PASS/FAIL
DT-386: PASS/FAIL
DT-387: PASS/FAIL
DT-388: PASS/FAIL

PHASE 30 INDEPENDENT REVIEW:
PASS / FAIL

PREPROCESSING DOCUMENT:
FINAL / INCOMPLETE

FROZEN DATATHON PIPELINES:
UNCHANGED / CHANGED

READY FOR PHASE 31:
YES / NO

If PASS:

PHASE 30 INDEPENDENT REVIEW: PASS
PREPROCESSING DOCUMENT: FINAL
FROZEN DATATHON PIPELINES: UNCHANGED
BLOCKERS: None
READY FOR PHASE 31: YES

Then STOP.

Do not start Phase31.

```

---

# 130. Completion record

```markdown
# Phase 30 Completion Record

## Tasks

- [ ] DT-379
- [ ] DT-380
- [ ] DT-381
- [ ] DT-382
- [ ] DT-383
- [ ] DT-384
- [ ] DT-385
- [ ] DT-386
- [ ] DT-387
- [ ] DT-388

## Document

- [ ] docs/preprocessing.md
- [ ] preprocessing manifest
- [ ] dataset inventory
- [ ] joins
- [ ] labels
- [ ] cleaning
- [ ] features
- [ ] leakage
- [ ] validation
- [ ] model rationale
- [ ] forecasting method
- [ ] Task2B preparation

## Critical semantics

- [ ] Task1 early wait excluded from service
- [ ] Task1 strict `arrival > close`
- [ ] actual fields not direct prediction-time features
- [ ] Task2A both demand-history sources
- [ ] deferred/not_run included
- [ ] requested order week
- [ ] Style/Tech chilled zero
- [ ] Task2B no trained model required
- [ ] `order_ref` key
- [ ] no return journey
- [ ] seven hard rules
- [ ] WayLoom policy separate from official rules
- [ ] checker feasibility-only

## Quality / safety

- [ ] final model names correct
- [ ] Phase29 consistent
- [ ] no placeholders
- [ ] no private IDs
- [ ] no unsupported claims
- [ ] brief/readable
- [ ] targeted tests pass
- [ ] full safe suite pass

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 30 STATUS: PASS / FAIL
PREPROCESSING DOCUMENT: FINAL / INCOMPLETE
FROZEN DATATHON PIPELINES: UNCHANGED / CHANGED
READY FOR PHASE 31: YES / NO
```

---

# 131. Final checklist

Before Phase 31:

- [ ] exact DT-379–DT-388 coverage.
- [ ] official preprocessing requirement satisfied.
- [ ] final source inventory accurate.
- [ ] joins accurate.
- [ ] Task1 service label exact.
- [ ] Task1 strict late label exact.
- [ ] cleaning matches implementation.
- [ ] final Task1 features only.
- [ ] final Task2A features only.
- [ ] leakage prevention explicit.
- [ ] Task1 validation accurate.
- [ ] Task2A validation accurate.
- [ ] Task2B validation accurate.
- [ ] final model choice rationale grounded.
- [ ] Task2A demand history exact.
- [ ] Task2A 10-week forecasting strategy exact.
- [ ] Task2B preparation exact.
- [ ] hard rules and policy separated.
- [ ] official checker semantics correct.
- [ ] official vs WayLoom decisions clear.
- [ ] Phase29 diagrams and Phase30 prose agree.
- [ ] no private data/paths.
- [ ] no placeholders.
- [ ] word count/readability reviewed.
- [ ] tests pass.
- [ ] full safe suite passes.
- [ ] independent review passes.
- [ ] frozen artifacts unchanged.

Only then:

```text
PHASE 30 STATUS: PASS
PREPROCESSING DOCUMENT: FINAL
FROZEN DATATHON PIPELINES: UNCHANGED
READY FOR PHASE 31: YES
```
