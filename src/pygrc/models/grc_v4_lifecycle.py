"""Bounded C_OS ordinary-operation and lifecycle owner (P9-4.5/P9-4.6).

One immutable lifecycle tuple is published only after numerical admission,
reference restart admission, receipt construction and result binding succeed.
Snapshot/load/reset/rebase operate on the same receiver. Migration, events,
full receipt-lineage pressure and public facade/profile conformance are later work. There are no injectable production solvers, commit callbacks or faults.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from pathlib import Path
from fractions import Fraction
from threading import Lock
from typing import Any, Self, cast

from .grc_v4 import GRCV4StepRequestInput
from .grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError
from .grc_v4_codec import (
    V4IdentityError,
    V4SchemaError,
    canonical_json_bytes,
    cos_snapshot_payload,
    decode_canonical_json,
    payload_identity,
)
from .grc_v4_geometry import (
    GRCV4ReferenceGeometry,
    GeometryStageInputs,
    GeometryDomainError,
    NonfiniteGeometryError,
    VertexScalar,
    _state_from_payload,
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
    CommitPayload,
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


def _receipt_context(
    ref: GRCV4ReferenceGeometry,
) -> tuple[dict[str, Any], dict[str, str]]:
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
    return channels, {
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
    }


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
    channels, references = _receipt_context(ref)
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
        **references,
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


@dataclass(frozen=True, slots=True)
class _OwnedCOS:
    """One publication includes the state and all receipt commit preimages."""

    state: GRCV4LifecycleState
    commits: tuple[CommitPayload, ...]


def _state_inputs(
    reference: GRCV4ReferenceGeometry,
    state: GRCV4LifecycleState,
    operation_id: str = "lifecycle_readmission",
) -> GeometryStageInputs:
    return GeometryStageInputs(
        reference.geometry(),
        reference.context,
        state.current,
        state.reset.authoritative,
        operation_id,
        state.Q_target,
        tuple(cast(str, r["receipt_id"]) for r in state.receipt_ledger),
        state.step_index,
        state.time,
        0,
        "pre_read",
        0,
        None,
    )


def _restore_commits(
    records: list[Any],
    ledger: tuple[SuccessfulReceiptEnvelope, ...],
    reference: GRCV4ReferenceGeometry,
    Q_target: float,
    reset_digest: str,
) -> tuple[CommitPayload, ...]:
    """Check content and ordered commit coverage of this receiver's ledger.

    This bounded import does not certify the truth of an externally supplied
    history or discharge the later receipt-ownership/replay pressure leaf.
    Migration/event and alternative parent conventions are not imported here.
    """
    commits: list[CommitPayload] = []
    position = 0
    seen: set[str] = set()
    last_step: str | None = None
    last_primary: str | None = None
    last_reset: str | None = None
    _, reference_ids = _receipt_context(reference)
    for record in records:
        commit = CommitPayload.from_payload(record["payload"])
        commit_id = payload_identity(
            "commit_payload", commit.to_payload(), expected=record["commit_id"]
        )
        group = ledger[position : position + len(commit.emitted_receipt_ids)]
        if (
            len(group) != 4
            or tuple(r.receipt_id for r in group) != commit.emitted_receipt_ids
        ):
            raise V4IdentityError(
                "commit does not cover its ordered four-receipt delta"
            )
        primary = group[0].identity_payload.to_dict()
        kind = primary["schema_version"]
        if kind not in {
            "grcv4-step-commit-receipt-v1",
            "grcv4-reset-receipt-v1",
            "grcv4-rebase-receipt-v1",
        }:
            raise V4SchemaError("unsupported lifecycle operation in C_OS snapshot")
        if commits:
            previous = commits[-1]
            index_delta = commit.target_step_index - previous.target_step_index
            if kind == "grcv4-step-commit-receipt-v1":
                # Assignment, reset and rebase do not write the clock. Ordinary
                # dt=0 keeps both fields; positive binary64 dt increments the
                # index once and adds at least the smallest positive duration.
                valid_clock = (
                    index_delta == 0 and commit.target_time == previous.target_time
                ) or (
                    index_delta == 1
                    and commit.target_time >= previous.target_time + 5e-324
                )
            else:
                valid_clock = (
                    index_delta == 0 and commit.target_time == previous.target_time
                )
            if not valid_clock:
                raise V4IdentityError(
                    "impossible clock transition in local commit history"
                )
        core = primary["core"]
        assert isinstance(core, dict)
        expected_parent = (
            last_step if kind == "grcv4-step-commit-receipt-v1" else last_primary
        )
        if core["parent_receipt_ids"] != (
            [] if expected_parent is None else [expected_parent]
        ):
            raise V4IdentityError(
                "snapshot does not use this receiver's local parent convention"
            )
        if (
            core["operation_id"],
            core["source_state_digest"],
            core["target_state_digest"],
        ) != (
            commit.operation_id,
            commit.source_state_digest,
            commit.target_state_digest,
        ):
            raise V4IdentityError(
                "receipt and commit operation/state bindings disagree"
            )
        if any(core[key] != expected for key, expected in reference_ids.items()):
            raise V4IdentityError(
                "receipt resource/history reference identity is unreconstructible"
            )
        if last_reset is not None and core["source_reset_digest"] != last_reset:
            raise V4IdentityError("local operation silently replaces reset baseline")
        last_reset = cast(str, core["target_reset_digest"])
        for prefix in ("source", "target"):
            if (core[prefix + "_graph_digest"], core[prefix + "_model_identity"]) != (
                reference.graph.graph_digest,
                reference.profile.complete_profile_id,
            ):
                raise V4IdentityError(
                    "fixed-profile snapshot contains a foreign graph/profile receipt"
                )
        for receipt in group:
            if (
                receipt.receipt_id in seen
                or receipt.commit_id != commit_id
                or receipt.identity_payload["core"] != group[0].identity_payload["core"]
            ):
                raise V4IdentityError(
                    "duplicate receipt or inconsistent commit/core ownership"
                )
            seen.add(receipt.receipt_id)
        charge = group[1].identity_payload
        if charge["schema_version"] != "grcv4-charge-receipt-v1":
            raise V4IdentityError("missing ordered charge receipt")
        if charge["target_charge"] != Q_target:
            raise V4IdentityError("receipt changes the fixed lifecycle charge target")
        actual = cast(float, charge["admitted_charge"])
        delta = Fraction(actual) - Fraction(Q_target)
        policy = reference.profile.params_resolved.charge
        bound = Fraction(policy.absolute_tolerance) + Fraction(
            policy.relative_tolerance
        ) * max(abs(Fraction(Q_target)), Fraction(1))
        try:
            residual = float(delta)
        except OverflowError:
            raise V4IdentityError("unrepresentable receipted charge residual") from None
        if actual < 0 or abs(delta) > bound or residual != charge["residual"]:
            raise V4IdentityError("charge receipt is outside its declared admission")
        for receipt, subject, disposition in zip(
            group[2:],
            ("candidate", "carrier"),
            ("rederived", "not_applicable"),
            strict=True,
        ):
            p = receipt.identity_payload
            if (
                p["schema_version"],
                p.get("subject"),
                p.get("history_disposition"),
                p.get("information_loss"),
            ) != (
                "grcv4-history-disposition-receipt-v1",
                subject,
                disposition,
                "none",
            ):
                raise V4IdentityError("snapshot invents candidate/carrier history")
        if core["information_losses"]:
            raise V4IdentityError("C_OS local operations have no history loss")
        if kind == "grcv4-reset-receipt-v1" and not (
            primary["reset_baseline_digest"]
            == core["source_reset_digest"]
            == core["target_reset_digest"]
        ):
            raise V4IdentityError("reset receipt changes its reset baseline")
        if kind == "grcv4-rebase-receipt-v1" and (
            primary["old_reset_digest"],
            primary["new_reset_digest"],
        ) != (core["source_reset_digest"], core["target_reset_digest"]):
            raise V4IdentityError("rebase receipt disagrees with baseline transition")
        if kind == "grcv4-rebase-receipt-v1" and (
            core["source_authoritative_digest"] != core["target_authoritative_digest"]
            or core["actual_charge_delta"] != 0
        ):
            raise V4IdentityError("rebase cannot change current authority or charge")
        if kind == "grcv4-step-commit-receipt-v1":
            if core["source_reset_digest"] != core["target_reset_digest"]:
                raise V4IdentityError("ordinary step cannot rebase reset")
            last_step = group[0].receipt_id
        last_primary = group[0].receipt_id
        position += len(group)
        commits.append(commit)
    if last_reset is not None and last_reset != reset_digest:
        raise V4IdentityError(
            "ledger reset identity does not match the restored baseline"
        )
    if position != len(ledger):
        raise V4IdentityError("snapshot has receipts without their commit preimages")
    return tuple(commits)


class CandidateCOSOperation:
    """Bounded C_OS receiver; the full public GRCV4 facade remains later work.

    Fresh construction has an empty ledger. from_state/load restore a complete
    snapshot, including commit preimages. References, current/reset coordinates,
    receipts and commits have no mutable aliases; numerical caches never persist.
    Calls that publish state are serialized, with one immutable pointer swap.
    """

    __slots__ = ("_reference", "_owned", "_lock")

    def __init__(self, initial: GeometryStageInputs) -> None:
        before = _os_inputs(initial)
        if before.receipt_ids:
            raise ValueError("fresh C_OS owner cannot import unauthenticated receipts")
        # dt=0 performs all reference/current/reset/charge admission, no writer.
        ProvisionalCandidateCOSStep(replace(before, dt=0))
        self._reference = before.geometry.reference
        self._owned = _OwnedCOS(_lifecycle_state(before, ()), ())
        self._lock = Lock()

    @property
    def state(self) -> GRCV4LifecycleState:
        """One recursively immutable observation of the committed tuple."""
        return self._owned.state

    @property
    def reference(self) -> GRCV4ReferenceGeometry:
        return self._reference

    @property
    def _state(self) -> GRCV4LifecycleState:
        return self._owned.state

    def get_state(self) -> GRCV4LifecycleState:
        return self.state

    def snapshot(self) -> dict[str, Any]:
        """Detached, self-contained JSON values; no causal or inspection caches."""
        # Capture once. Reference identity cannot change on this bounded owner.
        owned = self._owned
        inputs = _state_inputs(self._reference, owned.state)
        return {
            "schema_version": "grcv4-snapshot-v1",
            "model_family": "GRCV4",
            "implementation_layout_id": "pygrc-c-os-snapshot-v1",
            "reference": self._reference.to_payload(),
            "scientific_state": inputs.scientific_state_preimage,
            "scientific_state_digest": owned.state.scientific_state_digest,
            "reset": inputs.reset_preimage,
            "reset_digest": owned.state.reset.reset_digest,
            "receipt_ledger": [r.to_dict() for r in owned.state.receipt_ledger],
            "commit_records": [
                {
                    "commit_id": payload_identity("commit_payload", c.to_payload()),
                    "payload": c.to_payload(),
                }
                for c in owned.commits
            ],
            "lifecycle": {
                "schema_version": "grcv4-lifecycle-envelope-v1",
                "scientific_state_digest": owned.state.scientific_state_digest,
                "receipt_ids": list(inputs.receipt_ids),
            },
            "lifecycle_digest": owned.state.lifecycle_digest,
        }

    @classmethod
    def from_state(cls, state: object, params: object = None) -> Self:
        """Full restoration; optional resolved params are an equality assertion.

        This internal receiver accepts its explicit snapshot layout. It is not
        the public common-interface facade or a migration route. No missing
        identity, history, baseline, commit preimage or reference is synthesized.
        """
        data = cast(dict[str, Any], cos_snapshot_payload(state))
        reference = GRCV4ReferenceGeometry.from_payload(data["reference"])
        if params is not None and canonical_json_bytes(params) != canonical_json_bytes(
            reference.profile.params_resolved.to_payload()
        ):
            raise V4IdentityError(
                "restoration parameters differ from embedded resolved identity"
            )
        scientific, reset = data["scientific_state"], data["reset"]
        if (
            payload_identity("scientific_state_payload", scientific)
            != data["scientific_state_digest"]
        ):
            raise V4IdentityError("scientific state digest does not match content")
        if payload_identity("grcv4_reset_payload", reset) != data["reset_digest"]:
            raise V4IdentityError("reset digest does not match content")
        ledger = _ledger(data["receipt_ledger"])
        commits = _restore_commits(
            data["commit_records"],
            ledger,
            reference,
            scientific["Q_target"],
            data["reset_digest"],
        )
        inputs = GeometryStageInputs(
            reference.geometry(),
            reference.context,
            _state_from_payload(scientific["authoritative"]),
            _state_from_payload(reset["authoritative"]),
            "restoration",
            scientific["Q_target"],
            tuple(r.receipt_id for r in ledger),
            scientific["step_index"],
            scientific["time"],
            0,
            "pre_read",
            0,
            None,
        )
        if canonical_json_bytes(scientific) != canonical_json_bytes(
            inputs.scientific_state_preimage
        ) or canonical_json_bytes(reset) != canonical_json_bytes(inputs.reset_preimage):
            raise V4IdentityError(
                "snapshot graph/profile/context/reset/charge identities disagree"
            )
        expected_lifecycle = {
            "schema_version": "grcv4-lifecycle-envelope-v1",
            "scientific_state_digest": inputs.scientific_state_id,
            "receipt_ids": list(inputs.receipt_ids),
        }
        if canonical_json_bytes(data["lifecycle"]) != canonical_json_bytes(
            expected_lifecycle
        ):
            raise V4IdentityError(
                "snapshot lifecycle does not bind its state and ordered receipts"
            )
        if (
            payload_identity("lifecycle_envelope_payload", expected_lifecycle)
            != data["lifecycle_digest"]
        ):
            raise V4IdentityError("lifecycle digest does not match content")
        authority_id = payload_identity(
            "authoritative_state_identity_payload",
            {
                "schema_version": "grcv4-authoritative-state-identity-v1",
                "authoritative": scientific["authoritative"],
            },
        )
        for receipt in ledger:
            core = cast(FrozenJSONMap, receipt.identity_payload["core"])
            for prefix in ("source", "target"):
                if core[prefix + "_state_digest"] == inputs.scientific_state_id and (
                    core[prefix + "_authoritative_digest"] != authority_id
                    or core[prefix + "_reset_digest"] != inputs.reset_id
                ):
                    raise V4IdentityError(
                        "receipt subdigests contradict the embedded scientific state"
                    )
        for commit in commits:
            if commit.target_state_digest == inputs.scientific_state_id and (
                commit.target_step_index,
                commit.target_time,
            ) != (inputs.step_index, inputs.time):
                raise V4IdentityError(
                    "commit clock contradicts its embedded target state"
                )
        if commits and (commits[-1].target_step_index, commits[-1].target_time) != (
            inputs.step_index,
            inputs.time,
        ):
            raise V4IdentityError("restored clock differs from the last local commit")
        # Fresh profile, reset and current admission at the OS reference geometry.
        # dt=0 deliberately performs no next-beat predictor/corrector or writer.
        inputs = _os_inputs(inputs)
        ProvisionalCandidateCOSStep(inputs)
        target = _lifecycle_state(inputs, ledger)
        publication = _OwnedCOS(target, commits)
        result = cls.__new__(cls)
        result._lock = Lock()
        result._reference = inputs.geometry.reference
        result._owned = publication
        return result

    def save(self, path: str) -> None:
        # Fully materialize before opening the destination. Filesystem failures
        # propagate; no crash/durable-storage transaction is claimed.
        content = canonical_json_bytes(self.snapshot())
        Path(path).write_bytes(content)

    @classmethod
    def load(cls, path: str) -> Self:
        # Explicit canonical route preserves JCS large binary64 number tokens.
        return cls.from_state(decode_canonical_json(Path(path).read_bytes()))

    def duplicate(self) -> Self:
        return type(self).from_state(self.snapshot())

    def __copy__(self) -> Self:
        return self.duplicate()

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        duplicate = self.duplicate()
        memo[id(self)] = duplicate
        return duplicate

    def set_state(self, state: GRCV4LifecycleState) -> None:
        """Assign compatible C only; the live clock and lifecycle remain fixed."""
        if type(state) is not GRCV4LifecycleState:
            raise TypeError("set_state requires a typed complete lifecycle state")
        # Revalidate storage even if the caller supplied an existing frozen DTO.
        state = GRCV4LifecycleState(
            **{f.name: getattr(state, f.name) for f in fields(state)}
        )
        with self._lock:
            live = self._owned
            for name in (
                "step_index",
                "time",
                "graph",
                "graph_digest",
                "orientation_identity",
                "profile",
                "context_contract_id",
                "context_value_digest",
                "reset",
                "Q_target",
                "receipt_ledger",
            ):
                if getattr(state, name) != getattr(live.state, name):
                    raise V4IdentityError("set_state cannot replace " + name)
            inputs = _os_inputs(_state_inputs(self._reference, state))
            ProvisionalCandidateCOSStep(inputs)
            ledger = _ledger([r.to_dict() for r in state.receipt_ledger])
            target = _lifecycle_state(inputs, ledger)
            if target != state:
                raise V4IdentityError(
                    "assigned current state has incorrect content digests"
                )
            publication = _OwnedCOS(target, live.commits)
            self._owned = publication

    def reset(self) -> None:
        self._administrative("reset")

    def rebase_reset_baseline(self) -> None:
        self._administrative("rebase")

    def _administrative(self, kind: str) -> None:
        with self._lock:
            owned = self._owned
            before = _state_inputs(
                self._reference, owned.state, kind + ":" + owned.state.lifecycle_digest
            )
            ledger = _ledger([r.to_dict() for r in owned.state.receipt_ledger])
            # The frozen reduced baseline has no clock or receipt list. Reset
            # changes C only and retains live clock; rebase changes reset only.
            following = (
                replace(before, current=before.reset)
                if kind == "reset"
                else replace(before, reset=before.current)
            )
            following = _os_inputs(following)
            admitted = ProvisionalCandidateCOSStep(following)
            payloads = _ordinary_receipts(before, following, admitted, ledger)
            core = payloads[0]["core"]
            core["parent_receipt_ids"] = (
                [] if not owned.commits else [owned.commits[-1].emitted_receipt_ids[0]]
            )
            payloads[0] = {
                "schema_version": "grcv4-" + kind + "-receipt-v1",
                "core": core,
                **(
                    {"reset_baseline_digest": before.reset_id}
                    if kind == "reset"
                    else {
                        "old_reset_digest": before.reset_id,
                        "new_reset_digest": following.reset_id,
                    }
                ),
            }
            commit, emitted = make_commit_receipts(
                payloads,
                operation_id=before.operation_id,
                source_state_digest=before.scientific_state_id,
                target_state_digest=following.scientific_state_id,
                target_step_index=following.step_index,
                target_time=following.time,
            )
            target = _lifecycle_state(following, ledger + emitted)
            publication = _OwnedCOS(target, owned.commits + (commit,))
            self._owned = publication

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
        publication = _OwnedCOS(target, self._owned.commits + (commit,))
        self._owned = publication
        return result
