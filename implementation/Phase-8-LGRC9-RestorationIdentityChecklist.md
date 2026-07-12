# Phase 8 LGRC9 Restoration Identity Checklist

This checklist tracks:

- [`Phase-8-LGRC9-RestorationIdentityPlan.md`](./Phase-8-LGRC9-RestorationIdentityPlan.md)
- [`../specs/lgrc-9-v3-restoration-identity.md`](../specs/lgrc-9-v3-restoration-identity.md)
- [`Phase-8-LGRC9-RestorationIdentityCloseout.md`](./Phase-8-LGRC9-RestorationIdentityCloseout.md)
- [`Phase-8-LGRC9-RestorationIdentityCloseout.json`](./Phase-8-LGRC9-RestorationIdentityCloseout.json)

## Ground Rules

- [x] Treat C01 as an over-broad RCAE equality predicate, not evidence of lost
  scientific state in its tested continuation.
- [x] Treat C02 as fixture-bounded evidence, not the general PyGRC identity
  definition.
- [x] Keep raw snapshot identity distinct from restoration identity.
- [x] Keep restoration identity distinct from bounded continuation replay.
- [x] Include embedded GRC9V3 state through an LGRC9V3-owned read-only
  projection.
- [x] Keep GRC9V3 source, behavior, and public API outside Phase 8 changes.
- [x] Do not exclude the complete nested base snapshot merely because it is
  stored under `caches`.
- [x] Preserve snapshot format, loader behavior, runtime dynamics, budgets,
  topology semantics, events, observables, and compatibility.
- [x] Keep external ecology medium/pool state outside native PyGRC identity.
- [x] Keep RC identity, selfhood, identity acceptance, agency, ecology, and
  Phase 8 completion claims blocked.

## Iteration 90. Baseline And Contract Freeze

Status: passed.

### Documentation Definition

- [x] Add the dedicated restoration-identity specification.
- [x] Define raw snapshot identity versus restoration identity.
- [x] Define LGRC9V3 ownership and the read-only GRC9V3 boundary.
- [x] Define explicit inclusion and exclusion policy.
- [x] Define compatibility and claim boundaries.
- [x] Define the P2-I2 adoption/fallback decision boundary.

### Baseline Work

- [x] Record exact source revision and clean-worktree state.
- [x] Reproduce the C01 fixture observation against current source.
- [x] Record raw before/after snapshot digests.
- [x] Record recursive difference paths and values.
- [x] Confirm exact LGRC runtime-artifact equality.
- [x] Confirm outer topology, basin attributes, edge labels, events, and
  observables agree.
- [x] Confirm existing bounded continue-after-load tests pass.
- [x] Test and record repeated-load normalization or representation cycling.
- [x] Confirm no restoration-identity public callable exists.
- [x] Record source diff outside implementation/spec records as empty.
- [x] Write baseline freeze JSON and Markdown artifacts.

### Required Baseline Artifacts

```text
implementation/Phase-8-LGRC9-RestorationIdentityBaselineFreeze.json
implementation/Phase-8-LGRC9-RestorationIdentityBaselineFreeze.md
scripts/audit_lgrc9v3_restoration_baseline.py
```

### Implementation Details

Iteration 90 uses the retained diagnostic:

```text
scripts/audit_lgrc9v3_restoration_baseline.py
sha256 = b9647dbe53ab67d087f079c01da64f2ba883fa5cc702a2ae4e3a91bc793f3c0a
```

The script is an implementation-boundary audit, not runtime code. It:

1. resolves the RCAE repository through the relative sibling-repository
   default or explicit `--rcae-root`;
2. loads the retained P2-I1 fixture and cell definitions read-only;
3. reconstructs seed `211`, `candidate-conditioning`, through the public
   PyGRC `LGRC9V3` facade;
4. runs the writer packet window and emits the declared feedback surface;
5. captures the post-writer/post-surface branch-point snapshot;
6. performs three native save/load cycles in a temporary directory;
7. computes canonical raw snapshot digests at each cycle;
8. compares snapshots recursively with type-sensitive and signed-zero-sensitive
   leaf comparison;
9. compares outer groups, the exact LGRC runtime artifact, and the historical
   RCAE C02 projection separately; and
10. confirms that the target native restoration-identity callable is absent.

The first load reproduces the C01 normalization boundary, but the stricter
comparator records seven canonical leaves rather than six:

```text
budget_target_source: absent -> explicit_state
params_identity: null -> resolved digest
port edge 1 endpoints: (1, 0) -> (0, 1)
port edge 1 flux_uv: +0.0 -> -0.0
runtime RNG: null -> deterministic state
metadata RNG: absent -> deterministic state
```

The signed-zero leaf was absent from C01's count because ordinary Python
equality treats `+0.0 == -0.0`. Canonical JSON preserves the sign, so repeated
loads alternate raw digests:

```text
before save       = 37ac41bce4a0c8b4ae93bb0435b2abb0312e189b5d73380a46533b0ae5486a87
after first load  = bd316a368afc4728cd8a60b00abd1fdb3bd8deb1a45ba24c23fd9a5edfee6f9d
after second load = efa8171d1c366fb23e2059c2c6418ba7a8c3f73a6e43dd119390159132c12e04
after third load  = bd316a368afc4728cd8a60b00abd1fdb3bd8deb1a45ba24c23fd9a5edfee6f9d
```

Only `caches.base_grc9v3_snapshot.dynamics.state.port_edges.1.flux_uv`
changes after the first load, alternating `-0.0` and `+0.0`. Flux magnitude
and Python value equality remain unchanged. All outer groups and the exact
`dynamics.lgrc9v3_runtime` artifact remain equal.

This changes the implementation requirement in one precise way:

```text
raw snapshot fixed point = not required
restoration identity fixed point = required
signed zero in embedded port-edge flux = canonically collapsed by LGRC identity
```

It does not authorize dropping dynamic port-edge flux from identity. Nonzero
signed flux remains identity-bearing and is a required Iteration 93
sensitivity control. It also does not authorize any GRC9V3 source or behavior
change.

Verification:

```text
.venv/bin/python scripts/audit_lgrc9v3_restoration_baseline.py
    passed

.venv/bin/python -m pytest \
  tests/core/test_serialization_contract.py \
  tests/models/test_grc_9_v3_state.py \
  tests/models/test_lgrc_9_v3_runtime.py -q
    203 passed, 17 subtests passed

.venv/bin/python -m ruff check \
  scripts/audit_lgrc9v3_restoration_baseline.py
    passed

git diff --name-only HEAD -- src tests examples
    no output

git diff --check
    passed
```

Iteration 90 therefore closes as a documentation, diagnostic, and freeze
iteration. Restoration identity remains unsupported until Iterations 91-93
implement and validate the LGRC-only surface.

## Iteration 91. Embedded GRC9V3 State Projection

Status: passed.

- [x] Freeze exact public callable names and artifact schema.
- [x] Add the internal `lgrc9v3_embedded_grc9v3_state_v1` component.
- [x] Include canonical resolved parameter identity.
- [x] Include complete topology and stable allocation state.
- [x] Include node, basin, hierarchy, and expansion state.
- [x] Include canonical port edges with signed flux orientation.
- [x] Include analytic edge labels and constitutive modes.
- [x] Include potential, sink set, and basin membership.
- [x] Include choice and collapse registries.
- [x] Include step/time, budget target, and remainder.
- [x] Include RNG state and parameter identity after deterministic
  normalization.
- [x] Include base-state events and observables represented by current GRC9V3
  state.
- [x] Include load-bearing/evidence-bearing cached quantities and coarse state.
- [x] Record every representation-only exclusion explicitly.
- [x] Confirm identity construction does not mutate model or snapshot input.
- [x] Reject malformed and wrong-family inputs.
- [x] Add deterministic artifact and digest tests.
- [x] Confirm `src/pygrc/models/grc_9_v3.py` is unchanged.
- [x] Confirm GRC9V3 public exports are unchanged.
- [x] Confirm embedded component helpers remain absent from the public models
  facade until Iteration 92.
- [x] Confirm GRC9V3 behavior and snapshot outputs are unchanged.

### Implementation Details

Iteration 91 adds:

```text
src/pygrc/models/lgrc_9_v3_restoration.py
tests/models/test_lgrc_9_v3_restoration.py
```

The exact internal component callables are:

```text
build_lgrc9v3_embedded_grc9v3_state_v1
digest_lgrc9v3_embedded_grc9v3_state_v1
```

The public Iteration 92 callable names are also frozen, but remain
unimplemented:

```text
lgrc9v3_restoration_identity_v1
digest_lgrc9v3_restoration_identity_v1
```

The implementation accepts a complete LGRC9V3 snapshot, validates the outer
family, locates the required embedded GRC9V3 snapshot, and deep-copies it. The
copy is restored through the existing `GRC9V3._from_snapshot` path. This is a
read-only consumption of the current GRC9V3 contract: it resolves parameter
identity, RNG state, budget provenance, and other deterministic defaults
without changing GRC9V3 source or behavior.

Topology, stable allocation, and serialized state are all derived from the
same normalized GRC9V3 snapshot. Stable allocation is reconstructed from that
snapshot's next IDs and live topology IDs, avoiding a split between live-object
and serialized representations.

The resulting component records:

```text
resolved parameter identity
canonical topology and port occupancy
next stable node/edge IDs
live and tombstoned allocation slots
complete serialized GRC9V3 state
normalized base GRC9V3 event and observable views
included-state manifest
explicit representation exclusions
```

The complete state includes node/basin/hierarchy/expansion fields, analytic
edge labels, potential, sinks, basin membership, choice/collapse registries,
step/time/budget/remainder, RNG, events, observables, cached quantities, and
coarse state. Cache containers are not excluded wholesale.

After existing default materialization, the LGRC-owned projection performs
the normalization that the I90 baseline proved necessary:

```text
topology endpoints are ordered by (node_id, slot)
port-edge endpoints are ordered by (node_id, port_id)
nonzero flux changes sign when endpoint orientation is reversed
zero flux is normalized to positive 0.0
```

The nonzero flux sign remains scientific state. Only the sign bit of an exact
zero after orientation canonicalization is excluded as representation history.
Signed zero is not normalized in any other state field in version 1; those
values remain exact until a later source-backed contract revision proves a
narrow representation-only exclusion.

Port-edge/topology correspondence is consumed through the unchanged GRC9V3
loader and its post-hydration state validation. I91 does not impose a second
raw pre-hydration key policy, because the current GRC9V3 contract may
materialize supported edge defaults from topology. I93 malformed-input controls
must verify this inherited boundary rather than silently redefine it.

Dedicated tests prove:

```text
repeated construction is deterministic
the source snapshot is not mutated
node and edge allocation tombstones are retained
before-save and three repeated-load components agree
zero-flux sign is canonical
opposite raw endpoint encodings preserve the same nonzero signed flux
nonzero signed-flux mutation changes the digest
included coherence mutation changes the digest
non-mapping input fails closed
invalid conductance fails closed
missing topology edge ID fails closed
wrong-family input fails closed
missing embedded base snapshot fails closed
```

The component is intentionally not exported through `pygrc.models` in I91.
It remains an internal LGRC composition surface until I92 adds and exports the
complete public identity. `src/pygrc/models/grc_9_v3.py`, the GRC9V3 public
facade, snapshot payloads, loaders, equations, and runtime behavior are
unchanged.

### Verification Results

Focused restoration and serialization verification:

```text
.venv/bin/python -m pytest \
  tests/core/test_serialization_contract.py \
  tests/models/test_grc_9_v3_state.py \
  tests/models/test_lgrc_9_v3_runtime.py \
  tests/models/test_lgrc_9_v3_restoration.py -q

211 passed, 20 subtests passed
```

Static verification:

```text
ruff format --check: passed
ruff check: passed
mypy lgrc_9_v3_restoration.py: passed
git diff --check: passed
I90 RCAE baseline diagnostic rerun: passed
GRC9V3 source/public-facade diff from I90: empty
```

The complete repository test run before the final review corrections reached:

```text
1621 passed
741 subtests passed
25 failed
```

All 25 failures require precomputed discovery/telemetry files under ignored
`outputs/...` session paths that are absent from this checkout. Git confirms
those paths are ignored. No full-suite failure imports or exercises the I91
module, and the complete focused LGRC9V3/GRC9V3 serialization matrix passes.
The repository-wide suite is therefore not globally green in this checkout,
but no I91 regression was observed.

The final review corrections add only fail-closed validation and focused
tests. The complete 20-minute repository run was not repeated because the same
ignored output prerequisites remain absent; the complete focused matrix above
was rerun after those corrections.

## Iteration 92. LGRC9V3 Composite Restoration Identity

Status: passed.

- [x] Add `lgrc9v3_restoration_identity_v1`.
- [x] Consume the internal embedded-GRC9V3 state component.
- [x] Include the exact LGRC runtime artifact.
- [x] Include LGRC event state.
- [x] Include LGRC observables.
- [x] Include source snapshot schema/version provenance.
- [x] Include explicit inclusion/exclusion manifest.
- [x] Keep raw snapshot digest outside the identity digest.
- [x] Export the concrete helper through the public models facade.
- [x] Do not change the abstract `GRCModel` interface.
- [x] Do not change `snapshot()`, `save()`, or `load()` payload or behavior.
- [x] Add deterministic repeated-construction tests.

### Implementation Details

Iteration 92 extends the dedicated LGRC-owned restoration module with:

```text
LGRC9V3_RESTORATION_IDENTITY_KIND
LGRC9V3_RESTORATION_IDENTITY_SCHEMA_VERSION
lgrc9v3_restoration_identity_v1
digest_lgrc9v3_restoration_identity_v1
```

The concrete public helpers are exported through `pygrc.models`. They are not
methods on `GRCModel` or `LGRC9V3`, so the abstract interface and runtime class
contracts remain unchanged.

Both supported inputs follow one explicit path:

```text
LGRC9V3 model -> model.snapshot() -> composite identity
LGRC9V3 snapshot mapping ---------> composite identity
```

The composite artifact contains:

```text
artifact kind and schema version
model family
source snapshot schema/version
Iteration 91 embedded GRC9V3 state component
canonical dynamics.lgrc9v3_runtime artifact (current artifacts remain exact)
exact serialized LGRC9V3 events
exact serialized LGRC9V3 observables
included-state manifest
explicit representation exclusions
```

At I92, the native runtime, event, and observable groups were deep-copied from
the supplied current snapshot. I93 retained exact current runtime values while
adding native default materialization for older supported runtime artifacts.
Events and observables remain exact. The complete artifact is
JSON-canonicalized. Raw snapshot bytes, raw full-snapshot digest, duplicate
outer GRC9V3 views, and the raw embedded GRC9V3 representation are excluded.
No raw digest is present in the artifact used by
`digest_lgrc9v3_restoration_identity_v1`.

Dedicated I92 tests use a nonempty packet-event runtime and prove:

```text
model and snapshot inputs produce the same artifact
source snapshot remains unchanged
runtime artifact is included exactly
events and observables are included exactly
artifact kind, schema, family, and manifests are present
raw snapshot and raw digest are absent
artifact and digest construction are deterministic
digest equals canonical digest of the public artifact
identity agrees before save and after native load
runtime, event, and observable mutations change the digest
unsupported input fails closed
missing runtime artifact fails closed
malformed event or observable groups fail closed
```

Iteration 92 establishes the public composition surface, not the full claim.
The comprehensive replay, sensitivity, normalization, old-snapshot, and
negative-control matrix remains assigned to Iteration 93.

The post-I92 state is therefore:

```text
lgrc9v3_restoration_identity_v1_callable_available = true
lgrc9v3_restoration_identity_v1_artifact_shape_frozen = true
lgrc9v3_restoration_identity_v1_supported = false
support_blocker = iteration_93_matrix_not_run
phase8_restoration_identity_closeout_complete = false
```

The stricter integer checks in the identity projection intentionally reject
boolean IDs even though Python treats `bool` as a subclass of `int`. This is a
family-specific identity validation boundary, not a change to core snapshot
validation. Stable allocation remains an explicit slot-by-slot representation
in version 1; its size scales with the highest allocated stable ID by design.

### Verification Results

```text
.venv/bin/python -m pytest \
  tests/core/test_serialization_contract.py \
  tests/models/test_grc_9_v3_state.py \
  tests/models/test_lgrc_9_v3_runtime.py \
  tests/models/test_lgrc_9_v3_restoration.py -q

216 passed, 20 subtests passed
```

```text
I92 dedicated tests: 13 passed, 3 subtests passed
ruff format --check: passed
ruff check: passed
mypy lgrc_9_v3_restoration.py: passed
git diff --check: passed
I90 RCAE baseline diagnostic rerun: passed
GRCModel, GRC9V3, LGRC9V3 runtime/state source diff from I91: empty
```

The only source changes are the dedicated restoration module and concrete
`pygrc.models` exports. Snapshot construction, save/load behavior, runtime
state, equations, scheduling, producers, and abstract interfaces remain
unchanged. The repository-wide suite was not repeated in I92 because the 25
known ignored-output prerequisite failures recorded under I91 remain present;
all directly affected and focused regression tests pass.

## Iteration 93. Replay, Sensitivity, And Compatibility Matrix

Status: passed.

### Positive Matrix

- [x] `identity(before_save) == identity(after_load)`.
- [x] Native LGRC runtime artifacts remain exact.
- [x] Events and observables remain exact.
- [x] Equal-input continuation twins remain equivalent.
- [x] Repeated identity construction is deterministic.
- [x] Restoration identity remains fixed across repeated native loads.

### Sensitivity Matrix

- [x] Topology mutation changes identity.
- [x] Stable allocation-ID mutation changes identity.
- [x] Node/basin mutation changes identity.
- [x] Nonzero signed port-edge flux mutation changes identity.
- [x] Edge-label or constitutive-mode mutation changes identity.
- [x] Potential, sink-set, or basin-membership mutation changes identity.
- [x] Budget target or remainder mutation changes identity.
- [x] RNG mutation changes identity.
- [x] Event or observable mutation changes identity.
- [x] State-owned event/observable mutations change the normalized embedded
  component; raw duplicate outer-only changes normalize away when the native
  loader does not restore them as state.
- [x] LGRC queue, clock, ledger, surface, topology-history, route, or producer
  mutation changes identity.
- [x] A mutation hidden under a cache container still changes identity when
  that field is load-bearing or evidence-bearing.

### Normalization Controls

- [x] Equivalent undirected endpoint reversal plus signed-flux reversal keeps
  identity stable.
- [x] Deterministic parameter-identity materialization keeps identity stable.
- [x] Deterministic RNG materialization keeps identity stable.
- [x] Declared budget-source materialization keeps identity stable.
- [x] Mapping/set insertion-order changes keep identity stable.
- [x] Signed zero outside oriented port-edge flux remains exact and is not
  silently normalized by version 1.

### Compatibility And Negative Controls

- [x] Old supported GRC9V3 snapshots remain loadable.
- [x] Old supported LGRC9V3 snapshots remain loadable.
- [x] Raw full-snapshot digest remains observable and may differ.
- [x] Missing included state fails closed.
- [x] Wrong model family fails closed.
- [x] Malformed runtime artifact fails closed.
- [x] Raw digest cannot be relabeled as restoration identity.
- [x] Experiment projection cannot be relabeled as native identity.
- [x] Equal restoration identity cannot be relabeled as unrestricted
  behavioral equivalence.
- [x] Full focused and core/model regression suites pass.
- [x] Repository-wide ignored-output prerequisite failures remain separately
  recorded and unrelated to restoration identity.
- [x] `git diff --check` passes.

### Implementation Details

Iteration 93 adds:

```text
tests/models/test_lgrc_9_v3_restoration_matrix.py
scripts/audit_lgrc9v3_restoration_identity_matrix.py
implementation/Phase-8-LGRC9-RestorationIdentityRCAEReplayMatrix.json
implementation/Phase-8-LGRC9-RestorationIdentityValidationMatrix.md
```

The local executable matrix has 19 test methods and five subtests. It uses
current nonempty LGRC packet state, explicit topology/allocation gaps,
source-current causal-pulse surface production, older supported snapshot
variants, repeated native loads, and equal-input continuation twins.

The original RCAE C02 fixture is rerun read-only at seed 211 in the
`candidate-conditioning` cell. Its four raw representations retain three
distinct raw digests and the known signed-zero cycle, while all four produce
one restoration identity digest. All 11 retained RCAE checks pass, including
bounded equal-input continuation after the branch point.

I93 found that copying an older raw LGRC runtime artifact was insufficient:
supported historical snapshots may omit later-added empty logs that the native
restorer materializes. The composite now passes the runtime artifact through
`restore_lgrc9v3_runtime_state_artifact(...).to_artifact()`. Current artifacts
remain exact; old supported artifacts reach the same fixed point. No runtime,
loader, snapshot, state, GRC9V3, or abstract-interface implementation changed.

The post-I93 state is:

```text
restoration_identity_matrix_passed = true
lgrc9v3_restoration_identity_v1_candidate_supported_pending_closeout = true
lgrc9v3_restoration_identity_v1_supported = false
support_blocker = iteration_94_closeout_not_run
raw_snapshot_byte_identity_required = false
unrestricted_behavioral_equivalence = false
```

### Verification Results

```text
I93 matrix: 19 passed, 5 subtests passed
I91-I93 focused matrix: 235 passed, 25 subtests passed
core + models regression: 857 passed, 260 subtests passed
RCAE retained replay: 11 / 11 checks passed
audit script SHA-256: 51c022184120019a0b55a165f21c34e602fd4d58bbbbfc4097f7daa418d0f593
matrix test SHA-256: b5c740545022c3be11e256d95645b57954bce993a46e7cc26edcca33517eb154
RCAE matrix SHA-256: a0ec3183fba78e21110a948cd349c380553383051cd3e6958d04618076bbc426
ruff: passed
mypy: passed
git diff --check: passed
```

## Iteration 94. Closeout And RCAE Return

Status: passed.

- [x] Produce closeout JSON and Markdown artifacts.
- [x] Record exact supported snapshot families and versions.
- [x] Record exact identity schema version and public callable paths.
- [x] Record raw snapshot identity as separate observational data.
- [x] Record restoration-identity fixed-point status and raw representation
  cycling separately.
- [x] Record bounded continuation-validation scope.
- [x] Record old-snapshot compatibility status.
- [x] Confirm snapshot schema unchanged.
- [x] Confirm runtime behavior unchanged.
- [x] Confirm C01/C02 classifications unchanged.
- [x] Record explicit P2-I2 realization-profile transition requirements.
- [x] Record the C02 projection fallback if native identity cannot close
  without broad redesign.
- [x] Update Phase 8 plan, checklist, handoff, specs, and reference guide.
- [x] Keep all unsafe claim flags false.

### Implementation Details

Iteration 94 adds:

```text
implementation/Phase-8-LGRC9-RestorationIdentityCloseout.json
implementation/Phase-8-LGRC9-RestorationIdentityCloseout.md
```

The closeout freezes `pygrc.snapshot` version 1 LGRC9V3 model/snapshot input,
the `lgrc9v3_restoration_identity_v1` artifact schema, and both public
`pygrc.models` callable paths. Plain GRC9V3 snapshots remain outside the
LGRC-specific helper; no GRC9V3 public identity API is introduced.

Raw snapshot cycling and restoration-identity stability are recorded as
separate facts. C01 remains bounded incomplete under its over-broad raw
equality predicate, and C02 remains passed under its RCAE-owned projection.
P2-I2 may adopt the native helper only through an explicit realization-profile
transition. The C02 projection remains a non-native fallback.

No source, runtime, loader, snapshot schema, or behavior changes are made in
I94.

All unsafe claim flags in the closeout JSON are explicitly `false`.

The final state is:

```text
lgrc9v3_restoration_identity_v1_supported = true
raw_snapshot_byte_identity_required = false
snapshot_schema_changed = false
runtime_behavior_changed = false
old_snapshots_loadable = true
equal_input_continuation_validated = true
rcae_p2_i2_native_identity_handoff_ready = true
```

### Verification Results

```text
I91-I93 focused matrix: 235 passed, 25 subtests passed
RCAE retained replay rerun: 11 / 11 checks passed
closeout JSON parse and acceptance assertions: passed
recorded matrix artifact SHA-256 checks: passed
relative Markdown link check: passed
git diff --check: passed
I94 src/tests/scripts diff: empty
```

## Unsafe Claim Flags

The closeout must force false:

```text
raw_snapshot_byte_identity_required
unrestricted_continuation_equivalence
rc_identity_supported
selfhood_supported
identity_acceptance_supported
agency_supported
native_shared_medium_supported
ecology_supported
organism_or_life_supported
phase8_complete
```
