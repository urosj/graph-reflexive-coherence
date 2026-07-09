# N30 Outputs

Selected N30 output artifacts will be stored here when they are part of the
historical evidence record.

## Iteration Artifacts

- `n30_source_inventory_i1.json`: source inventory and method admission. It
  pins shared-medium method documents by digest and keeps positive N30 evidence
  closed.
- `n30_schema_control_freeze_i2.json`: participant/medium schema freeze. It
  freezes P0-P7, M0-M6, N30-C0-N30-C6, required candidate fields, controls,
  replay gates, medium debt, and claim boundaries.
- `n30_active_nulls_i3.json`: active-null and failure-baseline matrix. It
  instantiates the I2 control IDs, maps each null to a blocked gate/rung and
  dependent hypothesis, and keeps positive N30 evidence closed.
- `n30_participant_admissibility_i4.json`: first participant-only positive
  content artifact. It consumes underlying N27 source-current traces and replay
  records to support a bounded P2 participant-admissibility candidate while
  keeping medium-relation and shared-medium claims closed.
- `n30_participant_admissibility_i4_artifacts/`: supporting threshold,
  carrier-state, attribution, replay-recognizability, label-drift, and I4
  medium-leakage guard traces.
- `n30_participant_admissibility_i4a.json`: P2 participant-admissibility
  strengthening artifact. It consumes the N27 topology/fixture variant traces
  to show a second recognizable participant carrier under a branched/folded
  topology shape while keeping medium-relation and shared-medium claims closed.
- `n30_participant_admissibility_i4a_artifacts/`: supporting threshold,
  carrier-state, attribution, replay-recognizability, label-drift,
  topology-variant strengthening, and I4-A medium-leakage guard traces.
- `n30_participant_boundary_support_i4b.json`: participant boundary/support
  sensitivity artifact. It consumes the N27 stress/mapping-variant matrix to
  preserve I4 as boundary-limited and support the I4-A carrier as a bounded P4
  participant candidate while keeping medium-relation claims closed.
- `n30_participant_boundary_support_i4b_artifacts/`: supporting stress-policy,
  sensitivity-matrix, P4-candidate, stress-limited, and I4-B
  medium-leakage guard traces.
- `n30_medium_surface_trace_i5.json`: first medium-surface positive artifact.
  It consumes the N28 I4-A source-current focal/neighbor traces and replay
  record to declare the neighbor capacity shell as a shared-local medium
  surface with a replay-persistent surface change, while keeping later
  eligibility and minimal shared-medium participation claims closed.
- `n30_medium_surface_trace_i5_artifacts/`: supporting medium-surface
  declaration, participant/medium separation, perturbation, surface-change,
  trace persistence/debt, scope-classification, and I5 claim-boundary guard
  traces.
- `n30_medium_surface_trace_i5a.json`: mechanism-diverse M1 strengthening
  artifact. It consumes the N28 I4-A2 split-shell / delayed-boundary
  mechanism-diversity row and replay trace as a second shared-local medium
  surface candidate, without replacing I5 or opening later-eligibility claims.
- `n30_medium_surface_trace_i5a_artifacts/`: supporting I5-A medium-surface
  declaration, participant/medium separation, perturbation, surface-change,
  trace persistence/debt, scope-classification, claim-boundary guard, and
  I5-vs-I5-A comparison traces.
- `n30_medium_surface_scope_window_i5b.json`: medium-surface persistence /
  scope-window audit. It consumes I5, I5-A, and N28 neighbor-capacity stress
  rows to support local split-shell scope and replay/stress-variant
  persistence while blocking temporal decay, slow-trace, C5/M2, and minimal
  shared-medium participation claims.
- `n30_medium_surface_scope_window_i5b_artifacts/`: supporting window policy,
  scope-window matrix, persistence/decay limit, and I5-B claim-boundary guard
  traces.
- `n30_later_eligibility_i6.json`: later eligibility / susceptibility probe.
  It consumes I5, I5-A, I5-B, and the N28 same-policy transition traces to
  support provisional M2 input evidence while keeping final N30-C5/C6 and
  minimal shared-medium participation claims blocked pending I7 controls.
- `n30_later_eligibility_i6_artifacts/`: supporting susceptibility or
  eligibility traces, coupled relation-lineage traces, aggregate later
  eligibility trace, and I6 claim-boundary guard.
- `n30_later_eligibility_margin_i6a.json`: later-eligibility contrast-margin
  probe. It consumes I6 and shows that the provisional M2 dependency is more
  clearly separated from neutral-gap and extractive-cross counterfactuals than
  the narrow threshold margin alone indicates, while preserving the no-C5
  closeout boundary.
- `n30_later_eligibility_margin_i6a_artifacts/`: supporting contrast-threshold
  policy, contrast-margin matrix, and I6-A claim-boundary guard.
