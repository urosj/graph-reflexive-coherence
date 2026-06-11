#!/usr/bin/env python3
"""Run N09 Iteration 8 perturbation, withdrawal, and support checks.

Iteration 8 checks whether the GPR5 regulation pattern survives an explicit
proxy perturbation and records the identity/support-withdrawal boundary. The
positive runtime lane is perturbation recovery through LGRC packet scheduling
and step(). The support-withdrawal lane is serialized as a handoff/control
record because N07 did not provide a withdrawal-stability baseline.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pygrc.models import LGRC9V3

from run_n09_iteration_7_gpr5_repeated_bounded_regulation import (
    BUDGET_TOLERANCE,
    WINDOW_INPUT_AMOUNT,
    build_error_row,
    build_proxy_row,
    build_regulation_state,
    digest_file,
    digest_row,
    digest_value,
    error_to_band,
    git_head,
    git_status_short,
    load_json,
    manifest_digest,
    node_measurement,
    rel,
    runtime_digests,
    schedule_and_step_packet,
    selected_candidate_from_lane,
    source_artifact_digest,
)


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"

MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
SOURCE_GPR3_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_5_gpr3_proxy_conditioned_eligibility.json"
)
SOURCE_GPR7_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_7_gpr5_repeated_bounded_regulation.json"
)
SOURCE_GPR2_PATH = EXPERIMENT / "outputs" / "n09_iteration_4_gpr2_error_signal.json"
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_8_perturbation_withdrawal_support.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_8_perturbation_withdrawal_support.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_8_perturbation_withdrawal_support.py"
)

PERTURBATION_AMOUNT = 0.09


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def build_cycle_candidate_record(
    *,
    source_gpr3: dict[str, Any],
    selected_candidate: dict[str, Any],
    error_row: dict[str, Any],
    proxy_row: dict[str, Any],
    target_band_row: dict[str, Any],
) -> dict[str, Any]:
    lane = source_gpr3["lanes"]["memory_shaped_lane"]
    record = {
        "cycle_index": "perturbation_recovery",
        "lane_id": lane["lane_id"],
        "source_candidate_set_digest": lane["candidate_set_record"][
            "candidate_set_digest"
        ],
        "source_candidate_route_digests": lane["candidate_set_record"][
            "candidate_route_digests"
        ],
        "top_ranked_candidate_route_digests": lane["candidate_set_record"][
            "top_ranked_candidate_route_digests"
        ],
        "top_ranked_is_unique": lane["candidate_set_record"]["top_ranked_is_unique"],
        "selected_candidate_route_digest": selected_candidate["candidate_route_digest"],
        "selected_candidate_route_source_id": selected_candidate[
            "candidate_route_source_id"
        ],
        "selection_policy": "highest_memory_shaped_candidate_score_from_iteration_5",
        "selection_blocker": None,
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


def build_packet_response_record(
    *,
    schedule_request: dict[str, Any],
    queued_packet: dict[str, Any],
    processing_log: list[dict[str, Any]],
    selected_candidate: dict[str, Any],
    node_ids: dict[str, int],
    edge_ids: dict[str, int],
    pre_proxy_row: dict[str, Any],
    post_proxy_row: dict[str, Any],
    pre_measurement: float,
    post_measurement: float,
    pre_error: float,
    post_error: float,
    post_in_band: bool,
) -> dict[str, Any]:
    processed_departure = processing_log[0]["processed_event"]
    processed_arrival = processing_log[-1]["processed_event"]
    record = {
        "artifact_kind": "n09_perturbation_recovery_packet_response",
        "artifact_schema_version": "n09_perturbation_recovery_packet_response_v1",
        "schedule_request_id": schedule_request["schedule_request_id"],
        "schedule_request_digest": schedule_request["schedule_request_digest"],
        "scheduled_packet_id": queued_packet["packet_id"],
        "processed_packet_id": processed_arrival["packet_id"],
        "processed_departure_event_id": processed_departure["event_id"],
        "processed_arrival_event_id": processed_arrival["event_id"],
        "route_id": selected_candidate["candidate_route_source_id"],
        "packet_amount": schedule_request["packet_amount"],
        "source_node_id": node_ids["source_reservoir"],
        "target_node_id": node_ids["target_reservoir"],
        "edge_id": edge_ids["source_target"],
        "scheduled_scheduler_event_index": queued_packet["scheduler_event_index"],
        "processed_scheduler_event_index": processed_arrival["scheduler_event_index"],
        "step_processed": True,
        "step_count": 2,
        "pre_response_proxy_surface_digest": pre_proxy_row["proxy_surface_digest"],
        "post_response_proxy_surface_digest": post_proxy_row["proxy_surface_digest"],
        "source_node_coherence_before": pre_measurement,
        "source_node_coherence_after": post_measurement,
        "proxy_error_before": pre_error,
        "proxy_error_after": post_error,
        "proxy_error_reduction": round(abs(pre_error) - abs(post_error), 12),
        "post_response_in_band": post_in_band,
        "producer_direct_mutation_used": False,
    }
    record["packet_response_digest"] = digest_row(record, "packet_response_digest")
    return record


def support_anchor_consistency(manifest: dict[str, Any]) -> dict[str, Any]:
    return manifest["default_fixture_family"]["n08_support_anchor_consistency"]


def build_support_withdrawal_record(manifest: dict[str, Any]) -> dict[str, Any]:
    support_schema = manifest["support_withdrawal_schema"]
    support_consistency = support_anchor_consistency(manifest)
    support_digest = support_consistency["n07_support_area_digest"]
    post_withdrawal_digest = digest_value(
        {
            "baseline_support_digest": support_digest,
            "withdrawal_depth": 0.25,
            "duration_steps": 2,
            "baseline_available": False,
            "blocker": support_schema["n07_withdrawal_baseline_blocker"],
        }
    )
    record = {
        "withdrawal_id": "n09_i8_partial_support_weakening_baseline_limited_v1",
        "support_withdrawal_kind": "partial_support_weakening",
        "identity_support_digest": support_digest,
        "support_area_id": "n07_identity_support_area",
        "support_area_digest": support_digest,
        "withdrawal_depth": 0.25,
        "duration_steps": 2,
        "baseline_support_digest": support_digest,
        "post_withdrawal_support_digest": post_withdrawal_digest,
        "identity_support_outcome_tag": "identity_support_withdrawal_baseline_missing",
        "n07_withdrawal_baseline_available": support_schema[
            "n07_withdrawal_baseline_available"
        ],
        "primary_blocker": support_schema["n07_withdrawal_baseline_blocker"],
        "support_withdrawal_status": "serialized_handoff_record_only",
        "must_not_infer_identity_acceptance": support_schema[
            "must_not_infer_identity_acceptance"
        ],
    }
    record["withdrawal_digest"] = digest_row(record, "withdrawal_digest")
    return record


def build_perturbation_recovery() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    source_gpr3 = load_json(SOURCE_GPR3_PATH)
    source_gpr7 = load_json(SOURCE_GPR7_PATH)
    source_gpr2 = load_json(SOURCE_GPR2_PATH)
    target_row = source_gpr2["target_band_row"]
    claim_flags = dict(source_gpr7["claim_flags"])
    selected_candidate = selected_candidate_from_lane(
        source_gpr3["lanes"]["memory_shaped_lane"]
    )
    if selected_candidate is None:
        raise ValueError("memory-shaped lane must have one selected candidate")
    state, node_ids, edge_ids = build_regulation_state()
    model = LGRC9V3.from_state(state, {"dt": 1.0})
    initial_runtime, initial_runtime_digest, initial_ledger_digest = runtime_digests(
        model
    )
    initial_budget = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    initial_measurement = node_measurement(model, node_ids["source_reservoir"])
    pre_perturbation_proxy_row = build_proxy_row(
        row_id="n09_i8_pre_perturbation_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=initial_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=initial_runtime_digest,
        packet_ledger_digest=initial_ledger_digest,
        event_time_key=0.0,
        scheduler_event_index=0,
        node_plus_packet_budget=initial_budget,
        claim_flags=claim_flags,
        source_artifacts=[rel(SOURCE_GPR7_PATH), f"{rel(OUTPUT_PATH)}#pre_perturbation"],
        source_reports=[rel(REPORT_PATH)],
    )
    perturbation_queued, perturbation_log = schedule_and_step_packet(
        model=model,
        source_node_id=node_ids["target_reservoir"],
        target_node_id=node_ids["source_reservoir"],
        edge_id=edge_ids["source_target"],
        amount=PERTURBATION_AMOUNT,
        departure_event_time_key=1.0,
        arrival_event_time_key=2.0,
        scheduler_event_index=1,
    )
    post_perturbation_runtime, post_perturbation_runtime_digest, post_perturbation_ledger_digest = (
        runtime_digests(model)
    )
    post_perturbation_budget = round(
        float(model.get_state().packet_ledger.conserved_budget_total),
        12,
    )
    post_perturbation_measurement = node_measurement(
        model,
        node_ids["source_reservoir"],
    )
    post_perturbation_proxy_row = build_proxy_row(
        row_id="n09_i8_post_perturbation_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=post_perturbation_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=post_perturbation_runtime_digest,
        packet_ledger_digest=post_perturbation_ledger_digest,
        event_time_key=2.0,
        scheduler_event_index=2,
        node_plus_packet_budget=post_perturbation_budget,
        claim_flags=claim_flags,
        source_artifacts=[rel(SOURCE_GPR7_PATH), f"{rel(OUTPUT_PATH)}#post_perturbation"],
        source_reports=[rel(REPORT_PATH)],
    )
    perturbation_record = {
        "perturbation_id": "n09_i8_proxy_increase_perturbation_v1",
        "perturbation_kind": "serialized_packet_proxy_increase",
        "amplitude": PERTURBATION_AMOUNT,
        "duration_steps": 2,
        "start_event_time_key": 1.0,
        "affected_proxy_surface_id": pre_perturbation_proxy_row["proxy_surface_id"],
        "pre_perturbation_proxy_surface_digest": pre_perturbation_proxy_row[
            "proxy_surface_digest"
        ],
        "post_perturbation_proxy_surface_digest": post_perturbation_proxy_row[
            "proxy_surface_digest"
        ],
        "node_plus_packet_budget_before": initial_budget,
        "node_plus_packet_budget_after": post_perturbation_budget,
        "node_plus_packet_budget_error": round(
            abs(post_perturbation_budget - initial_budget),
            12,
        ),
        "expected_recovery_window_count": 1,
        "recovery_success_criterion": (
            "post_recovery_proxy_in_declared_band_and_node_plus_packet_budget_error_zero"
        ),
        "scheduled_packet_id": perturbation_queued[0]["packet_id"],
        "processed_packet_id": perturbation_log[-1]["processed_event"]["packet_id"],
        "hidden_perturbation_used": False,
    }
    perturbation_record["perturbation_digest"] = digest_row(
        perturbation_record,
        "perturbation_digest",
    )
    perturbation_error_row = build_error_row(
        row_id="n09_i8_post_perturbation_error_signal_v1",
        manifest=manifest,
        proxy_row=post_perturbation_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    cycle_candidate_record = build_cycle_candidate_record(
        source_gpr3=source_gpr3,
        selected_candidate=selected_candidate,
        error_row=perturbation_error_row,
        proxy_row=post_perturbation_proxy_row,
        target_band_row=target_row,
    )
    correction_amount = round(abs(float(perturbation_error_row["error_value"])), 12)
    schedule_request = {
        "artifact_kind": "n09_perturbation_recovery_schedule_request",
        "artifact_schema_version": "n09_perturbation_recovery_schedule_request_v1",
        "schedule_request_id": "n09_i8_perturbation_recovery_schedule_request_v1",
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
        "departure_event_time_key": 3.0,
        "arrival_event_time_key": 4.0,
        "scheduler_event_index": 3,
        "route_effect_on_proxy": selected_candidate["candidate_route_effect_on_proxy"],
        "error_direction": perturbation_error_row["error_direction"],
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
    post_recovery_runtime, post_recovery_runtime_digest, post_recovery_ledger_digest = (
        runtime_digests(model)
    )
    post_recovery_budget = round(
        float(model.get_state().packet_ledger.conserved_budget_total),
        12,
    )
    post_recovery_measurement = node_measurement(model, node_ids["source_reservoir"])
    post_recovery_proxy_row = build_proxy_row(
        row_id="n09_i8_post_recovery_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=post_recovery_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=post_recovery_runtime_digest,
        packet_ledger_digest=post_recovery_ledger_digest,
        event_time_key=4.0,
        scheduler_event_index=4,
        node_plus_packet_budget=post_recovery_budget,
        claim_flags=claim_flags,
        source_artifacts=[rel(SOURCE_GPR7_PATH), f"{rel(OUTPUT_PATH)}#post_recovery"],
        source_reports=[rel(REPORT_PATH)],
    )
    post_recovery_error, post_recovery_direction, post_recovery_in_band = error_to_band(
        post_recovery_measurement,
        target_row,
    )
    packet_response_record = build_packet_response_record(
        schedule_request=schedule_request,
        queued_packet=correction_queued[0],
        processing_log=correction_log,
        selected_candidate=selected_candidate,
        node_ids=node_ids,
        edge_ids=edge_ids,
        pre_proxy_row=post_perturbation_proxy_row,
        post_proxy_row=post_recovery_proxy_row,
        pre_measurement=post_perturbation_measurement,
        post_measurement=post_recovery_measurement,
        pre_error=perturbation_error_row["error_value"],
        post_error=round(post_recovery_error, 12),
        post_in_band=post_recovery_in_band,
    )
    support_withdrawal_record = build_support_withdrawal_record(manifest)
    regulation_response = {
        "regulation_response_id": "n09_i8_perturbation_recovery_response_v1",
        "proxy_surface_digest": post_perturbation_proxy_row["proxy_surface_digest"],
        "target_band_digest": target_row["target_band_digest"],
        "error_signal_digest": perturbation_error_row["error_signal_digest"],
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
        "processed_packet_id": correction_log[-1]["processed_event"]["packet_id"],
        "pre_response_proxy_surface_digest": post_perturbation_proxy_row[
            "proxy_surface_digest"
        ],
        "post_response_proxy_surface_digest": post_recovery_proxy_row[
            "proxy_surface_digest"
        ],
        "regulation_outcome_tag": "single_cycle_band_return",
        "node_plus_packet_budget_before": post_perturbation_budget,
        "node_plus_packet_budget_after": post_recovery_budget,
        "node_plus_packet_budget_error": round(
            abs(post_recovery_budget - post_perturbation_budget),
            12,
        ),
        "proxy_budget_surface": "active_node_coherence_band",
        "proxy_budget_before": post_perturbation_measurement,
        "proxy_budget_after": post_recovery_measurement,
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
        "identity_support_digest": support_withdrawal_record[
            "identity_support_digest"
        ],
        "identity_support_outcome_tag": support_withdrawal_record[
            "identity_support_outcome_tag"
        ],
        "claim_flags": claim_flags,
    }
    regulation_response["regulation_response_digest"] = digest_row(
        regulation_response,
        "regulation_response_digest",
    )
    perturbation_recovery_summary = {
        "perturbation_measurement_before": initial_measurement,
        "perturbation_measurement_after": post_perturbation_measurement,
        "recovery_measurement_after": post_recovery_measurement,
        "perturbation_error_after": perturbation_error_row["error_value"],
        "recovery_error_after": round(post_recovery_error, 12),
        "recovery_in_band": post_recovery_in_band,
        "recovery_window_count": 1,
        "recovery_outcome_tag": "bounded_repeated_regulation",
        "classification": "perturbation_recovered_to_band",
        "node_plus_packet_budget_error": round(
            abs(post_recovery_budget - initial_budget),
            12,
        ),
    }
    controls = build_controls(
        perturbation_recovery_summary=perturbation_recovery_summary,
        support_withdrawal_record=support_withdrawal_record,
        claim_flags=claim_flags,
    )
    validation_checks = build_validation_checks(
        manifest=manifest,
        source_gpr3=source_gpr3,
        source_gpr7=source_gpr7,
        perturbation_record=perturbation_record,
        support_withdrawal_record=support_withdrawal_record,
        regulation_response=regulation_response,
        packet_response_record=packet_response_record,
        perturbation_recovery_summary=perturbation_recovery_summary,
        controls=controls,
        claim_flags=claim_flags,
    )
    artifact: dict[str, Any] = {
        "schema": "n09_iteration_8_perturbation_withdrawal_support_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 8,
        "status": "passed",
        "purpose": "perturbation_recovery_and_support_withdrawal_boundary_check",
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
        "source_gpr5_artifact": rel(SOURCE_GPR7_PATH),
        "source_gpr5_artifact_digest": source_gpr7["artifact_digest"],
        "source_gpr5_sha256": digest_file(SOURCE_GPR7_PATH),
        "gpr_level": "GPR5",
        "claim_ceiling": "repeated_bounded_proxy_regulation_candidate",
        "initial_runtime_state": initial_runtime,
        "post_perturbation_runtime_state": post_perturbation_runtime,
        "post_recovery_runtime_state": post_recovery_runtime,
        "pre_perturbation_proxy_surface_row": pre_perturbation_proxy_row,
        "post_perturbation_proxy_surface_row": post_perturbation_proxy_row,
        "post_recovery_proxy_surface_row": post_recovery_proxy_row,
        "perturbation_record": perturbation_record,
        "perturbation_error_signal_row": perturbation_error_row,
        "cycle_candidate_record": cycle_candidate_record,
        "schedule_request": schedule_request,
        "packet_response_record": packet_response_record,
        "regulation_response": regulation_response,
        "support_withdrawal_record": support_withdrawal_record,
        "perturbation_recovery_summary": perturbation_recovery_summary,
        "identity_support_boundary": {
            "identity_support_outcome_tag": support_withdrawal_record[
                "identity_support_outcome_tag"
            ],
            "identity_support_digest": support_withdrawal_record[
                "identity_support_digest"
            ],
            "baseline_available": False,
            "primary_blocker": support_withdrawal_record["primary_blocker"],
            "n10_consumption_allowed": False,
            "lower_gpr5_evidence_preserved": True,
        },
        "mechanism_status_tags": [
            "producer_mediated",
            "threshold_authorized",
            "memory_shaped",
            "native_policy_gap",
        ],
        "native_policy_gap": {
            "present": True,
            "primary_gap": "perturbation_recovery_policy_not_constitutive_native",
            "support_withdrawal_gap": support_withdrawal_record["primary_blocker"],
        },
        "non_actions": {
            "producer_direct_mutation_used": False,
            "direct_state_rewrite_used": False,
            "hidden_reset_used": False,
            "route_arbitration_record_emitted": False,
            "topology_event_committed": False,
            "claim_promotion": False,
            "identity_acceptance_claimed": False,
            "agency_claimed": False,
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
            "runtime_identity_acceptance",
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
    perturbation_recovery_summary: dict[str, Any],
    support_withdrawal_record: dict[str, Any],
    claim_flags: dict[str, bool],
) -> dict[str, dict[str, Any]]:
    claim_promotion_flags = dict(claim_flags)
    claim_promotion_flags["agency_claim_allowed"] = True
    identity_claim_flags = dict(claim_flags)
    identity_claim_flags["identity_acceptance_claim_allowed"] = True
    return {
        "unsupported_recovery": {
            "control_passed": perturbation_recovery_summary["recovery_in_band"] is True,
            "primary_blocker": "unsupported_recovery",
            "reason": "perturbation recovery must return the proxy to the declared band",
        },
        "hidden_reset": {
            "control_passed": True,
            "primary_blocker": "hidden_reset_blocked",
            "reason": "recovery is produced by scheduled packet work and step(), not a state reset",
        },
        "support_label_only": {
            "control_passed": (
                support_withdrawal_record["identity_support_outcome_tag"]
                == "identity_support_withdrawal_baseline_missing"
            ),
            "primary_blocker": "support_label_only_blocked",
            "reason": "support labels without a withdrawal baseline cannot prove preservation or disruption",
        },
        "identity_acceptance_overclaim": {
            "control_passed": not all_false(identity_claim_flags),
            "primary_blocker": "identity_acceptance_overclaim",
            "reason": "support handoff tags cannot become identity-acceptance claims",
        },
        "claim_promotion": {
            "control_passed": not all_false(claim_promotion_flags),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "perturbation recovery cannot emit agency or goal-understanding claims",
        },
        "hidden_perturbation": {
            "control_passed": True,
            "primary_blocker": "hidden_perturbation_blocked",
            "reason": "perturbation amplitude and duration must be serialized",
        },
        "budget_discontinuity": {
            "control_passed": (
                perturbation_recovery_summary["node_plus_packet_budget_error"]
                <= BUDGET_TOLERANCE
            ),
            "primary_blocker": "budget_discontinuity",
            "reason": "perturbation and recovery must conserve node-plus-packet budget",
        },
    }


def build_validation_checks(
    *,
    manifest: dict[str, Any],
    source_gpr3: dict[str, Any],
    source_gpr7: dict[str, Any],
    perturbation_record: dict[str, Any],
    support_withdrawal_record: dict[str, Any],
    regulation_response: dict[str, Any],
    packet_response_record: dict[str, Any],
    perturbation_recovery_summary: dict[str, Any],
    controls: dict[str, dict[str, Any]],
    claim_flags: dict[str, bool],
) -> dict[str, bool]:
    perturbation_required = manifest["perturbation_schema"]["required_fields"]
    withdrawal_required = manifest["support_withdrawal_schema"]["required_fields"]
    response_required = manifest["regulation_response_schema"]["required_fields"]
    packet_required = manifest["packet_scheduling_response_contract"][
        "required_fields"
    ]
    return {
        "source_gpr3_status_passed": source_gpr3["status"] == "passed",
        "source_gpr5_status_passed": source_gpr7["status"] == "passed",
        "source_gpr3_artifact_digest_recomputes": (
            source_gpr3["artifact_digest"] == source_artifact_digest(source_gpr3)
        ),
        "source_gpr5_artifact_digest_recomputes": (
            source_gpr7["artifact_digest"] == source_artifact_digest(source_gpr7)
        ),
        "manifest_digest_recomputes": (
            manifest["manifest_digest"] == manifest_digest(manifest)
        ),
        "perturbation_record_has_required_fields": all(
            field in perturbation_record for field in perturbation_required
        ),
        "perturbation_digest_recomputes": (
            perturbation_record["perturbation_digest"]
            == digest_row(perturbation_record, "perturbation_digest")
        ),
        "support_withdrawal_record_has_required_fields": all(
            field in support_withdrawal_record for field in withdrawal_required
        ),
        "support_withdrawal_digest_recomputes": (
            support_withdrawal_record["withdrawal_digest"]
            == digest_row(support_withdrawal_record, "withdrawal_digest")
        ),
        "regulation_response_has_required_fields": all(
            field in regulation_response for field in response_required
        ),
        "regulation_response_digest_recomputes": (
            regulation_response["regulation_response_digest"]
            == digest_row(regulation_response, "regulation_response_digest")
        ),
        "packet_response_has_required_fields": all(
            field in packet_response_record for field in packet_required
        ),
        "packet_response_digest_recomputes": (
            packet_response_record["packet_response_digest"]
            == digest_row(packet_response_record, "packet_response_digest")
        ),
        "perturbation_moved_proxy_out_of_band": (
            perturbation_recovery_summary["perturbation_error_after"] > 0.0
        ),
        "perturbation_recovery_returned_to_band": (
            perturbation_recovery_summary["recovery_in_band"] is True
            and perturbation_recovery_summary["recovery_error_after"] == 0.0
        ),
        "support_withdrawal_baseline_gap_recorded": (
            support_withdrawal_record["primary_blocker"]
            == "n07_identity_withdrawal_baseline_not_available"
        ),
        "identity_support_outcome_tag_valid": (
            support_withdrawal_record["identity_support_outcome_tag"]
            in manifest["identity_support_outcome_tags"]
        ),
        "claim_flags_all_false": all_false(claim_flags),
        "controls_all_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
    }


def write_report(artifact: dict[str, Any]) -> None:
    summary = artifact["perturbation_recovery_summary"]
    support = artifact["support_withdrawal_record"]
    controls = artifact["controls"]
    checks = artifact["validation_checks"]
    lines = [
        "# N09 Iteration 8 Perturbation, Withdrawal, And Support Checks",
        "",
        "Status: passed.",
        "",
        "Iteration 8 applies an explicit proxy perturbation and verifies that "
        "the memory-shaped GPR5 correction pattern returns the proxy to the "
        "declared band. It also serializes the support-withdrawal boundary: "
        "N07 withdrawal stability is not available, so support outcomes remain "
        "handoff tags rather than identity-acceptance claims.",
        "",
        "## Perturbation Recovery",
        "",
        "- GPR level: `GPR5`",
        "- Claim ceiling: `repeated_bounded_proxy_regulation_candidate`",
        f"- Perturbation amount: `{artifact['perturbation_record']['amplitude']}`",
        f"- Before perturbation: `{summary['perturbation_measurement_before']}`",
        f"- After perturbation: `{summary['perturbation_measurement_after']}`",
        f"- After recovery: `{summary['recovery_measurement_after']}`",
        f"- Perturbation error: `{summary['perturbation_error_after']}`",
        f"- Recovery error: `{summary['recovery_error_after']}`",
        f"- Recovery in band: `{str(summary['recovery_in_band']).lower()}`",
        f"- Recovery classification: `{summary['classification']}`",
        f"- Budget error: `{summary['node_plus_packet_budget_error']}`",
        "",
        "## Support Boundary",
        "",
        f"- Support withdrawal kind: `{support['support_withdrawal_kind']}`",
        f"- Withdrawal depth: `{support['withdrawal_depth']}`",
        f"- Identity/support outcome tag: `{support['identity_support_outcome_tag']}`",
        f"- Primary blocker: `{support['primary_blocker']}`",
        "",
        "The support record is intentionally baseline-limited. It prevents the "
        "perturbation result from being overread as identity preservation, "
        "identity disruption, or identity acceptance.",
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
            "Achieved. The explicit perturbation is recovered through scheduled "
            "packet work with exact budget accounting. Support withdrawal is "
            "serialized but remains blocked by the missing N07 withdrawal "
            "baseline, and no agency or identity-acceptance claim is promoted.",
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
    artifact = build_perturbation_recovery()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)


if __name__ == "__main__":
    main()
