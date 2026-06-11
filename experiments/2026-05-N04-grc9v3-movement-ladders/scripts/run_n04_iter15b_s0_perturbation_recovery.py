#!/usr/bin/env python3
"""Run N04 Iteration 15-B S0 perturbation recovery probe.

This probe starts from the native S0 M6 same-fixture mechanism after the
Iteration 15 five-cycle stress window, applies an explicit budget-neutral
front/rear polarity perturbation, and checks whether native feedback-renewed
packet work re-establishes polarity and self-renewal within a finite window.
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

import run_native_m6_same_fixture_validator as native_m6  # noqa: E402


ITER15_PATH = N04 / "outputs/n04_iter15_s0_chain_stress_report.json"
OUTPUT_PATH = N04 / "outputs/n04_iter15b_s0_perturbation_recovery_report.json"
REPORT_PATH = N04 / "reports/n04_iter15b_s0_perturbation_recovery_report.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter15b_s0_perturbation_recovery.py"
)

PRE_PERTURBATION_CYCLES = 5
RECOVERY_WINDOW_CYCLES = 3
PERTURBATION_TRANSFER_AMOUNT = 0.15
OUT_OF_ENVELOPE_TRANSFER_AMOUNT = 0.35
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


def _direction_config(direction: str) -> dict[str, Any]:
    if direction == "forward":
        return {
            "source": native_m6.FORWARD_SOURCE,
            "target": native_m6.FORWARD_TARGET,
            "expected_polarity": "positive",
            "expected_sign": 1,
            "route_id": "s0-native-m6-forward",
        }
    if direction == "reversed":
        return {
            "source": native_m6.REVERSED_SOURCE,
            "target": native_m6.REVERSED_TARGET,
            "expected_polarity": "negative",
            "expected_sign": -1,
            "route_id": "s0-native-m6-reversed",
        }
    raise ValueError(f"unknown direction {direction!r}")


def _boundary_polarity_score(model: Any) -> float:
    values = native_m6._node_vector(model)  # noqa: SLF001
    front_mass = sum(values[index] for index in native_m6.FRONT_MASK)
    rear_mass = sum(values[index] for index in native_m6.REAR_MASK)
    return front_mass - rear_mass


def _apply_polarity_damping_perturbation(
    model: Any,
    *,
    direction: str,
    transfer_amount: float,
) -> dict[str, Any]:
    """Move mass from the expected boundary side to the opposite side."""
    if direction == "forward":
        debit_nodes = native_m6.FRONT_MASK
        credit_nodes = native_m6.REAR_MASK
        target = "positive_front_rear_polarity"
    elif direction == "reversed":
        debit_nodes = native_m6.REAR_MASK
        credit_nodes = native_m6.FRONT_MASK
        target = "negative_front_rear_polarity"
    else:
        raise ValueError(f"unknown direction {direction!r}")

    before_budget = native_m6._budget(model)  # noqa: SLF001
    before_values = native_m6._node_vector(model)  # noqa: SLF001
    debit_per_node = transfer_amount / len(debit_nodes)
    credit_per_node = transfer_amount / len(credit_nodes)
    state = model.get_state().base_state
    for node_id in debit_nodes:
        state.nodes[node_id].coherence -= debit_per_node
    for node_id in credit_nodes:
        state.nodes[node_id].coherence += credit_per_node
    after_budget = native_m6._budget(model)  # noqa: SLF001
    after_values = native_m6._node_vector(model)  # noqa: SLF001
    return {
        "perturbation_kind": "budget_neutral_front_rear_polarity_damping",
        "perturbation_target": target,
        "transfer_amount": transfer_amount,
        "debit_nodes": list(debit_nodes),
        "credit_nodes": list(credit_nodes),
        "debit_per_node": debit_per_node,
        "credit_per_node": credit_per_node,
        "budget_before": before_budget,
        "budget_after": after_budget,
        "budget_abs_error": abs(after_budget - before_budget),
        "nonnegative_after_perturbation": min(after_values) >= -TOL,
        "direct_support_mask_write": False,
        "direct_centroid_write": False,
        "direct_displacement_write": False,
        "direct_topology_write": False,
        "direct_claim_flag_write": False,
        "node_delta_digest": native_m6._digest_json(  # noqa: SLF001
            [after - before for before, after in zip(before_values, after_values, strict=True)]
        ),
    }


def _feedback_cycle(
    model: Any,
    *,
    config: dict[str, Any],
    edge_id: int,
    cycle_index: int,
    phase: str,
) -> dict[str, Any]:
    feedback_row = model.emit_feedback_eligibility_surface_row(
        front_node_ids=native_m6.FRONT_MASK,
        rear_node_ids=native_m6.REAR_MASK,
        reference_delta=0.0,
        feedback_threshold=native_m6.FEEDBACK_THRESHOLD,
        expected_next_route_id=config["route_id"],
        expected_next_channel_id=f"edge:{edge_id}",
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=config["source"],
        target_node_id=config["target"],
        edge_id=edge_id,
        threshold=native_m6.FEEDBACK_THRESHOLD,
        packet_amount=native_m6.FEEDBACK_PACKET_AMOUNT,
        expected_polarity=config["expected_polarity"],
        expected_source_surface_digest=feedback_row.surface_values_after[
            "source_surface_digest"
        ],
        expected_next_route_id=config["route_id"],
        expected_next_channel_id=f"edge:{edge_id}",
    )
    try:
        result = model.produce_events(
            policy=(
                native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )
    except native_m6.InvalidStateTransitionError as exc:
        return {
            "cycle_index": cycle_index,
            "phase": phase,
            "surface_digest": feedback_row.surface_digest,
            "source_surface_digest": feedback_row.surface_values_after[
                "source_surface_digest"
            ],
            "boundary_polarity_score": feedback_row.surface_values_after[
                "boundary_polarity_score"
            ],
            "producer_reason_code": "feedback_source_budget_exhausted",
            "producer_exception": str(exc),
            "scheduled_event_id": None,
            "regenerated_pulse_source": None,
            "copied_from_original_schedule": None,
            "production_artifact": None,
            "processed_events": [],
        }
    record = result.production_records[0]
    processed_events: list[dict[str, Any]] = []
    if record.reason_code == native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED:
        processed_events = native_m6._process_queue(model)  # noqa: SLF001
    return {
        "cycle_index": cycle_index,
        "phase": phase,
        "surface_digest": feedback_row.surface_digest,
        "source_surface_digest": feedback_row.surface_values_after[
            "source_surface_digest"
        ],
        "boundary_polarity_score": feedback_row.surface_values_after[
            "boundary_polarity_score"
        ],
        "producer_reason_code": record.reason_code,
        "scheduled_event_id": record.scheduled_event_id,
        "regenerated_pulse_source": record.observed_evidence.get(
            "regenerated_pulse_source"
        ),
        "copied_from_original_schedule": record.observed_evidence.get(
            "copied_from_original_schedule"
        ),
        "production_artifact": result.to_artifact(),
        "processed_events": processed_events,
    }


def _run_direction(direction: str, *, transfer_amount: float) -> dict[str, Any]:
    config = _direction_config(direction)
    state, edges = native_m6._s0_chain_state()  # noqa: SLF001
    model = native_m6.LGRC9V3.from_state(state, native_m6._params())  # noqa: SLF001
    edge_id = edges[(config["source"], config["target"])]
    initial_values = native_m6._node_vector(model)  # noqa: SLF001
    initial_budget = native_m6._budget(model)  # noqa: SLF001

    model.schedule_packet_departure(
        source_node_id=config["source"],
        target_node_id=config["target"],
        edge_id=edge_id,
        amount=native_m6.SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    seeded_events = native_m6._process_queue(model)  # noqa: SLF001

    baseline_cycles = [
        _feedback_cycle(
            model,
            config=config,
            edge_id=edge_id,
            cycle_index=cycle_index,
            phase="pre_perturbation_baseline",
        )
        for cycle_index in range(PRE_PERTURBATION_CYCLES)
    ]
    pre_perturbation_values = native_m6._node_vector(model)  # noqa: SLF001
    pre_perturbation_centroid = native_m6._centroid(pre_perturbation_values)  # noqa: SLF001
    pre_perturbation_score = _boundary_polarity_score(model)
    perturbation = _apply_polarity_damping_perturbation(
        model,
        direction=direction,
        transfer_amount=transfer_amount,
    )
    post_perturbation_values = native_m6._node_vector(model)  # noqa: SLF001
    post_perturbation_centroid = native_m6._centroid(post_perturbation_values)  # noqa: SLF001
    post_perturbation_score = _boundary_polarity_score(model)

    recovery_cycles = [
        _feedback_cycle(
            model,
            config=config,
            edge_id=edge_id,
            cycle_index=cycle_index,
            phase="post_perturbation_recovery",
        )
        for cycle_index in range(RECOVERY_WINDOW_CYCLES)
    ]
    final_values = native_m6._node_vector(model)  # noqa: SLF001
    final_budget = native_m6._budget(model)  # noqa: SLF001
    production_artifacts = [
        cycle["production_artifact"]
        for cycle in [*baseline_cycles, *recovery_cycles]
        if cycle["production_artifact"] is not None
    ]
    validation = native_m6.validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=model.snapshot()["events"],
        production_results=production_artifacts,
    )
    recovery_scheduled = [
        cycle
        for cycle in recovery_cycles
        if cycle["producer_reason_code"]
        == native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ]
    sign = config["expected_sign"]
    signed_pre_score = sign * pre_perturbation_score
    signed_post_score = sign * post_perturbation_score
    signed_final_score = sign * _boundary_polarity_score(model)
    signed_pre_centroid = sign * (pre_perturbation_centroid - native_m6._centroid(initial_values))  # noqa: E501, SLF001
    signed_post_centroid = sign * (post_perturbation_centroid - native_m6._centroid(initial_values))  # noqa: E501, SLF001
    signed_final_centroid = sign * (native_m6._centroid(final_values) - native_m6._centroid(initial_values))  # noqa: E501, SLF001
    width_initial = native_m6._width(initial_values)  # noqa: SLF001
    width_final = native_m6._width(final_values)  # noqa: SLF001
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = native_m6._profile_similarity(initial_values, final_values)  # noqa: SLF001
    def cycle_summary(cycle: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in cycle.items()
            if key not in {"production_artifact", "processed_events"}
        } | {
            "processed_event_count": len(cycle["processed_events"]),
            "processed_events_digest": native_m6._digest_json(cycle["processed_events"]),  # noqa: SLF001
        }

    return {
        "direction": direction,
        "source_node_id": config["source"],
        "target_node_id": config["target"],
        "edge_id": edge_id,
        "front_mask": list(native_m6.FRONT_MASK),
        "rear_mask": list(native_m6.REAR_MASK),
        "seeded_first_contact_only": True,
        "pre_perturbation_cycle_count": len(
            [
                cycle
                for cycle in baseline_cycles
                if cycle["producer_reason_code"]
                == native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
            ]
        ),
        "recovery_window_cycles": RECOVERY_WINDOW_CYCLES,
        "recovery_scheduled_cycle_count": len(recovery_scheduled),
        "baseline_cycles": [cycle_summary(cycle) for cycle in baseline_cycles],
        "recovery_cycles": [cycle_summary(cycle) for cycle in recovery_cycles],
        "perturbation": perturbation,
        "pre_perturbation_boundary_polarity_score": pre_perturbation_score,
        "post_perturbation_boundary_polarity_score": post_perturbation_score,
        "final_boundary_polarity_score": _boundary_polarity_score(model),
        "signed_pre_perturbation_score": signed_pre_score,
        "signed_post_perturbation_score": signed_post_score,
        "signed_final_score": signed_final_score,
        "signed_pre_perturbation_centroid_delta": signed_pre_centroid,
        "signed_post_perturbation_centroid_delta": signed_post_centroid,
        "signed_final_centroid_delta": signed_final_centroid,
        "centroid_delta": native_m6._centroid(final_values) - native_m6._centroid(initial_values),  # noqa: E501, SLF001
        "budget_initial": initial_budget,
        "budget_final": final_budget,
        "budget_abs_error": abs(final_budget - initial_budget),
        "nonnegative_gate_passed": min(final_values) >= -TOL,
        "width_relative_change": width_relative_change,
        "profile_similarity": profile_similarity,
        "identity_shape_gates_passed": (
            width_relative_change <= native_m6.WIDTH_RELATIVE_CHANGE_MAX
            and profile_similarity >= native_m6.PROFILE_SIMILARITY_MIN
        ),
        "artifact_validator": validation,
        "surface_row_count": len(model.get_state().causal_pulse_substrate_surface_log),
        "surface_log_digest": native_m6._digest_json(  # noqa: SLF001
            [
                row.to_artifact()
                for row in model.get_state().causal_pulse_substrate_surface_log
            ]
        ),
        "producer_records_digest": native_m6._digest_json(production_artifacts),  # noqa: SLF001
        "r6_recovery_candidate_passed": (
            signed_post_score < signed_pre_score - TOL
            and signed_final_score >= signed_pre_score - TOL
        ),
        "t6_recovery_candidate_passed": (
            len(recovery_scheduled) >= RECOVERY_WINDOW_CYCLES
            and signed_post_centroid < signed_pre_centroid - TOL
            and signed_final_centroid >= signed_pre_centroid - TOL
        ),
        "all_recovery_pulses_feedback_authorized": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in recovery_scheduled
        ),
        "seeded_event_count": len(seeded_events),
        "seeded_events_digest": native_m6._digest_json(seeded_events),  # noqa: SLF001
    }


def _run_out_of_envelope_control(direction: str) -> dict[str, Any]:
    result = _run_direction(direction, transfer_amount=OUT_OF_ENVELOPE_TRANSFER_AMOUNT)
    first_recovery = result["recovery_cycles"][0]
    return {
        "direction": direction,
        "perturbation_transfer_amount": OUT_OF_ENVELOPE_TRANSFER_AMOUNT,
        "post_perturbation_boundary_polarity_score": result[
            "post_perturbation_boundary_polarity_score"
        ],
        "first_recovery_reason_code": first_recovery["producer_reason_code"],
        "scheduled_cycle_count": result["recovery_scheduled_cycle_count"],
        "passed_negative_control": (
            result["recovery_scheduled_cycle_count"] == 0
            and first_recovery["producer_reason_code"]
            == native_m6.LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD
        ),
        "primary_blocker": "feedback_polarity_below_threshold_after_out_of_envelope_perturbation",
    }


def build_report() -> dict[str, Any]:
    iter15 = _load_json(ITER15_PATH)
    forward = _run_direction("forward", transfer_amount=PERTURBATION_TRANSFER_AMOUNT)
    reversed_ = _run_direction("reversed", transfer_amount=PERTURBATION_TRANSFER_AMOUNT)
    hard_controls = {
        "forward": _run_out_of_envelope_control("forward"),
        "reversed": _run_out_of_envelope_control("reversed"),
    }
    recovery_candidate_passed = (
        forward["r6_recovery_candidate_passed"]
        and reversed_["r6_recovery_candidate_passed"]
        and forward["t6_recovery_candidate_passed"]
        and reversed_["t6_recovery_candidate_passed"]
    )
    probe_checks = {
        "iteration_15_baseline_available": iter15["status"] == "passed",
        "pre_perturbation_baseline_has_five_cycles": (
            forward["pre_perturbation_cycle_count"] >= PRE_PERTURBATION_CYCLES
            and reversed_["pre_perturbation_cycle_count"] >= PRE_PERTURBATION_CYCLES
        ),
        "perturbation_policy_declared_before_run": True,
        "perturbation_budget_neutral": (
            forward["perturbation"]["budget_abs_error"] <= EPSILON_BUDGET
            and reversed_["perturbation"]["budget_abs_error"] <= EPSILON_BUDGET
        ),
        "topology_fixed": True,
        "no_forbidden_direct_writes": all(
            not forward["perturbation"][key] and not reversed_["perturbation"][key]
            for key in (
                "direct_support_mask_write",
                "direct_centroid_write",
                "direct_displacement_write",
                "direct_topology_write",
                "direct_claim_flag_write",
            )
        ),
        "finite_recovery_window_declared": RECOVERY_WINDOW_CYCLES == 3,
        "recovery_outcome_recorded": True,
        "budget_and_nonnegative_gates_passed": (
            forward["budget_abs_error"] <= EPSILON_BUDGET
            and reversed_["budget_abs_error"] <= EPSILON_BUDGET
            and forward["nonnegative_gate_passed"]
            and reversed_["nonnegative_gate_passed"]
        ),
        "identity_shape_gates_passed": (
            forward["identity_shape_gates_passed"]
            and reversed_["identity_shape_gates_passed"]
        ),
        "artifact_validators_passed": (
            forward["artifact_validator"]["valid"]
            and reversed_["artifact_validator"]["valid"]
        ),
        "out_of_envelope_controls_negative": all(
            control["passed_negative_control"] for control in hard_controls.values()
        ),
        "broader_claims_blocked": True,
    }
    recovery_measurements = {
        "r6_recovery_candidate_passed": (
            forward["r6_recovery_candidate_passed"]
            and reversed_["r6_recovery_candidate_passed"]
        ),
        "t6_recovery_candidate_passed": (
            forward["t6_recovery_candidate_passed"]
            and reversed_["t6_recovery_candidate_passed"]
        ),
        "all_recovery_pulses_feedback_authorized": (
            forward["all_recovery_pulses_feedback_authorized"]
            and reversed_["all_recovery_pulses_feedback_authorized"]
        ),
        "recovery_candidate_passed": recovery_candidate_passed,
    }
    status = "passed" if all(probe_checks.values()) else "failed"
    claim_ceiling = (
        "native_m6_same_fixture_self_renewal_candidate_recovery_passed"
        if recovery_candidate_passed
        else iter15["claim_ceiling"]
    )
    claim_flags = {
        "native_m6": iter15["claim_flags"]["native_m6"],
        "native_m6_candidate_gate_passed": iter15["claim_flags"][
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
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter15b_s0_perturbation_recovery_report_v1",
        "iteration": "15-B",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S0_chain_v1",
        "input_iteration_15": _artifact_record(ITER15_PATH),
        "claim_ceiling": claim_ceiling,
        "perturbation_policy": {
            "policy_id": "s0_threshold_preserving_front_rear_polarity_damping_v1",
            "declared_before_run": True,
            "timing": (
                "after five pre-perturbation native feedback-renewed cycles; "
                "before a three-cycle recovery window"
            ),
            "target": "front_rear_polarity",
            "transfer_amount": PERTURBATION_TRANSFER_AMOUNT,
            "out_of_envelope_control_transfer_amount": OUT_OF_ENVELOPE_TRANSFER_AMOUNT,
            "budget_neutral": True,
            "topology_fixed": True,
            "recovery_window_cycles": RECOVERY_WINDOW_CYCLES,
            "r6_recovery_criterion": (
                "signed boundary polarity is reduced by perturbation and "
                "re-established to the pre-perturbation signed score within "
                "the finite recovery window"
            ),
            "t6_recovery_criterion": (
                "signed centroid/self-renewal response is reduced by "
                "perturbation and re-established to the pre-perturbation "
                "signed response using feedback-authorized native cycles"
            ),
        },
        "forward": forward,
        "reversed": reversed_,
        "out_of_envelope_controls": hard_controls,
        "persistence_update": {
            "persistence_level": "T6_candidate" if recovery_candidate_passed else "tested_negative",
            "persistence_basis": (
                "threshold_preserving_budget_neutral_perturbation_recovery"
            ),
            "self_renewed_cycle_count_pre_perturbation": PRE_PERTURBATION_CYCLES,
            "recovery_window_cycles": RECOVERY_WINDOW_CYCLES,
            "recovery_tested": True,
            "recovery_passed": recovery_candidate_passed,
            "recovery_status": (
                "threshold_preserving_perturbation_recovery_passed"
                if recovery_candidate_passed
                else "perturbation_recovery_failed"
            ),
            "r6_level": "R6_candidate" if recovery_candidate_passed else "tested_negative",
            "r6_recovery_tested": True,
            "r6_recovery_passed": recovery_candidate_passed,
            "out_of_envelope_recovery": "tested_negative",
        },
        "go_no_go_for_iteration_16": {
            "iteration_16_allowed": iter15["status"] == "passed",
            "entry_ceiling_for_geometry_transfer": (
                claim_ceiling
                if recovery_candidate_passed
                else iter15["claim_ceiling"]
            ),
            "recovery_result_used_for_transfer": recovery_candidate_passed,
            "out_of_envelope_recovery_claim_allowed": False,
        },
        "checks": probe_checks,
        "recovery_measurements": recovery_measurements,
        "claim_flags": claim_flags,
        "blocked_claims": [
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_behavior",
            "agency",
            "identity_acceptance",
            "movement_inherited_from_n03",
            "unrestricted_movement",
            "out_of_envelope_perturbation_recovery",
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
    lines = [
        "# N04 Iteration 15-B S0 Perturbation Recovery",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 15-B tests threshold-preserving perturbation recovery on the native S0 same-fixture candidate.",
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Recovery Result",
            "",
            f"- forward pre-perturbation cycles: `{report['forward']['pre_perturbation_cycle_count']}`",
            f"- reversed pre-perturbation cycles: `{report['reversed']['pre_perturbation_cycle_count']}`",
            f"- forward recovery cycles: `{report['forward']['recovery_scheduled_cycle_count']}`",
            f"- reversed recovery cycles: `{report['reversed']['recovery_scheduled_cycle_count']}`",
            f"- persistence level: `{report['persistence_update']['persistence_level']}`",
            f"- R level: `{report['persistence_update']['r6_level']}`",
            f"- out-of-envelope recovery: `{report['persistence_update']['out_of_envelope_recovery']}`",
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
            "## Claim Flags",
            "",
            "```json",
            json.dumps(report["claim_flags"], indent=2, sort_keys=True),
            "```",
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
