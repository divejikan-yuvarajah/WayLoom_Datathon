# PHASE 31 — Final Competition Notebook

> **Filename:** `PHASE_31_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 31 — Final competition notebook  
> **Task range:** **DT-389 → DT-411**  
> **Task count:** **23**  
> **Phase dependency:** **Phases 10, 17, 24 and documentation state**  
> **Default phase priority:** **P0**  
> **Master phase gate:** Final notebook runs top-to-bottom and final inference loads saved models rather than relying on hidden state.  
> **Primary deliverable:** `TeamName_FinalNotebook.ipynb`  
> **Critical cross-phase dependency:** **DT-405 depends on Phase 32 DT-412–DT-419.**

---

# 1. Phase 31 purpose

Phase 31 creates the official final competition notebook for the WayLoom Datathon.

The Rootcode Tech-Triathlon Challenge Booklet requires the final notebook to retain the cells used for:

```text
label construction
preprocessing
training
evaluation
```

and requires a **final cell** that:

```text
loads the saved models

demonstrates inference for Task 1

demonstrates inference for Task 2A

clearly prints the inputs and predictions
```

This is not a scratch notebook and not a second implementation of the project.

The notebook is the competition-facing evidence layer over the reusable code already implemented in `src/`.

---

# 2. Official source requirement

The official Challenge Booklet Deliverables section states, in substance:

```text
Final notebook (TeamName_FinalNotebook.ipynb).
Retain the cells used for label construction, preprocessing, training, and evaluation.
Add a final cell that loads the saved models, demonstrates inference for Task 1 and Task 2A,
and clearly prints the inputs and predictions.
```

The same deliverables section separately requires saved final model files alongside the notebook.

Therefore Phase 31 must not substitute:

- a notebook that only loads CSV predictions;
- a notebook that omits training/evaluation cells;
- a final cell that reuses in-memory fitted models;
- a notebook that only links to scripts without showing the required competition workflow.

---

# 3. Finalized Phase 31 master inventory

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-389** | [O] | P0 | Task 1, Task 2A and Task 2B finalized | Create `TeamName_FinalNotebook.ipynb` |
| [ ] | **DT-390** | [E] | P0 | Phases 10,17,24 and documentation state | Add project/problem overview |
| [ ] | **DT-391** | [E] | P0 | Phases 10,17,24 and documentation state | Add imports/configuration |
| [ ] | **DT-392** | [E] | P0 | Phases 10,17,24 and documentation state | Add data loading |
| [ ] | **DT-393** | [E] | P0 | Phases 10,17,24 and documentation state | Add data validation |
| [ ] | **DT-394** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 1 label construction |
| [ ] | **DT-395** | [O] | P0 | Phases 10,17,24 and documentation state | Add preprocessing cells |
| [ ] | **DT-396** | [E] | P0 | Phases 10,17,24 and documentation state | Add EDA summary |
| [ ] | **DT-397** | [O] | P0 | Phases 10,17,24 and documentation state | Add feature engineering |
| [ ] | **DT-398** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 1 training cells |
| [ ] | **DT-399** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 1 evaluation |
| [ ] | **DT-400** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 2A aggregation |
| [ ] | **DT-401** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 2A training/backtesting |
| [ ] | **DT-402** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 2A evaluation |
| [ ] | **DT-403** | [E] | P0 | Phases 10,17,24 and documentation state | Add Task 2B summary/pointer |
| [ ] | **DT-404** | [O] | P0 | Saved models available | Add final inference section |
| [ ] | **DT-405** | [O] | P0 | DT-412–DT-419 | Load saved models in final cell |
| [ ] | **DT-406** | [O] | P0 | Phases 10,17,24 and documentation state | Demonstrate Task 1 inference |
| [ ] | **DT-407** | [O] | P0 | Phases 10,17,24 and documentation state | Demonstrate Task 2A inference |
| [ ] | **DT-408** | [O] | P0 | Phases 10,17,24 and documentation state | Clearly print inputs and predictions |
| [ ] | **DT-409** | [O] | P0 | Phases 10,17,24 and documentation state | Restart kernel and run all |
| [ ] | **DT-410** | [E] | P0 | Phases 10,17,24 and documentation state | Remove broken/temporary cells |
| [ ] | **DT-411** | [O] | P0 | Phases 10,17,24 and documentation state | Ensure notebook runs without hidden state |

**Expected tasks:** 23  
**Missing tasks allowed:** 0

---

# 4. Master-plan dependency bridge: Phase 31 ↔ Phase 32

There is an intentional cross-phase dependency in the finalized inventory:

```text
DT-405 — Load saved models in final cell
Dependency: DT-412–DT-419
```

Phase 32 owns:

```text
DT-412 save Task1 service model
DT-413 save Task1 lateness model
DT-414 save Task2A model/artifacts
DT-415 save preprocessing objects if necessary
DT-416 record model versions
DT-417 test serialization
DT-418 test deserialization
DT-419 compare loaded-model predictions with original predictions
```

Therefore Phase 31 should be executed in two stages.

## Stage A — core notebook implementation

Build the entire notebook structure, training/evaluation evidence, and the final inference cell against canonical loader interfaces.

If Phase 32 is not complete:

```text
DT-405 = BLOCKED_BY_PHASE32
PHASE31 CORE = READY
PHASE31 FINAL PASS = NO
```

The next engineering action is Phase 32 artifact finalization.

## Stage B — final Phase 31 closure

After Phase 32 passes:

```text
reload all saved artifacts
run notebook from clean kernel
run final cell alone in a fresh kernel
verify prediction parity
rerun independent Phase31 review
```

Only then:

```text
PHASE 31 STATUS: PASS
```

This staged flow is a WayLoom engineering orchestration; it does not alter the official notebook requirement.

---

# 5. Notebook principle: evidence, not the only implementation

The master plan explicitly states:

> Notebook is evidence, not the only implementation. Important reusable logic belongs in `src/` and is called from the final notebook where practical.

Therefore the notebook should contain:

```text
clear markdown explanation
thin orchestration cells
calls to canonical src/ functions
compact evidence tables/plots
final saved-model inference demonstration
```

It should not contain:

```text
copy-pasted production modules
second feature-engineering implementation
second label implementation
second Task2B optimizer
notebook-only hidden patches
```

If notebook behavior differs from canonical source behavior, the phase is blocked.

---

# 6. Frozen artifact boundary

Phase 31 is not allowed to modify the frozen final results.

Do not modify or regenerate:

```text
configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

configs/task2a_final_models.yaml
Task2A final model/runtime artifacts
outputs/submission_task2a.csv

data/interim/task2b_final_allocation.csv
data/interim/task2b_final_trip_summary.csv
configs/task2b_priority.yaml
outputs/submission_task2b.csv
docs/task2b_policy.md
Phase22/23 private freeze/checker evidence
```

Notebook training/backtesting cells must use in-memory objects or private temporary runtime paths.

---

# 7. Required Phase 31 files

Create/update:

```text
TeamName_FinalNotebook.ipynb

configs/final_notebook.yaml

scripts/validate_final_notebook.py
scripts/execute_final_notebook.py

# optional if useful for deterministic construction
scripts/build_final_notebook.py

tests/test_final_notebook_structure.py
tests/test_final_notebook_contract.py
tests/test_final_notebook_final_inference.py
tests/test_final_notebook_privacy.py
tests/test_final_notebook_no_hidden_state.py
```

Private local evidence:

```text
reports/private/phase31_final_notebook/
├── run_manifest.json
├── execution_summary.json
├── TeamName_FinalNotebook.executed.ipynb
├── final_cell_only.executed.ipynb
├── final_inference_parity.json
└── frozen_hash_audit.json
```

Do not publish or publicly commit the private executed notebook if it contains competition records/derivatives.

---

# 8. Source notebook vs executed evidence notebook

Use two representations for safety.

## Tracked canonical source notebook

```text
TeamName_FinalNotebook.ipynb
```

Recommended public-repository state:

```text
outputs cleared
code/markdown intact
no private rows embedded
```

## Private executed verification copy

```text
reports/private/phase31_final_notebook/TeamName_FinalNotebook.executed.ipynb
```

Contains the local execution results needed to prove clean run and the required inference demonstration.

During final packaging, the validated executed copy may be used as the submitted `TeamName_FinalNotebook.ipynb`, because the organizer is an authorized competition recipient.

---

# 9. Recommended `configs/final_notebook.yaml`

```yaml
version: 1
notebook_filename: TeamName_FinalNotebook.ipynb

execution:
  kernel_name: python3
  timeout_seconds: 7200
  working_directory: .
  private_output_dir: reports/private/phase31_final_notebook

reproducibility:
  random_seed: 42
  deterministic_where_supported: true

content:
  max_demo_rows: 3
  max_table_rows: 10
  keep_outputs_compact: true
  require_task_mapping_tags: true

final_inference:
  require_saved_model_reload: true
  require_final_cell_is_last_cell: true
  require_final_cell_self_contained: true
  require_task1_demo: true
  require_task2a_demo: true
  require_clear_input_print: true
  require_clear_prediction_print: true
  require_submission_parity_check: true
  do_not_write_official_outputs: true

privacy:
  public_repo_may_contain_executed_private_outputs: false
  print_full_private_rows: false
  max_demo_rows: 3
```

The seed is a WayLoom engineering default unless a frozen phase requires a different specific seed.

---

# 10. Notebook cell metadata/tags

Use notebook cell tags to make the final artifact machine-checkable.

Recommended task tags:

```text
dt-389
...
dt-411
```

Recommended semantic tags:

```text
overview
configuration
data-loading
data-validation
task1-labels
preprocessing
eda-summary
feature-engineering
task1-training
task1-evaluation
task2a-aggregation
task2a-backtesting
task2a-evaluation
task2b-summary
final-inference
```

The final code cell should be tagged:

```text
dt-404
dt-405
dt-406
dt-407
dt-408
final-inference
```

Do not retain final tags such as:

```text
scratch
temporary
broken
debug
```

---

# 11. Required notebook ordering

Recommended final sequence:

```text
Title + confidentiality
Project overview
Imports/config/reproducibility
Data loading
Data validation
Task1 label construction
Preprocessing
EDA summary
Task1 feature engineering
Task1 training replay
Task1 evaluation
Task2A aggregation/history
Task2A feature construction
Task2A training/backtesting
Task2A evaluation
Task2B summary/pointer
Final Saved-Model Inference markdown heading
FINAL CODE CELL
```

The **final code cell must be the last cell in the notebook**.

No markdown or cleanup cell may follow it.

---

# 12. DT-389 — Create `TeamName_FinalNotebook.ipynb`

Create a valid `nbformat` v4 notebook.

Requirements:

- correct official/master naming pattern;
- Python kernel metadata;
- relative project paths;
- no machine-specific absolute paths;
- no notebook environment-install cells;
- no internet-download cell;
- no secrets/API keys;
- no broken output;
- readable markdown headings;
- deterministic cell order;
- no dependency on a browser extension or hidden notebook widget.

The notebook should be immediately understandable to a judge when opened.

---

# 13. Notebook title and metadata

The first markdown cell should identify:

```text
WayLoom Datathon
Rootcode Tech-Triathlon 2026
Final Competition Notebook
```

Include a concise scope statement for Task 1, Task 2A and Task 2B.

Include a confidentiality note such as:

> This notebook operates on competition data locally and is intended for the authorized competition submission workflow.

Do not include a local user directory or private account detail.

---

# 14. DT-390 — Project/problem overview

Explain all three official Datathon tasks accurately.

## Task 1

Predict, for each test `delivery_id`:

```text
pred_service_min
pred_late_prob
```

## Task 2A

Forecast 10 future weeks per supplied depot+brand+week:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

## Task 2B

Produce a feasible peak-day allocation with:

```text
served/deferred decision
vehicle assignment
trip assignment
written prioritization policy
```

Explain the technical distinction:

```text
Task1 = regression + probability classification
Task2A = time-aware demand forecasting
Task2B = constraint optimization
```

---

# 15. Official output summary in notebook

Use a compact table.

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

No unofficial uncertainty/explainability fields should be presented as official submission columns.

---

# 16. DT-391 — Imports and configuration

Use canonical project modules.

The cell should:

- locate the project root;
- load `configs/final_notebook.yaml`;
- load final Task1/Task2A configs;
- load required feature/history/validation configs;
- set safe reproducibility controls;
- import canonical loaders/validators/feature builders/evaluators.

Do not import abandoned experiment-only packages.

---

# 17. Project-root resolution

Do not use:

```text
C:\Users\...
/home/user/...
```

Use a repository-root resolver based on tracked sentinel files/directories.

Examples:

```text
WAYLOOM_DATATHON_MASTER_PLAN.md
configs/
src/
```

The notebook should run whether opened from the repository root or through Jupyter with the repository as working directory.

---

# 18. Reproducibility settings

Use the frozen random seeds where already defined.

Where the final pipeline uses seed 42, expose it in the notebook.

Do not introduce a different seed just for the notebook.

Record package versions in a compact environment summary cell or execution manifest.

Avoid printing a huge `pip freeze` into the notebook.

---

# 19. DT-392 — Data loading

Use canonical manifest/path loaders.

Do not hard-code CSV paths.

The notebook may load:

## Task 1 historical

- canonical delivery training source;
- canonical route-leg training source;
- required reference tables.

## Task 1 inference demo

- `task1_test_inputs.csv`;
- `route_legs_test.csv`;
- required references.

## Task 2A

- `deliveries_train.csv`;
- `task1_test_inputs.csv`;
- `calendar.csv`;
- `task2a_test_inputs.csv` where needed.

## Task 2B

Prefer safe summary/pointer metadata rather than loading/printing row-level frozen allocation in the notebook.

---

# 20. Data-loading output hygiene

Do not run:

```python
display(df)
```

on full private datasets.

Prefer:

```text
shape
column names
dtypes summary
safe aggregate counts
validation status
```

The final inference cell is the only place that should deliberately show a small number of official test input rows to satisfy the competition requirement.

---

# 21. Missing private data behavior

The notebook must not download data if the local competition dataset is absent.

Fail clearly with a message such as:

```text
Competition data not found in the configured local data root.
Run this notebook in the authorized WayLoom Datathon environment.
```

Do not automatically fetch external copies.

---

# 22. DT-393 — Data validation

Call canonical validators before any modelling section.

Show compact checks for:

```text
required files
required columns
key uniqueness
join-key coverage
timestamp parseability
reference coverage
categorical domains
numeric validity
```

The notebook should fail early if a critical contract fails.

Do not continue with partially invalid data.

---

# 23. Validation output format

Recommended small table:

| Check | Task | Result |
|---|---|---|
| Schema | Task1 | PASS |
| Join keys | Task1 | PASS |
| Demand history inputs | Task2A | PASS |
| Scenario refs | Task2B | PASS |

Do not print the real IDs of failing rows in competition-facing outputs.

---

# 24. DT-394 — Task 1 label construction

Retain executable label-construction cells.

Show official formulas in markdown.

```text
service_start = max(actual arrival, window opening)

service_minutes = leave_outlet_time - service_start

late_flag = 1 only if actual arrival > window_close_time
```

Explicitly state:

```text
early waiting is not service
arrival exactly at close is not late
```

The executable code must call the canonical Phase 4 label implementation.

---

# 25. Task 1 training join

The notebook should show the official training join concept:

```text
deliveries_train.(route_id, seq_in_route)
↔
route_legs_train.(route_id, seq)
```

Use the canonical join helper.

Do not create an alternate join in the notebook.

---

# 26. Task 1 label validation

Run canonical checks and show aggregate status.

Examples:

```text
join coverage: PASS
service target finite/nonnegative: PASS
late label binary: PASS
strict close boundary: PASS
```

Do not print private row IDs.

---

# 27. DT-395 — Preprocessing cells

Retain executable preprocessing cells for the final pipelines.

Task1 may include, according to actual implementation:

```text
time normalization
reference joins
categorical normalization
numeric coercion
planned-route preparation
```

Task2A may include:

```text
order-history normalization
calendar mapping
weekly panel construction
```

Use canonical source modules.

---

# 28. Fitted preprocessing objects

If a model requires fitted preprocessors:

- fit evaluation copies inside the correct training split;
- keep notebook replay copies private/in-memory;
- never overwrite frozen canonical preprocessors;
- final inference cell reloads Phase 32 validated objects.

If final models rely on native categorical support or no fitted preprocessor, document that actual design instead.

---

# 29. DT-396 — EDA summary

Add only the EDA needed to explain model decisions.

Recommended Task1 summaries:

```text
service target distribution
late class balance
selected operational segments
```

Recommended Task2A summaries:

```text
weekly demand trend
brand/depot aggregate behavior
chilled vs total for Fresh
```

Keep the number of figures/tables small.

---

# 30. EDA privacy and readability

No real identifiers in plot labels.

No row-level hover widgets that leak records.

No huge correlation matrix unless it is genuinely useful and readable.

Figures should have:

```text
title
axis labels
units
legend when needed
```

---

# 31. DT-397 — Feature engineering

Retain executable final feature-engineering cells.

Do not show abandoned candidate features as if they were final.

Use final feature registries/configs.

Display:

```text
final feature groups
feature count
small semantic examples
```

Do not display a 300-column raw feature matrix.

---

# 32. Task 1 leakage guard

The notebook must explicitly demonstrate that direct current predictors exclude:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

Run the canonical feature leakage audit and show a compact PASS.

Historical target-derived features, if used, must be chronology-safe.

---

# 33. Task 2A chronology guard

The notebook must show that:

```text
lags use past weeks
rolling values use past weeks
future forecast targets are unavailable
rolling validation preserves time order
```

Call canonical chronology checks.

---

# 34. DT-398 — Task 1 training cells

Retain executable training cells for the frozen final Task1 configurations.

This section is **not a new model-selection phase**.

Do not:

```text
run Optuna/grid/random search
try new model families
retune after inspecting test predictions
change final feature set
change class-positive mapping
change calibration policy
```

Use Phase 9/10 frozen final configs.

---

# 35. Notebook Task 1 training behavior

Recommended:

```text
load frozen config
construct frozen train/validation data
fit evaluation replay model(s)
evaluate
show compact final-config result
```

Any fitted notebook replay model should remain in memory or private runtime storage.

Do not overwrite canonical `models/task1_*` paths.

---

# 36. Task 1 training output

Display only useful evidence:

```text
selected service family/config
selected late family/config
training completion
safe training/validation counts if appropriate
```

No full training logs if excessively long.

---

# 37. DT-399 — Task 1 evaluation

Use the frozen validation contract.

Report actual canonical metrics.

Possible metrics depend on final implementation; do not invent them.

Show a compact table for:

```text
service regression
late-probability/classification
calibration if applicable
```

Never use official test labels.

---

# 38. Task 1 baseline context

A small baseline vs final table is useful if safe and already supported by frozen evidence.

Do not re-run the entire model competition.

The goal is to show why the final configuration was reasonable.

---

# 39. DT-400 — Task 2A aggregation

Retain executable cells implementing the official demand-history logic:

```text
deliveries_train
+
task1_test_inputs
```

Then:

```text
each unique order once
include deferred/not_run orders
requested order_date
calendar ISO year/week
depot + brand + week aggregation
```

Only Fresh has chilled demand.

---

# 40. Task 2A history validation

Show compact status:

```text
both source inputs loaded: PASS
unique-order rule: PASS
calendar coverage: PASS
weekly grain validation: PASS
```

Do not print real order IDs.

---

# 41. DT-401 — Task 2A training/backtesting

Retain executable rolling/time-aware backtesting cells.

Use the final frozen strategy.

Do not:

```text
randomly split weeks
use future folds for earlier origins
change horizon from 10 weeks
introduce a new model family
retune on future test data
```

Use reusable Phase 14/16/17 functions.

---

# 42. Task 2A runtime orchestration

If final strategy uses multiple horizons/models, call one reusable backtest orchestrator.

Do not create ten manually duplicated model cells.

Display:

```text
validation design
forecast horizon 1..10
final strategy name
completion status
```

---

# 43. DT-402 — Task 2A evaluation

Display canonical rolling-backtest performance.

Include actual final metrics for:

```text
total volume
chilled volume
horizon summary if part of frozen evaluation
```

Do not use future competition test outcomes.

---

# 44. Task 2A output-rule check

Demonstrate final forecast post-processing rules on evaluation/demo predictions:

```text
total >= 0
chilled >= 0
chilled <= total
Style chilled = 0
Tech chilled = 0
```

No uncertainty fields in the official output section.

---

# 45. DT-403 — Task 2B summary/pointer

Task2B does not require a trained model.

The notebook should not rerun the full optimizer.

Use a concise competition-facing summary covering:

```text
S1 scenario inputs
available fleet
compatibility
trip time
seven hard rules
WayLoom lexicographic policy
OR-Tools CP-SAT
freeze/audit
independent validator
organizer checker
final CSV
written policy
```

---

# 46. Task 2B trip-time formula

Include:

```text
trip_minutes
=
depot_to_district_freeflow_min
+
inter_stop_freeflow_min * (num_orders - 1)
+
sum(service_allowance_min)
```

State:

```text
No return leg.
```

---

# 47. Task 2B hard constraints

Summarize the official seven groups:

```text
same brand + district per trip
chilled -> reefer
van_only -> van
home depot match
whole order / no split
weight + volume capacity
max 2 trips + Fresh <=270 + Style+Tech <=480
```

Do not add Hackathon fuel/window rules.

---

# 48. Task 2B policy distinction

Clearly state:

```text
Official hard feasibility
```

is separate from:

```text
WayLoom engineering priority policy
```

Summarize the frozen Phase21 hierarchy accurately.

Do not present it as organizer priority.

---

# 49. Task 2B checker semantics

State:

```text
organizer check_allocation.py proves feasibility only
```

It does not prove optimality.

Point to:

```text
outputs/submission_task2b.csv
docs/task2b_policy.md
```

Do not display private order assignments.

---

# 50. DT-404 — Final inference section

Add a markdown heading immediately before the last code cell:

```text
# Final Saved-Model Inference Demonstration
```

Explain that the final cell:

```text
reloads saved artifacts from disk
runs Task1 inference
runs Task2A inference
prints selected inputs and predictions
performs parity checks
writes no official outputs
```

---

# 51. Final cell must actually be final

The final inference code cell is the **last notebook cell**.

Do not place after it:

```text
markdown conclusion
cleanup cell
export cell
empty cell
debug cell
```

If a conclusion is needed, put it before the final inference heading.

---

# 52. DT-405 — Load saved models in the final cell

The final cell must load saved artifacts itself.

It may import canonical loader helpers, but it must not reuse:

```text
service_model
late_model
task2a_model
preprocessor
```

objects from earlier cells.

Paths must come from final configs / Phase32 artifact management.

Do not hard-code a guessed Task2A artifact path.

---

# 53. Phase 32 gate for DT-405

Before DT-412–DT-419 PASS:

```text
DT-405 cannot be FINAL PASS.
```

The notebook can still be structurally complete.

The validator should report:

```text
PHASE32 SAVED ARTIFACT GATE: AWAITING_PHASE32
```

After Phase32, rerun all Phase31 execution gates.

---

# 54. Final-cell self containment

The final cell should locally import:

```text
Path / required standard utilities
canonical config loader
Task1 saved-artifact loader / predictor
Task2A saved-artifact loader / predictor
safe display utilities
```

It should resolve the project root and configs within the cell or imported canonical helper.

It should not require a notebook variable defined hours earlier.

---

# 55. Strong hidden-state proof

After Phase32, execute the final cell **alone** in a fresh kernel.

Recommended execution strategy:

- extract the last cell into a temporary one-cell notebook;
- preserve required notebook metadata/environment;
- start a new kernel;
- execute it;
- require full Task1/Task2A inference success.

This is stronger than only restarting and running all.

---

# 56. DT-406 — Task 1 saved-model inference demo

The final cell should:

```text
load Task1 test inputs through canonical loader
select deterministic 1–3 demo rows
construct prediction-time features
reload saved service model
reload saved late model/calibrator
predict service minutes
predict late probability
compare to frozen canonical final output
print selected inputs
print predictions
```

Do not write `outputs/submission_task1.csv`.

---

# 57. Task 1 demo input display

Show only a small human-readable input view.

Possible fields, depending on actual test contract:

```text
delivery_id
brand/district
window fields
planned timing fields
planned travel/distance
order size
```

Do not print:

```text
actual_arrival
actual_leave
actual_travel
training target
hundreds of encoded features
```

Use actual available test columns only.

---

# 58. Task 1 demo selection

Use deterministic official order:

```text
first N rows
```

with:

```text
N <= 3
```

by default.

Do not cherry-pick low-risk/high-risk examples for appearance.

---

# 59. Task 1 final-cell parity

Compare the newly loaded-model predictions to the frozen official output for the selected demo rows.

Use the canonical numerical tolerance from artifact/inference validation.

Require:

```text
TASK 1 SAVED-MODEL PARITY: PASS
```

Mismatch blocks the phase.

---

# 60. DT-407 — Task 2A saved-model inference demo

The final cell should:

```text
load saved Task2A artifact(s)
load/reconstruct required demand-history context
load future Task2A grid
run frozen final inference in memory
select 1–3 deterministic display rows
compare against frozen official output
print inputs
print predictions
```

Do not rewrite `outputs/submission_task2a.csv`.

---

# 61. Task 2A demo input display

Show compact forecast context:

```text
row_id
depot
brand
iso_year
iso_week
forecast_horizon if the final strategy exposes it
```

Then print:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

No historical raw order rows.

---

# 62. Task 2A final-cell parity

Compare selected predictions with the frozen final output.

Require:

```text
TASK 2A SAVED-MODEL PARITY: PASS
```

For Style and Tech, chilled must remain exactly zero.

Mismatch blocks Phase31/Phase32 artifact integrity.

---

# 63. DT-408 — Clearly print inputs and predictions

The final cell output should contain four obvious blocks:

```text
TASK 1 — INPUTS
TASK 1 — PREDICTIONS
TASK 2A — INPUTS
TASK 2A — PREDICTIONS
```

Use compact pandas displays or clear tabular printing.

Avoid raw numpy arrays without labels.

---

# 64. Final cell parity status

Also print:

```text
TASK 1 SAVED-MODEL PARITY: PASS
TASK 2A SAVED-MODEL PARITY: PASS
```

If parity fails, raise an exception.

Do not continue and display misleading output.

---

# 65. Final cell must not write official outputs

The final inference demonstration is read-only.

Do not call export routines targeting:

```text
outputs/submission_task1.csv
outputs/submission_task2a.csv
```

Use in-memory prediction functions or private temporary paths only.

---

# 66. DT-409 — Restart kernel and run all

This is a required local execution gate.

Run:

```text
fresh kernel
cell 1 → final cell
```

No preloaded variables.

No manual cell skipping.

No interactive repair midway.

Save the executed notebook privately.

---

# 67. Recommended `scripts/execute_final_notebook.py`

Implement a wrapper around `nbclient` / Jupyter execution.

Required capabilities:

```text
--mode run-all
--mode final-cell-only
fresh kernel
project-root working directory
execution timeout
fail on error
private output notebook path
execution summary JSON
```

Do not execute into the tracked source notebook by default.

---

# 68. Run-all output validation

Require:

```text
all code cells executed
0 execution errors
final cell executed
Task1 input/prediction output present
Task2A input/prediction output present
parity PASS markers present
```

A notebook that merely opens is not sufficient.

---

# 69. DT-410 — Remove broken/temporary cells

Remove:

```text
scratch EDA
failed models
commented tuning loops
debug path hacks
manual file copies
TODO/TBD cells
empty abandoned code cells
traceback outputs
install cells
old model names
```

Keep concise explanatory markdown.

---

# 70. No environment-install cells

The final notebook must not contain:

```text
!pip install
%pip install
!conda install
```

Environment reproducibility belongs in requirements and Phase39 reproduction work.

If a dependency is missing, fail clearly.

---

# 71. No network/data download cells

The notebook should not call external services to retrieve competition data or models.

Reject unjustified use of:

```text
requests
urllib
wget
curl
external model APIs
```

All competition data/model artifacts are local.

---

# 72. DT-411 — Ensure no hidden state

Final closure requires both:

```text
CLEAN-KERNEL RUN-ALL: PASS
```

and:

```text
FINAL-CELL-ONLY FRESH KERNEL: PASS
```

The second test is especially important because the official final cell must load saved models rather than relying on earlier training state.

---

# 73. Hidden-state examples that must fail

Examples:

```text
final cell uses `service_model` created in DT-398
final cell uses preprocessor variable from DT-395
final cell depends on earlier `os.chdir`
final cell uses helper function defined only in an earlier notebook cell
final cell uses a mutable global DataFrame built earlier
final cell depends on IPython history
```

Import helpers from `src/` instead.

---

# 74. Static hidden-state validation

`validate_final_notebook.py` should inspect the final cell for:

```text
explicit imports
explicit config/path resolution
explicit saved-artifact loading
Task1 predictor call
Task2A predictor call
input display
prediction display
```

Static checks supplement but do not replace runtime final-cell-only execution.

---

# 75. Training/evaluation runtime design

The notebook may be computationally heavier than a demo notebook because the official deliverable requires training/evaluation cells.

Still, avoid unnecessary repeated work.

Do not run:

```text
hyperparameter sweeps
full candidate model searches
repeated feature ablations
optional Phase25/26/27 heavy analysis
```

Replay only the final frozen methodology and compact baseline context.

---

# 76. Task 1 training artifacts in notebook

Notebook replay models must be temporary.

Recommended:

```text
reports/private/phase31_final_notebook/runtime_models/task1/
```

or in-memory only.

Never write to canonical Phase10/32 model artifact paths.

---

# 77. Task 2A backtest artifacts in notebook

Use private runtime/cache paths only if needed.

Do not overwrite Phase17/32 final model artifacts.

Do not persist forecast rows to public/tracked paths.

---

# 78. Task 2B notebook behavior

Task2B should remain a summary/pointer because:

- no trained model is required;
- the optimizer is already frozen;
- rerunning it adds risk and runtime;
- the official Task2B output/policy are separate deliverables.

Do not turn the final notebook into a second Task2B solver run.

---

# 79. Privacy boundary for notebook outputs

The notebook is a competition submission artifact and may locally operate on private competition data.

However:

```text
external agent must not inspect private rows
public repository should not contain executed private outputs
source notebook should avoid embedded private row values
```

The human local run may produce a private executed notebook for authorized submission.

---

# 80. Final inference output privacy

The official requirement says to clearly print inputs and predictions.

Use the minimum needed to satisfy that:

```text
1–3 Task1 rows
1–3 Task2A rows
selected readable columns
```

Do not print entire test datasets.

---

# 81. Notebook execution manifest

Create private:

```text
reports/private/phase31_final_notebook/run_manifest.json
```

Recommended fields:

```text
phase
source notebook SHA256
executed notebook SHA256
kernel/python versions
package versions
execution duration
cell counts
error count
run-all result
final-cell-only result
Phase32 artifact gate result
Task1 saved-model parity
Task2A saved-model parity
frozen output hash result
frozen model artifact hash result
git commit
```

No row-level values.

---

# 82. Frozen output hash guard

Before and after the local notebook execution, hash:

```text
outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv
docs/task2b_policy.md
```

Require unchanged.

The notebook may read them for parity/reference.

---

# 83. Frozen model hash guard

After Phase32 finalizes artifacts, hash canonical model/preprocessing files before and after notebook execution.

Require unchanged.

Notebook training replay must not mutate saved model artifacts.

---

# 84. Official Task 1 model-load parity

The final cell should use the same canonical saved-model inference interface that Phase10/32 validate.

Do not reconstruct a model from config and call that "loading saved models."

Actual serialized artifact loading is required.

---

# 85. Official Task 2A model-load parity

Phase17 may have runtime fit state but Phase32 owns final artifact management.

After Phase32, the final cell must load the actual saved Task2A artifact(s) and any required preprocessing state.

No silent retraining fallback.

If an artifact is missing:

```text
FAIL
```

not:

```text
retrain automatically
```

---

# 86. Task 2A baseline-champion edge case

Phase17 supports the possibility that the frozen champion is baseline-based.

If so, Phase32/31 artifact loading should faithfully persist/load the baseline parameters/state required for inference.

Do not force a learned model artifact if the frozen final strategy is a baseline.

The final cell still must load saved final inference state rather than recompute it from hidden notebook state.

---

# 87. Calibration edge case

If final Task1 lateness uses calibration:

load the saved calibrator and positive-class metadata.

If calibration is not used:

do not invent a calibrator in the notebook.

---

# 88. Fitted feature-state edge case

If Task1/Task2A inference needs:

```text
encoders
feature schemas
category maps
imputers
scalers
historical state
```

Phase32 must save them as needed and the final cell must load them.

No hidden reconstruction from validation notebook state.

---

# 89. EDA output size gate

Keep EDA compact.

Recommended maximum:

```text
~4–8 figures total across Task1 + Task2A
```

This is a WayLoom readability guideline, not an organizer rule.

If more are necessary, justify them.

---

# 90. Table output size gate

Default:

```text
<=10 displayed rows
```

outside the final input demo.

Use aggregate summaries.

Do not embed thousands of rows into notebook output.

---

# 91. Warning handling

Do not globally suppress all warnings.

It is acceptable to suppress a known, documented benign library warning narrowly.

Execution warnings that indicate feature mismatch, convergence failure or deprecated inference behavior must remain visible and be resolved.

---

# 92. Notebook markdown quality

Use concise explanations before code cells.

Explain:

```text
what the cell does
why it matters
what official rule it protects
```

Avoid one-line headings with no context or long report-style essays.

Phase30 contains the full preprocessing write-up.

---

# 93. Link to Phase29/30 docs

Where helpful, reference relative paths:

```text
docs/architecture/high_level_datathon.svg
docs/preprocessing.md
```

Do not depend on rendered images to execute the notebook.

If Phase29/30 are not yet final, do not add broken links/placeholders.

---

# 94. Notebook validator: `scripts/validate_final_notebook.py`

Required checks:

```text
file exists
nbformat v4
kernel metadata
expected section headings
task tags/mapping
final code cell is last
final cell tags correct
no cells after final code cell
no placeholder/TODO/TBD
no pip/conda install
no network data download
no proprietary API inference
no absolute local paths
no secrets
no public embedded private outputs
required official formulas/rules present
saved-model reload markers present
no official submission write in final cell
executed-copy error count zero when provided
Phase32 dependency handled truthfully
```

---

# 95. `scripts/execute_final_notebook.py`

Recommended CLI:

```text
--input
--output
--config
--mode run-all|final-cell-only
--timeout
```

Requirements:

- fresh kernel for each execution;
- repository root working directory;
- deterministic environment vars where required;
- fail on code exception;
- never overwrite frozen official outputs;
- private execution output by default.

---

# 96. Optional deterministic notebook builder

`scripts/build_final_notebook.py` is optional.

Use it only if it improves reproducibility.

If used:

- generate `nbformat` notebook deterministically;
- preserve markdown/code cell order;
- attach task tags;
- do not embed private outputs;
- avoid duplicating long code snippets from `src/`.

Do not require the builder to execute private data.

---

# 97. Tests — structure

Create:

```text
tests/test_final_notebook_structure.py
```

Test:

- notebook exists;
- nbformat version;
- nonzero cell count;
- all required sections;
- all DT-389–DT-411 task mappings;
- final cell is code;
- final cell is last;
- no cell after final inference;
- kernel metadata;
- no abandoned empty code cells.

---

# 98. Tests — official contract semantics

Create:

```text
tests/test_final_notebook_contract.py
```

Require semantic coverage of:

```text
Task1 service_start max(arrival, open)
service = leave - service_start
late strict > close
early wait not service
Task1 actual-field leakage boundary
Task2A deliveries_train + task1_test_inputs
unique order once
deferred/not_run included
requested week / ISO calendar
10-week validation
Style/Tech chilled zero
Task2B no trained model
Task2B exact trip formula/no return
seven hard rules
WayLoom priority separate
organizer checker feasibility-only
```

---

# 99. Tests — final inference cell

Create:

```text
tests/test_final_notebook_final_inference.py
```

Static/synthetic-safe checks:

```text
final cell imports canonical loader/predictor helpers
explicit saved-artifact load
Task1 prediction call
Task2A prediction call
input-print markers
prediction-print markers
parity check markers
no training/search call
no write to official submission path
max demo rows respected
```

Runtime private checks are performed locally.

---

# 100. Tests — privacy

Create:

```text
tests/test_final_notebook_privacy.py
```

Reject source notebook content containing:

```text
C:\Users\...
user-specific /home/... paths
API keys/tokens
hardcoded real private IDs
embedded full private DataFrames
raw official test table outputs
network upload code
external proprietary prediction APIs
```

No private data access required for the test.

---

# 101. Tests — hidden state

Create:

```text
tests/test_final_notebook_no_hidden_state.py
```

Static checks:

```text
final cell self-imports helpers
final cell resolves config/path
final cell loads artifacts explicitly
final cell has no `%run` scratch dependency
final cell has no obvious earlier model-variable dependency
```

Runtime final-cell-only fresh-kernel test is mandatory after Phase32.

---

# 102. Synthetic test strategy

External-agent safe tests should not execute private real data.

Use synthetic fixtures to test reusable notebook-support functions where needed.

Do not create a second synthetic version of the final notebook that can drift from the real source.

Static validation + canonical module tests + human local execution are preferred.

---

# 103. Clean-kernel run command

Recommended:

```bash
python scripts/execute_final_notebook.py   --input TeamName_FinalNotebook.ipynb   --output reports/private/phase31_final_notebook/TeamName_FinalNotebook.executed.ipynb   --config configs/final_notebook.yaml   --mode run-all
```

Use actual implemented CLI.

---

# 104. Final-cell-only command

After Phase32:

```bash
python scripts/execute_final_notebook.py   --input TeamName_FinalNotebook.ipynb   --output reports/private/phase31_final_notebook/final_cell_only.executed.ipynb   --config configs/final_notebook.yaml   --mode final-cell-only
```

Must use a fresh kernel.

---

# 105. Notebook validation command

Recommended:

```bash
python scripts/validate_final_notebook.py   --source TeamName_FinalNotebook.ipynb   --executed reports/private/phase31_final_notebook/TeamName_FinalNotebook.executed.ipynb   --final-cell-executed reports/private/phase31_final_notebook/final_cell_only.executed.ipynb   --config configs/final_notebook.yaml
```

---

# 106. Safe test loop

Run:

```bash
pytest -q   tests/test_final_notebook_structure.py   tests/test_final_notebook_contract.py   tests/test_final_notebook_final_inference.py   tests/test_final_notebook_privacy.py   tests/test_final_notebook_no_hidden_state.py
```

Then relevant frozen Task1/Task2A/Task2B tests.

Then:

```bash
pytest -q
python -m pip check
git diff --check
git status
```

Do not run private real-data notebook in the external agent.

---

# 107. Human-local sanitized execution result

Target after Phase32:

```text
WAYLOOM — PHASE 31 FINAL NOTEBOOK

SOURCE NOTEBOOK STRUCTURE                 : PASS
TASK MAPPING DT-389–DT-411               : PASS

TASK1 LABEL / PREPROCESSING CELLS         : PASS
TASK1 TRAINING / EVALUATION CELLS         : PASS
TASK2A AGGREGATION CELLS                  : PASS
TASK2A BACKTEST / EVALUATION CELLS        : PASS
TASK2B SUMMARY                            : PASS

PHASE32 SAVED ARTIFACT GATE               : PASS
FINAL CELL LOADS SAVED MODELS             : PASS
TASK1 INFERENCE DEMO                      : PASS
TASK2A INFERENCE DEMO                     : PASS
INPUTS PRINTED                            : PASS
PREDICTIONS PRINTED                       : PASS

CLEAN-KERNEL RUN-ALL                      : PASS
FINAL-CELL-ONLY FRESH KERNEL              : PASS
HIDDEN STATE DEPENDENCY                   : NONE

EXECUTION ERRORS                          : 0
BROKEN/TEMP CELLS                         : 0

TASK1 SAVED-MODEL PARITY                  : PASS
TASK2A SAVED-MODEL PARITY                 : PASS

OFFICIAL OUTPUTS CHANGED                  : NO
SAVED MODEL ARTIFACTS CHANGED             : NO

PHASE 31                                  : PASS
READY FOR INDEPENDENT REVIEW              : YES
```

Do not include private prediction values in the sanitized handoff.

---

# 108. Edge case — Phase32 pending

This is expected during initial implementation.

Do not fake final closure.

Correct status:

```text
PHASE31 CORE NOTEBOOK: READY
DT-405: BLOCKED_BY_PHASE32
DT-409: PRELIMINARY/PENDING FINAL
DT-411: PRELIMINARY/PENDING FINAL
AUTHORIZED NEXT ACTION: PHASE32
READY FOR PHASE33: NO
```

---

# 109. Edge case — Task2A artifact not serialized yet

Phase17 final inference may exist without the Phase32 formal serialized artifact bundle.

Do not:

```text
fit Task2A model inside final cell
pickle it from notebook state
hardcode a private runtime object
```

Wait for Phase32.

---

# 110. Edge case — final cell alone fails

If run-all passes but final-cell-only fresh kernel fails:

```text
DT-411 FAIL
```

This is hidden state.

Fix the cell's imports/path/model/data loading.

---

# 111. Edge case — run-all fails

If final cell works alone but full notebook fails:

```text
DT-409 FAIL
```

The official notebook must run top-to-bottom.

Resolve earlier cell failure.

---

# 112. Edge case — output parity mismatch

If final loaded-model predictions differ from frozen final output:

Stop.

Possible causes:

```text
wrong artifact
wrong preprocessor
wrong feature order
wrong calibration
wrong model version
wrong historical forecast state
numeric drift beyond approved tolerance
```

Do not change official CSV to match the notebook.

---

# 113. Edge case — notebook overwrites models

Immediate blocker.

Training replay output belongs in a private runtime location.

Restore canonical artifacts from verified source.

Rerun Phase32/affected integrity checks.

---

# 114. Edge case — notebook overwrites official CSVs

Immediate blocker.

Final inference is read-only.

Remove canonical export calls from notebook.

---

# 115. Edge case — model search accidentally retained

If notebook contains grid/random/Bayesian search cells:

remove them from final notebook unless the cell is strictly historical evidence required by the official final process and can run deterministically without changing final choices.

Preferred final notebook shows final training/evaluation, not the entire research history.

---

# 116. Edge case — stale model names

If markdown names a different model family than the final config:

fail.

Update notebook text to final frozen config.

Do not change model.

---

# 117. Edge case — huge executed notebook

If executed notebook becomes very large because of tables/images:

- reduce display rows;
- simplify EDA;
- use reasonable image dimensions;
- clear unnecessary training logs.

Do not remove required inference output.

---

# 118. Edge case — warnings obscure output

Resolve important warnings.

Narrowly suppress only known benign warnings.

Do not globally suppress all warnings.

---

# 119. Edge case — package path differs on Windows/Linux

Use `pathlib` and project-relative paths.

Avoid shell-specific path concatenation.

Notebook should be reproducible later in Phase39 clean-environment testing.

---

# 120. Edge case — team name not yet configured

Do not invent a team name.

The master name `TeamName_FinalNotebook.ipynb` is a pattern.

Use the canonical team name if already tracked.

Otherwise Phase40 packaging must resolve the final name before submission.

---

# 121. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-31-final-notebook
```

Recommended commits:

```text
feat(notebook): add final competition notebook structure
feat(notebook): add Task1 labels preprocessing training evaluation
feat(notebook): add Task2A aggregation backtesting evaluation
feat(notebook): add Task2B summary and saved-model inference section
test(notebook): validate final notebook contract and hidden-state safety
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run safe tests.

Do not stage private executed notebook evidence.

---

# 122. Public-repository safety

If the repository is public or may later be shared publicly:

commit only the output-cleared source notebook.

Do not commit:

```text
reports/private/phase31_final_notebook/**
```

The competition packaging phase may use the privately executed validated notebook.

---

# 123. STOP conditions

`PHASE 31 FINAL PASS` remains **NO** if any of the following holds:

- any DT-389–DT-411 task missing;
- notebook file invalid;
- official notebook requirement incomplete;
- final code cell is not the final notebook cell;
- cell follows final inference cell;
- DT-405 marked PASS before Phase32 artifact management passes;
- final cell does not load serialized saved models;
- final cell silently retrains;
- final cell relies on earlier model objects;
- final-cell-only fresh-kernel run fails;
- clean-kernel run-all fails;
- execution errors exist;
- Task1 label formula incorrect;
- Task1 strict late boundary incorrect;
- actual current Task1 fields become predictors;
- Task2A history rules incorrect;
- Task2A backtesting leaks future data;
- Task2B optimizer is unnecessarily rerun;
- Task2B checker mislabeled as optimality proof;
- new model search/tuning appears;
- final model names differ from frozen config;
- notebook writes frozen models;
- notebook writes official CSVs;
- loaded-model parity fails;
- broken/temp/TODO cells remain;
- source notebook contains private row dumps/secrets/absolute user paths;
- environment-install cells remain;
- network/proprietary modelling calls remain;
- frozen artifacts change;
- tests fail;
- `pip check` fails;
- independent Phase31 review fails.

---

# 124. Definition of Done — Stage A core implementation

Before Phase32, the notebook core is ready only when:

- [ ] DT-389 READY
- [ ] DT-390 READY
- [ ] DT-391 READY
- [ ] DT-392 READY
- [ ] DT-393 READY
- [ ] DT-394 READY
- [ ] DT-395 READY
- [ ] DT-396 READY
- [ ] DT-397 READY
- [ ] DT-398 READY
- [ ] DT-399 READY
- [ ] DT-400 READY
- [ ] DT-401 READY
- [ ] DT-402 READY
- [ ] DT-403 READY
- [ ] DT-404 READY
- [ ] DT-406 READY
- [ ] DT-407 READY
- [ ] DT-408 READY
- [ ] DT-410 READY
- [ ] source notebook validator PASS
- [ ] targeted safe tests PASS
- [ ] frozen artifacts unchanged
- [ ] no private data exposed to external agent

And:

```text
DT-405 = BLOCKED_BY_PHASE32
DT-409 = PENDING FINAL CLEAN RUN
DT-411 = PENDING FINAL HIDDEN-STATE PROOF
```

Then:

```text
PHASE 31 CORE STATUS: READY
AUTHORIZED NEXT ACTION: PHASE32 ARTIFACT MANAGEMENT
PHASE 31 FINAL STATUS: PENDING
READY FOR PHASE33: NO
```

---

# 125. Definition of Done — final closure after Phase32

Phase 31 is fully complete only when:

- [ ] DT-389 PASS
- [ ] DT-390 PASS
- [ ] DT-391 PASS
- [ ] DT-392 PASS
- [ ] DT-393 PASS
- [ ] DT-394 PASS
- [ ] DT-395 PASS
- [ ] DT-396 PASS
- [ ] DT-397 PASS
- [ ] DT-398 PASS
- [ ] DT-399 PASS
- [ ] DT-400 PASS
- [ ] DT-401 PASS
- [ ] DT-402 PASS
- [ ] DT-403 PASS
- [ ] DT-404 PASS
- [ ] DT-405 PASS
- [ ] DT-406 PASS
- [ ] DT-407 PASS
- [ ] DT-408 PASS
- [ ] DT-409 PASS
- [ ] DT-410 PASS
- [ ] DT-411 PASS
- [ ] Phase32 DT-412–DT-419 PASS
- [ ] final saved models/preprocessors load from disk
- [ ] final cell is last cell
- [ ] final cell self-contained
- [ ] Task1 saved-model inference PASS
- [ ] Task2A saved-artifact inference PASS
- [ ] Task1 parity PASS
- [ ] Task2A parity PASS
- [ ] inputs clearly printed
- [ ] predictions clearly printed
- [ ] clean-kernel run-all PASS
- [ ] final-cell-only fresh-kernel PASS
- [ ] hidden state NONE
- [ ] execution errors 0
- [ ] temporary/broken cells 0
- [ ] official output hashes unchanged
- [ ] model artifact hashes unchanged
- [ ] source notebook privacy PASS
- [ ] full safe test suite PASS
- [ ] `python -m pip check` PASS
- [ ] `git diff --check` PASS
- [ ] fresh independent Phase31 review PASS

Then:

```text
PHASE 31 STATUS: PASS
FINAL NOTEBOOK: COMPETITION-READY
HIDDEN STATE: NONE
FROZEN DATATHON PIPELINES: UNCHANGED
READY FOR PHASE33: YES
```

---

# 126. Recommended model

Phase 31 is high-risk because it consolidates the entire solution into an official evidence artifact and must prove saved-model inference without hidden state.

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

# 127. Ready-to-copy Cursor/Codex implementation prompt

```text
You are implementing WayLoom Datathon PHASE 31 only.

PHASE:
Final Competition Notebook

TASK RANGE:
DT-389 through DT-411

EXECUTION MODE:
NOTEBOOK-AS-EVIDENCE.
REUSE CANONICAL src/ LOGIC.
PRIVATE REAL-DATA EXECUTION IS HUMAN-LOCAL.
NO MODEL SEARCH.
NO FROZEN OUTPUT REGENERATION.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 32 IMPLEMENTATION EXCEPT FOR THE EXPLICIT ARTIFACT-DEPENDENCY HANDOFF DESCRIBED BELOW.
DO NOT START PHASE 33.

==================================================
MISSION
==================================================

Create the official competition notebook:

TeamName_FinalNotebook.ipynb

and make it a faithful, runnable evidence document for the finalized WayLoom
Datathon solution.

The official Challenge Booklet requires the final notebook to:

- retain cells used for label construction;
- retain preprocessing cells;
- retain training cells;
- retain evaluation cells;
- include a final cell that loads SAVED models;
- demonstrate inference for Task 1;
- demonstrate inference for Task 2A;
- clearly print the inputs and predictions.

The finalized master inventory additionally requires:

DT-389 Create TeamName_FinalNotebook.ipynb
DT-390 Add project/problem overview
DT-391 Add imports/configuration
DT-392 Add data loading
DT-393 Add data validation
DT-394 Add Task 1 label construction
DT-395 Add preprocessing cells
DT-396 Add EDA summary
DT-397 Add feature engineering
DT-398 Add Task 1 training cells
DT-399 Add Task 1 evaluation
DT-400 Add Task 2A aggregation
DT-401 Add Task 2A training/backtesting
DT-402 Add Task 2A evaluation
DT-403 Add Task 2B summary/pointer
DT-404 Add final inference section
DT-405 Load saved models in final cell
DT-406 Demonstrate Task 1 inference
DT-407 Demonstrate Task 2A inference
DT-408 Clearly print inputs and predictions
DT-409 Restart kernel and run all
DT-410 Remove broken/temporary cells
DT-411 Ensure notebook runs without hidden state

Do not skip any task.

==================================================
IMPORTANT MASTER-PLAN DEPENDENCY BRIDGE
==================================================

DT-405 explicitly depends on DT-412–DT-419 in Phase 32.

Therefore Phase 31 has TWO gates:

GATE A — NOTEBOOK CORE READY

Implement DT-389–DT-404 and DT-406–DT-411 structurally, using canonical saved-
artifact loader interfaces and final configs.

If Phase 32 has not yet formalized/validated every required saved artifact,
return:

PHASE 31 CORE: READY
DT-405: BLOCKED_BY_PHASE32
AUTHORIZED NEXT ACTION: PHASE 32 ARTIFACT FINALIZATION

Do NOT pretend Phase 31 is finally closed.

GATE B — FINAL PHASE 31 CLOSURE

After DT-412–DT-419 PASS:

- rerun the notebook from a clean kernel;
- run the final inference cell in a fresh kernel by itself;
- prove it reloads saved models and preprocessing state;
- prove Task 1 and Task 2A inference work;
- prove displayed predictions match the frozen inference contract;
- rerun independent Phase 31 review.

Only then can Phase 31 be FINAL PASS.

This staged handoff is a WayLoom engineering orchestration needed to honor the
master inventory's explicit future dependency.

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - execution rules
   - Phase 31 DT-389–DT-411
   - Phase 32 DT-412–DT-419 dependency
   - final checklist
4. Official Challenge Booklet
   - Task 1
   - Task 2A
   - Task 2B
   - restrictions / data confidentiality
   - Deliverables page: final notebook requirement
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
23. PHASE_30_COMPETITION_CONTRACT.md when final/available
24. PHASE_31_COMPETITION_CONTRACT.md

Inspect canonical implementation/configs for the FINAL state.

Do NOT inspect private real rows in external-agent context.

==================================================
OFFICIAL NOTEBOOK REQUIREMENT — DO NOT DILUTE
==================================================

The official booklet requires:

Final notebook (TeamName_FinalNotebook.ipynb).
Retain the cells used for:

- label construction
- preprocessing
- training
- evaluation

Add a FINAL CELL that:

- loads the saved models;
- demonstrates inference for Task 1;
- demonstrates inference for Task 2A;
- clearly prints the inputs and predictions.

The final code cell MUST be the actual last cell in the notebook.

Do not place a markdown appendix after it.
Do not place cleanup/debug cells after it.
Do not rely on model objects created earlier in the notebook.

==================================================
NOTEBOOK PHILOSOPHY
==================================================

The master plan states:

"Notebook is evidence, not the only implementation. Important reusable logic
belongs in src/ and is called from the final notebook where practical."

Therefore:

- do NOT duplicate large production functions in notebook cells;
- import canonical src/ functions;
- keep orchestration/explanation in notebook;
- keep reusable transformations/models/validators in src/;
- do not fork a second notebook-only implementation.

If notebook behavior differs from src/ behavior:
STOP.

==================================================
FROZEN ARTIFACTS — MUST NOT CHANGE
==================================================

Do NOT modify or regenerate:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

configs/task2a_final_models.yaml
Task2A final model/runtime artifacts
outputs/submission_task2a.csv

data/interim/task2b_final_allocation.csv
outputs/submission_task2b.csv
docs/task2b_policy.md
Phase22/23 private evidence

Notebook training/backtesting cells must not overwrite canonical frozen models.

Use private notebook runtime paths for any temporary fitted objects.

==================================================
CREATE / UPDATE
==================================================

Create/update:

TeamName_FinalNotebook.ipynb

configs/final_notebook.yaml

scripts/validate_final_notebook.py
scripts/execute_final_notebook.py

Optional only if deterministic notebook construction is useful:

scripts/build_final_notebook.py

Tests:

tests/test_final_notebook_structure.py
tests/test_final_notebook_contract.py
tests/test_final_notebook_final_inference.py
tests/test_final_notebook_privacy.py
tests/test_final_notebook_no_hidden_state.py

Private local execution evidence:

reports/private/phase31_final_notebook/
  run_manifest.json
  execution_summary.json
  TeamName_FinalNotebook.executed.ipynb
  final_cell_only.executed.ipynb
  frozen_hash_audit.json
  final_inference_parity.json

Do not commit private executed notebook outputs publicly.

==================================================
CONFIG
==================================================

Create:

configs/final_notebook.yaml

Recommended structure:

version: 1
notebook_filename: TeamName_FinalNotebook.ipynb

execution:
  kernel_name: python3
  timeout_seconds: 7200
  working_directory: .
  private_output_dir: reports/private/phase31_final_notebook

reproducibility:
  random_seed: 42
  deterministic_where_supported: true

content:
  max_demo_rows: 3
  max_table_rows: 10
  keep_outputs_compact: true
  require_task_mapping_tags: true

final_inference:
  require_saved_model_reload: true
  require_final_cell_is_last_cell: true
  require_final_cell_self_contained: true
  require_task1_demo: true
  require_task2a_demo: true
  require_clear_input_print: true
  require_clear_prediction_print: true
  require_submission_parity_check: true
  do_not_write_official_outputs: true

privacy:
  public_repo_may_contain_executed_private_outputs: false
  print_full_private_rows: false
  max_demo_rows: 3

Do not invent the actual team name.
If the repository already defines a team name, use it consistently.
Otherwise retain the master-plan pattern until packaging resolves it.

==================================================
NOTEBOOK CELL TAGGING
==================================================

Use cell metadata tags so the notebook can be validated structurally.

Recommended tags:

dt-389
...
dt-411

and semantic tags:

overview
configuration
data-loading
data-validation
task1-labels
preprocessing
eda-summary
feature-engineering
task1-training
task1-evaluation
task2a-aggregation
task2a-backtesting
task2a-evaluation
task2b-summary
final-inference

The final code cell should include:

dt-404
dt-405
dt-406
dt-407
dt-408
final-inference

Do not use tags like:

temporary
scratch
broken
debug-final

in the final notebook.

==================================================
RECOMMENDED NOTEBOOK ORDER
==================================================

0. Title / submission metadata
1. Project and problem overview
2. Imports / configuration / reproducibility
3. Data loading
4. Data validation
5. Task 1 label construction
6. Shared / Task 1 preprocessing
7. Compact EDA summary
8. Task 1 feature engineering
9. Task 1 final-config training/evaluation replay
10. Task 1 evaluation summary
11. Task 2A demand-history aggregation
12. Task 2A forecast feature construction
13. Task 2A final-config rolling backtesting/training
14. Task 2A evaluation summary
15. Task 2B summary/pointer
16. Final inference markdown section
17. FINAL CODE CELL — reload saved models + Task1/Task2A inference + print inputs/predictions

Do not put cells after the final inference code cell.

==================================================
DT-389 — CREATE TeamName_FinalNotebook.ipynb
==================================================

Create a valid nbformat v4 notebook.

Requirements:

- filename matches the master/official naming pattern;
- Python kernel metadata is present;
- relative project paths only;
- no absolute C:\\Users\\... path;
- no /home/<user>/ hardcoding;
- no internet-download cell;
- no `pip install` cell in final notebook;
- no shell commands that alter the environment;
- no API keys/secrets;
- no execution error outputs;
- no hidden notebook extension dependency required for correctness.

The notebook must be understandable when opened directly by a judge.

==================================================
NOTEBOOK TITLE CELL
==================================================

Include:

WayLoom Datathon
Rootcode Tech-Triathlon 2026
Final Competition Notebook

Include a concise confidentiality note:

"This notebook operates on competition data locally and is intended for the
authorized competition submission workflow."

Do not include personal machine paths or secrets.

==================================================
DT-390 — PROJECT / PROBLEM OVERVIEW
==================================================

Add a concise overview of:

Task 1:
predict outlet service minutes and late probability.

Task 2A:
forecast depot/brand total and chilled volume for 10 future weeks.

Task 2B:
produce a feasible peak-day allocation under official vehicle/trip/capacity/
time constraints and explain prioritization.

Explain that the three tasks are technically different:

regression + probability classification
forecasting
constraint optimization

Do not overstate optional Phase25–28 work.

==================================================
OVERVIEW OFFICIAL OUTPUTS
==================================================

State exact official outputs:

Task1:
delivery_id
pred_service_min
pred_late_prob

Task2A:
row_id
pred_total_volume_m3
pred_chilled_volume_m3

Task2B:
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id

Keep concise.

==================================================
DT-391 — IMPORTS / CONFIGURATION
==================================================

Use canonical package imports.

At minimum:

pathlib
pandas / numpy where actually used
plotting library already in project
canonical src/common loaders/validators
Task1 modules
Task2A modules
safe Task2B summary/validator interfaces

Do not import abandoned experiment libraries merely because they exist in
requirements.

Set deterministic seeds where relevant.

Use project-root discovery that works when notebook is started from repository
root or notebook context.

No absolute paths.

==================================================
PROJECT ROOT RESOLUTION
==================================================

Use a deterministic helper such as:

find parent containing:
WAYLOOM_DATATHON_MASTER_PLAN.md
or
configs/

Do not silently chdir to a user-specific directory.

Print:

"Project root resolved"

without printing private workstation-specific absolute paths in saved public
outputs if that would expose usernames.

Prefer relative path reporting.

==================================================
CONFIG LOADS
==================================================

Load final tracked configs.

At minimum as applicable:

configs/dataset_manifest.yaml
configs/task1_final_models.yaml
Task1 feature/inference config
configs/task2a_final_models.yaml
Task2A history/feature/validation/inference config
Task2B scenario/priority/optimizer validation metadata
configs/final_notebook.yaml

Fail if final configs are missing/unfrozen.

Do not select a fallback model in notebook.

==================================================
DT-392 — DATA LOADING
==================================================

Use canonical manifest/path loaders.

Do not hard-code local CSV paths.

Load only datasets needed for the notebook sections.

Task1 historical:
canonical training delivery + route-leg sources and required references.

Task1 test:
task1_test_inputs + route_legs_test for final demo/inference.

Task2A:
deliveries_train + task1_test_inputs + calendar + future grid as needed.

Task2B:
do NOT load row-level private allocation unnecessarily for the notebook if a
safe summary/pointer is sufficient.

No data download from internet.

==================================================
DATA DISPLAY SAFETY
==================================================

Do not display full private datasets.

For intermediate sections prefer:

schema summaries
column lists
aggregate counts
aggregated distributions

The final official inference demonstration may print a SMALL number of input
rows because the organizer requires inputs and predictions to be shown.

Limit:
1–3 demo rows.

Do not dump hundreds of rows.

==================================================
DT-393 — DATA VALIDATION
==================================================

Call canonical validators.

Show compact PASS/FAIL summaries for:

schema
required columns
key uniqueness where required
join coverage
categorical domains
numeric/time sanity
reference coverage

Do not duplicate validator logic in notebook.

No row-level invalid IDs should be printed in the competition-facing output.

If validation fails:
raise and stop execution.

==================================================
VALIDATION OUTPUT STYLE
==================================================

Use a compact table such as:

Check | Task | Status

No raw failing rows.

A judge should see that data correctness was verified before modelling.

==================================================
DT-394 — TASK 1 LABEL CONSTRUCTION
==================================================

Retain executable cells that construct Task1 labels through canonical Phase4
logic.

Show official formulas in markdown:

service_start = max(actual arrival, window opening)

service_minutes = leave_outlet_time - service_start

late_flag = 1 only if actual arrival > window_close_time

Explicitly state:

early waiting is not service
arrival exactly at close is not late

Call canonical implementation for the actual label dataframe.

Do not reimplement a subtly different formula in notebook.

==================================================
TASK1 LABEL VALIDATION
==================================================

Run canonical label assertions/tests on local data.

Display only aggregate/sanitized results:

label rows constructed
service target finite/nonnegative validation
late label domain {0,1}
strict-close check PASS

Do not print real delivery IDs that violate conditions.

==================================================
DT-395 — PREPROCESSING CELLS
==================================================

Retain cells that execute the final preprocessing stages used by the final
pipelines.

Use canonical src/ functions.

Show at a high level:

Task1 join / time normalization / reference enrichment
Task1 final preprocessing state
Task2A demand-history normalization
Task2A calendar/week preparation

Do not create a notebook-only preprocessing fork.

Do not silently mutate raw data files.

==================================================
PREPROCESSING OBJECTS
==================================================

If final models require fitted preprocessing objects:

- use training-split-local objects in evaluation cells;
- do not overwrite canonical saved objects;
- final inference cell reloads Phase32-validated saved preprocessing objects.

If the final model uses native categories / no fitted preprocessor:
reflect that actual design.

==================================================
DT-396 — EDA SUMMARY
==================================================

Add a compact, competition-facing EDA summary.

The notebook is not an exploratory scratchpad.

Recommended Task1 summaries:

service target distribution
late class balance
selected aggregate segment behavior

Recommended Task2A summaries:

weekly total/chilled trend
brand/depot aggregate patterns
forecast history coverage

Keep to a small number of charts/tables.

No row-level identifiers.
No dozens of unused plots.
No private diagnostic dump.

==================================================
EDA FIGURE RULES
==================================================

Use deterministic plotting.

Readable titles/axes.

No external style downloads.

No image file dependency required for notebook execution unless tracked.

Close figures after display where needed.

Do not save private figures to public paths automatically.

==================================================
DT-397 — FEATURE ENGINEERING
==================================================

Retain executable feature-engineering cells.

Task1:
call final frozen feature builder.

Task2A:
call final frozen forecast feature builder.

Display:

final feature-group summary
feature count
selected semantic examples

Do not print hundreds of encoded features unless necessary.

==================================================
FEATURE LEAKAGE GUARD
==================================================

Task1 direct current predictors must NOT include:

actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time

The notebook should run the canonical leakage audit and display PASS.

Task2A lag/rolling features must be past-only relative to forecast origin.

Display a concise chronology/leakage PASS.

==================================================
DT-398 — TASK 1 TRAINING CELLS
==================================================

Retain Task1 training cells using the FINAL frozen model configurations.

Important:

This is NOT a renewed model search.

Do not:

run hyperparameter search
compare new model families
retune from test predictions
change calibration
change feature set

Training/evaluation cells should replay the frozen final configuration under
the frozen validation contract.

==================================================
TASK1 TRAINING ARTIFACT SAFETY
==================================================

Notebook training must NOT overwrite:

models/task1_service/**
models/task1_late/**

Use:

in-memory evaluation models

or:

reports/private/phase31_final_notebook/runtime_models/

for temporary notebook-only fitted objects.

Final inference must load canonical saved models separately.

==================================================
TASK1 TRAINING CELL CONTENT
==================================================

Show:

final service configuration identifier/family
final lateness configuration identifier/family
training split sizes only if safe/appropriate
fit invocation through canonical code
training completion

Do not print full feature matrix.

==================================================
DT-399 — TASK 1 EVALUATION
==================================================

Run the frozen validation/evaluation contract.

Use actual final metrics from the canonical evaluator.

Examples may include regression and probability/classification metrics only
if actually used.

Do not invent metric names.
Do not evaluate on Task1 test labels.

Show a compact metric table.

If calibration is part of final pipeline:
show the relevant calibrated evaluation summary.

==================================================
TASK1 BASELINE CONTEXT
==================================================

The notebook may show a compact final-vs-baseline comparison using already
frozen evidence.

Do not rerun broad model search.

One small table is enough.

==================================================
DT-400 — TASK 2A AGGREGATION
==================================================

Retain executable cells that construct the official demand history:

deliveries_train
+
task1_test_inputs

Rules:

each unique order counted once
include deferred/not_run demand
use requested order_date
map through calendar ISO year/week
aggregate by depot + brand + week
only Fresh has chilled demand

Call canonical Phase11 logic.

==================================================
TASK2A AGGREGATION VALIDATION
==================================================

Display compact checks:

unique-order rule PASS
calendar coverage PASS
weekly panel schema PASS
Style/Tech chilled history rule as applicable

Do not print private order IDs.

==================================================
DT-401 — TASK 2A TRAINING / BACKTESTING
==================================================

Retain executable cells using the FINAL frozen Task2A strategy.

Run the canonical rolling/time-aware backtesting process.

Do not:

randomly split time series
search new model families
change lag windows
change horizon strategy
use future test outcomes

Use exactly the frozen Phase14/16/17 feature/model contract.

==================================================
TASK2A BACKTEST RUNTIME
==================================================

If the final strategy trains multiple horizon models, keep code high-level by
calling reusable backtest functions.

Do not expand ten near-duplicate notebook cells.

Display:

forecast origins/horizon design
final strategy name
backtest completion

Do not print private row-level forecasts.

==================================================
DT-402 — TASK 2A EVALUATION
==================================================

Display frozen rolling-backtest metrics.

Use actual metrics from canonical evaluator.

Show:

total-volume performance
chilled-volume performance
horizon summary if implemented
baseline/final comparison if useful

Do not use future test targets.

==================================================
TASK2A POSTPROCESSING CHECK
==================================================

Demonstrate the frozen output semantics:

nonnegative total/chilled
chilled <= total
Style chilled == 0
Tech chilled == 0

This may be tested on validation/demo outputs.

Do not add Phase27 uncertainty to official outputs.

==================================================
DT-403 — TASK 2B SUMMARY / POINTER
==================================================

Task2B requires no trained model.

Do not rerun the Phase22 optimizer in the final notebook.

Provide a concise summary/pointer:

inputs
compatibility
trip-time formula
seven official hard rules
WayLoom lexicographic policy
OR-Tools CP-SAT
independent validator
organizer checker feasibility-only
final submission path
task2b_policy.md path

Use safe aggregate status only.

Do not print real order/vehicle/trip assignments.

==================================================
TASK2B OFFICIAL FORMULA SUMMARY
==================================================

Include:

trip_minutes
=
outbound
+
inter_stop * (num_orders - 1)
+
sum(service_allowance)

No return leg.

Fresh <=270
Style+Tech <=480
max 2 trips per vehicle

Keep concise.

==================================================
DT-404 — FINAL INFERENCE SECTION
==================================================

Add a markdown heading immediately before the final code cell:

# Final Saved-Model Inference Demonstration

Explain:

- the cell is intentionally independent of training state;
- it reloads saved artifacts from disk;
- it demonstrates Task1 and Task2A inference;
- it does not rewrite official submission files.

Then place the final code cell.

No cells after it.

==================================================
DT-405 — LOAD SAVED MODELS IN FINAL CELL
==================================================

The FINAL CODE CELL must reload saved artifacts.

It must not use:

service_model
late_model
task2a_model
preprocessor

objects created in earlier cells.

It should import canonical loader/predictor functions itself.

Resolve saved artifact paths from canonical final configs / Phase32 artifact
management.

Do not hard-code a guessed Task2A model path.

==================================================
PHASE32 ARTIFACT DEPENDENCY
==================================================

Until DT-412–DT-419 PASS:

DT-405 cannot receive FINAL PASS.

The final cell may already be implemented against canonical loader interfaces,
but the Phase31 validator must report:

SAVED ARTIFACT MANAGEMENT:
AWAITING PHASE32

After Phase32:

verify every required artifact loads and reproduces intended predictions.

==================================================
FINAL CELL SELF-CONTAINMENT
==================================================

The final cell must itself import the minimal helpers it needs.

It must itself resolve project-relative configs.

It must itself load input data needed for the inference demonstration.

It must itself load saved model/preprocessing artifacts.

It must not depend on variables from earlier cells.

Stronger validation:
extract this final code cell into a one-cell notebook and run it in a fresh
kernel.

Require PASS.

==================================================
DT-406 — DEMONSTRATE TASK 1 INFERENCE
==================================================

Use the canonical saved-model Task1 inference path.

The final cell should:

1. load a small Task1 test/demo slice using the canonical input loader;
2. build the prediction-time feature matrix through the frozen pipeline;
3. reload saved service and lateness artifacts;
4. produce:
   pred_service_min
   pred_late_prob
5. compare the demo predictions against the corresponding frozen final
   submission rows or canonical inference output within approved tolerance;
6. print the inputs and predictions clearly.

Do not write submission_task1.csv.

==================================================
TASK1 DEMO ROWS
==================================================

Use a deterministic small selection:

first N rows in official template/input order

where:
N <= 3 by default.

Do not cherry-pick for impressive predictions.

Do not use labels/actual outcomes.

==================================================
DT-407 — DEMONSTRATE TASK 2A INFERENCE
==================================================

Use the canonical saved-artifact Task2A inference path.

The final cell should:

1. load the final Task2A saved model/runtime artifacts;
2. build the required historical/future feature context using canonical code;
3. run future-grid inference in memory;
4. select a deterministic small set of rows for display;
5. produce:
   pred_total_volume_m3
   pred_chilled_volume_m3
6. compare demo values against frozen final submission rows within approved
   tolerance;
7. print inputs and predictions clearly.

Do not write submission_task2a.csv.

==================================================
TASK2A DEMO ROWS
==================================================

Prefer up to 3 rows with deterministic template order.

Display identifying/input fields needed to understand the forecast, such as:

row_id
depot
brand
iso_year
iso_week
forecast_horizon if present

and the two predictions.

Do not display full historical training rows.

==================================================
DT-408 — CLEARLY PRINT INPUTS AND PREDICTIONS
==================================================

The final cell output must visibly separate:

TASK 1 — INPUTS
TASK 1 — PREDICTIONS
TASK 2A — INPUTS
TASK 2A — PREDICTIONS

Use compact DataFrames or clear printed tables.

Do not show raw internal feature matrices with hundreds of columns.

The goal is judge readability.

==================================================
FINAL CELL PARITY OUTPUT
==================================================

Also print safe status:

TASK 1 SAVED-MODEL PARITY: PASS
TASK 2A SAVED-MODEL PARITY: PASS

If mismatch:
raise and stop.

Do not print private mismatch IDs in a public/sanitized log.

The executed competition notebook may show the selected demo IDs/inputs because
it is an authorized submission artifact, but external-agent logs should not.

==================================================
DT-409 — RESTART KERNEL AND RUN ALL
==================================================

This is a HUMAN-LOCAL real-data gate.

Use a fresh kernel/process.

Execute the notebook from cell 1 to final cell in order.

Do not manually pre-run setup cells.

Do not rely on an interactive session.

Capture a PRIVATE executed notebook and execution summary.

==================================================
NOTEBOOK EXECUTION SCRIPT
==================================================

Implement:

scripts/execute_final_notebook.py

Recommended behavior:

- use nbclient/nbformat or repository-approved Jupyter execution;
- set working directory to project root;
- start a fresh kernel;
- enforce timeout;
- fail on first execution error;
- save executed copy under reports/private/phase31_final_notebook/;
- optionally support --final-cell-only;
- do not overwrite source notebook unless explicitly requested;
- do not write official submissions.

==================================================
DT-410 — REMOVE BROKEN / TEMPORARY CELLS
==================================================

Final notebook must contain no:

scratch experiments
failed code
commented-out tuning loops
duplicate implementations
temporary path fixes
manual `pip install`
debug-only prints
"TODO"
"TBD"
empty code cells with abandoned code
cells producing tracebacks
cells that mutate final official outputs

Keep useful explanatory markdown.

==================================================
OUTPUT CLEANLINESS
==================================================

Tracked source notebook should normally have outputs cleared to avoid public
private-data leakage.

The private local executed copy is the execution evidence.

For final competition packaging, the validated executed copy may be used as
the submitted TeamName_FinalNotebook.ipynb because the organizer is an
authorized recipient.

Do not publish the executed private-output notebook publicly.

==================================================
DT-411 — NO HIDDEN STATE
==================================================

Require BOTH:

A. CLEAN-KERNEL RUN-ALL PASS

and

B. FINAL-CELL-ONLY FRESH-KERNEL PASS

after Phase32 saved artifacts are final.

The final cell must not depend on:

variables from training cells
in-memory fitted models
manually imported interactive objects
previous execution order
notebook widget state
hidden files outside documented project paths

==================================================
HIDDEN-STATE STATIC CHECKS
==================================================

Validator should flag likely hidden-state risks:

final cell references variable names assigned only in earlier notebook cells
without recreating/loading them

final cell uses notebook magic state

final cell assumes current working directory from prior `os.chdir`

final cell uses global model object

final cell calls undefined helper created in a prior notebook cell instead of
importing canonical src helper

Do not rely solely on static analysis.
Fresh-kernel final-cell execution is authoritative.

==================================================
NOTEBOOK VALIDATOR
==================================================

Create:

scripts/validate_final_notebook.py

It must validate at minimum:

filename/pattern
nbformat
kernel metadata
cell tags/order
all DT-389–DT-411 mappings
final code cell is last cell
final cell tags DT-404–DT-408
required official formulas/text present
Task2A history rules present
Task2B summary present
no placeholder/TODO/temp cells
no `pip install`
no external data download/network API
no absolute local paths
no secrets
no execution errors in executed copy
no huge output dump
saved-model reload semantics present
Phase32 dependency state truthful
no official output write in final inference cell

==================================================
NOTEBOOK TASK MAPPING
==================================================

Create either:

- cell metadata tags; and/or
- a safe notebook manifest section in config.

Validator must prove every task DT-389–DT-411 maps to at least one cell or
execution evidence.

DT-409 and DT-411 map to execution evidence, not just notebook text.

==================================================
NOTEBOOK STRUCTURE TESTS
==================================================

Create:

tests/test_final_notebook_structure.py

Test:

file exists
nbformat v4
nonzero cells
expected section headings
cell tags valid
all tasks mapped
final cell is code
final code cell is last
no cells after final cell
kernel metadata present
no empty/broken temporary cells

==================================================
NOTEBOOK CONTRACT TESTS
==================================================

Create:

tests/test_final_notebook_contract.py

Test semantic presence:

Task1 service label formula
strict late > boundary
early wait not service
Task1 leakage statement
Task2A both history sources
unique order once
deferred/not_run included
requested order week / ISO week
10-week backtesting
Style/Tech chilled zero
Task2B no-trained-model summary
Task2B trip formula/no return
Task2B official hard rules
WayLoom policy separate
organizer checker feasibility-only

No stale model names.

==================================================
FINAL INFERENCE TESTS
==================================================

Create:

tests/test_final_notebook_final_inference.py

Static/synthetic-safe tests:

final cell imports canonical loaders
final cell does not invoke training/tuning
final cell loads saved artifacts
final cell performs Task1 inference
final cell performs Task2A inference
final cell prints inputs
final cell prints predictions
final cell does not write official submissions
final cell demo row limit <= configured maximum

After Phase32, local execution evidence closes runtime checks.

==================================================
PRIVACY TESTS
==================================================

Create:

tests/test_final_notebook_privacy.py

Scan source notebook for:

absolute C:\\Users\\ paths
specific /home/<user>/ paths
secrets/API keys
raw private row dumps embedded in markdown/source
hardcoded real delivery/order/vehicle IDs
network upload calls
external proprietary inference API calls
large saved private outputs in tracked source notebook

Do not open private raw data.

==================================================
NO-HIDDEN-STATE TESTS
==================================================

Create:

tests/test_final_notebook_no_hidden_state.py

Static checks:

final cell self-imports helper functions
final cell resolves configs/paths itself
final cell loads saved artifacts explicitly
final cell does not reference obvious earlier model variables
final cell has no `%run` dependency on scratch notebooks
final cell has no hidden IPython history dependency

Runtime local gate:

--final-cell-only fresh kernel PASS

==================================================
OFFICIAL RESTRICTIONS IN NOTEBOOK
==================================================

Notebook must not:

call proprietary modelling/preprocessing APIs
upload competition data externally
use prohibited low/no-code end-to-end modelling tools
fetch external datasets
install unapproved pretrained models

Use only locally available project dependencies/artifacts.

==================================================
NO PACKAGE INSTALL CELLS
==================================================

Do not include:

!pip install ...
%pip install ...
!conda install ...

Environment belongs in requirements / reproducibility documentation.

Notebook should fail clearly if required dependency is missing.

==================================================
NO NETWORK CELLS
==================================================

Reject final notebook code importing/using network clients for data/model
retrieval where not required by the competition implementation.

Examples to reject in final notebook unless explicitly justified:

requests.get
urllib download
wget
curl
external SDK prediction calls

==================================================
TRAINING / EVALUATION RUNTIME
==================================================

The clean run may be computationally heavier than a normal demo.

That is acceptable because the official notebook must retain training and
evaluation work.

However:

- no hyperparameter search;
- no experiment sweep;
- no repeated full training beyond the frozen final validation replay;
- use canonical cached safe intermediate preparation only if its regeneration
  semantics are fully documented and clean-environment reproduction still
  works later.

==================================================
NOTEBOOK EXECUTION TIME
==================================================

Record total runtime in private execution summary.

If >2 hours:
non-blocking engineering review should consider whether redundant work can be
removed without violating the official requirement.

Do not skip required training/evaluation just to make it fast.

==================================================
MODEL ARTIFACT PARITY
==================================================

After Phase32:

The final cell's loaded-model predictions must match canonical frozen
inference behavior.

For Task1 demo rows:
compare:

pred_service_min
pred_late_prob

For Task2A demo rows:
compare:

pred_total_volume_m3
pred_chilled_volume_m3

Use canonical configured numeric tolerance.

No approximate visual-only check.

==================================================
OFFICIAL OUTPUT IMMUTABILITY
==================================================

Hash before/after local notebook run:

outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv

docs/task2b_policy.md

Require unchanged.

Notebook may read final submission files for parity checks.

It must not rewrite them.

==================================================
MODEL ARTIFACT IMMUTABILITY
==================================================

Hash canonical saved model/preprocessing artifacts before/after notebook run.

Require unchanged.

Notebook training replay must use temporary/private runtime objects.

==================================================
EXECUTION MANIFEST
==================================================

Private:

reports/private/phase31_final_notebook/run_manifest.json

Recommended fields:

phase = 31
source_notebook_sha256
executed_notebook_sha256
kernel
python_version
package_versions
execution_start/end/runtime
cell_count
code_cell_count
error_output_count
final_cell_is_last
run_all_status
final_cell_only_status
phase32_artifact_status
Task1 parity status
Task2A parity status
frozen output hash status
model artifact hash status
git_commit

No private row values.

==================================================
EXECUTED NOTEBOOK VALIDATION
==================================================

Validate:

all code cells have execution counts in full-run copy
execution counts increase consistently / reflect fresh ordered execution
no Error outputs
no stale traceback text
final cell has visible Task1 input/prediction output
final cell has visible Task2A input/prediction output
final parity statuses PASS
output volume reasonable

Do not rely only on execution_count; verify outputs/statuses too.

==================================================
EDGE CASE — PHASE32 NOT YET COMPLETE
==================================================

Expected during initial Phase31 implementation.

Do not fake DT-405.

Return:

PHASE 31 CORE IMPLEMENTATION: PASS
DT-405: BLOCKED_BY_PHASE32
FINAL CLEAN-RUN CLOSURE: PENDING
AUTHORIZED NEXT ACTION: PHASE32

Do not start Phase33.

==================================================
EDGE CASE — TASK2A FINAL ARTIFACT FORMAT UNRESOLVED
==================================================

Do not hardcode a model path/type.

Use the canonical Phase32 artifact loader once available.

If Phase17 final inference can run but Phase32 has not serialized the required
artifacts:
DT-405 remains blocked.

==================================================
EDGE CASE — FINAL CELL ALONE FAILS BUT RUN-ALL PASSES
==================================================

This is a hidden-state blocker.

DT-411 FAIL.

Fix the final cell so it imports/loads/resolves everything itself.

Do not accept run-all alone.

==================================================
EDGE CASE — RUN-ALL FAILS BUT FINAL CELL ALONE PASSES
==================================================

DT-409 FAIL.

The official notebook must run top-to-bottom.

Fix the earlier cell failure.

==================================================
EDGE CASE — NOTEBOOK TRAINING CHANGES FROZEN MODELS
==================================================

Immediate blocker.

Move notebook training outputs to private temporary runtime paths.

Restore frozen artifacts from verified source and rerun affected integrity
checks.

Do not manually overwrite frozen model files.

==================================================
EDGE CASE — FINAL INFERENCE CHANGES OFFICIAL CSV
==================================================

Immediate blocker.

Final demonstration must be in-memory/read-only.

Do not call export functions with canonical output paths.

==================================================
EDGE CASE — FULL PRIVATE INPUT PRINT
==================================================

Reduce to 1–3 deterministic demo rows and selected readable columns.

The final notebook is authorized for organizer submission, but excessive data
exposure is unnecessary and creates public-repo risk.

==================================================
EDGE CASE — SOURCE NOTEBOOK CONTAINS PRIVATE OUTPUTS
==================================================

If repository may be public:
clear outputs before commit.

Keep executed notebook in ignored private report directory.

Final packaging may copy the validated executed notebook privately.

==================================================
EDGE CASE — TEAM NAME UNKNOWN
==================================================

Do not invent a team name.

Keep the master filename pattern until the canonical team-name setting is
available.

Phase40 packaging must resolve the final required filename.

==================================================
EDGE CASE — EDA TOO LARGE
==================================================

Reduce to a compact summary.

Do not delete the EDA task entirely.

Use aggregate tables/plots only.

==================================================
EDGE CASE — MODEL METRICS DIFFER FROM FROZEN EVIDENCE
==================================================

STOP.

Do not update the notebook with the new metric silently.

Investigate whether:

- split differs;
- config differs;
- preprocessing differs;
- nondeterminism exists;
- stale frozen evidence exists.

==================================================
EDGE CASE — TASK2A BACKTEST DIFFERS
==================================================

STOP.

Do not silently change the documented final strategy.

==================================================
EDGE CASE — TASK2B SUMMARY DISAGREES WITH PHASE24
==================================================

STOP.

Use the final frozen policy/output semantics.

==================================================
GIT WORKFLOW
==================================================

Recommended branch:

git checkout main
git pull
git checkout -b feature/phase-31-final-notebook

Recommended commits:

feat(notebook): add final competition notebook structure
feat(notebook): add Task1 labels preprocessing training evaluation
feat(notebook): add Task2A aggregation backtesting evaluation
feat(notebook): add Task2B summary and saved-model inference cell
test(notebook): validate structure privacy and hidden-state contract

Before commit:

git status
git diff
git diff --check

Run safe tests.

Commit the source notebook with cleared private outputs if repository may be
public.

Never stage:

data/raw/**
data/interim/**
data/processed/**
reports/private/**

Do not stage private executed notebook evidence.

==================================================
SAFE TEST LOOP
==================================================

Run:

pytest -q \
  tests/test_final_notebook_structure.py \
  tests/test_final_notebook_contract.py \
  tests/test_final_notebook_final_inference.py \
  tests/test_final_notebook_privacy.py \
  tests/test_final_notebook_no_hidden_state.py

Then relevant Task1/Task2A/Task2B frozen-pipeline tests.

Then:

pytest -q
python -m pip check
git diff --check
git status

Do not execute the private real-data notebook in external-agent context.

==================================================
HUMAN-LOCAL FULL NOTEBOOK COMMAND
==================================================

Expected shape:

python scripts/execute_final_notebook.py \
  --input TeamName_FinalNotebook.ipynb \
  --output reports/private/phase31_final_notebook/TeamName_FinalNotebook.executed.ipynb \
  --config configs/final_notebook.yaml \
  --mode run-all

Use actual implemented CLI.

Run only after private competition data is available locally.

==================================================
HUMAN-LOCAL FINAL-CELL-ONLY COMMAND
==================================================

After Phase32 PASS:

python scripts/execute_final_notebook.py \
  --input TeamName_FinalNotebook.ipynb \
  --output reports/private/phase31_final_notebook/final_cell_only.executed.ipynb \
  --config configs/final_notebook.yaml \
  --mode final-cell-only

This must start a fresh kernel.

==================================================
HUMAN-LOCAL VALIDATION COMMAND
==================================================

Expected:

python scripts/validate_final_notebook.py \
  --source TeamName_FinalNotebook.ipynb \
  --executed reports/private/phase31_final_notebook/TeamName_FinalNotebook.executed.ipynb \
  --final-cell-executed reports/private/phase31_final_notebook/final_cell_only.executed.ipynb \
  --config configs/final_notebook.yaml

==================================================
SANITIZED EXPECTED HUMAN RESULT
==================================================

WAYLOOM — PHASE 31 FINAL NOTEBOOK

SOURCE NOTEBOOK STRUCTURE                 : PASS
TASK MAPPING DT-389–DT-411               : PASS

TASK1 LABEL / PREPROCESSING CELLS         : PASS
TASK1 TRAINING / EVALUATION CELLS         : PASS
TASK2A AGGREGATION CELLS                  : PASS
TASK2A BACKTEST / EVALUATION CELLS        : PASS
TASK2B SUMMARY                            : PASS

PHASE32 SAVED ARTIFACT GATE               : PASS
FINAL CELL LOADS SAVED MODELS             : PASS
TASK1 INFERENCE DEMO                      : PASS
TASK2A INFERENCE DEMO                     : PASS
INPUTS PRINTED                            : PASS
PREDICTIONS PRINTED                       : PASS

CLEAN-KERNEL RUN-ALL                      : PASS
FINAL-CELL-ONLY FRESH KERNEL              : PASS
HIDDEN STATE DEPENDENCY                   : NONE

EXECUTION ERRORS                          : 0
BROKEN/TEMP CELLS                         : 0

TASK1 SAVED-MODEL PARITY                  : PASS
TASK2A SAVED-MODEL PARITY                 : PASS

OFFICIAL OUTPUTS CHANGED                  : NO
SAVED MODEL ARTIFACTS CHANGED             : NO

PHASE 31                                  : PASS
READY FOR INDEPENDENT REVIEW              : YES

Do not include private row values in the sanitized report.

==================================================
STOP CONDITIONS
==================================================

STOP if:

any DT-389–DT-411 task is missing

final notebook filename/pattern wrong

final code cell is not last

cell exists after final inference cell

final cell does not reload saved models

DT-405 claimed PASS before Phase32 DT-412–DT-419 PASS

final cell relies on earlier model/preprocessor objects

final-cell-only fresh-kernel execution fails

clean-kernel run-all fails

execution error output exists

Task1 label formula wrong

Task1 late boundary uses >=

Task1 current actual fields appear as direct predictors

Task2A history misses either required source

Task2A deferred/not_run demand omitted

Task2A validation becomes random/non-time-aware

Task2B is retrained/rerun unnecessarily

Task2B checker described as optimality proof

new model search/tuning introduced

notebook overwrites frozen model artifacts

notebook overwrites official submissions

final demo predictions fail parity

private dataset rows dumped excessively

source notebook includes secrets/private absolute paths

proprietary modelling API/network data upload appears

`pip install`/environment mutation cell appears

broken/TODO/scratch cells remain

frozen artifacts change

tests fail

pip check fails

Phase33 work introduced

==================================================
DEFINITION OF DONE — CORE GATE
==================================================

Before Phase32, require:

DT-389 READY
DT-390 READY
DT-391 READY
DT-392 READY
DT-393 READY
DT-394 READY
DT-395 READY
DT-396 READY
DT-397 READY
DT-398 READY
DT-399 READY
DT-400 READY
DT-401 READY
DT-402 READY
DT-403 READY
DT-404 READY
DT-406 READY
DT-407 READY
DT-408 READY
DT-410 READY

DT-405:
BLOCKED_BY_PHASE32 unless saved artifact management already passed.

DT-409/DT-411:
may receive PRELIMINARY PASS against currently available artifacts, but FINAL
PASS requires post-Phase32 execution.

Then:

PHASE31 CORE NOTEBOOK: READY
AUTHORIZED NEXT ACTION: PHASE32 ARTIFACT MANAGEMENT
PHASE31 FINAL PASS: NO

==================================================
DEFINITION OF DONE — FINAL CLOSURE
==================================================

After Phase32 PASS, require ALL:

DT-389 PASS
DT-390 PASS
DT-391 PASS
DT-392 PASS
DT-393 PASS
DT-394 PASS
DT-395 PASS
DT-396 PASS
DT-397 PASS
DT-398 PASS
DT-399 PASS
DT-400 PASS
DT-401 PASS
DT-402 PASS
DT-403 PASS
DT-404 PASS
DT-405 PASS
DT-406 PASS
DT-407 PASS
DT-408 PASS
DT-409 PASS
DT-410 PASS
DT-411 PASS

Plus:

source notebook valid

all reusable logic sourced from canonical src/ modules

final code cell is last

saved models loaded from disk

saved preprocessing objects loaded if required

Task1 inference demonstrated

Task2A inference demonstrated

inputs clearly printed

predictions clearly printed

saved-model parity PASS

clean-kernel run-all PASS

fresh-kernel final-cell-only PASS

no hidden state

no execution errors

no temporary/broken cells

no environment-install cells

no network/proprietary API use

no frozen artifact changes

private execution evidence stored only in private report path

fresh independent Phase31 review PASS

Then:

PHASE 31 STATUS: PASS
FINAL NOTEBOOK: COMPETITION-READY
HIDDEN STATE: NONE
FROZEN ARTIFACTS: UNCHANGED
READY FOR PHASE 33 AFTER PHASE32: YES

==================================================
FINAL SELF-REVIEW
==================================================

Verify exact task count:
23

Verify:

DT-389 READY/PASS
DT-390 READY/PASS
DT-391 READY/PASS
DT-392 READY/PASS
DT-393 READY/PASS
DT-394 READY/PASS
DT-395 READY/PASS
DT-396 READY/PASS
DT-397 READY/PASS
DT-398 READY/PASS
DT-399 READY/PASS
DT-400 READY/PASS
DT-401 READY/PASS
DT-402 READY/PASS
DT-403 READY/PASS
DT-404 READY/PASS
DT-405 BLOCKED/PASS according to Phase32
DT-406 READY/PASS
DT-407 READY/PASS
DT-408 READY/PASS
DT-409 PRELIMINARY/FINAL PASS
DT-410 READY/PASS
DT-411 PRELIMINARY/FINAL PASS

No tasks skipped.
No Phase33 work.

==================================================
RETURN ONLY — INITIAL IMPLEMENTATION STAGE
==================================================

PHASE:
31 — CORE IMPLEMENTATION STAGE

TASK STATUS:

DT-389 READY / FAIL
DT-390 READY / FAIL
DT-391 READY / FAIL
DT-392 READY / FAIL
DT-393 READY / FAIL
DT-394 READY / FAIL
DT-395 READY / FAIL
DT-396 READY / FAIL
DT-397 READY / FAIL
DT-398 READY / FAIL
DT-399 READY / FAIL
DT-400 READY / FAIL
DT-401 READY / FAIL
DT-402 READY / FAIL
DT-403 READY / FAIL
DT-404 READY / FAIL
DT-405 BLOCKED_BY_PHASE32 / PASS / FAIL
DT-406 READY / FAIL
DT-407 READY / FAIL
DT-408 READY / FAIL
DT-409 PRELIMINARY_PASS / PENDING / FAIL
DT-410 READY / FAIL
DT-411 PRELIMINARY_PASS / PENDING / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

NOTEBOOK STRUCTURE:
PASS / FAIL

TASK1 LABEL/PREPROCESSING:
PASS / FAIL

TASK1 TRAINING/EVALUATION:
PASS / FAIL

TASK2A AGGREGATION/BACKTESTING:
PASS / FAIL

TASK2A EVALUATION:
PASS / FAIL

TASK2B SUMMARY:
PASS / FAIL

FINAL INFERENCE CELL:
READY / BLOCKED / FAIL

FINAL CELL IS LAST CELL:
PASS / FAIL

PHASE32 SAVED ARTIFACT GATE:
PASS / AWAITING_PHASE32 / FAIL

SAFE TESTS:
...

FULL SAFE SUITE:
...

PIP CHECK:
PASS / FAIL

GIT DIFF CHECK:
PASS / FAIL

PRIVATE REAL DATA ACCESSED:
NO

FROZEN ARTIFACTS CHANGED:
NO

PHASE33 WORK:
NONE

HUMAN LOCAL ACTION REQUIRED:
YES

Print exact:

1. run-all command
2. final-cell-only command
3. validation command

If Phase32 is pending:

PHASE 31 CORE STATUS:
READY FOR PHASE32 ARTIFACT HANDOFF

PHASE 31 FINAL STATUS:
PENDING PHASE32 + LOCAL CLEAN EXECUTION

READY FOR PHASE33:
NO

Then STOP.

```

---

# 128. Independent Phase 31 review prompt

```text
Perform an INDEPENDENT FRESH-SESSION REVIEW of WayLoom Datathon PHASE 31.

PHASE:
Final Competition Notebook

TASK RANGE:
DT-389 through DT-411

REVIEW MODE:
READ-ONLY
FRESH SESSION
SOURCE-GROUNDED
NO PRIVATE ROW INSPECTION

Do NOT implement Phase32/33.
Do NOT modify frozen models or submissions.
Do NOT execute private real-data notebook inside the external-agent context.

==================================================
SOURCE AUTHORITY
==================================================

Read:

1. Official Challenge Booklet Deliverables page
2. WAYLOOM_DATATHON_MASTER_PLAN.md
   - execution rules
   - Phase31
   - Phase32 dependency DT-412–DT-419
   - final checklist
3. PHASE_31_COMPETITION_CONTRACT.md
4. PHASE_10_COMPETITION_CONTRACT.md
5. PHASE_17_COMPETITION_CONTRACT.md
6. PHASE_24_COMPETITION_CONTRACT.md
7. PHASE_29_COMPETITION_CONTRACT.md
8. PHASE_30_COMPETITION_CONTRACT.md if final

Inspect:

TeamName_FinalNotebook.ipynb
configs/final_notebook.yaml
scripts/validate_final_notebook.py
scripts/execute_final_notebook.py
scripts/build_final_notebook.py if present

tests/test_final_notebook_structure.py
tests/test_final_notebook_contract.py
tests/test_final_notebook_final_inference.py
tests/test_final_notebook_privacy.py
tests/test_final_notebook_no_hidden_state.py

Inspect canonical safe model/config/inference interfaces.

Do not inspect private rows.

==================================================
OFFICIAL NOTEBOOK REQUIREMENT
==================================================

Verify the notebook truly retains cells for:

label construction
preprocessing
training
evaluation

Verify the ACTUAL LAST CODE CELL:

loads saved models
runs Task1 inference
runs Task2A inference
clearly prints inputs
clearly prints predictions

This is the central official gate.

==================================================
PHASE32 DEPENDENCY
==================================================

DT-405 depends on DT-412–DT-419.

If Phase32 has not passed:

DT-405 cannot PASS.

The independent review may return:

PHASE31 CORE REVIEW: PASS
FINAL PHASE31 REVIEW: BLOCKED_BY_PHASE32
AUTHORIZED NEXT ACTION: PHASE32

Do not call final Phase31 PASS.

If Phase32 has passed, require sanitized local evidence for save/load parity.

==================================================
HUMAN SANITIZED EVIDENCE
==================================================

Use human-local results such as:

PHASE32 ARTIFACT MANAGEMENT: PASS/NOT YET

SOURCE NOTEBOOK VALIDATION: PASS/FAIL

CLEAN-KERNEL RUN-ALL: PASS/FAIL

FINAL-CELL-ONLY FRESH KERNEL: PASS/FAIL

EXECUTION ERRORS: <count>

FINAL CELL IS LAST: PASS/FAIL

TASK1 SAVED MODEL LOAD: PASS/FAIL
TASK1 INFERENCE DEMO: PASS/FAIL
TASK1 SAVED-MODEL PARITY: PASS/FAIL

TASK2A SAVED ARTIFACT LOAD: PASS/FAIL
TASK2A INFERENCE DEMO: PASS/FAIL
TASK2A SAVED-MODEL PARITY: PASS/FAIL

INPUTS PRINTED: PASS/FAIL
PREDICTIONS PRINTED: PASS/FAIL

BROKEN/TEMP CELLS: <count>

OFFICIAL OUTPUT HASHES: UNCHANGED/FAIL
MODEL ARTIFACT HASHES: UNCHANGED/FAIL

Do not ask for private IDs/prediction values.

==================================================
AUDIT DT-389
==================================================

Notebook exists and is valid nbformat.

Correct naming pattern.

No absolute paths/secrets.

No environment mutation cells.

==================================================
AUDIT DT-390
==================================================

Project/problem overview correctly distinguishes:

Task1 regression + lateness probability
Task2A 10-week demand forecast
Task2B constraint optimization

Official outputs accurate.

==================================================
AUDIT DT-391
==================================================

Imports/configuration are canonical.

Final configs loaded.

Reproducibility controls present.

No stale experiment configs.

No user-specific chdir.

==================================================
AUDIT DT-392
==================================================

Canonical loaders used.

No internet download.

No full private row dump.

Task1/Task2A inputs correspond to final pipeline.

==================================================
AUDIT DT-393
==================================================

Canonical validators called.

Fail-closed behavior.

Compact status display.

No notebook-only validator fork.

==================================================
AUDIT DT-394
==================================================

Require exact Task1 labels:

service_start = max(arrival, open)
service_minutes = leave - service_start
late = arrival > close

Early wait not service.
Arrival exactly at close not late.

Executable cell calls canonical label logic.

==================================================
AUDIT DT-395
==================================================

Preprocessing cells reflect final pipeline.

No second implementation.

No overwrite of canonical frozen preprocessing/model artifacts.

==================================================
AUDIT DT-396
==================================================

EDA summary exists, compact and relevant.

No identifier-level row dump.

No giant scratchpad plot sequence.

==================================================
AUDIT DT-397
==================================================

Final feature engineering only.

Task1 leakage guard present.

Task2A chronology guard present.

No disabled candidate features described/executed as final.

==================================================
AUDIT DT-398
==================================================

Task1 training cells use frozen final configurations.

No hyperparameter search.

No test tuning.

Training replay does not overwrite canonical saved models.

==================================================
AUDIT DT-399
==================================================

Task1 evaluation uses frozen validation contract and real final metrics.

No Task1 test labels.

Calibration evaluation accurate if applicable.

==================================================
AUDIT DT-400
==================================================

Task2A demand history uses:

deliveries_train + task1_test_inputs

Each unique order once.
Deferred/not_run included.
Requested order week.
ISO calendar.

==================================================
AUDIT DT-401
==================================================

Task2A backtesting is time-aware / rolling.

10-week horizon.

Frozen final strategy.

No new model search.

No future leakage.

==================================================
AUDIT DT-402
==================================================

Task2A evaluation reports canonical backtest metrics.

No future test target.

Output semantics checked:
nonnegative
chilled<=total
Style/Tech chilled zero

==================================================
AUDIT DT-403
==================================================

Task2B section is summary/pointer only.

No trained-model claim.

No unnecessary optimizer rerun.

Correct trip formula/no return.

Seven hard rules.

WayLoom policy separate.

Organizer checker feasibility-only.

No private assignment dump.

==================================================
AUDIT DT-404
==================================================

Final inference section is clear and immediately precedes the final code cell.

No cells after final code cell.

==================================================
AUDIT DT-405
==================================================

After Phase32 only:

Final cell explicitly reloads saved model/preprocessing artifacts.

No reliance on earlier model objects.

Artifact loader path is canonical.

Save/load parity evidence PASS.

If Phase32 pending:
FAIL/BLOCKED, not PASS.

==================================================
AUDIT DT-406
==================================================

Task1 saved-model inference demonstrated.

Uses prediction-time data only.

No label/actual fields.

Prediction parity with frozen canonical output PASS.

No official CSV rewrite.

==================================================
AUDIT DT-407
==================================================

Task2A saved-artifact inference demonstrated.

Uses canonical future forecast context.

Prediction parity PASS.

No official CSV rewrite.

==================================================
AUDIT DT-408
==================================================

Visible final-cell output clearly contains four blocks:

Task1 inputs
Task1 predictions
Task2A inputs
Task2A predictions

Compact / readable.

No huge raw feature matrix.

==================================================
AUDIT DT-409
==================================================

Require human-local clean-kernel run-all PASS.

Every code cell executes in order.

No error outputs.

Do not accept "works interactively".

==================================================
AUDIT DT-410
==================================================

No scratch/broken/TODO/TBD/debug/install cells.

No traceback outputs.

No abandoned experiment blocks.

==================================================
AUDIT DT-411
==================================================

Require BOTH:

clean-kernel run-all PASS

and

final-cell-only fresh-kernel PASS

after Phase32.

This proves no hidden state.

==================================================
FINAL CELL STATIC AUDIT
==================================================

The last code cell should itself:

import canonical helpers
resolve project/config paths
load Task1 input/demo context
load Task1 saved artifacts
run Task1 inference
load Task2A context
load Task2A saved artifacts
run Task2A inference
print inputs
print predictions
verify parity

It should not reference variables defined only in earlier cells.

==================================================
PRIVACY AUDIT
==================================================

Tracked source notebook should not embed private executed row outputs if the
repo may be public.

Allow final submitted/private executed notebook to contain the minimal 1–3
required input/prediction demonstration rows.

Reject:

full test table output
private raw dump
absolute local path
secret/API key
network upload
proprietary prediction API

==================================================
FROZEN ARTIFACT AUDIT
==================================================

Use sanitized evidence.

Require before/after unchanged:

submission_task1.csv
submission_task2a.csv
submission_task2b.csv
task2b_policy.md
canonical final models/preprocessors

Notebook must be evidence, not a mutation step.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_final_notebook_structure.py \
  tests/test_final_notebook_contract.py \
  tests/test_final_notebook_final_inference.py \
  tests/test_final_notebook_privacy.py \
  tests/test_final_notebook_no_hidden_state.py

Then relevant final Task1/Task2A/Task2B tests.

Then:

pytest -q
python -m pip check
git diff --check
git status

Do not execute private real-data notebook here.

==================================================
RETURN FORMAT
==================================================

Provide:

| Task | Requirement | PASS/FAIL/BLOCKED | Evidence | Blocking fix |

Then:

OFFICIAL FINAL NOTEBOOK DELIVERABLE:
PASS / FAIL / BLOCKED_BY_PHASE32

NOTEBOOK STRUCTURE:
PASS / FAIL

PROJECT OVERVIEW:
PASS / FAIL

IMPORTS / CONFIG:
PASS / FAIL

DATA LOADING:
PASS / FAIL

DATA VALIDATION:
PASS / FAIL

TASK1 LABEL CONSTRUCTION:
PASS / FAIL

PREPROCESSING:
PASS / FAIL

EDA SUMMARY:
PASS / FAIL

FEATURE ENGINEERING:
PASS / FAIL

TASK1 TRAINING:
PASS / FAIL

TASK1 EVALUATION:
PASS / FAIL

TASK2A AGGREGATION:
PASS / FAIL

TASK2A TRAINING / BACKTESTING:
PASS / FAIL

TASK2A EVALUATION:
PASS / FAIL

TASK2B SUMMARY:
PASS / FAIL

FINAL INFERENCE SECTION:
PASS / FAIL

PHASE32 ARTIFACT GATE:
PASS / BLOCKED / FAIL

FINAL CELL LOADS SAVED MODELS:
PASS / BLOCKED / FAIL

TASK1 INFERENCE DEMO:
PASS / BLOCKED / FAIL

TASK2A INFERENCE DEMO:
PASS / BLOCKED / FAIL

INPUTS / PREDICTIONS CLEAR:
PASS / FAIL

CLEAN-KERNEL RUN-ALL:
PASS / PENDING / FAIL

FINAL-CELL-ONLY FRESH KERNEL:
PASS / PENDING / FAIL

HIDDEN STATE:
NONE / PRESENT / PENDING

BROKEN / TEMP CELLS:
0 / <count>

EXECUTION ERRORS:
0 / <count> / PENDING

PRIVACY:
PASS / FAIL

FROZEN ARTIFACTS:
UNCHANGED / CHANGED / PENDING

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

DT-389: PASS/FAIL
DT-390: PASS/FAIL
DT-391: PASS/FAIL
DT-392: PASS/FAIL
DT-393: PASS/FAIL
DT-394: PASS/FAIL
DT-395: PASS/FAIL
DT-396: PASS/FAIL
DT-397: PASS/FAIL
DT-398: PASS/FAIL
DT-399: PASS/FAIL
DT-400: PASS/FAIL
DT-401: PASS/FAIL
DT-402: PASS/FAIL
DT-403: PASS/FAIL
DT-404: PASS/FAIL
DT-405: PASS/BLOCKED/FAIL
DT-406: PASS/BLOCKED/FAIL
DT-407: PASS/BLOCKED/FAIL
DT-408: PASS/FAIL
DT-409: PASS/PENDING/FAIL
DT-410: PASS/FAIL
DT-411: PASS/PENDING/FAIL

If Phase32 is pending but all core work passes:

PHASE 31 CORE REVIEW: PASS
PHASE 31 FINAL REVIEW: BLOCKED_BY_PHASE32
AUTHORIZED NEXT ACTION: PHASE32
READY FOR PHASE33: NO

If Phase32 + local execution all pass:

PHASE 31 INDEPENDENT REVIEW: PASS
FINAL NOTEBOOK: COMPETITION-READY
HIDDEN STATE: NONE
FROZEN ARTIFACTS: UNCHANGED
BLOCKERS: None
READY FOR PHASE33: YES

Then STOP.

```

---

# 129. Completion record

# Phase 31 completion report

- Phase name: Final competition notebook.
- Date: 2026-10-08 (documentation reconciliation).
- Operator: Codex for source/documentation checks; clean-kernel and private-data execution evidence was supplied from human-local runs, not executed by this agent.
- Tasks in phase: DT-389 through DT-411 (23 P0 tasks).
- Tasks completed [x]: 23/23 technical tasks, as individually judged PASS in the latest independent review and itemized below.
- Tasks skipped: None.
- Tasks blocked [!]: None. The earlier formal-documentation blocker was resolved and the fresh independent closure review passed.
- Official rules verified: the challenge booklet requires `TeamName_FinalNotebook.ipynb`, substantive label-construction, preprocessing, training, and evaluation cells, and a last cell that loads saved models and prints Task 1 and Task 2A inputs/predictions. The latest source review found these requirements satisfied. No private competition rows were opened for this reconciliation.
- Tests run and results: the latest independent reviewer and this reconciliation each ran 42 targeted synthetic tests (PASS), the full safe suite (765 passed, 1 skipped, 4 nonblocking warnings), `python -m pip check` (PASS), and `git diff --check` (PASS). The separately supplied human-local full suite reported 766 passed and 4 warnings. These are distinct runs; do not conflate their counts.
- Checker/script evidence: this reconciliation reran source notebook validation (23/23 mappings, last-cell placement, zero broken/temporary cells, zero saved private outputs, Phase 32 artifact gate) and verified all 12 registered artifact checksums without private data. Official CSV and registry SHA256 values matched the pre-edit baselines. Human-local clean-kernel Run All passed with zero errors; separate fresh-kernel final-cell-only execution passed under the registered WayLoom Datathon `.venv` kernel. Human-local Task 1 and Task 2A saved-model parity and pre/post official-output/model hash guards passed. Agent-side source validation is not a substitute for those human-local runs.
- Artifacts produced: no new competition output or model artifact. The tracked source is `TeamName_FinalNotebook.ipynb`; private executed evidence is saved only under ignored `reports/private/phase31_final_notebook/` and was not opened here.
- Decision-log entries created: None; no model, feature, policy, or submission decision changed.
- Data-safety check (no restricted data committed/uploaded): PASS based on source/Git review and supplied human-local guards; no commit, upload, private output inspection, retraining, or official-output regeneration occurred during reconciliation.
- Issues found: the earlier independent review returned overall FAIL solely because this completion record and the master-plan Phase 31 statuses were then unfilled. That historical FAIL remains valid for its review point; the subsequent fresh read-only independent closure review returned PASS after those documentation changes.
- Follow-ups: existing uncommitted Phase 31 work and narrow `.gitattributes` remain Git-workflow follow-ups, not notebook defects. This administrative synchronization does not authorize a commit or Phase 33 implementation in this turn.
- READY FOR NEXT PHASE: YES (fresh independent closure review PASS; Phase 31 master-plan flag synchronized).

## Task coverage

- [x] DT-389 PASS - valid, correctly named source notebook; source validator and independent structural review.
- [x] DT-390 PASS - problem/competition overview; notebook cells 0-1.
- [x] DT-391 PASS - imports, frozen configuration, and reproducibility; cell 3.
- [x] DT-392 PASS - authorized manifest-based local data loading; cell 5.
- [x] DT-393 PASS - schema/key validation; cell 7.
- [x] DT-394 PASS - canonical Task 1 label semantics and outcome leakage guard; cell 9 and `src/task1/labels.py`.
- [x] DT-395 PASS - executable canonical preprocessing; cell 11.
- [x] DT-396 PASS - useful EDA summaries/charts; cell 13 and human-local readable output confirmation.
- [x] DT-397 PASS - final feature engineering/order and leakage barriers; cell 15.
- [x] DT-398 PASS - frozen Task 1 training replay in memory, without model overwrite; cell 17.
- [x] DT-399 PASS - Task 1 evaluation from actual labels/predictions; cell 19.
- [x] DT-400 PASS - both-source, unique-order, requested-date ISO-week Task 2A history; cell 21 and `src/task2a/history.py`.
- [x] DT-401 PASS - rolling backtest and frozen 50/50 CatBoost-LightGBM method; cell 23.
- [x] DT-402 PASS - Task 2A evaluation and nonnegative/chilled constraints; cell 25.
- [x] DT-403 PASS - Task 2B optimizer summary/pointer, no rerun; cell 26.
- [x] DT-404 PASS - visible final inference heading; cell 28.
- [x] DT-405 PASS - final cell loads through the secured Phase 32 registry, with verified paths/checksums before deserialization; cell 29 and `src/common/artifact_registry.py`.
- [x] DT-406 PASS - Task 1 saved-model inference and human-local parity; cell 29.
- [x] DT-407 PASS - Task 2A saved-model inference and human-local parity; cell 29.
- [x] DT-408 PASS - bounded, labeled inputs and predictions for both tasks; cell 29.
- [x] DT-409 PASS - supplied human-local clean-kernel Run All, zero errors; not independently rerun with private data by the agent.
- [x] DT-410 PASS - source validator found zero broken/temporary cells and no saved private outputs.
- [x] DT-411 PASS - supplied separate human-local fresh-kernel final-cell-only run; final cell self-bootstraps.

## Notebook

- [x] valid nbformat
- [x] correct naming pattern
- [x] no workstation-specific absolute paths
- [x] no install/network cells
- [x] final code cell is last
- [x] no cells after final inference
- [x] no broken/temp cells

## Task1

- [x] label construction
- [x] preprocessing
- [x] feature engineering
- [x] training
- [x] evaluation
- [x] saved-model inference
- [x] saved-model parity (human-local)

## Task2A

- [x] aggregation/history
- [x] feature construction
- [x] rolling backtesting
- [x] evaluation
- [x] saved-artifact inference
- [x] saved-model parity (human-local)

## Task2B

- [x] summary/pointer
- [x] no optimizer rerun
- [x] checker feasibility-only

## Phase32 artifact gate

- [x] DT-412–DT-419 PASS (supplied Phase 32 independent review)
- [x] all saved objects load (supplied Phase 32 validation and fresh-process evidence)
- [x] loaded predictions reproduce canonical inference (supplied human-local parity)

## Execution

- [x] clean-kernel run-all (human-local)
- [x] final-cell-only fresh kernel (human-local)
- [x] 0 execution errors (human-local)
- [x] hidden state NONE (separate human-local fresh-kernel proof)

## Frozen artifacts

- official outputs changed: NO (human-local pre/post guards; safe hash recheck)
- saved models changed: NO (human-local pre/post guards; registry checksum verification)
- Task2B policy changed: NO (Git/source check)

## Review

- earlier independent review: 23/23 technical tasks PASS; overall formal closure FAIL because the completion record and master-plan statuses were unfilled at that time. Preserve this historical verdict.
- subsequent fresh read-only independent closure review: PASS. It verified 23/23 task statuses, the populated completion report, master-plan task synchronization, notebook integrity, human-local execution evidence provenance, official CSV and Phase 32 artifact integrity, safe tests, and repository privacy. It explicitly authorized formal Phase 31 closure and updating the remaining master-plan completion/readiness flags; it did not itself edit those flags.

## Verdict

PHASE 31 TECHNICAL STATUS: 23/23 PASS
PHASE 31 FORMAL STATUS: PASS - CLOSED
FINAL NOTEBOOK: COMPETITION-READY ON REVIEWED TECHNICAL EVIDENCE
HIDDEN STATE: NONE ON SUPPLIED HUMAN-LOCAL PROOF
READY FOR PHASE33: YES (authorization only; Phase 33 not started here)

---

# 130. Final checklist

Before final Phase31 closure:

- [x] Exact 23 tasks DT-389–DT-411 covered.
- [x] Official final notebook requirement satisfied.
- [x] Cells for label construction retained.
- [x] Cells for preprocessing retained.
- [x] Cells for training retained.
- [x] Cells for evaluation retained.
- [x] Task1 label semantics exact.
- [x] Task1 leakage safeguards exact.
- [x] Task2A history rules exact.
- [x] Task2A rolling validation exact.
- [x] Task2B summary accurate.
- [x] Final cell is the actual final cell.
- [x] Final cell reloads saved models/artifacts.
- [x] Phase32 artifact gate passed.
- [x] Task1 inference demonstrated.
- [x] Task2A inference demonstrated.
- [x] Inputs clearly printed.
- [x] Predictions clearly printed.
- [x] Saved-model parity checks pass.
- [x] Official output files unchanged.
- [x] Canonical saved artifacts unchanged.
- [x] Clean-kernel run-all passes.
- [x] Final-cell-only fresh-kernel execution passes.
- [x] Hidden state is absent.
- [x] No errors/temp/broken cells.
- [x] No install/network/proprietary API cells.
- [x] Source notebook safe for tracked repo.
- [x] Private executed evidence remains private.
- [x] Safe tests pass.
- [x] Full suite passes.
- [x] `pip check` passes.
- [x] Fresh independent review of the reconciled formal closure passes.

Only then:

```text
PHASE 31 STATUS: PASS
FINAL NOTEBOOK: COMPETITION-READY
HIDDEN STATE: NONE
FROZEN DATATHON PIPELINES: UNCHANGED
READY FOR PHASE33: YES
```
