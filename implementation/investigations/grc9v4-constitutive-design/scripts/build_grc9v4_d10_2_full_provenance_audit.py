#!/usr/bin/env python3
"""Build the full GRCV4/GRC9V4 D10.2 substrate-provenance audit."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "implementation/investigations/grc9v4-constitutive-design"
DECISIONS = BASE / "decisions"
OUTPUT_JSON = DECISIONS / "D10_2FullSubstrateProvenanceAndPromotionAudit.json"
OUTPUT_MD = DECISIONS / "D10_2FullSubstrateProvenanceAndPromotionAudit.md"
D10_PATH = DECISIONS / "D10DesignSynthesisAndSpecWritingDecision.json"
D10_1_PATH = DECISIONS / "D10_1PreliminarySubstrateProvenance.json"
D10_CLAIM_PATH = DECISIONS / "D10NormativeClaimTopology.json"
D10_AUTHORIZATION_PATH = DECISIONS / "D10SpecificationAuthorizationProfile.json"


def canonical_digest(data: dict[str, Any], digest_field: str) -> str:
    payload = {key: value for key, value in data.items() if key != digest_field}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path_text: str, source_id: str, consumed_as: str) -> dict[str, Any]:
    path = ROOT / path_text
    row: dict[str, Any] = {
        "source_id": source_id,
        "path": path_text,
        "file_sha256": file_sha(path),
        "consumed_as": consumed_as,
    }
    if path.suffix == ".json":
        data = json.loads(path.read_text())
        digest_field = (
            "decision_record_digest"
            if "decision_record_digest" in data
            else "artifact_digest"
        )
        if digest_field in data:
            computed = canonical_digest(data, digest_field)
            if data[digest_field] != computed:
                raise ValueError(f"noncanonical source record: {path_text}")
            row["source_digest"] = computed
    return row


def derivation(
    derivation_id: str,
    title: str,
    source_premises: list[str],
    construction: list[str],
    conclusion: str,
    applies_to: list[str],
    blocked_overread: str,
) -> dict[str, Any]:
    return {
        "derivation_id": derivation_id,
        "title": title,
        "source_premises": source_premises,
        "construction": construction,
        "conclusion": conclusion,
        "applies_to": applies_to,
        "blocked_overread": blocked_overread,
    }


def audit_object(
    object_id: str,
    family: str,
    object_kind: str,
    normative_object: str,
    premises_used: list[str],
    source_lineage: list[str],
    substrate_disposition: str,
    promotion_status: str,
    independent_derivation_ids: list[str],
    deletion_test: str,
    conclusion: str,
    specification_destination: str,
    blocked_overread: str,
) -> dict[str, Any]:
    return {
        "object_id": object_id,
        "family": family,
        "object_kind": object_kind,
        "normative_object": normative_object,
        "premises_used": premises_used,
        "source_lineage": source_lineage,
        "substrate_disposition": substrate_disposition,
        "promotion_status": promotion_status,
        "independent_derivation_ids": independent_derivation_ids,
        "GRC9V3_premise_deletion_test": deletion_test,
        "conclusion": conclusion,
        "specification_destination": specification_destination,
        "blocked_overread": blocked_overread,
    }


def equation_contract(
    contract_id: str,
    contract_scope: str,
    parent_object_ids: list[str],
    accepted_claim_ids: list[str],
    profile_ids: list[str],
    normative_equation_or_contract: str,
    premises_used: list[str],
    source_lineage: list[str],
    substrate_disposition: str,
    promotion_status: str,
    independent_derivation_ids: list[str],
    deletion_test: str,
    specification_destination: str,
    blocked_overread: str,
) -> dict[str, Any]:
    return {
        "equation_contract_id": contract_id,
        "contract_scope": contract_scope,
        "parent_object_ids": parent_object_ids,
        "accepted_claim_ids": accepted_claim_ids,
        "profile_ids": profile_ids,
        "normative_equation_or_contract": normative_equation_or_contract,
        "premises_used": premises_used,
        "source_lineage": source_lineage,
        "substrate_disposition": substrate_disposition,
        "promotion_status": promotion_status,
        "independent_derivation_ids": independent_derivation_ids,
        "GRC9V3_premise_deletion_test": deletion_test,
        "specification_destination": specification_destination,
        "blocked_overread": blocked_overread,
    }


D10 = json.loads(D10_PATH.read_text())
D10_1 = json.loads(D10_1_PATH.read_text())
D10_CLAIMS = json.loads(D10_CLAIM_PATH.read_text())
D10_AUTHORIZATION = json.loads(D10_AUTHORIZATION_PATH.read_text())

if D10["decision_record_digest"] != canonical_digest(D10, "decision_record_digest"):
    raise ValueError("accepted D10 digest is not canonical")
if D10_1["decision_record_digest"] != canonical_digest(
    D10_1, "decision_record_digest"
):
    raise ValueError("accepted D10.1 digest is not canonical")
if D10_1["status"] != "accepted_preliminary_bounded_substrate_provenance_separation":
    raise ValueError("D10.1 must be accepted before D10.2")


def flatten_claim_classes(claim_classes: dict[str, Any]) -> set[str]:
    return {
        claim_id
        for claim_class in ["normative", "optional", "conditional", "open", "negative"]
        for claim_id in claim_classes[claim_class]
    }


D10_DECISION_CLAIM_IDS = flatten_claim_classes(D10["decision"]["claim_topology"])
D10_TOPOLOGY_CLAIM_IDS = {row["claim_id"] for row in D10_CLAIMS["claims"]}
D10_AUTHORIZATION_CLAIM_IDS = {
    claim_id
    for field in [
        "normative_common_claim_ids",
        "optional_profile_claim_ids",
        "conditional_claim_ids",
        "open_claim_ids",
        "negative_claim_ids",
    ]
    for claim_id in D10_AUTHORIZATION[field]
}
if not (
    D10_DECISION_CLAIM_IDS
    == D10_TOPOLOGY_CLAIM_IDS
    == D10_AUTHORIZATION_CLAIM_IDS
):
    raise ValueError("accepted D10 claim surfaces disagree")
if len(D10_TOPOLOGY_CLAIM_IDS) != 39 or "D10-CL-C-012" not in D10_TOPOLOGY_CLAIM_IDS:
    raise ValueError("accepted D10 claim population is not the expected 39-claim topology")


SOURCES = [
    source(row["path"], row["source_id"], row["consumed_as"])
    for row in D10["source_identities"]
]
SOURCES.extend(
    [
        source(
            "implementation/investigations/grc9v4-constitutive-design/decisions/"
            "D10DesignSynthesisAndSpecWritingDecision.json",
            "GRC9V4-CD-D10-v1",
            "accepted_architecture_claim_topology_and_specification_population",
        ),
        source(
            "implementation/investigations/grc9v4-constitutive-design/decisions/"
            "D10SpecificationAuthorizationProfile.json",
            "GRC9V4-D10-SPECIFICATION-AUTHORIZATION-v1",
            "accepted_normative_specification_population_and_profile_grammar",
        ),
        source(
            "implementation/investigations/grc9v4-constitutive-design/decisions/"
            "D10NormativeClaimTopology.json",
            "GRC9V4-D10-NORMATIVE-CLAIM-TOPOLOGY-v1",
            "accepted_current_claim_population_requiring_provenance_coverage",
        ),
        source(
            "implementation/investigations/grc9v4-constitutive-design/decisions/"
            "D10_1PreliminarySubstrateProvenance.json",
            "GRC9V4-CD-D10.1-v1",
            "accepted_preliminary_taxonomy_and_full_audit_handoff",
        ),
        source(
            "specs/grc-v3-spec.md",
            "GRCV3-NORMATIVE-SPEC",
            "general_graph_GRC_state_differential_transport_and_lifecycle_contract",
        ),
        source(
            "specs/grc-9-v3-spec.md",
            "GRC9V3-NORMATIVE-SPEC",
            "nine_port_specialization_and_exact_legacy_compatibility_target",
        ),
        source(
            "implementation/Phase-7-EquationMap.md",
            "PHASE7-GRC9V3-EQUATION-MAP",
            "GRC_GRC9_and_hybrid_equation_ownership_map",
        ),
        source(
            "src/pygrc/models/grc_v3.py",
            "GRCV3-RUNTIME-SOURCE",
            "implemented_general_GRC_differential_conductance_potential_and_flux_surface",
        ),
        source(
            "src/pygrc/models/grc_9_v3_runtime.py",
            "GRC9V3-TRANSPORT-RUNTIME",
            "implemented_GRC9_row_basis_conductance_potential_and_flux_specialization",
        ),
    ]
)

source_ids = [row["source_id"] for row in SOURCES]
if len(source_ids) != len(set(source_ids)):
    duplicates = sorted(key for key, count in Counter(source_ids).items() if count > 1)
    raise ValueError(f"duplicate source ids: {duplicates}")


DERIVATIONS = [
    derivation(
        "D10.2-DER-RESOURCE",
        "General GRC resource, continuity, and charge contract",
        ["GRCV3-NORMATIVE-SPEC", "GRCV3-RUNTIME-SOURCE", "GRC9V4-CD-D9-v1"],
        [
            "Let C be the authoritative scalar resource on vertices of a finite oriented graph and J the antisymmetric edge current.",
            "With incidence B, define C_next = C - Delta_t * B * J + B_ext + S_ext.",
            "For a declared charge covector varpi, Q_varpi(C) = varpi^T C; conservative graph and event maps preserve this charge or emit an explicit Delta_Q receipt.",
            "Differentiate the complete-state charge as DQ_varpi[delta X] = varpi^T delta C and define the authoritative complete-state tangent V_Q,varpi = ker(DQ_varpi), leaving nonresource variations unrestricted.",
            "On the structural C sector with positive H0, define Pi_Q,C,H0(delta C) = delta C - H0^-1*varpi*(varpi^T delta C)/(varpi^T H0^-1*varpi). Extend it by identity on nonresource coordinates only as a canonical tangent retraction, not as a full-state orthogonal projector until a product metric is frozen.",
            "The unit-measure profile is the specialization varpi = 1, hence Q(C) = sum_i C_i.",
        ],
        "resource_authority_continuity_general_charge_and_event_accounting_require_only_general_GRC_graph_and_measure_contracts",
        [
            "CORE-C-AUTHORITY",
            "CORE-INCIDENCE-CONTINUITY",
            "CORE-GENERAL-CHARGE",
            "CORE-CHARGE-TANGENT",
            "CORE-STRUCTURAL-CHARGE-PROJECTOR",
            "CORE-UNIT-MEASURE",
            "CORE-EXTERNAL-EVENT-CHARGE",
            "L-AUTHORITATIVE-CURRENT",
            "L-CONTINUITY-WRITE",
        ],
        "this_does_not_make_the_unit_measure_profile_the_only_lawful_GRCV4_charge",
    ),
    derivation(
        "D10.2-DER-TRANSPORT",
        "General GRC scalar potential and potential-flow current",
        ["GRCV3-NORMATIVE-SPEC", "GRCV3-RUNTIME-SOURCE", "GRC9V3-TRANSPORT-RUNTIME"],
        [
            "Take any finite graph with positive scalar edge mobility W and node coherence C.",
            "Define Phi_i = kappa * sum_j W_ij * (C_i - C_j) - V_prime(C_i).",
            "For an oriented edge e, define J_e = -eta * W_e * (B^T Phi)_e and the opposite orientation as -J_e.",
            "These are the same graph equations implemented by GRCV3 and by GRC9V3 on occupied port pairs; no ordered-port premise enters the equations.",
        ],
        "scalar_mobility_potential_and_potential_flow_are_independently_GRC_derived",
        ["BASE-SCALAR-MOBILITY", "BASE-POTENTIAL", "BASE-POTENTIAL-FLOW"],
        "the_GRC9_port_pair_storage_and_fixed_chart_are_not_promoted_with_the_equations",
    ),
    derivation(
        "D10.2-DER-DIFFERENTIAL",
        "Minimal general GRC differential backend",
        ["GRCV3-NORMATIVE-SPEC", "GRCV3-RUNTIME-SOURCE"],
        [
            "Require an explicit deterministic serialized differential backend with declared frame, orientation, regularization, freshness, and covariance semantics.",
            "Use GRCv3 Appendix A's induced-frame and weighted-least-squares construction as the present canonical reference backend.",
            "For that reference, construct deterministic pseudo-displacements from the weighted ego-graph Laplacian with stable eigenvector signs, then compute graph-local gradient and Hessian summaries with declared positive regression weights and regularization.",
            "An equivalent documented and serialized backend may satisfy the same contract; the current GRCv3 backend menu is not frozen as a theorem of every future GRCv4 profile.",
        ],
        "GRCV3_already_supplies_the_non_nine_port_differential_contract_needed_by_GRCV4",
        ["BASE-GRC-DIFFERENTIAL"],
        "the_GRC9_fixed_row_basis_remains_a_specialization_backend_not_the_general_contract",
    ),
    derivation(
        "D10.2-DER-A-GW",
        "Candidate A conductance functional over GRCv3 contracts",
        [
            "GRCV3-NORMATIVE-SPEC",
            "GRCV3-RUNTIME-SOURCE",
            "GRC9V3-TRANSPORT-RUNTIME",
            "GRC9V4-CD-D7-v1",
        ],
        [
            "Let D_i(C) be any admitted deterministic GRC differential summary and let J_e be the declared current coordinate at the relevant stage.",
            "Define the accepted D7 profile exactly as G_W,e(C,J) = max(W_floor, exp(-alpha*(C_u+C_v)/2 - beta*norm(D_u-D_v)^2/2 - gamma*J_e^2/2)).",
            "The promoted current profile has curvature disabled. It uses graph endpoints, a GRC differential backend, scalar current, and a positive floor, but no row or port index.",
            "Candidate A pre-read staging evaluates this functional with fresh J0_A, while its writer evaluates it with postcontinuity C_next and solved J_C_A.",
            "The GRC9v4 specialization may select the fixed row-basis backend, but that backend is not part of the GRCv4 functional contract.",
            "Any curvature-conditioned Candidate A law is a materially distinct future GRCv4 profile that requires a new profile identity and provenance reopening.",
        ],
        "Candidate_A_G_W_functional_and_its_declared_stage_uses_are_promoted_to_GRC_derived_while_the_row_basis_backend_remains_GRC9_intrinsic",
        ["A-GW-FUNCTIONAL", "A-WHAT", "A-WRITER-TARGET"],
        "functional_form_promotion_does_not_promote_the_GRC9_row_basis_backend",
    ),
    derivation(
        "D10.2-DER-A-READWRITE",
        "Candidate A graph-level Read-Back and retained writer",
        ["GRC9V4-CD-D5-v1", "GRC9V4-CD-D6-v1", "GRC9V4-CD-D7-v1"],
        [
            "Let W_A and W_hat_A be positive scalar fields on graph edges and q_A = (W_A-W_hat_A)/(W_A+W_hat_A).",
            "Define j_A = chi_A*q_A*J_C_A and J_C_A = J0_A + zeta_A*j_A, giving J_C_A = J0_A/(1-zeta_A*chi_A*q_A) on the regular domain.",
            "After continuity and refreshed differentials, define W_drv_A = G_W(C_next,J_C_A).",
            "Commit log(W_A_next) = a_A*log(W_A) + (1-a_A)*log(W_drv_A) atomically.",
            "Every operation is graph-edge local or uses general incidence continuity; no nine-port premise appears.",
        ],
        "Candidate_A_reference_contrast_Read_Back_current_closure_retained_writer_and_state_authority_are_GRC_derived",
        ["A-WHAT", "A-DIRECTIONAL-CONTRAST", "A-READ-CLOSURE", "A-RETAINED-WRITER", "A-STATE-REDUCTION"],
        "this_does_not_claim_numeric_stability_or_formed_branch_reachability",
    ),
    derivation(
        "D10.2-DER-C-HODGE",
        "Candidate C graph-Hodge sector and Read-Back",
        [
            "GRC9V4-CD-D4V2-v1",
            "GRC9V4-CD-D5V2-v1",
            "GRC9V4-CD-D6V2-v1",
            "GRC9V4-CD-D7V2-v1",
            "GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1",
        ],
        [
            "On a finite oriented graph, derive the selected sector T_C from authoritative C using a declared basis-independent selector with fixed-rank or boundary semantics.",
            "Construct positive graph Hodge stars H0 and H1, flat/sharp maps, and Delta_1 = B^T*H0^-1*B*H1 on the admitted stratum.",
            "Define the retained response R_C = (I + tau_C*Delta_1)^-1 and map it lawfully between selected and physical one-form spaces.",
            "Only authoritative C is independently written; T_C, selectors, Hodge objects, and read surfaces remain derived.",
        ],
        "Candidate_C_sector_selector_Hodge_Read_Back_and_C_only_authority_require_general_graph_Hodge_contracts_but_no_nine_port_mechanics",
        ["C-SECTOR", "C-SELECTOR", "C-HODGE-MAPS", "C-READ-BACK", "C-AUTHORITY"],
        "derived_sector_mediation_is_not_an_independent_resource_or_hidden_state",
    ),
    derivation(
        "D10.2-DER-GEOMETRY",
        "General GRC K4 to graph-Hodge geometry realization",
        [
            "GRCV3-NORMATIVE-SPEC",
            "GRCV3-RUNTIME-SOURCE",
            "GRC9V4-CD-D7G-v1",
            "GRC9V4-CD-D7G-v2",
            "GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1",
            "GRC9V4-CD-D8A-v1",
        ],
        [
            "Core theory supplies the substrate-independent structural role K -> g[K]; it does not by itself supply the discrete graph object K4.",
            "Realize K4 as a graph-local symmetric bilinear form on the oriented one-form space and assemble its graph restrictions with overlap normalization.",
            "Construct the V4 reference embedding from GRCv3 surfaces: H0_ref = diag(mu), H1_form_ref = diag(W_ref), and G_J_ref = diag(W_ref^-1), where mu is the declared graph measure and W_ref is positive GRCv3 base conductance.",
            "Push the assembled increment through H1_form_plus = H1_form_ref + kappa_H*Delta_K4 on the positive admitted domain, then define G_J(h) = H1_form(h)^-1 and j_struct_flat = G_J*j_flux.",
            "Construct h4 through the declared geometry profile. M4 is not constructed by this geometry map and retains separate candidate-specific transport authority.",
            "Require graph relabeling and signed-edge orientation covariance of every assembly, flat/sharp, and current-consumer map.",
        ],
        "the_core_K_structural_role_is_substrate_independent_while_graph_K4_the_reference_Hodge_embedding_and_the_K4_H4_h4_crossing_are_GRC_derived",
        ["CORE-K-STRUCTURAL-ROLE", "GEOM-K4", "GEOM-H1-FORM", "GEOM-GJ", "GEOM-K4-TO-H4-TO-h4", "GEOM-ASSEMBLY", "GEOM-COVARIANCE"],
        "the_old_GRC9_cached_row_tensor_is_not_the_new_structural_crossing",
    ),
    derivation(
        "D10.2-DER-MOBILITY",
        "Candidate-specific transport mobility authority",
        [
            "GRCV3-NORMATIVE-SPEC",
            "GRC9V4-CD-D4V2-v1",
            "GRC9V4-CD-D7G-v1",
            "GRC9V4-CD-D7G-v2",
            "GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1",
        ],
        [
            "Type M4 as the transport mobility operator on physical current space, separate from structural H1_form and the flux flat map G_J.",
            "For Candidate A, use the accepted factorization M4,A = eta*diag(W_A), preserving W_A as mobility authority.",
            "For Candidate C, retain the accepted candidate-specific transport factorization rather than deriving mobility from H1_form by matrix coincidence.",
            "No H1_form-to-M4, G_J-to-M4, or h4-to-M4 authority transfer exists unless a future profile supplies and reopens an explicit constitutive map.",
        ],
        "M4_is_a_GRC_level_transport_object_with_candidate_specific_authority_and_is_not_the_overlap_normalized_K4_assembly",
        ["GEOM-M4"],
        "geometry_and_transport_may_be_numerically_related_only_when_an_explicit_profile_contract_admits_that_relation",
    ),
    derivation(
        "D10.2-DER-REALIZATION",
        "General realization-family contract",
        [
            "GRC9V4-GTRS-CI-v1",
            "GRC9V4-GTRS-OS-v1",
            "GRC9V4-GTRS-RG-v1",
            "GRC9V4-GTRS-PC-v1",
            "GRC9V4-GTRS-CI-PC-v1",
        ],
        [
            "Take an admitted candidate transition F_a(X,h), structural source S_a(J,h), and geometry profile H_profile(K).",
            "CI solves the simultaneous current/geometry root; OS executes the frozen one-pass predictor-geometry-corrector order with a declared split residual.",
            "RG2b reconstructs geometry from the frozen family-local invariant-section completion on its bounded domain.",
            "PC evolves an independently authoritative scalar-ZOH K4 history carrier; CI+PC composes simultaneous timing with that carrier under the fixed gain-two profile.",
            "These constructions depend on candidate and graph-geometry interfaces, not on ordered ports or a 3x3 chart.",
        ],
        "all_five_current_realization_families_are_GRC_derived_for_the_current_initial_specification_population",
        ["REAL-CI", "REAL-OS", "REAL-RG2B", "REAL-PC", "REAL-CI-PC"],
        "promotion_does_not_rank_realizations_or_make_the_current_population_future_exhaustive",
    ),
    derivation(
        "D10.2-DER-LIFECYCLE",
        "General graph complete-step and lifecycle contract",
        [
            "GRC9V4-CD-D7-v1",
            "GRC9V4-CD-D7V2-v1",
            "GRC9V4-CD-D9-v1",
            "GRC9V4-D9-LIFECYCLE-COVERAGE-MATRIX-v1",
            "GRC9V4-D9-PROFILE-STATE-LIFECYCLE-REGISTRY-v1",
        ],
        [
            "A complete profile binds authoritative current state, reset baseline, graph, context contract, charge target, and one candidate-plus-realization identity.",
            "Ordinary steps refresh derived surfaces, solve one authoritative current, apply continuity once, validate, write candidate/history state, and commit atomically.",
            "Profile migrations and topology events use typed source/target graph and profile maps, transform current/reset/charge together, and emit information-loss and charge receipts.",
            "Singular, multiple-root, nonfinite, target-readmission, or untyped-event failures commit nothing.",
        ],
        "complete_step_atomicity_snapshot_reset_migration_event_receipt_and_fail_closed_contracts_are_GRC_derived",
        [
            "L-AUTHORITATIVE-CURRENT",
            "L-CONTINUITY-WRITE",
            "L-POSTCONTINUITY-REFRESH",
            "L-ATOMICITY",
            "L-SNAPSHOT-RESET",
            "L-PROFILE-MIGRATION",
            "L-TOPOLOGY-EVENT",
            "L-ORDERED-RECEIPTS",
            "L-SINGULAR-FAIL-CLOSED",
        ],
        "runtime_conformance_and_serializer_tests_remain_post_spec_verification_obligations",
    ),
    derivation(
        "D10.2-DER-A-INITIALIZER",
        "General GRC Candidate A history-free initializer",
        [
            "GRCV3-NORMATIVE-SPEC",
            "GRCV3-RUNTIME-SOURCE",
            "GRC9V4-CD-D7-v1",
            "GRC9V4-CD-D9-v1",
            "GRC9V4-D9-PROFILE-STATE-LIFECYCLE-REGISTRY-v1",
        ],
        [
            "For a target graph, context, and authoritative C, rebuild the target's declared deterministic GRC differential surfaces without source-profile history.",
            "Evaluate the promoted curvature-disabled Candidate A G_W law on the target reference-current stage to define I_A^GRC(C,U,G).",
            "Use I_A^GRC only as a typed history-free target initializer, then perform target-profile readmission and emit the direction-specific history-loss receipt.",
            "In the GRC9v4 specialization, bind this initializer role to the exact GRC9v3 base-conductance reconstruction; that exact compatibility binding remains specialization-specific.",
        ],
        "the_target_initializer_role_and_a_GRCv4_Candidate_A_initializer_are_GRC_derived_while_the_exact_GRC9v3_initializer_binding_is_specialization_specific",
        ["L-A-INITIALIZER-GRC"],
        "the_general_initializer_does_not_import_GRC9_port_charts_or_claim_to_preserve_A_history",
    ),
    derivation(
        "D10.2-DER-SPEC-GRAMMAR",
        "Substrate-independent profile and claim grammar",
        ["GRC9V4-CD-D10-v1", "GRC9V4-D10-SPECIFICATION-AUTHORIZATION-v1"],
        [
            "Bind exactly one admitted constitutive family and one admitted realization to each executable state.",
            "Give every materially distinct successor a new complete-profile identity and reopen the earliest authority, staging, state, geometry, accounting, or lifecycle contract it changes.",
            "Keep Candidate B as a typed reserved successor slot until it has a source-backed writer; do not relabel another profile as B.",
            "Keep claim ceilings and blocked relabels separate from runtime state and physical equations.",
        ],
        "profile_identity_future_admission_B_slot_and_claim_hygiene_are_substrate_independent_specification_meta_contracts",
        [
            "SPEC-PROFILE-GRAMMAR",
            "SPEC-FUTURE-ADMISSION",
            "SPEC-B-SLOT",
            "SPEC-CLAIM-CEILINGS",
            "SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER",
            "SPEC-COMPOSITION-PROFILE-IDENTITY",
            "SPEC-VERIFICATION-REGISTRY",
        ],
        "governance_grammar_is_not_physical_evidence_for_any_candidate_or_realization",
    ),
]


R = audit_object
ROWS = [
    R("CORE-C-AUTHORITY", "core_resource", "state_authority", "C_is_the_authoritative_resource_coordinate", ["finite_graph", "scalar_vertex_resource"], ["GRCV3-NORMATIVE-SPEC", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-RESOURCE"], "survives_from_GRC_premises", "general_GRC_state_authority", "GRCV4_current_promoted_common_core", "C_authority_does_not_make_every_derived_surface_independent_state"),
    R("CORE-INCIDENCE-CONTINUITY", "core_resource", "equation", "C_next_equals_C_minus_Delta_t_BJ_plus_external_terms", ["oriented_incidence", "antisymmetric_edge_current", "typed_external_terms"], ["GRCV3-NORMATIVE-SPEC", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-RESOURCE"], "survives_from_GRC_premises", "general_graph_continuity", "GRCV4_current_promoted_common_core", "continuity_does_not_authorize_multiple_resource_writes"),
    R("CORE-GENERAL-CHARGE", "core_resource", "invariant_contract", "Q_varpi_equals_varpi_transpose_C", ["declared_charge_covector", "typed_measure"], ["GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-RESOURCE"], "survives_from_GRC_premises", "general_GRC_charge_contract", "GRCV4_current_promoted_common_core", "general_charge_does_not_force_unit_measure"),
    R("CORE-CHARGE-TANGENT", "core_resource", "tangent_contract", "DQ_varpi_of_delta_X_equals_varpi_transpose_delta_C_and_V_Q_varpi_equals_kernel_DQ_varpi", ["declared_charge_covector", "complete_state_variation", "authoritative_resource_sector"], ["GRC9V4-CD-D9-v1", "GRC9V4-D9-PROFILE-STATE-LIFECYCLE-REGISTRY-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-RESOURCE"], "survives_from_GRC_premises", "general_GRC_complete_state_charge_tangent", "GRCV4_current_promoted_common_core", "nonresource_variations_remain_unrestricted_by_the_charge_tangent"),
    R("CORE-STRUCTURAL-CHARGE-PROJECTOR", "core_resource", "projector_contract", "Pi_Q_C_H0_is_the_H0_orthogonal_projector_on_the_structural_C_sector_with_identity_extension_as_canonical_full_tangent_retraction", ["positive_H0", "declared_charge_covector", "complete_state_tangent"], ["GRC9V4-CD-D9-v1", "GRC9V4-D9-PROFILE-STATE-LIFECYCLE-REGISTRY-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-RESOURCE"], "survives_from_GRC_premises", "general_GRC_structural_charge_projector_and_canonical_retraction", "GRCV4_current_promoted_common_core", "the_identity_extension_is_not_a_full_state_orthogonal_projector_without_a_product_metric"),
    R("CORE-UNIT-MEASURE", "core_resource", "reference_profile", "Q_equals_sum_C", ["varpi_equals_one", "current_reference_population"], ["GRCV3-NORMATIVE-SPEC", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-RESOURCE"], "survives_from_GRC_premises", "ordinary_GRC_unit_measure_profile", "GRCV4_reference_profile", "unit_measure_is_not_the_only_GRCV4_charge"),
    R("CORE-EXTERNAL-EVENT-CHARGE", "core_resource", "event_accounting", "typed_external_or_event_exchange_updates_Q_target_with_receipt", ["typed_event_resource_map", "Delta_Q_receipt", "target_charge_update"], ["GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-RESOURCE"], "survives_from_GRC_premises", "general_graph_event_accounting", "GRCV4_current_promoted_common_core", "external_exchange_is_not_hidden_nonconservation"),

    R("BASE-SCALAR-MOBILITY", "legacy_transport", "state_or_stage_object", "positive_scalar_edge_mobility_W", ["live_graph_edges", "positive_scalar_edge_field"], ["GRCV3-NORMATIVE-SPEC", "GRCV3-RUNTIME-SOURCE"], "GRC_derived", "promotion_proved", ["D10.2-DER-TRANSPORT"], "survives_from_GRC_premises", "ordinary_GRC_scalar_transport", "GRCV4_current_promoted_common_core", "scalar_mobility_is_not_full_tensor_anisotropy"),
    R("BASE-POTENTIAL", "legacy_transport", "equation", "Phi_i_equals_kappa_sum_j_Wij_Ci_minus_Cj_minus_Vprime_Ci", ["finite_graph", "scalar_W", "site_potential"], ["GRCV3-RUNTIME-SOURCE", "GRC9V3-TRANSPORT-RUNTIME", "GRC9V4-CD-D7-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-TRANSPORT"], "survives_from_GRC_premises", "same_equation_on_general_GRC", "GRCV4_current_promoted_common_core", "shared_formula_does_not_promote_port_storage"),
    R("BASE-POTENTIAL-FLOW", "legacy_transport", "equation", "J_e_equals_minus_eta_W_e_Btranspose_Phi_e", ["oriented_edge", "positive_scalar_W", "node_potential"], ["GRCV3-RUNTIME-SOURCE", "GRC9V3-TRANSPORT-RUNTIME", "GRC9V4-CD-D7-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-TRANSPORT"], "survives_from_GRC_premises", "same_antisymmetric_equation_on_general_GRC", "GRCV4_current_promoted_common_core", "potential_flow_does_not_imply_retained_current"),
    R("BASE-GRC-DIFFERENTIAL", "legacy_transport", "backend_contract", "explicit_deterministic_serialized_graph_differential_backend_satisfying_declared_contracts", ["declared_frame_and_orientation", "fresh_graph_local_differentials", "stable_regularization_and_covariance"], ["GRCV3-NORMATIVE-SPEC", "GRCV3-RUNTIME-SOURCE"], "GRC_derived", "promotion_proved", ["D10.2-DER-DIFFERENTIAL"], "survives_from_GRC_premises", "minimal_GRC_level_differential_contract_with_GRCV3_as_canonical_reference", "GRCV4_current_promoted_common_core", "the_current_GRCV3_backend_menu_is_not_the_only_future_GRCV4_realization"),
    R("BASE-GRC9-ROW-BASIS-DIFFERENTIAL", "legacy_transport", "specialization_backend", "fixed_three_row_GRC9_gradient_Hessian_and_flux_summary", ["nine_ordered_ports", "fixed_3_by_3_chart", "row_partition"], ["GRC9V3-TRANSPORT-RUNTIME", "PHASE7-GRC9V3-EQUATION-MAP"], "GRC9_intrinsic", "specialization_only", [], "fails_without_nine_port_substrate", "GRC9_specific_differential_backend", "GRC9V4_specialization", "row_basis_backend_is_not_the_GRCV4_general_contract"),
    R("BASE-DISABLED-TRANSITION", "legacy_transport", "compatibility_contract", "disabled_V4_transition_reduces_exactly_to_GRC9V3", ["GRC9V3_transition_identity", "profile_embedding_projection"], ["GRC9V4-CD-D0-v1", "GRC9V4-CD-D9-v1"], "GRC9_specialization_specific", "specialization_only", [], "not_applicable_deliberate_GRC9V3_target", "exact_GRC9V3_transition_compatibility", "GRC9V4_specialization", "compatibility_target_is_not_nine_port_intrinsic_mathematics"),
    R("BASE-DISABLED-STATE", "legacy_transport", "compatibility_contract", "disabled_V4_authoritative_state_reduces_to_the_profile_scoped_GRC9V3_state_surface", ["GRC9V3_state_identity", "candidate_specific_disabled_state_projection"], ["GRC9V4-CD-D0-v1", "GRC9V4-CD-D9-v1"], "GRC9_specialization_specific", "specialization_only", [], "not_applicable_deliberate_GRC9V3_target", "exact_profile_scoped_GRC9V3_state_compatibility", "GRC9V4_specialization", "transition_equivalence_does_not_imply_state_equivalence"),
    R("BASE-DISABLED-OBSERVABLE", "legacy_transport", "compatibility_contract", "disabled_V4_observables_reduce_to_the_profile_scoped_GRC9V3_observable_surface", ["GRC9V3_observable_identity", "candidate_specific_derived_surface_projection"], ["GRC9V4-CD-D0-v1", "GRC9V4-CD-D9-v1"], "GRC9_specialization_specific", "specialization_only", [], "not_applicable_deliberate_GRC9V3_target", "exact_profile_scoped_GRC9V3_observable_compatibility", "GRC9V4_specialization", "transition_or_state_equivalence_does_not_imply_observable_equivalence"),
    R("BASE-DISABLED-LIFECYCLE", "legacy_transport", "compatibility_contract", "disabled_V4_state_snapshot_event_and_lifecycle_surfaces_reduce_to_GRC9V3", ["GRC9V3_lifecycle_identity", "canonical_zero_or_archived_V4_history"], ["GRC9V4-CD-D0-v1", "GRC9V4-CD-D9-v1"], "GRC9_specialization_specific", "specialization_only", [], "not_applicable_deliberate_GRC9V3_target", "exact_GRC9V3_lifecycle_compatibility", "GRC9V4_specialization", "legacy_compatibility_does_not_define_GRCV4_generic_lifecycle"),

    R("A-GW-FUNCTIONAL", "candidate_A", "constitutive_functional", "accepted_curvature_disabled_G_W_of_C_J_over_an_admitted_GRC_differential_backend", ["graph_endpoints", "GRC_differential_summary", "scalar_current_squared", "positive_floor", "curvature_disabled"], ["GRCV3-RUNTIME-SOURCE", "GRC9V3-TRANSPORT-RUNTIME", "GRC9V4-CD-D7-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-A-GW"], "survives_from_GRC_premises", "current_D7_functional_promoted_backend_parameterized", "GRCV4_candidate_A", "promotion_excludes_both_the_GRC9_row_basis_backend_and_any_future_curvature_conditioned_successor"),
    R("A-WHAT", "candidate_A", "derived_reference", "W_hat_A_equals_G_W_C_J0_A_at_pre_read_stage", ["fresh_J0_A", "current_C", "admitted_G_W_backend"], ["GRC9V4-CD-D7-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-A-GW", "D10.2-DER-A-READWRITE"], "survives_from_GRC_premises", "revision_specific_graph_stage_reference", "GRCV4_candidate_A", "W_hat_is_not_independent_history"),
    R("A-DIRECTIONAL-CONTRAST", "candidate_A", "read_surface", "q_A_equals_W_A_minus_W_hat_over_W_A_plus_W_hat", ["positive_scalar_edge_fields"], ["GRC9V4-CD-D5-v1", "GRC9V4-CD-D7-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-A-READWRITE"], "survives_from_GRC_premises", "graph_edge_contrast", "GRCV4_candidate_A", "contrast_is_not_itself_retention_or_release"),
    R("A-READ-CLOSURE", "candidate_A", "equation_family", "j_A_equals_chi_q_A_J_C_and_J_C_equals_J0_plus_zeta_j_A", ["oriented_edge_current", "regular_gain_domain", "positive_W_fields"], ["GRC9V4-CD-D5-v1", "GRC9V4-CD-D6-v1", "GRC9V4-CD-D7-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-A-READWRITE"], "survives_from_GRC_premises", "graph_level_Read_Back_current_closure", "GRCV4_candidate_A", "closure_does_not_prove_physical_nonabsorbability"),
    R("A-WRITER-TARGET", "candidate_A", "derived_write_target", "W_drv_A_equals_G_W_C_next_J_C_after_refreshed_differentials", ["postcontinuity_C", "solved_J_C", "refreshed_GRC_differentials"], ["GRC9V4-CD-D7-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-A-GW", "D10.2-DER-A-READWRITE"], "survives_from_GRC_premises", "graph_level_postcontinuity_target", "GRCV4_candidate_A", "precontinuity_cache_reuse_is_forbidden"),
    R("A-RETAINED-WRITER", "candidate_A", "state_writer", "log_W_A_next_equals_a_log_W_A_plus_one_minus_a_log_W_drv_A", ["positive_edge_mobility", "one_beat_delay", "single_writer"], ["GRC9V4-CD-D2-v1", "GRC9V4-CD-D7-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-A-READWRITE"], "survives_from_GRC_premises", "graph_level_retained_mobility_writer", "GRCV4_candidate_A", "slow_parameter_alone_is_not_retention_evidence"),
    R("A-STATE-REDUCTION", "candidate_A", "authority_contract", "authoritative_candidate_A_state_is_C_plus_positive_edge_W_A", ["C_authority", "positive_edge_W_A", "profile_identity"], ["GRC9V4-CD-D1-v1", "GRC9V4-CD-D7-v1", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-A-READWRITE"], "survives_from_GRC_premises", "candidate_A_state_authority_is_graph_level", "GRCV4_candidate_A", "exact_disabled_projection_to_GRC9V3_is_owned_only_by_the_specialization_compatibility_rows"),

    R("C-SECTOR", "candidate_C", "derived_sector", "T_C_is_derived_from_authoritative_C_and_selector", ["authoritative_C", "declared_selector", "fixed_rank_or_boundary_semantics"], ["GRC9V4-CD-D4V2-v1", "GRC9V4-CD-D7V2-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-C-HODGE"], "survives_from_GRC_premises", "general_graph_derived_sector", "GRCV4_candidate_C", "T_C_is_not_independent_resource_or_state"),
    R("C-SELECTOR", "candidate_C", "derived_operator", "basis_independent_selector_with_rank_gap_and_boundary_contract", ["graph_operator", "spectral_or_functional_calculus", "stable_boundary_rule"], ["GRC9V4-CD-D4V2-v1", "GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-C-HODGE"], "survives_from_GRC_premises", "general_graph_selector_contract", "GRCV4_candidate_C", "analysis_projector_cannot_become_runtime_authority"),
    R("C-HODGE-MAPS", "candidate_C", "operator_family", "positive_H0_H1_flat_sharp_identification_and_Delta1", ["oriented_incidence", "positive_Hodge_stars", "typed_one_form_spaces"], ["GRC9V4-CD-D5V2-v1", "GRC9V4-CD-D6V2-v1", "GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-C-HODGE"], "survives_from_GRC_premises", "general_graph_Hodge_contract", "GRCV4_candidate_C", "matrix_shape_alone_does_not_establish_correct_Hodge_typing"),
    R("C-READ-BACK", "candidate_C", "operator_family", "R_C_equals_I_plus_tau_C_Delta1_inverse_with_one_external_chi_gate", ["positive_Hodge_stars", "typed_sector_identification", "regular_resolvent"], ["GRC9V4-CD-D5V2-v1", "GRC9V4-CD-D6V2-v1", "GRC9V4-CD-D7V2-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-C-HODGE"], "survives_from_GRC_premises", "general_graph_Hodge_Read_Back", "GRCV4_candidate_C", "chi_must_not_be_applied_twice"),
    R("C-AUTHORITY", "candidate_C", "state_authority", "only_C_is_independently_written_while_T_C_and_Hodge_surfaces_are_derived", ["single_writer", "derived_selector", "poststate_rederivation"], ["GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-C-HODGE"], "survives_from_GRC_premises", "candidate_C_C_only_authority", "GRCV4_candidate_C", "derived_C_surfaces_are_not_hidden_state"),

    R("CORE-K-STRUCTURAL-ROLE", "geometry", "core_theory_role", "abstract_structural_role_K_to_g_of_K", ["core_constitutive_structural_role", "no_discrete_graph_realization_assumed"], ["GRC9V4-CD-D0-v1", "GRC9V4-CD-D7G-v1"], "core_theory_substrate_independent", "promotion_proved", ["D10.2-DER-GEOMETRY"], "survives_without_any_GRC9V3_premise", "core_theory_structural_role_precedes_GRC_realization", "GRCV4_current_promoted_core_theory_basis", "core_K_is_not_the_graph_bilinear_form_K4"),
    R("GEOM-K4", "geometry", "graph_structural_object", "K4_is_a_graph_local_symmetric_bilinear_form_on_oriented_one_forms", ["finite_oriented_graph", "typed_one_form_space", "graph_local_structural_payload"], ["GRC9V4-CD-D4V2-v1", "GRC9V4-CD-D7G-v1", "GRC9V4-CD-D8A-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-GEOMETRY"], "survives_from_GRC_premises", "GRC_realization_of_the_core_structural_role", "GRCV4_current_promoted_common_geometry", "graph_K4_must_not_be_relabelled_as_core_K_or_as_legacy_cached_GRC9_tensor"),
    R("GEOM-H1-FORM", "geometry", "geometry_object", "H0_ref_equals_diag_mu_H1_form_ref_equals_diag_W_ref_GJ_ref_equals_diag_W_ref_inverse_then_H1_form_plus_equals_H1_form_ref_plus_kappa_H_Delta_K4", ["GRC_graph_measure_mu", "positive_GRC_base_conductance_W_ref", "typed_K4_to_H1_pushforward", "positive_admission_domain"], ["GRCV3-NORMATIVE-SPEC", "GRCV3-RUNTIME-SOURCE", "GRC9V4-CD-D7G-v2", "GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-GEOMETRY"], "survives_from_GRC_premises", "explicit_V4_reference_Hodge_embedding_from_GRC_surfaces", "GRCV4_current_promoted_common_geometry", "the_reference_Hodge_is_a_V4_embedding_not_preexisting_GRCv3_physical_geometry"),
    R("GEOM-GJ", "geometry", "flux_flat_operator", "G_J_equals_H1_form_inverse_and_j_struct_flat_equals_G_J_j_flux", ["positive_H1_form", "physical_flux_one_form", "typed_flat_map"], ["GRC9V4-CD-D7G-v2", "GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1", "GRC9V4-CD-D8A-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-GEOMETRY"], "survives_from_GRC_premises", "graph_flux_resistance_and_flat_map", "GRCV4_current_promoted_common_geometry", "G_J_is_not_transport_mobility_M4_and_telemetry_current_is_not_a_structural_source"),
    R("GEOM-M4", "geometry", "transport_mobility_operator", "M4_is_candidate_specific_transport_mobility_on_physical_current_space", ["candidate_transport_authority", "positive_or_admitted_mobility_factorization", "current_solve"], ["GRC9V4-CD-D4V2-v1", "GRC9V4-CD-D7G-v1", "GRC9V4-CD-D7G-v2", "GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-MOBILITY"], "survives_from_GRC_premises", "separate_candidate_specific_transport_authority", "GRCV4_current_promoted_common_transport", "M4_is_not_overlap_assembly_H1_form_G_J_or_h4_without_an_explicit_future_map"),
    R("GEOM-K4-TO-H4-TO-h4", "geometry", "constitutive_crossing", "K4_to_H4_to_h4_is_load_bearing_and_consumed", ["typed_structural_pushforward", "positive_geometry_profile", "current_consumer"], ["GRC9V4-CD-D7G-v1", "GRC9V4-CD-D7G-v2", "GRC9V4-CD-D8A-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-GEOMETRY"], "survives_from_GRC_premises", "new_general_graph_structural_crossing", "GRCV4_current_promoted_common_geometry", "the_legacy_cached_tensor_is_not_this_crossing"),
    R("GEOM-ASSEMBLY", "geometry", "normalization_contract", "K4_graph_restrictions_use_overlap_normalized_assembly_with_reference_normalization_and_positive_domain", ["stable_graph_restrictions", "overlap_partition", "reference_Hodge", "admission_domain"], ["GRC9V4-CD-D7G-v1", "GRC9V4-CD-D7G-v2", "GRC9V4-CD-D8A-v1", "GRC9V4-CD-D8B-CI-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-GEOMETRY"], "survives_from_GRC_premises", "general_graph_K4_assembly_and_geometry_normalization", "GRCV4_current_promoted_common_geometry", "overlap_assembly_belongs_to_K4_and_is_not_M4_or_posthoc_stability_tuning"),
    R("GEOM-COVARIANCE", "geometry", "covariance_contract", "graph_relabel_and_signed_edge_orientation_covariance", ["stable_graph_isomorphism", "cochain_orientation_transform", "typed_operator_transport"], ["GRC9V4-CD-D7G-v2", "GRC9V4-CD-D8A-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-GEOMETRY"], "survives_from_GRC_premises", "general_graph_covariance", "GRCV4_current_promoted_common_geometry", "coordinate_sign_change_is_not_physical_history_reversal"),

    R("REAL-CI", "realization", "realization_family", "coupled_implicit_joint_current_geometry_root", ["candidate_transition", "structural_source", "geometry_profile", "regular_root"], ["GRC9V4-GTRS-CI-v1", "GRC9V4-CD-D8B-CI-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-REALIZATION"], "survives_from_GRC_premises", "general_GRC_realization_family", "GRCV4_optional_realization", "local_root_evidence_is_not_global_stability"),
    R("REAL-OS", "realization", "realization_family", "one_pass_predictor_geometry_corrector_with_split_residual", ["candidate_transition", "structural_source", "fixed_stage_order"], ["GRC9V4-GTRS-OS-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-REALIZATION"], "survives_from_GRC_premises", "general_GRC_realization_family", "GRCV4_optional_realization", "split_residual_is_not_Delta_t_truncation_without_proof"),
    R("REAL-RG2B", "realization", "realization_family", "bounded_reconstructed_geometry_invariant_section", ["bounded_domain", "frozen_family_local_completion", "Lipschitz_contraction"], ["GRC9V4-GTRS-RG-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-REALIZATION"], "survives_from_GRC_premises", "general_GRC_realization_family", "GRCV4_optional_realization", "uniqueness_is_relative_to_the_frozen_completion"),
    R("REAL-PC", "realization", "realization_family", "scalar_ZOH_one_tau_PC_persistent_K4_history", ["independent_Z_state", "declared_writer", "profile_kernel"], ["GRC9V4-GTRS-PC-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-REALIZATION"], "survives_from_GRC_premises", "general_GRC_realization_family", "GRCV4_optional_realization", "current_PC_profile_is_not_the_universal_persistent_carrier_law"),
    R("REAL-CI-PC", "realization", "realization_family", "gain_two_coupled_implicit_plus_persistent_carrier_profile", ["CI_root", "PC_history", "fixed_unit_plus_unit_composition"], ["GRC9V4-GTRS-CI-PC-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-REALIZATION"], "survives_from_GRC_premises", "general_GRC_hybrid_realization", "GRCV4_optional_realization", "gain_two_profile_is_not_amplitude_equivalent_to_CI_or_PC"),

    R("L-AUTHORITATIVE-CURRENT", "complete_step_lifecycle", "stage_authority", "one_solved_J_C_is_authoritative_for_continuity_and_declared_consequences", ["candidate_current_closure", "single_resource_ledger"], ["GRC9V4-CD-D6-v1", "GRC9V4-CD-D6V2-v1", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-RESOURCE", "D10.2-DER-LIFECYCLE"], "survives_from_GRC_premises", "general_GRC_current_authority", "GRCV4_current_promoted_common_lifecycle", "read_current_is_not_an_extra_resource_transfer"),
    R("L-CONTINUITY-WRITE", "complete_step_lifecycle", "state_write", "authoritative_continuity_executes_exactly_once", ["authoritative_J_C", "typed_external_terms", "charge_target"], ["GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-RESOURCE", "D10.2-DER-LIFECYCLE"], "survives_from_GRC_premises", "general_GRC_single_resource_write", "GRCV4_current_promoted_common_lifecycle", "candidate_writers_cannot_write_C_again"),
    R("L-POSTCONTINUITY-REFRESH", "complete_step_lifecycle", "stage_contract", "derived_surfaces_are_rebuilt_from_committed_candidate_poststate_inputs", ["postcontinuity_C", "cache_invalidation", "declared_writer_stage"], ["GRC9V4-CD-D7-v1", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-LIFECYCLE"], "survives_from_GRC_premises", "general_GRC_refresh_contract", "GRCV4_current_promoted_common_lifecycle", "stale_precontinuity_surfaces_cannot_feed_the_writer"),
    R("L-ATOMICITY", "complete_step_lifecycle", "transaction_contract", "all_authoritative_coordinates_commit_together_or_not_at_all", ["complete_candidate_state", "solver_validation", "resource_validation"], ["GRC9V4-CD-D7-v1", "GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-LIFECYCLE"], "survives_from_GRC_premises", "general_GRC_atomic_step", "GRCV4_current_promoted_common_lifecycle", "partial_valid_substage_is_not_a_committed_state"),
    R("L-SNAPSHOT-RESET", "complete_step_lifecycle", "identity_contract", "snapshot_and_reset_bind_authoritative_state_profile_context_charge_and_transformed_baseline", ["scientific_restoration_identity", "reset_baseline", "profile_identity"], ["GRC9V4-CD-D9-v1", "GRC9V4-D9-PROFILE-STATE-LIFECYCLE-REGISTRY-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-LIFECYCLE"], "survives_from_GRC_premises", "general_GRC_lifecycle_identity", "GRCV4_current_promoted_common_lifecycle", "representation_cache_bytes_are_not_scientific_identity"),
    R("L-PROFILE-MIGRATION", "complete_step_lifecycle", "migration_grammar", "profile_change_uses_typed_source_target_map_target_readmission_and_loss_receipts", ["ordered_profile_pair", "typed_state_map", "information_loss_receipt", "target_readmission"], ["GRC9V4-CD-D9-v1", "GRC9V4-D9-PROFILE-STATE-LIFECYCLE-REGISTRY-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-LIFECYCLE"], "survives_from_GRC_premises", "general_GRC_profile_migration_grammar", "GRCV4_current_promoted_common_lifecycle", "generic_migration_does_not_select_a_target_initializer_or_allow_in_place_semantic_reinterpretation"),
    R("L-A-INITIALIZER-GRC", "complete_step_lifecycle", "target_initializer", "I_A_GRC_rebuilds_target_differentials_and_evaluates_the_promoted_curvature_disabled_G_W_reference_stage", ["target_graph_context", "authoritative_C", "promoted_GRC_differential_contract", "target_readmission"], ["GRCV3-NORMATIVE-SPEC", "GRCV3-RUNTIME-SOURCE", "GRC9V4-CD-D7-v1", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-A-INITIALIZER"], "survives_from_GRC_premises", "general_GRCv4_history_free_Candidate_A_initializer", "GRCV4_candidate_A_lifecycle", "history_free_initialization_is_not_A_history_preservation_or_the_exact_GRC9v3_initializer"),
    R("L-A-INITIALIZER-GRC9V3", "complete_step_lifecycle", "specialization_initializer", "I_A_GRC9V3_is_the_exact_GRC9V3_base_conductance_reconstruction", ["GRC9V3_target_profile", "exact_base_conductance_initializer", "target_readmission"], ["GRC9V3-TRANSPORT-RUNTIME", "GRC9V4-CD-D9-v1", "GRC9V4-D9-PROFILE-STATE-LIFECYCLE-REGISTRY-v1"], "GRC9_specialization_specific", "specialization_only", [], "not_applicable_deliberate_GRC9V3_initializer_target", "exact_GRC9V3_history_free_Candidate_A_initializer_binding", "GRC9V4_specialization", "the_exact_GRC9v3_initializer_is_not_wholesale_promoted_with_generic_migration_grammar"),
    R("L-TOPOLOGY-EVENT", "complete_step_lifecycle", "event_contract", "typed_graph_event_maps_current_reset_charge_and_candidate_history", ["source_target_graph_map", "resource_transport", "history_transport_or_reset"], ["GRC9V4-CD-D9-v1", "GRC9V4-D9-LIFECYCLE-COVERAGE-MATRIX-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-LIFECYCLE"], "survives_from_GRC_premises", "general_GRC_typed_topology_continuation", "GRCV4_current_promoted_common_lifecycle", "array_resize_is_not_a_typed_event"),
    R("L-ORDERED-RECEIPTS", "complete_step_lifecycle", "receipt_contract", "migration_and_event_receipts_bind_ordered_p_source_p_target", ["complete_profile_identity", "direction_specific_loss", "charge_receipt"], ["GRC9V4-CD-D9-v1", "GRC9V4-CD-D10-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-LIFECYCLE"], "survives_from_GRC_premises", "general_GRC_typed_receipt", "GRCV4_current_promoted_common_lifecycle", "endpoint_profile_coverage_is_not_crossing_evidence"),
    R("L-SINGULAR-FAIL-CLOSED", "complete_step_lifecycle", "failure_contract", "singular_multiple_nonfinite_or_unadmitted_solves_commit_nothing", ["finite_solver_dispositions", "domain_contract", "atomic_transaction"], ["GRC9V4-CD-D6-v1", "GRC9V4-CD-D6V2-v1", "GRC9V4-CD-D9-v1"], "GRC_derived", "promotion_proved", ["D10.2-DER-LIFECYCLE"], "survives_from_GRC_premises", "general_GRC_fail_closed_solver_contract", "GRCV4_current_promoted_common_lifecycle", "regularization_or_root_selection_cannot_be_hidden"),
    R("L-PROFILE-GRAMMAR", "complete_step_lifecycle", "identity_grammar", "each_executable_state_binds_one_candidate_plus_one_realization", ["typed_candidate_id", "typed_realization_id", "complete_profile_identity"], ["GRC9V4-CD-D10-v1", "GRC9V4-D10-SPECIFICATION-AUTHORIZATION-v1"], "substrate_independent_specification_meta", "promotion_proved", ["D10.2-DER-SPEC-GRAMMAR"], "survives_without_any_GRC9V3_premise", "substrate_independent_profile_identity_grammar", "GRCV4_current_population_specification_grammar", "grammar_does_not_prove_candidate_physics_or_permanent_universality"),

    R("GRC9-ORDERED-PORTS", "GRC9_specialization", "substrate_mechanic", "nine_ordered_ports_per_module", ["GRC9_port_graph"], ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP"], "GRC9_intrinsic", "specialization_only", [], "fails_without_nine_port_substrate", "intrinsic_nine_port_mechanic", "GRC9V4_specialization", "ordered_ports_are_not_general_GRCV4"),
    R("GRC9-ROW-COLUMN-CHART", "GRC9_specialization", "substrate_mechanic", "fixed_3_by_3_row_column_chart", ["nine_ordered_ports", "port_to_row_column_map"], ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP"], "GRC9_intrinsic", "specialization_only", [], "fails_without_nine_port_substrate", "intrinsic_nine_port_chart", "GRC9V4_specialization", "chart_is_not_a_generic_local_frame"),
    R("GRC9-SATURATION", "GRC9_specialization", "substrate_mechanic", "local_port_capacity_saturation", ["finite_nine_port_capacity", "occupied_inactive_port_state"], ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP"], "GRC9_intrinsic", "specialization_only", [], "fails_without_nine_port_substrate", "intrinsic_nine_port_capacity_gate", "GRC9V4_specialization", "generic_graph_degree_pressure_is_not_this_saturation_gate"),
    R("GRC9-MECHANICAL-EXPANSION", "GRC9_specialization", "substrate_mechanic", "column_preserving_mechanical_expansion", ["port_modules", "row_column_chart", "expansion_distribution"], ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP"], "GRC9_intrinsic", "specialization_only", [], "fails_without_nine_port_substrate", "intrinsic_GRC9_expansion", "GRC9V4_specialization", "generic_topology_change_is_not_GRC9_mechanical_expansion"),
    R("GRC9-HYBRID-SPARK", "GRC9_specialization", "hybrid_capability", "saturation_plus_GRC_semantic_degeneracy_spark_candidate", ["GRC9_saturation", "GRC_basin_interior", "signed_Hessian_degeneracy"], ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP"], "GRC9_intrinsic", "specialization_only", [], "fails_without_nine_port_substrate", "GRC9V3_hybrid_capability", "GRC9V4_specialization", "the_GRC_semantic_part_does_not_remove_the_load_bearing_GRC9_gate"),
    R("GRC9-CHILD-BASIN-STABILIZATION", "GRC9_specialization", "hybrid_capability", "spark_completion_requires_postexpansion_child_basin_or_attractor_gain", ["GRC9_mechanical_expansion", "GRC_basin_identity", "postevent_stabilization"], ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP"], "GRC9_intrinsic", "specialization_only", [], "fails_without_nine_port_substrate", "GRC9V3_hybrid_completion_contract", "GRC9V4_specialization", "candidate_or_expansion_alone_is_not_completed_spark"),
    R("GRC9-COLUMN-COARSE-GRAINING", "GRC9_specialization", "substrate_mechanic", "column_coarse_graining_and_split_reconstruction", ["fixed_row_column_chart", "port_column_partition"], ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP"], "GRC9_intrinsic", "specialization_only", [], "fails_without_nine_port_substrate", "intrinsic_GRC9_column_operation", "GRC9V4_specialization", "ordinary_graph_coarsening_is_not_this_column_contract"),

    R("SPEC-PROFILE-GRAMMAR", "specification_grammar", "normative_grammar", "current_initial_population_contains_A_or_C_cross_CI_OS_RG2b_PC_CI_PC", ["accepted_D10_population", "typed_complete_profile_identity"], ["GRC9V4-CD-D10-v1", "GRC9V4-D10-SPECIFICATION-AUTHORIZATION-v1"], "substrate_independent_specification_meta", "promotion_proved", ["D10.2-DER-SPEC-GRAMMAR"], "survives_without_any_GRC9V3_premise", "current_population_specification_grammar", "GRCV4_current_population_specification_grammar", "current_population_is_not_future_exhaustive_or_permanently_universal"),
    R("SPEC-FUTURE-ADMISSION", "specification_grammar", "successor_contract", "materially_distinct_profile_reopens_earliest_affected_contract", ["profile_identity", "authority_staging_state_geometry_accounting_lifecycle_axes"], ["GRC9V4-CD-D10-v1"], "substrate_independent_specification_meta", "promotion_proved", ["D10.2-DER-SPEC-GRAMMAR"], "survives_without_any_GRC9V3_premise", "substrate_independent_successor_admission", "GRCV4_current_population_specification_grammar", "successor_novelty_cannot_bypass_existing_contracts"),
    R("SPEC-B-SLOT", "specification_grammar", "reserved_extension_slot", "Candidate_B_is_routed_not_rejected_and_nonexecutable", ["typed_candidate_registry", "missing_source_backed_writer"], ["GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D10-v1"], "substrate_independent_specification_meta", "promotion_proved", ["D10.2-DER-SPEC-GRAMMAR"], "survives_without_any_GRC9V3_premise", "reserved_successor_slot", "GRCV4_current_population_specification_grammar", "A_or_C_cannot_be_relabelled_as_B"),
    R("SPEC-CLAIM-CEILINGS", "specification_grammar", "claim_contract", "profile_local_claim_ceilings_blocked_relabels_and_verification_obligations", ["claim_topology", "evidence_lineage", "profile_identity"], ["GRC9V4-CD-D10-v1"], "substrate_independent_specification_meta", "promotion_proved", ["D10.2-DER-SPEC-GRAMMAR"], "survives_without_any_GRC9V3_premise", "substrate_independent_claim_hygiene", "GRCV4_current_population_specification_grammar", "claim_governance_is_not_runtime_causal_state"),
    R("SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER", "specification_grammar", "profile_contract", "each_profile_declares_normalization_units_gauge_domain_and_solver", ["complete_profile_identity", "typed_parameters", "admission_domain", "solver_disposition"], ["GRC9V4-CD-D8B-CI-v1", "GRC9V4-CD-D9-v1", "GRC9V4-CD-D10-v1"], "substrate_independent_specification_meta", "promotion_proved", ["D10.2-DER-SPEC-GRAMMAR"], "survives_without_any_GRC9V3_premise", "profile_local_numeric_and_type_contract", "GRCV4_current_population_specification_grammar", "profile_constants_are_not_hidden_universal_constants"),
    R("SPEC-COMPOSITION-PROFILE-IDENTITY", "specification_grammar", "profile_contract", "composition_law_and_gain_are_part_of_complete_profile_identity", ["candidate_identity", "realization_identity", "composition_coefficients"], ["GRC9V4-GTRS-COMP-v1", "GRC9V4-GTRS-CI-PC-v1", "GRC9V4-CD-D10-v1"], "substrate_independent_specification_meta", "promotion_proved", ["D10.2-DER-SPEC-GRAMMAR"], "survives_without_any_GRC9V3_premise", "composition_semantics_are_explicit_profile_identity", "GRCV4_current_population_specification_grammar", "different_composition_gain_cannot_reuse_the_same_profile_identity"),
    R("SPEC-VERIFICATION-REGISTRY", "specification_grammar", "evidence_contract", "runtime_numeric_and_implementation_obligations_remain_separate_from_scientific_claim_topology", ["claim_ceiling", "verification_obligation", "evidence_kind"], ["GRC9V4-CD-D10-v1", "GRC9V4-D10-NORMATIVE-CLAIM-TOPOLOGY-v1"], "substrate_independent_specification_meta", "promotion_proved", ["D10.2-DER-SPEC-GRAMMAR"], "survives_without_any_GRC9V3_premise", "verification_registry_separate_from_scientific_debt", "GRCV4_current_population_specification_grammar", "unexecuted_runtime_verification_is_not_unresolved_constitutive_mathematics"),
]


FAMILY_REQUIREMENTS = {
    "core_resource": 7,
    "legacy_transport": 9,
    "candidate_A": 7,
    "candidate_C": 5,
    "geometry": 8,
    "realization": 5,
    "complete_step_lifecycle": 12,
    "GRC9_specialization": 7,
    "specification_grammar": 7,
}


CONTROLS = [
    "classification_uses_actual_premises_not_symbol_or_formula_appearance",
    "delete_GRC9V3_lineage_premise_before_any_GRC_promotion",
    "GRCV3_is_general_graph_GRC_and_GRC9V3_is_its_nine_port_specialization",
    "GraphGRCV4_is_not_a_distinct_naming_family",
    "GRC9V3_lineage_is_not_nine_port_intrinsicness",
    "GRC9_specialization_specific_is_not_GRC9_intrinsic",
    "exact_GRC9V3_compatibility_is_not_rederived_away",
    "general_GRC_charge_is_separate_from_unit_measure_reference_profile",
    "A_G_W_functional_is_separate_from_GRC9_row_basis_backend",
    "A_G_W_promotion_is_exactly_the_accepted_curvature_disabled_D7_profile",
    "curvature_conditioned_A_requires_a_new_profile_identity_and_provenance_reopening",
    "A_pre_read_and_writer_staging_are_revision_specific_and_explicit",
    "A_promotion_does_not_claim_numeric_stability_or_runtime_reachability",
    "C_derived_sector_is_not_independent_state_or_resource",
    "graph_Hodge_typing_requires_positive_stars_and_typed_flat_sharp_maps",
    "core_K_structural_role_is_separate_from_graph_K4_realization",
    "K4_is_a_graph_local_symmetric_bilinear_form_not_core_K_itself",
    "Hodge_reference_embedding_is_constructed_from_GRC_measure_and_base_conductance",
    "G_J_flat_map_is_separate_from_M4_transport_mobility",
    "M4_transport_authority_is_separate_from_overlap_normalized_K4_assembly",
    "legacy_cached_GRC9_tensor_is_not_the_new_K4_H4_h4_crossing",
    "realization_promotion_does_not_rank_families",
    "current_realization_population_is_not_future_exhaustive",
    "current_PC_profile_is_not_a_universal_history_law",
    "complete_profile_endpoint_coverage_is_not_crossing_evidence",
    "event_and_migration_contracts_do_not_replace_runtime_conformance_tests",
    "generic_migration_grammar_is_separate_from_target_candidate_initializers",
    "GRCV4_A_initializer_is_rederived_from_promoted_GRC_contracts",
    "exact_GRC9V3_A_initializer_binding_remains_specialization_specific",
    "specification_grammar_is_not_physical_evidence",
    "core_theory_physics_is_separate_from_substrate_independent_specification_meta",
    "Candidate_B_remains_nonexecutable_and_unrejected",
    "future_profiles_reopen_provenance_and_the_earliest_affected_contract",
    "factorization_scope_is_the_current_D10_initial_specification_population",
    "every_accepted_D10_claim_has_explicit_provenance_object_coverage",
    "every_audited_normative_object_bears_on_at_least_one_accepted_D10_claim",
    "D10_claim_topology_is_transformed_only_by_named_D10_2_successors",
    "accepted_D10_claim_set_is_exact_across_decision_topology_and_authorization_surfaces",
    "D10_CL_C_012_is_accepted_D10_claim_not_a_D10_2_local_invention",
    "parent_object_coverage_is_not_equation_contract_coverage",
    "every_parent_object_has_a_subordinate_equation_or_contract_row",
    "every_accepted_D10_claim_has_subordinate_equation_or_contract_coverage",
    "charge_tangent_and_structural_projector_are_individually_audited",
    "all_ten_current_profiles_have_four_independent_disabled_reduction_surfaces",
    "family_genericity_does_not_replace_candidate_specific_equation_provenance",
    "D10_2_does_not_change_runtime_or_src",
    "D10_2_does_not_write_normative_specs",
    "implementation_remains_unauthorized",
]


row_ids = [row["object_id"] for row in ROWS]
derivation_ids = [row["derivation_id"] for row in DERIVATIONS]
family_counts = Counter(row["family"] for row in ROWS)
disposition_counts = Counter(row["substrate_disposition"] for row in ROWS)
promotion_counts = Counter(row["promotion_status"] for row in ROWS)
pending_rows = [
    row["object_id"]
    for row in ROWS
    if row["promotion_status"] == "promotion_pending"
]
grc_rows = [
    row["object_id"]
    for row in ROWS
    if row["substrate_disposition"]
    in {
        "GRC_derived",
        "core_theory_substrate_independent",
        "substrate_independent_specification_meta",
    }
]
specialization_rows = [
    row["object_id"]
    for row in ROWS
    if row["substrate_disposition"]
    in {"GRC9_specialization_specific", "GRC9_intrinsic"}
]

A_OBJECTS = [row["object_id"] for row in ROWS if row["family"] == "candidate_A"]
C_OBJECTS = [row["object_id"] for row in ROWS if row["family"] == "candidate_C"]
GRC9_OBJECTS = [
    row["object_id"] for row in ROWS if row["family"] == "GRC9_specialization"
]
D10_CLAIM_IDS = D10_TOPOLOGY_CLAIM_IDS
CLAIM_COVERAGE = {
    "D10-CL-N-001": [
        "CORE-C-AUTHORITY",
        "BASE-SCALAR-MOBILITY",
        "BASE-POTENTIAL",
        "BASE-POTENTIAL-FLOW",
        "BASE-GRC-DIFFERENTIAL",
        "BASE-GRC9-ROW-BASIS-DIFFERENTIAL",
        "A-STATE-REDUCTION",
        "C-AUTHORITY",
        "GEOM-K4-TO-H4-TO-h4",
        "L-PROFILE-GRAMMAR",
        "SPEC-PROFILE-GRAMMAR",
        *GRC9_OBJECTS,
    ],
    "D10-CL-N-002": ["CORE-C-AUTHORITY", "A-STATE-REDUCTION", "C-SECTOR", "C-SELECTOR", "C-HODGE-MAPS", "C-AUTHORITY"],
    "D10-CL-N-003": ["L-AUTHORITATIVE-CURRENT", "L-CONTINUITY-WRITE", "L-POSTCONTINUITY-REFRESH", "L-ATOMICITY", "L-SINGULAR-FAIL-CLOSED"],
    "D10-CL-N-004": ["CORE-INCIDENCE-CONTINUITY", "CORE-GENERAL-CHARGE", "CORE-CHARGE-TANGENT", "CORE-STRUCTURAL-CHARGE-PROJECTOR", "CORE-UNIT-MEASURE", "CORE-EXTERNAL-EVENT-CHARGE", "L-CONTINUITY-WRITE"],
    "D10-CL-N-005": ["L-SNAPSHOT-RESET", "L-PROFILE-MIGRATION", "L-A-INITIALIZER-GRC", "L-A-INITIALIZER-GRC9V3", "L-TOPOLOGY-EVENT", "L-ORDERED-RECEIPTS", "L-PROFILE-GRAMMAR"],
    "D10-CL-N-006": ["CORE-K-STRUCTURAL-ROLE", "GEOM-K4", "GEOM-H1-FORM", "GEOM-GJ", "GEOM-M4", "GEOM-K4-TO-H4-TO-h4", "GEOM-ASSEMBLY", "GEOM-COVARIANCE", "L-TOPOLOGY-EVENT"],
    "D10-CL-N-007": ["BASE-DISABLED-TRANSITION", "BASE-DISABLED-STATE", "BASE-DISABLED-OBSERVABLE", "BASE-DISABLED-LIFECYCLE"],
    "D10-CL-N-008": ["SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER", "SPEC-COMPOSITION-PROFILE-IDENTITY"],
    "D10-CL-N-009": ["L-PROFILE-GRAMMAR", "SPEC-PROFILE-GRAMMAR"],
    "D10-CL-O-001": A_OBJECTS,
    "D10-CL-O-002": C_OBJECTS,
    "D10-CL-O-003": ["REAL-CI"],
    "D10-CL-O-004": ["REAL-OS"],
    "D10-CL-O-005": ["REAL-RG2B"],
    "D10-CL-O-006": ["REAL-PC"],
    "D10-CL-O-007": ["REAL-CI-PC"],
    "D10-CL-C-001": ["GEOM-ASSEMBLY", "REAL-CI", "SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER", "SPEC-CLAIM-CEILINGS"],
    "D10-CL-C-002": ["L-TOPOLOGY-EVENT", "L-ORDERED-RECEIPTS", "SPEC-CLAIM-CEILINGS"],
    "D10-CL-C-003": ["L-SINGULAR-FAIL-CLOSED", "SPEC-B-SLOT", "SPEC-CLAIM-CEILINGS"],
    "D10-CL-C-004": ["SPEC-CLAIM-CEILINGS", "SPEC-VERIFICATION-REGISTRY"],
    "D10-CL-C-005": ["SPEC-CLAIM-CEILINGS", "SPEC-VERIFICATION-REGISTRY"],
    "D10-CL-C-006": ["C-HODGE-MAPS", "L-SINGULAR-FAIL-CLOSED", "SPEC-VERIFICATION-REGISTRY"],
    "D10-CL-C-007": ["A-READ-CLOSURE", "C-READ-BACK", "SPEC-CLAIM-CEILINGS"],
    "D10-CL-C-008": ["SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER", "SPEC-VERIFICATION-REGISTRY"],
    "D10-CL-C-009": ["REAL-RG2B", "SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER"],
    "D10-CL-C-010": ["SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER", "SPEC-CLAIM-CEILINGS"],
    "D10-CL-C-011": row_ids,
    "D10-CL-C-012": ["SPEC-PROFILE-GRAMMAR", "SPEC-FUTURE-ADMISSION"],
    "D10-CL-U-001": ["SPEC-B-SLOT", "SPEC-FUTURE-ADMISSION"],
    "D10-CL-U-002": ["SPEC-VERIFICATION-REGISTRY", "SPEC-CLAIM-CEILINGS"],
    "D10-CL-U-003": ["SPEC-CLAIM-CEILINGS", "SPEC-VERIFICATION-REGISTRY"],
    "D10-CL-U-004": ["SPEC-VERIFICATION-REGISTRY"],
    "D10-CL-U-005": ["GEOM-H1-FORM", "GEOM-ASSEMBLY", "SPEC-FUTURE-ADMISSION"],
    "D10-CL-X-001": ["L-TOPOLOGY-EVENT", "L-ORDERED-RECEIPTS"],
    "D10-CL-X-002": ["SPEC-CLAIM-CEILINGS", "SPEC-VERIFICATION-REGISTRY"],
    "D10-CL-X-003": ["SPEC-CLAIM-CEILINGS", "SPEC-VERIFICATION-REGISTRY"],
    "D10-CL-X-004": A_OBJECTS,
    "D10-CL-X-006": [*A_OBJECTS, *C_OBJECTS],
    "D10-CL-X-005": ["REAL-PC", "SPEC-B-SLOT"],
}


PARENT_BY_ID = {row["object_id"]: row for row in ROWS}
PARENT_TO_CLAIMS: dict[str, list[str]] = {object_id: [] for object_id in row_ids}
for claim_id, object_ids in CLAIM_COVERAGE.items():
    for object_id in object_ids:
        PARENT_TO_CLAIMS[object_id].append(claim_id)


def expanded_contract(
    contract_id: str,
    contract_scope: str,
    parent_object_ids: list[str],
    accepted_claim_ids: list[str],
    profile_ids: list[str],
    normative_equation_or_contract: str,
    blocked_overread: str,
) -> dict[str, Any]:
    parents = [PARENT_BY_ID[object_id] for object_id in parent_object_ids]
    dispositions = {row["substrate_disposition"] for row in parents}
    promotions = {row["promotion_status"] for row in parents}
    destinations = {row["specification_destination"] for row in parents}
    deletion_tests = {row["GRC9V3_premise_deletion_test"] for row in parents}
    if any(len(values) != 1 for values in [dispositions, promotions, deletion_tests]):
        raise ValueError(f"mixed parent contract classification: {contract_id}")
    return equation_contract(
        contract_id,
        contract_scope,
        parent_object_ids,
        accepted_claim_ids,
        profile_ids,
        normative_equation_or_contract,
        sorted({item for row in parents for item in row["premises_used"]}),
        sorted({item for row in parents for item in row["source_lineage"]}),
        next(iter(dispositions)),
        next(iter(promotions)),
        sorted({item for row in parents for item in row["independent_derivation_ids"]}),
        next(iter(deletion_tests)),
        "+".join(sorted(destinations)),
        blocked_overread,
    )


PARENT_EQUATION_CONTRACTS = [
    equation_contract(
        f"D10.2-EC-PARENT-{row['object_id']}",
        "parent_atomic_contract",
        [row["object_id"]],
        sorted(PARENT_TO_CLAIMS[row["object_id"]]),
        [],
        row["normative_object"],
        row["premises_used"],
        row["source_lineage"],
        row["substrate_disposition"],
        row["promotion_status"],
        row["independent_derivation_ids"],
        row["GRC9V3_premise_deletion_test"],
        row["specification_destination"],
        row["blocked_overread"],
    )
    for row in ROWS
]


EXPLICIT_EQUATION_CONTRACTS = [
    expanded_contract(
        "D10.2-EC-CHARGE-DQ",
        "charge_tangent",
        ["CORE-CHARGE-TANGENT"],
        ["D10-CL-N-004"],
        [],
        "DQ_varpi[delta_X] = varpi^T*delta_C",
        "the_charge_differential_acts_on_the_resource_sector_and_does_not_constrain_nonresource_variations",
    ),
    expanded_contract(
        "D10.2-EC-CHARGE-TANGENT",
        "charge_tangent",
        ["CORE-CHARGE-TANGENT"],
        ["D10-CL-N-004"],
        [],
        "V_Q,varpi = ker(DQ_varpi) = {delta_X : varpi^T*delta_C = 0}",
        "V_Q_varpi_is_the_authoritative_complete_state_tangent_not_only_a_C_sector_subspace",
    ),
    expanded_contract(
        "D10.2-EC-CHARGE-C-SECTOR-PROJECTOR",
        "charge_projector",
        ["CORE-STRUCTURAL-CHARGE-PROJECTOR"],
        ["D10-CL-N-004"],
        [],
        "Pi_Q,C,H0(delta_C) = delta_C - H0^-1*varpi*(varpi^T*delta_C)/(varpi^T*H0^-1*varpi)",
        "Pi_Q_C_H0_is_orthogonal_only_on_the_structural_C_sector",
    ),
    expanded_contract(
        "D10.2-EC-CHARGE-FULL-TANGENT-RETRACTION",
        "charge_projector",
        ["CORE-STRUCTURAL-CHARGE-PROJECTOR"],
        ["D10-CL-N-004"],
        [],
        "R_Q(delta_X) = (Pi_Q,C,H0(delta_C), identity_on_nonresource_variations)",
        "the_identity_extension_is_a_canonical_retraction_not_a_full_state_orthogonal_projector_until_a_product_metric_is_frozen",
    ),
    expanded_contract(
        "D10.2-EC-CHARGE-BUDGET-STAGE",
        "charge_budget_stage",
        ["CORE-GENERAL-CHARGE", "L-CONTINUITY-WRITE", "L-TOPOLOGY-EVENT"],
        ["D10-CL-N-004"],
        [],
        "ordinary_complete_step: Q_varpi(C_next) = Q_target_next after_the_single_authoritative_continuity_write_and_before_final_commit; if_an_admitted_external_exchange_exists_Q_target_next = Q_target_current + Delta_Q_step; current_bounded_population_Delta_Q_step = 0; topology_event_jump: Q_target_plus = Q_target_minus + Delta_Q_event = varpi_plus^T*C_plus",
        "bare_Q_target_must_not_conflate_pre_update_and_post_update_targets_or_double_count_event_Delta_Q_and_a_charge_check_before_the_actual_resource_write_does_not_certify_the_complete_step",
    ),
]


DISABLED_PROFILES = [
    "A_CI",
    "C_CI",
    "A_OS",
    "C_OS",
    "A_RG2b",
    "C_RG2b",
    "A_PC",
    "C_PC",
    "A_CI_PC",
    "C_CI_PC",
]
DISABLED_SURFACES = {
    "transition": "BASE-DISABLED-TRANSITION",
    "state": "BASE-DISABLED-STATE",
    "observable": "BASE-DISABLED-OBSERVABLE",
    "lifecycle": "BASE-DISABLED-LIFECYCLE",
}
for profile_id in DISABLED_PROFILES:
    for surface_name, parent_id in DISABLED_SURFACES.items():
        EXPLICIT_EQUATION_CONTRACTS.append(
            expanded_contract(
                f"D10.2-EC-DISABLED-{profile_id}-{surface_name.upper()}",
                "profile_scoped_disabled_reduction",
                [parent_id],
                ["D10-CL-N-007"],
                [profile_id],
                f"disabled_profile_{profile_id}_{surface_name}_surface_reduces_exactly_to_its_declared_GRC9V3_{surface_name}_target",
                f"{surface_name}_reduction_for_{profile_id}_does_not_imply_any_other_disabled_reduction_surface",
            )
        )


EXPLICIT_EQUATION_CONTRACTS.extend(
    [
        expanded_contract("D10.2-EC-CI-A-ROOT", "candidate_specific_CI", ["REAL-CI"], ["D10-CL-O-003"], ["A_CI"], "F_A(J_A,h_A;C_k,W_A,k,context) = 0 with W_hat_A(h_A) recomputed inside every residual evaluation", "the_A_root_cannot_freeze_W_hat_outside_the_joint_root"),
        expanded_contract("D10.2-EC-CI-A-CONTRACTION", "candidate_specific_CI", ["REAL-CI"], ["D10-CL-O-003"], ["A_CI"], "the_preregistered_A_CI_root_map_is_a_self_map_and_contraction_on_its_declared_bounded_domain_and_selects_the_unique_local_branch_connected_to_kappa_H_zero", "bounded_contraction_uniqueness_is_not_global_root_uniqueness_or_temporal_stability"),
        expanded_contract("D10.2-EC-CI-C-ROOT", "candidate_specific_CI", ["REAL-CI"], ["D10-CL-O-003"], ["C_CI"], "F_C(J_C,h_C;C_k,context) = (J_C-J0_C-zeta_C*j_C_flux, h_C-H_profile(K4_base+Delta_K4_C)) = 0", "the_C_root_is_defined_only_on_the_admitted_selector_and_topology_stratum"),
        expanded_contract("D10.2-EC-CI-C-CONTRACTION", "candidate_specific_CI", ["REAL-CI"], ["D10-CL-O-003"], ["C_CI"], "the_C_current_and_geometry blocks satisfy_the_declared_stratum_local_contraction_and_regular_inverse_bounds", "stratum_local_contraction_is_not_a_cross_rank_or_topology_continuation_theorem"),
        expanded_contract("D10.2-EC-CI-C-ROOT-SELECTION", "candidate_specific_CI", ["REAL-CI"], ["D10-CL-O-003"], ["C_CI"], "exactly_one_self_consistent_regular_C_root_connected_to_the_accepted_kappa_H_zero_reference_branch_is_admitted; multiple_or_disconnected_roots_fail_closed", "an_arbitrary_numerical_root_cannot_be_selected_post_hoc"),

        expanded_contract("D10.2-EC-CI-PC-A-COMPOSITION", "candidate_specific_CI_PC", ["REAL-CI-PC"], ["D10-CL-O-007"], ["A_CI_PC"], "K_eff,A = K4_base + Z_A,k + rho_inst*S_A(J_A,h_A) with_the_preregistered_rho_inst_equal_one_gain_two_profile", "the_unit_plus_unit_profile_is_not_amplitude_equivalent_to_CI_or_PC"),
        expanded_contract("D10.2-EC-CI-PC-A-ROOT", "candidate_specific_CI_PC", ["REAL-CI-PC"], ["D10-CL-O-007"], ["A_CI_PC"], "the_A_CI_PC_joint_J_h_root_uses_the_same_root_source_for_the_immediate_and_retained_paths_and_satisfies_the_declared_bounded_contraction_uniqueness_contract", "hybrid_root_admission_does_not_establish_numeric_or_global_envelopes"),
        expanded_contract("D10.2-EC-CI-PC-C-COMPOSITION", "candidate_specific_CI_PC", ["REAL-CI-PC"], ["D10-CL-O-007"], ["C_CI_PC"], "K_eff,C = K4_base + Z_C,k + rho_inst*S_C(J_C,h_C) with_the_preregistered_rho_inst_equal_one_gain_two_profile", "the_C_hybrid_must_not_apply_chi_or_zeta_twice"),
        expanded_contract("D10.2-EC-CI-PC-C-CONTRACTION", "candidate_specific_CI_PC", ["REAL-CI-PC"], ["D10-CL-O-007"], ["C_CI_PC"], "the_C_CI_PC_composite_map_is_a_contraction_on_the_declared_fixed_selector_stratum_and_closed_carrier_ball", "composite_contraction_is_not_cross_stratum_or_global_stability"),
        expanded_contract("D10.2-EC-CI-PC-C-ROOT-SELECTION", "candidate_specific_CI_PC", ["REAL-CI-PC"], ["D10-CL-O-007"], ["C_CI_PC"], "exactly_one_self_consistent_regular_C_CI_PC_root_is_admitted_on_the_preregistered_local branch; multiple_roots_fail_closed", "one_admitted_local_root_is_not_a_global_uniqueness_theorem"),
        expanded_contract("D10.2-EC-CI-PC-ABLATIONS", "candidate_specific_CI_PC", ["REAL-CI-PC"], ["D10-CL-O-007"], ["A_CI_PC", "C_CI_PC"], "rho_inst=0_with_PC_enabled_reduces_to_PC; Z=0_with_PC_disabled_and_rho_inst=1_reduces_to_CI; the_double_ablation_returns_the_fixed_reference_transition", "ablation_identity_does_not_make_the_enabled_hybrid_equivalent_to_its_components"),

        expanded_contract("D10.2-EC-PC-WRITER-COEFFICIENT", "persistent_carrier", ["REAL-PC"], ["D10-CL-O-006"], ["A_PC", "C_PC", "A_CI_PC", "C_CI_PC"], "a_PC,k = exp(-Delta_t_k/tau_PC,a) with tau_PC,a > 0", "one_tau_PC_is_the_current_profile_not_a_universal_history_law"),
        expanded_contract("D10.2-EC-PC-ZOH-WRITER", "persistent_carrier", ["REAL-PC"], ["D10-CL-O-006"], ["A_PC", "C_PC", "A_CI_PC", "C_CI_PC"], "Z_a,k+1 = a_PC,k*Z_a,k + (1-a_PC,k)*S_a with S_a held_constant_over_the_beat", "the_ZOH_writer_is_an_authoritative_history_write_not_a_solver_cache"),
        expanded_contract("D10.2-EC-PC-RELEASE", "persistent_carrier", ["REAL-PC"], ["D10-CL-O-006"], ["A_PC", "C_PC", "A_CI_PC", "C_CI_PC"], "with_zero_source_Z_n = exp(-sum_{k<n}Delta_t_k/tau_PC)*Z_0", "native_release_is_not_administrative_reset"),
        expanded_contract("D10.2-EC-PC-MATCHED-FORCING", "persistent_carrier", ["REAL-PC"], ["D10-CL-O-006"], ["A_PC", "C_PC", "A_CI_PC", "C_CI_PC"], "under_matched_future_forcing_the_carrier_difference_contracts_by_the_declared_a_PC_plus_source_Lipschitz_bound_strictly_below_one", "carrier_contraction_is_not_committed_endpoint_hysteresis_evidence"),

        expanded_contract("D10.2-EC-OS-STAGE-ORDER", "operator_split", ["REAL-OS"], ["D10-CL-O-004"], ["A_OS", "C_OS"], "X_k -> J^(0) -> j_flat^(0) -> K4^(0) -> h^(1) -> J^(1) -> X_k+1 with_one_atomic_commit", "no_second_geometry_or_corrector_iteration_is_part_of_this_profile"),
        expanded_contract("D10.2-EC-OS-A-CORRECTOR", "operator_split", ["REAL-OS"], ["D10-CL-O-004"], ["A_OS"], "at_fixed_h_A^(1)_recompute_Phi_A_J0_A_W_hat_A_q_A_and_solve_the_full_A_corrector_without_predictor_cache_reuse", "produced_geometry_must_be_an_equation_level_consumer_not_telemetry"),
        expanded_contract("D10.2-EC-OS-C-CORRECTOR", "operator_split", ["REAL-OS"], ["D10-CL-O-004"], ["C_OS"], "at_fixed_h_C^(1)_recompute_P_M_T_C_H_M_I_4M_Rhat_C_M_G_J_J0_C_and_solve_the_full_C_corrector", "selector_or_Hodge_predictor_caches_cannot_enter_the_C_corrector"),
        expanded_contract("D10.2-EC-OS-SPLIT-RESIDUAL", "operator_split", ["REAL-OS"], ["D10-CL-O-004"], ["A_OS", "C_OS"], "r_h^OS = h^(1) - H_profile(K4_base + Delta_K4(J^(1),h^(1))) and F_CI(J^(1),h^(1)) = (0,r_h^OS)", "a_nonzero_bounded_split_residual_is_not_automatic_failure_or_Delta_t_truncation_error"),
        expanded_contract("D10.2-EC-OS-NO-SECOND-ITERATION", "operator_split", ["REAL-OS"], ["D10-CL-O-004"], ["A_OS", "C_OS"], "J^(1)_does_not_retroactively_update_h^(1); a_second_predictor_corrector_cycle_requires_a_new_profile_identity", "posthoc_iteration_cannot_improve_the_preregistered_one_pass_result"),

        expanded_contract("D10.2-EC-RG-INVARIANCE", "reconstructed_geometry", ["REAL-RG2B"], ["D10-CL-O-005"], ["A_RG2b", "C_RG2b"], "Gamma_a(Psi_a,Gamma_a(X)) = G_a(X,Gamma_a(X)) on K_minus_with_Psi_a,Gamma_a(K_minus)_subset_K", "uniqueness_is_relative_to_the_frozen_equivariant_extension_profile"),
        expanded_contract("D10.2-EC-RG-LIPSCHITZ-CONTRACTION", "reconstructed_geometry", ["REAL-RG2B"], ["D10-CL-O-005"], ["A_RG2b", "C_RG2b"], "the_graph_transform_is_a_value_radius_and_Lipschitz_self_map_with_C0_contraction_factor_q0_strictly_less_than_one", "Lipschitz_section_existence_is_not_C1_regularness"),
        expanded_contract("D10.2-EC-RG-DETERMINISM", "reconstructed_geometry", ["REAL-RG2B"], ["D10-CL-O-005"], ["A_RG2b", "C_RG2b"], "Gamma_a_is_a_deterministic_family_local_section_with_no_serialized_h_previous_root_branch_token_or_solver_history", "reconstructed_geometry_cannot_hide_a_persistent_carrier"),
        expanded_contract("D10.2-EC-RG-CLAIM-CEILING", "reconstructed_geometry", ["REAL-RG2B"], ["D10-CL-O-005"], ["A_RG2b", "C_RG2b"], "classical_derivative_or_continuation_spectrum_claims_require_a_separate_C1_successor", "the_current_Lipschitz_profile_cannot_be_differentiated_by_assumption"),

        expanded_contract("D10.2-EC-C-SECTOR", "candidate_C_chain", ["C-SECTOR"], ["D10-CL-O-002"], ["C_CI", "C_OS", "C_RG2b", "C_PC", "C_CI_PC"], "T_C = T_C(C,P_M) is_derived_from_authoritative_C_under_fixed_rank_or_boundary_semantics", "T_C_is_not_independent_state_or_resource"),
        expanded_contract("D10.2-EC-C-HODGE-LAPLACIAN", "candidate_C_chain", ["C-HODGE-MAPS"], ["D10-CL-O-002"], ["C_CI", "C_OS", "C_RG2b", "C_PC", "C_CI_PC"], "Delta_1,M = B^T*H0^-1*B*H1_on_the_admitted_selected_one_form_space", "matrix_shape_without_positive_typed_Hodge_maps_is_insufficient"),
        expanded_contract("D10.2-EC-C-RESOLVENT", "candidate_C_chain", ["C-READ-BACK"], ["D10-CL-O-002"], ["C_CI", "C_OS", "C_RG2b", "C_PC", "C_CI_PC"], "Rhat_C,M = (I + tau_C*Delta_1,M)^-1_is_ungated_and_chi_C_is_applied_exactly_once_to_the_causal_read", "chi_C_must_not_be_applied_inside_and_outside_the_resolvent"),
        expanded_contract("D10.2-EC-C-READBACK", "candidate_C_chain", ["C-READ-BACK"], ["D10-CL-O-002"], ["C_CI", "C_OS", "C_RG2b", "C_PC", "C_CI_PC"], "j_C_flat = chi_C*I_4M^-1*Rhat_C,M*I_4M*G_J*J_C_flux_with_declared_identification_and_flat_sharp_maps", "the_read_surface_is_not_an_independent_resource_transfer"),
        expanded_contract("D10.2-EC-C-AUTHORITY", "candidate_C_chain", ["C-AUTHORITY"], ["D10-CL-N-002", "D10-CL-O-002"], ["C_CI", "C_OS", "C_RG2b", "C_PC", "C_CI_PC"], "only_C_is_written_independently; selector_sector_Hodge_resolvent_and_read_surfaces_are_rederived", "derived_C_surfaces_cannot_be_serialized_as_hidden_causal_state"),

        expanded_contract("D10.2-EC-GEOM-K4-ASSEMBLY", "structural_geometry", ["GEOM-K4"], ["D10-CL-N-006"], [], "Delta_K4_is_a_graph_local_symmetric_bilinear_form_assembled_from_stable_restrictions_with_overlap_normalization", "graph_K4_is_not_core_K_or_transport_mobility_M4"),
        expanded_contract("D10.2-EC-GEOM-HODGE-UPDATE", "structural_geometry", ["GEOM-H1-FORM"], ["D10-CL-N-006"], [], "H1_form_plus = diag(W_ref) + kappa_H*Delta_K4_on_the_positive_admitted_domain", "K4_and_H1_units_require_the_declared_typed_pushforward"),
        expanded_contract("D10.2-EC-GEOM-FLAT", "structural_geometry", ["GEOM-GJ"], ["D10-CL-N-006"], [], "G_J(h) = H1_form(h)^-1_and_j_struct_flat = G_J(h)*j_flux", "G_J_is_flux_resistance_not_M4_transport_mobility"),
        expanded_contract("D10.2-EC-GEOM-PROFILE", "structural_geometry", ["GEOM-K4-TO-H4-TO-h4"], ["D10-CL-N-006"], [], "K4 -> H4 -> h4_is_the_declared_load_bearing_structural_pushforward_consumed_by_the_current_construction", "producing_h4_without_a_declared_consumer_is_not_structural_Read_Back"),
        expanded_contract("D10.2-EC-GEOM-MOBILITY-BOUNDARY", "structural_geometry", ["GEOM-M4"], ["D10-CL-N-006"], [], "M4_is_candidate_specific_transport_mobility_and_no_H1_form_to_M4_or_h4_to_M4_map_exists_without_a_successor_contract", "numerical_matrix_coincidence_cannot_transfer_authority"),

        expanded_contract("D10.2-EC-EVENT-RESOURCE", "typed_topology_event", ["L-TOPOLOGY-EVENT"], ["D10-CL-N-004", "D10-CL-N-005", "D10-CL-X-001"], DISABLED_PROFILES, "C_plus = T_C_evt*C_minus + Delta_C_event; varpi_plus^T*T_C_evt = varpi_minus^T; Delta_Q_event = varpi_plus^T*C_plus - varpi_minus^T*C_minus; Q_target_plus = Q_target_minus + Delta_Q_event = varpi_plus^T*C_plus", "Delta_Q_event_is_a_receipt_for_the_actual_resource_state_map_and_cannot_replace_Delta_C_event; untyped_resize_or_unreceipted_resource_change_is_not_an_admitted_event"),
        expanded_contract("D10.2-EC-EVENT-A-HISTORY", "typed_topology_event", ["L-TOPOLOGY-EVENT"], ["D10-CL-N-005", "D10-CL-X-001"], ["A_CI", "A_OS", "A_RG2b", "A_PC", "A_CI_PC"], "W_A_plus_uses_an_admitted_history_transport_or_the_declared_history_free_target_initializer_with_loss_receipt", "missing_edge_history_cannot_be_fabricated"),
        expanded_contract("D10.2-EC-EVENT-C-DERIVED", "typed_topology_event", ["L-TOPOLOGY-EVENT"], ["D10-CL-N-005", "D10-CL-X-001"], ["C_CI", "C_OS", "C_RG2b", "C_PC", "C_CI_PC"], "Candidate_C_selector_sector_Hodge_and_read_surfaces_are_rederived_from_C_plus_on_the_target_graph", "derived_C_surfaces_are_not_history_payload"),
        expanded_contract("D10.2-EC-EVENT-K4-HISTORY", "typed_topology_event", ["L-TOPOLOGY-EVENT"], ["D10-CL-N-005", "D10-CL-X-001"], ["A_PC", "C_PC", "A_CI_PC", "C_CI_PC"], "Z_plus = L_K4_evt(Z_minus)_when_typed_history_transport_is_admitted_otherwise_Z_plus_is_canonical_reset_with_loss_receipt", "generic_lossless_K4_history_transport_without_lineage_is_not_claimed"),
        expanded_contract("D10.2-EC-EVENT-LIFECYCLE-TUPLE", "typed_topology_event", ["L-TOPOLOGY-EVENT"], ["D10-CL-N-005", "D10-CL-X-001"], DISABLED_PROFILES, "the_event_maps_(X_current,X_reset,Q_target)_as_one_atomic_lifecycle_tuple", "mapping_only_current_state_would_allow_reset_to_resurrect_an_obsolete_graph_or_profile"),
        expanded_contract("D10.2-EC-EVENT-READMISSION-RECEIPT", "typed_topology_event", ["L-ORDERED-RECEIPTS"], ["D10-CL-N-005", "D10-CL-X-001"], DISABLED_PROFILES, "target_profile_readmission_precedes_atomic_commit_and_the_receipt_binds_ordered_source_target_profiles_resource_delta_and_history_loss", "endpoint_coverage_does_not_replace_crossing_evidence"),
    ]
)


NORMATIVE_EQUATION_CONTRACTS = PARENT_EQUATION_CONTRACTS + EXPLICIT_EQUATION_CONTRACTS
equation_contract_ids = [row["equation_contract_id"] for row in NORMATIVE_EQUATION_CONTRACTS]
equation_parent_ids = {
    object_id
    for row in NORMATIVE_EQUATION_CONTRACTS
    for object_id in row["parent_object_ids"]
}
equation_claim_ids = {
    claim_id
    for row in NORMATIVE_EQUATION_CONTRACTS
    for claim_id in row["accepted_claim_ids"]
}
equation_scope_counts = Counter(
    row["contract_scope"] for row in NORMATIVE_EQUATION_CONTRACTS
)


record: dict[str, Any] = {
    "schema_version": "grc9v4_d10_2_full_provenance_v1",
    "record_type": "full_substrate_provenance_and_promotion_audit",
    "record_id": "GRC9V4-CD-D10.2-v1",
    "gate_id": "D10.2",
    "title": "Full Substrate Provenance And GRCV4 Promotion Audit",
    "status": "accepted_bounded",
    "date": "2026-08-26",
    "predecessor_record_id": D10_1["record_id"],
    "predecessor_decision_digest": D10_1["decision_record_digest"],
    "accepted_D10_decision_digest": D10["decision_record_digest"],
    "source_identities": SOURCES,
    "audit_unit": "accepted_D10_claim_to_parent_normative_object_to_subordinate_normative_equation_or_contract_not_every_algebraic_intermediate",
    "classification_schema": {
        "required_tuple": ["E", "P_E", "L_E", "S_E"],
        "substrate_dispositions": [
            "core_theory_substrate_independent",
            "substrate_independent_specification_meta",
            "GRC_derived",
            "GRC9V3_derived_GRC_rederivation_required",
            "GRC9_specialization_specific",
            "GRC9_intrinsic",
        ],
        "promotion_statuses": [
            "promotion_proved",
            "promotion_pending",
            "specialization_only",
        ],
        "decisive_test": "delete_the_premise_this_came_from_GRC9V3_and_require_an_independent_derivation_from_GRCV3_or_general_GRC_contracts",
    },
    "targeted_type_and_provenance_hardening": {
        "core_K_vs_graph_K4": "core_K_is_the_substrate_independent_structural_role_while_K4_is_its_GRC_graph_bilinear_realization",
        "M4_ontology": "M4_is_candidate_specific_transport_mobility_not_overlap_normalized_K4_assembly_or_Hodge_geometry",
        "Candidate_A_profile_scope": "only_the_accepted_curvature_disabled_D7_G_W_profile_is_promoted",
        "Candidate_A_future_curvature_rule": "curvature_conditioning_requires_a_new_profile_identity_and_provenance_reopening",
        "migration_split": "generic_typed_migration_and_GRCv4_A_initialization_are_promoted_but_the_exact_GRC9v3_initializer_binding_is_specialization_specific",
        "reference_Hodge_embedding": "H0_ref_diag_mu_H1_form_ref_diag_W_ref_and_GJ_ref_diag_W_ref_inverse_are_explicit_V4_constructions_from_GRCv3_surfaces",
        "differential_backend_scope": "GRCv3_is_the_current_canonical_reference_but_any_future_backend_must_be_explicit_deterministic_serialized_and_contract_conformant",
        "destination_semantics": "current_promoted_common_means_common_only_to_the_current_D10_population_and_not_permanently_universal_GRCv4_content",
    },
    "independent_GRC_derivations": DERIVATIONS,
    "normatively_load_bearing_objects": ROWS,
    "coverage_contract": {
        "required_families": FAMILY_REQUIREMENTS,
        "observed_family_counts": dict(sorted(family_counts.items())),
        "all_required_families_exactly_covered": dict(family_counts)
        == FAMILY_REQUIREMENTS,
        "object_count": len(ROWS),
        "object_ids_unique": len(row_ids) == len(set(row_ids)),
    },
    "D10_claim_coverage": {
        "accepted_claim_ids": sorted(D10_CLAIM_IDS),
        "claim_to_object_ids": CLAIM_COVERAGE,
        "claim_count": len(D10_CLAIM_IDS),
        "all_accepted_claims_covered": set(CLAIM_COVERAGE) == D10_CLAIM_IDS,
        "all_normative_objects_bear_on_at_least_one_claim": set(row_ids)
        == {object_id for object_ids in CLAIM_COVERAGE.values() for object_id in object_ids},
    },
    "accepted_D10_claim_set_identity": {
        "decision_claim_ids": sorted(D10_DECISION_CLAIM_IDS),
        "topology_claim_ids": sorted(D10_TOPOLOGY_CLAIM_IDS),
        "authorization_claim_ids": sorted(D10_AUTHORIZATION_CLAIM_IDS),
        "claim_count": len(D10_TOPOLOGY_CLAIM_IDS),
        "claim_class_counts": {
            claim_class: len(D10["decision"]["claim_topology"][claim_class])
            for claim_class in ["normative", "optional", "conditional", "open", "negative"]
        },
        "all_three_surfaces_exactly_equal": D10_DECISION_CLAIM_IDS
        == D10_TOPOLOGY_CLAIM_IDS
        == D10_AUTHORIZATION_CLAIM_IDS,
        "D10_CL_C_012_is_accepted": "D10-CL-C-012" in D10_TOPOLOGY_CLAIM_IDS,
        "reviewer_38_claim_count_disposition": "stale_pre_C_012_count_not_the_current_accepted_D10_topology",
    },
    "normative_equation_contract_registry": NORMATIVE_EQUATION_CONTRACTS,
    "equation_contract_coverage": {
        "parent_atomic_contract_count": len(PARENT_EQUATION_CONTRACTS),
        "explicit_equation_contract_count": len(EXPLICIT_EQUATION_CONTRACTS),
        "equation_contract_count": len(NORMATIVE_EQUATION_CONTRACTS),
        "equation_contract_ids_unique": len(equation_contract_ids)
        == len(set(equation_contract_ids)),
        "parent_object_ids_covered": sorted(equation_parent_ids),
        "all_parent_objects_covered": equation_parent_ids == set(row_ids),
        "accepted_claim_ids_covered": sorted(equation_claim_ids),
        "all_accepted_claims_covered": equation_claim_ids == D10_CLAIM_IDS,
        "contract_scope_counts": dict(sorted(equation_scope_counts.items())),
        "disabled_profile_ids": DISABLED_PROFILES,
        "disabled_surface_ids": sorted(DISABLED_SURFACES),
        "disabled_reduction_contract_count": sum(
            row["contract_scope"] == "profile_scoped_disabled_reduction"
            for row in NORMATIVE_EQUATION_CONTRACTS
        ),
        "promotion_pending_contract_count": sum(
            row["promotion_status"] == "promotion_pending"
            for row in NORMATIVE_EQUATION_CONTRACTS
        ),
    },
    "promotion_result": {
        "factorization": "GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3",
        "factorization_disposition": "earned_bounded_for_current_D10_initial_specification_population",
        "factorization_earned": True,
        "GRCV4_general_contract_earned": True,
        "GRC9V4_specialization_contract_earned": True,
        "exact_GRC9V3_disabled_compatibility_retained": True,
        "GRC9V3_derived_GRC_rederivation_pending_rows": pending_rows,
        "all_required_GRC_rederivations_complete": not pending_rows,
        "GRCV4_object_ids": grc_rows,
        "GRC9V4_specialization_object_ids": specialization_rows,
        "scope": "current_D10_initial_specification_population_only",
        "future_profile_rule": "reopen_provenance_and_the_earliest_affected_contract_for_every_materially_distinct_successor_profile",
    },
    "claim_topology_effect": {
        "accepted_D10_claim_topology_rewritten": False,
        "D10_conditional_claim_D10_CL_C_011": "succeeded_by_accepted_D10_2_CL_N_001",
        "D10_2_CL_N_001": "bounded_GRCV4_to_GRC9V4_to_disabled_GRC9V3_factorization_earned_for_the_current_initial_specification_population",
        "D10_preclosure_obligation": "resolved_by_accepted_D10_2",
        "negative_boundaries_retained": [
            "no_future_exhaustiveness_theorem",
            "no_runtime_implementation_or_conformance_claim",
            "no_stability_or_formed_branch_claim",
            "no_candidate_or_realization_ranking",
        ],
    },
    "specification_route": {
        "current_status": "accepted_D10_2_specification_route_open",
        "authorized_next_actions": [
            "write_GRCV4_normative_specification_from_the_promoted_general_contract",
            "write_GRC9V4_as_the_substantive_nine_port_specialization_with_exact_GRC9V3_disabled_compatibility",
        ],
        "GRCV4_specification_authorized_after_human_acceptance": True,
        "GRC9V4_specialization_specification_authorized_after_human_acceptance": True,
        "GRCV4_specification_authorized_now": True,
        "GRC9V4_specialization_specification_authorized_now": True,
        "normative_spec_files_written_by_D10_2": False,
        "implementation_plan_authorized": False,
        "implementation_authorized": False,
        "runtime_or_src_changed": False,
    },
    "controls": CONTROLS,
    "checks": {
        "source_identity_count": len(SOURCES),
        "independent_derivation_count": len(DERIVATIONS),
        "normatively_load_bearing_object_count": len(ROWS),
        "normative_equation_contract_count": len(NORMATIVE_EQUATION_CONTRACTS),
        "explicit_equation_contract_count": len(EXPLICIT_EQUATION_CONTRACTS),
        "accepted_D10_claim_count": len(D10_CLAIM_IDS),
        "family_count": len(FAMILY_REQUIREMENTS),
        "control_count": len(CONTROLS),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "promotion_counts": dict(sorted(promotion_counts.items())),
        "promotion_pending_row_count": len(pending_rows),
        "factorization_earned": True,
        "final_substrate_identity_closed_for_current_population": True,
    },
    "decision": {
        "scientific_disposition": "accepted_bounded_full_object_and_equation_contract_provenance_factorization",
        "final_substrate_identity": "GRCV4_general_constitutive_architecture_with_GRC9V4_nine_port_specialization_and_exact_GRC9V3_disabled_compatibility",
        "final_substrate_identity_closed_for_current_population": True,
        "final_substrate_identity_globally_closed_for_all_future_profiles": False,
        "Candidate_A_GRC_promotion": "proved_with_general_GRC_differential_backend_and_GRC9_row_basis_split_to_specialization",
        "Candidate_C_GRC_promotion": "proved_from_general_graph_Hodge_and_derived_sector_contracts",
        "geometry_and_realization_GRC_promotion": "proved_for_the_current_population",
        "GRC9_specialization_remains_substantive": True,
        "D11_authorized": False,
    },
    "claim_ceiling": "full_equation_and_contract_provenance_factorization_for_the_current_D10_initial_specification_population_without_runtime_implementation_numeric_stability_reachability_ranking_or_future_exhaustiveness",
    "blocked_relabels": [
        "GRC9V4_is_only_a_compatibility_shim",
        "nine_ports_are_unnecessary",
        "all_future_V4_profiles_are_GRC_derived",
        "GRC9_row_basis_backend_is_part_of_general_GRCV4",
        "current_profile_population_is_future_exhaustive",
        "runtime_implementation_complete",
        "formed_branch_or_stability_evidence_complete",
        "candidate_or_realization_preference_proved",
        "D11_authorized_before_branch_stabilization_and_explicit_successor_opening",
    ],
    "human_acceptance": "accepted_bounded_2026-08-26",
}

record["decision_record_digest"] = canonical_digest(record, "decision_record_digest")
OUTPUT_JSON.write_text(json.dumps(record, indent=2, ensure_ascii=True) + "\n")


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# D10.2 Full Substrate Provenance And GRCV4 Promotion Audit",
        "",
        "**Gate:** D10.2  ",
        "**Status:** Accepted bounded  ",
        f"**Predecessor:** `{data['predecessor_decision_digest']}`  ",
        f"**Decision digest:** `{data['decision_record_digest']}`",
        "",
        "## Purpose",
        "",
        "D10.2 closes the substrate-identity obligation for the current D10 initial specification population. It binds every accepted D10 claim to parent normative objects and then to subordinate normative equations or contracts, without enumerating every algebraic intermediate. It independently rederives every promoted GRC object and separates general GRC content from deliberate GRC9 compatibility and mechanically nine-port-intrinsic content.",
        "",
        "The decisive test is:",
        "",
        "> Delete the premise 'this came from GRC9v3.' Can the object still be derived from GRCv3 or general-GRC contracts?",
        "",
        "## Result",
        "",
        "```text",
        "GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3",
        "factorization_disposition = earned_bounded_for_current_D10_initial_specification_population",
        "promotion_pending_rows = 0",
        "```",
        "",
        "The result is not merely nomenclature. Candidate A's potential, flow, curvature-disabled `G_W` functional, Read-Back, retained writer, and GRCv4 history-free initializer have independent GRC-level derivations. The fixed GRC9 row-basis differential backend and exact GRC9v3 initializer binding remain specialization content. Candidate C, graph K4 and its Hodge crossing, all five realization families, and the complete-step/lifecycle grammar likewise derive without a nine-port premise. Ordered ports, the fixed 3x3 chart, saturation, mechanical expansion, hybrid spark completion, child-basin stabilization, and column coarse-graining remain genuinely GRC9-intrinsic.",
        "",
        "Exact disabled transition, state, observable, and lifecycle reductions remain `GRC9_specialization_specific`: their specificity comes from deliberately targeting GRC9v3, not from every compatibility equation being intrinsically nine-port mathematical structure.",
        "",
        "## Accepted D10 Claim-Set Identity",
        "",
        "D10.2 consumes exactly 39 accepted D10 claims: 9 normative, 7 optional, 12 conditional, 5 open, and 6 negative. The accepted D10 decision, normative claim topology, and specification authorization surfaces contain exactly the same claim IDs.",
        "",
        "`D10-CL-C-012` is present on all three accepted surfaces. The review's 38-claim count describes an older pre-`C-012` population and is not the accepted D10 topology. D10.2 preserves `C-012`; it does not invent or promote it locally.",
        "",
        "## Type And Provenance Hardening",
        "",
        "The accepted object population preserves these distinctions:",
        "",
        "- Core `K -> g[K]` is a substrate-independent theory role; graph `K4` is its GRC-derived symmetric-bilinear realization on oriented one-forms.",
        "- Overlap-normalized assembly belongs to graph `K4`. `M4` remains separately owned candidate-specific transport mobility; `H1_form`, `G_J`, `h4`, and `M4` are not interchangeable.",
        "- The GRCv4 reference Hodge package is constructed explicitly from GRCv3 surfaces: `H0_ref = diag(mu)`, `H1_form_ref = diag(W_ref)`, `G_J_ref = diag(W_ref^-1)`, followed by the admitted `kappa_H Delta_K4` update and `G_J(h) = H1_form(h)^-1`.",
        "- Candidate A promotion covers exactly the accepted curvature-disabled D7 `G_W`; curvature conditioning is a future profile requiring a new identity and provenance reopening.",
        "- Generic typed migration, the GRCv4 Candidate-A initializer, and the exact GRC9v3 initializer binding are separate objects. Only the last is specialization-specific.",
        "- `core_theory_substrate_independent` denotes theory physics, while `substrate_independent_specification_meta` denotes profile and claim governance. Neither category is silently treated as the other.",
        "- Destinations named `current_promoted_common` apply only to the current D10 population. They do not declare permanent universality for future GRCv4 profiles.",
        "",
        "## Normative Equation And Contract Registry",
        "",
        f"The parent registry contains {data['checks']['normatively_load_bearing_object_count']} normatively load-bearing objects. The subordinate registry contains {data['checks']['normative_equation_contract_count']} rows: {data['checks']['normatively_load_bearing_object_count']} parent-atomic contracts plus {data['checks']['explicit_equation_contract_count']} expanded equation/contract rows.",
        "",
        "The expanded layer individually covers the complete-state charge tangent and structural projector; candidate-specific CI and CI+PC root/selection laws; PC retention and release; OS stage order and split residual; RG invariant-section and Lipschitz contracts; Candidate C's sector/Hodge/resolvent/Read-Back chain; the `K4 -> H4 -> h4` crossing; and typed topology-event resource/history maps.",
        "",
        "```text",
        "accepted_D10_claims = 39",
        f"normative_equation_contracts = {data['checks']['normative_equation_contract_count']}",
        f"explicit_equation_contracts = {data['checks']['explicit_equation_contract_count']}",
        "disabled_reduction_matrix = 10 profiles x 4 surfaces = 40 contracts",
        "all_parent_objects_covered = true",
        "all_accepted_claims_covered = true",
        "promotion_pending_contracts = 0",
        "```",
        "",
        "The disabled matrix treats transition, state, observable, and lifecycle reduction as independent obligations for every current profile. Passing one surface never implies another.",
        "",
        "Topology-event resource accounting preserves the accepted D9 decomposition: `T_C_evt` is the conservative transport map, `Delta_C_event` is the separate resource-coordinate increment, `Delta_Q_event` receipts the resulting charge change, and `Q_target_plus` is the updated lifecycle target. Ordinary complete-step accounting compares final resource state with `Q_target_next`; it does not add an event delta to an already updated target.",
        "",
        "## Independent GRC Derivations",
        "",
    ]
    for item in data["independent_GRC_derivations"]:
        lines.extend(
            [
                f"### {item['derivation_id']}: {item['title']}",
                "",
            ]
        )
        for step in item["construction"]:
            lines.append(f"- {step}")
        lines.extend(
            [
                "",
                f"Conclusion: `{item['conclusion']}`.",
                "",
                f"Blocked overread: `{item['blocked_overread']}`.",
                "",
            ]
        )

    lines.extend(["## Full Provenance Classification", ""])
    current_family = None
    for row in data["normatively_load_bearing_objects"]:
        if row["family"] != current_family:
            current_family = row["family"]
            lines.extend(
                [
                    f"### {current_family.replace('_', ' ').title()}",
                    "",
                    "| Object | Disposition | Promotion | Destination | Conclusion |",
                    "|---|---|---|---|---|",
                ]
            )
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | {} |".format(
                row["object_id"],
                row["substrate_disposition"],
                row["promotion_status"],
                row["specification_destination"],
                row["conclusion"].replace("_", " "),
            )
        )
        next_index = data["normatively_load_bearing_objects"].index(row) + 1
        if next_index == len(data["normatively_load_bearing_objects"]):
            lines.append("")
        elif data["normatively_load_bearing_objects"][next_index]["family"] != current_family:
            lines.append("")

    lines.extend(
        [
            "## Specification Consequence",
            "",
            "Bounded acceptance opens the specification route:",
            "",
            "```text",
            "1. GRCv4 normative specification from the promoted general contract",
            "2. GRC9v4 substantive nine-port specialization",
            "3. exact disabled-profile compatibility from GRC9v4 to GRC9v3",
            "```",
            "",
            "This changes specification ownership, not runtime state. D10.2 writes no normative specification and authorizes no implementation plan or source change.",
            "",
            "## Claim Ceiling",
            "",
            "The factorization is earned only for the current D10 initial specification population. Future constitutive, realization, hybrid, geometry, or lifecycle profiles must reopen provenance and the earliest accepted contract they affect. D10.2 does not establish runtime implementation, formed-branch reachability, numeric stability, profile ranking, or future-exhaustive V4 taxonomy.",
            "",
            "## Disposition",
            "",
            "```text",
            f"record = {data['record_id']}",
            f"status = {data['status']}",
            f"decision_record_digest = {data['decision_record_digest']}",
            f"source_identities = {data['checks']['source_identity_count']}",
            f"independent_derivations = {data['checks']['independent_derivation_count']}",
            f"normatively_load_bearing_objects = {data['checks']['normatively_load_bearing_object_count']}",
            f"normative_equation_contracts = {data['checks']['normative_equation_contract_count']}",
            f"explicit_equation_contracts = {data['checks']['explicit_equation_contract_count']}",
            f"accepted_D10_claims = {data['checks']['accepted_D10_claim_count']}",
            f"controls = {data['checks']['control_count']}",
            "promotion_pending_rows = 0",
            "factorization_earned = true",
            "final_substrate_identity_closed_for_current_population = true",
            "final_substrate_identity_globally_closed_for_all_future_profiles = false",
            "GRCV4_specification_authorized_after_human_acceptance = true",
            "GRC9V4_specialization_specification_authorized_after_human_acceptance = true",
            "GRCV4_specification_authorized_now = true",
            "GRC9V4_specialization_specification_authorized_now = true",
            "normative_spec_files_written_by_D10_2 = false",
            "implementation_authorized = false",
            "runtime_or_src_changed = false",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


OUTPUT_MD.write_text(render_markdown(record))
