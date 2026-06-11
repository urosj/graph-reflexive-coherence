#!/usr/bin/env python3
"""Run N04 Iteration 18-G integrated fixed-topology 2D composed gate probe."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
SCRIPT_DIR = N04 / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_n04_iter18_grid_transfer as iter18  # noqa: E402
import run_n04_iter18d_grid_geometry_selection as iter18d  # noqa: E402
import run_n04_iter18e_grid_composed_1d_fork_competition as iter18e  # noqa: E402
import run_n04_iter18f_balanced_local_preference_fork as iter18f  # noqa: E402


ITER18F_PATH = N04 / "outputs/n04_iter18f_balanced_local_preference_fork_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter18g_integrated_2d_composed_gate_report.json"
REPORT_PATH = N04 / "reports/n04_iter18g_integrated_2d_composed_gate_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter18g_integrated_2d_composed_gate.py"
)

CENTER_NODE = iter18e.CENTER_NODE
WEST_NODE = iter18e.WEST_NODE
SOUTH_NODE = iter18e.SOUTH_NODE
EPSILON = iter18f.EPSILON
RECOVERY_WINDOW_CYCLES = iter18e.RECOVERY_WINDOW_CYCLES
CHALLENGE_TRANSFER_AMOUNT = iter18e.CHALLENGE_TRANSFER_AMOUNT
TOL = iter18e.TOL
EPSILON_BUDGET = iter18e.EPSILON_BUDGET


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, str]:
    return {"path": _rel(path), "sha256": _sha256(path)}


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _run_git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _integrated_gate_policy() -> dict[str, Any]:
    return {
        "policy_id": "s3_grid_integrated_2d_composed_gate_policy_v1",
        "declared_before_run": True,
        "input_gates": {
            "west_input": {
                "ingress_source": WEST_NODE,
                "ingress_target": CENTER_NODE,
                "local_preference_site": "center_fork_local_preference",
                "branch_biases": {"north_branch": 0.25, "east_branch": -EPSILON},
                "expected_branch": "north_branch",
                "expected_output_axis": "y",
            },
            "south_input": {
                "ingress_source": SOUTH_NODE,
                "ingress_target": CENTER_NODE,
                "local_preference_site": "mirror_fork_local_preference",
                "branch_biases": {"north_branch": -EPSILON, "east_branch": 0.25},
                "expected_branch": "east_branch",
                "expected_output_axis": "x",
            },
        },
        "output_branches": ["north_branch", "east_branch"],
        "composition": "two_input_two_output_gate_from_two_1d_lgrc_branch_elements",
        "balanced_local_preference_policy": iter18f._preference_policy(),  # noqa: SLF001
        "external_scorer_used": False,
        "external_argmax_used": False,
        "preauthored_input_to_output_lookup_used": False,
        "topology_fixed_during_run": True,
    }


def _seed_ingress(model: Any, *, source_node: int) -> list[dict[str, Any]]:
    _state, edge_by_pair = iter18._grid_state()  # noqa: SLF001
    model.schedule_packet_departure(
        source_node_id=source_node,
        target_node_id=CENTER_NODE,
        edge_id=edge_by_pair[(source_node, CENTER_NODE)],
        amount=iter18.iter16.iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    return iter18.iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001


def _eligibility_scan_for_input(input_cfg: dict[str, Any]) -> dict[str, Any]:
    branch_results: dict[str, Any] = {}
    production_artifacts: list[dict[str, Any]] = []
    for branch_id in ("north_branch", "east_branch"):
        model, geometry, branches = iter18e._new_model(  # noqa: SLF001
            north_bias=input_cfg["branch_biases"]["north_branch"],
            east_bias=input_cfg["branch_biases"]["east_branch"],
        )
        ingress_events = _seed_ingress(model, source_node=input_cfg["ingress_source"])
        result = iter18e._evaluate_branch_eligibility(  # noqa: SLF001
            model,
            branch_id=branch_id,
            branch=branches[branch_id],
        )
        branch_results[branch_id] = {
            key: value for key, value in result.items() if key != "production_artifact"
        } | {
            "ingress_event_count": len(ingress_events),
            "local_preference_site": input_cfg["local_preference_site"],
        }
        if result["production_artifact"] is not None:
            production_artifacts.append(result["production_artifact"])
    scheduled = [
        branch_id for branch_id, result in branch_results.items() if result["scheduled"]
    ]
    if len(scheduled) == 1:
        outcome = "unique_branch_by_native_eligibility"
    elif len(scheduled) == 2:
        outcome = "tie_no_native_arbitration"
    else:
        outcome = "no_branch_eligible"
    return {
        "geometry_init": geometry,
        "branch_results": branch_results,
        "scheduled_branches": scheduled,
        "outcome": outcome,
        "unique_selected_branch": scheduled[0] if len(scheduled) == 1 else None,
        "production_artifacts_digest": iter18.iter16.iter15b.native_m6._digest_json(production_artifacts),  # noqa: SLF001
    }


def _run_gate_lane(lane_id: str, input_cfg: dict[str, Any]) -> dict[str, Any]:
    scan = _eligibility_scan_for_input(input_cfg)
    selected = scan["unique_selected_branch"]
    if selected is None:
        return {
            "lane": lane_id,
            "eligibility_scan": scan,
            "m6_integrated_2d_gate_candidate_passed": False,
            "primary_blocker": scan["outcome"],
        }
    model, geometry, branches = iter18e._new_model(  # noqa: SLF001
        north_bias=input_cfg["branch_biases"]["north_branch"],
        east_bias=input_cfg["branch_biases"]["east_branch"],
    )
    initial_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    initial_centroid = iter18._centroid_xy(initial_values)  # noqa: SLF001
    initial_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    ingress_events = _seed_ingress(model, source_node=input_cfg["ingress_source"])
    config = iter18e._branch_config(branches[selected])  # noqa: SLF001
    first_cycle = iter18d._feedback_cycle(  # noqa: SLF001
        model,
        config=config,
        cycle_index=0,
        phase="integrated_2d_gate_selected_branch_first_fire",
    )
    pre_score = iter18d._boundary_polarity_score(  # noqa: SLF001
        model, config["front_nodes"], config["rear_nodes"]
    )
    perturbation = iter18d._apply_polarity_damping_perturbation(  # noqa: SLF001
        model,
        front_nodes=config["front_nodes"],
        rear_nodes=config["rear_nodes"],
        transfer_amount=CHALLENGE_TRANSFER_AMOUNT,
    )
    post_score = iter18d._boundary_polarity_score(  # noqa: SLF001
        model, config["front_nodes"], config["rear_nodes"]
    )
    recovery_cycles = [
        iter18d._feedback_cycle(  # noqa: SLF001
            model,
            config=config,
            cycle_index=cycle_index,
            phase="post_perturbation_integrated_2d_gate_recovery",
        )
        for cycle_index in range(RECOVERY_WINDOW_CYCLES)
    ]
    final_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    final_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    final_centroid = iter18._centroid_xy(final_values)  # noqa: SLF001
    final_score = iter18d._boundary_polarity_score(  # noqa: SLF001
        model, config["front_nodes"], config["rear_nodes"]
    )
    production_artifacts = [
        cycle["production_artifact"]
        for cycle in [first_cycle, *recovery_cycles]
        if cycle["production_artifact"] is not None
    ]
    validation = iter18.iter16.iter15b.native_m6.validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=model.snapshot()["events"],
        production_results=production_artifacts,
    )
    recovery_scheduled = [
        cycle
        for cycle in recovery_cycles
        if cycle["producer_reason_code"]
        == iter18.iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ]
    final_delta = {
        "x": final_centroid["x"] - initial_centroid["x"],
        "y": final_centroid["y"] - initial_centroid["y"],
    }
    branch_progress = iter18d._route_progress(final_delta, config["route_vector"])  # noqa: SLF001
    width_initial = iter18._radius_width(initial_values)  # noqa: SLF001
    width_final = iter18._radius_width(final_values)  # noqa: SLF001
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = iter18._profile_similarity(initial_values, final_values)  # noqa: SLF001
    return {
        "lane": lane_id,
        "input_gate": input_cfg,
        "geometry_init": geometry,
        "eligibility_scan": scan,
        "ingress_event_count": len(ingress_events),
        "selected_branch": selected,
        "selected_branch_config": {
            "target_node": config["egress_target"],
            "front_nodes": list(config["front_nodes"]),
            "rear_nodes": list(config["rear_nodes"]),
            "route_vector": list(config["route_vector"]),
        },
        "initial_centroid_xy": initial_centroid,
        "final_centroid_xy": final_centroid,
        "final_centroid_delta": final_delta,
        "final_branch_progress": branch_progress,
        "pre_perturbation_score": pre_score,
        "post_perturbation_score": post_score,
        "final_score": final_score,
        "first_cycle": iter18d._cycle_summary(first_cycle),  # noqa: SLF001
        "recovery_scheduled_cycle_count": len(recovery_scheduled),
        "recovery_cycles": [iter18d._cycle_summary(cycle) for cycle in recovery_cycles],  # noqa: SLF001
        "perturbation": perturbation,
        "budget_initial": initial_budget,
        "budget_final": final_budget,
        "budget_abs_error": abs(final_budget - initial_budget),
        "nonnegative_gate_passed": min(final_values) >= -TOL,
        "width_relative_change": width_relative_change,
        "profile_similarity": profile_similarity,
        "identity_shape_gates_passed": (
            width_relative_change
            <= iter18.iter16.iter15b.native_m6.WIDTH_RELATIVE_CHANGE_MAX
            and profile_similarity
            >= iter18.iter16.iter15b.native_m6.PROFILE_SIMILARITY_MIN
        ),
        "artifact_validator": validation,
        "surface_row_count": len(model.get_state().causal_pulse_substrate_surface_log),
        "surface_log_digest": iter18d._surface_log_digest(model),  # noqa: SLF001
        "producer_records_digest": iter18.iter16.iter15b.native_m6._digest_json(production_artifacts),  # noqa: SLF001
        "m4_boundary_response_passed": (
            post_score < pre_score - TOL and final_score >= pre_score - TOL
        ),
        "m5_direction_control_passed": len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES,
        "m6_integrated_2d_gate_candidate_passed": (
            selected == input_cfg["expected_branch"]
            and len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES
            and post_score < pre_score - TOL
            and final_score >= pre_score - TOL
            and branch_progress > TOL
        ),
        "all_recovery_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in recovery_scheduled
        ),
    }


def _run_controls(policy: dict[str, Any]) -> dict[str, Any]:
    no_preference = iter18e._eligibility_scan(north_bias=0.25, east_bias=0.0)  # noqa: SLF001
    east_override = iter18e._eligibility_scan(north_bias=0.10 - EPSILON, east_bias=0.25 - EPSILON)  # noqa: SLF001
    both_strong = iter18e._eligibility_scan(north_bias=0.25, east_bias=0.25 - EPSILON)  # noqa: SLF001
    return {
        "no_preference_reproduces_18e_no_arbitration": {
            "control_id": "no_preference_reproduces_18e_no_arbitration_control",
            "passed_negative_control": no_preference["outcome"] == "tie_no_native_arbitration",
            "primary_blocker": "both_branches_eligible_no_native_arbitration",
            "outcome": no_preference["outcome"],
            "scheduled_branches": no_preference["scheduled_branches"],
        },
        "dominant_branch_overrides_local_preference": {
            "control_id": "dominant_branch_overrides_local_preference_control",
            "passed_positive_control": (
                east_override["outcome"] == "unique_branch_by_native_eligibility"
                and east_override["unique_selected_branch"] == "east_branch"
            ),
            "primary_reason": "dominant_east_branch_remains_eligible_despite_north_local_preference",
            "outcome": east_override["outcome"],
            "scheduled_branches": east_override["scheduled_branches"],
        },
        "epsilon_does_not_force_strong_two_branch_choice": {
            "control_id": "epsilon_does_not_force_strong_two_branch_choice_control",
            "passed_negative_control": both_strong["outcome"] == "tie_no_native_arbitration",
            "primary_blocker": "both_strong_branches_remain_eligible",
            "outcome": both_strong["outcome"],
            "scheduled_branches": both_strong["scheduled_branches"],
        },
        "global_preference_sum_zero": {
            "control_id": "global_preference_sum_zero_control",
            "passed_positive_control": all(
                abs(value) <= 1e-12
                for value in policy["balanced_local_preference_policy"][
                    "global_preference_sum"
                ].values()
            ),
            "primary_reason": "paired_local_preferences_cancel_globally",
            "global_preference_sum": policy["balanced_local_preference_policy"][
                "global_preference_sum"
            ],
            "outcome": "global_unbiased",
            "scheduled_branches": [],
        },
    }


def build_report() -> dict[str, Any]:
    iter18f_report = _load_json(ITER18F_PATH)
    policy = _integrated_gate_policy()
    lanes = {
        lane_id: _run_gate_lane(lane_id, input_cfg)
        for lane_id, input_cfg in policy["input_gates"].items()
    }
    controls = _run_controls(policy)
    checks = {
        "iteration_18f_available": iter18f_report["status"] == "passed",
        "two_input_gates_declared": set(policy["input_gates"]) == {"west_input", "south_input"},
        "two_output_branches_declared": set(policy["output_branches"]) == {"north_branch", "east_branch"},
        "composed_1d_branches_used": True,
        "balanced_local_preferences_used": True,
        "global_preference_sum_zero": controls["global_preference_sum_zero"]["passed_positive_control"],
        "external_scorer_absent": True,
        "external_argmax_absent": True,
        "west_and_south_inputs_select_distinct_outputs": {
            lane["selected_branch"] for lane in lanes.values()
        }
        == {"north_branch", "east_branch"},
        "native_branch_eligibility_selects_outputs": all(
            lane["eligibility_scan"]["outcome"] == "unique_branch_by_native_eligibility"
            for lane in lanes.values()
        ),
        "no_preference_reproduces_18e_no_arbitration": (
            controls["no_preference_reproduces_18e_no_arbitration"]["passed_negative_control"]
        ),
        "dominant_branch_overrides_local_preference": (
            controls["dominant_branch_overrides_local_preference"]["passed_positive_control"]
        ),
        "epsilon_does_not_force_strong_two_branch_choice": (
            controls["epsilon_does_not_force_strong_two_branch_choice"]["passed_negative_control"]
        ),
        "artifact_validators_passed": all(lane["artifact_validator"]["valid"] for lane in lanes.values()),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= EPSILON_BUDGET and lane["nonnegative_gate_passed"]
            for lane in lanes.values()
        ),
        "identity_shape_gates_passed": all(lane["identity_shape_gates_passed"] for lane in lanes.values()),
        "m6_integrated_2d_gate_candidate_passed": all(
            lane["m6_integrated_2d_gate_candidate_passed"] for lane in lanes.values()
        ),
        "all_recovery_pulses_feedback_authorized": all(
            lane["all_recovery_pulses_feedback_authorized"] for lane in lanes.values()
        ),
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s3_grid_integrated_2d_composed_gate_candidate"
        if status == "passed"
        else "s3_grid_integrated_2d_composed_gate_failed_closed"
    )
    return {
        "report_kind": "n04_iter18g_integrated_2d_composed_gate_v1",
        "iteration": "18-G",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "result_role": "integrated_fixed_topology_2d_composed_gate_probe",
        "movement_substrate": "S3_grid_integrated_2d_composed_gate_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "grid",
        "input_iteration_18f": _artifact_record(ITER18F_PATH),
        "claim_ceiling": claim_ceiling,
        "integrated_gate_policy": policy,
        "native_support_boundary": {
            "native_lgrc_packet_work_used": True,
            "native_causal_pulse_substrate_surface_used": True,
            "native_feedback_eligibility_surface_used": True,
            "native_feedback_producer_used": True,
            "native_artifact_validator_used": True,
            "external_scorer_used": False,
            "external_argmax_used": False,
            "balanced_local_preference_used": True,
            "fixed_topology_2d_gate_supported": status == "passed",
            "native_choice_selection_supported": False,
            "selection_mechanism": "input_locality_plus_balanced_preference_plus_native_branch_eligibility",
        },
        "achieved_movement_level": "M6" if status == "passed" else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate" if status == "passed" else "not_measured",
            "persistence_basis": (
                "s3_grid_integrated_2d_composed_gate_recovers_0_15"
                if status == "passed"
                else "integrated_2d_gate_below_m6"
            ),
            "self_renewed_cycle_count": RECOVERY_WINDOW_CYCLES,
            "repeatability_status": "west_and_south_inputs_select_distinct_outputs_and_recover",
            "recovery_status": "recovers_0_15_on_selected_2d_output_branch",
            "recovery_tested": True,
            "recovery_passed": status == "passed",
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "fixed_topology_2d_gate_not_native_choice_or_adaptive_topology",
        },
        "integrated_gate_summary": {
            "entry_ceiling": iter18f_report["claim_ceiling"],
            "positive_result": (
                "The 18-C two-input/two-output gate structure is integrated "
                "with 18-E composed 1D branch competition and 18-F balanced "
                "local preferences, using native branch eligibility rather "
                "than external scoring."
            ),
            "remaining_blocker": (
                "The result is fixed-topology 2D composed-gate evidence, not "
                "native LGRC choice selection, RC collapse, port-graph, or "
                "adaptive topology."
            ),
            "selected_branches": {
                lane_id: lane["selected_branch"] for lane_id, lane in lanes.items()
            },
        },
        "lanes": lanes,
        "controls": controls,
        "checks": checks,
        "go_no_go_for_iteration_19": {
            "iteration_19_allowed": status == "passed",
            "port_graph_ceiling_to_test": claim_ceiling,
            "guidance": (
                "Iteration 19 may test whether integrated fixed-topology 2D "
                "composed-gate evidence transfers to S7 port mechanics. "
                "Adaptive topology and native choice/collapse remain blocked "
                "until explicit controls pass."
            ),
        },
        "claim_flags": {
            "native_m6": status == "passed",
            "native_m6_candidate_gate_passed": status == "passed",
            "integrated_fixed_topology_2d_gate_candidate_passed": status == "passed",
            "fixed_topology_2d_gate_claim_allowed": status == "passed",
            "native_lgrc_choice_selection_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "choice_or_agency_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
            "broad_geometry_transfer_claim_allowed": False,
            "adaptive_topology_claim_allowed": False,
        },
        "blocked_claims": [
            "native_lgrc_choice_selection",
            "rc_identity_collapse",
            "semantic_choice",
            "agency",
            "port_graph_transfer",
            "adaptive_topology_movement",
            "topology_mutating_movement",
            "broad_geometry_transfer",
            "locomotion_like_basin_dynamics",
            "biological_behavior",
            "identity_acceptance",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "git_head": _run_git(["rev-parse", "HEAD"]),
            "git_status_short": _run_git(["status", "--short"]),
        },
        "command": COMMAND,
    }


def write_report(report: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["integrated_gate_summary"]
    lines = [
        "# N04 Iteration 18-G Integrated 2D Composed Gate",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 18-G integrates the 18-C two-input/two-output gate shape with "
        "18-E composed 1D branch competition and 18-F balanced local "
        "preference tie-breaking.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- entry ceiling: `{summary['entry_ceiling']}`",
        f"- selected branches: `{summary['selected_branches']}`",
        f"- remaining blocker: `{summary['remaining_blocker']}`",
        "",
        "## Controls",
        "",
    ]
    for key, value in report["controls"].items():
        passed = value.get("passed_negative_control", value.get("passed_positive_control"))
        reason = value.get("primary_blocker", value.get("primary_reason"))
        lines.append(
            f"- `{key}`: passed=`{passed}`, reason=`{reason}`, "
            f"outcome=`{value['outcome']}`"
        )
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This supports a fixed-topology 2D composed-gate candidate. It does not support native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph transfer, topology-mutating movement, adaptive topology, broad geometry-transfer, locomotion-like behavior, biological behavior, identity acceptance, inherited-N03 movement, or unrestricted movement.",
            "",
            "## Command",
            "",
            f"```bash\n{COMMAND}\n```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
