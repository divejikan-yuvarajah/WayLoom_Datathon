# Task 1 Advanced Modeling (Phase 09)

Phase 09 implements bounded, reproducible advanced model development for Task 1
using the frozen Phase 07 validation contract and frozen Phase 08 baselines.

Core guarantees:

- Development uses only Phase 07 development folds.
- Final holdout is excluded from search, tuning, and calibration fitting.
- Feature safety remains registry-driven with forbidden actual/target fields blocked.
- Classifier outputs probabilities and uses log loss as the primary criterion.
- Hyperparameter search is bounded and deterministic.
- Calibration is chronology-safe and based on development OOF probabilities only.
- Exactly one provisional service config and one provisional lateness config are
  eligible for one-time holdout confirmation.
- Final tracked model freeze config stores only reproducible model identity and
  settings, not private metric tables or row-level outputs.
