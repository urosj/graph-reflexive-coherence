# Hypothesis B - Source-Current Collapse And Replay

N23 can distinguish live-continuation collapse from post-hoc selection by
showing that a live branch set resolves into one source-current continuation
while the non-selected branches remain auditable as counterfactual
alternatives.

Support requires:

```text
pre_collapse_live_branch_set_trace present
collapsed_continuation_trace present
counterfactual_branch_retention_trace present
counterfactual retention is immutable pre-collapse audit evidence
selected_branch_source_current_reason recorded
selected_branch_source_current_reason is one of the frozen source-current
geometry reasons
producer_selected_branch_label_absent = true
producer_preference_injection_absent = true
collapse window declared before use
branch_window.end_step <= collapse_window.start_step
selected branch reason computed from traces available before or during the
collapse window
artifact replay passes
snapshot/load replay passes
duplicate replay stable where applicable
order-inversion or post-hoc stitching controls fail closed
fake-alternative control fails closed
single-branch relabel control fails closed
random-tie-as-collapse control fails closed
producer preference injection control fails closed
same-basin continuation remains inside declared floors
```

Failure conditions:

```text
collapsed continuation is present but live branch set is missing
non-selected branches are not retained as auditable counterfactuals
counterfactual retention contains only labels, producer alternatives,
replay-created branches, or report-side reconstruction
selected branch is assigned by producer label or hidden preference
collapse appears only after report-side reconstruction
random tie is interpreted as geometry-conditioned collapse
replay diverges without declared scope reason
support/coherence/boundary/flux floors are crossed
```
