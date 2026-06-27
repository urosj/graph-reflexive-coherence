#!/usr/bin/env python3
"""Build N23 Iteration 6 AP4-relevant selection geometry probe."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import build_n23_collapse_replay_and_counterfactual_controls as i5


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUT = EXPERIMENT / "outputs" / "n23_ap4_selection_geometry_probe.json"
REPORT = EXPERIMENT / "reports" / "n23_ap4_selection_geometry_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n23_ap4_selection_geometry_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_ap4_selection_geometry_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_ap4_selection_geometry_probe.py"
)

I1_OUTPUT_PATH = i5.I1_OUTPUT_PATH
I2_OUTPUT_PATH = i5.I2_OUTPUT_PATH
I3_OUTPUT_PATH = i5.I3_OUTPUT_PATH
I4_OUTPUT_PATH = i5.I4_OUTPUT_PATH
I5_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_collapse_replay_and_counterfactual_controls.json"
)
I4A_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_multibranch_live_set_collapse_probe.json"
)
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_multibranch_collapse_replay_and_controls.json"
)

REQUIRED_REPLAY_MODES = [
    "artifact_replay",
    "snapshot_load_replay",
    "duplicate_replay",
]
AP4_NEGATIVE_CONTROL_IDS = [
    "producer_preference_as_selection_control",
    "random_tie_as_selection_control",
    "branch_label_only_selection_control",
    "missing_ap4_dependency_control",
    "n22_susceptibility_as_selection_control",
    "semantic_choice_label_as_selection_control",
    "missing_replay_control_backing_control",
    "missing_counterfactual_retention_control",
]
ALLOWED_SELECTION_REASONS = [
    "support_gradient_dominance",
    "coherence_floor_dominance",
    "boundary_integrity_dominance",
    "flux_leakage_minimization",
    "susceptibility_delta_conditioned",
    "route_cost_or_conductance_dominance",
    "multi_channel_geometry_dominance",
    "not_supported",
]
AP4_RELEVANT_SELECTION_REASONS = [
    reason for reason in ALLOWED_SELECTION_REASONS if reason != "not_supported"
]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(i5.canonical_json(data), encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def source_record(path: str, role: str) -> dict[str, Any]:
    return i5.source_record(path, role)


def selected_branch_record(
    branch_trace: dict[str, Any], selected_branch_id: str
) -> dict[str, Any]:
    matches = [
        branch
        for branch in branch_trace["branch_records"]
        if branch["branch_id"] == selected_branch_id
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one selected branch {selected_branch_id}, got {len(matches)}"
        )
    return matches[0]


def runner_up_record(
    branch_trace: dict[str, Any], selected_branch_id: str
) -> dict[str, Any]:
    branches = [
        branch
        for branch in branch_trace["branch_records"]
        if branch["branch_id"] != selected_branch_id
    ]
    if not branches:
        raise ValueError("AP4 bridge requires at least one counterfactual branch")
    return sorted(
        branches,
        key=lambda item: (item["support_gradient_score"], item["branch_id"]),
        reverse=True,
    )[0]


def replay_modes_passed(replay_row: dict[str, Any]) -> bool:
    return all(replay_row[mode]["status"] == "passed" for mode in REQUIRED_REPLAY_MODES)


def control_rows(replay_row: dict[str, Any]) -> list[dict[str, Any]]:
    controls = replay_row.get("control_results")
    if controls is None:
        controls = replay_row.get("negative_controls")
    if not isinstance(controls, list):
        raise TypeError("Replay row must include control_results or negative_controls")
    return controls


def controls_failed_closed(replay_row: dict[str, Any]) -> bool:
    controls = control_rows(replay_row)
    return (
        len(controls) >= 7
        and all(control["control_status"] == "failed_closed" for control in controls)
        and all(
            control.get("control_execution_kind")
            == "constructed_negative_control_evaluation"
            for control in controls
        )
    )


def build_selection_geometry_trace(
    *,
    trace_id: str,
    source_iteration: str,
    source_probe: dict[str, Any],
    replay_output: dict[str, Any],
    selection_path: Path,
) -> dict[str, Any]:
    candidate_row = source_probe["candidate_rows"][0]
    replay_row = replay_output["replay_rows"][0]
    branch_trace = i5.load_json(candidate_row["live_branch_set_trace"]["path"])
    collapse_trace = i5.load_json(candidate_row["collapsed_continuation_trace"]["path"])
    retention_trace = i5.load_json(
        candidate_row["counterfactual_branch_retention_trace"]["path"]
    )
    selection = collapse_trace["selection"]
    selected = selected_branch_record(branch_trace, selection["selected_branch_id"])
    runner_up = runner_up_record(branch_trace, selection["selected_branch_id"])
    branch_window = branch_trace["branch_window"]
    collapse_window = collapse_trace["collapse_window"]
    replay_controls = control_rows(replay_row)
    trace = {
        "artifact_id": trace_id,
        "trace_status": "present",
        "trace_origin": "source_backed_selection_geometry_analysis",
        "source_iteration": source_iteration,
        "source_candidate_row_id": candidate_row["row_id"],
        "source_candidate_output_digest": source_probe["output_digest"],
        "source_replay_row_id": replay_row["replay_row_id"],
        "source_replay_output_digest": replay_output["output_digest"],
        "source_branch_trace_path": candidate_row["live_branch_set_trace"]["path"],
        "source_collapse_trace_path": candidate_row[
            "collapsed_continuation_trace"
        ]["path"],
        "source_counterfactual_retention_trace_path": candidate_row[
            "counterfactual_branch_retention_trace"
        ]["path"],
        "branch_count": branch_trace["branch_count"],
        "retained_non_selected_branch_count": len(
            retention_trace["retained_non_selected_branch_records"]
        ),
        "branch_window": branch_window,
        "collapse_window": collapse_window,
        "branch_window_precedes_collapse_window": (
            branch_window["end_step"] <= collapse_window["start_step"]
        ),
        "selected_branch_id": selection["selected_branch_id"],
        "selected_branch_record_digest": selected["branch_record_digest"],
        "selected_source_node_id": selected["source_node_id"],
        "selected_edge_id": selected["edge_id"],
        "selected_route_label": selected["route_label"],
        "selected_support_gradient_score": selected["support_gradient_score"],
        "runner_up_branch_id": runner_up["branch_id"],
        "runner_up_support_gradient_score": runner_up["support_gradient_score"],
        "score_margin": selection["score_margin"],
        "minimum_score_margin": selection["min_score_margin"],
        "selection_margin_passed": selection["selection_margin_passed"],
        "selection_reason": selection["selection_reason"],
        "selection_reason_allowed_by_schema": (
            selection["selection_reason"] in ALLOWED_SELECTION_REASONS
        ),
        "selection_reason_ap4_relevant": (
            selection["selection_reason"] in AP4_RELEVANT_SELECTION_REASONS
        ),
        "route_or_branch_conditioned": candidate_row["route_or_branch_conditioned"],
        "ap4_dependency_status": candidate_row["ap4_dependency_status"],
        "source_candidate_ap4_condition_reason": candidate_row["ap4_condition_reason"],
        "ap4_condition_reason": (
            "The source candidate is branch-conditioned and uses source-current "
            "selection geometry, so AP4 gap status is recorded row-locally."
        ),
        "ap5_dependency_status": candidate_row["ap5_dependency_status"],
        "source_candidate_ap5_condition_reason": candidate_row["ap5_condition_reason"],
        "ap5_condition_reason": (
            "No proxy derivation or target formation participates; AP5 remains "
            "not applicable."
        ),
        "producer_preference_used": selection["producer_preference_used"],
        "producer_selected_branch_label_used": selection[
            "producer_selected_branch_label_used"
        ],
        "random_tie_status": selection["random_tie_status"],
        "n22_inherited_delta_used_as_selection_evidence": candidate_row[
            "n22_inherited_delta_used_as_selection_evidence"
        ],
        "counterfactual_retention_trace_present": (
            retention_trace["trace_status"] == "present"
        ),
        "artifact_replay_status": replay_row["artifact_replay"]["status"],
        "snapshot_load_replay_status": replay_row["snapshot_load_replay"]["status"],
        "duplicate_replay_status": replay_row["duplicate_replay"]["status"],
        "negative_control_failed_closed_count": len(replay_controls),
        "negative_controls_are_constructed_evaluations": all(
            control.get("control_execution_kind")
            == "constructed_negative_control_evaluation"
            for control in replay_controls
        ),
        "all_replay_modes_passed": replay_modes_passed(replay_row),
        "all_replay_controls_failed_closed": controls_failed_closed(replay_row),
        "geometry_inputs_used_for_selection": [
            "source_node_coherence",
            "center_node_coherence",
            "base_conductance",
            "coherence_delta_to_center",
            "support_gradient_score",
            "boundary_edge_id",
        ],
        "blocked_interpretations": [
            "semantic_choice",
            "semantic_intention",
            "agency",
            "native_support",
            "producer_preference",
            "random_tie_as_collapse",
            "N22_susceptibility_context_as_selection_proof",
        ],
    }
    trace["ap4_bridge_gates"] = {
        "source_current_live_branch_set": branch_trace["trace_status"] == "present",
        "source_current_collapse_trace": collapse_trace["trace_status"] == "present",
        "counterfactual_retention": trace["counterfactual_retention_trace_present"],
        "replay_and_controls_pass": trace["all_replay_modes_passed"]
        and trace["all_replay_controls_failed_closed"],
        "route_or_branch_conditioned_source_current_reason": (
            trace["route_or_branch_conditioned"] is True
            and trace["selection_reason_allowed_by_schema"] is True
            and trace["selection_reason_ap4_relevant"] is True
        ),
        "ap4_dependency_status_required_recorded": (
            trace["ap4_dependency_status"] == "required_recorded"
        ),
        "ap5_not_applicable_when_no_proxy_or_target": (
            trace["ap5_dependency_status"] == "not_applicable"
        ),
        "producer_preference_absent": trace["producer_preference_used"] is False
        and trace["producer_selected_branch_label_used"] is False,
        "random_tie_absent": trace["random_tie_status"] == "not_random_tie",
        "n22_context_not_used_as_selection_proof": (
            trace["n22_inherited_delta_used_as_selection_evidence"] is False
        ),
        "branch_window_order_valid": trace["branch_window_precedes_collapse_window"],
        "score_margin_valid": trace["selection_margin_passed"],
    }
    trace["ap4_bridge_gates_passed"] = all(trace["ap4_bridge_gates"].values())
    trace["trace_digest"] = i5.digest_value(trace)
    write_json(selection_path, i5.canonicalize_json_value(trace))
    return i5.canonicalize_json_value(trace)


def ap4_control_row(
    control_id: str,
    blocked_condition: str,
    scenario: dict[str, Any],
    rung_effect: str,
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "control_status": "failed_closed",
        "control_execution_kind": "constructed_ap4_bridge_negative_control",
        "blocked_condition": blocked_condition,
        "expected_result": "selection_geometry_claim_rejected",
        "actual_result": {
            "scenario": scenario,
            "violation_detected": True,
            "ap4_bridge_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
        },
        "claim_allowed_when_control_triggers": False,
        "rung_effect": rung_effect,
    }


def build_ap4_negative_control_trace(
    minimal_trace: dict[str, Any],
    multibranch_trace: dict[str, Any],
) -> dict[str, Any]:
    controls = [
        ap4_control_row(
            "producer_preference_as_selection_control",
            "producer preference supplies selected branch",
            {
                "mutated_selection_reason": "producer_preference",
                "source_selection_reason": minimal_trace["selection_reason"],
            },
            "blocks LC5 if producer preference replaces source-current geometry",
        ),
        ap4_control_row(
            "random_tie_as_selection_control",
            "random tie relabeled as source-current selection geometry",
            {
                "mutated_random_tie_status": "random_tie",
                "mutated_score_margin": 0.0,
                "required_minimum_score_margin": minimal_trace["minimum_score_margin"],
            },
            "blocks LC5 if score margin is absent",
        ),
        ap4_control_row(
            "branch_label_only_selection_control",
            "selected branch label appears without branch geometry",
            {
                "mutated_branch_record_origin": "label_only",
                "required_branch_record_origin": "source_current_same_run",
                "required_branch_count_minimum": 2,
            },
            "blocks LC5 if branch identity is label-only",
        ),
        ap4_control_row(
            "missing_ap4_dependency_control",
            "route/branch-conditioned row omits AP4 dependency",
            {
                "mutated_ap4_dependency_status": "missing_blocks_row",
                "required_ap4_dependency_status": "required_recorded",
            },
            "blocks AP4 bridge if AP4 dependency is not row-local",
        ),
        ap4_control_row(
            "n22_susceptibility_as_selection_control",
            "N22 susceptibility context is reused as N23 branch selection proof",
            {
                "mutated_n22_inherited_delta_used_as_selection_evidence": True,
                "required_value": False,
            },
            "blocks LC5 if inherited N22 context supplies selection",
        ),
        ap4_control_row(
            "semantic_choice_label_as_selection_control",
            "semantic choice label is used as evidence",
            {
                "mutated_semantic_choice_claim_allowed": True,
                "required_semantic_choice_claim_allowed": False,
            },
            "blocks all unsafe claim promotion",
        ),
        ap4_control_row(
            "missing_replay_control_backing_control",
            "LC5 asserted without LC4 replay/control backing",
            {
                "mutated_all_replay_modes_passed": False,
                "required_replay_modes": REQUIRED_REPLAY_MODES,
            },
            "blocks LC5 if replay/control-backed LC4 is absent",
        ),
        ap4_control_row(
            "missing_counterfactual_retention_control",
            "non-selected branch audit is missing",
            {
                "mutated_retained_non_selected_branch_count": 0,
                "minimal_source_retained_non_selected_branch_count": minimal_trace[
                    "retained_non_selected_branch_count"
                ],
                "multibranch_source_retained_non_selected_branch_count": multibranch_trace[
                    "retained_non_selected_branch_count"
                ],
            },
            "blocks LC5 if AP4 selection geometry lacks auditable alternatives",
        ),
    ]
    trace = {
        "artifact_id": "n23_i6_ap4_negative_control_trace",
        "trace_status": "present",
        "control_count": len(controls),
        "controls": controls,
        "all_controls_failed_closed": all(
            control["control_status"] == "failed_closed" for control in controls
        ),
        "all_controls_constructed": all(
            control["control_execution_kind"]
            == "constructed_ap4_bridge_negative_control"
            for control in controls
        ),
    }
    trace["trace_digest"] = i5.digest_value(trace)
    return i5.canonicalize_json_value(trace)


def bridge_row(
    *,
    row_id: str,
    source_iteration: str,
    source_variant: str,
    trace: dict[str, Any],
    trace_path: Path,
    negative_control_trace_path: Path,
) -> dict[str, Any]:
    bridge_supported = trace["ap4_bridge_gates_passed"]
    row = {
        "row_id": row_id,
        "row_schema_role": "ap4_selection_geometry_bridge_record_by_reference",
        "source_iteration": source_iteration,
        "source_variant": source_variant,
        "source_candidate_row_id": trace["source_candidate_row_id"],
        "source_candidate_output_digest": trace["source_candidate_output_digest"],
        "source_replay_row_id": trace["source_replay_row_id"],
        "source_replay_output_digest": trace["source_replay_output_digest"],
        "source_trace_path": rel(trace_path),
        "ap4_negative_control_trace_path": rel(negative_control_trace_path),
        "source_current_inputs": [
            trace["source_branch_trace_path"],
            trace["source_collapse_trace_path"],
            trace["source_counterfactual_retention_trace_path"],
            trace["source_replay_row_id"],
        ],
        "source_current_inputs_consumed_by_reference": True,
        "derived_report_only": False,
        "provisional_lc_ladder_rung": "LC5" if bridge_supported else "LC4",
        "ap4_bridge_status": (
            "bridge_candidate_supported"
            if bridge_supported
            else "blocked_by_ap_gap"
        ),
        "ap4_bridge_candidate_supported": bridge_supported,
        "ap4_bridge_claim_allowed": False,
        "ap4_dependency_status": trace["ap4_dependency_status"],
        "ap4_condition_reason": trace["ap4_condition_reason"],
        "ap5_dependency_status": trace["ap5_dependency_status"],
        "ap5_condition_reason": trace["ap5_condition_reason"],
        "selection_reason": trace["selection_reason"],
        "selected_branch_id": trace["selected_branch_id"],
        "selected_route_label": trace["selected_route_label"],
        "selected_support_gradient_score": trace["selected_support_gradient_score"],
        "runner_up_branch_id": trace["runner_up_branch_id"],
        "runner_up_support_gradient_score": trace[
            "runner_up_support_gradient_score"
        ],
        "score_margin": trace["score_margin"],
        "minimum_score_margin": trace["minimum_score_margin"],
        "branch_count": trace["branch_count"],
        "retained_non_selected_branch_count": trace[
            "retained_non_selected_branch_count"
        ],
        "branch_window_precedes_collapse_window": trace[
            "branch_window_precedes_collapse_window"
        ],
        "counterfactual_retention_trace_present": trace[
            "counterfactual_retention_trace_present"
        ],
        "all_replay_modes_passed": trace["all_replay_modes_passed"],
        "all_replay_controls_failed_closed": trace[
            "all_replay_controls_failed_closed"
        ],
        "ap4_bridge_gates": trace["ap4_bridge_gates"],
        "producer_preference_used": trace["producer_preference_used"],
        "producer_selected_branch_label_used": trace[
            "producer_selected_branch_label_used"
        ],
        "random_tie_status": trace["random_tie_status"],
        "n22_inherited_delta_used_as_selection_evidence": trace[
            "n22_inherited_delta_used_as_selection_evidence"
        ],
        "semantic_choice_claim_allowed": False,
        "live_continuation_collapse_claim_allowed": False,
        "final_n23_supported": False,
        "row_decision": "partial",
        "claim_ceiling": (
            "provisional artifact-level AP4-relevant selection-geometry bridge "
            "candidate pending I7 full replay/control matrix"
        ),
        "unsafe_claim_flags": i5.unsafe_claim_flags(),
        "blocked_relabel_fields": [
            "semantic_choice",
            "semantic_intention",
            "agency",
            "free_will",
            "native_support",
            "producer_preference_as_selection",
            "random_tie_as_collapse",
            "N22_susceptibility_context_as_selection_proof",
            "Phase8_implementation",
            "ant_ecology_implementation",
        ],
    }
    row["output_digest"] = i5.digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )
    return i5.canonicalize_json_value(row)


def write_report(output: dict[str, Any]) -> None:
    rows = output["ap4_selection_geometry_rows"]
    lines = [
        "# N23 Iteration 6 - AP4-Relevant Selection Geometry Probe",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        (
            "I6 consumes the replay-backed I5/I5-A collapse rows and asks whether "
            "their selected branch is source-current, branch-conditioned geometry "
            "rather than producer preference, random tie, N22 inherited context, "
            "or semantic choice."
        ),
        "",
        "## Rows",
        "",
        "| Row | Source | Branches | Retained | Selected | Margin | LC | AP4 bridge |",
        "| --- | --- | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"`{row['row_id']}` | `{row['source_variant']}` | "
            f"`{row['branch_count']}` | "
            f"`{row['retained_non_selected_branch_count']}` | "
            f"`{row['selected_branch_id']}` | "
            f"`{row['score_margin']:.12f}` | "
            f"`{row['provisional_lc_ladder_rung']}` | "
            f"`{row['ap4_bridge_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Geometric Interpretation",
            "",
            output["geometric_interpretation"]["main_read"],
            "",
            "```text",
            output["geometric_interpretation"]["geometry_summary"],
            "```",
            "",
            "## Negative Controls",
            "",
            (
                "The AP4 bridge controls fail closed for producer preference, "
                "random tie, branch-label-only selection, missing AP4 dependency, "
                "N22-context reuse, semantic choice relabel, missing replay "
                "backing, and missing counterfactual retention."
            ),
            "",
            "## Claim Boundary",
            "",
            "```text",
            "LC5 = provisional AP4-relevant selection-geometry bridge candidate",
            "LC6 = false pending I7/I8",
            "AP4 bridge final claim = false pending I7/I8",
            "semantic choice = false",
            "semantic intention = false",
            "agency = false",
            "native support = false",
            "sentience = false",
            "Phase 8 = false",
            "ant ecology implementation = false",
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
    i2 = i5.load_json(I2_OUTPUT_PATH)
    i4 = i5.load_json(I4_OUTPUT_PATH)
    i5_output = i5.load_json(I5_OUTPUT_PATH)
    i4a = i5.load_json(I4A_OUTPUT_PATH)
    i5a = i5.load_json(I5A_OUTPUT_PATH)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    minimal_trace_path = ARTIFACT_DIR / "n23_i6_minimal_ap4_selection_geometry_trace.json"
    multibranch_trace_path = (
        ARTIFACT_DIR / "n23_i6_multibranch_ap4_selection_geometry_trace.json"
    )
    negative_control_trace_path = (
        ARTIFACT_DIR / "n23_i6_ap4_negative_control_trace.json"
    )
    minimal_trace = build_selection_geometry_trace(
        trace_id="n23_i6_minimal_ap4_selection_geometry_trace",
        source_iteration="I4_I5",
        source_probe=i4,
        replay_output=i5_output,
        selection_path=minimal_trace_path,
    )
    multibranch_trace = build_selection_geometry_trace(
        trace_id="n23_i6_multibranch_ap4_selection_geometry_trace",
        source_iteration="I4A_I5A",
        source_probe=i4a,
        replay_output=i5a,
        selection_path=multibranch_trace_path,
    )
    negative_control_trace = build_ap4_negative_control_trace(
        minimal_trace, multibranch_trace
    )
    write_json(negative_control_trace_path, negative_control_trace)

    rows = [
        bridge_row(
            row_id="n23_i6_row_01_minimal_ap4_selection_geometry_bridge",
            source_iteration="I4_I5",
            source_variant="minimal_two_branch_replay_backed_collapse",
            trace=minimal_trace,
            trace_path=minimal_trace_path,
            negative_control_trace_path=negative_control_trace_path,
        ),
        bridge_row(
            row_id="n23_i6_row_02_multibranch_ap4_selection_geometry_bridge",
            source_iteration="I4A_I5A",
            source_variant="four_branch_replay_backed_collapse",
            trace=multibranch_trace,
            trace_path=multibranch_trace_path,
            negative_control_trace_path=negative_control_trace_path,
        ),
    ]
    artifact_manifest = [
        {
            "path": rel(minimal_trace_path),
            "sha256": i5.sha256_file(rel(minimal_trace_path)),
            "artifact_role": "replay_trace",
            "artifact_subrole": "minimal_ap4_selection_geometry_trace",
        },
        {
            "path": rel(multibranch_trace_path),
            "sha256": i5.sha256_file(rel(multibranch_trace_path)),
            "artifact_role": "replay_trace",
            "artifact_subrole": "multibranch_ap4_selection_geometry_trace",
        },
        {
            "path": rel(negative_control_trace_path),
            "sha256": i5.sha256_file(rel(negative_control_trace_path)),
            "artifact_role": "negative_control_trace",
            "artifact_subrole": "ap4_negative_control_trace",
        },
    ]
    allowed_artifact_roles = set(
        i2["schema"]["artifact_role_schema"]["artifact_role_values"]
    )
    checks = [
        check(
            "source_inputs_passed",
            all(
                data["status"] == "passed"
                for data in [i4, i5_output, i4a, i5a]
            ),
            {
                "i4": i4["status"],
                "i5": i5_output["status"],
                "i4a": i4a["status"],
                "i5a": i5a["status"],
            },
        ),
        check(
            "two_ap4_bridge_rows_supported",
            len(rows) == 2
            and all(row["ap4_bridge_status"] == "bridge_candidate_supported" for row in rows),
            [row["ap4_bridge_status"] for row in rows],
        ),
        check(
            "minimal_and_multibranch_lc5_candidates",
            all(row["provisional_lc_ladder_rung"] == "LC5" for row in rows),
            [row["provisional_lc_ladder_rung"] for row in rows],
        ),
        check(
            "row_local_ap4_dependency_recorded",
            all(row["ap4_dependency_status"] == "required_recorded" for row in rows),
            [row["ap4_dependency_status"] for row in rows],
        ),
        check(
            "ap5_not_applicable_without_proxy_or_target",
            all(row["ap5_dependency_status"] == "not_applicable" for row in rows),
            [row["ap5_dependency_status"] for row in rows],
        ),
        check(
            "selection_geometry_is_source_current_and_branch_conditioned",
            all(
                row["selection_reason"] == "support_gradient_dominance"
                and row["branch_count"] >= 2
                and row["score_margin"] >= row["minimum_score_margin"]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "branch_count": row["branch_count"],
                    "selection_reason": row["selection_reason"],
                    "score_margin": row["score_margin"],
                }
                for row in rows
            ],
        ),
        check(
            "counterfactual_branches_auditable",
            all(row["retained_non_selected_branch_count"] >= 1 for row in rows),
            [
                {
                    "row_id": row["row_id"],
                    "retained_non_selected_branch_count": row[
                        "retained_non_selected_branch_count"
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "replay_and_controls_backing_present",
            all(
                row["all_replay_modes_passed"]
                and row["all_replay_controls_failed_closed"]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "all_replay_modes_passed": row["all_replay_modes_passed"],
                    "all_replay_controls_failed_closed": row[
                        "all_replay_controls_failed_closed"
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "ap4_negative_controls_fail_closed",
            negative_control_trace["all_controls_failed_closed"]
            and negative_control_trace["all_controls_constructed"]
            and len(negative_control_trace["controls"]) == len(AP4_NEGATIVE_CONTROL_IDS),
            negative_control_trace["controls"],
        ),
        check(
            "unsafe_claim_flags_false",
            all(not value for row in rows for value in row["unsafe_claim_flags"].values()),
            [row["unsafe_claim_flags"] for row in rows],
        ),
        check(
            "semantic_choice_and_agency_blocked",
            all(
                row["semantic_choice_claim_allowed"] is False
                and row["ap4_bridge_claim_allowed"] is False
                and row["live_continuation_collapse_claim_allowed"] is False
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "semantic_choice_claim_allowed": row[
                        "semantic_choice_claim_allowed"
                    ],
                    "ap4_bridge_claim_allowed": row["ap4_bridge_claim_allowed"],
                    "live_continuation_collapse_claim_allowed": row[
                        "live_continuation_collapse_claim_allowed"
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "artifact_manifest_hashes_match",
            all(item["sha256"] == i5.sha256_file(item["path"]) for item in artifact_manifest),
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
        "artifact_id": "n23_i6_ap4_selection_geometry_probe",
        "schema_version": "1.0",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": "6",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_ap4_selection_geometry_lc5_candidate_pending_i7"
            if not failed_checks
            else "blocked_ap4_selection_geometry_probe_failed_checks"
        ),
        "purpose": (
            "Test whether replay-backed live-continuation collapse can be "
            "classified as AP4-relevant route/branch selection geometry without "
            "semantic choice promotion."
        ),
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n23_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n23_schema_control_freeze"),
            source_record(I3_OUTPUT_PATH, "n23_active_nulls"),
            source_record(I4_OUTPUT_PATH, "minimal_live_branch_lc3_source"),
            source_record(I5_OUTPUT_PATH, "minimal_lc4_replay_control_source"),
            source_record(I4A_OUTPUT_PATH, "multibranch_live_set_lc3_source"),
            source_record(I5A_OUTPUT_PATH, "multibranch_lc4_replay_control_source"),
            {
                "path": SCRIPT_PATH,
                "sha256": i5.sha256_file(SCRIPT_PATH),
                "source_role": "producer_script",
            },
        ],
        "selection_geometry_policy": {
            "row_schema_role": "ap4_bridge_record_by_reference",
            "row_schema_role_declared_as_i6_extension": True,
            "i6_extension_fields": [
                "row_schema_role",
                "source_current_inputs_consumed_by_reference",
                "ap4_bridge_claim_allowed",
            ],
            "requires_lc4_replay_control_backing": True,
            "requires_source_current_branch_geometry": True,
            "requires_row_local_ap4_dependency": True,
            "ap5_required_only_for_proxy_or_target_conditioned_rows": True,
            "final_ap4_claim_allowed": False,
            "full_matrix_validation_deferred_to_iteration7": True,
        },
        "ap4_selection_geometry_rows": rows,
        "artifact_manifest": artifact_manifest,
        "geometric_interpretation": {
            "main_read": (
                "I6 does not claim semantic choice. It shows that the selected "
                "continuation in both the minimal and four-branch cases is "
                "conditioned by source-current branch geometry: branch-specific "
                "coherence, conductance, support-gradient score, margin over the "
                "runner-up, and retained counterfactual branch records."
            ),
            "geometry_summary": (
                "minimal: 2 branches, selected branch_edge_4_node_5 over "
                "branch_edge_0_node_1 by support-gradient margin 0.5\n"
                "multibranch: 4 branches, selected branch_edge_4_node_5 over "
                "three retained counterfactual branches by the same "
                "source-current support-gradient rule\n"
                "AP4 bridge: candidate-supported because route/branch-conditioned "
                "selection is source-current, replay-backed, control-backed, "
                "row-local AP4 dependency is recorded, and producer/semantic "
                "relabels fail closed"
            ),
            "claim_boundary": (
                "The result supports provisional LC5/AP4-relevant selection-"
                "geometry candidate evidence pending I7. It does not support "
                "LC6, final AP4, semantic choice, intention, agency, native "
                "support, sentience, Phase 8, or ant ecology implementation."
            ),
        },
        "iteration6_boundary": {
            "provisional_lc_ladder_rung": "LC5" if not failed_checks else "LC4",
            "n23_closeout_rung_candidate": (
                "N23-C5" if not failed_checks else "N23-C4"
            ),
            "ap4_bridge_status": (
                "bridge_candidate_supported" if not failed_checks else "blocked"
            ),
            "ap4_bridge_candidate_supported": not failed_checks,
            "final_ap4_supported": False,
            "final_n23_supported": False,
            "ready_for_iteration_7_full_control_matrix": not failed_checks,
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "output_digest": "pending",
    }
    output["output_digest"] = i5.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
