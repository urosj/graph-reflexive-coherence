# Phase 6 GRC9 Step Loop

## Purpose

This note fixes the exact Phase 6 reference `GRC9` step loop in one place.

The first representative runtime lanes used in Phase 6 may remain relatively
small, but the step loop itself is not a reduced or "toy" loop. It is the
paper-facing mechanical baseline that later runtime lanes, telemetry, and
`GRC9V3` hybrid work should inherit unless a later phase explicitly revises it.

## Canonical Phase 6 Step Order

The current Phase 6 baseline `GRC9.step()` should execute the following order:

1. `compute_row_tensor`
   Build the row-diagonal local tensor `K_i` from:
   - the density term
   - the row-wise mismatch term
   - the flux-feedback term

2. `compute_metric`
   Update occupied-port-pair conductance using the Phase 6 constitutive metric
   law under the selected `curvature_backend`.

3. `compute_edge_labels`
   Compute the selected analytic edge-label families on occupied port-pairs:
   - geometric length
   - temporal delay
   - flux coupling

4. `compute_potential`
   Compute node potentials from the current conductance-weighted coherence
   differences and the selected site-potential derivative.

5. `compute_flux`
   Compute occupied-port-pair flux using the canonical `PortEdge` orientation,
   with oriented views required to remain antisymmetric.

6. `detect_identities`
   Rebuild the successor map, sink set, and basins from the current conductance,
   potential, and flux state.

7. `detect_sparks`
   Evaluate the mechanical spark rule:
   - compute or refresh column diagnostics `H^(b)` for the current candidate
     sink set
   - apply the saturation gate
   - evaluate the instability and/or column-proxy branch
   - classify each candidate with explicit `SparkKind`
   - use the intentional single-class precedence:
     instability `>` column proxy `>` sign crossing

8. `apply_expansion`
   Apply spark-triggered mechanical expansion sequentially:
   - expand the first deterministic candidate
   - verify budget preservation immediately after the local topology event
   - correct only if drift is detected
   - recompute sink/candidate structure before considering the next spark
   - if adiabatic expansion is enabled, register or advance the in-progress
     schedule here rather than treating it as an out-of-band process

9. `apply_growth`
   Apply configured front growth:
   - select parent nodes under the configured birth rule
   - attach new nodes through the lowest-index inactive port on each selected
     parent

10. `apply_boundary_behavior`
    Apply configured boundary behavior if implemented:
    - `prune`
    - `barrier`
    - `ghost`
    Phase 6 only executes `prune`. `barrier` / `ghost` are reserved spec-facing
    names and should be rejected during config/state validation until explicit
    boundary behavior and `boundary_barrier` capability support exist.

11. `apply_continuity`
    Update node coherence by `dt`-scaled flux divergence on the settled
    post-topology, post-boundary graph for this step.

12. `enforce_budget`
    Preserve the global budget exactly at the end of the step:
    - close against the scalar `budget_target` fixed before step execution
    - use the uniform shift rule when sufficient
    - fall back to positivity-preserving correction when needed
    - record bounded remainder if exact closure cannot be completed numerically

13. `refresh_or_invalidate_coarse_cache`
    Refresh or invalidate coarse states after all value and topology mutations
    relevant to this step have settled.

14. `compute_observables`
    Compute observables from the fully settled post-step state.

## Why There Is No Separate Post-Flux Label Pass

Unlike the Phase 5 `GRCV3` loop, the Phase 6 baseline does not introduce a
second post-flux edge-label pass.

That is intentional.

Phase 6 follows the `GRC9` spec-locked order:

1. tensor
2. conductance
3. selected labels
4. potential
5. flux
6. identities
7. sparks
8. expansion
9. growth
10. boundary
11. continuity
12. budget
13. coarse cache
14. observables

If a selected label family needs information that is only available after the
new flux update, that should be treated as:

- a constitutive choice that must still respect the spec order,
- or a clearly documented later extension,
- not as a silent second label phase.

The baseline loop therefore keeps one label step only.
The paper's compact algorithmic loop does not independently place
edge-label computation relative to potential, so this is a spec-driven
discrete-runtime choice rather than a paper-level reordering.

## Budget Target Precondition

The scalar budget target is a state invariant, not a value that should be
discovered after arbitrary runtime mutation. For paper-facing Phase 6 behavior:

```text
B = sum_i C_i
```

must be fixed from the initial live `node_coherence` field during construction
or `from_state(...)` normalization when no explicit target is provided.

The legacy lazy `_ensure_budget_target()` behavior is a compatibility fallback:
normal step paths infer it before budget-sensitive topology events, so ordinary
historical results are not automatically invalidated, but the locked-step
contract should treat construction-time target fixation as the preferred
invariant discipline.

## Why Column Diagnostics Live Inside Spark Detection

The column diagnostic

$$
H_s^{(b)}=\sum_{a=1}^{3} w_{s,a,b}\bigl(C_{n(s,a,b)}-C_s\bigr)
$$

depends on:

- current occupied-port conductance,
- current coherence,
- and the settled local port topology.

It does not require the sink set mathematically, but Phase 6 evaluates it
inside the spark-detection stage because:

- only sinks can spark in the baseline semantics,
- the current candidate set is therefore known only after identity extraction,
- and the diagnostic is part of the spark predicate, not a freestanding public
  phase of the loop.

Operationally, `_compute_column_diagnostic()` should run:

- after `detect_identities`
- before spark predicate evaluation
- inside the broader `detect_sparks` stage

Persistence policy:

- `prev_column_diagnostic` should be refreshed on every spark-detection pass
  for candidate sinks
- sign-crossing support, if enabled, consumes the previous-step values from that
  persisted state
- this keeps replay/debugging and telemetry symmetric even when the sign-crossing
  branch is disabled

This keeps the runtime order aligned with the spec while making the helper
surface explicit.

## Why Spark Classification Uses Priority Order

Phase 6 uses one deterministic spark classification per eligible sink.

The baseline precedence is:

1. `saturation_instability`
2. `saturation_column_proxy`
3. `saturation_sign_crossing`

This is intentional because:

- the three branches are alternative explanations for the same spark decision,
  not three independent topology events
- emitting multiple concurrent branch labels for one sink would complicate
  sequential expansion handling without adding mechanical resolution
- a single precedence rule keeps event payloads stable for replay and testing

If later work wants multi-cause attribution, that should be added as diagnostic
metadata, not by turning one sink into multiple spark events.

## Why Expansion Is Sequential

Phase 6 uses **sequential**, not batch, spark application.

The order is:

1. sort spark candidates deterministically
2. expand the first candidate
3. verify local budget preservation immediately
4. recompute sink/candidate structure on the changed substrate
5. continue only if additional valid candidates still exist

This is slower than a naive batch application, but it is safer because:

- expansion changes local topology materially
- sink membership may change immediately
- column reassignment may invalidate later candidates from the pre-expansion
  snapshot

The sequential rule is therefore part of the constitutive deterministic
baseline, not a temporary implementation shortcut.

If adiabatic expansion is enabled later, its sub-step schedule should remain
owned by the current sequential candidate. The runtime should therefore
advance that schedule inside the normal topology-event stage rather than
maintaining a second independent expansion queue.

## Why Boundary Handling Precedes Continuity

The Phase 6 implementation follows the `GRC9` spec, which places boundary
handling before continuity.

That ordering is authoritative for the discrete runtime because:

- boundary behavior can change the live topology or traversal cost surface
- continuity should sum flux divergence over the graph that actually survives
  this step
- applying continuity first would mix transport on a pre-boundary graph with a
  post-boundary state

The paper’s compact algorithmic loop does not break out a separate
boundary-management phase. The spec does, and the spec-level discrete order is
the implementation reference.

## Why Budget Preservation Appears Twice Around Expansion

Phase 6 uses two budget-related checkpoints for different reasons.

### Immediate Post-Expansion Verification

Expansion is a topology event that redistributes existing coherence across a new
module.

Immediately after expansion, the runtime should:

- verify that the event preserved budget by construction
- apply correction only if numerical drift or implementation error is detected

This is a local event-integrity check.

### End-Of-Step Budget Closure

After:

- growth
- boundary handling
- continuity

the global coherence field may still require one end-of-step exact closure pass.

That final pass is the canonical `enforce_budget` stage of the step loop.

The two checks therefore do not duplicate one another:

- immediate expansion verification protects topology-event integrity
- final budget closure protects whole-step state integrity

## Deterministic Tie-Break Rules

The baseline Phase 6 loop must keep the following tie-breaks explicit.

### Successor Map

When multiple neighbors share the same maximal positive outgoing flux for one
node, the successor map chooses the neighbor with the ascending node ID.

This is a concrete deterministic implementation detail required for replay and
testability. The paper's `argmax` rule does not supply a tie-break on its own.

### PortEdge Orientation

`PortEdge` stores one canonical orientation.

The baseline convention is:

- ascending `node_id` for `(node_u, node_v)`

Derived oriented views must satisfy the antisymmetry invariant implied by
`flux_uv`.

### Spark Candidates

Spark candidates are processed in deterministic order before sequential
expansion begins.

The exact ordering rule should remain stable and test-backed once implemented.

### Growth Port Choice

Parent selection may follow the configured birth rule, but chosen-port
selection is always:

- the lowest-index inactive port on the selected parent

This distinction must remain visible in code and tests.

## Coarse-Cache Timing

Phase 6 refreshes or invalidates coarse state only after the full step has
settled.

That is intentional because the coarse view can be invalidated by:

- conductance recomputation
- flux recomputation
- expansion rewiring
- growth
- and any other occupied-port topology mutation

Refreshing too early would risk caching a half-pre / half-post state.

The post-budget timing ensures the stored coarse state, if refreshed, is a real
post-step view. This does not require eager recomputation on every step:
invalidation may happen eagerly once the step settles, while actual coarse
rebuild remains on demand. That keeps the implementation compatible with the
paper's recommendation that coarse states be computed on demand and refreshed
when topology events require it.

## Minimum Observable Timing Contract

The required observables should be computed only after:

- topology events are settled
- continuity has run
- budget has been enforced
- coarse-cache state has been refreshed or invalidated

That means observables such as:

- `budget_current`
- `budget_error`
- `spark_count`
- `active_degree_histogram`

must describe the actual post-step state, not an intermediate runtime phase.

The paper's compact algorithmic loop does not list observables as a separate
mechanical phase. The explicit `compute_observables` step comes from the `GRC9`
spec and the Phase 6 runtime/artifact contract.

## Observable Identity Contract

Phase 6 now fixes the `abundance` contract explicitly.

Chosen contract:

- `abundance` is a topology-updated sink diagnostic derived inside
  `compute_observables()` from the current stored flux field

This means:

- it does **not** read the persisted step-6 `sink_set` directly
- it does **not** insert a new named `refresh_identities` phase into the public
  14-step loop
- it does **not** claim to be a second full reflexive pass after continuity

Operational meaning:

- topology is current at the time observables are computed
- successor/sink composition is recomputed locally for observability only
- the flux field is still the current stored flux surface rather than a freshly
  recomputed post-continuity flux pass

This is the Phase 6 baseline because it improves artifact honesty without
changing the canonical step contract.

Any later sink-derived telemetry lane should inherit this same definition unless
a later phase explicitly revises the family contract.

## Birth Rule Note

The paper's growth rule is probabilistic:

$$
p_{\mathrm{birth}}(i)=1-\exp(-\lambda F_i^{\mathrm{out}})
$$

The StepLoop fixes where birth selection occurs in the step, but does not by
itself force one sampling policy. The implementation must still decide
explicitly whether the Phase 6 baseline uses:

- seeded stochastic sampling under `rng_state`,
- or a deterministic birth-selection rule derived from outward-flux pressure

Whichever baseline is chosen, it should remain distinct from the separate
deterministic chosen-port rule:

- use the lowest-index inactive port once a parent has already been selected

## Phase 6 Boundary

This loop is the canonical Phase 6 `GRC9` baseline, but not the final possible
nine-slot loop forever.

Later phases may still add:

- richer boundary semantics
- additional curvature backends
- stronger source/projector coupling
- hybrid `GRC9V3` semantic layers
- more expressive artifact capture around topology events

For boundary behavior specifically, enabling `boundary_mode = barrier` or
`boundary_mode = ghost` later requires actual runtime implementation plus honest
capability advertisement through `boundary_barrier`; Phase 6 should not accept
those modes speculatively.

Those are extensions.
They should not silently replace the semantics fixed here.
