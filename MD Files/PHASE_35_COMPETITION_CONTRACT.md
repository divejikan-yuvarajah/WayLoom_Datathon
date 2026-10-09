# PHASE 35 — AI-Use Disclosure: Competition Implementation Contract

> **Canonical file:** `PHASE_35_COMPETITION_CONTRACT.md` (copy to `MD Files/` according to repository conventions)
> **Project:** WayLoom Datathon — Rootcode Tech-Triathlon 2026
> **Phase theme and confirmed inventory:** **AI-use disclosure**, **DT-451 through DT-455** (five task IDs).
> **Master inventory verification:** The local master plan was inspected during implementation. Section 4 records the verbatim DT-451–DT-455 names, marks, priorities, dependencies, and phase gate.
> **Primary official rule:** Challenge Booklet, printed **page 22**, *Deliverables*: an **AI tool disclosure** explaining **which work was AI-assisted, which was not, and how tools were used**.
> **State of this file:** Planning/implementation instructions only. **DT-451–DT-455 are not yet verified complete**, nor is Phase 35 formally closed.

---

## 1. Purpose, deliverable and strict source hierarchy

Phase 35 creates a **truthful, specific, source-grounded competition AI-use disclosure**, not a public marketing claim and not a replacement for the final notebook, README, model files or submission CSVs. It must show the competition organizers what assistance was used, what was completed without AI assistance, how assistance affected actual work, what humans reviewed and ran, and the meaningful AI/data policy boundaries. It must be clear enough to include in the final `TeamName_Datathon.zip` after later packaging gates.

**Authority, highest first:**

1. Official `Challenge Booklet.pdf`, with organizer-issued clarifications where actually available; use p. 22 for AI/data restrictions and disclosure deliverable.
2. `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` (or its actual local location) for **exact Phase 35 IDs, work item wording, task metadata, completion gate, and dependency**.
3. Signed/approved prior phase contracts and formal closure evidence, notably Phase 34, Phase 33 submission integrity and Phase 32 artifact loading.
4. Actual current repository configuration, implementation, tests, history and safe sanitized results.
5. `AGENTS.md`, `CODEX_HANDOFF_PHASE_11_ONWARDS.md` and this new contract.
6. Engineering proposals labelled as such — never treat them as official rules.

**Evidence caution:** A draft can state that this project has used ChatGPT and Cursor/Codex to assist writing and implementation because the conversation establishes their use, but **specific roles, versions, dates, inputs, model-training decisions, private-data handling and human approval must still be verified from repository or human evidence**. A disclosure must not attribute Designathon-only use (e.g., prototype tools) to Datathon without proof.

## 2. Official Challenge Booklet requirements vs engineering enhancements

### 2.1 Official requirements, with source distinctions

| Official source | Rule or deliverable | Phase 35 consequence |
|---|---|---|
| Challenge Booklet p.22, **Deliverables** | AI tool disclosure: explain work that **was AI-assisted**, work that **was not**, and **how tools were used** | A final concise disclosure must explicitly answer **all three**, with specific tools and tasks. |
| Challenge Booklet p.22, **Rules and Regulations** | Pre-trained models restricted, except the stated synthetic-data-generation or preprocessing exceptions | Accurately describe model origin, training, and any exceptions **only when evidenced**. Do not imply that an LLM writing a document is necessarily a trained prediction model. |
| Challenge Booklet p.22, **Rules and Regulations** | Proprietary API-based modelling/preprocessing prohibited | Identify whether any external API was used to transform/train on competition data; if unclear, stop for human/organizer clarification. |
| Challenge Booklet p.22, **Rules and Regulations** | Low-code/no-code AI tools or fully automated end-to-end modelling tools prohibited | Explain actual workflow; distinguish assistant-generated suggestions/coding support from prohibited automated modelling, based on evidence, not guesses. |
| Challenge Booklet p.22, **Terms and Conditions** | Competition data only for competition; no third-party distribution/transmission; no public derivatives without organizer authorization; maintain confidentiality | Final disclosure/logs must not contain restricted rows, IDs, private prediction samples, attached private files, secrets, or unapproved datasets/derivatives. Ask humans to attest to actual handling; Git ignore alone is not proof of no transmission. |
| Challenge Booklet p.22, **Submission** | AI disclosure included among Datathon deliverables in one compressed submission folder | Provide a clear documentation artifact for later Phase 40/42 packaging; this phase **does not** build/submit ZIP. |

**Booklet limits:** It **does not specify** a name like `AI_USE_DISCLOSURE.md`, a numbered five-step workflow, Python lint schema, consent checkbox or a particular AI assistant. Those are WayLoom **engineering implementation choices**, subject to the finalized master plan.

### 2.2 Engineering objectives (not organizer-mandated wording)

- Five-ID proof matrix; evidence-quality tags; human sign-off; contradiction review; confidentiality-safe internal ledger; optional deterministic documentation tests; integrity/hashing gate; fresh independent review before formal closure.
- Disclosure should be short enough to read without repository access (approximately 1–2 pages of substantive prose is a **recommended editorial target**, not an official limit).
- Do not over-claim approval, ethics certification, algorithmic optimality, independent reproductions, or that humans manually authored code actually generated/edited through an agent.

## 3. Preconditions and freeze rules

### 3.1 Phase 34 formal gate

The prior conversation includes an explicit Phase 34 formal closure report: DT-438–DT-450 13/13 PASS, Phase complete `[x]`, readiness YES, review PASS, protected hashes unchanged. **Codex must verify those facts in the current local master plan and Phase 34 completion record before editing Phase 35.** If the repository does not reflect closure, STOP; reports from chat are not substitutes for the current files.

Also verify that the official booklet is available locally; the existing notebook/models/output baseline is frozen; project instructions (`AGENTS.md`, handoff) are read; the working tree's preexisting state is recorded and respected.

### 3.2 Immutable and restricted areas

**Do not modify** during this phase:

- `outputs/submission_task1.csv`, `outputs/submission_task2a.csv`, `outputs/submission_task2b.csv` and any official template originals.
- `models/**`, including `models/artifact_registry.json`, 12 registered trained-model/processing artifacts and frozen feature schema references.
- `TeamName_FinalNotebook.ipynb` or any executable Phase 31 notebook/Phase 32 secure bridge.
- Task 1 / Task 2A training, evaluation and inference code; Task 2B optimizer, checker, validator and final allocations.
- `data/raw/**`, `data/interim/**`, `reports/private/**`; no private executed notebook inspection.
- Phase 32 inconsistent master-plan administrative flags, earlier phase statuses or Phase 36+ tasks: report status inconsistencies separately; do not silently fix them under a Phase 35 documentation change.

**Hash-only read** of protected files and registry metadata is allowed when performed safely; no private row inspection, sample printing, serializing or external transmission. Model checksum and byte-size checks do not require unpickling.

### 3.3 Git baseline and strict scope

Record `git status --short --branch`, `git diff --name-only`, staged status, and SHA256 of frozen CSVs, registry and all registry-listed files before changes. Confirm private directory ignore rules. Distinguish pre-existing changes from current edits; never silently reset or overwrite them. No stage/commit/push unless user explicitly authorizes it.

## 4. Exact-count Phase 35 inventory and metadata-verification gate

The local source-of-truth inventory is:

| Master task ID | Exact master-plan work item | Mark | Priority | Dependency |
|---|---|---:|---:|---|
| **DT-451** | Record all AI-assisted activities | [O] | P0 | Maintain throughout project |
| **DT-452** | Record human-controlled modelling work | [O] | P0 | Ongoing log from project start; finalize after core work |
| **DT-453** | Record where AI was not used | [O] | P0 | Ongoing log from project start; finalize after core work |
| **DT-454** | Confirm compliance with competition restrictions | [O] | P0 | Ongoing log from project start; finalize after core work |
| **DT-455** | Write final AI-tool disclosure | [O] | P0 | Ongoing log from project start; finalize after core work |

**Phase dependency:** Ongoing log from project start; finalize after core work.
**Phase gate:** AI-use disclosure is complete, accurate and consistent with competition restrictions.
**Count check:** 451, 452, 453, 454, 455 — exactly **5/5 IDs**, no omissions or invented DT-456. The provisional workstream descriptions were reconciled to these exact master titles without changing master-plan status.

Recommended first evidence note (private only if needed):

```text
PHASE35 MASTER INVENTORY EXTRACTED LOCALLY
DT-451 — <copy exact master work item>
DT-452 — <copy exact master work item>
DT-453 — <copy exact master work item>
DT-454 — <copy exact master work item>
DT-455 — <copy exact master work item>
MARK / PRIORITY / DEPENDENCY — <copy each exactly>
MASTER COMPLETION GATE — <copy exact text>
CONTRACT MISMATCHES — NONE / <document exact differences>
```

## 5. Inputs, outputs, owners and file discovery

| Category | Input or artifact | Handling |
|---|---|---|
| Official | Challenge Booklet p.22; any actual organizer clarification | Read-only requirements. |
| Master | Finalized `WAYLOOM_DATATHON_MASTER_PLAN.md` Phase 35 entries | Read-only except later authorized **separate formal closure**. |
| Existing phase proof | Phase 31 notebook closure, Phase 32 registry evidence, Phase 33 CSV validation, Phase 34 test suite and review | Sanitized summaries only; label past human-local evidence. |
| Existing repo | `AGENTS.md`, handoff, Phase 29 architecture / Phase 30 preprocessing, README if any, known PR/commits/tool use | Read narrowly; verify facts; never inspect private datasets. |
| Human declaration | Tool-use inventory, who did what, verification steps, possible external uploads, ambiguity to organizer | Must be consciously confirmed by an authorized team member. |
| Proposed disclosure | `docs/AI_USE_DISCLOSURE.md` or `MD Files/AI_USE_DISCLOSURE.md` | **Engineering suggestion; not booklet-prescribed filename.** Choose existing repo convention. |
| Proposed traceability | `docs/ai_use_evidence_matrix.md`, or sanitized table within disclosure; optional | Prefer no second artifact if one is enough; no transcript dumping. |
| Optional tests | `tests/test_ai_use_disclosure.py` or existing docs validator | Synthetic/markdown-lint only, conditional on actual need. |
| Private verification | Local-only confirmation checklist or safe summary in ignored reports | Do not leak private IDs/rows/prompts/paths. |
| Final proof | Human-readable implementation report and review-ready checklist | No falsely completed checklist/status before review. |

**Actual path discovery:** `rg --files | rg '(^|/)(AI|ai).*disclos|README|phase35|phase_35|docs/'`, `git status --short`, `rg -n 'AI|Codex|Cursor|ChatGPT'` restricted to public repository docs and sanitized configs. Never search `data/raw`, `data/interim` or `reports/private` recursively for tool-use clues. If prompts or chat logs contain private data, **do not open/export them**.

## 6. Documentation/evidence design and truthfulness policy

### 6.1 Claim-evidence levels

| Status | Means | Acceptable language |
|---|---|---|
| `REPOSITORY_VERIFIED` | Specific safe source shows behavior or created artifact | "The implementation contains ...", with source/path. |
| `HUMAN_CONFIRMED` | Authorized team member personally confirms activity beyond safe repository introspection | "A team member confirms ...", noting human confirmation. |
| `SUPPORTED_BY_BOTH` | Safe repo evidence and authorized human account agree | Firm statements within verified scope. |
| `NOT_YET_CONFIRMED` | No safe adequate source or human answer | Placeholder/question; **not submission-ready** if material. |
| `CONFLICT_OR_POSSIBLE_POLICY_ISSUE` | Accounts/evidence differ or prohibited activity suspected | STOP, investigate, potentially seek organizer clarification. |

Do **not** equate a passed unit test with a proven human decision. Do **not** equate `.gitignore` with proof that no data ever left the machine. Do **not** attribute all work to a human simply because the human approved a Codex-generated patch.

### 6.2 Minimum disclosure table fields

`Tool or platform | Confirmed purpose | Competition stage/artifacts | Assistance method (what/how) | Inputs at safe category level | Output at safe category level | Human validation/decisions | Evidence grade | Known limits / uncertainty`.

An internal table may additionally include `evidence reference` and `confirmed by` (role, not personal data). Omit exact dates/versions if unknown. If tools were not used for modeling, describe that limitation accurately but do not assert you proved zero external calls from static source alone.

### 6.3 Safe tool taxonomy

Distinguish these categories when applicable to **Datathon specifically**:

1. **Generative assistant for writing/analysis:** e.g. ChatGPT helps brainstorm architecture, explain constraints, draft text or review results; not a model to produce official numeric submissions by API.
2. **Coding assistant/agent:** e.g. Cursor / Codex suggests/edits Python/test/documentation, under human-run/review and version control; identify true autonomy/scope honestly.
3. **Local computational tools:** e.g. Jupyter/Python/sklearn/CatBoost/LightGBM/OR-Tools if verified. These are not automatically 'AI assistants' in disclosure wording, but may be mentioned for context of locally trained models or solver computation.
4. **Other AI tools:** list only if actual Datathon use is confirmed. Avoid importing Designathon/Hackathon tool lists into Datathon.
5. **No-assistance activities:** personally confirmed real-world/team choices, data access, human-local notebook runs, organizer validation, final upload, etc., if true.

**Illustrative only, not a claim of completed work:** "A coding assistant suggested a test; team members reviewed and executed it against synthetic fixtures using the local Python environment." Human must confirm that this matches reality.

## 7. Requirements-to-evidence and privacy traceability

Every material sentence in the final disclosure should map to at least one source or signed human verification. **Do not include confidential raw evidence in final deliverable**. Suggested internal evidence register:

```text
claim_id | dt_id | work_area | claim_text_safe | evidence_grade |
repo_reference_or_human_attestation | evidence_scope | discrepancy | reviewer | disposition
```

Use `claim_id` like `AI-001`, never a private `delivery_id`, `order_ref`, actual outlet identifier or prompt containing data. Human attestation can be confirmed via a checklist without collecting names or secret account information. Do not use screenshots of connected systems or chat logs unnecessarily.

**Negative assertion warning:** 'No private data was transmitted externally' requires a human process confirmation and applicable evidence; an audit of Git tracking cannot prove it by itself. Where a concern or unknown remains, disclose the limitation and escalate; do not fabricate a clean bill of health.

## 8. Human confirmation gate (mandatory factual validation)

Before declaring the disclosure final, ask the user/team a compact set of concrete questions (can be grouped in one message; no intrusive form required):

1. **Tools:** Which AI tools were actually used for the Datathon (names, optional versions) and for which tasks? Distinguish ChatGPT, Cursor, Codex and any others; separate Designathon/Hackathon.
2. **Inputs/exposure:** Were private competition datasets, samples, outputs, IDs, private notebooks or secrets ever pasted/uploaded/shared with any external AI tool or third-party service? If yes or uncertain, don't suppress: determine exact facts and organizer implications; do not paste those private details into this chat.
3. **Model work:** Did any pre-trained predictive model, proprietary remote API for modelling/preprocessing, or low/no-code auto-modelling platform touch Task 1/2A model training, features or predictions? Distinguish AI for documentation/coding from model computation.
4. **Human participation:** Who, in role terms, selected final models, approved business constraints, executed training/evaluation, ran Jupyter local checks and official checker, and made the final submission decisions? Confirm what AI did independently.
5. **Review:** Has an authorized team member actually read the final disclosure and approved its factual accuracy? Record YES/NO with safe evidence, not a forged signature.

If any answer is unavailable, label `NOT_YET_CONFIRMED` and **keep affected task PENDING**. Ask organizer clarification for credible policy ambiguity before submission.

---

## 9. DT-451 — Record all AI-assisted activities

**Authority note:** Exact local master-plan title and metadata verified; the detailed inventory/evidence steps below are Phase 35 engineering acceptance criteria.

**Objective.** Record all evidenced AI-assisted Datathon activities and identify any material inventory gaps that require team confirmation.

**Candidate file ownership.** Main disclosure in verified docs path, with optional sanitized internal evidence matrix and a narrow `tests/test_ai_use_disclosure.py` when justified. Do not assume those candidates already exist; discover actual paths. No production source edits.

**Inputs.** local master inventory; sanitized project/public docs; safe git history/commit messages where permitted; team confirmation of actual tools. Never open private datasets or raw AI chat transcripts.

**Outputs.** a verified tool register with actual name/provider only when proven; tool category; stage; purpose; whether it is an AI assistant or local ML library; evidence grade; explicit list of still-unknown tools/use.

**Step-by-step implementation.** 1. Copy exact DT-451 title and metadata from master into evidence matrix. 2. Build candidate tool list from public docs/known chats; mark each as provisional. 3. Confirm with human which tools actually operated in Datathon and whether the AI role was drafting, reviewing, coding, testing or executing. 4. Separate AI tools from locally trained ML frameworks/solver libraries. 5. Remove duplicate marketing synonyms; do not mislabel Designathon's Google Stitch as Datathon without confirmation. 6. Resolve scope/time/version ambiguities honestly: omit unknown version numbers rather than fabricate them. 7. Link each confirmed tool to a safe evidence ID or human attestation.

**Required tests and proof.** all asserted tool names supported by evidence; every listed platform has at least one actual purpose; no duplicated aliases; no invented vendor/version; human-verification unknowns block final sign-off; no tool-list claims sourced only to prior draft prose.

**Edge cases.** alias 'Cursor' vs 'Codex in Cursor'; multiple models over time; AI suggestions rejected; tool investigated but not actually used; a tool used in Designathon only; a local Python package incorrectly treated as a generative assistant.

**Task stop conditions.** unverifiable tool use, suspected private prompts in evidence, or contradictory human recollection of tool category.

**Definition of task completion:** exact local master scope verified; content built and reviewed using authentic evidence; all tests/safety gates for this task passed; unresolved material unknowns absent; source/line or human confirmation recorded; no prohibited changes. Mark task "IMPLEMENTED / READY FOR REVIEW" only until fresh independent review passes.


## 10. DT-452 — Record human-controlled modelling work

**Authority note:** Exact local master-plan title and metadata verified; the detailed activity/role mapping below is a Phase 35 engineering acceptance criterion.

**Objective.** Record the human-controlled modelling work precisely, distinguishing human decisions and local execution from AI-assisted code, documentation, and review.

**Candidate file ownership.** Main disclosure in verified docs path, with optional sanitized internal evidence matrix and a narrow `tests/test_ai_use_disclosure.py` when justified. Do not assume those candidates already exist; discover actual paths. No production source edits.

**Inputs.** approved inventory; safe code/docs history; project phase artefacts and reviewed implementation reports; human confirmations.

**Outputs.** an evidence-backed account of who selected final models, approved modelling/constraint decisions, executed training/evaluation and private validation, and made final submission decisions; unknown role claims remain explicit and block task completion.

**Step-by-step implementation.** 1. Capture exact master title. 2. Map safe registry and phase-closure evidence to modelling stages without inferring human ownership from files alone. 3. Ask the human, in role terms, who selected final models, approved constraints, executed training/evaluation and private checks, and made final decisions. 4. Distinguish 'suggested model design' from 'selected model', 'code generated' from 'code executed locally', and solver computation from human approval. 5. Label mixed or unknown authorship accurately. 6. Reconcile statements to Phase 31/32/33 evidence and repository history. 7. Draft concise competition-facing prose without raw private excerpts.

**Required tests and proof.** every human-control assertion has safe evidence or human attestation; human-local execution is not inflated into sole authorship; no claim that a hosted assistant trained or generated official predictions unless proven; reviewed evidence excludes actual private IDs/records.

**Edge cases.** AI suggested a failed approach; mixed human/AI writing; code review done by another AI session; synthetic-only example vs private data; automatic code edits without human line-by-line approval; user executed Jupyter after assistant drafted tests.

**Task stop conditions.** actual assistance used for competition-prohibited proprietary API modelling or a material unverified claim about what the agent executed.

**Definition of task completion:** exact local master scope verified; content built and reviewed using authentic evidence; all tests/safety gates for this task passed; unresolved material unknowns absent; source/line or human confirmation recorded; no prohibited changes. Mark task "IMPLEMENTED / READY FOR REVIEW" only until fresh independent review passes.


## 11. DT-453 — Record where AI was not used

**Authority note:** Exact local master-plan title and metadata verified; the detailed human/non-AI boundary below is a Phase 35 engineering acceptance criterion.

**Objective.** Record specifically what was not AI-assisted, without converting human-local execution into an unsupported claim of wholly human authorship.

**Candidate file ownership.** Main disclosure in verified docs path, with optional sanitized internal evidence matrix and a narrow `tests/test_ai_use_disclosure.py` when justified. Do not assume those candidates already exist; discover actual paths. No production source edits.

**Inputs.** confirmed division of work, local-execution attestation, approved final model/validation/solver results, sanitized recorded evidence.

**Outputs.** explicitly non-AI-assisted activities and scope; human decisions; distinction between human-local execution and writing assistance; factual review sign-off status.

**Step-by-step implementation.** 1. Copy exact master title. 2. Identify truthful examples of tasks completed without generative assistance; do not assume full human ownership of every experiment. 3. Cross-check human-local evidence such as Jupyter Run All (Phase 31), final-cell-only, relevant private checker when confirmed, and official upload (if already completed); don't claim independent Codex execution of those. 4. Separate HUMAN-EXECUTED / AI-DRAFTED / HUMAN-REVIEWED / CODE-GENERATED/EXECUTED-BY-AGENT / UNKNOWN as needed. 5. Capture human attestation for each material negative claim. 6. Summarize human accountability for choice, verification and submission without generic 'humans did everything' language. 7. Do not invent participant identity, dates or approvals.

**Required tests and proof.** distinct 'not AI-assisted' section exists; every 'human-only' assertion has human confirmation or safe evidence; human-local runs are not mislabeled independent fresh-review reruns; ambiguous mixed-authorship activities are described as mixed rather than falsely exclusive.

**Edge cases.** generative AI drafted human-revised content; code executed by person but authored by assistant; solver optimized decision automatically; a test-run report generated by an agent; human finalized a model based partly on AI advice.

**Task stop conditions.** human participation cannot be confirmed for a declared human-only assertion, or apparent contradiction with repo automation.

**Definition of task completion:** exact local master scope verified; content built and reviewed using authentic evidence; all tests/safety gates for this task passed; unresolved material unknowns absent; source/line or human confirmation recorded; no prohibited changes. Mark task "IMPLEMENTED / READY FOR REVIEW" only until fresh independent review passes.


## 12. DT-454 — Confirm compliance with competition restrictions

**Authority note:** Exact local master-plan title and metadata verified; the detailed rule/evidence cross-check below is a Phase 35 engineering acceptance criterion.

**Objective.** Confirm competition-restriction compliance only to the extent supported by official rules, safe repository evidence, and required human attestations.

**Candidate file ownership.** Main disclosure in verified docs path, with optional sanitized internal evidence matrix and a narrow `tests/test_ai_use_disclosure.py` when justified. Do not assume those candidates already exist; discover actual paths. No production source edits.

**Inputs.** official booklet p22; source/registry metadata; safe confirmed tool ledger; human account of any data transfers; project compliance notes.

**Outputs.** clearly sourced policy matrix; concise justified disclosure statements; list of ambiguous/incident concerns and resolution status; confidentiality-safe evidence note.

**Step-by-step implementation.** 1. Copy exact master title. 2. Enumerate distinct p22 rules exactly without strengthening/weaken them. 3. Verify trained prediction models in Phase 31/32 against safe registry metadata; do not load model bytes or private data merely to draft this disclosure. 4. Ask human whether any pretrained model, proprietary remote preprocessing/modelling API, no-code AutoML or fully automated model platform was used for competition computation. 5. Evaluate whether coding/document AI use is different from prohibited predictive modelling and describe actual behavior without claiming blanket permission. 6. Check third-party transmission risk; don't infer lack of transmission from Git history alone. 7. If actual prohibited tool/data transfer is plausible, hold approval and advise organizer clarification before further sharing. 8. No made-up permissions or claims the organizer reviewed/approved this workflow.

**Required tests and proof.** complete rule matrix p22; every 'compliant' claim annotated with underlying evidence or human attestation; no unverified categorical absolutes; no private records/prompts in deliverable; protected registry/models untouched; risk/unknown states have fail-closed disposition.

**Edge cases.** API only for general text rewriting vs API for feature transformation; foundation model drafting code vs pretrained predictor as actual competition model; synthetic data allowed exception misrepresented as general pretrained-model permission; private aggregate report considered dataset derivative; any previously shared real example or record requires factual human assessment; do not reproduce it or assume transmission compliance.

**Task stop conditions.** suspected breach, unknown transmission, unsanctioned use, or any protected model/CSV mutation; escalate to human/organizer, never conceal.

**Definition of task completion:** exact local master scope verified; content built and reviewed using authentic evidence; all tests/safety gates for this task passed; unresolved material unknowns absent; source/line or human confirmation recorded; no prohibited changes. Mark task "IMPLEMENTED / READY FOR REVIEW" only until fresh independent review passes.


## 13. DT-455 — Write final AI-tool disclosure

**Authority note:** Exact local master-plan title and metadata verified; the detailed consistency/privacy/sign-off checks below are Phase 35 engineering acceptance criteria.

**Objective.** Produce the final readable AI-tool disclosure once the human factual gate is satisfied, without pretending Phase 35 is formally closed before independent review.

**Candidate file ownership.** Main disclosure in verified docs path, with optional sanitized internal evidence matrix and a narrow `tests/test_ai_use_disclosure.py` when justified. Do not assume those candidates already exist; discover actual paths. No production source edits.

**Inputs.** all prior task outputs; final repo structure; official Deliverables p22; human factual review/attestation; sanitized automated checks.

**Outputs.** one clear AI disclosure file, optionally safe appendix/evidence matrix; tests for content/consistency if warranted; unambiguous implementation report; independent-review-ready checklist.

**Step-by-step implementation.** 1. Copy exact master title. 2. Assemble overview, tool/use table, how assistance affected specific Datathon areas, NOT AI-assisted human work, compliance boundary, human validation, limitations, factual sign-off. 3. Ensure not to confuse WayLoom's AI prediction/optimization product features with the team using generative assistants. 4. Check consistency with Phase 29 architecture, Phase 30 preprocessing, final notebook, model registry, README if present; be precise about Task 2B optimizer vs ML model. 5. Run documentation checks (manual and optional synthetic lint) verifying all three official questions, five task IDs, contradictions, no placeholders, private IDs/secrets, no confidential inputs. 6. Capture before/after frozen file hashes. 7. Ask human to approve exact final text; do not simulate sign-off. 8. Prepare fresh-review evidence and stop before status flipping, commit, package or Phase36.

**Required tests and proof.** final headings/three core questions present, specific how descriptions, at least one explicit not-AI-assisted statement supported, policy caveats, no TODO/unanswered material facts, no private data, no false organizer endorsement, no unapproved model/regenerated outputs, git diff clean and artifact hashes unchanged.

**Edge cases.** markdown path/links broken; disclosure saved only in ignored folder; final package path different; omitted AI tool category; outdated phase status; broad 'no API used' contradicted by code; empty non-AI section; incorrect role of human vs automation; human sign-off pending.

**Task stop conditions.** unresolved factual/official ambiguity, required human confirmation absent, private data leak in document, unreviewed disclosure, changed protected hash or master-plan mismatch.

**Definition of task completion:** exact local master scope verified; content built and reviewed using authentic evidence; all tests/safety gates for this task passed; unresolved material unknowns absent; source/line or human confirmation recorded; no prohibited changes. Mark task "IMPLEMENTED / READY FOR REVIEW" only until fresh independent review passes.


---

## 14. Disclosure output specification and ready-to-use skeleton

This is a **template**, not a factual statement about what the team did. Replace `[CONFIRM]` items from an authorized human and safe repository evidence. Do not submit with unanswered material placeholders.

```markdown
# WayLoom Datathon — AI Tool Use Disclosure

## Scope
This disclosure describes generative AI assistance used during the **Datathon** submission. It does not attribute tools used only in other competition phases to the Datathon.

## Work that was AI-assisted
| Tool | What it assisted | How it was used | What the team reviewed/verified |
|---|---|---|---|
| [CONFIRM ACTUAL TOOL] | [SPECIFIC WORK/ARTIFACT] | [CONCRETE DESCRIPTION] | [CONFIRMED HUMAN/LOCAL VALIDATION] |

## Work that was not AI-assisted
[CONFIRM SPECIFIC HUMAN-ONLY ACTIONS. Distinguish local training execution from AI-assisted code drafting.]

## Model, automated-tool, API and data handling boundaries
[State only verified facts about actual trained models, prohibited tool categories, any external transmission, and confidentiality, with human attestation and unresolved issues explicitly resolved.]

## Human oversight and independent checks
[Evidence-backed checks; distinguish agent tests from human-local private-data runs; do not falsely claim organizer endorsement.]

## Limitations and final factual review
[Qualify unknowns, record team confirmation in a privacy-safe manner.]
```

**Submission editing principle:** the final disclosure can be short, but cannot be empty or generic. Avoid copying the internal compliance audit verbatim into the competition-facing file; summarize honestly and comprehensibly. The user/team—not the assistant—must confirm what they really did.

## 15. Validation/test matrix, threat model and expected results

| Test ID | Covers | Positive case | Negative / edge case | Allowed test inputs |
|---|---|---|---|---|
| AI35-T01 | Phase34 gate | All 13 checked, closure/review/readiness recorded | Any closure flag NO: stop | Master/contract metadata |
| AI35-T02 | 5-ID inventory | Exact 451–455 extracted, scope reconciled | Missing/mismatched title/extra ID: stop | Master plan text |
| AI35-T03 | Official 3-question rule | AI-assisted, not assisted, how answered specifically | Generic 'AI used' only: fail | Public disclosure Markdown |
| AI35-T04 | Tool truthfulness | Tool appears in evidence/human attestation | Unconfirmed tool/version: fail | Sanitized tool ledger |
| AI35-T05 | Datathon track | Tools belong to correct track | Designathon-only Stitch falsely claimed: fail | Source/human categorization |
| AI35-T06 | Human-vs-agent roles | Mixed authorship/execution clear | 'Entirely human' contradicted by Codex history: fail | Safe repository history |
| AI35-T07 | Human-only work | Specific verifiable human activities | Blanket unevidenced human claim: fail | Human attestation |
| AI35-T08 | No pretrained/proprietary modelling | Accurate evidence-aware explanation | Blanket innocence based only on docs: fail | Rules + safe model registry |
| AI35-T09 | API vs assistant distinction | Remote modelling/preprocessing distinguished from drafting code | Confusion or suspect unverified API use: stop | Safe confirmed tool scopes |
| AI35-T10 | Automation tool restriction | No unsupported claims of fully automated modelling | Potential AutoML use unresolved: stop | Human verification |
| AI35-T11 | Confidentiality | No private data in docs/logs and handling attested | Private IDs, secret, upload risk: stop | Publication artifacts only |
| AI35-T12 | Evidence quality | Every significant claim grounded | AI-generated narrative cited as its own evidence: fail | Public source references |
| AI35-T13 | Consistency | Docs match local model/artifact stages | Task2B optimizer called 'trained LLM': fail | Public docs and safe configs |
| AI35-T14 | Fresh-review gate | Human approved final text, report ready | Missing human approval: pending | Human confirmation summary |
| AI35-T15 | Immutable assets | Pre/post hashes identical for 3 CSV + registry + 12 artifacts | Any hash deviation: stop | Hash/size metadata |
| AI35-T16 | Git & privacy | Only authorized docs/tests changed; ignored private files | Staged private files or new output modifications: fail | Git metadata |

**Suggested minimal docs-check test cases (only if useful):** use synthetic Markdown strings to assert that sections and claim statuses are present and that TODO placeholders are absent in the final export; test that the final linked file exists and is trackable; reject suspicious private-path content or row-level identifiers using cautious patterns with review of false positives. Do not implement a scanner that opens restricted private directories. Do not assert 'policy compliance' solely because Markdown headings are present. Manual human attestation and independent evidence are indispensable.

**Nonblocking nuances:** A previously reviewed Windows symlink test skip in Phase 34 is not evidence of AI compliance. Phase 32 administratively unchecked master-plan flags are a separate issue to report, not silently edit during Phase 35. The **final submission deadline** in the official booklet is **9 October 2026 at 11:59 PM Sri Lanka time**: prioritize completing human review and submission handoff promptly; this contract does not upload the ZIP or promise an on-time upload.

## 16. Failure taxonomy and stop/rollback rules

| Code | Symptom | Immediate response | Who resolves |
|---|---|---|---|
| `P35-GATE` | Phase34 closure missing/contradictory | Stop before changes; report exact docs | Phase34 owner / human |
| `P35-INVENTORY` | One or more five master titles/scope unavailable or conflict | Stop work on affected tasks; reconcile contract to master first | Human/plan maintainer |
| `P35-EVIDENCE` | Tool or role claims cannot be verified | Mark unknown; ask team; never invent | Human owner |
| `P35-PRIVACY` | Data transmission/exposure suspected or private text found | Stop, do not copy/share; assess appropriately | Human/organizer as needed |
| `P35-MODEL-RULE` | Pretrained/proprietary API/AutoML usage ambiguous or apparently prohibited | Stop and seek actual facts/organizer interpretation | Human/organizer |
| `P35-CONTRADICTION` | Documents conflict with model registry, notebook, version control or team account | Identify exact conflict; do not paper over it | Repo owner + reviewer |
| `P35-HASH` | Any protected artifact checksum changed | Stop, preserve diagnostics; no automatic repair/revert | Human owner |
| `P35-SIGNOFF` | Human has not read/confirmed disclosure | Keep review status PENDING | Human signer |
| `P35-REVIEW` | Independent read-only review FAIL or not run | No formal phase closure/readiness YES | Independent reviewer |

Never 'fix' a suspected policy issue by rewriting history, deleting logs, modifying a model, altering an official CSV or inventing a clearance. A serious policy ambiguity should be escalated, not disguised as a finished checklist.

## 17. Definition of Done (implementation versus formal phase closure)

### 17.1 Implementation-ready checklist

- [x] The current master plan Phase 35 lists exactly DT-451, DT-452, DT-453, DT-454, DT-455, and the **verbatim names/marks/priorities/dependencies** have been extracted and reconciled.
- [x] Phase 34 is formally closed in the current repo and its independent PASS is recorded.
- [x] All five exact task scopes are implemented and mapped to evidence; no tasks skipped.
- [x] Final disclosure unambiguously answers official AI-assisted / not-AI-assisted / how-used questions.
- [x] Each tool-use claim is specific, true, grounded and appropriately human-confirmed.
- [x] AI assistance in coding/documentation is not misrepresented as algorithmic model inference or proprietary API-based preprocessing.
- [x] Human-only actions, mixed authorship, agent-run tests and private human-local validation are described accurately.
- [x] No unresolved pre-trained/API/fully-automated-modelling/personal-data confidentiality ambiguity remains.
- [x] No fabricated tool names, versions, team identities, dates or claims of organizer approval.
- [x] Human reviewed/approved factual disclosure; evidence is safe to present externally.
- [x] Private datasets, derived rows, private notebook output, secrets and raw prompts are absent from the public-facing file and any tracked test fixtures.
- [x] Verified structure/consistency tests pass; test counts and skips are reported honestly (or test not run with reason).
- [x] SHA256 for all three official submission CSVs, registry and all 12 registered model artifacts is unchanged.
- [x] `git diff --check` passes and Git/private ignore safety is proven with metadata only.
- [x] No unauthorized model, source, notebook, previous phase or downstream phase changes; no staging/commit.
- [x] An independent reviewer can use repo-safe evidence to verify the disclosure without inspecting private rows.

### 17.2 Formal closure gate (separate and later)

- [x] Fresh independent Phase 35 READ-ONLY review issues overall PASS, 5/5 exact-master tasks PASS and authorizes closure.
- [x] Phase 35 completion report is filled, including fact-check provenance and prior failures if any.
- [x] Master plan DT-451–455 statuses updated only after review authority.
- [x] `Phase complete: [x]` and `READY FOR NEXT PHASE: YES` set only through a separate authorized administrative closure action.
- [x] Review/closure update does not alter frozen official CSV/model/registry hashes or private Git safety.

**Implementation session end state:** `READY FOR FRESH INDEPENDENT PHASE35 REVIEW: YES/NO`; `PHASE35 FORMALLY CLOSED: NO`; `PHASE36 STARTED: NO`. **Formal status only after independent review + final closure sync.**

## 18. Git workflow and non-destructive verification

### Before work (PowerShell from repository root)

```powershell
$python = '.\.venv\Scripts\python.exe'
git status --short --branch
git diff --name-only
git diff --cached --name-only
# Discover actual locations; do not guess if a path differs:
rg --files | rg 'Challenge Booklet|WAYLOOM_DATATHON_MASTER_PLAN|PHASE_34|AGENTS|CODEX_HANDOFF'
```

A safe local artifact-hash procedure must discover the **actual official output paths** and registry-listed artifact paths, record baseline hashes to an **ignored local evidence path if needed**, compare again afterward, and print only counts/PASS or changed filenames — no confidential content. Do not unpickle or load models merely to hash them. Do not run a validator if it overwrites preserved private evidence.

### During implementation

Work on the current authorized Phase 35 branch. Preserve pre-existing modified/untracked Phase33/34 files; do not reset them. Prefer a minimum diff to the disclosure document, an optional sanitized internal register, and narrow documentation checks. Avoid touching Phase 35 completion/master plan status until the independent review. Never stage automatically.

### After work

```powershell
$python = '.\.venv\Scripts\python.exe'
# Run only tests that are actually implemented; report exact counts.
& $python -m pytest -q -p no:cacheprovider tests/test_ai_use_disclosure.py
# Optional full suite, ONLY if non-destructive and safe for the current repo:
& $python -m pytest -q -p no:cacheprovider
& $python -m pip check
git diff --check
git status --short
git diff --cached --name-only
# Human and local reviewer: independently recompare protected SHA256 baselines.
```

**Execution caution:** `tests/test_ai_use_disclosure.py` is an example path, not guaranteed to exist; inspect first. If no automated docs test is justified, report manual + file/consistency checks and `NOT RUN — no relevant test file`, rather than fabricating PASS. Default pytest may create `.pytest_cache`; use `-p no:cacheprovider`, and an OS temporary `--basetemp` where safe. Avoid running scripts that mutate outputs or private reports. Only run full safe suite when its behavior is understood.

**Git staging/commit only when separately authorized:** verify doc files do not contain row-level private data; `git add -- <explicit approved paths>` only if user requests. Never use `git add .` or `git add -A` when private content may exist. Use no commit/push during implementation by default. Human upload is later Phase42, not a Codex automation.

## 19. Required implementation evidence report template

```text
PHASE 35 SOURCE/PRECONDITION: PASS / FAIL
EXACT MASTER INVENTORY DT-451–DT-455: VERIFIED / NOT VERIFIED
MASTER WORK-ITEM TITLES: [paste exact five labels]
DT-451: PASS / FAIL / PENDING — evidence
DT-452: PASS / FAIL / PENDING — evidence
DT-453: PASS / FAIL / PENDING — evidence
DT-454: PASS / FAIL / PENDING — evidence
DT-455: PASS / FAIL / PENDING — evidence
DISCLOSURE FILE: exact path or BLOCKED
OFFICIAL AI-ASSISTED / NOT-ASSISTED / HOW: PASS / FAIL
HUMAN FACTUAL ATTESTATION: RECEIVED / PENDING
PROHIBITED-MODELLING/DATA-RULE CHECK: PASS / FAIL / NEEDS CLARIFICATION
DOC TESTS: exact result or NOT RUN (why)
FULL SAFE SUITE: exact result or NOT RUN (why)
PIP CHECK: PASS / FAIL / NOT RUN
GIT DIFF CHECK: PASS / FAIL
FROZEN CSV SHA256: UNCHANGED / CHANGED / NOT CHECKED
REGISTRY+12 MODELS: PASS / FAIL / NOT CHECKED
PRIVATE DATA / GIT: PASS / FAIL
FILES CHANGED: exact paths
BLOCKERS: None / list
READY FOR FRESH INDEPENDENT PHASE35 REVIEW: YES / NO
PHASE35 FORMALLY CLOSED: NO
PHASE36 STARTED: NO
```

### 19.1 Implementation evidence — human attestation received; fresh review pending

- **Precondition:** PASS. The local master records DT-438–DT-450 checked, Phase 34 complete, readiness YES, and a fresh independent PASS authorizing closure.
- **Exact inventory:** VERIFIED. Section 4 now reproduces all five local master-plan titles, marks, priorities, dependencies, and the Phase 35 gate.
- **Disclosure artifact:** `docs/AI_USE_DISCLOSURE.md`.
- **Automated coverage:** `tests/test_ai_use_disclosure.py` checks the three official disclosure questions, exact five-task traceability, fail-closed human status, public-text privacy tokens, and unchanged open Phase 35 flags.
- **Protected baseline:** the three official CSVs and `models/artifact_registry.json` were SHA-256 guarded; all 12 registry-listed files matched their recorded hashes and sizes before documentation edits.
- **Confirmed data-sharing incident:** a human has confirmed that selected real competition-derived Task 1 and Task 2A inference inputs, identifiers, and numerical predictions were pasted into ChatGPT for notebook troubleshooting and inference-result interpretation. This does not establish that complete training or test datasets were uploaded. The disclosure reproduces none of the shared content.
- **Expanded human confirmation:** competition CSV/dataset files and private Jupyter notebooks were shared with ChatGPT and Codex; selected real inference inputs, identifiers, and predictions were shared with ChatGPT. Exact counts, completeness, per-tool inventory, and any additional transmissions remain under investigation.
- **Reported organizer response:** a WayLoom team member reports that Rootcode Tech Triathlon organizers said “no worries” and participation could continue. Date/time/channel, correspondent identities/roles, and written provenance are **NOT CONFIRMED**; no blanket permission or compliance finding is inferred.
- **Organizer-awareness update:** an authorized WayLoom team member confirms that the organizers knew actual competition CSV/dataset files and private Jupyter notebooks had been shared with ChatGPT and Codex before the reported response. This awareness is **HUMAN_CONFIRMED**; the response is `PERMISSION_TO_CONTINUE_REPORTED`. Dates, channel, names, written clearance, inference-snippet awareness, and broader compliance scope remain unconfirmed.
- **New written-response evidence:** the team supplied a Gmail screenshot whose visible content supports the reply subject, displayed Rootcode Team identity/domain, and exact response body. An authorized human confirms that their preceding email explicitly disclosed real Task 1 and Task 2A inference inputs, identifiers, and predictions shared with ChatGPT and that the response was in the same conversation. The context is `HUMAN_CONFIRMED` and the response is `SCREENSHOT_SUPPORTED`; raw headers and the complete exported thread have not been inspected. DT-454 is ready for fresh independent review without claiming a blanket exemption from unrelated rules.
- **Complete AI-tool inventory:** an authorized representative confirms ChatGPT and Cursor/OpenAI Codex were the only Datathon AI assistants. Confirmed categories are planning, requirements interpretation, coding assistance, debugging, implementation, testing, documentation, troubleshooting, and review. This does not import tools used only for other competition tracks.
- **AI modelling-restriction evidence:** repository verification is **PASS — no prohibited modelling implementation identified**. Registered prediction artifacts use local CatBoost and CatBoost/LightGBM with repository-controlled preprocessing/inference; no implemented proprietary remote modelling API, AutoML dependency, or low/no-code modelling service was found. The authorized representative additionally confirms no unrecorded restricted modelling tool or service was used; this is human testimony rather than independent proof of off-repository history.
- **Human decision ownership:** final model selection = Abdul Basith; business and optimization constraints = Mohamed Musamil; training and evaluation oversight = Divejikan; Task 2B allocation approval = Mustak Ahmed; final Datathon submission authorization = Divejikan. These assignments establish accountability without claiming exclusively human code authorship.
- **Final factual approval:** an authorized representative confirms that the disclosure accurately records the known external sharing and reported organizer communication and approves its factual accuracy, including labelled uncertainties. This is not organizer approval or an independent-review verdict.
- **Preserved limitations:** exact shared filenames/counts/completeness, additional unidentified transmissions, organizer date/time/channel/correspondents/written provenance, organizer awareness of inference snippets, and guidance on eligibility/deletion/remediation/disclosure remain unconfirmed. No blanket compliance or organizer-clearance conclusion is made.
- **Current task disposition:** DT-451, DT-452 and DT-453 are **IMPLEMENTED — READY FOR INDEPENDENT REVIEW**. DT-454 is **READY FOR FRESH INDEPENDENT REVIEW** based on official-rule disclosure, human-confirmed same-conversation context, and the screenshot-supported response; no blanket exemption or invented deletion/remediation terms are claimed. DT-455 is **PASS — HUMAN APPROVED; INDEPENDENT REVIEW PENDING**.
- **Clarification artifact:** `docs/PHASE35_ORGANIZER_CLARIFICATION_REQUEST.md` contains a sanitized request without identifiers, predictions, confidential rows, prompts, or files.
- **Communication record:** `docs/PHASE35_ORGANIZER_COMMUNICATION_RECORD.md` records the reported continuation decision and keeps missing provenance/scope fields explicitly unconfirmed.
- **Human approval gate:** `docs/PHASE35_FINAL_HUMAN_APPROVAL_CHECKLIST.md` records the direct answers, responsibility assignments, preserved historical ambiguity, and current approval provenance.
- **Verification results:** Phase 35 disclosure tests **14 passed**; combined Phase 35/36 documentation tests **39 passed**; full safe suite **897 passed, 2 skipped, 4 warnings** after repairing the stale Phase 36 post-closure status assertion; `python -m pip check` and `git diff --check` passed.
- **Protected integrity:** all three official CSV hashes, the artifact-registry hash, the final-notebook hash, and all 12 registered artifact hashes/sizes remained unchanged. No private rows or model bytes were opened or deserialized.
- **Master status:** intentionally unchanged. Phase 35 is ready for a fresh independent read-only review but remains formally incomplete until that review passes and a separate administrative closure is authorized. Phase 36's already completed status is not altered by this Phase 35 implementation update.

### 19.2 Formal completion report — final independent re-review PASS

**Closure authority.** A final narrow, fresh, read-only DT-455 re-review returned **PASS**, reconfirmed DT-451 through DT-454 as PASS, found no blockers, and explicitly authorized formal Phase 35 administrative closure. This section records that verdict; it does not claim this administrative edit independently reran the review's tests.

| Task | Final verdict | Completion evidence |
|---|---|---|
| DT-451 — Record all AI-assisted activities | PASS | Authorized human confirmation identifies ChatGPT and Cursor/OpenAI Codex as the complete Datathon assistant inventory and records their actual development activities without importing other competition tracks. |
| DT-452 — Record human-controlled modelling work | PASS | Local CatBoost/LightGBM and repository Task 2B evidence is separated from human-confirmed model, constraint, training/evaluation, allocation and submission responsibilities. |
| DT-453 — Record where AI was not used | PASS | Human-local notebook, parity, validation and checker execution plus human decision ownership are recorded without denying AI-assisted implementation. |
| DT-454 — Confirm compliance with competition restrictions | PASS | Competition CSV/dataset, notebook and real inference-result sharing is truthfully disclosed. Human-confirmed same-conversation context and the screenshot-supported organizer response were accepted for the disclosed incident only; no blanket exemption, authenticated-header claim or invented deletion/remediation instruction is made. |
| DT-455 — Write final AI-tool disclosure | PASS | The stale organizer statements were corrected, semantic cross-document and negative mutation tests were added, exact-version human approval was hash-bound in a separate record, and the final independent re-review verified the repair. |

**Approved immutable versions.** The authorized representative approved the following exact files, and the approval record binds to these hashes without modifying them:

- `docs/AI_USE_DISCLOSURE.md`: `715c2dca328a6792adffad5073633fcd7e362272578dbed788a8179418b6d4d3`
- `docs/PHASE35_FINAL_HUMAN_APPROVAL_CHECKLIST.md`: `ef448b08c5666ef691039e077e96dbae4c9f9c1b7435e4979978a2c0dc0e3c79`
- Approval provenance: `docs/PHASE35_FINAL_HUMAN_APPROVAL_RECORD.md`; factual approval only, not a blanket competition-rule exemption.

**Independent-review history.** The first fresh Phase 35 final review returned **FAIL** only for DT-455. It found two stale checklist statements, insufficient cross-document contradiction detection, and no verified renewed approval for the exact post-update text. DT-451 through DT-454 passed. A narrow repair preserved all sharing disclosures, synchronized organizer-evidence wording, added a semantic validator and two mutation tests, and marked renewed approval pending. An authorized representative then approved the exact SHA-256 versions above. The narrow fresh DT-455 re-review independently recomputed both hashes, verified the hash-bound approval, observed the repaired tests, returned **PASS** for DT-455, reconfirmed all five tasks, and authorized closure. The earlier FAIL and the earlier ambiguous/incomplete signoff remain preserved as historical evidence rather than rewritten as passes.

**Verification evidence.** The final independent re-review observed Phase 35 tests **18 passed**, combined Phase 35/36 documentation tests **43 passed**, `python -m pip check` PASS and `git diff --check` PASS. The administrative closure verified the same approved document hashes, unchanged official CSV/registry/final-notebook hashes, all **12/12** registered artifact checksum and size entries, ignored and unstaged private organizer evidence, and no staged files. No private row or model deserialization was required.

**Protected integrity.** Official hashes remained:

- `outputs/submission_task1.csv`: `9e0faa83a8dd1401ebaf72f1b1602dc560049d4a0cfba19676dbb69bf0de7918`
- `outputs/submission_task2a.csv`: `142842eef5e4a2e7a6db450c19f4062e4a6eb065481aa21720b59556f9edd55d`
- `outputs/submission_task2b.csv`: `15f98c8abc434811bc8d6db6ce64c4a746d0acd401f9147d7b15c0958d62b431`
- `models/artifact_registry.json`: `eb1491b782f835cd7ec5046980d3ea234c9a69e68e006a4eef885f1feef5c82d`
- `TeamName_FinalNotebook.ipynb`: `da7127bba73e6537631b281a70dcc17fad70f5ded5261a4ddfb624b11917f021`

**Final closure disposition.** DT-451 through DT-455 are **5/5 COMPLETE**. The Phase 35 Definition of Done and formal closure gate are satisfied. Phase 35 is formally closed, the synchronized master-plan readiness is **YES**, Phase 36 remains closed and unchanged, and this administrative action does not begin Phase 37.

## 20. Ready-to-copy Cursor/Codex implementation prompt

This appendix duplicates the full implementation instructions delivered separately as `PHASE_35_CODEX_CURSOR_PROMPT.txt` so the contract is self-contained.

```text
WAYLOOM DATATHON — PHASE 35 CURSOR/CODEX IMPLEMENTATION
AI-USE DISCLOSURE | DT-451 THROUGH DT-455 | STRICT SOURCE-OF-TRUTH

ROLE
You are a senior competition compliance analyst, evidence-grounded technical writer, Python repository maintainer, and privacy reviewer. Work in the ACTUAL local WayLoom Datathon repository. This is a disclosure/documentation phase, NOT modelling, retraining, submission regeneration or an AI-product feature implementation.

READ BEFORE ANY EDIT
1. AGENTS.md and CODEX_HANDOFF_PHASE_11_ONWARDS.md.
2. Official MD Files/Challenge Booklet.pdf, especially printed page 22, Rules and Regulations, Terms and Conditions and Deliverables.
3. MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md — copy the EXACT Phase 35 DT-451, DT-452, DT-453, DT-454 and DT-455 titles, mark, priority, dependency and phase gate. IMPORTANT: The externally supplied handoff confirms the range and theme, but not verbatim task titles. DO NOT accept the workstream names in the draft contract as verbatim master-plan labels. If a mismatch exists, reconcile the draft contract to the actual master; do not silently change the master.
4. MD Files/PHASE_35_COMPETITION_CONTRACT.md — implement every acceptance criterion, test, edge case and stop condition.
5. Phase 34 signed formal closure (13/13, independent PASS and ready-next YES) and relevant Phase 31/32/33 closure summaries.
6. Only the relevant sanitized repository documentation, code history and existing tool-use evidence. Do NOT inspect restricted row-level data.

MANDATORY PRECONDITIONS
- Verify Phase 34 is formally closed in CURRENT working tree and master plan: DT-438–DT-450 checked; Phase complete [x]; READY FOR NEXT PHASE YES; independent PASS recorded. STOP if not.
- Capture git status and preserve pre-existing changes. Record protected output CSV, artifact registry and registered-model hashes BEFORE any work using read-only metadata; DO NOT print private rows.
- Extract all FIVE exact master-plan task entries. List any naming differences and conform work to the actual source. STOP for material scope conflicts.
- Verify the official rules: AI tool disclosure must explain what work was AI-assisted, what was not, and how tools were used. Pretrained-model and proprietary API-based modelling/preprocessing restrictions, prohibited low/no-code fully automated modelling, and competition-data sharing restrictions are distinct. Do not infer that ordinary writing assistance was itself an approved modelling method.

DELIVERABLES (confirm actual repo conventions, no invented official filename)
A. A concise, competition-ready AI-use disclosure in an appropriate docs path (candidate: docs/AI_USE_DISCLOSURE.md). The official booklet specifies CONTENT, not this filename.
B. A sanitized internal evidence/coverage register or annex only if necessary and explicitly approved for project use. It must not contain private prompts, output samples, identifiable row IDs, raw datasets or credentials.
C. Tests/lint checks for disclosure coverage/claims where practical, non-destructive. Existing tools may be reused; avoid overengineering a documentation phase.
D. A Phase35 task-to-evidence matrix; an explicit human attestation gate listing unknowns and open factual questions.
E. Updated Phase35 contract implementation/evidence sections if permissible under existing workflow; DO NOT check master-plan phase-complete/readiness before fresh independent review and final status synchronization.

COMPLETE TASK SET — NO OMISSIONS
DT-451: implement the workstream associated with its actual master-plan title, including a verified inventory of AI tools and uses. Provisional engineering workstream only until master is inspected.
DT-452: implement the actual master-plan requirement, including a clear mapping of AI assistance by activity, stage and artifact, accurately separating ideation/writing/coding/debug/test assistance from model training/inference.
DT-453: implement the actual master-plan requirement, including explicit human/team work and what was NOT AI-assisted; provide human ownership and factual sign-off. Never fill unknowns with guesses.
DT-454: implement the actual master-plan requirement, including official rule/compliance checks, absence of prohibited conduct only when evidence supports it, correct distinctions between foundation-model writing assistants and competition modelling restrictions, and privacy boundaries.
DT-455: implement the actual master-plan requirement, including readable final disclosure, completeness, consistency, safe packaging handoff, proof checks, human acceptance, and independent-review readiness.
Replace these provisional shorthand labels with exact master titles inside the resulting report once read.

DISCLOSURE MUST BE SPECIFIC AND HONEST
- Tool/service, purpose, activity or artifact, inputs at a safe category level, outputs at a safe category level, when/how used, human review, independent execution/validation and limitations.
- Include only tools VERIFIED in project evidence or confirmed by human operator. ChatGPT, Cursor/Codex appear in project conversation as writing/coding assistance; confirm actual dates/scopes. Never claim Google Stitch was used for Datathon unless Datathon evidence confirms it (past Designathon activity is a DIFFERENT submission track).
- Explicitly cover human-authored/locally run actions: data handling, decisions, training/evaluation, model selection, saved-model tests, allocation decisions, private Jupyter Run All, official checker and submission upload ONLY where humans confirm or evidence supports them. Do not automatically credit humans with all actions if repository shows agent-driven work.
- Never claim AI use was zero, never claim all development was AI-driven, and never invent named humans, dates, versions, prompt histories, counts, consent, approval, or compliance clearance.
- If prohibited or ambiguous use is suspected, STOP, quarantine from disclosure approval and escalate for factual team investigation/organizer clarification; do not conceal it behind a generic disclaimer.
- Do not claim all private-data transmission was prevented merely from Git-ignore checks. A Git privacy check cannot prove that no information was sent through an external service. Ask the human for attestation and distinguish tested facts from declarations.
- Note that AI-assisted code generation and documentation do not by themselves mean proprietary API-based modelling/preprocessing occurred. Conversely, do not assume compliance based solely on this distinction: inspect evidence and ask a human to verify boundaries.

EXACT OFFICIAL BOUNDARIES
Challenge Booklet printed p.22:
- AI tool disclosure: explain which work was AI-assisted, which was not, and how tools were used.
- Restricted pretrained models except stated synthetic data generation/pre-processing exception.
- Proprietary API-based modelling/preprocessing prohibited.
- Low-code/no-code AI and fully automated end-to-end modelling tools prohibited.
- Dataset distribution/transmission to third parties prohibited; derivatives may not be made public without organizer authorization.
- Do not transmit restricted data or private output rows to external tools during this phase.

EXECUTION PLAN
1. Read and extract exact master IDs/titles, confirm dependency and protected baselines.
2. Build an honest evidence matrix for AI uses. Mark every claim VERIFIED / HUMAN-CONFIRMED / UNKNOWN; file+line/test info for technical proof where safe. Never cite unverifiable sources as proof.
3. Ask the human ONE grouped verification checklist for unknown actual tool use, roles, external transmission, forbidden-tool risk, private-data handling and final declaration; do not fabricate answers. Continue only with supported parts.
4. Draft clear final disclosure: overview; tools and specific assistance; non-AI/human work; modelling and data compliance; review/verification; limitations and sign-off; no private information.
5. Reconcile each of five exact master tasks against artifact evidence and the official p22 disclosure requirement.
6. Run non-destructive checks: synthetic doc validation; tests if added; selected/full pytest only if necessary/non-writing; pip check; git diff --check; git status; protected SHA256 guards (all 3 CSVs, registry, 12 registered models).
7. Keep master Phase35 task/phase flags PENDING until a FRESH, independent, read-only review returns PASS and a separate formal closure update is authorized.

FILES / CHANGE SCOPE
Prefer only a docs AI-use disclosure, a minimal synthetic/metadata-only tracker/test if needed, and limited Phase 35 contract implementation notes. Do not touch:
- outputs/submission_task1.csv, outputs/submission_task2a.csv, outputs/submission_task2b.csv;
- models/** and models/artifact_registry.json;
- actual competition data under data/raw/** or data/interim/**;
- reports/private/** (do not read/overwrite);
- TeamName_FinalNotebook.ipynb or any retraining/inference/optimizer production logic;
- prior phase statuses and Phase36+ tasks.
Never stage or commit without explicit permission.

STOP IMMEDIATELY IF
- Phase34 closure invalid;
- exact five task definitions unavailable or materially contradict draft assumptions;
- a disclosure claim about an AI tool, human work or restricted data cannot be substantiated;
- plausible prohibited API modelling, pretrained model or auto-ML use requires investigation;
- a protected hash differs;
- a step requires private records, prompts containing confidential data, or transmission of restricted material;
- the agent is tempted to 'improve' a model, official submission, prior-phase status or human sign-off.

FINAL REPORT (exact)
PHASE35 PRECONDITION: PASS / FAIL
SOURCE INVENTORY: DT-451–DT-455 exact master titles and labels copied / NOT VERIFIED
DT-451: PASS / FAIL / PENDING + evidence
DT-452: PASS / FAIL / PENDING + evidence
DT-453: PASS / FAIL / PENDING + evidence
DT-454: PASS / FAIL / PENDING + evidence
DT-455: PASS / FAIL / PENDING + evidence
AI-USE DISCLOSURE DRAFT: COMPLETE / BLOCKED
HUMAN FACTUAL ATTESTATION: RECEIVED / PENDING
OFFICIAL AI/DATA RULE CHECK: PASS / FAIL / ESCALATION
SYNTHETIC DOC TESTS: exact counts or NOT RUN with reason
FULL SAFE TESTS: exact counts or NOT RUN with reason
PIP / GIT DIFF CHECK: PASS / FAIL
FROZEN OFFICIAL CSV SHA256: UNCHANGED / CHANGED / NOT CHECKED
REGISTRY + 12 MODEL HASHES: PASS / FAIL / NOT CHECKED
PRIVATE DATA / GIT SAFETY: PASS / FAIL
FILES CREATED / CHANGED: exact paths
BLOCKERS: none / specifics
READY FOR FRESH INDEPENDENT PHASE35 REVIEW: YES / NO
PHASE35 FORMALLY CLOSED: NO
PHASE36 STARTED: NO

Proceed with implementation ONLY after the preconditions and exact master inventory are verified. Do not invent evidence or silently make official-rule assumptions.

```

## 21. Ready-to-copy fresh independent review prompt

This appendix duplicates the full review instructions delivered separately as `PHASE_35_INDEPENDENT_REVIEW_PROMPT.txt`. Run it in a **new read-only session** after implementation and human fact-checking.

```text
WAYLOOM DATATHON — PHASE 35 FRESH INDEPENDENT REVIEW
AI-USE DISCLOSURE | DT-451–DT-455 | STRICT READ-ONLY

ROLE
You are an INDEPENDENT competition rules reviewer, technical writer, privacy auditor, and repository-integrity verifier. New session; no prior coding involvement. Work READ-ONLY. No edits, automatic fixes, staging, commits, model runs, output regeneration or Phase36 implementation.

SOURCES (AUTHORITY ORDER)
1. Official MD Files/Challenge Booklet.pdf, printed p22 (Rules/Terms/Deliverables), and any organizer FAQ/clarification actually included in the repository.
2. MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md: exact Phase35 DT-451 through DT-455 titles, task mark, priority, dependency and completion gate. NOTE: External handoff confirms the ID range and theme, NOT titles. First verify the five exact entries; flag any contract/name drift.
3. MD Files/PHASE_35_COMPETITION_CONTRACT.md.
4. Phase34 independent PASS + formal closure record, and relevant Phase31–33 records.
5. Actual AI disclosure document, safe evidence and implementation history; validate claims with repository evidence when possible and HUMAN ATTESTATIONS where necessarily external.
6. AGENTS.md, CODEX_HANDOFF_PHASE_11_ONWARDS.md.

READ-ONLY PRECONDITION CHECK
- Phase34 DT-438–DT-450 13/13 checked, phase complete [x], readiness YES and independent PASS evidence recorded.
- Preserve current git status; do not restore pre-existing changes.
- Verify no private information needs to be read; use filenames/hashes and aggregate sanitized summaries only.
- If master plan lacks exact DT-451–455 inventory, STOP and report unable to verify task names; do not fill titles from inference.

REVIEW ALL FIVE TASKS INDIVIDUALLY
For each DT-451, DT-452, DT-453, DT-454, DT-455: quote exact master work item; map to content/line references/test; issue PASS/FAIL; list specific blocking remedy. No easy all-PASS based on presence of a heading.

OFFICIAL DISCLOSURE REQUIREMENT (BOOKLET PRINTED P22)
The submitted AI-use disclosure must explain WHICH work was AI-assisted, WHICH was not, and HOW tools were used. Verify identifiable tools and actual scopes; do not accept unsupported 'we used AI ethically' platitudes.

SUBSTANTIVE REVIEW
A. Tool inventory: Evidence-backed tools/platforms and version if known; no hallucinated versions, dates or vendors; other contest tracks not misattributed to Datathon.
B. Work breakdown: Distinguish ideation, documentation, Python coding, testing, model training, training-run execution, actual saved models, inference, allocation optimization, validation, packaging and submission, with AI/human role accurate for each.
C. Human-owned / NOT AI assisted work: Explicit and evidence-supported, not a bare 'humans reviewed all'. Human-local activities must be tagged HUMAN-ATTESTED, not independently rerun by agent.
D. How tools were used: qualitative workflow details, safe category-level inputs and outputs, iterations, reviews, independent checks; no private prompts, identifiers, real rows, private predictions.
E. Official restrictions: prohibited pretrained models (limited official exceptions), prohibited proprietary API-based modelling/preprocessing and fully automated modelling tools; dataset third-party transfer, derivative publication and confidentiality. Check that claims are nuanced, actual evidence exists, risks are escalated; generic statements are not proof. The fact that an LLM helped write/correct code does not automatically mean it supplied the prediction model or processed private data; conversely avoid treating that distinction as proof of compliance.
F. Completeness: Final document readable, submission-ready, consistent with final notebook, architecture/README, final code/test history, without contradicting the earlier Phase34 report or Phase32 artifact registry.
G. Provenance: VERIFIED, HUMAN-CONFIRMED and UNKNOWN separated; unresolved material compliance or factual unknowns are FAIL until clarified by the human/organizer. Human sign-off documented but not forged.
H. No sensitive data or disallowed path exposure in final disclosure, docs, repo status or stdout.
I. No developer-generated 'approved by organizer' claim absent documentary evidence. Do not change source files to make review pass.

TEST/SAFETY VERIFICATION (ONLY NON-DESTRUCTIVE)
- Run available disclosure structure/lint tests, deterministic assertions against public text, and task-to-evidence mapping checks.
- If appropriate run existing safe targeted tests. Full suite not necessarily needed for documentation-only diff; if omitted, state NOT RUN, never invent.
- Run python -m pip check only if appropriate, git diff --check, git status --short, and staged-file check.
- Before and after, independently compare read-only hashes of the 3 official CSVs, artifact_registry.json and all 12 registered models. Do not run a validator that overwrites private reports.
- Verify reports/private ignored, no private artifacts tracked, no unapproved changes to model, outputs, final notebook or production code.
- Source p22 booklet rule and masters are absolute; project engineering additions are not organizer-imposed requirements.

STOP/FAIL IF
- Phase34 formal closure absent;
- DT task titles/requirements inferred rather than read;
- any task unproved;
- known AI assistance omitted;
- human-only assertions are invented or unsupported;
- private data transmission is declared impossible based only on Git ignore;
- any suspicious prohibited use unresolved;
- private data exposed;
- forbidden assets changed;
- protected hashes differ;
- evidence contains unverifiable approval or falsified tool-use descriptions.

REQUIRED OUTPUT
1. Exact master five-task inventory and task-by-task PASS/FAIL table with verifiable evidence.
2. Official p22 compliance matrix: AI-assisted / NOT AI-assisted / HOW / model/API/tool/data restrictions.
3. Claim-to-evidence audit; tool/workflow traceability; human confirmation outstanding.
4. Disclosure artifact names; content/format; readability; internal consistency.
5. Independent checks run (exact command, pass/fail/skip counts), and those not run.
6. Frozen hashes, model registry counts, privacy and git status.
7. Any finding about Phase32 administratively unchecked master plan as SEPARATE follow-up, not automatically a Phase35 blocker unless its dependency demands.
8. Blockers, next actions, formal Phase35 closure authorization and Phase36 readiness gate. DO NOT actually close phase in this read-only review.

FINAL VERDICT FORMAT
PHASE35 FRESH INDEPENDENT REVIEW: PASS / FAIL
PHASE34 PRECONDITION: PASS / FAIL
MASTER DT-451–DT-455 TITLES VERIFIED: YES / NO
DT-451: PASS / FAIL
DT-452: PASS / FAIL
DT-453: PASS / FAIL
DT-454: PASS / FAIL
DT-455: PASS / FAIL
OFFICIAL AI DISCLOSURE: PASS / FAIL
HUMAN ROLE + NON-AI WORK ACCURACY: PASS / FAIL
MODEL/API/AUTOML RESTRICTIONS: PASS / FAIL / REQUIRES HUMAN OR ORGANIZER CLARIFICATION
DATA PRIVACY + THIRD-PARTY SHARING: PASS / FAIL / REQUIRES HUMAN ATTESTATION
HUMAN ATTESTATION: VERIFIED / PENDING
DISCLOSURE DOC QUALITY: PASS / FAIL
TESTS: exact counts / NOT RUN, with reason
FROZEN CSV / REGISTRY / MODEL HASHES: PASS / FAIL / NOT CHECKED
GIT + PRIVACY: PASS / FAIL
FORMAL PHASE35 CLOSURE AUTHORIZED: YES / NO
PHASE36 MAY BEGIN AFTER REQUIRED CLOSURE: YES / NO
BLOCKERS: None / precise list
FILES MODIFIED BY REVIEW: NONE

```

---

## 22. Planning integrity note and handoff

- **Confirmed from the local master plan:** Phase 35 is AI-use disclosure; Section 4 records the exact DT-451–DT-455 inventory and metadata.
- **Confirmed from official booklet printed p.22:** the final disclosure must explain AI-assisted work, non-AI-assisted work and tool usage; the same page includes model/tool and competition-data restrictions.
- **Confirmed locally:** Phase 34 formal closure PASS and readiness YES; the protected artifact baseline is intact.
- **Implemented:** a fail-closed disclosure draft and narrow deterministic document tests.
- **Not yet done:** obtaining the mandatory human factual attestation and final wording approval, fresh independent Phase 35 review, formal closure, or Phase 36 work.

**Earliest authorized next action:** obtain the grouped human attestation, update only supported disclosure facts, and then request a fresh read-only Phase 35 review. **Do not treat this contract or the current draft as evidence of final factual approval.**
