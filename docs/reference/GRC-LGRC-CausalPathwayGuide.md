# GRC/LGRC Causal Pathway Guide

**Status:** Phase 8 Iteration 109 evidence-derived selection guide frozen

**Machine guide:** [`grc-lgrc-causal-pathway-selection-guide.json`](../../specs/grc-lgrc-causal-pathway-selection-guide.json)

**Registry:** [`grc-lgrc-causal-pathway-contracts.json`](../../specs/grc-lgrc-causal-pathway-contracts.json)

**Evidence crosswalk:** [`grc-lgrc-causal-pathway-evidence-crosswalk.json`](../../specs/grc-lgrc-causal-pathway-evidence-crosswalk.json)

**Composition matrix:** [`GRC-LGRC-CompositionMatrix.md`](./GRC-LGRC-CompositionMatrix.md)

## Purpose And Authority

Use this guide to select an existing GRC9V3/LGRC9V3 pathway or registered
directional crossing while retaining its owner, residue, evidence status, and
claim ceiling. The guide is derived from the registry, crosswalk, and matrix.
It is not an execution API and cannot create pathway or crossing facts.

The guide distinguishes:

```text
existing pathway
existing lawful native composition
lawful composition with explicit adapter
diagnostic-only composition
producer-mediated composition
registered unsupported crossing
invalid relabel
unregistered directional pair
ambiguous registered crossing
```

An unregistered pair is unclassified, not evidence of a missing crossing. A
registered missing crossing does not authorize an extension. Composition
status is not maturity, and no selection establishes ecology or agency.

## Selection Sequence

1. State the required time semantics.
2. State whether the route is explicit, configured, selected over supplied
   candidates, or expected to form.
3. State the required retained relation.
4. Select the pathway whose registry contract actually supplies that surface.
5. If two pathways must interact, look up the exact directional matrix row.
6. Preserve adapter/producer ownership, configured residue, claim ceiling, and
   blocked relabels from the authoritative records.
7. If no exact row exists, report the pair as unregistered and audit it; do not
   infer `unsupported_missing_crossing` from absent matrix coverage.
8. If several rows share endpoints, specify the required crossing semantics;
   do not select the first match.

## Time-Semantics Index

| Required semantics | Registered pathways |
| --- | --- |
| `caller_checkpoint` | `lgrc9v3.diagnostic_grc_reconstruction` |
| `checkpoint_time` | `pygrc.restoration_replay_identity` |
| `configuration_time` | `lgrc9v3.configured_flux_route` |
| `derived_event_time` | `lgrc9v3.causal_history_annotation`, `lgrc9v3.fixed_topology_eligibility` |
| `event_time` | `lgrc9v3.boundary_birth`, `lgrc9v3.causal_pulse_surface_lineage`, `lgrc9v3.causal_spark_topology_integration`, `lgrc9v3.collapse_reabsorption`, `lgrc9v3.explicit_packet_transport`, `lgrc9v3.multi_basin_record_validation`, `lgrc9v3.native_route_arbitration`, `lgrc9v3.proper_time_identity_acceptance` |
| `explicit_call` | `lgrc9v3.native_route_arbitration` |
| `global_synchronous_step` | `grc9v3.front_capacity_growth`, `grc9v3.hybrid_spark_refinement`, `grc9v3.identity_basin_reconstruction`, `grc9v3.legacy_inactive_port_growth`, `grc9v3.sink_compatibility_choice`, `grc9v3.synchronous_update_cycle` |
| `producer_frontier` | `lgrc9v3.boundary_birth`, `lgrc9v3.feedback_eligibility_producer`, `lgrc9v3.pulse_substrate_coupling_producer`, `lgrc9v3.route_aspect_surplus` |
| `producer_frontier_then_event_time` | `lgrc9v3.configured_flux_route`, `lgrc9v3.feedback_eligibility_producer`, `lgrc9v3.pulse_substrate_coupling_producer`, `lgrc9v3.route_aspect_surplus` |
| `proper_time_and_event_time` | `lgrc9v3.proper_time_identity_evaluation` |
| `replay_window` | `lgrc9v3.multi_basin_record_validation`, `pygrc.restoration_replay_identity` |
| `synchronous_limit_at_checkpoint` | `lgrc9v3.diagnostic_grc_reconstruction` |

Time compatibility at a crossing still comes from its matrix row. Sharing a
time label does not establish interoperability.

## Route And Authority Questions

| Demand | Candidate pathway | Boundary |
| --- | --- | --- |
| Explicit packet endpoints and schedule | `lgrc9v3.explicit_packet_transport` | Route, amount, and times remain supplied. |
| Configured causal route producer | `lgrc9v3.configured_flux_route` | Configuration is not route formation. |
| Configured pole/aspect surplus | `lgrc9v3.route_aspect_surplus` | Pole meaning and thresholds remain configured. |
| Selection over supplied candidates | `lgrc9v3.native_route_arbitration` | Candidate and score formation remain separate. |
| Route expected from state/history/current | No generic V1 pathway | Use a registered mediated crossing or record the exact unclassified/missing relation. |

For every candidate, answer separately who owns direction, funding,
eligibility, scheduling, commitment, and reception. Native commitment does not
naturalize externally authored eligibility.

## Retained Relations

| Required relation | Candidate surface | Boundary |
| --- | --- | --- |
| Present synchronous state | `grc9v3.synchronous_update_cycle` | Current transport/continuity only. |
| Event-time packet history | `lgrc9v3.explicit_packet_transport` | Packet/queue settlement only. |
| Causal annotation | `lgrc9v3.causal_history_annotation` | Diagnostic unless a registered producer consumes it. |
| Pulse surface lineage | `lgrc9v3.causal_pulse_surface_lineage` | Configured surface records and lineage only. |
| Persistent topology event | `lgrc9v3.boundary_birth`, `lgrc9v3.collapse_reabsorption`, or `lgrc9v3.causal_spark_topology_integration` | Use the mechanism-specific contract; no generic admission follows. |
| Snapshot/reset/replay relation | `pygrc.restoration_replay_identity` | Versioned restoration identity, not semantic identity. |

## Composition Outcomes

The I108 matrix contains 26 representative
directional rows: 10 lawful native,
1 lawful with explicit adapter,
2 diagnostic only,
4 producer mediated,
3 unsupported missing crossings,
and 6 invalid relabels.

| Case | Demand | Resolution | Composition | Owner |
| --- | --- | --- | --- | --- |
| `SEL-01` | Existing event-time packet pathway | `existing_pathway` | `none` | `none` |
| `SEL-02` | Native packet lifecycle crossing | `existing_lawful_composition` | `CMP-02` | `native` |
| `SEL-03` | Explicit cross-runtime front-capacity adapter | `existing_composition_with_explicit_adapter` | `CMP-26` | `library_construction_adapter_invoked_by_caller` |
| `SEL-04` | Post-commit multi-basin diagnostic | `diagnostic_surface_only` | `CMP-24` | `runtime_diagnostic_hook` |
| `SEL-05` | Producer-owned feedback eligibility | `producer_mediated_composition` | `CMP-20` | `installed_producer` |
| `SEL-06` | Missing sink-choice to route-schedule crossing | `precise_missing_crossing` | `CMP-06` | `none` |
| `SEL-07` | Diagnostic-as-behavioral relabel rejection | `rejected_invalid_relabel` | `CMP-05` | `none` |
| `SEL-08` | Arbitration-backed behavioral topology commit | `existing_lawful_composition` | `CMP-07` | `native` |
| `SEL-09` | Unregistered pair remains unclassified | `unregistered_not_classified` | `none` | `none` |
| `SEL-10` | Multiple crossings require semantic disambiguation | `ambiguous_registered_crossing` | `none` | `none` |

## Worked Cases

### SEL-01: Existing event-time packet pathway

Execute a declared packet schedule with debit, in-flight retention, arrival, and target credit without claiming route formation.

```text
resolution = existing_pathway
pathways = lgrc9v3.explicit_packet_transport
composition = none
composition status = not_applicable_pathway_only
adapter/producer owner = none
missing relation = none
```

Selected pathways: `lgrc9v3.explicit_packet_transport`. Configured residue: `route endpoints`, `amount`, `departure/arrival times`.

Claim ceiling: native packet accounting and queue-processing mechanics

Blocked nearby interpretation: `substrate-formed route`, `native departure reason`, `agency`.

### SEL-02: Native packet lifecycle crossing

Carry one supplied packet identity through schedule, debit, in-flight state, and arrival credit.

```text
resolution = existing_lawful_composition
pathways = lgrc9v3.explicit_packet_transport
composition = CMP-02
composition status = lawful_native
adapter/producer owner = native
missing relation = none
```

Selected pathways: `lgrc9v3.explicit_packet_transport`. Configured residue: `route endpoints`, `amount`, `departure/arrival times`.

Claim ceiling: Native packet debit/arrival mechanics; route, amount, and schedule remain supplied.

Blocked nearby interpretation: `native route formation`, `generic work admission`.

### SEL-03: Explicit cross-runtime front-capacity adapter

Place GRC front-capacity state at a declared LGRC event-time boundary-birth frontier while keeping construction ownership visible.

```text
resolution = existing_composition_with_explicit_adapter
pathways = grc9v3.front_capacity_growth, lgrc9v3.boundary_birth
composition = CMP-26
composition status = lawful_with_explicit_adapter
adapter/producer owner = library_construction_adapter_invoked_by_caller
missing relation = none
```

Selected pathways: `grc9v3.front_capacity_growth`, `lgrc9v3.boundary_birth`. Configured residue: `GRCL9V3 front-capacity eligibility mode`, `front-capacity map`, `birth alpha`, `RNG policy`, `front propagation`, `eligibility mode`, `front-capacity source`, `birth probability`, `edge delay`.

Claim ceiling: Lawful explicit construction adapter; not native cross-runtime formation or inherited event history.

Blocked nearby interpretation: `lawful_native`, `automatic time-semantics conversion`, `native role formation`.

### SEL-04: Post-commit multi-basin diagnostic

Read validated child-basin and flow-window records after an arbitration-backed topology commit without treating records as the mutation.

```text
resolution = diagnostic_surface_only
pathways = lgrc9v3.native_route_arbitration, lgrc9v3.multi_basin_record_validation
composition = CMP-24
composition status = diagnostic_only
adapter/producer owner = runtime_diagnostic_hook
missing relation = none
```

Selected pathways: `lgrc9v3.native_route_arbitration`, `lgrc9v3.multi_basin_record_validation`. Configured residue: `candidate schema`, `score/order policy`, `claim flags`, `budget prediction`, `multi-basin policy`, `window`, `metrics`, `control thresholds`.

Claim ceiling: Diagnostic records over a committed native/configured topology event.

Blocked nearby interpretation: `basin formation by record`, `general robustness`.

### SEL-05: Producer-owned feedback eligibility

Let an installed producer read a feedback surface and schedule native packet mechanics while retaining eligibility and direction ownership.

```text
resolution = producer_mediated_composition
pathways = lgrc9v3.feedback_eligibility_producer, lgrc9v3.explicit_packet_transport
composition = CMP-20
composition status = producer_mediated
adapter/producer owner = installed_producer
missing relation = none
```

Selected pathways: `lgrc9v3.feedback_eligibility_producer`, `lgrc9v3.explicit_packet_transport`. Configured residue: `feedback masks`, `thresholds`, `route`, `amount`, `route endpoints`, `departure/arrival times`.

Claim ceiling: Producer-mediated feedback eligibility followed by native packet mechanics.

Blocked nearby interpretation: `lawful_native`, `native feedback admission`.

### SEL-06: Missing sink-choice to route-schedule crossing

Use a GRC sink-compatibility result to schedule LGRC route work without inventing an admission bridge.

```text
resolution = precise_missing_crossing
pathways = grc9v3.sink_compatibility_choice, lgrc9v3.configured_flux_route
composition = CMP-06
composition status = unsupported_missing_crossing
adapter/producer owner = none
missing relation = CMP-06
```

Selected pathways: `grc9v3.sink_compatibility_choice`, `lgrc9v3.configured_flux_route`. Configured residue: `choice backend`, `epsilon choice`, `epsilon collapse`, `learning rate`, `budget policy`, `route`, `target`, `amount source`, `arrival delay`.

Claim ceiling: Unsupported until an explicit admission and scheduling relation is supplied.

Blocked nearby interpretation: `semantic choice`, `native route formation`.

### SEL-07: Diagnostic-as-behavioral relabel rejection

Treat an explicit GRC reconstruction over LGRC state as if ordinary LGRC packet behavior had consumed it.

```text
resolution = rejected_invalid_relabel
pathways = lgrc9v3.diagnostic_grc_reconstruction, lgrc9v3.explicit_packet_transport
composition = CMP-05
composition status = invalid_relabel
adapter/producer owner = none
missing relation = none
```

Selected pathways: `lgrc9v3.diagnostic_grc_reconstruction`, `lgrc9v3.explicit_packet_transport`. Configured residue: `diagnostic modes`, `copied params`, `route endpoints`, `amount`, `departure/arrival times`.

Claim ceiling: No ordinary LGRC behavior claim is allowed.

Blocked nearby interpretation: `diagnostic_as_behavior`, `native packet admission`.

### SEL-08: Arbitration-backed behavioral topology commit

Commit the selected arbitration candidate through collapse and reabsorption while keeping candidate and score formation external.

```text
resolution = existing_lawful_composition
pathways = lgrc9v3.native_route_arbitration, lgrc9v3.collapse_reabsorption
composition = CMP-07
composition status = lawful_native
adapter/producer owner = native
missing relation = none
```

Selected pathways: `lgrc9v3.native_route_arbitration`, `lgrc9v3.collapse_reabsorption`. Configured residue: `candidate schema`, `score/order policy`, `claim flags`, `budget prediction`, `collapse policy`, `explicit or arbitration input`, `reabsorption modes`.

Claim ceiling: Native arbitration-to-collapse commit mechanics; candidate and score formation remain external/configured.

Blocked nearby interpretation: `native candidate formation`, `semantic choice`.

### SEL-09: Unregistered pair remains unclassified

Ask whether synchronous GRC transport composes directly into restoration identity when I108 registered no such crossing.

```text
resolution = unregistered_not_classified
pathways = grc9v3.synchronous_update_cycle, pygrc.restoration_replay_identity
composition = none
composition status = unregistered_not_classified
adapter/producer owner = none
missing relation = unclassified_directional_pair_requires_source_audit
```

Selected pathways: `grc9v3.synchronous_update_cycle`, `pygrc.restoration_replay_identity`. Configured residue: `constitutive modes`, `backend selections`, `evolution parameters`, `identity schema version`, `legacy compatibility policy`, `replay scope`.

Claim ceiling: No composition claim; the directional pair was not registered in I108.

Blocked nearby interpretation: `unregistered pair as unsupported_missing_crossing`, `endpoint evidence as crossing evidence`, `automatic extension authorization`.

### SEL-10: Multiple crossings require semantic disambiguation

Select an arbitration-to-collapse relation without specifying whether direct commit or lineage-aware transport is required.

```text
resolution = ambiguous_registered_crossing
pathways = lgrc9v3.native_route_arbitration, lgrc9v3.collapse_reabsorption
composition = none
composition status = ambiguous_registered_crossing
adapter/producer owner = none
missing relation = none
```

Selected pathways: `lgrc9v3.native_route_arbitration`, `lgrc9v3.collapse_reabsorption`. Configured residue: `candidate schema`, `score/order policy`, `claim flags`, `budget prediction`, `collapse policy`, `explicit or arbitration input`, `reabsorption modes`.

Claim ceiling: No selection until the required crossing semantics are specified.

Blocked nearby interpretation: `first matching composition as selected crossing`, `shared endpoints as equivalent composition semantics`.

## Diagnostic Versus Behavioral Pair

`SEL-04` and `SEL-08` begin from
`lgrc9v3.native_route_arbitration`, but they do not have the same crossing.
`CMP-07` commits selected topology behavior through collapse/reabsorption.
`CMP-24` emits diagnostic multi-basin records after a commit. Shared origin and
current crossing evidence do not let the diagnostic record become the
mutation, and the behavioral commit does not establish the record's broader
interpretation.

## When No Registered Crossing Fits

Record the two endpoint pathway IDs, required direction, missing state/time/
budget/authority mapping, proposed adapter or producer owner, native mechanics
retained, claim ceiling, and controls. If the pair is absent from the
representative matrix, call it `unregistered_not_classified` until a source
audit establishes one of the six composition statuses.

## Claim Boundary

Only runtime artifacts, tests, and experiment evidence can establish that a
selected pathway executed. This guide does not admit a primitive, building
block, motif, regime, support relation, role, shared-medium behavior, agency,
native Read-Back, or N32.
