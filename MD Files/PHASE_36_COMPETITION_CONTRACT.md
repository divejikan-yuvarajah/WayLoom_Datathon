# PHASE 36 — README / Project Documentation: Competition Implementation Contract

> **Project:** WayLoom — Rootcode Tech-Triathlon 2026 Datathon  
> **Canonical filename:** `PHASE_36_COMPETITION_CONTRACT.md` (place under repository `MD Files/` according to existing convention)  
> **Inventory confirmed from supplied project handoff:** **Phase 36, DT-456–DT-463, exactly 8 task IDs**.  
> **Exact master-plan task titles / metadata:** **RECONCILED against the local master plan on 9 October 2026**. Phase 36 contains exactly DT-456–DT-463; every item is `[E]`, P1, and depends on `Stable repository and outputs`. The exact titles and gate are recorded in §4; formal completion is recorded in §13.1 after the authorized independent re-review PASS.  
> **Official-booklet distinction:** the booklet requires particular Datathon deliverables (not a standalone README by name). The Phase 36 README is a **WayLoom master-plan documentation deliverable** and should guide judges to the actual mandated files without inventing an organizer README requirement.  
> **Known actual project status from conversation:** Phase 34 formally CLOSED; **Phase 35 remains OPEN**, due to unresolved AI-use factual attestation, compliance scope and final human approval. Preparing README documentation in parallel is allowed; **formal Phase 36 implementation/closure readiness must obey the actual master-plan dependency gate**. Do NOT change Phase 35 to PASS, conceal its status or imply organizer blanket clearance.  
> **Document status:** **FORMALLY COMPLETE.** Implementation evidence, the historical failed review, the repaired DT-460 path semantics, and the final independent re-review PASS are recorded in §13.1. Phase 35 remains open and Phase 37 has not been started by this closure action.

---

## 1. Executive purpose and desired result

Produce a compact, honest, navigable, reproducible **project-facing README and supporting documentation map** for a judge or reviewer who is unfamiliar with WayLoom. They should be able to discover the problem, the three Datathon tasks, the actual outputs, how to inspect and validate them safely, the training/inference architecture, where the official deliverables reside, and what can or cannot be rerun without access to restricted data. Documentation must accurately reflect the **current frozen repository**, not an aspirational design or the unrelated Hackathon/Designathon implementation.

**Primary proposed deliverable:** root `README.md` with clear section hierarchy, file table and clickable relative links. **Supporting deliverables (only as needed after inspecting repo):** a concise judge walkthrough under `docs/`, a documentation-to-source traceability check under `tests/`, and safe relative links to the existing approved architecture, preprocessing, policy, results and disclosure documents. Do not duplicate all prior material inside README.

**Success condition:** every Phase 36 master-plan requirement is demonstrably satisfied with documented source evidence; all stated commands are copied from discoverable repository entry points and safely verified as far as the agent's permissions allow; documentation introduces no false claims or confidential-data leakage; the fresh independent review eventually authorizes closure.

## 2. Authority, evidence grades and unresolved prerequisites

### 2.1 Source order — read in this sequence

1. Official **`Challenge Booklet.pdf`** (Datathon printed pages **21–25**, especially **p.22 Deliverables** and **p.23 Submission**); accompanying supplied template / checker definitions if referenced. Formal organizer clarifications count only when actually available, and must be quoted within their established scope.
2. Actual LOCAL `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` for **exact DT-456…DT-463 text**, priority, optional/required mark, dependencies and phase-complete gate.
3. Actual LOCAL `MD Files/PHASE_35_COMPETITION_CONTRACT.md`, Phase 35 disclosure and signed status; verified Phase 34 closure and approved earlier contracts (notably Phases 24, 29–34).
4. Actual source, `configs/`, safe tests, model-registry metadata, `TeamName_FinalNotebook.ipynb` *source cells only*, current `README.md`, pyproject/requirements and available documentation.
5. `AGENTS.md`, `CODEX_HANDOFF_PHASE_11_ONWARDS.md`, this contract and user-approved engineering decisions.

**Do not resolve source disagreements silently.** Quote the conflicting text and designate the higher authority; change this contract before implementing any mismatched provisional task. Claim grades in documentation: `OFFICIAL` (booklet/template), `REPOSITORY_VERIFIED` (actual committed/source path), `HUMAN_LOCAL_REPORTED` (sanitized local test proof), `TEAM_REPORTED` (e.g., organizer communication), `PROPOSED` (never presented as implemented), `UNKNOWN` (not assumed).

### 2.2 Phase 35 conflict: scope-safe path

- **Readiness check:** inspect *current repo* master-plan Phase 35 block and its completion report. Current conversation evidence says Phase 35 is open; **do not pretend otherwise**.
- If the local master plan requires Phase 35 formal completion for Phase 36 execution, **STOP formal implementation**. You may create or revise **clearly labelled preparatory README drafts only** if the user's instruction and repo rules permit, but leave DT-456–DT-463 unchecked and Phase 36 `READY` = NO.
- If the master plan allows independent Phase 36 documentation work, implement source-grounded sections without touching Phase 35; still do not declare the whole project submission-compliant or final-disclosure-approved.
- The README can say "AI-use disclosure: see docs/AI_USE_DISCLOSURE.md; factual review is pending" **only if the referenced local document really says this**. Never publish private incidents or organizers' communications beyond appropriate documented, sanitized disclosures. No invented blanket waiver.
- Do not block urgent *preparation of other deliverables* solely because the internal checklist is open, but do not bypass an explicit mandatory phase gate.

### 2.3 Restricted content and external-agent threat boundary

**Do not open, inspect, paste, summarize or copy private row-level content:** `data/raw/**`, `data/interim/**`, `reports/private/**`, private executed notebooks, confidential CSV rows, order/delivery identifiers, nonpublic predictions, secrets, access tokens or organizer correspondence. The previous Phase 35 record confirms real competition dataset/notebook sharing with ChatGPT/Codex; **do not repeat it**. Use schema names, publicly allowed rules, source-code-only inspections, safe metadata and synthetic fixtures. Never ask an AI agent to upload datasets to create README examples.

Protected immutable paths: `outputs/submission_task1.csv`, `outputs/submission_task2a.csv`, `outputs/submission_task2b.csv`, `models/**` incl `models/artifact_registry.json` and all twelve registered artifacts, `TeamName_FinalNotebook.ipynb`, implementation code under `src/`, approved model/training/optimization configs, raw reference tables/templates, private reports. In this documentation phase perform **hash-only** verification where safe. Do not retrain, reserialize, regenerate, open private data, regenerate a notebook or execute the Task 2B checker on real-data inputs in an agent session.

## 3. Official booklet crosswalk — what IS and IS NOT official

The following requirements are from the supplied **Challenge Booklet.pdf**, printed pages indicated; wording is paraphrased faithfully. The proposed README structure/test automation is an engineering implementation, **not** an extra official submission requirement.

| Source | Official requirement | Phase 36 README consequence |
|---|---|---|
| p.22, Deliverables | Architecture diagrams: model(s), preprocessing and proposed deployment approach; high-level acceptable | Link to the **actual** architecture file(s), describe what exists vs what is proposed; do not invent deployed service |
| p.22 | Brief preprocessing write-up: preparation, label construction, cleaning, feature engineering, rationale | Link to existing actual Phase 30 write-up; short factual summary only |
| p.22 | Save final model file(s) **alongside the final notebook** | Document model registry and expected submission package relationship without exposing restricted binaries in public docs |
| p.22 | `TeamName_FinalNotebook.ipynb` retains label/preprocess/train/evaluation cells; final cell loads saved Task 1+2A models and prints their inputs and predictions | Document notebook role and **local-only** safe execution; do not claim notebook itself is a clean-room no-data public demo |
| p.22 and p.25 | Output CSV names `submission_task1.csv`, `submission_task2a.csv`, `submission_task2b.csv`; exact template identifiers; Task 1 preserves original row order | Make filenames and column schema explicit; never expose real rows; README links should not imply CSVs may be redistributed |
| p.21–22 | Task 2B peak-day allocation + approximately one-page-or-less written prioritization policy showing calculations and deferral reasoning | Link to actual policy and describe feasibility / prioritization vs official checker limits |
| p.22 | 3–5 minute **unlisted YouTube** Datathon demo on model architecture, preprocessing, label construction and challenges | Link to *existing* video only if URL is verified; otherwise `PENDING — Phase 38`; don't invent URL |
| p.22 | AI-tool disclosure: which work was AI-assisted, not AI-assisted, and how tools were used | Link to the truthful existing disclosure and show actual approval state; don't assert cleared when Phase 35 blocked |
| p.22, Rules/Terms | Restricted pretrained predictors, proprietary modelling/preprocessing APIs and automated/low/no-code modelling; competition data is confidential and must not be transmitted to third parties | No public private-data links, no upload instructions, no unsupported compliance certification; refer to factual disclosure/organizer-specific guidance if verified |
| p.23 | One folder zipped as `TeamName_Datathon.zip`, upload via official form by **Friday, 9 October 2026, 11:59 PM Sri Lanka time** | Document future packaging flow as Phase 40–42, not completed work; final submission/upload is a human action |
| p.23, Judging | Data/labels 20%; models/architecture 25%; performance 20%; Task 2B feasibility/policy 15%; creativity 10%; demo 10% | README navigation should help judges find evidence; percentages optional and sourced if included |

**Critical distinction:** the booklet's Datathon deliverable list **does not name `README.md` specifically**. The README is required by the finalized **WayLoom Phase 36 master-plan work**, subject to the exact local task text. It must not replace any booklet-required file. The PDF also does not require Docker, an online app, FastAPI service, hosted UI, or Hackathon integration for Datathon; do not claim any of these as Datathon deliverables without local evidence.

## 4. Complete 8-ID Phase 36 task inventory — reconciled

The canonical local master-plan Phase 36 section was inspected before implementation. Its exact inventory is:

| Status | ID | Exact master-plan work item | Mark / priority / dependency |
|---|---|---|---|
| [x] | **DT-456** | Write Datathon README | [E] / P1 / Stable repository and outputs |
| [x] | **DT-457** | Explain project objectives | [E] / P1 / Stable repository and outputs |
| [x] | **DT-458** | Explain folder structure | [E] / P1 / Stable repository and outputs |
| [x] | **DT-459** | Explain environment setup | [E] / P1 / Stable repository and outputs |
| [x] | **DT-460** | Explain how to run notebook | [E] / P1 / Stable repository and outputs |
| [x] | **DT-461** | Explain model files | [E] / P1 / Stable repository and outputs |
| [x] | **DT-462** | Explain how outputs are generated | [E] / P1 / Stable repository and outputs |
| [x] | **DT-463** | Document random seed/reproducibility | [E] / P1 / Stable repository and outputs |

**Accounting:** 8 unique IDs; no missing or duplicate tasks: DT-456, 457, 458, 459, 460, 461, 462, 463. All eight remained `[ ]` during implementation and review, then changed to `[x]` only in the explicitly authorized administrative closure after the fresh independent re-review PASS.

### Mandatory evidence extract for implementation session

```text
LOCAL MASTER PLAN: MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md
PHASE36 STATUS ON ENTRY: eight task flags [ ]; Phase complete [ ]; READY FOR NEXT PHASE NO
DT-456 = Write Datathon README; mark=[E]; priority=P1; dependency=Stable repository and outputs
DT-457 = Explain project objectives; mark=[E]; priority=P1; dependency=Stable repository and outputs
DT-458 = Explain folder structure; mark=[E]; priority=P1; dependency=Stable repository and outputs
DT-459 = Explain environment setup; mark=[E]; priority=P1; dependency=Stable repository and outputs
DT-460 = Explain how to run notebook; mark=[E]; priority=P1; dependency=Stable repository and outputs
DT-461 = Explain model files; mark=[E]; priority=P1; dependency=Stable repository and outputs
DT-462 = Explain how outputs are generated; mark=[E]; priority=P1; dependency=Stable repository and outputs
DT-463 = Document random seed/reproducibility; mark=[E]; priority=P1; dependency=Stable repository and outputs
PHASE36 MASTER COMPLETION GATE: README allows a reviewer/team member to understand and reproduce the Datathon workflow.
PHASE35 GATE: OPEN; Phase36 documentation is independently permitted because its named dependency is Stable repository and outputs.
PROVISIONAL VS MASTER DIFFERENCES: the draft workstreams were reordered and narrowed to the eight exact titles above.
```

## 5. Input/output contract and strict file ownership

### 5.1 Source materials the agent MAY inspect, if present

- `README.md` source, `docs/**/*.md` that contain **sanitized** descriptions, `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md`, Phase 29 architecture, Phase 30 preprocessing, Phase 31 notebook contract/source (unexecuted cell text only), Phase 32 registry schema metadata (no model deserialization), Phase 33 submission-schema contract, Phase 34 test traceability, Phase 35 **public-safe** disclosure status.
- `src/` and `scripts/` **source definitions only** to discover actual public CLI flags, imports and file paths; relevant `configs/*.yaml` absent secrets, dependency manifests, `pytest.ini`, `.gitignore`, `AGENTS.md`, handoff.
- `outputs/` **filenames, existence and SHA256 only**, not content; registry **paths, SHA256, byte lengths and serializer metadata only**; no dump of private registry paths into public README if harmful.
- Local executed test summaries described in prior human reports can be labelled `HUMAN_LOCAL_REPORTED`; do not attribute them to a fresh agent rerun.

### 5.2 Allowed owned outputs

| File | Type | Purpose / limitations |
|---|---|---|
| `README.md` | **Primary, preferred** | Entry point, problem, task interfaces, methodology overview, environment/setup, verified safe commands, deliverable map, limitations/privacy |
| `docs/DATATHON_JUDGE_WALKTHROUGH.md` | Optional, only if actual master calls for or root README becomes too dense | Source-backed, minimal judge navigation; must not duplicate or conflict with README; no fabricated metrics |
| `docs/PHASE36_DOCUMENTATION_TRACEABILITY.md` | Optional internal | Eight task IDs mapped to README sections, files, source/proof, pending validations. No private content |
| `tests/test_phase36_documentation.py` | Recommended safe deterministic tests | Validate required headings, links, approved tool claims, private-path exclusion, code block sanity, task references, blocker markers |
| `MD Files/PHASE_36_COMPETITION_CONTRACT.md` | Contract | Status/checklist remains pending until evidence/review; only update task wording to match master during implementation |
| `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` | **Read-only during implementation** | May be updated **only after** a separate independent review PASS and explicit administrative closure action |

**Do not create fake files just to make relative links pass.** If an artifact is expected in a later phase, label `Planned / pending (Phase ##)` as plain text instead of creating an empty placeholder. Avoid adding a large new `docs/` hierarchy unless warranted by exact master items.

### 5.3 Required README outputs / audience

- **Technical judge:** knows where notebook, models, CSVs, written policy, architecture and preprocessing documents belong.
- **Team operator:** gets actual local-setup/validation commands, prerequisites, dependency pinned paths and safe expected outputs.
- **Independent reviewer:** can trace every *implemented* claim to code/source, clearly distinguish local reported proof and synthetic-only verification, and spot what is pending.
- **Submission organizer:** receives concise, factual disclosure cross-references and no false certification or private-record links.

## 6. README information architecture — recommended, adaptable to exact master

Use this order unless the canonical master prescribes another:

1. `# WayLoom — Rootcode Tech-Triathlon 2026 Datathon` + one-paragraph problem/mission, 3-task overview, **Datathon scope only**.
2. `## Challenge and Task Overview` — Task1 service duration/late probability, Task2A volume/chilled forecast, Task2B peak-day served/deferred allocation.
3. `## Key Deliverables` — exact CSV names/column lists, final notebook/model files, preprocessing & architecture docs, Task2B written policy, video & disclosure status; no local private file links intended for publishing.
4. `## Approach / Architecture` — frozen Task1 CatBoost services; Task2A CatBoost/LightGBM ensemble; Task2B deterministic allocation optimizer; Phase32 secure registry, source-linked and status-qualified.
5. `## Repository Layout` — meaningful current directories and actual nonsecret file paths; not a stale idealized tree.
6. `## Requirements and Local Environment` — actual supported Python version and requirements manifest from source, OS notes (Windows PowerShell is a known operator environment), CPU/RAM only if documented, no fabricated GPU requirements.
7. `## Setup and Validation` — installation **optional / only if dependency path verified**, correct `.venv` kernel if Jupyter, safe test commands and expected summary without exact invented counts; private runs clearly human-local.
8. `## Inference and Reproducibility` — final notebook last-cell saved-model demo, safe synthetic smoke path if exists; include only commands that are inspectable and verified; **no download/upload instructions for restricted datasets**.
9. `## Evaluation and Evidence` — link to existing Phase 37 planned results only if real; do not invent accuracy, RMSE, MAE, optimization scores, or production deployment claims.
10. `## Task 2B Constraints and Written Prioritization` — brief rule crosswalk; link to actual policy.
11. `## Privacy, AI-Use and Data Handling` — confidentiality, synthetic-only documentation examples, factual AI use disclosure reference and its current unresolved human status without raw incidents/data.
12. `## Troubleshooting and Limitations` — safe common problems (wrong kernel, missing private files, checksum mismatch, Windows symlink privilege, missing env var), and clear what judges can run without restricted files.
13. `## Documentation / Judge Navigation` — table with actual relative paths; label unavailable future artifacts.

**Editorial target (engineering suggestion):** readable root README (about 1,200–2,500 words plus short code snippets), concise supporting docs where required; this is **not** an official word limit. Prefer a README that is shorter than the aggregate of the architecture + preprocessing documents and links to those source documents.

## 7. Detailed Phase 36 task-by-task engineering contracts

The following eight implementation contracts use the exact master-plan titles. The older draft workstream notes that follow are retained only as cross-cutting safety guidance and are not alternate task definitions.

### DT-456 — Write Datathon README

Create the root `README.md` as the concise project entry point. It must explain the Datathon scope, link existing public-safe evidence, distinguish implemented/pending items, contain one H1, and use only valid repository-relative links. It must not claim the booklet mandates a README or that a pending phase is complete.

### DT-457 — Explain project objectives

Explain Task 1 service/lateness prediction, Task 2A 10-week total/chilled forecasting, and Task 2B allocation/deferral as separate objectives. State all three exact output filenames and column orders, identifier/order guarantees, and core business constraints without private examples or invented metrics.

### DT-458 — Explain folder structure

Map the actual notebook, production modules, shared modules, configs, scripts, models, outputs, docs, tests, phase records, and restricted local areas. The map must distinguish controlled/private artifacts from publishable documentation and match the current repository tree and ignore policy.

### DT-459 — Explain environment setup

Document the recorded Python 3.13.7 Windows PowerShell reference environment, virtual-environment creation, lock/direct requirement manifests, dependency verification, and direct-interpreter fallback. Do not invent Docker/GPU/cloud requirements or imply dependency installation fetches competition data.

### DT-460 — Explain how to run notebook

Document the source-only notebook validator and the actual `execute_final_notebook.py` run-all command/flags. Explain the disposable ignored executed copy, authorized human-local data boundary, 7,200-second configured timeout, clean-kernel evidence provenance, and prohibition on overwriting the source notebook or official outputs.

### DT-461 — Explain model files

Explain the authoritative 12-entry Phase 32 registry; Task 1 CatBoost bundles; Task 2A CatBoost/LightGBM ensemble bundles; metadata, schemas and manifest; relative paths, sizes, hashes, runtime versions, and checksum-before-deserialization controls. State that Task 2B is optimization and has no predictive-model artifact.

### DT-462 — Explain how outputs are generated

Describe the three frozen generation paths from validated inputs through features/inference or optimization to exact template mapping and final validation. Explain that Phase 33 is read-only and that documentation/review work must not retrain, rerun inference/optimization, regenerate, normalize, or reorder official outputs.

### DT-463 — Document random seed/reproducibility

Document seed 42, lockfile/runtime metadata, chronology controls, deterministic/single-thread settings where configured, notebook `PYTHONHASHSEED`, and the limits of seed-based reproducibility. Distinguish frozen hash integrity from retraining and label clean-environment reproduction as pending Phase 39.

### Cross-cutting draft guidance retained for safety

The notes below supplied useful edge cases, privacy checks, and reviewer expectations before the local task titles were available. They supplement the exact contracts above but do not change their identity or completion state.

#### Supporting note — README and navigation

**Objective.** Create/strengthen the root-level project entry point. Explain what WayLoom Datathon actually solves and give immediate access to all required competition deliverables without duplicating the full technical reports.

**Source inputs.** Local master task text; current root README; official p.22/p.23; Phase 29/30 docs and actual tracked folder names. **Output.** `README.md`, links to real local files, durable section navigation and clear Datathon-only scope.

**Implementation steps.** (1) Inspect actual README and avoid destructive rewrite of useful verified information. (2) Extract exact master acceptance. (3) Draft precise project tagline and role of three tasks. (4) Add high-signal top-of-file quick navigation and maturity/status labels. (5) Use only repository-relative links, no `C:\Users\...` paths, localhost tokens, internal private paths, placeholders pretending to be finished outputs or confidential examples. (6) Differentiate reference methodology vs executed status for all late phases. (7) Keep markdown accessible and compatible with GitHub/Cursor.

**Assertions / tests.** Exactly one H1; functional relative links for existing public-safe docs; no duplicate misleading major headings; no broken local anchor; no fabricated badges/results/date/official README requirement; README renders as plain Markdown; no unsafe external disclosure.

**Edge cases.** Existing README has valuable content; non-ASCII markdown; links to paths with spaces; future docs missing; user may submit packaged version omitting development-only files. **STOP:** no reliable current repository structure, local Phase 35 gate forbids docs changes, or README demands embedding restricted rows. **Done when:** verified README root entry point exists, links and claims are source-backed, and approved task title matches master.

#### Supporting note — challenge scope and task interfaces

**Objective.** Give a task-by-task explanation that a judge can match to official templates and code, without conflating Task 1 supervised prediction, Task 2A weekly forecasting or Task 2B allocation.

**Source inputs.** Official booklet pp. relevant Task1/Task2A/Task2B and p.25 submission templates; existing Phase 33 schema contract, code/data schema constants. **Output.** README task table, exact CSV schema references and inputs/outputs text; no row-level data.

**Implementation steps.** Document Task1 predictions `delivery_id,pred_service_min,pred_late_prob` and preservation of ID/order; Task2A `row_id,pred_total_volume_m3,pred_chilled_volume_m3` with ten weekly horizons, requested-date ISO grouping from both authoritative history sources; Task2B `scenario,order_ref,outlet_id,decision,vehicle_id,trip_id` with `order_ref` key, served/deferred, blank deferred assignments. Explain outcome times unavailable to inference and separate Task2B feasibility from solver optimality. Link to official write-up and output contract sections only if present. Avoid unsupported simplifications about all depots/brands or vehicle availability.

**Assertions / tests.** Three distinct task sections; exact filenames and column-order checked against source; no inferred official metric values, no placeholders or private ID examples; row-order rule specifically for Task1; no mistaken `outlet_id` uniqueness assertion for Task2B.

**Edge cases.** Real file output absent on a cloned public repo; Task 2B template has duplicate outlets; forecast ISO year rollover; all-deferred allocation still valid format. **STOP:** schema differs from booklet/template without formal clarification; cannot find Phase33 verified schema contract. **Done when:** reviewer can reconstruct expected interfaces from docs without accessing private records.

#### Supporting note — environment and safe installation

**Objective.** Give reproducible local **setup guidance**, clearly separated from Phase 39's later clean-environment *execution* gate.

**Source inputs.** Real `requirements*.txt`, `pyproject.toml`, `environment.yml`, `.python-version`, current `.venv` setup, Jupyter metadata, CI workflows if any. **Outputs.** Source-checked requirements, Windows PowerShell + optional cross-platform equivalents, activation, install, `pip check`, safe smoke/pytest commands, optional Jupyter `.venv` kernel instructions.

**Implementation steps.** (1) Discover actual Python/runtime version from tracked requirement markers rather than assume. (2) Identify exact dependency installation command based on repository file; no unattended network installs in agent review. (3) Include `python -m venv .venv`, PowerShell `.\.venv\Scripts\python.exe` variants only when compatible; optional bash commands clearly labeled. (4) If notebook execution described, show proper `ipykernel` registration, restart/final-last-cell distinction, local-only/private-data caveat. (5) Explain pinned dependencies/version variance; mark untested OS as unverified. (6) Document import sanity, `pip check`, safe pytest, and don't confuse synthetic suite with official checker/private competition validation.

**Assertions / tests.** All referenced files actually exist; all CLI `--flag` values match real `--help`/argparse source; no fictitious `make`, Docker, `conda`, `python3`, `scripts/run_everything.py`; no dependency install inside test collection; required PATH shells clearly labeled.

**Edge cases.** Windows symlink skips, wrong Jupyter kernel, missing `joblib` in system kernel, expected private-data paths absent, virtual-env path contains spaces, no network. **STOP:** actual version/dependency manifest not discoverable; setup demands credentials or private data in public README. **Done when:** judge/operator can follow setup without inventing commands or transmitting restricted files.

#### Supporting note — repository layout and data boundaries

**Objective.** Teach judges where safe code, docs, tests, configs, official deliverable *locations* and private input areas are, without leaking private data or suggesting Git-staging it.

**Inputs.** `git ls-files`, `rg --files`, `.gitignore`, current structure, source imports, relevant approved contracts. **Outputs.** Up-to-date compact code tree / directory-role map in README, clear safe-vs-restricted boundaries and ownership.

**Implementation steps.** Identify `src/task1`, `src/task2a`, `src/task2b`, `src/common` only when they truly exist; map `configs`, `scripts`, `tests`, `docs`, `MD Files`, `models`, `outputs`, `data`. Mark each as public-safe or potentially sensitive. Differentiate tracked source from locally generated protected output; verify actual filenames without opening the files. Add one-sentence data-handling rule: no raw competition data, private predictions, executed notebooks, secret files in public repo/logs. Flag output artifact checksums as verification evidence, not a license to redistribute them.

**Assertions / tests.** Tree names match actual repo; no real file samples; `.gitignore` actually covers `reports/private/**`; link target exists or is labelled pending; no stale references to older architecture or Legacy loader as authoritative.

**Edge cases.** Public release may omit confidential dataset/model files; Gitignored files exist locally but no safe link can be made; a local `Untitled.ipynb` shouldn't be documented. **STOP:** there are tracked private files, a public link reveals restricted data, or an actual path can't be reconciled. **Done when:** layout and restrictions are accurate and safe for repository distribution.

#### Supporting note — model and optimizer methodology

**Objective.** Explain the final engineering approach at the right level for README and direct readers to deeper Phase 29 architecture/Phase 30 preprocessing/Phase 24 policy.

**Inputs.** Frozen source implementations, model registry metadata, architecture/preprocessing document, Phase31 approved notebook source, Phase32/33 validation summaries. **Outputs.** Concise, source-backed workflow section (textual flow and optional existing diagram link) separating Task1, Task2A, Task2B.

**Implementation steps.** For Task1 describe label waiting exclusion, strict lateness `arrival > close`, pre-event-safe features, local CatBoost saved-service and late-probability models, calibration/positive-class behavior only if source evidences it. For Task2A explain authorized history (`deliveries_train` + `task1_test_inputs`, each order once, cross-source duplicates fail closed), requested-date ISO calendar, local CatBoost/LightGBM ensemble and chilled constraints (Fresh only, Style/Tech zero, chilled <= total), without inventing weights beyond config. For Task2B explain S1 vehicle/order feasibility, brand/district/depot/reefer/van-only/capacity, max two trips, no return leg, 270/480 budget and policy/optimizer evidence. Cite official 101-minute example only as *booklet example*, not achieved final trip. Mention hash-verified Phase32 registry for saved-model inference. Keep deployment **proposed** if not built; Datathon need not prove Hackathon integration.

**Assertions / tests.** Source references for each substantive claim; no claim unseen private backtest metrics; no claims all orders served or optimizer proven optimal without exact separate proof; no historic forbidden feature leakage; no silent cross-source duplicate precedence; correct model names and registry relationship.

**Edge cases.** One output model served by ensemble, immutable hash metadata; different brands/forecast weeks; frozen Task2B policy contains a value not in public source. **STOP:** contract/code contradiction, unsupported inference, request to rerun training to write docs. **Done when:** judge understands the actual three-pipeline architecture and can locate deeper proof.

#### Supporting note — commands and judge walkthrough

**Objective.** Supply an honest, reproducible **navigation** and local demonstration route while keeping Phase 39 clean-environment reproduction and Phase 40 packaging as future gates.

**Inputs.** Existing actual CLI scripts and `--help` contracts; `.venv`, unit tests, notebook final cell, Phase32 registry loader, Phase33 local check evidence. **Outputs.** README command table and optionally `docs/DATATHON_JUDGE_WALKTHROUGH.md` for a 5–10-minute judge review.

**Implementation steps.** Start from `README` and find official templates/CSV outputs by filenames; review notebook source; run safe synthetic pytest with project `.venv`; optionally inspect source for stable secure artifact metadata; point to validated submission files by filename but **never display rows**. Separate: (A) `agent-safe tests`, (B) `human-local restricted-data notebook/checker commands` requiring authorized user, (C) later clean-environment execution in Phase 39, (D) final packaging/upload Phase 40–42. Show clearly what results mean and what they do not prove. If no CLI exists for an action, write "manual source inspection" or a verified notebook instruction, not a fictional command. Prevent commands overwriting existing private validation reports.

**Assertions / tests.** Every command parses under source CLI / `--help` where feasible, no command uses private data in agent context, no `pytest` without safeguards if suite has side effects, no fake GPU/cloud requirements; judge path table points to true current files and marks unknowns.

**Edge cases.** `.venv` not created; Jupyter system kernel wrong; `safe_validation.json` validator would overwrite private proof; internet offline; official checker requires private inputs; videos not yet uploaded. **STOP:** command may mutate frozen models/submissions, leak restricted data, or require side-effecting validator. **Done when:** a new operator can navigate and safely validate the documented public/synthetic aspects.

#### Supporting note — deliverables, evidence and limitations

**Objective.** Make README competition-complete *as an index*, not as a replacement for the official deliverables or Phase 37 results report.

**Inputs.** Booklet p.22–25; Phase29 architecture, Phase30 preprocessing, Phase31 notebook, Phase32 model registration, Phase33 CSVs, Phase24 Task2B written policy, Phase35 disclosure current approval state, Phase37/38 planned artifacts. **Outputs.** Key-deliverable table with official requirement, actual path(s), available/pending, permissible review/usage, and owner if verified.

**Implementation steps.** Link real architecture diagram(s); actual preprocessing document; notebook model registry; CSV filenames; Task2B prioritization policy; AI disclosure; video **ONLY if verified unlisted URL**; future result summary if present, or explicitly pending Phase 37. Distinguish evidence tags such as `[SOURCE VERIFIED]`, `[HUMAN-LOCAL REPORTED]`, `[PENDING]` from official score. Document limitations: private datasets unavailable in public checkout, time/fleet constraints, synthetic tests vs private checker, model trained locally, performance only if metrics trace to sanctioned logs. Document known Phase35 unresolved approval in a neutral factual way; do not replace or bury it. If master instructs README embedding results, use approved sanitized aggregate numbers, not invented scores.

**Assertions / tests.** Required booklet items covered exactly; every existing path link resolves; no fabricated demo URL, organizer approval, metric, judge outcome, deployment/endpoint. User can locate policy and existing source files without access to `reports/private`.

**Edge cases.** Required item technically ready but not yet included in final ZIP; disclosure draft approved? check actual; video URL absent; named package `TeamName_Datathon.zip` not assembled until Phase42. **STOP:** required file absent and README falsely declares it completed; disclosure may misrepresent organizer guidance. **Done when:** deliverable index is accurate, permission-aware and actionable.

#### Supporting note — documentation QA and independent-review readiness

**Objective.** Provide automated and human-readable proof that README and any companion docs are coherent, accurate, safe and consistent with the current repo, without substituting a checker for factual human approval.

**Inputs.** Final candidate README, local Phase36 master tasks and gate, official booklet, actual safe paths and text source, prior-phase approvals, baseline SHA256. **Outputs.** `tests/test_phase36_documentation.py` or existing safe doc tests; optional sanitized traceability, verification report and exact task checklist.

**Implementation steps.** (1) Build task→README section→source→verification map for all 8 IDs with exact master labels. (2) Implement deterministic tests for key headings, relative links, no local user paths/tokens/raw-data inclusion, official filenames/columns, real command references, status honesty. (3) Detect unsupported claims using targeted manual code/doc crosswalk; no superficial heading-only proof. (4) Run tests against repo version and provide expected safe human-local validations when unavailable to agent. (5) Ensure frozen hashes/Git hygiene before/after. (6) Submit to **new, read-only independent review**; leave master task boxes and flags open until approval/authorized admin closure.

**Assertions / tests.** Eight distinct IDs exact in traceability; links resolved or pending; no privacy contents; no stray debug/empty placeholder; README command syntactic sanity; doc tests fail on intentionally broken link/incorrect official column name; `git diff --check` and `pip check` pass. Run phase tests/full-safe suite if authorized and safe; report skipped tests and evidence provenance accurately.

**Edge cases.** Broken relative links with spaces; Markdown anchor collision; separate OS path semantics; root README pre-existing; unrelated Git edits; Phase35 gate remains open; privacy scanner false positives due to mere schema column names. **STOP:** leaked restricted row/sample, frozen hash difference, mandatory Phase35 precondition unmet, false claim of README completion or user approval. **Done when:** independent reviewer can audit all 8 tasks, all documentation claims and safety results, and authorize formal closure under actual master gates.


---

## 8. Machine-checkable acceptance matrix and test design

**Engineering tests supplement, but never replace, source review or human sign-off.** Reuse existing testing infrastructure; do not create a fragile parallel framework. Candidate nodes below are suggested names, not claims that the files/tests already exist.

| Check ID | Applies to | Suggested safe test/evidence | Required acceptance |
|---|---|---|---|
| DOC-01 | DT-456 | `test_readme_is_coherent_and_covers_all_phase36_sections` | README exists and is parseable with coherent headings |
| DOC-02 | DT-456,458 | `test_all_local_markdown_links_resolve` | Public-safe actual linked files exist; future deliverables never masquerade as broken links |
| DOC-03 | DT-457,462 | `test_official_filenames_and_columns_match_phase33_config` | Exact three filenames and Task1/2A/2B schema/order preserved |
| DOC-04 | DT-457,462 | `test_task_rules_and_output_generation_are_not_conflated` | Correct Task1 strict lateness/waiting rule, Task2A demand/chilled rules, and Task2B constraints |
| DOC-05 | DT-459,460 | `test_documented_cli_entrypoints_and_manifests_exist`; `test_documented_notebook_command_uses_configured_private_output` | Actual referenced file/function/flags, configured private output path, shell and safe mode |
| DOC-06 | DT-456,458 | `test_pending_status_and_public_safety_fail_closed` | No real rows, personal paths, secret-like tokens or leaked private notebook outputs |
| DOC-07 | DT-458 | `test_readme_is_coherent_and_covers_all_phase36_sections` plus manual tree check | Path tree matches repo / ignore policy |
| DOC-08 | DT-461,462 | Manual source-to-claim trace audit | Local saved models and deterministic solver/output paths described accurately, no invented metrics |
| DOC-09 | DT-459,460,463 | `test_setup_notebook_models_outputs_and_reproducibility_are_factual` | Commands and reproducibility statements match actual configuration |
| DOC-10 | DT-456,462 | Deliverables/status table plus link test | All actual official deliverables navigable or explicitly pending |
| DOC-11 | DT-456 | `test_pending_status_and_public_safety_fail_closed` | Phase35 draft/pending represented accurately, no blanket organizer clearance |
| DOC-12 | All | `test_master_inventory_and_traceability_are_exact_and_open` | Exactly eight IDs, exact local-master names/marks after reconciliation |
| DOC-13 | All | Before/after metadata/hash guard | Three official CSVs, registry and 12 artifacts unchanged |
| DOC-14 | All | `git diff --check`, status/ignore check | No private files staged or tracked, no unexpected production changes |
| DOC-15 | All | Fresh read-only independent review | Every task substantiated; formal closure only with authorized review PASS |

**Required mutation/negative assertions for new tests:** broken relative link -> fails; unknown documented script -> fails; deliberate incorrect `submission_task2a.csv` column -> fails; fabricated video URL/status -> flagged; `C:\Users\...` hard-coded Windows profile path -> flagged; real sample output pasted -> blocked; duplicated task ID -> fails. Avoid tests that require presence of private datasets or enforce arbitrary editorial preferences in absence of a master requirement.

**Stable test approach:** `pytest` over source+sanitized docs using `pathlib`, test monkeypatch/temp fixtures; avoid external requests and notebook execution. For Windows symlink cases elsewhere, report skip reasons honestly. Run `pytest -q -p no:cacheprovider` with OS-temp basetemp where safe; avoid validators that overwrite preserved Phase32 private reports. Do not run privacy checker against confidential contents or print them.

## 9. Safe command inventory — VERIFY BEFORE PUTTING IN README

This is an engineering **candidate** for local Windows PowerShell; only advertise commands whose prerequisites and paths really exist. **Do not confuse commands authored in this contract with commands already validated in local repository.**

```powershell
# At repository root; not a requirement to download private data.
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_phase36_documentation.py
git diff --check
git status --short
git diff --cached --name-only
```

> **Verification rule:** confirm the actual `.venv` Python path before copying commands into README. This contract does not establish the existence of any optional test file or script.

**Better read-only prior-to-implementation checklist (non-executing):**

```powershell
# Inspect only safe tracked text; do not read private inputs.
git status --short --branch
git diff --name-only
git ls-files README.md docs tests scripts configs
rg --files docs tests scripts configs
```

**Do not suggest:** `git add .`, `git clean -fd`, destructive notebook Run All in an agent context, curl upload of competition CSVs, untrusted pickle loads, deleting/private-report overwrites, running unofficial `check_allocation.py` commands with assumed flags, or posting private data to GitHub for reproduction.

## 10. Practical source-to-claim evidence worksheet

| README claim | Required local proof | How to state if absent |
|---|---|---|
| "Final Task1 CatBoost pipeline" | Phase32 trusted registry metadata + actual inference source/Phase31 notebook | "Model architecture described in [actual docs]; artifact verification pending" |
| "Task2A CatBoost/LightGBM ensemble" | Registry/config with exact composition and preprocessing | Don't write a fixed 50/50 weight unless registry/Phase17 final config establishes it |
| "Task2B optimizer is feasible/optimal" | Specific approved independent solution-audit/status, NOT solely official checker | "Produces a tested allocation subject to hard rules" if no optimality proof |
| "Clean Run All / final last-cell only" | Phase31 human-local closure result (sanitized) | "Human-local check recorded; not independently rerun here" |
| "Artifacts trusted" | Phase32 registry and checksum-before-load path; verified actual safe tests | "Validation controls implemented" until tested |
| "Final performance score" | Phase37 verified metric report / immutable evidence | `PENDING` / omit score, never invent numbers |
| "Demo video available" | Actual unlisted YouTube URL from team | `PENDING (Phase 38)` |
| "AI disclosure approved" | Current authorized team signoff and independent review verdict | `DRAFT — HUMAN APPROVAL PENDING` if that is true |
| "Phase 36 officially complete" | Master task checkmarks, report + fresh independent PASS + admin update | `IN PROGRESS` until gate actually met |
| "Reproducible end-to-end" | Phase39 clean-env successful execution proof | "Local setup documented; clean-environment verification pending" |

## 11. Readme acceptance rubric (reviewer may score, not an official competition rubric)

Use objective PASS/FAIL rather than inflated quality scores:

1. **Task coverage:** 8/8 exactly reconciled to actual master.
2. **Booklet fidelity:** official deliverables/task interfaces/constraints correct and labelled.
3. **Link hygiene:** root README and linked local documents resolve or pending is explicit; no fabricated artifacts.
4. **Operational clarity:** source-matching commands, shell/OS/kernel notes, no hidden state assumptions.
5. **Method fidelity:** three approaches reflect frozen code, not speculative architecture.
6. **Privacy honesty:** no sensitive content; reported Phase35 limitations accurately distinguished from formal clearances.
7. **Evidence provenance:** don't misattribute human-run private checks to agent tests; no fake performance.
8. **Scope:** does not prematurely implement Phase37–42 or modify protected artifacts.
9. **Regression:** safe documentation tests, pip/diff/hash safety checks pass.
10. **Governance:** independent fresh review PASS and explicit admin closure only after prerequisites.

## 12. STOP conditions (mandatory, precedence over speed)

- **If** the actual local master plan requires Phase 35 formal closure before Phase 36, and Phase 35 remains open, **stop formal Phase36 implementation**; allow only explicitly permitted preparatory draft work. Do not assume an undocumented dependency.
- Exact Phase36 master title, dependency, priority or acceptance criterion cannot be extracted or reconciled.
- Official booklet/templates disagree with current README schema or task interpretation; report source conflict rather than rationalize.
- Agent needs to open confidential rows, produce real data samples or transmit private content; always stop.
- A README command would run training, official submissions, private checker or unsafe model loads without explicit separate human approval.
- Documentation needs to claim human AI-disclosure attestation, organizer blanket exemption, independent review or performance result that has not occurred.
- Frozen submission/registry/model bytes change or Git reveals accidental protected-file modification.
- Any required doc deliverable is absent and cannot be labelled pending honestly.
- Documentation QA cannot distinguish synthetic test proof from real private validation.
- A test can only pass by changing frozen source/official outcomes; stop and escalate.

## 13. Definition of Done — 16 evidence-backed checks

Do not check any item without supporting proof; **Phase36 is not formally done simply because README text exists**.

- [x] 01. **Master reconciliation:** extracted exact DT-456–DT-463 titles/marks/priorities/dependencies and updated this contract accordingly.
- [x] 02. **Phase dependency gate:** current master authorizes phase work or records only preparatory drafting pending Phase35 closure.
- [x] 03. **Primary document:** root `README.md` is concise, present, coherent, and has functional links.
- [x] 04. **Task scope:** Task1/Task2A/Task2B correctly explained and distinguish actual inputs, algorithms and outputs.
- [x] 05. **Official artifacts:** booklet deliverable crosswalk includes all required categories and exact filenames.
- [x] 06. **Source integrity:** all implementation claims trace to frozen code/configs or properly labeled human-local proof.
- [x] 07. **Setup fidelity:** Python/dependency/Jupyter instructions match actual repo and verified supported environment.
- [x] 08. **Commands:** all documented scripts/arguments/shell variants exist and safe statuses are labelled.
- [x] 09. **Data boundaries:** no restricted data/IDs/predictions/credentials/secret URLs/absolute local personal paths.
- [x] 10. **No false results:** no fabricated performance, optimizer outcome, YouTube video, deployment or organizer sign-off.
- [x] 11. **Factual AI status:** truthful reference to Phase35 disclosure and its actual human approval status.
- [x] 12. **Links and layout:** relative links valid and current project tree accurate; pending items explicit.
- [x] 13. **Tests:** targeted documentation tests and safe suite completed (or a disclosed prerequisite block, not silent PASS).
- [x] 14. **Integrity:** frozen CSV SHA256, registry and twelve artifacts unchanged; Git privacy and `diff --check` pass.
- [x] 15. **Review:** independent **fresh read-only** Phase36 review PASS with 8 individual task verdicts.
- [x] 16. **Administrative closure:** required completion report and master `[x]`/READY flags updated only in separate authorized action after review/prerequisites.

**Completion accounting:** DT-456 through DT-463 = 8/8 required verified verdicts, 0 missing; do not translate blocked/ready-to-review into PASS.

### 13.1 Formal completion report — 9 October 2026

**Final status:** Phase 36 is formally complete. DT-456 through DT-463 are 8/8 PASS, and the fresh independent re-review explicitly authorized this separate administrative closure.

| Task | Exact work item | Final verdict | Completion evidence |
|---|---|---|---|
| DT-456 | Write Datathon README | PASS | Root README structure, navigation, links, scope, pending-status honesty and privacy controls independently verified. |
| DT-457 | Explain project objectives | PASS | Task 1, Task 2A and Task 2B objectives and official output interfaces independently verified. |
| DT-458 | Explain folder structure | PASS | Repository layout and restricted-data boundaries independently verified against the actual tree and ignore policy. |
| DT-459 | Explain environment setup | PASS | Python 3.13.7, virtual-environment, dependency-lock and validation instructions independently verified. |
| DT-460 | Explain how to run notebook | PASS | Executor CLI, configured private output directory, Windows containment semantics and negative path cases independently verified after repair. |
| DT-461 | Explain model files | PASS | Twelve-entry Phase 32 registry, model families, schemas and checksum-before-load safeguards independently verified. |
| DT-462 | Explain how outputs are generated | PASS | Distinct Task 1, Task 2A and Task 2B generation paths and no-regeneration restriction independently verified. |
| DT-463 | Document random seed/reproducibility | PASS | Seed 42, `PYTHONHASHSEED`, deterministic validation settings, dependency controls and limitations independently verified. |

**Review history preserved:**

- The first independent Phase 36 review returned **FAIL** on DT-460. The README placed the disposable executed notebook under `tmp/`, while production `configs/final_notebook.yaml` permits executed output only under `reports/private/phase31_final_notebook`. The original documentation test checked script existence but did not validate the actual `--output` path semantics.
- The repair changed the README destination to the configured ignored private directory without changing executor logic. Documentation tests were strengthened to parse the command and configuration and reject `tmp/`, outside destinations, parent traversal, similar-prefix sibling paths, missing/malformed `--output`, and private-content exposure.
- The subsequent fresh, strictly read-only independent re-review returned **PASS** for DT-456 through DT-463, confirmed the former DT-460 blocker fully resolved, and explicitly authorized formal Phase 36 administrative closure.

**Verification evidence and provenance:**

- Phase 36 targeted documentation tests: **25 passed**.
- Full safe pytest suite: **895 passed, 2 skipped, 4 warnings**. The two skips were host-unavailable Windows symlink-capability branches; warnings were dependency deprecations.
- Final-notebook source validator: **PASS** without executing the private-data notebook; private clean-kernel results were not re-attributed as agent reruns.
- `python -m pip check`: **PASS**; `git diff --check`: **PASS**.
- All three official submission CSV SHA256 values and the artifact-registry SHA256 remained unchanged.
- All **12/12** registered model artifacts matched their registry SHA256 and byte-size metadata; no model deserialization, retraining or regeneration occurred.
- `reports/private/**` remained Git-ignored; no private rows, identifiers, predictions or executed notebooks were inspected or disclosed; no files were staged or committed.
- Phase 35 remains **OPEN** with DT-451 through DT-455 and its completion/readiness flags unchanged. Its formal closure is not the named Phase 36 dependency, and this report does not assert human approval or organizer clearance.
- Phase 37 implementation was **not started** by this closure action.

**Closure authorization:** PASS — update only the Phase 36 master-plan task boxes, phase-complete flag and readiness flag. No other phase status is authorized to change.

## 14. Git workflow — safe, minimal and reviewable

**Before changes:**

1. Confirm active branch, local master and Phase35 status.
2. `git status --short --branch`; `git diff --name-only`; `git diff --cached --name-only`.
3. Snapshot frozen official outputs/registry + all registered artifact checksums from safe metadata without displaying private rows; use ignored report for baseline if needed.
4. `git check-ignore -v reports/private/...` for any private evidence file; do not create tracked private outputs.
5. Record pre-existing tracked/untracked changes, including Phase35 documentation, separately from proposed README changes. **Never reset another phase's edits.**

**During changes:** only allowed README/docs/docs-tests and contract reconciliation; avoid broad auto-format/rebuild; do not alter model files, official outputs, production code, notebooks, registry, Phase35 disclosure or master statuses. Use repo-relative links, review every code fence, preserve historical reports.

**Validation:** relevant safe docs pytest → full suite only if safely authorized → `python -m pip check` → `git diff --check` → no staged files → SHA256 parity → documentation-based review checklist. If tests are skipped or cannot run due to unclosed Phase35 gate, state `NOT RUN` not PASS.

**After implementation:** send task-by-task report and exact paths changed; conduct a brand-new independent read-only review before any task checkmarks/phase completion. **Do not stage, commit, push or prepare a final public repo mirror unless the human explicitly authorizes and confidential-data checks have passed**. Later packaging (Phase40–42) requires separate human submission authorization.

### 14.1 Git workflow sample (Windows PowerShell; adjust to actual project)

```powershell
git status --short --branch
git diff --name-only
git diff --cached --name-only
git check-ignore -v reports/private/phase36_documentation/evidence.txt
# Agent should not stage/commit automatically.
git diff --check
```

Do not create a protected dataset as a dummy `evidence.txt` just to run `git check-ignore`; an unused path may still be checked.

## 15. Phase36 implementation deliverable report template

```text
PHASE36 MASTER INVENTORY EXTRACTED: YES / NO
DT-456 EXACT MASTER TITLE: ... | VERIFIED / PENDING / BLOCKED
DT-457 EXACT MASTER TITLE: ... | VERIFIED / PENDING / BLOCKED
DT-458 EXACT MASTER TITLE: ... | VERIFIED / PENDING / BLOCKED
DT-459 EXACT MASTER TITLE: ... | VERIFIED / PENDING / BLOCKED
DT-460 EXACT MASTER TITLE: ... | VERIFIED / PENDING / BLOCKED
DT-461 EXACT MASTER TITLE: ... | VERIFIED / PENDING / BLOCKED
DT-462 EXACT MASTER TITLE: ... | VERIFIED / PENDING / BLOCKED
DT-463 EXACT MASTER TITLE: ... | VERIFIED / PENDING / BLOCKED
PHASE35 GATE: OPEN / CLOSED / SPECIFICALLY NONBLOCKING BY MASTER
PRIMARY README: CREATED / UPDATED / DEFERRED
SUPPORTING DOCS: <paths>
OFFICIAL BOOKLET CROSSWALK: PASS / FAIL / NOT CHECKED
DOC TESTS: <exact passed/failed/skipped> / NOT RUN
FULL SAFE SUITE: <exact passed/failed/skipped> / NOT RUN
PIP: PASS / FAIL / NOT RUN
GIT DIFF: PASS / FAIL / NOT RUN
FROZEN CSV SHA256: PASS / FAIL / NOT CHECKED
REGISTRY + 12 ARTIFACTS: PASS / FAIL / NOT CHECKED
PRIVATE DATA INSPECTED OR SHARED: NO / YES (must STOP)
FILES CREATED OR CHANGED: <paths>
FRESH INDEPENDENT PHASE36 REVIEW: PENDING
FORMAL PHASE36 CLOSURE: NO
PHASE37 IMPLEMENTATION: NOT STARTED
BLOCKERS: <facts, precise>
```

## 16. Reviewer evidence rubric and acceptable outcomes

- **PASS** only if master prerequisites and all eight exactly titled work items are implemented and source-evidenced, frozen hashes unchanged, privacy preserved, tests meaningful, and no misrepresentations.
- **CONDITIONAL / PREPARATORY DRAFT READY** if README safe drafting is done but Phase35 formal prerequisite blocks implementation; **not** synonymous with formal PASS.
- **FAIL / BLOCKED** if content materially contradicts the booklet, external data safety, unsupported claims or required tasks; do not edit during independent review.
- **Administrative closure** is a separate later action after fresh reviewer PASS plus any outstanding master gating status. Do not advance Phase37 prematurely.

## Appendix A. Official Task 2B time formula reference (for documentation fidelity)

Task 2B official formula:  
`trip_minutes = depot_to_district_freeflow_min + inter_stop_freeflow_min * (n_orders - 1) + sum(service_allowance_min)`  
No return leg; vehicle maximum two trips; combined Fresh 270 minutes and Style+Tech 480 minutes, separate windows. The official Gampaha illustrative trip is `37 + 9*(3-1) + 15 + 15 + 16 = 101 minutes`. If README includes this, label it **official illustrative calculation**, not final WayLoom result.

## Appendix B. Canonical saved hashes — READ-ONLY expected evidence from prior Phase34 report

The previous, human-supplied independent Phase34 closure used these baseline SHA256s (full values for comparison only; recheck local current files in Phase36):

```text
Task1 submission_task1.csv  9e0faa83a8dd1401ebaf72f1b1602dc560049d4a0cfba19676dbb69bf0de7918
Task2A submission_task2a.csv 142842eef5e4a2e7a6db450c19f4062e4a6eb065481aa21720b59556f9edd55d
Task2B submission_task2b.csv 15f98c8abc434811bc8d6db6ce64c4a746d0acd401f9147d7b15c0958d62b431
models/artifact_registry.json eb1491b782f835cd7ec5046980d3ea234c9a69e68e006a4eef885f1feef5c82d
```

These are **prior-user-reported baselines**, not independently rechecked in this artifact-authoring session. Do not copy raw private files into external tools to verify them. Preserve the model registry's twelve SHA256+size records and recompute only on the authorized local machine via hash-only processes.

## Appendix C. Cursor/Codex prompts

The full self-contained prompts are embedded below **and also delivered as separate `.txt` files** alongside this contract:

- `PHASE_36_CODEX_CURSOR_IMPLEMENTATION_PROMPT.txt`
- `PHASE_36_FRESH_INDEPENDENT_REVIEW_PROMPT.txt`

**First run:** implementation-mode agent may edit only the approved docs/tests (and reconcile contract wording) if actual master Phase35 gate permits. **Second run:** brand-new independent session, read-only, with no prior authoring role. Both must preserve open Phase35 issues and forbid unauthorized Phase37 execution.

### Appendix C.1 — Full ready-to-copy Cursor/Codex implementation prompt

```text
# WAYLOOM DATATHON — PHASE 36 COMPLETE README / DOCUMENTATION IMPLEMENTATION

ROLE: Senior ML documentation engineer, Python project maintainer, competition compliance reviewer and secure-repository auditor. Operate in the USER'S LOCAL WayLoom Datathon repo, not in an imagined repo. Act carefully but autonomously on purely safe documentation tasks.

PRIMARY CONTRACT: `MD Files/PHASE_36_COMPETITION_CONTRACT.md` (provided; inspect current local version). PROJECT: Rootcode Tech Triathlon 2026 Datathon, WayLoom. SCOPE: Phase 36 only — README/project documentation, DT-456–DT-463 inclusive, exactly 8 IDs.

## CRITICAL STATUS: DO NOT SKIP
Phase 34 was reported formally closed, but Phase 35 currently remains OPEN because the AI-use disclosure lacks final human attestation and independent approval. The user is requesting Phase36 PLANNING and expedited README preparation, NOT authorization to bypass a mandatory master-plan phase gate. Inspect actual LOCAL Phase35 and Phase36 master sections before editing. If Phase36 requires Phase35 closure, STOP formal Phase36 implementation; at most create source-grounded preparatory README draft work that is clearly allowed, with all DT completion flags, Phase36 READY and Phase37 NOT STARTED. Never claim Phase35/organizer compliance PASS.

## STEP 0 — MASTER TASK TITLES & SOURCE AUTHORITY (MANDATORY FIRST)
1. Open `AGENTS.md`, `CODEX_HANDOFF_PHASE_11_ONWARDS.md`, official `MD Files/Challenge Booklet.pdf` (focus printed pp.21–25), `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` (Phase35 and Phase36), current Phase36 contract, Phase34 formal closure, Phase35 status/disclosure.
2. Confirm the reconciled verbatim master DT-456, DT-457, DT-458, DT-459, DT-460, DT-461, DT-462, DT-463 task titles, priority, mark, dependency and Phase36 completion gate against the current master. Flag any later drift before implementing.
3. If exact master inventory is inaccessible, differs materially or contradicts official booklet, STOP and report precise evidence needed. Do not make the source claims up.
4. Verify Phase35 prerequisite locally, don't infer formal closure from past chat reports; if Phase35 open and master mandates closure, report blocker and write drafts only if explicitly allowed. No administrative phase status updates now.

## STEP 1 — INITIAL GIT/PRIVACY/HASH SNAPSHOT
Run read-only `git status --short --branch`, `git diff --name-only`, `git diff --cached --name-only`; record all pre-existing edits and don't revert/stage them. Verify `.gitignore` excludes private reports. Verify three official submission CSVs, `models/artifact_registry.json` and the 12 registry-listed models by SHA256+size using HASH-ONLY reads. The prior user-reported baselines are in the Phase36 contract appendix; don't blindly trust them; compare actual local values. Absolutely do NOT open data/raw, data/interim, reports/private, private executed notebooks, private rows, IDs, prediction output, secrets, tokens or organizer correspondence.

## STEP 2 — DOCUMENTATION IMPLEMENTATION (CONDITIONAL ON GATE)
Read actual tracked README and docs first. Create or enhance `README.md` preserving useful correct content, and only necessary supporting docs (`docs/DATATHON_JUDGE_WALKTHROUGH.md`, `docs/PHASE36_DOCUMENTATION_TRACEABILITY.md`) if justified by exact master task titles. Reuse existing architecture diagrams, Phase30 preprocessing, Task2B written policy, saved-model registry and validated tests by relative links. Never invent docs/filenames or print private datasets. Exact master work items:
- DT-456 Write Datathon README.
- DT-457 Explain project objectives.
- DT-458 Explain folder structure.
- DT-459 Explain environment setup.
- DT-460 Explain how to run notebook.
- DT-461 Explain model files.
- DT-462 Explain how outputs are generated.
- DT-463 Document random seed/reproducibility.
The detailed contracts earlier in this file supply the source and safety checks for each exact item. Keep Task2B official checker feasibility separate from optimality.

## OFFICIAL CONTENT GUARANTEES
- READ p22 booklet: final notebook retains labels/preprocessing/training/evaluation and last cell loads Task1+Task2A saved models, prints inputs/predictions. The official booklet requires specific deliverables, **not a README by name** (README is master work).
- Task1 exact `delivery_id,pred_service_min,pred_late_prob`; preserved supplied identifiers and order.
- Task2A exact `row_id,pred_total_volume_m3,pred_chilled_volume_m3`; both demand history sources exactly once, requested-date ISO week, Style/Tech chilled zero, chilled<=total.
- Task2B exact `scenario,order_ref,outlet_id,decision,vehicle_id,trip_id`; whole-order served or deferred, blank vehicle/trip if deferred, at most 2 trips, 270 Fresh / 480 Style+Tech budgets; no depot return in formula; repeat `outlet_id` allowed and `order_ref` unique.
- AI-use disclosure must not falsely say approved or contain private incidents beyond the approved sanitized disclosure. Phase35 currently human-signoff pending and data transmission with ChatGPT/Codex was confirmed; do not conceal or misrepresent it. Do NOT upload data to AI services.
- Performance results, videos, official submission ZIP, hosted UI, cloud deployment, organizer clearance: document ONLY IF actually evidenced; otherwise clearly pending or omit.

## STEP 3 — TEST REAL DOCUMENTATION, NOT JUST HEADINGS
Reuse safe test infrastructure and add `tests/test_phase36_documentation.py` only if necessary; tests must actually validate source-backed references, all official filenames/schema, relative links, CLI entrypoint existence and flags, no private-row leakage, pending status honesty, and exactly eight reconciled task references. Use deterministic synthetic text fixtures, no network, no private file reads, no model deserialization. Include negative test for broken link, wrong schema, fake demo URL, hardcoded user path and wrong master ID. Verify reported testing nodes exist and collect. Run targeted tests, then full safe pytest if gate and non-destructive; pip check; git diff --check. Avoid canonical validators known to overwrite private reports. Report actual pass/skip counts rather than assume historical 858 tests still match.

## STEP 4 — PROTECT FROZEN ARTIFACTS AND SCOPE
Recompute submission CSV hashes, registry hash and 12 artifact hashes/sizes after edits; no protected bytes modified. No edits to src/, scripts/, frozen configs, models/, outputs/, notebook executable content, raw data, private reports, Phase35 closure or Phase37+. Do not stage/commit/push. Do not change master Phase36 task flags during implementation. If any protected hash changed, STOP and report, no silent restoration.

## STEP 5 — COMPLETION AND HANDOFF
Deliver an evidence-backed per-task table DT-456…DT-463 with **EXACT extracted master title**, state `DONE / PREPARATORY_ONLY / BLOCKED / NOT_STARTED`, source evidence and test node(s). Show actual files changed, safe test counts, pre/post hashes, Git/privacy and unresolved Phase35 gate. Independently check booklet deliverable crosswalk. If implementation complete and master gate satisfied, label "READY FOR FRESH PHASE36 INDEPENDENT REVIEW"; not formal closure. Otherwise label "PREPARATORY DRAFT COMPLETE — PHASE35 BLOCKED" honestly.

REQUIRED FINAL SUMMARY:
PHASE36 MASTER INVENTORY: VERIFIED / UNAVAILABLE
DT-456…DT-463: individually state exact master title and result
PHASE35 PREREQUISITE: PASS / BLOCKED / NOT REQUIRED BY MASTER
README: CREATED / UPDATED / DRAFT ONLY / NOT STARTED
BOOKLET CROSSWALK: PASS / FAIL / PENDING
SAFE DOC TESTS: exact counts / NOT RUN
FULL SAFE SUITE: exact counts / NOT RUN
PIP CHECK / GIT DIFF: PASS / FAIL / NOT RUN
OFFICIAL CSV SHA256 + REGISTRY + 12 ARTIFACTS: PASS / FAIL / NOT CHECKED
PRIVATE DATA EXPOSED: NO
STAGED OR COMMITTED: NO
FORMAL PHASE36 CLOSURE: NO
FRESH REVIEW: PENDING
PHASE37 STARTED: NO
BLOCKERS: exact, no invented evidence

Do not begin Phase37, Phase35 closure, final submission upload or ZIP packaging.
```

### Appendix C.2 — Full ready-to-copy independent review prompt

```text
# WAYLOOM DATATHON — PHASE 36 FRESH INDEPENDENT README/DOCS REVIEW

ROLE: Independent senior ML documentation reviewer, source-grounding auditor, competition compliance reviewer and privacy/Git integrity auditor. NEW SESSION, HIGH REASONING, STRICTLY READ-ONLY. You were not the author of the docs. Do not fix/modify/stage/commit any file, run destructive processes, regenerate artifacts, or start Phase37.

OBJECTIVE: Independently decide if the canonical Phase36 master inventory DT-456 through DT-463 (8 tasks) is fully, accurately implemented, source-grounded and authorized for formal closure; or whether only preparatory README work is complete because Phase35 remains open.

1. SOURCE ORDER: official `MD Files/Challenge Booklet.pdf` (Datathon pp21–25), actual `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md`, Phase36 contract, actual Phase35 current status and disclosure, Phase34 closure, prior approved architecture/preprocessing/notebook/model-registry/submission contracts, current tracked README and docs, actual source/test configs, `AGENTS.md`, handoff. Confirm the reconciled exact DT-456...DT-463 text/metadata against the master and flag any drift. Official booklet DOES NOT mandate README by filename; that requirement is master-plan work.
2. PHASE GATE: read current Phase35 master flags and contract. Past user reports say Phase35 is NOT formally closed. If Phase36 master requires Phase35 closure, return formal closure NOT AUTHORIZED even when draft README is good. A safe preparatory README result may be labelled DRAFT/PREPARATION PASS, but not Phase36 overall PASS. Never infer organizer written blanket compliance permission or human sign-off.
3. EIGHT TASKS: for each exact task DT-456 through DT-463, show exact master title; priority/mark/dependency; verdict PASS/FAIL/PREP_ONLY/BLOCKED; README/docs path+heading; source citation; actual tests/evidence and smallest needed fix. Check no master tasks skipped, merged away or silently reinterpreted.
4. BOOKLET CROSSWALK: verify all real deliverable categories: architecture diagrams, preprocessing write-up, model files next to final notebook, notebook retains labels/preprocessing/training/evaluation and last saved-model Task1+2A inference cell printing inputs/predictions, Task2B allocation CSV + written prioritization, Task1/2A CSV filenames/schema, unlisted 3–5m YouTube video (if pending mark), and AI disclosure status. Submission zip is future Phase42 human-controlled. Link only to real docs; do not invent YouTube URL, README official mandate, scores or deployment.
5. THREE TASKS: Task1 strict late/equality, waiting excluded, official order/IDs/3 column schema. Task2A two history sources exactly once, requested-date ISO weeks, forecast 10 weeks, Fresh-only chilled and chilled<=total; fail closed duplicate IDs. Task2B S1, order_ref key, served/deferred, blank deferred fields, max 2 trips, 270/480, no return leg, check_allocation proves feasibility not optimality. Compare actual repo configuration/source and official booklet; NO private rows.
6. SETUP: commands/reference paths and argparse flags must exist, shell correct Windows PowerShell and optional POSIX; dependency manifest correct, no fake containers/GPU/cloud API; Jupyter kernel `.venv` guidance if present; distinguish synthetic safe tests/human-local private validation/Phase39 clean-environment reproduction. Do not execute commands that touch restricted data or overwrite preserved private reports.
7. HONESTY: verify references to existing docs and Phase35 pending factual approval. Distinguish HUMAN_LOCAL_REPORTED vs independently rerun. No false model scores, hidden full simulation, invented performance, complete AI-tool inventory, organizer clearance, privacy compliance or unlisted video.
8. SAFETY: snapshot initial/final git status and protected hashes without reading private datasets: all three official CSVs, registry and 12 artifacts; test read-only document links, no private output or secrets, reports/private ignored, staged files remain none; note pre-existing Git changes. Do not open `data/raw`, `data/interim`, `reports/private`, executed private notebooks, model pickles/joblib or row-level CSVs.
9. RUN NON-DESTRUCTIVE VERIFICATION only: collect/examine doc test nodes, targeted doc tests, safe full suite if permitted, `pip check`, `git diff --check`, link/status checks. Use `.venv` runtime, `-p no:cacheprovider`, temp pytest directories to avoid writing tracked/private evidence. If a command may mutate protected files, SKIP and report why. Ignore no failed tests. Report exact observed pass/skip/warnings, and identify tests that merely check existence rather than substantive assertions.
10. INDEPENDENT REVIEW — **NO EDITS**. Return task table, master title/provenance, official booklet compliance, broken links/commands, security/privacy, hash guards, blockers and minimal fixes. If required Phase35 gate unmet, explicitly deny formal Phase36 closure, even if README quality is high. Do not require fictitious tests or invented evidence.

MANDATORY RESULT TEMPLATE:
PHASE36 FRESH INDEPENDENT REVIEW: PASS / FAIL / PREPARATORY_ONLY
PHASE35 FORMAL GATE: PASS / BLOCKED / NOT_REQUIRED_PER_MASTER
EXACT LOCAL DT-456...DT-463 TITLES: VERIFIED / NOT VERIFIED
DT-456: PASS / FAIL / PREP_ONLY / BLOCKED
DT-457: PASS / FAIL / PREP_ONLY / BLOCKED
DT-458: PASS / FAIL / PREP_ONLY / BLOCKED
DT-459: PASS / FAIL / PREP_ONLY / BLOCKED
DT-460: PASS / FAIL / PREP_ONLY / BLOCKED
DT-461: PASS / FAIL / PREP_ONLY / BLOCKED
DT-462: PASS / FAIL / PREP_ONLY / BLOCKED
DT-463: PASS / FAIL / PREP_ONLY / BLOCKED
BOOKLET CROSSWALK: PASS / FAIL
LINKS & VERIFIED COMMANDS: PASS / FAIL
METHOD/SCHEMA FIDELITY: PASS / FAIL
AI DISCLOSURE STATUS HONESTY: PASS / FAIL
TARGETED DOC TESTS: <exact counts / NOT RUN>
FULL SAFE SUITE: <counts / NOT RUN>
PIP/GIT DIFF: PASS / FAIL / NOT RUN
FROZEN CSV HASHES: PASS / FAIL / NOT CHECKED
REGISTRY AND TWELVE MODEL ARTIFACTS: PASS / FAIL / NOT CHECKED
PRIVACY/GIT STATUS: PASS / FAIL
FORMAL PHASE36 CLOSURE AUTHORIZED: YES / NO
PHASE37 MAY BEGIN AFTER REQUIRED CLOSURE: YES / NO
BLOCKERS: precise list or None
FILES MODIFIED BY REVIEW: NONE
```
