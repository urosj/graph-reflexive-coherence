"""Bounded enabled GRC9V4 lifecycle: one publication and one receipt journal.

P9-9.1b composes the accepted ordinary kernels and mechanical event receiver.
It does not select an allocator, implement completion/hierarchy, or advertise
full GRC9V4 compatibility. Disabled delegation and crossings are separate work.
Snapshots replay the actual mixed operation journal from an admitted seed;
the seed is not evidence of earlier beats. Numerical policy is explicit and
captured, with no retry, backend substitution, or precision fallback.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from threading import RLock

from . import grc_9_v4_lifecycle as events
from . import grc_v4_lifecycle as generic
from ._grc_v4_evidence import _operation_evidence
from .grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from .grc_9_v4_topology import GRC9V4CandidateADifferentialReference
from .grc_v4 import GRCV4StepRequestInput
from .grc_v4_certification import (
    NumericalPolicy,
    current_numerical_policy,
    numerical_policy,
)
from .grc_v4_codec import canonical_json_bytes, decode_canonical_json, payload_identity
from .grc_v4_exact import ExactBackend, current_exact_backend, exact_backend
from .grc_v4_geometry import GeometryStageInputs
from .grc_v4_state import FrozenJSONMap, GRCV4LifecycleResult, GRCV4StepResult
from .grc_v4_step import (
    FailureReceipt,
    FailureReceiptIdentityPayload,
    GRCV4Failure,
    ResourceBoundaryError,
    make_commit_receipts,
)


_OWNERS = {
    "C_OS": events.GRC9V4COSOperation,
    "C_CI": events.GRC9V4CCIOperation,
    "A_CI": events.GRC9V4ACIOperation,
    "A_PC": events.GRC9V4APCOperation,
}
_LAYOUT = "grc9v4-enabled-lifecycle-checkpoint-v1"


def _decode_state(value, family):
    if type(value) is not dict or set(value) != {
        "inputs",
        "specialization",
        "scientific_digest",
        "reset_digest",
        "model_identity",
    }:
        raise ValueError("closed native state required")
    spec = value["specialization"]
    if type(spec) is not dict or set(spec) != {"resolved", "identity_payload"}:
        raise ValueError("closed specialization required")
    state = _OWNERS[family].STATE(
        GeometryStageInputs.from_payload(value["inputs"]),
        events.GRC9V4Specialization(
            FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])
        ),
    )
    if canonical_json_bytes(state.to_payload()) != canonical_json_bytes(value):
        raise ValueError("native state identity mismatch")
    return state


def _backend(state):
    return (
        GRC9V4CandidateADifferentialReference(
            state.inputs.geometry.reference.graph.port_graph
        )
        if state.FAMILY.startswith("A_")
        else None
    )


def _payloads(before, after, charge, ledger):
    # The generic kernel's diagnostic identities are never published as the
    # specialization model/reset/state. All other numerical facts stay intact.
    payloads = generic._ordinary_receipts(before.inputs, after.inputs, charge, ledger)
    core = payloads[0]["core"]
    for prefix, state in (("source", before), ("target", after)):
        core.update(
            {
                prefix + "_state_digest": state.scientific_digest,
                prefix + "_model_identity": state.model_identity,
                prefix + "_reset_digest": state.reset_digest,
            }
        )
    return payloads


def _bind_result(result, request, before, after, ledger, *, commit=None):
    """Bind actual nine-port endpoints; generic binders deliberately reject these.

    Native state construction binds profile + resolved specialization, including
    the port owner. Schema constructors validate receipts/results; this check
    links them to the operation that just ran, before publication.
    """
    if (
        result.active_model_identity != after.model_identity
        or result.active_profile_id
        != after.inputs.geometry.reference.profile.complete_profile_id
        or (result.step_index, result.time)
        != (after.inputs.step_index, after.inputs.time)
    ):
        raise ValueError("result differs from native model/profile/clock")
    if result.committed:
        if (
            request.dt < 0
            or result.solver_disposition != "valid_root"
            or commit is None
        ):
            raise ValueError("invalid successful step disposition")
        expected = dict(
            schema_version="grcv4-commit-payload-v1",
            operation_id=request.operation_id,
            source_state_digest=before.scientific_digest,
            target_state_digest=after.scientific_digest,
            emitted_receipt_ids=[r.receipt_id for r in result.emitted_receipts],
            target_step_index=after.inputs.step_index,
            target_time=after.inputs.time,
        )
        if canonical_json_bytes(commit.to_payload()) != canonical_json_bytes(expected):
            raise ValueError("commit differs from native operation/endpoints/delta")
        if payload_identity("commit_payload", expected) != result.commit_id:
            raise ValueError("commit identity mismatch")
        for key in (
            "active_model_identity",
            "graph_digest",
            "orientation_identity",
            "reset_digest",
            "context_contract_id",
        ):
            if before.scientific_payload[key] != after.scientific_payload[key]:
                raise ValueError("ordinary step changed lifecycle identity")
    else:
        failure = result.failure
        life = before.lifecycle_digest(ledger)
        if (
            commit is not None
            or failure is None
            or before != after
            or failure.failure_receipt.identity_payload.operation_id
            != request.operation_id
            or (failure.prestate_digest, failure.poststate_digest)
            != (before.scientific_digest,) * 2
            or (failure.pre_lifecycle_digest, failure.post_lifecycle_digest)
            != (life,) * 2
        ):
            raise ValueError("failure differs from actual unchanged native publication")
        if (request.dt < 0) != (failure.code == "invalid_duration"):
            raise ValueError("duration failure does not match request")


@dataclass(frozen=True, slots=True)
class _Publication:
    state: events._GRC9V4EventState
    receipts: tuple = ()
    journal: tuple[FrozenJSONMap, ...] = ()
    archives: tuple[FrozenJSONMap, ...] = ()
    reference_currents: tuple[FrozenJSONMap, ...] = ()


class GRC9V4EnabledOperation:
    """Internal enabled owner for the four selected families; no public G3 grant.

    Callers may explicitly request a mechanical expansion. Detection and target
    admission run afresh in the accepted event receiver. Nothing schedules an
    autonomous event or chooses target resource/history allocations here.
    """

    def __init__(self, state):
        family = getattr(state, "FAMILY", None)
        if family not in _OWNERS or type(state) is not _OWNERS[family].STATE:
            raise TypeError("expected a selected native C_OS/C_CI/A_CI/A_PC state")
        if state.specialization.resolved["spark"]["child_stabilization"] is not None:
            raise ValueError("completion/hierarchy is unselected in P9-9.1b")
        self._backend_choice = current_exact_backend()
        self._policy = current_numerical_policy()
        # Reuse the closed constructor and both-role admission, not a flag.
        seed = _OWNERS[family](state).state
        self._initial = seed
        self._published = _Publication(seed)
        self._lock = RLock()

    @property
    def state(self):
        return self._published.state

    @property
    def receipts(self):
        return self._published.receipts

    @property
    def numerical_policy(self):
        return self._policy

    def _publish(
        self, before, after, emitted, action, *, archives=None, references=None
    ):
        # Validate the mixed chain before the sole write. Unexpected defects
        # propagate; they never become an apparent scientific rejection.
        parent = generic._previous_primary(before.receipts)
        if not emitted or len({r.receipt_id for r in before.receipts + emitted}) != len(
            before.receipts + emitted
        ):
            raise ValueError("successful receipt IDs must be globally unique")
        for receipt in emitted:
            core = receipt.identity_payload["core"]
            if (
                list(core["parent_receipt_ids"]) != ([] if parent is None else [parent])
                or core["source_state_digest"] != before.state.scientific_digest
                or core["target_state_digest"] != after.scientific_digest
                or core["source_model_identity"] != before.state.model_identity
                or core["target_model_identity"] != after.model_identity
                or core["source_reset_digest"] != before.state.reset_digest
                or core["target_reset_digest"] != after.reset_digest
            ):
                raise ValueError("specialization publication/receipt mismatch")
        publication = _Publication(
            after,
            before.receipts + emitted,
            before.journal + (FrozenJSONMap(action),),
            before.archives if archives is None else archives,
            before.reference_currents if references is None else references,
        )
        self._published = publication

    def expand(self, request):
        if type(request) is not GRC9V4ExpansionRequestInput:
            raise TypeError("expected closed nine-port expansion request")
        with (
            self._lock,
            exact_backend(self._backend_choice),
            numerical_policy(self._policy),
        ):
            before = self._published
            # A disposable transaction receiver, not a second live owner. Seed
            # its ledger with the entire mixed prefix so event parents are real.
            receiver = _OWNERS[before.state.FAMILY](before.state)
            receiver._published = events._EventPublication(
                before.state,
                before.receipts,
                (),
                before.archives,
                before.reference_currents,
            )
            result = receiver.expand(request)
            if result.committed:
                target = receiver._published
                self._publish(
                    before,
                    target.state,
                    result.emitted_receipts,
                    {"kind": "expand", "request": request.to_payload()},
                    archives=target.archives,
                    references=target.reference_currents,
                )
            return result

    def step_v4(self, request):
        if type(request) is not GRCV4StepRequestInput:
            raise TypeError("expected decoded external step input")
        request = GRCV4StepRequestInput.from_payload(request.to_payload())
        with (
            self._lock,
            exact_backend(self._backend_choice),
            numerical_policy(self._policy),
        ):
            return self._step(request)

    @_operation_evidence
    def _step(self, request):
        published = self._published
        before = published.state
        profile = before.inputs.geometry.reference.profile.complete_profile_id
        if request.dt < 0:
            return self._rejected(
                request, "admission", "invalid_duration", None, "negative duration"
            )
        inputs = replace(
            before.inputs, operation_id=request.operation_id, dt=request.dt
        )
        try:
            if (
                request.context_value
                or request.boundary_input is not None
                or request.external_source is not None
            ):
                raise ResourceBoundaryError(
                    "admission",
                    "domain_failure",
                    "local enabled owner requires zero context and no external input",
                )
            step = generic._profile_step(inputs, _backend(before))
            generic._check_step_target(inputs, step.next_inputs)
            selected, restart, selected_stage = generic._step_currents(step)
        except ResourceBoundaryError as exc:
            solver = (
                None
                if exc.stage in ("admission", "pre_read_reconstruction")
                else "valid_root"
                if exc.stage
                in (
                    "continuity",
                    "charge_admission",
                    "final_reconstruction",
                    "history_write",
                    "commit",
                )
                else next(
                    (
                        s
                        for s, c in generic._RESOURCE_SOLVER_FAILURES.items()
                        if c == exc.code
                    ),
                    "valid_root",
                )
            )
            return self._rejected(request, exc.stage, exc.code, solver, str(exc))
        except (
            generic.OSStageError,
            generic.CandidateCStageError,
            generic.CandidateAStageError,
            generic.GeometryDomainError,
            generic.NonfiniteGeometryError,
        ) as exc:
            if isinstance(exc, generic.OSStageError):
                solver = generic._failed_solver(exc)
                return self._rejected(
                    request,
                    "candidate_solve",
                    generic._RESOURCE_SOLVER_FAILURES[solver],
                    solver,
                    str(exc),
                )
            return self._rejected(
                request,
                "pre_read_reconstruction",
                "nonfinite_value"
                if generic._failed_solver(exc) == "nonfinite"
                else "domain_failure",
                None,
                str(exc),
            )
        after = type(before)(
            replace(step.next_inputs, receipt_ids=()), before.specialization
        )
        # Bind receipt request to the actual operation; operation_id/dt are not
        # scientific authority and do not change the source scientific digest.
        source = type(before)(inputs, before.specialization)
        commit, emitted = make_commit_receipts(
            _payloads(source, after, step.resource.charge, published.receipts),
            operation_id=request.operation_id,
            source_state_digest=before.scientific_digest,
            target_state_digest=after.scientific_digest,
            target_step_index=after.inputs.step_index,
            target_time=after.inputs.time,
        )
        observations = generic._public_observables(
            after.inputs,
            published.receipts + emitted,
            step.resource.charge,
            selected if request.dt > 0 else restart,
            stage="commit",
            current_stage=selected_stage if request.dt > 0 else "commit_reconstruction",
            solver="valid_root",
            consumed=request.dt > 0,
        )
        observations.update(
            active_model_identity=after.model_identity,
            compatibility_branch="enabled_v4",
            support_status="bounded_enabled_lifecycle_not_full_GRC9V4_conformance",
            charge=step.resource.charge.receipt_values(),
            continuity_evaluations=step.resource.continuity_evaluations,
        )
        result = GRCV4StepResult(
            after.inputs.step_index,
            after.inputs.time,
            (),
            observations,
            profile,
            after.model_identity,
            "committed",
            "valid_root",
            True,
            emitted[0].commit_id,
            None,
            emitted,
        )
        _bind_result(result, request, before, after, published.receipts, commit=commit)
        self._publish(
            published, after, emitted, {"kind": "step", "request": request.to_payload()}
        )
        return result

    def _rejected(self, request, stage, code, solver, message):
        before = self._published
        state = before.state
        identity = FailureReceiptIdentityPayload(
            "grcv4-failure-receipt-v1",
            request.operation_id,
            stage,
            code,
            state.scientific_digest,
            state.scientific_digest,
        )
        receipt = FailureReceipt(
            "grcv4-failure-receipt-envelope-v1",
            payload_identity("failure_receipt_identity_payload", identity.to_payload()),
            identity,
        )
        life = state.lifecycle_digest(before.receipts)
        failure = GRCV4Failure(
            stage,
            solver,
            code,
            message,
            state.scientific_digest,
            state.scientific_digest,
            life,
            life,
            receipt,
        )
        result = GRCV4StepResult(
            state.inputs.step_index,
            state.inputs.time,
            (),
            {},
            state.inputs.geometry.reference.profile.complete_profile_id,
            state.model_identity,
            "rejected",
            solver,
            False,
            None,
            failure,
            (receipt,),
        )
        _bind_result(result, request, state, state, before.receipts)
        return result

    def reset(self):
        return self._administrative("reset")

    def rebase(self):
        return self._administrative("rebase")

    def _administrative(self, kind):
        with (
            self._lock,
            exact_backend(self._backend_choice),
            numerical_policy(self._policy),
        ):
            published = self._published
            before = published.state
            inputs = replace(
                before.inputs,
                operation_id=kind + ":" + before.lifecycle_digest(published.receipts),
            )
            following = generic._fresh_geometry(
                replace(
                    inputs,
                    **(
                        {"current": inputs.reset}
                        if kind == "reset"
                        else {"reset": inputs.current}
                    ),
                )
            )
            _, charge = generic._readmit_state(following, _backend(before))
            after = type(before)(following, before.specialization)
            source = type(before)(inputs, before.specialization)
            payloads = _payloads(source, after, charge, published.receipts)
            payloads[0] = {
                "schema_version": "grcv4-" + kind + "-receipt-v1",
                "core": payloads[0]["core"],
                **(
                    {"reset_baseline_digest": before.reset_digest}
                    if kind == "reset"
                    else {
                        "old_reset_digest": before.reset_digest,
                        "new_reset_digest": after.reset_digest,
                    }
                ),
            }
            _, emitted = make_commit_receipts(
                payloads,
                operation_id=inputs.operation_id,
                source_state_digest=before.scientific_digest,
                target_state_digest=after.scientific_digest,
                target_step_index=after.inputs.step_index,
                target_time=after.inputs.time,
            )
            self._publish(published, after, emitted, {"kind": kind})
            return GRCV4LifecycleResult(
                "committed", True, emitted[0].commit_id, None, emitted
            )

    def snapshot(self):
        with self._lock:
            p = self._published
            return canonical_json_bytes(
                {
                    "descriptor_version": _LAYOUT,
                    "family": p.state.FAMILY,
                    "exact_backend": self._backend_choice.value,
                    "numerical_policy": self._policy.value,
                    "initial": self._initial.to_payload(),
                    "state": p.state.to_payload(),
                    "journal": [a.to_dict() for a in p.journal],
                    "receipts": [r.to_payload() for r in p.receipts],
                    "carrier_archives": [a.to_dict() for a in p.archives],
                    "reference_currents": [a.to_dict() for a in p.reference_currents],
                    "lifecycle_digest": p.state.lifecycle_digest(p.receipts),
                }
            )

    @classmethod
    def from_state(cls, snapshot):
        data = decode_canonical_json(snapshot)
        keys = {
            "descriptor_version",
            "family",
            "exact_backend",
            "numerical_policy",
            "initial",
            "state",
            "journal",
            "receipts",
            "carrier_archives",
            "reference_currents",
            "lifecycle_digest",
        }
        if (
            type(data) is not dict
            or set(data) != keys
            or data["descriptor_version"] != _LAYOUT
        ):
            raise ValueError("closed enabled lifecycle snapshot required")
        if data["family"] not in _OWNERS or type(data["journal"]) is not list:
            raise ValueError("unsupported snapshot family/journal")
        with (
            exact_backend(ExactBackend(data["exact_backend"])),
            numerical_policy(NumericalPolicy(data["numerical_policy"])),
        ):
            owner = cls(_decode_state(data["initial"], data["family"]))
            for action in data["journal"]:
                if type(action) is not dict:
                    raise ValueError("invalid journal action")
                kind = action.get("kind")
                if kind in ("step", "expand") and set(action) == {"kind", "request"}:
                    result = (
                        owner.step_v4(
                            GRCV4StepRequestInput.from_payload(action["request"])
                        )
                        if kind == "step"
                        else owner.expand(
                            GRC9V4ExpansionRequestInput.from_payload(action["request"])
                        )
                    )
                elif kind in ("reset", "rebase") and set(action) == {"kind"}:
                    result = owner._administrative(kind)
                else:
                    raise ValueError("unknown or extended lifecycle journal action")
                if not result.committed:
                    raise ValueError("retained successful operation failed replay")
            if owner.snapshot() != canonical_json_bytes(data):
                raise ValueError("mixed lifecycle replay mismatch")
            return owner

    def set_state(self, snapshot):
        # Failed loading cannot alter the live publication or execution policy.
        replacement = type(self).from_state(snapshot)
        with self._lock:
            if (replacement._policy, replacement._backend_choice) != (
                self._policy,
                self._backend_choice,
            ):
                raise ValueError(
                    "set_state cannot silently switch numerical execution policy"
                )
            self._initial = replacement._initial
            self._published = replacement._published

    def duplicate(self):
        return type(self).from_state(self.snapshot())

    def save(self, path):
        Path(path).write_bytes(self.snapshot())

    @classmethod
    def load(cls, path):
        return cls.from_state(Path(path).read_bytes())
