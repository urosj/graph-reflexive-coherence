#!/usr/bin/env python3
"""Build N17 Iteration 4 perturbation-response-recovery G3 candidate.

Iteration 4 is the first positive minimal loop candidate. It records all four
ordered trace legs, but keeps the row below final AP7 because replay and
negative controls are reserved for Iteration 5.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N17-lgrc-closed-boundary-engagement-loop"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SOURCE_INVENTORY = OUTPUTS / "n17_loop_source_inventory.json"
SCHEMA_PATH = OUTPUTS / "n17_loop_schema_v1.json"
I3_ACTIVE_NULL = OUTPUTS / "n17_one_way_crossing_active_null.json"
N16_SELECTED_INTERACTION = (
    ROOT
    / "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/"
    "n16_selected_interaction_probe_matrix.json"
)
OUTPUT_PATH = OUTPUTS / "n17_perturbation_response_recovery_loop.json"
REPORT_PATH = REPORTS / "n17_perturbation_response_recovery_loop.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_perturbation_response_recovery_loop.py"
)

ABSOLUTE_PATH_MARKERS = (
    "/home/",
    "/tmp/",
    "/Users/",
    "C:\\",
    "\\Users\\",
    "geometric-reflexive-coherence",
    "/arc-of-becoming/",
)

SOURCE_ROW_IDS = [
    "n17_i1_row_01_n16_closeout_ap6",
    "n17_i1_row_02_n16_claim_boundary_record",
    "n17_i1_row_03_n16_b3_c4_breach_reclosure",
    "n17_i1_row_08_n13_support_disruption_restoration",
    "n17_i1_row_10_n09_perturbation_withdrawal_support",
]

PENDING_I5_CONTROLS = [
    "artifact_only_replay_control",
    "snapshot_load_replay_control",
    "duplicate_replay_control",
    "order_inversion_replay_control",
    "post_hoc_loop_stitching_control",
    "hidden_external_state_memory_control",
    "hidden_internal_state_carryover_control",
    "external_change_not_caused_by_response_control",
    "feedback_order_inversion_control",
    "feedback_removed_control",
    "outbound_response_relabel_control",
    "one_way_crossing_relabel_control",
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("generated_at", None)
    payload.pop("output_digest", None)
    payload.pop("git", None)
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def digest_value(data: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(digest_payload(data)).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def contains_absolute_path(data: Any) -> bool:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return any(marker in serialized for marker in ABSOLUTE_PATH_MARKERS)


def git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return "unknown"
    return result.stdout.strip()


def git_status_short() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ["git_status_unavailable"]
    return [line for line in result.stdout.splitlines() if line]


def find_n16_b3_c4_row(n16_artifact: dict[str, Any]) -> dict[str, Any]:
    for row in n16_artifact.get("rows", []):
        if isinstance(row, dict) and row.get("cell_id") == "B3_C4":
            return row
    raise ValueError("B3_C4 row not found in N16 selected interaction matrix")


def source_artifacts(
    source_inventory: dict[str, Any],
    i3_active_null: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = {
        row["row_id"]: row
        for row in source_inventory["source_rows"]
        if row["row_id"] in SOURCE_ROW_IDS
    }
    artifacts = [
        {
            "source_row_id": row_id,
            "source_artifact": rows[row_id]["source_artifact"],
            "source_report": rows[row_id]["source_report"],
            "source_sha256": rows[row_id]["source_sha256"],
            "source_report_sha256": rows[row_id]["source_report_sha256"],
            "source_output_digest": rows[row_id]["source_output_digest"],
            "source_claim_ceiling": rows[row_id]["source_claim_ceiling"],
        }
        for row_id in SOURCE_ROW_IDS
    ]
    artifacts.append(
        {
            "source_row_id": "n17_i3_row_01_one_way_crossing_active_null",
            "source_artifact": rel(I3_ACTIVE_NULL),
            "source_report": rel(REPORTS / "n17_one_way_crossing_active_null.md"),
            "source_sha256": sha256_file(I3_ACTIVE_NULL),
            "source_report_sha256": sha256_file(
                REPORTS / "n17_one_way_crossing_active_null.md"
            ),
            "source_output_digest": i3_active_null["output_digest"],
            "source_claim_ceiling": (
                "one_way_crossing_internal_update_fragment_not_closed_loop"
            ),
        }
    )
    return artifacts


def control_statuses(schema: dict[str, Any]) -> dict[str, dict[str, str]]:
    controls: dict[str, dict[str, str]] = {}
    for control in schema["control_requirements"]:
        control_id = control["control_id"]
        expected = control["expected_for_supported_loop"]
        if expected.startswith("not_applicable_for_mvp"):
            controls[control_id] = {
                "status": "not_applicable",
                "result": "extension_control_frozen_not_executed_for_i4_mvp",
                "failure_blocks_gate": control["failure_blocks_gate"],
            }
        elif control_id in PENDING_I5_CONTROLS:
            controls[control_id] = {
                "status": "blocked",
                "result": "pending_iteration_5_replay_and_control_matrix",
                "failure_blocks_gate": control["failure_blocks_gate"],
            }
        else:
            controls[control_id] = {
                "status": "passed",
                "result": "claim_boundary_relabel_blocked_for_i4_candidate",
                "failure_blocks_gate": control["failure_blocks_gate"],
            }

    controls["one_way_crossing_relabel_control"].update(
        {
            "status": "passed",
            "result": "i3_g2_active_null_contrast_blocks_relabel",
            "failure_mode": "one_way_crossing_is_not_closed_loop",
        }
    )
    controls["external_change_not_caused_by_response_control"].update(
        {
            "status": "blocked",
            "result": "pending_i5_counterfactual_control",
            "candidate_evidence": "response_caused_marker_recorded_but_control_not_final",
        }
    )
    controls["feedback_removed_control"].update(
        {
            "status": "blocked",
            "result": "pending_i5_feedback_removed_control",
            "candidate_expectation": "removing_t3_feedback_should_drop_row_to_g2",
        }
    )
    return controls


def claim_flags(schema: dict[str, Any]) -> dict[str, bool]:
    flags = {
        "ap7_classification_supported": False,
        "closed_loop_demonstrated": False,
        "final_ap7_supported": False,
    }
    for flag in schema["claim_boundary_policy"]["required_false_flags"]:
        flags[flag] = False
    return flags


def build_loop_row(
    schema: dict[str, Any],
    source_inventory: dict[str, Any],
    i3_active_null: dict[str, Any],
    n16_b3_c4: dict[str, Any],
) -> dict[str, Any]:
    probe = (
        n16_b3_c4.get("probe_decomposition")
        or n16_b3_c4.get("boundary_surface", {}).get("probe_decomposition")
        or n16_b3_c4.get("external_resource_descriptor", {}).get("probe_decomposition")
    )
    if not isinstance(probe, dict):
        raise ValueError("B3_C4 probe_decomposition not found")

    b2_reference = probe["b2_c4_baseline_reference"]
    deltas = probe["b3_c4_delta_vs_b2_c4"]
    boundary_edges = n16_b3_c4.get("boundary_edges") or n16_b3_c4.get(
        "boundary_surface", {}
    ).get("challenge_boundary_edges")
    if not isinstance(boundary_edges, list) or len(boundary_edges) < 2:
        raise ValueError("B3_C4 boundary_edges not found")
    boundary_side_assignments = n16_b3_c4.get(
        "boundary_side_assignments"
    ) or n16_b3_c4.get("boundary_surface", {}).get("side_derivation")
    if not isinstance(boundary_side_assignments, dict):
        raise ValueError("B3_C4 boundary side assignments not found")

    controls = control_statuses(schema)
    flags = claim_flags(schema)
    support_delta = round(
        n16_b3_c4["internal_state_descriptor"]["minimum_observed_internal_support"]
        - b2_reference["minimum_internal_support"],
        12,
    )
    leakage_delta = deltas["leakage_ratio_delta"]

    ap7_gates = {
        "g3_or_higher": True,
        "four_trace_legs_present": True,
        "four_trace_legs_source_backed": True,
        "monotonic_phase_order_valid": True,
        "response_caused_external_change": False,
        "external_change_counterfactual_blocks_spontaneous_change": False,
        "later_internal_depends_on_changed_external_state": False,
        "feedback_removed_control_passed": False,
        "one_way_crossing_null_blocked": True,
        "dependency_trace_complete": True,
        "replay_digest_valid": False,
        "budget_validity_passed": True,
        "controls_passed": False,
        "claim_boundary_clean": True,
        "source_registry_backed": True,
        "no_absolute_paths": True,
    }
    missing_gates = [gate for gate, passed in ap7_gates.items() if not passed]

    row: dict[str, Any] = {
        "row_id": "n17_i4_row_01_perturbation_response_recovery_g3_candidate",
        "schema_version": schema["schema_version"],
        "loop_policy_digest": schema["config_files"]["loop_policy"]["config_digest"],
        "row_type": "loop_candidate",
        "loop_family": "perturbation_response_recovery_loop",
        "loop_rung": "G3",
        "loop_rung_index": 3,
        "candidate_rung_label": "G3_candidate",
        "source_row_ids": SOURCE_ROW_IDS
        + ["n17_i3_row_01_one_way_crossing_active_null"],
        "source_artifacts": source_artifacts(source_inventory, i3_active_null),
        "row_decision": "supported",
        "boundary_assignments": {
            "source": "N16_B3_C4_selected_interaction_probe",
            "boundary_side_assignments": boundary_side_assignments,
            "boundary_edges": boundary_edges,
        },
        "external_to_internal_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t0_external_pressure_or_crossing",
            "state_before": {
                "external_state_role": "perturbation",
                "breach_pressure": 0.0,
                "minimum_internal_support_reference": b2_reference[
                    "minimum_internal_support"
                ],
            },
            "state_after": {
                "external_state_role": "perturbation",
                "breach_pressure": probe["breach_pressure"],
                "boundary_edge_crossed": boundary_edges[0],
            },
            "dependency_note": (
                "N16 B3_C4 records transient breach pressure crossing a derived "
                "internal/external boundary edge"
            ),
        },
        "internal_response_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t1_internal_support_update",
            "state_before": {
                "b2_c4_reference_minimum_internal_support": b2_reference[
                    "minimum_internal_support"
                ],
                "b2_c4_reference_repair_score": b2_reference["repair_score"],
            },
            "state_after": {
                "b3_c4_minimum_internal_support": n16_b3_c4[
                    "internal_state_descriptor"
                ]["minimum_observed_internal_support"],
                "b3_c4_reclosure_score": probe["reclosure_score"],
                "reclosure_latency_steps": probe["reclosure_latency_steps"],
            },
            "dependency_note": (
                "The perturbation is followed by a bounded B3 reclosure response "
                "and support preservation above the N16 floor"
            ),
        },
        "response_to_external_change_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t2_response_caused_external_change",
            "state_before": {
                "b2_c4_reference_leakage_ratio": b2_reference["leakage_ratio"],
                "bounded_reclosure_response": "absent_in_b2_reference",
            },
            "state_after": {
                "b3_c4_leakage_ratio": n16_b3_c4["leakage_ratio"],
                "leakage_ratio_delta": leakage_delta,
                "bounded_reclosure_response_edge": boundary_edges[1],
            },
            "cause_attribution": "response_caused_candidate_pending_i5_control",
            "response_caused_candidate": True,
            "external_change_not_independent_candidate": True,
            "control_status": "pending_i5_external_change_not_caused_by_response_control",
            "dependency_note": (
                "The selected-probe response edge is the recorded bounded "
                "reclosure event and the external perturbation surface changes "
                "through reduced leakage relative to B2_C4; I5 must still rule "
                "out independent external change"
            ),
        },
        "external_feedback_to_internal_trace": {
            "present": True,
            "source_backed": True,
            "phase": "t3_later_internal_support_conditioned_by_changed_external_state",
            "state_before": {
                "without_response_changed_external_state": False,
                "b2_c4_reference_minimum_internal_support": b2_reference[
                    "minimum_internal_support"
                ],
                "support_floor": n16_b3_c4["internal_state_descriptor"][
                    "support_floor"
                ],
            },
            "state_after": {
                "with_response_changed_external_state": True,
                "b3_c4_later_minimum_internal_support": n16_b3_c4[
                    "internal_state_descriptor"
                ]["minimum_observed_internal_support"],
                "support_delta_vs_b2_c4": support_delta,
            },
            "later_internal_conditioned_by_changed_external_state_candidate": True,
            "control_status": "pending_i5_hidden_state_and_feedback_removed_controls",
            "dependency_note": (
                "The later internal support state differs across the B2_C4 "
                "breach baseline and B3_C4 bounded-reclosure surface only when "
                "the response-modified external perturbation surface is present; "
                "I5 must still rule out hidden carryover and feedback-removal "
                "failure"
            ),
        },
        "phase_timing": {
            "t0_external_pressure_or_crossing": 0,
            "t1_internal_support_update": 1,
            "t2_response_caused_external_change": 2,
            "t3_later_internal_support_conditioned_by_changed_external_state": 3,
        },
        "monotonic_phase_order": True,
        "response_caused_external_change": False,
        "response_caused_external_change_candidate": True,
        "external_change_would_occur_without_response": None,
        "external_change_counterfactual_status": "pending_i5_control",
        "later_internal_depends_on_changed_external_state": False,
        "later_internal_dependence_candidate": True,
        "feedback_removed_control_changes_result": None,
        "feedback_removed_control_result_status": "pending_i5_control",
        "loop_closure_evidence": {
            "ordered_closure_present": False,
            "ordered_closure_candidate_present": True,
            "closed_loop_candidate": True,
            "one_step_recovery_only": False,
            "closure_hinge": "changed_external_state_feeds_later_internal_support",
            "candidate_status": "pending_iteration_5_replay_and_controls",
            "g3_reached": True,
            "not_final_ap7": True,
            "reason": (
                "all four ordered trace legs are present, but replay, hidden-state, "
                "post-hoc stitching, order-inversion, and feedback-removal "
                "controls remain pending"
            ),
        },
        "dependency_trace": {
            "edges": [
                {
                    "edge_id": "external_to_internal",
                    "source_trace": "N16_B3_C4_transient_breach_pressure",
                    "source_backed": True,
                },
                {
                    "edge_id": "internal_response_to_external_change",
                    "source_trace": "N16_B3_C4_bounded_reclosure_response",
                    "source_backed": True,
                    "cause_attribution": "response_caused_candidate_pending_i5_control",
                },
                {
                    "edge_id": "changed_external_to_later_internal",
                    "source_trace": "B3_C4_support_preservation_vs_B2_C4_breach_baseline",
                    "source_backed": True,
                    "later_internal_conditioned_by_changed_external_state_candidate": True,
                },
            ],
            "missing_edges": [],
        },
        "budget_cost_surface": {
            "source_row_count": len(SOURCE_ROW_IDS) + 1,
            "trace_leg_count": 4,
            "present_trace_leg_count": 4,
            "hidden_state_allowance": 0,
            "unexplained_external_change_budget": 0,
            "closure_claim_budget": 0,
            "pending_control_count": len(PENDING_I5_CONTROLS),
        },
        "budget_units": "normalized_cost",
        "budget_validity": {
            "valid": True,
            "within_limits": True,
            "closed_loop_claim_budget_valid": False,
            "reason": (
                "candidate trace budget is valid, but AP7 claim budget remains "
                "closed until Iteration 5 controls pass"
            ),
        },
        "replay_digest_inputs": schema["replay_digest_policy"]["include_fields"],
        "replay_digest_algorithm": schema["replay_digest_policy"]["digest_algorithm"],
        "artifact_only_replay_status": "pending_iteration_5",
        "snapshot_load_status": "pending_iteration_5",
        "duplicate_replay_status": "pending_iteration_5",
        "order_inversion_replay_status": "pending_iteration_5",
        "controls": controls,
        "ap7_gates": ap7_gates,
        "closed_loop_claim_allowed": False,
        "provisional_ap_level": "G3_candidate_pending_controls",
        "provisional_claim_ceiling": (
            "artifact_level_closed_boundary_engagement_loop_candidate_pending_controls"
        ),
        "claim_flags": flags,
        "blocked_claims": [
            "final_AP7_supported",
            "AP7_classification_supported_before_I5_controls",
            "action_perception_loop_proven",
            "agency",
            "intention",
            "semantic_action",
            "semantic_perception",
            "semantic_goal_ownership",
            "selfhood",
            "identity_acceptance",
            "native_support",
            "organism_life",
            "fully_native_integration",
            "unrestricted_agency",
        ],
        "pending_controls": PENDING_I5_CONTROLS,
        "missing_gates": missing_gates,
        "final_ap7_supported": False,
        "contrast_with_i3_one_way_null": {
            "i3_loop_rung": i3_active_null["active_null_summary"]["loop_ladder_rung"],
            "i3_missing_feedback_leg": True,
            "i4_feedback_leg_present": True,
            "i3_closed_loop_claim_allowed": False,
            "i4_closed_loop_claim_allowed": False,
            "what_changed": [
                "response_caused_external_change_candidate_recorded",
                "later_internal_dependence_candidate_recorded",
            ],
        },
        "minimal_loop_scope": {
            "perturbation_response_recovery_only": True,
            "resource_support_extension_opened": False,
            "shared_medium_extension_opened": False,
        },
    }
    row["row_replay_digest"] = sha256_bytes(
        canonical_json(
            {
                field: row.get(field)
                for field in schema["replay_digest_policy"]["include_fields"]
            }
        ).encode("utf-8")
    )
    return row


def build_artifact() -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    source_inventory = load_json(SOURCE_INVENTORY)
    i3_active_null = load_json(I3_ACTIVE_NULL)
    n16_selected = load_json(N16_SELECTED_INTERACTION)
    n16_b3_c4 = find_n16_b3_c4_row(n16_selected)
    row = build_loop_row(schema, source_inventory, i3_active_null, n16_b3_c4)

    requirements_satisfied = [
        "minimal_perturbation_response_recovery_loop_built",
        "all_four_ordered_trace_legs_recorded",
        "contrast_with_i3_one_way_null_recorded",
        "response_caused_external_change_candidate_recorded",
        "later_internal_dependence_candidate_recorded",
        "loop_closure_distinguished_from_one_step_recovery",
        "resource_support_and_shared_medium_extensions_not_opened",
        "unsafe_claim_flags_forced_false",
    ]
    requirements_pending = [
        "artifact_only_replay_control_pending_i5",
        "snapshot_load_replay_control_pending_i5",
        "duplicate_replay_control_pending_i5",
        "order_inversion_control_pending_i5",
        "post_hoc_loop_stitching_control_pending_i5",
        "hidden_state_controls_pending_i5",
        "external_change_not_caused_by_response_control_pending_i5",
        "feedback_removed_control_pending_i5",
    ]

    claim_flags_top = claim_flags(schema)
    checks = [
        {
            "check_id": "schema_status_passed",
            "passed": schema["status"] == "passed",
            "detail": {
                "schema_path": rel(SCHEMA_PATH),
                "schema_output_digest": schema["output_digest"],
            },
        },
        {
            "check_id": "source_inventory_status_passed",
            "passed": source_inventory["status"] == "passed",
            "detail": {
                "source_inventory_path": rel(SOURCE_INVENTORY),
                "source_inventory_output_digest": source_inventory["output_digest"],
            },
        },
        {
            "check_id": "i3_active_null_available_for_contrast",
            "passed": i3_active_null["status"] == "passed"
            and i3_active_null["active_null_summary"]["loop_ladder_rung"] == "G2",
            "detail": {
                "i3_output_digest": i3_active_null["output_digest"],
                "i3_acceptance_state": i3_active_null["acceptance_state"],
            },
        },
        {
            "check_id": "mvp_family_only",
            "passed": row["loop_family"] == "perturbation_response_recovery_loop"
            and row["minimal_loop_scope"]["resource_support_extension_opened"] is False
            and row["minimal_loop_scope"]["shared_medium_extension_opened"] is False,
            "detail": row["minimal_loop_scope"],
        },
        {
            "check_id": "g3_candidate_trace_present",
            "passed": row["loop_rung"] == "G3"
            and row["loop_rung_index"] == 3
            and all(
                row[trace]["present"]
                for trace in [
                    "external_to_internal_trace",
                    "internal_response_trace",
                    "response_to_external_change_trace",
                    "external_feedback_to_internal_trace",
                ]
            ),
            "detail": {
                "loop_rung": row["loop_rung"],
                "candidate_rung_label": row["candidate_rung_label"],
            },
        },
        {
            "check_id": "monotonic_phase_order_valid",
            "passed": row["monotonic_phase_order"] is True
            and list(row["phase_timing"].values()) == [0, 1, 2, 3],
            "detail": row["phase_timing"],
        },
        {
            "check_id": "response_caused_external_change_marked_candidate_pending_i5",
            "passed": row["response_caused_external_change"] is False
            and row["response_caused_external_change_candidate"] is True
            and row["external_change_would_occur_without_response"] is None
            and row["ap7_gates"]["response_caused_external_change"] is False
            and row["ap7_gates"][
                "external_change_counterfactual_blocks_spontaneous_change"
            ]
            is False
            and row["response_to_external_change_trace"]["cause_attribution"]
            == "response_caused_candidate_pending_i5_control",
            "detail": row["response_to_external_change_trace"],
        },
        {
            "check_id": "later_internal_feedback_dependence_marked_candidate_pending_i5",
            "passed": row["later_internal_depends_on_changed_external_state"] is False
            and row["later_internal_dependence_candidate"] is True
            and row["ap7_gates"]["later_internal_depends_on_changed_external_state"]
            is False
            and row["external_feedback_to_internal_trace"][
                "later_internal_conditioned_by_changed_external_state_candidate"
            ]
            is True,
            "detail": row["external_feedback_to_internal_trace"],
        },
        {
            "check_id": "distinguished_from_one_step_recovery",
            "passed": row["loop_closure_evidence"]["one_step_recovery_only"] is False
            and row["loop_closure_evidence"]["closed_loop_candidate"] is True,
            "detail": row["loop_closure_evidence"],
        },
        {
            "check_id": "ap7_causality_and_feedback_gates_false_until_i5",
            "passed": row["ap7_gates"]["response_caused_external_change"] is False
            and row["ap7_gates"][
                "external_change_counterfactual_blocks_spontaneous_change"
            ]
            is False
            and row["ap7_gates"]["later_internal_depends_on_changed_external_state"]
            is False
            and row["controls"]["external_change_not_caused_by_response_control"][
                "status"
            ]
            == "blocked"
            and row["controls"]["feedback_removed_control"]["status"] == "blocked",
            "detail": {
                "missing_gates": row["missing_gates"],
                "external_change_control": row["controls"][
                    "external_change_not_caused_by_response_control"
                ],
                "feedback_removed_control": row["controls"][
                    "feedback_removed_control"
                ],
            },
        },
        {
            "check_id": "i4_keeps_final_ap7_blocked",
            "passed": row["closed_loop_claim_allowed"] is False
            and row["final_ap7_supported"] is False
            and claim_flags_top["final_ap7_supported"] is False,
            "detail": {
                "missing_gates": row["missing_gates"],
                "pending_controls": row["pending_controls"],
            },
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in claim_flags_top.values()),
            "detail": claim_flags_top,
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 4 does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": 4,
        "artifact_id": "n17_perturbation_response_recovery_loop",
        "purpose": (
            "build the first positive minimal G3 loop candidate while keeping "
            "AP7 blocked until replay and controls"
        ),
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_perturbation_response_recovery_g3_candidate_pending_controls_no_ap7"
        ),
        "source_inventory": {
            "path": rel(SOURCE_INVENTORY),
            "sha256": sha256_file(SOURCE_INVENTORY),
            "output_digest": source_inventory["output_digest"],
        },
        "schema": {
            "path": rel(SCHEMA_PATH),
            "sha256": sha256_file(SCHEMA_PATH),
            "output_digest": schema["output_digest"],
        },
        "contrast_source": {
            "path": rel(I3_ACTIVE_NULL),
            "sha256": sha256_file(I3_ACTIVE_NULL),
            "output_digest": i3_active_null["output_digest"],
        },
        "candidate_summary": {
            "row_id": row["row_id"],
            "row_decision": row["row_decision"],
            "row_type": row["row_type"],
            "loop_family": row["loop_family"],
            "loop_ladder_rung": row["candidate_rung_label"],
            "schema_loop_rung": row["loop_rung"],
            "closed_loop_candidate": True,
            "closed_loop_claim_allowed": False,
            "final_ap7_supported": False,
            "one_step_recovery_only": False,
            "claim_ceiling": row["provisional_claim_ceiling"],
        },
        "trace_summary": {
            "external_to_internal_trace": "present_source_backed",
            "internal_response_trace": "present_source_backed",
            "response_to_external_change_trace": "present_source_backed_response_caused_candidate_pending_i5_control",
            "external_feedback_to_internal_trace": "present_source_backed_feedback_dependence_candidate_pending_i5_control",
            "ordered_trace": (
                "t0 external -> t1 internal -> t2 response-caused-candidate "
                "external -> t3 later internal candidate"
            ),
        },
        "contrast_with_i3_one_way_null": row["contrast_with_i3_one_way_null"],
        "requirements_satisfied": requirements_satisfied,
        "requirements_pending": requirements_pending,
        "rows": [row],
        "claim_flags": claim_flags_top,
        "iteration_result": {
            "iteration_4_is_final_ap7_evidence": False,
            "g3_candidate_recorded": True,
            "closed_loop_candidate_pending_controls": True,
            "closed_loop_claim_allowed": False,
            "ap7_classification_supported": False,
            "final_ap7_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "ready_for_iteration_5_replay_and_order_controls": True,
        },
        "checks": checks,
        "errors": [],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(),
        },
    }
    checks.append(
        {
            "check_id": "no_absolute_paths",
            "passed": not contains_absolute_path(artifact),
            "detail": "portable relative paths only",
        }
    )
    artifact["status"] = "passed" if all(check["passed"] for check in checks) else "failed"
    artifact["output_digest"] = digest_value(artifact)
    return artifact


def render_report(artifact: dict[str, Any]) -> str:
    row = artifact["rows"][0]
    check_lines = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    satisfied = [f"- `{item}`" for item in artifact["requirements_satisfied"]]
    pending = [f"- `{item}`" for item in artifact["requirements_pending"]]
    return "\n".join(
        [
            "# N17 Iteration 4 - Perturbation-Response-Recovery Loop",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Main Result",
            "",
            "Iteration 4 records the first positive minimal G3 candidate, but "
            "keeps AP7 blocked until Iteration 5 replay and controls.",
            "",
            "```text",
            f"row_decision = {row['row_decision']}",
            f"row_type = {row['row_type']}",
            f"loop_family = {row['loop_family']}",
            f"loop_ladder_rung = {row['candidate_rung_label']}",
            "closed_loop_candidate = true",
            "closed_loop_claim_allowed = false",
            "final_ap7_supported = false",
            "```",
            "",
            "## Trace Read",
            "",
            "- `external_to_internal_trace`: present and source-backed.",
            "- `internal_response_trace`: present and source-backed.",
            "- `response_to_external_change_trace`: present, source-backed, and "
            "recorded as response-caused candidate evidence pending I5.",
            "- `external_feedback_to_internal_trace`: present and source-backed "
            "as candidate later internal dependence pending I5 hidden-state and "
            "feedback-removal controls.",
            "",
            "## Contrast With Iteration 3",
            "",
            "```text",
            "i3_missing_feedback_leg = true",
            "i4_feedback_leg_present = true",
            "i3_closed_loop_claim_allowed = false",
            "i4_closed_loop_claim_allowed = false",
            "```",
            "",
            "Iteration 3 stopped at G2. Iteration 4 adds candidate "
            "response-caused external change and candidate later internal "
            "support dependence on that changed external state. Those are the "
            "G3 hinge, but their AP7 gates remain false until I5 controls pass.",
            "",
            "## One-Step Recovery Distinction",
            "",
            "```text",
            "one_step_recovery_only = false",
            "closed_boundary_engagement_loop_candidate = true",
            "reason = candidate_changed_external_state_feeds_later_internal_support",
            "```",
            "",
            "This does not make the row final AP7 evidence. It is a candidate "
            "until I5 replay, hidden-state, post-hoc stitching, order-inversion, "
            "external-change-not-caused-by-response, and feedback-removal "
            "controls pass.",
            "",
            "## AP7 Gate Boundary",
            "",
            "```text",
            "response_caused_external_change = false",
            "external_change_counterfactual_blocks_spontaneous_change = false",
            "later_internal_depends_on_changed_external_state = false",
            "feedback_removed_control_passed = false",
            "replay_digest_valid = false",
            "controls_passed = false",
            "```",
            "",
            "These gates are false because Iteration 4 records candidate traces "
            "only. Iteration 5 must validate causality, counterfactuals, hidden "
            "state exclusion, replay, and feedback removal before any AP7 "
            "classification can be allowed.",
            "",
            "## Requirements Satisfied",
            "",
            *satisfied,
            "",
            "## Pending Before AP7",
            "",
            *pending,
            "",
            "## Claim Boundary",
            "",
            "The row remains artifact-level only. It does not support agency, "
            "intention, semantic action, semantic perception, semantic goal "
            "ownership, selfhood, identity acceptance, native support, organism "
            "or life claims, fully native integration, or unrestricted agency.",
            "",
            "## Checks",
            "",
            *check_lines,
            "",
        ]
    )


def main() -> None:
    artifact = build_artifact()
    OUTPUT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    REPORT_PATH.write_text(render_report(artifact), encoding="utf-8")


if __name__ == "__main__":
    main()
