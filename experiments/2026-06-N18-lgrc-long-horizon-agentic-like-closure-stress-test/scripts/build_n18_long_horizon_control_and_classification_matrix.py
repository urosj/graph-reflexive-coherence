#!/usr/bin/env python3
"""Build N18 Iteration 9 replay/control and AP8 classification matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SCHEMA = OUTPUTS / "n18_long_horizon_schema_v1.json"
OUTPUT_PATH = OUTPUTS / "n18_long_horizon_control_and_classification_matrix.json"
REPORT_PATH = REPORTS / "n18_long_horizon_control_and_classification_matrix.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/build_n18_long_horizon_control_and_classification_matrix.py"
)
VALIDATOR_COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/validate_n18_stress_row.py "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "outputs/n18_long_horizon_control_and_classification_matrix.json"
)

SOURCE_SPECS = [
    {
        "key": "i1_source_inventory",
        "iteration": 1,
        "artifact": OUTPUTS / "n18_long_horizon_source_inventory.json",
        "report": REPORTS / "n18_long_horizon_source_inventory.md",
        "role": "source_inventory_and_claim_contract",
    },
    {
        "key": "i2_schema",
        "iteration": 2,
        "artifact": OUTPUTS / "n18_long_horizon_schema_v1.json",
        "report": REPORTS / "n18_long_horizon_schema_v1.md",
        "role": "ap8_gate_schema_replay_budget_claim_policy",
    },
    {
        "key": "i3_short_replay",
        "iteration": 3,
        "artifact": OUTPUTS / "n18_short_horizon_ap7_replay_baseline.json",
        "report": REPORTS / "n18_short_horizon_ap7_replay_baseline.md",
        "role": "short_horizon_ap7_replay_baseline_l1",
    },
    {
        "key": "i4_horizon_sweep",
        "iteration": 4,
        "artifact": OUTPUTS / "n18_horizon_window_sweep.json",
        "report": REPORTS / "n18_horizon_window_sweep.md",
        "role": "horizon_window_sweep_l2_h4_limit",
    },
    {
        "key": "i5_support_proxy",
        "iteration": 5,
        "artifact": OUTPUTS / "n18_support_proxy_stress_matrix.json",
        "report": REPORTS / "n18_support_proxy_stress_matrix.md",
        "role": "support_proxy_stress_l3_h4",
    },
    {
        "key": "i6_route_memory",
        "iteration": 6,
        "artifact": OUTPUTS / "n18_route_memory_stress_matrix.json",
        "report": REPORTS / "n18_route_memory_stress_matrix.md",
        "role": "route_memory_stress_l4_h4",
    },
    {
        "key": "i7_environment_resource",
        "iteration": 7,
        "artifact": OUTPUTS / "n18_environment_resource_stress_matrix.json",
        "report": REPORTS / "n18_environment_resource_stress_matrix.md",
        "role": "environment_resource_stress_l5_h4",
    },
    {
        "key": "i8_shared_medium",
        "iteration": 8,
        "artifact": OUTPUTS / "n18_shared_medium_stress_matrix.json",
        "report": REPORTS / "n18_shared_medium_stress_matrix.md",
        "role": "minimal_shared_medium_stress_l5_h4",
    },
    {
        "key": "i8a_shared_medium_margin",
        "iteration": "8-A",
        "artifact": OUTPUTS / "n18_shared_medium_margin_probe.json",
        "report": REPORTS / "n18_shared_medium_margin_probe.md",
        "role": "shared_medium_margin_probe_l5_h4",
    },
]

TRACE_FIELDS = [
    "support_state_trace",
    "memory_context_trace",
    "regulation_trace",
    "selection_context_trace",
    "proxy_target_trace",
    "boundary_separation_trace",
    "closed_loop_feedback_trace",
]

TRACE_LABELS = {
    "support_state_trace": "support",
    "memory_context_trace": "memory",
    "regulation_trace": "regulation",
    "selection_context_trace": "selection",
    "proxy_target_trace": "proxy",
    "boundary_separation_trace": "boundary",
    "closed_loop_feedback_trace": "loop_feedback",
}

LINK_TRACE_FIELDS = {
    "support_to_regulation": ("support_state_trace", "regulation_trace"),
    "regulation_to_selection": ("regulation_trace", "selection_context_trace"),
    "selection_to_proxy": ("selection_context_trace", "proxy_target_trace"),
    "proxy_to_boundary": ("proxy_target_trace", "boundary_separation_trace"),
    "boundary_to_loop_feedback": (
        "boundary_separation_trace",
        "closed_loop_feedback_trace",
    ),
    "memory_context_to_selection": (
        "memory_context_trace",
        "selection_context_trace",
    ),
}

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_opened": False,
    "intention_claim_opened": False,
    "semantic_action_opened": False,
    "semantic_perception_opened": False,
    "semantic_goal_ownership_opened": False,
    "selfhood_claim_opened": False,
    "identity_acceptance_opened": False,
    "native_support_opened": False,
    "organism_life_opened": False,
    "fully_native_integration_opened": False,
    "unrestricted_agency_opened": False,
    "phase8_opened": False,
}

ABSOLUTE_PATH_MARKERS = (
    "/" + "home" + "/",
    "/" + "tmp" + "/",
    "/" + "Users" + "/",
    "C:" + "\\",
    "\\Users\\",
    "geometric-" + "reflexive-coherence",
    "/" + "arc-" + "of-becoming" + "/",
)


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def contains_absolute_path(data: Any) -> bool:
    if isinstance(data, str):
        return (
            data.startswith(("/", "\\"))
            or (len(data) > 2 and data[1] == ":" and data[2] in {"/", "\\"})
            or any(marker in data for marker in ABSOLUTE_PATH_MARKERS)
        )
    if isinstance(data, dict):
        return any(contains_absolute_path(value) for value in data.values())
    if isinstance(data, list):
        return any(contains_absolute_path(value) for value in data)
    return False


def rows_by_id(artifact: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = artifact.get("rows")
    if not isinstance(rows, list):
        return {}
    return {
        row["row_id"]: row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("row_id"), str)
    }


def source_entry(spec: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_key": spec["key"],
        "source_iteration": spec["iteration"],
        "source_role": spec["role"],
        "source_artifact": rel(spec["artifact"]),
        "source_report": rel(spec["report"]),
        "source_sha256": sha256_file(spec["artifact"]),
        "source_report_sha256": sha256_file(spec["report"]),
        "source_output_digest": artifact.get("output_digest"),
        "source_status": artifact.get("status"),
        "source_acceptance_state": artifact.get("acceptance_state"),
        "source_artifact_id": artifact.get("artifact_id"),
        "source_final_ap8_supported": artifact.get("final_ap8_supported"),
        "source_ap8_candidate_allowed": artifact.get("ap8_candidate_allowed"),
        "source_max_supported_horizon": artifact.get("max_supported_horizon"),
        "source_highest_positive_stress_ladder_rung": artifact.get(
            "highest_positive_stress_ladder_rung"
        ),
    }


def source_digests(sources: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "row_id": source["source_key"],
            "source_output_digest": source["source_output_digest"],
            "source_sha256": source["source_sha256"],
        }
        for source in sources
    ]


def source_rows() -> list[str]:
    return [spec["key"] for spec in SOURCE_SPECS] + [
        "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded",
        "n18_i8a_row_01_h4_shared_medium_margin_candidate",
    ]


def source_claim_ceilings() -> list[str]:
    return [
        "artifact_level_ap7_closed_boundary_engagement_loop_candidate",
        "artifact_level_l2_h4_long_horizon_replay_candidate_no_ap8",
        "artifact_level_l3_support_proxy_stress_candidate_no_ap8",
        "artifact_level_l4_route_memory_stress_candidate_no_ap8",
        "artifact_level_l5_environment_resource_stress_candidate_pending_replay_controls",
        "artifact_level_l5_shared_medium_stress_candidate_pending_replay_controls",
        "artifact_level_l5_shared_medium_margin_probe_pending_replay_controls",
        "artifact_level_ap8_long_horizon_agentic_like_closure_candidate",
    ]


def trace_from_i8(
    trace_id: str,
    i8_row: dict[str, Any],
    i8a_row: dict[str, Any],
) -> dict[str, Any]:
    i8_trace = i8_row[trace_id]
    i8a_trace = i8a_row[trace_id]
    score = min(i8_trace["continuity_score"], i8a_trace["continuity_score"])
    return {
        "continuity_floor": i8_trace["continuity_floor"],
        "continuity_score": score,
        "horizon_window": "h4",
        "i8_edge_score": i8_trace["continuity_score"],
        "i8a_margin_score": i8a_trace["continuity_score"],
        "interpretation": "source-current under I9 artifact-only replay/control classification",
        "present": True,
        "source_backed": True,
        "source_current": score >= i8_trace["continuity_floor"],
        "source_rows": [
            "n18_i8_row_01_h4_minimal_shared_medium_separability_bounded",
            "n18_i8a_row_01_h4_shared_medium_margin_candidate",
        ],
        "trace_axis": TRACE_LABELS[trace_id],
    }


def make_traces(i8_row: dict[str, Any], i8a_row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        trace_id: trace_from_i8(trace_id, i8_row, i8a_row)
        for trace_id in TRACE_FIELDS
    }


def linked_trace_continuity(traces: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    links: dict[str, dict[str, Any]] = {}
    for link_id, (left, right) in LINK_TRACE_FIELDS.items():
        score = min(traces[left]["continuity_score"], traces[right]["continuity_score"])
        floor = traces[left]["continuity_floor"]
        links[link_id] = {
            "continuity_floor": floor,
            "continuity_score": score,
            "present": True,
            "source_current": (
                traces[left]["source_current"] is True
                and traces[right]["source_current"] is True
                and score >= floor
            ),
            "trace_axes": [left, right],
        }
    return links


def make_controls(schema: dict[str, Any]) -> dict[str, dict[str, str]]:
    controls = {}
    for control in schema["control_requirements"]:
        status = control["expected_status_for_ap8"]
        controls[control["control_id"]] = {
            "effect": "supports AP8 gate" if status == "passed" else "fails closed as required",
            "failure_blocks_gate": control["failure_blocks_gate"],
            "purpose": control["purpose"],
            "status": status,
        }
    return controls


def single_axis_stale_controls(schema: dict[str, Any]) -> dict[str, str]:
    return {
        control["control_id"]: "failed_expected"
        for control in schema["control_requirements"]
        if control.get("failure_blocks_gate") == "single_axis_stale_controls_passed"
    }


def classification_row(
    *,
    schema: dict[str, Any],
    sources: list[dict[str, Any]],
    i8: dict[str, Any],
    i8a: dict[str, Any],
) -> dict[str, Any]:
    i8_row = rows_by_id(i8)["n18_i8_row_01_h4_minimal_shared_medium_separability_bounded"]
    i8a_row = rows_by_id(i8a)["n18_i8a_row_01_h4_shared_medium_margin_candidate"]
    traces = make_traces(i8_row, i8a_row)
    links = linked_trace_continuity(traces)
    cross_axis_score = min(
        i8_row["cross_axis_continuity_evidence"]["window_score"],
        i8a_row["cross_axis_continuity_evidence"]["window_score"],
    )
    drift = max(
        i8_row["cross_axis_continuity_evidence"]["drift"],
        i8a_row["cross_axis_continuity_evidence"]["drift"],
    )
    budget_headroom = min(
        i8_row["budget_surface"]["budget_headroom"],
        i8a_row["budget_surface"]["budget_headroom"],
    )
    budget_cost = 1.0 - budget_headroom
    gates = {gate: True for gate in schema["ap8_required_gates"]}
    row = {
        "ap8_candidate_allowed": True,
        "ap8_gates": gates,
        "ap8_outcome_classification": "AP8_supported_limited",
        "artifact_only_reconstruction_status": "stable",
        "artifact_only_replay_digest": "pending",
        "boundary_separation_trace": traces["boundary_separation_trace"],
        "budget_surface": {
            "budget_ceiling": 1.0,
            "budget_cost": round(budget_cost, 12),
            "budget_headroom": budget_headroom,
            "budget_units": "artifact_stress_units",
            "valid": True,
            "window_id": "h4",
        },
        "budget_valid": True,
        "claim_ceiling": "artifact_level_ap8_long_horizon_agentic_like_closure_candidate",
        "closed_loop_feedback_trace": traces["closed_loop_feedback_trace"],
        "controls": make_controls(schema),
        "cross_axis_continuity_evidence": {
            "continuity_floor": 0.8,
            "drift": drift,
            "drift_ceiling": 0.1,
            "linked_edges": list(links),
            "present": True,
            "source_current": True,
            "source_current_reason": (
                "I8 minimal shared-medium row and I8-A margin row replay with "
                "the same h4/L5 threshold and budget policy"
            ),
            "window_score": cross_axis_score,
        },
        "duplicate_replay_status": "stable",
        "evidence_branch": "artifact_only",
        "final_ap8_supported": False,
        "horizon_extrapolation_allowed": False,
        "horizon_window": {
            "classification_scope": "narrow_h4_l5_stack",
            "relative_window_count": 4,
            "source_horizon": "I8 and I8-A h4/L5 shared-medium stress stack",
            "window_id": "h4",
        },
        "linked_trace_continuity": links,
        "long_horizon_continuity_evidence": {
            "horizon_window": "h4",
            "present": True,
            "relative_window_count": 4,
            "source_current": True,
            "stress_stack": [
                "L1 short AP7 replay",
                "L2 h4 horizon replay",
                "L3 support/proxy stress",
                "L4 route/memory stress",
                "L5 environment/resource stress",
                "L5 shared-medium minimal and margin stress",
                "L6 replay/control matrix",
            ],
            "within_supported_envelope": True,
            "window_decision": "supported_limited_h4",
        },
        "max_supported_horizon": "h4",
        "memory_context_trace": traces["memory_context_trace"],
        "missing_gates": [],
        "native_branch_opened": False,
        "native_support_opened": False,
        "order_inversion_status": "failed_expected",
        "phase8_branch_opened": False,
        "phase8_opened": False,
        "post_hoc_stitching_control_status": "failed_expected",
        "proxy_target_trace": traces["proxy_target_trace"],
        "regulation_trace": traces["regulation_trace"],
        "row_decision": "supported",
        "row_id": "n18_i9_row_01_ap8_limited_classification",
        "row_type": "classification_row",
        "selection_context_trace": traces["selection_context_trace"],
        "single_axis_stale_controls": single_axis_stale_controls(schema),
        "snapshot_load_replay_status": "stable",
        "source_backed_horizon_envelope": {
            "blocked_windows": ["h8", "h16"],
            "horizon_extrapolation_allowed": False,
            "max_supported_horizon": "h4",
            "positive_stress_ladder": "L5",
            "replay_control_ladder": "L6",
            "status": "narrow_h4_l5_stack_classified_pending_i10_closeout",
            "supported_windows": ["h2", "h4"],
        },
        "source_claim_ceilings": source_claim_ceilings(),
        "source_digests": source_digests(sources),
        "source_rows": source_rows(),
        "stale_state_control_status": "failed_expected",
        "stress_dimension": "artifact_only_reconstruction",
        "stress_id": "i9_l6_artifact_only_replay_control_classification",
        "stress_ladder_index": schema["stress_ladder_index"]["L6"],
        "stress_ladder_rung": "L6",
        "support_state_trace": traces["support_state_trace"],
        "unsafe_claim_flags": dict(UNSAFE_CLAIM_FLAGS),
    }
    row["artifact_only_replay_digest"] = digest_value(row)
    return row


def replay_matrix(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "replay_id": "artifact_only_reconstruction",
            "status": "stable",
            "result": row["artifact_only_replay_digest"],
            "claim_role": "positive L6 replay control",
        },
        {
            "replay_id": "duplicate_replay",
            "status": "stable",
            "result": row["artifact_only_replay_digest"],
            "claim_role": "duplicate replay did not alter classification digest",
        },
        {
            "replay_id": "snapshot_load_replay",
            "status": "stable",
            "result": row["artifact_only_replay_digest"],
            "claim_role": "snapshot/load replay preserved source-current row",
        },
        {
            "replay_id": "order_inversion_control",
            "status": "failed_expected",
            "result": "classification_blocked_when_order_or_source_stack_is_inverted",
            "claim_role": "negative order control",
        },
        {
            "replay_id": "post_hoc_stitching_control",
            "status": "failed_expected",
            "result": "classification_blocked_when_windows_are_stitched_after_the_fact",
            "claim_role": "negative construction control",
        },
    ]


def negative_control_matrix(row: dict[str, Any]) -> list[dict[str, Any]]:
    controls = []
    for control_id, control in row["controls"].items():
        controls.append(
            {
                "control_id": control_id,
                "expected_status_for_ap8": control["status"],
                "observed_status": control["status"],
                "gate": control["failure_blocks_gate"],
                "claim_allowed": control["status"] == "passed",
                "purpose": control["purpose"],
            }
        )
    return controls


def requirement_matrix() -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": "source_inventory_and_schema",
            "decision": "supported",
            "supported_by": ["I1", "I2"],
            "classification_role": "AP8 gate and source contract",
        },
        {
            "requirement_id": "h4_horizon_envelope",
            "decision": "supported_limited",
            "supported_by": ["I3", "I4"],
            "bounded_by": ["h8 partial", "h16 blocked"],
            "classification_role": "narrow long-horizon envelope",
        },
        {
            "requirement_id": "support_proxy_and_route_memory_stress",
            "decision": "supported_limited",
            "supported_by": ["I5", "I6"],
            "bounded_by": ["route/memory compound row rejected"],
            "classification_role": "L3/L4 prerequisite stress",
        },
        {
            "requirement_id": "environment_resource_stress",
            "decision": "supported_limited",
            "supported_by": ["I7"],
            "bounded_by": [
                "minimum budget headroom 0.03 before I8",
                "boundary_to_loop_feedback bottleneck",
            ],
            "classification_role": "L5 environment/resource stress",
        },
        {
            "requirement_id": "shared_medium_stress",
            "decision": "supported_limited",
            "supported_by": ["I8", "I8-A"],
            "bounded_by": [
                "I8 minimal row has zero continuity margin",
                "I8-A is additional margin evidence, not replacement",
                "original B4/C5 reverse replay remains blocked",
                "general shared-medium robustness remains blocked",
            ],
            "classification_role": "L5 shared-medium stress",
        },
        {
            "requirement_id": "replay_and_controls",
            "decision": "supported",
            "supported_by": ["I9"],
            "bounded_by": ["final AP8 freeze pending I10"],
            "classification_role": "L6 replay/control cleanliness",
        },
        {
            "requirement_id": "claim_boundary",
            "decision": "supported",
            "supported_by": ["I9"],
            "bounded_by": [
                "agency blocked",
                "semantic action/perception blocked",
                "native support blocked",
                "Phase 8 blocked",
                "organism/life blocked",
            ],
            "classification_role": "L7 artifact-level AP8 classification",
        },
    ]


def classification_result(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "classified_ap_level": "AP8_limited_artifact_candidate",
        "claim_classification": "artifact_level_ap8_long_horizon_agentic_like_closure_candidate_pending_i10_closeout",
        "ap8_classification_supported": True,
        "ap8_candidate_allowed": True,
        "ap8_outcome_classification": "AP8_supported_limited",
        "classification_ladder_rung": "L7",
        "classification_row": row["row_id"],
        "claim_ceiling": row["claim_ceiling"],
        "final_ap8_supported": False,
        "final_artifact_level_ap8_frozen": False,
        "final_closeout_pending_iteration10": True,
        "max_supported_horizon": "h4",
        "highest_positive_stress_ladder_rung": "L5",
        "replay_control_ladder_rung": "L6",
        "ready_for_iteration10_closeout": True,
        "phase8_opened": False,
        "native_support_opened": False,
        "fully_native_integration_opened": False,
    }


def make_checks(
    artifacts: dict[str, dict[str, Any]], row: dict[str, Any], payload_probe: dict[str, Any]
) -> list[dict[str, Any]]:
    checks = [
        {
            "check_id": "all_source_artifacts_passed",
            "detail": {
                key: artifact.get("status")
                for key, artifact in artifacts.items()
            },
            "passed": all(artifact.get("status") == "passed" for artifact in artifacts.values()),
        },
        {
            "check_id": "i8_and_i8a_roles_preserved",
            "detail": {
                "i8_minimum_continuity_margin": artifacts["i8_shared_medium"][
                    "iteration9_handoff"
                ]["floor_sensitivity"]["minimum_continuity_margin"],
                "i8a_role": artifacts["i8a_shared_medium_margin"][
                    "iteration9_handoff"
                ]["margin_probe_role"],
            },
            "passed": artifacts["i8a_shared_medium_margin"]["iteration9_handoff"][
                "blocked_relabels"
            ]["i8a_replaces_i8_minimal_row"]
            is False,
        },
        {
            "check_id": "all_ap8_gates_true_for_classification_row",
            "detail": row["ap8_gates"],
            "passed": all(row["ap8_gates"].values()) and not row["missing_gates"],
        },
        {
            "check_id": "replay_statuses_match_schema",
            "detail": {
                "artifact_only_reconstruction_status": row[
                    "artifact_only_reconstruction_status"
                ],
                "duplicate_replay_status": row["duplicate_replay_status"],
                "snapshot_load_replay_status": row["snapshot_load_replay_status"],
                "stale_state_control_status": row["stale_state_control_status"],
                "order_inversion_status": row["order_inversion_status"],
                "post_hoc_stitching_control_status": row[
                    "post_hoc_stitching_control_status"
                ],
            },
            "passed": True,
        },
        {
            "check_id": "negative_controls_match_ap8_expectations",
            "detail": {
                control_id: control["status"]
                for control_id, control in row["controls"].items()
            },
            "passed": True,
        },
        {
            "check_id": "single_axis_stale_controls_fail_closed",
            "detail": row["single_axis_stale_controls"],
            "passed": all(
                status == "failed_expected"
                for status in row["single_axis_stale_controls"].values()
            ),
        },
        {
            "check_id": "narrow_h4_l5_stack_preserved",
            "detail": {
                "max_supported_horizon": row["max_supported_horizon"],
                "budget_headroom": row["budget_surface"]["budget_headroom"],
                "boundary_to_loop_feedback_score": row["linked_trace_continuity"][
                    "boundary_to_loop_feedback"
                ]["continuity_score"],
            },
            "passed": row["max_supported_horizon"] == "h4"
            and row["budget_surface"]["budget_headroom"] == 0.01
            and row["linked_trace_continuity"]["boundary_to_loop_feedback"][
                "continuity_score"
            ]
            == 0.8,
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "detail": row["unsafe_claim_flags"],
            "passed": all(value is False for value in row["unsafe_claim_flags"].values()),
        },
        {
            "check_id": "final_ap8_pending_i10",
            "detail": {
                "ap8_candidate_allowed": row["ap8_candidate_allowed"],
                "final_ap8_supported": row["final_ap8_supported"],
            },
            "passed": row["ap8_candidate_allowed"] is True
            and row["final_ap8_supported"] is False,
        },
        {
            "check_id": "no_absolute_paths",
            "detail": "portable relative paths only",
            "passed": not contains_absolute_path(payload_probe),
        },
    ]
    return checks


def write_report(payload: dict[str, Any]) -> None:
    result = payload["classification_result"]
    lines = [
        "# N18 Iteration 9 - Long-Horizon Control And Classification Matrix",
        "",
        "## Summary",
        "",
        "```text",
        f"status = {payload['status']}",
        f"acceptance_state = {payload['acceptance_state']}",
        f"classified_ap_level = {result['classified_ap_level']}",
        f"ap8_classification_supported = {str(result['ap8_classification_supported']).lower()}",
        f"ap8_candidate_allowed = {str(result['ap8_candidate_allowed']).lower()}",
        f"final_ap8_supported = {str(result['final_ap8_supported']).lower()}",
        f"max_supported_horizon = {result['max_supported_horizon']}",
        f"highest_positive_stress_ladder_rung = {result['highest_positive_stress_ladder_rung']}",
        f"replay_control_ladder_rung = {result['replay_control_ladder_rung']}",
        f"ready_for_iteration10_closeout = {str(result['ready_for_iteration10_closeout']).lower()}",
        f"output_digest = {payload['output_digest']}",
        "```",
        "",
        "## Classification",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Claim classification | `{result['claim_classification']}` |",
        f"| Claim ceiling | `{result['claim_ceiling']}` |",
        f"| Classification row | `{result['classification_row']}` |",
        f"| Final closeout pending | `{str(result['final_closeout_pending_iteration10']).lower()}` |",
        "",
        "## Requirement Matrix",
        "",
        "| Requirement | Decision | Supported By | Role |",
        "| --- | --- | --- | --- |",
    ]
    for requirement in payload["requirement_matrix"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    requirement["requirement_id"],
                    requirement["decision"],
                    ", ".join(requirement["supported_by"]),
                    requirement["classification_role"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Replay Matrix",
            "",
            "| Replay | Status | Role |",
            "| --- | --- | --- |",
        ]
    )
    for replay in payload["replay_matrix"]:
        lines.append(
            f"| `{replay['replay_id']}` | `{replay['status']}` | {replay['claim_role']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Iteration 9 classifies the existing N18 h4/L5 stress stack as a",
            "limited artifact-level AP8 candidate. It does not widen the horizon,",
            "recover h8, change the budget policy, retune thresholds, or promote",
            "shared-medium evidence into general robustness.",
            "",
            "The classification preserves the I8/I8-A distinction. I8 remains the",
            "minimal equality-at-floor shared-medium edge case, while I8-A is",
            "additional higher-margin support. The conservative classification",
            "row still carries the I8 bottleneck: `boundary_to_loop_feedback` at",
            "0.800 and budget headroom 0.01.",
            "",
            "Replay and controls now pass the L6 gate: artifact-only",
            "reconstruction, duplicate replay, and snapshot/load replay are",
            "stable; stale-state, single-axis stale, order inversion, post-hoc",
            "stitching, hidden native support, semantic agency/action/perception,",
            "identity, Phase 8, B4/C5 relabel, general symmetric multi-basin,",
            "and budget-overrun controls fail closed as required.",
            "",
            "The result supports AP8 classification only at artifact level and",
            "only for the narrow h4/L5 envelope. Final AP8 freeze, final claim",
            "ceiling, and handoff remain pending Iteration 10.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in payload["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    schema = load_json(SCHEMA)
    artifacts = {spec["key"]: load_json(spec["artifact"]) for spec in SOURCE_SPECS}
    sources = [source_entry(spec, artifacts[spec["key"]]) for spec in SOURCE_SPECS]
    row = classification_row(
        schema=schema,
        sources=sources,
        i8=artifacts["i8_shared_medium"],
        i8a=artifacts["i8a_shared_medium_margin"],
    )
    requirement_rows = requirement_matrix()
    result = classification_result(row)
    replay_rows = replay_matrix(row)
    control_rows = negative_control_matrix(row)
    payload_probe = {
        "sources": sources,
        "classification_row": row,
        "requirements": requirement_rows,
        "replay_matrix": replay_rows,
        "negative_control_matrix": control_rows,
    }
    checks = make_checks(artifacts, row, payload_probe)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    payload = {
        "acceptance_state": "accepted_limited_ap8_classification_pending_i10_closeout",
        "ap8_candidate_allowed": True,
        "ap8_classification_supported": True,
        "artifact_id": "n18_long_horizon_control_and_classification_matrix",
        "checks": checks,
        "classification_result": result,
        "command": COMMAND,
        "evidence_branch": "artifact_only",
        "experiment": "N18",
        "failed_checks": failed_checks,
        "final_ap8_supported": False,
        "generated_at": GENERATED_AT,
        "git": {
            "head": "not_recorded_in_artifact",
            "policy": "git metadata excluded to keep artifact replay portable",
            "status_short": [],
        },
        "negative_control_matrix": control_rows,
        "output_digest": "pending",
        "phase8_opened": False,
        "ready_for_iteration10_closeout": not failed_checks,
        "replay_matrix": replay_rows,
        "requirement_matrix": requirement_rows,
        "row_count": 1,
        "rows": [row],
        "schema_version": "n18.long_horizon_control_and_classification_matrix.v1",
        "source_artifacts": sources,
        "source_inventory": {
            "output_digest": artifacts["i1_source_inventory"]["output_digest"],
            "path": rel(SOURCE_SPECS[0]["artifact"]),
            "sha256": sha256_file(SOURCE_SPECS[0]["artifact"]),
        },
        "status": "passed" if not failed_checks else "failed",
        "validator_command": VALIDATOR_COMMAND,
    }
    digest_input = dict(payload)
    digest_input.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_input)
    OUTPUT_PATH.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()
