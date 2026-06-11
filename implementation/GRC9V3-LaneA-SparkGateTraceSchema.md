# GRC9V3 Lane A Spark-Gate Trace Schema

Schema id: `grc9v3_lane_a_spark_gate_trace_v1`

Runtime lane: `current_hybrid_signed_hessian`

Status: implementation-readiness artifact contract.

This document defines the artifact record used to audit `GRC9V3` Lane A spark
candidate evidence. It is a schema and reporting rule, not a runtime semantic
change.

Lane A candidates are signed-Hessian hybrid candidates. A derived column-H or
column-cancellation proxy may be reported as analysis evidence, but it is not a
spark predicate in Lane A.

Iteration 3 does not define a column-H proxy formula. Until a separate formula
specification exists, the proxy section must be emitted as `status: "blocked"`
or omitted by an extractor.

## Record Scope

Emit one trace record per `hybrid_spark_candidate` event.

Each record may attach follow-up evidence from later events in the same step:

- `hybrid_mechanical_expansion`
- `hybrid_spark_completed`

If a candidate has no matched expansion or completion event, record the
follow-up section with `present: false`.

## Evidence Status

Use these labels for every field group:

| Status | Meaning |
|---|---|
| `direct` | Read directly from an event payload, state field, checkpoint field, or telemetry extension. |
| `reconstructed` | Computed from direct runtime artifacts without changing runtime behavior. |
| `derived` | Analysis-level proxy computed from direct/reconstructed fields; not a runtime predicate. |
| `partial` | Some required source fields are missing or event/state windows are incomplete. |
| `blocked` | Required source fields are absent. Do not infer the claim. |

## Telemetry Contract Mapping

This trace schema is a candidate-centric artifact record. It is not a
replacement for `src/pygrc/telemetry/grc9v3_contract.py`.

The expected mapping to existing telemetry extensions is:

| Trace Schema Field | Telemetry Dataclass / Field | Notes |
|---|---|---|
| `candidate_event.candidate_node_id` | `GRC9V3SparkEvidence.candidate_node_id` | Same meaning. |
| `candidate_event.sink_node_id` | `GRC9V3SparkEvidence.sink_node_id` | Same meaning. |
| `candidate_event.depth` | `GRC9V3SparkEvidence.depth` | Same meaning. |
| `lane_a_gate_evidence.active_degree` | `GRC9V3SparkEvidence.active_degree` | Same meaning. |
| `lane_a_gate_evidence.saturation_gate` | `GRC9V3SparkEvidence.saturation_gate` | Same meaning. |
| `lane_a_gate_evidence.basin_interior_gate` | `GRC9V3SparkEvidence.basin_interior_gate` | Same meaning. |
| `lane_a_gate_evidence.signed_hessian_degeneracy_gate` | `GRC9V3SparkEvidence.signed_hessian_degeneracy_gate` | Same meaning. |
| `row_differential_evidence.gradient_norm` | `GRC9V3SparkEvidence.gradient_norm` | Same meaning. |
| `signed_hessian_evidence.min_signed_hessian` | `GRC9V3SparkEvidence.min_signed_hessian` | Same meaning. |
| `signed_hessian_evidence.signed_crossing_enabled` | `GRC9V3SparkEvidence.signed_crossing_enabled` | Same meaning. |
| `signed_hessian_evidence.signed_crossing_gate` | `GRC9V3SparkEvidence.signed_crossing_gate` | Same meaning. |
| `mechanical_expansion_followup.sink_node_id` | `GRC9V3ExpansionEvidence.parent_sink_id` | Trace keeps runtime payload naming; telemetry normalizes it to parent sink. |
| `mechanical_expansion_followup.module_node_ids` | `GRC9V3ExpansionEvidence.module_node_ids` | Same meaning. |
| `mechanical_expansion_followup.budget_before` | `GRC9V3ExpansionEvidence.budget_before` | Same meaning. |
| `mechanical_expansion_followup.budget_after` | `GRC9V3ExpansionEvidence.budget_after` | Same meaning. |
| `mechanical_expansion_followup.budget_error` | `GRC9V3ExpansionEvidence.budget_error` | Same meaning. |
| `mechanical_expansion_followup.budget_preservation_path` | `GRC9V3ExpansionEvidence.budget_preservation_path` | Same meaning. |
| `mechanical_expansion_followup.reassignment_map` | `GRC9V3ExpansionEvidence.reassignment_count` | Telemetry currently stores count only; full map requires event payload, cache, registry, or checkpoint evidence. |
| `identity_event_followup.stabilized_child_node_ids` | `GRC9V3CompletionEvidence.stabilized_child_node_ids` | Same meaning. |
| `identity_event_followup.stable_child_basin_count` | `GRC9V3CompletionEvidence.stable_child_basin_count` | Same meaning. |
| `identity_event_followup.hierarchy_parent` | `GRC9V3CompletionEvidence.hierarchy_parent` | Same meaning. |
| `identity_event_followup.hierarchy_children` | `GRC9V3CompletionEvidence.hierarchy_children` | Same meaning. |

Fields not present in the telemetry dataclasses, such as
`reassignment_map_source`, `gradient_row_basis`, `signed_hessian_row_basis`, and
derived column-H proxy fields, require direct event payloads, runtime state,
checkpoint fields, or future artifact extraction code.

## Top-Level Shape

```json
{
  "schema_id": "grc9v3_lane_a_spark_gate_trace_v1",
  "model_family": "grc9v3",
  "spark_lane_id": "current_hybrid_signed_hessian",
  "run": {},
  "candidate_event": {},
  "lane_a_gate_evidence": {},
  "row_differential_evidence": {},
  "signed_hessian_evidence": {},
  "mechanical_expansion_followup": {},
  "identity_event_followup": {},
  "derived_column_h_proxy": {},
  "blocked_observations": [],
  "reporting_rules": {}
}
```

## Run Metadata

```json
{
  "run": {
    "run_id": "string",
    "fixture_id": "string",
    "seed": "integer|null",
    "params_identity": "string|null",
    "dt": "number|null",
    "artifact_source": "StepResult.events|telemetry_event_rows|checkpoint_replay|mixed",
    "artifact_schema_version": "string|null"
  }
}
```

`params_identity` should match `GRC9V3State.params_identity` or
`GRCParams.params_hash` when available.

`dt` is optional run-level context. Per-candidate runtime time belongs in
`candidate_event.time` when a state, checkpoint, or telemetry row exposes it.

## Candidate Event

Source priority:

1. `StepResult.events[kind=hybrid_spark_candidate].payload`
2. telemetry event row `family_extensions.grc9v3.spark_evidence`
3. checkpoint/state replay that reconstructs the same candidate condition

```json
{
  "candidate_event": {
    "status": "direct|reconstructed|partial|blocked",
    "event_kind": "hybrid_spark_candidate",
    "step_index": "integer",
    "time": "number|null",
    "event_index": "integer|null",
    "candidate_node_id": "integer",
    "sink_node_id": "integer|null",
    "basin_id": "integer|string|null",
    "parent_id": "integer|string|null",
    "depth": "integer|null"
  }
}
```

The `candidate_node_id` and `sink_node_id` may be equal in current Lane A
payloads. Do not infer a persistent child identity from this event.

## Lane A Gate Evidence

```json
{
  "lane_a_gate_evidence": {
    "status": "direct|reconstructed|partial|blocked",
    "gate_family": "current_hybrid_signed_hessian",
    "active_degree": "integer|null",
    "saturation_gate": "boolean|null",
    "sink_status": {
      "status": "direct|reconstructed|partial|blocked",
      "is_sink": "boolean|null",
      "source": "candidate_payload|state.sink_set|telemetry|checkpoint|unavailable"
    },
    "basin_interior_gate": "boolean|null",
    "signed_hessian_degeneracy_gate": "boolean|null",
    "candidate_condition": "boolean|null",
    "not_a_gate": [
      "derived_column_h_proxy"
    ]
  }
}
```

`sink_status` is direct when it comes from a state/checkpoint `sink_set`, and
reconstructed when inferred from a matching telemetry or event context. If only
`sink_node_id` exists in the candidate payload, record
`source: "candidate_payload"` and do not claim an independently observed sink
set.

`candidate_condition` is the boolean conjunction of `saturation_gate`,
`basin_interior_gate`, and `signed_hessian_degeneracy_gate`. The textual rule is
kept in `reporting_rules.lane_a_candidate_condition_rule`.

## Row Differential Evidence

```json
{
  "row_differential_evidence": {
    "status": "direct|reconstructed|partial|blocked",
    "source": "candidate_payload|GRC9V3State.nodes|checkpoint|telemetry|unavailable",
    "gradient_norm": "number|null",
    "eps_gradient": "number|null",
    "gradient_row_basis": ["number"],
    "basin_interior_gate": "boolean|null"
  }
}
```

`gradient_norm` and `eps_gradient` are direct in current candidate payloads.
`gradient_row_basis` is direct only when node state or checkpoint state is
available for the candidate step.

## Signed-Hessian Evidence

```json
{
  "signed_hessian_evidence": {
    "status": "direct|reconstructed|partial|blocked",
    "source": "candidate_payload|GRC9V3State.nodes|checkpoint|telemetry|unavailable",
    "hessian_backend": "row_basis_diagonal|weighted_least_squares|null",
    "signed_hessian_row_basis": ["number"],
    "min_signed_hessian": "number|null",
    "eps_spark": "number|null",
    "signed_hessian_degeneracy_gate": "boolean|null",
    "signed_crossing_enabled": "boolean|null",
    "signed_crossing_gate": "boolean|null",
    "signed_crossing_status": "capability_disabled|history_unavailable|evaluated|null"
  }
}
```

`min_signed_hessian`, `eps_spark`, `signed_hessian_degeneracy_gate`,
`signed_crossing_enabled`, and `signed_crossing_gate` are direct in current
candidate payloads. `hessian_backend`, `signed_hessian_row_basis`, and
`signed_crossing_status` require state, checkpoint, or cached-quantity evidence.

## Mechanical Expansion Follow-Up

Match an expansion to a candidate by:

1. same `step_index`,
2. expansion payload `sink_node_id == candidate_event.sink_node_id`,
3. expansion payload `expansion_id`, when present.

```json
{
  "mechanical_expansion_followup": {
    "present": "boolean",
    "status": "direct|reconstructed|partial|blocked",
    "event_kind": "hybrid_mechanical_expansion|null",
    "step_index": "integer|null",
    "sink_node_id": "integer|null",
    "expansion_id": "string|null",
    "module_node_ids": ["integer"],
    "reassignment_map_source": "event_payload|cached_quantities.last_hybrid_expansion|expansion_registry|snapshot_basin_attributes_expansion_registry|unavailable",
    "reassignment_map": {},
    "budget_measure": "string|null",
    "budget_before": "number|null",
    "budget_after": "number|null",
    "budget_error": "number|null",
    "budget_preservation_path": "string|null"
  }
}
```

During Iteration 3, the trace schema recognizes the event payload as the primary
direct source when it is available. The full extractor priority rule over cache,
registry, and checkpoint overlays is handled by Iteration 4 artifact hardening.

## Identity Event Follow-Up

Match a completion event to a candidate by:

1. same `step_index`,
2. completion payload `expansion_id == mechanical_expansion_followup.expansion_id`,
3. completion payload `candidate_node_id == candidate_event.candidate_node_id`.

```json
{
  "identity_event_followup": {
    "present": "boolean",
    "status": "direct|reconstructed|partial|blocked",
    "event_kind": "hybrid_spark_completed|null",
    "step_index": "integer|null",
    "completed_identity_event": "boolean",
    "expansion_id": "string|null",
    "parent_basin_id": "integer|string|null",
    "stabilized_child_node_ids": ["integer"],
    "stable_child_basin_count": "integer|null",
    "hierarchy_parent": "string|null",
    "hierarchy_children": ["string"]
  }
}
```

Use `completed_identity_event` in reports. Avoid the ambiguous phrase
`completed spark` unless quoting the runtime event kind exactly.

## Derived Column-H / Cancellation Proxy

This section is optional and must remain analysis-only in Lane A.

No `grc9v3_column_h_proxy_v0` formula is defined by this readiness pass. The
default valid Iteration 3 value is:

```json
{
  "status": "blocked",
  "predicate_role": "analysis_proxy_only",
  "formula_status": "undefined_in_iteration_3",
  "formula_version": null,
  "near_zero_threshold": null,
  "near_zero": null,
  "must_not_claim_direct_gate": true
}
```

An extractor must not populate `by_column`, `min_abs_proxy`, `near_zero`, or a
non-null `formula_version` until a separate formula specification defines:

- the per-column expression,
- the required source fields,
- orientation conventions,
- the near-zero threshold,
- blocked/partial handling.

```json
{
  "derived_column_h_proxy": {
    "status": "derived|partial|blocked",
    "predicate_role": "analysis_proxy_only",
    "formula_status": "defined|undefined_in_iteration_3",
    "formula_version": "string|null",
    "candidate_source_state_fields": [
      "GRC9V3State.topology",
      "GRC9V3State.port_edges",
      "GRC9V3State.nodes",
      "GRC9V3State.base_conductance",
      "GRC9V3State.flux_coupling",
      "GRC9V3NodeState.net_flux_summary"
    ],
    "candidate_source_artifact_fields": [
      "snapshot.topology",
      "snapshot.basin_attributes.nodes",
      "snapshot.edge_labels",
      "snapshot.dynamics.state.port_edges",
      "snapshot.dynamics.state.cached_quantities",
      "event_rows.family_extensions.grc9v3"
    ],
    "candidate_source_helpers": [
      "port_to_rc",
      "oriented PortEdge.flux_uv"
    ],
    "by_column": {
      "1": {},
      "2": {},
      "3": {}
    },
    "min_abs_proxy": "number|null",
    "near_zero_threshold": "number|null",
    "near_zero": "boolean|null",
    "must_not_claim_direct_gate": true
  }
}
```

If no formula specification is available, set `status: "blocked"` and add a
`blocked_observations` row. If a future formula exists but only a subset of its
source fields is available, set `status: "partial"` and do not use the proxy for
a positive claim.

## Blocked Observation Row

```json
{
  "blocked_observations": [
    {
      "field_group": "derived_column_h_proxy",
      "field": "formula_version",
      "reason": "no column-H proxy formula is defined for Iteration 3",
      "effect": "column-H proxy cannot be evaluated for this candidate"
    }
  ]
}
```

## Reporting Rules

```json
{
  "reporting_rules": {
    "allowed_column_h_sentence": "derived column-H proxy was near zero at the candidate event",
    "forbidden_without_lane_b": "column-H triggered the spark",
    "lane_a_candidate_condition_rule": "saturation_gate AND basin_interior_gate AND signed_hessian_degeneracy_gate",
    "candidate_term": "spark_candidate",
    "expansion_term": "mechanical_expansion",
    "identity_term": "completed_identity_event"
  }
}
```

Allowed Lane A wording:

```text
The candidate satisfied the Lane A signed-Hessian gate. A derived column-H
proxy was near zero at the candidate event.
```

Forbidden without Lane B or a direct runtime field:

```text
Column-H triggered the spark.
```

## Minimal Valid Record

A minimal valid record must include:

- `schema_id`
- `spark_lane_id`
- `candidate_event.event_kind`
- `candidate_event.step_index`
- `candidate_event.candidate_node_id`
- `lane_a_gate_evidence.active_degree`
- `lane_a_gate_evidence.saturation_gate`
- `row_differential_evidence.gradient_norm`
- `row_differential_evidence.eps_gradient`
- `signed_hessian_evidence.min_signed_hessian`
- `signed_hessian_evidence.eps_spark`
- `signed_hessian_evidence.signed_hessian_degeneracy_gate`
- `mechanical_expansion_followup.present`
- `identity_event_followup.present`
- `derived_column_h_proxy.status`
- `derived_column_h_proxy.predicate_role`
- `derived_column_h_proxy.formula_status`

If any minimal candidate-gate field is absent, the record is still admissible
only with `candidate_event.status: "partial"` or `"blocked"` and a blocked
observation explaining the missing source.
