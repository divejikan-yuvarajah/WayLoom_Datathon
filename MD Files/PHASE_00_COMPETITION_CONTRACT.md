# PHASE 00 — Competition Understanding & Scope Freeze

**Project:** WayLoom — Rootcode Tech-Triathlon 2026 Datathon  
**Phase ID:** 00  
**Task range:** DT-000 → DT-010  
**Priority:** P0 — Essential  
**Execution style:** Full phase, documentation-only, followed by an independent review  
**Depends on:** Nothing  
**Blocks:** Phase 01 and every later Datathon phase  
**Primary authority:** Official Rootcode Tech-Triathlon 2026 Challenge Booklet and official supplied competition artifacts  
**Master registry:** `WAYLOOM_DATATHON_MASTER_PLAN.md`

---

## 1. Purpose of this phase

Phase 00 freezes the rules of the Datathon before any environment setup, data processing, feature engineering, modelling, forecasting, optimization, API integration, or submission-file generation begins.

The goal is simple:

> **Every later technical decision must be traceable to a verified competition rule or clearly marked as a WayLoom engineering recommendation.**

This phase is intentionally documentation-only. It prevents the team from building the wrong targets, using the wrong demand accounting logic, applying Hackathon rules to Task 2B, violating data restrictions, or discovering submission requirements too late.

---

## 2. Phase authority and source hierarchy

When sources disagree, use this order:

1. **Latest official organizer clarification**, if one exists and is verifiably official.
2. **Official Rootcode Tech-Triathlon 2026 Challenge Booklet.**
3. **Official supplied competition artifacts**, including submission templates and `check_allocation.py`.
4. **WayLoom Product & Competition Master Plan.**
5. **`WAYLOOM_DATATHON_MASTER_PLAN.md`.**
6. **This Phase 00 implementation guide and later phase/task guides.**

### Conflict rule

If an internal WayLoom document conflicts with the official booklet or an official artifact:

- do **not** silently reconcile it;
- record the conflict;
- use the official requirement;
- update the internal source of truth;
- add a decision-log entry.

---

## 3. Marking convention

Use these labels throughout Phase 00 outputs:

- **[O] OFFICIAL** — directly required, defined, or constrained by the organizer.
- **[E] ENGINEERING** — WayLoom implementation choice needed to execute the official requirement reliably.
- **[C] COMPETITIVE** — optional enhancement intended to differentiate the solution.
- **[A] ASSUMPTION** — temporary assumption that must not be presented as an official fact.

For this phase, DT-000 through DT-010 are all **[O]** in the master registry because they exist to freeze official competition rules.

---

## 4. Phase outputs

Phase 00 should produce the following planning artifacts. Do not create code, notebooks, models, data derivatives, or submission CSVs.

### Required output files

1. `docs/competition_contract.md`  
   The verified Datathon source-of-truth contract containing all official tasks, formulas, outputs, restrictions, deliverables, judging criteria, and deadlines.

2. `docs/competition_requirements_checklist.md`  
   A checkbox-based acceptance list mapping every official requirement to the phase/task that will satisfy it.

3. `docs/internal_milestones.md`  
   A short internal schedule that never changes the official deadline and clearly labels internal dates as team targets rather than organizer requirements.

### Files to read

- Official Challenge Booklet.
- `WAYLOOM_DATATHON_MASTER_PLAN.md`.
- WayLoom Product & Competition Master Plan.
- Official submission-template filenames and checker names, where available.

### Files/folders NOT to read or modify in this phase

- Raw competition CSV contents.
- `DataSet_New.zip` contents.
- model files.
- notebooks.
- source-code modules.
- submission prediction values.
- Hackathon application source code.

Phase 00 does **not** require data access.

---

## 5. Official Datathon contract that must be frozen

The outputs created in this phase must capture the following official requirements exactly in meaning.

### 5.1 Overall Datathon structure

The Datathon is judged separately from the Hackathon. Integration of Datathon models into the Hackathon system is **not required**. The Datathon contains:

1. **Task 1 — Predict service time and lateness**
2. **Task 2A — Forecast depot demand over 10 future weeks**
3. **Task 2B — Allocate the fleet on peak-day scenario S1**

Do not describe the Datathon as one single ML model. Task 2B explicitly does not require a trained model.

### 5.2 Task 1 target definitions

For each planned test `delivery_id`, the official outputs are:

- `pred_service_min`
- `pred_late_prob`

The training labels are constructed from historical actual route events.

Freeze these definitions:

```text
service_start = max(actual_arrival_time, window_open_time)
service_min   = leave_outlet_time - service_start
late_flag     = 1 if actual_arrival_time > window_close_time else 0
```

Important boundary rule:

- arrival **exactly at** `window_close_time` is **not late**;
- lateness is only when actual arrival is **strictly after** the close time.

Prediction-time rule:

- planned journey information may be available;
- actual future journey/handling information exists only in training route records and must never be used as test-time predictors.

Submission rule:

- preserve every supplied Task 1 `delivery_id`;
- preserve original row order;
- do not add or remove rows;
- fill only the required prediction columns.

### 5.3 Task 2A demand-accounting rules

Predict for every supplied depot + brand + forecast-week combination:

- `pred_total_volume_m3`
- `pred_chilled_volume_m3`

Freeze these official accounting rules:

1. Build history from **both** `deliveries_train.csv` and `task1_test_inputs.csv`.
2. Count every unique order once.
3. Include attempted, deferred, and never-dispatched / `not_run` orders because they represent demand.
4. Assign demand to the store-requested `order_date`, not later `dispatch_date`.
5. Join `calendar.csv` and use `iso_year` + `iso_week`.
6. Only Fresh has chilled demand.
7. `pred_chilled_volume_m3` must be exactly `0` for Style.
8. `pred_chilled_volume_m3` must be exactly `0` for Tech.
9. Preserve official `row_id` values in the submission template.
10. The official task asks for volume forecasts, not a conversion into vehicle/driver counts.

### 5.4 Task 2B scenario and outputs

Freeze the official scenario contract:

- Scenario identifier: `S1`.
- Dispatch depot: Peliyagoda.
- Use only vehicles marked `available` in the scenario fleet.
- Vehicles marked `in_workshop` cannot be used.
- Allocation key is `order_ref`, not `outlet_id`.
- Every order must receive a decision: `served` or `deferred`.
- A served order requires `vehicle_id` and `trip_id`.
- A deferred order must leave `vehicle_id` and `trip_id` blank.
- `trip_id` is `1` or `2`.

#### Seven hard feasibility rules

1. **Brand and district** — all orders sharing a `vehicle_id` + `trip_id` must belong to the same brand and district.
2. **Refrigeration** — chilled orders require a reefer vehicle; reefer vehicles may also carry ambient goods.
3. **Vehicle access** — `van_only` outlets require a van.
4. **Home depot** — vehicle and outlet depot must be compatible according to the official scenario/reference data.
5. **Whole orders** — never split a served order across vehicles or trips.
6. **Capacity** — both total trip weight and total trip volume must fit vehicle limits.
7. **Trips and time** — at most two trips per vehicle, with official daily time budgets.

#### Official Task 2B trip-time formula

```text
trip_minutes =
    depot_to_district_freeflow_min
    + inter_stop_freeflow_min * (number_of_orders - 1)
    + sum(service_allowance_min for all stops)
```

Do **not** add a return-to-depot travel leg. The stated time budgets already account for return travel.

Time budgets per vehicle:

- Fresh trip minutes combined: **≤ 270 minutes**.
- Style + Tech trip minutes combined: **≤ 480 minutes**.
- Maximum total trips per vehicle: **2**.

Task 2B requires a short written prioritization policy explaining calculations, limiting resources, deferrals, unavoidable deferrals, chosen tradeoffs, and impact/cost.

The official `check_allocation.py` confirms **feasibility only**. It does not prove that the allocation is optimal or that the prioritization policy is high quality.

### 5.5 Official model/data restrictions

Freeze these restrictions:

- No pretrained models except the stated competition exceptions for synthetic-data generation or preprocessing.
- Proprietary API-based modelling/preprocessing is prohibited.
- Low-code/no-code AI tools or fully automated end-to-end modelling tools are prohibited.
- Supplied competition data may be used only for this competition.
- Competition datasets must not be shared, distributed, or transmitted to third parties.
- Datasets and derivatives must not be publicly disclosed without organizer authorization.
- Maintain an accurate AI-use disclosure.
- If a data/tool workflow is ambiguous under these restrictions, stop and seek organizer clarification rather than assume it is allowed.

### 5.6 Official final deliverables

Freeze the required hand-in list:

- Architecture diagram(s) covering models, preprocessing pipeline, and proposed deployment approach.
- Data preprocessing document covering preparation, label construction, cleaning, feature engineering, and rationale.
- Saved final model file(s).
- `TeamName_FinalNotebook.ipynb` retaining label-construction, preprocessing, training, and evaluation cells.
- A final notebook cell/section that loads the **saved models**, demonstrates Task 1 and Task 2A inference, and clearly prints inputs and predictions.
- `submission_task1.csv`.
- `submission_task2a.csv`.
- `submission_task2b.csv`.
- Task 2B written prioritization policy.
- Unlisted 3–5 minute demo video explaining model architecture, preprocessing, label construction, and challenges encountered.
- AI-tool disclosure.
- Final folder compressed as `TeamName_Datathon.zip`.

### 5.7 Official judging criteria

Freeze the scoring weights:

| Criterion | Weight |
|---|---:|
| Data wrangling and label construction | 20% |
| Model and architecture implementation | 25% |
| Performance score — Task 1 + Task 2A | 20% |
| Task 2B allocation feasibility and prioritization policy | 15% |
| Creativity | 10% |
| Demo video | 10% |

### 5.8 Deadline

Official Datathon submission deadline:

> **Friday, 9 October 2026 at 11:59 PM Sri Lanka time (Asia/Colombo, UTC+05:30).**

Internal milestones may be earlier, but must never be presented as official organizer deadlines.

---

# 6. Task-by-task implementation guide

## DT-000 — Read the official Datathon rules

**Mark:** [O]  
**Priority:** P0  
**Dependency:** None

### Objective
Read and identify every Datathon rule that can change implementation, evaluation, packaging, tool use, or eligibility.

### Why it matters
A modelling solution can be technically strong and still fail if it uses the wrong target, wrong demand date, wrong allocation rules, wrong submission schema, or prohibited tooling.

### Inputs
- Challenge Booklet Datathon pages, especially pp. 15–23 and data reference pp. 24–31.
- Official submission templates/checker documentation where available.

### Output
A source-note section inside `docs/competition_contract.md` mapping each official topic to the relevant booklet page/artifact.

### Detailed instructions
1. Read the Datathon overview.
2. Read Task 1 end-to-end.
3. Read Task 2A end-to-end.
4. Read Task 2B end-to-end.
5. Read rules/regulations and data restrictions.
6. Read official deliverables.
7. Read judging criteria.
8. Read data-reference relationships and checker notes.
9. Record only what the source supports.
10. Mark anything that is a WayLoom interpretation as [E] or [A], never [O].

### Tests / validation
- Confirm all three tasks are identified.
- Confirm the official deliverables section is captured.
- Confirm restrictions are captured.
- Confirm deadline and timezone are captured.

### Edge cases
- A later organizer clarification may supersede the booklet.
- Internal documents may summarize rules imperfectly.
- Hackathon constraints must not be silently applied to Task 2B unless Task 2B explicitly includes them.

### Definition of Done
- [ ] All Datathon source sections have been read.
- [ ] Relevant page/artifact references are recorded.
- [ ] No internal recommendation is mislabeled as official.

### Task STOP conditions
Stop if the official booklet is unavailable, unreadable, incomplete, or conflicts with a later official organizer clarification that has not been resolved.

### Cursor implementation prompt
```text
Implement ONLY DT-000 for WayLoom Datathon Phase 00.

Read the official Datathon sections and official competition artifacts available in the repository/project context. Do not read raw CSV data and do not implement code.

Create/update the source-notes section of docs/competition_contract.md.

Capture:
- Datathon overview
- Task 1
- Task 2A
- Task 2B
- restrictions
- deliverables
- judging criteria
- deadline/timezone
- data-reference/checker notes

For every item, preserve official meaning and record the official source page/artifact.
Mark interpretations as [E] or [A], never [O].

Do not execute DT-001 or later tasks.
Report DT-000 PASS/FAIL and any source conflicts, then STOP.
```

### Codex implementation prompt
```text
Execute only DT-000 from PHASE_00_COMPETITION_CONTRACT.md.
This is documentation-only.

Inspect the official Challenge Booklet and official competition artifacts, not raw competition CSV contents.
Update docs/competition_contract.md with a concise official-source map for the Datathon rules.

Do not infer missing rules and do not copy Hackathon rules into Task 2B.
Do not modify code/notebooks/models/submission files.

Return:
- sections reviewed
- official source references captured
- conflicts/ambiguities
- DT-000 status
Then stop before DT-001.
```

---

## DT-001 — Create competition requirements checklist

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-000 recommended

### Objective
Convert the official Datathon rules into an actionable checklist that can be verified before final submission.

### Inputs
- Verified DT-000 source notes.
- Official booklet and artifacts.

### Output
`docs/competition_requirements_checklist.md`

### Detailed instructions
Organize the checklist into:

1. Task 1 input/label/output requirements.
2. Task 2A input/accounting/output requirements.
3. Task 2B scenario/feasibility/output/policy requirements.
4. Tool/model/data restrictions.
5. Notebook/model-artifact requirements.
6. Documentation requirements.
7. Demo requirements.
8. Packaging/naming/deadline requirements.

For each checklist row include:

```text
Requirement ID | Requirement | Source | Planned phase/task | Status
```

Use stable IDs such as `REQ-T1-001`, `REQ-T2A-001`, `REQ-T2B-001`, `REQ-SUB-001`.

### Tests / validation
- Every requirement in the contract appears in the checklist.
- Every checklist requirement has a source.
- Every checklist requirement has a planned future phase/task owner.

### Edge cases
If one official requirement maps to multiple future tasks, list all relevant task IDs rather than forcing a one-to-one mapping.

### Definition of Done
- [ ] Checklist file exists.
- [ ] No official requirement is unmapped.
- [ ] Every row has a source and owner task/phase.

### Task STOP conditions
Stop if a requirement cannot be mapped to a source or if its implementation owner is unclear.

### Cursor implementation prompt
```text
Implement ONLY DT-001.

Using the verified Phase 00 official contract, create docs/competition_requirements_checklist.md.

Include every official Datathon requirement under Task 1, Task 2A, Task 2B, restrictions, deliverables, demo, packaging, naming, and deadline.

For each requirement include:
Requirement ID | Requirement | Official source | Future phase/task owner | Status checkbox

Do not invent requirements.
Do not implement any technical task.
Do not continue to DT-002.

Run a coverage review against docs/competition_contract.md and report unmapped items.
Then STOP.
```

### Codex implementation prompt
```text
Execute only DT-001 from Phase 00.
Create docs/competition_requirements_checklist.md from the already verified official contract.

Use stable requirement IDs and map each official requirement to the future DT task(s) that will satisfy it.
No code, no data access, no modelling.

Validate that every official rule in the contract appears at least once in the checklist.
Return PASS/FAIL, missing mappings, and file changed. Stop before DT-002.
```

---

## DT-002 — Separate the three Datathon problems

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-000

### Objective
Freeze the fact that the Datathon has three distinct problem types and prevent architecture/model confusion.

### Output
A section in `docs/competition_contract.md` named **Problem Decomposition**.

### Required content

| Task | Official problem | Required output | Nature |
|---|---|---|---|
| Task 1 | Service-time + lateness prediction | `pred_service_min`, `pred_late_prob` | prediction; two targets |
| Task 2A | 10-week depot/brand demand forecast | total + chilled m³ | forecasting |
| Task 2B | Peak-day S1 fleet allocation | served/deferred + vehicle/trip + written policy | constraint allocation; no trained model required |

### Tests / validation
- Task 1 must not be described as one target.
- Task 2B must not be described as requiring ML.
- Optional Hackathon integration must not be presented as mandatory.

### Definition of Done
- [ ] Three problems are clearly separated.
- [ ] Inputs/outputs and purpose are distinguishable.
- [ ] Optional integration is marked optional.

### STOP conditions
Stop if internal architecture assumes one common model or requires Datathon integration to complete the official Hackathon.

### Cursor implementation prompt
```text
Implement ONLY DT-002.
Add a Problem Decomposition section to docs/competition_contract.md.
Clearly separate Task 1, Task 2A, and Task 2B with official purpose and outputs.
State that Task 2B does not require a trained model and Datathon/Hackathon integration is optional.
Do not design models yet.
Stop before DT-003.
```

### Codex implementation prompt
```text
Execute only DT-002.
Document the three official Datathon problem types in docs/competition_contract.md.
Preserve organizer terminology and required outputs.
Do not introduce model choices or optimization policies.
Report PASS/FAIL, then stop.
```

---

## DT-003 — Freeze Task 1 target definitions

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-000

### Objective
Create an immutable written contract for Task 1 target construction before any data code is written.

### Output
A **Task 1 Target Contract** section in `docs/competition_contract.md`.

### Official formulas

```text
service_start = max(actual_arrival_time, window_open_time)
service_min   = leave_outlet_time - service_start
late_flag     = 1 if actual_arrival_time > window_close_time else 0
```

### Required boundary examples

1. Early arrival before open → service starts at opening.
2. Arrival after open but before close → service starts at arrival.
3. Arrival exactly at close → `late_flag = 0`.
4. Arrival one minute after close → `late_flag = 1`.

### Leakage contract
Historical actual journey fields may construct labels in training but must not become prediction-time features for test inference.

### Tests / validation
Perform a manual formula review and ensure the exact comparison operator for lateness is `>` rather than `>=`.

### Definition of Done
- [ ] Formula exists exactly in meaning.
- [ ] Boundary examples documented.
- [ ] Leakage rule documented.
- [ ] Required Task 1 output columns documented.

### STOP conditions
Stop if any team document defines service time from raw arrival without respecting waiting until window opening, or uses `>=` for late.

### Cursor implementation prompt
```text
Implement ONLY DT-003.
Freeze the official Task 1 target contract in docs/competition_contract.md.

Document:
service_start = max(actual_arrival_time, window_open_time)
service_min = leave_outlet_time - service_start
late_flag = 1 only when actual_arrival_time > window_close_time

Add boundary examples and the rule that actual future journey/handling fields cannot be prediction-time features.
Do not implement label code yet.
Stop before DT-004.
```

### Codex implementation prompt
```text
Execute only DT-003.
Add the verified Task 1 target definitions and edge-case examples to the competition contract.
Explicitly verify strict-after-close lateness and early-arrival waiting.
No Python implementation yet.
Return PASS/FAIL and stop.
```

---

## DT-004 — Freeze Task 2A demand rules

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-000

### Objective
Prevent the most common Task 2A accounting errors before aggregation/forecasting begins.

### Output
A **Task 2A Demand Contract** section in `docs/competition_contract.md`.

### Required rules
- combine `deliveries_train.csv` and `task1_test_inputs.csv` for demand history;
- each unique order counts once;
- include attempted, deferred, and `not_run` orders;
- use requested `order_date`;
- derive forecast week using `calendar.csv` `iso_year` + `iso_week`;
- only Fresh has chilled demand;
- Style chilled prediction = exactly 0;
- Tech chilled prediction = exactly 0;
- official outputs are volumes, not vehicle/driver counts;
- preserve official `row_id` values.

### Tests / validation
Create a paper example where an order requested in week 38 but dispatched in week 39 must count toward week 38 demand.

### Definition of Done
- [ ] All official accounting rules documented.
- [ ] Deferred/not-run handling explicit.
- [ ] Requested-date vs dispatch-date distinction explicit.
- [ ] chilled-zero rules explicit.

### STOP conditions
Stop if any internal plan says to forecast delivered volume instead of requested volume.

### Cursor implementation prompt
```text
Implement ONLY DT-004.
Add the official Task 2A demand-accounting contract to docs/competition_contract.md.
Include both source order files, unique-order counting, attempted/deferred/not_run inclusion, requested order_date, calendar ISO week, chilled-zero rules for Style/Tech, official outputs, and row_id preservation.
Add one deferred-order week example.
No forecasting code.
Stop before DT-005.
```

### Codex implementation prompt
```text
Execute only DT-004.
Freeze Task 2A's official demand accounting rules in the contract.
Do not infer any forecast model or vehicle conversion.
Validate the requested-week vs dispatch-week distinction.
Return PASS/FAIL and stop.
```

---

## DT-005 — Freeze Task 2B seven feasibility rules

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-000

### Objective
Create an exact hard-constraint contract for Scenario S1.

### Output
A **Task 2B Feasibility Contract** section in `docs/competition_contract.md`.

### Required content
Record the seven rules exactly in meaning:

1. same brand and district per trip;
2. chilled → reefer;
3. `van_only` → van;
4. home depot restriction;
5. whole order, never split;
6. weight **and** volume capacity;
7. maximum two trips and official time budgets.

Also record:
- S1;
- Peliyagoda;
- `available` vehicles only;
- exclude `in_workshop`;
- use `order_ref` as allocation key.

### Tests / validation
Create a seven-row validation matrix with one invalid example per rule.

### Definition of Done
- [ ] All seven hard rules present.
- [ ] Scenario context present.
- [ ] `order_ref` key rule present.
- [ ] No Hackathon-only constraint silently added.

### STOP conditions
Stop if fuel quotas, general Hackathon windows, or other rules are being added to the Task 2B validator without official Task 2B support.

### Cursor implementation prompt
```text
Implement ONLY DT-005.
Document Task 2B Scenario S1 and all seven official feasibility rules in docs/competition_contract.md.
Add a validation matrix with one violating example per rule.
Explicitly separate Task 2B hard rules from broader Hackathon planning rules.
Do not implement the optimizer.
Stop before DT-006.
```

### Codex implementation prompt
```text
Execute only DT-005.
Freeze the exact seven Task 2B feasibility rules, scenario scope, available-vehicle rule, workshop exclusion, and order_ref allocation key.
Do not add non-Task-2B constraints.
Return PASS/FAIL and stop.
```

---

## DT-006 — Freeze Task 2B trip-time formula

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-005

### Objective
Prevent a mathematically incorrect allocation validator or solver.

### Output
A **Task 2B Trip-Time Contract** section in `docs/competition_contract.md`.

### Official formula

```text
trip_minutes =
    depot_to_district_freeflow_min
  + inter_stop_freeflow_min * (number_of_orders - 1)
  + Σ service_allowance_min
```

### Required clarifications
- outbound travel counted once per trip;
- a one-order trip has zero inter-stop movements;
- service allowance uses brand + dock type;
- do not add return travel;
- Fresh combined minutes/vehicle ≤270;
- Style+Tech combined minutes/vehicle ≤480;
- total trips/vehicle ≤2.

### Required worked check
Document the official three-Fresh-stop Gampaha example total of 101 minutes as a later unit-test reference.

### Tests / validation
Check the arithmetic structure against the official example and ensure no return leg appears.

### Definition of Done
- [ ] Formula frozen.
- [ ] budgets frozen.
- [ ] return-leg prohibition explicit.
- [ ] official worked example captured as test reference.

### STOP conditions
Stop if any implementation plan adds return travel or applies 270/480 as per-trip rather than the defined per-vehicle category budgets.

### Cursor implementation prompt
```text
Implement ONLY DT-006.
Add the official Task 2B trip-time formula and time budgets to docs/competition_contract.md.
Include the official 101-minute Gampaha example as a future unit-test reference.
Explicitly state that no return-to-depot leg is added.
No solver code.
Stop before DT-007.
```

### Codex implementation prompt
```text
Execute only DT-006.
Freeze the exact trip-duration formula, budget semantics, max-two-trips rule, and official worked-example reference.
Check that return travel is excluded.
Return PASS/FAIL and stop.
```

---

## DT-007 — Freeze official submission file structures

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-000

### Objective
Lock filenames, identifier preservation, and answer columns before any inference/export code exists.

### Output
A **Submission Schema Contract** section in `docs/competition_contract.md`.

### Required schemas

#### Task 1 — `submission_task1.csv`
- `delivery_id` — supplied ID; unchanged; preserve original row order.
- `pred_service_min` — numeric predicted handling minutes.
- `pred_late_prob` — probability in `[0,1]`.

#### Task 2A — `submission_task2a.csv`
- `row_id` — supplied ID; unchanged.
- `pred_total_volume_m3` — predicted total volume.
- `pred_chilled_volume_m3` — predicted chilled volume; exactly 0 for Style/Tech.

#### Task 2B — `submission_task2b.csv`
- `scenario` — supplied; S1.
- `order_ref` — supplied; allocation key.
- `outlet_id` — supplied.
- `decision` — `served` or `deferred`.
- `vehicle_id` — required for served; blank for deferred.
- `trip_id` — 1 or 2 for served; blank for deferred.

### Tests / validation
- filenames match official templates;
- no extra columns introduced;
- identifier preservation rules captured;
- Task 1 row-order requirement explicitly captured;
- Task 2B placeholder replacement requirement captured.

### Definition of Done
- [ ] Three schemas documented.
- [ ] Identifier rules documented.
- [ ] Blank-field rules documented.

### STOP conditions
Stop if template files available locally disagree with the documented schema; the official template then becomes the artifact to inspect and reconcile.

### Cursor implementation prompt
```text
Implement ONLY DT-007.
Add the exact official submission schema contract for submission_task1.csv, submission_task2a.csv, and submission_task2b.csv.
Document identifier preservation, Task 1 row-order preservation, required answer columns, Task 2B blank-field rules, and placeholder replacement.
Do not generate predictions or modify templates.
Stop before DT-008.
```

### Codex implementation prompt
```text
Execute only DT-007.
Document the three official submission filenames/schemas and all ID/order preservation rules.
If local official templates conflict with the written contract, stop and report the mismatch rather than editing them.
No inference/export code.
```

---

## DT-008 — Record competition restrictions

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-000

### Objective
Prevent accidental disqualification or restricted data exposure.

### Output
A **Competition Restrictions & Data Safety** section in `docs/competition_contract.md` and corresponding checklist items in `docs/competition_requirements_checklist.md`.

### Required content
Capture official restrictions on:

- pretrained models;
- proprietary API modelling/preprocessing;
- low-code/no-code and fully automated end-to-end modelling;
- dataset usage scope;
- dataset sharing/distribution;
- public publication/disclosure of datasets or derivatives;
- confidentiality;
- integrity/cheating/plagiarism;
- AI-tool disclosure.

### WayLoom operating rule [E]
Because the official terms restrict third-party data sharing, raw competition data must not be pasted into AI prompts or sent to external services unless the organizer explicitly confirms that workflow is permitted.

### Tests / validation
Create a tool-use decision table:

```text
Activity | Allowed by explicit rule? | Risk/ambiguity | Team action
```

For ambiguous external-tool workflows, mark **STOP / seek organizer clarification**.

### Definition of Done
- [ ] Restrictions section exists.
- [ ] AI/data-sharing risk is explicit.
- [ ] Ambiguous workflows have a stop rule.

### STOP conditions
Stop the project if any planned tool workflow requires prohibited or ambiguous dataset transmission and no official clarification exists.

### Cursor implementation prompt
```text
Implement ONLY DT-008.
Document all official Datathon model/tool/data restrictions and AI-use disclosure requirements.
Add a conservative WayLoom data-safety rule: do not send raw competition data or derivatives to external services when the rules make that workflow prohibited or ambiguous; seek organizer clarification instead.
Do not access raw data.
Stop before DT-009.
```

### Codex implementation prompt
```text
Execute only DT-008.
Add the official restrictions and a tool-use safety decision table to the competition contract/checklist.
Do not reinterpret ambiguous restrictions as permission.
Flag ambiguity for organizer clarification.
Return PASS/FAIL and stop.
```

---

## DT-009 — Record judging criteria

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-000

### Objective
Freeze the official score weights so later prioritization reflects how the competition is judged.

### Output
A **Judging Contract** section in `docs/competition_contract.md`.

### Official scoring

| Criterion | Weight |
|---|---:|
| Data wrangling and label construction | 20% |
| Model and architecture implementation | 25% |
| Performance score — Task 1 + Task 2A | 20% |
| Task 2B allocation feasibility and prioritization policy | 15% |
| Creativity | 10% |
| Demo video | 10% |

### Implementation note [E]
Add a short planning implication section, clearly marked [E], explaining that the team should not optimize only for predictive accuracy because 80% of the score is allocated across broader criteria, including wrangling/labels, architecture, Task 2B, creativity, and demo.

### Tests / validation
- weights total 100%;
- all labels match official meaning;
- engineering interpretation is marked [E].

### Definition of Done
- [ ] All weights recorded.
- [ ] Total = 100%.
- [ ] Planning implication separated from official facts.

### STOP conditions
Stop if another internal document uses a different Datathon scoring table without official evidence.

### Cursor implementation prompt
```text
Implement ONLY DT-009.
Add the exact official Datathon judging criteria and weights to docs/competition_contract.md.
Verify they total 100%.
Add a separately marked [E] planning implication, without turning it into an official rule.
Stop before DT-010.
```

### Codex implementation prompt
```text
Execute only DT-009.
Record the official judging weights and validate their sum.
Keep any prioritization interpretation clearly labeled engineering guidance.
Return PASS/FAIL and stop.
```

---

## DT-010 — Freeze deadline and internal milestones

**Mark:** [O]  
**Priority:** P0  
**Dependency:** DT-000–DT-009

### Objective
Lock the official deadline and create conservative internal milestones without confusing the two.

### Outputs
- deadline section in `docs/competition_contract.md`;
- `docs/internal_milestones.md`.

### Official deadline

**Friday, 9 October 2026 at 11:59 PM Sri Lanka time (Asia/Colombo, UTC+05:30).**

### Recommended internal milestone logic [E]
Use internal milestones that finish major technical work before the final day. At minimum define:

- competition contract freeze;
- data audit/Task 1 labels complete;
- Task 1 candidate models complete;
- Task 2A forecast candidate complete;
- Task 2B first feasible allocation + checker pass;
- model/allocation freeze;
- final notebook/docs/video freeze;
- clean reproduction + packaging;
- submission buffer.

Do not fabricate organizer milestones. Label every internal date **TEAM TARGET**.

### Tests / validation
- official deadline appears once as official source of truth;
- internal dates are labeled as team targets;
- internal plan includes a submission buffer;
- timezone is explicit.

### Definition of Done
- [ ] Official deadline frozen.
- [ ] Internal milestones documented.
- [ ] No internal milestone is presented as organizer-mandated.

### STOP conditions
Stop if the team has conflicting official deadline information; resolve from organizer source before proceeding.

### Cursor implementation prompt
```text
Implement ONLY DT-010.
Freeze the official Datathon deadline in docs/competition_contract.md and create docs/internal_milestones.md.

Official deadline:
Friday, 9 October 2026, 11:59 PM Sri Lanka time (Asia/Colombo, UTC+05:30).

Create conservative TEAM TARGET milestones for the remaining work, but clearly distinguish them from the official deadline.
Include a final submission buffer.
Do not start Phase 01.
Return DT-010 PASS/FAIL and STOP.
```

### Codex implementation prompt
```text
Execute only DT-010.
Document the official Datathon deadline and create an internal milestone plan whose dates are explicitly labeled TEAM TARGET.
Never present internal milestones as organizer requirements.
Do not initialize the repository or begin Phase 01.
Return PASS/FAIL and stop.
```

---

# 7. Phase 00 testing strategy

Phase 00 does not have software unit tests. It uses **contract verification tests**.

## 7.1 Registry coverage test

Expected task set:

```text
DT-000, DT-001, DT-002, DT-003, DT-004,
DT-005, DT-006, DT-007, DT-008, DT-009, DT-010
```

Expected task count: **11**.

## 7.2 Contract verification checklist

- [ ] Three Datathon problems are separated correctly.
- [ ] Task 1 formulas are captured exactly in meaning.
- [ ] Task 1 late boundary uses strict `>`.
- [ ] Task 1 original row-order requirement is captured.
- [ ] Task 2A uses both official order sources.
- [ ] Task 2A includes deferred and `not_run` demand.
- [ ] Task 2A uses requested `order_date`.
- [ ] Task 2A uses calendar ISO week.
- [ ] Style and Tech chilled predictions are exactly zero.
- [ ] Task 2B has exactly seven feasibility rules.
- [ ] Task 2B uses `order_ref` as allocation key.
- [ ] Task 2B excludes `in_workshop` vehicles.
- [ ] Task 2B trip formula excludes return travel.
- [ ] Fresh 270-minute budget captured.
- [ ] Style+Tech 480-minute budget captured.
- [ ] Maximum two trips captured.
- [ ] Submission schemas captured.
- [ ] Data/model/tool restrictions captured.
- [ ] Required deliverables captured.
- [ ] Judging weights total 100%.
- [ ] Datathon deadline and timezone captured.
- [ ] Datathon/Hackathon integration is not presented as mandatory.

## 7.3 Cross-source conflict test

Compare:

1. `docs/competition_contract.md`
2. official booklet
3. official templates/checker notes
4. WayLoom master plan
5. `WAYLOOM_DATATHON_MASTER_PLAN.md`

Any conflict with official sources must be resolved before Phase 01.

---

# 8. Phase-wide edge cases

1. **Later official clarification appears**  
   Update the contract, cite the clarification, mark the previous rule superseded, and log the decision.

2. **Official template differs from booklet prose**  
   Stop and inspect whether this is a schema/detail clarification. Do not silently edit the template.

3. **Hackathon planner rule differs from Task 2B rule**  
   Keep the rule sets separate. Task 2B is evaluated against its explicit scenario contract.

4. **Internal master plan contains a recommendation phrased too strongly**  
   Relabel it [E] or [C]. Do not promote it to [O].

5. **Unclear use of an AI/cloud tool with restricted data**  
   Stop. Do not upload or transmit competition data. Seek organizer clarification.

6. **Deadline shown without timezone**  
   Treat it as incomplete until Asia/Colombo / Sri Lanka time is explicitly recorded.

7. **Task 1 equality-at-close ambiguity**  
   Official rule is strict-after-close; equality is not late.

8. **Task 2A `not_run` confusion**  
   `not_run` is still demand and must be counted.

9. **Task 2B return-leg confusion**  
   Do not add return travel to the official formula.

10. **Task 2B checker misconception**  
    Checker pass means feasible, not optimal.

---

# 9. Global Phase 00 STOP CONDITIONS

Do **not** proceed to Phase 01 if any of the following is true:

- [ ] official Challenge Booklet cannot be accessed;
- [ ] Task 1 target formulas are unresolved;
- [ ] Task 2A demand accounting is unresolved;
- [ ] any of the seven Task 2B hard rules is unresolved;
- [ ] Task 2B trip formula/budgets are unresolved;
- [ ] official submission schemas are unclear;
- [ ] tool/model/data restrictions are not documented;
- [ ] judging weights are not verified;
- [ ] official deadline/timezone is not verified;
- [ ] a conflict between official and internal rules remains unresolved;
- [ ] an external data/tool workflow is planned despite unresolved confidentiality ambiguity.

If a STOP CONDITION occurs, record it under **Open Issues** and do not silently continue.

---

# 10. Phase 00 Definition of Done

Phase 00 is complete only when all of the following are true:

- [ ] DT-000 PASS
- [ ] DT-001 PASS
- [ ] DT-002 PASS
- [ ] DT-003 PASS
- [ ] DT-004 PASS
- [ ] DT-005 PASS
- [ ] DT-006 PASS
- [ ] DT-007 PASS
- [ ] DT-008 PASS
- [ ] DT-009 PASS
- [ ] DT-010 PASS
- [ ] `docs/competition_contract.md` exists and is reviewed.
- [ ] `docs/competition_requirements_checklist.md` exists and maps official requirements to future work.
- [ ] `docs/internal_milestones.md` exists and labels all non-official dates as TEAM TARGET.
- [ ] Cross-source conflict review is clean.
- [ ] No raw competition dataset content was accessed, copied, or transmitted for this documentation phase.
- [ ] No technical implementation was started prematurely.
- [ ] `WAYLOOM_DATATHON_MASTER_PLAN.md` still contains Phase 00 as DT-000 → DT-010 with no task-ID drift.

**Phase complete:** [ ]  
**READY FOR PHASE 01:** NO

Change `READY FOR PHASE 01` to **YES** only after the independent Phase 00 review passes.

---

# 11. Git workflow

Phase 00 occurs before the official repository-initialization task in Phase 01.

## If Git has NOT yet been initialized

Do not initialize Git early just for this phase. Create the documentation files locally. Phase 01 will initialize the repository and then include the approved Phase 00 documents in the first controlled commit.

## If a Git repository already exists

Recommended branch:

```bash
git checkout -b docs/phase-00-competition-contract
```

Suggested commits:

```text
docs(datathon): freeze official competition contract
docs(datathon): add official requirements checklist
docs(datathon): add internal milestone schedule
```

Before merge:

- run the Phase 00 independent review;
- resolve all official/internal conflicts;
- verify no raw data or derivatives are staged.

Example safety check:

```bash
git status
git diff --cached --name-only
```

Do not commit any official raw CSVs.

---

# 12. Full-phase Cursor implementation prompt

Use this when you want Cursor to implement the complete Phase 00 rather than task-by-task.

```text
You are implementing WayLoom Datathon Phase 00 — Competition Understanding & Scope Freeze.

AUTHORITATIVE FILES:
1. Official Rootcode Tech-Triathlon 2026 Challenge Booklet
2. Official competition templates/checker documentation available locally
3. WAYLOOM_DATATHON_MASTER_PLAN.md
4. PHASE_00_COMPETITION_CONTRACT.md
5. WayLoom Product & Competition Master Plan as an internal interpretation only

SCOPE:
Implement every task DT-000 through DT-010 and nothing beyond Phase 00.

THIS PHASE IS DOCUMENTATION-ONLY.
Do not initialize the Python environment, process CSVs, write modelling code, build notebooks, train models, generate predictions, implement Task 2B optimization, or begin Phase 01.

DO NOT READ OR TRANSMIT RAW COMPETITION DATA.
Phase 00 does not require CSV access.

CREATE/UPDATE:
- docs/competition_contract.md
- docs/competition_requirements_checklist.md
- docs/internal_milestones.md

EXECUTE IN ORDER:
DT-000 Read and map official Datathon rules.
DT-001 Build official requirements checklist.
DT-002 Separate Task 1 / Task 2A / Task 2B.
DT-003 Freeze Task 1 target definitions.
DT-004 Freeze Task 2A demand rules.
DT-005 Freeze Task 2B seven feasibility rules.
DT-006 Freeze Task 2B trip-time formula and budgets.
DT-007 Freeze submission schemas.
DT-008 Record model/tool/data restrictions.
DT-009 Record judging criteria.
DT-010 Freeze official deadline and internal TEAM TARGET milestones.

PRESERVE OFFICIAL MEANING:
Task 1:
service_start = max(actual_arrival_time, window_open_time)
service_min = leave_outlet_time - service_start
late_flag = 1 only if actual_arrival_time > window_close_time
Preserve delivery_id and original Task 1 row order.
Actual future journey/handling information must not become prediction-time features.

Task 2A:
Use deliveries_train.csv + task1_test_inputs.csv for demand history.
Count each unique order once, including deferred and not_run.
Use requested order_date.
Use calendar iso_year + iso_week.
Style chilled = exactly 0.
Tech chilled = exactly 0.

Task 2B:
S1, Peliyagoda, available vehicles only, no in_workshop vehicles.
Use order_ref as allocation key.
Hard rules: same brand+district, chilled→reefer, van_only→van, home depot, whole order, weight+volume, max two trips + time budgets.
trip_minutes = outbound district free-flow + inter-stop free-flow*(n-1) + sum(service allowance)
DO NOT add return travel.
Fresh <= 270 minutes per vehicle.
Style+Tech <= 480 minutes per vehicle.
Maximum two trips total.
check_allocation.py proves feasibility only.

RESTRICTIONS:
Preserve official restrictions on pretrained models, proprietary API modelling/preprocessing, low-code/no-code/fully automated modelling, data use/sharing/publication/confidentiality, and AI-use disclosure.
If an external tool/data workflow is ambiguous, mark STOP / seek organizer clarification. Do not assume permission.

DELIVERABLES:
Capture all official final Datathon deliverables and the 3–5 minute unlisted demo requirement.

JUDGING:
Record the official 20/25/20/15/10/10 percentage weights and verify total=100%.

DEADLINE:
Friday, 9 October 2026 at 11:59 PM Sri Lanka time (Asia/Colombo, UTC+05:30).
Internal dates must be labelled TEAM TARGET.

CONFLICT HANDLING:
Official organizer source wins over internal WayLoom guidance.
Do not silently reconcile conflicts. Record them.

VALIDATION BEFORE FINISHING:
- verify all 11 tasks DT-000...DT-010 are completed
- verify all three output docs exist
- verify Task 1 strict > close rule
- verify Task 2A not_run/deferred/requested-date rules
- verify exactly seven Task 2B feasibility rules
- verify no return leg
- verify submission schemas
- verify restrictions
- verify judging weights total 100%
- verify deadline/timezone
- verify no raw data was accessed or added

If any STOP CONDITION in PHASE_00_COMPETITION_CONTRACT.md is triggered, STOP immediately and report it.

FINAL REPORT FORMAT:
PHASE: 00
TASKS:
DT-000 PASS/FAIL
...
DT-010 PASS/FAIL

FILES CREATED/MODIFIED:
...

OFFICIAL/INTERNAL CONFLICTS:
...

STOP CONDITIONS:
...

PHASE 00 STATUS: PASS/FAIL
READY FOR PHASE 01: YES/NO

Do not begin Phase 01.
```

---

# 13. Full-phase Codex implementation prompt

```text
Work only on WayLoom Datathon Phase 00.

Read first:
- PHASE_00_COMPETITION_CONTRACT.md
- WAYLOOM_DATATHON_MASTER_PLAN.md
- official Rootcode Tech-Triathlon 2026 Challenge Booklet
- official template/checker documentation that can be inspected without processing private raw datasets

Treat the official organizer materials as authoritative. Treat WayLoom planning documents as internal guidance only.

Implement DT-000 through DT-010 exactly as defined in the Phase 00 guide.

This is a documentation-only phase.
Do not touch:
- raw CSV contents
- DataSet_New.zip contents
- Python source modules
- notebooks
- models
- output predictions
- submission CSV values
- Hackathon application code

Create/update:
1. docs/competition_contract.md
2. docs/competition_requirements_checklist.md
3. docs/internal_milestones.md

The contract must freeze:
- Task 1 targets and strict late boundary
- Task 1 ID/original-order submission rule
- Task 2A two-source demand history
- inclusion of deferred and not_run demand
- requested order_date + ISO week
- zero chilled volume for Style/Tech
- Task 2B S1 scope
- available-only/workshop exclusion
- order_ref allocation key
- exactly seven hard feasibility rules
- exact Task 2B trip-time formula
- no return leg
- Fresh 270-minute and Style+Tech 480-minute vehicle budgets
- maximum two trips
- submission schemas
- model/API/AI/data restrictions
- required deliverables
- official judging weights
- final deadline/timezone
- optional nature of Datathon-to-Hackathon integration

The requirements checklist must map each official requirement to its future DT task(s).

The milestone file must distinguish:
OFFICIAL DEADLINE
from
TEAM TARGETS.

Do not invent organizer requirements.
Do not convert WayLoom recommendations into official facts.
Do not silently resolve conflicts.

Run a Phase 00 documentation audit when complete:
- task coverage DT-000...DT-010 = 11/11
- judging weights = 100%
- Task 2B hard-rule count = 7
- no unresolved official/internal conflict
- no raw data access
- no Phase 01 implementation

Return only:
PHASE 00 TASK STATUS TABLE
FILES CREATED/MODIFIED
CONFLICTS/AMBIGUITIES
STOP CONDITIONS
PHASE 00 PASS/FAIL
READY FOR PHASE 01 YES/NO

Then stop.
```

---

# 14. Independent review prompt — Cursor or Codex

Run this with a fresh agent/context after implementation if possible.

```text
Independently review WayLoom Datathon Phase 00.

DO NOT MODIFY FILES initially.

Review:
- PHASE_00_COMPETITION_CONTRACT.md
- WAYLOOM_DATATHON_MASTER_PLAN.md
- docs/competition_contract.md
- docs/competition_requirements_checklist.md
- docs/internal_milestones.md
- official Rootcode Tech-Triathlon 2026 Challenge Booklet
- official template/checker documentation where relevant

Audit DT-000 through DT-010.

For every task return:
Task ID | PASS/FAIL | Evidence | Issue / Missing Item

Verify specifically:
1. Three Datathon problems are correctly separated.
2. Task 1 service_start/service_min formulas are correct.
3. late_flag uses strictly after window close, not >=.
4. Task 1 delivery_id and original-row-order requirements are captured.
5. Task 2A uses both deliveries_train.csv and task1_test_inputs.csv.
6. deferred and not_run orders count as demand.
7. requested order_date is used, not dispatch_date.
8. calendar ISO year/week is captured.
9. Style and Tech chilled prediction = exactly 0.
10. Task 2B has exactly seven hard feasibility rules.
11. Task 2B uses order_ref, available vehicles only, excludes in_workshop.
12. trip formula is exact in meaning and return travel is excluded.
13. Fresh <=270 and Style+Tech <=480 per vehicle; maximum two trips.
14. submission schemas and identifier-preservation rules are correct.
15. model/tool/data restrictions are captured accurately.
16. final deliverables are complete.
17. judging weights are 20/25/20/15/10/10 and total 100%.
18. official deadline is 9 Oct 2026, 11:59 PM Sri Lanka time.
19. internal milestones are clearly labelled TEAM TARGET.
20. Datathon/Hackathon integration is not falsely presented as mandatory.
21. no WayLoom recommendation is mislabeled official.
22. no raw competition data was unnecessarily accessed or copied.
23. all 11 Phase 00 tasks are represented.

Do not fix anything unless explicitly asked after the review.

Return:
PHASE 00 REVIEW: PASS/FAIL
BLOCKERS:
...
NON-BLOCKING IMPROVEMENTS:
...
READY FOR PHASE 01: YES/NO

Stop.
```

---

# 15. Phase completion report template

Complete this after implementation and independent review.

```markdown
## Phase 00 Completion Report

### Task Status
- [x] DT-000 — Read official Datathon rules
- [x] DT-001 — Competition requirements checklist
- [x] DT-002 — Separate three Datathon problems
- [x] DT-003 — Freeze Task 1 target definitions
- [x] DT-004 — Freeze Task 2A demand rules
- [x] DT-005 — Freeze Task 2B seven feasibility rules
- [x] DT-006 — Freeze Task 2B trip-time formula
- [x] DT-007 — Freeze submission structures
- [x] DT-008 — Record competition restrictions
- [x] DT-009 — Record judging criteria
- [x] DT-010 — Freeze deadline and internal milestones

### Files Created / Updated
- [x] docs/competition_contract.md
- [x] docs/competition_requirements_checklist.md
- [x] docs/internal_milestones.md

### Validation
- [x] All official rules source-verified
- [x] Judging weights total 100%
- [x] Exactly seven Task 2B hard rules
- [x] No unresolved source conflict
- [x] No raw data accessed
- [x] No technical implementation started

### Open Issues
- None. Documented interpretation tensions are recorded in `docs/competition_contract.md`; official sources control.

### Decisions Recorded
- Phase 00 conflict register created in `docs/competition_contract.md`.

### Independent Review
- Reviewer: Documentation audit performed against the project booklet and internal guidance
- Date/time: 2026-10-02
- Result: PASS

### Phase Result
PHASE 00 STATUS: PASS
READY FOR PHASE 01: YES
```

---

# 16. Final instruction

When Phase 00 passes, **do not start modelling**. The next phase is:

> `PHASE_01_PROJECT_ENVIRONMENT.md` — project environment and repository setup.

Phase 01 may begin only when `READY FOR PHASE 01 = YES`.
