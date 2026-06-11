# Iteration 2 Shared Fixture And Transform Harness

Status: complete.

## Scope

This report defines the experiment-local central-node fixture schema,
transform utilities, seed replay convention, artifact entry points, and
comparison report schema for the GRC9V3 property experiments.

The baseline lane is `current_hybrid_signed_hessian`. Column-H remains
a derived analysis proxy unless a separate canonical-column-H lane exists.

## Generated Artifacts

- `../configs/shared_fixture_transform_manifest.json`
- `../outputs/iter2_fixture_transform_verification.json`

## Verification

- `schema_version`: `"grc9v3_properties_iter2_v1"`
- `fixture_generation_deterministic`: `true`
- `edge_count_preserved`: `true`
- `active_degree_preserved`: `{"column_permutation_312": 9, "degree_preserving_random_relabel": 9, "row_column_transpose": 9, "row_permutation_231": 9}`
- `row_transform_factorized`: `true`
- `column_transform_factorized`: `true`
- `transpose_transform_swaps_axes`: `true`
- `random_relabel_breaks_factorization`: `true`
- `balanced_energy_preserved_under_transforms`: `{"column_permutation_312": true, "degree_preserving_random_relabel": true, "row_column_transpose": true, "row_permutation_231": true}`
- `non_uniform_energy_preserved_under_transforms`: `{"column_permutation_312": true, "degree_preserving_random_relabel": true, "row_column_transpose": true, "row_permutation_231": true}`
- `partial_activity_degree_8_helper_active_count`: `8`
- `fixture_contract_validation`: `true`
- `runtime_binding_requirements_declared`: `true`
- `blocked_observations_schema_declared`: `true`
- `run_id_convention_declared`: `true`
- `state_mapping_convention_declared`: `true`
- `imports_from_src_without_runtime_mutation`: `true`

## Seed Replay

- base seed: `0`
- random relabel seed: `1000`
- required run-manifest fields: `seed`, `fixture_id`, `transform_id`,
  `lane_id`, and `schema_version`
- run id format: `<experiment_id>__<fixture_id>__<transform_id>__seed_<seed>__<schema_version>`

## Runtime Assumptions

- lane id: `current_hybrid_signed_hessian`
- signed Hessian backend: `row_basis_diagonal`
- column-H status: `derived_analysis_proxy_only`

## Artifact Entry Points

- `run_manifest`: `../outputs/<run_id>/run_manifest.json`
- `step_events`: `../outputs/<run_id>/step_events.jsonl`
- `lane_a_spark_gate_traces`: `../outputs/<run_id>/lane_a_spark_gate_traces.jsonl`
- `state_snapshots`: `../outputs/<run_id>/snapshots/`
- `comparison_report`: `../reports/<run_id>_comparison.md`
- `blocked_observations`: `../reports/<run_id>_blocked_observations.csv`

## Blocked Observations CSV

- `experiment`: experiment or discriminator id
- `observation`: claim-specific observation name
- `status`: blocked | inconclusive
- `artifact_source`: artifact path or runtime surface attempted
- `reconstruction_attempt`: short description of extraction/reconstruction attempt
- `notes`: free-form audit note

## State Mapping Convention

- `central_node_id`: must exist in the target GRC9V3State before binding
- `active_false`: schema placeholder only; do not create a live PortEdge
- `active_true`: create one live PortEdge attached to central_node_id and treatment.port_id
- `coherence_delta`: added to the selected node coherence by the experiment-specific fixture builder
- `conductance`: maps to PortEdge.conductance and GRC9V3State.base_conductance[edge_id]
- `flux_uv`: maps to PortEdge.flux_uv with orientation recorded in the run manifest

## Runtime Binding Requirements

- `central_node_exists`: assert central_node_id is present in GRC9V3State.topology
- `active_degree_matches`: assert live edges at the central node equal active treatment count
- `port_occupancy_matches`: assert active treatments occupy exactly their declared ports
- `inactive_ports_absent`: assert inactive treatments do not create live PortEdge records
