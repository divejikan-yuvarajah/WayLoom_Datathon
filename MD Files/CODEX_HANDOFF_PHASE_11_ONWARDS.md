# WayLoom Datathon — Codex Handoff Guide (Phase 11 Onwards)

> **Project:** WayLoom — Rootcode Tech-Triathlon 2026 Datathon  
> **Purpose:** Transfer the repository safely from Cursor-based development to OpenAI Codex in VS Code without losing the decisions, safety boundaries, phase gates, or reproducibility controls established in Phases 00–10.  
> **Current milestone:** Phases 00–10 are complete. Task 1 final output has passed final revalidation and `outputs/submission_task1.csv` is considered frozen unless a later global validation phase finds a genuine defect.  
> **Next implementation phase:** Phase 11 — Task 2A demand-history construction (`DT-174` → `DT-191`).

---

# 1. How to use this file

Keep this document in the repository root (or in `docs/`) and make Codex read it at the start of Phase 11.

Recommended files:

```text
AGENTS.md
CODEX_HANDOFF_PHASE_11_ONWARDS.md
WAYLOOM_DATATHON_MASTER_PLAN.md
PHASE_00_COMPETITION_CONTRACT.md
...
PHASE_10_COMPETITION_CONTRACT.md
```

For each later phase, add the new phase contract before implementation, for example:

```text
PHASE_11_COMPETITION_CONTRACT.md
PHASE_12_COMPETITION_CONTRACT.md
...
```

Use a **fresh Codex conversation/session per phase**. This reduces stale assumptions and token waste.

Do not paste all project files into the prompt. Let Codex read the specific repository files it needs.

---

# 2. Authority order

When implementation details conflict, use this order:

1. **Official Rootcode Tech-Triathlon 2026 Challenge Booklet**.
2. **Official supplied competition files/templates/checker**.
3. `WAYLOOM_DATATHON_MASTER_PLAN.md`.
4. Approved phase contracts (`PHASE_00...PHASE_XX`).
5. Existing tested production code from completed phases.
6. This Codex handoff guide.
7. New engineering assumptions.

Never silently replace an official rule with a convenient implementation assumption.

If a requirement is not supported by the official material, describe it as a **WayLoom engineering decision**.

---

# 3. Current project state Codex must inherit

## Completed phases

```text
Phase 00  Competition understanding and scope freeze
Phase 01  Secure environment/repository setup
Phase 02  Raw dataset inventory
Phase 03  Data-quality audit
Phase 04  Task 1 training-data and label construction
Phase 05  Task 1 EDA
Phase 06  Task 1 feature engineering
Phase 07  Task 1 validation design
Phase 08  Task 1 baselines
Phase 09  Task 1 advanced modelling/model freeze
Phase 10  Task 1 final training and inference
```

## Task 1 frozen milestone

The project has already revalidated Task 1 successfully.

Treat the following as frozen unless a later official/global validation phase identifies a real defect:

```text
configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv
```

Task 1 final revalidation status supplied by the operator:

```text
TASK 01 FINAL VALIDATION : PASS
TASK 01 OUTPUT READY     : YES
```

Do not reopen Task 1 model search while implementing Task 2A/Task 2B.

Do not modify Task 1 predictions merely because later code refactoring makes a different output look plausible.

---

# 4. Core official competition contracts Codex must know

## 4.1 Task 1 — already complete, keep frozen

Output:

```text
submission_task1.csv
```

Required predictions:

```text
pred_service_min
pred_late_prob
```

Historical labels:

```text
service_start = max(actual arrival, window opening)
service_minutes = leave_outlet_time - service_start
late_flag = 1 only when actual arrival > window_close_time
```

Arrival exactly at closing time is **not late**.

Training-only actual route fields must not become prediction-time features:

```text
actual_depart_time
actual_travel_duration_min
arrival_time
leave_outlet_time
```

Task 1 has already passed its final output checks. Do not redesign it during Phases 11–28.

---

## 4.2 Task 2A — demand forecasting

Task 2A forecasts a **10-week future horizon** for the supplied depot/brand/week rows.

Output columns:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

Demand history must use **both**:

```text
deliveries_train.csv
task1_test_inputs.csv
```

Every unique requested order must count once in demand history, including:

```text
attempted
deferred
not_run
```

Use requested:

```text
order_date
```

not later dispatch date.

Join the official calendar and use official:

```text
iso_year
iso_week
```

Chilled-demand logic:

```text
Fresh → chilled demand may be > 0
Style → chilled demand exactly 0
Tech  → chilled demand exactly 0
```

Preserve the official Task 2A `row_id` and exact template ordering.

Task 2A is forecasting **volume**, not fleet or driver counts.

---

## 4.3 Task 2B — peak-day allocation scenario S1

Task 2B is a **constraint allocation problem**, not necessarily a trained ML model.

Scenario:

```text
S1
Peliyagoda
festival one week away
Fresh demand rising
not payday
no monsoon
some vehicles in workshop
```

Use:

```text
order_ref
```

as the peak-day order key.

Only available vehicles may be assigned.

A served order receives a vehicle and trip `1` or `2`.

A deferred order has blank vehicle/trip assignment fields as required by the template.

Core official feasibility rules:

1. Orders sharing a vehicle+trip must have the same brand and district.
2. Chilled demand requires reefer capability; reefers may carry ambient demand.
3. `van_only` demand requires a van.
4. Vehicle home depot must match the scenario depot.
5. An order is whole; do not split it across vehicles/trips.
6. Both weight and volume capacity must be respected.
7. Maximum two trips per vehicle. Fresh combined trip duration must respect the Fresh limit; Style/Tech combined duration must respect their limit.

The working limits established from the official brief are:

```text
Fresh combined <= 270 minutes
Style + Tech combined <= 480 minutes
```

Trip duration calculation:

```text
depot_to_district_freeflow_min
+ inter_stop_freeflow_min * (num_orders - 1)
+ sum(service_allowance_min)
```

Do **not** add a return journey unless the official rules explicitly change.

Do not import unrelated Hackathon fuel/window constraints into Task 2B.

The official checker proves feasibility, not optimality.

---

# 5. Competition-data safety boundary

The competition rules restrict sharing/distributing/transmitting the supplied datasets and derivatives to third parties.

Therefore Codex must treat the following as restricted:

```text
data/raw/**
data/interim/**
reports/private/**
```

## Codex may freely access

```text
src/**
tests/**
scripts/**
configs/**
docs/**
notebook source/structure
requirements files
tracked synthetic fixtures
tracked safe aggregate metadata
phase contracts
master plan
Git history/status/diffs
```

## Codex must not inspect

```text
real official competition rows
raw CSV content
private row-level labels
private row-level model predictions
private private-report contents
```

## Execution split

Codex should:

1. implement code;
2. build synthetic fixtures;
3. run safe unit/integration tests;
4. debug safe test failures;
5. run static/dependency/Git checks;
6. print the exact real-data command for the operator.

The human operator should:

1. run real competition-data commands locally;
2. inspect private reports locally;
3. give Codex only a sanitized PASS/FAIL summary when review is needed.

Do not weaken this boundary just because Codex runs inside VS Code.

---

# 6. Codex repository behavior

## 6.1 Use `AGENTS.md`

Codex automatically reads repository `AGENTS.md` instructions. Keep `AGENTS.md` compact and stable.

Do not put the entire master plan into `AGENTS.md`; doing so wastes context on every turn.

Use `AGENTS.md` for rules that apply to **every** phase:

- source authority;
- private-data boundary;
- no silent cross-phase redesign;
- safe autonomous testing/debugging;
- Git discipline;
- phase stop rules.

Keep the detailed task list in the current `PHASE_XX_COMPETITION_CONTRACT.md`.

## 6.2 Read only context relevant to the phase

At Phase 11, Codex should not repeatedly reread 10 giant contracts if only a few are relevant.

Use this pattern:

```text
Always read:
- AGENTS.md
- CODEX_HANDOFF_PHASE_11_ONWARDS.md
- WAYLOOM_DATATHON_MASTER_PLAN.md phase section
- current PHASE_XX_COMPETITION_CONTRACT.md

Read earlier contracts only when the current task depends on them.
```

Examples:

```text
Phase 11 → Phase 02, Phase 03, relevant official data definitions
Phase 13 → Phase 11 + Phase 12
Phase 14 → Phase 11–13
Phase 16 → Phase 14–15
Phase 17 → Phase 16 + official Task 2A template
Phase 19 → Phase 18 + official Task 2B rules
Phase 22 → Phase 18–21
Phase 23 → Phase 18–22 + official checker contract
Phase 31 → final artifacts from Task 1, 2A, 2B + docs
Phase 39 → release/reproduction contracts only
```

This is intentionally token-efficient.

---

# 7. Codex autonomous development policy

Codex has broad autonomy for safe engineering.

It MAY:

- create/edit/refactor phase-relevant code;
- add tests;
- add synthetic fixtures;
- run `pytest`;
- run targeted tests repeatedly;
- run the complete safe test suite;
- inspect traceback/stack traces;
- fix ordinary bugs automatically;
- run `python -m pip check`;
- inspect Git status/diff;
- inspect tracked configuration and documentation;
- self-review against phase Definition of Done.

Codex should **not stop for ordinary coding failures** it can safely repair.

Codex MUST stop for:

- official-rule ambiguity;
- required access to restricted row-level competition data;
- a contradiction with a frozen earlier phase;
- unresolved leakage/future-information issue;
- a request to change a frozen model/validation contract after seeing private results;
- a genuine schema/data-quality blocker;
- a solver/forecast design change that materially changes the approved phase contract;
- any violation of competition AI/data restrictions.

---

# 8. Token-efficient Codex workflow

Use this workflow to conserve credits/tokens.

## Before implementation

Codex should use targeted file discovery:

```text
rg / grep
small file excerpts
specific symbols/functions
current phase contract
```

Avoid asking it to summarize the entire repository on every turn.

## During implementation

Use:

```text
small logical batches
focused tests
concise status updates
```

Do not ask for long explanations of code that already passes tests.

## At phase end

Request one compact report:

```text
TASK STATUS
FILES CHANGED
TESTS
DATA-SAFETY STATUS
STOP CONDITIONS
LOCAL COMMAND
READY FOR REVIEW
```

## Fresh review session

Use a separate Codex session for independent review rather than continuing a huge implementation conversation.

---

# 9. When to use an ExecPlan

Use a short execution plan for high-risk or multi-hour phases only.

Recommended ExecPlan phases:

```text
11  demand-history construction
13  forecasting features
14  forecast validation
16  advanced forecasting
17  final Task 2A inference
19  compatibility engine
20  trip engine
22  optimizer
23  independent validator
31  final notebook
33  final submission tests
39  clean reproduction
41  final competition validation
42  packaging/submission verification
```

For simple documentation/reporting phases, a full ExecPlan is unnecessary and increases token use.

---

# 10. Phase-by-phase execution style from the finalized master plan

| Phase | Tasks | Phase | Recommended execution style |
|---:|---|---|---|
| 11 | DT-174–191 | Task 2A demand-history construction | Task/small-batch; data logic is high risk |
| 12 | DT-192–203 | Task 2A exploratory analysis | Full-phase tooling |
| 13 | DT-204–221 | Task 2A forecasting features | Hybrid; leakage-sensitive feature batches |
| 14 | DT-222–227 | Task 2A forecast validation | Critical task/small-batch |
| 15 | DT-228–233 | Task 2A baseline models | Full phase |
| 16 | DT-234–241 | Task 2A advanced forecasting | Hybrid model experiment phase |
| 17 | DT-242–253 | Task 2A final inference | Critical task/small-batch |
| 18 | DT-254–270 | Task 2B scenario understanding | Full phase |
| 19 | DT-271–283 | Task 2B compatibility engine | Task/small-batch |
| 20 | DT-284–292 | Task 2B trip calculation engine | Task/small-batch |
| 21 | DT-293–298 | Task 2B priority-policy design | Full phase |
| 22 | DT-299–319 | Task 2B optimization solver | Task/small-batch; solver-critical |
| 23 | DT-320–330 | Task 2B independent validator | Task/small-batch; independently gate each rule |
| 24 | DT-331–342 | Task 2B output and written policy | Hybrid |
| 25 | DT-343–349 | Explainability | Full phase |
| 26 | DT-350–357 | Explainable Deferral Reasoner | Task/small-batch |
| 27 | DT-358–361 | Optional forecast uncertainty | Full phase / optional |
| 28 | DT-362–373 | Optional WayLoom integration contract | Hybrid / optional |
| 29 | DT-374–378 | Architecture documentation | Full phase |
| 30 | DT-379–388 | Preprocessing document | Full phase |
| 31 | DT-389–411 | Final competition notebook | Task/small-batch; high integration risk |
| 32 | DT-412–419 | Model artifact management | Full phase |
| 33 | DT-420–437 | Final submission-file testing | Full phase but critical gates |
| 34 | DT-438–450 | General automated testing | Hybrid |
| 35 | DT-451–455 | AI-use disclosure | Full phase |
| 36 | DT-456–463 | README / project documentation | Full phase |
| 37 | DT-464–474 | Results summary and evidence | Full phase |
| 38 | DT-475–491 | Demo video preparation | Full phase |
| 39 | DT-492–501 | Clean-environment reproduction | Task/small-batch; environment-critical |
| 40 | DT-502–515 | Final competition folder | Full phase |
| 41 | DT-516–527 | Final competition validation | Critical task/small-batch |
| 42 | DT-528–539 | Packaging and submission | Task/small-batch + human upload |

---

# 11. Current Codex model strategy — capability vs token usage

The model names below reflect the Codex model family available in late 2026. Actual availability depends on the user's plan/workspace.

Use this hierarchy:

```text
GPT-5.6 Luna
→ cheapest/fastest option for focused and repetitive work

GPT-5.6 Terra
→ default balanced model for routine implementation and analysis

GPT-5.6 Sol
→ use for high-risk coding/reasoning and cross-file logic

GPT-6 Astra
→ reserve for the hardest solver/debug/reproduction problems
```

## Token-saving rule

Start with the **Low-token model** shown below.

Escalate only when:

- two serious implementation attempts fail;
- the phase contains a critical leakage/validation/solver invariant;
- the bug spans multiple subsystems;
- the low-token model cannot produce a convincing passing test.

For most phases, do **not** start with Astra.

---

# 12. Recommended Codex model for every remaining phase

| Phase | Work | Low-token/default choice | Reasoning | Best-quality escalation | Why |
|---:|---|---|---|---|---|
| 11 | Demand-history construction | **GPT-5.6 Terra** | Medium | **GPT-5.6 Sol** High | Deduplication/order-date/weekly aggregation are correctness-critical |
| 12 | Task 2A EDA | **GPT-5.6 Luna** | Medium | **GPT-5.6 Terra** Medium | Mostly repetitive summaries/plots |
| 13 | Forecast features | **GPT-5.6 Terra** | High | **GPT-5.6 Sol** High | Lag/rolling/horizon leakage risk |
| 14 | Forecast validation | **GPT-5.6 Sol** | High | **GPT-6 Astra** | Rolling-origin leakage is competition-critical |
| 15 | Forecast baselines | **GPT-5.6 Terra** | Medium | **GPT-5.6 Sol** Medium | Straightforward baseline implementation |
| 16 | Advanced forecasting | **GPT-5.6 Sol** | High | **GPT-6 Astra** | Model comparison/ensembling/config freeze |
| 17 | Task 2A final inference | **GPT-5.6 Terra** | High | **GPT-5.6 Sol** High | Exact template/order/business invariants matter more than creativity |
| 18 | Task 2B scenario understanding | **GPT-5.6 Terra** | Medium | **GPT-5.6 Sol** Medium | Rule parsing and data contracts |
| 19 | Compatibility engine | **GPT-5.6 Terra** | High | **GPT-5.6 Sol** High | Multiple hard feasibility rules |
| 20 | Trip calculation engine | **GPT-5.6 Terra** | High | **GPT-5.6 Sol** High | Formula/boundary correctness |
| 21 | Priority policy | **GPT-5.6 Luna** | Medium | **GPT-5.6 Terra** Medium | Mostly transparent business logic/documentation |
| 22 | Optimization solver | **GPT-5.6 Sol** | High | **GPT-6 Astra** | CP-SAT/constraint debugging is the hardest Task 2B coding phase |
| 23 | Independent validator | **GPT-5.6 Sol** | High | **GPT-6 Astra** | Must independently catch optimizer mistakes |
| 24 | Task 2B output/policy | **GPT-5.6 Terra** | Medium | **GPT-5.6 Sol** Medium | Template + written policy integration |
| 25 | Explainability | **GPT-5.6 Luna** | Medium | **GPT-5.6 Terra** Medium | Mostly summaries and explanations |
| 26 | Deferral Reasoner | **GPT-5.6 Terra** | High | **GPT-5.6 Sol** High | Cross-rule explanations need correctness |
| 27 | Forecast uncertainty | **GPT-5.6 Terra** | Medium | **GPT-5.6 Sol** High | Optional statistical logic |
| 28 | WayLoom integration contract | **GPT-5.6 Terra** | Medium | **GPT-5.6 Sol** Medium | Interfaces/contracts rather than core scoring |
| 29 | Architecture documentation | **GPT-5.6 Luna** | Medium | **GPT-5.6 Terra** Medium | Document generation from existing code |
| 30 | Preprocessing document | **GPT-5.6 Luna** | Medium | **GPT-5.6 Terra** Medium | Source-grounded documentation |
| 31 | Final notebook | **GPT-5.6 Sol** | High | **GPT-6 Astra** | Many components must run end-to-end correctly |
| 32 | Model artifacts | **GPT-5.6 Terra** | Medium | **GPT-5.6 Sol** Medium | Serialization/manifest work |
| 33 | Final submission testing | **GPT-5.6 Sol** | High | **GPT-6 Astra** | One wrong validation can invalidate submission |
| 34 | Automated tests | **GPT-5.6 Terra** | High | **GPT-5.6 Sol** High | Repetitive coding but broad coverage |
| 35 | AI disclosure | **GPT-5.6 Luna** | Low/Medium | **GPT-5.6 Terra** Medium | Documentation, no complex code |
| 36 | README | **GPT-5.6 Luna** | Low/Medium | **GPT-5.6 Terra** Medium | Documentation |
| 37 | Results/evidence | **GPT-5.6 Terra** | Medium | **GPT-5.6 Sol** Medium | Needs careful metric consistency |
| 38 | Demo preparation | **GPT-5.6 Luna** | Medium | **GPT-5.6 Terra** Medium | Script/storyboard/checklist work |
| 39 | Clean reproduction | **GPT-5.6 Sol** | High | **GPT-6 Astra** | Environment/path/version bugs can be difficult |
| 40 | Final folder | **GPT-5.6 Luna** | Medium | **GPT-5.6 Terra** Medium | Mostly deterministic packaging checks |
| 41 | Final validation | **GPT-5.6 Sol** | High | **GPT-6 Astra** | Last critical compliance gate |
| 42 | Packaging/submission | **GPT-5.6 Luna** | Medium | **GPT-5.6 Terra** Medium | File/ZIP verification; upload remains human-controlled |

## If only one model is available

Use it, but adjust reasoning effort:

```text
routine docs/tests      → Low/Medium
normal implementation  → Medium
leakage/validation      → High
solver/reproduction     → High/XHigh if available
```

---

# 13. Context-size strategy for Codex

Large prompts waste allowance. Use references instead of copying files.

Good phase prompt:

```text
Read AGENTS.md, CODEX_HANDOFF_PHASE_11_ONWARDS.md,
WAYLOOM_DATATHON_MASTER_PLAN.md Phase 11,
PHASE_11_COMPETITION_CONTRACT.md,
and only earlier files explicitly required by that contract.
```

Avoid:

```text
Read every file in the repository and summarize everything first.
```

For a specific bug, point directly to:

```text
file
function
failing test
expected invariant
```

---

# 14. Git workflow from Phase 11 onward

Use one branch per phase:

```text
feature/phase-11-task2a-history
feature/phase-12-task2a-eda
...
```

Before edits:

```bash
git status
```

Before committing:

```bash
git diff
git diff --cached --name-only
```

Never commit:

```text
data/raw/**
data/interim/**
reports/private/**
local credentials
API keys
private temporary outputs
```

At phase end:

```bash
pytest -q
python -m pip check
git status
```

If full `pytest -q` contains a deliberately private-data-only integration test, exclude only the documented test and state why.

---

# 15. Testing policy

## Codex tests

Codex runs:

```text
synthetic unit tests
synthetic integration tests
schema tests
leakage tests
constraint tests
serialization tests
regression tests
```

Codex should automatically debug normal failures.

## Human/local tests

The human runs any command that directly consumes official private competition rows.

The command should print only sanitized status such as:

```text
LOCAL PHASE 11 HISTORY BUILD: PASS
UNIQUE ORDER INTEGRITY: PASS
MISSING OFFICIAL WEEKS: 0
STYLE CHILLED NONZERO: 0
TECH CHILLED NONZERO: 0
```

Avoid pasting exact private aggregates into Codex unless competition rules and data-handling configuration explicitly permit it.

---

# 16. Phase completion contract

Every phase should end with two stages.

## Stage A — implementation

Codex returns:

```text
PHASE XX — IMPLEMENTATION

TASK STATUS
FILES CREATED/MODIFIED
TARGETED TESTS
FULL SAFE TEST SUITE
PIP CHECK
DATA-SAFETY STATUS
LOCAL COMMAND REQUIRED
READY FOR LOCAL RUN: YES/NO
```

## Stage B — independent review

Start a fresh Codex session.

Review:

```text
phase contract
diff/source code
synthetic tests
sanitized local-run status
Git safety
Definition of Done
```

Reviewer must not automatically fix first. It reports blockers first.

Only after review passes:

```text
PHASE XX STATUS: PASS
READY FOR PHASE XX+1: YES
```

---

# 17. Generic Codex phase implementation prompt template

Copy this for every phase and replace placeholders.

```text
You are implementing WayLoom Datathon PHASE <XX> only.

PHASE:
<PHASE NAME>

TASK RANGE:
<DT-AAA> through <DT-BBB>

Read:
1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase <XX> section
4. PHASE_<XX>_COMPETITION_CONTRACT.md
5. only earlier contracts/source files explicitly required by the current phase

Do not start the next phase.

Follow this authority:
Official Challenge Booklet / official artifacts
>
WayLoom master plan
>
approved phase contracts
>
engineering assumptions

DATA SAFETY:
Do not inspect data/raw/**, data/interim/**, or reports/private/**.
Use synthetic fixtures for agent-run tests.
The human will run private-data commands locally.

AUTONOMY:
You may create/edit/refactor all phase-relevant tracked code, configs, docs,
and tests. Run tests, inspect failures, fix ordinary bugs, rerun tests, run
python -m pip check, and inspect git status/diff without asking for approval.

Do not stop for normal coding failures you can safely fix.

STOP for:
- official-rule ambiguity
- need for restricted row-level competition data
- conflict with a frozen prior phase
- unresolved leakage/future-information issue
- material contract change
- genuine schema/data blocker

IMPLEMENT:
Every task in PHASE_<XX>_COMPETITION_CONTRACT.md.
Do not skip optional-status handling required by the contract.

TEST:
Run targeted tests after each critical batch.
Then run the complete safe regression suite.

GIT:
Do not stage restricted data/private reports.

RETURN:
PHASE <XX> — AGENT IMPLEMENTATION STAGE

TASK STATUS:
<one line per DT task>

FILES CREATED:
...

FILES MODIFIED:
...

TESTS:
...

STOP CONDITIONS:
CLEAR / BLOCKED

PRIVATE DATA ACCESSED:
MUST BE NO

HUMAN LOCAL ACTION REQUIRED:
YES / NO

If YES, print the exact local command.

PHASE <XX> STATUS:
AWAITING LOCAL RUN / READY FOR REVIEW / BLOCKED

READY FOR NEXT PHASE:
NO

Then STOP.
```

---

# 18. Generic independent review prompt

```text
Perform an independent review of WayLoom Datathon Phase <XX>.

Read:
- AGENTS.md
- CODEX_HANDOFF_PHASE_11_ONWARDS.md
- WAYLOOM_DATATHON_MASTER_PLAN.md Phase <XX>
- PHASE_<XX>_COMPETITION_CONTRACT.md
- files changed for this phase
- tests changed for this phase
- relevant prior frozen contracts

Do NOT access:
- data/raw/**
- data/interim/**
- reports/private/**

Do not modify code initially.
Do not start the next phase.

Use the human-supplied sanitized local result:
<PASTE SANITIZED STATUS ONLY>

Audit every DT task against the contract.
Audit:
- official-rule compliance
- train/test or forecast-time leakage
- schema/key correctness
- deterministic behavior
- edge cases
- test coverage
- Git/data safety
- Definition of Done

Run safe tests only.

Return:
| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:
OFFICIAL CONTRACT: PASS/FAIL
DATA SAFETY: PASS/FAIL
LEAKAGE/FUTURE INFO: PASS/FAIL/N/A
TESTS: PASS/FAIL
LOCAL RUN: PASS/FAIL
BLOCKERS: ...
NON-BLOCKING IMPROVEMENTS: ...
PHASE <XX> REVIEW: PASS/FAIL
READY FOR NEXT PHASE: YES/NO

If FAIL, list exact blockers only.
Do not fix automatically.
```

---

# 19. First Codex handoff/bootstrap prompt

Use this once when moving from Cursor to Codex.

```text
You are taking over the WayLoom Datathon repository from an earlier
Cursor-based development workflow.

This is a HANDOFF REVIEW ONLY.
Do not implement Phase 11 yet.
Do not modify production code.
Do not access private competition rows.

Read:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
4. PHASE_00_COMPETITION_CONTRACT.md through PHASE_10_COMPETITION_CONTRACT.md

Important: use targeted reading. You do not need to repeat every line of
every phase contract back to me. Extract the frozen contracts, repository
interfaces and dependencies needed for Phase 11 onward.

Do NOT access:

data/raw/**
data/interim/**
reports/private/**

Current operator-confirmed state:

- Phases 00–10 completed.
- Task 1 final model configuration is frozen.
- Saved Task 1 service/late models exist.
- outputs/submission_task1.csv passed final revalidation.
- TASK 01 FINAL VALIDATION = PASS.
- TASK 01 OUTPUT READY = YES.

Perform these checks using tracked/safe files only:

1. Confirm the master-plan task ranges and remaining phases 11–42.
2. Identify the repository modules Phase 11 can reuse.
3. Identify frozen Task 1 files that Phase 11 must not alter.
4. Confirm Git working-tree status.
5. Confirm restricted paths are ignored/not intended for agent inspection.
6. Identify requirements/test commands available for future phases.
7. Identify any stale Cursor-specific instruction that should be treated as
   historical rather than authoritative for Codex.
8. Confirm readiness to receive PHASE_11_COMPETITION_CONTRACT.md.

Do not run real-data commands.
Do not retrain models.
Do not regenerate Task 1 output.
Do not create Phase 11 code.

Return only:

WAYLOOM CODEX HANDOFF REVIEW

MASTER PLAN: PASS/FAIL
PHASE 00–10 CONTRACTS FOUND: PASS/FAIL
TASK 1 FROZEN STATE UNDERSTOOD: PASS/FAIL
RESTRICTED DATA BOUNDARY UNDERSTOOD: PASS/FAIL
REUSABLE INFRASTRUCTURE IDENTIFIED: PASS/FAIL
GIT SAFETY: PASS/FAIL
SAFE TEST COMMANDS IDENTIFIED: PASS/FAIL
PHASES 11–42 TASK RANGES VERIFIED: PASS/FAIL

FROZEN TASK 1 FILES:
...

REUSABLE MODULES FOR PHASE 11+:
...

BLOCKERS BEFORE PHASE 11:
...

READY FOR PHASE 11 CONTRACT:
YES/NO

Then STOP.
```

---

# 20. Phase 11-specific handoff notes

Phase 11 starts a **new competition task**. Do not copy Task 1 modelling assumptions into it.

Phase 11 tasks are:

```text
DT-174 Load deliveries_train.csv
DT-175 Load task1_test_inputs.csv
DT-176 Append both demand datasets
DT-177 Verify delivery_id uniqueness after combination
DT-178 Keep attempted orders
DT-179 Keep deferred orders
DT-180 Keep not_run orders
DT-181 Use requested order_date
DT-182 Join calendar.csv
DT-183 Add ISO year
DT-184 Add ISO week
DT-185 Aggregate total demand
DT-186 Aggregate Fresh chilled demand separately
DT-187 Force Style chilled history logically to zero
DT-188 Force Tech chilled history logically to zero
DT-189 Build complete weekly panel
DT-190 Investigate missing weeks
DT-191 Validate weekly totals
```

The most dangerous Phase 11 mistakes are:

```text
counting only attempted deliveries
excluding deferred/not_run requested demand
using dispatch_date instead of order_date
double-counting orders present across sources
wrong ISO week/year handling
aggregating chilled volume for Style/Tech
silently dropping missing weeks
```

These must become explicit tests in the Phase 11 contract.

---

# 21. Later critical gates Codex must anticipate

## Task 2A

```text
Phase 11  demand-history correctness
Phase 13  lag/rolling leakage
Phase 14  rolling-origin validation
Phase 16  advanced model must justify itself against baselines
Phase 17  exact final template and business invariants
```

## Task 2B

```text
Phase 19  compatibility rules
Phase 20  trip-duration formula
Phase 22  optimization constraints
Phase 23  independent validator/checker
Phase 24  exact submission + one-page policy
```

## Final submission

```text
Phase 31  final notebook must load saved models
Phase 33  all submission files hard-tested
Phase 39  clean environment reproduction
Phase 41  final line-by-line audit
Phase 42  ZIP/extract/upload evidence
```

---

# 22. Human-control tasks

The human remains responsible for:

- executing restricted-data commands locally;
- interpreting private competition metrics;
- deciding whether optional work is worth the time;
- recording the demo video;
- creating/uploading the unlisted YouTube video;
- manually submitting the final ZIP;
- keeping submission confirmation/evidence;
- deciding not to modify the frozen final package after submission.

Codex should never claim an external upload/submission succeeded unless the human confirms it.

---

# 23. Global stop conditions from Phase 11 onward

Stop downstream work if any of these occurs:

- official requirement is unclear or contradicted;
- raw/private competition content is exposed to the agent;
- a phase mutates a frozen earlier output without explicit justification;
- Task 2A history excludes valid requested demand;
- Task 2A features leak future actual demand;
- forecast validation uses future data;
- Task 2B solver violates a feasibility rule;
- optimizer and independent validator disagree;
- official checker fails;
- final notebook cannot run from a clean kernel;
- a saved model cannot reload;
- final CSV template/ID/order validation fails;
- clean-environment reproduction fails;
- final folder contains raw competition data or secrets;
- ZIP extraction/revalidation fails.

---

# 24. Handoff Definition of Done

Codex handoff is complete when:

- [ ] `AGENTS.md` exists at repository root.
- [ ] this guide is available to Codex.
- [ ] Codex confirms Phase 00–10 contracts are understood.
- [ ] Codex understands Task 1 is frozen and already validated.
- [ ] Codex understands the competition-data safety boundary.
- [ ] Codex verifies remaining task range DT-174 → DT-539.
- [ ] Codex is ready to consume `PHASE_11_COMPETITION_CONTRACT.md`.
- [ ] no production code is changed during the handoff review.
- [ ] no real competition data is inspected during the handoff review.

Then begin Phase 11 in a fresh Codex session.

---

# 25. Short operator workflow

Use this every time:

```text
1. Ask ChatGPT for PHASE_XX_COMPETITION_CONTRACT.md
2. Save it to repo root
3. Open a fresh Codex session
4. Choose the low-token model from the table above
5. Give Codex the phase implementation prompt
6. Let Codex code + test + debug safely
7. Run the private-data command yourself if required
8. Give Codex only sanitized PASS/FAIL
9. Open a fresh Codex review session
10. Run independent review prompt
11. Merge only after PASS
12. Move to the next phase
```

This is the default WayLoom development workflow from Phase 11 through Phase 42.
