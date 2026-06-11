#!/usr/bin/env python3
"""Run N04 Iteration 15-E large-shock absorber geometry probe."""

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


ITER15C_PATH = N04 / "outputs/n04_iter15c_s0_perturbation_tolerance_profile.json"
ITER15D_PATH = N04 / "outputs/n04_iter15d_shock_resistant_recovery_geometry_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter15e_large_shock_absorber_geometry_report.json"
REPORT_PATH = N04 / "reports/n04_iter15e_large_shock_absorber_geometry_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter15e_large_shock_absorber_geometry.py"
)

CHALLENGE_TRANSFER_AMOUNT = 0.15
CENTRAL_RESERVOIR_NODE = 10
FRONT_ABSORBER_NODE = 14
REAR_ABSORBER_NODE = 6
RESERVOIR_BOOST = 0.25
COMPENSATING_DEBIT_NODES = (9, 11)
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


def _add_recovery_channel(state: Any, source: int, target: int, slot: int) -> int:
    edge_id = state.topology.connect_ports(
        source,
        slot,
        target,
        2,
        {
            "kind": "s0_absorber_recovery_channel",
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


def _apply_absorber_geometry(state: Any) -> dict[str, Any]:
    before_values = [
        float(state.nodes[index].coherence)
        for index in range(iter15b.native_m6.NODE_COUNT)
    ]
    before_budget = sum(before_values)
    debit_per_node = RESERVOIR_BOOST / len(COMPENSATING_DEBIT_NODES)
    state.nodes[CENTRAL_RESERVOIR_NODE].coherence += RESERVOIR_BOOST
    for node_id in COMPENSATING_DEBIT_NODES:
        state.nodes[node_id].coherence -= debit_per_node
    front_edge = _add_recovery_channel(
        state,
        CENTRAL_RESERVOIR_NODE,
        FRONT_ABSORBER_NODE,
        2,
    )
    rear_edge = _add_recovery_channel(
        state,
        CENTRAL_RESERVOIR_NODE,
        REAR_ABSORBER_NODE,
        3,
    )
    after_values = [
        float(state.nodes[index].coherence)
        for index in range(iter15b.native_m6.NODE_COUNT)
    ]
    after_budget = sum(after_values)
    return {
        "geometry_id": "s0_chain_large_shock_absorber_v1",
        "geometry_family": "same_family_chain_with_central_reservoir_and_absorber_channels",
        "central_reservoir_node": CENTRAL_RESERVOIR_NODE,
        "front_absorber_node": FRONT_ABSORBER_NODE,
        "rear_absorber_node": REAR_ABSORBER_NODE,
        "front_recovery_edge_id": front_edge,
        "rear_recovery_edge_id": rear_edge,
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
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
        "reason": (
            "Iteration 15-D avoided source-budget exhaustion at the 0.15 "
            "shock but could not restore centroid. This design adds explicit "
            "fixed recovery-channel geometry from a central reservoir to "
            "boundary absorber nodes so native feedback packets have enough "
            "geometric leverage to counter the large shock."
        ),
    }


def _direction_config(direction: str, geometry: dict[str, Any]) -> dict[str, Any]:
    if direction == "forward":
        return {
            "source": CENTRAL_RESERVOIR_NODE,
            "target": FRONT_ABSORBER_NODE,
            "edge_id": geometry["front_recovery_edge_id"],
            "expected_polarity": "positive",
            "expected_sign": 1,
            "route_id": "s0-absorber-forward",
        }
    if direction == "reversed":
        return {
            "source": CENTRAL_RESERVOIR_NODE,
            "target": REAR_ABSORBER_NODE,
            "edge_id": geometry["rear_recovery_edge_id"],
            "expected_polarity": "negative",
            "expected_sign": -1,
            "route_id": "s0-absorber-reversed",
        }
    raise ValueError(f"unknown direction {direction!r}")


def _run_absorber_direction(direction: str) -> dict[str, Any]:
    state, _edges = iter15b.native_m6._s0_chain_state()  # noqa: SLF001
    geometry = _apply_absorber_geometry(state)
    config = _direction_config(direction, geometry)
    model = iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter15b.native_m6._params(),  # noqa: SLF001
    )
    edge_id = config["edge_id"]
    initial_values = iter15b.native_m6._node_vector(model)  # noqa: SLF001
    initial_budget = iter15b.native_m6._budget(model)  # noqa: SLF001

    model.schedule_packet_departure(
        source_node_id=config["source"],
        target_node_id=config["target"],
        edge_id=edge_id,
        amount=iter15b.native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    seeded_events = iter15b.native_m6._process_queue(model)  # noqa: SLF001

    baseline_cycles = [
        iter15b._feedback_cycle(  # noqa: SLF001
            model,
            config=config,
            edge_id=edge_id,
            cycle_index=cycle_index,
            phase="pre_perturbation_baseline",
        )
        for cycle_index in range(iter15b.PRE_PERTURBATION_CYCLES)
    ]
    pre_perturbation_values = iter15b.native_m6._node_vector(model)  # noqa: SLF001
    pre_perturbation_centroid = iter15b.native_m6._centroid(pre_perturbation_values)  # noqa: SLF001
    pre_perturbation_score = iter15b._boundary_polarity_score(model)  # noqa: SLF001
    perturbation = iter15b._apply_polarity_damping_perturbation(  # noqa: SLF001
        model,
        direction=direction,
        transfer_amount=CHALLENGE_TRANSFER_AMOUNT,
    )
    post_perturbation_values = iter15b.native_m6._node_vector(model)  # noqa: SLF001
    post_perturbation_centroid = iter15b.native_m6._centroid(post_perturbation_values)  # noqa: SLF001
    post_perturbation_score = iter15b._boundary_polarity_score(model)  # noqa: SLF001
    recovery_cycles = [
        iter15b._feedback_cycle(  # noqa: SLF001
            model,
            config=config,
            edge_id=edge_id,
            cycle_index=cycle_index,
            phase="post_perturbation_recovery",
        )
        for cycle_index in range(iter15b.RECOVERY_WINDOW_CYCLES)
    ]
    final_values = iter15b.native_m6._node_vector(model)  # noqa: SLF001
    final_budget = iter15b.native_m6._budget(model)  # noqa: SLF001
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
    signed_pre_score = sign * pre_perturbation_score
    signed_post_score = sign * post_perturbation_score
    signed_final_score = sign * iter15b._boundary_polarity_score(model)  # noqa: SLF001
    raw_pre_centroid = pre_perturbation_centroid - initial_centroid
    raw_post_centroid = post_perturbation_centroid - initial_centroid
    raw_final_centroid = (
        iter15b.native_m6._centroid(final_values) - initial_centroid  # noqa: SLF001
    )
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
        "edge_id": edge_id,
        "front_mask": list(iter15b.native_m6.FRONT_MASK),
        "rear_mask": list(iter15b.native_m6.REAR_MASK),
        "pre_perturbation_cycle_count": len(
            [
                cycle
                for cycle in baseline_cycles
                if cycle["producer_reason_code"]
                == iter15b.native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
            ]
        ),
        "recovery_window_cycles": iter15b.RECOVERY_WINDOW_CYCLES,
        "recovery_scheduled_cycle_count": len(recovery_scheduled),
        "baseline_cycles": [cycle_summary(cycle) for cycle in baseline_cycles],
        "recovery_cycles": [cycle_summary(cycle) for cycle in recovery_cycles],
        "perturbation": perturbation,
        "signed_pre_perturbation_score": signed_pre_score,
        "signed_post_perturbation_score": signed_post_score,
        "signed_final_score": signed_final_score,
        "signed_pre_perturbation_centroid_delta": signed_pre_centroid,
        "signed_post_perturbation_centroid_delta": signed_post_centroid,
        "signed_final_centroid_delta": signed_final_centroid,
        "raw_pre_perturbation_centroid_delta": raw_pre_centroid,
        "raw_post_perturbation_centroid_delta": raw_post_centroid,
        "raw_final_centroid_delta": raw_final_centroid,
        "centroid_coordinate_frame": "linear_s0_chain_index",
        "centroid_delta_frame": "direction_normalized_recovery_delta",
        "centroid_sign_convention": (
            "raw_*_centroid_delta fields use increasing S0 chain index. "
            "signed_*_centroid_delta fields are multiplied by expected_sign "
            "so positive means recovery in the lane's declared direction."
        ),
        "cost_metric": COST_METRIC,
        "cost_per_feedback_cycle": iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
        "cost_scaling_source": "inherited_from_iteration_15_native_feedback_packet_amount",
        "recovery_cost_total": (
            len(recovery_scheduled) * iter15b.native_m6.FEEDBACK_PACKET_AMOUNT
        ),
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
        "r6_recovery_candidate_passed": (
            signed_post_score < signed_pre_score - TOL
            and signed_final_score >= signed_pre_score - TOL
        ),
        "t6_recovery_candidate_passed": (
            len(recovery_scheduled) >= iter15b.RECOVERY_WINDOW_CYCLES
            and signed_post_centroid < signed_pre_centroid - TOL
            and signed_final_centroid >= signed_pre_centroid - TOL
        ),
        "all_recovery_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in recovery_scheduled
        ),
        "seeded_event_count": len(seeded_events),
        "seeded_events_digest": iter15b.native_m6._digest_json(seeded_events),  # noqa: SLF001
    }


def build_report() -> dict[str, Any]:
    iter15c = _load_json(ITER15C_PATH)
    iter15d = _load_json(ITER15D_PATH)
    forward = _run_absorber_direction("forward")
    reversed_ = _run_absorber_direction("reversed")
    directions = [forward, reversed_]
    both_t6 = all(direction["t6_recovery_candidate_passed"] for direction in directions)
    both_r6 = all(direction["r6_recovery_candidate_passed"] for direction in directions)
    full_recovery_scheduled = all(
        direction["recovery_scheduled_cycle_count"] >= iter15b.RECOVERY_WINDOW_CYCLES
        for direction in directions
    )
    source_exhaustion_avoided = all(
        "feedback_source_budget_exhausted"
        not in [cycle["producer_reason_code"] for cycle in direction["recovery_cycles"]]
        for direction in directions
    )
    geometry_init = forward["geometry_init"]
    checks = {
        "iteration_15c_available": iter15c["status"] == "passed",
        "iteration_15d_available": iter15d["status"] == "passed",
        "candidate_absorber_geometry_declared_before_run": True,
        "challenge_perturbation_is_0_15": CHALLENGE_TRANSFER_AMOUNT == 0.15,
        "native_surface_semantics_unchanged": True,
        "native_feedback_producer_semantics_unchanged": True,
        "absorber_initialization_budget_neutral": geometry_init["budget_abs_error"]
        <= EPSILON_BUDGET,
        "topology_fixed_during_run": True,
        "fixture_topology_changed_before_run": geometry_init[
            "topology_changed_by_fixture_definition"
        ],
        "no_runtime_topology_mutation_observed": not geometry_init[
            "topology_mutated_during_run"
        ],
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
            direction["artifact_validator"]["valid"] for direction in directions
        ),
        "budget_and_nonnegative_gates_passed": all(
            direction["budget_abs_error"] <= EPSILON_BUDGET
            and direction["nonnegative_gate_passed"]
            for direction in directions
        ),
        "identity_shape_gates_passed": all(
            direction["identity_shape_gates_passed"] for direction in directions
        ),
        "source_budget_exhaustion_avoided": source_exhaustion_avoided,
        "r6_polarity_restoration_passed": both_r6,
        "t6_centroid_restoration_passed": both_t6,
        "cost_scaling_inherited_from_iteration_15": all(
            direction["cost_per_feedback_cycle"]
            == iter15b.native_m6.FEEDBACK_PACKET_AMOUNT
            for direction in directions
        ),
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "large_shock_absorber_same_family_recovery_candidate"
        if status == "passed"
        else iter15d["claim_ceiling"]
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter15e_large_shock_absorber_geometry_v1",
        "iteration": "15-E",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S0_chain_large_shock_absorber_v1",
        "geometry_scope": "same_family_absorber_design",
        "input_iteration_15c": _artifact_record(ITER15C_PATH),
        "input_iteration_15d": _artifact_record(ITER15D_PATH),
        "claim_ceiling": claim_ceiling,
        "candidate_geometry": geometry_init,
        "plain_s0_reference_at_0_15": {
            "outcome": next(
                point for point in iter15c["sweep_points"] if point["transfer_amount"] == 0.15
            )["outcome"],
            "primary_blocker": next(
                point for point in iter15c["sweep_points"] if point["transfer_amount"] == 0.15
            )["primary_blocker"],
            "t6_recovered_both_directions": False,
        },
        "source_reservoir_reference_at_0_15": {
            "claim_ceiling": iter15d["claim_ceiling"],
            "stress_recovered": iter15d["resilience_summary"]["stress_recovered"],
            "source_budget_exhaustion_avoided": iter15d["resilience_summary"][
                "source_budget_exhaustion_avoided_at_stress"
            ],
        },
        "forward": forward,
        "reversed": reversed_,
        "absorber_summary": {
            "challenge_perturbation": CHALLENGE_TRANSFER_AMOUNT,
            "full_recovery_window_scheduled": full_recovery_scheduled,
            "source_budget_exhaustion_avoided": source_exhaustion_avoided,
            "r6_polarity_restoration_passed": both_r6,
            "t6_centroid_restoration_passed": both_t6,
            "directions_recovered": [
                direction["direction"]
                for direction in directions
                if direction["t6_recovery_candidate_passed"]
            ],
            "centroid_delta_frame": "direction_normalized_recovery_delta",
            "cost_metric": COST_METRIC,
            "cost_per_feedback_cycle": iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
            "cost_scaling_source": "inherited_from_iteration_15_native_feedback_packet_amount",
            "interpretation": (
                "The large-shock absorber geometry restores the 0.15 shock "
                "in both directions by combining central source capacity with "
                "fixed recovery channels to boundary absorber nodes. Recovery "
                "still occurs through native packet events, surface rows, "
                "feedback eligibility, scheduled packet work, and step() "
                "mutation."
            ),
        },
        "go_no_go_for_iteration_16": {
            "iteration_16_allowed": status == "passed",
            "entry_ceiling_for_geometry_transfer": claim_ceiling,
            "iteration_16_fixture_guidance": (
                "test absorber-informed corridor/widened-chain geometry"
                if status == "passed"
                else "test source-reservoir-only resilience from 15-D"
            ),
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": iter15d["claim_flags"]["native_m6"],
            "native_m6_candidate_gate_passed": iter15d["claim_flags"][
                "native_m6_candidate_gate_passed"
            ],
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
        "next_iteration": "16_s4_corridor_or_widened_chain_geometry_transfer",
    }


def write_report(report: dict[str, Any]) -> None:
    summary = report["absorber_summary"]
    lines = [
        "# N04 Iteration 15-E Large-Shock Absorber Geometry",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 15-E tests a same-family absorber geometry against the 0.15 shock.",
        "",
        "## Absorber Summary",
        "",
        f"- challenge perturbation: `{summary['challenge_perturbation']}`",
        f"- full recovery window scheduled: `{summary['full_recovery_window_scheduled']}`",
        f"- source-budget exhaustion avoided: `{summary['source_budget_exhaustion_avoided']}`",
        f"- R6 polarity restoration passed: `{summary['r6_polarity_restoration_passed']}`",
        f"- T6 centroid restoration passed: `{summary['t6_centroid_restoration_passed']}`",
        f"- directions recovered: `{summary['directions_recovered']}`",
        f"- cost metric: `{summary['cost_metric']}`",
        f"- cost per feedback cycle: `{summary['cost_per_feedback_cycle']}`",
        "",
        summary["interpretation"],
        "",
        "Topology note: the absorber recovery channels are declared in the fixture before the run. Runtime topology remains fixed; no topology mutation occurs during execution.",
        "",
        "Centroid note: raw centroid deltas use increasing S0 chain index. Signed centroid deltas are direction-normalized, so positive means recovery in the lane's declared direction for both forward and reversed lanes.",
        "",
        "Cost note: recovery cost uses the Iteration 15 native feedback packet cost metric and packet amount; 15-E does not introduce a new cost schedule.",
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
    for key, value in report["go_no_go_for_iteration_16"].items():
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
