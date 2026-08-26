#!/usr/bin/env python3
"""Audit the emitted GRC9V4 D10 claim-topology synthesis."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
DECISIONS = ROOT / "implementation/investigations/grc9v4-constitutive-design/decisions"


def load(name: str) -> dict[str, Any]:
    return json.loads((DECISIONS / name).read_text())


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


checks: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append((name, bool(condition), detail))


topology = load("D10NormativeClaimTopology.json")
debt = load("D10DebtClaimTransformationLedger.json")
profile = load("D10SpecificationAuthorizationProfile.json")
decision = load("D10DesignSynthesisAndSpecWritingDecision.json")
d9 = load("D9ResidualDebtLedger.json")
d0 = load("D0TargetInheritanceAndClaimCeiling.json")
d1 = load("D1RetainedRepresentationOntologyAndCandidateAdmission.json")
d7g = load("D7Gv2GeometryParametricClosureAndFinalization.json")
comp = load("GeometryTemporalRealizationComparativeSynthesis.json")
pc = load("GeometryTemporalRealizationSuccessorPersistentCarrier.json")
decision_report = (
    DECISIONS / "D10DesignSynthesisAndSpecWritingDecision.md"
).read_text()

for name, data, field in (
    ("topology", topology, "artifact_digest"),
    ("debt", debt, "artifact_digest"),
    ("profile", profile, "artifact_digest"),
    ("decision", decision, "decision_record_digest"),
):
    check(
        f"{name}_canonical_digest",
        data[field] == canonical_digest(data, field),
        f"{data[field]} / {canonical_digest(data, field)}",
    )

manifest_by_path = {row["path"]: row for row in decision["artifact_manifest"]}
check("supporting_artifact_count", len(manifest_by_path) == 3)
for path_text, row in manifest_by_path.items():
    path = ROOT / path_text
    data = json.loads(path.read_text())
    check(f"manifest_path_exists:{path.name}", path.is_file())
    check(
        f"manifest_digest:{path.name}",
        row["artifact_digest"] == data["artifact_digest"],
    )
    check(f"manifest_SHA:{path.name}", row["file_sha256"] == file_sha(path))
    check(f"manifest_repo_relative:{path.name}", not Path(path_text).is_absolute())

sources = decision["source_identities"]
check("accepted_source_count", len(sources) == 27)
check("source_ids_unique", len({row["source_id"] for row in sources}) == 27)
for row in sources:
    path = ROOT / row["path"]
    data = json.loads(path.read_text())
    digest_field = (
        "decision_record_digest"
        if "decision_record_digest" in data
        else "artifact_digest"
    )
    check(f"source_exists:{row['source_id']}", path.is_file())
    check(
        f"source_digest:{row['source_id']}",
        row["source_digest"] == data[digest_field],
    )
    check(
        f"source_digest_canonical:{row['source_id']}",
        row["source_digest"] == canonical_digest(data, digest_field),
    )
    check(f"source_SHA:{row['source_id']}", row["file_sha256"] == file_sha(path))
    check(
        f"source_repo_relative:{row['source_id']}", not Path(row["path"]).is_absolute()
    )

claims = topology["claims"]
claim_ids = [row["claim_id"] for row in claims]
claim_by_id = {row["claim_id"]: row for row in claims}
historical_claims = topology["historical_claim_nodes"]
historical_claim_ids = [row["claim_id"] for row in historical_claims]
historical_by_id = {row["claim_id"]: row for row in historical_claims}
all_claim_ids = set(claim_ids) | set(historical_claim_ids)
categories = topology["claim_categories"]
expected_classes = {"normative", "optional", "conditional", "open", "negative"}
check("claim_count_39", len(claims) == topology["claim_count"] == 39)
check("claim_ids_unique", len(set(claim_ids)) == 39)
check(
    "historical_claim_count_29",
    len(historical_claims) == topology["historical_claim_count"] == 29,
)
check("historical_claim_ids_unique", len(set(historical_claim_ids)) == 29)
check("current_and_historical_claim_ids_disjoint", len(all_claim_ids) == 68)
check("total_claim_node_count_68", topology["total_claim_node_count"] == 68)
check("claim_classes_exact", set(categories) == expected_classes)
check(
    "claim_category_partition",
    set().union(*map(set, categories.values())) == set(claim_ids)
    and sum(map(len, categories.values())) == len(claims),
)
check(
    "claim_category_membership_matches_rows",
    all(row["claim_id"] in categories[row["claim_class"]] for row in claims),
)
check(
    "claim_category_counts",
    topology["category_counts"]
    == {name: len(categories[name]) for name in expected_classes},
)
check("normative_count_9", len(categories["normative"]) == 9)
check("optional_count_7", len(categories["optional"]) == 7)
check("conditional_count_12", len(categories["conditional"]) == 12)
check("open_count_5", len(categories["open"]) == 5)
check("negative_count_6", len(categories["negative"]) == 6)

d9_carried = {
    row["debt_id"]
    for row in d9["predecessor_dispositions"]
    if row["status"] == "carried"
}
debt_rows = debt["debt_transformations"]
debt_ids = [row["debt_id"] for row in debt_rows]
debt_by_id = {row["debt_id"]: row for row in debt_rows}
check("D9_carried_count_29", len(d9_carried) == 29)
check("D10_debt_count_29", len(debt_rows) == debt["debt_count"] == 29)
check("debt_ids_unique", len(set(debt_ids)) == 29)
check("D10_debts_equal_D9_union", set(debt_ids) == d9_carried)
check(
    "all_debts_have_claim_dispositions",
    all(
        row["blocked_claim_id"] in all_claim_ids
        and row["supported_claim_id"] in all_claim_ids
        and row["successor_claim_ids"]
        and set(row["successor_claim_ids"]) <= set(claim_ids)
        for row in debt_rows
    ),
)
typed_claim_fields = (
    "predecessor_claim_ids",
    "blocked_claim_ids",
    "supported_claim_ids",
    "conditioned_claim_ids",
    "negative_successor_claim_ids",
    "routed_claim_ids",
    "successor_claim_ids",
)
check(
    "all_debts_have_typed_claim_fields",
    all(all(field in row for field in typed_claim_fields) for row in debt_rows),
)
check(
    "all_typed_debt_claim_refs_exist",
    all(
        set().union(*(set(row[field]) for field in typed_claim_fields)) <= all_claim_ids
        for row in debt_rows
    ),
)
check(
    "blocked_by_temporal_direction_is_valid",
    all(
        all(
            claim_id in historical_by_id
            or claim_by_id[claim_id]["claim_class"] in {"conditional", "open"}
            for claim_id in row["blocked_claim_ids"]
        )
        for row in debt_rows
    ),
)
allowed_transformations = set(debt["allowed_transformations"])
check("binary_resolved_forbidden", "resolved" not in allowed_transformations)
check(
    "all_transformations_typed",
    all(row["transformation"] in allowed_transformations for row in debt_rows),
)
check(
    "no_claimless_debt_disposition",
    debt["claimless_debt_disposition_count"] == 0,
)

bearing_debts = {item for row in claims for item in row["bearing_debt_ids"]}
check("all_debts_traced_from_claims", bearing_debts == set(debt_ids))
check(
    "all_normative_claim_debt_refs_valid",
    all(
        set(claim_by_id[claim_id]["bearing_debt_ids"]) <= set(debt_ids)
        for claim_id in categories["normative"]
    ),
)
check(
    "all_claim_evidence_nonempty",
    all(row["evidence_refs"] for row in claims),
)

for row in historical_claims:
    check(
        f"historical_claim_debt_exists:{row['claim_id']}",
        row["transformed_by_debt_id"] in debt_by_id,
    )
    check(
        f"historical_claim_predecessor_reciprocal:{row['claim_id']}",
        row["claim_id"]
        in debt_by_id[row["transformed_by_debt_id"]]["predecessor_claim_ids"],
    )
    check(
        f"historical_claim_successors_exact:{row['claim_id']}",
        row["successor_claim_ids"]
        == debt_by_id[row["transformed_by_debt_id"]]["successor_claim_ids"],
    )

expected_edge_types: dict[tuple[str, str], set[str]] = {}
edge_field_types = (
    ("predecessor_claim_ids", "predecessor_claim"),
    ("blocked_claim_ids", "blocked_by"),
    ("supported_claim_ids", "supported_by"),
    ("conditioned_claim_ids", "conditioned_by"),
    ("negative_successor_claim_ids", "negative_successor_of"),
    ("routed_claim_ids", "routed_through"),
    ("successor_claim_ids", "successor_of"),
)
for debt_row in debt_rows:
    for field, edge_type in edge_field_types:
        for claim_id in debt_row[field]:
            expected_edge_types.setdefault((claim_id, debt_row["debt_id"]), set()).add(
                edge_type
            )

serialized_edges = topology["claim_debt_edges"]
actual_edge_types = {
    (row["claim_id"], row["debt_id"]): set(row["edge_types"])
    for row in serialized_edges
}
check(
    "claim_debt_edges_unique",
    len(actual_edge_types) == len(serialized_edges),
)
check(
    "claim_debt_edge_count_reconciles",
    len(serialized_edges) == topology["claim_debt_edge_count"],
)
check(
    "claim_debt_graph_is_exactly_bidirectional",
    actual_edge_types == expected_edge_types,
    f"actual={len(actual_edge_types)} expected={len(expected_edge_types)}",
)

hodge_encoding_debt_id = "D8A-DEBT-HODGE-CORRECTION-NORMATIVE-ENCODING"
hodge_encoding_edge = actual_edge_types[("D10-CL-N-006", hodge_encoding_debt_id)]
check(
    "confirmed_Hodge_claim_is_supported_not_blocked",
    "supported_by" in hodge_encoding_edge
    and "successor_of" in hodge_encoding_edge
    and "blocked_by" not in hodge_encoding_edge,
)
composition_status_debt_id = "GTRS-CI-PC-DEBT-COMPOSITION-PROFILE-STATUS"
composition_negative_edge = actual_edge_types[
    ("D10-CL-X-002", composition_status_debt_id)
]
check(
    "composition_nonuniqueness_is_negative_successor_not_blocked",
    "negative_successor_of" in composition_negative_edge
    and "successor_of" in composition_negative_edge
    and "blocked_by" not in composition_negative_edge,
)
for row in claims:
    nested = {
        (row["claim_id"], edge["debt_id"]): set(edge["edge_types"])
        for edge in row["debt_edges"]
    }
    check(
        f"current_claim_nested_edges_exact:{row['claim_id']}",
        nested
        == {
            key: value
            for key, value in expected_edge_types.items()
            if key[0] == row["claim_id"]
        },
    )
    check(
        f"current_claim_bearing_debts_exact:{row['claim_id']}",
        set(row["bearing_debt_ids"])
        == {key[1] for key in expected_edge_types if key[0] == row["claim_id"]},
    )
for row in historical_claims:
    nested = {
        (row["claim_id"], edge["debt_id"]): set(edge["edge_types"])
        for edge in row["debt_edges"]
    }
    check(
        f"historical_claim_nested_edges_exact:{row['claim_id']}",
        nested
        == {
            key: value
            for key, value in expected_edge_types.items()
            if key[0] == row["claim_id"]
        },
    )

for row in debt_rows:
    debt_id = row["debt_id"]
    lineage = row["predecessor_lineage"]
    check(f"lineage_nonempty:{debt_id}", bool(lineage))
    check(f"lineage_complete:{debt_id}", row["predecessor_lineage_complete"] is True)
    check(
        f"lineage_contains_D9:{debt_id}",
        any(
            item["record_id"] == "GRC9V4-D9-RESIDUAL-DEBT-LEDGER-v1" for item in lineage
        ),
    )
    for item in lineage:
        path = ROOT / item["path"]
        data = json.loads(path.read_text())
        digest_field = (
            "decision_record_digest"
            if "decision_record_digest" in data
            else "artifact_digest"
        )
        check(f"lineage_path_exists:{debt_id}:{item['record_id']}", path.is_file())
        check(
            f"lineage_digest:{debt_id}:{item['record_id']}",
            item["source_digest"] == data[digest_field],
        )
        check(
            f"lineage_SHA:{debt_id}:{item['record_id']}",
            item["file_sha256"] == file_sha(path),
        )
        check(
            f"lineage_repo_relative:{debt_id}:{item['record_id']}",
            not Path(item["path"]).is_absolute(),
        )

transformation_counts = {
    name: sum(row["transformation"] == name for row in debt_rows)
    for name in debt["allowed_transformations"]
}
check(
    "transformation_counts_reconcile",
    transformation_counts == debt["transformation_counts"],
)
check("routed_debts_present", transformation_counts["routed"] == 18)
check("narrowed_debts_present", transformation_counts["narrowed"] == 7)
check("split_debts_present", transformation_counts["split"] == 2)
check(
    "resolved_negative_debts_present", transformation_counts["resolved_negative"] == 1
)
check("confirmed_debts_present", transformation_counts["confirmed"] == 1)

matched_debt = debt_by_id["GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION"]
check("matched_discrimination_is_routed", matched_debt["transformation"] == "routed")
check(
    "matched_discrimination_verification_preserved",
    matched_debt["verification_obligation"]
    == "D10-VERIFY-MATCHED-PROFILE-DISCRIMINATION",
)
check(
    "matched_current_evidence_negative_preserved",
    "D10-CL-X-002" in matched_debt["negative_successor_claim_ids"],
)

core_debt = debt_by_id["D7-DEBT-A-CORE-STATUS"]
check(
    "A_core_status_is_provenance_negative",
    core_debt["transformation"] == "resolved_negative",
)
check(
    "A_core_status_negative_split",
    {"D10-CL-X-004", "D10-CL-X-006"} <= set(core_debt["negative_successor_claim_ids"]),
)
check(
    "A_future_core_derivability_not_negated",
    "without_claiming_that_no_A_like_law_can_ever_be_derived_from_core"
    in claim_by_id["D10-CL-X-004"]["normative_effect"],
)
check(
    "A_nonuniqueness_is_constitutive_axis_only",
    "unique_GRC9V4_constitutive_completion" in claim_by_id["D10-CL-X-006"]["statement"]
    and "multiple_realization" not in claim_by_id["D10-CL-X-006"]["statement"],
)
check(
    "historical_A_core_question_is_provenance_only",
    historical_by_id["D10-HCL-D7-DEBT-A-CORE-STATUS"]["statement"]
    == "inherited_core_provenance_of_the_present_A_completion_was_unclassified"
    and historical_by_id["D10-HCL-D7-DEBT-A-CORE-STATUS"]["stronger_claim_blocked"]
    == "the_present_A_completion_is_inherited_core_by_provenance",
)

singular_claim = claim_by_id["D10-CL-C-003"]["statement"]
check(
    "singular_successor_does_not_preclose_future_B",
    "separately_admitted_named_singular_successor_profile" in singular_claim
    and "currently_admitted_regular_A_C_profiles" in singular_claim
    and "not_implied_merely_by_reopening_Candidate_B" in singular_claim
    and "future_B_profiles" not in singular_claim,
)

trajectory_claim = claim_by_id["D10-CL-C-012"]
check(
    "C012_propagates_across_topology_decision_and_authorization_surfaces",
    "D10-CL-C-012" in categories["conditional"]
    and "D10-CL-C-012" in decision["decision"]["claim_topology"]["conditional"]
    and "D10-CL-C-012" in profile["conditional_claim_ids"],
)
check(
    "current_profile_population_is_not_future_exhaustiveness",
    "complete_for_the_initial_lineage_local_specification_population"
    in trajectory_claim["statement"]
    and "not_a_completeness_theorem" in trajectory_claim["statement"]
    and trajectory_claim["bearing_debt_ids"] == [],
)
check(
    "trajectory_claim_has_source_backed_anti_exhaustion_lineage",
    set(trajectory_claim["evidence_refs"])
    == {
        "GRC9V4-CD-D0-v1",
        "GRC9V4-CD-D1-v1",
        "GRC9V4-CD-D7G-v2",
        "GRC9V4-GTRS-COMP-v1",
    }
    and set(trajectory_claim["blocked_relabels"])
    == {
        "A_C_exhaust_all_future_constitutive_families",
        "five_realizations_are_exhaustive",
        "current_PC_is_the_universal_persistent_carrier_law",
    },
)
check(
    "trajectory_claim_semantics_are_present_in_accepted_sources",
    d0["decision"]["candidate_admission_contract"]["candidate_universe_status"]
    == "exhaustive_over_named_pre_D1_families_not_exhaustive_over_all_possible_V4_architectures"
    and d1["decision"]["current_candidate_set_exhausted"] is False
    and d7g["decision"]["minimum_temporal_realization_pressure_surface"][
        "family_set_role"
    ]
    == "minimum_required_pressure_set_not_an_exhaustive_taxonomy"
    and comp["decision"]["separable_axis_result"]["consequence"]
    == "the_eight_positive_rows_are_primary_pressured_points_not_an_exhaustive_cartesian_product_and_axis_separation_is_not_a_composability_claim",
)
check(
    "current_PC_scope_is_present_in_accepted_sources",
    comp["decision"]["persistent_writer_family_boundary"]["pressured_representative"]
    == "scalar_ZOH_single_tau_PC"
    and comp["decision"]["persistent_writer_family_boundary"]["universal_family_law"]
    is False
    and pc["decision"]["primary_family_preregistration"]["family_scope"]
    == "one_preregistered_primary_representative_not_the_universal_persistent_carrier_law",
)
check(
    "future_profile_admission_reopens_earliest_affected_contract",
    "new_complete_profile_identity" in trajectory_claim["normative_effect"]
    and "earliest_accepted_contract" in trajectory_claim["normative_effect"]
    and all(
        term in trajectory_claim["normative_effect"]
        for term in (
            "authority",
            "staging",
            "state",
            "geometry",
            "accounting",
            "lifecycle",
        )
    )
    and trajectory_claim["activation_condition"]
    == "new_constitutive_realization_hybrid_or_geometry_profile_proposed",
)

units_debt = debt_by_id["D7-DEBT-A-UNITS-AND-GAUGE"]
check("A_units_debt_split", units_debt["transformation"] == "split")
check(
    "A_units_debt_supports_nondimensional_profile",
    units_debt["supported_claim_id"] == "D10-CL-O-001"
    and "normalized_nondimensional" in claim_by_id["D10-CL-O-001"]["statement"],
)

verification_ids = {row["obligation_id"] for row in debt["verification_obligations"]}
check("verification_obligation_count_11", len(verification_ids) == 11)
check(
    "verification_references_valid",
    all(
        row["verification_obligation"] is None
        or row["verification_obligation"] in verification_ids
        for row in debt_rows
    ),
)
check(
    "verification_claim_refs_valid",
    all(
        set(row["claim_ids_blocked"]) <= set(claim_ids)
        for row in debt["verification_obligations"]
    ),
)

architecture = topology["architecture_selection"]
check(
    "profile_explicit_architecture",
    "profile_explicit" in architecture["selected_architecture"],
)
check("no_unique_candidate", architecture["unique_candidate_selected"] is False)
check("no_unique_realization", architecture["unique_realization_selected"] is False)
check(
    "architecture_selection_does_not_claim_future_profile_exhaustion",
    architecture["current_admitted_profile_population_is_future_exhaustive"] is False
    and "the_current_complete_profile_roster_is_not_a_completeness_theorem_over_future_lawful_V4_profiles"
    in topology["invariants"],
)
check(
    "Candidate_B_not_rejected",
    profile["candidate_profiles"]["B"].startswith(
        "reserved_successor_extension_slot_routed_not_rejected"
    ),
)
check("A_optional", profile["candidate_profiles"]["A"].startswith("named_optional"))
check("C_optional", profile["candidate_profiles"]["C"].startswith("named_optional"))
check("RG_Lipschitz_only", "Lipschitz" in profile["realization_profiles"]["RG2b"])
check("CI_PC_gain_two", "gain_two" in profile["realization_profiles"]["CI_PC"])
check(
    "current_PC_is_exactly_scoped_not_universal",
    "scalar_ZOH_one_tau_PC" in profile["realization_profiles"]["PC"]
    and "scalar_ZOH_one_tau_PC" in claim_by_id["D10-CL-O-006"]["statement"]
    and "current_PC_is_the_universal_persistent_carrier_law"
    in claim_by_id["D10-CL-O-006"]["blocked_relabels"],
)

grammar = profile["executable_profile_conformance_grammar"]
expected_complete_profiles = {
    f"{candidate}_{realization}"
    for candidate in ("A", "C")
    for realization in ("CI", "OS", "RG2b", "PC", "CI_PC")
}
check(
    "complete_profile_grammar_exact",
    set(grammar["admitted_complete_profile_ids"]) == expected_complete_profiles
    and grammar["admitted_complete_profile_count"] == 10,
)
check(
    "exactly_one_candidate_and_realization_per_runtime_state",
    grammar["constitutive_family_cardinality_per_runtime_state"] == "exactly_one"
    and grammar["realization_cardinality_per_runtime_state"] == "exactly_one",
)
check(
    "implementation_support_nonempty_subset",
    "nonempty_subset" in grammar["implementation_support_rule"],
)
check(
    "zero_profile_and_B_execution_blocked",
    grammar["zero_candidate_or_zero_realization_executable_instance_allowed"] is False
    and grammar["Candidate_B_executable"] is False,
)
check(
    "state_snapshot_and_receipt_profile_identity_grammar",
    grammar["runtime_state_binding_rule"]
    == "X_current_X_reset_and_each_snapshot_bind_exactly_one_unambiguous_complete_profile_identity"
    and grammar["profile_migration_receipt_binding_rule"]
    == "each_migration_receipt_binds_the_ordered_pair_p_source_p_target"
    and grammar["topology_event_receipt_binding_rule"]
    == "each_topology_event_receipt_binds_the_ordered_pair_p_source_p_target_with_equality_when_the_complete_profile_is_unchanged",
)
check(
    "current_profile_grammar_is_initial_not_future_exhaustive",
    grammar["current_admitted_profile_population_scope"]
    == "complete_for_the_initial_lineage_local_specification_population_not_exhaustive_over_future_lawful_V4_profiles"
    and grammar["current_profile_population_is_future_exhaustive"] is False
    and "earliest_accepted_contract" in grammar["future_profile_admission_rule"],
)
unfolding = profile["unfolding_trajectory"]
check(
    "unfolding_trajectory_is_nonprescriptive",
    unfolding["prescribed_successor_schedule"] is False
    and "not_a_fixed_successor_schedule" in unfolding["current_topology_role"]
    and "not_a_mandatory_linear_backlog" in unfolding["verification_obligation_rule"],
)
check(
    "unfolding_trajectory_preserves_claim_activation_and_preclosure_boundary",
    "activate_only_when" in unfolding["conditional_and_open_activation_rule"]
    and "until_new_evidence_transforms_them" in unfolding["negative_claim_rule"]
    and "substrate_provenance_audit_remains_mandatory"
    in unfolding["preclosure_convergence_rule"]
    and decision["decision"]["unfolding_trajectory"] == unfolding,
)
check(
    "unfolding_machine_and_prose_contracts_agree",
    "## Unfolding Trajectory" in decision_report
    and "does not prescribe a fixed successor schedule" in decision_report
    and "mandatory linear backlog" in decision_report
    and "reopening of the earliest accepted contract" in decision_report
    and "Negative claims remain current boundaries unless new evidence transforms them"
    in decision_report,
)
check(
    "current_profile_and_PC_scope_propagate_to_human_surfaces",
    all(
        "current_profile_population_future_exhaustive = false" in text
        and "current_PC_profile = scalar_ZOH_one_tau_PC_persistent_K4_history" in text
        and "unfolding_trajectory = claim_activated_not_fixed_successor_schedule"
        in text
        for text in (
            (DECISIONS.parent / "GRC9V4ConstitutiveDesignPlan.md").read_text(),
            (DECISIONS.parent / "GRC9V4ConstitutiveDesignChecklist.md").read_text(),
            (
                DECISIONS.parent / "GRC9V4ConstitutiveDesignDecisionLedger.md"
            ).read_text(),
        )
    ),
)
check(
    "D9_root_strength_propagated_to_CI",
    "bounded_domain_uniqueness" in claim_by_id["D10-CL-O-003"]["statement"]
    and "contraction_contract" in claim_by_id["D10-CL-O-003"]["statement"]
    and "stratum_local_uniqueness" in claim_by_id["D10-CL-O-003"]["statement"]
    and "GRC9V4-CD-D9-v1" in claim_by_id["D10-CL-O-003"]["evidence_refs"],
)
check(
    "D9_root_strength_propagated_to_CI_PC",
    "bounded_domain_contraction" in claim_by_id["D10-CL-O-007"]["statement"]
    and "stratum_local_composite_contraction"
    in claim_by_id["D10-CL-O-007"]["statement"]
    and "GRC9V4-CD-D9-v1" in claim_by_id["D10-CL-O-007"]["evidence_refs"],
)
check(
    "preclosure_substrate_provenance_audit_registered",
    "D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT" in verification_ids
    and profile["preclosure_obligation_id"] == "D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT"
    and profile["final_substrate_identity_closed"] is False,
)
check(
    "lineage_local_authorization_scope",
    profile["authorization_scope"]
    == "lineage_local_profile_explicit_GRC9V4_specification_only",
)

check(
    "D10_and_supporting_artifacts_are_accepted_bounded",
    all(
        row["status"] == "accepted_bounded"
        for row in (decision, topology, debt, profile)
    ),
)
check(
    "D10_disposition_authorizes_bounded_lineage_local_specification",
    decision["decision"]["scientific_disposition"]
    == "accepted_bounded_lineage_local_profile_explicit_spec_authorization"
    and profile["D10_disposition"]
    == "accepted_bounded_lineage_local_profile_explicit_spec_authorization",
)
check(
    "bounded_human_acceptance_recorded",
    decision["human_acceptance"]
    == {
        "accepted": True,
        "status": "accepted_bounded_2026-08-26",
        "scope": "lineage_local_profile_explicit_specification_authorization_only",
    },
)
auth = decision["authorization_effect"]
check(
    "spec_after_acceptance",
    auth["specification_authorized_after_human_acceptance"] is True,
)
check(
    "authorization_is_lineage_local_and_preclosure_bounded",
    auth["specification_authorization_scope"] == "lineage_local_profile_explicit_GRC9V4"
    and auth["final_substrate_identity_closed"] is False
    and auth["preclosure_substrate_provenance_audit_required"] is True,
)
check(
    "lineage_local_specification_is_authorized",
    auth["specification_authorized"] is True
    and profile["specification_authorized_now"] is True,
)
check(
    "implementation_plan_not_authorized",
    auth["implementation_plan_authorized"] is False,
)
check("implementation_not_authorized", auth["implementation_authorized"] is False)
check(
    "runtime_change_not_authorized", auth["runtime_or_src_change_authorized"] is False
)

control_ids = [row["control_id"] for row in decision["control_contract"]]
expected_control_count = decision["control_contract_count"]
check("control_count_nontrivial", len(control_ids) == expected_control_count >= 60)
check("control_ids_unique", len(set(control_ids)) == expected_control_count)
check(
    "control_ids_contiguous",
    control_ids
    == [f"D10-C{index:03d}" for index in range(1, expected_control_count + 1)],
)
check(
    "all_controls_passed",
    all(row["status"] == "passed" for row in decision["control_contract"]),
)
control_rules = {row["rule"] for row in decision["control_contract"]}
check(
    "trajectory_controls_are_machine_enforced",
    {
        "current_ten_profile_roster_is_not_a_future_completeness_theorem",
        "current_PC_is_scalar_ZOH_one_tau_not_the_universal_persistent_carrier_law",
        "future_profiles_require_explicit_successor_admission_and_earliest_affected_contract_reopening",
        "unfolding_trajectory_does_not_prescribe_a_fixed_successor_schedule",
        "verification_obligations_gate_named_claims_not_a_linear_backlog",
        "negative_claims_remain_boundaries_until_transformed_by_new_evidence",
    }
    <= control_rules,
)

all_text = "\n".join(
    path.read_text()
    for path in [
        DECISIONS / "D10NormativeClaimTopology.json",
        DECISIONS / "D10DebtClaimTransformationLedger.json",
        DECISIONS / "D10SpecificationAuthorizationProfile.json",
        DECISIONS / "D10DesignSynthesisAndSpecWritingDecision.json",
        DECISIONS / "D10DesignSynthesisAndSpecWritingDecision.md",
    ]
)
check(
    "no_machine_local_paths",
    "/home/uros" not in all_text and "Documents/RC-github" not in all_text,
)
check(
    "no_runtime_or_src_change_claim",
    decision["verification"]["runtime_or_src_changed"] is False,
)

decision_digest = decision["decision_record_digest"]
status_documents = [
    DECISIONS / "D10DesignSynthesisAndSpecWritingDecision.md",
    DECISIONS.parent / "GRC9V4ConstitutiveDesignPlan.md",
    DECISIONS.parent / "GRC9V4ConstitutiveDesignChecklist.md",
    DECISIONS.parent / "GRC9V4ConstitutiveDesignDecisionLedger.md",
]
check(
    "decision_digest_propagated",
    all(decision_digest in path.read_text() for path in status_documents),
)
check(
    "D10_acceptance_status_propagated",
    all("accepted_bounded" in path.read_text() for path in status_documents),
)
status_lines = subprocess.run(
    ["git", "status", "--short"],
    cwd=ROOT,
    check=True,
    text=True,
    capture_output=True,
).stdout.splitlines()
changed_paths = [line[3:] for line in status_lines if line]
check(
    "no_src_tests_or_specs_changes",
    all(not path.startswith(("src/", "tests/", "specs/")) for path in changed_paths),
    str(changed_paths),
)

failed = [(name, detail) for name, passed, detail in checks if not passed]
print(f"checks={len(checks)} passed={len(checks) - len(failed)} failed={len(failed)}")
for name, detail in failed:
    print(f"FAIL {name}: {detail}")
if failed:
    raise SystemExit(1)
print("D10_CLAIM_TOPOLOGY_AUDIT_PASS")
