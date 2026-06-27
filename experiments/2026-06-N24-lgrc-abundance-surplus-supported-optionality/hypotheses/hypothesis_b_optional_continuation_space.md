# Hypothesis B - Optional Continuation Space Under Preserved Basin Integrity

N24 can produce source-backed evidence that surplus above the maintenance floor
opens optional continuation space while the maintenance basin remains intact.

Support requires:

```text
Hypothesis A support gates preserved
optional_continuation_set_trace present
original optional continuation set is recorded in the same source-current run
declared replay family validates replay/stress behavior but does not create the
original AB3 optional set
at least two optional continuation records are source-current and auditable
optional_continuation_availability_count >= 2 for AB3+
jointly_admissible_optional_continuation_count >= 2 for AB5+
optional continuations are recorded in the declared optionality window
optional continuations are branch-distinguishable in support/coherence,
boundary, or flux traces
optional branch records follow the frozen optional_branch_record schema
maintenance support floor remains preserved while optional branches are open
maintenance coherence floor remains preserved while optional branches are open
boundary_integrity_under_optionality_trace remains above floor
optional flux does not drain maintenance support below floor
residual_support_margin_under_optionality remains positive
residual_coherence_margin_under_optionality remains positive
same-basin continuation rule preserved
optional branch telemetry is not label-only
artifact replay passes
snapshot/load replay passes where applicable
duplicate replay passes where applicable
hidden-budget, proxy-only, floor-crossing, optional-label-only, and post-hoc
controls fail closed
surplus-without-optionality, optionality-without-surplus, independent-run
assembly, maintenance-basin-shift, and floor-renormalization controls fail
closed or demote as specified
```

Failure conditions:

```text
only one continuation exists and is relabeled as optionality
optional branches are labels without source-current traces
optional branches are assembled across independent runs
optional branches open only because hidden producer budget is added
optional branch count improves while maintenance floor, boundary, or flux gates
fail
surplus exists but no optional continuation set opens and the row is promoted
above AB2
optional branches exist without surplus above the maintenance floor
reward/proxy gain replaces same-basin continuation
N23 counterfactual branches are relabeled as N24 surplus optionality without
new surplus evidence
```
