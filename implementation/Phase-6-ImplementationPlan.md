# Phase 6 Implementation Plan

This document is the detailed execution plan for **Phase 6: `GRC9`
Mechanical Substrate**.

It turns the Phase 6 summary in
[`ImplementationPhases.md`](./ImplementationPhases.md), the entry handoff in
[`Phase-6-Handoff.md`](./Phase-6-Handoff.md), and the `GRC9` sources in
[`../specs/grc-9-spec.md`](../specs/grc-9-spec.md) and
[`../papers/2026-04-GRC-9.md`](../papers/2026-04-GRC-9.md) into explicit
workstreams for the first nine-slot mechanical family.

Required kickoff companion documents:

- `Phase-6-ImplementationChecklist.md`
- `Phase-6-EquationMap.md`
- `Phase-6-StepLoop.md`

Required mid-phase review artifact:

- `Phase-6-MidGate-Review.md`

## Purpose

Phase 6 exists to implement one authoritative `GRC9` baseline that:

- executes on the existing deterministic nine-slot port substrate,
- treats the 3x3 row/column chart as constitutive rather than decorative,
- computes the row-based coherence tensor directly from port-organized state,
- keeps conductance, potential, flux, sink, and basin logic inside the family
  runtime,
- implements a mechanical spark trigger based on saturation plus local
  instability or column diagnostics,
- refines topology through deterministic column-preserving expansion,
- supports deterministic inactive-port growth,
- exposes invertible column coarse-graining / Split as a first-class family
  capability,
- and remains clearly distinct from the later `GRC9V3` hybrid interpretation.

The purpose is not to build the hybrid family early.
The purpose is not to reinterpret `GRC9` as a weighted graph with extra
metadata.
The purpose is to close the mechanically explicit nine-slot family on top of
the already-finished shared infrastructure.

## Inputs From Earlier Phases

Phase 6 assumes the following outputs already exist and remain authoritative:

- Phase 0 determinism conventions and implementation-boundary decisions
- Phase 1 shared contracts in `src/pygrc/core/`
- Phase 2 port-graph substrate and backend matrix
- Phase 3 canonical serialization, save/load, and digest support
- Phase 4 executable `GRCV2` baseline and retrospective lessons
- Phase 5 / Phase T / Phase V closeout lessons about runtime, artifacts, and
  validation structure
- the current landscape seed layer and projector-boundary documents
- the `GRC9` paper in [`../papers/2026-04-GRC-9.md`](../papers/2026-04-GRC-9.md)
- the executable family contract in
  [`../specs/grc-9-spec.md`](../specs/grc-9-spec.md)

In particular, Phase 6 must reuse:

- `GRCModel`, `GRCParams`, `GRCState`, `StepResult`, and `GRCEvent`
- shared snapshot builders and save/load discipline
- the common backend-selection architecture in `src/pygrc/core/backends.py`
- the first-party `PortGraphBackend`
- the shared telemetry/report/visualization infrastructure
- the existing seed parsing and validation layer

Implementation consequence:

- `src/pygrc/models/grc_9.py` must stop being a Phase 1 `BaseFamilyStub`
  subclass and become the real executable `GRCModel` implementation owned by
  Phase 6

Phase 6 must not silently contradict those documents by collapsing `GRC9` into:

- a weighted graph family,
- a partial `GRC9V3`,
- or a visualization-only interpretation of rows and columns.

## In Scope

- executable `GRC9` model behavior
- `GRC9`-specific state construction on top of `GRCState`
- `GRC9` parameter parsing and validation
- explicit row/column and port-attached runtime semantics
- row-based tensor construction
- port-pair conductance update
- selected analytic edge-label computation
- potential and flux computation on occupied port-pairs
- successor map, sink extraction, and basin extraction
- mechanical spark detection
- deterministic expansion modules and column-preserving rewiring
- deterministic inactive-port growth
- configured boundary handling when implemented
- exact budget preservation
- scalar budget target locking from the initial live state, with lazy target
  inference retained only as a compatibility fallback
- invertible column coarse-graining / Split on supported fields
- deterministic serialization and replay
- observables, telemetry, and artifact-backed validation lanes sufficient for
  Phase 6 closeout

## Out Of Scope

- `GRC9V3` basin attributes
- signed-Hessian semantics as constitutive `GRC9` logic
- hierarchy tracking
- choice / collapse / learning semantics
- quadrature-budget interpretation beyond the baseline invariant
- host embedding frame semantics
- full causal / Lorentzian layer
- explicit multiscale `sigma` state
- PDE / seed-language expansion unless Phase 6 proves the neutral seed boundary
  genuinely insufficient
- performance tuning beyond the deterministic reference path

## Phase 6 Design Constraints

### 1. Mechanical Substrate, Not Hybrid Lift

`GRC9` is the nine-slot mechanical substrate.

Phase 6 must keep explicit:

- exact ordered ports,
- row-organized geometry,
- column-organized interface families,
- occupancy and rewiring as runtime state,
- and topology refinement as mechanical expansion.

It must not silently inherit:

- `GRCV3` basin attributes,
- `GRCV3` signed-Hessian spark semantics,
- hierarchy,
- or choice/collapse semantics.

Those belong to Phase 7 unless a later document explicitly re-scopes them.

### 2. Port Backend Authority Is Necessary But Not Sufficient

The `PortGraphBackend` is already implemented, but Phase 6 is not “mostly done”
just because the substrate exists.

Phase 6 must still define:

- the `GRC9` state model,
- the row-based tensor and metric law,
- the family-local meaning of conductance/flux on occupied port-pairs,
- the mechanical spark rule,
- the expansion operator,
- the growth rule,
- and the coarse-graining semantics.

The backend owns storage.
The family owns mechanics.

### 3. Rows And Columns Must Stay Distinct

The paper is explicit that rows and columns serve different constitutive roles.

Rows are:

- the local directional basis for the tensor,
- the unit of row-wise mismatch accumulation,
- and the minimum anisotropic geometry surface in `GRC9`.

Columns are:

- the stable interface families,
- the deterministic rewiring partition for expansion,
- and the unit of coarse-graining / Split.

Phase 6 should therefore reject shortcuts where:

- row operations implicitly depend on column labels without documentation,
- or coarse-graining mixes rows and columns into one undifferentiated port sum.

### 4. Deterministic Topology Events Must Be Fully Specified

Expansion and growth are the most failure-prone parts of Phase 6.

Before implementation becomes large, Phase 6 must lock:

- sink iteration order,
- spark candidate order,
- expansion size policy,
- canonical expansion wiring,
- column-preserving reassignment order,
- inactive-port selection order,
- and budget-correction timing around topology events.

If a tie-break rule is needed, it should be explicit in code and tests.

### 5. Runtime, Source, And Artifact Lanes Must Stay Separate

The main lesson from later `GRCV3` work applies immediately.

Phase 6 must keep separate:

1. runtime constitutive correctness
2. source/projector correctness
3. artifact/observability correctness

“The model steps” is not enough for closeout.

### 6. Coarse-Graining Must Be Honest About Exactness

The paper gives an exact nonnegative-column coarse-graining and an exact
positive/negative decomposition for signed flux.

Phase 6 should therefore treat:

- exact invertibility for supported fields as a required feature,
- compressed signed-flux reconstruction as optional and explicitly labeled,
- and cache invalidation for coarse states as part of the family contract.

### 7. Reuse Infrastructure Aggressively, Keep Semantics Family-Local

Phase 6 should reuse:

- common backend naming and serialization,
- common snapshot helpers,
- common telemetry/report layout,
- and common landscape/seed parsing.

But the family must still state explicitly:

- what is shared,
- what is renamed,
- and what differs mechanically.

## Phase 6 Backend And Public Configuration Surface

Phase 6 should reuse the common backend-selection vocabulary where it adds real
clarity, but avoid inventing unnecessary categories for already-shared family
mode flags.

Recommended Phase 6 public backend/config surface:

| Category / config surface | Public names for Phase 6 | Baseline default | Notes |
| --- | --- | --- | --- |
| `geometry` / `frame_mode` | `fixed_port_chart` | `fixed_port_chart` | The row/column chart is the constitutive local frame. |
| `metric` | `tensor_exponential` | `tensor_exponential` | Owns `K_i -> w_e` on occupied port-pairs. |
| `curvature` | `none`, `forman`, `ollivier` | `none` | Matches the `GRC9` spec vocabulary. |
| `spark` | `mechanical_saturation`, `mechanical_saturation_with_column_proxy`, `mechanical_saturation_with_instability_or_column_proxy` | `mechanical_saturation_with_instability_or_column_proxy` | The last one is the intended paper-facing baseline. |
| `birth` | `outward_flux_parent_selection` | `outward_flux_parent_selection` | Owns parent-selection policy only; chosen-port selection remains a separate deterministic lowest-index rule. |
| `coarse_graining` | `exact_column_profile`, `signed_flux_split` | `exact_column_profile` | `signed_flux_split` denotes exact `J+` / `J-` support for signed flux. |
| `boundary_mode` | `prune`, `barrier`, `ghost` | `prune` or omitted | Keep as a family config surface, but Phase 6 only executes `prune`; `barrier` / `ghost` remain reserved names until explicit boundary behavior and `boundary_barrier` capability support are implemented. |
| `expansion_distribution_mode` | `equal`, `custom` | `equal` | Keep as a family config surface. |
| `edge_label_selection` | `all`, subset modes if later added | `all` | Keep as a family config surface. |

Important boundary:

- `frame_mode`
- `boundary_mode`
- `expansion_distribution_mode`
- `edge_label_selection`

should remain explicit serialized family configuration surfaces even when their
values align with the common backend vocabulary.

Phase 6 should not create new backend categories just to rename one enum.

## Recommended Initial Package Shape

Phase 6 should stay explicit about file ownership before implementation begins.

Recommended target files:

```text
src/pygrc/models/
  grc_9.py                    # public model class and step orchestration
  grc_9_ports.py              # pure port <-> row/column helpers and membership helpers
  grc_9_state.py              # PortEdge and GRC9State
  grc_9_runtime.py            # tensor, metric, potential, flux, basin helpers
  grc_9_expansion.py          # spark expansion and growth helpers
  grc_9_coarse.py             # coarse-graining / Split helpers

tests/models/
  test_grc_9_state.py
  test_grc_9_tensor.py
  test_grc_9_runtime.py
  test_grc_9_expansion.py
  test_grc_9_coarse.py
  test_grc_9_serialization.py
  test_grc_9_step.py
```

This split is recommended, not mandatory.
The important requirement is that:

- state definition,
- runtime equations,
- topology mutation logic,
- and coarse-graining logic

do not collapse into one giant module.

## Workstreams

## Workstream 1. `GRC9` State And Parameter Surface

### Goal

Create the public state and parameter surface required by the `GRC9` spec.

### Scope

- `PortEdge`
- `GRC9State`
- node coherence storage
- occupied port-pair conductance and flux storage
- typed expansion in-progress state
- previous-step column-diagnostic state when the sign-crossing extension is
  enabled
- potential, sink, basin, expansion, and coarse-cache state
- `frame_mode`, `curvature_backend`, `boundary_mode`,
  `expansion_distribution_mode`, and `edge_label_selection`
- capability surface for `GRC9`

### Acceptance Criteria

- state fields match the `GRC9` spec directly
- no mechanical family state is hidden in unstructured dict payloads
- params resolve to explicit family modes and explicit backend selections
- capability claims match the actual implementation and do not smuggle in
  `GRC9V3`
- the plan defines the typed runtime shape for:
  - `expansion_registry`
  - previous-step column diagnostics
  - and any adiabatic expansion schedule state

## Workstream 2. Row/Column Runtime Semantics And Tensor Construction

### Goal

Turn the paper’s 3x3 chart into executable family-local geometry.

### Scope

- explicit helpers for `port <-> (row, column)`
- row membership helpers over occupied ports
- row-organized neighborhood aggregation
- row-based tensor construction from:
  - density term
  - row-wise mismatch term
  - flux feedback term
- a compact tensor representation for the row-diagonal payload:
  - `dict[ModeRow, float]`
  - or one ordered length-3 sequence
- public conventions for port-attached versus edge-attached views

### Acceptance Criteria

- rows and columns have distinct runtime meaning
- row-wise mismatch accumulation is deterministic and test-backed
- tensor construction is inspectable from public state or deterministic helper
  outputs
- the implementation does not materialize `K_i` as an unnecessary dense 3x3
  matrix when the runtime object is diagonal in the row basis
- no weighted-graph-only shortcut erases the port chart

## Workstream 3. Metric, Labels, Potential, Flux, And Basin Extraction

### Goal

Close the reflexive loop for the nine-slot substrate before topology events are
added.

### Scope

- conductance update on occupied port-pairs
- analytic edge labels:
  - geometric length
  - temporal delay
  - flux coupling
- potential computation
- flux computation
- successor map extraction
- sink-set extraction
- basin extraction

### Acceptance Criteria

- conductance remains the only dynamical weight used by the update equations
- analytic labels are explicit and separately serialized
- flux conventions are deterministic and antisymmetric where required
- one canonical storage direction for `PortEdge(node_u, port_u, node_v, port_v)`
  is fixed once, with the baseline convention:
  - `node_u < node_v`
  - or, for an internal restored-edge comparison path, canonical endpoint tuple
    ordering by `((node, port), (node, port))`
- runtime checks enforce the antisymmetry contract for oriented flux views
- sink/basin extraction works without any `GRCV3` semantic layer
- successor-map ties are broken deterministically by ascending neighbor node ID

## Workstream 4. Mechanical Spark Trigger

### Goal

Implement the baseline `GRC9` spark rule without hybrid reinterpretation.

### Scope

- active-degree saturation rule
- local instability proxy integration
- column diagnostic `H^(b)` support
- explicit spark-kind classification
- deterministic trigger ordering across sinks
- previous-step column-diagnostic persistence for replay/debugging, with
  sign-crossing consumption gated separately

Baseline instability proxy for Phase 6:

- for one candidate sink `s`, define the local patch `U(s) = {s} ∪ N(s)`
- let `cut_out(U)` be the sum of conductances on occupied port-pairs with
  exactly one endpoint in `U`
- let `support_in(U)` be the sum of conductances on occupied port-pairs with
  both endpoints in `U`
- define
  `Instability(s) = cut_out(U) / max(cut_out(U) + support_in(U), eps)`
- register the instability branch of the spark trigger when
  `Instability(s) >= tau_instability`

Recommended `SparkKind` vocabulary:

- `saturation_instability`
- `saturation_column_proxy`
- `saturation_sign_crossing`

Baseline priority order for one eligible saturated sink:

- `saturation_instability`
- then `saturation_column_proxy`
- then `saturation_sign_crossing`

This precedence is intentional. Phase 6 should emit one deterministic spark
classification per sink candidate rather than treating the branches as
independent simultaneous events.

### Acceptance Criteria

- the baseline trigger requires saturation plus instability or column proxy
- the implementation does not silently replace this with Hessian-based
  `GRC9V3` semantics
- column diagnostics are inspectable in tests and artifacts
- spark classification is deterministic under tied candidates
- `prev_column_diagnostic` is an explicit state field and should be refreshed on
  every spark-detection pass for telemetry/debugging, even when sign-crossing
  support is disabled
- sign-crossing support, if enabled, consumes that persisted previous-step state
  rather than introducing a second special-case cache

## Workstream 5. Expansion, Rewiring, Growth, And Boundary Handling

### Goal

Implement the family’s mechanical topology events.

### Scope

- target effective degree policy
- expansion-size calculation
- canonical expansion module:
  - core node
  - three primary satellites
  - internal wiring convention
- explicit multi-sink spark policy
- column-preserving boundary reassignment
- state transfer and bond initialization
- immediate budget closure after expansion
- optional adiabatic expansion schedule
- growth parent-selection policy
- inactive-port growth using lowest-index port selection
- configured boundary handling if implemented

Baseline decisions for this phase:

- spark expansion should be **sequential**, not batch-applied:
  - expand the first deterministic candidate
  - recompute sink/candidate structure
  - then continue
- expansion size uses
  `n = max(1, ceil((D_eff - 2) / 7))`
- if a satellite receives no inherited boundary edges:
  - it still exists in the canonical module
  - its coherence share is still assigned by the chosen distribution rule
  - and if bond initialization uses a local aggregate that is undefined for an
    empty column, the implementation falls back to the fixed `w_bond` rule
- parent selection for growth and chosen-port selection must remain distinct:
  - parent selection may depend on outward flux or another explicit birth rule
  - chosen-port selection is deterministic and always uses the lowest-index
    inactive port on that parent
- immediate post-expansion budget handling should distinguish:
  - verification that budget was preserved by construction
  - correction only if numerical or implementation drift is detected
- `budget_target` should be fixed during construction or `from_state(...)`
  normalization when omitted. The existing lazy `_ensure_budget_target()`
  behavior is acceptable for ordinary runtime results because it runs before
  budget-sensitive topology events, but it is weaker invariant discipline and
  should become a compatibility fallback rather than the primary path.

### Acceptance Criteria

- expansion is mechanical, deterministic, and column-preserving
- old boundary edges are reassigned by column family rather than ad hoc choice
- new capacity remains explicit as inactive ports
- growth uses lowest-index inactive ports first
- budget preservation survives every topology event path
- the budget target is not silently reinterpreted after coherence or topology
  mutation
- multi-sink spark handling is fixed once and tested

## Workstream 6. Column Coarse-Graining And Split

### Goal

Implement the family’s lossless local multiscale interface.

### Scope

- nonnegative field coarse-graining
- intra-column mode-profile construction
- exact Split reconstruction
- exact signed-flux support through positive/negative decomposition
- optional compressed signed-flux diagnostic mode
- coarse-cache invalidation policy after value or topology changes

Minimum invalidation triggers that must be named explicitly:

- any conductance recomputation
- any flux recomputation
- any expansion rewiring
- any growth event
- and any other topology mutation that changes occupied port structure

### Acceptance Criteria

- supported nonnegative fields satisfy `Split(G(X)) == X`
- signed flux has one exact supported representation
- compressed signed-flux mode is explicitly labeled as non-exact if added
- cached coarse states are invalidated deterministically after the named value
  and topology triggers

## Workstream 7. Serialization, Replay, And Family Tests

### Goal

Make `GRC9` reproducible before heavier experiments start.

### Scope

- `GRC9` snapshot schema
- port occupancy and port-edge structure serialization
- selected edge-label family serialization
- edge-label computation mode metadata
- expansion in-progress state serialization
- optional coarse-cache metadata serialization
- save/load roundtrip tests
- deterministic step and digest tests

### Acceptance Criteria

- same state + same params + same RNG state => same snapshot digest
- save/load preserves port occupancy and occupied port-pair state
- expansion state can be restored without semantic loss
- tests cover both direct family mechanics and contract-level replay behavior

## Workstream 8. Observables, Telemetry, And Artifact Lanes

### Goal

Make Phase 6 observable in the same honest way later `GRCV3` work became
observable.

### Scope

- required observables:
  - `abundance`
  - `budget_current`
  - `budget_error`
  - `num_nodes`
  - `num_port_edges`
  - `spark_count`
  - `active_degree_histogram`
- recommended observables:
  - column profile sparsity
  - expansion count
  - sink-module sizes
- family-local telemetry extension surface if needed
- checkpoint/report artifacts sufficient for graph-visible review

Recommended baseline observable encodings:

- `budget_error = abs(budget_current - budget_target)`
- `active_degree_histogram: dict[int, int]` over degrees `0..9`

### Acceptance Criteria

- Phase 6 artifacts expose the event sequence rather than only final state
- expansion and growth are visible in saved outputs
- observables distinguish runtime health from topology evolution
- Phase 6 can support at least one representative artifact-backed lane without
  inventing a new ad hoc telemetry architecture

## Workstream 9. Validation Ladder And Constitutive Review

### Goal

Close the family through explicit evidence rather than tests alone.

### Scope

- pure-runtime control probes
- representative artifact-backed lane
- real-seed / real-experiment lane
- later dense rich-source lane if family-local source semantics are introduced
- constitutive review against the paper and spec before closeout

### Acceptance Criteria

- each validation lane answers a distinct question and is named explicitly
- at least one saved lane makes spark, expansion, and post-event geometry
  visually legible
- unresolved constitutive compromises are documented explicitly
- no major `GRC9` claim depends only on unit tests

## Minimum `GRC9State` Surface

At minimum, `GRC9State` should carry:

- `step_index`
- `time`
- `budget_target`
- `remainder`
- `params_identity`
- `node_coherence`
- `port_edges`
- `geometric_length`
- `temporal_delay`
- `flux_coupling`
- `potential`
- `sink_set`
- `basins`
- `expansion_registry`

Budget-target note, May 2026: later Phase 7 basin-mass review prompted a
matching audit of pure GRC9. Pure GRC9 does not carry GRC9V3 `M_i` basin-mass
semantics, so it does not need the Phase 7 basin-mass repair. It does carry the
paper's scalar invariant `B = sum_i C_i`. Normal GRC9 runs appear numerically
correct because `_ensure_budget_target()` is called before budget-sensitive
expansion/growth/enforcement paths, but the target should still be locked at
state construction for stronger correctness discipline and clearer replay
semantics.
- `coarse_cache`
- `rng_state`

Minimum typed registry expectations:

- `expansion_registry` should map one stable expansion identifier to structured
  expansion state including:
  - `parent_sink_id`
  - `module_node_ids`
  - `expansion_step`
  - `distribution_weights`
  - and any in-progress schedule metadata required for replay

Implementation planning should additionally decide explicitly where to store:

- conductance on occupied port-pairs
- flux on occupied port-pairs
- row-diagonal tensor values if cached
- column diagnostic values if cached between steps
- previous-step column diagnostics for sign-crossing support
- and any expansion-schedule in-progress state

These should become part of the typed state surface rather than hidden scratch
data.

## Suggested Internal Hook Surface

Phase 6 should preserve the control-flow separation established by `GRCV2` and
adapt it to the nine-slot substrate.

Recommended internal hooks:

```python
def _compute_geometry(self) -> None
def _compute_column_diagnostic(self) -> None
def _compute_metric(self) -> None
def _compute_potential(self) -> None
def _compute_flux(self) -> None
def _detect_identities(self) -> None
def _detect_events(self) -> list[GRCEvent]
def _apply_topology_changes(self, events: list[GRCEvent]) -> None
def _apply_growth(self) -> None
def _apply_continuity(self) -> None
def _enforce_budget(self) -> None
def _refresh_coarse_cache(self) -> None
```

Exact helper names may vary, but this level of separation should remain
visible.

## Spec-Locked Step Order

Phase 6 should treat the `GRC9` step order as normative rather than
approximate.

The executable `GRC9.step()` should follow this ordered baseline:

1. compute row-based node tensor
2. update edge conductance
3. compute selected analytic edge labels
4. compute potential
5. compute flux
6. compute successor map, sink set, and basins
7. detect sparks using the mechanical trigger
8. expand modules where triggered
9. apply growth on lowest-index inactive ports
10. apply configured boundary behavior if implemented
11. apply continuity update
12. enforce exact budget preservation
13. refresh or invalidate coarse-state cache
14. compute observables

Tests and helper decomposition should reference this order explicitly.

This order intentionally matches the `GRC9` spec.
The paper’s compact algorithmic statement does not break out a separate
boundary-management step, so the spec-level discrete ordering is authoritative
for the implementation.

## Early Validation Ladder

Before Phase 6 becomes large, the plan should branch validation into explicit
lanes:

1. pure-runtime control probes
2. representative artifact-backed lane
3. real-seed / real-experiment lane
4. rich-source dense artifact lane if family-local source semantics are opened

These lanes answer different questions:

- control probes validate constitutive mechanics in isolation
- representative artifact lanes validate observability and event legibility
- real-seed lanes validate the family against nontrivial source inputs
- rich-source dense lanes justify stronger closeout claims once a family-local
  source surface exists

## Mid-Phase Validation Gate

Before expansion/growth machinery becomes difficult to revise, Phase 6 should
pause for an explicit constitutive review recorded in
`Phase-6-MidGate-Review.md`.

That review should answer:

- whether row and column semantics remain cleanly separated in code
- whether the tensor implementation still matches the paper intent
- whether the spark rule is still purely `GRC9` and not a hidden `GRC9V3`
  lift
- whether expansion wiring and reassignment are truly deterministic
- whether coarse-graining exactness claims are actually true for supported
  fields
- whether the observability surface is strong enough to support honest saved
  evidence

This gate should happen before later source/projector questions start to blur
the runtime baseline.

## Kickoff Rule

Before substantive Phase 6 runtime implementation begins, the repo should
contain:

1. `Phase-6-ImplementationPlan.md`
2. `Phase-6-ImplementationChecklist.md`
3. `Phase-6-EquationMap.md`
4. `Phase-6-StepLoop.md`

This is required to keep the paper-to-code traceability explicit before the
mechanical runtime grows large.

## Exit Criteria

Phase 6 should be considered complete only if:

- `GRC9` runs end to end without any `GRCV3` semantic dependency
- rows and columns remain constitutive and inspectable in runtime state
- the baseline mechanical spark rule is deterministic and test-backed
- expansion and rewiring are deterministic and column-preserving
- inactive-port growth follows an explicit deterministic rule
- supported coarse-grain / Split operations are invertible
- save/load preserves the nine-slot runtime state without semantic loss
- artifact-backed validation exists beyond tests alone
- the phase closes with explicit documentation of what remains deferred to
  `GRC9V3`

At that point `GRC9` can become the authoritative mechanical substrate for
later `GRC9V3` hybrid work rather than a speculative family stub.
