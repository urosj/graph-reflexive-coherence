#!/usr/bin/env python3
"""Build N25.1 Iteration 2 multi-basin extension schema freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_1_multi_basin_extension_schema.json"
REPORT = EXPERIMENT / "reports" / "n25_1_multi_basin_extension_schema.md"
I1_OUTPUT_PATH = (
    "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
    "outputs/n25_1_source_crosswalk_and_gap_inventory.json"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.1-lgrc9v3-multi-basin-formation-extension-requirements/"
    "scripts/build_n25_1_multi_basin_extension_schema.py"
)

MB_LADDER = {
    "MB0": "no LGRC9V3 multi-basin evidence",
    "MB1": "causal spark / boundary-birth candidate recorded",
    "MB2": "topology integration / mechanical refinement recorded",
    "MB3": "post-refinement child-basin cores detected",
    "MB4": "replay-backed child-basin persistence candidate",
    "MB5": "control-backed native multi-basin formation candidate",
    "MB6": "N26-ready multi-basin substrate evidence",
}
N25_1_CLOSEOUT_LADDER = {
    "N25.1-C0": "initialized requirements bridge only",
    "N25.1-C1": "source crosswalk and gap inventory passed",
    "N25.1-C2": "multi-basin extension schema frozen",
    "N25.1-C3": "Phase 8 extension requirement matrix ready",
    "N25.1-C4": "closeout and Phase 8 handoff complete",
}
ROW_DECISION_VALUES = ["supported", "partial", "blocked", "rejected", "not_applicable"]
CONTROL_STATUS_VALUES = [
    "passed",
    "failed_closed",
    "failed_open",
    "not_run",
    "not_applicable",
]
MB_RUNG_STATUS_VALUES = [
    "not_assigned",
    "provisional_pending_replay",
    "provisional_pending_controls",
    "supported",
    "blocked",
    "rejected",
]
ARTIFACT_ROLE_VALUES = [
    "source_crosswalk",
    "schema_control_freeze",
    "causal_spark_candidate_trace",
    "boundary_birth_event_trace",
    "topology_integration_trace",
    "mechanical_refinement_trace",
    "refinement_lineage_trace",
    "post_refinement_flow_window_trace",
    "child_basin_core_trace",
    "child_basin_support_coherence_trace",
    "child_basin_boundary_trace",
    "child_basin_flux_trace",
    "child_basin_membership_trace",
    "merge_leakage_trace",
    "producer_intervention_ledger",
    "replay_trace",
    "snapshot_load_replay_trace",
    "duplicate_replay_trace",
    "order_inversion_control_trace",
    "negative_control_trace",
    "n26_handoff_trace",
    "report",
]
POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES = [
    "source_crosswalk",
    "schema_control_freeze",
    "producer_intervention_ledger",
    "report",
]
UNSAFE_CLAIMS = [
    "agency",
    "ant_ecology",
    "bf6_without_mb6",
    "fully_native_integration",
    "identity_acceptance",
    "independent_new_basin_formation_without_controls",
    "lgrc9v3_native_multi_basin_formation_without_runtime_evidence",
    "native_support",
    "organism_life",
    "phase8_implementation_complete",
    "semantic_choice",
    "semantic_learning",
    "sentience",
    "unrestricted_autonomy",
]
REQUIRED_FUTURE_EXTENSION_FIELDS = [
    "row_id",
    "source_iteration",
    "source_crosswalk_digest",
    "runtime_config_digest",
    "source_commit_or_source_digest",
    "source_current_inputs",
    "causal_spark_or_boundary_birth_event_id",
    "causal_spark_candidate_event_ref",
    "topology_integration_event_id",
    "mechanical_refinement_event_id",
    "refinement_lineage_map",
    "pre_refinement_topology_signature",
    "post_refinement_topology_signature",
    "post_refinement_flow_window",
    "child_basin_core_ids",
    "child_basin_support_floor_records",
    "child_basin_coherence_floor_records",
    "child_basin_boundary_records",
    "child_basin_flux_records",
    "child_basin_membership_digest",
    "parent_basin_relation_record",
    "merge_leakage_trace",
    "old_basin_thickening_control_result",
    "sub_basin_relabel_control_result",
    "producer_residue_classification",
    "replay_window",
    "replay_results",
    "control_results",
    "artifact_manifest",
    "artifact_paths",
    "artifact_sha256",
    "artifact_paths_equal_manifest_paths",
    "artifact_sha256_equal_manifest_sha256",
    "all_artifact_sha256_match_file_contents",
    "row_specific_thresholds_declared_before_use",
    "mb_ladder_rung",
    "mb_rung_status",
    "row_decision",
    "multi_basin_claim_allowed",
    "n26_consumption_allowed",
    "claim_ceiling",
    "unsafe_claim_flags",
    "row_digest",
    "output_digest",
]


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


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/")
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def build_causal_refinement_schema() -> dict[str, Any]:
    return {
        "schema_id": "n25_1_causal_refinement_event_schema_v1",
        "required_for_mb": ["MB1", "MB2", "MB3", "MB4", "MB5", "MB6"],
        "allowed_source_event_kinds": [
            "lgrc9v3_causal_spark_candidate",
            "lgrc9v3_boundary_birth_trial",
            "lgrc9v3_topology_integration_event",
            "grc9v3_hybrid_mechanical_expansion_consumed_by_lgrc3",
        ],
        "ordering_rules": {
            "causal_spark_or_boundary_birth_precedes_topology_integration": True,
            "topology_integration_precedes_post_refinement_flow_window": True,
            "post_refinement_flow_window_precedes_child_basin_extraction": True,
            "child_basin_extraction_precedes_replay_and_control_claims": True,
        },
        "required_fields": [
            "causal_spark_or_boundary_birth_event_id",
            "causal_spark_candidate_event_ref",
            "causal_spark_trigger_source",
            "event_time_key",
            "scheduler_event_index",
            "candidate_node_proper_time",
            "pre_refinement_topology_signature",
            "topology_integration_event_id",
            "mechanical_refinement_event_id",
            "refinement_lineage_map",
            "node_plus_packet_budget_audit",
        ],
        "fail_closed_if": [
            "old_synchronous_expansion_relabel_as_causal_extension",
            "topology_integration_event_missing",
            "lineage_map_missing",
            "node_plus_packet_budget_audit_missing_or_mismatched",
            "producer_topology_insertion_hidden",
            "event_order_inverted",
        ],
    }


def build_child_basin_schema() -> dict[str, Any]:
    return {
        "schema_id": "n25_1_child_basin_extraction_schema_v1",
        "first_admissible_mb_rung": "MB3",
        "child_basin_core_definition": (
            "a post-refinement basin core must be a source-current sink or basin "
            "seed with replayable support/coherence/boundary/flux records and a "
            "membership digest; module-node creation alone is not sufficient"
        ),
        "required_fields": [
            "post_refinement_flow_window",
            "child_basin_core_ids",
            "child_basin_support_floor_records",
            "child_basin_coherence_floor_records",
            "child_basin_boundary_records",
            "child_basin_flux_records",
            "child_basin_membership_digest",
            "parent_basin_relation_record",
            "old_basin_relation_trace",
            "same_parent_lineage_or_declared_birth_relation",
        ],
        "floor_record_requirements": {
            "support_floor_declared_before_use": True,
            "coherence_floor_declared_before_use": True,
            "boundary_integrity_floor_declared_before_use": True,
            "flux_or_leakage_bound_declared_before_use": True,
        },
        "fail_closed_if": [
            "child_identity_label_only",
            "module_node_created_equals_child_basin",
            "transient_sink_as_persistent_child_basin",
            "support_floor_missing",
            "coherence_floor_missing",
            "boundary_record_missing",
            "flux_record_missing",
            "membership_digest_missing",
            "parent_relation_missing",
        ],
    }


def build_replay_schema() -> dict[str, Any]:
    return {
        "schema_id": "n25_1_replay_schema_v1",
        "replay_status_values": CONTROL_STATUS_VALUES,
        "replay_result_field_convention": {
            "container_field": "replay_results",
            "allowed_granular_fields": [
                "artifact_replay_result",
                "snapshot_load_replay_result",
                "duplicate_replay_result",
                "handoff_reconstruction_replay_result",
            ],
            "granular_fields_may_be_nested_under_replay_results": True,
        },
        "mb4_requires": [
            "artifact_replay",
            "snapshot_load_replay",
            "duplicate_replay",
            "declared_replay_window",
        ],
        "mb5_requires": [
            "all_MB4_replay_modes_passed",
            "order_inversion_control_failed_closed",
            "post_hoc_child_basin_stitching_control_failed_closed",
            "merge_leakage_control_failed_closed",
            "producer_insertion_control_failed_closed",
        ],
        "mb6_requires": [
            "all_MB5_controls_passed_or_failed_closed_as_expected",
            "handoff_reconstruction_replay",
            "n26_consumption_constraints_recorded",
        ],
        "fail_closed_if": [
            "any_required_replay_mode_not_run",
            "artifact_digest_mismatch",
            "snapshot_load_replay_mismatch",
            "duplicate_replay_mismatch",
            "order_inversion_passes_as_positive_claim",
            "post_hoc_stitching_passes_as_positive_claim",
        ],
    }


def build_control_schema() -> dict[str, Any]:
    control_ids = [
        "old_synchronous_expansion_relabel_control",
        "causal_spark_label_only_control",
        "module_node_created_as_child_basin_control",
        "transient_sink_as_child_basin_control",
        "old_basin_thickening_control",
        "sub_basin_relabel_as_independent_multi_basin_control",
        "merge_leakage_as_separation_control",
        "neighbor_leakage_as_child_support_control",
        "producer_topology_insertion_control",
        "producer_hidden_support_control",
        "producer_threshold_relaxation_control",
        "producer_success_as_native_upgrade_control",
        "producer_scaffold_overwrites_native_failure_control",
        "topology_integration_event_missing_control",
        "support_floor_missing_control",
        "coherence_floor_missing_control",
        "boundary_record_missing_control",
        "flux_record_missing_control",
        "membership_digest_missing_control",
        "post_hoc_child_basin_stitching_control",
        "event_order_inversion_control",
        "missing_replay_control",
        "bf5_scoped_sub_basin_as_bf6_control",
        "n25_result_as_unscoped_n26_substrate_control",
        "semantic_learning_relabel_control",
        "semantic_choice_relabel_control",
        "agency_relabel_control",
        "native_support_relabel_control",
        "phase8_complete_relabel_control",
        "ant_ecology_relabel_control",
    ]
    return {
        "schema_id": "n25_1_merge_leakage_and_relabel_controls_v1",
        "control_status_values": CONTROL_STATUS_VALUES,
        "required_control_ids": control_ids,
        "control_result_fields": [
            "control_id",
            "control_status",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "claim_allowed_when_control_triggers",
            "rung_effect",
        ],
        "positive_mb5_requires": "all_applicable_controls_passed_or_failed_closed_as_expected",
        "failed_open_effect": "blocks_MB4_MB5_MB6_and_native_multi_basin_claim",
        "not_run_effect": "blocks_dependent_MB_rung",
    }


def build_producer_residue_schema() -> dict[str, Any]:
    return {
        "schema_id": "n25_1_producer_residue_blockers_v1",
        "producer_residue_class_values": [
            "none_detected",
            "producer_observes_records_schedules_only",
            "producer_mediated_scaffold",
            "hidden_producer_support_blocks_row",
            "hidden_producer_topology_insertion_blocks_row",
            "producer_threshold_relaxation_blocks_row",
        ],
        "allowed_producer_behavior": [
            "observe_committed_runtime_state",
            "record_digest_backed_evidence",
            "schedule_policy_gated_work_if_declared",
        ],
        "forbidden_producer_behavior": [
            "direct_coherence_write",
            "direct_support_write",
            "direct_topology_insertion_without_step_event",
            "hidden_threshold_relaxation",
            "backfill_child_basin_membership_after_outcome",
            "upgrade_native_result_from_producer_assisted_success",
        ],
        "producer_assisted_lane_ceiling": {
            "may_support": [
                "producer_assisted_scaffold_candidate",
                "missing_native_mechanism_probe",
                "future_naturalization_target",
            ],
            "must_not_support": [
                "native_MB5",
                "native_MB6",
                "BF6",
                "native_support",
                "phase8_implementation_complete",
            ],
        },
    }


def build_n26_consumption_constraints() -> dict[str, Any]:
    return {
        "schema_id": "n25_1_n26_consumption_constraints_v1",
        "current_allowed_n26_consumption": [
            "N25_scoped_BF5_high_margin_core_sub_basin_context",
            "N25.1_requirements_schema_context",
            "producer_assisted_scaffold_as_naturalization_target_only",
        ],
        "blocked_until_mb6": [
            "N26_unscoped_multi_basin_substrate",
            "N26_independent_new_basin_substrate",
            "N26_native_LGRC9V3_multi_basin_claim",
            "N26_BF6_consumption",
        ],
        "mb6_consumption_preconditions": [
            "native_causal_refinement_event_source_current",
            "topology_integration_lineage_budget_clean",
            "post_refinement_child_basin_cores_source_current",
            "child_basin_support_coherence_boundary_flux_records_present",
            "merge_leakage_controls_clean",
            "artifact_snapshot_duplicate_replay_clean",
            "producer_residue_does_not_upgrade_native",
            "unsafe_claim_flags_false",
        ],
        "n26_must_preserve": [
            "N25_BF5_scope_not_BF6",
            "N25_native_flux_debt_context",
            "N25_1_runtime_evidence_closed_until_extension_runs",
            "producer_assisted_results_do_not_upgrade_native",
        ],
    }


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    source_inventory = {
        "path": I1_OUTPUT_PATH,
        "sha256": sha256_file(I1_OUTPUT_PATH),
        "status": i1.get("status", "not_recorded"),
        "acceptance_state": i1.get("acceptance_state", "not_recorded"),
        "output_digest": i1.get("output_digest", "not_recorded"),
        "failed_checks": i1.get("failed_checks", "not_recorded"),
    }
    candidate_schema = {
        "schema_id": "n25_1_future_multi_basin_candidate_row_schema_v1",
        "required_fields": REQUIRED_FUTURE_EXTENSION_FIELDS,
        "row_decision_values": ROW_DECISION_VALUES,
        "mb_rung_status_values": MB_RUNG_STATUS_VALUES,
        "artifact_role_values": ARTIFACT_ROLE_VALUES,
        "positive_support_forbidden_if_only_artifact_roles": (
            POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES
        ),
        "strict_boolean_fields_for_positive_rows": [
            "artifact_paths_equal_manifest_paths",
            "artifact_sha256_equal_manifest_sha256",
            "all_artifact_sha256_match_file_contents",
            "multi_basin_claim_allowed",
            "n26_consumption_allowed",
        ],
        "string_sentinels_allowed_only_when": {
            "schema_only": True,
            "positive_evidence_admissible": False,
        },
    }
    unsafe_flags = unsafe_claim_flags()
    output: dict[str, Any] = {
        "artifact_id": "n25_1_multi_basin_extension_schema",
        "status": "passed",
        "acceptance_state": "accepted_multi_basin_extension_schema_frozen_no_runtime_evidence",
        "generated_at": GENERATED_AT,
        "reproduction_command": COMMAND,
        "experiment": "N25.1",
        "iteration": "I2",
        "source_inventory": source_inventory,
        "experiment_kind": "requirements_spec_bridge",
        "runtime_implementation_opened": False,
        "phase8_extension_implemented": False,
        "multi_basin_evidence_opened": False,
        "mb_ladder_rung_assigned": False,
        "mb_ladder_ceiling": "MB0_schema_freeze_only",
        "n25_1_closeout_ceiling": "N25.1-C2_multi_basin_extension_schema_frozen",
        "mb_ladder": MB_LADDER,
        "n25_1_closeout_ladder": N25_1_CLOSEOUT_LADDER,
        "candidate_evidence_row_schema": candidate_schema,
        "causal_refinement_event_schema": build_causal_refinement_schema(),
        "child_basin_extraction_schema": build_child_basin_schema(),
        "replay_schema": build_replay_schema(),
        "control_schema": build_control_schema(),
        "producer_residue_schema": build_producer_residue_schema(),
        "n26_consumption_constraints": build_n26_consumption_constraints(),
        "source_theory_boundary": {
            "schema_must_be_based_on_sources": True,
            "paper_or_spec_vocabulary_can_define_fields": True,
            "paper_or_spec_vocabulary_cannot_satisfy_runtime_evidence_gates": True,
            "requirements_contract_cannot_be_counted_as_multi_basin_evidence": True,
        },
        "claim_boundary": {
            "requirements_contract_allowed": True,
            "runtime_evidence_allowed": False,
            "native_multi_basin_formation_supported": False,
            "BF6_supported": False,
            "phase8_extension_ready_to_implement": False,
            "N26_unscoped_multi_basin_consumption_allowed": False,
            "unsafe_claim_flags": unsafe_flags,
        },
    }
    required_schema_sections = [
        "candidate_evidence_row_schema",
        "causal_refinement_event_schema",
        "child_basin_extraction_schema",
        "replay_schema",
        "control_schema",
        "producer_residue_schema",
        "n26_consumption_constraints",
    ]
    required_fields_present = all(
        field in output["candidate_evidence_row_schema"]["required_fields"]
        for field in [
            "causal_spark_or_boundary_birth_event_id",
            "topology_integration_event_id",
            "post_refinement_flow_window",
            "child_basin_core_ids",
            "child_basin_membership_digest",
            "merge_leakage_trace",
            "replay_results",
            "control_results",
            "unsafe_claim_flags",
        ]
    )
    checks = [
        check(
            "i1_source_inventory_passed",
            source_inventory["status"] == "passed"
            and source_inventory["failed_checks"] == [],
            source_inventory,
        ),
        check(
            "mb_ladder_frozen",
            list(MB_LADDER.keys()) == ["MB0", "MB1", "MB2", "MB3", "MB4", "MB5", "MB6"],
            MB_LADDER,
        ),
        check(
            "required_schema_sections_present",
            all(section in output for section in required_schema_sections),
            required_schema_sections,
        ),
        check(
            "future_candidate_required_fields_present",
            required_fields_present,
            output["candidate_evidence_row_schema"]["required_fields"],
        ),
        check(
            "child_basin_schema_blocks_label_or_transient_success",
            {
                "child_identity_label_only",
                "module_node_created_equals_child_basin",
                "transient_sink_as_persistent_child_basin",
            }.issubset(set(output["child_basin_extraction_schema"]["fail_closed_if"])),
            output["child_basin_extraction_schema"]["fail_closed_if"],
        ),
        check(
            "replay_and_control_gates_fail_closed",
            output["replay_schema"]["fail_closed_if"] != []
            and output["control_schema"]["failed_open_effect"]
            == "blocks_MB4_MB5_MB6_and_native_multi_basin_claim",
            {
                "replay_fail_closed_if": output["replay_schema"]["fail_closed_if"],
                "control_failed_open_effect": output["control_schema"][
                    "failed_open_effect"
                ],
            },
        ),
        check(
            "producer_results_cannot_upgrade_native",
            "upgrade_native_result_from_producer_assisted_success"
            in output["producer_residue_schema"]["forbidden_producer_behavior"]
            and "native_MB6"
            in output["producer_residue_schema"]["producer_assisted_lane_ceiling"][
                "must_not_support"
            ],
            output["producer_residue_schema"]["producer_assisted_lane_ceiling"],
        ),
        check(
            "n26_unscoped_consumption_blocked_until_mb6",
            "N26_unscoped_multi_basin_substrate"
            in output["n26_consumption_constraints"]["blocked_until_mb6"],
            output["n26_consumption_constraints"],
        ),
        check(
            "runtime_evidence_still_closed",
            output["runtime_implementation_opened"] is False
            and output["phase8_extension_implemented"] is False
            and output["multi_basin_evidence_opened"] is False
            and output["claim_boundary"]["runtime_evidence_allowed"] is False,
            output["claim_boundary"],
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in unsafe_flags.values()),
            unsafe_flags,
        ),
        check(
            "no_absolute_paths_in_records",
            not contains_absolute_path(output),
            "repo_relative_paths_only",
        ),
    ]
    output["checks"] = checks
    output["failed_checks"] = [
        item["check_id"] for item in checks if item["passed"] is not True
    ]
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N25.1 Iteration 2 - Multi-Basin Extension Schema Freeze",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Interpretation",
        "",
        (
            "I2 freezes the future extension contract. It defines what a later "
            "native LGRC9V3 multi-basin row must record, which controls must "
            "fail closed, and what N26 may consume. It does not implement the "
            "extension and does not open runtime evidence."
        ),
        "",
        "The schema is deliberately source-constrained: paper/spec vocabulary may "
        "define fields and controls, but cannot satisfy runtime evidence gates.",
        "",
        "## MB Ladder",
        "",
        "| Rung | Meaning |",
        "| --- | --- |",
    ]
    for rung, meaning in data["mb_ladder"].items():
        lines.append(f"| `{rung}` | {meaning} |")
    lines.extend(
        [
            "",
            "## N25.1 Closeout Ladder",
            "",
            "| Rung | Meaning |",
            "| --- | --- |",
        ]
    )
    for rung, meaning in data["n25_1_closeout_ladder"].items():
        lines.append(f"| `{rung}` | {meaning} |")
    lines.extend(
        [
            "",
            "## Required Schema Sections",
            "",
            "| Section | Purpose |",
            "| --- | --- |",
            "| `candidate_evidence_row_schema` | Required fields and row-level enums for future extension rows. |",
            "| `causal_refinement_event_schema` | Causal spark/boundary-birth to topology-integration ordering. |",
            "| `child_basin_extraction_schema` | Source-current child-basin core, support, coherence, boundary, flux, and membership records. |",
            "| `replay_schema` | Replay modes required before MB4/MB5/MB6. |",
            "| `control_schema` | Merge/leakage, relabel, producer, and unsafe-claim controls. |",
            "| `producer_residue_schema` | Producer/step boundary and producer-assisted lane ceiling. |",
            "| `n26_consumption_constraints` | What N26 may consume before or after MB6. |",
            "",
            "## N26 Constraint",
            "",
            "```text",
            "N26 may consume N25 scoped BF5 and the N25.1 requirements schema.",
            "N26 may not consume unscoped multi-basin substrate, independent new-basin substrate, native LGRC9V3 multi-basin claims, or BF6 until MB6 exists.",
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            f"runtime_implementation_opened = {str(data['runtime_implementation_opened']).lower()}",
            f"phase8_extension_implemented = {str(data['phase8_extension_implemented']).lower()}",
            f"multi_basin_evidence_opened = {str(data['multi_basin_evidence_opened']).lower()}",
            f"native_multi_basin_formation_supported = {str(data['claim_boundary']['native_multi_basin_formation_supported']).lower()}",
            f"BF6_supported = {str(data['claim_boundary']['BF6_supported']).lower()}",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for item in data["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"output_digest {data['output_digest']}")


if __name__ == "__main__":
    main()
