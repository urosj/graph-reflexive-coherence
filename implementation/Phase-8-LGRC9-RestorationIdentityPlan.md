# Phase 8 LGRC9 Restoration Identity Plan

Status: Open; Iterations 90-91 complete. The public composite restoration
identity, replay/sensitivity matrix, and closeout remain pending.

This continuation is opened by RCAE P2-I1 C01/C02. C01 compared complete
LGRC9V3 snapshots across native save/load and stopped before scientific
execution because nested GRC9V3 representation was normalized. C02 retained
raw snapshot digests, used an RCAE-owned restoration projection, and required
equal-input continuation. All 84 C02 opportunities preserved the projection
and continuation, but the projection remains experiment-owned and
fixture-bounded.

Companion records:

- [`../specs/lgrc-9-v3-restoration-identity.md`](../specs/lgrc-9-v3-restoration-identity.md)
- [`Phase-8-LGRC9-RestorationIdentityChecklist.md`](./Phase-8-LGRC9-RestorationIdentityChecklist.md)

## Goal

Add a bounded, versioned, library-owned restoration identity:

```text
LGRC9V3-owned read-only projection of embedded GRC9V3 state
  + exact LGRC9V3 runtime artifact
  + events and observables
  -> lgrc9v3_restoration_identity_v1
```

The identity should let PyGRC and downstream projects distinguish semantic
restoration equality from raw snapshot representation equality without
changing runtime behavior or snapshot compatibility.

## Why This Is A Phase 8 Continuation

The gap appears at the LGRC9V3 native snapshot boundary and affects causal
branch replay. It does not require new GRC equations or a new ecology
mechanism. The work belongs entirely to the Phase 8 LGRC9V3 implementation
surface. LGRC9V3 must inspect its embedded GRC9V3 state without changing the
GRC9V3 substrate or public API.

## Non-Goals

- Do not force byte-identical full snapshots after load.
- Do not redesign the snapshot schema or move the nested base snapshot.
- Do not preserve arbitrary endpoint orientation.
- Do not retain unresolved defaults solely to reproduce pre-load
  representation.
- Do not copy pre-load caches back after restoration.
- Do not special-case only the six fields observed by RCAE.
- Do not exclude the complete nested GRC9V3 snapshot from native identity.
- Do not change GRC9V3 or LGRC9V3 equations, scheduling, topology, budgets,
  producers, observables, or claim semantics.
- Do not add the method to the abstract `GRCModel` interface in this tranche.
- Do not modify `src/pygrc/models/grc_9_v3.py`, GRC9V3 behavior, or the
  GRC9V3 public API.
- Do not modify RCAE from the graph repository.
- Do not retroactively reclassify C01 or C02.

## Source Basis

RCAE read-only source basis:

```text
../reflexive-coherence-agentic-ecology/
  experiments/2026-07-AE01-post-n30-demand-composition-atlas/
    reports/P2-I1-C01-bounded-incomplete.md
    reports/P2-I1-C02-result.md
    configs/p2_i1_c02_execution_policy.json
    scripts/p2_i1_execution.py
```

Graph source basis:

```text
specs/grc-common-interface.md
specs/lgrc-9-v3-spec.md
implementation/Phase-0-DeterminismConventions.md
src/pygrc/core/serialization.py
src/pygrc/core/digests.py
src/pygrc/models/grc_9_v3.py
src/pygrc/models/grc_9_v3_state.py
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/lgrc_9_v3_runtime_state.py
```

RCAE artifacts may define the observed gap and downstream need. They must not
define PyGRC's general identity projection.

## Current Boundary

Supported now:

- canonical JSON-safe snapshot serialization;
- strict snapshot-family validation;
- native GRC9V3 and LGRC9V3 save/load;
- exact preservation tests for LGRC runtime artifacts;
- multiple bounded continue-after-load tests; and
- raw snapshot digest helpers.

Missing now:

- a public semantic restoration-identity surface;
- sensitivity tests proving which state is identity-bearing; and
- a downstream capability path that RCAE P2-I2 can consume without inventing
  another native-state projection.

Implemented internally in Iteration 91:

- an LGRC9V3-owned canonical projection of embedded GRC9V3 state;
- deterministic default materialization through the unchanged GRC9V3 loader;
- stable allocation/tombstone-state recording;
- undirected endpoint and signed-flux canonicalization; and
- deterministic component artifact and digest helpers.

Documented and frozen in Iteration 90:

- canonical file encoding does not imply restored-model re-snapshot equality;
- raw snapshot cycling remains observable and outside restoration identity;
  and
- no lost scientific state was observed in the retained RCAE fixture.

Architectural debt retained by this tranche:

```text
caches.base_grc9v3_snapshot is named as a cache but is required by LGRC9V3.load
```

The tranche records that tension but does not migrate the snapshot layout.

## Ownership

### Core Serialization

Core serialization owns canonical encoding and raw snapshot digests. It should
document that canonical output does not imply re-snapshot equality after
loader normalization. It should not decide family-specific scientific
identity.

### LGRC9V3

LGRC9V3 owns both the read-only embedded-GRC9V3 state projection and the
composite identity over that projection, exact LGRC runtime artifact, events,
and observables. This ownership does not permit GRC9V3 source or behavior
changes.

### GRC9V3 Boundary

GRC9V3 is an inspected dependency, not an implementation target. If the work
reveals a genuine GRC9V3 restoration defect or a need for a general GRC9V3
identity API, record it and stop. Any correction belongs to a separate
non-Phase-8 tranche.

### Downstream Projects

RCAE and other consumers own any external medium, pool, intervention, or
experiment state not serialized by PyGRC. They may compose identities, but may
not relabel external state as native LGRC state.

## Change Boundary

The baseline iteration opens documentation and freeze artifacts only. The
first source-changing iteration may touch:

```text
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/lgrc_9_v3_restoration.py, if a dedicated module is selected
src/pygrc/models/__init__.py
specs/grc-common-interface.md
specs/lgrc-9-v3-spec.md
specs/lgrc-9-v3-restoration-identity.md
tests/models/test_lgrc_9_v3_runtime.py
docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md
```

Any change to snapshot payload shape, loader behavior, runtime output, or
abstract model interfaces is outside this tranche and requires a separately
reviewed extension.

## Iteration 90. Baseline And Contract Freeze

Freeze current behavior and reproduce the bounded RCAE observation without
changing source:

- raw LGRC9V3 snapshot digest differs after one native load;
- exactly the declared normalization leaves differ for the retained fixture;
- outer geometry, exact LGRC runtime artifact, events, and observables agree;
- existing continue-after-load tests pass;
- current snapshots remain loadable; and
- the target public identity surface is absent.

A retained read-only diagnostic under `scripts/` may reconstruct the fixture
and comparison. It is an Iteration 90 audit artifact, not PyGRC runtime code.

The freeze must also audit repeated loads for representation cycling or
continued normalization. Raw snapshot stabilization is observed, not required;
the later native restoration identity must be the stable fixed point.

## Iteration 91. Embedded GRC9V3 State Projection

Implement an LGRC9V3-owned, non-mutating canonical projection of the complete
embedded GRC9V3 scientific and continuation state. The component remains
internal to `lgrc9v3_restoration_identity_v1`.

Required properties:

- normalize deterministic defaults without mutating source state;
- canonicalize undirected endpoints and signed flux together;
- include state hidden by the outer LGRC snapshot groups;
- include load-bearing and evidence-bearing cached state;
- use explicit narrow representation exclusions;
- reject malformed or wrong-family inputs; and
- change digest when included state changes.

No GRC9V3 source, API, constructor, loader, snapshot, or runtime behavior may
change in this iteration.

Implemented as a dedicated LGRC-owned module:

```text
src/pygrc/models/lgrc_9_v3_restoration.py
```

The projection deep-copies the embedded snapshot, restores that copy through
the existing GRC9V3 loader, and serializes the fully materialized state into
the internal `lgrc9v3_embedded_grc9v3_state_v1` component. It then applies an
LGRC-owned endpoint/sign canonicalization without mutating the source input.
This preserves GRC9V3 as an inspected dependency and avoids duplicating its
default-resolution rules.

## Iteration 92. LGRC9V3 Composite Restoration Identity

Implement `lgrc9v3_restoration_identity_v1` by composing:

```text
LGRC9V3 embedded-GRC9V3 state component
exact dynamics.lgrc9v3_runtime artifact
events
observables
snapshot schema/version provenance
explicit inclusion/exclusion manifest
```

Expose the concrete public helper and digest path without changing
`GRCModel`, `snapshot()`, `save()`, or `load()` behavior.

## Iteration 93. Replay, Sensitivity, And Compatibility Matrix

Run the complete matrix defined by the dedicated specification:

- before/after restoration identity equality;
- raw snapshot inequality remains observable;
- restoration-identity fixed point across repeated load;
- exact runtime artifact;
- equal-input continuation twins;
- included-state mutation sensitivity;
- representation-normalization invariance;
- old snapshot loading;
- malformed/wrong-family fail-closed controls; and
- full regression suite.

The matrix must include nonzero signed port-edge flux and nonempty basin,
registry, budget, RNG, and LGRC runtime surfaces. A fixture containing only the
six RCAE differences is insufficient.

## Iteration 94. Closeout And RCAE Return

Close only if:

- the public identity is versioned and documented;
- runtime and snapshot behavior remain unchanged;
- compatibility and sensitivity matrices pass;
- raw snapshot digest remains separately observable;
- the claim ceiling remains restoration identity only; and
- a downstream handoff states how P2-I2 may explicitly adopt the identity.

If complete base-state normalization requires snapshot redesign, stop the
tranche as bounded incomplete. Record the graph-side debt and return the
versioned C02 projection as the explicit P2-I2 fallback. Do not broaden source
changes to force completion.

## Acceptance State

The intended closeout state is:

```text
lgrc9v3_restoration_identity_v1_supported = true
raw_snapshot_byte_identity_required = false
snapshot_schema_changed = false
runtime_behavior_changed = false
old_snapshots_loadable = true
equal_input_continuation_validated = true
rcae_p2_i2_native_identity_handoff_ready = true
```

The strongest allowed claim is a versioned PyGRC restoration identity for
supported LGRC9V3 snapshots, including a read-only embedded-GRC9V3 state
component, with bounded continuation validation.
