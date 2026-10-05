# Phase 21 priority specification

This is WayLoom engineering policy, not organizer-mandated priority order.
The metadata builder is allocation-free and emits exactly one row per
`order_ref`. Hard feasibility is a gate before the objective is compared.

## Classification and lineage

| rule or signal | classification | source | can be violated? | phase enforced | notes |
|---|---|---|---|---|---|
| same brand and district per trip | HARD_OFFICIAL | Phase 18/20 contract | No | Phase 22 | trip feasibility |
| chilled requires reefer | HARD_OFFICIAL | Phase 19 contract | No | Phase 19/22 | compatibility |
| van-only requires van | HARD_OFFICIAL | Phase 19 contract | No | Phase 19/22 | compatibility |
| home-depot match | HARD_OFFICIAL | Phase 18/19 contract | No | Phase 19/22 | Peliyagoda S1 |
| whole order | HARD_OFFICIAL | Phase 18 contract | No | Phase 22 | no split delivery |
| weight and volume capacity | HARD_OFFICIAL | Phase 18/19 contract | No | Phase 19/22 | vehicle capacity |
| maximum trips and time budgets | HARD_OFFICIAL | Phase 20 contract | No | Phase 20/22 | trip feasibility |
| `deferred_yesterday` | SOFT_POLICY | S1 order history | Yes | Phase 21/22 | fairness tier 2 |
| `days_since_last_served` | SOFT_POLICY | S1 order history | Yes | Phase 21/22 | fairness tier 3 |
| low compatible-vehicle count | SOFT_POLICY | Phase 19 matrix | Yes | Phase 21/22 | fairness tier 4 |
| Fresh chilled | SOFT_POLICY | S1 brand/context | Yes | Phase 21/22 | business tier 5 |
| Fresh | SOFT_POLICY | S1 brand/context | Yes | Phase 21/22 | business tier 6 |
| avoidable specialized use | SOFT_TIEBREAKER | Phase 19 matrix | Yes | Phase 21/22 | stewardship tiers 7A–7C |
| unique-outlet counts | DIAGNOSTIC_ONLY | policy metrics | Yes | Phase 21/23 | does not merge orders |

The policy cannot override any `HARD_OFFICIAL` rule. `hard_feasible=False`
always loses to `hard_feasible=True` before any objective tier is compared.

## Objective

Among hard-feasible plans, compare lexicographically in this exact order:

1. maximize served orders;
2. maximize served previous-deferred orders;
3. maximize served waiting-days sum;
4. maximize served low-flexibility orders;
5. maximize served Fresh chilled orders;
6. maximize served Fresh orders;
7. minimize avoidable reefer-van assignments;
8. minimize avoidable reefer assignments;
9. minimize avoidable van assignments.

No arbitrary weighted score is used.
