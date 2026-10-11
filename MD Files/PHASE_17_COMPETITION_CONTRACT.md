# PHASE 17 — Task 2A Final Inference & Submission

> **Canonical filename:** `PHASE_17_COMPETITION_CONTRACT.md`  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** **DT-242 → DT-253**  
> **Task count:** 12  
> **Default phase priority:** P0  
> **Phase dependency:** Phase 16 must have passed and `configs/task2a_final_models.yaml` must be frozen  
> **Phase gate:** Exact `submission_task2a.csv` passes row-ID, schema, non-negativity, Style/Tech chilled-zero, finite-value, and chilled≤total checks.

---

# 1. Purpose of Phase 17

Phase 17 converts the frozen Task 2A forecasting decision from Phase 16 into the **actual competition submission file**.

Phases 11–16 already established:

- the canonical requested-demand history;
- the complete weekly panel;
- Task 2A EDA;
- leakage-safe lag/rolling/calendar features;
- rolling-origin 10-week validation;
- simple forecast baselines;
- advanced model challengers;
- baseline-vs-advanced comparison;
- exactly one frozen total-volume champion;
- exactly one frozen Fresh chilled-volume champion;
- structural zero rules for Style and Tech chilled demand;
- final Phase 17 post-processing ownership.

Phase 17 must now execute that frozen design **without reopening model selection**.

The phase must answer twelve questions:

1. Can the official Task 2A future input be loaded without changing its identifiers or rows?
2. Can target-week calendar features be created entirely from official future-known calendar information?
3. Can the frozen total-volume champion generate one forecast for every official row?
4. Can the frozen Fresh chilled champion generate the Fresh chilled forecasts?
5. Are Style chilled forecasts exactly zero?
6. Are Tech chilled forecasts exactly zero?
7. Are impossible negative outputs corrected only by the predeclared Phase 17 rule?
8. Is chilled demand always a subset of total demand after final post-processing?
9. Are all supplied `row_id` values preserved unchanged?
10. Are predictions mapped to the exact official submission template?
11. Is `submission_task2a.csv` exported without extra/debug columns?
12. Does a hard final validator prove the Task 2A file is submission-ready?

Phase 17 is **not** another modelling phase.

It must **not**:

- reopen Phase 14 validation;
- compare new model families;
- tune hyperparameters;
- tune ensemble weights;
- choose a different baseline after viewing official test predictions;
- change feature definitions because forecasts look unusual;
- use future actual demand;
- use Task 2A test outputs as labels;
- use proprietary model APIs or external AutoML;
- alter Task 1 outputs;
- begin Task 2B.

---

# 2. Finalized master-inventory contract

The finalized WayLoom Datathon master task inventory defines Phase 17 exactly as follows.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-242** | [O] | P0 | DT-239–DT-241 | Load `task2a_test_inputs.csv` |
| [ ] | **DT-243** | [O] | P0 | Phase 16 | Generate future known calendar features |
| [ ] | **DT-244** | [O] | P0 | Phase 16 | Produce total-volume forecast |
| [ ] | **DT-245** | [O] | P0 | Phase 16 | Produce Fresh chilled forecast |
| [ ] | **DT-246** | [O] | P0 | Phase 16 | Set Style chilled exactly to 0 |
| [ ] | **DT-247** | [O] | P0 | Phase 16 | Set Tech chilled exactly to 0 |
| [ ] | **DT-248** | [O] | P0 | Phase 16 | Clip negative forecasts |
| [ ] | **DT-249** | [O] | P0 | Phase 16 | Enforce chilled ≤ total |
| [ ] | **DT-250** | [O] | P0 | Phase 16 | Preserve official `row_id` |
| [ ] | **DT-251** | [O] | P0 | Phase 16 | Map predictions to exact template |
| [ ] | **DT-252** | [O] | P0 | DT-242–DT-251 | Export `submission_task2a.csv` |
| [ ] | **DT-253** | [O] | P0 | Phase 16 | Validate Task 2A file |

**Phase complete:** [ ]  
**TASK 2A FINAL OUTPUT READY:** NO  
**READY FOR PHASE 18:** NO

---

# 3. Official Task 2A requirements that constrain Phase 17

The official Challenge Booklet requires WayLoom to forecast ordered volume for each supplied depot, brand, and future forecast week over the **10 future weeks** in `task2a_test_inputs.csv`.

The two required predictions are:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

Official semantics:

```text
pred_total_volume_m3
= total ordered volume for that depot + brand + week

pred_chilled_volume_m3
= chilled portion of that total
```

Official output rules include:

- `task2a_test_inputs.csv` has one row per depot, brand, and forecast week;
- `submission_task2a.csv` is the official template;
- preserve the supplied `row_id` values unchanged;
- fill the two prediction columns;
- only Fresh has chilled demand;
- Style chilled must be exactly `0`;
- Tech chilled must be exactly `0`;
- Task 2A predicts volume only; do not convert the result into vehicle or driver counts.

The challenge booklet does **not** prescribe:

- CatBoost vs LightGBM vs a baseline;
- ensemble weights;
- the final-training implementation;
- the exact clipping implementation;
- the exact software architecture of the inference runner.

Those are WayLoom engineering decisions frozen by Phases 13–16.

## 3.1 Chilled ≤ total

The official definition says chilled volume is the **chilled portion of total volume**. Therefore a final submission with:

```text
pred_chilled_volume_m3 > pred_total_volume_m3
```

would contradict the target definition.

The WayLoom master plan therefore makes `chilled <= total` a hard final-output acceptance check.

## 3.2 Competition modelling/data restrictions remain active

Phase 17 must still respect the official restrictions:

- no pre-trained model substitution;
- no proprietary API-based modelling/preprocessing;
- no low-code/no-code fully automated modelling workflow;
- no public/private transmission of competition datasets or private derivatives to third parties;
- accurate AI-tool disclosure later.

---

# 4. Source hierarchy

Use the following order of authority:

1. official Challenge Booklet and supplied competition files/templates;
2. finalized `WAYLOOM_DATATHON_MASTER_PLAN.md`;
3. approved Phase 11 Task 2A history contract;
4. approved Phase 13 forecasting-feature contract;
5. approved Phase 14 validation contract;
6. approved Phase 15 baseline contract;
7. approved Phase 16 advanced-model/final-selection contract;
8. `configs/task2a_final_models.yaml` frozen by Phase 16;
9. this Phase 17 contract;
10. explicit engineering assumptions.

If a lower-level design conflicts with an official artifact:

```text
STOP
```

Do not silently reinterpret the competition file.

---

# 5. Frozen upstream state

Phase 17 starts only if Phase 16 has passed.

## 5.1 Frozen final configuration

Canonical handoff:

```text
configs/task2a_final_models.yaml
```

Expected high-level state:

```yaml
state: FROZEN
selection_complete: true
```

It must identify exactly one:

```text
total champion
```

and exactly one:

```text
Fresh chilled champion
```

Each champion may be:

```text
baseline
single locally trained model
fixed predeclared ensemble
```

Phase 17 must execute the frozen identity exactly.

## 5.2 Structural chilled rules

The frozen Phase 16 contract must retain:

```text
Style chilled = 0
Tech chilled = 0
```

These are output rules, not learned models.

## 5.3 Frozen post-processing ownership

Phase 16 deliberately deferred final output corrections to Phase 17:

```text
clip negative forecasts

enforce chilled <= total
```

Phase 17 may perform those transformations because they are already frozen in the final config.

It must not invent additional test-time corrections.

## 5.4 Task 1 is frozen

Never modify:

```text
configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv
```

---

# 6. Recommended Codex model / token strategy

Phase 17 is high stakes but mostly deterministic final-fit/inference/output engineering.

Recommended:

```text
GPT-5.6 Terra
Reasoning: High
```

Escalate only if there is a genuine model-serialization or ensemble-orchestration problem:

```text
GPT-5.6 Sol
Reasoning: Medium/High
```

Do not spend the strongest model merely to run repetitive schema/output tests.

---

# 7. Data-safety execution model

Codex/VS Code may autonomously:

- read tracked code/config/docs;
- create/refactor Phase 17 code;
- create synthetic test fixtures;
- run unit/integration tests on synthetic fixtures;
- run `pytest`;
- run `python -m pip check`;
- inspect Git status/diff;
- fix ordinary implementation/test failures;
- build a deterministic local command for real inference;
- review sanitized PASS/FAIL output.

Codex must not inspect or print row-level content from:

```text
data/raw/**
data/interim/**
reports/private/**
```

unless the user has independently confirmed a compliant fully local workflow that does not transmit competition data to the model provider.

The default competition-safe workflow remains:

```text
Codex implements + tests synthetically
        ↓
Human executes real competition-data command locally
        ↓
Human returns sanitized PASS/FAIL
        ↓
Fresh Codex review
```

---

# 8. Phase 17 inputs and outputs

## 8.1 Required tracked inputs

```text
configs/dataset_manifest.yaml
configs/task2a_history.yaml
configs/task2a_features.yaml
configs/task2a_validation.yaml
configs/task2a_baselines.yaml
configs/task2a_advanced_models.yaml
configs/task2a_final_models.yaml
```

Use the existing approved paths; do not duplicate a registry/config merely to simplify Phase 17.

## 8.2 Required private/local inputs

At minimum:

```text
data/interim/task2a_weekly_panel.csv
```

Potentially also:

```text
data/interim/task2a_multihorizon_train.csv
```

if the frozen model-based champion requires the direct multi-horizon training table.

Official/private raw inputs resolved through the manifest:

```text
task2a_test_inputs.csv
calendar.csv
submission_task2a.csv template
```

## 8.3 Required final output

```text
outputs/submission_task2a.csv
```

## 8.4 Required private reports

Recommended:

```text
reports/private/phase17_task2a_final/
├── run_manifest.json
├── test_input_validation.json
├── forecast_origin_validation.json
├── future_calendar_validation.json
├── final_fit_summary.json
├── raw_prediction_diagnostics.json
├── postprocessing_summary.json
├── row_id_validation.json
├── template_validation.json
├── submission_validation.json
└── phase17_final_report.md
```

Do not commit private values.

---

# 9. Required repository additions

Create or update:

```text
src/task2a/final_fit.py
src/task2a/final_inference.py
src/task2a/submission.py

scripts/run_task2a_final_inference.py
scripts/validate_task2a_submission.py

configs/task2a_inference.yaml

docs/task2a_final_inference_spec.md

tests/test_task2a_final_fit.py
tests/test_task2a_final_inference.py
tests/test_task2a_submission.py
```

Reuse rather than duplicate:

```text
src/task2a/history.py
src/task2a/features.py
src/task2a/calendar_features.py
src/task2a/multihorizon.py
src/task2a/baselines.py
src/task2a/advanced_models.py
src/task2a/model_preprocessing.py
src/task2a/ensembles.py
src/task2a/model_selection.py
```

Phase 17 should be an orchestration layer over already-tested logic.

---

# 10. Phase 17 execution checkpoints

Recommended implementation order:

```text
Checkpoint A
DT-242
Official future grid + row-ID validation
        ↓
Checkpoint B
DT-243
Future-known calendar features + horizon mapping
        ↓
Checkpoint C
DT-244–DT-245
Frozen total + Fresh chilled champion execution
        ↓
Checkpoint D
DT-246–DT-249
Structural zeros + frozen post-processing
        ↓
Checkpoint E
DT-250–DT-251
Row-ID/template mapping
        ↓
Checkpoint F
DT-252–DT-253
Atomic export + hard final validation
        ↓
Human local run
        ↓
Independent review
```

Do not skip directly to CSV export.

---

# 11. Canonical final forecast origin

Phase 17 needs one final information cutoff for historical demand.

Recommended canonical definition:

```text
final_forecast_origin
=
latest week in the approved Phase 11 weekly panel for which historical demand is fully known
```

Use the canonical continuous week date/key established in Phase 11/13, preferably:

```text
week_start_date
```

Do not determine final origin separately per depot/brand unless an earlier approved contract explicitly says so.

The preferred global rule is:

```text
one common final origin
```

because the official test covers a common 10-week future forecast period.

Required checks:

- all required historical series are valid through the approved origin;
- no unresolved weekly gaps exist;
- no historical target after the origin is used to generate origin features;
- every official target week is after the origin;
- each official test target week maps to a valid horizon `1..10`.

If the supplied official test grid does not align with the expected final origin/horizon contract:

```text
STOP
```

Do not silently shift the origin.

---

# 12. DT-242 — Load `task2a_test_inputs.csv`

**Mark:** [O]  
**Priority:** P0

## 12.1 Objective

Load the official future Task 2A forecast grid while preserving every supplied identifier and row.

## 12.2 Official grain

The booklet defines:

```text
one row per depot + brand + forecast week
```

and supplies:

```text
row_id
```

as the official submission identifier.

## 12.3 Loading rules

Use the canonical manifest/path loader.

Immediately create an internal immutable order marker:

```text
__official_row_order = 0,1,2,...
```

This is an engineering safeguard.

Do not expose it in the final CSV.

## 12.4 Required validations

At minimum verify:

```text
row_id exists
row_id non-null
row_id nonblank
row_id unique

depot exists
brand exists
forecast-week fields exist according to the supplied schema

row count > 0
```

Validate brand against the approved official domain:

```text
Fresh
Style
Tech
```

Validate depot using the approved reference/Phase 11 domain.

Do not invent missing rows.

Do not drop unexpected rows to make a clean 10-week grid.

## 12.5 Official-week mapping

Use the actual approved schema/manifest for Task 2A test forecast-week fields.

Where the canonical fields are `iso_year` and `iso_week`, retain them unchanged.

Do not recalculate them from an unrelated date if they are already supplied.

## 12.6 Tests

Synthetic tests:

- valid unique row IDs;
- duplicate `row_id` rejected;
- blank `row_id` rejected;
- missing brand rejected;
- unknown brand rejected;
- required forecast-week field missing;
- original row-order marker exact;
- loader does not mutate input.

## 12.7 Definition of Done

- [ ] official test file loads through manifest;
- [ ] every row is preserved;
- [ ] `row_id` unique and immutable;
- [ ] official order marker captured;
- [ ] no prediction made yet.

## 12.8 STOP conditions

Stop if:

- duplicate `row_id` exists;
- official schema cannot be resolved;
- an official row must be dropped to continue.

---

# 13. DT-243 — Generate future known calendar features

**Mark:** [O]  
**Priority:** P0

## 13.1 Objective

Recreate the exact target-week calendar features used by the frozen Phase 16 approach.

## 13.2 Source

Use official:

```text
calendar.csv
```

Only future-known calendar context is allowed.

Do not call external calendars, holiday APIs, weather APIs, or web services.

## 13.3 Required weekly context

Reuse the Phase 12/13 canonical weekly calendar feature builder.

Examples of approved future-known fields include:

```text
target_operating_days

target_payday_days
target_has_payday

target_holiday_days
target_has_holiday

target_festival_days
target_has_festival

target_max_festival_ramp
target_mean_festival_ramp

target_monsoon_days
target_monsoon_day_fraction
target_has_monsoon_day
```

Use only those required by the frozen final feature profile.

## 13.4 Horizon mapping

For each official test row derive/validate:

```text
forecast_horizon ∈ {1,...,10}
```

relative to the approved final forecast origin.

Required:

```text
target_week = final_origin + forecast_horizon
```

using the canonical weekly date index.

Do not infer horizon from row order.

## 13.5 Calendar completeness

Every official target week must map to complete official calendar context.

Missing target-week calendar coverage is a hard failure.

Do not fill missing official calendar context with guesses.

## 13.6 Tests

- horizon 1;
- horizon 10;
- horizon 0 rejected;
- horizon 11 rejected;
- cross-year future week;
- ISO week 53;
- operating-day aggregation;
- festival/payday/holiday features;
- monsoon mixed week;
- festival ramp bounds;
- missing target calendar coverage fails;
- external context never used.

## 13.7 Definition of Done

- [ ] every official test row has a valid horizon 1..10;
- [ ] all required calendar features generated by canonical code;
- [ ] no target-week actual demand used;
- [ ] no calendar gap remains.

---

# 14. Final-fit policy for model-based champions

The master inventory labels Phase 17 as final inference, but a model-based champion still needs a model fitted on the allowed full historical training population before it can predict the future test grid.

This is **execution of the frozen Phase 16 configuration**, not renewed model selection.

## 14.1 Final training population

Use only historical direct multi-horizon rows whose labels were actually known by the final forecast origin.

Recommended condition:

```text
training_row.target_week_start_date <= final_forecast_origin
```

This mirrors the Phase 14 leakage rule.

Do not use:

```text
any future official Task 2A target
any future predicted value as a label
```

## 14.2 Frozen model settings

Use exactly:

- champion family;
- feature profile;
- categorical handling;
- hyperparameters;
- seed;
- frozen final iteration value/policy;
- baseline window/weights/fallback if baseline champion;
- component IDs/weights if ensemble.

No early-stopping search is needed if Phase 16 already froze a deterministic final iteration count.

## 14.3 Baseline champion

If a Phase 15 baseline is champion:

- no ML model training is needed;
- use the canonical baseline code;
- calculate prediction using history available through final origin only.

## 14.4 Ensemble champion

Fit/execute every frozen component independently.

Combine by explicit key, never current row position.

Use exactly the frozen weights.

Do not drop a component because its forecast looks strange.

## 14.5 Model artifacts

Phase 32 formally owns final model/artifact management.

Phase 17 may produce private runtime state necessary for final inference, but do not create competing permanent model-artifact conventions here.

The inference orchestration should nevertheless be designed so Phase 32 can serialize/reload the selected Task 2A components cleanly.

---

# 15. DT-244 — Produce total-volume forecast

**Mark:** [O]  
**Priority:** P0

## 15.1 Objective

Generate exactly one raw total-volume prediction for every official Task 2A test row using the frozen total champion.

## 15.2 Allowed champion types

```text
baseline
CatBoost
LightGBM
fixed ensemble
```

according to `configs/task2a_final_models.yaml`.

## 15.3 Feature generation

For the final origin:

1. load the canonical weekly panel;
2. verify no unresolved history gaps;
3. build origin-known lag/rolling/trend features using Phase 13 code;
4. generate official target-week calendar features;
5. carry static series features (`depot`, `brand`);
6. carry `forecast_horizon`;
7. resolve exactly the frozen feature profile;
8. assert no target column is present in `X_test`.

All demand-derived values must come from weeks:

```text
<= final_forecast_origin
```

## 15.4 No recursive actual-demand use

The test covers ten future weeks.

Do not simulate:

```text
predict h1
pretend h1 prediction is actual demand
update lag features
predict h2
```

unless the frozen Phase 16 champion explicitly used an approved recursive architecture—which the finalized WayLoom Phase 13/16 design does not.

The canonical architecture is direct multi-horizon.

All h=1..10 rows use the same origin-known demand history, with different target-week calendar/horizon context.

## 15.5 Raw output

Create internal:

```text
raw_pred_total_volume_m3
```

Do not write this debug column to the official template.

Phase 17 post-processing comes later.

## 15.6 Requirements

One raw forecast per official row.

Raw prediction must be:

```text
numeric
finite
```

Negative raw values are allowed temporarily because DT-248 owns clipping.

## 15.7 Tests

- baseline champion execution;
- CatBoost champion execution;
- LightGBM champion execution;
- ensemble champion execution;
- exact feature profile;
- target columns excluded;
- h1..h10 all produced;
- same-origin historical features stable across horizons;
- future-demand mutation invariant;
- finite raw outputs;
- missing component fails;
- invalid frozen champion fails.

## 15.8 STOP conditions

Stop if:

- a new candidate/model search path appears;
- a required champion component is unavailable;
- a prediction is NaN/Inf;
- a future actual demand value is required.

---

# 16. DT-245 — Produce Fresh chilled forecast

**Mark:** [O]  
**Priority:** P0

## 16.1 Objective

Generate the raw chilled-volume forecast for official rows where:

```text
brand == Fresh
```

using exactly the frozen Fresh chilled champion.

## 16.2 Training/feature population

If the champion is model-based, final fit uses only the approved Fresh historical training rows.

Do not add Style/Tech zero rows to final chilled training if Phase 16 explicitly selected a Fresh-only model.

## 16.3 Feature contract

Reuse Phase 13 features and the frozen Fresh chilled feature profile.

Allowed chilled-history features may include:

```text
chilled_lag_1
chilled_lag_2
chilled_lag_4
chilled_lag_13
chilled_lag_52
chilled_roll_mean_4
chilled_roll_mean_8
chilled_roll_mean_13
chilled trend features
```

plus approved total-demand/calendar/static/horizon features if the frozen profile includes them.

## 16.4 Raw output

Internal:

```text
raw_pred_chilled_volume_m3
```

Fresh raw values may temporarily be:

```text
negative
or > raw total
```

because DT-248/249 own the final constraints.

They must still be finite numeric values.

## 16.5 Tests

- baseline Fresh chilled champion;
- ML Fresh chilled champion;
- ensemble Fresh chilled champion;
- Style/Tech never sent through Fresh-only model unnecessarily;
- future chilled-demand mutation invariant;
- horizon 1..10 complete;
- finite raw Fresh predictions.

---

# 17. DT-246 — Set Style chilled exactly to 0

**Mark:** [O]  
**Priority:** P0

Official rule:

```text
Style pred_chilled_volume_m3 = 0
```

Use exact numeric zero:

```python
0.0
```

Do not output:

```text
NaN
-0.0 as a deliberately encoded special state
1e-9
model-estimated chilled demand
```

If upstream code produced a Style chilled prediction, it must not override the structural official rule.

Required invariant:

```text
all Style rows → chilled == 0.0 exactly
```

Tests:

- one Style row;
- multiple Style weeks;
- nonzero upstream placeholder overridden to zero;
- zero remains zero after DT-248/249.

---

# 18. DT-247 — Set Tech chilled exactly to 0

**Mark:** [O]  
**Priority:** P0

Official rule:

```text
Tech pred_chilled_volume_m3 = 0
```

Use exact numeric:

```python
0.0
```

Required invariant:

```text
all Tech rows → chilled == 0.0 exactly
```

Tests mirror DT-246.

---

# 19. DT-248 — Clip negative forecasts

**Mark:** [O]  
**Priority:** P0

## 19.1 Frozen rule

Phase 16 assigned negative clipping to Phase 17.

Apply:

```text
pred_total_volume_m3 = max(raw_pred_total_volume_m3, 0.0)

pred_chilled_volume_m3 = max(raw_or_structural_chilled, 0.0)
```

This applies after raw forecasts exist.

## 19.2 Why this is allowed here

Order volume cannot be physically negative, and the final WayLoom config explicitly froze this post-processing rule before official test prediction review.

## 19.3 Do not add any other clipping

Do not:

- cap large positive forecasts;
- winsorize;
- replace negatives with historical medians;
- take absolute values;
- round to integers;
- invent minimum positive demand.

## 19.4 Diagnostics

Record privately:

```text
negative_raw_total_count
negative_raw_chilled_count
minimum_raw_total
minimum_raw_chilled
postprocessed_total_count
postprocessed_chilled_count
```

Do not print private values in a public/screenshot summary.

## 19.5 Tests

- negative total → zero;
- zero total unchanged;
- positive total unchanged;
- negative Fresh chilled → zero;
- structural Style/Tech zero unchanged;
- NaN/Inf rejected before clipping;
- `abs()` behavior explicitly absent.

---

# 20. DT-249 — Enforce chilled ≤ total

**Mark:** [O]  
**Priority:** P0

## 20.1 Frozen rule

After non-negativity:

```text
pred_chilled_volume_m3
=
min(pred_chilled_volume_m3, pred_total_volume_m3)
```

for every row.

## 20.2 Recommended deterministic ordering

Use this exact post-processing sequence:

```text
1. produce raw total
2. produce raw Fresh chilled
3. set Style chilled = 0
4. set Tech chilled = 0
5. clip total below 0 to 0
6. clip chilled below 0 to 0
7. cap chilled at total
8. validate
```

Consequences:

- if total becomes `0`, Fresh chilled also becomes `0` if it was positive;
- Style/Tech remain exact zero;
- every final row obeys:

```text
0 <= chilled <= total
```

## 20.3 No hidden reallocation

Do not increase total to accommodate chilled.

The frozen policy is:

```text
cap chilled downward
```

not:

```text
raise total upward
```

## 20.4 Diagnostics

Record:

```text
raw_chilled_gt_raw_total_count
post_clip_chilled_gt_total_count_before_cap
chilled_capped_count
```

## 20.5 Tests

- chilled below total unchanged;
- chilled equal total unchanged;
- chilled above total capped;
- total clipped to zero then chilled capped to zero;
- Style/Tech zero invariant preserved;
- no total inflation.

---

# 21. DT-250 — Preserve official `row_id`

**Mark:** [O]  
**Priority:** P0

## 21.1 Official requirement

The booklet explicitly says:

```text
row_id
Supplied identifier. Keep unchanged.
```

## 21.2 Required checks

Final output must have:

```text
same row_id values
same number of row_id values
no duplicate row_id
no missing row_id
no added row_id
no modified row_id
```

Use ordered-list equality against the official template as an additional engineering safeguard:

```text
final row_id sequence == official template row_id sequence
```

The booklet explicitly requires Task 1 original order; for Task 2A it requires unchanged rows/identifiers. Preserving official template order is the safest implementation and avoids unnecessary risk.

## 21.3 Prediction mapping

Map internal predictions by:

```text
row_id
```

not raw DataFrame row position.

Then restore official template order.

Never regenerate `row_id`.

## 21.4 Tests

- shuffled internal prediction table maps correctly by ID;
- missing prediction ID fails;
- extra prediction ID fails;
- duplicate prediction ID fails;
- modified ID fails;
- ordered template sequence restored.

---

# 22. DT-251 — Map predictions to exact template

**Mark:** [O]  
**Priority:** P0

## 22.1 Structural authority

Use the official:

```text
Submission Templates/submission_task2a.csv
```

as the final schema authority.

Do not manually recreate a "similar" CSV if the official template exists.

## 22.2 Required columns

Official prediction columns:

```text
row_id
pred_total_volume_m3
pred_chilled_volume_m3
```

The template itself is the final authority for exact column order.

## 22.3 Fill only prediction columns

Preserve official identifiers/rows.

Fill:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

Do not add:

```text
depot
brand
iso_year
iso_week
forecast_horizon
model_name
raw_total
raw_chilled
clipped_flag
ensemble_id
__official_row_order
```

## 22.4 Mapping contract

Recommended:

```text
template row_id
LEFT JOIN / MAP
final predictions by row_id
```

Validate one-to-one.

Do not use depot+brand+week as the final submission identifier if official `row_id` exists.

## 22.5 Tests

- exact official template columns;
- exact column order;
- only prediction fields filled;
- extra debug field fails;
- missing prediction fails;
- duplicate prediction mapping fails;
- template identifier unchanged.

---

# 23. DT-252 — Export `submission_task2a.csv`

**Mark:** [O]  
**Priority:** P0

## 23.1 Required filename

```text
outputs/submission_task2a.csv
```

Use:

```python
index=False
```

## 23.2 Atomic export

Recommended:

```text
write temporary candidate file
        ↓
read candidate back
        ↓
run DT-253 validator
        ↓
only if PASS:
rename/move atomically to outputs/submission_task2a.csv
```

This avoids leaving a misleading "final" file after failed validation.

## 23.3 Deterministic output

Given identical:

- frozen config;
- historical data;
- official test grid;
- package versions/seeds;

Phase 17 should produce deterministic predictions within the expected numerical tolerance of the chosen model family.

## 23.4 No rounding unless frozen

The Phase 16 frozen config uses:

```text
rounding: none
```

Therefore do not round output merely for appearance.

CSV serialization may use standard numeric formatting but must not intentionally alter precision.

## 23.5 Tests

- index column absent;
- exact filename;
- read-back success;
- numeric dtypes recoverable;
- repeat synthetic inference produces equivalent file contents/values.

---

# 24. DT-253 — Validate Task 2A file

**Mark:** [O]  
**Priority:** P0

This is the Phase 17 hard gate.

Create:

```text
scripts/validate_task2a_submission.py
```

It must validate the **current file** without silently repairing it.

## 24.1 File/schema checks

Verify:

```text
file exists
file readable
correct filename
exact official template columns
exact official column order
no accidental CSV index column
no debug columns
```

## 24.2 Row-ID checks

Verify:

```text
row count matches official template
row_id non-null
row_id unique
row_id values exactly preserved
no missing row_id
no extra row_id
official template order preserved
```

## 24.3 Total forecast checks

```text
pred_total_volume_m3 numeric
finite
not NaN
not Inf
>= 0
```

## 24.4 Chilled forecast checks

```text
pred_chilled_volume_m3 numeric
finite
not NaN
not Inf
>= 0
```

## 24.5 Structural brand rules

Using the official test grid locally:

```text
Style chilled == 0 exactly
Tech chilled == 0 exactly
```

Do not print row IDs for violations in the sanitized console summary.

## 24.6 Subset rule

For all rows:

```text
pred_chilled_volume_m3 <= pred_total_volume_m3
```

## 24.7 Coverage checks

Validate every official test input row has exactly one final prediction.

No test row may disappear because:

- a lag is missing;
- a model cannot encode a category;
- a baseline seasonal lookup is unavailable;
- a calendar field is missing.

Such issues must have been resolved by the frozen model/fallback design or must cause a hard failure.

## 24.8 Frozen-config proof

Validator/report should confirm:

```text
final config state = FROZEN
selection_complete = true
exactly one total champion
exactly one Fresh chilled champion
Style zero rule enabled
Tech zero rule enabled
clip-negative enabled
chilled<=total enabled
```

## 24.9 Inference integrity checks

Confirm from run manifest:

```text
no Phase 17 model search
no new hyperparameter candidates
no tuned ensemble weights
Phase 16 champion IDs unchanged
future actual demand used = NO
```

## 24.10 Final status

Only if every check passes:

```text
TASK 02A FINAL VALIDATION: PASS
TASK 02A OUTPUT READY: YES
```

Otherwise:

```text
TASK 02A FINAL VALIDATION: FAIL
TASK 02A OUTPUT READY: NO
```

---

# 25. `configs/task2a_inference.yaml`

Recommended tracked configuration:

```yaml
version: 1

final_model_config:
  path: configs/task2a_final_models.yaml
  required_state: FROZEN

inputs:
  weekly_panel: data/interim/task2a_weekly_panel.csv
  multihorizon_train: data/interim/task2a_multihorizon_train.csv
  test_manifest_key: task2a_test_inputs
  calendar_manifest_key: calendar
  template_manifest_key: submission_task2a

forecast_origin:
  strategy: latest_complete_historical_week
  require_global_origin: true

future_grid:
  expected_horizons:
    - 1
    - 2
    - 3
    - 4
    - 5
    - 6
    - 7
    - 8
    - 9
    - 10
  require_calendar_coverage: true

postprocessing:
  clip_negative: true
  enforce_chilled_le_total: true
  style_chilled_zero: true
  tech_chilled_zero: true
  rounding: none

submission:
  output_path: outputs/submission_task2a.csv
  use_official_template: true
  map_by: row_id
  preserve_template_order: true
  atomic_write: true

privacy:
  report_dir: reports/private/phase17_task2a_final
  print_row_ids: false
  print_prediction_rows: false
```

This must agree with the frozen Phase 16 config.

If the two configs disagree on a final-output rule:

```text
STOP
```

Do not let Phase 17 override Phase 16 silently.

---

# 26. Recommended implementation architecture

## `src/task2a/final_fit.py`

Recommended functions/classes:

```python
validate_frozen_task2a_config(...)
resolve_final_forecast_origin(...)
build_final_training_population(...)
fit_total_champion(...)
fit_fresh_chilled_champion(...)
fit_component_if_required(...)
```

The code must support:

```text
baseline champion
single-model champion
ensemble champion
```

without model search.

## `src/task2a/final_inference.py`

Recommended:

```python
load_task2a_test_grid(...)
build_target_week_calendar_features(...)
build_final_origin_features(...)
build_task2a_test_feature_matrix(...)
predict_total_volume(...)
predict_fresh_chilled_volume(...)
apply_structural_chilled_rules(...)
apply_final_postprocessing(...)
run_task2a_final_inference(...)
```

## `src/task2a/submission.py`

Recommended:

```python
map_predictions_by_row_id(...)
fill_task2a_template(...)
validate_task2a_submission_frame(...)
write_task2a_submission_atomic(...)
```

Keep submission validation separate from forecasting code so it can independently reject a bad file.

---

# 27. Final-run manifest

Create private:

```text
reports/private/phase17_task2a_final/run_manifest.json
```

Recommended fields:

```text
phase
created_at
git_commit
final_config_path
final_config_hash
feature_config_hash
history_config_hash
validation_config_hash
final_forecast_origin
champion_total_id
champion_chilled_id
champion_total_type
champion_chilled_type
seed
postprocessing_policy
test_row_count
template_row_count
calendar_coverage_status
future_actual_demand_used
model_search_performed
ensemble_weight_search_performed
library_versions
```

Expected:

```text
future_actual_demand_used = false
model_search_performed = false
ensemble_weight_search_performed = false
```

Do not write private row-level predictions into tracked files.

---

# 28. Required synthetic tests

Create comprehensive synthetic tests.

## 28.1 Frozen config

- valid baseline champion config;
- valid CatBoost config;
- valid LightGBM config;
- valid ensemble config;
- unfrozen config rejected;
- `selection_complete=false` rejected;
- missing total champion rejected;
- missing chilled champion rejected;
- bad ensemble weights rejected;
- structural zero rule disabled rejected;
- post-processing mismatch rejected.

## 28.2 Test input loading

- unique `row_id`;
- duplicate ID rejected;
- blank ID rejected;
- unknown brand rejected;
- original order marker captured;
- all rows retained.

## 28.3 Forecast origin/horizon

- latest historical origin selected;
- one global origin;
- target week after origin;
- horizon 1;
- horizon 10;
- horizon 0 rejected;
- horizon 11 rejected;
- cross-year mapping;
- ISO week 53;
- missing calendar week rejected.

## 28.4 Final training population

- training label target week <= final origin;
- future target row excluded;
- target columns excluded from X;
- baseline requires no model fitting;
- model final iteration comes from frozen config;
- no tuning loop.

## 28.5 Total forecast

- baseline champion;
- CatBoost champion;
- LightGBM champion;
- ensemble champion;
- exact row coverage;
- finite prediction;
- future-demand mutation invariant;
- h10 unaffected by h1 actual demand.

## 28.6 Fresh chilled forecast

- Fresh baseline/model/ensemble;
- only Fresh fed to Fresh-only model as appropriate;
- finite raw predictions;
- future chilled mutation invariant.

## 28.7 Structural zero

- Style exact zero;
- Tech exact zero;
- nonzero upstream value overwritten to zero;
- zero survives clipping/capping.

## 28.8 Negative clipping

- negative total → zero;
- negative chilled → zero;
- positive unchanged;
- zero unchanged;
- NaN/Inf rejected;
- no absolute-value transformation.

## 28.9 Chilled≤total

- below unchanged;
- equal unchanged;
- above capped;
- total zero forces chilled zero;
- total never raised to satisfy chilled.

## 28.10 Row-ID/template

- shuffled predictions correctly mapped by `row_id`;
- missing prediction fails;
- extra prediction fails;
- duplicate mapping fails;
- exact template schema;
- exact template order;
- extra column fails;
- accidental `Unnamed: 0` fails.

## 28.11 End-to-end

Synthetic end-to-end test:

```text
weekly history
→ frozen config
→ future test grid
→ future calendar
→ final predictions
→ structural rules
→ clipping
→ chilled cap
→ official synthetic template
→ atomic CSV
→ read-back validator
```

Run twice.

Assert equivalent final results.

---

# 29. Edge cases

## 29.1 Champion is a simple baseline

Do not force model training.

The final inference system must support a baseline champion as a first-class valid outcome.

## 29.2 Total champion and chilled champion are different families

Valid.

Example:

```text
total = CatBoost
Fresh chilled = recent seasonal baseline
```

Phase 17 must execute both independently.

## 29.3 Ensemble has model + baseline

Valid if Phase 16 froze it.

Align components by official row key/metadata, not current DataFrame row position.

## 29.4 Lag 52 unavailable for newest/short series

Follow the frozen Phase 13/16 feature/preprocessing policy.

Do not invent future demand.

## 29.5 Future target week is ISO week 53

Use canonical continuous week mapping and official calendar.

Do not assume every year has week 53.

## 29.6 Official test row order differs from internal sorted feature order

Internal sorting is fine.

Final mapping must use `row_id` and restore official template order.

## 29.7 Raw total negative and raw chilled positive

Correct final sequence:

```text
total -> 0
chilled -> nonnegative
chilled -> min(chilled, 0) = 0
```

## 29.8 Raw chilled > total

Cap chilled downward.

Do not increase total.

## 29.9 Style/Tech raw chilled model output accidentally exists

Ignore/overwrite it.

Official structural zero wins.

## 29.10 Unknown category at final inference

The frozen preprocessing/category-handling policy must handle it deterministically.

Do not refit an encoder on official test data merely to add a category.

If the frozen pipeline cannot handle the category:

```text
STOP
```

## 29.11 Official template contains placeholders

Replace only the prediction placeholders.

Do not alter identifiers.

## 29.12 Repeated local run

Must not silently change the frozen config.

Predictions should be deterministic within model numerical tolerance.

---

# 30. Phase 17 STOP conditions

`TASK 2A OUTPUT READY` must remain **NO** if any of the following occurs:

- Phase 16 did not pass;
- `configs/task2a_final_models.yaml` is not frozen;
- more than one total champion remains;
- more than one Fresh chilled champion remains;
- Phase 17 starts hyperparameter/model/ensemble search;
- official test input has duplicate or missing `row_id`;
- an official row is dropped;
- future week cannot map to official calendar context;
- horizon is outside 1..10;
- final training includes a target label not known by the final origin;
- future actual demand enters test features;
- h=1 actual outcome is used to update h=2..10;
- target columns enter the predictor matrix;
- a frozen champion component is unavailable;
- raw prediction contains NaN/Inf;
- Style chilled is nonzero after post-processing;
- Tech chilled is nonzero after post-processing;
- final total is negative;
- final chilled is negative;
- final chilled exceeds total;
- `row_id` changes;
- template row coverage differs;
- final CSV has extra columns;
- final CSV has missing columns;
- read-back validation fails;
- private data must be exposed to the external agent;
- Task 1 frozen artifacts change;
- Phase 18 code is started before Phase 17 passes.

---

# 31. Phase 17 Definition of Done

Phase 17 passes only when:

- [ ] DT-242 PASS
- [ ] DT-243 PASS
- [ ] DT-244 PASS
- [ ] DT-245 PASS
- [ ] DT-246 PASS
- [ ] DT-247 PASS
- [ ] DT-248 PASS
- [ ] DT-249 PASS
- [ ] DT-250 PASS
- [ ] DT-251 PASS
- [ ] DT-252 PASS
- [ ] DT-253 PASS
- [ ] Phase 16 frozen config reused exactly
- [ ] no Phase 17 model search occurred
- [ ] one global final forecast origin resolved
- [ ] all official target weeks mapped to horizons 1..10
- [ ] canonical future calendar features reused
- [ ] final training uses only known historical labels
- [ ] future actual demand leakage = 0
- [ ] total forecast produced for every official row
- [ ] Fresh chilled forecast produced for every Fresh row
- [ ] Style chilled = 0 exactly
- [ ] Tech chilled = 0 exactly
- [ ] all final forecasts finite
- [ ] all final forecasts nonnegative
- [ ] chilled <= total for every row
- [ ] all official `row_id` values unchanged
- [ ] official template schema exact
- [ ] no extra columns
- [ ] `outputs/submission_task2a.csv` exported
- [ ] final CSV read-back passes
- [ ] synthetic unit/integration tests pass
- [ ] full safe regression suite passes
- [ ] `python -m pip check` passes
- [ ] private output paths remain ignored
- [ ] Task 1 artifacts unchanged
- [ ] independent review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 17 STATUS: PASS
TASK 02A FINAL OUTPUT READY: YES
READY FOR PHASE 18: YES
```

---

# 32. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-17-task2a-final-inference
```

Recommended commits:

```text
feat(task2a): add frozen final forecast execution
feat(task2a): add future calendar inference grid
feat(task2a): add final postprocessing rules
feat(task2a): add official template submission mapper
feat(task2a): add Task 2A submission validator
test(task2a): add final inference and submission tests
docs(task2a): document Phase 17 final inference contract
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

`outputs/submission_task2a.csv` handling depends on the repository's established private-output policy. Do not commit it publicly unless competition/repository policy permits it.

Before merge:

```bash
pytest -q
python -m pip check
git status
```

Merge only after:

```text
LOCAL PHASE 17 TASK2A FINAL INFERENCE: PASS
INDEPENDENT PHASE 17 REVIEW: PASS
```

---

# 33. Local real-data execution

The external agent implements the commands but the human executes them locally against competition data.

## 33.1 Final inference

Recommended:

```bash
python scripts/run_task2a_final_inference.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --multihorizon-table data/interim/task2a_multihorizon_train.csv \
  --history-config configs/task2a_history.yaml \
  --feature-config configs/task2a_features.yaml \
  --final-model-config configs/task2a_final_models.yaml \
  --inference-config configs/task2a_inference.yaml \
  --output outputs/submission_task2a.csv \
  --report-dir reports/private/phase17_task2a_final
```

If the frozen champion is purely baseline-based and does not need the multi-horizon training table, the CLI may accept that path but avoid loading it unnecessarily.

Do not create a second special CLI per champion family.

## 33.2 Final validation

```bash
python scripts/validate_task2a_submission.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --final-model-config configs/task2a_final_models.yaml \
  --submission outputs/submission_task2a.csv \
  --report-dir reports/private/phase17_task2a_final
```

PowerShell may use the same arguments on one line.

## 33.3 Sanitized expected status

Return only high-level results, for example:

```text
LOCAL PHASE 17 TASK2A FINAL INFERENCE: PASS
FINAL CONFIG FROZEN: YES
OFFICIAL TEST ROWS PREDICTED: YES
MISSING ROW_ID: 0
DUPLICATE ROW_ID: 0
STYLE CHILLED EXACT ZERO: YES
TECH CHILLED EXACT ZERO: YES
NEGATIVE FINAL TOTAL: 0
NEGATIVE FINAL CHILLED: 0
CHILLED > TOTAL: 0
NaN / INF: 0
OFFICIAL TEMPLATE: PASS
TASK 02A FINAL VALIDATION: PASS
TASK 02A OUTPUT READY: YES
```

Do not paste private forecast values or official row IDs into the coding agent.

---

# 34. Enhanced Codex / Cursor implementation prompt

The following prompt is optimized for **Codex in VS Code** and is also compatible with Cursor.

```text
You are implementing WayLoom Datathon PHASE 17 only.

PHASE:
Task 2A Final Inference & Submission

TASK RANGE:
DT-242 through DT-253

EXECUTION MODE:
High-risk controlled autonomous implementation with full SAFE engineering autonomy.

RECOMMENDED MODEL:
GPT-5.6 Terra — High reasoning

ESCALATE ONLY IF NEEDED:
GPT-5.6 Sol — Medium/High reasoning

You MAY:

- create/edit/refactor Phase 17 tracked code
- create/edit configuration
- create/edit documentation
- create synthetic fixtures
- run targeted pytest tests
- run the complete safe regression suite
- inspect tracebacks
- diagnose ordinary implementation failures
- fix ordinary bugs automatically
- rerun failed tests
- run python -m pip check
- inspect git status/diff
- verify ignore rules
- self-review against Phase 17 Definition of Done

Do NOT stop for routine coding/test failures that can safely be fixed.

STOP only for:

- official competition-rule ambiguity
- requirement to inspect restricted competition row-level data
- Phase 16 final configuration not genuinely frozen
- unresolved conflict with Phase 11–16 contracts
- missing final champion/component
- future-demand leakage that cannot be safely removed
- official test/template schema conflict
- genuine package/model-runtime incompatibility
- need to reopen model selection

DO NOT START PHASE 18.

==================================================
READ FIRST
==================================================

Read with targeted context:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase 17 and Task 2A final-output rules
4. PHASE_11_COMPETITION_CONTRACT.md
   - canonical Task 2A history
5. PHASE_13_COMPETITION_CONTRACT.md
   - final feature semantics
6. PHASE_14_COMPETITION_CONTRACT.md
   - label availability / leakage rules
7. PHASE_15_COMPETITION_CONTRACT.md
   - baseline execution semantics
8. PHASE_16_COMPETITION_CONTRACT.md
   - frozen champion and final config
9. PHASE_17_COMPETITION_CONTRACT.md
10. configs/task2a_final_models.yaml
11. existing Task 2A history/features/baseline/model/ensemble code

Use targeted reading.

Do not reread unrelated phases unless a direct dependency requires it.

TASK 1 IS FROZEN.

Do not modify:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do NOT inspect or print real competition rows from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for agent-run implementation/testing.

The HUMAN will execute the real Phase 17 final inference locally.

==================================================
OFFICIAL TASK 2A OUTPUT CONTRACT
==================================================

The official Task 2A test input contains one row per:

depot + brand + forecast week

for ten future weeks.

Final official output uses:

submission_task2a.csv

Preserve supplied:

row_id

unchanged.

Fill:

pred_total_volume_m3
pred_chilled_volume_m3

Official structural chilled rule:

Fresh:
forecast chilled demand

Style:
pred_chilled_volume_m3 = 0 exactly

Tech:
pred_chilled_volume_m3 = 0 exactly

Chilled is a portion of total, therefore final WayLoom acceptance requires:

0 <= pred_chilled_volume_m3 <= pred_total_volume_m3

Do not convert forecast volume to vehicle/driver counts.

==================================================
NO MODEL SEARCH
==================================================

Load:

configs/task2a_final_models.yaml

Require:

state = FROZEN
selection_complete = true

There must be exactly:

one total champion
one Fresh chilled champion

Phase 17 MUST NOT:

- tune parameters
- compare candidates
- change ensemble weights
- reopen Phase 14 validation
- change baseline formulas
- change features after viewing test predictions
- create a new model family

Execute the frozen design only.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2a/final_fit.py
src/task2a/final_inference.py
src/task2a/submission.py

scripts/run_task2a_final_inference.py
scripts/validate_task2a_submission.py

configs/task2a_inference.yaml

docs/task2a_final_inference_spec.md

tests/test_task2a_final_fit.py
tests/test_task2a_final_inference.py
tests/test_task2a_submission.py

Reuse all mature Phase 11–16 components instead of duplicating them.

==================================================
DT-242 — LOAD OFFICIAL TEST GRID
==================================================

Load task2a_test_inputs.csv via the canonical manifest.

Preserve every row.

Create internal:

__official_row_order = 0..N-1

Validate:

row_id exists
row_id nonblank
row_id unique
brand valid
depot valid
forecast-week schema resolvable
row count > 0

Do not drop rows.

Do not regenerate row_id.

==================================================
FINAL FORECAST ORIGIN
==================================================

Resolve one canonical final forecast origin:

latest complete historical week in the approved Phase 11 weekly panel.

Use the canonical continuous week key/date from Phase 11/13.

Require:

all official target weeks > final origin

every official target week maps to horizon 1..10

Do NOT infer horizon from row position.

Do NOT shift the origin to make the test grid fit.

If the official grid does not align:
STOP.

==================================================
DT-243 — FUTURE KNOWN CALENDAR FEATURES
==================================================

Use the existing Phase 12/13 canonical weekly calendar builder.

Source:
calendar.csv only.

Generate only feature fields required by the frozen feature profile.

May include:

target_operating_days

target_payday_days
target_has_payday

target_holiday_days
target_has_holiday

target_festival_days
target_has_festival

target_max_festival_ramp
target_mean_festival_ramp

target_monsoon_days
target_monsoon_day_fraction
target_has_monsoon_day

Create/validate:

forecast_horizon = 1..10

Use official calendar context only.

Do not call external calendar/weather APIs.

Missing target-week calendar coverage:
FAIL.

==================================================
FINAL FIT POLICY
==================================================

If champion is model-based:

build the final training population from historical direct multi-horizon rows where:

training_row.target_week_start_date <= final_forecast_origin

Use exactly frozen:

model family
parameters
feature profile
categorical/preprocessing policy
seed
final iteration rule/value

No tuning.

If champion is a baseline:

use the canonical baseline implementation and history through final origin only.

If champion is an ensemble:

execute every frozen component independently and combine using frozen weights.

Align components by explicit keys, never current row position.

==================================================
DT-244 — TOTAL FORECAST
==================================================

Produce exactly one:

raw_pred_total_volume_m3

for every official test row.

Use the frozen total champion.

Build test features with canonical Phase 13 code.

Demand-derived feature source weeks must all be:

<= final forecast origin

Do not recursively update h2..h10 with predicted/actual h1 demand.

This is the frozen direct multi-horizon design.

Raw predictions must be numeric and finite.

Do not clip yet.

==================================================
DT-245 — FRESH CHILLED FORECAST
==================================================

For brand == Fresh:

produce:

raw_pred_chilled_volume_m3

using exactly the frozen Fresh chilled champion.

If model-based, train only on approved Fresh chilled modelling population according to Phase 16.

Raw Fresh predictions must be finite.

Do not clip or cap at total yet.

==================================================
DT-246 — STYLE CHILLED ZERO
==================================================

For every Style row:

pred_chilled_volume_m3 = 0.0 exactly

This official structural rule overrides any accidental upstream model value.

==================================================
DT-247 — TECH CHILLED ZERO
==================================================

For every Tech row:

pred_chilled_volume_m3 = 0.0 exactly

==================================================
DT-248 — CLIP NEGATIVE FORECASTS
==================================================

Use the already frozen Phase 16 post-processing rule.

Apply:

pred_total_volume_m3 = max(raw_total, 0.0)

pred_chilled_volume_m3 = max(raw_or_structural_chilled, 0.0)

Do NOT:

- take absolute value
- replace negative with median
- cap large positive values
- round
- invent a minimum positive value

Reject NaN/Inf before clipping.

Record private counts of corrections.

==================================================
DT-249 — ENFORCE CHILLED <= TOTAL
==================================================

After non-negativity:

pred_chilled_volume_m3 = min(
    pred_chilled_volume_m3,
    pred_total_volume_m3,
)

Do NOT increase total to match chilled.

Recommended exact post-processing order:

1 raw total
2 raw Fresh chilled
3 Style chilled = 0
4 Tech chilled = 0
5 clip total below zero
6 clip chilled below zero
7 cap chilled at total
8 validate

Final invariant:

0 <= chilled <= total

for every row.

==================================================
DT-250 — PRESERVE OFFICIAL ROW_ID
==================================================

Final submission must contain exactly the supplied row_id values.

Assert:

same row count
same ID set
no missing ID
no extra ID
no duplicate ID
no modified ID

Use row_id as the prediction mapping key.

As an engineering safeguard restore exact official template row order.

Do not map final predictions solely by DataFrame row position.

==================================================
DT-251 — MAP TO EXACT OFFICIAL TEMPLATE
==================================================

Use the organizer-provided:

submission_task2a.csv

as final schema authority.

Fill only:

pred_total_volume_m3
pred_chilled_volume_m3

Keep official row_id unchanged.

No debug columns.

No depot/brand/week/model columns in final CSV unless the actual official template contains them; the template is authoritative.

Validate exact template column order.

==================================================
DT-252 — EXPORT
==================================================

Final path:

outputs/submission_task2a.csv

Use:

index=False

Prefer atomic write:

write candidate temp file
read back
validate
rename to final only on PASS

No intentional rounding unless frozen config explicitly says otherwise.

==================================================
DT-253 — FINAL HARD VALIDATOR
==================================================

Implement:

scripts/validate_task2a_submission.py

Validation only.

Do NOT silently repair the current CSV.

Check:

FILE:
- exists
- readable
- exact official schema
- exact column order
- no accidental index column
- no debug columns

ROW IDs:
- exact official count
- unique
- nonblank
- all official IDs present
- no extra IDs
- official template order preserved

TOTAL:
- numeric
- finite
- no NaN/Inf
- >= 0

CHILLED:
- numeric
- finite
- no NaN/Inf
- >= 0
- <= total

STRUCTURAL RULES:
- every Style chilled = 0.0 exactly
- every Tech chilled = 0.0 exactly

FROZEN CONFIG:
- state FROZEN
- selection_complete true
- one total champion
- one Fresh chilled champion
- Style zero enabled
- Tech zero enabled
- negative clipping enabled
- chilled<=total enabled

RUN MANIFEST:
- model search performed = false
- ensemble weight search performed = false
- future actual demand used = false
- Phase 16 champion IDs unchanged

If any rule fails:

TASK 02A FINAL VALIDATION = FAIL
TASK 02A OUTPUT READY = NO

Do not modify predictions during validation.

==================================================
SYNTHETIC TESTS
==================================================

Create tests covering:

FROZEN CONFIG:
- baseline/model/ensemble champion
- unfrozen rejected
- missing champion rejected
- bad weights rejected
- final postprocessing contract required

TEST GRID:
- row_id uniqueness
- blank ID
- unknown brand
- all rows retained
- row-order marker

HORIZON/CALENDAR:
- horizon 1
- horizon 10
- h0 rejected
- h11 rejected
- cross-year
- ISO week 53
- missing calendar fails

FINAL FIT:
- target week <= final origin
- future target excluded
- no tuning loop
- frozen final iteration used

TOTAL:
- baseline champion
- CatBoost champion
- LightGBM champion
- ensemble champion
- finite outputs
- future-demand mutation invariant
- h10 unaffected by h1 actual

CHILLED:
- Fresh baseline/model/ensemble
- future chilled mutation invariant

STRUCTURAL ZERO:
- Style exact zero
- Tech exact zero

POSTPROCESSING:
- negative total -> 0
- negative chilled -> 0
- positive unchanged
- NaN/Inf rejected
- chilled > total capped
- total never raised

TEMPLATE:
- prediction mapping by row_id
- shuffled internal rows correct
- missing ID fails
- extra ID fails
- duplicate ID fails
- exact columns/order
- debug column fails
- accidental CSV index fails

END TO END:
- run complete synthetic inference twice
- final results equivalent
- current validator passes

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After DT-242–243:
run grid/calendar tests.

After DT-244–245:
run final-fit/prediction/leakage tests.

After DT-246–249:
run postprocessing tests.

After DT-250–253:
run submission tests.

For ordinary failures:

inspect traceback
fix implementation
rerun failing test
rerun Phase 17 tests

At the end run the full Task 2A safe suite, including all existing Phase 11–17 tests.

Then:

pytest -q

python -m pip check

git status

git diff

If a documented test requires real private competition data:

do NOT run it in Codex.

Report the exact local human command.

Ensure none of these are staged:

data/raw/**
data/interim/**
reports/private/**

==================================================
LOCAL FINAL INFERENCE COMMAND
==================================================

Implement but DO NOT execute against restricted real competition data in Codex:

python scripts/run_task2a_final_inference.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --multihorizon-table data/interim/task2a_multihorizon_train.csv \
  --history-config configs/task2a_history.yaml \
  --feature-config configs/task2a_features.yaml \
  --final-model-config configs/task2a_final_models.yaml \
  --inference-config configs/task2a_inference.yaml \
  --output outputs/submission_task2a.csv \
  --report-dir reports/private/phase17_task2a_final

==================================================
LOCAL VALIDATION COMMAND
==================================================

Implement:

python scripts/validate_task2a_submission.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --final-model-config configs/task2a_final_models.yaml \
  --submission outputs/submission_task2a.csv \
  --report-dir reports/private/phase17_task2a_final

==================================================
STOP CONDITIONS
==================================================

STOP if:

- final Task 2A config is not frozen
- Phase 17 starts model search
- test row_id duplicates/missing values exist
- official target week cannot map to horizon 1..10
- target calendar coverage missing
- final training includes future target labels
- future actual demand enters X
- h1 result updates later horizons
- target columns enter X
- frozen champion component missing
- predictions contain NaN/Inf
- Style chilled not exactly zero
- Tech chilled not exactly zero
- final total negative
- final chilled negative
- chilled > total
- row_id changes
- official template mismatch
- extra output column exists
- atomic read-back fails
- Task 1 artifacts change
- private data must be exposed
- safe tests cannot pass without violating approved contracts

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-242 READY
DT-243 READY
DT-244 READY
DT-245 READY
DT-246 READY
DT-247 READY
DT-248 READY
DT-249 READY
DT-250 READY
DT-251 READY
DT-252 READY
DT-253 READY

Phase 16 frozen config reused exactly
no model search
one final origin
horizons exactly 1..10
future calendar official
final training label availability safe
future demand leakage = 0
total predictions complete
Fresh chilled complete
Style chilled zero
Tech chilled zero
nonnegative outputs
chilled <= total
row IDs exact
template exact
final output path correct
validator independent
synthetic tests pass
full safe suite passes
pip check passes
private outputs ignored
Task 1 unchanged
no Phase 18 code added

==================================================
RETURN ONLY
==================================================

PHASE:
17 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-242 READY / FAIL
DT-243 READY / FAIL
DT-244 READY / FAIL
DT-245 READY / FAIL
DT-246 READY / FAIL
DT-247 READY / FAIL
DT-248 READY / FAIL
DT-249 READY / FAIL
DT-250 READY / FAIL
DT-251 READY / FAIL
DT-252 READY / FAIL
DT-253 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

PHASE 16 FROZEN CONFIG:
PASS / FAIL

MODEL SEARCH IN PHASE 17:
MUST BE NO

FINAL FORECAST ORIGIN:
PASS / FAIL

HORIZON 1..10 COVERAGE:
PASS / FAIL

FUTURE CALENDAR FEATURES:
PASS / FAIL

FINAL TRAINING LABEL AVAILABILITY:
PASS / FAIL

FUTURE-DEMAND LEAKAGE AUDIT:
PASS / FAIL

TOTAL FORECAST COVERAGE:
PASS / FAIL

FRESH CHILLED FORECAST COVERAGE:
PASS / FAIL

STYLE CHILLED ZERO:
PASS / FAIL

TECH CHILLED ZERO:
PASS / FAIL

NEGATIVE CLIPPING POLICY:
PASS / FAIL

CHILLED <= TOTAL:
PASS / FAIL

ROW_ID INTEGRITY:
PASS / FAIL

OFFICIAL TEMPLATE:
PASS / FAIL

TASK2A SUBMISSION VALIDATOR:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 17 final-inference command and validation command.

PHASE 17 STATUS:
AWAITING LOCAL TASK2A FINAL INFERENCE

TASK 02A FINAL OUTPUT READY:
NO

READY FOR PHASE 18:
NO

Then STOP.

Do not execute private competition inference.
Do not start Phase 18.
```

---

# 35. Independent Phase 17 review prompt

Use a **fresh Codex session** after the human local Phase 17 run.

```text
Perform an independent review of completed WayLoom Datathon Phase 17.

REVIEW ONLY.

Do NOT:

- reopen model selection
- retrain/reforecast private real data
- access data/raw/**
- access data/interim/**
- access reports/private/**
- modify outputs/submission_task2a.csv initially
- start Phase 18

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md Phase 17
4. PHASE_16_COMPETITION_CONTRACT.md
5. PHASE_17_COMPETITION_CONTRACT.md
6. configs/task2a_final_models.yaml
7. configs/task2a_inference.yaml
8. src/task2a/final_fit.py
9. src/task2a/final_inference.py
10. src/task2a/submission.py
11. scripts/run_task2a_final_inference.py
12. scripts/validate_task2a_submission.py
13. Phase 17 tests
14. .gitignore
15. .cursorignore / equivalent agent ignore rules if present

HUMAN LOCAL RESULT:

LOCAL PHASE 17 TASK2A FINAL INFERENCE: <PASS/FAIL>
FINAL CONFIG FROZEN: <YES/NO>
OFFICIAL TEST ROWS PREDICTED: <YES/NO>
MISSING ROW_ID: <number>
DUPLICATE ROW_ID: <number>
STYLE CHILLED EXACT ZERO: <YES/NO>
TECH CHILLED EXACT ZERO: <YES/NO>
NEGATIVE FINAL TOTAL: <number>
NEGATIVE FINAL CHILLED: <number>
CHILLED > TOTAL: <number>
NaN / INF: <number>
OFFICIAL TEMPLATE: <PASS/FAIL>
TASK 02A FINAL VALIDATION: <PASS/FAIL>
TASK 02A OUTPUT READY: <YES/NO>

Do not ask for private forecast values or row IDs.

==================================================
AUDIT EVERY TASK
==================================================

DT-242:
official test grid loaded safely; row IDs immutable and unique.

DT-243:
future calendar features come from official calendar; horizons map exactly 1..10.

DT-244:
total forecast executes frozen champion only; no model search; no future demand.

DT-245:
Fresh chilled forecast executes frozen chilled champion only.

DT-246:
Style chilled final output exactly zero.

DT-247:
Tech chilled final output exactly zero.

DT-248:
negative clipping is the frozen max(x,0) policy only; no hidden caps/abs/rounding.

DT-249:
chilled is capped downward at total; total is never inflated.

DT-250:
official row_id values are mapped/preserved exactly.

DT-251:
organizer template is structural authority; no debug fields.

DT-252:
atomic export/read-back design exists; correct filename.

DT-253:
independent validator rejects bad current files instead of repairing them.

==================================================
GLOBAL AUDIT
==================================================

Confirm:

- Phase 16 config state FROZEN
- exactly one total champion
- exactly one Fresh chilled champion
- no new model/tuning search in Phase 17
- final training labels known by final origin
- no target columns in inference X
- no future actual demand in inference features
- no recursive use of within-test outcomes
- Style/Tech zeros cannot be overridden
- postprocessing order deterministic
- row_id is final mapping key
- official template column order exact
- private reports ignored
- Task 1 frozen artifacts untouched

Run SAFE synthetic tests only:

pytest -q tests/test_task2a_final_fit.py tests/test_task2a_final_inference.py tests/test_task2a_submission.py

Then run appropriate existing Task 2A regression tests.

Then:

python -m pip check
git status

Do not execute the real private inference command.

==================================================
RETURN
==================================================

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

PHASE 16 CONFIG REUSE: PASS / FAIL
NO MODEL SEARCH: PASS / FAIL
FINAL ORIGIN/HORIZON CONTRACT: PASS / FAIL
FUTURE CALENDAR CONTRACT: PASS / FAIL
FINAL TRAINING LEAKAGE: PASS / FAIL
TOTAL FORECAST PIPELINE: PASS / FAIL
FRESH CHILLED PIPELINE: PASS / FAIL
STYLE ZERO RULE: PASS / FAIL
TECH ZERO RULE: PASS / FAIL
NEGATIVE CLIPPING: PASS / FAIL
CHILLED<=TOTAL: PASS / FAIL
ROW_ID INTEGRITY: PASS / FAIL
OFFICIAL TEMPLATE: PASS / FAIL
SUBMISSION VALIDATOR: PASS / FAIL
SYNTHETIC TESTS: PASS / FAIL
HUMAN LOCAL FINAL RUN: PASS / FAIL
DATA SAFETY: PASS / FAIL

DT-242: PASS/FAIL
DT-243: PASS/FAIL
DT-244: PASS/FAIL
DT-245: PASS/FAIL
DT-246: PASS/FAIL
DT-247: PASS/FAIL
DT-248: PASS/FAIL
DT-249: PASS/FAIL
DT-250: PASS/FAIL
DT-251: PASS/FAIL
DT-252: PASS/FAIL
DT-253: PASS/FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

PHASE 17 REVIEW:
PASS / FAIL

TASK 02A FINAL OUTPUT READY:
YES / NO

READY FOR PHASE 18:
YES / NO

If FAIL:
list exact blockers only.

Do not fix automatically.
Do not start Phase 18.
```

---

# 36. Completion record template

```markdown
# Phase 17 Completion Record

## Tasks

- [ ] DT-242
- [ ] DT-243
- [ ] DT-244
- [ ] DT-245
- [ ] DT-246
- [ ] DT-247
- [ ] DT-248
- [ ] DT-249
- [ ] DT-250
- [ ] DT-251
- [ ] DT-252
- [ ] DT-253

## Frozen configuration

- Phase 16 final config frozen: YES / NO
- Exactly one total champion: YES / NO
- Exactly one Fresh chilled champion: YES / NO
- Phase 17 model search performed: NO / YES

## Future grid

- Official rows retained: YES / NO
- row_id unique: YES / NO
- Final forecast origin valid: YES / NO
- Horizon 1..10 coverage: PASS / FAIL
- Future calendar coverage: PASS / FAIL

## Predictions

- Total coverage: PASS / FAIL
- Fresh chilled coverage: PASS / FAIL
- Style chilled exact zero: PASS / FAIL
- Tech chilled exact zero: PASS / FAIL
- Final total nonnegative: PASS / FAIL
- Final chilled nonnegative: PASS / FAIL
- Chilled <= total: PASS / FAIL
- NaN / Inf: 0 / nonzero

## Submission

- Official row IDs preserved: PASS / FAIL
- Official template exact: PASS / FAIL
- outputs/submission_task2a.csv exists: YES / NO
- Read-back validator: PASS / FAIL

## Safety / regression

- Future actual demand used: NO / YES
- Task 1 changed: NO / YES
- Synthetic tests: PASS / FAIL
- Full safe tests: PASS / FAIL
- pip check: PASS / FAIL
- Independent review: PASS / FAIL

## Verdict

PHASE 17 STATUS: PASS / FAIL
TASK 02A FINAL OUTPUT READY: YES / NO
READY FOR PHASE 18: YES / NO
```

---

# 37. Final Phase 17 checklist

Before Phase 18:

- [ ] Phase 16 has passed.
- [ ] `configs/task2a_final_models.yaml` is `FROZEN`.
- [ ] Exactly one total champion exists.
- [ ] Exactly one Fresh chilled champion exists.
- [ ] No model search occurred in Phase 17.
- [ ] Official Task 2A test rows were loaded without dropping rows.
- [ ] Every official `row_id` is unchanged.
- [ ] One canonical final forecast origin is used.
- [ ] All official future target weeks map to horizons 1..10.
- [ ] Future calendar features come only from official calendar data.
- [ ] Final model training uses only historically known labels.
- [ ] No future actual demand enters forecast features.
- [ ] Total forecast covers every official row.
- [ ] Fresh chilled forecast covers every Fresh row.
- [ ] Style chilled is exactly zero.
- [ ] Tech chilled is exactly zero.
- [ ] Negative forecasts are clipped only by the frozen rule.
- [ ] Every final forecast is nonnegative.
- [ ] Every final chilled forecast is <= total.
- [ ] Predictions are mapped by `row_id`.
- [ ] Official template is used as structural authority.
- [ ] No debug columns are present.
- [ ] `outputs/submission_task2a.csv` exists.
- [ ] Final CSV read-back passes.
- [ ] Hard Task 2A validator passes.
- [ ] Synthetic Phase 17 tests pass.
- [ ] Full safe regression suite passes.
- [ ] `python -m pip check` passes.
- [ ] Private outputs remain ignored.
- [ ] Task 1 output/artifacts remain unchanged.
- [ ] Independent Phase 17 review passes.

Only then:

```text
PHASE 17 STATUS: PASS
TASK 02A FINAL OUTPUT READY: YES
READY FOR PHASE 18: YES
```

Do not begin Task 2B until this gate is green.
