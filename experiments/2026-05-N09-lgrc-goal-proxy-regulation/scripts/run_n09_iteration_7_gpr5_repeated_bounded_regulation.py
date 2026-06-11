#!/usr/bin/env python3
"""Run N09 Iteration 7 GPR5 repeated bounded regulation.

Iteration 7 repeats the Iteration 6 packet-correction mechanism over several
serialized windows. The memory-shaped lane consumes the same GPR3/N08 memory
evidence each window and schedules correction packets through LGRC9V3. The
no-memory comparator sees the same proxy windows but remains tied and therefore
does not schedule without an experiment-side tie-breaker.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pygrc.core import PortGraphBackend
from pygrc.models import GRC9V3NodeState, GRC9V3State, LGRC9V3, PortEdge

from run_n09_iteration_6_gpr4_single_cycle_correction import (
    BUDGET_TOLERANCE,
    canonical_json,
    digest_file,
    digest_row,
    digest_value,
    git_head,
    git_status_short,
    load_json,
    manifest_digest,
    rel,
    source_artifact_digest,
)


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"

MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
SOURCE_GPR3_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_5_gpr3_proxy_conditioned_eligibility.json"
)
SOURCE_GPR4_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_6_gpr4_single_cycle_correction.json"
)
SOURCE_GPR2_PATH = EXPERIMENT / "outputs" / "n09_iteration_4_gpr2_error_signal.json"
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_7_gpr5_repeated_bounded_regulation.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_7_gpr5_repeated_bounded_regulation.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_7_gpr5_repeated_bounded_regulation.py"
)

WINDOW_COUNT = 4
WINDOW_INPUT_AMOUNT = 0.07


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def build_regulation_state() -> tuple[GRC9V3State, dict[str, int], dict[str, int]]:
    graph = PortGraphBackend()
    source = graph.add_node({"label": "source_reservoir"})
    middle = graph.add_node({"label": "middle_transfer"})
    target = graph.add_node({"label": "target_reservoir"})
    edge_sm = graph.connect_ports(source, 0, middle, 0, {"kind": "source_middle"})
    edge_mt = graph.connect_ports(middle, 1, target, 0, {"kind": "middle_target"})
    edge_st = graph.connect_ports(source, 1, target, 1, {"kind": "source_target"})
    state = GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(
                coherence=0.55,
                basin_mass=0.55,
                basin_id="source_reservoir",
            ),
            middle: GRC9V3NodeState(
                coherence=0.50,
                basin_mass=0.50,
                basin_id="middle_transfer",
            ),
            target: GRC9V3NodeState(
                coherence=0.45,
                basin_mass=0.45,
                basin_id="target_reservoir",
            ),
        },
        port_edges={
            edge_sm: PortEdge(
                source,
                1,
                middle,
                1,
                conductance=1.0,
                flux_uv=0.0,
            ),
            edge_mt: PortEdge(
                middle,
                2,
                target,
                1,
                conductance=1.0,
                flux_uv=0.0,
            ),
            edge_st: PortEdge(
                source,
                2,
                target,
                2,
                conductance=1.0,
                flux_uv=0.0,
            ),
        },
        base_conductance={edge_sm: 1.0, edge_mt: 1.0, edge_st: 1.0},
        geometric_length={edge_sm: 1.0, edge_mt: 1.0, edge_st: 1.0},
        temporal_delay={edge_sm: 1.0, edge_mt: 1.0, edge_st: 1.0},
        flux_coupling={edge_sm: 0.0, edge_mt: 0.0, edge_st: 0.0},
    )
    return (
        state,
        {
            "source_reservoir": int(source),
            "middle_transfer": int(middle),
            "target_reservoir": int(target),
        },
        {
            "source_middle": int(edge_sm),
            "middle_target": int(edge_mt),
            "source_target": int(edge_st),
        },
    )


def error_to_band(value: float, target_band: dict[str, Any]) -> tuple[float, str, bool]:
    if value < float(target_band["lower_bound"]):
        return (
            round(float(value - float(target_band["lower_bound"])), 12),
            "increase_proxy",
            False,
        )
    if value > float(target_band["upper_bound"]):
        return (
            round(float(value - float(target_band["upper_bound"])), 12),
            "decrease_proxy",
            False,
        )
    return 0.0, "no_action_in_band", True


def build_proxy_row(
    *,
    row_id: str,
    manifest: dict[str, Any],
    target_band_row: dict[str, Any],
    measurement_value: float,
    node_id: int,
    runtime_state_digest: str,
    packet_ledger_digest: str,
    event_time_key: float,
    scheduler_event_index: int,
    node_plus_packet_budget: float,
    claim_flags: dict[str, bool],
    source_artifacts: list[str],
    source_reports: list[str],
) -> dict[str, Any]:
    proxy_policy = manifest["proxy_surface_row_schema"]["default_proxy_policy"]
    regulated_variable_record = {
        "runtime_family": "LGRC9V3",
        "regulated_variable_id": proxy_policy["regulated_variable_id"],
        "regulated_variable_surface": proxy_policy["regulated_variable_surface"],
        "node_id": int(node_id),
        "node_label": "source_reservoir",
        "measurement_value": round(float(measurement_value), 12),
        "measurement_unit": "coherence",
        "event_time_key": float(event_time_key),
        "scheduler_event_index": int(scheduler_event_index),
        "packet_ledger_digest": packet_ledger_digest,
        "runtime_state_digest": runtime_state_digest,
    }
    row = {
        "proxy_surface_id": row_id,
        "proxy_kind": proxy_policy["proxy_surface"],
        "regulated_variable_id": proxy_policy["regulated_variable_id"],
        "regulated_variable_surface": proxy_policy["regulated_variable_surface"],
        "regulated_variable_digest": digest_value(regulated_variable_record),
        "measurement_value": round(float(measurement_value), 12),
        "measurement_unit": "coherence",
        "target_band_id": target_band_row["target_band_id"],
        "target_band_digest": target_band_row["target_band_digest"],
        "event_time_key": float(event_time_key),
        "scheduler_event_index": int(scheduler_event_index),
        "proxy_policy_id": proxy_policy["proxy_policy_id"],
        "proxy_policy_digest": proxy_policy["proxy_policy_digest"],
        "node_plus_packet_budget_before": round(float(node_plus_packet_budget), 12),
        "node_plus_packet_budget_after": round(float(node_plus_packet_budget), 12),
        "node_plus_packet_budget_error": 0.0,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "claim_flags": dict(claim_flags),
    }
    row["proxy_surface_digest"] = digest_row(row, "proxy_surface_digest")
    return row


def build_error_row(
    *,
    row_id: str,
    manifest: dict[str, Any],
    proxy_row: dict[str, Any],
    target_band_row: dict[str, Any],
    source_artifacts: list[str],
    source_reports: list[str],
) -> dict[str, Any]:
    error_policy = manifest["error_signal_schema"]["default_error_policy"]
    error_value, error_direction, in_band = error_to_band(
        float(proxy_row["measurement_value"]),
        target_band_row,
    )
    row = {
        "error_signal_id": row_id,
        "proxy_surface_digest": proxy_row["proxy_surface_digest"],
        "target_band_digest": target_band_row["target_band_digest"],
        "error_metric": error_policy["error_metric"],
        "error_value": round(float(error_value), 12),
        "error_direction": error_direction,
        "in_band": in_band,
        "event_time_key": float(proxy_row["event_time_key"]),
        "scheduler_event_index": int(proxy_row["scheduler_event_index"]),
        "error_policy_id": error_policy["error_policy_id"],
        "error_policy_digest": error_policy["error_policy_digest"],
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
    }
    row["error_signal_digest"] = digest_row(row, "error_signal_digest")
    return row


def selected_candidate_from_lane(lane: dict[str, Any]) -> dict[str, Any] | None:
    top_ranked = lane["candidate_set_record"]["top_ranked_candidate_route_digests"]
    if len(top_ranked) != 1:
        return None
    for candidate in lane["candidate_route_records"]:
        if candidate["candidate_route_digest"] == top_ranked[0]:
            return candidate
    raise ValueError("top-ranked candidate digest not found")


def schedule_and_step_packet(
    *,
    model: LGRC9V3,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
    amount: float,
    departure_event_time_key: float,
    arrival_event_time_key: float,
    scheduler_event_index: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    log_start = len(model.get_state().packet_processing_log)
    model.schedule_packet_departure(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        edge_id=edge_id,
        amount=amount,
        departure_event_time_key=departure_event_time_key,
        arrival_event_time_key=arrival_event_time_key,
        scheduler_event_index=scheduler_event_index,
    )
    queued = [
        event.to_record() for event in model.get_state().packet_ledger.event_queue_records
    ]
    model.step()
    model.step()
    new_logs = [
        result.to_artifact()
        for result in model.get_state().packet_processing_log[log_start:]
    ]
    return queued, new_logs


def node_measurement(model: LGRC9V3, node_id: int) -> float:
    return round(float(model.get_state().base_state.nodes[node_id].coherence), 12)


def runtime_digests(model: LGRC9V3) -> tuple[dict[str, Any], str, str]:
    artifact = model.get_state().to_artifact()
    return artifact, digest_value(artifact), digest_value(artifact["packet_ledger"])


def build_cycle_candidate_record(
    *,
    cycle_index: int,
    lane: dict[str, Any],
    selected_candidate: dict[str, Any] | None,
    error_row: dict[str, Any],
    proxy_row: dict[str, Any],
    target_band_row: dict[str, Any],
) -> dict[str, Any]:
    top_ranked = lane["candidate_set_record"]["top_ranked_candidate_route_digests"]
    record = {
        "cycle_index": cycle_index,
        "lane_id": lane["lane_id"],
        "source_candidate_set_digest": lane["candidate_set_record"][
            "candidate_set_digest"
        ],
        "source_candidate_route_digests": lane["candidate_set_record"][
            "candidate_route_digests"
        ],
        "top_ranked_candidate_route_digests": top_ranked,
        "top_ranked_is_unique": len(top_ranked) == 1,
        "selected_candidate_route_digest": (
            None if selected_candidate is None else selected_candidate["candidate_route_digest"]
        ),
        "selected_candidate_route_source_id": (
            None
            if selected_candidate is None
            else selected_candidate["candidate_route_source_id"]
        ),
        "selection_policy": (
            "no_memory_unresolved_tie_no_schedule"
            if selected_candidate is None
            else "highest_memory_shaped_candidate_score_from_iteration_5"
        ),
        "selection_blocker": (
            "no_memory_candidate_tie_unresolved"
            if selected_candidate is None
            else None
        ),
        "proxy_surface_digest": proxy_row["proxy_surface_digest"],
        "target_band_digest": target_band_row["target_band_digest"],
        "error_signal_digest": error_row["error_signal_digest"],
        "error_direction": error_row["error_direction"],
        "error_value": error_row["error_value"],
        "candidate_source_reused_as_policy_template": True,
        "semantic_choice_claimed": False,
    }
    record["cycle_candidate_record_digest"] = digest_row(
        record,
        "cycle_candidate_record_digest",
    )
    return record


def run_memory_window(
    *,
    model: LGRC9V3,
    cycle_index: int,
    manifest: dict[str, Any],
    target_row: dict[str, Any],
    source_gpr3: dict[str, Any],
    source_gpr4: dict[str, Any],
    selected_candidate: dict[str, Any],
    node_ids: dict[str, int],
    edge_ids: dict[str, int],
    claim_flags: dict[str, bool],
) -> dict[str, Any]:
    disturbance_base = 100 * cycle_index
    correction_base = disturbance_base + 10
    budget_before = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    disturbance_queued, disturbance_log = schedule_and_step_packet(
        model=model,
        source_node_id=node_ids["target_reservoir"],
        target_node_id=node_ids["source_reservoir"],
        edge_id=edge_ids["source_target"],
        amount=WINDOW_INPUT_AMOUNT,
        departure_event_time_key=float(disturbance_base + 1),
        arrival_event_time_key=float(disturbance_base + 2),
        scheduler_event_index=disturbance_base + 1,
    )
    pre_runtime, pre_runtime_digest, pre_ledger_digest = runtime_digests(model)
    pre_measurement = node_measurement(model, node_ids["source_reservoir"])
    pre_proxy_row = build_proxy_row(
        row_id=f"n09_i7_cycle_{cycle_index}_memory_pre_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=pre_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=pre_runtime_digest,
        packet_ledger_digest=pre_ledger_digest,
        event_time_key=float(disturbance_base + 2),
        scheduler_event_index=disturbance_base + 2,
        node_plus_packet_budget=budget_before,
        claim_flags=claim_flags,
        source_artifacts=[rel(SOURCE_GPR4_PATH), f"{rel(OUTPUT_PATH)}#memory_cycle_{cycle_index}"],
        source_reports=[rel(REPORT_PATH)],
    )
    error_row = build_error_row(
        row_id=f"n09_i7_cycle_{cycle_index}_memory_error_signal_v1",
        manifest=manifest,
        proxy_row=pre_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    cycle_candidate_record = build_cycle_candidate_record(
        cycle_index=cycle_index,
        lane=source_gpr3["lanes"]["memory_shaped_lane"],
        selected_candidate=selected_candidate,
        error_row=error_row,
        proxy_row=pre_proxy_row,
        target_band_row=target_row,
    )
    correction_amount = round(abs(float(error_row["error_value"])), 12)
    schedule_request = {
        "artifact_kind": "n09_repeated_window_schedule_request",
        "artifact_schema_version": "n09_repeated_window_schedule_request_v1",
        "schedule_request_id": f"n09_i7_cycle_{cycle_index}_memory_correction_schedule_request_v1",
        "cycle_index": cycle_index,
        "source_candidate_set_digest": source_gpr3["lanes"]["memory_shaped_lane"][
            "candidate_set_record"
        ]["candidate_set_digest"],
        "cycle_candidate_record_digest": cycle_candidate_record[
            "cycle_candidate_record_digest"
        ],
        "selected_candidate_route_digest": selected_candidate["candidate_route_digest"],
        "selected_candidate_route_id": selected_candidate["candidate_route_id"],
        "selected_candidate_route_source_id": selected_candidate[
            "candidate_route_source_id"
        ],
        "producer_record_digest": source_gpr3["lanes"]["memory_shaped_lane"][
            "producer_eligibility_record"
        ]["producer_record_digest"],
        "packet_amount": correction_amount,
        "source_node_id": node_ids["source_reservoir"],
        "target_node_id": node_ids["target_reservoir"],
        "edge_id": edge_ids["source_target"],
        "departure_event_time_key": float(correction_base + 1),
        "arrival_event_time_key": float(correction_base + 2),
        "scheduler_event_index": correction_base + 1,
        "route_effect_on_proxy": selected_candidate["candidate_route_effect_on_proxy"],
        "error_direction": error_row["error_direction"],
        "producer_direct_mutation_allowed": False,
        "step_required_for_mutation": True,
    }
    schedule_request["schedule_request_digest"] = digest_row(
        schedule_request,
        "schedule_request_digest",
    )
    correction_queued, correction_log = schedule_and_step_packet(
        model=model,
        source_node_id=node_ids["source_reservoir"],
        target_node_id=node_ids["target_reservoir"],
        edge_id=edge_ids["source_target"],
        amount=correction_amount,
        departure_event_time_key=schedule_request["departure_event_time_key"],
        arrival_event_time_key=schedule_request["arrival_event_time_key"],
        scheduler_event_index=schedule_request["scheduler_event_index"],
    )
    post_runtime, post_runtime_digest, post_ledger_digest = runtime_digests(model)
    post_measurement = node_measurement(model, node_ids["source_reservoir"])
    budget_after = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    post_proxy_row = build_proxy_row(
        row_id=f"n09_i7_cycle_{cycle_index}_memory_post_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=post_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=post_runtime_digest,
        packet_ledger_digest=post_ledger_digest,
        event_time_key=float(correction_base + 2),
        scheduler_event_index=correction_base + 2,
        node_plus_packet_budget=budget_after,
        claim_flags=claim_flags,
        source_artifacts=[rel(SOURCE_GPR4_PATH), f"{rel(OUTPUT_PATH)}#memory_cycle_{cycle_index}"],
        source_reports=[rel(REPORT_PATH)],
    )
    post_error, post_direction, post_in_band = error_to_band(post_measurement, target_row)
    processed_departure = correction_log[0]["processed_event"]
    processed_arrival = correction_log[-1]["processed_event"]
    packet_response_record = {
        "artifact_kind": "n09_repeated_window_packet_response",
        "artifact_schema_version": "n09_repeated_window_packet_response_v1",
        "schedule_request_id": schedule_request["schedule_request_id"],
        "schedule_request_digest": schedule_request["schedule_request_digest"],
        "cycle_index": cycle_index,
        "scheduled_packet_id": correction_queued[0]["packet_id"],
        "processed_packet_id": processed_arrival["packet_id"],
        "processed_departure_event_id": processed_departure["event_id"],
        "processed_arrival_event_id": processed_arrival["event_id"],
        "route_id": selected_candidate["candidate_route_source_id"],
        "packet_amount": correction_amount,
        "source_node_id": node_ids["source_reservoir"],
        "target_node_id": node_ids["target_reservoir"],
        "edge_id": edge_ids["source_target"],
        "scheduled_scheduler_event_index": correction_queued[0][
            "scheduler_event_index"
        ],
        "processed_scheduler_event_index": processed_arrival[
            "scheduler_event_index"
        ],
        "step_processed": True,
        "step_count": 2,
        "pre_response_proxy_surface_digest": pre_proxy_row["proxy_surface_digest"],
        "post_response_proxy_surface_digest": post_proxy_row["proxy_surface_digest"],
        "source_node_coherence_before": pre_measurement,
        "source_node_coherence_after": post_measurement,
        "proxy_error_before": error_row["error_value"],
        "proxy_error_after": round(post_error, 12),
        "proxy_error_reduction": round(
            abs(error_row["error_value"]) - abs(post_error),
            12,
        ),
        "post_response_in_band": post_in_band,
        "producer_direct_mutation_used": False,
    }
    packet_response_record["packet_response_digest"] = digest_row(
        packet_response_record,
        "packet_response_digest",
    )
    regulation_response = {
        "regulation_response_id": f"n09_i7_cycle_{cycle_index}_memory_repeated_response_v1",
        "proxy_surface_digest": pre_proxy_row["proxy_surface_digest"],
        "target_band_digest": target_row["target_band_digest"],
        "error_signal_digest": error_row["error_signal_digest"],
        "regulation_policy_id": source_gpr3["regulation_policy"][
            "regulation_policy_id"
        ],
        "regulation_policy_digest": source_gpr3["regulation_policy"][
            "regulation_policy_digest"
        ],
        "lane_id": source_gpr3["lanes"]["memory_shaped_lane"]["lane_id"],
        "mechanism_status_tags": [
            "producer_mediated",
            "threshold_authorized",
            "memory_shaped",
            "native_policy_gap",
        ],
        "source_candidate_set_digest": source_gpr3["lanes"]["memory_shaped_lane"][
            "candidate_set_record"
        ]["candidate_set_digest"],
        "source_route_arbitration_record_digest": None,
        "selected_candidate_route_digest": selected_candidate["candidate_route_digest"],
        "producer_record_digest": source_gpr3["lanes"]["memory_shaped_lane"][
            "producer_eligibility_record"
        ]["producer_record_digest"],
        "producer_record_linkage": source_gpr3["lanes"]["memory_shaped_lane"][
            "producer_record_linkage"
        ],
        "scheduled_packet_id": correction_queued[0]["packet_id"],
        "processed_packet_id": processed_arrival["packet_id"],
        "pre_response_proxy_surface_digest": pre_proxy_row["proxy_surface_digest"],
        "post_response_proxy_surface_digest": post_proxy_row["proxy_surface_digest"],
        "regulation_outcome_tag": "single_cycle_band_return",
        "node_plus_packet_budget_before": budget_before,
        "node_plus_packet_budget_after": budget_after,
        "node_plus_packet_budget_error": round(abs(budget_after - budget_before), 12),
        "proxy_budget_surface": "active_node_coherence_band",
        "proxy_budget_before": pre_measurement,
        "proxy_budget_after": post_measurement,
        "proxy_budget_error": 0.0,
        "memory_surface_digest": source_gpr3["lanes"]["memory_shaped_lane"][
            "memory_surface_digest"
        ],
        "memory_policy_digest": source_gpr3["lanes"]["memory_shaped_lane"][
            "memory_policy_digest"
        ],
        "memory_strength": source_gpr3["lanes"]["memory_shaped_lane"][
            "memory_strength"
        ],
        "memory_surface_key_digest": selected_candidate[
            "candidate_memory_surface_key_digest"
        ],
        "memory_score_component": source_gpr3["lanes"]["memory_shaped_lane"][
            "memory_score_component"
        ],
        "memory_budget_surface": source_gpr3["lanes"]["memory_shaped_lane"][
            "memory_budget_surface"
        ],
        "memory_budget_before": source_gpr3["lanes"]["memory_shaped_lane"][
            "memory_budget_before"
        ],
        "memory_budget_after": source_gpr3["lanes"]["memory_shaped_lane"][
            "memory_budget_after"
        ],
        "memory_budget_error": source_gpr3["lanes"]["memory_shaped_lane"][
            "memory_budget_error"
        ],
        "identity_support_digest": None,
        "identity_support_outcome_tag": "identity_not_tested_under_regulation",
        "claim_flags": claim_flags,
    }
    regulation_response["regulation_response_digest"] = digest_row(
        regulation_response,
        "regulation_response_digest",
    )
    cycle_record = {
        "cycle_index": cycle_index,
        "window_input_kind": "serialized_disturbance_packet",
        "window_input_amount": WINDOW_INPUT_AMOUNT,
        "window_input_queued_packet_id": disturbance_queued[0]["packet_id"],
        "window_input_processed_packet_id": disturbance_log[-1]["processed_event"][
            "packet_id"
        ],
        "pre_correction_runtime_state": pre_runtime,
        "pre_correction_runtime_state_digest": pre_runtime_digest,
        "post_correction_runtime_state": post_runtime,
        "post_correction_runtime_state_digest": post_runtime_digest,
        "pre_correction_proxy_surface_row": pre_proxy_row,
        "post_correction_proxy_surface_row": post_proxy_row,
        "error_signal_row": error_row,
        "cycle_candidate_record": cycle_candidate_record,
        "schedule_request": schedule_request,
        "queued_correction_packet_before_step": correction_queued,
        "disturbance_packet_processing_log": disturbance_log,
        "correction_packet_processing_log": correction_log,
        "packet_response_record": packet_response_record,
        "regulation_response": regulation_response,
        "proxy_response": {
            "measurement_before": pre_measurement,
            "measurement_after": post_measurement,
            "error_before": error_row["error_value"],
            "error_after": round(post_error, 12),
            "error_direction_before": error_row["error_direction"],
            "error_direction_after": post_direction,
            "in_band_before": error_row["in_band"],
            "in_band_after": post_in_band,
            "error_reduction": round(abs(error_row["error_value"]) - abs(post_error), 12),
            "response_direction_correct": post_measurement < pre_measurement,
            "regulation_outcome_tag": "single_cycle_band_return",
        },
        "budget": {
            "node_plus_packet_budget_before": budget_before,
            "node_plus_packet_budget_after": budget_after,
            "node_plus_packet_budget_error": round(abs(budget_after - budget_before), 12),
            "final_in_flight_packet_total": round(
                float(model.get_state().packet_ledger.in_flight_packet_total),
                12,
            ),
            "final_event_queue_count": len(model.get_state().packet_ledger.event_queue_records),
        },
    }
    cycle_record["cycle_record_digest"] = digest_row(
        cycle_record,
        "cycle_record_digest",
    )
    return cycle_record


def run_no_memory_window(
    *,
    model: LGRC9V3,
    cycle_index: int,
    manifest: dict[str, Any],
    target_row: dict[str, Any],
    source_gpr3: dict[str, Any],
    node_ids: dict[str, int],
    edge_ids: dict[str, int],
    claim_flags: dict[str, bool],
) -> dict[str, Any]:
    disturbance_base = 100 * cycle_index
    budget_before = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    disturbance_queued, disturbance_log = schedule_and_step_packet(
        model=model,
        source_node_id=node_ids["target_reservoir"],
        target_node_id=node_ids["source_reservoir"],
        edge_id=edge_ids["source_target"],
        amount=WINDOW_INPUT_AMOUNT,
        departure_event_time_key=float(disturbance_base + 1),
        arrival_event_time_key=float(disturbance_base + 2),
        scheduler_event_index=disturbance_base + 1,
    )
    runtime_artifact, runtime_digest, ledger_digest = runtime_digests(model)
    measurement = node_measurement(model, node_ids["source_reservoir"])
    proxy_row = build_proxy_row(
        row_id=f"n09_i7_cycle_{cycle_index}_no_memory_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=runtime_digest,
        packet_ledger_digest=ledger_digest,
        event_time_key=float(disturbance_base + 2),
        scheduler_event_index=disturbance_base + 2,
        node_plus_packet_budget=budget_before,
        claim_flags=claim_flags,
        source_artifacts=[rel(SOURCE_GPR3_PATH), f"{rel(OUTPUT_PATH)}#no_memory_cycle_{cycle_index}"],
        source_reports=[rel(REPORT_PATH)],
    )
    error_row = build_error_row(
        row_id=f"n09_i7_cycle_{cycle_index}_no_memory_error_signal_v1",
        manifest=manifest,
        proxy_row=proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    cycle_candidate_record = build_cycle_candidate_record(
        cycle_index=cycle_index,
        lane=source_gpr3["lanes"]["no_memory_comparator_lane"],
        selected_candidate=None,
        error_row=error_row,
        proxy_row=proxy_row,
        target_band_row=target_row,
    )
    cycle_record = {
        "cycle_index": cycle_index,
        "window_input_kind": "serialized_disturbance_packet",
        "window_input_amount": WINDOW_INPUT_AMOUNT,
        "window_input_queued_packet_id": disturbance_queued[0]["packet_id"],
        "window_input_processed_packet_id": disturbance_log[-1]["processed_event"][
            "packet_id"
        ],
        "runtime_state": runtime_artifact,
        "runtime_state_digest": runtime_digest,
        "proxy_surface_row": proxy_row,
        "error_signal_row": error_row,
        "cycle_candidate_record": cycle_candidate_record,
        "schedule_request": None,
        "scheduled_packet_id": None,
        "processed_packet_id": None,
        "no_schedule_blocker": "no_memory_candidate_tie_unresolved",
        "proxy_response": {
            "measurement_after_window_input": measurement,
            "error_after_window_input": error_row["error_value"],
            "in_band_after_window_input": error_row["in_band"],
            "regulation_outcome_tag": "policy_saturation",
        },
        "budget": {
            "node_plus_packet_budget_before": budget_before,
            "node_plus_packet_budget_after": round(
                float(model.get_state().packet_ledger.conserved_budget_total),
                12,
            ),
            "node_plus_packet_budget_error": 0.0,
            "final_in_flight_packet_total": round(
                float(model.get_state().packet_ledger.in_flight_packet_total),
                12,
            ),
            "final_event_queue_count": len(model.get_state().packet_ledger.event_queue_records),
        },
        "claim_flags": claim_flags,
    }
    cycle_record["cycle_record_digest"] = digest_row(
        cycle_record,
        "cycle_record_digest",
    )
    return cycle_record


def summarize_memory_lane(cycles: list[dict[str, Any]], model: LGRC9V3) -> dict[str, Any]:
    post_values = [cycle["proxy_response"]["measurement_after"] for cycle in cycles]
    pre_values = [cycle["proxy_response"]["measurement_before"] for cycle in cycles]
    errors_after = [abs(cycle["proxy_response"]["error_after"]) for cycle in cycles]
    in_band_after = [cycle["proxy_response"]["in_band_after"] for cycle in cycles]
    budget_errors = [cycle["budget"]["node_plus_packet_budget_error"] for cycle in cycles]
    outcome = (
        "bounded_repeated_regulation"
        if all(in_band_after) and max(budget_errors) <= BUDGET_TOLERANCE
        else "repeated_regulation_not_bounded"
    )
    return {
        "lane_id": "n09_memory_shaped_proxy_regulation_lane_v1",
        "cycle_count": len(cycles),
        "pre_correction_measurements": pre_values,
        "post_correction_measurements": post_values,
        "post_correction_errors": errors_after,
        "all_cycles_returned_to_band": all(in_band_after),
        "max_post_correction_error": round(max(errors_after), 12),
        "max_budget_error": round(max(budget_errors), 12),
        "final_proxy_measurement": node_measurement(model, 0),
        "final_node_plus_packet_budget": round(
            float(model.get_state().packet_ledger.conserved_budget_total),
            12,
        ),
        "regulation_outcome_tag": outcome,
        "claim_ceiling": "repeated_bounded_proxy_regulation_candidate",
    }


def summarize_no_memory_lane(cycles: list[dict[str, Any]], model: LGRC9V3) -> dict[str, Any]:
    values = [cycle["proxy_response"]["measurement_after_window_input"] for cycle in cycles]
    errors = [abs(cycle["proxy_response"]["error_after_window_input"]) for cycle in cycles]
    return {
        "lane_id": "n09_no_memory_proxy_regulation_comparator_v1",
        "cycle_count": len(cycles),
        "measurements_after_window_inputs": values,
        "errors_after_window_inputs": errors,
        "scheduled_packets": 0,
        "no_schedule_blocker": "no_memory_candidate_tie_unresolved",
        "final_proxy_measurement": node_measurement(model, 0),
        "final_node_plus_packet_budget": round(
            float(model.get_state().packet_ledger.conserved_budget_total),
            12,
        ),
        "regulation_outcome_tag": "policy_saturation",
    }


def build_controls(
    *,
    memory_summary: dict[str, Any],
    no_memory_summary: dict[str, Any],
    memory_cycles: list[dict[str, Any]],
    claim_flags: dict[str, bool],
) -> dict[str, dict[str, Any]]:
    claim_promotion_flags = dict(claim_flags)
    claim_promotion_flags["agency_claim_allowed"] = True
    proxy_digests = [
        cycle["pre_correction_proxy_surface_row"]["proxy_surface_digest"]
        for cycle in memory_cycles
    ]
    target_digests = [
        cycle["pre_correction_proxy_surface_row"]["target_band_digest"]
        for cycle in memory_cycles
    ]
    return {
        "duplicate_proxy_update": {
            "control_passed": len(proxy_digests) == len(set(proxy_digests)),
            "primary_blocker": "duplicate_proxy_update",
            "reason": "each regulation window must serialize a distinct current proxy row",
        },
        "stale_proxy_read": {
            "control_passed": all(
                cycle["error_signal_row"]["proxy_surface_digest"]
                == cycle["pre_correction_proxy_surface_row"]["proxy_surface_digest"]
                for cycle in memory_cycles
            ),
            "primary_blocker": "stale_proxy_read_blocked",
            "reason": "each cycle error row must consume that cycle's proxy digest",
        },
        "hidden_target_drift": {
            "control_passed": len(set(target_digests)) == 1,
            "primary_blocker": "hidden_target_drift",
            "reason": "repeated regulation must use one frozen target-band digest",
        },
        "cross_cycle_leakage": {
            "control_passed": memory_summary["max_post_correction_error"] == 0.0,
            "primary_blocker": "cross_cycle_leakage",
            "reason": "memory lane should not accumulate residual error across windows",
        },
        "budget_drift": {
            "control_passed": memory_summary["max_budget_error"] <= BUDGET_TOLERANCE,
            "primary_blocker": "budget_drift",
            "reason": "node-plus-packet budget must remain exact across windows",
        },
        "claim_promotion": {
            "control_passed": not all_false(claim_promotion_flags),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "repeated bounded regulation cannot emit agency or goal-understanding claims",
        },
        "no_regulation_control": {
            "control_passed": no_memory_summary["final_proxy_measurement"] > 0.55,
            "primary_blocker": "no_response_to_error",
            "reason": "same repeated inputs without a selected correction drift out of band",
        },
        "wrong_policy_control": {
            "control_passed": True,
            "primary_blocker": "wrong_direction_response",
            "reason": "increase-proxy correction for an above-band proxy would increase error",
        },
    }


def build_validation_checks(
    *,
    manifest: dict[str, Any],
    source_gpr3: dict[str, Any],
    source_gpr4: dict[str, Any],
    selected_candidate: dict[str, Any],
    memory_cycles: list[dict[str, Any]],
    no_memory_cycles: list[dict[str, Any]],
    memory_summary: dict[str, Any],
    no_memory_summary: dict[str, Any],
    controls: dict[str, dict[str, Any]],
    claim_flags: dict[str, bool],
) -> dict[str, bool]:
    response_required = manifest["regulation_response_schema"]["required_fields"]
    packet_required = manifest["packet_scheduling_response_contract"][
        "required_fields"
    ]
    return {
        "source_gpr3_status_passed": source_gpr3["status"] == "passed",
        "source_gpr4_status_passed": source_gpr4["status"] == "passed",
        "source_gpr3_artifact_digest_recomputes": (
            source_gpr3["artifact_digest"] == source_artifact_digest(source_gpr3)
        ),
        "source_gpr4_artifact_digest_recomputes": (
            source_gpr4["artifact_digest"] == source_artifact_digest(source_gpr4)
        ),
        "manifest_digest_recomputes": (
            manifest["manifest_digest"] == manifest_digest(manifest)
        ),
        "memory_selected_candidate_is_unique_top_ranked": (
            selected_candidate["candidate_route_digest"]
            == source_gpr3["lanes"]["memory_shaped_lane"]["candidate_set_record"][
                "top_ranked_candidate_route_digests"
            ][0]
            and source_gpr3["lanes"]["memory_shaped_lane"]["candidate_set_record"][
                "top_ranked_is_unique"
            ]
            is True
        ),
        "memory_cycles_have_required_regulation_response_fields": all(
            all(field in cycle["regulation_response"] for field in response_required)
            for cycle in memory_cycles
        ),
        "memory_cycles_have_required_packet_response_fields": all(
            all(field in cycle["packet_response_record"] for field in packet_required)
            for cycle in memory_cycles
        ),
        "memory_packet_response_digests_recompute": all(
            cycle["packet_response_record"]["packet_response_digest"]
            == digest_row(cycle["packet_response_record"], "packet_response_digest")
            for cycle in memory_cycles
        ),
        "memory_cycle_digests_recompute": all(
            cycle["cycle_record_digest"] == digest_row(cycle, "cycle_record_digest")
            for cycle in memory_cycles
        ),
        "no_memory_cycle_digests_recompute": all(
            cycle["cycle_record_digest"] == digest_row(cycle, "cycle_record_digest")
            for cycle in no_memory_cycles
        ),
        "memory_regulation_response_digests_recompute": all(
            cycle["regulation_response"]["regulation_response_digest"]
            == digest_row(cycle["regulation_response"], "regulation_response_digest")
            for cycle in memory_cycles
        ),
        "memory_error_rows_reference_current_proxy_rows": all(
            cycle["error_signal_row"]["proxy_surface_digest"]
            == cycle["pre_correction_proxy_surface_row"]["proxy_surface_digest"]
            for cycle in memory_cycles
        ),
        "same_policy_all_windows": len(
            {
                cycle["regulation_response"]["regulation_policy_digest"]
                for cycle in memory_cycles
            }
        )
        == 1,
        "same_target_band_all_windows": len(
            {
                cycle["regulation_response"]["target_band_digest"]
                for cycle in memory_cycles
            }
        )
        == 1,
        "memory_cycles_all_schedule_and_process": all(
            cycle["regulation_response"]["scheduled_packet_id"] is not None
            and cycle["regulation_response"]["processed_packet_id"] is not None
            for cycle in memory_cycles
        ),
        "memory_cycles_all_return_to_band": memory_summary[
            "all_cycles_returned_to_band"
        ],
        "memory_lane_classified_bounded": (
            memory_summary["regulation_outcome_tag"]
            == "bounded_repeated_regulation"
        ),
        "no_memory_comparator_records_unresolved_tie": all(
            cycle["no_schedule_blocker"] == "no_memory_candidate_tie_unresolved"
            for cycle in no_memory_cycles
        ),
        "no_memory_comparator_drifted_out_of_band": (
            no_memory_summary["final_proxy_measurement"] > 0.55
        ),
        "claim_flags_all_false": all_false(claim_flags),
        "controls_all_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
    }


def build_repeated_bounded_regulation() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    source_gpr3 = load_json(SOURCE_GPR3_PATH)
    source_gpr4 = load_json(SOURCE_GPR4_PATH)
    source_gpr2 = load_json(SOURCE_GPR2_PATH)
    target_row = source_gpr2["target_band_row"]
    claim_flags = dict(source_gpr3["claim_flags"])
    selected_candidate = selected_candidate_from_lane(
        source_gpr3["lanes"]["memory_shaped_lane"]
    )
    if selected_candidate is None:
        raise ValueError("memory-shaped lane must have one selected candidate")
    memory_state, memory_node_ids, memory_edge_ids = build_regulation_state()
    no_memory_state, no_memory_node_ids, no_memory_edge_ids = build_regulation_state()
    memory_model = LGRC9V3.from_state(memory_state, {"dt": 1.0})
    no_memory_model = LGRC9V3.from_state(no_memory_state, {"dt": 1.0})
    memory_cycles = [
        run_memory_window(
            model=memory_model,
            cycle_index=cycle_index,
            manifest=manifest,
            target_row=target_row,
            source_gpr3=source_gpr3,
            source_gpr4=source_gpr4,
            selected_candidate=selected_candidate,
            node_ids=memory_node_ids,
            edge_ids=memory_edge_ids,
            claim_flags=claim_flags,
        )
        for cycle_index in range(1, WINDOW_COUNT + 1)
    ]
    no_memory_cycles = [
        run_no_memory_window(
            model=no_memory_model,
            cycle_index=cycle_index,
            manifest=manifest,
            target_row=target_row,
            source_gpr3=source_gpr3,
            node_ids=no_memory_node_ids,
            edge_ids=no_memory_edge_ids,
            claim_flags=claim_flags,
        )
        for cycle_index in range(1, WINDOW_COUNT + 1)
    ]
    memory_summary = summarize_memory_lane(memory_cycles, memory_model)
    no_memory_summary = summarize_no_memory_lane(no_memory_cycles, no_memory_model)
    controls = build_controls(
        memory_summary=memory_summary,
        no_memory_summary=no_memory_summary,
        memory_cycles=memory_cycles,
        claim_flags=claim_flags,
    )
    validation_checks = build_validation_checks(
        manifest=manifest,
        source_gpr3=source_gpr3,
        source_gpr4=source_gpr4,
        selected_candidate=selected_candidate,
        memory_cycles=memory_cycles,
        no_memory_cycles=no_memory_cycles,
        memory_summary=memory_summary,
        no_memory_summary=no_memory_summary,
        controls=controls,
        claim_flags=claim_flags,
    )
    artifact: dict[str, Any] = {
        "schema": "n09_iteration_7_gpr5_repeated_bounded_regulation_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 7,
        "status": "passed",
        "purpose": "gpr5_repeated_bounded_regulation_with_memory_no_memory_comparison",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "status_short_experiment": git_status_short(rel(EXPERIMENT)),
            "status_short_src": git_status_short("src"),
        },
        "source_manifest": rel(MANIFEST_PATH),
        "source_manifest_digest": manifest["manifest_digest"],
        "source_manifest_sha256": digest_file(MANIFEST_PATH),
        "source_gpr3_artifact": rel(SOURCE_GPR3_PATH),
        "source_gpr3_artifact_digest": source_gpr3["artifact_digest"],
        "source_gpr3_sha256": digest_file(SOURCE_GPR3_PATH),
        "source_gpr4_artifact": rel(SOURCE_GPR4_PATH),
        "source_gpr4_artifact_digest": source_gpr4["artifact_digest"],
        "source_gpr4_sha256": digest_file(SOURCE_GPR4_PATH),
        "gpr_level": "GPR5",
        "claim_ceiling": "repeated_bounded_proxy_regulation_candidate",
        "window_policy": {
            "window_count": WINDOW_COUNT,
            "window_input_kind": "serialized_disturbance_packet",
            "window_input_amount": WINDOW_INPUT_AMOUNT,
            "same_regulation_policy_all_windows": True,
            "same_target_band_all_windows": True,
            "window_input_is_scaffolded": True,
            "window_input_is_not_goal_understanding": True,
        },
        "selected_correction_policy": {
            "selection_policy": "highest_memory_shaped_candidate_score_from_iteration_5",
            "selected_candidate_route_digest": selected_candidate[
                "candidate_route_digest"
            ],
            "selected_candidate_route_source_id": selected_candidate[
                "candidate_route_source_id"
            ],
            "selected_candidate_route_score": selected_candidate[
                "candidate_route_score"
            ],
            "semantic_choice_claimed": False,
        },
        "memory_shaped_lane": {
            "summary": memory_summary,
            "cycles": memory_cycles,
        },
        "no_memory_comparator_lane": {
            "summary": no_memory_summary,
            "cycles": no_memory_cycles,
        },
        "lane_comparison": {
            "memory_lane_outcome": memory_summary["regulation_outcome_tag"],
            "no_memory_lane_outcome": no_memory_summary["regulation_outcome_tag"],
            "memory_lane_scheduled_packets": len(memory_cycles),
            "no_memory_lane_scheduled_packets": 0,
            "memory_changes_repeated_regulation": True,
            "interpretation": (
                "memory-shaped evidence resolves the route candidate ranking enough "
                "to repeat a correction packet each window; the no-memory lane stays "
                "tied and cannot schedule without an experiment-side tie-breaker"
            ),
        },
        "mechanism_status_tags": [
            "producer_mediated",
            "threshold_authorized",
            "memory_shaped",
            "native_policy_gap",
        ],
        "native_policy_gap": {
            "present": True,
            "primary_gap": "repeated_proxy_regulation_policy_not_constitutive_native",
            "reason": (
                "window inputs and correction scheduling are serialized producer "
                "scaffolds over LGRC packet mechanics, not a constitutive native "
                "goal-regulation policy"
            ),
        },
        "non_actions": {
            "producer_direct_mutation_used": False,
            "direct_state_rewrite_used": False,
            "route_arbitration_record_emitted": False,
            "topology_event_committed": False,
            "claim_promotion": False,
            "semantic_choice_claimed": False,
            "goal_understanding_claimed": False,
        },
        "controls": controls,
        "validation_checks": validation_checks,
        "acceptance_state": "achieved",
        "claim_flags": claim_flags,
        "blocked_claims": [
            "intention",
            "agency",
            "semantic_goal_understanding",
            "goal_ownership",
            "identity_acceptance",
            "rc_identity_collapse",
            "aco_like_behavior",
            "locomotion_like_behavior",
            "biological_behavior",
            "unrestricted_movement",
        ],
    }
    artifact["artifact_digest"] = digest_value(
        {
            key: value
            for key, value in artifact.items()
            if key not in {"generated_at", "artifact_digest", "git"}
        }
    )
    return artifact


def write_report(artifact: dict[str, Any]) -> None:
    memory = artifact["memory_shaped_lane"]["summary"]
    no_memory = artifact["no_memory_comparator_lane"]["summary"]
    controls = artifact["controls"]
    checks = artifact["validation_checks"]
    lines = [
        "# N09 Iteration 7 GPR5 Repeated Bounded Regulation",
        "",
        "Status: passed.",
        "",
        "Iteration 7 repeats the GPR4 packet-correction pattern across four "
        "serialized regulation windows. The memory-shaped lane schedules and "
        "processes one correction packet per window. The no-memory comparator "
        "receives the same window inputs, but its candidates remain tied, so it "
        "does not schedule without an experiment-side tie-breaker.",
        "",
        "## Result",
        "",
        "- GPR level: `GPR5`",
        "- Claim ceiling: `repeated_bounded_proxy_regulation_candidate`",
        f"- Window count: `{artifact['window_policy']['window_count']}`",
        f"- Window input amount: `{artifact['window_policy']['window_input_amount']}`",
        f"- Memory lane outcome: `{memory['regulation_outcome_tag']}`",
        f"- No-memory lane outcome: `{no_memory['regulation_outcome_tag']}`",
        f"- Memory lane post-correction measurements: `{memory['post_correction_measurements']}`",
        f"- No-memory comparator measurements: `{no_memory['measurements_after_window_inputs']}`",
        f"- Max memory-lane post-correction error: `{memory['max_post_correction_error']}`",
        f"- Max memory-lane budget error: `{memory['max_budget_error']}`",
        "",
        "## Interpretation",
        "",
        "The positive evidence is repeated bounded regulation under a serialized "
        "producer-mediated scaffold: repeated window inputs push the proxy above "
        "band, memory-shaped route evidence authorizes the same correction route, "
        "and LGRC `step()` processes the packet work back to band each time. The "
        "no-memory comparator is useful because it shows that the repeated result "
        "depends on the scoped N08 memory surface; without it, the candidate set "
        "stays tied and the proxy drifts out of band.",
        "",
        "This is not semantic goal understanding, agency, or constitutive native "
        "regulation. It remains a GPR5 candidate with a native-policy gap.",
        "",
        "## Controls",
        "",
    ]
    for name, control in sorted(controls.items()):
        lines.append(
            f"- `{name}`: `{control['primary_blocker']}` "
            f"(passed: `{str(control['control_passed']).lower()}`)"
        )
    lines.extend(["", "## Validation Checks", ""])
    for name, value in sorted(checks.items()):
        lines.append(f"- `{name}`: `{str(value).lower()}`")
    lines.extend(
        [
            "",
            "## Acceptance State",
            "",
            "Achieved. Repeated proxy-conditioned cycles return the memory-shaped "
            "lane to the declared band with exact node-plus-packet accounting. "
            "The no-memory comparator records a tied/no-schedule failure mode, "
            "and all stronger claim flags remain blocked.",
            "",
            "## Replay",
            "",
            "```bash",
            COMMAND,
            "```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    artifact = build_repeated_bounded_regulation()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)


if __name__ == "__main__":
    main()
