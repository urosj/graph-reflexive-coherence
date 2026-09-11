"""Shared generic lifecycle owner, with bounded C_OS mapped transitions.

One immutable lifecycle tuple is published only after numerical admission,
reference restart admission, receipt construction and result binding succeed.
Snapshot/load/reset/rebase, registered C_OS migration and affine events use
that same receiver, including through GRCV4. Full G2 conformance remains separate.
There are no injectable production solvers, commit callbacks or faults.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from pathlib import Path
from fractions import Fraction
from math import isfinite
from threading import Lock
from typing import Any, Self, cast

from .grc_v4 import (
    GRCV4StepRequestInput,
    GRCV4StepRequest,
    MissingV4StepRequest,
    GRCV4MigrationRequest,
    GRCV4MappedTopologyEventRequest,
)
from .grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError
from .grc_v4_candidate_a import CandidateADifferentialReference, CandidateAStageError
from .grc_v4_codec import (
    COS_SNAPSHOT_LAYOUT_ID,
    GENERIC_SNAPSHOT_LAYOUT_ID,
    MIGRATION_SNAPSHOT_LAYOUT_ID,
    INITIALIZER_SNAPSHOT_LAYOUT_ID,
    INITIALIZER_RELEASE_ID,
    RECEIPT_PARENT_POLICY_ID,
    RELEASE_ID,
    V4IdentityError,
    V4SchemaError,
    canonical_json_bytes,
    snapshot_payload,
    decode_canonical_json,
    payload_identity,
)
from .grc_v4_geometry import (
    GRCV4ReferenceGeometry,
    GRCV4Graph,
    GeometryStageInputs,
    GeometryDomainError,
    NonfiniteGeometryError,
    VertexScalar,
    _state_from_payload,
    _computed,
)
from .grc_v4_realizations import OSStageError
from .grc_v4_state import (
    FrozenJSONMap,
    GRCV4LifecycleState,
    GRCV4AuthoritativeState,
    GRCV4LifecycleResult,
    GRCV4ResetBaseline,
    GRCV4StepResult,
    SolverDisposition,
)
from .grc_v4_step import (
    CommitPayload,
    FailureReceipt,
    FailureCode,
    FailureReceiptIdentityPayload,
    GRCV4Failure,
    OperationStage,
    ProvisionalCandidateCOSStep,
    ProvisionalCandidateAOSStep,
    ResourceBoundaryError,
    SuccessfulReceiptEnvelope,
    _RESOURCE_SOLVER_FAILURES,
    _ledger,
    _resource_charge,
    bind_step_result,
    make_commit_receipts,
    negative_duration_result,
)

from .grc_v4_transport import ChargeEvaluation, ChargeDomainError
from .grc_v4_profile import GRCV4Profile


def _fresh_geometry(inputs: GeometryStageInputs) -> GeometryStageInputs:
    """Rebuild derived geometry only; C/W/Z and the reduced reset stay authority."""
    reference = inputs.geometry.reference
    if reference.profile.identity_payload.realization == "PC":
        from .grc_v4_pc import carrier_geometry
        return replace(inputs, geometry=carrier_geometry(inputs, inputs.current))
    return replace(inputs, geometry=reference.geometry())


def _profile_step(inputs: GeometryStageInputs, backend: CandidateADifferentialReference | None) -> Any:
    """Dispatch existing provisional numerical owners, never a second writer."""
    identity = inputs.geometry.reference.profile.identity_payload
    if identity.candidate == "A":
        if type(backend) is not CandidateADifferentialReference:
            raise V4IdentityError("Candidate A requires its explicit differential reference")
    elif backend is not None:
        raise V4IdentityError("Candidate C cannot import Candidate A differential authority")
    if identity.realization == "OS":
        return (ProvisionalCandidateCOSStep(inputs) if identity.candidate == "C"
                else ProvisionalCandidateAOSStep(inputs, backend))
    if identity.realization in ("CI", "CI+PC"):
        from .grc_v4_ci import ProvisionalCandidateCIStep
        return ProvisionalCandidateCIStep(inputs, backend)
    if identity.realization == "PC":
        from .grc_v4_pc import ProvisionalCandidatePCStep
        return ProvisionalCandidatePCStep(inputs, backend)
    if identity.realization == "RG2b":
        from .grc_v4_rg2b import ProvisionalCandidateRG2bStep, RG2bStageError
        try:
            return ProvisionalCandidateRG2bStep(inputs, backend)
        except RG2bStageError as exc:
            # The provisional owner's declaration check precedes its numerical
            # try block. In particular, a decoded positive request can disagree
            # with the frozen completion duration: reject it as input admission.
            raise ResourceBoundaryError("admission", "domain_failure", str(exc)) from exc
    raise V4IdentityError("unimplemented generic lifecycle realization")


def _step_currents(step: Any) -> tuple[Any, Any, str]:
    """Return consumed/read current and freshly reconstructed restart current."""
    realization = step.inputs.geometry.reference.profile.identity_payload.realization
    if realization == "OS":
        # C_OS historically checks restart separately; retain that postcondition.
        restart = (CandidateCCurrent(replace(step.next_inputs, dt=0))
                   if type(step) is ProvisionalCandidateCOSStep else step.restart)
        return (step.os_pass.corrector if step.os_pass is not None else restart,
                restart, "os_corrector")
    if realization in ("CI", "CI+PC"):
        return step.root, step.restart, "ci_selected_root"
    if realization == "PC":
        return step.read.point, step.restart.point, "pc_old_history"
    return step.point, step.restart_point, "rg2b_section"


def _readmit_state(
    inputs: GeometryStageInputs, backend: CandidateADifferentialReference | None,
) -> tuple[Any, ChargeEvaluation]:
    """Read current/reset authority without imposing eligibility for a new beat.

    RG2b publishes in K, while its ordinary entry (including a zero step)
    requires K_minus. A section/native-current read on K is not another step.
    Other realizations retain their existing zero-writer readmission path.
    No derived section, solver work or geometry becomes lifecycle authority.
    """
    inputs = replace(inputs, dt=0)
    ref = inputs.geometry.reference
    if ref.profile.identity_payload.realization != "RG2b":
        step = _profile_step(inputs, backend)
        return _step_currents(step)[1], step.resource.charge
    from .grc_v4_rg2b import CandidateRG2bSection
    from .grc_v4_candidate_a import CandidateACurrent

    charge = _resource_charge(inputs, VertexScalar(ref.graph, inputs.current.C), "admission")
    _resource_charge(inputs, VertexScalar(ref.graph, inputs.reset.C), "admission")

    def native(state: GRCV4AuthoritativeState) -> Any:
        section = CandidateRG2bSection(replace(inputs, current=state), backend)
        selected = replace(section.inputs, geometry=section.geometry, stage="rg2b_section")
        return (CandidateACurrent(selected, cast(CandidateADifferentialReference, backend))
                if ref.profile.identity_payload.candidate == "A" else CandidateCCurrent(selected))

    native(inputs.reset)
    return native(inputs.current), charge


def _rg2b_beat(reference: GRCV4ReferenceGeometry) -> float:
    """Read the duration from the active frozen completion, not a new policy."""
    from .grc_v4_rg2b import RG2bDomain
    from .grc_v4_rg2b_graph import EXTENSION, RG2bGraphDomain
    identity = reference.profile.params_resolved.realization.extension_evaluator_id
    domain = RG2bGraphDomain if identity.startswith(EXTENSION) else RG2bDomain
    return domain.from_identity(identity).beat_dt


def _validate_abundance_projection(
    projection: dict[str, Any], *, release_id: str, model_identity: str,
    observed_state_digest: str, stage: str, capability: bool,
    definition: tuple[str, str, str, str, str, str] | None = None,
) -> None:
    """Pure protocol validation, not definition admission or detector execution.

    Production has no admitted definition and never advertises the capability.
    Synthetic tests exercise the numeric protocol using a declared tuple of
    (release, model, definition, detector, stage, value-kind). No public receiver
    accepts this tuple or an injected detector; future admission remains separate.
    """
    if set(projection) != {"abundance", "abundance_status", "abundance_observation"}:
        raise ValueError("invalid abundance projection fields")
    if not all(isinstance(v, str) and v for v in (release_id, model_identity, observed_state_digest, stage)):
        raise ValueError("missing abundance observation context")
    if type(capability) is not bool:
        raise ValueError("invalid abundance capability")
    value = projection["abundance"]
    metadata = projection["abundance_observation"]
    if definition is None:
        if capability or value is not None or metadata is not None or projection["abundance_status"] != "unavailable_no_admitted_definition":
            raise ValueError("no admitted abundance definition")
        return
    if (len(definition) != 6 or definition[0:2] != (release_id, model_identity)
            or definition[4] != stage or definition[5] not in {"count", "nonnegative_number"}
            or not all(isinstance(v, str) and v for v in definition)):
        raise ValueError("unresolved abundance definition context")
    if not capability or projection["abundance_status"] != "available":
        raise ValueError("declared definition cannot downgrade to unavailable")
    if type(value) not in (int, float):
        raise ValueError("abundance must be a finite nonnegative number")
    try:
        finite = isfinite(value)
    except OverflowError:
        finite = False
    if (not finite or value < 0 or (type(value) is int and value > 2**53 - 1)
            or (definition[5] == "count" and (value > 2**53 - 1 or value % 1 != 0))):
        raise ValueError("invalid abundance numeric value")
    if type(metadata) is not dict or metadata != {
        "definition_id": definition[2], "detector_id": definition[3],
        "stage": stage, "observed_state_digest": observed_state_digest,
        "model_identity": model_identity,
    }:
        raise ValueError("stale or invalid abundance observation metadata")


def _public_observables(
    inputs: GeometryStageInputs,
    ledger: tuple[SuccessfulReceiptEnvelope, ...],
    charge: ChargeEvaluation,
    current: Any,
    *,
    stage: str,
    current_stage: str,
    solver: SolverDisposition | None,
    consumed: bool,
) -> dict[str, Any]:
    """Detached projections; no new scientific state or retained solver cache.

    P9-4.9.1a admits availability semantics, not a numeric V4 definition.
    No detector is advertised or run; no basin/charge proxy is inferred.
    """
    ref = inputs.geometry.reference
    identity = ref.profile.identity_payload
    abundance = {"abundance": None, "abundance_status": "unavailable_no_admitted_definition",
                 "abundance_observation": None}
    _validate_abundance_projection(
        abundance, release_id=RELEASE_ID, model_identity=ref.profile.complete_profile_id,
        observed_state_digest=inputs.scientific_state_id, stage=stage, capability=False,
    )
    return {
        "stage": stage,
        "budget_current": charge.actual,
        "budget_error": charge.residual,
        "num_nodes": len(ref.graph.live_node_ids),
        "num_edges": len(ref.graph.oriented_edges),
        **abundance,
        "complete_profile_id": ref.profile.complete_profile_id,
        "candidate_id": identity.candidate,
        "realization_id": identity.realization,
        "charge_target": charge.target,
        "charge_current": charge.actual,
        "charge_error": charge.residual,
        "solver_disposition": solver,
        "authoritative_current": {
            "stage": current_stage,
            "consumed_by_continuity": consumed,
            "values": list(current.current.values),
        },
        "geometry_profile_id": identity.geometry_profile_id,
        "receipt_ledger": [r.to_payload() for r in ledger],
        "support_status": "local_" + identity.profile_family_id + "_execution_not_G2_acceptance",
    }


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
        if isinstance(current, (CandidateCStageError, CandidateAStageError)):
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
                "rederived" if ref.profile.identity_payload.candidate == "C" else "exact_transport",
            ),
            ("carrier", "no_persistent_carrier_v1", "not_applicable")
            if ref.profile.identity_payload.realization not in ("PC", "CI+PC")
            else ("carrier", "identity_carrier_coordinates_v1", "exact_transport"),
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
    charge: ChargeEvaluation,
    ledger: tuple[SuccessfulReceiptEnvelope, ...],
) -> list[dict[str, Any]]:
    """Actual ordinary-operation receipts, with no event or history transport.

    The universal core's resource transform identifies unchanged vertex
    placement (identity, no event increment), not the nonlinear continuity
    map. Source/target authority binds the actual resource write. The history
    bundle names identity coordinate placement for retained W/Z (not an
    assertion that a writer or reset leaves their values unchanged), C
    rederivation, and absent channels. Actual endpoint authority binds every
    writer/reset value. No topology/history-map execution is claimed. All operations use
    the accepted previous-successful-primary policy, including auxiliaries.
    """
    ref = before.geometry.reference
    channels, references = _receipt_context(ref)
    parent = None if not ledger else ledger[-4].receipt_id
    core: dict[str, Any] = {
        "operation_id": before.operation_id,
        **references,
        "actual_charge_delta": _computed(
            float(
                Fraction(charge.actual)
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
            **charge.receipt_values(),
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
    reference: GRCV4ReferenceGeometry
    transitions: tuple[FrozenJSONMap, ...] = ()


def _state_inputs(
    reference: GRCV4ReferenceGeometry,
    state: GRCV4LifecycleState,
    operation_id: str = "lifecycle_readmission",
) -> GeometryStageInputs:
    return _fresh_geometry(GeometryStageInputs(
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
    ))


class _CrossingFailure(ValueError):
    def __init__(
        self,
        stage: OperationStage,
        code: FailureCode,
        message: str,
    ) -> None:
        super().__init__(message)
        self.stage, self.code = stage, code


_CrossingRequest = GRCV4MigrationRequest | GRCV4MappedTopologyEventRequest


def _reference_key(ref: GRCV4ReferenceGeometry) -> tuple[str, str]:
    return ref.profile.complete_profile_id, ref.graph.graph_digest


def _reference_registry(references: object, *, generic: bool = False) -> tuple[GRCV4ReferenceGeometry, ...]:
    if type(references) not in (tuple, list) or not references:
        raise V4SchemaError("expected a nonempty ordered reference registry")
    rows: list[GRCV4ReferenceGeometry] = []
    seen: set[tuple[str, str]] = set()
    for value in cast(list[Any], references):
        ref = GRCV4ReferenceGeometry.from_payload(
            value.to_payload() if type(value) is GRCV4ReferenceGeometry else value
        )
        if not generic and ref.profile.identity_payload.profile_family_id != "C_OS":
            raise V4IdentityError(
                "reference registry supports only bounded C_OS targets"
            )
        key = _reference_key(ref)
        if key in seen:
            raise V4IdentityError("duplicate or ambiguous profile/graph reference")
        rows.append(ref)
        seen.add(key)
    return tuple(rows)


def _resolve_reference(
    registry: tuple[GRCV4ReferenceGeometry, ...], profile: str, graph: str
) -> GRCV4ReferenceGeometry:
    for ref in registry:
        if _reference_key(ref) == (profile, graph):
            return ref
    raise _CrossingFailure(
        "admission",
        "unsupported_profile",
        "target profile/graph has no registered complete reference",
    )


def _backend_registry(values: object, references: tuple[GRCV4ReferenceGeometry, ...]) -> tuple[CandidateADifferentialReference, ...]:
    if type(values) not in (list, tuple):
        raise V4SchemaError("differential registry requires an ordered array")
    result: list[CandidateADifferentialReference] = []
    for value in values:
        backend = CandidateADifferentialReference.from_payload(
            value.to_payload() if type(value) is CandidateADifferentialReference else value)
        if any(row.identity == backend.identity for row in result):
            raise V4IdentityError("duplicate differential recipe")
        if not any(ref.profile.identity_payload.candidate == "A"
                   and ref.profile.params_resolved.candidate.descriptor_backend_id == backend.identity
                   and ref.graph == backend.graph and ref.edge_weights == backend.reference_weights
                   for ref in references):
            raise V4IdentityError("differential recipe has no matching registered target")
        result.append(backend)
    return tuple(result)


class _CrossingDeclarationError(V4IdentityError):
    """An explicitly unsupported declaration at the lifecycle admission owner."""


def _backend_for(reference: GRCV4ReferenceGeometry, backends: tuple[CandidateADifferentialReference, ...]) -> CandidateADifferentialReference | None:
    if reference.profile.identity_payload.candidate == "C":
        return None
    identity = reference.profile.params_resolved.candidate.descriptor_backend_id
    for backend in backends:
        if backend.identity == identity:
            if backend.graph != reference.graph or backend.reference_weights != reference.edge_weights:
                raise _CrossingDeclarationError("Candidate A target differential graph/weights mismatch")
            return backend
    raise _CrossingDeclarationError("Candidate A reference has no registered differential recipe")


def _crossing_declaration(reference: GRCV4ReferenceGeometry) -> None:
    """Classify unsupported dispatch declarations before constructing numerics.

    These are the existing owners' supported declaration IDs, not a numerical
    admission proof. Their domain/solver checks still run. Unexpected exceptions
    from those constructors must not be relabeled as scientific negatives.
    """
    from .grc_v4_candidate_a import A_SITE_POTENTIAL, ADMITTED_HISTORY_POLICIES
    from .grc_v4_candidate_c import _fixed_current_policy

    profile = reference.profile
    identity, params = profile.identity_payload, profile.params_resolved
    common, candidate, realization = params.common, params.candidate, params.realization
    if (common.domain_id != "fixed_graph_strict_gap_spd_v1"
            or common.gauge_id != "component_zero_mean_potential_v1"
            or common.normalization_id != "unnormalized_vertex_stiffness_v1"
            or common.measure_profile_id != "unit_vertex_measure_v1"
            or identity.charge_profile_id != "unit_vertex_measure_v1"
            or identity.realization != "RG2b" and not _fixed_current_policy(profile)):
        raise _CrossingDeclarationError("unsupported crossing current/charge declaration")
    if identity.candidate == "A":
        if candidate.site_potential_id != A_SITE_POTENTIAL:
            raise _CrossingDeclarationError("unsupported A potential declaration")
    elif (candidate.potential_evaluator_id != "quadratic_site_potential_zero_derivative_v1"
          or candidate.current_conditioning_policy_id != "strict_invertible_current_block_v1"):
        raise _CrossingDeclarationError("unsupported C potential/conditioning declaration")
    if identity.realization == "OS" and (
        realization.predictor_policy_id != "reference_geometry_predictor_v1"
        or realization.corrector_policy_id != "one_fresh_geometry_corrector_v1"
        or realization.split_residual_norm_id != "edge_l2_v1"
        or identity.candidate == "A" and params.lifecycle.history_policy_id not in ADMITTED_HISTORY_POLICIES
    ):
        raise _CrossingDeclarationError("unsupported crossing OS declaration")


def _snapshot_layout(reference: GRCV4ReferenceGeometry, registry: tuple[GRCV4ReferenceGeometry, ...], transitions: object) -> str:
    from .grc_v4_initializer import HISTORY_POLICY
    if any(ref.profile.params_resolved.lifecycle.history_policy_id == HISTORY_POLICY for ref in registry):
        return INITIALIZER_SNAPSHOT_LAYOUT_ID
    if any(ref.profile.identity_payload.profile_family_id != "C_OS" for ref in registry) and (len(registry) > 1 or transitions):
        return MIGRATION_SNAPSHOT_LAYOUT_ID
    return (COS_SNAPSHOT_LAYOUT_ID if reference.profile.identity_payload.profile_family_id == "C_OS"
            else GENERIC_SNAPSHOT_LAYOUT_ID)


def _readmit_crossing(inputs: GeometryStageInputs, stage: OperationStage,
                      backends: tuple[CandidateADifferentialReference, ...] = ()) -> None:
    from .grc_v4_ci import CIStageError
    from .grc_v4_rg2b import RG2bStageError

    try:
        _crossing_declaration(inputs.geometry.reference)
        _readmit_state(_fresh_geometry(inputs), _backend_for(inputs.geometry.reference, backends))
    except (ResourceBoundaryError, CandidateCStageError, CandidateAStageError,
            CIStageError, RG2bStageError, OSStageError, GeometryDomainError,
            NonfiniteGeometryError, _CrossingDeclarationError) as exc:
        raise _CrossingFailure(
            stage,
            "target_readmission_failure"
            if stage == "target_readmission"
            else "domain_failure",
            str(exc),
        ) from exc


def _history_bundle(
    request: _CrossingRequest,
    source: GRCV4ReferenceGeometry,
    target: GRCV4ReferenceGeometry,
) -> dict[str, Any]:
    bundle = request.history_policy.to_payload()
    allowed = {
        "candidate": {
            source.profile.params_resolved.lifecycle.history_policy_id,
            target.profile.params_resolved.lifecycle.history_policy_id,
            "candidate_c_rederive_no_history_v1",
        },
        "carrier": {"no_persistent_carrier_v1", "carrier_not_applicable_v1"},
    }
    for subject, disposition in (
        ("candidate", "rederived"),
        ("carrier", "not_applicable"),
    ):
        row = cast(dict[str, Any], bundle[subject])
        if (
            row["subject"] != subject
            or row["disposition"] != disposition
            or row["policy_id"] not in allowed[subject]
            or row["source_history_digest"] is not None
            or row["target_initializer_id"] is not None
            or row["information_loss"] != "none"
        ):
            raise _CrossingFailure(
                "admission",
                "invalid_migration"
                if type(request) is GRCV4MigrationRequest
                else "invalid_topology_event",
                "C_OS requires candidate rederivation and an absent carrier without invented history",
            )
    return cast(dict[str, Any], bundle)


def _crossing_references(
    request: _CrossingRequest, source: GRCV4ReferenceGeometry
) -> dict[str, str]:
    if type(request) is GRCV4MappedTopologyEventRequest:
        transform = request.resource_transform.to_payload()
        resource_id = payload_identity(
            "resource_transform_identity_payload",
            {
                "schema_version": "grcv4-resource-transform-identity-v1",
                "transform": transform,
            },
        )
    else:
        _, ids = _receipt_context(source)
        resource_id = ids["resource_transform_digest"]
    return {
        "resource_transform_digest": resource_id,
        "history_bundle_digest": payload_identity(
            "history_bundle_identity_payload",
            {
                "schema_version": "grcv4-history-bundle-identity-v1",
                "history_bundle": request.history_policy.to_payload(),
            },
        ),
    }


class ResourceTransformDimensionError(ValueError):
    """Semantic shape diagnostic, distinct from wire and operation errors."""

    diagnostic = "resource_transform_dimension_mismatch"


def _validate_resource_transform_dimensions(transform: Any) -> None:
    # Decode/schema validation precedes this semantic boundary. The matrix is
    # target-by-source; an admissible shape does not admit a graph or event.
    from .grc_v4 import ResolvedResourceEventTransform

    if type(transform) is not ResolvedResourceEventTransform:
        raise TypeError("expected a decoded resource transform")
    n, m = len(transform.source_vertex_ids), len(transform.target_vertex_ids)
    if (len(transform.row_major_coefficients) != m * n
            or len(transform.target_increment) != m):
        raise ResourceTransformDimensionError(ResourceTransformDimensionError.diagnostic)


def _affine_resource(
    request: GRCV4MappedTopologyEventRequest,
    before: GeometryStageInputs,
    target: GRCV4ReferenceGeometry,
    resource: tuple[float, ...],
) -> GRCV4AuthoritativeState:
    transform = request.resource_transform
    source_ids = before.geometry.reference.graph.live_node_ids
    target_ids = target.graph.live_node_ids
    n, m = len(source_ids), len(target_ids)
    # These exact orders are part of the map's type. Unit vertex measures are
    # fixed by the admitted receiver; no row normalization or implicit reorder.
    try:
        _validate_resource_transform_dimensions(transform)
    except ResourceTransformDimensionError as exc:
        raise _CrossingFailure("admission", "invalid_topology_event", exc.diagnostic) from exc
    if (
        tuple(transform.source_vertex_ids) != source_ids
        or tuple(transform.target_vertex_ids) != target_ids
    ):
        raise _CrossingFailure(
            "admission",
            "invalid_topology_event",
            "affine map orders or dimensions differ from the live graphs",
        )
    coefficients = tuple(Fraction(x) for x in transform.row_major_coefficients)
    if any(
        sum((coefficients[i * n + j] for i in range(m)), Fraction()) != 1
        for j in range(n)
    ):
        raise _CrossingFailure(
            "admission",
            "invalid_topology_event",
            "affine linear part does not transport the exact unit charge form",
        )
    try:
        mapped = tuple(
            _computed(
                float(
                    sum(
                        (
                            coefficients[i * n + j] * Fraction(resource[j])
                            for j in range(n)
                        ),
                        Fraction(transform.target_increment[i]),
                    )
                )
            )
            for i in range(m)
        )
    except (OverflowError, NonfiniteGeometryError) as exc:
        raise _CrossingFailure(
            "target_construction",
            "nonfinite_value",
            "affine resource output is nonfinite",
        ) from exc
    if any(x < 0 for x in mapped):
        raise _CrossingFailure(
            "target_construction",
            "domain_failure",
            "affine resource output is negative",
        )
    return GRCV4AuthoritativeState(mapped, None, None)


def _map_crossing(
    before: GeometryStageInputs,
    request: _CrossingRequest,
    target: GRCV4ReferenceGeometry,
    initializer_pair: dict | None = None,
) -> GeometryStageInputs:
    source = before.geometry.reference
    if initializer_pair is not None and not (
        type(request) is GRCV4MigrationRequest
        and source.profile.identity_payload.candidate == "C"
        and target.profile.identity_payload.candidate == "A"
    ):
        raise _CrossingFailure("admission", "invalid_migration", "extraneous initializer pair")
    if request.source_state_digest != before.scientific_state_id:
        raise _CrossingFailure(
            "admission",
            "invalid_identity",
            "request does not bind the live scientific state",
        )
    if request.target_profile_id != target.profile.complete_profile_id:
        raise _CrossingFailure(
            "admission",
            "unsupported_profile",
            "request target differs from the resolved profile",
        )
    legacy = (source.profile.identity_payload.profile_family_id == "C_OS"
              and target.profile.identity_payload.profile_family_id == "C_OS")
    if type(request) is GRCV4MappedTopologyEventRequest and not legacy:
        raise _CrossingFailure("admission", "unsupported_profile", "non-C_OS events require P9-7.2b")
    if type(request) is GRCV4MappedTopologyEventRequest or legacy:
        _history_bundle(request, source, target)
    if type(request) is GRCV4MigrationRequest:
        if source.graph != target.graph:
            raise _CrossingFailure(
                "admission",
                "invalid_migration",
                "profile migration cannot change the graph",
            )
        if request.target_context_value:
            raise _CrossingFailure(
                "admission",
                "invalid_migration",
                "target requires constant-zero context",
            )
        if legacy:
            following = replace(before, geometry=target.geometry(), context=target.context)
        else:
            from .grc_v4_migration import map_migration, _map_migration, MigrationAdmissionError
            try:
                following = (map_migration(before, target, request.history_policy) if initializer_pair is None
                             else _map_migration(before, target, request.history_policy, initializer_pair))
            except MigrationAdmissionError as exc:
                raise _CrossingFailure("admission", "invalid_migration", str(exc)) from exc
    else:
        assert isinstance(request, GRCV4MappedTopologyEventRequest)
        if (
            request.source_graph_digest != source.graph.graph_digest
            or canonical_json_bytes(request.target_graph)
            != canonical_json_bytes(target.graph.to_payload())
        ):
            raise _CrossingFailure(
                "admission",
                "invalid_identity",
                "event graph identity differs from its resolved endpoints",
            )
        current = _affine_resource(request, before, target, before.current.C)
        reset = _affine_resource(request, before, target, before.reset.C)
        try:
            source_charge = ChargeEvaluation(
                VertexScalar(source.graph, before.current.C),
                before.Q_target,
                source.profile,
            )
            target_charge = ChargeEvaluation(
                VertexScalar(target.graph, current.C), before.Q_target, target.profile
            )
        except (ChargeDomainError, NonfiniteGeometryError) as exc:
            raise _CrossingFailure(
                "target_construction",
                "charge_failure",
                "event charge evaluation is not finite",
            ) from exc
        delta = Fraction(target_charge.actual) - Fraction(source_charge.actual)
        try:
            receipt_delta = _computed(float(delta))
            new_charge = _computed(float(Fraction(before.Q_target) + delta))
        except (OverflowError, NonfiniteGeometryError) as exc:
            raise _CrossingFailure(
                "target_construction",
                "charge_failure",
                "event charge accounting is unrepresentable",
            ) from exc
        if (
            Fraction(receipt_delta) != delta
            or Fraction(new_charge) != Fraction(before.Q_target) + delta
        ):
            raise _CrossingFailure(
                "target_construction",
                "charge_failure",
                "event charge accounting loses a nonzero delta",
            )
        if new_charge < 0:
            raise _CrossingFailure(
                "target_construction",
                "charge_failure",
                "event charge target is negative",
            )
        following = replace(
            before,
            geometry=target.geometry(),
            context=target.context,
            current=current,
            reset=reset,
            Q_target=new_charge,
        )
    return _fresh_geometry(following)


def _prepare_crossing(
    before: GeometryStageInputs,
    request: _CrossingRequest,
    target: GRCV4ReferenceGeometry,
    backends: tuple[CandidateADifferentialReference, ...] = (),
    initializer_pair: dict | None = None,
) -> GeometryStageInputs:
    from .grc_v4_pc import PCStageError

    try:
        following = _map_crossing(before, request, target, initializer_pair)
    except _CrossingFailure:
        raise
    except (GeometryDomainError, NonfiniteGeometryError, PCStageError) as exc:
        # Target geometry reconstruction can fail before numerical readmission,
        # including removal of the immediate CI path from a persistent state.
        raise _CrossingFailure("target_construction", "domain_failure", str(exc)) from exc
    if initializer_pair is None:
        _readmit_crossing(before, "pre_read_reconstruction", backends)
    # Provisional admission checks current AND reset at the target reference.
    _readmit_crossing(following, "target_readmission", backends)
    return following


def _crossing_receipts(
    before: GeometryStageInputs,
    after: GeometryStageInputs,
    request: _CrossingRequest,
    ledger: tuple[SuccessfulReceiptEnvelope, ...],
    initializer_pair: dict | None = None,
) -> list[dict[str, Any]]:
    source, target = before.geometry.reference, after.geometry.reference
    old_charge = ChargeEvaluation(
        VertexScalar(source.graph, before.current.C), before.Q_target, source.profile
    )
    charge = ChargeEvaluation(
        VertexScalar(target.graph, after.current.C), after.Q_target, target.profile
    )
    references = _crossing_references(request, source)
    core: dict[str, Any] = {
        "operation_id": request.operation_id,
        **references,
        "actual_charge_delta": _computed(
            float(Fraction(charge.actual) - Fraction(old_charge.actual))
        ),
        "information_losses": [],
        "disposition": "committed",
        "parent_receipt_ids": [] if not ledger else [ledger[-4].receipt_id],
    }
    for prefix, inputs in (("source", before), ("target", after)):
        ref = inputs.geometry.reference
        core.update(
            {
                prefix + "_state_digest": inputs.scientific_state_id,
                prefix + "_graph_digest": ref.graph.graph_digest,
                prefix + "_model_identity": ref.profile.complete_profile_id,
                prefix + "_reset_digest": inputs.reset_id,
                prefix + "_authoritative_digest": payload_identity(
                    "authoritative_state_identity_payload",
                    {
                        "schema_version": "grcv4-authoritative-state-identity-v1",
                        "authoritative": inputs.scientific_state_preimage[
                            "authoritative"
                        ],
                    },
                ),
            }
        )
    history = {
        "schema_version": "grcv4-history-bundle-receipt-v1",
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
    }
    if type(request) is GRCV4MigrationRequest and not (
        source.profile.identity_payload.profile_family_id == "C_OS"
        and target.profile.identity_payload.profile_family_id == "C_OS"
    ):
        from .grc_v4_migration import history_digest
        for subject in ("candidate", "carrier"):
            channel = getattr(request.history_policy, subject)
            history[subject] = dict(subject=subject, disposition=channel.disposition,
                                    source_history_digest=history_digest(before, subject),
                                    target_history_digest=history_digest(after, subject),
                                    information_loss=channel.information_loss)
        core["information_losses"] = [history[s]["information_loss"] for s in ("candidate", "carrier")
                                      if history[s]["information_loss"] != "none"]
    primary: dict[str, Any] = {
        "schema_version": "grcv4-profile-migration-receipt-v1",
        "core": core,
        "history": history,
    }
    if initializer_pair is not None:
        primary.update(schema_version="grcv4-profile-migration-receipt-v2",
                       initializer_pair_id=initializer_pair["initializer_pair_id"])
    if type(request) is GRCV4MappedTopologyEventRequest:
        primary["schema_version"] = "grcv4-topology-event-receipt-v1"
        primary["event_id"] = payload_identity(
            "mapped_topology_event_identity_payload",
            {
                "schema_version": "grcv4-mapped-topology-event-identity-v1",
                "source_state_digest": before.scientific_state_id,
                "source_graph_digest": source.graph.graph_digest,
                "target_graph_digest": target.graph.graph_digest,
                "target_profile_id": target.profile.complete_profile_id,
                **references,
            },
        )
    return [
        primary,
        {
            "schema_version": "grcv4-charge-receipt-v1",
            "core": core,
            **charge.receipt_values(),
        },
        *(
            {
                "schema_version": "grcv4-history-disposition-receipt-v1",
                "core": core,
                "subject": subject,
                "history_disposition": disposition,
                "information_loss": history[subject]["information_loss"],
            }
            for subject, disposition in ((s, history[s]["disposition"]) for s in ("candidate", "carrier"))
        ),
    ]


@dataclass(frozen=True, slots=True)
class _Crossing:
    request: _CrossingRequest
    before: GeometryStageInputs
    after: GeometryStageInputs
    initializer_pair: dict | None = None


def _archive_inputs(
    registry: tuple[GRCV4ReferenceGeometry, ...],
    scientific: dict[str, Any],
    reset: dict[str, Any],
    operation_id: str,
) -> GeometryStageInputs:
    ref = _resolve_reference(
        registry, scientific["active_model_identity"], scientific["graph_digest"]
    )
    inputs = GeometryStageInputs(
        ref.geometry(),
        ref.context,
        _state_from_payload(scientific["authoritative"]),
        _state_from_payload(reset["authoritative"]),
        operation_id,
        scientific["Q_target"],
        (),
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
            "crossing preimages contradict their embedded reference/reset identity"
        )
    return inputs


def _restore_crossings(
    records: list[Any],
    registry: tuple[GRCV4ReferenceGeometry, ...],
    *,
    readmit: bool = True,
    backends: tuple[CandidateADifferentialReference, ...] = (),
) -> dict[str, _Crossing]:
    result: dict[str, _Crossing] = {}
    for row in records:
        request_data = row["request"]
        kind = request_data.get("schema_version")
        if kind == "grcv4-migration-request-v1":
            request: _CrossingRequest = GRCV4MigrationRequest.from_payload(request_data)
        elif kind == "grcv4-mapped-topology-event-request-v1":
            request = GRCV4MappedTopologyEventRequest.from_payload(request_data)
            if request.metadata:
                raise V4SchemaError(
                    "crossing archive excludes nonauthoritative event metadata"
                )
        else:
            raise V4SchemaError("unsupported crossing declaration in snapshot")
        before = _archive_inputs(
            registry, row["source"], row["source_reset"], request.operation_id
        )
        after = _archive_inputs(
            registry, row["target"], row["target_reset"], request.operation_id
        )
        pair = row.get("initializer_pair")
        if pair is not None and readmit:
            from .grc_v4_initializer import CandidateAReferencePassPair
            _readmit_crossing(before, "pre_read_reconstruction", backends)
            rebuilt = CandidateAReferencePassPair.from_record(pair).to_record()
            if canonical_json_bytes(pair) != canonical_json_bytes(rebuilt):
                raise V4IdentityError("archived initializer pair does not recompute")
        # Live archives have already passed whole-tuple admission before their
        # immutable publication. Imported archives must reconstruct that proof.
        expected = (
            _prepare_crossing(before, request, after.geometry.reference, backends, pair)
            if readmit
            else _map_crossing(before, request, after.geometry.reference, pair)
        )
        if expected.scientific_state_id != after.scientific_state_id:
            raise V4IdentityError(
                "crossing archive does not apply its declared whole-lifecycle map"
            )
        if not isinstance(row["commit_id"], str) or row["commit_id"] in result:
            raise V4IdentityError("duplicate or missing crossing commit identity")
        result[row["commit_id"]] = _Crossing(request, before, after, pair)
    return result


def _check_step_target(before: GeometryStageInputs, after: GeometryStageInputs) -> None:
    """The commit owner checks transition semantics, not just matching hashes."""
    if (
        after.geometry.reference != before.geometry.reference
        or after.context != before.context
        or after.reset != before.reset
        or after.Q_target != before.Q_target
        or after.receipt_ids != before.receipt_ids
        or after.operation_id != before.operation_id
    ):
        raise V4IdentityError("ordinary target replaces lifecycle authority")
    expected_clock = (
        before.step_index + int(before.dt > 0),
        float(Fraction(before.time) + Fraction(before.dt)),
    )
    if (after.step_index, after.time) != expected_clock:
        raise V4IdentityError("ordinary target violates the requested clock transition")
    if before.dt == 0 and after.scientific_state_id != before.scientific_state_id:
        raise V4IdentityError("zero-duration target changes scientific state")


def _restore_commits(
    records: list[Any],
    ledger: tuple[SuccessfulReceiptEnvelope, ...],
    reference: GRCV4ReferenceGeometry,
    Q_target: float,
    reset_digest: str,
    crossings: dict[str, _Crossing] | None = None,
) -> tuple[CommitPayload, ...]:
    """Check content and ordered commit coverage of this receiver's ledger.

    This bounded import does not certify the truth of an externally supplied
    history. Registered crossing preimages reconstruct lifecycle maps;
    alternative parent conventions are not imported here.
    """
    commits: list[CommitPayload] = []
    position = 0
    seen: set[str] = set()
    last_primary: str | None = None
    last_reset: str | None = None
    crossings = {} if crossings is None else crossings
    crossed: list[str] = []
    final_reference, final_charge = reference, Q_target
    if crossings:
        first = next(iter(crossings.values()))
        reference, Q_target = first.before.geometry.reference, first.before.Q_target
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
            "grcv4-profile-migration-receipt-v1",
            "grcv4-profile-migration-receipt-v2",
            "grcv4-topology-event-receipt-v1",
        }:
            raise V4SchemaError("unsupported lifecycle operation in V4 snapshot")
        source_reference = reference
        target_reference = reference
        crossing = crossings.get(commit_id)
        if kind in {
            "grcv4-profile-migration-receipt-v1",
            "grcv4-profile-migration-receipt-v2",
            "grcv4-topology-event-receipt-v1",
        }:
            if crossing is None:
                raise V4IdentityError(
                    "crossing receipt has no reconstruction preimages"
                )
            if (
                crossing.before.geometry.reference != reference
                or crossing.before.Q_target != Q_target
            ):
                raise V4IdentityError(
                    "crossing source breaks ordered profile/charge lineage"
                )
            expected = _crossing_receipts(
                crossing.before, crossing.after, crossing.request, ledger[:position], crossing.initializer_pair
            )
            if canonical_json_bytes(expected) != canonical_json_bytes(
                [r.identity_payload.to_dict() for r in group]
            ):
                raise V4IdentityError(
                    "crossing receipts contradict their reconstructed whole-lifecycle operation"
                )
            if (commit.target_step_index, commit.target_time) != (
                crossing.after.step_index,
                crossing.after.time,
            ):
                raise V4IdentityError(
                    "crossing commit changes its readmitted target clock"
                )
            reference_ids = _crossing_references(crossing.request, reference)
            target_reference = crossing.after.geometry.reference
            Q_target = crossing.after.Q_target
            crossed.append(commit_id)
        else:
            if crossing is not None:
                raise V4IdentityError(
                    "ordinary/administrative commit has foreign crossing preimages"
                )
            _, reference_ids = _receipt_context(reference)
        if commits:
            previous = commits[-1]
            index_delta = commit.target_step_index - previous.target_step_index
            if kind == "grcv4-step-commit-receipt-v1":
                # Assignment, reset and rebase do not write the clock. Ordinary
                # dt=0 keeps both fields; positive binary64 dt increments the
                # index once and adds at least the smallest positive duration.
                valid_clock = (
                    index_delta == 0 and commit.target_time == previous.target_time
                    and commit.source_state_digest == commit.target_state_digest
                ) or (
                    index_delta == 1
                    and commit.target_time >= previous.target_time + 5e-324
                )
                if index_delta == 1 and reference.profile.identity_payload.realization == "RG2b":
                    # Retained clocks decide this contradiction without an
                    # invented origin, trajectory replay or adjacency rule.
                    # Exact input sum, rounded once to binary64; large clocks
                    # may lawfully retain the same represented time.
                    try:
                        expected = float(Fraction(previous.target_time) + Fraction(_rg2b_beat(reference)))
                    except OverflowError as exc:
                        raise V4IdentityError("historical RG2b clock overflow") from exc
                    valid_clock = isfinite(expected) and commit.target_time == expected
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
        expected_parent = last_primary
        if core["parent_receipt_ids"] != (
            [] if expected_parent is None else [expected_parent]
        ):
            raise V4IdentityError(
                "snapshot violates the accepted previous-successful-primary parent convention"
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
        for prefix, endpoint in (
            ("source", source_reference),
            ("target", target_reference),
        ):
            if (core[prefix + "_graph_digest"], core[prefix + "_model_identity"]) != (
                endpoint.graph.graph_digest,
                endpoint.profile.complete_profile_id,
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
        policy = target_reference.profile.params_resolved.charge
        bound = Fraction(policy.absolute_tolerance) + Fraction(
            policy.relative_tolerance
        ) * max(abs(Fraction(Q_target)), Fraction(1))
        try:
            residual = float(delta)
        except OverflowError:
            raise V4IdentityError("unrepresentable receipted charge residual") from None
        if actual < 0 or abs(delta) > bound or residual != charge["residual"]:
            raise V4IdentityError("charge receipt is outside its declared admission")
        channels = (primary["history"] if crossing is not None else
                    _receipt_context(reference)[0])
        for receipt, subject, disposition in zip(
            group[2:],
            ("candidate", "carrier"),
            tuple(channels[s]["disposition"] for s in ("candidate", "carrier")),
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
                channels[subject]["information_loss"],
            ):
                raise V4IdentityError("snapshot invents candidate/carrier history")
        if crossing is None and core["information_losses"]:
            raise V4IdentityError("ordinary local operations cannot claim topology history loss")
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
        last_primary = group[0].receipt_id
        position += len(group)
        commits.append(commit)
        reference = target_reference
    if tuple(crossed) != tuple(crossings):
        raise V4IdentityError(
            "crossing archive is missing, extra or out of ledger order"
        )
    if reference != final_reference or Q_target != final_charge:
        raise V4IdentityError(
            "final reference/charge differs from the receipted lineage"
        )
    if last_reset is not None and last_reset != reset_digest:
        raise V4IdentityError(
            "ledger reset identity does not match the restored baseline"
        )
    if position != len(ledger):
        raise V4IdentityError("snapshot has receipts without their commit preimages")
    return tuple(commits)


def _validate_scientific_commitments(
    ledger: tuple[SuccessfulReceiptEnvelope, ...],
    commits: tuple[CommitPayload, ...],
    known_states: tuple[dict[str, Any], ...],
) -> None:
    """One scientific identity cannot carry conflicting component commitments.

    Use available preimages, then compare repeated claims even without one.
    This temporary lookup neither requires adjacent states nor attests that an
    external historical computation occurred. No solver or persistent registry.
    """
    components: dict[str, tuple[str, ...]] = {}
    clocks: dict[str, tuple[int, float]] = {}
    names = ("graph_digest", "model_identity", "authoritative_digest", "reset_digest")
    for scientific in known_states:
        state_id = payload_identity("scientific_state_payload", scientific)
        authority = payload_identity("authoritative_state_identity_payload", {
            "schema_version": "grcv4-authoritative-state-identity-v1",
            "authoritative": scientific["authoritative"],
        })
        value = (scientific["graph_digest"], scientific["active_model_identity"],
                 authority, scientific["reset_digest"])
        if components.setdefault(state_id, value) != value:
            raise V4IdentityError("known scientific preimages contradict component commitments")
        clocks[state_id] = (scientific["step_index"], scientific["time"])
    for receipt in ledger:
        core = cast(FrozenJSONMap, receipt.identity_payload["core"])
        for prefix in ("source", "target"):
            state_id = core[prefix + "_state_digest"]
            value = tuple(core[prefix + "_" + name] for name in names)
            if components.setdefault(state_id, value) != value:
                raise V4IdentityError("receipt commitments contradict one scientific-state identity")
    for commit in commits:
        clock = (commit.target_step_index, commit.target_time)
        if clocks.setdefault(commit.target_state_digest, clock) != clock:
            raise V4IdentityError("commit clock contradicts its scientific-state identity")


def _validate_publication(
    before: GeometryStageInputs,
    after: GeometryStageInputs,
    owned: _OwnedCOS,
    target: GRCV4LifecycleState,
    commit: CommitPayload,
    emitted: tuple[SuccessfulReceiptEnvelope, ...],
    registry: tuple[GRCV4ReferenceGeometry, ...],
    transitions: tuple[FrozenJSONMap, ...],
    kind: str,
) -> None:
    """Bind actual endpoints, then apply the same ledger semantics as import.

    Hash/schema validity alone does not establish the operation being published.
    Immutable old archives were admitted when created/imported; this check does
    not rerun numerical solvers or treat historical receipt hashes as testimony.
    """
    expected_administrative = (
        replace(before, current=before.reset)
        if kind == "grcv4-reset-receipt-v1"
        else replace(before, reset=before.current)
        if kind == "grcv4-rebase-receipt-v1"
        else None
    )
    if expected_administrative is not None and after != _fresh_geometry(expected_administrative):
        raise V4IdentityError(
            "administrative target changes undeclared lifecycle authority"
        )
    ledger = _ledger([r.to_dict() for r in owned.state.receipt_ledger])
    if len(emitted) != 4 or emitted[0].identity_payload["schema_version"] != kind:
        raise V4IdentityError("publication has the wrong operation/receipt delta")
    if (
        commit.operation_id,
        commit.source_state_digest,
        commit.target_state_digest,
        commit.target_step_index,
        commit.target_time,
    ) != (
        before.operation_id,
        before.scientific_state_id,
        after.scientific_state_id,
        after.step_index,
        after.time,
    ):
        raise V4IdentityError("publication commit contradicts actual endpoints")
    core = emitted[0].identity_payload["core"]
    assert isinstance(core, FrozenJSONMap)
    for prefix, endpoint in (("source", before), ("target", after)):
        ref = endpoint.geometry.reference
        expected = {
            "state_digest": endpoint.scientific_state_id,
            "graph_digest": ref.graph.graph_digest,
            "model_identity": ref.profile.complete_profile_id,
            "authoritative_digest": payload_identity(
                "authoritative_state_identity_payload",
                {
                    "schema_version": "grcv4-authoritative-state-identity-v1",
                    "authoritative": endpoint.scientific_state_preimage[
                        "authoritative"
                    ],
                },
            ),
            "reset_digest": endpoint.reset_id,
        }
        if any(core[prefix + "_" + name] != value for name, value in expected.items()):
            raise V4IdentityError("publication receipt contradicts actual authority")
    charges = [
        ChargeEvaluation(
            VertexScalar(endpoint.geometry.reference.graph, endpoint.current.C),
            endpoint.Q_target,
            endpoint.geometry.reference.profile,
        )
        for endpoint in (before, after)
    ]
    if core["actual_charge_delta"] != float(
        Fraction(charges[1].actual) - Fraction(charges[0].actual)
    ) or any(
        emitted[1].identity_payload.get(name) != value
        for name, value in charges[1].receipt_values().items()
    ):
        raise V4IdentityError("publication charge receipt contradicts actual resource")
    if target != _lifecycle_state(after, ledger + emitted):
        raise V4IdentityError("publication state contradicts the committed delta")
    commits = owned.commits + (commit,)
    crossings = _restore_crossings(
        [row.to_dict() for row in transitions], registry, readmit=False
    )
    _restore_commits(
        [
            {
                "commit_id": payload_identity("commit_payload", item.to_payload()),
                "payload": item.to_payload(),
            }
            for item in commits
        ],
        ledger + emitted,
        after.geometry.reference,
        after.Q_target,
        after.reset_id,
        crossings,
    )
    _validate_scientific_commitments(
        ledger + emitted, commits,
        (before.scientific_state_preimage, after.scientific_state_preimage,
         *(endpoint.scientific_state_preimage for crossing in crossings.values()
           for endpoint in (crossing.before, crossing.after))),
    )


class GRCV4Operation:
    """Sole generic lifecycle owner, also used by the public GRCV4 facade.

    Fresh construction has an empty ledger. from_state/load restore a complete
    snapshot, including commit preimages. References, current/reset coordinates,
    receipts and commits have no mutable aliases; numerical caches never persist.
    Calls that publish state are serialized, with one immutable pointer swap.
    """

    __slots__ = ("_registry", "_owned", "_lock", "_backends")

    def __init__(
        self,
        initial: GeometryStageInputs,
        *,
        targets: tuple[GRCV4ReferenceGeometry, ...] = (),
        differential_reference: CandidateADifferentialReference | None = None,
        target_differential_references: tuple[CandidateADifferentialReference, ...] = (),
    ) -> None:
        before = GeometryStageInputs.from_payload(initial.to_payload())
        backend = (None if differential_reference is None else
                   CandidateADifferentialReference.from_payload(differential_reference.to_payload()))
        if before.receipt_ids:
            raise ValueError("fresh lifecycle owner cannot import unauthenticated receipts")
        _readmit_state(replace(before, dt=0), backend)
        if type(targets) is not tuple:
            raise TypeError("targets must be an ordered tuple of complete references")
        if type(target_differential_references) is not tuple:
            raise TypeError("target differential references must be an ordered tuple")
        self._registry = _reference_registry((before.geometry.reference, *targets), generic=True)
        self._backends = _backend_registry((() if backend is None else (backend,)) + target_differential_references, self._registry)
        self._owned = _OwnedCOS(
            _lifecycle_state(before, ()), (), before.geometry.reference
        )
        self._lock = Lock()

    @property
    def state(self) -> GRCV4LifecycleState:
        """One recursively immutable observation of the committed tuple."""
        return self._owned.state

    @property
    def reference(self) -> GRCV4ReferenceGeometry:
        return self._reference

    @property
    def _reference(self) -> GRCV4ReferenceGeometry:
        return self._owned.reference

    @property
    def _state(self) -> GRCV4LifecycleState:
        return self._owned.state

    @property
    def _backend(self) -> CandidateADifferentialReference | None:
        # Active backend selection is part of the same reference publication;
        # migrations never mutate a second live backend pointer.
        return _backend_for(self._owned.reference, self._backends)

    def get_state(self) -> GRCV4LifecycleState:
        return self.state

    def snapshot(self) -> dict[str, Any]:
        """Detached, self-contained JSON values; no causal or inspection caches."""
        # Reference, state and archives are one immutable publication.
        owned = self._owned
        inputs = _state_inputs(owned.reference, owned.state)
        snapshot = {
            "schema_version": "grcv4-snapshot-v1",
            "model_family": "GRCV4",
            "implementation_layout_id": COS_SNAPSHOT_LAYOUT_ID,
            "receipt_parent_policy_id": RECEIPT_PARENT_POLICY_ID,
            "specification_release_id": RELEASE_ID,
            "reference_registry": [ref.to_payload() for ref in self._registry],
            "transition_records": [row.to_dict() for row in owned.transitions],
            "reference": owned.reference.to_payload(),
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
        layout = _snapshot_layout(owned.reference, self._registry, owned.transitions)
        snapshot["implementation_layout_id"] = layout
        if layout in (MIGRATION_SNAPSHOT_LAYOUT_ID, INITIALIZER_SNAPSHOT_LAYOUT_ID):
            snapshot["differential_reference_registry"] = [b.to_payload() for b in self._backends]
            if layout == INITIALIZER_SNAPSHOT_LAYOUT_ID:
                snapshot["specification_release_id"] = INITIALIZER_RELEASE_ID
                snapshot["transition_records"] = [dict(row, initializer_pair=row.get("initializer_pair"))
                                                  for row in snapshot["transition_records"]]
        elif layout == GENERIC_SNAPSHOT_LAYOUT_ID:
            backend = _backend_for(owned.reference, self._backends)
            snapshot["differential_reference"] = (
                None if backend is None else backend.to_payload()
            )
        return snapshot

    @classmethod
    def from_state(cls, state: object, params: object = None) -> Self:
        """Full restoration; optional resolved params are an equality assertion.

        This internal receiver accepts its explicit snapshot layout. It is not
        the public common-interface facade or a migration route. No missing
        identity, history, baseline, commit preimage or reference is synthesized.
        """
        data = cast(dict[str, Any], snapshot_payload(state))
        reference = GRCV4ReferenceGeometry.from_payload(data["reference"])
        registry = _reference_registry(data["reference_registry"], generic=True)
        expected_layout = _snapshot_layout(reference, registry, data["transition_records"])
        if data["implementation_layout_id"] != expected_layout:
            raise V4IdentityError("snapshot layout does not match its active profile family")
        values = (data["differential_reference_registry"] if expected_layout in (MIGRATION_SNAPSHOT_LAYOUT_ID, INITIALIZER_SNAPSHOT_LAYOUT_ID) else
                  [] if data.get("differential_reference") is None else [data["differential_reference"]])
        backends = _backend_registry(values, registry)
        backend = _backend_for(reference, backends)
        if _resolve_reference(registry, *_reference_key(reference)) != reference:
            raise V4IdentityError("current reference contradicts the snapshot registry")
        transitions = data["transition_records"]
        crossings = _restore_crossings(transitions, registry, backends=backends)
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
            crossings,
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
        _validate_scientific_commitments(
            ledger, commits,
            (inputs.scientific_state_preimage,
             *(endpoint.scientific_state_preimage for crossing in crossings.values()
               for endpoint in (crossing.before, crossing.after))),
        )
        if commits and (commits[-1].target_step_index, commits[-1].target_time) != (
            inputs.step_index,
            inputs.time,
        ):
            raise V4IdentityError("restored clock differs from the last local commit")
        # Fresh profile/reset/current admission. Derived geometry, roots and
        # sections are reconstructed, never imported as persistent authority.
        # State admission is not ordinary-step entry admission (RG2b K vs K_minus).
        inputs = _fresh_geometry(inputs)
        _readmit_state(inputs, backend)
        target = _lifecycle_state(inputs, ledger)
        publication = _OwnedCOS(
            target,
            commits,
            inputs.geometry.reference,
            tuple(FrozenJSONMap(row) for row in transitions),
        )
        result = cls.__new__(cls)
        result._lock = Lock()
        result._registry = registry
        result._backends = backends
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
        """Assign compatible current authority; clock and lifecycle remain fixed."""
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
            inputs = _state_inputs(self._reference, state)
            _readmit_state(inputs, self._backend)
            ledger = _ledger([r.to_dict() for r in state.receipt_ledger])
            target = _lifecycle_state(inputs, ledger)
            if target != state:
                raise V4IdentityError(
                    "assigned current state has incorrect content digests"
                )
            publication = _OwnedCOS(
                target, live.commits, live.reference, live.transitions
            )
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
            # changes current C/W/Z and retains clock; rebase changes reset only.
            following = (
                replace(before, current=before.reset)
                if kind == "reset"
                else replace(before, reset=before.current)
            )
            following = _fresh_geometry(following)
            _, charge = _readmit_state(following, self._backend)
            payloads = _ordinary_receipts(before, following, charge, ledger)
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
            _validate_publication(
                before,
                following,
                owned,
                target,
                commit,
                emitted,
                self._registry,
                owned.transitions,
                "grcv4-" + kind + "-receipt-v1",
            )
            publication = _OwnedCOS(
                target, owned.commits + (commit,), owned.reference, owned.transitions
            )
            self._owned = publication

    def list_supported_profiles(self) -> frozenset[str]:
        """Locally admitted declarations; not global conformance advertisement."""
        return frozenset(ref.profile.complete_profile_id for ref in self._registry)

    def get_supported_profile(self, complete_profile_id: str) -> GRCV4Profile:
        if type(complete_profile_id) is not str:
            raise TypeError("expected an exact complete-profile identifier")
        for reference in self._registry:
            if reference.profile.complete_profile_id == complete_profile_id:
                return reference.profile
        raise V4IdentityError("unregistered complete-profile identifier")

    def compute_observables(self) -> dict[str, Any]:
        # One immutable capture remains coherent even if another thread commits.
        owned = self._owned
        state, ref = owned.state, owned.reference
        ledger = _ledger([r.to_dict() for r in state.receipt_ledger])
        inputs = _state_inputs(ref, state, "read-only-observation")
        if ref.profile.identity_payload.profile_family_id == "C_OS":
            current = CandidateCCurrent(inputs)
        else:
            current, _ = _readmit_state(inputs, _backend_for(ref, self._backends))
        charge = _resource_charge(
            inputs, VertexScalar(ref.graph, state.current.C), "pre_read_reconstruction"
        )
        observed_stage = ("read_only_reference" if ref.profile.identity_payload.realization == "OS"
                          else "read_only_" + ref.profile.identity_payload.realization.lower().replace("+", "_"))
        result = _public_observables(
            inputs, ledger, charge, current, stage=observed_stage,
            current_stage=observed_stage, solver=None, consumed=False,
        )
        # Same serializable, recursively owned domain as successful results.
        return FrozenJSONMap(result).to_dict()

    def migrate_profile(self, request: GRCV4MigrationRequest) -> GRCV4LifecycleResult:
        if type(request) is not GRCV4MigrationRequest:
            raise TypeError("expected a typed migration request")
        request = GRCV4MigrationRequest.from_payload(request.to_payload())
        with self._lock:
            return self._crossing(request)

    def apply_topology_event(
        self, request: GRCV4MappedTopologyEventRequest
    ) -> GRCV4LifecycleResult:
        if type(request) is not GRCV4MappedTopologyEventRequest:
            raise TypeError("expected a typed generic mapped-event request")
        request = GRCV4MappedTopologyEventRequest.from_payload(request.to_payload())
        with self._lock:
            return self._crossing(request)

    def _crossing(self, request: _CrossingRequest) -> GRCV4LifecycleResult:
        owned = self._owned
        before = _state_inputs(owned.reference, owned.state, request.operation_id)
        ledger = _ledger([r.to_dict() for r in owned.state.receipt_ledger])
        try:
            if type(request) is GRCV4MappedTopologyEventRequest and owned.reference.profile.identity_payload.profile_family_id != "C_OS":
                raise _CrossingFailure("admission", "unsupported_profile", "non-C_OS events require P9-7.2b")
            if request.source_state_digest != before.scientific_state_id:
                raise _CrossingFailure(
                    "admission",
                    "invalid_identity",
                    "request is stale or foreign to the live state",
                )
            graph_digest = owned.reference.graph.graph_digest
            if type(request) is GRCV4MappedTopologyEventRequest:
                if request.source_graph_digest != graph_digest:
                    raise _CrossingFailure(
                        "admission",
                        "invalid_identity",
                        "event source graph differs from the live graph",
                    )
                try:
                    graph_digest = GRCV4Graph.from_payload(
                        request.target_graph
                    ).graph_digest
                except ValueError as exc:
                    raise _CrossingFailure(
                        "admission", "invalid_topology_event", str(exc)
                    ) from exc
            target_ref = _resolve_reference(
                self._registry, request.target_profile_id, graph_digest
            )
            if type(request) is GRCV4MappedTopologyEventRequest and target_ref.profile.identity_payload.profile_family_id != "C_OS":
                raise _CrossingFailure("admission", "unsupported_profile", "non-C_OS events require P9-7.2b")
            pair = None
            if (type(request) is GRCV4MigrationRequest
                    and owned.reference.profile.identity_payload.candidate == "C"
                    and target_ref.profile.identity_payload.candidate == "A"):
                from .grc_v4_initializer import CandidateAReferencePassPair, InitializerStageError
                from .grc_v4_migration import migration_history_policy, MigrationAdmissionError
                _readmit_crossing(before, "pre_read_reconstruction", self._backends)
                try:
                    if request.history_policy != migration_history_policy(before, target_ref):
                        raise MigrationAdmissionError("initializer migration history policy mismatch")
                    _crossing_declaration(target_ref)
                    backend = _backend_for(target_ref, self._backends)
                except (MigrationAdmissionError, _CrossingDeclarationError) as exc:
                    raise _CrossingFailure("admission", "invalid_migration", str(exc)) from exc
                try:
                    pair = CandidateAReferencePassPair.construct(
                        target_ref, backend, before.current.C, before.reset.C).to_record()
                except InitializerStageError as exc:
                    raise _CrossingFailure("target_construction", "domain_failure", str(exc)) from exc
            following = _prepare_crossing(before, request, target_ref, self._backends, pair)
        except _CrossingFailure as exc:
            identity_payload = FailureReceiptIdentityPayload(
                "grcv4-failure-receipt-v1",
                request.operation_id,
                exc.stage,
                exc.code,
                before.scientific_state_id,
                before.scientific_state_id,
            )
            receipt = FailureReceipt(
                "grcv4-failure-receipt-envelope-v1",
                payload_identity(
                    "failure_receipt_identity_payload", identity_payload.to_payload()
                ),
                identity_payload,
            )
            failure = GRCV4Failure(
                exc.stage,
                None,
                exc.code,
                str(exc),
                before.scientific_state_id,
                before.scientific_state_id,
                before.source_lifecycle_id,
                before.source_lifecycle_id,
                receipt,
            )
            return GRCV4LifecycleResult("rejected", False, None, failure, (receipt,))
        # Everything below is internal content/result preparation. Unexpected
        # errors propagate with the old whole publication intact.
        if following != _map_crossing(before, request, target_ref, pair):
            raise V4IdentityError(
                "crossing target contradicts its declared lifecycle map"
            )
        payloads = _crossing_receipts(before, following, request, ledger, pair)
        commit, emitted = make_commit_receipts(
            payloads,
            operation_id=request.operation_id,
            source_state_digest=before.scientific_state_id,
            target_state_digest=following.scientific_state_id,
            target_step_index=following.step_index,
            target_time=following.time,
        )
        target = _lifecycle_state(following, ledger + emitted)
        result = GRCV4LifecycleResult(
            "committed", True, emitted[0].commit_id, None, emitted
        )
        request_payload = request.to_payload()
        if type(request) is GRCV4MappedTopologyEventRequest:
            request_payload["metadata"] = {}
        archive_payload = {
                "commit_id": emitted[0].commit_id,
                "request": request_payload,
                "source": before.scientific_state_preimage,
                "source_reset": before.reset_preimage,
                "target": following.scientific_state_preimage,
                "target_reset": following.reset_preimage,
            }
        if pair is not None:
            archive_payload["initializer_pair"] = pair
        archive = FrozenJSONMap(archive_payload)
        _validate_publication(
            before,
            following,
            owned,
            target,
            commit,
            emitted,
            self._registry,
            owned.transitions + (archive,),
            ("grcv4-profile-migration-receipt-v2" if pair is not None else "grcv4-profile-migration-receipt-v1")
            if type(request) is GRCV4MigrationRequest
            else "grcv4-topology-event-receipt-v1",
        )
        publication = _OwnedCOS(
            target,
            owned.commits + (commit,),
            target_ref,
            owned.transitions + (archive,),
        )
        self._owned = publication
        return result

    def _inputs(self, request: GRCV4StepRequestInput) -> GeometryStageInputs:
        return replace(_state_inputs(self._reference, self._state, request.operation_id),
                       dt=max(0, request.dt))

    def step_v4(self, request: GRCV4StepRequestInput) -> GRCV4StepResult:
        if type(request) is not GRCV4StepRequestInput:
            raise TypeError("expected decoded external step input")
        request = GRCV4StepRequestInput.from_payload(request.to_payload())
        with self._lock:
            return self._execute(request)

    def step_default(self) -> GRCV4StepResult:
        # Bind default selection and admission to one active profile: migration
        # cannot interleave between reading its parameters and executing it.
        with self._lock:
            default = self._reference.profile.params_resolved.common.default_step_request
            if default is None:
                raise MissingV4StepRequest("active profile has no default_step_request")
            request = GRCV4StepRequest.from_payload(default).to_payload()
            request["schema_version"] = "grcv4-step-request-input-v1"
            return self._execute(GRCV4StepRequestInput.from_payload(request))

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
                    "local lifecycle requires constant-zero context and no external input",
                )
            stage = "pre_read_reconstruction"
            # Rebuild from owned immutable values; caller caches are never inputs.
            stage = "candidate_solve"
            step = _profile_step(before, self._backend)
            solver = "valid_root"
            stage = "final_reconstruction"
            following = step.next_inputs
            _check_step_target(before, following)
            # Final-C at consumed h1 does not establish next-reference admission.
            # This is a read-only commit postcondition, never another OS pass.
            selected, restart, selected_stage = _step_currents(step)
        except (
            ResourceBoundaryError,
            OSStageError,
            CandidateCStageError,
            CandidateAStageError,
            GeometryDomainError,
            NonfiniteGeometryError,
        ) as exc:
            if isinstance(exc, ResourceBoundaryError):
                stage, code = exc.stage, exc.code
                solver = (
                    None
                    if stage in ("admission", "pre_read_reconstruction")
                    else next((disposition for disposition, failure_code in _RESOURCE_SOLVER_FAILURES.items()
                               if failure_code == code), "valid_root")
                    if stage == "candidate_solve"
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
            _ordinary_receipts(before, following, step.resource.charge, ledger),
            operation_id=request.operation_id,
            source_state_digest=before.scientific_state_id,
            target_state_digest=following.scientific_state_id,
            target_step_index=following.step_index,
            target_time=following.time,
        )
        target_ledger = ledger + emitted
        target = _lifecycle_state(following, target_ledger)
        reconstruction_stage = ("commit_reference_readmission"
                                if self._reference.profile.identity_payload.realization == "OS"
                                else "commit_reconstruction")
        observations = _public_observables(
            following, target_ledger, step.resource.charge,
            selected if request.dt > 0 else restart,
            stage="commit", solver="valid_root",
            current_stage=selected_stage if request.dt > 0 else reconstruction_stage,
            consumed=request.dt > 0,
        )
        observations.update({
            "charge": step.resource.charge.receipt_values(),
            "reference_current": {
                "stage": reconstruction_stage,
                "values": list(restart.current.values),
            },
            "continuity_evaluations": step.resource.continuity_evaluations,
        })
        if self._reference.profile.identity_payload.realization != "OS":
            # A CI root, RG2b section or PC carrier geometry is not h_reference.
            observations["reconstructed_current"] = observations.pop("reference_current")
        if getattr(step, "os_pass", None) is not None:
            observations["os"] = {
                "stage": "os_corrector",
                "current": list(step.os_pass.corrector.current.values),
                "split_residual": (
                    None if step.os_pass.residual.values is None
                    else [list(row) for row in step.os_pass.residual.values]
                ),
                "exact_split_residual": [
                    list(row) for row in step.os_pass.residual.exact_values
                ],
                **({"selector_path_segments": step.os_pass.selector_path_segments}
                   if type(step) is ProvisionalCandidateCOSStep else {}),
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
        _validate_publication(
            before,
            following,
            self._owned,
            target,
            commit,
            emitted,
            self._registry,
            self._owned.transitions,
            "grcv4-step-commit-receipt-v1",
        )
        # No fallible validation, serialization or callback follows publication.
        publication = _OwnedCOS(
            target,
            self._owned.commits + (commit,),
            self._owned.reference,
            self._owned.transitions,
        )
        self._owned = publication
        return result


# Historical import spelling; both names resolve to the one publication owner.
CandidateCOSOperation = GRCV4Operation
