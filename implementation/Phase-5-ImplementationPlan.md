# Phase 5 Implementation Plan

This document is the detailed execution plan for **Phase 5: `GRCV3` Semantic
Lift**.

It turns the Phase 5 summary in
[`ImplementationPhases.md`](./ImplementationPhases.md) and the handoff in
[`Phase-5-Handoff.md`](./Phase-5-Handoff.md) into explicit workstreams for the
first basin-attribute family.

Companion documents:

- [`Phase-5-ImplementationChecklist.md`](./Phase-5-ImplementationChecklist.md)
- [`Phase-5-EquationMap.md`](./Phase-5-EquationMap.md)
- [`GRCV3-Landscape-ProjectorProposal.md`](./GRCV3-Landscape-ProjectorProposal.md)
- [`Phase-5-LandscapeProjectorChecklist.md`](./Phase-5-LandscapeProjectorChecklist.md)

## Purpose

Phase 5 exists to lift the executable `GRCV2` baseline into a semantic-rich
graph family that:

- stores basin attributes explicitly on nodes,
- supports direct differential summaries instead of only inferred topology,
- separates base conductance from analytic edge labels,
- tracks hierarchy,
- supports signed-Hessian spark semantics,
- and introduces optional choice / collapse / learning event logic without
  breaking the baseline reflexive loop.

The purpose is not to create an all-purpose graph semantics engine. The purpose
is to implement one authoritative `GRCV3` baseline that is:

- paper-facing,
- deterministic,
- serializable,
- testable,
- and extensible through explicit backend-selection categories rather than
  hidden internal branches.

## Inputs From Earlier Phases

Phase 5 assumes the following outputs already exist and remain authoritative:

- Phase 0 determinism and implementation-boundary decisions
- Phase 1 shared contracts in `src/pygrc/core/`
- Phase 2 weighted graph substrate
- Phase 3 serialization, digest, and replay path
- Phase 4 executable `GRCV2` baseline and its validation artifacts
- Phase L / L1 landscape bridge and seed-driven realization discipline
- Phase T telemetry/report artifact layer
- Phase V artifact-driven visualization layer

Phase 5 must explicitly reuse:

- `GRCModel`, `GRCParams`, `GRCState`, `StepResult`, and `GRCEvent`
- shared snapshot builders and save/load discipline
- the first-party weighted graph substrate
- the common backend-selection architecture from
  [`Common-BackendStrategyPlan.md`](./Common-BackendStrategyPlan.md)
- the `GRCV2` closeout and retrospective lessons

## In Scope

- `GRCV3` state design and public model surface
- `BasinAttributes` and `GRCV3State`
- `GRCV3` parameter validation and backend selection surface
- explicit geometry / frame interpretation for basin-attribute nodes
- differential-summary construction:
  - gradient
  - Hessian
  - net flux summary
  - effective basin mass
- base conductance and analytic edge-label computation
- signed-Hessian semantics
- direct spark detection plus attractor-count confirmation
- hierarchy tracking and parent/child basin updates
- optional choice / collapse / learning event layer
- deterministic serialization, replay, and snapshot compatibility
- theory-facing tests and a mid-phase constitutive validation gate

## Out Of Scope

- `GRC9` mechanical substrate logic
- `GRC9V3` hybrid semantics
- causal / Lorentzian discrete layer
- multiscale `sigma` / FRC state
- embedding and integration adapters beyond the `frame_mode` contract
- machine-driver semantics beyond what Phase 10 will own
- performance tuning beyond the deterministic reference implementation
- PDE-bridge rework unless a genuine contradiction is found

## Post-Closeout Follow-On: Seed-Driven `GRCV3` Projector Revision

Phase 5 baseline runtime closeout remains valid, but later seed-driven
`GRCV3` comparison work exposed one explicit family-local gap:

- the current `GRCL -> GRCV3` projector is too coarse for the `GRCV3`
  differential and spark stack on `cell-4`

That follow-on is now tracked explicitly through:

- [`GRCV3-Landscape-ProjectorProposal.md`](./GRCV3-Landscape-ProjectorProposal.md)
- [`Phase-5-LandscapeProjectorChecklist.md`](./Phase-5-LandscapeProjectorChecklist.md)

Boundary for that follow-on:

- keep `GRCV3` runtime equations fixed first
- keep shared `GRCL` seeds fixed first
- push the first correction into the family-local projector in
  `src/pygrc/models/grc_v3_landscape.py`
- only reconsider source-language expansion or runtime-equation changes if the
  richer projector still fails

This follow-on should be read as a Phase 5 extension, not as a silent Phase 6
carry-over.

## Phase 5 Design Constraints

### 1. Semantic Lift, Not Baseline Reinvention

`GRCV3` is allowed to add semantics. It is not allowed to silently redefine
shared semantics that already close in `GRCV2`.

Shared meanings that must remain explicit:

- snapshot identity and deterministic replay
- shared observable names that still apply
- graph identity and ordering rules
- budget closure discipline
- backend identity and parameter hashing

### 2. Backend Architecture Before Backend Proliferation

Phase 5 must establish the backend-selection vocabulary and serialization
surface before multiple `GRCV3` formulas start to accumulate in code.

This is a hard requirement because Phase 4 already demonstrated how quickly one
family can become branch-heavy when constitutive choices remain implicit.

### 3. Theory-Facing Checks Early

Tests must not wait until the implementation is almost complete.

Phase 5 needs direct checks early for:

- gradient construction
- Hessian construction
- Hessian sign handling
- basin-attribute materialization
- spark registration semantics
- hierarchy updates
- choice / collapse event meaning

### 4. Family-Local Math, Common-Layer Naming

The common layer should own:

- backend category names
- backend selection representation
- backend serialization shape
- backend identity participation in replay

The family layer should own:

- actual differential formulas
- actual metric law
- actual spark semantics
- actual hierarchy update behavior
- actual choice / collapse scoring logic

### 5. Weighted Graph Authority Remains

Baseline `GRCV3` must still execute on the authoritative weighted graph
substrate.

`GRCV3` should not smuggle in a second topology representation just because node
state is richer.

### 6. Optional Semantics Must Stay Optional

Choice / collapse / learning support is required at the event-contract level,
but the initial baseline may still use a disabled backend or a minimal viable
backend for that category.

Optional semantics must be:

- explicitly selected,
- explicitly serialized,
- explicitly tested,
- and explicitly named in artifacts.

## Phase 5 Backend Categories And Public Names

Phase 5 should lock the following category vocabulary for `GRCV3`.

These names are the public implementation vocabulary and should appear in
params, serialization, tests, and validation docs.

| Category | Public names for Phase 5 | Baseline default | Notes |
| --- | --- | --- | --- |
| `geometry` | `host_embedding`, `induced_local_frame`, `combinatorial` | `induced_local_frame` | Aligns with `frame_mode` values from the spec. |
| `differential_summary` | `weighted_least_squares`, `combinatorial_surrogate` | `weighted_least_squares` | Owns gradient/Hessian summary formulas. |
| `metric` | `tensor_exponential` | `tensor_exponential` | Owns `K_i -> w_ij` and the three analytic edge labels. |
| `curvature` | `none`, `forman`, `ollivier` | `none` | Reuses common-family naming from earlier phases. |
| `spark` | `signed_hessian_degeneracy`, `signed_hessian_plus_attractor_delta` | `signed_hessian_plus_attractor_delta` | The second is the intended paper-facing baseline. |
| `hierarchy_update` | `basin_parent_child` | `basin_parent_child` | Owns parent/depth/basin-tree maintenance. |
| `choice` | `disabled`, `sink_compatibility` | `disabled` | `sink_compatibility` is the first real event-level backend. |

Important boundary:

- `boundary_mode`
- `split_distribution_mode`
- `edge_label_selection`

remain family config surfaces, not new Phase 5 backend categories.

They are already shared parameter surfaces and should not be duplicated into the
backend registry unless a future phase proves that is necessary.

## Recommended Initial Package Shape

Phase 5 should stay explicit about file ownership before implementation begins.

Recommended target files:

```text
src/pygrc/core/
  backends.py                # common backend-selection datatypes/helpers

src/pygrc/models/
  grc_v3.py                  # public model class and step orchestration
  grc_v3_state.py            # BasinAttributes and GRCV3State
  grc_v3_backends.py         # backend registries / dispatch tables
  grc_v3_differential.py     # gradient / Hessian / local frame helpers
  grc_v3_hierarchy.py        # basin-tree maintenance
  grc_v3_choice.py           # choice / collapse helpers

tests/models/
  test_grc_v3_state.py
  test_grc_v3_backends.py
  test_grc_v3_differential.py
  test_grc_v3_hierarchy.py
  test_grc_v3_choice.py
  test_grc_v3_step.py
  test_grc_v3_serialization.py
```

This file split is recommended, not mandatory. The important requirement is
that backend variation, state definition, and step orchestration do not collapse
into one giant module.

## Workstreams

## Workstream 1. Common Backend-Selection Scaffolding

### Goal

Make backend choices first-class before `GRCV3` math is added.

### Scope

- create or extend common backend-selection datatypes
- define category vocabulary and validation rules
- define resolved backend-selection participation in param identity / replay
- define backend serialization placement

### Acceptance Criteria

- `GRCV3` can advertise backend selections without ad hoc string handling
- unknown backend categories or names fail early
- backend params participate in deterministic identity
- snapshots can reconstruct selected backends unambiguously

## Workstream 2. `GRCV3` State And Parameter Surface

### Goal

Create the public state and parameter surface required by the spec.

### Scope

- `BasinAttributes`
- `GRCV3State`
- `frame_mode` / backend selection resolution
- required thresholds and edge-label parameters
- public capability surface

### Acceptance Criteria

- state fields match the `GRCV3` spec
- params resolve into explicit backend selections and explicit family modes
- capabilities reflect the actual configured implementation
- no `GRCV3` semantic state is hidden in unstructured dict payloads

## Workstream 3. Geometry And Differential Summary Backends

### Goal

Implement the first real `GRCV3` mathematical lift over `GRCV2`.

### Scope

- local frame construction
- gradient summary
- Hessian summary
- signed Hessian convention
- net flux summary
- basin mass summary

### Acceptance Criteria

- the chosen baseline backends produce deterministic gradient/Hessian output
- signed Hessian convention is fixed once and serialized
- differential summaries are queryable from public state
- direct unit tests exist for core formulas and sign behavior

## Workstream 4. Metric, Labels, Potential, And Flux

### Goal

Map basin attributes back into the reflexive loop.

### Scope

- node tensor construction
- base conductance update
- geometric length
- temporal delay
- flux coupling
- potential and flux update on the weighted graph

### Acceptance Criteria

- `base_conductance` remains the only dynamic edge weight
- analytic edge labels are explicit and separately serialized
- edge-label computation mode metadata is preserved
- flux remains antisymmetric and compatible with budget closure

## Workstream 5. Identity Layers And Hierarchy

### Goal

Implement the two-layer identity story required by `GRCV3`.

### Scope

- sink-set extraction
- attraction basins
- geometric basin validation from gradient / Hessian summaries
- basin id / parent / depth updates
- hierarchy structure and serialization

### Acceptance Criteria

- both identity layers are visible in state or events
- hierarchy updates are deterministic
- child basins inherit parent information explicitly
- hierarchy structure survives save/load roundtrip

## Workstream 6. Sparks, Splits, And Optional Choice / Collapse

### Goal

Implement the direct `GRCV3` event semantics.

### Scope

- spark candidate detection from signed Hessian degeneracy
- completed spark confirmation through attractor-count change
- split integration with child-basin initialization
- optional choice / collapse backend
- optional learning-style persistent post-collapse deformation bookkeeping

### Acceptance Criteria

- transient flattening is not misclassified as a completed spark
- child-basin creation is deterministic and serializable
- `choice_detected` / `collapse` events have explicit semantics
- disabled choice backend leaves no ambiguous partial state behind

## Workstream 7. Serialization, Replay, And Family Tests

### Goal

Make the richer family reproducible before larger experiments begin.

### Scope

- `GRCV3` snapshot schema
- backend-selection serialization
- signed-Hessian serialization
- event log reproducibility
- theory-facing tests and save/load tests

### Acceptance Criteria

- same state + same params + same RNG state => same snapshot digest
- backend selections are round-trippable
- `GRCV3` state can be restored without semantic loss
- tests cover both implementation behavior and direct theory contracts

## Workstream 8. Constitutive Validation Gate

### Goal

Review the family against the paper before the phase is considered done.

### Scope

- theory-facing review of gradient / Hessian / sign handling
- review of spark completion logic
- review of hierarchy semantics
- review of choice / collapse semantics if enabled
- review of backend naming against common-layer conventions

### Acceptance Criteria

- no known mismatch remains hidden behind passing tests
- unresolved constitutive compromises are documented explicitly
- baseline and optional backends are clearly distinguished
- the phase can be closed without leaving `GRCV3` semantically provisional

## Minimum Shared State Surface

At minimum, `GRCV3State` should carry:

- `step_index`
- `time`
- `budget_target`
- `remainder`
- `params`
- `nodes`
- `base_conductance`
- `geometric_length`
- `temporal_delay`
- `flux_coupling`
- `flux`
- `potential`
- `sink_set`
- `basins`
- `hierarchy`
- `choice_registry`
- `collapse_registry`
- `rng_state`

Node payloads should materialize:

- coherence
- gradient
- Hessian
- net flux summary
- basin mass
- basin id
- parent id
- depth

## Suggested Internal Hook Surface

Phase 5 should preserve the control-flow separation established by `GRCV2` and
extend it only where `GRCV3` semantics require more structure.

Recommended internal hooks:

```python
def _compute_geometry(self) -> None
def _compute_differential_summary(self) -> None
def _compute_metric(self) -> None
def _compute_potential(self) -> None
def _compute_flux(self) -> None
def _detect_identities(self) -> None
def _detect_events(self) -> list[GRCEvent]
def _apply_topology_changes(self, events: list[GRCEvent]) -> None
def _update_choice_state(self) -> list[GRCEvent]
def _apply_continuity(self) -> None
def _enforce_budget(self) -> None
```

Exact helper names may vary, but this level of separation should remain visible.

## Mid-Phase Validation Gate

Before the implementation becomes large, the phase should pause for an explicit
constitutive review.

That review should answer:

- whether the baseline gradient/Hessian formulas still match the paper intent
- whether `s_H` is fixed and serialized correctly
- whether spark completion requires attractor-count change in the implemented path
- whether hierarchy updates mean what the paper says they mean
- whether any backend names currently imply more mathematical richness than the
  implementation actually delivers

This gate should happen before optional backends or optimizations expand the
surface further.

## Exit Criteria

Phase 5 should be considered complete only if:

- `GRCV3` exposes basin attributes directly in public state
- backend categories and public names are explicit and serialized
- signed-Hessian semantics are deterministic and reproducible
- both identity layers are implemented and inspectable
- spark completion uses more than transient degeneracy alone
- hierarchy survives runtime, save/load, and replay
- optional choice / collapse semantics are either implemented cleanly or
  explicitly disabled
- theory-facing validation was completed before closeout

At that point `GRCV3` can become the semantic reference family for later `GRC9`
and `GRC9V3` work.
