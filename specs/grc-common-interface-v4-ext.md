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
| State | Adds immutable lifecycle-owned payloads and read-only base-field projections without inheriting storage from the mutable base dataclass. |
| Parameters | Makes every trajectory-changing candidate, realization, geometry, differential, charge, solver, and lifecycle choice part of a noncircular canonical profile identity. |
| Graph backend | Requires deterministic vertex and oriented-edge order, typed differential and pairing surfaces, signed reorientation, and reconstruction from serialized identity. |
| Lifecycle | Separates ordinary beats, caller-mapped generic topology events, and canonically constructed GRC9V4 expansion transactions. |
| Capabilities | Adds V4 common, candidate, realization, and nine-port specialization capabilities without treating planned support as implemented support. |
| Observables | Adds profile, charge, current, geometry, solver, lifecycle, and specialization diagnostics while preserving authority labels. |
| Serialization | Preserves exact versioned parameter, profile, model, state, event, commit, and receipt payload identities. |
| Errors | Closes stage, disposition, failure-code, receipt-delta, and atomic rollback schemas. |
| D11-C transport | Requires Candidate C profiles to bind the exact `C-HM-STIFFNESS-BASELINE-v1` stable-edge reference map and separate Hodge/mobility constructors. |
| D11-G9 expansion | Adds explicit chirality, conditional growth phase, canonical event identity, and legacy-defined-domain failure surfaces for GRC9V4 events. |

No inherited common method changes signature. V4 adds typed methods beside
them and defines when an inherited zero-argument method may delegate to the
new surface.

## Concrete class relationships

The common class registry is extended by:

```python
class GRCV4(GRCModel): ...
class GRC9V4(GRCV4): ...
```

The base `GRCState` and `StepResult` dataclasses are compatibility surfaces,
not storage superclasses for V4. Their required fields are exposed by
structural read-only projections:

```python
@runtime_checkable
class GRCStateSurface(Protocol):
    @property
    def step_index(self) -> int: ...
    @property
    def time(self) -> float: ...
    @property
    def budget_target(self) -> float: ...
    @property
    def remainder(self) -> float | None: ...

@runtime_checkable
class StepResultSurface(Protocol):
    step_index: int
    time: float
    events: Sequence[GRCEvent]
    observables: Mapping[str, JSONValue]
```

`GRCV4State` and `GRCV4StepResult` are standalone immutable records satisfying
these protocols. They do not inherit the nonfrozen base dataclasses and do not
carry duplicate base storage. For every currently admitted V4 profile,
`remainder` is the read-only constant `None`; the measured charge residual is
an observable and receipt field, never a repair coordinate.

The GRC9V4 disabled branch is a discriminated exact legacy delegate, not a
V4-shaped subclass with legacy fields projected out. Its union is defined in
the GRC9V4 family specification.

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

Every Candidate C profile additionally binds
`candidate_c_transport_id = "C-HM-STIFFNESS-BASELINE-v1"`, the exact positive
map from stable unoriented live-edge identities to $W_{C,\mathrm{tr}}$, its
content identity, $\eta_C$, and the separate $E_H$ and $E_M$ constructor
identities. This map is profile/reference context: it is not mutable state,
must not be reconstructed from Hodge or geometry arrays, and must be complete
for the target live-edge set before restoration or event readmission.

Defaults must resolve at construction. Environment, observer, device,
telemetry, and storage choices remain outside model parameters unless the
family contract explicitly promotes one into trajectory semantics.

`context_contract_id` identifies the schema, units, and semantic meaning of a
context input. `context_value` is the per-beat value. Its optional
`context_value_digest` identifies the exact admitted value and belongs to a
state or receipt only when the selected profile makes context persistence
trajectory-bearing; it never replaces the contract ID. A serialized
`default_step_request`, when present, is part of resolved parameters, profile
identity, snapshots, and reset identity. It cannot contain a one-shot
topology event because ordinary step requests have no event field.

`from_state()` must validate the complete snapshot before exposing any live
state. It must not silently select another profile, create or discard retained
history, rebase charge, repair topology, or substitute a solver policy.

Resolved parameters use the typed records in
[`grc-v4-contract-schema.json`](grc-v4-contract-schema.json). Identity-bearing
payloads are serialized with RFC 8785 JSON Canonicalization Scheme (JCS) over
I-JSON data: UTF-8, Unicode preserved without normalization, UTF-16 code-unit
property ordering, ECMAScript finite binary64 number serialization, and no
duplicate keys, NaN, infinities, negative zero, or integers outside the I-JSON
safe range. Arrays retain declared order. A snapshot carries each resolved
payload and its typed digest; a bare hash, runtime callable name, environment
lookup, or mutable configuration object is not reconstruction authority.

## Canonical identity and deep immutability

Every derived identity is the lowercase SHA-256 hex digest of the JCS bytes of
the named payload, prefixed exactly as follows:

| Payload | Identifier grammar |
|---|---|
| resolved parameters | `grcv4-params-sha256:<64-hex>` |
| generic complete profile | `grcv4-profile-sha256:<64-hex>` |
| candidate-discriminated target profile template | `grcv4-profile-template-sha256:<64-hex>` |
| GRC9V4 specialization parameters | `grc9v4-params-sha256:<64-hex>` |
| GRC9V4 specialization | `grc9v4-specialization-sha256:<64-hex>` |
| combined GRC9V4 model | `grc9v4-model-sha256:<64-hex>` |
| graph | `grc-graph-sha256:<64-hex>` |
| scientific state | `grcv4-state-sha256:<64-hex>` |
| lifecycle envelope | `grcv4-lifecycle-sha256:<64-hex>` |
| reset baseline | `grcv4-reset-sha256:<64-hex>` |
| topology event | `grc-event-sha256:<64-hex>` |
| committed transaction | `grc-commit-sha256:<64-hex>` |
| lifecycle receipt | `grc-receipt-sha256:<64-hex>` |

Load-bearing referenced content uses the same rule with its own versioned
preimage rather than an unpublished `{"value": ...}` convention:

| Versioned preimage | Identifier grammar |
|---|---|
| `grcv4-authoritative-state-identity-v1` | `grcv4-authoritative-sha256:<64-hex>` |
| `grcv4-wctr-identity-v1` | `grcv4-wctr-sha256:<64-hex>` |
| `grcv4-resource-transform-identity-v1` | `grcv4-resource-transform-sha256:<64-hex>` |
| `grcv4-history-channel-policy-identity-v1` | `grcv4-history-policy-sha256:<64-hex>` |
| `grcv4-history-bundle-identity-v1` or `grc9v4-expansion-history-identity-v1` | `grcv4-history-map-sha256:<64-hex>` |
| `grcv4-history-content-identity-v1` | `grcv4-history-content-sha256:<64-hex>` |
| `grc9v4-expansion-policy-identity-v1` | `grc9v4-expansion-policy-sha256:<64-hex>` |
| `grcv4-k4-identity-v1` | `grcv4-k4-sha256:<64-hex>` |
| `grcv4-reference-hodge-identity-v1` | `grcv4-hodge-sha256:<64-hex>` |

The machine schema defines every field in these wrappers, and the concrete
vector bundle publishes at least one canonical UTF-8 preimage, byte string,
and expected identifier for each family. Reading the creation script is never
required to reproduce a normative digest.

The payload records never contain the identifier derived from themselves.
References to already-derived child identities are allowed and are explicitly
listed in the schema. `params_hash`, `complete_profile_id`, full GRC9V4 model
identity, event ID, state digest, commit ID, and receipt ID are recomputed and
compared on admission; mismatches fail before mutation.

Deep immutability is normative. Constructors defensively copy and freeze every
array, mapping, nested payload, graph record, and receipt before validation.
Public access returns immutable views or defensive copies. Python `dict`,
`list`, and writable array objects may be accepted as configuration input but
must not survive inside admitted scientific state.

## State and authority extension

The base `GRCState` surface remains available. For V4, `budget_target` is a
read-only compatibility property backed by the one serialized `Q_target`
field; two stored copies are forbidden.

Every `GRCV4State` binds one `GRCV4LifecycleState`, which is the single owner
of:

- canonical graph payload and orientation identity;
- one exact `GRCV4Profile` and its canonical parameter identity;
- context identity;
- authoritative resource state $C$;
- only the candidate- and realization-specific nonresource coordinates
  admitted by that profile;
- a reduced reset baseline rather than a second live runtime;
- one `Q_target`; and
- ordered lifecycle, migration, event, and information-loss receipts.

The profile rules determine whether $W_A$ or $Z_4$ is authoritative.
Potential, current, selector, $T_C$, Hodge operators, structural geometry,
solver roots, row summaries, and coarse summaries remain derived or transient
unless a family contract explicitly says otherwise. Caching or serializing a
derived surface does not promote it to authoritative state.

The current deterministic population has no scientific RNG state. Derived
caches live outside scientific state. Snapshot-carried inspection caches are
representation-only, provenance-bound, and excluded from scientific equality.

`get_state()` must return immutable/read-only authority or a deep copy; it may
not expose live mutable arrays, mappings, receipts, graph data, or reset data.
`set_state()` must validate the entire target state atomically and must not
alter the reset baseline, charge target, graph, profile, or history by
implication.

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

## V4 input-bearing operations

The additive public request surface is:

```python
@dataclass(frozen=True)
class GRCV4MigrationPolicy:
    schema_version: Literal["grcv4-migration-policy-v1"]
    policy_id: Literal["typed_bidirectional_profile_migration_v1"]
    resource_policy_id: Literal["identity_resource_transport_v1"]
    target_readmission_policy_id: Literal["full_target_fail_closed_v1"]

@dataclass(frozen=True, slots=True)
class ResolvedHistoryChannelPolicy:
    schema_version: Literal["grcv4-history-channel-policy-v1"]
    subject: Literal["candidate", "carrier"]
    policy_id: str
    disposition: HistoryDisposition
    source_history_digest: str | None
    target_initializer_id: str | None
    information_loss: InformationLossClass

@dataclass(frozen=True, slots=True)
class ResolvedHistoryBundlePolicy:
    schema_version: Literal["grcv4-history-bundle-policy-v1"]
    candidate: ResolvedHistoryChannelPolicy
    carrier: ResolvedHistoryChannelPolicy

@dataclass(frozen=True, slots=True)
class ResolvedExpansionHistoryPolicy:
    schema_version: Literal["grc9v4-expansion-history-policy-v2"]
    candidate: ResolvedHistoryChannelPolicy
    carrier: ResolvedHistoryChannelPolicy
    candidate_history_policy_digest: str
    carrier_history_policy_digest: str

@dataclass(frozen=True, slots=True)
class ResolvedResourceEventTransform:
    schema_version: Literal["grcv4-resource-event-transform-v1"]
    policy_id: str
    source_vertex_ids: tuple[NodeId, ...]
    target_vertex_ids: tuple[NodeId, ...]
    row_major_coefficients: tuple[float, ...]
    target_increment: tuple[float, ...]

@dataclass(frozen=True)
class GRCV4StepRequest:
    schema_version: Literal["grcv4-step-request-v1"]
    operation_id: str
    dt: float
    context_value: FrozenJSONMap
    boundary_input: FrozenJSONMap | None = None
    external_source: FrozenJSONMap | None = None

@dataclass(frozen=True, slots=True)
class GRCV4StepRequestInput:
    schema_version: Literal["grcv4-step-request-input-v1"]
    operation_id: str
    dt: float
    context_value: FrozenJSONMap
    boundary_input: FrozenJSONMap | None = None
    external_source: FrozenJSONMap | None = None

@dataclass(frozen=True)
class GRCV4MigrationRequest:
    schema_version: Literal["grcv4-migration-request-v1"]
    operation_id: str
    source_state_digest: str
    target_profile_id: str
    migration_policy: "GRCV4MigrationPolicy"
    history_policy: "ResolvedHistoryBundlePolicy"
    target_context_value: FrozenJSONMap

@dataclass(frozen=True)
class GRCV4MappedTopologyEventRequest:
    schema_version: Literal["grcv4-mapped-topology-event-request-v1"]
    operation_id: str
    source_state_digest: str
    source_graph_digest: str
    target_graph: SerializedGraphState
    target_profile_id: str
    resource_transform: "ResolvedResourceEventTransform"
    history_policy: "ResolvedHistoryBundlePolicy"
    metadata: FrozenJSONMap

@dataclass(frozen=True)
class GRC9V4ExpansionEventRequest:
    schema_version: Literal["grc9v4-expansion-event-request-v1"]
    operation_id: str
    source_state_digest: str
    source_graph_digest: str
    source_node_id: NodeId
    target_profile_template_id: str
    target_specialization_id: str
    expansion_policy_id: Literal[
        "grc9v4_axis_preserving_chiral_same_port_expansion_v1"
    ]
    target_effective_degree: int
    module_chirality: Literal[-1, 1]
    growth_phase: Literal[1, 2, 3] | None
    resource_distribution: tuple[float, float, float]
    history_policy: "ResolvedExpansionHistoryPolicy"
    expected_event_id: str | None = None
    expected_target_graph_digest: str | None = None

@dataclass(frozen=True, slots=True)
class GRC9V4ExpansionEventRequestInput:
    schema_version: Literal["grc9v4-expansion-event-request-input-v1"]
    operation_id: str
    source_state_digest: str
    source_graph_digest: str
    source_node_id: NodeId
    target_profile_template_id: str
    target_specialization_id: str
    expansion_policy_id: str
    target_effective_degree: int
    module_chirality: Literal[-1, 1] | None
    growth_phase: Literal[1, 2, 3] | None
    resource_distribution: tuple[float, float, float]
    history_policy: "ResolvedExpansionHistoryPolicy"
    expected_event_id: str | None = None
    expected_target_graph_digest: str | None = None

TopologyEventRequest = (
    GRCV4MappedTopologyEventRequest | GRC9V4ExpansionEventRequest
)

def step_v4(self, request: GRCV4StepRequest) -> "GRCV4StepResult": ...
def run_v4(
    self,
    requests: Iterable[GRCV4StepRequest],
) -> list["GRCV4StepResult"]: ...
def migrate_profile(
    self,
    request: GRCV4MigrationRequest,
) -> "GRCV4LifecycleResult": ...
def apply_topology_event(
    self,
    request: TopologyEventRequest,
) -> "GRCV4LifecycleResult": ...
```

`ResolvedResourceEventTransform.row_major_coefficients` is the
target-by-source matrix in the exact listed vertex orders, has length
`len(target_vertex_ids) * len(source_vertex_ids)`, contains only nonnegative
finite binary64 values, and is followed by the finite
`target_increment`, whose length is `len(target_vertex_ids)`. The event applies

$$
C^+=T_{C,\mathrm{evt}}C^-+\Delta C_{\mathrm{event}},
$$

then computes rather than assumes
$\Delta Q=\varpi_+^\top C^+-\varpi_-^\top C^-$ and advances
`Q_target` by exactly that amount. The linear part alone satisfies the declared
source/target charge-form transport rule; the increment may be nonzero.
Duplicate vertex IDs, a dimension mismatch, a nonfinite increment, or failed
charge accounting rejects admission. The mapped graph payload, affine
resource transform, two-channel history policy, and target profile are all
identity-bearing even
when a Python API passes their immutable record objects rather than serialized
JSON.

Wire/test input and admitted operation records are distinct. JSON syntax or a
shape-invalid `*-request-input-v1` payload fails in the decoder or transport
before a V4 operation exists. A shape-valid input containing a scientifically
invalid value, such as negative `dt` or null expansion chirality, reaches
semantic admission and returns a typed `FailureReceipt` without mutation. An
admitted `GRCV4StepRequest` or `GRC9V4ExpansionEventRequest` always satisfies
the stricter internal schema (`dt >= 0`, chirality exactly `-1 | +1`). Harness
fault injection uses the separate
`grcv4-conformance-harness-fault-v1` schema, is unavailable in production,
and is excluded from every scientific and event identity.

The current context value and ordinary boundary/external inputs must enter
through the request. Hidden mutable model fields, private queues, process
globals, telemetry, or environment variables may not supply scientific beat
input. `GRCV4StepRequest` never contains a topology event. A generic mapped
event accepts one caller-supplied target graph as explicit authority. Generic
target-profile IDs and GRC9V4 target references resolve through the same
admitted immutable identity registry to complete digest-matching payloads. A
GRC9V4 expansion accepts no target graph: the model constructs it canonically
from the admitted post-beat source state and the resolved policy. The source
node is explicit. Snapshots and conformance bundles carry referenced payloads,
not only identifier strings. `metadata` is nonauthoritative annotation,
excluded from event and state identity, and may not change construction.
`expected_event_id` and `expected_target_graph_digest` are
optional conformance assertions only; they never become target authority.

Generic mapped events have their own noncircular identity:

```python
@dataclass(frozen=True, slots=True)
class GRCV4MappedTopologyEventIdentityPayload:
    schema_version: Literal["grcv4-mapped-topology-event-identity-v1"]
    source_state_digest: str
    source_graph_digest: str
    target_graph_digest: str
    target_profile_id: str
    resource_transform_digest: str
    history_bundle_digest: str
```

Its event ID is `"grc-event-sha256:" + SHA256(JCS(payload))`. The arbitrary
`operation_id` and nonauthoritative `metadata` are excluded. The exact affine
resource-transform and history-bundle digest preimages remain separately
content-addressed and must be supplied with the request or resolved losslessly
from the admitted immutable registry.

## Lifecycle and event extension

The inherited public methods remain:

```python
def step(self) -> StepResult: ...
def run(self, num_steps: int) -> list[StepResult]: ...
def reset(self) -> None: ...
def rebase_reset_baseline(self) -> None: ...
```

`step_v4()` is the exact atomic complete-step transaction defined in the
`GRCV4` specification. All candidate and realization work is provisional until
the complete authoritative state and its postconditions commit together. Any
failure preserves the complete prestate.

The inherited `step()` may delegate only when construction bound an immutable,
serialized `default_step_request`; otherwise it raises a typed
`MissingV4StepRequest`. Inherited `run(num_steps)` is exactly repeated
zero-argument `step()` under that same fixed default. `run_v4(requests)` is
the input-sequence operation and returns one result per consumed request. No
run method may reuse a cache, solver root, or history value beyond its declared
identity or stage.

`reset()` restores the admitted V4 reset state and its compatible graph,
profile, parameters, charge target, retained history, and receipts.
`rebase_reset_baseline()` is the only inherited operation that replaces that
baseline. Neither method may manufacture missing lineage.

Profile migration and topology change are not ordinary `set_state()` calls.
They execute only through `migrate_profile()` and `apply_topology_event()` as
typed, ordered transformations of current and reset state followed by target
reconstruction, readmission, and atomic commit. Their receipts must record
source and target identities, charge effects, history disposition, information
loss, and admission outcome. A target profile not present in
`list_supported_profiles()` is rejected before provisional mutation.

`GRC9V4` mechanical expansion is such a topology event. The ordinary beat
commits first; fresh candidate detection reads that committed state; a caller
then submits a separate expansion request; expansion succeeds or fails as its
own atomic commit; and only then may ordinary stepping resume. No combined
beat-plus-expansion commit exists. Candidate detection, expansion, and
child-basin completion remain distinct lifecycle facts. The computed
`event_id` must use the
`grc-event-sha256:<64-lowercase-hex-digits>` grammar and bind the source,
source node, desired capacity, module size, chirality, canonical phase, port
and bond policies, exact resource tuple, and candidate/history policies via
the versioned event payload. `growth_phase` is `None` exactly when
$(n_{\mathrm{canonical}}-4)\bmod3=0$; otherwise it is one of `1`, `2`, or
`3`.

## Step results, receipts, and observables

The closed result vocabulary is:

```python
OperationStage = Literal[
    "admission", "pre_read_reconstruction", "candidate_solve",
    "continuity", "charge_admission", "final_reconstruction",
    "history_write", "target_construction", "target_readmission",
    "restoration", "commit",
]
SolverDisposition = Literal[
    "valid_root", "domain_failure", "singular", "conditioning_failure",
    "nonfinite", "no_admitted_root", "multiple_admitted_roots",
]
OperationDisposition = Literal["committed", "rejected"]
HistoryDisposition = Literal[
    "not_applicable", "exact_transport", "target_initializer",
    "whole_carrier_map", "whole_carrier_reset", "explicit_loss", "rederived",
]
InformationLossClass = Literal[
    "none", "candidate_history_loss", "carrier_history_loss",
    "v4_surface_projection", "whole_state_delegate_crossing",
]
FailureCode = Literal[
    "invalid_identity", "invalid_duration", "domain_failure",
    "singular_solver", "conditioning_failure", "nonfinite_value",
    "no_admitted_root", "multiple_admitted_roots", "charge_failure",
    "stale_cache", "unsupported_profile", "invalid_migration",
    "invalid_topology_event", "source_node_not_saturated",
    "source_self_loop_unsupported", "module_chirality_required",
    "module_growth_phase_required",
    "reject_noncanonical_inactive_growth_phase", "target_readmission_failure",
    "legacy_expansion_target_undefined", "restoration_failure",
]

@dataclass(frozen=True, slots=True)
class ReceiptCore:
    operation_id: str
    source_state_digest: str
    target_state_digest: str
    source_graph_digest: str
    target_graph_digest: str
    source_model_identity: str
    target_model_identity: str
    source_authoritative_digest: str
    target_authoritative_digest: str
    source_reset_digest: str
    target_reset_digest: str
    resource_transform_digest: str
    history_bundle_digest: str
    actual_charge_delta: float
    information_losses: tuple[InformationLossClass, ...]
    disposition: Literal["committed"]
    parent_receipt_ids: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class HistoryChannelReceipt:
    subject: Literal["candidate", "carrier"]
    disposition: HistoryDisposition
    source_history_digest: str | None
    target_history_digest: str | None
    information_loss: InformationLossClass

@dataclass(frozen=True, slots=True)
class HistoryBundleReceipt:
    schema_version: Literal["grcv4-history-bundle-receipt-v1"]
    candidate: HistoryChannelReceipt
    carrier: HistoryChannelReceipt

@dataclass(frozen=True, slots=True)
class StepCommitReceipt:
    schema_version: Literal["grcv4-step-commit-receipt-v1"]
    core: ReceiptCore

@dataclass(frozen=True, slots=True)
class ResetReceipt:
    schema_version: Literal["grcv4-reset-receipt-v1"]
    core: ReceiptCore
    reset_baseline_digest: str

@dataclass(frozen=True, slots=True)
class RebaseReceipt:
    schema_version: Literal["grcv4-rebase-receipt-v1"]
    core: ReceiptCore
    old_reset_digest: str
    new_reset_digest: str

@dataclass(frozen=True, slots=True)
class ProfileMigrationReceipt:
    schema_version: Literal["grcv4-profile-migration-receipt-v1"]
    core: ReceiptCore
    history: HistoryBundleReceipt

@dataclass(frozen=True, slots=True)
class TopologyEventReceipt:
    schema_version: Literal["grcv4-topology-event-receipt-v1"]
    core: ReceiptCore
    event_id: str
    history: HistoryBundleReceipt

@dataclass(frozen=True, slots=True)
class ChargeReceipt:
    schema_version: Literal["grcv4-charge-receipt-v1"]
    core: ReceiptCore
    target_charge: float
    admitted_charge: float
    residual: float

@dataclass(frozen=True, slots=True)
class HistoryDispositionReceipt:
    schema_version: Literal["grcv4-history-disposition-receipt-v1"]
    core: ReceiptCore
    subject: Literal["candidate", "carrier"]
    history_disposition: HistoryDisposition
    information_loss: InformationLossClass

@dataclass(frozen=True, slots=True)
class LegacyCompatibilityReceipt:
    schema_version: Literal["grc9v4-legacy-compatibility-receipt-v1"]
    core: ReceiptCore
    target_spec_version: str
    compatibility_surfaces: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class FailureReceiptIdentityPayload:
    schema_version: Literal["grcv4-failure-receipt-v1"]
    operation_id: str
    stage: OperationStage
    code: FailureCode
    source_state_digest: str
    observed_poststate_digest: str

@dataclass(frozen=True, slots=True)
class FailureReceipt:
    schema_version: Literal["grcv4-failure-receipt-envelope-v1"]
    receipt_id: str
    identity_payload: FailureReceiptIdentityPayload

LifecycleReceipt = (
    StepCommitReceipt | ResetReceipt | RebaseReceipt |
    ProfileMigrationReceipt | TopologyEventReceipt | ChargeReceipt |
    HistoryDispositionReceipt | LegacyCompatibilityReceipt
)

@dataclass(frozen=True, slots=True)
class SuccessfulReceiptEnvelope:
    schema_version: Literal["grcv4-successful-receipt-envelope-v1"]
    receipt_id: str
    commit_id: str
    identity_payload: LifecycleReceipt

@dataclass(frozen=True, slots=True)
class GRCV4Failure:
    stage: OperationStage
    solver_disposition: SolverDisposition | None
    code: FailureCode
    message: str
    prestate_digest: str
    poststate_digest: str
    pre_lifecycle_digest: str
    post_lifecycle_digest: str
    failure_receipt: FailureReceipt

@dataclass(frozen=True, slots=True)
class GRCV4StepResult:
    schema_version: Literal["grcv4-step-result-v1"]
    step_index: int
    time: float
    events: tuple[GRCEvent, ...]
    observables: FrozenJSONMap
    active_profile_id: str
    active_model_identity: str
    operation_disposition: OperationDisposition
    solver_disposition: SolverDisposition | None
    committed: bool
    commit_id: str | None
    failure: GRCV4Failure | None
    emitted_receipts: tuple[SuccessfulReceiptEnvelope | FailureReceipt, ...]

@dataclass(frozen=True, slots=True)
class GRCV4LifecycleResult:
    operation_disposition: OperationDisposition
    committed: bool
    commit_id: str | None
    failure: GRCV4Failure | None
    emitted_receipts: tuple[SuccessfulReceiptEnvelope | FailureReceipt, ...]
```

The operation/solver split is normative:

```text
committed is true
  iff operation_disposition is committed
  and failure is None
  and commit_id is present

failure before candidate solve
  -> operation_disposition = rejected
  -> solver_disposition = None

failure after a valid solve, including charge rejection
  -> operation_disposition = rejected
  -> solver_disposition = valid_root
```

No admission, lifecycle, or receipt failure invents a solver disposition.
`ReceiptCore.information_losses` is a canonical-order tuple with no duplicate.
Its sole order is
`candidate_history_loss`, `carrier_history_loss`, `v4_surface_projection`,
then `whole_state_delegate_crossing`, with absent classes omitted without
changing the relative order. No loss is the empty tuple, never a synthetic
`"none"` loss. The machine `information_loss_tuple` schema enumerates every
admitted ordered subset, and the concrete receipt-identity vector includes
both Candidate and carrier losses so that the ordering affects a checked
receipt ID. Candidate and carrier outcomes are independently mandatory in
every migration/topology
history bundle. A missing channel is represented by that channel's explicit
`not_applicable` disposition and null source/target history digests.

Each `LifecycleReceipt` above is the versioned **receipt identity payload**:
its `schema_version`, `core`, and type-specific fields contain neither
`receipt_id` nor `commit_id`. Its `receipt_id` is the digest of that payload.
A commit payload then binds the operation ID, source and target state
digests, ordered emitted receipt IDs, and committed step/time; it never
contains `commit_id`. Finally, `SuccessfulReceiptEnvelope` carries the identity
payload, its computed ID, and the computed commit ID. Admission verifies both
directions: the commit names the receipt ID and the envelope names that commit.
This three-step order is normative and removes a receipt/commit hash cycle.
`FailureReceipt.identity_payload` is hashed without the enclosing
`receipt_id`. It is returned as operation evidence but is never appended to
the persistent scientific receipt ledger.

Domain, solver, charge, migration, event, readmission, and compatibility
failures return a noncommitted typed result. Programmer errors involving an
invalid Python type or malformed object construction raise. A returned
failure must have equal pre/post scientific-state digests. An exception raised
after admission begins must provide the same atomicity guarantee.

Every successful step result must identify the complete model and committed
step. `events` and `emitted_receipts` contain only the delta from the attempted
operation. The complete ordered persistent receipt ledger lives in lifecycle
state. A telemetry log is nonauthoritative. Events must bind
their graph/profile source and target, atomic commit, and relevant lifecycle
receipt. A rejected transaction must not report an event as committed or
append a persistent commit receipt.

In addition to the common observables, `GRCV4` exposes the profile, candidate,
realization, charge target/current/error, solver disposition, authoritative
current, geometry profile, and lifecycle receipts required by its family
specification. `GRC9V4` adds its port, row, spark, expansion, hierarchy,
coarse-graining, compatibility-branch, and target-version observables.

Derived observables must name their producing stage. Capability and observable
presence establishes implementation support only; it is not scientific
evidence for stability, persistence, preference, or physical attribution.

## Capability and profile discovery

Every `GRCV4` instance must advertise the common V4 capabilities declared in
its family specification and only the candidate and realization capabilities
it actually implements. Every `GRC9V4` instance must additionally advertise
the required nine-port specialization capabilities.

```python
@property
def active_profile_id(self) -> str: ...

@property
def active_model_identity(self) -> str: ...

def list_supported_profiles(self) -> frozenset[str]: ...

def get_supported_profile(
    self,
    complete_profile_id: str,
) -> "GRCV4Profile": ...

def list_supported_model_identities(self) -> frozenset[str]: ...
```

`active_profile_id` is the exact complete-profile digest bound to the live
instance. For graph-generic `GRCV4`, `active_model_identity` equals
`active_profile_id`. For `GRC9V4`, it is the combined generic-profile plus
specialization identity; the generic profile ID remains separately visible.
`list_supported_profiles()` and `get_supported_profile()` form the lossless
generic profile registry that the implementation can construct and migrate
to. GRC9V4 additionally exposes the exact supported combined identities
through `list_supported_model_identities()`; no generic ID may stand in for a
specialization identity.
Candidate and realization capability flags are only marginals; they must not
be used to infer unlisted cross-products. For example, support for `A_CI` and
`C_OS` does not imply `A_OS` or `C_CI`.

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
- ordered migration, event, compatibility, and information-loss receipts; and
- cache provenance sufficient to reject or deterministically rebuild every
  derived surface.

The scientific-state digest is computed from the versioned authoritative
state payload only: complete model identity, canonical graph payload or its
single owning representation, orientation, clock, authoritative coordinates,
reset-baseline digest, charge target, context identity when trajectory-bearing,
and no receipt fields. It excludes the digest itself, derived caches,
observables, telemetry, solver workspaces, and object-layout details. The
separate lifecycle-envelope digest binds that scientific-state digest plus the
ordered persistent receipt IDs. Receipts bind source/target scientific-state
digests; commits bind those digests plus emitted receipt IDs; the lifecycle
envelope is computed last. This acyclic order prevents state/receipt hash
recursion. The reset digest likewise excludes itself and live clock/receipt
state. Exact payload definitions are in the contract schema and canonical
cross-language vectors.

Candidate C snapshots and target profiles preserve the exact identity and
content of $W_{C,\mathrm{tr}}$ without promoting it into ordinary-beat state.
GRC9V4 expansion receipts additionally preserve chirality, canonical growth
phase, stable role IDs, the complete port plan, fixed bond seed, resource and
history disposition, and target-readmission outcome.

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
independent disabled-reduction surface are additional typed failures. The
expansion admission surface includes `module_chirality_required`,
`module_growth_phase_required`,
`reject_noncanonical_inactive_growth_phase`, and stable-role collision
failures. A disabled legacy expansion for which unchanged authority has no
unique target returns `legacy_expansion_target_undefined`.

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
architecture, lifecycle, Hodge typing, profile-identity, D11-C transport,
D11-G9 expansion, and independently scoped GRC9V3 compatibility requirements.
The complete claim classes and
ceilings remain in the [GRCV4 claim matrix](grc-v4-spec.md#claim-conformance-matrix)
and its [paper source][paper-claims] and [proposal crosswalk][proposal-claims].

Interface conformance does not establish runtime formation, retention,
release, replay, stability, persistence, endpoint behavior, physical
attribution, profile preference, or uniqueness. It does not promote an open or
conditional claim and does not make dependency reach into scientific support.

[paper-claims]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#15-claims-established-by-the-substrate-definition
[proposal-claims]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#15-claims-established-by-the-substrate-definition
