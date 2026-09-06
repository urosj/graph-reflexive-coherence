"""Pure duration-admission prefix; no candidate execution or state mutation.

The lifecycle owner must supply a genuine prestate digest and still admit the
complete graph/profile/context/state before running a strict request. This
module neither discovers those inputs nor claims runtime-profile support.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Literal, TypeAlias

from .grc_v4 import GRCV4StepRequest, GRCV4StepRequestInput, _nested_record
from .grc_v4_codec import V4IdentityError, payload_identity
from .grc_v4_profile import _Record

OperationStage: TypeAlias = Literal[
    "admission", "pre_read_reconstruction", "candidate_solve", "continuity",
    "charge_admission", "final_reconstruction", "history_write",
    "target_construction", "target_readmission", "restoration", "commit",
]
FailureCode: TypeAlias = Literal[
    "invalid_identity", "invalid_duration", "domain_failure", "singular_solver",
    "conditioning_failure", "nonfinite_value", "no_admitted_root",
    "multiple_admitted_roots", "charge_failure", "stale_cache",
    "unsupported_profile", "invalid_migration", "invalid_topology_event",
    "source_node_not_saturated", "source_self_loop_unsupported",
    "module_chirality_required", "module_growth_phase_required",
    "reject_noncanonical_inactive_growth_phase", "target_readmission_failure",
    "legacy_expansion_target_undefined", "restoration_failure",
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
            raise V4IdentityError("failure evidence must preserve the scientific prestate")


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
        object.__setattr__(self, "identity_payload", _nested_record(
            self.identity_payload, FailureReceiptIdentityPayload))
        _Record.__post_init__(self)
        payload_identity("failure_receipt_identity_payload",
                         self.identity_payload.to_payload(), expected=self.receipt_id)


def admit_step_request(
    request: GRCV4StepRequestInput, *, source_state_digest: str,
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
        "grcv4-failure-receipt-v1", detached.operation_id, "admission",
        "invalid_duration", source_state_digest, source_state_digest,
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
