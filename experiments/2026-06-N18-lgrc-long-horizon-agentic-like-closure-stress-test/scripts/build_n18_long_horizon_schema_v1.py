#!/usr/bin/env python3
"""Build N18 Iteration 2 long-horizon schema, AP8 gate, and configs."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test"
)
CONFIGS = EXPERIMENT / "configs"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SCRIPTS = EXPERIMENT / "scripts"

SOURCE_INVENTORY = OUTPUTS / "n18_long_horizon_source_inventory.json"
OUTPUT_PATH = OUTPUTS / "n18_long_horizon_schema_v1.json"
REPORT_PATH = REPORTS / "n18_long_horizon_schema_v1.md"

CONFIG_PATHS = {
    "source_registry": CONFIGS / "n18_source_registry.json",
    "horizon_policy": CONFIGS / "n18_horizon_policy_v1.json",
    "stress_policy": CONFIGS / "n18_stress_policy_v1.json",
    "budget_limits": CONFIGS / "n18_budget_limits_v1.json",
    "control_variants": CONFIGS / "n18_control_variants_v1.json",
    "replay_policy": CONFIGS / "n18_replay_policy_v1.json",
}

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/"
    "scripts/build_n18_long_horizon_schema_v1.py"
)

ABSOLUTE_PATH_MARKERS = (
    "/" + "home" + "/",
    "/" + "tmp" + "/",
    "/" + "Users" + "/",
    "C:" + "\\",
    "\\Users\\",
    "geometric-" + "reflexive-coherence",
    "/" + "arc-" + "of-becoming" + "/",
)

STRESS_LADDER = {
    "L0": "source inventory and AP8 contract only",
    "L1": "short-horizon AP7 replay remains source-current",
    "L2": "longer horizon replay remains source-current without added perturbation",
    "L3": "support withdrawal/restoration and proxy perturbation remain bounded",
    "L4": "route/context reversal and memory relaxation remain bounded",
    "L5": "environment/resource and shared-medium perturbation remain separable",
    "L6": "artifact-only reconstruction and replay controls pass",
    "L7": "claim-clean AP8 candidate, unsafe promotions blocked",
}

STRESS_LADDER_INDEX = {key: index for index, key in enumerate(STRESS_LADDER)}

STRESS_DIMENSIONS = [
    "baseline_ap7_replay",
    "longer_horizon_window",
    "support_withdrawal_restoration",
    "proxy_perturbation",
    "route_context_reversal",
    "memory_relaxation",
    "environment_resource_perturbation",
    "shared_medium_perturbation",
    "artifact_only_reconstruction",
    "duplicate_replay",
    "snapshot_load_replay",
    "stale_state_control",
    "stale_support_state_control",
    "stale_memory_context_control",
    "stale_selection_context_control",
    "stale_proxy_target_control",
    "stale_boundary_state_control",
    "stale_loop_feedback_control",
]

TRACE_FIELDS = [
    "support_state_trace",
    "memory_context_trace",
    "regulation_trace",
    "selection_context_trace",
    "proxy_target_trace",
    "boundary_separation_trace",
    "closed_loop_feedback_trace",
]

ROW_SCHEMA_FIELDS = [
    "row_id",
    "row_type",
    "stress_id",
    "stress_dimension",
    "stress_ladder_rung",
    "stress_ladder_index",
    "horizon_window",
    "max_supported_horizon",
    "source_backed_horizon_envelope",
    "horizon_extrapolation_allowed",
    "evidence_branch",
    "native_branch_opened",
    "phase8_branch_opened",
    "source_rows",
    "source_claim_ceilings",
    "source_digests",
    "budget_surface",
    "budget_valid",
    "support_state_trace",
    "memory_context_trace",
    "regulation_trace",
    "selection_context_trace",
    "proxy_target_trace",
    "boundary_separation_trace",
    "closed_loop_feedback_trace",
    "linked_trace_continuity",
    "cross_axis_continuity_evidence",
    "long_horizon_continuity_evidence",
    "artifact_only_replay_digest",
    "artifact_only_reconstruction_status",
    "duplicate_replay_status",
    "snapshot_load_replay_status",
    "stale_state_control_status",
    "order_inversion_status",
    "post_hoc_stitching_control_status",
    "single_axis_stale_controls",
    "controls",
    "ap8_gates",
    "row_decision",
    "claim_ceiling",
    "ap8_candidate_allowed",
    "final_ap8_supported",
    "phase8_opened",
    "native_support_opened",
    "unsafe_claim_flags",
    "missing_gates",
    "ap8_outcome_classification",
]

AP8_REQUIRED_GATES = [
    "source_rows_pinned",
    "source_claim_ceilings_preserved",
    "evidence_branch_artifact_only",
    "horizon_envelope_declared",
    "horizon_policy_satisfied",
    "all_required_trace_axes_present",
    "linked_trace_continuity_present",
    "cross_axis_continuity_evidence_present",
    "long_horizon_continuity_present",
    "budget_valid",
    "artifact_only_reconstruction_passed",
    "duplicate_replay_passed",
    "snapshot_load_replay_passed",
    "stale_state_control_passed",
    "single_axis_stale_controls_passed",
    "post_hoc_stitching_control_passed",
    "drift_as_autonomy_control_passed",
    "b4c5_relabel_controls_passed",
    "stress_controls_passed",
    "unsafe_claim_flags_false",
    "phase8_not_opened",
    "native_support_not_opened",
]

ROW_DECISIONS = ["supported", "partial", "blocked", "rejected", "not_applicable"]

ROW_TYPES = [
    "baseline_replay",
    "stress_candidate",
    "control_row",
    "classification_row",
    "validator_self_test_not_evidence",
]

CONTROL_REQUIREMENTS = [
    {
        "control_id": "stale_state_replay_control",
        "purpose": "blocks stale earlier-window state from passing as long-horizon continuity",
        "failure_blocks_gate": "stale_state_control_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "stale_support_state_control",
        "purpose": "blocks stale support state from carrying long-horizon continuity alone",
        "failure_blocks_gate": "single_axis_stale_controls_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "stale_memory_context_control",
        "purpose": "blocks stale memory/context state from passing as live continuity",
        "failure_blocks_gate": "single_axis_stale_controls_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "stale_selection_context_control",
        "purpose": "blocks stale selection context from passing as current selection continuity",
        "failure_blocks_gate": "single_axis_stale_controls_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "stale_proxy_target_control",
        "purpose": "blocks stale proxy/target state from passing as current proxy continuity",
        "failure_blocks_gate": "single_axis_stale_controls_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "stale_boundary_state_control",
        "purpose": "blocks stale boundary assignment from passing as current separability",
        "failure_blocks_gate": "single_axis_stale_controls_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "stale_loop_feedback_control",
        "purpose": "blocks stale loop feedback from passing as current closed-loop feedback",
        "failure_blocks_gate": "single_axis_stale_controls_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "order_inversion_control",
        "purpose": "blocks inverted or shuffled horizon/order traces from passing as source-current continuity",
        "failure_blocks_gate": "post_hoc_stitching_control_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "hidden_native_support_relabel_control",
        "purpose": "blocks interpreting artifact evidence as native support",
        "failure_blocks_gate": "unsafe_claim_flags_false",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "semantic_agency_relabel_control",
        "purpose": "blocks agency, intention, action/perception, and goal-ownership relabels",
        "failure_blocks_gate": "unsafe_claim_flags_false",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "identity_acceptance_relabel_control",
        "purpose": "blocks identity acceptance from support/memory continuity",
        "failure_blocks_gate": "unsafe_claim_flags_false",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "phase8_native_implementation_relabel_control",
        "purpose": "blocks Phase 8/native implementation claims unless separately opened",
        "failure_blocks_gate": "phase8_not_opened",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "long_horizon_drift_envelope_control",
        "purpose": "blocks drift outside source-backed envelope",
        "failure_blocks_gate": "horizon_policy_satisfied",
        "expected_status_for_ap8": "passed",
    },
    {
        "control_id": "drift_relabel_as_autonomy_control",
        "purpose": "blocks long-horizon drift from being relabeled as autonomous adaptation",
        "failure_blocks_gate": "drift_as_autonomy_control_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "resource_shared_medium_merge_control",
        "purpose": "blocks resource or shared-medium merge/leakage as closure",
        "failure_blocks_gate": "stress_controls_passed",
        "expected_status_for_ap8": "passed",
    },
    {
        "control_id": "b4c5_original_reverse_replay_relabel_control",
        "purpose": "preserves N17's blocker that original B4/C5 reverse replay remains unsupported",
        "failure_blocks_gate": "b4c5_relabel_controls_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "general_symmetric_native_multibasin_relabel_control",
        "purpose": "blocks local shared-medium evidence from becoming general symmetric/native multi-basin claims",
        "failure_blocks_gate": "b4c5_relabel_controls_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "post_hoc_long_horizon_stitching_control",
        "purpose": "blocks assembling compatible windows after the fact",
        "failure_blocks_gate": "post_hoc_stitching_control_passed",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "budget_overrun_control",
        "purpose": "blocks rows outside declared budget surface",
        "failure_blocks_gate": "budget_valid",
        "expected_status_for_ap8": "failed_expected",
    },
    {
        "control_id": "artifact_only_reconstruction_mismatch_control",
        "purpose": "requires artifact-only reconstruction to match source row digest inputs",
        "failure_blocks_gate": "artifact_only_reconstruction_passed",
        "expected_status_for_ap8": "failed_expected",
    },
]

REPLAY_DIGEST_INCLUDE_FIELDS = [
    "schema_version",
    "stress_id",
    "stress_dimension",
    "stress_ladder_rung",
    "horizon_window",
    "max_supported_horizon",
    "source_backed_horizon_envelope",
    "horizon_extrapolation_allowed",
    "evidence_branch",
    "source_rows",
    "source_claim_ceilings",
    "source_digests",
    "budget_surface",
    "support_state_trace",
    "memory_context_trace",
    "regulation_trace",
    "selection_context_trace",
    "proxy_target_trace",
    "boundary_separation_trace",
    "closed_loop_feedback_trace",
    "linked_trace_continuity",
    "cross_axis_continuity_evidence",
    "long_horizon_continuity_evidence",
    "controls",
    "ap8_gates",
    "row_decision",
    "claim_ceiling",
    "ap8_candidate_allowed",
    "unsafe_claim_flags",
]

REPLAY_DIGEST_EXCLUDE_FIELDS = [
    "generated_at",
    "wall_clock_time",
    "local_absolute_paths",
    "git",
    "process_id",
    "temporary_files",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def contains_absolute_path(data: Any) -> bool:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return any(marker in serialized for marker in ABSOLUTE_PATH_MARKERS)


def git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return "unknown"
    return result.stdout.strip()


def git_status_short() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ["git_status_unavailable"]
    return [line for line in result.stdout.splitlines() if line]


def write_config(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.write_text(canonical_json(payload), encoding="utf-8")
    return {"path": rel(path), "sha256": sha256_file(path), "digest": digest_value(payload)}


def source_registry_config(inventory: dict[str, Any]) -> dict[str, Any]:
    rows = inventory["source_rows"]
    return {
        "config_id": "n18_source_registry",
        "schema_version": "n18.source_registry.v1",
        "source_inventory": rel(SOURCE_INVENTORY),
        "source_inventory_digest": inventory["output_digest"],
        "source_rows": [
            {
                "row_id": row["row_id"],
                "source_experiment": row["source_experiment"],
                "source_artifact": row["source_artifact"],
                "source_report": row["source_report"],
                "source_sha256": row["source_sha256"],
                "source_output_digest": row["source_output_digest"],
                "source_claim_ceiling": row["source_claim_ceiling"],
                "source_consumption_rule": row["source_consumption_rule"],
                "construction_role": row["construction_role"],
                "mvp_relevance": row["mvp_relevance"],
            }
            for row in rows
        ],
    }


def horizon_policy_config() -> dict[str, Any]:
    tested_windows = [
        {"window_id": "h2", "relative_window_count": 2},
        {"window_id": "h4", "relative_window_count": 4},
        {"window_id": "h8", "relative_window_count": 8},
        {"window_id": "h16", "relative_window_count": 16},
    ]
    return {
        "config_id": "n18_horizon_policy_v1",
        "schema_version": "n18.horizon_policy.v1",
        "baseline_horizon": {
            "name": "n17_ap7_closeout_baseline",
            "minimum_stress_ladder_rung": "L1",
        },
        "tested_horizon_windows": tested_windows,
        "longer_horizon_windows": tested_windows,
        "max_supported_horizon": "not_established_until_iteration_4",
        "source_backed_horizon_envelope": {
            "status": "not_established_until_iteration_4",
            "supported_windows": [],
            "blocked_windows": [],
        },
        "horizon_extrapolation_allowed": False,
        "window_units": "declared_artifact_trace_windows",
        "support_statement": (
            "AP8 support is horizon-bounded. A row supports only the explicit "
            "tested horizon window and stress envelope, not indefinite persistence."
        ),
        "admissibility": {
            "must_preserve_source_current_inputs": True,
            "must_record_per_window_budget": True,
            "must_reject_drift_outside_source_backed_envelope": True,
            "baseline_replay_alone_cannot_support_ap8": True,
        },
    }


def stress_policy_config() -> dict[str, Any]:
    return {
        "config_id": "n18_stress_policy_v1",
        "schema_version": "n18.stress_policy.v1",
        "stress_dimensions": STRESS_DIMENSIONS,
        "required_positive_stress_dimensions": [
            "longer_horizon_window",
            "support_withdrawal_restoration",
            "proxy_perturbation",
            "route_context_reversal",
            "memory_relaxation",
            "environment_resource_perturbation",
            "shared_medium_perturbation",
        ],
        "required_control_dimensions": [
            "artifact_only_reconstruction",
            "duplicate_replay",
            "snapshot_load_replay",
            "stale_state_control",
        ],
        "trace_axes": TRACE_FIELDS,
        "linked_trace_policy": {
            "required_links": [
                "support_to_regulation",
                "regulation_to_selection",
                "selection_to_proxy",
                "proxy_to_boundary",
                "boundary_to_loop_feedback",
                "memory_context_to_selection",
            ],
            "all_links_must_be_source_current": True,
            "trace_presence_alone_is_insufficient": True,
        },
        "cross_axis_continuity_policy": {
            "field": "cross_axis_continuity_evidence",
            "required_for_ap8": True,
            "must_bind_linked_trace_continuity": True,
            "trace_presence_alone_is_insufficient": True,
        },
        "ap8_outcome_taxonomy": {
            "AP8_supported_full": (
                "all required stress families pass under the declared horizon "
                "and stress envelope"
            ),
            "AP8_supported_limited": (
                "long-horizon replay plus some stress families pass while other "
                "families are deferred or blocked"
            ),
            "AP8_blocked": (
                "core continuity, budget, replay, or claim controls fail"
            ),
        },
        "fail_closed_rules": {
            "missing_trace_axis": "ap8_candidate_allowed_false",
            "missing_linked_trace_continuity": "ap8_candidate_allowed_false",
            "budget_invalid": "ap8_candidate_allowed_false",
            "unsafe_claim_flag_true": "ap8_candidate_allowed_false",
            "phase8_or_native_support_opened": "ap8_candidate_allowed_false",
        },
    }


def budget_limits_config() -> dict[str, Any]:
    return {
        "config_id": "n18_budget_limits_v1",
        "schema_version": "n18.budget_limits.v1",
        "budget_units": "artifact_stress_units",
        "limits": {
            "max_relative_window_count": 16,
            "max_positive_stress_rows_per_iteration": 12,
            "max_control_rows_per_iteration": 16,
            "max_total_source_rows_per_candidate": 12,
            "must_record_budget_surface": True,
        },
        "invalid_budget_effect": {
            "row_decision": "blocked",
            "ap8_candidate_allowed": False,
        },
    }


def control_variants_config() -> dict[str, Any]:
    return {
        "config_id": "n18_control_variants_v1",
        "schema_version": "n18.control_variants.v1",
        "control_requirements": CONTROL_REQUIREMENTS,
        "unsafe_claims_blocked": [
            "agency",
            "intention",
            "semantic_action",
            "semantic_perception",
            "semantic_goal_ownership",
            "selfhood",
            "personhood",
            "biological_behavior",
            "identity_acceptance",
            "native_support",
            "native_support_without_phase8_validation",
            "organism_life",
            "fully_native_integration",
            "fully_native_agentic_like_integration",
            "unrestricted_agency",
            "original_b4c5_reverse_replay",
            "general_symmetric_native_multi_basin",
        ],
    }


def replay_policy_config() -> dict[str, Any]:
    return {
        "config_id": "n18_replay_policy_v1",
        "schema_version": "n18.replay_policy.v1",
        "digest_algorithm": "sha256_canonical_json",
        "include_fields": REPLAY_DIGEST_INCLUDE_FIELDS,
        "exclude_fields": REPLAY_DIGEST_EXCLUDE_FIELDS,
        "required_replay_statuses_for_ap8": {
            "artifact_only_reconstruction_status": "stable",
            "duplicate_replay_status": "stable",
            "snapshot_load_replay_status": "stable",
            "stale_state_control_status": "failed_expected",
            "order_inversion_status": "failed_expected",
            "post_hoc_stitching_control_status": "failed_expected",
        },
    }


def build_schema(inventory: dict[str, Any], config_files: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "experiment": "N18",
        "iteration": 2,
        "artifact_id": "n18_long_horizon_schema_v1",
        "purpose": "long-horizon schema, replay, budget, and AP8 claim gate",
        "schema_version": "n18.long_horizon_schema.v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_long_horizon_schema_v1_no_ap8_evidence",
        "source_inventory": {
            "path": rel(SOURCE_INVENTORY),
            "output_digest": inventory["output_digest"],
            "sha256": sha256_file(SOURCE_INVENTORY),
            "ready_for_iteration_2_schema": inventory["ready_for_iteration_2_schema"],
        },
        "evidence_branch": "artifact_only",
        "native_branch_opened": False,
        "phase8_branch_opened": False,
        "config_files": config_files,
        "stress_ladder": STRESS_LADDER,
        "stress_ladder_index": STRESS_LADDER_INDEX,
        "stress_dimensions": STRESS_DIMENSIONS,
        "row_schema_contract": {
            "row_schema_fields": ROW_SCHEMA_FIELDS,
            "row_type_values": ROW_TYPES,
            "row_decision_values": ROW_DECISIONS,
            "trace_fields": TRACE_FIELDS,
        },
        "horizon_policy": horizon_policy_config(),
        "stress_policy": stress_policy_config(),
        "linked_trace_policy": stress_policy_config()["linked_trace_policy"],
        "cross_axis_continuity_policy": stress_policy_config()[
            "cross_axis_continuity_policy"
        ],
        "ap8_outcome_taxonomy": stress_policy_config()["ap8_outcome_taxonomy"],
        "budget_policy": budget_limits_config(),
        "control_requirements": CONTROL_REQUIREMENTS,
        "unsafe_claims_blocked": control_variants_config()["unsafe_claims_blocked"],
        "replay_digest_policy": replay_policy_config(),
        "ap8_required_gates": AP8_REQUIRED_GATES,
        "gate_policy": {
            "ap8_candidate_allowed_requires_all_gates_true": True,
            "final_ap8_supported_forbidden_before_final_closeout": True,
            "baseline_ap7_replay_alone_cannot_support_ap8": True,
            "phase8_opened_forces_artifact_only_ap8_false_until_separate_native_validation": True,
            "native_support_opened_forces_artifact_only_ap8_false_until_separate_native_validation": True,
        },
        "stress_ladder_dimension_policy": {
            "baseline_ap7_replay": ["L1"],
            "longer_horizon_window": ["L2"],
            "support_withdrawal_restoration": ["L3"],
            "proxy_perturbation": ["L3"],
            "route_context_reversal": ["L4"],
            "memory_relaxation": ["L4"],
            "environment_resource_perturbation": ["L5"],
            "shared_medium_perturbation": ["L5"],
            "artifact_only_reconstruction": ["L6"],
            "duplicate_replay": ["L6"],
            "snapshot_load_replay": ["L6"],
            "stale_state_control": ["L6"],
            "stale_support_state_control": ["L6"],
            "stale_memory_context_control": ["L6"],
            "stale_selection_context_control": ["L6"],
            "stale_proxy_target_control": ["L6"],
            "stale_boundary_state_control": ["L6"],
            "stale_loop_feedback_control": ["L6"],
        },
        "claim_ceiling_policy": {
            "allowed_ap8_claim_ceilings": [
                "artifact_only_agentic_like_closure_candidate",
                "artifact_level_ap8_long_horizon_agentic_like_closure_candidate",
                "agency_prerequisite_long_horizon_closure_candidate",
            ],
            "source_claim_ceilings_must_be_recorded": True,
            "source_claim_ceilings_must_not_be_rewritten": True,
        },
        "claim_boundary": {
            "allowed_if_supported": [
                "artifact_only_agentic_like_closure_candidate",
                "artifact_level_ap8_long_horizon_agentic_like_closure_candidate",
                "agency_prerequisite_long_horizon_closure_candidate",
            ],
            "blocked": [
                "agency",
                "intention",
                "semantic_action",
                "semantic_perception",
                "semantic_goal_ownership",
                "selfhood",
                "personhood",
                "biological_behavior",
                "identity_acceptance",
                "native_support_without_phase8_validation",
                "native_support",
                "organism_life",
                "fully_native_agentic_like_integration",
                "fully_native_integration",
                "unrestricted_agency",
                "original_b4c5_reverse_replay",
                "general_symmetric_native_multi_basin",
            ],
        },
        "rows": [],
        "ap8_candidate_allowed": False,
        "final_ap8_supported": False,
        "closed_long_horizon_agentic_like_closure_demonstrated": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "checks": [],
        "errors": [],
        "git": {
            "head": "not_recorded_in_artifact",
            "status_short": [],
            "policy": "git metadata excluded to keep artifact replay portable",
        },
    }


def make_checks(schema: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": "source_inventory_ready",
            "passed": schema["source_inventory"]["ready_for_iteration_2_schema"] is True,
            "detail": schema["source_inventory"],
        },
        {
            "check_id": "required_config_files_written",
            "passed": all(Path(ROOT / item["path"]).exists() for item in schema["config_files"].values()),
            "detail": sorted(schema["config_files"]),
        },
        {
            "check_id": "stress_ladder_frozen",
            "passed": list(schema["stress_ladder"]) == [f"L{i}" for i in range(8)],
            "detail": schema["stress_ladder"],
        },
        {
            "check_id": "ap8_gates_fail_closed",
            "passed": schema["gate_policy"]["ap8_candidate_allowed_requires_all_gates_true"]
            and schema["gate_policy"]["final_ap8_supported_forbidden_before_final_closeout"],
            "detail": schema["ap8_required_gates"],
        },
        {
            "check_id": "artifact_only_branch_visible",
            "passed": schema["evidence_branch"] == "artifact_only"
            and schema["native_branch_opened"] is False
            and schema["phase8_branch_opened"] is False,
            "detail": {
                "evidence_branch": schema["evidence_branch"],
                "native_branch_opened": schema["native_branch_opened"],
                "phase8_branch_opened": schema["phase8_branch_opened"],
            },
        },
        {
            "check_id": "horizon_envelope_policy_frozen",
            "passed": schema["horizon_policy"]["horizon_extrapolation_allowed"] is False
            and "max_supported_horizon" in schema["horizon_policy"]
            and "source_backed_horizon_envelope" in schema["horizon_policy"],
            "detail": {
                "max_supported_horizon": schema["horizon_policy"]["max_supported_horizon"],
                "horizon_extrapolation_allowed": schema["horizon_policy"][
                    "horizon_extrapolation_allowed"
                ],
            },
        },
        {
            "check_id": "linked_trace_continuity_policy_frozen",
            "passed": len(schema["linked_trace_policy"]["required_links"]) == 6
            and schema["linked_trace_policy"]["trace_presence_alone_is_insufficient"] is True,
            "detail": schema["linked_trace_policy"]["required_links"],
        },
        {
            "check_id": "cross_axis_continuity_policy_frozen",
            "passed": schema["cross_axis_continuity_policy"]["required_for_ap8"] is True
            and schema["cross_axis_continuity_policy"][
                "trace_presence_alone_is_insufficient"
            ]
            is True,
            "detail": schema["cross_axis_continuity_policy"],
        },
        {
            "check_id": "single_axis_stale_controls_frozen",
            "passed": all(
                control_id
                in [item["control_id"] for item in schema["control_requirements"]]
                for control_id in [
                    "stale_support_state_control",
                    "stale_memory_context_control",
                    "stale_selection_context_control",
                    "stale_proxy_target_control",
                    "stale_boundary_state_control",
                    "stale_loop_feedback_control",
                ]
            ),
            "detail": [
                item["control_id"]
                for item in schema["control_requirements"]
                if item.get("failure_blocks_gate") == "single_axis_stale_controls_passed"
            ],
        },
        {
            "check_id": "order_inversion_control_frozen",
            "passed": any(
                item["control_id"] == "order_inversion_control"
                and item["failure_blocks_gate"] == "post_hoc_stitching_control_passed"
                for item in schema["control_requirements"]
            ),
            "detail": "order_inversion_control blocks inverted or shuffled horizon traces",
        },
        {
            "check_id": "b4c5_relabel_controls_frozen",
            "passed": all(
                control_id
                in [item["control_id"] for item in schema["control_requirements"]]
                for control_id in [
                    "b4c5_original_reverse_replay_relabel_control",
                    "general_symmetric_native_multibasin_relabel_control",
                ]
            ),
            "detail": [
                item["control_id"]
                for item in schema["control_requirements"]
                if item.get("failure_blocks_gate") == "b4c5_relabel_controls_passed"
            ],
        },
        {
            "check_id": "claim_boundary_names_aligned",
            "passed": set(schema["claim_boundary"]["blocked"])
            == set(schema["unsafe_claims_blocked"]),
            "detail": sorted(set(schema["claim_boundary"]["blocked"]) ^ set(schema["unsafe_claims_blocked"])),
        },
        {
            "check_id": "ap8_outcome_taxonomy_frozen",
            "passed": set(schema["ap8_outcome_taxonomy"]) == {
                "AP8_supported_full",
                "AP8_supported_limited",
                "AP8_blocked",
            },
            "detail": schema["ap8_outcome_taxonomy"],
        },
        {
            "check_id": "config_embedded_policy_consistency",
            "passed": schema["horizon_policy"] == horizon_policy_config()
            and schema["stress_policy"] == stress_policy_config()
            and schema["budget_policy"] == budget_limits_config()
            and schema["replay_digest_policy"] == replay_policy_config()
            and schema["control_requirements"]
            == control_variants_config()["control_requirements"]
            and schema["row_schema_contract"]["trace_fields"]
            == schema["stress_policy"]["trace_axes"],
            "detail": "embedded policy sections match generated config payloads",
        },
        {
            "check_id": "baseline_replay_cannot_support_ap8",
            "passed": schema["gate_policy"]["baseline_ap7_replay_alone_cannot_support_ap8"],
            "detail": "Iteration 3 baseline replay can be L1 only.",
        },
        {
            "check_id": "phase8_native_flags_false",
            "passed": schema["phase8_opened"] is False and schema["native_support_opened"] is False,
            "detail": {
                "phase8_opened": schema["phase8_opened"],
                "native_support_opened": schema["native_support_opened"],
            },
        },
        {
            "check_id": "no_final_ap8_claim",
            "passed": schema["ap8_candidate_allowed"] is False
            and schema["final_ap8_supported"] is False,
            "detail": "Iteration 2 freezes rules only.",
        },
        {
            "check_id": "no_absolute_paths",
            "passed": not contains_absolute_path(schema),
            "detail": "portable relative paths only",
        },
    ]


def digest_payload(payload: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(payload)
    value.pop("output_digest", None)
    value.pop("generated_at", None)
    value.pop("git", None)
    return value


def write_report(schema: dict[str, Any]) -> None:
    def json_bool(value: bool) -> str:
        return json.dumps(value)

    lines = [
        "# N18 Long-Horizon Schema V1",
        "",
        f"Status: `{schema['status']}`",
        "",
        f"Acceptance state: `{schema['acceptance_state']}`",
        "",
        f"Output digest: `{schema['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 2 freezes the AP8 stress-row schema, horizon policy, replay",
        "policy, budget policy, controls, and claim gate. It does not generate",
        "positive long-horizon evidence and it does not support final AP8.",
        "",
        "```text",
        f"rows = {len(schema['rows'])}",
        f"ap8_candidate_allowed = {json_bool(schema['ap8_candidate_allowed'])}",
        f"final_ap8_supported = {json_bool(schema['final_ap8_supported'])}",
        f"phase8_opened = {json_bool(schema['phase8_opened'])}",
        f"native_support_opened = {json_bool(schema['native_support_opened'])}",
        "```",
        "",
        "## Stress Ladder",
        "",
        "| Rung | Meaning |",
        "| --- | --- |",
    ]
    for rung, meaning in schema["stress_ladder"].items():
        lines.append(f"| `{rung}` | {meaning} |")
    lines.extend(
        [
            "",
            "## AP8 Required Gates",
            "",
            "```json",
            json.dumps(schema["ap8_required_gates"], indent=2, sort_keys=True),
            "```",
            "",
            "## Config Files",
            "",
            "| Config | Path | SHA-256 |",
            "| --- | --- | --- |",
        ]
    )
    for name, info in schema["config_files"].items():
        lines.append(f"| `{name}` | `{info['path']}` | `{info['sha256']}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The schema makes AP8 fail closed: a row cannot allow AP8 unless source",
            "rows are pinned, claim ceilings are preserved, the artifact-only branch",
            "is declared, the horizon envelope is explicit, horizon policy passes,",
            "all trace axes are present, linked and cross-axis continuity are shown,",
            "budget is valid, replay/reconstruction, order-inversion, stale-axis,",
            "drift/autonomy, and B4/C5 relabel controls pass, unsafe claim flags",
            "remain false, and Phase 8/native support remain unopened.",
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for check in schema["checks"]:
        detail = json.dumps(check["detail"], sort_keys=True)
        lines.append(
            f"| `{check['check_id']}` | `{json_bool(check['passed'])}` | `{detail}` |"
        )
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    inventory = load_json(SOURCE_INVENTORY)
    configs = {
        "source_registry": source_registry_config(inventory),
        "horizon_policy": horizon_policy_config(),
        "stress_policy": stress_policy_config(),
        "budget_limits": budget_limits_config(),
        "control_variants": control_variants_config(),
        "replay_policy": replay_policy_config(),
    }
    config_files = {
        name: write_config(CONFIG_PATHS[name], payload) for name, payload in configs.items()
    }
    schema = build_schema(inventory, config_files)
    schema["checks"] = make_checks(schema)
    if not all(check["passed"] for check in schema["checks"]):
        schema["status"] = "failed"
        schema["acceptance_state"] = "blocked_schema_checks_failed"
        schema["errors"] = [
            check["check_id"] for check in schema["checks"] if not check["passed"]
        ]
    schema["output_digest"] = digest_value(digest_payload(schema))
    OUTPUT_PATH.write_text(canonical_json(schema), encoding="utf-8")
    write_report(schema)
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    for info in config_files.values():
        print(f"wrote {info['path']}")
    if schema["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
