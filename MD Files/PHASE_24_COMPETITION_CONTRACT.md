# PHASE 24 — Task 2B Output and Written Policy

> **Filename:** `PHASE_24_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026  
> **Canonical phase:** Phase 24 — Task 2B Output and Written Policy  
> **Task range:** **DT-331 → DT-342**  
> **Task count:** **12**  
> **Default phase priority:** **P0**  
> **Phase dependency:** **Phase 23**  
> **Phase gate:** Exact `submission_task2b.csv` and approximately one-page prioritization policy are complete, evidence-grounded and defensible.  
> **Execution mode:** Read-only export from the frozen Phase 22 allocation + deterministic policy-evidence generation.  
> **Do not re-optimize or manually alter any Task 2B decision in this phase.**

---

# 1. Purpose

Phase 24 converts the already validated and frozen Task 2B allocation into the **official competition output** and the required written explanation.

The official challenge requires two Task 2B deliverables:

```text
submission_task2b.csv
```

and:

```text
a short written prioritization policy
```

The output file must preserve the organizer-supplied identity columns and replace the answer placeholders with the final served/deferred allocation.

The written policy must be approximately one page or less and must:

```text
show the calculations behind the allocation
identify what limited service on the day
explain which deferrals were unavoidable
explain which deferrals were a choice
explain what those deferrals cost
```

Phase 24 must not change the allocation that already passed Phase 23.

Its job is:

```text
frozen allocation
+
official template
+
validated evidence
→
exact final CSV
+
short defensible policy
```

---

# 2. Finalized Phase 24 task inventory

The finalized WayLoom master inventory defines exactly:

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-331** | [O] | P0 | DT-329–DT-330 | Populate official Task 2B template |
| [ ] | **DT-332** | [O] | P0 | Phase 23 | Preserve scenario |
| [ ] | **DT-333** | [O] | P0 | Phase 23 | Preserve order_ref |
| [ ] | **DT-334** | [O] | P0 | Phase 23 | Preserve outlet_id |
| [ ] | **DT-335** | [O] | P0 | Phase 23 | Remove every placeholder |
| [ ] | **DT-336** | [O] | P0 | Phase 23 | Export submission_task2b.csv |
| [ ] | **DT-337** | [O] | P0 | DT-331–DT-336 | Write one-page prioritization policy |
| [ ] | **DT-338** | [O] | P0 | Phase 23 | Explain limiting resources |
| [ ] | **DT-339** | [O] | P0 | Phase 23 | Explain allocation calculations |
| [ ] | **DT-340** | [O] | P0 | Phase 23 | Explain unavoidable deferrals |
| [ ] | **DT-341** | [O] | P0 | Phase 23 | Explain policy-choice deferrals |
| [ ] | **DT-342** | [O] | P0 | Phase 23 | Explain cost/impact of deferrals |

**Expected Phase 24 tasks:** 12  
**Missing tasks allowed:** 0  
**Phase complete:** [ ]  
**READY FOR PHASE 25:** NO

---

# 3. Official Task 2B output contract

The official Challenge Booklet says to complete the organizer-supplied:

```text
Submission Templates/submission_task2b.csv
```

and keep:

```text
scenario
order_ref
outlet_id
```

unchanged.

The answer columns are:

```text
decision
vehicle_id
trip_id
```

Official field contract:

| Column | Official requirement |
|---|---|
| `scenario` | Supplied identifier; always `S1`. |
| `order_ref` | Supplied order identifier and allocation key. |
| `outlet_id` | Supplied outlet identifier; may repeat. |
| `decision` | `served` or `deferred`. |
| `vehicle_id` | Assigned vehicle for served; blank for deferred. |
| `trip_id` | `1` or `2` for served; blank for deferred. |

The supplied template answer columns contain placeholders.

Every placeholder must be replaced.

---

# 4. Official template preservation contract

The general Datathon template rule says:

```text
Use the exact filenames.
Keep all supplied identifiers and rows unchanged.
Fill the answer columns and replace any placeholders.
```

Task 1 alone has an additional explicit original-row-order rule.

For Task 2B, WayLoom will nevertheless preserve the organizer template row order as a **safe engineering guarantee**.

This phase must therefore:

- use the official template as the export base;
- preserve every supplied row;
- preserve every `scenario`;
- preserve every `order_ref`;
- preserve every `outlet_id`;
- preserve template row order;
- fill only the three answer columns;
- output the exact filename.

Do not construct an unrelated replacement CSV from scratch.

---

# 5. Phase 24 preconditions

Before any real-data export:

```text
Phase 22 final allocation = FROZEN
Phase 23 own validator = PASS
Phase 23 official check_allocation.py = PASS
Phase 23 checker evidence = SAVED
```

Require Phase 22 allocation SHA256 to still match the freeze manifest.

Require Phase 23 checker evidence to reference the same frozen allocation.

If any precondition fails:

```text
STOP
```

Do not attempt to "finish the CSV anyway."

---

# 6. Frozen-allocation immutability

Phase 24 is **not an optimization phase**.

Do not alter:

```text
data/interim/task2b_final_allocation.csv
```

Do not:

- change served to deferred;
- change deferred to served;
- change a vehicle;
- change a trip ID;
- move an order;
- combine trips;
- split orders;
- modify the frozen priority policy.

Any allocation problem discovered in Phase 24 requires:

```text
reopen Phase 22
→ rerun optimizer
→ refreeze
→ rerun Phase 23
→ return to Phase 24
```

---

# 7. Recommended repository additions

Create/update:

```text
src/task2b/submission.py
src/task2b/policy_writer.py
src/task2b/policy_evidence.py

scripts/export_task2b_submission.py
scripts/build_task2b_policy.py
scripts/validate_phase24_task2b_output.py

configs/task2b_output.yaml

docs/task2b_policy.md
docs/task2b_output_spec.md

tests/test_task2b_submission.py
tests/test_task2b_policy_writer.py
tests/test_task2b_phase24_output.py
```

Reuse:

```text
src/task2b/scenario.py
src/task2b/trip_time.py
src/task2b/priority.py
src/task2b/policy_metrics.py
src/task2b/allocation_validator.py
```

Do not create Phase 25 explainability implementation.

---

# 8. Phase 24 final and private outputs

## Official final Task 2B CSV

```text
outputs/submission_task2b.csv
```

## Written policy

Canonical project path:

```text
docs/task2b_policy.md
```

This file is intended for the competition submission package.

## Private reports

```text
reports/private/phase24_task2b_output/
├── export_manifest.json
├── template_identity_audit.json
├── placeholder_audit.json
├── allocation_parity_audit.json
├── policy_evidence_context.json
├── policy_fact_validation.json
├── policy_length_check.json
├── warnings.json
└── phase24_output_report.md
```

Do not commit private reports.

---

# 9. Recommended output configuration

Create:

```text
configs/task2b_output.yaml
```

Suggested structure:

```yaml
version: 1

submission:
  filename: submission_task2b.csv
  output_path: outputs/submission_task2b.csv

  columns:
    - scenario
    - order_ref
    - outlet_id
    - decision
    - vehicle_id
    - trip_id

  identity_columns:
    - scenario
    - order_ref
    - outlet_id

  answer_columns:
    - decision
    - vehicle_id
    - trip_id

  preserve_template_row_order: true
  write_index: false
  atomic_write: true
  refuse_unapproved_overwrite: true

policy:
  output_path: docs/task2b_policy.md
  target_word_count_max: 550
  warning_word_count_max: 650
  include_monetary_cost_estimate: false

reports:
  private_output_dir: reports/private/phase24_task2b_output
```

The word-count limits are engineering guards, not official competition numbers.

---

# 10. Canonical Task 2B export strategy

The final output should be created by:

```text
OFFICIAL TEMPLATE
        ↓
validate template identities
        ↓
join FROZEN allocation by order_ref
        ↓
verify scenario/outlet identity parity
        ↓
fill ONLY decision/vehicle_id/trip_id
        ↓
remove/validate placeholders
        ↓
write atomically
        ↓
read back
        ↓
validate exact schema/identities/answers
        ↓
hash final file
```

Do not generate from a grouped trip table.

Do not sort by vehicle/trip.

Do not make `outlet_id` the join key.

---

# 11. DT-331 — Populate official Task 2B template

## Objective

Fill the organizer-supplied template from the frozen allocation.

## Inputs

Official:

```text
submission_task2b.csv template
```

Frozen:

```text
data/interim/task2b_final_allocation.csv
```

Integrity/evidence:

```text
Phase 22 freeze manifest
Phase 23 checker evidence
```

## Required template checks before join

Require exact columns:

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

Require:

```text
order_ref nonblank
order_ref unique
```

Require template row count equals frozen allocation row count.

Require exact `order_ref` set equality.

## Join

Use:

```text
order_ref
```

only.

Recommended:

```python
template.merge(
    frozen_answers,
    on="order_ref",
    how="left",
    validate="one_to_one",
    sort=False,
)
```

Preserve the template's original row-position marker before join.

## Identity parity

Before filling answers, assert:

```text
template.scenario == frozen/source scenario
template.outlet_id == source/frozen outlet_id
```

If mismatched:

```text
FAIL
```

Do not overwrite the template identity to hide a mismatch.

## Answer fill

Fill only:

```text
decision
vehicle_id
trip_id
```

from the frozen allocation.

---

# 12. DT-332 — Preserve scenario

## Objective

Keep the organizer-supplied `scenario` untouched.

Require final row-by-row:

```text
final.scenario == template.scenario
```

Also require:

```text
all scenario == S1
```

Do not regenerate the column from a constant as a substitute for preserving it.

A constant check can be an additional invariant.

## Tests

- exact preservation;
- S1 passes;
- blank fails;
- non-S1 fails;
- frozen/template mismatch fails.

---

# 13. DT-333 — Preserve order_ref

## Objective

Protect the official allocation identifier.

Require:

```text
final.order_ref
==
template.order_ref
```

row-by-row.

Also:

```text
nonblank
unique
same row count
same set
same template order
```

Do not:

- normalize;
- trim/rewrite;
- regenerate;
- sort;
- use `outlet_id` instead.

## Tests

- exact pass;
- duplicate fail;
- missing fail;
- extra fail;
- reorder fails the Phase 24 safety check;
- repeated outlet with distinct order refs passes.

---

# 14. DT-334 — Preserve outlet_id

Require row-by-row:

```text
final.outlet_id == template.outlet_id
```

Also verify:

```text
outlet_id
```

matches the canonical S1 source for that `order_ref`.

Repeated `outlet_id` values are valid.

Do not deduplicate.

Do not replace with an outlet reference joined through another grain.

---

# 15. DT-335 — Remove every placeholder

The official template explicitly instructs teams to replace all answer placeholders.

The template example includes placeholders such as:

```text
(served/deferred)
(e.g. VEH014)
(1 or 2)
```

Final validation must be semantic, not only token-based.

## Decision

Every row must be exactly:

```text
served
deferred
```

## Served rows

Require:

```text
vehicle_id populated
trip_id in (1, 2)
```

## Deferred rows

Require:

```text
vehicle_id blank
trip_id blank
```

## Additional placeholder denylist

Also fail obvious nonfinal values in answer fields, including:

```text
placeholder
TBD
TODO
N/A
-
<...>
(...)
```

where applicable.

Do not reject valid empty fields for deferred assignments.

Do not repair placeholder values automatically.

---

# 16. DT-336 — Export submission_task2b.csv

## Exact filename

```text
outputs/submission_task2b.csv
```

## Exact column order

```text
scenario
order_ref
outlet_id
decision
vehicle_id
trip_id
```

## Write requirements

Use:

```text
index = false
```

Prefer:

```text
UTF-8
standard CSV
```

Do not add:

```text
Unnamed: 0
debug columns
policy scores
compatibility counts
deferral reasons
trip minutes
```

## Atomic export

Recommended:

1. write temp file in same filesystem;
2. read temp back;
3. run final validation;
4. calculate checksum;
5. replace final path atomically.

## Overwrite protection

Do not silently overwrite an existing final file if:

- source frozen allocation hash differs;
- output hash differs from manifest without explicit approved regeneration.

Allow explicit regeneration only when all Phase 22/23 preconditions still match.

---

# 17. Final submission read-back validation

After export, reopen:

```text
outputs/submission_task2b.csv
```

and independently revalidate.

Require:

```text
file exists
filename exact
column names exact
column order exact
row count exact
template row order preserved
scenario exact
order_ref exact
outlet_id exact
decision exact
served assignment valid
deferred assignment blank
trip ID valid
no placeholders
no duplicate order_ref
no index column
```

Also compare by `order_ref`:

```text
decision
vehicle_id
trip_id
```

against the frozen Phase 22 allocation.

Require exact semantic parity.

---

# 18. Phase 23 checker-candidate parity

Phase 23 ran the organizer checker using a private checker candidate.

If that candidate remains available, compare its six official columns against the Phase 24 final export.

Because Phase 24 starts from the organizer template, row order may be template-controlled.

Compare semantically by:

```text
order_ref
```

Require the same:

```text
scenario
outlet_id
decision
vehicle_id
trip_id
```

If the files disagree:

```text
STOP
```

Do not choose whichever "looks right."

Investigate the export transform.

---

# 19. Export manifest

Create private:

```text
reports/private/phase24_task2b_output/export_manifest.json
```

Recommended content:

```text
phase = 24
state = FINAL_EXPORTED

official_template_sha256

phase22_frozen_allocation_sha256

phase22_freeze_manifest_sha256

phase23_checker_evidence_sha256

phase23_checker_input_sha256

submission_task2b_sha256

row_count

columns

template_row_order_preserved = true

scenario_preserved = true

order_ref_preserved = true

outlet_id_preserved = true

placeholder_audit = PASS

allocation_parity = PASS

timestamp

git_commit
```

Do not include raw rows.

---

# 20. Official written-policy requirement

The official Challenge Booklet requires:

```text
a write-up of approximately one page or less
```

and says the analysis should:

```text
show the calculations behind your allocation

identify what limited service on this day

explain which deferrals were unavoidable

explain which deferrals were your choice

explain what they cost
```

This is a judged part of:

```text
Task 2B allocation feasibility and prioritization policy
```

Therefore the policy must be concise but evidence-rich.

---

# 21. Source-grounded meaning of "cost"

The official source asks teams to explain:

```text
what deferrals cost
```

but the supplied Task 2B source contract described in the booklet does **not** provide:

```text
monetary revenue
margin
delivery penalty
lost-sales value
customer churn cost
currency cost per unit
```

Therefore WayLoom must not invent a monetary estimate.

## Recommended interpretation

Report the deferral "cost/impact" using operational metrics that the official data actually supports.

Examples:

```text
number/share of orders deferred

units deferred

kilograms deferred

cubic metres deferred

chilled demand deferred

previously deferred demand deferred again

days-since-last-served impact

brand-level deferred demand

unique outlets affected
```

State explicitly:

> The supplied scenario data does not contain a monetary cost field, so WayLoom reports the impact of deferrals operationally rather than inventing a currency estimate.

This is an engineering interpretation made to avoid unsupported claims.

---

# 22. Policy generation architecture

Do not ask a generative model to read raw/private scenario rows.

Use a deterministic local evidence builder:

```text
frozen allocation
+
canonical S1 order aggregates
+
Phase 19 scarcity summaries
+
Phase 22 trip summary
+
Phase 23 PASS evidence
→
private aggregate evidence context
```

Then render:

```text
docs/task2b_policy.md
```

from:

```text
pre-approved prose template
+
verified aggregate numbers
```

The model/agent may implement the writer without seeing real rows.

---

# 23. Required policy evidence context

Implement:

```python
build_task2b_policy_evidence(...)
```

Recommended aggregate keys:

```text
total_orders
served_orders
deferred_orders
served_share
deferred_share

served_orders_by_brand
deferred_orders_by_brand

served_units
deferred_units

served_weight_kg
deferred_weight_kg

served_volume_m3
deferred_volume_m3

deferred_chilled_orders
deferred_chilled_volume_m3

previously_deferred_total
previously_deferred_served
previously_deferred_still_deferred

deferred_days_since_last_served_sum
deferred_days_since_last_served_mean
deferred_days_since_last_served_median
deferred_days_since_last_served_max

individually_impossible_count
low_flexibility_deferred_count

available_vehicle_count
workshop_vehicle_count

available_reefer_count
available_reefer_van_count

used_vehicle_count
used_trip_count
available_trip_slot_upper_bound

max_fresh_minutes_used_by_vehicle
max_style_tech_minutes_used_by_vehicle

fresh_budget_limit
style_tech_budget_limit

phase23_own_validator_pass
phase23_official_checker_pass
```

No order IDs.

---

# 24. Policy fact provenance

Every actual number inserted into the final policy must have provenance.

Recommended internal map:

```text
policy sentence/fact
→ evidence key
→ source artifact
```

Example:

```text
"X orders were deferred"
→ deferred_orders
→ frozen allocation + S1 source
```

```text
"Y vehicles were unavailable in workshop"
→ workshop_vehicle_count
→ task2b_peak_day_fleet
```

```text
"max Fresh use was Z of 270 minutes"
→ max_fresh_minutes_used_by_vehicle
→ frozen trip summary independently recomputed
```

If a numeric policy fact has no evidence key:

```text
FAIL POLICY BUILD
```

Do not let final numbers be free-form LLM text.

---

# 25. DT-337 — Write one-page prioritization policy

## Final file

```text
docs/task2b_policy.md
```

## Required content

Recommended compact structure:

### A. Allocation policy

Summarize the frozen WayLoom lexicographic policy.

### B. Feasibility and calculations

Summarize official hard rules and exact trip-time arithmetic.

### C. What limited service

Use actual aggregate evidence.

### D. Deferrals

Separate:

```text
clearly unavoidable
```

from:

```text
shared-resource / policy tradeoff
```

### E. Cost/impact

Use supported operational metrics.

## Length

Official:

```text
approximately one page or less
```

Engineering target:

```text
roughly 350–550 words
```

Warning:

```text
>650 words
```

unless the final rendered one-page format proves acceptable.

Do not claim the word limit itself is official.

---

# 26. Frozen prioritization policy to summarize

The written policy must accurately reflect Phase 21.

Hard feasibility always comes first.

Among feasible allocations:

```text
Level 1:
maximize served orders

Level 2:
maximize previously-deferred orders served

Level 3:
maximize waiting-days served

Level 4:
maximize low-flexibility orders served

Level 5:
maximize Fresh chilled orders served

Level 6:
maximize Fresh orders served

Level 7:
minimize avoidable specialized vehicle usage
  reefer-van
  reefer
  van
```

Clearly label this as:

```text
WayLoom allocation policy
```

not:

```text
official organizer priority order
```

---

# 27. Calculation explanation required in the policy

The policy should compactly explain the allocation feasibility calculations:

```text
same brand + district per trip

chilled → reefer

van_only → van

home depot match

whole order / no split

both weight + volume capacity

max two trips
```

and exact time:

```text
trip_minutes
=
depot-to-district outbound once
+
inter-stop free-flow × (orders - 1)
+
sum(service allowance by brand+dock type)
```

with:

```text
no return leg
```

Budget summary:

```text
Fresh <=270 minutes per vehicle

Style+Tech combined <=480 minutes per vehicle
```

Do not turn the one-page policy into a full technical specification.

---

# 28. DT-338 — Explain limiting resources

The official policy must identify what limited service on S1.

Do not pre-decide the answer in source code.

Derive it from local evidence.

Potential factors include:

```text
vehicles in workshop

limited available reefers

limited reefer vans

orders with zero/few compatible vehicles

two-trip cap

Fresh 270-minute budget

Style+Tech 480-minute budget

weight capacity

volume capacity
```

## Evidence threshold

Only call a resource a demonstrated limiter if actual Phase 19/22/23 evidence supports it.

Use cautious wording if the evidence is only contextual:

```text
"created pressure"
"reduced flexibility"
"constrained the allocation"
```

Do not write:

```text
"the reefer fleet was the sole bottleneck"
```

without proof.

---

# 29. Limiting-resource evidence examples

Acceptable evidence includes:

- workshop vehicles removed from the usable fleet;
- deferred chilled demand with zero or very few reefer options;
- chilled+van-only demand depending on a very small reefer-van set;
- constrained vehicles at/near official time budgets while compatible demand remains;
- capacity that prevents one more whole order being added to a legal trip;
- all compatible trip slots for a constrained resource already consumed.

Do not infer precise counterfactual causality from a simple scarcity count alone.

---

# 30. DT-339 — Explain allocation calculations

The policy must "show the calculations behind your allocation."

At minimum include:

```text
official trip-time formula
```

and concise scenario-level arithmetic.

Recommended actual aggregates:

```text
served vs deferred orders

used trips

used vehicles

maximum Fresh minutes / 270

maximum Style+Tech minutes / 480

specialized-fleet use

orders with no compatible vehicle
```

Use only locally generated verified values.

Do not manually type real numbers from memory.

---

# 31. DT-340 — Explain unavoidable deferrals

Use a conservative evidence standard.

## Definitely unavoidable

An order with:

```text
compatible_vehicle_count == 0
```

cannot be carried by any available legal vehicle even as a whole order.

That is a direct hard-feasibility deferral.

These may be described as:

```text
directly unavoidable
```

## Other deferrals

Do not call them unavoidable solely because the optimizer deferred them.

A deferred order may be individually feasible but lose out under:

```text
shared vehicle capacity
trip slots
time budgets
other hard constraints
policy tradeoffs
```

If stronger counterfactual evidence exists, it may be used.

Otherwise keep the wording conservative.

---

# 32. DT-341 — Explain policy-choice deferrals

For individually feasible deferred orders competing for shared legal capacity:

explain that the **specific identity of served vs deferred demand** was chosen under the frozen priority policy.

Recommended language:

> After hard feasibility was satisfied, WayLoom maximized the number of served orders, then used previous deferral, service recency, vehicle flexibility, Fresh chilled/Fresh context, and specialized-vehicle conservation to break ties.

Do not say:

```text
the AI decided
the optimizer preferred it for unknown reasons
```

Do not imply:

```text
every feasible deferred order could simply have been added
```

The accurate claim is:

```text
their specific deferral reflects a tradeoff under shared constrained capacity/time.
```

---

# 33. DT-342 — Explain cost/impact of deferrals

Use aggregate operational impact.

Recommended possible metrics:

```text
deferred order count/share

deferred units

deferred kg

deferred m3

deferred chilled demand

previously deferred demand deferred again

waiting-days impact

number of outlets affected

brand distribution
```

Do not invent monetary values.

If no official price/cost field exists, explicitly say so.

---

# 34. Policy narrative example — structure only

Do not copy this with fake numbers.

```text
WayLoom applied the seven official feasibility rules first, then used a
lexicographic policy that maximized served orders before considering prior
deferral, service recency, low vehicle flexibility and the festival-related
Fresh context. A trip's duration was calculated as one outbound district
journey plus inter-stop time for n−1 movements plus per-order handling
allowances; no return leg was added.

On S1, [evidence-based limiting resources] constrained the plan. The final
allocation served [verified aggregate] orders and deferred [verified
aggregate]. [Verified number] deferrals had no compatible available
vehicle and were directly unavoidable. The remaining deferrals occurred
under shared vehicle, trip, capacity or time constraints, with the frozen
policy determining which feasible demand received the limited capacity.

The deferred demand represented [verified operational impact]. The supplied
data contains no monetary cost field, so this policy reports operational
impact rather than inventing a currency estimate.
```

This is a prose structure, not a source of numbers.

---

# 35. Policy page-length verification

Markdown does not have intrinsic pages.

Therefore Phase 24 should:

1. compute word count;
2. warn above engineering target;
3. keep headings/tables compact;
4. if a rendered PDF/DOCX is later produced, verify it is one page or less.

Recommended:

```text
target <=550 words
warning >650 words
```

Again, only the official phrase:

```text
approximately one page or less
```

is source-derived.

---

# 36. Privacy / publication handling for the policy

The official competition terms prohibit publicly disclosing competition data and derivatives without authorization.

The policy is a required competition deliverable, so it may be included in the authorized competition submission package.

However:

- do not publish the real-data policy publicly;
- do not paste aggregate private evidence into external AI chats;
- do not include raw order IDs;
- do not commit the generated policy to a public repository.

If the repository is private and authorized for the team/submission:

follow the project's approved handling.

---

# 37. Phase 24 tests — submission export

Create:

```text
tests/test_task2b_submission.py
```

Synthetic tests:

```text
official template controls schema

exact six columns

exact column order

template row count preserved

template row order preserved

scenario preserved

order_ref preserved

outlet_id preserved

duplicate outlet allowed

join uses order_ref

missing frozen allocation row fails

extra allocation row fails

identity mismatch fails

only answer columns filled

served assignment correct

deferred fields blank

trip 1/2 only

no placeholders

no debug/index columns

atomic write/read-back

output SHA256 manifest

overwrite protection

allocation parity
```

---

# 38. Placeholder tests

Explicitly test:

```text
(served/deferred)
(e.g. VEH014)
(1 or 2)
placeholder
TBD
TODO
N/A
-
```

in answer columns.

All must fail where nonblank final answers are expected.

Also test:

```text
deferred + empty vehicle/trip
```

passes.

---

# 39. Phase 24 tests — policy evidence

Create:

```text
tests/test_task2b_policy_writer.py
```

Synthetic evidence tests:

```text
total = served + deferred

brand aggregates reconcile

units reconcile

weight reconcile

volume reconcile

previously-deferred totals reconcile

waiting-day stats correct

available/workshop fleet counts correct

reefer count correct

reefer-van count correct

trip count correct

Fresh max minutes correct

Style+Tech max minutes correct

individually impossible count correct
```

No row IDs in aggregate output.

---

# 40. Policy-content tests

Require semantic concepts, not exact prose.

Policy should include:

```text
WayLoom priority policy

hard feasibility before preference

trip-time calculation

no return

270 Fresh

480 Style+Tech

limiting-resource explanation

unavoidable deferrals

policy/shared-resource deferrals

deferral cost/impact

no monetary cost field / no fake currency claim
```

Do not require a particular adjective or sentence.

---

# 41. Policy fact-integrity tests

Every inserted real numeric value must map to an evidence key.

Tests should fail when:

```text
template has an unresolved numeric placeholder

evidence key missing

served + deferred != total

previously-deferred served + still-deferred != total

policy claims monetary LKR/USD value without source

policy claims a limiting resource without evidence flag/context
```

---

# 42. Phase 24 end-to-end synthetic test

Use a synthetic official template, synthetic frozen allocation and synthetic policy evidence.

Run:

```text
template validation
→ answer population
→ placeholder audit
→ atomic export
→ read-back validation
→ export manifest
→ policy evidence builder
→ policy writer
→ policy fact validator
→ Phase24 final validator
```

Expected:

```text
PASS
```

Then introduce:

- one identity mismatch;
- one placeholder;
- one unsupported policy number.

Each must fail.

---

# 43. Phase 24 local execution order

Real private run should be:

```text
1. verify Phase 22/23 evidence
2. export submission_task2b.csv
3. build policy evidence
4. write task2b_policy.md
5. run Phase24 validator
6. inspect sanitized PASS output
7. independent Phase24 review
```

Do not write the policy before real evidence context exists.

---

# 44. Suggested local Task 2B export command

```bash
python scripts/export_task2b_submission.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output-config configs/task2b_output.yaml \
  --template submission_task2b.csv \
  --allocation data/interim/task2b_final_allocation.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --phase23-evidence reports/private/phase23_task2b_validator/checker_evidence.json \
  --output outputs/submission_task2b.csv \
  --report-dir reports/private/phase24_task2b_output
```

Resolve the template via the actual manifest/path layer used by the project.

Do not invent a second unofficial template.

---

# 45. Suggested local policy command

```bash
python scripts/build_task2b_policy.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --priority-config configs/task2b_priority.yaml \
  --output-config configs/task2b_output.yaml \
  --allocation data/interim/task2b_final_allocation.csv \
  --trip-summary data/interim/task2b_final_trip_summary.csv \
  --phase23-report-dir reports/private/phase23_task2b_validator \
  --policy-output docs/task2b_policy.md \
  --report-dir reports/private/phase24_task2b_output
```

Do not print the full private evidence context to console.

---

# 46. Suggested local Phase 24 validation command

```bash
python scripts/validate_phase24_task2b_output.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output-config configs/task2b_output.yaml \
  --submission outputs/submission_task2b.csv \
  --policy docs/task2b_policy.md \
  --allocation data/interim/task2b_final_allocation.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --phase23-evidence reports/private/phase23_task2b_validator/checker_evidence.json \
  --report-dir reports/private/phase24_task2b_output
```

---

# 47. Recommended sanitized local output

Target:

```text
WAYLOOM — PHASE 24 TASK 2B FINAL EXPORT

PHASE 23 PRECONDITION                : PASS
PHASE 22 FROZEN HASH                 : PASS

OFFICIAL TEMPLATE FOUND              : PASS
OFFICIAL TEMPLATE SCHEMA             : PASS
TEMPLATE ROW COUNT                   : PASS
TEMPLATE ROW ORDER                   : PASS

SCENARIO PRESERVED                   : PASS
ORDER_REF PRESERVED                  : PASS
OUTLET_ID PRESERVED                  : PASS

DECISION VALUES                      : PASS
SERVED ASSIGNMENTS                   : PASS
DEFERRED BLANK FIELDS                : PASS
TRIP ID DOMAIN                       : PASS
PLACEHOLDERS REMOVED                 : PASS

FROZEN ALLOCATION PARITY             : PASS
PHASE23 CHECKER-CANDIDATE PARITY     : PASS

submission_task2b.csv EXPORT         : PASS
OUTPUT READ-BACK                     : PASS
OUTPUT SHA256                        : PASS

POLICY EVIDENCE CONTEXT              : PASS
POLICY CALCULATIONS                  : PASS
LIMITING RESOURCE EXPLANATION        : PASS
UNAVOIDABLE DEFERRALS                : PASS
POLICY-CHOICE DEFERRALS              : PASS
DEFERRAL COST/IMPACT                 : PASS
FAKE MONETARY COST                   : NO
POLICY LENGTH GUARD                  : PASS

PHASE 24 FINAL VALIDATION            : PASS
READY FOR PHASE 25                   : YES
```

No row-level IDs.

---

# 48. STOP conditions

`READY FOR PHASE 25` remains **NO** if:

- Phase 23 is not PASS;
- Phase 23 checker evidence is missing;
- Phase 22 allocation hash differs;
- official template cannot be located;
- official template schema is unexpected;
- template has duplicate/blank `order_ref`;
- template and frozen allocation order sets differ;
- `scenario` changes;
- `order_ref` changes;
- `outlet_id` changes;
- template row order is not preserved under the WayLoom safety rule;
- placeholder remains;
- decision is not exact `served/deferred`;
- served assignment is incomplete;
- deferred assignment is nonblank;
- trip ID invalid;
- extra output column exists;
- output row count differs;
- output answer columns differ from the frozen allocation;
- Phase 23 checker candidate and final export disagree semantically;
- final file is manually edited;
- policy contains invented real numbers;
- policy claims a limiting resource unsupported by evidence;
- policy calls a deferral unavoidable without proof;
- policy omits calculations;
- policy omits limiting resources;
- policy omits unavoidable vs policy-choice explanation;
- policy omits deferral impact;
- policy invents monetary cost;
- policy changes the frozen Phase 21 priority order;
- policy exposes raw/private row IDs unnecessarily;
- policy is materially longer than the approximate one-page requirement without review;
- Phase 22 allocation changes;
- Phase 23 evidence changes;
- Task 1 changes;
- Task 2A changes;
- Phase 25 work is introduced;
- tests fail;
- `python -m pip check` fails;
- independent review fails.

---

# 49. Definition of Done

Phase 24 is complete only when:

- [ ] DT-331 PASS
- [ ] DT-332 PASS
- [ ] DT-333 PASS
- [ ] DT-334 PASS
- [ ] DT-335 PASS
- [ ] DT-336 PASS
- [ ] DT-337 PASS
- [ ] DT-338 PASS
- [ ] DT-339 PASS
- [ ] DT-340 PASS
- [ ] DT-341 PASS
- [ ] DT-342 PASS
- [ ] Phase 23 PASS evidence verified
- [ ] Phase 22 frozen hash verified
- [ ] official template is used as the base
- [ ] exact six official columns
- [ ] exact column order
- [ ] template row count preserved
- [ ] template row order preserved as WayLoom safety rule
- [ ] `scenario` unchanged
- [ ] `order_ref` unchanged
- [ ] `outlet_id` unchanged
- [ ] no placeholders
- [ ] exact decision spelling
- [ ] served vehicle/trip populated
- [ ] deferred vehicle/trip blank
- [ ] trip IDs only 1/2
- [ ] `outputs/submission_task2b.csv` exists
- [ ] output read-back passes
- [ ] output SHA256 recorded
- [ ] final answer columns exactly match frozen allocation
- [ ] final export semantically matches Phase 23 checker candidate
- [ ] final policy exists at `docs/task2b_policy.md`
- [ ] policy is approximately one page or less
- [ ] policy accurately states WayLoom objective
- [ ] policy shows allocation calculations
- [ ] policy explains actual limiting resources
- [ ] policy distinguishes directly unavoidable deferrals conservatively
- [ ] policy explains shared-resource/policy-choice deferrals
- [ ] policy explains operational cost/impact
- [ ] policy invents no monetary cost
- [ ] every policy number has provenance
- [ ] no raw order IDs unnecessarily exposed
- [ ] synthetic Phase 24 tests pass
- [ ] full safe suite passes
- [ ] `python -m pip check` passes
- [ ] private reports ignored
- [ ] Task 1 remains frozen
- [ ] Task 2A remains frozen
- [ ] Phase 22 allocation remains frozen/unchanged
- [ ] Phase 23 evidence remains unchanged
- [ ] independent Phase 24 review passes
- [ ] no unresolved STOP condition

Then:

```text
PHASE 24 STATUS: PASS
submission_task2b.csv: FINAL
TASK 2B POLICY: FINAL
READY FOR PHASE 25: YES
```

---

# 50. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-24-task2b-final-output
```

Recommended commits for tracked implementation:

```text
feat(task2b): add official Task 2B submission exporter
feat(task2b): add evidence-grounded policy writer
test(task2b): validate final Task 2B output contract
docs(task2b): document final output and policy generation
```

Before commit:

```bash
git status
git diff
git diff --check
```

Run:

```bash
pytest -q \
  tests/test_task2b_submission.py \
  tests/test_task2b_policy_writer.py \
  tests/test_task2b_phase24_output.py

pytest -q

python -m pip check
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

## Important policy/public-repository rule

The fully populated policy contains competition-data-derived aggregate facts.

If the repository is public or accessible outside the authorized competition context:

```text
DO NOT COMMIT THE REAL FILLED POLICY
```

Keep it local and include it later only in the authorized submission package.

If the repository is private and authorized:

follow the team's approved handling.

The same caution applies to final competition output files if repository publication would violate the competition's confidentiality terms.

---

# 51. Recommended model

Phase 24 is high-stakes but mostly deterministic export + evidence-grounded writing.

Recommended:

```text
GPT-5.6 Sol
Reasoning: Medium
```

Escalate the same model to:

```text
Reasoning: High
```

if cross-phase evidence reconciliation or policy correctness becomes difficult.

Do not use a low-reasoning model to write the final policy without the Phase 24 evidence safeguards.

---

# 52. Ready-to-copy implementation prompt

```text
You are implementing WayLoom Datathon PHASE 24 only.

PHASE:
Task 2B Output and Written Policy

TASK RANGE:
DT-331 through DT-342

EXECUTION MODE:
FINAL TASK 2B EXPORT + POLICY WRITING with full SAFE engineering autonomy.

RECOMMENDED MODEL:
GPT-5.6 Sol — Medium reasoning

ESCALATE ONLY IF NEEDED:
GPT-5.6 Sol — High reasoning

DO NOT START PHASE 25.

==================================================
MISSION
==================================================

Produce the exact official Task 2B output file:

outputs/submission_task2b.csv

from the FROZEN Phase 22 allocation, only after Phase 23 has PASS evidence.

Also produce the approximately one-page-or-less Task 2B prioritization policy required by the official challenge.

Do not re-optimize.
Do not modify any allocation decision.
Do not manually change vehicle/trip assignments.
Do not invent policy facts.
Do not expose private row-level data.

==================================================
READ FIRST
==================================================

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - Phase 24 only
4. PHASE_21_COMPETITION_CONTRACT.md
5. PHASE_22_COMPETITION_CONTRACT.md
6. PHASE_23_COMPETITION_CONTRACT.md
7. PHASE_24_COMPETITION_CONTRACT.md

Inspect:

8. Phase 22 frozen allocation/export interfaces
9. Phase 22 freeze manifest implementation
10. Phase 23 validator/checker evidence implementation
11. configs/task2b_priority.yaml
12. configs/task2b_validation.yaml
13. official submission_task2b.csv template location from the dataset manifest
14. existing Task 2B output/policy tests

Use the official Challenge Booklet as the source of truth.

==================================================
PRECONDITIONS
==================================================

Require Phase 23 PASS.

Require:

Phase 22 allocation state = FROZEN

Phase 22 allocation SHA256 matches freeze manifest

Phase 23 own validator = PASS

Phase 23 official check_allocation.py = PASS

Phase 23 checker evidence = SAVED

If any fails or evidence is missing:
STOP.

TASK 1 and TASK 2A remain frozen.

Do not modify:

outputs/submission_task1.csv
outputs/submission_task2a.csv
configs/task1_final_models.yaml
configs/task2a_final_models.yaml
models/task1_service/**
models/task1_late/**

Do not modify:

data/interim/task2b_final_allocation.csv

==================================================
PRIVATE DATA BOUNDARY
==================================================

Do not print or expose real row-level competition data from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for Codex-run tests.

The human will execute the real export/policy build locally.

Normal console output:
statuses and aggregate checks only.

No real:
order_ref lists
vehicle assignment lists
deferred-order IDs
trip member lists

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2b/submission.py
src/task2b/policy_writer.py
src/task2b/policy_evidence.py

scripts/export_task2b_submission.py
scripts/build_task2b_policy.py
scripts/validate_phase24_task2b_output.py

configs/task2b_output.yaml

docs/task2b_policy.md
docs/task2b_output_spec.md

tests/test_task2b_submission.py
tests/test_task2b_policy_writer.py
tests/test_task2b_phase24_output.py

Do not create Phase 25 explainability work.

==================================================
OFFICIAL OUTPUT CONTRACT
==================================================

Use the organizer-supplied:

submission_task2b.csv

template as the base.

Exact official columns:

scenario
order_ref
outlet_id
decision
vehicle_id
trip_id

Official rules:

scenario:
preserve supplied identifier; S1

order_ref:
preserve supplied identifier
canonical allocation key
outlet_id may repeat

outlet_id:
preserve supplied identifier

decision:
exactly served or deferred

vehicle_id:
assigned vehicle for served
blank for deferred

trip_id:
1 or 2 for served
blank for deferred

Replace every supplied placeholder.

Do not add extra columns.
Do not write an index.

==================================================
DT-331 — POPULATE OFFICIAL TASK 2B TEMPLATE
==================================================

Load the official organizer template through the manifest.

Do not construct the final file from scratch.

Validate before filling:

expected exact column names
expected column order
order_ref nonblank
order_ref unique
template order_ref set exactly equals frozen allocation order_ref set

Join the frozen allocation to the template by:

order_ref

Use many-to-one/one-to-one assertions as appropriate.

Verify before filling:

template scenario == frozen/source scenario

template outlet_id == canonical source outlet_id

Do not overwrite identity mismatches.

Fill ONLY:

decision
vehicle_id
trip_id

Identity columns remain template-controlled.

Preserve template row order as an engineering safety guarantee.

Do not sort by order_ref, vehicle or trip.

==================================================
DT-332 — PRESERVE SCENARIO
==================================================

Require final:

scenario

to equal the official template row-by-row.

Do not rewrite with a constant merely because all rows are expected S1.

Also assert every scenario == S1.

If template/frozen/source disagree:
FAIL.

==================================================
DT-333 — PRESERVE ORDER_REF
==================================================

Require final order_ref column:

byte/semantic values equal official template
same row count
same row order
unique
nonblank

Do not normalize or regenerate IDs.

Do not use outlet_id as key.

==================================================
DT-334 — PRESERVE OUTLET_ID
==================================================

Require final outlet_id values:

equal official template row-by-row

and:
match canonical source mapping for order_ref.

Repeated outlet_id is valid.

Do not deduplicate.

==================================================
DT-335 — REMOVE EVERY PLACEHOLDER
==================================================

The official template contains placeholders in answer columns.

After filling, require no placeholder remains.

Decision must be exact:
served
deferred

Served:
vehicle_id real populated ID
trip_id 1 or 2

Deferred:
vehicle_id empty
trip_id empty

Also reject obvious placeholder tokens such as:
(served/deferred)
(e.g. VEH014)
(1 or 2)
placeholder
TBD
TODO
N/A
-
where those appear in answer fields.

Do not "repair" unknown invalid values.
FAIL.

==================================================
DT-336 — EXPORT submission_task2b.csv
==================================================

Canonical filename:

outputs/submission_task2b.csv

Write atomically:

1. create temp file
2. write exact six columns
3. no index
4. read back
5. revalidate
6. os.replace into final path

Use UTF-8 and normal CSV semantics.

Do not write debug columns.

Do not include extra blank leading/trailing rows.

After export calculate SHA256.

Create private export manifest.

Do not overwrite a valid final output silently.

Recommended:
refuse overwrite unless --force is explicitly supplied AND source frozen allocation hash is unchanged.

==================================================
FINAL OUTPUT VALIDATION AFTER WRITE
==================================================

Read the exported file back from disk.

Require:

filename exact

columns exact

column order exact

row count exact

template order_ref set exact

template row order preserved

scenario unchanged

order_ref unchanged

outlet_id unchanged

decision exact

served vehicle populated

served trip 1/2

deferred vehicle blank

deferred trip blank

no placeholders

no duplicate order_ref

no extra index column

Then compare decision/vehicle_id/trip_id by order_ref against:

Phase22 frozen allocation

and the Phase23 private checker candidate if available.

Require semantic parity.

Do not rerun the optimizer.

Phase33 will run the official checker again on the final official file.

==================================================
OUTPUT MANIFEST
==================================================

Create private:

reports/private/phase24_task2b_output/export_manifest.json

Include:

phase = 24

state = FINAL_EXPORTED

official_template_sha256

phase22_frozen_allocation_sha256

phase23_checker_input_sha256 if available

submission_task2b_sha256

row_count

column_list

identity_preservation = PASS

placeholder_audit = PASS

allocation_parity = PASS

phase23_own_validator = PASS

phase23_official_checker = PASS

timestamp

git commit if available

Do not store row-level output in the manifest.

==================================================
POLICY SOURCE BOUNDARY
==================================================

The official challenge requires approximately one page or less.

It must:

show calculations behind the allocation

identify what limited service on the day

explain why specific orders were deferred

distinguish unavoidable deferrals from deferrals that were a choice

explain what the deferrals cost

The official source does NOT provide monetary revenue/cost data.

Therefore:
DO NOT INVENT CURRENCY COST.

Interpret "cost/impact" using transparent operational metrics available in the official scenario data, such as:

deferred order count
deferred units
deferred weight_kg
deferred volume_m3
deferred chilled order count/volume
previously-deferred demand still deferred
days_since_last_served impact
brand distribution of deferred demand

Clearly state that no monetary cost is claimed because the official data does not provide monetary values.

==================================================
DT-337 — WRITE ONE-PAGE PRIORITIZATION POLICY
==================================================

Final file:

docs/task2b_policy.md

This is the final competition-facing policy text.

Build from:

Phase21 frozen policy
Phase22 frozen allocation
Phase19 scarcity diagnostics
Phase20 exact trip formula
Phase23 validation/checker PASS evidence
local aggregate policy evidence

Do not include row-level IDs unless the competition requires them.
Prefer aggregate explanation.

Target:
approximately one page or less.

Engineering length target:
about 350–550 words before headings/table formatting.

Do not treat the word target as an official rule; it is only to keep the document near one page.

Required policy structure:

1. Allocation objective
2. Feasibility/calculation method
3. Limiting resources
4. Deferral rationale
5. Operational cost/impact

Use concise prose.

No unsupported causal claims.

No invented monetary value.

==================================================
POLICY — ALLOCATION OBJECTIVE
==================================================

Accurately summarize the frozen Phase21 lexicographic policy:

1 maximize served orders
2 maximize previously-deferred orders served
3 maximize waiting-days served
4 maximize low-flexibility orders served
5 maximize Fresh chilled orders served
6 maximize Fresh orders served
7 conserve avoidable reefer-van / reefer / van usage

Clearly label:
WayLoom engineering policy

not:
official organizer priority rule.

Hard feasibility always dominates the policy.

==================================================
POLICY — CALCULATION METHOD
==================================================

Explain the actual allocation calculations.

Mention:

same brand + district per trip

chilled -> reefer

van_only -> van

home-depot compatibility

whole-order assignment

weight + volume capacity

maximum two trips per vehicle

exact trip time:

outbound once
+
inter-stop * (orders - 1)
+
sum brand+dock service allowances

no return journey

Fresh combined <=270 per vehicle

Style+Tech combined <=480 per vehicle

Do not fill the one-page policy with every test detail.
Summarize the calculation compactly.

==================================================
DT-338 — EXPLAIN LIMITING RESOURCES
==================================================

Use REAL AGGREGATE EVIDENCE from local/private Phase19/22/23 reports.

Do not pre-write a bottleneck conclusion.

The policy writer must derive a short factual statement from evidence such as:

available fleet vs workshop fleet

available reefer count

available reefer-van count

orders with zero compatible vehicles

orders with one/two compatible vehicles

used vs available trip slots

vehicles near Fresh 270-minute limit

vehicles near Style+Tech 480-minute limit

weight/volume-capacity pressure

Do not claim:
"reefers were the bottleneck"
unless the evidence actually supports it.

If several limits mattered:
state them jointly.

If a resource was not binding:
do not call it limiting.

==================================================
LIMITING-RESOURCE EVIDENCE RULE
==================================================

Classify a resource as a demonstrated limiter only from explicit evidence.

Examples of acceptable evidence:

some deferred chilled orders had no compatible reefer

some deferred van_only+chilled demand depended on a small reefer-van set

all/most compatible trip slots for a constrained class were consumed

a vehicle budget reached or nearly reached the official hard limit while compatible demand remained

combined capacity prevented adding another complete order to a legal trip

Do not infer exact counterfactual causality solely from general scarcity counts.

Use cautious language:
"constrained"
"limited flexibility"
"contributed to deferral pressure"

unless a stronger statement is proven.

==================================================
DT-339 — EXPLAIN ALLOCATION CALCULATIONS
==================================================

The one-page policy must show enough calculation detail to be auditable.

Include the official formula:

trip_minutes =
outbound
+
inter_stop * (n_orders - 1)
+
sum(service_allowance_min)

Mention:
return journey excluded.

Also report concise actual aggregate calculations, for example:

number of served/deferred orders

number of used trips

Fresh minutes used across relevant vehicles or maximum Fresh utilization

Style+Tech minutes used or maximum utilization

specialized fleet usage

Do not include every trip row.

Do not disclose unnecessary private IDs.

All actual numbers must come from local evidence generation, not from the language model.

==================================================
DT-340 — EXPLAIN UNAVOIDABLE DEFERRALS
==================================================

Use a conservative evidence standard.

Definitely unavoidable at individual-compatibility level:

compatible_vehicle_count == 0

because no available compatible vehicle can legally carry the whole order.

Also include any other deferral only if Phase22/23 evidence proves it was infeasible under hard constraints, not merely lower policy priority.

Do not call an order unavoidable just because it was deferred.

Recommended wording:

"Orders with no compatible available vehicle were directly unavoidable under the hard constraints."

For other deferred orders, use the shared-resource/policy section unless stronger proof exists.

Aggregate only.

Do not expose specific order_refs in the competition policy unless needed.

==================================================
DT-341 — EXPLAIN POLICY-CHOICE DEFERRALS
==================================================

For deferred orders that were individually feasible but competed for shared legal capacity/time:

explain that the frozen lexicographic policy determined which demand was served.

Do not say:
"the AI decided."

Use:
"Under equal feasibility, WayLoom maximized total served orders first, then prior deferrals, waiting time, low flexibility, Fresh chilled/Fresh demand, and finally specialized-vehicle conservation."

Important:
Do not imply every individually feasible deferred order could have been added with no tradeoff.

Use language:
"their specific deferral reflects the allocation tradeoff under shared capacity/time constraints."

==================================================
DT-342 — EXPLAIN COST / IMPACT OF DEFERRALS
==================================================

Official booklet asks what deferrals cost.

No official monetary cost/revenue field is provided.

Therefore report operational impact only.

Recommended aggregate impact metrics:

deferred_order_count

deferred_order_share

deferred_units

deferred_weight_kg

deferred_volume_m3

deferred_chilled_order_count

deferred_chilled_volume_m3 if derivable from official order volume

previously_deferred_orders_still_deferred

sum/mean/max days_since_last_served among deferred orders

brand-level deferred counts/volume

unique deferred outlet count

Use only metrics actually available and reliable.

Do not create fake:
LKR cost
lost revenue
penalty cost
customer churn cost

unless such values exist in official data, which the current source does not establish.

Recommended policy sentence:

"The supplied data contains no monetary cost field, so we report deferral impact operationally rather than inventing a currency estimate."

==================================================
POLICY EVIDENCE CONTEXT BUILDER
==================================================

Implement:

build_task2b_policy_evidence(...)

Output a private aggregate JSON/data structure with no row-level IDs.

Recommended fields:

total_orders
served_orders
deferred_orders
served_share

served_by_brand
deferred_by_brand

served_units
deferred_units

served_weight_kg
deferred_weight_kg

served_volume_m3
deferred_volume_m3

deferred_chilled_orders
deferred_chilled_volume_m3

previously_deferred_total
previously_deferred_served
previously_deferred_still_deferred

deferred_days_since_last_served_sum
deferred_days_since_last_served_mean
deferred_days_since_last_served_max

individually_impossible_count

low_flexibility_deferred_count

available_vehicle_count
workshop_vehicle_count
available_reefer_count
available_reefer_van_count

used_trip_count
available_trip_slot_upper_bound

max_fresh_minutes_used_by_vehicle
max_style_tech_minutes_used_by_vehicle

fresh_budget_limit = 270
style_tech_budget_limit = 480

own_validator_pass
official_checker_pass

Do not print this full object in Codex chat.

==================================================
POLICY FACT VALIDATION
==================================================

Any numeric value inserted into docs/task2b_policy.md must have a source key in the private evidence context.

Implement a simple citation/provenance map internally:

policy fact
→ evidence key
→ source artifact

Fail generation if a required numeric placeholder has no evidence.

Do not let the LLM invent final numbers.

==================================================
POLICY WRITER
==================================================

Prefer deterministic template-driven generation.

Do not ask an external generative model to read private rows.

A pure Python writer can create the final narrative using:

pre-approved static prose
+
aggregate evidence values

Human may later edit wording locally, but edits must not change facts.

If human edits:
rerun policy fact validation.

==================================================
POLICY PAGE-LENGTH CHECK
==================================================

Official says:
approximately one page or less.

For Markdown, page count is not intrinsic.

Implement an engineering guard:

target word count <= about 550 words

and:
warn if >650 words.

If the project later renders the policy to PDF/DOCX:
verify actual rendered output is <=1 page.

Do not claim the word threshold itself is official.

==================================================
POLICY PRIVACY
==================================================

The written policy is a required competition deliverable and may include aggregate scenario-derived calculations.

Do not publish it publicly outside the authorized competition submission context.

If the Git repository is public:
do not commit the fully populated real-data policy.

Use the project’s private artifact handling / final packaging flow.

If the repository is private and authorized:
follow the team’s approved policy.

Never include raw order rows.

==================================================
PHASE24 PRIVATE REPORTS
==================================================

Create:

reports/private/phase24_task2b_output/

with:

export_manifest.json

template_identity_audit.json

placeholder_audit.json

allocation_parity_audit.json

policy_evidence_context.json

policy_fact_validation.json

policy_length_check.json

warnings.json

phase24_output_report.md

Do not commit private reports.

==================================================
TESTS — SUBMISSION EXPORT
==================================================

Use synthetic fixtures only.

Test:

official template controls columns

exact six columns

exact column order

template row count preserved

template row order preserved

scenario preserved

order_ref preserved

outlet_id preserved

duplicate outlet_id allowed

order_ref key used

missing frozen allocation row fails

extra allocation row fails

identity mismatch fails

answer columns populated only

served vehicle/trip

deferred blank fields

trip 1/2

no placeholders

no index column

atomic write/readback

SHA256 manifest

overwrite protection

semantic parity with frozen allocation

==================================================
TESTS — PLACEHOLDERS
==================================================

Reject:

(served/deferred)

(e.g. VEH014)

(1 or 2)

placeholder

TBD

TODO

N/A

-

invalid decision

unknown served vehicle

invalid trip

Do not reject legitimate empty vehicle/trip for deferred rows.

==================================================
TESTS — POLICY EVIDENCE
==================================================

Synthetic aggregate calculations:

served/deferred counts

brand counts

units

weight

volume

chilled deferrals

previous-deferral outcomes

waiting-days metrics

available/workshop fleet counts

reefer/reefer-van counts

trip slot usage

Fresh/Style-Tech utilization

impossible count

No row IDs in evidence output.

==================================================
TESTS — POLICY CONTENT
==================================================

Require policy contains concepts for:

allocation objective

calculations

limiting resources

unavoidable deferrals

policy-choice/shared-resource deferrals

cost/impact

no monetary-cost fabrication statement

official trip formula

no return

Fresh 270

Style+Tech 480

WayLoom policy clearly separate from official hard rules

Do not require exact prose.

==================================================
TESTS — POLICY FACTS
==================================================

Every inserted actual numeric value must be traceable to an evidence key.

Fail on:
unknown placeholder
missing evidence
contradictory totals
served + deferred != total

Check:

previously-deferred served + still-deferred
=
previously-deferred total

deferred brand counts sum appropriately

No fabricated currency symbol/value.

==================================================
PHASE24 VALIDATION
==================================================

After export and policy generation:

run Phase24 validator.

Require:

submission file exact

policy complete

policy within engineering length guard

Phase23 PASS evidence still valid

Phase22 allocation hash unchanged

submission answer columns match frozen allocation

submission identity matches official template

No placeholders

No private row IDs leaked into policy

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After DT-331–336:
run submission export tests.

After DT-337–342:
run policy evidence/writer tests.

Fix ordinary engineering bugs automatically.

Do NOT:
change allocation
rerun optimizer
edit checker result
invent policy facts
change Phase21 policy

Then run:

pytest -q \
  tests/test_task2b_submission.py \
  tests/test_task2b_policy_writer.py \
  tests/test_task2b_phase24_output.py

Then run existing Task2B safe suite.

Then:

pytest -q

python -m pip check

git status

git diff

git diff --check

If real data is needed:
do not inspect it inside external-agent context.

Return exact local commands.

==================================================
LOCAL SUBMISSION EXPORT COMMAND
==================================================

Implement but do not execute private real data inside Codex:

python scripts/export_task2b_submission.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output-config configs/task2b_output.yaml \
  --template submission_task2b.csv \
  --allocation data/interim/task2b_final_allocation.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --phase23-evidence reports/private/phase23_task2b_validator/checker_evidence.json \
  --output outputs/submission_task2b.csv \
  --report-dir reports/private/phase24_task2b_output

Adapt --template resolution to the actual manifest convention.

==================================================
LOCAL POLICY BUILD COMMAND
==================================================

python scripts/build_task2b_policy.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --priority-config configs/task2b_priority.yaml \
  --output-config configs/task2b_output.yaml \
  --allocation data/interim/task2b_final_allocation.csv \
  --trip-summary data/interim/task2b_final_trip_summary.csv \
  --phase23-report-dir reports/private/phase23_task2b_validator \
  --policy-output docs/task2b_policy.md \
  --report-dir reports/private/phase24_task2b_output

==================================================
LOCAL PHASE24 VALIDATION COMMAND
==================================================

python scripts/validate_phase24_task2b_output.py \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --output-config configs/task2b_output.yaml \
  --submission outputs/submission_task2b.csv \
  --policy docs/task2b_policy.md \
  --allocation data/interim/task2b_final_allocation.csv \
  --phase22-freeze-manifest reports/private/phase22_task2b_optimizer/freeze_manifest.json \
  --phase23-evidence reports/private/phase23_task2b_validator/checker_evidence.json \
  --report-dir reports/private/phase24_task2b_output

==================================================
STOP CONDITIONS
==================================================

STOP if:

Phase23 not PASS

official checker evidence missing

Phase22 allocation hash mismatch

official template missing

template schema unexpected

template order_ref duplicate

template/frozen order sets differ

scenario mismatch

order_ref mismatch

outlet_id mismatch

placeholder remains

served vehicle/trip missing

deferred assignment populated

invalid trip ID

final output has extra column

output row count differs

allocation parity fails

output overwrite would replace unrelated valid file

policy uses facts not present in evidence

policy claims unsupported limiting resource

policy calls a deferral unavoidable without proof

policy claims fake monetary cost

policy changes frozen priority order

policy omits calculations

policy omits limiting resources

policy omits unavoidable-vs-choice explanation

policy omits cost/impact

policy exposes private row IDs unnecessarily

policy exceeds one-page target materially without review

Task1 changes

Task2A changes

Phase22 allocation changes

Phase23 evidence changes

Phase25 work added

safe tests cannot pass

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-331 READY
DT-332 READY
DT-333 READY
DT-334 READY
DT-335 READY
DT-336 READY
DT-337 READY
DT-338 READY
DT-339 READY
DT-340 READY
DT-341 READY
DT-342 READY

official template used

scenario preserved

order_ref preserved

outlet_id preserved

answer placeholders removed

exact filename submission_task2b.csv

exact six columns

template row order preserved

frozen allocation parity exact

policy one-page-or-less target

policy calculations supported

limiting resource claims evidence-based

unavoidable deferrals conservative

policy-choice deferrals accurate

cost/impact operational and evidence-based

no fake monetary cost

Phase23 PASS evidence preserved

Task1 unchanged

Task2A unchanged

Phase22 allocation unchanged

no Phase25 implementation

safe tests pass

full suite passes

pip check passes

private reports ignored

==================================================
RETURN ONLY
==================================================

PHASE:
24 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-331 READY / FAIL
DT-332 READY / FAIL
DT-333 READY / FAIL
DT-334 READY / FAIL
DT-335 READY / FAIL
DT-336 READY / FAIL
DT-337 READY / FAIL
DT-338 READY / FAIL
DT-339 READY / FAIL
DT-340 READY / FAIL
DT-341 READY / FAIL
DT-342 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

OFFICIAL TEMPLATE USED:
PASS / FAIL

SCENARIO PRESERVED:
PASS / FAIL

ORDER_REF PRESERVED:
PASS / FAIL

OUTLET_ID PRESERVED:
PASS / FAIL

PLACEHOLDERS REMOVED:
PASS / FAIL

SUBMISSION_TASK2B EXPORT:
READY / FAIL

FROZEN ALLOCATION PARITY:
PASS / FAIL

ONE-PAGE POLICY:
READY / FAIL

LIMITING RESOURCE EVIDENCE:
PASS / FAIL

ALLOCATION CALCULATIONS:
PASS / FAIL

UNAVOIDABLE DEFERRALS:
PASS / FAIL

POLICY-CHOICE DEFERRALS:
PASS / FAIL

DEFERRAL COST/IMPACT:
PASS / FAIL

MONETARY COST FABRICATED:
MUST BE NO

TASK1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

TASK2A FROZEN ARTIFACTS CHANGED:
MUST BE NO

PHASE22 FROZEN ALLOCATION CHANGED:
MUST BE NO

PHASE23 EVIDENCE CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print:

1. exact local submission-export command
2. exact local policy-build command
3. exact local Phase24 validation command

PHASE 24 STATUS:
AWAITING LOCAL EXPORT + POLICY BUILD

READY FOR PHASE 25:
NO

Then STOP.

Do not start Phase25.

```

---

# 53. Independent Phase 24 review prompt

Use a fresh Codex/Cursor session after the human local export, policy build and Phase 24 validation all pass.

```text
Perform an INDEPENDENT REVIEW of completed WayLoom Datathon Phase 24.

Do NOT implement Phase 25.
Do NOT change the frozen Phase22 allocation.
Do NOT rewrite the policy unless reporting a blocker.
Do NOT inspect private row-level competition data.

READ:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase24
4. PHASE_21_COMPETITION_CONTRACT.md
5. PHASE_22_COMPETITION_CONTRACT.md
6. PHASE_23_COMPETITION_CONTRACT.md
7. PHASE_24_COMPETITION_CONTRACT.md

8. src/task2b/submission.py
9. src/task2b/policy_writer.py
10. src/task2b/policy_evidence.py

11. scripts/export_task2b_submission.py
12. scripts/build_task2b_policy.py
13. scripts/validate_phase24_task2b_output.py

14. configs/task2b_output.yaml
15. docs/task2b_output_spec.md

16. tests/test_task2b_submission.py
17. tests/test_task2b_policy_writer.py
18. tests/test_task2b_phase24_output.py

Inspect official Task 2B template schema only through tracked schema/manifest
or safe code. Do not print private final rows.

HUMAN SANITIZED LOCAL RESULT:

PHASE23 PRECONDITION: <PASS/FAIL>
PHASE22 FROZEN HASH: <PASS/FAIL>

OFFICIAL TEMPLATE: <PASS/FAIL>
TEMPLATE SCHEMA: <PASS/FAIL>
TEMPLATE ROW COUNT: <PASS/FAIL>
TEMPLATE ROW ORDER: <PASS/FAIL>

SCENARIO PRESERVED: <PASS/FAIL>
ORDER_REF PRESERVED: <PASS/FAIL>
OUTLET_ID PRESERVED: <PASS/FAIL>

DECISION VALUES: <PASS/FAIL>
SERVED ASSIGNMENTS: <PASS/FAIL>
DEFERRED BLANK FIELDS: <PASS/FAIL>
TRIP ID DOMAIN: <PASS/FAIL>
PLACEHOLDERS REMOVED: <PASS/FAIL>

FROZEN ALLOCATION PARITY: <PASS/FAIL>
PHASE23 CHECKER-CANDIDATE PARITY: <PASS/FAIL>

submission_task2b.csv EXPORT: <PASS/FAIL>
OUTPUT SHA256: <PASS/FAIL>

POLICY EVIDENCE: <PASS/FAIL>
POLICY CALCULATIONS: <PASS/FAIL>
LIMITING RESOURCE EXPLANATION: <PASS/FAIL>
UNAVOIDABLE DEFERRALS: <PASS/FAIL>
POLICY-CHOICE DEFERRALS: <PASS/FAIL>
DEFERRAL COST/IMPACT: <PASS/FAIL>
FAKE MONETARY COST: <YES/NO>
POLICY LENGTH GUARD: <PASS/FAIL>

==================================================
AUDIT EVERY TASK
==================================================

DT-331:
official template is used, not recreated independently.

DT-332:
scenario preserved exactly.

DT-333:
order_ref preserved exactly; order_ref used as key.

DT-334:
outlet_id preserved exactly; repeats allowed.

DT-335:
all answer placeholders removed.

DT-336:
exact outputs/submission_task2b.csv exported with exact six columns.

DT-337:
policy approximately one page or less and competition-facing.

DT-338:
limiting-resource claims supported by evidence, not guessed.

DT-339:
policy shows real calculation method and verified aggregate calculations.

DT-340:
unavoidable deferrals are conservatively classified.

DT-341:
shared-resource/policy-choice deferrals correctly explain frozen policy.

DT-342:
deferral cost/impact is operational and source-supported;
no fake monetary cost.

==================================================
CRITICAL OUTPUT AUDIT
==================================================

Verify:

exact filename

exact columns

exact order

template row count

template row order preserved as engineering guard

scenario/order_ref/outlet_id exact

decision only served/deferred

served vehicle populated

served trip 1/2

deferred assignment blank

no placeholders

no index/debug fields

allocation parity exact

Phase23 checker-candidate semantic parity exact

==================================================
CRITICAL POLICY AUDIT
==================================================

Verify policy:

does not claim WayLoom priority is official

does not change Phase21 tier order

does not claim a bottleneck without evidence

does not label all deferred orders unavoidable

does not invent currency cost

does state no monetary field if discussing operational impact

does include official trip formula

does mention no return leg

does mention Fresh 270

does mention Style+Tech 480

does distinguish hard feasibility from priority choice

uses only evidence-backed numeric values

does not unnecessarily expose private order IDs

==================================================
RUN SAFE TESTS
==================================================

pytest -q \
  tests/test_task2b_submission.py \
  tests/test_task2b_policy_writer.py \
  tests/test_task2b_phase24_output.py

Then run existing Task2B safe tests.

Then:

pytest -q
python -m pip check
git status
git diff --check

Do not execute private real-data generation.

==================================================
RETURN
==================================================

Provide:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

OFFICIAL TEMPLATE EXPORT:
PASS / FAIL

IDENTITY PRESERVATION:
PASS / FAIL

PLACEHOLDER REMOVAL:
PASS / FAIL

FROZEN ALLOCATION PARITY:
PASS / FAIL

FINAL CSV CONTRACT:
PASS / FAIL

POLICY LENGTH/SCOPE:
PASS / FAIL

POLICY FACT PROVENANCE:
PASS / FAIL

LIMITING RESOURCE CLAIMS:
PASS / FAIL

UNAVOIDABLE DEFERRAL CLAIMS:
PASS / FAIL

POLICY-CHOICE DEFERRALS:
PASS / FAIL

DEFERRAL COST/IMPACT:
PASS / FAIL

NO FABRICATED MONETARY COST:
PASS / FAIL

NO PRIVATE ROW DISCLOSURE:
PASS / FAIL

NO PHASE25 WORK:
PASS / FAIL

SAFE TESTS:
PASS / FAIL

HUMAN LOCAL EXPORT:
PASS / FAIL

HUMAN LOCAL POLICY BUILD:
PASS / FAIL

HUMAN LOCAL PHASE24 VALIDATION:
PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-331: PASS/FAIL
DT-332: PASS/FAIL
DT-333: PASS/FAIL
DT-334: PASS/FAIL
DT-335: PASS/FAIL
DT-336: PASS/FAIL
DT-337: PASS/FAIL
DT-338: PASS/FAIL
DT-339: PASS/FAIL
DT-340: PASS/FAIL
DT-341: PASS/FAIL
DT-342: PASS/FAIL

PHASE 24 REVIEW:
PASS / FAIL

submission_task2b.csv:
FINAL / NOT FINAL

TASK 2B POLICY:
FINAL / NOT FINAL

READY FOR PHASE 25:
YES / NO

If FAIL:
list exact blockers only.

Do not automatically alter the frozen allocation.
Do not start Phase25.
```

---

# 54. Completion record

```markdown
# Phase 24 Completion Record

## Tasks

- [ ] DT-331
- [ ] DT-332
- [ ] DT-333
- [ ] DT-334
- [ ] DT-335
- [ ] DT-336
- [ ] DT-337
- [ ] DT-338
- [ ] DT-339
- [ ] DT-340
- [ ] DT-341
- [ ] DT-342

## Output

- [ ] official template used
- [ ] scenario preserved
- [ ] order_ref preserved
- [ ] outlet_id preserved
- [ ] all placeholders removed
- [ ] exact six columns
- [ ] template row order preserved
- [ ] allocation parity PASS
- [ ] submission_task2b.csv exported
- [ ] SHA256 recorded

## Policy

- [ ] approximately one page or less
- [ ] frozen prioritization policy explained
- [ ] allocation calculations shown
- [ ] limiting resources supported
- [ ] unavoidable deferrals explained conservatively
- [ ] policy-choice/shared-resource deferrals explained
- [ ] operational cost/impact quantified
- [ ] no fake monetary cost
- [ ] all policy numbers have evidence

## Safety

- Task 1 changed: NO
- Task 2A changed: NO
- Phase22 allocation changed: NO
- Phase23 evidence changed: NO
- private rows exposed: NO

## Review

- independent review: PASS / FAIL

## Verdict

PHASE 24 STATUS: PASS / FAIL
submission_task2b.csv: FINAL / NOT FINAL
TASK 2B POLICY: FINAL / NOT FINAL
READY FOR PHASE 25: YES / NO
```

---

# 55. Final Phase 24 checklist

Before Phase 25:

- [ ] Phase 23 own validator passed.
- [ ] Phase 23 organizer checker passed.
- [ ] Phase 23 evidence is saved.
- [ ] Phase 22 allocation hash still matches.
- [ ] official Task 2B template is used.
- [ ] exact official filename is used.
- [ ] exact six official columns are present.
- [ ] template identities are unchanged.
- [ ] template rows are all preserved.
- [ ] template row order is preserved.
- [ ] every placeholder is gone.
- [ ] every decision is `served` or `deferred`.
- [ ] every served order has valid vehicle/trip.
- [ ] every deferred order has blank vehicle/trip.
- [ ] final answer columns equal the frozen allocation.
- [ ] final output semantically equals Phase 23 checker candidate.
- [ ] output read-back passes.
- [ ] output hash is recorded.
- [ ] written policy exists.
- [ ] policy is approximately one page or less.
- [ ] policy explains the allocation objective.
- [ ] policy shows the calculation method.
- [ ] policy identifies actual limiting resources.
- [ ] policy conservatively explains unavoidable deferrals.
- [ ] policy explains shared-resource/policy-choice deferrals.
- [ ] policy explains operational cost/impact.
- [ ] policy explicitly avoids unsupported monetary claims.
- [ ] every numeric policy fact is evidence-backed.
- [ ] no row-level IDs are unnecessarily disclosed.
- [ ] Task 1 remains frozen.
- [ ] Task 2A remains frozen.
- [ ] Phase 22 allocation remains unchanged.
- [ ] Phase 23 evidence remains unchanged.
- [ ] safe tests pass.
- [ ] full suite passes.
- [ ] independent review passes.

Only then:

```text
PHASE 24 STATUS: PASS
submission_task2b.csv: FINAL
TASK 2B POLICY: FINAL
READY FOR PHASE 25: YES
```
