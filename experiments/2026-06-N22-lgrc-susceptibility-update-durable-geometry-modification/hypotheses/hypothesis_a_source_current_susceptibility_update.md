# Hypothesis A - Source-Current Susceptibility Update

N22 can produce source-backed evidence that prior interaction changes later
route, boundary, corridor, or region susceptibility in LGRC-visible geometry.

Support requires:

```text
N20 I5 susceptibility_update contract consumed without redefinition
N21 closeout consumed as prerequisite context only
interaction window declared before use
later re-entry window declared before use
source_current_inputs recorded
row_specific_thresholds_declared_before_use = true
pre_interaction_geometry_trace present
post_interaction_geometry_trace present
susceptibility_delta_trace present
route_or_region_reentry_trace present
allowed_delta_fields declared
same_basin_invariant_fields preserved
out_of_scope_drift_blocks_row = true
delta_not_label_reassignment = true
peer_same_budget_comparison present when route or region conditioning is claimed
same-basin continuation preserved
support/coherence/boundary/flux gates preserved
derived_report_only = false
route label alone not used as evidence
reinforcement schedule alone not used as evidence
unsafe claim flags false
```

Failure conditions:

```text
route label changes without source-current geometry change
post-interaction delta is report-built or post-hoc
susceptibility update is inferred only from producer schedule
N21 WR/ND closeout is treated as susceptibility evidence
same-budget peer route or region shows the same delta and the row is still
claimed as target-route susceptibility
out-of-scope drift is treated as valid update
support/coherence/boundary/flux gates fail
semantic learning, choice, intention, agency, or native support labels are used
as evidence
```
