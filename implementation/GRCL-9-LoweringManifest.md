# GRCL-9 Lowering Manifest

Manifest version: `grcl9_lowering_manifest_v1`

Source schema version: `grcl9.source.v1`

Source catalog:
`outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.md`

Output root:
`outputs/grcl9/lowering`

## Purpose

This manifest is the contract bridge between reviewed GRC9-native motifs and
future GRCL-9 source fixtures.

It does not implement lowering and it does not claim that any S0026 motif is
already source syntax. It records which GRCL-9 source constructs must exist,
which graph preconditions they must lower, which metadata carriers must be
written, and which Phase T-GRC9 telemetry fields validate the result after the
runtime runs.

## Boundary Rules

- Source constructs declare mechanical preconditions and policy only.
- Source constructs do not declare spark, expansion, growth, or fission
  outcomes.
- Telemetry expectations use `family_extensions.grc9.*` field paths.
- Historical convenience fields such as `event_counts_by_kind.*` are not valid
  manifest fields.
- Optional telemetry remains optional in this manifest.
- Fission entries lower sink-capable geometry and evaluator parameters; they
  do not claim runtime-computed basins or source-level fission confirmation.

## Required Lowering Carriers

Common carriers:

- `extensions.grcl9`
- `node_payload.grcl9_source_construct_id`
- `edge_payload.grcl9_source_construct_id`
- `cached_quantities.grcl9_provenance`
- `cached_quantities.grcl9_motif_registry`
- `cached_quantities.grcl9_assembly_policy`

Specialized carriers:

- `cached_quantities.grcl9_expected_saturated_node_ids`
- `cached_quantities.grcl9_expected_column_proxy_candidate_ids`
- `cached_quantities.grcl9_bridge_edge_ids`

## Manifest Entries

### `grcl9_lowering_spark_column_proxy_v1`

Phenomenon: `spark`

Seed family: `spark_column_proxy_emitter`

Source constructs:

- `spark_candidate_region`
- `column_proxy_profile`

Graph preconditions:

- saturated candidate node
- target column diagnostic near epsilon
- spark gate intent `saturation_column_proxy`

Required source knobs:

- `candidate_id`
- `coherence_allocation`
- `neighbor_coherence_profile`
- `target_column`
- `spark_threshold`
- `spark_gate_intent`

Expected telemetry:

- `family_extensions.grc9.final_column_diagnostic_summary.column_proxy_candidate_count`
- `family_extensions.grc9.lifecycle_event_counts.spark_column_proxy_count`
- `family_extensions.grc9.spark_evidence.spark_kind`

Controls:

- pass: `spark_column_proxy_eps_pass`
- fail: `spark_column_proxy_eps_fail`

### `grcl9_lowering_spark_instability_v1`

Phenomenon: `spark`

Seed family: `spark_instability_emitter`

Source constructs:

- `spark_candidate_region`
- `instability_profile`

Graph preconditions:

- saturated candidate node
- controlled row tensor anisotropy
- controlled cut/support proxy
- spark gate intent `saturation_instability`

Required source knobs:

- `candidate_id`
- `coherence_allocation`
- `row_anisotropy_profile`
- `support_cut_profile`
- `tau_instability`
- `spark_gate_intent`

Expected telemetry:

- `family_extensions.grc9.final_row_tensor_summary.row_tensor_anisotropy_max`
- `family_extensions.grc9.lifecycle_event_counts.spark_instability_count`
- `family_extensions.grc9.spark_evidence.instability_score`

Controls:

- pass: `spark_instability_tau_pass`
- fail: `spark_instability_tau_fail`

### `grcl9_lowering_expansion_refinement_v1`

Phenomenon: `expansion`

Seed family: `spark_to_expansion_emitter`

Source constructs:

- `spark_candidate_region`
- `expansion_refinement_region`

Graph preconditions:

- saturated spark-capable parent
- declared `target_effective_degree`
- column-preserving boundary reassignment

Required source knobs:

- `candidate_id`
- `target_effective_degree`
- `module_size_formula`
- `bond_weight_mode`
- `coherence_transfer_mode`
- `coherence_transfer_ratios`

Expected telemetry:

- `family_extensions.grc9.lifecycle_event_counts.expansion_count`
- `family_extensions.grc9.expansion_summary.max_module_node_count`
- `family_extensions.grc9.expansion_evidence.target_effective_degree`
- `family_extensions.grc9.expansion_evidence.coherence_transfer_ratios`

Controls:

- low: `spark_to_expansion_d_eff_low`
- high: `spark_to_expansion_d_eff_high`

### `grcl9_lowering_growth_pressure_v1`

Phenomenon: `growth`

Seed family: `growth_pressure_emitter`

Source constructs:

- `growth_locus`

Graph preconditions:

- inactive parent port
- localized outward flux pressure
- birth rule `outward_flux_pressure`

Required source knobs:

- `parent_id`
- `inactive_parent_port`
- `pressure_profile`
- `birth_rule`
- `lambda_birth`

Expected telemetry:

- `family_extensions.grc9.lifecycle_event_counts.growth_count`
- `family_extensions.grc9.growth_evidence.outward_flux_pressure`
- optional `family_extensions.grc9.growth_evidence.birth_probability`
- optional `family_extensions.grc9.growth_summary.birth_probability_max`

Controls:

- high: `growth_pressure_lambda_high`
- low: `growth_pressure_lambda_low`

### `grcl9_lowering_post_expansion_fission_v1`

Phenomenon: `fission`

Seed family: `post_expansion_fission_emitter`

Source constructs:

- `post_expansion_fission_geometry`

Graph preconditions:

- two sink-capable regions
- separable conductance geometry
- declared minimum basin mass
- declared persistence window

Required source knobs:

- `module_region_id`
- `sink_region_a`
- `sink_region_b`
- `identity_fission_min_basin_mass`
- `identity_fission_persistence_delta`

Expected telemetry:

- `family_extensions.grc9.expansion_summary.identity_fission_confirmed_count`
- `family_extensions.grc9.expansion_summary.identity_fission_max_persistence_steps`
- `family_extensions.grc9.identity_abundance.basin_size_max`

Controls:

- pass: `post_expansion_fission_min_mass_pass`
- fail: `post_expansion_fission_min_mass_fail`

## Code Contract

The typed manifest lives in:

- `src/pygrc/grcl9/manifest.py`

The default manifest helper is:

- `default_grcl9_lowering_manifest()`

The focused tests are:

- `tests/grcl9/test_grcl9_manifest.py`

The typed model validates:

- manifest version
- source schema version
- supported source construct kinds
- unique entry ids
- unique seed families
- unique accepted S0026 motif ids
- contract-aligned telemetry field paths
- explicit optional telemetry
- pass/fail control links
