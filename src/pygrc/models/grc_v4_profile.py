"""Immutable resolved profile declarations, not executable-profile admission.

All trajectory fields are explicit. Schema/identity consistency is checked here;
graph/SPD/selector/solver-domain admission remains with its runtime owner.
Python equality of these records uses JCS, never loose mapping equality.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from typing import ClassVar, Literal, Self

from .grc_v4_codec import (
    JSONValue, V4IdentityError, V4SchemaError, canonical_json_bytes, decode_canonical_json,
    json_value, payload_identity, validate_payload,
)
from .grc_v4_state import FrozenJSONMap


def _project(value: object) -> JSONValue:
    if isinstance(value, _Record):
        return value.to_payload()
    return json_value(value)


@dataclass(frozen=True, slots=True, eq=False)
class _Record:
    SCHEMA: ClassVar[str] = ""
    INTEGER_FIELDS: ClassVar[tuple[str, ...]] = ()

    def __post_init__(self) -> None:
        # No mutable configuration aliases survive inside any record.
        for member in fields(self):
            value = getattr(self, member.name)
            if isinstance(value, Mapping):
                object.__setattr__(self, member.name, FrozenJSONMap(value))
        validated = validate_payload(self.SCHEMA, self.to_payload())
        # JSON Schema accepts integral floats. Resolve only declared count/
        # integer-constant storage, after domain validation, on BOTH factory
        # and direct construction paths. JCS identities remain unchanged.
        for name in self.INTEGER_FIELDS:
            value = validated[name]
            if (type(value) is not int and type(value) is not float) or value != int(value):
                raise V4SchemaError(f"{name}: expected a validated integer")
            object.__setattr__(self, name, int(value))

    def to_payload(self) -> dict[str, JSONValue]:
        """Project declared public fields only, not dataclass storage helpers."""
        return {member.name: _project(getattr(self, member.name))
                for member in fields(self)}

    @classmethod
    def from_payload(cls, value: object) -> Self:
        data = validate_payload(cls.SCHEMA, value)
        result = object.__new__(cls)
        for member in fields(cls):
            object.__setattr__(result, member.name, data[member.name])
        result.__post_init__()
        return result

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return False
        assert isinstance(other, _Record)
        return canonical_json_bytes(self.to_payload()) == canonical_json_bytes(
            other.to_payload()
        )

    def __hash__(self) -> int:
        return hash(canonical_json_bytes(self.to_payload()))


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4CommonParams(_Record):
    SCHEMA: ClassVar[str] = "common_params"
    schema_version: Literal["grcv4-common-params-v1"]
    differential_backend_id: str
    boundary_policy_id: str
    measure_profile_id: str
    context_contract_id: str
    units_id: str
    gauge_id: str
    normalization_id: str
    domain_id: str
    default_step_request: Mapping[str, object] | None


@dataclass(frozen=True, slots=True, eq=False)
class CandidateAParams(_Record):
    SCHEMA: ClassVar[str] = "candidate_a_params"
    schema_version: Literal["grcv4-candidate-a-params-v1"]
    eta: float
    kappa_c: float
    site_potential_id: str
    W_floor: float
    alpha: float
    beta: float
    gamma: float
    kappa_Ah: float
    chi_A: float
    zeta_A: float
    tau_A: float
    descriptor_backend_id: str
    conductance_evaluator_id: Literal["curvature_disabled_G_W_v1"]


@dataclass(frozen=True, slots=True, eq=False)
class CandidateCParams(_Record):
    SCHEMA: ClassVar[str] = "candidate_c_params"
    schema_version: Literal["grcv4-candidate-c-params-v1"]
    transport_id: Literal["C-HM-STIFFNESS-BASELINE-v1"]
    Lambda_C: float
    selector_boundary_policy_id: Literal["strict_rank_gap_fail_closed_v1"]
    C_ref: float
    kappa_M_C: float
    kappa_Phi_C: float
    eta_C: float
    W_C_tr: Mapping[str, object]
    W_C_tr_content_digest: str
    potential_evaluator_id: str
    tau_C: float
    chi_C: float
    zeta_C: float
    current_conditioning_policy_id: str
    E_H_policy_id: Literal["diag_W_C_tr_structural_hodge_v1"]
    E_M_policy_id: Literal["eta_C_diag_W_C_tr_mobility_v1"]

    def __post_init__(self) -> None:
        _Record.__post_init__(self)
        payload_identity("wctr_identity_payload", {
            "schema_version": "grcv4-wctr-identity-v1",
            "W_C_tr": self.W_C_tr,
        }, expected=self.W_C_tr_content_digest)


@dataclass(frozen=True, slots=True, eq=False)
class GeometryProfileParams(_Record):
    SCHEMA: ClassVar[str] = "geometry_params"
    schema_version: Literal["grcv4-geometry-profile-params-v1"]
    K4_base_digest: str
    reference_hodge_digest: str
    star_cover_id: str
    overlap_normalization_id: str
    candidate_adapter_id: str
    flat_sharp_solver_id: str
    geometry_domain_id: str
    kappa_H: float


@dataclass(frozen=True, slots=True, eq=False)
class CISolverParams(_Record):
    INTEGER_FIELDS: ClassVar[tuple[str, ...]] = ("iteration_limit",)
    SCHEMA: ClassVar[str] = "ci_params"
    schema_version: Literal["grcv4-ci-params-v1"]
    contraction_domain_id: str
    root_selector_id: Literal["unique_admitted_root_v1"]
    iteration_limit: int
    residual_norm_id: str
    tolerance: float


@dataclass(frozen=True, slots=True, eq=False)
class OSParams(_Record):
    SCHEMA: ClassVar[str] = "os_params"
    schema_version: Literal["grcv4-os-params-v1"]
    predictor_policy_id: Literal["reference_geometry_predictor_v1"]
    corrector_policy_id: Literal["one_fresh_geometry_corrector_v1"]
    split_residual_norm_id: str
    tolerance: float


@dataclass(frozen=True, slots=True, eq=False)
class RG2bParams(_Record):
    INTEGER_FIELDS: ClassVar[tuple[str, ...]] = ("iteration_limit",)
    SCHEMA: ClassVar[str] = "rg2b_params"
    schema_version: Literal["grcv4-rg2b-params-v1"]
    extension_evaluator_id: str
    approximation_policy_id: str
    error_norm_id: str
    error_tolerance: float
    containment_certificate_id: str
    iteration_limit: int
    failure_policy_id: Literal["fail_closed_on_uncertified_section_v1"]


@dataclass(frozen=True, slots=True, eq=False)
class PCParams(_Record):
    SCHEMA: ClassVar[str] = "pc_params"
    schema_version: Literal["grcv4-pc-params-v1"]
    tau_PC: float
    radius: float
    carrier_norm_id: str
    source_envelope_id: str
    writer_id: Literal["zero_order_hold_exponential_v1"]


@dataclass(frozen=True, slots=True, eq=False)
class CIPCParams(_Record):
    INTEGER_FIELDS: ClassVar[tuple[str, ...]] = ("iteration_limit", "rho_inst")
    SCHEMA: ClassVar[str] = "cipc_params"
    schema_version: Literal["grcv4-cipc-params-v1"]
    contraction_domain_id: str
    root_selector_id: Literal["unique_admitted_root_v1"]
    iteration_limit: int
    residual_norm_id: str
    tolerance: float
    tau_PC: float
    radius: float
    carrier_norm_id: str
    source_envelope_id: str
    writer_id: Literal["zero_order_hold_exponential_v1"]
    rho_inst: Literal[1]


@dataclass(frozen=True, slots=True, eq=False)
class SolverPolicy(_Record):
    INTEGER_FIELDS: ClassVar[tuple[str, ...]] = ("iteration_limit",)
    SCHEMA: ClassVar[str] = "solver_policy"
    schema_version: Literal["grcv4-solver-policy-v1"]
    solver_kind: Literal["direct", "fixed_point", "newton"]
    root_selector_id: Literal["unique_admitted_root_v1"]
    iteration_limit: int
    conditioning_limit: float
    residual_norm_id: str
    absolute_tolerance: float
    relative_tolerance: float
    failure_policy_id: Literal["fail_closed_no_fallback_v1"]


@dataclass(frozen=True, slots=True, eq=False)
class ChargePolicy(_Record):
    SCHEMA: ClassVar[str] = "charge_policy"
    schema_version: Literal["grcv4-charge-policy-v1"]
    policy_id: Literal["stable_pairwise_binary64_charge_v1"]
    accumulation_order: Literal["canonical_live_vertex_balanced_binary_tree"]
    rounding_mode: Literal["IEEE754_binary64_roundTiesToEven"]
    absolute_tolerance: float
    relative_tolerance: float
    repair_policy: Literal["never_mutate_resource"]
    remainder_policy: Literal["compatibility_projection_is_none"]


@dataclass(frozen=True, slots=True, eq=False)
class LifecyclePolicy(_Record):
    SCHEMA: ClassVar[str] = "lifecycle_policy"
    schema_version: Literal["grcv4-lifecycle-policy-v1"]
    migration_policy_id: Literal["typed_bidirectional_profile_migration_v1"]
    mapped_event_policy_id: Literal["caller_mapped_atomic_topology_event_v1"]
    reset_policy_id: Literal["restore_current_baseline_append_receipt_v1"]
    rebase_policy_id: Literal["replace_baseline_append_receipt_v1"]
    history_policy_id: str
    receipt_policy_id: Literal["operation_delta_plus_persistent_ledger_v1"]
    target_readmission_policy_id: Literal["full_target_fail_closed_v1"]


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4ProfileIdentityPayload(_Record):
    SCHEMA: ClassVar[str] = "profile_identity_payload"
    schema_version: Literal["grcv4-profile-identity-v1"]
    profile_family_id: Literal["A_CI", "C_CI", "A_OS", "C_OS", "A_RG2b", "C_RG2b", "A_PC", "C_PC", "A_CI_PC", "C_CI_PC"]
    candidate: Literal["A", "C"]
    realization: Literal["CI", "OS", "RG2b", "PC", "CI+PC"]
    differential_backend_id: str
    charge_profile_id: str
    geometry_profile_id: str
    context_contract_id: str
    units_id: str
    gauge_id: str
    normalization_id: str
    domain_id: str
    solver_id: str
    lifecycle_policy_id: str
    candidate_c_transport_id: Literal[None, "C-HM-STIFFNESS-BASELINE-v1"]
    composition_gain: float | None
    params_hash: str


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4ResolvedParams(_Record):
    SCHEMA: ClassVar[str] = "resolved_params"
    schema_version: Literal["grcv4-resolved-params-v1"]
    common: GRCV4CommonParams
    candidate: CandidateAParams | CandidateCParams
    realization: CISolverParams | OSParams | RG2bParams | PCParams | CIPCParams
    geometry: GeometryProfileParams
    solver: SolverPolicy
    charge: ChargePolicy
    lifecycle: LifecyclePolicy

    def __post_init__(self) -> None:
        expected = {
            "common": (GRCV4CommonParams,),
            "candidate": (CandidateAParams, CandidateCParams),
            "realization": (CISolverParams, OSParams, RG2bParams, PCParams, CIPCParams),
            "geometry": (GeometryProfileParams,),
            "solver": (SolverPolicy,),
            "charge": (ChargePolicy,),
            "lifecycle": (LifecyclePolicy,),
        }
        for name, classes in expected.items():
            if type(getattr(self, name)) not in classes:
                raise V4SchemaError(f"{name}: expected a typed resolved record")
        _Record.__post_init__(self)

    @classmethod
    def from_payload(cls, value: object) -> Self:
        data = validate_payload(cls.SCHEMA, value)
        result = object.__new__(cls)
        object.__setattr__(result, "schema_version", data["schema_version"])
        for name in ("common", "candidate", "realization", "geometry",
                     "solver", "charge", "lifecycle"):
            section = data[name]
            if not isinstance(section, dict):
                raise V4SchemaError(f"{name}: expected a parameter object")
            record_class = _PARAMETER_CLASSES.get(str(section["schema_version"]))
            if record_class is None:
                raise V4SchemaError("unknown parameter record version")
            object.__setattr__(result, name, record_class.from_payload(section))
        result.__post_init__()
        return result

    @property
    def params_hash(self) -> str:
        return payload_identity(self.SCHEMA, self.to_payload())


_PARAMETER_CLASSES: dict[str, type[_Record]] = {
    "grcv4-common-params-v1": GRCV4CommonParams,
    "grcv4-candidate-a-params-v1": CandidateAParams,
    "grcv4-candidate-c-params-v1": CandidateCParams,
    "grcv4-geometry-profile-params-v1": GeometryProfileParams,
    "grcv4-ci-params-v1": CISolverParams,
    "grcv4-os-params-v1": OSParams,
    "grcv4-rg2b-params-v1": RG2bParams,
    "grcv4-pc-params-v1": PCParams,
    "grcv4-cipc-params-v1": CIPCParams,
    "grcv4-solver-policy-v1": SolverPolicy,
    "grcv4-charge-policy-v1": ChargePolicy,
    "grcv4-lifecycle-policy-v1": LifecyclePolicy,
}


def resolve_parameters(value: object) -> GRCV4ResolvedParams:
    """Resolve every explicit field; no environment lookup or numeric defaults."""
    return GRCV4ResolvedParams.from_payload(value)


@dataclass(frozen=True, slots=True)
class GRCV4Profile:
    """Consistent, immutable complete declaration; NOT a runtime capability."""

    identity_payload: GRCV4ProfileIdentityPayload
    params_resolved: GRCV4ResolvedParams
    complete_profile_id: str

    def to_canonical_bytes(self) -> bytes:
        """Serialize this declaration, not a scientific state/snapshot."""
        return canonical_json_bytes(self.to_payload())

    @classmethod
    def from_canonical_bytes(cls, data: bytes | str) -> GRCV4Profile:
        """Restore a canonical declaration and verify all its supplied IDs."""
        payload = decode_canonical_json(data)
        if not isinstance(payload, dict) or set(payload) != {
            "identity_payload", "params_resolved", "complete_profile_id"
        } or type(payload["complete_profile_id"]) is not str:
            raise V4SchemaError("expected the exact complete-profile declaration")
        return resolve_profile(
            payload["params_resolved"], payload["identity_payload"],
            expected_complete_profile_id=payload["complete_profile_id"],
        )

    def __post_init__(self) -> None:
        if type(self.identity_payload) is not GRCV4ProfileIdentityPayload or (
            type(self.params_resolved) is not GRCV4ResolvedParams
        ):
            raise V4SchemaError("profile requires typed identity and parameters")
        identity, params = self.identity_payload, self.params_resolved
        payload_identity("resolved_params", params.to_payload(),
                         expected=identity.params_hash)
        expected_candidate = "A" if isinstance(params.candidate, CandidateAParams) else "C"
        expected_realization = {
            CISolverParams: "CI", OSParams: "OS", RG2bParams: "RG2b",
            PCParams: "PC", CIPCParams: "CI+PC",
        }[type(params.realization)]
        if (identity.candidate, identity.realization) != (
            expected_candidate, expected_realization
        ):
            raise V4IdentityError("candidate/realization parameter mismatch")
        for name in ("differential_backend_id", "context_contract_id", "units_id",
                     "gauge_id", "normalization_id", "domain_id"):
            if getattr(identity, name) != getattr(params.common, name):
                raise V4IdentityError(f"profile/common disagreement: {name}")
        # Charge/geometry/solver/lifecycle IDs are algorithm identifiers, not
        # digests or aliases inferred from parameter field names. A future
        # executable registry must resolve them to reviewed implementations.
        payload_identity("profile_identity_payload", identity.to_payload(),
                         expected=self.complete_profile_id)

    def to_payload(self) -> dict[str, JSONValue]:
        return {
            "identity_payload": self.identity_payload.to_payload(),
            "params_resolved": self.params_resolved.to_payload(),
            "complete_profile_id": self.complete_profile_id,
        }


def resolve_profile(
    params_resolved: object,
    identity_payload: object,
    *,
    expected_complete_profile_id: str | None = None,
) -> GRCV4Profile:
    """Resolve and cross-check supplied complete payloads, without advertising."""
    params = resolve_parameters(params_resolved)
    identity = GRCV4ProfileIdentityPayload.from_payload(identity_payload)
    identifier = payload_identity(
        "profile_identity_payload", identity.to_payload(),
        expected=expected_complete_profile_id,
    )
    return GRCV4Profile(identity, params, identifier)


def validate_profile_references(
    profile: GRCV4Profile,
    *,
    live_edge_ids: Sequence[str],
    k4_preimage: object,
    reference_hodge_preimage: object,
) -> None:
    """Check content, coverage and C reference weights, not graph/SPD admission.

    The graph owner must supply its validated stable *unoriented* live-edge
    roster. No position-based remapping, Hodge-to-mobility transfer or repair.
    """
    if isinstance(live_edge_ids, (str, bytes)) or not isinstance(
        live_edge_ids, Sequence
    ):
        raise V4SchemaError("live edges require an ordered stable-ID sequence")
    edges = tuple(live_edge_ids)
    if any(type(edge) is not str or not edge for edge in edges):
        raise V4SchemaError("live edge IDs must be nonempty strings")
    if len(set(edges)) != len(edges):
        raise V4IdentityError("duplicate live edge ID")
    geometry = profile.params_resolved.geometry
    payload_identity("k4_identity_payload", k4_preimage,
                     expected=geometry.K4_base_digest)
    payload_identity("reference_hodge_identity_payload", reference_hodge_preimage,
                     expected=geometry.reference_hodge_digest)
    hodge = validate_payload("reference_hodge_identity_payload", reference_hodge_preimage)
    weights = hodge["edge_weights"]
    if not isinstance(weights, dict) or set(weights) != set(edges):
        raise V4IdentityError("reference Hodge/live-edge mismatch")
    candidate = profile.params_resolved.candidate
    if isinstance(candidate, CandidateCParams) and set(candidate.W_C_tr) != set(edges):
        raise V4IdentityError("target_W_C_tr_matches_live_edges")
    if isinstance(candidate, CandidateCParams) and canonical_json_bytes(
        weights
    ) != canonical_json_bytes(candidate.W_C_tr):
        # D11-C: E_H(W_C_tr) = Diag(W_C_tr), not the eta-scaled mobility
        # nor trial/retained H1_form,M. Compare stable-ID maps; never repair.
        raise V4IdentityError("Candidate C reference Hodge weights must match W_C_tr")


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4ProfileTemplate(_Record):
    """Candidate-discriminated identity only; no target allocator or migration."""

    SCHEMA: ClassVar[str] = "profile_template_payload"
    schema_version: Literal["grcv4-profile-template-v1"]
    source_complete_profile_id: str
    profile_family_id: str
    topology_dependent_map_policy_id: str
    geometry_reference_policy_id: str

    @property
    def profile_template_id(self) -> str:
        return payload_identity(self.SCHEMA, self.to_payload())


def resolve_profile_template(
    value: object, *, source: GRCV4Profile, expected: str | None = None
) -> GRCV4ProfileTemplate:
    template = GRCV4ProfileTemplate.from_payload(value)
    if template.source_complete_profile_id != source.complete_profile_id or (
        template.profile_family_id != source.identity_payload.profile_family_id
    ):
        raise V4IdentityError("template/source profile mismatch")
    payload_identity(template.SCHEMA, template.to_payload(), expected=expected)
    return template


def list_supported_profiles() -> frozenset[str]:
    """No executable profiles have earned acceptance in this foundation leaf."""
    return frozenset()


def get_supported_profile(complete_profile_id: str) -> GRCV4Profile:
    raise V4IdentityError(f"unsupported executable profile: {complete_profile_id}")
