# WayLoom Datathon Reproducibility Notes

## System information

These values are recorded from the Phase 01 setup environment:

- Operating system: Windows 10, build 26100
- Python version: 3.13.7
- pip version: 26.2.1
- Git version: 2.47.1.windows.2
- Environment creation date: 2 October 2026

## Environment creation

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip freeze > requirements-lock.txt
```

If PowerShell activation is unavailable, use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Dependency verification

```powershell
python -m pip check
pytest -q tests/test_project_setup.py
```

`requirements.txt` contains direct dependencies. `requirements-lock.txt` is the exact local `pip freeze` snapshot and must not contain secrets, private paths, or editable machine-specific dependencies.

## Configuration and random seed

Configuration is stored in:

- `configs/paths.yaml`
- `configs/model_config.yaml`

The project default random seed is `42`. A seed improves reproducibility but does not guarantee bit-for-bit identical results across library versions, hardware, multithreading, or nondeterministic algorithms.

## Local competition-data placement

Phase 02 is the first phase permitted to extract or inventory official competition files. When authorized, place raw data only under ignored local paths such as `data/raw/`; private derivatives belong under `data/interim/` or `data/processed/`.

Do not commit, publish, transmit, or expose official competition data or private derivatives. Do not include raw rows in logs, screenshots, documentation, tests, or coding-agent prompts.

## Phase boundary

Phase 01 performs infrastructure setup only. It does not inspect CSV rows, extract archives, perform EDA, construct labels, build features, train models, forecast demand, optimize Task 2B, or generate submissions.

Phase 02 owns dataset extraction and inventory. Do not proceed to Phase 02 until the Phase 01 gate is explicitly approved.
