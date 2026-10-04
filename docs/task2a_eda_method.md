# Task 2A Phase 12 EDA method

Phase 12 reads the Phase 11 canonical weekly panel and official daily
`calendar.csv`. It does not rebuild order history or create forecast features.
All comparisons are descriptive associations; they do not establish causes.

The runner validates unique depot/brand/ISO-week keys, nonnegative finite
targets, Fresh chilled bounds, exact Style/Tech chilled zeros, and the Phase 11
week status. ISO chronology follows `week_start_date` (or an ISO-derived Monday
only when the canonical field is absent). It retains confirmed-zero weeks and
allows documented boundary partial periods; unresolved/incomplete weeks block
EDA. Each panel ISO week must have seven dates in the official calendar.

Calendar context is aggregated directly from official daily fields. Payday,
holiday, festival, festival-ramp, monsoon, weekend, and operating-day values are
not reconstructed from dates or outside sources. Ramp bins, trend windows,
minimum seasonal support, and robust-spike thresholds are WayLoom engineering
settings in `configs/task2a_eda.yaml`.

Trend summaries use only historical rows in chronological order. Seasonal
profiles group by ISO week while retaining ISO year support, including week 53.
Same-week comparisons retain the observed years only. Rolling-median/MAD spike
scores use preceding observations only; MAD-zero cases are represented without
infinite scores. A whole-series IQR flag is secondary. No detector removes,
caps, replaces, or changes a target.

Trend output reports rolling-summary support separately from equal-length
recent-versus-prior comparison support. `SUFFICIENT` means both sides of that
comparison are present; otherwise the output labels whether the recent window
or its prior comparison lacks support. Same-week summaries include explicit
first and last observed ISO years. The CLI resolves the destination and rejects
any output path outside the ignored Phase 12 private-report directory.

The CLI writes aggregate tables, JSON summaries, a descriptive report, and
figures under the requested private output directory. Its console output is
sanitized. Run against real competition data locally only:

```powershell
python scripts/run_task2a_eda.py `
  --weekly-panel data/interim/task2a_weekly_panel.csv `
  --raw-root data/raw `
  --manifest configs/dataset_manifest.yaml `
  --history-config configs/task2a_history.yaml `
  --eda-config configs/task2a_eda.yaml `
  --output-dir reports/private/phase12_task2a_eda
```
