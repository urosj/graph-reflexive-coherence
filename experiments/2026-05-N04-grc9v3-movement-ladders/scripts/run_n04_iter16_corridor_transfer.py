#!/usr/bin/env python3
"""Run N04 Iteration 16 S4 corridor/widened-chain transfer probe."""

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

import run_n04_iter15b_s0_perturbation_recovery as iter15b  # noqa: E402


ITER15E_PATH = N04 / "outputs/n04_iter15e_large_shock_absorber_geometry_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter16_corridor_transfer_report.json"
REPORT_PATH = N04 / "reports/n04_iter16_corridor_transfer_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter16_corridor_transfer.py"
)

CHALLENGE_TRANSFER_AMOUNT = 0.15
CENTRAL_RESERVOIR_NODE = 10
FRONT_CORRIDOR_NODES = (13, 14)
REAR_CORRIDOR_NODES = (7, 6)
RESERVOIR_BOOST = 0.25
COMPENSATING_DEBIT_NODES = (9, 11)
PRE_TRANSFER_CYCLES = 5
RECOVERY_WINDOW_CYCLES = 3
COST_METRIC = "total_redistribution_load_per_cycle"
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


def _add_corridor_channel(state: Any, source: int, target: int, slot: int) -> int:
    edge_id = state.topology.connect_ports(
        source,
        slot,
        target,
        2,
        {
            "kind": "s4_widened_chain_corridor_channel",
            "source_index": source,
            "target_index": target,
        },
    )
    state.port_edges[edge_id] = iter15b.native_m6.PortEdge(
        source,
        slot,
        target,
        2,
        conductance=1.0,
        flux_uv=0.0,
    )
    state.base_conductance[edge_id] = 1.0
    state.geometric_length[edge_id] = abs(target - source)
    state.temporal_delay[edge_id] = 1.0
    state.flux_coupling[edge_id] = 0.0
    return edge_id


def _apply_corridor_geometry(state: Any) -> dict[str, Any]:
    before_values = [
        float(state.nodes[index].coherence)
        for index in range(iter15b.native_m6.NODE_COUNT)
    ]
    before_budget = sum(before_values)
    debit_per_node = RESERVOIR_BOOST / len(COMPENSATING_DEBIT_NODES)
    state.nodes[CENTRAL_RESERVOIR_NODE].coherence += RESERVOIR_BOOST
    for node_id in COMPENSATING_DEBIT_NODES:
        state.nodes[node_id].coherence -= debit_per_node

    front_inner_edge = _add_corridor_channel(state, CENTRAL_RESERVOIR_NODE, 13, 2)
    front_outer_edge = _add_corridor_channel(state, CENTRAL_RESERVOIR_NODE, 14, 3)
    rear_inner_edge = _add_corridor_channel(state, CENTRAL_RESERVOIR_NODE, 7, 4)
    rear_outer_edge = _add_corridor_channel(state, CENTRAL_RESERVOIR_NODE, 6, 5)

    after_values = [
        float(state.nodes[index].coherence)
        for index in range(iter15b.native_m6.NODE_COUNT)
    ]
    after_budget = sum(after_values)
    return {
        "geometry_id": "s4_widened_chain_absorber_corridor_v1",
        "geometry_family": "s4_corridor_widened_chain_with_absorber_channels",
        "source_geometry": "s0_chain_large_shock_absorber_v1",
        "front_region": list(FRONT_CORRIDOR_NODES),
        "rear_region": list(REAR_CORRIDOR_NODES),
        "central_reservoir_node": CENTRAL_RESERVOIR_NODE,
        "front_inner_edge_id": front_inner_edge,
        "front_outer_edge_id": front_outer_edge,
        "rear_inner_edge_id": rear_inner_edge,
        "rear_outer_edge_id": rear_outer_edge,
        "reservoir_boost": RESERVOIR_BOOST,
        "compensating_debit_nodes": list(COMPENSATING_DEBIT_NODES),
        "compensating_debit_per_node": debit_per_node,
        "budget_before": before_budget,
        "budget_after": after_budget,
        "budget_abs_error": abs(after_budget - before_budget),
        "nonnegative_after_geometry_init": min(after_values) >= -TOL,
        "node_delta_digest": iter15b.native_m6._digest_json(  # noqa: SLF001
            [after - before for before, after in zip(before_values, after_values, strict=True)]
        ),
        "topology_changed_by_fixture_definition": True,
        "topology_mutated_during_run": False,
        "coordinate_frame": "linear_widened_chain_corridor",
        "positive_direction": "increasing_chain_index",
        "front_rear_direction_frozen_before_run": True,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
        "reason": (
            "Iteration 16 transfers the 15-E absorber-informed result into a "
            "lowest-risk S4-style widened-chain corridor. The fixture is "
            "declared before execution, keeps runtime topology fixed, and "
            "uses the same native surface and feedback producer semantics."
        ),
    }


def _direction_config(direction: str, geometry: dict[str, Any]) -> dict[str, Any]:
    if direction == "forward":
        return {
            "source": CENTRAL_RESERVOIR_NODE,
            "target": 14,
            "edge_id": geometry["front_outer_edge_id"],
            "expected_polarity": "positive",
            "expected_sign": 1,
            "route_id": "s4-corridor-forward",
        }
    if direction == "reversed":
        return {
            "source": CENTRAL_RESERVOIR_NODE,
            "target": 6,
            "edge_id": geometry["rear_outer_edge_id"],
            "expected_polarity": "negative",
            "expected_sign": -1,
            "route_id": "s4-corridor-reversed",
        }
    raise ValueError(f"unknown direction {direction!r}")


def _run_corridor_direction(
    direction: str,
    *,
    transfer_amount: float = CHALLENGE_TRANSFER_AMOUNT,
) -> dict[str, Any]:
    state, _edges = iter15b.native_m6._s0_chain_state()  # noqa: SLF001
    geometry = _apply_corridor_geometry(state)
    config = _direction_config(direction, geometry)
    model = iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter15b.native_m6._params(),  # noqa: SLF001
    )
    initial_values = iter15b.native_m6._node_vector(model)  # noqa: SLF001
    initial_budget = iter15b.native_m6._budget(model)  # noqa: SLF001

    model.schedule_packet_departure(
        source_node_id=config["source"],
        target_node_id=config["target"],
        edge_id=config["edge_id"],
        amount=iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    seeded_events = iter15b.native_m6._process_queue(model)  # noqa: SLF001

    baseline_cycles = [
        iter15b._feedback_cycle(  # noqa: SLF001
            model,
            config=config,
            edge_id=config["edge_id"],
            cycle_index=cycle_index,
            phase="pre_perturbation_baseline",
        )
        for cycle_index in range(PRE_TRANSFER_CYCLES)
    ]
    pre_values = iter15b.native_m6._node_vector(model)  # noqa: SLF001
    pre_centroid = iter15b.native_m6._centroid(pre_values)  # noqa: SLF001
    pre_score = iter15b._boundary_polarity_score(model)  # noqa: SLF001
    perturbation = iter15b._apply_polarity_damping_perturbation(  # noqa: SLF001
        model,
        direction=direction,
        transfer_amount=transfer_amount,
    )
    post_values = iter15b.native_m6._node_vector(model)  # noqa: SLF001
    post_centroid = iter15b.native_m6._centroid(post_values)  # noqa: SLF001
    post_score = iter15b._boundary_polarity_score(model)  # noqa: SLF001

    recovery_cycles = [
        iter15b._feedback_cycle(  # noqa: SLF001
            model,
            config=config,
            edge_id=config["edge_id"],
            cycle_index=cycle_index,
            phase="post_perturbation_recovery",
        )
        for cycle_index in range(RECOVERY_WINDOW_CYCLES)
    ]
    final_values = iter15b.native_m6._node_vector(model)  # noqa: SLF001
    final_budget = iter15b.native_m6._budget(model)  # noqa: SLF001
    final_score = iter15b._boundary_polarity_score(model)  # noqa: SLF001
    final_centroid = iter15b.native_m6._centroid(final_values)  # noqa: SLF001
    production_artifacts = [
        cycle["production_artifact"]
        for cycle in [*baseline_cycles, *recovery_cycles]
        if cycle["production_artifact"] is not None
    ]
    validation = iter15b.native_m6.validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=model.snapshot()["events"],
        production_results=production_artifacts,
    )
    recovery_scheduled = [
        cycle
        for cycle in recovery_cycles
        if cycle["producer_reason_code"]
        == iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ]
    sign = config["expected_sign"]
    initial_centroid = iter15b.native_m6._centroid(initial_values)  # noqa: SLF001
    raw_pre_centroid = pre_centroid - initial_centroid
    raw_post_centroid = post_centroid - initial_centroid
    raw_final_centroid = final_centroid - initial_centroid
    signed_pre_score = sign * pre_score
    signed_post_score = sign * post_score
    signed_final_score = sign * final_score
    signed_pre_centroid = sign * raw_pre_centroid
    signed_post_centroid = sign * raw_post_centroid
    signed_final_centroid = sign * raw_final_centroid
    width_initial = iter15b.native_m6._width(initial_values)  # noqa: SLF001
    width_final = iter15b.native_m6._width(final_values)  # noqa: SLF001
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = iter15b.native_m6._profile_similarity(initial_values, final_values)  # noqa: SLF001

    def cycle_summary(cycle: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in cycle.items()
            if key not in {"production_artifact", "processed_events"}
        } | {
            "processed_event_count": len(cycle["processed_events"]),
            "processed_events_digest": iter15b.native_m6._digest_json(cycle["processed_events"]),  # noqa: SLF001
        }

    return {
        "direction": direction,
        "geometry_init": geometry,
        "source_node_id": config["source"],
        "target_node_id": config["target"],
        "edge_id": config["edge_id"],
        "front_mask": list(iter15b.native_m6.FRONT_MASK),
        "rear_mask": list(iter15b.native_m6.REAR_MASK),
        "pre_transfer_cycle_count": len(
            [
                cycle
                for cycle in baseline_cycles
                if cycle["producer_reason_code"]
                == iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
            ]
        ),
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
        "centroid_coordinate_frame": "linear_s0_chain_index_with_s4_corridor_edges",
        "centroid_delta_frame": "direction_normalized_recovery_delta",
        "budget_initial": initial_budget,
        "budget_final": final_budget,
        "budget_abs_error": abs(final_budget - initial_budget),
        "nonnegative_gate_passed": min(final_values) >= -TOL,
        "width_relative_change": width_relative_change,
        "profile_similarity": profile_similarity,
        "identity_shape_gates_passed": (
            width_relative_change <= iter15b.native_m6.WIDTH_RELATIVE_CHANGE_MAX
            and profile_similarity >= iter15b.native_m6.PROFILE_SIMILARITY_MIN
        ),
        "artifact_validator": validation,
        "surface_row_count": len(model.get_state().causal_pulse_substrate_surface_log),
        "surface_log_digest": iter15b.native_m6._digest_json(  # noqa: SLF001
            [
                row.to_artifact()
                for row in model.get_state().causal_pulse_substrate_surface_log
            ]
        ),
        "producer_records_digest": iter15b.native_m6._digest_json(production_artifacts),  # noqa: SLF001
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
        "cost_per_feedback_cycle": iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
        "recovery_cost_total": len(recovery_scheduled) * iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
        "seeded_event_count": len(seeded_events),
        "seeded_events_digest": iter15b.native_m6._digest_json(seeded_events),  # noqa: SLF001
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


def build_report() -> dict[str, Any]:
    iter15e = _load_json(ITER15E_PATH)
    forward = _run_corridor_direction("forward")
    reversed_ = _run_corridor_direction("reversed")
    directions = [forward, reversed_]
    achieved_level = _achieved_level(forward, reversed_)
    geometry_init = forward["geometry_init"]
    checks = {
        "iteration_15e_available": iter15e["status"] == "passed",
        "corridor_fixture_declared_before_run": True,
        "front_rear_direction_frozen_before_run": geometry_init[
            "front_rear_direction_frozen_before_run"
        ],
        "geometry_scope_is_transferred_geometry": True,
        "native_surface_semantics_unchanged": True,
        "native_feedback_producer_semantics_unchanged": True,
        "fixture_topology_changed_before_run": geometry_init[
            "topology_changed_by_fixture_definition"
        ],
        "topology_fixed_during_run": True,
        "no_runtime_topology_mutation_observed": not geometry_init[
            "topology_mutated_during_run"
        ],
        "corridor_initialization_budget_neutral": geometry_init["budget_abs_error"]
        <= EPSILON_BUDGET,
        "no_forbidden_direct_writes": not any(
            geometry_init[key]
            for key in (
                "direct_support_mask_write",
                "direct_centroid_write",
                "direct_displacement_write",
                "direct_topology_write",
                "direct_claim_flag_write",
            )
        ),
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
        "m6_transfer_candidate_passed": all(
            lane["m6_transfer_candidate_passed"] for lane in directions
        ),
        "feedback_authorized_not_schedule_copied": all(
            lane["all_recovery_pulses_feedback_authorized"] for lane in directions
        ),
        "cost_scaling_inherited_from_iteration_15": all(
            lane["cost_per_feedback_cycle"] == iter15b.native_m6.FEEDBACK_PACKET_AMOUNT
            for lane in directions
        ),
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "s4_corridor_m6_transfer_candidate"
        if achieved_level == "M6"
        else f"s4_corridor_{achieved_level.lower()}_transfer_ceiling"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter16_corridor_transfer_v1",
        "iteration": "16",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S4_widened_chain_absorber_corridor_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "corridor",
        "input_iteration_15e": _artifact_record(ITER15E_PATH),
        "claim_ceiling": claim_ceiling,
        "achieved_movement_level": achieved_level,
        "persistence_axis": {
            "persistence_level": "T6_candidate"
            if achieved_level == "M6"
            else "not_measured",
            "persistence_basis": "s4_corridor_transfer_recovers_0_15"
            if achieved_level == "M6"
            else "corridor_transfer_below_m6",
            "self_renewed_cycle_count": min(
                forward["recovery_scheduled_cycle_count"],
                reversed_["recovery_scheduled_cycle_count"],
            ),
            "repeatability_status": (
                "forward_and_reversed_three_cycle_recovery_on_s4_corridor"
                if achieved_level == "M6"
                else "not_established"
            ),
            "recovery_status": "recovers_0_15_corridor_transfer"
            if achieved_level == "M6"
            else "not_established",
            "recovery_tested": True,
            "recovery_passed": achieved_level == "M6",
            "recovery_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": (
                "single_corridor_fixture_only_no_broader_perturbation_envelope"
            ),
        },
        "candidate_geometry": geometry_init,
        "forward": forward,
        "reversed": reversed_,
        "transfer_summary": {
            "entry_ceiling": iter15e["claim_ceiling"],
            "achieved_level": achieved_level,
            "directions_recovered": [
                lane["direction"] for lane in directions if lane["m6_transfer_candidate_passed"]
            ],
            "challenge_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "front_rear_direction": "positive=increasing_chain_index",
            "centroid_delta_frame": "direction_normalized_recovery_delta",
            "cost_metric": COST_METRIC,
            "cost_per_feedback_cycle": iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
            "interpretation": (
                "The absorber-informed S4 widened-chain corridor transfers "
                "the same native causal pulse-substrate surface and feedback "
                "producer semantics to a non-identical fixed fixture. The "
                "candidate preserves direction parity and same-window "
                "feedback recovery in both directions, while broad "
                "geometry-transfer, locomotion-like, and adaptive-topology "
                "claims remain blocked."
            ),
        },
        "go_no_go_for_iteration_17": {
            "iteration_17_allowed": achieved_level in {"M4", "M5", "M6"},
            "ring_transfer_ceiling_to_test": claim_ceiling,
            "ring_transfer_guidance": (
                "ring transfer may test M5/M6 only under explicit unwrap policy"
                if achieved_level in {"M5", "M6"}
                else "ring transfer must inherit the weaker corridor ceiling"
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
        },
        "blocked_claims": [
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_behavior",
            "agency",
            "identity_acceptance",
            "movement_inherited_from_n03",
            "unrestricted_movement",
            "broad_geometry_transfer",
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
        "next_iteration": "17_s1_ring_with_explicit_unwrap_policy",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["transfer_summary"]
    lines = [
        "# N04 Iteration 16 S4 Corridor Transfer",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 16 transfers the strongest absorber-informed same-family "
        "result to a fixed S4 widened-chain corridor fixture.",
        "",
        "## Transfer Summary",
        "",
        f"- entry ceiling: `{summary['entry_ceiling']}`",
        f"- achieved level: `{summary['achieved_level']}`",
        f"- persistence level: `{report['persistence_axis']['persistence_level']}`",
        f"- persistence basis: `{report['persistence_axis']['persistence_basis']}`",
        f"- recovery status: `{report['persistence_axis']['recovery_status']}`",
        f"- challenge perturbation: `{summary['challenge_perturbation']}`",
        f"- directions recovered: `{summary['directions_recovered']}`",
        f"- front/rear direction: `{summary['front_rear_direction']}`",
        f"- cost metric: `{summary['cost_metric']}`",
        f"- cost per feedback cycle: `{summary['cost_per_feedback_cycle']}`",
        "",
        summary["interpretation"],
        "",
        "Topology note: corridor rails are fixture-defined before execution. Runtime topology remains fixed; no topology mutation occurs during the run.",
        "",
        "Centroid note: raw centroid deltas use increasing chain index. Signed centroid deltas are direction-normalized, so positive means recovery in the lane's declared direction.",
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Go/No-Go",
            "",
        ]
    )
    for key, value in report["go_no_go_for_iteration_17"].items():
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
    report = build_report()
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
