"""Result composition, duration admission and the provisional resource boundary.

The lifecycle owner must supply a genuine prestate digest and still admit the
complete graph/profile/context/state before running a strict request. This
module neither discovers those inputs nor claims runtime-profile support.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field as dataclass_field, fields
from typing import Any, ClassVar, Literal, TypeAlias, cast, get_args

from .grc_v4 import GRCV4StepRequest, GRCV4StepRequestInput, _nested_record
from .grc_v4_codec import (
    V4IdentityError,
    V4SchemaError,
    canonical_json_bytes,
    payload_identity,
    validate_payload,
)
from .grc_v4_profile import _Record
from .grc_v4_geometry import (
    GeometryStageInputs,
    GeometryDomainError,
    NonfiniteGeometryError,
    PhysicalFlux,
    VertexScalar,
    _local_payload,
    _require_coordinates,
    _state_payload,
)
from .grc_v4_state import (
    FrozenJSONMap,
    GRCV4AuthoritativeState,
    GRCV4LifecycleResult,
    GRCV4StepResult,
    SolverDisposition,
)
from .grc_v4_transport import (
    ChargeDomainError,
    ChargeEvaluation,
    provisional_continuity,
)
from .grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError
from .grc_v4_candidate_a import (
    CandidateACurrent,
    CandidateADifferentialReference,
    CandidateAStageError,
    CandidateAWriter,
)
from .grc_v4_realizations import (
    CandidateCOSPass,
    CandidateAOSPass,
    _a_os_inputs,
    _os_inputs,
)

OperationStage: TypeAlias = Literal[
    "admission",
    "pre_read_reconstruction",
    "candidate_solve",
    "continuity",
    "charge_admission",
    "final_reconstruction",
    "history_write",
    "target_construction",
    "target_readmission",
    "restoration",
    "commit",
]
FailureCode: TypeAlias = Literal[
    "invalid_identity",
    "invalid_duration",
    "domain_failure",
    "singular_solver",
    "conditioning_failure",
    "nonfinite_value",
    "no_admitted_root",
    "multiple_admitted_roots",
    "charge_failure",
    "stale_cache",
    "unsupported_profile",
    "invalid_migration",
    "invalid_topology_event",
    "source_node_not_saturated",
    "source_self_loop_unsupported",
    "module_chirality_required",
    "module_growth_phase_required",
    "reject_noncanonical_inactive_growth_phase",
    "target_readmission_failure",
    "legacy_expansion_target_undefined",
    "restoration_failure",
]


@dataclass(frozen=True, slots=True, eq=False)
class FailureReceiptIdentityPayload(_Record):
    SCHEMA: ClassVar[str] = "failure_receipt_identity_payload"
    schema_version: Literal["grcv4-failure-receipt-v1"]
    operation_id: str
    stage: OperationStage
    code: FailureCode
    source_state_digest: str
    observed_poststate_digest: str

    def __post_init__(self) -> None:
        _Record.__post_init__(self)
        if self.source_state_digest != self.observed_poststate_digest:
            raise V4IdentityError(
                "failure evidence must preserve the scientific prestate"
            )


@dataclass(frozen=True, slots=True, eq=False)
class FailureReceipt(_Record):
    """Content-identity-checked noncommitting receipt, not authenticated provenance.

    The digest and equal state labels prove neither an observed operation nor
    live-state authenticity, rollback or a signature. The operation/lifecycle
    owner must bind those facts and keep emitted evidence separate from the
    persistent ledger. Receipt equality does not imply request equality: the
    frozen preimage omits duration and context. Reconstruction checks the enum
    vocabulary, not whether a stage/code pair occurred in an execution.
    """

    SCHEMA: ClassVar[str] = "failure_receipt"
    schema_version: Literal["grcv4-failure-receipt-envelope-v1"]
    receipt_id: str
    identity_payload: FailureReceiptIdentityPayload

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "identity_payload",
            _nested_record(self.identity_payload, FailureReceiptIdentityPayload),
        )
        _Record.__post_init__(self)
        payload_identity(
            "failure_receipt_identity_payload",
            self.identity_payload.to_payload(),
            expected=self.receipt_id,
        )


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4Failure(_Record):
    """Cross-checked failure declaration; operation binding is a separate check."""

    SCHEMA: ClassVar[str] = "failure_detail"
    stage: OperationStage
    solver_disposition: SolverDisposition | None
    code: FailureCode
    message: str
    prestate_digest: str
    poststate_digest: str
    pre_lifecycle_digest: str
    post_lifecycle_digest: str
    failure_receipt: FailureReceipt

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "failure_receipt",
            _nested_record(self.failure_receipt, FailureReceipt),
        )
        _Record.__post_init__(self)
        identity = self.failure_receipt.identity_payload
        if (
            self.prestate_digest != self.poststate_digest
            or self.pre_lifecycle_digest != self.post_lifecycle_digest
            or (self.stage, self.code, self.prestate_digest, self.poststate_digest)
            != (
                identity.stage,
                identity.code,
                identity.source_state_digest,
                identity.observed_poststate_digest,
            )
        ):
            raise V4IdentityError(
                "failure detail/receipt or pre/post identities disagree"
            )
        if (
            self.stage in ("admission", "pre_read_reconstruction")
            and self.solver_disposition is not None
        ):
            raise V4SchemaError("pre-solver failure cannot invent a solver disposition")


_SUCCESS_SCHEMAS = {
    "grcv4-" + kind.replace("_", "-") + "-receipt-v1": kind
    + "_receipt_identity_payload"
    for kind in (
        "step_commit",
        "reset",
        "rebase",
        "profile_migration",
        "topology_event",
        "charge",
        "history_disposition",
    )
}
_SUCCESS_SCHEMAS["grc9v4-legacy-compatibility-receipt-v1"] = (
    "legacy_compatibility_receipt_identity_payload"
)
_SUCCESS_SCHEMAS["grcv4-profile-migration-receipt-v2"] = "initializer_migration_receipt"


@dataclass(frozen=True, slots=True, eq=False)
class SuccessfulReceiptEnvelope(_Record):
    """Content-checked closed receipt payload, not proof of a successful operation.

    Versioned payloads remain immutable primitive declarations here. Their
    migration/history/compatibility effects belong to the lifecycle owners.
    The commit preimage is checked separately by bind_step_result.
    Parent receipt IDs are content only: this record does not resolve lineage.
    """

    SCHEMA: ClassVar[str] = "successful_receipt_envelope"
    schema_version: Literal["grcv4-successful-receipt-envelope-v1"]
    receipt_id: str
    commit_id: str
    identity_payload: FrozenJSONMap

    def __post_init__(self) -> None:
        _Record.__post_init__(self)
        payload = self.identity_payload.to_dict()
        schema = _SUCCESS_SCHEMAS[cast(str, payload["schema_version"])]
        payload_identity(schema, payload, expected=self.receipt_id)


Receipt: TypeAlias = SuccessfulReceiptEnvelope | FailureReceipt


@dataclass(frozen=True, slots=True, eq=False)
class CommitPayload(_Record):
    """Acyclic commit preimage; constructing it does not commit a model."""

    SCHEMA: ClassVar[str] = "commit_payload"
    INTEGER_FIELDS: ClassVar[tuple[str, ...]] = ("target_step_index",)
    schema_version: Literal["grcv4-commit-payload-v1"]
    operation_id: str
    source_state_digest: str
    target_state_digest: str
    emitted_receipt_ids: tuple[str, ...]
    target_step_index: int
    target_time: float

    def __post_init__(self) -> None:
        _Record.__post_init__(self)
        object.__setattr__(self, "emitted_receipt_ids", tuple(self.emitted_receipt_ids))
        object.__setattr__(self, "target_time", float(self.target_time))


def make_commit_receipts(
    receipt_payloads: object,
    *,
    operation_id: str,
    source_state_digest: str,
    target_state_digest: str,
    target_step_index: int,
    target_time: float,
) -> tuple[CommitPayload, tuple[SuccessfulReceiptEnvelope, ...]]:
    """Hash receipt payloads, then commit, then envelopes; no persistent write.

    This acyclic hashing order is not parent-receipt DAG validation. Parent
    scope/order remains the lifecycle owner's unresolved contract obligation.
    """
    if type(receipt_payloads) not in (list, tuple) or not receipt_payloads:
        raise TypeError("expected a nonempty ordered receipt payload sequence")
    payloads = [
        cast(dict[str, Any], validate_payload("successful_receipt_identity_payload", p))
        for p in cast(list[object], receipt_payloads)
    ]
    for p in payloads:
        core = p["core"]
        if (
            core["operation_id"],
            core["source_state_digest"],
            core["target_state_digest"],
        ) != (operation_id, source_state_digest, target_state_digest):
            raise V4IdentityError("receipt payload does not belong to this commit")
    identifiers = tuple(
        payload_identity(_SUCCESS_SCHEMAS[p["schema_version"]], p) for p in payloads
    )
    commit = CommitPayload(
        "grcv4-commit-payload-v1",
        operation_id,
        source_state_digest,
        target_state_digest,
        identifiers,
        target_step_index,
        target_time,
    )
    commit_id = payload_identity("commit_payload", commit.to_payload())
    return commit, tuple(
        SuccessfulReceiptEnvelope(
            "grcv4-successful-receipt-envelope-v1",
            identifier,
            commit_id,
            FrozenJSONMap(p),
        )
        for identifier, p in zip(identifiers, payloads, strict=True)
    )


def _result_parts(
    failure: object, receipts: object
) -> tuple[GRCV4Failure | None, tuple[Receipt, ...]]:
    detail = None if failure is None else _nested_record(failure, GRCV4Failure)
    if type(receipts) not in (tuple, list):
        raise TypeError("receipt delta must be an ordered list or tuple")
    result: list[Receipt] = []
    for value in cast(list[object] | tuple[object, ...], receipts):
        if type(value) in (FailureReceipt, SuccessfulReceiptEnvelope):
            assert isinstance(value, (FailureReceipt, SuccessfulReceiptEnvelope))
            result.append(type(value).from_payload(value.to_payload()))
        elif isinstance(value, Mapping):
            kind = (
                FailureReceipt
                if value.get("schema_version") == "grcv4-failure-receipt-envelope-v1"
                else SuccessfulReceiptEnvelope
            )
            result.append(kind.from_payload(value))
        else:
            raise TypeError("expected a closed receipt envelope")
    return detail, tuple(result)


def _validate_result(value: GRCV4StepResult | GRCV4LifecycleResult) -> None:
    """Local constructor invariants; no state, execution or replay authority."""
    if isinstance(value, GRCV4StepResult):
        validate_payload("step_result", value.to_payload())
    if value.committed:
        if not value.emitted_receipts:
            raise V4SchemaError(
                "a committed result must identify its emitted receipt delta"
            )
        for receipt in value.emitted_receipts:
            if (
                not isinstance(receipt, SuccessfulReceiptEnvelope)
                or receipt.commit_id != value.commit_id
            ):
                raise V4IdentityError(
                    "committed result requires receipts of this commit only"
                )
        if isinstance(value, GRCV4StepResult):
            # Migration/event/reset cannot be smuggled into an ordinary beat.
            allowed = {
                "grcv4-step-commit-receipt-v1",
                "grcv4-charge-receipt-v1",
                "grcv4-history-disposition-receipt-v1",
            }
            receipts = cast(
                tuple[SuccessfulReceiptEnvelope, ...], value.emitted_receipts
            )
            if any(
                cast(str, r.identity_payload["schema_version"]) not in allowed
                for r in receipts
            ):
                raise V4SchemaError("foreign lifecycle receipt in ordinary step")
    else:
        assert value.failure is not None
        if value.emitted_receipts != (value.failure.failure_receipt,):
            raise V4IdentityError(
                "rejected result emits its failure receipt, not persistent history"
            )
        if isinstance(value, GRCV4StepResult):
            if value.events:
                raise V4SchemaError("rejected step cannot emit committed events")
            failure = value.failure
            if value.solver_disposition != failure.solver_disposition:
                raise V4SchemaError(
                    "operation and failure solver dispositions disagree"
                )
            if (
                failure.stage
                in (
                    "continuity",
                    "charge_admission",
                    "final_reconstruction",
                    "history_write",
                    "commit",
                )
                and value.solver_disposition != "valid_root"
            ):
                raise V4SchemaError("post-solver step rejection must retain valid_root")
            if failure.stage == "candidate_solve":
                codes = {
                    "domain_failure": "domain_failure",
                    "singular": "singular_solver",
                    "conditioning_failure": "conditioning_failure",
                    "nonfinite": "nonfinite_value",
                    "no_admitted_root": "no_admitted_root",
                    "multiple_admitted_roots": "multiple_admitted_roots",
                }
                if codes.get(value.solver_disposition or "") != failure.code:
                    raise V4SchemaError(
                        "candidate-solve rejection requires its failed solver disposition"
                    )
            if failure.stage in (
                "target_construction",
                "target_readmission",
                "restoration",
            ):
                raise V4SchemaError("lifecycle stage is not an ordinary-step failure")
        elif value.failure.solver_disposition is not None:
            raise V4SchemaError(
                "lifecycle failure cannot invent a step solver disposition"
            )


def _ledger(value: object) -> tuple[SuccessfulReceiptEnvelope, ...]:
    _, receipts = _result_parts(None, value)
    if any(not isinstance(r, SuccessfulReceiptEnvelope) for r in receipts):
        raise V4SchemaError("failure receipt is not a persistent ledger entry")
    return cast(tuple[SuccessfulReceiptEnvelope, ...], receipts)


def _state_evidence(
    state: object, ledger: tuple[SuccessfulReceiptEnvelope, ...]
) -> tuple[dict[str, Any], str, str]:
    data = cast(dict[str, Any], validate_payload("scientific_state_payload", state))
    state_id = payload_identity("scientific_state_payload", data)
    lifecycle_id = payload_identity(
        "lifecycle_envelope_payload",
        {
            "schema_version": "grcv4-lifecycle-envelope-v1",
            "scientific_state_digest": state_id,
            "receipt_ids": [r.receipt_id for r in ledger],
        },
    )
    return data, state_id, lifecycle_id


@dataclass(frozen=True, slots=True)
class StepResultEvidence:
    """Immutable byte values; never a solver certificate, lineage or replay permit.

    Direct construction validates storage types only, not byte contents or
    whether bind_step_result was called. No consumer may trust the class alone.
    """

    request_bytes: bytes
    result_bytes: bytes
    prestate_bytes: bytes
    poststate_bytes: bytes
    pre_ledger_bytes: bytes
    post_ledger_bytes: bytes

    def __post_init__(self) -> None:
        for field in fields(self):
            if type(getattr(self, field.name)) is not bytes:
                raise TypeError(
                    "comparison evidence fields require exact immutable bytes"
                )


def bind_step_result(
    result: GRCV4StepResult,
    *,
    request: GRCV4StepRequestInput,
    prestate: object,
    poststate: object,
    pre_ledger: object,
    post_ledger: object,
    observed_stage: OperationStage,
    observed_code: FailureCode | None,
    observed_solver: SolverDisposition | None,
    commit_payload: object = None,
) -> StepResultEvidence:
    """Compare result, exact request, observed outcome, state payloads and ledgers.

    The operation owner must capture the actual inputs/outputs and observed
    stage, not obtain them from an imported receipt. This pure comparator does
    not execute, admit a graph/domain, authenticate an observer or roll back a
    mutable model. Content-matching observations are not scientific execution.
    A committed result accepts a primitive commit preimage or an exact
    CommitPayload; both are detached and revalidated before comparison.

    Parent receipt references are syntax/content checked, not resolved as a DAG.
    The frozen contract does not settle intra-commit versus historical parents
    or ordering; P9-7.6 must resolve that before claiming lineage conformance.
    Nor does this comparator validate clock progression, charge arithmetic or
    history-map truth. The harness must use independent live-operation oracles.
    """
    if (
        type(result) is not GRCV4StepResult
        or type(request) is not GRCV4StepRequestInput
    ):
        raise TypeError("expected V4 result and external step input records")
    if (
        type(observed_stage) is not str
        or (observed_code is not None and type(observed_code) is not str)
        or (observed_solver is not None and type(observed_solver) is not str)
    ):
        raise TypeError("observed outcome requires literal stage/code/solver labels")
    result = GRCV4StepResult.from_payload(result.to_payload())
    request = GRCV4StepRequestInput.from_payload(request.to_payload())
    before, after = _ledger(pre_ledger), _ledger(post_ledger)
    source, source_id, source_lifecycle = _state_evidence(prestate, before)
    target, target_id, target_lifecycle = _state_evidence(poststate, after)
    if result.active_model_identity != target["active_model_identity"] or (
        result.step_index,
        result.time,
    ) != (target["step_index"], target["time"]):
        raise V4IdentityError("result model or clock disagrees with observed state")
    if (
        result.active_model_identity.startswith("grcv4-profile-sha256:")
        and result.active_profile_id != result.active_model_identity
    ):
        raise V4IdentityError("generic active profile/model identities disagree")
    if not result.active_model_identity.startswith("grcv4-profile-sha256:"):
        raise V4SchemaError(
            "specialization model/profile binding requires its later owner"
        )
    if result.solver_disposition != observed_solver:
        raise V4IdentityError("result differs from observed solver disposition")
    if not result.committed:
        failure = result.failure
        assert failure is not None
        if commit_payload is not None:
            raise V4SchemaError("rejected operation cannot have a commit payload")
        if (
            (failure.stage, failure.code) != (observed_stage, observed_code)
            or failure.failure_receipt.identity_payload.operation_id
            != request.operation_id
            or (failure.prestate_digest, failure.poststate_digest)
            != (source_id, target_id)
            or (failure.pre_lifecycle_digest, failure.post_lifecycle_digest)
            != (source_lifecycle, target_lifecycle)
        ):
            raise V4IdentityError(
                "failure is not bound to this operation and observed state"
            )
        if (
            canonical_json_bytes(source) != canonical_json_bytes(target)
            or before != after
        ):
            raise V4IdentityError(
                "rejected operation changed scientific payload or persistent ledger"
            )
        if request.dt < 0 and (observed_stage, observed_code, observed_solver) != (
            "admission",
            "invalid_duration",
            None,
        ):
            raise V4IdentityError("negative duration must reject before solving")
        if request.dt >= 0 and observed_code == "invalid_duration":
            raise V4IdentityError(
                "nonnegative request cannot claim negative-duration rejection"
            )
    else:
        if request.dt < 0 or (observed_stage, observed_code, observed_solver) != (
            "commit",
            None,
            "valid_root",
        ):
            raise V4SchemaError(
                "commit requires nonnegative duration and an observed valid root"
            )
        commit = _nested_record(commit_payload, CommitPayload).to_payload()
        payload_identity("commit_payload", commit, expected=result.commit_id)
        expected = {
            "schema_version": "grcv4-commit-payload-v1",
            "operation_id": request.operation_id,
            "source_state_digest": source_id,
            "target_state_digest": target_id,
            "emitted_receipt_ids": [r.receipt_id for r in result.emitted_receipts],
            "target_step_index": result.step_index,
            "target_time": result.time,
        }
        if canonical_json_bytes(commit) != canonical_json_bytes(expected):
            raise V4IdentityError(
                "commit does not name this operation/state/ordered receipt delta"
            )
        if after != before + result.emitted_receipts:
            raise V4IdentityError(
                "persistent ledger is not prior history plus this operation delta"
            )
        for key in (
            "active_model_identity",
            "graph_digest",
            "orientation_identity",
            "reset_digest",
            "context_contract_id",
        ):
            if source[key] != target[key]:
                raise V4IdentityError("ordinary step cannot change lifecycle identity")
        for receipt in result.emitted_receipts:
            assert isinstance(receipt, SuccessfulReceiptEnvelope)
            core = cast(dict[str, Any], receipt.identity_payload.to_dict()["core"])
            for prefix, state, digest in [
                ("source", source, source_id),
                ("target", target, target_id),
            ]:
                authority_id = payload_identity(
                    "authoritative_state_identity_payload",
                    {
                        "schema_version": "grcv4-authoritative-state-identity-v1",
                        "authoritative": state["authoritative"],
                    },
                )
                for key, expected_value in {
                    "state_digest": digest,
                    "graph_digest": state["graph_digest"],
                    "model_identity": state["active_model_identity"],
                    "authoritative_digest": authority_id,
                    "reset_digest": state["reset_digest"],
                }.items():
                    if core[prefix + "_" + key] != expected_value:
                        raise V4IdentityError(
                            "receipt core differs from observed state"
                        )
            if core["operation_id"] != request.operation_id:
                raise V4IdentityError("foreign operation receipt")
        receipts_by_id = {r.receipt_id: r for r in result.emitted_receipts}
        for event in result.events:
            payload = event.payload
            receipt_key = payload.get("receipt_id")
            event_receipt = (
                receipts_by_id.get(receipt_key) if type(receipt_key) is str else None
            )
            if not isinstance(event_receipt, SuccessfulReceiptEnvelope):
                raise V4IdentityError("event must name an emitted successful receipt")
            core = cast(
                dict[str, Any], event_receipt.identity_payload.to_dict()["core"]
            )
            expected_event = {
                k: core[k]
                for k in (
                    "source_graph_digest",
                    "target_graph_digest",
                    "source_model_identity",
                    "target_model_identity",
                )
            }
            expected_event.update(
                commit_id=result.commit_id,
                source_profile_id=result.active_profile_id,
                target_profile_id=result.active_profile_id,
            )
            if event.step_index != result.step_index or any(
                payload.get(k) != v for k, v in expected_event.items()
            ):
                raise V4IdentityError(
                    "event lacks this operation's graph/profile/commit bindings"
                )
    return StepResultEvidence(
        request.to_canonical_bytes(),
        result.to_canonical_bytes(),
        canonical_json_bytes(source),
        canonical_json_bytes(target),
        canonical_json_bytes([r.to_payload() for r in before]),
        canonical_json_bytes([r.to_payload() for r in after]),
    )


def negative_duration_result(
    request: GRCV4StepRequestInput,
    *,
    prestate: object,
    receipt_ledger: object,
    active_profile_id: str,
    message: str = "negative duration",
) -> tuple[GRCV4StepResult, StepResultEvidence]:
    """Compose the actually executed duration rejection, with no solver or writer.

    Takes captured scientific payload/ledger values, not a live model. Positive
    and zero requests cannot produce a completed result through this helper.
    """
    if type(request) is not GRCV4StepRequestInput:
        raise TypeError("expected external step input")
    request = GRCV4StepRequestInput.from_payload(request.to_payload())
    ledger = _ledger(receipt_ledger)
    state, state_id, lifecycle_id = _state_evidence(prestate, ledger)
    receipt = admit_step_request(request, source_state_digest=state_id)
    if not isinstance(receipt, FailureReceipt):
        raise V4SchemaError(
            "nonnegative request still requires full step admission/execution"
        )
    failure = GRCV4Failure(
        "admission",
        None,
        "invalid_duration",
        message,
        state_id,
        state_id,
        lifecycle_id,
        lifecycle_id,
        receipt,
    )
    result = GRCV4StepResult(
        state["step_index"],
        state["time"],
        (),
        {},
        active_profile_id,
        state["active_model_identity"],
        "rejected",
        None,
        False,
        None,
        failure,
        (receipt,),
    )
    evidence = bind_step_result(
        result,
        request=request,
        prestate=state,
        poststate=state,
        pre_ledger=ledger,
        post_ledger=ledger,
        observed_stage="admission",
        observed_code="invalid_duration",
        observed_solver=None,
    )
    return result, evidence


def admit_step_request(
    request: GRCV4StepRequestInput,
    *,
    source_state_digest: str,
) -> GRCV4StepRequest | FailureReceipt:
    """Admit duration only, after transport shape; never run a scientific beat.

    Wrong Python types/forged records raise, not a semantic failure receipt.
    Source identity is supplied by the lifecycle owner, not authenticated from
    an unavailable state here. Even dt=0 must continue through later complete
    state/domain admission. No mutable model or caller callback is consumed.
    """
    if type(request) is not GRCV4StepRequestInput:
        raise TypeError("expected decoded GRCV4StepRequestInput")
    detached = GRCV4StepRequestInput.from_payload(request.to_payload())
    # Validate the supplied evidence context even on the positive-duration path.
    identity = FailureReceiptIdentityPayload(
        "grcv4-failure-receipt-v1",
        detached.operation_id,
        "admission",
        "invalid_duration",
        source_state_digest,
        source_state_digest,
    )
    if detached.dt < 0:
        return FailureReceipt(
            "grcv4-failure-receipt-envelope-v1",
            payload_identity("failure_receipt_identity_payload", identity.to_payload()),
            identity,
        )
    payload = detached.to_payload()
    payload["schema_version"] = "grcv4-step-request-v1"
    return GRCV4StepRequest.from_payload(payload)


@dataclass(frozen=True, slots=True)
class CurrentSelection:
    """A stage owner's supplied result; construction is not a root certificate.

    The later candidate/realization owner must actually execute residual,
    branch/stratum and current-domain checks. This record lets the common
    boundary reject failed dispositions, foreign inputs and predictor/trial
    substitutions without manufacturing an executable candidate provider.
    """

    inputs: GeometryStageInputs
    solver_disposition: SolverDisposition
    current: PhysicalFlux | None

    def __post_init__(self) -> None:
        if type(self.inputs) is not GeometryStageInputs:
            raise TypeError("current selection requires captured stage inputs")
        inputs = GeometryStageInputs.from_payload(self.inputs.to_payload())
        if type(
            self.solver_disposition
        ) is not str or self.solver_disposition not in get_args(SolverDisposition):
            raise ValueError("unknown current solver disposition")
        if self.current is not None:
            _require_coordinates(
                self.current, PhysicalFlux, inputs.geometry.reference.graph
            )
            object.__setattr__(
                self, "current", PhysicalFlux(self.current.graph, self.current.values)
            )
        object.__setattr__(self, "inputs", inputs)

    def to_payload(self) -> dict[str, Any]:
        return {
            "descriptor_version": "grcv4-current-selection-v1",
            "inputs": self.inputs.to_payload(),
            "solver_disposition": self.solver_disposition,
            "current": None if self.current is None else list(self.current.values),
        }

    @classmethod
    def from_payload(cls, value: object) -> CurrentSelection:
        data = _local_payload(
            value,
            {"descriptor_version", "inputs", "solver_disposition", "current"},
            "descriptor_version",
            "grcv4-current-selection-v1",
        )
        inputs = GeometryStageInputs.from_payload(data["inputs"])
        current = (
            None
            if data["current"] is None
            else PhysicalFlux(
                inputs.geometry.reference.graph, cast(Any, data["current"])
            )
        )
        return cls(inputs, cast(SolverDisposition, data["solver_disposition"]), current)


class ResourceBoundaryError(ValueError):
    """Local rejection to be composed by the later operation/receipt owner.

    This is not a returned GRCV4StepResult or evidence that a live lifecycle
    rolled back. No authoritative model is consumed or mutated here.
    """

    def __init__(
        self,
        stage: OperationStage,
        code: FailureCode,
        message: str,
        *,
        charge: ChargeEvaluation | None = None,
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.code = code
        self.charge = charge


def _resource_charge(
    inputs: GeometryStageInputs, resource: VertexScalar, stage: OperationStage
) -> ChargeEvaluation:
    try:
        evaluation = ChargeEvaluation(
            resource, inputs.Q_target, inputs.geometry.reference.profile
        )
    except (ChargeDomainError, NonfiniteGeometryError) as exc:
        code: FailureCode = (
            "nonfinite_value"
            if isinstance(exc, NonfiniteGeometryError)
            else "domain_failure"
        )
        raise ResourceBoundaryError(stage, code, str(exc)) from exc
    if not evaluation.admitted:
        raise ResourceBoundaryError(
            stage,
            "charge_failure",
            "resource charge is outside the declared tolerance",
            charge=evaluation,
        )
    return evaluation


_RESOURCE_SOLVER_FAILURES: dict[SolverDisposition, FailureCode] = {
    "domain_failure": "domain_failure",
    "singular": "singular_solver",
    "conditioning_failure": "conditioning_failure",
    "nonfinite": "nonfinite_value",
    "no_admitted_root": "no_admitted_root",
    "multiple_admitted_roots": "multiple_admitted_roots",
}
_SELECTED_CURRENT_STAGES = {
    "OS": "os_corrector",
    "CI": "ci_trial",
    "PC": "pc_old_history",
    "CI+PC": "cipc_trial",
    "RG2b": "rg2b_section",
}


@dataclass(frozen=True, slots=True)
class ProvisionalResourceStep:
    """The common resource-write/charge boundary inside a complete step.

    The caller independently captures pre-read inputs and supplies the actual
    current owner's result. A positive-duration evaluation invokes continuity
    once, validates its resource/charge and returns a provisional C with old
    nonresource authority. A zero-duration evaluation checks local prestate
    and reset charges and returns their unchanged resource with no current
    selection or writer advancement. Full admission, current/root execution,
    final-C reconstruction, writers, clock advancement and atomic lifecycle
    commit remain with their owners; this is not a complete numerical step.
    """

    prestate: GeometryStageInputs
    selection: CurrentSelection | None
    provisional_state: GRCV4AuthoritativeState = dataclass_field(init=False)
    charge: ChargeEvaluation = dataclass_field(init=False)
    continuity_evaluations: int = dataclass_field(init=False)

    def __post_init__(self) -> None:
        if type(self.prestate) is not GeometryStageInputs:
            raise TypeError(
                "resource boundary requires independently captured prestate"
            )
        before = GeometryStageInputs.from_payload(self.prestate.to_payload())
        if before.stage != "pre_read" or before.trial_current is not None:
            raise ResourceBoundaryError(
                "admission", "stale_cache", "resource boundary requires pre-read inputs"
            )
        ref = before.geometry.reference
        initial = VertexScalar(ref.graph, before.current.C)
        charge = _resource_charge(before, initial, "admission")
        _resource_charge(before, VertexScalar(ref.graph, before.reset.C), "admission")
        selection = self.selection
        if before.dt == 0:
            if selection is not None:
                raise ResourceBoundaryError(
                    "admission",
                    "domain_failure",
                    "zero duration has no current-selection or writer advancement",
                )
            resource = initial
        else:
            if type(selection) is not CurrentSelection:
                raise TypeError("positive duration requires the current owner's result")
            selection = CurrentSelection.from_payload(selection.to_payload())
            chosen = selection.inputs
            # Scientific/lifecycle IDs omit duration and actual stage geometry.
            # Bind those separately without forbidding a lawful corrected Hodge.
            if (
                canonical_json_bytes(before.scientific_state_preimage)
                != canonical_json_bytes(chosen.scientific_state_preimage)
                or before.source_lifecycle_id != chosen.source_lifecycle_id
                or before.operation_id != chosen.operation_id
                or before.dt != chosen.dt
                or canonical_json_bytes(ref.to_payload())
                != canonical_json_bytes(chosen.geometry.reference.to_payload())
                or before.context != chosen.context
                or chosen.stage
                != _SELECTED_CURRENT_STAGES[ref.profile.identity_payload.realization]
            ):
                raise ResourceBoundaryError(
                    "candidate_solve",
                    "stale_cache",
                    "selected current belongs to another input or realization stage",
                )
            if selection.solver_disposition != "valid_root":
                raise ResourceBoundaryError(
                    "candidate_solve",
                    _RESOURCE_SOLVER_FAILURES[selection.solver_disposition],
                    "failed solver disposition cannot supply a fallback current",
                )
            if selection.current is None:
                raise ResourceBoundaryError(
                    "candidate_solve",
                    "domain_failure",
                    "valid root lacks a typed current",
                )
            if (
                chosen.stage in ("ci_trial", "cipc_trial")
                and selection.current != chosen.trial_current
            ):
                raise ResourceBoundaryError(
                    "candidate_solve",
                    "stale_cache",
                    "selected current differs from the accepted trial evaluation",
                )
            try:
                resource = provisional_continuity(
                    initial, selection.current, before.dt, differential=ref.differential
                )
            except NonfiniteGeometryError as exc:
                raise ResourceBoundaryError(
                    "continuity", "nonfinite_value", str(exc)
                ) from exc
            charge = _resource_charge(before, resource, "charge_admission")
        provisional = GRCV4AuthoritativeState(
            resource.values, before.current.W_A, before.current.Z_4
        )
        for name, value in (
            ("prestate", before),
            ("selection", selection),
            ("provisional_state", provisional),
            ("charge", charge),
            ("continuity_evaluations", int(before.dt > 0)),
        ):
            object.__setattr__(self, name, value)

    def consume(
        self,
        *,
        expected_prestate: GeometryStageInputs,
        expected_selection: CurrentSelection | None,
    ) -> GRCV4AuthoritativeState:
        """Check independently held expectations before a final-C consumer."""
        if type(expected_prestate) is not GeometryStageInputs or (
            expected_selection is not None
            and type(expected_selection) is not CurrentSelection
        ):
            raise TypeError(
                "resource consumption requires typed independent expectations"
            )
        if canonical_json_bytes(self.prestate.to_payload()) != canonical_json_bytes(
            expected_prestate.to_payload()
        ) or canonical_json_bytes(
            None if self.selection is None else self.selection.to_payload()
        ) != canonical_json_bytes(
            None if expected_selection is None else expected_selection.to_payload()
        ):
            raise ResourceBoundaryError(
                "final_reconstruction",
                "stale_cache",
                "stale provisional resource result",
            )
        return self.provisional_state

    def to_payload(self) -> dict[str, Any]:
        """Local reconstruction evidence, separate from frozen lifecycle wire data."""
        return {
            "descriptor_version": "grcv4-provisional-resource-step-v1",
            "prestate": self.prestate.to_payload(),
            "selection": None
            if self.selection is None
            else self.selection.to_payload(),
            "provisional_state": _state_payload(self.provisional_state),
            "charge": self.charge.receipt_values(),
            "remainder": self.charge.remainder,
            "continuity_evaluations": self.continuity_evaluations,
        }


@dataclass(frozen=True, slots=True)
class ProvisionalCandidateCOSStep:
    """A C_OS numerical step through final-C refresh, with no live mutation.

    One pass selects the corrector, one resource boundary writes provisional C,
    and all final C-derived operators are rebuilt at the consumed geometry.
    next_inputs resets geometry to the profile reference for the next beat;
    no OS geometry/cache becomes retained history. Clock addition is binary64;
    a positive subnormal duration still takes the positive-duration path even
    if the represented clock or resource does not change.

    The lifecycle owner still authenticates the source/ledger, creates commit
    receipts, checks its complete postconditions and commits atomically. This
    immutable result is not an exported model, receipt or conformance claim.
    """

    inputs: GeometryStageInputs
    os_pass: CandidateCOSPass | None = dataclass_field(init=False)
    resource: ProvisionalResourceStep = dataclass_field(init=False)
    final: CandidateCCurrent | None = dataclass_field(init=False)
    next_inputs: GeometryStageInputs = dataclass_field(init=False)

    def __post_init__(self) -> None:
        from dataclasses import replace
        from fractions import Fraction
        import math

        before = _os_inputs(self.inputs)
        if before.dt > 0 and before.step_index == 2**53 - 1:
            raise ResourceBoundaryError(
                "admission",
                "domain_failure",
                "step index would exceed the safe integer domain",
            )
        graph = before.geometry.reference.graph
        _resource_charge(before, VertexScalar(graph, before.current.C), "admission")
        _resource_charge(before, VertexScalar(graph, before.reset.C), "admission")
        # The reset baseline is a future restart input, not just a charge label.
        CandidateCCurrent(
            replace(before, current=before.reset, stage="reset_readmission")
        )
        try:
            next_time = float(Fraction(before.time) + Fraction(before.dt))
        except OverflowError as exc:
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "step clock overflow"
            ) from exc
        if not math.isfinite(next_time):
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "step clock overflow"
            )
        if before.dt == 0:
            # Admission is still required; identity is not an escape from a
            # singular current, invalid selector, context or reset baseline.
            CandidateCCurrent(before)
            result = ProvisionalResourceStep(before, None)
            passed = None
            final = None
            following = before
        else:
            passed = CandidateCOSPass(before)
            corrector = passed.corrector
            result = ProvisionalResourceStep(
                before,
                CurrentSelection(corrector.inputs, "valid_root", corrector.current),
            )
            try:
                final = CandidateCCurrent(
                    replace(
                        corrector.inputs,
                        current=result.provisional_state,
                        stage="post_continuity",
                    )
                )
            except (
                CandidateCStageError,
                GeometryDomainError,
                NonfiniteGeometryError,
            ) as exc:
                code: FailureCode = (
                    "nonfinite_value"
                    if isinstance(exc, NonfiniteGeometryError)
                    or isinstance(exc, CandidateCStageError)
                    and exc.disposition == "nonfinite"
                    else "domain_failure"
                )
                raise ResourceBoundaryError(
                    "final_reconstruction", code, str(exc)
                ) from exc
            following = replace(
                before,
                current=result.provisional_state,
                step_index=before.step_index + 1,
                time=next_time,
            )
        for name, value in (
            ("inputs", before),
            ("os_pass", passed),
            ("resource", result),
            ("final", final),
            ("next_inputs", following),
        ):
            object.__setattr__(self, name, value)


@dataclass(frozen=True, slots=True)
class ProvisionalCandidateAOSStep:
    """A OS pass, one continuity/write, and separate final current admission.

    Positive writer output does not establish current regularity. Reconstruct
    the written state at consumed geometry and at the next reference geometry
    before returning any candidate poststate. Neither check can feed back into
    continuity or the writer. Complete receipt/lifecycle publication remains
    with the A lifecycle child; a failure leaves all supplied authority intact.
    """

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference
    os_pass: CandidateAOSPass | None = dataclass_field(init=False)
    resource: ProvisionalResourceStep = dataclass_field(init=False)
    writer: CandidateAWriter | None = dataclass_field(init=False)
    final: CandidateACurrent = dataclass_field(init=False)
    restart: CandidateACurrent = dataclass_field(init=False)
    next_inputs: GeometryStageInputs = dataclass_field(init=False)

    def __post_init__(self) -> None:
        from dataclasses import replace
        from fractions import Fraction
        import math

        before = _a_os_inputs(self.inputs)
        if before.dt > 0 and before.step_index == 2**53 - 1:
            raise ResourceBoundaryError(
                "admission",
                "domain_failure",
                "step index would exceed the safe integer domain",
            )
        graph = before.geometry.reference.graph
        _resource_charge(before, VertexScalar(graph, before.current.C), "admission")
        _resource_charge(before, VertexScalar(graph, before.reset.C), "admission")
        try:
            CandidateACurrent(
                replace(before, current=before.reset, stage="reset_readmission"),
                self.differential_reference,
            )
        except (
            CandidateAStageError,
            GeometryDomainError,
            NonfiniteGeometryError,
        ) as exc:
            raise ResourceBoundaryError(
                "pre_read_reconstruction",
                "nonfinite_value"
                if isinstance(exc, NonfiniteGeometryError)
                or isinstance(exc, CandidateAStageError)
                and exc.disposition == "nonfinite"
                else "domain_failure",
                str(exc),
            ) from exc
        try:
            next_time = float(Fraction(before.time) + Fraction(before.dt))
        except OverflowError as exc:
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "step clock overflow"
            ) from exc
        if not math.isfinite(next_time):
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "step clock overflow"
            )
        passed = None
        writer = None
        if before.dt == 0:
            try:
                final = CandidateACurrent(before, self.differential_reference)
            except (
                CandidateAStageError,
                GeometryDomainError,
                NonfiniteGeometryError,
            ) as exc:
                raise ResourceBoundaryError(
                    "pre_read_reconstruction",
                    "nonfinite_value"
                    if isinstance(exc, NonfiniteGeometryError)
                    or isinstance(exc, CandidateAStageError)
                    and exc.disposition == "nonfinite"
                    else "domain_failure",
                    str(exc),
                ) from exc
            resource = ProvisionalResourceStep(before, None)
            restart, following = final, before
        else:
            passed = CandidateAOSPass(before, self.differential_reference)
            corrector = passed.corrector
            resource = ProvisionalResourceStep(
                before,
                CurrentSelection(corrector.inputs, "valid_root", corrector.current),
            )
            stage: OperationStage = "history_write"
            try:
                writer = CandidateAWriter(corrector, resource)
                stage = "final_reconstruction"
                final = CandidateACurrent(
                    replace(
                        corrector.inputs,
                        current=writer.authority.state,
                        stage="post_continuity",
                    ),
                    self.differential_reference,
                )
                following = replace(
                    before,
                    current=writer.authority.state,
                    step_index=before.step_index + 1,
                    time=next_time,
                )
                restart = CandidateACurrent(
                    replace(following, dt=0, stage="target_readmission"),
                    self.differential_reference,
                )
            except (
                CandidateAStageError,
                GeometryDomainError,
                NonfiniteGeometryError,
            ) as exc:
                raise ResourceBoundaryError(
                    stage,
                    "nonfinite_value"
                    if isinstance(exc, NonfiniteGeometryError)
                    or isinstance(exc, CandidateAStageError)
                    and exc.disposition == "nonfinite"
                    else "domain_failure",
                    str(exc),
                ) from exc
        for name, value in (
            ("inputs", before),
            ("os_pass", passed),
            ("resource", resource),
            ("writer", writer),
            ("final", final),
            ("restart", restart),
            ("next_inputs", following),
        ):
            object.__setattr__(self, name, value)

    def to_payload(self) -> dict[str, object]:
        return {
            "schema_version": "grcv4-a-os-step-v1",
            "inputs": self.inputs.to_payload(),
            "differential_reference": self.differential_reference.to_payload(),
        }

    @classmethod
    def from_payload(cls, value: object) -> ProvisionalCandidateAOSStep:
        data = _local_payload(
            value,
            {"schema_version", "inputs", "differential_reference"},
            "schema_version",
            "grcv4-a-os-step-v1",
        )
        return cls(
            GeometryStageInputs.from_payload(data["inputs"]),
            CandidateADifferentialReference.from_payload(
                data["differential_reference"]
            ),
        )
