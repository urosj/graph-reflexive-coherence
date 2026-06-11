# Phase 4 Implementation Plan

This document is the detailed execution plan for **Phase 4: `GRCV2` Baseline**.

It turns the Phase 4 summary in `ImplementationPhases.md` into concrete workstreams for
the first full executable model family.

Companion note: [`Phase-4-DiscretizationDefense.md`](./Phase-4-DiscretizationDefense.md)

Retrospective note: [`Phase-4-Retrospective.md`](./Phase-4-Retrospective.md)

Phase 4 exists to turn the shared contracts, substrates, and persistence path from
Phases 0 through 3 into one end-to-end deterministic graph simulation that actually
steps state forward.

## Purpose

Phase 4 must establish:

- the first executable `GRCModel` implementation in the repo,
- a deterministic `GRCV2` state shape on top of the weighted graph substrate,
- the baseline v2 conductance / potential / flux loop,
- sink-set and basin extraction,
- proxy spark detection,
- soft split and front birth,
- configured boundary handling,
- exact budget preservation with bounded remainder accounting,
- and observable/snapshot output stable enough for later semantic lift in `GRCV3`.

`GRCV2` is intentionally the simplest full model family. It is the place where the
graph loop, budget logic, topology events, and determinism have to work cleanly before
the richer `GRCV3` and `GRC9` families are attempted.

## Inputs From Earlier Phases

Phase 4 assumes the following outputs already exist and remain authoritative:

- Phase 0 determinism conventions in [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
- Phase 0 implementation boundaries in [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md)
- Phase 1 shared contracts in `src/pygrc/core/`
- Phase 2 weighted graph substrate in `src/pygrc/core/storage.py`
- Phase 3 canonical serialization, save/load, and digest support
- the `GRCV2` implementation contract in [`../specs/grc-v2-spec.md`](../specs/grc-v2-spec.md)

In particular, Phase 4 builds on:

- `GRCParams`, `GRCState`, `StepResult`, and `GRCEvent`
- `WeightedGraphBackend`
- the shared snapshot builders and save/load path:
  - `build_snapshot_metadata(...)`
  - `build_standard_snapshot(...)`
  - `save_snapshot(...)`
  - `load_snapshot(...)`
  - `restore_weighted_graph(...)`
- the capability profile for `GRCV2`
- the already-existing `src/pygrc/core/observables.py` shared observable surface

Phase 4 must not silently reinterpret those boundaries or backfill missing contract
decisions by hiding them in ad hoc model code.

## In Scope

- executable `GRCV2` model class behavior
- `GRCV2`-specific state construction on top of `GRCState`
- parameter parsing/validation for the v2 family
- node tensor and scalar conductance computation
- selected analytic edge-label computation
- potential and flux computation
- sink-set and basin extraction
- spark proxy detection backends
- soft split initialization/progression
- front birth
- configured boundary handling (`prune`, `barrier`, `ghost`)
- exact budget enforcement
- core observables for `GRCV2`
- deterministic tests for the full step loop

## Out Of Scope

- `GRCV3` gradient/Hessian summaries and basin attributes
- `GRC9` port-mechanical substrate logic
- Lorentzian/causal-layer behavior
- multiscale `sigma` / FRC semantics
- machine-driver replay/diff workflows
- embedding/integration-layer adapters
- performance optimization beyond the deterministic reference path

## Phase 4 Design Constraints

### 1. First Executable Family, Not First Optimized Family

Phase 4 must prioritize correctness, determinism, and spec alignment over numerical
performance tuning.

The reference `GRCV2` path should be easy to inspect and test. If a later phase wants
faster kernels, it must preserve the Phase 4 semantics rather than redefining them.

### 2. Weighted-Graph Authority

`GRCV2` must use the authoritative in-house weighted backend from Phase 2.

Phase 4 must not:

- bypass the weighted backend with raw dict-only topology storage,
- depend on adapter-layer graph types,
- or treat graph identity/order as incidental.

### 3. Deterministic Event Ordering

All topology and state events in the step loop must be deterministic:

- sink ordering,
- spark ordering,
- split/birth application order,
- node/edge insertion order,
- and snapshot/observable emission order.

If a tie-break rule is needed, it should be explicit and documented in code or tests.

### 4. Budget Preservation Is A Core Semantic

Budget preservation is not a post-processing convenience. It is part of the model
contract.

Phase 4 must make it explicit:

- how abundance/budget is measured,
- where continuity update happens,
- where split/birth/prune mass transfers happen,
- and how the final budget correction / remainder accounting is applied.

### 5. Baseline Means Minimal, Not Ambiguous

`GRCV2` is the minimal full graph realization, but “minimal” must not mean
under-specified.

Phase 4 must lock in:

- the actual step order,
- default spark backend behavior,
- equal split distribution as the baseline,
- and the practical baseline for selected edge labels and observables.

### 6. Shared Hook Surface Before Equation Complexity

The common contract already recommends a stable internal decomposition of the step loop.

Phase 4 should use or closely mirror the following internal hook names so that later
families can lift the same structure rather than inventing a new control flow:

```python
def _compute_geometry(self) -> None
def _compute_metric(self) -> None
def _compute_potential(self) -> None
def _compute_flux(self) -> None
def _detect_identities(self) -> None
def _detect_events(self) -> list[GRCEvent]
def _apply_topology_changes(self, events: list[GRCEvent]) -> None
def _apply_continuity(self) -> None
def _enforce_budget(self) -> None
```

The exact helper split may differ, but the implementation should preserve this level of
separation between geometry, flux, identity/event detection, topology mutation, and
budget closure.

## Existing Infrastructure To Reuse

Phase 4 should extend the existing codebase rather than reintroducing parallel layers.

Already in place:

- `src/pygrc/core/observables.py`
- `src/pygrc/core/serialization.py`
- `src/pygrc/core/digests.py`
- `src/pygrc/core/storage.py`
- `src/pygrc/models/grc_v2.py` as the current stub entrypoint

New files should be created only where the implementation pressure justifies them.
In particular, the plan should not imply that `core/observables.py` still needs to be
introduced from scratch.

## Spec-Locked Step Order

Phase 4 should treat the v2 step order as normative rather than approximate.

The executable `GRCV2.step()` should follow this ordered baseline:

1. compute node tensors `K_i`
2. compute edge conductances `w_ij`
3. compute selected analytic edge labels
4. build/update graph Laplacian if required
5. compute node potentials `Phi_i`
6. compute edge fluxes `J_ij`
7. detect sink set and attraction basins
8. detect sparks using eigenvalue or Cheeger proxy
9. apply soft-split initialization/progression
10. apply front birth
11. apply configured boundary behavior
12. apply continuity update to `C_i`
13. enforce exact budget preservation
14. compute observables

Tests and helper decomposition should reference this order explicitly.

## Required `GRCV2State` Surface

Phase 4 should implement `GRCV2State` as a real `@dataclass` subclass of `GRCState`
to match the v2 spec directly.

The intended state contract is:

```python
@dataclass
class GRCV2State(GRCState):
    nodes: dict[NodeId, float]                  # C_i
    edges: dict[EdgeId, float]                  # w_ij
    geometric_length: dict[EdgeId, float]
    temporal_delay: dict[EdgeId, float]
    flux_coupling: dict[EdgeId, float]
    flux: dict[OrientedEdgeId, float]           # J_ij
    potential: dict[NodeId, float]              # Phi_i
    sink_set: set[NodeId]
    basins: dict[NodeId, set[NodeId]]
    split_registry: dict[str, Any]
    rng_state: Any | None
```

`OrientedEdgeId` should be treated explicitly in implementation planning as a stable
oriented edge key, for example one ordered pair such as:

```python
type OrientedEdgeId = tuple[EdgeId, NodeId]
```

or an equivalent deterministic directed-edge identifier.

`split_registry` should be treated as structured model state rather than an opaque blob.
At minimum, Phase 4 should expect it to carry enough information to serialize and resume:

- parent node ID
- child node IDs
- split ratio / distribution state
- current progress or elapsed split time
- completion status

The executable model should expose these fields clearly enough that serialization,
tests, and later `GRCV3` lift work do not have to rediscover the state shape.

## Required Parameter Catalogue

Phase 4 should validate the full v2 required parameter surface, not just the mode flags.

At minimum, the resolved `GRCV2` config should carry:

- `dt`
- `alpha`, `beta`, `gamma`, `delta`
- `eta`
- `kappa_c`
- `lambda_c`, `xi_c`, `zeta_c`
- site potential selection and any required potential parameters
- `eps_spark` or `h_thr`
- `tau_split`
- `lambda_birth`
- `alpha_seed`
- `eps_prune`
- `curvature_backend`
- `frame_mode`
- `boundary_mode`
- `split_distribution_mode`
- `edge_label_selection`

The plan should treat the scalar evolution coefficients and topology thresholds as
first-class validated inputs, not as incidental constants hidden in helper code.

`site potential selection and potential parameters` remain part of the required v2
parameter surface. If their concrete shape is not fully obvious from the spec text
alone, the implementation phase should resolve them directly against
`papers/2025-12-GRC-V2.md` rather than inventing an undocumented interpretation.

## Constitutive Mode Value Sets

The executable model should reject unsupported constitutive mode values at construction
time using the exact spec-defined sets:

- `curvature_backend`: `ollivier | forman | none`
- `frame_mode`: `host_embedding | induced_local_frame | combinatorial`
- `boundary_mode`: `prune | barrier | ghost`
- `split_distribution_mode`: `equal | custom`

The Phase 0 rollout guidance still applies:

- default authoritative baseline: `curvature_backend = "none"`
- first in-house richer backend: `forman`
- later advanced backend: `ollivier`

## Edge-Label Rules That Phase 4 Must Preserve

The `GRCV2` plan should treat the shared label contract as part of the executable model,
not as serializer-only metadata.

Required analytic labels:

- `geometric_length`
- `temporal_delay`
- `flux_coupling`

Required formulas/interpretations:

```python
flux_coupling_ij := abs(J_ij)
temporal_delay_ij = geometric_length_ij / (v0 + rho * flux_coupling_ij + eps_tau)
```

Required serialization/inspection sidecars:

- `edge_label_computation_mode`
- `edge_label_params`

Mode values should stay aligned with the common-interface contract:

- `geometric_length`: `ambient_metric | induced_intrinsic | intrinsic_surrogate`
- `temporal_delay`: `transport_ratio`
- `flux_coupling`: `absolute_flux`

`edge_label_selection` still controls which labels are populated, with `"all"` as the
baseline default.

## Frame And Capability Advertising

Phase 4 should keep the capability surface truthful to the chosen frame mode.

`list_capabilities()` must include exactly one of:

- `host_embedding_frame`
- `intrinsic_frame`

If `frame_mode="host_embedding"`, the config/state surface must identify the required
host-provided geometric fields explicitly rather than relying on undocumented ambient
coordinates.

## Budget-Remainder Guidance To Carry Forward

The common-interface remainder rules remain binding in Phase 4:

- store target budget explicitly
- store running remainder only when a step cannot be closed exactly
- clear remainder by an explicit correction step as soon as practical
- never allow silent drift to accumulate across many steps

Budget enforcement helpers and tests should reference this guidance directly.

## Expected Code Shape After Phase 4

The exact files may still evolve, but the intended Phase 4 shape is close to:

```text
src/pygrc/
  core/
    observables.py          # already exists; extend only if needed
    budget.py               # optional new helper module if budget logic needs separation
  models/
    grc_v2.py
    grc_v2_state.py          # optional split if state/helpers need separation
    grc_v2_kernels.py        # optional split for pure update helpers
tests/
  models/
    test_grc_v2_*.py
```

The exact split may differ, but the boundary between:

- public `GRCV2` model surface,
- internal update helpers,
- and deterministic tests

should already be clear.

## Workstreams

## 1. `GRCV2` State And Config Surface

### Tasks

- Replace the Phase 1 stub behavior in `src/pygrc/models/grc_v2.py`.
- Define the concrete `GRCV2State` surface on top of `GRCState`.
- Implement `GRCV2State` as a dedicated `@dataclass` subclass of `GRCState` in
  `src/pygrc/models/grc_v2_state.py`, or inline in `src/pygrc/models/grc_v2.py`
  if the split does not justify a separate file.
- Validate required v2 parameters and constitutive modes at construction time.

### Required Decisions

- `frame_mode`, `boundary_mode`, `curvature_backend`, `split_distribution_mode`,
  and `edge_label_selection` are explicit resolved params
- required scalar evolution coefficients and topology thresholds are validated explicitly
- `GRCV2` capabilities include exactly the required baseline claims
- `list_capabilities()` advertises exactly one of:
  - `host_embedding_frame`
  - `intrinsic_frame`
- the model exposes one stable initial-state construction path from config

### Acceptance Criteria

- `GRCV2.from_config(...)` constructs a valid executable baseline model.
- `GRCV2.get_state()` exposes a coherent `GRCV2State` shape.
- Construction-time validation rejects unsupported mode values early.

## 2. Conductance, Labels, Potential, And Flux Core

### Tasks

- Implement node-tensor / conductance-map computation from node coherence and local graph state.
- Implement the scalar dynamical conductance `w_ij`.
- Implement selected analytic edge labels:
  - `geometric_length`
  - `temporal_delay`
  - `flux_coupling`
- Implement the shared edge-label computation metadata:
  - `edge_label_computation_mode`
  - `edge_label_params`
- Implement node potential computation.
- Implement directed edge flux computation.

### Required Decisions

- conductance and flux helpers should be deterministic and side-effect controlled
- analytic labels remain interpretive products; only `w_ij` drives the core update
- label availability follows the common-interface computation-mode contract
- `flux_coupling := abs(J_ij)` is explicit rather than inferred later
- `temporal_delay` follows the transport-ratio formula from the spec
- directed flux preserves antisymmetry explicitly
- local directional reconstruction follows the configured `frame_mode`

### Acceptance Criteria

- One step computes stable `w_ij`, `Phi_i`, and `J_ij` values from a fixed state.
- Selected edge labels are populated consistently with `edge_label_selection`.
- The implementation keeps baseline `GRCV2` scalar-edge semantics intact.

## 3. Identity Basins And Proxy Sparks

### Tasks

- Implement sink-set detection from directed flux.
- Implement basin extraction from repeated successor composition.
- Implement at least one spark trigger backend:
  - restricted Laplacian eigenvalue trigger
  - or Cheeger conductance proxy
- Support the public backend selector where multiple spark backends exist.

### Required Decisions

- sink extraction tie-breaks are deterministic
- directed edge `i -> j` exists when `J_ij > 0`
- sink set is derived from non-positive outflow plus positive inflow
- basin extraction follows repeated successor composition
- basin membership is reproducible from the current flux graph
- spark candidates are ordered deterministically before topology changes are applied
- the Phase 4 reference path should start with one explicit authoritative spark backend,
  preferably the Cheeger proxy unless the eigenvalue path is already equally stable

The v2 spec does not itself mandate a default spark backend, only that the public
configuration can choose the supported backend. The Phase 4 plan is therefore choosing
practical implementation guidance here, not claiming that the spec requires that default.

Phase 4 does not need to implement every candidate spark backend before the rest of the
`GRCV2` loop is executable. The current phase should keep one backend authoritative so
soft split, birth, continuity, and budget behavior can be validated end to end first.
Additional spark backends and backend-to-backend behavioral comparison should be
revisited after Phase 4 closeout, or later when comparison against richer families is
actually informative.

### Acceptance Criteria

- The model produces reproducible sink sets and basin partitions for a fixed state.
- Spark detection is deterministic for fixed params and fixed state.
- Spark outputs are structured enough to drive split/birth decisions without hidden globals.

## 4. Topology Events: Soft Split And Front Birth

### Tasks

- Implement soft split initialization from spark events.
- Implement split progression over `tau_split`.
- Apply the baseline equal split-distribution rule.
- Implement front birth at frontier nodes from outward flux pressure.
- Ensure new nodes and edges enter the weighted backend deterministically.

### Required Decisions

- baseline split distribution is `equal`
- parent removal happens only after split completion
- split completion condition is explicit and testable
- new IDs come only from the backend monotone counters
- multiple topology events in one step follow one explicit application order

### Acceptance Criteria

- Split progression changes topology deterministically over successive steps.
- Birth adds nodes/edges and transfers seed mass without violating budget invariants.
- Topology events can be serialized and replayed through the Phase 3 path.

## 5. Boundary Handling And Pruning

### Tasks

- Implement baseline `prune` boundary behavior.
- Add internal hooks for `barrier` and `ghost` modes if they are included in Phase 4;
  otherwise reject unsupported modes clearly.
- Preserve exact budget through pruning/boundary regularization.
- Keep boundary behavior explicit in observables and snapshot state where relevant.

### Required Decisions

- Phase 4 reference path should treat `prune` as the minimum fully supported boundary mode
- if `barrier` or `ghost` are only partial in Phase 4, they must fail explicitly rather
  than silently degrade into `prune`
- `eps_prune` is a validated required parameter and the pruning threshold is explicit
- prune ordering and redistribution order are deterministic

### Acceptance Criteria

- The reference implementation supports the baseline `prune` mode correctly.
- Unsupported richer boundary modes are not silently misrepresented.
- Boundary handling does not break replay or budget preservation.

## 6. Continuity Update, Budget Enforcement, And Observables

### Tasks

- Implement the continuity update for node coherence.
- Enforce exact budget preservation or explicitly bounded remainder accounting.
- Compute required observables:
  - `abundance`
  - `weighted_abundance`
  - `sink_count`
  - `budget_current`
  - `budget_error`
  - `num_nodes`
  - `num_edges`
- Add recommended observables where practical:
  - `spark_count`
  - `birth_count`
  - `prune_count`
  - average conductance

### Required Decisions

- one explicit budget target definition is used consistently through the loop
- final budget correction/remainder handling happens in one known place
- remainder handling follows the common-interface guidance from Phase 0/1
- coherence must remain non-negative after budget correction
- observable computation is derived from post-step state, not mixed intermediate state

### Acceptance Criteria

- Each step returns a coherent `StepResult` with deterministic observables/events.
- Budget error is zero or within the explicitly accepted bounded remainder policy.
- Observables match the actual post-step graph/state.

## 7. Model Integration On The Shared Runtime Surface

### Tasks

- Make `GRCV2.step()` return a real `StepResult`.
- Make `from_state(...)` construct a runnable model from explicit state and params.
- Make `set_state(...)` validate incoming v2 state before installation.
- Make `reset()` restore the construction baseline deterministically.
- Make `run(...)`, `snapshot()`, `save(...)`, and `load(...)` work on the executable model.
- Ensure `list_capabilities()` and `compute_observables()` are truthful for the real model.
- Keep state/save/load compatible with the Phase 3 serializer.

### Required Decisions

- executable `GRCV2` keeps the same public contract shape as the stub
- snapshot groups remain aligned with the v2 spec and the common serializer
- persistence is routed through the shared Phase 3 path:
  - `save_snapshot(...)`
  - `load_snapshot(...)`
  - `restore_weighted_graph(...)`
- RNG state persistence is routed through the shared Phase 3 helpers:
  - `serialize_rng_state(...)`
  - `deserialize_rng_state(...)`
- `params_hash` remains an explicit serialized field and canonical identity marker
- state restoration is sufficient to resume deterministic stepping

### Acceptance Criteria

- `GRCV2` runs from config through multiple steps and emits stable snapshots.
- Save/load resumes the model without changing IDs, counters, params identity, or ordering.
- The executable model does not need a separate persistence path from other families.

## 8. Deterministic Tests And Smoke Coverage

### Tasks

- Add deterministic unit tests around:
  - parameter validation
  - error handling for invalid params/state/topology requests
  - one-step update behavior
  - sink/basin extraction
  - spark detection
  - split/birth application
  - prune/budget enforcement
  - save/load and replay
- Add one or more smoke-style scenarios for the full v2 loop.
- Verify that fixed seed + fixed params + fixed initial state gives repeatable results.

The default test placement should stay aligned with the existing repo pattern:

- `tests/models/test_grc_v2_*.py` for focused model tests
- `tests/models/` for larger deterministic scenario tests when they remain unittest-shaped
- repo-root smoke scripts only when the scenario is intentionally manual/operator-facing

Required common-interface error paths to cover explicitly:

- invalid topology
- invalid parameter ranges
- negative coherence after correction
- unsupported capability requests
- incompatible state deserialization

### Acceptance Criteria

- The `GRCV2` baseline is covered by both focused unit tests and at least one end-to-end smoke scenario.
- Replay/save/load tests prove deterministic persistence across actual model steps.
- No test depends on `GRCV3` or `GRC9` semantics.

## 9. Paper-Alignment Remediation

### Tasks

- Reconcile the executable `GRCV2` constitutive core against `papers/2025-12-GRC-V2.md`.
- Replace any baseline surrogate that currently contradicts the paper’s central v2 equations unless the deviation is intentionally kept and explicitly documented.
- Re-run the paper-facing smoke and deterministic test matrix after each constitutive correction.

### Required Decisions

- Eq. (1) tensor construction must either be implemented directly or reduced to a clearly justified discrete form that preserves the paper’s three-term structure:
  - density term
  - gradient-pressure term
  - flux-feedback term
- Eq. (2) conductance must be aligned with the paper’s exponential constitutive map, or any retained approximation must be called out explicitly as a Phase 4 deviation.
- Observable naming must not silently redefine paper terms:
  - `abundance` should match the paper definition
  - any mass-sum observable should use a different name if retained
- Birth behavior must follow the paper’s Bernoulli rule while preserving deterministic replay through explicit RNG seed/state handling.
- `curvature_backend` must be upgraded from placeholder surrogates to real in-house weighted-substrate implementations of:
  - `forman`
  - `ollivier`

### Acceptance Criteria

- The executable loop no longer contradicts the paper on the central v2 constitutive claims without that contradiction being explicitly documented.
- Paper-facing smoke coverage passes against the remediated implementation.
- Remaining deviations, if any, are deliberate, named, and narrow enough that `GRCV2` still serves as the reference executable baseline for later family lift work.

### Accepted Residual Deviations

After the remediation pass, no residual deviation is accepted for the birth law or for
the declared curvature backends:

- front birth should follow the paper-facing Bernoulli rule
- deterministic replay should come from explicit `rng_seed` and serialized `rng_state`,
  not from replacing the Bernoulli rule with a threshold rule
- `curvature_backend="forman"` and `curvature_backend="ollivier"` should refer to real
  in-house weighted-substrate implementations, not placeholders

If any narrower residual deviation remains after those upgrades, it must be recorded
explicitly in the checklist and justified against the paper rather than treated as an
implicit baseline simplification.

## Deliverables

Phase 4 should produce:

- executable `GRCV2` model behavior
- validated v2 family config/state surface
- deterministic weighted-graph step loop
- sink/basin and spark machinery
- split/birth/prune baseline behavior
- budget enforcement and required observables
- paper-alignment remediation of the constitutive baseline
- `GRCV2`-specific tests and smoke coverage

## Acceptance Criteria

Phase 4 is complete only if all of the following are true.

### A. Structural Acceptance

- `src/pygrc/models/grc_v2.py` is an executable model, not a stub.
- The model uses `WeightedGraphBackend` and the shared core contracts.
- Snapshot/save/load continue to use the common Phase 3 persistence layer.

### B. Semantic Acceptance

- One full `GRCV2` step performs the required ordered semantics from the spec.
- Sink sets, basins, and spark proxies are reproducible.
- Split, birth, and prune behavior are explicit and deterministic.
- The constitutive core is either aligned with the paper’s main equations or any remaining deviations are explicitly documented and accepted.

### C. Budget Acceptance

- Budget preservation is enforced through the full update loop.
- Remainder behavior is explicit and bounded if non-zero.
- Topology events do not hide untracked mass loss or gain.

### D. Determinism Acceptance

- Fixed initial state + fixed params + fixed RNG seed produce identical step sequences.
- Save/load roundtrip preserves the ability to continue deterministically.
- Snapshot and observable ordering remain stable.
- Backend-derived serialization order remains deterministic.
- Stable integer IDs are preserved without reuse; tombstoned-slot policy remains intact.

### E. Boundary Acceptance

- No `GRCV3`-only state (gradient/Hessian/hierarchy objects) leaks into `GRCV2`.
- No `GRC9`-only substrate logic leaks into `GRCV2`.
- No third-party graph or persistence framework is required.

## Suggested Follow-On Documents

Create these only if the implementation pressure justifies them:

- `Phase-4-EquationMap.md` for the concrete numerical/update ordering
- `Phase-4-EventOrdering.md` if split/birth/prune ordering becomes subtle
- `Phase-4-TestMatrix.md` if the deterministic scenario set outgrows the checklist
