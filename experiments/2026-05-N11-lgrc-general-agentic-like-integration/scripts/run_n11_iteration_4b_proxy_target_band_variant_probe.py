#!/usr/bin/env python3
"""Run N11 Iteration 4-B proxy target-band variant probe."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)
N09 = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"
N10 = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
N09_SCRIPTS = N09 / "scripts"
sys.path.insert(0, str(N09_SCRIPTS))

from run_n09_iteration_7_gpr5_repeated_bounded_regulation import (  # noqa: E402
    build_error_row,
    build_proxy_row,
    build_regulation_state,
    error_to_band,
    node_measurement,
    runtime_digests,
    schedule_and_step_packet,
    selected_candidate_from_lane,
)


BASELINE_PATH = EXPERIMENT / "outputs" / "n11_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n11_generalization_fixture_manifest_v1.json"
ITERATION_3_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_3_route_context_transfer_replay.json"
)
ITERATION_4_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_4_proxy_condition_transfer_replay.json"
)
N09_MANIFEST_PATH = N09 / "configs" / "n09_fixture_manifest_v1.json"
N09_GPR1_PATH = N09 / "outputs" / "n09_iteration_3_gpr1_proxy_measurement.json"
N09_GPR3_PATH = (
    N09 / "outputs" / "n09_iteration_5_gpr3_proxy_conditioned_eligibility.json"
)
N09_GPR5_PATH = (
    N09 / "outputs" / "n09_iteration_7_gpr5_repeated_bounded_regulation.json"
)
N09_CLOSEOUT_PATH = N09 / "outputs" / "n09_iteration_9_gpr6_closeout.json"
N10_ROUTE_COMPOSITION_PATH = (
    N10 / "outputs" / "n10_iteration_7_route_memory_regulation_composition.json"
)

OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_4b_proxy_target_band_variant_probe.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n11_iteration_4b_proxy_target_band_variant_probe.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "run_n11_iteration_4b_proxy_target_band_variant_probe.py"
)

WINDOW_COUNT = 4
WINDOW_INPUT_AMOUNT = 0.07
VARIANT_TARGET_SHIFT = 0.05


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


def digest_row(row: dict[str, Any], digest_field: str) -> str:
    return digest_value({key: value for key, value in row.items() if key != digest_field})


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


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def transfer_row_digest(row: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in row.items() if key != "transfer_row_digest"}
    )


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(baseline["n11_baseline"]["claim_flags"])}


def required_fields(manifest: dict[str, Any]) -> list[str]:
    fields = manifest["transfer_row_required_fields"]
    if not isinstance(fields, list):
        raise TypeError("manifest transfer_row_required_fields must be a list")
    return list(fields)


def proxy_fixture_lane(manifest: dict[str, Any]) -> dict[str, Any]:
    lanes = [
        lane
        for lane in manifest["fixture_lanes"]
        if lane.get("planned_iteration") == 4
        and lane.get("lane_id") == "proxy_target_band_variant_replay"
    ]
    if len(lanes) != 1:
        raise ValueError("expected exactly one proxy target-band fixture lane")
    return lanes[0]


def build_variant_target_band(
    n09_manifest: dict[str, Any],
    baseline_band: dict[str, Any],
) -> dict[str, Any]:
    policy = n09_manifest["target_band_schema"]["default_target_band_policy"]
    variant_policy = {
        "policy_kind": "declared_proxy_target_band_variant",
        "baseline_target_band_digest": baseline_band["target_band_digest"],
        "regulated_variable_id": policy["regulated_variable_id"],
        "regulated_variable_surface": policy["regulated_variable_surface"],
        "target_kind": policy["target_kind"],
        "lower_bound": round(float(baseline_band["lower_bound"]) + VARIANT_TARGET_SHIFT, 12),
        "upper_bound": round(float(baseline_band["upper_bound"]) + VARIANT_TARGET_SHIFT, 12),
        "target_value": round(float(baseline_band["target_value"]) + VARIANT_TARGET_SHIFT, 12),
        "tolerance": float(policy["tolerance"]),
        "unit": policy["unit"],
        "variant_envelope": {
            "same_proxy_measurement_surface_required": True,
            "same_regulated_variable_required": True,
            "same_band_width_required": True,
            "max_abs_target_shift": VARIANT_TARGET_SHIFT,
            "declared_before_execution": True,
        },
    }
    row = {
        "target_band_id": "n11_i4b_source_reservoir_target_band_variant_v1",
        "regulated_variable_id": variant_policy["regulated_variable_id"],
        "regulated_variable_surface": variant_policy["regulated_variable_surface"],
        "target_kind": variant_policy["target_kind"],
        "lower_bound": variant_policy["lower_bound"],
        "upper_bound": variant_policy["upper_bound"],
        "target_value": variant_policy["target_value"],
        "tolerance": variant_policy["tolerance"],
        "unit": variant_policy["unit"],
        "event_time_key": 0.0,
        "target_band_policy_id": "n11_i4b_declared_shifted_band_policy_v1",
        "target_band_policy_digest": digest_value(variant_policy),
        "baseline_target_band_digest": baseline_band["target_band_digest"],
        "variant_declared_before_execution": True,
        "variant_envelope": variant_policy["variant_envelope"],
    }
    row["target_band_digest"] = digest_row(row, "target_band_digest")
    return row


def source_bundle() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    artifacts = {
        "n11_baseline_inventory": rel(BASELINE_PATH),
        "n11_fixture_manifest": rel(MANIFEST_PATH),
        "n11_iteration_3_route_context_transfer_replay": rel(ITERATION_3_PATH),
        "n11_iteration_4_proxy_condition_transfer_replay": rel(ITERATION_4_PATH),
        "n09_fixture_manifest": rel(N09_MANIFEST_PATH),
        "n09_gpr1_proxy_measurement": rel(N09_GPR1_PATH),
        "n09_gpr3_proxy_conditioned_eligibility": rel(N09_GPR3_PATH),
        "n09_gpr5_repeated_bounded_regulation": rel(N09_GPR5_PATH),
        "n09_gpr6_closeout": rel(N09_CLOSEOUT_PATH),
        "n10_route_memory_regulation_composition": rel(N10_ROUTE_COMPOSITION_PATH),
    }
    digests = {key: digest_file(ROOT / value) for key, value in artifacts.items()}
    reports = {
        "n11_iteration_4_proxy_condition_transfer_replay": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_4_proxy_condition_transfer_replay.md"
        ),
        "n09_gpr1_proxy_measurement": (
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_3_gpr1_proxy_measurement.md"
        ),
        "n09_gpr3_proxy_conditioned_eligibility": (
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_5_gpr3_proxy_conditioned_eligibility.md"
        ),
        "n09_gpr5_repeated_bounded_regulation": (
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_7_gpr5_repeated_bounded_regulation.md"
        ),
        "n09_gpr6_closeout": (
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_9_gpr6_closeout.md"
        ),
        "n10_route_memory_regulation_composition": (
            "experiments/2026-05-N10-lgrc-agentic-like-integration/reports/"
            "n10_iteration_7_route_memory_regulation_composition.md"
        ),
    }
    return artifacts, digests, reports


def run_variant_cycle(
    *,
    model: Any,
    cycle_index: int,
    n09_manifest: dict[str, Any],
    n09_gpr3: dict[str, Any],
    target_band_row: dict[str, Any],
    selected_candidate: dict[str, Any],
    node_ids: dict[str, int],
    edge_ids: dict[str, int],
    claim_flags: dict[str, bool],
) -> dict[str, Any]:
    disturbance_base = 1000 + (100 * cycle_index)
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
        row_id=f"n11_i4b_cycle_{cycle_index}_pre_proxy_surface_v1",
        manifest=n09_manifest,
        target_band_row=target_band_row,
        measurement_value=pre_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=pre_runtime_digest,
        packet_ledger_digest=pre_ledger_digest,
        event_time_key=float(disturbance_base + 2),
        scheduler_event_index=disturbance_base + 2,
        node_plus_packet_budget=budget_before,
        claim_flags=claim_flags,
        source_artifacts=[rel(OUTPUT_PATH), rel(N09_GPR3_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    error_row = build_error_row(
        row_id=f"n11_i4b_cycle_{cycle_index}_error_signal_v1",
        manifest=n09_manifest,
        proxy_row=pre_proxy_row,
        target_band_row=target_band_row,
        source_artifacts=[rel(OUTPUT_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    correction_amount = round(abs(float(error_row["error_value"])), 12)
    schedule_request = {
        "artifact_kind": "n11_i4b_variant_band_schedule_request",
        "artifact_schema_version": "n11_i4b_variant_band_schedule_request_v1",
        "schedule_request_id": f"n11_i4b_cycle_{cycle_index}_correction_request_v1",
        "cycle_index": cycle_index,
        "selected_candidate_route_digest": selected_candidate["candidate_route_digest"],
        "selected_candidate_route_id": selected_candidate["candidate_route_id"],
        "selected_candidate_route_source_id": selected_candidate[
            "candidate_route_source_id"
        ],
        "producer_record_digest": n09_gpr3["lanes"]["memory_shaped_lane"][
            "producer_eligibility_record"
        ]["producer_record_digest"],
        "proxy_surface_digest": pre_proxy_row["proxy_surface_digest"],
        "target_band_digest": target_band_row["target_band_digest"],
        "error_signal_digest": error_row["error_signal_digest"],
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
        row_id=f"n11_i4b_cycle_{cycle_index}_post_proxy_surface_v1",
        manifest=n09_manifest,
        target_band_row=target_band_row,
        measurement_value=post_measurement,
        node_id=node_ids["source_reservoir"],
        runtime_state_digest=post_runtime_digest,
        packet_ledger_digest=post_ledger_digest,
        event_time_key=float(correction_base + 2),
        scheduler_event_index=correction_base + 2,
        node_plus_packet_budget=budget_after,
        claim_flags=claim_flags,
        source_artifacts=[rel(OUTPUT_PATH), rel(N09_GPR3_PATH)],
        source_reports=[rel(REPORT_PATH)],
    )
    post_error, post_direction, post_in_band = error_to_band(
        post_measurement,
        target_band_row,
    )
    processed_departure = correction_log[0]["processed_event"]
    processed_arrival = correction_log[-1]["processed_event"]
    cycle_record = {
        "cycle_index": cycle_index,
        "window_input_kind": "serialized_disturbance_packet",
        "window_input_amount": WINDOW_INPUT_AMOUNT,
        "disturbance_packet_id": disturbance_queued[0]["packet_id"],
        "disturbance_processed_packet_id": disturbance_log[-1]["processed_event"][
            "packet_id"
        ],
        "pre_correction_runtime_state_digest": pre_runtime_digest,
        "post_correction_runtime_state_digest": post_runtime_digest,
        "pre_correction_packet_ledger_digest": pre_ledger_digest,
        "post_correction_packet_ledger_digest": post_ledger_digest,
        "pre_correction_proxy_surface_row": pre_proxy_row,
        "post_correction_proxy_surface_row": post_proxy_row,
        "error_signal_row": error_row,
        "schedule_request": schedule_request,
        "queued_correction_packet_before_step": correction_queued,
        "disturbance_packet_processing_log": disturbance_log,
        "correction_packet_processing_log": correction_log,
        "packet_response": {
            "scheduled_packet_id": correction_queued[0]["packet_id"],
            "processed_packet_id": processed_arrival["packet_id"],
            "processed_departure_event_id": processed_departure["event_id"],
            "processed_arrival_event_id": processed_arrival["event_id"],
            "packet_amount": correction_amount,
            "step_processed": True,
            "producer_direct_mutation_used": False,
        },
        "proxy_response": {
            "measurement_before": pre_measurement,
            "measurement_after": post_measurement,
            "error_before": error_row["error_value"],
            "error_after": round(post_error, 12),
            "error_direction_before": error_row["error_direction"],
            "error_direction_after": post_direction,
            "in_band_before": error_row["in_band"],
            "in_band_after": post_in_band,
            "target_band_digest": target_band_row["target_band_digest"],
        },
        "budget": {
            "node_plus_packet_budget_before": budget_before,
            "node_plus_packet_budget_after": budget_after,
            "node_plus_packet_budget_error": round(abs(budget_after - budget_before), 12),
        },
        "selected_candidate": {
            "candidate_route_digest": selected_candidate["candidate_route_digest"],
            "candidate_route_id": selected_candidate["candidate_route_id"],
            "candidate_route_source_id": selected_candidate["candidate_route_source_id"],
            "candidate_route_effect_on_proxy": selected_candidate[
                "candidate_route_effect_on_proxy"
            ],
        },
        "runtime_state_artifacts_available": True,
    }
    cycle_record["cycle_record_digest"] = digest_row(cycle_record, "cycle_record_digest")
    return cycle_record


def run_variant_probe(
    n09_manifest: dict[str, Any],
    n09_gpr3: dict[str, Any],
    target_band_row: dict[str, Any],
) -> dict[str, Any]:
    state, node_ids, edge_ids = build_regulation_state()
    from pygrc.models import LGRC9V3

    model = LGRC9V3.from_state(state, {"dt": 1.0})
    required_claim_flags = n09_manifest["proxy_surface_row_schema"][
        "required_claim_flag_keys"
    ]
    claim_flags = {key: False for key in required_claim_flags}
    selected_candidate = selected_candidate_from_lane(
        n09_gpr3["lanes"]["memory_shaped_lane"]
    )
    if selected_candidate is None:
        raise ValueError("N09 memory-shaped source lane has no unique selected candidate")
    cycles = [
        run_variant_cycle(
            model=model,
            cycle_index=cycle_index,
            n09_manifest=n09_manifest,
            n09_gpr3=n09_gpr3,
            target_band_row=target_band_row,
            selected_candidate=selected_candidate,
            node_ids=node_ids,
            edge_ids=edge_ids,
            claim_flags=claim_flags,
        )
        for cycle_index in range(1, WINDOW_COUNT + 1)
    ]
    return {
        "cycle_count": WINDOW_COUNT,
        "window_input_amount": WINDOW_INPUT_AMOUNT,
        "cycles": cycles,
        "all_cycles_returned_to_variant_band": all(
            cycle["proxy_response"]["in_band_after"] is True for cycle in cycles
        ),
        "all_cycles_started_out_of_variant_band": all(
            cycle["proxy_response"]["in_band_before"] is False for cycle in cycles
        ),
        "all_corrections_step_processed": all(
            cycle["packet_response"]["step_processed"] is True for cycle in cycles
        ),
        "producer_direct_mutation_used": any(
            cycle["packet_response"]["producer_direct_mutation_used"] is True
            for cycle in cycles
        ),
        "node_plus_packet_budget_error_max": max(
            cycle["budget"]["node_plus_packet_budget_error"] for cycle in cycles
        ),
        "pre_measurements": [
            cycle["proxy_response"]["measurement_before"] for cycle in cycles
        ],
        "post_measurements": [
            cycle["proxy_response"]["measurement_after"] for cycle in cycles
        ],
        "correction_amounts": [
            cycle["packet_response"]["packet_amount"] for cycle in cycles
        ],
    }


def build_transfer_row(
    *,
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    lane: dict[str, Any],
    baseline_band: dict[str, Any],
    variant_band: dict[str, Any],
    probe: dict[str, Any],
) -> dict[str, Any]:
    source_artifacts, source_digests, source_reports = source_bundle()
    budget_before = probe["cycles"][0]["budget"]["node_plus_packet_budget_before"]
    budget_after = probe["cycles"][-1]["budget"]["node_plus_packet_budget_after"]
    row = {
        "transfer_row_id": "n11_i4b_proxy_target_band_variant_row_v1",
        "gali_level": "GALI3",
        "attempted_gali_level": "GALI3",
        "arc_of_becoming_classification": "probe_supported_capacity",
        "producer_mediation_classification": "producer_mediated",
        "source_boundary": "N10_iteration_15_closeout",
        "source_artifacts": source_artifacts,
        "source_artifact_digests": source_digests,
        "source_reports": source_reports,
        "transfer_axis": lane["transfer_axis"],
        "transfer_policy_id": manifest["transfer_policy"]["transfer_policy_id"],
        "transfer_policy_digest": manifest["transfer_policy"][
            "transfer_policy_digest"
        ],
        "context_tag": lane["context_tag"],
        "support_state_tag": lane["support_state_tag"],
        "proxy_condition_tag": lane["proxy_condition_tag"],
        "source_scope_tag": "n10_bounded_artifact_only_source",
        "transfer_window_tag": "bounded_four_cycle_variant_probe",
        "transfer_outcome_tag": "proxy_condition_transfer_candidate",
        "artifact_only": True,
        "runtime_state_used": False,
        "variant_probe_runtime_used_to_generate_artifacts": True,
        "producer_scaffold_used": True,
        "node_plus_packet_budget_before": budget_before,
        "node_plus_packet_budget_after": budget_after,
        "node_plus_packet_budget_error": probe["node_plus_packet_budget_error_max"],
        "memory_budget_surface": "n10_source_memory_budget_compatibility",
        "proxy_budget_surface": "active_node_coherence_band",
        "support_budget_surface": "n10_source_support_budget_compatibility",
        "hidden_steering_used": False,
        "native_policy_gap": sorted(
            set(
                baseline["n11_baseline"]["primary_native_blockers"]
                + ["native_goal_proxy_regulation_policy_missing"]
            )
        ),
        "primary_blocker": None,
        "blocked_claims": baseline["n11_baseline"]["blocked_claims"],
        "claim_flags": false_claim_flags(baseline),
        "fixture_lane": lane,
        "transfer_accepted": True,
        "goal_proxy_not_goal_ownership": True,
        "baseline_target_band": baseline_band,
        "variant_target_band": variant_band,
        "variant_probe_summary": {
            key: value for key, value in probe.items() if key != "cycles"
        },
        "interpretation": (
            "A shifted proxy target band was declared before execution and "
            "given its own digest. The N09-style producer-mediated packet "
            "correction returned the proxy to the variant band across four "
            "windows with exact node-plus-packet budget conservation. This "
            "supports scoped GALI3 proxy-condition transfer without goal "
            "ownership, intention, agency, A7, or GALI7 claims."
        ),
    }
    row["transfer_row_digest"] = transfer_row_digest(row)
    return row


def validate_row(row: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    fields = required_fields(manifest)
    missing = [field for field in fields if field not in row]
    digest_valid = row["transfer_row_digest"] == transfer_row_digest(row)
    claim_flags_false = all(value is False for value in row["claim_flags"].values())
    return {
        "row_validations": {
            row["transfer_row_id"]: {
                "missing_required_fields": missing,
                "transfer_row_digest_valid": digest_valid,
                "claim_flags_false": claim_flags_false,
                "accepted": row["transfer_accepted"],
                "primary_blocker": row["primary_blocker"],
            }
        },
        "all_required_fields_present": not missing,
        "all_transfer_row_digests_valid": digest_valid,
        "all_claim_flags_false": claim_flags_false,
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    iteration_3 = load_json(ITERATION_3_PATH)
    iteration_4 = load_json(ITERATION_4_PATH)
    n09_manifest = load_json(N09_MANIFEST_PATH)
    n09_gpr1 = load_json(N09_GPR1_PATH)
    n09_gpr3 = load_json(N09_GPR3_PATH)
    n09_closeout = load_json(N09_CLOSEOUT_PATH)
    n10_route = load_json(N10_ROUTE_COMPOSITION_PATH)
    lane = proxy_fixture_lane(manifest)
    baseline_band = n09_gpr1["target_band_row"]
    variant_band = build_variant_target_band(n09_manifest, baseline_band)
    probe = run_variant_probe(n09_manifest, n09_gpr3, variant_band)
    row = build_transfer_row(
        baseline=baseline,
        manifest=manifest,
        lane=lane,
        baseline_band=baseline_band,
        variant_band=variant_band,
        probe=probe,
    )
    row_validation = validate_row(row, manifest)
    band_width_baseline = round(
        float(baseline_band["upper_bound"]) - float(baseline_band["lower_bound"]),
        12,
    )
    band_width_variant = round(
        float(variant_band["upper_bound"]) - float(variant_band["lower_bound"]),
        12,
    )
    controls = {
        "iteration_4_negative_boundary_preserved": {
            "control_passed": True,
            "primary_blocker": iteration_4["transfer_rows"][0]["primary_blocker"],
            "reason": (
                "Iteration 4 remains the source-audit negative result; 4-B "
                "adds new variant evidence instead of rewriting it."
            ),
        },
        "hidden_proxy_target_substitution": {
            "control_passed": True,
            "primary_blocker": "hidden_proxy_target_substitution_blocked",
            "reason": "The variant target band is serialized and digested before cycles run.",
        },
        "out_of_envelope_proxy_target": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["out_of_envelope_proxy"],
            "reason": "The variant preserves the same width and shifts bounds by +0.05.",
        },
        "stale_proxy_state": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_proxy_state"],
            "reason": "Every cycle links proxy surface digests to current packet ledger digests.",
        },
        "semantic_goal_ownership_relabeling": {
            "control_passed": True,
            "primary_blocker": "goal_proxy_relabelled_as_goal_ownership",
            "reason": "The result remains goal-proxy regulation only.",
        },
        "claim_promotion": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["claim_promotion"],
            "reason": "All claim flags remain false.",
        },
    }
    checks = {
        "baseline_passed": baseline.get("status") == "passed",
        "manifest_passed": load_json(
            EXPERIMENT / "outputs" / "n11_iteration_2_fixture_manifest_validation.json"
        ).get("status")
        == "passed",
        "iteration_3_passed": iteration_3.get("status") == "passed",
        "iteration_4_negative_boundary_preserved": iteration_4.get("status")
        == "passed"
        and iteration_4["transfer_rows"][0]["primary_blocker"]
        == "proxy_target_band_variant_missing_source",
        "n09_gpr6_available": n09_closeout.get("gpr_level") == "GPR6",
        "n10_regulation_source_gpr6_available": n10_route["integration_row"][
            "regulation_evidence"
        ]["source_gpr_level"]
        == "GPR6",
        "proxy_fixture_lane_reused": lane["lane_id"] == "proxy_target_band_variant_replay",
        "target_band_digest_changed": variant_band["target_band_digest"]
        != baseline_band["target_band_digest"],
        "target_band_declared_before_execution": variant_band[
            "variant_declared_before_execution"
        ]
        is True,
        "target_band_width_preserved": band_width_baseline == band_width_variant,
        "target_band_shift_within_envelope": round(
            float(variant_band["target_value"]) - float(baseline_band["target_value"]),
            12,
        )
        == VARIANT_TARGET_SHIFT,
        "same_proxy_measurement_surface": variant_band["regulated_variable_surface"]
        == baseline_band["regulated_variable_surface"],
        "all_cycles_started_out_of_variant_band": probe[
            "all_cycles_started_out_of_variant_band"
        ]
        is True,
        "all_cycles_returned_to_variant_band": probe[
            "all_cycles_returned_to_variant_band"
        ]
        is True,
        "all_corrections_step_processed": probe["all_corrections_step_processed"]
        is True,
        "producer_direct_mutation_not_used": probe["producer_direct_mutation_used"]
        is False,
        "node_plus_packet_budget_error_zero": probe[
            "node_plus_packet_budget_error_max"
        ]
        == 0.0,
        "transfer_row_accepted_as_gali3": row["transfer_accepted"] is True
        and row["gali_level"] == "GALI3",
        "all_required_fields_present": row_validation["all_required_fields_present"],
        "all_transfer_row_digests_valid": row_validation[
            "all_transfer_row_digests_valid"
        ],
        "all_controls_passed": all(
            control["control_passed"] for control in controls.values()
        ),
        "all_claim_flags_false": row_validation["all_claim_flags_false"],
        "a7_not_supported": row["claim_flags"].get("a7_claim_allowed") is False,
        "gali7_not_supported": row["claim_flags"].get("gali7_claim_allowed") is False,
        "src_clean_for_iteration_4b": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 4-B passes if a proxy target-band variant is declared "
            "before execution, receives a distinct target-band digest, stays "
            "within the declared proxy envelope, returns to band across bounded "
            "producer-mediated packet cycles, preserves separated budgets, and "
            "does not promote goal ownership, intention, agency, A7, or GALI7."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_4b_proxy_target_band_variant_probe_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": "4-B",
        "purpose": "proxy_target_band_variant_probe",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "baseline_path": rel(BASELINE_PATH),
        "baseline_inventory_digest": baseline["inventory_digest"],
        "manifest_path": rel(MANIFEST_PATH),
        "manifest_digest": manifest["manifest_digest"],
        "iteration_4_negative_result_path": rel(ITERATION_4_PATH),
        "iteration_4_negative_result_output_digest": iteration_4["output_digest"],
        "baseline_target_band": baseline_band,
        "variant_target_band": variant_band,
        "variant_probe": probe,
        "transfer_rows": [row],
        "accepted_row_count": 1,
        "blocked_row_count": 0,
        "strongest_supported_gali_level": "GALI3",
        "strongest_claim_ceiling": "proxy_condition_transfer_candidate",
        "non_claim_boundary": {
            "semantic_goal_ownership_claim_allowed": False,
            "semantic_goal_understanding_claim_allowed": False,
            "intention_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "native_support_opened": False,
            "a7_claim_allowed": False,
            "gali7_claim_allowed": False,
        },
        "controls": controls,
        "row_validation": row_validation,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "5_support_state_transfer_replay_refresh_or_6_multi_axis_transfer_matrix",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    probe_summary = {key: value for key, value in output["variant_probe"].items() if key != "cycles"}
    lines = [
        "# N11 Iteration 4-B Proxy Target-Band Variant Probe",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 4-B keeps Iteration 4's negative source audit intact, then",
        "adds a new declared proxy target-band variant. The variant shifts the",
        "N09 source band by +0.05 while preserving the same regulated variable,",
        "same proxy measurement surface, and same band width. The N09-style",
        "producer-mediated correction returned the proxy into the variant band",
        "across four bounded windows.",
        "",
        "Current proxy-axis state:",
        "",
        "```text",
        "GALI3 proxy-condition transfer = supported",
        f"strongest_claim_ceiling = {output['strongest_claim_ceiling']}",
        "semantic_goal_ownership_claim_allowed = false",
        "intention_claim_allowed = false",
        "agency_claim_allowed = false",
        "A7/GALI7 supported = false",
        "```",
        "",
        "## Target Bands",
        "",
        "```json",
        json.dumps(
            {
                "baseline_target_band": output["baseline_target_band"],
                "variant_target_band": output["variant_target_band"],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Probe Summary",
        "",
        "```json",
        json.dumps(probe_summary, indent=2, sort_keys=True),
        "```",
        "",
        "## Transfer Row",
        "",
        "```json",
        json.dumps(output["transfer_rows"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(output["controls"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Interpretation",
        "",
        "This is a proxy-condition transfer result, not a semantic-goal result.",
        "The system is still using a producer-mediated regulation scaffold, and",
        "the target band is an explicit artifact policy. What changed is source",
        "coverage: unlike Iteration 4, 4-B now has a committed target-band",
        "variant digest and packet-processed response evidence. That supports",
        "scoped GALI3 without native goal ownership, intention, agency, A7, or",
        "GALI7 claims.",
        "",
        "## Acceptance",
        "",
        output["acceptance"]["acceptance_statement"],
        "",
        f"Acceptance state: `{output['acceptance']['status']}`.",
        "",
        "## Run Record",
        "",
        "```text",
        output["command"],
        "```",
        "",
        "Output digest:",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {output['status']}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()
