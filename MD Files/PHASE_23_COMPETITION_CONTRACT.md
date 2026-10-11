# PHASE 23 — Task 2B Independent Validator

> **Filename:** `PHASE_23_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 23 — Task 2B Independent Validator  
> **Task range:** **DT-320 → DT-330**  
> **Task count:** **11**  
> **Default phase priority:** **P0**  
> **Phase dependency:** **Phase 22**  
> **Phase gate:** **Independent validator passes and organizer `check_allocation.py` passes; checker evidence is saved.**  
> **Execution mode:** Read-only validation of the frozen Phase 22 allocation + local organizer-checker execution + immutable evidence capture.  
> **Do not repair, re-optimize, reorder policy, or manually edit the frozen allocation in this phase.**

---

# 1. Purpose

Phase 23 answers one question:

> **Is the frozen Phase 22 Task 2B allocation independently valid under the official Task 2B feasibility contract, and does it also pass the organizer-supplied `check_allocation.py`?**

Phase 22 created the allocation.

Phase 23 must **not trust the optimizer that created it**.

Instead, Phase 23 builds a separate validation layer that:

1. verifies the allocation structure independently;
2. verifies the official seven hard feasibility rules independently;
3. recomputes the exact official trip-time arithmetic from source references;
4. verifies the Fresh and Style+Tech daily vehicle budgets;
5. builds a private checker-input candidate from the frozen allocation;
6. runs the organizer-supplied `check_allocation.py` locally;
7. saves checker evidence and hashes;
8. blocks Phase 24 if either validator disagrees or fails.

This phase must be **read-only with respect to the frozen allocation**.

If anything is wrong:

```text
DO NOT PATCH THE CSV
DO NOT MANUALLY MOVE ORDERS
DO NOT CHANGE A DECISION
DO NOT CHANGE A VEHICLE/TRIP
```

Instead:

```text
reopen Phase 22
fix the solver/model issue
rerun the full Phase 22 solve
rerun the independent Phase 22 audit
freeze a new allocation
return to Phase 23
```

---

# 2. Finalized Phase 23 task inventory

The finalized WayLoom master inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-320** | [O] | P0 | DT-319 | Build own allocation validator |
| [ ] | **DT-321** | [O] | P0 | Phase 22 | Validate scenario values |
| [ ] | **DT-322** | [O] | P0 | Phase 22 | Validate one row per order_ref |
| [ ] | **DT-323** | [O] | P0 | Phase 22 | Validate decisions are only served/deferred |
| [ ] | **DT-324** | [O] | P0 | Phase 22 | Validate vehicle/trip populated for served |
| [ ] | **DT-325** | [O] | P0 | Phase 22 | Validate vehicle/trip blank for deferred |
| [ ] | **DT-326** | [O] | P0 | Phase 22 | Validate trip IDs 1 or 2 |
| [ ] | **DT-327** | [O] | P0 | Phase 22 | Validate all seven hard rules |
| [ ] | **DT-328** | [O] | P0 | Phase 22 | Validate exact time-budget calculation |
| [ ] | **DT-329** | [O] | P0 | DT-320–DT-328 | Run official `check_allocation.py` |
| [ ] | **DT-330** | [E] | P0 | Phase 22 | Save checker output/evidence |

**Expected Phase 23 tasks:** 11  
**Missing tasks allowed:** 0  
**Phase complete:** [ ]  
**READY FOR PHASE 24:** NO

---

# 3. Official Task 2B source contract

The official Challenge Booklet states that Task 2B requires:

```text
a complete allocation
```

that marks every order:

```text
served
or
deferred
```

and assigns every served order to a:

```text
vehicle
and
trip
```

The official output template uses:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

Official identity rules:

```text
scenario
order_ref
outlet_id
```

are supplied identifiers and must remain unchanged in the final submission.

Official decision rules:

```text
decision = served
→ vehicle_id populated
→ trip_id is 1 or 2
```

```text
decision = deferred
→ vehicle_id blank
→ trip_id blank
```

`order_ref` is the allocation key because:

```text
outlet_id may appear more than once
```

---

# 4. Official scenario facts relevant to validation

Official Scenario S1:

```text
scenario = S1
depot = Peliyagoda
```

The official fleet file identifies vehicles as:

```text
available
in_workshop
```

Only:

```text
available
```

vehicles may be allocated.

A vehicle with:

```text
status = in_workshop
```

must never appear on a served row.

---

# 5. Official seven feasibility rules — validator authority

The independent validator must implement all seven exactly.

## H1 — Brand and district

All orders sharing:

```text
vehicle_id + trip_id
```

must belong to the same:

```text
brand
district
```

## H2 — Refrigeration

```text
temp_requirement = chilled
→ vehicle.temp = reefer
```

Refrigerated vehicles may carry ambient orders.

## H3 — Vehicle access

```text
parking_constraint = van_only
→ vehicle.type = van
```

## H4 — Home depot

A vehicle may serve only orders/outlets assigned to its own home depot.

S1 is Peliyagoda.

## H5 — Whole orders

Each served order must be assigned to exactly:

```text
one vehicle
one trip
```

No splitting.

## H6 — Capacity

For every actual used trip:

```text
sum(order_volume_m3)
<=
vehicle.volume_cap_m3
```

and:

```text
sum(order_weight_kg)
<=
vehicle.weight_cap_kg
```

Both must pass.

## H7 — Trips and time

Each vehicle may run:

```text
at most two trips total
```

and its trip times must satisfy:

```text
Fresh trips combined <= 270 minutes
```

```text
Style + Tech trips combined <= 480 minutes
```

Fresh and Style+Tech are separate windows.

---

# 6. Official trip-time calculation — validator must recompute

For each actual served trip:

```text
trip_minutes
=
outbound travel
+
inter-stop travel
+
total handling time
```

## Outbound

Use:

```text
depot_to_district_freeflow_min
```

from the trip's district reference.

Count it:

```text
once per trip
```

## Inter-stop

Use:

```text
inter_stop_freeflow_min * (number_of_orders - 1)
```

A one-order trip has:

```text
0 inter-stop journeys
```

## Handling

For every order:

```text
brand + dock_type
→ service_allowance_min
```

Sum every order's allowance.

## Return journey

The official booklet explicitly says:

```text
DO NOT ADD THE RETURN JOURNEY
```

because the daily budgets already allow for it.

---

# 7. Official examples retained as regression evidence

Mandatory Phase 23 validator regression test:

```text
Fresh / Gampaha / 3 orders

outbound = 37

inter-stop = 9 * (3 - 1)
           = 18

handling = 15 + 15 + 16
         = 46

trip total = 101
```

Recommended second public regression:

```text
Fresh / Colombo / 4 street orders

24 + (8 * 3) + (16 * 4)
=
112
```

The official example states:

```text
101 + 112 = 213 Fresh minutes
```

which is valid within:

```text
270
```

and a third trip is not allowed.

---

# 8. Organizer checker contract

The official booklet states:

```text
check_allocation.py
```

checks the Task 2B allocation against the feasibility rules and can be run before submission.

The booklet explicitly states:

> Passing these checks confirms that your allocation meets the feasibility rules, not that it is optimal.

Therefore Phase 23 must preserve this distinction:

```text
OWN VALIDATOR PASS
+
OFFICIAL CHECKER PASS
=
FEASIBILITY EVIDENCE
```

It does **not** prove:

```text
optimality
best possible policy
business superiority
```

The frozen Phase 21 policy and Phase 22 lexicographic optimization provide the separate decision-quality rationale.

---

# 9. Important source limitation — checker CLI is not specified by the booklet

The official booklet identifies:

```text
check_allocation.py
```

but does **not** specify its exact command-line arguments in the booklet text.

Therefore:

```text
DO NOT INVENT A CHECKER CLI
```

During implementation, Codex must inspect the locally supplied official:

```text
check_allocation.py
```

source and/or its:

```text
--help
```

behavior **without exposing competition rows**.

Then implement a wrapper that invokes the checker using its actual local interface.

If the checker has:

- fixed relative paths;
- positional arguments;
- flags;
- no CLI at all and expects a file in a known location;

the wrapper must respect that actual official implementation.

Do not rewrite the official checker.

Do not alter its rules.

---

# 10. Phase-ordering note: Phase 23 checker vs Phase 24 final template

The finalized WayLoom master inventory intentionally runs the organizer checker in Phase 23, while Phase 24 creates the canonical final:

```text
outputs/submission_task2b.csv
```

To preserve that order without creating the Phase 24 artifact early, Phase 23 should create a **private checker candidate** derived from the frozen Phase 22 allocation.

Recommended private candidate:

```text
reports/private/phase23_task2b_validator/checker_workspace/submission_task2b.csv
```

It should have the official output schema:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

and be derived read-only from:

```text
data/interim/task2b_final_allocation.csv
```

Phase 24 will later populate/export the canonical official final file after Phase 23 passes.

This private checker candidate is an **engineering bridge required by the phase order**.

It is not the final submission artifact.

---

# 11. Independence requirements

The Phase 23 validator must be independent of the Phase 22 optimizer.

## Allowed reuse

It may reuse canonical non-solver reference/utility code such as:

```text
Phase 18 scenario loaders
Phase 20 pure trip-time calculator
common schema/IO helpers
```

## It must not use as proof

Do not validate by asking:

```text
"did CP-SAT constraint X exist?"
```

Do not validate by reading only:

```text
Phase 22 audit PASS
```

Do not import the CP-SAT model and inspect constraints as the primary validator.

Instead, validate the **extracted frozen allocation itself** against:

```text
official source orders
official fleet
official vehicle reference
official district travel
official service allowance
```

The validator should remain useful even if the Phase 22 solver implementation is replaced.

---

# 12. Read-only frozen-allocation integrity

Before semantic validation:

1. locate:

```text
data/interim/task2b_final_allocation.csv
```

2. locate Phase 22 private:

```text
freeze_manifest.json
```

3. require:

```text
state = FROZEN
```

4. recompute:

```text
SHA256(allocation file)
```

5. compare to Phase 22 freeze manifest.

Recommended also verify:

```text
trip summary SHA256
```

if Phase 23 reads the frozen trip summary.

If the hash differs:

```text
STOP
```

Do not validate a modified allocation.

This is an engineering integrity check, separate from the organizer's feasibility rules.

---

# 13. Recommended repository additions

Create/update:

```text
src/task2b/allocation_validator.py
src/task2b/checker_runner.py
src/task2b/checker_evidence.py

scripts/validate_task2b_allocation.py
scripts/run_official_task2b_checker.py

configs/task2b_validation.yaml

docs/task2b_validation_spec.md

tests/test_task2b_allocation_validator.py
tests/test_task2b_checker_runner.py
tests/test_task2b_checker_evidence.py
```

Reuse but do not modify semantics of:

```text
src/task2b/scenario.py
src/task2b/trip_time.py
src/task2b/solution.py
```

Do not implement Phase 24 final submission export.

---

# 14. Private Phase 23 outputs

Recommended:

```text
reports/private/phase23_task2b_validator/
├── validation_summary.json
├── allocation_identity_audit.json
├── decision_schema_audit.json
├── hard_rule_audit.json
├── trip_time_audit.csv
├── vehicle_budget_audit.csv
├── checker_workspace/
│   └── submission_task2b.csv
├── checker_stdout.txt
├── checker_stderr.txt
├── checker_evidence.json
├── checker_input_sha256.txt
├── official_checker_sha256.txt
├── warnings.json
└── phase23_validation_report.md
```

These are local/private evidence artifacts.

Do not commit them unless a later evidence phase explicitly creates a sanitized derivative.

---

# 15. Recommended validation config

Create:

```text
configs/task2b_validation.yaml
```

Recommended structure:

```yaml
version: 1

scenario:
  expected_id: S1
  expected_depot: Peliyagoda

allocation:
  path: data/interim/task2b_final_allocation.csv
  phase22_freeze_manifest: reports/private/phase22_task2b_optimizer/freeze_manifest.json
  require_frozen_state: true
  require_sha256_match: true

identity:
  key: order_ref
  require_exact_order_set: true
  require_exact_outlet_id_match: true
  require_exact_scenario_match: true

decision:
  allowed_values:
    - served
    - deferred

served:
  require_vehicle_id: true
  allowed_trip_ids:
    - 1
    - 2

deferred:
  require_blank_vehicle_id: true
  require_blank_trip_id: true

time:
  fresh_budget_min: 270
  style_tech_budget_min: 480
  include_return_leg: false

numeric:
  tolerance: 1.0e-9

official_checker:
  source_manifest_key: check_allocation
  inspect_actual_interface: true
  do_not_guess_cli: true
  private_workspace: reports/private/phase23_task2b_validator/checker_workspace

reports:
  private_output_dir: reports/private/phase23_task2b_validator
```

Adapt the checker locator to the actual repository manifest/path layer.

Do not hard-code a checker invocation unsupported by the official file.

---

# 16. Validation result model

Recommended status:

```text
PASS
FAIL
```

Each rule result should include:

```text
rule_id
task_id
status
violation_count
summary
```

Do not expose private `order_ref` values in sanitized console output.

Private violation detail may include IDs locally when necessary for debugging.

If any violation exists:

```text
PHASE 23 VALIDATION = FAIL
```

No "warning-only" downgrade for official hard rules.

---

# 17. DT-320 — Build own allocation validator

## Objective

Create an independent, read-only validator for the frozen Phase 22 allocation.

Recommended main API:

```python
validate_frozen_task2b_allocation(
    allocation,
    orders_s1,
    fleet_s1,
    vehicles_ref,
    district_travel_ref,
    service_allowance_ref,
    config,
) -> AllocationValidationReport
```

The validator must validate the allocation data, not optimizer code.

## Required characteristics

```text
deterministic
read-only
source-grounded
complete
fail-closed
no silent repair
```

## Required layers

1. frozen file/hash integrity;
2. identity/schema;
3. decision semantics;
4. field population;
5. official seven hard rules;
6. exact time arithmetic;
7. vehicle daily budgets;
8. final summary.

## No repair behavior

Do not:

```text
fill missing trip_id
normalize "Served" to "served"
strip an invalid vehicle assignment from a deferred row
drop duplicate order rows
replace wrong scenario with S1
```

Validator detects failures.

It does not fix them.

## Tests

- correct allocation passes;
- one deliberate error fails;
- multiple violations all reported;
- validator does not mutate input;
- validation repeat deterministic.

---

# 18. DT-321 — Validate scenario values

## Official requirement

Final Task 2B scenario is:

```text
S1
```

## Validate

Every frozen allocation row:

```text
scenario == S1
```

Also compare against the canonical S1 order source:

```text
allocation.scenario
==
source.scenario
```

Do not merely overwrite scenario with S1.

## Defensive identity check

Also validate:

```text
outlet_id
```

matches the canonical source row for that `order_ref`.

This identity check is officially required for the final output, although the specific master task "preserve outlet_id" appears again in Phase 24.

Phase 23 should detect a mismatch early.

Do not modify it.

## Tests

- all S1 pass;
- S2 fails;
- blank scenario fails;
- source mismatch fails;
- outlet identity mismatch fails.

---

# 19. DT-322 — Validate one row per order_ref

## Official key

```text
order_ref
```

is the unique allocation key.

## Validate exact set equality

Let:

```text
expected = set(S1 source order_ref)
actual = set(frozen allocation order_ref)
```

Require:

```text
actual == expected
```

and:

```text
len(allocation) == len(expected)
```

and:

```text
order_ref unique
```

Detect separately:

```text
missing order_ref
extra order_ref
duplicate order_ref
blank order_ref
```

Do not collapse duplicate `outlet_id`.

Two different `order_ref` values for the same outlet are valid.

## Tests

- exact set pass;
- duplicate fails;
- missing fails;
- extra fails;
- blank fails;
- repeated outlet with different order_refs passes.

---

# 20. DT-323 — Validate decisions are only served/deferred

Allowed exact values:

```text
served
deferred
```

Require every row to contain exactly one of those values.

Do not accept:

```text
Serve
Served
DEFERRED
pending
unknown
blank
placeholder
(served/deferred)
```

The validator must not auto-normalize.

## Tests

- served pass;
- deferred pass;
- capitalization fail;
- placeholder fail;
- blank fail;
- extra whitespace fail unless the canonical writer already guarantees normalized values.

Recommended strict policy:

```text
value must already be canonical
```

---

# 21. DT-324 — Validate vehicle/trip populated for served

For every:

```text
decision == served
```

require:

```text
vehicle_id is nonblank
trip_id is nonblank
```

Additionally:

```text
vehicle_id exists in task2b_peak_day_fleet.csv
vehicle_id exists in vehicles.csv
```

Availability is validated under hard rules.

Do not treat:

```text
""
" "
NaN
None
placeholder
```

as valid populated values.

## Tests

- valid served row;
- missing vehicle fails;
- missing trip fails;
- both missing fails;
- unknown vehicle fails.

---

# 22. DT-325 — Validate vehicle/trip blank for deferred

For every:

```text
decision == deferred
```

require:

```text
vehicle_id blank
trip_id blank
```

Canonical blank semantics may include in-memory:

```text
None
NaN
empty string
whitespace-only
```

for **validation detection**, but the checker candidate writer should serialize deferred fields as truly empty CSV fields.

Do not accept:

```text
vehicle_id populated but "ignored"
trip_id populated but "ignored"
0
-
N/A
placeholder
```

as canonical final values.

## Tests

- both blank pass;
- vehicle populated fails;
- trip populated fails;
- placeholder fails;
- numeric zero fails.

---

# 23. DT-326 — Validate trip IDs 1 or 2

For every served row:

```text
trip_id ∈ {1,2}
```

The internal parsed value may be numeric integer-like, but checker candidate output must canonicalize it to:

```text
1
2
```

only after validation.

Reject:

```text
0
3
-1
1.5
"trip1"
```

Deferred rows must remain blank.

## Important

Do **not** add an unofficial rule:

```text
trip 2 requires trip 1
```

Phase 22 used that as a safe symmetry breaker, but it is **not** one of the seven official feasibility rules.

The independent Phase 23 validator should not fail an otherwise official-feasible allocation solely because a vehicle uses only trip 2.

## Tests

- served trip 1 pass;
- served trip 2 pass;
- trip 0 fail;
- trip 3 fail;
- noninteger fail;
- deferred blank pass.

---

# 24. DT-327 — Validate all seven hard rules

This task is the core of Phase 23.

The validator must recompute every rule from the frozen allocation and official source/reference data.

---

## 24.1 Hard Rule 1 — same brand + district per trip

Group served rows by:

```text
vehicle_id
trip_id
```

Join each `order_ref` to canonical S1 order data.

For every group require:

```text
brand.nunique() == 1
district.nunique() == 1
```

Do not trust brand/district columns copied into an allocation.

Use canonical source order facts.

Fail on:

```text
mixed brand
mixed district
```

---

## 24.2 Hard Rule 2 — refrigeration

For each served row:

join source order:

```text
temp_requirement
```

and vehicle reference:

```text
temp
```

Require:

```text
if order temp_requirement == chilled:
    vehicle temp == reefer
```

Ambient on reefer:

```text
PASS
```

Do not over-restrict.

---

## 24.3 Hard Rule 3 — van-only access

For each served row:

```text
if parking_constraint == van_only:
    vehicle.type == van
```

Normal-access order on van:

```text
PASS
```

---

## 24.4 Hard Rule 4 — home depot

For each served row:

```text
vehicle.home_depot == order.depot
```

Use exact official vehicle-reference home-depot field.

S1 expected:

```text
Peliyagoda
```

Also validate assigned vehicle is:

```text
status == available
```

in scenario fleet and never:

```text
in_workshop
```

Availability is a scenario requirement and must be part of Phase 23 feasibility evidence.

---

## 24.5 Hard Rule 5 — whole orders

Phase 23's one-row-per-`order_ref` validation and served assignment fields should already imply one assignment.

Still explicitly validate:

```text
every served order appears in exactly one vehicle+trip
```

and:

```text
no served order is represented more than once
```

No partial/split representation exists.

---

## 24.6 Hard Rule 6 — capacity

For every served:

```text
vehicle_id + trip_id
```

group, compute from canonical source order rows:

```text
total_weight_kg
=
sum(order_weight_kg)
```

```text
total_volume_m3
=
sum(order_volume_m3)
```

Join vehicle capacities:

```text
weight_cap_kg
volume_cap_m3
```

Require:

```text
total_weight_kg
<=
weight_cap_kg
```

and:

```text
total_volume_m3
<=
volume_cap_m3
```

Equality is valid.

Use deterministic numeric handling.

Do not subtract an arbitrary safety margin.

---

## 24.7 Hard Rule 7 — trips and time

For every vehicle:

### Trip count

Count nonempty distinct:

```text
trip_id
```

Require:

```text
<= 2
```

Because served trip IDs are already restricted to 1/2, this should hold, but validate it independently.

### Fresh budget

Recompute every used trip time.

Then for each vehicle:

```text
sum(trip_minutes where trip brand == Fresh)
<=
270
```

### Style+Tech budget

For each vehicle:

```text
sum(trip_minutes where trip brand in {Style, Tech})
<=
480
```

Style and Tech share the same 480 budget.

Fresh is separate.

---

# 25. DT-328 — Validate exact time-budget calculation

DT-327 checks the budget rule.

DT-328 must prove the arithmetic itself is correct.

For every used trip:

1. get canonical brand and district;
2. count orders;
3. get outbound district travel;
4. get inter-stop district travel;
5. get every order's service allowance using:

```text
brand + dock_type
```

6. compute:

```text
outbound
```

7. compute:

```text
inter_stop * (n_orders - 1)
```

8. compute:

```text
sum handling
```

9. calculate:

```text
trip_minutes
```

10. assert:

```text
return_minutes_added = 0
```

Recommended to call the Phase 20 pure:

```text
calculate_trip_time(...)
```

because Phase 20 is independent of the Phase 22 optimizer.

But Phase 23 should still test the Phase 20 function against the public 101/112 examples.

## Vehicle budget table

Produce private:

```text
vehicle_budget_audit.csv
```

Recommended fields:

```text
vehicle_id
trip_count

fresh_trip_count
fresh_minutes
fresh_budget_min
fresh_budget_ok

style_trip_count
tech_trip_count
style_tech_minutes
style_tech_budget_min
style_tech_budget_ok

overall_budget_ok
```

Do not print real vehicle IDs to the sanitized console.

## Tests

- one trip;
- two Fresh trips combined;
- Fresh + Style;
- Style + Tech combined;
- exact 270;
- 271 fail;
- exact 480;
- 481 fail;
- 101 example;
- 112 example;
- no return.

---

# 26. Identity checks beyond the explicit Phase 23 tasks

These are defensive preflight checks, not new master tasks.

Validate:

```text
allocation scenario unchanged

allocation order_ref unchanged

allocation outlet_id matches source
```

Also recommended:

```text
source row count unchanged

no unexpected columns required for feasibility
```

Do not fail merely because the private frozen allocation contains additional internal diagnostic columns, if it does.

For the official checker candidate, write only the official six columns.

---

# 27. Validator must not enforce Phase 21 policy as feasibility

The Phase 23 independent validator validates **feasibility**, not business policy optimality.

Do not fail the allocation because:

```text
a Fresh order is deferred

a Style order is served before a Fresh order

a previously-deferred order remains deferred

a low-flexibility order remains deferred

a reefer carries ambient demand
```

if the official hard rules still pass.

Phase 22 objective optimality was frozen separately.

Phase 23 may verify Phase 22 freeze integrity, but it should not reinterpret policy as an eighth official rule.

---

# 28. Validator must not import non-Task2B constraints

Do not add hard validation for:

```text
fuel quota

Task 1 predicted lateness

Task 1 service time

delivery windows

mall window

traffic_speed

road_conditions

return journey

Hackathon route distance
```

unless the official Task 2B feasibility section/checker explicitly uses them.

The official Task 2B seven-rule contract is the validator authority.

---

# 29. Validation report schema

Recommended `AllocationValidationReport`:

```text
overall_status

frozen_integrity_status

identity_status

decision_status

field_population_status

hard_rules_status

time_budget_status

violation_counts_by_rule

used_trip_count

checked_order_count

checked_vehicle_count

checked_trip_count
```

Private detailed objects can include violating IDs.

Sanitized console should print only counts/status.

---

# 30. Checker-candidate builder

Implement a dedicated read-only transform:

```python
build_official_checker_candidate(
    frozen_allocation,
    canonical_orders_s1,
) -> pd.DataFrame
```

Exact output columns:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

Requirements:

```text
one row per order_ref

identity values sourced/verified against canonical S1 orders

decision copied from frozen allocation

served assignment copied from frozen allocation

deferred vehicle/trip serialized blank

trip IDs canonical 1 or 2

no placeholders

no debug columns
```

Do not change a decision.

Do not reassign any order.

Do not fill a missing field "to make the checker pass."

If the frozen allocation cannot be converted losslessly:

```text
FAIL BEFORE CHECKER
```

---

# 31. DT-329 — Run official `check_allocation.py`

## Preconditions

Run only if:

```text
DT-320 PASS
DT-321 PASS
DT-322 PASS
DT-323 PASS
DT-324 PASS
DT-325 PASS
DT-326 PASS
DT-327 PASS
DT-328 PASS
```

Do not run the checker as a substitute for your own validator.

## Official checker source

Locate the organizer-supplied:

```text
check_allocation.py
```

using the repository/data manifest or documented project path.

## Determine actual interface

Before implementation freeze:

- inspect official checker source;
- inspect `--help` if supported;
- identify required input filename/path;
- identify any required working directory/reference paths;
- identify exit-code behavior;
- identify PASS/FAIL output markers.

Do not modify checker.

Do not copy its validation logic into your own validator as the sole implementation.

## Private checker workspace

Stage the checker candidate locally in:

```text
reports/private/phase23_task2b_validator/checker_workspace/
```

If the official checker expects a specific filename such as:

```text
submission_task2b.csv
```

use that filename **inside the private checker workspace**.

Do not create:

```text
outputs/submission_task2b.csv
```

yet.

## Run via subprocess

Recommended wrapper behavior:

```text
capture stdout
capture stderr
capture exit code
record command/interface
record checker path/hash
record candidate hash
```

Do not stream private row-level diagnostics into an external agent.

## PASS determination

Use the actual official checker behavior.

Prefer:

```text
documented exit code
+
documented PASS marker
```

if both exist.

Do not infer PASS merely because Python returned no exception if the checker explicitly prints failures.

## Official meaning

Checker PASS proves:

```text
feasibility under official checker
```

not:

```text
optimality
```

---

# 32. Official checker must remain unmodified

Before running:

```text
compute SHA256(check_allocation.py)
```

Record it.

Recommended:

```text
official_checker_sha256
```

in evidence.

Do not:

```text
patch checker
comment out a rule
change tolerance
change source paths to use altered data
monkeypatch checker logic
```

If the official checker itself crashes due to a genuine environment issue:

```text
record evidence
fix environment/path invocation only
rerun unchanged checker
```

If its rule behavior conflicts with the booklet:

```text
STOP FOR HUMAN REVIEW
```

Do not silently alter your validator or checker.

---

# 33. Cross-validator consistency rules

## Own validator PASS + official checker PASS

Required successful state.

## Own validator FAIL + official checker FAIL

Phase 23 fails.

Reopen Phase 22 as required.

## Own validator PASS + official checker FAIL

Blocker.

Possible causes:

- own validator missed a rule;
- checker candidate shape is wrong;
- checker invocation/environment is wrong;
- official checker has additional implementation expectations.

Investigate without editing the frozen allocation.

Do not weaken the official checker.

## Own validator FAIL + official checker PASS

Blocker.

Possible causes:

- own validator is over-strict;
- own validator accidentally imported a nonofficial rule;
- numeric interpretation differs.

Investigate against the official source.

Do not loosen the validator merely because checker passes unless the official contract supports the correction.

Both validators must agree before Phase 24.

---

# 34. DT-330 — Save checker output/evidence

Save immutable private evidence from the successful official checker run.

Recommended files:

```text
checker_stdout.txt

checker_stderr.txt

checker_evidence.json

checker_input_sha256.txt

official_checker_sha256.txt
```

Recommended `checker_evidence.json`:

```json
{
  "phase": 23,
  "task": "DT-330",
  "checker": "check_allocation.py",
  "checker_sha256": "...",
  "checker_input_sha256": "...",
  "frozen_allocation_sha256": "...",
  "phase22_freeze_manifest_sha256": "...",
  "python_version": "...",
  "working_directory": "...",
  "invocation_mode": "...",
  "exit_code": 0,
  "pass_detected": true,
  "stdout_sha256": "...",
  "stderr_sha256": "...",
  "timestamp": "...",
  "git_commit": "...",
  "own_validator_status": "PASS",
  "official_checker_status": "PASS"
}
```

Do not invent:

```text
exit_code = 0
```

as a universal PASS rule if the actual checker interface says otherwise.

The evidence builder must use the actual checker semantics discovered in DT-329.

---

# 35. Evidence immutability

After successful Phase 23 completion:

- hash checker input;
- hash checker source;
- hash raw stdout/stderr;
- hash evidence JSON if useful;
- record Phase 22 frozen allocation hash.

Do not overwrite evidence silently.

Recommended rerun behavior:

```text
new run → new timestamped evidence subdirectory
```

or:

```text
refuse overwrite unless --new-run / explicit flag
```

The latest successful evidence may be referenced by a small private pointer/manifest.

---

# 36. Recommended files for implementation

Create:

```text
src/task2b/allocation_validator.py
src/task2b/checker_runner.py
src/task2b/checker_evidence.py

scripts/validate_task2b_allocation.py
scripts/run_official_task2b_checker.py

configs/task2b_validation.yaml

docs/task2b_validation_spec.md

tests/test_task2b_allocation_validator.py
tests/test_task2b_checker_runner.py
tests/test_task2b_checker_evidence.py
```

Potential reuse:

```text
src/task2b/trip_time.py
src/common/io.py
src/common/validation.py
```

Do not edit the official `check_allocation.py`.

---

# 37. Required synthetic tests — allocation identity/schema

Create synthetic tests for:

```text
scenario exact S1

one row per order_ref

duplicate order_ref fail

missing order_ref fail

extra order_ref fail

blank order_ref fail

repeated outlet_id allowed

outlet_id source mismatch fail

decision only served/deferred

capitalized decision fail

placeholder decision fail

blank decision fail
```

---

# 38. Required synthetic tests — served/deferred fields

## Served

Test:

```text
vehicle populated
trip populated
known vehicle
trip 1
trip 2
```

Failures:

```text
missing vehicle
missing trip
unknown vehicle
```

## Deferred

Test both blank passes.

Failures:

```text
vehicle populated
trip populated
placeholder
zero
```

---

# 39. Required synthetic tests — all seven hard rules

Build a valid base allocation, then mutate one rule at a time.

Required deliberate violations:

```text
mixed brand on one vehicle+trip

mixed district on one vehicle+trip

chilled on dry/ambient vehicle

van_only on truck

wrong home depot

served order duplicated/split

trip overweight

trip over volume

vehicle uses invalid/extra trip

Fresh vehicle total = 271

Style+Tech vehicle total = 481
```

Every mutation must be detected.

Also include exact-boundary passes:

```text
weight == capacity

volume == capacity

Fresh == 270

Style+Tech == 480
```

---

# 40. Required synthetic tests — trip-time arithmetic

Test:

```text
one-order trip
two-order trip
three-order trip
repeated outlet IDs
mixed dock types
```

Mandatory public regressions:

```text
Gampaha = 101
Colombo = 112
```

No return.

Test:

```text
outbound counted once

inter-stop uses orders-1

handling uses brand+dock

handling sums every order
```

---

# 41. Required tests — official checker runner

Do not require real competition data in automated Codex tests.

Create synthetic/mock checker scripts for wrapper behavior.

Test runner handles:

```text
successful checker

nonzero exit

PASS marker

FAIL marker

stdout capture

stderr capture

checker timeout

missing checker file

unexecutable/invalid Python checker

working directory

candidate path with spaces

hash calculation
```

Then locally, the human runs the real official checker.

Do not mock the **final evidence** as if it were organizer proof.

Synthetic runner tests prove the wrapper only.

---

# 42. Required tests — checker evidence

Test:

```text
checker SHA256 correct

candidate SHA256 correct

stdout/stderr hashes correct

evidence status derived from real runner result

own validator PASS required

official checker PASS required

timestamp present

git commit optional but recorded when available

evidence overwrite protection
```

Do not write fake PASS evidence from a failed runner.

---

# 43. End-to-end synthetic validation test

Construct a synthetic scenario/reference set and a valid frozen-allocation fixture.

Run:

```text
freeze-hash verification
→ own validator
→ checker-candidate builder
→ synthetic/mock official checker
→ evidence builder
```

Expected:

```text
own validator PASS
checker runner PASS
evidence PASS
```

Then introduce one violation.

Expected:

```text
own validator FAIL
official checker stage not run
or explicitly blocked
```

This validates the Phase 23 sequencing.

---

# 44. Edge cases

## Empty served set

A complete all-deferred allocation can be structurally feasible if every row has:

```text
decision = deferred
vehicle blank
trip blank
```

Phase 23 validates feasibility, not policy optimality.

Therefore do not fail it solely because no orders are served.

Phase 22 lexicographic optimality is responsible for avoiding a poor all-deferred plan when service is feasible.

---

## Trip 2 without trip 1

Official Task 2B only says trip ID is 1 or 2 and max two trips.

Phase 23 must not invent:

```text
trip 2 requires trip 1
```

as an official validation rule.

The Phase 22 symmetry breaker may prevent this in practice, but the independent official-rule validator should not rely on it.

---

## Reefer used for ambient

Valid.

Do not fail.

---

## Van used for normal-access order

Valid.

Do not fail.

---

## Same vehicle has Fresh trip and Style/Tech trip

Valid if:

```text
trip count <= 2

Fresh total <=270

Style+Tech total <=480
```

---

## Same vehicle has one Style and one Tech trip

Valid if their combined time:

```text
<=480
```

---

## Same vehicle has two Fresh trips

Valid if combined Fresh:

```text
<=270
```

---

## Duplicate outlet_id with distinct order_ref

Valid.

Each order is independently validated.

---

## Unknown vehicle on deferred row

If vehicle field is truly blank:

not applicable.

If populated:

DT-325 already fails.

---

## Whitespace in deferred fields

Validator may identify whitespace-only as blank-like for diagnostics, but the canonical checker candidate writer should output a truly empty field.

Do not use whitespace as final canonical content.

---

# 45. Numerical comparison policy

Official capacity/time rules are non-strict:

```text
<=
```

Exact boundaries pass.

Because the source values may be decimal, use a deterministic numeric strategy.

Preferred:

```text
Decimal(str(value))
```

for validator arithmetic where practical.

Alternative:

reuse the exact Phase 20 numeric representation.

Do not introduce a large tolerance that effectively increases vehicle capacity/time budget.

If a float tolerance is used for presentation-level comparison:

```text
1e-9
```

or similarly tight representation-only tolerance is appropriate.

Document it.

---

# 46. Official checker invocation implementation

Because the booklet does not define exact CLI flags, implement the wrapper with an explicit discovery step.

Recommended:

```python
OfficialCheckerInterface
```

fields:

```text
checker_path
invocation_kind
candidate_argument_mode
working_directory
expected_success_semantics
timeout_seconds
```

On first configuration:

1. locate checker;
2. inspect official source/`--help`;
3. store the discovered local invocation method in `configs/task2b_validation.yaml`;
4. add a small tracked note in `docs/task2b_validation_spec.md`;
5. never modify official checker code.

If exact invocation cannot be determined safely:

```text
STOP
```

Ask the human to inspect the official checker.

Do not guess.

---

# 47. Suggested local own-validator command

Implement:

```bash
python scripts/validate_task2b_allocation.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --validation-config configs/task2b_validation.yaml \
  --allocation data/interim/task2b_final_allocation.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --report-dir reports/private/phase23_task2b_validator
```

PowerShell one-line:

```powershell
python scripts/validate_task2b_allocation.py --raw-root data/raw --manifest configs/dataset_manifest.yaml --scenario-config configs/task2b_scenario.yaml --validation-config configs/task2b_validation.yaml --allocation data/interim/task2b_final_allocation.csv --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json --report-dir reports/private/phase23_task2b_validator
```

Do not print private order IDs in normal console output.

---

# 48. Suggested official-checker wrapper command

Because the actual organizer checker CLI must be discovered from the supplied file, use a WayLoom wrapper command whose own interface is stable:

```bash
python scripts/run_official_task2b_checker.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --validation-config configs/task2b_validation.yaml \
  --allocation data/interim/task2b_final_allocation.csv \
  --report-dir reports/private/phase23_task2b_validator
```

The wrapper must internally invoke the organizer checker using the **actual discovered official interface**.

Do not hard-code an invented direct command such as:

```text
python check_allocation.py --submission ...
```

unless inspection of the supplied official file confirms that exact interface.

---

# 49. Recommended sanitized own-validator output

Target:

```text
WAYLOOM — TASK 2B INDEPENDENT VALIDATION

PHASE22 FROZEN HASH                 : PASS

SCENARIO VALUES                     : PASS
ORDER_REF EXACT COVERAGE            : PASS
ORDER_REF UNIQUENESS                : PASS
OUTLET_ID SOURCE CONSISTENCY        : PASS

DECISION DOMAIN                     : PASS
SERVED FIELD POPULATION             : PASS
DEFERRED FIELD BLANKNESS            : PASS
TRIP ID DOMAIN {1,2}                : PASS

RULE 1 BRAND + DISTRICT             : PASS
RULE 2 REFRIGERATION                : PASS
RULE 3 VAN-ONLY ACCESS              : PASS
RULE 4 HOME DEPOT / AVAILABILITY    : PASS
RULE 5 WHOLE ORDERS                 : PASS
RULE 6 WEIGHT + VOLUME              : PASS
RULE 7 TRIPS + TIME                 : PASS

EXACT TRIP-TIME CALCULATION         : PASS
RETURN LEG ADDED                    : NO

FRESH >270 VIOLATIONS               : 0
STYLE+TECH >480 VIOLATIONS          : 0

TASK 2B OWN VALIDATOR               : PASS
READY FOR OFFICIAL CHECKER          : YES
```

No private IDs.

---

# 50. Recommended sanitized official-checker output

The wrapper may print:

```text
WAYLOOM — OFFICIAL TASK 2B CHECKER

CHECKER FILE FOUND                  : PASS
CHECKER SHA256 CAPTURED             : PASS
PRIVATE CHECKER CANDIDATE BUILT     : PASS
CHECKER CANDIDATE SHA256            : PASS
OFFICIAL CHECKER EXECUTED           : PASS
OFFICIAL CHECKER RESULT             : PASS
RAW CHECKER EVIDENCE SAVED          : PASS

OWN VALIDATOR                       : PASS
OFFICIAL CHECKER                    : PASS

PHASE 23 VALIDATION                 : PASS
READY FOR PHASE 24                  : YES
```

Do not suppress raw official checker output from evidence storage.

Just avoid dumping private violation details into the external-agent chat.

---

# 51. Phase 23 STOP conditions

`READY FOR PHASE 24` remains **NO** if any of the following occurs:

- Phase 22 allocation is not frozen;
- Phase 22 freeze hash does not match the allocation;
- scenario is not exactly S1;
- allocation contains missing/extra/duplicate `order_ref`;
- `outlet_id` does not match canonical source;
- decision outside `served/deferred`;
- served row lacks vehicle;
- served row lacks trip;
- deferred row has vehicle;
- deferred row has trip;
- served trip ID outside 1/2;
- assigned vehicle is unknown;
- assigned vehicle is not `available`;
- assigned vehicle is `in_workshop`;
- one trip mixes brands;
- one trip mixes districts;
- chilled order uses non-reefer;
- van-only order uses truck;
- vehicle home depot mismatch;
- whole order is split/duplicated;
- trip weight exceeds capacity;
- trip volume exceeds capacity;
- vehicle uses more than two trips;
- exact trip arithmetic is wrong;
- return leg is added;
- Fresh vehicle minutes exceed 270;
- Style+Tech vehicle minutes exceed 480;
- public 101-minute regression fails;
- own validator modifies the allocation;
- private checker candidate cannot be derived losslessly;
- exact official checker interface is unknown and would need guessing;
- official checker source is modified;
- official checker crashes due to unresolved invocation/environment;
- own validator and official checker disagree;
- official checker fails;
- checker evidence is not saved;
- checker source/input hashes are missing;
- evidence falsely claims PASS;
- Phase 24 final output is created prematurely;
- Task 1 frozen artifacts change;
- Task 2A frozen artifacts change;
- Phase 22 allocation is manually patched;
- private rows must be exposed to an external agent;
- safe tests fail;
- `python -m pip check` fails;
- independent review fails.

---

# 52. Definition of Done

Phase 23 is complete only when:

- [ ] DT-320 PASS
- [ ] DT-321 PASS
- [ ] DT-322 PASS
- [ ] DT-323 PASS
- [ ] DT-324 PASS
- [ ] DT-325 PASS
- [ ] DT-326 PASS
- [ ] DT-327 PASS
- [ ] DT-328 PASS
- [ ] DT-329 PASS
- [ ] DT-330 PASS
- [ ] Phase 22 frozen state confirmed
- [ ] allocation SHA256 matches Phase 22 freeze manifest
- [ ] validator is read-only
- [ ] exact S1 scenario validated
- [ ] exact `order_ref` set validated
- [ ] `order_ref` uniqueness validated
- [ ] repeated `outlet_id` permitted
- [ ] source `outlet_id` consistency validated
- [ ] decision domain exact
- [ ] served assignment fields valid
- [ ] deferred assignment fields blank
- [ ] served trip IDs only 1/2
- [ ] no unofficial trip2→trip1 rule added
- [ ] all seven official hard rules pass
- [ ] assigned vehicles are available/not workshop
- [ ] exact weight capacity validation passes
- [ ] exact volume capacity validation passes
- [ ] exact Phase 20 trip arithmetic passes
- [ ] no return journey
- [ ] Fresh per-vehicle total ≤270
- [ ] Style+Tech per-vehicle total ≤480
- [ ] official 101-minute regression passes
- [ ] recommended 112-minute regression passes
- [ ] checker candidate is losslessly derived
- [ ] checker candidate uses only official six columns
- [ ] actual official checker interface inspected, not guessed
- [ ] official checker source remains unchanged
- [ ] official checker runs locally
- [ ] official checker returns PASS
- [ ] own validator and official checker agree
- [ ] checker source SHA256 saved
- [ ] checker input SHA256 saved
- [ ] checker stdout/stderr saved
- [ ] checker evidence JSON saved
- [ ] no final `outputs/submission_task2b.csv` yet
- [ ] synthetic validator tests pass
- [ ] synthetic checker-runner tests pass
- [ ] full safe repository suite passes
- [ ] `python -m pip check` passes
- [ ] private outputs ignored
- [ ] Task 1 remains frozen
- [ ] Task 2A remains frozen
- [ ] Phase 22 allocation remains unchanged
- [ ] independent Phase 23 review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 23 STATUS: PASS
OWN TASK 2B VALIDATOR: PASS
OFFICIAL check_allocation.py: PASS
CHECKER EVIDENCE: SAVED
READY FOR PHASE 24: YES
```

---

# 53. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-23-task2b-validator
```

Recommended commits:

```text
feat(task2b): add independent allocation validator
test(task2b): cover official Task 2B feasibility rules
feat(task2b): add official checker runner
feat(task2b): add immutable checker evidence capture
docs(task2b): document independent validation and checker contract
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

Ensure none of these are staged:

```text
data/raw/**
data/interim/**
reports/private/**
outputs/submission_task1.csv
outputs/submission_task2a.csv
```

Also ensure Phase 23 has **not** created or staged:

```text
outputs/submission_task2b.csv
```

Merge only after:

```text
LOCAL PHASE 23 OWN VALIDATOR: PASS
LOCAL OFFICIAL CHECKER: PASS
INDEPENDENT PHASE 23 REVIEW: PASS
```

---

# 54. Recommended Codex model

Phase 23 is high-stakes but less algorithmically complex than Phase 22.

The difficult parts are:

- keeping the validator genuinely independent;
- exact seven-rule revalidation;
- exact time-budget recomputation;
- safely discovering the real organizer checker interface;
- preserving frozen-allocation immutability;
- evidence hashing and disagreement handling.

Recommended:

```text
GPT-5.6 Terra
Reasoning: High
```

Escalate to:

```text
GPT-5.6 Sol
Reasoning: High
```

only if the official checker interface/environment or independent-rule audit becomes difficult.

A low-reasoning model is not recommended for the first implementation of this phase.

---

# 55. Ready-to-copy Codex / Cursor implementation prompt

```text
You are implementing WayLoom Datathon PHASE 23 only.

PHASE:
Task 2B Independent Validator

TASK RANGE:
DT-320 through DT-330

EXECUTION MODE:
HIGH-INTEGRITY READ-ONLY VALIDATION PHASE with full SAFE engineering autonomy.

RECOMMENDED MODEL:
GPT-5.6 Terra — High reasoning

ESCALATE IF NEEDED:
GPT-5.6 Sol — High reasoning

Do NOT start Phase 24.

==================================================
MISSION
==================================================

Independently validate the FROZEN Phase22 Task2B allocation against the
official Task2B contract.

Then run the organizer-supplied:

check_allocation.py

locally using its ACTUAL supplied interface.

Save immutable private checker evidence.

Do NOT:

repair allocation

re-optimize

change decisions

move orders

change vehicles

change trip IDs

change Phase21 policy

edit the official checker

generate final outputs/submission_task2b.csv

==================================================
READ FIRST
==================================================

Read with targeted context:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase23
4. PHASE_18_COMPETITION_CONTRACT.md
5. PHASE_19_COMPETITION_CONTRACT.md
6. PHASE_20_COMPETITION_CONTRACT.md
7. PHASE_21_COMPETITION_CONTRACT.md
8. PHASE_22_COMPETITION_CONTRACT.md
9. PHASE_23_COMPETITION_CONTRACT.md

Inspect canonical Task2B modules:

10. src/task2b/scenario.py
11. src/task2b/trip_time.py
12. src/task2b/solution.py

Inspect:

13. configs/task2b_scenario.yaml
14. configs/task2b_trip_time.yaml
15. configs/task2b_optimizer.yaml
16. Phase22 freeze workflow implementation
17. relevant Task2B tests

Locate the organizer-supplied:

check_allocation.py

You MAY inspect the official checker source and its --help behavior.

Do NOT edit it.

Do NOT run it on private real data inside external-agent context.

==================================================
SOURCE AUTHORITY
==================================================

Official Task2B source rules:

- complete allocation
- every order served/deferred
- served gets vehicle + trip
- deferred vehicle/trip blank
- order_ref is allocation key
- S1 only
- only available vehicles
- seven official hard rules
- exact official trip-time formula
- Fresh <=270 per vehicle
- Style+Tech <=480 per vehicle
- no return journey

Official checker PASS confirms feasibility, NOT optimality.

Do not validate Phase21 preference as an eighth hard rule.

==================================================
TASK1/TASK2A FREEZE
==================================================

Do NOT modify:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

configs/task2a_final_models.yaml
outputs/submission_task2a.csv

Do not modify the Phase22 frozen allocation either.

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do NOT inspect or print real private rows from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for all agent-run tests.

The human will run the real Phase23 validation and checker locally.

Normal console output must be sanitized.

No real:

order_ref
vehicle assignments
trip membership
deferred order lists

in external-agent output.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2b/allocation_validator.py

src/task2b/checker_runner.py

src/task2b/checker_evidence.py

scripts/validate_task2b_allocation.py

scripts/run_official_task2b_checker.py

configs/task2b_validation.yaml

docs/task2b_validation_spec.md

tests/test_task2b_allocation_validator.py

tests/test_task2b_checker_runner.py

tests/test_task2b_checker_evidence.py

Do NOT create:

outputs/submission_task2b.csv

Phase24 owns the canonical final output.

==================================================
FROZEN ALLOCATION INTEGRITY
==================================================

Before semantic validation:

require Phase22 freeze manifest

require:
state = FROZEN

recompute SHA256 of:

data/interim/task2b_final_allocation.csv

compare with Phase22 recorded allocation hash

If mismatch:
FAIL / STOP.

Do not validate a tampered file.

If using frozen trip summary, verify its hash too.

This is an engineering integrity precheck.

==================================================
DT-320 — OWN INDEPENDENT VALIDATOR
==================================================

Build a deterministic READ-ONLY validator.

Validate the extracted allocation against canonical source/reference
tables.

Do NOT validate by inspecting CP-SAT model constraints.

Allowed reuse:

Phase18 source loaders

Phase20 pure trip-time calculator

common IO/schema utilities

Do not use:
"Phase22 audit said PASS"
as proof.

Validator layers:

1 frozen hash

2 identity

3 decision domain

4 served/deferred field rules

5 all seven hard rules

6 exact time arithmetic

7 vehicle budget aggregation

8 final PASS/FAIL

Validator must NOT mutate/fix its input.

==================================================
DT-321 — SCENARIO VALUES
==================================================

Require every allocation row:

scenario == S1

Also verify against canonical S1 source.

Defensively verify:

outlet_id matches the canonical source row for order_ref.

Do not overwrite wrong identity values.

==================================================
DT-322 — ONE ROW PER ORDER_REF
==================================================

order_ref is canonical key.

Require:

nonblank

unique

exact same set as official S1 source

no missing

no extra

same row count

Duplicate outlet_id with different order_refs is VALID.

Do not collapse by outlet_id.

==================================================
DT-323 — DECISION DOMAIN
==================================================

Allowed exact canonical values:

served

deferred

Reject:

Served

DEFERRED

pending

blank

placeholder

(served/deferred)

Do not auto-normalize invalid values.

==================================================
DT-324 — SERVED FIELDS
==================================================

For decision == served:

vehicle_id nonblank

trip_id nonblank

vehicle exists in scenario fleet

vehicle exists in vehicles.csv

Do not fill missing fields.

==================================================
DT-325 — DEFERRED FIELDS
==================================================

For decision == deferred:

vehicle_id blank

trip_id blank

Reject placeholder/0/N-A values.

Checker candidate writer should serialize truly empty CSV fields.

==================================================
DT-326 — TRIP ID 1 OR 2
==================================================

For served:

trip_id must be exactly integer-like 1 or 2.

Deferred:
blank.

Do NOT add an unofficial rule that trip2 requires trip1.

Phase22 symmetry breaking is not an official validation rule.

==================================================
DT-327 — ALL SEVEN HARD RULES
==================================================

Independently recompute from canonical source/reference data.

RULE 1:

Group served by vehicle_id + trip_id.

Each group:
one brand
one district.

RULE 2:

chilled -> assigned vehicle temp = reefer.

Ambient + reefer is valid.

RULE 3:

van_only -> vehicle.type = van.

Normal-access + van valid.

RULE 4:

vehicle home depot == order depot.

Also require assigned vehicle status == available.

in_workshop is never allowed.

RULE 5:

every served order appears exactly once in exactly one vehicle+trip.

No split.

RULE 6:

Per served vehicle+trip:

sum source order_weight_kg <= weight_cap_kg

sum source order_volume_m3 <= volume_cap_m3

Equality valid.

RULE 7:

per vehicle:
<=2 used trips

sum Fresh trip minutes <=270

sum Style+Tech trip minutes <=480

Fresh and Style+Tech separate.

==================================================
DT-328 — EXACT TIME/BUDGET CALCULATION
==================================================

For every actual served trip, recompute with Phase20 exact formula:

outbound once

+

inter_stop_freeflow_min * (n_orders - 1)

+

sum service_allowance_min per order using brand + dock_type

RETURN:
0 / not added

Use canonical source order facts and official reference tables.

Do not trust stored solver trip minutes.

If a Phase22 trip summary exists:

compare its trip minutes with independently recomputed minutes.

Mandatory regression tests:

Gampaha example = 101

Colombo example = 112

Budget boundaries:

Fresh 270 PASS
Fresh 271 FAIL

Style+Tech 480 PASS
Style+Tech 481 FAIL

==================================================
NO UNOFFICIAL HARD RULES
==================================================

Do NOT fail allocation for:

Fresh deferred

Style served ahead of Fresh

previously-deferred order still deferred

low-flexibility order deferred

reefer carrying ambient

van carrying normal-access order

trip2 used without trip1

Do NOT add:

fuel quotas

delivery-window feasibility

Task1 lateness

Task1 service-time predictions

Task2A forecasts

traffic/road penalties

return journey

as Task2B hard validation unless the official Task2B checker/source
explicitly requires it.

==================================================
VALIDATOR OUTPUT
==================================================

Produce private:

validation_summary.json

allocation_identity_audit.json

decision_schema_audit.json

hard_rule_audit.json

trip_time_audit.csv

vehicle_budget_audit.csv

warnings.json

phase23_validation_report.md

Normal console:
status/counts only.

No real order IDs.

==================================================
CHECKER CANDIDATE
==================================================

The master inventory runs official checker in Phase23 but final canonical
submission export belongs Phase24.

Therefore create a PRIVATE checker candidate derived losslessly from the
frozen allocation.

Recommended path:

reports/private/phase23_task2b_validator/checker_workspace/submission_task2b.csv

Exact official columns only:

scenario

order_ref

outlet_id

decision

vehicle_id

trip_id

Identity must match canonical source.

Decision/assignment must come unchanged from frozen allocation.

Deferred vehicle/trip:
truly blank CSV fields.

No placeholders.

No debug columns.

Do NOT write outputs/submission_task2b.csv.

==================================================
OFFICIAL CHECKER INTERFACE
==================================================

IMPORTANT:

The Challenge Booklet names:

check_allocation.py

but does NOT state its exact CLI arguments.

DO NOT GUESS THE CLI.

Inspect the supplied official checker source and/or:

--help

to determine:

required candidate file name/path

positional/flag arguments

working-directory expectations

reference-data expectations

exit-code behavior

PASS/FAIL output semantics

Then implement the WayLoom wrapper around THAT actual interface.

Do not modify the checker.

If interface cannot be safely determined:

STOP and report blocker.

==================================================
DT-329 — RUN OFFICIAL CHECKER
==================================================

Run only if DT-320 through DT-328 PASS.

Locate official check_allocation.py.

Hash it before execution.

Stage private checker candidate.

Invoke checker locally with its ACTUAL discovered interface.

Use subprocess.

Capture:

stdout

stderr

exit code

timeout

working directory

command/interface metadata

Do not stream private failure rows to external agent.

Determine PASS according to the actual official checker semantics.

Checker PASS = feasibility evidence only.

Not optimality evidence.

==================================================
CROSS-VALIDATOR AGREEMENT
==================================================

Own PASS + checker PASS:
required successful state.

Own FAIL + checker FAIL:
Phase23 FAIL.

Own PASS + checker FAIL:
BLOCKER.
Investigate validator gap / candidate format / invocation.
Do not patch allocation manually.

Own FAIL + checker PASS:
BLOCKER.
Investigate whether own validator is over-strict/unofficial.
Use official source as authority.
Do not loosen it without source support.

Both must PASS.

==================================================
DT-330 — SAVE CHECKER EVIDENCE
==================================================

Save private immutable evidence:

checker_stdout.txt

checker_stderr.txt

checker_evidence.json

checker_input_sha256.txt

official_checker_sha256.txt

Evidence JSON must record at least:

phase = 23

task = DT-330

checker path/name

checker SHA256

checker input SHA256

Phase22 frozen allocation SHA256

Phase22 freeze manifest SHA256

Python version

working directory

actual invocation mode

exit code

PASS detection

stdout SHA256

stderr SHA256

timestamp

git commit if available

own validator status

official checker status

Do not hard-code exit_code 0 as universal PASS unless actual checker
semantics confirm it.

Do not produce PASS evidence from failed execution.

==================================================
EVIDENCE OVERWRITE PROTECTION
==================================================

Do not silently overwrite previous successful checker evidence.

Use either:

timestamped run directories

or:

explicit --new-run / overwrite authorization

Hash evidence artifacts.

A later evidence phase may create sanitized tracked evidence separately.

==================================================
CHECKER SOURCE IMMUTABILITY
==================================================

Never modify:

check_allocation.py

Do not:

comment out rules

change tolerance

monkeypatch logic

use an edited copy

Before run:
hash official checker.

If checker crashes due environment/path:

fix wrapper/environment only.

If checker behavior conflicts with booklet:
STOP for human review.

==================================================
TESTS
==================================================

Use synthetic fixtures only.

IDENTITY:

S1 pass
non-S1 fail
duplicate order_ref fail
missing fail
extra fail
blank fail
repeated outlet allowed
outlet source mismatch fail

DECISION:

served pass
deferred pass
capitalization fail
placeholder fail
blank fail

SERVED FIELDS:

valid
missing vehicle
missing trip
unknown vehicle

DEFERRED:

both blank pass
vehicle populated fail
trip populated fail
placeholder fail
0 fail

TRIP ID:

1 pass
2 pass
0 fail
3 fail
fraction fail
deferred blank pass

HARD RULE MUTATIONS:

mixed brand

mixed district

chilled on non-reefer

van-only on truck

wrong depot

in_workshop assignment

split/duplicate served order

overweight

over-volume

more than two trips / invalid trip representation

Fresh 271

Style+Tech 481

BOUNDARIES:

weight == cap pass

volume == cap pass

Fresh 270 pass

Style+Tech 480 pass

TIME:

one order

two orders

three orders

repeated outlet

mixed dock

101 public example

112 public example

no return

CHECKER RUNNER:

mock success checker

mock fail checker

nonzero exit

PASS/FAIL marker handling

stdout capture

stderr capture

timeout

missing checker

path with spaces

working dir

hashes

EVIDENCE:

hash correctness

status derivation

overwrite protection

no fake PASS

END TO END:

synthetic frozen allocation
→ own validator
→ checker candidate
→ mock checker
→ evidence

Then mutate one official rule:
own validator must block checker stage.

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After DT-320–326:
run identity/decision/field tests.

After DT-327–328:
run every hard-rule and exact-time test.

Do not continue to checker runner while own validator can miss an official
rule.

After DT-329:
run synthetic checker-runner tests.

After DT-330:
run evidence/hash tests.

Fix ordinary implementation defects automatically.

Do NOT change frozen allocation.

Do NOT change official rules.

Do NOT edit official checker.

Then run relevant Task2B safe tests, including new Phase23 tests.

Run:

pytest -q \
  tests/test_task2b_allocation_validator.py \
  tests/test_task2b_checker_runner.py \
  tests/test_task2b_checker_evidence.py

Then all existing Task2B tests.

Then:

pytest -q

python -m pip check

git status

git diff

git diff --check

If real private data is required:

do not inspect it in Codex.

Return exact local commands to human.

Ensure private paths remain ignored/unstaged.

==================================================
LOCAL OWN-VALIDATOR COMMAND
==================================================

Implement but do NOT execute real private allocation inside Codex:

python scripts/validate_task2b_allocation.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --scenario-config configs/task2b_scenario.yaml \
  --validation-config configs/task2b_validation.yaml \
  --allocation data/interim/task2b_final_allocation.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --report-dir reports/private/phase23_task2b_validator

==================================================
LOCAL OFFICIAL-CHECKER WRAPPER COMMAND
==================================================

Implement:

python scripts/run_official_task2b_checker.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --validation-config configs/task2b_validation.yaml \
  --allocation data/interim/task2b_final_allocation.csv \
  --report-dir reports/private/phase23_task2b_validator

The wrapper must call check_allocation.py using the ACTUAL supplied
official interface discovered from the official file.

Do not invent a direct checker CLI in documentation unless verified.

==================================================
STOP CONDITIONS
==================================================

STOP if:

Phase22 not frozen

allocation hash mismatch

scenario not S1

order_ref set mismatch

duplicate order_ref

outlet identity mismatch

invalid decision

served missing assignment

deferred has assignment

invalid trip ID

unknown/unavailable/workshop vehicle

mixed brand

mixed district

chilled non-reefer

van-only truck

wrong depot

whole-order violation

weight violation

volume violation

>2 trips

wrong trip arithmetic

return added

Fresh >270

Style+Tech >480

public 101 regression fails

validator mutates input

checker candidate not lossless

official checker interface would need guessing

official checker modified

official checker fails/crashes unresolved

own/checker disagree

checker evidence incomplete

false PASS evidence

Phase24 final CSV generated early

Phase22 allocation manually patched

Task1 changed

Task2A changed

private rows must be exposed

tests cannot pass

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-320 READY
DT-321 READY
DT-322 READY
DT-323 READY
DT-324 READY
DT-325 READY
DT-326 READY
DT-327 READY
DT-328 READY
DT-329 READY
DT-330 READY

Phase22 frozen hash verified

validator read-only

scenario exact

order set exact

decision domain exact

served fields valid

deferred fields blank

trip ID domain exact

all seven hard rules implemented independently

exact Phase20 trip arithmetic reused

no return

Fresh budget exact

Style+Tech budget exact

101 example passes

112 example passes

private checker candidate builder complete

official checker interface discovery implemented

official checker remains unmodified

checker evidence capture complete

cross-validator disagreement blocks

no policy-as-feasibility rule

no unofficial hard rules

no final Task2B output yet

safe tests pass

full suite passes

pip check passes

private outputs ignored

Task1 unchanged

Task2A unchanged

Phase22 allocation unchanged

no Phase24 implementation added

==================================================
RETURN ONLY
==================================================

PHASE:
23 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-320 READY / FAIL
DT-321 READY / FAIL
DT-322 READY / FAIL
DT-323 READY / FAIL
DT-324 READY / FAIL
DT-325 READY / FAIL
DT-326 READY / FAIL
DT-327 READY / FAIL
DT-328 READY / FAIL
DT-329 READY / FAIL
DT-330 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

PHASE22 FROZEN HASH:
PASS / FAIL

SCENARIO VALUES:
PASS / FAIL

ORDER_REF EXACT COVERAGE:
PASS / FAIL

DECISION DOMAIN:
PASS / FAIL

SERVED FIELD RULE:
PASS / FAIL

DEFERRED FIELD RULE:
PASS / FAIL

TRIP ID DOMAIN:
PASS / FAIL

SEVEN HARD RULE VALIDATOR:
PASS / FAIL

EXACT TIME-BUDGET VALIDATOR:
PASS / FAIL

OFFICIAL CHECKER INTERFACE:
DISCOVERED / BLOCKED

OFFICIAL CHECKER WRAPPER:
READY / FAIL

CHECKER EVIDENCE CAPTURE:
READY / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

TASK 2A FROZEN ARTIFACTS CHANGED:
MUST BE NO

PHASE22 FROZEN ALLOCATION CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print:

1. exact local own-validator command
2. exact local official-checker wrapper command

PHASE 23 STATUS:
AWAITING LOCAL VALIDATION + OFFICIAL CHECKER

READY FOR PHASE 24:
NO

Then STOP.

Do not start Phase24.
```

---

# 56. Independent Phase 23 review prompt

Use a fresh Codex/Cursor session only after the human has run both the own validator and the official checker locally.

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon Phase 23.

Do NOT implement Phase 24.
Do NOT run the real private-data validator/checker.
Do NOT inspect private row-level allocation/checker contents.
Do NOT modify code initially.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase23
4. PHASE_20_COMPETITION_CONTRACT.md
5. PHASE_21_COMPETITION_CONTRACT.md
6. PHASE_22_COMPETITION_CONTRACT.md
7. PHASE_23_COMPETITION_CONTRACT.md

8. src/task2b/allocation_validator.py
9. src/task2b/checker_runner.py
10. src/task2b/checker_evidence.py

11. scripts/validate_task2b_allocation.py
12. scripts/run_official_task2b_checker.py

13. configs/task2b_validation.yaml
14. docs/task2b_validation_spec.md

15. tests/test_task2b_allocation_validator.py
16. tests/test_task2b_checker_runner.py
17. tests/test_task2b_checker_evidence.py

18. relevant Phase20 pure trip-time code
19. Phase22 freeze/hash code
20. .gitignore
21. .cursorignore if present

You MAY inspect the official check_allocation.py SOURCE to verify the
wrapper interface and prove it was not modified.

Do NOT run it on private real data.

==================================================
HUMAN SANITIZED LOCAL RESULT
==================================================

LOCAL PHASE23 OWN VALIDATOR: <PASS/FAIL>

PHASE22 FROZEN HASH: <PASS/FAIL>

SCENARIO VALUES: <PASS/FAIL>
ORDER_REF EXACT COVERAGE: <PASS/FAIL>
ORDER_REF UNIQUENESS: <PASS/FAIL>
OUTLET_ID SOURCE CONSISTENCY: <PASS/FAIL>

DECISION DOMAIN: <PASS/FAIL>
SERVED FIELD POPULATION: <PASS/FAIL>
DEFERRED FIELD BLANKNESS: <PASS/FAIL>
TRIP ID DOMAIN: <PASS/FAIL>

RULE 1 BRAND + DISTRICT: <PASS/FAIL>
RULE 2 REFRIGERATION: <PASS/FAIL>
RULE 3 VAN-ONLY ACCESS: <PASS/FAIL>
RULE 4 HOME DEPOT / AVAILABILITY: <PASS/FAIL>
RULE 5 WHOLE ORDERS: <PASS/FAIL>
RULE 6 WEIGHT + VOLUME: <PASS/FAIL>
RULE 7 TRIPS + TIME: <PASS/FAIL>

EXACT TRIP-TIME CALCULATION: <PASS/FAIL>
RETURN LEG ADDED: <YES/NO>

FRESH >270 VIOLATIONS: <number>
STYLE+TECH >480 VIOLATIONS: <number>

OFFICIAL CHECKER FILE FOUND: <PASS/FAIL>
OFFICIAL CHECKER SHA256 CAPTURED: <PASS/FAIL>
CHECKER CANDIDATE SHA256: <PASS/FAIL>
OFFICIAL check_allocation.py RESULT: <PASS/FAIL>
RAW CHECKER EVIDENCE SAVED: <PASS/FAIL>

Do not ask for private allocation rows.

==================================================
AUDIT MASTER TASKS
==================================================

DT-320:
own validator genuinely independent/read-only.

DT-321:
scenario S1 exact; identity comparison sensible.

DT-322:
exact one-row-per-order_ref and exact order set.

DT-323:
decision only served/deferred.

DT-324:
served vehicle/trip populated.

DT-325:
deferred vehicle/trip blank.

DT-326:
served trip IDs exactly 1 or 2; no unofficial trip2->trip1 rule.

DT-327:
all seven official hard rules independently recomputed.

DT-328:
exact trip-time and 270/480 vehicle budgets independently recomputed;
no return.

DT-329:
official checker invoked via actual supplied interface, not guessed;
checker unmodified.

DT-330:
stdout/stderr/hash/evidence saved accurately and immutably.

==================================================
CRITICAL INDEPENDENCE AUDIT
==================================================

Verify allocation validator does NOT use the optimizer model as proof.

It may reuse Phase20 pure trip calculator.

Verify it joins back to canonical order/fleet/vehicle/reference facts.

Verify violations are detected from frozen allocation content.

==================================================
CRITICAL RULE AUDIT
==================================================

Verify:

same brand + district

chilled -> reefer

van_only -> van

home depot

available/not workshop

whole order

weight

volume

max two trips

Fresh combined <=270

Style+Tech combined <=480

Trip time:

outbound once

inter-stop*(orders-1)

handling per order brand+dock

no return

==================================================
CRITICAL SCOPE AUDIT
==================================================

Validator must NOT add hard rules for:

policy preference

Fresh priority

previous deferral

waiting-days priority

fuel

delivery windows

Task1 outputs

Task2A outputs

trip2 requiring trip1

reefer ambient use

van normal-access use

==================================================
CHECKER INTERFACE AUDIT
==================================================

Because booklet does not specify CLI:

verify wrapper inspected/uses the actual official checker interface.

Verify no invented CLI assumption.

Verify official checker source hash is captured.

Verify checker source is unmodified.

Verify private candidate is separate from final Phase24 output.

==================================================
CROSS-VALIDATOR AUDIT
==================================================

Own PASS + official PASS:
required.

Any disagreement:
Phase23 must block.

Verify code cannot report overall PASS on disagreement.

==================================================
EVIDENCE AUDIT
==================================================

Verify:

checker source SHA256

checker input SHA256

frozen allocation SHA256

Phase22 freeze manifest hash

stdout/stderr captured

stdout/stderr hashes

actual exit/result semantics

timestamp

git commit where available

own validator status

checker status

overwrite protection

No false PASS.

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_task2b_allocation_validator.py \
  tests/test_task2b_checker_runner.py \
  tests/test_task2b_checker_evidence.py

Run existing Task2B safe suite.

Then:

pytest -q

python -m pip check

git status

git diff --check

Do NOT run private real-data validation/checker.

==================================================
RETURN
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

FROZEN ALLOCATION INTEGRITY:
PASS / FAIL

OWN VALIDATOR INDEPENDENCE:
PASS / FAIL

IDENTITY / ORDER COVERAGE:
PASS / FAIL

DECISION / FIELD RULES:
PASS / FAIL

SEVEN OFFICIAL HARD RULES:
PASS / FAIL

EXACT TIME/BUDGET CALCULATION:
PASS / FAIL

NO UNOFFICIAL HARD RULES:
PASS / FAIL

OFFICIAL CHECKER INTERFACE:
PASS / FAIL

OFFICIAL CHECKER IMMUTABILITY:
PASS / FAIL

CROSS-VALIDATOR AGREEMENT:
PASS / FAIL

CHECKER EVIDENCE INTEGRITY:
PASS / FAIL

NO PHASE24 FINAL OUTPUT:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

HUMAN OWN-VALIDATOR RUN:
PASS / FAIL

HUMAN OFFICIAL-CHECKER RUN:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-320: PASS/FAIL
DT-321: PASS/FAIL
DT-322: PASS/FAIL
DT-323: PASS/FAIL
DT-324: PASS/FAIL
DT-325: PASS/FAIL
DT-326: PASS/FAIL
DT-327: PASS/FAIL
DT-328: PASS/FAIL
DT-329: PASS/FAIL
DT-330: PASS/FAIL

PHASE 23 REVIEW:
PASS / FAIL

OWN TASK2B VALIDATOR:
PASS / FAIL

OFFICIAL check_allocation.py:
PASS / FAIL

CHECKER EVIDENCE:
SAVED / MISSING

READY FOR PHASE 24:
YES / NO

If FAIL:
list exact blockers only.

Do not fix the frozen allocation manually.
Do not start Phase24.
```

---

# 57. Completion record

```markdown
# Phase 23 Completion Record

## Tasks

- [ ] DT-320
- [ ] DT-321
- [ ] DT-322
- [ ] DT-323
- [ ] DT-324
- [ ] DT-325
- [ ] DT-326
- [ ] DT-327
- [ ] DT-328
- [ ] DT-329
- [ ] DT-330

## Frozen integrity

- [ ] Phase22 state FROZEN
- [ ] allocation SHA256 matches freeze manifest

## Own validator

- [ ] S1 exact
- [ ] exact order_ref set
- [ ] decision domain
- [ ] served fields
- [ ] deferred fields
- [ ] trip IDs
- [ ] hard rules 7/7
- [ ] exact time
- [ ] Fresh <=270
- [ ] Style+Tech <=480
- [ ] no return

## Official checker

- [ ] actual interface inspected
- [ ] checker unmodified
- [ ] private checker candidate built
- [ ] checker PASS
- [ ] stdout/stderr saved
- [ ] checker hash saved
- [ ] input hash saved
- [ ] evidence JSON saved

## Safety

- Task 1 changed: NO
- Task 2A changed: NO
- Phase22 allocation changed: NO
- final Task2B official output created: NO
- private rows exposed: NO

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 23 STATUS: PASS / FAIL
OWN TASK 2B VALIDATOR: PASS / FAIL
OFFICIAL CHECKER: PASS / FAIL
CHECKER EVIDENCE: SAVED / MISSING
READY FOR PHASE 24: YES / NO
```

---

# 58. Final Phase 23 checklist

Before Phase 24:

- [ ] Phase 22 allocation is still frozen and hash-matched.
- [ ] validator is independent/read-only.
- [ ] scenario is exactly S1.
- [ ] every source `order_ref` exists exactly once.
- [ ] no extra order exists.
- [ ] repeated outlets are not collapsed.
- [ ] decisions are only served/deferred.
- [ ] served assignment fields are populated.
- [ ] deferred assignment fields are blank.
- [ ] served trip IDs are 1 or 2.
- [ ] assigned vehicles are available.
- [ ] workshop vehicles are never assigned.
- [ ] one brand per trip.
- [ ] one district per trip.
- [ ] chilled only on reefer.
- [ ] van-only only on van.
- [ ] home-depot rule passes.
- [ ] whole-order rule passes.
- [ ] trip weight capacity passes.
- [ ] trip volume capacity passes.
- [ ] each vehicle uses at most two trips.
- [ ] exact trip formula passes.
- [ ] return journey is not added.
- [ ] Fresh per vehicle <=270.
- [ ] Style+Tech per vehicle <=480.
- [ ] 101-minute public regression passes.
- [ ] 112-minute public regression passes.
- [ ] validator does not enforce Phase21 preference as feasibility.
- [ ] validator does not add fuel/window/Task1/Task2A constraints.
- [ ] checker candidate is lossless and private.
- [ ] official checker CLI/interface was inspected, not invented.
- [ ] official checker remains unchanged.
- [ ] official checker passes.
- [ ] own validator and official checker agree.
- [ ] raw checker stdout/stderr saved.
- [ ] checker source/input hashes saved.
- [ ] evidence JSON saved.
- [ ] no final `outputs/submission_task2b.csv` exists yet from Phase 23.
- [ ] Task 1 remains frozen.
- [ ] Task 2A remains frozen.
- [ ] Phase 22 allocation remains unchanged.
- [ ] independent review passes.

Only then:

```text
PHASE 23 STATUS: PASS
OWN TASK 2B VALIDATOR: PASS
OFFICIAL check_allocation.py: PASS
CHECKER EVIDENCE: SAVED
READY FOR PHASE 24: YES
```
