# Artifact Surface Inventory

Experiment:

```text
2026-05-N03-grc9v3-polarized-basin-loops
```

Iteration:

```text
Iteration 1. Artifact Surface Inventory
```

Status:

```text
complete
```

## Summary

The first implementation should use an experiment-local fixed-topology
continuity runner around existing `GRC9V3` state/model surfaces.

Selected runner:

```text
runner_mode = "fixed_topology_continuity_runner"
model_family = "GRC9V3"
```

Do not use full `GRC9V3.step()` for the first pass. The full step includes
hybrid spark stages, growth, boundary behavior, choice/collapse learning,
continuity, budget correction, and final rebuilds. That is broader than the
fixed-topology loop experiment needs.

Selected parent-basin evidence mode:

```text
same_parent_basin_mode = "configured_parent_region_only"
```

Rationale: `GRC9V3State` exposes measured basin surfaces (`sink_set`,
`basins`, node `basin_id`, `parent_id`, `basin_mass`), but the first loop
fixtures should not overclaim measured flux-successor basin membership before
the fixed-topology runner and region masks are implemented. Stronger
`flux_successor_basin` evidence can be promoted later.

## Runtime Surfaces

### Available Fixed-Topology Calls

These calls exist and are suitable for a fixed-topology continuity runner when
used without topology-changing stages:

| Surface | Status | Notes |
|---|---|---|
| `rebuild_differential_state()` | available | materializes gradients, signed Hessian row basis, and net flux summaries |
| `rebuild_transport_state()` | available | computes conductance, potentials, flux, and edge labels |
| `apply_continuity()` | available | applies one coherence update from current antisymmetric edge flux |
| `enforce_quadrature_budget()` | available | returns budget summary and stores `last_quadrature_budget` |
| `rebuild_identity_state()` | available | rebuilds sink/basin identity surfaces without changing topology |
| `compute_observables()` | available | exposes node/edge count, active basin count, hierarchy/choice/collapse counts |

### Excluded Full-Step Stages

These are available in `GRC9V3`, but out of scope for the first loop runner:

| Surface | Status for this experiment | Reason |
|---|---|---|
| `detect_hybrid_spark_candidates()` | excluded from runner | diagnostic candidate surface only; spark refinement is out of scope |
| `apply_hybrid_sparks()` | disallowed | may emit mechanical expansion |
| `apply_growth()` | disallowed | may create new nodes when enabled |
| `apply_boundary_behavior()` | disallowed | boundary pruning/adaptation is out of scope |
| `rebuild_choice_state()` | disallowed in first runner | choice/collapse learning is not part of fixed loop evidence |
| full `step()` | non-default escape hatch only | includes several topology/semantic phases before continuity |

## Observable Inventory

### Node Coherence History

Status:

```text
available
```

Source:

```text
GRC9V3State.nodes[node_id].coherence
```

Experiment use:

- capture `C_pre`;
- capture `C_post_continuity`;
- capture `C_post_budget`;
- derive `C_source`, `C_sink`, source/sink deltas, and region mass histories.

### Edge Flux And Conductance History

Status:

```text
available
```

Sources:

```text
GRC9V3State.port_edges[edge_id].flux_uv
GRC9V3State.port_edges[edge_id].conductance
GRC9V3State.base_conductance[edge_id]
GRC9V3State.flux_coupling[edge_id]
GRC9V3State.geometric_length[edge_id]
GRC9V3State.temporal_delay[edge_id]
GRC9V3State.potential[node_id]
```

Orientation convention:

```text
oriented_flux(edge, node) =
    +flux_uv if node == edge.node_u
    -flux_uv if node == edge.node_v
```

This matches `GRC9V3._oriented_flux()` and `apply_continuity()`: positive
oriented flux contributes positive divergence at the local node, and continuity
updates coherence by `Delta C = -dt * divergence`.

Experiment use:

- reconstruct region export/import from boundary edges;
- reconstruct `J_forward` and `J_return`;
- avoid relying on `net_flux_summary` alone.

### Edge Endpoint And Port Orientation

Status:

```text
available
```

Sources:

```text
PortEdge.node_u
PortEdge.port_u
PortEdge.node_v
PortEdge.port_v
PortGraphBackend.edge_ports(edge_id)
PortGraphBackend.incident_edge_ids(node_id)
```

Experiment use:

- validate masks reference live edges;
- reconstruct edge direction and local port evidence;
- support future ported-ring fixture checks.

### Basin / Sink / Parent-Basin Evidence

Status:

```text
partial
```

Sources:

```text
GRC9V3State.sink_set
GRC9V3State.basins
GRC9V3NodeState.basin_id
GRC9V3NodeState.parent_id
GRC9V3NodeState.basin_mass
GRC9V3NodeState.depth
GRC9V3State.hierarchy
```

First-pass decision:

```text
same_parent_basin_mode = "configured_parent_region_only"
```

Notes:

- `sink_set` is a runtime attractor/identity surface, not the experiment's
  sink-aspect mask.
- `source_aspect_nodes` and `sink_aspect_nodes` remain experiment masks.
- Full `flux_successor_basin` evidence is deferred until the first runner and
  fixture path evidence are implemented.

### Budget Audit

Status:

```text
available
```

Sources:

```text
sum(node.coherence)
GRC9V3.enforce_quadrature_budget()
GRC9V3State.cached_quantities["last_quadrature_budget"]
```

Available budget summary fields from the core helper:

```text
quadrature_mode
budget_correction_method
budget_before
budget_after_negative_clamp
budget_target
budget_after
budget_error
negative_mass_correction
```

Derived experiment fields:

```text
before_continuity
after_continuity
after_correction
error_pre_correction
error_post_correction
correction_magnitude
simplex_projection_count
uniform_shift_count
```

`simplex_projection_count` and `uniform_shift_count` are runner-derived counts
because the core budget helper returns a per-call summary, not accumulated
experiment counters.

### Fixed-Topology Audit

Status:

```text
available
```

Sources:

```text
PortGraphBackend.iter_live_node_ids()
PortGraphBackend.iter_live_edge_ids()
GRC9V3State.event_log
GRC9V3.compute_observables()
```

Experiment use:

- compare initial/final node count;
- compare initial/final edge count;
- count topology event kinds if any appear;
- block first-pass loop claims on topology change.

### Topology Config Flags

Status:

```text
derived
```

Native config surfaces:

```text
evolution.lambda_birth
constitutive_semantic_modes.boundary_mode
constitutive_semantic_modes.spark_lane
constitutive_semantic_modes.enable_column_h_threshold
constitutive_semantic_modes.enable_column_h_sign_crossing
```

First-pass runner config interpretation:

```text
topology_events_enabled = false
spark_enabled = false
growth_enabled = false
boundary_behavior_enabled = false
birth_enabled = false
```

Rationale:

The fixed-topology runner disables topology events primarily by not invoking
topology-changing phases. `lambda_birth = 0.0` should also be used for safety,
but not invoking `apply_growth()` is the stronger execution-surface guarantee.

### Region Export / Import Evidence

Status:

```text
derived
```

Required source:

```text
edge-level flux_uv plus region masks
```

Derived fields:

```text
source_export
sink_import
J_forward
J_return
source_delta_C_pre_budget
sink_delta_C_pre_budget
source_delta_C_post_budget
sink_delta_C_post_budget
```

Implementation note:

Do not treat node `net_flux_summary` as authoritative loop evidence. It is a
useful node diagnostic, but region export/import must be reconstructable from
edge-level flux and masks.

### Time-Series Artifact Storage

Status:

```text
available as experiment-local artifact
```

Chosen first storage:

```text
canonical JSONL
```

Each record should contain one runner tick / measurement surface. The summary
report should include:

```text
timeseries.artifact_path
timeseries.artifact_digest
```

Digest:

```text
sha256 over the emitted time-series file bytes
```

Acceptable later alternatives:

```text
CSV
NPZ
canonical JSON
```

JSONL is selected first because it is readable, append-friendly, and easy to
hash.

## Runner Decision

First runner:

```text
fixed_topology_continuity_runner
```

Model substrate:

```text
GRC9V3
```

Default call sequence:

```text
C_pre
rebuild_differential_state()
rebuild_transport_state()
capture transport_state / flux_uv
apply_continuity()
capture C_post_continuity
enforce_quadrature_budget()
capture C_post_budget and budget summary
rebuild_differential_state()
rebuild_transport_state()
rebuild_identity_state()
compute_observables()
experiment-local loop observables
```

Blocked / non-default runner:

```text
full_step_runner
```

Reason:

`GRC9V3.step()` includes spark stages, choice/collapse learning, growth,
boundary behavior, continuity, budget correction, and final rebuilds. It can be
used only as a separately declared escape hatch with per-step topology proof.

## README Runner Mapping

| README step | Inventory result | Default runtime phase |
|---|---|---|
| compute basin attributes | available | `rebuild_differential_state()`, `rebuild_identity_state()` |
| compute `K_i`-like local state | available as model diagnostics | `rebuild_differential_state()` |
| update conductances | available | `rebuild_transport_state()` |
| compute potentials | available | `rebuild_transport_state()` |
| compute antisymmetric flux | available | `rebuild_transport_state()` / `flux_uv` |
| update `C_i` by continuity | available | `apply_continuity()` |
| enforce budget / projection | available | `enforce_quadrature_budget()` |
| identify basins | partial | `rebuild_identity_state()` plus configured-parent evidence |
| compute source/sink summaries | derived | experiment-local postprocessor |
| compute loop scores | derived | experiment-local postprocessor |
| assign L-level | derived | experiment-local classifier |

## Fixture Decision

First serious GRC9V3 fixture:

```text
grc9v3_ported_ring_v1
```

Analysis/control fixture:

```text
simple_unported_ring_v1
```

`simple_unported_ring_v1` may be used for synthetic metric tests and post-hoc
classifier controls. GRC9V3 loop evidence should use the ported ring unless the
run explicitly declares itself an analysis/control run.

## Control Feasibility

| Control | Feasibility | Notes |
|---|---|---|
| `shuffled_conductance` | partial | runtime form must specify whether shuffling affects initial fixture conductance or per-tick rebuilt conductance |
| `zero_flux_reset` | available / sometimes not applicable | useful for snapshot/replay lanes; fresh rebuild-only lanes can mark it not applicable |
| `budget_projection_disabled_dry_run` | partial | diagnostic only; may require a runner mode that computes pre-correction drift and skips enforcement for the dry run |
| `randomized_labels_posthoc` | available | post-hoc classifier control; does not rerun dynamics |
| `topology_disabled` | available by runner selection | enforce by not invoking topology-changing phases and by topology audit |

## Blocked Or Partial Surfaces

| Surface | Status | Reason |
|---|---|---|
| `flux_successor_basin` strong evidence | partial | defer until runner/fixture masks define directed successor path evidence |
| full `GRC9V3.step()` fixed-topology evidence | blocked by default | too broad for first fixed-topology pass |
| accumulated projection counts from core | derived | core returns per-call budget summary; experiment runner counts calls |
| `budget_projection_disabled_dry_run` as positive evidence | blocked | diagnostic only, cannot support positive conservation claims |
| multi-pole Appendix A evidence | deferred | not part of first two-aspect implementation |

## Core-Library Stop Rule

No `src/*` changes are required for Iteration 1.

If later work appears to require a missing core API, pause the experiment and
open a separately approved core-library task. Do not patch `src/*` from this
experiment track.
