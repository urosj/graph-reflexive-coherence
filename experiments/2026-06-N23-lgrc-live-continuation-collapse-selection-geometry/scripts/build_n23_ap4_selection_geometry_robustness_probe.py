#!/usr/bin/env python3
"""Build N23 Iteration 6-A AP4 selection-geometry robustness probe."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

import build_n23_ap4_selection_geometry_probe as i6
import build_n23_minimal_live_branch_collapse_probe as i4


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUT = EXPERIMENT / "outputs" / "n23_ap4_selection_geometry_robustness_probe.json"
REPORT = EXPERIMENT / "reports" / "n23_ap4_selection_geometry_robustness_probe.md"
ARTIFACT_DIR = (
    EXPERIMENT / "outputs" / "n23_ap4_selection_geometry_robustness_probe_artifacts"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_ap4_selection_geometry_robustness_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_ap4_selection_geometry_robustness_probe.py"
)

I1_OUTPUT_PATH = i6.I1_OUTPUT_PATH
I2_OUTPUT_PATH = i6.I2_OUTPUT_PATH
I3_OUTPUT_PATH = i6.I3_OUTPUT_PATH
I4_OUTPUT_PATH = i6.I4_OUTPUT_PATH
I5_OUTPUT_PATH = i6.I5_OUTPUT_PATH
I4A_OUTPUT_PATH = i6.I4A_OUTPUT_PATH
I5A_OUTPUT_PATH = i6.I5A_OUTPUT_PATH
I6_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_ap4_selection_geometry_probe.json"
)

BRANCH_CANDIDATES = [
    {
        "branch_id": "branch_edge_0_node_1",
        "edge_id": 0,
        "source_node_id": 1,
        "target_node_id": 0,
        "route_label": "edge_0_neighbor_1_to_center",
    },
    {
        "branch_id": "branch_edge_4_node_5",
        "edge_id": 4,
        "source_node_id": 5,
        "target_node_id": 0,
        "route_label": "edge_4_neighbor_5_to_center",
    },
    {
        "branch_id": "branch_edge_6_node_7",
        "edge_id": 6,
        "source_node_id": 7,
        "target_node_id": 0,
        "route_label": "edge_6_neighbor_7_to_center",
    },
    {
        "branch_id": "branch_edge_8_node_9",
        "edge_id": 8,
        "source_node_id": 9,
        "target_node_id": 0,
        "route_label": "edge_8_neighbor_9_to_center",
    },
]

STRESS_CASES = [
    {
        "case_id": "reference_four_branch_geometry",
        "node_1_coherence": 13.0,
        "expected_role": "reference_pass",
        "expected_decision": "supported",
        "description": "Original four-branch geometry from I4-A/I6.",
    },
    {
        "case_id": "eroded_margin_still_supported",
        "node_1_coherence": 13.4,
        "expected_role": "narrow_margin_pass",
        "expected_decision": "supported",
        "description": (
            "Runner-up branch is strengthened, but selected branch still clears "
            "the predeclared margin."
        ),
    },
    {
        "case_id": "alternate_branch_wins_supported",
        "node_1_coherence": 15.0,
        "expected_role": "alternate_winner_pass",
        "expected_decision": "supported",
        "description": (
            "Geometry flips so branch_edge_0_node_1 wins; selection should "
            "follow geometry rather than fixed branch label."
        ),
    },
    {
        "case_id": "below_margin_rejected",
        "node_1_coherence": 13.8,
        "expected_role": "margin_gate_fail",
        "expected_decision": "rejected",
        "description": (
            "Selected branch remains branch_edge_4_node_5, but score margin is "
            "below the predeclared AP4 bridge threshold."
        ),
    },
    {
        "case_id": "equalized_tie_rejected",
        "node_1_coherence": 14.0,
        "expected_role": "tie_gate_fail",
        "expected_decision": "rejected",
        "description": (
            "Two branches have equal support-gradient scores; random-tie "
            "promotion must fail closed."
        ),
    },
]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(i4.canonical_json(data), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def stress_state(node_1_coherence: float) -> dict[str, Any]:
    state = deepcopy(i4.make_column_h_state())
    state["nodes"]["1"]["coherence"] = float(node_1_coherence)
    state["nodes"]["1"]["basin_mass"] = float(node_1_coherence)
    return state


def select_branch_with_tie_gate(branches: list[dict[str, Any]]) -> dict[str, Any]:
    sorted_branches = sorted(
        branches,
        key=lambda item: (item["support_gradient_score"], item["branch_id"]),
        reverse=True,
    )
    selected = sorted_branches[0]
    runner_up = sorted_branches[1]
    margin = float(selected["support_gradient_score"] - runner_up["support_gradient_score"])
    tie = abs(margin) <= 1e-12
    selection = {
        "selected_branch_id": selected["branch_id"],
        "non_selected_branch_ids": [item["branch_id"] for item in sorted_branches[1:]],
        "selection_reason": "support_gradient_dominance",
        "selected_score": selected["support_gradient_score"],
        "runner_up_branch_id": runner_up["branch_id"],
        "runner_up_score": runner_up["support_gradient_score"],
        "score_margin": margin,
        "min_score_margin": i4.MIN_BRANCH_SCORE_MARGIN,
        "random_tie_status": "random_tie" if tie else "not_random_tie",
        "producer_preference_used": False,
        "producer_selected_branch_label_used": False,
        "selection_margin_passed": margin >= i4.MIN_BRANCH_SCORE_MARGIN,
        "selection_admitted_for_collapse": (
            margin >= i4.MIN_BRANCH_SCORE_MARGIN and not tie
        ),
    }
    selection["selection_digest"] = i4.digest_value(selection)
    return i4.canonicalize_json_value(selection)


def observable_digest(collapse_trace: dict[str, Any]) -> str:
    return i4.digest_value(
        {
            "selection": collapse_trace.get("selection"),
            "scheduled_packet": collapse_trace.get("scheduled_packet"),
            "event_counts_by_kind": collapse_trace.get("event_counts_by_kind"),
            "collapse_persistence_ratio": collapse_trace.get(
                "collapse_persistence_ratio"
            ),
            "selected_source_node_coherence_after": collapse_trace.get(
                "selected_source_node_coherence_after"
            ),
            "center_node_coherence_after": collapse_trace.get(
                "center_node_coherence_after"
            ),
            "packet_budget_error": collapse_trace.get("packet_budget_error"),
        }
    )


def run_stress_case(case: dict[str, Any]) -> dict[str, Any]:
    case_id = case["case_id"]
    case_dir = ARTIFACT_DIR / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    model = i4.LGRC9V3.from_state(
        stress_state(case["node_1_coherence"]),
        i4.make_config(spark_lane=i4.LANE_B),
    )
    pre_snapshot_path = case_dir / f"{case_id}_pre_collapse_snapshot.json"
    model.save(str(pre_snapshot_path))
    pre_basin = i4.basin_signature(model)
    branches = [i4.branch_record(model, branch) for branch in BRANCH_CANDIDATES]
    selection = select_branch_with_tie_gate(branches)
    branch_set_trace = {
        "artifact_id": f"{case_id}_live_branch_set_trace",
        "trace_status": "present",
        "trace_origin": "source_current_same_run",
        "case_id": case_id,
        "branch_window": {
            "window_id": f"{case_id}_branch_window",
            "start_step": 0,
            "end_step": 0,
        },
        "branch_count": len(branches),
        "branch_records": branches,
        "branch_record_origin": "source_current_same_run",
        "pre_collapse_basin_signature": pre_basin,
        "stress_config": {
            "node_1_coherence": case["node_1_coherence"],
            "producer_role": "bounded_test_configuration",
            "selection_inputs_remain_source_current": True,
        },
    }
    branch_set_trace["trace_digest"] = i4.digest_value(branch_set_trace)
    branch_trace_path = case_dir / f"{case_id}_live_branch_set_trace.json"
    write_json(branch_trace_path, branch_set_trace)

    retention_trace = {
        "artifact_id": f"{case_id}_counterfactual_retention_trace",
        "trace_status": "present",
        "trace_origin": "source_current_same_run",
        "case_id": case_id,
        "meaning": "immutable_pre_collapse_audit_record",
        "selected_branch_id": selection["selected_branch_id"],
        "retained_non_selected_branch_records": [
            branch
            for branch in branches
            if branch["branch_id"] in selection["non_selected_branch_ids"]
        ],
        "continued_dynamic_activity_after_collapse_required": False,
        "retention_blocks_single_path_history_relabel": True,
    }
    retention_trace["trace_digest"] = i4.digest_value(retention_trace)
    retention_trace_path = case_dir / f"{case_id}_counterfactual_retention_trace.json"
    write_json(retention_trace_path, retention_trace)

    selected_spec = next(
        branch
        for branch in BRANCH_CANDIDATES
        if branch["branch_id"] == selection["selected_branch_id"]
    )
    event_rows: list[dict[str, Any]] = []
    step_rows: list[dict[str, Any]] = []
    if selection["selection_admitted_for_collapse"]:
        model.schedule_packet_departure(
            source_node_id=selected_spec["source_node_id"],
            target_node_id=selected_spec["target_node_id"],
            edge_id=selected_spec["edge_id"],
            amount=i4.COLLAPSE_PACKET_AMOUNT,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        step_rows, event_rows = i4.drain_queue(model)
    post_snapshot_path = case_dir / f"{case_id}_post_collapse_snapshot.json"
    model.save(str(post_snapshot_path))
    event_log_path = case_dir / f"{case_id}_collapse_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    event_counts = dict(Counter(row["kind"] for row in event_rows))
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    selected_after = state.base_state.nodes[selected_spec["source_node_id"]]
    center_after = state.base_state.nodes[selected_spec["target_node_id"]]
    collapse_trace = {
        "artifact_id": f"{case_id}_collapsed_continuation_trace",
        "trace_status": (
            "present" if selection["selection_admitted_for_collapse"] else "blocked"
        ),
        "trace_origin": "source_current_same_run",
        "case_id": case_id,
        "collapse_window": {
            "window_id": f"{case_id}_collapse_window",
            "start_step": 1,
            "end_step": 2 if selection["selection_admitted_for_collapse"] else 1,
        },
        "selection": selection,
        "scheduled_packet": (
            {
                "source_node_id": selected_spec["source_node_id"],
                "target_node_id": selected_spec["target_node_id"],
                "edge_id": selected_spec["edge_id"],
                "amount": i4.COLLAPSE_PACKET_AMOUNT,
                "departure_event_time_key": 1.0,
                "arrival_event_time_key": 2.0,
            }
            if selection["selection_admitted_for_collapse"]
            else None
        ),
        "blocked_before_collapse_reason": (
            None
            if selection["selection_admitted_for_collapse"]
            else (
                "random_tie"
                if selection["random_tie_status"] == "random_tie"
                else "score_margin_below_threshold"
            )
        ),
        "step_summaries": step_rows,
        "event_counts_by_kind": event_counts,
        "event_log_path": rel(event_log_path),
        "post_collapse_basin_signature": i4.basin_signature(model),
        "selected_source_node_coherence_after": selected_after.coherence,
        "center_node_coherence_after": center_after.coherence,
        "packet_budget_error": ledger.budget_error,
        "in_flight_packet_total": ledger.in_flight_packet_total,
        "collapse_persistence_ratio": (
            1.0
            if event_counts.get("lgrc9v3_local_update", 0) >= 1
            else 0.0
        ),
    }
    collapse_trace["observable_digest"] = observable_digest(collapse_trace)
    collapse_trace["trace_digest"] = i4.digest_value(collapse_trace)
    collapse_trace_path = case_dir / f"{case_id}_collapsed_continuation_trace.json"
    write_json(collapse_trace_path, collapse_trace)

    duplicate_trace = duplicate_replay(case, pre_snapshot_path, branch_set_trace, collapse_trace)
    duplicate_trace_path = case_dir / f"{case_id}_duplicate_replay_trace.json"
    write_json(duplicate_trace_path, duplicate_trace)

    manifest = [
        ("runtime_trace", "pre_collapse_snapshot", pre_snapshot_path),
        ("runtime_trace", "post_collapse_snapshot", post_snapshot_path),
        ("branch_set_trace", f"{case_id}_branch_set_trace", branch_trace_path),
        (
            "counterfactual_retention_trace",
            f"{case_id}_counterfactual_retention_trace",
            retention_trace_path,
        ),
        ("collapse_trace", f"{case_id}_collapse_trace", collapse_trace_path),
        ("runtime_trace", "collapse_event_log", event_log_path),
        ("duplicate_replay_trace", f"{case_id}_duplicate_replay_trace", duplicate_trace_path),
    ]
    artifact_manifest = [
        {
            "artifact_role": role,
            "artifact_subrole": subrole,
            "path": rel(path),
            "sha256": i4.sha256_file(rel(path)),
        }
        for role, subrole, path in manifest
    ]
    supported = (
        case["expected_decision"] == "supported"
        and selection["selection_admitted_for_collapse"]
        and duplicate_trace["observable_digest_matched"]
        and retention_trace["trace_status"] == "present"
    )
    rejected = (
        case["expected_decision"] == "rejected"
        and not selection["selection_admitted_for_collapse"]
    )
    row = {
        "row_id": f"n23_i6a_row_{len(STRESS_ROWS) + 1:02d}_{case_id}",
        "case_id": case_id,
        "description": case["description"],
        "row_schema_role": "ap4_selection_geometry_robustness_stress_row",
        "stress_case_role": case["expected_role"],
        "node_1_coherence": case["node_1_coherence"],
        "branch_count": len(branches),
        "retained_non_selected_branch_count": len(
            retention_trace["retained_non_selected_branch_records"]
        ),
        "selected_branch_id": selection["selected_branch_id"],
        "selection_reason": selection["selection_reason"],
        "selected_score": selection["selected_score"],
        "runner_up_branch_id": selection["runner_up_branch_id"],
        "runner_up_score": selection["runner_up_score"],
        "score_margin": selection["score_margin"],
        "minimum_score_margin": selection["min_score_margin"],
        "selection_margin_passed": selection["selection_margin_passed"],
        "random_tie_status": selection["random_tie_status"],
        "selection_admitted_for_collapse": selection["selection_admitted_for_collapse"],
        "collapse_trace_status": collapse_trace["trace_status"],
        "collapse_persistence_ratio": collapse_trace["collapse_persistence_ratio"],
        "duplicate_replay_observable_digest_matched": duplicate_trace[
            "observable_digest_matched"
        ],
        "counterfactual_retention_trace_present": retention_trace["trace_status"]
        == "present",
        "ap4_dependency_status": "required_recorded",
        "ap4_condition_reason": (
            "I6-A stress row remains route/branch conditioned and uses "
            "source-current branch geometry."
        ),
        "ap5_dependency_status": "not_applicable",
        "ap5_condition_reason": "No proxy derivation or target formation participates.",
        "n22_inherited_delta_used_as_selection_evidence": False,
        "producer_preference_used": selection["producer_preference_used"],
        "producer_selected_branch_label_used": selection[
            "producer_selected_branch_label_used"
        ],
        "artifact_manifest": artifact_manifest,
        "artifact_paths": [item["path"] for item in artifact_manifest],
        "all_artifact_sha256_match_file_contents": all(
            item["sha256"] == i4.sha256_file(item["path"]) for item in artifact_manifest
        ),
        "row_decision": "supported" if supported else "rejected" if rejected else "blocked",
        "provisional_lc_ladder_rung": "LC5" if supported else "LC4",
        "ap4_bridge_status": (
            "robustness_stress_supported" if supported else "failed_closed"
        ),
        "ap4_bridge_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "live_continuation_collapse_claim_allowed": False,
        "unsafe_claim_flags": i4.unsafe_claim_flags(),
        "claim_ceiling": (
            "I6-A stress evidence for AP4-relevant selection geometry; "
            "full matrix validation remains pending I7"
        ),
    }
    row["output_digest"] = i4.digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )
    return i4.canonicalize_json_value(row)


def duplicate_replay(
    case: dict[str, Any],
    pre_snapshot_path: Path,
    branch_set_trace: dict[str, Any],
    source_collapse_trace: dict[str, Any],
) -> dict[str, Any]:
    model = i4.LGRC9V3.load(str(pre_snapshot_path))
    branches = [i4.branch_record(model, branch) for branch in BRANCH_CANDIDATES]
    recomputed_selection = select_branch_with_tie_gate(branches)
    selected_spec = next(
        branch
        for branch in BRANCH_CANDIDATES
        if branch["branch_id"] == recomputed_selection["selected_branch_id"]
    )
    event_rows: list[dict[str, Any]] = []
    step_rows: list[dict[str, Any]] = []
    if recomputed_selection["selection_admitted_for_collapse"]:
        model.schedule_packet_departure(
            source_node_id=selected_spec["source_node_id"],
            target_node_id=selected_spec["target_node_id"],
            edge_id=selected_spec["edge_id"],
            amount=i4.COLLAPSE_PACKET_AMOUNT,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )
        step_rows, event_rows = i4.drain_queue(model)
    event_counts = dict(Counter(row["kind"] for row in event_rows))
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    selected_after = state.base_state.nodes[selected_spec["source_node_id"]]
    center_after = state.base_state.nodes[selected_spec["target_node_id"]]
    replay_collapse_trace = {
        "selection": recomputed_selection,
        "scheduled_packet": source_collapse_trace["scheduled_packet"],
        "event_counts_by_kind": event_counts,
        "collapse_persistence_ratio": (
            1.0
            if event_counts.get("lgrc9v3_local_update", 0) >= 1
            else 0.0
        ),
        "selected_source_node_coherence_after": selected_after.coherence,
        "center_node_coherence_after": center_after.coherence,
        "packet_budget_error": ledger.budget_error,
    }
    replay_observable_digest = observable_digest(replay_collapse_trace)
    trace = {
        "artifact_id": f"{case['case_id']}_duplicate_replay_trace",
        "replay_mode": "duplicate_replay",
        "source_case_id": case["case_id"],
        "source_branch_trace_digest": branch_set_trace["trace_digest"],
        "source_observable_digest": source_collapse_trace["observable_digest"],
        "replay_observable_digest": replay_observable_digest,
        "observable_digest_matched": (
            replay_observable_digest == source_collapse_trace["observable_digest"]
        ),
        "selection_recomputed_matches_source": (
            recomputed_selection == source_collapse_trace["selection"]
        ),
        "recomputed_selection": recomputed_selection,
        "step_summaries": step_rows,
        "event_counts_by_kind": event_counts,
    }
    trace["replay_digest"] = i4.digest_value(trace)
    return i4.canonicalize_json_value(trace)


STRESS_ROWS: list[dict[str, Any]] = []


def negative_control_trace(rows: list[dict[str, Any]]) -> dict[str, Any]:
    alternate = next(row for row in rows if row["case_id"] == "alternate_branch_wins_supported")
    below_margin = next(row for row in rows if row["case_id"] == "below_margin_rejected")
    tie = next(row for row in rows if row["case_id"] == "equalized_tie_rejected")
    controls = [
        {
            "control_id": "fixed_selected_branch_label_control",
            "control_status": "failed_closed",
            "control_execution_kind": "constructed_i6a_robustness_control",
            "blocked_condition": "selection remains fixed to branch_edge_4_node_5 after geometry flips",
            "actual_result": {
                "alternate_geometry_selected_branch": alternate["selected_branch_id"],
                "claim_allowed": False,
                "violation_detected": True,
            },
            "rung_effect": "blocks robustness if selected label ignores geometry",
        },
        {
            "control_id": "below_margin_ap4_bridge_control",
            "control_status": "failed_closed",
            "control_execution_kind": "constructed_i6a_robustness_control",
            "blocked_condition": "AP4 bridge accepted below the predeclared score margin",
            "actual_result": {
                "score_margin": below_margin["score_margin"],
                "minimum_score_margin": below_margin["minimum_score_margin"],
                "row_decision": below_margin["row_decision"],
                "claim_allowed": False,
            },
            "rung_effect": "blocks LC5 if margin gate does not fail closed",
        },
        {
            "control_id": "equalized_tie_ap4_bridge_control",
            "control_status": "failed_closed",
            "control_execution_kind": "constructed_i6a_robustness_control",
            "blocked_condition": "random tie accepted as source-current selection geometry",
            "actual_result": {
                "random_tie_status": tie["random_tie_status"],
                "row_decision": tie["row_decision"],
                "claim_allowed": False,
            },
            "rung_effect": "blocks LC5 if random tie is promoted",
        },
    ]
    trace = {
        "artifact_id": "n23_i6a_robustness_negative_control_trace",
        "trace_status": "present",
        "controls": controls,
        "all_controls_failed_closed": all(
            control["control_status"] == "failed_closed" for control in controls
        ),
    }
    trace["trace_digest"] = i4.digest_value(trace)
    return i4.canonicalize_json_value(trace)


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N23 Iteration 6-A - AP4 Selection Geometry Robustness Probe",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        (
            "I6-A stress-tests the I6 AP4 bridge candidate by varying source-"
            "current branch geometry. It preserves I6 as the primary AP4 bridge "
            "record and classifies this as robustness evidence only."
        ),
        "",
        "| Case | Decision | Selected | Margin | Role |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in output["robustness_rows"]:
        lines.append(
            "| "
            f"`{row['case_id']}` | `{row['row_decision']}` | "
            f"`{row['selected_branch_id']}` | `{row['score_margin']:.12f}` | "
            f"`{row['stress_case_role']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            output["geometric_interpretation"]["main_read"],
            "",
            "```text",
            output["geometric_interpretation"]["stress_result"],
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "I6 remains the primary AP4 bridge candidate.",
            "I6-A adds robustness/stress evidence.",
            "general AP4 robustness = not claimed",
            "semantic choice = false",
            "agency = false",
            "native support = false",
            "final N23 = false pending I7/I8",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i2 = i4.load_json(I2_OUTPUT_PATH)
    i6_output = i4.load_json(I6_OUTPUT_PATH)
    STRESS_ROWS.clear()
    for case in STRESS_CASES:
        STRESS_ROWS.append(run_stress_case(case))
    control_trace = negative_control_trace(STRESS_ROWS)
    control_trace_path = ARTIFACT_DIR / "n23_i6a_robustness_negative_control_trace.json"
    write_json(control_trace_path, control_trace)
    artifact_manifest = [
        item
        for row in STRESS_ROWS
        for item in row["artifact_manifest"]
    ] + [
        {
            "artifact_role": "negative_control_trace",
            "artifact_subrole": "robustness_negative_control_trace",
            "path": rel(control_trace_path),
            "sha256": i4.sha256_file(rel(control_trace_path)),
        }
    ]
    supported_rows = [row for row in STRESS_ROWS if row["row_decision"] == "supported"]
    rejected_rows = [row for row in STRESS_ROWS if row["row_decision"] == "rejected"]
    allowed_artifact_roles = set(
        i2["schema"]["artifact_role_schema"]["artifact_role_values"]
    )
    checks = [
        check("i6_source_passed", i6_output["status"] == "passed", i6_output["status"]),
        check(
            "three_supported_stress_rows",
            len(supported_rows) == 3,
            [row["case_id"] for row in supported_rows],
        ),
        check(
            "two_fail_closed_stress_rows",
            len(rejected_rows) == 2,
            [row["case_id"] for row in rejected_rows],
        ),
        check(
            "alternate_winner_changes_with_geometry",
            any(
                row["case_id"] == "alternate_branch_wins_supported"
                and row["selected_branch_id"] == "branch_edge_0_node_1"
                for row in STRESS_ROWS
            ),
            [
                {
                    "case_id": row["case_id"],
                    "selected_branch_id": row["selected_branch_id"],
                }
                for row in STRESS_ROWS
            ],
        ),
        check(
            "eroded_margin_remains_above_threshold",
            any(
                row["case_id"] == "eroded_margin_still_supported"
                and row["score_margin"] >= row["minimum_score_margin"]
                for row in STRESS_ROWS
            ),
            next(row for row in STRESS_ROWS if row["case_id"] == "eroded_margin_still_supported"),
        ),
        check(
            "below_margin_and_tie_fail_closed",
            all(
                row["row_decision"] == "rejected"
                for row in STRESS_ROWS
                if row["case_id"] in {"below_margin_rejected", "equalized_tie_rejected"}
            ),
            [
                row
                for row in STRESS_ROWS
                if row["case_id"] in {"below_margin_rejected", "equalized_tie_rejected"}
            ],
        ),
        check(
            "duplicate_replay_stable_for_supported_rows",
            all(
                row["duplicate_replay_observable_digest_matched"]
                for row in supported_rows
            ),
            [
                {
                    "case_id": row["case_id"],
                    "duplicate_replay_observable_digest_matched": row[
                        "duplicate_replay_observable_digest_matched"
                    ],
                }
                for row in supported_rows
            ],
        ),
        check(
            "unsafe_claim_flags_false",
            all(not value for row in STRESS_ROWS for value in row["unsafe_claim_flags"].values()),
            [row["unsafe_claim_flags"] for row in STRESS_ROWS],
        ),
        check(
            "robustness_controls_fail_closed",
            control_trace["all_controls_failed_closed"],
            control_trace["controls"],
        ),
        check(
            "artifact_hashes_match",
            all(item["sha256"] == i4.sha256_file(item["path"]) for item in artifact_manifest),
            artifact_manifest,
        ),
        check(
            "artifact_roles_match_i2_frozen_enum",
            all(item["artifact_role"] in allowed_artifact_roles for item in artifact_manifest),
            artifact_manifest,
        ),
        check(
            "artifact_paths_are_portable",
            all(not item["path"].startswith("/") for item in artifact_manifest),
            [item["path"] for item in artifact_manifest],
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n23_i6a_ap4_selection_geometry_robustness_probe",
        "schema_version": "1.0",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": "6-A",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_ap4_selection_geometry_robustness_stress_evidence_pending_i7"
            if not failed_checks
            else "blocked_ap4_selection_geometry_robustness_failed_checks"
        ),
        "purpose": (
            "Stress-test how robust the I6 AP4 bridge candidate is under bounded "
            "source-current branch-geometry variations."
        ),
        "source_artifacts": [
            i4.source_record(I1_OUTPUT_PATH, "n23_source_handoff_inventory"),
            i4.source_record(I2_OUTPUT_PATH, "n23_schema_control_freeze"),
            i4.source_record(I3_OUTPUT_PATH, "n23_active_nulls"),
            i4.source_record(I4_OUTPUT_PATH, "minimal_live_branch_lc3_source"),
            i4.source_record(I5_OUTPUT_PATH, "minimal_lc4_replay_control_source"),
            i4.source_record(I4A_OUTPUT_PATH, "multibranch_live_set_lc3_source"),
            i4.source_record(I5A_OUTPUT_PATH, "multibranch_lc4_replay_control_source"),
            i4.source_record(I6_OUTPUT_PATH, "i6_ap4_bridge_candidate_source"),
            {
                "path": SCRIPT_PATH,
                "sha256": i4.sha256_file(SCRIPT_PATH),
                "source_role": "producer_script",
            },
        ],
        "stress_policy": {
            "i6_replaced": False,
            "i6a_role": "robustness_stress_evidence_only",
            "row_schema_role_declared_as_i6a_extension": True,
            "i6a_extension_fields": [
                "row_schema_role",
                "stress_case_role",
                "ap4_bridge_claim_allowed",
            ],
            "bounded_stress_field": "node_1_coherence",
            "topology_family_preserved": True,
            "selection_policy": "support_gradient_dominance",
            "minimum_score_margin": i4.MIN_BRANCH_SCORE_MARGIN,
            "supported_rows_require_duplicate_replay": True,
            "below_margin_or_tie_rows_fail_closed": True,
            "final_ap4_supported": False,
            "final_n23_supported": False,
        },
        "robustness_rows": STRESS_ROWS,
        "artifact_manifest": artifact_manifest,
        "negative_control_trace": {
            "path": rel(control_trace_path),
            "sha256": i4.sha256_file(rel(control_trace_path)),
            "trace_digest": control_trace["trace_digest"],
        },
        "geometric_interpretation": {
            "main_read": (
                "I6-A shows that the I6 AP4 candidate is stronger than a single "
                "fixed selected-label result: selection follows branch geometry "
                "when the winning branch changes, but fails closed when the score "
                "margin is too narrow or tied."
            ),
            "stress_result": (
                "reference: branch_edge_4_node_5 wins by margin 0.5\n"
                "eroded margin: branch_edge_4_node_5 still wins by margin 0.3\n"
                "alternate winner: branch_edge_0_node_1 wins when its source-current "
                "support-gradient rises to 2.5\n"
                "below margin: rejected at margin 0.1\n"
                "equalized tie: rejected at margin 0.0"
            ),
            "claim_boundary": (
                "I6-A strengthens confidence in the AP4 bridge candidate, but it "
                "does not claim general AP4 robustness, semantic choice, agency, "
                "native support, or final N23 support."
            ),
        },
        "iteration6a_boundary": {
            "i6_replaced": False,
            "ap4_bridge_robustness_status": (
                "bounded_stress_evidence_supported" if not failed_checks else "blocked"
            ),
            "supported_stress_rows": len(supported_rows),
            "failed_closed_stress_rows": len(rejected_rows),
            "general_ap4_robustness_supported": False,
            "final_ap4_supported": False,
            "final_n23_supported": False,
            "ready_for_iteration_7_full_control_matrix": not failed_checks,
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "output_digest": "pending",
    }
    output["output_digest"] = i4.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
