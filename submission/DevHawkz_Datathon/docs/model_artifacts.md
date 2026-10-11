# Final model artifact contract

Phase 32 manages model state only; it does not select, retune, or retrain champions during safe validation.

Task 1 uses the existing immutable Phase 10 CatBoost bundles. The service artifact applies the frozen `fail` negative-prediction policy. The lateness artifact uses raw probabilities, class order `[0, 1]`, and positive-class index `1`; no calibration artifact is required.

Task 2A uses two frozen 50/50 CatBoost-LightGBM ensembles: one for total demand and one for Fresh chilled demand. Each serialized `FittedComponent` contains both model components and the learned LightGBM preprocessing object. Feature construction and output postprocessing remain deterministic canonical code. Forecast horizon is 10 weeks; Style and Tech chilled output is exactly zero.

`models/artifact_registry.json` is the single final authority. It records package-relative paths, sizes, SHA256 checksums, schema references, runtime versions, preprocessor modes, and canonical load/inference entrypoints. The loader rejects absolute paths, traversal, URLs, unknown serializers, missing files, and checksum mismatches before deserialization.

Task 2A candidates are serialized under ignored staging storage and loaded through the secured registry before synthetic and full parity validation. Canonical promotion and registry publication occur only afterward; an existing different canonical bundle requires explicit controlled refinalization.

Safe validation may load only registered trusted local artifacts. Private prediction parity requires the authorized local competition data and must run through `scripts/run_model_artifact_parity.py`; its console output is aggregate PASS/FAIL only.

The Phase 31 final cell and private parity both load the exact bundles returned by the secured registry loader. The older `configs/final_artifacts.yaml` inventory is deprecated and guarded against divergence.

After Phase 32 human-local parity is rerun through this unified path, control returns to Phase 31 for its clean-kernel run-all and final-cell-only closure. Phase 33 is not authorized by Phase 32 alone.
