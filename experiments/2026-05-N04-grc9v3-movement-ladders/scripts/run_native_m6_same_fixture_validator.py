#!/usr/bin/env python3
"""Run a native same-fixture M6 validator for N04.

This validator uses the native LGRC9V3 causal pulse-substrate surface and
feedback producer on the S0 chain. It starts with one seeded packet contact,
then requires later pulse work to be authorized by native feedback eligibility
surface rows and scheduled by the native feedback producer.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygrc.core import InvalidStateTransitionError, PortGraphBackend  # noqa: E402
from pygrc.models import (  # noqa: E402
    CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3NodeState,
    GRC9V3State,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC2,
    LGRC9V3,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC9V3_PACKET_STATE_IN_FLIGHT,
    PortEdge,
    validate_lgrc9v3_causal_pulse_substrate_surface_artifacts,
)


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
OUTPUT_PATH = N04 / "outputs/native_m6_same_fixture_validator.json"
REPORT_PATH = N04 / "reports/native_m6_same_fixture_validator.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_native_m6_same_fixture_validator.py"
)

NODE_COUNT = 21
FORWARD_SOURCE = 12
FORWARD_TARGET = 13
REVERSED_SOURCE = 8
REVERSED_TARGET = 7
FRONT_MASK = (13, 14)
REAR_MASK = (6, 7)
SEED_AMOUNT = 0.25
FEEDBACK_PACKET_AMOUNT = 0.10
FEEDBACK_THRESHOLD = 0.20
SELF_RENEWED_CYCLE_MIN = 3
WIDTH_RELATIVE_CHANGE_MAX = 0.15
PROFILE_SIMILARITY_MIN = 0.8
TOL = 1e-12


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _digest_json(data: Any) -> str:
    return _sha256_bytes(
        json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


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


def _s0_chain_state() -> tuple[GRC9V3State, dict[tuple[int, int], int]]:
    graph = PortGraphBackend()
    node_ids = [graph.add_node({"label": f"s0:{index}"}) for index in range(NODE_COUNT)]
    edge_by_pair: dict[tuple[int, int], int] = {}
    port_edges: dict[int, PortEdge] = {}
    base_conductance: dict[int, float] = {}
    geometric_length: dict[int, float] = {}
    temporal_delay: dict[int, float] = {}
    flux_coupling: dict[int, float] = {}

    for index in range(NODE_COUNT - 1):
        edge_id = graph.connect_ports(
            node_ids[index],
            1,
            node_ids[index + 1],
            0,
            {"kind": "s0_chain_edge", "source_index": index},
        )
        edge_by_pair[(index, index + 1)] = edge_id
        edge_by_pair[(index + 1, index)] = edge_id
        port_edges[edge_id] = PortEdge(
            node_ids[index],
            1,
            node_ids[index + 1],
            1,
            conductance=1.0,
            flux_uv=0.0,
        )
        base_conductance[edge_id] = 1.0
        geometric_length[edge_id] = 1.0
        temporal_delay[edge_id] = 1.0
        flux_coupling[edge_id] = 0.0

    nodes = {
        node_id: GRC9V3NodeState(coherence=1.0)
        for node_id in node_ids
    }
    return (
        GRC9V3State(
            topology=graph,
            nodes=nodes,
            port_edges=port_edges,
            base_conductance=base_conductance,
            geometric_length=geometric_length,
            temporal_delay=temporal_delay,
            flux_coupling=flux_coupling,
        ),
        edge_by_pair,
    )


def _params() -> dict[str, Any]:
    return {
        "dt": 1.0,
        "causal_modes": {
            "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "explicit_event_time_key",
            "proper_time_accumulation_policy": "local_event_frontier",
            "causal_pulse_substrate_surface_enabled": True,
            "causal_pulse_substrate_surface_policy": (
                LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
            ),
            "causal_pulse_substrate_surface_validated": True,
        },
    }


def _node_vector(model: LGRC9V3) -> list[float]:
    state = model.get_state().base_state
    return [float(state.nodes[index].coherence) for index in range(NODE_COUNT)]


def _centroid(values: list[float]) -> float:
    total = sum(values)
    return sum(index * value for index, value in enumerate(values)) / total


def _width(values: list[float]) -> float:
    center = _centroid(values)
    total = sum(values)
    variance = sum(((index - center) ** 2) * value for index, value in enumerate(values))
    return math.sqrt(variance / total)


def _profile_similarity(before: list[float], after: list[float]) -> float:
    dot = sum(a * b for a, b in zip(before, after, strict=True))
    norm_a = math.sqrt(sum(a * a for a in before))
    norm_b = math.sqrt(sum(b * b for b in after))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _budget(model: LGRC9V3) -> float:
    state = model.get_state()
    node_budget = sum(float(node.coherence) for node in state.base_state.nodes.values())
    packet_budget = 0.0
    ledger = state.packet_ledger
    if ledger is not None:
        packet_budget = sum(
            float(packet.amount)
            for packet in ledger.packet_records
            if packet.packet_state == LGRC9V3_PACKET_STATE_IN_FLIGHT
        )
    return node_budget + packet_budget


def _process_queue(model: LGRC9V3) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        events.extend(
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "source_family": event.source_family,
                "payload": dict(event.payload),
            }
            for event in result.events
        )
    return events


def _latest_feedback_row(model: LGRC9V3) -> Any:
    return model.get_state().causal_pulse_substrate_surface_log[-1]


def _run_direction(direction: str) -> dict[str, Any]:
    if direction == "forward":
        source = FORWARD_SOURCE
        target = FORWARD_TARGET
        expected_polarity = "positive"
        expected_sign = 1
    elif direction == "reversed":
        source = REVERSED_SOURCE
        target = REVERSED_TARGET
        expected_polarity = "negative"
        expected_sign = -1
    else:
        raise ValueError(f"unknown direction {direction!r}")

    state, edges = _s0_chain_state()
    model = LGRC9V3.from_state(state, _params())
    edge_id = edges[(source, target)]
    initial_values = _node_vector(model)
    initial_budget = _budget(model)
    events: list[dict[str, Any]] = []
    production_artifacts: list[dict[str, Any]] = []
    cycles: list[dict[str, Any]] = []

    model.schedule_packet_departure(
        source_node_id=source,
        target_node_id=target,
        edge_id=edge_id,
        amount=SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    events.extend(_process_queue(model))

    for cycle_index in range(SELF_RENEWED_CYCLE_MIN):
        feedback_row = model.emit_feedback_eligibility_surface_row(
            front_node_ids=FRONT_MASK,
            rear_node_ids=REAR_MASK,
            reference_delta=0.0,
            feedback_threshold=FEEDBACK_THRESHOLD,
            expected_next_route_id=f"s0-native-m6-{direction}",
            expected_next_channel_id=f"edge:{edge_id}",
        )
        model.set_feedback_coupled_pulse_producer(
            source_node_id=source,
            target_node_id=target,
            edge_id=edge_id,
            threshold=FEEDBACK_THRESHOLD,
            packet_amount=FEEDBACK_PACKET_AMOUNT,
            expected_polarity=expected_polarity,
            expected_source_surface_digest=feedback_row.surface_values_after[
                "source_surface_digest"
            ],
            expected_next_route_id=f"s0-native-m6-{direction}",
            expected_next_channel_id=f"edge:{edge_id}",
        )
        result = model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )
        production_artifacts.append(result.to_artifact())
        record = result.production_records[0]
        if record.reason_code == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED:
            events.extend(_process_queue(model))
        cycles.append(
            {
                "cycle_index": cycle_index,
                "surface_digest": feedback_row.surface_digest,
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
            }
        )

    final_values = _node_vector(model)
    final_budget = _budget(model)
    validation = validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(
        events=model.snapshot()["events"],
        production_results=production_artifacts,
    )
    scheduled_cycles = [
        cycle
        for cycle in cycles
        if cycle["producer_reason_code"]
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
    ]
    centroid_delta = _centroid(final_values) - _centroid(initial_values)
    width_initial = _width(initial_values)
    width_final = _width(final_values)
    width_relative_change = (
        abs(width_final - width_initial) / width_initial if width_initial else 0.0
    )
    profile_similarity = _profile_similarity(initial_values, final_values)
    nonnegative = all(value >= -TOL for value in final_values)
    return {
        "direction": direction,
        "source_node_id": source,
        "target_node_id": target,
        "edge_id": edge_id,
        "front_mask": list(FRONT_MASK),
        "rear_mask": list(REAR_MASK),
        "seeded_first_response_required": True,
        "self_renewed_cycle_count": len(scheduled_cycles),
        "cycles": cycles,
        "centroid_delta": centroid_delta,
        "centroid_sign_passed": centroid_delta * expected_sign > 0.0,
        "budget_initial": initial_budget,
        "budget_final": final_budget,
        "budget_abs_error": abs(final_budget - initial_budget),
        "nonnegative_gate_passed": nonnegative,
        "width_initial": width_initial,
        "width_final": width_final,
        "width_relative_change": width_relative_change,
        "profile_similarity": profile_similarity,
        "identity_shape_gates_passed": (
            nonnegative
            and width_relative_change <= WIDTH_RELATIVE_CHANGE_MAX
            and profile_similarity >= PROFILE_SIMILARITY_MIN
        ),
        "artifact_validator": validation,
        "surface_row_count": len(model.get_state().causal_pulse_substrate_surface_log),
        "event_count": len(events),
        "surface_log_digest": _digest_json(
            [
                row.to_artifact()
                for row in model.get_state().causal_pulse_substrate_surface_log
            ]
        ),
        "producer_records_digest": _digest_json(production_artifacts),
    }


def _run_controls() -> dict[str, Any]:
    state, edges = _s0_chain_state()
    model = LGRC9V3.from_state(state, _params())
    pulse_disabled_passed = False
    try:
        model.emit_feedback_eligibility_surface_row(
            front_node_ids=FRONT_MASK,
            rear_node_ids=REAR_MASK,
            feedback_threshold=FEEDBACK_THRESHOLD,
        )
    except InvalidStateTransitionError:
        pulse_disabled_passed = True

    model.schedule_packet_departure(
        source_node_id=FORWARD_SOURCE,
        target_node_id=FORWARD_TARGET,
        edge_id=edges[(FORWARD_SOURCE, FORWARD_TARGET)],
        amount=SEED_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    _process_queue(model)
    feedback_row = model.emit_feedback_eligibility_surface_row(
        front_node_ids=FRONT_MASK,
        rear_node_ids=REAR_MASK,
        feedback_threshold=FEEDBACK_THRESHOLD,
    )

    model.set_feedback_coupled_pulse_producer(
        source_node_id=FORWARD_SOURCE,
        target_node_id=FORWARD_TARGET,
        edge_id=edges[(FORWARD_SOURCE, FORWARD_TARGET)],
        threshold=FEEDBACK_THRESHOLD,
        packet_amount=FEEDBACK_PACKET_AMOUNT,
        expected_source_surface_digest=feedback_row.surface_values_after[
            "source_surface_digest"
        ],
        enabled=False,
    )
    disabled = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )

    model.set_feedback_coupled_pulse_producer(
        source_node_id=FORWARD_SOURCE,
        target_node_id=FORWARD_TARGET,
        edge_id=edges[(FORWARD_SOURCE, FORWARD_TARGET)],
        threshold=10.0,
        packet_amount=FEEDBACK_PACKET_AMOUNT,
        expected_source_surface_digest=feedback_row.surface_values_after[
            "source_surface_digest"
        ],
    )
    subthreshold = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )

    model.set_feedback_coupled_pulse_producer(
        source_node_id=FORWARD_SOURCE,
        target_node_id=FORWARD_TARGET,
        edge_id=edges[(FORWARD_SOURCE, FORWARD_TARGET)],
        threshold=FEEDBACK_THRESHOLD,
        packet_amount=FEEDBACK_PACKET_AMOUNT,
        expected_polarity="negative",
        expected_source_surface_digest=feedback_row.surface_values_after[
            "source_surface_digest"
        ],
    )
    wrong_polarity = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
    )

    budget_violation_passed = False
    try:
        model.set_feedback_coupled_pulse_producer(
            source_node_id=FORWARD_SOURCE,
            target_node_id=FORWARD_TARGET,
            edge_id=edges[(FORWARD_SOURCE, FORWARD_TARGET)],
            threshold=FEEDBACK_THRESHOLD,
            packet_amount=10_000.0,
            expected_source_surface_digest=feedback_row.surface_values_after[
                "source_surface_digest"
            ],
        )
        model.produce_events(
            policy=(
                LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FEEDBACK_ELIGIBILITY
            )
        )
    except InvalidStateTransitionError:
        budget_violation_passed = True

    return {
        "pulse_disabled": {
            "passed": pulse_disabled_passed,
            "primary_blocker": "feedback_surface_requires_committed_pulse_contact",
        },
        "feedback_disabled": {
            "passed": len(disabled.production_records) == 1
            and disabled.production_records[0].reason_code != (
                LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SCHEDULED
            ),
            "reason_code": disabled.production_records[0].reason_code,
        },
        "subthreshold": {
            "passed": subthreshold.production_records[0].reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_SUBTHRESHOLD,
            "reason_code": subthreshold.production_records[0].reason_code,
        },
        "wrong_polarity": {
            "passed": wrong_polarity.production_records[0].reason_code
            == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_FEEDBACK_WRONG_POLARITY,
            "reason_code": wrong_polarity.production_records[0].reason_code,
        },
        "budget_violation": {
            "passed": budget_violation_passed,
            "primary_blocker": "budget_surface_gate_failed",
        },
    }


def _build_report() -> dict[str, Any]:
    forward = _run_direction("forward")
    reversed_ = _run_direction("reversed")
    controls = _run_controls()
    direction_parity = (
        forward["centroid_delta"] > 0.0
        and reversed_["centroid_delta"] < 0.0
        and abs(abs(forward["centroid_delta"]) - abs(reversed_["centroid_delta"]))
        <= 1e-9
    )
    gates = {
        "native_same_fixture_validator_available": True,
        "forward_self_renewed_cycles_passed": (
            forward["self_renewed_cycle_count"] >= SELF_RENEWED_CYCLE_MIN
        ),
        "reversed_self_renewed_cycles_passed": (
            reversed_["self_renewed_cycle_count"] >= SELF_RENEWED_CYCLE_MIN
        ),
        "native_repeated_self_renewed_cycles_measured": True,
        "movement_restores_pulse_conditions": all(
            cycle["regenerated_pulse_source"] == "feedback_eligibility"
            and cycle["copied_from_original_schedule"] is False
            for cycle in [*forward["cycles"], *reversed_["cycles"]]
        ),
        "polarity_regeneration_measured": direction_parity,
        "artifact_only_validation_passed": (
            forward["artifact_validator"]["valid"]
            and reversed_["artifact_validator"]["valid"]
        ),
        "budget_gate_passed": (
            forward["budget_abs_error"] <= TOL and reversed_["budget_abs_error"] <= TOL
        ),
        "nonnegative_gate_passed": (
            forward["nonnegative_gate_passed"] and reversed_["nonnegative_gate_passed"]
        ),
        "identity_shape_gates_integrated": (
            forward["identity_shape_gates_passed"]
            and reversed_["identity_shape_gates_passed"]
        ),
        "controls_negative": all(control["passed"] for control in controls.values()),
        "topology_fixed": True,
    }
    native_m6_candidate_gate_passed = all(gates.values())
    claim_flags = {
        "native_m6": native_m6_candidate_gate_passed,
        "native_m6_candidate_gate_passed": native_m6_candidate_gate_passed,
        "movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "biological_claim_allowed": False,
        "agency_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "movement_claim_inherited_from_n03": False,
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "native_m6_same_fixture_validator_v1",
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S0_chain_v1",
        "status": "passed" if native_m6_candidate_gate_passed else "failed",
        "claim_ceiling": (
            "native_m6_same_fixture_self_renewal_candidate"
            if native_m6_candidate_gate_passed
            else "native_m6_same_fixture_validator_failed"
        ),
        "native_m6_candidate_gate_passed": native_m6_candidate_gate_passed,
        "gates": gates,
        "forward": forward,
        "reversed": reversed_,
        "direction_parity": {
            "passed": direction_parity,
            "forward_centroid_delta": forward["centroid_delta"],
            "reversed_centroid_delta": reversed_["centroid_delta"],
        },
        "controls": controls,
        "claim_flags": claim_flags,
        "blocked_claims": [
            "unrestricted_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_behavior",
            "agency",
            "identity_acceptance",
            "movement_inherited_from_n03",
        ],
        "interpretation": (
            "Native LGRC9V3 now supports a same-fixture M6 self-renewal "
            "candidate on S0: after one seeded packet contact, native feedback "
            "eligibility rows authorize regenerated packet work through the "
            "native feedback producer for both forward and reversed boundary "
            "polarity. This remains a bounded M6 candidate, not locomotion, "
            "agency, biology, adaptive topology, or unrestricted movement."
        ),
        "environment": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "rev_parse_head": _run_git(["rev-parse", "HEAD"]),
            "diff_check": _run_git(["diff", "--check"]),
            "status_short": _run_git(["status", "--short"]),
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# N04 Native M6 Same-Fixture Validator",
        "",
        f"Status: `{payload['status']}`",
        f"Claim ceiling: `{payload['claim_ceiling']}`",
        "",
        "## Result",
        "",
        payload["interpretation"],
        "",
        "## Gates",
        "",
    ]
    for key, value in payload["gates"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Direction Parity",
            "",
            f"- forward dX: `{payload['direction_parity']['forward_centroid_delta']}`",
            f"- reversed dX: `{payload['direction_parity']['reversed_centroid_delta']}`",
            f"- passed: `{payload['direction_parity']['passed']}`",
            "",
            "## Self-Renewed Cycles",
            "",
            f"- forward: `{payload['forward']['self_renewed_cycle_count']}`",
            f"- reversed: `{payload['reversed']['self_renewed_cycle_count']}`",
            "",
            "## Controls",
            "",
        ]
    )
    for key, value in payload["controls"].items():
        lines.append(
            f"- {key}: passed=`{value['passed']}`, "
            f"reason=`{value.get('reason_code', value.get('primary_blocker'))}`"
        )
    lines.extend(
        [
            "",
            "## Claim Flags",
            "",
            "```json",
            json.dumps(payload["claim_flags"], indent=2, sort_keys=True),
            "```",
            "",
            "Command:",
            "",
            "```bash",
            COMMAND,
            "```",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = _build_report()
    _write_json(OUTPUT_PATH, report)
    _write_report(REPORT_PATH, report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "claim_ceiling": report["claim_ceiling"],
                "native_m6_candidate_gate_passed": report[
                    "native_m6_candidate_gate_passed"
                ],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
