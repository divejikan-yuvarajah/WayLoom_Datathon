# WAYLOOM DATATHON MASTER PLAN

> **Central source of truth for the WayLoom Datathon workstream — Rootcode Tech-Triathlon 2026**
>
> **Status:** Active working plan  
> **Official Datathon deadline:** Friday, 9 October 2026, 11:59 PM Sri Lanka time (Day 15)  
> **Scope:** Datathon only. Designathon/Hackathon integration is optional and must not block submission.  
> **Task registry:** DT-000 through DT-539 — 540 tasks, sequential, unique  
> **Phase registry:** Phase 00 through Phase 42 — 43 phases, continuous

This file is the **single master control document** for the entire WayLoom Datathon development lifecycle. Future phase Markdown files, notebooks, prompts, and code may add detail. They must not silently override this plan or any official organizer rule.

---

## Document map

1. Purpose of the master plan
2. Source hierarchy
3. Official / Engineering / Competitive legend
4. Priority definitions
5. Status conventions
6. Non-negotiable competition contract
7. Task 1 official rules
8. Task 2A official rules
9. Task 2B official rules
10. Competition restrictions
11. Required final deliverables
12. Recommended repository structure
13. Data-safety rules
14. Execution rules
15. Git branching and commit guidance
16. Phase dependency rules
17. Phase gates
18. Global STOP CONDITIONS
19. Rules for updating task statuses
20. Decision-log template
21. Master execution order
22. Instructions for future Phase MD files
23. Required structure of future Phase MD files
24. Phase-completion report rules
25. Master task registry (Phase 00–42 / DT-000–DT-539)
26. Final release/submission checklist
27. Registry-integrity section

---

## 1. Purpose of the master plan

This file is the **central source of truth** for WayLoom Datathon planning, execution, review, and submission.

Use it to:

- see every required, recommended, and optional development task in one place;
- track status with checkboxes;
- distinguish organizer requirements from WayLoom engineering choices and optional competitive enhancements;
- enforce phase dependencies, phase gates, and stop conditions;
- prevent accidental scope drift into Hackathon/Designathon work;
- coordinate future phase-specific `.md` implementation guides;
- keep official datasets and private derivatives out of Git and out of this document;
- ensure the final package is reproducible, auditable, and competition-compliant.

**Conflict rule:** if a future phase document, coding-agent suggestion, notebook experiment, or implementation conflicts with an explicit official competition rule, the official rule wins. If two internal documents conflict, this master plan controls until it is deliberately updated. If an organizer clarification contradicts this plan, record the clarification in the decision log and update this file.

**This task is documentation/planning only.** Completing or updating this file does **not** authorize Phase 00 execution, modelling, data processing, or submission generation.

---

## 2. Source hierarchy

Authority is strictly ordered. Lower sources may add method and sequencing. They may not invent or override organizer requirements.

1. **Official Rootcode Tech-Triathlon 2026 Challenge Booklet** — highest authority for Datathon problem statements, restrictions, deliverables, judging, deadline, and data-reference conventions.
2. **Official supplied datasets, submission templates, and `check_allocation.py`** — executable/data-level authority for filenames, identifiers, schemas, and Task 2B feasibility checks.
3. **WayLoom Product & Competition Master Plan** — internal cross-phase interpretation and team agreement. Binding for WayLoom execution only where it does not contradict sources 1–2.
4. **Finalized WayLoom Datathon task inventory DT-000 through DT-539** — complete development work breakdown used to populate this registry.
5. **This Datathon Master Plan** — Datathon execution source of truth for sequencing, status, and engineering method.
6. **Future phase/task `.md` files** — implementation-level instructions. They may add detail but must not silently change this master plan or official rules.
7. **Notebooks, code comments, prompts, and experiments** — lowest authority unless promoted into documentation.

Do **not** invent organizer requirements. If a rule is not in sources 1–2, mark it **[E]** or **[C]** and say so.

---

## 3. Official / Engineering / Competitive legend

| Mark | Meaning | How to treat it |
|---|---|---|
| **[O] Official** | Explicit organizer requirement, rule, output, restriction, schema, or required deliverable from the Challenge Booklet, official templates, official datasets, or `check_allocation.py`. | Non-negotiable unless the organizer clarifies otherwise. |
| **[E] Engineering** | WayLoom implementation/reliability recommendation needed to execute the official task safely. | Strong default; change only with a documented reason. Must not contradict [O]. |
| **[C] Competitive** | Optional enhancement intended to improve differentiation, explainability, or presentation. | Never allow it to delay a P0 official deliverable. First items to cut under time pressure after P3 experiments. |

A task marked **[O]** may still have an **[E]** implementation method. The official *requirement* is frozen; the *method* remains a recommendation unless the booklet or checker specifies it.

---

## 4. Priority definitions

| Priority | Meaning |
|---|---|
| **P0** | Essential for correctness, compliance, or a valid submission. Must be completed. |
| **P1** | High-impact engineering/model quality work. Complete after P0 in that stream is stable. |
| **P2** | Competitive enhancement or useful-but-not-blocking quality work. Implement only when P0/P1 are healthy. |
| **P3** | Experimental/optional. First items to cut under time pressure. |

**Priority rule:** P0 before P1; P1 before P2/P3. Optional work never blocks official outputs.

Some environment tasks in the original inventory were P1 (configuration, logging, reproducibility notes). This master plan elevates DT-020–DT-022 to **P0** as an **[E]** sequencing choice so the repository is reproducible before data work. That elevation is internal, not an organizer requirement.

---

## 5. Status conventions

| Checkbox | Meaning |
|---|---|
| `[ ]` | Not started |
| `[~]` | In progress — use if the Markdown viewer supports it; otherwise keep `[ ]` and add `(IN PROGRESS)` |
| `[x]` | Completed **and verified** against the phase Definition of Done / tests |
| `[!]` | Blocked — write the blocking issue beside the task |

A task is **not** complete merely because code exists. Mark `[x]` only after its Definition of Done and required tests/checks are satisfied in the corresponding phase guide.

Phase-level status:

- **Phase complete:** `[ ]` until the phase gate is satisfied.
- **READY FOR NEXT PHASE:** `NO` until the gate is verified. Change to `YES` only in this file after the phase-completion report is filled.

---

## 6. Non-negotiable competition contract

The Datathon is judged separately from the Hackathon. Teams are **not required** to integrate Datathon solutions into the Hackathon build. Optional integration must not expose restricted data and must not delay Datathon submission.

Complete **two prediction tasks** and **one peak-day allocation task**:

| Task | Official objective | Official output file |
|---|---|---|
| Task 1 | Predict outlet handling minutes and lateness probability for each test `delivery_id` | `submission_task1.csv` |
| Task 2A | Forecast depot+brand weekly total and chilled volume for the supplied 10 future weeks | `submission_task2a.csv` |
| Task 2B | Produce a feasible S1 Peliyagoda allocation plus a written prioritization policy | `submission_task2b.csv` + written policy |

Clock times in official data use **HH:MM in Asia/Colombo**. Durations are in minutes.

The detailed official rules follow in sections 7–11. The frozen Task 1 label equations in section 7 are the WayLoom execution contract derived from the booklet; see the conflict note in section 27 if an organizer clarification appears.

---

## 7. Task 1 official rules

**Official source:** Challenge Booklet Datathon Task 1, data-reference pages, and submission template `submission_task1.csv`.

### 7.1 Booklet requirements [O]

- Predict, for every planned test `delivery_id`:
  - `pred_service_min` — predicted handling time at the outlet, in minutes;
  - `pred_late_prob` — probability the delivery arrives after the outlet’s delivery window has closed, in `[0, 1]`.
- Neither target is supplied as a label. Construct training labels from the dataset using column descriptions. Correct label construction is part of the assessment.
- Outlets receive goods only within their delivery window. A vehicle that arrives early waits until the window opens.
- A late arrival is still delivered in the supplied scenario. Lateness refers to **arrival after the window closes**.
- At prediction time, planned departure, travel duration, and arrival are available. **Actual journey and handling times are available only in the training route records.**
- Test inputs: `task1_test_inputs.csv` (one row per order) and `route_legs_test.csv` (matching planned route legs). Every test `delivery_id` matches exactly one route leg.
- Use relevant Training Data and General Data. The challenge does **not** prescribe a feature set.
- Complete `submission_task1.csv`. **Keep `delivery_id` values and original row order exactly as supplied.** Do not add or remove rows. Fill only the two prediction columns.

### 7.2 Official join convention [O]

- Training: each **dispatched** order is delivered as its own stop where `route_id` + `seq_in_route` in `deliveries_train.csv` match exactly one route leg (`route_id` + `seq`) in `route_legs_train.csv`.
- `seq_in_route` / `seq` start at 0.
- Actual times (`actual_depart_time`, `actual_travel_duration_min`, `arrival_time`, `leave_outlet_time`) appear **only** in training route records.

### 7.3 Frozen official-label contract for WayLoom execution [O]

The booklet requires labels to be constructed from historical actuals and states the wait-until-window-open and lateness-after-window-close rules. It does **not** print algebraic equations. The WayLoom Product & Competition Master Plan freezes the following as the binding Task 1 label contract unless the organizer contradicts it:

- Build labels **only** from historical actual route data for dispatched orders with usable actuals.
- `service_start = max(actual arrival, window opening)`
- `service_min = leave_outlet_time - service_start`
- `late_flag = 1` **only** when actual arrival is **strictly after** `window_close_time`; otherwise `0`
- No actual future journey/handling information may be used as prediction features
- Preserve Task 1 `delivery_id` values and original row order

### 7.4 Official Task 1 submission schema [O]

| Column | Type | Required value |
|---|---|---|
| `delivery_id` | string | Supplied identifier. Keep unchanged. |
| `pred_service_min` | number | Predicted outlet handling time, minutes. |
| `pred_late_prob` | number from 0 to 1 | Probability of arrival after window close. |

---

## 8. Task 2A official rules

**Official source:** Challenge Booklet Datathon Task 2A, calendar reference, and submission template `submission_task2a.csv`.

### 8.1 Booklet requirements [O]

- Forecast volume ordered for each depot and brand over the **10 future weeks** in `task2a_test_inputs.csv`.
- Predict two values per depot + brand + week:
  - `pred_total_volume_m3` — total order volume, cubic meters;
  - `pred_chilled_volume_m3` — chilled portion of that total, cubic meters.
- Do **not** convert volumes into vehicle or driver requirements.
- **Build training data from both `deliveries_train.csv` and `task1_test_inputs.csv`.** Each row is one order identified by `delivery_id`.
- **Count every order once, including orders that were deferred or never dispatched.** They still represent demand.
- **Assign each order to the week the store requested the order.**
- **Use `iso_year` and `iso_week` from `calendar.csv`** so forecast periods match the supplied calendar.
- **Only Fresh has chilled demand. Set `pred_chilled_volume_m3` to exactly `0` for Style and Tech.**
- Complete `submission_task2a.csv`. Preserve supplied `row_id` values and fill the two prediction columns.

### 8.2 Frozen WayLoom reading of “requested week” [O]

The booklet says “the week the store requested the order.” The order-record column `order_date` is defined as “the date the store's order was for.” `dispatch_date` is the date the order was dispatched and is blank if it never ran.

WayLoom therefore freezes:

- use requested **`order_date`**, not later **`dispatch_date`**;
- join that date to `calendar.csv` ISO year/week.

If an organizer clarification names a different date column, the clarification wins.

### 8.3 Official Task 2A submission schema [O]

| Column | Type | Required value |
|---|---|---|
| `row_id` | string | Supplied identifier. Keep unchanged. |
| `pred_total_volume_m3` | number | Total demand volume for depot, brand, and week, m³. |
| `pred_chilled_volume_m3` | number | Chilled volume within that total. Use `0` for Style and Tech. |

Engineering checks that support the official schema, but are not printed as booklet formulas: predictions should be finite and non-negative; chilled should not exceed total. Treat those as **[E]** guards around an **[O]** template.

---

## 9. Task 2B official rules

**Official source:** Challenge Booklet Datathon Task 2B, peak-day data reference, submission template `submission_task2b.csv`, and `check_allocation.py`.

This task does **not** require a trained model. There is **no single correct allocation**. Judges assess **feasibility** and the **reasoning** behind decisions. `check_allocation.py` verifies feasibility, **not** allocation optimality.

### 9.1 Scenario and fleet [O]

- Scenario is **S1**.
- Depot is **Peliyagoda**.
- Use only vehicles marked **`available`**.
- Vehicles with status **`in_workshop` cannot be used**.
- Use **`order_ref` as the allocation key** because `outlet_id` may appear more than once.
- Keep `scenario`, `order_ref`, and `outlet_id` unchanged.
- Every order must be **`served` or `deferred`**.
- Served orders receive `vehicle_id` and `trip_id` (`1` or `2`).
- Deferred orders have **blank** `vehicle_id` / `trip_id`.
- Replace every placeholder in the template.

**Executable spelling:** `check_allocation.py` requires decision values exactly `served` or `deferred` (lowercase). Follow the checker and the booklet’s completed example, not title-case wording that appears in one booklet table cell.

### 9.2 Seven official feasibility rules [O]

1. **Brand and district.** All orders sharing a `vehicle_id` and `trip_id` must belong to the same brand and district.
2. **Refrigeration.** Orders with `temp_requirement = chilled` require a vehicle with `temp = reefer`. Refrigerated vehicles may also carry ambient orders.
3. **Vehicle access.** Outlets with `parking_constraint = van_only` require a vehicle with `type = van`.
4. **Home depot.** A vehicle may serve only outlets assigned to its own depot.
5. **Whole orders.** Assign each served order to one vehicle and one trip. Do not split an order across trips or vehicles.
6. **Capacity.** For each trip, total `order_volume_m3` must not exceed `volume_cap_m3`, **and** total `order_weight_kg` must not exceed `weight_cap_kg`.
7. **Trips and time.** Each vehicle may run **at most two trips in total**. Fresh total trip minutes per vehicle **≤ 270**. Style + Tech combined minutes per vehicle **≤ 480**. These are separate windows. A vehicle may run one Fresh trip and one Style/Tech trip, each against its own budget, but still only two trips total.

### 9.3 Official trip-duration formula [O]

Do **not** add a return-to-depot leg. The stated budgets already allow for it.

```text
trip_minutes =
    depot_to_district_freeflow_min                  # once per trip
  + inter_stop_freeflow_min × (number of orders - 1)
  + sum of service_allowance_min for each order     # lookup by brand + dock_type
```

Booklet worked example (planning standard, not live data): a Fresh trip to Gampaha with three orders (two rear docks, one street) is `37 + 9×(3−1) + 15 + 15 + 16 = 101` minutes.

`check_allocation.py` implements the same published planning standard:

```text
trip_time = depot_to_district_freeflow_min
          + (n_orders - 1) * inter_stop_freeflow_min
          + sum(service_allowance_min for each dock on the trip)
```

Time budgets in the checker: `TRIP_BUDGET_PREDAWN = 270` (Fresh), `TRIP_BUDGET_DAYTIME = 480` (Style+Tech combined), `MAX_TRIPS_PER_VEHICLE = 2`.

### 9.4 Official Task 2B submission schema [O]

| Column | Type | Required value |
|---|---|---|
| `scenario` | string | Supplied identifier; always S1. |
| `order_ref` | string | Supplied order identifier and allocation key. |
| `outlet_id` | string | Supplied outlet identifier, included for readability. |
| `decision` | string | `served` or `deferred` for every order. |
| `vehicle_id` | string | Assigned vehicle for a served order. Leave blank if deferred. |
| `trip_id` | 1 or 2 | Assigned trip for a served order. Leave blank if deferred. |

Checker required columns: `scenario`, `order_ref`, `decision`, `vehicle_id`, `trip_id`. Keep `outlet_id` anyway because the official template and booklet require it.

### 9.5 Written prioritization policy [O]

Submit a write-up of approximately one page or less. Show the calculations behind the allocation. Identify what limited service on this day. Explain which deferrals were unavoidable, which were policy choices, and what they cost.

### 9.6 Checker versus optimality [O]

Passing `check_allocation.py` confirms feasibility, not that the allocation is optimal. Judges assess prioritization and deferral explanations.

**Checker note [E]:** if a deferred row names a vehicle or trip, the official script currently **warns** and ignores those fields rather than failing. Follow the booklet anyway: leave them blank.

---

## 10. Competition restrictions

**Official source:** Challenge Booklet “Rules and Regulations” and “Terms and Conditions” for the Datathon.

| Restriction | Official rule |
|---|---|
| Deadline | The submission form closes after the deadline. Submit by Friday, 9 October 2026, 11:59 PM Sri Lanka time. |
| Pretrained models | Restricted from using any pre-trained models, **except** for synthetic data generation or pre-processing. |
| APIs | Proprietary API-based modelling/preprocessing is prohibited. |
| Low-code / no-code | Usage of low-code/no-code AI tools or fully automated end-to-end modelling tools is strictly prohibited. |
| Integrity | Cheating, plagiarism, or rule violations will result in disqualification. |
| Use of data | Provided datasets may be used solely for this competition. Commercial, academic, or personal reuse is prohibited. |
| Data sharing | Datasets must not be shared, distributed, or transmitted in any form — publicly or privately — to any third party, including upload to external websites, forums, or social media. |
| Publication | Do not publish, disclose, or make the datasets or any derivatives publicly available unless explicitly authorized by the organizers. |
| Confidentiality | Maintain confidentiality of the datasets and sensitive information contained in them. |
| AI disclosure | Explain which work was AI-assisted, which was not, and how tools were used. |

**Engineering reading of the pretrained exception:** locally training CatBoost/LightGBM/sklearn models on official competition data is allowed. Shipping a model pretrained on external corpora as the Datathon predictor is not, except where the booklet’s preprocessing/synthetic-data exception applies. Do not use prohibited automated modelling platforms.

---

## 11. Required final deliverables

**Official source:** Challenge Booklet Datathon deliverables and submission instructions.

Place all deliverables in one folder, compress as `TeamName_Datathon.zip`, and upload through the Datathon submission form.

| Deliverable | Official requirement |
|---|---|
| Architecture diagrams | Show models, preprocessing pipeline, and proposed deployment approach. High-level diagrams are sufficient. |
| Data preprocessing document | Brief write-up of data preparation, label construction, data cleaning, feature engineering, and rationale. |
| Saved final model files | Save final model files alongside the notebook. |
| `TeamName_FinalNotebook.ipynb` | Retain cells used for label construction, preprocessing, training, and evaluation. Add a **final cell that loads the saved models**, demonstrates inference for Task 1 and Task 2A, and clearly prints inputs and predictions. |
| `submission_task1.csv` | Exact template columns and identifiers; original Task 1 row order. |
| `submission_task2a.csv` | Exact template columns and identifiers. |
| `submission_task2b.csv` | Exact template columns and identifiers; no placeholders. |
| Task 2B written prioritization policy | Approximately one page or less; calculations, limiting resources, unavoidable vs chosen deferrals, and cost/impact. |
| AI-tool disclosure | Which work was AI-assisted, which was not, and how tools were used. |
| 3–5 minute unlisted demo video | Unlisted YouTube video explaining model architecture, preprocessing, label construction, and challenges encountered. |
| Final `TeamName_Datathon.zip` | One compressed folder containing the Datathon deliverables. |

### Official judging criteria [O]

| Criterion | Weight |
|---|---|
| Data wrangling and label construction | 20% |
| Model and architecture implementation | 25% |
| Performance score (Task 1, Task 2A) | 20% |
| Task 2B allocation feasibility and prioritization policy | 15% |
| Creativity of the solution | 10% |
| Demo video | 10% |

---

## 12. Recommended repository structure

This layout is **[E] Engineering**. Folder names may be adjusted, but data-safety boundaries and the separation of Task 1, Task 2A, and Task 2B must remain clear.

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
│   ├── README.md                 # explains local-only placement; no data
│   ├── raw/                      # PRIVATE / NEVER COMMIT
│   ├── interim/                  # PRIVATE DERIVATIVES / NEVER PUBLIC
│   └── processed/                # PRIVATE DERIVATIVES / NEVER PUBLIC
│
├── docs/
│   ├── 00_MASTER_INDEX.md
│   ├── competition_contract.md
│   ├── preprocessing.md
│   ├── task2b_policy.md
│   ├── ai_tool_disclosure.md
│   ├── integration_contract.md   # optional
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
│   ├── task1/
│   ├── task2a/
│   └── task2b/
│
├── models/
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

Until Phase 01 creates the runtime repository layout, this planning file may live under `MD Files/`. After DT-019, keep one canonical copy of this master plan at the repository root (or a clearly linked path) so it remains the source of truth.

---

## 13. Data-safety rules

These rules combine **[O] official dataset terms** with **[E] WayLoom handling practice**.

1. Official competition datasets may be used **only** for this competition.
2. Do **not** share, distribute, or transmit official datasets or derivatives to any third party.
3. Do **not** upload official datasets, private extracts, or row-level derivatives to GitHub, Gists, Google Drive public links, chatbots, public notebooks, Discord, or other external services unless the organizers explicitly authorize it.
4. Do **not** commit `data/raw/`, `data/interim/`, `data/processed/`, or any CSV that contains official competition rows.
5. `.gitignore` must ignore raw data, interim data, processed data, `.env`, virtualenvs, and notebook checkpoints.
6. **This master plan must not contain official competition datasets or private derivatives.** No raw rows, no sampled records, no reconstructed tables of live competition values.
7. Local data dictionaries may list **column names, types, and file purposes**. They must not paste live values.
8. Prompts sent to Cursor/Codex/other tools must not include raw competition rows.
9. Optional WayLoom product integration may use **schemas and synthetic/demo records only**, unless organizer authorization says otherwise.
10. The final ZIP should not contain raw official datasets unless the organizers explicitly require them. Default: **do not include raw data** in `TeamName_Datathon.zip`.
11. If restricted data is accidentally staged or uploaded, stop, remove it, rotate any exposed secrets, and record the incident in the decision log.

---

## 14. Execution rules

1. **P0 before P1; P1 before P2/P3.** Optional work never blocks official outputs.
2. **Do not start modelling before label/data correctness is verified.** Task 1 modelling is blocked by DT-055–DT-071.
3. **Use time-aware validation. [E]** Never use a random split that lets later operational information leak into earlier validation. The booklet does not prescribe a split; chronological validation is our method.
4. **Treat Task 1, Task 2A, and Task 2B as different technical problems.** Shared utilities are fine; do not force one modelling pattern across them.
5. **Do not silently delete outliers.** Investigate them and document any cleaning decision.
6. **No test-label inference from future actuals.** Any Task 1 feature unavailable before the delivery starts is forbidden for prediction.
7. **Keep official templates immutable except answer columns.** Preserve identifiers and required order.
8. **Use the official Task 2B rules exactly.** Do not substitute wider Hackathon fuel/window logic into the Task 2B validator.
9. **Run an independent validator before the organizer checker.** Passing the checker does not prove a good policy.
10. **Notebook is evidence, not the only implementation.** Important reusable logic belongs in `src/` and is called from the final notebook where practical. **[E]**
11. **Every final model must survive save/load.** The official notebook requirement is to load saved models for Task 1 and Task 2A inference.
12. **All AI usage must remain competition-compliant and disclosed.**
13. **Never expose official private data in a public WayLoom deployment.**
14. **Freeze final artifacts before packaging.** After final validation, changes require re-running all affected checks.
15. **Keep an experiment/decision log.**
16. **Do not continue to later phases while a STOP CONDITION is open.**
17. **Do not implement Datathon code from this planning file alone.** Each phase needs its phase MD, tests, and gate.

---

## 15. Git branching and commit guidance

This entire section is **[E]** except the official data-sharing prohibition, which forbids public commits of restricted data.

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

Keep the repository **private**. Official datasets must never be committed publicly.

---

## 16. Phase dependency rules

1. Phases are numbered **00 through 42** and must remain continuous. Do not skip, merge, or renumber phases without updating this master plan.
2. A phase may start only when every listed **phase dependency** is complete **or** the dependency is explicitly marked optional/non-blocking (Phases 25–28).
3. Task-level dependencies inside a phase are **minimum gates**. A phase MD may add tighter prerequisites; it may not remove a master-plan dependency.
4. Streams may proceed in parallel only where this plan says so:
   - Task 1 core path: Phases 04–10 after Phases 00–03;
   - Task 2A core path: Phases 11–17 after Phases 00–03;
   - Task 2B core path: Phases 18–24 after Phases 00–03;
   - these three streams are independent of each other after the shared data audit;
   - documentation, notebook, packaging: Phases 29–42 after the relevant stream outputs exist.
5. Competitive Phases 25–28 must not block P0 submission work.
6. Later discovery that invalidates an earlier phase gate re-opens that phase and all dependent work.
7. “Phase N” in task-dependency cells means “Phase 0N” for N < 10 (Phase 0 = Phase 00).

---

## 17. Phase gates

A phase is complete only when its gate is true. Summary gates (detail remains in the registry):

| Phase | Name | Depends on | Gate |
|---|---|---|---|
| 00 | Competition understanding and scope freeze | None | Official tasks, formulas, restrictions, outputs, judging, and deadline are documented without ambiguity. |
| 01 | Project environment and repository setup | 00 | Private reproducible repo exists; restricted data paths ignored; dependencies installable. |
| 02 | Raw dataset inventory | 01 | Every supplied file is inventoried, loadable, keyed, and typed at a basic level. |
| 03 | Data-quality audit | 02 | Core integrity assertions pass or every exception is documented. |
| 04 | Task 1 training-data construction | 02–03 | Official service and lateness labels are reproducible and unit-tested. |
| 05 | Task 1 exploratory analysis | 04 | EDA identifies relationships without changing official labels. |
| 06 | Task 1 feature engineering | 04 (05 informs) | Shared train/test schema; no future actual journey fields. |
| 07 | Task 1 validation design | 04–06 | Chronological validation and metrics frozen. |
| 08 | Task 1 baselines | 07 | Simple baselines stored and reproducible. |
| 09 | Task 1 advanced modelling | 08 | Champion models selected with calibration/error analysis. |
| 10 | Task 1 final training and inference | 09 | Saved models and exact `submission_task1.csv` exist. |
| 11 | Task 2A demand-history construction | 02–03 | Weekly panel counts requested orders correctly; Fresh chilled logic preserved. |
| 12 | Task 2A exploratory analysis | 11 | Seasonality/trend understood enough to justify features. |
| 13 | Task 2A forecasting features | 11 (12 informs) | Features are past-known or target-week-known. |
| 14 | Task 2A forecast validation | 11–13 | Rolling-origin ten-week backtesting frozen. **[E] method** around official 10-week forecast. |
| 15 | Task 2A baseline models | 14 | Seasonal/simple baselines exist. |
| 16 | Task 2A advanced forecasting | 15 | Champion approach justified against baselines. |
| 17 | Task 2A final inference | 16 | Exact `submission_task2a.csv` with Style/Tech chilled = 0. |
| 18 | Task 2B scenario understanding | 02–03 | S1 demand and available Peliyagoda fleet understood; workshop excluded. |
| 19 | Task 2B compatibility engine | 18 | Compatible-vehicle sets validated; impossible orders identified. |
| 20 | Task 2B trip calculation engine | 18 | Official trip-minute formula unit-tested against booklet example. |
| 21 | Task 2B priority-policy design | 18–20 | Transparent policy documented separately from hard rules. |
| 22 | Task 2B optimization solver | 19–21 | Feasible allocation exists under all seven hard rules. |
| 23 | Task 2B independent validator | 22 | Independent validator and `check_allocation.py` both pass. |
| 24 | Task 2B output and written policy | 23 | Exact CSV and written policy complete. |
| 25 | Explainability | 09–10 | Explanations accurate; no unsupported causal claims. Optional. |
| 26 | Explainable Deferral Reasoner | 22–24 | If implemented, solver-grounded and non-blocking. Optional. |
| 27 | Optional forecast uncertainty | Task 1/2A models | Unofficial fields stay out of official CSVs. Optional. |
| 28 | Optional WayLoom integration contract | Final outputs | Schemas/synthetic only; no restricted data. Optional. |
| 29 | Architecture documentation | 04–24 | Diagrams match final pipelines and proposed deployment. |
| 30 | Preprocessing document | 04–24 | Required write-up is accurate. |
| 31 | Final competition notebook | 10, 17, 24 | Notebook runs top-to-bottom; final inference loads saved models. |
| 32 | Model artifact management | Final models | Artifacts load and reproduce intended predictions. |
| 33 | Final submission-file testing | 10, 17, 24 | All three official files pass schema/ID/value checks. |
| 34 | General automated testing | Pipelines | Critical rules, labels, inference, constraints covered. |
| 35 | AI-use disclosure | Ongoing | Complete, accurate, restriction-compliant. |
| 36 | README / project documentation | Stable repo | Reviewer can understand and reproduce the workflow. |
| 37 | Results summary and evidence | Final metrics | Strongest evidence selected. |
| 38 | Demo video preparation | 29–37 | 3–5 minute unlisted video; link works logged out. |
| 39 | Clean-environment reproduction | 31–38 | Fresh environment reproduces notebook, models, outputs. |
| 40 | Final competition folder | 39 | Required deliverables only; no raw data/secrets/clutter. |
| 41 | Final competition validation | 40 | Line-by-line validation after freeze. |
| 42 | Packaging and submission | 41 | `TeamName_Datathon.zip` valid, backed up, submitted; evidence retained. |

---

## 18. Global STOP CONDITIONS

Stop downstream work and resolve the issue if any of the following occurs:

- official task interpretation is unresolved;
- required file/schema/key is missing or inconsistent;
- Task 1 route join cardinality is not proven;
- Task 1 label unit tests fail;
- leakage is detected or prediction-time availability is uncertain;
- Task 2A order counting / requested-week aggregation is inconsistent;
- Task 2A validation uses future actual demand information;
- Task 2B trip-time implementation disagrees with the official formula/example or `check_allocation.py`;
- any Task 2B hard rule fails;
- organizer `check_allocation.py` fails;
- official template identifiers/order/schema change unexpectedly;
- saved models cannot be loaded or inference differs unexpectedly;
- raw/private competition data is staged for public sharing or pasted into this document;
- final notebook depends on hidden state;
- final ZIP fails extraction/validation;
- a coding agent is asked to implement an exploit, leak data, or skip official rules.

When blocked, document: `issue → affected task(s) → evidence → decision/fix → retest result`.

---

## 19. Rules for updating task statuses

- Update this file at the end of every development session.
- Mark a task `[x]` only after its phase-MD Definition of Done and tests pass.
- Mark a phase complete only when its phase gate is satisfied.
- Keep `READY FOR NEXT PHASE: NO` until the gate is verified in this file.
- A future phase MD cannot mark a task complete on its own; completion must be reflected here.
- If a P2/P3 enhancement threatens deadline or P0/P1 stability, stop it immediately.
- If a later discovery invalidates an earlier `[x]` task, revert it to `[ ]` or `[!]` and re-open dependent work.
- Do not renumber, skip, or reuse task IDs. If new work appears, attach it as a child of an existing ID or deliberately revise this master plan.
- Status changes that alter official-rule interpretation require a decision-log entry.

---

## 20. Decision-log template

```markdown
### YYYY-MM-DD — Decision
- Related tasks: DT-xxx, DT-yyy
- Official / Engineering / Competitive: [O] / [E] / [C]
- Question:
- Evidence (booklet page, checker behavior, experiment):
- Decision:
- Why:
- Alternative rejected:
- Downstream impact:
- Retest required: YES / NO
```

Keep decision logs in `docs/` or `reports/`. Do not paste restricted data into the log.

---

## 21. Master execution order

```text
Phase 00  Competition contract
    ↓
Phase 01  Environment + secure repo
    ↓
Phase 02  Dataset inventory
    ↓
Phase 03  Data-quality audit
    ↓
    ├── Task 1: 04 labels → 05 EDA → 06 features → 07 validation
    │            → 08 baselines → 09 models → 10 inference
    ├── Task 2A: 11 history → 12 EDA → 13 features → 14 validation
    │            → 15 baselines → 16 models → 17 inference
    └── Task 2B: 18 scenario → 19 compatibility → 20 trip engine
                 → 21 policy → 22 solver → 23 checker → 24 output
    ↓
Phases 25–28  Optional explainability / uncertainty / integration
    (never block P0)
    ↓
Phases 29–30  Architecture + preprocessing documentation
    ↓
Phases 31–34  Final notebook, model files, submission tests, automated tests
    ↓
Phases 35–38  AI disclosure, README, evidence, demo
    ↓
Phases 39–42  Clean reproduction → final folder → validation → ZIP + submit
```

Do **not** give an agent the entire remaining project. Execute one phase (or a tightly coupled task group) at a time.

---

## 22. Instructions for future Phase MD files

A future phase document must be named clearly, for example:

```text
docs/phases/PHASE_04_TASK1_LABEL_CONSTRUCTION.md
```

Rules:

1. Create **one MD per phase** (Phase 00 through Phase 42).
2. Cover **every task ID** from this master plan that belongs to that phase. None may be omitted or renumbered.
3. Quote official rules from this file / the booklet. Label WayLoom method as **[E]** or **[C]**.
4. Include ready-to-copy Cursor and Codex implementation prompts with explicit scope and stop-after-completion instructions.
5. Include a **separate** review/audit prompt. Implementation and review must not be the same prompt.
6. End with a completion checklist, completion report, and `READY FOR NEXT PHASE = YES/NO`.
7. Do not embed official competition rows in prompts or phase files.
8. A phase file may split a task into subtasks, but the master task ID remains the unit of status in this file.
9. If new work is discovered, record it as a child under an existing task or revise this master plan. Do not create hidden side work.

### Phase execution loop

```text
Open phase MD
    ↓
Implement one task or tightly coupled task group
    ↓
Run its tests/validation
    ↓
Review result with the review prompt
    ↓
Update checkbox + decision log in this master plan
    ↓
Proceed only if stop conditions are clear
```

---

## 23. Required structure of future Phase MD files

Every future phase MD **must** contain, in this order or with equivalent headings:

1. **Phase goal**
2. **Official rules** that apply (quoted/paraphrased from booklet + this plan; no invented rules)
3. **Prerequisites** and blocked downstream phases
4. **All task IDs belonging to that phase**
5. For **each task**:
   - Task ID and short name
   - Official / Engineering / Competitive marking
   - Priority
   - **Objective**
   - **Why it matters**
   - **Inputs**
   - **Outputs**
   - **Files to create/modify**
   - **Files not to modify**
   - **Implementation instructions**
   - **Formulas** (or “none”)
   - **Edge cases**
   - **Validations**
   - **Tests**
   - **Definition of Done**
   - **Common mistakes**
6. **STOP CONDITIONS**
7. **Git branch**
8. **Suggested commit**
9. **Cursor implementation prompt**
10. **Codex implementation prompt**
11. **Separate review prompt**
12. **Completion checklist**
13. **Completion report**
14. **READY FOR NEXT PHASE = YES/NO**

---

## 24. Phase-completion report rules

No phase may set `READY FOR NEXT PHASE = YES` without a completion report in the phase MD **and** a matching update here.

Required report fields:

```markdown
# Phase <NN> completion report

- Phase name:
- Date:
- Operator:
- Tasks in phase: DT-xxx to DT-yyy
- Tasks completed [x]:
- Tasks skipped (must be P2/P3 only, with reason):
- Tasks blocked [!]:
- Official rules verified:
- Tests run and results:
- Checker/script evidence (if applicable):
- Artifacts produced (paths only, no data):
- Decision-log entries created:
- Data-safety check (no restricted data committed/uploaded): PASS / FAIL
- Issues found:
- Follow-ups:
- READY FOR NEXT PHASE: YES / NO
```

Rules:

- P0 tasks cannot be skipped.
- If any P0 task is `[!]` or `[ ]`, READY must remain `NO`.
- Competitive phases may report `YES` with skipped P2/P3 work if the skip is explicit and non-blocking.
- Copy the READY flag into this master plan only after the report is filled.

---

## 25. Master task registry

**Checkboxes below are the authoritative project-progress tracker.** Dependencies shown are minimum gates; the corresponding phase `.md` should refine them where necessary.

Each row includes: status checkbox, Task ID, Official/Engineering/Competitive mark, priority, minimum dependency, and short task name.

### Phase 00 — Competition understanding and scope freeze

**Phase dependency:** None  
**Default phase priority:** P0  
**Phase gate:** All official Datathon tasks, formulas, restrictions, outputs, judging criteria and deadline are documented without ambiguity.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [x] | **DT-000** | [O] | P0 | None | Read the official Datathon rules |
| [x] | **DT-001** | [O] | P0 | None | Create competition requirements checklist |
| [x] | **DT-002** | [O] | P0 | None | Separate the three Datathon problems |
| [x] | **DT-003** | [O] | P0 | None | Freeze Task 1 target definitions |
| [x] | **DT-004** | [O] | P0 | None | Freeze Task 2A demand rules |
| [x] | **DT-005** | [O] | P0 | None | Freeze Task 2B seven feasibility rules |
| [x] | **DT-006** | [O] | P0 | None | Freeze Task 2B trip-time formula |
| [x] | **DT-007** | [O] | P0 | None | Freeze official submission file structures |
| [x] | **DT-008** | [O] | P0 | None | Record competition restrictions |
| [x] | **DT-009** | [O] | P0 | None | Record judging criteria |
| [x] | **DT-010** | [O] | P0 | None | Freeze deadline and internal milestones |

**Phase complete:** [x]  
**READY FOR NEXT PHASE:** YES


### Phase 01 — Project environment and repository setup

**Phase dependency:** Phase 0  
**Default phase priority:** P0  
**Phase gate:** A private, reproducible repository exists; raw/restricted data paths are ignored and dependencies are installable.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [x] | **DT-011** | [E] | P0 | Phase 0 | Create project root directory |
| [x] | **DT-012** | [E] | P0 | Phase 0 | Initialize Git repository |
| [x] | **DT-013** | [E] | P0 | Phase 0 | Decide private repository policy |
| [x] | **DT-014** | [E] | P0 | Phase 0 | Create .gitignore |
| [x] | **DT-015** | [E] | P0 | Phase 0 | Create Python virtual environment |
| [x] | **DT-016** | [E] | P0 | Phase 0 | Install required libraries |
| [x] | **DT-017** | [E] | P0 | Phase 0 | Create requirements.txt |
| [x] | **DT-018** | [E] | P0 | Phase 0 | Set random seed policy |
| [x] | **DT-019** | [E] | P0 | Phase 0 | Create repository folder structure |
| [x] | **DT-020** | [E] | P0 | Phase 0 | Create project configuration |
| [x] | **DT-021** | [E] | P0 | Phase 0 | Create logging utility |
| [x] | **DT-022** | [E] | P0 | Phase 0 | Create reproducibility notes |

**Phase complete:** [x]  
**READY FOR NEXT PHASE:** YES


### Phase 02 — Raw dataset inventory

**Phase dependency:** Phase 1  
**Default phase priority:** P0  
**Phase gate:** Every supplied file is inventoried, loadable, keyed and typed at a basic level.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [x] | **DT-023** | [E] | P0 | Phase 1 | Extract DataSet_New.zip |
| [x] | **DT-024** | [E] | P0 | Phase 1 | Inventory every supplied file |
| [x] | **DT-025** | [E] | P0 | Phase 1 | Categorize files |
| [x] | **DT-026** | [E] | P0 | Phase 1 | Load every CSV successfully |
| [x] | **DT-027** | [E] | P0 | Phase 1 | Record row/column counts |
| [x] | **DT-028** | [E] | P0 | Phase 1 | Record all column names |
| [x] | **DT-029** | [E] | P0 | Phase 1 | Generate local data dictionary |
| [x] | **DT-030** | [E] | P0 | Phase 1 | Identify primary keys |
| [x] | **DT-031** | [E] | P0 | Phase 1 | Identify relational joins |
| [x] | **DT-032** | [E] | P0 | Phase 1 | Identify numerical variables |
| [x] | **DT-033** | [E] | P0 | Phase 1 | Identify categorical variables |
| [x] | **DT-034** | [E] | P0 | Phase 1 | Identify date/time variables |
| [x] | **DT-035** | [E] | P0 | Phase 1 | Identify future-known versus future-unknown variables |

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
| [ ] | **DT-222** | [E] | P0 | DT-204–DT-221 | Define rolling-origin validation |
| [ ] | **DT-223** | [E] | P0 | Phases 11–13 | Use 10-week validation windows |
| [ ] | **DT-224** | [E] | P0 | Phases 11–13 | Prevent future-demand leakage |
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
| [x] | **DT-389** | [O] | P0 | Task 1, Task 2A and Task 2B finalized | Create TeamName_FinalNotebook.ipynb |
| [x] | **DT-390** | [E] | P0 | Phases 10,17,24 and documentation state | Add project/problem overview |
| [x] | **DT-391** | [E] | P0 | Phases 10,17,24 and documentation state | Add imports/configuration |
| [x] | **DT-392** | [E] | P0 | Phases 10,17,24 and documentation state | Add data loading |
| [x] | **DT-393** | [E] | P0 | Phases 10,17,24 and documentation state | Add data validation |
| [x] | **DT-394** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 1 label construction |
| [x] | **DT-395** | [O] | P0 | Phases 10,17,24 and documentation state | Add preprocessing cells |
| [x] | **DT-396** | [E] | P0 | Phases 10,17,24 and documentation state | Add EDA summary |
| [x] | **DT-397** | [O] | P0 | Phases 10,17,24 and documentation state | Add feature engineering |
| [x] | **DT-398** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 1 training cells |
| [x] | **DT-399** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 1 evaluation |
| [x] | **DT-400** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 2A aggregation |
| [x] | **DT-401** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 2A training/backtesting |
| [x] | **DT-402** | [O] | P0 | Phases 10,17,24 and documentation state | Add Task 2A evaluation |
| [x] | **DT-403** | [E] | P0 | Phases 10,17,24 and documentation state | Add Task 2B summary/pointer |
| [x] | **DT-404** | [O] | P0 | Saved models available | Add final inference section |
| [x] | **DT-405** | [O] | P0 | DT-412–DT-419 | Load saved models in final cell |
| [x] | **DT-406** | [O] | P0 | Phases 10,17,24 and documentation state | Demonstrate Task 1 inference |
| [x] | **DT-407** | [O] | P0 | Phases 10,17,24 and documentation state | Demonstrate Task 2A inference |
| [x] | **DT-408** | [O] | P0 | Phases 10,17,24 and documentation state | Clearly print inputs and predictions |
| [x] | **DT-409** | [O] | P0 | Phases 10,17,24 and documentation state | Restart kernel and run all |
| [x] | **DT-410** | [E] | P0 | Phases 10,17,24 and documentation state | Remove broken/temporary cells |
| [x] | **DT-411** | [O] | P0 | Phases 10,17,24 and documentation state | Ensure notebook runs without hidden state |

**Phase complete:** [x]
**READY FOR NEXT PHASE:** YES

Phase 31 closure: DT-389–DT-411 remain 23/23 PASS. Human-local clean-kernel Run All (DT-409) and separate fresh-kernel final-cell-only execution (DT-411) passed with zero errors; Task 1 and Task 2A saved-model parity passed. The Phase 31 completion report records the evidence and safeguards. The earlier independent review's formal FAIL reflected then-unfilled records and remains historical. A subsequent fresh read-only independent closure review returned PASS and explicitly authorized these phase-complete and next-phase-readiness updates. Phase 31 is formally closed; this status update does not start Phase 33 implementation.


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

**Phase complete:** [x]
**READY FOR NEXT PHASE:** YES

Phase 33 closure: DT-420–DT-437 are 18/18 PASS. Sanitized human-local validation confirmed all three final submission files, the independent Task 2B validator, the official feasibility checker, unchanged pre/post CSV hashes and no printed private identifiers. A fresh read-only independent Phase 33 review returned PASS, found no blockers and explicitly authorized formal closure. Closure recovery revalidated 80 targeted Phase 33 tests and the Phase 32 registry/checksum, feature-schema, fresh-process load and synthetic-inference gates. Phase 33 is formally closed; this status synchronization does not start Phase 34 implementation.


### Phase 34 — General automated testing

**Phase dependency:** Implemented pipelines  
**Default phase priority:** P1  
**Phase gate:** Automated test suite covers critical data rules, labels, inference and allocation constraints.

| Status | Task | Mark | Pri | Dependency | Work item |
|---|---|---:|---:|---|---|
| [x] | **DT-438** | [E] | P1 | Core modules implemented | Create pytest test suite |
| [x] | **DT-439** | [E] | P1 | Implemented pipelines | Test schemas |
| [x] | **DT-440** | [E] | P1 | Implemented pipelines | Test joins |
| [x] | **DT-441** | [E] | P1 | Implemented pipelines | Test time utilities |
| [x] | **DT-442** | [E] | P1 | Implemented pipelines | Test label generation |
| [x] | **DT-443** | [E] | P1 | Implemented pipelines | Test feature generation |
| [x] | **DT-444** | [E] | P1 | Implemented pipelines | Test Task 1 inference |
| [x] | **DT-445** | [E] | P1 | Implemented pipelines | Test Task 2A aggregation |
| [x] | **DT-446** | [E] | P1 | Implemented pipelines | Test Task 2A forecast output constraints |
| [x] | **DT-447** | [E] | P1 | Implemented pipelines | Test Task 2B compatibility rules |
| [x] | **DT-448** | [E] | P1 | Implemented pipelines | Test Task 2B trip-time formula |
| [x] | **DT-449** | [E] | P1 | Implemented pipelines | Test Task 2B optimizer output |
| [x] | **DT-450** | [E] | P1 | Implemented pipelines | Test saved-model loading |

**Phase complete:** [x]
**READY FOR NEXT PHASE:** YES

Phase 34 closure: DT-438-DT-450 are 13/13 PASS. The fresh independent re-review verified 89 traceability mappings across 87 unique pytest nodes, resolved all five findings from the earlier failed review, confirmed the full safe suite and protected-artifact integrity, found no blockers, and explicitly authorized formal closure. Phase 34 is formally closed; this status synchronization does not start Phase 35 implementation.

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
| [ ] | **DT-486** | [C] | P2 | Phases 29–37 | Show hero feature if completed |
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

## 26. Final release/submission checklist

Before submission, at minimum verify:

- [ ] Task 1 labels match the frozen official-label contract (`service_start`, `service_min`, `late_flag`).
- [ ] No Task 1 actual-future leakage exists.
- [ ] `submission_task1.csv` has exact IDs, original row order, and valid numeric outputs.
- [ ] Task 2A uses both `deliveries_train.csv` and `task1_test_inputs.csv`.
- [ ] Task 2A counts attempted, deferred, and not_run orders.
- [ ] Task 2A uses requested `order_date` / calendar ISO year-week, not `dispatch_date`.
- [ ] Style and Tech chilled forecasts are exactly zero.
- [ ] `submission_task2a.csv` has exact `row_id` values; chilled ≤ total; non-negative finite numbers.
- [ ] Task 2B is scenario S1, Peliyagoda, available vehicles only; workshop vehicles unused.
- [ ] Task 2B uses `order_ref` as the allocation key.
- [ ] Served orders have `vehicle_id` and `trip_id`; deferred rows leave them blank.
- [ ] All seven Task 2B rules pass independently (brand+district, reefer, van_only, home depot, whole orders, weight AND volume, max two trips + time budgets).
- [ ] Trip duration uses free-flow outbound + inter-stop × (n−1) + service allowances, with **no return-to-depot leg**.
- [ ] Fresh ≤ 270 minutes/vehicle; Style+Tech combined ≤ 480 minutes/vehicle.
- [ ] `check_allocation.py` passes. Feasibility is confirmed; optimality is not claimed from the checker.
- [ ] `submission_task2b.csv` has no placeholders.
- [ ] Task 2B written prioritization policy explains calculations, limiting resources, unavoidable deferrals, chosen deferrals, and impact.
- [ ] Architecture diagrams are present and match the final implementation.
- [ ] Preprocessing document is complete.
- [ ] Required saved models are present and load successfully.
- [ ] `TeamName_FinalNotebook.ipynb` runs from a clean kernel.
- [ ] Final notebook loads saved models and demonstrates Task 1/2A inference with printed inputs and predictions.
- [ ] AI-tool disclosure is complete and accurate.
- [ ] 3–5 minute unlisted demo video link works while logged out.
- [ ] No private raw competition data/secrets are inside public repos or the final package unless explicitly required/authorized.
- [ ] Clean-environment reproduction passes.
- [ ] `TeamName_Datathon.zip` opens and contains every required deliverable.
- [ ] Upload is complete before Friday, 9 October 2026, 11:59 PM Sri Lanka time, and confirmation evidence is retained.

---

## 27. Registry-integrity section

This master plan must contain every finalized development task from **DT-000 through DT-539** exactly once, organized under **Phase 00 through Phase 42**.

| Check | Required value |
|---|---|
| First task ID | DT-000 |
| Last task ID | DT-539 |
| Task ID count | **540** |
| Missing IDs | **none** |
| Duplicated IDs | **none** |
| First phase | Phase 00 |
| Last phase | Phase 42 |
| Phase count | **43** |
| Phase numbering | continuous 00, 01, 02, …, 42 |

When editing the registry:

1. Do not skip, reuse, or renumber IDs.
2. Do not add a 44th phase or a 541st task without a deliberate plan revision.
3. Re-run an ID audit (see command below) after any registry edit.
4. If an ID is missing or duplicated, **fix this document before continuing any other work**.

```text
Audit method:
- extract every table row matching **DT-xxx**
- compare against the closed range DT-000 .. DT-539
- extract every heading matching ### Phase NN
- compare against the closed range 00 .. 42
```

### Integrity audit result (this revision)

- File: `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md`
- Total phases: **43** (00–42, continuous)
- Total task IDs: **540** (DT-000–DT-539, unique)
- Missing IDs: **none**
- Duplicated IDs: **none**

### Known source tensions (not registry defects)

These are **not** missing/duplicate IDs. They are conflicts or interpretation gaps between official sources and internal planning. Official sources win.

1. **Task 1 equations are not printed in the booklet.** The booklet requires constructing labels from historical actuals, waiting until window open, and treating lateness as arrival after window close. The algebraic contract `service_start = max(actual arrival, window opening)`, `service_min = leave_outlet_time - service_start`, and `late_flag = 1` only when actual arrival is strictly after `window_close_time` is frozen from the WayLoom Product & Competition Master Plan. It is the binding execution contract unless the organizer contradicts it.
2. **Task 2A “requested week” column.** The booklet says assign demand to the week the store requested the order and to use `calendar.csv` ISO year/week. It does not say “not `dispatch_date`” in those words. WayLoom freezes `order_date` rather than `dispatch_date` because `order_date` is defined as the date the store’s order was for.
3. **Decision capitalization.** One booklet table cell says “Served or deferred.” The completed example and `check_allocation.py` require lowercase `served` / `deferred`. Follow the checker and example.
4. **Deferred vehicle/trip fields.** The booklet requires blanks. `check_allocation.py` currently warns if they are filled rather than failing. Follow the booklet: leave them blank.
5. **Rolling-origin / ten-week backtesting (Phase 14).** The official forecast horizon is 10 weeks. Rolling-origin validation is **[E]**, not a booklet-mandated protocol. DT-222–DT-224 are engineering controls around the official 10-week task.
6. **Pretrained-model exception.** The booklet bans pretrained models *except* for synthetic data generation or pre-processing. Internal phrasing “no prohibited pretrained models” must preserve that exception.
7. **Hackathon fuel/window logic** must not be imported into Task 2B. Datathon Task 2B uses the published free-flow + allowance formula and the 270/480 minute budgets only.
8. **Optional integration (Phase 28)** is internal/competitive. Official rule: Datathon is judged separately and live integration is not required.
9. **Inventory priority vs this plan.** The task inventory listed DT-020–DT-022 as P1. This plan elevates them to P0 as an engineering sequencing choice.

---

_End of central master plan. Do not start Phase 00 execution from this documentation task._
