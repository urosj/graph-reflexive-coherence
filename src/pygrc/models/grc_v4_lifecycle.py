"""Bounded C_OS ordinary-operation owner (P9-4.5).

One immutable lifecycle tuple is published only after numerical admission,
reference restart admission, receipt construction and result binding succeed.
Snapshot/load/reset/migration and public facade/profile conformance are later
work. There are no injectable production solvers, commit callbacks or faults.
"""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from threading import Lock
from typing import Any

from .grc_v4 import GRCV4StepRequestInput
from .grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError
from .grc_v4_codec import payload_identity
from .grc_v4_geometry import (
    GRCV4ReferenceGeometry,
    GeometryStageInputs,
    GeometryDomainError,
    NonfiniteGeometryError,
    VertexScalar,
    _computed,
)
from .grc_v4_realizations import OSStageError, _os_inputs
from .grc_v4_state import (
    FrozenJSONMap,
    GRCV4LifecycleState,
    GRCV4ResetBaseline,
    GRCV4StepResult,
    SolverDisposition,
)
from .grc_v4_step import (
    FailureReceipt,
    FailureReceiptIdentityPayload,
    GRCV4Failure,
    OperationStage,
    ProvisionalCandidateCOSStep,
    ResourceBoundaryError,
    SuccessfulReceiptEnvelope,
    _RESOURCE_SOLVER_FAILURES,
    _ledger,
    _resource_charge,
    bind_step_result,
    make_commit_receipts,
    negative_duration_result,
)


def _lifecycle_state(
    inputs: GeometryStageInputs, ledger: tuple[SuccessfulReceiptEnvelope, ...]
) -> GRCV4LifecycleState:
    """Derive every identity from owned values; no caller digest is accepted."""
    before = replace(inputs, receipt_ids=tuple(r.receipt_id for r in ledger))
    ref = before.geometry.reference
    reset = GRCV4ResetBaseline(
        before.reset,
        ref.graph.graph_digest,
        ref.graph.orientation_identity,
        ref.profile.complete_profile_id,
        before.context.contract_id,
        before.Q_target,
        before.reset_id,
    )
    return GRCV4LifecycleState(
        before.step_index,
        before.time,
        FrozenJSONMap(ref.graph.to_payload()),
        ref.graph.graph_digest,
        ref.graph.orientation_identity,
        FrozenJSONMap(ref.profile.to_payload()),
        before.context.contract_id,
        None,
        before.current,
        reset,
        before.Q_target,
        tuple(FrozenJSONMap(r.to_payload()) for r in ledger),
        before.scientific_state_id,
        before.source_lifecycle_id,
    )


def _failed_solver(error: BaseException) -> SolverDisposition:
    """Use typed originating failures, never parse human-readable messages."""
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, CandidateCStageError):
            return current.disposition
        if isinstance(current, (NonfiniteGeometryError, OverflowError)):
            return "nonfinite"
        current = current.__cause__
    return "domain_failure"


def _ordinary_receipts(
    before: GeometryStageInputs,
    after: GeometryStageInputs,
    step: ProvisionalCandidateCOSStep,
    ledger: tuple[SuccessfulReceiptEnvelope, ...],
) -> list[dict[str, Any]]:
    """Actual ordinary-operation receipts, with no event or history transport.

    The universal core's resource transform identifies unchanged vertex
    placement (identity, no event increment), not the nonlinear continuity
    map. Source/target authority binds the actual resource write. The history
    bundle names C rederivation and absence of a carrier. Parents form only
    this owner's provisional ordinary-commit chain. Later lineage ownership
    may revise this schema-filling convention and the resulting receipt IDs.
    """
    ref = before.geometry.reference
    vertices = ref.graph.live_node_ids
    size = len(vertices)
    relocation = {
        "schema_version": "grcv4-resource-event-transform-v1",
        "policy_id": "identity_resource_transport_v1",
        "source_vertex_ids": list(vertices),
        "target_vertex_ids": list(vertices),
        "row_major_coefficients": [
            int(i == j) for i in range(size) for j in range(size)
        ],
        "target_increment": [0] * size,
    }
    channels = {
        subject: {
            "schema_version": "grcv4-history-channel-policy-v1",
            "subject": subject,
            "policy_id": policy,
            "disposition": disposition,
            "source_history_digest": None,
            "target_initializer_id": None,
            "information_loss": "none",
        }
        for subject, policy, disposition in (
            (
                "candidate",
                ref.profile.params_resolved.lifecycle.history_policy_id,
                "rederived",
            ),
            ("carrier", "no_persistent_carrier_v1", "not_applicable"),
        )
    }
    parent = next(
        (
            r.receipt_id
            for r in reversed(ledger)
            if r.identity_payload["schema_version"] == "grcv4-step-commit-receipt-v1"
        ),
        None,
    )
    core: dict[str, Any] = {
        "operation_id": before.operation_id,
        "resource_transform_digest": payload_identity(
            "resource_transform_identity_payload",
            {
                "schema_version": "grcv4-resource-transform-identity-v1",
                "transform": relocation,
            },
        ),
        "history_bundle_digest": payload_identity(
            "history_bundle_identity_payload",
            {
                "schema_version": "grcv4-history-bundle-identity-v1",
                "history_bundle": {
                    "schema_version": "grcv4-history-bundle-policy-v1",
                    **channels,
                },
            },
        ),
        "actual_charge_delta": _computed(
            float(
                Fraction(step.resource.charge.actual)
                - Fraction(
                    _resource_charge(
                        before, VertexScalar(ref.graph, before.current.C), "admission"
                    ).actual
                )
            )
        ),
        "information_losses": [],
        "disposition": "committed",
        "parent_receipt_ids": [] if parent is None else [parent],
    }
    for prefix, inputs in (("source", before), ("target", after)):
        core.update(
            {
                prefix + "_state_digest": inputs.scientific_state_id,
                prefix + "_graph_digest": ref.graph.graph_digest,
                prefix + "_model_identity": ref.profile.complete_profile_id,
                prefix + "_authoritative_digest": payload_identity(
                    "authoritative_state_identity_payload",
                    {
                        "schema_version": "grcv4-authoritative-state-identity-v1",
                        "authoritative": inputs.scientific_state_preimage[
                            "authoritative"
                        ],
                    },
                ),
                prefix + "_reset_digest": inputs.reset_id,
            }
        )
    return [
        {"schema_version": "grcv4-step-commit-receipt-v1", "core": core},
        {
            "schema_version": "grcv4-charge-receipt-v1",
            "core": core,
            **step.resource.charge.receipt_values(),
        },
        *(
            {
                "schema_version": "grcv4-history-disposition-receipt-v1",
                "core": core,
                "subject": subject,
                "history_disposition": channel["disposition"],
                "information_loss": "none",
            }
            for subject, channel in channels.items()
        ),
    ]


class CandidateCOSOperation:
    """An ordinary-operation receiver, not the complete public GRCV4 facade.

    Construction admits a fresh declared initial state with an empty ledger;
    it is not snapshot/load or receipt import. Initial input request metadata
    is discarded. Every call captures its actual request and current ledger.
    Only reference geometry and scientific/lifecycle values persist; no OS
    current, geometry, residual or cache is retained. Calls are serialized.
    """

    __slots__ = ("_reference", "_state", "_lock")

    def __init__(self, initial: GeometryStageInputs) -> None:
        before = _os_inputs(initial)
        if before.receipt_ids:
            raise ValueError("fresh C_OS owner cannot import unauthenticated receipts")
        # dt=0 performs all reference/current/reset/charge admission, no writer.
        ProvisionalCandidateCOSStep(replace(before, dt=0))
        self._reference = before.geometry.reference
        self._state = _lifecycle_state(before, ())
        self._lock = Lock()

    @property
    def state(self) -> GRCV4LifecycleState:
        """One recursively immutable observation of the committed tuple."""
        return self._state

    @property
    def reference(self) -> GRCV4ReferenceGeometry:
        return self._reference

    def _inputs(self, request: GRCV4StepRequestInput) -> GeometryStageInputs:
        state = self._state
        ledger = _ledger([r.to_dict() for r in state.receipt_ledger])
        return GeometryStageInputs(
            self._reference.geometry(),
            self._reference.context,
            state.current,
            state.reset.authoritative,
            request.operation_id,
            state.Q_target,
            tuple(r.receipt_id for r in ledger),
            state.step_index,
            state.time,
            max(0, request.dt),
            "pre_read",
            0,
            None,
        )

    def step_v4(self, request: GRCV4StepRequestInput) -> GRCV4StepResult:
        if type(request) is not GRCV4StepRequestInput:
            raise TypeError("expected decoded external step input")
        request = GRCV4StepRequestInput.from_payload(request.to_payload())
        with self._lock:
            return self._execute(request)

    def _execute(self, request: GRCV4StepRequestInput) -> GRCV4StepResult:
        before = self._inputs(request)
        owned = self._state
        ledger = _ledger([r.to_dict() for r in owned.receipt_ledger])
        source = before.scientific_state_preimage
        profile_id = self._reference.profile.complete_profile_id
        if request.dt < 0:
            result, _ = negative_duration_result(
                request,
                prestate=source,
                receipt_ledger=ledger,
                active_profile_id=profile_id,
            )
            return result
        stage: OperationStage = "admission"
        solver: SolverDisposition | None = None
        try:
            if (
                request.context_value
                or request.boundary_input is not None
                or request.external_source is not None
            ):
                raise ResourceBoundaryError(
                    "admission",
                    "domain_failure",
                    "C_OS requires constant-zero context and no external input",
                )
            stage = "pre_read_reconstruction"
            # Rebuild from owned immutable values; caller caches are never inputs.
            before = _os_inputs(before)
            stage = "candidate_solve"
            step = ProvisionalCandidateCOSStep(before)
            solver = "valid_root"
            stage = "final_reconstruction"
            following = step.next_inputs
            # Final-C at consumed h1 does not establish next-reference admission.
            # This is a read-only commit postcondition, never another OS pass.
            restart = CandidateCCurrent(replace(following, dt=0))
        except (
            ResourceBoundaryError,
            OSStageError,
            CandidateCStageError,
            GeometryDomainError,
            NonfiniteGeometryError,
        ) as exc:
            if isinstance(exc, ResourceBoundaryError):
                stage, code = exc.stage, exc.code
                solver = (
                    None
                    if stage in ("admission", "pre_read_reconstruction")
                    else "valid_root"
                )
            elif isinstance(exc, OSStageError):
                stage, solver = "candidate_solve", _failed_solver(exc)
                code = _RESOURCE_SOLVER_FAILURES[solver]
            elif stage == "candidate_solve":
                # Reset/reference admission fails before OS candidate execution.
                stage, solver = "pre_read_reconstruction", None
                code = (
                    "nonfinite_value"
                    if _failed_solver(exc) == "nonfinite"
                    else "domain_failure"
                )
            else:
                code = (
                    "nonfinite_value"
                    if _failed_solver(exc) == "nonfinite"
                    else "domain_failure"
                )
            identity = FailureReceiptIdentityPayload(
                "grcv4-failure-receipt-v1",
                request.operation_id,
                stage,
                code,
                before.scientific_state_id,
                before.scientific_state_id,
            )
            receipt = FailureReceipt(
                "grcv4-failure-receipt-envelope-v1",
                payload_identity(
                    "failure_receipt_identity_payload", identity.to_payload()
                ),
                identity,
            )
            failure = GRCV4Failure(
                stage,
                solver,
                code,
                str(exc),
                before.scientific_state_id,
                before.scientific_state_id,
                before.source_lifecycle_id,
                before.source_lifecycle_id,
                receipt,
            )
            result = GRCV4StepResult(
                owned.step_index,
                owned.time,
                (),
                {},
                profile_id,
                profile_id,
                "rejected",
                solver,
                False,
                None,
                failure,
                (receipt,),
            )
            bind_step_result(
                result,
                request=request,
                prestate=source,
                poststate=source,
                pre_ledger=ledger,
                post_ledger=ledger,
                observed_stage=stage,
                observed_code=code,
                observed_solver=solver,
            )
            return result
        # Internal receipt, identity and binding errors propagate; they are not
        # observations of a scientific domain failure. Publication is still last.
        stage = "commit"
        commit, emitted = make_commit_receipts(
            _ordinary_receipts(before, following, step, ledger),
            operation_id=request.operation_id,
            source_state_digest=before.scientific_state_id,
            target_state_digest=following.scientific_state_id,
            target_step_index=following.step_index,
            target_time=following.time,
        )
        target_ledger = ledger + emitted
        target = _lifecycle_state(following, target_ledger)
        observations: dict[str, Any] = {
            "charge": step.resource.charge.receipt_values(),
            "reference_current": {
                "stage": "commit_reference_readmission",
                "values": list(restart.current.values),
            },
            "continuity_evaluations": step.resource.continuity_evaluations,
        }
        if step.os_pass is not None:
            observations["os"] = {
                "stage": "os_corrector",
                "current": list(step.os_pass.corrector.current.values),
                "split_residual": [list(row) for row in step.os_pass.residual.values],
                "exact_split_residual": [
                    list(row) for row in step.os_pass.residual.exact_values
                ],
                "selector_path_segments": step.os_pass.selector_path_segments,
            }
        result = GRCV4StepResult(
            target.step_index,
            target.time,
            (),
            observations,
            profile_id,
            profile_id,
            "committed",
            "valid_root",
            True,
            emitted[0].commit_id,
            None,
            emitted,
        )
        bind_step_result(
            result,
            request=request,
            prestate=source,
            poststate=following.scientific_state_preimage,
            pre_ledger=ledger,
            post_ledger=target_ledger,
            observed_stage="commit",
            observed_code=None,
            observed_solver="valid_root",
            commit_payload=commit,
        )
        # No fallible validation, serialization or callback follows publication.
        self._state = target
        return result
