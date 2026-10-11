# WayLoom Datathon — AI-Tool Use Disclosure

**Status: Proposed competition-facing wording — authorized team review required before submission.**

## Scope

This disclosure concerns the WayLoom submission to the Rootcode Tech Triathlon 2026 **Datathon**. It describes generative AI assistance, what was done through local project tooling and human execution, and known limitations. It does not automatically attribute tools used only in the Designathon or Hackathon to this track.

## Work assisted by AI and how the tools were used

| Tool | Datathon involvement |
|---|---|
| **ChatGPT** | Explaining and interpreting requirements; planning the modelling and documentation workflow; drafting project contracts, review prompts and explanatory text; troubleshooting Jupyter notebook execution; interpreting execution status and selected Task 1/Task 2A inference demonstrations. |
| **Cursor / OpenAI Codex** | AI-assisted repository coding, debugging, test design, source review, documentation, traceability, and technical audits. Some code and documentation were drafted or modified with AI assistance; human-local execution of some validation steps does **not** establish that their source code was entirely human-written. |

These are the tools **confirmed in the available records**. The team has not yet attested that this is a complete inventory of every AI assistant used during the Datathon.

## Work completed through local workflows and human execution

The project records identify locally runnable **CatBoost** models for Task 1 and a **CatBoost/LightGBM ensemble** for Task 2A, together with repository-controlled preprocessing and inference. Task 2B uses a coded deterministic optimization/allocation workflow rather than a language model acting as the optimizer.

The final-notebook clean-kernel execution, separate saved-model inference/parity checks, and certain private validation/checker runs were performed **by a human operator in the local project environment**, based on the project's human-local closure evidence. Their scripts and implementation may have been AI-assisted. The records do not independently establish every human decision-maker for model choice, feature and business constraints, complete training/evaluation history, allocation approvals, or submission authorization; the team must confirm those responsibilities separately.

## Competition tool restrictions and data handling

The official Challenge Booklet restricts pretrained models (with specified exceptions), prohibits proprietary API-based modelling/preprocessing and low/no-code or fully automated end-to-end modelling tools, and restricts third-party transmission of competition datasets. The reviewed project evidence identifies local model artifacts and found **no implemented proprietary remote modelling/preprocessing API or AutoML dependency**. This technical finding does not prove that no unrecorded off-repository service was ever used; complete historical tool usage remains subject to human confirmation.

**Confirmed external transfers:** The team has confirmed that competition CSV/dataset files and private Jupyter notebook files were shared with **ChatGPT and OpenAI Codex**. Separately, selected **real competition-derived** Task 1 and Task 2A inference input records, identifiers, and numerical predictions were pasted into ChatGPT while troubleshooting final notebook execution. These demonstrations were **not purely synthetic**. This disclosure does not claim that full datasets were or were not uploaded to either service, because exact file scope, counts and completeness have not been established.

**Reported organizer communication:** A team member reports that the competition organizers were informed of competition CSV/dataset and private notebook sharing with ChatGPT/Codex, responded **“no worries,”** and indicated the team could continue. The precise date, channel, participants, complete wording and written evidence have not been established in the available record. Whether the organizers were specifically told about the separate real inference snippets or addressed disclosure, remediation, deletion and final submission eligibility is not established. The reported response is **not represented as blanket written compliance clearance**.

No actual competition rows, private identifiers, numerical predictions, private notebooks, uploaded datasets or credentials are reproduced in this disclosure.

## Verification and oversight

The project reports local saved-model inference, output integrity, Phase 32 registered artifact checks, Phase 33 official file validation, and Phase 34 automated testing and independent review. These support reproducibility and implementation quality, **not** a categorical finding that data-sharing or tool-use rules were complied with. The disclosure must be reviewed for factual accuracy by an authorized team representative, and the unresolved issues above must remain visible unless new verifiable information resolves them.

**Factual approval status: PENDING AUTHORIZED TEAM REVIEW.** The team has not yet provided final authorization of this exact draft.
