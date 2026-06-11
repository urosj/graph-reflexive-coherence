# GRC9V3 Theory / Runtime Gap Ledger

Status: reconstructed historical artifact.

Spark lane: `current_hybrid_signed_hessian`
Lane B status: `deferred_not_rejected`

This ledger was reconstructed from the readiness checklist and artifact-surface hardening note because telemetry-scale outputs are not included in the public checkout.

## Summary

- Direct surfaces: `7`
- Derived surfaces: `1`
- Partial surfaces: `1`
- Absent surfaces: `0`

## Surfaces

### row_differential_state

- Status: `direct`
- Meaning: Per-node row-basis gradient and differential evidence used to judge the Lane A small-gradient envelope.
- Artifact sources: GRC9V3NodeState.gradient_row_basis, snapshot basin_attributes.nodes[*].gradient_row_basis, hybrid_spark_candidate payload gradient_norm and eps_gradient
- Experiment impact: Supports Lane A spark-envelope interpretation directly when state snapshots or candidate payloads are available.
- Blocked claims: none
- Lane B requirement: No Lane B change required for the row differential surface itself.

### signed_hessian_hybrid_spark_candidate

- Status: `direct`
- Meaning: Candidate events expose the current signed-Hessian degeneracy gate used by the default hybrid spark lane.
- Artifact sources: StepResult.events[kind=hybrid_spark_candidate].payload, family_extensions.grc9v3.spark_evidence, cached_quantities.hybrid_spark_signed_crossing_status
- Experiment impact: Allows current-lane spark candidates to be audited without reinterpreting them as canonical column-H gates.
- Blocked claims: Direct column-H triggered the spark is blocked in Lane A.
- Lane B requirement: canonical_column_h, Add an explicit opt-in Lane B spark lane with direct column-H proxy-branch fields.

### active_degree_saturation

- Status: `direct`
- Meaning: The active-port count and saturation gate identify whether a candidate is in the required current-lane degree envelope.
- Artifact sources: hybrid_spark_candidate payload active_degree, hybrid_spark_candidate payload saturation_gate, topology endpoint slots and port occupancy
- Experiment impact: Separates degree-8 near-saturation observations from the degree-9 Lane A gate.
- Blocked claims: none
- Lane B requirement: No Lane B change required unless a future lane deliberately changes the active-degree gate.

### mechanical_expansion_mapping

- Status: `direct`
- Meaning: Expansion event payloads preserve the reassignment map from a sparked sink into the mechanical refinement module.
- Artifact sources: StepResult.events[kind=hybrid_mechanical_expansion].payload.reassignment_map, cached_quantities.last_hybrid_expansion.reassignment_map, GRC9V3State.expansion_registry, snapshot basin_attributes.expansion_registry
- Experiment impact: Makes post-spark mechanical expansion claims auditable from primary event payloads with registry corroboration.
- Blocked claims: none
- Lane B requirement: No Lane B change required for expansion mapping; Lane B only changes spark-gate attribution.

### edge_labels

- Status: `direct`
- Meaning: Runtime edge labels expose conductance, geometry, delay, and coupling values used by the graph substrate.
- Artifact sources: GRC9V3 edge label payloads, snapshot edge_labels, telemetry graph checkpoint overlays
- Experiment impact: Supports substrate-level audits and replay checks for transport and geometry-dependent claims.
- Blocked claims: none
- Lane B requirement: No Lane B change required.

### coarse_graining_split

- Status: `direct`
- Meaning: Coarse G/Split reconstruction surfaces the coarse-graining relation used to compare graph partitions and local structure.
- Artifact sources: GRC9V3 coarse/Split runtime helpers, tests.models.test_grc_9_v3_coarse, coarse cache invalidation telemetry when present
- Experiment impact: Keeps coarse-graining evidence separated from source-language claims and cache diagnostics.
- Blocked claims: none
- Lane B requirement: No Lane B change required.

### sink_basin_hierarchy

- Status: `direct`
- Meaning: Basin ids, parent links, depth, and completion events expose the hierarchy surrounding spark and expansion events.
- Artifact sources: GRC9V3State.sink_set, hybrid_spark_candidate payload basin_id parent_id depth, hybrid_spark_completed payload hierarchy_parent and hierarchy_children, snapshot basin_attributes.hierarchy
- Experiment impact: Supports identity-event and daughter-basin interpretation when candidate, expansion, and completion evidence line up.
- Blocked claims: none
- Lane B requirement: No Lane B change required.

### column_h_cancellation_diagnostic

- Status: `derived`
- Meaning: Column-H-like cancellation is available only as an analysis proxy under the current Lane A baseline, not as a runtime spark predicate.
- Artifact sources: derived column-H proxy analysis, row/column basis reconstruction from direct Hessian fields, GRC9V3-LaneA-SparkGateTraceSchema.md reporting rule
- Experiment impact: Reports may say the derived column-H proxy was near zero at a candidate event, but may not attribute the Lane A spark to direct column-H gating.
- Blocked claims: Direct column-H triggered the spark is blocked in Lane A., Column-H is not a direct Lane A spark-gate predicate.
- Lane B requirement: canonical_column_h, Define a separate opt-in lane with runtime-computed column-H proxy fields, gate reasons, and positive/negative controls.

### full_port_history_motion_observer

- Status: `partial`
- Meaning: Complete motion claims require ordered port-occupancy changes across snapshot or checkpoint windows, not only a single candidate payload.
- Artifact sources: ordered snapshot/checkpoint sequences, topology endpoint slots and incidence, port-history reconstruction rules in GRC9V3-ArtifactSurfaceHardening.md
- Experiment impact: Single-step artifacts can support local port state, but full motion narratives require rerun or retained checkpoint sequences.
- Blocked claims: Full port-history motion is not proven from isolated candidate or summary artifacts.
- Lane B requirement: Add or retain ordered checkpoint windows and an analyzer that emits complete port-history motion tables.
