"""Fresh mechanical detection and bounded native C_OS/C_PC/A_OS/C_CI event transactions.

The event checkpoint/replay owner is internal integration, not the later full
GRC9V4 facade, compatibility crossing, completion rule or capability claim.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from threading import Lock
from typing import Any, ClassVar, Literal, Self, cast

from .grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4AOSExpansion,
    GRC9V4CCIExpansion,
    GRC9V4COSExpansion,
    GRC9V4CPCExpansion,
    GRC9V4ExpansionError,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
    _GRC9V4CExpansion,
    aos_history_policy,
    candidate_content_payload,
    carrier_content_payload,
    cpc_history_policy,
)
from .grc_9_v4_topology import (
    PORT_COUNT,
    GRC9V4CandidateADifferentialReference,
    GRC9V4PostbeatRows,
    GRC9V4RowDifferential,
    GRC9V4RowSummary,
    _coordinate,
)
from .grc_v4_candidate_a import candidate_a_writer_target
from .grc_v4_candidate_c import CandidateCCurrent
from .grc_v4_ci import ProvisionalCandidateCIStep
from .grc_v4_codec import (
    canonical_json_bytes,
    decode_canonical_json,
    payload_identity,
    validate_payload,
)
from .grc_v4_exact import current_exact_backend, exact_backend, exact_number
from .grc_v4_geometry import (
    GeometryStageInputs,
    NodeId,
    PhysicalFlux,
    VertexScalar,
    _identity,
    _local_payload,
    _ordered,
)
from .grc_v4_pc import CandidatePCRead, ProvisionalCandidatePCStep, carrier_geometry
from .grc_v4_profile import CandidateAParams, _Record
from .grc_v4_realizations import CandidateAOSPass, CandidateCOSPass
from .grc_v4_state import FrozenJSONMap, GRCV4LifecycleResult, _number
from .grc_v4_step import (
    FailureCode,
    FailureReceipt,
    FailureReceiptIdentityPayload,
    GRCV4Failure,
    OperationStage,
    ProvisionalCandidateAOSStep,
    ProvisionalCandidateCOSStep,
    SuccessfulReceiptEnvelope,
    make_commit_receipts,
)
from .grc_v4_transport import ChargeEvaluation


@dataclass(frozen=True, slots=True, eq=False)
class GRC9SparkPolicy(_Record):
    """Closed specification policy; schema recognition is not lane support.

    Child stabilization is detached policy content only. Its presence neither
    runs a completion rule nor enables a completed-spark capability.
    """

    SCHEMA: ClassVar[str] = "spark_policy"
    schema_version: Literal["grc9v4-spark-policy-v1"]
    lane: Literal["current_hybrid_signed_hessian", "grc9v3_column_h_assisted"]
    gradient_tolerance: float
    basin_hessian_tolerance: float
    spark_hessian_tolerance: float
    child_stabilization: Mapping[str, object] | None

    def __post_init__(self) -> None:
        _Record.__post_init__(self)
        for name in (
            "gradient_tolerance",
            "basin_hessian_tolerance",
            "spark_hessian_tolerance",
        ):
            object.__setattr__(self, name, _number(getattr(self, name)))


class UnsupportedGRC9SparkLane(ValueError):
    """A declared optional lane has no admitted executable policy here."""


def _baseline_policy(value: GRC9SparkPolicy) -> GRC9SparkPolicy:
    if type(value) is not GRC9SparkPolicy:
        raise TypeError("candidate detection requires GRC9SparkPolicy")
    policy = GRC9SparkPolicy.from_payload(value.to_payload())
    if policy.lane != "current_hybrid_signed_hessian":
        raise UnsupportedGRC9SparkLane(
            "grc9v3_column_h_assisted requires separately bound executable controls"
        )
    return policy


@dataclass(frozen=True, slots=True)
class GRC9V4CandidateAssessment:
    """Immutable derived node diagnostics, not an event or admission token.

    Local construction validates values but cannot establish graph provenance.
    Detection constructs these from the admitted port owner and fresh rows;
    it never consumes externally supplied assessments as candidate evidence.
    """

    row: GRC9V4RowSummary
    occupied_ports: tuple[int, ...]
    policy: GRC9SparkPolicy

    def __post_init__(self) -> None:
        if type(self.row) is not GRC9V4RowSummary:
            raise TypeError("assessment requires a fixed-row summary")
        object.__setattr__(self, "row", replace(self.row))
        ports = tuple(
            _coordinate(p, PORT_COUNT, "port") for p in _ordered(self.occupied_ports)
        )
        if len(set(ports)) != len(ports):
            raise ValueError("duplicate occupied port")
        object.__setattr__(self, "occupied_ports", tuple(sorted(ports)))
        object.__setattr__(self, "policy", _baseline_policy(self.policy))

    @property
    def node_id(self) -> NodeId:
        return self.row.node_id

    @property
    def saturated(self) -> bool:
        return len(self.occupied_ports) == PORT_COUNT

    @property
    def small_gradient(self) -> bool:
        # Compare the norm without rounding a square root, overflowing a square,
        # or underflowing a subnormal. These are the fresh .b row coordinates,
        # not a newly chosen unrounded differential backend.
        squared = sum((exact_number(x) ** 2 for x in self.row.gradient), exact_number())
        return bool(squared < exact_number(self.policy.gradient_tolerance) ** 2)

    @property
    def minimum_signed_hessian(self) -> float:
        value = min(self.row.hessian_sign * x for x in self.row.gradient)
        return 0.0 if value == 0 else value

    @property
    def hessian_degenerate(self) -> bool:
        return self.minimum_signed_hessian < self.policy.spark_hessian_tolerance

    @property
    def basin_seed(self) -> bool:
        return self.small_gradient and (
            self.minimum_signed_hessian > self.policy.basin_hessian_tolerance
        )

    @property
    def is_candidate(self) -> bool:
        return self.saturated and self.small_gradient and self.hessian_degenerate


@dataclass(frozen=True, slots=True)
class GRC9V4CandidateDetection:
    """Baseline detection from detached fresh-postbeat numerical inputs.

    Native lifecycle wiring must supply the actual committed state and current,
    fixing sign and policy through the combined specialization identity. Like
    the row input record, this boundary validates declared content and stage,
    not the caller's chronology. Every assessment recomputes the row backend;
    no supplied summary, cache, previous verdict or candidate list is accepted.
    """

    postbeat: GRC9V4PostbeatRows
    policy: GRC9SparkPolicy

    def __post_init__(self) -> None:
        if type(self.postbeat) is not GRC9V4PostbeatRows:
            raise TypeError("candidate detection requires GRC9V4PostbeatRows")
        object.__setattr__(self, "postbeat", replace(self.postbeat))
        object.__setattr__(self, "policy", _baseline_policy(self.policy))

    @property
    def identity(self) -> str:
        """Input binding for these candidate diagnostics, not scientific state."""
        return _identity(
            "grc9v4-candidate-detection-sha256",
            {
                "descriptor_version": "grc9v4-baseline-candidate-detection-v1",
                "row_inputs_identity": self.postbeat.identity,
                "spark_policy": self.policy.to_payload(),
            },
        )

    def assess(self) -> tuple[GRC9V4CandidateAssessment, ...]:
        graph = self.postbeat.port_graph
        ports: dict[NodeId, list[int]] = {node: [] for node in graph.live_node_ids}
        for edge in graph.edges:
            ports[edge.tail.node_id].append(edge.tail.port)
            ports[edge.head.node_id].append(edge.head.port)
        return tuple(
            GRC9V4CandidateAssessment(row, tuple(ports[row.node_id]), self.policy)
            for row in self.postbeat.evaluate()
        )

    def candidate_node_ids(self) -> tuple[NodeId, ...]:
        return tuple(row.node_id for row in self.assess() if row.is_candidate)


@dataclass(frozen=True, slots=True)
class GRC9V4Specialization:
    """Resolved immutable declaration, not an advertised runtime capability."""

    resolved: FrozenJSONMap
    identity_payload: FrozenJSONMap

    def __post_init__(self) -> None:
        resolved = validate_payload("resolved_specialization", self.resolved)
        identity = validate_payload(
            "specialization_identity_payload", self.identity_payload
        )
        payload_identity(
            "resolved_specialization",
            resolved,
            expected=cast(str, identity["specialization_params_hash"]),
        )
        params: Any = resolved
        for key, value in (
            ("spark_lane", params["spark"]["lane"]),
            ("expansion_policy_id", params["expansion"]["policy_id"]),
            ("row_weight_policy_id", params["row_weight"]["schema_version"]),
            ("coarse_policy_id", params["coarse_graining"]["schema_version"]),
            (
                "grc9v3_target_spec_version",
                params["compatibility"]["target_spec_version"],
            ),
        ):
            if identity[key] != value:
                raise ValueError("specialization identity differs from resolved policy")
        object.__setattr__(self, "resolved", FrozenJSONMap(resolved))
        object.__setattr__(self, "identity_payload", FrozenJSONMap(identity))

    @property
    def specialization_id(self) -> str:
        return payload_identity(
            "specialization_identity_payload", self.identity_payload
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "resolved": self.resolved.to_dict(),
            "identity_payload": self.identity_payload.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class _GRC9V4EventState:
    """Native identity over port-owned numerical inputs; admission is separate.

    GeometryStageInputs identities remain internal kernel diagnostics. Enabled
    scientific/reset identities below always bind the combined model identity.
    No caller-supplied cache or target graph becomes scientific authority.
    """

    inputs: GeometryStageInputs
    specialization: GRC9V4Specialization
    FAMILY: ClassVar[Literal["C_OS", "C_PC", "A_OS", "C_CI"]]

    def __post_init__(self) -> None:
        if (
            type(self.inputs) is not GeometryStageInputs
            or type(self.specialization) is not GRC9V4Specialization
        ):
            raise TypeError(
                "native event state requires typed inputs and specialization"
            )
        inputs, spec = replace(self.inputs), replace(self.specialization)
        reference = inputs.geometry.reference
        if (
            reference.graph.port_graph is None
            or reference.profile.identity_payload.profile_family_id != self.FAMILY
        ):
            raise ValueError(
                f"native {self.FAMILY} requires a port-owned {self.FAMILY} reference"
            )
        geometry = (
            reference.geometry()
            if self.FAMILY in {"C_OS", "A_OS", "C_CI"}
            else carrier_geometry(inputs, inputs.current)
        )
        if (
            inputs.geometry != geometry
            or inputs.stage != "pre_read"
            or inputs.trial_current is not None
        ):
            raise ValueError("native state must restart from its realization geometry")
        if inputs.receipt_ids:
            raise ValueError("kernel diagnostic receipts are not a native event ledger")
        if any(x != 0 for row in reference.K4_base for x in row):
            raise ValueError("bounded event scope requires zero structural K4 base")
        if self.FAMILY == "A_OS":
            backend = GRC9V4CandidateADifferentialReference(reference.graph.port_graph)
            candidate = reference.profile.params_resolved.candidate
            if (
                type(candidate) is not CandidateAParams
                or candidate.descriptor_backend_id != backend.identity
            ):
                raise ValueError("native A_OS requires its bound fixed-row descriptor")
        _baseline_policy(GRC9SparkPolicy.from_payload(spec.resolved["spark"]))
        object.__setattr__(self, "inputs", inputs)
        object.__setattr__(self, "specialization", spec)

    @property
    def model_identity(self) -> str:
        return payload_identity(
            "complete_model_identity_payload",
            {
                "schema_version": "grc9v4-complete-identity-v1",
                "grcv4_complete_profile_id": self.inputs.geometry.reference.profile.complete_profile_id,
                "specialization_id": self.specialization.specialization_id,
            },
        )

    @property
    def reset_payload(self) -> dict[str, Any]:
        return {
            **self.inputs.reset_preimage,
            "schema_version": "grc9v4-reset-baseline-v1",
            "active_model_identity": self.model_identity,
        }

    @property
    def reset_digest(self) -> str:
        return payload_identity("grc9v4_reset_payload", self.reset_payload)

    @property
    def scientific_payload(self) -> dict[str, Any]:
        return {
            **self.inputs.scientific_state_preimage,
            "active_model_identity": self.model_identity,
            "reset_digest": self.reset_digest,
        }

    @property
    def scientific_digest(self) -> str:
        return payload_identity("scientific_state_payload", self.scientific_payload)

    def lifecycle_digest(self, receipts: tuple[SuccessfulReceiptEnvelope, ...]) -> str:
        return payload_identity(
            "lifecycle_envelope_payload",
            {
                "schema_version": "grcv4-lifecycle-envelope-v1",
                "scientific_state_digest": self.scientific_digest,
                "receipt_ids": [r.receipt_id for r in receipts],
            },
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "inputs": self.inputs.to_payload(),
            "specialization": self.specialization.to_payload(),
            "scientific_digest": self.scientific_digest,
            "reset_digest": self.reset_digest,
            "model_identity": self.model_identity,
        }


@dataclass(frozen=True, slots=True)
class GRC9V4COSState(_GRC9V4EventState):
    """Native OS state with no independent carrier authority."""

    FAMILY: ClassVar[Literal["C_OS", "C_PC", "A_OS", "C_CI"]] = "C_OS"


@dataclass(frozen=True, slots=True)
class GRC9V4CPCState(_GRC9V4EventState):
    """Native PC state; geometry must derive from current's own committed Z."""

    FAMILY: ClassVar[Literal["C_OS", "C_PC", "A_OS", "C_CI"]] = "C_PC"


@dataclass(frozen=True, slots=True)
class GRC9V4AOSState(_GRC9V4EventState):
    """A_OS port owner with distinct current/reset retained W and no carrier."""

    FAMILY: ClassVar[Literal["C_OS", "C_PC", "A_OS", "C_CI"]] = "A_OS"

    @property
    def differential_reference(self) -> GRC9V4CandidateADifferentialReference:
        graph = self.inputs.geometry.reference.graph.port_graph
        assert graph is not None
        return GRC9V4CandidateADifferentialReference(graph)


@dataclass(frozen=True, slots=True)
class GRC9V4CCIState(_GRC9V4EventState):
    """C_CI authority; geometry restarts from reference, never a previous root."""

    FAMILY: ClassVar[Literal["C_OS", "C_PC", "A_OS", "C_CI"]] = "C_CI"


def _cci_readmit(state: GRC9V4CCIState) -> tuple[PhysicalFlux, PhysicalFlux]:
    """Rebuild both certified joint roots without continuity or history writes."""
    probe = ProvisionalCandidateCIStep(replace(state.inputs, dt=0))
    reference = state.inputs.geometry.reference
    graph = reference.graph.port_graph
    assert graph is not None
    rows = GRC9V4RowDifferential(
        graph, cast(int, state.specialization.identity_payload["hessian_sign"])
    )
    weights = tuple(
        cast(float, reference.edge_weights[e]) for e in reference.graph.live_edge_ids
    )
    for authority, root in (
        (state.inputs.current, probe.root),
        (state.inputs.reset, probe.reset_root),
    ):
        rows.evaluate(authority.C, weights, root.current.values)
    return probe.root.current, probe.reset_root.current


def _aos_readmit(state: GRC9V4AOSState) -> tuple[PhysicalFlux, PhysicalFlux]:
    """Full OS read/split on both roles; never run continuity or a W writer.

    The zero step supplies common charge checks only. A positive local duration
    opens each read-only OS pass; no resulting hypothetical update is published.
    """
    backend = state.differential_reference
    ProvisionalCandidateAOSStep(replace(state.inputs, dt=0), backend)
    graph = backend.port_graph
    rows = GRC9V4RowDifferential(
        graph, cast(int, state.specialization.identity_payload["hessian_sign"])
    )
    reads = []
    for authority in (state.inputs.current, state.inputs.reset):
        surface = CandidateAOSPass(
            replace(state.inputs, current=authority, dt=1), backend
        )
        assert authority.W_A is not None
        rows.evaluate(authority.C, authority.W_A, surface.corrector.current.values)
        candidate_a_writer_target(
            surface.corrector, VertexScalar(backend.graph, authority.C)
        )
        reads.append(surface.corrector.current)
    return reads[0], reads[1]


def _event_readmit(
    state: _GRC9V4EventState,
) -> tuple[PhysicalFlux, PhysicalFlux] | None:
    if type(state) is GRC9V4AOSState:
        return _aos_readmit(state)
    if type(state) is GRC9V4CCIState:
        return _cci_readmit(state)
    _c_readmit(state)
    return None


def _cos_readmit(state: GRC9V4COSState) -> None:
    """Read both complete OS surfaces, without advancing either resource role.

    A zero step checks charge/reference current but deliberately bypasses OS
    geometry/corrector/split admission. Paper 12.7.5 requires those additional
    surfaces at an event. CandidateCOSPass has a positive-duration API gate;
    its read equations do not consume duration or advance resource/clock.
    The local dt=1 probe only opens that read path and is never published.
    """
    ProvisionalCandidateCOSStep(replace(state.inputs, dt=0))
    reference = state.inputs.geometry.reference
    graph = reference.graph.port_graph
    assert graph is not None
    rows = GRC9V4RowDifferential(
        graph, cast(int, state.specialization.identity_payload["hessian_sign"])
    )
    weights = tuple(
        cast(float, reference.edge_weights[e]) for e in reference.graph.live_edge_ids
    )
    for authority in (state.inputs.current, state.inputs.reset):
        surface = CandidateCOSPass(replace(state.inputs, current=authority, dt=1))
        # Target analysis is reconstructed, not copied from source caches or
        # advertised as a new postbeat candidate/completed-spark observation.
        rows.evaluate(authority.C, weights, surface.corrector.current.values)


def _cpc_readmit(state: GRC9V4CPCState) -> None:
    """PC's zero step admits both whole-chart envelopes and old-Z reads.

    Unlike OS's zero step, this kernel performs the full PC read. It runs no
    carrier writer and supplies independent current/reset reconstructed points.
    """
    probe = ProvisionalCandidatePCStep(replace(state.inputs, dt=0))
    reference = state.inputs.geometry.reference
    graph = reference.graph.port_graph
    assert graph is not None
    rows = GRC9V4RowDifferential(
        graph, cast(int, state.specialization.identity_payload["hessian_sign"])
    )
    weights = tuple(
        cast(float, reference.edge_weights[e]) for e in reference.graph.live_edge_ids
    )
    for authority, read in (
        (state.inputs.current, probe.read),
        (state.inputs.reset, probe.reset_read),
    ):
        rows.evaluate(authority.C, weights, read.point.current.values)


def _c_readmit(state: _GRC9V4EventState) -> None:
    if type(state) is GRC9V4COSState:
        _cos_readmit(state)
    elif type(state) is GRC9V4CPCState:
        _cpc_readmit(state)
    else:
        raise TypeError("expected a closed native C state")


def _event_receipts(
    before: _GRC9V4EventState,
    after: _GRC9V4EventState,
    target: _GRC9V4CExpansion | GRC9V4AOSExpansion,
    ledger: tuple[SuccessfulReceiptEnvelope, ...],
) -> list[dict[str, Any]]:
    history: dict[str, Any] = dict(
        schema_version="grcv4-history-bundle-receipt-v1",
        **{
            subject: {
                "subject": subject,
                "disposition": disposition,
                "source_history_digest": None,
                "target_history_digest": None,
                "information_loss": "none",
            }
            for subject, disposition in (
                ("candidate", "rederived"),
                ("carrier", "not_applicable"),
            )
        },
    )
    if type(target) is GRC9V4AOSExpansion:
        history["candidate"].update(
            disposition="exact_transport",
            source_history_digest=payload_identity(
                "history_content_identity_payload",
                candidate_content_payload(before.inputs.current, before.inputs.reset),
            ),
            target_history_digest=payload_identity(
                "history_content_identity_payload",
                candidate_content_payload(after.inputs.current, after.inputs.reset),
            ),
        )
    if type(target) is GRC9V4CPCExpansion:
        history["carrier"].update(
            disposition="whole_carrier_reset",
            source_history_digest=payload_identity(
                "history_content_identity_payload",
                carrier_content_payload(before.inputs.current, before.inputs.reset),
            ),
            target_history_digest=payload_identity(
                "history_content_identity_payload",
                carrier_content_payload(after.inputs.current, after.inputs.reset),
            ),
            information_loss="carrier_history_loss",
        )
    charges = [
        ChargeEvaluation(
            VertexScalar(s.inputs.geometry.reference.graph, s.inputs.current.C),
            s.inputs.Q_target,
            s.inputs.geometry.reference.profile,
        )
        for s in (before, after)
    ]
    core: dict[str, Any] = {
        "operation_id": target.plan.request.operation_id,
        "resource_transform_digest": payload_identity(
            "resource_transform_identity_payload",
            {
                "schema_version": "grcv4-resource-transform-identity-v1",
                "transform": target.resource_transform_payload(),
            },
        ),
        "history_bundle_digest": payload_identity(
            "expansion_history_identity_payload",
            {
                "schema_version": "grc9v4-expansion-history-identity-v1",
                "history_policy": target.plan.request.history_policy,
            },
        ),
        "actual_charge_delta": float(
            exact_number(charges[1].actual) - exact_number(charges[0].actual)
        ),
        "information_losses": ["carrier_history_loss"]
        if type(target) is GRC9V4CPCExpansion
        else [],
        "disposition": "committed",
        "parent_receipt_ids": []
        if not ledger
        else [
            next(r.receipt_id for r in ledger if r.commit_id == ledger[-1].commit_id)
        ],
    }
    for prefix, state in (("source", before), ("target", after)):
        core.update(
            {
                prefix + "_state_digest": state.scientific_digest,
                prefix
                + "_graph_digest": state.inputs.geometry.reference.graph.graph_digest,
                prefix + "_model_identity": state.model_identity,
                prefix + "_reset_digest": state.reset_digest,
                prefix + "_authoritative_digest": payload_identity(
                    "authoritative_state_identity_payload",
                    {
                        "schema_version": "grcv4-authoritative-state-identity-v1",
                        "authoritative": state.scientific_payload["authoritative"],
                    },
                ),
            }
        )
    return [
        {
            "schema_version": "grcv4-topology-event-receipt-v1",
            "core": core,
            "history": history,
            "event_id": target.plan.event_id,
        },
        dict(
            schema_version="grcv4-charge-receipt-v1",
            core=core,
            **charges[1].receipt_values(),
        ),
        *(
            {
                "schema_version": "grcv4-history-disposition-receipt-v1",
                "core": core,
                "subject": subject,
                "history_disposition": history[subject]["disposition"],
                "information_loss": history[subject]["information_loss"],
            }
            for subject in ("candidate", "carrier")
        ),
    ]


@dataclass(frozen=True, slots=True)
class _EventPublication:
    state: _GRC9V4EventState
    receipts: tuple[SuccessfulReceiptEnvelope, ...] = ()
    requests: tuple[GRC9V4ExpansionRequestInput, ...] = ()
    archives: tuple[FrozenJSONMap, ...] = ()
    reference_currents: tuple[FrozenJSONMap, ...] = ()


class _GRC9V4EventOperation:
    """Shared atomic receiver; siblings retain closed candidate/realization types.

    The seed is numerical state, not proof of earlier operation chronology.
    Checkpoints replay every event from that admitted seed and verify the full
    resulting payload/ledger. This is deliberately an internal event checkpoint,
    not the later public model snapshot/load/reset/step/capability facade.
    The owner captures ExactScalar backend selection at construction.
    """

    STATE: ClassVar[type[_GRC9V4EventState]]
    CHECKPOINT: ClassVar[str]

    def __init__(self, state: _GRC9V4EventState) -> None:
        if type(state) is not self.STATE:
            raise TypeError("expected native " + self.STATE.FAMILY + " state")
        self._backend = current_exact_backend()
        with exact_backend(self._backend):
            state = self.STATE(
                GeometryStageInputs.from_payload(state.inputs.to_payload()),
                replace(state.specialization),
            )
            _event_readmit(state)
        self._initial = state
        self._published = _EventPublication(state)
        self._lock = Lock()

    @property
    def state(self) -> _GRC9V4EventState:
        return self._published.state

    @property
    def receipts(self) -> tuple[SuccessfulReceiptEnvelope, ...]:
        return self._published.receipts

    def checkpoint(self) -> bytes:
        with self._lock:
            published = self._published
            return canonical_json_bytes(
                {
                    "descriptor_version": self.CHECKPOINT,
                    **(
                        {"carrier_archives": [a.to_dict() for a in published.archives]}
                        if self.STATE is GRC9V4CPCState
                        else {}
                    ),
                    **(
                        {
                            "reference_currents": [
                                a.to_dict() for a in published.reference_currents
                            ]
                        }
                        if self.STATE in {GRC9V4AOSState, GRC9V4CCIState}
                        else {}
                    ),
                    "initial": self._initial.to_payload(),
                    "requests": [r.to_payload() for r in published.requests],
                    "state": published.state.to_payload(),
                    "receipts": [r.to_payload() for r in published.receipts],
                    "lifecycle_digest": published.state.lifecycle_digest(
                        published.receipts
                    ),
                }
            )

    @classmethod
    def replay(cls, checkpoint: bytes) -> Self:
        data: Any = _local_payload(
            decode_canonical_json(checkpoint),
            {
                "descriptor_version",
                "initial",
                "requests",
                "state",
                "receipts",
                "lifecycle_digest",
            }
            | ({"carrier_archives"} if cls.STATE is GRC9V4CPCState else set())
            | (
                {"reference_currents"}
                if cls.STATE in {GRC9V4AOSState, GRC9V4CCIState}
                else set()
            ),
            "descriptor_version",
            cls.CHECKPOINT,
        )
        initial = data["initial"]
        specialization = initial["specialization"]
        state = cls.STATE(
            GeometryStageInputs.from_payload(initial["inputs"]),
            GRC9V4Specialization(
                FrozenJSONMap(specialization["resolved"]),
                FrozenJSONMap(specialization["identity_payload"]),
            ),
        )
        result = cls(state)
        for request in data["requests"]:
            if not result.expand(
                GRC9V4ExpansionRequestInput.from_payload(request)
            ).committed:
                raise ValueError("event checkpoint replay rejected")
        if result.checkpoint() != checkpoint:
            raise ValueError("event checkpoint differs from native replay")
        return result

    def expand(self, request: GRC9V4ExpansionRequestInput) -> GRCV4LifecycleResult:
        if type(request) is not GRC9V4ExpansionRequestInput:
            raise TypeError("expected a closed expansion request")
        with self._lock, exact_backend(self._backend):
            published = self._published
            before = published.state
            stage: OperationStage = "admission"
            try:
                request = replace(request)
                if (
                    request.target_specialization_id
                    != before.specialization.specialization_id
                ):
                    raise ValueError(
                        "target specialization differs from the admitted declaration"
                    )
                if before.inputs.step_index == 0:
                    raise ValueError("expansion requires a postbeat seed")
                graph = before.inputs.geometry.reference.graph.port_graph
                assert graph is not None
                if type(before) is GRC9V4CPCState and canonical_json_bytes(
                    request.history_policy
                ) != canonical_json_bytes(
                    cpc_history_policy(before.inputs.current, before.inputs.reset)
                ):
                    raise ValueError(
                        "C_PC requires the actual whole carrier pair and explicit reset/loss policy"
                    )
                if type(before) is GRC9V4AOSState and canonical_json_bytes(
                    request.history_policy
                ) != canonical_json_bytes(
                    aos_history_policy(before.inputs.current, before.inputs.reset)
                ):
                    raise ValueError(
                        "A_OS requires the actual candidate-history pair and exact lineage policy"
                    )
                plan = GRC9V4ExpansionPlan(
                    graph,
                    before.scientific_digest,
                    request,
                    GRC9ExpansionPolicy.from_payload(
                        before.specialization.resolved["expansion"]
                    ),
                )
                role_reads = _event_readmit(before)
                current = (
                    role_reads[0].values
                    if role_reads is not None
                    else CandidatePCRead(before.inputs).point.current.values
                    if type(before) is GRC9V4CPCState
                    else CandidateCCurrent(before.inputs).current.values
                )
                detection = GRC9V4CandidateDetection(
                    GRC9V4PostbeatRows(
                        graph,
                        before.inputs.geometry.reference.profile,
                        before.inputs.current,
                        current,
                        before.inputs.step_index,
                        cast(
                            int, before.specialization.identity_payload["hessian_sign"]
                        ),
                    ),
                    GRC9SparkPolicy.from_payload(
                        before.specialization.resolved["spark"]
                    ),
                )
                if request.source_node_id not in detection.candidate_node_ids():
                    raise ValueError("source is not a fresh hybrid spark candidate")
                stage = "target_construction"
                target: _GRC9V4CExpansion | GRC9V4AOSExpansion
                if type(before) is GRC9V4AOSState:
                    target = GRC9V4AOSExpansion(
                        plan,
                        before.inputs.geometry.reference,
                        before.inputs.current,
                        before.inputs.reset,
                    )
                elif type(before) is GRC9V4CPCState:
                    target = GRC9V4CPCExpansion(
                        plan,
                        before.inputs.geometry.reference,
                        before.inputs.current,
                        before.inputs.reset,
                    )
                elif type(before) is GRC9V4CCIState:
                    target = GRC9V4CCIExpansion(plan, before.inputs.geometry.reference)
                else:
                    target = GRC9V4COSExpansion(plan, before.inputs.geometry.reference)
                inputs = replace(
                    before.inputs,
                    geometry=target.target.geometry(),
                    current=target.transfer(before.inputs.current),
                    reset=target.transfer(before.inputs.reset),
                    dt=0,
                    operation_id=request.operation_id,
                )
                after = self.STATE(inputs, before.specialization)
                stage = "target_readmission"
                _event_readmit(after)
                stage = "commit"
                commit, receipts = make_commit_receipts(
                    _event_receipts(before, after, target, published.receipts),
                    operation_id=request.operation_id,
                    source_state_digest=before.scientific_digest,
                    target_state_digest=after.scientific_digest,
                    target_step_index=inputs.step_index,
                    target_time=inputs.time,
                )
                archives = published.archives
                if type(target) is GRC9V4CPCExpansion:
                    archives += (FrozenJSONMap(target.carrier_archive_payload()),)
                reference_currents = published.reference_currents
                if type(target) in {GRC9V4AOSExpansion, GRC9V4CCIExpansion}:
                    assert isinstance(target, (GRC9V4AOSExpansion, GRC9V4CCIExpansion))
                    assert role_reads is not None
                    reference_currents += (
                        FrozenJSONMap(
                            {
                                "event_id": plan.event_id,
                                "source_graph_digest": target.source.graph.graph_digest,
                                "target_graph_digest": target.target.graph.graph_digest,
                                "roles": {
                                    role: {
                                        "source": list(read.values),
                                        "target": list(
                                            target.transfer_reference_current(
                                                read
                                            ).values
                                        ),
                                    }
                                    for role, read in zip(
                                        ("current", "reset"), role_reads, strict=True
                                    )
                                },
                            }
                        ),
                    )
                following = _EventPublication(
                    after,
                    published.receipts + receipts,
                    published.requests + (request,),
                    archives,
                    reference_currents,
                )
                result = GRCV4LifecycleResult(
                    "committed",
                    True,
                    payload_identity("commit_payload", commit.to_payload()),
                    None,
                    receipts,
                )
                # One publication: no target resource/profile/reset/receipt can
                # become visible while any construction or result check can fail.
                self._published = following
                return result
            except (ValueError, TypeError, ArithmeticError) as exc:
                code: FailureCode = (
                    "target_readmission_failure"
                    if stage == "target_readmission"
                    else "invalid_topology_event"
                )
                if isinstance(exc, GRC9V4ExpansionError):
                    codes: dict[str, FailureCode] = {
                        "source_not_saturated": "source_node_not_saturated",
                        "source_self_loop_unsupported": "source_self_loop_unsupported",
                        "module_chirality_required": "module_chirality_required",
                        "module_growth_phase_required": "module_growth_phase_required",
                        "reject_noncanonical_inactive_growth_phase": "reject_noncanonical_inactive_growth_phase",
                    }
                    code = codes.get(exc.code, code)
                digest = before.scientific_digest
                lifecycle = before.lifecycle_digest(published.receipts)
                payload = FailureReceiptIdentityPayload(
                    "grcv4-failure-receipt-v1",
                    request.operation_id,
                    stage,
                    code,
                    digest,
                    digest,
                )
                receipt = FailureReceipt(
                    "grcv4-failure-receipt-envelope-v1",
                    payload_identity(
                        "failure_receipt_identity_payload", payload.to_payload()
                    ),
                    payload,
                )
                failure = GRCV4Failure(
                    stage,
                    None,
                    code,
                    str(exc) or type(exc).__name__,
                    digest,
                    digest,
                    lifecycle,
                    lifecycle,
                    receipt,
                )
                return GRCV4LifecycleResult(
                    "rejected", False, None, failure, (receipt,)
                )


class GRC9V4COSOperation(_GRC9V4EventOperation):
    """Bounded native OS event owner; archive-free checkpoint bytes are stable."""

    STATE = GRC9V4COSState
    CHECKPOINT = "grc9v4-cos-event-checkpoint-v1"

    @property
    def state(self) -> GRC9V4COSState:
        return cast(GRC9V4COSState, self._published.state)


class GRC9V4CPCOperation(_GRC9V4EventOperation):
    """Bounded native PC event owner with atomic whole-carrier archives.

    The archive binds actual current then reset content and source edge order.
    It is retained evidence only; no archived coordinate enters target history.
    This internal event checkpoint is not the public Tranche 9 model facade.
    """

    STATE = GRC9V4CPCState
    CHECKPOINT = "grc9v4-cpc-event-checkpoint-v1"

    @property
    def state(self) -> GRC9V4CPCState:
        return cast(GRC9V4CPCState, self._published.state)

    @property
    def carrier_archives(self) -> tuple[FrozenJSONMap, ...]:
        return self._published.archives


class GRC9V4AOSOperation(_GRC9V4EventOperation):
    """Bounded A_OS event owner with exact W lineage and independent role reads.

    Checkpoint reference currents are replay-checked evidence, not authoritative
    state, target initializers, or cached inputs to any numerical kernel.
    """

    STATE = GRC9V4AOSState
    CHECKPOINT = "grc9v4-aos-event-checkpoint-v1"

    @property
    def state(self) -> GRC9V4AOSState:
        return cast(GRC9V4AOSState, self._published.state)


class GRC9V4CCIOperation(_GRC9V4EventOperation):
    """Bounded C_CI event owner with fresh current/reset joint-root admission.

    Mapped reference currents are replay evidence, never target root seeds.
    This internal checkpoint does not advertise public profile support.
    """

    STATE = GRC9V4CCIState
    CHECKPOINT = "grc9v4-cci-event-checkpoint-v1"

    @property
    def state(self) -> GRC9V4CCIState:
        return cast(GRC9V4CCIState, self._published.state)
