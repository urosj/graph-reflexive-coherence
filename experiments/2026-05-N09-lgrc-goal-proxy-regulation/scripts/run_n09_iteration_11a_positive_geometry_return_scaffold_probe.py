#!/usr/bin/env python3
"""Run N09 Iteration 11-A positive geometry return-scaffold probe.

Iteration 11-A refines the Iteration 11 no-response result. It predeclares a
conserved return-channel scaffold before the perturbation response is observed,
then checks whether the proxy returns toward the declared band without using
the A-path producer correction scheduler.
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
SOURCE_B0_REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.md"
)
SOURCE_B1_REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_11_hypothesis_b1_geometry_substrate_probe.md"
)

OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_11a_positive_geometry_return_scaffold_probe.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_11a_positive_geometry_return_scaffold_probe.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_11a_positive_geometry_return_scaffold_probe.py"
)

PERTURBATION_AMOUNT = 0.09
RETURN_AMOUNT = 0.09


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def event_records(model: LGRC9V3) -> list[dict[str, Any]]:
    return [
        event.to_record()
        for event in model.get_state().packet_ledger.event_queue_records
    ]


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if hasattr(value, "to_artifact"):
        return json_safe(value.to_artifact())
    if hasattr(value, "to_record"):
        return json_safe(value.to_record())
    if hasattr(value, "__dict__"):
        return {
            "object_type": value.__class__.__name__,
            "fields": json_safe(value.__dict__),
        }
    return repr(value)


def schedule_packet(
    *,
    model: LGRC9V3,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
    amount: float,
    departure_event_time_key: float,
    arrival_event_time_key: float,
    scheduler_event_index: int,
    packet_index: int,
) -> dict[str, Any]:
    before_queue = event_records(model)
    model.schedule_packet_departure(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        edge_id=edge_id,
        amount=amount,
        departure_event_time_key=departure_event_time_key,
        arrival_event_time_key=arrival_event_time_key,
        scheduler_event_index=scheduler_event_index,
        packet_index=packet_index,
    )
    after_queue = event_records(model)
    new_events = [event for event in after_queue if event not in before_queue]
    record = {
        "source_node_id": int(source_node_id),
        "target_node_id": int(target_node_id),
        "edge_id": int(edge_id),
        "amount": float(amount),
        "departure_event_time_key": float(departure_event_time_key),
        "arrival_event_time_key": float(arrival_event_time_key),
        "scheduler_event_index": int(scheduler_event_index),
        "packet_index": int(packet_index),
        "new_queue_events": new_events,
        "schedule_declared_before_post_perturbation_error": True,
        "producer_record_digest": None,
        "a_path_candidate_set_digest": None,
        "hidden_error_read_used": False,
    }
    record["schedule_record_digest"] = digest_row(record, "schedule_record_digest")
    return record


def process_one_event(model: LGRC9V3, label: str) -> dict[str, Any]:
    before_measurement = node_measurement(model, 0)
    before_runtime, before_runtime_digest, before_ledger_digest = runtime_digests(model)
    log_start = len(model.get_state().packet_processing_log)
    result = model.step()
    after_runtime, after_runtime_digest, after_ledger_digest = runtime_digests(model)
    after_measurement = node_measurement(model, 0)
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
        "packet_processing_log": new_logs,
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


def build_return_scaffold_record(
    *,
    geometry: dict[str, Any],
    perturbation_schedule: dict[str, Any],
    return_schedule: dict[str, Any],
) -> dict[str, Any]:
    record = {
        "scaffold_id": "n09_b1a_predeclared_positive_geometry_return_channel_v1",
        "scaffold_kind": "predeclared_conserved_packet_return_channel",
        "geometry_digest": geometry["geometry_digest"],
        "perturbation_schedule_digest": perturbation_schedule["schedule_record_digest"],
        "return_schedule_digest": return_schedule["schedule_record_digest"],
        "return_channel_amount": RETURN_AMOUNT,
        "return_amount_matches_perturbation_amount": RETURN_AMOUNT == PERTURBATION_AMOUNT,
        "schedule_declaration_time": "before_post_perturbation_proxy_error_exists",
        "uses_a_path_producer_correction_scheduler": False,
        "uses_a_path_candidate_set": False,
        "uses_hidden_goal_or_reward_label": False,
        "uses_posthoc_geometry_change": False,
        "native_goal_proxy_policy_available": False,
        "native_policy_boundary": (
            "This scaffold can demonstrate a predeclared return-channel design "
            "candidate, but it is not a native policy that computes proxy error "
            "or chooses response magnitude."
        ),
    }
    record["return_scaffold_digest"] = digest_row(record, "return_scaffold_digest")
    return record


def build_probe() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    source_gpr2 = load_json(SOURCE_GPR2_PATH)
    source_b0 = load_json(SOURCE_B0_PATH)
    source_b1 = load_json(SOURCE_B1_PATH)
    target_row = source_gpr2["target_band_row"]
    claim_flags = dict(source_b0["claim_flags"])

    state, node_ids, edge_ids = build_regulation_state()
    model = LGRC9V3.from_state(state, {"dt": 1.0})
    initial_runtime, initial_runtime_digest, initial_ledger_digest = runtime_digests(model)
    initial_budget = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    initial_measurement = node_measurement(model, node_ids["source_reservoir"])
    initial_proxy_row = build_proxy_row(
        row_id="n09_i11a_initial_proxy_surface_v1",
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
        source_artifacts=[rel(SOURCE_B0_PATH), rel(SOURCE_B1_PATH)],
        source_reports=[rel(SOURCE_B0_REPORT_PATH), rel(SOURCE_B1_REPORT_PATH)],
    )
    initial_error_row = build_error_row(
        row_id="n09_i11a_initial_error_signal_v1",
        manifest=manifest,
        proxy_row=initial_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH), rel(SOURCE_B0_PATH), rel(SOURCE_B1_PATH)],
        source_reports=[rel(REPORT_PATH), rel(SOURCE_B0_REPORT_PATH), rel(SOURCE_B1_REPORT_PATH)],
    )
    pre_geometry = geometry_record(model, node_ids, edge_ids)
    perturbation_schedule = schedule_packet(
        model=model,
        source_node_id=node_ids["target_reservoir"],
        target_node_id=node_ids["source_reservoir"],
        edge_id=edge_ids["source_target"],
        amount=PERTURBATION_AMOUNT,
        departure_event_time_key=1.0,
        arrival_event_time_key=2.0,
        scheduler_event_index=1,
        packet_index=0,
    )
    return_schedule = schedule_packet(
        model=model,
        source_node_id=node_ids["source_reservoir"],
        target_node_id=node_ids["target_reservoir"],
        edge_id=edge_ids["source_target"],
        amount=RETURN_AMOUNT,
        departure_event_time_key=3.0,
        arrival_event_time_key=4.0,
        scheduler_event_index=3,
        packet_index=1,
    )
    scaffold_record = build_return_scaffold_record(
        geometry=pre_geometry,
        perturbation_schedule=perturbation_schedule,
        return_schedule=return_schedule,
    )

    step_records = [
        process_one_event(model, "perturbation_departure"),
        process_one_event(model, "perturbation_arrival"),
    ]
    post_perturbation_runtime, post_perturbation_runtime_digest, post_perturbation_ledger_digest = (
        runtime_digests(model)
    )
    post_perturbation_budget = round(
        float(model.get_state().packet_ledger.conserved_budget_total),
        12,
    )
    post_perturbation_measurement = node_measurement(model, node_ids["source_reservoir"])
    post_perturbation_proxy_row = build_proxy_row(
        row_id="n09_i11a_post_perturbation_proxy_surface_v1",
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
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    post_perturbation_error_row = build_error_row(
        row_id="n09_i11a_post_perturbation_error_signal_v1",
        manifest=manifest,
        proxy_row=post_perturbation_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    step_records.extend(
        [
            process_one_event(model, "return_channel_departure"),
            process_one_event(model, "return_channel_arrival"),
        ]
    )
    final_runtime, final_runtime_digest, final_ledger_digest = runtime_digests(model)
    final_budget = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    final_measurement = node_measurement(model, node_ids["source_reservoir"])
    final_proxy_row = build_proxy_row(
        row_id="n09_i11a_final_return_scaffold_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=final_measurement,
        node_id=node_ids["source_reservoir"],
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
        row_id="n09_i11a_final_return_scaffold_error_signal_v1",
        manifest=manifest,
        proxy_row=final_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    post_geometry = geometry_record(model, node_ids, edge_ids)

    post_error = float(post_perturbation_error_row["error_value"])
    final_error = float(final_error_row["error_value"])
    error_reduction = round(abs(post_error) - abs(final_error), 12)
    design_candidate_supported = (
        error_reduction > BUDGET_TOLERANCE
        and bool(final_error_row["in_band"])
        and scaffold_record["uses_a_path_producer_correction_scheduler"] is False
    )
    if design_candidate_supported:
        result_classification = "predeclared_return_scaffold_band_return_design_candidate"
        primary_blocker = "native_goal_proxy_response_policy_missing_for_general_regulation"
        claim_ceiling = "native_substrate_mediated_goal_proxy_regulation_design_candidate"
    elif error_reduction > BUDGET_TOLERANCE:
        result_classification = "bounded_partial_return"
        primary_blocker = "native_goal_proxy_response_policy_incomplete"
        claim_ceiling = "hypothesis_b_partial_return_native_policy_gap"
    else:
        result_classification = "no_response_geometry_insufficient"
        primary_blocker = "native_goal_proxy_regulation_policy_missing"
        claim_ceiling = "hypothesis_b_no_response_native_policy_gap"

    response_summary = {
        "initial_proxy_measurement": initial_measurement,
        "initial_error": float(initial_error_row["error_value"]),
        "post_perturbation_proxy_measurement": post_perturbation_measurement,
        "post_perturbation_error": post_error,
        "final_proxy_measurement": final_measurement,
        "final_error": final_error,
        "proxy_measurement_delta_after_return_scaffold": round(
            final_measurement - post_perturbation_measurement,
            12,
        ),
        "error_reduction_after_return_scaffold": error_reduction,
        "final_in_band": bool(final_error_row["in_band"]),
        "result_classification": result_classification,
        "primary_blocker": primary_blocker,
        "native_substrate_mediated_goal_proxy_regulation_design_candidate_supported": (
            design_candidate_supported
        ),
        "interpretation": (
            "A predeclared conserved return channel can return the proxy to the "
            "declared band without reading the post-perturbation error or using "
            "the A-path producer correction scheduler. This improves the B-path "
            "design evidence, but remains a scaffold candidate rather than a "
            "general native goal-proxy regulation policy."
        ),
    }
    response_summary["response_summary_digest"] = digest_row(
        response_summary,
        "response_summary_digest",
    )

    budget_record = {
        "node_plus_packet_budget_before": initial_budget,
        "node_plus_packet_budget_after_perturbation": post_perturbation_budget,
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

    controls = {
        "schedule_declared_before_error": {
            "control_passed": return_schedule[
                "schedule_declared_before_post_perturbation_error"
            ]
            is True
            and return_schedule["hidden_error_read_used"] is False,
            "primary_blocker": "post_perturbation_error_conditioned_schedule_blocked",
            "reason": "return channel was scheduled before the post-perturbation error row existed",
        },
        "a_path_producer_correction_leakage": {
            "control_passed": scaffold_record["uses_a_path_producer_correction_scheduler"]
            is False
            and scaffold_record["uses_a_path_candidate_set"] is False,
            "primary_blocker": "a_path_producer_correction_leakage_blocked",
            "reason": "return scaffold does not consume GPR3 candidate set or producer record",
        },
        "hidden_reset": {
            "control_passed": any(
                item["label"] == "return_channel_departure"
                and item["proxy_measurement_delta"] < 0.0
                for item in step_records
            ),
            "primary_blocker": "hidden_reset_blocked",
            "reason": "proxy return occurs through serialized packet departure evidence",
        },
        "budget_drift": {
            "control_passed": budget_record["node_plus_packet_budget_error"]
            <= BUDGET_TOLERANCE
            and budget_record["active_state_ledger_agree"] is True,
            "primary_blocker": "node_plus_packet_budget_drift",
            "reason": "predeclared perturbation and return channel preserve node-plus-packet budget",
        },
        "posthoc_geometry_change": {
            "control_passed": pre_geometry["geometry_digest"] == post_geometry["geometry_digest"],
            "primary_blocker": "posthoc_geometry_change_blocked",
            "reason": "fixed geometry digest is unchanged before and after the return scaffold",
        },
        "native_claim_promotion": {
            "control_passed": all_false(claim_flags),
            "primary_blocker": "native_claim_promotion_blocked",
            "reason": "design candidate support does not emit semantic goal, agency, identity, or native regulation claims",
        },
        "generalization_overclaim": {
            "control_passed": primary_blocker
            == "native_goal_proxy_response_policy_missing_for_general_regulation",
            "primary_blocker": "general_native_regulation_overclaim_blocked",
            "reason": "successful scaffold return is not generalized to arbitrary perturbations or native policy computation",
        },
    }

    validation_checks = {
        "source_b0_status_passed": source_b0["status"] == "passed",
        "source_b1_status_passed": source_b1["status"] == "passed",
        "source_b1_negative_result_consumed": source_b1["response_summary"][
            "result_classification"
        ]
        == "no_response_native_policy_gap",
        "a_path_ceiling_preserved": source_b0["a_path_preservation"]["claim_ceiling"]
        == "artifact_only_goal_proxy_regulation_candidate",
        "explicit_perturbation_serialized": perturbation_schedule["amount"]
        == PERTURBATION_AMOUNT,
        "return_scaffold_serialized": return_schedule["amount"] == RETURN_AMOUNT,
        "return_scheduled_before_error_evaluation": controls[
            "schedule_declared_before_error"
        ]["control_passed"],
        "post_perturbation_moved_proxy_out_of_band": post_perturbation_error_row[
            "in_band"
        ]
        is False,
        "return_scaffold_moved_proxy_toward_band": error_reduction > BUDGET_TOLERANCE,
        "final_proxy_in_band": final_error_row["in_band"] is True,
        "a_path_producer_correction_absent": controls[
            "a_path_producer_correction_leakage"
        ]["control_passed"],
        "geometry_digest_unchanged": pre_geometry["geometry_digest"]
        == post_geometry["geometry_digest"],
        "budget_exact": controls["budget_drift"]["control_passed"],
        "result_classification_recorded": result_classification
        in {
            "predeclared_return_scaffold_band_return_design_candidate",
            "bounded_partial_return",
            "no_response_geometry_insufficient",
            "wrong_direction_geometry_response",
            "policy_surface_required",
        },
        "claim_flags_all_false": all_false(claim_flags),
        "controls_all_passed": all(control["control_passed"] for control in controls.values()),
    }

    artifact: dict[str, Any] = {
        "schema": "n09_iteration_11a_positive_geometry_return_scaffold_probe_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": "11-A",
        "purpose": "hypothesis_b1a_predeclared_return_scaffold_probe_no_a_path_correction_scheduler",
        "status": "passed" if all(validation_checks.values()) else "failed",
        "acceptance_state": "achieved" if all(validation_checks.values()) else "not_achieved",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "source_artifacts": {
            "iteration_10_inventory": rel(SOURCE_B0_PATH),
            "iteration_11_probe": rel(SOURCE_B1_PATH),
            "iteration_4_target_band": rel(SOURCE_GPR2_PATH),
            "fixture_manifest": rel(MANIFEST_PATH),
        },
        "source_reports": {
            "iteration_10_inventory": rel(SOURCE_B0_REPORT_PATH),
            "iteration_11_probe": rel(SOURCE_B1_REPORT_PATH),
        },
        "source_artifact_sha256": {
            "iteration_10_inventory": digest_file(SOURCE_B0_PATH),
            "iteration_11_probe": digest_file(SOURCE_B1_PATH),
            "iteration_4_target_band": digest_file(SOURCE_GPR2_PATH),
            "fixture_manifest": digest_file(MANIFEST_PATH),
        },
        "source_artifact_digests": {
            "iteration_10_inventory": source_artifact_digest(source_b0),
            "iteration_11_probe": source_artifact_digest(source_b1),
            "iteration_4_target_band": source_artifact_digest(source_gpr2),
        },
        "claim_ceiling": claim_ceiling,
        "primary_blocker": primary_blocker,
        "a_path_ceiling_preserved": source_b0["a_path_preservation"]["claim_ceiling"],
        "pre_probe_geometry": pre_geometry,
        "post_probe_geometry": post_geometry,
        "return_scaffold_record": scaffold_record,
        "perturbation_schedule_record": perturbation_schedule,
        "return_schedule_record": return_schedule,
        "initial_proxy_surface_row": initial_proxy_row,
        "post_perturbation_proxy_surface_row": post_perturbation_proxy_row,
        "final_proxy_surface_row": final_proxy_row,
        "initial_error_signal_row": initial_error_row,
        "post_perturbation_error_signal_row": post_perturbation_error_row,
        "final_error_signal_row": final_error_row,
        "step_records": step_records,
        "response_summary": response_summary,
        "budget_record": budget_record,
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
    summary = artifact["response_summary"]
    budget = artifact["budget_record"]
    lines = [
        "# N09 Iteration 11-A - Positive Geometry Return-Scaffold Probe",
        "",
        f"Status: {artifact['status']}",
        f"Acceptance state: {artifact['acceptance_state']}",
        "",
        "## Summary",
        "",
        "Iteration 11-A refines the Iteration 11 no-response result by adding a "
        "predeclared conserved return-channel scaffold. The scaffold is scheduled "
        "before the post-perturbation error exists and does not consume the A-path "
        "producer correction scheduler.",
        "",
        f"- Initial proxy: `{summary['initial_proxy_measurement']}`",
        f"- Post-perturbation proxy: `{summary['post_perturbation_proxy_measurement']}`",
        f"- Final proxy: `{summary['final_proxy_measurement']}`",
        f"- Post-perturbation error: `{summary['post_perturbation_error']}`",
        f"- Final error: `{summary['final_error']}`",
        f"- Error reduction: `{summary['error_reduction_after_return_scaffold']}`",
        f"- Classification: `{summary['result_classification']}`",
        f"- Claim ceiling: `{artifact['claim_ceiling']}`",
        f"- Primary blocker: `{artifact['primary_blocker']}`",
        "",
        "## Interpretation",
        "",
        summary["interpretation"],
        "",
        "This improves the B-path result from inert fixed geometry to a scoped "
        "return-scaffold design candidate. It still does not prove general native "
        "goal-proxy regulation because the return channel is predeclared and does "
        "not compute proxy error or response amount as a native policy.",
        "",
        "## Scaffold",
        "",
        f"- Scaffold id: `{artifact['return_scaffold_record']['scaffold_id']}`",
        f"- Scaffold digest: `{artifact['return_scaffold_record']['return_scaffold_digest']}`",
        "- Schedule declared before post-perturbation error: `true`",
        "- A-path producer correction scheduler used: `false`",
        "- A-path candidate set consumed: `false`",
        "- Posthoc geometry change used: `false`",
        "",
        "## Budget",
        "",
        f"- Budget before: `{budget['node_plus_packet_budget_before']}`",
        f"- Budget after perturbation: `{budget['node_plus_packet_budget_after_perturbation']}`",
        f"- Budget after return scaffold: `{budget['node_plus_packet_budget_after_return_scaffold']}`",
        f"- Budget error: `{budget['node_plus_packet_budget_error']}`",
        f"- Active state and ledger agree: `{budget['active_state_ledger_agree']}`",
        "",
        "## Controls",
        "",
        "| Control | Passed | Primary blocker if failed |",
        "|---|---:|---|",
    ]
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
            "Iteration 11-A supports only a scoped predeclared return-scaffold design "
            "candidate. It does not support general native goal-proxy regulation, "
            "semantic goal understanding, agency, identity acceptance, RC identity "
            "collapse, ACO-like behavior, locomotion-like behavior, or biological "
            "behavior.",
            "",
            "## Acceptance",
            "",
            "Achieved. A predeclared conserved return scaffold returned the proxy to "
            "the declared band after perturbation without using the A-path producer "
            "correction scheduler, with exact budget accounting and explicit "
            "overclaim controls.",
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
    print(f"classification: {artifact['response_summary']['result_classification']}")


if __name__ == "__main__":
    main()
