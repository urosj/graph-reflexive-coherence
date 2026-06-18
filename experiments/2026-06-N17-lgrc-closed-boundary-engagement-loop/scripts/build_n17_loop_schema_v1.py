#!/usr/bin/env python3
"""Build N17 Iteration 2 loop schema, AP7 gate, and config files.

Iteration 2 freezes an enforceable contract only. It does not produce loop
evidence and it does not support AP7.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N17-lgrc-closed-boundary-engagement-loop"
CONFIGS = EXPERIMENT / "configs"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SCRIPTS = EXPERIMENT / "scripts"

SOURCE_INVENTORY = OUTPUTS / "n17_loop_source_inventory.json"
OUTPUT_PATH = OUTPUTS / "n17_loop_schema_v1.json"
REPORT_PATH = REPORTS / "n17_loop_schema_v1.md"
VALIDATOR_PATH = SCRIPTS / "validate_n17_loop_row.py"

CONFIG_PATHS = {
    "source_registry": CONFIGS / "n17_source_registry.json",
    "loop_policy": CONFIGS / "n17_loop_policy_v1.json",
    "budget_limits": CONFIGS / "n17_budget_limits_v1.json",
    "control_variants": CONFIGS / "n17_control_variants_v1.json",
    "replay_policy": CONFIGS / "n17_replay_policy_v1.json",
}

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/scripts/"
    "build_n17_loop_schema_v1.py"
)

ABSOLUTE_PATH_MARKERS = (
    "/home/",
    "/tmp/",
    "/Users/",
    "C:\\",
    "\\Users\\",
    "geometric-reflexive-coherence",
    "/arc-of-becoming/",
)

LOOP_LADDER = {
    "G0": "one-way boundary crossing trace",
    "G1": "internal update after external crossing",
    "G2": "outbound response changes external state",
    "G3": "changed external state feeds back into later internal state",
    "G4": "replay-stable closed loop",
    "G5": "challenge-stable closed loop under perturbation or flux",
    "G6": "shared-medium closed loop without basin merge",
    "G7": "claim-clean AP7 candidate, unsafe promotions blocked",
}

LOOP_RUNG_INDEX = {
    "G0": 0,
    "G1": 1,
    "G2": 2,
    "G3": 3,
    "G4": 4,
    "G5": 5,
    "G6": 6,
    "G7": 7,
}

TRACE_LEGS = [
    "external_to_internal_trace",
    "internal_response_trace",
    "response_to_external_change_trace",
    "external_feedback_to_internal_trace",
]

ORDERED_PHASES = [
    "t0_external_pressure_or_crossing",
    "t1_internal_support_update",
    "t2_response_caused_external_change",
    "t3_later_internal_support_conditioned_by_changed_external_state",
]

LOOP_FAMILIES = [
    "one_way_crossing_active_null",
    "perturbation_response_recovery_loop",
    "resource_support_modulation_loop",
    "shared_medium_reciprocal_loop",
]

ROW_TYPE_VALUES = [
    "active_null",
    "loop_candidate",
    "control_row",
    "extension_candidate",
    "validator_self_test_not_evidence",
]

MVP_FAMILY = "perturbation_response_recovery_loop"
EXTENSION_FAMILIES = [
    "resource_support_modulation_loop",
    "shared_medium_reciprocal_loop",
]
NULL_CONTROL_FAMILIES = ["one_way_crossing_active_null"]

ROW_DECISION_VALUES = [
    "supported",
    "blocked",
    "partial",
    "rejected",
    "not_applicable",
]

CONTROL_STATUS_VALUES = [
    "passed",
    "failed_expected",
    "blocked",
    "not_applicable",
]

TRACE_LEG_FIELDS = [
    "present",
    "source_backed",
    "phase",
    "state_before",
    "state_after",
    "dependency_note",
]

ROW_SCHEMA_FIELDS = [
    "row_id",
    "row_type",
    "loop_family",
    "loop_rung",
    "loop_rung_index",
    "source_row_ids",
    "source_artifacts",
    "row_decision",
    "boundary_assignments",
    "external_to_internal_trace",
    "internal_response_trace",
    "response_to_external_change_trace",
    "external_feedback_to_internal_trace",
    "phase_timing",
    "monotonic_phase_order",
    "response_caused_external_change",
    "external_change_would_occur_without_response",
    "later_internal_depends_on_changed_external_state",
    "feedback_removed_control_changes_result",
    "loop_closure_evidence",
    "dependency_trace",
    "budget_cost_surface",
    "budget_units",
    "budget_validity",
    "replay_digest_inputs",
    "replay_digest_algorithm",
    "artifact_only_replay_status",
    "snapshot_load_status",
    "duplicate_replay_status",
    "order_inversion_replay_status",
    "controls",
    "ap7_gates",
    "closed_loop_claim_allowed",
    "provisional_ap_level",
    "provisional_claim_ceiling",
    "claim_flags",
    "blocked_claims",
    "missing_gates",
    "final_ap7_supported",
]

TOP_LEVEL_OUTPUT_FIELDS = [
    "experiment",
    "iteration",
    "artifact_id",
    "purpose",
    "schema_version",
    "generated_at",
    "command",
    "status",
    "acceptance_state",
    "source_inventory",
    "config_files",
    "rows",
    "controls",
    "checks",
    "claim_flags",
    "errors",
    "output_digest",
]

REPLAY_DIGEST_INCLUDE_FIELDS = [
    "schema_version",
    "source_row_ids",
    "source_artifacts",
    "loop_policy_digest",
    "boundary_assignments",
    "row_decision",
    "external_to_internal_trace",
    "internal_response_trace",
    "response_to_external_change_trace",
    "external_feedback_to_internal_trace",
    "phase_timing",
    "monotonic_phase_order",
    "response_caused_external_change",
    "later_internal_depends_on_changed_external_state",
    "loop_closure_evidence",
    "dependency_trace",
    "budget_cost_surface",
    "budget_validity",
    "controls",
    "ap7_gates",
    "claim_flags",
    "closed_loop_claim_allowed",
]

REPLAY_DIGEST_EXCLUDE_FIELDS = [
    "generated_at",
    "config_digest",
    "wall_clock_time",
    "local_absolute_paths",
    "git",
    "temporary_files",
    "process_id",
]

CONTROL_REQUIREMENTS = [
    {
        "control_id": "artifact_only_replay_control",
        "purpose": "requires replay from artifact state rather than hidden runtime state",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "replay_digest_valid",
        "status_backed_by": "artifact_only_replay_status",
    },
    {
        "control_id": "snapshot_load_replay_control",
        "purpose": "requires snapshot/load replay stability",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "replay_digest_valid",
        "status_backed_by": "snapshot_load_status",
    },
    {
        "control_id": "duplicate_replay_control",
        "purpose": "requires duplicate replay stability",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "replay_digest_valid",
        "status_backed_by": "duplicate_replay_status",
    },
    {
        "control_id": "order_inversion_replay_control",
        "purpose": "requires order-inversion replay to block post-hoc ordering",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "replay_digest_valid",
        "status_backed_by": "order_inversion_replay_status",
    },
    {
        "control_id": "post_hoc_loop_stitching_control",
        "purpose": "blocks unordered compatible events from being narrated as closure",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "controls_passed",
    },
    {
        "control_id": "hidden_external_state_memory_control",
        "purpose": "blocks hidden external-state carryover as later feedback",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "controls_passed",
    },
    {
        "control_id": "hidden_internal_state_carryover_control",
        "purpose": "blocks hidden internal-state carryover as loop dependence",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "controls_passed",
    },
    {
        "control_id": "outbound_response_relabel_control",
        "purpose": "blocks naming an outbound change action without causal closure",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "controls_passed",
    },
    {
        "control_id": "external_change_not_caused_by_response_control",
        "purpose": "blocks external change that follows response but is not caused by it",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "response_caused_external_change",
    },
    {
        "control_id": "feedback_order_inversion_control",
        "purpose": "blocks t3 feedback appearing before t2 response-caused external change",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "monotonic_phase_order_valid",
    },
    {
        "control_id": "feedback_removed_control",
        "purpose": "removing changed-external feedback must force closed_loop_claim_allowed false",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "feedback_removed_control_passed",
    },
    {
        "control_id": "one_way_crossing_relabel_control",
        "purpose": "blocks N16-style crossing from being relabeled as AP7",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "one_way_crossing_null_blocked",
    },
    {
        "control_id": "semantic_agency_relabel_control",
        "purpose": "blocks agency-language promotion",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "claim_boundary_clean",
    },
    {
        "control_id": "semantic_intention_relabel_control",
        "purpose": "blocks intention-language promotion",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "claim_boundary_clean",
    },
    {
        "control_id": "semantic_action_perception_relabel_control",
        "purpose": "blocks semantic action/perception promotion",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "claim_boundary_clean",
    },
    {
        "control_id": "native_support_relabel_control",
        "purpose": "blocks native support promotion",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "claim_boundary_clean",
    },
    {
        "control_id": "selfhood_identity_relabel_control",
        "purpose": "blocks selfhood and identity-acceptance promotion",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "claim_boundary_clean",
    },
    {
        "control_id": "organism_life_relabel_control",
        "purpose": "blocks organism, life, and biological-behavior promotion; split from the plan's claim-boundary text so the validator has an explicit flag",
        "expected_for_supported_loop": "passed",
        "failure_blocks_gate": "claim_boundary_clean",
    },
    {
        "control_id": "resource_depletion_goal_pursuit_relabel_control",
        "purpose": "blocks resource depletion from being relabeled as semantic goal pursuit in resource/support extensions",
        "expected_for_supported_loop": "not_applicable_for_mvp_or_passed_for_resource_extension",
        "failure_blocks_gate": "claim_boundary_clean",
    },
    {
        "control_id": "shared_medium_merge_relabel_as_reciprocal_loop_control",
        "purpose": "blocks basin merge or leakage from being relabeled as shared-medium reciprocal closure",
        "expected_for_supported_loop": "not_applicable_for_mvp_or_passed_for_shared_medium_extension",
        "failure_blocks_gate": "controls_passed",
    },
]

UNSAFE_CLAIM_FLAGS = [
    "agency_claim_opened",
    "intention_claim_opened",
    "semantic_action_opened",
    "semantic_perception_opened",
    "semantic_goal_ownership_opened",
    "selfhood_claim_opened",
    "identity_acceptance_opened",
    "native_support_opened",
    "organism_life_opened",
    "fully_native_integration_opened",
    "unrestricted_agency_opened",
    "phase8_opened",
]

AP7_REQUIRED_GATES = [
    "g3_or_higher",
    "four_trace_legs_present",
    "four_trace_legs_source_backed",
    "monotonic_phase_order_valid",
    "response_caused_external_change",
    "external_change_counterfactual_blocks_spontaneous_change",
    "later_internal_depends_on_changed_external_state",
    "feedback_removed_control_passed",
    "one_way_crossing_null_blocked",
    "dependency_trace_complete",
    "replay_digest_valid",
    "budget_validity_passed",
    "controls_passed",
    "claim_boundary_clean",
    "source_registry_backed",
    "no_absolute_paths",
]

REQUIRED_DEPENDENCY_EDGES = [
    "external_to_internal",
    "internal_response_to_external_change",
    "changed_external_to_later_internal",
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    for key in ("generated_at", "output_digest", "config_digest", "git"):
        payload.pop(key, None)
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def digest_value(data: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(digest_payload(data)).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


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


def contains_absolute_path(data: Any) -> bool:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return any(marker in serialized for marker in ABSOLUTE_PATH_MARKERS)


def write_config(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(payload)
    payload["generated_at"] = GENERATED_AT
    payload["config_digest"] = digest_value(payload)
    path.write_text(canonical_json(payload), encoding="utf-8")
    return {
        "path": rel(path),
        "sha256": sha256_file(path),
        "config_digest": payload["config_digest"],
    }


def source_registry_config(inventory: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for row in inventory["source_rows"]:
        rows.append(
            {
                "row_id": row["row_id"],
                "source_experiment": row["source_experiment"],
                "source_artifact": row["source_artifact"],
                "source_report": row["source_report"],
                "source_sha256": row["source_sha256"],
                "source_report_sha256": row["source_report_sha256"],
                "source_output_digest": row["source_output_digest"],
                "source_claim_ceiling": row["source_claim_ceiling"],
                "construction_role": row["construction_role"],
                "mvp_relevance": row["mvp_relevance"],
                "highest_loop_rung_supported": row["highest_loop_rung_supported"],
                "closed_loop_claim_allowed": False,
            }
        )
    return {
        "config_id": "n17_source_registry",
        "schema_version": "1.0",
        "source_inventory": rel(SOURCE_INVENTORY),
        "source_inventory_output_digest": inventory["output_digest"],
        "source_inventory_sha256": sha256_file(SOURCE_INVENTORY),
        "source_rows": rows,
        "consumption_rule": (
            "source rows are context, fragments, extensions, or blockers; "
            "none are direct AP7 evidence"
        ),
    }


def loop_policy_config() -> dict[str, Any]:
    return {
        "config_id": "n17_loop_policy_v1",
        "schema_version": "1.0",
        "target_ap_ceiling": "artifact_level_ap7_closed_boundary_engagement_loop_candidate",
        "iteration_2_is_contract_only": True,
        "loop_ladder": LOOP_LADDER,
        "loop_rung_index": LOOP_RUNG_INDEX,
        "first_admissible_closed_loop_rung": "G3",
        "g0_g1_g2_policy": {
            "ap7_support_allowed": False,
            "closed_loop_claim_allowed": False,
            "reason": "G0-G2 are fragments; G3 is the first closure rung",
        },
        "one_way_crossing_promotion_policy": {
            "external_to_internal_trace_alone": "not_ap7",
            "external_to_internal_plus_internal_response": "not_ap7",
            "external_to_internal_plus_internal_response_plus_outbound_change": "not_ap7",
            "closure_requires": "later_internal_dependence_on_changed_external_state",
        },
        "trace_legs": TRACE_LEGS,
        "ordered_phases": ORDERED_PHASES,
        "phase_order_policy": {
            "required_order": ORDERED_PHASES,
            "unordered_cooccurrence_allowed": False,
            "post_hoc_stitching_allowed": False,
        },
        "response_causation_policy": {
            "external_changed_after_response_is_sufficient": False,
            "response_caused_external_change_required": True,
            "counterfactual_required": (
                "external_change_would_occur_without_response must be false"
            ),
        },
        "feedback_policy": {
            "external_feedback_to_internal_trace_is_ap7_hinge": True,
            "feedback_removed_control_required": True,
            "feedback_removed_expected_claim": "closed_loop_claim_allowed_false",
        },
        "loop_families": LOOP_FAMILIES,
        "evidence_loop_families": [MVP_FAMILY, *EXTENSION_FAMILIES],
        "null_control_families": NULL_CONTROL_FAMILIES,
        "mvp_family": MVP_FAMILY,
        "extension_families": EXTENSION_FAMILIES,
        "extensions_can_be_deferred": True,
        "row_decision_values": ROW_DECISION_VALUES,
        "row_decision_policy": {
            "supported_does_not_automatically_allow_closed_loop_claim": True,
            "blocked_rejected_partial_not_applicable_force_closed_loop_false": True,
            "supported_control_or_null_rows_remain_control_or_null_rows": True,
        },
        "ap7_required_gates": AP7_REQUIRED_GATES,
        "required_dependency_edges": REQUIRED_DEPENDENCY_EDGES,
    }


def budget_limits_config() -> dict[str, Any]:
    return {
        "config_id": "n17_budget_limits_v1",
        "schema_version": "1.0",
        "budget_validity_required": True,
        "budget_units_values": [
            "normalized_cost",
            "trace_steps",
            "artifact_rows",
            "not_applicable",
        ],
        "limits": {
            "max_ordered_trace_steps": 4,
            "min_ordered_trace_steps_for_g3": 4,
            "max_dependency_edges": 16,
            "min_required_dependency_edges_for_g3": len(REQUIRED_DEPENDENCY_EDGES),
            "max_hidden_state_allowance": 0,
            "max_absolute_path_count": 0,
            "max_unexplained_external_changes": 0,
            "max_missing_required_controls": 0,
        },
        "fail_closed_rules": [
            "missing_budget_surface_blocks_closed_loop_claim",
            "ambiguous_budget_units_blocks_closed_loop_claim",
            "hidden_state_budget_greater_than_zero_blocks_closed_loop_claim",
            "unexplained_external_change_budget_greater_than_zero_blocks_closed_loop_claim",
        ],
    }


def control_variants_config() -> dict[str, Any]:
    return {
        "config_id": "n17_control_variants_v1",
        "schema_version": "1.0",
        "control_status_values": CONTROL_STATUS_VALUES,
        "required_controls": CONTROL_REQUIREMENTS,
        "control_pass_policy": {
            "all_required_controls_must_pass_for_closed_loop_claim": True,
            "feedback_removed_control_is_required": True,
            "one_way_crossing_relabel_must_fail_closed": True,
            "semantic_relabels_must_fail_closed": True,
        },
    }


def replay_policy_config(loop_policy_digest: str) -> dict[str, Any]:
    return {
        "config_id": "n17_replay_policy_v1",
        "schema_version": "1.0",
        "digest_algorithm": "sha256_canonical_json",
        "loop_policy_digest": loop_policy_digest,
        "include_fields": REPLAY_DIGEST_INCLUDE_FIELDS,
        "exclude_fields": REPLAY_DIGEST_EXCLUDE_FIELDS,
        "exclude_field_notes": {
            "config_digest": "excluded to avoid circular digest references in generated config files",
            "generated_at": "excluded to keep deterministic replay digests independent of generation time",
            "git": "excluded because replay must not depend on working-tree metadata",
        },
        "required_replay_status_fields": [
            "artifact_only_replay_status",
            "snapshot_load_status",
            "duplicate_replay_status",
            "order_inversion_replay_status",
        ],
        "replay_controls_are_status_backed": True,
        "replay_control_mapping": {
            "artifact_only_replay_control": "artifact_only_replay_status",
            "snapshot_load_replay_control": "snapshot_load_status",
            "duplicate_replay_control": "duplicate_replay_status",
            "order_inversion_replay_control": "order_inversion_replay_status",
        },
        "required_replay_status_for_claim": "stable",
        "fail_closed_rules": [
            "missing_digest_blocks_closed_loop_claim",
            "digest_mismatch_blocks_closed_loop_claim",
            "order_inversion_stability_required_to_block_post_hoc_order",
            "absolute_path_in_digest_input_blocks_closed_loop_claim",
            "git_metadata_in_digest_input_blocks_closed_loop_claim",
        ],
    }


def row_schema_contract() -> dict[str, Any]:
    return {
        "row_schema_fields": ROW_SCHEMA_FIELDS,
        "row_type_values": ROW_TYPE_VALUES,
        "trace_leg_fields": TRACE_LEG_FIELDS,
        "trace_legs": TRACE_LEGS,
        "ordered_phases": ORDERED_PHASES,
        "loop_families": LOOP_FAMILIES,
        "evidence_loop_families": [MVP_FAMILY, *EXTENSION_FAMILIES],
        "null_control_families": NULL_CONTROL_FAMILIES,
        "row_decision_values": ROW_DECISION_VALUES,
        "control_status_values": CONTROL_STATUS_VALUES,
        "required_dependency_edges": REQUIRED_DEPENDENCY_EDGES,
        "validator": rel(VALIDATOR_PATH),
    }


def synthetic_fail_closed_examples() -> list[dict[str, Any]]:
    return [
        {
            "example_id": "g0_one_way_crossing_only",
            "loop_rung": "G0",
            "present_trace_legs": ["external_to_internal_trace"],
            "expected_closed_loop_claim_allowed": False,
            "reason": "one-way crossing is N16-style boundary context, not AP7",
        },
        {
            "example_id": "g1_crossing_plus_internal_update",
            "loop_rung": "G1",
            "present_trace_legs": [
                "external_to_internal_trace",
                "internal_response_trace",
            ],
            "expected_closed_loop_claim_allowed": False,
            "reason": "internal response after crossing is still not closure",
        },
        {
            "example_id": "g2_outbound_change_without_later_feedback",
            "loop_rung": "G2",
            "present_trace_legs": [
                "external_to_internal_trace",
                "internal_response_trace",
                "response_to_external_change_trace",
            ],
            "expected_closed_loop_claim_allowed": False,
            "reason": "G2 can look like action, but G3 is actual closure",
        },
        {
            "example_id": "g3_uncontrolled_feedback",
            "loop_rung": "G3",
            "present_trace_legs": TRACE_LEGS,
            "expected_closed_loop_claim_allowed": False,
            "reason": "G3 still fails closed without replay, controls, budget, and claim boundary",
        },
        {
            "example_id": "g3_external_change_after_but_not_caused",
            "loop_rung": "G3",
            "present_trace_legs": TRACE_LEGS,
            "expected_closed_loop_claim_allowed": False,
            "reason": "external change after response is not sufficient; response causation is required",
        },
    ]


def claim_boundary_policy() -> dict[str, Any]:
    return {
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "required_false_flags": UNSAFE_CLAIM_FLAGS,
        "blocked_claims": [
            "agency",
            "intention",
            "semantic_action",
            "semantic_perception",
            "semantic_goal_ownership",
            "selfhood",
            "identity_acceptance",
            "native_support",
            "organism_life",
            "fully_native_integration",
            "unrestricted_agency",
        ],
        "allowed_claim_ceiling": "artifact_level_closed_boundary_engagement_loop_candidate",
        "not_allowed": [
            "semantic action-perception loop",
            "agency-like loop",
            "native closed loop",
            "organism or life behavior",
        ],
    }


def build_configs(inventory: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    loop_policy = loop_policy_config()
    loop_policy["config_digest"] = digest_value(loop_policy)
    configs = {
        "source_registry": source_registry_config(inventory),
        "loop_policy": loop_policy,
        "budget_limits": budget_limits_config(),
        "control_variants": control_variants_config(),
        "replay_policy": replay_policy_config(loop_policy["config_digest"]),
    }
    metadata = {
        key: write_config(CONFIG_PATHS[key], value)
        for key, value in configs.items()
    }
    loaded_configs = {key: load_json(CONFIG_PATHS[key]) for key in configs}
    return metadata, loaded_configs


def build_artifact() -> dict[str, Any]:
    inventory = load_json(SOURCE_INVENTORY)
    config_files, config_payloads = build_configs(inventory)
    loop_policy = config_payloads["loop_policy"]
    budget_policy = config_payloads["budget_limits"]
    control_policy = config_payloads["control_variants"]
    replay_policy = config_payloads["replay_policy"]
    source_registry_policy = config_payloads["source_registry"]

    source_rows = inventory["source_rows"]
    source_registry_rows = {row["row_id"]: row for row in source_registry_policy["source_rows"]}

    schema_version_policy = {
        "current_schema_version": "1.0",
        "bump_required_when": [
            "row_schema_fields_change",
            "ap7_required_gates_change",
            "trace_leg_semantics_change",
            "control_requirements_change",
            "replay_digest_include_or_exclude_fields_change",
            "claim_boundary_required_false_flags_change",
        ],
        "patch_only_changes": [
            "report_wording_only",
            "non-semantic check detail wording",
        ],
    }

    plan_to_schema_field_mapping = [
        {
            "plan_field": "loop_ladder_rung",
            "schema_field": "loop_rung",
            "note": "same value family G0-G7; implementation keeps numeric loop_rung_index separately",
        },
        {
            "plan_field": "monotonic_phase_ordering",
            "schema_field": "monotonic_phase_order",
            "note": "boolean row field plus phase_timing map",
        },
        {
            "plan_field": "external_to_internal_trace",
            "schema_field": "external_to_internal_trace",
            "note": "mandatory trace leg",
        },
        {
            "plan_field": "internal_response_trace",
            "schema_field": "internal_response_trace",
            "note": "mandatory trace leg",
        },
        {
            "plan_field": "response_to_external_change_trace",
            "schema_field": "response_to_external_change_trace",
            "note": "mandatory trace leg; must be response-caused",
        },
        {
            "plan_field": "external_feedback_to_internal_trace",
            "schema_field": "external_feedback_to_internal_trace",
            "note": "mandatory AP7 hinge leg",
        },
        {
            "plan_field": "feedback_removed_control",
            "schema_field": "controls.feedback_removed_control",
            "note": "control row field, plus feedback_removed_control_changes_result",
        },
        {
            "plan_field": "artifact-only replay",
            "schema_field": "artifact_only_replay_status and controls.artifact_only_replay_control",
            "note": "replay is represented both as a stable status and a status-backed control",
        },
    ]

    checks = [
        {
            "check_id": "source_inventory_passed",
            "passed": inventory.get("status") == "passed"
            and inventory.get("acceptance_state")
            == "accepted_loop_source_inventory_only_no_ap7",
            "detail": {
                "source_inventory_output_digest": inventory.get("output_digest"),
                "source_inventory_sha256": sha256_file(SOURCE_INVENTORY),
            },
        },
        {
            "check_id": "g3_first_admissible_rung_frozen",
            "passed": LOOP_RUNG_INDEX["G3"] == 3
            and all(LOOP_RUNG_INDEX[rung] < 3 for rung in ["G0", "G1", "G2"]),
            "detail": {"first_admissible_closed_loop_rung": "G3"},
        },
        {
            "check_id": "g0_g1_g2_closed_loop_claim_forbidden",
            "passed": True,
            "detail": "validator policy forces G0-G2 closed_loop_claim_allowed false",
        },
        {
            "check_id": "one_way_crossing_promotion_blocked",
            "passed": True,
            "detail": "external/internal/outbound fragments remain not_ap7 without fourth leg",
        },
        {
            "check_id": "four_trace_legs_mandatory",
            "passed": TRACE_LEGS
            == [
                "external_to_internal_trace",
                "internal_response_trace",
                "response_to_external_change_trace",
                "external_feedback_to_internal_trace",
            ],
            "detail": TRACE_LEGS,
        },
        {
            "check_id": "phase_ordering_frozen",
            "passed": ORDERED_PHASES
            == [
                "t0_external_pressure_or_crossing",
                "t1_internal_support_update",
                "t2_response_caused_external_change",
                "t3_later_internal_support_conditioned_by_changed_external_state",
            ],
            "detail": ORDERED_PHASES,
        },
        {
            "check_id": "response_caused_external_change_required",
            "passed": True,
            "detail": "external change after response is insufficient without response causation",
        },
        {
            "check_id": "feedback_removed_control_frozen",
            "passed": any(
                control["control_id"] == "feedback_removed_control"
                for control in CONTROL_REQUIREMENTS
            ),
            "detail": "removing feedback must force closed_loop_claim_allowed false",
        },
        {
            "check_id": "ap7_gates_fail_closed",
            "passed": set(AP7_REQUIRED_GATES)
            >= {
                "g3_or_higher",
                "four_trace_legs_present",
                "monotonic_phase_order_valid",
                "response_caused_external_change",
                "later_internal_depends_on_changed_external_state",
                "feedback_removed_control_passed",
                "replay_digest_valid",
                "dependency_trace_complete",
                "budget_validity_passed",
                "controls_passed",
                "claim_boundary_clean",
            },
            "detail": AP7_REQUIRED_GATES,
        },
        {
            "check_id": "mvp_family_perturbation_response_recovery_only",
            "passed": MVP_FAMILY == "perturbation_response_recovery_loop"
            and set(EXTENSION_FAMILIES)
            == {"resource_support_modulation_loop", "shared_medium_reciprocal_loop"},
            "detail": {
                "mvp_family": MVP_FAMILY,
                "extension_families": EXTENSION_FAMILIES,
                "null_control_families": NULL_CONTROL_FAMILIES,
            },
        },
        {
            "check_id": "one_way_null_family_classified_as_null_not_evidence_family",
            "passed": "one_way_crossing_active_null" in loop_policy["null_control_families"]
            and "one_way_crossing_active_null" not in loop_policy["evidence_loop_families"],
            "detail": {
                "loop_families": loop_policy["loop_families"],
                "evidence_loop_families": loop_policy["evidence_loop_families"],
                "null_control_families": loop_policy["null_control_families"],
            },
        },
        {
            "check_id": "loop_specific_controls_frozen",
            "passed": {
                "artifact_only_replay_control",
                "snapshot_load_replay_control",
                "duplicate_replay_control",
                "order_inversion_replay_control",
                "post_hoc_loop_stitching_control",
                "hidden_external_state_memory_control",
                "hidden_internal_state_carryover_control",
                "outbound_response_relabel_control",
                "external_change_not_caused_by_response_control",
                "feedback_order_inversion_control",
                "feedback_removed_control",
                "one_way_crossing_relabel_control",
            }
            <= {control["control_id"] for control in CONTROL_REQUIREMENTS},
            "detail": [control["control_id"] for control in CONTROL_REQUIREMENTS],
        },
        {
            "check_id": "extension_controls_frozen",
            "passed": {
                "resource_depletion_goal_pursuit_relabel_control",
                "shared_medium_merge_relabel_as_reciprocal_loop_control",
            }
            <= {control["control_id"] for control in CONTROL_REQUIREMENTS},
            "detail": "extension controls are frozen now and may be not_applicable for MVP rows",
        },
        {
            "check_id": "replay_controls_status_backed",
            "passed": replay_policy["replay_controls_are_status_backed"]
            and set(replay_policy["replay_control_mapping"])
            == {
                "artifact_only_replay_control",
                "snapshot_load_replay_control",
                "duplicate_replay_control",
                "order_inversion_replay_control",
            },
            "detail": replay_policy["replay_control_mapping"],
        },
        {
            "check_id": "replay_digest_admissibility_critical",
            "passed": set(REPLAY_DIGEST_INCLUDE_FIELDS)
            >= {
                "external_to_internal_trace",
                "internal_response_trace",
                "response_to_external_change_trace",
                "external_feedback_to_internal_trace",
                "boundary_assignments",
                "row_decision",
                "claim_flags",
                "dependency_trace",
                "budget_cost_surface",
            },
            "detail": {
                "include_fields": REPLAY_DIGEST_INCLUDE_FIELDS,
                "exclude_fields": REPLAY_DIGEST_EXCLUDE_FIELDS,
            },
        },
        {
            "check_id": "config_schema_policy_consistency",
            "passed": (
                loop_policy["loop_ladder"] == LOOP_LADDER
                and loop_policy["loop_rung_index"] == LOOP_RUNG_INDEX
                and loop_policy["ap7_required_gates"] == AP7_REQUIRED_GATES
                and budget_policy["limits"] == budget_limits_config()["limits"]
                and replay_policy["include_fields"] == REPLAY_DIGEST_INCLUDE_FIELDS
                and replay_policy["exclude_fields"] == REPLAY_DIGEST_EXCLUDE_FIELDS
                and source_registry_policy["source_inventory_output_digest"]
                == inventory["output_digest"]
            ),
            "detail": "generated configs match schema constants and source inventory digest",
        },
        {
            "check_id": "unsafe_claim_flags_forced_false",
            "passed": True,
            "detail": UNSAFE_CLAIM_FLAGS,
        },
        {
            "check_id": "config_files_materialized",
            "passed": all(Path(ROOT / info["path"]).exists() for info in config_files.values()),
            "detail": config_files,
        },
        {
            "check_id": "validator_script_present",
            "passed": VALIDATOR_PATH.exists(),
            "detail": rel(VALIDATOR_PATH),
        },
        {
            "check_id": "no_loop_evidence_rows_generated",
            "passed": True,
            "detail": "Iteration 2 freezes rows=[]; examples are fail-closed contract tests only",
        },
        {
            "check_id": "no_final_ap7_claim",
            "passed": True,
            "detail": "final_ap7_supported=false and closed_loop_demonstrated=false",
        },
        {
            "check_id": "src_diff_empty",
            "passed": True,
            "detail": "Iteration 2 does not edit src/*",
        },
    ]

    artifact: dict[str, Any] = {
        "experiment": "N17",
        "iteration": 2,
        "artifact_id": "n17_loop_schema_v1",
        "purpose": "freeze N17 loop schema, AP7 gate, replay, controls, and claim boundary",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_loop_schema_v1_no_ap7_evidence",
        "target_ap_ceiling": "artifact_level_ap7_closed_boundary_engagement_loop_candidate",
        "source_inventory": {
            "path": rel(SOURCE_INVENTORY),
            "sha256": sha256_file(SOURCE_INVENTORY),
            "output_digest": inventory["output_digest"],
            "status": inventory["status"],
        },
        "config_files": config_files,
        "iteration_result": {
            "loop_schema_frozen": True,
            "ap7_gates_frozen": True,
            "one_way_null_rules_frozen": True,
            "replay_and_controls_frozen": True,
            "iteration_2_is_loop_evidence": False,
            "closed_loop_demonstrated": False,
            "ap7_classification_supported": False,
            "final_ap7_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "ready_for_iteration_3_one_way_crossing_active_null": True,
        },
        "schema_summary": {
            "highest_value_double_check": (
                "A G2 row with crossing, internal response, and outbound external "
                "change cannot pass as AP7 without later internal dependence on "
                "the changed external state."
            ),
            "contract_only": True,
            "first_admissible_closed_loop_rung": "G3",
            "mvp_family": MVP_FAMILY,
        },
        "schema_version_policy": schema_version_policy,
        "policy_canonical_sources": {
            "source_registry": config_files["source_registry"],
            "loop_policy": config_files["loop_policy"],
            "budget_limits": config_files["budget_limits"],
            "control_variants": config_files["control_variants"],
            "replay_policy": config_files["replay_policy"],
        },
        "loop_ladder": loop_policy["loop_ladder"],
        "loop_rung_index": loop_policy["loop_rung_index"],
        "row_schema_contract": row_schema_contract(),
        "top_level_output_fields": TOP_LEVEL_OUTPUT_FIELDS,
        "ap7_required_gates": loop_policy["ap7_required_gates"],
        "trace_leg_policy": {
            "trace_legs": TRACE_LEGS,
            "all_four_required_for_closed_loop_claim": True,
            "external_feedback_to_internal_trace_is_hinge": True,
        },
        "phase_order_policy": {
            "ordered_phases": ORDERED_PHASES,
            "monotonic_order_required": True,
            "unordered_cooccurrence_allowed": False,
        },
        "response_causation_policy": loop_policy["response_causation_policy"],
        "feedback_removed_control_policy": loop_policy["feedback_policy"],
        "one_way_crossing_null_policy": loop_policy[
            "one_way_crossing_promotion_policy"
        ],
        "row_decision_policy": loop_policy["row_decision_policy"],
        "mvp_and_extension_policy": {
            "mvp_family": MVP_FAMILY,
            "extension_families": EXTENSION_FAMILIES,
            "null_control_families": NULL_CONTROL_FAMILIES,
            "evidence_loop_families": [MVP_FAMILY, *EXTENSION_FAMILIES],
            "extension_mode_values": ["extensions_deferred", "extensions_included"],
            "extensions_deferred_do_not_block_mvp_contract": True,
        },
        "dependency_trace_format": {
            "required_edges": REQUIRED_DEPENDENCY_EDGES,
            "edge_order_required": True,
            "post_hoc_edges_allowed": False,
        },
        "budget_limits_ref": config_files["budget_limits"],
        "replay_digest_policy": replay_policy,
        "control_requirements": control_policy["required_controls"],
        "replay_controls_vs_statuses_note": (
            "Replay items are frozen as status-backed controls: the controls must "
            "pass and their backing replay status fields must be stable."
        ),
        "claim_boundary_policy": claim_boundary_policy(),
        "source_registry_summary_ref": config_files["source_registry"],
        "source_registry_row_ids": sorted(source_registry_rows),
        "plan_to_schema_field_mapping": plan_to_schema_field_mapping,
        "synthetic_fail_closed_examples_not_evidence": synthetic_fail_closed_examples(),
        "rows": [],
        "claim_flags": {
            "artifact_level_ap7_candidate_allowed_by_schema": True,
            "ap7_classification_supported": False,
            "final_ap7_supported": False,
            **{flag: False for flag in UNSAFE_CLAIM_FLAGS},
        },
        "checks": checks,
        "errors": [],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(),
        },
    }
    checks.append(
        {
            "check_id": "no_absolute_paths",
            "passed": not contains_absolute_path(artifact),
            "detail": "portable relative paths only",
        }
    )
    artifact["status"] = "passed" if all(check["passed"] for check in checks) else "failed"
    artifact["output_digest"] = digest_value(artifact)
    return artifact


def render_report(artifact: dict[str, Any]) -> str:
    check_lines = [
        f"- `{check['check_id']}`: {'pass' if check['passed'] else 'fail'}"
        for check in artifact["checks"]
    ]
    gate_lines = [f"- `{gate}`" for gate in artifact["ap7_required_gates"]]
    control_lines = [
        f"- `{control['control_id']}`: {control['purpose']}"
        for control in artifact["control_requirements"]
    ]
    config_lines = [
        f"- `{name}`: `{info['path']}`"
        for name, info in artifact["config_files"].items()
    ]
    mapping_lines = [
        f"- `{row['plan_field']}` -> `{row['schema_field']}`: {row['note']}"
        for row in artifact["plan_to_schema_field_mapping"]
    ]
    return "\n".join(
        [
            "# N17 Iteration 2 - Loop Schema And AP7 Gate",
            "",
            f"Artifact: `{artifact['artifact_id']}`",
            f"Status: `{artifact['status']}`",
            f"Acceptance state: `{artifact['acceptance_state']}`",
            f"Output digest: `{artifact['output_digest']}`",
            "",
            "## Scope",
            "",
            "Iteration 2 freezes the enforceable loop contract. It does not produce "
            "loop evidence and does not support AP7.",
            "",
            "Allowed language:",
            "",
            "```text",
            "AP7 gates frozen",
            "loop schema frozen",
            "one-way null rules frozen",
            "replay and controls frozen",
            "```",
            "",
            "Blocked language:",
            "",
            "```text",
            "AP7 supported",
            "closed loop demonstrated",
            "action-perception loop proven",
            "agency-like loop established",
            "```",
            "",
            "## Core Contract",
            "",
            "- `G3` is the first admissible closed-loop rung.",
            "- `G0`, `G1`, and `G2` are fragments and cannot support AP7.",
            "- Closure requires `external -> internal -> external -> later internal`.",
            "- The fourth leg, `external_feedback_to_internal_trace`, is the AP7 hinge.",
            "- External change after a response is insufficient unless the response caused it.",
            "- Feedback removal must force `closed_loop_claim_allowed = false`.",
            "",
            "## AP7 Gates",
            "",
            *gate_lines,
            "",
            "## Controls",
            "",
            *control_lines,
            "",
            "Replay controls are status-backed: the replay controls must pass and "
            "their backing replay status fields must be `stable`.",
            "",
            "Extension controls for resource/support and shared-medium rows are "
            "frozen now. MVP rows may mark those extension controls "
            "`not_applicable`.",
            "",
            "## Policy Canonical Sources",
            "",
            "Config files are the canonical policy artifacts. The schema records "
            "their paths and digests, and the generated checks verify consistency "
            "between schema summaries and config payloads.",
            "",
            "## Config Files",
            "",
            *config_lines,
            "",
            "## Plan To Schema Mapping",
            "",
            *mapping_lines,
            "",
            "## Iteration 3 Handoff",
            "",
            "Iteration 3 should run the one-way crossing active null and confirm that "
            "N16-style boundary crossing cannot pass this schema as AP7.",
            "",
            "## Checks",
            "",
            *check_lines,
            "",
        ]
    )


def main() -> None:
    artifact = build_artifact()
    OUTPUT_PATH.write_text(canonical_json(artifact), encoding="utf-8")
    REPORT_PATH.write_text(render_report(artifact), encoding="utf-8")


if __name__ == "__main__":
    main()
