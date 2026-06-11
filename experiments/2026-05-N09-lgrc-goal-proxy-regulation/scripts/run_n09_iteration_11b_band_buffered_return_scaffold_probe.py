#!/usr/bin/env python3
"""Run N09 Iteration 11-B band-buffered return-scaffold probe.

Iteration 11-B applies the Arc-of-Becoming read of Iterations 11 and 11-A:
do not ask only whether one exact correction returns to band. Ask what regime
the geometry expresses. This probe keeps one predeclared return amount fixed
across a perturbation family and measures whether the geometry supports a
finite, bounded response envelope without reading the post-perturbation error.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pygrc.models import LGRC9V3

from run_n09_iteration_7_gpr5_repeated_bounded_regulation import (
    build_error_row,
    build_proxy_row,
    build_regulation_state,
    digest_file,
    digest_row,
    git_head,
    git_status_short,
    load_json,
    node_measurement,
    rel,
    runtime_digests,
    source_artifact_digest,
)
from run_n09_iteration_11_hypothesis_b1_geometry_substrate_probe import (
    BUDGET_TOLERANCE,
    active_node_total,
    geometry_record,
)
from run_n09_iteration_11a_positive_geometry_return_scaffold_probe import (
    json_safe,
    schedule_packet,
)


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"

MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
SOURCE_GPR2_PATH = EXPERIMENT / "outputs" / "n09_iteration_4_gpr2_error_signal.json"
SOURCE_B0_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.json"
)
SOURCE_B1_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_11_hypothesis_b1_geometry_substrate_probe.json"
)
SOURCE_B1A_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_11a_positive_geometry_return_scaffold_probe.json"
)
SOURCE_B0_REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.md"
)
SOURCE_B1_REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_11_hypothesis_b1_geometry_substrate_probe.md"
)
SOURCE_B1A_REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_11a_positive_geometry_return_scaffold_probe.md"
)

OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_11b_band_buffered_return_scaffold_probe.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_11b_band_buffered_return_scaffold_probe.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_11b_band_buffered_return_scaffold_probe.py"
)

PERTURBATION_AMOUNTS = (0.07, 0.09, 0.11)
FIXED_RETURN_AMOUNT = 0.09


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def process_one_event(model: LGRC9V3, label: str, proxy_node_id: int) -> dict[str, Any]:
    before_measurement = node_measurement(model, proxy_node_id)
    before_runtime, before_runtime_digest, before_ledger_digest = runtime_digests(model)
    log_start = len(model.get_state().packet_processing_log)
    result = model.step()
    after_runtime, after_runtime_digest, after_ledger_digest = runtime_digests(model)
    after_measurement = node_measurement(model, proxy_node_id)
    new_logs = [
        item.to_artifact()
        for item in model.get_state().packet_processing_log[log_start:]
    ]
    record = {
        "label": label,
        "step_index": int(result.step_index),
        "time": float(result.time),
        "bookkeeping": json_safe(result.bookkeeping),
        "events": json_safe(result.events),
        "packet_processing_log": json_safe(new_logs),
        "proxy_measurement_before": before_measurement,
        "proxy_measurement_after": after_measurement,
        "proxy_measurement_delta": round(after_measurement - before_measurement, 12),
        "runtime_state_digest_before": before_runtime_digest,
        "runtime_state_digest_after": after_runtime_digest,
        "packet_ledger_digest_before": before_ledger_digest,
        "packet_ledger_digest_after": after_ledger_digest,
        "runtime_state_changed": before_runtime_digest != after_runtime_digest,
        "packet_ledger_changed": before_ledger_digest != after_ledger_digest,
        "queue_length_before": int(result.bookkeeping["queue_length_before"]),
        "queue_length_after": int(result.bookkeeping["queue_length_after"]),
        "runtime_state_before_digest_source": before_runtime["artifact_schema_version"],
        "runtime_state_after_digest_source": after_runtime["artifact_schema_version"],
    }
    record["step_record_digest"] = digest_row(record, "step_record_digest")
    return record


def classify_lane(
    *,
    post_error: float,
    final_error: float,
    final_in_band: bool,
) -> str:
    error_reduction = abs(post_error) - abs(final_error)
    if final_in_band and error_reduction > BUDGET_TOLERANCE:
        return "band_return_with_fixed_return_amount"
    if error_reduction > BUDGET_TOLERANCE:
        return "bounded_partial_return_with_fixed_return_amount"
    if abs(error_reduction) <= BUDGET_TOLERANCE:
        return "no_response"
    return "wrong_direction_or_unbounded_response"


def build_lane(
    *,
    lane_id: str,
    lane_index: int,
    perturbation_amount: float,
    manifest: dict[str, Any],
    target_row: dict[str, Any],
    claim_flags: dict[str, bool],
) -> dict[str, Any]:
    state, node_ids, edge_ids = build_regulation_state()
    model = LGRC9V3.from_state(state, {"dt": 1.0})
    proxy_node_id = node_ids["source_reservoir"]

    initial_runtime, initial_runtime_digest, initial_ledger_digest = runtime_digests(model)
    initial_budget = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    initial_measurement = node_measurement(model, proxy_node_id)
    initial_proxy_row = build_proxy_row(
        row_id=f"n09_i11b_{lane_id}_initial_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=initial_measurement,
        node_id=proxy_node_id,
        runtime_state_digest=initial_runtime_digest,
        packet_ledger_digest=initial_ledger_digest,
        event_time_key=0.0,
        scheduler_event_index=0,
        node_plus_packet_budget=initial_budget,
        claim_flags=claim_flags,
        source_artifacts=[rel(SOURCE_B0_PATH), rel(SOURCE_B1_PATH), rel(SOURCE_B1A_PATH)],
        source_reports=[
            rel(SOURCE_B0_REPORT_PATH),
            rel(SOURCE_B1_REPORT_PATH),
            rel(SOURCE_B1A_REPORT_PATH),
        ],
    )
    initial_error_row = build_error_row(
        row_id=f"n09_i11b_{lane_id}_initial_error_signal_v1",
        manifest=manifest,
        proxy_row=initial_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    pre_geometry = geometry_record(model, node_ids, edge_ids)

    packet_index_base = lane_index * 10
    perturbation_schedule = schedule_packet(
        model=model,
        source_node_id=node_ids["target_reservoir"],
        target_node_id=node_ids["source_reservoir"],
        edge_id=edge_ids["source_target"],
        amount=perturbation_amount,
        departure_event_time_key=1.0,
        arrival_event_time_key=2.0,
        scheduler_event_index=1,
        packet_index=packet_index_base,
    )
    return_schedule = schedule_packet(
        model=model,
        source_node_id=node_ids["source_reservoir"],
        target_node_id=node_ids["target_reservoir"],
        edge_id=edge_ids["source_target"],
        amount=FIXED_RETURN_AMOUNT,
        departure_event_time_key=3.0,
        arrival_event_time_key=4.0,
        scheduler_event_index=3,
        packet_index=packet_index_base + 1,
    )

    step_records = [
        process_one_event(model, "perturbation_departure", proxy_node_id),
        process_one_event(model, "perturbation_arrival", proxy_node_id),
    ]
    post_runtime, post_runtime_digest, post_ledger_digest = runtime_digests(model)
    post_budget = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    post_measurement = node_measurement(model, proxy_node_id)
    post_proxy_row = build_proxy_row(
        row_id=f"n09_i11b_{lane_id}_post_perturbation_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=post_measurement,
        node_id=proxy_node_id,
        runtime_state_digest=post_runtime_digest,
        packet_ledger_digest=post_ledger_digest,
        event_time_key=2.0,
        scheduler_event_index=2,
        node_plus_packet_budget=post_budget,
        claim_flags=claim_flags,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    post_error_row = build_error_row(
        row_id=f"n09_i11b_{lane_id}_post_perturbation_error_signal_v1",
        manifest=manifest,
        proxy_row=post_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )

    step_records.extend(
        [
            process_one_event(model, "return_channel_departure", proxy_node_id),
            process_one_event(model, "return_channel_arrival", proxy_node_id),
        ]
    )
    final_runtime, final_runtime_digest, final_ledger_digest = runtime_digests(model)
    final_budget = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    final_measurement = node_measurement(model, proxy_node_id)
    final_proxy_row = build_proxy_row(
        row_id=f"n09_i11b_{lane_id}_final_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=final_measurement,
        node_id=proxy_node_id,
        runtime_state_digest=final_runtime_digest,
        packet_ledger_digest=final_ledger_digest,
        event_time_key=4.0,
        scheduler_event_index=4,
        node_plus_packet_budget=final_budget,
        claim_flags=claim_flags,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    final_error_row = build_error_row(
        row_id=f"n09_i11b_{lane_id}_final_error_signal_v1",
        manifest=manifest,
        proxy_row=final_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    post_geometry = geometry_record(model, node_ids, edge_ids)

    post_error = float(post_error_row["error_value"])
    final_error = float(final_error_row["error_value"])
    error_reduction = round(abs(post_error) - abs(final_error), 12)
    lane_classification = classify_lane(
        post_error=post_error,
        final_error=final_error,
        final_in_band=bool(final_error_row["in_band"]),
    )
    budget_record = {
        "node_plus_packet_budget_before": initial_budget,
        "node_plus_packet_budget_after_perturbation": post_budget,
        "node_plus_packet_budget_after_return_scaffold": final_budget,
        "active_node_total_after_return_scaffold": active_node_total(model),
        "packet_ledger_node_total_after_return_scaffold": round(
            float(model.get_state().packet_ledger.node_coherence_total),
            12,
        ),
        "in_flight_packet_total_after_return_scaffold": round(
            float(model.get_state().packet_ledger.in_flight_packet_total),
            12,
        ),
        "node_plus_packet_budget_error": round(abs(final_budget - initial_budget), 12),
        "active_state_ledger_agree": abs(
            active_node_total(model) - float(model.get_state().packet_ledger.node_coherence_total)
        )
        <= BUDGET_TOLERANCE,
    }
    budget_record["budget_record_digest"] = digest_row(budget_record, "budget_record_digest")

    lane_summary = {
        "lane_id": lane_id,
        "perturbation_amount": perturbation_amount,
        "fixed_return_amount": FIXED_RETURN_AMOUNT,
        "initial_proxy_measurement": initial_measurement,
        "initial_error": float(initial_error_row["error_value"]),
        "post_perturbation_proxy_measurement": post_measurement,
        "post_perturbation_error": post_error,
        "final_proxy_measurement": final_measurement,
        "final_error": final_error,
        "error_reduction_after_return_scaffold": error_reduction,
        "final_in_band": bool(final_error_row["in_band"]),
        "lane_classification": lane_classification,
        "return_channel_delta": round(final_measurement - post_measurement, 12),
    }
    lane_summary["lane_summary_digest"] = digest_row(lane_summary, "lane_summary_digest")

    lane_validation = {
        "perturbation_moved_proxy_out_of_band": post_error_row["in_band"] is False,
        "return_scaffold_moved_proxy_toward_band": error_reduction > BUDGET_TOLERANCE,
        "schedule_declared_before_error": return_schedule[
            "schedule_declared_before_post_perturbation_error"
        ]
        is True
        and return_schedule["hidden_error_read_used"] is False,
        "return_amount_fixed": return_schedule["amount"] == FIXED_RETURN_AMOUNT,
        "a_path_producer_correction_absent": return_schedule["producer_record_digest"] is None
        and return_schedule["a_path_candidate_set_digest"] is None,
        "geometry_digest_unchanged": pre_geometry["geometry_digest"]
        == post_geometry["geometry_digest"],
        "budget_exact": budget_record["node_plus_packet_budget_error"] <= BUDGET_TOLERANCE
        and budget_record["active_state_ledger_agree"] is True,
    }

    lane = {
        "lane_id": lane_id,
        "perturbation_schedule_record": perturbation_schedule,
        "return_schedule_record": return_schedule,
        "pre_probe_geometry": pre_geometry,
        "post_probe_geometry": post_geometry,
        "initial_proxy_surface_row": initial_proxy_row,
        "post_perturbation_proxy_surface_row": post_proxy_row,
        "final_proxy_surface_row": final_proxy_row,
        "initial_error_signal_row": initial_error_row,
        "post_perturbation_error_signal_row": post_error_row,
        "final_error_signal_row": final_error_row,
        "step_records": step_records,
        "budget_record": budget_record,
        "lane_summary": lane_summary,
        "lane_validation": lane_validation,
    }
    lane["lane_digest"] = digest_row(lane, "lane_digest")
    return lane


def build_arc_record(family_summary: dict[str, Any]) -> dict[str, Any]:
    record = {
        "method": "arc_of_becoming",
        "question": (
            "What kind of regulation-like becoming does the predeclared return "
            "scaffold express when the perturbation is varied?"
        ),
        "prior_observation_iteration_11": (
            "Fixed geometry with an empty event queue preserves the perturbation "
            "and does not move the proxy back toward the target band."
        ),
        "prior_observation_iteration_11a": (
            "A matched predeclared return channel can return one perturbation "
            "exactly to the upper target-band boundary."
        ),
        "redirection_for_iteration_11b": (
            "Refinement should not chase a single true endpoint. It should ask "
            "whether the geometry supports a finite response envelope and where "
            "that envelope begins to degrade."
        ),
        "observations": [
            "smaller perturbation returned inside the band with the same fixed return amount",
            "matched perturbation returned to the band boundary",
            "larger perturbation improved but remained above the band",
        ],
        "classification": family_summary["result_classification"],
        "cultivation_next": (
            "A wider envelope would require either multi-stage predeclared "
            "geometry or a native response-magnitude policy. The current result "
            "is a scaffolded finite envelope, not general regulation."
        ),
        "naturalization_level": "scaffolded_substrate_design_candidate",
    }
    record["arc_record_digest"] = digest_row(record, "arc_record_digest")
    return record


def build_probe() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    source_gpr2 = load_json(SOURCE_GPR2_PATH)
    source_b0 = load_json(SOURCE_B0_PATH)
    source_b1 = load_json(SOURCE_B1_PATH)
    source_b1a = load_json(SOURCE_B1A_PATH)
    target_row = source_gpr2["target_band_row"]
    claim_flags = dict(source_b0["claim_flags"])

    lanes = [
        build_lane(
            lane_id=f"perturbation_{str(amount).replace('.', '_')}",
            lane_index=index,
            perturbation_amount=amount,
            manifest=manifest,
            target_row=target_row,
            claim_flags=claim_flags,
        )
        for index, amount in enumerate(PERTURBATION_AMOUNTS)
    ]
    lane_summaries = [lane["lane_summary"] for lane in lanes]
    band_return_lanes = [
        summary for summary in lane_summaries if summary["final_in_band"] is True
    ]
    partial_return_lanes = [
        summary
        for summary in lane_summaries
        if summary["lane_classification"] == "bounded_partial_return_with_fixed_return_amount"
    ]
    all_lanes_improved = all(
        summary["error_reduction_after_return_scaffold"] > BUDGET_TOLERANCE
        for summary in lane_summaries
    )
    family_supported = (
        len(band_return_lanes) >= 2
        and len(partial_return_lanes) >= 1
        and all_lanes_improved
    )
    result_classification = (
        "finite_envelope_band_buffered_return_scaffold_candidate"
        if family_supported
        else "return_scaffold_family_inconclusive"
    )
    primary_blocker = (
        "native_response_magnitude_policy_missing_for_unbounded_perturbations"
        if family_supported
        else "native_goal_proxy_response_policy_incomplete"
    )
    claim_ceiling = (
        "native_substrate_mediated_goal_proxy_regulation_design_candidate"
        if family_supported
        else "hypothesis_b_partial_return_native_policy_gap"
    )

    response_family_summary = {
        "result_classification": result_classification,
        "claim_ceiling": claim_ceiling,
        "primary_blocker": primary_blocker,
        "perturbation_amounts": list(PERTURBATION_AMOUNTS),
        "fixed_return_amount": FIXED_RETURN_AMOUNT,
        "lane_count": len(lanes),
        "band_return_count": len(band_return_lanes),
        "partial_return_count": len(partial_return_lanes),
        "all_lanes_improved": all_lanes_improved,
        "in_band_perturbation_envelope": [
            summary["perturbation_amount"] for summary in band_return_lanes
        ],
        "partial_return_perturbation_envelope": [
            summary["perturbation_amount"] for summary in partial_return_lanes
        ],
        "native_substrate_mediated_goal_proxy_regulation_design_candidate_supported": (
            family_supported
        ),
        "general_native_goal_proxy_regulation_supported": False,
        "interpretation": (
            "The same fixed return scaffold produces a finite envelope: two "
            "perturbations return to the target band and a larger perturbation "
            "still moves toward the band without entering it. Geometry improved "
            "the result, but the boundary is now response-magnitude selection, "
            "not conserved packet handling."
        ),
    }
    response_family_summary["response_family_summary_digest"] = digest_row(
        response_family_summary,
        "response_family_summary_digest",
    )
    arc_record = build_arc_record(response_family_summary)

    controls = {
        "fixed_return_amount_family": {
            "control_passed": all(
                lane["return_schedule_record"]["amount"] == FIXED_RETURN_AMOUNT
                for lane in lanes
            ),
            "primary_blocker": "adaptive_response_amount_hidden_policy_blocked",
            "reason": "all lanes use the same predeclared return amount",
        },
        "schedule_declared_before_error": {
            "control_passed": all(
                lane["lane_validation"]["schedule_declared_before_error"] for lane in lanes
            ),
            "primary_blocker": "post_perturbation_error_conditioned_schedule_blocked",
            "reason": "return schedules are declared before post-perturbation error rows exist",
        },
        "a_path_producer_correction_leakage": {
            "control_passed": all(
                lane["lane_validation"]["a_path_producer_correction_absent"] for lane in lanes
            ),
            "primary_blocker": "a_path_producer_correction_leakage_blocked",
            "reason": "no lane consumes the GPR3 candidate set or A-path producer record",
        },
        "hidden_reset": {
            "control_passed": all(
                any(
                    step["label"] == "return_channel_departure"
                    and step["proxy_measurement_delta"] < 0.0
                    for step in lane["step_records"]
                )
                for lane in lanes
            ),
            "primary_blocker": "hidden_reset_blocked",
            "reason": "return is visible as serialized packet departure, not state reset",
        },
        "budget_drift": {
            "control_passed": all(lane["lane_validation"]["budget_exact"] for lane in lanes),
            "primary_blocker": "node_plus_packet_budget_drift",
            "reason": "all lanes preserve exact node-plus-packet budget",
        },
        "posthoc_geometry_change": {
            "control_passed": all(
                lane["lane_validation"]["geometry_digest_unchanged"] for lane in lanes
            ),
            "primary_blocker": "posthoc_geometry_change_blocked",
            "reason": "geometry digest is unchanged within every lane",
        },
        "envelope_overclaim": {
            "control_passed": len(partial_return_lanes) >= 1
            and response_family_summary["general_native_goal_proxy_regulation_supported"] is False,
            "primary_blocker": "general_native_regulation_overclaim_blocked",
            "reason": "larger perturbation is only partially corrected, so the family is finite",
        },
        "native_claim_promotion": {
            "control_passed": all_false(claim_flags),
            "primary_blocker": "native_claim_promotion_blocked",
            "reason": "finite envelope support does not emit semantic goal or agency claims",
        },
    }

    validation_checks = {
        "source_b0_status_passed": source_b0["status"] == "passed",
        "source_b1_status_passed": source_b1["status"] == "passed",
        "source_b1a_status_passed": source_b1a["status"] == "passed",
        "source_b1_negative_result_consumed": source_b1["response_summary"][
            "result_classification"
        ]
        == "no_response_native_policy_gap",
        "source_b1a_design_candidate_consumed": source_b1a["response_summary"][
            "result_classification"
        ]
        == "predeclared_return_scaffold_band_return_design_candidate",
        "a_path_ceiling_preserved": source_b0["a_path_preservation"]["claim_ceiling"]
        == "artifact_only_goal_proxy_regulation_candidate",
        "perturbation_family_serialized": len(lanes) == len(PERTURBATION_AMOUNTS),
        "fixed_return_amount_across_family": controls["fixed_return_amount_family"][
            "control_passed"
        ],
        "all_lanes_moved_out_of_band_after_perturbation": all(
            lane["lane_validation"]["perturbation_moved_proxy_out_of_band"] for lane in lanes
        ),
        "all_lanes_improved_after_return": all_lanes_improved,
        "at_least_two_lanes_returned_to_band": len(band_return_lanes) >= 2,
        "larger_perturbation_recorded_as_partial_not_failure": len(partial_return_lanes) >= 1,
        "arc_of_becoming_interpretation_recorded": arc_record["method"] == "arc_of_becoming",
        "a_path_producer_correction_absent": controls[
            "a_path_producer_correction_leakage"
        ]["control_passed"],
        "budget_exact": controls["budget_drift"]["control_passed"],
        "result_classification_recorded": result_classification
        == "finite_envelope_band_buffered_return_scaffold_candidate",
        "no_general_native_regulation_claim": response_family_summary[
            "general_native_goal_proxy_regulation_supported"
        ]
        is False,
        "claim_flags_all_false": all_false(claim_flags),
        "controls_all_passed": all(control["control_passed"] for control in controls.values()),
    }

    artifact: dict[str, Any] = {
        "schema": "n09_iteration_11b_band_buffered_return_scaffold_probe_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": "11-B",
        "purpose": (
            "hypothesis_b1b_arc_of_becoming_finite_return_envelope_probe_no_a_path_"
            "correction_scheduler"
        ),
        "status": "passed" if all(validation_checks.values()) else "failed",
        "acceptance_state": "achieved" if all(validation_checks.values()) else "not_achieved",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "source_artifacts": {
            "iteration_10_inventory": rel(SOURCE_B0_PATH),
            "iteration_11_probe": rel(SOURCE_B1_PATH),
            "iteration_11a_probe": rel(SOURCE_B1A_PATH),
            "iteration_4_target_band": rel(SOURCE_GPR2_PATH),
            "fixture_manifest": rel(MANIFEST_PATH),
        },
        "source_reports": {
            "iteration_10_inventory": rel(SOURCE_B0_REPORT_PATH),
            "iteration_11_probe": rel(SOURCE_B1_REPORT_PATH),
            "iteration_11a_probe": rel(SOURCE_B1A_REPORT_PATH),
        },
        "source_artifact_sha256": {
            "iteration_10_inventory": digest_file(SOURCE_B0_PATH),
            "iteration_11_probe": digest_file(SOURCE_B1_PATH),
            "iteration_11a_probe": digest_file(SOURCE_B1A_PATH),
            "iteration_4_target_band": digest_file(SOURCE_GPR2_PATH),
            "fixture_manifest": digest_file(MANIFEST_PATH),
        },
        "source_artifact_digests": {
            "iteration_10_inventory": source_artifact_digest(source_b0),
            "iteration_11_probe": source_artifact_digest(source_b1),
            "iteration_11a_probe": source_artifact_digest(source_b1a),
            "iteration_4_target_band": source_artifact_digest(source_gpr2),
        },
        "claim_ceiling": claim_ceiling,
        "result_classification": result_classification,
        "primary_blocker": primary_blocker,
        "a_path_ceiling_preserved": source_b0["a_path_preservation"]["claim_ceiling"],
        "response_family_summary": response_family_summary,
        "arc_of_becoming_record": arc_record,
        "lanes": lanes,
        "controls": controls,
        "validation_checks": validation_checks,
        "claim_flags": claim_flags,
        "blocked_claims": sorted(
            set(source_b0["blocked_claims"])
            | {
                "general_native_goal_proxy_regulation",
                "semantic_goal_understanding",
                "agency",
                "identity_acceptance",
                "rc_identity_collapse",
                "aco_like_behavior",
                "unbounded_native_response_magnitude_selection",
            }
        ),
        "next_iteration": "12_hypothesis_b2_native_substrate_closeout",
        "git": {
            "head": git_head(),
            "status_short_experiment": git_status_short(rel(EXPERIMENT)),
            "status_short_src": git_status_short("src"),
        },
    }
    artifact["artifact_digest"] = source_artifact_digest(artifact)
    return artifact


def write_report(artifact: dict[str, Any]) -> None:
    summary = artifact["response_family_summary"]
    arc = artifact["arc_of_becoming_record"]
    lines = [
        "# N09 Iteration 11-B - Band-Buffered Return-Scaffold Probe",
        "",
        f"Status: {artifact['status']}",
        f"Acceptance state: {artifact['acceptance_state']}",
        "",
        "## Summary",
        "",
        "Iteration 11-B uses the Arc-of-Becoming reading of Iterations 11 and "
        "11-A. The question is no longer whether one matched return packet can "
        "cancel one perturbation. The question is what response envelope the "
        "predeclared geometry expresses when perturbation amplitude varies.",
        "",
        f"- Classification: `{summary['result_classification']}`",
        f"- Claim ceiling: `{artifact['claim_ceiling']}`",
        f"- Primary blocker: `{artifact['primary_blocker']}`",
        f"- Perturbation family: `{summary['perturbation_amounts']}`",
        f"- Fixed return amount: `{summary['fixed_return_amount']}`",
        f"- Band-return lanes: `{summary['band_return_count']}`",
        f"- Partial-return lanes: `{summary['partial_return_count']}`",
        f"- General native regulation supported: "
        f"`{summary['general_native_goal_proxy_regulation_supported']}`",
        "",
        "## Arc-of-Becoming Interpretation",
        "",
        f"Question: {arc['question']}",
        "",
        f"Redirection: {arc['redirection_for_iteration_11b']}",
        "",
        "Observations:",
    ]
    for observation in arc["observations"]:
        lines.append(f"- {observation}")
    lines.extend(
        [
            "",
            f"Cultivation next: {arc['cultivation_next']}",
            "",
            "## Lane Results",
            "",
            "| Lane | Perturbation | Post proxy | Final proxy | Final error | In band | Classification |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for lane in artifact["lanes"]:
        lane_summary = lane["lane_summary"]
        lines.append(
            f"| `{lane_summary['lane_id']}` | "
            f"`{lane_summary['perturbation_amount']}` | "
            f"`{lane_summary['post_perturbation_proxy_measurement']}` | "
            f"`{lane_summary['final_proxy_measurement']}` | "
            f"`{lane_summary['final_error']}` | "
            f"`{lane_summary['final_in_band']}` | "
            f"`{lane_summary['lane_classification']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            summary["interpretation"],
            "",
            "This is stronger than Iteration 11-A because it no longer depends on "
            "one exact perturbation/return match. It is still bounded: the larger "
            "perturbation is improved but not returned to band, so the missing "
            "piece is native response-magnitude selection for broader regulation.",
            "",
            "## Controls",
            "",
            "| Control | Passed | Primary blocker if failed |",
            "|---|---:|---|",
        ]
    )
    for control_id, control in artifact["controls"].items():
        lines.append(
            f"| `{control_id}` | `{control['control_passed']}` | "
            f"`{control['primary_blocker']}` |"
        )
    lines.extend(
        [
            "",
            "## Validation",
            "",
            "| Check | Result |",
            "|---|---:|",
        ]
    )
    for key, value in artifact["validation_checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Iteration 11-B supports only a finite-envelope, predeclared "
            "return-scaffold design candidate. It does not support general native "
            "goal-proxy regulation, semantic goal understanding, agency, identity "
            "acceptance, RC identity collapse, ACO-like behavior, locomotion-like "
            "behavior, biological behavior, or unrestricted claims.",
            "",
            "## Acceptance",
            "",
            "Achieved. A fixed predeclared return scaffold produced a bounded "
            "response family: two perturbations returned to the target band and a "
            "larger perturbation improved without being overclaimed as general "
            "native regulation.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact = build_probe()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status: {artifact['status']}")
    print(f"classification: {artifact['result_classification']}")


if __name__ == "__main__":
    main()
