#!/usr/bin/env python3
"""Audit the full GRCV4/GRC9V4 D10.2 substrate-provenance record."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
DECISIONS = ROOT / "implementation/investigations/grc9v4-constitutive-design/decisions"
RECORD_PATH = DECISIONS / "D10_2FullSubstrateProvenanceAndPromotionAudit.json"
REPORT_PATH = DECISIONS / "D10_2FullSubstrateProvenanceAndPromotionAudit.md"
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


record = json.loads(RECORD_PATH.read_text())
report = REPORT_PATH.read_text()
d10 = json.loads(D10_PATH.read_text())
d10_1 = json.loads(D10_1_PATH.read_text())
d10_claim_topology = json.loads(D10_CLAIM_PATH.read_text())
d10_authorization = json.loads(D10_AUTHORIZATION_PATH.read_text())
checks: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    checks.append((name, bool(condition)))


check(
    "record_digest",
    record["decision_record_digest"]
    == canonical_digest(record, "decision_record_digest"),
)
check("status_accepted_bounded", record["status"] == "accepted_bounded")
check(
    "human_acceptance_recorded",
    record["human_acceptance"] == "accepted_bounded_2026-08-26",
)
check(
    "D10_digest_canonical",
    d10["decision_record_digest"]
    == canonical_digest(d10, "decision_record_digest"),
)
check(
    "D10_1_digest_canonical",
    d10_1["decision_record_digest"]
    == canonical_digest(d10_1, "decision_record_digest"),
)
check(
    "accepted_D10_1_predecessor",
    d10_1["status"]
    == "accepted_preliminary_bounded_substrate_provenance_separation"
    and record["predecessor_decision_digest"] == d10_1["decision_record_digest"],
)
check(
    "accepted_D10_bound",
    record["accepted_D10_decision_digest"] == d10["decision_record_digest"],
)

sources = record["source_identities"]
source_ids = {row["source_id"] for row in sources}
check("source_count_36", len(sources) == 36)
check("source_ids_unique", len(source_ids) == len(sources))
for row in sources:
    path = ROOT / row["path"]
    check(f"source_exists:{row['source_id']}", path.is_file())
    check(f"source_repo_relative:{row['source_id']}", not Path(row["path"]).is_absolute())
    check(f"source_SHA:{row['source_id']}", row["file_sha256"] == file_sha(path))
    if "source_digest" in row:
        data = json.loads(path.read_text())
        digest_field = (
            "decision_record_digest"
            if "decision_record_digest" in data
            else "artifact_digest"
        )
        check(
            f"source_digest:{row['source_id']}",
            row["source_digest"]
            == data[digest_field]
            == canonical_digest(data, digest_field),
        )

schema = record["classification_schema"]
check("audit_tuple_exact", schema["required_tuple"] == ["E", "P_E", "L_E", "S_E"])
check(
    "substrate_dispositions_exact",
    set(schema["substrate_dispositions"])
    == {
        "core_theory_substrate_independent",
        "substrate_independent_specification_meta",
        "GRC_derived",
        "GRC9V3_derived_GRC_rederivation_required",
        "GRC9_specialization_specific",
        "GRC9_intrinsic",
    },
)
check(
    "promotion_statuses_exact",
    set(schema["promotion_statuses"])
    == {"promotion_proved", "promotion_pending", "specialization_only"},
)
check(
    "decisive_deletion_test_frozen",
    schema["decisive_test"]
    == "delete_the_premise_this_came_from_GRC9V3_and_require_an_independent_derivation_from_GRCV3_or_general_GRC_contracts",
)

rows = record["normatively_load_bearing_objects"]
row_ids = {row["object_id"] for row in rows}
required_row_fields = {
    "object_id",
    "family",
    "object_kind",
    "normative_object",
    "premises_used",
    "source_lineage",
    "substrate_disposition",
    "promotion_status",
    "independent_derivation_ids",
    "GRC9V3_premise_deletion_test",
    "conclusion",
    "specification_destination",
    "blocked_overread",
}
check("object_count_67", len(rows) == 67)
check("object_ids_unique", len(row_ids) == len(rows))
check("all_object_fields_present", all(required_row_fields <= set(row) for row in rows))
check("all_object_source_lineage_resolves", all(set(row["source_lineage"]) <= source_ids for row in rows))
check("no_empty_object_premises", all(row["premises_used"] for row in rows))
check("no_empty_object_lineage", all(row["source_lineage"] for row in rows))
check("no_empty_object_conclusions", all(row["conclusion"] for row in rows))
check("all_object_dispositions_valid", all(row["substrate_disposition"] in schema["substrate_dispositions"] for row in rows))
check("all_object_promotions_valid", all(row["promotion_status"] in schema["promotion_statuses"] for row in rows))

required_families = {
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
family_counts = Counter(row["family"] for row in rows)
check("family_counts_exact", dict(family_counts) == required_families)
check("coverage_contract_exact", record["coverage_contract"]["required_families"] == required_families)
check("coverage_passed", record["coverage_contract"]["all_required_families_exactly_covered"] is True)

claim_topology = json.loads((DECISIONS / "D10NormativeClaimTopology.json").read_text())
accepted_claim_ids = {row["claim_id"] for row in claim_topology["claims"]}
claim_coverage = record["D10_claim_coverage"]
claim_map = claim_coverage["claim_to_object_ids"]
check("accepted_claim_count_39", len(accepted_claim_ids) == 39)
decision_claim_ids = {
    claim_id
    for claim_class in ["normative", "optional", "conditional", "open", "negative"]
    for claim_id in d10["decision"]["claim_topology"][claim_class]
}
authorization_claim_ids = {
    claim_id
    for field in [
        "normative_common_claim_ids",
        "optional_profile_claim_ids",
        "conditional_claim_ids",
        "open_claim_ids",
        "negative_claim_ids",
    ]
    for claim_id in d10_authorization[field]
}
check(
    "accepted_D10_claim_surfaces_exact",
    decision_claim_ids == accepted_claim_ids == authorization_claim_ids,
)
check("C012_is_accepted_D10_claim", "D10-CL-C-012" in accepted_claim_ids)
claim_identity = record["accepted_D10_claim_set_identity"]
check(
    "recorded_claim_identity_exact",
    set(claim_identity["decision_claim_ids"])
    == set(claim_identity["topology_claim_ids"])
    == set(claim_identity["authorization_claim_ids"])
    == accepted_claim_ids
    and claim_identity["claim_count"] == 39
    and claim_identity["claim_class_counts"]
    == {"normative": 9, "optional": 7, "conditional": 12, "open": 5, "negative": 6}
    and claim_identity["all_three_surfaces_exactly_equal"] is True
    and claim_identity["D10_CL_C_012_is_accepted"] is True,
)
check("claim_coverage_keys_exact", set(claim_map) == accepted_claim_ids)
check("claim_coverage_values_resolve", all(set(object_ids) <= row_ids for object_ids in claim_map.values()))
check("no_empty_claim_coverage", all(object_ids for object_ids in claim_map.values()))
check("all_objects_bear_on_claim", {object_id for object_ids in claim_map.values() for object_id in object_ids} == row_ids)
check("C011_covers_full_audit_population", set(claim_map["D10-CL-C-011"]) == row_ids)
check("claim_coverage_flags_true", claim_coverage["all_accepted_claims_covered"] is True and claim_coverage["all_normative_objects_bear_on_at_least_one_claim"] is True)

derivations = record["independent_GRC_derivations"]
derivation_ids = {row["derivation_id"] for row in derivations}
required_derivation_fields = {
    "derivation_id",
    "title",
    "source_premises",
    "construction",
    "conclusion",
    "applies_to",
    "blocked_overread",
}
check("derivation_count_12", len(derivations) == 12)
check("derivation_ids_unique", len(derivation_ids) == len(derivations))
check("all_derivation_fields_present", all(required_derivation_fields <= set(row) for row in derivations))
check("all_derivation_sources_resolve", all(set(row["source_premises"]) <= source_ids for row in derivations))
check("all_derivation_targets_resolve", all(set(row["applies_to"]) <= row_ids for row in derivations))
check("all_derivation_constructions_nonempty", all(row["construction"] for row in derivations))
check("all_row_derivation_refs_resolve", all(set(row["independent_derivation_ids"]) <= derivation_ids for row in rows))

equation_rows = record["normative_equation_contract_registry"]
equation_ids = [row["equation_contract_id"] for row in equation_rows]
equation_by_id = {row["equation_contract_id"]: row for row in equation_rows}
required_equation_fields = {
    "equation_contract_id",
    "contract_scope",
    "parent_object_ids",
    "accepted_claim_ids",
    "profile_ids",
    "normative_equation_or_contract",
    "premises_used",
    "source_lineage",
    "substrate_disposition",
    "promotion_status",
    "independent_derivation_ids",
    "GRC9V3_premise_deletion_test",
    "specification_destination",
    "blocked_overread",
}
check("equation_contract_count_152", len(equation_rows) == 152)
check("equation_contract_ids_unique", len(equation_ids) == len(set(equation_ids)))
check("equation_contract_fields_complete", all(required_equation_fields <= set(row) for row in equation_rows))
check("equation_parent_refs_resolve", all(set(row["parent_object_ids"]) <= row_ids and row["parent_object_ids"] for row in equation_rows))
check("equation_claim_refs_resolve", all(set(row["accepted_claim_ids"]) <= accepted_claim_ids and row["accepted_claim_ids"] for row in equation_rows))
check("equation_source_refs_resolve", all(set(row["source_lineage"]) <= source_ids and row["source_lineage"] for row in equation_rows))
check("equation_derivation_refs_resolve", all(set(row["independent_derivation_ids"]) <= derivation_ids for row in equation_rows))
check("equation_contract_text_nonempty", all(row["normative_equation_or_contract"] and row["blocked_overread"] for row in equation_rows))
check("equation_dispositions_valid", all(row["substrate_disposition"] in schema["substrate_dispositions"] for row in equation_rows))
check("equation_promotions_valid", all(row["promotion_status"] in schema["promotion_statuses"] for row in equation_rows))

parent_equation_rows = [row for row in equation_rows if row["contract_scope"] == "parent_atomic_contract"]
explicit_equation_rows = [row for row in equation_rows if row["contract_scope"] != "parent_atomic_contract"]
check("parent_atomic_contract_count_67", len(parent_equation_rows) == 67)
check("explicit_equation_contract_count_85", len(explicit_equation_rows) == 85)
check(
    "one_parent_atomic_contract_per_object",
    Counter(row["parent_object_ids"][0] for row in parent_equation_rows)
    == Counter({object_id: 1 for object_id in row_ids}),
)
check(
    "parent_atomic_claim_links_match_object_coverage",
    all(
        set(row["accepted_claim_ids"])
        == {claim_id for claim_id, object_ids in claim_map.items() if row["parent_object_ids"][0] in object_ids}
        for row in parent_equation_rows
    ),
)
check(
    "all_parents_covered_by_equation_registry",
    {object_id for row in equation_rows for object_id in row["parent_object_ids"]}
    == row_ids,
)
check(
    "all_claims_covered_by_equation_registry",
    {claim_id for row in equation_rows for claim_id in row["accepted_claim_ids"]}
    == accepted_claim_ids,
)

equation_coverage = record["equation_contract_coverage"]
expected_scope_counts = {
    "candidate_C_chain": 5,
    "candidate_specific_CI": 5,
    "candidate_specific_CI_PC": 6,
    "charge_budget_stage": 1,
    "charge_projector": 2,
    "charge_tangent": 2,
    "operator_split": 5,
    "parent_atomic_contract": 67,
    "persistent_carrier": 4,
    "profile_scoped_disabled_reduction": 40,
    "reconstructed_geometry": 4,
    "structural_geometry": 5,
    "typed_topology_event": 6,
}
check("equation_scope_counts_exact", equation_coverage["contract_scope_counts"] == expected_scope_counts)
check(
    "equation_coverage_summary_exact",
    equation_coverage["parent_atomic_contract_count"] == 67
    and equation_coverage["explicit_equation_contract_count"] == 85
    and equation_coverage["equation_contract_count"] == 152
    and equation_coverage["equation_contract_ids_unique"] is True
    and equation_coverage["all_parent_objects_covered"] is True
    and equation_coverage["all_accepted_claims_covered"] is True
    and equation_coverage["promotion_pending_contract_count"] == 0,
)

disabled_rows = [row for row in equation_rows if row["contract_scope"] == "profile_scoped_disabled_reduction"]
expected_profiles = {
    "A_CI", "C_CI", "A_OS", "C_OS", "A_RG2b", "C_RG2b",
    "A_PC", "C_PC", "A_CI_PC", "C_CI_PC",
}
expected_surfaces = {"TRANSITION", "STATE", "OBSERVABLE", "LIFECYCLE"}
observed_disabled_pairs = {
    (row["profile_ids"][0], row["equation_contract_id"].rsplit("-", 1)[-1])
    for row in disabled_rows
}
check("disabled_reduction_matrix_10_by_4", len(disabled_rows) == 40 and observed_disabled_pairs == {(profile, surface) for profile in expected_profiles for surface in expected_surfaces})
check("disabled_rows_only_cover_N007", all(row["accepted_claim_ids"] == ["D10-CL-N-007"] for row in disabled_rows))

required_explicit_ids = {
    "D10.2-EC-CHARGE-DQ",
    "D10.2-EC-CHARGE-TANGENT",
    "D10.2-EC-CHARGE-C-SECTOR-PROJECTOR",
    "D10.2-EC-CHARGE-FULL-TANGENT-RETRACTION",
    "D10.2-EC-CHARGE-BUDGET-STAGE",
    "D10.2-EC-CI-A-ROOT",
    "D10.2-EC-CI-C-ROOT-SELECTION",
    "D10.2-EC-CI-PC-A-COMPOSITION",
    "D10.2-EC-CI-PC-C-ROOT-SELECTION",
    "D10.2-EC-PC-ZOH-WRITER",
    "D10.2-EC-PC-RELEASE",
    "D10.2-EC-OS-STAGE-ORDER",
    "D10.2-EC-OS-SPLIT-RESIDUAL",
    "D10.2-EC-RG-INVARIANCE",
    "D10.2-EC-RG-LIPSCHITZ-CONTRACTION",
    "D10.2-EC-C-HODGE-LAPLACIAN",
    "D10.2-EC-C-RESOLVENT",
    "D10.2-EC-C-READBACK",
    "D10.2-EC-GEOM-K4-ASSEMBLY",
    "D10.2-EC-GEOM-PROFILE",
    "D10.2-EC-EVENT-RESOURCE",
    "D10.2-EC-EVENT-K4-HISTORY",
    "D10.2-EC-EVENT-LIFECYCLE-TUPLE",
}
check("required_explicit_equation_contracts_present", required_explicit_ids <= set(equation_ids))
check("no_equation_promotion_pending", not any(row["promotion_status"] == "promotion_pending" for row in equation_rows))
event_resource = equation_by_id["D10.2-EC-EVENT-RESOURCE"]
event_resource_text = event_resource["normative_equation_or_contract"]
check(
    "event_resource_preserves_D9_transport_increment_split",
    all(
        token in event_resource_text
        for token in [
            "C_plus = T_C_evt*C_minus + Delta_C_event",
            "varpi_plus^T*T_C_evt = varpi_minus^T",
            "Delta_Q_event = varpi_plus^T*C_plus - varpi_minus^T*C_minus",
            "Q_target_plus = Q_target_minus + Delta_Q_event = varpi_plus^T*C_plus",
        ]
    ),
)
check(
    "event_resource_receipt_does_not_replace_coordinate_increment",
    "cannot_replace_Delta_C_event" in event_resource["blocked_overread"]
    and set(event_resource["accepted_claim_ids"])
    == {"D10-CL-N-004", "D10-CL-N-005", "D10-CL-X-001"},
)
budget_stage = equation_by_id["D10.2-EC-CHARGE-BUDGET-STAGE"]
budget_stage_text = budget_stage["normative_equation_or_contract"]
check(
    "charge_budget_stage_distinguishes_ordinary_and_event_targets",
    all(
        token in budget_stage_text
        for token in [
            "ordinary_complete_step: Q_varpi(C_next) = Q_target_next",
            "Q_target_next = Q_target_current + Delta_Q_step",
            "current_bounded_population_Delta_Q_step = 0",
            "topology_event_jump: Q_target_plus = Q_target_minus + Delta_Q_event",
        ]
    ),
)
check(
    "charge_budget_stage_blocks_event_double_count",
    "double_count_event_Delta_Q" in budget_stage["blocked_overread"]
    and set(budget_stage["parent_object_ids"])
    == {"CORE-GENERAL-CHARGE", "L-CONTINUITY-WRITE", "L-TOPOLOGY-EVENT"},
)

derivation_by_id = {row["derivation_id"]: row for row in derivations}
a_gw_derivation_text = " ".join(
    derivation_by_id["D10.2-DER-A-GW"]["construction"]
)
geometry_derivation_text = " ".join(
    derivation_by_id["D10.2-DER-GEOMETRY"]["construction"]
)
differential_derivation_text = " ".join(
    derivation_by_id["D10.2-DER-DIFFERENTIAL"]["construction"]
)
check(
    "A_derivation_promotes_exact_D7_formula",
    "gamma*J_e^2/2" in a_gw_derivation_text
    and "delta*Ric" not in a_gw_derivation_text
    and "curvature disabled" in a_gw_derivation_text,
)
check(
    "geometry_derivation_constructs_reference_Hodge",
    all(
        token in geometry_derivation_text
        for token in [
            "H0_ref = diag(mu)",
            "H1_form_ref = diag(W_ref)",
            "G_J_ref = diag(W_ref^-1)",
            "G_J(h) = H1_form(h)^-1",
        ]
    ),
)
check(
    "geometry_derivation_does_not_construct_M4",
    "M4 is not constructed by this geometry map" in geometry_derivation_text,
)
check(
    "differential_contract_keeps_equivalent_backends_open",
    "equivalent documented and serialized backend" in differential_derivation_text
    and "not frozen as a theorem" in differential_derivation_text,
)

general_rows = [
    row
    for row in rows
    if row["substrate_disposition"]
    in {
        "core_theory_substrate_independent",
        "substrate_independent_specification_meta",
        "GRC_derived",
    }
]
specialization_rows = [
    row
    for row in rows
    if row["substrate_disposition"]
    in {"GRC9_specialization_specific", "GRC9_intrinsic"}
]
pending_rows = [row for row in rows if row["promotion_status"] == "promotion_pending"]
check("all_general_rows_promotion_proved", all(row["promotion_status"] == "promotion_proved" for row in general_rows))
check("all_general_rows_have_derivations", all(row["independent_derivation_ids"] for row in general_rows))
check("all_general_rows_survive_deletion", all(row["GRC9V3_premise_deletion_test"] in {"survives_from_GRC_premises", "survives_without_any_GRC9V3_premise"} for row in general_rows))
check("all_specialization_rows_specialization_only", all(row["promotion_status"] == "specialization_only" for row in specialization_rows))
check("specialization_rows_have_no_fake_GRC_derivation", all(not row["independent_derivation_ids"] for row in specialization_rows))
check("promotion_pending_rows_zero", not pending_rows)
check("rederivation_required_rows_zero", not any(row["substrate_disposition"] == "GRC9V3_derived_GRC_rederivation_required" for row in rows))
check(
    "object_disposition_counts_exact",
    Counter(row["substrate_disposition"] for row in rows)
    == {
        "GRC_derived": 45,
        "core_theory_substrate_independent": 1,
        "substrate_independent_specification_meta": 8,
        "GRC9_specialization_specific": 5,
        "GRC9_intrinsic": 8,
    },
)

by_id = {row["object_id"]: row for row in rows}
check("A_GW_promoted", by_id["A-GW-FUNCTIONAL"]["substrate_disposition"] == "GRC_derived" and by_id["A-GW-FUNCTIONAL"]["promotion_status"] == "promotion_proved")
check("A_GW_is_curvature_disabled", "curvature_disabled" in by_id["A-GW-FUNCTIONAL"]["normative_object"] and "curvature_conditioned_successor" in by_id["A-GW-FUNCTIONAL"]["blocked_overread"])
check("GRC9_row_backend_intrinsic", by_id["BASE-GRC9-ROW-BASIS-DIFFERENTIAL"]["substrate_disposition"] == "GRC9_intrinsic" and by_id["BASE-GRC9-ROW-BASIS-DIFFERENTIAL"]["promotion_status"] == "specialization_only")
check("disabled_transition_specialization_specific", by_id["BASE-DISABLED-TRANSITION"]["substrate_disposition"] == "GRC9_specialization_specific")
check("disabled_state_specialization_specific", by_id["BASE-DISABLED-STATE"]["substrate_disposition"] == "GRC9_specialization_specific")
check("disabled_observable_specialization_specific", by_id["BASE-DISABLED-OBSERVABLE"]["substrate_disposition"] == "GRC9_specialization_specific")
check("disabled_lifecycle_specialization_specific", by_id["BASE-DISABLED-LIFECYCLE"]["substrate_disposition"] == "GRC9_specialization_specific")
check("general_charge_promoted", by_id["CORE-GENERAL-CHARGE"]["substrate_disposition"] == "GRC_derived")
check("charge_tangent_promoted", by_id["CORE-CHARGE-TANGENT"]["substrate_disposition"] == "GRC_derived" and "V_Q_varpi" in by_id["CORE-CHARGE-TANGENT"]["normative_object"])
check("structural_projector_promoted_bounded", by_id["CORE-STRUCTURAL-CHARGE-PROJECTOR"]["substrate_disposition"] == "GRC_derived" and "not_a_full_state_orthogonal_projector" in by_id["CORE-STRUCTURAL-CHARGE-PROJECTOR"]["blocked_overread"])
check("unit_charge_scoped_to_reference", by_id["CORE-UNIT-MEASURE"]["specification_destination"] == "GRCV4_reference_profile")
check("C_sector_promoted_but_derived", by_id["C-SECTOR"]["substrate_disposition"] == "GRC_derived" and "T_C_is_not_independent" in by_id["C-SECTOR"]["blocked_overread"])
check("core_K_role_is_theory_independent", by_id["CORE-K-STRUCTURAL-ROLE"]["substrate_disposition"] == "core_theory_substrate_independent" and "core_K_is_not" in by_id["CORE-K-STRUCTURAL-ROLE"]["blocked_overread"])
check("graph_K4_is_GRC_derived", by_id["GEOM-K4"]["substrate_disposition"] == "GRC_derived" and "symmetric_bilinear_form" in by_id["GEOM-K4"]["normative_object"])
check("Hodge_reference_is_explicit_GRC_embedding", all(token in by_id["GEOM-H1-FORM"]["normative_object"] for token in ["H0_ref_equals_diag_mu", "H1_form_ref_equals_diag_W_ref", "GJ_ref_equals_diag_W_ref_inverse"]))
check("GJ_is_flat_not_mobility", "j_struct_flat_equals_G_J_j_flux" in by_id["GEOM-GJ"]["normative_object"] and "not_transport_mobility_M4" in by_id["GEOM-GJ"]["blocked_overread"])
check("M4_is_transport_not_assembly", by_id["GEOM-M4"]["object_kind"] == "transport_mobility_operator" and "candidate_specific_transport_mobility" in by_id["GEOM-M4"]["normative_object"] and "not_overlap_assembly" in by_id["GEOM-M4"]["blocked_overread"])
check("assembly_belongs_to_K4", "K4_graph_restrictions_use_overlap_normalized_assembly" in by_id["GEOM-ASSEMBLY"]["normative_object"] and "not_M4" in by_id["GEOM-ASSEMBLY"]["blocked_overread"])
check("A_state_reduction_excludes_specialization_projection", "disabled" not in by_id["A-STATE-REDUCTION"]["normative_object"] and "specialization_compatibility_rows" in by_id["A-STATE-REDUCTION"]["blocked_overread"])
check("generic_migration_excludes_initializer", "migration_grammar" == by_id["L-PROFILE-MIGRATION"]["object_kind"] and "does_not_select_a_target_initializer" in by_id["L-PROFILE-MIGRATION"]["blocked_overread"])
check("GRC_A_initializer_promoted", by_id["L-A-INITIALIZER-GRC"]["substrate_disposition"] == "GRC_derived" and by_id["L-A-INITIALIZER-GRC"]["promotion_status"] == "promotion_proved")
check("GRC9V3_A_initializer_specialization_specific", by_id["L-A-INITIALIZER-GRC9V3"]["substrate_disposition"] == "GRC9_specialization_specific" and by_id["L-A-INITIALIZER-GRC9V3"]["promotion_status"] == "specialization_only" and not by_id["L-A-INITIALIZER-GRC9V3"]["independent_derivation_ids"])
check("specification_meta_is_not_core_theory", all(by_id[object_id]["substrate_disposition"] == "substrate_independent_specification_meta" for object_id in ["L-PROFILE-GRAMMAR", "SPEC-PROFILE-GRAMMAR", "SPEC-FUTURE-ADMISSION", "SPEC-B-SLOT", "SPEC-CLAIM-CEILINGS", "SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER", "SPEC-COMPOSITION-PROFILE-IDENTITY", "SPEC-VERIFICATION-REGISTRY"]))
check("common_destinations_are_current_scoped", all("GRCV4_common" not in row["specification_destination"] for row in rows) and all("current_promoted_common" in row["specification_destination"] for row in rows if "common" in row["specification_destination"]))
for object_id in ["REAL-CI", "REAL-OS", "REAL-RG2B", "REAL-PC", "REAL-CI-PC"]:
    check(f"realization_promoted:{object_id}", by_id[object_id]["substrate_disposition"] == "GRC_derived" and by_id[object_id]["promotion_status"] == "promotion_proved")
for object_id in [
    "GRC9-ORDERED-PORTS",
    "GRC9-ROW-COLUMN-CHART",
    "GRC9-SATURATION",
    "GRC9-MECHANICAL-EXPANSION",
    "GRC9-HYBRID-SPARK",
    "GRC9-CHILD-BASIN-STABILIZATION",
    "GRC9-COLUMN-COARSE-GRAINING",
]:
    check(f"GRC9_intrinsic:{object_id}", by_id[object_id]["substrate_disposition"] == "GRC9_intrinsic" and by_id[object_id]["GRC9V3_premise_deletion_test"] == "fails_without_nine_port_substrate")

promotion = record["promotion_result"]
check("factorization_exact", promotion["factorization"] == "GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3")
check("factorization_earned", promotion["factorization_earned"] is True)
check("factorization_scope_bounded", promotion["scope"] == "current_D10_initial_specification_population_only")
check("all_rederivations_complete", promotion["all_required_GRC_rederivations_complete"] is True)
check("pending_list_empty", promotion["GRC9V3_derived_GRC_rederivation_pending_rows"] == [])
check("GRCV4_population_exact", set(promotion["GRCV4_object_ids"]) == {row["object_id"] for row in general_rows})
check("GRC9V4_specialization_exact", set(promotion["GRC9V4_specialization_object_ids"]) == {row["object_id"] for row in specialization_rows})

claim_effect = record["claim_topology_effect"]
check("accepted_D10_not_rewritten", claim_effect["accepted_D10_claim_topology_rewritten"] is False)
check("D10_C011_named_successor", claim_effect["D10_conditional_claim_D10_CL_C_011"] == "succeeded_by_accepted_D10_2_CL_N_001")
check("preclosure_obligation_resolved", claim_effect["D10_preclosure_obligation"] == "resolved_by_accepted_D10_2")

route = record["specification_route"]
check("GRCV4_spec_after_acceptance", route["GRCV4_specification_authorized_after_human_acceptance"] is True)
check("GRC9V4_spec_after_acceptance", route["GRC9V4_specialization_specification_authorized_after_human_acceptance"] is True)
check(
    "specification_route_open_now",
    route["current_status"] == "accepted_D10_2_specification_route_open"
    and route["GRCV4_specification_authorized_now"] is True
    and route["GRC9V4_specialization_specification_authorized_now"] is True
    and route["authorized_next_actions"]
    == [
        "write_GRCV4_normative_specification_from_the_promoted_general_contract",
        "write_GRC9V4_as_the_substantive_nine_port_specialization_with_exact_GRC9V3_disabled_compatibility",
    ],
)
check("no_spec_written", route["normative_spec_files_written_by_D10_2"] is False)
check("implementation_not_authorized", route["implementation_authorized"] is False and route["implementation_plan_authorized"] is False)
check("runtime_unchanged", route["runtime_or_src_changed"] is False)

hardening = record["targeted_type_and_provenance_hardening"]
check(
    "hardening_contract_complete",
    set(hardening)
    == {
        "core_K_vs_graph_K4",
        "M4_ontology",
        "Candidate_A_profile_scope",
        "Candidate_A_future_curvature_rule",
        "migration_split",
        "reference_Hodge_embedding",
        "differential_backend_scope",
        "destination_semantics",
    },
)

decision = record["decision"]
check("current_population_identity_closed", decision["final_substrate_identity_closed_for_current_population"] is True)
check("future_identity_not_globally_closed", decision["final_substrate_identity_globally_closed_for_all_future_profiles"] is False)
check("A_promotion_proved", decision["Candidate_A_GRC_promotion"].startswith("proved_with_general_GRC"))
check("C_promotion_proved", decision["Candidate_C_GRC_promotion"].startswith("proved_from_general_graph_Hodge"))
check("D11_not_authorized", decision["D11_authorized"] is False)

check("control_count_48", len(record["controls"]) == 48 == len(set(record["controls"])))
check("report_has_digest", record["decision_record_digest"] in report)
check("report_has_accepted_status", "**Status:** Accepted bounded" in report and "status = accepted_bounded" in report)
check("report_has_factorization", "GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3" in report)
check("report_says_factorization_earned", "factorization_disposition = earned_bounded_for_current_D10_initial_specification_population" in report)
check("report_explains_A_backend_split", "fixed GRC9 row-basis differential backend and exact GRC9v3 initializer binding remain specialization content" in report)
check("report_explains_type_hardening", "Core `K -> g[K]` is a substrate-independent theory role" in report and "`M4` remains separately owned" in report)
check("report_keeps_future_scope_open", "Future constitutive, realization, hybrid, geometry, or lifecycle profiles must reopen provenance" in report)
check("report_has_39_claim_identity", "accepted_D10_claims = 39" in report and "D10-CL-C-012" in report)
check("report_has_equation_registry", "normative_equation_contracts = 152" in report and "explicit_equation_contracts = 85" in report)
check("report_has_disabled_matrix", "disabled_reduction_matrix = 10 profiles x 4 surfaces = 40 contracts" in report)
check("no_absolute_paths_in_record", "/home/" not in json.dumps(record) and "Documents/RC-github" not in json.dumps(record))

failed = [name for name, passed in checks if not passed]
print(f"D10.2 audit: {len(checks) - len(failed)}/{len(checks)} checks passed")
if failed:
    for name in failed:
        print(f"FAIL {name}")
    raise SystemExit(1)
