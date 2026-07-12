# LGRC9V3 Restoration Identity Specification

Status: Phase 8 additive contract in implementation. The internal embedded
GRC9V3 state component is available; the public composite identity remains
pending.

This specification defines a versioned, library-owned equality surface for
save/load restoration. It does not redefine raw snapshots, change runtime
dynamics, or claim that every valid restoration must reproduce the same
in-memory representation byte for byte.

The first contract identity is:

```text
lgrc9v3_restoration_identity_v1
```

Companion implementation records:

- [`../implementation/Phase-8-LGRC9-RestorationIdentityPlan.md`](../implementation/Phase-8-LGRC9-RestorationIdentityPlan.md)
- [`../implementation/Phase-8-LGRC9-RestorationIdentityChecklist.md`](../implementation/Phase-8-LGRC9-RestorationIdentityChecklist.md)

## Motivation

Canonical JSON serialization and semantic restoration identity answer
different questions:

```text
raw snapshot digest
  = identity of one complete serialized representation

restoration identity
  = identity of the canonical scientific and continuation-relevant state
    restored from that representation
```

The canonical serializer guarantees deterministic encoding of the supplied
snapshot. It does not, by itself, guarantee:

```text
model.snapshot()
==
type(model).load(model.snapshot()).snapshot()
```

A loader may legitimately materialize deterministic defaults or canonicalize
an undirected representation while preserving the represented state.

## Contract Boundary

The restoration identity is:

- additive;
- versioned;
- deterministic;
- JSON-safe;
- model-family-specific;
- exact over its canonical payload;
- non-mutating; and
- independent of raw snapshot byte identity.

It is not:

- an RC identity, selfhood, or identity-acceptance claim;
- a replacement for continuation replay;
- a tolerance-based approximate-state comparison;
- a license to discard every field stored under `caches`;
- a snapshot schema migration;
- a hidden compatibility adapter; or
- evidence that two different model implementations are behaviorally
  equivalent.

## Public Surface

The bounded implementation should expose one concrete LGRC9V3 helper rather
than changing the abstract `GRCModel` interface:

```text
lgrc9v3_restoration_identity_v1
```

The helper should accept a supported model or snapshot input through an
explicit API and return a JSON-safe artifact. A matching digest helper may
return the SHA-256 digest of the canonical identity payload.

Exact callable names are frozen before source implementation. The artifact
kind and schema values are fixed here:

```text
artifact_kind = "lgrc9v3_restoration_identity"
artifact_schema_version = "lgrc9v3_restoration_identity_v1"
model_family = "LGRC9V3"
```

The embedded base-state component is internal to the LGRC9V3 artifact:

```text
component_kind = "lgrc9v3_embedded_grc9v3_state"
component_schema_version = "lgrc9v3_embedded_grc9v3_state_v1"
```

The exact callable names are:

```text
internal component artifact:
  build_lgrc9v3_embedded_grc9v3_state_v1

internal component digest:
  digest_lgrc9v3_embedded_grc9v3_state_v1

public composite artifact, pending Iteration 92:
  lgrc9v3_restoration_identity_v1

public composite digest, pending Iteration 92:
  digest_lgrc9v3_restoration_identity_v1
```

The embedded helpers are callable from their dedicated LGRC module for
testing and composition, but are not exported through the public models
facade. They do not create a public GRC9V3 identity contract.

## Embedded GRC9V3 Base-State Component

LGRC9V3 restoration identity must include an LGRC9V3-owned, read-only
projection of the `GRC9V3State` embedded in its runtime. It must not reproduce
an experiment-owned projection, add a public GRC9V3 identity API, or change the
GRC9V3 substrate.

The embedded component must cover the canonicalized continuation and
scientific state represented by the current GRC9V3 contract:

```text
resolved parameter identity
topology, incidence, port occupancy, and next stable IDs
node and basin attributes
canonical port-edge endpoints, conductance, and signed flux
analytic edge labels and their constitutive modes
potential, sink set, and basin membership
hierarchy and expansion state
choice and collapse registries
step index and time
budget target and remainder
random-generator state
event and observable state owned by GRC9V3
scientifically or operationally load-bearing cached quantities
coarse-state cache when it is preserved as runtime/evidence state
```

Version 1 records that coverage with this component shape:

```text
component_kind
component_schema_version
source_model_family
source_snapshot_schema
source_snapshot_version
resolved_parameter_identity
topology
stable_allocation
state
base_events
base_observables
included_state_groups
excluded_representation_fields
```

`stable_allocation` includes next IDs, live IDs, and live/tombstone slot
status. `state` is the complete current serialized `GRC9V3State` payload after
the existing GRC9V3 loader has materialized deterministic defaults. The LGRC
projection then independently canonicalizes undirected topology endpoints and
port-edge endpoint/sign orientation. `base_events` and `base_observables`
retain the normalized outer GRC9V3 evidence views as well as the corresponding
state-owned fields. Zero flux is represented as positive `0.0`; nonzero signed
flux remains identity-bearing.

Version 1 does not normalize signed zero globally. The I90 representation
cycle was source-backed only for oriented `port_edges[*].flux_uv`, so only
that field receives signed-zero normalization. Signed zero in potential,
labels, budget fields, caches, or future state remains exact identity-bearing
state unless a later source-backed contract revision proves it to be
representation-only. Iteration 93 must exercise such fields when checking the
identity fixed point; it may not silently widen the version-1 exclusion.

Before identity construction, deterministic normalization must resolve:

- absent versus materialized parameter identity;
- absent versus materialized deterministic RNG state;
- absent versus deterministically inferred budget-target provenance, under a
  declared provenance interpretation;
- undirected port-edge endpoint order, including the corresponding signed
  flux orientation; and
- canonical mapping, set, and sequence order.

Normalization must not mutate the source model or snapshot.

This component is scoped only to LGRC9V3 restoration. A general GRC9V3
restoration-identity contract would require a separate, non-Phase-8 plan.

## LGRC9V3 Composite Identity

The LGRC9V3 identity payload must contain:

```text
artifact_kind
artifact_schema_version
model_family
source_snapshot_schema
source_snapshot_version
embedded_grc9v3_state
lgrc9v3_runtime_artifact
events
observables
included_state_groups
excluded_representation_fields
```

The identity digest is computed over this payload. Raw snapshot digests may be
returned in a separate diagnostic envelope, but must not be included in the
restoration-identity digest.

The exact native `dynamics.lgrc9v3_runtime` artifact remains included. This
preserves packet ledgers, queues, clocks, causal routes, topology history,
surface lineage, multi-basin records, route arbitration, producer records,
idempotency state, and other serialized LGRC runtime surfaces.

Events and observables remain included because they are part of the auditable
scientific state and are validated by native load.

The embedded component intentionally contains both the state-owned event and
observable fields and the normalized outer GRC9V3 event/observable views. They
are separate serialized contract surfaces even when they agree. Iteration 93
must test sensitivity and restoration consistency for both paths.

## Representation Exclusions

Exclusions must be explicit and narrow. Version 1 may exclude only fields
whose difference is proven to be representation history rather than a change
to continuation, evidence, or claim-relevant state.

Permitted exclusion classes are:

```text
duplicate embedding of an already canonically represented group
mapping insertion order removed by canonical serialization
undirected endpoint order after signed-orientation canonicalization
absence versus deterministic materialization of one declared default
raw file layout or raw full-snapshot digest
```

The following are not blanket exclusions:

```text
caches
cached_quantities
coarse_cache
rng_state
budget state
provenance records
producer configuration
idempotency keys
dynamic port-edge flux
```

Some fields in these groups affect continuation or evidence even when their
container is named `cache`. They remain included unless a later identity
version individually proves and records a narrower exclusion.

## Required Relations

For any supported snapshot `S` and native restored model `M = load(S)`:

```text
identity(S) == identity(M.snapshot())
```

For repeated restoration:

```text
S1 = load(S).snapshot()
S2 = load(S1).snapshot()
identity(S) == identity(S1) == identity(S2)
```

The second relation is a restoration-identity fixed-point requirement. It does
not require `S`, `S1`, and `S2` to have equal raw digests. Representation-only
normalization, including signed-zero orientation on a physically zero
undirected flux, may remain visible in those raw observations.

Equal restoration identities are necessary for a restoration-equivalence
claim, but not sufficient for arbitrary behavioral equivalence. Bounded
equal-input continuation replay remains a separate required test.

## Compatibility

The v1 implementation must:

- preserve the existing snapshot schema and file format;
- keep old supported snapshots loadable;
- avoid writing identity artifacts into snapshots unless a later versioned
  extension explicitly opens that change;
- avoid changing `LGRC9V3.load()` behavior;
- avoid modifying GRC9V3, its public API, or its source files;
- avoid changing equations, event scheduling, topology mutation, producer
  eligibility, budgets, or observables; and
- fail clearly on unsupported model families or malformed snapshots.

Identity construction from an old snapshot may use deterministic native
restoration to materialize missing defaults. It must not invent scientific
state that the native loader cannot derive.

## Downstream Composition

The PyGRC restoration identity covers PyGRC-owned model state only. An
experiment or consuming project may compose it with separately versioned
state that PyGRC does not own:

```text
composite branch identity
  = PyGRC restoration identity
  + ecology-owned medium/pool identity
  + experiment-owned intervention identity
```

Such composition must not relabel ecology-owned state as native LGRC state.

## Validation Matrix

The implementation must include positive, sensitivity, compatibility, and
negative-control coverage.

Positive coverage:

- native identity equality before save and after load;
- exact LGRC runtime-artifact preservation;
- event and observable preservation;
- restoration-identity fixed point across repeated load;
- equal-input continuation equivalence; and
- deterministic repeated identity construction.

Sensitivity coverage must show that identity changes when included state
changes, including at least:

- topology or stable allocation IDs;
- node/basin state;
- nonzero signed port-edge flux;
- edge labels or constitutive selection;
- potential, sink set, or basin membership;
- budget target or remainder;
- RNG state;
- event or observable state; and
- LGRC queue, clock, ledger, surface, topology-history, or producer state.

Normalization controls must show identity stability for:

- canonical undirected endpoint reversal with physically equivalent signed
  flux;
- deterministic RNG and parameter-identity materialization;
- declared budget-source materialization; and
- canonical mapping/set order.

Fail-closed controls must reject:

- deletion of included scientific state;
- mutation hidden beneath a cache container;
- identity construction for the wrong model family;
- malformed runtime artifacts;
- raw snapshot equality relabeled as restoration identity;
- experiment-owned projection relabeled as native identity; and
- equal identity relabeled as proof of unrestricted continuation equivalence.

## Claim Ceiling

The strongest allowed claim is:

```text
versioned PyGRC restoration identity for supported LGRC9V3 snapshots, with a
read-only embedded-GRC9V3 state component and bounded continuation-equivalence
validation
```

It does not support native agency, selfhood, semantic identity, identity
acceptance, organism/life, ecology, unrestricted replay equivalence, or Phase
8 completion.
