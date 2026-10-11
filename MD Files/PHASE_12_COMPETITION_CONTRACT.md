# PHASE 12 — Task 2A Exploratory Analysis

> **Canonical filename:** `PHASE_12_COMPETITION_CONTRACT.md`  
> **Project:** WayLoom — Rootcode Tech-Triathlon 2026 Datathon  
> **Task range:** **DT-192 → DT-203**  
> **Task count:** **12**  
> **Master-plan phase name:** **Phase 12 — Task 2A exploratory analysis**  
> **Phase dependency:** **Phase 11**  
> **Default phase priority:** **P1**  
> **Phase gate:** **Demand seasonality, trend and calendar relationships are understood sufficiently to justify forecasting features.**  
> **Agent environment:** OpenAI Codex in VS Code. Earlier “Cursor” wording in project contracts should be interpreted as generic coding-agent instructions.  
> **Recommended economical agent setting:** use the lowest-cost capable coding model available in your Codex picker at **medium reasoning** for implementation. Escalate only if the calendar/week logic or tests expose a genuine blocker; Phase 12 is primarily deterministic EDA/reporting, not advanced modelling.

---

# 1. Phase purpose

Phase 12 performs **historical exploratory analysis for Task 2A** using the canonical weekly demand history built and reconciled in Phase 11.

This phase does **not** forecast future demand yet.

It answers:

- How does weekly total requested volume vary by depot and brand?
- How does Fresh chilled demand behave over time?
- Is there an observable recent trend?
- Is there repeatable annual/ISO-week seasonality?
- How are demand levels associated with festivals and the official `festival_ramp` field?
- How are weekly volumes associated with paydays, holidays, monsoon context, and the number of operating days?
- Do corresponding ISO weeks behave similarly across years?
- Which weeks are unusual enough to require modelling caution rather than automatic deletion?

The outputs of this phase inform:

```text
Phase 13 → Task 2A forecasting features
Phase 14 → forecasting validation
Phase 15 → forecasting baselines
Phase 16 → advanced forecasting
Phase 17 → final Task 2A inference
```

Phase 12 is **descriptive**. It must not silently become a model-selection or future-target-engineering phase.

---

# 2. Official Task 2A contract that constrains this phase

The official challenge requires forecasts of:

```text
pred_total_volume_m3
pred_chilled_volume_m3
```

for each supplied:

```text
depot + brand + future ISO week
```

over a **10-week forecast horizon**.

The official demand-history rules already enforced in Phase 11 remain non-negotiable:

1. Historical demand comes from **both**:

   ```text
   deliveries_train.csv
   task1_test_inputs.csv
   ```

2. Every unique requested order counts once, including:

   ```text
   attempted
   deferred
   not_run
   ```

3. Demand belongs to requested:

   ```text
   order_date
   ```

   not later `dispatch_date`.

4. Official weekly grouping comes from `calendar.csv`:

   ```text
   iso_year
   iso_week
   ```

5. Only **Fresh** has chilled demand.
6. Style chilled volume is logically **0**.
7. Tech chilled volume is logically **0**.
8. Task 2A predicts **volume only**; it does not forecast numbers of vehicles or drivers.

The official `calendar.csv` provides historical/future-known context including:

```text
date
dow
dow_name
is_weekend
iso_year
iso_week
is_payday
festival
festival_ramp
is_holiday
monsoon
is_operating
```

Important official meanings:

```text
is_payday
1 on payday

festival
festival name on festival date; blank otherwise

festival_ramp
0..1; proximity to a festival, rising during the preceding nine days,
with 1 on the festival date

is_holiday
1 on a festival date or public holiday

monsoon
1 during monsoon/inter-monsoon month; otherwise 0

is_operating
1 when deliveries operate on that date; otherwise 0
```

The challenge does **not** prescribe a particular EDA methodology, plot library, trend window, spike detector, or statistical test. Those are **WayLoom engineering decisions** and must remain clearly distinguished from official requirements.

---

# 3. Source authority and precedence

When implementation details conflict, use this precedence:

1. Official Challenge Booklet.
2. Official supplied CSVs/templates.
3. `WAYLOOM_DATATHON_MASTER_PLAN.md`.
4. Approved phase contracts.
5. Existing tested project code.
6. `AGENTS.md` and `CODEX_HANDOFF_PHASE_11_ONWARDS.md`.
7. Engineering assumptions in this document.

Do not silently replace an official definition with a convenience rule.

---

# 4. Phase 12 finalized master task registry

This list is copied from the finalized WayLoom master inventory.

| Status | Task | Mark | Priority | Dependency | Work item |
|---|---|---:|---:|---|---|
| [ ] | **DT-192** | [E] | P1 | Phase 11 | Plot weekly total demand by depot/brand |
| [ ] | **DT-193** | [E] | P1 | Phase 11 | Plot Fresh chilled demand |
| [ ] | **DT-194** | [E] | P1 | Phase 11 | Analyze recent trend |
| [ ] | **DT-195** | [E] | P1 | Phase 11 | Analyze yearly seasonality |
| [ ] | **DT-196** | [E] | P1 | Phase 11 | Analyze festival effects |
| [ ] | **DT-197** | [E] | P1 | Phase 11 | Analyze festival-ramp effects |
| [ ] | **DT-198** | [E] | P1 | Phase 11 | Analyze payday effects |
| [ ] | **DT-199** | [E] | P1 | Phase 11 | Analyze holiday effects |
| [ ] | **DT-200** | [E] | P1 | Phase 11 | Analyze monsoon effects |
| [ ] | **DT-201** | [E] | P1 | Phase 11 | Analyze number of operating days per week |
| [ ] | **DT-202** | [E] | P1 | Phase 11 | Compare same week across years |
| [ ] | **DT-203** | [E] | P1 | Phase 11 | Detect abnormal weekly spikes |

**Phase complete:** [ ]  
**READY FOR PHASE 13:** NO

---

# 5. Phase prerequisites

Before implementing/running Phase 12, Phase 11 must be complete.

The following Phase 11 artifacts/interfaces should exist or have canonical equivalents:

```text
data/interim/task2a_weekly_panel.csv
configs/task2a_history.yaml
src/task2a/history.py
```

The local Phase 11 validation should already establish:

```text
combined delivery_id uniqueness      PASS
attempted retained                   PASS
deferred retained                    PASS
not_run retained                     PASS
order_date rule                      PASS
calendar join                        PASS
weekly total reconciliation          PASS
Style chilled == 0                  PASS
Tech chilled == 0                   PASS
unresolved weekly gaps              0
```

Phase 12 must **consume**, not reinterpret, that canonical history.

If Phase 11 is not passing:

```text
STOP
```

Do not “repair” historical demand inside EDA code.

---

# 6. Data safety and Codex execution boundary

Phase 12 produces aggregate private statistics and charts derived from competition data.

Codex may autonomously:

- read tracked code/config/docs;
- create EDA utilities;
- create plotting/reporting functions;
- create synthetic fixtures;
- run synthetic unit/integration tests;
- debug ordinary implementation failures;
- run the complete safe test suite;
- inspect Git status/diff;
- verify ignore rules.

Codex should **not** inspect or print real row-level competition data from:

```text
data/raw/**
data/interim/**
reports/private/**
```

The human runs the real Phase 12 EDA locally.

Detailed real-data EDA artifacts should stay under:

```text
reports/private/phase12_task2a_eda/**
```

Return only sanitized local status to Codex/review.

---

# 7. Phase 12 inputs

## Canonical required input

```text
data/interim/task2a_weekly_panel.csv
```

Canonical grain:

```text
one row per:

depot
brand
iso_year
iso_week
```

Expected Phase 11 fields include canonical equivalents of:

```text
depot
brand
iso_year
iso_week
week_start_date
week_end_date
total_volume_m3
chilled_volume_m3
order_count
operating_days
week_status
```

Exact existing field names should be reused rather than unnecessarily renamed.

## Official calendar source

```text
calendar.csv
```

Phase 12 should derive weekly calendar context deterministically from official daily calendar values where the Phase 11 panel does not already contain those aggregates.

Do not infer festivals/paydays/holidays/monsoon from external sources.

---

# 8. Required repository additions

Create or update tracked files:

```text
src/task2a/eda.py
scripts/run_task2a_eda.py
configs/task2a_eda.yaml
docs/task2a_eda_method.md
tests/test_task2a_eda.py
```

Optional if the existing project architecture prefers separation:

```text
src/task2a/calendar_features.py
```

Do not create a duplicate module if a canonical Task 2A calendar utility already exists.

Private local outputs:

```text
reports/private/phase12_task2a_eda/
├── eda_summary.json
├── weekly_calendar_context.json
├── total_demand_summary.csv
├── chilled_demand_summary.csv
├── trend_analysis.csv
├── seasonality_analysis.csv
├── festival_analysis.csv
├── festival_ramp_analysis.csv
├── payday_analysis.csv
├── holiday_analysis.csv
├── monsoon_analysis.csv
├── operating_days_analysis.csv
├── same_week_across_years.csv
├── spike_analysis.csv
├── feature_candidates.json
├── warnings.json
├── phase12_eda_report.md
└── figures/
```

These outputs are private competition derivatives and must remain ignored.

---

# 9. Recommended configuration

Create:

```text
configs/task2a_eda.yaml
```

Recommended engineering contract:

```yaml
version: 1

input:
  weekly_panel: data/interim/task2a_weekly_panel.csv

series_keys:
  - depot
  - brand

time_keys:
  - iso_year
  - iso_week

targets:
  total: total_volume_m3
  chilled: chilled_volume_m3

trend:
  windows_weeks:
    - 4
    - 8
    - 13
  minimum_history_weeks: 8
  compare_recent_vs_prior: true

seasonality:
  week_of_year_min_support_years: 2
  normalize_within_series: true

festival:
  weekly_any_flag: true
  weekly_day_count: true
  preserve_names: true

festival_ramp:
  summaries:
    - max
    - mean
  bins:
    - 0.0
    - 0.25
    - 0.50
    - 0.75
    - 1.000001

payday:
  weekly_day_count: true
  any_flag: true

holiday:
  weekly_day_count: true
  any_flag: true

monsoon:
  weekly_day_count: true
  weekly_fraction: true

operating_days:
  use_calendar_is_operating: true

spikes:
  primary_method: rolling_mad
  trailing_window_weeks: 13
  minimum_history_weeks: 8
  robust_z_threshold: 3.5
  secondary_method: iqr
  iqr_multiplier: 1.5
  do_not_drop_detected_weeks: true

small_sample:
  minimum_group_n: 4

privacy:
  output_dir: reports/private/phase12_task2a_eda
```

These values are **WayLoom engineering defaults**, not official organizer requirements.

Do not tune thresholds after viewing future Task 2A outcomes.

---

# 10. Weekly calendar-context construction

Phase 12 needs weekly calendar context for DT-196–DT-201.

Create deterministic weekly aggregates from `calendar.csv` keyed by:

```text
iso_year
iso_week
```

Recommended fields:

```text
calendar_days
operating_days
weekend_days
payday_days
has_payday
holiday_days
has_holiday
festival_days
has_festival
festival_names
max_festival_ramp
mean_festival_ramp
monsoon_days
monsoon_day_fraction
has_monsoon_day
```

Recommended semantics:

```text
calendar_days
count of official calendar dates in that ISO week

operating_days
sum(is_operating)

payday_days
sum(is_payday)

has_payday
1 if payday_days > 0 else 0

holiday_days
sum(is_holiday)

has_holiday
1 if holiday_days > 0 else 0

festival_days
number of dates with nonblank festival

has_festival
1 if festival_days > 0 else 0

festival_names
sorted unique nonblank festival names joined deterministically

max_festival_ramp
max daily festival_ramp within week

mean_festival_ramp
mean daily festival_ramp within week

monsoon_days
sum(monsoon)

monsoon_day_fraction
monsoon_days / calendar_days
```

Do not assume an ISO week has exactly seven calendar rows without checking coverage.

If calendar coverage is incomplete for a historical week:

```text
STOP / warning according to Phase 11 week-status policy
```

Do not silently calculate context on partial calendar weeks and compare it as if complete.

---

# 11. General EDA principles

## 11.1 EDA is descriptive, not causal

Use language such as:

```text
associated with
coincides with
shows a historical pattern
candidate for Phase 13 validation
```

Avoid:

```text
causes demand
proves festival effect
monsoon drives volume
```

Phase 12 is observational.

## 11.2 Preserve series grain

Primary Task 2A series are:

```text
depot + brand
```

Do not combine all brands/depots into one series for core analysis.

Portfolio-level views may be secondary only.

## 11.3 Always report support

Every grouped comparison must include:

```text
n_weeks
```

and where relevant:

```text
n_years
```

Do not overinterpret a one-week festival group.

## 11.4 Do not remove unusual weeks

DT-203 detects spikes for modelling awareness.

It does **not** authorize:

- deleting weeks;
- capping target volume;
- winsorizing history;
- replacing observed demand with rolling means.

Any later outlier treatment would require a separate validated modelling decision.

## 11.5 Avoid using future test outcomes

Task 2A future inputs contain future depot/brand/week rows, not true future demand.

Phase 12 must not require or fabricate future actual volumes.

---

# 12. DT-192 — Plot weekly total demand by depot/brand

**Mark:** [E]  
**Priority:** P1  
**Dependency:** Phase 11

## Objective

Visualize and summarize the canonical weekly requested **total volume** for every Task 2A series:

```text
depot + brand
```

## Input

```text
task2a_weekly_panel
```

using:

```text
depot
brand
iso_year
iso_week
week_start_date
total_volume_m3
week_status
```

## Required checks

Before plotting:

- panel key unique;
- total volume numeric;
- total volume finite;
- total volume nonnegative;
- chronology ordered by actual week/date, not lexicographic string;
- unresolved gap statuses absent.

## Required outputs

For each series report:

```text
n_weeks
start_week
end_week
mean_total_volume_m3
median_total_volume_m3
std_total_volume_m3
min_total_volume_m3
p25
p75
p90
p95
max_total_volume_m3
coefficient_of_variation (optional diagnostic)
```

Required figure:

```text
weekly total demand over time by depot/brand
```

Prefer separate facets/series rather than an unreadable all-series overlay.

## Interpretation questions

- Are levels materially different by brand?
- Are Peliyagoda and Kandy on different scales?
- Is demand stable, trending, seasonal, or irregular?
- Are zero-demand weeks genuine `CONFIRMED_ZERO` weeks?
- Are there visible level shifts?

## Tests

Synthetic:

- two depots × three brands;
- correct chronological ordering across ISO-year boundary;
- zero week retained;
- negative target rejected;
- duplicate weekly key rejected.

## STOP conditions

- unresolved Phase 11 gap;
- duplicate series/week key;
- negative/nonfinite target.

## Definition of Done

- [ ] all available depot/brand series summarized;
- [ ] weekly total plot generated;
- [ ] support and date ranges reported;
- [ ] no target mutation.

---

# 13. DT-193 — Plot Fresh chilled demand

**Mark:** [E]  
**Priority:** P1

## Objective

Understand historical **Fresh chilled volume** separately from total Fresh demand.

## Scope

Only rows where:

```text
brand == Fresh
```

are eligible for nonzero chilled demand.

For Style and Tech:

```text
chilled_volume_m3 == 0
```

must still be asserted as a global invariant, but they are not the focus of the chilled-demand plot.

## Required Fresh summaries

Per depot:

```text
n_weeks
mean_chilled_volume_m3
median_chilled_volume_m3
p90_chilled_volume_m3
max_chilled_volume_m3
mean_chilled_share
median_chilled_share
```

where:

```text
chilled_share = chilled_volume_m3 / total_volume_m3
```

with safe handling when total volume is zero.

Recommended zero-total policy:

```text
if total_volume_m3 == 0:
    chilled_share = NaN
```

Do not divide by zero or create infinity.

## Required invariants

For every Fresh row:

```text
0 <= chilled_volume_m3 <= total_volume_m3
```

For Style/Tech:

```text
chilled_volume_m3 == 0.0 exactly
```

## Figures

Recommended:

1. Fresh chilled weekly volume by depot;
2. Fresh total vs chilled over time;
3. chilled share over time as a secondary diagnostic.

## Tests

- Fresh chilled subset;
- Fresh ambient-only week;
- Fresh zero-total week;
- chilled share safe division;
- chilled > total fails;
- Style/Tech nonzero chilled fails.

## Definition of Done

- [ ] Fresh chilled time series generated;
- [ ] chilled share safely summarized;
- [ ] all chilled invariants pass.

---

# 14. DT-194 — Analyze recent trend

**Mark:** [E]  
**Priority:** P1

## Objective

Describe whether each depot/brand series has recently increased, decreased, or remained broadly stable.

This is EDA only; it does not yet create final forecast features.

## Recommended engineering methods

For each series, compute trailing summaries using configurable windows such as:

```text
4 weeks
8 weeks
13 weeks
```

Possible diagnostics:

```text
rolling_mean
rolling_median
recent_mean
prior_equal_length_mean
recent_vs_prior_absolute_change
recent_vs_prior_percent_change
robust_recent_slope
```

Recommended slope:

simple OLS slope on week index for descriptive use, or a robust median-based slope if already supported.

Do not create an elaborate forecasting model here.

## Percent-change safety

If prior mean is zero or near zero:

- do not produce infinity;
- mark percent change unavailable;
- still report absolute change.

## Required support

Do not calculate a 13-week trend from fewer than the configured minimum weeks.

Return:

```text
INSUFFICIENT_HISTORY
```

rather than fabricating a trend.

## Interpretation

Trend labels such as:

```text
UP
DOWN
STABLE
```

may be included only if thresholds are predeclared and described as engineering diagnostics.

Prefer numeric trend measures in the report.

## Tests

Synthetic:

- increasing series;
- decreasing series;
- flat series;
- too-short series;
- prior mean zero;
- chronological boundary across ISO years.

## STOP conditions

No hard stop solely because a series trends strongly.

Stop only for broken chronology or invalid target values.

## Definition of Done

- [ ] recent rolling summaries produced;
- [ ] short-history behavior explicit;
- [ ] no future demand used;
- [ ] candidate trend windows recorded for Phase 13 consideration.

---

# 15. DT-195 — Analyze yearly seasonality

**Mark:** [E]  
**Priority:** P1

## Objective

Determine whether demand appears to have repeatable within-year patterns by official ISO week.

## Required grouping

Use:

```text
series = depot + brand
seasonal position = iso_week
```

Always preserve `iso_year` separately.

Never use week number alone as a unique timestamp.

## Recommended analyses

For each series and `iso_week`:

```text
n_years
mean_volume
median_volume
std_volume
min_volume
max_volume
```

Optional normalized analysis:

Normalize each year's weekly values relative to that series/year level, e.g.:

```text
volume / yearly median
```

This helps distinguish seasonality from long-term level growth.

If used, document that normalization is an EDA diagnostic, not an official rule.

## Minimum support

A week-of-year seasonal estimate should not be treated as repeatable unless observed in at least:

```text
configured minimum number of years
```

Recommended default:

```text
2 years
```

If history contains only one year for a week:

```text
seasonality_support = INSUFFICIENT
```

## Figures

Recommended:

- ISO week vs median/mean demand by series;
- overlay annual trajectories by ISO week;
- normalized seasonal profile if useful.

## Tests

- repeated same ISO week across two years;
- single-year insufficient support;
- week 53;
- ISO-year boundary;
- normalization with zero yearly median handled safely.

## Definition of Done

- [ ] seasonal profile generated;
- [ ] support by number of years included;
- [ ] unsupported weeks clearly marked;
- [ ] no claim of seasonality based on one occurrence.

---

# 16. DT-196 — Analyze festival effects

**Mark:** [E]  
**Priority:** P1

## Objective

Explore historical association between weekly demand and official festival dates from `calendar.csv`.

## Weekly festival context

Recommended fields:

```text
festival_days
has_festival
festival_names
```

`festival_names` should be deterministic:

```text
sorted unique nonblank names
```

Do not infer festivals from date strings or external calendars.

## Comparison

Per depot/brand series compare:

```text
festival weeks
vs
non-festival weeks
```

Required metrics:

```text
n_weeks
mean_volume
median_volume
p25
p75
p90
```

Optional normalized comparison:

```text
volume relative to trailing nonfuture baseline
```

If implemented, that baseline must use only earlier weeks for that historical row.

For pure EDA, raw grouped statistics are sufficient.

## Festival-specific breakdown

If sample sizes permit, summarize by festival name.

Always include:

```text
n_weeks
```

Do not report a festival-specific “effect” from a single historical week as stable evidence.

## Interpretation

Use:

```text
historically higher/lower around observed festival weeks
```

not:

```text
festival causes X% uplift
```

unless a formal causal design exists, which this phase does not provide.

## Tests

- blank festival ignored;
- one festival date sets weekly flag;
- multiple festival names deterministic;
- group counts correct;
- no external calendar usage.

## Definition of Done

- [ ] official festival context aggregated weekly;
- [ ] festival/nonfestival comparison produced;
- [ ] festival-name support included;
- [ ] causal wording avoided.

---

# 17. DT-197 — Analyze festival-ramp effects

**Mark:** [E]  
**Priority:** P1

## Objective

Explore whether weekly demand changes as official festival proximity rises.

Official daily field:

```text
festival_ramp ∈ [0,1]
```

with values rising during the preceding nine days and reaching 1 on the festival date.

## Weekly aggregation

Recommended:

```text
max_festival_ramp
mean_festival_ramp
```

Reason:

- `max` captures whether the week gets close to a festival;
- `mean` captures sustained festival proximity across the week.

Do not sum ramp values and present the sum as an official field.

## Analysis

Use configurable bins, e.g.:

```text
[0.00,0.25)
[0.25,0.50)
[0.50,0.75)
[0.75,1.00]
```

For each bin and series report:

```text
n_weeks
mean_volume
median_volume
p90_volume
```

Optional descriptive correlation:

```text
Spearman(max_festival_ramp, total_volume_m3)
```

with adequate sample size.

## Validation

Assert daily ramp values are:

```text
0 <= festival_ramp <= 1
```

Do not silently clip invalid calendar values.

## Tests

- weekly max ramp;
- weekly mean ramp;
- exact 0 and 1 boundaries;
- invalid <0/>1 fails;
- bin assignment deterministic;
- constant ramp handles correlation gracefully.

## Definition of Done

- [ ] weekly ramp summaries created;
- [ ] ramp-bin demand comparison produced;
- [ ] support sizes included;
- [ ] ramp semantics remain official.

---

# 18. DT-198 — Analyze payday effects

**Mark:** [E]  
**Priority:** P1

## Objective

Describe historical weekly demand around official payday dates.

## Weekly context

Derive:

```text
payday_days = sum(is_payday)
has_payday = payday_days > 0
```

from official calendar rows.

Do not infer payday from day-of-month.

## Analysis

Compare per series:

```text
has_payday = 1
vs
has_payday = 0
```

Metrics:

```text
n_weeks
mean_volume
median_volume
p90_volume
```

Also inspect `payday_days` if any week can contain more than one official payday flag.

## Optional chilled analysis

For Fresh, the same context may be compared with:

```text
chilled_volume_m3
```

as a secondary diagnostic.

## Tests

- payday day count;
- no-payday week;
- weekly flag;
- values outside 0/1 rejected.

## Definition of Done

- [ ] official payday context used;
- [ ] grouped demand comparison produced;
- [ ] support sizes reported.

---

# 19. DT-199 — Analyze holiday effects

**Mark:** [E]  
**Priority:** P1

## Objective

Explore association between weekly demand and official holidays.

Official daily field:

```text
is_holiday
```

includes festival dates or public holidays according to the official calendar.

## Weekly context

```text
holiday_days = sum(is_holiday)
has_holiday = holiday_days > 0
```

## Analysis

Per series compare:

```text
holiday weeks
vs
non-holiday weeks
```

Report:

```text
n_weeks
mean_volume
median_volume
p90_volume
```

Optionally evaluate demand per operating day as a secondary diagnostic:

```text
total_volume_m3 / operating_days
```

only when `operating_days > 0`.

Do not replace the main weekly target with per-day demand.

## Important distinction

`festival` and `is_holiday` are related but not identical fields.

Do not merge their analyses into one flag and lose official distinctions.

## Tests

- holiday count;
- weekly flag;
- festival and holiday fields can differ;
- zero-operating-day rate calculation handled safely.

## Definition of Done

- [ ] holiday/nonholiday comparison generated;
- [ ] official holiday field preserved distinctly from festival.

---

# 20. DT-200 — Analyze monsoon effects

**Mark:** [E]  
**Priority:** P1

## Objective

Describe weekly demand under official monsoon/inter-monsoon context.

Official daily field:

```text
monsoon ∈ {0,1}
```

## Weekly context

Recommended:

```text
monsoon_days = sum(monsoon)
monsoon_day_fraction = monsoon_days / calendar_days
has_monsoon_day = monsoon_days > 0
```

Because a week can cross month/context boundaries, do not assume every week is necessarily entirely monsoon or entirely non-monsoon.

## Analysis

Per series analyze:

- demand by `has_monsoon_day`;
- demand against `monsoon_day_fraction`;
- optional Fresh chilled demand by monsoon context.

Metrics:

```text
n_weeks
mean_volume
median_volume
p90_volume
```

Optional Spearman association with fraction if there is variation.

## Interpretation

Do not claim monsoon causes demand changes.

Remember monsoon may also coincide with:

- calendar season;
- festivals;
- holidays;
- other time trends.

## Tests

- all-zero week;
- all-one week;
- mixed week;
- fraction calculation;
- invalid daily monsoon value rejected.

## Definition of Done

- [ ] monsoon weekly context correct;
- [ ] mixed-context weeks handled transparently;
- [ ] demand comparison produced.

---

# 21. DT-201 — Analyze number of operating days per week

**Mark:** [E]  
**Priority:** P1

## Objective

Understand how weekly requested demand varies with the official number of delivery operating days.

Official source:

```text
calendar.is_operating
```

Do not infer operating days from weekday alone.

## Weekly context

```text
operating_days = sum(is_operating)
```

Recommended validation:

```text
0 <= operating_days <= calendar_days
```

Do not hard-code Monday–Saturday as six days for every week; official calendar values are authoritative.

## Analysis

Per series report by `operating_days`:

```text
n_weeks
mean_volume
median_volume
p90_volume
```

Secondary diagnostic:

```text
volume_per_operating_day = total_volume_m3 / operating_days
```

only when operating days > 0.

For Fresh chilled, optional:

```text
chilled_volume_per_operating_day
```

## Zero-operating-day weeks

If an official week has zero operating days:

- keep it;
- do not divide by zero;
- inspect whether demand was still requested;
- record it explicitly.

Demand is requested volume, not necessarily dispatched volume, so zero operating days does not automatically imply zero requested demand.

## Tests

- operating day count;
- official values overriding weekday intuition;
- zero operating days;
- partial/boundary calendar week;
- safe per-day division.

## Definition of Done

- [ ] operating-day relationship summarized;
- [ ] official `is_operating` used;
- [ ] zero-day weeks handled safely;
- [ ] weekly target remains primary.

---

# 22. DT-202 — Compare same week across years

**Mark:** [E]  
**Priority:** P1

## Objective

Compare corresponding ISO weeks across historical years to understand repeatability and year-over-year change.

## Comparison key

For each:

```text
depot
brand
iso_week
```

compare rows across:

```text
iso_year
```

## Required output

For each eligible same-week pair or group:

```text
depot
brand
iso_week
n_years
first_year
last_year
volumes_by_year or private long form
year_over_year_absolute_change
year_over_year_percent_change (when denominator > 0)
median_same_week_volume
same_week_variability
```

For Fresh optionally include chilled equivalents.

## Important ISO rule

Never compare by Gregorian calendar date/month in place of official `iso_week`.

Week 53 may not exist in every year.

Do not force a missing week 53 observation.

## Support rules

If `n_years < 2`:

```text
SAME_WEEK_COMPARISON_UNAVAILABLE
```

Do not calculate fake year-over-year change.

## Percent change

If prior-year same-week volume is zero:

- absolute change remains valid;
- percentage change is unavailable;
- do not create infinity.

## Figures

Recommended:

- year-over-year same-week scatter;
- ISO-week seasonal overlay;
- distribution of same-week absolute/relative changes.

## Tests

- same ISO week across two years;
- three-year sequence;
- missing middle year;
- week 53;
- prior zero denominator;
- one-year support.

## Definition of Done

- [ ] same-week comparison generated where supported;
- [ ] insufficient support explicit;
- [ ] ISO-year/week semantics correct;
- [ ] no synthetic missing year inserted as observed demand.

---

# 23. DT-203 — Detect abnormal weekly spikes

**Mark:** [E]  
**Priority:** P1

## Objective

Identify unusual historical weekly demand values that could affect forecasting, while preserving them as legitimate observations unless independently proven erroneous.

This is **anomaly detection for EDA**, not data cleaning.

## Primary engineering method

Recommended robust trailing detector per series:

```text
rolling median
rolling MAD
```

using only prior historical weeks for each diagnostic row.

Conceptually:

```text
baseline_t = median(previous W weeks)
MAD_t      = median(abs(previous W weeks - baseline_t))
robust_z   = 0.6745 * (y_t - baseline_t) / MAD_t
```

Recommended default:

```text
W = 13 weeks
minimum prior history = 8 weeks
threshold |robust_z| >= 3.5
```

These are WayLoom engineering values.

## MAD = 0 handling

Do not divide by zero.

Recommended policy:

- if MAD == 0 and current equals baseline → score 0;
- if MAD == 0 and current differs materially → flag via deterministic zero-MAD rule and record score unavailable/inf-safe status.

Do not create numerical infinity in stored report fields.

## Secondary detector

An IQR-based whole-series diagnostic may be included:

```text
Q1 - 1.5*IQR
Q3 + 1.5*IQR
```

but should be secondary because it ignores time order and trend.

## Required spike report fields

```text
depot
brand
iso_year
iso_week
week_start_date
spike_direction
spike_flag
rolling_history_n
rolling_median
rolling_mad
robust_z_or_status
secondary_iqr_flag
calendar_context_summary
```

Private report may include target values.

Tracked docs must not contain private weekly values.

## Context review

For each flagged week, attach aggregate context such as:

```text
has_festival
max_festival_ramp
has_payday
has_holiday
monsoon_day_fraction
operating_days
week_status
```

This helps distinguish plausible event-driven spikes from possible data-quality concerns.

## Critical rule

Do NOT:

```text
drop spike weeks
cap spike weeks
replace spike weeks
winsorize target
mark them invalid automatically
```

A spike can be the exact phenomenon the forecast must learn.

## Tests

Synthetic:

- obvious upward spike;
- obvious downward anomaly;
- flat series;
- MAD zero;
- insufficient history;
- trend without isolated spike;
- spike at festival context still retained;
- no mutation of target values.

## Definition of Done

- [ ] robust spike detector implemented;
- [ ] thresholds configurable;
- [ ] short-history/MAD-zero behavior tested;
- [ ] detected weeks retained unchanged;
- [ ] calendar context attached;
- [ ] warnings ready for Phase 13/14 decisions.

---

# 24. Feature-candidate handoff to Phase 13

Phase 12 should produce a structured private candidate table, but **must not yet implement the final forecasting features**.

Recommended schema:

```text
candidate
source
historical_signal
future_known_at_prediction_time
support
stability_warning
phase13_recommendation
reason
```

Allowed recommendation values:

```text
KEEP_CANDIDATE
KEEP_WITH_CAUTION
DEFER
DISABLE
```

Likely candidates to assess include:

```text
recent lag/rolling demand summaries
iso_week seasonal position
festival flag/name representation
festival_ramp
payday
holiday
monsoon
operating_days
```

Important:

A strong EDA relationship does **not** automatically make a feature safe.

Phase 13 must still prove that every feature is:

```text
past-known
or
target-week-known
```

without using unknown future actual demand.

---

# 25. Recommended `src/task2a/eda.py` architecture

Recommended pure functions:

```python
validate_task2a_eda_input(...)

build_weekly_calendar_context(...)

summarize_weekly_total_demand(...)

summarize_fresh_chilled_demand(...)

analyze_recent_trend(...)

analyze_yearly_seasonality(...)

analyze_festival_context(...)

analyze_festival_ramp(...)

analyze_payday_context(...)

analyze_holiday_context(...)

analyze_monsoon_context(...)

analyze_operating_days(...)

compare_same_week_across_years(...)

detect_weekly_spikes(...)

build_task2a_feature_candidate_table(...)

build_task2a_eda_warnings(...)

generate_task2a_eda(...)
```

Plot functions may be included separately if needed:

```python
plot_total_series(...)
plot_fresh_chilled(...)
plot_recent_trend(...)
plot_seasonality(...)
plot_calendar_context_comparison(...)
plot_same_week_comparison(...)
plot_spikes(...)
```

Keep computation separate from plotting where practical so logic can be unit tested without image comparison.

---

# 26. Input validation contract

Before any EDA:

Assert:

```text
weekly key unique:
  depot + brand + iso_year + iso_week

depot nonblank
brand in official brand domain
iso_year integer-like
iso_week valid official value
total_volume_m3 numeric finite >= 0
chilled_volume_m3 numeric finite >= 0
chilled_volume_m3 <= total_volume_m3
Style chilled == 0
Tech chilled == 0
week_status contains no unresolved blocker
chronology resolvable
```

Also verify weekly calendar context:

```text
calendar day keys unique
festival_ramp within [0,1]
is_payday in {0,1}
is_holiday in {0,1}
monsoon in {0,1}
is_operating in {0,1}
```

Do not silently coerce invalid official values into the expected range.

---

# 27. Statistical/reporting guidance

## Central tendency

For weekly volumes report both:

```text
mean
median
```

because demand may be skewed.

## Spread

Prefer:

```text
std
IQR
p90/p95
```

where sample size supports them.

## Correlation

If used for ramp/monsoon/operating-day analyses, prefer descriptive:

```text
Spearman
```

for monotonic relationships.

If a field is constant:

```text
correlation = unavailable
```

Do not crash or report misleading zero correlation.

## Confidence intervals

Optional.

Not required by the challenge.

If implemented, test them and label them as engineering/statistical aids.

## Multiple comparisons

Phase 12 is exploratory.

Do not convert many subgroup comparisons into formal “statistically significant” claims unless a predeclared statistical testing framework is introduced, which is not required here.

---

# 28. Required synthetic test suite

Create:

```text
tests/test_task2a_eda.py
```

All agent-run tests must use synthetic data.

## Input validation

- duplicate weekly key fails;
- negative total fails;
- NaN total fails;
- Inf total fails;
- chilled > total fails;
- Style chilled nonzero fails;
- Tech chilled nonzero fails;
- unresolved gap status fails;
- invalid ISO week fails.

## Weekly calendar context

- operating-day count;
- payday-day count;
- payday flag;
- holiday-day count;
- holiday flag;
- festival-day count;
- festival-name dedupe/sort;
- max festival ramp;
- mean festival ramp;
- ramp bounds;
- monsoon-day count;
- monsoon fraction;
- partial calendar coverage warning/failure.

## DT-192

- per-series summary;
- chronology across year boundary;
- confirmed zero retained.

## DT-193

- Fresh chilled series;
- chilled share;
- zero-total denominator;
- chilled invariant.

## DT-194

- increasing trend;
- decreasing trend;
- flat trend;
- insufficient history;
- zero prior mean.

## DT-195

- repeated ISO week across years;
- one-year insufficient support;
- week 53;
- normalized seasonal profile safe division.

## DT-196

- festival flag;
- blank festival;
- multiple names;
- small-support warning.

## DT-197

- ramp max/mean;
- ramp bins;
- exact 0/1;
- invalid ramp;
- constant correlation handling.

## DT-198

- payday week/no-payday week;
- multiple payday-day count if present in synthetic fixture.

## DT-199

- holiday week;
- holiday differs from festival;
- no forced equivalence.

## DT-200

- nonmonsoon;
- monsoon;
- mixed week;
- fraction.

## DT-201

- varying operating days;
- zero operating days;
- per-operating-day safe division;
- official calendar value used rather than weekday assumption.

## DT-202

- same-week two years;
- same-week three years;
- missing year;
- week 53;
- prior zero denominator;
- single-year unavailable.

## DT-203

- obvious upward spike;
- obvious downward spike;
- no spike;
- MAD zero;
- insufficient history;
- trending series;
- detector does not mutate targets;
- event-context fields attached.

## Privacy/reporting

- report does not emit row-level order IDs;
- tracked summary does not contain private weekly values;
- output paths are private.

---

# 29. Edge cases

## ISO week 53

Treat as a valid official week when supplied by `calendar.csv`.

Do not force all years to have week 53.

## Gregorian-year / ISO-year mismatch

Use official:

```text
iso_year + iso_week
```

not Gregorian year extracted from the date.

## Boundary partial week

If Phase 11 marks a boundary week partial/excluded, Phase 12 must honor that status.

Do not compare a partial boundary week with complete weeks as if equivalent.

## Confirmed zero demand week

Keep it.

A genuine zero is informative.

## Zero total Fresh week

Chilled must also be zero by invariant.

Chilled share is undefined, not infinity.

## One-year history for a seasonal week

Report insufficient repeat support.

Do not claim repeatable seasonality.

## Festival and holiday in same week

Both official contexts may be true.

Keep separate features/analyses.

## Multiple festival dates/names in one week

Keep deterministic set/list representation.

Do not arbitrarily choose the first festival.

## Week crossing monsoon boundary

Use day count/fraction rather than forcing binary all-week identity.

## Zero operating days with positive requested demand

Valid in principle because Task 2A history is requested demand, not successful dispatch volume.

Do not force volume to zero.

## Short series

Trend, spike, and same-week analysis must expose insufficient support rather than use unstable calculations.

## MAD = 0

Handle explicitly; never create uncontrolled infinity.

## Strong spike

Do not remove it.

## Very different depot/brand scales

Use per-series charts and optional normalized views.

Do not let one large series visually hide smaller series.

---

# 30. Phase 12 STOP conditions

`READY FOR PHASE 13` must remain **NO** if any of the following is true:

- Phase 11 has not passed;
- Phase 11 canonical weekly panel is bypassed/rebuilt differently;
- weekly panel contains duplicate series/week keys;
- weekly panel contains negative/nonfinite total volume;
- chilled > total;
- Style chilled is nonzero;
- Tech chilled is nonzero;
- unresolved Phase 11 gaps remain;
- official calendar mapping is replaced by an external calendar;
- festival/payday/holiday/monsoon values are invented externally;
- calendar aggregation uses incomplete weeks without explicit status handling;
- official `is_operating` is replaced by a weekday-only assumption;
- ISO week is used without ISO year for unique chronology;
- recent trend calculation uses future weeks for historical rows in a way later presented as a safe forecasting feature;
- same-week comparison fabricates missing years;
- spike detection mutates/removes target values;
- spike thresholds are tuned against future Task 2A outcomes;
- private competition-derived charts/tables are committed;
- tests fail;
- real local EDA run fails;
- independent Phase 12 review fails.

---

# 31. Phase 12 Definition of Done

Phase 12 passes only when:

- [ ] DT-192 PASS
- [ ] DT-193 PASS
- [ ] DT-194 PASS
- [ ] DT-195 PASS
- [ ] DT-196 PASS
- [ ] DT-197 PASS
- [ ] DT-198 PASS
- [ ] DT-199 PASS
- [ ] DT-200 PASS
- [ ] DT-201 PASS
- [ ] DT-202 PASS
- [ ] DT-203 PASS
- [ ] Phase 11 weekly panel reused unchanged
- [ ] weekly key uniqueness passes
- [ ] total/chilled invariants pass
- [ ] weekly calendar context generated from official `calendar.csv`
- [ ] total demand time series summarized for all depot/brand series
- [ ] Fresh chilled series summarized by depot
- [ ] recent trend analysis generated with explicit support rules
- [ ] annual/ISO-week seasonality analyzed with `n_years`
- [ ] festival analysis generated
- [ ] festival-ramp analysis generated
- [ ] payday analysis generated
- [ ] holiday analysis generated
- [ ] monsoon analysis generated
- [ ] operating-day analysis generated
- [ ] same-week-across-years comparison generated where supported
- [ ] robust weekly spike detection generated
- [ ] spike weeks remain unchanged
- [ ] feature-candidate handoff produced for Phase 13
- [ ] warnings generated
- [ ] private EDA report/figures generated locally
- [ ] all synthetic tests pass
- [ ] full safe regression suite passes
- [ ] `python -m pip check` passes
- [ ] private paths remain ignored
- [ ] Task 1 frozen artifacts remain untouched
- [ ] independent Phase 12 review passes
- [ ] no unresolved STOP condition remains

Then:

```text
PHASE 12 STATUS: PASS
READY FOR PHASE 13: YES
```

---

# 32. Git workflow

Recommended branch:

```bash
git checkout main
git pull
git checkout -b feature/phase-12-task2a-eda
```

Recommended commit sequence:

```text
feat(task2a): add weekly calendar EDA context
feat(task2a): add demand trend and seasonality analysis
feat(task2a): add calendar-event demand analysis
feat(task2a): add same-week and spike diagnostics
test(task2a): add synthetic Task 2A EDA coverage
docs(task2a): document Phase 12 exploratory methodology
```

Before staging:

```bash
git status
git diff
```

Never stage:

```text
data/raw/**
data/interim/**
reports/private/**
```

Verify ignore behavior, for example:

```bash
git check-ignore -v reports/private/phase12_task2a_eda/eda_summary.json
```

Before merge:

```bash
pytest -q tests/test_task2a_history.py tests/test_task2a_eda.py
pytest -q
python -m pip check
git status
```

If repository-wide `pytest -q` contains an explicitly documented real-data-only test, exclude only that specific test and record the exclusion.

Do not weaken tests merely to make the branch green.

---

# 33. Local execution command

Codex should implement but not execute the private real-data EDA in the external-agent context.

Recommended command:

```bash
python scripts/run_task2a_eda.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --history-config configs/task2a_history.yaml \
  --eda-config configs/task2a_eda.yaml \
  --output-dir reports/private/phase12_task2a_eda
```

PowerShell one-line form:

```powershell
python scripts/run_task2a_eda.py --weekly-panel data/interim/task2a_weekly_panel.csv --raw-root data/raw --manifest configs/dataset_manifest.yaml --history-config configs/task2a_history.yaml --eda-config configs/task2a_eda.yaml --output-dir reports/private/phase12_task2a_eda
```

The CLI should:

- validate Phase 11 panel contract first;
- resolve official calendar through the manifest/path layer;
- print only high-level status;
- never print private weekly volume tables;
- never print order IDs;
- write detailed results privately;
- return nonzero on hard validation failure.

Recommended sanitized local result:

```text
LOCAL PHASE 12 TASK2A EDA: PASS
SERIES COVERAGE: PASS
FRESH CHILLED EDA: PASS
RECENT TREND ANALYSIS: PASS
SEASONALITY ANALYSIS: PASS
CALENDAR CONTEXT ANALYSIS: PASS
SAME-WEEK COMPARISON: PASS
SPIKE DETECTION: PASS
TARGET MUTATION: NO
UNRESOLVED WARNINGS/BLOCKERS: 0
```

---

# 34. Ready-to-copy Codex implementation prompt

```text
You are implementing WayLoom Datathon PHASE 12 only.

PHASE:
Task 2A Exploratory Analysis

TASK RANGE:
DT-192 through DT-203

EXECUTION MODE:
Full-phase controlled autonomous implementation using SAFE synthetic tests.

You have permission to perform all safe engineering work required for Phase 12.

You MAY:

- create/edit/refactor Phase 12 tracked code
- create/edit configuration
- create/edit documentation
- create synthetic fixtures
- run targeted pytest tests
- run the full safe test suite
- inspect stack traces
- diagnose ordinary failures
- fix ordinary implementation bugs
- rerun failed tests
- run python -m pip check
- inspect git status/diff
- verify private paths are ignored
- self-review against the Phase 12 Definition of Done

Do NOT stop for normal coding/test failures that can safely be fixed.

STOP only for:

- official-rule ambiguity
- requirement to inspect restricted competition rows
- Phase 11 contract failure
- unresolved weekly-history/calendar inconsistency
- target mutation requirement
- genuine schema/data-quality blocker
- a change outside Phase 12 scope

DO NOT START PHASE 13.

==================================================
READ FIRST
==================================================

Read with targeted context:

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md
   - focus on Phase 12 and Task 2A global rules
4. PHASE_11_COMPETITION_CONTRACT.md
   - focus on canonical weekly panel semantics
5. PHASE_12_COMPETITION_CONTRACT.md
6. src/task2a/history.py
7. configs/task2a_history.yaml
8. configs/dataset_manifest.yaml
9. existing common IO/schema/validation utilities

Do NOT reread every Phase 00–10 contract unless a specific dependency requires it.

TASK 1 IS FROZEN.

Do not modify:

configs/task1_final_models.yaml
models/task1_service/**
models/task1_late/**
outputs/submission_task1.csv

==================================================
DATA BOUNDARY
==================================================

Do NOT inspect/print real competition rows from:

data/raw/**
data/interim/**
reports/private/**

Use synthetic fixtures for Codex-run tests.

The human will run the real Phase 12 EDA locally.

Do not print private weekly demand values in the final Codex summary.

==================================================
OFFICIAL TASK 2A CONTRACT
==================================================

Task 2A forecasts:

pred_total_volume_m3
pred_chilled_volume_m3

for supplied depot + brand + future ISO week rows.

Phase 11 already established the official historical rules:

- use deliveries_train.csv AND task1_test_inputs.csv
- count every unique requested order once
- retain attempted, deferred and not_run
- demand date = order_date
- official week = calendar.iso_year + calendar.iso_week
- only Fresh may have chilled demand
- Style chilled = exactly 0
- Tech chilled = exactly 0

Phase 12 MUST reuse the canonical Phase 11 weekly panel.

Do NOT rebuild demand history differently.

==================================================
CREATE / UPDATE
==================================================

Create/update:

src/task2a/eda.py
scripts/run_task2a_eda.py
configs/task2a_eda.yaml
docs/task2a_eda_method.md
tests/test_task2a_eda.py

Reuse existing common and Task 2A history utilities.

Private runtime outputs belong under:

reports/private/phase12_task2a_eda/**

==================================================
WEEKLY CALENDAR CONTEXT
==================================================

From official calendar.csv aggregate by:

iso_year
iso_week

Build deterministic weekly context:

calendar_days
operating_days
weekend_days
payday_days
has_payday
holiday_days
has_holiday
festival_days
has_festival
festival_names
max_festival_ramp
mean_festival_ramp
monsoon_days
monsoon_day_fraction
has_monsoon_day

Use official calendar values only.

DO NOT infer:

festivals from external calendars
paydays from day-of-month
operating days from weekday alone
monsoon from external weather data

Validate:

festival_ramp in [0,1]
is_payday in {0,1}
is_holiday in {0,1}
monsoon in {0,1}
is_operating in {0,1}

Do not silently clip invalid official values.

==================================================
DT-192 — WEEKLY TOTAL DEMAND
==================================================

For every depot + brand series:

validate chronology
validate unique week key
summarize:

n_weeks
start/end
mean
median
std
min
p25
p75
p90
p95
max

Generate weekly total-demand plot(s).

Keep confirmed zero weeks.

Do not mutate targets.

==================================================
DT-193 — FRESH CHILLED DEMAND
==================================================

Analyze Fresh only for nonzero chilled demand.

Per depot summarize:

n_weeks
mean chilled
median chilled
p90 chilled
max chilled
mean/median chilled share

chilled_share = chilled / total

If total == 0:
chilled_share = missing/undefined, not infinity.

Assert:

Fresh: 0 <= chilled <= total
Style: chilled == 0 exactly
Tech: chilled == 0 exactly

Generate Fresh chilled and total-vs-chilled plots.

==================================================
DT-194 — RECENT TREND
==================================================

Implement configurable descriptive windows:

4
8
13 weeks

Analyze:

rolling mean
rolling median
recent vs prior equal-length mean
absolute change
percent change when denominator valid
optional descriptive slope

Insufficient history must return explicit status.

Do not fabricate a trend.

Do not use future Task 2A actual demand.

==================================================
DT-195 — YEARLY SEASONALITY
==================================================

Analyze by:

depot + brand + iso_week

across iso_year.

Report:

n_years
mean
median
std
min
max

Require at least configured support (default 2 years) before calling a
seasonal pattern repeatable.

Support week 53 correctly.

Optional normalized seasonal analysis is allowed if documented as EDA.

==================================================
DT-196 — FESTIVAL EFFECTS
==================================================

Use official calendar festival field.

Weekly fields:

festival_days
has_festival
festival_names

Compare festival vs nonfestival weeks per series.

Report support n_weeks.

If breaking down by festival name, report support and do not overinterpret
single occurrences.

Use association language, not causal language.

==================================================
DT-197 — FESTIVAL-RAMP EFFECTS
==================================================

Use official festival_ramp daily field.

Weekly summaries:

max_festival_ramp
mean_festival_ramp

Default descriptive bins:

[0,0.25)
[0.25,0.50)
[0.50,0.75)
[0.75,1.0]

Report:

n_weeks
mean volume
median volume
p90 volume

Optional Spearman if supported.

Do not redefine ramp semantics.

==================================================
DT-198 — PAYDAY EFFECTS
==================================================

Weekly:

payday_days = sum(is_payday)
has_payday = payday_days > 0

Compare payday vs nonpayday weeks per series.

Use official calendar only.

==================================================
DT-199 — HOLIDAY EFFECTS
==================================================

Weekly:

holiday_days = sum(is_holiday)
has_holiday = holiday_days > 0

Compare holiday vs nonholiday weeks.

Keep holiday analysis distinct from festival analysis.

Do not assume festival == holiday in every case.

==================================================
DT-200 — MONSOON EFFECTS
==================================================

Weekly:

monsoon_days
monsoon_day_fraction
has_monsoon_day

Handle mixed-context weeks transparently.

Analyze total demand and optionally Fresh chilled.

Do not make causal claims.

==================================================
DT-201 — OPERATING DAYS
==================================================

Use:

operating_days = sum(calendar.is_operating)

Do NOT infer operating days from Monday-Saturday alone.

Analyze demand by operating-day count.

Optional secondary diagnostic:

total_volume_m3 / operating_days

only if operating_days > 0.

Zero operating-day weeks remain valid records.

Do not force requested demand to zero.

==================================================
DT-202 — SAME WEEK ACROSS YEARS
==================================================

For each:

depot + brand + iso_week

compare across iso_year.

Report:

n_years
year-over-year absolute change
percent change when denominator > 0
median same-week volume
variability

If n_years < 2:
mark comparison unavailable.

Support ISO week 53.

Do not fabricate missing years/weeks.

==================================================
DT-203 — ABNORMAL WEEKLY SPIKES
==================================================

Implement robust anomaly detection for EDA only.

Recommended primary detector per series:

trailing rolling median + MAD

Default engineering parameters:

window = 13 prior weeks
minimum prior history = 8
|robust_z| threshold = 3.5

Handle MAD == 0 safely.

Optional secondary IQR detector:

1.5 * IQR

Attach calendar context to flagged weeks:

has_festival
max_festival_ramp
has_payday
has_holiday
monsoon_day_fraction
operating_days
week_status

CRITICAL:

DO NOT:

drop spikes
cap spikes
winsorize spikes
replace spikes with rolling means
change historical target values

Spike detection is descriptive only.

==================================================
FEATURE-CANDIDATE HANDOFF
==================================================

Generate private feature_candidates.json/table with:

candidate
source
historical_signal
future_known_at_prediction_time
support
stability_warning
phase13_recommendation
reason

Allowed recommendation:

KEEP_CANDIDATE
KEEP_WITH_CAUTION
DEFER
DISABLE

This is not final feature engineering.

Phase 13 must still prove every actual feature is past-known or target-week-known.

==================================================
PLOTTING / REPORTING
==================================================

Generate private:

phase12_eda_report.md
eda_summary.json
warnings.json
feature_candidates.json
figures/

Keep computational logic testable separately from plotting.

Do not include row-level order IDs.

Do not commit private weekly-volume values to tracked docs.

Every grouped comparison must include sample support.

Use descriptive, non-causal wording.

==================================================
SYNTHETIC TESTS
==================================================

Implement comprehensive tests for:

weekly panel validation
calendar context aggregation
calendar coverage
weekly total series
Fresh chilled series
chilled share zero denominator
trend increasing/decreasing/flat/short history
seasonality repeated weeks/single-year/week53
festival flag/names
festival ramp max/mean/bins/bounds
payday aggregation
holiday aggregation
monsoon mixed week/fraction
operating-day counts/zero days
same-week across years/missing year/zero denominator
spike up/down/no spike/MAD zero/insufficient history/trend
spike target non-mutation
privacy-safe output paths

Use synthetic data only.

==================================================
AUTONOMOUS DEBUG LOOP
==================================================

After each logical batch:

1. run targeted tests
2. inspect failures
3. fix ordinary implementation defects
4. rerun failed tests
5. rerun tests/test_task2a_eda.py
6. continue only when clean

At the end run:

pytest -q tests/test_task2a_history.py tests/test_task2a_eda.py

Then:

pytest -q

Then:

python -m pip check

Then:

git status
git diff

If a documented test requires private real data, do not run it in Codex.
Report it for the human local run.

Verify these are not staged:

data/raw/**
data/interim/**
reports/private/**

==================================================
LOCAL REAL-DATA COMMAND
==================================================

Implement but DO NOT run against private competition data in Codex:

python scripts/run_task2a_eda.py \
  --weekly-panel data/interim/task2a_weekly_panel.csv \
  --raw-root data/raw \
  --manifest configs/dataset_manifest.yaml \
  --history-config configs/task2a_history.yaml \
  --eda-config configs/task2a_eda.yaml \
  --output-dir reports/private/phase12_task2a_eda

Console output must be sanitized.

Do not print private weekly tables/values.

==================================================
STOP CONDITIONS
==================================================

STOP if:

- Phase 11 contract is not passing
- canonical Phase 11 panel is rebuilt differently
- duplicate weekly keys exist
- targets are negative/nonfinite
- chilled invariants fail
- unresolved history gaps remain
- external calendar sources are introduced
- official calendar context is silently rewritten
- operating days are inferred from weekday instead of is_operating
- calendar weeks are incomplete without explicit handling
- spike detection changes target values
- missing historical years/weeks are fabricated
- future actual demand is required
- private competition data must be exposed
- tests cannot pass without violating approved contracts

==================================================
FINAL SELF-REVIEW
==================================================

Verify:

DT-192 READY
DT-193 READY
DT-194 READY
DT-195 READY
DT-196 READY
DT-197 READY
DT-198 READY
DT-199 READY
DT-200 READY
DT-201 READY
DT-202 READY
DT-203 READY

Phase 11 weekly panel reused
weekly key unique
chilled invariants pass
calendar context official
trend analysis support-aware
seasonality support-aware
festival analysis complete
festival-ramp analysis complete
payday analysis complete
holiday analysis complete
monsoon analysis complete
operating-day analysis complete
same-week analysis support-aware
spike detection robust and non-mutating
feature candidate handoff generated
all synthetic tests pass
full safe tests pass
pip check passes
private outputs ignored
Task 1 artifacts unchanged
no Phase 13 code added

==================================================
RETURN ONLY
==================================================

PHASE:
12 — AGENT IMPLEMENTATION STAGE

TASK STATUS:

DT-192 READY / FAIL
DT-193 READY / FAIL
DT-194 READY / FAIL
DT-195 READY / FAIL
DT-196 READY / FAIL
DT-197 READY / FAIL
DT-198 READY / FAIL
DT-199 READY / FAIL
DT-200 READY / FAIL
DT-201 READY / FAIL
DT-202 READY / FAIL
DT-203 READY / FAIL

FILES CREATED:
...

FILES MODIFIED:
...

TEST RESULTS:
...

PHASE 11 PANEL REUSE:
PASS / FAIL

WEEKLY KEY INTEGRITY:
PASS / FAIL

CHILLED INVARIANTS:
PASS / FAIL

OFFICIAL CALENDAR CONTEXT:
PASS / FAIL

TREND ANALYSIS:
PASS / FAIL

SEASONALITY ANALYSIS:
PASS / FAIL

CALENDAR EVENT ANALYSIS:
PASS / FAIL

SAME-WEEK COMPARISON:
PASS / FAIL

SPIKE DETECTION NON-MUTATION:
PASS / FAIL

FEATURE-CANDIDATE HANDOFF:
PASS / FAIL

TASK 1 FROZEN ARTIFACTS CHANGED:
MUST BE NO

PRIVATE DATA ACCESSED:
NO

HUMAN LOCAL ACTION REQUIRED:
YES

Print the exact local Phase 12 EDA command.

PHASE 12 STATUS:
AWAITING LOCAL TASK2A EDA RUN

READY FOR PHASE 13:
NO

Then STOP.

Do not start Phase 13.
```

---

# 35. Independent Codex Phase 12 review prompt

Run this in a **fresh Codex session** after the human local Phase 12 command passes.

```text
Perform an independent review of completed WayLoom Datathon PHASE 12.

PHASE:
Task 2A Exploratory Analysis

TASK RANGE:
DT-192 through DT-203

REVIEW MODE:
Read-only first.
Do not modify implementation unless explicitly asked after the review.

DO NOT:

- access data/raw/**
- access data/interim/**
- access reports/private/**
- print private weekly demand values
- alter Task 1 artifacts
- implement Phase 13

==================================================
READ
==================================================

1. AGENTS.md
2. CODEX_HANDOFF_PHASE_11_ONWARDS.md
3. WAYLOOM_DATATHON_MASTER_PLAN.md — Phase 12 section
4. PHASE_11_COMPETITION_CONTRACT.md — relevant panel contract
5. PHASE_12_COMPETITION_CONTRACT.md
6. src/task2a/eda.py
7. scripts/run_task2a_eda.py
8. configs/task2a_eda.yaml
9. docs/task2a_eda_method.md
10. tests/test_task2a_eda.py
11. relevant Phase 11 history utilities/config
12. .gitignore
13. AGENTS.md / any ignore configuration used by the development agent

HUMAN LOCAL SANITIZED RESULT:

LOCAL PHASE 12 TASK2A EDA: <PASS / FAIL>
SERIES COVERAGE: <PASS / FAIL>
FRESH CHILLED EDA: <PASS / FAIL>
RECENT TREND ANALYSIS: <PASS / FAIL>
SEASONALITY ANALYSIS: <PASS / FAIL>
CALENDAR CONTEXT ANALYSIS: <PASS / FAIL>
SAME-WEEK COMPARISON: <PASS / FAIL>
SPIKE DETECTION: <PASS / FAIL>
TARGET MUTATION: <NO / YES>
UNRESOLVED WARNINGS/BLOCKERS: <number>

Do not ask for private report contents if these sanitized controls are enough.

==================================================
AUDIT TASK BY TASK
==================================================

DT-192
Verify total demand EDA is per depot+brand, chronological, support-aware,
and target-preserving.

DT-193
Verify only Fresh can have nonzero chilled demand, chilled<=total, and
zero-total share is safe.

DT-194
Verify recent-trend windows are configurable, short history is explicit,
and no future demand is used.

DT-195
Verify seasonality uses official iso_week across iso_year, handles week 53,
and requires repeated-year support before claiming repeatability.

DT-196
Verify festival context comes only from official calendar, names are
handled deterministically, and support counts are reported.

DT-197
Verify official festival_ramp semantics/range are preserved and weekly
max/mean are correctly aggregated.

DT-198
Verify payday comes from calendar.is_payday, not date heuristics.

DT-199
Verify holiday comes from calendar.is_holiday and remains distinct from
festival analysis.

DT-200
Verify monsoon comes from official calendar and mixed weeks use day
count/fraction rather than forced binary simplification.

DT-201
Verify operating days use calendar.is_operating, not weekday assumptions,
and zero operating-day weeks are handled safely.

DT-202
Verify same-week comparison uses iso_year+iso_week semantics, requires at
least two years, handles zero denominator and week 53, and does not
fabricate missing years.

DT-203
Verify spike detection is robust/configurable, handles MAD=0 and short
history, attaches calendar context, and NEVER mutates/removes target weeks.

==================================================
GLOBAL REVIEW
==================================================

Verify:

- Phase 11 canonical panel is consumed, not rebuilt differently
- no official historical demand rules are changed
- private outputs stay under reports/private
- no private values are stored in tracked docs/tests
- calendar context comes only from official calendar
- every grouped analysis reports support
- no causal claims are encoded as conclusions
- feature candidate handoff is advisory only
- Phase 13 forecasting features are not implemented prematurely
- Task 1 frozen artifacts are untouched

Run safe tests:

pytest -q tests/test_task2a_history.py tests/test_task2a_eda.py

then if safe:

pytest -q

then:

python -m pip check

git status

Do not execute real-data EDA.

==================================================
RETURN
==================================================

Return a table:

| Task | Requirement | PASS/FAIL | Evidence | Blocking fix |

Then:

PHASE 11 PANEL REUSE:
PASS / FAIL

WEEKLY CALENDAR CONTEXT:
PASS / FAIL

TARGET INTEGRITY:
PASS / FAIL

TREND ANALYSIS:
PASS / FAIL

SEASONALITY ANALYSIS:
PASS / FAIL

EVENT/CALENDAR ANALYSIS:
PASS / FAIL

SAME-WEEK ANALYSIS:
PASS / FAIL

SPIKE DETECTION:
PASS / FAIL

FEATURE-CANDIDATE HANDOFF:
PASS / FAIL

SYNTHETIC TESTS:
PASS / FAIL

HUMAN LOCAL EDA:
PASS / FAIL

DATA SAFETY:
PASS / FAIL

DT-192: PASS / FAIL
DT-193: PASS / FAIL
DT-194: PASS / FAIL
DT-195: PASS / FAIL
DT-196: PASS / FAIL
DT-197: PASS / FAIL
DT-198: PASS / FAIL
DT-199: PASS / FAIL
DT-200: PASS / FAIL
DT-201: PASS / FAIL
DT-202: PASS / FAIL
DT-203: PASS / FAIL

BLOCKERS:
...

NON-BLOCKING IMPROVEMENTS:
...

PHASE 12 REVIEW:
PASS / FAIL

READY FOR PHASE 13:
YES / NO

If FAIL, list exact blockers only.

Do not automatically fix them.
Do not start Phase 13.
```

---

# 36. Human local review checklist

After Codex implements Phase 12:

1. Run synthetic tests.
2. Run the local private EDA command.
3. Open the private report/figures locally.
4. Confirm no chart is obviously generated from a partial/unresolved week.
5. Confirm each depot/brand series is visible and not hidden by scale.
6. Confirm Fresh chilled is plausible and never above Fresh total.
7. Confirm Style/Tech chilled remain exactly zero.
8. Confirm trend conclusions have enough history.
9. Confirm seasonal claims show number of years.
10. Confirm festival/payday/holiday/monsoon/operating-day groups include support counts.
11. Confirm same-week comparisons do not invent absent years/week 53.
12. Confirm detected spikes remain unchanged in the panel.
13. Confirm no private EDA outputs are tracked by Git.
14. Run the independent Codex review.

Only then move to Phase 13.

---

# 37. Completion record template

```markdown
# Phase 12 Completion Record

## Tasks

- [ ] DT-192
- [ ] DT-193
- [ ] DT-194
- [ ] DT-195
- [ ] DT-196
- [ ] DT-197
- [ ] DT-198
- [ ] DT-199
- [ ] DT-200
- [ ] DT-201
- [ ] DT-202
- [ ] DT-203

## Agent implementation

- Phase 11 panel reused: PASS / FAIL
- Synthetic tests: PASS / FAIL
- Full safe suite: PASS / FAIL
- pip check: PASS / FAIL
- Private paths protected: PASS / FAIL

## Local EDA

- Local run: PASS / FAIL
- Weekly total demand plots: PASS / FAIL
- Fresh chilled plots: PASS / FAIL
- Trend analysis: PASS / FAIL
- Seasonality analysis: PASS / FAIL
- Festival analysis: PASS / FAIL
- Festival-ramp analysis: PASS / FAIL
- Payday analysis: PASS / FAIL
- Holiday analysis: PASS / FAIL
- Monsoon analysis: PASS / FAIL
- Operating-day analysis: PASS / FAIL
- Same-week comparison: PASS / FAIL
- Spike detection: PASS / FAIL
- Target mutation: NO / YES
- Unresolved blockers: 0 / <count>

## Safety

- Real competition rows exposed to agent: NO
- Task 1 frozen artifact changed: NO
- Private EDA committed: NO

## Review

- Independent Phase 12 review: PASS / FAIL

## Verdict

PHASE 12 STATUS: PASS / FAIL
READY FOR PHASE 13: YES / NO
```

---

# 38. Final Phase 12 checklist

Before Phase 13:

- [ ] `DT-192` complete.
- [ ] `DT-193` complete.
- [ ] `DT-194` complete.
- [ ] `DT-195` complete.
- [ ] `DT-196` complete.
- [ ] `DT-197` complete.
- [ ] `DT-198` complete.
- [ ] `DT-199` complete.
- [ ] `DT-200` complete.
- [ ] `DT-201` complete.
- [ ] `DT-202` complete.
- [ ] `DT-203` complete.
- [ ] Phase 11 canonical panel reused.
- [ ] Official weekly calendar context used.
- [ ] All series have support/date summaries.
- [ ] Fresh chilled invariants pass.
- [ ] Trend analysis is support-aware.
- [ ] Seasonality includes `n_years`.
- [ ] Festival context uses official calendar.
- [ ] Festival ramp uses official 0–1 semantics.
- [ ] Payday uses official `is_payday`.
- [ ] Holiday uses official `is_holiday`.
- [ ] Monsoon uses official `monsoon`.
- [ ] Operating days use official `is_operating`.
- [ ] Same-week comparison handles week 53/missing years.
- [ ] Spike detector does not mutate targets.
- [ ] Feature-candidate handoff created.
- [ ] Private report/figures generated locally.
- [ ] Synthetic tests pass.
- [ ] Full safe tests pass.
- [ ] `pip check` passes.
- [ ] Task 1 final artifacts untouched.
- [ ] Private outputs ignored.
- [ ] Independent review passes.

Only then:

```text
PHASE 12 STATUS: PASS
READY FOR PHASE 13: YES
```

Do not automatically begin Phase 13.
