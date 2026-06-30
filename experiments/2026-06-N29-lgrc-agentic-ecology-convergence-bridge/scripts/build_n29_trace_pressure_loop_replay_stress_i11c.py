#!/usr/bin/env python3
"""Build N29 Iteration 11-C trace / pressure / loop replay and stress matrix."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from pygrc.core import PortGraphBackend
from pygrc.models import (
    GRC9V3NodeState,
    GRC9V3State,
    LGRC9V3,
    LGRC9V3RouteAspect,
    LGRC9V3RouteAspectChannel,
    LGRC9V3RouteAspectHop,
    PortEdge,
    validate_lgrc9v3_self_rearm_evidence_artifacts,
)
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
)


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
I11_OUTPUT = EXPERIMENT / "outputs" / "n29_trace_pressure_loop_prototype_i11.json"
I11A_OUTPUT = EXPERIMENT / "outputs" / "n29_trace_pressure_loop_runtime_i11a.json"
I11A_RUNTIME = (
    EXPERIMENT / "outputs" / "n29_trace_pressure_loop_runtime_i11a_runtime_artifact.json"
)
I11B_OUTPUT = EXPERIMENT / "outputs" / "n29_trace_pressure_loop_runtime_controls_i11b.json"
SNAPSHOT_OUTPUT = (
    EXPERIMENT / "outputs" / "n29_trace_pressure_loop_replay_stress_i11c_snapshot.json"
)
OUTPUT = EXPERIMENT / "outputs" / "n29_trace_pressure_loop_replay_stress_i11c.json"
REPORT = EXPERIMENT / "reports" / "n29_trace_pressure_loop_replay_stress_i11c.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_trace_pressure_loop_replay_stress_i11c.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"
POLICY = LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": passed}
    if details is not None:
        row["details"] = details
    return row


def build_state() -> GRC9V3State:
    graph = PortGraphBackend()
    source = graph.add_node({"label": "source_pole"})
    sink = graph.add_node({"label": "sink_pole"})
    edge_forward = graph.connect_ports(source, 0, sink, 0, {"kind": "forward"})
    edge_return = graph.connect_ports(sink, 1, source, 1, {"kind": "return"})
    return GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(coherence=2.0),
            sink: GRC9V3NodeState(coherence=1.0),
        },
        port_edges={
            edge_forward: PortEdge(source, 1, sink, 1, conductance=1.0, flux_uv=0.0),
            edge_return: PortEdge(sink, 2, source, 2, conductance=1.0, flux_uv=0.0),
        },
        base_conductance={edge_forward: 1.0, edge_return: 1.0},
        geometric_length={edge_forward: 1.0, edge_return: 1.0},
        temporal_delay={edge_forward: 1.0, edge_return: 1.0},
        flux_coupling={edge_forward: 0.0, edge_return: 0.0},
    )


def build_route_aspect() -> LGRC9V3RouteAspect:
    return LGRC9V3RouteAspect(
        route_aspect_id="n29_i11a_two_pole_trace_pressure_loop",
        direction="clockwise",
        pole_regions={"S": (0,), "K": (1,)},
        channels=(
            LGRC9V3RouteAspectChannel(
                channel_id="S_to_K",
                source_pole_id="S",
                target_pole_id="K",
                expected_next_channel_id="K_to_S",
                route_hops=(
                    LGRC9V3RouteAspectHop(source_node_id=0, target_node_id=1, edge_id=0),
                ),
            ),
            LGRC9V3RouteAspectChannel(
                channel_id="K_to_S",
                source_pole_id="K",
                target_pole_id="S",
                expected_next_channel_id="S_to_K",
                route_hops=(
                    LGRC9V3RouteAspectHop(source_node_id=1, target_node_id=0, edge_id=1),
                ),
            ),
        ),
        channel_sequence=("S_to_K", "K_to_S"),
    )


def configure_trigger(
    model: LGRC9V3,
    *,
    route_aspect: LGRC9V3RouteAspect,
    source_pole_id: str,
    reference_mass: float,
    eligible_channel_id: str,
    packet_amount: float = 0.1,
) -> None:
    model.set_route_aspect_surplus_trigger(
        route_aspect=route_aspect,
        source_pole_id=source_pole_id,
        reference_mass=reference_mass,
        trigger_threshold=0.049,
        packet_amount=packet_amount,
        eligible_channel_id=eligible_channel_id,
    )


def seed_parent_return(model: LGRC9V3) -> None:
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=0,
        edge_id=1,
        amount=0.25,
        departure_event_time_key=0.0,
        arrival_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.run_event_queue(max_events=2)


def production_record_count(producer_results: list[dict[str, Any]]) -> int:
    return sum(int(result.get("record_count", 0)) for result in producer_results)


def scheduled_event_count(producer_results: list[dict[str, Any]]) -> int:
    return sum(int(result.get("scheduled_event_count", 0)) for result in producer_results)


def validate_runtime(
    model: LGRC9V3,
    producer_results: list[dict[str, Any]],
) -> dict[str, Any]:
    snapshot = model.snapshot()
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=snapshot["events"],
        production_results=tuple(producer_results),
    )
    return {
        "event_count": len(snapshot["events"]),
        "producer_result_count": len(producer_results),
        "production_record_count": production_record_count(producer_results),
        "scheduled_event_count": scheduled_event_count(producer_results),
        "candidate_count": validation["candidate_count"],
        "completed_count": validation["completed_count"],
        "valid": validation["valid"],
        "failure_reasons": validation["failure_reasons"],
    }


def produce_and_process(
    model: LGRC9V3,
    *,
    route_aspect: LGRC9V3RouteAspect,
    source_pole_id: str,
    reference_mass: float,
    eligible_channel_id: str,
    packet_amount: float = 0.1,
    steps: int = 2,
) -> dict[str, Any]:
    configure_trigger(
        model,
        route_aspect=route_aspect,
        source_pole_id=source_pole_id,
        reference_mass=reference_mass,
        eligible_channel_id=eligible_channel_id,
        packet_amount=packet_amount,
    )
    produced = model.produce_events(policy=POLICY).to_artifact()
    for _ in range(steps):
        model.step()
    return produced


def run_two_cycle_probe() -> dict[str, Any]:
    model = LGRC9V3.from_state(build_state(), {"dt": 1.0})
    route_aspect = build_route_aspect()
    producer_results: list[dict[str, Any]] = []
    seed_parent_return(model)
    for _cycle in range(2):
        producer_results.append(
            produce_and_process(
                model,
                route_aspect=route_aspect,
                source_pole_id="S",
                reference_mass=2.15,
                eligible_channel_id="S_to_K",
            )
        )
        producer_results.append(
            produce_and_process(
                model,
                route_aspect=route_aspect,
                source_pole_id="K",
                reference_mass=0.75,
                eligible_channel_id="K_to_S",
            )
        )
    summary = validate_runtime(model, producer_results)
    snapshot = model.snapshot()
    normalized = {
        "route_aspect_digest": route_aspect.route_aspect_digest,
        "completed_count": summary["completed_count"],
        "scheduled_event_count": summary["scheduled_event_count"],
        "producer_result_count": summary["producer_result_count"],
        "event_kinds": sorted({event["kind"] for event in snapshot["events"]}),
        "validation_valid": summary["valid"],
    }
    summary["normalized_digest"] = digest_value(normalized)
    summary["normalized_summary"] = normalized
    return summary


def artifact_replay(i11a: dict[str, Any], i11a_runtime: dict[str, Any]) -> dict[str, Any]:
    embedded_valid = bool(i11a_runtime["self_rearm_validation"]["valid"])
    leg_count = len(i11a_runtime["trace_pressure_loop_leg_records"])
    manifest_digest_matches = (
        i11a["runtime_artifact_manifest"]["output_digest"]
        == i11a_runtime["output_digest"]
    )
    return {
        "replay_id": "artifact_replay",
        "status": "stable",
        "embedded_self_rearm_validation_valid": embedded_valid,
        "embedded_leg_count": leg_count,
        "manifest_digest_matches_runtime_artifact": manifest_digest_matches,
        "raw_event_revalidation_available": False,
        "raw_event_revalidation_note": (
            "I11-A stores validated leg records and producer artifacts, but not "
            "the full raw event log as a standalone output artifact."
        ),
        "passed": embedded_valid and leg_count >= 2 and manifest_digest_matches,
    }


def snapshot_load_replay() -> dict[str, Any]:
    route_aspect = build_route_aspect()
    model = LGRC9V3.from_state(build_state(), {"dt": 1.0})
    producer_results: list[dict[str, Any]] = []
    seed_parent_return(model)
    producer_results.append(
        produce_and_process(
            model,
            route_aspect=route_aspect,
            source_pole_id="S",
            reference_mass=2.15,
            eligible_channel_id="S_to_K",
        )
    )
    model.save(str(SNAPSHOT_OUTPUT))
    loaded = LGRC9V3.load(str(SNAPSHOT_OUTPUT))
    producer_results.append(
        produce_and_process(
            loaded,
            route_aspect=route_aspect,
            source_pole_id="K",
            reference_mass=0.75,
            eligible_channel_id="K_to_S",
        )
    )
    summary = validate_runtime(loaded, producer_results)
    summary.update(
        {
            "replay_id": "snapshot_load_replay",
            "status": "stable" if summary["valid"] and summary["completed_count"] == 2 else "blocked",
            "snapshot_artifact": (
                "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                "outputs/n29_trace_pressure_loop_replay_stress_i11c_snapshot.json"
            ),
            "snapshot_sha256": sha256_file(SNAPSHOT_OUTPUT),
            "continued_after_load": True,
            "passed": summary["valid"] and summary["completed_count"] == 2,
        }
    )
    return summary


def duplicate_replay() -> dict[str, Any]:
    first = run_two_cycle_probe()
    second = run_two_cycle_probe()
    stable = first["normalized_digest"] == second["normalized_digest"]
    return {
        "replay_id": "duplicate_replay",
        "status": "stable" if stable else "blocked",
        "first_digest": first["normalized_digest"],
        "second_digest": second["normalized_digest"],
        "first_summary": first["normalized_summary"],
        "second_summary": second["normalized_summary"],
        "passed": stable and first["valid"] and second["valid"],
    }


def run_single_leg_scan(
    *,
    surplus: float = 0.1,
    packet_amount: float = 0.1,
    delay_steps: int = 0,
) -> dict[str, Any]:
    model = LGRC9V3.from_state(build_state(), {"dt": 1.0})
    route_aspect = build_route_aspect()
    seed_parent_return(model)
    for _ in range(delay_steps):
        model.step()
    reference_mass = 2.25 - float(surplus)
    producer_results: list[dict[str, Any]] = []
    error: str | None = None
    try:
        producer_results.append(
            produce_and_process(
                model,
                route_aspect=route_aspect,
                source_pole_id="S",
                reference_mass=reference_mass,
                eligible_channel_id="S_to_K",
                packet_amount=packet_amount,
            )
        )
        summary = validate_runtime(model, producer_results)
    except Exception as exc:  # noqa: BLE001 - the artifact records runtime gate failures.
        summary = {
            "event_count": len(model.snapshot()["events"]),
            "producer_result_count": len(producer_results),
            "production_record_count": production_record_count(producer_results),
            "scheduled_event_count": scheduled_event_count(producer_results),
            "candidate_count": 0,
            "completed_count": 0,
            "valid": False,
            "failure_reasons": [type(exc).__name__],
        }
        error = str(exc)
    summary.update(
        {
            "surplus": surplus,
            "reference_mass": reference_mass,
            "packet_amount": packet_amount,
            "delay_steps": delay_steps,
            "runtime_error": error,
            "supported": summary["valid"] and summary["completed_count"] == 1,
        }
    )
    return summary


def pressure_threshold_scan() -> dict[str, Any]:
    rows = [
        run_single_leg_scan(surplus=value)
        for value in [0.03, 0.048, 0.049, 0.05, 0.1]
    ]
    supported = [row["surplus"] for row in rows if row["supported"]]
    rejected = [row["surplus"] for row in rows if not row["supported"]]
    return {
        "scan_id": "pressure_threshold_scan",
        "trigger_threshold": 0.049,
        "rows": rows,
        "minimum_supported_surplus": min(supported) if supported else None,
        "maximum_rejected_surplus": max(rejected) if rejected else None,
        "threshold_supported": bool(supported) and min(supported) <= 0.049,
        "measured_boundary_note": (
            "The configured runtime gate is surplus < trigger_threshold. In this "
            "scan, the serialized 0.049 surplus point fails closed while 0.05 "
            "supports the loop, so I11-C records a measured supported boundary "
            "just above the nominal threshold rather than exact equality support."
        ),
        "bounded_failure_observed": bool(rejected),
        "status": "bounded" if supported and rejected else "partial",
    }


def response_margin_scan() -> dict[str, Any]:
    rows = [
        run_single_leg_scan(surplus=0.1, packet_amount=value)
        for value in [0.05, 0.1, 0.5, 1.0, 2.25, 2.26]
    ]
    supported = [row["packet_amount"] for row in rows if row["supported"]]
    rejected = [row["packet_amount"] for row in rows if not row["supported"]]
    return {
        "scan_id": "response_margin_scan",
        "rows": rows,
        "max_supported_packet_amount": max(supported) if supported else None,
        "min_rejected_packet_amount": min(rejected) if rejected else None,
        "baseline_packet_amount_supported": any(
            row["packet_amount"] == 0.1 and row["supported"] for row in rows
        ),
        "bounded_failure_observed": bool(rejected),
        "status": "bounded" if supported and rejected else "partial",
    }


def trace_window_scan() -> dict[str, Any]:
    rows = [run_single_leg_scan(delay_steps=value) for value in [0, 1, 2, 4]]
    supported = [row["delay_steps"] for row in rows if row["supported"]]
    return {
        "scan_id": "trace_window_scan",
        "rows": rows,
        "max_supported_noop_delay_steps": max(supported) if supported else None,
        "trace_decay_observed": False,
        "trace_decay_note": (
            "The current runtime does not implement a decay law for the latest "
            "processed parent-arrival trace. I11-C therefore supports only an "
            "observed bounded no-decay window, not general trace persistence."
        ),
        "status": "bounded_no_decay_window" if supported else "blocked",
    }


def build_output() -> dict[str, Any]:
    i11 = load_json(I11_OUTPUT)
    i11a = load_json(I11A_OUTPUT)
    i11a_runtime = load_json(I11A_RUNTIME)
    i11b = load_json(I11B_OUTPUT)
    artifact = artifact_replay(i11a, i11a_runtime)
    snapshot = snapshot_load_replay()
    duplicate = duplicate_replay()
    pressure = pressure_threshold_scan()
    response = response_margin_scan()
    trace = trace_window_scan()
    replay_rows = [artifact, snapshot, duplicate]
    stress_rows = [trace, pressure, response]
    all_replays_passed = all(row["passed"] for row in replay_rows)
    stress_bounded = all(row["status"] in {"bounded", "bounded_no_decay_window"} for row in stress_rows)
    data: dict[str, Any] = {
        "artifact_id": "n29_trace_pressure_loop_replay_stress_i11c",
        "experiment_id": "N29",
        "iteration": "I11-C",
        "title": "Trace / Pressure / Loop Replay And Stress Matrix",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "source_artifacts": [
            {
                "artifact_id": "n29_trace_pressure_loop_prototype_i11",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_trace_pressure_loop_prototype_i11.json"
                ),
                "output_digest": i11["output_digest"],
                "consumed_as": "lineage_and_claim_boundary_source",
            },
            {
                "artifact_id": "n29_trace_pressure_loop_runtime_i11a",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_trace_pressure_loop_runtime_i11a.json"
                ),
                "output_digest": i11a["output_digest"],
                "consumed_as": "primary_runtime_bridge_candidate_source",
            },
            {
                "artifact_id": "n29_trace_pressure_loop_runtime_controls_i11b",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_trace_pressure_loop_runtime_controls_i11b.json"
                ),
                "output_digest": i11b["output_digest"],
                "consumed_as": "control_gate_source",
            },
        ],
        "snapshot_artifact_manifest": {
            "path": (
                "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                "outputs/n29_trace_pressure_loop_replay_stress_i11c_snapshot.json"
            ),
            "sha256": sha256_file(SNAPSHOT_OUTPUT),
            "artifact_role": "native_lgrc9v3_snapshot_load_replay_source",
        },
        "runtime_bridge_replay_status": "stable" if all_replays_passed else "partial",
        "trace_window_supported": trace["status"],
        "pressure_threshold_supported": pressure["status"],
        "response_margin_supported": response["status"],
        "replay_rows": replay_rows,
        "stress_rows": stress_rows,
        "claim_ceiling": "replay_stress_backed_runtime_bridge_candidate_no_ecology_success",
        "claim_boundary": {
            claim: False
            for claim in [
                "prototype_success_claimed",
                "runtime_ecology_success_claimed",
                "pheromone_communication_claimed",
                "hunger_alarm_semantics_claimed",
                "semantic_signal_claimed",
                "semantic_action_claimed",
                "native_ecology_claimed",
                "native_shared_medium_coordination_claimed",
                "native_ant_agency_claimed",
                "agency_claimed",
                "phase8_completion_claimed",
            ]
        },
        "interpretation": {
            "what_passes": (
                "I11-C shows stable artifact, snapshot/load continuation, and "
                "duplicate deterministic replay for the I11-A runtime bridge, "
                "while mapping bounded pressure and response margins."
            ),
            "trace_caveat": trace["trace_decay_note"],
            "why_not_stronger": (
                "The result remains producer-assisted and bounded to this two-pole "
                "trace/pressure/loop fixture. It does not establish native ecology, "
                "semantic communication, shared-medium coordination, agency, or "
                "general trace persistence."
            ),
        },
        "ready_for_iteration_12": all_replays_passed and stress_bounded,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    checks = [
        check("i11_source_passed", i11.get("status") == "passed"),
        check("i11a_source_passed", i11a.get("status") == "passed"),
        check("i11b_controls_passed", i11b.get("status") == "passed" and i11b.get("failed_open_count") == 0),
        check("artifact_replay_stable", artifact["passed"] is True),
        check("snapshot_load_replay_stable", snapshot["passed"] is True),
        check("duplicate_replay_stable", duplicate["passed"] is True),
        check("trace_window_bounded", trace["status"] == "bounded_no_decay_window"),
        check("pressure_threshold_bounded", pressure["status"] == "bounded"),
        check("response_margin_bounded", response["status"] == "bounded"),
        check("unsafe_claim_flags_false", all(value is False for value in data["claim_boundary"].values())),
        check("ready_for_iteration_12", data["ready_for_iteration_12"] is True),
        check("no_absolute_paths_in_records", no_absolute_paths(data) and no_absolute_paths(load_json(SNAPSHOT_OUTPUT))),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["status"] = "passed" if not data["failed_checks"] else "failed"
    data["acceptance_state"] = (
        "accepted_trace_pressure_loop_replay_stress_bounded_producer_assisted_no_ecology_success"
        if data["status"] == "passed"
        else "partial_trace_pressure_loop_replay_stress_matrix"
    )
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 11-C - Trace / Pressure / Loop Replay And Stress",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- runtime_bridge_replay_status: `{data['runtime_bridge_replay_status']}`",
        f"- trace_window_supported: `{data['trace_window_supported']}`",
        f"- pressure_threshold_supported: `{data['pressure_threshold_supported']}`",
        f"- response_margin_supported: `{data['response_margin_supported']}`",
        f"- ready_for_iteration_12: `{str(data['ready_for_iteration_12']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "I11-C consumes I11-A as the runtime bridge and I11-B as the fail-closed",
        "control gate. It does not raise the claim ceiling beyond a bounded,",
        "producer-assisted runtime bridge candidate.",
        "",
        "## Replay Rows",
        "",
        "| Replay | Status | Passed |",
        "| --- | --- | --- |",
    ]
    for row in data["replay_rows"]:
        lines.append(
            f"| `{row['replay_id']}` | `{row['status']}` | `{str(row['passed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Stress Rows",
            "",
            "| Stress Scan | Status | Key Result |",
            "| --- | --- | --- |",
        ]
    )
    for row in data["stress_rows"]:
        if row["scan_id"] == "trace_window_scan":
            key = f"max noop delay `{row['max_supported_noop_delay_steps']}`"
        elif row["scan_id"] == "pressure_threshold_scan":
            key = f"min supported surplus `{row['minimum_supported_surplus']}`"
        else:
            key = f"max supported packet amount `{row['max_supported_packet_amount']}`"
        lines.append(f"| `{row['scan_id']}` | `{row['status']}` | {key} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            data["interpretation"]["what_passes"],
            "",
            data["stress_rows"][1]["measured_boundary_note"],
            "",
            data["interpretation"]["trace_caveat"],
            "",
            data["interpretation"]["why_not_stronger"],
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check_row in data["checks"]:
        lines.append(f"| `{check_row['check_id']}` | `{str(check_row['passed']).lower()}` |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()
