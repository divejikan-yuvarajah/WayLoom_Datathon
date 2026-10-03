# PHASE 11 — Task 2A Demand-History Construction

> **Canonical filename:** `PHASE_11_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom — Rootcode Tech-Triathlon 2026 Datathon  
> **Task range:** **DT-174 → DT-191**  
> **Task count:** **18**  
> **Master-plan phase name:** **Phase 11 — Task 2A demand-history construction**  
> **Phase dependency:** Phases 02–03  
> **Default phase priority:** P0  
> **Phase gate:** The Task 2A weekly panel counts every unique requested order correctly and preserves Fresh chilled logic.  
> **Agent environment:** OpenAI Codex in VS Code (Cursor wording in earlier phases should now be interpreted as generic coding-agent guidance).  
> **Recommended economical model:** **GPT-6 Luna, medium reasoning** if available; otherwise **GPT-5.6 Luna high** or **GPT-5.6 Terra medium**. Escalate to a stronger model only if the weekly-panel/missing-week logic produces a genuine blocker.

---

# 1. Phase purpose

Phase 11 creates the canonical historical demand table for **Task 2A — ten-week depot demand forecasting**.

This phase is not forecasting yet. It answers a more fundamental question:

> **What volume did stores request, by depot + brand + official ISO week, after counting every unique order exactly once?**

The output of this phase becomes the source of truth for:

- Phase 12 Task 2A exploratory analysis;
- Phase 13 forecasting features;
- Phase 14 rolling-origin validation;
- Phase 15 baselines;
- Phase 16 advanced forecasting;
- Phase 17 final Task 2A inference;
- the final notebook and preprocessing documentation.

A demand-history mistake here can invalidate every later Task 2A score. Therefore Phase 11 must prefer explicit reconciliation and hard assertions over convenient aggregation.

---

# 2. Official Task 2A contract

The official challenge requires a **10-week forecast** for every supplied depot + brand + future week combination.

Final Task 2A outputs are:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

The official history rules that directly constrain this phase are:

1. Build demand history from **both**:

   ```text
   deliveries_train.csv
   task1_test_inputs.csv
   ```

2. In both files, each row is one order identified by `delivery_id`.
3. Count **every order once**, including orders that were deferred or never dispatched.
4. Assign demand to the week of the requested `order_date`, **not** the later `dispatch_date`.
5. Join `calendar.csv` and use its official `iso_year` and `iso_week`.
6. Only **Fresh** has chilled demand.
7. Style chilled demand is logically zero.
8. Tech chilled demand is logically zero.
9. Task 2A forecasts **volume**, not vehicle counts or driver counts.

The order-record schema defines:

```text
delivery_id
order_date
dispatch_date
dispatch_status
outlet_id
brand
district
depot
temp_requirement
order_units
order_weight_kg
order_volume_m3
...
```

The official dispatch statuses are:

```text
attempted  → dispatched on order_date
deferred   → dispatched later because fleet capacity was short
not_run    → never dispatched
```

For Task 2A, all three still represent requested demand.

---

# 3. Source authority and non-negotiable precedence

When implementation details conflict, use:

1. Official Challenge Booklet.
2. Official supplied CSVs/templates.
3. `WAYLOOM_DATATHON_MASTER_PLAN.md`.
4. Approved phase contracts.
5. Existing tested project code.
6. `CODEX_HANDOFF_PHASE_11_ONWARDS.md` / `AGENTS.md`.
7. Engineering assumptions in this document.

Do not silently replace an official rule with a modelling convenience.

Engineering decisions in this contract are explicitly identified as such.

---

# 4. Phase 11 master task registry

This task list is copied from the finalized WayLoom master inventory.

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-174** | [O] | P0 | Phases 2–3 | Load `deliveries_train.csv` |
| [ ] | **DT-175** | [O] | P0 | Phases 2–3 | Load `task1_test_inputs.csv` |
| [ ] | **DT-176** | [O] | P0 | DT-174–DT-175 | Append both demand datasets |
| [ ] | **DT-177** | [O] | P0 | Phases 2–3 | Verify `delivery_id` uniqueness after combination |
| [ ] | **DT-178** | [O] | P0 | Phases 2–3 | Keep attempted orders |
| [ ] | **DT-179** | [O] | P0 | Phases 2–3 | Keep deferred orders |
| [ ] | **DT-180** | [O] | P0 | Phases 2–3 | Keep `not_run` orders |
| [ ] | **DT-181** | [O] | P0 | Phases 2–3 | Use requested `order_date` |
| [ ] | **DT-182** | [O] | P0 | DT-176–DT-181 | Join `calendar.csv` |
| [ ] | **DT-183** | [O] | P0 | Phases 2–3 | Add ISO year |
| [ ] | **DT-184** | [O] | P0 | Phases 2–3 | Add ISO week |
| [ ] | **DT-185** | [O] | P0 | DT-182–DT-184 | Aggregate total demand |
| [ ] | **DT-186** | [O] | P0 | DT-182–DT-184 | Aggregate Fresh chilled demand separately |
| [ ] | **DT-187** | [O] | P0 | Phases 2–3 | Force Style chilled history logically to zero |
| [ ] | **DT-188** | [O] | P0 | Phases 2–3 | Force Tech chilled history logically to zero |
| [ ] | **DT-189** | [O] | P0 | DT-185–DT-188 | Build complete weekly panel |
| [ ] | **DT-190** | [O] | P0 | Phases 2–3 | Investigate missing weeks |
| [ ] | **DT-191** | [O] | P0 | Phases 2–3 | Validate weekly totals |

**Phase complete:** [ ]  
**READY FOR PHASE 12:** NO

---

# 5. Phase execution strategy

Phase 11 should be implemented in small audited batches because demand-accounting errors can be silent.

Recommended checkpoints:

```text
Checkpoint A — DT-174 → DT-177
Load + append + unique-order proof

Checkpoint B — DT-178 → DT-181
Demand inclusion + requested-date semantics

Checkpoint C — DT-182 → DT-184
Official calendar mapping

Checkpoint D — DT-185 → DT-188
Weekly total/chilled target construction

Checkpoint E — DT-189 → DT-190
Complete panel + missing-week investigation

Checkpoint F — DT-191
Full reconciliation and freeze
```

Codex may autonomously implement and test all safe code, but it must not inspect restricted competition rows in agent context.

The human operator runs the real-data build locally after the synthetic test suite passes.

---

# 6. Data-safety boundary

Follow the repository `AGENTS.md` and Codex handoff rules.

## Codex may access

```text
src/**
tests/**
scripts/**
configs/**
docs/**
requirements files
tracked phase contracts
synthetic fixtures
Git status/diff
```

## Codex must not inspect or print row-level content from

```text
data/raw/**
data/interim/**
reports/private/**
```

Do not paste real `delivery_id`, private row-level order values, private weekly volumes, or private report tables into the coding-agent chat.

The human operator executes real competition-data commands locally and returns only sanitized PASS/FAIL status.

---

# 7. Frozen Task 1 boundary

Phases 00–10 are complete and Task 1 has passed final revalidation.

Treat as frozen:

```text
configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv
```

Phase 11 may read shared tracked utilities if useful, but must not:

- retrain Task 1;
- change Task 1 models;
- alter `submission_task1.csv`;
- reopen Task 1 feature/model selection;
- use Task 1 predictions as Task 2A demand history.

Important distinction:

```text
task1_test_inputs.csv
```

is used in Phase 11 because the **official Task 2A rule explicitly requires its order records as demand history**. That does not reopen Task 1 modelling.

---

# 8. Canonical Phase 11 data grain

## 8.1 Combined order-level demand history grain

One row per unique:

```text
delivery_id
```

Required lineage columns should include at least:

```text
delivery_id
source_file
order_date
dispatch_date
dispatch_status
brand
depot
temp_requirement
order_volume_m3
iso_year
iso_week
```

Additional original order fields may be retained privately for later diagnostics, but aggregation must not duplicate an order.

## 8.2 Weekly observed grain

One row per observed:

```text
depot
brand
iso_year
iso_week
```

with at least:

```text
total_volume_m3
chilled_volume_m3
order_count
chilled_order_count
```

Diagnostic counts by status are recommended:

```text
attempted_order_count
deferred_order_count
not_run_order_count
```

## 8.3 Complete weekly panel grain

One row per validated historical:

```text
depot
brand
iso_year
iso_week
```

including weeks with confirmed zero demand after missing-week investigation.

Recommended calendar metadata:

```text
week_start_date
week_end_date
calendar_days
operating_days
is_complete_calendar_week
is_confirmed_zero_demand
panel_status
```

Do not allow an ambiguous missing week to silently become zero.

---

# 9. Required tracked files

Create or update:

```text
src/task2a/__init__.py
src/task2a/history.py

scripts/build_task2a_history.py

configs/task2a_history.yaml

docs/task2a_history_spec.md

tests/test_task2a_history.py
```

Reuse common utilities where appropriate:

```text
src/common/io.py
src/common/validation.py
src/common/data_inventory.py
src/common/data_quality.py
src/common/schema_assertions.py
```

Do not duplicate a mature loader/schema utility just because Phase 11 starts a new task family.

---

# 10. Required private local outputs

Recommended outputs:

```text
data/interim/task2a_demand_orders.csv
data/interim/task2a_weekly_observed.csv
data/interim/task2a_weekly_panel.csv
```

Private reports:

```text
reports/private/phase11_task2a_history/
├── build_summary.json
├── source_reconciliation.json
├── delivery_id_uniqueness.json
├── dispatch_status_retention.json
├── calendar_join_validation.json
├── chilled_logic_validation.json
├── missing_weeks.json
├── weekly_reconciliation.json
└── phase11_history_report.md
```

All competition-derived outputs remain private/ignored.

---

# 11. Recommended `configs/task2a_history.yaml`

This configuration is a WayLoom engineering decision, not an organizer-provided file.

```yaml
version: 1

official_sources:
  deliveries_train: deliveries_train.csv
  task1_test_inputs: task1_test_inputs.csv
  calendar: calendar.csv

order_key: delivery_id
requested_date_column: order_date
volume_column: order_volume_m3

required_dispatch_statuses:
  - attempted
  - deferred
  - not_run

series_keys:
  - depot
  - brand

week_keys:
  - iso_year
  - iso_week

chilled:
  eligible_brand: Fresh
  chilled_temp_value: chilled
  nonfresh_brands:
    - Style
    - Tech
  strict_nonfresh_chilled_input_check: true

calendar:
  join_key: order_date
  calendar_date_column: date
  use_calendar_iso_fields_as_source_of_truth: true
  require_unique_calendar_date: true
  require_all_order_dates_matched: true

panel:
  build_calendar_week_spine: true
  require_missing_week_investigation: true
  zero_fill_only_confirmed_gaps: true
  flag_boundary_partial_weeks: true
  unresolved_gap_is_blocker: true

validation:
  require_unique_combined_delivery_id: true
  require_nonnegative_volume: true
  require_finite_volume: true
  require_chilled_le_total: true
  require_style_chilled_zero: true
  require_tech_chilled_zero: true
  require_weekly_total_reconciliation: true

private_output_dir: reports/private/phase11_task2a_history
```

Do not add data-dependent thresholds after seeing private results unless they are documented as a deliberate engineering decision and do not alter the official accounting rules.

---

# 12. Recommended implementation API

`src/task2a/history.py` should be deterministic and testable with synthetic DataFrames.

Recommended functions:

```python
validate_order_history_schema(...)
load_task2a_demand_sources(...)
append_demand_sources(...)
validate_combined_delivery_ids(...)
validate_dispatch_status_retention(...)
assign_requested_demand_date(...)
join_official_calendar(...)
build_calendar_week_spine(...)
aggregate_weekly_total_demand(...)
aggregate_weekly_chilled_demand(...)
combine_weekly_targets(...)
build_complete_weekly_panel(...)
classify_missing_weeks(...)
validate_weekly_panel(...)
build_task2a_history(...)
```

Prefer one canonical orchestration function:

```python
build_task2a_history(...)
```

that returns structured outputs rather than mixing loading, validation and writing in one large function.

---

# 13. Detailed task specifications

## DT-174 — Load `deliveries_train.csv`

**Mark:** [O]  
**Priority:** P0

### Objective

Load the historical order records required for Task 2A.

### Required fields

At minimum validate presence of:

```text
delivery_id
order_date
dispatch_date
dispatch_status
brand
depot
temp_requirement
order_volume_m3
```

Retain the original `delivery_id` exactly.

### Critical rules

- One row represents one order.
- Do not prefilter to dispatched orders.
- Do not require `route_id` to be nonblank.
- Do not require `dispatch_date` to be present.
- `not_run` orders are legitimate demand rows.

### Output

Private in-memory/order table tagged with:

```text
source_file = deliveries_train
```

### Tests

Synthetic:

- valid schema loads;
- missing `delivery_id` fails;
- missing `order_date` fails;
- missing `order_volume_m3` fails;
- `not_run` with blank dispatch/route fields remains valid for Task 2A.

### STOP

Stop if the source schema contradicts the official order-record contract in a material way not already resolved by Phase 03.

---

## DT-175 — Load `task1_test_inputs.csv`

**Mark:** [O]  
**Priority:** P0

### Objective

Load the later Task 1 order records because the official Task 2A history rule explicitly requires them.

### Critical distinction

This file is **not** being used for Task 1 modelling here.

Use only its order-record demand fields.

Do not join `route_legs_test.csv` for Task 2A demand history.

### Required fields

Same demand fields as DT-174:

```text
delivery_id
order_date
dispatch_status
brand
depot
temp_requirement
order_volume_m3
```

`task1_test_inputs.csv` is documented as containing dispatched Task 1 orders, but Phase 11 should still validate the fields rather than infer demand from route-leg existence.

### Output

Private in-memory/order table tagged:

```text
source_file = task1_test_inputs
```

### Tests

- valid schema loads;
- Task 1 prediction columns are irrelevant/not required;
- no Task 1 model output is required;
- no route-leg join occurs.

---

## DT-176 — Append both demand datasets

**Mark:** [O]  
**Priority:** P0

### Objective

Create the official combined order-demand universe from both required sources.

### Correct operation

Use row-wise append/concatenation with aligned order-record semantics.

Conceptually:

```python
combined = pd.concat(
    [deliveries_train_orders, task1_test_orders],
    axis=0,
    ignore_index=True,
    sort=False,
)
```

### Do not

- merge sources horizontally;
- join on outlet;
- aggregate before uniqueness validation;
- call `drop_duplicates()` as a convenient cleanup;
- discard rows missing route information;
- discard `not_run`.

### Required lineage

Keep:

```text
source_file
```

so every order can be traced to its required source without exposing it publicly.

### Reconciliation

Before any calendar join:

```text
combined row count
=
deliveries_train row count
+
task1_test_inputs row count
```

provided each source is loaded at one-row-per-order grain.

### Tests

- append preserves all rows;
- source tag preserved;
- columns aligned;
- no accidental index column used as identifier;
- input frames not mutated.

---

## DT-177 — Verify `delivery_id` uniqueness after combination

**Mark:** [O]  
**Priority:** P0  
**CRITICAL GATE**

### Objective

Prove that every requested order contributes exactly once.

### Required validations

Check:

```text
null delivery_id count = 0
blank delivery_id count = 0
duplicate delivery_id count = 0
```

Also validate uniqueness within each source and after append.

### Critical policy

If the same `delivery_id` appears in both sources:

```text
STOP
```

Do not automatically choose one source.

Do not `drop_duplicates()`.

The official rule says every unique order once; silent deduplication can hide a source-boundary defect.

### Private report

Recommended:

```text
delivery_id_uniqueness.json
```

Sanitized console output must not print actual duplicate IDs.

### Tests

- unique IDs pass;
- duplicate inside first source fails;
- duplicate inside second source fails;
- duplicate across sources fails;
- null/blank IDs fail.

---

## DT-178 — Keep attempted orders

**Mark:** [O]  
**Priority:** P0

### Objective

Confirm `attempted` orders remain in Task 2A history.

Official meaning:

```text
attempted = dispatched on order_date
```

These clearly represent requested demand and must count once.

### Required test

Synthetic attempted order volume must appear in its requested ISO week total.

### Do not

Filter orders based on successful/failed operational outcome beyond the official demand-accounting rule.

---

## DT-179 — Keep deferred orders

**Mark:** [O]  
**Priority:** P0

### Objective

Ensure deferred demand is counted in the week it was originally requested.

Official meaning:

```text
deferred = dispatched later because fleet capacity was short
```

### Critical example

If an order is requested in week 38 but dispatched in week 39:

```text
Task 2A demand week = week 38
```

not week 39.

### Required synthetic test

Create:

```text
order_date    → ISO week A
dispatch_date → ISO week B
status        → deferred
```

Assert the volume appears only in week A demand.

---

## DT-180 — Keep `not_run` orders

**Mark:** [O]  
**Priority:** P0

### Objective

Count never-dispatched orders because they still represent requested demand.

Official meaning:

```text
not_run = never dispatched
```

### Critical rule

A valid Task 2A `not_run` row may have blank:

```text
dispatch_date
route_id
seq_in_route
vehicle_id
```

Those blanks must not cause the order to be dropped.

### Required synthetic test

A `not_run` order with no route/vehicle fields contributes its full `order_volume_m3` to the requested week.

---

## DT-181 — Use requested `order_date`

**Mark:** [O]  
**Priority:** P0  
**CRITICAL GATE**

### Objective

Freeze the canonical Task 2A demand date as:

```text
order_date
```

### Forbidden substitutes

Do not aggregate demand by:

```text
dispatch_date
route date
actual arrival date
Task 1 route date
file source period alone
```

### Date parsing

Use strict date parsing.

Required:

```text
order_date non-null
order_date valid
```

If invalid/missing dates exist after Phase 03, stop rather than silently imputing a week.

### Optional consistency diagnostic

For `attempted`, dispatch date is expected by definition to be the order date. A mismatch may be reported privately as a data-quality inconsistency, but the Task 2A requested-date rule still uses `order_date`.

### Tests

- deferred order counted by `order_date`;
- not-run order needs no dispatch date;
- invalid order date fails;
- aggregation code never reads dispatch date as the grouping date.

---

## DT-182 — Join `calendar.csv`

**Mark:** [O]  
**Priority:** P0  
**CRITICAL GATE**

### Objective

Attach official calendar context to every requested order via `order_date`.

### Official join

Conceptually:

```text
combined.order_date
↔
calendar.date
```

### Required cardinality

Calendar must have one row per date.

Validate:

```text
calendar.date unique
```

Then use a left join from combined demand orders to calendar.

Recommended:

```python
combined.merge(
    calendar,
    how="left",
    left_on="order_date",
    right_on="date",
    validate="many_to_one",
    indicator=True,
)
```

### Required assertions

```text
joined row count == combined row count
all order rows matched calendar
no order duplication after join
```

### Do not

- inner join first and hide unmatched dates;
- calculate ISO week independently as a replacement for missing calendar rows;
- duplicate demand because of duplicate calendar dates.

### Tests

- all matched pass;
- missing calendar date fails;
- duplicate calendar date fails;
- row count preserved.

---

## DT-183 — Add ISO year

**Mark:** [O]  
**Priority:** P0

### Objective

Use:

```text
calendar.iso_year
```

as the official Task 2A year grouping field.

### Critical rule

Do not use plain calendar year (`order_date.year`) as a substitute near ISO year boundaries.

An early-January date may belong to the previous ISO year; a late-December date may belong to the next ISO year.

### Engineering cross-check

It is acceptable to compute Python ISO calendar values as a validation cross-check, but the official `calendar.csv` fields remain source of truth.

### Tests

Synthetic year-boundary calendar mapping where calendar year and ISO year differ.

---

## DT-184 — Add ISO week

**Mark:** [O]  
**Priority:** P0

### Objective

Use:

```text
calendar.iso_week
```

as the official weekly grouping field.

### Required validation

Ensure ISO week is integer-like and in a valid official domain.

Do not build a key from week number alone; always pair:

```text
iso_year + iso_week
```

### Recommended derived engineering fields

For sorting/reporting only:

```text
iso_year_week
week_start_date
week_end_date
```

The model target grain remains separate `iso_year`, `iso_week` columns.

### Tests

- same week number in different years remains separate;
- week 1 after week 52/53 sorts chronologically using week metadata, not string mistakes.

---

## DT-185 — Aggregate total demand

**Mark:** [O]  
**Priority:** P0

### Objective

Compute total requested volume by:

```text
depot
brand
iso_year
iso_week
```

### Canonical target

```text
total_volume_m3 = sum(order_volume_m3)
```

### Required input validation

Before aggregation:

```text
order_volume_m3 numeric
order_volume_m3 finite
order_volume_m3 >= 0
```

Do not round source volumes before summing.

### Recommended diagnostic fields

```text
order_count
attempted_order_count
deferred_order_count
not_run_order_count
```

These diagnostics help prove that deferred/not-run demand was retained.

### Reconciliation

For all included orders:

```text
sum(weekly total_volume_m3)
==
sum(combined order_volume_m3)
```

within a tight floating-point tolerance.

Also:

```text
sum(weekly order_count)
==
combined row count
```

### Tests

- known group sums;
- groups separated by depot;
- groups separated by brand;
- groups separated by ISO year/week;
- zero volume valid if official data permits;
- negative/nonfinite volume rejected.

---

## DT-186 — Aggregate Fresh chilled demand separately

**Mark:** [O]  
**Priority:** P0

### Objective

Construct the historical chilled portion of Task 2A demand.

### WayLoom calculation grounded in the official schema

An order contributes to historical chilled volume when:

```text
brand == "Fresh"
AND
temp_requirement == "chilled"
```

Then:

```text
chilled_volume_m3 = sum(order_volume_m3)
```

for that depot + Fresh + ISO year/week.

Fresh ambient orders contribute to `total_volume_m3` but not to `chilled_volume_m3`.

### Required invariants

For every Fresh week:

```text
0 <= chilled_volume_m3 <= total_volume_m3
```

### Recommended diagnostic

```text
chilled_order_count
```

### Tests

- Fresh chilled counted;
- Fresh ambient excluded from chilled but included total;
- mixed Fresh ambient/chilled correct;
- chilled cannot exceed total.

---

## DT-187 — Force Style chilled history logically to zero

**Mark:** [O]  
**Priority:** P0

### Objective

Apply the official rule:

```text
Style chilled demand = 0
```

for every historical panel row.

### Critical distinction

Do not estimate chilled Style demand from `temp_requirement` or any vehicle data.

### Data-quality contradiction handling

If a raw Style order is unexpectedly marked:

```text
temp_requirement == chilled
```

then:

- the Task 2A historical chilled target still remains zero because only Fresh has chilled demand;
- record a private inconsistency warning/blocker according to strict config;
- do not silently redefine the official rule.

Default strict behavior in this contract:

```text
STOP for review if non-Fresh chilled source records exist
```

because this would contradict the official brand/chilled semantics and should be consciously resolved.

### Tests

- Style weekly chilled exactly numeric `0.0`;
- not NaN;
- not tiny floating residue.

---

## DT-188 — Force Tech chilled history logically to zero

**Mark:** [O]  
**Priority:** P0

Same contract as DT-187:

```text
Tech chilled demand = exactly 0
```

No chilled estimation for Tech.

If a Tech source order is marked chilled, flag it under the strict non-Fresh chilled consistency rule rather than changing the official target definition.

### Tests

- Tech chilled exactly `0.0`;
- no NaN;
- no floating residue.

---

## DT-189 — Build complete weekly panel

**Mark:** [O]  
**Priority:** P0  
**CRITICAL GATE**

### Objective

Create a continuous, auditable historical weekly series for every Task 2A series.

Canonical series key:

```text
depot + brand
```

Canonical time key:

```text
iso_year + iso_week
```

### Required series universe

Use official observed/reference depot and brand semantics.

Expected brands:

```text
Fresh
Style
Tech
```

Expected depots:

```text
Peliyagoda
Kandy
```

Do not hard-code a Cartesian product without validating that the source/reference contract supports it. Build/validate the intended series universe explicitly.

### Calendar week spine

Construct week metadata from `calendar.csv`, not from order rows alone.

Recommended grouped week spine:

```text
iso_year
iso_week
week_start_date
week_end_date
calendar_days
operating_days
```

where:

```text
operating_days = sum(calendar.is_operating)
```

### Panel construction

Conceptually:

```text
series universe
×
validated historical week spine
```

left-join observed weekly demand.

### Missing target cells

Do not immediately execute:

```python
fillna(0)
```

for every missing aggregate.

Missing cells must first be classified by DT-190.

### Recommended panel status values

```text
OBSERVED_DEMAND
CONFIRMED_ZERO
BOUNDARY_PARTIAL
CALENDAR_INCOMPLETE
UNRESOLVED_GAP
```

Only confirmed zero-demand weeks should receive zero target values automatically.

### Cardinality check

After final gap resolution:

```text
panel rows
=
validated series count
×
validated week count
```

if a common week spine is intentionally used.

If series-specific coverage is deliberately used instead, document and test its exact cardinality contract.

### Tests

- missing interior series/week appears in panel;
- observed rows preserved;
- no duplicate series/week key;
- series × week cardinality correct;
- no blind zero-fill.

---

## DT-190 — Investigate missing weeks

**Mark:** [O]  
**Priority:** P0  
**CRITICAL GATE**

### Objective

Determine whether a missing weekly aggregate means true zero requested demand or incomplete/ambiguous historical coverage.

The internal WayLoom plan explicitly warns not to equate absent rows with zero without checking.

### Required analysis

For every missing series/week cell, inspect only derived metadata locally:

```text
calendar coverage
week position relative to source history boundaries
operating_days
whether other series have demand in the same week
source coverage from both required order files
```

Do not expose private weekly volumes to Codex chat.

### Recommended classification logic

Engineering policy:

#### `CONFIRMED_ZERO`

A candidate only when:

- the week is within validated source coverage;
- official calendar coverage is complete enough for that week;
- the series is expected to exist;
- there is no source/data-quality sign of missing records;
- absence therefore represents no requested orders for that series/week.

#### `BOUNDARY_PARTIAL`

First/last historical week where source coverage may begin/end mid-week or cannot be proven complete.

#### `CALENDAR_INCOMPLETE`

Calendar does not provide required dates/metadata for the expected week.

#### `UNRESOLVED_GAP`

Cannot confidently distinguish zero demand from missing history.

### Default policy

```text
UNRESOLVED_GAP => STOP
CALENDAR_INCOMPLETE => STOP
BOUNDARY_PARTIAL => exclude from full-week modelling panel or resolve explicitly; do not silently zero
CONFIRMED_ZERO => zero-fill total/chilled/order counts
```

The exact boundary handling must be documented in `docs/task2a_history_spec.md` and remain stable for Phases 12–17.

### Important

Do not use future Task 2A test targets to decide historical missing-week semantics.

### Private output

```text
missing_weeks.json
```

The console should report only counts/statuses, not private series values.

### Tests

Synthetic cases for:

- confirmed zero interior week;
- incomplete calendar week;
- first/last boundary partial week;
- unresolved gap blocker;
- other-series activity does not by itself override calendar/source coverage checks.

---

## DT-191 — Validate weekly totals

**Mark:** [O]  
**Priority:** P0  
**FINAL PHASE GATE**

### Objective

Prove that the Phase 11 panel is a faithful transformation of the official order records.

### Required invariants

#### Order identity

```text
combined delivery_id unique
```

#### Source accounting

```text
combined row count
=
source A rows + source B rows
```

with no silent deduplication/drop.

#### Status retention

Every official order contributes once regardless of:

```text
attempted
deferred
not_run
```

#### Requested-date rule

Every weekly assignment uses:

```text
order_date → calendar.date → calendar.iso_year + calendar.iso_week
```

#### Calendar join

```text
unmatched order dates = 0
calendar duplicate dates = 0
row multiplication = 0
```

#### Total volume reconciliation

For the validated historical coverage:

```text
sum(order-level order_volume_m3)
≈
sum(weekly panel total_volume_m3)
```

Use a tight floating tolerance; do not round to force equality.

#### Order-count reconciliation

```text
combined order count
=
sum(panel order_count)
```

for rows/weeks included in the validated panel coverage.

If boundary partial weeks are explicitly excluded from the modelling panel, reconciliation must separately account for the excluded orders so no demand disappears silently.

#### Chilled logic

```text
Fresh:
0 <= chilled_volume_m3 <= total_volume_m3

Style:
chilled_volume_m3 == 0 exactly

Tech:
chilled_volume_m3 == 0 exactly
```

#### Panel uniqueness

Unique:

```text
depot + brand + iso_year + iso_week
```

#### Numeric validity

```text
total_volume_m3 finite and >= 0
chilled_volume_m3 finite and >= 0
```

#### Gap resolution

```text
UNRESOLVED_GAP count = 0
CALENDAR_INCOMPLETE unresolved count = 0
```

### Private report

Generate:

```text
weekly_reconciliation.json
phase11_history_report.md
```

### Final status

Only after every invariant passes:

```text
PHASE 11 STATUS: PASS
READY FOR PHASE 12: YES
```

---

# 14. Full input contract

## Official competition inputs used in this phase

```text
Training Data/deliveries_train.csv
Test Data/task1_test_inputs.csv
General Data/calendar.csv
```

No route-leg file is required for Task 2A demand-history construction.

## Shared tracked project inputs

```text
configs/dataset_manifest.yaml
configs/data_quality_rules.yaml
AGENTS.md
CODEX_HANDOFF_PHASE_11_ONWARDS.md
WAYLOOM_DATATHON_MASTER_PLAN.md
approved Phase 02/03 contracts and utilities
```

Task 1 saved models/predictions are not inputs to Task 2A history.

---

# 15. Full output contract

## Private order-level history

Recommended columns:

```text
delivery_id
source_file
order_date
dispatch_date
dispatch_status
brand
depot
temp_requirement
order_volume_m3
iso_year
iso_week
```

## Private observed weekly aggregate

Recommended columns:

```text
depot
brand
iso_year
iso_week
total_volume_m3
chilled_volume_m3
order_count
chilled_order_count
attempted_order_count
deferred_order_count
not_run_order_count
```

## Private complete weekly panel

Recommended columns:

```text
depot
brand
iso_year
iso_week
week_start_date
week_end_date
calendar_days
operating_days
total_volume_m3
chilled_volume_m3
order_count
chilled_order_count
panel_status
is_confirmed_zero_demand
```

Later phases may add forecasting features. Phase 11 should keep the historical target panel clean and minimally derived.

---

# 16. Detailed validation helpers

Recommended hard assertion helpers:

```python
assert_unique_nonblank_delivery_id(...)
assert_expected_dispatch_status_domain(...)
assert_finite_nonnegative_volume(...)
assert_calendar_date_unique(...)
assert_calendar_join_complete(...)
assert_unique_weekly_key(...)
assert_nonfresh_chilled_zero(...)
assert_chilled_le_total(...)
assert_weekly_volume_reconciliation(...)
assert_weekly_order_count_reconciliation(...)
assert_no_unresolved_panel_gaps(...)
```

Prefer explicit exception messages containing aggregate counts only.

Avoid dumping private rows into exceptions or logs.

---

# 17. Missing-week engineering policy in more detail

This is the most nuanced part of Phase 11 and is **not fully prescribed by the booklet**.

The official sources tell us to count orders by requested ISO week. The WayLoom plan recommends a complete weekly calendar but warns against blindly treating absent rows as zero.

Therefore the implementation should separate:

```text
OBSERVED aggregate
```

from:

```text
PANEL completion decision
```

## Safe procedure

1. Aggregate actual observed orders first.
2. Build official week spine from `calendar.csv`.
3. Create candidate series/week grid.
4. Mark absent aggregate cells as `MISSING_PENDING_REVIEW`.
5. Classify with deterministic coverage rules.
6. Zero-fill only `CONFIRMED_ZERO`.
7. Leave ambiguous boundary/incomplete gaps flagged.
8. Fail Phase 11 if unresolved gaps remain.
9. Freeze the policy in config/docs before Phase 12.

This allows later forecasting to distinguish true zeros from absent records and avoids inventing demand history.

---

# 18. Important edge cases

## 18.1 Duplicate `delivery_id` across required sources

Hard failure. No automatic dedupe.

## 18.2 Deferred order crosses ISO week/year

Count only in requested `order_date` week from official calendar.

## 18.3 `not_run` has no dispatch/route/vehicle

Still count the order.

## 18.4 `order_date` at ISO-year boundary

Use `calendar.iso_year` + `calendar.iso_week`, not calendar year/week arithmetic.

## 18.5 ISO week 53

Support if present in official calendar. Do not assume 52 weeks every year.

## 18.6 Same `iso_week` in different years

Never combine them.

## 18.7 Missing `order_volume_m3`

Do not silently treat as zero. Stop/data-quality review.

## 18.8 Negative/nonfinite volume

Hard failure.

## 18.9 Fresh ambient order

Included in total; excluded from chilled.

## 18.10 Fresh chilled order

Included in both total and chilled.

## 18.11 Style/Tech chilled-labelled source row

Official Task 2A chilled history remains zero, but strict data-consistency audit should stop/report rather than silently normalize contradictory source semantics.

## 18.12 Week with no orders for one series

Not automatically zero until DT-190 classifies coverage.

## 18.13 Week with no orders for any series

Requires source/calendar coverage investigation. Do not infer zero solely from absence.

## 18.14 First/last partial historical week

Flag boundary coverage. Do not silently use as a full zero week.

## 18.15 Calendar duplicate date

Hard failure because it would multiply orders.

## 18.16 Calendar missing order date

Hard failure. Do not derive replacement ISO values silently.

## 18.17 Floating sum tolerance

Use a tight numeric tolerance based on floating-point arithmetic; do not round source rows to force reconciliation.

## 18.18 Zero-volume order

If valid under data-quality rules, it remains an order and contributes to order count even though volume sum is unchanged.

---

# 19. Required synthetic test suite

Create:

```text
tests/test_task2a_history.py
```

All agent-run fixtures must be synthetic.

## Source loading

- deliveries_train schema pass;
- task1_test_inputs schema pass;
- missing required field fail;
- input DataFrames not mutated.

## Append and identity

- both source row counts preserved;
- source lineage field correct;
- unique combined delivery IDs pass;
- duplicate within source fails;
- duplicate across sources fails;
- blank/null ID fails;
- no `drop_duplicates()` behavior hides defect.

## Status retention

- attempted retained;
- deferred retained;
- not_run retained;
- not_run can have blank dispatch/route/vehicle;
- unknown status rejected or flagged according to approved Phase 03 domain rule.

## Requested date

- deferred crosses week: counted in request week;
- deferred crosses year: counted in requested ISO year/week;
- not_run with blank dispatch date still works;
- invalid/missing order date fails.

## Calendar

- many orders map to one calendar date safely;
- duplicate calendar date fails;
- unmatched order date fails;
- official calendar ISO values used;
- ISO-year boundary handled;
- week 53 supported;
- row count unchanged after join.

## Total aggregation

- known weekly total sum;
- separate depots;
- separate brands;
- separate years/weeks;
- order counts correct;
- status counts sum to order count;
- negative volume rejected;
- NaN/Inf rejected.

## Chilled aggregation

- Fresh chilled counted;
- Fresh ambient excluded from chilled;
- Fresh chilled ≤ total;
- Style chilled exactly zero;
- Tech chilled exactly zero;
- non-Fresh chilled-labelled source inconsistency follows strict policy.

## Panel

- expected series/week grid;
- unique weekly key;
- observed rows retained;
- confirmed zero filled with exact zero;
- unresolved missing week not zero-filled;
- boundary partial flagged;
- calendar incomplete flagged;
- no duplicate panel rows.

## Reconciliation

- combined source row count reconciles;
- weekly order counts reconcile;
- weekly total volume reconciles;
- excluded boundary orders, if policy excludes them, are explicitly reconciled separately;
- no unresolved gap passes final validator;
- deterministic output ordering.

---

# 20. Output ordering

For deterministic private panel files, recommended sort:

```text
depot
brand
week_start_date
iso_year
iso_week
```

Do not make lexical `iso_year_week` strings the sole chronological ordering mechanism.

This ordering is an engineering convenience only; final Task 2A submission order is handled later in Phase 17 using official `row_id`.

---

# 21. Logging and privacy

CLI console output should be sanitized.

Allowed:

```text
SOURCE LOAD: PASS
COMBINED DELIVERY IDs UNIQUE: PASS
CALENDAR JOIN: PASS
UNRESOLVED WEEK GAPS: 0
STYLE CHILLED ZERO: PASS
TECH CHILLED ZERO: PASS
WEEKLY RECONCILIATION: PASS
```

Do not print:

```text
real delivery_id values
row-level orders
private weekly volume values
full depot/brand weekly tables
private source dates if unnecessary
```

Detailed information belongs in ignored private reports.

---

# 22. Local CLI contract

Implement:

```bash
python scripts/build_task2a_history.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --config configs/task2a_history.yaml \
  --combined-output data/interim/task2a_demand_orders.csv \
  --weekly-observed-output data/interim/task2a_weekly_observed.csv \
  --weekly-panel-output data/interim/task2a_weekly_panel.csv \
  --report-dir reports/private/phase11_task2a_history
```

PowerShell one-line equivalent:

```powershell
python scripts/build_task2a_history.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --config configs/task2a_history.yaml --combined-output data/interim/task2a_demand_orders.csv --weekly-observed-output data/interim/task2a_weekly_observed.csv --weekly-panel-output data/interim/task2a_weekly_panel.csv --report-dir reports/private/phase11_task2a_history
```

The script must:

- resolve official files through the canonical manifest/path layer;
- validate before writing final panel output;
- return non-zero on blocker;
- avoid printing private rows;
- use atomic/temp writing where practical;
- not overwrite a valid existing output with a failed/partial build.

---

# 23. Required sanitized local result

After the human runs real data locally, report only:

```text
LOCAL PHASE 11 TASK2A HISTORY: PASS
COMBINED DELIVERY_ID UNIQUE: YES
ATTEMPTED RETAINED: YES
DEFERRED RETAINED: YES
NOT_RUN RETAINED: YES
ORDER_DATE RULE: PASS
CALENDAR JOIN UNMATCHED: 0
UNRESOLVED MISSING WEEKS: 0
STYLE CHILLED EXACT ZERO: YES
TECH CHILLED EXACT ZERO: YES
CHILLED <= TOTAL: PASS
WEEKLY TOTAL RECONCILIATION: PASS
WEEKLY ORDER COUNT RECONCILIATION: PASS
```

Do not paste the generated private tables into Codex.

---

# 24. Phase 11 STOP conditions

`READY FOR PHASE 12` must remain **NO** if any of the following occurs:

- `deliveries_train.csv` cannot be loaded with official order fields;
- `task1_test_inputs.csv` cannot be loaded with official order fields;
- either required source is omitted;
- rows are filtered because they lack route/vehicle information;
- attempted orders are dropped;
- deferred orders are dropped;
- `not_run` orders are dropped;
- `dispatch_date` is used as the Task 2A demand date;
- `route date` is used as the Task 2A demand date;
- combined `delivery_id` is not unique;
- duplicate IDs are silently deduplicated;
- calendar date is not unique;
- any order date fails calendar join;
- the calendar join multiplies rows;
- `iso_year`/`iso_week` are replaced by an unofficial grouping without justification;
- order volume is negative, missing, or nonfinite;
- Style chilled history is not exactly zero;
- Tech chilled history is not exactly zero;
- Fresh chilled exceeds Fresh total;
- missing weeks are blindly zero-filled;
- unresolved historical week gaps remain;
- weekly total volume does not reconcile to order-level volume;
- weekly order counts do not reconcile to included orders;
- private competition data is exposed in agent output;
- tests fail;
- local build fails;
- independent review fails.

---

# 25. Definition of Done

Phase 11 passes only when:

- [ ] DT-174 PASS
- [ ] DT-175 PASS
- [ ] DT-176 PASS
- [ ] DT-177 PASS
- [ ] DT-178 PASS
- [ ] DT-179 PASS
- [ ] DT-180 PASS
- [ ] DT-181 PASS
- [ ] DT-182 PASS
- [ ] DT-183 PASS
- [ ] DT-184 PASS
- [ ] DT-185 PASS
- [ ] DT-186 PASS
- [ ] DT-187 PASS
- [ ] DT-188 PASS
- [ ] DT-189 PASS
- [ ] DT-190 PASS
- [ ] DT-191 PASS
- [ ] both required order sources are included;
- [ ] every combined `delivery_id` is unique;
- [ ] no silent deduplication occurs;
- [ ] attempted, deferred and not_run demand is retained;
- [ ] requested `order_date` is the only canonical demand date;
- [ ] official calendar join is complete;
- [ ] official `iso_year`/`iso_week` are source of truth;
- [ ] total demand sums requested `order_volume_m3`;
- [ ] Fresh chilled is separately aggregated;
- [ ] Style chilled is exactly zero;
- [ ] Tech chilled is exactly zero;
- [ ] chilled is never greater than total;
- [ ] complete weekly panel exists;
- [ ] missing-week semantics are investigated;
- [ ] unresolved gaps equal zero;
- [ ] weekly volume reconciliation passes;
- [ ] weekly order-count reconciliation passes;
- [ ] private artifacts remain ignored;
- [ ] synthetic tests pass;
- [ ] full safe regression suite passes;
- [ ] `python -m pip check` passes;
- [ ] local real-data build passes;
- [ ] independent review passes;
- [ ] no unresolved STOP condition remains.

Then:

```text
PHASE 11 STATUS: PASS
READY FOR PHASE 12: YES
```

---

# 26. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-11-task2a-history
```

Recommended logical commits:

```text
feat(task2a): add official demand source loader
feat(task2a): add combined order history validation
feat(task2a): add requested-date calendar mapping
feat(task2a): add weekly total and chilled aggregation
feat(task2a): add complete weekly panel and gap audit
test(task2a): add synthetic demand-history tests
docs(task2a): document Task 2A history construction
```

Before commit:

```bash
git status
git diff
git diff --cached --name-only
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

Verify ignore rules when private files exist locally:

```bash
git check-ignore -v data/interim/task2a_weekly_panel.csv
git check-ignore -v reports/private/phase11_task2a_history/weekly_reconciliation.json
```

Before merge:

```bash
pytest -q
python -m pip check
git status
```

Merge only after local private execution and independent review pass.

---

# 27. Autonomous Codex testing/debugging policy

Codex may automatically:

1. implement a checkpoint;
2. run its synthetic tests;
3. inspect traceback;
4. fix ordinary code/test defects;
5. rerun failing tests;
6. rerun Phase 11 tests;
7. run the complete safe repository test suite;
8. run `python -m pip check`;
9. inspect Git diff/status;
10. self-review against this DoD.

Codex should **not** stop for routine failures it can safely fix.

Codex must stop for:

- official-rule ambiguity;
- a need to inspect restricted real rows;
- an unresolved data-coverage decision that requires operator review;
- a conflict with frozen Task 1 artifacts;
- a material change outside Phase 11;
- a genuine source-schema/data-quality contradiction.

---

# 28. Recommended model / token-efficiency guidance for Codex

Phase 11 is mostly deterministic data engineering with several important accounting guards. It does not need the most expensive reasoning model by default.

Recommended order:

```text
1. GPT-6 Luna — medium reasoning
   Best low-token/cost default if available.

2. GPT-5.6 Luna — high reasoning
   Use if GPT-6 Luna is unavailable and Phase 11 fits comfortably.

3. GPT-5.6 Terra — medium reasoning
   Escalate if the panel/gap logic spans many existing utilities or tests.

4. GPT-5.6 Sol / stronger model
   Use only for a genuine hard blocker, not routine implementation.
```

Token-saving rules:

- let Codex read `AGENTS.md` automatically;
- read `CODEX_HANDOFF_PHASE_11_ONWARDS.md` once at session start;
- read only the Phase 11 section of the master plan plus this contract;
- read Phase 02/03 code/contracts only where loader/data-quality behavior is reused;
- do not reread Phase 04–10 contracts except the Task 1 frozen-boundary summary;
- use targeted symbol/file search instead of repository-wide summaries;
- keep output reports compact.

---

# 29. Ready-to-copy Codex implementation prompt

```text
You are implementing WayLoom Datathon PHASE 11 only.

PHASE:
Task 2A Demand-History Construction

TASK RANGE:
DT-174 through DT-191

EXECUTION MODE:
Controlled autonomous implementation with full SAFE engineering autonomy.

RECOMMENDED MODEL:
Use the lowest-cost coding-capable model that can reliably complete the phase.
Preferred: GPT-6 Luna medium reasoning if available.
Fallback: GPT-5.6 Luna high or GPT-5.6 Terra medium.

You MAY:

- create/edit/refactor Phase 11 tracked code
- create/edit configs
- create/edit docs
- create synthetic fixtures
- run targeted pytest tests
- run the full SAFE test suite
- inspect stack traces
- diagnose/fix ordinary implementation failures
- rerun tests automatically
- run python -m pip check
- inspect git status/diff
- verify ignore rules
- self-review against the Phase 11 DoD

Do NOT stop for routine coding failures that can be safely fixed.

STOP only for:

- official-rule ambiguity
- requirement to inspect restricted competition rows
- conflict with frozen earlier-phase contracts
- unresolved source coverage/missing-week ambiguity requiring human decision
- genuine schema/data-quality blocker
- competition data/AI compliance concern

DO NOT START PHASE 12.

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 11 section only plus needed global rules
4. PHASE_11_COMPETITION_CONTRACT.md
5. existing Phase 02/03 tracked loaders/data-quality utilities
6. configs/dataset_manifest.yaml

Read older contracts only when directly needed.

Task 1 is frozen.
Do not reopen Task 1.

==================================================
OFFICIAL TASK 2A HISTORY RULES
==================================================

Demand history MUST use BOTH:

deliveries_train.csv
task1_test_inputs.csv

Each row is one order identified by delivery_id.

Count every unique requested order exactly once, including:

attempted
deferred
not_run

Use requested:

order_date

NOT:

dispatch_date
route date
actual arrival date

Join calendar.csv using order_date → calendar.date.

Use OFFICIAL:

calendar.iso_year
calendar.iso_week

Only Fresh has chilled demand.

Style historical chilled volume = exactly 0.
Tech historical chilled volume = exactly 0.

Task 2A forecasts VOLUME only.
Do not convert to vehicle/driver counts.

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do NOT inspect/print row-level competition data from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for agent-run tests.

The human operator will run the real Phase 11 build locally.

Do not print:

real delivery IDs
real row values
private weekly volumes
private panel tables

==================================================
CREATE / UPDATE
==================================================

src/task2a/__init__.py
src/task2a/history.py
scripts/build_task2a_history.py
configs/task2a_history.yaml
docs/task2a_history_spec.md
tests/test_task2a_history.py

Reuse common Phase 02/03 loader/validation utilities rather than duplicating them.

Private outputs must be designed for:

data/interim/task2a_demand_orders.csv
data/interim/task2a_weekly_observed.csv
data/interim/task2a_weekly_panel.csv
reports/private/phase11_task2a_history/**

These paths must remain ignored.

==================================================
CHECKPOINT A — DT-174 → DT-177
==================================================

DT-174:
Load deliveries_train.csv using the canonical manifest/path layer.

Validate Task 2A required fields at minimum:

delivery_id
order_date
dispatch_date
dispatch_status
brand
depot
temp_requirement
order_volume_m3

Do NOT filter by route_id, dispatch_date, vehicle, or dispatched state.

Add safe lineage:
source_file = deliveries_train

DT-175:
Load task1_test_inputs.csv as ORDER HISTORY for Task 2A.

Do not use Task 1 predictions.
Do not join route_legs_test.

Add:
source_file = task1_test_inputs

DT-176:
Append the two order tables row-wise.

Before any aggregation assert:

combined row count
=
source1 row count + source2 row count

Do NOT call drop_duplicates().

DT-177:
Validate combined delivery_id:

non-null
nonblank
unique

Check uniqueness within source and across sources.

If any duplicate exists:
STOP.
Do not auto-dedupe.

Run synthetic tests for Checkpoint A.
Fix normal coding failures automatically.

==================================================
CHECKPOINT B — DT-178 → DT-181
==================================================

DT-178:
Keep attempted orders.

DT-179:
Keep deferred orders.

DT-180:
Keep not_run orders.

A not_run order may legitimately have blank:

dispatch_date
route_id
seq_in_route
vehicle_id

It must still contribute demand.

DT-181:
Canonical Task 2A demand date = order_date.

Strictly parse/validate it.

Never group demand by dispatch_date.

Add a synthetic deferred example where:
order_date week != dispatch_date week

Assert the order contributes to order_date week only.

Add a not_run example with no dispatch date.

Run tests.

==================================================
CHECKPOINT C — DT-182 → DT-184
==================================================

DT-182:
Join official calendar:

combined.order_date
→
calendar.date

Use left join and validate many_to_one.

Before join:
calendar.date must be unique.

After join:
joined row count == combined row count
unmatched order dates == 0
no row multiplication

Do not use inner join first.
Do not silently derive replacement weeks for unmatched dates.

DT-183:
Use calendar.iso_year as official source of truth.

DT-184:
Use calendar.iso_week as official source of truth.

Always pair iso_year + iso_week.
Support ISO week 53.
Support ISO-year/calendar-year boundary cases.

Python ISO calculations may only be a cross-check, not a replacement.

Run tests.

==================================================
CHECKPOINT D — DT-185 → DT-188
==================================================

Before aggregation validate order_volume_m3:

numeric
finite
>= 0

DT-185:
Aggregate requested total volume by:

depot
brand
iso_year
iso_week

Canonical:

total_volume_m3 = sum(order_volume_m3)

Also create diagnostic:

order_count
attempted_order_count
deferred_order_count
not_run_order_count

DT-186:
Fresh chilled historical demand:

brand == Fresh
AND
temp_requirement == chilled

Then:

chilled_volume_m3 = sum(order_volume_m3)

Fresh ambient contributes total but not chilled.

Assert:

0 <= Fresh chilled <= Fresh total

DT-187:
For every Style weekly row:

chilled_volume_m3 = exactly 0.0

DT-188:
For every Tech weekly row:

chilled_volume_m3 = exactly 0.0

If source records unexpectedly mark Style/Tech as chilled:
follow configs/task2a_history.yaml strict consistency policy.
Default: STOP/report contradiction rather than silently redefining official semantics.

Run aggregation/chilled tests.

==================================================
CHECKPOINT E — DT-189 → DT-190
==================================================

DT-189:
Build the complete weekly panel.

Series key:

depot + brand

Time key:

iso_year + iso_week

Build official week spine from calendar.csv.

Recommended week metadata:

week_start_date
week_end_date
calendar_days
operating_days

Panel key must be unique:

depot + brand + iso_year + iso_week

IMPORTANT:
Do NOT blindly fill every missing aggregate with zero.

Initially classify missing series/week cells.

Recommended statuses:

OBSERVED_DEMAND
CONFIRMED_ZERO
BOUNDARY_PARTIAL
CALENDAR_INCOMPLETE
UNRESOLVED_GAP

DT-190:
Investigate missing weeks using deterministic coverage logic.

A missing week may become CONFIRMED_ZERO only after coverage checks.

Do not assume:
absence = zero

Default:

CONFIRMED_ZERO
→ fill exact 0 targets/counts

BOUNDARY_PARTIAL
→ resolve/document or exclude explicitly

CALENDAR_INCOMPLETE
→ STOP

UNRESOLVED_GAP
→ STOP

Do not use future Task 2A target information.

Create synthetic cases for each panel status.

Run tests.

==================================================
CHECKPOINT F — DT-191
==================================================

Perform complete reconciliation.

Assert:

combined delivery_id unique

combined row count = both source row counts combined

attempted retained

deferred retained

not_run retained

all weekly assignment based on order_date + official calendar

calendar unmatched = 0

calendar duplicate dates = 0

weekly key duplicates = 0

sum weekly total_volume_m3
≈
sum order-level order_volume_m3

sum weekly order_count
=
order-level included count

Fresh chilled <= total

Style chilled == 0 exactly

Tech chilled == 0 exactly

all targets finite

all targets >= 0

UNRESOLVED_GAP count = 0

If boundary weeks are excluded by documented policy, explicitly reconcile their orders separately so no demand disappears silently.

==================================================
IMPLEMENT LOCAL CLI
==================================================

Implement:

python scripts/build_task2a_history.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --config configs/task2a_history.yaml \
  --combined-output data/interim/task2a_demand_orders.csv \
  --weekly-observed-output data/interim/task2a_weekly_observed.csv \
  --weekly-panel-output data/interim/task2a_weekly_panel.csv \
  --report-dir reports/private/phase11_task2a_history

Do NOT run it against restricted real data in the agent context.

CLI rules:

- no private rows printed
- no delivery IDs printed
- detailed reports private only
- non-zero exit on blocker
- validate before final write
- avoid replacing a valid output with partial failed output

==================================================
REQUIRED SYNTHETIC TESTS
==================================================

Cover all Phase 11 tasks including:

source schemas
append row counts
source lineage
duplicate IDs within/across files
null IDs
attempted/deferred/not_run retention
not_run blank dispatch/route fields
deferred request-week behavior
invalid order_date
calendar duplicate date
calendar unmatched date
calendar no-row-multiplication
ISO-year boundary
ISO week 53
known weekly totals
separate depot/brand groups
nonnegative finite volume
Fresh chilled/ambient split
Style chilled exact zero
Tech chilled exact zero
non-Fresh chilled contradiction policy
complete panel uniqueness
confirmed-zero fill
boundary partial handling
calendar incomplete handling
unresolved-gap blocker
weekly volume reconciliation
weekly order-count reconciliation
deterministic output

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After every checkpoint:

1. run relevant tests
2. inspect traceback
3. fix ordinary implementation bugs
4. rerun failing tests
5. rerun tests/test_task2a_history.py
6. continue only when clean

At the end run:

pytest -q
python -m pip check
git status
git diff

If a documented test requires real private data, do not run it in agent context.
Report the exact human-local command instead.

Verify none of these are staged:

data/raw/**
data/interim/**
reports/private/**

==================================================
STOP CONDITIONS
==================================================

STOP if:

- either required demand source is omitted
- any order status is wrongly filtered
- dispatch_date is used as demand date
- duplicate delivery_id exists
- code silently deduplicates
- calendar has duplicate dates
- any order date is unmatched
- calendar join multiplies demand rows
- official iso_year/week is bypassed
- volume is negative/nonfinite/missing
- Style chilled is nonzero
- Tech chilled is nonzero
- Fresh chilled > total
- missing weeks are blindly zero-filled
- unresolved week gaps remain
- weekly totals do not reconcile
- order counts do not reconcile
- Task 1 frozen artifacts are altered
- private competition rows are exposed
- tests cannot pass without violating the official contract

==================================================
RETURN ONLY
==================================================

PHASE:
11 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-174 READY / FAIL
DT-175 READY / FAIL
DT-176 READY / FAIL
DT-177 READY / FAIL
DT-178 READY / FAIL
DT-179 READY / FAIL
DT-180 READY / FAIL
DT-181 READY / FAIL
DT-182 READY / FAIL
DT-183 READY / FAIL
DT-184 READY / FAIL
DT-185 READY / FAIL
DT-186 READY / FAIL
DT-187 READY / FAIL
DT-188 READY / FAIL
DT-189 READY / FAIL
DT-190 READY / FAIL
DT-191 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

BOTH OFFICIAL HISTORY SOURCES USED:
PASS / FAIL

COMBINED DELIVERY_ID UNIQUENESS:
PASS / FAIL

STATUS RETENTION CONTRACT:
PASS / FAIL

REQUESTED ORDER_DATE CONTRACT:
PASS / FAIL

CALENDAR JOIN:
PASS / FAIL

OFFICIAL ISO WEEK MAPPING:
PASS / FAIL

TOTAL DEMAND AGGREGATION:
PASS / FAIL

FRESH CHILLED AGGREGATION:
PASS / FAIL

STYLE CHILLED ZERO:
PASS / FAIL

TECH CHILLED ZERO:
PASS / FAIL

MISSING-WEEK AUDIT:
PASS / FAIL

WEEKLY RECONCILIATION:
PASS / FAIL

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 11 build command.

PHASE 11 STATUS:
AWAITING LOCAL TASK2A HISTORY BUILD

READY FOR PHASE 12:
NO

Then STOP.
Do not start Phase 12.
```

---

# 30. Ready-to-copy independent Codex review prompt

Use a **fresh Codex session** after the human local run passes.

```text
Perform an independent REVIEW of completed WayLoom Datathon PHASE 11.

PHASE:
Task 2A Demand-History Construction

TASK RANGE:
DT-174 through DT-191

This is a review, not implementation.

DO NOT:

- open data/raw/**
- open data/interim/**
- open reports/private/**
- inspect real delivery IDs
- inspect real weekly volumes
- modify code initially
- start Phase 12
- reopen frozen Task 1

==================================================
READ
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md Phase 11 section
4. PHASE_11_COMPETITION_CONTRACT.md
5. src/task2a/history.py
6. scripts/build_task2a_history.py
7. configs/task2a_history.yaml
8. docs/task2a_history_spec.md
9. tests/test_task2a_history.py
10. relevant common loader/schema utilities
11. .gitignore
12. .cursorignore/.codexignore if present

==================================================
HUMAN LOCAL RESULT
==================================================

The operator will provide only a sanitized result in this shape:

LOCAL PHASE 11 TASK2A HISTORY: PASS
COMBINED DELIVERY_ID UNIQUE: YES
ATTEMPTED RETAINED: YES
DEFERRED RETAINED: YES
NOT_RUN RETAINED: YES
ORDER_DATE RULE: PASS
CALENDAR JOIN UNMATCHED: 0
UNRESOLVED MISSING WEEKS: 0
STYLE CHILLED EXACT ZERO: YES
TECH CHILLED EXACT ZERO: YES
CHILLED <= TOTAL: PASS
WEEKLY TOTAL RECONCILIATION: PASS
WEEKLY ORDER COUNT RECONCILIATION: PASS

Do not ask for private tables or real values.

==================================================
AUDIT EVERY TASK
==================================================

DT-174:
deliveries_train loader keeps all demand rows and validates required fields.

DT-175:
task1_test_inputs is loaded as required Task 2A order history without route-leg or model-output dependency.

DT-176:
sources are appended row-wise and source counts reconcile.

DT-177:
combined delivery_id is validated unique; no silent drop_duplicates behavior.

DT-178:
attempted orders retained.

DT-179:
deferred orders retained.

DT-180:
not_run orders retained even with blank operational dispatch fields.

DT-181:
requested order_date is canonical; dispatch_date is not used to assign demand week.

DT-182:
calendar join is left/many-to-one, calendar date unique, no hidden unmatched rows.

DT-183:
calendar.iso_year is source of truth.

DT-184:
calendar.iso_week is source of truth and paired with iso_year.

DT-185:
total_volume_m3 is sum of requested order_volume_m3 by depot+brand+ISO week.

DT-186:
Fresh chilled = Fresh orders with temp_requirement chilled; Fresh ambient excluded from chilled.

DT-187:
Style chilled target exactly zero.

DT-188:
Tech chilled target exactly zero.

DT-189:
complete weekly panel has unique series/week keys and uses official calendar spine.

DT-190:
missing weeks are investigated; no blind fillna(0); unresolved gaps block.

DT-191:
weekly order/volume/chilled reconciliation is explicit and enforced.

==================================================
GLOBAL AUDIT
==================================================

Confirm:

- Task 1 frozen artifacts unchanged
- no route-based filtering of Task 2A demand
- no dispatch-date demand grouping
- no duplicate ID auto-deduplication
- no inner join that hides unmatched calendar dates
- no unofficial ISO replacement
- no negative/nonfinite target volumes
- no nonzero Style/Tech chilled history
- chilled never exceeds total
- no blind zero-fill
- private outputs ignored
- tests are synthetic
- exceptions/logging do not expose private rows
- no Phase 12 feature/EDA implementation slipped into Phase 11

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q tests/test_task2a_history.py

Then:

pytest -q

If a known documented test requires private data, skip only that test and report it.

Then:

python -m pip check
git status
git diff

Do not run the real-data build.

==================================================
RETURN
==================================================

Return a compact table:

| Task | Requirement | PASS/FAIL | Safe evidence | Blocking fix |

Then print:

OFFICIAL SOURCE INCLUSION          : PASS / FAIL
DELIVERY_ID UNIQUENESS             : PASS / FAIL
STATUS RETENTION                   : PASS / FAIL
REQUESTED ORDER_DATE               : PASS / FAIL
CALENDAR / ISO MAPPING             : PASS / FAIL
TOTAL DEMAND ACCOUNTING            : PASS / FAIL
FRESH CHILLED LOGIC                : PASS / FAIL
STYLE/TECH CHILLED ZERO            : PASS / FAIL
COMPLETE PANEL                     : PASS / FAIL
MISSING-WEEK POLICY                : PASS / FAIL
WEEKLY RECONCILIATION              : PASS / FAIL
SYNTHETIC TESTS                    : PASS / FAIL
FULL SAFE REGRESSION               : PASS / FAIL
PIP CHECK                          : PASS / FAIL
DATA SAFETY                        : PASS / FAIL
HUMAN LOCAL BUILD                  : PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-174: PASS/FAIL
DT-175: PASS/FAIL
DT-176: PASS/FAIL
DT-177: PASS/FAIL
DT-178: PASS/FAIL
DT-179: PASS/FAIL
DT-180: PASS/FAIL
DT-181: PASS/FAIL
DT-182: PASS/FAIL
DT-183: PASS/FAIL
DT-184: PASS/FAIL
DT-185: PASS/FAIL
DT-186: PASS/FAIL
DT-187: PASS/FAIL
DT-188: PASS/FAIL
DT-189: PASS/FAIL
DT-190: PASS/FAIL
DT-191: PASS/FAIL

PHASE 11 REVIEW:
PASS / FAIL

READY FOR PHASE 12:
YES / NO

If FAIL, list exact blockers only.
Do not fix automatically.
Do not begin Phase 12.
```

---

# 31. Human local execution checklist

After Codex implementation reports READY and all safe tests pass:

1. Confirm private paths are ignored.
2. Run Phase 11 CLI locally.
3. Inspect private missing-week report.
4. Resolve any boundary/gap policy issue locally without exposing raw records.
5. Rerun until Phase 11 local status is PASS.
6. Start a **fresh Codex review session** using the review prompt above.
7. Merge only after independent review PASS.

Recommended local commands:

```bash
git check-ignore -v data/interim/task2a_weekly_panel.csv
git check-ignore -v reports/private/phase11_task2a_history/weekly_reconciliation.json

pytest -q tests/test_task2a_history.py

python scripts/build_task2a_history.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --config configs/task2a_history.yaml \
  --combined-output data/interim/task2a_demand_orders.csv \
  --weekly-observed-output data/interim/task2a_weekly_observed.csv \
  --weekly-panel-output data/interim/task2a_weekly_panel.csv \
  --report-dir reports/private/phase11_task2a_history
```

---

# 32. Phase 11 completion record template

```markdown
# Phase 11 Completion Record

## Tasks

- [ ] DT-174
- [ ] DT-175
- [ ] DT-176
- [ ] DT-177
- [ ] DT-178
- [ ] DT-179
- [ ] DT-180
- [ ] DT-181
- [ ] DT-182
- [ ] DT-183
- [ ] DT-184
- [ ] DT-185
- [ ] DT-186
- [ ] DT-187
- [ ] DT-188
- [ ] DT-189
- [ ] DT-190
- [ ] DT-191

## Safe agent stage

- Phase 11 tests: PASS / FAIL
- Full safe regression: PASS / FAIL
- pip check: PASS / FAIL
- private paths protected: YES / NO

## Local data stage

- Both required sources used: YES / NO
- Combined delivery_id unique: YES / NO
- Attempted retained: YES / NO
- Deferred retained: YES / NO
- not_run retained: YES / NO
- Requested order_date rule: PASS / FAIL
- Calendar unmatched: 0 / NONZERO
- Unresolved missing weeks: 0 / NONZERO
- Style chilled exactly zero: YES / NO
- Tech chilled exactly zero: YES / NO
- Chilled <= total: PASS / FAIL
- Weekly volume reconciliation: PASS / FAIL
- Weekly order-count reconciliation: PASS / FAIL

## Independent review

- Review: PASS / FAIL

## Verdict

PHASE 11 STATUS: PASS / FAIL
READY FOR PHASE 12: YES / NO
```

---

# 33. Final checklist before Phase 12

- [ ] `deliveries_train.csv` included.
- [ ] `task1_test_inputs.csv` included.
- [ ] Combined `delivery_id` unique.
- [ ] No automatic dedupe.
- [ ] Attempted orders counted.
- [ ] Deferred orders counted.
- [ ] `not_run` orders counted.
- [ ] Demand grouped by requested `order_date`.
- [ ] Calendar joined by requested date.
- [ ] Calendar join does not change row count.
- [ ] `calendar.iso_year` used.
- [ ] `calendar.iso_week` used.
- [ ] Total demand is requested `order_volume_m3` sum.
- [ ] Fresh chilled subset constructed separately.
- [ ] Style chilled exactly zero.
- [ ] Tech chilled exactly zero.
- [ ] `chilled_volume_m3 <= total_volume_m3`.
- [ ] Complete weekly panel generated.
- [ ] Missing weeks investigated.
- [ ] No blind zero-fill.
- [ ] Unresolved gaps = 0.
- [ ] Weekly total volume reconciles.
- [ ] Weekly order count reconciles.
- [ ] Private files remain ignored.
- [ ] Synthetic tests pass.
- [ ] Full safe suite passes.
- [ ] pip check passes.
- [ ] Local real-data build passes.
- [ ] Independent review passes.
- [ ] Task 1 frozen artifacts unchanged.

Only then:

```text
PHASE 11 STATUS: PASS
READY FOR PHASE 12: YES
```

