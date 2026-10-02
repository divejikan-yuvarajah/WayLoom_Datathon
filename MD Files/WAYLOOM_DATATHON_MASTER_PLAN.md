# WAYLOOM DATATHON MASTER PLAN

> **Central source of truth for the WayLoom Datathon workstream — Rootcode Tech-Triathlon 2026**
>
> **Status:** Active working plan  
> **Competition deadline:** 9 October 2026, 11:59 PM Sri Lanka time  
> **Scope:** Datathon only, with optional non-blocking integration contracts for Designathon/Hackathon  
> **Task registry:** DT-000 through DT-539 — complete and sequential

---

## 1. Purpose of this file

This file is the **single master control document** for the WayLoom Datathon. It defines the complete development sequence from competition-rule analysis through final submission. It is intentionally broader than any individual phase guide.

Use this file to:

- see every required and proposed development task in one place;
- track status using checkboxes;
- distinguish organizer requirements from our engineering choices and optional competitive enhancements;
- enforce phase dependencies and stop conditions;
- prevent accidental scope drift;
- coordinate future phase-specific `.md` implementation guides;
- keep the Datathon independent from the Hackathon while exposing optional integration contracts;
- ensure the final submission is reproducible, auditable and competition-compliant.

**Rule:** if a future phase document, coding-agent suggestion, notebook experiment or implementation conflicts with an explicit official competition rule, the official rule wins. If two internal documents conflict, this master plan controls until it is deliberately updated.

---

## 2. Source hierarchy

1. **Official Rootcode Tech-Triathlon 2026 Challenge Booklet** — highest authority.
2. **Official supplied datasets, submission templates and `check_allocation.py`** — executable/data-level authority.
3. **WayLoom Product & Competition Master Plan** — internal cross-phase interpretation and team agreement.
4. **This Datathon Master Plan** — Datathon execution source of truth.
5. **Future phase/task `.md` files** — implementation-level instructions; they may add detail but must not silently change this master plan.
6. **Notebooks, code comments, prompts and experiments** — lowest authority unless promoted into documentation.

---

## 3. Marking legend

| Mark | Meaning | How to treat it |
|---|---|---|
| **[O] Official** | Explicit organizer requirement, rule, output, restriction or required deliverable. | Non-negotiable unless the organizer clarifies otherwise. |
| **[E] Engineering** | WayLoom implementation/reliability recommendation needed to execute the official task safely. | Strong default; change only with documented reason. |
| **[C] Competitive** | Optional enhancement intended to improve differentiation, explainability or presentation. | Never allow it to delay a P0 official deliverable. |

### Priority legend

| Priority | Meaning |
|---|---|
| **P0** | Essential for correctness, compliance or a valid submission. Must be completed. |
| **P1** | High-impact engineering/model quality work. Complete after P0 is stable. |
| **P2** | Competitive enhancement. Implement only when P0/P1 are healthy. |
| **P3** | Experimental/optional. First items to cut under time pressure. |

### Status convention

- `[ ]` Not started
- `[~]` In progress — use manually if your Markdown viewer supports it; otherwise keep `[ ]` and add `(IN PROGRESS)`
- `[x]` Completed and verified
- `[!]` Blocked — write the blocking issue beside the task

A task is **not** complete merely because code exists. Mark `[x]` only after its Definition of Done and required tests/checks are satisfied in the corresponding phase guide.

---

## 4. Non-negotiable competition contract

### Task 1 — service time and lateness

- Predict `pred_service_min` and `pred_late_prob` for every official Task 1 `delivery_id`.
- Construct labels from historical actual route records; labels are not provided directly.
- `service_start = max(actual arrival, window open)`.
- `service_min = leave_outlet_time - service_start`.
- `late_flag = 1` only when actual arrival is strictly after `window_close_time`.
- At test/prediction time, do not use actual future journey/handling fields.
- Preserve the supplied Task 1 `delivery_id` values and original row order.

### Task 2A — ten-week demand forecast

- Build demand history from **both** `deliveries_train.csv` and `task1_test_inputs.csv`.
- Count every unique order once, including `deferred` and `not_run` orders.
- Assign demand to the store-requested `order_date`, not later `dispatch_date`.
- Use `calendar.csv` ISO year/week.
- Predict `pred_total_volume_m3` and `pred_chilled_volume_m3` for the exact template rows.
- Only Fresh has chilled demand; Style and Tech chilled predictions must be exactly `0`.

### Task 2B — peak-day allocation

- Scenario is `S1`, Peliyagoda.
- Use only scenario vehicles marked `available`; workshop vehicles are forbidden.
- Use `order_ref` as the allocation key.
- Every order must be `served` or `deferred`; served orders receive one vehicle and trip 1 or 2; deferred rows leave vehicle/trip blank.
- Enforce all seven official feasibility rules: same brand+district per trip; chilled→reefer; van_only→van; home depot; whole order; weight+volume capacity; max two trips and official time budgets.
- Trip minutes = outbound district free-flow + inter-stop free-flow × (`number_of_orders - 1`) + sum of brand+dock service allowances.
- Do **not** add a separate return-to-depot leg.
- Fresh minutes per vehicle ≤ 270; combined Style+Tech minutes per vehicle ≤ 480; max two trips total.
- `check_allocation.py` verifies feasibility, not prioritization quality or optimality.

### Datathon submission restrictions and deliverables

- No prohibited pretrained models; no proprietary API-based modelling/preprocessing; no low-code/no-code end-to-end modelling tools.
- Keep official competition datasets and restricted derivatives private; do not publish or distribute them.
- Submit saved final model files, architecture diagrams, preprocessing document, final notebook, three official submission CSVs, Task 2B prioritization policy, AI-tool disclosure and an unlisted 3–5 minute demo video.
- Final notebook must retain label/preprocessing/training/evaluation work and include a final section/cell that **loads saved models** and demonstrates Task 1 and Task 2A inference with clearly printed inputs and predictions.
- Final package naming: `TeamName_Datathon.zip`.

---

## 5. Repository structure

```text
WayLoom_Datathon/
│
├── README.md
├── WAYLOOM_DATATHON_MASTER_PLAN.md
├── TeamName_FinalNotebook.ipynb
├── requirements.txt
├── .gitignore
│
├── configs/
│   ├── paths.yaml
│   └── model_config.yaml
│
├── data/
│   ├── README.md
│   ├── raw/                  # PRIVATE / NEVER COMMIT
│   ├── interim/              # PRIVATE DERIVATIVES / NEVER PUBLIC
│   └── processed/            # PRIVATE DERIVATIVES / NEVER PUBLIC
│
├── docs/
│   ├── 00_MASTER_INDEX.md
│   ├── competition_contract.md
│   ├── preprocessing.md
│   ├── task2b_policy.md
│   ├── ai_tool_disclosure.md
│   ├── integration_contract.md       # optional
│   ├── architecture/
│   └── phases/
│       ├── PHASE_00_COMPETITION_CONTRACT.md
│       ├── PHASE_01_PROJECT_ENVIRONMENT.md
│       └── ...
│
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_task1_labels_eda.ipynb
│   ├── 03_task1_modeling.ipynb
│   ├── 04_task2a_forecasting.ipynb
│   └── 05_task2b_analysis.ipynb
│
├── src/
│   ├── common/
│   │   ├── io.py
│   │   ├── validation.py
│   │   └── time_utils.py
│   ├── task1/
│   │   ├── labels.py
│   │   ├── features.py
│   │   ├── train_service.py
│   │   ├── train_late.py
│   │   └── inference.py
│   ├── task2a/
│   │   ├── aggregate.py
│   │   ├── features.py
│   │   ├── forecast.py
│   │   └── inference.py
│   └── task2b/
│       ├── compatibility.py
│       ├── trip_time.py
│       ├── optimizer.py
│       ├── validator.py
│       └── explain_deferral.py       # competitive enhancement
│
├── models/
│   ├── task1_service.*
│   ├── task1_late.*
│   └── task2a/
│
├── outputs/
│   ├── submission_task1.csv
│   ├── submission_task2a.csv
│   └── submission_task2b.csv
│
├── reports/
│   ├── figures/
│   ├── metrics/
│   └── checker/
│
└── tests/
    ├── test_schemas.py
    ├── test_task1_labels.py
    ├── test_task1_features.py
    ├── test_task2a_aggregation.py
    ├── test_task2b_constraints.py
    └── test_submission_files.py
```

Folder names may be adjusted to the actual repository, but data-safety boundaries and the logical separation of Task 1, Task 2A and Task 2B must remain clear.

---

## 6. Execution rules

1. **P0 before P1; P1 before P2/P3.** Optional work never blocks official outputs.
2. **Do not start modelling before label/data correctness is verified.** Task 1 modelling is blocked by DT-055–DT-071.
3. **Use time-aware validation.** Never use a random split that lets later operational information leak into earlier validation.
4. **Treat Task 1, Task 2A and Task 2B as different technical problems.** Shared utilities are fine; do not force one modelling pattern across them.
5. **Do not silently delete outliers.** Investigate them and document any cleaning decision.
6. **No test-label inference from future actuals.** Any feature unavailable before the delivery starts is forbidden for Task 1 prediction.
7. **Keep official templates immutable except answer columns.** Preserve identifiers and required order.
8. **Use the official Task 2B rules exactly.** Do not substitute wider Hackathon fuel/window logic into the Task 2B validator.
9. **Run an independent validator before the organizer checker.** Passing the checker does not prove a good policy.
10. **Notebook is evidence, not the only implementation.** Important reusable logic belongs in `src/` and is called from the final notebook where practical.
11. **Every final model must survive save/load.** Loaded-model predictions must reproduce the expected inference behavior.
12. **All AI usage must remain competition-compliant and disclosed.** Coding assistance must not become prohibited automated modelling or external data disclosure.
13. **Never expose official private data in a public WayLoom deployment.** Optional integration uses schemas and synthetic/demo records unless organizer authorization says otherwise.
14. **Freeze final artifacts before packaging.** After final validation, changes require re-running all affected checks.
15. **Keep an experiment/decision log.** Record why a model, feature or allocation policy was selected or rejected.

---

## 7. Git rules

Recommended branch pattern:

```text
main
├── feature/data-audit
├── feature/task1-labels
├── feature/task1-features
├── feature/task1-models
├── feature/task2a-forecast
├── feature/task2b-optimizer
├── feature/explainability
└── release/datathon-final
```

Recommended commits:

```text
feat(task1): implement official label construction
fix(task2b): enforce reefer compatibility
test(task2a): verify requested-week aggregation
refactor(task1): extract route feature builder
docs: add Task 2B prioritization policy
chore: freeze final submission artifacts
```

Before merging a phase branch:

- run the phase tests/checks;
- update task checkboxes in this master plan;
- update the phase completion report;
- record any decision that changes downstream assumptions;
- ensure no raw/restricted competition data was accidentally staged.

---

## 8. Future phase `.md` usage contract

A future phase document must be named clearly, for example:

```text
docs/phases/PHASE_04_TASK1_LABEL_CONSTRUCTION.md
```

Every phase file must include:

1. Phase goal and scope.
2. Official rules that apply.
3. Prerequisites and blocked downstream phases.
4. Every task ID from this master plan in that phase — **none may be omitted**.
5. For each task: objective, why it matters, inputs, outputs, files to create/modify, step-by-step implementation, edge cases, validation, tests, Definition of Done, common mistakes, Git guidance.
6. Explicit **STOP CONDITIONS**.
7. Ready-to-copy Cursor/Codex implementation prompt(s).
8. Separate review/audit prompt(s).
9. Phase completion report.
10. Final phase gate: `READY FOR NEXT PHASE = YES/NO`.

A phase file may split a task into subtasks, but it must not renumber or remove the master task ID. If new work is discovered, record it as a child item under an existing task or deliberately revise this master plan; do not create hidden side work.

### Phase execution rule

```text
Open phase MD
    ↓
Implement one task or tightly coupled task group
    ↓
Run its tests/validation
    ↓
Review result
    ↓
Update checkbox + decision log
    ↓
Proceed only if stop conditions are clear
```

Do **not** give Cursor/Codex an entire multi-week project and ask it to finish autonomously. Use phase/task prompts with explicit scope and stop-after-completion instructions.

---

## 9. Master phase order

```text
Competition Contract
→ Environment + Secure Repo
→ Dataset Inventory
→ Data Quality Audit
→ Task 1 Labels
→ Task 1 EDA
→ Task 1 Features
→ Task 1 Validation
→ Task 1 Baselines
→ Task 1 Advanced Models
→ Task 1 Final Inference
→ Task 2A Demand History
→ Task 2A EDA
→ Task 2A Features
→ Task 2A Validation
→ Task 2A Baselines
→ Task 2A Advanced Forecasting
→ Task 2A Final Inference
→ Task 2B Scenario Audit
→ Task 2B Compatibility
→ Task 2B Trip Engine
→ Task 2B Priority Policy
→ Task 2B Solver
→ Task 2B Independent + Official Validation
→ Task 2B Output + Written Policy
→ Explainability / Optional Differentiators
→ Architecture + Preprocessing Documentation
→ Final Notebook + Model Artifacts
→ Submission Tests + Automated Tests
→ AI Disclosure + README + Results Evidence
→ Demo
→ Clean Reproduction
→ Final Folder
→ Final Validation
→ ZIP + Submission
```

---

## 10. Master task registry

**Checkboxes below are the authoritative project-progress tracker.** Dependencies shown are minimum gates; the corresponding phase `.md` should refine them where necessary.


### Phase 00 — Competition understanding and scope freeze

**Phase dependency:** None  
**Default phase priority:** P0  
**Phase gate:** All official Datathon tasks, formulas, restrictions, outputs, judging criteria and deadline are documented without ambiguity.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-000** | [O] | P0 | None | Read the official Datathon rules |
| [ ] | **DT-001** | [O] | P0 | None | Create competition requirements checklist |
| [ ] | **DT-002** | [O] | P0 | None | Separate the three Datathon problems |
| [ ] | **DT-003** | [O] | P0 | None | Freeze Task 1 target definitions |
| [ ] | **DT-004** | [O] | P0 | None | Freeze Task 2A demand rules |
| [ ] | **DT-005** | [O] | P0 | None | Freeze Task 2B seven feasibility rules |
| [ ] | **DT-006** | [O] | P0 | None | Freeze Task 2B trip-time formula |
| [ ] | **DT-007** | [O] | P0 | None | Freeze official submission file structures |
| [ ] | **DT-008** | [O] | P0 | None | Record competition restrictions |
| [ ] | **DT-009** | [O] | P0 | None | Record judging criteria |
| [ ] | **DT-010** | [O] | P0 | None | Freeze deadline and internal milestones |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 01 — Project environment and repository setup

**Phase dependency:** Phase 0  
**Default phase priority:** P0  
**Phase gate:** A private, reproducible repository exists; raw/restricted data paths are ignored and dependencies are installable.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-011** | [E] | P0 | Phase 0 | Create project root directory |
| [ ] | **DT-012** | [E] | P0 | Phase 0 | Initialize Git repository |
| [ ] | **DT-013** | [E] | P0 | Phase 0 | Decide private repository policy |
| [ ] | **DT-014** | [E] | P0 | Phase 0 | Create .gitignore |
| [ ] | **DT-015** | [E] | P0 | Phase 0 | Create Python virtual environment |
| [ ] | **DT-016** | [E] | P0 | Phase 0 | Install required libraries |
| [ ] | **DT-017** | [E] | P0 | Phase 0 | Create requirements.txt |
| [ ] | **DT-018** | [E] | P0 | Phase 0 | Set random seed policy |
| [ ] | **DT-019** | [E] | P0 | Phase 0 | Create repository folder structure |
| [ ] | **DT-020** | [E] | P0 | Phase 0 | Create project configuration |
| [ ] | **DT-021** | [E] | P0 | Phase 0 | Create logging utility |
| [ ] | **DT-022** | [E] | P0 | Phase 0 | Create reproducibility notes |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 02 — Raw dataset inventory

**Phase dependency:** Phase 1  
**Default phase priority:** P0  
**Phase gate:** Every supplied file is inventoried, loadable, keyed and typed at a basic level.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-023** | [E] | P0 | Phase 1 | Extract DataSet_New.zip |
| [ ] | **DT-024** | [E] | P0 | Phase 1 | Inventory every supplied file |
| [ ] | **DT-025** | [E] | P0 | Phase 1 | Categorize files |
| [ ] | **DT-026** | [E] | P0 | Phase 1 | Load every CSV successfully |
| [ ] | **DT-027** | [E] | P0 | Phase 1 | Record row/column counts |
| [ ] | **DT-028** | [E] | P0 | Phase 1 | Record all column names |
| [ ] | **DT-029** | [E] | P0 | Phase 1 | Generate local data dictionary |
| [ ] | **DT-030** | [E] | P0 | Phase 1 | Identify primary keys |
| [ ] | **DT-031** | [E] | P0 | Phase 1 | Identify relational joins |
| [ ] | **DT-032** | [E] | P0 | Phase 1 | Identify numerical variables |
| [ ] | **DT-033** | [E] | P0 | Phase 1 | Identify categorical variables |
| [ ] | **DT-034** | [E] | P0 | Phase 1 | Identify date/time variables |
| [ ] | **DT-035** | [E] | P0 | Phase 1 | Identify future-known versus future-unknown variables |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 03 — Data-quality audit

**Phase dependency:** Phase 2  
**Default phase priority:** P0  
**Phase gate:** Core integrity assertions pass or every exception is documented before label/model work begins.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-036** | [E] | P0 | Phase 2 | Check missing values |
| [ ] | **DT-037** | [E] | P0 | Phase 2 | Check complete duplicate rows |
| [ ] | **DT-038** | [E] | P0 | Phase 2 | Check duplicate primary keys |
| [ ] | **DT-039** | [E] | P0 | Phase 2 | Validate data types |
| [ ] | **DT-040** | [E] | P0 | Phase 2 | Validate date formats |
| [ ] | **DT-041** | [E] | P0 | Phase 2 | Validate time formats |
| [ ] | **DT-042** | [E] | P0 | Phase 2 | Validate categorical values |
| [ ] | **DT-043** | [E] | P0 | Phase 2 | Check negative or impossible numeric values |
| [ ] | **DT-044** | [E] | P0 | Phase 2 | Check extreme values and outliers |
| [ ] | **DT-045** | [E] | P0 | Phase 2 | Check order ID uniqueness |
| [ ] | **DT-046** | [E] | P0 | Phase 2 | Check route-leg key uniqueness |
| [ ] | **DT-047** | [E] | P0 | Phase 2 | Check outlet-reference consistency |
| [ ] | **DT-048** | [E] | P0 | Phase 2 | Check vehicle-reference consistency |
| [ ] | **DT-049** | [E] | P0 | Phase 2 | Check calendar coverage |
| [ ] | **DT-050** | [E] | P0 | Phase 2 | Check road-condition coverage |
| [ ] | **DT-051** | [E] | P0 | Phase 2 | Check traffic-speed coverage |
| [ ] | **DT-052** | [E] | P0 | Phase 2 | Check train/test category compatibility |
| [ ] | **DT-053** | [E] | P0 | Phase 2 | Create automated schema assertions |
| [ ] | **DT-054** | [E] | P0 | Phase 2 | Produce dataset-audit report |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 04 — Task 1 training-data construction

**Phase dependency:** Phases 2–3  
**Default phase priority:** P0  
**Phase gate:** Task 1 dispatched orders join correctly to actual route legs; official service and lateness labels are reproducible and unit-tested.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-055** | [O] | P0 | Phases 2–3 | Identify dispatched historical orders |
| [ ] | **DT-056** | [O] | P0 | Phases 2–3 | Exclude orders without usable historical actual route records from Task 1 modelling |
| [ ] | **DT-057** | [O] | P0 | DT-055–DT-056 | Join orders to route legs |
| [ ] | **DT-058** | [O] | P0 | DT-057 | Validate one-to-one join cardinality |
| [ ] | **DT-059** | [E] | P0 | Phases 2–3 | Detect unmatched orders |
| [ ] | **DT-060** | [E] | P0 | Phases 2–3 | Detect duplicate route matches |
| [ ] | **DT-061** | [E] | P0 | Phases 2–3 | Validate joined outlet identity |
| [ ] | **DT-062** | [E] | P0 | Phases 2–3 | Convert clock-time strings to usable datetime/minute values |
| [ ] | **DT-063** | [E] | P0 | Phases 2–3 | Handle midnight/time-boundary cases safely |
| [ ] | **DT-064** | [O] | P0 | DT-057–DT-063 | Calculate service_start |
| [ ] | **DT-065** | [O] | P0 | DT-064 | Calculate service_min |
| [ ] | **DT-066** | [O] | P0 | DT-057–DT-063 | Calculate late_flag |
| [ ] | **DT-067** | [E] | P0 | Phases 2–3 | Validate non-negative service labels |
| [ ] | **DT-068** | [E] | P0 | Phases 2–3 | Inspect suspiciously long service durations |
| [ ] | **DT-069** | [E] | P0 | Phases 2–3 | Check late-class distribution |
| [ ] | **DT-070** | [E] | P0 | DT-064–DT-066 | Create Task 1 label unit tests |
| [ ] | **DT-071** | [E] | P0 | DT-070 | Save reproducible label-construction function |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 05 — Task 1 exploratory analysis

**Phase dependency:** Phase 4  
**Default phase priority:** P1  
**Phase gate:** EDA identifies useful operational relationships without changing official labels or deleting unexplained data.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-072** | [E] | P1 | Phase 4 | Analyze service-time distribution |
| [ ] | **DT-073** | [E] | P1 | Phase 4 | Analyze service time by brand |
| [ ] | **DT-074** | [E] | P1 | Phase 4 | Analyze service time by dock type |
| [ ] | **DT-075** | [E] | P1 | Phase 4 | Analyze service time by outlet |
| [ ] | **DT-076** | [E] | P1 | Phase 4 | Analyze service time vs order units |
| [ ] | **DT-077** | [E] | P1 | Phase 4 | Analyze service time vs weight |
| [ ] | **DT-078** | [E] | P1 | Phase 4 | Analyze service time vs volume |
| [ ] | **DT-079** | [E] | P1 | Phase 4 | Analyze late rate overall |
| [ ] | **DT-080** | [E] | P1 | Phase 4 | Analyze late rate by brand |
| [ ] | **DT-081** | [E] | P1 | Phase 4 | Analyze late rate by district |
| [ ] | **DT-082** | [E] | P1 | Phase 4 | Analyze late rate by depot |
| [ ] | **DT-083** | [E] | P1 | Phase 4 | Analyze late rate by route position |
| [ ] | **DT-084** | [E] | P1 | Phase 4 | Analyze late rate by planned-arrival slack |
| [ ] | **DT-085** | [E] | P1 | Phase 4 | Analyze road disruption effects |
| [ ] | **DT-086** | [E] | P1 | Phase 4 | Analyze traffic-speed effects |
| [ ] | **DT-087** | [E] | P1 | Phase 4 | Analyze monsoon effects |
| [ ] | **DT-088** | [E] | P1 | Phase 4 | Analyze day-of-week effects |
| [ ] | **DT-089** | [E] | P1 | Phase 4 | Check train/test distribution shift |
| [ ] | **DT-090** | [E] | P1 | Phase 4 | Select useful Task 1 visualizations |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 06 — Task 1 feature engineering

**Phase dependency:** Phase 4 (Phase 5 informs selection)  
**Default phase priority:** P1  
**Phase gate:** Train/test feature pipelines share the same schema; no future actual journey field can enter Task 1 predictors.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-091** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Build base order features |
| [ ] | **DT-092** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add outlet features |
| [ ] | **DT-093** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add dock/access features |
| [ ] | **DT-094** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add depot/district features |
| [ ] | **DT-095** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add vehicle features |
| [ ] | **DT-096** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add route-position features |
| [ ] | **DT-097** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add route-stop-count feature |
| [ ] | **DT-098** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add sequence fraction |
| [ ] | **DT-099** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add first-stop indicator |
| [ ] | **DT-100** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add planned arrival/departure time features |
| [ ] | **DT-101** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add planned-slack feature |
| [ ] | **DT-102** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add planned early-wait feature |
| [ ] | **DT-103** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add distance features |
| [ ] | **DT-104** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add planned travel duration |
| [ ] | **DT-105** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add calendar features |
| [ ] | **DT-106** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add payday feature |
| [ ] | **DT-107** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add festival feature |
| [ ] | **DT-108** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add festival-ramp feature |
| [ ] | **DT-109** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add monsoon feature |
| [ ] | **DT-110** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add road-condition feature |
| [ ] | **DT-111** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add traffic-speed feature |
| [ ] | **DT-112** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add service-allowance feature |
| [ ] | **DT-113** | [E] | P2 | Phase 4 (Phase 5 informs selection) | Add weight-per-unit |
| [ ] | **DT-114** | [E] | P2 | Phase 4 (Phase 5 informs selection) | Add volume-per-unit |
| [ ] | **DT-115** | [E] | P2 | Phase 4 (Phase 5 informs selection) | Add density |
| [ ] | **DT-116** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Add route-total weight/volume features |
| [ ] | **DT-117** | [E] | P2 | Phase 4 (Phase 5 informs selection) | Add vehicle utilization estimates |
| [ ] | **DT-118** | [E] | P2 | Phase 4 (Phase 5 informs selection) | Add cumulative route-context features |
| [ ] | **DT-119** | [E] | P2 | Phase 4 (Phase 5 informs selection) | Build leakage-safe historical features |
| [ ] | **DT-120** | [E] | P1 | Phase 4 (Phase 5 informs selection) | Create feature metadata table |
| [ ] | **DT-121** | [E] | P1 | DT-091–DT-120 | Create automatic leakage check |
| [ ] | **DT-122** | [O] | P0 | DT-121 | Ensure no actual journey fields enter prediction features |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 07 — Task 1 validation design

**Phase dependency:** Phases 4–6  
**Default phase priority:** P1  
**Phase gate:** Chronological validation and metrics are frozen before model comparison.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-123** | [E] | P1 | Phases 4–6 | Sort historical data chronologically |
| [ ] | **DT-124** | [E] | P1 | Phases 4–6 | Define chronological holdout |
| [ ] | **DT-125** | [E] | P1 | Phases 4–6 | Define expanding time folds |
| [ ] | **DT-126** | [E] | P1 | Phases 4–6 | Keep same-date records in the same split |
| [ ] | **DT-127** | [E] | P1 | Phases 4–6 | Freeze regression metrics |
| [ ] | **DT-128** | [E] | P1 | Phases 4–6 | Freeze lateness probability metrics |
| [ ] | **DT-129** | [E] | P1 | Phases 4–6 | Define segment-level metrics |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 08 — Task 1 baselines

**Phase dependency:** Phase 7  
**Default phase priority:** P1  
**Phase gate:** Simple baselines are reproducible and stored; advanced models must be compared against them.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-130** | [E] | P1 | DT-123–DT-129 | Build global median service baseline |
| [ ] | **DT-131** | [E] | P1 | Phase 7 | Build brand median service baseline |
| [ ] | **DT-132** | [E] | P1 | Phase 7 | Build brand+dock service baseline |
| [ ] | **DT-133** | [E] | P1 | Phase 7 | Build constant late-probability baseline |
| [ ] | **DT-134** | [E] | P1 | Phase 7 | Build grouped late-rate baseline |
| [ ] | **DT-135** | [E] | P1 | Phase 7 | Build linear regression baseline |
| [ ] | **DT-136** | [E] | P1 | Phase 7 | Build logistic regression baseline |
| [ ] | **DT-137** | [E] | P1 | Phase 7 | Store baseline experiment results |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 09 — Task 1 advanced modelling

**Phase dependency:** Phase 8  
**Default phase priority:** P1  
**Phase gate:** Champion Task 1 models are selected using frozen validation, with calibration/error analysis completed.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-138** | [E] | P1 | DT-130–DT-137 | Train CatBoost regression model |
| [ ] | **DT-139** | [E] | P1 | DT-130–DT-137 | Train CatBoost late classifier |
| [ ] | **DT-140** | [C] | P2 | Phase 8 | Train LightGBM challenger |
| [ ] | **DT-141** | [C] | P2 | Phase 8 | Optionally train XGBoost challenger |
| [ ] | **DT-142** | [E] | P1 | Phase 8 | Compare models under same folds |
| [ ] | **DT-143** | [E] | P1 | Phase 8 | Tune regression hyperparameters |
| [ ] | **DT-144** | [E] | P1 | Phase 8 | Tune classifier hyperparameters |
| [ ] | **DT-145** | [E] | P1 | Phase 8 | Use early stopping |
| [ ] | **DT-146** | [E] | P1 | Phase 8 | Analyze overfitting |
| [ ] | **DT-147** | [E] | P1 | Phase 8 | Inspect worst regression errors |
| [ ] | **DT-148** | [E] | P1 | Phase 8 | Inspect high-confidence classification errors |
| [ ] | **DT-149** | [E] | P1 | Phase 8 | Check brand-specific model performance |
| [ ] | **DT-150** | [E] | P1 | Phase 8 | Check depot-specific model performance |
| [ ] | **DT-151** | [E] | P1 | Phase 8 | Generate calibration curve |
| [ ] | **DT-152** | [E] | P1 | Phase 8 | Test probability calibration |
| [ ] | **DT-153** | [E] | P1 | Phase 8 | Compare uncalibrated vs calibrated probability metrics |
| [ ] | **DT-154** | [E] | P1 | DT-142–DT-153 | Select final Task 1 regression model |
| [ ] | **DT-155** | [E] | P1 | DT-142–DT-153 | Select final Task 1 lateness model |
| [ ] | **DT-156** | [E] | P1 | Phase 8 | Freeze Task 1 model configuration |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 10 — Task 1 final training and inference

**Phase dependency:** Phase 9  
**Default phase priority:** P0  
**Phase gate:** Saved Task 1 models and exact `submission_task1.csv` are generated by a deterministic inference pipeline.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-157** | [E] | P0 | DT-154 | Retrain final service model on allowed full history |
| [ ] | **DT-158** | [E] | P0 | DT-155 | Retrain final late model |
| [ ] | **DT-159** | [O] | P0 | Phase 9 | Save service model |
| [ ] | **DT-160** | [O] | P0 | Phase 9 | Save lateness model |
| [ ] | **DT-161** | [E] | P0 | DT-157–DT-160 | Build Task 1 inference pipeline |
| [ ] | **DT-162** | [O] | P0 | Phase 9 | Load task1_test_inputs.csv |
| [ ] | **DT-163** | [O] | P0 | Phase 9 | Join route_legs_test.csv |
| [ ] | **DT-164** | [E] | P0 | Phase 9 | Generate identical test features |
| [ ] | **DT-165** | [O] | P0 | Phase 9 | Generate pred_service_min |
| [ ] | **DT-166** | [E] | P0 | Phase 9 | Reject/check impossible negative service predictions |
| [ ] | **DT-167** | [O] | P0 | Phase 9 | Generate pred_late_prob |
| [ ] | **DT-168** | [O] | P0 | Phase 9 | Ensure all probabilities are within [0,1] |
| [ ] | **DT-169** | [O] | P0 | Phase 9 | Restore official Task 1 row order |
| [ ] | **DT-170** | [O] | P0 | Phase 9 | Preserve every official delivery_id |
| [ ] | **DT-171** | [O] | P0 | Phase 9 | Fill official Task 1 template only |
| [ ] | **DT-172** | [O] | P0 | DT-161–DT-171 | Export submission_task1.csv |
| [ ] | **DT-173** | [O] | P0 | Phase 9 | Validate Task 1 final file |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 11 — Task 2A demand-history construction

**Phase dependency:** Phases 2–3  
**Default phase priority:** P0  
**Phase gate:** The Task 2A weekly panel counts every unique requested order correctly and preserves Fresh chilled logic.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-174** | [O] | P0 | Phases 2–3 | Load deliveries_train.csv |
| [ ] | **DT-175** | [O] | P0 | Phases 2–3 | Load task1_test_inputs.csv |
| [ ] | **DT-176** | [O] | P0 | DT-174–DT-175 | Append both demand datasets |
| [ ] | **DT-177** | [O] | P0 | Phases 2–3 | Verify delivery_id uniqueness after combination |
| [ ] | **DT-178** | [O] | P0 | Phases 2–3 | Keep attempted orders |
| [ ] | **DT-179** | [O] | P0 | Phases 2–3 | Keep deferred orders |
| [ ] | **DT-180** | [O] | P0 | Phases 2–3 | Keep not_run orders |
| [ ] | **DT-181** | [O] | P0 | Phases 2–3 | Use requested order_date |
| [ ] | **DT-182** | [O] | P0 | DT-176–DT-181 | Join calendar.csv |
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
**READY FOR NEXT PHASE:** NO


### Phase 12 — Task 2A exploratory analysis

**Phase dependency:** Phase 11  
**Default phase priority:** P1  
**Phase gate:** Demand seasonality, trend and calendar relationships are understood sufficiently to justify forecasting features.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-192** | [E] | P1 | Phase 11 | Plot weekly total demand by depot/brand |
| [ ] | **DT-193** | [E] | P1 | Phase 11 | Plot Fresh chilled demand |
| [ ] | **DT-194** | [E] | P1 | Phase 11 | Analyze recent trend |
| [ ] | **DT-195** | [E] | P1 | Phase 11 | Analyze yearly seasonality |
| [ ] | **DT-196** | [E] | P1 | Phase 11 | Analyze festival effects |
| [ ] | **DT-197** | [E] | P1 | Phase 11 | Analyze festival-ramp effects |
| [ ] | **DT-198** | [E] | P1 | Phase 11 | Analyze payday effects |
| [ ] | **DT-199** | [E] | P1 | Phase 11 | Analyze holiday effects |
| [ ] | **DT-200** | [E] | P1 | Phase 11 | Analyze monsoon effects |
| [ ] | **DT-201** | [E] | P1 | Phase 11 | Analyze number of operating days per week |
| [ ] | **DT-202** | [E] | P1 | Phase 11 | Compare same week across years |
| [ ] | **DT-203** | [E] | P1 | Phase 11 | Detect abnormal weekly spikes |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 13 — Task 2A forecasting features

**Phase dependency:** Phase 11 (Phase 12 informs selection)  
**Default phase priority:** P1  
**Phase gate:** All forecast features are past-known or target-week-known; no future actual demand leaks into predictors.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-204** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Create lag-1 feature |
| [ ] | **DT-205** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Create lag-2 feature |
| [ ] | **DT-206** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Create lag-4 feature |
| [ ] | **DT-207** | [E] | P2 | Phase 11 (Phase 12 informs selection) | Create lag-13 feature |
| [ ] | **DT-208** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Create lag-52 feature |
| [ ] | **DT-209** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Create rolling 4-week mean |
| [ ] | **DT-210** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Create rolling 8-week mean |
| [ ] | **DT-211** | [E] | P2 | Phase 11 (Phase 12 informs selection) | Create rolling 13-week mean |
| [ ] | **DT-212** | [E] | P2 | Phase 11 (Phase 12 informs selection) | Create trend features |
| [ ] | **DT-213** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Add future operating-day count |
| [ ] | **DT-214** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Add future payday count |
| [ ] | **DT-215** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Add future holiday/festival features |
| [ ] | **DT-216** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Add future festival-ramp features |
| [ ] | **DT-217** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Add monsoon features |
| [ ] | **DT-218** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Add depot |
| [ ] | **DT-219** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Add brand |
| [ ] | **DT-220** | [E] | P1 | Phase 11 (Phase 12 informs selection) | Add forecast horizon |
| [ ] | **DT-221** | [E] | P2 | Phase 11 (Phase 12 informs selection) | Build direct multi-horizon modelling table |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 14 — Task 2A forecast validation

**Phase dependency:** Phases 11–13  
**Default phase priority:** P0  
**Phase gate:** Rolling-origin, ten-week backtesting is frozen and reproducible.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-222** | [O] | P0 | DT-204–DT-221 | Define rolling-origin validation |
| [ ] | **DT-223** | [O] | P0 | Phases 11–13 | Use 10-week validation windows |
| [ ] | **DT-224** | [O] | P0 | Phases 11–13 | Prevent future-demand leakage |
| [ ] | **DT-225** | [E] | P0 | Phases 11–13 | Define forecast metrics |
| [ ] | **DT-226** | [E] | P0 | Phases 11–13 | Evaluate per series |
| [ ] | **DT-227** | [E] | P0 | Phases 11–13 | Evaluate overall |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 15 — Task 2A baseline models

**Phase dependency:** Phase 14  
**Default phase priority:** P1  
**Phase gate:** Seasonal/simple forecasting baselines exist for total and chilled demand.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-228** | [E] | P1 | DT-222–DT-227 | Last-week baseline |
| [ ] | **DT-229** | [E] | P1 | Phase 14 | Recent rolling-mean baseline |
| [ ] | **DT-230** | [E] | P1 | Phase 14 | Same-week-last-year baseline |
| [ ] | **DT-231** | [E] | P1 | Phase 14 | Seasonal/recent weighted baseline |
| [ ] | **DT-232** | [E] | P1 | Phase 14 | Build separate chilled-demand baseline |
| [ ] | **DT-233** | [E] | P1 | Phase 14 | Compare baseline results across backtests |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 16 — Task 2A advanced forecasting

**Phase dependency:** Phase 15  
**Default phase priority:** P1  
**Phase gate:** Champion Task 2A approach is selected only if it beats/justifies itself against baselines across rolling backtests.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-234** | [E] | P1 | DT-228–DT-233 | Train global CatBoost forecast model |
| [ ] | **DT-235** | [E] | P2 | Phase 15 | Train LightGBM challenger |
| [ ] | **DT-236** | [E] | P1 | Phase 15 | Compare ML against seasonal baselines |
| [ ] | **DT-237** | [E] | P1 | Phase 15 | Reject advanced model if it does not beat simpler approach |
| [ ] | **DT-238** | [E] | P1 | Phase 15 | Test forecast ensemble |
| [ ] | **DT-239** | [E] | P1 | DT-236–DT-238 | Select best total-volume forecast approach |
| [ ] | **DT-240** | [E] | P1 | DT-236–DT-238 | Select best chilled-volume forecast approach |
| [ ] | **DT-241** | [E] | P1 | Phase 15 | Freeze Task 2A model/configuration |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 17 — Task 2A final inference

**Phase dependency:** Phase 16  
**Default phase priority:** P0  
**Phase gate:** Exact `submission_task2a.csv` passes non-negativity, chilled-zero and chilled≤total checks.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-242** | [O] | P0 | DT-239–DT-241 | Load task2a_test_inputs.csv |
| [ ] | **DT-243** | [O] | P0 | Phase 16 | Generate future known calendar features |
| [ ] | **DT-244** | [O] | P0 | Phase 16 | Produce total-volume forecast |
| [ ] | **DT-245** | [O] | P0 | Phase 16 | Produce Fresh chilled forecast |
| [ ] | **DT-246** | [O] | P0 | Phase 16 | Set Style chilled exactly to 0 |
| [ ] | **DT-247** | [O] | P0 | Phase 16 | Set Tech chilled exactly to 0 |
| [ ] | **DT-248** | [O] | P0 | Phase 16 | Clip negative forecasts |
| [ ] | **DT-249** | [O] | P0 | Phase 16 | Enforce chilled ≤ total |
| [ ] | **DT-250** | [O] | P0 | Phase 16 | Preserve official row_id |
| [ ] | **DT-251** | [O] | P0 | Phase 16 | Map predictions to exact template |
| [ ] | **DT-252** | [O] | P0 | DT-242–DT-251 | Export submission_task2a.csv |
| [ ] | **DT-253** | [O] | P0 | Phase 16 | Validate Task 2A file |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 18 — Task 2B scenario understanding

**Phase dependency:** Phases 2–3  
**Default phase priority:** P0  
**Phase gate:** S1 demand and available Peliyagoda fleet are correctly understood; workshop vehicles are excluded.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-254** | [O] | P0 | Phases 2–3 | Load peak-day orders |
| [ ] | **DT-255** | [O] | P0 | Phases 2–3 | Load peak-day fleet |
| [ ] | **DT-256** | [O] | P0 | Phases 2–3 | Load full vehicle reference |
| [ ] | **DT-257** | [O] | P0 | Phases 2–3 | Load district travel table |
| [ ] | **DT-258** | [O] | P0 | Phases 2–3 | Load service allowance |
| [ ] | **DT-259** | [O] | P0 | Phases 2–3 | Filter to scenario S1 |
| [ ] | **DT-260** | [O] | P0 | Phases 2–3 | Filter fleet to available vehicles |
| [ ] | **DT-261** | [O] | P0 | Phases 2–3 | Exclude in_workshop vehicles |
| [ ] | **DT-262** | [O] | P0 | Phases 2–3 | Confirm Peliyagoda home-depot requirement |
| [ ] | **DT-263** | [E] | P0 | Phases 2–3 | Summarize demand by brand |
| [ ] | **DT-264** | [E] | P0 | Phases 2–3 | Summarize demand by district |
| [ ] | **DT-265** | [E] | P0 | Phases 2–3 | Summarize chilled demand |
| [ ] | **DT-266** | [E] | P0 | Phases 2–3 | Summarize van-only demand |
| [ ] | **DT-267** | [E] | P0 | Phases 2–3 | Summarize weight demand |
| [ ] | **DT-268** | [E] | P0 | Phases 2–3 | Summarize volume demand |
| [ ] | **DT-269** | [E] | P0 | Phases 2–3 | Identify previously deferred orders |
| [ ] | **DT-270** | [E] | P0 | Phases 2–3 | Inspect days_since_last_served |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 19 — Task 2B compatibility engine

**Phase dependency:** Phase 18  
**Default phase priority:** P1  
**Phase gate:** Every order has a validated compatible-vehicle set and individually impossible orders are identified.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-271** | [O] | P0 | DT-254–DT-270 | Generate order-to-vehicle compatibility matrix |
| [ ] | **DT-272** | [O] | P0 | Phase 18 | Enforce refrigeration compatibility |
| [ ] | **DT-273** | [O] | P0 | Phase 18 | Enforce van-only compatibility |
| [ ] | **DT-274** | [O] | P0 | Phase 18 | Enforce vehicle home depot |
| [ ] | **DT-275** | [O] | P0 | Phase 18 | Check whether each order fits a vehicle by weight |
| [ ] | **DT-276** | [O] | P0 | Phase 18 | Check whether each order fits a vehicle by volume |
| [ ] | **DT-277** | [O] | P0 | Phase 18 | Identify orders individually impossible to serve |
| [ ] | **DT-278** | [E] | P1 | Phase 18 | Count compatible vehicles per order |
| [ ] | **DT-279** | [E] | P1 | Phase 18 | Calculate vehicle scarcity |
| [ ] | **DT-280** | [E] | P1 | Phase 18 | Identify reefer bottleneck |
| [ ] | **DT-281** | [E] | P1 | Phase 18 | Identify reefer-van bottleneck |
| [ ] | **DT-282** | [E] | P1 | Phase 18 | Identify trip-slot bottlenecks |
| [ ] | **DT-283** | [E] | P1 | Phase 18 | Produce Task 2B scarcity report |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 20 — Task 2B trip calculation engine

**Phase dependency:** Phase 18  
**Default phase priority:** P0  
**Phase gate:** Official Task 2B trip-minute formula is implemented and unit-tested against the booklet example.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-284** | [O] | P0 | DT-254–DT-270 | Group candidate trips by brand + district |
| [ ] | **DT-285** | [O] | P0 | Phase 18 | Calculate outbound district travel |
| [ ] | **DT-286** | [O] | P0 | Phase 18 | Calculate inter-stop travel |
| [ ] | **DT-287** | [O] | P0 | Phase 18 | Join brand+dock service allowance |
| [ ] | **DT-288** | [O] | P0 | Phase 18 | Calculate total handling allowance |
| [ ] | **DT-289** | [O] | P0 | DT-284–DT-288 | Calculate exact trip minutes |
| [ ] | **DT-290** | [O] | P0 | Phase 18 | Do not add return leg |
| [ ] | **DT-291** | [E] | P0 | Phase 18 | Build trip-time unit tests |
| [ ] | **DT-292** | [O] | P0 | Phase 18 | Validate example from official booklet |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 21 — Task 2B priority-policy design

**Phase dependency:** Phases 18–20  
**Default phase priority:** P1  
**Phase gate:** A transparent prioritization policy is documented separately from hard feasibility rules.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-293** | [E] | P1 | DT-271–DT-292 | Decide what good allocation means |
| [ ] | **DT-294** | [E] | P1 | Phases 18–20 | Design transparent prioritization policy |
| [ ] | **DT-295** | [E] | P1 | Phases 18–20 | Distinguish hard rules from our priority policy |
| [ ] | **DT-296** | [E] | P1 | Phases 18–20 | Decide lexicographic or weighted objective |
| [ ] | **DT-297** | [E] | P1 | Phases 18–20 | Document fairness rationale |
| [ ] | **DT-298** | [E] | P1 | Phases 18–20 | Document business rationale |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 22 — Task 2B optimization solver

**Phase dependency:** Phases 19–21  
**Default phase priority:** P0  
**Phase gate:** A final feasible allocation exists under all seven hard rules and the chosen priority objective.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-299** | [E] | P0 | DT-293–DT-298 | Install/configure OR-Tools |
| [ ] | **DT-300** | [E] | P0 | Phases 19–21 | Define order assignment variables |
| [ ] | **DT-301** | [E] | P0 | Phases 19–21 | Define vehicle/trip usage variables |
| [ ] | **DT-302** | [O] | P0 | Phases 19–21 | Enforce one decision per order |
| [ ] | **DT-303** | [O] | P0 | Phases 19–21 | Enforce whole-order assignment |
| [ ] | **DT-304** | [O] | P0 | Phases 19–21 | Enforce same-brand-per-trip |
| [ ] | **DT-305** | [O] | P0 | Phases 19–21 | Enforce same-district-per-trip |
| [ ] | **DT-306** | [O] | P0 | Phases 19–21 | Enforce reefer rule |
| [ ] | **DT-307** | [O] | P0 | Phases 19–21 | Enforce van-only rule |
| [ ] | **DT-308** | [O] | P0 | Phases 19–21 | Enforce home-depot rule |
| [ ] | **DT-309** | [O] | P0 | Phases 19–21 | Enforce weight capacity |
| [ ] | **DT-310** | [O] | P0 | Phases 19–21 | Enforce volume capacity |
| [ ] | **DT-311** | [O] | P0 | Phases 19–21 | Enforce maximum two trips per vehicle |
| [ ] | **DT-312** | [O] | P0 | Phases 19–21 | Enforce Fresh ≤270 minutes |
| [ ] | **DT-313** | [O] | P0 | Phases 19–21 | Enforce Style+Tech ≤480 minutes |
| [ ] | **DT-314** | [E] | P0 | Phases 19–21 | Add prioritization objective |
| [ ] | **DT-315** | [E] | P0 | DT-299–DT-314 | Solve initial feasible allocation |
| [ ] | **DT-316** | [E] | P0 | Phases 19–21 | Inspect solver status |
| [ ] | **DT-317** | [E] | P0 | Phases 19–21 | Validate every served trip manually/independently |
| [ ] | **DT-318** | [E] | P0 | Phases 19–21 | Tune prioritization objective |
| [ ] | **DT-319** | [E] | P0 | DT-315–DT-318 | Freeze final allocation |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 23 — Task 2B independent validator

**Phase dependency:** Phase 22  
**Default phase priority:** P0  
**Phase gate:** Independent validator passes and organizer `check_allocation.py` passes; checker evidence is saved.

| Status | Task | Mark | Pri | Dependency | Work item |
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
| [ ] | **DT-329** | [O] | P0 | DT-320–DT-328 | Run official check_allocation.py |
| [ ] | **DT-330** | [E] | P0 | Phase 22 | Save checker output/evidence |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 24 — Task 2B output and written policy

**Phase dependency:** Phase 23  
**Default phase priority:** P0  
**Phase gate:** Exact `submission_task2b.csv` and one-page prioritization policy are complete and defensible.

| Status | Task | Mark | Pri | Dependency | Work item |
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

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 25 — Explainability

**Phase dependency:** Final/near-final Task 1 models (Phases 9–10)  
**Default phase priority:** P1  
**Phase gate:** Selected model explanations are accurate, useful and do not make causal claims unsupported by the data.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-343** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate service-model feature importance |
| [ ] | **DT-344** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate lateness-model feature importance |
| [ ] | **DT-345** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate SHAP global explanation |
| [ ] | **DT-346** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate local service prediction explanation |
| [ ] | **DT-347** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Generate local late-risk explanation |
| [ ] | **DT-348** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Identify meaningful business drivers |
| [ ] | **DT-349** | [C] | P2 | Final/near-final Task 1 models (Phases 9–10) | Avoid unsupported causal claims |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 26 — Hero feature — Explainable Deferral Reasoner

**Phase dependency:** Phases 22–24  
**Default phase priority:** P2  
**Phase gate:** If implemented, deferral explanations are solver-grounded and do not displace required work.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-350** | [C] | P2 | DT-319 + DT-337–DT-342 | Build reason-code taxonomy |
| [ ] | **DT-351** | [C] | P2 | Phases 22–24 | Detect individually infeasible orders |
| [ ] | **DT-352** | [C] | P2 | Phases 22–24 | Detect shared resource bottleneck |
| [ ] | **DT-353** | [C] | P2 | Phases 22–24 | Force deferred order in counterfactual solve |
| [ ] | **DT-354** | [C] | P2 | Phases 22–24 | Measure what must change to serve it |
| [ ] | **DT-355** | [C] | P2 | Phases 22–24 | Classify unavoidable vs policy tradeoff |
| [ ] | **DT-356** | [C] | P2 | Phases 22–24 | Generate human-readable deferral explanation |
| [ ] | **DT-357** | [C] | P2 | Phases 22–24 | Select 1–2 strong demo examples |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 27 — Optional forecast uncertainty

**Phase dependency:** Final Task 1/Task 2A models  
**Default phase priority:** P3  
**Phase gate:** If implemented, uncertainty outputs are clearly unofficial and do not alter official CSV schemas.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-358** | [C] | P3 | Final Task 1/Task 2A models | Estimate service prediction uncertainty |
| [ ] | **DT-359** | [C] | P2 | Final Task 1/Task 2A models | Estimate forecast uncertainty |
| [ ] | **DT-360** | [C] | P2 | Final Task 1/Task 2A models | Build forecast confidence intervals |
| [ ] | **DT-361** | [O] | P0 | Final Task 1/Task 2A models | Keep unofficial uncertainty fields out of official CSV |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 28 — Optional WayLoom integration contract

**Phase dependency:** Final Task 1/2A/2B outputs; optional and must not block submission  
**Default phase priority:** P2  
**Phase gate:** If implemented, integration uses schemas/synthetic examples and never exposes restricted competition data.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-362** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Define Task 1 JSON schema |
| [ ] | **DT-363** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Define demand forecast JSON schema |
| [ ] | **DT-364** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Define allocation insight JSON schema |
| [ ] | **DT-365** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Define deferral explanation schema |
| [ ] | **DT-366** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Create synthetic demo responses |
| [ ] | **DT-367** | [C] | P2 | Final Task 1/2A/2B outputs; optional and must not block submission | Share integration contract with Hackathon team |
| [ ] | **DT-368** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Build optional FastAPI service |
| [ ] | **DT-369** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Implement model loading endpoint |
| [ ] | **DT-370** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Implement delivery-risk endpoint |
| [ ] | **DT-371** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Implement demand-forecast endpoint |
| [ ] | **DT-372** | [C] | P3 | Final Task 1/2A/2B outputs; optional and must not block submission | Implement allocation endpoint |
| [ ] | **DT-373** | [O] | P0 | Final Task 1/2A/2B outputs; optional and must not block submission | Prevent official private test records from becoming public |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 29 — Architecture documentation

**Phase dependency:** Stable architecture from Phases 4–24  
**Default phase priority:** P0  
**Phase gate:** Required architecture diagrams accurately match the final implemented pipelines and proposed deployment.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-374** | [O] | P0 | Core pipeline architecture stable | Create high-level Datathon architecture |
| [ ] | **DT-375** | [E] | P0 | Stable architecture from Phases 4–24 | Create Task 1 pipeline diagram |
| [ ] | **DT-376** | [E] | P0 | Stable architecture from Phases 4–24 | Create Task 2A forecasting diagram |
| [ ] | **DT-377** | [E] | P0 | Stable architecture from Phases 4–24 | Create Task 2B optimization diagram |
| [ ] | **DT-378** | [O] | P0 | Stable architecture from Phases 4–24 | Show proposed deployment approach |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 30 — Preprocessing document

**Phase dependency:** Stable pipelines from Phases 4–24  
**Default phase priority:** P0  
**Phase gate:** Required preprocessing document accurately explains preparation, labels, cleaning, features and rationale.

| Status | Task | Mark | Pri | Dependency | Work item |
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

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 31 — Final competition notebook

**Phase dependency:** Phases 10,17,24 and documentation state  
**Default phase priority:** P0  
**Phase gate:** Final notebook runs top-to-bottom and final inference loads saved models rather than relying on hidden state.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-389** | [O] | P0 | Task 1, Task 2A and Task 2B finalized | Create TeamName_FinalNotebook.ipynb |
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

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 32 — Model artifact management

**Phase dependency:** Final selected models  
**Default phase priority:** P0  
**Phase gate:** All serialized model/preprocessing artifacts load successfully and reproduce intended predictions.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-412** | [O] | P0 | Final selected models | Save Task 1 service model |
| [ ] | **DT-413** | [O] | P0 | Final selected models | Save Task 1 lateness model |
| [ ] | **DT-414** | [O] | P0 | Final selected models | Save Task 2A model/artifacts if applicable |
| [ ] | **DT-415** | [E] | P0 | Final selected models | Save preprocessing objects if necessary |
| [ ] | **DT-416** | [E] | P0 | Final selected models | Record model versions |
| [ ] | **DT-417** | [O] | P0 | Final selected models | Test model serialization |
| [ ] | **DT-418** | [O] | P0 | Final selected models | Test model deserialization |
| [ ] | **DT-419** | [E] | P0 | Final selected models | Compare loaded-model predictions with original predictions |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 33 — Final submission-file testing

**Phase dependency:** Phases 10,17,24  
**Default phase priority:** P0  
**Phase gate:** All three official submission files pass exact schema, ID, row and value validations.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-420** | [O] | P0 | Submission files generated | Test Task 1 filename |
| [ ] | **DT-421** | [O] | P0 | Phases 10,17,24 | Test Task 1 columns |
| [ ] | **DT-422** | [O] | P0 | Phases 10,17,24 | Test Task 1 row count |
| [ ] | **DT-423** | [O] | P0 | Phases 10,17,24 | Test Task 1 row order |
| [ ] | **DT-424** | [O] | P0 | Phases 10,17,24 | Test Task 1 IDs unchanged |
| [ ] | **DT-425** | [O] | P0 | Phases 10,17,24 | Test Task 1 predictions finite |
| [ ] | **DT-426** | [O] | P0 | Phases 10,17,24 | Test Task 1 probabilities in range |
| [ ] | **DT-427** | [O] | P0 | Phases 10,17,24 | Test Task 2A filename |
| [ ] | **DT-428** | [O] | P0 | Phases 10,17,24 | Test Task 2A row IDs unchanged |
| [ ] | **DT-429** | [O] | P0 | Phases 10,17,24 | Test Task 2A predictions nonnegative |
| [ ] | **DT-430** | [O] | P0 | Phases 10,17,24 | Test Style chilled exactly zero |
| [ ] | **DT-431** | [O] | P0 | Phases 10,17,24 | Test Tech chilled exactly zero |
| [ ] | **DT-432** | [O] | P0 | Phases 10,17,24 | Test chilled ≤ total |
| [ ] | **DT-433** | [O] | P0 | Phases 10,17,24 | Test Task 2B filename |
| [ ] | **DT-434** | [O] | P0 | Phases 10,17,24 | Test Task 2B all orders present |
| [ ] | **DT-435** | [O] | P0 | Phases 10,17,24 | Test Task 2B all placeholders removed |
| [ ] | **DT-436** | [O] | P0 | Phases 10,17,24 | Test served/deferred spelling/format |
| [ ] | **DT-437** | [O] | P0 | Phases 10,17,24 | Test Task 2B with official checker again |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 34 — General automated testing

**Phase dependency:** Implemented pipelines  
**Default phase priority:** P1  
**Phase gate:** Automated test suite covers critical data rules, labels, inference and allocation constraints.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-438** | [E] | P1 | Core modules implemented | Create pytest test suite |
| [ ] | **DT-439** | [E] | P1 | Implemented pipelines | Test schemas |
| [ ] | **DT-440** | [E] | P1 | Implemented pipelines | Test joins |
| [ ] | **DT-441** | [E] | P1 | Implemented pipelines | Test time utilities |
| [ ] | **DT-442** | [E] | P1 | Implemented pipelines | Test label generation |
| [ ] | **DT-443** | [E] | P1 | Implemented pipelines | Test feature generation |
| [ ] | **DT-444** | [E] | P1 | Implemented pipelines | Test Task 1 inference |
| [ ] | **DT-445** | [E] | P1 | Implemented pipelines | Test Task 2A aggregation |
| [ ] | **DT-446** | [E] | P1 | Implemented pipelines | Test Task 2A forecast output constraints |
| [ ] | **DT-447** | [E] | P1 | Implemented pipelines | Test Task 2B compatibility rules |
| [ ] | **DT-448** | [E] | P1 | Implemented pipelines | Test Task 2B trip-time formula |
| [ ] | **DT-449** | [E] | P1 | Implemented pipelines | Test Task 2B optimizer output |
| [ ] | **DT-450** | [E] | P1 | Implemented pipelines | Test saved-model loading |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 35 — AI-use disclosure

**Phase dependency:** Ongoing log from project start; finalize after core work  
**Default phase priority:** P0  
**Phase gate:** AI-use disclosure is complete, accurate and consistent with competition restrictions.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-451** | [O] | P0 | Maintain throughout project | Record all AI-assisted activities |
| [ ] | **DT-452** | [O] | P0 | Ongoing log from project start; finalize after core work | Record human-controlled modelling work |
| [ ] | **DT-453** | [O] | P0 | Ongoing log from project start; finalize after core work | Record where AI was not used |
| [ ] | **DT-454** | [O] | P0 | Ongoing log from project start; finalize after core work | Confirm compliance with competition restrictions |
| [ ] | **DT-455** | [O] | P0 | Ongoing log from project start; finalize after core work | Write final AI-tool disclosure |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 36 — README / project documentation

**Phase dependency:** Stable repository and outputs  
**Default phase priority:** P1  
**Phase gate:** README allows a reviewer/team member to understand and reproduce the Datathon workflow.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-456** | [E] | P1 | Stable repository and outputs | Write Datathon README |
| [ ] | **DT-457** | [E] | P1 | Stable repository and outputs | Explain project objectives |
| [ ] | **DT-458** | [E] | P1 | Stable repository and outputs | Explain folder structure |
| [ ] | **DT-459** | [E] | P1 | Stable repository and outputs | Explain environment setup |
| [ ] | **DT-460** | [E] | P1 | Stable repository and outputs | Explain how to run notebook |
| [ ] | **DT-461** | [E] | P1 | Stable repository and outputs | Explain model files |
| [ ] | **DT-462** | [E] | P1 | Stable repository and outputs | Explain how outputs are generated |
| [ ] | **DT-463** | [E] | P1 | Stable repository and outputs | Document random seed/reproducibility |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 37 — Results summary and competition evidence

**Phase dependency:** Final metrics/outputs  
**Default phase priority:** P1  
**Phase gate:** Final evidence includes only the strongest metrics/charts needed to support the technical story.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-464** | [E] | P1 | Final metrics/outputs | Produce final Task 1 metrics table |
| [ ] | **DT-465** | [E] | P1 | Final metrics/outputs | Compare Task 1 baseline vs final model |
| [ ] | **DT-466** | [E] | P1 | Final metrics/outputs | Produce calibration visualization |
| [ ] | **DT-467** | [E] | P1 | Final metrics/outputs | Produce Task 1 feature explanation |
| [ ] | **DT-468** | [E] | P1 | Final metrics/outputs | Produce Task 2A backtesting results |
| [ ] | **DT-469** | [E] | P1 | Final metrics/outputs | Compare Task 2A baselines/final model |
| [ ] | **DT-470** | [E] | P1 | Final metrics/outputs | Produce future-demand chart |
| [ ] | **DT-471** | [E] | P1 | Final metrics/outputs | Produce Task 2B scarcity summary |
| [ ] | **DT-472** | [E] | P1 | Final metrics/outputs | Produce served/deferred summary |
| [ ] | **DT-473** | [E] | P1 | Final metrics/outputs | Produce solver/checker evidence |
| [ ] | **DT-474** | [E] | P1 | Final metrics/outputs | Select only strongest charts for demo |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 38 — Demo video preparation

**Phase dependency:** Phases 29–37  
**Default phase priority:** P0  
**Phase gate:** 3–5 minute unlisted video covers architecture, preprocessing, labels, results and challenges, and its link works.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-475** | [O] | P0 | Final results/docs available | Define demo story |
| [ ] | **DT-476** | [O] | P0 | Phases 29–37 | Write video structure |
| [ ] | **DT-477** | [O] | P0 | Phases 29–37 | Explain business problem |
| [ ] | **DT-478** | [O] | P0 | Phases 29–37 | Explain Task 1 labels |
| [ ] | **DT-479** | [O] | P0 | Phases 29–37 | Explain Task 1 model architecture |
| [ ] | **DT-480** | [O] | P0 | Phases 29–37 | Show Task 1 result |
| [ ] | **DT-481** | [O] | P0 | Phases 29–37 | Explain Task 2A data construction |
| [ ] | **DT-482** | [O] | P0 | Phases 29–37 | Show demand forecast |
| [ ] | **DT-483** | [O] | P0 | Phases 29–37 | Explain Task 2B bottleneck |
| [ ] | **DT-484** | [O] | P0 | Phases 29–37 | Show final allocation |
| [ ] | **DT-485** | [O] | P0 | Phases 29–37 | Show checker pass |
| [ ] | **DT-486** | [O] | P2 | Phases 29–37 | Show hero feature if completed |
| [ ] | **DT-487** | [O] | P0 | Phases 29–37 | Explain challenges encountered |
| [ ] | **DT-488** | [O] | P0 | Phases 29–37 | Record demo |
| [ ] | **DT-489** | [O] | P0 | Phases 29–37 | Edit to 3–5 minutes |
| [ ] | **DT-490** | [O] | P0 | Phases 29–37 | Upload as unlisted YouTube video |
| [ ] | **DT-491** | [O] | P0 | Phases 29–37 | Verify video URL works while logged out |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 39 — Clean-environment reproduction

**Phase dependency:** Phases 31–38  
**Default phase priority:** P0  
**Phase gate:** A fresh environment can reproduce the notebook, model loading and all three final outputs/checks.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-492** | [E] | P0 | Release candidate frozen | Create completely fresh environment |
| [ ] | **DT-493** | [E] | P0 | Phases 31–38 | Install only from requirements.txt |
| [ ] | **DT-494** | [E] | P0 | Phases 31–38 | Run test suite |
| [ ] | **DT-495** | [E] | P0 | Phases 31–38 | Run final notebook from beginning |
| [ ] | **DT-496** | [E] | P0 | Phases 31–38 | Load saved models |
| [ ] | **DT-497** | [E] | P0 | Phases 31–38 | Reproduce Task 1 predictions |
| [ ] | **DT-498** | [E] | P0 | Phases 31–38 | Reproduce Task 2A predictions |
| [ ] | **DT-499** | [E] | P0 | Phases 31–38 | Reproduce Task 2B allocation/check |
| [ ] | **DT-500** | [E] | P0 | Phases 31–38 | Compare regenerated files with final frozen files |
| [ ] | **DT-501** | [E] | P0 | Phases 31–38 | Fix any environment-specific assumptions |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 40 — Final competition folder

**Phase dependency:** Phase 39  
**Default phase priority:** P0  
**Phase gate:** Final folder contains required deliverables only, with no raw data, secrets or accidental experiment clutter.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-502** | [E] | P0 | DT-492–DT-501 | Create clean final folder |
| [ ] | **DT-503** | [O] | P0 | Phase 39 | Add final notebook |
| [ ] | **DT-504** | [O] | P0 | Phase 39 | Add saved models |
| [ ] | **DT-505** | [O] | P0 | Phase 39 | Add submission_task1.csv |
| [ ] | **DT-506** | [O] | P0 | Phase 39 | Add submission_task2a.csv |
| [ ] | **DT-507** | [O] | P0 | Phase 39 | Add submission_task2b.csv |
| [ ] | **DT-508** | [O] | P0 | Phase 39 | Add preprocessing document |
| [ ] | **DT-509** | [O] | P0 | Phase 39 | Add architecture diagrams |
| [ ] | **DT-510** | [O] | P0 | Phase 39 | Add Task 2B policy |
| [ ] | **DT-511** | [O] | P0 | Phase 39 | Add AI disclosure |
| [ ] | **DT-512** | [E] | P0 | Phase 39 | Add any supporting documentation required for understanding |
| [ ] | **DT-513** | [O] | P0 | Phase 39 | Remove raw competition datasets from submission unless explicitly required |
| [ ] | **DT-514** | [E] | P0 | Phase 39 | Remove temporary experiment artifacts |
| [ ] | **DT-515** | [E] | P0 | Phase 39 | Remove secrets/local paths |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 41 — Final competition validation

**Phase dependency:** Phase 40  
**Default phase priority:** P0  
**Phase gate:** Line-by-line final validation passes after the release candidate is frozen.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-516** | [O] | P0 | DT-502–DT-515 | Review requirements checklist line-by-line |
| [ ] | **DT-517** | [O] | P0 | Phase 40 | Re-check exact filenames |
| [ ] | **DT-518** | [O] | P0 | Phase 40 | Re-check exact CSV columns |
| [ ] | **DT-519** | [O] | P0 | Phase 40 | Re-check exact IDs |
| [ ] | **DT-520** | [O] | P0 | Phase 40 | Re-run Task 2B official checker |
| [ ] | **DT-521** | [O] | P0 | Phase 40 | Re-run final notebook |
| [ ] | **DT-522** | [O] | P0 | Phase 40 | Re-test model loading |
| [ ] | **DT-523** | [O] | P0 | Phase 40 | Proofread preprocessing document |
| [ ] | **DT-524** | [O] | P0 | Phase 40 | Proofread Task 2B policy |
| [ ] | **DT-525** | [O] | P0 | Phase 40 | Proofread AI disclosure |
| [ ] | **DT-526** | [O] | P0 | Phase 40 | Verify architecture diagrams readable |
| [ ] | **DT-527** | [O] | P0 | Phase 40 | Verify YouTube link |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


### Phase 42 — Packaging and submission

**Phase dependency:** Phase 41  
**Default phase priority:** P0  
**Phase gate:** `TeamName_Datathon.zip` is valid, backed up, submitted successfully and submission evidence is retained.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-528** | [O] | P0 | DT-516–DT-527 | Name final directory correctly |
| [ ] | **DT-529** | [O] | P0 | Phase 41 | Compress as TeamName_Datathon.zip |
| [ ] | **DT-530** | [E] | P0 | Phase 41 | Open ZIP locally |
| [ ] | **DT-531** | [E] | P0 | Phase 41 | Verify every required file exists inside ZIP |
| [ ] | **DT-532** | [E] | P0 | Phase 41 | Extract ZIP to fresh location |
| [ ] | **DT-533** | [E] | P0 | Phase 41 | Verify files are not corrupted |
| [ ] | **DT-534** | [E] | P0 | Phase 41 | Keep local backup |
| [ ] | **DT-535** | [E] | P0 | Phase 41 | Keep second backup |
| [ ] | **DT-536** | [O] | P0 | Phase 41 | Upload through Datathon submission form |
| [ ] | **DT-537** | [O] | P0 | Phase 41 | Verify upload completed |
| [ ] | **DT-538** | [E] | P0 | Phase 41 | Keep submission confirmation/evidence |
| [ ] | **DT-539** | [E] | P0 | Phase 41 | Do not modify final frozen submission afterward |

**Phase complete:** [ ]  
**READY FOR NEXT PHASE:** NO


---

## 11. Global stop conditions

Stop downstream work and resolve the issue if any of the following occurs:

- official task interpretation is unresolved;
- required file/schema/key is missing or inconsistent;
- Task 1 route join cardinality is not proven;
- Task 1 label unit tests fail;
- leakage is detected or prediction-time availability is uncertain;
- Task 2A order counting/requested-week aggregation is inconsistent;
- Task 2A validation uses future demand information;
- Task 2B trip-time implementation disagrees with the official formula/example;
- any Task 2B hard rule fails;
- organizer `check_allocation.py` fails;
- official template identifiers/order/schema change unexpectedly;
- saved models cannot be loaded or inference differs unexpectedly;
- raw/private competition data is staged for public sharing;
- final notebook depends on hidden state;
- final ZIP fails extraction/validation.

When blocked, document: `issue → affected task(s) → evidence → decision/fix → retest result`.

---

## 12. Progress-control rules

- Update this file at the end of every development session.
- Mark a phase complete only when its phase gate is satisfied.
- Keep `READY FOR NEXT PHASE: NO` until the gate is verified.
- A future phase MD can contain more detail but cannot mark a task complete on its own; completion must be reflected here.
- If a P2/P3 enhancement threatens deadline or P0/P1 stability, stop it immediately.
- If a later discovery invalidates an earlier `[x]` task, revert it to `[ ]` or `[!]` and re-open dependent work.

---

## 13. Recommended daily decision log format

```markdown
### YYYY-MM-DD — Decision
- Related tasks: DT-xxx, DT-yyy
- Question:
- Evidence:
- Decision:
- Why:
- Alternative rejected:
- Downstream impact:
- Retest required: YES / NO
```

---

## 14. Future phase-file request template

Use this when generating the next phase guide:

```text
Create the full implementation MD for Phase <N> — <NAME> from the finalized WayLoom Datathon Master Plan.
Cover every task ID in that phase and do not omit or renumber tasks.

For every task include:
- Task ID and name
- Official / Engineering / Competitive marking
- Priority
- Objective
- Why it matters
- Official rule or assumption
- Prerequisites/dependencies
- Input files and required columns
- Output files/artifacts
- Files/folders to create or modify
- Files not to modify
- Detailed implementation steps
- Exact formulas/logic where applicable
- Edge cases
- Data validation checks
- Unit/integration tests
- Expected output
- Definition of Done
- Common mistakes
- STOP CONDITIONS
- Git branch name
- Suggested commit message
- Ready-to-copy Cursor implementation prompt
- Ready-to-copy Codex implementation prompt
- Separate review/audit prompt

End with:
- Phase completion checklist
- Phase Completion Report template
- READY FOR NEXT PHASE = YES/NO gate

Base official rules on the Challenge Booklet and keep our proposed methods clearly labelled as recommendations.
Do not use or expose private competition data in prompts.
```

---

## 15. Final release checklist summary

Before submission, at minimum verify:

- [ ] Task 1 labels match official definitions.
- [ ] No Task 1 actual-future leakage exists.
- [ ] `submission_task1.csv` has exact IDs, row order and valid numeric outputs.
- [ ] Task 2A uses both required source files and requested order week.
- [ ] Deferred/not-run orders are included in Task 2A demand.
- [ ] Style and Tech chilled forecasts are exactly zero.
- [ ] `submission_task2a.csv` has exact row IDs and `0 ≤ chilled ≤ total`.
- [ ] Task 2B uses only available S1 vehicles and `order_ref` as allocation key.
- [ ] All seven Task 2B rules pass independently.
- [ ] `check_allocation.py` passes.
- [ ] `submission_task2b.csv` has no placeholders.
- [ ] Task 2B written prioritization policy explains calculations, limiting resources, unavoidable deferrals, chosen deferrals and impact.
- [ ] Required saved models are present and load successfully.
- [ ] `TeamName_FinalNotebook.ipynb` runs from a clean kernel.
- [ ] Final notebook loads saved models and demonstrates Task 1/2A inference.
- [ ] Architecture diagrams match final implementation.
- [ ] Preprocessing document is complete.
- [ ] AI-tool disclosure is complete and accurate.
- [ ] 3–5 minute unlisted demo video link works.
- [ ] No private raw competition data/secrets are inside public repos or final package unless explicitly required/authorized.
- [ ] Clean-environment reproduction passes.
- [ ] `TeamName_Datathon.zip` opens and contains every required deliverable.
- [ ] Upload is complete before the official deadline and confirmation evidence is retained.

---

## 16. Registry integrity

This master plan is intended to contain every finalized development task from **DT-000 through DT-539** exactly once. When editing the registry, run a simple ID audit or manually verify that no ID has been skipped, duplicated or renumbered.

**Current expected task count: 540.**

---

_End of central master plan._
