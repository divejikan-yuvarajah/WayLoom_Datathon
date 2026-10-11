# Task 2A Phase 17 final inference

Phase 17 executes the already `FROZEN` Phase 16 configuration only. It rebuilds
origin-safe Phase 13 demand features at the one latest complete historical
week, joins official future calendar features by ISO year/week, and requires
every official target to map to horizon 1 through 10. No model search,
hyperparameter tuning, recursive demand update, or validation re-selection is
available in this path.

Model components use their frozen family, parameters, feature profile, seed,
and final median iteration count. Baseline components reuse the Phase 15
origin-bounded baseline API. Ensemble components run independently and combine
only with their frozen 50/50 weights.

The postprocessing order is fixed: raw total, raw Fresh chilled, Style/Tech
structural zero, nonnegative clipping, then chilled capped down to total. The
submission is mapped by `row_id`, restored to template order, written
atomically, read back, and validated without repair.

The local runner writes only private diagnostics under
`reports/private/phase17_task2a_final/`; console output is sanitized status
only. Run the two Phase 17 commands supplied in the phase handoff locally.
