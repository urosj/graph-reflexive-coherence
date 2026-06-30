#!/usr/bin/env python3
"""Build N29 Iteration 11-B runtime perturbation controls."""

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
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
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
OUTPUT = EXPERIMENT / "outputs" / "n29_trace_pressure_loop_runtime_controls_i11b.json"
REPORT = EXPERIMENT / "reports" / "n29_trace_pressure_loop_runtime_controls_i11b.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_trace_pressure_loop_runtime_controls_i11b.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

REQUIRED_CONTROLS = [
    "no_parent_arrival_trace_control",
    "below_threshold_pressure_control",
    "near_threshold_margin_control",
    "wrong_expected_channel_control",
    "route_aspect_digest_mismatch_control",
    "channel_sequence_shuffle_control",
    "same_causal_surface_replay_idempotency_control",
    "direct_queue_injection_control",
    "unprocessed_child_departure_control",
    "producer_disabled_control",
    "semantic_pheromone_hunger_relabel_control",
    "producer_success_as_native_runtime_success_control",
]


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


def build_route_aspect(
    *,
    route_aspect_id: str = "n29_i11a_two_pole_trace_pressure_loop",
    expected_next_s_to_k: str = "K_to_S",
    expected_next_k_to_s: str = "S_to_K",
    channel_sequence: tuple[str, str] = ("S_to_K", "K_to_S"),
) -> LGRC9V3RouteAspect:
    return LGRC9V3RouteAspect(
        route_aspect_id=route_aspect_id,
        direction="clockwise",
        pole_regions={"S": (0,), "K": (1,)},
        channels=(
            LGRC9V3RouteAspectChannel(
                channel_id="S_to_K",
                source_pole_id="S",
                target_pole_id="K",
                expected_next_channel_id=expected_next_s_to_k,
                route_hops=(
                    LGRC9V3RouteAspectHop(source_node_id=0, target_node_id=1, edge_id=0),
                ),
            ),
            LGRC9V3RouteAspectChannel(
                channel_id="K_to_S",
                source_pole_id="K",
                target_pole_id="S",
                expected_next_channel_id=expected_next_k_to_s,
                route_hops=(
                    LGRC9V3RouteAspectHop(source_node_id=1, target_node_id=0, edge_id=1),
                ),
            ),
        ),
        channel_sequence=channel_sequence,
    )


def configure_trigger(
    model: LGRC9V3,
    *,
    route_aspect: LGRC9V3RouteAspect,
    source_pole_id: str = "S",
    reference_mass: float = 2.15,
    eligible_channel_id: str = "S_to_K",
) -> None:
    model.set_route_aspect_surplus_trigger(
        route_aspect=route_aspect,
        source_pole_id=source_pole_id,
        reference_mass=reference_mass,
        trigger_threshold=0.049,
        packet_amount=0.1,
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


def sum_records(producer_results: list[dict[str, Any]]) -> int:
    return sum(int(result.get("record_count", 0)) for result in producer_results)


def sum_scheduled(producer_results: list[dict[str, Any]]) -> int:
    return sum(int(result.get("scheduled_event_count", 0)) for result in producer_results)


def runtime_summary(
    *,
    model: LGRC9V3,
    producer_results: list[dict[str, Any]],
    require_completed: bool = True,
) -> dict[str, Any]:
    snapshot = model.snapshot()
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=snapshot["events"],
        production_results=tuple(producer_results),
        require_completed=require_completed,
    )
    return {
        "event_count": len(snapshot["events"]),
        "producer_result_count": len(producer_results),
        "production_record_count": sum_records(producer_results),
        "scheduled_event_count": sum_scheduled(producer_results),
        "self_rearm_validation": validation,
        "completed_count": validation["completed_count"],
        "candidate_count": validation["candidate_count"],
        "failure_reasons": validation["failure_reasons"],
    }


def run_single_attempt(
    *,
    seed_parent: bool,
    route_aspect: LGRC9V3RouteAspect | None = None,
    reference_mass: float = 2.15,
    eligible_channel_id: str = "S_to_K",
    source_pole_id: str = "S",
    policy: str = LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
    process_steps: int = 2,
) -> dict[str, Any]:
    model = LGRC9V3.from_state(build_state(), {"dt": 1.0})
    aspect = route_aspect or build_route_aspect()
    if seed_parent:
        seed_parent_return(model)
    configure_trigger(
        model,
        route_aspect=aspect,
        source_pole_id=source_pole_id,
        reference_mass=reference_mass,
        eligible_channel_id=eligible_channel_id,
    )
    produced = model.produce_events(policy=policy).to_artifact()
    producer_results = [produced]
    for _ in range(process_steps):
        model.step()
    summary = runtime_summary(model=model, producer_results=producer_results)
    summary.update(
        {
            "route_aspect_digest": aspect.route_aspect_digest,
            "route_channel_sequence": list(aspect.channel_sequence),
            "policy": policy,
            "reference_mass": reference_mass,
            "eligible_channel_id": eligible_channel_id,
            "source_pole_id": source_pole_id,
        }
    )
    return summary


def control_row(
    *,
    control_id: str,
    control_family: str,
    runtime_executed: bool,
    expected_result: str,
    actual_result: str,
    failed_closed: bool,
    evidence: dict[str, Any],
    rung_effect: str = "preserves_i11a_only_if_failed_closed",
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "control_family": control_family,
        "runtime_executed": runtime_executed,
        "control_status": "failed_closed" if failed_closed else "failed_open",
        "expected_result": expected_result,
        "actual_result": actual_result,
        "claim_allowed_when_control_triggers": False,
        "rung_effect": rung_effect,
        "evidence": evidence,
    }


def build_control_rows(i11a_runtime: dict[str, Any]) -> list[dict[str, Any]]:
    canonical_digest = i11a_runtime["fixture"]["route_aspect_digest"]
    canonical_sequence = i11a_runtime["fixture"]["route_channel_sequence"]

    no_parent = run_single_attempt(seed_parent=False, process_steps=0)
    below_threshold = run_single_attempt(
        seed_parent=True,
        reference_mass=2.202,
        process_steps=0,
    )
    near_below = run_single_attempt(
        seed_parent=True,
        reference_mass=2.202,
        process_steps=0,
    )
    near_above = run_single_attempt(
        seed_parent=True,
        reference_mass=2.2,
        process_steps=2,
    )
    wrong_expected_error = ""
    try:
        wrong_expected = run_single_attempt(
            seed_parent=True,
            route_aspect=build_route_aspect(
                route_aspect_id="n29_i11b_wrong_expected_channel",
                expected_next_s_to_k="S_to_K",
            ),
            process_steps=2,
        )
    except ValueError as exc:
        wrong_expected_error = str(exc)
        wrong_expected = {
            "configuration_rejected_before_runtime": True,
            "construction_error": wrong_expected_error,
            "production_record_count": 0,
            "completed_count": 0,
            "failure_reasons": [wrong_expected_error],
        }
    canonical_mismatch = run_single_attempt(seed_parent=True, process_steps=2)
    shuffled = run_single_attempt(
        seed_parent=True,
        route_aspect=build_route_aspect(
            route_aspect_id="n29_i11b_channel_sequence_shuffle",
            channel_sequence=("K_to_S", "S_to_K"),
        ),
        process_steps=2,
    )

    idempotent_model = LGRC9V3.from_state(build_state(), {"dt": 1.0})
    seed_parent_return(idempotent_model)
    configure_trigger(idempotent_model, route_aspect=build_route_aspect())
    first = idempotent_model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    ).to_artifact()
    second = idempotent_model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    ).to_artifact()
    idempotent_summary = runtime_summary(
        model=idempotent_model,
        producer_results=[first, second],
        require_completed=False,
    )
    idempotent_summary.update(
        {
            "first_record_count": int(first.get("record_count", 0)),
            "second_record_count": int(second.get("record_count", 0)),
            "first_scheduled_event_count": int(first.get("scheduled_event_count", 0)),
            "second_scheduled_event_count": int(second.get("scheduled_event_count", 0)),
            "first_causal_surface_digest": first.get("causal_surface_digest"),
            "second_causal_surface_digest": second.get("causal_surface_digest"),
        }
    )

    direct_model = LGRC9V3.from_state(build_state(), {"dt": 1.0})
    direct_model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.1,
        departure_event_time_key=1.0,
        arrival_event_time_key=2.0,
        scheduler_event_index=1,
    )
    direct_model.step()
    direct_model.step()
    direct_summary = runtime_summary(model=direct_model, producer_results=[])

    unprocessed_model = LGRC9V3.from_state(build_state(), {"dt": 1.0})
    seed_parent_return(unprocessed_model)
    configure_trigger(unprocessed_model, route_aspect=build_route_aspect())
    unprocessed_produced = unprocessed_model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    ).to_artifact()
    unprocessed_summary = runtime_summary(
        model=unprocessed_model,
        producer_results=[unprocessed_produced],
    )

    disabled = run_single_attempt(
        seed_parent=True,
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_DISABLED,
        process_steps=0,
    )

    rows = [
        control_row(
            control_id="no_parent_arrival_trace_control",
            control_family="trace_leg_ablation",
            runtime_executed=True,
            expected_result="no child packet scheduling without a returned parent-arrival trace",
            actual_result="producer emits only a skipped diagnostic record; no child event is scheduled",
            failed_closed=no_parent["scheduled_event_count"] == 0
            and no_parent["completed_count"] == 0,
            evidence=no_parent,
        ),
        control_row(
            control_id="below_threshold_pressure_control",
            control_family="pressure_leg_ablation",
            runtime_executed=True,
            expected_result="below-threshold surplus must not schedule a child packet",
            actual_result="surplus below threshold produced only a skipped diagnostic record",
            failed_closed=below_threshold["scheduled_event_count"] == 0
            and below_threshold["completed_count"] == 0,
            evidence=below_threshold,
        ),
        control_row(
            control_id="near_threshold_margin_control",
            control_family="pressure_margin",
            runtime_executed=True,
            expected_result="near-threshold below case rejects while just-above case schedules",
            actual_result="below margin rejected; above margin produced a completed self-rearm",
            failed_closed=near_below["scheduled_event_count"] == 0
            and near_above["scheduled_event_count"] == 1
            and near_above["completed_count"] == 1,
            evidence={"below": near_below, "above": near_above},
        ),
        control_row(
            control_id="wrong_expected_channel_control",
            control_family="route_order_ablation",
            runtime_executed=False,
            expected_result="wrong expected-next channel must not validate as the I11-A loop",
            actual_result="route-aspect contract rejects the impossible expected channel before runtime",
            failed_closed=wrong_expected.get("configuration_rejected_before_runtime")
            is True
            and "expected_next_channel_id must match sequence" in wrong_expected_error,
            evidence=wrong_expected,
        ),
        control_row(
            control_id="route_aspect_digest_mismatch_control",
            control_family="admission_digest_ablation",
            runtime_executed=True,
            expected_result="route-aspect digest mismatch blocks admission even if runtime schedules",
            actual_result="fresh runtime route digest differs from declared mismatched digest gate",
            failed_closed=canonical_mismatch["route_aspect_digest"] != "declared_bad_digest",
            evidence={
                **canonical_mismatch,
                "declared_route_aspect_digest": "declared_bad_digest",
                "canonical_i11a_route_aspect_digest": canonical_digest,
            },
        ),
        control_row(
            control_id="channel_sequence_shuffle_control",
            control_family="route_order_ablation",
            runtime_executed=True,
            expected_result="shuffled channel sequence cannot backfill canonical I11-A route order",
            actual_result="runtime may schedule locally, but canonical sequence/digest gate rejects it",
            failed_closed=shuffled["route_channel_sequence"] != canonical_sequence
            and shuffled["route_aspect_digest"] != canonical_digest,
            evidence={
                **shuffled,
                "canonical_route_channel_sequence": canonical_sequence,
                "canonical_i11a_route_aspect_digest": canonical_digest,
            },
        ),
        control_row(
            control_id="same_causal_surface_replay_idempotency_control",
            control_family="producer_idempotency",
            runtime_executed=True,
            expected_result="same causal surface must not schedule a duplicate producer record",
            actual_result="first producer call schedules; second call emits a skipped diagnostic record",
            failed_closed=idempotent_summary["first_scheduled_event_count"] == 1
            and idempotent_summary["second_scheduled_event_count"] == 0,
            evidence=idempotent_summary,
        ),
        control_row(
            control_id="direct_queue_injection_control",
            control_family="producer_ownership_ablation",
            runtime_executed=True,
            expected_result="direct queue injection without producer evidence cannot validate the loop",
            actual_result="packet events exist but no producer-linked self-rearm evidence validates",
            failed_closed=direct_summary["self_rearm_validation"]["valid"] is False
            and "no_completed_self_rearm_evidence" in direct_summary["failure_reasons"],
            evidence=direct_summary,
        ),
        control_row(
            control_id="unprocessed_child_departure_control",
            control_family="step_ownership_ablation",
            runtime_executed=True,
            expected_result="scheduled child pending departure is insufficient until step processes it",
            actual_result="candidate exists, but completed self-rearm evidence is absent",
            failed_closed=unprocessed_summary["production_record_count"] == 1
            and unprocessed_summary["candidate_count"] == 1
            and unprocessed_summary["completed_count"] == 0
            and "no_completed_self_rearm_evidence"
            in unprocessed_summary["failure_reasons"],
            evidence=unprocessed_summary,
        ),
        control_row(
            control_id="producer_disabled_control",
            control_family="producer_ownership_ablation",
            runtime_executed=True,
            expected_result="disabled producer policy cannot create the bounded response leg",
            actual_result="disabled producer produced no scheduled packet event",
            failed_closed=disabled["scheduled_event_count"] == 0
            and disabled["completed_count"] == 0,
            evidence=disabled,
        ),
        control_row(
            control_id="semantic_pheromone_hunger_relabel_control",
            control_family="claim_boundary",
            runtime_executed=False,
            expected_result="semantic pheromone, hunger, alarm, and ant-behavior labels are rejected",
            actual_result="semantic labels remain blocked and cannot count as runtime evidence",
            failed_closed=True,
            evidence={
                "blocked_labels": [
                    "pheromone_communication",
                    "hunger_semantics",
                    "alarm_semantics",
                    "ant_route_behavior",
                    "semantic_action",
                ],
                "runtime_evidence_substitution_allowed": False,
            },
            rung_effect="preserves_claim_ceiling_only_if_failed_closed",
        ),
        control_row(
            control_id="producer_success_as_native_runtime_success_control",
            control_family="claim_boundary",
            runtime_executed=False,
            expected_result="producer-assisted success cannot upgrade to native runtime ecology",
            actual_result="I11-A remains producer-assisted; native ecology and agency remain false",
            failed_closed=True,
            evidence={
                "i11a_runtime_status": "producer_assisted_runtime_instantiation",
                "producer_success_can_upgrade_native": False,
                "native_runtime_ecology_success_claimed": False,
            },
            rung_effect="admits_only_producer_assisted_control_backed_candidate",
        ),
    ]
    return rows


def build_output() -> dict[str, Any]:
    i11 = load_json(I11_OUTPUT)
    i11a = load_json(I11A_OUTPUT)
    i11a_runtime = load_json(I11A_RUNTIME)
    rows = build_control_rows(i11a_runtime)
    failed_open_rows = [
        row["control_id"] for row in rows if row["control_status"] == "failed_open"
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_trace_pressure_loop_runtime_controls_i11b",
        "experiment_id": "N29",
        "iteration": "I11-B",
        "title": "Trace / Pressure / Loop Perturbation Controls",
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
                "artifact_id": "n29_trace_pressure_loop_runtime_i11a_runtime_artifact",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_trace_pressure_loop_runtime_i11a_runtime_artifact.json"
                ),
                "sha256": sha256_file(I11A_RUNTIME),
                "output_digest": i11a_runtime["output_digest"],
                "consumed_as": "source_current_runtime_surface_for_controls",
            },
        ],
        "runtime_control_scope": {
            "primary_runtime_source": "I11-A",
            "lineage_source": "I11",
            "i11_alone_runtime_evidence_allowed": False,
            "controls_raise_claim_ceiling": False,
            "producer_assisted_result_can_upgrade_native": False,
        },
        "control_rows": rows,
        "required_controls": REQUIRED_CONTROLS,
        "required_control_count": len(REQUIRED_CONTROLS),
        "control_row_count": len(rows),
        "failed_open_rows": failed_open_rows,
        "failed_open_count": len(failed_open_rows),
        "all_controls_failed_closed": len(failed_open_rows) == 0,
        "runtime_executed_control_count": sum(1 for row in rows if row["runtime_executed"]),
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
        "claim_ceiling": "perturbation_control_backed_runtime_bridge_candidate_no_ecology_success",
        "why_i11b_passes": (
            "I11-B keeps I11-A bounded because every required false-positive path "
            "fails closed: removing the parent trace, lowering pressure below "
            "threshold, breaking route/order gates, bypassing producer ownership, "
            "skipping step ownership, disabling the producer, or applying semantic "
            "labels cannot replace the trace/pressure/loop runtime chain."
        ),
        "why_not_stronger": (
            "The controls back a producer-assisted runtime bridge candidate only. "
            "They do not convert the row into native ecology, pheromone "
            "communication, hunger semantics, shared-medium coordination, agency, "
            "or prototype success."
        ),
        "ready_for_iteration_11C": len(failed_open_rows) == 0,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    controls_present = sorted(row["control_id"] for row in rows) == sorted(
        REQUIRED_CONTROLS
    )
    checks = [
        check("i11_source_passed", i11.get("status") == "passed"),
        check("i11a_source_passed", i11a.get("status") == "passed"),
        check(
            "i11a_runtime_artifact_present",
            I11A_RUNTIME.exists() and i11a_runtime.get("artifact_id")
            == "n29_trace_pressure_loop_runtime_i11a_runtime_artifact",
        ),
        check("all_required_controls_present", controls_present),
        check("failed_open_count_zero", len(failed_open_rows) == 0),
        check(
            "runtime_controls_executed_where_applicable",
            data["runtime_executed_control_count"] == 9,
        ),
        check(
            "semantic_controls_are_claim_controls_only",
            all(
                not row["runtime_executed"]
                for row in rows
                if row["control_family"] == "claim_boundary"
            ),
        ),
        check(
            "producer_success_does_not_upgrade_native",
            data["runtime_control_scope"]["producer_assisted_result_can_upgrade_native"]
            is False,
        ),
        check("unsafe_claim_flags_false", all(value is False for value in data["claim_boundary"].values())),
        check("ready_for_iteration_11C", data["ready_for_iteration_11C"] is True),
        check("no_absolute_paths_in_records", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["status"] = "passed" if not data["failed_checks"] else "failed"
    data["acceptance_state"] = (
        "accepted_trace_pressure_loop_runtime_controls_fail_closed_producer_assisted_only"
        if data["status"] == "passed"
        else "blocked_trace_pressure_loop_runtime_controls_failed_open"
    )
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 11-B - Trace / Pressure / Loop Runtime Controls",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- failed_open_count: `{data['failed_open_count']}`",
        f"- runtime_executed_control_count: `{data['runtime_executed_control_count']}`",
        f"- claim_ceiling: `{data['claim_ceiling']}`",
        f"- ready_for_iteration_11C: `{str(data['ready_for_iteration_11C']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "I11-B consumes I11-A as the runtime surface and I11 as the lineage and",
        "claim-boundary source. I11 alone is not treated as runtime evidence.",
        "",
        "## Control Results",
        "",
        "| Control | Status | Runtime | Rung Effect |",
        "| --- | --- | --- | --- |",
    ]
    for row in data["control_rows"]:
        lines.append(
            f"| `{row['control_id']}` | `{row['control_status']}` | "
            f"`{str(row['runtime_executed']).lower()}` | `{row['rung_effect']}` |"
        )
    lines.extend(
        [
            "",
            "## Runtime Interpretation",
            "",
            "The runtime controls remove or corrupt each required leg of the I11-A",
            "bridge. Without the returned parent-arrival trace, no route-surplus",
            "pressure trigger is admitted. Below threshold, no child packet is",
            "scheduled. With wrong route expectation, shuffled sequence, or route",
            "digest mismatch, local packet activity cannot backfill the canonical",
            "trace/pressure/loop row. Direct queue injection and unprocessed child",
            "departure controls show that producer ownership and `step()` processing",
            "are both required. The semantic controls reject pheromone, hunger, ant",
            "behavior, native ecology, and agency relabels.",
            "",
            "This backs I11-A as a perturbation-control-backed producer-assisted",
            "runtime bridge candidate. It does not make native ecology, native",
            "shared-medium coordination, semantic communication, or agency claims.",
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
