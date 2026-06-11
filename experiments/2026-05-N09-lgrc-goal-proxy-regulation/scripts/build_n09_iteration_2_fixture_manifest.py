#!/usr/bin/env python3
"""Build and validate the N09 Iteration 2 fixture manifest.

Iteration 2 is contract-only. It freezes proxy-regulation schemas, lanes,
controls, budgets, and replay requirements before any positive regulation
probe is run.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"
BASELINE_PATH = EXPERIMENT / "outputs" / "n09_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n09_iteration_2_fixture_manifest_validation.json"
REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_2_fixture_manifest_validation.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "build_n09_iteration_2_fixture_manifest.py"
)

PROXY_SURFACE_REQUIRED_FIELDS = [
    "proxy_surface_id",
    "proxy_kind",
    "regulated_variable_id",
    "regulated_variable_surface",
    "regulated_variable_digest",
    "measurement_value",
    "measurement_unit",
    "target_band_id",
    "target_band_digest",
    "event_time_key",
    "scheduler_event_index",
    "proxy_policy_id",
    "proxy_policy_digest",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "source_artifacts",
    "source_reports",
    "claim_flags",
    "proxy_surface_digest",
]

TARGET_BAND_REQUIRED_FIELDS = [
    "target_band_id",
    "regulated_variable_id",
    "regulated_variable_surface",
    "target_kind",
    "lower_bound",
    "upper_bound",
    "target_value",
    "tolerance",
    "unit",
    "event_time_key",
    "target_band_policy_id",
    "target_band_policy_digest",
    "target_band_digest",
]

ERROR_SIGNAL_REQUIRED_FIELDS = [
    "error_signal_id",
    "proxy_surface_digest",
    "target_band_digest",
    "error_metric",
    "error_value",
    "error_direction",
    "in_band",
    "event_time_key",
    "scheduler_event_index",
    "error_policy_id",
    "error_policy_digest",
    "error_signal_digest",
]

REGULATION_RESPONSE_REQUIRED_FIELDS = [
    "regulation_response_id",
    "proxy_surface_digest",
    "target_band_digest",
    "error_signal_digest",
    "regulation_policy_id",
    "regulation_policy_digest",
    "lane_id",
    "mechanism_status_tags",
    "source_candidate_set_digest",
    "source_route_arbitration_record_digest",
    "selected_candidate_route_digest",
    "producer_record_digest",
    "producer_record_linkage",
    "scheduled_packet_id",
    "processed_packet_id",
    "pre_response_proxy_surface_digest",
    "post_response_proxy_surface_digest",
    "regulation_outcome_tag",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "proxy_budget_surface",
    "proxy_budget_before",
    "proxy_budget_after",
    "proxy_budget_error",
    "memory_surface_digest",
    "memory_policy_digest",
    "memory_strength",
    "memory_surface_key_digest",
    "memory_score_component",
    "memory_budget_surface",
    "memory_budget_before",
    "memory_budget_after",
    "memory_budget_error",
    "identity_support_digest",
    "identity_support_outcome_tag",
    "claim_flags",
    "regulation_response_digest",
]

MEMORY_LANE_REQUIRED_FIELDS = [
    "memory_surface_digest",
    "memory_policy_digest",
    "memory_strength",
    "memory_surface_key_digest",
    "memory_score_component",
]

ROUTE_PRODUCER_EVIDENCE_FIELDS = [
    "source_candidate_set_digest",
    "source_route_arbitration_record_digest",
    "selected_candidate_route_digest",
    "rejected_candidate_route_digests",
    "candidate_runtime_visible_inputs",
    "candidate_score_components",
    "candidate_budget_prediction",
    "producer_record_digest",
    "producer_record_linkage",
    "scheduled_packet_id",
]

PACKET_RESPONSE_FIELDS = [
    "schedule_request_id",
    "scheduled_packet_id",
    "processed_packet_id",
    "route_id",
    "packet_amount",
    "source_node_id",
    "target_node_id",
    "scheduled_scheduler_event_index",
    "processed_scheduler_event_index",
    "step_processed",
    "pre_response_proxy_surface_digest",
    "post_response_proxy_surface_digest",
]

IDENTITY_SUPPORT_OUTCOME_TAGS = [
    "identity_not_tested_under_regulation",
    "identity_preserved_under_regulation",
    "identity_disrupted_under_regulation",
    "support_preserved_under_regulation",
    "support_disrupted_under_regulation",
    "identity_support_withdrawal_baseline_missing",
]

REQUIRED_CONTROL_BLOCKERS = {
    "missing_proxy_surface": "proxy_surface_missing",
    "proxy_surface_digest_mismatch": "proxy_surface_digest_mismatch",
    "hidden_proxy_source": "hidden_proxy_source_rejected",
    "target_band_missing": "target_band_missing",
    "hidden_proxy_target": "hidden_proxy_target_rejected",
    "posthoc_target_change": "posthoc_target_change_rejected",
    "error_policy_missing": "error_policy_missing",
    "error_signal_digest_mismatch": "error_signal_digest_mismatch",
    "regulation_policy_missing": "regulation_policy_missing",
    "hidden_reward_or_goal_label": "hidden_reward_or_goal_label_rejected",
    "n06_packet_execution_inherited": (
        "n06_selection_only_no_packet_execution_for_regulation"
    ),
    "unknown_candidate_source_surface": (
        "native_route_candidate_committed_source_surface_required"
    ),
    "candidate_budget_prediction_missing": "candidate_budget_prediction_missing",
    "memory_surface_missing_for_memory_lane": "memory_surface_missing_for_memory_lane",
    "memory_surface_read_in_no_memory_lane": "memory_surface_read_in_no_memory_lane",
    "producer_direct_mutation": "producer_direct_mutation_blocked",
    "scheduled_packet_missing": "scheduled_packet_missing",
    "processed_packet_missing": "processed_packet_missing",
    "wrong_direction_response": "wrong_direction_response",
    "node_plus_packet_budget_discontinuity": (
        "node_plus_packet_budget_discontinuity"
    ),
    "proxy_budget_ambiguity": "proxy_budget_ambiguity",
    "perturbation_schema_missing": "perturbation_schema_missing",
    "support_withdrawal_baseline_missing": (
        "n07_identity_withdrawal_baseline_not_available"
    ),
    "identity_support_digest_mismatch": "identity_support_digest_mismatch",
    "oscillator_fixture_without_explicit_opt_in": (
        "oscillator_regulation_fixture_requires_explicit_opt_in"
    ),
    "artifact_order_inversion": "artifact_order_inversion",
    "duplicate_regulation_response": "duplicate_regulation_response",
    "claim_promotion": "claim_promotion_blocked",
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


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(baseline["claim_flags"])}


def policy_with_digest(policy: dict[str, Any], digest_field: str) -> dict[str, Any]:
    copied = dict(policy)
    copied[digest_field] = digest_value(
        {key: value for key, value in copied.items() if key != digest_field}
    )
    return copied


def build_manifest(baseline: dict[str, Any]) -> dict[str, Any]:
    claim_flags = false_claim_flags(baseline)
    all_proxy_measurement_surfaces = {
        row["surface_id"]: row
        for row in baseline["available_proxy_measurement_surfaces"]
        if isinstance(row, dict) and row.get("surface_id")
    }
    source_surfaces = {
        surface_id: row
        for surface_id, row in all_proxy_measurement_surfaces.items()
        if row.get("runtime_visible") is True
        and "cannot be used directly as regulated_variable_surface"
        not in str(row.get("regulation_constraint", ""))
    }
    excluded_proxy_measurement_surfaces = {
        surface_id: {
            **row,
            "proxy_exclusion_reason": (
                "not_runtime_visible_or_declared_anchor_only_not_regulated_variable"
            ),
        }
        for surface_id, row in all_proxy_measurement_surfaces.items()
        if surface_id not in source_surfaces
    }
    action_surfaces = {
        row["surface_id"]: row
        for row in baseline["available_proxy_conditioned_action_surfaces"]
        if isinstance(row, dict) and row.get("surface_id")
    }
    n06_constraint = baseline["n06_inventory"]["regulation_constraint"]
    n07_gap = baseline["n07_inventory"]["identity_preservation_precondition_gap"]
    n08_anchor = baseline["n08_inventory"]["hypothesis_a"][
        "support_anchor_consistency"
    ]

    default_proxy_policy = policy_with_digest(
        {
            "proxy_policy_id": "n09_active_node_coherence_proxy_policy_v1",
            "proxy_surface": "active_node_coherence_band",
            "regulated_variable_id": "source_reservoir_node_coherence",
            "regulated_variable_surface": "active_node_state",
            "runtime_visible_source_required": True,
            "budget_auditable": True,
            "hidden_proxy_source_allowed": False,
            "posthoc_proxy_definition_allowed": False,
        },
        "proxy_policy_digest",
    )
    default_target_band_policy = policy_with_digest(
        {
            "target_band_policy_id": "n09_static_declared_band_policy_v1",
            "regulated_variable_id": "source_reservoir_node_coherence",
            "regulated_variable_surface": "active_node_state",
            "target_kind": "closed_interval",
            "lower_bound": 0.45,
            "upper_bound": 0.55,
            "target_value": 0.5,
            "tolerance": 1e-9,
            "unit": "coherence",
            "hidden_target_allowed": False,
            "posthoc_target_change_allowed": False,
        },
        "target_band_policy_digest",
    )
    default_error_policy = policy_with_digest(
        {
            "error_policy_id": "n09_signed_band_error_policy_v1",
            "error_metric": "signed_distance_to_declared_band",
            "in_band_error_value": 0.0,
            "below_band_direction": "increase_proxy",
            "above_band_direction": "decrease_proxy",
            "below_band_formula": "measurement_value - lower_bound",
            "above_band_formula": "measurement_value - upper_bound",
            "in_band_formula": "0.0",
            "runtime_visible_inputs": [
                "proxy_surface_digest",
                "measurement_value",
                "target_band_digest",
                "lower_bound",
                "upper_bound",
            ],
            "hidden_error_input_allowed": False,
        },
        "error_policy_digest",
    )
    default_regulation_policy = policy_with_digest(
        {
            "regulation_policy_id": "n09_proxy_error_threshold_schedule_policy_v1",
            "policy_surface": "experiment_local_serialized_policy",
            "native_support_status": "producer_scaffold_until_native_policy_exists",
            "error_threshold": 1e-9,
            "response_if_below_band": "schedule_or_select_route_that_increases_proxy",
            "response_if_above_band": "schedule_or_select_route_that_decreases_proxy",
            "response_if_in_band": "no_action_or_maintenance_non_trigger",
            "producer_scheduling_allowed": True,
            "producer_direct_mutation_allowed": False,
            "step_remains_mutation_boundary": True,
            "hidden_reward_or_goal_label_allowed": False,
            "semantic_goal_understanding_claim_allowed": False,
        },
        "regulation_policy_digest",
    )

    manifest: dict[str, Any] = {
        "schema": "n09_fixture_manifest_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 2,
        "purpose": "fixture_manifest_and_proxy_regulation_contract",
        "source_baseline_inventory": rel(BASELINE_PATH),
        "source_baseline_inventory_digest": baseline["inventory_digest"],
        "regulation_probe_run": False,
        "positive_regulation_evidence_generated": False,
        "default_fixture_family": {
            "fixture_family_id": "n09_default_active_node_band_regulation_v1",
            "regulated_proxy_surface": "active_node_coherence_band",
            "regulated_variable_id": "source_reservoir_node_coherence",
            "primary_reason": (
                "directly budget-auditable runtime-visible node coherence "
                "before oscillator-return or multi-variable fixtures"
            ),
            "memory_shaped_lane_required_for_gpr3_plus": True,
            "no_memory_comparator_required_for_gpr3_plus": True,
            "n06_selection_only_constraint": n06_constraint,
            "n07_withdrawal_precondition_gap": n07_gap,
            "n08_support_anchor_consistency": n08_anchor,
        },
        "secondary_fixture_families": {
            "oscillator_return_amount": {
                "status": "deferred_secondary_fixture",
                "explicit_opt_in_required": True,
                "source": "N05 O5 return amount",
                "primary_blocker_without_opt_in": (
                    "oscillator_regulation_fixture_requires_explicit_opt_in"
                ),
                "available_fields": baseline["n05_inventory"][
                    "oscillator_proxy_field_inventory"
                ],
            }
        },
        "available_proxy_measurement_surfaces": all_proxy_measurement_surfaces,
        "allowed_proxy_measurement_surfaces": source_surfaces,
        "excluded_proxy_measurement_surfaces": excluded_proxy_measurement_surfaces,
        "available_proxy_conditioned_action_surfaces": action_surfaces,
        "proxy_surface_row_schema": {
            "artifact_kind": "n09_proxy_surface_row",
            "schema_version": "n09_proxy_surface_row_v1",
            "required_fields": PROXY_SURFACE_REQUIRED_FIELDS,
            "allowed_proxy_kinds": sorted(source_surfaces),
            "excluded_proxy_kinds": sorted(excluded_proxy_measurement_surfaces),
            "proxy_kind_constraints": {
                "route_arbitration_context_surface": {
                    "gpr4_plus_constraint": (
                        "selection surface only; cannot supply scheduled or "
                        "processed packet evidence without an N09 "
                        "scheduling/processing lane"
                    )
                },
                "n08_serialized_memory_surface_strength": {
                    "budget_constraint": (
                        "memory budget only; cannot substitute for "
                        "node-plus-packet budget"
                    )
                },
                "n05_oscillator_return_amount": {
                    "fixture_constraint": (
                        "deferred secondary fixture; requires explicit opt-in"
                    )
                },
            },
            "default_proxy_policy": default_proxy_policy,
            "digest_field": "proxy_surface_digest",
            "digest_rule": (
                "sha256(canonical_json(proxy_surface_row_without_proxy_surface_digest))"
            ),
            "invalid_proxy_sources": [
                "hidden_reward",
                "fixture_food_or_danger_label_without_runtime_evidence",
                "experiment_side_if_else",
                "report_side_correction",
                "posthoc_target_change",
                "unserialized_python_state",
                "agent_intention_or_desire_label",
            ],
            "claim_flags_must_remain_false": True,
            "required_claim_flag_keys": sorted(claim_flags),
        },
        "target_band_schema": {
            "artifact_kind": "n09_target_band",
            "schema_version": "n09_target_band_v1",
            "required_fields": TARGET_BAND_REQUIRED_FIELDS,
            "default_target_band_policy": default_target_band_policy,
            "digest_field": "target_band_digest",
            "digest_rule": (
                "sha256(canonical_json(target_band_without_target_band_digest))"
            ),
            "posthoc_target_change_allowed": False,
            "hidden_target_allowed": False,
        },
        "error_signal_schema": {
            "artifact_kind": "n09_error_signal",
            "schema_version": "n09_error_signal_v1",
            "required_fields": ERROR_SIGNAL_REQUIRED_FIELDS,
            "default_error_policy": default_error_policy,
            "digest_field": "error_signal_digest",
            "digest_rule": (
                "sha256(canonical_json(error_signal_without_error_signal_digest))"
            ),
            "hidden_error_input_allowed": False,
        },
        "regulation_policy_schema": {
            "artifact_kind": "n09_regulation_policy",
            "schema_version": "n09_regulation_policy_v1",
            "default_regulation_policy": default_regulation_policy,
            "required_policy_fields": sorted(default_regulation_policy),
            "digest_field": "regulation_policy_digest",
            "digest_rule": (
                "sha256(canonical_json(regulation_policy_without_regulation_policy_digest))"
            ),
            "error_threshold_design_note": (
                "1e-9 is a strict contract tolerance for the baseline fixture; "
                "later probes may declare a different serialized threshold but "
                "cannot change it post hoc."
            ),
            "native_goal_proxy_regulation_policy_available": False,
            "native_goal_proxy_regulation_policy_blocker": (
                "native_goal_proxy_regulation_policy_missing"
            ),
        },
        "regulation_response_schema": {
            "artifact_kind": "n09_regulation_response",
            "schema_version": "n09_regulation_response_v1",
            "required_fields": REGULATION_RESPONSE_REQUIRED_FIELDS,
            "digest_field": "regulation_response_digest",
            "digest_rule": (
                "sha256(canonical_json(regulation_response_without_regulation_response_digest))"
            ),
            "memory_lane_attachment": {
                "attachment_mode": "nullable_fields_on_regulation_response",
                "required_non_null_when_lane_id": "n09_memory_shaped_proxy_regulation_lane_v1",
                "must_be_null_or_zero_when_lane_id": (
                    "n09_no_memory_proxy_regulation_comparator_v1"
                ),
                "fields": MEMORY_LANE_REQUIRED_FIELDS
                + [
                    "memory_budget_surface",
                    "memory_budget_before",
                    "memory_budget_after",
                    "memory_budget_error",
                ],
            },
            "identity_support_attachment": {
                "attachment_mode": "nullable_fields_on_regulation_response",
                "fields": [
                    "identity_support_digest",
                    "identity_support_outcome_tag",
                ],
                "schema_evolution_note": (
                    "Iteration 1 froze a monolithic GPR row schema. Iteration "
                    "2 decomposes that row into proxy, target, error, response, "
                    "and optional identity/support artifacts while retaining "
                    "join fields on the regulation response."
                ),
            },
            "claim_flags_must_remain_false": True,
            "required_claim_flag_keys": sorted(claim_flags),
        },
        "lane_contract": {
            "memory_shaped_lane": {
                "lane_id": "n09_memory_shaped_proxy_regulation_lane_v1",
                "required_for_gpr3_plus": True,
                "required_fields": MEMORY_LANE_REQUIRED_FIELDS,
                "memory_source": "N08 Hypothesis A serialized memory surface",
                "n08_field_mapping": {
                    "memory_surface_digest": "memory_surface_digest",
                    "memory_policy_digest": "memory_policy_digest",
                    "memory_strength": "memory_strength",
                    "memory_surface_key_digest": "memory_surface_key_digest",
                    "memory_score_component": "candidate_score_components.memory_trail_strength",
                },
                "legacy_aliases_not_preferred": {
                    "memory_surface_policy_digest": "memory_policy_digest",
                    "memory_surface_strength": "memory_strength",
                },
                "memory_surface_native": False,
                "mechanism_status_tags": [
                    "producer_mediated",
                    "memory_shaped",
                    "native_policy_gap",
                ],
            },
            "no_memory_comparator_lane": {
                "lane_id": "n09_no_memory_proxy_regulation_comparator_v1",
                "required_for_gpr3_plus": True,
                "same_proxy_target_and_policy_required": True,
                "memory_surface_digest_must_be_null": True,
                "memory_score_component_must_be_absent_or_zero": True,
                "control_blocker_if_memory_read": "memory_surface_read_in_no_memory_lane",
            },
            "comparison_rule": (
                "GPR3+ claims that cite N08 memory must compare the same proxy, "
                "target, and regulation policy with and without memory."
            ),
        },
        "route_and_producer_evidence_contract": {
            "required_fields": ROUTE_PRODUCER_EVIDENCE_FIELDS,
            "n06_route_arbitration_may_supply_selection_evidence": True,
            "n06_packet_execution_may_be_inherited": False,
            "primary_blocker_if_packet_execution_inherited": n06_constraint[
                "primary_blocker_if_packet_execution_inherited"
            ],
            "unknown_source_surface_blocker": baseline["n06_inventory"][
                "source_provenance_constraints"
            ]["unknown_source_blockers"][0],
            "producer_record_digest_policy": (
                "N09 response artifacts may digest producer records when present; "
                "otherwise strict producer_record_linkage must include causal "
                "surface digest, reason code, scheduler order, and scheduled packet id."
            ),
            "producer_record_linkage_schema": {
                "required_fields": [
                    "causal_surface_digest",
                    "reason_code",
                    "scheduler_event_index",
                    "scheduled_packet_id",
                ],
                "producer_record_digest_available": "optional",
                "linkage_validation_required_without_digest": True,
            },
            "candidate_budget_prediction_requirement": {
                "required_for_new_n09_route_or_producer_evidence": True,
                "n06_closeout_rows_do_not_serialize_direct_candidate_budget_prediction": True,
                "n06_selection_only_rows_alone_cannot_satisfy_gpr4_plus_budget_gate": True,
                "primary_blocker_if_missing": "candidate_budget_prediction_missing",
            },
            "producer_may_mutate_state": False,
            "producer_may_mutate_claims": False,
        },
        "packet_scheduling_response_contract": {
            "required_fields": PACKET_RESPONSE_FIELDS,
            "gpr4_plus_requires_scheduled_and_processed_packet": True,
            "scheduled_packet_must_follow_producer_or_arbitration_record": True,
            "processed_packet_must_be_consumed_by_step": True,
            "step_remains_mutation_boundary": True,
            "n06_scheduled_processed_packet_scope": n06_constraint[
                "scheduled_processed_packet_scope"
            ],
        },
        "budget_contract": {
            "node_plus_packet_budget": {
                "fields": [
                    "node_plus_packet_budget_before",
                    "node_plus_packet_budget_after",
                    "node_plus_packet_budget_error",
                ],
                "must_remain_exact": True,
                "tolerance": 1e-9,
                "semantics": (
                    "physical LGRC coherence and in-flight packet accounting; "
                    "proxy or memory bookkeeping cannot repair drift"
                ),
            },
            "proxy_budget": {
                "fields": [
                    "proxy_budget_surface",
                    "proxy_budget_before",
                    "proxy_budget_after",
                    "proxy_budget_error",
                ],
                "semantics": (
                    "derived measurement accounting for proxy surfaces; not a "
                    "replacement for node-plus-packet conservation"
                ),
                "ambiguity_blocker": "proxy_budget_ambiguity",
            },
            "memory_budget": {
                "source": "N08 serialized memory budget when memory lane is active",
                "required_when_memory_shaped": True,
                "not_node_plus_packet_budget": True,
            },
        },
        "perturbation_schema": {
            "artifact_kind": "n09_proxy_perturbation",
            "required_fields": [
                "perturbation_id",
                "perturbation_kind",
                "amplitude",
                "duration_steps",
                "start_event_time_key",
                "affected_proxy_surface_id",
                "pre_perturbation_proxy_surface_digest",
                "post_perturbation_proxy_surface_digest",
                "node_plus_packet_budget_before",
                "node_plus_packet_budget_after",
                "node_plus_packet_budget_error",
                "expected_recovery_window_count",
                "recovery_success_criterion",
                "perturbation_digest",
            ],
            "amplitude_units": ["coherence", "normalized_proxy_units"],
            "duration_basis": "scheduler_steps",
            "hidden_perturbation_allowed": False,
        },
        "support_withdrawal_schema": {
            "artifact_kind": "n09_identity_support_withdrawal",
            "required_fields": [
                "withdrawal_id",
                "support_withdrawal_kind",
                "identity_support_digest",
                "support_area_id",
                "support_area_digest",
                "withdrawal_depth",
                "duration_steps",
                "baseline_support_digest",
                "post_withdrawal_support_digest",
                "identity_support_outcome_tag",
                "withdrawal_digest",
            ],
            "support_withdrawal_kind_values": [
                "partial_support_weakening",
                "source_support_reduction",
                "target_support_reduction",
                "full_support_withdrawal_control",
            ],
            "withdrawal_depth_range": [0.0, 1.0],
            "n07_withdrawal_baseline_available": False,
            "n07_withdrawal_baseline_blocker": (
                "n07_identity_withdrawal_baseline_not_available"
            ),
            "must_not_infer_identity_acceptance": True,
        },
        "identity_support_outcome_tags": IDENTITY_SUPPORT_OUTCOME_TAGS,
        "regulation_outcome_taxonomy": baseline["regulation_outcome_taxonomy"],
        "ceiling_algorithm": baseline["ceiling_algorithm"],
        "gpr_ladder": baseline["gpr_ladder"],
        "n10_handoff_fields": baseline["n10_handoff_fields"],
        "artifact_only_replay_requirements": {
            "artifact_only": True,
            "runtime_state_used": False,
            "ordered_chain": [
                "fixture_manifest",
                "proxy_surface_row",
                "target_band",
                "error_signal",
                "regulation_policy",
                "perturbation_if_tested",
                "support_withdrawal_if_tested",
                "route_or_producer_evidence",
                "scheduled_packet",
                "processed_packet",
                "post_response_proxy_surface_row",
                "regulation_response",
                "identity_support_outcome_if_tested",
                "n10_handoff_fields_if_closeout",
            ],
            "digest_recomputation_required": True,
            "scheduler_order_monotonic_required": True,
            "control_blockers_distinct_required": True,
        },
        "control_contract": [
            {
                "control_id": control_id,
                "expected_status": "blocked",
                "primary_blocker": blocker,
                "distinct_primary_blocker_required": True,
            }
            for control_id, blocker in REQUIRED_CONTROL_BLOCKERS.items()
        ],
        "native_policy_gap_records": [
            {
                "gap_id": gap,
                "status": "missing",
                "claim_boundary": "record_gap_do_not_promote_claim",
            }
            for gap in baseline["missing_native_policy_surfaces"]
        ],
        "claim_boundary": {
            "claim_flags": claim_flags,
            "claim_flags_must_remain_false": True,
            "goal_proxy_regulation_claim_requires_gpr6_closeout": True,
            "agency_intention_identity_aco_locomotion_claims_blocked": True,
        },
    }
    manifest["manifest_digest_scope"] = {
        "included": "manifest fields except manifest_digest",
        "excluded": ["manifest_digest"],
        "stable_across_same_inputs": True,
    }
    manifest["manifest_digest"] = digest_value(
        {key: value for key, value in manifest.items() if key != "manifest_digest"}
    )
    return manifest


def validate_manifest(manifest: dict[str, Any], baseline: dict[str, Any]) -> dict[str, bool]:
    controls = manifest["control_contract"]
    control_map = {row["control_id"]: row["primary_blocker"] for row in controls}
    claim_flags = manifest["claim_boundary"]["claim_flags"]
    lane = manifest["lane_contract"]
    budget = manifest["budget_contract"]
    replay = manifest["artifact_only_replay_requirements"]
    n06_constraint = manifest["route_and_producer_evidence_contract"]
    support_schema = manifest["support_withdrawal_schema"]
    proxy_schema = manifest["proxy_surface_row_schema"]
    target_policy = manifest["target_band_schema"]["default_target_band_policy"]
    response_schema = manifest["regulation_response_schema"]
    perturbation_fields = set(manifest["perturbation_schema"]["required_fields"])
    support_fields = set(support_schema["required_fields"])
    allowed_proxy_kinds = set(proxy_schema["allowed_proxy_kinds"])
    allowed_proxy_surface_rows = [
        manifest["available_proxy_measurement_surfaces"][surface_id]
        for surface_id in allowed_proxy_kinds
    ]
    support_anchor_rows = manifest["default_fixture_family"][
        "n08_support_anchor_consistency"
    ]["rows"]

    return {
        "source_baseline_digest_matches": (
            manifest["source_baseline_inventory_digest"] == baseline["inventory_digest"]
        ),
        "regulation_probe_not_run": manifest["regulation_probe_run"] is False,
        "positive_regulation_evidence_not_generated": (
            manifest["positive_regulation_evidence_generated"] is False
        ),
        "proxy_surface_schema_complete": all(
            field in proxy_schema["required_fields"]
            for field in PROXY_SURFACE_REQUIRED_FIELDS
        ),
        "allowed_proxy_kinds_runtime_visible": all(
            row.get("runtime_visible") is True for row in allowed_proxy_surface_rows
        ),
        "n07_identity_support_area_excluded_as_proxy_kind": (
            "n07_identity_support_area" not in allowed_proxy_kinds
            and "n07_identity_support_area" in proxy_schema["excluded_proxy_kinds"]
        ),
        "route_arbitration_context_constraint_visible": (
            "gpr4_plus_constraint"
            in proxy_schema["proxy_kind_constraints"]["route_arbitration_context_surface"]
        ),
        "target_band_schema_complete": all(
            field in manifest["target_band_schema"]["required_fields"]
            for field in TARGET_BAND_REQUIRED_FIELDS
        ),
        "target_band_bounds_valid_for_coherence": (
            0.0 <= target_policy["lower_bound"] <= target_policy["target_value"]
            <= target_policy["upper_bound"] <= 1.0
        ),
        "error_signal_schema_complete": all(
            field in manifest["error_signal_schema"]["required_fields"]
            for field in ERROR_SIGNAL_REQUIRED_FIELDS
        ),
        "regulation_response_schema_complete": all(
            field in response_schema["required_fields"]
            for field in REGULATION_RESPONSE_REQUIRED_FIELDS
        ),
        "regulation_response_attaches_memory_lane_fields": all(
            field in response_schema["required_fields"]
            for field in MEMORY_LANE_REQUIRED_FIELDS
            + [
                "memory_budget_surface",
                "memory_budget_before",
                "memory_budget_after",
                "memory_budget_error",
            ]
        ),
        "regulation_response_attaches_identity_support_fields": all(
            field in response_schema["required_fields"]
            for field in ["identity_support_digest", "identity_support_outcome_tag"]
        ),
        "regulation_policy_digest_rule_declared": (
            manifest["regulation_policy_schema"]["digest_field"]
            == "regulation_policy_digest"
            and "regulation_policy_without_regulation_policy_digest"
            in manifest["regulation_policy_schema"]["digest_rule"]
        ),
        "memory_lane_required": lane["memory_shaped_lane"]["required_for_gpr3_plus"]
        is True,
        "memory_lane_field_mapping_to_n08_declared": lane["memory_shaped_lane"][
            "n08_field_mapping"
        ]["memory_policy_digest"]
        == "memory_policy_digest",
        "no_memory_comparator_required": lane["no_memory_comparator_lane"][
            "required_for_gpr3_plus"
        ]
        is True,
        "same_proxy_target_policy_required_for_lane_comparison": (
            lane["no_memory_comparator_lane"]["same_proxy_target_and_policy_required"]
            is True
        ),
        "route_producer_evidence_fields_complete": all(
            field
            in manifest["route_and_producer_evidence_contract"]["required_fields"]
            for field in ROUTE_PRODUCER_EVIDENCE_FIELDS
        ),
        "packet_response_fields_complete": all(
            field
            in manifest["packet_scheduling_response_contract"]["required_fields"]
            for field in PACKET_RESPONSE_FIELDS
        ),
        "n06_packet_execution_not_inherited": (
            n06_constraint["n06_packet_execution_may_be_inherited"] is False
        ),
        "n06_unknown_source_blocker_preserved": (
            n06_constraint["unknown_source_surface_blocker"]
            == "native_route_candidate_committed_source_surface_required"
        ),
        "n06_candidate_budget_prediction_gap_recorded": (
            n06_constraint["candidate_budget_prediction_requirement"][
                "n06_closeout_rows_do_not_serialize_direct_candidate_budget_prediction"
            ]
            is True
            and n06_constraint["candidate_budget_prediction_requirement"][
                "primary_blocker_if_missing"
            ]
            == "candidate_budget_prediction_missing"
        ),
        "producer_record_linkage_schema_structured": set(
            n06_constraint["producer_record_linkage_schema"]["required_fields"]
        )
        == {
            "causal_surface_digest",
            "reason_code",
            "scheduler_event_index",
            "scheduled_packet_id",
        },
        "node_plus_packet_budget_separate_and_exact": (
            budget["node_plus_packet_budget"]["must_remain_exact"] is True
            and budget["memory_budget"]["not_node_plus_packet_budget"] is True
        ),
        "proxy_budget_ambiguity_blocker_declared": (
            budget["proxy_budget"]["ambiguity_blocker"] == "proxy_budget_ambiguity"
        ),
        "perturbation_schema_complete": "perturbation_digest"
        in perturbation_fields,
        "perturbation_recovery_fields_declared": {
            "expected_recovery_window_count",
            "recovery_success_criterion",
        }.issubset(perturbation_fields),
        "support_withdrawal_schema_complete": "withdrawal_digest" in support_fields,
        "support_withdrawal_kind_declared": "support_withdrawal_kind"
        in support_fields,
        "n07_withdrawal_gap_preserved": (
            support_schema["n07_withdrawal_baseline_available"] is False
            and support_schema["n07_withdrawal_baseline_blocker"]
            == "n07_identity_withdrawal_baseline_not_available"
        ),
        "identity_support_outcome_tags_declared": set(IDENTITY_SUPPORT_OUTCOME_TAGS)
        == set(manifest["identity_support_outcome_tags"]),
        "regulation_outcome_taxonomy_inherited": (
            manifest["regulation_outcome_taxonomy"]
            == baseline["regulation_outcome_taxonomy"]
        ),
        "ceiling_algorithm_inherited": manifest["ceiling_algorithm"]
        == baseline["ceiling_algorithm"],
        "n10_handoff_fields_inherited": manifest["n10_handoff_fields"]
        == baseline["n10_handoff_fields"],
        "oscillator_fixture_deferred": manifest["secondary_fixture_families"][
            "oscillator_return_amount"
        ]["status"]
        == "deferred_secondary_fixture",
        "artifact_only_replay_chain_declared": (
            replay["artifact_only"] is True
            and replay["runtime_state_used"] is False
            and "processed_packet" in replay["ordered_chain"]
        ),
        "artifact_only_replay_chain_includes_perturbation_and_withdrawal": {
            "perturbation_if_tested",
            "support_withdrawal_if_tested",
        }.issubset(set(replay["ordered_chain"])),
        "controls_have_distinct_blockers": len(set(control_map.values()))
        == len(control_map),
        "required_controls_present": set(REQUIRED_CONTROL_BLOCKERS) == set(control_map),
        "control_blockers_match_contract": control_map == REQUIRED_CONTROL_BLOCKERS,
        "claim_flags_all_false": all(value is False for value in claim_flags.values()),
        "claim_flag_keys_match_baseline": sorted(claim_flags)
        == sorted(baseline["claim_flags"]),
        "native_policy_gaps_recorded": {
            row["gap_id"] for row in manifest["native_policy_gap_records"]
        }
        == set(baseline["missing_native_policy_surfaces"]),
        "default_fixture_is_budget_auditable_node_band": manifest[
            "default_fixture_family"
        ]["regulated_proxy_surface"]
        == "active_node_coherence_band",
        "n08_support_anchor_consistency_revalidated": all(
            row["source_matches_n07_support_area"]
            and row["target_matches_n07_11b_target_support_area"]
            for row in support_anchor_rows
        ),
    }


def build_validation(manifest: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    checks = validate_manifest(manifest, baseline)
    validation: dict[str, Any] = {
        "schema": "n09_iteration_2_fixture_manifest_validation_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 2,
        "status": "passed" if all(checks.values()) else "failed",
        "purpose": "fixture_manifest_and_proxy_regulation_contract_validation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "source_baseline_inventory": rel(BASELINE_PATH),
        "source_baseline_inventory_digest": baseline["inventory_digest"],
        "manifest_path": rel(MANIFEST_PATH),
        "manifest_digest": manifest["manifest_digest"],
        "manifest_sha256": digest_file(MANIFEST_PATH),
        "checks": checks,
        "control_summary": {
            row["control_id"]: {
                "status": row["expected_status"],
                "primary_blocker": row["primary_blocker"],
            }
            for row in manifest["control_contract"]
        },
        "contract_summary": {
            "default_fixture_family": manifest["default_fixture_family"][
                "fixture_family_id"
            ],
            "memory_lane_required": manifest["lane_contract"]["memory_shaped_lane"][
                "required_for_gpr3_plus"
            ],
            "no_memory_comparator_required": manifest["lane_contract"][
                "no_memory_comparator_lane"
            ]["required_for_gpr3_plus"],
            "n06_packet_execution_inherited": manifest[
                "route_and_producer_evidence_contract"
            ]["n06_packet_execution_may_be_inherited"],
            "n07_withdrawal_baseline_available": manifest[
                "support_withdrawal_schema"
            ]["n07_withdrawal_baseline_available"],
            "oscillator_fixture_status": manifest["secondary_fixture_families"][
                "oscillator_return_amount"
            ]["status"],
            "native_goal_proxy_regulation_policy_available": manifest[
                "regulation_policy_schema"
            ]["native_goal_proxy_regulation_policy_available"],
        },
        "acceptance": {
            "status": "passed" if all(checks.values()) else "failed",
            "achieved": all(checks.values()),
            "acceptance_statement": (
                "Iteration 2 passes if N09 has a replayable proxy-regulation "
                "fixture contract with target/error policies, producer/route "
                "boundaries, budget separation, memory/no-memory lanes, "
                "perturbation/support schemas, identity/support outcome tags, "
                "ceiling algorithm, N10 handoff fields, controls, and claim "
                "flags frozen before any positive regulation probe."
            ),
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
    }
    validation["validation_digest_scope"] = {
        "included": "validation fields except generated_at, validation_digest, and git",
        "excluded": ["generated_at", "validation_digest", "git"],
        "stable_across_same_inputs": True,
    }
    validation["validation_digest"] = digest_value(
        {
            key: value
            for key, value in validation.items()
            if key not in {"generated_at", "validation_digest", "git"}
        }
    )
    return validation


def render_report(validation: dict[str, Any], manifest: dict[str, Any]) -> str:
    checks = validation["checks"]
    passed = sum(1 for value in checks.values() if value)
    total = len(checks)
    controls = validation["control_summary"]
    summary = validation["contract_summary"]
    return "\n".join(
        [
            "# N09 Iteration 2 Fixture Manifest Validation",
            "",
            f"Status: {validation['status']}",
            "",
            "Iteration 2 is contract-only. No proxy-regulation probe was run and "
            "no positive regulation evidence was generated.",
            "",
            "## Contract Summary",
            "",
            f"- Default fixture family: `{summary['default_fixture_family']}`",
            f"- Memory-shaped lane required: {summary['memory_lane_required']}",
            f"- No-memory comparator required: {summary['no_memory_comparator_required']}",
            f"- N06 packet execution inherited: {summary['n06_packet_execution_inherited']}",
            f"- N07 withdrawal baseline available: {summary['n07_withdrawal_baseline_available']}",
            f"- Oscillator fixture status: `{summary['oscillator_fixture_status']}`",
            "- Native goal-proxy regulation policy available: "
            f"{summary['native_goal_proxy_regulation_policy_available']}",
            "",
            "## Frozen Schemas",
            "",
            "- Proxy surface row schema",
            "- Target-band schema",
            "- Error signal and error policy schema",
            "- Regulation policy and response schema",
            "- Route/producer evidence contract",
            "- Packet scheduling/processing response contract",
            "- Perturbation and support-withdrawal schemas",
            "- Artifact-only replay requirements",
            "",
            "## Boundary Records",
            "",
            "- `n07_identity_support_area` is excluded from `allowed_proxy_kinds`; "
            "it remains an identity/support anchor, not a runtime-visible "
            "regulated variable.",
            "- Memory-shaped response fields attach directly to the regulation "
            "response and map N09 names to N08 `memory_policy_digest` and "
            "`memory_strength` fields.",
            "- N06 route arbitration is selection-only for N09; GPR4+ must "
            "produce N09 scheduling and processed-packet evidence.",
            "- N06 source rows do not serialize direct candidate budget "
            "predictions; missing prediction fails with "
            "`candidate_budget_prediction_missing`.",
            "- N07 withdrawal stability is not available; support withdrawal "
            "checks carry `n07_identity_withdrawal_baseline_not_available`.",
            "- N08 memory-shaped rows may be consumed only as serialized "
            "producer/policy memory evidence.",
            "- Perturbation artifacts must declare expected recovery window "
            "count and recovery success criterion.",
            "- Oscillator-return regulation is a deferred secondary fixture "
            "unless explicitly selected.",
            "",
            "## Validation Checks",
            "",
            f"Passed checks: {passed}/{total}",
            "",
            "```json",
            json.dumps(checks, indent=2, sort_keys=True),
            "```",
            "",
            "## Controls",
            "",
            "```json",
            json.dumps(controls, indent=2, sort_keys=True),
            "```",
            "",
            "## Digests",
            "",
            f"- Manifest digest: `{manifest['manifest_digest']}`",
            f"- Validation digest: `{validation['validation_digest']}`",
            f"- Manifest SHA-256: `{validation['manifest_sha256']}`",
            "",
            "## Acceptance",
            "",
            validation["acceptance"]["acceptance_statement"],
            "",
            f"Acceptance achieved: {validation['acceptance']['achieved']}",
            "",
        ]
    )


def main() -> None:
    baseline = load_json(BASELINE_PATH)
    manifest = build_manifest(baseline)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    validation = build_validation(manifest, baseline)
    OUTPUT_PATH.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(validation, manifest), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": validation["status"],
                "checks_passed": all(validation["checks"].values()),
                "manifest": rel(MANIFEST_PATH),
                "output": rel(OUTPUT_PATH),
                "report": rel(REPORT_PATH),
                "manifest_digest": manifest["manifest_digest"],
                "validation_digest": validation["validation_digest"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
