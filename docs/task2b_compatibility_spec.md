# Task 2B Phase 19 compatibility

The matrix grain is `order_ref + vehicle_id`, covering every S1 order and every
available Peliyagoda-home vehicle. Each pair independently records refrigeration,
van-access, home-depot, weight, and volume checks, plus deterministic failure codes.
Incompatible pairs remain in the matrix. Scarcity outputs are diagnostics only:
they do not reserve vehicles, make priority decisions, create trips, or prove
full-day feasibility.
