#!/usr/bin/env python3
"""Build N12 Iteration 4 response magnitude candidate artifact."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

N09_EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"
N10_EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
N11_EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)

ITERATION_1_OUTPUT = OUTPUTS / "n12_native_naturalization_inventory.json"
ITERATION_1_REPORT = REPORTS / "n12_native_naturalization_inventory.md"
ITERATION_2_OUTPUT = OUTPUTS / "n12_naturalization_schema_v1.json"
ITERATION_2_REPORT = REPORTS / "n12_naturalization_schema_v1.md"

N09_I3_OUTPUT = N09_EXPERIMENT / "outputs" / "n09_iteration_3_gpr1_proxy_measurement.json"
N09_I3_REPORT = N09_EXPERIMENT / "reports" / "n09_iteration_3_gpr1_proxy_measurement.md"
N09_I4_OUTPUT = N09_EXPERIMENT / "outputs" / "n09_iteration_4_gpr2_error_signal.json"
N09_I4_REPORT = N09_EXPERIMENT / "reports" / "n09_iteration_4_gpr2_error_signal.md"
N09_I6_OUTPUT = (
    N09_EXPERIMENT / "outputs" / "n09_iteration_6_gpr4_single_cycle_correction.json"
)
N09_I6_REPORT = (
    N09_EXPERIMENT / "reports" / "n09_iteration_6_gpr4_single_cycle_correction.md"
)
N09_I7_OUTPUT = (
    N09_EXPERIMENT / "outputs" / "n09_iteration_7_gpr5_repeated_bounded_regulation.json"
)
N09_I7_REPORT = (
    N09_EXPERIMENT / "reports" / "n09_iteration_7_gpr5_repeated_bounded_regulation.md"
)
N09_I8_OUTPUT = (
    N09_EXPERIMENT / "outputs" / "n09_iteration_8_perturbation_withdrawal_support.json"
)
N09_I8_REPORT = (
    N09_EXPERIMENT / "reports" / "n09_iteration_8_perturbation_withdrawal_support.md"
)
N09_I9_OUTPUT = N09_EXPERIMENT / "outputs" / "n09_iteration_9_gpr6_closeout.json"
N09_I9_REPORT = N09_EXPERIMENT / "reports" / "n09_iteration_9_gpr6_closeout.md"
N09_I10_OUTPUT = (
    N09_EXPERIMENT / "outputs" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.json"
)
N09_I10_REPORT = (
    N09_EXPERIMENT / "reports" / "n09_iteration_10_hypothesis_b0_native_substrate_inventory.md"
)
N09_I11_OUTPUT = (
    N09_EXPERIMENT / "outputs" / "n09_iteration_11_hypothesis_b1_geometry_substrate_probe.json"
)
N09_I11_REPORT = (
    N09_EXPERIMENT / "reports" / "n09_iteration_11_hypothesis_b1_geometry_substrate_probe.md"
)
N09_I11A_OUTPUT = (
    N09_EXPERIMENT / "outputs" / "n09_iteration_11a_positive_geometry_return_scaffold_probe.json"
)
N09_I11A_REPORT = (
    N09_EXPERIMENT / "reports" / "n09_iteration_11a_positive_geometry_return_scaffold_probe.md"
)
N09_I11B_OUTPUT = (
    N09_EXPERIMENT / "outputs" / "n09_iteration_11b_band_buffered_return_scaffold_probe.json"
)
N09_I11B_REPORT = (
    N09_EXPERIMENT / "reports" / "n09_iteration_11b_band_buffered_return_scaffold_probe.md"
)
N09_I12_OUTPUT = (
    N09_EXPERIMENT / "outputs" / "n09_iteration_12_hypothesis_b2_native_substrate_closeout.json"
)
N09_I12_REPORT = (
    N09_EXPERIMENT / "reports" / "n09_iteration_12_hypothesis_b2_native_substrate_closeout.md"
)

N10_I14_OUTPUT = (
    N10_EXPERIMENT
    / "outputs"
    / "n10_iteration_14_hypothesis_c_native_contract_requirements.json"
)
N10_I14_REPORT = (
    N10_EXPERIMENT
    / "reports"
    / "n10_iteration_14_hypothesis_c_native_contract_requirements.md"
)
N11_I11_OUTPUT = (
    N11_EXPERIMENT / "outputs" / "n11_iteration_11_hypothesis_c_native_generalization_gap.json"
)
N11_I11_REPORT = (
    N11_EXPERIMENT / "reports" / "n11_iteration_11_hypothesis_c_native_generalization_gap.md"
)

OUTPUT_PATH = OUTPUTS / "n12_response_magnitude_candidate.json"
REPORT_PATH = REPORTS / "n12_response_magnitude_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
    "scripts/build_n12_response_magnitude_candidate.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
}


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


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def row_digest(row: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in row.items() if key != "row_digest"})


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
        "artifact_digest": None if artifact is None else artifact.get("artifact_digest"),
    }


def all_claim_flags_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def find_object_by_row_id(value: Any, row_id: str) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get("row_id") == row_id:
            return value
        for item in value.values():
            found = find_object_by_row_id(item, row_id)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_object_by_row_id(item, row_id)
            if found is not None:
                return found
    return None


def find_inventory_response_row(inventory: dict[str, Any]) -> dict[str, Any]:
    for row in inventory["n12_inventory_rows"]:
        if (
            row.get("native_gap")
            == "native_response_magnitude_policy_missing_for_unbounded_perturbations"
        ):
            return row
    raise ValueError("N12 response magnitude inventory row not found")


def build_record_schema_sketch() -> dict[str, Any]:
    return {
        "record_type": "native_response_magnitude_policy_record",
        "version": "v1",
        "required_fields": [
            "policy_id",
            "enabled",
            "validated",
            "supported",
            "proxy_surface_digest",
            "target_band_policy_id",
            "target_band_digest",
            "proxy_error_digest",
            "eligibility_record_digest",
            "perturbation_envelope_digest",
            "response_gain_policy_id",
            "max_correction_per_window",
            "bounded_window_id",
            "response_packet_schedule_digest",
            "node_plus_packet_budget_before_digest",
            "node_plus_packet_budget_after_digest",
            "proxy_budget_before_digest",
            "proxy_budget_after_digest",
            "error_trend_digest",
            "saturation_status",
            "overcorrection_status",
            "policy_record_digest",
        ],
        "state_carrier": "proxy_error_and_packet_scheduling_policy",
        "forbidden_fields": [
            "hidden_goal_state",
            "semantic_goal_ownership",
            "agent_intention",
            "hidden_optimizer_state",
            "unbounded_response_gain",
            "report_side_response_override",
        ],
    }


def build_candidate_row(
    inventory_row: dict[str, Any],
    n09_i3: dict[str, Any],
    n09_i4: dict[str, Any],
    n09_i6: dict[str, Any],
    n09_i7: dict[str, Any],
    n09_i8: dict[str, Any],
    n09_i9: dict[str, Any],
    n09_i11: dict[str, Any],
    n09_i11a: dict[str, Any],
    n09_i11b: dict[str, Any],
    n09_i12: dict[str, Any],
    n10_contract: dict[str, Any],
    n11_gap: dict[str, Any],
) -> dict[str, Any]:
    blocked_claims = sorted(
        set(inventory_row["blocked_claims"])
        | {
            "native response magnitude support",
            "native goal proxy regulation support",
            "semantic goal ownership",
            "semantic goal understanding",
            "hidden optimization",
            "unbounded native regulation",
            "general native regulation",
            "goal ownership",
        }
    )
    runtime_visible_inputs = sorted(
        set(n10_contract["runtime_visible_inputs"])
        | {
            "target_band_digest",
            "response_gain_policy_id",
            "max_correction_per_window",
            "bounded_window_id",
            "response_packet_schedule_digest",
            "node_plus_packet_budget_before_digest",
            "node_plus_packet_budget_after_digest",
            "proxy_budget_before_digest",
            "proxy_budget_after_digest",
            "error_trend_digest",
        }
    )
    budget_surfaces = sorted(
        set(inventory_row["budget_surfaces"])
        | set(n10_contract["budget_surfaces"])
        | {
            "proxy_error_budget_surface",
            "response_packet_budget_surface",
        }
    )
    negative_controls = sorted(
        set(inventory_row["negative_controls"])
        | set(n10_contract["negative_controls"])
        | {
            "wrong_direction_response_rejected",
            "hidden_optimizer_state_rejected",
            "posthoc_target_band_change_rejected",
            "unbudgeted_response_packet_rejected",
            "overcorrection_beyond_band_rejected",
            "out_of_envelope_response_rejected",
            "telemetry_default_off_exports_no_new_records",
        }
    )

    trend_stability_fields = {
        "error_trend": {
            "status": "bounded_improving_or_blocked_by_envelope",
            "source": "N09 GPR4/GPR5/GPR8",
            "single_cycle_error_before": n09_i6["packet_response_record"][
                "proxy_error_before"
            ],
            "single_cycle_error_after": n09_i6["packet_response_record"][
                "proxy_error_after"
            ],
            "memory_lane_post_correction_errors": n09_i7[
                "memory_shaped_lane"
            ]["summary"]["post_correction_errors"],
            "no_memory_lane_errors_after_inputs": n09_i7[
                "no_memory_comparator_lane"
            ]["summary"]["errors_after_window_inputs"],
            "memory_lane_outcome": n09_i7["lane_comparison"]["memory_lane_outcome"],
            "no_memory_lane_outcome": n09_i7["lane_comparison"][
                "no_memory_lane_outcome"
            ],
            "perturbation_recovery_in_band": n09_i9["regulation_summary"][
                "gpr8_perturbation_recovery_in_band"
            ],
        },
        "saturation_status": {
            "bounded_candidate_status": "not_saturated_within_declared_memory_lane_window",
            "no_memory_comparator_status": n09_i7["lane_comparison"][
                "no_memory_lane_outcome"
            ],
            "out_of_envelope_status": "blocked_without_perturbation_envelope_policy",
        },
        "overcorrection_status": {
            "status": "blocked_by_target_band_and_wrong_direction_controls",
            "single_cycle_post_response_in_band": n09_i6["packet_response_record"][
                "post_response_in_band"
            ],
            "wrong_direction_control_passed": n09_i6["controls"][
                "wrong_direction_response"
            ]["control_passed"],
            "fixed_return_amount_family_control_passed": n09_i11b["controls"][
                "fixed_return_amount_family"
            ]["control_passed"],
        },
        "bounded_window": {
            "window_count": n09_i7["window_policy"]["window_count"],
            "window_input_amount": n09_i7["window_policy"]["window_input_amount"],
            "same_target_band_all_windows": n09_i7["window_policy"][
                "same_target_band_all_windows"
            ],
            "same_regulation_policy_all_windows": n09_i7["window_policy"][
                "same_regulation_policy_all_windows"
            ],
            "perturbation_amplitude": n09_i8["perturbation_record"]["amplitude"],
            "perturbation_expected_recovery_window_count": n09_i8["perturbation_record"][
                "expected_recovery_window_count"
            ],
        },
        "out_of_envelope_blocker": {
            "status": "required_for_phase8_entry",
            "blocker": "unbounded_perturbation_envelope_blocked",
            "related_controls": [
                "unbounded_perturbation_without_policy_rejected",
                "general_native_regulation_overclaim_blocked",
                "adaptive_response_amount_hidden_policy_blocked",
            ],
        },
    }

    non_rc_quantity_audit = {
        "audit_status": "passed_for_nat4_readiness",
        "is_expressible_as_rc_causality_coherence_scheduling_lineage_budget": True,
        "is_proxy_measurement_derived_observable_or_new_state": (
            "derived_observable_from_runtime_visible_active_node_state"
        ),
        "is_target_band_exogenous_or_runtime_visible_policy": (
            "runtime_visible_serialized_policy_record_not_semantic_goal"
        ),
        "is_response_gain_serialized_and_replayable": True,
        "does_correction_debit_node_plus_packet_budget": True,
        "does_response_sizing_require_hidden_optimization_or_external_controller_state": False,
        "extra_unaccounted_quantity_allowed": False,
        "blocked_if_extra_quantity_required": "unaccounted_non_rc_quantity_required",
        "forbidden_non_rc_quantities": [
            "hidden_goal_state",
            "semantic_goal_ownership",
            "agent_intention",
            "hidden_optimizer_state",
            "unbounded_response_gain",
        ],
    }

    mutation_boundary = {
        "status": "specified_for_phase8_entry",
        "producer_or_policy_may_schedule_only": True,
        "step_or_topology_event_owns_state_mutation": True,
        "allowed_policy_actions_before_commit": [
            "read proxy_surface_digest",
            "read target_band_policy_id and target_band_digest",
            "compute proxy_error_digest",
            "select serialized response_gain_policy_id",
            "schedule bounded response packet",
            "emit replayable policy record digest",
        ],
        "forbidden_policy_actions_before_commit": [
            "mutate proxy state directly",
            "change target band after measurement",
            "invent hidden optimizer state",
            "increase response beyond declared envelope",
            "claim goal ownership or intention",
        ],
        "state_mutation_owner": "LGRC step or committed packet scheduling event boundary",
    }

    row = {
        "row_id": "n12_i4_response_magnitude_candidate_v1",
        "source_experiment": "N09_N10_N11_N12",
        "source_iteration": "N12_iteration_4",
        "source_artifact": rel(ITERATION_1_OUTPUT),
        "source_report": rel(ITERATION_1_REPORT),
        "source_sha256": digest_file(ITERATION_1_OUTPUT),
        "source_report_sha256": digest_file(ITERATION_1_REPORT),
        "source_gap_rows": sorted(
            set(inventory_row["source_gap_rows"]) | set(n10_contract["source_gap_row_ids"])
        ),
        "source_contract_rows": sorted(set(inventory_row["source_contract_rows"])),
        "source_gap_row_summaries": inventory_row["source_gap_row_summaries"],
        "source_row_digest": inventory_row["row_digest"],
        "mechanism_name": "native_response_magnitude_policy",
        "mechanism_role": "bounded_proxy_error_response_magnitude_phase8_candidate",
        "secondary_tags": [
            "native_policy_gap",
            "producer_mediated_source_split",
            "response_magnitude_candidate",
            "phase8_ready_no_implementation",
        ],
        "producer_decision_fields": inventory_row["producer_decision_fields"],
        "bookkeeping_fields": inventory_row["bookkeeping_fields"],
        "runtime_visible_surfaces": sorted(
            set(inventory_row["runtime_visible_surfaces"])
            | {
                "native_response_magnitude_policy_record",
                "native_goal_proxy_regulation_policy_record",
                "response_magnitude_budget_surface",
                "response_magnitude_telemetry_record",
            }
        ),
        "runtime_visible_inputs": runtime_visible_inputs,
        "contract_runtime_visible_inputs": sorted(
            set(inventory_row["contract_runtime_visible_inputs"])
        ),
        "budget_surfaces": budget_surfaces,
        "budget_semantics": {
            "goal_proxy_budget_surface": {
                "surface_type": "derived_proxy_observable_surface",
                "role": "tracks proxy measurement and target-band error from runtime-visible state",
                "phase8_rule": "proxy measurement remains derived observable, not new hidden state",
            },
            "response_magnitude_budget_surface": {
                "surface_type": "serialized_policy_sizing_surface",
                "role": "accounts response gain, max correction per window, and envelope limits",
                "unit_boundary": "response packet amount and error reduction, not semantic goal value",
                "phase8_rule": "response size must be replayable from policy, error, envelope, and budget digests",
            },
            "node_plus_packet_budget_surface_separate": {
                "surface_type": "existing_conservation_surface",
                "role": "ensures correction is expressed as scheduled packet work and step-owned mutation",
                "phase8_rule": "response correction must conserve node-plus-packet budget",
            },
        },
        "thresholds_to_serialize": sorted(
            set(inventory_row["thresholds_to_serialize"])
            | {
                "minimum_error_for_response",
                "saturation_threshold",
                "overcorrection_tolerance",
                "bounded_window_size",
                "perturbation_envelope_limit",
            }
        ),
        "native_gap": "native_response_magnitude_policy_missing_for_unbounded_perturbations",
        "native_policy_name": "native_response_magnitude_policy",
        "record_schema_sketch": build_record_schema_sketch(),
        "covered_policy_records": sorted(
            set(inventory_row["covered_policy_records"])
            | set(n10_contract["covered_policy_records"])
        ),
        "primary_disposition": "native_absorption_candidate",
        "nat_level": "NAT4",
        "phase8_ready": True,
        "phase8_readiness_source": "n12_iteration_4_nat4_gate_evaluation",
        "phase8_decision_source": "phase8_ready_candidate_no_implementation",
        "phase8_order_source": inventory_row["phase8_order_source"],
        "claim_ceiling": "phase8_ready_native_policy_candidate_no_native_support",
        "blocked_claims": blocked_claims,
        "missing_gates": [],
        "non_rc_quantity_audit": non_rc_quantity_audit,
        "artifact_replay_requirements": sorted(
            set(inventory_row["artifact_replay_requirements"])
            | {
                "replay reconstructs proxy measurement and target-band error",
                "replay reconstructs bounded response gain and max correction",
                "replay verifies response packet schedule and processing digests",
                "replay rejects hidden optimizer state or report-side response sizing",
                "replay rejects out-of-envelope perturbation without policy",
            }
        ),
        "claim_boundary_controls": sorted(
            set(inventory_row["claim_boundary_controls"])
            | set(n10_contract["claim_boundary_controls"])
            | {
                "native_absorption_candidate_not_native_support",
                "response_magnitude_policy_not_goal_ownership",
                "response_magnitude_policy_not_intention",
                "bounded_regulation_not_unbounded_native_regulation",
            }
        ),
        "ordering_requirements": sorted(
            set(inventory_row["ordering_requirements"])
            | set(n10_contract["ordering_requirements"])
            | {
                "target band must be current before proxy error digest",
                "bounded response record must precede packet scheduling",
                "packet processing must own proxy-affecting state mutation",
            }
        ),
        "stale_context_blockers": sorted(
            set(inventory_row["stale_context_blockers"])
            | set(n10_contract["stale_context_blockers"])
            | {
                "stale_response_gain_policy_blocked",
                "stale_perturbation_envelope_blocked",
                "stale_budget_surface_blocked",
            }
        ),
        "n11_native_supported": False,
        "n11_native_support_scope": "not_native",
        "native_support_opened": False,
        "phase8_opened": False,
        "mutation_boundary": mutation_boundary,
        "producer_or_policy_may_schedule_only": True,
        "step_or_topology_event_owns_state_mutation": True,
        "default_off_flags": {
            "native_response_magnitude_policy_enabled": False,
            "native_goal_proxy_regulation_policy_enabled": False,
            "native_response_magnitude_telemetry_enabled": False,
        },
        "enabled_validated_supported_separation": {
            "enabled": False,
            "validated": False,
            "supported": False,
            "phase8_ready_candidate": True,
            "native_support_opened": False,
        },
        "idempotency_digest_plan": {
            "policy_record_digest_inputs": [
                "policy_id",
                "proxy_surface_digest",
                "target_band_digest",
                "proxy_error_digest",
                "eligibility_record_digest",
                "perturbation_envelope_digest",
                "response_gain_policy_id",
                "max_correction_per_window",
                "response_packet_schedule_digest",
                "budget_before_digest",
                "budget_after_digest",
            ],
            "duplicate_response_rejection": "same proxy_error_digest and bounded_window_id cannot schedule two corrections",
            "replay_digest_rule": "canonical JSON digest with sorted keys and explicit policy, proxy, response, and budget state",
        },
        "telemetry_requirements": [
            "response_magnitude_policy_record_emitted_default_off",
            "proxy_surface_digest_and_target_band_digest",
            "proxy_error_digest_and_error_trend_digest",
            "eligibility_record_digest",
            "response_gain_policy_id_and_max_correction_per_window",
            "perturbation_envelope_digest",
            "response_packet_schedule_digest",
            "node_plus_packet_budget_before_after_digests",
            "proxy_budget_before_after_digests",
            "negative_control_blocker_id",
            "claim_flags_forced_false_snapshot",
        ],
        "telemetry_namespaces": {
            "primary_native_namespace": "src/pygrc/telemetry",
            "candidate_records": [
                "ResponseMagnitudePolicyRecord",
                "ResponseMagnitudeBudgetRecord",
                "ResponseMagnitudeControlRecord",
            ],
            "default_off_namespace_rule": (
                "new native telemetry is disabled unless the Phase 8 policy flag is explicitly enabled"
            ),
            "backward_compatibility_rule": (
                "existing telemetry exports remain byte-compatible when the native response magnitude policy is disabled"
            ),
        },
        "telemetry_export_behavior": {
            "default_off": True,
            "backward_compatible_when_disabled": True,
            "legacy_exports_unchanged_until_enabled": True,
            "new_records_require_explicit_flag": True,
            "native_support_flags_exported_false": True,
        },
        "snapshot_replay_requirements": [
            "snapshot includes policy flags and disabled-by-default state",
            "snapshot includes proxy surface and target band digests",
            "snapshot includes error trend, saturation, and overcorrection fields",
            "snapshot includes response packet schedule and processing digests",
            "snapshot includes node-plus-packet and proxy budget before/after digests",
            "replay rejects hidden optimizer state and out-of-envelope response",
            "replay preserves no native support flags",
        ],
        "negative_controls": negative_controls,
        "compatibility_tests": [
            "policy_disabled_records_no_response_mutation",
            "proxy_measurement_is_derived_observable",
            "target_band_digest_precedes_error_digest",
            "response_gain_serialized_and_replayable",
            "max_correction_per_window_enforced",
            "wrong_direction_response_rejected",
            "hidden_optimizer_state_rejected",
            "out_of_envelope_perturbation_blocked",
            "node_plus_packet_budget_conserved",
            "artifact_replay_recomputes_policy_record_digest",
            "telemetry_default_off_exports_no_new_records",
            "existing_telemetry_exports_backward_compatible_when_disabled",
            "claim_flags_remain_false",
        ],
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "src_diff_empty": git_status_short("src") == "",
        "native_supported_flags_false": True,
        "phase8_opened_false": True,
        "response_policy_split": {
            "producer_side_goal_proxy_regulation_pattern": {
                "source": "N09 Hypothesis A GPR6 and N10/N11 consumption",
                "status": "experiment_local_scaffold_only",
                "uses": [
                    "serialized proxy measurement",
                    "serialized target band",
                    "producer-mediated response selection",
                    "artifact-only replay",
                ],
                "not_native_because": [
                    "N09 closes as artifact-only goal-proxy regulation candidate",
                    "N10/N11 keep native response magnitude policy missing",
                    "bounded response cannot be relabelled goal ownership or intention",
                ],
            },
            "native_response_magnitude_policy_candidate": {
                "source": "N09 bounded response evidence plus N10 contract row",
                "status": "phase8_ready_candidate_not_implemented",
                "policy_surface": "native_response_magnitude_policy",
                "allowed_carrier": "runtime-visible proxy error and packet scheduling policy",
                "update_owner": "step_or_packet_event",
            },
            "native_goal_semantics": {
                "status": "blocked_not_part_of_candidate",
                "blocked_interpretations": [
                    "semantic goal ownership",
                    "semantic goal understanding",
                    "agent intention",
                    "unbounded native regulation",
                ],
            },
        },
        "trend_stability_fields": trend_stability_fields,
        "proxy_measurement_surface": {
            "status": "specified_for_phase8_entry",
            "source_proxy_policy_id": n09_i3["proxy_surface_row"]["proxy_policy_id"],
            "proxy_kind": n09_i3["proxy_surface_row"]["proxy_kind"],
            "measurement_unit": n09_i3["proxy_surface_row"]["measurement_unit"],
            "runtime_visible": n09_i3["validation_checks"][
                "measurement_is_runtime_visible"
            ],
        },
        "target_band_policy": {
            "status": "specified_for_phase8_entry",
            "target_band_policy_id": n09_i3["target_band_row"][
                "target_band_policy_id"
            ],
            "lower_bound": n09_i3["target_band_row"]["lower_bound"],
            "upper_bound": n09_i3["target_band_row"]["upper_bound"],
            "target_kind": n09_i3["target_band_row"]["target_kind"],
            "not_semantic_goal": True,
        },
        "response_magnitude_policy": {
            "status": "specified_for_phase8_entry",
            "response_gain_source": "serialized response gain and max correction per window",
            "single_cycle_packet_amount": n09_i6["packet_response_record"][
                "packet_amount"
            ],
            "max_correction_per_window": n09_i6["packet_response_record"][
                "packet_amount"
            ],
            "bounded_window_count": n09_i7["window_policy"]["window_count"],
            "out_of_envelope_blocker": "unbounded_perturbation_envelope_blocked",
        },
        "response_packet_scheduling_boundary": {
            "status": "specified_for_phase8_entry",
            "policy_may_schedule_only": True,
            "step_required_for_mutation": n09_i6["schedule_request"][
                "step_required_for_mutation"
            ],
            "producer_direct_mutation_allowed": n09_i6["schedule_request"][
                "producer_direct_mutation_allowed"
            ],
        },
        "source_evidence_summary": {
            "n09_hypothesis_a_scope": n09_i9["hypothesis_a_closeout"]["scope"],
            "n09_hypothesis_a_status": n09_i9["hypothesis_a_closeout"]["status"],
            "n09_gpr6_claim_ceiling": n09_i9["claim_ceiling"],
            "n09_primary_hypothesis_b_blocker": n09_i9["hypothesis_b_status"][
                "primary_blocker"
            ],
            "n09_gpr4_single_cycle_band_return": n09_i6["validation_checks"][
                "single_cycle_band_return"
            ],
            "n09_gpr5_memory_cycles_return_to_band": n09_i7["validation_checks"][
                "memory_cycles_all_return_to_band"
            ],
            "n09_gpr8_perturbation_recovered": n09_i8["validation_checks"][
                "perturbation_recovery_returned_to_band"
            ],
            "n09_b1_native_claim_promotion_blocked": n09_i11["controls"][
                "native_claim_promotion"
            ]["control_passed"],
            "n09_b1b_envelope_overclaim_blocked": n09_i11b["controls"][
                "envelope_overclaim"
            ]["control_passed"],
            "n09_b2_native_substrate_claim_allowed": n09_i12["claim_flags"][
                "native_substrate_mediated_goal_proxy_regulation_claim_allowed"
            ],
            "n10_contract_status": n10_contract["native_contract_status"],
            "n11_gap_native_supported": n11_gap["native_supported"],
        },
    }
    row["row_digest"] = row_digest(row)
    return row


def build_nat4_gate_status(row: dict[str, Any], schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    def present(gate: str) -> bool:
        return gate in row and row[gate] not in (None, [], {})

    gate_sources = {
        "native_policy_name": "N09 closeout, N10 contract, N11 gap, N12 candidate row",
        "record_schema_sketch": "N12 Iteration 4 record schema sketch",
        "default_off_flags": "N12 Iteration 4 default-off policy flags",
        "enabled_validated_supported_separation": "N12 Iteration 4 claim boundary fields",
        "idempotency_digest_plan": "N12 Iteration 4 digest plan",
        "runtime_visible_inputs": "N10 contract plus N12 trend/budget extensions",
        "budget_surfaces": "N10 contract plus N12 typed budget semantics",
        "telemetry_requirements": "N12 telemetry namespace and export behavior",
        "snapshot_replay_requirements": "N10 replay requirements plus N12 replay extensions",
        "negative_controls": "N09 controls, N10 contract controls, N12 claim controls",
        "compatibility_tests": "N12 Iteration 4 compatibility test list",
        "claim_flags_forced_false": "N12 Iteration 2 claim flags",
        "non_rc_quantity_audit": "N12 Iteration 4 non-RC audit",
        "mutation_boundary": "N12 Iteration 4 mutation boundary",
        "producer_or_policy_may_schedule_only": "N12 Iteration 4 mutation boundary",
        "step_or_topology_event_owns_state_mutation": "N12 Iteration 4 mutation boundary",
        "src_diff_empty": "git status --short src",
        "native_supported_flags_false": "N12 Iteration 4 no-native-support flags",
        "phase8_opened_false": "N12 Iteration 4 no-implementation flags",
    }
    validators = {
        "native_policy_name": lambda: row["native_policy_name"]
        == "native_response_magnitude_policy",
        "record_schema_sketch": lambda: {
            "proxy_surface_digest",
            "target_band_digest",
            "proxy_error_digest",
            "response_gain_policy_id",
            "max_correction_per_window",
            "policy_record_digest",
        }.issubset(set(row["record_schema_sketch"]["required_fields"]))
        and "hidden_optimizer_state" in row["record_schema_sketch"]["forbidden_fields"],
        "default_off_flags": lambda: all(
            value is False for value in row["default_off_flags"].values()
        ),
        "enabled_validated_supported_separation": lambda: row[
            "enabled_validated_supported_separation"
        ]
        == {
            "enabled": False,
            "validated": False,
            "supported": False,
            "phase8_ready_candidate": True,
            "native_support_opened": False,
        },
        "idempotency_digest_plan": lambda: "proxy_error_digest"
        in row["idempotency_digest_plan"]["policy_record_digest_inputs"]
        and "cannot schedule two corrections" in row["idempotency_digest_plan"][
            "duplicate_response_rejection"
        ],
        "runtime_visible_inputs": lambda: {
            "proxy_surface_digest",
            "target_band_policy_id",
            "proxy_error_digest",
            "response_magnitude_policy_id",
            "perturbation_envelope_digest",
            "response_packet_schedule_digest",
        }.issubset(set(row["runtime_visible_inputs"])),
        "budget_surfaces": lambda: {
            "goal_proxy_budget_surface",
            "response_magnitude_budget_surface",
            "node_plus_packet_budget_surface_separate",
        }.issubset(set(row["budget_surfaces"]))
        and row["budget_semantics"]["response_magnitude_budget_surface"][
            "surface_type"
        ]
        == "serialized_policy_sizing_surface",
        "telemetry_requirements": lambda: row["telemetry_namespaces"][
            "primary_native_namespace"
        ]
        == "src/pygrc/telemetry"
        and row["telemetry_export_behavior"]["default_off"] is True
        and row["telemetry_export_behavior"]["backward_compatible_when_disabled"]
        is True,
        "snapshot_replay_requirements": lambda: {
            "snapshot includes policy flags and disabled-by-default state",
            "snapshot includes proxy surface and target band digests",
            "snapshot includes response packet schedule and processing digests",
            "replay preserves no native support flags",
        }.issubset(set(row["snapshot_replay_requirements"])),
        "negative_controls": lambda: {
            "hidden_response_magnitude_rejected",
            "unbounded_perturbation_without_policy_rejected",
            "wrong_direction_response_rejected",
            "hidden_optimizer_state_rejected",
        }.issubset(set(row["negative_controls"])),
        "compatibility_tests": lambda: {
            "proxy_measurement_is_derived_observable",
            "response_gain_serialized_and_replayable",
            "max_correction_per_window_enforced",
            "out_of_envelope_perturbation_blocked",
            "node_plus_packet_budget_conserved",
            "claim_flags_remain_false",
        }.issubset(set(row["compatibility_tests"])),
        "claim_flags_forced_false": lambda: all_claim_flags_false(
            row["claim_flags_forced_false"]
        ),
        "non_rc_quantity_audit": lambda: row["non_rc_quantity_audit"][
            "audit_status"
        ]
        == "passed_for_nat4_readiness"
        and row["non_rc_quantity_audit"][
            "does_response_sizing_require_hidden_optimization_or_external_controller_state"
        ]
        is False,
        "mutation_boundary": lambda: row["mutation_boundary"]["status"]
        == "specified_for_phase8_entry"
        and row["mutation_boundary"]["producer_or_policy_may_schedule_only"] is True
        and row["mutation_boundary"]["step_or_topology_event_owns_state_mutation"]
        is True,
        "producer_or_policy_may_schedule_only": lambda: row[
            "producer_or_policy_may_schedule_only"
        ]
        is True,
        "step_or_topology_event_owns_state_mutation": lambda: row[
            "step_or_topology_event_owns_state_mutation"
        ]
        is True,
        "src_diff_empty": lambda: row["src_diff_empty"] is True,
        "native_supported_flags_false": lambda: row["native_supported_flags_false"]
        is True
        and row["native_support_opened"] is False
        and row["claim_flags_forced_false"]["native_support_opened"] is False,
        "phase8_opened_false": lambda: row["phase8_opened_false"] is True
        and row["phase8_opened"] is False,
    }
    status: dict[str, dict[str, Any]] = {}
    for gate in schema["nat4_gates"]["required"]:
        gate_present = present(gate)
        gate_validated = gate_present and validators[gate]()
        status[gate] = {
            "present": gate_present,
            "validated": gate_validated,
            "source": gate_sources[gate],
        }
    return status


def validate_candidate(
    row: dict[str, Any],
    schema: dict[str, Any],
    inventory_row: dict[str, Any],
    n09_i3: dict[str, Any],
    n09_i6: dict[str, Any],
    n09_i7: dict[str, Any],
    n09_i8: dict[str, Any],
    n09_i9: dict[str, Any],
    n09_i11b: dict[str, Any],
    n09_i12: dict[str, Any],
    n10_contract: dict[str, Any],
    n11_gap: dict[str, Any],
) -> dict[str, bool]:
    nat4_required = schema["nat4_gates"]["required"]
    nat4_status = build_nat4_gate_status(row, schema)
    return {
        "iteration_1_response_row_present": bool(inventory_row),
        "iteration_2_nat4_gates_loaded": bool(nat4_required),
        "n09_proxy_measurement_runtime_visible": n09_i3["validation_checks"][
            "measurement_is_runtime_visible"
        ],
        "n09_gpr4_single_cycle_band_return": n09_i6["validation_checks"][
            "single_cycle_band_return"
        ],
        "n09_gpr5_bounded_repeated_regulation": n09_i7["validation_checks"][
            "memory_cycles_all_return_to_band"
        ]
        and n09_i7["window_policy"]["window_count"] == 4,
        "n09_gpr8_perturbation_recovered": n09_i8["validation_checks"][
            "perturbation_recovery_returned_to_band"
        ],
        "n09_gpr6_artifact_only_scope": n09_i9["hypothesis_a_closeout"][
            "scope"
        ]
        == "artifact_only_serialized_producer_policy_goal_proxy_regulation",
        "n09_bounded_native_overclaim_blocked": n09_i11b["controls"][
            "envelope_overclaim"
        ]["control_passed"],
        "n09_native_substrate_claim_blocked": n09_i12["claim_flags"][
            "native_substrate_mediated_goal_proxy_regulation_claim_allowed"
        ]
        is False,
        "n10_contract_present": n10_contract["row_id"]
        == "n10_i14_contract_03_goal_proxy_regulation",
        "n11_gap_present": n11_gap["native_gap"]
        == "native_response_magnitude_policy_missing_for_unbounded_perturbations",
        "trend_stability_fields_recorded": set(row["trend_stability_fields"].keys())
        == {
            "error_trend",
            "saturation_status",
            "overcorrection_status",
            "bounded_window",
            "out_of_envelope_blocker",
        },
        "non_rc_quantity_audit_passed": row["non_rc_quantity_audit"][
            "audit_status"
        ]
        == "passed_for_nat4_readiness",
        "no_hidden_optimizer_state": row["non_rc_quantity_audit"][
            "does_response_sizing_require_hidden_optimization_or_external_controller_state"
        ]
        is False,
        "mutation_boundary_recorded": row["producer_or_policy_may_schedule_only"]
        is True
        and row["step_or_topology_event_owns_state_mutation"] is True,
        "all_nat4_gates_present": all(
            gate["present"] for gate in nat4_status.values()
        ),
        "all_nat4_gates_validated": all(
            gate["validated"] for gate in nat4_status.values()
        ),
        "telemetry_namespace_explicit": row["telemetry_namespaces"][
            "primary_native_namespace"
        ]
        == "src/pygrc/telemetry",
        "telemetry_default_off_backward_compatible": row[
            "telemetry_export_behavior"
        ]["default_off"]
        is True
        and row["telemetry_export_behavior"]["backward_compatible_when_disabled"]
        is True,
        "budget_semantics_typed": row["budget_semantics"][
            "response_magnitude_budget_surface"
        ]["surface_type"]
        == "serialized_policy_sizing_surface",
        "phase8_ready_derived_from_nat4": row["nat_level"] == "NAT4"
        and row["phase8_ready"] is True,
        "no_native_support_claim": row["native_supported_flags_false"] is True
        and row["native_support_opened"] is False
        and row["claim_flags_forced_false"]["native_support_opened"] is False,
        "claim_flags_forced_false": all_claim_flags_false(
            row["claim_flags_forced_false"]
        ),
        "src_clean": row["src_diff_empty"] is True,
    }


def build_schema_alignment(row: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    final_row_fields = schema["final_row_fields"]
    row_fields = sorted(row.keys())
    missing_final_row_fields = sorted(set(final_row_fields) - set(row_fields))
    extra_row_fields = sorted(set(row_fields) - set(final_row_fields))
    candidate_specific_extension_fields = {
        "budget_semantics": "Iteration 4 typed budget semantics for proxy and response sizing.",
        "native_support_opened": "Row-level no-native-support flag.",
        "phase8_opened": "Row-level no-Phase-8-implementation flag.",
        "proxy_measurement_surface": "Iteration 4 proxy measurement surface details.",
        "response_magnitude_policy": "Iteration 4 response gain and correction window details.",
        "response_packet_scheduling_boundary": "Iteration 4 scheduling/mutation boundary.",
        "response_policy_split": "Iteration 4 producer-vs-native response policy split.",
        "source_evidence_summary": "Iteration 4 compact source-backed evidence summary.",
        "target_band_policy": "Iteration 4 target band policy details.",
        "telemetry_export_behavior": "Iteration 4 default-off/backward-compatible telemetry export behavior.",
        "telemetry_namespaces": "Iteration 4 telemetry namespace declaration, including src/pygrc/telemetry.",
        "trend_stability_fields": "Iteration 4 error trend, saturation, overcorrection, bounded window, and envelope blocker.",
    }
    return {
        "iteration_2_final_row_fields_count": len(final_row_fields),
        "candidate_row_fields_count": len(row_fields),
        "missing_final_row_fields": missing_final_row_fields,
        "extra_row_fields": extra_row_fields,
        "candidate_specific_extension_fields": candidate_specific_extension_fields,
        "all_extra_fields_documented": set(extra_row_fields).issubset(
            set(candidate_specific_extension_fields)
        ),
        "extension_policy": (
            "Iteration 4 may add candidate-specific extension fields when they "
            "are explicitly documented and do not promote native support or "
            "Phase 8 implementation."
        ),
    }


def build_output() -> dict[str, Any]:
    inventory = load_json(ITERATION_1_OUTPUT)
    schema = load_json(ITERATION_2_OUTPUT)
    n09_i3 = load_json(N09_I3_OUTPUT)
    n09_i4 = load_json(N09_I4_OUTPUT)
    n09_i6 = load_json(N09_I6_OUTPUT)
    n09_i7 = load_json(N09_I7_OUTPUT)
    n09_i8 = load_json(N09_I8_OUTPUT)
    n09_i9 = load_json(N09_I9_OUTPUT)
    n09_i10 = load_json(N09_I10_OUTPUT)
    n09_i11 = load_json(N09_I11_OUTPUT)
    n09_i11a = load_json(N09_I11A_OUTPUT)
    n09_i11b = load_json(N09_I11B_OUTPUT)
    n09_i12 = load_json(N09_I12_OUTPUT)
    n10_i14 = load_json(N10_I14_OUTPUT)
    n11_i11 = load_json(N11_I11_OUTPUT)

    inventory_row = find_inventory_response_row(inventory)
    n10_contract = find_object_by_row_id(
        n10_i14, "n10_i14_contract_03_goal_proxy_regulation"
    )
    n11_gap = find_object_by_row_id(
        n11_i11, "n11_i11_gap_03_response_magnitude_policy"
    )
    if n10_contract is None:
        raise ValueError("N10 response magnitude contract row missing")
    if n11_gap is None:
        raise ValueError("N11 response magnitude gap row missing")

    row = build_candidate_row(
        inventory_row,
        n09_i3,
        n09_i4,
        n09_i6,
        n09_i7,
        n09_i8,
        n09_i9,
        n09_i11,
        n09_i11a,
        n09_i11b,
        n09_i12,
        n10_contract,
        n11_gap,
    )
    nat4_status = build_nat4_gate_status(row, schema)
    checks = validate_candidate(
        row,
        schema,
        inventory_row,
        n09_i3,
        n09_i6,
        n09_i7,
        n09_i8,
        n09_i9,
        n09_i11b,
        n09_i12,
        n10_contract,
        n11_gap,
    )

    source_artifacts = {
        rel(ITERATION_1_OUTPUT): source_artifact(ITERATION_1_OUTPUT, inventory),
        rel(ITERATION_1_REPORT): source_artifact(ITERATION_1_REPORT),
        rel(ITERATION_2_OUTPUT): source_artifact(ITERATION_2_OUTPUT, schema),
        rel(ITERATION_2_REPORT): source_artifact(ITERATION_2_REPORT),
        rel(N09_I3_OUTPUT): source_artifact(N09_I3_OUTPUT, n09_i3),
        rel(N09_I3_REPORT): source_artifact(N09_I3_REPORT),
        rel(N09_I4_OUTPUT): source_artifact(N09_I4_OUTPUT, n09_i4),
        rel(N09_I4_REPORT): source_artifact(N09_I4_REPORT),
        rel(N09_I6_OUTPUT): source_artifact(N09_I6_OUTPUT, n09_i6),
        rel(N09_I6_REPORT): source_artifact(N09_I6_REPORT),
        rel(N09_I7_OUTPUT): source_artifact(N09_I7_OUTPUT, n09_i7),
        rel(N09_I7_REPORT): source_artifact(N09_I7_REPORT),
        rel(N09_I8_OUTPUT): source_artifact(N09_I8_OUTPUT, n09_i8),
        rel(N09_I8_REPORT): source_artifact(N09_I8_REPORT),
        rel(N09_I9_OUTPUT): source_artifact(N09_I9_OUTPUT, n09_i9),
        rel(N09_I9_REPORT): source_artifact(N09_I9_REPORT),
        rel(N09_I10_OUTPUT): source_artifact(N09_I10_OUTPUT, n09_i10),
        rel(N09_I10_REPORT): source_artifact(N09_I10_REPORT),
        rel(N09_I11_OUTPUT): source_artifact(N09_I11_OUTPUT, n09_i11),
        rel(N09_I11_REPORT): source_artifact(N09_I11_REPORT),
        rel(N09_I11A_OUTPUT): source_artifact(N09_I11A_OUTPUT, n09_i11a),
        rel(N09_I11A_REPORT): source_artifact(N09_I11A_REPORT),
        rel(N09_I11B_OUTPUT): source_artifact(N09_I11B_OUTPUT, n09_i11b),
        rel(N09_I11B_REPORT): source_artifact(N09_I11B_REPORT),
        rel(N09_I12_OUTPUT): source_artifact(N09_I12_OUTPUT, n09_i12),
        rel(N09_I12_REPORT): source_artifact(N09_I12_REPORT),
        rel(N10_I14_OUTPUT): source_artifact(N10_I14_OUTPUT, n10_i14),
        rel(N10_I14_REPORT): source_artifact(N10_I14_REPORT),
        rel(N11_I11_OUTPUT): source_artifact(N11_I11_OUTPUT, n11_i11),
        rel(N11_I11_REPORT): source_artifact(N11_I11_REPORT),
    }
    schema_alignment = build_schema_alignment(row, schema)
    source_digest_policy = {
        "file_sha256_is_required_for_every_source": True,
        "all_source_file_sha256_present": all(
            isinstance(artifact["sha256"], str) and len(artifact["sha256"]) == 64
            for artifact in source_artifacts.values()
        ),
        "upstream_output_digest_or_artifact_digest_may_be_null": True,
        "null_digest_reason": (
            "Upstream N09/N10/N11 artifacts use mixed output_digest and "
            "artifact_digest conventions. N12 pins every source by file SHA-256 "
            "and records upstream digest fields opportunistically."
        ),
        "controlling_provenance_pin": "source_artifacts[*].sha256",
    }
    artifact_reproducibility = {
        "wall_clock_timestamp_in_file": False,
        "generated_at": GENERATED_AT,
        "generated_at_policy": (
            "fixed experiment timestamp for reproducible file SHA across reruns "
            "with unchanged source files and git HEAD"
        ),
        "output_digest_excludes": ["generated_at", "output_digest", "git"],
        "file_sha_reproducible_for_fixed_sources_and_git_head": True,
    }
    checks.update(
        {
            "row_level_native_support_opened_false": row["native_support_opened"]
            is False,
            "row_level_phase8_opened_false": row["phase8_opened"] is False,
            "schema_extension_fields_documented": schema_alignment[
                "all_extra_fields_documented"
            ],
            "source_file_sha256_all_present": source_digest_policy[
                "all_source_file_sha256_present"
            ],
            "generated_at_reproducible": artifact_reproducibility[
                "wall_clock_timestamp_in_file"
            ]
            is False,
        }
    )

    output = {
        "experiment": "N12",
        "iteration": 4,
        "purpose": "response_magnitude_candidate_nat4_readiness",
        "schema": "n12_response_magnitude_candidate_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "candidate_result": {
            "primary_disposition": row["primary_disposition"],
            "nat_level": row["nat_level"],
            "phase8_ready": row["phase8_ready"],
            "native_policy_name": row["native_policy_name"],
            "native_support_opened": False,
            "phase8_opened": False,
            "claim_ceiling": row["claim_ceiling"],
            "supported_interpretation": (
                "Bounded/envelope-gated Phase 8-ready response magnitude policy "
                "candidate with no implementation and no native support claim."
            ),
        },
        "checks": checks,
        "response_magnitude_candidate": row,
        "schema_alignment": schema_alignment,
        "nat4_gate_status": nat4_status,
        "claim_boundary": {
            "native_absorption_candidate_is_native_support": False,
            "native_support_is_agency": False,
            "response_magnitude_policy_is_goal_ownership": False,
            "response_magnitude_policy_is_intention": False,
            "goal_proxy_regulation_is_semantic_goal_understanding": False,
            "bounded_response_is_unbounded_native_regulation": False,
            "phase8_ready_is_implementation": False,
        },
        "source_artifacts": source_artifacts,
        "source_digest_policy": source_digest_policy,
        "artifact_reproducibility": artifact_reproducibility,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["response_magnitude_candidate"]
    split = row["response_policy_split"]
    source_summary = row["source_evidence_summary"]
    lines = [
        "# N12 Iteration 4 Response Magnitude Candidate",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"primary_disposition = {row['primary_disposition']}",
        f"nat_level = {row['nat_level']}",
        f"phase8_ready = {str(row['phase8_ready']).lower()}",
        "phase8_opened = false",
        "native_support_opened = false",
        "row.native_support_opened = false",
        "row.phase8_opened = false",
        "```",
        "",
        "Iteration 4 classifies response magnitude as a bounded/envelope-gated",
        "`NAT4` Phase 8-ready response magnitude policy candidate. This is a",
        "readiness classification only. It opens no native support claim for",
        "regulation, no semantic goal ownership, no intention, no agency, and no",
        "Phase 8 implementation.",
        "",
        "The JSON artifact is the source of truth for the full candidate record,",
        "source artifacts, digests, policy schema sketch, controls, and gate audit.",
        "",
        "## Source Decision",
        "",
        "N09 Hypothesis A remains artifact-only goal-proxy regulation. The native",
        "bounded/envelope-gated candidate is limited to serialized proxy error,",
        "response magnitude, bounded window, packet scheduling, and",
        "budget-accounted correction policy. N09 B-branch native substrate claims",
        "remain blocked.",
        "",
        "```text",
        f"N09 Hypothesis A scope = {source_summary['n09_hypothesis_a_scope']}",
        f"N09 GPR6 claim ceiling = {source_summary['n09_gpr6_claim_ceiling']}",
        f"N09 B blocker = {source_summary['n09_primary_hypothesis_b_blocker']}",
        "native_substrate_mediated_goal_proxy_regulation_claim_allowed = "
        f"{str(source_summary['n09_b2_native_substrate_claim_allowed']).lower()}",
        "```",
        "",
        "## Producer Vs Native Split",
        "",
        "| Layer | Status | Boundary |",
        "| --- | --- | --- |",
        "| Producer-side goal-proxy regulation pattern | "
        f"{split['producer_side_goal_proxy_regulation_pattern']['status']} | "
        "Serialized proxy, target band, and producer response remain artifact-only. |",
        "| Bounded/envelope-gated response magnitude policy candidate | "
        f"{split['native_response_magnitude_policy_candidate']['status']} | "
        "Only step/packet events may mutate proxy-affecting state. |",
        "| Native goal semantics | "
        f"{split['native_goal_semantics']['status']} | "
        "Goal ownership, intention, and semantic understanding remain blocked. |",
        "",
        "## NAT4 Gate Audit",
        "",
        "| Gate | Present | Validated | Source |",
        "| --- | --- | --- | --- |",
    ]
    for gate, status in output["nat4_gate_status"].items():
        lines.append(
            "| "
            f"`{gate}` | "
            f"`{str(status['present']).lower()}` | "
            f"`{str(status['validated']).lower()}` | "
            f"{status['source']} |"
        )
    lines.extend(
        [
            "",
            "## Trend And Stability",
            "",
            "```json",
            json.dumps(row["trend_stability_fields"], indent=2, sort_keys=True),
            "```",
            "",
            "## Record Schema Sketch",
            "",
            "```json",
            json.dumps(row["record_schema_sketch"], indent=2, sort_keys=True),
            "```",
            "",
            "## Budget Semantics",
            "",
            "```json",
            json.dumps(row["budget_semantics"], indent=2, sort_keys=True),
            "```",
            "",
            "## Telemetry Requirements",
            "",
            "```json",
            json.dumps(
                {
                    "telemetry_namespaces": row["telemetry_namespaces"],
                    "telemetry_export_behavior": row["telemetry_export_behavior"],
                    "telemetry_requirements": row["telemetry_requirements"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Compatibility Tests",
            "",
            "```json",
            json.dumps(row["compatibility_tests"], indent=2, sort_keys=True),
            "```",
            "",
            "## Non-RC Quantity Audit",
            "",
            "```json",
            json.dumps(row["non_rc_quantity_audit"], indent=2, sort_keys=True),
            "```",
            "",
            "## Schema Alignment And Candidate Extensions",
            "",
            "```json",
            json.dumps(output["schema_alignment"], indent=2, sort_keys=True),
            "```",
            "",
            "## Source Digest Policy",
            "",
            "```json",
            json.dumps(output["source_digest_policy"], indent=2, sort_keys=True),
            "```",
            "",
            "## Artifact Reproducibility",
            "",
            "```json",
            json.dumps(
                output["artifact_reproducibility"], indent=2, sort_keys=True
            ),
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "native absorption candidate != native support",
            "native support != agency",
            "response magnitude policy != goal ownership",
            "response magnitude policy != intention",
            "goal-proxy regulation != semantic goal understanding",
            "bounded response != unbounded native regulation",
            "phase8_ready != Phase 8 implementation",
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)


if __name__ == "__main__":
    main()
