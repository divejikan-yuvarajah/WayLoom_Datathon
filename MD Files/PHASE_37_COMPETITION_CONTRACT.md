# PHASE 37 — Results Summary and Evidence: Competition Implementation Contract

> **Version:** 2026-10-09 master-reconciled implementation revision | **Status:** PREPARATORY EVIDENCE PACKAGE TECHNICALLY REPAIRED — missing approved evidence, fresh independent review and formal closure remain pending.  
> **Local master-plan verification:** The repository copy of `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` was inspected. Section 4 records the exact eleven DT-464–DT-474 work items, `[E]` marks, P1 priority, `Final metrics/outputs` dependency, and phase gate.  
> **Deadline priority:** Submit only already-authorized official deliverables by **2026-10-09 23:59 Sri Lanka time**; do not let an internal Phase37 reporting enhancement delay official submission or justify omitting required deliverables.  

> **Project:** WayLoom — Rootcode Tech-Triathlon 2026, Datathon track  
> **Canonical repository destination:** `MD Files/PHASE_37_COMPETITION_CONTRACT.md`  
> **Verified task range:** **DT-464 through DT-474 inclusive — eleven task IDs** (confirmed in the supplied `CODEX_HANDOFF_PHASE_11_ONWARDS.md`, phase table).  
> **Master-title evidence:** The exact local master items are reproduced in §4. The more detailed engineering guidance retained in §6 is supporting guidance only and cannot replace or broaden those canonical work items.  
> **Official rule distinction:** The official booklet sets judging criteria and deliverables; it does **not** prescribe a separate Phase 37 results report, any particular metric table/plot, official MAE/RMSE/AUC threshold, or test-set ground truth. Those are proposed WayLoom master-plan/reporting controls, not additional organizer rules.  
> **Verified project gate (2026-10-09):** The local master records Phases **35 and 36 formally CLOSED**. Phase 35 retains the truthful AI-use disclosure, hash-bound human approval and **incident-specific** organizer response; it is not a blanket data-sharing exemption. Phase 37 remains open and Phase 38 has not started.  
> **Deliverable status:** Phase 37 evidence package prepared for fresh independent review; **not a computed private performance score, organizer assessment, formal phase closure, or authorization to submit**.

---

## 1. Purpose, audience, and scope boundaries

Create an evidence-backed, competition-facing **results narrative and traceable evidence index** explaining what the frozen WayLoom Datathon solution achieved, what was measured, on which permitted split and methodology, and what remains unverified. Organizers and technical reviewers must be able to distinguish: (a) *held-out validation/backtest observations*, (b) *official submission-file integrity*, (c) *Task 2B hard-rule feasibility and prioritization*, (d) *safe regression-suite results*, and (e) *future/deployment aspirations*. No assertion may silently change category.

**Candidate files, conditional on local master reconciliation:** `docs/RESULTS_SUMMARY.md`, `docs/RESULTS_EVIDENCE_INDEX.md`, a small *synthetic-only* evidence schema/manifest such as `configs/phase37_results_evidence.yaml`, and `tests/test_phase37_results_evidence.py` (only if fitting repository conventions). Existing sanctioned task evaluation reports or notebook **source code** may be referenced. Reuse them; do not re-train, regenerate or recalculate private metrics within an external agent context. Do not create new private metric exports merely to populate an attractive chart.

**Outputs:** a source-verifiable results overview covering Task 1 service minutes and late probability, Task 2A total/chilled volume and 10-week forecasting, Task 2B S1 feasibility/policy outcomes, known limitations and honest evidence provenance. Clearly label numbers as unavailable if no safe approved aggregate exists. Provide an evidence matrix and executable *synthetic* document QA. Preserve the **approved Phase 35 AI-use disclosure** and its incident-specific organizer-guidance limitations; Phase 37 must not recertify competition compliance or imply a blanket exemption.

### 1.1 Non-goals and decision guardrails

- Not an official leaderboard score, organizer rank, victory claim, production deployment, causal uplift, or new benchmark result.
- Not another training, optimization, hyperparameter selection, calibration, fairness audit or model selection phase.
- Not a public data release. Supplied datasets and their derivatives are confidential unless organizers explicitly authorize publication; competition-facing confidential submission and public repo are different destinations.
- Not a route to falsify, override or reopen the reported Phase 35/36 formal closures or their verified evidence.
- No real row-level content in chat, external agent prompts, README, sample output, generated graphics or tests.
- No external uploading of competition data or private notebooks to make this report. The Phase 35 record already documents prior sharing; **do not repeat** that transmission.

---

## 2. Authority and exact official rules

Read in strict order:

1. `MD Files/Challenge Booklet.pdf` (same content as supplied `Challenge Booklet.pdf`), official Datathon pp. **15–25**, particularly **pp. 15–21 tasks**, **p. 22 rules/deliverables**, **p. 23 judging/submission**, and **p. 25 template/official checker reference**. If local organizer clarification exists, record its verified scope rather than inventing a waiver.
2. **Actual local** `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` — exact DT-464–DT-474 titles, full descriptions, dependencies, priority and closure prerequisites. This is mandatory before mapping work to IDs.
3. Actual local statuses and contracts for Phases **35 and 36**; frozen approved evaluation/training/validation/optimizer artifacts and relevant Phase **24, 29–34** contracts; Phase 32 saved-model registry.
4. Existing source (`src/**`, `scripts/**`, `configs/**`), source-only final notebook, safe `tests/**` and approved **sanitized** prior human reports. Do not inspect private row-level tables, executed notebooks or model predictions.
5. `AGENTS.md`, `CODEX_HANDOFF_PHASE_11_ONWARDS.md`, this provisional phase contract. Engineering proposals never supersede official/master instructions.

### 2.1 Official challenge crosswalk (fact, not invented scoring method)

| Official booklet / printed page | Actual requirement or scoring fact | Required Phase 37 evidence handling |
|---|---|---|
| p.15–16, Task 1 | Predict service time in **minutes** and probability that arrival is **strictly after** delivery-window close; early waiting excluded from handling duration | Separate service-time regression evidence from lateness probability evidence; use correct label definitions and units. |
| p.16, Task 1 template | `delivery_id,pred_service_min,pred_late_prob`; preserve `delivery_id`, row count and **row order** | Report submission integrity via safe checks/hashes, never print real IDs or prediction records. |
| p.17–18, Task 2A | Forecast **10 future weeks** for depot/brand, total and chilled `m3`; include each order once from train + Task 1 test inputs including deferred/not-run, by requested-date ISO year/week; only Fresh chilled | Evaluation must identify horizon/split and metric targets; do not call Style/Tech structural zeros a learned model triumph. |
| p.18, Task 2A template | `row_id,pred_total_volume_m3,pred_chilled_volume_m3`; preserve IDs | Evidence of schema/identity/constraints separate from predictive accuracy. |
| pp.18–21, Task 2B S1 | One-day Peliyagoda served/deferred allocation; assign whole served orders to eligible vehicles/trips; explain priorities, limiting resources and deferrals; no single correct solution | Report feasibility and actual priority policy, not invented unique-optimal claim. Rule checks are different from competition judging. |
| pp.20–21, Task 2B hard rules | Same brand/district per trip; chilled requires reefer; van-only access; home depot; volume/weight capacities; maximum **two trips** total; Fresh combined **270 min**, Style+Tech combined **480 min**; outbound+interstop+service with **no depot return** | Refer to actual independent validator and official checker *status*, retain check provenance and known limitations; show no private rows. |
| p.21–22, Task 2B policy | Approximately one page or less; explain calculations, choices versus unavoidable deferrals and their cost | Cross-link the actual written priority policy and supporting sanitized/approved calculations; no fresh counterfactuals required. |
| p.22, Deliverables | Architecture diagrams, preprocessing write-up, models alongside `TeamName_FinalNotebook.ipynb`, final-cell saved-model Task1+2A demo, Task2B allocation+policy, all three CSVs, unlisted 3–5min video, truthful AI-use disclosure | Include navigational evidence, distinguish *exists*, *locally checked*, *approved*, *pending*. No new official Phase37 document is prescribed. |
| p.22, Rules/Terms | Restricted pretrained models, proprietary modelling/preprocessing APIs, automated AI tools, and non-transmission/non-publication of confidential datasets and derivatives | No private records or unsupported compliance certification; cite the Phase 35 approved disclosure only within its established, incident-specific scope. |
| p.23, Judging criteria | Data wrangling/labels **20%**; model/architecture **25%**; Task1/2A performance **20%**; Task2B feasibility/policy **15%**; creativity **10%**; demo **10%** | Do not turn rubric weights into measured model metrics, claim internal validation predicts leaderboard points, or add invented submetrics. |
| p.23, submission | All deliverables in `TeamName_Datathon.zip`; submission form closes **2026-10-09 23:59 Sri Lanka time** | Phase37 writes no ZIP and performs no upload; deadline increases urgency but never authorizes fabricated evidence. |

**Important:** MAE, RMSE, ROC-AUC, Brier, LogLoss, rolling-origin WAPE, served share or optimization objective components are *possible internally chosen measures only*. Use a measure in the submitted narrative **only if already computed, definition verified and evidence authorized**. No threshold or leaderboard metric is stated in the booklet for those named measures.

---

## 3. Preconditions, evidence integrity and local verification of closed Phase 35/36 gates

**Verified implementation gate (2026-10-09):** the actual local master records **Phase 35** 5/5 complete, phase complete `[x]`, readiness `YES`, and **Phase 36** 8/8 complete, phase complete `[x]`, readiness `YES`. Their supporting records preserve the exact-version disclosure approval, incident-specific organizer-response boundary, repaired README command, and independent-review history. Earlier human-local/private results remain reported evidence and were not rerun. An older Phase 32 master-plan administrative inconsistency is outside Phase 37 and was not modified.

**Gate decision:**

1. Read Phase35/36 master rows, completion notes and Phase37 dependency text verbatim.
2. If both master-plan phase statuses are **formally closed as reported** and the actual Phase 37 dependency is satisfied, implementation may proceed. If any mandatory local gate is actually open or contradictory, **STOP formal DT-464–DT-474 implementation**; produce only clearly labeled `PREPARATORY — GATE BLOCKED` documents if policy permits, without checking task IDs.
3. Proceed only to the extent authorized by the exact local dependency. Do not expand the already approved Phase 35 incident-specific organizer response into a general waiver or claim official eligibility beyond the verified organizer communication.
4. If a conflict between the master and this contract is material, document it and reconcile the contract; never skip a canonical task.
5. The reported organizer's “no worries” is not independently established blanket written clearance. Do not use it as unconditional evidence of compliance.

**Read-only protected and confidential boundaries:**

- Never read or expose content from `data/raw/**`, `data/interim/**`, `reports/private/**`, uploaded data, private executed notebooks, internal prediction samples, real IDs, raw strings, secrets/tokens, organizer correspondence. Use safe *filenames, existence, size and SHA-256 only*, where authorized.
- Frozen files include `outputs/submission_task1.csv`, `outputs/submission_task2a.csv`, `outputs/submission_task2b.csv`, `models/artifact_registry.json`, all **12 registered model/preprocessing artifacts**, `TeamName_FinalNotebook.ipynb`, approved task preprocessing/algorithm source, training configs, Phase24 Task2B policy/allocations. **Never edit or regenerate**.
- No model deserialize, private inference, Task2B real checker, private metric recomputation or official submission writes in AI agent context; use existing provenance or ask an authorized local operator to run *documented* private-only commands, sharing non-sensitive aggregate PASS/FAIL only if permitted. Even aggregate derivatives require suitable authorization for publication; do not treat anonymization as automatic permission.
- Preserve preexisting Git changes; no `git add -A`, no force/reset/clean, commit, push or ZIP/upload in this phase.

### 3.1 Evidence provenance levels and honest reporting

| Evidence label | Meaning | Allowed claim |
|---|---|---|
| `OFFICIAL_RULE` | Text verified from booklet/template/checker | Requirements, not actual performance. |
| `REPO_VERIFIED` | Source/config/test inspected by agent in this run | Implemented method/guard, not real-data execution. |
| `INDEPENDENT_SAFE_TEST` | Reviewer ran synthetic safe tests and has report | Safe code behavior, not private competition score. |
| `HUMAN_LOCAL_REPORTED` | Authorised operator ran private commands and supplied sanitized result | Local check reported PASS, not agent-rerun/organizer-verified. |
| `TRACKED_INTERNAL_AGGREGATE` | A safe aggregate or ranking appears in a tracked internal source, but exact public/demo approval is not recorded | Internal source-backed discussion only; do not select for public release. |
| `SANITIZED_AGGREGATE_APPROVED` | A specific metric has exact definition, split, sample coverage, source hash/provenance and owner approval to disclose | Accurate report number within approved audience. |
| `TEAM_REPORTED` | Team testimony (e.g. organizer communication) with limited provenance | Reported guidance only; not organizer waiver. |
| `UNVERIFIED` | Missing, ambiguous or contradictory evidence | `PENDING`, `NOT MEASURED`, `NOT AVAILABLE` — no invented score. |

**Do not call `pytest passed`, model round-trip PASS, artifact-checksum PASS or Task2B feasibility PASS a predictive validation score.** Submission file validity ≠ accuracy. A synthetic backtest ≠ performance on organizer's withheld labels. Task2B feasibility ≠ unique global optimality.

---

## 4. Exact Phase 37 local-master inventory — eleven IDs

**Phase dependency:** `Final metrics/outputs`  
**Default priority:** P1  
**Phase gate:** “Final evidence includes only the strongest metrics/charts needed to support the technical story.”  
**Status at implementation:** all eleven master checkboxes remain `[ ]`; Phase complete remains `[ ]`; readiness remains `NO` until a fresh independent review and later administrative closure.

| Master ID | Mark | Priority | Dependency | Exact local-master work item |
|---|---:|---:|---|---|
| DT-464 | [E] | P1 | Final metrics/outputs | Produce final Task 1 metrics table |
| DT-465 | [E] | P1 | Final metrics/outputs | Compare Task 1 baseline vs final model |
| DT-466 | [E] | P1 | Final metrics/outputs | Produce calibration visualization |
| DT-467 | [E] | P1 | Final metrics/outputs | Produce Task 1 feature explanation |
| DT-468 | [E] | P1 | Final metrics/outputs | Produce Task 2A backtesting results |
| DT-469 | [E] | P1 | Final metrics/outputs | Compare Task 2A baselines/final model |
| DT-470 | [E] | P1 | Final metrics/outputs | Produce future-demand chart |
| DT-471 | [E] | P1 | Final metrics/outputs | Produce Task 2B scarcity summary |
| DT-472 | [E] | P1 | Final metrics/outputs | Produce served/deferred summary |
| DT-473 | [E] | P1 | Final metrics/outputs | Produce solver/checker evidence |
| DT-474 | [E] | P1 | Final metrics/outputs | Select only strongest charts for demo |

### 4.1 Reconciled acceptance map

| Task | Phase 37 output and evidence boundary |
|---|---|
| DT-464 | A Task 1 metric table with exact metric definitions, units, split provenance and explicit `NOT AVAILABLE` values where no approved aggregate exists. |
| DT-465 | A source-backed model-selection comparison; no numerical uplift claim without an approved result artifact. |
| DT-466 | A calibration-visualization specification and explicit unavailable status; no invented bins or curve. |
| DT-467 | A concise feature explanation grounded in the existing tracked SHAP summary, with association/causality caveats. |
| DT-468 | A Task 2A rolling-origin backtest table and protocol; unavailable numerical cells remain explicit. |
| DT-469 | A source-backed baseline/final comparison and frozen ensemble description; no invented error reduction. |
| DT-470 | A future-demand chart specification; no plot is rendered from confidential or unavailable forecast values. |
| DT-471 | A scarcity summary using only already tracked safe aggregates from `docs/task2b_policy.md`. |
| DT-472 | A served/deferred summary using the same tracked aggregate source and no order identifiers. |
| DT-473 | Solver/checker evidence that distinguishes feasibility from optimality and judge score. |
| DT-474 | A minimal demo-chart shortlist that includes only supported evidence and excludes unavailable calibration/forecast charts. |

The detailed material in §6 predates this reconciliation. It remains useful engineering guidance only where compatible with this exact map. Section 4.1 and the completion record in §12 govern task identity and verdicts.

---

## 5. Shared results/evidence contract and file plan

### 5.1 Candidate deliverables and ownership (verify actual local paths first)

| File | Proposed owner | Contents / prohibited contents |
|---|---|---|
| `docs/RESULTS_SUMMARY.md` | Phase37 primary | Competition-facing narrative, clearly labeled measured/supported metrics or `NOT AVAILABLE`; no real rows. |
| `docs/RESULTS_EVIDENCE_INDEX.md` | Phase37 | Claim-to-source provenance matrix, human/safe distinction, exact metric definitions, access labels. |
| `configs/phase37_results_evidence.yaml` | Phase37 optional | Declarative source *references and validations*, never real values, raw data path lists, secret URIs, unrestricted private report excerpts. |
| `tests/test_phase37_results_evidence.py` | Phase37 optional | Synthetic deterministic documentation/claim/traceability regressions; no private datasets, models or network. |
| Existing approved architecture/preprocessing/final notebook/Task2B policy | **Reference only** | Link, don't overwrite or repackage during this phase. |
| Human-approved private evaluation reports | **Read by authorized human only**, not agent | Human summarizes only disclosure-authorized aggregates and meta evidence without revealing rows or derivatives publicly. |
| `README.md` / judge walkthrough | Phase36 source | If Phase36 exists, cross-link; no speculative links to nonexistent results. |

### 5.2 Standard evidence record template

Use actual existing evidence format if defined; otherwise the following is a **proposed** YAML-like schema, not an official format. Manifest may hold **only safe descriptors**, not raw metrics unless their inclusion is specifically approved:

```yaml
evidence_id: P37-T1-SERVICE-01
claim: "Task 1 service-time validation metric"
task_id: DT-465
provenance_level: UNVERIFIED
measure_name: NOT_AVAILABLE
measure_unit: minutes
metric_definition_ref: "<verified source function/report section>"
validation_method: "<chronological holdout / other verified method>"
source_reference: "<non-sensitive relative source/config path>"
source_sha256: "<approved source or report hash if permitted>"
model_or_run_id: "<non-sensitive frozen run reference>"
verified_by_role: NOT_CONFIRMED
approval_to_disclose: false
intended_audience: competition_reviewers
record_status: PENDING
```

A measured numerical value must have its exact source, split/origin, target, unit, metric formula/version, aggregation, sample coverage (safe), validation vs test distinction, evidence owner, reported timestamp if available and authorization. Do **not** include a sensitive source path, identifying key, private filename token or a real-data example in a public docs index. Evidence paths must be repo-relative, exist, and remain authorized; a human-local report hash may be recorded as hash only if privacy rules permit.

### 5.3 Minimum results-summary outline

1. Purpose, scope, evidence grading and no-leaderboard caveat.
2. Task 1 service: correct label, chosen final model, evaluation setup, source-backed measured metrics or unavailable status.
3. Task 1 lateness: strict-close target, class/probability/calibration policy, separately sourced evaluation, reliability/limitations.
4. Task 2A: demanded volume history construction, ten-week backtest semantics, total/chilled outcomes, structural rules and uncertainty.
5. Task 2B: S1 priorities, coverage, hard-rule feasibility, independent/official checker evidence provenance, tradeoffs and deferred orders rationale.
6. Comparisons/interpretability **only where truly supported** by prior approved evidence.
7. File/claim evidence index with safety labels.
8. Known limitations and blockers: no withheld test labels or unsupported production claims; Phases 35 and 36 reportedly CLOSED, subject to source-of-truth verification; no unverified leaderboard score.
9. Safe reproduction/test guide and links to official deliverables or Phase38 video **only when verified**.

### 5.4 What a metric means (definitions illustrative, NOT already measured)

| Internal metric candidate | Valid report requirement | Common invalid claim |
|---|---|---|
| Task1 MAE (minutes) | Held-out true service label vs final-model predicted service, with exact split/units and n | Calling 766/858 pytest PASS an MAE. |
| Task1 RMSE (minutes) | Same held-out label/prediction alignment; avoid leakage and train metrics | Claiming lower than a benchmark without evidenced benchmark. |
| Late ROC-AUC | Need correct positive late class and held-out **both classes**; no undefined-case score | Reporting AUC for one-class slices or post-hoc test submission without labels. |
| Late Brier/log-loss | Probability calibrated/raw policy must match *frozen* model, correct label/split and valid probabilities | Calling low predicted late probabilities proof of accuracy. |
| Task2A MAE/WMAPE (m3) | Rolling-origin forecast target, depot/brand/horizon aggregation, zero-denominator policy, observed labels | Evaluating forecast ten-week submission with unknown future truth. |
| Task2A chilled metrics | Only Fresh can have chilled; clearly distinguish structural-zero Style/Tech | Treating zero structural labels as predictive success. |
| Task2B served share | Verify order-ref denominator, scenario, counts and access restrictions from authorized validated private evidence | Calling served share an official optimization score. |
| Task2B objective | Use exact Phase21/22 approved lexicographic objective and optimality proof only if logged | Equating `check_allocation.py` feasibility with objective optimality. |

---
## 6. Detailed DT-464–DT-474 implementation contracts

The local master is canonical. Each task below records the deliverable, evidence boundary, acceptance rule and implementation state. A result can be technically prepared while remaining `PREP_ONLY` or `BLOCKED`; no task checkbox is changed before fresh independent review.

### DT-464 — Produce final Task 1 metrics table

- **Deliverable:** the Task 1 table in `docs/RESULTS_SUMMARY.md` plus metric records in `configs/phase37_results_evidence.yaml`.
- **Required semantics:** service MAE/RMSE in minutes; early waiting excluded; late positive class is arrival strictly after close; split and provenance named.
- **Evidence boundary:** `configs/task1_validation.yaml` and `docs/task1_label_spec.md` define the method. Approved numerical aggregates are not present.
- **Acceptance:** each missing number is `NOT AVAILABLE`, never zero or an implied PASS.
- **Implementation state:** `PREP_ONLY`.

### DT-465 — Compare Task 1 baseline vs final model

- **Deliverable:** source-backed baseline/final comparison table.
- **Required semantics:** distinguish configured comparison completion and frozen CatBoost families from measured uplift.
- **Evidence boundary:** `configs/task1_final_models.yaml` records the frozen selections, but the safe tracked package contains no approved numerical comparison.
- **Acceptance:** no invented scores, percentage improvement or withheld-test result.
- **Implementation state:** `PREP_ONLY`.

### DT-466 — Produce calibration visualization

- **Deliverable:** reliability-chart specification with axes, bin counts, split and positive-class definition.
- **Evidence boundary:** no approved calibration-bin table exists in the tracked public evidence.
- **Acceptance:** do not render a curve from private, reconstructed or fabricated values; exclude it from the demo shortlist.
- **Implementation state:** `BLOCKED` pending an authorized sanitized calibration aggregate.

### DT-467 — Produce Task 1 feature explanation

- **Deliverable:** the two tracked five-feature global mean-absolute-SHAP summaries with interpretation caveats.
- **Evidence boundary:** `docs/task1_explainability.md`; no private example or row is reproduced.
- **Acceptance:** preserve feature order, distinguish log-odds from probability points, and state association is not causation.
- **Implementation state:** `PASS_CANDIDATE`.

### DT-468 — Produce Task 2A backtesting results

- **Deliverable:** result schema and rolling-origin protocol table for total and Fresh chilled targets.
- **Required semantics:** latest four eligible origins, complete horizons 1–10, at least 52 historical weeks, requested-date ISO weeks, both official sources counted once, duplicates fail closed.
- **Evidence boundary:** `configs/task2a_validation.yaml` and `docs/task2a_validation_spec.md` define the method; approved aggregate values are absent.
- **Acceptance:** missing values are `NOT AVAILABLE`; structural-zero categories are not treated as model accuracy.
- **Implementation state:** `PREP_ONLY`.

### DT-469 — Compare Task 2A baselines/final model

- **Deliverable:** comparison table naming candidates/final family and evidence availability.
- **Evidence boundary:** `configs/task2a_final_models.yaml` records frozen 50/50 CatBoost/LightGBM ensembles; approved baseline/final error values are absent.
- **Acceptance:** constraints and selection state remain separate from accuracy or improvement.
- **Implementation state:** `PREP_ONLY`.

### DT-470 — Produce future-demand chart

- **Deliverable:** disclosure-safe ten-week chart specification.
- **Required semantics:** total and chilled cubic metres separated; Style/Tech structural chilled zeros labelled; no IDs or small-cell slices.
- **Evidence boundary:** official forecast values are protected and no approved aggregate chart series exists.
- **Acceptance:** do not derive the chart from official submission rows; exclude it from the demo shortlist until approved evidence exists.
- **Implementation state:** `BLOCKED` pending an authorized aggregate series.

### DT-471 — Produce Task 2B scarcity summary

- **Deliverable:** aggregate table of usable/specialized vehicles, workshop unavailability, trip-slot use, peak time/capacity and compatibility pressure.
- **Evidence boundary:** values are copied only from the already tracked `docs/task2b_policy.md`.
- **Acceptance:** no order identifiers, fabricated counterfactual, monetary cost, or unique-cause claim.
- **Implementation state:** `PASS_CANDIDATE`.

### DT-472 — Produce served/deferred summary

- **Deliverable:** aggregate served/deferred counts, shares, prior-deferral handling and operational impact.
- **Evidence boundary:** `docs/task2b_policy.md`; values are not recomputed from private rows.
- **Acceptance:** order grain is preserved conceptually, while no order/outlet identifier or private row is disclosed.
- **Implementation state:** `PASS_CANDIDATE`.

### DT-473 — Produce solver/checker evidence

- **Deliverable:** concise independent-validator and official-checker evidence with rule coverage.
- **Required semantics:** no return leg; at most two trips; combined Fresh 270 minutes and Style+Tech 480 minutes; brand/district, compatibility and capacity rules.
- **Evidence boundary:** `docs/task2b_validation_spec.md` and `docs/final_submission_validation.md`.
- **Acceptance:** checker PASS means feasibility under implemented rules, not global optimality, a judge score or rank.
- **Implementation state:** `PASS_CANDIDATE`.

### DT-474 — Select only strongest charts for demo

- **Deliverable:** a small, named shortlist in `docs/RESULTS_SUMMARY.md` and the manifest.
- **Selected:** Task 1 feature ranking; Task 2B served/deferred aggregate; Task 2B constraint pressure; existing Phase 36 architecture/process visuals where useful.
- **Excluded:** Task 1 calibration and Task 2A future-demand visuals while their approved aggregate data is unavailable.
- **Acceptance:** every selected visual has a tracked source; no decorative, fabricated, private or unsupported chart.
- **Implementation state:** `PASS_CANDIDATE`.

### 6.1 Common review and safety rule

All eleven tasks are covered by `tests/test_phase37_results_evidence.py`, including mutation checks for invented metrics, wrong units, missing split/approval, organizer-held-out claims, stale links, identifier-like content, late-close equality, duplicate-source precedence, wrong Task 2B time budgets, checker/optimality equivalence, a blanket organizer waiver, and falsely reopened prerequisite phases. Tests are synthetic/documentary and never load competition rows or deserialize models.

Fresh independent review must assess whether `PREP_ONLY` and `BLOCKED` tasks satisfy the master intent or require an authorized local aggregate evidence handoff. Until then, Phase 37 remains open and Phase 38 must not start.

## 7. End-to-end work sequence, file ownership and review checkpoints

| Order | Checkpoint | Read inputs | Permitted write surface | Proof / exit |
|---|---|---|---|---|
| 00 | Freeze working-tree and protected hashes | `git status`, metadata, local master and protected file SHA256 | None | Pre-existing modifications listed; protected baseline captured without opening rows |
| 01 | Master task extraction / prerequisites | Actual DT-464–474 and Phase35/36 status | **Only** contract reconciliation if permitted | Exactly 11 verbatim tasks, dependent phase gates classified |
| 02 | Evidence discovery | Safe source and prior sanitized non-sensitive reports | Evidence index / optional metadata manifest | Each proposed claim owned and source-graded |
| 03 | Task1 evidence | Task1 label/model/evaluation sources | Results summary | Service vs late separated; no invented metrics |
| 04 | Task2A evidence | Demand-history/rolling-origin/model sources | Results summary | Requested-date aggregation, ten-week and chilled semantics correct |
| 05 | Task2B evidence | Frozen allocation validation/policy source | Results summary | Hard feasibility separate from policy/optimality |
| 06 | Comparison/limitations | Historic approved experiments only | Results summary | Unsupported material explicitly excluded |
| 07 | Documentation QA | Report text, evidence index and source links | Synthetic test(s) | Positive and negative tests; no row/data access |
| 08 | Integrity/regression | Immutable metadata and safe tests | OS tmp only | No changed protected hashes; no staged private material |
| 09 | Independent handoff | Exact task matrix and safe PASS/FAIL proof | Completion record draft only | Review ready *if allowed by master*, otherwise `PREPARATORY ONLY` |

### 7.1 No invented requirements or values

- The organizer **does** score performance of Task1/Task2A at 20%, **does not** specify a named reporting metric or public leaderboard score in the provided booklet.
- The organizer **does** require Task2B feasible allocation and a short prioritization policy, **does not** say checker PASS means optimization optimality.
- The organizer **does** request an unlisted 3–5minute video, **does not** require Phase37 to host its own results video or publish confidential analyses.
- The organizer **does** require a truthful AI-use disclosure. Phase 35's approved document and incident-specific organizer reply must remain intact; Phase 37 tests do not grant new, blanket compliance clearance.

---

## 8. Complete synthetic verification matrix and negative-test design

Run meaningful tests against actual document parsing/claim relationships; mere keyword presence is insufficient. Suggested test IDs below are **candidates**, not assertions that they exist now.

| Check ID | Mapped IDs | Synthetic-only test specification | Required rejection / positive proof |
|---|---|---|---|
| P37-01 | All | `test_master_phase37_inventory_exact` | Exactly DT-464..DT-474, local exact title/dependency captured; missing or extra ID fails |
| P37-02 | 464,474 | `test_claims_have_provenance` | Numerical claims require source, split, metric definition, target, unit, status and approval |
| P37-03 | 464,473 | `test_unverified_metric_cannot_render_number` | Fake metric with `UNVERIFIED`/`approval=false` rejected |
| P37-04 | 465 | `test_service_label_excludes_waiting_in_report_contract` | Source-backed early waiting excluded; positive sample synthetic only |
| P37-05 | 466 | `test_late_strict_boundary_and_probability_semantics` | Equality at close not late; positive class mapping correct; no unsupported AUC |
| P37-06 | 467 | `test_task1_holdout_leakage_claims` | Chronology/source lineage based; train vs held-out split confusion fails |
| P37-07 | 468 | `test_task2a_requested_week_and_duplicates` | ISO origin and duplicate-ID hard failure described, not precedence merging |
| P37-08 | 468,469 | `test_task2a_horizon_and_chilled_rules` | Ten weeks; nonnegative; chilled<=total; Style/Tech chilled zero |
| P37-09 | 470 | `test_task2b_checker_claim_scope` | `feasible` ≠ `globally optimal`; unknown checker result not PASS |
| P37-10 | 470,471 | `test_task2b_trip_formula_and_policy` | No depot return, 2 trips, 270 Fresh / 480 Style+Tech and accurate source policy |
| P37-11 | 472 | `test_comparison_requires_matched_target_split` | Invalid baseline or invented uplift blocked |
| P37-12 | 472 | `test_explanation_output_space` | Raw classifier score explanation not mislabeled calibrated prob causal effect |
| P37-13 | 473 | `test_all_relative_links_resolve` | Broken/absolute/user-specific paths fail; private sources not clickable/public |
| P37-14 | 473 | `test_no_confidential_samples_or_unapproved_derivatives` | Regex text-only scan; no sample IDs/rows/screenshots, tokens or private report copies |
| P37-15 | 474 | `test_phase35_status_matches_authoritative_closure` | Reported Phase35 closeout must match local source; incident-specific organizer guidance is not represented as a blanket exemption |
| P37-16 | 474 | `test_submission_requirements_crosswalk` | Official deliverables accurately listed; no invented official Phase37 report filename |
| P37-17 | 474 | `test_evidence_index_claim_bidirectionality` | Every metric claim points to evidence; stale/orphan evidence flagged where required |
| P37-18 | All | Full project safe regression suite | No existing production semantic regression; skip reasons explained |
| P37-19 | All | Hash+size before/after + `git diff --check` | Identical official CSV, registry, 12 artifacts, unchanged code/notebook |

**Test design details:** Use `tmp_path` and fake evidence records, not genuine competition rows; reject unknown paths or private-data prefix, permit the *literal* schema column names where necessary. Avoid dynamic execution of manifest-supplied code. Import safe validation helpers if they have no private-data I/O side effect. A test file may be new, or extend an existing synthetic docs test module following local master conventions.

**Coverage acceptance:** every master task must have relevant evidence and tests, including negative tests that truly exercise production or document-validation code; collect-only success is not behavioral proof. Maintain a traceability mapping from **exact** master title → result section → evidence claim → pytest node or manual check → last independent verdict. If an authoritative task only supports manual inspection, document that explicitly rather than fabricating an automated test.

---

## 9. Git workflow, safe commands, and integrity snapshots

**Default branch proposal** (use repo conventions; don't auto-switch over working changes): `docs/phase-37-results-evidence`. Inspect `git status --short --branch` and recent closure notes first. Scope paths before editing; never silently overwrite user edits. **Do not stage, commit, merge or push** without explicit human authorization.

### 9.1 Baseline before any change (PowerShell at repository root)

```powershell
cd C:\Users\ASUS\Desktop\WayLoom_Datathon
git status --short --branch
git diff --name-only
git diff --cached --name-only
$protected = @(
  'outputs/submission_task1.csv',
  'outputs/submission_task2a.csv',
  'outputs/submission_task2b.csv',
  'models/artifact_registry.json',
  'TeamName_FinalNotebook.ipynb'
)
$before = @{}
foreach ($path in $protected) {
  if (-not (Test-Path -LiteralPath $path)) { throw "Protected path missing: $path" }
  $before[$path] = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
}
# Additionally use the actual registered-artifact metadata and an existing
# read-only verifier to hash/size-check all 12 registry entries.
# Do NOT run a verifier that overwrites preserved private safe_validation.json.
```

**Previously recorded baselines for comparison only**, not substitutes for fresh authorized local file checks:

- Task1: `9e0faa83a8dd1401ebaf72f1b1602dc560049d4a0cfba19676dbb69bf0de7918`
- Task2A: `142842eef5e4a2e7a6db450c19f4062e4a6eb065481aa21720b59556f9edd55d`
- Task2B: `15f98c8abc434811bc8d6db6ce64c4a746d0acd401f9147d7b15c0958d62b431`
- Registry: `eb1491b782f835cd7ec5046980d3ea234c9a69e68e006a4eef885f1feef5c82d`

### 9.2 Test and post-change commands

```powershell
# Only if test module exists/was created and the implementation gate permits it:
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_phase37_results_evidence.py

# If safe under AGENTS and no write-sensitive test configuration:
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pip check
git diff --check
git status --short --branch
git diff --cached --name-only

foreach ($path in $protected) {
  $after = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
  if ($before[$path] -ne $after) { throw "PROTECTED HASH CHANGED: $path" }
}
# Re-run read-only model registry artifact hash-and-size verification.
```

Check test safe behavior before full suite: use `-p no:cacheprovider`, OS temporary `--basetemp` if needed, and ensure no test executes private-data or output writers. Tests run by a **human-local** operator when private data is necessary; the external agent cannot open actual competition CSV contents or private reports to gather statistics.

### 9.3 Whitelisted editing, staging and review

Permitted only if local phase prerequisites allow and the actual master requires: existing `docs/RESULTS_SUMMARY.md`, existing `docs/RESULTS_EVIDENCE_INDEX.md`, optional `configs/phase37_results_evidence.yaml`, relevant synthetic `tests/test_phase37_results_evidence.py`, and Phase37 contract reconciliation. Any README changes belong to Phase36 unless explicitly approved. Protected raw CSVs/models/notebook/src/scripts/other phase closure flags are out of scope.

**For a later separately authorized commit**, stage only explicitly reviewed documentation/testing paths, for example:

```powershell
# Do not run this during implementation/review without explicit approval.
# git add -- 'docs/RESULTS_SUMMARY.md' 'docs/RESULTS_EVIDENCE_INDEX.md' 'tests/test_phase37_results_evidence.py' 'MD Files/PHASE_37_COMPETITION_CONTRACT.md'
# git diff --cached --check
# git diff --cached --name-only
# git commit -m "docs(datathon): verify phase 37 results evidence"
```

Never stage `data/raw`, `data/interim`, `reports/private`, approved private metric reports, executed notebooks, model binaries, output submissions, credentials or communications. Keep `reports/private/**` Git-ignored. `git status` need not be clean if changes are pre-existing, but **must not contain unexpected modified protected files or confidential exports**.

---

## 10. Phase 37 stop conditions and escalation decision tree

**STOP immediately and report** if any of these occurs:

1. Exact Phase37 master inventory cannot be extracted, differs substantively from this task scaffold, or the requested task is not authorized by master dependencies.
2. Phase35/36 gate explicitly forbids Phase37 implementation; allow only appropriately marked drafts if policy permits.
3. A numeric predictive metric is not backed by an approved sanitized source with precise target, units, split and sample coverage.
4. A report suggests final-test accuracy, an organizer rank, a winner claim or deployed-system performance without official verification.
5. A Task2B allocation/feasibility/optimality statement exceeds the official checker's proven scope.
6. An external AI service would need to read/upload real competition data or derivatives, private executed notebook outputs or organizer correspondence.
7. A confidential derivative or subgroup metric has no organizer-approved sharing audience.
8. Any frozen official submission, saved model, registry, feature schema, training code, notebook or allocation/policy bytes change.
9. An existing claimed metric contradicts documented label/history computation or leakage-safe split and cannot be reconciled without retraining.
10. Hidden Git changes, unexpected staged files, path traversal, injected secret or unsafe report copy is discovered.
11. A requirement requires independently proving a historical human action or organizer approval that is not actually evidenced.
12. A full-suite test would write/replace official CSV, preserved private `safe_validation.json` or private reports.

**Recovery:** preserve diff and hash baseline, do not reset automatically, report `BLOCKED` with evidence; do not authorize Phase38 or submission packaging by changing statuses.

---

## 11. Definition of Done — 22 independently checkable items

> **Note:** a prepared report can satisfy technical drafting items but **cannot** satisfy formal Phase37 closure if master gating, approval or fresh independent review remains open.

- [x] 01. Exact local DT-464–DT-474 task names, scope, priority, mandatory/optional and dependencies extracted and reconciled.
- [x] 02. Local Phase35 and Phase36 master statuses verified and master phase-gate respected.
- [x] 03. All eleven task IDs have task-specific outputs or explicit `BLOCKED` findings; no omissions.
- [x] 04. Official task definitions, p22 deliverables and p23 judging rubric checked, without inventing official metric mandates.
- [x] 05. Task1 service label and `minutes` unit are source-correct; early waiting excluded.
- [x] 06. Task1 late probability uses strict-close definition and real positive-class/calibration metadata.
- [x] 07. No unverified held-out, test or leaderboard Task1 accuracy is reported.
- [x] 08. Task1 validation and leakage claims reference actual frozen functions/config/tests.
- [x] 09. Task2A both history sources, cross-source duplicate fail-closed, requested-date ISO calendar semantics documented.
- [x] 10. Task2A ten-week total/chilled forecasts, structural zeros, nonnegative/capping limitations correct.
- [x] 11. Task2A metrics, if reported, include approved split/origin/target/unit/aggregation; no withheld-test accuracy claims.
- [x] 12. Task2B S1 feasibility, eligibility, trip-time and budget rules accurately sourced.
- [x] 13. Task2B actual prioritization and deferral rationale linked; no fabricated costs/order examples.
- [x] 14. Official checker feasibility is not misrepresented as global optimality or judge score.
- [x] 15. Any model comparisons, explainability, uncertainty or improvement metrics come from approved existing evidence.
- [x] 16. Every numerical claim has unique ID, exact source, provenance level, unit, metric definition and disclosure permission.
- [x] 17. Missing evidence is presented as `NOT AVAILABLE`/`UNVERIFIED`, never as zero or assumed PASS.
- [x] 18. Safe relative links, source-to-claim traceability, intended audience and no private row/ID leakage verified.
- [x] 19. Approved Phase 35 disclosure, truthful sharing history and incident-specific organizer response referenced accurately; no invented blanket waiver.
- [x] 20. Synthetic targeted document tests and safe appropriate regressions pass, with real counts/skips recorded. **Post-remediation targeted Phase 37: 38 passed. Combined Phase 35/37: 56 passed. Full safe suite: 939 passed, 2 skipped, 4 warnings. The stale Phase 35 open-flag assertion was replaced with a closure assertion without changing the approved disclosure documents.**
- [x] 21. Official CSVs, registry, notebook and all 12 artifacts unchanged by before/after SHA256; Git/privacy safe.
- [ ] 22. **Fresh independent Phase37 read-only review PASS** and subsequent authorized administrative closure recorded *before* Phase38 readiness YES.

**Phase-count rule:** 11 master IDs, 11 documented task verdicts. A task can be implemented yet remain `PREPARATORY ONLY` if Phase35/36 gate is unmet. `TESTS PASSED` and `READY FOR REVIEW` are **not** `FORMALLY CLOSED`.

---

## 12. Task verification and completion record — fill only after actual implementation

| Task | Exact master title | Implementation verdict | Evidence IDs / real test nodes | Blocker or reviewer note |
|---|---|---|---|---|
| DT-464 | Produce final Task 1 metrics table | PREP_ONLY | E-P37-003, E-P37-005; `test_results_summary_has_exact_task_sections_and_semantics` | Metric definitions/split/units complete; approved numerical aggregates `NOT AVAILABLE`. |
| DT-465 | Compare Task 1 baseline vs final model | PREP_ONLY | E-P37-003, E-P37-004; `test_mutation_rejects_invented_metric_value` | Frozen final families recorded; approved baseline/final numbers `NOT AVAILABLE`. |
| DT-466 | Produce calibration visualization | BLOCKED | E-P37-003, E-P37-005; `test_unavailable_visuals_are_not_selected` | Approved calibration-bin data `NOT AVAILABLE`; specification only. |
| DT-467 | Produce Task 1 feature explanation | PREP_ONLY | E-P37-006, E-P37-013; `test_task1_feature_rankings_match_approved_source` | Tracked SHAP rankings and non-causal caveats summarized; owner publication approval remains pending. |
| DT-468 | Produce Task 2A backtesting results | PREP_ONLY | E-P37-007; `test_task2a_semantics_and_constraints_are_explicit` | Protocol/result table complete; approved aggregates `NOT AVAILABLE`. |
| DT-469 | Compare Task 2A baselines/final model | PREP_ONLY | E-P37-007, E-P37-008; `test_mutation_rejects_invented_metric_value` | Frozen ensemble recorded; approved numerical comparison `NOT AVAILABLE`. |
| DT-470 | Produce future-demand chart | BLOCKED | E-P37-008; `test_unavailable_visuals_are_not_selected` | Approved public aggregate forecast series `NOT AVAILABLE`; specification only. |
| DT-471 | Produce Task 2B scarcity summary | PREP_ONLY | E-P37-009, E-P37-013; `test_task2b_claim_register_matches_summary_and_index_exactly` | Complete internal claim register; owner publication approval remains pending. |
| DT-472 | Produce served/deferred summary | PREP_ONLY | E-P37-009, E-P37-013; `test_task2b_claim_register_matches_summary_and_index_exactly` | Complete internal claim register; no identifiers; owner publication approval remains pending. |
| DT-473 | Produce solver/checker evidence | PASS_CANDIDATE | E-P37-010, E-P37-011, E-P37-015; `test_phase33_checker_evidence_uses_actual_completion_and_closure_records`; `test_checker_is_feasibility_not_optimality` | Checker implementation, validation semantics, human-local execution record and independently reviewed Phase 33 closure are distinguished. |
| DT-474 | Select only strongest charts for demo | PREP_ONLY | E-P37-006, E-P37-009, E-P37-013; `test_unavailable_visuals_are_not_selected` | No Phase 37 result asset is selected for public/demo release while owner approval remains pending. |

```text
PHASE37 MASTER PLAN EXTRACTION: VERIFIED — EXACT 11/11
PHASE35 / PHASE36 GATE: VERIFIED CLOSED IN LOCAL MASTER
DT-464...DT-474: 1 PASS_CANDIDATE / 8 PREP_ONLY / 2 BLOCKED — FRESH RE-REVIEW PENDING
RESULTS SUMMARY: GENERATED — SAFE, SOURCE-GROUNDED, PREPARATORY
CLAIM-TO-EVIDENCE INDEX: GENERATED — 33/33 TASK2B CLAIMS STRUCTURALLY RECONCILED; PUBLICATION APPROVAL PENDING
SAFE TARGETED PYTEST: PASS — 38 PASSED
COMBINED PHASE35/37 DOC TESTS: PASS — 56 PASSED
FULL SAFE PYTEST: PASS — 939 PASSED, 2 SKIPPED, 4 WARNINGS
PIP CHECK: PASS
GIT DIFF --CHECK: PASS
OFFICIAL CSV / REGISTRY / NOTEBOOK HASHES: UNCHANGED
REGISTERED ARTIFACT HASH/SIZE: 12/12 PASS
PRIVATE DATA EXPOSED: NO
INDEPENDENT REVIEW: PENDING
PHASE37 FORMAL CLOSURE: NO
PHASE38 STARTED: NO
```

**Historical independent review and remediation:** The first fresh Phase 37 review returned `FAIL` because the Markdown/YAML Task 2B claim IDs diverged, several displayed claims were absent from the manifest, publication approval was not substantiated, E-P37-011 cited a procedure instead of the actual Phase 33 PASS record, and the full suite retained one stale Phase 35 assertion. The remediation preserved unavailable Task 1/2A values, established the YAML as the canonical 33-claim register, added field-for-field Markdown/YAML and negative mutation tests, made publication selection fail closed, corrected Phase 33 evidence provenance and repaired the stale Phase 35 test. A new independent read-only review is still required; Phase 37 remains open.

**Subsequent technical audit:** E-P37-006 and E-P37-009 were still labelled `SANITIZED_AGGREGATE_APPROVED` in the evidence catalog even though their exact public/demo approval remains `PENDING`. They are now classified `TRACKED_INTERNAL_AGGREGATE`; the results summary is explicitly internal-only, its public README link has been removed, and regression tests reject renewed approval-by-source inference. Local post-repair checks observed 41 passing Phase 37 tests, 59 passing combined Phase 35/37 tests, 66 passing Phase 36/37 tests, and 947 passed / 2 skipped / 4 warnings in the full safe suite. These are agent-run safe checks, not private evaluation or a fresh independent review. This repair does not supply missing Task 1/2A aggregates or charts, grant publication approval, or authorize Phase 37 closure. The earlier review and its failures remain historical facts.

**Approval protocol:** once task-level work is actually complete and dependencies satisfied, request a fresh independent *read-only* review. After an independent PASS, authorized owner reconciles the Phase37 completion record and master checkboxes/phase readiness; preserve historical FAILs as such. Do not rewrite prerequisite Phase35/36 statuses simply to make the phase look closed. Human-controlled official submission remains separate from this implementation phase.

---

---

## Appendix A. Ready-to-copy enhanced implementation prompt (same as separate TXT)

```text
# WAYLOOM — PHASE 37: RESULTS SUMMARY & EVIDENCE — ENHANCED CURSOR/CODEX IMPLEMENTATION PROMPT

Act as a senior ML evaluation engineer, competition compliance auditor, evidence/measurement provenance specialist and Python test engineer. Work in the existing WayLoom Datathon repository as a scoped implementation agent. **DO NOT** invent source text, measured performance, organizer scores, dataset rows, human approvals, or phase-status evidence absent from the local repository.

PRIMARY CONTRACT: `MD Files/PHASE_37_COMPETITION_CONTRACT.md` (provided). OFFICIAL SOURCE: `MD Files/Challenge Booklet.pdf`. LOCAL MASTER SOURCE: `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md`. PROJECT RULES: `AGENTS.md` and `CODEX_HANDOFF_PHASE_11_ONWARDS.md`.

## MISSION
Produce an honest, safe, traceable Phase37 evidence summary across **all eleven DT-464…DT-474** tasks, **only to the extent authorized by the local master-plan dependencies**. Before doing anything substantive, reconcile the **exact** master titles/requirements against provisional titles in this contract. According to the latest provided closure reports, **Phases 34, 35 and 36 are formally closed**. Verify those statuses in the *actual local master plan and contracts* before executing Phase37; preserve the approved Phase35 data-sharing disclosure and incident-specific organizer reply. Do not assume that the official rules, master task titles, metric values or Phase37 completion have been verified until inspected. Do not proceed to Phase38.

## STEP 0 — SOURCE + STATUS GATE (MANDATORY)
1. Read official booklet Datathon printed pp15–25 (tasks, rule/data terms, p22 deliverables, p23 weights), actual local master Phase35–37 blocks, Phase35 disclosure/record, Phase36 completion, Phase34 closure, prior approved task-model/evaluation/optimizer source, Phase37 contract, AGENTS, handoff.
2. Extract **verbatim** every `DT-464` to `DT-474`: title, full work item text, checkbox/priority, mandatory/optional, dependency, DoD and Phase37 completion gate; present eleven-row reconciliation. Provisional workstreams are not canonical. If mismatch, edit this contract **only if authorized** to align with actual source and preserve all task IDs; do not quietly substitute different tasks.
3. Verify Phase35 and Phase36 master task checkboxes, phase-complete/readiness flags and independent-review closure records. If a required gate is actually open, contradictory or missing, **STOP formal Phase37 implementation**; only clearly labeled **PREPARATORY** results-index scaffolding is allowed when approved. Do not check Phase37 tasks in that situation.
4. If the verified local gate authorizes implementation, proceed with Phase37 results/evidence work and accurately record Phases 35 and 36 as formally closed without overstating Phase35 organizer clearance.

## URGENT DEADLINE / SCOPE GUARD
This internal Phase37 results report is **not** an additional official booklet-required submission file. Prioritize the booklet's mandatory deliverables and final ZIP/upload on time. Never invent numbers to finish faster. If safe aggregate metric evidence is unavailable, publish a clear `NOT AVAILABLE` statement and meaningful method/evaluation traceability rather than fabricating accuracy.

## STEP 1 — PROTECTION / BEFORE STATE
`git status --short --branch`, `git diff --name-only`, `git diff --cached --name-only`; record pre-existing modifications. Verify SHA256 of each frozen `outputs/submission_task1.csv`, `outputs/submission_task2a.csv`, `outputs/submission_task2b.csv`, `models/artifact_registry.json`, `TeamName_FinalNotebook.ipynb`, and 12 registry-listed artifacts **via hash-and-size only**. Use actual registry schema/known read-only checker; don't run the canonical validator when it overwrites private `safe_validation.json`.
NEVER open/print/copy real competition rows, IDs, predictions, datasets, private executed notebooks, hidden outputs, private reports (`data/raw`, `data/interim`, `reports/private`), secrets or organizer correspondence. The real-data sharing history is already documented: do not repeat it by transmitting datasets to ChatGPT/Codex or any other external service. Do not run private inference, data-based metric scripts or official checker in agent context.

## STEP 2 — TASK-BY-TASK IMPLEMENTATION
Using **EXACT reconciled local master tasks** (not provisional names), cover all IDs individually. Suggested engineering components if compatible:
- DT-464 — Safe claim/evidence inventory with source/metric/approval grades.
- DT-465 — Task1 service handling-time results; MAE/RMSE **only if genuinely computed and approved**, unit minutes, early wait excluded.
- DT-466 — Task1 late probability results; actual late is arrival strictly after window close, correct positive class and calibration policy; avoid invented AUC/Brier.
- DT-467 — Task1 chronology/held-out split, leakage and apples-to-apples baselines; no withheld-test accuracy.
- DT-468 — Task2A rolling-origin total/chilled metrics, requested-date ISO calendar, count orders once; cross-source duplicates fail closed.
- DT-469 — Task2A ten-week grid/structural zero Style+Tech, capping/nonnegative, distinguish constraints vs accuracy.
- DT-470 — S1 Task2B whole-order served/deferred and hard-rule compatibility/time/capacity checker evidence; no invented serving numbers.
- DT-471 — Actual frozen lexicographic priority / deferral tradeoffs; costs and optimality only where proven; preserve one-page policy.
- DT-472 — Existing valid baseline comparisons, ablations, SHAP calibration bridge, optionally uncertainty only if proven.
- DT-473 — Safe summary/figures/claim-to-evidence index; no real rows, identifiers, small-cell sensitive slices or invented plots; mechanistic test coverage.
- DT-474 — Final factual QA, exact source crosswalk, safe regression/hash guards, readiness for independent review.

Candidate files after inspecting current repo: `docs/RESULTS_SUMMARY.md`, `docs/RESULTS_EVIDENCE_INDEX.md`, optional metadata-only `configs/phase37_results_evidence.yaml`, synthetic `tests/test_phase37_results_evidence.py`. Reuse real paths and approved prior phase records. Every numeric result needs named target, formula, unit, holdout origin, source provenance, approved disclosure audience and evidence ID. If unavailable, say `NOT AVAILABLE` **without a placeholder number**. Official judge weights are not performance metrics. Official `check_allocation.py` PASS proves feasibility, not global optimum. Model/test hashes and passing pytest are engineering quality evidence, not private predictive accuracy. No public release of confidential derivatives.

## STEP 3 — TEST LIKE AN AUDITOR
Before adding tests, inspect existing synthetic docs/traceability tests. Verify each task has real source-backed evidence rather than cosmetic headings. Add targeted synthetic negative tests for false score, wrong unit, missing metric/split/approval, unsupported held-out test evaluation, stale relative link, invented public/YouTube URL, confidential-looking row/identifier, incorrect late-close definition, duplicate-ID source precedence, wrong Task2B trip budget or checker-optimality equivalence, fabricated organizer blanket exemption or falsely reverted Phase35 status. Use actual source/validation functions where safe; never import code with private-data I/O side effects.
Run targeted suite; full safe pytest only if gate, suite and permissions allow; pip check; git diff --check; source-only claim audit; hash-and-size after. Report actual counts and skips. Do not auto-run scripts that retrain, regenerate CSV or overwrite private reports.

## STEP 4 — CHANGE/GIT DISCIPLINE
Change only Phase37 owned docs/metadata/synthetic tests and this contract if reconciliation demands it. No frozen `outputs/`, `models/`, notebook, `src/`, `scripts/`, training configs, Phase24 policy or prior completion statuses changed. No staging/commit/push/ZIP/YouTube upload. Never use `git add -A` or `git reset --hard`. Preserve all preexisting diffs. If any frozen hash changes, stop, report and do not silently restore.

## STEP 5 — HANDOFF REPORT
Provide all **11 tasks with exact local master titles**, state `PASS / PREPARATORY ONLY / BLOCKED / NOT STARTED`, source/evidence IDs, substantive pytest/manual checks and blockers; files created/modified; comparison of initial/final Git status; source-backed metric table (no fabricated values); test counts with skips; pre/post hashes and 12 model checks; privacy; Phase35/36 gates; readiness for a fresh independent review. A fresh **independent** review is required before phase closure; even technical PASS is not an authorization to begin Phase38.

OUTPUT TEMPLATE:
PHASE37 EXACT MASTER INVENTORY: VERIFIED / UNAVAILABLE
PHASE35 PREREQUISITE: PASS / BLOCKED / NOT REQUIRED BY MASTER
PHASE36 PREREQUISITE: PASS / BLOCKED / NOT REQUIRED BY MASTER
DT-464: <exact title> — PASS / PREP_ONLY / BLOCKED
DT-465: ...
DT-466: ...
DT-467: ...
DT-468: ...
DT-469: ...
DT-470: ...
DT-471: ...
DT-472: ...
DT-473: ...
DT-474: ...
RESULTS REPORT: FINAL DRAFT / PREPARATORY / NOT STARTED
EVIDENCE TRACEABILITY: PASS / FAIL / PENDING
REAL METRICS: SOURCE-APPROVED ONLY / NOT AVAILABLE
TARGETED PYTEST: <actual counts / NOT RUN>
FULL SAFE SUITE: <actual counts / NOT RUN>
PIP / GIT DIFF: PASS / FAIL / NOT RUN
FROZEN CSV + REGISTRY + NOTEBOOK + 12 ARTIFACT HASH GUARDS: PASS / FAIL / NOT CHECKED
CONFIDENTIAL DATA OPENED OR EXPORTED: NO
PHASE37 FRESH INDEPENDENT REVIEW: PENDING
PHASE37 FORMALLY CLOSED: NO
PHASE38 STARTED: NO
FILES CHANGED: <exact paths>
BLOCKERS: <actual gate/evidence findings>

**Explicit final stop:** Never invent organizer-scored results, falsely extend Phase35 incident-specific permission into a blanket waiver, fabricate metric evidence, alter Phase35/36 closure records, or begin the next phase. Human attestations and official communications retain their actual recorded scope.
```

---

## Appendix B. Ready-to-copy fresh independent review prompt (same as separate TXT)

```text
# WAYLOOM — PHASE 37 FRESH INDEPENDENT RESULTS/EVIDENCE REVIEW — READ-ONLY CURSOR/CODEX PROMPT

ROLE: Independent senior ML metric-validity auditor, competition rule reviewer, reproducibility/privacy auditor and adversarial software-test reviewer. **STRICT READ-ONLY**: do not edit, format, regenerate, stage, commit, retrain, run private-data tasks, publish, zip or begin Phase38. Treat implementer's status and earlier session claims as untrusted until independently substantiated.

SOURCES (authority descending): official local `MD Files/Challenge Booklet.pdf` Datathon pp15–25 including p22/23, actual `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` Phase35–37; exact reconciled Phase37 contract; Phase35/36 current completion records; prior frozen evaluation and Task2B policy/validator contracts; current source tests/config; `AGENTS.md` and handoff; generated `docs/RESULTS_SUMMARY.md`, `docs/RESULTS_EVIDENCE_INDEX.md` and any phase37 manifest/tests.

## A. PREREQUISITE AND EXACT TASK INVENTORY
1. Extract verbatim all **DT-464 through DT-474** master tasks — exactly 11 IDs, titles, priorities, dependencies, marks and acceptance text; compare against contract and deliverables. Fail claims of full completion where actual task mapping omitted or substituted.
2. Check Phase35 and Phase36 **real** current master/contract statuses. Latest user-provided independent reviews and administrative closure reports state **Phase35 and Phase36 are both formally CLOSED**. Verify this in the actual local master plan and completion records; if a mandatory gate is in fact still open or inconsistent, report Phase37 `BLOCKED`. Do not rewrite phase statuses as part of this read-only review.
3. Correctly distinguish official booklet criteria from optional Phase37 internal reporting. Booklet has performance judging at 20%, not specified MAE/RMSE/AUC score tables or public leaderboard ranks. No fabricated official requirement.

## B. EACH ELEVEN TASKS — SUBSTANTIVE INSPECTION
For **each DT-464…DT-474**, report exact master title, accepted scope, implementation path/section, actual source/evidence and test node, and verdict `PASS / FAIL / PREP_ONLY / BLOCKED`, with minimal blocking fix. Suggested risk focal points if compatible with local titles:
- claim ledger/provenance;
- Task1 service label/MAE unit/held-out split;
- late strict close, positive class, probability vs actual late and calibration;
- leakage-free Task1 validation/comparisons;
- Task2A two-source demand aggregation by requested-date ISO week, 10-week rolling-origin, chilled evaluation;
- Task2A Style/Tech zeros and clipped/capped values;
- Task2B S1 feasibility/eligibility/time/whole-order checks;
- actual priority policy and cost/deferral substantiation;
- optional baseline/SHAP output-space validity;
- figures and evidence index with privacy/links;
- final cross-document completeness, tests and gates.

## URGENT JUDGING / DEADLINE GUARD
Phase37 is an internal master-plan phase, not an official additional deliverable. Do not insist on unrequired plots or guessed metrics when they would delay the organizer-required final ZIP. Nevertheless, each substantive local master item and each factual claim must be satisfied truthfully.

## C. NUMERICAL CLAIM FORENSICS
Make a **claim-to-evidence table** for every number presented as real model performance, allocation result, improvement, served count or evaluation statistic. Verify its source exists; unit; formula/target; split/horizon; provenance; permitted audience; owner approval; whether measured or only human-local reported. A reported metric without approval becomes `NOT AVAILABLE`; **do not inspect private data to recover it**. Verify Task1 minutes and [0,1] late probability; Task2A m3/chilled structural zero; Task2B feasibility ≠ unique/global optimum. No official-future-test accuracy without ground truth, no organizer score inferred from rubric. No cherry-picked dissimilar baselines or data leakage.

## D. PRIVACY / DATA INCIDENT / OFFICIAL COMPLIANCE
Respect `data/raw/**`, `data/interim/**`, `reports/private/**`, private notebooks and organizer correspondence as off-limits. Do not read/report raw competition rows, identifiers, predictions, derivatives, secrets or small sensitive subgroup details. The Phase35 record documents dataset/notebook transmissions to ChatGPT/Codex and reported organizer 'no worries'; no unconditional compliance/clearance statement is valid. No output data upload, retraining or model deserialization. Distinguish `HUMAN_LOCAL_REPORTED` from reviewer-executed tests. If any results report is destined for public distribution, separately verify publication authority for derivatives — do not assume synthetic data is public.

## E. ACTUAL SAFE TESTS AND HASH GUARDS
Record `git status --short --branch`, staged diff and initial protected hashes for all three `outputs/submission_task*.csv`, registry, final notebook and 12 registered artifacts via read-only metadata verification. Review only source/traceability/approved aggregate docs. Run non-destructive targeted Phase37 synthetic tests, full safe pytest only if available/authorized (no cache/private-report overwrites), `.venv` `pip check`, `git diff --check`, evidence link/metric/type audits. Compare end-state hashes and Git status; account for pre-existing modifications. Explain skips and unrun private checks. Do not run a canonical validator if it overwrites preserved private `safe_validation.json`.

## F. SCORING AND FINAL OUTPUT
FAIL for unsupported metric, mislabeled validation, scope overstatement, missing exact master item, forbidden data exposure, violated gate or altered frozen artifact. If docs are accurate but a local Phase35/36 required prerequisite proves open, assign `PREPARATORY ONLY / BLOCKED` rather than formal PASS. A fresh review may judge technical prep positively without authorizing phase-complete or Phase38.

Required report:
1. Exact 11-row DT-464–DT-474 matrix: master title, task verdict, evidence paths/source lines, actual pytest nodes or manual proof, remediation if needed.
2. Official p15–p23 crosswalk and metric validity table.
3. All numeric claims and their provenance/approval status; invalid/unavailable separately listed.
4. Actual fresh targeted/full test counts/skips/pip/diff; artifact hashes/size integrity; initial/final Git changes; privacy findings.
5. Phase35/36 gate finding, Phase37 task/blocker status and formal authorization decision.

END EXACTLY WITH:
PHASE37 FRESH INDEPENDENT REVIEW: PASS / FAIL / PREPARATORY_ONLY
EXACT DT-464–DT-474 LOCAL MASTER TITLES: VERIFIED / NOT VERIFIED
PHASE35 PREREQUISITE: PASS / BLOCKED / NOT_REQUIRED
PHASE36 PREREQUISITE: PASS / BLOCKED / NOT_REQUIRED
DT-464: PASS / FAIL / PREP_ONLY / BLOCKED
DT-465: PASS / FAIL / PREP_ONLY / BLOCKED
DT-466: PASS / FAIL / PREP_ONLY / BLOCKED
DT-467: PASS / FAIL / PREP_ONLY / BLOCKED
DT-468: PASS / FAIL / PREP_ONLY / BLOCKED
DT-469: PASS / FAIL / PREP_ONLY / BLOCKED
DT-470: PASS / FAIL / PREP_ONLY / BLOCKED
DT-471: PASS / FAIL / PREP_ONLY / BLOCKED
DT-472: PASS / FAIL / PREP_ONLY / BLOCKED
DT-473: PASS / FAIL / PREP_ONLY / BLOCKED
DT-474: PASS / FAIL / PREP_ONLY / BLOCKED
METRIC CLAIMS SOURCE-VERIFIED: YES / NO / NOT_APPLICABLE
OFFICIAL RULE CROSSWALK: PASS / FAIL
DOC/EVIDENCE TRACEABILITY: PASS / FAIL / PENDING
TARGETED PYTEST: ACTUAL COUNTS / NOT_RUN
FULL SAFE PYTEST: ACTUAL COUNTS / NOT_RUN
PIP CHECK / GIT DIFF: PASS / FAIL / NOT_RUN
FROZEN CSV + REGISTRY + NOTEBOOK + 12 ARTIFACT HASHES: PASS / FAIL / NOT_CHECKED
DATA / PRIVACY SAFETY: PASS / FAIL
FORMAL PHASE37 CLOSURE AUTHORIZED: YES / NO
PHASE38 MAY BEGIN AFTER AUTHORIZED CLOSURE: YES / NO
BLOCKERS: NONE / PRECISE FINDINGS
FILES MODIFIED BY REVIEW: NONE
```
