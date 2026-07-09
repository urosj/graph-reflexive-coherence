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
