# Task 1 Baselines (Phase 08)

Phase 08 compares fixed, transparent baselines only on the immutable Phase 07
development folds. The final chronological holdout is not read or evaluated.

Service baselines: global median, brand median, brand+dock median, and fixed
`LinearRegression`. Lateness baselines: training-mean probability,
brand+dock rate with hierarchical fallback, and fixed `LogisticRegression`.

All grouped statistics, preprocessing, category vocabularies, and models are
fit only on each fold's training rows. Logistic regression uses probability
outputs; linear predictions are not clipped.

The implementation reuses Phase 07 MAE/RMSE and log-loss/Brier contracts plus
the frozen segment diagnostics. It does not tune hyperparameters, rebalance
classes, or select a final model.
