# WayLoom Datathon — AI-Tool Use Disclosure

> **Status: CORRECTED FINAL DRAFT — RENEWED EXACT-VERSION HUMAN APPROVAL PENDING**
> An authorized WayLoom team representative confirmed the underlying factual attestations and approved an earlier version. After the independent review required organizer-evidence reconciliation, the corrected exact document requires renewed human approval. Neither the earlier approval nor the pending renewed approval is organizer approval, independent-review approval, or formal Phase 35 closure.

## Scope

This disclosure concerns the WayLoom **Datathon** work only. It separates generative-assistant support from the local machine-learning libraries and deterministic optimization code used to produce the competition results. It does not import tool claims from the Designathon or Hackathon tracks.

## Work that was AI-assisted

The repository records an AI-assisted development workflow. The safe evidence currently supports the following categories; it does not establish every tool version, date, prompt, or interaction.

The authorized representative confirms that ChatGPT and Cursor/OpenAI Codex were the only AI assistants used for the Datathon. Their confirmed assistance categories were planning, requirements interpretation, coding assistance, debugging, implementation, testing, documentation, troubleshooting, and review. Tools used only for other competition tracks are not included.

| Tool or workflow | What it assisted | How it was used | Safe inputs and outputs | Review or validation | Evidence status |
|---|---|---|---|---|---|
| Cursor/OpenAI Codex coding workflow | Repository development before and after the Phase 11 handoff | Assisted planning, requirements interpretation, coding, debugging, implementation, testing, documentation, troubleshooting, and technical reviews. The exact division between suggestions, edits, and human authorship is not reconstructed interaction by interaction. | Repository requirements, source code, documentation, schemas, synthetic fixtures, and human-confirmed private competition materials; code, tests, documentation, and reports | Changes were checked through version control, pytest, artifact hash guards, Git review, and separate review sessions. Human-local execution provenance does not negate the external sharing. | Tool inventory and usage categories `HUMAN_CONFIRMED`; counts and exact sharing scope unresolved |
| ChatGPT | Phase-contract and prompt drafting, notebook-execution troubleshooting, and interpretation of saved-model inference results | Helped prepare implementation/review instructions and explanatory text. Competition CSV/dataset files, private Jupyter notebooks, and selected real Task 1/Task 2A inference inputs and predictions were shared during the Datathon workflow. | Planning context and human-confirmed private competition materials, including real records, identifiers, and numerical predictions; generated troubleshooting and interpretive guidance | Repository contracts were reconciled to the master plan and official booklet. The external-sharing scope remains under compliance assessment. | `HUMAN_CONFIRMED`; exact sharing scope and compliance disposition unresolved |

AI assistance included writing and coding support. That fact does **not** mean a hosted language model generated the official predictions, trained the registered competition models through an API, or solved Task 2B remotely. Repository evidence and the authorized human attestation addressing those separate restrictions are recorded below.

## Human-confirmed data-sharing incident

An authorized human has confirmed that competition CSV/dataset files and private Jupyter notebooks were shared with ChatGPT and Codex. Selected Task 1 and Task 2A inference inputs, identifiers, and numerical predictions derived from real competition data were additionally pasted into ChatGPT; they were not synthetic demonstration records. ChatGPT was used for notebook-execution troubleshooting and interpretation of saved-model inference results. The precise purpose for every item shared with Codex is still being documented.

This establishes external transmission of private competition materials. Exact counts, filenames, the per-tool file inventory, and whether complete official training or test datasets were included are `COUNTS AND EXACT SCOPE PENDING`. Other transmissions, screenshots, derivatives, credentials, or secrets have not been fully verified; the disclosure does not declare that there were none.

The incident must be assessed against the official competition data-sharing, third-party-transmission, derivative-publication, confidentiality, and integrity restrictions. The representative previously approved this account's underlying sharing facts and unknowns. Renewed approval of the exact corrected document is pending; neither approval state creates an unconditional compliance conclusion, organizer submission approval, or Phase 35 closure.

## Reported organizer communication

An authorized WayLoom team member confirms that the Rootcode Tech Triathlon organizers were informed that actual competition CSV/dataset files and private Jupyter notebooks had been shared with ChatGPT and Codex before responding. Organizer awareness of those sharing categories is `HUMAN_CONFIRMED`.

The team supplied a Gmail screenshot of a written response attributed to the Rootcode Team stating, in part, “No problem at all,” “you can proceed as you wish,” and thanking the team for being transparent. The screenshot visibly supports the reply subject, displayed organizer identity/domain, and response body. An authorized human confirms that their preceding email explicitly disclosed real Task 1 and Task 2A inference inputs, identifiers, and predictions shared with ChatGPT and that the reply was in the same conversation. This is recorded as `ORIGINAL DISCLOSURE SCOPE: HUMAN_CONFIRMED` and `ORGANIZER WRITTEN RESPONSE: SCREENSHOT_SUPPORTED`.

The communication channel is email/Gmail, supported by the human-provided screenshot. The complete original conversation export and authenticated headers have not been inspected. The evidence therefore distinguishes human-confirmed same-conversation context from independently authenticated headers. The supplied response gives guidance to proceed following the disclosed activities; it gives no specific deletion or remediation instruction and is not treated as a blanket exemption from unrelated rules.

Accordingly, “may continue participating” is recorded as a reported continuation decision only. It is not represented as a finding that the sharing complied with the rules, blanket permission for future sharing, a waiver, or organizer approval of this disclosure. The independent Phase 35 reviewer accepted this evidence as sufficient for the disclosed incident, with these scope limitations preserved.

## Human-controlled modelling work

The repository verifies the technical result, and the authorized representative has supplied the decision-owner assignments below. Decision ownership does not imply that the named people manually authored all AI-assisted code.

- The registered Task 1 artifacts identify locally loadable CatBoost models; the registered Task 2A artifacts identify locally loadable CatBoost/LightGBM ensembles. Deterministic repository code supplies preprocessing and inference entry points. A public-source audit found no implemented proprietary remote modelling API or AutoML dependency, and configuration explicitly prohibits AutoML. This technical evidence does not prove that no unrecorded external modelling service was used.
- Task 2B is implemented as a deterministic optimization/allocation workflow, not as a trained language model.
- The Phase 31 record attributes the clean-kernel notebook Run All, final-cell-only check, and private saved-model parity execution to a human-local operator. The Phase 33 record similarly attributes final-file validation and the official Task 2B checker run to human-local evidence. These statements describe who executed the private checks; they do not claim the underlying code was written without AI assistance.
- Human-local execution is verified through the evidence above. The following responsibility assignments are `HUMAN_CONFIRMED`:

| Responsibility | Team-confirmed decision owner |
|---|---|
| Final model selection | Abdul Basith |
| Business and optimization constraints | Mohamed Musamil |
| Training and evaluation oversight | Divejikan |
| Task 2B allocation approval | Mustak Ahmed |
| Final Datathon submission authorization | Divejikan |

## Work that was not AI-assisted

The private-data notebook/checker/parity commands recorded in the Phase 31 and Phase 33 closure evidence were executed in the approved local environment by a human operator, not rerun by the external coding agent. The authorized representative additionally confirms the decision owners listed above. These are human execution and accountability statements; the related scripts, analysis, tests, and documentation may still have been AI-assisted, and no claim is made that the named people manually authored all code.

## Model, automated-tool, API, and data-handling boundaries

The official rules distinguish the AI-use disclosure from restrictions on prediction models, remote modelling/preprocessing, automated modelling platforms, and competition-data handling.

| Official boundary | Repository-supported finding | Remaining human confirmation |
|---|---|---|
| Restricted pretrained models, subject to the stated synthetic-data/preprocessing exception | Technical evidence: `PASS`. The artifact registry describes locally loadable CatBoost and CatBoost/LightGBM competition artifacts with repository-controlled preprocessing and inference. No pretrained predictive model implementation was identified as training models or generating final Task 1/Task 2A predictions. | `HUMAN_CONFIRMED`: no additional or unrecorded pretrained predictive model was used. This is testimony, not independent proof of off-repository history. |
| No proprietary API-based modelling or preprocessing | Technical evidence: `PASS`. The reviewed dependencies, source, and registered inference entry points contain no implemented proprietary remote modelling/preprocessing API. ChatGPT/Codex development assistance and confirmed information sharing are disclosed separately and are not hidden by this technical finding. | `HUMAN_CONFIRMED`: no proprietary remote modelling or preprocessing API was used. |
| No low-code/no-code AI or fully automated end-to-end modelling tool | Technical evidence: `PASS`. The repository contains explicit feature, training, validation, inference, optimization, and test code; no AutoML dependency or low/no-code modelling implementation was identified, and configuration prohibits AutoML. | `HUMAN_CONFIRMED`: no AutoML platform or low-code/no-code predictive modelling service was used. |
| Competition data must not be distributed or transmitted to third parties, and derivatives must remain confidential | Human confirmation establishes that competition CSV/dataset files and private Jupyter notebooks were shared with ChatGPT and Codex, and selected real inference inputs, identifiers, and predictions were shared with ChatGPT. An authorized human confirms those inference details were disclosed in the email conversation before the screenshot-supported organizer response. | Exact file counts/completeness, additional unidentified transmissions, raw-header authentication, and specific deletion/remediation instructions remain unconfirmed; no blanket exemption is inferred. |

The project makes no categorical compliance claim based on static source, ignored paths, or passing tests. The confirmed external transmission is an open compliance matter, not an absence-of-evidence question.

## Human oversight and independent checks

- Phase 31 records human-local clean-kernel/final-cell validation and saved-model parity, while explicitly distinguishing that evidence from agent execution.
- Phase 32 records a 12-entry model artifact registry with checksum, schema, fresh-process loading, and synthetic-inference controls.
- Phase 33 records human-local final-submission and official-checker validation followed by an independent review.
- Phase 34 records synthetic/deterministic automated coverage and a separate fresh independent review.
- Phase 35 uses read-only SHA-256 guards for the three official submission CSVs, the registry, and all 12 registered artifacts. These integrity checks do not inspect private rows or deserialize model files.

These checks support software and artifact integrity. They are not organizer approval and are not substitutes for the team's factual declaration about tool use and data handling.

## Task-to-evidence register

| Task | Exact master-plan work item | Current evidence | Implementation status |
|---|---|---|---|
| DT-451 | Record all AI-assisted activities | ChatGPT and Cursor/OpenAI Codex are the human-confirmed complete Datathon assistant inventory; their activity categories and the external sharing are recorded | `IMPLEMENTED — READY FOR INDEPENDENT REVIEW` |
| DT-452 | Record human-controlled modelling work | Local model families, human-local validation, and the five team-confirmed decision-owner assignments are recorded without denying AI-assisted implementation | `IMPLEMENTED — READY FOR INDEPENDENT REVIEW` |
| DT-453 | Record where AI was not used | Human-local private execution and team decision ownership are distinguished from AI-assisted source, tests, and documentation | `IMPLEMENTED — READY FOR INDEPENDENT REVIEW` |
| DT-454 | Confirm compliance with competition restrictions | Technical and human attestations find no prohibited modelling tool use; sharing is disclosed; an authorized human confirms the organizer reply followed explicit inference-sharing disclosure, and the response is screenshot-supported; the independent reviewer accepted the incident-specific scope without finding a blanket exemption | `PASS — INDEPENDENTLY REVIEWED` |
| DT-455 | Write final AI-tool disclosure | The stale organizer statements were reconciled and cross-document consistency checks added; renewed human approval must bind to the exact corrected disclosure and checklist versions | `IMPLEMENTED — RENEWED HUMAN APPROVAL AND NARROW RE-REVIEW PENDING` |

## Final human verification record

| Verification item | Recorded answer | Status |
|---|---|---|
| Organizer awareness of inference inputs, identifiers, and predictions shared with ChatGPT | Authorized human confirms the preceding email explicitly disclosed them and the response was in the same conversation | `HUMAN_CONFIRMED`; response `SCREENSHOT_SUPPORTED`; raw headers not independently authenticated |
| Eligibility, deletion, remediation, and disclosure guidance | Organizers reportedly said “no worries” and permitted continued participation; no specific guidance on these subjects is confirmed | `NOT CONFIRMED BEYOND CONTINUED PARTICIPATION` |
| Files and scope shared | CSV/dataset files and private Jupyter notebooks were shared with ChatGPT and Codex; real inference records and predictions were shared with ChatGPT | `HUMAN_CONFIRMED`; filenames, counts, completeness, and other transmissions `NOT CONFIRMED` |
| Prohibited modelling tools | Local CatBoost/LightGBM pipelines and no prohibited implementation identified in repository evidence | `TECHNICAL PASS` and `HUMAN_CONFIRMED`: no additional restricted modelling tool was used |
| AI-tool inventory | ChatGPT and Cursor/OpenAI Codex were the only Datathon AI assistants | `HUMAN_CONFIRMED COMPLETE` |
| Prohibited modelling/automated tools | No additional pretrained predictive model, proprietary remote modelling/preprocessing API, AutoML platform, or low/no-code predictive modelling service was used | `HUMAN_CONFIRMED`; consistent with repository technical evidence |
| Human responsibility | Human-local operators executed notebook, parity, and private validation procedures; Abdul Basith owned final model selection, Mohamed Musamil owned business/optimization constraints, Divejikan owned training/evaluation oversight and final submission authorization, and Mustak Ahmed owned Task 2B allocation approval | `HUMAN_CONFIRMED`; decision ownership does not imply exclusively human code authorship |
| Communication provenance | Channel is email/Gmail; the human-provided screenshot supports reply subject, displayed Rootcode Team identity/domain, and response body; same-conversation context is human-confirmed | Complete original conversation export `PENDING`; original headers not independently authenticated |
| Earlier approval response (historical) | An earlier response did not establish approval and contained an ambiguous modelling answer | Preserved as history; superseded by the new direct authorized attestation below |
| Earlier factual approval | The authorized representative approved the earlier disclosure version and its stated uncertainties | `HUMAN_CONFIRMED — HISTORICAL`; material organizer-evidence reconciliation followed |
| Renewed exact-version approval | An authorized representative must approve the corrected disclosure and checklist identified by their final SHA-256 values | `PENDING` |

## Human approval and remaining limitations

The authorized representative directly confirmed approver authority, the complete Datathon AI-tool inventory, the absence of additional restricted modelling tools, the five human responsibility assignments, and the external-sharing and organizer-communication facts. The representative approved an earlier disclosure version, superseding the unresolved answers in the earlier minimal signoff without deleting that historical record. Because the organizer-evidence language was materially reconciled after that approval, renewed approval must identify the exact corrected disclosure and checklist versions.

The earlier approval does not resolve exact shared filenames/counts/completeness, additional unidentified transmissions, the exact organizer-message date, authenticated original headers, or specific deletion/remediation instructions. These limitations remain visible and prevent a blanket exemption claim. The human-confirmed same-conversation context and screenshot-supported reply were accepted by the independent reviewer as sufficient for the disclosed incident; the complete original conversation export remains pending private preservation.

The approval checklist is maintained in `docs/PHASE35_FINAL_HUMAN_APPROVAL_CHECKLIST.md`. Phase 35 remains open until an authorized representative approves the exact corrected versions, a narrow fresh DT-455 review passes, and a separate administrative closure is authorized.

**Attestation status:** `HUMAN CONFIRMED`
**Earlier-version factual approval:** `HUMAN CONFIRMED — HISTORICAL`
**Renewed exact-version factual approval:** `PENDING`
**AI modelling-restriction technical evidence:** `PASS — NO PROHIBITED MODELLING IMPLEMENTATION IDENTIFIED`
**AI modelling-restriction human attestation:** `PASS — NO ADDITIONAL RESTRICTED MODELLING TOOLS USED`
**Compliance resolution:** `DT-454 PASS — INDEPENDENT REVIEW ACCEPTED HUMAN-CONFIRMED DISCLOSURE CONTEXT AND SCREENSHOT-SUPPORTED GUIDANCE FOR THE DISCLOSED INCIDENT; NO BLANKET EXEMPTION CLAIMED`
**Submission status:** `READY FOR AUTHORIZED FINAL APPROVAL — RENEWED APPROVAL AND NARROW DT-455 RE-REVIEW PENDING; PHASE 35 REMAINS OPEN`
