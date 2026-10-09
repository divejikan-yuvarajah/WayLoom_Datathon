# WayLoom final model artifacts

Phase 32 registers the frozen Task 1 and Task 2A artifacts used by the final competition notebook.

- `artifact_registry.json` is the single authoritative package-relative, checksum-bound inventory.
- `task1_service/` and `task1_late/` are the immutable Phase 10 bundles.
- `task2a_total/` and `task2a_chilled/` contain the frozen Phase 17 ensemble components serialized during the authorized Phase 32 finalization.
- `task2a/artifact_manifest.json` describes the fixed component mapping, weights, feature schema, and postprocessing contract.

All binary artifacts are trusted local competition artifacts. The registry loader verifies model-root containment, file size, and SHA256 before joblib deserialization. It does not accept arbitrary paths, URLs, or uploaded pickle/joblib files.

Task 1 preprocessing uses canonical deterministic feature code plus the registered feature schema. Task 2A deterministic feature construction remains in canonical code; learned LightGBM preprocessing state is embedded in the saved ensemble components. No raw training or test rows are stored in this registry layer.

Phase 31 loads through `src.common.artifact_registry.load_phase31_artifact_set`. Private real-data parity remains a human-local gate.

`configs/final_artifacts.yaml` is retained only for backward-compatible audit evidence. It is not an authoritative loading source, and safe validation rejects any hash divergence from the registry.

Task 2A finalization writes candidates under ignored `models/.staging/phase32/`, reloads them through a staging-scoped secured registry, runs synthetic and prediction parity, and publishes canonical files plus the registry only after validation. Existing valid canonical artifacts are never overwritten by default.
