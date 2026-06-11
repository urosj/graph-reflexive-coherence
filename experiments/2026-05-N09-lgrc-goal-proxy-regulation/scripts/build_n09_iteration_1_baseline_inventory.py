#!/usr/bin/env python3
"""Build N09 Iteration 1 baseline and source inventory artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n09_iteration_1_baseline_inventory.json"
REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_1_baseline_inventory.md"

N05 = ROOT / "experiments" / "2026-05-N05-lgrc-coherence-waves-oscillators"
N06 = ROOT / "experiments" / "2026-05-N06-lgrc-semantic-route-choice"
N07 = ROOT / "experiments" / "2026-05-N07-rc-identity-attractor-invariance"
N08 = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"

N05_O5_OUTPUT = N05 / "outputs" / "n05_iteration_7_o5_self_sustained_boundary.json"
N05_O5_REPORT = N05 / "reports" / "n05_iteration_7_o5_self_sustained_boundary.md"
N05_CLOSEOUT_OUTPUT = N05 / "outputs" / "n05_iteration_8_o6_closeout.json"
N05_CLOSEOUT_REPORT = N05 / "reports" / "n05_iteration_8_o6_closeout.md"

N06_CLOSEOUT_OUTPUT = N06 / "outputs" / "n06_iteration_8_sc6_closeout.json"
N06_CLOSEOUT_REPORT = N06 / "reports" / "n06_iteration_8_sc6_closeout.md"

N07_11B_OUTPUT = N07 / "outputs" / "n07_iteration_11b_neutral_absorber_reservoir.json"
N07_11B_REPORT = N07 / "reports" / "n07_iteration_11b_neutral_absorber_reservoir.md"
N07_CLOSEOUT_OUTPUT = (
    N07 / "outputs" / "n07_iteration_12_long_horizon_compatibility_closeout.json"
)
N07_CLOSEOUT_REPORT = (
    N07 / "reports" / "n07_iteration_12_long_horizon_compatibility_closeout.md"
)

N08_MEM2_OUTPUT = N08 / "outputs" / "n08_iteration_4_mem2_memory_surface.json"
N08_MEM2_REPORT = N08 / "reports" / "n08_iteration_4_mem2_memory_surface.md"
N08_MEM5_OUTPUT = N08 / "outputs" / "n08_iteration_7_mem5_repeated_memory_selection.json"
N08_MEM5_REPORT = N08 / "reports" / "n08_iteration_7_mem5_repeated_memory_selection.md"
N08_HYP_A_OUTPUT = N08 / "outputs" / "n08_iteration_8_mem6_closeout.json"
N08_HYP_A_REPORT = N08 / "reports" / "n08_iteration_8_mem6_closeout.md"
N08_HYP_B_OUTPUT = N08 / "outputs" / "n08_iteration_13_native_geometry_trail_closeout.json"
N08_HYP_B_REPORT = N08 / "reports" / "n08_iteration_13_native_geometry_trail_closeout.md"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def inventory_stable_digest(inventory: dict[str, Any]) -> str:
    excluded = {"generated_at", "inventory_digest", "git"}
    return canonical_digest(
        {key: value for key, value in inventory.items() if key not in excluded}
    )


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def compact_n06_cycles(n06: dict[str, Any]) -> list[dict[str, Any]]:
    cycles = n06.get("artifact_only_closeout", {}).get("per_cycle", [])
    if not isinstance(cycles, list):
        return []
    rows: list[dict[str, Any]] = []
    for cycle in cycles:
        if not isinstance(cycle, dict):
            continue
        rows.append(
            {
                "cycle_id": cycle.get("cycle_id"),
                "context_state_id": cycle.get("context_state_id"),
                "candidate_set_digest": cycle.get("candidate_set_digest"),
                "selected_route": cycle.get("selected_route"),
                "selected_candidate_route_digest": cycle.get(
                    "selected_candidate_route_digest"
                ),
                "rejected_candidate_route_digests": cycle.get(
                    "rejected_candidate_route_digests", []
                ),
                "candidate_source_surface_digests": cycle.get(
                    "candidate_source_surface_digests", []
                ),
                "candidate_score_component_sums": cycle.get(
                    "candidate_score_component_sums", {}
                ),
                "candidate_context_values": cycle.get("candidate_context_values", {}),
                "source_surface_provenance": cycle.get("source_surface_provenance", {}),
                "scheduled_processed_packet_evidence": cycle.get(
                    "scheduled_processed_packet_evidence", {}
                ),
            }
        )
    return rows


def compact_memory_rows(rows: list[Any], limit: int = 4) -> list[dict[str, Any]]:
    compacted: list[dict[str, Any]] = []
    for row in rows[:limit]:
        if not isinstance(row, dict):
            continue
        if row.get("selected_route_id") is not None:
            route_id = row.get("selected_route_id")
            route_id_source = "selected_route_id"
        elif row.get("route_id") is not None:
            route_id = row.get("route_id")
            route_id_source = "route_id"
        else:
            route_id = row.get("memory_surface_key", {}).get("route_id")
            route_id_source = "memory_surface_key.route_id"
        compacted.append(
            {
                "memory_surface_id": row.get("memory_surface_id"),
                "memory_surface_digest": row.get("memory_surface_digest"),
                "memory_surface_key_digest": row.get("memory_surface_key_digest"),
                "memory_surface_key": row.get("memory_surface_key", {}),
                "memory_policy_id": row.get("memory_policy_id"),
                "memory_policy_digest": row.get("memory_policy_digest"),
                "memory_surface_kind": row.get("memory_surface_kind"),
                "memory_strength": row.get("memory_strength"),
                "memory_budget_surface": row.get("memory_budget_surface"),
                "memory_budget_error": row.get("memory_budget_error"),
                "node_plus_packet_budget_error": row.get(
                    "node_plus_packet_budget_error"
                ),
                "route_id": route_id,
                "route_id_source": route_id_source,
                "route_id_missing": route_id is None,
                "source_arbitration_record_digest": row.get(
                    "source_arbitration_record_digest"
                ),
                "route_use_event_digest": row.get("route_use_event_digest"),
                "claim_ceiling": row.get("claim_ceiling"),
            }
        )
    return compacted


def first_cycle_candidate_fields(n08_mem5: dict[str, Any]) -> dict[str, Any]:
    cycles = n08_mem5.get("cycles", [])
    if not cycles:
        return {"present": False, "primary_blocker": "n08_mem5_cycles_missing"}
    first = cycles[0]
    if not isinstance(first, dict):
        return {
            "present": False,
            "primary_blocker": "n08_mem5_first_cycle_malformed",
        }
    records = first.get("candidate_route_records", [])
    if not records:
        return {
            "present": False,
            "primary_blocker": "n08_mem5_candidate_records_missing",
        }
    first_record = records[0]
    if not isinstance(first_record, dict):
        return {
            "present": False,
            "primary_blocker": "n08_mem5_first_candidate_record_malformed",
        }
    return {
        "present": True,
        "candidate_route_record_schema": first_record.get("artifact_schema_version"),
        "candidate_score_components": sorted(
            first_record.get("candidate_score_components", {}).keys()
        ),
        "candidate_runtime_visible_inputs": first_record.get(
            "candidate_runtime_visible_inputs", []
        ),
        "candidate_budget_prediction": first_record.get("candidate_budget_prediction"),
        "candidate_memory_budget_prediction": first_record.get(
            "candidate_memory_budget_prediction"
        ),
        "native_route_arbitration_policy_id": first_record.get(
            "native_route_arbitration_policy_id"
        ),
    }


def build_inventory() -> dict[str, Any]:
    n05_o5 = load_json(N05_O5_OUTPUT)
    n05 = load_json(N05_CLOSEOUT_OUTPUT)
    n06 = load_json(N06_CLOSEOUT_OUTPUT)
    n07_11b = load_json(N07_11B_OUTPUT)
    n07 = load_json(N07_CLOSEOUT_OUTPUT)
    n08_mem2 = load_json(N08_MEM2_OUTPUT)
    n08_mem5 = load_json(N08_MEM5_OUTPUT)
    n08_a = load_json(N08_HYP_A_OUTPUT)
    n08_b = load_json(N08_HYP_B_OUTPUT)

    n06_cycles = compact_n06_cycles(n06)
    n07_closeout_row = n07["long_horizon_closeout_row"]
    n08_mem2_rows = n08_mem2.get("memory_surface_rows", [])

    source_artifacts = {
        rel(N05_O5_OUTPUT): sha256_file(N05_O5_OUTPUT),
        rel(N05_CLOSEOUT_OUTPUT): sha256_file(N05_CLOSEOUT_OUTPUT),
        rel(N06_CLOSEOUT_OUTPUT): sha256_file(N06_CLOSEOUT_OUTPUT),
        rel(N07_11B_OUTPUT): sha256_file(N07_11B_OUTPUT),
        rel(N07_CLOSEOUT_OUTPUT): sha256_file(N07_CLOSEOUT_OUTPUT),
        rel(N08_MEM2_OUTPUT): sha256_file(N08_MEM2_OUTPUT),
        rel(N08_MEM5_OUTPUT): sha256_file(N08_MEM5_OUTPUT),
        rel(N08_HYP_A_OUTPUT): sha256_file(N08_HYP_A_OUTPUT),
        rel(N08_HYP_B_OUTPUT): sha256_file(N08_HYP_B_OUTPUT),
    }
    source_reports = {
        rel(N05_O5_REPORT): sha256_file(N05_O5_REPORT),
        rel(N05_CLOSEOUT_REPORT): sha256_file(N05_CLOSEOUT_REPORT),
        rel(N06_CLOSEOUT_REPORT): sha256_file(N06_CLOSEOUT_REPORT),
        rel(N07_11B_REPORT): sha256_file(N07_11B_REPORT),
        rel(N07_CLOSEOUT_REPORT): sha256_file(N07_CLOSEOUT_REPORT),
        rel(N08_MEM2_REPORT): sha256_file(N08_MEM2_REPORT),
        rel(N08_MEM5_REPORT): sha256_file(N08_MEM5_REPORT),
        rel(N08_HYP_A_REPORT): sha256_file(N08_HYP_A_REPORT),
        rel(N08_HYP_B_REPORT): sha256_file(N08_HYP_B_REPORT),
    }

    gpr_ladder = {
        "GPR0": "no_regulation_label_only_or_unmeasured_proxy",
        "GPR1": "proxy_measurement_serialized_with_digest_and_order",
        "GPR2": "error_signal_from_serialized_runtime_visible_evidence",
        "GPR3": "proxy_conditioned_action_eligibility_without_direct_mutation",
        "GPR4": "single_cycle_proxy_error_reduction_or_band_return",
        "GPR5": "repeated_bounded_proxy_regulation",
        "GPR6": "artifact_only_goal_proxy_regulation_candidate",
    }
    gpr_row_schema = [
        "row_id",
        "gpr_level",
        "claim_ceiling",
        "proxy_id",
        "proxy_kind",
        "regulated_variable_id",
        "regulated_variable_surface",
        "regulated_variable_digest",
        "measurement_value",
        "target_band",
        "error_metric",
        "error_value",
        "event_time_key",
        "scheduler_event_index",
        "proxy_policy_id",
        "proxy_policy_digest",
        "error_policy_id",
        "error_policy_digest",
        "regulation_response_digest",
        "regulation_response_policy_id",
        "mechanism_status_tags",
        "memory_surface_digest",
        "memory_surface_policy_digest",
        "identity_support_digest",
        "identity_support_outcome_tag",
        "regulation_outcome_tag",
        "source_candidate_set_digest",
        "source_route_arbitration_record_digest",
        "selected_candidate_route_digest",
        "producer_record_digest",
        "scheduled_packet_id",
        "processed_packet_id",
        "node_plus_packet_budget_before",
        "node_plus_packet_budget_after",
        "node_plus_packet_budget_error",
        "source_artifacts",
        "source_reports",
        "claim_flags",
    ]
    regulation_outcome_taxonomy = [
        "no_response_to_error",
        "wrong_direction_response",
        "single_cycle_error_reduction",
        "single_cycle_band_return",
        "bounded_repeated_regulation",
        "overshoot_oscillation",
        "saturation_no_recovery",
        "policy_saturation",
        "memory_poisoning",
        "budget_violation",
        "identity_disrupted_under_regulation",
        "identity_preserved_under_regulation",
        "native_policy_gap",
    ]
    n10_handoff_fields = [
        "goal_proxy_regulation_policy_digest",
        "proxy_surface_digest",
        "error_policy_digest",
        "regulation_response_digest",
        "memory_surface_digest",
        "identity_support_digest",
        "mechanism_status_tags",
        "regulation_outcome_tag",
        "identity_support_outcome_tag",
        "native_policy_gap_records",
    ]
    claim_flags = {
        "goal_proxy_regulation_claim_allowed": False,
        "agency_claim_allowed": False,
        "agentic_like_claim_allowed": False,
        "intention_claim_allowed": False,
        "semantic_goal_understanding_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "runtime_identity_acceptance_claim_allowed": False,
        "aco_like_claim_allowed": False,
        "ant_colony_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "biological_claim_allowed": False,
        "personhood_claim_allowed": False,
        "movement_claim_allowed": False,
        "unrestricted_identity_claim_allowed": False,
        "unrestricted_movement_claim_allowed": False,
    }
    missing_native_policy_surfaces = [
        "native_goal_proxy_regulation_policy_missing",
        "native_proxy_surface_policy_missing",
        "native_proxy_error_policy_missing",
        "native_proxy_conditioned_response_policy_missing",
        "native_goal_proxy_regulation_artifact_replay_validator_missing",
        "native_memory_shaped_regulation_surface_missing",
        "native_identity_preserving_regulation_validator_missing",
        "native_oscillator_return_regulation_policy_missing",
    ]

    n05_route_fields = n05["o6_boundary"]["route_coupling_fields"]
    n05_o5_positive = n05_o5["positive_lane"]
    n08_a_closeout = n08_a["closeout"]
    n08_b_closeout = n08_b["closeout_summary"]
    n07_support_digest = n07_closeout_row["support_area_digest"]
    n07_target_support_digest = n07_11b["source_metrics"].get("B_support_area_digest")
    n08_memory_rows_compact = compact_memory_rows(n08_mem2_rows)
    n08_memory_anchor_rows = [
        {
            "memory_surface_id": row.get("memory_surface_id"),
            "memory_surface_digest": row.get("memory_surface_digest"),
            "route_id": row.get("memory_surface_key", {}).get("route_id"),
            "source_support_area_digest": row.get("memory_surface_key", {}).get(
                "source_support_area_digest"
            ),
            "target_support_area_digest": row.get("memory_surface_key", {}).get(
                "target_support_area_digest"
            ),
            "source_matches_n07_support_area": row.get("memory_surface_key", {}).get(
                "source_support_area_digest"
            )
            == n07_support_digest,
            "target_matches_n07_11b_target_support_area": row.get(
                "memory_surface_key", {}
            ).get("target_support_area_digest")
            == n07_target_support_digest,
        }
        for row in n08_mem2_rows
        if isinstance(row, dict)
    ]
    n06_unknown_source_blockers = sorted(
        {
            row.get("source_surface_provenance", {}).get(
                "primary_blocker_for_unknown_source"
            )
            for row in n06_cycles
            if row.get("source_surface_provenance", {}).get(
                "primary_blocker_for_unknown_source"
            )
        }
    )

    inventory: dict[str, Any] = {
        "schema": "n09_iteration_1_baseline_inventory_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 1,
        "status": "passed",
        "purpose": "baseline_source_inventory_no_regulation_probe",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": (
            ".venv/bin/python "
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
            "build_n09_iteration_1_baseline_inventory.py"
        ),
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "regulation_probe_run": False,
        "n05_inventory": {
            "source_artifact": rel(N05_CLOSEOUT_OUTPUT),
            "o5_source_artifact": rel(N05_O5_OUTPUT),
            "status": n05["status"],
            "strongest_supported_o_level": n05["n05_closeout"][
                "strongest_supported_o_level"
            ],
            "strongest_claim_ceiling": n05["n05_closeout"][
                "strongest_claim_ceiling"
            ],
            "o5_cycle_count": n05_o5_positive["self_rearm_cycle_count"],
            "o5_cycle_definition": n05_o5_positive["cycle_semantics"][
                "cycle_definition"
            ],
            "o5_return_amount": n05_o5_positive["return_amount"],
            "o5_return_route_id": n05_o5_positive["return_route_id"],
            "o5_cycle_ids": n05_o5_positive["cycle_ids"],
            "oscillator_proxy_field_inventory": {
                "proxy_surface_id": "n05_oscillator_return_amount",
                "return_amount": n05_o5_positive["return_amount"],
                "return_route_id": n05_o5_positive["return_route_id"],
                "cycle_definition": n05_o5_positive["cycle_semantics"][
                    "cycle_definition"
                ],
                "cycle_count": n05_o5_positive["self_rearm_cycle_count"],
                "cycle_ids": n05_o5_positive["cycle_ids"],
                "cycle_count_basis": n05_o5_positive["cycle_semantics"][
                    "cycle_count_basis"
                ],
                "route_aspect_id": n05_route_fields["route_aspect_id"],
                "route_aspect_digest": n05_route_fields["route_aspect_digest"],
                "channel_sequence": n05_route_fields["channel_sequence"],
                "channel_sequence_digest": n05_route_fields[
                    "channel_sequence_digest"
                ],
                "route_edge_ids": n05_route_fields["route_edge_ids"],
                "causal_delay_status": "not_frozen_as_n09_default_fixture",
                "amplification_accounting_status": (
                    "available_in_n05_o3_source_but_not_default_n09_fixture"
                ),
            },
            "o6_supported": n05["n05_closeout"]["o6_supported"],
            "o6_primary_blocker": n05["n05_closeout"]["o6_primary_blocker"],
            "route_coupling_fields": n05_route_fields,
            "oscillator_regulation_fixture_status": (
                "secondary_fixture_deferred_until_simple_proxy_path_understood"
            ),
            "phase3_native_policy_blockers": n05[
                "phase3_native_policy_support_audit"
            ]["native_policy_blockers"],
        },
        "n06_inventory": {
            "source_artifact": rel(N06_CLOSEOUT_OUTPUT),
            "status": n06["status"],
            "strongest_supported_sc_level": n06["closeout"][
                "strongest_supported_sc_level"
            ],
            "strongest_claim_ceiling": n06["closeout"]["strongest_claim_ceiling"],
            "selection_scope": n06["artifact_only_closeout"]["scope"],
            "regulation_constraint": {
                "n06_selection_only_pre_topology_commit": True,
                "packet_execution_inherited_from_n06": False,
                "scheduled_processed_packet_scope": n06["closeout"][
                    "scheduled_processed_packet_evidence_applicability"
                ],
                "iteration_2_requirement": (
                    "N09 must define its own packet scheduling/processing path "
                    "for GPR4+; N06 supplies route-selection evidence only."
                ),
                "primary_blocker_if_packet_execution_inherited": (
                    "n06_selection_only_no_packet_execution_for_regulation"
                ),
            },
            "context_affordance_evidence_present": n06["artifact_only_closeout"][
                "checks"
            ]["context_relations_replayed"],
            "candidate_route_records_present": all(
                cycle.get("checks", {}).get("candidate_route_records_replayed")
                for cycle in n06["artifact_only_closeout"].get("per_cycle", [])
            ),
            "candidate_set_records_present": all(
                cycle.get("checks", {}).get("candidate_set_record_replayed")
                for cycle in n06["artifact_only_closeout"].get("per_cycle", [])
            ),
            "native_route_arbitration_records_present": all(
                cycle.get("checks", {}).get("native_route_arbitration_record_replayed")
                for cycle in n06["artifact_only_closeout"].get("per_cycle", [])
            ),
            "selected_rejected_route_digest_rows": n06_cycles,
            "source_provenance_constraints": {
                "unknown_source_blockers": n06_unknown_source_blockers,
                "committed_source_surface_required": (
                    "native_route_candidate_committed_source_surface_required"
                    in n06_unknown_source_blockers
                ),
            },
            "scheduled_processed_packet_scope": n06["closeout"][
                "scheduled_processed_packet_evidence_applicability"
            ],
        },
        "n07_inventory": {
            "source_artifact": rel(N07_CLOSEOUT_OUTPUT),
            "source_11b_artifact": rel(N07_11B_OUTPUT),
            "status": n07["status"],
            "frozen_n07_ceiling": n07["closeout_decision"]["frozen_n07_ceiling"],
            "strongest_trajectory_regime": n07["closeout_decision"][
                "strongest_trajectory_regime"
            ],
            "claim_ceiling": n07_closeout_row["claim_ceiling"],
            "support_area_id": n07_closeout_row["support_area_id"],
            "support_area_digest": n07_closeout_row["support_area_digest"],
            "activity_history_digest": n07_closeout_row["activity_history_digest"],
            "candidate_identity_carrier_type": n07_closeout_row[
                "candidate_identity_carrier_type"
            ],
            "identity_carrier_surface": n07_closeout_row[
                "identity_carrier_surface"
            ],
            "identity_acceptance_claim_allowed": n07_closeout_row[
                "identity_acceptance_claim_allowed"
            ],
            "identity_support_fields_for_n09": {
                "identity_support_digest": n07_closeout_row[
                    "activity_history_digest"
                ],
                "support_area_digest": n07_closeout_row["support_area_digest"],
                "support_area_id": n07_closeout_row["support_area_id"],
                "gate_vector": n07_closeout_row["gate_vector"],
                "trajectory_regime": n07_closeout_row["trajectory_regime"],
                "support_dependency_status": n07_closeout_row[
                    "support_dependency_status"
                ],
                "withdrawal_test_status": n07_closeout_row["withdrawal_test_status"],
            },
            "identity_preservation_precondition_gap": {
                "withdrawal_test_status": n07_closeout_row["withdrawal_test_status"],
                "identity_withdrawal_stability_baseline_available": False,
                "iteration_8_requirement": (
                    "N09 support-withdrawal lanes must include a baseline or "
                    "control that distinguishes regulation disruption from "
                    "pre-existing untested withdrawal stability."
                ),
                "primary_blocker_if_untreated": (
                    "n07_identity_withdrawal_baseline_not_available"
                ),
            },
        },
        "n08_inventory": {
            "hypothesis_a": {
                "source_artifact": rel(N08_HYP_A_OUTPUT),
                "status": n08_a["status"],
                "mem_level": n08_a["mem_level"],
                "claim_ceiling": n08_a["claim_ceiling"],
                "memory_or_trail_claim_scope": n08_a_closeout[
                    "memory_or_trail_claim_scope"
                ],
                "consumable_for_n09_memory_shaped_lane": True,
                "consumption_boundary": (
                    "serialized producer/policy memory evidence only; not native "
                    "trail memory and not goal-proxy regulation"
                ),
                "sample_memory_surface_rows": n08_memory_rows_compact,
                "support_anchor_consistency": {
                    "n07_support_area_digest": n07_support_digest,
                    "n07_11b_target_support_area_digest": n07_target_support_digest,
                    "memory_row_count_checked": len(n08_memory_anchor_rows),
                    "rows": n08_memory_anchor_rows,
                    "all_source_support_digests_match_n07": all(
                        row["source_matches_n07_support_area"]
                        for row in n08_memory_anchor_rows
                    ),
                    "all_target_support_digests_match_n07_11b": all(
                        row["target_matches_n07_11b_target_support_area"]
                        for row in n08_memory_anchor_rows
                    ),
                },
                "mem5_trend_summary": n08_mem5["trend_summary"],
                "mem5_candidate_fields": first_cycle_candidate_fields(n08_mem5),
            },
            "hypothesis_b": {
                "source_artifact": rel(N08_HYP_B_OUTPUT),
                "status": n08_b["status"],
                "hypothesis": n08_b["hypothesis"],
                "claim_ceiling": n08_b_closeout["hypothesis_b_claim_ceiling"],
                "status_detail": n08_b_closeout["hypothesis_b_status"],
                "current_blocker": n08_b_closeout["hypothesis_b_current_blocker"],
                "static_positive_geometry_response_persisted": n08_b_closeout[
                    "static_positive_geometry_response_persisted"
                ],
                "native_policy_absorption_needed": n08_b_closeout[
                    "native_policy_absorption_needed"
                ],
                "consumable_for_n09_hypothesis_b_inventory": True,
                "consumable_as_native_regulation_policy": False,
            },
        },
        "hypothesis_b_staged_status": {
            "status": "staged",
            "b0_inventory": "complete_iteration_1",
            "b0_considered_surfaces": [
                {
                    "surface_id": "n05_oscillator_route_aspect",
                    "possible_role": "proxy_carrier_or_circuit_background",
                    "current_limit": "no native route conductance memory or regulation policy",
                    "usable_for_b1": "secondary_fixture_after_simple_proxy_path",
                },
                {
                    "surface_id": "n06_native_route_candidate_score_components",
                    "possible_role": "proxy_conditioned route-score carrier",
                    "current_limit": "selection-only; no inherited packet execution",
                    "usable_for_b1": "yes_as_selection_surface_not_correction_execution",
                },
                {
                    "surface_id": "n07_identity_support_area_digest",
                    "possible_role": "identity/support preservation anchor",
                    "current_limit": "not runtime regulated variable; withdrawal baseline untested",
                    "usable_for_b1": "anchor_only_not_proxy_surface",
                },
                {
                    "surface_id": "n08_static_positive_geometry_route_response",
                    "possible_role": "substrate-mediated response design direction",
                    "current_limit": "static response only; native regulation policy missing",
                    "usable_for_b1": "yes_as_design_direction_not_native_policy",
                },
            ],
            "b1_probe": (
                "planned_after_hypothesis_a_identifies_load_bearing_proxy_"
                "variables_and_response_laws"
            ),
            "b2_native_absorption_blocker": "native_goal_proxy_regulation_policy_missing",
            "not_discarded": True,
            "full_native_absorption_deferred": True,
        },
        "available_proxy_measurement_surfaces": [
            {
                "surface_id": "active_node_coherence_band",
                "source": "LGRC runtime active node state and packet ledger",
                "runtime_visible": True,
                "native": True,
                "preferred_default_fixture": True,
                "budget_auditable": True,
            },
            {
                "surface_id": "route_arbitration_context_surface",
                "source": "N06 candidate context values and source surface digests",
                "runtime_visible": True,
                "native": True,
                "preferred_default_fixture": False,
                "budget_auditable": False,
                "regulation_constraint": (
                    "selection surface only; cannot supply GPR4+ packet "
                    "execution without an N09 scheduling/processing lane"
                ),
            },
            {
                "surface_id": "n08_serialized_memory_surface_strength",
                "source": "N08 Hypothesis A memory surface rows",
                "runtime_visible": True,
                "native": False,
                "preferred_default_fixture": False,
                "budget_auditable": "memory_budget_only_not_node_plus_packet",
            },
            {
                "surface_id": "n07_identity_support_area",
                "source": "N07 ID6 support area and activity history digests",
                "runtime_visible": False,
                "native": False,
                "preferred_default_fixture": False,
                "budget_auditable": False,
                "regulation_constraint": (
                    "identity/support anchor only; cannot be used directly as "
                    "regulated_variable_surface"
                ),
            },
            {
                "surface_id": "n05_oscillator_return_amount",
                "source": "N05 O5 self-rearm return amount",
                "runtime_visible": True,
                "native": True,
                "preferred_default_fixture": False,
                "budget_auditable": True,
                "secondary_fixture_fields": [
                    "return_amount",
                    "return_route_id",
                    "cycle_definition",
                    "cycle_ids",
                    "route_aspect_digest",
                    "channel_sequence_digest",
                ],
            },
        ],
        "available_proxy_conditioned_action_surfaces": [
            {
                "surface_id": "producer_scheduling_eligibility_record",
                "source": "committed runtime-visible state observed by producer",
                "allowed_boundary": "producer schedules_only_step_mutates",
                "native": False,
            },
            {
                "surface_id": "native_route_candidate_score_components",
                "source": "LGRC9V3 route arbitration candidate records",
                "allowed_boundary": "serialized_runtime_visible_score_components",
                "native": True,
            },
            {
                "surface_id": "n08_memory_shaped_candidate_score_components",
                "source": "N08 Hypothesis A memory score components",
                "allowed_boundary": "artifact-backed memory-shaped comparator",
                "native": False,
            },
            {
                "surface_id": "n08_static_positive_geometry_route_response",
                "source": "N08 Hypothesis B positive geometry route response",
                "allowed_boundary": "staged_hypothesis_b_design_direction",
                "native": "partial_static_geometry_response_only",
            },
        ],
        "missing_native_policy_surfaces": missing_native_policy_surfaces,
        "gpr_ladder": gpr_ladder,
        "frozen_gpr_row_schema": gpr_row_schema,
        "regulation_outcome_taxonomy": regulation_outcome_taxonomy,
        "ceiling_algorithm": {
            "rule": (
                "ceiling equals highest GPR level whose required gates pass; "
                "later gate failure falls back to strongest passing level and "
                "records primary blocker"
            ),
            "fallback_examples": {
                "artifact_replay_fails_after_gpr5": {
                    "ceiling": "repeated_bounded_proxy_regulation_candidate",
                    "blocker": "artifact_only_goal_proxy_replay_failed",
                },
                "repeated_windows_fail_after_gpr4": {
                    "ceiling": "single_cycle_proxy_correction_candidate",
                    "blocker": "repeated_regulation_not_bounded",
                },
                "correction_absent_after_gpr3": {
                    "ceiling": "proxy_conditioned_route_selection_candidate",
                    "blocker": "no_response_to_error",
                },
            },
            "identity_support_rule": (
                "identity/support disruption blocks N10 consumption but does "
                "not automatically erase lower valid proxy-regulation evidence"
            ),
        },
        "n10_handoff_fields": n10_handoff_fields,
        "downstream_iteration_constraints": {
            "iteration_2": [
                {
                    "constraint_id": "n06_selection_only_no_packet_execution",
                    "severity": "high",
                    "requirement": (
                        "Fixture contract must create N09 packet scheduling/"
                        "processing evidence for GPR4+ instead of inheriting it "
                        "from N06."
                    ),
                },
                {
                    "constraint_id": "n06_candidate_source_surface_required",
                    "severity": "medium",
                    "requirement": (
                        "Any N06 route-arbitration surface consumed by N09 must "
                        "preserve committed source surface provenance and reject "
                        "unknown source digests."
                    ),
                },
            ],
            "iteration_8": [
                {
                    "constraint_id": "n07_withdrawal_baseline_not_tested",
                    "severity": "high",
                    "requirement": (
                        "Identity/support disruption tags need a baseline or "
                        "control because N07 withdrawal stability was not tested."
                    ),
                }
            ],
        },
        "claim_flags": claim_flags,
    }

    checks = {
        "n05_status_passed": inventory["n05_inventory"]["status"] == "passed",
        "n05_o5_inventory_present": inventory["n05_inventory"][
            "strongest_supported_o_level"
        ]
        == "O5",
        "n05_o6_blocker_recorded": inventory["n05_inventory"]["o6_primary_blocker"]
        == "missing_route_conductance_memory_policy",
        "n06_status_passed": inventory["n06_inventory"]["status"] == "passed",
        "n06_sc6_inventory_present": inventory["n06_inventory"][
            "strongest_supported_sc_level"
        ]
        == "SC6",
        "n06_selection_scope_constraint_recorded": inventory["n06_inventory"][
            "selection_scope"
        ]
        == "selection_only_pre_topology_commit"
        and not inventory["n06_inventory"]["regulation_constraint"][
            "packet_execution_inherited_from_n06"
        ],
        "n06_route_arbitration_records_present": inventory["n06_inventory"][
            "native_route_arbitration_records_present"
        ],
        "n06_selected_rejected_digests_present": all(
            bool(row["selected_candidate_route_digest"])
            and isinstance(row["rejected_candidate_route_digests"], list)
            for row in n06_cycles
        ),
        "n06_unknown_source_blocker_carried_forward": (
            "native_route_candidate_committed_source_surface_required"
            in inventory["n06_inventory"]["source_provenance_constraints"][
                "unknown_source_blockers"
            ]
        ),
        "n07_status_passed": inventory["n07_inventory"]["status"] == "passed",
        "n07_id6_inventory_present": inventory["n07_inventory"][
            "frozen_n07_ceiling"
        ]
        == "ID6",
        "n07_support_digest_present": bool(
            inventory["n07_inventory"]["support_area_digest"]
        ),
        "n07_withdrawal_precondition_gap_recorded": inventory["n07_inventory"][
            "identity_preservation_precondition_gap"
        ]["withdrawal_test_status"]
        == "not_tested",
        "n07_support_dependency_status_recorded": inventory["n07_inventory"][
            "identity_support_fields_for_n09"
        ]["support_dependency_status"]
        == "regime_assisted",
        "n08_hypothesis_a_passed": inventory["n08_inventory"]["hypothesis_a"][
            "status"
        ]
        == "passed",
        "n08_hypothesis_a_consumable_for_memory_lane": inventory["n08_inventory"][
            "hypothesis_a"
        ]["consumable_for_n09_memory_shaped_lane"],
        "n08_mem5_candidate_fields_present": inventory["n08_inventory"][
            "hypothesis_a"
        ]["mem5_candidate_fields"]["present"],
        "n08_memory_rows_have_route_id": all(
            not row["route_id_missing"]
            for row in inventory["n08_inventory"]["hypothesis_a"][
                "sample_memory_surface_rows"
            ]
        ),
        "n08_n07_support_anchor_consistency_checked": inventory["n08_inventory"][
            "hypothesis_a"
        ]["support_anchor_consistency"]["all_source_support_digests_match_n07"]
        and inventory["n08_inventory"]["hypothesis_a"]["support_anchor_consistency"][
            "all_target_support_digests_match_n07_11b"
        ],
        "n08_hypothesis_b_passed": inventory["n08_inventory"]["hypothesis_b"][
            "status"
        ]
        == "passed",
        "n08_hypothesis_b_staged_not_native_regulation": (
            inventory["n08_inventory"]["hypothesis_b"][
                "consumable_for_n09_hypothesis_b_inventory"
            ]
            and not inventory["n08_inventory"]["hypothesis_b"][
                "consumable_as_native_regulation_policy"
            ]
        ),
        "hypothesis_b_staged_status_recorded": inventory["hypothesis_b_staged_status"][
            "status"
        ]
        == "staged",
        "hypothesis_b_b0_inventory_complete": len(
            inventory["hypothesis_b_staged_status"]["b0_considered_surfaces"]
        )
        >= 4,
        "native_goal_proxy_blocker_recorded": (
            "native_goal_proxy_regulation_policy_missing"
            in inventory["missing_native_policy_surfaces"]
        ),
        "proxy_measurement_surfaces_inventoried": len(
            inventory["available_proxy_measurement_surfaces"]
        )
        >= 5,
        "proxy_conditioned_action_surfaces_inventoried": len(
            inventory["available_proxy_conditioned_action_surfaces"]
        )
        >= 4,
        "gpr_ladder_complete": sorted(inventory["gpr_ladder"]) == [
            "GPR0",
            "GPR1",
            "GPR2",
            "GPR3",
            "GPR4",
            "GPR5",
            "GPR6",
        ],
        "gpr_row_schema_has_proxy_fields": all(
            field in inventory["frozen_gpr_row_schema"]
            for field in (
                "proxy_kind",
                "measurement_value",
                "error_value",
                "node_plus_packet_budget_error",
            )
        ),
        "regulation_outcome_taxonomy_frozen": (
            "memory_poisoning" in inventory["regulation_outcome_taxonomy"]
            and "native_policy_gap" in inventory["regulation_outcome_taxonomy"]
        ),
        "ceiling_algorithm_frozen": bool(inventory["ceiling_algorithm"]["rule"]),
        "n10_handoff_fields_frozen": all(
            field in inventory["n10_handoff_fields"]
            for field in (
                "goal_proxy_regulation_policy_digest",
                "proxy_surface_digest",
                "regulation_outcome_tag",
                "native_policy_gap_records",
            )
        ),
        "claim_flags_all_false": all(
            value is False for value in inventory["claim_flags"].values()
        ),
        "no_regulation_probe_run": inventory["regulation_probe_run"] is False,
        "src_clean_for_iteration_1": inventory["git"]["src_clean"],
    }
    inventory["checks"] = checks
    inventory["acceptance"] = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 1 passes if N09 has a source-backed inventory of "
            "inherited N05/N06/N07/N08 artifacts, available proxy/regulation "
            "surfaces, missing native policy surfaces, Hypothesis B staged "
            "status, memory and identity/support source fields, frozen GPR row "
            "schema, regulation outcome taxonomy, ceiling algorithm, N10 "
            "handoff fields, clean claim boundaries, and no regulation probe "
            "execution."
        ),
    }
    inventory["inventory_digest_scope"] = {
        "included": "all fields except generated_at, inventory_digest, and git metadata",
        "excluded": ["generated_at", "inventory_digest", "git"],
        "stable_across_same_inputs": True,
    }
    inventory["inventory_digest"] = inventory_stable_digest(inventory)
    inventory["status"] = inventory["acceptance"]["status"]
    return inventory


def write_report(inventory: dict[str, Any]) -> None:
    checks = inventory["checks"]
    check_lines = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(checks.items())
    )
    blocker_lines = "\n".join(
        f"- `{blocker}`" for blocker in inventory["missing_native_policy_surfaces"]
    )
    schema_lines = "\n".join(
        f"- `{field}`" for field in inventory["frozen_gpr_row_schema"]
    )
    outcome_lines = "\n".join(
        f"- `{tag}`" for tag in inventory["regulation_outcome_taxonomy"]
    )
    handoff_lines = "\n".join(
        f"- `{field}`" for field in inventory["n10_handoff_fields"]
    )
    proxy_surface_lines = "\n".join(
        "- `{surface_id}`: native=`{native}`, source={source}".format(**surface)
        for surface in inventory["available_proxy_measurement_surfaces"]
    )
    action_surface_lines = "\n".join(
        "- `{surface_id}`: native=`{native}`, boundary={allowed_boundary}".format(
            **surface
        )
        for surface in inventory["available_proxy_conditioned_action_surfaces"]
    )
    n05 = inventory["n05_inventory"]
    n06 = inventory["n06_inventory"]
    n07 = inventory["n07_inventory"]
    n08_a = inventory["n08_inventory"]["hypothesis_a"]
    n08_b = inventory["n08_inventory"]["hypothesis_b"]
    hyp_b = inventory["hypothesis_b_staged_status"]
    downstream_constraints = inventory["downstream_iteration_constraints"]
    support_anchor_consistency = n08_a["support_anchor_consistency"]

    report = f"""# N09 Iteration 1 Baseline And Source Inventory

Status: `{inventory['status']}`.

## Result

Iteration 1 built a source-backed inventory from existing N05, N06, N07, and
N08 artifacts only. No N09 regulation probe was run.

The starting boundary is:

```text
GPR evidence = not yet produced
default fixture = directly budget-auditable node coherence band
N08 Hypothesis A = consumable as serialized memory-shaped evidence
N08 Hypothesis B = staged native/substrate-mediated question, not discarded
full native absorption blocker = native_goal_proxy_regulation_policy_missing
goal_proxy_regulation_claim_allowed = false
```

## Inherited Sources

N05:

- strongest O-level: `{n05['strongest_supported_o_level']}`
- claim ceiling: `{n05['strongest_claim_ceiling']}`
- O5 cycle count: `{n05['o5_cycle_count']}`
- O5 return amount: `{n05['o5_return_amount']}`
- O5 return route: `{n05['o5_return_route_id']}`
- O6 supported: `{n05['o6_supported']}`
- O6 blocker: `{n05['o6_primary_blocker']}`
- oscillator regulation fixture status:
  `{n05['oscillator_regulation_fixture_status']}`

N06:

- strongest SC-level: `{n06['strongest_supported_sc_level']}`
- claim ceiling: `{n06['strongest_claim_ceiling']}`
- selection scope: `{n06['selection_scope']}`
- context/affordance evidence present:
  `{n06['context_affordance_evidence_present']}`
- native route-arbitration records present:
  `{n06['native_route_arbitration_records_present']}`
- selected/rejected digest rows: `{len(n06['selected_rejected_route_digest_rows'])}`
- packet execution inherited by N09:
  `{n06['regulation_constraint']['packet_execution_inherited_from_n06']}`
- committed-source blocker carried forward:
  `{n06['source_provenance_constraints']['unknown_source_blockers']}`

N07:

- frozen ceiling: `{n07['frozen_n07_ceiling']}`
- trajectory regime: `{n07['strongest_trajectory_regime']}`
- support area id: `{n07['support_area_id']}`
- support area digest: `{n07['support_area_digest']}`
- identity acceptance allowed: `{n07['identity_acceptance_claim_allowed']}`
- support dependency status:
  `{n07['identity_support_fields_for_n09']['support_dependency_status']}`
- withdrawal test status:
  `{n07['identity_support_fields_for_n09']['withdrawal_test_status']}`

N08 Hypothesis A:

- MEM level: `{n08_a['mem_level']}`
- claim ceiling: `{n08_a['claim_ceiling']}`
- claim scope: `{n08_a['memory_or_trail_claim_scope']}`
- consumable for N09 memory-shaped lane:
  `{n08_a['consumable_for_n09_memory_shaped_lane']}`
- boundary: `{n08_a['consumption_boundary']}`
- N08/N07 support-anchor consistency:
  source match = `{support_anchor_consistency['all_source_support_digests_match_n07']}`,
  target match = `{support_anchor_consistency['all_target_support_digests_match_n07_11b']}`

N08 Hypothesis B:

- claim ceiling: `{n08_b['claim_ceiling']}`
- status: `{n08_b['status_detail']}`
- current blocker: `{n08_b['current_blocker']}`
- static positive geometry response persisted:
  `{n08_b['static_positive_geometry_response_persisted']}`
- consumable as native regulation policy:
  `{n08_b['consumable_as_native_regulation_policy']}`

## Hypothesis B Staging

Hypothesis B is staged, not discarded:

```json
{json.dumps(hyp_b, indent=2, sort_keys=True)}
```

The inventory closes B0. B1 should only run after the A-path identifies which
proxy variables and response laws are load-bearing. B2 remains blocked for full
native absorption until a minimal LGRC-native policy surface is identified.

## Downstream Constraints

Iteration 2 constraints:

```json
{json.dumps(downstream_constraints['iteration_2'], indent=2, sort_keys=True)}
```

Iteration 8 constraints:

```json
{json.dumps(downstream_constraints['iteration_8'], indent=2, sort_keys=True)}
```

The two material boundaries are:

```text
N06 is selection-only and has no scheduled/processed packet evidence for GPR4+.
N07 withdrawal stability is not tested, so N09 identity/support disruption
tags need their own baseline or control.
```

## Available Surfaces

Proxy measurement surfaces:

{proxy_surface_lines}

Proxy-conditioned action surfaces:

{action_surface_lines}

Missing native policy surfaces:

{blocker_lines}

## Frozen GPR Schema

The GPR ladder is frozen as evidence classification only. Claim flags remain
separate.

Frozen row fields:

{schema_lines}

## Regulation Outcome Taxonomy

{outcome_lines}

## Ceiling Algorithm

{inventory['ceiling_algorithm']['rule']}

Identity/support disruption blocks N10 consumption but does not automatically
erase lower valid N09 proxy-regulation evidence.

## N10 Handoff Fields

{handoff_lines}

## Claim Boundary

All N09 claim flags are false in Iteration 1. Inherited N08 memory evidence may
be cited as source evidence, but N09 has not yet produced goal-proxy regulation.

```json
{json.dumps(inventory['claim_flags'], indent=2, sort_keys=True)}
```

## Checks

| Check | Passed |
|---|---|
{check_lines}

## Source Artifact Digests

```json
{json.dumps(inventory['source_artifacts'], indent=2, sort_keys=True)}
```

## Source Report Digests

```json
{json.dumps(inventory['source_reports'], indent=2, sort_keys=True)}
```

## Acceptance Result

Achieved: `{inventory['acceptance']['achieved']}`.

Inventory digest: `{inventory['inventory_digest']}`.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    inventory = build_inventory()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(inventory)


if __name__ == "__main__":
    main()
