# WayLoom Datathon Architecture

## Purpose

These diagrams describe the finalized WayLoom Datathon implementation at a judge-friendly level. They document the system that exists; they do not redesign, retrain, or re-optimize any frozen pipeline.

## Official requirement

The competition requires architecture diagrams showing the models, preprocessing pipeline, and proposed deployment approach. High-level diagrams are sufficient. The Datathon is judged separately from the Hackathon, so Hackathon integration is optional and is not a requirement for these pipelines.

## Diagram index

| Diagram | Mermaid source | Static export | Purpose |
|---|---|---|---|
| High-level Datathon | [high_level_datathon.mmd](high_level_datathon.mmd) | [high_level_datathon.svg](high_level_datathon.svg) | Three analytical branches and controlled deliverables |
| Task 1 pipeline | [task1_pipeline.mmd](task1_pipeline.mmd) | [task1_pipeline.svg](task1_pipeline.svg) | Label construction, leakage-safe features, final CatBoost models and inference |
| Task 2A forecasting | [task2a_forecasting.mmd](task2a_forecasting.mmd) | [task2a_forecasting.svg](task2a_forecasting.svg) | Demand history, direct-global features, rolling validation and final ensembles |
| Task 2B optimization | [task2b_optimization.mmd](task2b_optimization.mmd) | [task2b_optimization.svg](task2b_optimization.svg) | Official feasibility, WayLoom policy, CP-SAT, freeze and checking |
| Proposed deployment | [proposed_deployment.mmd](proposed_deployment.mmd) | [proposed_deployment.svg](proposed_deployment.svg) | Clearly proposed private, internal batch operation |

## Source-of-truth policy

Architecture facts follow the official Challenge Booklet, the master plan, frozen phase contracts, final tracked configurations, and implementation code in that order. When historical design examples differ from the final configuration, the final configuration wins. The machine-checkable [architecture_manifest.yaml](architecture_manifest.yaml) is generated from safe tracked configurations.

## Diagram legend

- Blue: data or versioned artifacts.
- Green: preprocessing and deterministic transformation.
- Purple: trained model inference.
- Orange: optimization or WayLoom soft policy.
- Yellow: validation, audit, freeze, or monitoring gate.
- Teal: controlled output or consumer.
- Dashed gray/red: optional, excluded, proposed, or privacy-boundary information.

Labels and shapes carry the meaning, so the diagrams remain understandable without color.

## Required and optional architecture

Task 1, Task 2A, Task 2B, their validation gates, and their competition artifacts are the required core. The Phase 28 synthetic/internal integration contract is shown only as an optional dashed deployment extension. It is not a dependency of model inference, optimization, official submissions, or Hackathon delivery.

## Rendering instructions

Mermaid source is canonical. With Mermaid CLI already installed locally, render deterministic white-background SVGs with:

```powershell
.\.venv\Scripts\python.exe scripts\render_architecture_diagrams.py --source-dir docs\architecture --output-dir docs\architecture
```

The rendering script embeds each source SHA256 and stable diagram title in its SVG so validation detects stale exports. It does not download fonts or other remote assets.

## Privacy note

The files contain architecture metadata only. They contain no competition rows, sample identifiers, private report contents, credentials, private hashes, or local user paths. Private data and derivatives remain inside the secure execution boundary. Official submissions are controlled artifacts rather than API data sources.

## Validation status

Build and validate with:

```powershell
.\.venv\Scripts\python.exe scripts\build_architecture_manifest.py
.\.venv\Scripts\python.exe scripts\validate_architecture_docs.py --architecture-dir docs\architecture --manifest docs\architecture\architecture_manifest.yaml
```

Static diagrams still require a human visual check at desktop, fit-to-page, and projected/video scale before final packaging.
