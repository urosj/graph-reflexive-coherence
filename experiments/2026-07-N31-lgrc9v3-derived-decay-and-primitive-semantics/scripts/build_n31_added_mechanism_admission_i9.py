#!/usr/bin/env python3
"""Build N31 Iteration 9 added-mechanism admission artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i9_added_mechanism_admission_artifacts"
CONTRACT_BUNDLE = ARTIFACT_DIR / "n31_i9_candidate_contract_bundle.json"
I8_REVISION_LINEAGE = ARTIFACT_DIR / "n31_i8_revision_lineage_r1.json"
OUTPUT = OUTPUTS / "n31_added_mechanism_admission_i9.json"
REPORT = REPORTS / "n31_added_mechanism_admission_i9.md"
I2 = OUTPUTS / "n31_semantic_representation_control_schema_i2.json"
I8 = OUTPUTS / "n31_d0_replay_controls_classification_i8.json"
SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_added_mechanism_admission_i9.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
GOVERNANCE_BASE_REVISION = "33951a8eebcd4d03e32581aa189eaf81c71bb8f6"
SOURCE_IDENTITIES = {
    I2: (
        "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf",
        "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6",
    ),
    I8: (
        "bf7d5eb98ab6b84e16a86fe4eba662e9b99ac648abd9b9490dcc6598c40cb5d8",
        "28a3d8b9e98b23ebdc7d852e9264fd802dad9bb45d48097d40efa2a0b1c9dc61",
    ),
}
PROTECTED_PATHS = (
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
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
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


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def git_diff_empty(path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", GOVERNANCE_BASE_REVISION, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def source_record(path: Path) -> dict[str, Any]:
    value = load_json(path)
    expected_digest, expected_sha = SOURCE_IDENTITIES[path]
    actual_sha = sha256_file(path)
    return {
        "path": relative(path),
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


def topology(
    contract_id: str,
    nodes: list[int],
    edges: list[dict[str, Any]],
    roles: dict[str, int],
    route_support: list[int],
    route_boundary: list[int],
    source_region: list[int],
    receiver_region: list[int],
    transfer_scope: str,
) -> dict[str, Any]:
    node_payloads = [
        {
            "node_id": node_id,
            "payload": {
                "fixture_role": next(
                    role for role, role_node_id in roles.items() if role_node_id == node_id
                )
            },
        }
        for node_id in nodes
    ]
    executable_identity = {
        "node_ids": nodes,
        "edge_ids": [edge["edge_id"] for edge in edges],
        "node_payloads": node_payloads,
        "edge_payloads": edges,
        "role_to_node_id": roles,
    }
    return {
        "topology_contract_id": contract_id,
        "topology_signature": digest_value(executable_identity),
        "canonical_topology_digest": digest_value(executable_identity),
        **executable_identity,
        "node_roles": roles,
        "registered_route_support": route_support,
        "registered_route_boundary": route_boundary,
        "source_region": source_region,
        "receiver_region": receiver_region,
        "mutable_topology_policy": "frozen_no_topology_mutation",
        "transfer_scope": transfer_scope,
        "independent_fixture_reconstruction_required": True,
        "topology_identity_match_rule": (
            "reconstructed_canonical_topology_digest_must_equal_frozen_digest"
        ),
    }


def edge(
    edge_id: int,
    source_node_id: int,
    source_port_id: int,
    target_node_id: int,
    target_port_id: int,
    relation: str,
) -> dict[str, Any]:
    return {
        "edge_id": edge_id,
        "source_node_id": source_node_id,
        "source_port_id": source_port_id,
        "target_node_id": target_node_id,
        "target_port_id": target_port_id,
        "orientation": "canonical_source_to_target",
        "delay": 1.0,
        "conductance": 1.0,
        "payload": {"fixture_relation": relation},
    }


def input_record(
    path: str,
    role: str,
    read_phase: str,
    *,
    historical_depth: str = "current",
    load_bearing: bool = True,
    forbidden_adjacent_inputs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "input_path": path,
        "input_role": role,
        "read_phase": read_phase,
        "required_or_optional": "required",
        "historical_depth": historical_depth,
        "load_bearing": load_bearing,
        "forbidden_adjacent_inputs": forbidden_adjacent_inputs or [],
    }


def freeze_execution_boundary(
    candidate: dict[str, Any],
    i2: dict[str, Any],
    allowlist: list[dict[str, Any]],
) -> None:
    controls = i2["controls"]
    semantic = candidate["primary_semantic_class"]
    lane_specific = list(controls[f"candidate_{semantic}_controls"])
    inherited = list(
        dict.fromkeys(
            controls["common_active_nulls"]
            + controls["D0_controls"]
            + controls["schema_relation_controls"]
        )
    )
    complete = list(dict.fromkeys(inherited + lane_specific))
    candidate.pop("control_ids", None)
    candidate["source_current_inputs"] = [row["input_path"] for row in allowlist]
    candidate["source_current_input_allowlist"] = allowlist
    candidate["source_current_input_policy"] = {
        "unlisted_input_read_status": "blocks_candidate_row",
        "global_state_scan_allowed": False,
        "labels_as_causal_inputs_allowed": False,
        "outcome_inspection_allowed": False,
        "allowlist_digest": digest_value(allowlist),
    }
    candidate["lane_specific_control_ids"] = lane_specific
    candidate["inherited_required_control_ids"] = inherited
    candidate["complete_control_ids"] = complete
    candidate["complete_control_set_digest"] = digest_value(complete)
    candidate["candidate_specific_regeneration_required"] = True
    candidate["direct_I3_null_consumption_allowed"] = False
    candidate["direct_I3_null_consumption_count"] = 0
    candidate["control_resolution_status"] = (
        "not_run_pending_candidate_specific_regeneration_and_execution"
    )


def common_lane(
    candidate_id: str,
    semantic_class: str,
    authority: str,
    execution_iteration: str,
    later_ceiling: str,
    rung_qualifier: str,
    causal_owner: str,
    producer_residue: list[str],
    naturalization_debt: list[str],
) -> dict[str, Any]:
    return {
        "lane_id": "added_mechanism",
        "candidate_id": candidate_id,
        "candidate_schema_version": "n31_decay_candidate_schema_v2",
        "schema_change_record_id": "n31_i2_schema_freeze",
        "source_iteration": "I9",
        "primary_semantic_class": semantic_class,
        "representation_or_authority_class": authority,
        "candidate_disposition": "not_executed",
        "execution_decision": "execute",
        "execution_iteration": execution_iteration,
        "current_decay_relation_ladder_rung": "DR0",
        "current_rung_reason": "admission_contract_only_no_candidate_runtime_evidence",
        "highest_later_eligible_ceiling": later_ceiling,
        "candidate_specific_rung_qualifier": rung_qualifier,
        "causal_transition_owner": causal_owner,
        "producer_residue": producer_residue,
        "naturalization_debt": naturalization_debt,
        "reusable_contract_status": "not_tested_pending_I10_through_I12",
        "native_upgrade_allowed": False,
        "producer_DR5_or_DR6_implies_native_DR5_or_DR6": False,
        "source_current_inputs": [],
        "positive_candidate_evidence_opened": False,
        "row_decision": "not_applicable",
        "row_decision_scope_reason": "I9_admission_only_before_candidate_execution",
    }


def build_candidate_contracts(i2: dict[str, Any]) -> dict[str, Any]:
    controls = i2["controls"]
    candidate_a = {
        **common_lane(
            "A_release_efficacy_attenuation",
            "A",
            "producer_mediated",
            "I9-A",
            "DR5_expression_attenuation_not_field_state_decay",
            "release_efficacy_expression_attenuation",
            "registered_release_policy_producer",
            [
                "release_phase_state_and_transition_owned_by_experiment_producer",
                "producer_selects_new_packet_amount_at_creation",
            ],
            [
                "native_release_phase_state_missing",
                "native_packet_creation_efficacy_surface_missing",
            ],
        ),
        "execution_rationale": "comparative_semantic_control_under_D0_insufficiency",
        "topology": topology(
            "n31_i9_A_three_node_release_path_v1",
            [0, 1, 2],
            [
                edge(0, 0, 1, 1, 1, "formation_source_to_release_source"),
                edge(1, 1, 2, 2, 1, "release_source_to_release_receiver"),
            ],
            {
                "formation_source": 0,
                "release_source": 1,
                "release_receiver": 2,
            },
            [0, 1],
            [1],
            [1],
            [2],
            "new_packet_creation_then_native_packet_transport",
        ),
        "role_contract": {
            "formation_source_node_id": 0,
            "release_source_node_id": 1,
            "release_receiver_node_id": 2,
            "source_debit_owner_node_id": 1,
        },
        "carrier_definition": "newly_created_LGRC_coherence_packet",
        "continuation_state_definition": (
            "complete_LGRC_state_plus_registered_release_phase_closure_state"
        ),
        "equation_or_relation": {
            "equation_or_relation_id": "n31_A_release_efficacy_v1",
            "packet_creation_relation": "q_created = q_requested * epsilon_A(phase)",
            "epsilon_A_by_phase": {"fresh": 1.0, "aged": 0.5},
            "release_policy_schema": "n31_A_release_efficacy_policy_v1",
            "release_policy_identity": digest_value(
                {
                    "release_policy_schema": "n31_A_release_efficacy_policy_v1",
                    "epsilon_A_by_phase": {"fresh": 1.0, "aged": 0.5},
                    "packet_creation_relation": (
                        "q_created = q_requested * epsilon_A(phase)"
                    ),
                }
            ),
            "in_flight_packet_relation": "q_in_flight(t+1) = q_in_flight(t)",
            "unreleased_relation": "q_unreleased = q_requested - q_created",
            "outcome_tuning_allowed": False,
        },
        "units_by_state": {
            "q_requested": "coherence",
            "q_created": "coherence",
            "epsilon_A": "dimensionless",
            "phase": "registered_discrete_phase",
        },
        "internal_time_contract": {
            "internal_time_owner": "registered_release_phase_closure",
            "internal_time_state_path": "candidate_closure.release_phase_receipt_count",
            "amount_policy_state_path": "candidate_closure.release_phase",
            "receipt_count_input_role": "validation_only_not_amount_selecting",
            "malformed_phase_count_pair_behavior": "refuse_release_evaluation",
            "internal_time_units": "qualifying_event_receipts",
            "internal_time_advance_event": "n31_A_exact_formation_arrival",
            "internal_time_advance_equation": (
                "phase=fresh before first exact receipt; phase=aged after exactly one receipt"
            ),
            "wall_clock_excluded": True,
            "snapshot_path": "candidate_closure.release_phase",
        },
        "qualifying_phase_event_contract": {
            "event_contract_id": "n31_A_exact_formation_arrival_v1",
            "event_kind": "lgrc9v3_packet_arrival",
            "edge_id": 0,
            "source_node_id": 0,
            "target_node_id": 1,
            "lineage_id": "n31_A_formation_lineage",
            "minimum_occurrence_count": 1,
            "maximum_occurrence_count": 1,
            "callback_order": "after_committed_arrival_before_release_decision",
            "unrelated_events_advance_phase": False,
        },
        "fresh_aged_branch_match_contract": {
            "matched_fields": [
                "q_requested",
                "release_source_C_before",
                "canonical_topology_digest",
                "event_queue_excluding_qualifying_event",
                "release_receiver_node_id",
                "complete_LGRC_continuation_state",
            ],
            "only_allowed_difference_at_release_decision": (
                "registered_release_phase_closure_bundle"
            ),
        },
        "update_phase": "packet_creation_only_never_in_flight",
        "invariant_contract": {
            "invariant_id": "n31_A_total_coherence_with_unreleased_source_v1",
            "quantity": "node_plus_in_flight_coherence",
            "system_boundary": "all_three_nodes_plus_in_flight_packets",
            "relation": (
                "C_release_source_before - C_release_source_after == q_created "
                "== in_flight_packet_amount == eventual_receiver_credit"
            ),
            "unreleased_coherence_remains_at_source": True,
            "q_unreleased_semantics": "derived_counterfactual_not_stored_state",
            "only_q_created_is_debited": True,
            "separate_unreleased_reservoir_created": False,
            "release_source_C_before_after_required": True,
            "tolerance": 1e-12,
        },
        "control_ids": controls["candidate_A_controls"],
        "claim_ceiling": "DR5_expression_attenuation_not_field_state_decay",
        "blocked_relabels": [
            "field_state_decay",
            "native_decay",
            "in_flight_attenuation",
            "native_memory",
        ],
    }
    candidate_b = {
        **common_lane(
            "B_conserved_source_leakage",
            "B",
            "producer_mediated",
            "I9-B",
            "DR6_after_DR5_and_reusable_B_R_contract",
            "B_R_conserved_export_policy",
            "registered_route_local_export_policy_producer",
            [
                "producer_owns_export_eligibility_amount_time_and_destination",
                "native_LGRC_only_executes_conservative_packet_transport",
            ],
            [
                "native_route_local_export_policy_missing",
                "ordinary_D0_R_bridge_unproven",
            ],
        ),
        "execution_rationale": "registered_D0_R_to_B_R_bridge_and_conserved_export_test",
        "topology": topology(
            "n31_i9_B_four_node_export_and_readout_v1",
            [0, 1, 2, 3],
            [
                edge(0, 0, 1, 1, 1, "formation_source_to_leakage_source"),
                edge(1, 1, 2, 2, 1, "leakage_source_to_export_destination"),
                edge(2, 1, 3, 3, 1, "leakage_source_to_later_readout"),
            ],
            {
                "formation_source": 0,
                "leakage_source": 1,
                "export_destination": 2,
                "later_readout_target": 3,
            },
            [0, 1],
            [1],
            [1],
            [2],
            "route_local_export_to_explicit_destination_excluded_from_readout_path",
        ),
        "role_contract": {
            "formation_source_node_id": 0,
            "leakage_source_node_id": 1,
            "export_destination_node_id": 2,
            "later_readout_target_node_id": 3,
        },
        "later_readout_path": [0, 1, 3],
        "export_destination_excluded_from_later_readout_path": True,
        "carrier_definition": "LGRC_coherence_packet_to_explicit_destination",
        "continuation_state_definition": (
            "complete_LGRC_state_plus_registered_one_shot_export_policy_receipt"
        ),
        "equation_or_relation": {
            "equation_or_relation_id": "n31_B_bounded_export_v1",
            "emission_relation": (
                "q_emit = min(q_cap, max(0, C_leakage_source - C_floor))"
            ),
            "q_cap": 0.04,
            "C_floor": 0.20,
            "trigger": "first_registered_local_source_event_after_formation",
            "global_scheduler_allowed": False,
            "outcome_tuning_allowed": False,
        },
        "units_by_state": {
            "q_emit": "coherence",
            "q_cap": "coherence",
            "C_leakage_source": "coherence",
            "C_floor": "coherence",
        },
        "internal_time_contract": {
            "internal_time_owner": "native_LGRC_event_queue_with_local_export_callback",
            "internal_time_state_path": "event_queue.registered_local_source_event",
            "internal_time_units": "processed_native_events",
            "internal_time_advance_event": "registered_local_source_event",
            "internal_time_advance_equation": "one_shot_export_eligibility_after_formation",
            "wall_clock_excluded": True,
            "snapshot_path": "candidate_closure.export_policy_receipt",
        },
        "one_shot_trigger_contract": {
            "trigger_contract_id": "n31_B_first_local_arrival_after_formation_v1",
            "event_kind": "lgrc9v3_packet_arrival",
            "edge_id": 0,
            "source_node_id": 0,
            "target_node_id": 1,
            "lineage_id": "n31_B_formation_lineage",
            "callback_phase": "after_committed_arrival_before_export_packet_creation",
            "eligibility_consumption": "atomic_on_first_qualifying_attempt",
            "second_trigger_behavior": "refused_from_restored_one_shot_receipt",
            "receipt_snapshot_path": "candidate_closure.export_policy_receipt",
            "receipt_restoration_required": True,
            "zero_emission_behavior": "consume_receipt_and_record_zero_emission",
            "failed_emission_retry_behavior": "no_retry_without_new_versioned_contract",
        },
        "organization_contract": {
            "organization_observable_id": "n31_B_route_source_contrast_v1",
            "organization_domain": "spatial_route_distribution",
            "observable_relation": "O_B = C_leakage_source - C_formation_source",
            "stronger_weaker_ordering": "larger_O_B_is_stronger",
            "formed_organization_minimum": 0.04,
            "minimum_weakening_delta": 0.01,
            "post_export_rule": "O_B_post <= O_B_formed - minimum_weakening_delta",
            "route_mass_observable": "M_B = C_formation_source + C_leakage_source",
            "mass_loss_is_not_organization_weakening": True,
            "mass_loss_substitution_control": (
                "matched_route_mass_loss_without_source_contrast_change"
            ),
            "matched_fixture_fields": [
                "canonical_topology_digest",
                "formed_route_mass",
                "formed_O_B",
                "event_queue",
                "readout_probe",
            ],
        },
        "destination_isolation_contract": {
            "automatic_return_packets_allowed_before_readout": False,
            "destination_originated_events_allowed_before_readout": False,
            "shared_selector_reads_destination_state": False,
            "destination_clamp_pair_required": True,
            "destination_clamp_rule": (
                "vary_destination_state_after_credit_while_matching_source_route_and_queue; "
                "later_readout_must_remain_unchanged"
            ),
            "event_trace_no_return_required": True,
            "derived_geometry_dependency_control_required": True,
            "isolation_failure_blocks_DR4_plus": True,
        },
        "update_phase": "registered_local_source_event_before_packet_creation",
        "invariant_contract": {
            "invariant_id": "n31_B_source_packet_destination_conservation_v1",
            "quantity": "node_plus_in_flight_coherence",
            "system_boundary": "all_four_nodes_plus_in_flight_packets",
            "relation": (
                "C_leakage_source_before - C_leakage_source_after == packet_amount "
                "== export_destination_credit"
            ),
            "explicit_destination_required": True,
            "tolerance": 1e-12,
        },
        "export_ownership": {
            "d0_subclass": "not_applicable_candidate_B",
            "B_R_subtype": True,
            "ordinary_post_formation_flux_generated": "not_run",
            "added_export_policy_present": True,
            "export_policy_owner": "experiment_producer",
            "d0_to_br_bridge_status": "not_tested",
        },
        "control_ids": controls["candidate_B_controls"],
        "claim_ceiling": "DR6_reusable_B_R_contract_not_native_D0_R",
        "blocked_relabels": [
            "ordinary_D0_R",
            "coherence_destruction",
            "native_decay",
            "global_emission_scheduler",
        ],
    }
    candidate_c = {
        **common_lane(
            "C_route_susceptibility_relaxation",
            "C",
            "effective_non_markovian_closure",
            "I9-C",
            "DR6_after_DR5_and_reusable_susceptibility_contract",
            "closure_owned_route_susceptibility_relaxation",
            "versioned_susceptibility_closure",
            [
                "independent_susceptibility_state_owned_by_effective_closure",
                "closure_updates_and_relaxes_state_then_modulates_local_conductance",
            ],
            [
                "native_susceptibility_state_missing",
                "native_update_and_relaxation_surface_missing",
                "susceptibility_cost_not_naturalized_into_RC_coherence",
            ],
        ),
        "execution_rationale": "direct_missing_autonomous_weakening_transition_test",
        "topology": topology(
            "n31_i9_C_three_node_susceptible_route_v1",
            [0, 1, 2],
            [
                edge(0, 0, 1, 1, 1, "source_to_susceptible_route"),
                edge(1, 1, 2, 2, 1, "susceptible_route_to_local_readout"),
            ],
            {
                "source": 0,
                "susceptible_route_node": 1,
                "local_readout_receiver": 2,
            },
            [0, 1],
            [1],
            [0, 1],
            [2],
            "route_local_susceptibility_modulates_registered_local_conductance",
        ),
        "carrier_definition": "versioned_route_local_susceptibility_state_S_1_2",
        "continuation_state_definition": (
            "complete_LGRC_state_plus_versioned_susceptibility_closure_state"
        ),
        "equation_or_relation": {
            "equation_or_relation_id": "n31_C_susceptibility_relaxation_v1",
            "formation_relation": "S_after_use = min(S_max, S + alpha * q_use)",
            "relaxation_relation": "S_next = S_floor + rho * (S - S_floor)",
            "readout_relation": "g_effective = S * g_native",
            "S_floor": 0.5,
            "S_max": 1.0,
            "alpha": 1.0,
            "rho": 0.75,
            "outcome_tuning_allowed": False,
        },
        "units_by_state": {
            "S": "dimensionless_conductance_multiplier",
            "q_use": "coherence",
            "g_native": "native_conductance_units",
            "g_effective": "native_conductance_units",
        },
        "internal_time_contract": {
            "internal_time_owner": "susceptibility_closure_advanced_by_declared_LGRC_events",
            "internal_time_state_path": "candidate_closure.processed_progression_event_count",
            "internal_time_units": "declared_disjoint_native_progression_events",
            "internal_time_advance_event": "declared_disjoint_LGRC_progression_event",
            "internal_time_advance_equation": "one_relaxation_step_per_declared_event",
            "wall_clock_excluded": True,
            "snapshot_path": "candidate_closure.susceptibility_state",
        },
        "update_phase": "after_registered_route_use_then_before_later_local_readout",
        "executable_conductance_path": {
            "closure_state_path": "candidate_closure.S_by_edge[1]",
            "native_state_path_read": "LGRC9V3RuntimeState.base_state.base_conductance[1]",
            "native_state_path_written": "LGRC9V3RuntimeState.base_state.base_conductance[1]",
            "mirrored_port_edge_path": "LGRC9V3RuntimeState.base_state.port_edges[1].conductance",
            "state_api_path": "LGRC9V3.get_state/LGRC9V3.set_state",
            "executable_operation_sequence": [
                "deepcopy_LGRC9V3_get_state",
                "compute_base_conductance_with_frozen_native_evolution_and_modes",
                "read_g_native_on_edge_1",
                "write_S_times_g_native_to_base_conductance_and_port_edge_1",
                "compute_potential_with_same_frozen_native_evolution",
                "compute_flux_with_same_frozen_native_evolution",
                "LGRC9V3_set_state",
                "restore_original_native_conductance_before_unqualified_step",
            ],
            "callback_phase": (
                "after_pygrc.models.grc_9_v3_runtime.compute_base_conductance_"
                "before_compute_potential"
            ),
            "write_relation": "g_effective = S * g_native",
            "native_operation_consumers": [
                "pygrc.models.grc_9_v3_runtime.compute_potential",
                "pygrc.models.grc_9_v3_runtime.compute_flux",
            ],
            "expected_future_difference": (
                "same_native_state_and_probe_with_different_S_produces_different_"
                "potential_or_flux_on_edge_1"
            ),
            "original_native_conductance_restoration_required": True,
            "ordinary_LGRC9V3_step_compatible_without_hook": False,
            "missing_runtime_hook_debt": (
                "normal_step_recomputes_base_conductance_before_consumption; "
                "closure_must_own_the_partial_native_pipeline_order"
            ),
            "packet_amount_scaling_allowed": False,
            "export_scheduling_allowed": False,
            "label_only_write_allowed": False,
        },
        "matched_branch_contract": {
            "comparison_phase": "before_closure_application",
            "matched_fields": [
                "complete_LGRC_state",
                "event_queue",
                "native_base_conductance",
                "canonical_topology_digest",
                "later_native_probe",
            ],
            "only_allowed_pre_application_difference": "restored_candidate_closure_S",
            "post_application_LGRC_state_described_as_matched": False,
        },
        "non_coherence_state_contract": {
            "units": "dimensionless_conductance_multiplier",
            "bounds": [0.5, 1.0],
            "susceptibility_update_magnitude": "absolute_delta_S",
            "susceptibility_update_ledger_role": "report_only_noncausal",
            "susceptibility_update_ledger_in_restoration_identity": False,
            "susceptibility_update_ledger_affects_future_behavior": False,
            "invariant": "S_floor <= S <= S_max",
            "coherence_quantity_claimed": False,
            "effective_non_markovian_relative_to": "LGRC_state_alone",
            "composed_LGRC_plus_S_may_be_markovian": True,
        },
        "invariant_contract": {
            "invariant_id": "n31_C_coherence_and_susceptibility_bounds_v1",
            "quantity": "coherence_plus_separate_bounded_susceptibility_state",
            "system_boundary": "all_three_nodes_plus_in_flight_packets_plus_closure_state",
            "coherence_relation": "node_plus_in_flight_coherence_before == after",
            "susceptibility_relation": "S_floor <= S <= S_max",
            "tolerance": 1e-12,
        },
        "restoration_contract": {
            "LGRC_current_state_schema": "lgrc9v3_restoration_identity_v1",
            "LGRC_reset_sensitive_schema": "lgrc9v3_restoration_identity_v2",
            "candidate_state_schema": "n31_candidate_C_susceptibility_identity_v1",
            "composed_identity_required": True,
            "same_complete_C_different_S_intervention_required": True,
        },
        "control_ids": controls["candidate_C_controls"],
        "claim_ceiling": "DR6_reusable_effective_susceptibility_closure_not_native_memory",
        "blocked_relabels": [
            "coherence_only_D0",
            "native_memory",
            "native_susceptibility",
            "free_unaccounted_noncoherence_state",
        ],
    }
    freeze_execution_boundary(
        candidate_a,
        i2,
        [
            input_record(
                "candidate_closure.release_phase",
                "registered_release_phase",
                "immediately_before_packet_creation",
                historical_depth="restored_current_receipt_state",
                forbidden_adjacent_inputs=[
                    "global_processed_event_count",
                    "wall_clock",
                    "unrelated_event_history",
                ],
            ),
            input_record(
                "candidate_closure.release_phase_receipt_count",
                "phase_receipt_count_invariant_validation_only",
                "immediately_before_packet_creation_validation",
                historical_depth="one_exact_registered_event",
                load_bearing=False,
                forbidden_adjacent_inputs=[
                    "epsilon_selection",
                    "q_created_selection",
                ],
            ),
            input_record(
                "candidate_policy.q_requested",
                "requested_new_packet_amount",
                "packet_creation",
                forbidden_adjacent_inputs=["outcome_selected_packet_amount"],
            ),
            input_record(
                "LGRC9V3RuntimeState.base_state.nodes[1].coherence",
                "release_source_C",
                "packet_creation_precondition",
                forbidden_adjacent_inputs=["global_node_scan", "route_label"],
            ),
            input_record(
                "candidate_policy.epsilon_A_by_phase",
                "frozen_release_efficacy_table",
                "packet_creation",
                historical_depth="versioned_policy_configuration",
                forbidden_adjacent_inputs=["outcome_tuned_epsilon"],
            ),
            input_record(
                "candidate_policy.release_policy_identity",
                "release_policy_configuration_binding",
                "fixture_admission",
                historical_depth="versioned_policy_configuration",
                load_bearing=False,
            ),
            input_record(
                "candidate_topology.registered_release_edge_id",
                "numeric_registered_release_edge",
                "fixture_admission",
                historical_depth="frozen_fixture",
                forbidden_adjacent_inputs=["edge_payload_label"],
            ),
            input_record(
                "candidate_topology.registered_release_source_node_id",
                "numeric_registered_release_source",
                "fixture_admission",
                historical_depth="frozen_fixture",
            ),
            input_record(
                "candidate_topology.registered_release_receiver_node_id",
                "numeric_registered_release_receiver",
                "fixture_admission",
                historical_depth="frozen_fixture",
            ),
            input_record(
                "candidate_topology.canonical_topology_digest",
                "registered_topology_identity_binding",
                "fixture_admission",
                historical_depth="frozen_fixture",
                load_bearing=False,
            ),
        ],
    )
    freeze_execution_boundary(
        candidate_b,
        i2,
        [
            input_record(
                "LGRC9V3RuntimeState.base_state.nodes[1].coherence",
                "C_leakage_source",
                "one_shot_export_decision",
                forbidden_adjacent_inputs=["global_node_scan", "destination_state"],
            ),
            input_record(
                "candidate_policy.C_floor",
                "predeclared_leakage_source_floor",
                "one_shot_export_decision",
            ),
            input_record(
                "candidate_policy.q_cap",
                "predeclared_export_cap",
                "one_shot_export_decision",
            ),
            input_record(
                "candidate_closure.qualifying_local_event_receipt",
                "exact_local_trigger_receipt",
                "registered_event_callback",
                historical_depth="one_exact_registered_event",
                forbidden_adjacent_inputs=["global_event_count", "wall_clock"],
            ),
            input_record(
                "candidate_closure.export_policy_receipt",
                "restored_one_shot_consumption_state",
                "before_export_attempt",
                historical_depth="restored_current_receipt_state",
            ),
            input_record(
                "candidate_fixture.edge_payloads[1]",
                "registered_export_boundary_and_destination",
                "fixture_admission",
                historical_depth="frozen_fixture",
            ),
            input_record(
                "candidate_fixture.role_to_node_id",
                "formation_leakage_destination_readout_roles",
                "fixture_admission",
                historical_depth="frozen_fixture",
            ),
        ],
    )
    freeze_execution_boundary(
        candidate_c,
        i2,
        [
            input_record(
                "candidate_closure.S_by_edge[1]",
                "restored_route_susceptibility",
                "closure_application",
                historical_depth="restored_current_closure_state",
                forbidden_adjacent_inputs=["outcome_history", "route_label"],
            ),
            input_record(
                "candidate_fixture.edge_payloads[1]",
                "registered_susceptible_edge",
                "fixture_admission",
                historical_depth="frozen_fixture",
            ),
            input_record(
                "LGRC9V3RuntimeState.base_state.base_conductance[1]",
                "g_native",
                "after_native_conductance_rebuild_before_closure_write",
            ),
            input_record(
                "LGRC9V3.get_params().evolution_and_constitutive_semantic_modes",
                "native_conductance_potential_and_flux_parameters",
                "partial_native_pipeline_invocation",
                historical_depth="frozen_model_parameters",
                forbidden_adjacent_inputs=["outcome_tuned_evolution_parameters"],
            ),
            input_record(
                "candidate_closure.q_use_by_edge[1]",
                "registered_route_use_amount",
                "after_registered_route_use",
                historical_depth="current_registered_use_only",
            ),
            input_record(
                "candidate_closure.qualifying_progression_receipt",
                "exact_relaxation_event_receipt",
                "registered_event_callback",
                historical_depth="one_exact_registered_event",
                forbidden_adjacent_inputs=["global_event_count", "wall_clock"],
            ),
            input_record(
                "candidate_closure.update_count",
                "restored_closure_update_count",
                "before_relaxation_update",
                historical_depth="restored_current_closure_state",
            ),
        ],
    )
    return {
        "artifact_kind": "added_mechanism_candidate_contract_bundle",
        "artifact_schema_version": "n31_i9_candidate_contract_bundle_v2",
        "generated_at": GENERATED_AT,
        "global_admission_reason": "d0_insufficient",
        "global_admission_reason_qualifier": (
            "d0_insufficient_for_autonomous_causal_weakening"
        ),
        "candidate_contracts": [candidate_a, candidate_b, candidate_c],
        "cross_candidate_rules": {
            "one_generic_scalar_decay_law_used": False,
            "raw_effect_magnitude_ranking_allowed": False,
            "native_upgrade_from_added_mechanism_allowed": False,
            "candidate_semantics_interchangeable": False,
            "positive_rung_assigned_from_admission": False,
            "N31_C6_implies_DR6": False,
        },
    }


def build_i8_revision_lineage(i8: dict[str, Any]) -> dict[str, Any]:
    lineage: dict[str, Any] = {
        "artifact_kind": "n31_i8_revision_lineage",
        "artifact_schema_version": "n31_i8_revision_lineage_r1",
        "generated_at": GENERATED_AT,
        "reviewed_I8_identity": {
            "output_digest": (
                "3527615b47e6510acad152647731d405bdb845d7ab380f6b0bc1fb379966a2ba"
            ),
            "artifact_sha256": "not_recorded_in_review_snapshot",
            "identity_role": "pre_correction_reviewed_I8",
        },
        "current_I8_identity": {
            "path": relative(I8),
            "output_digest": i8["output_digest"],
            "artifact_sha256": sha256_file(I8),
            "identity_role": "corrected_I8_consumed_by_I9",
        },
        "corrections_made": [
            "manifest_reference_and_count_normalization",
            "D0_R_scope_qualification",
            "D0_insufficiency_narrowed_to_autonomous_causal_weakening",
            "direct_and_transitive_replay_scope_separated",
            "control_status_boolean_meaning_normalized",
            "equal_complete_state_scope_made_explicit",
            "floating_point_boundary_checks_normalized",
            "I3_null_controls_separated_from_future_candidate_regeneration",
        ],
        "scientific_conclusion_changed": False,
        "preserved_scientific_conclusion": {
            "native_semantic_class": "D0a",
            "native_ladder_rung": "DR2",
            "formation": "supported",
            "persistence": "supported",
            "autonomous_weakening": "unsupported",
            "added_mechanism_admission_reason_qualifier": (
                "d0_insufficient_for_autonomous_causal_weakening"
            ),
        },
        "I9_consumption": {
            "exact_current_I8_consumed": True,
            "reviewed_pre_correction_I8_consumed": False,
            "scientific_rerun_required_for_lineage_only_correction": False,
        },
    }
    lineage["output_digest"] = digest_value(lineage)
    I8_REVISION_LINEAGE.write_text(canonical_json(lineage), encoding="utf-8")
    return lineage


def build() -> dict[str, Any]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i2 = load_json(I2)
    i8 = load_json(I8)
    sources = [source_record(I2), source_record(I8)]
    i8_revision_lineage = build_i8_revision_lineage(i8)
    contract_bundle = build_candidate_contracts(i2)
    contract_bundle["output_digest"] = digest_value(contract_bundle)
    CONTRACT_BUNDLE.write_text(canonical_json(contract_bundle), encoding="utf-8")
    candidates = contract_bundle["candidate_contracts"]
    native = {
        "lane_id": "native",
        "primary_semantic_class": "D0a",
        "carrier_state_authority": "existing_native",
        "organization_observable_authority": "exact_derived_projection",
        "carrier_state_path": "LGRC9V3RuntimeState.base_state.nodes[*].coherence",
        "organization_observable_path": (
            "exact_projection_over_registered_route_node_coherence"
        ),
        "decay_relation_ladder_rung": "DR2",
        "formation": "supported",
        "persistence": "supported",
        "autonomous_weakening": "unsupported",
        "source_iteration": "I8",
        "native_upgrade_from_I9_allowed": False,
    }
    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9",
        "artifact_kind": "added_mechanism_admission",
        "artifact_schema_version": "n31_i9_added_mechanism_admission_v2",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_lane_qualified_added_mechanism_admission_"
            "frozen_no_candidate_evidence"
        ),
        "command": COMMAND,
        "script": SCRIPT_RELATIVE,
        "source_chain": sources,
        "I8_revision_lineage": {
            "path": relative(I8_REVISION_LINEAGE),
            "sha256": sha256_file(I8_REVISION_LINEAGE),
            "output_digest": i8_revision_lineage["output_digest"],
            "scientific_conclusion_changed": False,
            "exact_current_I8_consumed": True,
        },
        "source_contract": {
            "path": relative(CONTRACT_BUNDLE),
            "sha256": sha256_file(CONTRACT_BUNDLE),
            "output_digest": contract_bundle["output_digest"],
        },
        "review_resolution": {
            "admission_decision": "passed",
            "semantic_lane_separation": "passed",
            "pre_execution_contract_completeness": "passed_after_I9_revision",
            "candidate_execution_performed": False,
            "scientific_rerun_performed": False,
            "revision_scope": (
                "preregistration_inputs_controls_lineage_authority_roles_"
                "causal_paths_and_executable_topology"
            ),
        },
        "admission_decision": {
            "added_mechanism_admission_reason": "d0_insufficient",
            "admission_reason_qualifier": (
                "d0_insufficient_for_autonomous_causal_weakening"
            ),
            "D0_wholly_insufficient": False,
            "A_execution_decision": "execute_I9_A",
            "B_execution_decision": "execute_I9_B",
            "C_execution_decision": "execute_I9_C",
            "admission_is_positive_candidate_evidence": False,
        },
        "native_decay_classification": native,
        "added_mechanism_decay_classifications": candidates,
        "lane_classification_policy": {
            "shared_evidence_strength_ladder": "DR0_through_DR6",
            "separate_numeric_producer_ladder_created": False,
            "semantic_and_authority_qualification_required": True,
            "native_upgrade_allowed": False,
            "future_native_implementation_requires_new_native_validation": True,
            "N31_C6_is_not_DR6": True,
        },
        "evidence_state": {
            "candidate_runtime_evidence_opened": False,
            "source_current_candidate_rows": 0,
            "positive_added_mechanism_rungs_assigned": False,
            "current_added_mechanism_rung_by_candidate": {
                row["candidate_id"]: row["current_decay_relation_ladder_rung"]
                for row in candidates
            },
        },
        "n31_closeout_progress": {
            "n31_closeout_progress_rung": "N31-C4",
            "n31_closeout_ceiling": (
                "N31-C4_added_mechanism_admission_frozen_probes_pending"
            ),
            "n31_closeout_ladder_rung_assigned": False,
            "ready_for_I9_A": True,
            "ready_for_I9_B": True,
            "ready_for_I9_C": True,
            "final_N31_supported": False,
        },
        "claim_boundary": {
            "allowed_claim": (
                "three_lane_qualified_added_mechanism_contracts_admitted_for_"
                "execution_with_native_D0a_preserved_at_DR2"
            ),
            "blocked_claims": [
                "positive_A_support",
                "positive_B_support",
                "positive_C_support",
                "added_mechanism_DR5",
                "added_mechanism_DR6",
                "native_DR4_or_stronger",
                "native_decay",
                "native_memory",
                "trail_or_stigmergy",
                "communication",
                "ecology",
                "agency",
                "native_support",
                "Phase_8_completion",
            ],
            "unsafe_claim_flags": {
                "positive_A_claim_allowed": False,
                "positive_B_claim_allowed": False,
                "positive_C_claim_allowed": False,
                "added_mechanism_DR5_claim_allowed": False,
                "added_mechanism_DR6_claim_allowed": False,
                "native_DR4_or_stronger_claim_allowed": False,
                "native_memory_claim_allowed": False,
                "trail_or_stigmergy_claim_allowed": False,
                "communication_claim_allowed": False,
                "ecology_claim_allowed": False,
                "agency_claim_allowed": False,
                "native_support_claim_allowed": False,
                "phase8_completion_claim_allowed": False,
            },
        },
        "governance": {
            "governance_base_revision": GOVERNANCE_BASE_REVISION,
            "src_diff_empty": git_diff_empty("src"),
            "protected_runtime_contract_diff_empty": all(
                git_diff_empty(path) for path in PROTECTED_PATHS
            ),
        },
        "artifact_manifest": [
            {
                "path": relative(CONTRACT_BUNDLE),
                "sha256": sha256_file(CONTRACT_BUNDLE),
                "artifact_role": "I9_pre_execution_candidate_contract_bundle",
            },
            {
                "path": relative(I8_REVISION_LINEAGE),
                "sha256": sha256_file(I8_REVISION_LINEAGE),
                "artifact_role": "I8R1_revision_lineage",
            },
        ],
        "artifact_validation": {
            "artifact_paths_equal_manifest_paths": True,
            "all_artifact_sha256_match_file_contents": True,
        },
    }
    required_topology = set(i2["schema"]["candidate_topology_schema"]["required_fields"])
    candidate_topologies_complete = all(
        required_topology.issubset(row["topology"]) for row in candidates
    )
    authority_enum = set(
        i2["schema"]["taxonomy"]["representation_or_authority_classes"]
    )
    controls = i2["controls"]
    expected_controls = {
        "A": controls["candidate_A_controls"],
        "B": controls["candidate_B_controls"],
        "C": controls["candidate_C_controls"],
    }
    inherited_controls = list(
        dict.fromkeys(
            controls["common_active_nulls"]
            + controls["D0_controls"]
            + controls["schema_relation_controls"]
        )
    )
    candidate_by_class = {
        row["primary_semantic_class"]: row for row in candidates
    }
    a = candidate_by_class["A"]
    b = candidate_by_class["B"]
    c = candidate_by_class["C"]
    payload["checks"] = [
        check("I2_and_I8_source_identities_exact", all(row["identity_exact"] for row in sources), sources),
        check(
            "I8_ready_for_I9_admission",
            i8["n31_closeout_progress"]["ready_for_iteration_9_added_mechanism_admission"]
            and i8["added_mechanism_decision"]["admission_reason_qualifier"]
            == "d0_insufficient_for_autonomous_causal_weakening",
            i8["added_mechanism_decision"],
        ),
        check(
            "I8R1_revision_lineage_explicit_and_current_I8_consumed",
            i8_revision_lineage["reviewed_I8_identity"]["output_digest"]
            == "3527615b47e6510acad152647731d405bdb845d7ab380f6b0bc1fb379966a2ba"
            and i8_revision_lineage["current_I8_identity"]["output_digest"]
            == i8["output_digest"]
            and not i8_revision_lineage["scientific_conclusion_changed"]
            and i8_revision_lineage["I9_consumption"]["exact_current_I8_consumed"],
            payload["I8_revision_lineage"],
        ),
        check(
            "native_lane_preserved_at_DR2",
            native["decay_relation_ladder_rung"] == "DR2"
            and native["autonomous_weakening"] == "unsupported"
            and native["carrier_state_authority"] == "existing_native"
            and native["organization_observable_authority"]
            == "exact_derived_projection"
            and not native["native_upgrade_from_I9_allowed"],
            native,
        ),
        check(
            "three_distinct_added_mechanism_lanes_admitted",
            [row["primary_semantic_class"] for row in candidates] == ["A", "B", "C"]
            and all(row["execution_decision"] == "execute" for row in candidates),
            [row["candidate_id"] for row in candidates],
        ),
        check(
            "authority_classes_use_frozen_enum",
            all(row["representation_or_authority_class"] in authority_enum for row in candidates),
            [row["representation_or_authority_class"] for row in candidates],
        ),
        check(
            "all_added_mechanism_lanes_remain_DR0_without_evidence",
            all(
                row["current_decay_relation_ladder_rung"] == "DR0"
                and row["candidate_disposition"] == "not_executed"
                and not row["positive_candidate_evidence_opened"]
                for row in candidates
            ),
            payload["evidence_state"],
        ),
        check(
            "candidate_topologies_complete_and_executable",
            candidate_topologies_complete
            and all(
                row["topology"]["topology_signature"]
                == row["topology"]["canonical_topology_digest"]
                == digest_value(
                    {
                        "node_ids": row["topology"]["node_ids"],
                        "edge_ids": row["topology"]["edge_ids"],
                        "node_payloads": row["topology"]["node_payloads"],
                        "edge_payloads": row["topology"]["edge_payloads"],
                        "role_to_node_id": row["topology"]["role_to_node_id"],
                    }
                )
                and all(isinstance(edge_id, int) for edge_id in row["topology"]["edge_ids"])
                and all(
                    set(edge_row)
                    >= {
                        "edge_id",
                        "source_node_id",
                        "source_port_id",
                        "target_node_id",
                        "target_port_id",
                        "orientation",
                        "delay",
                        "conductance",
                        "payload",
                    }
                    for edge_row in row["topology"]["edge_payloads"]
                )
                for row in candidates
            ),
            sorted(required_topology),
        ),
        check(
            "source_current_input_allowlists_fail_closed",
            all(
                row["source_current_inputs"]
                and row["source_current_inputs"]
                == [item["input_path"] for item in row["source_current_input_allowlist"]]
                and all(
                    set(item)
                    == {
                        "input_path",
                        "input_role",
                        "read_phase",
                        "required_or_optional",
                        "historical_depth",
                        "load_bearing",
                        "forbidden_adjacent_inputs",
                    }
                    for item in row["source_current_input_allowlist"]
                )
                and row["source_current_input_policy"]["unlisted_input_read_status"]
                == "blocks_candidate_row"
                and not row["source_current_input_policy"]["global_state_scan_allowed"]
                for row in candidates
            ),
            {row["candidate_id"]: row["source_current_inputs"] for row in candidates},
        ),
        check(
            "candidate_equations_clocks_invariants_frozen",
            all(
                row.get("equation_or_relation")
                and row.get("internal_time_contract", {}).get("wall_clock_excluded")
                and row.get("invariant_contract")
                for row in candidates
            ),
            [row["candidate_id"] for row in candidates],
        ),
        check(
            "lane_specific_controls_are_valid_frozen_I2_controls",
            all(
                row["lane_specific_control_ids"]
                == expected_controls[row["primary_semantic_class"]]
                for row in candidates
            ),
            expected_controls,
        ),
        check(
            "complete_inherited_control_matrices_frozen_for_regeneration",
            all(
                row["inherited_required_control_ids"] == inherited_controls
                and set(row["complete_control_ids"])
                == set(inherited_controls)
                | set(expected_controls[row["primary_semantic_class"]])
                and row["complete_control_set_digest"]
                == digest_value(row["complete_control_ids"])
                and row["candidate_specific_regeneration_required"]
                and not row["direct_I3_null_consumption_allowed"]
                and row["direct_I3_null_consumption_count"] == 0
                for row in candidates
            ),
            {
                row["candidate_id"]: len(row["complete_control_ids"])
                for row in candidates
            },
        ),
        check(
            "candidate_A_release_efficacy_boundary_frozen",
            a["update_phase"] == "packet_creation_only_never_in_flight"
            and a["equation_or_relation"]["in_flight_packet_relation"]
            == "q_in_flight(t+1) = q_in_flight(t)"
            and a["invariant_contract"]["unreleased_coherence_remains_at_source"]
            and a["role_contract"]["release_source_node_id"] == 1
            and a["invariant_contract"]["only_q_created_is_debited"]
            and not a["invariant_contract"]["separate_unreleased_reservoir_created"]
            and not a["qualifying_phase_event_contract"][
                "unrelated_events_advance_phase"
            ]
            and a["fresh_aged_branch_match_contract"][
                "only_allowed_difference_at_release_decision"
            ]
            == "registered_release_phase_closure_bundle"
            and a["internal_time_contract"]["receipt_count_input_role"]
            == "validation_only_not_amount_selecting"
            and a["equation_or_relation"]["release_policy_identity"]
            == digest_value(
                {
                    "release_policy_schema": "n31_A_release_efficacy_policy_v1",
                    "epsilon_A_by_phase": {"fresh": 1.0, "aged": 0.5},
                    "packet_creation_relation": (
                        "q_created = q_requested * epsilon_A(phase)"
                    ),
                }
            )
            and "candidate_fixture.edge_payloads[1]"
            not in a["source_current_inputs"]
            and a["highest_later_eligible_ceiling"]
            == "DR5_expression_attenuation_not_field_state_decay",
            {
                "update_phase": a["update_phase"],
                "ceiling": a["highest_later_eligible_ceiling"],
            },
        ),
        check(
            "candidate_B_conservation_destination_and_ownership_frozen",
            b["export_destination_excluded_from_later_readout_path"]
            and b["role_contract"]["leakage_source_node_id"] == 1
            and "C_leakage_source" in b["equation_or_relation"]["emission_relation"]
            and b["export_ownership"]["B_R_subtype"]
            and b["export_ownership"]["d0_to_br_bridge_status"] == "not_tested"
            and not b["equation_or_relation"]["global_scheduler_allowed"],
            {
                "later_readout_path": b["later_readout_path"],
                "destination": b["topology"]["receiver_region"],
                "export_ownership": b["export_ownership"],
            },
        ),
        check(
            "candidate_B_organization_isolation_and_one_shot_contracts_frozen",
            b["organization_contract"]["mass_loss_is_not_organization_weakening"]
            and b["organization_contract"]["mass_loss_substitution_control"]
            and b["destination_isolation_contract"]["destination_clamp_pair_required"]
            and b["destination_isolation_contract"]["event_trace_no_return_required"]
            and b["one_shot_trigger_contract"]["eligibility_consumption"]
            == "atomic_on_first_qualifying_attempt"
            and b["one_shot_trigger_contract"]["receipt_restoration_required"]
            and b["one_shot_trigger_contract"]["zero_emission_behavior"]
            == "consume_receipt_and_record_zero_emission",
            {
                "organization": b["organization_contract"],
                "isolation": b["destination_isolation_contract"],
            },
        ),
        check(
            "candidate_C_independent_state_restoration_and_update_magnitude_frozen",
            c["representation_or_authority_class"]
            == "effective_non_markovian_closure"
            and c["restoration_contract"]["composed_identity_required"]
            and c["restoration_contract"][
                "same_complete_C_different_S_intervention_required"
            ]
            and set(c["non_coherence_state_contract"])
            >= {
                "units",
                "bounds",
                "susceptibility_update_magnitude",
                "invariant",
            }
            and c["non_coherence_state_contract"][
                "susceptibility_update_ledger_role"
            ]
            == "report_only_noncausal"
            and c["non_coherence_state_contract"]["effective_non_markovian_relative_to"]
            == "LGRC_state_alone"
            and 0.0 < c["equation_or_relation"]["rho"] < 1.0,
            {
                "authority": c["representation_or_authority_class"],
                "restoration": c["restoration_contract"],
                "non_coherence_state": c["non_coherence_state_contract"],
            },
        ),
        check(
            "candidate_C_executable_native_consumer_path_frozen_with_hook_debt",
            c["executable_conductance_path"]["write_relation"]
            == "g_effective = S * g_native"
            and c["executable_conductance_path"]["native_operation_consumers"]
            == [
                "pygrc.models.grc_9_v3_runtime.compute_potential",
                "pygrc.models.grc_9_v3_runtime.compute_flux",
            ]
            and not c["executable_conductance_path"][
                "ordinary_LGRC9V3_step_compatible_without_hook"
            ]
            and c["executable_conductance_path"]["missing_runtime_hook_debt"]
            and not c["executable_conductance_path"]["packet_amount_scaling_allowed"]
            and not c["executable_conductance_path"]["export_scheduling_allowed"]
            and c["matched_branch_contract"]["comparison_phase"]
            == "before_closure_application",
            c["executable_conductance_path"],
        ),
        check(
            "producer_residue_and_naturalization_debt_explicit",
            all(row["producer_residue"] and row["naturalization_debt"] for row in candidates),
            [row["candidate_id"] for row in candidates],
        ),
        check(
            "native_upgrade_blocked_for_all_added_lanes",
            all(not row["native_upgrade_allowed"] for row in candidates),
            [row["native_upgrade_allowed"] for row in candidates],
        ),
        check(
            "candidate_semantics_not_collapsed_or_ranked",
            not contract_bundle["cross_candidate_rules"]["one_generic_scalar_decay_law_used"]
            and not contract_bundle["cross_candidate_rules"]["raw_effect_magnitude_ranking_allowed"]
            and len({row["equation_or_relation"]["equation_or_relation_id"] for row in candidates}) == 3,
            contract_bundle["cross_candidate_rules"],
        ),
        check(
            "no_positive_candidate_evidence_opened",
            not payload["evidence_state"]["candidate_runtime_evidence_opened"]
            and payload["evidence_state"]["source_current_candidate_rows"] == 0
            and not payload["evidence_state"]["positive_added_mechanism_rungs_assigned"],
            payload["evidence_state"],
        ),
        check(
            "artifact_manifest_exact",
            payload["artifact_validation"][
                "artifact_paths_equal_manifest_paths"
            ]
            and payload["artifact_validation"][
                "all_artifact_sha256_match_file_contents"
            ]
            and {
                row["path"]: row["sha256"] for row in payload["artifact_manifest"]
            }
            == {
                relative(CONTRACT_BUNDLE): sha256_file(CONTRACT_BUNDLE),
                relative(I8_REVISION_LINEAGE): sha256_file(I8_REVISION_LINEAGE),
            },
            payload["artifact_manifest"],
        ),
        check(
            "unsafe_claim_flags_false",
            not any(payload["claim_boundary"]["unsafe_claim_flags"].values()),
            payload["claim_boundary"]["unsafe_claim_flags"],
        ),
        check("src_diff_empty", payload["governance"]["src_diff_empty"], GOVERNANCE_BASE_REVISION),
        check(
            "protected_runtime_contract_diff_empty",
            payload["governance"]["protected_runtime_contract_diff_empty"],
            GOVERNANCE_BASE_REVISION,
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(payload), "recursive"),
    ]
    payload["failed_checks"] = [
        row["check_id"] for row in payload["checks"] if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "rejected_I9_admission_checks_failed"
        payload["n31_closeout_progress"]["ready_for_I9_A"] = False
        payload["n31_closeout_progress"]["ready_for_I9_B"] = False
        payload["n31_closeout_progress"]["ready_for_I9_C"] = False
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    candidate_rows = "\n".join(
        "| {candidate} | {semantic} | {authority} | {decision} | {rung} | {ceiling} |".format(
            candidate=row["candidate_id"],
            semantic=row["primary_semantic_class"],
            authority=row["representation_or_authority_class"],
            decision=row["execution_iteration"],
            rung=row["current_decay_relation_ladder_rung"],
            ceiling=row["highest_later_eligible_ceiling"],
        )
        for row in payload["added_mechanism_decay_classifications"]
    )
    check_rows = "\n".join(
        f"| `{row['check_id']}` | {str(row['passed']).lower()} |"
        for row in payload["checks"]
    )
    execution_rows = "\n".join(
        "| {candidate} | {inputs} | {lane_controls} | {complete_controls} | `{topology}` |".format(
            candidate=row["candidate_id"],
            inputs=len(row["source_current_inputs"]),
            lane_controls=len(row["lane_specific_control_ids"]),
            complete_controls=len(row["complete_control_ids"]),
            topology=row["topology"]["canonical_topology_digest"],
        )
        for row in payload["added_mechanism_decay_classifications"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 9 - Added-Mechanism Admission

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
native_carrier_lane = D0a / existing_native carrier / DR2
native_organization_observable = exact_derived_projection
added_mechanism_lanes = A, B, C
positive_candidate_evidence_opened = false
n31_closeout_progress_rung = N31-C4
ready_for_I9_A = {str(payload['n31_closeout_progress']['ready_for_I9_A']).lower()}
ready_for_I9_B = {str(payload['n31_closeout_progress']['ready_for_I9_B']).lower()}
ready_for_I9_C = {str(payload['n31_closeout_progress']['ready_for_I9_C']).lower()}
final_N31_supported = false
```

I9 freezes three semantically distinct added-mechanism contracts. It does not
run them and assigns no positive producer or closure rung.

The reviewed pre-correction I8 identity and the exact corrected I8 consumed by
I9 are linked in `n31_i8_revision_lineage_r1.json`. The correction changed no
scientific conclusion.

## Lane-Qualified Classification

| Candidate | Semantic class | Authority | Next probe | Current rung | Later eligible ceiling |
|---|---|---|---|---|---|
{candidate_rows}

The native D0a lane remains at DR2. A later producer-assisted DR5 or DR6 result
will remain separate and cannot upgrade that native ceiling. A future native
implementation must be rerun as native evidence.

## Candidate Roles

```text
A = release-efficacy expression attenuation; never in-flight attenuation
B = producer-owned conserved B-R export to an explicit destination
C = independently restored susceptibility closure with explicit relaxation
```

## Pre-Execution Boundary

| Candidate | Allowed source-current inputs | Lane controls | Complete controls to regenerate | Canonical topology digest |
|---|---:|---:|---:|---|
{execution_rows}

Every unlisted input blocks the candidate row. I3 null results are not consumed
directly: all applicable common, D0, schema-relation, and lane controls must be
regenerated against the candidate carrier and authority.

Candidate A distinguishes formation source node 0, release source node 1, and
receiver node 2. Only `q_created` is debited; `q_unreleased` is a derived
counterfactual that remains in release-source coherence. Only the exact
registered formation-arrival receipt can age the release phase.

Candidate B distinguishes formation source node 0, leakage source node 1,
destination node 2, and later readout node 3. Conserved export is not enough:
the preregistered route-organization contrast must weaken independently of mass
loss, and destination clamp/trace controls must exclude return influence before
readout.

Candidate C applies `S * g_native` after native conductance reconstruction and
before native `compute_potential` and `compute_flux`. Ordinary `LGRC9V3.step()`
would overwrite a prior conductance write, so the closure owns this partial
pipeline ordering. That missing hook is explicit producer/closure debt, not a
native decay claim. `absolute_delta_S` is a report-only update magnitude, not a
resource cost; the composed LGRC-plus-S system may itself be Markovian.

The candidates do not share one scalar decay law and are not ranked by raw
effect size. A is capped at expression-attenuation DR5. B and C may become DR6
only after DR5 controls and a reusable bounded contract. `N31-C6` remains a
closeout-completeness statement rather than mechanism DR6 evidence.

## Claim Boundary

```text
{payload['claim_boundary']['allowed_claim']}
```

No positive A/B/C support, native decay, memory, trail, communication, ecology,
agency, native-support, or Phase 8 claim is opened.

## Checks

| Check | Passed |
|---|---:|
{check_rows}
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build()
    write_report(payload)
    print(canonical_json(payload), end="")


if __name__ == "__main__":
    main()
