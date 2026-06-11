#!/usr/bin/env python3
"""Build and validate the N10 Iteration 2 integration fixture manifest.

Iteration 2 is contract-only. It freezes the integration row schema, support
tags, source requirements, controls, and claim boundary before any positive
N10 integration probe is run.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
BASELINE_PATH = EXPERIMENT / "outputs" / "n10_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n10_integration_fixture_manifest_v1.json"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n10_iteration_2_fixture_manifest_validation.json"
REPORT_PATH = EXPERIMENT / "reports" / "n10_iteration_2_fixture_manifest_validation.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "build_n10_iteration_2_fixture_manifest.py"
)


INTEGRATION_ROW_REQUIRED_FIELDS = [
    "integration_row_id",
    "integration_level",
    "n10_category_level",
    "integration_policy_id",
    "integration_policy_digest",
    "event_time_key",
    "scheduler_event_index",
    "source_experiment_ids",
    "source_artifacts",
    "source_reports",
    "source_artifact_digests",
    "route_choice_artifact",
    "route_choice_digest",
    "memory_affordance_artifact",
    "memory_affordance_digest",
    "identity_support_artifact",
    "identity_support_digest",
    "goal_proxy_regulation_artifact",
    "goal_proxy_regulation_digest",
    "support_state_tag",
    "route_context_tag",
    "memory_scope_tag",
    "regulation_scope_tag",
    "integration_outcome_tag",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "memory_budget_surface",
    "proxy_budget_surface",
    "artifact_only",
    "runtime_state_used",
    "producer_scaffold_used",
    "native_policy_gap",
    "blocked_claims",
    "claim_flags",
    "integration_row_digest",
]

N10_CATEGORY_LADDER = {
    "ALI0": "no_integration_inventory_schema_or_external_juxtaposition_only",
    "ALI1": "source_backed_bookkeeping_composition_schema_valid_no_causal_replay",
    "ALI2": "support_aware_regulation_replay",
    "ALI3": "support_sensitive_regulation_with_disruption_and_restoration_controls",
    "ALI4": "route_memory_regulation_composition",
    "ALI5": "bounded_repeated_integration",
    "ALI6": "bounded_artifact_only_agentic_like_integration_candidate",
}

SUPPORT_STATE_TAGS = [
    "support_intact_survives",
    "mild_withdrawal_survives",
    "n09_matched_withdrawal_disrupts_support",
    "explicit_restoration_recovers_support",
    "support_state_not_applicable",
]

SOURCE_SUPPORT_OUTCOME_MAP = {
    "support_intact_bounded_exchange_reference": "support_intact_survives",
    "support_withdrawal_survival_baseline": "mild_withdrawal_survives",
    "support_disrupted_by_withdrawal_without_restoration": (
        "n09_matched_withdrawal_disrupts_support"
    ),
    "explicit_restoration_recovers_support_survival_baseline": (
        "explicit_restoration_recovers_support"
    ),
}

ROUTE_CONTEXT_TAGS = [
    "route_context_source_backed",
    "route_context_selection_only",
    "route_context_stale",
    "route_context_missing",
    "route_context_not_applicable",
]

MEMORY_SCOPE_TAGS = [
    "artifact_only_serialized_producer_policy_route_memory_or_trail",
    "native_geometry_design_direction_only",
    "memory_scope_missing",
    "memory_scope_stale",
    "memory_scope_not_applicable",
]

REGULATION_SCOPE_TAGS = [
    "artifact_only_goal_proxy_regulation_candidate",
    "native_substrate_mediated_goal_proxy_regulation_design_candidate",
    "regulation_scope_missing",
    "regulation_scope_stale",
    "native_policy_gap",
]

INTEGRATION_OUTCOME_TAGS = [
    "bookkeeping_only",
    "support_aware_regulation_candidate",
    "memory_shaped_support_aware_regulation_candidate",
    "route_memory_regulation_composition_candidate",
    "support_disruption_blocked_integration",
    "restoration_gated_integration_candidate",
    "bounded_artifact_only_agentic_like_integration_candidate",
    "native_policy_gap",
]

CONTROL_BLOCKERS = {
    "missing_route_choice_artifact": "missing_route_choice_artifact",
    "missing_memory_affordance_artifact": "missing_memory_affordance_artifact",
    "missing_identity_support_artifact": "missing_identity_support_artifact",
    "missing_goal_proxy_regulation_artifact": "missing_goal_proxy_regulation_artifact",
    "source_artifact_digest_mismatch": "source_artifact_digest_mismatch",
    "stale_route_context": "stale_route_context",
    "stale_memory_surface": "stale_memory_surface",
    "stale_identity_support_baseline": "stale_identity_support_baseline",
    "support_disrupted_but_integration_allowed": (
        "support_disrupted_but_integration_allowed"
    ),
    "restoration_required_but_missing": "restoration_required_but_missing",
    "hidden_experiment_side_steering": "hidden_experiment_side_steering",
    "producer_direct_mutation": "producer_direct_mutation_blocked",
    "budget_surface_ambiguity": "budget_surface_ambiguity",
    "node_plus_packet_budget_discontinuity": (
        "node_plus_packet_budget_discontinuity"
    ),
    "artifact_only_replay_missing_link": "artifact_only_replay_missing_link",
    "claim_promotion": "claim_promotion_blocked",
    "agency_overclaim": "agency_overclaim_blocked",
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
    flags = baseline["claim_boundary"]["claim_flags"]
    return {key: False for key in sorted(flags)}


def with_digest(record: dict[str, Any], digest_field: str) -> dict[str, Any]:
    result = dict(record)
    result[digest_field] = digest_value(
        {key: value for key, value in result.items() if key != digest_field}
    )
    return result


def manifest_digest(manifest: dict[str, Any]) -> str:
    return digest_value({k: v for k, v in manifest.items() if k != "manifest_digest"})


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "validation_digest", "git"}
    return digest_value({k: v for k, v in output.items() if k not in excluded})


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
    support_lanes = baseline["source_inventory"]["n07_iteration_13"]["support_lanes"]

    integration_policy = with_digest(
        {
            "integration_policy_id": "n10_bounded_artifact_only_integration_policy_v1",
            "contract_only": True,
            "artifact_only_required": True,
            "runtime_state_fallback_allowed": False,
            "hidden_experiment_side_steering_allowed": False,
            "producer_direct_mutation_allowed": False,
            "claim_promotion_allowed": False,
            "source_digest_validation_required": True,
            "support_disruption_must_block_or_downgrade": True,
            "explicit_restoration_required_after_disruption": True,
            "node_plus_packet_budget_error_required": 0.0,
            "memory_budget_surface_separate": True,
            "proxy_budget_surface_separate": True,
            "n10_positive_probe_run": False,
        },
        "integration_policy_digest",
    )

    fixture_lanes = [
        {
            "lane_id": "support_intact_regulation_replay",
            "planned_iteration": 3,
            "hypothesis": "A_with_B_support_gate",
            "source_support_lane_id": "support_intact_reference",
            "required_support_state_tag": "support_intact_survives",
            "expected_role": "support_aware_regulation_candidate",
        },
        {
            "lane_id": "mild_withdrawal_survival_replay",
            "planned_iteration": 4,
            "hypothesis": "B_support_sensitivity",
            "source_support_lane_id": "mild_support_weakening",
            "required_support_state_tag": "mild_withdrawal_survives",
            "expected_role": "support_aware_regulation_candidate_or_downgrade",
        },
        {
            "lane_id": "disrupted_support_control",
            "planned_iteration": 5,
            "hypothesis": "B_support_sensitivity",
            "source_support_lane_id": "n09_matched_partial_support_withdrawal",
            "required_support_state_tag": "n09_matched_withdrawal_disrupts_support",
            "expected_role": "support_disruption_blocked_integration",
        },
        {
            "lane_id": "explicit_restoration_replay",
            "planned_iteration": 6,
            "hypothesis": "B_support_sensitivity",
            "source_support_lane_id": "restored_after_n09_partial_withdrawal",
            "required_support_state_tag": "explicit_restoration_recovers_support",
            "expected_role": "restoration_gated_integration_candidate",
        },
        {
            "lane_id": "route_memory_regulation_composition",
            "planned_iteration": 7,
            "hypothesis": "A_bounded_artifact_only_integration",
            "source_support_lane_id": "support_intact_reference",
            "required_support_state_tag": "support_intact_survives",
            "required_route_context_tag": "route_context_selection_only",
            "route_context_constraint": "N06_SC6_is_selection_only_pre_topology_scope",
            "expected_role": "route_memory_regulation_composition_candidate",
        },
        {
            "lane_id": "bounded_repeated_integration",
            "planned_iteration": 8,
            "hypothesis": "A_bounded_artifact_only_integration",
            "source_support_lane_id": "support_intact_reference",
            "required_support_state_tag": "support_intact_survives",
            "required_route_context_tag": "route_context_selection_only",
            "route_context_constraint": "N06_SC6_is_selection_only_pre_topology_scope",
            "expected_role": "bounded_artifact_only_agentic_like_integration_candidate",
        },
        {
            "lane_id": "bounded_repeated_integration_mild_withdrawal_companion",
            "planned_iteration": 8,
            "hypothesis": "A_with_B_support_gate_a5_companion",
            "source_support_lane_id": "mild_support_weakening",
            "required_support_state_tag": "mild_withdrawal_survives",
            "required_route_context_tag": "route_context_selection_only",
            "route_context_constraint": "N06_SC6_is_selection_only_pre_topology_scope",
            "expected_role": "bounded_repeated_integration_a5_relevant_companion_or_downgrade",
        },
    ]

    exemplar_row = with_digest(
        {
            "integration_row_id": "n10_i2_schema_validation_exemplar_not_evidence",
            "integration_level": "A0",
            "n10_category_level": "ALI1",
            "integration_policy_id": integration_policy["integration_policy_id"],
            "integration_policy_digest": integration_policy[
                "integration_policy_digest"
            ],
            "event_time_key": "schema_validation_only",
            "scheduler_event_index": None,
            "source_experiment_ids": ["N05", "N06", "N07", "N08", "N09"],
            "source_artifacts": {
                key: baseline["source_artifacts"][key]["path"] for key in source_keys
            },
            "source_reports": {
                key: baseline["source_reports"][key]["path"] for key in source_keys
            },
            "source_artifact_digests": {
                key: baseline["source_artifacts"][key]["sha256"]
                for key in source_keys
            },
            "route_choice_artifact": "n06_closeout",
            "route_choice_digest": baseline["source_artifacts"]["n06_closeout"][
                "sha256"
            ],
            "memory_affordance_artifact": "n08_hypothesis_a_closeout",
            "memory_affordance_digest": baseline["source_artifacts"][
                "n08_hypothesis_a_closeout"
            ]["sha256"],
            "identity_support_artifact": "n07_withdrawal_baseline",
            "identity_support_digest": baseline["source_artifacts"][
                "n07_withdrawal_baseline"
            ]["sha256"],
            "goal_proxy_regulation_artifact": "n09_hypothesis_a_closeout",
            "goal_proxy_regulation_digest": baseline["source_artifacts"][
                "n09_hypothesis_a_closeout"
            ]["sha256"],
            "support_state_tag": "support_intact_survives",
            "route_context_tag": "route_context_selection_only",
            "memory_scope_tag": "artifact_only_serialized_producer_policy_route_memory_or_trail",
            "regulation_scope_tag": "artifact_only_goal_proxy_regulation_candidate",
            "integration_outcome_tag": "bookkeeping_only",
            "node_plus_packet_budget_before": None,
            "node_plus_packet_budget_after": None,
            "node_plus_packet_budget_error": None,
            "memory_budget_surface": "separate_not_evaluated_in_schema_validation",
            "proxy_budget_surface": "separate_not_evaluated_in_schema_validation",
            "artifact_only": True,
            "runtime_state_used": False,
            "producer_scaffold_used": False,
            "native_policy_gap": baseline["native_policy_gaps"],
            "blocked_claims": baseline["claim_boundary"]["blocked_claims"],
            "claim_flags": claim_flags,
            "example_only_not_evidence": True,
            "exemplar_note": (
                "Schema-populated bookkeeping example only. It demonstrates "
                "tag shape and source linkage, but does not establish a causal "
                "integration replay or A6 support."
            ),
        },
        "integration_row_digest",
    )

    manifest: dict[str, Any] = {
        "schema": "n10_integration_fixture_manifest_v1",
        "manifest_kind": "contract_only_no_positive_integration_probe",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "baseline_artifact": {
            "path": rel(BASELINE_PATH),
            "inventory_digest": baseline["inventory_digest"],
            "sha256": digest_file(BASELINE_PATH),
        },
        "source_requirements": {
            "required_source_artifact_keys": source_keys,
            "source_digest_validation_required": True,
            "source_report_validation_required": True,
            "visual_references_are_not_evidence": True,
        },
        "integration_policy": integration_policy,
        "n10_category_ladder": N10_CATEGORY_LADDER,
        "integration_row_required_fields": INTEGRATION_ROW_REQUIRED_FIELDS,
        "allowed_values": {
            "integration_level": ["A0", "A1", "A2", "A3", "A4", "A5", "A6"],
            "n10_category_level": list(N10_CATEGORY_LADDER),
            "support_state_tag": SUPPORT_STATE_TAGS,
            "source_support_outcome_map": SOURCE_SUPPORT_OUTCOME_MAP,
            "route_context_tag": ROUTE_CONTEXT_TAGS,
            "memory_scope_tag": MEMORY_SCOPE_TAGS,
            "regulation_scope_tag": REGULATION_SCOPE_TAGS,
            "integration_outcome_tag": INTEGRATION_OUTCOME_TAGS,
        },
        "source_support_lanes": support_lanes,
        "fixture_lanes": fixture_lanes,
        "budget_boundaries": {
            "budget_mode_for_iterations_3_to_7": (
                "source_artifact_budget_compatibility_not_single_runtime_continuity"
            ),
            "budget_mode_for_new_n10_runs": "same_run_node_plus_packet_continuity",
            "node_plus_packet_budget_required": True,
            "node_plus_packet_budget_error_required_when_same_run": 0.0,
            "source_artifact_budget_errors_must_be_zero_or_explicitly_blocked": True,
            "memory_budget_surface_must_remain_separate": True,
            "proxy_budget_surface_must_remain_separate": True,
            "support_metrics_are_evidence_tags_not_budget_surfaces": True,
            "cross_artifact_budget_continuity_claim_allowed": False,
        },
        "budget_extraction_spec": {
            "n06": {
                "source_key": "n06_closeout",
                "budget_role": "route_selection_budget_evidence_only",
                "field_policy": "use candidate budget predictions and closeout budget controls where present; do not inherit scheduled packet execution",
                "continuity_boundary": "selection_only_pre_topology_scope",
            },
            "n07": {
                "source_key": "n07_withdrawal_baseline",
                "budget_role": "support_lane_budget_compatibility",
                "field_policy": "use withdrawal_lanes[].final_budget_error",
                "support_metrics_are_not_budget": True,
            },
            "n08": {
                "source_key": "n08_hypothesis_a_closeout",
                "budget_role": "memory_budget_surface_compatibility",
                "field_policy": "use serialized memory-budget evidence where present and keep separate from node-plus-packet budget",
            },
            "n09": {
                "source_key": "n09_hypothesis_a_closeout",
                "budget_role": "goal_proxy_regulation_budget_compatibility",
                "field_policy": "use GPR closeout budget controls and source row budget errors where present",
            },
            "n10": {
                "budget_role": "integration_budget_contract",
                "field_policy": "artifact-only rows may claim source-budget compatibility only; same-run N10 rows require node_plus_packet_budget_before/after/error from the same run",
            },
        },
        "control_blockers": CONTROL_BLOCKERS,
        "non_actions": {
            "positive_integration_probe_run": False,
            "a6_supported_by_iteration_2": False,
            "runtime_state_used": False,
            "src_changes_required": False,
            "claim_promotion_allowed": False,
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
        field for field in INTEGRATION_ROW_REQUIRED_FIELDS if field not in exemplar
    ]

    invalid_controls = {
        "missing_route_choice_artifact": CONTROL_BLOCKERS[
            "missing_route_choice_artifact"
        ],
        "missing_memory_affordance_artifact": CONTROL_BLOCKERS[
            "missing_memory_affordance_artifact"
        ],
        "missing_identity_support_artifact": CONTROL_BLOCKERS[
            "missing_identity_support_artifact"
        ],
        "missing_goal_proxy_regulation_artifact": CONTROL_BLOCKERS[
            "missing_goal_proxy_regulation_artifact"
        ],
        "source_artifact_digest_mismatch": CONTROL_BLOCKERS[
            "source_artifact_digest_mismatch"
        ],
        "claim_promotion": CONTROL_BLOCKERS["claim_promotion"],
        "hidden_experiment_side_steering": CONTROL_BLOCKERS[
            "hidden_experiment_side_steering"
        ],
        "budget_surface_ambiguity": CONTROL_BLOCKERS["budget_surface_ambiguity"],
        "support_disrupted_but_integration_allowed": CONTROL_BLOCKERS[
            "support_disrupted_but_integration_allowed"
        ],
        "restoration_required_but_missing": CONTROL_BLOCKERS[
            "restoration_required_but_missing"
        ],
    }

    checks = {
        "manifest_digest_present": bool(manifest.get("manifest_digest")),
        "baseline_inventory_digest_pinned": manifest["baseline_artifact"][
            "inventory_digest"
        ]
        == baseline["inventory_digest"],
        "source_artifact_digests_validate": source_validation["all_match"],
        "integration_row_required_fields_complete": not missing_fields,
        "n10_category_ladder_frozen": set(N10_CATEGORY_LADDER)
        == set(manifest["allowed_values"]["n10_category_level"]),
        "support_state_tags_frozen": set(SUPPORT_STATE_TAGS)
        == set(manifest["allowed_values"]["support_state_tag"]),
        "route_context_tags_frozen": set(ROUTE_CONTEXT_TAGS)
        == set(manifest["allowed_values"]["route_context_tag"]),
        "memory_scope_tags_frozen": set(MEMORY_SCOPE_TAGS)
        == set(manifest["allowed_values"]["memory_scope_tag"]),
        "regulation_scope_tags_frozen": set(REGULATION_SCOPE_TAGS)
        == set(manifest["allowed_values"]["regulation_scope_tag"]),
        "integration_outcome_tags_frozen": set(INTEGRATION_OUTCOME_TAGS)
        == set(manifest["allowed_values"]["integration_outcome_tag"]),
        "control_blockers_frozen": set(CONTROL_BLOCKERS)
        == set(manifest["control_blockers"]),
        "all_required_controls_declared": set(invalid_controls).issubset(
            set(manifest["control_blockers"])
        ),
        "fixture_lanes_cover_iterations_3_to_8": sorted(
            set(lane["planned_iteration"] for lane in manifest["fixture_lanes"])
        )
        == [3, 4, 5, 6, 7, 8],
        "support_disruption_lane_declared": any(
            lane["required_support_state_tag"]
            == "n09_matched_withdrawal_disrupts_support"
            for lane in manifest["fixture_lanes"]
        ),
        "explicit_restoration_lane_declared": any(
            lane["required_support_state_tag"]
            == "explicit_restoration_recovers_support"
            for lane in manifest["fixture_lanes"]
        ),
        "a5_mild_withdrawal_companion_lane_declared": any(
            lane["lane_id"] == "bounded_repeated_integration_mild_withdrawal_companion"
            for lane in manifest["fixture_lanes"]
        ),
        "n06_selection_only_constraint_declared_for_full_composition": all(
            lane.get("required_route_context_tag") == "route_context_selection_only"
            for lane in manifest["fixture_lanes"]
            if lane["planned_iteration"] in {7, 8}
        ),
        "budget_extraction_spec_declared": bool(manifest.get("budget_extraction_spec")),
        "cross_artifact_budget_continuity_not_claimed": manifest["budget_boundaries"][
            "cross_artifact_budget_continuity_claim_allowed"
        ]
        is False,
        "claim_flags_all_false": all(
            value is False for value in manifest["claim_flags"].values()
        ),
        "exemplar_is_not_evidence": exemplar["example_only_not_evidence"] is True,
        "no_positive_probe_run": manifest["non_actions"][
            "positive_integration_probe_run"
        ]
        is False,
        "a6_not_supported_by_iteration_2": manifest["non_actions"][
            "a6_supported_by_iteration_2"
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
            "invalid_controls": invalid_controls,
        },
        "checks": checks,
    }


def build_output(manifest: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    checks = validation["checks"]
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 2 passes if the N10 integration schema and fixture "
            "manifest are frozen before positive integration runs. The schema "
            "must keep evidence levels, support tags, budget surfaces, source "
            "provenance, and claim flags separate, and must reject missing "
            "source artifacts or claim-promotion fields."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_2_fixture_manifest_validation_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 2,
        "purpose": "integration_schema_fixture_manifest_contract_only",
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
            "n10_category_ladder": manifest["n10_category_ladder"],
            "integration_row_required_fields": INTEGRATION_ROW_REQUIRED_FIELDS,
            "allowed_values": manifest["allowed_values"],
            "control_blockers": manifest["control_blockers"],
        },
        "fixture_lanes": manifest["fixture_lanes"],
        "budget_boundaries": manifest["budget_boundaries"],
        "non_actions": manifest["non_actions"],
        "claim_flags": manifest["claim_flags"],
        "source_digest_validation": validation["source_digest_validation"],
        "schema_validation": validation["schema_validation"],
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "3_support_aware_regulation_replay",
    }
    output["validation_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any], manifest: dict[str, Any]) -> str:
    lines = [
        "# N10 Iteration 2 Integration Schema And Fixture Manifest",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 2 froze the N10 integration contract before any positive",
        "integration probe. The manifest is contract-only and does not support",
        "A6 by itself.",
        "",
        "```text",
        "positive integration probe run = false",
        "A6 supported by Iteration 2 = false",
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
        "## Frozen Tags",
        "",
        "N10 category ladder:",
        "",
        "```json",
        json.dumps(
            output["frozen_schema"]["n10_category_ladder"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "Support-state tags:",
        "",
        "```json",
        json.dumps(
            output["frozen_schema"]["allowed_values"]["support_state_tag"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "Integration outcome tags:",
        "",
        "```json",
        json.dumps(
            output["frozen_schema"]["allowed_values"]["integration_outcome_tag"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Fixture Lanes",
        "",
        "```json",
        json.dumps(output["fixture_lanes"], indent=2, sort_keys=True),
        "```",
        "",
        "## Control Blockers",
        "",
        "```json",
        json.dumps(output["frozen_schema"]["control_blockers"], indent=2, sort_keys=True),
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
    baseline = load_json(BASELINE_PATH)
    manifest = build_manifest(baseline)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    validation = validate_manifest(manifest, baseline)
    output = build_output(manifest, validation)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output, manifest), encoding="utf-8")
    if output["status"] != "passed":
        raise SystemExit(f"Iteration 2 manifest validation failed: {output['checks']}")
    print(f"wrote {rel(MANIFEST_PATH)}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"validation_digest {output['validation_digest']}")


if __name__ == "__main__":
    main()
