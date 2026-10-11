# WayLoom Datathon — Codex Repository Instructions

## Scope

This repository is the WayLoom submission for the Rootcode Tech-Triathlon 2026 Datathon.

Use `WAYLOOM_DATATHON_MASTER_PLAN.md` and the current `PHASE_XX_COMPETITION_CONTRACT.md` as task-level execution contracts. Use `CODEX_HANDOFF_PHASE_11_ONWARDS.md` for the post-Phase-10 handoff and global workflow.

## Authority

When requirements conflict, follow:

1. Official Challenge Booklet and official supplied artifacts/templates/checker.
2. `WAYLOOM_DATATHON_MASTER_PLAN.md`.
3. Approved phase contracts.
4. Existing tested frozen production code.
5. Engineering assumptions.

Do not silently change an official rule.

## Restricted competition data

Do not inspect or print row-level content from:

```text
data/raw/**
data/interim/**
reports/private/**
```

Use synthetic fixtures for agent-run tests. The human operator runs real competition-data commands locally and shares sanitized PASS/FAIL status when needed.

Never print private IDs, raw competition rows, row-level labels or predictions into chat output.

## Completed/frozen work

Phases 00–10 are complete.

Task 1 final output has passed revalidation. Treat these as frozen unless a later formal global validation finds a genuine defect:

```text
configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv
```

Do not reopen Task 1 model search while implementing Task 2A/Task 2B.

## Engineering autonomy

You may autonomously:

- edit phase-relevant tracked code/config/docs;
- add synthetic tests;
- run targeted/full safe tests;
- inspect failures and fix ordinary bugs;
- run `python -m pip check`;
- inspect `git status` and `git diff`;
- self-review against the current phase Definition of Done.

Do not stop for routine coding failures you can safely fix.

## Mandatory stops

Stop and report a blocker for:

- official-rule ambiguity;
- need for restricted row-level competition data;
- conflict with a frozen prior-phase contract;
- leakage/future-information issue;
- material design change outside the current phase;
- genuine schema/data-quality blocker;
- competition AI/data-compliance concern.

## Phase discipline

Implement only the current phase. Do not start the next phase automatically.

Use targeted context. Read earlier phase contracts only when the current phase depends on them; do not reread the entire repository unnecessarily.

For high-risk or multi-hour phases, use an ExecPlan. For routine documentation or small changes, avoid unnecessary planning overhead.

## Testing

After phase implementation:

```bash
pytest -q
python -m pip check
git status
```

If a documented test requires restricted real data, do not run it in the agent context. Report the exact local command for the operator.

## Git/data safety

Never stage/commit:

```text
data/raw/**
data/interim/**
reports/private/**
credentials/secrets
private experiment artifacts
```

## End-of-phase report

Return a compact report containing:

```text
TASK STATUS
FILES CREATED/MODIFIED
TEST RESULTS
STOP CONDITIONS
PRIVATE DATA ACCESSED: NO
HUMAN LOCAL ACTION REQUIRED: YES/NO
EXACT LOCAL COMMAND (if required)
READY FOR NEXT PHASE: NO
```

A fresh independent review session must pass before the next phase begins.
