#!/usr/bin/env python3
"""Build the bounded GRC9V4 D10.1 preliminary provenance record."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "implementation/investigations/grc9v4-constitutive-design"
DECISIONS = BASE / "decisions"
OUTPUT_JSON = DECISIONS / "D10_1PreliminarySubstrateProvenance.json"
OUTPUT_MD = DECISIONS / "D10_1PreliminarySubstrateProvenance.md"


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


def finding(
    finding_id: str,
    statement: str,
    evidence_refs: list[str],
    current_status: str,
    blocked_overread: str,
) -> dict[str, Any]:
    return {
        "finding_id": finding_id,
        "statement": statement,
        "evidence_refs": evidence_refs,
        "current_status": current_status,
        "blocked_overread": blocked_overread,
    }


def provenance_row(
    object_id: str,
    object_kind: str,
    premises_used: list[str],
    source_lineage: list[str],
    substrate_disposition: str,
    promotion_status: str,
    current_finding: str,
    evidence_refs: list[str],
) -> dict[str, Any]:
    return {
        "object_id": object_id,
        "object_kind": object_kind,
        "premises_used": premises_used,
        "source_lineage": source_lineage,
        "substrate_disposition": substrate_disposition,
        "promotion_status": promotion_status,
        "current_finding": current_finding,
        "evidence_refs": evidence_refs,
    }


SOURCES = [
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D10DesignSynthesisAndSpecWritingDecision.json",
        "GRC9V4-CD-D10-v1",
        "accepted_predecessor_and_open_substrate_identity_boundary",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D0TargetInheritanceAndClaimCeiling.json",
        "GRC9V4-CD-D0-v1",
        "exact_GRC9V3_inheritance_target_and_disabled_profile_boundary",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D7ClosedWriteReadLoop.json",
        "GRC9V4-CD-D7-v1",
        "candidate_A_exact_GRC9V3_formula_reuse_and_revision_specific_writer",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D7GGlobalMetricAndStructuralCultivationClosure.json",
        "GRC9V4-CD-D7G-v1",
        "GRC9V3_source_check_and_missing_K_to_h_crossing",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D7Gv2GeometryParametricClosureAndFinalization.json",
        "GRC9V4-CD-D7G-v2",
        "V3_reference_embedding_and_revision_specific_geometry_profile",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D9CompleteStepAndLifecycleContract.json",
        "GRC9V4-CD-D9-v1",
        "exact_disabled_GRC9V3_reduction_and_typed_graph_event_contract",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "GeometryTemporalRealizationSuccessorCoupledImplicit.json",
        "GRC9V4-GTRS-CI-v1",
        "direct_coupled_implicit_realization_source",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "GeometryTemporalRealizationSuccessorOperatorSplit.json",
        "GRC9V4-GTRS-OS-v1",
        "direct_operator_split_realization_source",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "GeometryTemporalRealizationSuccessorReconstructedGeometry.json",
        "GRC9V4-GTRS-RG-v1",
        "direct_reconstructed_geometry_realization_source",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "GeometryTemporalRealizationSuccessorPersistentCarrier.json",
        "GRC9V4-GTRS-PC-v1",
        "direct_persistent_carrier_realization_source",
    ),
    source(
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "GeometryTemporalRealizationHybridCoupledPersistentCarrier.json",
        "GRC9V4-GTRS-CI-PC-v1",
        "direct_coupled_persistent_hybrid_realization_source",
    ),
    source(
        "specs/grc-9-v3-spec.md",
        "GRC9V3-NORMATIVE-SPEC",
        "legacy_nine_port_substrate_and_complete_step_contract",
    ),
    source(
        "specs/grc-v3-spec.md",
        "GRCV3-NORMATIVE-SPEC",
        "general_GRC_semantic_and_differential_comparison_surface",
    ),
    source(
        "implementation/Phase-7-EquationMap.md",
        "PHASE7-GRC9V3-EQUATION-MAP",
        "GRC9_mechanical_GRCV3_semantic_and_hybrid_ownership_map",
    ),
    source(
        "src/pygrc/models/grc_9_v3_runtime.py",
        "GRC9V3-RUNTIME-SOURCE",
        "implemented_conductance_potential_flux_and_row_basis_mechanics",
    ),
    source(
        "src/pygrc/models/grc_v3.py",
        "GRCV3-RUNTIME-SOURCE",
        "implemented_general_GRC_conductance_potential_and_flux_comparison",
    ),
]


FINDINGS = [
    finding(
        "D10.1-P1",
        "GRC9V3_provenance_is_load_bearing_for_the_current_lineage_local_design",
        ["GRC9V4-CD-D7-v1", "GRC9V4-CD-D9-v1", "GRC9V3-RUNTIME-SOURCE"],
        "supported_preliminary",
        "the_design_is_only_generically_inspired_and_does_not_consume_GRC9V3",
    ),
    finding(
        "D10.1-P2",
        "current_evidence_does_not_establish_intrinsic_nine_port_necessity_for_the_new_constitutive_architecture",
        ["GRC9V4-CD-D7G-v1", "GRCV3-RUNTIME-SOURCE", "PHASE7-GRC9V3-EQUATION-MAP"],
        "supported_negative_current_evidence_boundary",
        "nine_ports_are_unnecessary",
    ),
    finding(
        "D10.1-P3",
        "Candidate_A_is_GRC9V3_derived_and_appears_liftable_to_GRCV4_but_requires_an_independent_derivation_over_GRCV3_differential_and_transport_contracts_before_promotion_from_the_GRC9_lineage",
        ["GRC9V4-CD-D7-v1", "GRC9V3-RUNTIME-SOURCE", "GRCV3-RUNTIME-SOURCE"],
        "supported_preliminary_promotion_pending",
        "Candidate_A_is_already_GRC_derived",
    ),
    finding(
        "D10.1-P4",
        "Candidate_C_and_the_K4_Hodge_realization_surface_are_stronger_GRC_level_candidates_but_are_not_yet_promoted_from_the_GRC9_lineage_to_GRCV4",
        ["GRC9V4-CD-D7G-v1", "GRC9V4-CD-D7G-v2", "GRC9V4-CD-D10-v1"],
        "supported_preliminary_promotion_pending",
        "graph_shaped_notation_alone_proves_GRC_level_provenance",
    ),
    finding(
        "D10.1-P5",
        "ordered_ports_fixed_row_column_mechanics_mechanical_expansion_hybrid_sparks_child_basin_stabilization_and_column_coarse_graining_are_GRC9_intrinsic_while_exact_disabled_reduction_and_lifecycle_targeting_are_GRC9_specialization_specific",
        ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP", "GRC9V4-CD-D9-v1"],
        "supported_preliminary_specialization_boundary",
        "an_abstractable_constitutive_core_makes_GRC9_a_compatibility_shim",
    ),
]


ROWS = [
    provenance_row(
        "legacy_disabled_transition_and_lifecycle_reduction",
        "compatibility_contract",
        ["exact_GRC9V3_transition_state_observable_event_and_lifecycle_semantics"],
        ["GRC9V4-CD-D0-v1", "GRC9V4-CD-D9-v1"],
        "GRC9_specialization_specific",
        "specialization_only",
        "load_bearing_exact_GRC9V3_compatibility_target_that_is_deliberately_specific_to_the_nine_port_specialization",
        ["GRC9V4-CD-D9-v1"],
    ),
    provenance_row(
        "A_baseline_potential_and_potential_flow_current",
        "equation_family",
        ["live_graph_incidence", "scalar_edge_mobility", "site_potential", "GRC9V3_stage_contract"],
        ["GRC9V3-RUNTIME-SOURCE", "GRC9V4-CD-D7-v1", "GRCV3-RUNTIME-SOURCE"],
        "GRC9V3_derived_GRC_rederivation_required",
        "promotion_pending",
        "exactly_reused_from_GRC9V3_and_equation_shaped_like_GRCV3_but_not_yet_independently_rederived_over_GRCV3_contracts",
        ["GRC9V4-CD-D7-v1", "GRC9V3-RUNTIME-SOURCE", "GRCV3-RUNTIME-SOURCE"],
    ),
    provenance_row(
        "A_instantaneous_conductance_target_G_W",
        "equation_family",
        [
            "inherited_GRC9V3_conductance_functional",
            "GRC9V3_row_basis_gradient_backend",
            "sign_even_current_squared_functional_dependence",
            "positive_floor",
            "enabled_A_pre_read_uses_fresh_J0_A_not_incoming_stored_current",
            "enabled_A_writer_uses_postcontinuity_C_and_solved_JC_A",
        ],
        ["GRC9V3-RUNTIME-SOURCE", "GRC9V4-CD-D7-v1"],
        "GRC9V3_derived_GRC_rederivation_required",
        "promotion_pending",
        "the_functional_form_is_inherited_from_GRC9V3_but_enabled_A_uses_revision_distinct_pre_read_and_writer_staging_while_the_backend_remains_to_be_rederived_over_GRCV3_contracts",
        ["GRC9V3-RUNTIME-SOURCE", "GRCV3-RUNTIME-SOURCE", "GRC9V4-CD-D7-v1"],
    ),
    provenance_row(
        "general_GRC_continuity_and_charge_covector_accounting",
        "invariant_contract",
        ["oriented_graph_incidence", "typed_resource_measure", "atomic_resource_write"],
        ["GRCV3-NORMATIVE-SPEC", "GRC9V4-CD-D9-v1"],
        "GRC_derived",
        "promotion_pending",
        "ordinary_graph_GRC_continuity_and_general_charge_covector_accounting_with_no_identified_nine_port_premise",
        ["GRC9V4-CD-D9-v1"],
    ),
    provenance_row(
        "unit_measure_Q_equals_sum_C_reference_profile",
        "current_reference_profile_contract",
        ["unit_site_measure", "Q_equals_sum_of_site_coherence", "current_population_profile"],
        ["GRCV3-NORMATIVE-SPEC", "GRC9V4-CD-D9-v1"],
        "GRC_derived",
        "specialization_only",
        "ordinary_GRC_level_unit_measure_profile_that_does_not_define_the_general_GRCV4_charge_contract",
        ["GRCV3-NORMATIVE-SPEC", "GRC9V4-CD-D9-v1"],
    ),
    provenance_row(
        "A_directional_contrast_Read_Back_and_total_current_closure",
        "revision_specific_constitutive_completion",
        ["positive_edge_mobility", "present_current", "oriented_edge_cochain", "regular_gain_domain"],
        ["GRC9V4-CD-D7-v1"],
        "GRC_derived",
        "promotion_pending",
        "the_admitted_read_and_closure_use_graph_edge_objects_without_an_identified_nine_port_only_premise",
        ["GRC9V4-CD-D7-v1"],
    ),
    provenance_row(
        "A_log_geometric_retained_mobility_writer",
        "revision_specific_constitutive_completion",
        ["positive_mobility_domain", "postcontinuity_G_W_target", "one_beat_delayed_writer"],
        ["GRC9V4-CD-D7-v1"],
        "GRC_derived",
        "promotion_pending",
        "new_V4_completion_built_from_the_GRC9V3_target_surface_not_inherited_core_or_nine_port_mechanics",
        ["GRC9V4-CD-D7-v1"],
    ),
    provenance_row(
        "C_derived_sector_graph_Hodge_Read_Back",
        "revision_specific_constitutive_completion",
        ["graph_incidence", "positive_Hodge_stars", "derived_C_sector", "typed_flat_sharp_maps"],
        ["GRC9V4-CD-D7G-v2", "GRC9V4-CD-D10-v1"],
        "GRC_derived",
        "promotion_pending",
        "strong_GRC_level_candidate_with_no_identified_ordered_port_premise",
        ["GRC9V4-CD-D7G-v2", "GRC9V4-CD-D10-v1"],
    ),
    provenance_row(
        "K4_H4_h4_structural_crossing_and_Hodge_typing",
        "core_to_graph_realization_contract",
        ["core_K_to_g_requirement", "graph_local_bilinear_assembly", "form_space_Hodge_typing"],
        ["GRC9V4-CD-D7G-v1", "GRC9V4-CD-D7G-v2"],
        "GRC_derived",
        "promotion_pending",
        "the_crossing_is_new_and_was_not_already_executed_by_the_GRC9V3_row_basis_tensor_cache",
        ["GRC9V4-CD-D7G-v1", "GRC9V4-CD-D7G-v2"],
    ),
    provenance_row(
        "CI_OS_RG2b_PC_and_CI_PC_realization_contracts",
        "temporal_and_history_realization_families",
        ["accepted_A_or_C_constitutive_maps", "graph_geometry_profile", "declared_state_and_stage_authority"],
        [
            "GRC9V4-GTRS-CI-v1",
            "GRC9V4-GTRS-OS-v1",
            "GRC9V4-GTRS-RG-v1",
            "GRC9V4-GTRS-PC-v1",
            "GRC9V4-GTRS-CI-PC-v1",
            "GRC9V4-CD-D10-v1",
        ],
        "GRC_derived",
        "promotion_pending",
        "no_current_result_makes_the_realization_families_intrinsically_nine_port",
        [
            "GRC9V4-GTRS-CI-v1",
            "GRC9V4-GTRS-OS-v1",
            "GRC9V4-GTRS-RG-v1",
            "GRC9V4-GTRS-PC-v1",
            "GRC9V4-GTRS-CI-PC-v1",
            "GRC9V4-CD-D10-v1",
        ],
    ),
    provenance_row(
        "typed_topology_event_and_profile_migration_grammar",
        "lifecycle_contract",
        ["typed_source_target_graph_map", "resource_receipt", "history_transport_or_loss", "target_readmission"],
        ["GRC9V4-CD-D9-v1"],
        "GRC_derived",
        "promotion_pending",
        "the_grammar_is_graph_typed_while_exact_GRC9V3_event_parity_remains_specialization_content",
        ["GRC9V4-CD-D9-v1"],
    ),
    provenance_row(
        "ordered_nine_port_chart_mechanical_expansion_hybrid_spark_and_column_coarse_graining",
        "substrate_capability_family",
        ["nine_ordered_ports", "fixed_3_by_3_row_column_chart", "port_saturation", "GRC9_mechanical_expansion"],
        ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP"],
        "GRC9_intrinsic",
        "specialization_only",
        "genuine_nine_port_specialization_content_preserved_by_the_lineage_local_successor_scope",
        ["GRC9V3-NORMATIVE-SPEC", "PHASE7-GRC9V3-EQUATION-MAP"],
    ),
]


CONTROLS = [
    "GRCV3_is_general_graph_GRC_and_GRC9V3_is_its_nine_port_specialization",
    "GraphGRCV4_is_not_a_distinct_naming_family_from_GRCV4",
    "formula_contains_no_9_does_not_prove_GRC_level_provenance",
    "GRC9V3_lineage_does_not_prove_nine_port_intrinsicness",
    "absence_of_demonstrated_nine_port_necessity_does_not_prove_nine_ports_unnecessary",
    "abstractable_constitutive_core_does_not_reduce_GRC9_specialization_to_a_shim",
    "representative_preliminary_rows_do_not_claim_equation_by_equation_audit_completeness",
    "D10_1_does_not_modify_the_accepted_D10_claim_topology",
    "working_factorization_is_not_final_taxonomy_or_promotion",
    "promotion_from_the_GRC9_lineage_to_GRCV4_requires_independent_derivation_over_GRCV3_contracts_not_notational_relabeling",
    "exact_GRC9V3_disabled_reduction_remains_required_for_the_current_lineage_local_profiles",
    "inherited_functional_form_provenance_is_separate_from_enabled_revision_specific_staging",
    "general_charge_covector_accounting_is_separate_from_the_unit_measure_reference_profile",
    "composite_realization_classification_binds_each_direct_realization_decision",
    "no_specification_or_implementation_authority_is_added_by_D10_1",
]


record: dict[str, Any] = {
    "record_id": "GRC9V4-CD-D10.1-v1",
    "gate_id": "D10.1",
    "title": "Preliminary Substrate Provenance And Nine-Port Necessity Classification",
    "status": "accepted_preliminary_bounded_substrate_provenance_separation",
    "date": "2026-08-26",
    "predecessor_decision_digest": "3e673b335ad428d01006f231765d060a9bdd5f134332b143048f774de94bad00",
    "supersedes": None,
    "purpose": "record_the_first_bounded_substantive_result_on_D10_final_substrate_identity_without_performing_or_preempting_the_final_preclosure_equation_by_equation_audit",
    "scope": {
        "D10_authorization_unchanged": True,
        "D10_claim_topology_unchanged": True,
        "representative_provenance_classification_only": True,
        "equation_by_equation_audit_complete": False,
        "promotion_proved": False,
        "final_substrate_identity_closed": False,
        "runtime_or_src_changed": False,
    },
    "source_identities": SOURCES,
    "classification_schema": {
        "required_tuple": ["E", "P_E", "L_E", "S_E"],
        "meanings": {
            "E": "equation_contract_lifecycle_rule_or_capability",
            "P_E": "premises_actually_used_in_derivation",
            "L_E": "source_lineage",
            "S_E": "substrate_disposition",
        },
        "substrate_dispositions": [
            "core_substrate_independent",
            "GRC_derived",
            "GRC9V3_derived_GRC_rederivation_required",
            "GRC9_specialization_specific",
            "GRC9_intrinsic",
        ],
        "promotion_statuses": ["promotion_proved", "promotion_pending", "specialization_only"],
        "classification_rule": "classify_from_actual_derivation_premises_and_lineage_not_symbol_or_formula_appearance",
    },
    "preliminary_findings": FINDINGS,
    "representative_provenance_rows": ROWS,
    "taxonomy_contract": {
        "GRCV3": "general_graph_GRC_without_the_nine_port_specialization",
        "GRC9V3": "nine_port_specialization_profile_of_GRCV3",
        "GRCV4": "prospective_general_graph_GRC_V4_constitutive_architecture",
        "GRC9V4": "prospective_nine_port_specialization_profile_of_GRCV4",
        "historical_D10_generic_Graph_GRC_V4_phrase": "descriptive_reference_to_GRCV4_not_a_distinct_naming_family",
    },
    "working_factorization_hypothesis": {
        "expression": "GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3",
        "status": "hypothesis_supported_by_preliminary_provenance_separation",
        "promotion_proved": False,
        "interpretation": "a_possible_GRCV4_constitutive_architecture_with_GRC9V4_as_its_substantive_nine_port_specialization_and_GRC9V3_as_the_exact_disabled_profile_compatibility_target",
    },
    "final_audit_handoff": {
        "obligation_id": "D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT",
        "still_required": True,
        "must_cover_every_selected_normative_equation_and_contract": True,
        "must_supply_independent_derivation_over_GRCV3_contracts_before_promotion_to_GRCV4": True,
        "must_separate_constitutive_core_specialization_capabilities_and_compatibility_reduction": True,
        "must_not_classify_from_formula_appearance": True,
    },
    "controls": CONTROLS,
    "checks": {
        "source_identity_count": len(SOURCES),
        "preliminary_finding_count": len(FINDINGS),
        "representative_provenance_row_count": len(ROWS),
        "control_count": len(CONTROLS),
        "all_required_findings_present": {row["finding_id"] for row in FINDINGS}
        == {f"D10.1-P{index}" for index in range(1, 6)},
        "nine_port_intrinsic_row_present": any(
            row["substrate_disposition"] == "GRC9_intrinsic" for row in ROWS
        ),
        "GRC9V3_derived_rows_present": any(
            row["substrate_disposition"]
            == "GRC9V3_derived_GRC_rederivation_required"
            for row in ROWS
        ),
        "GRC_derived_rows_present": any(
            row["substrate_disposition"] == "GRC_derived" for row in ROWS
        ),
        "GRC9_specialization_specific_row_present": any(
            row["substrate_disposition"] == "GRC9_specialization_specific"
            for row in ROWS
        ),
        "promotion_proved": False,
        "final_substrate_identity_closed": False,
    },
    "decision": {
        "scientific_disposition": "accepted_preliminary_bounded_substrate_provenance_separation",
        "lineage_local_name_meaning": "derivation_and_compatibility_provenance_not_intrinsic_nine_port_necessity",
        "GRC9V3_provenance_load_bearing": True,
        "intrinsic_nine_port_necessity_established": False,
        "nine_ports_unnecessary_established": False,
        "Candidate_A_GRCV4_promotion": "pending_independent_derivation_over_GRCV3_differential_and_transport_contracts",
        "Candidate_C_and_K4_Hodge_GRCV4_promotion": "pending_full_provenance_stripping_and_independent_GRC_level_derivation",
        "GRC9_specialization_content_remains_substantive": True,
        "final_audit_replaced": False,
    },
    "claim_ceiling": "preliminary_provenance_separation_and_working_factorization_hypothesis_only",
    "blocked_relabels": [
        "GRC9V4_is_intrinsically_nine_port",
        "nine_ports_are_unnecessary",
        "Candidate_A_is_already_GRC_derived",
        "Candidate_C_graph_notation_proves_GRCV4_promotion",
        "GRC9_is_only_a_compatibility_shim",
        "preclosure_provenance_audit_complete",
        "final_substrate_identity_closed",
        "GRCV4_specification_authorized",
    ],
    "open_obligations": ["D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT"],
    "authorization_effect": {
        "D10_lineage_local_specification_authorization_unchanged": True,
        "GRCV4_specification_authorized": False,
        "implementation_plan_authorized": False,
        "implementation_authorized": False,
        "runtime_or_src_changed": False,
    },
    "human_acceptance": "accepted_preliminary_bounded_substrate_provenance_separation_2026-08-26",
}

record["decision_record_digest"] = canonical_digest(record, "decision_record_digest")
OUTPUT_JSON.write_text(json.dumps(record, indent=2, ensure_ascii=True) + "\n")


def render_markdown(data: dict[str, Any]) -> str:
    rows = data["representative_provenance_rows"]
    findings = data["preliminary_findings"]
    lines = [
        "# D10.1 Preliminary Substrate Provenance And Nine-Port Necessity Classification",
        "",
        "**Gate:** D10.1  ",
        "**Status:** Accepted preliminary bounded substrate-provenance separation  ",
        f"**Predecessor:** `{data['predecessor_decision_digest']}`  ",
        f"**Decision digest:** `{data['decision_record_digest']}`",
        "",
        "## Purpose And Boundary",
        "",
        "D10 freezes the architecture currently authorized for lineage-local specification writing. D10.1 records the first bounded substantive finding about the substrate identity of that architecture. It does not rewrite D10, complete the final provenance audit, promote the design from the GRC9 lineage to GRCv4, or authorize implementation.",
        "",
        "> The lineage-local name `GRC9V4` records derivation and compatibility provenance. It does not assert that the new V4 constitutive architecture intrinsically requires nine ports.",
        "",
        "The repository taxonomy is `GRCv3` for general graph GRC and `GRC9v3` for its nine-port specialization. Accordingly, the prospective general successor is `GRCv4`, while `GRC9v4` is its substantive nine-port specialization. The descriptive D10 phrase `generic Graph GRC V4` refers to `GRCv4`; it does not introduce a separate `GraphGRCV4` naming family.",
        "",
        "The distinction is:",
        "",
        "```text",
        "D10   = architecture currently authorized",
        "D10.1 = current bounded knowledge about that architecture's substrate identity",
        "final pre-closure audit = equation/contract-by-equation proof of final factorization",
        "```",
        "",
        "## Preliminary Findings",
        "",
    ]
    for item in findings:
        lines.extend(
            [
                f"### {item['finding_id']}",
                "",
                item["statement"].replace("_", " ") + ".",
                "",
                f"Status: `{item['current_status']}`. Blocked overread: `{item['blocked_overread']}`.",
                "",
            ]
        )
    lines.extend(
        [
            "## Representative Provenance Classification",
            "",
            "These rows are representative and deliberately incomplete. They sharpen the final audit; they do not replace it.",
            "",
            "| Object | Disposition | Promotion | Current finding |",
            "|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| `{}` | `{}` | `{}` | {} |".format(
                row["object_id"],
                row["substrate_disposition"],
                row["promotion_status"],
                row["current_finding"].replace("_", " "),
            )
        )
    lines.extend(
        [
            "",
            "## Working Factorization Hypothesis",
            "",
            "```text",
            "GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3",
            "```",
            "",
            "This is a hypothesis supported by preliminary provenance separation. `promotion_proved = false`. It means a GRCv4 constitutive architecture with a substantive GRC9v4 specialization is plausible; it does not establish that factorization.",
            "",
            "## Final Audit Contract",
            "",
            "For every selected equation, contract, lifecycle rule, or capability `E`, the final audit must record:",
            "",
            "```text",
            "E   = object under audit",
            "P_E = premises actually used",
            "L_E = source lineage",
            "S_E = substrate disposition",
            "```",
            "",
            "Allowed substrate dispositions are:",
            "",
            "```text",
            "core_substrate_independent",
            "GRC_derived",
            "GRC9V3_derived_GRC_rederivation_required",
            "GRC9_specialization_specific",
            "GRC9_intrinsic",
            "```",
            "",
            "`GRC_derived` means valid at ordinary graph-GRC level without a nine-port premise. `GRC9_specialization_specific` covers deliberate specialization contracts such as exact disabled-profile compatibility with GRC9v3, while `GRC9_intrinsic` is reserved for constructions that mechanically require the nine-port substrate.",
            "",
            "Formula appearance is not provenance. Promotion from the GRC9 lineage to GRCv4 requires an independent derivation over GRCv3 contracts and explicit separation of the constitutive core, GRC9 specialization capabilities, and exact GRC9v3 compatibility reduction.",
            "",
            "## Claim Ceiling",
            "",
            "D10.1 supports only a preliminary provenance separation, the five bounded findings above, and a working factorization hypothesis. It does not prove intrinsic nine-port necessity, prove that nine ports are unnecessary, promote A or C from the GRC9 lineage to GRCv4, complete the pre-closure audit, close final substrate identity, or change D10 authorization.",
            "",
            "## Disposition",
            "",
            "```text",
            f"record = {data['record_id']}",
            f"status = {data['status']}",
            f"decision_record_digest = {data['decision_record_digest']}",
            "scientific_disposition = accepted_preliminary_bounded_substrate_provenance_separation",
            f"human_acceptance = {data['human_acceptance']}",
            "D10_claim_topology_unchanged = true",
            "promotion_proved = false",
            "final_substrate_identity_closed = false",
            "preclosure_substrate_provenance_audit_still_required = true",
            "GRCV4_specification_authorized = false",
            "implementation_authorized = false",
            "runtime_or_src_changed = false",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


OUTPUT_MD.write_text(render_markdown(record))
