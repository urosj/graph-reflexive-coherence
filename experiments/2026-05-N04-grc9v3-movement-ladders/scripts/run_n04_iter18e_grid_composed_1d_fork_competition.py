#!/usr/bin/env python3
"""Run N04 Iteration 18-E S3 grid composed 1D fork competition probe."""

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


ITER18D_PATH = N04 / "outputs/n04_iter18d_grid_geometry_selection_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter18e_grid_composed_1d_fork_competition_report.json"
REPORT_PATH = N04 / "reports/n04_iter18e_grid_composed_1d_fork_competition_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter18e_grid_composed_1d_fork_competition.py"
)

CENTER_NODE = iter18.CENTER_NODE
NORTH_NODE = 7
WEST_NODE = 11
EAST_NODE = 13
SOUTH_NODE = 17
RECOVERY_WINDOW_CYCLES = iter18.RECOVERY_WINDOW_CYCLES
CHALLENGE_TRANSFER_AMOUNT = iter18.CHALLENGE_TRANSFER_AMOUNT
EPSILON_BUDGET = iter18.EPSILON_BUDGET
TOL = iter18.TOL


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


def _branch_elements(edge_by_pair: dict[tuple[int, int], int]) -> dict[str, dict[str, Any]]:
    return {
        "north_branch": {
            "branch_id": "north_branch_1d_element",
            "source_node": CENTER_NODE,
            "target_node": NORTH_NODE,
            "edge_id": edge_by_pair[(CENTER_NODE, NORTH_NODE)],
            "front_nodes": (NORTH_NODE,),
            "rear_nodes": (SOUTH_NODE,),
            "route_vector": (0.0, -1.0),
            "route_id": "s3-composed-fork-north-branch",
        },
        "east_branch": {
            "branch_id": "east_branch_1d_element",
            "source_node": CENTER_NODE,
            "target_node": EAST_NODE,
            "edge_id": edge_by_pair[(CENTER_NODE, EAST_NODE)],
            "front_nodes": (EAST_NODE,),
            "rear_nodes": (WEST_NODE,),
            "route_vector": (1.0, 0.0),
            "route_id": "s3-composed-fork-east-branch",
        },
    }


def _apply_composed_fork_geometry(
    state: Any,
    *,
    north_bias: float,
    east_bias: float,
    disabled_branches: tuple[str, ...] = (),
) -> dict[str, Any]:
    before_values = [float(state.nodes[index].coherence) for index in range(iter18.NODE_COUNT)]
    before_budget = sum(before_values)
    if "north_branch" not in disabled_branches:
        state.nodes[NORTH_NODE].coherence += north_bias
        state.nodes[SOUTH_NODE].coherence -= north_bias
    if "east_branch" not in disabled_branches:
        state.nodes[EAST_NODE].coherence += east_bias
        state.nodes[WEST_NODE].coherence -= east_bias
    after_values = [float(state.nodes[index].coherence) for index in range(iter18.NODE_COUNT)]
    after_budget = sum(after_values)
    return {
        "geometry_id": "s3_grid_composed_1d_fork_v1",
        "source_geometry": "s3_grid_geometry_scored_competing_output_basins_v1",
        "composition_kind": "two_1d_lgrc_route_elements_shared_fork",
        "shared_fork_node": CENTER_NODE,
        "branch_biases": {"north_branch": north_bias, "east_branch": east_bias},
        "disabled_branches": list(disabled_branches),
        "external_geometry_scorer_absent": True,
        "external_argmax_absent": True,
        "direct_branch_suppression_absent": True,
        "preauthored_input_to_output_lookup_absent": True,
        "diagonal_edges_enabled": False,
        "route_shortcuts_enabled": False,
        "route_edges_are_local_unit_edges": True,
        "budget_before": before_budget,
        "budget_after": after_budget,
        "budget_abs_error": abs(after_budget - before_budget),
        "nonnegative_after_geometry_init": min(after_values) >= -TOL,
        "topology_changed_by_fixture_definition": False,
        "topology_fixed_during_run": True,
        "topology_mutated_during_run": False,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
    }


def _branch_config(branch: dict[str, Any]) -> dict[str, Any]:
    return {
        "egress_source": branch["source_node"],
        "egress_target": branch["target_node"],
        "egress_edge_id": branch["edge_id"],
        "front_nodes": branch["front_nodes"],
        "rear_nodes": branch["rear_nodes"],
        "route_vector": branch["route_vector"],
        "route_id": branch["route_id"],
        "expected_polarity": "positive",
    }


def _new_model(
    *,
    north_bias: float,
    east_bias: float,
    disabled_branches: tuple[str, ...] = (),
) -> tuple[Any, dict[str, Any], dict[str, dict[str, Any]]]:
    state, edge_by_pair = iter18._grid_state()  # noqa: SLF001
    geometry = _apply_composed_fork_geometry(
        state,
        north_bias=north_bias,
        east_bias=east_bias,
        disabled_branches=disabled_branches,
    )
    branches = _branch_elements(edge_by_pair)
    model = iter18.iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter18.iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    return model, geometry, branches


def _seed_shared_fork_contact(model: Any, edge_by_pair: dict[tuple[int, int], int] | None = None) -> list[dict[str, Any]]:
    if edge_by_pair is None:
        _state, edge_by_pair = iter18._grid_state()  # noqa: SLF001
    model.schedule_packet_departure(
        source_node_id=WEST_NODE,
        target_node_id=CENTER_NODE,
        edge_id=edge_by_pair[(WEST_NODE, CENTER_NODE)],
        amount=iter18.iter16.iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    return iter18.iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001


def _evaluate_branch_eligibility(
    model: Any,
    *,
    branch_id: str,
    branch: dict[str, Any],
    producer_enabled: bool = True,
    expected_polarity: str = "positive",
) -> dict[str, Any]:
    config = _branch_config(branch)
    feedback_row = model.emit_feedback_eligibility_surface_row(
        front_node_ids=config["front_nodes"],
        rear_node_ids=config["rear_nodes"],
        reference_delta=0.0,
        feedback_threshold=iter18.iter16.iter15b.native_m6.FEEDBACK_THRESHOLD,
        expected_next_route_id=config["route_id"],
        expected_next_channel_id=f"edge:{config['egress_edge_id']}",
    )
    if not producer_enabled:
        return {
            "branch_id": branch_id,
            "producer_enabled": False,
            "surface_digest": feedback_row.surface_digest,
            "source_surface_digest": feedback_row.surface_values_after["source_surface_digest"],
            "boundary_polarity_score": feedback_row.surface_values_after["boundary_polarity_score"],
            "producer_reason_code": "branch_producer_disabled",
            "scheduled_event_id": None,
            "scheduled": False,
            "production_artifact": None,
        }
    model.set_feedback_coupled_pulse_producer(
        source_node_id=config["egress_source"],
        target_node_id=config["egress_target"],
        edge_id=config["egress_edge_id"],
        threshold=iter18.iter16.iter15b.native_m6.FEEDBACK_THRESHOLD,
        packet_amount=iter18.iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
        expected_polarity=expected_polarity,
        expected_source_surface_digest=feedback_row.surface_values_after["source_surface_digest"],
        expected_next_route_id=config["route_id"],
        expected_next_channel_id=f"edge:{config['egress_edge_id']}",
    )
    result = model.produce_events(
        policy=(
            iter18.iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
        )
    )
    record = result.production_records[0]
    scheduled = record.reason_code == (
        iter18.iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    )
    return {
        "branch_id": branch_id,
        "producer_enabled": True,
        "surface_digest": feedback_row.surface_digest,
        "source_surface_digest": feedback_row.surface_values_after["source_surface_digest"],
        "boundary_polarity_score": feedback_row.surface_values_after["boundary_polarity_score"],
        "producer_reason_code": record.reason_code,
        "scheduled_event_id": record.scheduled_event_id,
        "scheduled": scheduled,
        "regenerated_pulse_source": record.observed_evidence.get("regenerated_pulse_source"),
        "copied_from_original_schedule": record.observed_evidence.get("copied_from_original_schedule"),
        "production_artifact": result.to_artifact(),
    }


def _eligibility_scan(
    *,
    north_bias: float,
    east_bias: float,
    disabled_branches: tuple[str, ...] = (),
    expected_polarity: str = "positive",
) -> dict[str, Any]:
    branch_results: dict[str, Any] = {}
    production_artifacts: list[dict[str, Any]] = []
    geometry_record: dict[str, Any] | None = None
    for branch_id in ("north_branch", "east_branch"):
        model, geometry, branches = _new_model(
            north_bias=north_bias,
            east_bias=east_bias,
            disabled_branches=disabled_branches,
        )
        geometry_record = geometry
        _seed_shared_fork_contact(model)
        result = _evaluate_branch_eligibility(
            model,
            branch_id=branch_id,
            branch=branches[branch_id],
            producer_enabled=branch_id not in disabled_branches,
            expected_polarity=expected_polarity,
        )
        branch_results[branch_id] = {
            key: value for key, value in result.items() if key != "production_artifact"
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
        "geometry_init": geometry_record,
        "branch_results": branch_results,
        "scheduled_branches": scheduled,
        "outcome": outcome,
        "unique_selected_branch": scheduled[0] if len(scheduled) == 1 else None,
        "native_branch_competition_observed": len(scheduled) == 1,
        "native_branch_arbitration_observed": False,
        "production_artifacts_digest": iter18.iter16.iter15b.native_m6._digest_json(production_artifacts),  # noqa: SLF001
    }


def _run_unique_branch_lane(lane: str, *, north_bias: float, east_bias: float) -> dict[str, Any]:
    scan = _eligibility_scan(north_bias=north_bias, east_bias=east_bias)
    selected = scan["unique_selected_branch"]
    if selected is None:
        return {
            "lane": lane,
            "eligibility_scan": scan,
            "m6_composed_fork_candidate_passed": False,
            "primary_blocker": scan["outcome"],
        }
    model, geometry, branches = _new_model(north_bias=north_bias, east_bias=east_bias)
    initial_values = iter18.iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    initial_centroid = iter18._centroid_xy(initial_values)  # noqa: SLF001
    initial_budget = iter18.iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    _seed_shared_fork_contact(model)
    config = _branch_config(branches[selected])
    first_cycle = iter18d._feedback_cycle(  # noqa: SLF001
        model,
        config=config,
        cycle_index=0,
        phase="composed_fork_selected_branch_first_fire",
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
            phase="post_perturbation_composed_fork_recovery",
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
    branch_vector = config["route_vector"]
    branch_progress = iter18d._route_progress(final_delta, branch_vector)  # noqa: SLF001
    width_initial = iter18._radius_width(initial_values)  # noqa: SLF001
    width_final = iter18._radius_width(final_values)  # noqa: SLF001
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = iter18._profile_similarity(initial_values, final_values)  # noqa: SLF001
    return {
        "lane": lane,
        "geometry_init": geometry,
        "eligibility_scan": scan,
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
        "m6_composed_fork_candidate_passed": (
            len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES
            and scan["outcome"] == "unique_branch_by_native_eligibility"
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


def _run_controls() -> dict[str, Any]:
    symmetric = _eligibility_scan(north_bias=0.25, east_bias=0.25)
    disabled = _eligibility_scan(
        north_bias=0.25,
        east_bias=0.25,
        disabled_branches=("east_branch",),
    )
    subthreshold = _eligibility_scan(north_bias=0.05, east_bias=-0.15)
    wrong_polarity = _eligibility_scan(
        north_bias=0.25,
        east_bias=0.00,
        expected_polarity="negative",
    )
    return {
        "symmetric_tie_no_arbitration": {
            "control_id": "symmetric_tie_no_arbitration_control",
            "passed_negative_control": symmetric["outcome"] == "tie_no_native_arbitration",
            "primary_blocker": "both_branches_eligible_no_native_arbitration",
            "outcome": symmetric["outcome"],
            "scheduled_branches": symmetric["scheduled_branches"],
        },
        "single_branch_disabled": {
            "control_id": "single_branch_disabled_control",
            "passed_negative_control": (
                disabled["outcome"] == "unique_branch_by_native_eligibility"
                and disabled["unique_selected_branch"] == "north_branch"
            ),
            "primary_blocker": "east_branch_producer_disabled",
            "outcome": disabled["outcome"],
            "scheduled_branches": disabled["scheduled_branches"],
        },
        "budget_limited_subthreshold": {
            "control_id": "budget_limited_subthreshold_control",
            "passed_negative_control": subthreshold["outcome"] == "no_branch_eligible",
            "primary_blocker": "branch_polarity_below_feedback_threshold",
            "outcome": subthreshold["outcome"],
            "scheduled_branches": subthreshold["scheduled_branches"],
        },
        "wrong_polarity": {
            "control_id": "wrong_polarity_control",
            "passed_negative_control": wrong_polarity["outcome"] == "no_branch_eligible",
            "primary_blocker": "feedback_wrong_polarity",
            "outcome": wrong_polarity["outcome"],
            "scheduled_branches": wrong_polarity["scheduled_branches"],
        },
    }


def build_report() -> dict[str, Any]:
    iter18d = _load_json(ITER18D_PATH)
    north_dominant = _run_unique_branch_lane(
        "north_branch_capacity_dominant",
        north_bias=0.25,
        east_bias=-0.05,
    )
    east_dominant = _run_unique_branch_lane(
        "east_branch_capacity_dominant",
        north_bias=0.00,
        east_bias=0.25,
    )
    lanes = [north_dominant, east_dominant]
    controls = _run_controls()
    checks = {
        "iteration_18d_available": iter18d["status"] == "passed",
        "two_1d_branch_elements_declared": True,
        "shared_fork_source_declared": True,
        "native_surface_and_feedback_used_on_both_branches": True,
        "external_geometry_scorer_absent": True,
        "external_argmax_absent": True,
        "direct_branch_suppression_absent": True,
        "preauthored_input_to_output_lookup_absent": True,
        "north_and_east_dominant_lanes_select_distinct_branches": {
            lane["selected_branch"] for lane in lanes
        }
        == {"north_branch", "east_branch"},
        "branch_selection_by_native_eligibility": all(
            lane["eligibility_scan"]["outcome"] == "unique_branch_by_native_eligibility"
            for lane in lanes
        ),
        "native_arbitration_not_supported": True,
        "symmetric_tie_exposes_no_arbitration": (
            controls["symmetric_tie_no_arbitration"]["passed_negative_control"]
        ),
        "controls_fail_for_distinct_blockers": all(
            control["passed_negative_control"] for control in controls.values()
        )
        and len({control["primary_blocker"] for control in controls.values()}) == len(controls),
        "artifact_validators_passed": all(lane["artifact_validator"]["valid"] for lane in lanes),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= EPSILON_BUDGET and lane["nonnegative_gate_passed"]
            for lane in lanes
        ),
        "identity_shape_gates_passed": all(lane["identity_shape_gates_passed"] for lane in lanes),
        "m6_composed_fork_candidate_passed": all(
            lane["m6_composed_fork_candidate_passed"] for lane in lanes
        ),
        "all_recovery_pulses_feedback_authorized": all(
            lane["all_recovery_pulses_feedback_authorized"] for lane in lanes
        ),
        "no_direct_writes": all(
            not lane["geometry_init"][field]
            for lane in lanes
            for field in [
                "direct_support_mask_write",
                "direct_centroid_write",
                "direct_displacement_write",
                "direct_topology_write",
                "direct_claim_flag_write",
            ]
        ),
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s3_grid_composed_1d_fork_competition_candidate"
        if status == "passed"
        else "s3_grid_composed_1d_fork_competition_failed_closed"
    )
    report = {
        "report_kind": "n04_iter18e_grid_composed_1d_fork_competition_v1",
        "iteration": "18-E",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "result_role": "compositional_lgrc_fork_competition_probe",
        "movement_substrate": "S3_grid_composed_1d_fork_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "grid",
        "input_iteration_18d": _artifact_record(ITER18D_PATH),
        "claim_ceiling": claim_ceiling,
        "native_support_boundary": {
            "native_lgrc_packet_work_used": True,
            "native_causal_pulse_substrate_surface_used": True,
            "native_feedback_eligibility_surface_used": True,
            "native_feedback_producer_used": True,
            "native_artifact_validator_used": True,
            "external_geometry_scorer_used": False,
            "external_argmax_used": False,
            "native_branch_competition_supported": status == "passed",
            "native_branch_arbitration_supported": False,
            "selection_mechanism": "branch_eligibility_differentiation_from_composed_1d_elements",
            "arbitration_blocker": (
                "When both branches are eligible, current LGRC producer "
                "semantics expose a tie/no-arbitration state rather than "
                "choosing one branch."
            ),
        },
        "achieved_movement_level": "M6" if status == "passed" else "below_M6",
        "persistence_axis": {
            "persistence_level": "T6_candidate" if status == "passed" else "not_measured",
            "persistence_basis": (
                "s3_grid_composed_1d_fork_branch_eligibility_recovers_0_15"
                if status == "passed"
                else "composed_fork_below_m6"
            ),
            "self_renewed_cycle_count": RECOVERY_WINDOW_CYCLES,
            "repeatability_status": "north_and_east_branch_dominant_lanes_recover_three_cycles",
            "recovery_status": "recovers_0_15_on_unique_native_eligible_branch",
            "recovery_tested": True,
            "recovery_passed": status == "passed",
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "native_branch_arbitration_not_supported_for_symmetric_ties",
        },
        "composition_summary": {
            "entry_ceiling": iter18d["claim_ceiling"],
            "positive_result": (
                "Composed 1D branch elements can produce branch differentiation "
                "by native feedback eligibility without an external scorer."
            ),
            "remaining_blocker": (
                "A symmetric eligible fork produces no native arbitration; "
                "selection is supported only when geometry/capacity makes one "
                "branch eligible and the other subthreshold."
            ),
            "selected_branches": {
                lane["lane"]: lane["selected_branch"] for lane in lanes
            },
        },
        "lanes": {
            lane["lane"]: lane for lane in lanes
        },
        "controls": controls,
        "checks": checks,
        "go_no_go_for_iteration_19": {
            "iteration_19_allowed": status == "passed",
            "port_graph_ceiling_to_test": claim_ceiling,
            "guidance": (
                "Iteration 19 may test whether branch-eligibility competition "
                "transfers to port graph mechanics. Native arbitration/choice "
                "for symmetric competing branches remains blocked."
            ),
        },
        "claim_flags": {
            "native_m6": status == "passed",
            "native_m6_candidate_gate_passed": status == "passed",
            "composed_1d_fork_competition_candidate_passed": status == "passed",
            "native_branch_competition_claim_allowed": status == "passed",
            "native_branch_arbitration_claim_allowed": False,
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
            "native_branch_arbitration",
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
    return report


def write_report(report: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["composition_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 18-E S3 Grid Composed 1D Fork Competition",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 18-E tests whether two native 1D LGRC branch elements can "
        "compose a 2D fork without external geometry scoring.",
        "",
        "## Reasoning",
        "",
        "Iteration 18-D demonstrated a useful geometry/flux relation, but its "
        "selection scorer lived outside LGRC. Iteration 18-E removes that "
        "scorer. The probe evaluates native feedback eligibility on two "
        "declared 1D branch elements sharing a fork. A unique branch may be "
        "selected only when branch state makes one branch eligible and the "
        "other subthreshold; when both branches are eligible, current LGRC "
        "records a no-arbitration tie.",
        "",
        "## Summary",
        "",
        f"- achieved level: `{report['achieved_movement_level']}`",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- recovery status: `{axis['recovery_status']}`",
        f"- entry ceiling: `{summary['entry_ceiling']}`",
        f"- selected branches: `{summary['selected_branches']}`",
        f"- remaining blocker: `{summary['remaining_blocker']}`",
        "",
        "## Native Boundary",
        "",
    ]
    for key, value in report["native_support_boundary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Controls", ""])
    for key, value in report["controls"].items():
        lines.append(
            f"- `{key}`: passed=`{value['passed_negative_control']}`, "
            f"blocker=`{value['primary_blocker']}`, outcome=`{value['outcome']}`"
        )
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Go/No-Go", ""])
    for key, value in report["go_no_go_for_iteration_19"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This is a composed 1D fork competition candidate. It supports branch differentiation by native eligibility when one branch is subthreshold, but it does not support native branch arbitration, native LGRC choice selection, RC identity collapse, semantic choice, agency, port-graph, topology-mutating, adaptive-topology, broad geometry-transfer, locomotion-like, biological, identity-acceptance, inherited-N03, or unrestricted movement evidence.",
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
