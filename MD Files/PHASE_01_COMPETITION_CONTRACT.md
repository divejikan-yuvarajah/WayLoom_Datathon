# PHASE 01 — Project Environment & Secure Repository Setup

> **Requested filename:** `PHASE_01_COMPETITION_CONTRACT.md`  
> **Canonical phase name in the master plan:** **Phase 01 — Project environment and repository setup**  
> **WayLoom Datathon — Rootcode Tech-Triathlon 2026**  
> **Tasks covered:** DT-011 → DT-022  
> **Default priority:** P0  
> **Execution style:** Full phase is safe, with a mandatory completion audit before Phase 02  
> **Phase dependency:** Phase 00 must have passed  
> **Phase gate:** A private, reproducible repository exists; restricted-data paths are protected; dependencies are installable; configuration, logging and reproducibility controls are ready.

---

## 1. Purpose of Phase 01

Phase 01 creates the technical foundation for the entire WayLoom Datathon.

No modelling, forecasting, allocation, EDA, label construction or competition-data inspection should happen in this phase.

The goal is to make later work:

- reproducible;
- private;
- safe for competition data;
- easy to run on another machine;
- easy to review;
- easy to test;
- organized enough for Task 1, Task 2A and Task 2B to remain separated;
- resistant to accidental raw-data commits or external exposure.

This phase implements engineering controls around the official competition obligations. The organizer does **not** explicitly require a Git repository, Python virtual environment, the exact folder structure below, YAML configuration, or a logging helper for the Datathon. Those are **WayLoom engineering decisions** used to execute the official Datathon safely and reproducibly.

The official rules that influence this phase are primarily:

1. competition datasets may be used only for the competition;
2. datasets must not be shared or distributed to third parties;
3. datasets and derivatives must not be published without authorization;
4. competition data must remain confidential;
5. the final Datathon submission must include saved model files and a reproducible final notebook;
6. AI-assisted work must be disclosed;
7. prohibited modelling/tooling restrictions must be respected later in development.

**Important:** Phase 01 must not weaken, reinterpret, or bypass any rule frozen in Phase 00.

---

# 2. Phase 01 task registry

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---|---|---|---|
| [x] | **DT-011** | [E] | P0 | Phase 00 | Create project root directory |
| [x] | **DT-012** | [E] | P0 | DT-011 | Initialize Git repository |
| [x] | **DT-013** | [E] | P0 | DT-011–DT-012 | Decide private repository policy |
| [x] | **DT-014** | [E] | P0 | DT-013 | Create `.gitignore` and local agent/data-safety exclusions |
| [x] | **DT-015** | [E] | P0 | DT-011 | Create Python virtual environment |
| [x] | **DT-016** | [E] | P0 | DT-015 | Install required libraries |
| [x] | **DT-017** | [E] | P0 | DT-016 | Create dependency files |
| [x] | **DT-018** | [E] | P0 | DT-019–DT-020 | Set random-seed policy |
| [x] | **DT-019** | [E] | P0 | DT-011 | Create repository folder structure |
| [x] | **DT-020** | [E] | P0 | DT-019 | Create project configuration |
| [x] | **DT-021** | [E] | P0 | DT-019–DT-020 | Create logging utility |
| [x] | **DT-022** | [E] | P0 | DT-015–DT-021 | Create reproducibility notes |

**Phase complete:** [x]  
**READY FOR PHASE 02:** YES

---

# 3. Authority and source rules

Use this source order throughout Phase 01:

1. Official Rootcode Tech-Triathlon 2026 Challenge Booklet.
2. Official competition artifacts/templates/checker.
3. Approved `WAYLOOM_DATATHON_MASTER_PLAN.md`.
4. Approved `PHASE_00_COMPETITION_CONTRACT.md`.
5. This Phase 01 implementation guide.
6. Repository code/comments/prompts.

If this file conflicts with an official rule, the official rule wins.

If this file conflicts with the approved master plan, stop and report the conflict rather than silently changing either document.

---

# 4. Inputs

Phase 01 may use these inputs:

- `WAYLOOM_DATATHON_MASTER_PLAN.md`
- approved Phase 00 outputs:
  - `docs/competition_contract.md`
  - `docs/competition_requirements_checklist.md`
  - `docs/internal_milestones.md`
- the official Challenge Booklet for rule verification only;
- the local Python interpreter;
- Git;
- local terminal/shell;
- package installer (`pip`);
- the planned repository structure.

Phase 01 does **not** require reading competition CSV contents.

The supplied competition ZIP may exist outside the repository, but it must not be extracted or analyzed until Phase 02.

---

# 5. Expected Phase 01 outputs

At minimum, Phase 01 should leave the project in a state similar to:

```text
WayLoom_Datathon/
│
├── README.md                         # minimal Phase 01 project stub
├── WAYLOOM_DATATHON_MASTER_PLAN.md
├── requirements.txt
├── requirements-lock.txt             # exact local environment snapshot
├── .gitignore
├── .cursorignore                     # if Cursor is used; protects restricted data paths
│
├── configs/
│   ├── paths.yaml
│   └── model_config.yaml
│
├── data/
│   ├── README.md
│   ├── raw/                          # PRIVATE / never commit
│   ├── interim/                      # PRIVATE derivatives / never commit
│   └── processed/                    # PRIVATE derivatives / never commit
│
├── docs/
│   ├── 00_MASTER_INDEX.md
│   ├── competition_contract.md
│   ├── competition_requirements_checklist.md
│   ├── internal_milestones.md
│   ├── repository_data_policy.md
│   ├── reproducibility.md
│   ├── architecture/
│   └── phases/
│       ├── PHASE_00_COMPETITION_CONTRACT.md
│       └── PHASE_01_COMPETITION_CONTRACT.md
│
├── notebooks/
│
├── src/
│   ├── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   └── logging_utils.py
│   ├── task1/
│   │   └── __init__.py
│   ├── task2a/
│   │   └── __init__.py
│   └── task2b/
│       └── __init__.py
│
├── models/
├── outputs/
├── reports/
│   ├── figures/
│   ├── metrics/
│   └── checker/
│
└── tests/
    └── test_project_setup.py
```

The exact folder names may be adjusted only if the master plan is updated deliberately. Do not create a second competing structure.

---

# 6. Files/folders that Phase 01 must not populate with competition data

These folders may be created, but Phase 01 must leave them empty of official competition records:

```text
data/raw/
data/interim/
data/processed/
models/
outputs/
```

Do not:

- extract `DataSet_New.zip`;
- copy official CSVs into the repository;
- inspect rows using Cursor/Codex;
- create processed derivatives;
- generate predictions;
- create final submission CSVs;
- commit any competition dataset.

Phase 02 owns dataset extraction and inventory.

---

# 7. Detailed implementation tasks

---

## DT-011 — Create project root directory

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** Phase 00 approved

### Objective

Create one clean root directory that will contain all WayLoom Datathon code, documentation, configuration and local working folders.

### Why it matters

A single stable root prevents:

- duplicated notebooks;
- files scattered across Downloads/Desktop;
- broken relative paths;
- accidental cross-use of Hackathon code;
- confusion over which copy is the final competition project.

### Inputs

- approved master plan;
- chosen local parent directory.

### Outputs

```text
WayLoom_Datathon/
```

### Detailed instructions

1. Choose a local parent directory with enough disk space.
2. Create exactly one main Datathon root.
3. Do not place the root inside a public/shared synchronized folder unless the organizer has explicitly allowed that workflow.
4. Keep Hackathon and Designathon implementation separate unless there is an intentional monorepo decision documented by the team.
5. Place/copy the approved master plan into the root.
6. Create no modelling artifacts yet.

### Example

macOS/Linux:

```bash
mkdir -p WayLoom_Datathon
cd WayLoom_Datathon
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Path WayLoom_Datathon
Set-Location WayLoom_Datathon
```

### Validation

- current working directory is the intended root;
- only one active Datathon repository is being used;
- master plan is present or has a documented source location.

### Edge cases

- **Existing folder already exists:** inspect before overwriting anything.
- **Existing Git repository:** do not initialize nested Git accidentally.
- **Cloud-synced path:** stop and confirm it does not violate competition data-sharing constraints before placing restricted data there later.

### Tests

```bash
pwd
```

or PowerShell:

```powershell
Get-Location
```

### Definition of Done

- [ ] one approved Datathon root exists;
- [ ] no duplicate working root is active;
- [ ] root path is documented;
- [ ] no competition data has been copied into it.

### STOP conditions

Stop if:

- the only intended location is externally shared/public;
- an unrelated repository already occupies the root;
- there is uncertainty about which directory is authoritative.

---

## DT-012 — Initialize Git repository

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-011

### Objective

Initialize version control without exposing restricted competition data.

### Why it matters

Git enables:

- auditable changes;
- safe rollback;
- phase branches;
- clear documentation history;
- reliable collaboration.

### Inputs

- project root from DT-011.

### Outputs

```text
.git/
```

### Detailed instructions

1. Run `git status` first to check whether the root is already inside a repository.
2. If not, initialize Git.
3. Use `main` as the default branch unless the team already has another approved convention.
4. Do not add files until `.gitignore` is created and reviewed.
5. If a remote is used, it must follow the private repository policy in DT-013.
6. Do not create a public remote.

### Commands

```bash
git status
git init
git branch -M main
```

If `git status` says the folder is already inside another repository, stop and investigate.

### Validation

```bash
git rev-parse --show-toplevel
git branch --show-current
```

Expected:

```text
<WayLoom_Datathon root>
main
```

### Edge cases

- nested repository;
- repository inherited from Hackathon;
- public remote already attached;
- credentials belonging to a different account.

### Tests

```bash
git remote -v
git status
```

### Definition of Done

- [ ] Git root equals Datathon root;
- [ ] active branch is `main`;
- [ ] no public remote is attached;
- [ ] no restricted data is staged.

### STOP conditions

Stop immediately if:

- the project is nested inside another Git repository unexpectedly;
- an existing remote is public;
- competition data is already tracked.

---

## DT-013 — Decide private repository policy

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-011–DT-012

### Objective

Document exactly what may and may not enter Git or external developer tools.

### Why it matters

The competition restricts sharing, distributing and publishing supplied datasets and derivatives. A private-data policy must exist before any dataset is handled.

### Inputs

- Phase 00 competition restrictions;
- repository state.

### Outputs

Create:

```text
docs/repository_data_policy.md
```

### Required policy content

At minimum:

#### Allowed in Git

- source code;
- unit tests using synthetic fixtures;
- documentation that does not expose restricted records;
- configuration without secrets;
- diagrams;
- model-training code;
- safe aggregate/illustrative values when permitted and not reconstructive of restricted data;
- final competition artifacts only in locations permitted by the organizer/team policy.

#### Never commit

- raw official competition CSVs;
- extracted private datasets;
- private intermediate row-level datasets;
- raw derivatives that could redistribute competition data;
- local secrets;
- `.env`;
- API keys;
- cached notebook outputs containing sensitive/private rows;
- temporary exports;
- logs containing full private records.

#### AI/coding-agent rule

Cursor/Codex/other coding agents must not be instructed to inspect, upload, transmit, summarize or embed official competition rows unless the workflow has been explicitly confirmed as competition-compliant.

Use:

- schemas;
- column names;
- synthetic fixtures;
- local code;
- aggregate diagnostics that do not disclose restricted records.

### Recommended repository rule

Use a **private repository** if a remote repository is required.

If there is any doubt whether a private third-party Git hosting service counts as prohibited data sharing for competition data, do not place the dataset there. The safest approach is to keep datasets local and ignored even if code is hosted privately.

### Validation

Review the policy against Phase 00 restrictions.

### Tests

Search policy text for explicit protection of:

```text
data/raw
data/interim
data/processed
*.csv
*.zip
.env
API keys
third-party AI tools
```

### Definition of Done

- [ ] data policy exists;
- [ ] raw data is explicitly forbidden from Git;
- [ ] derivatives are addressed;
- [ ] agent-access rules are documented;
- [ ] public repository use is prohibited for restricted records;
- [ ] ambiguity requires organizer clarification rather than assumption.

### STOP conditions

Stop if the team intends to:

- upload raw data to a public repository;
- paste private rows into external AI tools;
- publish derivatives;
- use an ambiguous external data service without clarification.

---

## DT-014 — Create `.gitignore` and local agent/data-safety exclusions

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-013

### Objective

Add machine-enforced safeguards against accidentally staging or exposing private data and local development artifacts.

### Outputs

Required:

```text
.gitignore
```

Recommended when Cursor is used:

```text
.cursorignore
```

### Minimum `.gitignore`

```gitignore
# Python
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Jupyter
.ipynb_checkpoints/

# Local environment / secrets
.env
.env.*
!.env.example

# IDE / OS
.DS_Store
Thumbs.db
.vscode/
.idea/

# Competition data - NEVER COMMIT
data/raw/**
data/interim/**
data/processed/**
!data/raw/.gitkeep
!data/interim/.gitkeep
!data/processed/.gitkeep

# Competition dataset archives/files
DataSet_New.zip
*.zip
*.csv

# Local model/output artifacts during development
models/**
outputs/**
reports/checker/**
!models/.gitkeep
!outputs/.gitkeep
!reports/checker/.gitkeep

# Local logs
logs/
*.log

# Temporary files
tmp/
temp/
```

### Important nuance

A global `*.csv` ignore is deliberately conservative because official submission CSVs are private competition artifacts too. If later the team intentionally needs a specific CSV in the final submission package, Phase 40–42 can package it outside Git or explicitly force-add it after a documented review.

Do not weaken this rule casually.

### Recommended `.cursorignore`

```text
data/raw/**
data/interim/**
data/processed/**
models/**
outputs/**
DataSet_New.zip
*.csv
*.zip
.env
.env.*
```

The purpose is defense-in-depth. It is not a substitute for the human rule that coding agents must not inspect restricted competition data.

### Validation

Before any commit:

```bash
git status --ignored
git check-ignore -v data/raw/example.csv
git check-ignore -v DataSet_New.zip
```

Use dummy filenames only. Do not create real competition records for testing.

### Synthetic safety test

Create a temporary empty file:

```bash
touch data/raw/DO_NOT_COMMIT.csv
git check-ignore -v data/raw/DO_NOT_COMMIT.csv
rm data/raw/DO_NOT_COMMIT.csv
```

PowerShell:

```powershell
New-Item data/raw/DO_NOT_COMMIT.csv -ItemType File
git check-ignore -v data/raw/DO_NOT_COMMIT.csv
Remove-Item data/raw/DO_NOT_COMMIT.csv
```

### Definition of Done

- [ ] `.gitignore` exists;
- [ ] restricted paths are ignored;
- [ ] archives/CSV data are ignored;
- [ ] environment/secrets are ignored;
- [ ] Cursor exclusions exist if Cursor is used;
- [ ] dummy safety checks pass.

### STOP conditions

Do not continue if:

- `data/raw/*.csv` is not ignored;
- dataset ZIP is not ignored;
- `.env` is trackable;
- actual private files are already tracked by Git.

If private data is already tracked, do not simply add `.gitignore`; remove it from Git tracking/history using an approved remediation before proceeding.

---

## DT-015 — Create Python virtual environment

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-011

### Objective

Create an isolated Python environment for Datathon dependencies.

### Recommended Python

Prefer a stable Python 3.x version supported by the selected data-science libraries. Record the exact interpreter version actually used rather than inventing a version requirement.

### Commands

```bash
python --version
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then verify:

```bash
python -c "import sys; print(sys.executable); print(sys.version)"
```

### Outputs

```text
.venv/     # local only, ignored by Git
```

### Edge cases

- multiple installed Python versions;
- `python` points to Python 2 or unexpected interpreter;
- activation blocked by PowerShell policy;
- virtual environment created outside project accidentally.

### Tests

Inside activated environment:

```bash
python -c "import sys; assert '.venv' in sys.executable or 'venv' in sys.prefix.lower(); print(sys.executable)"
```

### Definition of Done

- [ ] `.venv` exists locally;
- [ ] activated interpreter belongs to it;
- [ ] Python version recorded;
- [ ] `.venv` is ignored by Git.

### STOP conditions

Stop if:

- environment uses the wrong Python interpreter;
- environment cannot be activated;
- package installation would occur globally unintentionally.

---

## DT-016 — Install required libraries

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-015

### Objective

Install the minimal practical toolset needed by the finalized Datathon plan.

### Core libraries

```text
pandas
numpy
scikit-learn
catboost
lightgbm
matplotlib
plotly
shap
joblib
jupyterlab
pytest
ortools
pyyaml
```

Optional libraries must not be installed simply because they are popular.

Do not install:

- deep-learning frameworks unless later justified;
- MLflow/W&B by default;
- cloud SDKs by default;
- proprietary modelling APIs;
- automatic end-to-end AutoML tools;
- unnecessary database clients.

### Installation

First upgrade packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Install direct dependencies:

```bash
python -m pip install pandas numpy scikit-learn catboost lightgbm matplotlib plotly shap joblib jupyterlab pytest ortools pyyaml
```

### Smoke-test imports

```bash
python - <<'PY'
import pandas
import numpy
import sklearn
import catboost
import lightgbm
import matplotlib
import plotly
import shap
import joblib
import pytest
import ortools
import yaml
print("core imports: PASS")
PY
```

On Windows PowerShell, use a short temporary Python file or `python -c` imports.

### Edge cases

- LightGBM native dependency failure;
- SHAP compatibility warning;
- package resolver conflict;
- OR-Tools version conflict;
- package installation accidentally targets global Python.

### Validation

```bash
python -m pip check
```

Expected:

```text
No broken requirements found.
```

### Definition of Done

- [ ] all core imports work;
- [ ] `pip check` passes;
- [ ] no prohibited modelling tool was installed as part of this phase;
- [ ] installation occurs inside `.venv`.

### STOP conditions

Stop if:

- dependency conflicts remain unresolved;
- core packages import from outside the virtual environment;
- package installation requires uploading competition data;
- a proposed library conflicts with official competition restrictions.

---

## DT-017 — Create dependency files

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-016

### Objective

Make the environment reproducible without losing clarity about direct versus transitive dependencies.

### Outputs

Recommended:

```text
requirements.txt
requirements-lock.txt
```

### `requirements.txt`

Keep this as the human-readable set of direct project dependencies:

```text
pandas
numpy
scikit-learn
catboost
lightgbm
matplotlib
plotly
shap
joblib
jupyterlab
pytest
ortools
pyyaml
```

Do not invent version pins before testing them.

### `requirements-lock.txt`

After successful installation:

```bash
python -m pip freeze > requirements-lock.txt
```

This captures the exact working environment.

### Reproduction test

Create a temporary test environment only if practical:

```bash
python -m venv .venv_repro
```

Install:

```bash
python -m pip install -r requirements-lock.txt
```

Then smoke-test imports.

Delete `.venv_repro` after test.

If this is too time-consuming during Phase 01, at minimum run the full clean reproduction in Phase 39. Record that deferred verification explicitly.

### Definition of Done

- [ ] direct requirements file exists;
- [ ] exact lock snapshot exists;
- [ ] both are plain text;
- [ ] no secrets or local paths appear;
- [ ] package list matches actual intended stack.

### STOP conditions

Stop if:

- requirements contain credentials;
- editable/local machine-specific paths appear in the lock unexpectedly;
- core packages are absent;
- prohibited tools are included.

---

## DT-018 — Set random-seed policy

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-019–DT-020

### Objective

Define one default seed policy so later experiments are reproducible where supported.

### Important principle

A random seed improves reproducibility but does **not** guarantee bit-for-bit identical results across:

- different library versions;
- different hardware;
- multi-threaded algorithms;
- non-deterministic solver implementations.

Do not claim stronger reproducibility than the tooling supports.

### Output

Record in:

```text
configs/model_config.yaml
docs/reproducibility.md
```

Recommended:

```yaml
random_seed: 42
```

Later training scripts should read the value from configuration where practical.

### Rules

1. Use one default project seed: `42`.
2. If an experiment intentionally changes seed, record it in experiment notes.
3. Pass `random_state` / equivalent to supported scikit-learn models.
4. Pass seed parameters to CatBoost/LightGBM where supported.
5. Record OR-Tools solver seed only if later used and relevant.
6. Do not use seed to conceal unstable validation.

### Test

Load configuration and assert:

```text
random_seed == 42
```

### Definition of Done

- [ ] seed is defined once in configuration;
- [ ] reproducibility notes explain its limitations;
- [ ] later code has a clear source for the seed.

### STOP conditions

Stop if multiple conflicting default seeds are introduced.

---

## DT-019 — Create repository folder structure

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-011

### Objective

Create the stable project skeleton defined in the master plan without populating data/model/output folders.

### Required directories

```text
configs/
data/raw/
data/interim/
data/processed/
docs/architecture/
docs/phases/
notebooks/
src/common/
src/task1/
src/task2a/
src/task2b/
models/
outputs/
reports/figures/
reports/metrics/
reports/checker/
tests/
```

### Minimal package markers

Create:

```text
src/__init__.py
src/common/__init__.py
src/task1/__init__.py
src/task2a/__init__.py
src/task2b/__init__.py
```

### Keep empty private directories

Because ignored directories are not tracked by Git, use `.gitkeep` only where needed:

```text
data/raw/.gitkeep
data/interim/.gitkeep
data/processed/.gitkeep
models/.gitkeep
outputs/.gitkeep
reports/checker/.gitkeep
```

The `.gitignore` must explicitly allow only these placeholders.

### `data/README.md`

Create a short safety document:

```markdown
# Local competition data

Official competition datasets and private derivatives belong only in the ignored local subdirectories below.

- raw/
- interim/
- processed/

Never commit or publish competition data from these folders.
Do not expose raw rows to external coding/model services.
```

### Minimal root `README.md`

Only a stub is needed now. Final README work belongs to Phase 36.

Include:

- project name;
- competition;
- Datathon scope;
- pointer to master plan;
- data-safety warning;
- setup pointer.

### Tests

Verify directories:

```bash
python - <<'PY'
from pathlib import Path
required = [
    "configs",
    "data/raw",
    "data/interim",
    "data/processed",
    "docs/architecture",
    "docs/phases",
    "notebooks",
    "src/common",
    "src/task1",
    "src/task2a",
    "src/task2b",
    "models",
    "outputs",
    "reports/figures",
    "reports/metrics",
    "reports/checker",
    "tests",
]
missing = [p for p in required if not Path(p).exists()]
assert not missing, f"Missing directories: {missing}"
print("repository structure: PASS")
PY
```

### Definition of Done

- [ ] full skeleton exists;
- [ ] Task 1/2A/2B code areas are separate;
- [ ] data folders contain no competition data yet;
- [ ] Python package markers exist;
- [ ] root/data README safety notes exist.

### STOP conditions

Stop if:

- raw data is copied as part of folder setup;
- duplicate competing folder layouts are introduced;
- Task 1/2A/2B logic is mixed into one generic module prematurely.

---

## DT-020 — Create project configuration

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-019

### Objective

Centralize paths and model-level defaults instead of hard-coding them throughout notebooks.

### Outputs

```text
configs/paths.yaml
configs/model_config.yaml
```

### Recommended `configs/paths.yaml`

```yaml
project_root: "."
data:
  raw: "data/raw"
  interim: "data/interim"
  processed: "data/processed"
models: "models"
outputs: "outputs"
reports:
  root: "reports"
  figures: "reports/figures"
  metrics: "reports/metrics"
  checker: "reports/checker"
```

Do not put absolute machine-specific paths here unless there is a documented local override strategy.

### Recommended `configs/model_config.yaml`

```yaml
project:
  random_seed: 42

task1:
  enabled: true

task2a:
  enabled: true

task2b:
  enabled: true
```

Do not add hyperparameters yet. Those are decided in modelling phases.

### Optional configuration loader

A lightweight loader may be added later. Phase 01 does not need a complex configuration framework.

If a loader is created now, keep it minimal and covered by tests.

### Validation

- paths are relative;
- no secret appears;
- no raw data filename is hardcoded prematurely;
- YAML parses successfully.

### Test

```bash
python - <<'PY'
from pathlib import Path
import yaml

for p in ["configs/paths.yaml", "configs/model_config.yaml"]:
    with open(p, "r", encoding="utf-8") as f:
        obj = yaml.safe_load(f)
    assert isinstance(obj, dict), p
print("configuration parse: PASS")
PY
```

### Definition of Done

- [ ] both YAML files exist;
- [ ] YAML parses;
- [ ] paths are portable;
- [ ] random seed is centralized;
- [ ] no modelling hyperparameters are invented yet;
- [ ] no credentials exist.

### STOP conditions

Stop if:

- absolute user-specific paths are committed without a portability plan;
- secrets/API keys are introduced;
- configuration embeds private data rows.

---

## DT-021 — Create logging utility

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-019–DT-020

### Objective

Create a small reusable logging helper that later pipelines can use without exposing private row-level data.

### Output

```text
src/common/logging_utils.py
```

### Logging principles

1. Log pipeline stage, counts, durations and validation summaries.
2. Do not log full competition rows.
3. Do not log API keys or environment variables.
4. Do not log raw model inputs containing private records by default.
5. Default to console logging.
6. File logging, if later used, must write to ignored local logs.

### Recommended implementation shape

```python
import logging


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    logger.propagate = False
    return logger
```

Avoid heavy logging frameworks.

### Test

Create or extend:

```text
tests/test_project_setup.py
```

Example expectations:

- logger can be constructed;
- repeated calls do not duplicate handlers;
- log level can be set.

Do not test using private dataset rows.

### Definition of Done

- [ ] reusable logger exists;
- [ ] duplicate handlers are prevented;
- [ ] logger does not expose private data by design;
- [ ] basic test passes.

### STOP conditions

Stop if logging automatically serializes DataFrames/records or sends logs to an external service.

---

## DT-022 — Create reproducibility notes

**Mark:** [E] Engineering  
**Priority:** P0  
**Dependency:** DT-015–DT-021

### Objective

Document exactly how another team member can recreate the development environment without receiving restricted data through Git.

### Output

```text
docs/reproducibility.md
```

### Required sections

#### 1. System information

Record:

```text
Operating system:
Python version:
pip version:
Git version:
Date environment created:
```

#### 2. Environment setup

```bash
python -m venv .venv
```

Activation commands for Windows/macOS/Linux.

#### 3. Install dependencies

Primary clean-reproduction command:

```bash
python -m pip install -r requirements-lock.txt
```

#### 4. Verify environment

```bash
python -m pip check
pytest -q tests/test_project_setup.py
```

#### 5. Random seed

```text
Default seed: 42
```

Explain deterministic limitations.

#### 6. Data placement

Explain that official data is obtained through the organizer-approved source and placed locally under ignored directories only.

Do not include the data itself.

#### 7. Data-safety restrictions

Reiterate:

- no Git commit;
- no public sharing;
- no raw-row logging;
- no external agent access unless explicitly permitted;
- no private data inside screenshots/docs.

#### 8. Phase execution

Phase 02 is the first phase allowed to extract/inventory competition files.

#### 9. Known platform-specific issues

Record any library installation differences.

### Validation

A teammate should be able to read the document and understand how to create the environment without asking where data should be committed.

### Definition of Done

- [ ] reproducibility document exists;
- [ ] exact Python/tool versions actually used are recorded;
- [ ] dependency install command exists;
- [ ] random seed policy exists;
- [ ] local-data handling is explicit;
- [ ] Phase 02 boundary is explicit.

### STOP conditions

Do not approve Phase 01 if reproduction instructions require:

- access to a developer's absolute personal path;
- committed competition data;
- undocumented package installation;
- undocumented secrets.

---

# 8. Phase-level automated setup test

Create:

```text
tests/test_project_setup.py
```

Recommended checks:

```python
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRS = [
    "configs",
    "data/raw",
    "data/interim",
    "data/processed",
    "docs",
    "notebooks",
    "src/common",
    "src/task1",
    "src/task2a",
    "src/task2b",
    "models",
    "outputs",
    "reports/figures",
    "reports/metrics",
    "reports/checker",
    "tests",
]


def test_required_directories_exist():
    missing = [p for p in REQUIRED_DIRS if not (ROOT / p).exists()]
    assert not missing, f"Missing directories: {missing}"


def test_configs_parse():
    for rel in ["configs/paths.yaml", "configs/model_config.yaml"]:
        with open(ROOT / rel, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        assert isinstance(cfg, dict)


def test_random_seed_is_frozen():
    with open(ROOT / "configs/model_config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg["project"]["random_seed"] == 42
```

Do not make tests depend on raw competition files in Phase 01.

---

# 9. Phase 01 integration validation

Run these checks after DT-011–DT-022.

## Environment

```bash
python --version
python -m pip --version
python -m pip check
```

## Git

```bash
git rev-parse --show-toplevel
git branch --show-current
git remote -v
git status
```

## Ignore rules

Using dummy files only:

```bash
git check-ignore -v data/raw/DO_NOT_COMMIT.csv
git check-ignore -v DataSet_New.zip
git check-ignore -v .env
```

## Config

```bash
python - <<'PY'
import yaml
for path in ["configs/paths.yaml", "configs/model_config.yaml"]:
    with open(path, encoding="utf-8") as f:
        assert isinstance(yaml.safe_load(f), dict)
print("config validation: PASS")
PY
```

## Tests

```bash
pytest -q tests/test_project_setup.py
```

## Restricted-data boundary

Verify:

```text
data/raw/        contains no official records yet
data/interim/    contains no derivatives
data/processed/  contains no derivatives
models/          contains no models
outputs/         contains no submission files
```

---

# 10. Phase 01 edge cases

## Existing repository

If the repository already exists:

- do not reinitialize blindly;
- verify root;
- verify remote privacy;
- verify ignore rules;
- update safely.

## Existing virtual environment

If `.venv` already exists:

- verify interpreter;
- run `pip check`;
- compare dependency snapshot;
- do not delete a working environment unless necessary.

## Existing raw data accidentally inside root

Do not ask Cursor/Codex to inspect it.

First:

- confirm it is ignored;
- move it to the intended local ignored path if safe;
- verify it was never committed;
- if committed, treat as a data-security incident and remediate before proceeding.

## Existing public remote

Do not push.

Stop and change repository strategy before any competition work.

## Existing notebook outputs with private rows

Remove/clear them before tracking notebooks later.

## Package failure

Do not substitute random alternative libraries without documenting why.

## Windows path differences

Use `pathlib` and relative project paths later; do not hardcode backslash-heavy absolute paths into committed config.

---

# 11. Global Phase 01 STOP CONDITIONS

Phase 01 must end with `READY FOR PHASE 02 = NO` if any of the following remains true:

- Phase 00 is not approved.
- Git root is incorrect.
- a public remote is attached without an approved safety decision.
- raw competition data is tracked by Git.
- raw data or derivatives are accessible to coding agents contrary to the agreed policy.
- `.gitignore` does not block restricted data paths.
- `.env` or secrets can be tracked.
- virtual environment is not isolated.
- required core libraries fail import.
- `pip check` fails.
- requirements/lock files are incomplete.
- repository structure is incomplete.
- configuration files do not parse.
- multiple default random seeds exist.
- logging transmits data externally.
- reproducibility notes are incomplete.
- Phase 02 dataset work has already been mixed into Phase 01.
- an unresolved official/internal rule conflict exists.

Do not "work around" a STOP condition by proceeding to data extraction.

---

# 12. Phase 01 Definition of Done

Phase 01 is complete only when:

- [ ] DT-011 PASS
- [ ] DT-012 PASS
- [ ] DT-013 PASS
- [ ] DT-014 PASS
- [ ] DT-015 PASS
- [ ] DT-016 PASS
- [ ] DT-017 PASS
- [ ] DT-018 PASS
- [ ] DT-019 PASS
- [ ] DT-020 PASS
- [ ] DT-021 PASS
- [ ] DT-022 PASS
- [ ] Git root is correct
- [ ] repository is private/local according to policy
- [ ] no raw official data is tracked
- [ ] ignore-rule safety test passes
- [ ] `.venv` works
- [ ] all required packages import
- [ ] `pip check` passes
- [ ] requirements files exist
- [ ] seed policy is frozen
- [ ] project skeleton exists
- [ ] config YAML parses
- [ ] logger test passes
- [ ] `pytest -q tests/test_project_setup.py` passes
- [ ] reproducibility notes exist
- [ ] no Phase 02 work has been performed
- [ ] completion audit passes

Then:

```text
PHASE 01 STATUS: PASS
READY FOR PHASE 02: YES
```

---

# 13. Git workflow for Phase 01

Phase 01 is the first phase that initializes Git.

## Before first commit

Complete DT-013 and DT-014 first.

Do **not** commit before private-data ignore rules are active.

Recommended sequence:

```bash
git init
git branch -M main

# create/review .gitignore first
git status --ignored
```

Recommended development branch after the initial safety setup:

```bash
git checkout -b chore/phase-01-project-environment
```

### Suggested commits

```text
chore(repo): initialize secure datathon repository
chore(env): add Python environment dependencies
chore(config): add project paths and seed policy
feat(common): add safe logging utility
docs(repro): document environment reproduction and data policy
test(setup): add project setup validation
```

### Before merge

Run:

```bash
python -m pip check
pytest -q tests/test_project_setup.py
git status
git diff --cached --name-only
```

Check manually that no restricted extension/path has been staged.

Then merge only after Phase 01 review says PASS.

---

# 14. Recommended execution grouping

Phase 01 is safe to execute as one full phase because it contains setup work rather than model/data logic.

If you prefer checkpoints, use these batches:

```text
Batch A
DT-011–DT-014
Root + Git + data-safety policy + ignore rules
STOP → security review

Batch B
DT-015–DT-017
Virtual environment + dependencies
STOP → import / pip-check review

Batch C
DT-019–DT-021
Repository structure + config + logging
STOP → pytest review

Batch D
DT-018 + DT-022
Seed policy + reproducibility documentation
STOP → Phase 01 audit
```

DT-018 appears after DT-020 because the seed should live in approved configuration.

---

# 15. Full-phase Cursor implementation prompt

```text
You are implementing WayLoom Datathon Phase 01 — Project Environment & Secure Repository Setup.

READ FIRST:
1. WAYLOOM_DATATHON_MASTER_PLAN.md
2. approved PHASE_00_COMPETITION_CONTRACT.md and its outputs
3. PHASE_01_COMPETITION_CONTRACT.md
4. official competition restrictions if needed for verification

SCOPE:
Implement ONLY DT-011 through DT-022.

Do not begin Phase 02.

PHASE 01 IS INFRASTRUCTURE/SETUP ONLY.

Do not:
- extract DataSet_New.zip
- inspect official CSV rows
- perform EDA
- build Task 1 labels
- build features
- train models
- forecast demand
- implement Task 2B optimization
- generate submission CSVs
- expose competition records to Cursor or another external service

OFFICIAL SAFETY CONTEXT:
The competition data is restricted and must not be shared, distributed or publicly exposed.
Treat raw competition data and private derivatives as local-only restricted material.

IMPLEMENT IN ORDER:

DT-011 Create project root directory.
DT-012 Initialize Git repository.
DT-013 Create and document private repository/data policy.
DT-014 Create .gitignore and, because Cursor is being used, .cursorignore safety exclusions.
DT-015 Create .venv.
DT-016 Install the approved core Python libraries.
DT-017 Create requirements.txt and requirements-lock.txt.
DT-019 Create the repository folder structure.
DT-020 Create configs/paths.yaml and configs/model_config.yaml.
DT-018 Freeze random_seed = 42 in configuration and reproducibility policy.
DT-021 Create src/common/logging_utils.py with safe local console logging.
DT-022 Create docs/reproducibility.md.

CREATE/VERIFY:
- README.md minimal stub
- .gitignore
- .cursorignore
- requirements.txt
- requirements-lock.txt
- configs/paths.yaml
- configs/model_config.yaml
- data/README.md
- docs/repository_data_policy.md
- docs/reproducibility.md
- src/common/logging_utils.py
- tests/test_project_setup.py
- required repository directories and __init__.py files

IMPORTANT:
Do not commit any official CSV, ZIP, private derivative, model artifact or submission output.
The data directories may be created but must remain empty except .gitkeep / safety documentation.

Use relative project paths.
Do not hardcode local absolute paths.
Do not add secrets.
Do not install unnecessary cloud/AutoML/experiment-tracking services.

DEPENDENCY STACK:
pandas
numpy
scikit-learn
catboost
lightgbm
matplotlib
plotly
shap
joblib
jupyterlab
pytest
ortools
pyyaml

If an approved working environment already exists, inspect it instead of destroying it.

VALIDATE:
- correct Git root
- main branch exists
- no unsafe public remote
- data/raw is ignored
- data/interim is ignored
- data/processed is ignored
- DataSet_New.zip is ignored
- *.csv is ignored
- .env is ignored
- Cursor excludes restricted paths
- .venv interpreter works
- core imports pass
- python -m pip check passes
- requirements files exist
- required directory skeleton exists
- config YAML parses
- random_seed == 42
- logging utility tests pass
- pytest -q tests/test_project_setup.py passes
- no official data was extracted/read
- no Phase 02 task was performed

If any STOP CONDITION in the Phase 01 MD occurs:
STOP immediately.
Do not continue by guessing.

AT COMPLETION RETURN ONLY:

PHASE: 01

TASK STATUS:
DT-011 PASS/FAIL
DT-012 PASS/FAIL
DT-013 PASS/FAIL
DT-014 PASS/FAIL
DT-015 PASS/FAIL
DT-016 PASS/FAIL
DT-017 PASS/FAIL
DT-018 PASS/FAIL
DT-019 PASS/FAIL
DT-020 PASS/FAIL
DT-021 PASS/FAIL
DT-022 PASS/FAIL

FILES CREATED:
...

FILES MODIFIED:
...

ENVIRONMENT:
Python:
pip:
Dependency check:

GIT SAFETY:
Git root:
Branch:
Remote status:
Restricted-data ignore test:

TESTS:
...

STOP CONDITIONS:
...

OPEN ISSUES:
...

PHASE 01 STATUS:
PASS / FAIL

READY FOR PHASE 02:
YES / NO

Then STOP.
Do not implement Phase 02.
```

---

# 16. Full-phase Codex implementation prompt

```text
Work inside the WayLoom Datathon project.

TASK:
Implement Phase 01 only — Project Environment & Secure Repository Setup.

AUTHORITATIVE SOURCES:
1. official competition rules
2. WAYLOOM_DATATHON_MASTER_PLAN.md
3. approved Phase 00 outputs
4. PHASE_01_COMPETITION_CONTRACT.md

TASK RANGE:
DT-011 through DT-022.

Do not work beyond this range.

FIRST:
Inspect the current project directory without opening restricted competition datasets.

If files already exist:
- preserve valid work
- do not overwrite blindly
- report conflicts
- modify only what is necessary for Phase 01

DATA SAFETY:
Official competition CSVs, ZIPs and derivatives are restricted.
Do not open or inspect their contents during Phase 01.
Do not transmit them.
Do not stage them in Git.
Do not embed their rows in tests, docs or logs.

IMPLEMENT:

DT-011:
Establish one authoritative WayLoom_Datathon project root.

DT-012:
Initialize/verify Git and main branch.
Ensure there is no unexpected nested repository.

DT-013:
Create docs/repository_data_policy.md.
Define raw data, derivative, Git, AI-agent and secret handling rules.

DT-014:
Create/verify .gitignore.
Protect data/raw, data/interim, data/processed, CSV/ZIP files, .env, virtual environments, caches, model/output development artifacts.
Create .cursorignore because this repository is being developed with Cursor.
Do not rely on ignore files alone as permission to expose restricted data.

DT-015:
Create/verify .venv using the intended local Python interpreter.

DT-016:
Install only the approved direct dependencies:
pandas numpy scikit-learn catboost lightgbm matplotlib plotly shap joblib jupyterlab pytest ortools pyyaml

Run import smoke tests and pip check.

DT-017:
Create requirements.txt with direct dependencies.
Create requirements-lock.txt using the resolved working environment.
Do not include secrets or machine-specific editable paths.

DT-019:
Create the repository structure defined by the master plan.
Create empty private data directories only.
Add package __init__.py files.
Create data/README.md and minimal root README.md.

DT-020:
Create configs/paths.yaml and configs/model_config.yaml.
Use relative paths only.
Do not add Task 1/2A/2B hyperparameters yet.

DT-018:
Freeze project random_seed = 42 in model_config and document its limitations.

DT-021:
Create src/common/logging_utils.py.
Use local console logging.
Avoid duplicate handlers.
Never automatically log full DataFrames/private records.
Do not use cloud logging.

DT-022:
Create docs/reproducibility.md with:
- actual OS/Python/pip/Git versions
- venv setup
- dependency install
- seed policy
- test commands
- local-only data placement
- data confidentiality reminder
- Phase 02 boundary

CREATE:
tests/test_project_setup.py

The test must validate:
- required directories
- YAML parsing
- random_seed = 42
- safe logging helper behavior

DO NOT:
- extract DataSet_New.zip
- inspect CSV rows
- write data ingestion
- perform EDA
- construct labels
- implement models
- implement forecasting
- implement allocation
- generate submissions
- build APIs
- start Phase 02

RUN BEFORE FINISHING:

python -m pip check
pytest -q tests/test_project_setup.py
git status
git remote -v
git check-ignore -v data/raw/DO_NOT_COMMIT.csv
git check-ignore -v DataSet_New.zip
git check-ignore -v .env

Use dummy empty files for ignore tests only.

PHASE GATE:
Every DT-011..DT-022 item must pass.
No restricted dataset may be tracked/read.
No STOP CONDITION may remain unresolved.

When finished, give a concise report:

PHASE: 01

TASK STATUS:
DT-011 ... DT-022 PASS/FAIL

FILES CREATED:
...

FILES MODIFIED:
...

VALIDATION:
...

GIT/DATA SAFETY:
...

ISSUES:
...

PHASE 01:
PASS / FAIL

READY FOR PHASE 02:
YES / NO

Do not begin Phase 02.
STOP.
```

---

# 17. Independent Phase 01 review prompt

Use this in a fresh Cursor/Codex chat after implementation.

```text
Audit the completed WayLoom Datathon Phase 01.

DO NOT implement new functionality first.
DO NOT begin Phase 02.
DO NOT inspect competition CSV contents.

READ:
- WAYLOOM_DATATHON_MASTER_PLAN.md
- PHASE_01_COMPETITION_CONTRACT.md
- repository tree
- Phase 01 files only

Audit DT-011 through DT-022.

CHECK:

1. Repository root is correct.
2. No accidental nested Git repository exists.
3. Main branch exists.
4. Remote is absent/private and does not create an obvious data-exposure risk.
5. docs/repository_data_policy.md exists and protects raw data, derivatives, secrets and AI-agent access.
6. .gitignore protects:
   - data/raw
   - data/interim
   - data/processed
   - CSV/ZIP data
   - .env
   - .venv
   - logs/caches
7. .cursorignore protects restricted data paths if Cursor is being used.
8. Dummy git check-ignore tests pass.
9. .venv uses intended Python.
10. approved dependencies import.
11. pip check passes.
12. requirements.txt exists.
13. requirements-lock.txt exists and has no secret/local editable path issue.
14. repository directory structure matches the master plan.
15. data folders do not contain official competition data yet.
16. configs/paths.yaml uses portable relative paths.
17. configs/model_config.yaml parses.
18. random_seed is exactly 42.
19. no premature model hyperparameters were invented.
20. logging_utils.py does not transmit externally or dump private DataFrames.
21. logging tests pass.
22. docs/reproducibility.md contains actual environment versions and setup instructions.
23. tests/test_project_setup.py passes.
24. no Phase 02 work has been done.
25. no official competition rule has been silently changed.

RUN:
python -m pip check
pytest -q tests/test_project_setup.py
git status
git remote -v

Use safe/dummy ignore checks only.

REPORT AS:

| Task | Requirement | PASS/FAIL | Evidence | Required fix |

Then:

CRITICAL ISSUES:
...

DATA-SAFETY ISSUES:
...

NON-BLOCKING IMPROVEMENTS:
...

DT-011 STATUS: PASS/FAIL
...
DT-022 STATUS: PASS/FAIL

PHASE 01 REVIEW:
PASS / FAIL

READY FOR PHASE 02:
YES / NO

If FAIL:
list the exact blockers only.

Do not fix them until I explicitly approve.
Do not begin Phase 02.
```

---

# 18. Phase 01 completion report template

```markdown
# Phase 01 Completion Report

## Phase
Project Environment & Secure Repository Setup

## Tasks

- [x] DT-011
- [x] DT-012
- [x] DT-013
- [x] DT-014
- [x] DT-015
- [x] DT-016
- [x] DT-017
- [x] DT-018
- [x] DT-019
- [x] DT-020
- [x] DT-021
- [x] DT-022

## Environment

- OS: Windows 10, build 26100
- Python: 3.13.7
- pip: 26.2.1
- Git: 2.47.1.windows.2
- Virtual environment: `.venv` verified and used
- Dependency check: `No broken requirements found.`

## Git/Data Safety

- Git root verified: YES
- Public remote present: NO; no remote is configured
- data/raw ignored: YES
- data/interim ignored: YES
- data/processed ignored: YES
- CSV/ZIP ignored: YES
- .env ignored: YES
- Cursor restricted-data exclusion present: YES
- Restricted competition data inspected in Phase 01: NO

## Tests

- `python -m pip check`: PASS
- `pytest -q tests/test_project_setup.py`: PASS (4 passed)
- config YAML parse: PASS
- ignore-rule safety checks: PASS using dummy filenames only

## Files Created

- `.gitignore`
- `.cursorignore`
- `README.md`
- `requirements.txt`
- `requirements-lock.txt`
- `configs/paths.yaml`
- `configs/model_config.yaml`
- `data/README.md`
- `docs/00_MASTER_INDEX.md`
- `docs/repository_data_policy.md`
- `docs/reproducibility.md`
- `src/__init__.py`
- `src/common/__init__.py`
- `src/common/logging_utils.py`
- `src/task1/__init__.py`
- `src/task2a/__init__.py`
- `src/task2b/__init__.py`
- `tests/test_project_setup.py`
- safe `.gitkeep` placeholders in required empty/local-only directories

## Files Modified

- `MD Files/PHASE_01_COMPETITION_CONTRACT.md` — completion report and validation results
- `MD Files/WAYLOOM_DATATHON_MASTER_PLAN.md` — Phase 01 status registry

## Decisions Made

- The repository remains local with no configured remote because the existing remote could not be verified as private.
- Official competition files and derivatives remain outside the Phase 01 implementation scope and were not opened or inspected.
- The approved dependency set was installed in `.venv`; no cloud, AutoML, experiment-tracking, or proprietary modeling services were added.

## Issues Found

- Two concurrent dependency-install attempts encountered Windows file-lock conflicts; a sequential installation completed successfully. No unresolved dependency issue remains.
- The previously configured remote was removed locally because privacy could not be verified without GitHub access.

## STOP Conditions Triggered

- None.

## Deferred Work

- Dataset extraction/inventory → Phase 02
- Schema/data profiling → Phase 02/03
- Modelling → later phases

## Phase Verdict

PHASE 01 STATUS: PASS

READY FOR PHASE 02: YES
```

---

# 19. Final Phase 01 checklist

Before changing `READY FOR PHASE 02` to YES:

- [ ] Phase 00 passed.
- [ ] DT-011 through DT-022 are all complete.
- [ ] Secure repository exists.
- [ ] No raw/private competition data is tracked.
- [ ] Data-safety policy exists.
- [ ] Ignore safety tests pass.
- [ ] Python environment works.
- [ ] Dependencies import.
- [ ] `pip check` passes.
- [ ] Dependency files exist.
- [ ] Repository structure is complete.
- [ ] Seed policy is frozen.
- [ ] Configuration parses.
- [ ] Logging utility is safe.
- [ ] Setup tests pass.
- [ ] Reproducibility document exists.
- [ ] No competition ZIP/CSV has been extracted or inspected during this phase.
- [ ] Independent Phase 01 review passes.
- [ ] No unresolved STOP condition remains.

Only then:

```text
PHASE 01 STATUS: PASS
READY FOR PHASE 02: YES
```

Do not start Phase 02 automatically.
