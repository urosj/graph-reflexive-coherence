#!/usr/bin/env python3
"""Build and validate the N11 Iteration 2 generalization fixture manifest."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)
BASELINE_PATH = EXPERIMENT / "outputs" / "n11_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n11_generalization_fixture_manifest_v1.json"
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_2_fixture_manifest_validation.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n11_iteration_2_fixture_manifest_validation.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "build_n11_iteration_2_fixture_manifest.py"
)

GALI_LADDER = {
    "GALI0": "no_generalization",
    "GALI1": "source_backed_transfer_inventory",
    "GALI2": "single_axis_context_transfer",
    "GALI3": "proxy_condition_transfer",
    "GALI4": "support_state_transfer",
    "GALI5": "multi_axis_bounded_transfer",
    "GALI6": "longer_horizon_generalization_candidate",
    "GALI7": "broader_general_artifact_only_agentic_like_integration_candidate",
}

TRANSFER_ROW_REQUIRED_FIELDS = [
    "transfer_row_id",
    "gali_level",
    "arc_of_becoming_classification",
    "producer_mediation_classification",
    "source_boundary",
    "source_artifacts",
    "source_artifact_digests",
    "source_reports",
    "transfer_axis",
    "transfer_policy_id",
    "transfer_policy_digest",
    "context_tag",
    "support_state_tag",
    "proxy_condition_tag",
    "source_scope_tag",
    "transfer_window_tag",
    "transfer_outcome_tag",
    "artifact_only",
    "runtime_state_used",
    "producer_scaffold_used",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "memory_budget_surface",
    "proxy_budget_surface",
    "support_budget_surface",
    "hidden_steering_used",
    "native_policy_gap",
    "primary_blocker",
    "blocked_claims",
    "claim_flags",
    "transfer_row_digest",
]

CONTEXT_TAGS = [
    "context_same_as_n10",
    "context_route_variant",
    "context_arbitration_policy_variant",
    "context_source_scope_variant",
    "context_out_of_scope",
    "context_stale",
    "context_hidden",
    "context_not_applicable",
]

SUPPORT_STATE_TAGS = [
    "support_intact_survives",
    "mild_withdrawal_survives",
    "n09_matched_withdrawal_disrupts_support",
    "explicit_restoration_recovers_support",
    "support_variant_new",
    "support_state_stale",
    "support_state_out_of_scope",
    "support_state_not_applicable",
]

PROXY_CONDITION_TAGS = [
    "proxy_same_as_n10",
    "proxy_target_band_variant",
    "proxy_perturbation_envelope_variant",
    "proxy_measurement_surface_variant",
    "proxy_out_of_envelope",
    "proxy_stale",
    "proxy_hidden",
    "proxy_not_applicable",
]

TRANSFER_WINDOW_TAGS = [
    "inventory_only",
    "single_replay_window",
    "bounded_repeated_window",
    "longer_horizon_window",
    "out_of_window",
    "not_applicable",
]

SOURCE_SCOPE_TAGS = [
    "n10_bounded_artifact_only_source",
    "n10_support_sensitive_source",
    "n10_native_contract_handoff_source",
    "source_scope_out_of_bounds",
    "source_scope_stale",
]

TRANSFER_AXES = [
    "inventory",
    "context",
    "proxy",
    "support",
    "multi_axis",
    "longer_horizon",
    "controls",
    "artifact_validator",
    "native_gap",
]

TRANSFER_OUTCOME_TAGS = [
    "no_transfer",
    "bookkeeping_only_transfer",
    "single_axis_context_transfer_candidate",
    "proxy_condition_transfer_candidate",
    "support_state_transfer_candidate",
    "multi_axis_bounded_transfer_candidate",
    "longer_horizon_generalization_candidate",
    "broader_general_artifact_only_agentic_like_integration_candidate",
    "transfer_blocked",
]

ARC_OF_BECOMING_CLASSIFICATIONS = [
    "local_observation_tag",
    "reusable_becoming_class",
    "probe_supported_capacity",
    "support_dependent_expression",
    "endogenous_precondition_candidate",
    "native_regime_expression",
    "not_applicable",
]

PRODUCER_MEDIATION_CLASSIFICATIONS = [
    "producer_mediated",
    "threshold_authorized",
    "native_route_arbitrated",
    "constitutive_native",
    "native_policy_gap",
    "not_applicable",
]

SUPPORT_MATRIX_STATES = [
    "support_intact_survives",
    "mild_withdrawal_survives",
    "n09_matched_withdrawal_disrupts_support",
    "explicit_restoration_recovers_support",
]

MULTI_AXIS_CONTEXT_VARIANTS = [
    "context_same_as_n10",
    "context_route_variant",
    "context_arbitration_policy_variant",
]

MULTI_AXIS_PROXY_VARIANTS = [
    "proxy_same_as_n10",
    "proxy_target_band_variant",
]

CONTROL_BLOCKERS = {
    "missing_n10_closeout_artifact": "missing_n10_closeout_artifact",
    "source_artifact_digest_mismatch": "source_artifact_digest_mismatch",
    "hidden_context_substitution": "hidden_context_substitution_blocked",
    "stale_context": "stale_context_blocked",
    "stale_support_state": "stale_support_state_blocked",
    "stale_proxy_state": "stale_proxy_state_blocked",
    "out_of_envelope_proxy": "out_of_envelope_proxy_blocked",
    "support_disrupted_but_generalization_allowed": (
        "support_disrupted_but_generalization_allowed"
    ),
    "restoration_required_but_missing": "restoration_required_but_missing",
    "budget_surface_ambiguity": "budget_surface_ambiguity",
    "node_plus_packet_budget_discontinuity": (
        "node_plus_packet_budget_discontinuity"
    ),
    "hidden_experiment_side_steering": "hidden_experiment_side_steering",
    "native_relabel_without_phase8": "native_relabel_without_phase8_blocked",
    "claim_promotion": "claim_promotion_blocked",
    "a7_by_inheritance": "a7_by_inheritance_blocked",
    "gali7_by_inheritance": "gali7_by_inheritance_blocked",
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


def with_digest(record: dict[str, Any], digest_field: str) -> dict[str, Any]:
    result = dict(record)
    result[digest_field] = digest_value(
        {key: value for key, value in result.items() if key != digest_field}
    )
    return result


def manifest_digest(manifest: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in manifest.items() if key != "manifest_digest"})


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "validation_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {
        key: False
        for key in sorted(baseline["n11_baseline"]["claim_flags"])
    }


def validate_source_digests(baseline: dict[str, Any]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    all_match = True
    for key, record in baseline["source_artifacts"].items():
        path = ROOT / record["path"]
        current = digest_file(path)
        matches = current == record["sha256"]
        all_match = all_match and matches
        rows[key] = {
            "path": record["path"],
            "expected_sha256": record["sha256"],
            "current_sha256": current,
            "matches": matches,
        }
    return {"all_match": all_match, "rows": rows}


def build_manifest(baseline: dict[str, Any]) -> dict[str, Any]:
    claim_flags = false_claim_flags(baseline)
    source_keys = sorted(baseline["source_artifacts"])

    transfer_policy = with_digest(
        {
            "transfer_policy_id": "n11_artifact_only_generalization_transfer_policy_v1",
            "contract_only": True,
            "artifact_only_required": True,
            "runtime_state_fallback_allowed": False,
            "hidden_experiment_side_steering_allowed": False,
            "claim_promotion_allowed": False,
            "a7_by_inheritance_allowed": False,
            "gali7_by_inheritance_allowed": False,
            "n10_source_boundary_required": True,
            "source_digest_validation_required": True,
            "support_disruption_must_block_or_downgrade": True,
            "explicit_restoration_required_after_disruption": True,
            "node_plus_packet_budget_error_required_when_same_run": 0.0,
            "memory_budget_surface_separate": True,
            "proxy_budget_surface_separate": True,
            "support_budget_surface_separate": True,
            "positive_generalization_probe_run": False,
        },
        "transfer_policy_digest",
    )

    fixture_lanes = [
        {
            "lane_id": "context_same_as_n10_reference",
            "planned_iteration": 3,
            "hypothesis": "A_artifact_only_generalization",
            "transfer_axis": "context",
            "context_tag": "context_same_as_n10",
            "support_state_tag": "support_intact_survives",
            "proxy_condition_tag": "proxy_same_as_n10",
            "expected_role": "reference_replay_before_context_variation",
        },
        {
            "lane_id": "context_route_variant_replay",
            "planned_iteration": 3,
            "hypothesis": "A_artifact_only_generalization",
            "transfer_axis": "context",
            "context_tag": "context_route_variant",
            "support_state_tag": "support_intact_survives",
            "proxy_condition_tag": "proxy_same_as_n10",
            "expected_role": "single_axis_context_transfer_candidate_or_blocked",
        },
        {
            "lane_id": "context_arbitration_policy_variant_replay",
            "planned_iteration": 3,
            "hypothesis": "A_artifact_only_generalization",
            "transfer_axis": "context",
            "context_tag": "context_arbitration_policy_variant",
            "support_state_tag": "support_intact_survives",
            "proxy_condition_tag": "proxy_same_as_n10",
            "expected_role": (
                "arbitration_policy_context_transfer_candidate_or_blocked"
            ),
        },
        {
            "lane_id": "proxy_target_band_variant_replay",
            "planned_iteration": 4,
            "hypothesis": "A_artifact_only_generalization",
            "transfer_axis": "proxy",
            "context_tag": "context_same_as_n10",
            "support_state_tag": "support_intact_survives",
            "proxy_condition_tag": "proxy_target_band_variant",
            "expected_role": "proxy_condition_transfer_candidate_or_blocked",
        },
        {
            "lane_id": "support_state_transfer_matrix",
            "planned_iteration": 5,
            "hypothesis": "B_generalization_envelope",
            "transfer_axis": "support",
            "context_tag": "context_same_as_n10",
            "support_state_tag": "support_variant_new",
            "proxy_condition_tag": "proxy_same_as_n10",
            "matrix_states": SUPPORT_MATRIX_STATES,
            "expected_role": "support_state_transfer_candidate_or_blocked",
        },
        {
            "lane_id": "multi_axis_context_proxy_support_matrix",
            "planned_iteration": 6,
            "hypothesis": "B_generalization_envelope",
            "transfer_axis": "multi_axis",
            "context_tag": "context_route_variant",
            "support_state_tag": "support_variant_new",
            "proxy_condition_tag": "proxy_target_band_variant",
            "matrix_spec": {
                "context_variants": MULTI_AXIS_CONTEXT_VARIANTS,
                "proxy_condition_variants": MULTI_AXIS_PROXY_VARIANTS,
                "support_state_variants": SUPPORT_MATRIX_STATES,
                "expected_minimum_row_count": (
                    len(MULTI_AXIS_CONTEXT_VARIANTS)
                    * len(MULTI_AXIS_PROXY_VARIANTS)
                    * len(SUPPORT_MATRIX_STATES)
                ),
                "matrix_expansion_required": True,
            },
            "expected_role": "multi_axis_bounded_transfer_candidate_or_blocked",
        },
        {
            "lane_id": "longer_horizon_generalization_window",
            "planned_iteration": 7,
            "hypothesis": "B_generalization_envelope",
            "transfer_axis": "longer_horizon",
            "context_tag": "context_route_variant",
            "support_state_tag": "mild_withdrawal_survives",
            "proxy_condition_tag": "proxy_perturbation_envelope_variant",
            "transfer_window_tag": "longer_horizon_window",
            "window_spec": {
                "reference_n10_bounded_window_count": baseline[
                    "source_inventory"
                ]["n10_hypothesis_a_closeout"]["bounded_window_count"],
                "minimum_extended_window_count": baseline["source_inventory"][
                    "n10_hypothesis_a_closeout"
                ]["bounded_window_count"]
                * 2,
                "boundedness_required": (
                    "node_plus_packet_budget_error remains zero or the row "
                    "is blocked; source-current status must remain true; "
                    "support, proxy, and transfer trends must remain bounded "
                    "or be explicitly downgraded"
                ),
                "trend_fields_required": [
                    "source_current_status_by_window",
                    "node_plus_packet_budget_error_by_window",
                    "support_trend",
                    "proxy_trend",
                    "transfer_stability_trend",
                    "degradation_or_recovery_pattern",
                ],
            },
            "expected_role": "longer_horizon_generalization_candidate_or_blocked",
        },
        {
            "lane_id": "hidden_stale_out_of_envelope_claim_controls",
            "planned_iteration": 8,
            "hypothesis": "A_B_claim_boundary",
            "transfer_axis": "controls",
            "context_tag": "context_hidden",
            "support_state_tag": "support_state_stale",
            "proxy_condition_tag": "proxy_out_of_envelope",
            "expected_role": "distinct_fail_closed_controls",
            "is_control_lane": True,
        },
        {
            "lane_id": "artifact_only_generalization_validator",
            "planned_iteration": 9,
            "hypothesis": "A_B_replay_validator",
            "transfer_axis": "artifact_validator",
            "context_tag": "context_not_applicable",
            "support_state_tag": "support_state_not_applicable",
            "proxy_condition_tag": "proxy_not_applicable",
            "expected_role": "artifact_only_replay_validator",
        },
    ]

    exemplar_row = with_digest(
        {
            "transfer_row_id": "n11_i2_schema_validation_exemplar_not_evidence",
            "gali_level": "GALI1",
            "arc_of_becoming_classification": "local_observation_tag",
            "producer_mediation_classification": "not_applicable",
            "source_boundary": "N10_iteration_15_closeout",
            "source_artifacts": {
                key: baseline["source_artifacts"][key]["path"] for key in source_keys
            },
            "source_artifact_digests": {
                key: baseline["source_artifacts"][key]["sha256"]
                for key in source_keys
            },
            "source_reports": {
                key: baseline["source_reports"][key]["path"] for key in source_keys
            },
            "transfer_axis": "inventory",
            "transfer_policy_id": transfer_policy["transfer_policy_id"],
            "transfer_policy_digest": transfer_policy["transfer_policy_digest"],
            "context_tag": "context_same_as_n10",
            "support_state_tag": "support_intact_survives",
            "proxy_condition_tag": "proxy_same_as_n10",
            "source_scope_tag": "n10_bounded_artifact_only_source",
            "transfer_window_tag": "inventory_only",
            "transfer_outcome_tag": "bookkeeping_only_transfer",
            "artifact_only": True,
            "runtime_state_used": False,
            "producer_scaffold_used": False,
            "node_plus_packet_budget_before": None,
            "node_plus_packet_budget_after": None,
            "node_plus_packet_budget_error": None,
            "memory_budget_surface": "separate_not_evaluated_in_schema_validation",
            "proxy_budget_surface": "separate_not_evaluated_in_schema_validation",
            "support_budget_surface": "separate_not_evaluated_in_schema_validation",
            "hidden_steering_used": False,
            "native_policy_gap": baseline["n11_baseline"]["primary_native_blockers"],
            "primary_blocker": None,
            "blocked_claims": baseline["n11_baseline"]["blocked_claims"],
            "claim_flags": claim_flags,
            "example_only_not_evidence": True,
            "exemplar_note": (
                "Schema-populated bookkeeping example only. It demonstrates "
                "source linkage and tag shape, but does not establish context, "
                "proxy, support, multi-axis, longer-horizon, A7, or GALI7 "
                "generalization evidence."
            ),
        },
        "transfer_row_digest",
    )

    manifest: dict[str, Any] = {
        "schema": "n11_generalization_fixture_manifest_v1",
        "manifest_kind": "contract_only_no_positive_generalization_probe",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "baseline_artifact": {
            "path": rel(BASELINE_PATH),
            "inventory_digest": baseline["inventory_digest"],
            "sha256": digest_file(BASELINE_PATH),
        },
        "source_requirements": {
            "required_n10_source_boundary": "N10_iteration_15_closeout",
            "required_source_artifact_keys": source_keys,
            "source_digest_validation_required": True,
            "source_report_validation_required": True,
            "visual_references_are_not_evidence": True,
            "missing_n10_closeout_must_fail": True,
        },
        "transfer_policy": transfer_policy,
        "gali_ladder": GALI_LADDER,
        "transfer_row_required_fields": TRANSFER_ROW_REQUIRED_FIELDS,
        "allowed_values": {
            "gali_level": list(GALI_LADDER),
            "arc_of_becoming_classification": ARC_OF_BECOMING_CLASSIFICATIONS,
            "producer_mediation_classification": PRODUCER_MEDIATION_CLASSIFICATIONS,
            "transfer_axis": TRANSFER_AXES,
            "context_tag": CONTEXT_TAGS,
            "support_state_tag": SUPPORT_STATE_TAGS,
            "proxy_condition_tag": PROXY_CONDITION_TAGS,
            "source_scope_tag": SOURCE_SCOPE_TAGS,
            "transfer_window_tag": TRANSFER_WINDOW_TAGS,
            "transfer_outcome_tag": TRANSFER_OUTCOME_TAGS,
        },
        "fixture_lanes": fixture_lanes,
        "support_state_matrix_spec": {
            "matrix_states": SUPPORT_MATRIX_STATES,
            "coverage_required_in_iteration_5": True,
            "disrupted_support_must_block_without_restoration": True,
            "explicit_restoration_must_preserve_disruption_history": True,
        },
        "multi_axis_matrix_spec": {
            "context_variants": MULTI_AXIS_CONTEXT_VARIANTS,
            "proxy_condition_variants": MULTI_AXIS_PROXY_VARIANTS,
            "support_state_variants": SUPPORT_MATRIX_STATES,
            "expected_minimum_row_count": (
                len(MULTI_AXIS_CONTEXT_VARIANTS)
                * len(MULTI_AXIS_PROXY_VARIANTS)
                * len(SUPPORT_MATRIX_STATES)
            ),
            "matrix_expansion_required_in_iteration_6": True,
        },
        "longer_horizon_window_spec": {
            "reference_n10_bounded_window_count": baseline["source_inventory"][
                "n10_hypothesis_a_closeout"
            ]["bounded_window_count"],
            "minimum_extended_window_count": baseline["source_inventory"][
                "n10_hypothesis_a_closeout"
            ]["bounded_window_count"]
            * 2,
            "trend_fields_required": [
                "source_current_status_by_window",
                "node_plus_packet_budget_error_by_window",
                "support_trend",
                "proxy_trend",
                "transfer_stability_trend",
                "degradation_or_recovery_pattern",
            ],
            "pass_fail_alone_sufficient": False,
        },
        "artifact_validator_architecture": {
            "validator_shape": "single_script_with_separate_validation_passes",
            "required_passes": [
                "source_artifact_digest_pass",
                "transfer_row_schema_pass",
                "context_proxy_support_matrix_pass",
                "longer_horizon_window_pass",
                "negative_control_pass",
                "budget_surface_pass",
                "claim_boundary_pass",
            ],
            "runtime_state_used": False,
        },
        "budget_boundaries": {
            "node_plus_packet_budget_required_for_same_run": True,
            "node_plus_packet_budget_error_required_when_same_run": 0.0,
            "source_artifact_budget_errors_must_be_zero_or_explicitly_blocked": True,
            "cross_artifact_budget_continuity_claim_allowed": False,
            "memory_budget_surface_must_remain_separate": True,
            "proxy_budget_surface_must_remain_separate": True,
            "support_budget_surface_must_remain_separate": True,
            "support_metrics_are_evidence_tags_not_budget_surfaces": True,
        },
        "control_blockers": CONTROL_BLOCKERS,
        "negative_control_contract": {
            "missing_n10_closeout_artifact": CONTROL_BLOCKERS[
                "missing_n10_closeout_artifact"
            ],
            "source_artifact_digest_mismatch": CONTROL_BLOCKERS[
                "source_artifact_digest_mismatch"
            ],
            "claim_promotion_fields": CONTROL_BLOCKERS["claim_promotion"],
            "hidden_context_substitution": CONTROL_BLOCKERS[
                "hidden_context_substitution"
            ],
            "stale_context": CONTROL_BLOCKERS["stale_context"],
            "stale_support_state": CONTROL_BLOCKERS["stale_support_state"],
            "stale_proxy_state": CONTROL_BLOCKERS["stale_proxy_state"],
            "out_of_envelope_proxy": CONTROL_BLOCKERS["out_of_envelope_proxy"],
            "support_disrupted_but_generalization_allowed": CONTROL_BLOCKERS[
                "support_disrupted_but_generalization_allowed"
            ],
            "restoration_required_but_missing": CONTROL_BLOCKERS[
                "restoration_required_but_missing"
            ],
            "budget_surface_ambiguity": CONTROL_BLOCKERS[
                "budget_surface_ambiguity"
            ],
            "node_plus_packet_budget_discontinuity": CONTROL_BLOCKERS[
                "node_plus_packet_budget_discontinuity"
            ],
            "hidden_experiment_side_steering": CONTROL_BLOCKERS[
                "hidden_experiment_side_steering"
            ],
            "native_relabel_without_phase8": CONTROL_BLOCKERS[
                "native_relabel_without_phase8"
            ],
            "a7_by_inheritance": CONTROL_BLOCKERS["a7_by_inheritance"],
            "gali7_by_inheritance": CONTROL_BLOCKERS["gali7_by_inheritance"],
        },
        "non_actions": {
            "positive_generalization_probe_run": False,
            "a7_supported_by_iteration_2": False,
            "gali7_supported_by_iteration_2": False,
            "runtime_state_used": False,
            "src_changes_required": False,
            "claim_promotion_allowed": False,
            "native_support_opened": False,
        },
        "claim_flags": claim_flags,
        "schema_validation_exemplar": exemplar_row,
    }
    manifest["manifest_digest"] = manifest_digest(manifest)
    return manifest


def validate_manifest(manifest: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    source_validation = validate_source_digests(baseline)
    exemplar = manifest["schema_validation_exemplar"]
    missing_fields = [
        field for field in TRANSFER_ROW_REQUIRED_FIELDS if field not in exemplar
    ]
    lane_tag_checks = []
    for lane in manifest["fixture_lanes"]:
        lane_tag_checks.append(
            lane["transfer_axis"] in TRANSFER_AXES
            and lane["context_tag"] in CONTEXT_TAGS
            and lane["support_state_tag"] in SUPPORT_STATE_TAGS
            and lane["proxy_condition_tag"] in PROXY_CONDITION_TAGS
        )

    checks = {
        "manifest_digest_present": bool(manifest.get("manifest_digest")),
        "baseline_inventory_digest_pinned": manifest["baseline_artifact"][
            "inventory_digest"
        ]
        == baseline["inventory_digest"],
        "source_artifact_digests_validate": source_validation["all_match"],
        "transfer_row_required_fields_complete": not missing_fields,
        "gali_ladder_frozen": set(GALI_LADDER)
        == set(manifest["allowed_values"]["gali_level"]),
        "arc_of_becoming_classifications_frozen": set(
            ARC_OF_BECOMING_CLASSIFICATIONS
        )
        == set(manifest["allowed_values"]["arc_of_becoming_classification"]),
        "producer_mediation_classifications_frozen": set(
            PRODUCER_MEDIATION_CLASSIFICATIONS
        )
        == set(manifest["allowed_values"]["producer_mediation_classification"]),
        "context_tags_frozen": set(CONTEXT_TAGS)
        == set(manifest["allowed_values"]["context_tag"]),
        "support_state_tags_frozen": set(SUPPORT_STATE_TAGS)
        == set(manifest["allowed_values"]["support_state_tag"]),
        "proxy_condition_tags_frozen": set(PROXY_CONDITION_TAGS)
        == set(manifest["allowed_values"]["proxy_condition_tag"]),
        "source_scope_tags_frozen": set(SOURCE_SCOPE_TAGS)
        == set(manifest["allowed_values"]["source_scope_tag"]),
        "transfer_window_tags_frozen": set(TRANSFER_WINDOW_TAGS)
        == set(manifest["allowed_values"]["transfer_window_tag"]),
        "transfer_outcome_tags_frozen": set(TRANSFER_OUTCOME_TAGS)
        == set(manifest["allowed_values"]["transfer_outcome_tag"]),
        "control_blockers_frozen": set(CONTROL_BLOCKERS)
        == set(manifest["control_blockers"]),
        "fixture_lane_tags_valid": all(lane_tag_checks),
        "fixture_lanes_cover_iterations_3_to_9": sorted(
            set(lane["planned_iteration"] for lane in manifest["fixture_lanes"])
        )
        == [3, 4, 5, 6, 7, 8, 9],
        "context_transfer_lane_declared": any(
            lane["transfer_axis"] == "context" for lane in manifest["fixture_lanes"]
        ),
        "context_arbitration_policy_variant_lane_declared": any(
            lane.get("context_tag") == "context_arbitration_policy_variant"
            for lane in manifest["fixture_lanes"]
        ),
        "proxy_transfer_lane_declared": any(
            lane["transfer_axis"] == "proxy" for lane in manifest["fixture_lanes"]
        ),
        "support_transfer_lane_declared": any(
            lane["transfer_axis"] == "support" for lane in manifest["fixture_lanes"]
        ),
        "support_transfer_matrix_states_declared": set(
            manifest["support_state_matrix_spec"]["matrix_states"]
        )
        == set(SUPPORT_MATRIX_STATES),
        "multi_axis_lane_declared": any(
            lane["transfer_axis"] == "multi_axis"
            for lane in manifest["fixture_lanes"]
        ),
        "multi_axis_matrix_spec_declared": manifest["multi_axis_matrix_spec"][
            "expected_minimum_row_count"
        ]
        == (
            len(MULTI_AXIS_CONTEXT_VARIANTS)
            * len(MULTI_AXIS_PROXY_VARIANTS)
            * len(SUPPORT_MATRIX_STATES)
        ),
        "longer_horizon_lane_declared": any(
            lane["transfer_axis"] == "longer_horizon"
            for lane in manifest["fixture_lanes"]
        ),
        "longer_horizon_window_spec_declared": manifest[
            "longer_horizon_window_spec"
        ]["minimum_extended_window_count"]
        > manifest["longer_horizon_window_spec"]["reference_n10_bounded_window_count"],
        "artifact_validator_architecture_declared": manifest[
            "artifact_validator_architecture"
        ]["runtime_state_used"]
        is False,
        "control_lane_declared": any(
            lane.get("is_control_lane") is True for lane in manifest["fixture_lanes"]
        ),
        "artifact_validator_lane_declared": any(
            lane["transfer_axis"] == "artifact_validator"
            for lane in manifest["fixture_lanes"]
        ),
        "missing_n10_closeout_rejected": manifest["negative_control_contract"][
            "missing_n10_closeout_artifact"
        ]
        == "missing_n10_closeout_artifact",
        "negative_control_contract_covers_required_controls": {
            "stale_context",
            "hidden_experiment_side_steering",
            "node_plus_packet_budget_discontinuity",
            "budget_surface_ambiguity",
        }.issubset(set(manifest["negative_control_contract"])),
        "claim_promotion_fields_rejected": manifest["negative_control_contract"][
            "claim_promotion_fields"
        ]
        == "claim_promotion_blocked",
        "a7_by_inheritance_rejected": manifest["negative_control_contract"][
            "a7_by_inheritance"
        ]
        == "a7_by_inheritance_blocked",
        "gali7_by_inheritance_rejected": manifest["negative_control_contract"][
            "gali7_by_inheritance"
        ]
        == "gali7_by_inheritance_blocked",
        "claim_flags_all_false": all(
            value is False for value in manifest["claim_flags"].values()
        ),
        "exemplar_is_not_evidence": exemplar["example_only_not_evidence"] is True,
        "no_positive_probe_run": manifest["non_actions"][
            "positive_generalization_probe_run"
        ]
        is False,
        "a7_not_supported_by_iteration_2": manifest["non_actions"][
            "a7_supported_by_iteration_2"
        ]
        is False,
        "gali7_not_supported_by_iteration_2": manifest["non_actions"][
            "gali7_supported_by_iteration_2"
        ]
        is False,
        "src_clean_for_iteration_2": git_status_short("src") == "",
    }

    return {
        "source_digest_validation": source_validation,
        "schema_validation": {
            "exemplar_row_valid": not missing_fields,
            "missing_required_fields": missing_fields,
            "exemplar_row_is_evidence": False,
            "lane_tag_checks": lane_tag_checks,
        },
        "checks": checks,
    }


def build_output(manifest: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    checks = validation["checks"]
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 2 passes if the N11 generalization schema and fixture "
            "manifest are frozen before any transfer probe, and the manifest "
            "validates source artifacts, tags, controls, and claim boundaries "
            "without producing positive evidence."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_2_fixture_manifest_validation_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 2,
        "purpose": "generalization_schema_fixture_manifest_contract_only",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "manifest_path": rel(MANIFEST_PATH),
        "manifest_digest": manifest["manifest_digest"],
        "manifest_sha256": digest_file(MANIFEST_PATH),
        "baseline_path": rel(BASELINE_PATH),
        "baseline_inventory_digest": manifest["baseline_artifact"][
            "inventory_digest"
        ],
        "frozen_schema": {
            "gali_ladder": manifest["gali_ladder"],
            "transfer_row_required_fields": TRANSFER_ROW_REQUIRED_FIELDS,
            "allowed_values": manifest["allowed_values"],
            "control_blockers": manifest["control_blockers"],
        },
        "fixture_lanes": manifest["fixture_lanes"],
        "support_state_matrix_spec": manifest["support_state_matrix_spec"],
        "multi_axis_matrix_spec": manifest["multi_axis_matrix_spec"],
        "longer_horizon_window_spec": manifest["longer_horizon_window_spec"],
        "artifact_validator_architecture": manifest["artifact_validator_architecture"],
        "budget_boundaries": manifest["budget_boundaries"],
        "negative_control_contract": manifest["negative_control_contract"],
        "non_actions": manifest["non_actions"],
        "claim_flags": manifest["claim_flags"],
        "source_digest_validation": validation["source_digest_validation"],
        "schema_validation": validation["schema_validation"],
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "3_route_context_transfer_replay",
    }
    output["validation_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any], manifest: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 2 Generalization Schema And Fixture Manifest",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 2 froze the N11 transfer schema and fixture manifest before",
        "any positive generalization probe. The manifest is contract-only; it",
        "does not support A7 or GALI7 by itself.",
        "",
        "```text",
        "positive generalization probe run = false",
        "A7 supported by Iteration 2 = false",
        "GALI7 supported by Iteration 2 = false",
        "runtime state used = false",
        "claim promotion allowed = false",
        "```",
        "",
        "## Manifest",
        "",
        f"- path: `{output['manifest_path']}`",
        f"- manifest digest: `{output['manifest_digest']}`",
        f"- manifest SHA-256: `{output['manifest_sha256']}`",
        "",
        "## Frozen GALI Ladder",
        "",
        "```json",
        json.dumps(output["frozen_schema"]["gali_ladder"], indent=2, sort_keys=True),
        "```",
        "",
        "## Frozen Tags",
        "",
        "```json",
        json.dumps(output["frozen_schema"]["allowed_values"], indent=2, sort_keys=True),
        "```",
        "",
        "## Fixture Lanes",
        "",
        "```json",
        json.dumps(output["fixture_lanes"], indent=2, sort_keys=True),
        "```",
        "",
        "## Matrix And Window Specs",
        "",
        "Support-state matrix:",
        "",
        "```json",
        json.dumps(output["support_state_matrix_spec"], indent=2, sort_keys=True),
        "```",
        "",
        "Multi-axis matrix:",
        "",
        "```json",
        json.dumps(output["multi_axis_matrix_spec"], indent=2, sort_keys=True),
        "```",
        "",
        "Longer-horizon window:",
        "",
        "```json",
        json.dumps(output["longer_horizon_window_spec"], indent=2, sort_keys=True),
        "```",
        "",
        "Artifact-validator architecture:",
        "",
        "```json",
        json.dumps(
            output["artifact_validator_architecture"], indent=2, sort_keys=True
        ),
        "```",
        "",
        "## Negative Control Contract",
        "",
        "```json",
        json.dumps(output["negative_control_contract"], indent=2, sort_keys=True),
        "```",
        "",
        "## Schema Validation",
        "",
        "```json",
        json.dumps(output["schema_validation"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
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
        "Validation digest:",
        "",
        "```text",
        output["validation_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    baseline = load_json(BASELINE_PATH)
    manifest = build_manifest(baseline)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    validation = validate_manifest(manifest, baseline)
    output = build_output(manifest, validation)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output, manifest), encoding="utf-8")
    print(f"wrote {rel(MANIFEST_PATH)}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {output['status']}")
    print(f"validation_digest {output['validation_digest']}")


if __name__ == "__main__":
    main()
