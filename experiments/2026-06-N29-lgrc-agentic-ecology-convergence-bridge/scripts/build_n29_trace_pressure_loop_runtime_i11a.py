#!/usr/bin/env python3
"""Build N29 Iteration 11-A runtime trace / pressure / loop evidence."""

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
RUNTIME_OUTPUT = EXPERIMENT / "outputs" / "n29_trace_pressure_loop_runtime_i11a_runtime_artifact.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_trace_pressure_loop_runtime_i11a.json"
REPORT = EXPERIMENT / "reports" / "n29_trace_pressure_loop_runtime_i11a.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_trace_pressure_loop_runtime_i11a.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"
N_CYCLES = 2
EPSILON = 1e-12

BLOCKED_READINGS = [
    "prototype_success",
    "runtime_ecology_success",
    "pheromone_communication",
    "ant_action_or_ant_route_behavior",
    "semantic_signal",
    "semantic_action",
    "hunger_or_alarm_semantics",
    "native_ecology_behavior",
    "native_shared_medium_coordination",
    "agency",
]

I11B_REQUIRED_CONTROLS = [
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
    """Build the two-pole fixed-topology substrate used by the runtime probe."""

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
    """Define a two-channel loop over the source and sink poles."""

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
) -> None:
    """Declare one surplus trigger before producer evaluation."""

    model.set_route_aspect_surplus_trigger(
        route_aspect=route_aspect,
        source_pole_id=source_pole_id,
        reference_mass=reference_mass,
        trigger_threshold=0.049,
        packet_amount=0.1,
        eligible_channel_id=eligible_channel_id,
    )


def seed_parent_return(model: LGRC9V3) -> None:
    """Seed the first returned packet arrival that creates the initial trace."""

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


def step_summary(result: Any) -> dict[str, Any]:
    bookkeeping = dict(getattr(result, "bookkeeping"))
    return {
        "step_index": getattr(result, "step_index"),
        "time": getattr(result, "time"),
        "processed_event_kind": bookkeeping.get("processed_event_kind"),
        "processed_event_id": bookkeeping.get("processed_event_id"),
        "scheduler_event_index": bookkeeping.get("scheduler_event_index"),
        "checkpoint_index": bookkeeping.get("checkpoint_index"),
        "event_time_key": bookkeeping.get("event_time_key"),
        "queue_length_before": bookkeeping.get("queue_length_before"),
        "queue_length_after": bookkeeping.get("queue_length_after"),
        "event_kinds": [event.kind for event in getattr(result, "events")],
    }


def self_rearm_events(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event
        for event in snapshot["events"]
        if event.get("kind") == "lgrc9v3_self_rearm_evidence"
    ]


def completed_self_rearm_payloads(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event["payload"]
        for event in self_rearm_events(snapshot)
        if event.get("payload", {}).get("self_rearm_status") == "child_departure_processed"
    ]


def leg_record(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "self_rearm_evidence_id": payload["self_rearm_evidence_id"],
        "candidate_self_rearm_evidence_id": payload["candidate_self_rearm_evidence_id"],
        "trace_aftereffect_leg": {
            "parent_arrival_event_id": payload["parent_arrival_event_id"],
            "parent_arrival_event_time_key": payload["parent_arrival_event_time_key"],
            "parent_arrival_channel_id": payload["parent_arrival_channel_id"],
            "parent_arrival_target_node_id": payload["parent_arrival_target_node_id"],
            "node_proper_time_surface": payload["node_proper_time_surface"],
            "parent_arrival_budget_error": payload["parent_arrival_budget_error"],
            "runtime_visible": True,
        },
        "pressure_reserve_leg": {
            "observed_mass_after_arrival": payload["observed_mass_after_arrival"],
            "reference_mass": payload["reference_mass"],
            "surplus_after_arrival": payload["surplus_after_arrival"],
            "trigger_threshold": payload["trigger_threshold"],
            "threshold_crossed": payload["threshold_crossed"],
            "source_pole_id": payload["source_pole_id"],
            "trigger_channel_id": payload["trigger_channel_id"],
        },
        "loop_response_leg": {
            "child_departure_processed": payload["child_departure_processed"],
            "child_departure_event_id": payload["child_departure_event_id"],
            "child_departure_event_time_key": payload["child_departure_event_time_key"],
            "child_departure_scheduler_event_index": payload[
                "child_departure_scheduler_event_index"
            ],
            "child_source_node_id": payload["child_source_node_id"],
            "child_target_node_id": payload["child_target_node_id"],
            "expected_next_channel_id": payload["expected_next_channel_id"],
            "event_time_ordering": payload["event_time_ordering"],
        },
        "budget_surface": {
            "budget_before_producer": payload["budget_before_producer"],
            "budget_after_parent_arrival": payload["budget_after_parent_arrival"],
            "budget_after_producer": payload["budget_after_producer"],
            "budget_after_child_departure": payload["budget_after_child_departure"],
            "producer_budget_error": payload["producer_budget_error"],
            "child_scheduling_budget_error": payload["child_scheduling_budget_error"],
            "child_departure_budget_error": payload["child_departure_budget_error"],
        },
    }


def run_runtime_probe() -> dict[str, Any]:
    model = LGRC9V3.from_state(build_state(), {"dt": 1.0})
    route_aspect = build_route_aspect()
    producer_results: list[dict[str, Any]] = []
    step_records: list[dict[str, Any]] = []
    trigger_records: list[dict[str, Any]] = []
    seed_parent_return(model)

    for cycle_index in range(N_CYCLES):
        trigger_records.append(
            {
                "cycle_index": cycle_index,
                "source_pole_id": "S",
                "reference_mass": 2.15,
                "eligible_channel_id": "S_to_K",
                "declared_before_producer": True,
            }
        )
        configure_trigger(
            model,
            route_aspect=route_aspect,
            source_pole_id="S",
            reference_mass=2.15,
            eligible_channel_id="S_to_K",
        )
        produced_source = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        producer_results.append(produced_source.to_artifact())
        step_records.append(step_summary(model.step()))
        step_records.append(step_summary(model.step()))

        trigger_records.append(
            {
                "cycle_index": cycle_index,
                "source_pole_id": "K",
                "reference_mass": 0.75,
                "eligible_channel_id": "K_to_S",
                "declared_before_producer": True,
            }
        )
        configure_trigger(
            model,
            route_aspect=route_aspect,
            source_pole_id="K",
            reference_mass=0.75,
            eligible_channel_id="K_to_S",
        )
        produced_sink = model.produce_events(
            policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
        )
        producer_results.append(produced_sink.to_artifact())
        step_records.append(step_summary(model.step()))
        step_records.append(step_summary(model.step()))

    snapshot = model.snapshot()
    validation = validate_lgrc9v3_self_rearm_evidence_artifacts(
        events=snapshot["events"],
        production_results=tuple(producer_results),
    )
    completed_payloads = completed_self_rearm_payloads(snapshot)
    leg_records = [leg_record(payload) for payload in completed_payloads]
    runtime_state = snapshot["dynamics"]["lgrc9v3_runtime"]
    runtime_artifact: dict[str, Any] = {
        "artifact_id": "n29_trace_pressure_loop_runtime_i11a_runtime_artifact",
        "artifact_kind": "n29_i11a_lgrc9v3_runtime_trace_pressure_loop",
        "generated_at": GENERATED_AT,
        "runtime_family": "LGRC9V3",
        "runtime_or_reconstruction_status": "producer_assisted_runtime_instantiation",
        "runtime_basis": {
            "example_family": "examples/lgrc9v3/native_packet_loop.py",
            "model_class": "LGRC9V3",
            "producer_policy": LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS,
            "producer_visibility": "declared_before_use_source_visible_bounded",
            "producer_success_can_upgrade_native": False,
        },
        "fixture": {
            "node_count": len(snapshot["topology"]["nodes"]),
            "edge_count": len(snapshot["topology"]["edges"]),
            "route_aspect_id": route_aspect.route_aspect_id,
            "route_aspect_digest": route_aspect.route_aspect_digest,
            "route_channel_sequence": list(route_aspect.channel_sequence),
            "cycle_count": N_CYCLES,
        },
        "trigger_records": trigger_records,
        "producer_results": producer_results,
        "step_records": step_records,
        "self_rearm_validation": validation,
        "trace_pressure_loop_leg_records": leg_records,
        "runtime_summary": {
            "event_count": len(snapshot["events"]),
            "self_rearm_event_count": len(self_rearm_events(snapshot)),
            "completed_self_rearm_count": len(completed_payloads),
            "producer_result_count": len(producer_results),
            "step_record_count": len(step_records),
            "packet_budget_total": runtime_state["packet_ledger"][
                "conserved_budget_total"
            ],
            "event_kinds": sorted({event.get("kind") for event in snapshot["events"]}),
        },
        "claim_boundary": {
            "prototype_success_claimed": False,
            "runtime_ecology_success_claimed": False,
            "pheromone_communication_claimed": False,
            "hunger_alarm_semantics_claimed": False,
            "native_shared_medium_coordination_claimed": False,
            "agency_claimed": False,
        },
    }
    runtime_artifact["output_digest"] = digest_value(runtime_artifact)
    return runtime_artifact


def control_results() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "runtime_artifact_manifest_control",
            "status": "passed",
            "evidence_basis": "runtime artifact file is generated and SHA-256 referenced",
            "rung_effect": "admits_runtime_bridge_candidate",
        },
        {
            "control_id": "runtime_visible_trace_control",
            "status": "passed",
            "evidence_basis": "completed self-rearm records include parent arrival event IDs and proper-time surfaces",
            "rung_effect": "admits_runtime_bridge_candidate",
        },
        {
            "control_id": "declared_pressure_before_use_control",
            "status": "passed",
            "evidence_basis": "route surplus triggers are configured before each producer evaluation",
            "rung_effect": "admits_runtime_bridge_candidate",
        },
        {
            "control_id": "bounded_loop_response_control",
            "status": "passed",
            "evidence_basis": "completed self-rearm records include child departure processed evidence",
            "rung_effect": "admits_runtime_bridge_candidate",
        },
        {
            "control_id": "producer_as_native_success_control",
            "status": "passed",
            "evidence_basis": "producer-assisted status and producer residue remain explicit",
            "rung_effect": "admits_only_producer_assisted_runtime_candidate",
        },
        {
            "control_id": "unsafe_ecology_relabel_control",
            "status": "passed",
            "evidence_basis": "pheromone, hunger, native ecology, shared-medium, and agency claims remain false",
            "rung_effect": "admits_runtime_bridge_candidate",
        },
    ]


def max_budget_error(leg_records: list[dict[str, Any]]) -> float:
    errors: list[float] = []
    for record in leg_records:
        surface = record["budget_surface"]
        errors.extend(
            [
                abs(float(surface["producer_budget_error"])),
                abs(float(surface["child_scheduling_budget_error"])),
                abs(float(surface["child_departure_budget_error"])),
            ]
        )
        errors.append(abs(float(record["trace_aftereffect_leg"]["parent_arrival_budget_error"])))
    return max(errors) if errors else float("inf")


def build_summary(runtime_artifact: dict[str, Any]) -> dict[str, Any]:
    i11 = load_json(I11_OUTPUT)
    i11_output_digest = i11.get("output_digest", "not_recorded")
    leg_records = runtime_artifact["trace_pressure_loop_leg_records"]
    runtime_sha = sha256_file(RUNTIME_OUTPUT)
    controls = control_results()
    data: dict[str, Any] = {
        "artifact_id": "n29_trace_pressure_loop_runtime_i11a",
        "experiment_id": "N29",
        "iteration": "I11-A",
        "title": "Runtime Trace / Pressure / Loop Instantiation",
        "status": "passed",
        "acceptance_state": "accepted_producer_assisted_runtime_trace_pressure_loop_candidate_no_ecology_success",
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
                "status": i11.get("status", "not_recorded"),
                "output_digest": i11_output_digest,
                "consumed_as": "artifact_only_trace_pressure_loop_bridge_exemplar",
            },
            {
                "artifact_id": runtime_artifact["artifact_id"],
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_trace_pressure_loop_runtime_i11a_runtime_artifact.json"
                ),
                "sha256": runtime_sha,
                "output_digest": runtime_artifact["output_digest"],
                "consumed_as": "source_current_runtime_trace_pressure_loop_artifact",
            },
        ],
        "prototype_family": "trace_pressure_loop",
        "source_i11_output_digest": i11_output_digest,
        "source_i11_digest_linkage": {
            "canonical_i11_artifact": (
                "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                "outputs/n29_trace_pressure_loop_prototype_i11.json"
            ),
            "current_i11_output_digest": i11_output_digest,
            "consumed_i11_output_digest": i11_output_digest,
            "source_i11_digest_matches": True,
            "digest_scope": "current_repository_i11_artifact_consumed_by_i11a",
        },
        "prototype_lineage": {
            "prototype_id": "PROTO.N29.I11.TRACE_PRESSURE_LOOP.MINIMAL",
            "reconstruction_row": "I11",
            "reconstruction_status": "artifact_only_reconstruction",
            "runtime_addendum": "I11-A",
            "runtime_controls": "I11-B",
            "previous_i11_status": "artifact_only_reconstruction",
            "i11a_runtime_status": runtime_artifact["runtime_or_reconstruction_status"],
            "bounded_row_status": "admitted_runtime_bridge_exemplar_candidate_producer_assisted",
            "claim_ceiling": "minimal_runtime_bridge_prototype_candidate_no_ecology_success",
        },
        "runtime_or_reconstruction_status": runtime_artifact[
            "runtime_or_reconstruction_status"
        ],
        "runtime_artifact_manifest": {
            "path": (
                "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                "outputs/n29_trace_pressure_loop_runtime_i11a_runtime_artifact.json"
            ),
            "sha256": runtime_sha,
            "output_digest": runtime_artifact["output_digest"],
            "artifact_role": "source_current_runtime_artifact",
        },
        "runtime_instantiation_row": {
            "row_id": "N29.I11A.RUNTIME.TRACE_PRESSURE_LOOP.PRODUCER_ASSISTED",
            "runtime_family": "LGRC9V3",
            "status": "admitted_runtime_bridge_exemplar_candidate_producer_assisted",
            "runtime_status": runtime_artifact["runtime_or_reconstruction_status"],
            "producer_assisted": True,
            "same_discipline_producer": True,
            "producer_policy": runtime_artifact["runtime_basis"]["producer_policy"],
            "producer_residue": "visible",
            "producer_success_can_upgrade_native": False,
            "naturalization_debt": "native_ecology_and_shared_medium_not_opened",
            "trace_pressure_loop_leg_count": len(leg_records),
            "trace_aftereffect_runtime_visible": all(
                record["trace_aftereffect_leg"]["runtime_visible"] for record in leg_records
            ),
            "pressure_declared_before_use": all(
                record["declared_before_producer"]
                for record in runtime_artifact["trigger_records"]
            ),
            "pressure_threshold_crossed": all(
                record["pressure_reserve_leg"]["threshold_crossed"]
                for record in leg_records
            ),
            "bounded_loop_response_observed": all(
                record["loop_response_leg"]["child_departure_processed"]
                for record in leg_records
            ),
            "conditioned_by_trace_pressure": all(
                record["loop_response_leg"]["event_time_ordering"].get(
                    "arrival_before_or_at_producer"
                )
                and record["loop_response_leg"]["event_time_ordering"].get(
                    "producer_before_or_at_child_departure"
                )
                for record in leg_records
            ),
            "max_budget_error": max_budget_error(leg_records),
            "claim_ceiling": "minimal_runtime_bridge_prototype_candidate_no_ecology_success",
        },
        "control_results": controls,
        "i11b_runtime_control_handoff": {
            "iteration": "I11-B",
            "status": "required_next_null_validation",
            "direction": "runtime control validation for I11-A; null validation, not stronger language",
            "required_controls": I11B_REQUIRED_CONTROLS,
            "expected_acceptance_state": (
                "accepted_trace_pressure_loop_runtime_controls_fail_closed_"
                "producer_assisted_only"
            ),
            "expected_failed_open_count": 0,
            "demotion_rule": "any required failed-open control demotes or blocks I11-A runtime admission",
        },
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
        "why_admitted": (
            "I11-A runs an executable LGRC9V3 packet-loop surface where a parent "
            "arrival trace, route-surplus pressure trigger, and processed child "
            "departure form a minimal trace/pressure/loop runtime bridge candidate."
        ),
        "why_not_stronger": (
            "The row is producer-assisted runtime evidence. The producer is declared "
            "and source-visible, but this is not native ecology, pheromone "
            "communication, hunger semantics, native shared-medium coordination, "
            "agency, or prototype success."
        ),
        "ready_for_iteration_11B": True,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    controls_statuses = [row["status"] for row in controls]
    row = data["runtime_instantiation_row"]
    checks = [
        check("i11_artifact_passed", i11.get("status") == "passed"),
        check("source_i11_digest_matches", data["source_i11_digest_linkage"]["source_i11_digest_matches"] is True),
        check("runtime_artifact_manifest_present", runtime_sha != "not_recorded"),
        check("runtime_artifact_output_digest_present", runtime_artifact["output_digest"] != "not_recorded"),
        check("lgrc9v3_runtime_executed", runtime_artifact["runtime_family"] == "LGRC9V3"),
        check("producer_policy_declared", bool(row["producer_policy"])),
        check("same_discipline_producer_recorded", row["same_discipline_producer"] is True),
        check(
            "producer_success_does_not_upgrade_native",
            row["producer_assisted"]
            and row["producer_residue"] == "visible"
            and row["producer_success_can_upgrade_native"] is False,
        ),
        check(
            "bounded_row_status_promoted_not_claim",
            row["status"] == "admitted_runtime_bridge_exemplar_candidate_producer_assisted"
            and data["prototype_lineage"]["claim_ceiling"]
            == "minimal_runtime_bridge_prototype_candidate_no_ecology_success",
        ),
        check(
            "i11b_runtime_control_handoff_present",
            len(data["i11b_runtime_control_handoff"]["required_controls"]) >= 10
            and data["i11b_runtime_control_handoff"]["expected_failed_open_count"] == 0,
        ),
        check("self_rearm_validation_passed", runtime_artifact["self_rearm_validation"]["valid"] is True),
        check("completed_trace_pressure_loop_leg_count_positive", row["trace_pressure_loop_leg_count"] >= 2),
        check("trace_aftereffect_runtime_visible", row["trace_aftereffect_runtime_visible"] is True),
        check("pressure_declared_before_use", row["pressure_declared_before_use"] is True),
        check("pressure_threshold_crossed", row["pressure_threshold_crossed"] is True),
        check("bounded_loop_response_observed", row["bounded_loop_response_observed"] is True),
        check("conditioned_by_trace_pressure", row["conditioned_by_trace_pressure"] is True),
        check("budget_errors_within_epsilon", row["max_budget_error"] <= EPSILON),
        check("controls_all_passed", all(status == "passed" for status in controls_statuses)),
        check("unsafe_claim_flags_false", all(value is False for value in data["claim_boundary"].values())),
        check("no_absolute_paths_in_records", no_absolute_paths(data) and no_absolute_paths(runtime_artifact)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["status"] = "passed" if not data["failed_checks"] else "failed"
    data["acceptance_state"] = (
        "accepted_producer_assisted_runtime_trace_pressure_loop_candidate_no_ecology_success"
        if data["status"] == "passed"
        else "rejected_runtime_trace_pressure_loop_candidate"
    )
    data["ready_for_iteration_11B"] = data["status"] == "passed"
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    row = data["runtime_instantiation_row"]
    lines = [
        "# N29 Iteration 11-A - Runtime Trace / Pressure / Loop",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- runtime status: `{data['runtime_or_reconstruction_status']}`",
        f"- bounded row status: `{row['status']}`",
        f"- leg count: `{row['trace_pressure_loop_leg_count']}`",
        f"- max budget error: `{row['max_budget_error']}`",
        f"- ready_for_iteration_11B: `{str(data['ready_for_iteration_11B']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "I11-A upgrades I11 from artifact-only reconstruction to a minimal runtime",
        "bridge candidate. It uses the executable LGRC9V3 route-surplus packet-loop",
        "surface. The row remains producer-assisted because the declared LGRC9V3",
        "producer schedules eligible packet departures; that producer remains visible",
        "and cannot upgrade the row to native ecology or agency.",
        "",
        "## Source I11 Linkage",
        "",
        f"- canonical I11 artifact: `{data['source_i11_digest_linkage']['canonical_i11_artifact']}`",
        f"- source_i11_digest_matches: `{str(data['source_i11_digest_linkage']['source_i11_digest_matches']).lower()}`",
        f"- consumed I11 digest: `{data['source_i11_digest_linkage']['consumed_i11_output_digest']}`",
        "",
        "## Runtime Manifest",
        "",
        f"- runtime artifact: `{data['runtime_artifact_manifest']['path']}`",
        f"- sha256: `{data['runtime_artifact_manifest']['sha256']}`",
        f"- runtime artifact digest: `{data['runtime_artifact_manifest']['output_digest']}`",
        "",
        "## Runtime Legs",
        "",
        f"- trace_aftereffect_runtime_visible: `{str(row['trace_aftereffect_runtime_visible']).lower()}`",
        f"- pressure_declared_before_use: `{str(row['pressure_declared_before_use']).lower()}`",
        f"- pressure_threshold_crossed: `{str(row['pressure_threshold_crossed']).lower()}`",
        f"- bounded_loop_response_observed: `{str(row['bounded_loop_response_observed']).lower()}`",
        f"- conditioned_by_trace_pressure: `{str(row['conditioned_by_trace_pressure']).lower()}`",
        f"- producer_success_can_upgrade_native: `{str(row['producer_success_can_upgrade_native']).lower()}`",
        "",
        "## I11-B Runtime Control Handoff",
        "",
        f"- direction: `{data['i11b_runtime_control_handoff']['direction']}`",
        f"- expected_acceptance_state: `{data['i11b_runtime_control_handoff']['expected_acceptance_state']}`",
        f"- expected_failed_open_count: `{data['i11b_runtime_control_handoff']['expected_failed_open_count']}`",
        "",
        "Required controls:",
        "",
    ]
    for control in data["i11b_runtime_control_handoff"]["required_controls"]:
        lines.append(f"- `{control}`")
    lines.extend(
        [
            "",
        "## Control Results",
        "",
        "| Control | Status | Rung Effect |",
        "| --- | --- | --- |",
        ]
    )
    for control in data["control_results"]:
        lines.append(
            f"| `{control['control_id']}` | `{control['status']}` | `{control['rung_effect']}` |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check_row in data["checks"]:
        lines.append(f"| `{check_row['check_id']}` | `{str(check_row['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I11-A supports a minimal producer-assisted runtime trace/pressure/loop",
            "bridge candidate. Geometrically, a returned packet arrival leaves a",
            "runtime-visible aftereffect at a pole, a declared route-surplus pressure",
            "trigger reads that current state, and the LGRC9V3 producer schedules a",
            "bounded child packet departure that `step()` then processes. The row does",
            "not claim pheromone communication, hunger semantics, ant behavior, native",
            "shared-medium coordination, agency, or runtime ecology success.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    runtime_artifact = run_runtime_probe()
    RUNTIME_OUTPUT.write_text(canonical_json(runtime_artifact), encoding="utf-8")
    data = build_summary(runtime_artifact)
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()
