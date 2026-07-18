#!/usr/bin/env python3
"""Build N31 Iteration 12 closeout and exact RCAE return bundle."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-07-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i12_closeout_and_rcae_return_artifacts"
OUTPUT = OUTPUTS / "n31_closeout_and_rcae_return_i12.json"
TRACE = OUTPUTS / "n31_i12_closeout_and_rcae_return_trace.json"
REPORT = REPORTS / "n31_closeout_and_rcae_return_i12.md"

I1 = OUTPUTS / "n31_source_inventory_i1.json"
I2 = OUTPUTS / "n31_semantic_representation_control_schema_i2.json"
I8 = OUTPUTS / "n31_d0_replay_controls_classification_i8.json"
I10 = OUTPUTS / "n31_added_mechanism_replay_controls_i10.json"
I11 = OUTPUTS / "n31_comparative_semantic_native_admission_i11.json"
I10_B_FAMILY = (
    OUTPUTS
    / "n31_i10_added_mechanism_replay_control_artifacts"
    / "n31_i10_B_family_replay_controls.json"
)
I10_C2_FAMILY = (
    OUTPUTS
    / "n31_i10_added_mechanism_replay_control_artifacts"
    / "n31_i10_C_family_replay_controls.json"
)

SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_closeout_and_rcae_return_i12.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
I11_COMMIT_REVISION = "55d5f083bfbc09d917d7a0c1df0600d4fb85cc43"
PROTECTED_BASE_REVISION = "7075ecb5e464401df96f16eac171fbefe0e532dc"

SOURCE_IDENTITIES = {
    I1: (
        "c8b1d7eb4b8009b418b7e7c240628b1c1a547d12e259156f2e53e63bb3dc9736",
        "1aff8008e26e29001da019168c8340322fe3172be8b2d8ea60c3de1496f47d79",
    ),
    I2: (
        "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf",
        "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6",
    ),
    I8: (
        "bf7d5eb98ab6b84e16a86fe4eba662e9b99ac648abd9b9490dcc6598c40cb5d8",
        "28a3d8b9e98b23ebdc7d852e9264fd802dad9bb45d48097d40efa2a0b1c9dc61",
    ),
    I10: (
        "29314dc62908e445deeb868ad04719dc1c23bd856562ac159098f5a3b081e257",
        "c8bf981ae9b5d59e2e486dc1c53bf84a1859ddf4569d4eea4c253e85039872af",
    ),
    I11: (
        "95d4577ea77f49afa185e49bccb3d29a2b404f1f1bb626c7a8840f2271c93eb6",
        "e3bd4c5f23956edd35d18c42b383302d34132a259e2ba2d2e0cb336686e0edc4",
    ),
}

CANDIDATE_IDS = [
    "D0a_native_spatial_organization",
    "D0b_finite_window_derived_observable",
    "D0c_instantaneous_geometry_comparator",
    "A_release_efficacy_attenuation",
    "B_conserved_export_policy",
    "C2_exact_history_susceptibility_closure",
]

BLOCKED_RELABELS = [
    "one_general_decay_law",
    "native_autonomous_decay",
    "D0_R_success",
    "B_R_as_D0_R",
    "B_R_D0_R_equivalence",
    "strict_current_C_only_C2",
    "native_C2",
    "trail_or_stigmergic_field",
    "memory_or_learning",
    "communication_or_coordination",
    "ecology_regime",
    "agency_or_selfhood",
    "sentience_or_organism_life",
    "native_support",
    "phase8_completion",
    "automatic_RCAE_adoption",
    "cross_context_reuse",
]

DR6_CONTRACT_ONLY_MEANS = (
    "reusable_testable_semantics_and_acceptance_contract"
)
DR6_CONTRACT_ONLY_DOES_NOT_MEAN = [
    "cross_context_execution",
    "native_implementation",
    "ecology_evidence",
    "provider_adoption",
    "general_decay_law",
]
CONFORMANCE_REQUIRED_FIELDS = {
    "admissible_inputs",
    "forbidden_inputs",
    "carrier_authority",
    "producer_authority",
    "native_executor_authority",
    "formation_condition",
    "weakening_condition",
    "later_readout_requirement",
    "conservation_accounting_invariants",
    "restoration_identity",
    "duplicate_behavior",
    "refusal_behavior",
    "topology_scope",
    "transfer_limitations",
    "claim_ceiling",
    "consumer_obligations",
    "consumer_control_set",
    "forbidden_claims",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def git_output(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def git_diff_empty(base: str, paths: list[str]) -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", base, "--", *paths],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def write_record(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    value = dict(record)
    value["output_digest"] = digest_value(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value), encoding="utf-8")
    return value


def source_record(path: Path, role: str) -> dict[str, Any]:
    value = load_json(path)
    expected_digest, expected_sha = SOURCE_IDENTITIES[path]
    actual_sha = sha256_file(path)
    return {
        "path": relative(path),
        "source_role": role,
        "status": value.get("status", "not_recorded"),
        "acceptance_state": value.get("acceptance_state", "not_recorded"),
        "expected_output_digest": expected_digest,
        "actual_output_digest": value.get("output_digest"),
        "internal_output_digest_exact": internal_output_digest_exact(value),
        "expected_sha256": expected_sha,
        "actual_sha256": actual_sha,
        "identity_exact": value.get("output_digest") == expected_digest
        and actual_sha == expected_sha,
    }


def artifact_entry(path: Path, role: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": relative(path),
        "artifact_role": role,
        "sha256": sha256_file(path),
        "output_digest": value["output_digest"],
    }


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def keyed(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    return {row["comparison_row_id"]: row[field] for row in rows}


def required_value_is_semantically_populated(value: Any) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, str):
        return value not in {"not_recorded", "pending", "placeholder"}
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def contract_statuses() -> dict[str, dict[str, Any]]:
    return {
        "D0a_native_spatial_organization": {
            "reusable_contract_status": "not_issued_native_foundation_not_decay_provider",
            "contract_semantics_rung": "not_assigned",
            "executed_mechanism_rung": "DR2",
            "cross_context_reuse_evidence": "unsupported",
        },
        "D0b_finite_window_derived_observable": {
            "reusable_contract_status": "not_issued_diagnostic_only",
            "contract_semantics_rung": "not_assigned",
            "executed_mechanism_rung": "DR3_observable_only",
            "cross_context_reuse_evidence": "unsupported",
        },
        "D0c_instantaneous_geometry_comparator": {
            "reusable_contract_status": "not_issued_instantaneous_diagnostic_only",
            "contract_semantics_rung": "not_assigned",
            "executed_mechanism_rung": "DR1_comparator_only",
            "cross_context_reuse_evidence": "unsupported",
        },
        "A_release_efficacy_attenuation": {
            "reusable_contract_status": "not_issued_retained_semantic_boundary",
            "contract_semantics_rung": "not_assigned",
            "executed_mechanism_rung": "DR5_producer_mediated",
            "cross_context_reuse_evidence": "unsupported",
        },
        "B_conserved_export_policy": {
            "reusable_contract_status": "issued",
            "contract_semantics_rung": "DR6_contract_only",
            "executed_mechanism_rung": "DR5_producer_mediated",
            "cross_context_reuse_evidence": "unsupported",
        },
        "C2_exact_history_susceptibility_closure": {
            "reusable_contract_status": "issued",
            "contract_semantics_rung": "DR6_contract_only",
            "executed_mechanism_rung": "DR5_producer_extension_relation_DR2_native_DR0",
            "cross_context_reuse_evidence": "unsupported",
        },
    }


def build_br_contract(i10: dict[str, Any], i11: dict[str, Any]) -> dict[str, Any]:
    i10_family = load_json(I10_B_FAMILY)
    consumer_control_set = [
        "artifact_replay",
        "snapshot_load_replay",
        "branch_replay",
        "duplicate_replay",
        "explicit_destination_and_complete_conservation",
        "source_C_clamp_reverses_readout",
        "destination_C_clamp_preserves_readout",
        "matched_route_mass_loss_without_contrast_change_preserves_readout",
        "producer_omission_yields_zero_export",
        "rejected_readout_is_atomic_and_state_neutral",
    ]
    forbidden_claims = [
        "ordinary_post_formation_D0_R",
        "autonomous_native_decay",
        "susceptibility_relaxation",
        "organization_transferred_to_destination",
        "cross_context_reuse_evidence",
        "native_support",
        "general_decay_law",
        "ecology_evidence",
    ]
    return {
        "artifact_kind": "n31_i12_B_R_reusable_contract",
        "artifact_schema_version": "n31_i12_B_R_reusable_contract_v2",
        "contract_id": "n31_B_R_conserved_redistribution_contract_v2",
        "candidate_id": "B_conserved_export_policy",
        "semantic_class": "B-R",
        "authority": {
            "transport": "native_LGRC9V3_conservative_packet_transport",
            "export_lifecycle": "consumer_or_producer_owned_until_naturalized",
            "native_upgrade_allowed": False,
        },
        "use_when": (
            "the consuming experiment requires conservative coherence redistribution "
            "to an explicit destination, with attributable local route-mass and "
            "route-contrast weakening"
        ),
        "must_not_use_as": forbidden_claims,
        "required_inputs": [
            "source_current_native_coherence_and_packet_state",
            "registered_route_support_and_boundary",
            "explicit_destination_outside_the_readout_path",
            "predeclared_export_eligibility_amount_time_and_destination_policy",
        ],
        "mass_contract": {
            "equation": "source_debit == in_flight_packet_amount == destination_credit",
            "zero_export_row_required": True,
            "destination_must_be_explicit": True,
            "global_coherence_budget_must_close": True,
        },
        "organization_contract": {
            "native_route_state_weakened": True,
            "organization_measure": "O_B route contrast from registered native coherence state",
            "route_mass_and_organization_reported_separately": True,
            "bounded_response_shape": "monotonic_linear_through_cap_boundary",
            "organization_at_destination_transferred": "unsupported",
        },
        "mediation_contract": {
            "supported": True,
            "scope": "bounded_partial_local_source_C",
            "full_route_distribution_mediation": False,
            "source_C_clamp_must_reverse_readout": True,
            "destination_C_clamp_must_preserve_readout": True,
            "matched_mass_loss_without_organization_change_must_preserve_readout": True,
        },
        "time_and_transition_owner": {
            "native_event_progression": True,
            "export_decision_owner": "declared_consumer_or_producer_policy",
            "ordinary_autonomous_export_available": False,
        },
        "restoration_and_controls": {
            "executed_evidence_rung": "DR5_producer_mediated",
            "required_replay_modes": [
                "artifact_replay",
                "snapshot_load_replay",
                "branch_replay",
                "duplicate_replay",
            ],
            "restoration_identity": "lgrc9v3_restoration_identity_v2_plus_export_policy_identity",
            "complete_I10_control_matrix_required": True,
        },
        "conformance_contract": {
            "admissible_inputs": [
                "source_current_native_coherence_and_packet_state",
                "registered_route_support_and_boundary",
                "explicit_destination_outside_the_readout_path",
                "predeclared_export_eligibility_amount_time_and_destination_policy",
            ],
            "forbidden_inputs": [
                "hidden_producer_support",
                "post_hoc_export_policy",
                "unspecified_destination",
                "label_only_route_state",
                "report_derived_state_as_runtime_input",
            ],
            "carrier_authority": "native_LGRC9V3_coherence_and_packet_state",
            "producer_authority": "export_eligibility_amount_cap_time_and_destination_only",
            "native_executor_authority": "LGRC9V3_packet_admission_transport_and_credit",
            "formation_condition": "registered_native_route_contrast_forms_and_persists_before_export",
            "weakening_condition": "export_decreases_local_route_mass_and_route_contrast_by_attributable_amount",
            "later_readout_requirement": "local_source_C_admission_boundary_changes_while_destination_C_clamp_does_not",
            "conservation_accounting_invariants": [
                "source_debit_equals_in_flight_packet_amount",
                "in_flight_packet_amount_equals_destination_credit",
                "global_node_plus_packet_coherence_budget_closes",
            ],
            "restoration_identity": "lgrc9v3_restoration_identity_v2_plus_export_policy_identity",
            "duplicate_behavior": "consumed_one_shot_receipt_refuses_second_export_without_mutation",
            "refusal_behavior": "ineligible_or_rejected_operations_are_atomic_and_state_neutral",
            "topology_scope": "declared_frozen_route_with_explicit_destination_outside_readout_path",
            "transfer_limitations": [
                "cross_context_reuse_unsupported",
                "organization_at_destination_transferred_unsupported",
                "D0_R_bridge_not_tested",
            ],
            "claim_ceiling": "producer_mediated_B_R_DR5_with_DR6_contract_only",
            "consumer_obligations": [
                "predeclare_export_policy_and_destination",
                "retain_separate_route_mass_and_route_contrast_fields",
                "retain_producer_residue_and_naturalization_debt",
                "generate_fresh_context_specific_evidence",
                "apply_all_consumer_controls",
            ],
            "consumer_control_set": consumer_control_set,
            "forbidden_claims": forbidden_claims,
        },
        "DR6_contract_only_means": DR6_CONTRACT_ONLY_MEANS,
        "DR6_contract_only_does_not_mean": DR6_CONTRACT_ONLY_DOES_NOT_MEAN,
        "source_evidence": [
            {
                "path": relative(I10),
                "artifact_role": "executed_DR5_replay_control_authority",
                "sha256": sha256_file(I10),
                "output_digest": i10["output_digest"],
            },
            {
                "path": relative(I10_B_FAMILY),
                "artifact_role": "B_R_family_execution_and_control_evidence",
                "sha256": sha256_file(I10_B_FAMILY),
                "output_digest": i10_family["output_digest"],
            },
            {
                "path": relative(I11),
                "artifact_role": "comparative_semantic_authority",
                "sha256": sha256_file(I11),
                "output_digest": i11["output_digest"],
            },
        ],
        "contract_status": contract_statuses()["B_conserved_export_policy"],
        "producer_residue": ["export eligibility", "amount/cap", "time", "destination"],
        "naturalization_debt": [
            "native route-local export lifecycle",
            "full route-distribution mediation",
            "separate D0-R bridge evidence",
        ],
        "source_I11_output_digest": i11["output_digest"],
    }


def build_c2_contract(i10: dict[str, Any], i11: dict[str, Any]) -> dict[str, Any]:
    i10_family = load_json(I10_C2_FAMILY)
    consumer_control_set = [
        "artifact_replay",
        "snapshot_load_replay",
        "branch_replay",
        "duplicate_replay",
        "post_feedback_restoration_replay",
        "exact_history_rederivation",
        "wrong_edge_or_nonqualifying_event_invariance",
        "wrong_lineage_invariance",
        "semantic_label_invariance",
        "role_preserving_topology_invariance",
        "physical_progression_changes_relation",
        "conservation_exact",
    ]
    forbidden_claims = [
        "strict_current_C_only_relation",
        "native_route_organization_weakening",
        "native_C2",
        "cross_context_reuse_evidence",
        "native_support",
        "general_decay_law",
        "ecology_evidence",
    ]
    return {
        "artifact_kind": "n31_i12_C2_reusable_contract",
        "artifact_schema_version": "n31_i12_C2_reusable_contract_v2",
        "contract_id": "n31_C2_exact_history_susceptibility_contract_v2",
        "candidate_id": "C2_exact_history_susceptibility_closure",
        "semantic_class": "C.2",
        "authority": {
            "history": "exact_serialized_native_packet_history",
            "susceptibility_relation": "exact_recomputed_functional",
            "constitutive_insertion": "consumer_or_producer_owned_closure",
            "native_runtime_support": "DR0",
            "native_upgrade_allowed": False,
        },
        "use_when": (
            "the consuming experiment requires activity-indexed susceptibility or "
            "effective-geometry relaxation rather than conservative field export"
        ),
        "must_not_use_as": forbidden_claims,
        "relation_contract": {
            "schema": "n31_C2_general_physical_history_susceptibility_v1",
            "form": "S_e=S_floor+clip(sum(alpha*q_r*rho^delta_tau),0,S_max-S_floor)",
            "executed_parameters": {"S_floor": 0.5, "S_max": 1.0, "alpha": 1.0, "rho": 0.75},
            "independent_S_state_allowed": False,
            "exact_recomputation_required": True,
            "event_or_packet_identifiers_are_duplicate_integrity_only": True,
        },
        "mediation_contract": {
            "supported": True,
            "scope": "bounded_effective_geometry",
            "ordinary_native_constitutive_hook_present": False,
            "producer_inserts_effective_conductance": True,
            "native_potential_flux_and_packet_executor_consumes_insertion": True,
        },
        "time_and_transition_owner": {
            "internal_progression": "qualifying committed local native arrivals",
            "wall_clock_decay": False,
            "quiescence_decay": False,
            "packet_scheduling": "experiment_producer",
        },
        "restoration_and_controls": {
            "executed_evidence_rung": "DR5_producer_extension_relation_DR2_native_DR0",
            "required_replay_modes": [
                "artifact_replay",
                "snapshot_load_replay",
                "branch_replay",
                "duplicate_replay",
                "post_feedback_restoration_replay",
            ],
            "restoration_identity": "lgrc9v3_restoration_identity_v2_plus_exact_rederived_relation",
            "post_feedback_S_and_next_step_exact": True,
        },
        "conformance_contract": {
            "admissible_inputs": [
                "exact_serialized_native_packet_history",
                "declared_local_relation_identity",
                "predeclared_susceptibility_parameters",
                "source_current_native_geometry_and_coherence",
            ],
            "forbidden_inputs": [
                "independent_stored_S_state",
                "external_history_archive_substituted_for_native_history",
                "post_hoc_relation_parameters",
                "semantic_labels_as_physical_history",
                "hidden_constitutive_state",
            ],
            "carrier_authority": "exact_serialized_native_packet_history",
            "producer_authority": "exact_relation_recomputation_effective_geometry_insertion_and_packet_scheduling",
            "native_executor_authority": "LGRC9V3_potential_flux_packet_transport_and_history_commit",
            "formation_condition": "qualifying_committed_local_native_arrival_history_exists",
            "weakening_condition": "causal_progression_reduces_exact_history_derived_susceptibility_toward_floor",
            "later_readout_requirement": "changed_effective_geometry_changes_later_native_flux_or_transport",
            "conservation_accounting_invariants": [
                "derived_relation_has_no_independent_mass",
                "native_node_plus_packet_coherence_budget_closes",
                "post_transport_history_rederives_relation_exactly",
            ],
            "restoration_identity": "lgrc9v3_restoration_identity_v2_plus_exact_rederived_relation",
            "duplicate_behavior": "duplicate_committed_arrival_identity_is_rejected_without_relation_change",
            "refusal_behavior": "wrong_edge_lineage_role_or_label_does_not_change_relation",
            "topology_scope": "declared_local_route_and_role_preserving_topology_family",
            "transfer_limitations": [
                "cross_context_reuse_unsupported",
                "native_constitutive_hook_absent",
                "packetization_invariance_pending",
                "multi_cycle_stability_pending",
            ],
            "claim_ceiling": "relation_DR2_producer_extension_DR5_native_DR0_with_DR6_contract_only",
            "consumer_obligations": [
                "bind_exact_history_functional_and_parameters",
                "retain_producer_constitutive_insertion_authority",
                "retain_native_runtime_DR0",
                "retain_producer_residue_and_naturalization_debt",
                "generate_fresh_context_specific_evidence",
                "apply_all_consumer_controls",
            ],
            "consumer_control_set": consumer_control_set,
            "forbidden_claims": forbidden_claims,
        },
        "DR6_contract_only_means": DR6_CONTRACT_ONLY_MEANS,
        "DR6_contract_only_does_not_mean": DR6_CONTRACT_ONLY_DOES_NOT_MEAN,
        "source_evidence": [
            {
                "path": relative(I10),
                "artifact_role": "executed_DR5_replay_control_authority",
                "sha256": sha256_file(I10),
                "output_digest": i10["output_digest"],
            },
            {
                "path": relative(I10_C2_FAMILY),
                "artifact_role": "C2_family_execution_and_control_evidence",
                "sha256": sha256_file(I10_C2_FAMILY),
                "output_digest": i10_family["output_digest"],
            },
            {
                "path": relative(I11),
                "artifact_role": "comparative_semantic_authority",
                "sha256": sha256_file(I11),
                "output_digest": i11["output_digest"],
            },
        ],
        "contract_status": contract_statuses()["C2_exact_history_susceptibility_closure"],
        "producer_residue": [
            "history functional application",
            "effective conductance insertion",
            "packet scheduling",
        ],
        "naturalization_debt": [
            "packetization invariance",
            "direct mediation controls",
            "multi-cycle stability",
            "topology lifecycle policy",
            "cache and pruning semantics",
            "native source-current re-admission",
        ],
        "source_I11_output_digest": i11["output_digest"],
    }


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    i1 = load_json(I1)
    i2 = load_json(I2)
    i8 = load_json(I8)
    i10 = load_json(I10)
    i11 = load_json(I11)
    profiles = i11["comparison_profiles"]
    profiles_by_id = {row["comparison_row_id"]: row for row in profiles}
    if list(profiles_by_id) != CANDIDATE_IDS:
        raise ValueError("I11 candidate order or identity changed")

    source_records = [
        source_record(I1, "N31_source_and_demand_authority"),
        source_record(I2, "N31_schema_and_return_contract_authority"),
        source_record(I8, "executed_D0_family_classification"),
        source_record(I10, "executed_added_mechanism_DR5_replay_control_authority"),
        source_record(I11, "comparative_conditional_frontier_authority"),
    ]

    br_contract_path = ARTIFACT_DIR / "n31_i12_B_R_reusable_contract.json"
    c2_contract_path = ARTIFACT_DIR / "n31_i12_C2_reusable_contract.json"
    disposition_path = ARTIFACT_DIR / "n31_i12_candidate_disposition_matrix.json"
    recommendation_path = ARTIFACT_DIR / "n31_i12_rcae_p2_i3_recommendation.json"
    authority_path = ARTIFACT_DIR / "n31_i12_source_authority_and_reconstruction.json"
    claim_path = ARTIFACT_DIR / "n31_i12_claim_debt_and_nativeness_register.json"

    br_contract = write_record(br_contract_path, build_br_contract(i10, i11))
    c2_contract = write_record(c2_contract_path, build_c2_contract(i10, i11))

    statuses = contract_statuses()
    disposition_rows = []
    for profile in profiles:
        candidate_id = profile["comparison_row_id"]
        disposition_rows.append(
            {
                "candidate_id": candidate_id,
                "primary_semantic_class": profile["semantic_class"],
                "representation_or_authority_class": profile["authority_lane"],
                "candidate_disposition": profile["selection_disposition"],
                "native_route_organization_state_weakened": profile[
                    "native_route_organization_state_weakened"
                ],
                "derived_organization_observable_weakened": profile[
                    "derived_organization_observable_weakened"
                ],
                "derived_susceptibility_relation_weakened": profile[
                    "derived_susceptibility_relation_weakened"
                ],
                "route_mass_decreased": profile["route_mass_decreased"],
                "later_readout_changed": profile["later_readout_changed"],
                "organization_mediated_readout_change_supported": profile[
                    "organization_mediated_readout_change_supported"
                ],
                "organization_mediation_scope": profile[
                    "organization_mediation_scope"
                ],
                "ladder_rungs": profile["ladder_rungs"],
                "reusable_contract": statuses[candidate_id],
                "producer_residue": profile["producer_residue"],
                "naturalization_debt": profile["naturalization_debt"],
                "native_upgrade_allowed": False,
                "topology_scope": profile["topology_scope"],
                "transfer_evidence": profile["transfer_evidence"],
            }
        )

    disposition_matrix = write_record(
        disposition_path,
        {
            "artifact_kind": "n31_i12_candidate_disposition_matrix",
            "artifact_schema_version": "n31_i12_candidate_disposition_matrix_v1",
            "candidate_count": len(disposition_rows),
            "rows": disposition_rows,
            "single_universal_selection": False,
            "selection_relation": "non_ranked_semantically_distinct_conditional_frontiers",
            "issued_contract_ids": [br_contract["contract_id"], c2_contract["contract_id"]],
            "contract_only_DR6_does_not_upgrade_execution": True,
        },
    )

    recommendation = write_record(
        recommendation_path,
        {
            "artifact_kind": "n31_i12_rcae_p2_i3_recommendation",
            "artifact_schema_version": "n31_i12_rcae_p2_i3_recommendation_v2",
            "rcae_source_revision": "ae11be2008b1902df1749faec531420432056c37",
            "target_lane": "AE01_L03_P2_I3_I03_re_admission",
            "return_status": "provider_contract_eligible_for_explicit_revision_bound_re_admission",
            "provider_contract_re_admission_eligible": True,
            "N31_positive_evidence_re_admitted_to_RCAE": False,
            "RCAE_ecology_evidence_must_be_generated_fresh": True,
            "automatic_adoption_allowed": False,
            "positive_P2_I3_may_resume_without_RCAE_re_admission": False,
            "required_RCAE_action": (
                "record a named re-admission decision selecting the demanded semantics, "
                "exact provider contract identity, exact N31 closeout identity, authority "
                "ceiling, producer residue, naturalization debt, controls, and forbidden "
                "claims before generating fresh positive ecology evidence"
            ),
            "required_re_admission_identity_fields": [
                "n31_closeout_output_digest",
                "contract_artifact_path",
                "contract_artifact_sha256",
                "contract_output_digest",
                "candidate_id",
                "semantic_route",
                "authority_ceiling",
                "executed_rung",
                "contract_only_rung",
                "producer_residue",
                "naturalization_debt",
                "consumer_control_set",
                "forbidden_claims",
            ],
            "n31_closeout_output_digest_source": {
                "path": relative(OUTPUT),
                "json_pointer": "/output_digest",
                "consumer_must_copy_exact_value": True,
            },
            "generic_decay_provider_selection_fails_closed": True,
            "semantic_routes": {
                "conservative_coherence_redistribution": {
                    "candidate_id": "B_conserved_export_policy",
                    "semantic_route": "conservative_coherence_redistribution",
                    "contract_id": br_contract["contract_id"],
                    "contract_artifact_path": relative(br_contract_path),
                    "contract_artifact_sha256": sha256_file(br_contract_path),
                    "contract_output_digest": br_contract["output_digest"],
                    "recommendation": "reopen around conserved coherence redistribution with explicit destination and local route weakening",
                    "authority_ceiling": "producer_mediated_B_R_DR5",
                    "executed_rung": "DR5_producer_mediated",
                    "contract_only_rung": "DR6_contract_only",
                    "producer_residue": br_contract["producer_residue"],
                    "naturalization_debt": br_contract["naturalization_debt"],
                    "consumer_control_set": br_contract["conformance_contract"]["consumer_control_set"],
                    "forbidden_claims": br_contract["conformance_contract"]["forbidden_claims"],
                },
                "activity_indexed_susceptibility": {
                    "candidate_id": "C2_exact_history_susceptibility_closure",
                    "semantic_route": "activity_indexed_susceptibility",
                    "contract_id": c2_contract["contract_id"],
                    "contract_artifact_path": relative(c2_contract_path),
                    "contract_artifact_sha256": sha256_file(c2_contract_path),
                    "contract_output_digest": c2_contract["output_digest"],
                    "recommendation": "reopen around effective susceptibility or geometry relaxation",
                    "authority_ceiling": "relation_DR2_producer_extension_DR5_native_DR0",
                    "executed_rung": "DR5_producer_extension",
                    "contract_only_rung": "DR6_contract_only",
                    "producer_residue": c2_contract["producer_residue"],
                    "naturalization_debt": c2_contract["naturalization_debt"],
                    "consumer_control_set": c2_contract["conformance_contract"]["consumer_control_set"],
                    "forbidden_claims": c2_contract["conformance_contract"]["forbidden_claims"],
                },
                "release_expression_attenuation": {
                    "candidate_id": "A_release_efficacy_attenuation",
                    "contract_id": "not_issued_current_demand",
                    "recommendation": "use A only if RCAE explicitly changes the demand to release expression",
                    "authority_ceiling": "producer_mediated_A_DR5_boundary",
                },
                "ordinary_native_D0_decay": {
                    "contract_id": "none",
                    "recommendation": "preserve blocker; autonomous native weakening was not found",
                    "authority_ceiling": "native_D0a_DR2",
                },
            },
            "B_R_and_C2_may_be_instantiated_together": True,
            "combined_effect_may_inherit_individual_DR5": False,
            "combined_provider_is_new_composition_candidate": True,
            "combined_provider_requires_separate_controls": True,
            "combined_provider_required_attribution": [
                "coherence_redistribution_caused_by_B_R",
                "susceptibility_modification_caused_by_C2",
                "interaction_or_interference_between_B_R_and_C2",
            ],
            "RCAE_owns": [
                "semantic_choice",
                "provider_admission",
                "topology_and_encounter_design",
                "ecology_side_controls",
                "later_trail_or_stigmergy_claim",
            ],
        },
    )

    protected_paths = i2["schema"]["protected_scope"]["protected_paths"]
    protected_git_paths = [
        "src",
        "lib",
        "specs",
        "implementation",
        "tests",
        "examples",
        "scripts",
        "pyproject.toml",
        "requirements.txt",
        "uv.lock",
    ]
    source_authority = write_record(
        authority_path,
        {
            "artifact_kind": "n31_i12_source_authority_and_reconstruction",
            "artifact_schema_version": "n31_i12_source_authority_and_reconstruction_v1",
            "graph_revision": I11_COMMIT_REVISION,
            "current_parent_revision": git_output("rev-parse", "HEAD"),
            "branch": git_output("branch", "--show-current"),
            "pygrc_version": importlib.metadata.version("pygrc"),
            "source_records": source_records,
            "all_source_identities_exact": all(row["identity_exact"] for row in source_records),
            "derived_cache_recomputation_status": {
                "D0": "passed_exact_I8",
                "A": "passed_exact_I10",
                "B_R": "passed_exact_I10",
                "C2": "passed_exact_I10",
            },
            "execution_reconstruction_status": {
                "D0": "passed_complete_I8",
                "A": "passed_complete_I10",
                "B_R": "passed_complete_I10",
                "C2": "passed_complete_including_post_feedback_next_step_I10",
            },
            "src_diff_empty_for_experiment_branch": git_diff_empty(
                PROTECTED_BASE_REVISION, ["src"]
            ),
            "protected_runtime_contract_diff_empty": git_diff_empty(
                PROTECTED_BASE_REVISION, protected_git_paths
            ),
            "protected_runtime_contract_path_scope": protected_paths,
            "I10_committed_authority_revision": "e7fc5b4a30e707c42aec83e94d40d36546a2af60",
            "I11_committed_authority_revision": I11_COMMIT_REVISION,
        },
    )

    claim_register = write_record(
        claim_path,
        {
            "artifact_kind": "n31_i12_claim_debt_and_nativeness_register",
            "artifact_schema_version": "n31_i12_claim_debt_and_nativeness_register_v2",
            "claim_ceiling": (
                "bounded graph-side decay-semantic classification and authority-qualified "
                "RCAE return contracts for conserved redistribution and effective susceptibility"
            ),
            "blocked_relabels": BLOCKED_RELABELS,
            "unsafe_claim_flags": {f"{claim}_allowed": False for claim in BLOCKED_RELABELS},
            "native_D0a_relation_ceiling": "DR2",
            "native_autonomous_weakening_supported": False,
            "native_decay_provider_available": False,
            "producer_contracts_do_not_upgrade_native": True,
            "contract_only_DR6_is_not_executed_DR6": True,
            "DR6_contract_only_means": DR6_CONTRACT_ONLY_MEANS,
            "DR6_contract_only_does_not_mean": DR6_CONTRACT_ONLY_DOES_NOT_MEAN,
            "cross_context_reuse_supported": False,
            "d0_to_br_bridge_status": "not_tested",
            "B_R_D0_R_equivalence_supported": False,
            "A_globally_rejected": False,
            "A_contract_issue_blocked_by_failure": False,
            "A_not_selected_because_current_return_targets_field_state_semantics": True,
            "deferred_C2_native_implementation_exists": True,
            "deferred_native_work_is_N31_closeout_blocker": False,
            "future_native_lane_must_restart_from_DR0": True,
            "producer_DR5_may_not_seed_native_rung": True,
            "remaining_debt_by_candidate": keyed(profiles, "naturalization_debt"),
            "producer_residue_by_candidate": keyed(profiles, "producer_residue"),
        },
    )

    generated = [
        (br_contract_path, "B_R_reusable_contract", br_contract),
        (c2_contract_path, "C2_reusable_contract", c2_contract),
        (disposition_path, "candidate_disposition_matrix", disposition_matrix),
        (recommendation_path, "RCAE_P2_I3_recommendation", recommendation),
        (authority_path, "source_authority_and_reconstruction", source_authority),
        (claim_path, "claim_debt_and_nativeness_register", claim_register),
    ]
    artifact_manifest = [artifact_entry(path, role, value) for path, role, value in generated]

    theory_source_ids = [
        row["source_id"]
        for row in i1["source_records"]
        if row["repository_id"] == "geometric_reflexive_coherence"
        and row["path"].startswith("core/")
    ]
    substrate_spec_source_ids = [
        row["source_id"]
        for row in i1["source_records"]
        if row["repository_id"] == "geometric_reflexive_coherence"
        and (row["path"].startswith("substrates/") or row["path"].startswith("investigations/"))
    ]
    pygrc_source_ids = [
        row["source_id"]
        for row in i1["source_records"]
        if row["repository_id"] == "graph_reflexive_coherence"
        and (row["path"].startswith("src/") or row["path"].startswith("specs/"))
    ]
    prior_experiment_source_ids = [
        row["source_id"]
        for row in i1["source_records"]
        if row["repository_id"] == "graph_reflexive_coherence"
        and row["path"].startswith("experiments/")
    ]
    rcae_demand_source_ids = [
        row["source_id"]
        for row in i1["source_records"]
        if row["repository_id"] == "reflexive_coherence_agentic_ecology"
    ]

    route_mass_contracts = {
        candidate_id: (
            "explicit_conservative_export_with_destination"
            if candidate_id == "B_conserved_export_policy"
            else "read_only_or_no_route_mass_change"
        )
        for candidate_id in CANDIDATE_IDS
    }
    route_organization_contracts = {
        "D0a_native_spatial_organization": "native_relation_forms_and_persists_no_autonomous_weakening",
        "D0b_finite_window_derived_observable": "exact_finite_window_observable_weakens_no_causal_mediation",
        "D0c_instantaneous_geometry_comparator": "instantaneous_current_state_comparison_only",
        "A_release_efficacy_attenuation": "route_state_not_weakened_expression_only",
        "B_conserved_export_policy": "native_route_mass_and_contrast_weaken_under_producer_owned_export_no_organization_transfer_claim",
        "C2_exact_history_susceptibility_closure": "derived_susceptibility_weakens_native_route_state_not_relabelled",
    }
    mediation_contracts = {
        candidate_id: {
            "supported": profiles_by_id[candidate_id][
                "organization_mediated_readout_change_supported"
            ],
            "scope": profiles_by_id[candidate_id]["organization_mediation_scope"],
        }
        for candidate_id in CANDIDATE_IDS
    }
    organization_domains = {
        "D0a_native_spatial_organization": "spatial_geometric",
        "D0b_finite_window_derived_observable": "mixed_spatial_temporal_diagnostic",
        "D0c_instantaneous_geometry_comparator": "geometric_instantaneous",
        "A_release_efficacy_attenuation": "functional_expression_phase",
        "B_conserved_export_policy": "spatial_coherence_magnitude_and_route_contrast",
        "C2_exact_history_susceptibility_closure": "mixed_causal_history_and_effective_geometry",
    }
    load_bearing_domains = {
        "D0a_native_spatial_organization": "native_spatial_route_state",
        "D0b_finite_window_derived_observable": "none_diagnostic_only",
        "D0c_instantaneous_geometry_comparator": "none_diagnostic_only",
        "A_release_efficacy_attenuation": "producer_owned_release_phase_and_local_receiver_C",
        "B_conserved_export_policy": "native_local_source_C_under_producer_owned_export",
        "C2_exact_history_susceptibility_closure": "exact_native_history_derived_effective_geometry",
    }
    trajectories = {
        "D0a_native_spatial_organization": "persistent_without_autonomous_weakening",
        "D0b_finite_window_derived_observable": "finite_window_fading_observable",
        "D0c_instantaneous_geometry_comparator": "instantaneous_change_no_trajectory",
        "A_release_efficacy_attenuation": "receipt_indexed_expression_attenuation",
        "B_conserved_export_policy": "bounded_monotonic_conservative_export",
        "C2_exact_history_susceptibility_closure": "activity_indexed_relaxation_toward_floor",
    }
    final_capability_dispositions = [
        {
            "question_id": "global_coherence_conservation",
            "theory_disposition": "direct_theory_requirement",
            "runtime_disposition": "candidate_specific_native_packet_and_budget_closure_available",
            "n31_closeout_disposition": "passed_for_all_executed_I8_and_I10_families",
        },
        {
            "question_id": "D0a_slow_causal_coherence_organization",
            "theory_disposition": "theoretically_compatible_not_automatically_discrete",
            "runtime_disposition": "exact_source_current_route_projection_formed_and_persisted",
            "n31_closeout_disposition": "native_DR2_autonomous_weakening_unsupported",
        },
        {
            "question_id": "D0b_fading_derived_observable",
            "theory_disposition": "admissible_as_observable_not_independent_state",
            "runtime_disposition": "exact_finite_window_derived_observable_available",
            "n31_closeout_disposition": "DR3_observable_only_no_causal_mediation",
        },
        {
            "question_id": "D0c_instantaneous_geometry",
            "theory_disposition": "directly_induced_by_current_coherence_flux_geometry",
            "runtime_disposition": "instantaneous_native_state_comparator_available",
            "n31_closeout_disposition": "DR1_no_persistence_or_weakening_trajectory",
        },
        {
            "question_id": "temporal_desynchronization_or_dispersion",
            "theory_disposition": "bounded_D0_domain_variant_only_if_causal_mediation_is_shown",
            "runtime_disposition": "native_timing_and_packet_events_available_without_native_distribution_mediator",
            "n31_closeout_disposition": "diagnostic_context_only_no_temporal_D0_provider_selected",
        },
        {
            "question_id": "candidate_A_release_efficacy",
            "theory_disposition": "expression_attenuation_not_field_state_decay",
            "runtime_disposition": "native_transport_plus_producer_owned_release_phase",
            "n31_closeout_disposition": "producer_mediated_DR5_retained_semantic_boundary_no_I12_contract",
        },
        {
            "question_id": "candidate_B_conserved_source_leakage",
            "theory_disposition": "continuity_compatible_with_explicit_destination",
            "runtime_disposition": "native_conservative_transport_plus_producer_owned_export_lifecycle",
            "n31_closeout_disposition": "B_R_DR5_with_DR6_contract_only_D0_R_bridge_not_tested",
        },
        {
            "question_id": "candidate_C2_exact_history_susceptibility",
            "theory_disposition": "effective_closure_beyond_strict_current_C_only_ontology",
            "runtime_disposition": "exact_native_history_available_native_constitutive_hook_missing",
            "n31_closeout_disposition": "relation_DR2_producer_DR5_native_DR0_with_DR6_contract_only",
        },
    ]

    required_return_fields = set(i2["schema"]["RCAE_return_manifest_schema"]["required_fields"])
    required_return_fields.update(
        {
            "native_route_organization_state_weakened_by_candidate",
            "derived_organization_observable_weakened_by_candidate",
            "derived_susceptibility_relation_weakened_by_candidate",
            "organization_mediated_readout_change_supported_by_candidate",
            "organization_mediation_scope_by_candidate",
            "n31_native_decay_classification",
            "n31_added_mechanism_decay_classifications",
            "native_upgrade_allowed_by_candidate",
            "causal_transition_owner_by_candidate",
            "candidate_specific_rung_qualifier_by_candidate",
            "reusable_contract_status_by_candidate",
            "native_D0a_relation_ceiling",
            "native_autonomous_weakening_supported",
            "native_decay_provider_available",
            "organization_at_destination_transferred_by_candidate",
            "provider_contract_re_admission_eligible",
            "N31_positive_evidence_re_admitted_to_RCAE",
            "RCAE_ecology_evidence_must_be_generated_fresh",
            "contract_re_admission_identity_requirements",
            "B_R_and_C2_composition_policy",
            "DR6_contract_only_means",
            "DR6_contract_only_does_not_mean",
            "A_globally_rejected",
            "A_contract_issue_blocked_by_failure",
            "A_not_selected_because_current_return_targets_field_state_semantics",
            "deferred_C2_native_implementation_exists",
            "deferred_native_work_is_N31_closeout_blocker",
            "future_native_lane_must_restart_from_DR0",
            "producer_DR5_may_not_seed_native_rung",
            "semantic_completeness_checks",
        }
    )

    return_manifest: dict[str, Any] = {
        "artifact_id": "n31_closeout_and_rcae_return_i12",
        "artifact_version": "1.1",
        "n31_candidate_schema_version": "n31_decay_candidate_schema_v2",
        "schema_change_record_id": "n31_pre_i1_mass_organization_mediation_normalization_v2",
        "n31_experiment_id": "N31_lgrc9v3_derived_decay_and_primitive_semantics",
        "n31_closeout_status": "N31-C6_exact_RCAE_return_bundle_complete",
        "graph_revision": I11_COMMIT_REVISION,
        "pygrc_version": source_authority["pygrc_version"],
        "reproduction_commands": [COMMAND],
        "theory_source_ids": theory_source_ids,
        "substrate_spec_source_ids": substrate_spec_source_ids,
        "pygrc_source_ids": pygrc_source_ids,
        "prior_experiment_source_ids": prior_experiment_source_ids,
        "rcae_demand_source_id": "rcae_n31_decay_primitive_handoff",
        "rcae_demand_source_ids": rcae_demand_source_ids,
        "paper_to_runtime_capability_dispositions": final_capability_dispositions,
        "candidate_dispositions": {row["candidate_id"]: row["candidate_disposition"] for row in disposition_rows},
        "primary_semantic_class_by_candidate": keyed(profiles, "semantic_class"),
        "representation_or_authority_class_by_candidate": keyed(profiles, "authority_lane"),
        "coherence_only_disposition": "D0a_native_DR2_foundation_no_autonomous_weakening",
        "d0a_representation_status": "represented_by_exact_source_current_route_projection",
        "d0a_projection_contract_id": "n31_i4_registered_route_projection_contract_v1",
        "d0_producer_role_audit_id": "n31_i8_D0_producer_role_audit",
        "d0_vs_b_redistribution_disposition": i11["d0_vs_b_redistribution"],
        "d0_subclass_by_candidate": {
            candidate_id: profiles_by_id[candidate_id]["semantic_class"]
            if candidate_id.startswith("D0")
            else "not_applicable_with_reason:not_D0"
            for candidate_id in CANDIDATE_IDS
        },
        "weakening_mode_by_candidate": trajectories,
        "route_mass_contract_by_candidate": route_mass_contracts,
        "route_organization_contract_by_candidate": route_organization_contracts,
        "organization_domain_by_candidate": organization_domains,
        "observed_diagnostic_domains_by_candidate": organization_domains,
        "load_bearing_organization_domain_by_candidate": load_bearing_domains,
        "mixed_domain_mediation_resolution_by_candidate": {
            candidate_id: (
                "resolved_to_" + load_bearing_domains[candidate_id]
                if "mixed" in organization_domains[candidate_id]
                else "not_applicable_with_reason:single_domain_or_nonmediating"
            )
            for candidate_id in CANDIDATE_IDS
        },
        "weakening_trajectory_class_by_candidate": trajectories,
        "causal_mediation_contract_by_candidate": mediation_contracts,
        "formation_packet_exclusion_status_by_candidate": {
            candidate_id: "passed_or_not_applicable_by_executed_family_scope"
            for candidate_id in CANDIDATE_IDS
        },
        "later_readout_probe_relation_by_candidate": {
            candidate_id: (
                "independent_local_readout_supported"
                if profiles_by_id[candidate_id]["later_readout_changed"]
                else "not_supported_or_not_applicable"
            )
            for candidate_id in CANDIDATE_IDS
        },
        "temporal_intervention_matching_status_by_candidate": {
            candidate_id: "passed_or_not_applicable_with_reason_by_family_scope"
            for candidate_id in CANDIDATE_IDS
        },
        "route_mass_decreased_by_candidate": keyed(profiles, "route_mass_decreased"),
        "route_organization_weakened_by_candidate": keyed(
            profiles, "native_route_organization_state_weakened"
        ),
        "organization_at_destination_transferred_by_candidate": {
            candidate_id: (
                "unsupported"
                if candidate_id == "B_conserved_export_policy"
                else "not_applicable_with_reason:not_conservative_destination_transfer"
            )
            for candidate_id in CANDIDATE_IDS
        },
        "native_route_organization_state_weakened_by_candidate": keyed(
            profiles, "native_route_organization_state_weakened"
        ),
        "derived_organization_observable_weakened_by_candidate": keyed(
            profiles, "derived_organization_observable_weakened"
        ),
        "derived_susceptibility_relation_weakened_by_candidate": keyed(
            profiles, "derived_susceptibility_relation_weakened"
        ),
        "later_readout_changed_by_candidate": keyed(profiles, "later_readout_changed"),
        "organization_mediated_readout_change_by_candidate": keyed(
            profiles, "organization_mediated_readout_change_supported"
        ),
        "organization_mediated_readout_change_supported_by_candidate": keyed(
            profiles, "organization_mediated_readout_change_supported"
        ),
        "organization_mediation_scope_by_candidate": keyed(
            profiles, "organization_mediation_scope"
        ),
        "ordinary_post_formation_flux_generated_by_candidate": {
            candidate_id: False for candidate_id in CANDIDATE_IDS
        },
        "added_export_policy_present_by_candidate": {
            candidate_id: candidate_id == "B_conserved_export_policy"
            for candidate_id in CANDIDATE_IDS
        },
        "export_policy_owner_by_candidate": {
            candidate_id: (
                "experiment_producer"
                if candidate_id == "B_conserved_export_policy"
                else "not_applicable_with_reason:no_export_policy"
            )
            for candidate_id in CANDIDATE_IDS
        },
        "producer_authors_aftereffect_by_candidate": {
            candidate_id: candidate_id in {
                "A_release_efficacy_attenuation",
                "B_conserved_export_policy",
                "C2_exact_history_susceptibility_closure",
            }
            for candidate_id in CANDIDATE_IDS
        },
        "d0_to_br_bridge_status": "not_tested",
        "added_mechanism_admission_reason_by_candidate": {
            candidate_id: (
                profiles_by_id[candidate_id]["semantic_fit"]
                if candidate_id in {
                    "A_release_efficacy_attenuation",
                    "B_conserved_export_policy",
                    "C2_exact_history_susceptibility_closure",
                }
                else "not_applicable_with_reason:not_added_mechanism"
            )
            for candidate_id in CANDIDATE_IDS
        },
        "post_formation_producer_call_policy_by_candidate": {
            "D0a_native_spatial_organization": "none_for_native_relation; perturbation_control_separate",
            "D0b_finite_window_derived_observable": "read_only_window_projection",
            "D0c_instantaneous_geometry_comparator": "read_only_comparator",
            "A_release_efficacy_attenuation": "producer_invokes_release_efficacy_policy",
            "B_conserved_export_policy": "producer_invokes_conservative_export_policy",
            "C2_exact_history_susceptibility_closure": "producer_derives_S_inserts_effective_geometry_and_schedules_packet",
        },
        "post_formation_producer_calls_by_candidate": {
            candidate_id: profiles_by_id[candidate_id]["producer_residue"]
            for candidate_id in CANDIDATE_IDS
        },
        "post_formation_state_mutating_producer_calls_by_candidate": {
            "D0a_native_spatial_organization": [],
            "D0b_finite_window_derived_observable": [],
            "D0c_instantaneous_geometry_comparator": [],
            "A_release_efficacy_attenuation": ["release_invocation"],
            "B_conserved_export_policy": ["export_schedule"],
            "C2_exact_history_susceptibility_closure": ["packet_schedule_from_effective_geometry"],
        },
        "producer_call_audit_status_by_candidate": {
            candidate_id: "passed_I8" if candidate_id.startswith("D0") else "passed_I10"
            for candidate_id in CANDIDATE_IDS
        },
        "decay_relation_ladder_rung": {
            candidate_id: profiles_by_id[candidate_id]["ladder_rungs"]
            for candidate_id in CANDIDATE_IDS
        },
        "n31_native_decay_classification": {
            "native_relation": "D0a_DR2",
            "exact_derived_observable": "D0b_DR3",
            "instantaneous_comparator": "D0c_DR1",
            "native_autonomous_weakening": "unsupported",
        },
        "native_D0a_relation_ceiling": "DR2",
        "native_autonomous_weakening_supported": False,
        "native_decay_provider_available": False,
        "n31_added_mechanism_decay_classifications": {
            "A": "producer_mediated_DR5_not_selected_current_demand",
            "B_R": "producer_mediated_DR5_with_DR6_contract_only",
            "C2": "producer_extension_DR5_relation_DR2_native_DR0_with_DR6_contract_only",
        },
        "n31_closeout_ladder_rung": "N31-C6_exact_RCAE_return_bundle_complete",
        "selected_primitive_ids": [],
        "derived_relation_ids": [
            "D0b_finite_window_derived_observable",
            "D0c_instantaneous_geometry_comparator",
            "C2_exact_history_susceptibility_relation",
        ],
        "effective_closure_ids": [c2_contract["contract_id"]],
        "runtime_extension_ids": [],
        "theory_extension_ids": [],
        "selection_or_nonselection_reason": (
            "No universal mechanism is selected. B-R and C.2 receive separate, "
            "semantics-conditioned reusable contracts; RCAE must select explicitly."
        ),
        "carrier_by_candidate": keyed(profiles, "carrier_authority"),
        "internal_time_by_candidate": keyed(profiles, "internal_time_ownership"),
        "invariants_by_candidate": keyed(profiles, "coherence_conservation"),
        "topology_scope_by_candidate": keyed(profiles, "topology_scope"),
        "timing_and_delay_surface_disposition_by_candidate": keyed(
            profiles, "internal_time_ownership"
        ),
        "native_api_by_candidate": {
            "D0a_native_spatial_organization": "existing_native_state_and_packet_runtime",
            "D0b_finite_window_derived_observable": "exact_derived_read_only_projection",
            "D0c_instantaneous_geometry_comparator": "existing_native_geometry_inputs",
            "A_release_efficacy_attenuation": "missing_native_release_lifecycle",
            "B_conserved_export_policy": "native_transport_present_export_policy_missing",
            "C2_exact_history_susceptibility_closure": "native_history_present_constitutive_hook_missing",
        },
        "producer_residue_by_candidate": keyed(profiles, "producer_residue"),
        "naturalization_debt_by_candidate": keyed(profiles, "naturalization_debt"),
        "native_upgrade_allowed_by_candidate": {
            candidate_id: False for candidate_id in CANDIDATE_IDS
        },
        "causal_transition_owner_by_candidate": {
            "D0a_native_spatial_organization": "native_runtime_for_formation_and_persistence",
            "D0b_finite_window_derived_observable": "native_history_plus_read_only_experiment_window",
            "D0c_instantaneous_geometry_comparator": "native_current_state_projection",
            "A_release_efficacy_attenuation": "experiment_producer_release_policy",
            "B_conserved_export_policy": "experiment_producer_export_policy_plus_native_transport",
            "C2_exact_history_susceptibility_closure": "exact_native_history_plus_experiment_constitutive_closure",
        },
        "candidate_specific_rung_qualifier_by_candidate": statuses,
        "reusable_contract_status_by_candidate": {
            candidate_id: value["reusable_contract_status"]
            for candidate_id, value in statuses.items()
        },
        "contract_semantics_rung_by_candidate": {
            candidate_id: value["contract_semantics_rung"]
            for candidate_id, value in statuses.items()
        },
        "executed_mechanism_rung_by_candidate": {
            candidate_id: value["executed_mechanism_rung"]
            for candidate_id, value in statuses.items()
        },
        "cross_context_reuse_evidence_by_candidate": {
            candidate_id: value["cross_context_reuse_evidence"]
            for candidate_id, value in statuses.items()
        },
        "DR6_contract_only_means": DR6_CONTRACT_ONLY_MEANS,
        "DR6_contract_only_does_not_mean": DR6_CONTRACT_ONLY_DOES_NOT_MEAN,
        "provider_contract_re_admission_eligible": recommendation[
            "provider_contract_re_admission_eligible"
        ],
        "N31_positive_evidence_re_admitted_to_RCAE": recommendation[
            "N31_positive_evidence_re_admitted_to_RCAE"
        ],
        "RCAE_ecology_evidence_must_be_generated_fresh": recommendation[
            "RCAE_ecology_evidence_must_be_generated_fresh"
        ],
        "contract_re_admission_identity_requirements": {
            "required_fields": recommendation["required_re_admission_identity_fields"],
            "n31_closeout_output_digest_source": recommendation[
                "n31_closeout_output_digest_source"
            ],
            "generic_decay_provider_selection_fails_closed": recommendation[
                "generic_decay_provider_selection_fails_closed"
            ],
            "route_bindings": {
                route_id: route
                for route_id, route in recommendation["semantic_routes"].items()
                if route_id in {
                    "conservative_coherence_redistribution",
                    "activity_indexed_susceptibility",
                }
            },
        },
        "B_R_and_C2_composition_policy": {
            "may_be_instantiated_together": recommendation[
                "B_R_and_C2_may_be_instantiated_together"
            ],
            "combined_effect_may_inherit_individual_DR5": recommendation[
                "combined_effect_may_inherit_individual_DR5"
            ],
            "combined_provider_is_new_composition_candidate": recommendation[
                "combined_provider_is_new_composition_candidate"
            ],
            "combined_provider_requires_separate_controls": recommendation[
                "combined_provider_requires_separate_controls"
            ],
            "required_attribution": recommendation[
                "combined_provider_required_attribution"
            ],
        },
        "A_globally_rejected": claim_register["A_globally_rejected"],
        "A_contract_issue_blocked_by_failure": claim_register[
            "A_contract_issue_blocked_by_failure"
        ],
        "A_not_selected_because_current_return_targets_field_state_semantics": claim_register[
            "A_not_selected_because_current_return_targets_field_state_semantics"
        ],
        "deferred_C2_native_implementation_exists": claim_register[
            "deferred_C2_native_implementation_exists"
        ],
        "deferred_native_work_is_N31_closeout_blocker": claim_register[
            "deferred_native_work_is_N31_closeout_blocker"
        ],
        "future_native_lane_must_restart_from_DR0": claim_register[
            "future_native_lane_must_restart_from_DR0"
        ],
        "producer_DR5_may_not_seed_native_rung": claim_register[
            "producer_DR5_may_not_seed_native_rung"
        ],
        "issued_contract_ids": [br_contract["contract_id"], c2_contract["contract_id"]],
        "restoration_identity_by_candidate": {
            "D0a_native_spatial_organization": "lgrc9v3_restoration_identity_v2",
            "D0b_finite_window_derived_observable": "native_v2_plus_exact_observable_reconstruction",
            "D0c_instantaneous_geometry_comparator": "native_current_state_identity_v1_sufficient_non_reset_sensitive",
            "A_release_efficacy_attenuation": "native_v2_plus_versioned_release_phase_state",
            "B_conserved_export_policy": "native_v2_plus_versioned_export_policy_state",
            "C2_exact_history_susceptibility_closure": "native_v2_plus_exact_rederived_S_no_stored_S",
        },
        "control_summary": {
            "D0_family": "I8_replay_and_controls_passed_at_lane_specific_rungs",
            "added_mechanism_families": "I10_complete_control_matrix_passed_no_failed_open_or_not_run_required_controls",
            "contract_generation": "no_new_scientific_execution",
        },
        "derived_cache_recomputation_status": source_authority[
            "derived_cache_recomputation_status"
        ],
        "execution_reconstruction_status": source_authority[
            "execution_reconstruction_status"
        ],
        "src_diff_empty_for_experiment_branch": source_authority[
            "src_diff_empty_for_experiment_branch"
        ],
        "protected_runtime_contract_diff_empty": source_authority[
            "protected_runtime_contract_diff_empty"
        ],
        "protected_runtime_contract_path_scope": protected_paths,
        "claim_ceiling": claim_register["claim_ceiling"],
        "blocked_relabels": BLOCKED_RELABELS,
        "p2_i3_return_recommendation": recommendation,
        "source_artifact_manifest": source_records + artifact_manifest,
        "semantic_completeness_checks": {},
    }

    missing_required_fields = sorted(required_return_fields - set(return_manifest))
    extra_required_field_count = len(set(return_manifest) - required_return_fields)
    all_artifact_sha = all(
        sha256_file(ROOT / row["path"]) == row["sha256"] for row in artifact_manifest
    )
    all_artifact_digest = all(
        load_json(ROOT / row["path"])["output_digest"] == row["output_digest"]
        and internal_output_digest_exact(load_json(ROOT / row["path"]))
        for row in artifact_manifest
    )

    allowed_empty_required_fields = {
        "selected_primitive_ids",
        "runtime_extension_ids",
        "theory_extension_ids",
        # This field is populated immediately after the bootstrap population audit.
        "semantic_completeness_checks",
    }
    required_field_population = {
        field: (
            True
            if field in allowed_empty_required_fields
            else required_value_is_semantically_populated(return_manifest.get(field))
        )
        for field in required_return_fields
    }
    expected_contract_binding = {
        "conservative_coherence_redistribution": {
            "candidate_id": "B_conserved_export_policy",
            "contract_artifact_path": relative(br_contract_path),
            "contract_artifact_sha256": sha256_file(br_contract_path),
            "contract_output_digest": br_contract["output_digest"],
            "executed_rung": "DR5_producer_mediated",
            "contract_only_rung": "DR6_contract_only",
        },
        "activity_indexed_susceptibility": {
            "candidate_id": "C2_exact_history_susceptibility_closure",
            "contract_artifact_path": relative(c2_contract_path),
            "contract_artifact_sha256": sha256_file(c2_contract_path),
            "contract_output_digest": c2_contract["output_digest"],
            "executed_rung": "DR5_producer_extension",
            "contract_only_rung": "DR6_contract_only",
        },
    }
    route_bindings = return_manifest["contract_re_admission_identity_requirements"][
        "route_bindings"
    ]
    all_contract_digests_resolve = all(
        all(binding.get(field) == expected for field, expected in expected_row.items())
        for route_id, expected_row in expected_contract_binding.items()
        for binding in [route_bindings[route_id]]
    )
    all_authority_ceilings_internally_consistent = (
        route_bindings["conservative_coherence_redistribution"]["authority_ceiling"]
        == "producer_mediated_B_R_DR5"
        and route_bindings["activity_indexed_susceptibility"]["authority_ceiling"]
        == "relation_DR2_producer_extension_DR5_native_DR0"
        and return_manifest["native_D0a_relation_ceiling"] == "DR2"
        and return_manifest["native_autonomous_weakening_supported"] is False
        and return_manifest["native_decay_provider_available"] is False
    )
    contract_source_evidence_exact = all(
        sha256_file(ROOT / source["path"]) == source["sha256"]
        and load_json(ROOT / source["path"])["output_digest"]
        == source["output_digest"]
        and internal_output_digest_exact(load_json(ROOT / source["path"]))
        for contract in [br_contract, c2_contract]
        for source in contract["source_evidence"]
    )
    all_selected_contracts_bind_source_evidence = (
        contract_source_evidence_exact
        and br_contract["source_evidence"][0]["output_digest"] == i10["output_digest"]
        and c2_contract["source_evidence"][0]["output_digest"] == i10["output_digest"]
        and br_contract["source_I11_output_digest"] == i11["output_digest"]
        and c2_contract["source_I11_output_digest"] == i11["output_digest"]
        and all_contract_digests_resolve
    )
    all_contract_conformance_fields_present = all(
        CONFORMANCE_REQUIRED_FIELDS <= set(contract["conformance_contract"])
        and all(
            required_value_is_semantically_populated(
                contract["conformance_contract"][field]
            )
            for field in CONFORMANCE_REQUIRED_FIELDS
        )
        for contract in [br_contract, c2_contract]
    )
    admitted_status_values = {
        "issued",
        "not_issued_native_foundation_not_decay_provider",
        "not_issued_diagnostic_only",
        "not_issued_instantaneous_diagnostic_only",
        "not_issued_retained_semantic_boundary",
    }
    all_enum_values_admitted = (
        all(
            row["reusable_contract_status"] in admitted_status_values
            and row["cross_context_reuse_evidence"] == "unsupported"
            for row in statuses.values()
        )
        and recommendation["return_status"]
        == "provider_contract_eligible_for_explicit_revision_bound_re_admission"
    )
    no_contradictory_positive_blocked_claim_pair = (
        all(value is False for value in claim_register["unsafe_claim_flags"].values())
        and return_manifest["N31_positive_evidence_re_admitted_to_RCAE"] is False
        and return_manifest["provider_contract_re_admission_eligible"] is True
        and return_manifest["native_autonomous_weakening_supported"] is False
        and return_manifest["native_decay_provider_available"] is False
    )
    semantic_completeness_checks = {
        "all_required_fields_nonplaceholder": all(required_field_population.values()),
        "all_enum_values_admitted": all_enum_values_admitted,
        "all_contract_digests_resolve": all_contract_digests_resolve,
        "all_authority_ceilings_internally_consistent": all_authority_ceilings_internally_consistent,
        "all_selected_contracts_bind_source_evidence": all_selected_contracts_bind_source_evidence,
        "all_contract_conformance_fields_present": all_contract_conformance_fields_present,
        "no_contradictory_positive_blocked_claim_pair": no_contradictory_positive_blocked_claim_pair,
    }
    return_manifest["semantic_completeness_checks"] = semantic_completeness_checks

    checks = [
        check("I1_I2_I8_I10_I11_source_identities_exact", all(row["identity_exact"] for row in source_records), source_records),
        check("I11_ready_for_I12", i11["n31_closeout_progress"]["ready_for_iteration_12_closeout_and_RCAE_return"], i11["n31_closeout_progress"]),
        check("all_six_candidate_dispositions_returned", set(return_manifest["candidate_dispositions"]) == set(CANDIDATE_IDS), sorted(return_manifest["candidate_dispositions"])),
        check("all_required_return_fields_present", not missing_required_fields, missing_required_fields),
        check("B_R_reusable_contract_issued", statuses["B_conserved_export_policy"]["reusable_contract_status"] == "issued", statuses["B_conserved_export_policy"]),
        check("C2_reusable_contract_issued", statuses["C2_exact_history_susceptibility_closure"]["reusable_contract_status"] == "issued", statuses["C2_exact_history_susceptibility_closure"]),
        check("contract_only_DR6_separate_from_executed_DR5", all(statuses[candidate]["contract_semantics_rung"] == "DR6_contract_only" and "DR5" in statuses[candidate]["executed_mechanism_rung"] for candidate in ["B_conserved_export_policy", "C2_exact_history_susceptibility_closure"]), statuses),
        check("cross_context_reuse_remains_unsupported", all(value["cross_context_reuse_evidence"] == "unsupported" for value in statuses.values()), statuses),
        check("native_D0a_relation_ceiling_preserved_without_native_decay_claim", return_manifest["native_D0a_relation_ceiling"] == "DR2" and return_manifest["native_autonomous_weakening_supported"] is False and return_manifest["native_decay_provider_available"] is False, return_manifest["n31_native_decay_classification"]),
        check("B_R_not_promoted_to_D0_R", return_manifest["d0_to_br_bridge_status"] == "not_tested" and claim_register["B_R_D0_R_equivalence_supported"] is False, return_manifest["d0_vs_b_redistribution_disposition"]),
        check("typed_weakening_fields_remain_separate", return_manifest["native_route_organization_state_weakened_by_candidate"]["D0a_native_spatial_organization"] is False and return_manifest["native_route_organization_state_weakened_by_candidate"]["D0b_finite_window_derived_observable"] == "unsupported" and return_manifest["derived_organization_observable_weakened_by_candidate"]["D0b_finite_window_derived_observable"] is True and return_manifest["route_mass_decreased_by_candidate"]["B_conserved_export_policy"] is True and return_manifest["native_route_organization_state_weakened_by_candidate"]["B_conserved_export_policy"] is True and return_manifest["organization_at_destination_transferred_by_candidate"]["B_conserved_export_policy"] == "unsupported" and return_manifest["native_route_organization_state_weakened_by_candidate"]["C2_exact_history_susceptibility_closure"] is False and return_manifest["derived_susceptibility_relation_weakened_by_candidate"]["C2_exact_history_susceptibility_closure"] is True, "D0a, D0b, B-R, and C2 typed boundaries"),
        check("RCAE_contract_re_admission_is_explicit_revision_bound_and_not_evidence_admission", recommendation["automatic_adoption_allowed"] is False and recommendation["provider_contract_re_admission_eligible"] is True and recommendation["N31_positive_evidence_re_admitted_to_RCAE"] is False and recommendation["RCAE_ecology_evidence_must_be_generated_fresh"] is True and recommendation["return_status"] == "provider_contract_eligible_for_explicit_revision_bound_re_admission", recommendation["required_RCAE_action"]),
        check("exact_per_contract_re_admission_identity_resolves", all_contract_digests_resolve and all_selected_contracts_bind_source_evidence, expected_contract_binding),
        check("B_R_C2_combination_is_new_controlled_composition", recommendation["B_R_and_C2_may_be_instantiated_together"] is True and recommendation["combined_effect_may_inherit_individual_DR5"] is False and recommendation["combined_provider_is_new_composition_candidate"] is True and recommendation["combined_provider_requires_separate_controls"] is True, recommendation["combined_provider_required_attribution"]),
        check("DR6_contract_only_is_mechanically_bounded", all(contract["DR6_contract_only_means"] == DR6_CONTRACT_ONLY_MEANS and contract["DR6_contract_only_does_not_mean"] == DR6_CONTRACT_ONLY_DOES_NOT_MEAN for contract in [br_contract, c2_contract]) and all_contract_conformance_fields_present, sorted(CONFORMANCE_REQUIRED_FIELDS)),
        check("A_retained_as_valid_nonselected_DR5_boundary", claim_register["A_globally_rejected"] is False and claim_register["A_contract_issue_blocked_by_failure"] is False and claim_register["A_not_selected_because_current_return_targets_field_state_semantics"] is True, statuses["A_release_efficacy_attenuation"]),
        check("deferred_C2_native_work_does_not_upgrade_or_block_N31", claim_register["deferred_C2_native_implementation_exists"] is True and claim_register["deferred_native_work_is_N31_closeout_blocker"] is False and claim_register["future_native_lane_must_restart_from_DR0"] is True and claim_register["producer_DR5_may_not_seed_native_rung"] is True, claim_register["naturalization_debt_by_candidate"] if "naturalization_debt_by_candidate" in claim_register else claim_register["remaining_debt_by_candidate"]["C2_exact_history_susceptibility_closure"]),
        check("semantic_return_completeness", all(semantic_completeness_checks.values()), semantic_completeness_checks),
        check("src_diff_empty", source_authority["src_diff_empty_for_experiment_branch"], PROTECTED_BASE_REVISION),
        check("protected_runtime_contract_diff_empty", source_authority["protected_runtime_contract_diff_empty"], protected_paths),
        check("all_generated_artifact_sha256_match", all_artifact_sha, artifact_manifest),
        check("all_generated_artifact_output_digests_exact", all_artifact_digest, artifact_manifest),
        check("unsafe_claim_flags_false", all(value is False for value in claim_register["unsafe_claim_flags"].values()), claim_register["unsafe_claim_flags"]),
        check("no_absolute_paths_in_return_manifest", no_absolute_paths(return_manifest), "repository-relative paths only"),
    ]
    failed_checks = [row["check_id"] for row in checks if not row["passed"]]

    trace_record = {
        "artifact_kind": "n31_i12_closeout_and_return_trace",
        "artifact_schema_version": "n31_i12_closeout_and_return_trace_v2",
        "source_records": source_records,
        "generated_artifact_manifest": artifact_manifest,
        "required_return_field_count": len(required_return_fields),
        "extra_return_field_count": extra_required_field_count,
        "missing_required_return_fields": missing_required_fields,
        "semantic_completeness_checks": semantic_completeness_checks,
        "checks": checks,
        "failed_checks": failed_checks,
    }
    trace_record["output_digest"] = digest_value(trace_record)

    payload = dict(return_manifest)
    payload.update(
        {
            "experiment": "N31_lgrc9v3_derived_decay_and_primitive_semantics",
            "iteration": "12_closeout_and_RCAE_return",
            "generated_at": GENERATED_AT,
            "script": SCRIPT_RELATIVE,
            "command": COMMAND,
            "status": "passed" if not failed_checks else "failed",
            "acceptance_state": (
                "accepted_N31_C6_exact_RCAE_return_bundle_complete"
                if not failed_checks
                else "blocked_N31_I12_return_bundle"
            ),
            "artifact_manifest": artifact_manifest,
            "required_return_field_count": len(required_return_fields),
            "missing_required_return_fields": missing_required_fields,
            "checks": checks,
            "failed_checks": failed_checks,
        }
    )
    payload["output_digest"] = digest_value(payload)
    return payload, trace_record


def write_report(payload: dict[str, Any]) -> None:
    checks = "\n".join(
        f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 12 - Closeout And RCAE Return

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
n31_closeout_ladder_rung = {payload['n31_closeout_ladder_rung']}
native_D0a_relation_ceiling = DR2
native_autonomous_weakening_supported = false
native_decay_provider_available = false
B-R executed / contract = DR5 producer-mediated / DR6 contract-only
C.2 executed / relation / native / contract = DR5 / DR2 / DR0 / DR6 contract-only
cross_context_reuse_evidence = unsupported
automatic_RCAE_adoption = false
provider_contract_re_admission_eligible = true
N31_positive_evidence_re_admitted_to_RCAE = false
RCAE_ecology_evidence_must_be_generated_fresh = true
```

N31 closes with two reusable but non-ranked semantic contracts. B-R is the
contract for conservative coherence redistribution to an explicit destination,
with attributable local route-mass and route-contrast weakening. It does not
claim that route organization is transported to the destination. C.2 is the contract for activity-indexed
susceptibility or effective-geometry relaxation derived from exact native
history. They answer different demands and do not become one general decay law.

## Executed Evidence Versus Contract Semantics

The contract rung and execution rung are deliberately separate:

```text
B-R:
  reusable_contract_status = issued
  contract_semantics_rung = DR6_contract_only
  executed_mechanism_rung = DR5_producer_mediated
  cross_context_reuse_evidence = unsupported

C.2:
  reusable_contract_status = issued
  contract_semantics_rung = DR6_contract_only
  executed_mechanism_rung = DR5_producer_extension
  relation_carrier_rung = DR2
  native_runtime_rung = DR0
  cross_context_reuse_evidence = unsupported
```

`DR6_contract_only` means `reusable_testable_semantics_and_acceptance_contract`.
Each contract binds admissible and forbidden inputs, carrier/producer/native
executor authority, formation and weakening conditions, later readout,
accounting invariants, restoration and duplicate/refusal behavior, topology,
transfer limits, controls, claim ceiling, and consumer obligations. It does not
mean cross-context execution, native implementation, ecology evidence, provider
adoption, or a general decay law.

## Native And Derived Boundary

Native D0a remains a formation-and-persistence foundation at `DR2`; ordinary
autonomous weakening was not found. D0b remains an exact finite-window fading
observable at `DR3` without causal mediation. D0c remains an instantaneous
comparator at `DR1`. I12 keeps native route-state weakening, derived-observable
weakening, and derived-susceptibility weakening as separate typed results.

## RCAE Return

RCAE P2-I3 may now perform explicit, revision-bound **provider-contract**
re-admission. N31 positive evidence is not re-admitted as ecology evidence;
RCAE must generate that evidence fresh. It must choose the semantics it needs:

```text
conservative coherence redistribution with explicit destination -> B-R contract
activity-indexed susceptibility/effective geometry -> C.2 contract
release-expression attenuation -> A boundary, no current reusable contract
ordinary autonomous native D0 decay -> unsupported; preserve blocker
```

The admission record must copy this closeout's exact `output_digest` and bind
the selected contract path, SHA-256, internal digest, candidate ID, semantic
route, authority ceiling, executed rung, contract-only rung, producer residue,
naturalization debt, controls, and forbidden claims. A generic
`selected_candidate = decay_provider` record fails closed.

N31 does not choose on RCAE's behalf. RCAE owns the provider admission,
topology and encounter design, ecology-side controls, and any later trail or
stigmergic-field claim. B-R and C.2 may be instantiated together, but the result
is a new composition candidate. It inherits neither individual `DR5` result and
must separately attribute B-R redistribution, C.2 susceptibility change, and
their interaction or interference.

## Ownership And Debt

B-R uses native coherence and conservative packet transport, while an external
policy still owns export eligibility, amount, timing, and destination. Candidate
A remains a valid producer-mediated `DR5` expression mechanism; it is not
globally rejected and was not selected because this return targets field-state
semantics. C.2 uses
exact serialized native packet history, but an external closure still derives
and inserts effective geometry and schedules transport. Neither producer result
upgrades native support. C.2 native implementation remains deferred but does not
block N31 closeout. Any future native lane restarts from `DR0`; producer `DR5`
cannot seed its rung.

The return gate is semantic as well as numeric: all required fields are
non-placeholder or explicitly allowed empty, enum values are admitted, contract
digests resolve, authority ceilings agree, contracts bind source evidence, and
no positive/blocked claim pair contradicts itself.

## Checks

| Check | Passed |
| --- | ---: |
{checks}

## Claim Ceiling

```text
{payload['claim_ceiling']}
```

This is not one general decay law, native autonomous decay, ordinary D0-R,
memory, stigmergy, communication, coordination, ecology, learning, agency,
selfhood, sentience, organism/life, native support, Phase 8 completion, or
automatic RCAE adoption.

## Reproduction

```bash
{payload['command']}
```

Output digest: `{payload['output_digest']}`
""",
        encoding="utf-8",
    )


def main() -> None:
    payload, trace_record = build()
    TRACE.write_text(canonical_json(trace_record), encoding="utf-8")
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    print(
        canonical_json(
            {
                "status": payload["status"],
                "acceptance_state": payload["acceptance_state"],
                "output": relative(OUTPUT),
                "report": relative(REPORT),
                "output_digest": payload["output_digest"],
                "failed_checks": payload["failed_checks"],
            }
        ),
        end="",
    )


if __name__ == "__main__":
    main()
