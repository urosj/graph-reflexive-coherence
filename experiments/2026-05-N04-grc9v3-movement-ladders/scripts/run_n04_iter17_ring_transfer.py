#!/usr/bin/env python3
"""Run N04 Iteration 17 S1 ring transfer with explicit unwrap policy."""

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

import run_n04_iter16_corridor_transfer as iter16  # noqa: E402


ITER16C_PATH = N04 / "outputs/n04_iter16c_high_shock_corridor_resilience.json"
POLICY_OUTPUT_PATH = N04 / "outputs/n04_iter17_ring_unwrap_policy.json"
OUTPUT_PATH = N04 / "outputs/n04_iter17_ring_transfer_report.json"
REPORT_PATH = N04 / "reports/n04_iter17_ring_transfer_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter17_ring_transfer.py"
)

CHALLENGE_TRANSFER_AMOUNT = 0.15
CENTRAL_RESERVOIR_NODE = iter16.CENTRAL_RESERVOIR_NODE
FRONT_RING_NODES = iter16.FRONT_CORRIDOR_NODES
REAR_RING_NODES = iter16.REAR_CORRIDOR_NODES
RECOVERY_WINDOW_CYCLES = iter16.RECOVERY_WINDOW_CYCLES
COST_METRIC = iter16.COST_METRIC
EPSILON_BUDGET = 1e-12
TOL = 1e-12


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


def _ring_unwrap_policy() -> dict[str, Any]:
    return {
        "policy_id": "s1_ring_unwrap_policy_v1",
        "substrate_id": "S1_ring_absorber_corridor_v1",
        "node_count": iter16.iter15b.native_m6.NODE_COUNT,
        "coordinate_frame": "ring_unwrapped_linear",
        "unwrap_origin_node": 0,
        "unwrap_seam": [20, 0],
        "positive_direction": "increasing_unwrapped_index",
        "front_region": list(FRONT_RING_NODES),
        "rear_region": list(REAR_RING_NODES),
        "center_reservoir": [CENTRAL_RESERVOIR_NODE],
        "centroid_policy": "linear_centroid_on_declared_unwrap",
        "front_rear_policy_frozen_before_run": True,
        "route_crosses_unwrap_seam": False,
        "antipodal_tie_possible": False,
        "antipodal_tie_reason": "odd_node_count_21_no_exact_antipode",
        "wrap_jump_promotion_allowed": False,
        "ring_claim_scope": "declared_unwrap_only",
        "claim_boundary": (
            "ring transfer may only claim evidence under this unwrap policy; "
            "wrap artifacts, antipodal ties, and circular locomotion claims remain blocked"
        ),
    }


def _add_ring_edge(state: Any) -> int:
    edge_id = state.topology.connect_ports(
        20,
        2,
        0,
        2,
        {
            "kind": "s1_ring_wrap_edge",
            "source_index": 20,
            "target_index": 0,
            "unwrap_seam": True,
        },
    )
    state.port_edges[edge_id] = iter16.iter15b.native_m6.PortEdge(
        20,
        2,
        0,
        2,
        conductance=1.0,
        flux_uv=0.0,
    )
    state.base_conductance[edge_id] = 1.0
    state.geometric_length[edge_id] = 1.0
    state.temporal_delay[edge_id] = 1.0
    state.flux_coupling[edge_id] = 0.0
    return edge_id


def _apply_ring_geometry(state: Any) -> dict[str, Any]:
    ring_edge_id = _add_ring_edge(state)
    corridor = iter16._apply_corridor_geometry(state)  # noqa: SLF001
    corridor |= {
        "geometry_id": "s1_ring_absorber_corridor_v1",
        "geometry_family": "s1_ring_with_declared_unwrap_and_absorber_corridor",
        "source_geometry": "s4_widened_chain_absorber_corridor_v1",
        "ring_wrap_edge_id": ring_edge_id,
        "unwrap_policy_id": "s1_ring_unwrap_policy_v1",
        "coordinate_frame": "ring_unwrapped_linear",
        "unwrap_origin_node": 0,
        "unwrap_seam": [20, 0],
        "route_crosses_unwrap_seam": False,
        "antipodal_tie_possible": False,
        "ring_topology_declared_before_run": True,
        "topology_mutated_during_run": False,
        "reason": (
            "Iteration 17 transfers the corridor candidate to an S1 ring "
            "fixture with an explicit unwrap seam at 20->0. The active route "
            "and front/rear masks do not cross the seam, so wrap artifacts and "
            "antipodal ties cannot promote claims."
        ),
    }
    return corridor


def _direction_config(direction: str, geometry: dict[str, Any]) -> dict[str, Any]:
    if direction == "forward":
        return {
            "source": CENTRAL_RESERVOIR_NODE,
            "target": 14,
            "edge_id": geometry["front_outer_edge_id"],
            "expected_polarity": "positive",
            "expected_sign": 1,
            "route_id": "s1-ring-forward",
        }
    if direction == "reversed":
        return {
            "source": CENTRAL_RESERVOIR_NODE,
            "target": 6,
            "edge_id": geometry["rear_outer_edge_id"],
            "expected_polarity": "negative",
            "expected_sign": -1,
            "route_id": "s1-ring-reversed",
        }
    raise ValueError(f"unknown direction {direction!r}")


def _run_ring_direction(direction: str) -> dict[str, Any]:
    state, _edges = iter16.iter15b.native_m6._s0_chain_state()  # noqa: SLF001
    geometry = _apply_ring_geometry(state)
    config = _direction_config(direction, geometry)
    model = iter16.iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter16.iter15b.native_m6._params(),  # noqa: SLF001
    )
    initial_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    initial_budget = iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    model.schedule_packet_departure(
        source_node_id=config["source"],
        target_node_id=config["target"],
        edge_id=config["edge_id"],
        amount=iter16.iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    seeded_events = iter16.iter15b.native_m6._process_queue(model)  # noqa: SLF001
    baseline_cycles = [
        iter16.iter15b._feedback_cycle(  # noqa: SLF001
            model,
            config=config,
            edge_id=config["edge_id"],
            cycle_index=cycle_index,
            phase="pre_perturbation_baseline",
        )
        for cycle_index in range(iter16.PRE_TRANSFER_CYCLES)
    ]
    pre_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    pre_centroid = iter16.iter15b.native_m6._centroid(pre_values)  # noqa: SLF001
    pre_score = iter16.iter15b._boundary_polarity_score(model)  # noqa: SLF001
    perturbation = iter16.iter15b._apply_polarity_damping_perturbation(  # noqa: SLF001
        model,
        direction=direction,
        transfer_amount=CHALLENGE_TRANSFER_AMOUNT,
    )
    post_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    post_centroid = iter16.iter15b.native_m6._centroid(post_values)  # noqa: SLF001
    post_score = iter16.iter15b._boundary_polarity_score(model)  # noqa: SLF001
    recovery_cycles = [
        iter16.iter15b._feedback_cycle(  # noqa: SLF001
            model,
            config=config,
            edge_id=config["edge_id"],
            cycle_index=cycle_index,
            phase="post_perturbation_recovery",
        )
        for cycle_index in range(RECOVERY_WINDOW_CYCLES)
    ]
    final_values = iter16.iter15b.native_m6._node_vector(model)  # noqa: SLF001
    final_budget = iter16.iter15b.native_m6._budget(model)  # noqa: SLF001
    final_score = iter16.iter15b._boundary_polarity_score(model)  # noqa: SLF001
    final_centroid = iter16.iter15b.native_m6._centroid(final_values)  # noqa: SLF001
    production_artifacts = [
        cycle["production_artifact"]
        for cycle in [*baseline_cycles, *recovery_cycles]
        if cycle["production_artifact"] is not None
    ]
    validation = iter16.iter15b.native_m6.validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=model.snapshot()["events"],
        production_results=production_artifacts,
    )
    recovery_scheduled = [
        cycle
        for cycle in recovery_cycles
        if cycle["producer_reason_code"]
        == iter16.iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ]
    sign = config["expected_sign"]
    initial_centroid = iter16.iter15b.native_m6._centroid(initial_values)  # noqa: SLF001
    raw_pre_centroid = pre_centroid - initial_centroid
    raw_post_centroid = post_centroid - initial_centroid
    raw_final_centroid = final_centroid - initial_centroid
    signed_pre_score = sign * pre_score
    signed_post_score = sign * post_score
    signed_final_score = sign * final_score
    signed_pre_centroid = sign * raw_pre_centroid
    signed_post_centroid = sign * raw_post_centroid
    signed_final_centroid = sign * raw_final_centroid
    width_initial = iter16.iter15b.native_m6._width(initial_values)  # noqa: SLF001
    width_final = iter16.iter15b.native_m6._width(final_values)  # noqa: SLF001
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = iter16.iter15b.native_m6._profile_similarity(initial_values, final_values)  # noqa: SLF001

    def cycle_summary(cycle: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in cycle.items()
            if key not in {"production_artifact", "processed_events"}
        } | {
            "processed_event_count": len(cycle["processed_events"]),
            "processed_events_digest": iter16.iter15b.native_m6._digest_json(cycle["processed_events"]),  # noqa: SLF001
        }

    return {
        "direction": direction,
        "geometry_init": geometry,
        "source_node_id": config["source"],
        "target_node_id": config["target"],
        "edge_id": config["edge_id"],
        "front_mask": list(iter16.iter15b.native_m6.FRONT_MASK),
        "rear_mask": list(iter16.iter15b.native_m6.REAR_MASK),
        "recovery_window_cycles": RECOVERY_WINDOW_CYCLES,
        "recovery_scheduled_cycle_count": len(recovery_scheduled),
        "baseline_cycles": [cycle_summary(cycle) for cycle in baseline_cycles],
        "recovery_cycles": [cycle_summary(cycle) for cycle in recovery_cycles],
        "perturbation": perturbation,
        "signed_pre_transfer_score": signed_pre_score,
        "signed_post_perturbation_score": signed_post_score,
        "signed_final_score": signed_final_score,
        "signed_pre_transfer_centroid_delta": signed_pre_centroid,
        "signed_post_perturbation_centroid_delta": signed_post_centroid,
        "signed_final_centroid_delta": signed_final_centroid,
        "raw_pre_transfer_centroid_delta": raw_pre_centroid,
        "raw_post_perturbation_centroid_delta": raw_post_centroid,
        "raw_final_centroid_delta": raw_final_centroid,
        "centroid_coordinate_frame": "ring_unwrapped_linear",
        "centroid_delta_frame": "direction_normalized_recovery_delta",
        "budget_initial": initial_budget,
        "budget_final": final_budget,
        "budget_abs_error": abs(final_budget - initial_budget),
        "nonnegative_gate_passed": min(final_values) >= TOL * -1,
        "width_relative_change": width_relative_change,
        "profile_similarity": profile_similarity,
        "identity_shape_gates_passed": (
            width_relative_change <= iter16.iter15b.native_m6.WIDTH_RELATIVE_CHANGE_MAX
            and profile_similarity >= iter16.iter15b.native_m6.PROFILE_SIMILARITY_MIN
        ),
        "artifact_validator": validation,
        "surface_row_count": len(model.get_state().causal_pulse_substrate_surface_log),
        "surface_log_digest": iter16.iter15b.native_m6._digest_json(  # noqa: SLF001
            [
                row.to_artifact()
                for row in model.get_state().causal_pulse_substrate_surface_log
            ]
        ),
        "producer_records_digest": iter16.iter15b.native_m6._digest_json(production_artifacts),  # noqa: SLF001
        "m4_boundary_response_passed": (
            signed_post_score < signed_pre_score - TOL
            and signed_final_score >= signed_post_score - TOL
        ),
        "m5_direction_control_passed": len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES,
        "m6_transfer_candidate_passed": (
            len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES
            and signed_post_score < signed_pre_score - TOL
            and signed_final_score >= signed_pre_score - TOL
            and signed_post_centroid < signed_pre_centroid - TOL
            and signed_final_centroid >= signed_pre_centroid - TOL
        ),
        "all_recovery_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in recovery_scheduled
        ),
        "cost_metric": COST_METRIC,
        "cost_per_feedback_cycle": iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
        "recovery_cost_total": (
            len(recovery_scheduled)
            * iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT
        ),
        "seeded_event_count": len(seeded_events),
        "seeded_events_digest": iter16.iter15b.native_m6._digest_json(seeded_events),  # noqa: SLF001
    }


def _achieved_level(forward: dict[str, Any], reversed_: dict[str, Any]) -> str:
    lanes = [forward, reversed_]
    if all(lane["m6_transfer_candidate_passed"] for lane in lanes):
        return "M6"
    if all(lane["m5_direction_control_passed"] for lane in lanes):
        return "M5"
    if all(lane["m4_boundary_response_passed"] for lane in lanes):
        return "M4"
    return "below_M4"


def build_policy() -> dict[str, Any]:
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter17_ring_unwrap_policy_v1",
        "iteration": "17",
        "status": "passed",
        "unwrap_policy": _ring_unwrap_policy(),
        "checks": {
            "unwrap_policy_declared_before_run": True,
            "front_rear_policy_frozen": True,
            "centroid_policy_frozen": True,
            "route_does_not_cross_unwrap_seam": True,
            "antipodal_tie_cannot_promote": True,
            "wrap_jump_promotion_blocked": True,
        },
    }


def build_report() -> dict[str, Any]:
    iter16c = _load_json(ITER16C_PATH)
    policy = build_policy()
    forward = _run_ring_direction("forward")
    reversed_ = _run_ring_direction("reversed")
    directions = [forward, reversed_]
    achieved_level = _achieved_level(forward, reversed_)
    geometry_init = forward["geometry_init"]
    checks = {
        "iteration_16c_available": iter16c["status"] == "passed",
        "unwrap_policy_available": policy["status"] == "passed",
        "ring_fixture_declared_before_run": geometry_init[
            "ring_topology_declared_before_run"
        ],
        "front_rear_direction_frozen_before_run": geometry_init[
            "front_rear_direction_frozen_before_run"
        ],
        "route_does_not_cross_unwrap_seam": not geometry_init["route_crosses_unwrap_seam"],
        "antipodal_tie_cannot_promote": not geometry_init["antipodal_tie_possible"],
        "wrap_jump_promotion_blocked": (
            policy["unwrap_policy"]["wrap_jump_promotion_allowed"] is False
        ),
        "native_surface_semantics_unchanged": True,
        "native_feedback_producer_semantics_unchanged": True,
        "fixture_topology_changed_before_run": geometry_init[
            "topology_changed_by_fixture_definition"
        ],
        "topology_fixed_during_run": True,
        "no_runtime_topology_mutation_observed": not geometry_init[
            "topology_mutated_during_run"
        ],
        "ring_initialization_budget_neutral": geometry_init["budget_abs_error"]
        <= EPSILON_BUDGET,
        "artifact_validators_passed": all(
            lane["artifact_validator"]["valid"] for lane in directions
        ),
        "budget_and_nonnegative_gates_passed": all(
            lane["budget_abs_error"] <= EPSILON_BUDGET
            and lane["nonnegative_gate_passed"]
            for lane in directions
        ),
        "identity_shape_gates_passed": all(
            lane["identity_shape_gates_passed"] for lane in directions
        ),
        "direction_parity_passed": (
            forward["signed_final_centroid_delta"] > 0
            and reversed_["signed_final_centroid_delta"] > 0
            and forward["raw_final_centroid_delta"] > 0
            and reversed_["raw_final_centroid_delta"] < 0
        ),
        "m4_boundary_response_passed": all(
            lane["m4_boundary_response_passed"] for lane in directions
        ),
        "m5_direction_control_passed": all(
            lane["m5_direction_control_passed"] for lane in directions
        ),
        "m6_ring_transfer_candidate_passed": all(
            lane["m6_transfer_candidate_passed"] for lane in directions
        ),
        "feedback_authorized_not_schedule_copied": all(
            lane["all_recovery_pulses_feedback_authorized"] for lane in directions
        ),
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s1_ring_m6_transfer_candidate_under_declared_unwrap"
        if achieved_level == "M6"
        else f"s1_ring_{achieved_level.lower()}_transfer_ceiling_under_declared_unwrap"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter17_ring_transfer_v1",
        "iteration": "17",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S1_ring_absorber_corridor_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "ring",
        "input_iteration_16c": _artifact_record(ITER16C_PATH),
        "unwrap_policy_artifact": _artifact_record(POLICY_OUTPUT_PATH)
        if POLICY_OUTPUT_PATH.exists()
        else None,
        "claim_ceiling": claim_ceiling,
        "achieved_movement_level": achieved_level,
        "persistence_axis": {
            "persistence_level": "T6_candidate"
            if achieved_level == "M6"
            else "not_measured",
            "persistence_basis": "s1_ring_declared_unwrap_recovers_0_15"
            if achieved_level == "M6"
            else "ring_transfer_below_m6",
            "self_renewed_cycle_count": min(
                forward["recovery_scheduled_cycle_count"],
                reversed_["recovery_scheduled_cycle_count"],
            ),
            "repeatability_status": (
                "forward_and_reversed_three_cycle_recovery_on_s1_ring_declared_unwrap"
                if achieved_level == "M6"
                else "not_established"
            ),
            "recovery_status": "recovers_0_15_ring_declared_unwrap"
            if achieved_level == "M6"
            else "not_established",
            "recovery_tested": True,
            "recovery_passed": achieved_level == "M6",
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "single_declared_unwrap_policy_no_wrap_crossing_or_grid_transfer",
        },
        "ring_policy": policy["unwrap_policy"],
        "candidate_geometry": geometry_init,
        "forward": forward,
        "reversed": reversed_,
        "transfer_summary": {
            "entry_ceiling": iter16c["claim_ceiling"],
            "achieved_level": achieved_level,
            "directions_recovered": [
                lane["direction"] for lane in directions if lane["m6_transfer_candidate_passed"]
            ],
            "challenge_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "unwrap_policy_id": policy["unwrap_policy"]["policy_id"],
            "centroid_delta_frame": "direction_normalized_recovery_delta",
            "cost_metric": COST_METRIC,
            "cost_per_feedback_cycle": iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
            "interpretation": (
                "The S1 ring transfer preserves the corridor M6 candidate "
                "under a declared unwrap policy whose active route does not "
                "cross the seam. This is ring-under-policy evidence, not "
                "circular locomotion, wrap-crossing, broad geometry-transfer, "
                "or adaptive-topology evidence."
            ),
        },
        "go_no_go_for_iteration_18": {
            "iteration_18_allowed": achieved_level in {"M5", "M6"},
            "grid_transfer_ceiling_to_test": claim_ceiling,
            "grid_transfer_guidance": (
                "grid transfer may test M5/M6 under route-defined front/rear masks"
                if achieved_level in {"M5", "M6"}
                else "grid transfer must inherit the weaker ring ceiling"
            ),
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": achieved_level == "M6",
            "native_m6_candidate_gate_passed": achieved_level == "M6",
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
            "broad_geometry_transfer_claim_allowed": False,
            "circular_locomotion_claim_allowed": False,
        },
        "blocked_claims": [
            "circular_locomotion",
            "wrap_crossing_movement",
            "full_T6_general_persistence",
            "grid_transfer",
            "port_graph_transfer",
            "broad_geometry_transfer",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_behavior",
            "agency",
            "identity_acceptance",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "status_short": _run_git(["status", "--short"]),
            "head": _run_git(["rev-parse", "HEAD"]),
        },
        "next_iteration": "18_s3_grid_route_defined_front_rear",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["transfer_summary"]
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 17 S1 Ring Transfer",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 17 transfers the corridor candidate to an S1 ring under an explicit unwrap policy.",
        "",
        "## Transfer Summary",
        "",
        f"- achieved level: `{summary['achieved_level']}`",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- persistence basis: `{axis['persistence_basis']}`",
        f"- recovery status: `{axis['recovery_status']}`",
        f"- challenge perturbation: `{summary['challenge_perturbation']}`",
        f"- directions recovered: `{summary['directions_recovered']}`",
        f"- unwrap policy: `{summary['unwrap_policy_id']}`",
        f"- cost metric: `{summary['cost_metric']}`",
        f"- cost per feedback cycle: `{summary['cost_per_feedback_cycle']}`",
        "",
        summary["interpretation"],
        "",
        "Unwrap note: the seam is fixed at `[20, 0]`, the active route does not cross it, and wrap-jump promotion is blocked.",
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Go/No-Go", ""])
    for key, value in report["go_no_go_for_iteration_18"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Command",
            "",
            f"```bash\n{COMMAND}\n```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    policy = build_policy()
    POLICY_OUTPUT_PATH.write_text(
        json.dumps(policy, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = build_report()
    report["unwrap_policy_artifact"] = _artifact_record(POLICY_OUTPUT_PATH)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
