#!/usr/bin/env python3
"""Run D2.1 packet loop robustness and conservation audit.

D2.1 hardens the D2 conserved causal packet loop prototype.  It remains
experiment-local prototype evidence: it does not import or modify `src/pygrc`,
and it is not native GRC9V3 loop evidence.

Budget invariant:

    B = sum(node coherence) + sum(in-flight packet coherence)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping, Sequence

import run_d2_conserved_causal_packet_loop as d2  # noqa: E402
from loop_observables import load_json, write_json, write_jsonl  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = EXPERIMENT_ROOT / "configs" / "fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs" / "d2_1_packet_loop_robustness.json"
REPORT_PATH = EXPERIMENT_ROOT / "reports" / "d2_1_packet_loop_robustness.md"
TIMESERIES_DIR = EXPERIMENT_ROOT / "outputs" / "d2_1_packet_loop_robustness_timeseries"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/"
    "scripts/run_d2_1_packet_loop_robustness.py"
)

BUDGET_TOLERANCE = 1e-9
N_CYCLES_MIN = 3


@dataclass(frozen=True)
class Packet:
    packet_id: str
    channel_id: str
    amount: float
    depart_step: int
    arrive_step: int
    parent_packet_id: str | None = None


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else 0.0


def _all_channels() -> dict[str, Mapping[str, Any]]:
    return {**d2.CW_CHANNELS, **d2.CCW_CHANNELS}


def _opposite_direction(direction: str) -> str:
    return "ccw" if direction == "cw" else "cw"


def _behavior_sequence(config: Mapping[str, Any]) -> tuple[str, ...]:
    behavior = str(config.get("behavior_direction", config["direction"]))
    return d2._sequence(behavior)


def _expected_sequence(config: Mapping[str, Any]) -> tuple[str, ...]:
    return d2._sequence(str(config["direction"]))


def _seed_sequence(config: Mapping[str, Any]) -> tuple[str, ...]:
    seed_direction = str(config.get("seed_direction", config.get("behavior_direction", config["direction"])))
    return d2._sequence(seed_direction)


def _next_channel(
    channel_id: str,
    *,
    behavior_sequence: Sequence[str],
    mode: str,
) -> str | None:
    if channel_id not in behavior_sequence:
        return None
    if mode == "forward_only":
        return behavior_sequence[0]
    if mode == "broken_return" and channel_id == behavior_sequence[-2]:
        return None
    if mode == "scrambled_order":
        scrambled = (
            behavior_sequence[0],
            behavior_sequence[2],
            behavior_sequence[1],
            behavior_sequence[3],
        )
        return scrambled[(scrambled.index(channel_id) + 1) % len(scrambled)]
    return behavior_sequence[(behavior_sequence.index(channel_id) + 1) % len(behavior_sequence)]


def _next_delay(config: Mapping[str, Any], *, step_index: int, event_index: int) -> int:
    base_delay = int(config["packet_delay"])
    jitter = tuple(int(value) for value in config.get("delay_jitter", ()))
    if not jitter:
        return max(1, base_delay)
    return max(1, base_delay + jitter[(step_index + event_index) % len(jitter)])


def _packet_budget(packets: Sequence[Packet]) -> float:
    return sum(packet.amount for packet in packets)


def _initial_nodes(config: Mapping[str, Any]) -> dict[int, float]:
    nodes = d2._initial_nodes()
    perturbation = float(config.get("node_perturbation", 0.0))
    if perturbation:
        # Deterministic zero-sum perturbation; keeps the conserved budget fixed.
        nodes[0] += perturbation
        nodes[6] -= perturbation
    return nodes


def _depart(
    nodes: dict[int, float],
    packets: deque[Packet],
    *,
    channel_id: str,
    channels: Mapping[str, Mapping[str, Any]],
    amount: float,
    depart_step: int,
    arrive_step: int,
    parent_packet_id: str | None,
    next_packet_index: int,
    created: dict[str, Packet],
    duplicate_packet_ids: set[str],
) -> int:
    actual = d2._subtract_from_source(
        nodes,
        channel_id=channel_id,
        channels=channels,
        amount=amount,
    )
    if actual <= 0.0:
        return next_packet_index
    packet_id = f"p{next_packet_index:06d}"
    packet = Packet(
        packet_id=packet_id,
        channel_id=channel_id,
        amount=actual,
        depart_step=depart_step,
        arrive_step=arrive_step,
        parent_packet_id=parent_packet_id,
    )
    if packet_id in created:
        duplicate_packet_ids.add(packet_id)
    created[packet_id] = packet
    packets.append(packet)
    return next_packet_index + 1


def _transition_record(
    *,
    packet: Packet,
    next_channel: str | None,
    channels: Mapping[str, Mapping[str, Any]],
    expected_sequence: Sequence[str],
    behavior_sequence: Sequence[str],
) -> dict[str, Any]:
    if next_channel is None:
        canonical_next = None
        behavior_next = None
        handoff_contiguous = True
    else:
        target = channels[packet.channel_id]["target"]
        next_source = channels[next_channel]["source"]
        handoff_contiguous = target == next_source
        canonical_next = (
            expected_sequence[(expected_sequence.index(packet.channel_id) + 1) % len(expected_sequence)]
            if packet.channel_id in expected_sequence
            else None
        )
        behavior_next = (
            behavior_sequence[(behavior_sequence.index(packet.channel_id) + 1) % len(behavior_sequence)]
            if packet.channel_id in behavior_sequence
            else None
        )
    return {
        "packet_id": packet.packet_id,
        "arrived_channel": packet.channel_id,
        "next_channel": next_channel,
        "canonical_next_channel": canonical_next,
        "behavior_next_channel": behavior_next,
        "canonical_transition_valid": next_channel is None or next_channel == canonical_next,
        "declared_transition_valid": next_channel is None or next_channel == behavior_next,
        "handoff_contiguous": handoff_contiguous,
    }


def _row(
    *,
    step_index: int,
    config: Mapping[str, Any],
    nodes_pre: Mapping[int, float],
    nodes_post: Mapping[int, float],
    packets: Sequence[Packet],
    events: Sequence[str],
    packet_events: Sequence[Mapping[str, Any]],
    transitions: Sequence[Mapping[str, Any]],
    flux_uv: Mapping[str, float],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "step_index": step_index,
        "lane_id": str(config["lane_id"]),
        "direction": str(config["direction"]),
        "mode": str(config["mode"]),
        "events": list(events),
        "packet_events": list(packet_events),
        "transitions": list(transitions),
        "flux_uv": dict(flux_uv),
        **d2._loop_metrics(flux_uv),
        "node_budget": d2._node_budget(nodes_post),
        "packet_budget": _packet_budget(packets),
        "in_flight_packet_ids": [packet.packet_id for packet in packets],
    }
    row["total_budget"] = row["node_budget"] + row["packet_budget"]
    for pole_id in d2.POLES:
        row[f"C_{pole_id}_pre"] = d2._pole_mass(nodes_pre, pole_id)
        row[f"C_{pole_id}_post"] = d2._pole_mass(nodes_post, pole_id)
        row[f"delta_{pole_id}"] = row[f"C_{pole_id}_post"] - row[f"C_{pole_id}_pre"]
    return row


def _run_lane(config: Mapping[str, Any], *, total_steps: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    channels = _all_channels()
    expected_sequence = _expected_sequence(config)
    behavior_sequence = _behavior_sequence(config)
    nodes = _initial_nodes(config)
    packets: deque[Packet] = deque()
    rows: list[dict[str, Any]] = []
    created: dict[str, Packet] = {}
    absorbed: set[str] = set()
    duplicate_packet_ids: set[str] = set()
    next_packet_index = 0

    if bool(config.get("seed", True)):
        seed_channel = _seed_sequence(config)[int(config.get("seed_channel_index", 0))]
        next_packet_index = _depart(
            nodes,
            packets,
            channel_id=seed_channel,
            channels=channels,
            amount=float(config["packet_amount"]),
            depart_step=0,
            arrive_step=_next_delay(config, step_index=0, event_index=0),
            parent_packet_id=None,
            next_packet_index=next_packet_index,
            created=created,
            duplicate_packet_ids=duplicate_packet_ids,
        )

    for step_index in range(total_steps):
        nodes_pre = dict(nodes)
        events: list[str] = []
        packet_events: list[dict[str, Any]] = []
        transitions: list[dict[str, Any]] = []
        flux_maps: list[dict[str, float]] = []
        arriving = sorted(
            [packet for packet in packets if packet.arrive_step <= step_index],
            key=lambda packet: packet.packet_id,
        )
        packets = deque(packet for packet in packets if packet.arrive_step > step_index)
        for event_index, packet in enumerate(arriving):
            d2._add_to_target(
                nodes,
                channel_id=packet.channel_id,
                channels=channels,
                amount=packet.amount,
            )
            absorbed.add(packet.packet_id)
            events.append(packet.channel_id)
            packet_events.append(
                {
                    "packet_id": packet.packet_id,
                    "channel_id": packet.channel_id,
                    "amount": packet.amount,
                    "depart_step": packet.depart_step,
                    "arrive_step": packet.arrive_step,
                    "parent_packet_id": packet.parent_packet_id,
                }
            )
            flux_maps.append(
                d2._flux_for_event(
                    packet.channel_id,
                    channels=channels,
                    amount=packet.amount,
                )
            )
            next_channel = _next_channel(
                packet.channel_id,
                behavior_sequence=behavior_sequence,
                mode=str(config["mode"]),
            )
            transitions.append(
                _transition_record(
                    packet=packet,
                    next_channel=next_channel,
                    channels=channels,
                    expected_sequence=expected_sequence,
                    behavior_sequence=behavior_sequence,
                )
            )
            if next_channel is not None:
                next_packet_index = _depart(
                    nodes,
                    packets,
                    channel_id=next_channel,
                    channels=channels,
                    amount=packet.amount,
                    depart_step=step_index,
                    arrive_step=step_index + _next_delay(config, step_index=step_index, event_index=event_index),
                    parent_packet_id=packet.packet_id,
                    next_packet_index=next_packet_index,
                    created=created,
                    duplicate_packet_ids=duplicate_packet_ids,
                )
        rows.append(
            _row(
                step_index=step_index,
                config=config,
                nodes_pre=nodes_pre,
                nodes_post=nodes,
                packets=tuple(packets),
                events=events,
                packet_events=packet_events,
                transitions=transitions,
                flux_uv=d2._merge_flux(flux_maps),
            )
        )

    in_flight_ids = {packet.packet_id for packet in packets}
    unknown_parent_ids = {
        packet.parent_packet_id
        for packet in created.values()
        if packet.parent_packet_id is not None and packet.parent_packet_id not in created
    }
    unknown_channel_ids = {
        packet.channel_id for packet in created.values() if packet.channel_id not in channels
    }
    packet_audit = {
        "packets_created_total": len(created),
        "packets_absorbed_total": len(absorbed),
        "packets_in_flight_total": len(in_flight_ids),
        "packet_balance_error": len(created) - len(absorbed) - len(in_flight_ids),
        "duplicate_packet_ids": sorted(duplicate_packet_ids),
        "orphan_parent_ids": sorted(str(value) for value in unknown_parent_ids),
        "unknown_channel_ids": sorted(unknown_channel_ids),
    }
    return rows, packet_audit


def _summarize_lane(
    config: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    packet_audit: Mapping[str, Any],
) -> dict[str, Any]:
    direction = str(config["direction"])
    expected_sequence = _expected_sequence(config)
    opposite_sequence = d2._sequence(_opposite_direction(direction))
    events = [event for row in rows for event in row["events"]]
    transitions = [transition for row in rows for transition in row["transitions"]]
    budget_errors = [abs(float(row["total_budget"]) - d2.TOTAL_BUDGET) for row in rows]
    cycle_count = d2._cycle_count(events, expected_sequence)
    opposite_cycle_count = d2._cycle_count(events, opposite_sequence)
    max_norm = max((abs(float(row["loop_normalized_circulation"])) for row in rows), default=0.0)
    max_abs = max((abs(float(row["loop_circulation"])) for row in rows), default=0.0)
    packet_budget_seen = max((float(row["packet_budget"]) for row in rows), default=0.0) > 0.0
    budget_passed = max(budget_errors, default=0.0) <= BUDGET_TOLERANCE
    packet_audit_passed = (
        int(packet_audit["packet_balance_error"]) == 0
        and not packet_audit["duplicate_packet_ids"]
        and not packet_audit["orphan_parent_ids"]
        and not packet_audit["unknown_channel_ids"]
    )
    canonical_causality_passed = all(
        bool(transition["canonical_transition_valid"]) and bool(transition["handoff_contiguous"])
        for transition in transitions
    )
    declared_causality_passed = all(
        bool(transition["declared_transition_valid"])
        for transition in transitions
    )
    prototype_positive = (
        cycle_count >= N_CYCLES_MIN
        and budget_passed
        and packet_audit_passed
        and canonical_causality_passed
        and packet_budget_seen
    )
    expected_positive = bool(config["expected_positive"])
    return {
        "lane_id": str(config["lane_id"]),
        "direction": direction,
        "behavior_direction": str(config.get("behavior_direction", direction)),
        "mode": str(config["mode"]),
        "packet_delay": int(config["packet_delay"]),
        "packet_amount": float(config["packet_amount"]),
        "expected_positive": expected_positive,
        "event_count": len(events),
        "cycle_count": cycle_count,
        "opposite_cycle_count": opposite_cycle_count,
        "max_abs_loop_circulation": max_abs,
        "max_abs_normalized_circulation": max_norm,
        "mean_abs_normalized_circulation": _mean(
            [abs(float(row["loop_normalized_circulation"])) for row in rows]
        ),
        "max_budget_error": max(budget_errors, default=0.0),
        "budget_passed": budget_passed,
        "packet_budget_seen": packet_budget_seen,
        "packet_audit_passed": packet_audit_passed,
        "canonical_causality_passed": canonical_causality_passed,
        "declared_causality_passed": declared_causality_passed,
        "prototype_positive": prototype_positive,
        "expectation_passed": prototype_positive is expected_positive,
        "packet_audit": dict(packet_audit),
    }


def _scenario_config() -> list[dict[str, Any]]:
    return [
        {
            "lane_id": "D2.1-U0-no-seed",
            "direction": "cw",
            "seed": False,
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": 0.006,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.1-P-cw-delay-1",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 1,
            "packet_amount": 0.006,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.1-P-cw-delay-3",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": 0.006,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.1-P-cw-delay-6",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 6,
            "packet_amount": 0.006,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.1-R-ccw-delay-3",
            "direction": "ccw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": 0.006,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.1-C-wrong-direction-seed",
            "direction": "cw",
            "behavior_direction": "ccw",
            "seed_direction": "ccw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": 0.006,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.1-C-forward-only",
            "direction": "cw",
            "mode": "forward_only",
            "packet_delay": 3,
            "packet_amount": 0.006,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.1-C-broken-return",
            "direction": "cw",
            "mode": "broken_return",
            "packet_delay": 3,
            "packet_amount": 0.006,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.1-C-scrambled-order",
            "direction": "cw",
            "mode": "scrambled_order",
            "packet_delay": 3,
            "packet_amount": 0.006,
            "expected_positive": False,
        },
        {
            "lane_id": "D2.1-S-weak-seed",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": 0.0005,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.1-S-over-seed",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": 0.02,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.1-N-jittered-delay",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "delay_jitter": (-1, 0, 1),
            "packet_amount": 0.006,
            "expected_positive": True,
        },
        {
            "lane_id": "D2.1-N-node-perturbation",
            "direction": "cw",
            "mode": "closed_loop",
            "packet_delay": 3,
            "packet_amount": 0.006,
            "node_perturbation": 0.01,
            "expected_positive": True,
        },
    ]


def _symmetry_audit(summaries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_id = {str(summary["lane_id"]): summary for summary in summaries}
    cw = by_id["D2.1-P-cw-delay-3"]
    ccw = by_id["D2.1-R-ccw-delay-3"]
    passed = (
        cw["cycle_count"] == ccw["cycle_count"]
        and cw["event_count"] == ccw["event_count"]
        and abs(float(cw["max_budget_error"]) - float(ccw["max_budget_error"])) <= BUDGET_TOLERANCE
        and bool(cw["prototype_positive"])
        and bool(ccw["prototype_positive"])
    )
    return {
        "cw_lane": cw["lane_id"],
        "ccw_lane": ccw["lane_id"],
        "cycle_count_delta": int(cw["cycle_count"]) - int(ccw["cycle_count"]),
        "event_count_delta": int(cw["event_count"]) - int(ccw["event_count"]),
        "max_budget_error_delta": float(cw["max_budget_error"]) - float(ccw["max_budget_error"]),
        "passed": passed,
    }


def _classify(
    summaries: Sequence[Mapping[str, Any]],
    *,
    symmetry: Mapping[str, Any],
) -> str:
    failed_expectations = [row["lane_id"] for row in summaries if not row["expectation_passed"]]
    if failed_expectations:
        return "d2_1_packet_robustness_expectation_failure"
    if not symmetry["passed"]:
        return "d2_1_packet_robustness_symmetry_failure"
    return "d2_1_packet_loop_robustness_passed"


def _write_markdown(result: Mapping[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D2.1 Packet Loop Robustness And Conservation Audit",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{result['status']}`",
        "",
        f"Classification: `{result['classification']}`",
        "",
        "D2.1 hardens the D2 packetized closed-flow prototype. It is",
        "experiment-local packetized prototype evidence, not native GRC9V3",
        "evidence, and it does not open movement claims.",
        "",
        "Budget invariant:",
        "",
        "```text",
        "B = sum(node coherence) + sum(in-flight packet coherence)",
        "```",
        "",
        "## Robustness Checks",
        "",
        f"- direction reversal symmetry: `{result['symmetry_audit']['passed']}`",
        f"- max packet budget error: `{result['max_packet_budget_error']:.6g}`",
        f"- duplicate packet ids: `{result['duplicate_packet_id_count']}`",
        f"- orphan parent ids: `{result['orphan_parent_id_count']}`",
        f"- unknown channel ids: `{result['unknown_channel_id_count']}`",
        "",
        "## Lane Summary",
        "",
        "| Lane | Mode | Direction | Delay | Amount | Events | Cycles | Opposite | Budget | Packet Audit | Causality | Expected | Positive |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in result["lane_summaries"]:
        lines.append(
            "| {lane} | {mode} | {direction} | {delay} | {amount:.6g} | {events} | {cycles} | {opposite} | {budget} | {packet_audit} | {causality} | {expected} | {positive} |".format(
                lane=row["lane_id"],
                mode=row["mode"],
                direction=row["direction"],
                delay=row["packet_delay"],
                amount=row["packet_amount"],
                events=row["event_count"],
                cycles=row["cycle_count"],
                opposite=row["opposite_cycle_count"],
                budget="pass" if row["budget_passed"] else "fail",
                packet_audit="pass" if row["packet_audit_passed"] else "fail",
                causality="pass" if row["canonical_causality_passed"] else "fail",
                expected="positive" if row["expected_positive"] else "negative",
                positive="yes" if row["prototype_positive"] else "no",
            )
        )
    lines.extend(["", "## Interpretation", "", result["interpretation"], "", "## Errors", ""])
    if result["errors"]:
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- none")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    total_steps = int(manifest["runner_config"]["total_steps"])
    lane_summaries: list[dict[str, Any]] = []
    errors: list[str] = []

    for config in _scenario_config():
        rows, packet_audit = _run_lane(config, total_steps=total_steps)
        lane_id = str(config["lane_id"])
        path = TIMESERIES_DIR / f"{lane_id.lower().replace('.', '_').replace('-', '_')}_timeseries.jsonl"
        write_jsonl(path, rows)
        summary = _summarize_lane(config, rows, packet_audit)
        summary["timeseries_path"] = str(path)
        lane_summaries.append(summary)
        if not summary["budget_passed"]:
            errors.append(f"{lane_id} failed budget")
        if not summary["packet_audit_passed"]:
            errors.append(f"{lane_id} failed packet audit")
        if not summary["expectation_passed"]:
            errors.append(f"{lane_id} failed expectation")

    symmetry = _symmetry_audit(lane_summaries)
    if not symmetry["passed"]:
        errors.append("direction reversal symmetry failed")

    classification = _classify(lane_summaries, symmetry=symmetry)
    positive_rows = [row["lane_id"] for row in lane_summaries if row["prototype_positive"]]
    max_packet_budget_error = max(
        (float(row["max_budget_error"]) for row in lane_summaries),
        default=0.0,
    )
    duplicate_packet_id_count = sum(
        len(row["packet_audit"]["duplicate_packet_ids"]) for row in lane_summaries
    )
    orphan_parent_id_count = sum(
        len(row["packet_audit"]["orphan_parent_ids"]) for row in lane_summaries
    )
    unknown_channel_id_count = sum(
        len(row["packet_audit"]["unknown_channel_ids"]) for row in lane_summaries
    )
    interpretation = (
        "D2.1 confirms whether the D2 packetized prototype survives robustness "
        "checks: exact node-plus-packet budget accounting, packet-id loss/"
        "duplication audit, declared channel causality, direction reversal "
        "symmetry, seed dependence controls, delay sweep, and deterministic "
        "small perturbations. Positive rows remain packetized prototype "
        "evidence only; native GRC9V3 and movement claims remain blocked."
    )
    result = {
        "schema": "grc9v3_polarized_basin_loop_d2_1_packet_loop_robustness_v1",
        "experiment_id": manifest["experiment_id"],
        "status": "pass" if not errors else "fail",
        "command": COMMAND,
        "native_evidence": False,
        "positive_loop_claim_allowed": False,
        "budget_invariant": "node_coherence + in_flight_packet_coherence",
        "classification": classification,
        "n_cycles_min": N_CYCLES_MIN,
        "positive_rows": positive_rows,
        "symmetry_audit": symmetry,
        "max_packet_budget_error": max_packet_budget_error,
        "duplicate_packet_id_count": duplicate_packet_id_count,
        "orphan_parent_id_count": orphan_parent_id_count,
        "unknown_channel_id_count": unknown_channel_id_count,
        "lane_summaries": lane_summaries,
        "interpretation": interpretation,
        "errors": errors,
    }
    write_json(OUTPUT_PATH, result)
    _write_markdown(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "classification": classification,
                "positive_rows": positive_rows,
                "symmetry_passed": symmetry["passed"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
