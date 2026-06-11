# Phase 6 Mid-Gate Review

Date: 2026-04-22

## Purpose

This artifact records the required mid-phase constitutive review for the Phase 6
`GRC9` baseline after Iterations 2 through 8.

The goal is not to claim Phase 6 closeout. The goal is to check whether the
current executable baseline still matches the intended mechanical `GRC9`
interpretation closely enough to justify moving on to Iteration 10 artifact and
telemetry work.

## Review Inputs

Reviewed sources:

- `implementation/Phase-6-ImplementationPlan.md`
- `implementation/Phase-6-EquationMap.md`
- `implementation/Phase-6-StepLoop.md`
- `src/pygrc/models/grc_9.py`
- `src/pygrc/models/grc_9_ports.py`
- `src/pygrc/models/grc_9_state.py`
- `src/pygrc/models/grc_9_coarse.py`
- `papers/2026-04-GRC-9.md`
- `specs/grc-9-spec.md`

Focused validation context:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_step tests.models.test_grc_9_coarse tests.models.test_grc_9_expansion tests.models.test_grc_9_sparks tests.models.test_grc_9_runtime tests.models.test_grc_9_tensor tests.models.test_grc_9_state tests.models.test_family_stubs`
- result:
  - `Ran 44 tests`
  - `OK`

## Gate Result

Current verdict:

- the executable baseline is still recognizably pure mechanical `GRC9`
- the row/column separation remains constitutive rather than decorative
- spark, expansion, growth, and coarse-graining remain inside the Phase 6
  mechanical boundary
- Iteration 10 may proceed

But the gate is not "clean with no caveats".

There is one constitutive runtime issue that should be fixed before strong
closeout claims:

1. the current observable contract is ambiguous about whether `abundance`
   describes the step-6 identity-phase sink count or a post-topology sink
   diagnostic for the current step

There were also two explicit boundary limitations that were acceptable at the
mid-gate stage and had to stay visible:

- `boundary_mode = barrier` and `boundary_mode = ghost` are still deferred
- artifact-backed telemetry lanes do not yet exist; that is Iteration 10 work

## Review By Required Topic

### 1. Row/Column Separation

Assessment: `pass`

Evidence:

- port/row/column conversion is isolated in `src/pygrc/models/grc_9_ports.py`
- `_compute_geometry()` groups incident edges by row only
- `_compute_column_diagnostic()` and expansion reassignment group by column only
- coarse-graining operates on column totals plus intra-column row profiles

Interpretation:

- rows still own tensor anisotropy
- columns still own interface families, rewiring, and Split
- there is no sign that the implementation has collapsed the chart into an
  undifferentiated nine-port bag

### 2. Tensor Representation Against Paper Intent

Assessment: `pass with one acceptable simplification`

Evidence:

- `_compute_geometry()` stores `row_tensor_diagonal` as a compact length-3
  payload in cached state rather than as a dense `3x3` matrix
- density, row mismatch, and flux-feedback terms are separated into explicit
  cached diagnostics

Interpretation:

- this matches the paper/spec intent that `K_i` is diagonal in the row basis
- the compact representation is a good implementation choice
- inspectability exists at runtime even though the tensor is not snapshot
  persisted

Open note:

- the tensor still lives in `cached_quantities` inside `grc_9.py` rather than a
  dedicated runtime helper module; that is structural debt, not constitutive
  drift

### 3. Spark Semantics Remain Purely `GRC9`

Assessment: `pass`

Evidence:

- `_detect_events()` uses active-degree saturation, the local instability
  proxy, the column diagnostic, and optional sign crossing
- the explicit precedence remains:
  - `saturation_instability`
  - `saturation_column_proxy`
  - `saturation_sign_crossing`
- there is no use of signed-Hessian state, hierarchy, choice, or collapse
  semantics

Interpretation:

- the current spark path is still mechanical `GRC9`
- the optional sign-crossing branch is still framed as a diagnostic extension,
  not as a hidden `GRC9V3` lift

Open note:

- the `deg_act >= 8` relaxation remains intentionally deferred, which is the
  correct Phase 6 boundary

### 4. Expansion Wiring And Reassignment Determinism

Assessment: `pass with explicit implementation compromise`

Evidence:

- `_apply_topology_changes()` is sequential
- `_apply_expansion()` uses deterministic sink ordering, canonical spine ports,
  per-column reassignment, and round-robin tree growth for `n > 4`
- expansion records are persisted in `expansion_registry`
- reassignment details are persisted in expansion event payloads

Interpretation:

- the topology event path is deterministic enough for replay and testing
- the implementation still respects column families during rewiring

Known compromise:

- exact old-port preservation is not always possible under the canonical center
  spine, so the current code falls back to the lowest available port in the
  same column tree
- this is already documented and is still acceptable at mid-gate

### 5. Coarse-Graining Exactness Claims

Assessment: `pass`

Evidence:

- `coarse_grain_nonnegative_port_field(...)` stores exact column totals and
  row profiles
- `split_nonnegative_port_field(...)` reconstructs the fine field exactly
- signed flux is represented through exact `J+` / `J-` decomposition
- compressed signed-flux mode remains deferred rather than being claimed
  implicitly

Interpretation:

- the current exactness claims are honest
- the implementation is not over-claiming compressed reconstruction support

### 6. Observability Strength For Later Artifact Lanes

Assessment: `mixed`

What is already good:

- required baseline observables exist:
  - `abundance`
  - `budget_current`
  - `budget_error`
  - `num_nodes`
  - `num_port_edges`
  - `spark_count`
  - `active_degree_histogram`
- event logs, expansion registry, and coarse cache all persist through
  snapshots
- step replay and snapshot digests are deterministic

What is not yet good enough for strong later claims:

- there is no representative artifact-backed lane yet
- there is no dedicated saved-output narrative for event sequences
- the current observables depend partly on identity state that is not refreshed
  again after topology mutation inside `step()`

## Findings

### 1. High: `abundance` Currently Has Ambiguous Identity Timing Semantics

Where:

- `src/pygrc/models/grc_9.py`
  - `step()`
  - `compute_observables()`

Problem:

- `compute_observables()` derives `abundance` from `self._state.sink_set`
- that sink set is computed at step 6, before expansion and growth
- later topology changes can change the live graph materially
- a naive late `_detect_identities()` call would not fully solve this because:
  - new edges start with `flux_uv = 0.0`
  - continuity has already shifted coherence
  - no second `_compute_potential()` / `_compute_flux()` pass occurs

Impact:

- at the time of the mid-gate, `abundance` was ambiguous between:
  - identity-phase sink count
  - and a would-be post-topology sink count
- any later sink-derived telemetry lane would have inherited that ambiguity if
  the contract had remained unresolved

Mid-gate recommended fix direction:

- preserve the locked 14-step loop rather than inserting a new named
  `refresh_identities` phase
- resolve the observable contract explicitly in Iteration 10 by choosing one
  of:
  - re-contract `abundance` as the identity-phase sink count
  - or compute a non-persisted topology-updated sink diagnostic from the
    current stored flux field and document that it is not a second reflexive
    pass

Later resolution:

- this was resolved in Iteration 10 and is no longer an open closeout blocker
- the implemented Phase 6 baseline chose the local non-persisted
  topology-updated sink diagnostic from the current stored flux field
- the locked 14-step public loop was preserved

### 2. Medium: Boundary Behavior Is Still Only Partially Implemented

Where:

- `src/pygrc/models/grc_9.py`
  - `_apply_boundary_behavior()`

Problem:

- `prune` is the only executable baseline
- `barrier` and `ghost` were not executable at the time of the review and now
  remain reserved until explicit boundary behavior and `boundary_barrier`
  capability support are implemented

Impact at the time of the mid-gate:

- this was acceptable for the then-current baseline
- but any later evidence lane would need to avoid implying Phase 6 had a
  complete boundary matrix

### 3. Medium: Artifact-Lane Observability Is Not Ready Yet

Where:

- Phase 6 iteration structure as a whole

Problem:

- current evidence is still mostly tests plus snapshots
- Iteration 10 artifact/report work has not started

Impact:

- mid-gate passes
- closeout does not

## Decision

Mid-gate decision: `proceed with Iteration 10, while carrying one required
runtime follow-up`

Required carried follow-up:

1. resolve the `abundance` observable contract explicitly before Phase 6
   closeout-style claims

Deferred-but-explicit boundaries:

1. `boundary_mode = barrier`
2. `boundary_mode = ghost`
3. artifact-backed telemetry/report lanes

Recorded post-mid-gate decision:

- Phase 6 should reject `barrier` / `ghost` during config/state validation
  rather than accepting them and failing later in `step()`
- enabling either mode later requires actual runtime implementation plus honest
  `boundary_barrier` capability advertisement
