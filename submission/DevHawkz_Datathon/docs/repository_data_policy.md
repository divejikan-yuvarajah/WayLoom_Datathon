# Repository and Competition-Data Policy

**Scope:** WayLoom Datathon, Rootcode Tech-Triathlon 2026  
**Classification:** Internal engineering policy  
**Phase:** 01

## 1. Raw competition data

Official competition datasets are restricted competition material. They may be used only for this competition and must remain local to an approved working environment.

- Place raw files only under ignored local data paths such as `data/raw/`.
- Do not copy raw files into source, notebooks, documentation, models, outputs, or reports.
- Do not commit, publish, upload, distribute, or transmit raw competition files.
- Do not inspect or process raw rows before the phase that authorizes that work.

## 2. Derivative-data policy

Private derivatives include processed tables, row-level extracts, feature tables, cached notebook outputs, predictions, labels, and logs that can reveal or reconstruct competition records.

- Keep derivatives local under ignored `data/interim/` or `data/processed/`.
- Never commit or publish row-level derivatives.
- Do not place private rows in screenshots, examples, documentation, tests, prompts, or demo materials.
- Synthetic fixtures and schema-only examples are preferred for tests and documentation.
- Aggregates may be shared only after confirming they cannot disclose or reconstruct restricted data and the competition rules permit the use.

## 3. Git restrictions

- The repository must remain private or local-only while restricted material is involved.
- The configured remote was removed during Phase 01 because its privacy could not be verified.
- Never stage `*.csv`, `*.zip`, `DataSet/**`, raw/interim/processed data, models, outputs, checker reports, logs, or secrets.
- Review `git status --ignored` and `git diff --cached --name-only` before every commit.
- Do not force-add ignored competition files without a documented organizer-approved exception.

## 4. Secrets policy

Never commit:

- `.env` or `.env.*`;
- API keys, access tokens, passwords, private keys, or credentials;
- personal absolute paths when avoidable;
- logs containing environment variables or restricted records.

Use `.env.example` only for non-secret variable names and placeholder values if a later phase needs it.

## 5. AI and coding-agent access

Cursor, Codex, and other coding agents must not be asked to inspect, summarize, upload, transmit, or embed official competition rows or private derivatives.

Permitted safe inputs include:

- documentation;
- schemas and column names;
- synthetic fixtures;
- local source code that does not contain restricted records;
- non-reconstructive diagnostics approved by the team.

If a tool workflow may transmit restricted data or its privacy is unclear, stop and seek organizer clarification. Do not assume that a private account or private third-party service is automatically permitted.

All AI-assisted work must be recorded in the final AI-tool disclosure.

## 6. Incident rule

If restricted data is accidentally staged, exposed, or transmitted:

1. Stop the affected work.
2. Do not continue to later phases.
3. Remove exposure only through an approved remediation.
4. Rotate any exposed secrets.
5. Record the issue, evidence, decision, and retest result.
