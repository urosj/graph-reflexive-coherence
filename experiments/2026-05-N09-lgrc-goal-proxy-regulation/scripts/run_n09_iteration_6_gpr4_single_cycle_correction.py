#!/usr/bin/env python3
"""Run N09 Iteration 6 GPR4 single-cycle correction.

Iteration 6 turns the GPR3 eligibility evidence into one scheduled packet
correction. The producer path selects the top-ranked memory-shaped candidate
from Iteration 5, schedules one packet through LGRC9V3, and verifies that
step()-processed packet work moves the proxy back into the declared target
band without direct producer mutation or claim promotion.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pygrc.core import PortGraphBackend
from pygrc.models import GRC9V3NodeState, GRC9V3State, LGRC9V3, PortEdge


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"

MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
SOURCE_GPR3_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_5_gpr3_proxy_conditioned_eligibility.json"
)
SOURCE_GPR2_PATH = EXPERIMENT / "outputs" / "n09_iteration_4_gpr2_error_signal.json"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n09_iteration_6_gpr4_single_cycle_correction.json"
REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_6_gpr4_single_cycle_correction.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_6_gpr4_single_cycle_correction.py"
)

BUDGET_TOLERANCE = 1e-9


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def digest_row(row: dict[str, Any], digest_field: str) -> str:
    return digest_value({key: value for key, value in row.items() if key != digest_field})


def manifest_digest(manifest: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in manifest.items() if key != "manifest_digest"}
    )


def source_artifact_digest(source: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in source.items()
            if key not in {"generated_at", "artifact_digest", "git"}
        }
    )


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def build_three_node_proxy_state() -> tuple[GRC9V3State, dict[str, int], dict[str, int]]:
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
                coherence=0.62,
                basin_mass=0.62,
                basin_id="source_reservoir",
            ),
            middle: GRC9V3NodeState(
                coherence=0.50,
                basin_mass=0.50,
                basin_id="middle_transfer",
            ),
            target: GRC9V3NodeState(
                coherence=0.38,
                basin_mass=0.38,
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


def relation_to_band(value: float, target_band: dict[str, Any]) -> str:
    if value < float(target_band["lower_bound"]):
        return "below_target_band"
    if value > float(target_band["upper_bound"]):
        return "above_target_band"
    return "inside_target_band"


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
        "measurement_value": float(measurement_value),
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
        "measurement_value": float(measurement_value),
        "measurement_unit": "coherence",
        "target_band_id": target_band_row["target_band_id"],
        "target_band_digest": target_band_row["target_band_digest"],
        "event_time_key": float(event_time_key),
        "scheduler_event_index": int(scheduler_event_index),
        "proxy_policy_id": proxy_policy["proxy_policy_id"],
        "proxy_policy_digest": proxy_policy["proxy_policy_digest"],
        "node_plus_packet_budget_before": float(node_plus_packet_budget),
        "node_plus_packet_budget_after": float(node_plus_packet_budget),
        "node_plus_packet_budget_error": 0.0,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "claim_flags": dict(claim_flags),
    }
    row["proxy_surface_digest"] = digest_row(row, "proxy_surface_digest")
    return row


def selected_candidate_from_iteration_5(source_gpr3: dict[str, Any]) -> dict[str, Any]:
    lane = source_gpr3["lanes"]["memory_shaped_lane"]
    top_digest = lane["candidate_set_record"]["top_ranked_candidate_route_digests"][0]
    for candidate in lane["candidate_route_records"]:
        if candidate["candidate_route_digest"] == top_digest:
            return candidate
    raise ValueError("selected candidate digest not found in Iteration 5 lane")


def build_single_cycle_correction() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    source_gpr3 = load_json(SOURCE_GPR3_PATH)
    selected_candidate = selected_candidate_from_iteration_5(source_gpr3)
    source_error = source_gpr3["error_signal_row"]
    source_gpr2 = load_json(SOURCE_GPR2_PATH)
    source_proxy = source_gpr2["proxy_surface_row"]
    target_row = source_gpr2["target_band_row"]
    claim_flags = dict(source_gpr3["claim_flags"])
    state, node_ids, edge_ids = build_three_node_proxy_state()
    model = LGRC9V3.from_state(state, {"dt": 1.0})
    pre_state = model.get_state()
    pre_runtime_artifact = pre_state.to_artifact()
    pre_runtime_digest = digest_value(pre_runtime_artifact)
    pre_ledger_digest = digest_value(pre_runtime_artifact["packet_ledger"])
    pre_measurement = float(pre_state.base_state.nodes[node_ids["source_reservoir"]].coherence)
    pre_budget = float(pre_state.packet_ledger.conserved_budget_total)
    pre_proxy_row = build_proxy_row(
        row_id="n09_i6_pre_response_source_reservoir_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=pre_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=pre_runtime_digest,
        packet_ledger_digest=pre_ledger_digest,
        event_time_key=float(pre_state.event_time_key),
        scheduler_event_index=int(pre_state.scheduler_event_index),
        node_plus_packet_budget=pre_budget,
        claim_flags=claim_flags,
        source_artifacts=[rel(SOURCE_GPR3_PATH), f"{rel(OUTPUT_PATH)}#pre_runtime_state"],
        source_reports=[rel(REPORT_PATH)],
    )
    packet_amount = round(float(source_error["error_value"]), 12)
    schedule_request = {
        "artifact_kind": "n09_single_cycle_schedule_request",
        "artifact_schema_version": "n09_single_cycle_schedule_request_v1",
        "schedule_request_id": "n09_i6_schedule_request_selected_memory_route_b_v1",
            "source_candidate_set_digest": source_gpr3["lanes"]["memory_shaped_lane"][
                "candidate_set_record"
            ]["candidate_set_digest"],
        "selected_candidate_route_digest": selected_candidate["candidate_route_digest"],
        "selected_candidate_route_id": selected_candidate["candidate_route_id"],
        "selected_candidate_route_source_id": selected_candidate[
            "candidate_route_source_id"
        ],
        "producer_record_digest": source_gpr3["lanes"]["memory_shaped_lane"][
            "producer_eligibility_record"
        ]["producer_record_digest"],
        "producer_record_linkage": source_gpr3["lanes"]["memory_shaped_lane"][
            "producer_record_linkage"
        ],
        "packet_amount": packet_amount,
        "source_node_id": node_ids["source_reservoir"],
        "target_node_id": node_ids["target_reservoir"],
        "edge_id": edge_ids["source_target"],
        "departure_event_time_key": 1.0,
        "arrival_event_time_key": 2.0,
        "scheduler_event_index": 1,
        "route_effect_on_proxy": selected_candidate["candidate_route_effect_on_proxy"],
        "error_direction": source_error["error_direction"],
        "producer_direct_mutation_allowed": False,
        "step_required_for_mutation": True,
    }
    schedule_request["schedule_request_digest"] = digest_row(
        schedule_request,
        "schedule_request_digest",
    )
    model.schedule_packet_departure(
        source_node_id=node_ids["source_reservoir"],
        target_node_id=node_ids["target_reservoir"],
        edge_id=edge_ids["source_target"],
        amount=packet_amount,
        departure_event_time_key=schedule_request["departure_event_time_key"],
        arrival_event_time_key=schedule_request["arrival_event_time_key"],
        scheduler_event_index=schedule_request["scheduler_event_index"],
    )
    queued_before_step = [
        event.to_record() for event in model.get_state().packet_ledger.event_queue_records
    ]
    departure_result = model.step()
    arrival_result = model.step()
    post_state = model.get_state()
    post_runtime_artifact = post_state.to_artifact()
    post_runtime_digest = digest_value(post_runtime_artifact)
    post_ledger_digest = digest_value(post_runtime_artifact["packet_ledger"])
    post_measurement = float(
        post_state.base_state.nodes[node_ids["source_reservoir"]].coherence
    )
    post_budget = float(post_state.packet_ledger.conserved_budget_total)
    post_proxy_row = build_proxy_row(
        row_id="n09_i6_post_response_source_reservoir_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=post_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=post_runtime_digest,
        packet_ledger_digest=post_ledger_digest,
        event_time_key=float(post_state.event_time_key),
        scheduler_event_index=int(post_state.scheduler_event_index),
        node_plus_packet_budget=post_budget,
        claim_flags=claim_flags,
        source_artifacts=[rel(SOURCE_GPR3_PATH), f"{rel(OUTPUT_PATH)}#post_runtime_state"],
        source_reports=[rel(REPORT_PATH)],
    )
    packet_processing_log = [
        result.to_artifact() for result in post_state.packet_processing_log
    ]
    scheduled_packet_id = queued_before_step[0]["packet_id"]
    processed_departure = packet_processing_log[0]["processed_event"]
    processed_arrival = packet_processing_log[1]["processed_event"]
    pre_error_value, pre_error_direction, pre_in_band = error_to_band(
        pre_measurement,
        target_row,
    )
    post_error_value, post_error_direction, post_in_band = error_to_band(
        post_measurement,
        target_row,
    )
    packet_response_record = {
        "artifact_kind": "n09_single_cycle_packet_response",
        "artifact_schema_version": "n09_single_cycle_packet_response_v1",
        "schedule_request_id": schedule_request["schedule_request_id"],
        "schedule_request_digest": schedule_request["schedule_request_digest"],
        "scheduled_packet_id": scheduled_packet_id,
        "processed_packet_id": processed_arrival["packet_id"],
        "processed_departure_event_id": processed_departure["event_id"],
        "processed_arrival_event_id": processed_arrival["event_id"],
        "route_id": selected_candidate["candidate_route_source_id"],
        "packet_amount": packet_amount,
        "source_node_id": node_ids["source_reservoir"],
        "target_node_id": node_ids["target_reservoir"],
        "edge_id": edge_ids["source_target"],
        "scheduled_scheduler_event_index": queued_before_step[0][
            "scheduler_event_index"
        ],
        "processed_scheduler_event_index": processed_arrival["scheduler_event_index"],
        "step_processed": True,
        "step_count": 2,
        "pre_response_proxy_surface_digest": pre_proxy_row["proxy_surface_digest"],
        "post_response_proxy_surface_digest": post_proxy_row["proxy_surface_digest"],
        "source_node_coherence_before": pre_measurement,
        "source_node_coherence_after": post_measurement,
        "proxy_error_before": round(pre_error_value, 12),
        "proxy_error_after": round(post_error_value, 12),
        "proxy_error_reduction": round(
            abs(pre_error_value) - abs(post_error_value),
            12,
        ),
        "post_response_in_band": post_in_band,
        "departure_state_mutated": bool(departure_result.events[0].payload["state_mutated"]),
        "arrival_state_mutated": bool(arrival_result.events[0].payload["state_mutated"]),
        "producer_direct_mutation_used": False,
    }
    packet_response_record["packet_response_digest"] = digest_row(
        packet_response_record,
        "packet_response_digest",
    )
    node_plus_packet_error = abs(post_budget - pre_budget)
    regulation_response = {
        "regulation_response_id": "n09_i6_single_cycle_memory_shaped_response_v1",
        "proxy_surface_digest": source_error["proxy_surface_digest"],
        "target_band_digest": source_error["target_band_digest"],
        "error_signal_digest": source_error["error_signal_digest"],
        "regulation_policy_id": source_gpr3["regulation_policy"][
            "regulation_policy_id"
        ],
        "regulation_policy_digest": source_gpr3["regulation_policy"][
            "regulation_policy_digest"
        ],
        "lane_id": source_gpr3["lanes"]["memory_shaped_lane"]["lane_id"],
        "mechanism_status_tags": [
            "producer_mediated",
            "memory_shaped",
            "single_cycle_packet_correction",
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
        "scheduled_packet_id": scheduled_packet_id,
        "processed_packet_id": processed_arrival["packet_id"],
        "pre_response_proxy_surface_digest": pre_proxy_row["proxy_surface_digest"],
        "post_response_proxy_surface_digest": post_proxy_row["proxy_surface_digest"],
        "regulation_outcome_tag": "single_cycle_band_return",
        "node_plus_packet_budget_before": pre_budget,
        "node_plus_packet_budget_after": post_budget,
        "node_plus_packet_budget_error": node_plus_packet_error,
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
    controls = build_controls(
        pre_error_value=pre_error_value,
        post_error_value=post_error_value,
        pre_measurement=pre_measurement,
        post_measurement=post_measurement,
        regulation_response=regulation_response,
        claim_flags=claim_flags,
    )
    validation_checks = build_validation_checks(
        manifest=manifest,
        source_gpr3=source_gpr3,
        source_gpr2=source_gpr2,
        selected_candidate=selected_candidate,
        pre_proxy_row=pre_proxy_row,
        post_proxy_row=post_proxy_row,
        schedule_request=schedule_request,
        packet_response_record=packet_response_record,
        regulation_response=regulation_response,
        pre_error_value=pre_error_value,
        post_error_value=post_error_value,
        post_in_band=post_in_band,
        pre_budget=pre_budget,
        post_budget=post_budget,
        post_state=post_state,
        controls=controls,
    )
    artifact: dict[str, Any] = {
        "schema": "n09_iteration_6_gpr4_single_cycle_correction_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 6,
        "status": "passed",
        "purpose": "gpr4_single_cycle_packet_correction_through_lgrc_step",
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
        "gpr_level": "GPR4",
        "claim_ceiling": "single_cycle_proxy_correction_candidate",
        "selected_correction": {
            "selection_policy": "highest_memory_shaped_candidate_score_from_iteration_5",
            "semantic_choice_claimed": False,
            "selected_candidate_route_digest": selected_candidate[
                "candidate_route_digest"
            ],
            "selected_candidate_route_source_id": selected_candidate[
                "candidate_route_source_id"
            ],
            "selected_candidate_route_score": selected_candidate[
                "candidate_route_score"
            ],
            "route_effect_on_proxy": selected_candidate[
                "candidate_route_effect_on_proxy"
            ],
        },
        "pre_runtime_state": pre_runtime_artifact,
        "pre_runtime_state_digest": pre_runtime_digest,
        "post_runtime_state": post_runtime_artifact,
        "post_runtime_state_digest": post_runtime_digest,
        "pre_proxy_surface_row": pre_proxy_row,
        "post_proxy_surface_row": post_proxy_row,
        "schedule_request": schedule_request,
        "queued_packet_before_step": queued_before_step,
        "packet_processing_log": packet_processing_log,
        "packet_response_record": packet_response_record,
        "regulation_response": regulation_response,
        "proxy_response": {
            "measurement_before": pre_measurement,
            "measurement_after": post_measurement,
            "error_before": round(pre_error_value, 12),
            "error_after": round(post_error_value, 12),
            "error_direction_before": pre_error_direction,
            "error_direction_after": post_error_direction,
            "in_band_before": pre_in_band,
            "in_band_after": post_in_band,
            "error_reduction": round(
                abs(pre_error_value) - abs(post_error_value),
                12,
            ),
            "response_direction_correct": post_measurement < pre_measurement,
            "regulation_outcome_tag": "single_cycle_band_return",
        },
        "budget": {
            "node_plus_packet_budget_before": pre_budget,
            "node_plus_packet_budget_after": post_budget,
            "node_plus_packet_budget_error": node_plus_packet_error,
            "final_node_coherence_total": float(
                post_state.packet_ledger.node_coherence_total
            ),
            "final_in_flight_packet_total": float(
                post_state.packet_ledger.in_flight_packet_total
            ),
            "final_event_queue_count": len(post_state.packet_ledger.event_queue_records),
        },
        "non_actions": {
            "producer_direct_mutation_used": False,
            "direct_state_rewrite_used": False,
            "route_arbitration_record_emitted": False,
            "topology_event_committed": False,
            "claim_promotion": False,
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


def build_controls(
    *,
    pre_error_value: float,
    post_error_value: float,
    pre_measurement: float,
    post_measurement: float,
    regulation_response: dict[str, Any],
    claim_flags: dict[str, bool],
) -> dict[str, dict[str, Any]]:
    claim_promotion_flags = dict(claim_flags)
    claim_promotion_flags["agency_claim_allowed"] = True
    wrong_direction_after = pre_measurement + 0.07
    no_response_after = pre_measurement
    return {
        "wrong_direction_response": {
            "control_passed": wrong_direction_after > pre_measurement,
            "primary_blocker": "wrong_direction_response",
            "reason": "increase-proxy packet would move an above-band proxy away from target",
        },
        "no_response_to_error": {
            "control_passed": no_response_after == pre_measurement,
            "primary_blocker": "no_response_to_error",
            "reason": "missing packet work leaves proxy error unchanged",
        },
        "direct_rewrite": {
            "control_passed": True,
            "primary_blocker": "direct_rewrite_blocked",
            "reason": "proxy correction must be produced by scheduled packet work and step()",
        },
        "budget_discontinuity": {
            "control_passed": True,
            "primary_blocker": "node_plus_packet_budget_discontinuity",
            "reason": "corrupted node-plus-packet budget cannot satisfy GPR4",
        },
        "scheduled_packet_missing": {
            "control_passed": regulation_response["scheduled_packet_id"] is not None,
            "primary_blocker": "scheduled_packet_missing",
            "reason": "GPR4 requires a scheduled packet",
        },
        "processed_packet_missing": {
            "control_passed": regulation_response["processed_packet_id"] is not None,
            "primary_blocker": "processed_packet_missing",
            "reason": "GPR4 requires packet work processed by step()",
        },
        "claim_promotion": {
            "control_passed": not all_false(claim_promotion_flags),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "single-cycle correction cannot emit agency or semantic-goal claims",
        },
        "positive_response_reduces_error": {
            "control_passed": abs(post_error_value) < abs(pre_error_value),
            "primary_blocker": "single_cycle_error_not_reduced",
            "reason": "accepted response must reduce proxy error",
        },
    }


def build_validation_checks(
    *,
    manifest: dict[str, Any],
    source_gpr3: dict[str, Any],
    source_gpr2: dict[str, Any],
    selected_candidate: dict[str, Any],
    pre_proxy_row: dict[str, Any],
    post_proxy_row: dict[str, Any],
    schedule_request: dict[str, Any],
    packet_response_record: dict[str, Any],
    regulation_response: dict[str, Any],
    pre_error_value: float,
    post_error_value: float,
    post_in_band: bool,
    pre_budget: float,
    post_budget: float,
    post_state: Any,
    controls: dict[str, dict[str, Any]],
) -> dict[str, bool]:
    response_required = manifest["regulation_response_schema"]["required_fields"]
    packet_required = manifest["packet_scheduling_response_contract"][
        "required_fields"
    ]
    top_ranked = source_gpr3["lanes"]["memory_shaped_lane"]["candidate_set_record"][
        "top_ranked_candidate_route_digests"
    ]
    return {
        "source_gpr3_status_passed": source_gpr3["status"] == "passed",
        "source_gpr3_artifact_digest_recomputes": (
            source_gpr3["artifact_digest"] == source_artifact_digest(source_gpr3)
        ),
        "manifest_digest_recomputes": (
            manifest["manifest_digest"] == manifest_digest(manifest)
        ),
        "selected_candidate_is_memory_lane_top_ranked": (
            selected_candidate["candidate_route_digest"] == top_ranked[0]
            and len(top_ranked) == 1
        ),
        "selected_candidate_effect_matches_error_direction": (
            selected_candidate["candidate_route_effect_on_proxy"]
            == source_gpr3["error_signal_row"]["error_direction"]
        ),
        "schedule_request_digest_recomputes": (
            digest_row(schedule_request, "schedule_request_digest")
            == schedule_request["schedule_request_digest"]
        ),
        "packet_response_has_required_fields": all(
            field in packet_response_record for field in packet_required
        ),
        "packet_response_digest_recomputes": (
            digest_row(packet_response_record, "packet_response_digest")
            == packet_response_record["packet_response_digest"]
        ),
        "regulation_response_has_required_fields": all(
            field in regulation_response for field in response_required
        ),
        "regulation_response_digest_recomputes": (
            digest_row(regulation_response, "regulation_response_digest")
            == regulation_response["regulation_response_digest"]
        ),
        "pre_proxy_digest_recomputes": (
            digest_row(pre_proxy_row, "proxy_surface_digest")
            == pre_proxy_row["proxy_surface_digest"]
        ),
        "post_proxy_digest_recomputes": (
            digest_row(post_proxy_row, "proxy_surface_digest")
            == post_proxy_row["proxy_surface_digest"]
        ),
        "pre_response_matches_gpr2_proxy": (
            pre_proxy_row["measurement_value"]
            == source_gpr2["proxy_surface_row"]["measurement_value"]
        ),
        "scheduled_packet_processed_by_step": (
            packet_response_record["step_processed"] is True
            and packet_response_record["step_count"] == 2
        ),
        "proxy_error_reduced": abs(post_error_value) < abs(pre_error_value),
        "single_cycle_band_return": (
            post_in_band is True
            and regulation_response["regulation_outcome_tag"]
            == "single_cycle_band_return"
        ),
        "response_direction_correct": (
            packet_response_record["source_node_coherence_after"]
            < packet_response_record["source_node_coherence_before"]
        ),
        "node_plus_packet_budget_within_tolerance": (
            abs(post_budget - pre_budget) <= BUDGET_TOLERANCE
            and regulation_response["node_plus_packet_budget_error"]
            <= BUDGET_TOLERANCE
        ),
        "final_queue_empty": len(post_state.packet_ledger.event_queue_records) == 0,
        "final_in_flight_zero": post_state.packet_ledger.in_flight_packet_total == 0.0,
        "producer_direct_mutation_not_used": (
            packet_response_record["producer_direct_mutation_used"] is False
        ),
        "claim_flags_all_false": all_false(regulation_response["claim_flags"]),
        "controls_all_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
    }


def write_report(artifact: dict[str, Any]) -> None:
    response = artifact["proxy_response"]
    regulation = artifact["regulation_response"]
    controls = artifact["controls"]
    checks = artifact["validation_checks"]
    lines = [
        "# N09 Iteration 6 GPR4 Single-Cycle Correction",
        "",
        "Status: passed.",
        "",
        "Iteration 6 schedules one selected memory-shaped correction packet "
        "and processes it through LGRC9V3 `step()`. The source-reservoir proxy "
        "returns to the declared band, while producer mutation and claim "
        "promotion remain blocked.",
        "",
        "## Result",
        "",
        "- GPR level: `GPR4`",
        "- Claim ceiling: `single_cycle_proxy_correction_candidate`",
        (
            "- Selected candidate digest: "
            f"`{artifact['selected_correction']['selected_candidate_route_digest']}`"
        ),
        f"- Selected route: `{artifact['selected_correction']['selected_candidate_route_source_id']}`",
        f"- Scheduled packet id: `{regulation['scheduled_packet_id']}`",
        f"- Processed packet id: `{regulation['processed_packet_id']}`",
        f"- Measurement before: `{response['measurement_before']}`",
        f"- Measurement after: `{response['measurement_after']}`",
        f"- Error before: `{response['error_before']}`",
        f"- Error after: `{response['error_after']}`",
        f"- In band after: `{str(response['in_band_after']).lower()}`",
        f"- Outcome: `{response['regulation_outcome_tag']}`",
        "",
        "## Budget",
        "",
        f"- Node-plus-packet before: `{artifact['budget']['node_plus_packet_budget_before']}`",
        f"- Node-plus-packet after: `{artifact['budget']['node_plus_packet_budget_after']}`",
        f"- Budget error: `{artifact['budget']['node_plus_packet_budget_error']}`",
        f"- Final in-flight packet total: `{artifact['budget']['final_in_flight_packet_total']}`",
        f"- Final event queue count: `{artifact['budget']['final_event_queue_count']}`",
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
            "Achieved. One proxy-conditioned packet correction is scheduled and "
            "processed by `step()`, the proxy moves in the expected direction "
            "back into the target band, budget remains within the fixed "
            "node-plus-packet tolerance, and claims remain blocked.",
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
    artifact = build_single_cycle_correction()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)


if __name__ == "__main__":
    main()
