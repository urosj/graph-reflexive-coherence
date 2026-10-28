"""Public GRC9V4 contracts for A/C × OS/CI/PC/CI+PC/RG2b.

These types describe data and operations independently of the installed runtime
scope. Constructing/decoding a configuration is not numerical admission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .grc_9_v4_lifecycle import GRC9V4Specialization
from .grc_9_v4_topology import GRC9V4PortGraph, GRC9V4CandidateADifferentialReference
from .grc_v4_step import SuccessfulReceiptEnvelope
from .grc_v4_certification import NumericalPolicy
from .grc_v4_exact import ExactBackend
from .grc_v4_geometry import GRCV4ReferenceGeometry
from .grc_v4_profile import (
    GRCV4Profile,
    CandidateAParams,
    CandidateCParams,
    OSParams,
    CISolverParams,
    PCParams,
    CIPCParams,
    RG2bParams,
)
from .grc_v4_state import GRCV4AuthoritativeState, GRCV4ResetBaseline, FrozenJSONMap


@dataclass(frozen=True, slots=True)
class GRC9V4Family:
    profile_family_id: str
    candidate: Literal["A", "C"]
    realization: Literal["OS", "CI", "PC", "CI+PC", "RG2b"]
    candidate_parameters: type
    realization_parameters: type
    solve_kind: str
    geometry_read: str
    history_write: str

    @property
    def persistent(self) -> bool:
        return self.realization in ("PC", "CI+PC")

    @property
    def authoritative_fields(self) -> tuple[str, ...]:
        return (
            ("C",)
            + (("W_A",) if self.candidate == "A" else ())
            + (("Z_4",) if self.persistent else ())
        )

    def validate_authority(
        self, value: GRCV4AuthoritativeState, graph: GRC9V4PortGraph
    ) -> None:
        if type(value) is not GRCV4AuthoritativeState:
            raise TypeError("typed authoritative state required")
        n, e = len(graph.live_node_ids), len(graph.edges)
        if (
            len(value.C) != n
            or (value.W_A is not None) != (self.candidate == "A")
            or value.W_A is not None
            and len(value.W_A) != e
            or (value.Z_4 is not None) != self.persistent
            or value.Z_4 is not None
            and len(value.Z_4) != e * e
        ):
            raise ValueError(
                f"{self.profile_family_id} authority requires {self.authoritative_fields} on the declared graph"
            )

    def to_payload(self):
        return dict(
            profile_family_id=self.profile_family_id,
            candidate=self.candidate,
            realization=self.realization,
            authoritative_fields=list(self.authoritative_fields),
            candidate_parameter_schema=self.candidate_parameters.SCHEMA,
            realization_parameter_schema=self.realization_parameters.SCHEMA,
            solve_kind=self.solve_kind,
            geometry_read=self.geometry_read,
            history_write=self.history_write,
        )


_REALIZATIONS = (
    (
        "OS",
        OSParams,
        "predictor_corrector",
        "reference_predictor_then_generated_corrector",
        "candidate_history_only",
    ),
    (
        "CI",
        CISolverParams,
        "joint_current_geometry_root",
        "selected_joint_root",
        "candidate_history_only",
    ),
    (
        "PC",
        PCParams,
        "old_carrier_read",
        "committed_Z_before_writer",
        "one_carrier_write_after_continuity",
    ),
    (
        "CI+PC",
        CIPCParams,
        "joint_root_with_fixed_old_carrier",
        "joint_root_with_old_Z_and_instantaneous_geometry",
        "same_selected_root_candidate_and_carrier_writers",
    ),
    (
        "RG2b",
        RG2bParams,
        "certified_section",
        "realization_section_at_declared_duration",
        "candidate_history_only_no_retained_section",
    ),
)
_FAMILIES = tuple(
    GRC9V4Family(
        c + "_" + r.replace("+", "_"),
        c,
        r,
        cp,
        rp,
        solve,
        read,
        (
            write
            if c == "A"
            else "same_selected_root_carrier_writer"
            if r == "CI+PC"
            else "one_carrier_write_after_continuity"
            if r == "PC"
            else "no_independent_history"
        ),
    )
    for c, cp in (("A", CandidateAParams), ("C", CandidateCParams))
    for r, rp, solve, read, write in _REALIZATIONS
)


def describe_families() -> tuple[GRC9V4Family, ...]:
    """All ten public contracts, independent of tested execution populations."""
    return _FAMILIES


def describe_family(profile_family_id: str) -> GRC9V4Family:
    for family in _FAMILIES:
        if family.profile_family_id == profile_family_id:
            return family
    raise ValueError("unknown GRC9V4 family: " + str(profile_family_id))


@dataclass(frozen=True, slots=True)
class GRC9V4ExecutionOptions:
    exact_backend: ExactBackend
    numerical_policy: NumericalPolicy

    def __post_init__(self):
        object.__setattr__(self, "exact_backend", ExactBackend(self.exact_backend))
        object.__setattr__(
            self, "numerical_policy", NumericalPolicy(self.numerical_policy)
        )

    def to_payload(self):
        return dict(
            exact_backend=self.exact_backend.value,
            numerical_policy=self.numerical_policy.value,
        )


class GRC9V4ExecutionUnavailable(ValueError):
    """The public contract is known; this runtime scope cannot execute it."""

    def __init__(self, family: str, available: tuple[str, ...]):
        self.family = describe_family(family)
        self.available_families = available
        super().__init__(
            f"{family} has a public contract; native lifecycle execution is not enabled in this scope ({', '.join(available)})"
        )


def validate_reference(reference: GRCV4ReferenceGeometry) -> GRC9V4Family:
    if (
        type(reference) is not GRCV4ReferenceGeometry
        or reference.graph.port_graph is None
    ):
        raise TypeError("typed port-owned reference required")
    family = describe_family(reference.profile.identity_payload.profile_family_id)
    params = reference.profile.params_resolved
    if (
        type(params.candidate) is not family.candidate_parameters
        or type(params.realization) is not family.realization_parameters
    ):
        raise ValueError("family/parameter type mismatch")
    if (
        family.candidate == "A"
        and params.candidate.descriptor_backend_id
        != GRC9V4CandidateADifferentialReference(reference.graph.port_graph).identity
    ):
        raise ValueError("Candidate A requires the native fixed-row descriptor")
    return family


def target_references(targets, graph):
    refs = {}
    for target in targets:
        target = GRCV4ReferenceGeometry.from_payload(target.to_payload())
        validate_reference(target)
        if target.graph != graph:
            raise ValueError("initial target registry requires same graph")
        key = target.profile.complete_profile_id
        if key in refs:
            raise ValueError("duplicate target profile")
        refs[key] = target
    return tuple(refs.values())


def _authority_payload(state):
    return {
        k: None if getattr(state, k) is None else list(getattr(state, k))
        for k in ("C", "W_A", "Z_4")
    }


@dataclass(frozen=True, slots=True)
class GRC9V4Configuration:
    """Scientific inputs, not a kernel stage or a caller-computed digest bundle.

    The existing typed profile owns candidate/realization parameters and the
    default request. Current and reset authority are always independent inputs.
    Numerical admission occurs only when an executable model is constructed.
    """

    reference: GRCV4ReferenceGeometry
    specialization: GRC9V4Specialization
    current: GRCV4AuthoritativeState
    reset: GRCV4AuthoritativeState
    budget_target: float
    execution: GRC9V4ExecutionOptions
    step_index: int = 0
    time: float = 0.0
    targets: tuple[GRCV4ReferenceGeometry, ...] = ()

    def __post_init__(self):
        from .grc_v4_state import _number

        family = validate_reference(self.reference)
        if (
            type(self.specialization) is not GRC9V4Specialization
            or type(self.execution) is not GRC9V4ExecutionOptions
        ):
            raise TypeError(
                "typed specialization and explicit execution options required"
            )
        graph = self.reference.graph.port_graph
        family.validate_authority(self.current, graph)
        family.validate_authority(self.reset, graph)
        if type(self.step_index) is not int or not 0 <= self.step_index <= 2**53 - 1:
            raise ValueError("safe nonnegative step index required")
        for key in ("budget_target", "time"):
            v = _number(getattr(self, key))
            if v < 0:
                raise ValueError("nonnegative budget/clock required")
            object.__setattr__(self, key, v)
        object.__setattr__(
            self, "targets", target_references(self.targets, self.reference.graph)
        )

    @property
    def family(self):
        return describe_family(
            self.reference.profile.identity_payload.profile_family_id
        )

    @property
    def profile(self):
        return self.reference.profile

    def to_payload(self):
        return dict(
            schema_version="grc9v4-configuration-v1",
            reference=self.reference.to_payload(),
            specialization=dict(
                resolved=self.specialization.resolved.to_dict(),
                identity_payload=self.specialization.identity_payload.to_dict(),
            ),
            current=_authority_payload(self.current),
            reset=_authority_payload(self.reset),
            budget_target=self.budget_target,
            step_index=self.step_index,
            time=self.time,
            execution=self.execution.to_payload(),
            targets=[t.to_payload() for t in self.targets],
        )

    @classmethod
    def from_payload(cls, value):
        keys = {
            "schema_version",
            "reference",
            "specialization",
            "current",
            "reset",
            "budget_target",
            "step_index",
            "time",
            "execution",
            "targets",
        }
        if (
            type(value) is not dict
            or set(value) != keys
            or value["schema_version"] != "grc9v4-configuration-v1"
        ):
            raise ValueError("closed public configuration required")
        spec = value["specialization"]
        execution = value["execution"]
        if (
            type(spec) is not dict
            or set(spec) != {"resolved", "identity_payload"}
            or type(execution) is not dict
            or set(execution) != {"exact_backend", "numerical_policy"}
            or type(value["targets"]) is not list
        ):
            raise ValueError("closed specialization/execution/targets required")
        for role in ("current", "reset"):
            if type(value[role]) is not dict or set(value[role]) != {"C", "W_A", "Z_4"}:
                raise ValueError("closed authority record required")
        return cls(
            GRCV4ReferenceGeometry.from_payload(value["reference"]),
            GRC9V4Specialization(
                FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])
            ),
            GRCV4AuthoritativeState(**value["current"]),
            GRCV4AuthoritativeState(**value["reset"]),
            value["budget_target"],
            GRC9V4ExecutionOptions(**execution),
            value["step_index"],
            value["time"],
            tuple(GRCV4ReferenceGeometry.from_payload(t) for t in value["targets"]),
        )


@dataclass(frozen=True, slots=True)
class EnabledGRC9V4State:
    port_graph: GRC9V4PortGraph
    profile: GRCV4Profile
    specialization: GRC9V4Specialization
    current: GRCV4AuthoritativeState
    reset: GRCV4ResetBaseline
    step_index: int
    time: float
    budget_target: float
    active_model_identity: str
    scientific_state_digest: str
    lifecycle_digest: str
    receipt_ledger: tuple[SuccessfulReceiptEnvelope, ...]
    branch: Literal["enabled_v4"] = field(default="enabled_v4", init=False)

    @property
    def family(self):
        return describe_family(self.profile.identity_payload.profile_family_id)


@dataclass(frozen=True, slots=True)
class DisabledGRC9V3State:
    """Exact native snapshot bytes; decoded access returns a detached copy.

    No C/W/Z-shaped surrogate is presented for a legacy state. Native JSON
    preserves signed zero; it is deliberately not normalized as V4 JSON.
    """

    delegate_checkpoint: bytes
    target_spec_version: str
    entry_receipt: SuccessfulReceiptEnvelope
    step_index: int
    time: float
    budget_target: float
    active_model_identity: str
    scientific_state_digest: str
    lifecycle_digest: str
    receipt_ledger: tuple[SuccessfulReceiptEnvelope, ...]
    branch: Literal["disabled_grc9v3"] = field(default="disabled_grc9v3", init=False)

    @property
    def delegate_snapshot(self):
        import json

        return json.loads(self.delegate_checkpoint)


GRC9V4ScientificState = EnabledGRC9V4State | DisabledGRC9V3State


@dataclass(frozen=True, slots=True)
class GRC9V4State:
    """Readable scientific state plus the complete replay checkpoint."""

    lifecycle: GRC9V4ScientificState
    checkpoint: bytes

    @property
    def step_index(self):
        return self.lifecycle.step_index

    @property
    def time(self):
        return self.lifecycle.time

    @property
    def budget_target(self):
        return self.lifecycle.budget_target

    @property
    def compatibility_branch(self):
        return self.lifecycle.branch

    @property
    def scientific_state_digest(self):
        return self.lifecycle.scientific_state_digest

    @property
    def active_model_identity(self):
        return self.lifecycle.active_model_identity

    @property
    def remainder(self):
        return None
