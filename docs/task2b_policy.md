# WayLoom Task 2B Prioritization Policy

## Allocation objective

This is a WayLoom engineering policy, not an organizer-mandated priority rule. Official feasibility always dominates priority. Among feasible allocations, WayLoom first maximized the number of served orders; ties then favored previously deferred demand, greater waiting days, low-flexibility orders, Fresh chilled demand, and Fresh demand. Only after those coverage and fairness tiers tied did it conserve avoidable reefer-van, reefer, and van use.

The frozen plan serves 79 of 85 orders (92.9%) and defers 6 (7.1%). Served and deferred decisions remain at `order_ref` grain; repeated outlets are not collapsed.

## Feasibility and calculation method

Every served order is assigned whole to one available home-depot vehicle and trip. A trip contains one brand and district; chilled demand requires a reefer, `van_only` demand requires a van, and both weight and volume capacities apply. Each vehicle uses at most two trips. Trip time is calculated as:

`trip_minutes = outbound + inter_stop * (n_orders - 1) + sum(service_allowance_min)`

Outbound travel is counted once, handling is included for every stop, and no return journey is added. A vehicle's combined Fresh trips must stay within 270 minutes, while its combined Style+Tech trips must stay within 480 minutes.

## Limiting resources

The usable home-depot fleet contained 28 vehicles, including 4 reefers and 1 reefer vans; 10 listed vehicles were unavailable in the workshop. The plan used 44 of the theoretical 56 available trip slots. The highest per-vehicle use was 268 of 270 Fresh minutes and 183 of 480 Style+Tech minutes. Peak trip loading reached 99.2% by weight and 99.7% by volume. Hard vehicle compatibility was a demonstrated direct limiter: 1 deferred orders had no compatible available vehicle for the whole order. These are aggregate indicators of constraint pressure; they are not an unsupported counterfactual claim that one resource alone caused every deferral.

## Deferral rationale

Orders with no compatible available vehicle were directly unavoidable under the hard constraints. The remaining 5 deferred orders each had at least one compatible vehicle in isolation, but that does not mean they could be added without a tradeoff. Their deferral reflects competition for legal brand-district trips, whole-order capacity, trip slots, and vehicle time under the frozen allocation. Under equal feasibility, the frozen lexicographic policy selected service by total coverage, prior deferral, waiting time, low flexibility, Fresh chilled/Fresh demand, and specialized-vehicle conservation - not by an AI-generated discretionary rule.

Of 10 previously deferred orders, 9 are served and 1 remain deferred. Deferred demand by brand is Fresh 5, Style 1.

## Operational cost and impact

The 6 deferrals affect 6 outlets and represent 1,188 units, 9,770.9 kg, and 81.57 m3. This includes 5 chilled orders totaling 40.91 m3. Deferred orders have a mean wait of 2 days and a maximum of 5 days since last service.

The supplied data contains no monetary cost field, so this policy reports deferral impact operationally rather than inventing a currency estimate.
