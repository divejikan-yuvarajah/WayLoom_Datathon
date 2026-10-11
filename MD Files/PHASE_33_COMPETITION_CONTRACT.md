# PHASE 33 — Final Submission-File Testing

> **Filename:** `PHASE_33_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 33 — Final submission-file testing  
> **Task range:** **DT-420 → DT-437**  
> **Task count:** **18**  
> **Formal master dependency:** **Phases 10, 17, 24**  
> **Default phase priority:** **P0**  
> **Master phase gate:** **All three official submission files pass exact schema, ID, row and value validations.**  
> **Execution mode:** Read-only validation of frozen final CSVs; no auto-repair.  
> **Critical Task 2B gate:** Run the official organizer `check_allocation.py` again against the exact final Task 2B submission (or a proven byte-identical staged copy only if the checker interface requires it).

---

# 1. Phase 33 purpose

Phase 33 is the final **submission-file compliance gate** for all three WayLoom Datathon CSV deliverables.

By this point, the modelling and optimization work should already be frozen:

```text
Task 1:
Phase 10 final prediction file

Task 2A:
Phase 17 final forecast file

Task 2B:
Phase 24 final allocation file
```

Phase 33 does not attempt to improve them.

It answers a narrower and extremely important question:

```text
Are the exact files we are about to package valid competition submissions?
```

That means validating:

- filenames;
- exact columns;
- supplied identifiers;
- row counts/order;
- numeric validity;
- Task 2A business invariants;
- Task 2B placeholder/field formatting;
- official Task 2B feasibility checker;
- and proof that validation itself did not modify the frozen files.

---

# 2. Finalized Phase 33 master inventory

The finalized WayLoom master inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [x] | **DT-420** | [O] | P0 | Submission files generated | Test Task 1 filename |
| [x] | **DT-421** | [O] | P0 | Phases 10,17,24 | Test Task 1 columns |
| [x] | **DT-422** | [O] | P0 | Phases 10,17,24 | Test Task 1 row count |
| [x] | **DT-423** | [O] | P0 | Phases 10,17,24 | Test Task 1 row order |
| [x] | **DT-424** | [O] | P0 | Phases 10,17,24 | Test Task 1 IDs unchanged |
| [x] | **DT-425** | [O] | P0 | Phases 10,17,24 | Test Task 1 predictions finite |
| [x] | **DT-426** | [O] | P0 | Phases 10,17,24 | Test Task 1 probabilities in range |
| [x] | **DT-427** | [O] | P0 | Phases 10,17,24 | Test Task 2A filename |
| [x] | **DT-428** | [O] | P0 | Phases 10,17,24 | Test Task 2A row IDs unchanged |
| [x] | **DT-429** | [O] | P0 | Phases 10,17,24 | Test Task 2A predictions nonnegative |
| [x] | **DT-430** | [O] | P0 | Phases 10,17,24 | Test Style chilled exactly zero |
| [x] | **DT-431** | [O] | P0 | Phases 10,17,24 | Test Tech chilled exactly zero |
| [x] | **DT-432** | [O] | P0 | Phases 10,17,24 | Test chilled ≤ total |
| [x] | **DT-433** | [O] | P0 | Phases 10,17,24 | Test Task 2B filename |
| [x] | **DT-434** | [O] | P0 | Phases 10,17,24 | Test Task 2B all orders present |
| [x] | **DT-435** | [O] | P0 | Phases 10,17,24 | Test Task 2B all placeholders removed |
| [x] | **DT-436** | [O] | P0 | Phases 10,17,24 | Test served/deferred spelling/format |
| [x] | **DT-437** | [O] | P0 | Phases 10,17,24 | Test Task 2B with official checker again |

**Expected Phase 33 tasks:** 18  
**Missing tasks allowed:** 0  
**Phase complete:** [x]
**READY FOR PHASE 34:** YES

---

# 3. Official Challenge Booklet — submission filename contract

The official booklet states:

```text
Use the exact filenames below.
Keep all supplied identifiers and rows unchanged.
Task 1 also requires the original row order.
Fill the answer columns and replace any placeholders.
```

Official filenames:

```text
submission_task1.csv

submission_task2a.csv

submission_task2b.csv
```

Identifiers match submissions to the correct records.

Mismatched identifiers cannot be scored.

This is the central official basis for DT-420, DT-427 and DT-433 and the identity checks throughout this phase.

---

# 4. Official Task 1 output contract

The official Task 1 output is:

```text
delivery_id
pred_service_min
pred_late_prob
```

Official instructions:

```text
Keep delivery_id values and row order exactly as supplied.

Do not add or remove rows.

Fill only the two prediction columns.
```

Types/semantics:

```text
delivery_id:
supplied identifier, unchanged

pred_service_min:
predicted outlet handling time in minutes

pred_late_prob:
number from 0 to 1
probability arrival is after the window closes
```

---

# 5. Official Task 2A output contract

The official Task 2A output is:

```text
row_id
pred_total_volume_m3
pred_chilled_volume_m3
```

Official instructions:

```text
Preserve the supplied row_id values.

Fill the two prediction columns.

Only Fresh has chilled demand.

Set pred_chilled_volume_m3 to 0 for Style and Tech.
```

The booklet describes chilled volume as:

```text
the chilled portion of total volume
```

which supports the final WayLoom invariant:

```text
pred_chilled_volume_m3 <= pred_total_volume_m3
```

---

# 6. Official Task 2B output contract

The official Task 2B output is:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

Official instructions:

```text
Keep scenario, order_ref and outlet_id unchanged.

Use order_ref as the allocation key because outlet_id may appear more than once.

Complete decision, vehicle_id and trip_id for every row.
```

For served:

```text
decision = served

vehicle_id = assigned vehicle

trip_id = 1 or 2
```

For deferred:

```text
decision = deferred

vehicle_id = blank

trip_id = blank
```

The template's answer fields contain placeholders.

Every placeholder must be replaced.

---

# 7. Official Task 2B checker contract

The booklet states:

```text
check_allocation.py checks the Task 2B allocation against the feasibility
rules and can be run before you submit.
```

And explicitly:

```text
Passing these checks confirms that your allocation meets the feasibility
rules, not that it is optimal.
```

DT-437 therefore proves:

```text
final Task2B file is feasible under the organizer checker
```

not:

```text
final Task2B allocation is globally optimal according to the organizer.
```

---

# 8. Phase 33 source-of-truth hierarchy

Use:

```text
Official Challenge Booklet
        ↓
official templates / official checker
        ↓
WAYLOOM_DATATHON_MASTER_PLAN.md
        ↓
frozen Phase10 / Phase17 / Phase24 outputs
        ↓
Phase10/17/23/24 validation code
        ↓
Phase33 final gate
```

Do not replace official template identities with remembered counts or local assumptions.

---

# 9. Formal dependency vs sequential workflow

The finalized master dependency for Phase 33 is:

```text
Phases 10, 17, 24
```

because those phases create the three final CSVs.

However the WayLoom sequential workflow also requires Phase 32 to return to Phase 31 for final notebook closure before moving forward to later submission phases.

Therefore:

- the Phase 33 contract can be implemented once the final CSVs exist;
- in the normal final workflow, execute/close Phase 33 only after Phase 31 final closure is complete;
- Phase 33 itself must not modify Phase 31/32 outputs.

---

# 10. Execution principle — read only

Phase 33 is **not an output writer**.

It must never:

```text
rewrite the final CSV

sort it and save

trim whitespace and save

fill missing values

clip probabilities

clip chilled volume

fix capitalization

remove placeholders

regenerate predictions

regenerate allocations
```

Any failure is a blocker.

The appropriate upstream phase must be reopened deliberately.

---

# 11. Frozen Phase 33 inputs

Canonical final files:

```text
outputs/submission_task1.csv

outputs/submission_task2a.csv

outputs/submission_task2b.csv
```

These must remain byte-identical throughout the phase.

---

# 12. Private-data boundary

The final submissions contain competition test identifiers and predictions/allocations.

Treat row-level contents as private competition derivatives.

External Codex/Cursor implementation work should not read real rows.

Allowed external-agent work:

```text
contracts

configs

source code

validator implementation

synthetic fixtures

unit tests
```

Human-local only:

```text
real templates

real test input identifiers

real final CSV rows

official checker against real final Task2B allocation
```

Return only sanitized PASS/FAIL evidence.

---

# 13. Recommended implementation files

Prefer reuse of existing validators.

Recommended:

```text
src/common/submission_validation.py

src/task1/final_submission_validation.py

src/task2a/final_submission_validation.py

src/task2b/final_submission_validation.py

scripts/validate_final_submissions.py

configs/final_submission_validation.yaml

docs/final_submission_validation.md

tests/test_final_submission_task1.py

tests/test_final_submission_task2a.py

tests/test_final_submission_task2b.py

tests/test_final_submission_contract.py

tests/test_final_submission_readonly.py

tests/test_final_submission_checker_bridge.py
```

Do not create duplicate copies of mature Phase10/17/23/24 validation logic if it can be safely composed.

---

# 14. Private evidence directory

Human-local:

```text
reports/private/phase33_final_submissions/
```

Recommended:

```text
run_manifest.json

task1_validation.json

task2a_validation.json

task2b_validation.json

official_checker_evidence.json

final_submission_hashes.json

phase33_gate.json
```

These should be ignored/untracked.

---

# 15. Final-submission validation config

Create:

```text
configs/final_submission_validation.yaml
```

Recommended structure:

```yaml
version: 1

submission_dir: outputs

filenames:
  task1: submission_task1.csv
  task2a: submission_task2a.csv
  task2b: submission_task2b.csv

templates:
  resolve_from_dataset_manifest: true

task1:
  expected_columns:
    - delivery_id
    - pred_service_min
    - pred_late_prob

  require_original_row_order: true
  require_finite_predictions: true

  probability_min: 0.0
  probability_max: 1.0

  engineering_require_nonnegative_service: true

task2a:
  expected_columns:
    - row_id
    - pred_total_volume_m3
    - pred_chilled_volume_m3

  require_template_row_identity: true
  require_template_row_order: true
  require_finite: true
  require_nonnegative: true

  zero_chilled_brands:
    - Style
    - Tech

  require_chilled_le_total: true

task2b:
  expected_columns:
    - scenario
    - order_ref
    - outlet_id
    - decision
    - vehicle_id
    - trip_id

  require_template_identity: true
  require_template_row_order: true

  allowed_decisions:
    - served
    - deferred

  served_trip_ids:
    - "1"
    - "2"

  deferred_fields_must_be_raw_blank: true
  run_independent_validator: true
  run_official_checker: true

integrity:
  read_only: true
  pre_post_sha256_equal: true

privacy:
  report_dir: reports/private/phase33_final_submissions
  print_ids: false
  print_rows: false
```

---

# 16. Why Phase 33 needs raw CSV + typed views

Some validations are numerical.

Others depend on the literal CSV representation.

Therefore use two safe in-memory views.

## Typed view

For:

```text
finite checks

probability range

nonnegative volume

chilled <= total
```

## Raw CSV view

For:

```text
exact headers

raw empty deferred fields

exact decision spelling

trip_id representation 1 vs 1.0

placeholder text

whitespace
```

Do not rely on a DataFrame parser alone for raw-blank semantics.

---

# 17. Strict CSV preflight

Before task-level validation, require each file to be a valid CSV.

Check:

```text
exists

regular file

nonempty

header parses

expected field count in every data row

no duplicate header names

no unexpected index column

no blank logical data rows
```

Do not modify line endings or encoding in Phase 33.

---

# 18. No hardcoded real row counts

Real row counts must come from the official templates at runtime.

Do not implement:

```python
assert len(task2b) == 85
```

just because a prior run contained 85 rows.

Instead:

```text
read official Task2B template
compare final count to template count
```

Synthetic unit tests may use fixed small counts.

---

# 19. No fabricated PASS evidence

Every printed PASS must correspond to an actual executed check.

Examples:

```text
official checker missing:
FAIL / NOT_RUN
not PASS

template unavailable:
FAIL

human-local real validation not performed:
NOT_RUN
```

Final Phase 33 closure requires real PASS, not NOT_RUN.

---

# 20. DT-420 — Test Task 1 filename

Required:

```text
submission_task1.csv
```

Exact basename.

Reject:

```text
Submission_Task1.csv

submission_task1 (1).csv

submission_task1_final.csv

task1.csv
```

This derives directly from the official submission-template filename requirement.

---

# 21. DT-420 implementation

The validator should accept a submission directory and resolve:

```text
<submission_dir>/submission_task1.csv
```

Do not accept "closest match."

Do not silently rename.

Missing exact file:

```text
DT-420 FAIL
```

---

# 22. DT-421 — Test Task 1 columns

Require exactly:

```text
delivery_id

pred_service_min

pred_late_prob
```

in this order.

No extra column.

No index.

No uncertainty field.

No model-debug metadata.

---

# 23. DT-421 rationale

The booklet says:

```text
Fill only the two prediction columns.
```

Therefore the final file is not allowed to include additional predictions, confidence bounds or diagnostics.

---

# 24. DT-422 — Test Task 1 row count

Load the official Task1 template locally.

Require:

```text
final rows == template rows
```

Do not add/remove rows.

Do not compare to a hardcoded count.

---

# 25. DT-423 — Test Task 1 row order

This requirement is explicitly stated by the booklet.

Compare:

```text
final delivery_id sequence
```

to:

```text
template delivery_id sequence
```

Require exact row-by-row equality.

Never sort before this comparison.

---

# 26. DT-424 — Test Task 1 IDs unchanged

Validate:

```text
no blank delivery_id

same values as template

same case/spelling

same set

no unintended duplicate
```

Because DT-423 already proves ordered sequence, DT-424 exists as a separate diagnostic identity guard.

---

# 27. Task 1 mismatch privacy

On failure, normal output should say:

```text
TASK1 ID MISMATCH COUNT: <n>
```

Do not print the actual `delivery_id` values by default.

Optional local-private debug output may contain details only under `reports/private/`.

---

# 28. DT-425 — Test Task 1 predictions finite

Validate both:

```text
pred_service_min

pred_late_prob
```

Require:

```text
numeric

not blank

not NaN

not +Inf

not -Inf
```

This is the exact master task requirement.

---

# 29. Task 1 service nonnegative engineering guard

Service time is a duration, and the frozen Task1 final pipeline already applies its validated service-time semantics/postprocessing.

Therefore additionally require:

```text
pred_service_min >= 0
```

Mark this as:

```text
WayLoom final-pipeline engineering invariant
```

not a separately quoted organizer output constraint.

Do not clip negative values during Phase 33.

---

# 30. DT-426 — Test Task 1 probabilities in range

Every:

```text
pred_late_prob
```

must satisfy:

```text
0 <= value <= 1
```

This is explicitly official.

Valid:

```text
0
1
0.37
```

Invalid:

```text
-0.01
1.01
NaN
Inf
```

---

# 31. Task 1 Phase 33 final gate

Task1 PASS requires all:

```text
DT-420
DT-421
DT-422
DT-423
DT-424
DT-425
DT-426
```

plus:

```text
no placeholders

no blank prediction cells

pre/post file hash unchanged
```

---

# 32. DT-427 — Test Task 2A filename

Required:

```text
submission_task2a.csv
```

Exact.

Reject renamed variants.

---

# 33. Task 2A exact-schema enhanced guard

Although the master names DT-427 as filename, the Phase 33 phase gate requires exact schema validation.

Require exact columns:

```text
row_id

pred_total_volume_m3

pred_chilled_volume_m3
```

in order.

No extra columns.

---

# 34. DT-428 — Test Task 2A row IDs unchanged

Compare final Task2A file to the official Task2A template.

Require:

```text
same row count

same row_id values

no blank row_id

no unintended duplicate

all official rows preserved
```

---

# 35. Task 2A row-order safety guard

The booklet explicitly singles out Task 1 for original row order.

Its general template rule says all supplied identifiers and rows must remain unchanged.

The frozen WayLoom Task2A pipeline also preserves template order.

Therefore Phase 33 should require:

```text
Task2A final row_id sequence == template row_id sequence
```

as a conservative engineering guard.

Label this as a WayLoom final-file safety check, not a new organizer wording.

---

# 36. Task 2A brand lookup

DT-430 and DT-431 need the brand.

The final submission does not contain brand.

Use locally:

```text
task2a_test_inputs.csv
```

Map:

```text
row_id -> brand
```

Require one-to-one mapping.

Do not infer brand from row_id text.

Do not hardcode row positions.

---

# 37. DT-429 — Test Task 2A predictions nonnegative

Validate both:

```text
pred_total_volume_m3

pred_chilled_volume_m3
```

Require:

```text
numeric

finite

>= 0
```

This means Phase33 also rejects:

```text
NaN

Inf

blank
```

because those are not valid nonnegative volumes.

---

# 38. Negative zero

Numeric:

```text
-0.0
```

equals zero.

It need not fail the value invariant.

If repository formatting policy requires canonical `0`, report a formatting warning.

Do not rewrite it in Phase33.

---

# 39. DT-430 — Test Style chilled exactly zero

For every row where official test input:

```text
brand == Style
```

require:

```text
pred_chilled_volume_m3 == 0
```

Exact numeric zero.

Do not use an approximate epsilon allowing a small nonzero prediction.

---

# 40. DT-431 — Test Tech chilled exactly zero

For:

```text
brand == Tech
```

require:

```text
pred_chilled_volume_m3 == 0
```

This must be a separate tested branch.

A validator that checks only:

```text
brand != Fresh
```

may be logically acceptable but tests still need to prove both official brands independently.

---

# 41. Fresh chilled

Fresh chilled:

```text
may be zero or positive
```

subject to:

```text
0 <= chilled <= total
```

Do not force Fresh chilled to be positive.

---

# 42. DT-432 — Test chilled ≤ total

For every Task2A row:

```text
pred_chilled_volume_m3
<=
pred_total_volume_m3
```

Chilled is a portion of total demand.

Require values to already be finite/nonnegative.

Do not auto-correct by setting chilled = total.

---

# 43. Task 2A Phase 33 final gate

Task2A PASS requires:

```text
DT-427
DT-428
DT-429
DT-430
DT-431
DT-432
```

plus:

```text
exact three-column schema

template row order safety

no blanks/placeholders

pre/post hash unchanged
```

---

# 44. DT-433 — Test Task 2B filename

Required:

```text
submission_task2b.csv
```

Exact.

No renamed final variants.

---

# 45. Task 2B exact schema

Require exactly:

```text
scenario

order_ref

outlet_id

decision

vehicle_id

trip_id
```

in that order.

No extra:

```text
reason_code

priority_score

trip_minutes

diagnostic columns
```

---

# 46. DT-434 — Test Task 2B all orders present

Compare to official Task2B template.

Require:

```text
same row count

same order_ref set

every official order exactly once

no extra order
```

Do not use `outlet_id` as the key.

---

# 47. Why order_ref matters

Official booklet:

```text
Use order_ref as the allocation key because outlet_id may appear more than once.
```

Therefore:

```text
duplicate outlet_id:
allowed

duplicate order_ref:
not allowed unless the official template itself is invalid
```

---

# 48. Task 2B identity triple

In addition to all orders being present, compare row-by-row:

```text
scenario

order_ref

outlet_id
```

against the official template.

This catches accidental row/identity corruption.

---

# 49. Task 2B row-order guard

Preserve official template order.

Although the master DT-434 is "all orders present", the frozen Phase24 export already uses template order.

Phase33 should validate it so later packaging cannot silently reshuffle the final file.

Do not sort to pass.

---

# 50. DT-435 — Test all placeholders removed

Official template answer placeholders include forms such as:

```text
(served/deferred)

(e.g. VEH014)

(1 or 2)
```

Every placeholder must be replaced.

Scan raw answer fields.

---

# 51. Placeholder detector

Recommended case-insensitive patterns in answer fields:

```text
(served/deferred)

(e.g.

(1 or 2)

TODO

TBD

PLACEHOLDER

<...>

[...]

fill here
```

Avoid overly broad patterns that reject legitimate vehicle IDs.

Apply placeholder rules specifically to:

```text
decision

vehicle_id

trip_id
```

---

# 52. Legitimate blank fields

Do not treat every blank Task2B answer cell as an unresolved placeholder.

For:

```text
decision == deferred
```

officially permitted blanks are:

```text
vehicle_id

trip_id
```

Decision itself is never blank.

---

# 53. DT-436 — Test served/deferred spelling and format

Require the raw decision field to be exactly:

```text
served
```

or:

```text
deferred
```

Canonical lowercase.

No whitespace.

---

# 54. Invalid decision examples

Reject:

```text
Served

DEFERRED

serve

defer

served 

 deferred

(served/deferred)

blank
```

Do not normalize in Phase33.

---

# 55. DT-436 — served-row field rules

If:

```text
decision == served
```

require:

```text
vehicle_id:
nonblank, non-whitespace

trip_id:
raw CSV text exactly "1" or "2"
```

Reject:

```text
1.0
2.0
T1
trip 1
0
blank
```

This matches the Phase24 canonical writer contract.

---

# 56. DT-436 — deferred-row field rules

If:

```text
decision == deferred
```

require raw CSV:

```text
vehicle_id = empty field

trip_id = empty field
```

Reject textual null markers:

```text
NaN

nan

None

null

N/A

-

" "
```

The official instruction is to leave the fields blank.

---

# 57. Scenario format

Task2B official scenario:

```text
S1
```

Require final scenario identity to match the official template on every row.

Do not hardcode this without also comparing to the template, although S1 is the expected official value.

---

# 58. DT-437 — Official checker again

Run:

```text
check_allocation.py
```

again after the exact final file passes DT-433–DT-436.

This is the final feasibility gate.

---

# 59. Why DT-437 matters

Earlier Phase23 may have run the organizer checker on a private checker candidate because Phase24 had not yet created the final canonical Task2B CSV.

Phase33 closes that gap by testing the actual final Phase24 artifact.

Preferred:

```text
official checker
→ outputs/submission_task2b.csv
```

---

# 60. Checker interface must be discovered, not guessed

The Challenge Booklet names the checker but does not specify its CLI.

Phase23 already required inspecting:

```text
checker source

--help / expected invocation

working-directory assumptions
```

Phase33 should reuse the existing verified checker adapter.

Do not create a second guessed invocation.

---

# 61. Direct final-file mode

Preferred evidence:

```text
checker input:
outputs/submission_task2b.csv

input SHA256:
<final hash>
```

This is the strongest DT-437 proof.

---

# 62. Byte-identical staging exception

If the organizer script requires a fixed local filename or location:

create a temporary staged copy.

Before checker:

```text
SHA256(staged)
==
SHA256(final)
```

After checker:

same.

Record:

```text
checker_input_mode = byte_identical_staged_copy
```

Do not alter the final file.

---

# 63. Independent validator rerun

Before the organizer checker, rerun the independent Phase23 validator against:

```text
outputs/submission_task2b.csv
```

or the same exact bytes.

Require:

```text
independent validator = PASS
```

This gives a second implementation of the official feasibility rules.

---

# 64. Validator/checker disagreement

Cases:

```text
own validator PASS
official checker FAIL
→ BLOCK

own validator FAIL
official checker PASS
→ BLOCK
```

Do not choose the more convenient result.

Investigate.

---

# 65. Checker result semantics

Required competition-facing wording:

```text
Official Task2B feasibility checker: PASS
```

Never:

```text
Official optimality checker: PASS
```

The booklet explicitly says feasibility only.

---

# 66. Official checker source integrity

Do not edit organizer:

```text
check_allocation.py
```

Private evidence should record its SHA256.

If source changes unexpectedly:

block DT-437.

---

# 67. Phase 33 read-only hash guard

Before all validation:

hash:

```text
submission_task1.csv

submission_task2a.csv

submission_task2b.csv
```

After all validation:

hash again.

Require:

```text
pre == post
```

for all three.

---

# 68. Why file hashes matter

A validation phase should not mutate what it validates.

This catches accidental code such as:

```python
df["decision"] = df["decision"].str.strip()
df.to_csv(...)
```

Even if the resulting file looks valid, Phase33 has violated its role.

---

# 69. Template provenance

Resolve official templates from:

```text
dataset manifest / canonical repository config
```

not user-entered arbitrary paths where possible.

Private evidence may store:

```text
relative source path

SHA256
```

No real IDs.

---

# 70. Task2A test-input provenance

DT-430/431 brand mapping should resolve:

```text
task2a_test_inputs.csv
```

from the canonical dataset manifest.

Do not infer from a copied external file.

---

# 71. Failure reporting

Default sanitized failure example:

```text
DT-430 STYLE CHILLED = 0: FAIL

violating_rows: 2

private row identifiers: REDACTED
```

Do not print the two row IDs.

---

# 72. Optional private debug mode

If needed, an explicit local flag may write:

```text
reports/private/phase33_final_submissions/debug/
```

with row-level diagnostics.

Requirements:

```text
off by default

untracked

never required for review

never printed into normal console
```

---

# 73. No auto-fix

The final validator should have no option such as:

```text
--fix

--normalize

--repair

--rewrite
```

Phase33 is a gate.

Repairs belong upstream.

---

# 74. Upstream repair map

If Task1 structural/value failure:

```text
reopen Phase10 final inference/submission
```

If Task2A failure:

```text
reopen Phase17 final inference/submission
```

If Task2B format/template failure:

```text
reopen Phase24 output generation
```

If Task2B feasibility failure:

```text
reopen Phase22/23/24 chain
```

Never manually edit the final CSV as a shortcut.

---

# 75. Validation orchestrator

Create:

```text
scripts/validate_final_submissions.py
```

Recommended high-level logic:

```text
load validation config

resolve official sources

hash final files

strict CSV preflight

Task1 checks

Task2A checks

Task2B checks

independent Task2B validator

official checker

hash final files again

build aggregate reports

exit 0 only if every gate passed
```

---

# 76. Exit code contract

Use:

```text
0:
all required Phase33 checks PASS

nonzero:
one or more required checks FAIL / could not run
```

Do not return zero with:

```text
official checker NOT_RUN
```

because DT-437 is mandatory.

---

# 77. Report schema

Recommended private `phase33_gate.json`:

```json
{
  "phase": 33,
  "status": "PASS",
  "tasks": {
    "DT-420": "PASS",
    "...": "...",
    "DT-437": "PASS"
  },
  "task1_hash_unchanged": true,
  "task2a_hash_unchanged": true,
  "task2b_hash_unchanged": true,
  "independent_task2b_validator": "PASS",
  "official_checker": "PASS",
  "official_checker_semantics": "feasibility_only"
}
```

No identifiers.

---

# 78. Task 1 validation evidence

Private aggregate:

```text
filename

column status

template row count equality

row-order equality

ID equality

finite value status

probability range status

service nonnegative engineering guard

pre/post hash
```

Do not include row values.

---

# 79. Task 2A validation evidence

Private aggregate:

```text
filename

schema

template row identity

template row order

finite/nonnegative

Style chilled zero

Tech chilled zero

chilled<=total

brand mapping completeness

pre/post hash
```

No row IDs.

---

# 80. Task 2B validation evidence

Private aggregate:

```text
filename

schema

identity triple

all orders exactly once

placeholder count = 0

decision domain

served format

deferred blank format

independent validator

official checker

pre/post hash
```

No order refs.

---

# 81. Tests — Task 1 final submission

Create:

```text
tests/test_final_submission_task1.py
```

Use synthetic fixtures only.

Required:

```text
exact filename pass

wrong filename fail

exact columns pass

wrong/missing/extra columns fail

row count equal pass

row count mismatch fail

row order exact pass

row order mismatch fail

IDs unchanged pass

changed ID fail

duplicate ID fail

blank ID fail

finite values pass

NaN fail

+Inf fail

-Inf fail

probability 0 pass

probability 1 pass

probability below 0 fail

probability above 1 fail

negative service engineering invariant fail

input bytes unchanged
```

---

# 82. Tests — Task 2A final submission

Create:

```text
tests/test_final_submission_task2a.py
```

Required:

```text
exact filename

exact columns

row count

row_id identity

row order guard

duplicate row_id

brand lookup

finite values

negative total

negative chilled

Style zero pass/fail

Tech zero pass/fail

Fresh chilled zero allowed

Fresh chilled positive allowed

chilled < total pass

chilled == total pass

chilled > total fail

input bytes unchanged
```

---

# 83. Tests — Task 2B final submission

Create:

```text
tests/test_final_submission_task2b.py
```

Required:

```text
exact filename

six columns

all orders

missing order

extra order

duplicate order_ref

repeated outlet_id allowed

identity triple

scenario mismatch

placeholder checks

decision exact domain

capitalization fail

whitespace fail

served vehicle required

served trip exactly 1/2

1.0 fail

deferred raw blanks pass

deferred NaN text fail

deferred null fail

deferred whitespace fail

input bytes unchanged
```

---

# 84. Tests — Phase 33 orchestrator

Create:

```text
tests/test_final_submission_contract.py
```

Require:

```text
all 18 task IDs mapped

any failed task -> overall FAIL

missing file -> FAIL

missing template -> FAIL

pre/post hash equality

no real row count hardcoding

no fabricated PASS

sanitized report behavior

exit code contract
```

---

# 85. Tests — explicit read-only behavior

Create:

```text
tests/test_final_submission_readonly.py
```

For PASS and FAIL fixtures:

```text
capture bytes

run validator

compare bytes
```

Require no mutation.

Also monkeypatch file-writing functions where practical to ensure the final-submission paths are never opened for write.

---

# 86. Tests — official checker bridge

Create:

```text
tests/test_final_submission_checker_bridge.py
```

Use mock/synthetic checker files.

Test:

```text
verified interface invocation

PASS recognized

FAIL recognized

checker missing

checker crash

source immutability

final-input hash

staged-copy SHA parity

staged mismatch

independent-validator disagreement

feasibility-only wording
```

No real Task2B data.

---

# 87. Regression tests

After Phase33 targeted tests, rerun relevant earlier validators:

```text
Task1 final output tests from Phase10

Task2A final output tests from Phase17

Task2B validator/checker bridge from Phase23

Task2B final export tests from Phase24
```

This catches validation-rule drift.

---

# 88. Full safe suite

Then run:

```bash
pytest -q
```

No private real data should be required for the automated suite.

---

# 89. Environment health

Run:

```bash
python -m pip check
```

Phase33 should not require new modelling dependencies.

---

# 90. Diff hygiene

Run:

```bash
git diff --check
git status
```

Expected Phase33 tracked changes:

```text
validator code

tests

config

documentation
```

Unexpected:

```text
official CSV modifications
model modifications
private evidence
Phase34 work
```

---

# 91. Human-local command

Recommended:

```bash
python scripts/validate_final_submissions.py   --config configs/final_submission_validation.yaml   --dataset-manifest configs/dataset_manifest.yaml   --submission-dir outputs   --report-dir reports/private/phase33_final_submissions
```

Use the actual repository's canonical dataset/checker resolution.

If the existing Phase23 checker bridge needs an explicit official data/checker root, expose only the minimum stable argument.

---

# 92. Human-local run must be final-file run

Do not validate a copied stale submission directory.

The canonical Phase33 run should point to the actual final:

```text
outputs/
```

directory that will feed final packaging.

If later Phase40 copies those files into the package, Phase41 should revalidate the packaged copies.

---

# 93. Sanitized local result

Expected:

```text
WAYLOOM — PHASE 33 FINAL SUBMISSION VALIDATION

TASK1
DT-420 FILENAME                         : PASS
DT-421 COLUMNS                          : PASS
DT-422 ROW COUNT                        : PASS
DT-423 ROW ORDER                        : PASS
DT-424 IDS UNCHANGED                    : PASS
DT-425 PREDICTIONS FINITE               : PASS
DT-426 PROBABILITIES [0,1]              : PASS

TASK2A
DT-427 FILENAME                         : PASS
DT-428 ROW IDS UNCHANGED                : PASS
DT-429 PREDICTIONS NONNEGATIVE          : PASS
DT-430 STYLE CHILLED = 0                : PASS
DT-431 TECH CHILLED = 0                 : PASS
DT-432 CHILLED <= TOTAL                 : PASS

TASK2B
DT-433 FILENAME                         : PASS
DT-434 ALL ORDERS PRESENT               : PASS
DT-435 PLACEHOLDERS REMOVED             : PASS
DT-436 DECISION/FIELD FORMAT            : PASS
INDEPENDENT TASK2B VALIDATOR             : PASS
DT-437 OFFICIAL check_allocation.py      : PASS
OFFICIAL CHECKER SEMANTICS               : FEASIBILITY ONLY

READ-ONLY HASH GUARD
submission_task1.csv                     : UNCHANGED
submission_task2a.csv                    : UNCHANGED
submission_task2b.csv                    : UNCHANGED

PHASE 33                                 : PASS
READY FOR PHASE 34                       : YES
```

No real IDs.

---

# 94. DT-420 edge cases

Wrong-case filename:

```text
Submission_Task1.csv
```

FAIL.

Exact file plus extra similarly named file:

```text
submission_task1.csv
submission_task1_old.csv
```

Canonical file can still pass, but validator may issue a non-blocking staging warning.

Phase40 should package only the exact canonical file.

---

# 95. DT-421 edge cases

CSV parser may produce:

```text
Unnamed: 0
```

from a saved index.

This is an extra column.

FAIL.

Do not silently drop it.

---

# 96. DT-422 edge cases

Trailing blank physical lines are not data rows if the CSV parser correctly ignores them.

A blank logical data record should fail strict preflight.

Use consistent parser semantics.

---

# 97. DT-423 edge cases

Same ID set but shuffled order:

```text
DT-423 FAIL
```

even though DT-424 ID-set check passes.

This is why the tasks are separate.

---

# 98. DT-425 edge cases

Strings such as:

```text
"nan"

"inf"
```

may parse differently by library.

Validator should reject both true nonfinite numeric values and nonnumeric string representations.

---

# 99. DT-426 edge cases

Floating noise:

```text
1.0000000001
```

is still greater than 1.

FAIL.

Do not apply a probability tolerance unless the final output contract explicitly defines one.

---

# 100. DT-428 edge cases

Task2A final file may have exactly the same row IDs but in a different order.

WayLoom final-safety guard:

FAIL.

Preserve frozen template order.

---

# 101. DT-429 edge cases

`-0.0` is numerically zero.

Do not fail nonnegativity solely on sign bit unless repository canonical-format requirements explicitly say so.

Do fail actual negative values.

---

# 102. DT-430/431 edge cases

Style/Tech chilled:

```text
1e-15
```

is not exactly zero.

FAIL.

The official rule is exact zero.

---

# 103. DT-432 edge cases

When:

```text
total = 0
chilled = 0
```

PASS.

When:

```text
total = 0
chilled > 0
```

FAIL.

---

# 104. DT-434 edge cases

Same outlet appears in several orders:

PASS.

Do not reject duplicate outlet_id.

Repeated order_ref:

FAIL.

---

# 105. DT-435 edge cases

Deferred row:

blank vehicle/trip is valid, not a placeholder.

Placeholder detector must understand this conditional.

---

# 106. DT-436 edge cases

A DataFrame may read blank trip_id as `NaN`.

Do not then write or report "NaN" as the raw field.

Use raw parser to establish the original CSV field was empty.

---

# 107. DT-437 checker crash

If official checker crashes due to invocation/environment:

```text
DT-437 FAIL/BLOCKED
```

until resolved.

Do not call a crash a PASS because own validator passed.

---

# 108. DT-437 checker output wording

If the official checker prints a success line with different capitalization/text:

the wrapper may normalize the status internally.

Store raw stdout privately.

Do not rewrite the checker.

---

# 109. Official checker direct vs staged

Best:

```text
DIRECT_FINAL_FILE
```

Acceptable only if interface requires it:

```text
BYTE_IDENTICAL_STAGED_COPY
```

Not acceptable:

```text
semantically recreated candidate
```

Phase33 is about the final exact file.

---

# 110. Read-only checker staging

If staging is required, staging must happen in a temporary/private directory.

Do not overwrite the final output.

Delete temporary staged copies after evidence is captured if repository policy prefers.

---

# 111. Checker SHA evidence

Private evidence should include:

```text
final Task2B SHA256

checker input SHA256

official checker SHA256
```

If staged:

final == checker input

must be true.

---

# 112. Phase33 privacy

Do not expose:

```text
delivery_id

row_id

order_ref

outlet_id

vehicle_id

prediction values tied to identifiers
```

in tracked documentation or review transcript.

Aggregates/statuses are sufficient.

---

# 113. Phase33 traceability

Each master task should map to:

```text
validator function

unit test(s)

human-local result field
```

Create a mapping in the validation config or docs.

This makes independent review straightforward.

---

# 114. Recommended task-function mapping

Example:

```text
DT-420:
validate_exact_filename(task1)

DT-421:
validate_exact_columns(task1)

DT-422:
validate_row_count(task1, template)

DT-423:
validate_ordered_identity(task1.delivery_id, template.delivery_id)

...
```

Use repository naming conventions.

---

# 115. Documentation

Create:

```text
docs/final_submission_validation.md
```

Required sections:

```text
Purpose

Official submission contracts

Read-only principle

Task1 checks

Task2A checks

Task2B checks

Official checker behavior

Private evidence

Local execution

Failure routing

Phase33 PASS criteria
```

Do not include real row examples.

---

# 116. Official vs engineering distinctions

Clearly label:

Official:

```text
exact filenames

Task1 exact row order

identifier preservation

Task1 probability range

Style/Tech chilled zero

Task2B field semantics

placeholder replacement

official checker feasibility
```

WayLoom final-safety/enhanced guards:

```text
Task1 service nonnegative

Task2A exact template row order

chilled <= total as final semantic invariant

independent validator rerun

pre/post SHA256 read-only proof
```

The master inventory itself requires some of these engineering gates, but do not misquote them as exact booklet wording where the booklet is less explicit.

---

# 117. No Phase34 implementation

Phase34 is:

```text
General automated testing
```

Phase33 may add its own tests.

It must not start the Phase34 task inventory early.

No Phase34 contract implementation.

---

# 118. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b test/phase-33-final-submissions
```

If validated Phase31/32 work is not yet merged, branch from the correct validated commit instead of losing work.

Recommended commits:

```text
test(submissions): add strict Task1 final CSV validation

test(submissions): add strict Task2A final CSV validation

test(submissions): add Task2B format and official checker gate

test(submissions): add read-only submission integrity checks

docs(submissions): document Phase33 final submission validation
```

---

# 119. Git safety

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

Do not modify final CSVs in this phase.

If they are already tracked, their Git diff must remain empty.

---

# 120. Targeted tests

Run:

```bash
pytest -q   tests/test_final_submission_task1.py   tests/test_final_submission_task2a.py   tests/test_final_submission_task2b.py   tests/test_final_submission_contract.py   tests/test_final_submission_readonly.py   tests/test_final_submission_checker_bridge.py
```

Then relevant prior-phase regression tests.

---

# 121. Full safe suite

Run:

```bash
pytest -q
```

All safe tests must pass before human-local final validation.

---

# 122. Environment checks

Run:

```bash
python -m pip check

git diff --check

git status
```

No new modelling dependency should be required.

---

# 123. Human-local validation gate

External agent completes implementation using synthetic fixtures.

Then human runs the real validator locally.

The human returns only:

```text
DT statuses

checker status

hash unchanged statuses

aggregate test results
```

No real rows.

---

# 124. Fresh independent review

After human-local Phase33 PASS:

run a fresh independent Phase33 review using the review prompt in this contract.

Do not have the implementing session self-approve the phase.

---

# 125. STOP conditions

`READY FOR PHASE 34` remains **NO** if:

- DT-420 filename wrong;
- DT-421 columns wrong;
- DT-422 row count mismatch;
- DT-423 Task1 row order mismatch;
- DT-424 Task1 IDs changed;
- DT-425 Task1 nonfinite prediction;
- DT-426 probability outside [0,1];
- DT-427 Task2A filename wrong;
- DT-428 Task2A row IDs changed;
- Task2A template identity/order mismatch;
- DT-429 Task2A negative/nonfinite prediction;
- DT-430 Style chilled nonzero;
- DT-431 Tech chilled nonzero;
- DT-432 chilled > total;
- DT-433 Task2B filename/schema wrong;
- DT-434 missing/extra/duplicate order;
- Task2B identity triple mismatch;
- DT-435 placeholder remains;
- DT-436 decision spelling/format wrong;
- served row missing vehicle/trip;
- served trip not canonical 1/2;
- deferred vehicle/trip not raw blank;
- independent Task2B validator fails;
- DT-437 official checker not actually run;
- official checker CLI/interface is guessed;
- checker source changed;
- official checker fails/crashes;
- own validator/checker disagree;
- any final CSV hash changes during validation;
- normal logs reveal private IDs;
- targeted tests fail;
- full safe suite fails;
- `pip check` fails;
- independent review fails;
- Phase34 work is introduced.

---

# 126. Definition of Done

Phase 33 is complete only when:

- [x] DT-420 PASS
- [x] DT-421 PASS
- [x] DT-422 PASS
- [x] DT-423 PASS
- [x] DT-424 PASS
- [x] DT-425 PASS
- [x] DT-426 PASS
- [x] DT-427 PASS
- [x] DT-428 PASS
- [x] DT-429 PASS
- [x] DT-430 PASS
- [x] DT-431 PASS
- [x] DT-432 PASS
- [x] DT-433 PASS
- [x] DT-434 PASS
- [x] DT-435 PASS
- [x] DT-436 PASS
- [x] DT-437 PASS
- [x] exact `submission_task1.csv` filename
- [x] exact Task1 three-column schema
- [x] Task1 row count matches official template
- [x] Task1 original row order exact
- [x] Task1 IDs exact
- [x] Task1 prediction values finite
- [x] Task1 service nonnegative final-pipeline guard
- [x] Task1 late probabilities inclusive [0,1]
- [x] exact `submission_task2a.csv` filename
- [x] exact Task2A three-column schema
- [x] Task2A row IDs exact
- [x] Task2A template row order preserved
- [x] Task2A values finite/nonnegative
- [x] Style chilled exactly zero
- [x] Tech chilled exactly zero
- [x] chilled <= total for every row
- [x] exact `submission_task2b.csv` filename
- [x] exact Task2B six-column schema
- [x] all official Task2B orders exactly once
- [x] scenario/order_ref/outlet_id exact
- [x] no placeholders
- [x] decision exactly served/deferred
- [x] served vehicle/trip format exact
- [x] deferred vehicle/trip raw blank
- [x] Phase23 independent validator passes on final Task2B file
- [x] official checker runs again
- [x] official checker passes
- [x] official checker input is exact final file or proven byte-identical staged copy
- [x] official checker source unchanged
- [x] official checker documented as feasibility-only
- [x] Task1 pre/post SHA256 unchanged
- [x] Task2A pre/post SHA256 unchanged
- [x] Task2B pre/post SHA256 unchanged
- [x] no hardcoded real row counts
- [x] no fabricated PASS result
- [x] no private identifiers in normal output
- [x] targeted Phase33 tests pass
- [x] relevant Phase10/17/23/24 regressions pass
- [x] full safe suite passes
- [x] `python -m pip check` passes
- [x] `git diff --check` passes
- [x] fresh independent Phase33 review passes
- [x] no unresolved STOP condition

Then:

```text
PHASE 33 STATUS: PASS
FINAL SUBMISSION FILES: VALIDATED
TASK2B OFFICIAL CHECKER: PASS
OFFICIAL SUBMISSION CSVs: UNCHANGED
READY FOR PHASE 34: YES
```

---

# 127. Completion record

# Phase 33 Completion Record

## Task1

- [x] DT-420 exact filename
- [x] DT-421 exact columns and order
- [x] DT-422 template-derived row count
- [x] DT-423 original row order
- [x] DT-424 identifiers unchanged
- [x] DT-425 finite predictions and engineering nonnegative-service guard
- [x] DT-426 inclusive probability range `[0,1]`

## Task2A

- [x] DT-427 exact filename and schema
- [x] DT-428 template row identity/order and canonical `row_id` brand mapping
- [x] DT-429 finite, nonnegative predictions
- [x] DT-430 Style chilled exactly zero
- [x] DT-431 Tech chilled exactly zero
- [x] DT-432 chilled <= total

## Task2B

- [x] DT-433 exact filename and six-column schema
- [x] DT-434 all orders exactly once with identity triple preserved
- [x] DT-435 no answer placeholders
- [x] DT-436 exact lowercase decision and dependent raw-field format
- [x] Phase 23 independent validator PASS on the final Task2B CSV
- [x] DT-437 official `check_allocation.py` PASS on the direct final file
- [x] Official checker meaning recorded as feasibility only, not optimality

## Integrity

- Human-local Task1 pre/post hash: UNCHANGED
- Human-local Task2A pre/post hash: UNCHANGED
- Human-local Task2B pre/post hash: UNCHANGED
- Closure-recovery frozen CSV worktree comparison: UNCHANGED
- Phase 32 artifact registry worktree comparison: UNCHANGED
- Phase 32 registered artifact checksum validation: PASS

## Safety

- hardcoded real row counts: NO
- fabricated PASS: NO
- private IDs printed: NO
- final files rewritten: NO
- private row-level evidence accessed by the closure agent: NO
- official checker source modified: NO

## Verification evidence

- Sanitized human-local final-file validation: DT-420 through DT-437 PASS; independent Task2B validator PASS; official checker PASS; all three CSV hash guards UNCHANGED; private identifiers printed NO.
- Fresh independent Phase 33 review (2026-10-08): PASS; 18/18 tasks PASS; final submission files VALIDATED; official Task2B checker PASS; official CSVs UNCHANGED; blockers NONE; READY FOR PHASE 34 YES.
- Fresh independent-review targeted suite: 80 passed.
- Fresh independent-review Phase 10/17/23/24 regression suite: 128 passed.
- Fresh independent-review full safe suite: 845 passed, 1 skipped, 5 warnings.
- Fresh independent-review dependency and Git checks: `pip check` PASS; `git diff --check` PASS.
- Closure-recovery revalidation: 80 targeted Phase 33 tests passed; Phase 32 artifact checksums, feature schemas, fresh-process load and fresh-process synthetic inference PASS.

The human-local results above are recorded as operator-provided sanitized evidence. The independent reviewer did not claim to have executed those private-data checks. No earlier Phase 33 FAIL verdict was found or rewritten; the implementation-stage wait for human-local validation remains part of the historical sequence.

## Review

- independent Phase33 review: PASS
- review provenance: fresh read-only independent review in the current Phase 33 review session
- formal closure authorization: YES

## Verdict

PHASE 33 STATUS: PASS
FINAL SUBMISSION FILES: VALIDATED
TASK2B OFFICIAL CHECKER: PASS
OFFICIAL SUBMISSION CSVs: UNCHANGED
READY FOR PHASE 34: YES

---

# 128. Recommended model

Phase 33 is mostly validation, but it is a **high-stakes final-file compliance phase**.

The biggest risks are:

- checking a stale copy instead of the final file;
- sorting before order checks;
- trusting IDs by set rather than ordered identity;
- allowing NaN/Inf;
- allowing tiny nonzero Style/Tech chilled values;
- accepting textual null markers as deferred blanks;
- checking a candidate instead of the final Task2B file;
- claiming the official checker proved optimality;
- accidentally modifying files while validating them.

Recommended:

```text
GPT-5.6 Sol
Reasoning: High
```

for implementation and fresh independent review.

---

# 129. Ready-to-copy Cursor / Codex implementation prompt

```text
You are implementing WayLoom Datathon PHASE 33 only.

PHASE:
Final Submission-File Testing

TASK RANGE:
DT-420 through DT-437

EXECUTION MODE:
READ-ONLY VALIDATION OF THE THREE FROZEN OFFICIAL SUBMISSION CSV FILES.
NO MODEL TRAINING.
NO INFERENCE REGENERATION.
NO CSV REWRITING OR AUTO-FIXING.
PRIVATE REAL-DATA/SUBMISSION VALIDATION IS HUMAN-LOCAL ONLY.

RECOMMENDED MODEL:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 34.

==================================================
MISSION
==================================================

Implement one deterministic final submission-validation gate covering every
master task:

DT-420 Test Task 1 filename
DT-421 Test Task 1 columns
DT-422 Test Task 1 row count
DT-423 Test Task 1 row order
DT-424 Test Task 1 IDs unchanged
DT-425 Test Task 1 predictions finite
DT-426 Test Task 1 probabilities in range

DT-427 Test Task 2A filename
DT-428 Test Task 2A row IDs unchanged
DT-429 Test Task 2A predictions nonnegative
DT-430 Test Style chilled exactly zero
DT-431 Test Tech chilled exactly zero
DT-432 Test chilled <= total

DT-433 Test Task 2B filename
DT-434 Test Task 2B all orders present
DT-435 Test Task 2B all placeholders removed
DT-436 Test served/deferred spelling/format
DT-437 Test Task 2B with official checker again

Formal master dependency:
Phases 10, 17, 24.

Sequential workflow gate:
If following the finalized WayLoom phase sequence, Phase32 should have passed
and Phase31 final closure should already be complete before moving beyond
Phase33. Do not modify Phase31/32 artifacts here.

==================================================
OFFICIAL SOURCE CONTRACT
==================================================

The Challenge Booklet states:

Submission templates:
Use the exact filenames.

submission_task1.csv
submission_task2a.csv
submission_task2b.csv

Keep all supplied identifiers and rows unchanged.

Task 1 additionally requires the original row order.

Fill answer columns and replace placeholders.

Task1 official output:
delivery_id
pred_service_min
pred_late_prob

Keep delivery_id values and row order exactly as supplied.
Do not add/remove rows.
Fill only the two prediction columns.
pred_late_prob must be from 0 to 1.

Task2A official output:
row_id
pred_total_volume_m3
pred_chilled_volume_m3

Preserve supplied row_id values.
Only Fresh has chilled demand.
pred_chilled_volume_m3 = 0 for Style and Tech.

Task2B official output:
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id

Keep scenario/order_ref/outlet_id unchanged.
Use order_ref as allocation key because outlet_id may repeat.
Complete decision/vehicle_id/trip_id.
For deferred rows, vehicle_id and trip_id are blank.
For served rows, vehicle_id is populated and trip_id is 1 or 2.
Replace every placeholder.

Official check_allocation.py:
checks Task2B feasibility.
Passing it confirms feasibility, NOT optimality.

==================================================
SOURCE AUTHORITY
==================================================

Read:

1. Challenge Booklet
2. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase33
3. PHASE_10_COMPETITION_CONTRACT.md
4. PHASE_17_COMPETITION_CONTRACT.md
5. PHASE_23_COMPETITION_CONTRACT.md
6. PHASE_24_COMPETITION_CONTRACT.md
7. PHASE_33_COMPETITION_CONTRACT.md

Then inspect SAFE code/config interfaces.

Do NOT inspect real private submission rows in external-agent context.

Do NOT open:

data/raw/**
data/interim/**
reports/private/**
outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv

or official test/template row data in external-agent context.

Build and test validation code with synthetic fixtures.
The human runs the validator locally against the real files and returns a
sanitized PASS/FAIL summary.

==================================================
FROZEN FILES — READ-ONLY
==================================================

These are final/frozen inputs to Phase33:

outputs/submission_task1.csv
outputs/submission_task2a.csv
outputs/submission_task2b.csv

Do NOT rewrite them.

Do NOT normalize them.

Do NOT sort them.

Do NOT trim whitespace in-place.

Do NOT convert data types and save.

Do NOT regenerate predictions.

Do NOT rerun model training.

Do NOT rerun Task2B optimizer.

Phase33 discovers errors; it does not repair them.

Any failure must identify the upstream phase to reopen.

==================================================
CREATE / UPDATE
==================================================

Prefer reusing existing Phase10/17/23/24 validators rather than duplicating
business logic.

Recommended:

src/common/submission_validation.py

src/task1/final_submission_validation.py
src/task2a/final_submission_validation.py
src/task2b/final_submission_validation.py

scripts/validate_final_submissions.py

configs/final_submission_validation.yaml

docs/final_submission_validation.md

tests/test_final_submission_task1.py
tests/test_final_submission_task2a.py
tests/test_final_submission_task2b.py
tests/test_final_submission_contract.py
tests/test_final_submission_readonly.py
tests/test_final_submission_checker_bridge.py

Private human-local evidence:

reports/private/phase33_final_submissions/
  run_manifest.json
  task1_validation.json
  task2a_validation.json
  task2b_validation.json
  official_checker_evidence.json
  final_submission_hashes.json
  phase33_gate.json

Do NOT create Phase34 tests beyond Phase33's own validation implementation.

==================================================
CONFIG
==================================================

Create:

configs/final_submission_validation.yaml

Recommended:

version: 1

submission_dir: outputs

filenames:
  task1: submission_task1.csv
  task2a: submission_task2a.csv
  task2b: submission_task2b.csv

templates:
  resolve_from_dataset_manifest: true

task1:
  expected_columns:
    - delivery_id
    - pred_service_min
    - pred_late_prob
  require_original_row_order: true
  require_finite_predictions: true
  probability_min: 0.0
  probability_max: 1.0
  engineering_require_nonnegative_service: true

task2a:
  expected_columns:
    - row_id
    - pred_total_volume_m3
    - pred_chilled_volume_m3
  require_template_row_identity: true
  require_template_row_order: true
  require_finite: true
  require_nonnegative: true
  zero_chilled_brands:
    - Style
    - Tech
  require_chilled_le_total: true

task2b:
  expected_columns:
    - scenario
    - order_ref
    - outlet_id
    - decision
    - vehicle_id
    - trip_id
  require_template_identity: true
  require_template_row_order: true
  allowed_decisions:
    - served
    - deferred
  served_trip_ids:
    - "1"
    - "2"
  deferred_fields_must_be_raw_blank: true
  run_independent_validator: true
  run_official_checker: true

integrity:
  read_only: true
  pre_post_sha256_equal: true

privacy:
  report_dir: reports/private/phase33_final_submissions
  print_ids: false
  print_rows: false

Adapt paths to actual repository conventions.
Do not put real template IDs into config.

==================================================
GENERAL VALIDATION ARCHITECTURE
==================================================

Implement one final orchestrator:

scripts/validate_final_submissions.py

Flow:

1. resolve official dataset/template paths from the repository manifest;
2. validate that the exact three filenames exist;
3. compute PRE-validation SHA256 of all three final CSVs;
4. parse files strictly;
5. run Task1 checks DT-420–DT-426;
6. run Task2A checks DT-427–DT-432;
7. run Task2B checks DT-433–DT-436;
8. rerun the independent Task2B validator on the exact final Task2B CSV;
9. run official check_allocation.py again on the exact final Task2B CSV,
   using the actual previously-discovered organizer checker interface;
10. compute POST-validation SHA256;
11. require PRE == POST for all three files;
12. write aggregate private evidence;
13. exit nonzero if any Phase33 check fails.

No auto-fix mode.

==================================================
STRICT CSV PREFLIGHT
==================================================

Before task-specific checks, validate each final CSV as a well-formed CSV.

Require:

file exists

regular file

nonempty

header parses

all logical rows have expected field count

no duplicate header names

no unexpected index column

no blank logical data row

UTF-8/standard CSV readability according to repository convention

No row rewrite.

Do not fail solely because line endings differ from another platform.

==================================================
READ RAW + TYPED
==================================================

For identity/format-sensitive checks, use two views:

RAW CSV view:
for exact header text
raw blanks
trip_id textual format
whitespace/placeholders

TYPED dataframe/table view:
for numeric finite/range/comparison checks

Do not let pandas convert blank deferred fields to NaN and then claim the
raw CSV was blank without checking the raw record.

==================================================
DT-420 — TEST TASK1 FILENAME
==================================================

Require exact basename:

submission_task1.csv

Case-sensitive for the final competition package.

Reject alternatives such as:

Submission_Task1.csv
submission_task1 (1).csv
submission_task1_final.csv

The validator should resolve the expected canonical path under outputs/ or
the configured final submission directory.

This is an official requirement.

==================================================
DT-421 — TEST TASK1 COLUMNS
==================================================

Require exactly, in order:

delivery_id
pred_service_min
pred_late_prob

No extra index column.

No uncertainty columns.

No debugging columns.

No unnamed column.

The official instruction says fill only the two prediction columns while
preserving delivery_id.

==================================================
DT-422 — TEST TASK1 ROW COUNT
==================================================

Compare final file to the official Task1 submission template.

Require:

final row count == template row count

No added rows.

No removed rows.

Do not use a remembered hardcoded row count.

Read it locally from the official template.

==================================================
DT-423 — TEST TASK1 ROW ORDER
==================================================

This is explicitly official.

Compare:

final delivery_id sequence

to:

official Task1 template delivery_id sequence

Require exact row-by-row equality.

Do NOT sort either side before comparison.

Set equality alone is insufficient.

==================================================
DT-424 — TEST TASK1 IDS UNCHANGED
==================================================

Require:

same identifiers as template

same spelling

same case

same values

no blank delivery_id

no duplicate delivery_id unless the official template itself contains one
(which should be treated as an upstream official-contract issue)

Because DT-423 already checks sequence, DT-424 should provide a separate
identity-integrity diagnostic.

If mismatch:
report counts only in normal console output.

Do not print private IDs externally.

==================================================
DT-425 — TEST TASK1 PREDICTIONS FINITE
==================================================

Check both:

pred_service_min
pred_late_prob

Require:

numeric

not blank

not NaN

not +Inf

not -Inf

The master task says predictions finite.

Additional WayLoom engineering guard:

pred_service_min >= 0

because service time is a duration and the frozen Task1 pipeline already
post-processes accordingly.

Label this nonnegative service check as an engineering/final-pipeline
invariant, not a separately quoted organizer output rule.

==================================================
DT-426 — TEST TASK1 PROBABILITIES IN RANGE
==================================================

Require every:

pred_late_prob

satisfies:

0 <= pred_late_prob <= 1

Endpoints 0 and 1 are valid.

Reject:

-0.0001
1.0001
NaN
Inf
strings

No clipping in Phase33.

If a value is invalid:
FAIL and reopen Task1 final inference/output phase.

==================================================
TASK1 ADDITIONAL STRUCTURAL GUARDS
==================================================

Also require:

no prediction cell blank

no placeholder text

delivery_id column unchanged

prediction columns contain parseable numeric values only

official file hash unchanged after validation

These are enhancements under the Phase33 gate, not new task IDs.

==================================================
DT-427 — TEST TASK2A FILENAME
==================================================

Require exact basename:

submission_task2a.csv

Reject renamed variants.

Also validate exact structural schema as an enhanced Phase33 guard:

row_id
pred_total_volume_m3
pred_chilled_volume_m3

in that order.

No extra columns.

==================================================
DT-428 — TEST TASK2A ROW IDS UNCHANGED
==================================================

Compare to the official Task2A template.

Require:

same row count

same row_id values

no blank row_id

no unexpected duplicate

all supplied rows preserved

WayLoom final-safety guard:

preserve template row order exactly.

The booklet explicitly singles out original row order for Task1, while the
general submission-template instruction says all supplied rows/identifiers
must remain unchanged. Preserving Task2A template order is a conservative
engineering guard and matches the frozen Phase17 output contract.

Do not sort to pass.

==================================================
TASK2A BRAND LOOKUP
==================================================

The final submission only contains row_id + two predictions.

DT-430 / DT-431 need the brand.

Use official:

task2a_test_inputs.csv

joined by:

row_id

locally.

Validate:

one-to-one row_id mapping

all final row_ids mapped

no extra final row_ids

Do not infer brand from row_id text.

Do not hardcode row positions.

==================================================
DT-429 — TEST TASK2A PREDICTIONS NONNEGATIVE
==================================================

Check:

pred_total_volume_m3

pred_chilled_volume_m3

Require:

numeric

finite

>= 0

Reject:

blank

NaN

Inf

negative zero is numerically zero and may be normalized only for comparison,
but Phase33 must not rewrite the file.

If the raw representation "-0.0" exists:
report a non-blocking formatting warning unless repository policy already
requires canonical positive zero; semantic value is zero.

==================================================
DT-430 — TEST STYLE CHILLED EXACTLY ZERO
==================================================

For rows whose official Task2A test input brand is:

Style

require:

pred_chilled_volume_m3 == 0

Use exact numeric zero after valid numeric parsing.

Do not use a tolerance that permits small positive/negative chilled volume.

Examples that must FAIL:

0.000001
-0.000001
NaN

0.0 and -0.0 are numerically zero; follow repository formatting policy for
raw representation warning.

==================================================
DT-431 — TEST TECH CHILLED EXACTLY ZERO
==================================================

For brand:

Tech

require:

pred_chilled_volume_m3 == 0

Same exact semantics as DT-430.

Do not accidentally test only one non-Fresh brand.

Separate tests for Style and Tech are mandatory.

==================================================
DT-432 — TEST CHILLED <= TOTAL
==================================================

For every Task2A row:

pred_chilled_volume_m3
<=
pred_total_volume_m3

This is a final WayLoom output invariant and follows the meaning of chilled
as a portion of total demand.

Require both values already finite/nonnegative.

Do not "repair" a violation by clipping in Phase33.

Reopen Phase17/final output logic if it fails.

==================================================
TASK2A ADDITIONAL STRUCTURAL GUARDS
==================================================

Require:

exact three columns

row count matches template

template row order preserved

all numeric prediction cells populated

no placeholders

no extra rows

no missing rows

official final CSV hash unchanged

==================================================
DT-433 — TEST TASK2B FILENAME
==================================================

Require exact basename:

submission_task2b.csv

Also validate exact official columns in order:

scenario
order_ref
outlet_id
decision
vehicle_id
trip_id

No extra diagnostic columns.

No index column.

==================================================
DT-434 — TEST TASK2B ALL ORDERS PRESENT
==================================================

Compare final Task2B file to the official Task2B submission template.

Require:

same row count

same order_ref set

same order_ref sequence as template as a final-safety guard

same scenario row-by-row

same outlet_id row-by-row

no blank order_ref

no duplicate order_ref unless official template itself is invalid

Every official order must appear exactly once.

Do NOT use outlet_id as the allocation key.

outlet_id may repeat.

==================================================
TASK2B IDENTITY TRIPLE
==================================================

Validate row-by-row:

scenario
order_ref
outlet_id

against template.

This prevents an allocation from being attached to the wrong order/outlet
while still containing the same number of rows.

No sorting.

==================================================
DT-435 — TEST TASK2B ALL PLACEHOLDERS REMOVED
==================================================

The official template says answer columns contain placeholders and every
placeholder must be replaced.

Scan raw:

decision
vehicle_id
trip_id

for template/placeholding values including the supplied forms such as:

(served/deferred)

(e.g. VEH014)

(1 or 2)

Also reject generic unresolved markers:

TODO
TBD
PLACEHOLDER
<...>
[...]
fill here

Only apply patterns to answer fields so legitimate identity strings are not
falsely rejected.

Blank is permitted only where the final Task2B contract permits it:

vehicle_id / trip_id for deferred orders.

decision can never be blank.

==================================================
DT-436 — TEST SERVED/DEFERRED SPELLING / FORMAT
==================================================

Require decision raw value exactly:

served

or:

deferred

Recommended canonical final format is lowercase with no leading/trailing
whitespace.

Reject:

Served
DEFERRED
serve
defer
served 
 deferred

Do not normalize in Phase33.

==================================================
DT-436 — SERVED FIELD FORMAT
==================================================

When:

decision == served

require:

vehicle_id nonblank after raw CSV parse

trip_id raw text exactly "1" or "2"

No:

1.0
2.0
trip 1
T1

unless the established Phase24 canonical writer officially uses a different
representation; Phase24 contract expects canonical 1/2.

Also reject whitespace-only vehicle_id.

==================================================
DT-436 — DEFERRED FIELD FORMAT
==================================================

When:

decision == deferred

require raw CSV fields:

vehicle_id = empty

trip_id = empty

Do not accept:

NaN
None
null
N/A
-
" "
0

The supplied official requirement says leave these fields blank.

Use raw CSV parsing to prove true blanks.

==================================================
TASK2B STRUCTURAL FORMAT
==================================================

Also require:

scenario == S1

on every row, matching the template.

Final fields:

scenario/order_ref/outlet_id unchanged.

All answer columns fully resolved.

No placeholder.

No malformed CSV row.

==================================================
DT-437 — RUN OFFICIAL CHECKER AGAIN
==================================================

This is a required final Task2B gate.

The official booklet states:

check_allocation.py checks feasibility.

Passing:
confirms feasibility.

It does NOT prove optimality.

Run the organizer checker again against the EXACT final:

outputs/submission_task2b.csv

after DT-433–DT-436 pass.

==================================================
DO NOT GUESS CHECKER CLI
==================================================

The Challenge Booklet names:

check_allocation.py

but does not define its exact CLI invocation.

Phase23 already required discovery of the actual supplied checker interface.

Reuse:

the existing Phase23 checker wrapper/interface/evidence mechanism

when available.

Do not invent:

python check_allocation.py --submission ...

unless that exact interface was verified from the supplied checker.

Do not modify the official checker.

==================================================
DIRECT FINAL-FILE CHECKER PREFERENCE
==================================================

Prefer invoking the official checker directly on:

outputs/submission_task2b.csv

This closes the previous gap where Phase23 may have checked a private
checker-candidate before Phase24 created the final canonical file.

If the official checker interface cannot consume an arbitrary path and
requires a fixed filename/location:

stage a BYTE-IDENTICAL temporary copy in the required location.

Prove:

SHA256(staged copy)
==
SHA256(outputs/submission_task2b.csv)

Record that the checker ran on a byte-identical staged copy.

Do not call this direct-file execution if it was staged.

==================================================
INDEPENDENT VALIDATOR AGAIN
==================================================

Before the organizer checker, rerun the independent Phase23 validator on the
exact final Task2B CSV.

Require:

independent validator PASS

then:

official checker PASS

If they disagree:

STOP.

Do not weaken either validator.

==================================================
OFFICIAL CHECKER EVIDENCE
==================================================

Private evidence should record:

checker filename

checker SHA256

checker invocation mode

working directory

final submission SHA256

staged copy SHA256 if applicable

exit code

PASS/FAIL

stdout/stderr stored privately

timestamp

No modification of checker source.

No row-level allocation details in the sanitized console summary.

==================================================
FINAL TASK2B CHECKER STATUS
==================================================

Console:

INDEPENDENT TASK2B VALIDATOR: PASS

OFFICIAL check_allocation.py: PASS

OFFICIAL CHECKER SEMANTICS:
FEASIBILITY ONLY

Do not write:

OPTIMALITY: PASS

from the official checker.

==================================================
READ-ONLY HASH GUARD
==================================================

Before any validation:

compute SHA256 for:

submission_task1.csv
submission_task2a.csv
submission_task2b.csv

After all validation/checker runs:

compute again.

Require byte-identical equality for all three.

If a validation script changes a file:
FAIL Phase33.

This phase is strictly read-only.

==================================================
TEMPLATE HASH / PROVENANCE
==================================================

For private evidence, record the official template hashes and source paths
relative to the repository/dataset package.

Do not expose test IDs.

Do not require template bytes to match the final files because predictions
replace placeholders.

Use templates only for identity/schema/row reference.

==================================================
NO HARD-CODED ROW COUNTS
==================================================

The validator must not contain remembered numbers such as:

85 Task2B rows

unless that count is read from the official template at runtime.

Why:

final validation should be source-driven.

Tests may use synthetic fixed counts.

Real validation reads template count.

==================================================
NO HARDCODED PASS RESULTS
==================================================

Do not print:

PASS

for a check that was not actually executed.

Examples:

official checker unavailable
→ NOT_RUN / FAIL according to gate, never PASS

template missing
→ FAIL

private local validation not run
→ NOT_RUN

Do not manufacture evidence.

==================================================
FAILURE OUTPUT PRIVACY
==================================================

Normal console/report should show:

failed task ID

check name

failure count

aggregate diagnostic

Do NOT print:

real delivery_id
row_id
order_ref
outlet_id
vehicle_id

by default.

If human needs local debugging:
allow an explicit private debug flag that writes an untracked report under
reports/private only.

Never send those rows externally.

==================================================
UPSTREAM REOPEN MAP
==================================================

Phase33 never auto-fixes.

Recommended blocker routing:

DT-420–DT-426 failure:
reopen Task1 Phase10 final output/inference as appropriate.

DT-427–DT-432 failure:
reopen Task2A Phase17 final output/inference.

DT-433–DT-436 failure:
reopen Phase24 Task2B export/policy output generation.

DT-437 structural checker invocation issue:
repair checker bridge in Phase23/Phase33 without changing allocation.

DT-437 actual feasibility failure:
reopen Task2B Phase22/23/24 validation chain.
Do NOT manually edit submission_task2b.csv.

==================================================
TESTS — TASK1
==================================================

Create:

tests/test_final_submission_task1.py

Use synthetic template/submission fixtures.

Test:

exact filename pass

wrong filename fail

exact columns pass

extra column fail

missing column fail

wrong order fail

row count mismatch fail

row order mismatch fail

ID changed fail

duplicate ID fail

blank ID fail

finite service/prob pass

NaN fail

+Inf fail

-Inf fail

probability 0 pass

probability 1 pass

probability <0 fail

probability >1 fail

negative service fails engineering final invariant

validator does not rewrite file

==================================================
TESTS — TASK2A
==================================================

Create:

tests/test_final_submission_task2a.py

Test:

exact filename

exact three-column schema

row count/template identity

row order

changed row_id fail

duplicate row_id fail

brand lookup one-to-one

finite values

negative total fail

negative chilled fail

Style chilled 0 pass

Style chilled nonzero fail

Tech chilled 0 pass

Tech chilled nonzero fail

Fresh chilled positive allowed

chilled == total pass

chilled < total pass

chilled > total fail

no file modification

==================================================
TESTS — TASK2B
==================================================

Create:

tests/test_final_submission_task2b.py

Test:

exact filename

exact six columns

all orders present

missing order fail

extra order fail

duplicate order_ref fail

outlet_id repeats allowed across different order_ref

scenario/order_ref/outlet_id row identity

wrong scenario fail

placeholder decision fail

placeholder vehicle fail

placeholder trip fail

decision served/deferred lowercase exact

capitalized fail

whitespace fail

served vehicle required

served trip raw "1" pass

served trip raw "2" pass

served trip "1.0" fail

deferred vehicle true blank pass

deferred trip true blank pass

deferred "NaN" fail

deferred whitespace fail

no rewrite

==================================================
TESTS — CONTRACT ORCHESTRATOR
==================================================

Create:

tests/test_final_submission_contract.py

Test:

all 18 DT mappings represented

all three filenames exact

pre/post hashes equal

validator failure -> nonzero exit

single failed task prevents overall PASS

missing template fails

missing submission fails

no hardcoded real row counts

aggregate-only failure output

report statuses not fabricated

==================================================
TESTS — READ ONLY
==================================================

Create:

tests/test_final_submission_readonly.py

Use temp files.

Snapshot bytes/hashes.

Run validators.

Require all input CSV/template bytes unchanged.

Test both PASS and FAIL cases.

A validator must not rewrite even on failure.

==================================================
TESTS — CHECKER BRIDGE
==================================================

Create:

tests/test_final_submission_checker_bridge.py

Use synthetic/mock checker fixtures.

Test:

actual checker interface adapter invoked

checker PASS recognized

checker FAIL recognized

checker crash -> FAIL/blocked

checker missing -> FAIL/blocked

checker source not modified

final file hash recorded

staged-copy mode requires byte-identical SHA

staged mismatch fails

no invented optimality claim

independent validator disagreement fails

No real official checker execution in external-agent tests.

==================================================
SAFE AGENT TEST LOOP
==================================================

Run:

pytest -q \
  tests/test_final_submission_task1.py \
  tests/test_final_submission_task2a.py \
  tests/test_final_submission_task2b.py \
  tests/test_final_submission_contract.py \
  tests/test_final_submission_readonly.py \
  tests/test_final_submission_checker_bridge.py

Then relevant Phase10/17/23/24 validator regression tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do NOT open/run against private real final CSVs in external-agent context.

==================================================
LOCAL HUMAN COMMAND
==================================================

Expected stable validator interface:

python scripts/validate_final_submissions.py \
  --config configs/final_submission_validation.yaml \
  --dataset-manifest configs/dataset_manifest.yaml \
  --submission-dir outputs \
  --report-dir reports/private/phase33_final_submissions

The script should discover official template/test/checker locations through
the repository's canonical manifest/config and existing Phase23 checker
bridge.

If actual repository needs an explicit checker-root argument, use the
discovered local interface.

Do not invent data paths.

==================================================
LOCAL HUMAN EXPECTED RESULT
==================================================

WAYLOOM — PHASE 33 FINAL SUBMISSION VALIDATION

TASK1
DT-420 FILENAME                         : PASS
DT-421 COLUMNS                          : PASS
DT-422 ROW COUNT                        : PASS
DT-423 ROW ORDER                        : PASS
DT-424 IDS UNCHANGED                    : PASS
DT-425 PREDICTIONS FINITE               : PASS
DT-426 PROBABILITIES [0,1]              : PASS

TASK2A
DT-427 FILENAME                         : PASS
DT-428 ROW IDS UNCHANGED                : PASS
DT-429 PREDICTIONS NONNEGATIVE          : PASS
DT-430 STYLE CHILLED = 0                : PASS
DT-431 TECH CHILLED = 0                 : PASS
DT-432 CHILLED <= TOTAL                 : PASS

TASK2B
DT-433 FILENAME                         : PASS
DT-434 ALL ORDERS PRESENT               : PASS
DT-435 PLACEHOLDERS REMOVED             : PASS
DT-436 DECISION/FIELD FORMAT            : PASS
INDEPENDENT TASK2B VALIDATOR             : PASS
DT-437 OFFICIAL check_allocation.py      : PASS
OFFICIAL CHECKER SEMANTICS               : FEASIBILITY ONLY

READ-ONLY HASH GUARD
submission_task1.csv                     : UNCHANGED
submission_task2a.csv                    : UNCHANGED
submission_task2b.csv                    : UNCHANGED

PHASE 33                                 : PASS
READY FOR PHASE 34                       : YES

No real IDs should be printed.

==================================================
PRIVATE EVIDENCE
==================================================

Create locally:

reports/private/phase33_final_submissions/phase33_gate.json

Recommended safe aggregate:

phase = 33

status = PASS

dt420 ... dt437 = PASS

task1_hash_unchanged = true

task2a_hash_unchanged = true

task2b_hash_unchanged = true

independent_task2b_validator = PASS

official_checker = PASS

official_checker_semantics = feasibility_only

No real IDs.

==================================================
STOP CONDITIONS
==================================================

STOP if:

any DT-420–DT-437 check fails

wrong filename

extra/missing columns

row count differs from template

Task1 row order differs

Task1 ID differs

Task1 NaN/Inf prediction

Task1 late probability outside [0,1]

Task2A row_id mismatch

Task2A row/template mismatch

Task2A negative/NaN/Inf volume

Style chilled !=0

Tech chilled !=0

chilled > total

Task2B missing/extra/duplicate order_ref

Task2B identity triple mismatch

Task2B unresolved placeholder

decision not exact served/deferred

served row lacks vehicle/trip

served trip not canonical 1/2

deferred vehicle/trip not truly blank

independent Task2B validator fails

official checker interface would need guessing

official checker missing/crashes/fails

official checker source modified

official checker and independent validator disagree

validation modifies any final CSV

private row IDs printed in normal report

Phase34 work introduced

tests fail

pip check fails

==================================================
DEFINITION OF DONE
==================================================

Require:

DT-420 PASS
DT-421 PASS
DT-422 PASS
DT-423 PASS
DT-424 PASS
DT-425 PASS
DT-426 PASS
DT-427 PASS
DT-428 PASS
DT-429 PASS
DT-430 PASS
DT-431 PASS
DT-432 PASS
DT-433 PASS
DT-434 PASS
DT-435 PASS
DT-436 PASS
DT-437 PASS

exact Task1 filename

exact Task1 3-column schema

Task1 template row count

Task1 original row order

Task1 IDs exact

Task1 finite predictions

Task1 probability bounds

exact Task2A filename

Task2A exact schema

Task2A template identity/order

Task2A finite/nonnegative values

Style chilled zero

Tech chilled zero

chilled <= total

exact Task2B filename

Task2B exact six-column schema

all official orders exactly once

scenario/order_ref/outlet_id exact

no placeholders

canonical served/deferred formatting

served/deferred dependent field formatting

independent Task2B validator PASS

official checker PASS on exact final file or proven byte-identical staged copy

checker feasibility-only semantics documented

all three final CSV pre/post hashes unchanged

targeted tests PASS

relevant regression tests PASS

full safe suite PASS

pip check PASS

git diff check PASS

fresh independent Phase33 review PASS

Then:

PHASE 33 STATUS: PASS
FINAL SUBMISSION FILES: VALIDATED
TASK2B OFFICIAL CHECKER: PASS
OFFICIAL SUBMISSION CSVs: UNCHANGED
READY FOR PHASE 34: YES

==================================================
GIT WORKFLOW
==================================================

Recommended branch:

git checkout main
git pull
git checkout -b test/phase-33-final-submissions

If prior validated work is not yet merged:
branch from the correct validated commit according to team workflow without
losing work.

Recommended commits:

test(submissions): add strict Task1 final CSV validation
test(submissions): add strict Task2A final CSV validation
test(submissions): add Task2B final format and checker gate
test(submissions): add read-only integrity guards
docs(submissions): document final submission validation

Before commit:

git status
git diff
git diff --check

Never stage:

data/raw/**
data/interim/**
reports/private/**

Do not modify/stage regenerated official CSVs in Phase33.

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-420 READY
DT-421 READY
DT-422 READY
DT-423 READY
DT-424 READY
DT-425 READY
DT-426 READY
DT-427 READY
DT-428 READY
DT-429 READY
DT-430 READY
DT-431 READY
DT-432 READY
DT-433 READY
DT-434 READY
DT-435 READY
DT-436 READY
DT-437 READY

no private rows accessed

no final CSV rewritten

official checker bridge reused correctly

no Phase34 work

==================================================
RETURN ONLY
==================================================

PHASE:
33 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-420 READY / FAIL
DT-421 READY / FAIL
DT-422 READY / FAIL
DT-423 READY / FAIL
DT-424 READY / FAIL
DT-425 READY / FAIL
DT-426 READY / FAIL
DT-427 READY / FAIL
DT-428 READY / FAIL
DT-429 READY / FAIL
DT-430 READY / FAIL
DT-431 READY / FAIL
DT-432 READY / FAIL
DT-433 READY / FAIL
DT-434 READY / FAIL
DT-435 READY / FAIL
DT-436 READY / FAIL
DT-437 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TASK1 VALIDATOR:
PASS / FAIL

TASK2A VALIDATOR:
PASS / FAIL

TASK2B VALIDATOR:
PASS / FAIL

OFFICIAL CHECKER BRIDGE:
PASS / FAIL

READ-ONLY HASH GUARD:
PASS / FAIL

TARGETED TESTS:
...

FULL SAFE SUITE:
...

PIP CHECK:
PASS / FAIL

GIT DIFF CHECK:
PASS / FAIL

PRIVATE REAL SUBMISSION ROWS ACCESSED:
NO

OFFICIAL CSVs MODIFIED:
NO

PHASE34 WORK:
NONE

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase33 validation command.

PHASE33 AGENT STATUS:
AWAITING HUMAN-LOCAL FINAL FILE VALIDATION

READY FOR FRESH PHASE33 INDEPENDENT REVIEW:
NO

READY FOR PHASE34:
NO

Then STOP.

Do not start Phase34.

```

---

# 130. Fresh independent Phase 33 review prompt

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon PHASE 33.

PHASE:
Final Submission-File Testing

TASK RANGE:
DT-420 through DT-437

REVIEW MODE:
FRESH SESSION
READ-ONLY
FINAL-FILE COMPLIANCE AUDIT

Do NOT implement Phase34.
Do NOT modify final CSV files.
Do NOT retrain models.
Do NOT rerun Task2B optimizer.
Do NOT inspect private row-level competition data.
Use sanitized human-local Phase33 evidence for real files.

==================================================
READ
==================================================

Read:

1. Official Challenge Booklet
   - Task1 outputs
   - Task2A outputs
   - Task2B outputs
   - submission templates
   - check_allocation.py semantics

2. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase33

3. PHASE_10_COMPETITION_CONTRACT.md
4. PHASE_17_COMPETITION_CONTRACT.md
5. PHASE_23_COMPETITION_CONTRACT.md
6. PHASE_24_COMPETITION_CONTRACT.md
7. PHASE_33_COMPETITION_CONTRACT.md

Inspect:

configs/final_submission_validation.yaml

src/common/submission_validation.py
src/task1/final_submission_validation.py
src/task2a/final_submission_validation.py
src/task2b/final_submission_validation.py
or actual equivalents

scripts/validate_final_submissions.py

docs/final_submission_validation.md

tests/test_final_submission_task1.py
tests/test_final_submission_task2a.py
tests/test_final_submission_task2b.py
tests/test_final_submission_contract.py
tests/test_final_submission_readonly.py
tests/test_final_submission_checker_bridge.py

Do not open real outputs or private templates.

==================================================
HUMAN SANITIZED LOCAL EVIDENCE
==================================================

DT-420: <PASS/FAIL>
DT-421: <PASS/FAIL>
DT-422: <PASS/FAIL>
DT-423: <PASS/FAIL>
DT-424: <PASS/FAIL>
DT-425: <PASS/FAIL>
DT-426: <PASS/FAIL>

DT-427: <PASS/FAIL>
DT-428: <PASS/FAIL>
DT-429: <PASS/FAIL>
DT-430: <PASS/FAIL>
DT-431: <PASS/FAIL>
DT-432: <PASS/FAIL>

DT-433: <PASS/FAIL>
DT-434: <PASS/FAIL>
DT-435: <PASS/FAIL>
DT-436: <PASS/FAIL>

INDEPENDENT TASK2B VALIDATOR:
<PASS/FAIL>

DT-437 OFFICIAL check_allocation.py:
<PASS/FAIL>

OFFICIAL CHECKER INPUT MODE:
<DIRECT FINAL FILE / BYTE-IDENTICAL STAGED COPY>

IF STAGED:
FINAL/STAGED SHA256 PARITY:
<PASS/FAIL>

TASK1 PRE/POST HASH:
<UNCHANGED/FAIL>

TASK2A PRE/POST HASH:
<UNCHANGED/FAIL>

TASK2B PRE/POST HASH:
<UNCHANGED/FAIL>

No IDs/rows should be supplied.

==================================================
AUDIT OFFICIAL CONTRACT
==================================================

Confirm official filenames:

submission_task1.csv
submission_task2a.csv
submission_task2b.csv

Confirm official identifier preservation.

Confirm Task1 original row order.

Confirm Task1 exact prediction columns.

Confirm Task2A row_id and two prediction columns.

Confirm Style/Tech chilled zero.

Confirm Task2B identity fields and answer fields.

Confirm placeholders removed.

Confirm deferred vehicle/trip blank.

Confirm official checker is feasibility-only.

==================================================
AUDIT DT-420–DT-426
==================================================

Task1:

DT-420 exact filename.

DT-421 exactly:
delivery_id
pred_service_min
pred_late_prob
in order.

DT-422 row count from official template, not hardcoded.

DT-423 delivery_id sequence exact, no sorting.

DT-424 IDs unchanged.

DT-425 both prediction fields finite; engineering service nonnegative guard
must be correctly labelled as such.

DT-426 pred_late_prob in inclusive [0,1].

Check validators never repair/clip/rewrite.

==================================================
AUDIT DT-427–DT-432
==================================================

Task2A:

DT-427 exact filename and enhanced exact schema.

DT-428 row_id identity against template; conservative row-order guard allowed
and should be labelled engineering/frozen-contract safety.

DT-429 numeric finite and nonnegative.

DT-430 Style chilled exactly zero.

DT-431 Tech chilled exactly zero.

DT-432 chilled <= total.

Brand must come from canonical Task2A test input mapping by row_id.

No row-position inference.

No tolerance for nonzero Style/Tech chilled.

==================================================
AUDIT DT-433–DT-436
==================================================

Task2B:

DT-433 exact filename + six official columns.

DT-434 every official order exactly once and identity triple preserved.

order_ref is the key.
outlet_id repetition allowed.

DT-435 all supplied answer placeholders removed.

DT-436:
decision exactly lowercase served/deferred.

Served:
vehicle_id populated
trip_id raw 1 or 2

Deferred:
vehicle_id raw blank
trip_id raw blank

No NaN/null marker accepted as blank.

Check raw CSV validation exists.

==================================================
AUDIT DT-437
==================================================

Require:

Phase23 independent validator rerun on final Task2B CSV.

Official checker run again.

Checker interface is actual discovered organizer interface, not guessed.

Official checker source unmodified.

Prefer direct exact final file.

If staging needed:
staged copy is byte-identical by SHA256.

Checker PASS.

Independent validator PASS.

No disagreement.

Checker described as feasibility-only.

No optimality claim.

==================================================
AUDIT READ-ONLY BEHAVIOR
==================================================

Phase33 must not modify final files.

Check code for:

to_csv
write_text
open(..., "w")
rename/replace
sorting-and-saving
normalization-and-saving

against canonical final CSV paths.

Synthetic test writers in temporary directories are fine.

Human pre/post hashes must be unchanged.

==================================================
AUDIT NO HARDCODED REAL COUNTS / PASS
==================================================

Validator should read row counts from official templates.

Do not accept a real production path that hardcodes:

85
or any remembered row count.

Do not accept:

official_checker = PASS

without execution evidence.

Missing checker/template/file must fail or report NOT_RUN according to state;
final Phase33 gate requires actual PASS.

==================================================
PRIVACY AUDIT
==================================================

Normal failures should print counts/check names, not real IDs.

Private debugging may be untracked and explicit.

Tracked docs/tests/config:

no real submission rows
no real IDs
no private paths
no private checker output

==================================================
RUN SAFE TESTS
==================================================

Run:

pytest -q \
  tests/test_final_submission_task1.py \
  tests/test_final_submission_task2a.py \
  tests/test_final_submission_task2b.py \
  tests/test_final_submission_contract.py \
  tests/test_final_submission_readonly.py \
  tests/test_final_submission_checker_bridge.py

Then relevant Phase10/17/23/24 validator regression tests.

Then:

pytest -q

python -m pip check

git diff --check

git status

Do not run against real private files.

==================================================
RETURN FORMAT
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

OFFICIAL FILENAMES:
PASS / FAIL

TASK1 EXACT SCHEMA:
PASS / FAIL

TASK1 ROW COUNT:
PASS / FAIL

TASK1 ROW ORDER:
PASS / FAIL

TASK1 IDS:
PASS / FAIL

TASK1 FINITE PREDICTIONS:
PASS / FAIL

TASK1 PROBABILITY RANGE:
PASS / FAIL

TASK2A EXACT SCHEMA:
PASS / FAIL

TASK2A ROW IDENTITY:
PASS / FAIL

TASK2A FINITE/NONNEGATIVE:
PASS / FAIL

STYLE CHILLED ZERO:
PASS / FAIL

TECH CHILLED ZERO:
PASS / FAIL

CHILLED <= TOTAL:
PASS / FAIL

TASK2B EXACT SCHEMA:
PASS / FAIL

TASK2B ALL ORDERS:
PASS / FAIL

TASK2B PLACEHOLDERS:
PASS / FAIL

TASK2B DECISION/FIELD FORMAT:
PASS / FAIL

INDEPENDENT TASK2B VALIDATOR:
PASS / FAIL

OFFICIAL TASK2B CHECKER:
PASS / FAIL

CHECKER INPUT FINAL-FILE PARITY:
PASS / NOT_APPLICABLE / FAIL

OFFICIAL CHECKER SEMANTICS:
FEASIBILITY_ONLY / FAIL

READ-ONLY HASH GUARD:
PASS / FAIL

NO HARDCODED REAL ROW COUNTS:
PASS / FAIL

NO FABRICATED PASS STATUS:
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

DT-420: PASS/FAIL
DT-421: PASS/FAIL
DT-422: PASS/FAIL
DT-423: PASS/FAIL
DT-424: PASS/FAIL
DT-425: PASS/FAIL
DT-426: PASS/FAIL
DT-427: PASS/FAIL
DT-428: PASS/FAIL
DT-429: PASS/FAIL
DT-430: PASS/FAIL
DT-431: PASS/FAIL
DT-432: PASS/FAIL
DT-433: PASS/FAIL
DT-434: PASS/FAIL
DT-435: PASS/FAIL
DT-436: PASS/FAIL
DT-437: PASS/FAIL

PHASE 33 INDEPENDENT REVIEW:
PASS / FAIL

FINAL SUBMISSION FILES:
VALIDATED / NOT VALIDATED

OFFICIAL SUBMISSION CSVs:
UNCHANGED / CHANGED

READY FOR PHASE 34:
YES / NO

If PASS:

PHASE 33 INDEPENDENT REVIEW: PASS
FINAL SUBMISSION FILES: VALIDATED
TASK2B OFFICIAL CHECKER: PASS
OFFICIAL SUBMISSION CSVs: UNCHANGED
BLOCKERS: None
READY FOR PHASE 34: YES

Then STOP.

Do not start Phase34.

```

---

# 131. Final checklist

Before Phase 34:

- [x] Exact DT-420–DT-437 coverage.
- [x] All three exact official filenames.
- [x] Task1 exact three-column schema.
- [x] Task1 template row count.
- [x] Task1 original row order.
- [x] Task1 identifiers exact.
- [x] Task1 predictions finite.
- [x] Task1 probabilities [0,1].
- [x] Task2A exact three-column schema.
- [x] Task2A row IDs/template rows exact.
- [x] Task2A values finite/nonnegative.
- [x] Style chilled exactly zero.
- [x] Tech chilled exactly zero.
- [x] chilled <= total.
- [x] Task2B exact six-column schema.
- [x] Every official Task2B order exactly once.
- [x] Task2B identity triple exact.
- [x] No placeholders.
- [x] `decision` exact lowercase `served` / `deferred`.
- [x] Served vehicle/trip populated/canonical.
- [x] Deferred vehicle/trip raw blank.
- [x] Independent Task2B validator PASS.
- [x] Official `check_allocation.py` PASS on final bytes.
- [x] Official checker = feasibility only.
- [x] Final CSV pre/post hashes unchanged.
- [x] No hardcoded real row counts.
- [x] No fabricated check status.
- [x] No private IDs in normal output.
- [x] Targeted Phase33 tests PASS.
- [x] Prior validator regressions PASS.
- [x] Full safe suite PASS.
- [x] `pip check` PASS.
- [x] `git diff --check` PASS.
- [x] Fresh independent Phase33 review PASS.

Only then:

```text
PHASE 33 STATUS: PASS
FINAL SUBMISSION FILES: VALIDATED
TASK2B OFFICIAL CHECKER: PASS
OFFICIAL SUBMISSION CSVs: UNCHANGED
READY FOR PHASE 34: YES
```
