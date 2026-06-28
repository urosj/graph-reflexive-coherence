#!/usr/bin/env python3
"""Build N26 Iteration 2 proxy divergence/collapse schema and controls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
SOURCE_INVENTORY = EXPERIMENT / "outputs" / "n26_source_inventory_and_scoped_substrate_admission.json"
OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_divergence_collapse_schema_and_controls.json"
REPORT = EXPERIMENT / "reports" / "n26_proxy_divergence_collapse_schema_and_controls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_proxy_divergence_collapse_schema_and_controls.py"
)

EXPECTED_I1_OUTPUT_DIGEST = "b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a"
EXPECTED_SOURCE_CONTRACT_ROW_DIGEST = (
    "5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61"
)
EXPECTED_SOURCE_CONSUMABLE_CONTRACT_ROW_DIGEST = (
    "99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec"
)

PD_LADDER = [
    {
        "rung": "PD0",
        "definition": "no source-current proxy evidence",
        "positive_proxy_support_allowed": False,
    },
    {
        "rung": "PD1",
        "definition": "proxy metric present, but not source-current or not lower-stack linked",
        "positive_proxy_support_allowed": False,
    },
    {
        "rung": "PD2",
        "definition": (
            "source-current proxy derivation candidate with target digest declared "
            "before use"
        ),
        "proxy_derivation_candidate_allowed": True,
        "proxy_divergence_allowed": False,
        "proxy_collapse_allowed": False,
    },
    {
        "rung": "PD3",
        "definition": "replay-backed proxy / basin contrast candidate",
        "requires_replay": ["artifact_replay", "snapshot_load_replay", "duplicate_replay", "order_control"],
        "proxy_divergence_allowed": False,
        "proxy_collapse_allowed": False,
    },
    {
        "rung": "PD4",
        "definition": "controlled proxy divergence candidate",
        "requires": [
            "proxy_metric_improves",
            "basin_persistence_or_deepening_stalls_or_degrades",
            "proxy_and_basin_measured_independently",
            "thresholds_and_target_declared_before_outcome_inspection",
            "negative_controls_fail_closed",
        ],
        "proxy_collapse_allowed": False,
    },
    {
        "rung": "PD5",
        "definition": "controlled proxy collapse candidate",
        "requires": [
            "proxy_optimized_path_fails_under_declared_perturbation",
            "basin_deepened_path_survives_same_perturbation_envelope",
            "perturbation_envelope_digest_identical_across_rows",
            "negative_controls_fail_closed",
        ],
    },
    {
        "rung": "PD6",
        "definition": (
            "N27-ready bounded proxy divergence / collapse evidence with scoped "
            "AP5 bridge candidate"
        ),
        "handoff_rung_only": True,
        "agency_claim_allowed": False,
    },
]

N26_CLOSEOUT_LADDER = [
    {"rung": "N26-C0", "definition": "initialized contract only"},
    {"rung": "N26-C1", "definition": "source inventory and scoped-substrate admission passed"},
    {"rung": "N26-C2", "definition": "proxy divergence / collapse schema frozen"},
    {"rung": "N26-C3", "definition": "active nulls fail closed"},
    {
        "rung": "N26-C4",
        "definition": "source-current proxy derivation and replay-backed contrast supported",
    },
    {"rung": "N26-C5", "definition": "controlled proxy divergence / collapse candidate supported"},
    {"rung": "N26-C6", "definition": "N27-ready bounded proxy divergence / collapse closeout"},
]

REQUIRED_CANDIDATE_FIELDS = [
    "row_id",
    "row_decision",
    "candidate_pd_ladder_rung",
    "source_current_inputs",
    "source_contract_row_digest",
    "source_consumable_contract_row_digest",
    "source_output_digest",
    "artifact_manifest",
    "all_artifact_sha256_match_file_contents",
    "row_specific_thresholds_declared_before_use",
    "scoped_mb6_substrate_consumption_record",
    "multi_basin_scope_id",
    "basin_ids_or_child_basin_ids",
    "n25_2_unscoped_consumption_allowed",
    "n25_2_unscoped_multi_basin_consumption_allowed",
    "front_capacity_companion_backfill_used",
    "proxy_metric_definition_digest",
    "proxy_derivation_policy_digest",
    "proxy_target_digest_declared_before_use",
    "proxy_policy_owner",
    "producer_mediated_target_derivation_counted_as_substrate",
    "lower_stack_input_trace",
    "proxy_metric_trace",
    "basin_persistence_capacity_trace",
    "support_coherence_floor_trace",
    "basin_deepening_comparison_trace",
    "proxy_vs_basin_delta_trace",
    "proxy_optimized_path_trace",
    "basin_deepened_path_trace",
    "perturbation_challenge_trace",
    "proxy_collapse_result_trace",
    "peer_or_control_basin_trace",
    "replay_result",
    "control_results",
    "ap5_dependency_status",
    "ap5_condition_reason",
    "claim_ceiling",
    "unsafe_claim_flags",
]

REQUIRED_ARTIFACT_ROLES = [
    "runtime_trace",
    "lower_stack_input_trace",
    "proxy_metric_trace",
    "basin_persistence_capacity_trace",
    "support_coherence_floor_trace",
    "basin_deepening_comparison_trace",
    "proxy_vs_basin_delta_trace",
    "proxy_optimized_path_trace",
    "basin_deepened_path_trace",
    "perturbation_challenge_trace",
    "proxy_collapse_result_trace",
    "peer_or_control_basin_trace",
    "replay_trace",
    "control_trace",
    "report",
    "closeout",
]

REQUIRED_ARTIFACT_ROLES_BY_PD_RUNG = {
    "PD2": [
        "runtime_trace",
        "lower_stack_input_trace",
        "proxy_metric_trace",
        "basin_persistence_capacity_trace",
        "support_coherence_floor_trace",
        "report",
    ],
    "PD3": [
        "runtime_trace",
        "lower_stack_input_trace",
        "proxy_metric_trace",
        "basin_persistence_capacity_trace",
        "support_coherence_floor_trace",
        "basin_deepening_comparison_trace",
        "proxy_vs_basin_delta_trace",
        "replay_trace",
        "report",
    ],
    "PD4": [
        "runtime_trace",
        "lower_stack_input_trace",
        "proxy_metric_trace",
        "basin_persistence_capacity_trace",
        "support_coherence_floor_trace",
        "basin_deepening_comparison_trace",
        "proxy_vs_basin_delta_trace",
        "peer_or_control_basin_trace",
        "replay_trace",
        "control_trace",
        "report",
    ],
    "PD5": [
        "runtime_trace",
        "lower_stack_input_trace",
        "proxy_metric_trace",
        "basin_persistence_capacity_trace",
        "support_coherence_floor_trace",
        "basin_deepening_comparison_trace",
        "proxy_vs_basin_delta_trace",
        "proxy_optimized_path_trace",
        "basin_deepened_path_trace",
        "perturbation_challenge_trace",
        "proxy_collapse_result_trace",
        "peer_or_control_basin_trace",
        "replay_trace",
        "control_trace",
        "report",
    ],
    "PD6": [
        "runtime_trace",
        "lower_stack_input_trace",
        "proxy_metric_trace",
        "basin_persistence_capacity_trace",
        "support_coherence_floor_trace",
        "basin_deepening_comparison_trace",
        "proxy_vs_basin_delta_trace",
        "proxy_optimized_path_trace",
        "basin_deepened_path_trace",
        "perturbation_challenge_trace",
        "proxy_collapse_result_trace",
        "peer_or_control_basin_trace",
        "replay_trace",
        "control_trace",
        "report",
        "closeout",
    ],
}

CONTROL_IDS = [
    "lower_stack_input_missing_control",
    "proxy_metric_not_replayable_control",
    "support_coherence_floor_missing_control",
    "proxy_basin_measurement_not_independent_control",
    "scoped_mb6_scope_id_missing_control",
    "derived_report_only_positive_row_control",
    "artifact_manifest_failure_control",
    "proxy_label_only_control",
    "post_hoc_target_digest_control",
    "hidden_proxy_policy_control",
    "proxy_only_improvement_control",
    "basin_degradation_hidden_by_proxy_control",
    "unscoped_mb6_consumption_control",
    "front_capacity_backfill_control",
    "peer_basin_missing_control",
    "perturbation_mismatch_control",
    "basin_deepened_survivor_missing_control",
    "AP5_gap_prose_only_control",
    "semantic_goal_relabel_control",
    "semantic_choice_relabel_control",
    "agency_relabel_control",
    "native_support_relabel_control",
    "sentience_relabel_control",
    "phase8_completion_relabel_control",
    "ant_ecology_relabel_control",
]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def collect_strings(data: Any) -> set[str]:
    strings: set[str] = set()
    if isinstance(data, str):
        strings.add(data)
    elif isinstance(data, list):
        for item in data:
            strings.update(collect_strings(item))
    elif isinstance(data, dict):
        for value in data.values():
            strings.update(collect_strings(value))
    return strings


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def build_output() -> dict[str, Any]:
    source_inventory = load_json(SOURCE_INVENTORY)
    unsafe_claim_flags = {claim: False for claim in UNSAFE_CLAIMS}
    ap5_dependency_status_enum = [
        "required_recorded",
        "missing_blocks_row",
        "not_applicable",
    ]
    proxy_policy_owner_enum = [
        "source_current_runtime",
        "declared_analysis_policy",
        "producer_mediated_blocks_substrate_claim",
        "hidden_policy_blocks_row",
    ]
    replay_schema = {
        "pd3_required_replay_modes": [
            "artifact_replay",
            "snapshot_load_replay",
            "duplicate_replay",
            "order_control",
        ],
        "pd3_if_any_required_replay_fails": "PD3_or_stronger_blocked",
        "pd4_pd5_required_control_summary": {
            "negative_controls_fail_closed": True,
            "failed_open_controls": 0,
            "not_run_required_controls": 0,
        },
    }
    scoped_mb6_schema = {
        "required_fields": [
            "scoped_mb6_substrate_consumption_record",
            "multi_basin_scope_id",
            "basin_ids_or_child_basin_ids",
            "n25_2_unscoped_consumption_allowed",
            "n25_2_unscoped_multi_basin_consumption_allowed",
            "front_capacity_companion_backfill_used",
        ],
        "required_values": {
            "n25_2_unscoped_consumption_allowed": False,
            "n25_2_unscoped_multi_basin_consumption_allowed": False,
            "front_capacity_companion_backfill_used": False,
        },
        "missing_scope_id_effect": "positive_proxy_support_blocked",
        "unscoped_consumption_effect": "positive_proxy_support_blocked",
    }
    artifact_manifest_schema = {
        "required_roles": REQUIRED_ARTIFACT_ROLES,
        "required_artifact_roles_by_pd_rung": REQUIRED_ARTIFACT_ROLES_BY_PD_RUNG,
        "per_artifact_required_fields": ["path", "sha256", "artifact_role"],
        "positive_support_blockers": [
            "artifact_missing",
            "sha256_mismatch",
            "artifact_role_missing",
            "derived_report_only_true",
            "absolute_path_present",
        ],
    }
    proxy_definition_schema = {
        "proxy_divergence_requires": PD_LADDER[4]["requires"],
        "proxy_collapse_requires": PD_LADDER[5]["requires"],
        "proxy_improvement_alone_effect": "blocked_below_PD4",
        "semantic_target_label_effect": "blocked_relabel",
    }
    candidate_row_schema = {
        "required_fields": REQUIRED_CANDIDATE_FIELDS,
        "required_source_digests": {
            "source_contract_row_digest": EXPECTED_SOURCE_CONTRACT_ROW_DIGEST,
            "source_consumable_contract_row_digest": EXPECTED_SOURCE_CONSUMABLE_CONTRACT_ROW_DIGEST,
            "source_output_digest": EXPECTED_I1_OUTPUT_DIGEST,
        },
        "derived_report_only_allowed_for_positive_support": False,
        "row_specific_thresholds_declared_before_use_required": True,
        "producer_mediated_target_derivation_counted_as_substrate_required_value": False,
        "artifact_manifest_schema": artifact_manifest_schema,
        "scoped_mb6_consumption_schema": scoped_mb6_schema,
    }
    ap5_dependency_schema = {
        "allowed_statuses": ap5_dependency_status_enum,
        "condition_reason_required": True,
        "ap5_gap_prose_only_control_required": True,
        "n15_n19_context_counts_as_native_ap5": False,
        "positive_proxy_rungs_require_ap5_dependency": ["PD2", "PD3", "PD4", "PD5", "PD6"],
        "not_applicable_allowed_only_for": [
            "inventory_rows",
            "schema_rows",
            "active_null_rows_without_proxy_or_target_formation_claim",
        ],
        "missing_status_effect": "row_blocks_at_AP5_gate",
    }
    control_schema = {
        "required_control_ids": CONTROL_IDS,
        "control_result_required_fields": [
            "control_id",
            "control_status",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "claim_allowed_when_control_triggers",
            "rung_effect",
            "control_satisfied_for_positive_row",
        ],
        "allowed_control_statuses": [
            "passed",
            "failed_closed",
            "failed_open",
            "not_run",
            "not_applicable",
        ],
        "failed_open_effect": "positive_proxy_support_invalidated",
        "not_run_required_control_effect": "PD4_PD5_PD6_blocked",
    }
    source_role_schema = {
        "source_role_split_immutable": True,
        "inventory_context_to_proxy_evidence_relabel_allowed": False,
        "source_rows": [
            {
                "source_id": row["source_id"],
                "source_classification": row["source_classification"],
                "source_role": row["source_role"],
                "may_consume_as": row["may_consume_as"],
                "must_not_consume_as": row["must_not_consume_as"],
            }
            for row in source_inventory["source_consumption_rows"]
        ],
    }

    checks = [
        check(
            "i1_source_inventory_passed",
            source_inventory.get("status") == "passed"
            and source_inventory.get("acceptance_state")
            == "accepted_source_inventory_scoped_substrate_admission_no_proxy_evidence",
            {
                "status": source_inventory.get("status"),
                "acceptance_state": source_inventory.get("acceptance_state"),
            },
        ),
        check(
            "source_inventory_digest_matches_expected",
            source_inventory.get("output_digest") == EXPECTED_I1_OUTPUT_DIGEST,
            {"output_digest": source_inventory.get("output_digest")},
        ),
        check(
            "source_contract_digests_match_i1",
            source_inventory.get("source_contract_row_digest")
            == EXPECTED_SOURCE_CONTRACT_ROW_DIGEST
            and source_inventory.get("source_consumable_contract_row_digest")
            == EXPECTED_SOURCE_CONSUMABLE_CONTRACT_ROW_DIGEST,
            {
                "source_contract_row_digest": source_inventory.get("source_contract_row_digest"),
                "source_consumable_contract_row_digest": source_inventory.get(
                    "source_consumable_contract_row_digest"
                ),
            },
        ),
        check(
            "source_role_split_frozen",
            all(row["may_consume_as"] and row["must_not_consume_as"] for row in source_role_schema["source_rows"])
            and source_role_schema["inventory_context_to_proxy_evidence_relabel_allowed"] is False,
            {"source_row_count": len(source_role_schema["source_rows"])},
        ),
        check(
            "pd_ladder_frozen",
            [row["rung"] for row in PD_LADDER] == ["PD0", "PD1", "PD2", "PD3", "PD4", "PD5", "PD6"],
            {"rungs": [row["rung"] for row in PD_LADDER]},
        ),
        check(
            "n26_closeout_ladder_frozen",
            [row["rung"] for row in N26_CLOSEOUT_LADDER]
            == ["N26-C0", "N26-C1", "N26-C2", "N26-C3", "N26-C4", "N26-C5", "N26-C6"],
            {"rungs": [row["rung"] for row in N26_CLOSEOUT_LADDER]},
        ),
        check(
            "candidate_row_required_fields_present",
            set(REQUIRED_CANDIDATE_FIELDS).issubset(candidate_row_schema["required_fields"]),
            {"field_count": len(candidate_row_schema["required_fields"])},
        ),
        check(
            "scoped_mb6_consumption_rules_frozen",
            scoped_mb6_schema["required_values"]
            == {
                "n25_2_unscoped_consumption_allowed": False,
                "n25_2_unscoped_multi_basin_consumption_allowed": False,
                "front_capacity_companion_backfill_used": False,
            },
            scoped_mb6_schema["required_values"],
        ),
        check(
            "ap5_dependency_enum_frozen",
            ap5_dependency_status_enum
            == ["required_recorded", "missing_blocks_row", "not_applicable"]
            and ap5_dependency_schema["n15_n19_context_counts_as_native_ap5"] is False,
            ap5_dependency_schema,
        ),
        check(
            "proxy_definition_rules_frozen",
            "basin_persistence_or_deepening_stalls_or_degrades"
            in proxy_definition_schema["proxy_divergence_requires"]
            and "perturbation_envelope_digest_identical_across_rows"
            in proxy_definition_schema["proxy_collapse_requires"],
            proxy_definition_schema,
        ),
        check(
            "proxy_policy_owner_enum_frozen",
            proxy_policy_owner_enum
            == [
                "source_current_runtime",
                "declared_analysis_policy",
                "producer_mediated_blocks_substrate_claim",
                "hidden_policy_blocks_row",
            ],
            proxy_policy_owner_enum,
        ),
        check(
            "artifact_roles_and_manifest_rules_frozen",
            len(REQUIRED_ARTIFACT_ROLES) == 16
            and "derived_report_only_true" in artifact_manifest_schema["positive_support_blockers"],
            artifact_manifest_schema,
        ),
        check(
            "artifact_roles_by_pd_rung_frozen",
            "proxy_collapse_result_trace" not in REQUIRED_ARTIFACT_ROLES_BY_PD_RUNG["PD2"]
            and "proxy_collapse_result_trace" in REQUIRED_ARTIFACT_ROLES_BY_PD_RUNG["PD5"]
            and "closeout" not in REQUIRED_ARTIFACT_ROLES_BY_PD_RUNG["PD4"]
            and "closeout" in REQUIRED_ARTIFACT_ROLES_BY_PD_RUNG["PD6"],
            REQUIRED_ARTIFACT_ROLES_BY_PD_RUNG,
        ),
        check(
            "ap5_not_applicable_constrained_for_positive_rows",
            ap5_dependency_schema["positive_proxy_rungs_require_ap5_dependency"]
            == ["PD2", "PD3", "PD4", "PD5", "PD6"]
            and "active_null_rows_without_proxy_or_target_formation_claim"
            in ap5_dependency_schema["not_applicable_allowed_only_for"],
            ap5_dependency_schema,
        ),
        check(
            "replay_requirements_frozen",
            replay_schema["pd3_required_replay_modes"]
            == ["artifact_replay", "snapshot_load_replay", "duplicate_replay", "order_control"]
            and replay_schema["pd4_pd5_required_control_summary"]["failed_open_controls"] == 0,
            replay_schema,
        ),
        check(
            "fail_closed_controls_frozen",
            set(CONTROL_IDS)
            == {
                "proxy_label_only_control",
                "post_hoc_target_digest_control",
                "hidden_proxy_policy_control",
                "proxy_only_improvement_control",
                "basin_degradation_hidden_by_proxy_control",
                "unscoped_mb6_consumption_control",
                "front_capacity_backfill_control",
                "peer_basin_missing_control",
                "perturbation_mismatch_control",
                "basin_deepened_survivor_missing_control",
                "AP5_gap_prose_only_control",
                "semantic_goal_relabel_control",
                "semantic_choice_relabel_control",
                "agency_relabel_control",
                "native_support_relabel_control",
                "sentience_relabel_control",
                "phase8_completion_relabel_control",
                "ant_ecology_relabel_control",
                "lower_stack_input_missing_control",
                "proxy_metric_not_replayable_control",
                "support_coherence_floor_missing_control",
                "proxy_basin_measurement_not_independent_control",
                "scoped_mb6_scope_id_missing_control",
                "derived_report_only_positive_row_control",
                "artifact_manifest_failure_control",
            },
            {"control_count": len(CONTROL_IDS)},
        ),
        check(
            "control_satisfied_for_positive_row_frozen",
            "control_satisfied_for_positive_row"
            in control_schema["control_result_required_fields"],
            control_schema["control_result_required_fields"],
        ),
        check(
            "source_current_derivation_blockers_frozen",
            {
                "lower_stack_input_missing_control",
                "proxy_metric_not_replayable_control",
                "support_coherence_floor_missing_control",
                "proxy_basin_measurement_not_independent_control",
                "scoped_mb6_scope_id_missing_control",
                "derived_report_only_positive_row_control",
                "artifact_manifest_failure_control",
            }.issubset(set(CONTROL_IDS)),
            {"control_ids": CONTROL_IDS},
        ),
        check(
            "no_positive_proxy_evidence_opened",
            True,
            "schema freeze only; no proxy derivation/divergence/collapse rows are produced",
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in unsafe_claim_flags.values()),
            unsafe_claim_flags,
        ),
    ]

    output: dict[str, Any] = {
        "artifact_id": "n26_proxy_divergence_collapse_schema_and_controls",
        "schema_version": "1.0",
        "experiment": "N26_proxy_divergence_proxy_collapse",
        "iteration": "2",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "freeze proxy divergence / collapse schema and fail-closed controls",
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "acceptance_state": "accepted_proxy_divergence_collapse_schema_frozen_no_proxy_evidence",
        "source_inventory_path": (
            "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/"
            "outputs/n26_source_inventory_and_scoped_substrate_admission.json"
        ),
        "source_inventory_output_digest": source_inventory.get("output_digest"),
        "source_contract_row_digest": EXPECTED_SOURCE_CONTRACT_ROW_DIGEST,
        "source_consumable_contract_row_digest": EXPECTED_SOURCE_CONSUMABLE_CONTRACT_ROW_DIGEST,
        "candidate_pd_ladder_rung": "not_assigned_schema_only",
        "n26_closeout_ceiling": "N26-C2_proxy_divergence_collapse_schema_frozen",
        "n26_closeout_ladder_rung_assigned": False,
        "positive_proxy_evidence_opened": False,
        "proxy_derivation_opened": False,
        "proxy_divergence_opened": False,
        "proxy_collapse_opened": False,
        "ap5_bridge_status": "not_supported_schema_only",
        "source_role_schema": source_role_schema,
        "pd_ladder": PD_LADDER,
        "n26_closeout_ladder": N26_CLOSEOUT_LADDER,
        "candidate_row_schema": candidate_row_schema,
        "scoped_mb6_consumption_schema": scoped_mb6_schema,
        "ap5_dependency_schema": ap5_dependency_schema,
        "proxy_definition_schema": proxy_definition_schema,
        "proxy_policy_owner_schema": {
            "allowed_values": proxy_policy_owner_enum,
            "producer_mediated_target_derivation_counted_as_substrate_required_value": False,
        },
        "artifact_manifest_schema": artifact_manifest_schema,
        "replay_schema": replay_schema,
        "control_schema": control_schema,
        "claim_boundary": {
            "claim_ceiling": (
                "schema/control freeze only; no proxy derivation, proxy divergence, "
                "proxy collapse, AP5 bridge, semantic goal, agency, native support, "
                "sentience, Phase 8, ant ecology, or unscoped multi-basin claim"
            ),
            "unsafe_claim_flags": unsafe_claim_flags,
        },
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    checks.append(
        check(
            "no_absolute_paths_in_records",
            not any(
                marker in value
                for value in collect_strings(output)
                for marker in ABSOLUTE_PATH_MARKERS
            ),
            "all paths are repository-relative",
        )
    )
    output["status"] = "passed" if all(item["passed"] for item in checks) else "failed"
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["checks"] = checks
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N26 Iteration 2 - Proxy Divergence / Collapse Schema And Controls",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Scope",
        "",
        "Iteration 2 freezes schema and controls only. It assigns no PD rung and opens no positive proxy evidence.",
        "",
        "## Frozen Ladders",
        "",
        "| Ladder | Rungs |",
        "| --- | --- |",
        f"| `PD` | `{', '.join(row['rung'] for row in output['pd_ladder'])}` |",
        f"| `N26-C` | `{', '.join(row['rung'] for row in output['n26_closeout_ladder'])}` |",
        "",
        "## Source Digests",
        "",
        "```text",
        f"source_inventory_output_digest = {output['source_inventory_output_digest']}",
        f"source_contract_row_digest = {output['source_contract_row_digest']}",
        f"source_consumable_contract_row_digest = {output['source_consumable_contract_row_digest']}",
        "```",
        "",
        "## Candidate Row Schema",
        "",
        f"Required field count: `{len(output['candidate_row_schema']['required_fields'])}`",
        "",
        "Required scoped substrate fields:",
        "",
        "```text",
        "\n".join(output["scoped_mb6_consumption_schema"]["required_fields"]),
        "```",
        "",
        "Artifact roles are rung-specific:",
        "",
        "| Rung | Required Roles |",
        "| --- | --- |",
    ]
    for rung, roles in output["artifact_manifest_schema"][
        "required_artifact_roles_by_pd_rung"
    ].items():
        lines.append(f"| `{rung}` | `{', '.join(roles)}` |")
    lines.extend(
        [
            "",
            "AP5 `not_applicable` is blocked for positive proxy rows:",
            "",
            "```text",
            "PD2...PD6 require required_recorded or missing_blocks_row",
            "not_applicable is limited to inventory/schema/null rows without proxy or target claims",
            "```",
            "",
        ]
    )
    lines.extend(
        [
            "## Controls",
            "",
            f"Required control count: `{len(output['control_schema']['required_control_ids'])}`",
            "",
            "```text",
            "\n".join(output["control_schema"]["required_control_ids"]),
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in output["checks"]:
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | "
            f"`{json.dumps(item['detail'], sort_keys=True, ensure_ascii=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            output["claim_boundary"]["claim_ceiling"],
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()
