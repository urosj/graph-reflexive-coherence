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


# P9-4.8B explicit user acceptance; local declarations never expand this set.
# The declaration is copied losslessly from the accepted fixture, not rebuilt
# from defaults. No repository/evidence file is needed by an installed package.
_ACCEPTED_C_OS_ID = 'grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d'
_ACCEPTED_C_OS_DECLARATION = (
    '{"complete_profile_id":"grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0'
    'f762503e8c424c2f59b6d","identity_payload":{"candidate":"C","candidate_c_transport_id":"C'
    '-HM-STIFFNESS-BASELINE-v1","charge_profile_id":"unit_vertex_measure_v1","composition_gai'
    'n":null,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"orie'
    'nted_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"'
    'component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","'
    'lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex'
    '_stiffness_v1","params_hash":"grcv4-params-sha256:81b0876e6852f2b08755f08cf932abf08d95a4'
    '763b43fc14bc607f45a5fde48f","profile_family_id":"C_OS","realization":"OS","schema_versio'
    'n":"grcv4-profile-identity-v1","solver_id":"direct_unique_root_v1","units_id":"grcv4_non'
    'dimensional_reference_v1"},"params_resolved":{"candidate":{"C_ref":1,"E_H_policy_id":"di'
    'ag_W_C_tr_structural_hodge_v1","E_M_policy_id":"eta_C_diag_W_C_tr_mobility_v1","Lambda_C'
    '":1,"W_C_tr":{"e":2},"W_C_tr_content_digest":"grcv4-wctr-sha256:fa845c7788b4d8877437f2c3'
    '456230a9365981e115465e3a393cc868351419fb","chi_C":1,"current_conditioning_policy_id":"st'
    'rict_invertible_current_block_v1","eta_C":0.5,"kappa_M_C":0,"kappa_Phi_C":1,"potential_e'
    'valuator_id":"quadratic_site_potential_zero_derivative_v1","schema_version":"grcv4-candi'
    'date-c-params-v1","selector_boundary_policy_id":"strict_rank_gap_fail_closed_v1","tau_C"'
    ':0,"transport_id":"C-HM-STIFFNESS-BASELINE-v1","zeta_C":3},"charge":{"absolute_tolerance'
    '":0,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stabl'
    'e_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_'
    'projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_bin'
    'ary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_po'
    'licy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_s'
    'tep_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain'
    '_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","meas'
    'ure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffne'
    'ss_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_refere'
    'nce_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:bc96c6d5259157dc72a745b81d31e8d3d'
    '927527ba9115b36ee169706ddac40f5","candidate_adapter_id":"candidate_c_exact_star_adapter_'
    'v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_gr'
    'aph_v1","kappa_H":0,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","refe'
    'rence_hodge_digest":"grcv4-hodge-sha256:a02932d58fbfa8b044f724284eb590065f2ee4cc42f3809e'
    '697781606530683e","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"v'
    'ertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_c_no_independe'
    'nt_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migrat'
    'ion_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_ba'
    'seline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1'
    '","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4'
    '-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"real'
    'ization":{"corrector_policy_id":"one_fresh_geometry_corrector_v1","predictor_policy_id":'
    '"reference_geometry_predictor_v1","schema_version":"grcv4-os-params-v1","split_residual_'
    'norm_id":"edge_l2_v1","tolerance":1},"schema_version":"grcv4-resolved-params-v1","solver'
    '":{"absolute_tolerance":0,"conditioning_limit":100,"failure_policy_id":"fail_closed_no_f'
    'allback_v1","iteration_limit":1,"relative_tolerance":0,"residual_norm_id":"edge_l2_v1","'
    'root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","s'
    'olver_kind":"direct"}}}'
)


_ACCEPTED_A_OS_ID = 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4'
_ACCEPTED_A_OS_DECLARATION = '{"complete_profile_id":"grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4","identity_payload":{"candidate":"A","candidate_c_transport_id":null,"charge_profile_id":"unit_vertex_measure_v1","composition_gain":null,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex_stiffness_v1","params_hash":"grcv4-params-sha256:1bb5271bc5743f3356b1b1d2ce3a07f8de25327d493ecc0ca467560becf97552","profile_family_id":"A_OS","realization":"OS","schema_version":"grcv4-profile-identity-v1","solver_id":"direct_unique_root_v1","units_id":"grcv4_nondimensional_reference_v1"},"params_resolved":{"candidate":{"W_floor":1e-12,"alpha":0,"beta":0,"chi_A":0.5,"conductance_evaluator_id":"curvature_disabled_G_W_v1","descriptor_backend_id":"grcv4-a-descriptor-sha256:6aaa0de5fbfcda770a02d928fe8bb0da0c10ed1191c7d50e21ce79cda67ab391","eta":0.25,"gamma":0,"kappa_Ah":0.25,"kappa_c":0.5,"schema_version":"grcv4-candidate-a-params-v1","site_potential_id":"quadratic_site_potential_zero_derivative_v1","tau_A":1,"zeta_A":0.75},"charge":{"absolute_tolerance":1e-12,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stable_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_binary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_policy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_step_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","measure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffness_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_reference_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:bc96c6d5259157dc72a745b81d31e8d3d927527ba9115b36ee169706ddac40f5","candidate_adapter_id":"candidate_a_exact_star_adapter_v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_graph_v1","kappa_H":0.125,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","reference_hodge_digest":"grcv4-hodge-sha256:39c788e2af9fd01ac76ebce739e40362ffee1388fef552c59840adba1c51f037","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"vertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_a_explicit_reference_initialization_log_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migration_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_baseline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"realization":{"corrector_policy_id":"one_fresh_geometry_corrector_v1","predictor_policy_id":"reference_geometry_predictor_v1","schema_version":"grcv4-os-params-v1","split_residual_norm_id":"edge_l2_v1","tolerance":10},"schema_version":"grcv4-resolved-params-v1","solver":{"absolute_tolerance":1e-12,"conditioning_limit":100,"failure_policy_id":"fail_closed_no_fallback_v1","iteration_limit":1,"relative_tolerance":1e-12,"residual_norm_id":"edge_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","solver_kind":"direct"}}}'


_ACCEPTED_A_CI_ID = 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946'
_ACCEPTED_A_CI_DECLARATION = '{"complete_profile_id":"grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946","identity_payload":{"candidate":"A","candidate_c_transport_id":null,"charge_profile_id":"unit_vertex_measure_v1","composition_gain":null,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex_stiffness_v1","params_hash":"grcv4-params-sha256:3a3907be149626365702aab85407957551c39f02c0e556ff3885c8ee54c5b687","profile_family_id":"A_CI","realization":"CI","schema_version":"grcv4-profile-identity-v1","solver_id":"ci_reduced_fixed_point_v1","units_id":"grcv4_nondimensional_reference_v1"},"params_resolved":{"candidate":{"W_floor":1e-12,"alpha":0,"beta":0,"chi_A":0.5,"conductance_evaluator_id":"curvature_disabled_G_W_v1","descriptor_backend_id":"grcv4-a-descriptor-sha256:6aaa0de5fbfcda770a02d928fe8bb0da0c10ed1191c7d50e21ce79cda67ab391","eta":0.25,"gamma":0.1,"kappa_Ah":0.25,"kappa_c":0.5,"schema_version":"grcv4-candidate-a-params-v1","site_potential_id":"quadratic_site_potential_zero_derivative_v1","tau_A":1,"zeta_A":0.75},"charge":{"absolute_tolerance":1e-11,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stable_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_binary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_policy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_step_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","measure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffness_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_reference_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:bc96c6d5259157dc72a745b81d31e8d3d927527ba9115b36ee169706ddac40f5","candidate_adapter_id":"candidate_a_exact_star_adapter_v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_graph_v1","kappa_H":0.00001,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","reference_hodge_digest":"grcv4-hodge-sha256:39c788e2af9fd01ac76ebce739e40362ffee1388fef552c59840adba1c51f037","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"vertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_a_explicit_reference_initialization_log_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migration_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_baseline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"realization":{"contraction_domain_id":"ci_reference_frobenius_ball_v1:0x1.0000000000000p-3","iteration_limit":60,"residual_norm_id":"joint_current_geometry_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-ci-params-v1","tolerance":1e-11},"schema_version":"grcv4-resolved-params-v1","solver":{"absolute_tolerance":1e-11,"conditioning_limit":100000000,"failure_policy_id":"fail_closed_no_fallback_v1","iteration_limit":60,"relative_tolerance":1e-11,"residual_norm_id":"edge_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","solver_kind":"fixed_point"}}}'

_ACCEPTED_C_CI_ID = 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e'
_ACCEPTED_C_CI_DECLARATION = '{"complete_profile_id":"grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e","identity_payload":{"candidate":"C","candidate_c_transport_id":"C-HM-STIFFNESS-BASELINE-v1","charge_profile_id":"unit_vertex_measure_v1","composition_gain":null,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex_stiffness_v1","params_hash":"grcv4-params-sha256:c2c2fee30e1508304d6cc8fb7842ba694845b40f4c377eace1e6d8745fd9d31a","profile_family_id":"C_CI","realization":"CI","schema_version":"grcv4-profile-identity-v1","solver_id":"ci_reduced_fixed_point_v1","units_id":"grcv4_nondimensional_reference_v1"},"params_resolved":{"candidate":{"C_ref":1,"E_H_policy_id":"diag_W_C_tr_structural_hodge_v1","E_M_policy_id":"eta_C_diag_W_C_tr_mobility_v1","Lambda_C":1,"W_C_tr":{"e":2},"W_C_tr_content_digest":"grcv4-wctr-sha256:fa845c7788b4d8877437f2c3456230a9365981e115465e3a393cc868351419fb","chi_C":0.25,"current_conditioning_policy_id":"strict_invertible_current_block_v1","eta_C":0.5,"kappa_M_C":0,"kappa_Phi_C":1,"potential_evaluator_id":"quadratic_site_potential_zero_derivative_v1","schema_version":"grcv4-candidate-c-params-v1","selector_boundary_policy_id":"strict_rank_gap_fail_closed_v1","tau_C":0.25,"transport_id":"C-HM-STIFFNESS-BASELINE-v1","zeta_C":0.25},"charge":{"absolute_tolerance":1e-11,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stable_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_binary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_policy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_step_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","measure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffness_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_reference_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:bc96c6d5259157dc72a745b81d31e8d3d927527ba9115b36ee169706ddac40f5","candidate_adapter_id":"candidate_c_exact_star_adapter_v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_graph_v1","kappa_H":0.00001,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","reference_hodge_digest":"grcv4-hodge-sha256:a02932d58fbfa8b044f724284eb590065f2ee4cc42f3809e697781606530683e","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"vertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_c_no_independent_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migration_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_baseline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"realization":{"contraction_domain_id":"ci_reference_frobenius_ball_v1:0x1.0000000000000p-3","iteration_limit":60,"residual_norm_id":"joint_current_geometry_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-ci-params-v1","tolerance":1e-11},"schema_version":"grcv4-resolved-params-v1","solver":{"absolute_tolerance":1e-11,"conditioning_limit":100000000,"failure_policy_id":"fail_closed_no_fallback_v1","iteration_limit":60,"relative_tolerance":1e-11,"residual_norm_id":"edge_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","solver_kind":"fixed_point"}}}'

_ACCEPTED_A_PC_ID = 'grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75'
_ACCEPTED_A_PC_DECLARATION = '{"complete_profile_id":"grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75","identity_payload":{"candidate":"A","candidate_c_transport_id":null,"charge_profile_id":"unit_vertex_measure_v1","composition_gain":null,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex_stiffness_v1","params_hash":"grcv4-params-sha256:83225e6bf7e0b0a1b653016e2202466a9bcc0893c214bf4822d0523348ccedab","profile_family_id":"A_PC","realization":"PC","schema_version":"grcv4-profile-identity-v1","solver_id":"direct_unique_root_v1","units_id":"grcv4_nondimensional_reference_v1"},"params_resolved":{"candidate":{"W_floor":1e-12,"alpha":0,"beta":0,"chi_A":0.5,"conductance_evaluator_id":"curvature_disabled_G_W_v1","descriptor_backend_id":"grcv4-a-descriptor-sha256:6aaa0de5fbfcda770a02d928fe8bb0da0c10ed1191c7d50e21ce79cda67ab391","eta":0.25,"gamma":0.1,"kappa_Ah":0.25,"kappa_c":0.5,"schema_version":"grcv4-candidate-a-params-v1","site_potential_id":"quadratic_site_potential_zero_derivative_v1","tau_A":1,"zeta_A":0.75},"charge":{"absolute_tolerance":1e-11,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stable_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_binary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_policy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_step_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","measure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffness_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_reference_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:bc96c6d5259157dc72a745b81d31e8d3d927527ba9115b36ee169706ddac40f5","candidate_adapter_id":"candidate_a_exact_star_adapter_v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_graph_v1","kappa_H":0.00001,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","reference_hodge_digest":"grcv4-hodge-sha256:39c788e2af9fd01ac76ebce739e40362ffee1388fef552c59840adba1c51f037","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"vertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_a_explicit_reference_initialization_log_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migration_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_baseline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"realization":{"carrier_norm_id":"symmetric_star_frobenius_v1","radius":64,"schema_version":"grcv4-pc-params-v1","source_envelope_id":"pc_compact_base_chart_v1:0x1.0000000000000p+2:0x1.999999999999ap-4:0x1.0000000000000p+1","tau_PC":0.5,"writer_id":"zero_order_hold_exponential_v1"},"schema_version":"grcv4-resolved-params-v1","solver":{"absolute_tolerance":1e-11,"conditioning_limit":100000000,"failure_policy_id":"fail_closed_no_fallback_v1","iteration_limit":60,"relative_tolerance":1e-11,"residual_norm_id":"edge_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","solver_kind":"direct"}}}'

_ACCEPTED_C_PC_ID = 'grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f'
_ACCEPTED_C_PC_DECLARATION = '{"complete_profile_id":"grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f","identity_payload":{"candidate":"C","candidate_c_transport_id":"C-HM-STIFFNESS-BASELINE-v1","charge_profile_id":"unit_vertex_measure_v1","composition_gain":null,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex_stiffness_v1","params_hash":"grcv4-params-sha256:345079769405a1c740aa54a86366111cbbcb8d885345cac73389b04d4bd9824a","profile_family_id":"C_PC","realization":"PC","schema_version":"grcv4-profile-identity-v1","solver_id":"direct_unique_root_v1","units_id":"grcv4_nondimensional_reference_v1"},"params_resolved":{"candidate":{"C_ref":1,"E_H_policy_id":"diag_W_C_tr_structural_hodge_v1","E_M_policy_id":"eta_C_diag_W_C_tr_mobility_v1","Lambda_C":1,"W_C_tr":{"e":2},"W_C_tr_content_digest":"grcv4-wctr-sha256:fa845c7788b4d8877437f2c3456230a9365981e115465e3a393cc868351419fb","chi_C":0.25,"current_conditioning_policy_id":"strict_invertible_current_block_v1","eta_C":0.5,"kappa_M_C":0,"kappa_Phi_C":1,"potential_evaluator_id":"quadratic_site_potential_zero_derivative_v1","schema_version":"grcv4-candidate-c-params-v1","selector_boundary_policy_id":"strict_rank_gap_fail_closed_v1","tau_C":0.25,"transport_id":"C-HM-STIFFNESS-BASELINE-v1","zeta_C":0.25},"charge":{"absolute_tolerance":1e-11,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stable_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_binary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_policy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_step_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","measure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffness_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_reference_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:bc96c6d5259157dc72a745b81d31e8d3d927527ba9115b36ee169706ddac40f5","candidate_adapter_id":"candidate_c_exact_star_adapter_v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_graph_v1","kappa_H":0.00001,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","reference_hodge_digest":"grcv4-hodge-sha256:a02932d58fbfa8b044f724284eb590065f2ee4cc42f3809e697781606530683e","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"vertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_c_no_independent_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migration_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_baseline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"realization":{"carrier_norm_id":"symmetric_star_frobenius_v1","radius":64,"schema_version":"grcv4-pc-params-v1","source_envelope_id":"pc_compact_base_chart_v1:0x1.0000000000000p+2:0x1.0000000000000p+0:0x1.0000000000000p+0","tau_PC":0.5,"writer_id":"zero_order_hold_exponential_v1"},"schema_version":"grcv4-resolved-params-v1","solver":{"absolute_tolerance":1e-11,"conditioning_limit":100000000,"failure_policy_id":"fail_closed_no_fallback_v1","iteration_limit":60,"relative_tolerance":1e-11,"residual_norm_id":"edge_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","solver_kind":"direct"}}}'


_ACCEPTED_A_CI_PC_ID = 'grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689'
_ACCEPTED_A_CI_PC_DECLARATION = '{"complete_profile_id":"grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689","identity_payload":{"candidate":"A","candidate_c_transport_id":null,"charge_profile_id":"unit_vertex_measure_v1","composition_gain":2,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex_stiffness_v1","params_hash":"grcv4-params-sha256:8a7635269bad7062ea17b27656f0677094e43b9413453bcf3e5e27142b3a25e7","profile_family_id":"A_CI_PC","realization":"CI+PC","schema_version":"grcv4-profile-identity-v1","solver_id":"ci_reduced_fixed_point_v1","units_id":"grcv4_nondimensional_reference_v1"},"params_resolved":{"candidate":{"W_floor":1e-12,"alpha":0,"beta":0,"chi_A":0.5,"conductance_evaluator_id":"curvature_disabled_G_W_v1","descriptor_backend_id":"grcv4-a-descriptor-sha256:6aaa0de5fbfcda770a02d928fe8bb0da0c10ed1191c7d50e21ce79cda67ab391","eta":0.25,"gamma":0.1,"kappa_Ah":0.25,"kappa_c":0.5,"schema_version":"grcv4-candidate-a-params-v1","site_potential_id":"quadratic_site_potential_zero_derivative_v1","tau_A":1,"zeta_A":0.75},"charge":{"absolute_tolerance":1e-11,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stable_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_binary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_policy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_step_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","measure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffness_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_reference_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:bc96c6d5259157dc72a745b81d31e8d3d927527ba9115b36ee169706ddac40f5","candidate_adapter_id":"candidate_a_exact_star_adapter_v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_graph_v1","kappa_H":0.00001,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","reference_hodge_digest":"grcv4-hodge-sha256:39c788e2af9fd01ac76ebce739e40362ffee1388fef552c59840adba1c51f037","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"vertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_a_explicit_reference_initialization_log_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migration_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_baseline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"realization":{"carrier_norm_id":"symmetric_star_frobenius_v1","contraction_domain_id":"ci_reference_frobenius_ball_v1:0x1.0000000000000p-3","iteration_limit":60,"radius":64,"residual_norm_id":"joint_current_geometry_l2_v1","rho_inst":1,"root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-cipc-params-v1","source_envelope_id":"pc_compact_base_chart_v1:0x1.0000000000000p+2:0x1.999999999999ap-4:0x1.0000000000000p+1","tau_PC":0.5,"tolerance":1e-11,"writer_id":"zero_order_hold_exponential_v1"},"schema_version":"grcv4-resolved-params-v1","solver":{"absolute_tolerance":1e-11,"conditioning_limit":100000000,"failure_policy_id":"fail_closed_no_fallback_v1","iteration_limit":60,"relative_tolerance":1e-11,"residual_norm_id":"edge_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","solver_kind":"fixed_point"}}}'

_ACCEPTED_C_CI_PC_ID = 'grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b'
_ACCEPTED_C_CI_PC_DECLARATION = '{"complete_profile_id":"grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b","identity_payload":{"candidate":"C","candidate_c_transport_id":"C-HM-STIFFNESS-BASELINE-v1","charge_profile_id":"unit_vertex_measure_v1","composition_gain":2,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex_stiffness_v1","params_hash":"grcv4-params-sha256:e77e7fe48b70b646c5ddb3292273f0837d4031cd400078bebb7e49e555ca6c89","profile_family_id":"C_CI_PC","realization":"CI+PC","schema_version":"grcv4-profile-identity-v1","solver_id":"ci_reduced_fixed_point_v1","units_id":"grcv4_nondimensional_reference_v1"},"params_resolved":{"candidate":{"C_ref":1,"E_H_policy_id":"diag_W_C_tr_structural_hodge_v1","E_M_policy_id":"eta_C_diag_W_C_tr_mobility_v1","Lambda_C":1,"W_C_tr":{"e":2},"W_C_tr_content_digest":"grcv4-wctr-sha256:fa845c7788b4d8877437f2c3456230a9365981e115465e3a393cc868351419fb","chi_C":0.25,"current_conditioning_policy_id":"strict_invertible_current_block_v1","eta_C":0.5,"kappa_M_C":0,"kappa_Phi_C":1,"potential_evaluator_id":"quadratic_site_potential_zero_derivative_v1","schema_version":"grcv4-candidate-c-params-v1","selector_boundary_policy_id":"strict_rank_gap_fail_closed_v1","tau_C":0.25,"transport_id":"C-HM-STIFFNESS-BASELINE-v1","zeta_C":0.25},"charge":{"absolute_tolerance":1e-11,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stable_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_binary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_policy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_step_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","measure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffness_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_reference_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:bc96c6d5259157dc72a745b81d31e8d3d927527ba9115b36ee169706ddac40f5","candidate_adapter_id":"candidate_c_exact_star_adapter_v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_graph_v1","kappa_H":0.00001,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","reference_hodge_digest":"grcv4-hodge-sha256:a02932d58fbfa8b044f724284eb590065f2ee4cc42f3809e697781606530683e","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"vertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_c_no_independent_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migration_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_baseline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"realization":{"carrier_norm_id":"symmetric_star_frobenius_v1","contraction_domain_id":"ci_reference_frobenius_ball_v1:0x1.0000000000000p-3","iteration_limit":60,"radius":64,"residual_norm_id":"joint_current_geometry_l2_v1","rho_inst":1,"root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-cipc-params-v1","source_envelope_id":"pc_compact_base_chart_v1:0x1.0000000000000p+2:0x1.0000000000000p+0:0x1.0000000000000p+0","tau_PC":0.5,"tolerance":1e-11,"writer_id":"zero_order_hold_exponential_v1"},"schema_version":"grcv4-resolved-params-v1","solver":{"absolute_tolerance":1e-11,"conditioning_limit":100000000,"failure_policy_id":"fail_closed_no_fallback_v1","iteration_limit":60,"relative_tolerance":1e-11,"residual_norm_id":"edge_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","solver_kind":"fixed_point"}}}'


_ACCEPTED_A_RG2B_ID = 'grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b'
_ACCEPTED_A_RG2B_DECLARATION = '{"complete_profile_id":"grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b","identity_payload":{"candidate":"A","candidate_c_transport_id":null,"charge_profile_id":"unit_vertex_measure_v1","composition_gain":null,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex_stiffness_v1","params_hash":"grcv4-params-sha256:910a0023088aef04af62f105792d0da6732d076e6be2ccdfa533c18e9e9990f7","profile_family_id":"A_RG2b","realization":"RG2b","schema_version":"grcv4-profile-identity-v1","solver_id":"direct_unique_root_v1","units_id":"grcv4_nondimensional_reference_v1"},"params_resolved":{"candidate":{"W_floor":1e-12,"alpha":0.02,"beta":0.03,"chi_A":0.1,"conductance_evaluator_id":"curvature_disabled_G_W_v1","descriptor_backend_id":"grcv4-a-descriptor-sha256:e5fdbe87141814e1a44a177c5a5272965dc2fd42cd9f96169ce001ab5e39a4b7","eta":0.05,"gamma":0.02,"kappa_Ah":0.1,"kappa_c":0.1,"schema_version":"grcv4-candidate-a-params-v1","site_potential_id":"quadratic_site_potential_zero_derivative_v1","tau_A":1,"zeta_A":0.1},"charge":{"absolute_tolerance":1e-11,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stable_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_binary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_policy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_step_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","measure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffness_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_reference_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:3301b25a6acf9ced2fdae1753f4083b767a804a1b59379cd351ddbd768c798d7","candidate_adapter_id":"candidate_a_exact_star_adapter_v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_graph_v1","kappa_H":0.001,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","reference_hodge_digest":"grcv4-hodge-sha256:23960857be86531b57935c80fc07d0cd750fde007568d409d1590dba26f9fabe","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"vertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_a_explicit_reference_initialization_log_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migration_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_baseline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"realization":{"approximation_policy_id":"rg2b_matrix_ball_graph_transform_160bit_inverse64_depth16_v1","containment_certificate_id":"rg2b_derived_graph_compact_linfty_C_W_certificate_v1","error_norm_id":"rg2b_hodge_frobenius_v1","error_tolerance":1e-11,"extension_evaluator_id":"rg2b_graph_cubic_completion_v1:0x1.0000000000000p+1:0x1.0000000000000p+1:0x1.0000000000000p-3:0x1.0000000000000p-2:0x1.8000000000000p-2:0x1.0000000000000p-6:0x1.0000000000000p-3:0x1.0000000000000p-20","failure_policy_id":"fail_closed_on_uncertified_section_v1","iteration_limit":4000,"schema_version":"grcv4-rg2b-params-v1"},"schema_version":"grcv4-resolved-params-v1","solver":{"absolute_tolerance":1e-12,"conditioning_limit":100000000,"failure_policy_id":"fail_closed_no_fallback_v1","iteration_limit":1,"relative_tolerance":1e-12,"residual_norm_id":"edge_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","solver_kind":"direct"}}}'


_ACCEPTED_C_RG2B_ID = 'grcv4-profile-sha256:413497bec4f219ec402d82d5cd2aced01dca25a58d2ab906c348472b98d596b0'
_ACCEPTED_C_RG2B_DECLARATION = '{"complete_profile_id":"grcv4-profile-sha256:413497bec4f219ec402d82d5cd2aced01dca25a58d2ab906c348472b98d596b0","identity_payload":{"candidate":"C","candidate_c_transport_id":"C-HM-STIFFNESS-BASELINE-v1","charge_profile_id":"unit_vertex_measure_v1","composition_gain":null,"context_contract_id":"constant_zero_context_v1","differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","geometry_profile_id":"affine_reference_relative_v1","lifecycle_policy_id":"grcv4-lifecycle-policy-v1","normalization_id":"unnormalized_vertex_stiffness_v1","params_hash":"grcv4-params-sha256:9348c01c1b244fedda110710f1f7ebea2fc6128293398c456d20b07adf8a4953","profile_family_id":"C_RG2b","realization":"RG2b","schema_version":"grcv4-profile-identity-v1","solver_id":"direct_unique_root_v1","units_id":"grcv4_nondimensional_reference_v1"},"params_resolved":{"candidate":{"C_ref":1,"E_H_policy_id":"diag_W_C_tr_structural_hodge_v1","E_M_policy_id":"eta_C_diag_W_C_tr_mobility_v1","Lambda_C":100,"W_C_tr":{"e000":1,"e001":1.125,"e002":1.25},"W_C_tr_content_digest":"grcv4-wctr-sha256:08e93631d97e2b264cb096970febdbef4ce9bad2db8ba211f4e12e92f39321d2","chi_C":0.1,"current_conditioning_policy_id":"strict_invertible_current_block_v1","eta_C":0.05,"kappa_M_C":0.1,"kappa_Phi_C":0.1,"potential_evaluator_id":"quadratic_site_potential_zero_derivative_v1","schema_version":"grcv4-candidate-c-params-v1","selector_boundary_policy_id":"strict_rank_gap_fail_closed_v1","tau_C":0.1,"transport_id":"C-HM-STIFFNESS-BASELINE-v1","zeta_C":0.1},"charge":{"absolute_tolerance":1e-11,"accumulation_order":"canonical_live_vertex_balanced_binary_tree","policy_id":"stable_pairwise_binary64_charge_v1","relative_tolerance":0,"remainder_policy":"compatibility_projection_is_none","repair_policy":"never_mutate_resource","rounding_mode":"IEEE754_binary64_roundTiesToEven","schema_version":"grcv4-charge-policy-v1"},"common":{"boundary_policy_id":"closed_no_flux_v1","context_contract_id":"constant_zero_context_v1","default_step_request":null,"differential_backend_id":"oriented_incidence_d0_equals_BT_v1","domain_id":"fixed_graph_strict_gap_spd_v1","gauge_id":"component_zero_mean_potential_v1","measure_profile_id":"unit_vertex_measure_v1","normalization_id":"unnormalized_vertex_stiffness_v1","schema_version":"grcv4-common-params-v1","units_id":"grcv4_nondimensional_reference_v1"},"geometry":{"K4_base_digest":"grcv4-k4-sha256:3301b25a6acf9ced2fdae1753f4083b767a804a1b59379cd351ddbd768c798d7","candidate_adapter_id":"candidate_c_exact_star_adapter_v1","flat_sharp_solver_id":"spd_direct_v1","geometry_domain_id":"positive_hodge_fixed_graph_v1","kappa_H":0.001,"overlap_normalization_id":"edge_multiplicity_inverse_sqrt_v1","reference_hodge_digest":"grcv4-hodge-sha256:23960857be86531b57935c80fc07d0cd750fde007568d409d1590dba26f9fabe","schema_version":"grcv4-geometry-profile-params-v1","star_cover_id":"vertex_star_exact_overlap_v1"},"lifecycle":{"history_policy_id":"candidate_c_no_independent_history_v1","mapped_event_policy_id":"caller_mapped_atomic_topology_event_v1","migration_policy_id":"typed_bidirectional_profile_migration_v1","rebase_policy_id":"replace_baseline_append_receipt_v1","receipt_policy_id":"operation_delta_plus_persistent_ledger_v1","reset_policy_id":"restore_current_baseline_append_receipt_v1","schema_version":"grcv4-lifecycle-policy-v1","target_readmission_policy_id":"full_target_fail_closed_v1"},"realization":{"approximation_policy_id":"rg2b_matrix_ball_graph_transform_160bit_inverse64_depth16_v1","containment_certificate_id":"rg2b_derived_graph_compact_linfty_C_W_certificate_v1","error_norm_id":"rg2b_hodge_frobenius_v1","error_tolerance":1e-11,"extension_evaluator_id":"rg2b_graph_cubic_completion_v1:0x1.0000000000000p+1:0x1.0000000000000p+0:0x1.0000000000000p-3:0x1.0000000000000p-2:0x1.8000000000000p-2:0x1.0000000000000p-6:0x1.0000000000000p-3:0x1.0000000000000p-20","failure_policy_id":"fail_closed_on_uncertified_section_v1","iteration_limit":4000,"schema_version":"grcv4-rg2b-params-v1"},"schema_version":"grcv4-resolved-params-v1","solver":{"absolute_tolerance":1e-11,"conditioning_limit":100000000,"failure_policy_id":"fail_closed_no_fallback_v1","iteration_limit":1,"relative_tolerance":1e-11,"residual_norm_id":"edge_l2_v1","root_selector_id":"unique_admitted_root_v1","schema_version":"grcv4-solver-policy-v1","solver_kind":"direct"}}}'

def list_supported_profiles() -> frozenset[str]:
    """Exact globally accepted G2 support, not all constructible local targets."""
    return frozenset({_ACCEPTED_C_OS_ID, _ACCEPTED_A_OS_ID, _ACCEPTED_A_CI_ID, _ACCEPTED_C_CI_ID, _ACCEPTED_A_PC_ID, _ACCEPTED_C_PC_ID, _ACCEPTED_A_CI_PC_ID, _ACCEPTED_C_CI_PC_ID, _ACCEPTED_A_RG2B_ID, _ACCEPTED_C_RG2B_ID})


def get_supported_profile(complete_profile_id: str) -> GRCV4Profile:
    """Return the immutable, digest-verified accepted declaration only."""
    if type(complete_profile_id) is not str or complete_profile_id not in list_supported_profiles():
        raise V4IdentityError(f"unsupported executable profile: {complete_profile_id}")
    return GRCV4Profile.from_canonical_bytes(
        {_ACCEPTED_C_OS_ID: _ACCEPTED_C_OS_DECLARATION,
         _ACCEPTED_A_OS_ID: _ACCEPTED_A_OS_DECLARATION,
         _ACCEPTED_A_CI_ID: _ACCEPTED_A_CI_DECLARATION,
         _ACCEPTED_C_CI_ID: _ACCEPTED_C_CI_DECLARATION,
         _ACCEPTED_A_PC_ID: _ACCEPTED_A_PC_DECLARATION,
         _ACCEPTED_C_PC_ID: _ACCEPTED_C_PC_DECLARATION,
         _ACCEPTED_A_CI_PC_ID: _ACCEPTED_A_CI_PC_DECLARATION,
         _ACCEPTED_C_CI_PC_ID: _ACCEPTED_C_CI_PC_DECLARATION,
         _ACCEPTED_A_RG2B_ID: _ACCEPTED_A_RG2B_DECLARATION,
         _ACCEPTED_C_RG2B_ID: _ACCEPTED_C_RG2B_DECLARATION}[complete_profile_id]
    )
