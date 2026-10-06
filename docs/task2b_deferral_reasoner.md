# Explainable Deferral Reasoner

WayLoom’s optional Phase 26 hero feature explains a frozen Task 2B deferral without changing the official allocation. It distinguishes three outcomes:

- **Hard-unavoidable:** no legal forced allocation can serve the order under the frozen hard constraints.
- **Policy tradeoff:** the order is legally servable, but forcing it worsens the frozen nine-tier WayLoom policy objective.
- **Alternative optimum:** an equally policy-optimal allocation can serve it, so the frozen allocation represents one of several equivalent choices.

The reasoner starts with whole-order compatibility and exact one-order trip time, then checks whether the order could be inserted directly into the frozen plan. A direct insertion would contradict the frozen maximum-coverage proof and is treated as a blocker. Otherwise, the reasoner forces the order served in the approved Phase 22 model, proves every Phase 21 objective stage, and—when feasible—finds the closest allocation witness after fixing the forced policy vector.

Resource explanations such as weight/volume competition, trip-slot pressure, Fresh or Style/Tech time limits, and reefer or reefer-van scarcity appear only when the diagnostic evidence supports them. A chilled requirement alone is not called a scarcity bottleneck.

Detailed order-level evidence remains private. Competition-facing examples are deterministic, limited to two, and anonymized as `DEFERRAL_EXAMPLE_A` and `DEFERRAL_EXAMPLE_B`.

These explanations are solver counterfactuals under the frozen Task 2B assumptions. They identify optimization constraints and policy tradeoffs, not real-world causal effects or guaranteed operational outcomes. The official allocation checker establishes feasibility, not optimality.
