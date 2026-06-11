# Phase T-GRC9 Collapse-Adjacent Observability Review

## Purpose

This review records the Phase T-GRC9 decision for the next GRCL-9
collapse-adjacent work batch.

The question is not whether GRC9 should import GRCV3 choice/collapse
semantics. It should not. The question is whether current Phase T-GRC9
telemetry can support structural probes for collapse-adjacent GRCL-9 source
structures such as membrane/ridge weakening, basin merge pressure, support
loss, sink dominance loss, or failed fission persistence.

## Decision

Phase T-GRC9 accepts **selector-backed structural diagnostics over existing
telemetry and checkpoints** for the next GRCL-9 batch.

Phase T-GRC9 does not add, in this pass:

- a `collapse` lifecycle event domain,
- a `collapse_evidence` event group,
- a `collapse_candidate_summary` run-summary group,
- GRCV3 `choice` / `collapse_registry` semantics,
- or a reinterpretation of identity fission as collapse.

The next GRCL-9 batch should first run structural probes against the existing
Phase T-GRC9 surface. New compact telemetry fields should be considered only
after those probes expose a concrete selector failure or artifact-size problem.

## Accepted Existing Evidence

The following evidence surfaces are accepted for collapse-adjacent selectors in
the next GRCL-9 batch.

### Failed Fission Persistence

Status: artifact-backed.

Use:

- `family_extensions.grc9.expansion_summary.identity_fission_candidate_count`
- `family_extensions.grc9.expansion_summary.identity_fission_confirmed_count`
- `family_extensions.grc9.expansion_summary.identity_fission_max_persistence_steps`
- `family_extensions.grc9.diagnostic_status_summary.identity_fission_confirmed`

Interpretation:

- candidate present with confirmed count zero may support a
  failed-persistence structural probe,
- it is not collapse,
- it is not GRCV3 hierarchy.

### Sink And Basin Change Pressure

Status: selector-backed over step rows and checkpoints.

Use:

- `family_extensions.grc9.identity_abundance.sink_count`
- `family_extensions.grc9.identity_abundance.basin_count`
- `family_extensions.grc9.identity_abundance.basin_size_min`
- `family_extensions.grc9.identity_abundance.basin_size_max`
- `family_extensions.grc9.identity_abundance.basin_size_mean`
- `family_extensions.grc9.identity_abundance.basin_mass_summary` when emitted
- graph checkpoint sink/basin overlays when present

Interpretation:

- selectors may compare windows for sink-count loss, basin-count decrease, or
  dominance concentration,
- no first-class `sink_loss` or `basin_merge` telemetry is emitted yet,
- source-side labels must remain `basin_merge_candidate` or
  `sink_loss_candidate`.

### Transport And Support Pressure

Status: selector-backed over step rows and checkpoints.

Use:

- `family_extensions.grc9.transport.conductance_min`
- `family_extensions.grc9.transport.conductance_max`
- `family_extensions.grc9.transport.conductance_mean`
- `family_extensions.grc9.transport.flux_abs_sum`
- `family_extensions.grc9.transport.flux_signed_balance`
- `family_extensions.grc9.transport.strongest_flux_edges_sample`
- graph checkpoint edge conductance/flux records when present

Interpretation:

- selectors may compare support weakening, strong-path loss, or asymmetric
  support concentration,
- role semantics such as membrane, ridge, or bridge come from GRCL-9
  provenance/checkpoint labels, not from the generic Phase T-GRC9 contract,
- no first-class `support_loss_candidate_count` is emitted yet.

### Membrane Or Ridge Rupture Structure

Status: structural/checkpoint-backed only.

Use:

- graph checkpoint topology,
- GRCL-9 lowered motif roles and source provenance,
- port occupancy and edge conductance records.

Interpretation:

- Phase T-GRC9 can expose the graph facts,
- GRCL-9 may interpret those graph facts as a source-authored membrane/ridge
  structural probe,
- Phase T-GRC9 does not define membrane semantics.

## Deferred Compact Fields

The following names remain reserved for a later compact diagnostic extension if
the next GRCL-9 probe batch proves they are needed:

- `structural_integrity_summary`
- `basin_merge_candidate_count`
- `sink_loss_candidate_count`
- `membrane_rupture_candidate_count`
- `support_loss_candidate_count`
- `collapse_candidate_summary`

If added later, they should be diagnostic-only fields or part of a new contract
version. They must not silently change `phase_t_grc9_iter1_v1`.

## Selector Guidance For GRCL-9 Iteration 8.1

The next GRCL-9 batch should use selector names that preserve diagnostic
status:

- `fission_persistence_failed_candidate`
- `basin_merge_pressure_candidate`
- `sink_loss_pressure_candidate`
- `support_loss_pressure_candidate`
- `membrane_rupture_structural_probe`
- `collapse_reserved_future`

Selectors should report:

- evidence field paths queried,
- time/window compared,
- checkpoint ids used when topology is required,
- whether the result is `artifact_backed`, `structural_only`, or
  `reserved_future`.

## Non-Claims

- This review does not add runtime collapse to GRC9.
- This review does not import GRCV3 choice/collapse semantics.
- This review does not make ComposingCells dysfunction a solved GRC9 event.
- This review does not reinterpret identity fission as collapse.
