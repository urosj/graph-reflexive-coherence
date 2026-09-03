# Common GRC Interface: V4 Extension

## Status and applicability

This document is the additive common-interface extension for
[`GRCV4`](grc-v4-spec.md) and [`GRC9V4`](grc-9-v4-spec.md). It imports the
[Common GRC Class and Interface Specification](grc-common-interface.md)
unchanged and strengthens that contract only for the V4 family.

A conforming V4 implementation must satisfy all three applicable layers:

1. the unchanged common GRC interface;
2. this V4 interface extension; and
3. the relevant family contract, either `GRCV4` or `GRC9V4`.

The family contracts own the mathematical equations, profile population, and
nine-port specialization. This extension owns only the shared Python-facing
interface consequences of those contracts. If this extension and a V4 family
contract disagree about V4 semantics, the family contract controls and this
extension must be corrected.

This document does not alter the interface or behavior of `GRCV2`, `GRCV3`,
`GRC9`, `GRC9V3`, or `LGRC9V3`.

## Changes relative to the common interface

| Common-interface area | V4 extension |
|---|---|
| Concrete classes | Registers `GRCV4(GRCModel)` and `GRC9V4(GRCV4)`. |
| State | Adds complete-profile, graph/orientation, context, typed nonresource state, lifecycle receipt, and cache-provenance requirements. |
| Parameters | Makes every trajectory-changing candidate, realization, geometry, differential, charge, solver, and lifecycle choice part of canonical profile identity. |
| Graph backend | Requires deterministic vertex and oriented-edge order, typed differential and pairing surfaces, signed reorientation, and reconstruction from serialized identity. |
| Lifecycle | Strengthens `step()` to the V4 atomic complete-step transaction and makes profile migration and topology change typed, receipted operations. |
| Capabilities | Adds V4 common, candidate, realization, and nine-port specialization capabilities without treating planned support as implemented support. |
| Observables | Adds profile, charge, current, geometry, solver, lifecycle, and specialization diagnostics while preserving authority labels. |
| Serialization | Preserves complete profile and lifecycle identity and enough provenance to reject or rebuild derived caches. |
| Errors | Requires fail-closed typed rejection before atomic commit for identity, domain, solver, charge, migration, event, or restoration failure. |

No V4 extension changes the signatures of the required common public methods.
It strengthens their accepted inputs, outputs, identity, atomicity, and
serialization semantics.

## Concrete class relationships

The common class registry is extended by:

```python
class GRCV4(GRCModel): ...
class GRC9V4(GRCV4): ...
```

The state hierarchy is correspondingly:

```python
class GRCV4State(GRCState): ...
class GRC9V4State(GRCV4State): ...
```

`GRCV4` is executable only with exactly one admitted complete profile.
`GRC9V4` inherits that profile requirement and adds one complete nine-port
specialization identity. Neither class may erase variant-specific fields to
fit the base `GRCState` shape.

## Construction and parameter resolution

The inherited `from_config()` and `from_state()` methods must resolve and
validate a complete V4 identity before exposing a model instance. That
identity includes, as applicable:

- candidate and realization IDs;
- differential, charge, geometry, context, units, gauge, normalization, and
  domain IDs;
- solver and deterministic root-selection policy;
- lifecycle, migration, topology-event, reset, and receipt policies;
- every trajectory-changing coefficient and tolerance;
- canonical resolved-parameter identity; and
- for `GRC9V4`, port chart, row backend, Hessian sign, spark lane, expansion,
  coarse-graining, compatibility branch, and GRC9V3 target identity.

Defaults must resolve at construction. Environment, observer, device,
telemetry, and storage choices remain outside model parameters unless the
family contract explicitly promotes one into trajectory semantics.

`from_state()` must validate the complete snapshot before exposing any live
state. It must not silently select another profile, create or discard retained
history, rebase charge, repair topology, or substitute a solver policy.

## State and authority extension

The base `GRCState` fields remain required. For V4, `budget_target` is the
serialized `Q_target` scalar and the two names must agree exactly.

Every `GRCV4State` additionally binds:

- graph and orientation identity;
- one exact `GRCV4Profile` and its canonical parameter identity;
- context identity;
- authoritative resource state $C$;
- only the candidate- and realization-specific nonresource coordinates
  admitted by that profile;
- ordered lifecycle, migration, event, and information-loss receipts;
- RNG state where applicable; and
- provenance for every retained derived cache.

The profile rules determine whether $W_A$ or $Z_4$ is authoritative.
Potential, current, selector, $T_C$, Hodge operators, structural geometry,
solver roots, row summaries, and coarse summaries remain derived or transient
unless a family contract explicitly says otherwise. Caching or serializing a
derived surface does not promote it to authoritative state.

`get_state()` may expose live state under the base contract, but callers must
not mutate profile identity or partially update V4 authority. `set_state()`
must validate the entire target state atomically and must not alter the reset
baseline, charge target, graph, profile, or history by implication.

## Graph and differential backend extension

A graph backend used by `GRCV4` must add these guarantees to the common graph
requirements:

- deterministic live vertex order and oriented-edge order;
- a stable orientation identity and incidence operator $B$;
- the scalar-to-edge differential $d_0=B^\top$;
- declared vertex and one-form pairings;
- deterministic boundary behavior;
- covariant graph relabeling and signed-edge reorientation;
- stable identities for cached differential, Hodge, geometry, and current
  surfaces; and
- reproducible reconstruction or explicit rejection from serialized backend
  identity.

The graph-generic backend must not imply a nine-port row basis. `GRC9V4`
additionally requires ordered ports, unique endpoint-port occupancy,
port-to-edge lookup, the fixed $3\times3$ chart, deterministic row/column
rewiring, and the fixed row-basis differential backend defined by its family
specification.

A backend choice that changes values, regularity, normalization, or semantic
interpretation is part of complete profile identity, not a performance-only
implementation detail.

## Edge-label compatibility

The shared edge-label names from the common interface remain the
interoperability vocabulary. For V4:

- `base_conductance` must be a stage-labeled view of the scalar edge mobility
  actually used by the selected profile's inherited reference channel;
- exposing such a view must not create a second mobility authority or turn a
  Candidate C derived quantity into retained Candidate A state;
- `flux_coupling` uses the magnitude of the authoritative same-beat current
  $J_C$, not a stale predictor or baseline current; and
- every derived edge label must bind its profile, graph, orientation, stage,
  computation mode, and parameters.

If a selected profile cannot provide a common analytic label on its admitted
domain, it must fail that capability request or expose the family-specified
typed alternative. It must not silently substitute a quantity of another
type.

## Lifecycle and event extension

The inherited public methods remain:

```python
def step(self) -> StepResult: ...
def run(self, num_steps: int) -> list[StepResult]: ...
def reset(self) -> None: ...
def rebase_reset_baseline(self) -> None: ...
```

For V4, `step()` is the exact atomic complete-step transaction defined in the
`GRCV4` specification. All candidate and realization work is provisional
until the complete authoritative state and its postconditions commit together.
Any failure preserves the complete prestate.

`run()` is only repeated application of that transaction. It must not reuse a
cache, solver root, or history value beyond its declared identity or stage.

`reset()` restores the admitted V4 reset state and its compatible graph,
profile, parameters, charge target, retained history, and receipts.
`rebase_reset_baseline()` is the only inherited operation that replaces that
baseline. Neither method may manufacture missing lineage.

Profile migration and topology change are not ordinary `set_state()` calls.
They are typed, ordered transformations of current and reset state followed by
target reconstruction, readmission, and atomic commit. Their receipts must
record source and target identities, charge effects, history disposition,
information loss, and admission outcome.

`GRC9V4` mechanical expansion is such a topology event. Its candidate
detection, expansion, and child-basin completion remain distinct lifecycle
facts.

## Step results, events, and observables

The base `StepResult` and `GRCEvent` shapes remain sufficient, but V4 payloads
must preserve their stronger semantics.

Every successful step result must identify the complete profile and committed
step. Events must bind their graph/profile source and target, atomic commit,
and relevant lifecycle receipt. A rejected transaction may return a typed
failure result or raise a typed exception, but it must not report an event as
committed.

In addition to the common observables, `GRCV4` exposes the profile, candidate,
realization, charge target/current/error, solver disposition, authoritative
current, geometry profile, and lifecycle receipts required by its family
specification. `GRC9V4` adds its port, row, spark, expansion, hierarchy,
coarse-graining, compatibility-branch, and target-version observables.

Derived observables must name their producing stage. Capability and observable
presence establishes implementation support only; it is not scientific
evidence for stability, persistence, preference, or physical attribution.

## Capability discovery

Every `GRCV4` instance must advertise the common V4 capabilities declared in
its family specification and only the candidate and realization capabilities
it actually implements. Every `GRC9V4` instance must additionally advertise
the required nine-port specialization capabilities.

`list_capabilities()` describes executable support for the instance's exact
profile. It must not:

- advertise all ten profiles merely because the implementation supports one;
- infer Candidate A from Candidate C, or the reverse;
- infer one realization from another;
- infer GRC9V3 state, observable, or lifecycle compatibility from transition
  compatibility; or
- present an open, conditional, or planned surface as implemented support.

## Serialization and restoration

The common serialization contract is extended to preserve, directly or by
stable reconstructible identity:

- the complete V4 profile and canonical resolved parameters;
- graph, live order, orientation, boundary, and differential backend;
- context, charge, geometry, solver, domain, units, gauge, and normalization;
- current and reset authoritative coordinates;
- `Q_target` and the active charge profile;
- candidate and persistent-carrier history only where admitted;
- RNG state where applicable;
- ordered migration, event, compatibility, and information-loss receipts; and
- cache provenance sufficient to reject or deterministically rebuild every
  derived surface.

`GRC9V4` snapshots additionally preserve its complete port-graph and
specialization identity. Restoration must readmit the complete target before
state is observable. Canonical serialization still does not imply byte
identity after lawful deterministic reconstruction.

## Error and atomicity extension

The inherited explicit-error requirement includes V4 failures involving:

- unsupported or inconsistent complete identity;
- graph, orientation, differential, pairing, or backend mismatch;
- invalid candidate state or derived-state promotion;
- domain, selector, regularity, solver, conditioning, or finiteness failure;
- nonnegative-resource or charge failure;
- stale or cross-profile cache use;
- missing migration, event, history, loss, or compatibility receipt;
- failed target reconstruction or readmission; and
- incompatible or unreconstructible restoration identity.

For `GRC9V4`, invalid ports, chart, spark, expansion, coarse-graining, or any
independent disabled-reduction surface are additional typed failures.

Every failure occurs before public state changes or rolls back the entire
transaction. Partial resource, nonresource, topology, reset, history, cache,
or receipt writes are nonconforming.

## Interoperability and non-retroactivity

The base interoperability contract remains controlling:

1. `snapshot()` identifies the exact model family.
2. `save()` and `load()` preserve the exact family and V4 profile.
3. `list_capabilities()` reports actual support.
4. V4-specific state remains accessible through its concrete state type.

A consumer written only to the unchanged common interface may use the common
methods and fields. A consumer that needs V4 profile, differential, geometry,
history, lifecycle, or nine-port meaning must detect the corresponding
capability and use the V4 family contract. It must not infer those meanings
from a base-class name or generic field shape.

The addition of these classes does not reinterpret an older snapshot, add V4
capabilities to an older family, or change any older family's class hierarchy,
graph backend, lifecycle, serialization, or error behavior.

## Claim boundary

This extension encodes the interface effects of the accepted V4 common
architecture, lifecycle, Hodge typing, profile-identity, and independently
scoped GRC9V3 compatibility requirements. The complete claim classes and
ceilings remain in the [GRCV4 claim matrix](grc-v4-spec.md#claim-conformance-matrix)
and its [paper source][paper-claims] and [proposal crosswalk][proposal-claims].

Interface conformance does not establish runtime formation, retention,
release, replay, stability, persistence, endpoint behavior, physical
attribution, profile preference, or uniqueness. It does not promote an open or
conditional claim and does not make dependency reach into scientific support.

[paper-claims]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#15-claims-established-by-the-substrate-definition
[proposal-claims]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#15-claims-established-by-the-substrate-definition
