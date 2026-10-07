# Phase 27 uncertainty specification

## Calibration sources

- Task 1: deterministic recreation of the frozen Phase 7/9 out-of-sample service validation. Training residuals are rejected.
- Task 2A: `reports/private/phase16_task2a_advanced/candidate_predictions.csv`, filtered to the frozen total and Fresh chilled champions and processed with Phase 17 semantics.

## Intervals

For nonnegative point prediction `p`, absolute OOS residual scores determine `q(c)` by rank `clip(ceil((n+1)c), 1, n)`. The additive interval is `[max(0,p-q), max(max(0,p-q),p+q)]`. Task 2A uses target+horizon calibration with a predeclared pooled-target fallback. Style/Tech chilled is always `[0,0]`.

Both raw chilled intervals and total-coherent presentation bounds are stored. Sequential coverage diagnostics for rolling folds use only residuals from strictly earlier origins. Unavailable early-fold diagnostics remain explicitly unavailable.

## Safety

The builder writes uncertainty artifacts only below `reports/private/`. It hashes frozen configs, model directories, submissions, and Task 2B final artifacts before and after execution. The validator compares private point columns exactly with official submissions and rejects official schema additions. Phase 28 is outside scope.
