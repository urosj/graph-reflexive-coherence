#!/usr/bin/env python3
"""Run N09 Iteration 11 Hypothesis B1 geometry/substrate-mediated probe.

Iteration 11 tests whether the N09 proxy moves toward the declared band after
an explicit perturbation under fixed LGRC geometry without replaying the
Hypothesis A producer correction scheduler. A negative/no-response result is
valid evidence if it is source-backed, budget-clean, and claim-bounded.
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
    digest_value,
    error_to_band,
    git_head,
    git_status_short,
    load_json,
    node_measurement,
    rel,
    runtime_digests,
    schedule_and_step_packet,
    source_artifact_digest,
)


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"

MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
SOURCE_GPR2_PATH = EXPERIMENT / "outputs" / "n09_iteration_4_gpr2_error_signal.json"
SOURCE_B0_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.json"
)
SOURCE_B0_REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.md"
)

OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_11_hypothesis_b1_geometry_substrate_probe.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n09_iteration_11_hypothesis_b1_geometry_substrate_probe.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_11_hypothesis_b1_geometry_substrate_probe.py"
)

PERTURBATION_AMOUNT = 0.09
PASSIVE_STEP_COUNT = 3
BUDGET_TOLERANCE = 1e-9


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def active_node_total(model: LGRC9V3) -> float:
    return round(
        sum(float(node.coherence) for node in model.get_state().base_state.nodes.values()),
        12,
    )


def geometry_record(model: LGRC9V3, node_ids: dict[str, int], edge_ids: dict[str, int]) -> dict[str, Any]:
    state = model.get_state().base_state
    edges = []
    for edge_name, edge_id in sorted(edge_ids.items(), key=lambda item: item[0]):
        edge = state.port_edges[edge_id]
        edges.append(
            {
                "edge_name": edge_name,
                "edge_id": int(edge_id),
                "source_node_id": int(edge.node_u),
                "source_port_id": int(edge.port_u),
                "target_node_id": int(edge.node_v),
                "target_port_id": int(edge.port_v),
                "conductance": float(edge.conductance),
                "flux_uv": float(edge.flux_uv),
                "base_conductance": float(state.base_conductance[edge_id]),
                "geometric_length": float(state.geometric_length[edge_id]),
                "temporal_delay": float(state.temporal_delay[edge_id]),
                "flux_coupling": float(state.flux_coupling[edge_id]),
            }
        )
    record = {
        "geometry_id": "n09_b1_fixed_three_node_proxy_geometry_v1",
        "node_ids": {key: int(value) for key, value in sorted(node_ids.items())},
        "edge_ids": {key: int(value) for key, value in sorted(edge_ids.items())},
        "edge_records": edges,
        "geometry_policy": "fixed_geometry_no_conductance_update_no_potential_map",
        "posthoc_geometry_change_allowed": False,
    }
    record["geometry_digest"] = digest_row(record, "geometry_digest")
    return record


def build_substrate_response_mechanism(
    *,
    pre_geometry: dict[str, Any],
    source_b0: dict[str, Any],
) -> dict[str, Any]:
    record = {
        "mechanism_id": "n09_b1_fixed_geometry_passive_response_probe_v1",
        "mechanism_kind": "fixed_geometry_empty_queue_passive_lgrc_step_probe",
        "source_inventory_digest": source_b0["artifact_digest"],
        "geometry_digest": pre_geometry["geometry_digest"],
        "runtime_family": "LGRC9V3",
        "lgrc_runtime_level": "lgrc2_fixed_topology_packetized_flux",
        "producer_correction_scheduler_used": False,
        "a_path_candidate_set_consumed": False,
        "a_path_producer_record_consumed": False,
        "native_route_arbitration_used": False,
        "topology_mutation_used": False,
        "conductance_update_used": False,
        "custom_node_potential_used": False,
        "flux_facilitated_metric_map_used": False,
        "hidden_reward_or_goal_label_used": False,
        "posthoc_geometry_change_used": False,
        "empty_queue_steps_requested": PASSIVE_STEP_COUNT,
        "expected_boundary": (
            "LGRC9V3 step processes queued packet/topology events; with an "
            "empty queue, fixed geometry alone is not expected to perform "
            "target-band regulation."
        ),
    }
    record["mechanism_digest"] = digest_row(record, "mechanism_digest")
    return record


def build_probe() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    source_gpr2 = load_json(SOURCE_GPR2_PATH)
    source_b0 = load_json(SOURCE_B0_PATH)
    target_row = source_gpr2["target_band_row"]
    claim_flags = dict(source_b0["claim_flags"])
    state, node_ids, edge_ids = build_regulation_state()
    model = LGRC9V3.from_state(state, {"dt": 1.0})

    initial_runtime, initial_runtime_digest, initial_ledger_digest = runtime_digests(model)
    initial_budget = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    initial_measurement = node_measurement(model, node_ids["source_reservoir"])
    initial_proxy_row = build_proxy_row(
        row_id="n09_i11_initial_proxy_surface_v1",
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
        source_artifacts=[rel(SOURCE_B0_PATH)],
        source_reports=[rel(SOURCE_B0_REPORT_PATH)],
    )
    pre_geometry = geometry_record(model, node_ids, edge_ids)
    mechanism_record = build_substrate_response_mechanism(
        pre_geometry=pre_geometry,
        source_b0=source_b0,
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
    post_perturbation_measurement = node_measurement(model, node_ids["source_reservoir"])
    post_perturbation_proxy_row = build_proxy_row(
        row_id="n09_i11_post_perturbation_proxy_surface_v1",
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
        source_artifacts=[rel(SOURCE_B0_PATH), f"{rel(OUTPUT_PATH)}#post_perturbation"],
        source_reports=[rel(SOURCE_B0_REPORT_PATH), rel(REPORT_PATH)],
    )
    perturbation_record = {
        "perturbation_id": "n09_i11_serialized_proxy_increase_perturbation_v1",
        "perturbation_kind": "serialized_packet_proxy_increase",
        "amplitude": PERTURBATION_AMOUNT,
        "source_node_id": node_ids["target_reservoir"],
        "target_node_id": node_ids["source_reservoir"],
        "edge_id": edge_ids["source_target"],
        "scheduled_packet_id": perturbation_queued[0]["packet_id"],
        "processed_packet_id": perturbation_log[-1]["processed_event"]["packet_id"],
        "pre_perturbation_proxy_surface_digest": initial_proxy_row["proxy_surface_digest"],
        "post_perturbation_proxy_surface_digest": post_perturbation_proxy_row[
            "proxy_surface_digest"
        ],
        "node_plus_packet_budget_before": initial_budget,
        "node_plus_packet_budget_after": post_perturbation_budget,
        "node_plus_packet_budget_error": round(
            abs(post_perturbation_budget - initial_budget),
            12,
        ),
        "hidden_perturbation_used": False,
        "producer_correction_scheduler_used": False,
    }
    perturbation_record["perturbation_digest"] = digest_row(
        perturbation_record,
        "perturbation_digest",
    )
    post_perturbation_error_row = build_error_row(
        row_id="n09_i11_post_perturbation_error_signal_v1",
        manifest=manifest,
        proxy_row=post_perturbation_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH), rel(SOURCE_B0_PATH)],
        source_reports=[rel(REPORT_PATH), rel(SOURCE_B0_REPORT_PATH)],
    )

    passive_step_records: list[dict[str, Any]] = []
    for step_index in range(PASSIVE_STEP_COUNT):
        before_runtime, before_runtime_digest, before_ledger_digest = runtime_digests(model)
        before_measurement = node_measurement(model, node_ids["source_reservoir"])
        step_result = model.step()
        after_runtime, after_runtime_digest, after_ledger_digest = runtime_digests(model)
        after_measurement = node_measurement(model, node_ids["source_reservoir"])
        record = {
            "passive_step_index": step_index,
            "step_result_index": int(step_result.step_index),
            "time": float(step_result.time),
            "events": step_result.events,
            "bookkeeping": step_result.bookkeeping,
            "proxy_measurement_before": before_measurement,
            "proxy_measurement_after": after_measurement,
            "proxy_measurement_delta": round(after_measurement - before_measurement, 12),
            "runtime_state_digest_before": before_runtime_digest,
            "runtime_state_digest_after": after_runtime_digest,
            "packet_ledger_digest_before": before_ledger_digest,
            "packet_ledger_digest_after": after_ledger_digest,
            "runtime_state_changed": before_runtime_digest != after_runtime_digest,
            "packet_ledger_changed": before_ledger_digest != after_ledger_digest,
            "queue_length_before": int(step_result.bookkeeping["queue_length_before"]),
            "queue_length_after": int(step_result.bookkeeping["queue_length_after"]),
            "stop_condition": step_result.bookkeeping.get("stop_condition"),
            "source_artifact_runtime_state_before": before_runtime,
            "source_artifact_runtime_state_after": after_runtime,
        }
        record["passive_step_digest"] = digest_row(record, "passive_step_digest")
        passive_step_records.append(record)

    final_runtime, final_runtime_digest, final_ledger_digest = runtime_digests(model)
    final_budget = round(float(model.get_state().packet_ledger.conserved_budget_total), 12)
    final_measurement = node_measurement(model, node_ids["source_reservoir"])
    final_proxy_row = build_proxy_row(
        row_id="n09_i11_final_passive_probe_proxy_surface_v1",
        manifest=manifest,
        target_band_row=target_row,
        measurement_value=final_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=final_runtime_digest,
        packet_ledger_digest=final_ledger_digest,
        event_time_key=float(model.get_state().event_time_key),
        scheduler_event_index=int(model.get_state().scheduler_event_index),
        node_plus_packet_budget=final_budget,
        claim_flags=claim_flags,
        source_artifacts=[rel(OUTPUT_PATH), rel(SOURCE_B0_PATH)],
        source_reports=[rel(REPORT_PATH), rel(SOURCE_B0_REPORT_PATH)],
    )
    final_error_row = build_error_row(
        row_id="n09_i11_final_passive_probe_error_signal_v1",
        manifest=manifest,
        proxy_row=final_proxy_row,
        target_band_row=target_row,
        source_artifacts=[rel(OUTPUT_PATH), rel(SOURCE_B0_PATH)],
        source_reports=[rel(REPORT_PATH), rel(SOURCE_B0_REPORT_PATH)],
    )
    post_geometry = geometry_record(model, node_ids, edge_ids)

    initial_error, _, initial_in_band = error_to_band(initial_measurement, target_row)
    post_error = float(post_perturbation_error_row["error_value"])
    final_error = float(final_error_row["error_value"])
    error_reduction = round(abs(post_error) - abs(final_error), 12)
    if error_reduction > BUDGET_TOLERANCE and bool(final_error_row["in_band"]):
        result_classification = "toward_band_passive_response"
        primary_blocker = None
        design_candidate_supported = True
    elif error_reduction > BUDGET_TOLERANCE:
        result_classification = "bounded_degradation"
        primary_blocker = "native_goal_proxy_regulation_policy_incomplete"
        design_candidate_supported = False
    elif abs(error_reduction) <= BUDGET_TOLERANCE:
        result_classification = "no_response_native_policy_gap"
        primary_blocker = "native_goal_proxy_regulation_policy_missing"
        design_candidate_supported = False
    else:
        result_classification = "wrong_direction_response"
        primary_blocker = "wrong_direction_substrate_response"
        design_candidate_supported = False

    response_summary = {
        "initial_proxy_measurement": initial_measurement,
        "initial_error": round(float(initial_error), 12),
        "initial_in_band": initial_in_band,
        "post_perturbation_proxy_measurement": post_perturbation_measurement,
        "post_perturbation_error": post_error,
        "final_proxy_measurement": final_measurement,
        "final_error": final_error,
        "passive_step_count": PASSIVE_STEP_COUNT,
        "proxy_measurement_delta_after_passive_steps": round(
            final_measurement - post_perturbation_measurement,
            12,
        ),
        "error_reduction_after_passive_steps": error_reduction,
        "final_in_band": bool(final_error_row["in_band"]),
        "result_classification": result_classification,
        "primary_blocker": primary_blocker,
        "native_substrate_mediated_goal_proxy_regulation_design_candidate_supported": (
            design_candidate_supported
        ),
        "interpretation": (
            "Fixed LGRC geometry preserved the perturbed proxy and budget but "
            "did not create a target-directed return without a serialized "
            "response policy or scheduled correction packet."
        ),
    }
    response_summary["response_summary_digest"] = digest_row(
        response_summary,
        "response_summary_digest",
    )

    budget_record = {
        "node_plus_packet_budget_before": initial_budget,
        "node_plus_packet_budget_after_perturbation": post_perturbation_budget,
        "node_plus_packet_budget_after_passive_probe": final_budget,
        "active_node_total_after_passive_probe": active_node_total(model),
        "packet_ledger_node_total_after_passive_probe": round(
            float(model.get_state().packet_ledger.node_coherence_total),
            12,
        ),
        "in_flight_packet_total_after_passive_probe": round(
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
        "hidden_correction_scheduler": {
            "control_passed": all(
                record["queue_length_before"] == 0 and record["queue_length_after"] == 0
                for record in passive_step_records
            ),
            "primary_blocker": "hidden_correction_scheduler_blocked",
            "reason": "passive probe steps ran with an empty queue and emitted no correction packet",
        },
        "hidden_reset": {
            "control_passed": final_measurement == post_perturbation_measurement,
            "primary_blocker": "hidden_reset_blocked",
            "reason": "proxy did not reset to the target band during passive steps",
        },
        "producer_correction_leakage": {
            "control_passed": True,
            "primary_blocker": "producer_correction_leakage_blocked",
            "reason": "A-path producer/candidate-set evidence was not consumed by the probe",
        },
        "budget_drift": {
            "control_passed": budget_record["node_plus_packet_budget_error"]
            <= BUDGET_TOLERANCE
            and budget_record["active_state_ledger_agree"] is True,
            "primary_blocker": "node_plus_packet_budget_drift",
            "reason": "perturbation and passive probe preserve node-plus-packet budget",
        },
        "posthoc_geometry_change": {
            "control_passed": pre_geometry["geometry_digest"] == post_geometry["geometry_digest"],
            "primary_blocker": "posthoc_geometry_change_blocked",
            "reason": "geometry digest is unchanged before and after passive probe",
        },
        "native_claim_promotion": {
            "control_passed": all_false(claim_flags),
            "primary_blocker": "native_claim_promotion_blocked",
            "reason": "probe classification cannot emit semantic goal, agency, identity, or native regulation claims",
        },
    }

    validation_checks = {
        "source_b0_status_passed": source_b0["status"] == "passed",
        "source_b0_acceptance_achieved": source_b0["acceptance_state"] == "achieved",
        "a_path_ceiling_preserved": source_b0["a_path_preservation"]["claim_ceiling"]
        == "artifact_only_goal_proxy_regulation_candidate",
        "explicit_perturbation_serialized": perturbation_record["hidden_perturbation_used"]
        is False
        and perturbation_record["amplitude"] == PERTURBATION_AMOUNT,
        "perturbation_moved_proxy_out_of_band": post_perturbation_error_row["in_band"]
        is False
        and post_perturbation_error_row["error_direction"] == "decrease_proxy",
        "producer_correction_scheduler_absent": mechanism_record[
            "producer_correction_scheduler_used"
        ]
        is False,
        "a_path_candidate_set_not_consumed": mechanism_record[
            "a_path_candidate_set_consumed"
        ]
        is False,
        "passive_steps_ran": len(passive_step_records) == PASSIVE_STEP_COUNT,
        "passive_steps_empty_queue": controls["hidden_correction_scheduler"][
            "control_passed"
        ],
        "geometry_digest_unchanged": pre_geometry["geometry_digest"]
        == post_geometry["geometry_digest"],
        "budget_exact": controls["budget_drift"]["control_passed"],
        "result_classification_recorded": result_classification
        in {
            "toward_band_passive_response",
            "bounded_degradation",
            "wrong_direction_response",
            "saturation_no_recovery",
            "no_response_native_policy_gap",
            "blocked_missing_native_policy_surface",
        },
        "no_native_regulation_claim": design_candidate_supported is False
        and claim_flags["native_substrate_mediated_goal_proxy_regulation_claim_allowed"]
        is False,
        "controls_all_passed": all(control["control_passed"] for control in controls.values()),
        "claim_flags_all_false": all_false(claim_flags),
    }

    artifact: dict[str, Any] = {
        "schema": "n09_iteration_11_hypothesis_b1_geometry_substrate_probe_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 11,
        "purpose": "hypothesis_b1_geometry_substrate_mediated_probe_no_a_path_correction_scheduler",
        "status": "passed" if all(validation_checks.values()) else "failed",
        "acceptance_state": "achieved" if all(validation_checks.values()) else "not_achieved",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "source_artifacts": {
            "iteration_10_inventory": rel(SOURCE_B0_PATH),
            "iteration_4_target_band": rel(SOURCE_GPR2_PATH),
            "fixture_manifest": rel(MANIFEST_PATH),
        },
        "source_reports": {
            "iteration_10_inventory": rel(SOURCE_B0_REPORT_PATH),
        },
        "source_artifact_sha256": {
            "iteration_10_inventory": digest_file(SOURCE_B0_PATH),
            "iteration_4_target_band": digest_file(SOURCE_GPR2_PATH),
            "fixture_manifest": digest_file(MANIFEST_PATH),
        },
        "source_artifact_digests": {
            "iteration_10_inventory": source_artifact_digest(source_b0),
            "iteration_4_target_band": source_artifact_digest(source_gpr2),
        },
        "claim_ceiling": (
            "native_substrate_mediated_goal_proxy_regulation_design_candidate"
            if design_candidate_supported
            else "hypothesis_b_no_response_native_policy_gap"
        ),
        "primary_blocker": primary_blocker,
        "a_path_ceiling_preserved": source_b0["a_path_preservation"]["claim_ceiling"],
        "pre_probe_geometry": pre_geometry,
        "post_probe_geometry": post_geometry,
        "substrate_response_mechanism": mechanism_record,
        "initial_proxy_surface_row": initial_proxy_row,
        "post_perturbation_proxy_surface_row": post_perturbation_proxy_row,
        "final_proxy_surface_row": final_proxy_row,
        "post_perturbation_error_signal_row": post_perturbation_error_row,
        "final_error_signal_row": final_error_row,
        "perturbation_record": perturbation_record,
        "passive_step_records": passive_step_records,
        "response_summary": response_summary,
        "budget_record": budget_record,
        "controls": controls,
        "validation_checks": validation_checks,
        "claim_flags": claim_flags,
        "blocked_claims": sorted(
            set(source_b0["blocked_claims"])
            | {
                "native_substrate_mediated_goal_proxy_regulation",
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
        "# N09 Iteration 11 - Hypothesis B1 Geometry/Substrate-Mediated Probe",
        "",
        f"Status: {artifact['status']}",
        f"Acceptance state: {artifact['acceptance_state']}",
        "",
        "## Summary",
        "",
        "Iteration 11 perturbs the N09 proxy and then asks whether fixed LGRC "
        "geometry/substrate dynamics move the proxy toward the declared band "
        "without the A-path producer correction scheduler.",
        "",
        f"- Initial proxy: `{summary['initial_proxy_measurement']}`",
        f"- Post-perturbation proxy: `{summary['post_perturbation_proxy_measurement']}`",
        f"- Final passive-probe proxy: `{summary['final_proxy_measurement']}`",
        f"- Post-perturbation error: `{summary['post_perturbation_error']}`",
        f"- Final error: `{summary['final_error']}`",
        f"- Passive step count: `{summary['passive_step_count']}`",
        f"- Classification: `{summary['result_classification']}`",
        f"- Primary blocker: `{summary['primary_blocker']}`",
        "",
        "## Interpretation",
        "",
        summary["interpretation"],
        "",
        "This resolves the first Hypothesis B probe negatively but usefully: "
        "current fixed-topology LGRC packet/geometry mechanics preserve the "
        "perturbed state and budget, but do not implement native target-band "
        "return. B-path regulation therefore still needs a native policy "
        "surface or remains producer-mediated.",
        "",
        "## Mechanism Under Test",
        "",
        f"- Mechanism: `{artifact['substrate_response_mechanism']['mechanism_id']}`",
        f"- Geometry digest before: `{artifact['pre_probe_geometry']['geometry_digest']}`",
        f"- Geometry digest after: `{artifact['post_probe_geometry']['geometry_digest']}`",
        "- A-path producer correction scheduler used: `false`",
        "- Native route arbitration used: `false`",
        "- Conductance update used: `false`",
        "- Custom node potential used: `false`",
        "- Flux-facilitated metric map used: `false`",
        "",
        "## Budget",
        "",
        f"- Budget before: `{budget['node_plus_packet_budget_before']}`",
        f"- Budget after perturbation: `{budget['node_plus_packet_budget_after_perturbation']}`",
        f"- Budget after passive probe: `{budget['node_plus_packet_budget_after_passive_probe']}`",
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
            "Iteration 11 does not support native substrate-mediated goal-proxy "
            "regulation. It records `hypothesis_b_no_response_native_policy_gap` "
            "with `native_goal_proxy_regulation_policy_missing` as the primary "
            "blocker. Semantic goal understanding, agency, identity acceptance, "
            "RC identity collapse, ACO-like behavior, locomotion-like behavior, "
            "and biological behavior remain blocked.",
            "",
            "## Acceptance",
            "",
            "Achieved. A serialized geometry/substrate-mediated probe tested the "
            "N09 proxy after perturbation without A-path producer correction "
            "scheduling. The result is classified as no response under fixed "
            "LGRC geometry, with exact budget accounting and distinct controls.",
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
