# PHASE 04 — Task 1 Training Data & Label Construction

> **Requested filename:** `PHASE_04_COMPETITION_CONTRACT.md`  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks:** **DT-055 → DT-071** (17 tasks)  
> **Dependency:** Phase 03 PASS, zero unresolved blockers  
> **Execution:** **Task-by-task / small batches only**  
> **Gate:** Every dispatched historical order maps to exactly one historical route leg; official service/lateness labels are reconstructed exactly; midnight handling is deterministic; unit tests pass; training-only actuals are blocked from prediction features.

---

# 1. Purpose

Task 1 does not provide ready-made labels. Phase 04 reconstructs two targets from historical order and route records:

- `service_minutes` — actual outlet handling time after receiving can start.
- `late_flag` — whether actual arrival is strictly after the outlet window closes.

Official formulas:

```text
service_start = max(actual arrival, window opening)
service_minutes = leave_outlet_time - service_start
late_flag = 1 only if actual arrival > window_close_time
```

Therefore:

- early-arrival waiting is **not** service time;
- arrival exactly at the close time is **not late**;
- late deliveries still receive a service-time label;
- planned times are not used to create the historical target;
- actual route outcomes are training-only and must not become direct prediction-time features later.

This phase is competition-critical because label construction is part of Datathon assessment.

---

# 2. Official Task 1 contract

## 2.1 Historical order source

`deliveries_train.csv` contains one row per order, identified by `delivery_id`.

Official `dispatch_status` semantics:

```text
attempted = dispatched on order_date
deferred  = dispatched later because fleet capacity was short
not_run   = never dispatched
```

Task 1 historical label construction therefore starts from `attempted` and `deferred` orders. `not_run` orders have no delivered-route outcome and are excluded from the Task 1 label population.

A deferred order that later ran **must not be excluded**.

## 2.2 Historical route source

`route_legs_train.csv` contains one row per historical route leg and includes planned and actual journey timestamps.

Official join:

```text
deliveries_train.(route_id, seq_in_route)
↔
route_legs_train.(route_id, seq)
```

Every dispatched training order must match exactly one route leg.

## 2.3 Historical actual fields

Training route records include:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

The official target formulas use `arrival_time` and `leave_outlet_time` plus the order/outlet delivery window. `actual_depart_time` and `actual_travel_duration_min` may be used only to validate chronology/midnight reconstruction.

## 2.4 Official labels

```python
service_start_dt = max(arrival_dt, window_open_dt)

service_minutes = (
    leave_outlet_dt - service_start_dt
).total_seconds() / 60.0

late_flag = int(arrival_dt > window_close_dt)
```

**Strict `>` is mandatory.** `arrival_dt == window_close_dt` means `late_flag = 0`.

## 2.5 Official-equivalent worked example

```text
arrival       07:10
window open   07:30
leave         07:50
window close  08:00

service start 07:30
service       20 minutes
late          0
```

Waiting from 07:10 to 07:30 is not service time.

---

# 3. Source authority

Use this priority:

1. Official Challenge Booklet.
2. Official competition files/templates.
3. Approved `WAYLOOM_DATATHON_MASTER_PLAN.md`.
4. Approved Phase 00–03 contracts.
5. This document.
6. Implementation assumptions.

If any internal recommendation conflicts with the official rule, stop and use the official rule.

---

# 4. Data-safety execution model

Competition data and derived row-level labels remain restricted.

## AI-agent stage

Cursor/Codex may implement code, synthetic tests, documentation, and review tracked source files. It must **not** open:

```text
data/raw/**
data/interim/**
reports/private/**
```

It must not inspect real `delivery_id`, arrival/leave times, real labels, or run the real label builder.

## Local operator stage

The human runs the completed builder in a normal local terminal. Private outputs stay under:

```text
data/interim/
reports/private/phase04_task1_labels/
```

Return to the AI agent only sanitized status, for example:

```text
LOCAL PHASE 04 LABEL BUILD: PASS
DISPATCHED ORDERS MATCHED 1:1: YES
UNMATCHED DISPATCHED ORDERS: 0
DUPLICATE MATCHES: 0
DESTINATION MISMATCHES: 0
NEGATIVE SERVICE LABELS: 0
LABEL TESTS: PASS
```

Do not paste row-level reports.

---

# 5. Task registry

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---|---|---|---|
| [ ] | **DT-055** | [O/E] | P0 | Phase 03 | Select dispatched historical orders |
| [ ] | **DT-056** | [O/E] | P0 | DT-055 | Exclude expected no-outcome rows without silently dropping broken dispatched rows |
| [ ] | **DT-057** | [O] | P0 | DT-055–056 | Join orders to route legs with official composite key |
| [ ] | **DT-058** | [O/E] | P0 | DT-057 | Prove one-to-one cardinality |
| [ ] | **DT-059** | [E] | P0 | DT-057 | Detect unmatched dispatched orders/orphan legs |
| [ ] | **DT-060** | [E] | P0 | DT-057 | Detect duplicate matches |
| [ ] | **DT-061** | [E] | P0 | DT-057 | Verify order outlet equals route-leg destination |
| [ ] | **DT-062** | [O/E] | P0 | DT-058–061 | Convert clock fields to resolved datetimes |
| [ ] | **DT-063** | [E] | P0 | DT-062 | Handle midnight rollover deterministically |
| [ ] | **DT-064** | [O] | P0 | DT-062–063 | Construct `service_start` |
| [ ] | **DT-065** | [O] | P0 | DT-064 | Construct `service_minutes` |
| [ ] | **DT-066** | [O] | P0 | DT-062–063 | Construct strict `late_flag` |
| [ ] | **DT-067** | [E] | P0 | DT-065–066 | Validate labels and invariants |
| [ ] | **DT-068** | [E] | P0 | DT-067 | Inspect long-service candidates |
| [ ] | **DT-069** | [E] | P0 | DT-066–067 | Summarize target/class distribution |
| [ ] | **DT-070** | [E] | P0 | DT-055–069 | Build comprehensive label unit tests |
| [ ] | **DT-071** | [E] | P0 | DT-070 | Freeze one reusable canonical label builder |

Legend: `[O]` official requirement; `[E]` engineering control; `[O/E]` official rule implemented with engineering safeguards.

---

# 6. Files to create

Tracked:

```text
src/task1/__init__.py
src/task1/labels.py
scripts/build_task1_labels.py
docs/task1_label_spec.md
tests/test_task1_labels.py
```

Optional tracked configuration:

```text
configs/task1_labels.yaml
```

Private ignored outputs:

```text
data/interim/task1_training_labels.csv
reports/private/phase04_task1_labels/build_summary.json
reports/private/phase04_task1_labels/join_integrity.json
reports/private/phase04_task1_labels/chronology_validation.json
reports/private/phase04_task1_labels/label_validation.json
reports/private/phase04_task1_labels/long_service_review.json
reports/private/phase04_task1_labels/target_distribution.json
```

Do not commit private outputs.

---

# 7. Detailed implementation tasks

## DT-055 — Select dispatched historical orders

**Execution:** small batch with DT-056.

### Objective

Create the historical Task 1 population from orders that actually ran.

### Implementation

Create a pure function such as:

```python
def select_dispatched_orders(deliveries: pd.DataFrame) -> pd.DataFrame:
    ...
```

Requirements:

1. Keep `dispatch_status in {"attempted", "deferred"}`.
2. Exclude `not_run`.
3. Preserve source row order/traceability.
4. Do not mutate input.
5. Do not drop a dispatched order merely because route fields are missing; that becomes a blocker in DT-056.

### Inputs

`deliveries_train.csv`.

### Synthetic tests

- attempted retained;
- deferred retained;
- not_run excluded;
- original order preserved;
- input unchanged.

### Edge cases

- no dispatched orders → blocker;
- unexpected status → blocker;
- dispatched row with blank route assignment → retain for explicit failure, not silent deletion.

### Definition of Done

- [ ] attempted retained;
- [ ] deferred retained;
- [ ] not_run excluded;
- [ ] no dispatched order silently disappears.

### STOP

Stop if status semantics disagree with Phase 03 or the official definitions.

---

## DT-056 — Exclude rows without historical delivery outcomes correctly

**Execution:** small batch with DT-055.

### Objective

Separate **expected exclusion** from **broken dispatched history**.

### Correct behavior

The expected Task 1 exclusion is:

```text
dispatch_status = not_run
```

For `attempted` or `deferred`, these are integrity failures rather than normal exclusions:

```text
missing route_id
missing seq_in_route
no matching route leg
missing arrival_time
missing leave_outlet_time
```

Do not create the training set with a generic `dropna()`.

### Output classes

```text
eligible_dispatched
expected_excluded_not_run
invalid_dispatched_missing_assignment
```

### Tests

- not_run → expected exclusion;
- attempted/deferred with assignment → eligible;
- attempted/deferred missing matching-key component → blocker class.

### Definition of Done

- [ ] expected exclusions explicit;
- [ ] invalid dispatched rows explicit;
- [ ] no silent `dropna`.

### STOP

Any dispatched order without the official matching key blocks progression until understood.

---

## DT-057 — Join orders to route legs using the official composite key

**Execution:** **INDIVIDUAL CRITICAL TASK**.

### Objective

Match every dispatched order to exactly one historical route leg.

### Official join

```python
left_on  = ["route_id", "seq_in_route"]
right_on = ["route_id", "seq"]
```

### Required design

Use a left join for audit visibility:

```python
joined = dispatched.merge(
    route_legs,
    how="left",
    left_on=["route_id", "seq_in_route"],
    right_on=["route_id", "seq"],
    validate="one_to_one",
    indicator=True,
    suffixes=("_order", "_leg"),
)
```

Why not an inner join? It can silently remove unmatched dispatched orders.

Preserve at least:

```text
delivery_id
route_id
seq_in_route
seq
leg_id
outlet_id
to_outlet
date
arrival_time
leave_outlet_time
window_open_time
window_close_time
```

### Tests

- one order ↔ one leg;
- same `seq` on different routes is valid;
- same route different sequences are valid;
- unmatched order remains visible;
- duplicate route key raises;
- source row traceability remains.

### Definition of Done

- [ ] exact official key;
- [ ] left join;
- [ ] one-to-one validation;
- [ ] merge indicator retained until audit;
- [ ] no labels calculated yet.

### STOP

Any alternate join key, ambiguous match, duplicate route key, or hidden unmatched row.

---

## DT-058 — Prove one-to-one match cardinality

### Objective

Prove the official relationship rather than assuming the merge succeeded.

Required assertions:

```text
joined row count == dispatched order row count
delivery_id remains unique
all dispatched merge indicators == both
no row multiplication
```

A matching row count alone is insufficient; semantic destination validation is also required by DT-061.

### Private output

`join_integrity.json`.

### Tests

Perfect match, unmatched row, duplicated left/right key, and a wrong-destination case caught later.

### Definition of Done

- [ ] explicit one-to-one proof;
- [ ] all dispatched rows accounted for.

### STOP

Any cardinality violation.

---

## DT-059 — Detect unmatched dispatched orders / orphan legs

### Dispatched side

`_merge == "left_only"` must be zero for a passing run.

Do not drop unmatched orders.

### Orphan route legs

A full outer diagnostic may record route legs not used by the Task 1 dispatched population. Report separately. The critical official requirement is that **every dispatched order matches exactly one leg**.

### Tests

- unmatched dispatched order → blocker;
- extra unrelated route leg → separately reported;
- no private IDs printed.

### Definition of Done

- [ ] unmatched dispatched count zero;
- [ ] orphan analysis separated from dispatched-order failure.

### STOP

Unmatched dispatched count > 0.

---

## DT-060 — Detect duplicate join matches

### Objective

Guarantee no order maps to multiple legs and no merge multiplies labels.

Revalidate:

```text
(route_id, seq_in_route) on dispatched side
(route_id, seq) on route side
delivery_id after join
```

### Tests

- duplicate route key;
- duplicate dispatched route-position key;
- duplicate delivery_id;
- same seq value on different route IDs remains valid.

### Definition of Done

- [ ] no ambiguous matches;
- [ ] no row multiplication.

### STOP

Any ambiguous match.

---

## DT-061 — Verify outlet destination consistency

### Objective

Catch a unique but semantically wrong composite-key join.

Required:

```text
deliveries_train.outlet_id == route_legs_train.to_outlet
```

for every matched dispatched order.

### Tests

Correct destination and wrong destination.

### Definition of Done

- [ ] destination mismatch count = 0.

### STOP

Any unexplained mismatch.

---

## DT-062 — Convert clock fields to resolved datetimes

**Execution:** time-system batch with DT-063.

### Objective

Convert `HH:MM` values into timestamps that can be compared/subtracted safely.

Historical route fields:

```text
date
actual_depart_time
arrival_time
leave_outlet_time
actual_travel_duration_min
```

Window fields:

```text
window_open_time
window_close_time
```

### Time convention

All source clock values are Asia/Colombo. For simplicity, use timezone-naive **local** datetimes consistently inside label construction and document that choice. Do not mix UTC/local values.

### Helpers

```python
def parse_clock(value: str) -> tuple[int, int]:
    ...

def combine_local_date_clock(date_value, clock_value, day_offset=0):
    ...
```

Preserve raw clock columns and create new resolved timestamp columns.

### Tests

- 00:00;
- 07:10;
- 23:59;
- invalid 24:00;
- malformed time;
- blank required actual time fails.

### Definition of Done

- [ ] strict parser;
- [ ] single local-time convention;
- [ ] original fields preserved.

### STOP

Required time cannot be parsed.

---

## DT-063 — Handle midnight rollover deterministically

**Execution:** **INDIVIDUAL CRITICAL TIME REVIEW**.

### Objective

Avoid negative or +24-hour-wrong labels when routes cross midnight.

Example:

```text
depart 23:50
arrival 00:10
leave 00:30
```

Arrival/leave are on the next calendar day.

### Recommended algorithm

Within each `route_id`, sort by `seq`. Resolve events in order:

```text
actual_depart_time
arrival_time
leave_outlet_time
```

Maintain a day offset and previous resolved event.

For each clock:

1. combine route date + clock + current offset;
2. if candidate is earlier than the previous event, increment the day offset until chronology is restored;
3. validate `arrival_dt - actual_depart_dt` against `actual_travel_duration_min` using a documented minute-level tolerance;
4. if the reconstructed duration cannot be reconciled, raise a blocker instead of silently adding another day.

### Window anchoring

Use the resolved arrival service-day offset:

```text
arrival day = route date + resolved arrival day offset
window open = arrival service day + window_open clock
window close = arrival service day + window_close clock
```

If:

```text
window_close_clock < window_open_clock
```

then the outlet window crosses midnight and close receives `+1 day`.

Do not shift windows merely to force a desired label.

### Ambiguity

If route sequence + clocks + actual travel duration cannot produce a consistent chronology, stop. Do not invent a hidden data-specific heuristic.

### Synthetic tests

Normal daytime route; midnight route; cross-midnight outlet window; impossible chronology such as a short backwards arrival that contradicts actual travel duration.

### Definition of Done

- [ ] deterministic rollover;
- [ ] duration guardrail;
- [ ] cross-midnight window support;
- [ ] impossible chronology raises.

### STOP

Any unresolved chronology ambiguity.

---

## DT-064 — Construct `service_start`

**Execution:** **INDIVIDUAL OFFICIAL LABEL TASK**.

### Formula

```python
service_start_dt = max(arrival_dt, window_open_dt)
```

### Cases

Early:

```text
arrival 07:10
open    07:30
→ 07:30
```

Inside window:

```text
arrival 07:40
open    07:30
→ 07:40
```

Late:

```text
arrival 08:10
close   08:00
→ service still starts 08:10
```

Do not use planned arrival. Window close does not cap service start.

### Definition of Done

- [ ] exact `max` rule;
- [ ] early waiting excluded;
- [ ] late service begins at actual arrival.

### STOP

Any use of planned arrival or window close in service-start selection.

---

## DT-065 — Construct `service_minutes`

**Execution:** **INDIVIDUAL OFFICIAL LABEL TASK**.

### Formula

```python
service_minutes = (
    leave_outlet_dt - service_start_dt
).total_seconds() / 60.0
```

Requirements:

```text
finite
>= 0
no rounding during label construction
```

Official-equivalent synthetic example:

```text
arrival 07:10
open    07:30
leave   07:50
→ 20 minutes
```

Wrong: `leave - arrival = 40` because that includes waiting.

Late delivery example:

```text
arrival 08:10
close   08:00
leave   08:32
→ service = 22
```

### Tests

Early, exact opening, inside window, late, midnight leave, and invalid leave before service start.

### Definition of Done

- [ ] official formula exact;
- [ ] waiting excluded;
- [ ] no clipping/rounding;
- [ ] no negative/nonfinite result.

### STOP

Negative/nonfinite label or planned-time use.

---

## DT-066 — Construct `late_flag`

**Execution:** **INDIVIDUAL OFFICIAL LABEL TASK**.

### Formula

```python
late_flag = (arrival_dt > window_close_dt).astype("int8")
```

### Boundary

```text
close 08:00
arrival 07:59 → 0
arrival 08:00 → 0
arrival 08:01 → 1
```

Do not use leave time, service completion, or planned arrival.

### Definition of Done

- [ ] strict `>`;
- [ ] equality gives 0;
- [ ] only `{0,1}` values.

### STOP

Use of `>=` is an immediate blocker.

---

## DT-067 — Validate label ranges and invariants

Required hard assertions:

```text
service_minutes finite
service_minutes >= 0
late_flag in {0,1}
service_start_dt >= arrival_dt
service_start_dt >= window_open_dt
leave_outlet_dt >= service_start_dt
delivery_id unique
row count == matched dispatched count
```

Semantic equivalence:

```text
arrival < open  → service_start == open
arrival >= open → service_start == arrival
arrival <= close → late_flag == 0
arrival > close  → late_flag == 1
```

Do not invent a relationship between service duration and lateness.

### Private output

`label_validation.json`.

### Definition of Done

- [ ] all invariants pass;
- [ ] zero invalid labels.

### STOP

Any invariant violation.

---

## DT-068 — Inspect long-service label candidates

### Objective

Find suspicious long service labels that may indicate chronology/join problems or genuine long handling.

The official booklet does **not** define a maximum service time. Therefore do not classify `service > X` as invalid without an official rule.

### Recommended private diagnostics

```text
median
p90
p95
p99
max
IQR
MAD-based extreme flags
```

For extremes, review in this order:

1. order-leg match;
2. timestamp resolution;
3. midnight handling;
4. window anchoring;
5. then treat as genuine extreme if structurally valid.

Never cap, delete, or winsorize the target in this phase.

### Definition of Done

- [ ] extremes reviewed structurally;
- [ ] no automatic target removal/transformation.

### STOP

Any extreme caused by unresolved join/time error.

---

## DT-069 — Summarize target/class distribution

Private summaries only.

For `service_minutes`:

```text
count, mean, median, std, p50, p75, p90, p95, p99, min, max
```

For `late_flag`:

```text
late_count
not_late_count
late_rate
```

Optional later-use segments if approved references are already joined correctly:

```text
brand
depot
dock_type
```

Do not resample, class-weight, calibrate, or train models here.

### Definition of Done

- [ ] target distributions recorded privately;
- [ ] no modelling performed.

### STOP

Impossible target pattern sends the work back to join/time/label validation.

---

## DT-070 — Build comprehensive label unit tests

**Execution:** critical test gate.

`tests/test_task1_labels.py` must use synthetic records only.

Required groups:

### Population

- attempted retained;
- deferred retained;
- not_run excluded;
- invalid dispatched row not silently dropped.

### Join

- official composite key;
- one-to-one success;
- unmatched dispatched fails;
- duplicate route key fails;
- destination mismatch fails.

### Time

- valid/invalid `HH:MM`;
- normal chronology;
- midnight rollover;
- cross-midnight window;
- impossible chronology fails.

### Service start

- early;
- exact opening;
- inside window;
- late arrival.

### Service minutes

- official-equivalent example = 20;
- waiting excluded;
- late service measured;
- midnight leave works;
- negative service fails.

### Late flag

- before close = 0;
- exact close = 0;
- after close = 1.

### Leakage guard

Future direct feature metadata must forbid:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag
```

Recommended explicit test names:

```python
test_arrival_exactly_at_window_close_is_not_late()
test_early_waiting_is_excluded_from_service_minutes()
test_dispatched_order_without_leg_fails()
test_midnight_rollover_produces_nonnegative_service()
```

### Definition of Done

- [ ] official boundaries covered;
- [ ] failure modes covered;
- [ ] all tests pass.

### STOP

Do not freeze label logic while any official-rule test fails.

---

## DT-071 — Freeze reusable Task 1 label-construction function

**Execution:** final engineering gate.

Recommended API:

```python
def build_task1_training_labels(
    deliveries_train: pd.DataFrame,
    route_legs_train: pd.DataFrame,
) -> pd.DataFrame:
    """Build official Task 1 historical labels."""
```

Recommended internal sequence:

```text
select_dispatched_orders
validate_task1_eligibility
validate_join_keys
join_orders_to_route_legs
validate_join_integrity
resolve_route_actual_datetimes
resolve_delivery_window_datetimes
compute_service_start
compute_service_minutes
compute_late_flag
validate_task1_labels
```

Required characteristics:

- deterministic;
- input DataFrames not mutated;
- explicit errors;
- no silent dropping;
- no feature engineering;
- no modelling;
- no split logic;
- one canonical implementation reused by notebooks/pipelines.

`scripts/build_task1_labels.py` should load local files, call the canonical function, save ignored interim labels/private reports, never print rows, and return nonzero on blockers.

### Definition of Done

- [ ] one canonical function;
- [ ] full tests pass;
- [ ] local official-data build passes;
- [ ] no duplicate competing label logic remains.

### STOP

Do not continue if notebooks/scripts contain conflicting copies of label formulas.

---

# 8. Recommended code architecture

`src/task1/labels.py` should expose focused helpers rather than one opaque function.

Recommended public/internal functions:

```python
select_dispatched_orders(...)
validate_task1_eligibility(...)
validate_task1_join_keys(...)
join_orders_to_route_legs(...)
validate_task1_join_integrity(...)
parse_clock(...)
resolve_route_actual_datetimes(...)
resolve_delivery_window_datetimes(...)
compute_service_start(...)
compute_service_minutes(...)
compute_late_flag(...)
validate_task1_labels(...)
build_task1_training_labels(...)
```

Avoid using notebook cells as the only source of truth.

---

# 9. Time-resolution rules

Do **not** compute label minutes by subtracting clock strings/minute-of-day values directly.

Bad:

```python
leave_minute_of_day - arrival_minute_of_day
```

This breaks early-arrival waiting and midnight rollover.

Recommended route event order:

```text
route seq 0: depart → arrival → leave
route seq 1: depart → arrival → leave
...
```

A clock-of-day decrease may indicate midnight. After unwrapping, validate:

```text
resolved arrival - resolved actual depart
```

against `actual_travel_duration_min`. A bad short backwards clock should not silently become a ~24-hour trip.

### Service-day window anchoring

If arrival resolves to the next day, anchor the outlet window to that resolved service day. If `close_clock < open_clock`, the window itself crosses midnight and close gets +1 day.

If chronology remains ambiguous after route sequence and actual travel-duration validation, fail explicitly.

---

# 10. Leakage boundary

Create and reuse:

```python
TASK1_FORBIDDEN_DIRECT_FEATURES = {
    "actual_depart_time",
    "actual_travel_duration_min",
    "arrival_time",
    "leave_outlet_time",
    "service_start_dt",
    "service_minutes",
    "late_flag",
}
```

Training actuals are legitimate for constructing labels but not direct prediction-time inputs.

Planned fields such as planned departure/travel/arrival may later be considered because the official Task 1 test data provides planned information, subject to later feature validation.

---

# 11. Local CLI contract

Preferred command:

```bash
python scripts/build_task1_labels.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output data/interim/task1_training_labels.csv \
  --report-dir reports/private/phase04_task1_labels
```

PowerShell one line:

```powershell
python scripts/build_task1_labels.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --output data/interim/task1_training_labels.csv --report-dir reports/private/phase04_task1_labels
```

Safe console output should only contain high-level PASS/FAIL checks. Never print delivery IDs, raw timestamps, labels, unmatched IDs, or DataFrame rows.

---

# 12. Execution plan — mandatory checkpoints

Phase 04 must **not** be a single autonomous run.

```text
Checkpoint A: DT-055 + DT-056
STOP

Checkpoint B: DT-057
STOP + review

Checkpoint C: DT-058 + DT-059 + DT-060 + DT-061
STOP + review

Checkpoint D: DT-062 + DT-063
STOP + review

Checkpoint E: DT-064
STOP + review

Checkpoint F: DT-065
STOP + review

Checkpoint G: DT-066
STOP + review

Checkpoint H: DT-067 + DT-068 + DT-069
STOP

Checkpoint I: DT-070 + DT-071
STOP

Human local official-data build
STOP

Independent Phase 04 review
```

Only then may the next phase begin.

---

# 13. Cursor checkpoint prompts

## Checkpoint A — DT-055 + DT-056

```text
Implement only Phase 04 tasks DT-055 and DT-056.

Read WAYLOOM_DATATHON_MASTER_PLAN.md and PHASE_04_COMPETITION_CONTRACT.md.
Use synthetic fixtures only. Do not access data/raw, data/interim, or reports/private.

Implement:
- attempted + deferred historical orders retained;
- not_run excluded as expected no-outcome rows;
- dispatched row missing route assignment classified as BLOCKER, not silently excluded;
- preserve source traceability;
- no generic dropna;
- do not mutate input DataFrame.

Add relevant tests and run them.

Return DT-055 PASS/FAIL, DT-056 PASS/FAIL, files changed, tests, issues.
Then STOP. Do not implement DT-057.
```

## Checkpoint B — DT-057

```text
Implement ONLY DT-057.

Official join:
deliveries route_id + seq_in_route
↔
route legs route_id + seq

Requirements:
- left join;
- one_to_one validation;
- merge indicator;
- preserve delivery_id/traceability;
- never use inner join to hide unmatched orders;
- no labels yet;
- synthetic tests only;
- do not access official data.

Return PASS/FAIL and STOP.
```

## Checkpoint C — DT-058 through DT-061

```text
Implement ONLY DT-058, DT-059, DT-060 and DT-061.

Verify:
- joined row count equals dispatched row count;
- every dispatched row matched exactly once;
- no duplicate/multiplied matches;
- delivery_id stays unique;
- unmatched dispatched count is zero in a passing run;
- outlet_id equals to_outlet;
- no private IDs printed.

Synthetic tests only. No time/label code.
Return each task PASS/FAIL and STOP.
```

## Checkpoint D — DT-062 + DT-063

```text
Implement ONLY DT-062 and DT-063.

Requirements:
- strict HH:MM parser;
- Asia/Colombo local-time convention;
- preserve raw clock columns;
- route events resolved in seq order;
- deterministic midnight rollover;
- validate resolved travel time using actual_travel_duration_min;
- window anchored to resolved service day;
- close < open means cross-midnight window;
- impossible chronology raises;
- synthetic tests only.

Do not calculate service_start, service_minutes, or late_flag yet.
Return PASS/FAIL and STOP.
```

## Checkpoint E — DT-064

```text
Implement ONLY DT-064.

Official formula:
service_start_dt = max(arrival_dt, window_open_dt)

Test early arrival, exact opening, inside-window arrival, and late arrival.
Do not use planned arrival.
Do not implement service_minutes or late_flag.
Return PASS/FAIL and STOP.
```

## Checkpoint F — DT-065

```text
Implement ONLY DT-065.

Official formula:
service_minutes = (leave_outlet_dt - service_start_dt).total_seconds() / 60

Requirements:
- waiting excluded;
- finite and >= 0;
- no rounding/clipping;
- late deliveries remain valid;
- midnight-resolved timestamps supported.

Synthetic official-equivalent case:
arrival 07:10, open 07:30, leave 07:50 → 20 minutes.

Return PASS/FAIL and STOP.
```

## Checkpoint G — DT-066

```text
Implement ONLY DT-066.

Official rule:
late_flag = 1 only when arrival_dt > window_close_dt

Boundary tests:
07:59 vs 08:00 → 0
08:00 vs 08:00 → 0
08:01 vs 08:00 → 1

Using >= is forbidden.
Do not use leave time or planned arrival.
Return PASS/FAIL and STOP.
```

## Checkpoint H — DT-067 through DT-069

```text
Implement ONLY DT-067, DT-068 and DT-069.

DT-067: hard label invariants.
DT-068: private long-service diagnostics; do not drop/clip/winsorize.
DT-069: private target/class summaries; do not train, resample, class-weight or calibrate.

Use synthetic tests where applicable.
Do not access official data.
Return each task PASS/FAIL and STOP.
```

## Checkpoint I — DT-070 + DT-071

```text
Implement ONLY DT-070 and DT-071.

Create comprehensive tests for selection, official join, failures, destination consistency, HH:MM parsing, midnight, cross-midnight windows, service_start, service_minutes, strict lateness boundary, negative-label rejection, no silent dispatched-row dropping, and leakage deny-list.

Freeze one canonical build_task1_training_labels(...) implementation.

Create/update:
src/task1/labels.py
tests/test_task1_labels.py
scripts/build_task1_labels.py
docs/task1_label_spec.md

Do not access official data and do not start EDA/modelling.
Run the full safe tests, report PASS/FAIL, then STOP.
```

---

# 14. Enhanced Cursor controller prompt

Use this at the **start** of Phase 04. It intentionally performs only Checkpoint A.

```text
We are starting WayLoom Datathon PHASE 04 — Task 1 Training Data & Label Construction.

TASK RANGE: DT-055 through DT-071.

This is a HIGH-RISK task-by-task phase. Do NOT implement the entire phase autonomously.

Read completely:
1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. approved Phase 00–03 contracts
3. PHASE_04_COMPETITION_CONTRACT.md
4. existing tracked data-quality/schema utilities

DATA SAFETY:
Do not access data/raw/**, data/interim/**, or reports/private/**.
Use synthetic fixtures only.

OFFICIAL RULES:

JOIN:
deliveries_train route_id + seq_in_route
↔
route_legs_train route_id + seq

Every dispatched training order must match exactly one leg.

SERVICE START:
max(actual arrival, window opening)

SERVICE MINUTES:
leave_outlet_time - service_start

LATE:
1 only when actual arrival > window close.
Arrival exactly at close is NOT late.

EARLY ARRIVAL:
waiting before window opening is not service time.

LEAKAGE:
actual_depart_time, actual_travel_duration_min, arrival_time, leave_outlet_time are training actuals and may not become direct prediction-time features.
service_start/service_minutes/late_flag are target-derived and may not be direct predictors of their own targets.

MANDATORY CHECKPOINT ORDER:
A DT-055 + DT-056
B DT-057
C DT-058–DT-061
D DT-062 + DT-063
E DT-064
F DT-065
G DT-066
H DT-067–DT-069
I DT-070 + DT-071

RIGHT NOW IMPLEMENT CHECKPOINT A ONLY.

Requirements:
- retain attempted;
- retain deferred;
- exclude not_run;
- missing route assignment on a dispatched row = BLOCKER, not silent exclusion;
- no generic dropna population creation;
- input DataFrame not mutated;
- preserve source traceability;
- synthetic tests only.

Return only:
CHECKPOINT A
DT-055 PASS/FAIL
DT-056 PASS/FAIL
FILES CREATED/MODIFIED
TESTS
ISSUES
OFFICIAL DATA ACCESSED: NO
READY FOR DT-057: YES/NO

Then STOP. Do not implement DT-057 until explicitly instructed.
```

---

# 15. Enhanced Codex controller prompt

```text
Work on WayLoom Datathon Phase 04 only.

PHASE: Task 1 Training Data & Label Construction
TASK RANGE: DT-055 through DT-071
EXECUTION MODE: TASK-BY-TASK / SMALL CHECKPOINTS

Read:
- WAYLOOM_DATATHON_MASTER_PLAN.md
- approved Phase 00–03 contracts
- PHASE_04_COMPETITION_CONTRACT.md
- tracked schema/data-quality code

Do not read:
data/raw/**
data/interim/**
reports/private/**

Use synthetic data only.

OFFICIAL CONTRACT:
- historical dispatched population = attempted + deferred;
- not_run has no historical delivery outcome;
- join deliveries (route_id, seq_in_route) to route legs (route_id, seq);
- every dispatched order must match exactly one route leg;
- service_start = max(actual arrival, window open);
- service_minutes = leave_outlet - service_start;
- late = 1 only when actual arrival > window_close;
- arrival exactly at close is not late;
- early waiting is not service;
- actual_depart_time, actual_travel_duration_min, arrival_time, leave_outlet_time are training-only actuals and must not become direct prediction features.

CHECKPOINTS:
A: DT-055 + DT-056
B: DT-057
C: DT-058–DT-061
D: DT-062 + DT-063
E: DT-064
F: DT-065
G: DT-066
H: DT-067–DT-069
I: DT-070 + DT-071

At each checkpoint implement only the requested tasks, run synthetic tests, report status, and stop.

RIGHT NOW DO CHECKPOINT A ONLY:

DT-055:
implement a pure dispatched-order selector.

DT-056:
implement eligibility classification.

Requirements:
- retain attempted;
- retain deferred;
- exclude not_run as expected;
- dispatched row missing route assignment = blocker;
- no silent dropping;
- no generic dropna;
- preserve traceability;
- do not mutate inputs.

Add synthetic tests.
Do not implement join code yet.

Return:
CHECKPOINT A
DT-055 PASS/FAIL
DT-056 PASS/FAIL
FILES
TESTS
ISSUES
OFFICIAL DATA ACCESSED: NO
READY FOR CHECKPOINT B: YES/NO

STOP.
```

---

# 16. Enhanced independent Phase 04 review prompt

Run this in a fresh Cursor/Codex chat **after all checkpoints and the human local label build pass**.

```text
Perform an independent review of completed WayLoom Datathon Phase 04.

DO NOT:
- open data/raw
- open data/interim
- open reports/private
- inspect real labels or IDs
- run the real label builder
- modify code initially
- begin the next phase

READ:
- WAYLOOM_DATATHON_MASTER_PLAN.md
- PHASE_04_COMPETITION_CONTRACT.md
- src/task1/labels.py
- scripts/build_task1_labels.py
- tests/test_task1_labels.py
- docs/task1_label_spec.md
- relevant tracked schema/data-quality utilities

HUMAN LOCAL CONTROL RESULT:
LOCAL PHASE 04 LABEL BUILD: <PASS/FAIL>
DISPATCHED ORDERS MATCHED 1:1: <YES/NO>
UNMATCHED DISPATCHED ORDERS: <0/nonzero>
DUPLICATE MATCHES: <0/nonzero>
DESTINATION MISMATCHES: <0/nonzero>
NEGATIVE SERVICE LABELS: <0/nonzero>
LABEL TESTS: <PASS/FAIL>

Do not ask for row-level private reports.

AUDIT:
DT-055 attempted + deferred retained; not_run excluded.
DT-056 no silent dropna; broken dispatched rows fail explicitly.
DT-057 exact official composite join.
DT-058 one-to-one cardinality proven.
DT-059 unmatched dispatched rows block.
DT-060 duplicate matches detected/prevented.
DT-061 outlet_id == to_outlet.
DT-062 strict HH:MM parsing and one local-time convention.
DT-063 deterministic midnight rollover, duration guardrail, cross-midnight window support.
DT-064 service_start = max(arrival, open).
DT-065 service_minutes = leave - service_start; early waiting excluded.
DT-066 strict arrival > close; equality gives 0; no >= bug.
DT-067 hard label invariants.
DT-068 long labels are reviewed but not automatically clipped/dropped.
DT-069 distributions summarized without modelling/resampling.
DT-070 comprehensive official-boundary tests.
DT-071 one canonical reusable builder.

LEAKAGE:
Confirm direct-feature deny-list contains:
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
service_start_dt
service_minutes
late_flag

DATA SAFETY:
- no real rows in tests/docs;
- private outputs ignored;
- raw data not modified;
- script does not print private rows/IDs.

RUN SAFE TESTS ONLY:
pytest -q tests/test_project_setup.py tests/test_data_inventory.py tests/test_data_quality.py tests/test_schema_assertions.py tests/test_task1_labels.py
python -m pip check

Do not run the official-data builder.

RETURN:
| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:
OFFICIAL JOIN: PASS/FAIL
SERVICE LABEL: PASS/FAIL
LATENESS LABEL: PASS/FAIL
MIDNIGHT HANDLING: PASS/FAIL
LEAKAGE PROTECTION: PASS/FAIL
SYNTHETIC TESTS: PASS/FAIL
HUMAN LOCAL BUILD: PASS/FAIL
DATA SAFETY: PASS/FAIL
BLOCKERS: ...
DT-055 ... DT-071: PASS/FAIL each
PHASE 04 REVIEW: PASS/FAIL
READY FOR NEXT PHASE: YES/NO

If FAIL, list exact blockers only.
Do not fix automatically.
Do not start the next phase.
```

---

# 17. Local operator instructions

After all checkpoints pass in synthetic testing:

## 17.1 Verify ignored outputs

```bash
git status
git check-ignore -v data/interim/task1_training_labels.csv
git check-ignore -v reports/private/phase04_task1_labels/build_summary.json
```

## 17.2 Run tests

```bash
pytest -q tests/test_task1_labels.py
```

Optionally:

```bash
pytest -q
```

## 17.3 Run the real label builder locally

```bash
python scripts/build_task1_labels.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output data/interim/task1_training_labels.csv \
  --report-dir reports/private/phase04_task1_labels
```

PowerShell:

```powershell
python scripts/build_task1_labels.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --output data/interim/task1_training_labels.csv --report-dir reports/private/phase04_task1_labels
```

Verify locally:

```text
one-to-one order/leg mapping
unmatched dispatched = 0
duplicate matches = 0
destination mismatches = 0
chronology valid
service_minutes finite and >= 0
late_flag only 0/1
strict equality-at-close behavior covered by tests
```

Then share only sanitized status with the review agent.

---

# 18. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-04-task1-labels
```

Recommended commits:

```text
feat(task1): define dispatched label population
feat(task1): add official order-to-route-leg join
test(task1): enforce join cardinality and destination integrity
feat(task1): add local clock and midnight resolution
feat(task1): implement official service-start label
feat(task1): implement official service-minutes target
feat(task1): implement strict late target
test(task1): add label invariants and boundary tests
refactor(task1): freeze canonical label builder
docs(task1): document official label construction
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
python -m pip check
pytest -q
git status
```

Merge only after local official-data build and independent Phase 04 review both pass.

---

# 19. Global STOP conditions

Do not proceed to later Task 1 analysis/features if any remains unresolved:

- Phase 03 did not pass.
- deferred orders are excluded from historical Task 1 labels.
- not_run orders are included as delivered history.
- a dispatched order is silently dropped.
- official composite join is not used exactly.
- any dispatched order is unmatched.
- any order maps to multiple route legs.
- destination mismatch exists.
- required clock parsing fails.
- midnight chronology is ambiguous.
- actual travel duration contradicts reconstructed chronology.
- `service_start` differs from `max(arrival, window open)`.
- early waiting is included in service time.
- any service label is negative/nonfinite.
- lateness uses `>=` instead of strict `>`.
- arrival exactly at close is labelled late.
- late flag contains values outside `{0,1}`.
- long service targets are silently removed/clipped.
- actual journey fields appear in prediction feature lists.
- target-derived fields appear as direct predictors.
- unit tests fail.
- local official-data label build fails.
- private derived label data is tracked by Git.
- raw official data is modified.
- independent review fails.

---

# 20. Phase 04 Definition of Done

- [ ] DT-055 PASS
- [ ] DT-056 PASS
- [ ] DT-057 PASS
- [ ] DT-058 PASS
- [ ] DT-059 PASS
- [ ] DT-060 PASS
- [ ] DT-061 PASS
- [ ] DT-062 PASS
- [ ] DT-063 PASS
- [ ] DT-064 PASS
- [ ] DT-065 PASS
- [ ] DT-066 PASS
- [ ] DT-067 PASS
- [ ] DT-068 PASS
- [ ] DT-069 PASS
- [ ] DT-070 PASS
- [ ] DT-071 PASS
- [ ] attempted retained
- [ ] deferred retained
- [ ] not_run excluded
- [ ] every dispatched order matches exactly one route leg
- [ ] unmatched dispatched = 0
- [ ] duplicate matches = 0
- [ ] destination mismatches = 0
- [ ] midnight tests pass
- [ ] `service_start = max(arrival, window open)`
- [ ] early waiting excluded
- [ ] service labels finite and nonnegative
- [ ] late rule uses strict `>`
- [ ] exact-close arrival returns 0
- [ ] late labels are binary
- [ ] long labels reviewed without automatic removal
- [ ] target distribution recorded privately
- [ ] canonical label builder exists
- [ ] comprehensive synthetic tests pass
- [ ] leakage deny-list exists
- [ ] local official-data build passes
- [ ] private outputs remain ignored
- [ ] independent review passes
- [ ] no unresolved STOP condition

Only then:

```text
PHASE 04 STATUS: PASS
READY FOR NEXT PHASE: YES
```

Do not automatically begin the next phase.
