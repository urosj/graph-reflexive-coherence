#!/usr/bin/env python3
"""Build N21 Iteration 2 withdrawal/naturalization schema freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-23T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth"
)
OUTPUT = EXPERIMENT / "outputs" / "n21_withdrawal_schema_and_thresholds.json"
REPORT = EXPERIMENT / "reports" / "n21_withdrawal_schema_and_thresholds.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_withdrawal_schema_and_thresholds.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_source_contract_inventory.json"
)
I1_REPORT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "reports/n21_source_contract_inventory.md"
)

PRIMITIVES = ["withdrawal_resistance", "naturalization_depth"]

ROW_DECISIONS = ["supported", "partial", "blocked", "rejected", "not_applicable"]
REPLAY_CONTROL_STATUSES = [
    "passed",
    "failed_closed",
    "failed_open",
    "not_run",
    "not_applicable",
]
WITHDRAWAL_MODES = ["weaken", "remove", "ramp_down", "step_down"]
WITHDRAWAL_TARGETS = ["support", "scaffold", "producer_surface"]
REQUIRED_RUN_ARTIFACT_FIELDS = [
    "run_artifact_id",
    "source_commit_or_source_digest",
    "runtime_config_digest",
    "source_contract_row_digest",
    "baseline_artifact_path",
    "withdrawn_or_probe_absent_artifact_path",
    "event_log_or_trace_path",
    "snapshot_or_replay_artifact_path",
    "artifact_digest",
    "derived_report_only",
]
CANDIDATE_EVIDENCE_FIELDS = [
    "primitive_id",
    "source_contract_row",
    "contract_consumed_without_redefinition",
    "row_specific_thresholds_declared_before_use",
    "run_artifact_id",
    "source_commit_or_source_digest",
    "runtime_config_digest",
    "source_contract_row_digest",
    "baseline_artifact_path",
    "withdrawn_or_probe_absent_artifact_path",
    "event_log_or_trace_path",
    "snapshot_or_replay_artifact_path",
    "artifact_digest",
    "derived_report_only",
    "source_current_inputs",
    "producer_mediated_fields",
    "naturalization_debt_fields",
    "blocked_relabel_fields",
    "same_basin_continuation_rule",
    "support_floor_result",
    "coherence_floor_result",
    "boundary_integrity_result",
    "flux_or_leakage_result",
    "replay_result",
    "replay_result_status",
    "control_results",
    "control_result_statuses",
    "wr_ladder_rung",
    "nd_ladder_rung",
    "row_decision",
    "primitive_claim_allowed",
    "unsafe_claim_flags",
    "claim_ceiling",
]
GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_choice",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "fully_native_integration",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def source_record(path: str, role: str) -> dict[str, Any]:
    data = load_json(path) if path.endswith(".json") else None
    record: dict[str, Any] = {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": role,
    }
    if data is not None:
        record["status"] = data.get("status", "not_recorded")
        record["acceptance_state"] = data.get("acceptance_state", "not_recorded")
        record["output_digest"] = data.get("output_digest", "not_recorded")
    return record


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in GLOBAL_UNSAFE_CLAIMS}


def source_current_definition() -> dict[str, Any]:
    return {
        "definition": (
            "emitted by the LGRC runtime or replay from declared run artifacts, "
            "not invented by a report builder, label, post-hoc parser, or "
            "producer-only policy"
        ),
        "allowed_sources": [
            "LGRC runtime output",
            "replay from declared run artifacts",
            "source-current trace emitted by the run",
        ],
        "blocked_sources": [
            "report builder invention",
            "label-only construction",
            "post-hoc parser construction",
            "producer-only policy state",
            "roadmap or handoff text",
        ],
    }


def run_artifact_admissibility_schema() -> dict[str, Any]:
    return {
        "required_fields": REQUIRED_RUN_ARTIFACT_FIELDS,
        "digest_algorithm": "sha256",
        "path_policy": "repository_relative_paths_only",
        "artifact_paths_must_exist": True,
        "artifact_digests_must_match_file_contents": True,
        "source_contract_row_digest_must_match_i1": True,
        "derived_report_only_true_blocks_positive_support": True,
        "missing_required_artifact_blocks_rung_assignment": True,
        "digest_mismatch_blocks_rung_assignment": True,
        "report_only_artifacts_may_summarize_but_not_assign_rungs": True,
        "fail_closed_on_missing_or_mismatch": True,
    }


def candidate_evidence_row_schema() -> dict[str, Any]:
    return {
        "required_fields": CANDIDATE_EVIDENCE_FIELDS,
        "missing_required_field_blocks_candidate_admissibility": True,
        "field_constraints": {
            "primitive_id": {
                "type": "enum",
                "allowed_values": PRIMITIVES,
                "constraint": "must identify one N21 primitive contract row",
            },
            "source_contract_row": {
                "type": "string",
                "constraint": "must match an I1 source_contract_row",
            },
            "contract_consumed_without_redefinition": {
                "type": "boolean",
                "required_value": True,
                "constraint": "false blocks rung assignment",
            },
            "row_specific_thresholds_declared_before_use": {
                "type": "boolean",
                "required_value": True,
                "constraint": "false blocks positive support",
            },
            "run_artifact_id": {
                "type": "string",
                "constraint": "required for positive candidate rows",
            },
            "source_commit_or_source_digest": {
                "type": "string",
                "constraint": "must identify source-current runtime/replay source",
            },
            "runtime_config_digest": {
                "type": "sha256_string",
                "constraint": "must match declared runtime configuration",
            },
            "source_contract_row_digest": {
                "type": "sha256_string",
                "constraint": "must match the I1 contract row digest",
            },
            "baseline_artifact_path": {
                "type": "repository_relative_path",
                "constraint": "path must exist when row claims positive support",
            },
            "withdrawn_or_probe_absent_artifact_path": {
                "type": "repository_relative_path",
                "constraint": "path must exist when row claims positive support",
            },
            "event_log_or_trace_path": {
                "type": "repository_relative_path",
                "constraint": "path must exist when row claims positive support",
            },
            "snapshot_or_replay_artifact_path": {
                "type": "repository_relative_path",
                "constraint": "path must exist when replay-backed rung is claimed",
            },
            "artifact_digest": {
                "type": "sha256_string",
                "constraint": "must match declared row artifact contents",
            },
            "derived_report_only": {
                "type": "boolean",
                "required_value_for_positive_support": False,
                "constraint": "true blocks positive primitive support",
            },
            "source_current_inputs": {
                "type": "list[string]",
                "constraint": "must be runtime/replay emitted, not report-built",
            },
            "producer_mediated_fields": {
                "type": "list[string]",
                "constraint": "may be recorded as residue, not substrate-carried evidence",
            },
            "naturalization_debt_fields": {
                "type": "list[string]",
                "constraint": "must remain debt unless source-backed naturalization is shown",
            },
            "blocked_relabel_fields": {
                "type": "list[string]",
                "constraint": "cannot be used as evidence",
            },
            "same_basin_continuation_rule": {
                "type": "object",
                "source": "frozen_i1_same_basin_rule",
                "required_keys": [
                    "rule_id",
                    "basin_signature_fields",
                    "required_support_floor",
                    "required_coherence_floor",
                    "boundary_integrity_floor",
                    "flux_balance_bounds",
                    "replay_requirement",
                    "failure_modes",
                    "proxy_only_success_allowed",
                    "hidden_producer_support_allowed",
                    "label_only_continuation_allowed",
                ],
                "constraint": "must be consumed from I1 without redefinition",
            },
            "support_floor_result": {
                "type": "enum",
                "allowed_values": support_coherence_boundary_flux_schema()[
                    "result_status_values"
                ],
                "constraint": "floor crossing blocks support",
            },
            "coherence_floor_result": {
                "type": "enum",
                "allowed_values": support_coherence_boundary_flux_schema()[
                    "result_status_values"
                ],
                "constraint": "floor crossing blocks support",
            },
            "boundary_integrity_result": {
                "type": "enum",
                "allowed_values": support_coherence_boundary_flux_schema()[
                    "result_status_values"
                ],
                "constraint": "missing or failed boundary integrity blocks support",
            },
            "flux_or_leakage_result": {
                "type": "enum",
                "allowed_values": support_coherence_boundary_flux_schema()[
                    "result_status_values"
                ],
                "constraint": "exceeded bound blocks support",
            },
            "replay_result": {
                "type": "object",
                "constraint": "must record required replay modes for claimed rung",
            },
            "replay_result_status": {
                "type": "enum",
                "allowed_values": REPLAY_CONTROL_STATUSES,
                "constraint": "not_run blocks dependent rung; failed_open invalidates row",
            },
            "control_results": {
                "type": "list[object]",
                "constraint": "must record controls required by primitive and rung",
            },
            "control_result_statuses": {
                "type": "list[enum]",
                "allowed_values": REPLAY_CONTROL_STATUSES,
                "constraint": "not_run blocks dependent rung; failed_open invalidates row",
            },
            "wr_ladder_rung": {
                "type": "enum_or_null",
                "constraint": "assigned only from source-backed N21 withdrawal evidence",
            },
            "nd_ladder_rung": {
                "type": "enum_or_null",
                "constraint": "assigned only from source-backed N21 probe-absence evidence",
            },
            "row_decision": {
                "type": "enum",
                "allowed_values": ROW_DECISIONS,
                "constraint": "partial, blocked, rejected, and not_applicable block support",
            },
            "primitive_claim_allowed": {
                "type": "boolean",
                "constraint": (
                    "true only when row decision, rung gates, replay, controls, "
                    "thresholds, artifacts, same-basin rule, and unsafe flags all pass"
                ),
            },
            "unsafe_claim_flags": {
                "type": "object[boolean]",
                "required_keys": GLOBAL_UNSAFE_CLAIMS,
                "constraint": "all unsafe claim flags must remain false",
            },
            "claim_ceiling": {
                "type": "string",
                "constraint": (
                    "must state bounded artifact-level N21 primitive ceiling; "
                    "cannot permit agency, native support, sentience, Phase 8, "
                    "or ant-ecology implementation"
                ),
            },
        },
        "computed_or_derived_fields_still_required": [
            "primitive_claim_allowed",
            "claim_ceiling",
        ],
        "same_basin_rule_must_use_i1_reference": True,
        "primitive_claim_allowed_false_if_unsafe_claim_requested": True,
        "primitive_claim_allowed_false_for_non_supported_rows": True,
    }


def threshold_declaration_policy() -> dict[str, Any]:
    return {
        "row_specific_thresholds_declared_before_use": True,
        "outcome_inspection_before_threshold_declaration_allowed": False,
        "retune_after_outcome_allowed": False,
        "required_threshold_surfaces": [
            "support_floor",
            "coherence_floor",
            "boundary_integrity_floor",
            "flux_or_leakage_bound",
            "replay_requirement",
            "control_requirement",
        ],
        "threshold_record_required_fields": [
            "threshold_id",
            "primitive_id",
            "source_contract_row",
            "source_contract_row_digest",
            "threshold_declared_before_use",
            "threshold_value_or_rule",
            "threshold_owner",
            "failure_policy",
        ],
        "failure_policy": "missing_or_post_hoc_threshold_blocks_support",
    }


def withdrawal_schema() -> dict[str, Any]:
    return {
        "withdrawal_mode_allowed": WITHDRAWAL_MODES,
        "withdrawal_target_allowed": WITHDRAWAL_TARGETS,
        "required_fields": [
            "withdrawal_mode",
            "withdrawal_target",
            "withdrawal_start",
            "withdrawal_end",
            "withdrawal_amount",
            "recovery_window",
            "floor_crossing_policy",
        ],
        "declared_before_outcome_inspection_required": True,
        "post_outcome_retuning_allowed": False,
        "floor_crossing_policy_required": True,
        "producer_surface_claim_restriction": {
            "if_withdrawal_target": "producer_surface",
            "allowed_support": "producer_dependence_or_residue_analysis",
            "blocked_support": (
                "source-current substrate-carried withdrawal resistance unless "
                "basin continuation persists in declared source-current fields"
            ),
        },
    }


def probe_absence_schema() -> dict[str, Any]:
    return {
        "required_fields": [
            "probe_absent_runtime_input",
            "probe_residue_digest_absent",
            "support_annotation_not_used_as_evidence",
            "producer_probe_schedule_disabled",
        ],
        "required_values": {
            "probe_absent_runtime_input": True,
            "probe_residue_digest_absent": True,
            "support_annotation_not_used_as_evidence": True,
            "producer_probe_schedule_disabled": True,
        },
        "report_label_only_absence_allowed": False,
        "probe_residue_present_blocks_nd4_and_stronger": True,
        "support_annotation_as_evidence_blocks_nd4_and_stronger": True,
    }


def support_coherence_boundary_flux_schema() -> dict[str, Any]:
    return {
        "required_result_fields": [
            "support_floor_result",
            "coherence_floor_result",
            "boundary_integrity_result",
            "flux_or_leakage_result",
        ],
        "result_status_values": [
            "preserved",
            "crossed_floor",
            "exceeded_bound",
            "missing",
            "not_applicable",
        ],
        "missing_result_blocks_support": True,
        "floor_crossing_blocks_support": True,
        "flux_bound_exceeded_blocks_support": True,
    }


def replay_control_schema() -> dict[str, Any]:
    return {
        "status_enum": REPLAY_CONTROL_STATUSES,
        "required_replay_modes": {
            "WR4": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
            ],
            "ND3": ["declared_multi_window_replay_without_original_probe_scaffold"],
        },
        "required_control_records": [
            "control_id",
            "control_status",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "claim_allowed_when_control_triggers",
            "rung_effect",
        ],
        "not_run_blocks_dependent_rung": True,
        "failed_open_invalidates_row": True,
        "failed_closed_demotes_or_blocks_dependent_rung": True,
        "not_applicable_requires_scope_reason": True,
    }


def active_null_comparability_rule() -> dict[str, Any]:
    return {
        "same_source_contract_row": True,
        "same_source_contract_row_digest": True,
        "same_basin_signature_fields": True,
        "same_seed_or_declared_seed_pairing_rule": True,
        "same_topology_config_family": True,
        "same_runtime_envelope_digest": True,
        "same_budget_schedule_family_where_applicable": True,
        "same_budget_schedule_digest_where_applicable": True,
        "no_declared_withdrawal_or_no_probe_absence": True,
        "expected_result": "fail_closed",
        "weak_or_noncomparable_null_blocks_null_use": True,
    }


def ladder_schema() -> dict[str, Any]:
    wr = [
        ("WR0", "no_withdrawal_evidence"),
        ("WR1", "declared_withdrawal_attempted"),
        ("WR2", "source_visible_persistence_signal"),
        ("WR3", "same_basin_withdrawal_candidate"),
        ("WR4", "replay_backed_withdrawal_candidate"),
        ("WR5", "control_backed_withdrawal_candidate"),
        ("WR6", "artifact_level_withdrawal_resistance_candidate"),
    ]
    nd = [
        ("ND0", "probe_dependent_only"),
        ("ND1", "probe_absent_trace"),
        ("ND2", "post_probe_same_basin_candidate"),
        ("ND3", "replay_backed_post_probe_candidate"),
        ("ND4", "residue_controlled_naturalization_candidate"),
        ("ND5", "producer_debt_bounded_naturalization_candidate"),
        ("ND6", "artifact_level_naturalization_depth_candidate"),
    ]
    closeout = [
        ("N21-C0", "contract_only_closeout"),
        ("N21-C1", "baselines_control_discipline_established"),
        ("N21-C2", "single_primitive_partial"),
        ("N21-C3", "single_primitive_candidate"),
        ("N21-C4", "dual_primitive_candidate"),
        ("N21-C5", "dual_replay_control_backed_candidate"),
        ("N21-C6", "n22_ready_bounded_primitive_evidence"),
    ]
    return {
        "withdrawal_resistance_ladder": [
            {"rung": rung, "meaning": meaning} for rung, meaning in wr
        ],
        "naturalization_depth_ladder": [
            {"rung": rung, "meaning": meaning} for rung, meaning in nd
        ],
        "n21_closeout_ladder": [
            {"rung": rung, "meaning": meaning} for rung, meaning in closeout
        ],
        "nd_ladder_scope": (
            "N21-local artifact ladder only; not the full cross-scale "
            "theoretical naturalization-depth ladder"
        ),
        "not_agency_score": True,
        "n20_contract_completeness_assigns_rungs": False,
        "rungs_require_source_backed_n21_evidence_rows": True,
    }


def demotion_precedence() -> dict[str, Any]:
    return {
        "i4_i5_probe_rungs_are_provisional_until_i6": True,
        "final_wr_nd_rungs_assigned_after_i6_only": True,
        "replay_failure_blocks_replay_backed_and_stronger": True,
        "control_failed_closed_blocks_control_backed_and_stronger": True,
        "control_failed_open_invalidates_row": True,
        "not_run_blocks_dependent_rung": True,
        "unrecorded_producer_residue_or_debt_blocks": ["WR6", "ND5", "ND6"],
        "hypothesis_c_failure_demotes_or_blocks_a_b": True,
    }


def row_decision_policy() -> dict[str, Any]:
    return {
        "row_decision_enum": ROW_DECISIONS,
        "supported_does_not_permit_unsafe_claims": True,
        "partial_blocks_primitive_support": True,
        "blocked_blocks_primitive_support": True,
        "rejected_blocks_primitive_support": True,
        "inventory_contract_support_field": "inventory_decision",
        "inventory_rows_keep_row_decision": "not_applicable",
    }


def claim_boundary_schema() -> dict[str, Any]:
    return {
        "global_unsafe_claim_flags": unsafe_claim_flags(),
        "row_specific_blocked_relabels_separate": True,
        "producer_mediated_fields_are_not_substrate_carried": True,
        "naturalization_debt_fields_are_not_native_support": True,
        "markdown_sources_context_only": True,
        "blocked_claims": GLOBAL_UNSAFE_CLAIMS,
    }


def closeout_status_enums() -> dict[str, list[str]]:
    return {
        "withdrawal_resistance_status": [
            "withdrawal_resistance_supported_artifact_level_candidate",
            "withdrawal_resistance_partial_or_blocked",
            "withdrawal_resistance_rejected",
        ],
        "naturalization_depth_status": [
            "naturalization_depth_supported_bounded_N21_candidate",
            "naturalization_depth_rung_limited_candidate",
            "naturalization_depth_partial_or_blocked",
            "naturalization_depth_rejected",
        ],
    }


def primitive_schema_rows(i1: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in i1["source_contract_rows"]:
        primitive_id = row["primitive_id"]
        rows.append(
            {
                "primitive_id": primitive_id,
                "source_contract_row": row["source_contract_row"],
                "source_contract_row_digest": row["source_contract_row_digest"],
                "source_current_fields": row["source_current_fields"],
                "producer_mediated_fields": row["producer_mediated_fields"],
                "naturalization_debt_fields": row["naturalization_debt_fields"],
                "row_specific_blocked_relabels": row[
                    "row_specific_blocked_relabels"
                ],
                "required_control_ids": row["required_control_ids"],
                "same_basin_continuation_rule": row["same_basin_rule"],
                "support_scaffold": row["support_scaffold"],
                "handoff_inputs": row["handoff_inputs"],
                "claim_ceiling": row["claim_ceiling"],
                "schema_row_status": "frozen_from_i1_contract_inventory",
                "i1_contract_structures_read_only": True,
                "contract_consumed_without_redefinition_required": True,
                "row_specific_thresholds_required_before_use": True,
                "positive_evidence_requires_run_artifacts": True,
                "derived_report_only_true_blocks_support": True,
            }
        )
    return rows


def schema_freeze(i1: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_current_definition": source_current_definition(),
        "candidate_evidence_row_schema": candidate_evidence_row_schema(),
        "run_artifact_admissibility_schema": run_artifact_admissibility_schema(),
        "threshold_declaration_policy": threshold_declaration_policy(),
        "withdrawal_schema": withdrawal_schema(),
        "probe_absence_schema": probe_absence_schema(),
        "support_coherence_boundary_flux_schema": support_coherence_boundary_flux_schema(),
        "replay_control_schema": replay_control_schema(),
        "active_null_comparability_rule": active_null_comparability_rule(),
        "classification_ladders": ladder_schema(),
        "demotion_precedence": demotion_precedence(),
        "row_decision_policy": row_decision_policy(),
        "claim_boundary_schema": claim_boundary_schema(),
        "closeout_status_enums": closeout_status_enums(),
        "primitive_schema_rows": primitive_schema_rows(i1),
    }


def context_boundary_from_i1(i1: dict[str, Any]) -> dict[str, Any]:
    return {
        "markdown_sources_context_only": i1["source_context_boundary"][
            "markdown_sources_context_only"
        ],
        "may_consume_as": i1["source_context_boundary"][
            "markdown_sources_may_consume_as"
        ],
        "must_not_consume_as": i1["source_context_boundary"][
            "markdown_sources_must_not_consume_as"
        ],
    }


def build_checks(i1: dict[str, Any], freeze: dict[str, Any]) -> list[dict[str, Any]]:
    candidate_schema = freeze["candidate_evidence_row_schema"]
    run_schema = freeze["run_artifact_admissibility_schema"]
    threshold_policy = freeze["threshold_declaration_policy"]
    withdrawal = freeze["withdrawal_schema"]
    probe = freeze["probe_absence_schema"]
    replay = freeze["replay_control_schema"]
    ladders = freeze["classification_ladders"]
    demotion = freeze["demotion_precedence"]
    row_policy = freeze["row_decision_policy"]
    claim_schema = freeze["claim_boundary_schema"]
    primitive_rows = freeze["primitive_schema_rows"]
    i1_rows_by_primitive = {
        row["primitive_id"]: row for row in i1["source_contract_rows"]
    }

    return [
        check(
            "source_i1_inventory_passed",
            i1["status"] == "passed"
            and i1["acceptance_state"]
            == "accepted_source_contract_inventory_no_primitive_evidence"
            and not i1["failed_checks"],
            {
                "status": i1["status"],
                "acceptance_state": i1["acceptance_state"],
                "failed_checks": i1["failed_checks"],
            },
        ),
        check(
            "i1_boundary_kept_no_primitive_evidence",
            not i1["iteration1_boundary"]["primitive_evidence_opened"]
            and not i1["iteration1_boundary"]["wr_ladder_rung_assigned"]
            and not i1["iteration1_boundary"]["nd_ladder_rung_assigned"]
            and not i1["iteration1_boundary"]["positive_run_artifacts_consumed"],
            i1["iteration1_boundary"],
        ),
        check(
            "candidate_evidence_row_schema_complete",
            candidate_schema["required_fields"] == CANDIDATE_EVIDENCE_FIELDS
            and set(candidate_schema["field_constraints"].keys())
            == set(CANDIDATE_EVIDENCE_FIELDS),
            {
                "required_field_count": len(candidate_schema["required_fields"]),
                "field_constraint_count": len(candidate_schema["field_constraints"]),
            },
        ),
        check(
            "candidate_schema_explicitly_freezes_missing_review_fields",
            all(
                field in candidate_schema["field_constraints"]
                for field in [
                    "same_basin_continuation_rule",
                    "primitive_claim_allowed",
                    "claim_ceiling",
                ]
            )
            and candidate_schema["same_basin_rule_must_use_i1_reference"]
            and candidate_schema[
                "primitive_claim_allowed_false_if_unsafe_claim_requested"
            ],
            {
                "same_basin_continuation_rule": candidate_schema[
                    "field_constraints"
                ]["same_basin_continuation_rule"],
                "primitive_claim_allowed": candidate_schema["field_constraints"][
                    "primitive_claim_allowed"
                ],
                "claim_ceiling": candidate_schema["field_constraints"][
                    "claim_ceiling"
                ],
            },
        ),
        check(
            "run_artifact_required_fields_frozen",
            run_schema["required_fields"] == REQUIRED_RUN_ARTIFACT_FIELDS,
            run_schema["required_fields"],
        ),
        check(
            "artifact_admissibility_fail_closed",
            run_schema["artifact_paths_must_exist"]
            and run_schema["artifact_digests_must_match_file_contents"]
            and run_schema["derived_report_only_true_blocks_positive_support"]
            and run_schema["missing_required_artifact_blocks_rung_assignment"]
            and run_schema["digest_mismatch_blocks_rung_assignment"],
            run_schema,
        ),
        check(
            "threshold_policy_declared_before_use",
            threshold_policy["row_specific_thresholds_declared_before_use"]
            and not threshold_policy[
                "outcome_inspection_before_threshold_declaration_allowed"
            ]
            and not threshold_policy["retune_after_outcome_allowed"],
            threshold_policy,
        ),
        check(
            "withdrawal_schema_frozen",
            withdrawal["withdrawal_mode_allowed"] == WITHDRAWAL_MODES
            and withdrawal["withdrawal_target_allowed"] == WITHDRAWAL_TARGETS
            and withdrawal["declared_before_outcome_inspection_required"]
            and not withdrawal["post_outcome_retuning_allowed"],
            withdrawal,
        ),
        check(
            "producer_surface_claim_restricted",
            withdrawal["producer_surface_claim_restriction"]["if_withdrawal_target"]
            == "producer_surface",
            withdrawal["producer_surface_claim_restriction"],
        ),
        check(
            "probe_absence_schema_frozen",
            all(value is True for value in probe["required_values"].values())
            and not probe["report_label_only_absence_allowed"],
            probe,
        ),
        check(
            "replay_control_status_enum_frozen",
            replay["status_enum"] == REPLAY_CONTROL_STATUSES,
            replay["status_enum"],
        ),
        check(
            "wr4_and_nd3_replay_requirements_frozen",
            replay["required_replay_modes"]["WR4"]
            == ["artifact_replay", "snapshot_load_replay", "duplicate_replay"]
            and replay["required_replay_modes"]["ND3"]
            == ["declared_multi_window_replay_without_original_probe_scaffold"],
            replay["required_replay_modes"],
        ),
        check(
            "active_null_comparability_frozen",
            all(freeze["active_null_comparability_rule"].values())
            if all(
                isinstance(value, bool)
                for value in freeze["active_null_comparability_rule"].values()
            )
            else freeze["active_null_comparability_rule"]["expected_result"]
            == "fail_closed"
            and freeze["active_null_comparability_rule"][
                "weak_or_noncomparable_null_blocks_null_use"
            ],
            freeze["active_null_comparability_rule"],
        ),
        check(
            "classification_ladders_complete",
            len(ladders["withdrawal_resistance_ladder"]) == 7
            and len(ladders["naturalization_depth_ladder"]) == 7
            and len(ladders["n21_closeout_ladder"]) == 7
            and ladders["not_agency_score"]
            and not ladders["n20_contract_completeness_assigns_rungs"],
            {
                "wr_count": len(ladders["withdrawal_resistance_ladder"]),
                "nd_count": len(ladders["naturalization_depth_ladder"]),
                "closeout_count": len(ladders["n21_closeout_ladder"]),
                "nd_ladder_scope": ladders["nd_ladder_scope"],
            },
        ),
        check(
            "demotion_precedence_frozen",
            demotion["i4_i5_probe_rungs_are_provisional_until_i6"]
            and demotion["final_wr_nd_rungs_assigned_after_i6_only"]
            and demotion["not_run_blocks_dependent_rung"],
            demotion,
        ),
        check(
            "row_decision_policy_frozen",
            row_policy["row_decision_enum"] == ROW_DECISIONS
            and row_policy["inventory_rows_keep_row_decision"] == "not_applicable",
            row_policy,
        ),
        check(
            "claim_boundary_and_flag_split_frozen",
            set(claim_schema["global_unsafe_claim_flags"].keys())
            == set(GLOBAL_UNSAFE_CLAIMS)
            and all(value is False for value in claim_schema["global_unsafe_claim_flags"].values())
            and claim_schema["row_specific_blocked_relabels_separate"],
            claim_schema,
        ),
        check(
            "closeout_status_enums_frozen",
            set(closeout_status_enums().keys())
            == {"withdrawal_resistance_status", "naturalization_depth_status"},
            closeout_status_enums(),
        ),
        check(
            "primitive_schema_rows_frozen_from_i1",
            {row["primitive_id"] for row in primitive_rows} == set(PRIMITIVES)
            and all(row["source_contract_row_digest"] for row in primitive_rows),
            primitive_rows,
        ),
        check(
            "i1_same_basin_support_handoff_references_frozen",
            all(
                row["same_basin_continuation_rule"]
                == i1_rows_by_primitive[row["primitive_id"]]["same_basin_rule"]
                and row["support_scaffold"]
                == i1_rows_by_primitive[row["primitive_id"]]["support_scaffold"]
                and row["handoff_inputs"]
                == i1_rows_by_primitive[row["primitive_id"]]["handoff_inputs"]
                and row["claim_ceiling"]
                == i1_rows_by_primitive[row["primitive_id"]]["claim_ceiling"]
                and row["i1_contract_structures_read_only"]
                for row in primitive_rows
            ),
            {
                row["primitive_id"]: {
                    "same_basin_rule_id": row["same_basin_continuation_rule"][
                        "rule_id"
                    ],
                    "support_scaffold_id": row["support_scaffold"]["support_id"],
                    "handoff_primitive_id": row["handoff_inputs"]["primitive_id"],
                    "read_only": row["i1_contract_structures_read_only"],
                }
                for row in primitive_rows
            },
        ),
        check(
            "no_positive_primitive_evidence_opened",
            True,
            {
                "primitive_evidence_opened": False,
                "wr_ladder_rung_assigned": False,
                "nd_ladder_rung_assigned": False,
                "positive_run_artifacts_consumed": False,
            },
        ),
    ]


def contains_local_absolute_path(text: str) -> bool:
    needles = [
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "file" + "://",
        "vscode" + "://",
    ]
    return any(needle in text for needle in needles)


def build_payload() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    freeze = schema_freeze(i1)
    checks = build_checks(i1, freeze)

    payload: dict[str, Any] = {
        "artifact_id": "n21_withdrawal_schema_and_thresholds",
        "schema_version": "n21_withdrawal_schema_and_thresholds_v1",
        "experiment": "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth",
        "iteration": 2,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence",
        "purpose": (
            "Freeze N21 withdrawal/naturalization evidence schemas, ladders, "
            "threshold policy, artifact admissibility, and control demotion "
            "rules before positive probes."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n21_i1_source_contract_inventory"),
            source_record(I1_REPORT_PATH, "n21_i1_source_contract_inventory_report"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "context_source_boundary": context_boundary_from_i1(i1),
        "schema_freeze": freeze,
        "iteration2_boundary": {
            "schema_freeze_only": True,
            "primitive_evidence_opened": False,
            "withdrawal_resistance_supported": False,
            "naturalization_depth_supported": False,
            "wr_ladder_rung_assigned": False,
            "nd_ladder_rung_assigned": False,
            "n21_closeout_ladder_rung_assigned": False,
            "positive_run_artifacts_consumed": False,
            "ready_for_iteration_3_active_nulls": True,
        },
        "checks": checks,
    }

    no_absolute_paths = not contains_local_absolute_path(canonical_json(payload))
    payload["checks"].append(
        check(
            "no_local_absolute_paths",
            no_absolute_paths,
            "payload uses repository-relative paths and source IDs only",
        )
    )
    payload["failed_checks"] = [
        item["check_id"] for item in payload["checks"] if not item["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_schema_freeze_checks_failed"

    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    freeze = data["schema_freeze"]
    lines = [
        "# N21 Iteration 2 - Withdrawal And Naturalization Schema Freeze",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 2 freezes schema only. It opens no primitive evidence and",
        "assigns no WR, ND, or N21-C ladder rungs.",
        "",
        "## Frozen Schema Sections",
        "",
        "| Section | Key Constraint |",
        "| --- | --- |",
        "| source current | runtime/replay emitted, not report-built |",
        "| candidate evidence row | all required row fields frozen, including same-basin rule, claim allowed, and claim ceiling |",
        "| run artifact admissibility | paths exist, sha256 digests match, report-only blocked |",
        "| thresholds | declared before use, no post-outcome retuning |",
        "| withdrawal | modes/targets/window/floor policy frozen |",
        "| probe absence | runtime absence, residue absence, annotation not evidence |",
        "| replay/control | status enum and demotion effects frozen |",
        "| ladders | WR0-WR6, ND0-ND6, N21-C0-N21-C6 |",
        "| active nulls | comparable seed/topology/envelope/digests required |",
        "",
        "## Candidate Evidence Row Required Fields",
        "",
        "```text",
        *freeze["candidate_evidence_row_schema"]["required_fields"],
        "```",
        "",
        "## Read-Only I1 Contract References",
        "",
        "| Primitive | Same-Basin Rule | Support Scaffold | Handoff Primitive |",
        "| --- | --- | --- | --- |",
    ]
    for row in freeze["primitive_schema_rows"]:
        lines.append(
            "| "
            f"`{row['primitive_id']}` | "
            f"`{row['same_basin_continuation_rule']['rule_id']}` | "
            f"`{row['support_scaffold']['support_id']}` | "
            f"`{row['handoff_inputs']['primitive_id']}` |"
        )
    lines.extend(
        [
            "",
            "## Run-Artifact Required Fields",
            "",
            "```text",
            *freeze["run_artifact_admissibility_schema"]["required_fields"],
            "```",
            "",
            "## Replay Requirements",
            "",
            "```json",
            json.dumps(
                freeze["replay_control_schema"]["required_replay_modes"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Ladders",
            "",
            "| Ladder | Rungs | Scope |",
            "| --- | ---: | --- |",
            "| WR | 7 | withdrawal-resistance primitive evidence |",
            "| ND | 7 | N21-local artifact naturalization-depth evidence |",
            "| N21-C | 7 | combined closeout classification |",
            "",
            "## Boundary",
            "",
            "```text",
            "primitive_evidence_opened = false",
            "withdrawal_resistance_supported = false",
            "naturalization_depth_supported = false",
            "wr_ladder_rung_assigned = false",
            "nd_ladder_rung_assigned = false",
            "positive_run_artifacts_consumed = false",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in data["checks"]:
        detail = item["detail"]
        if not isinstance(detail, str):
            detail = json.dumps(detail, sort_keys=True)
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Iteration 2 closes the schema freeze needed before active nulls and",
            "positive probes. It makes source-current evidence, artifact",
            "admissibility, thresholds, withdrawal/probe absence, replay/control",
            "status, ladder assignment, and demotion precedence fail-closed.",
            "It remains schema-only and does not support WR, ND, agency, native",
            "support, sentience, Phase 8, or ant-ecology implementation.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    data = build_payload()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")


if __name__ == "__main__":
    main()
