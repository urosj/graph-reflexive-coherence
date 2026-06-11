# Phase T GRC9 Implementation Plan

This document is the detailed execution plan for **Phase T-GRC9: GRC9
Mechanical Telemetry Extension**.

Phase 6 closed `GRC9` as an executable, replay-stable mechanical substrate.
That closeout deliberately reused the shared Phase T telemetry stack and kept
the family extension compact. That was the correct closeout move: it proved
that `GRC9` runs can emit deterministic step rows, event rows, summaries,
reports, and saved artifact lanes without inventing a second telemetry runtime.

This phase has a different purpose.

Phase T-GRC9 exists to make the **nine-slot phenomenology** visible in
telemetry artifacts:

- the 3x3 port chart,
- row-based anisotropic geometry,
- column-based interface families,
- mechanical chart failure,
- spark expansion as substrate refinement,
- identity fission after refinement,
- invertible column coarse-graining and Split,
- discrete multiscale extraction,
- and the explicit boundaries where the GRC9 paper points beyond the core
  mechanical implementation.

The goal is not to start `GRC9V3` early. The goal is to make `GRC9` observable
as `GRC9`, using signals justified by
[`papers/2026-04-GRC-9.md`](../papers/2026-04-GRC-9.md), not only by the
fields that happened to be easiest to expose during Phase 6 closeout.

## Purpose

Phase T-GRC9 must establish:

- an explicit `family_extensions["grc9"]` telemetry contract for GRC9-specific
  step rows, event rows, run summaries, and graph checkpoints,
- theory-facing telemetry surfaces for the distinctive phenomena in the GRC9
  paper,
- compressed but useful diagnostics for ports, rows, columns, tensor terms,
  sparks, expansion modules, growth, coarse-graining, and identity basins,
- event taxonomy strong enough for later reports and visualization,
- artifact-backed representative and seed-driven lanes that make the
  mechanical phenomena visible,
- and clear placeholders for paper-described phenomena that are not yet core
  Phase 6 runtime features.

This phase should preserve the shared telemetry architecture:

- common step rows remain common,
- family-specific data goes under `family_extensions["grc9"]`,
- graph checkpoints remain optional and explicit,
- reports and visualizations consume telemetry rather than reaching around it,
- and `GRC9.step()` remains telemetry-agnostic.

## Inputs From Earlier Phases

Phase T-GRC9 assumes the following are authoritative:

- the shared telemetry architecture from
  [`Phase-T-ImplementationPlan.md`](./Phase-T-ImplementationPlan.md),
- the family-extension rule from
  [`Phase-T-FamilyExtensionMatrix.md`](./Phase-T-FamilyExtensionMatrix.md),
- the completed Phase 6 runtime:
  - [`Phase-6-ImplementationPlan.md`](./Phase-6-ImplementationPlan.md)
  - [`Phase-6-StepLoop.md`](./Phase-6-StepLoop.md)
  - [`Phase-6-EquationMap.md`](./Phase-6-EquationMap.md)
  - [`Phase-6-Closeout.md`](./Phase-6-Closeout.md)
- the compact Phase 6 telemetry contract:
  - [`Phase-6-GRC9-TelemetryContract.md`](./Phase-6-GRC9-TelemetryContract.md)
  - [`Phase-6-GRC9-RepresentativeTelemetry.md`](./Phase-6-GRC9-RepresentativeTelemetry.md)
- the GRC9 theory and implementation contract:
  - [`../papers/2026-04-GRC-9.md`](../papers/2026-04-GRC-9.md)
  - [`../specs/grc-9-spec.md`](../specs/grc-9-spec.md)
- the existing GRCV3 telemetry-extension pattern:
  - [`Phase-T-GRCV3-TelemetryContract.md`](./Phase-T-GRCV3-TelemetryContract.md)
  - [`../src/pygrc/telemetry/grcv3_contract.py`](../src/pygrc/telemetry/grcv3_contract.py)

The compact Phase 6 contract should be treated as the historical closeout
surface, not as the final GRC9 telemetry shape.

## Relationship To Existing Phase 6 GRC9 Telemetry

Phase T-GRC9 extends the Phase 6 telemetry surface; it does not rewrite the
meaning of the Phase 6 artifacts.

The existing Phase 6 documents remain historical closeout records:

- [`Phase-6-GRC9-TelemetryContract.md`](./Phase-6-GRC9-TelemetryContract.md)
  records the compact contract version:
  - `phase6_iter10_v1`
- [`Phase-6-GRC9-RepresentativeTelemetry.md`](./Phase-6-GRC9-RepresentativeTelemetry.md)
  records the two closeout-facing lanes:
  - representative mechanical `primary` vs `replay`
  - seed-driven structural `cell-1` vs `cell-4`

Those lanes prove:

- the shared telemetry stack can capture `GRC9`,
- saved artifacts can expose spark, expansion, growth, and replay stability,
- the seed-driven bridge can run on real `cell-1` / `cell-4` seeds,
- and the Phase 6 closeout evidence is deterministic and reconstructable.

They do not attempt to expose the full nine-slot telemetry surface.

The new Phase T-GRC9 contract should therefore use a new version, beginning
with:

- `phase_t_grc9_iter1_v1`

and should be read as the current GRC9-specific mechanical telemetry layer.
The old `phase6_iter10_v1` payload remains valid for Phase 6 artifact
interpretation and should not be mutated retroactively.

## Current Code Structure And Migration Strategy

The shared telemetry core already has the extension hooks needed for this
phase.

Current shared structure:

- `src/pygrc/telemetry/schema.py`
  - owns `StepTelemetryRow`, `EventTelemetryRow`, `RunTelemetrySummary`, graph
    checkpoint artifacts, and the `family_extensions` envelope.
- `src/pygrc/telemetry/recorder.py`
  - owns `capture_run_telemetry(...)`.
  - already accepts:
    - `family_extensions`
    - `step_family_extensions`
    - `event_family_extensions_by_step`
    - `summary_family_extensions`
    - graph checkpoint payloads.
- `src/pygrc/telemetry/experiments.py`
  - currently wires GRC9 telemetry directly with compact dictionaries.

Current GRC9 telemetry constants are local to `experiments.py`:

```python
_GRC9_TELEMETRY_FAMILY = "grc9"
_GRC9_TELEMETRY_CONTRACT_VERSION = "phase6_iter10_v1"
_GRC9_ABUNDANCE_CONTRACT = "topology_updated_current_flux_diagnostic"
_GRC9_LANDSCAPE_LOWERING_MODE = "structural_graph_graft_v1"
```

The current representative and landscape GRC9 lanes pass one compact shared
`family_extensions["grc9"]` payload to every step/event row, plus a small
summary-only payload containing `final_expansion_count`.

Phase T-GRC9 should migrate this shape to a typed extension layer:

```text
src/pygrc/telemetry/
  grc9_contract.py          # public typed contract dataclasses and wrappers
  _grc9_extensions.py       # optional private builders from GRC9 state/results
```

The expected wiring change is:

- keep `capture_run_telemetry(...)` as the shared recorder,
- keep common schema rows unchanged unless a genuinely shared need appears,
- build GRC9-specific payloads before capture,
- pass them through:
  - `step_family_extensions=[...]`
  - `event_family_extensions_by_step=[...]`
  - `summary_family_extensions={...}`
- preserve the compact Phase 6 lane behavior for historical reconstruction
  where needed,
- write new richer artifacts under new lane/profile names.

In short:

```text
Phase 6:
  one compact grc9 extension copied onto all step/event rows

Phase T-GRC9:
  per-step grc9 mechanical summaries
  per-event grc9 classifications
  richer run-summary grc9 lifecycle summaries
  optional graph-checkpoint grc9 overlays
```

## In Scope

- a new explicit GRC9 telemetry contract module, expected target:
  - `src/pygrc/telemetry/grc9_contract.py`
- GRC9 contract tests, expected target:
  - `tests/telemetry/test_grc9_contract.py`
- richer step-level family extensions for:
  - port occupancy and inactive capacity
  - row tensor diagnostics
  - column diagnostics
  - conductance and flux summaries
  - sink/basin and abundance diagnostics
  - coarse-grain / Split diagnostics
- richer event-level family extensions for:
  - spark candidates and spark confirmations
  - expansion module creation
  - column-preserving boundary reassignment
  - growth events
  - coarse-cache invalidation when represented as an event or event-adjacent
    diagnostic
- run-summary family extensions for:
  - lifecycle counts
  - final mechanical state summaries
  - identity fission summaries
  - coarse-grain integrity summaries
  - calibration-window summaries when applicable
- optional GRC9 graph-checkpoint extensions for:
  - port chart overlays
  - row/column overlays
  - module membership and expansion lineage
  - edge-level conductance, flux, and analytic labels
- reconstruction scripts and saved artifact lanes for the new telemetry
  contract.

## Out Of Scope

This phase must not claim or implement:

- `GRC9V3` basin-attribute runtime semantics,
- hierarchy tracking as a constitutive runtime layer,
- choice/collapse semantics,
- family-native `GRCL-9` source lowering,
- signed-Hessian spark semantics as the core `GRC9` spark rule,
- Lorentzian causal cones or proper-time dynamics,
- full FRC scale-indexed coherence fields,
- or observer-local unpredictability as a property of the bare global
  simulation.

Those are paper-facing boundaries that telemetry should name honestly. Some of
them may receive reserved or diagnostic-only telemetry fields, but they must be
marked as unavailable, approximate, or future-facing rather than silently
promoted.

The next GRCL-9 work batch includes a narrower collapse-adjacent review, not a
change to this boundary. GRCV3-style choice/collapse semantics remain out of
scope for GRC9. That review may consider diagnostic-only GRC9-native
structural-collapse observability such as basin merge candidates, sink loss,
support loss, membrane/ridge rupture, or failed fission persistence, but only
as a new explicit surface or contract version.

Review outcome:

- [Phase-T-GRC9-CollapseAdjacentObservabilityReview.md](./Phase-T-GRC9-CollapseAdjacentObservabilityReview.md)
  accepts selector-backed structural diagnostics over existing
  `identity_abundance`, `transport`, identity-fission summary, and graph
  checkpoint fields for the next GRCL-9 batch.
- It does not add a `collapse` event domain, `collapse_evidence` group, or
  compact collapse-adjacent summary fields to `phase_t_grc9_iter1_v1`.

## Theory-To-Telemetry Phenomenology Map

This phase should start from the GRC9 paper's phenomena and then decide how
each can be observed.

| Paper phenomenon | Theory source | Telemetry target | Current status |
| --- | --- | --- | --- |
| Nine ordered ports and active degree | Sections 1.1-1.2 | port occupancy, active degree, inactive capacity | implemented, needs richer telemetry |
| Rows as local directional basis | Sections 1.2, 2 | row occupancy, row tensor diagonal, row mismatch terms | implemented, needs first-class contract |
| Columns as interface families | Sections 1.2, 8.2, 8.3, 9 | column diagnostics, reassignment groups, coarse profiles | implemented, needs first-class contract |
| Tensor from density, mismatch, flux feedback | Eq. (1) | tensor term summary and anisotropy indicators | implemented, needs compressed step payload |
| Conductance map and analytic labels | Eqs. (2), Appendix G.4 | conductance distribution, label availability, label mode | implemented, needs GRC9-specific edge summaries |
| Potential and flux | Eqs. (3)-(6) | potential range, signed flux split, strongest oriented flux | implemented, needs port-pair-aware summaries |
| Sinks and identity basins | Eqs. (8)-(10) | sink count, basin sizes, successor diagnostics | implemented, common observables are too thin |
| Scale-weighted abundance | Eq. (17) | `abundance_weighted` for configured gamma values | artifact-backed when gamma configured |
| Spark as chart failure under saturation | Eqs. (11)-(12), Appendix H.3 | candidate gate, active-degree gate, instability, column proxy | implemented, needs event taxonomy |
| Optional near-saturation rule | Section 8.2 | reserved gate diagnostic with `enabled=false` unless configured | deferred |
| Optional sign-crossing spark | Section 8.2 | previous/current column diagnostic and sign crossing count | partly implemented/config-gated |
| Expansion module | Eqs. (13)-(16) | module shape, core/satellite/helper IDs, inherited mass | implemented, needs event and checkpoint payloads |
| Expansion distribution | Eq. (16), spec expansion distribution rule | `expansion_distribution_mode`, actual transfer ratios | implemented, needs telemetry contract |
| Expansion bond initialization | Section 8.3.4 | bond mode, bond weight, internal conductance stats | implemented, needs telemetry contract |
| Effective degree policy | Eq. (13) | target effective degree and module-size formula | implemented, needs telemetry contract |
| Adiabatic expansion schedule | Section 8.3.5 | schedule mode and expansion substeps | schedule state exists, phased loop deferred |
| Identity fission after expansion | Appendix E | post-expansion sink emergence and basin persistence windows | artifact-backed when evaluator observations are supplied |
| Growth on inactive ports | Section 8.4 | growth parent, selected port, outward-flux pressure, birth probability | implemented, needs event summary |
| Invertible column coarse-graining | Eqs. (18)-(22) | field names, totals, profile sparsity, reconstruction error | implemented, needs telemetry contract |
| Signed flux exact encoding | Section 9.1 | `J+` / `J-` decomposition stats | implemented, needs telemetry contract |
| Profile sparsity compression | Appendix D.3 | profile compression mode and dominant-mode summary | diagnostic/future-facing |
| Successor-map tie handling | Eq. (8), Phase 6 tie rule | successor tie count and tie-break policy | implemented, needs telemetry contract |
| Budget preservation policy | Section 7 | budget policy, correction path, correction counts | implemented, needs telemetry contract |
| Ternary identity tree extraction | Appendix D.4 | optional checkpoint/report extraction, not core step payload | future-facing diagnostic |
| Calibration magnitudes | Appendix D.1 | burn-in `M_H`, `M_C`, spark-rate summary | diagnostic-only |
| Boundary-horizon analogue | Appendix I.1 | boundary mode status and reserved barrier/ghost diagnostics | deferred |
| Temporal/causal layer | Appendix I.4 | temporal-delay label only; no causal-layer claim | label implemented, causal layer deferred |
| Scale-indexed FRC field | Appendix I.5 | discrete coarse ladder only; no sigma-field claim | deferred |
| Observer-local unpredictability | Appendix I.7 | out of telemetry unless restricted observer views exist | deferred |

## Contract Shape

The new contract should use:

- family key: `grc9`
- contract version: `phase_t_grc9_iter1_v1` for the first implementation slice

The contract should be implemented as dataclasses and builder functions, similar
in style to the GRCV3 contract module.

Expected public builders:

- `grc9_step_family_extensions(...)`
- `grc9_event_family_extensions(...)`
- `grc9_run_summary_family_extensions(...)`
- `classify_grc9_event_extension(...)`

The first module should keep validation local to the contract dataclasses. The
shared recorder should remain family-agnostic.

## Step-Row Extension Surface

Each GRC9 step row should eventually carry a compressed payload with these
groups.

### Backend And Configuration Summary

Required fields:

- `contract_version`
- `frame_mode`
- `curvature_backend`
- `metric_backend`
- `spark_backend`
- `birth_backend`
- `growth_parent_eligibility_mode`
- `coarse_graining_backend`
- `boundary_mode`
- `budget_preservation_policy`
- `expansion_distribution_mode`
- `expansion_schedule`
- `edge_label_selection`
- `source_lowering_mode` when the lane is seed-driven

Interpretation:

- backend names must preserve the Phase 6 distinction between shared backend
  vocabulary and family-local mechanics.
- `boundary_mode = barrier` or `ghost` must not appear as executable unless the
  runtime implements them and capabilities are updated.
- `budget_preservation_policy` should describe the configured policy, while
  step/event diagnostics should record which correction path actually occurred.
- `expansion_schedule` should distinguish `instantaneous` from `adiabatic` and
  carry `tau_exp` or substep count when the adiabatic path is implemented.

### Port Chart Summary

Required fields:

- `num_nodes`
- `num_port_edges`
- `active_degree_histogram`
- `inactive_port_count`
- `saturated_node_count`
- `near_saturated_node_count`
- `row_occupancy_totals`
- `column_occupancy_totals`

Optional fields:

- `saturated_node_ids_sample`
- `inactive_capacity_by_column`

Compression rule:

- step rows should store counts and small samples, not the full port occupancy
  table. Full port occupancy belongs in graph checkpoints.

### Row Tensor Summary

Required fields:

- `row_tensor_min`
- `row_tensor_max`
- `row_tensor_mean`
- `row_tensor_anisotropy_max`
- `density_term_mean`
- `row_mismatch_term_max`
- `flux_feedback_term_mean`

Optional fields:

- `row_mismatch_hotspots`
- `row_tensor_by_node_sample`

Interpretation:

- this is the telemetry surface for Eq. (1).
- it must preserve that rows are the local directional basis.
- it must not imply unrestricted continuum tensor freedom; GRC9 uses the
  reduced three-row basis.

### Column Diagnostic Summary

Required fields:

- `column_diagnostic_min_abs`
- `column_diagnostic_mean_abs`
- `column_proxy_candidate_count`
- `sign_crossing_candidate_count`
- `column_profile_sparsity`

Optional fields:

- `column_diagnostic_by_candidate`
- `column_diagnostic_hotspots`
- `spark_calibration`

Interpretation:

- this is the telemetry surface for Eq. (11) and the column-proxy branch of
  Eq. (12).
- column diagnostics must remain column-facing, not row tensor aliases.
- `spark_calibration`, when present, should record:
  - `spark_threshold`
  - `spark_threshold_mode`
  - `burn_in_M_H`
  - `burn_in_M_C`
  so Appendix D.1 calibration can be audited without promoting calibration to a
  required runtime mode.

### Transport Summary

Required fields:

- `conductance_min`
- `conductance_max`
- `conductance_mean`
- `flux_abs_sum`
- `flux_signed_balance`
- `positive_flux_edge_count`
- `negative_flux_edge_count`
- `strongest_flux_edges_sample`

Optional fields:

- `potential_min`
- `potential_max`
- `potential_range`
- `label_availability`
- `label_computation_mode`

Interpretation:

- the single conductance remains the dynamical edge weight.
- analytic edge labels are telemetry labels, not extra dynamical weights.
- `label_availability` should be a per-label breakdown for:
  - `geometric_length_available`
  - `temporal_delay_available`
  - `flux_coupling_available`
  and `label_computation_mode` should record the selected mode per label when
  availability is partial or mode-specific.

### Identity And Abundance Summary

Required fields:

- `sink_count`
- `basin_count`
- `basin_size_min`
- `basin_size_max`
- `basin_size_mean`
- `abundance_contract`

Optional fields:

- `scale_weighted_abundance`
- `scale_weighted_abundance_gamma`
- `successor_self_loop_count`
- `successor_tie_count`
- `successor_tie_break_policy`
- `basin_mass_summary`

Interpretation:

- `abundance` keeps the Phase 6 contract:
  `topology_updated_current_flux_diagnostic`.
- scale-weighted abundance comes from Eq. (17) and should be explicit about
  the chosen gamma.

### Coarse-Graining Summary

Required fields:

- `coarse_fields_list`
- `coarse_cache_state`
- `coarse_cache_invalidation_reason`
- `exact_split_supported_fields`
- `signed_flux_mode`

Optional fields:

- `coarse_field_types`
- `max_reconstruction_error_by_field`
- `column_total_sparsity_by_field`
- `dominant_mode_profile_count`
- `profile_compression_mode`

Interpretation:

- exact reconstruction claims must be tested against supported fields.
- compressed signed-flux diagnostics, if added later, must be labeled
  non-exact.
- `coarse_field_types` should distinguish:
  - `nonnegative`
  - `signed_lossless`
  - `signed_compressed`
- `profile_compression_mode` should distinguish:
  - `full`
  - `dominant_index_residual`
  - `custom`

### Budget Correction Summary

Required fields:

- `budget_current`
- `budget_target`
- `budget_error`
- `budget_preservation_policy`
- `last_budget_correction_path`

Optional fields:

- `uniform_shift_delta`
- `simplex_projection_applied`
- `negative_clamp_count`

Interpretation:

- the configured policy belongs in backend/config telemetry.
- the actual path taken in a step belongs here or in budget event telemetry.
- if the runtime uses a common uniform correction with a positivity-preserving
  fallback, telemetry should expose the chosen path rather than collapsing both
  into one generic budget correction count.

## Event-Row Extension Surface

GRC9 event rows should gain a stable classification layer in addition to the
raw `event_kind` and raw event payload.

Required fields:

- `contract_version`
- `event_domain`
- `lifecycle_stage`
- `topology_mutation`
- `port_mutation`
- `budget_mutation`
- `primary_node_id`
- `primary_edge_id` when applicable
- `registry_key` when applicable

Recommended domains:

- `spark`
- `expansion`
- `growth`
- `coarse`
- `budget`
- `boundary`
- `other`

Recommended lifecycle stages:

- `candidate`
- `confirmed`
- `fission_confirmed`
- `module_created`
- `boundary_reassigned`
- `child_attached`
- `invalidated`
- `corrected`
- `other`

Spark events should expose:

- `spark_kind`
- `active_degree`
- `saturation_gate_pass`
- `instability_score`
- `instability_gate_pass`
- `column_proxy_min_abs`
- `column_proxy_gate_pass`
- `sign_crossing_gate_pass`
- `trigger_column`
- `predicted_D_eff`
- `predicted_module_size`
- `predicted_satellite_count`

Expansion events should expose:

- `parent_sink_id`
- `target_effective_degree`
- `module_size_formula`
- `module_node_count`
- `core_node_id`
- `satellite_node_ids`
- `helper_node_ids`
- `reassigned_edge_count`
- `reassigned_edge_count_by_column`
- `internal_edge_count`
- `coherence_transfer_mode`
- `coherence_transfer_ratios`
- `coherence_transfer_ratios_sum`
- `bond_weight_mode`
- `bond_weight`
- `internal_conductance_stats`
- `expansion_schedule`
- `expansion_substeps`
- `budget_preserved_by_construction`

Growth events should expose:

- `parent_node_id`
- `child_node_id`
- `selected_parent_port`
- `child_port`
- `parent_selection_mode`
- `parent_eligibility_mode`
- `parent_capacity_source`
- `front_growth_provenance_present`
- `legacy_broad_growth`
- `outward_flux_pressure`
- `birth_rule`
- `birth_probability`

Budget events should expose:

- `budget_preservation_policy`
- `correction_path`
- `uniform_shift_delta`
- `simplex_projection_applied`
- `budget_error_before`
- `budget_error_after`

## Run-Summary Extension Surface

Each GRC9 run summary should carry:

- `contract_version`
- `backend_summary`
- `final_port_chart_summary`
- `final_row_tensor_summary`
- `final_column_diagnostic_summary`
- `final_transport_summary`
- `final_identity_summary`
- `final_coarse_graining_summary`
- `lifecycle_event_counts`
- `expansion_summary`
- `growth_summary`

The lifecycle event counts should be fixed-width enough for reports:

- `spark_candidate_count`
- `spark_confirmed_count`
- `spark_instability_count`
- `spark_column_proxy_count`
- `spark_sign_crossing_count`
- `expansion_count`
- `growth_count`
- `front_capacity_growth_count`
- `legacy_broad_growth_count`
- `coarse_cache_invalidation_count`
- `budget_correction_count`
- `budget_uniform_correction_count`
- `budget_simplex_correction_count`

The expansion summary should include:

- `final_expansion_registry_size`
- `total_module_nodes_created`
- `total_boundary_reassignments`
- `max_module_node_count`
- `identity_fission_candidate_count`
- `identity_fission_confirmed_count`
- `identity_fission_max_persistence_steps`

The calibration summary should include when applicable:

- `spark_threshold`
- `spark_threshold_mode`
- `burn_in_M_H`
- `burn_in_M_C`
- `spark_rate_observed`

Identity fission should be summary-first:

- count post-expansion windows where one pre-spark sink module later supports
  two or more stable sinks,
- record basin persistence windows when available,
- distinguish candidates from confirmed fission using the Appendix E
  persistence-window criterion and a configured minimum basin mass threshold,
- do not claim GRCV3 hierarchy unless Phase 7 implements it.

## Graph Checkpoint Extension Surface

Phase T-GRC9 graph checkpoints are opt-in artifacts. The checkpoint exporter
defines the payload shape, and the representative / seed-driven experiment
lanes expose checkpoint-capture controls for generating saved artifacts when
visualization or inspection needs them.

Optional GRC9 checkpoint payloads should include:

- per-node:
  - active degree
  - row occupancy
  - column occupancy
  - coherence
  - potential
  - sink/basin role
  - module membership if created by expansion
- per-port:
  - occupied flag
  - row
  - column
  - incident edge id
- per-edge:
  - endpoint ports
  - conductance
  - oriented flux
  - geometric length
  - temporal delay
  - flux coupling
  - internal-module flag
  - reassigned-boundary flag
- per-module:
  - parent sink id
  - core/satellite/helper nodes
  - internal edge ids
  - reassigned boundary edges by column

These payloads are the natural input to GRC9 visualization surfaces.

## Validation Lanes

The phase should keep at least three lanes separate.

### Lane 1. Representative Mechanical Replay

Purpose:

- prove the richer contract on the existing eventful synthetic lane,
- preserve primary-vs-replay comparison,
- make spark, expansion, growth, and Split diagnostics visible.

Expected artifact path:

- `outputs/representative/grc9/<lane>/primary/.../telemetry/`
- `outputs/representative/grc9/<lane>/replay/.../telemetry/`

### Lane 2. Real-Seed Structural Bridge

Purpose:

- prove that richer GRC9 telemetry works on real `cell-1` / `cell-4` seeds,
- keep `source_lowering_mode = structural_graph_graft_v1`,
- avoid over-reading the lane as `GRCL-9` or `GRC9V3`.

Expected artifact path:

- `outputs/representative/grc9_landscape/<profile>/cell-1/.../telemetry/`
- `outputs/representative/grc9_landscape/<profile>/cell-4/.../telemetry/`

### Lane 3. Theory-Facing Diagnostic Probe

Purpose:

- exercise paper phenomena that the closeout lane may not naturally expose,
  especially:
  - scale-weighted abundance,
  - identity fission after expansion,
  - sign-crossing diagnostics,
  - calibration magnitudes,
  - coarse-grain reconstruction checks.

This lane may be synthetic at first. If it requires runtime behavior not yet
implemented, the plan should record that as a runtime gap rather than silently
flattening the telemetry claim.

## Workstreams

## Workstream 1. Contract Document And Checklist

### Goal

Lock the telemetry target before implementation begins.

### Scope

- create `Phase-T-GRC9-TelemetryContract.md`
- create `Phase-T-GRC9-ImplementationChecklist.md`
- link this plan from `ImplementationPhases.md`
- decide the first contract version string
- distinguish implemented, diagnostic-only, and reserved fields

### Acceptance Criteria

- the contract maps back to the GRC9 paper phenomena, not only current code
  fields
- the contract preserves runtime/source/artifact separation
- deferred GRC9V3 and GRCL-9 semantics are named explicitly

## Workstream 2. Typed Contract Module

### Goal

Implement a first-class GRC9 telemetry extension module.

### Scope

- add `src/pygrc/telemetry/grc9_contract.py`
- define dataclasses for step, event, and run-summary extension payloads
- define event classifiers
- export the public contract through `src/pygrc/telemetry/__init__.py`
- add focused tests in `tests/telemetry/test_grc9_contract.py`

### Acceptance Criteria

- GRC9 no longer relies on ad hoc dict assembly in `experiments.py`
- payload validation catches negative counts and invalid finite values
- family extensions are wrapped under `family_extensions["grc9"]`
- unknown events classify to `other` without breaking capture

## Workstream 3. Step Extension Builders

### Goal

Build compressed step-level diagnostics from live `GRC9` state.

### Scope

- port chart summary
- row tensor summary
- column diagnostic summary
- transport summary
- identity/abundance summary
- coarse-grain summary

### Acceptance Criteria

- builder output is deterministic on fixed state
- builder output does not mutate runtime state
- missing optional caches degrade to explicit unavailable fields
- row and column summaries remain semantically distinct

## Workstream 4. Event Extension Builders

### Goal

Classify GRC9 mechanical events for reports and later visualization.

### Scope

- spark candidate/confirmed classification
- expansion classification
- growth classification
- coarse-cache invalidation classification if event-backed
- budget correction classification if event-backed

### Acceptance Criteria

- topology, port, and budget mutation flags are stable
- spark events expose the trigger evidence needed to distinguish instability,
  column proxy, and sign crossing
- expansion events expose module shape and reassignment by column
- growth events expose selected inactive port

## Workstream 5. Run-Summary Extension Builders

### Goal

Summarize GRC9 mechanical trajectories without parsing raw event payloads.

### Scope

- lifecycle event counts
- final state summaries
- expansion/growth totals
- coarse-grain integrity summaries
- identity-fission candidate summaries
- calibration summaries when a burn-in lane is used

### Acceptance Criteria

- run summaries are fixed-width enough for comparison reports
- identity fission is reported as a post-expansion diagnostic, not a hard-coded
  split claim
- exact Split claims include reconstruction checks or are omitted

## Workstream 6. Graph Checkpoint Extensions

### Goal

Make GRC9 graph-visible artifacts carry port, row, column, and module overlays.

### Scope

- optional checkpoint payload groups for nodes, ports, edges, and modules
- integration with existing graph checkpoint artifact layout
- checkpoint tests for deterministic payloads

### Acceptance Criteria

- checkpoint export remains opt-in
- behavior-only telemetry still works without checkpoint artifacts
- later visualization can reconstruct port charts and expansion modules from
  saved checkpoint data

## Workstream 7. Artifact Lanes And Reconstruction Scripts

### Goal

Regenerate saved evidence with the richer contract.

### Scope

- update representative GRC9 telemetry capture
- update seed-driven GRC9 telemetry capture
- add or extend reconstruction scripts
- save closeout-facing artifacts under a new lane/profile name rather than
  mutating the Phase 6 baseline artifact meaning

### Acceptance Criteria

- primary/replay representative runs agree on final digest
- cell-1/cell-4 structural runs emit the richer family extension
- reports expose the GRC9-specific summaries
- the Phase 6 artifacts remain historically interpretable

## Workstream 8. Theory-Facing Review

### Goal

Check the telemetry contract against the paper before treating the phase as
closed.

### Scope

- review every major theory-to-telemetry row in this plan
- mark each field as:
  - implemented and artifact-backed,
  - diagnostic-only,
  - reserved/future,
  - or explicitly out of scope
- record any runtime gaps discovered while trying to observe paper phenomena

### Acceptance Criteria

- the closeout does not reduce the paper to current implementation details
- the closeout does not over-claim `GRC9V3`, `GRCL-9`, Lorentzian, FRC, or
  observer-local semantics
- later Phase 7 planning can reuse this telemetry surface rather than
  rediscovering which GRC9 mechanics matter

## Workstream 9. Appendix E Identity-Fission Persistence Diagnostic

Status: implemented in Iteration 11.

### Goal

Promote confirmed identity-fission telemetry from `reserved_future` to
artifact-backed diagnostic evidence without changing GRC9 topology dynamics.

### Scope

- add a non-mutating persistence-window evaluator over completed GRC9
  trajectories,
- evaluate post-expansion modules for the same stable descendant sink pair,
- require a configured persistence window `Delta`,
- require a configured minimum basin-mass threshold,
- update run-summary extension builders to populate:
  - `identity_fission_confirmed_count`,
  - `identity_fission_max_persistence_steps`,
  - diagnostic status for confirmed fission,
- add focused tests for candidate-only, confirmed, and below-threshold cases.

### Non-Scope

- do not create a new split/topology event,
- do not implement GRCV3 hierarchy semantics,
- do not claim GRCL-9 lowering,
- do not add observer-local views,
- do not add Lorentzian, FRC, or boundary barrier/ghost semantics.

### Acceptance Criteria

- Appendix E confirmed fission is derived only from observed same-pair sink/basin
  persistence,
- candidate and confirmed counts remain distinct,
- the evaluator is deterministic and replay-safe,
- runs without enough post-expansion history keep confirmed fission at zero,
- other deferred boundaries remain deferred.

### Implementation Notes

Iteration 11 adds compact non-mutating fission observations, an Appendix E
persistence-window evaluator, run-summary integration, rich-lane observation
capture, and diagnostic-probe coverage. The evaluator tracks the same
qualifying sink pair across the window, uses configurable
`identity_fission_persistence_delta` and `identity_fission_min_basin_mass`
values when present, with explicit override parameters available to the
run-summary builder.

## Initial Iteration Proposal

The first implementation iteration should be deliberately small:

1. Create `Phase-T-GRC9-TelemetryContract.md`.
2. Create `Phase-T-GRC9-ImplementationChecklist.md`.
3. Add `src/pygrc/telemetry/grc9_contract.py` with typed dataclasses for:
   - backend/config summary,
   - port chart summary,
   - row tensor summary,
   - column diagnostic summary,
   - transport summary,
   - identity summary,
   - coarse-graining summary,
   - event extension,
   - lifecycle event counts,
   - run-summary extension.
4. Add `tests/telemetry/test_grc9_contract.py`.
5. Export the contract from `pygrc.telemetry`.

Only after that should the existing representative and landscape GRC9 lanes be
rewired to emit the richer contract.

## Exit Criteria

Phase T-GRC9 is complete when:

- `GRC9` has an explicit versioned telemetry contract under the `grc9` family
  key,
- representative and seed-driven GRC9 lanes emit the richer family extension,
- GRC9-specific event taxonomy exists and is test-backed,
- graph checkpoint extensions either exist or are explicitly deferred with a
  documented contract,
- artifact lanes expose ports, rows, columns, sparks, expansion, growth,
  coarse-graining, and identity-basin diagnostics,
- theory-facing phenomena from the GRC9 paper are either artifact-backed or
  explicitly marked as future-facing,
- and the phase remains honest that `GRC9V3`, `GRCL-9`, Lorentzian causal
  layers, FRC sigma fields, and observer-local unpredictability are not core
  GRC9 telemetry claims.
