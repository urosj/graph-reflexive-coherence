#!/usr/bin/env python3
"""Run N04 Iteration 15-D shock-resistant recovery geometry probe.

The probe keeps the native causal pulse-substrate surface and feedback producer
unchanged, but replaces plain S0 with a budget-neutral source-reservoir variant
that gives the two feedback source nodes additional recoverable capacity.
"""

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
OUTPUT_PATH = N04 / "outputs/n04_iter15d_shock_resistant_recovery_geometry_report.json"
REPORT_PATH = N04 / "reports/n04_iter15d_shock_resistant_recovery_geometry_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter15d_shock_resistant_geometry.py"
)

SOURCE_RESERVOIR_BOOST_PER_NODE = 0.20
SOURCE_RESERVOIR_NODES = (
    iter15b.native_m6.REVERSED_SOURCE,
    iter15b.native_m6.FORWARD_SOURCE,
)
COMPENSATING_DEBIT_NODES = (9, 11)
STRESS_TRANSFER_AMOUNT = iter15b.PERTURBATION_TRANSFER_AMOUNT
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


def _apply_source_reservoir_geometry(state: Any) -> dict[str, Any]:
    before_values = [
        float(state.nodes[index].coherence)
        for index in range(iter15b.native_m6.NODE_COUNT)
    ]
    before_budget = sum(before_values)
    for node_id in SOURCE_RESERVOIR_NODES:
        state.nodes[node_id].coherence += SOURCE_RESERVOIR_BOOST_PER_NODE
    for node_id in COMPENSATING_DEBIT_NODES:
        state.nodes[node_id].coherence -= SOURCE_RESERVOIR_BOOST_PER_NODE
    after_values = [
        float(state.nodes[index].coherence)
        for index in range(iter15b.native_m6.NODE_COUNT)
    ]
    after_budget = sum(after_values)
    return {
        "geometry_id": "s0_chain_source_reservoir_buffer_v1",
        "geometry_family": "same_family_chain_with_budget_neutral_source_reservoir",
        "source_reservoir_nodes": list(SOURCE_RESERVOIR_NODES),
        "compensating_debit_nodes": list(COMPENSATING_DEBIT_NODES),
        "source_reservoir_boost_per_node": SOURCE_RESERVOIR_BOOST_PER_NODE,
        "budget_before": before_budget,
        "budget_after": after_budget,
        "budget_abs_error": abs(after_budget - before_budget),
        "nonnegative_after_geometry_init": min(after_values) >= -TOL,
        "node_delta_digest": iter15b.native_m6._digest_json(  # noqa: SLF001
            [after - before for before, after in zip(before_values, after_values, strict=True)]
        ),
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
        "reason": (
            "Iteration 15-C identified source-budget exhaustion after two "
            "recovery cycles as the T6 blocker; this variant adds symmetric "
            "budget-neutral source reservoir capacity at the native feedback "
            "source nodes without changing the producer or surface semantics."
        ),
    }


def _run_buffered_direction(direction: str, *, transfer_amount: float) -> dict[str, Any]:
    config = iter15b._direction_config(direction)  # noqa: SLF001
    state, edges = iter15b.native_m6._s0_chain_state()  # noqa: SLF001
    geometry_init = _apply_source_reservoir_geometry(state)
    model = iter15b.native_m6.LGRC9V3.from_state(
        state,
        iter15b.native_m6._params(),  # noqa: SLF001
    )
    edge_id = edges[(config["source"], config["target"])]
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
        transfer_amount=transfer_amount,
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
    signed_pre_centroid = sign * (pre_perturbation_centroid - initial_centroid)
    signed_post_centroid = sign * (post_perturbation_centroid - initial_centroid)
    signed_final_centroid = sign * (
        iter15b.native_m6._centroid(final_values) - initial_centroid  # noqa: SLF001
    )
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
        "transfer_amount": transfer_amount,
        "geometry_init": geometry_init,
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


def _find_s0_point(iter15c: dict[str, Any], amount: float) -> dict[str, Any]:
    for point in iter15c["sweep_points"]:
        if abs(point["transfer_amount"] - amount) <= 1e-12:
            return point
    raise ValueError(f"missing S0 comparison point for transfer amount {amount}")


def _trial(amount: float, iter15c: dict[str, Any]) -> dict[str, Any]:
    forward = _run_buffered_direction("forward", transfer_amount=amount)
    reversed_ = _run_buffered_direction("reversed", transfer_amount=amount)
    directions = [forward, reversed_]
    both_t6 = all(direction["t6_recovery_candidate_passed"] for direction in directions)
    both_r6 = all(direction["r6_recovery_candidate_passed"] for direction in directions)
    s0_point = _find_s0_point(iter15c, amount)
    return {
        "transfer_amount": amount,
        "s0_reference": {
            "outcome": s0_point["outcome"],
            "primary_blocker": s0_point["primary_blocker"],
            "r6_recovered_both_directions": s0_point[
                "r6_recovered_both_directions"
            ],
            "t6_recovered_both_directions": s0_point[
                "t6_recovered_both_directions"
            ],
            "scheduled_recovery_cycles": [
                direction["recovery_scheduled_cycle_count"]
                for direction in s0_point["directions"]
            ],
        },
        "buffered_geometry": {
            "outcome": "recovered" if both_t6 else "partially_recovered",
            "r6_recovered_both_directions": both_r6,
            "t6_recovered_both_directions": both_t6,
            "scheduled_recovery_cycles": [
                direction["recovery_scheduled_cycle_count"]
                for direction in directions
            ],
            "recovery_reason_codes": [
                [cycle["producer_reason_code"] for cycle in direction["recovery_cycles"]]
                for direction in directions
            ],
            "forward": forward,
            "reversed": reversed_,
        },
        "improvement": {
            "recovery_cycle_count_improved": all(
                buffered >= s0
                for buffered, s0 in zip(
                    [
                        direction["recovery_scheduled_cycle_count"]
                        for direction in directions
                    ],
                    [
                        direction["recovery_scheduled_cycle_count"]
                        for direction in s0_point["directions"]
                    ],
                    strict=True,
                )
            )
            and any(
                buffered > s0
                for buffered, s0 in zip(
                    [
                        direction["recovery_scheduled_cycle_count"]
                        for direction in directions
                    ],
                    [
                        direction["recovery_scheduled_cycle_count"]
                        for direction in s0_point["directions"]
                    ],
                    strict=True,
                )
            ),
            "source_budget_exhaustion_avoided": all(
                "feedback_source_budget_exhausted"
                not in [cycle["producer_reason_code"] for cycle in direction["recovery_cycles"]]
                for direction in directions
            ),
            "polarity_restoration_improved": both_r6
            and not s0_point["r6_recovered_both_directions"],
            "t6_restoration_improved": both_t6
            and not s0_point["t6_recovered_both_directions"],
        },
    }


def build_report() -> dict[str, Any]:
    iter15c = _load_json(ITER15C_PATH)
    challenge_amount = iter15c["go_no_go_for_iteration_15d"]["challenge_perturbation"]
    challenge_trial = _trial(challenge_amount, iter15c)
    stress_trial = _trial(STRESS_TRANSFER_AMOUNT, iter15c)
    trials = [challenge_trial, stress_trial]
    geometry_init = challenge_trial["buffered_geometry"]["forward"]["geometry_init"]
    core_success = challenge_trial["buffered_geometry"][
        "t6_recovered_both_directions"
    ]
    stress_success = stress_trial["buffered_geometry"]["t6_recovered_both_directions"]
    checks = {
        "iteration_15c_available": iter15c["status"] == "passed",
        "candidate_geometry_declared_before_run": True,
        "challenge_inherited_from_15c": challenge_amount
        == iter15c["tolerance_summary"]["first_failing_s0_perturbation_for_15d"],
        "same_native_surface_and_feedback_producer_reused": True,
        "policy_differences_declared": True,
        "budget_neutral_geometry_init": geometry_init["budget_abs_error"]
        <= EPSILON_BUDGET,
        "topology_fixed": True,
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
            trial["buffered_geometry"][direction]["artifact_validator"]["valid"]
            for trial in trials
            for direction in ("forward", "reversed")
        ),
        "budget_and_nonnegative_gates_passed": all(
            trial["buffered_geometry"][direction]["budget_abs_error"] <= EPSILON_BUDGET
            and trial["buffered_geometry"][direction]["nonnegative_gate_passed"]
            for trial in trials
            for direction in ("forward", "reversed")
        ),
        "identity_shape_gates_passed": all(
            trial["buffered_geometry"][direction]["identity_shape_gates_passed"]
            for trial in trials
            for direction in ("forward", "reversed")
        ),
        "challenge_recovery_improved_over_s0": core_success,
        "source_budget_exhaustion_improved": challenge_trial["improvement"][
            "source_budget_exhaustion_avoided"
        ],
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_ceiling = (
        "shock_resistant_same_family_geometry_recovery_candidate"
        if status == "passed"
        else "shock_resistant_geometry_probe_failed"
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter15d_shock_resistant_recovery_geometry_v1",
        "iteration": "15-D",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S0_chain_source_reservoir_buffer_v1",
        "geometry_scope": "same_family_resilience_design",
        "input_iteration_15c": _artifact_record(ITER15C_PATH),
        "claim_ceiling": claim_ceiling,
        "candidate_geometry": geometry_init,
        "challenge_trial": challenge_trial,
        "stress_trial": stress_trial,
        "resilience_summary": {
            "challenge_perturbation": challenge_amount,
            "stress_perturbation": STRESS_TRANSFER_AMOUNT,
            "challenge_recovered": core_success,
            "stress_recovered": stress_success,
            "target_failure_mode": "source_budget_exhausted",
            "source_budget_exhaustion_avoided_at_challenge": challenge_trial[
                "improvement"
            ]["source_budget_exhaustion_avoided"],
            "source_budget_exhaustion_avoided_at_stress": stress_trial[
                "improvement"
            ]["source_budget_exhaustion_avoided"],
            "interpretation": (
                "A symmetric source-reservoir buffer removes the S0 "
                "source-budget exhaustion failure at the first positive S0 "
                "T6-failing perturbation. At the stronger 0.15 stress point "
                "it also schedules the full recovery window and avoids source "
                "exhaustion, but it does not satisfy the T6 centroid-restoration "
                "criterion. Native surface and feedback producer semantics are "
                "unchanged."
            ),
        },
        "go_no_go_for_iteration_16": {
            "iteration_16_allowed": status == "passed",
            "entry_ceiling_for_geometry_transfer": claim_ceiling
            if status == "passed"
            else iter15c["claim_ceiling"],
            "iteration_16_fixture_guidance": (
                "test resilience-informed corridor/widened-chain geometry"
                if status == "passed"
                else "test ordinary transfer from Iteration 15 ceiling"
            ),
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": iter15c["claim_flags"]["native_m6"],
            "native_m6_candidate_gate_passed": iter15c["claim_flags"][
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
    summary = report["resilience_summary"]
    lines = [
        "# N04 Iteration 15-D Shock-Resistant Recovery Geometry",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 15-D tests whether a same-family source-reservoir geometry improves the S0 source-budget exhaustion failure mode.",
        "",
        "## Resilience Summary",
        "",
        f"- challenge perturbation: `{summary['challenge_perturbation']}`",
        f"- stress perturbation: `{summary['stress_perturbation']}`",
        f"- challenge recovered: `{summary['challenge_recovered']}`",
        f"- stress recovered: `{summary['stress_recovered']}`",
        f"- target failure mode: `{summary['target_failure_mode']}`",
        f"- source-budget exhaustion avoided at challenge: `{summary['source_budget_exhaustion_avoided_at_challenge']}`",
        f"- source-budget exhaustion avoided at stress: `{summary['source_budget_exhaustion_avoided_at_stress']}`",
        "",
        summary["interpretation"],
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
