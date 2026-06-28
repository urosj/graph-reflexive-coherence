#!/usr/bin/env python3
"""Build N25.2 Iteration 2 MB6 gate schema and controls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
I1_OUTPUT = EXPERIMENT / "outputs" / "n25_2_source_inventory_and_admissibility_audit.json"
OUTPUT = EXPERIMENT / "outputs" / "n25_2_mb6_gate_schema_and_controls.json"
REPORT = EXPERIMENT / "reports" / "n25_2_mb6_gate_schema_and_controls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_mb6_gate_schema_and_controls.py"
)

MB6_GATE_STATUS_ENUM = [
    "not_applied",
    "supported",
    "blocked",
    "demotes_mb5",
    "not_applicable",
]

GATE_RESULT_STATUS_ENUM = [
    "passed",
    "failed_closed",
    "failed_open",
    "blocked",
    "not_run",
    "not_applicable",
]

CONTROL_STATUS_ENUM = [
    "passed",
    "failed_closed",
    "failed_open",
    "blocked",
    "not_run",
    "not_applicable",
]

N26_CONSUMPTION_EFFECT_ENUM = [
    "unscoped_consumption_blocked",
    "scoped_mb6_substrate_consumption_allowed",
    "scoped_provisional_context_only",
    "blocked_pending_repair",
    "mb5_demoted_blocks_n26",
]

I3_MB5_CHAIN_STATUS_ENUM = [
    "mb5_chain_validated_for_runtime_probe",
    "mb5_chain_validated_with_blockers",
    "mb5_demoted_repair_required",
    "mb5_chain_unreadable_blocks_runtime_probe",
]

RUNTIME_ARTIFACT_ROLE_ENUM = [
    "runtime_execution_trace",
    "flow_window_records",
    "child_basin_state_records",
    "topology_refinement_provenance",
    "producer_native_mutation_ownership_ledger",
    "runtime_config",
    "runtime_snapshot",
    "artifact_replay_trace",
    "snapshot_load_replay_trace",
    "duplicate_replay_trace",
    "multi_window_persistence_replay_trace",
    "fail_closed_control_trace",
    "stress_variant_trace",
    "closeout",
    "report",
]

IMPLEMENTATION_DIGEST_FIELDS = [
    "runtime_source_digest",
    "runtime_config_digest",
    "implementation_contract_schema_digest",
    "lgrc9v3_runtime_file_sha256",
    "lgrc9v3_runtime_state_file_sha256",
    "lgrc9v3_contract_file_sha256",
    "telemetry_contract_file_sha256",
    "focused_test_digest_or_test_result_digest",
]

IMPLEMENTATION_NO_MUTATION_PROOF_FIELDS = [
    "implementation_modification_allowed",
    "implementation_source_modification_observed",
    "src_diff_expected",
    "src_diff_observed",
    "spec_diff_observed",
    "test_diff_observed",
    "example_diff_observed",
    "runtime_execution_from_closed_implementation",
    "defect_fix_attempted",
    "defect_disposition",
]

CHILD_BASIN_STATE_RECORD_REQUIRED_FIELDS = [
    "child_basin_id",
    "birth_or_detection_step",
    "parent_or_source_basin_id",
    "boundary_birth_or_refinement_provenance",
    "support_core_nodes",
    "coherence_core_nodes",
    "basin_signature_digest",
    "topology_signature_before",
    "topology_signature_after",
    "flow_window_id",
    "merge_leakage_status",
    "persistence_window_status",
    "producer_native_mutation_owner",
    "trace_origin",
    "trace_digest",
]

SOURCE_ADMISSIBILITY_ENUM = [
    "admissible_for_inventory",
    "admissible_for_mb5_chain_audit",
    "admissible_for_mb6_gate_context",
    "corroboration_only",
    "blocked_missing_or_unparseable",
]

SOURCE_ROLE_ENUM = [
    "n25_bf5_context",
    "n25_1_requirements_context",
    "phase8_mb5_closeout_evidence",
    "phase8_plan_context",
    "phase8_contract_schema_context",
    "runtime_source_audit",
    "test_audit",
    "telemetry_example_corroboration",
    "visual_corroboration_only",
    "report_context_only",
]

SOURCE_ROLE_CONSUMPTION_RULES = {
    "n25_bf5_context": {
        "may_support": ["scoped_sub_basin_context"],
        "must_not_support": ["MB6", "independent_multi_basin_formation"],
    },
    "n25_1_requirements_context": {
        "may_support": ["requirements_context", "MB_ladder_context"],
        "must_not_support": ["runtime_evidence", "MB5", "MB6"],
    },
    "phase8_mb5_closeout_evidence": {
        "may_support": ["MB5_evidence_input"],
        "must_not_support": ["automatic_MB6", "native_support"],
    },
    "phase8_plan_context": {
        "may_support": ["planned_gate_context"],
        "must_not_support": ["final_result_evidence"],
    },
    "phase8_contract_schema_context": {
        "may_support": ["schema_admissibility_context"],
        "must_not_support": ["positive_runtime_result_by_itself"],
    },
    "runtime_source_audit": {
        "may_support": ["audit_runtime_surface_verification"],
        "must_not_support": ["new_implementation", "claim_support_without_artifacts"],
    },
    "test_audit": {
        "may_support": ["admissibility_context"],
        "must_not_support": ["MB6_support_by_itself"],
    },
    "telemetry_example_corroboration": {
        "may_support": ["telemetry_corroboration_only"],
        "must_not_support": ["runtime_evidence", "replay_evidence", "MB6_support"],
    },
    "visual_corroboration_only": {
        "may_support": ["visual_corroboration_only"],
        "must_not_support": ["runtime_evidence", "replay_evidence", "MB6_support"],
    },
    "report_context_only": {
        "may_support": ["interpretation_context"],
        "must_not_support": ["runtime_evidence_by_itself"],
    },
}

MB5_MB6_INVARIANTS = {
    "phase8_mb5_validated_does_not_imply_mb6": True,
    "mb6_requires_independent_n25_2_gate": True,
    "n25_2_c6_closeout_does_not_imply_mb6": True,
}

MB5_DEMOTION_POLICY = {
    "mb5_demoted_if": [
        "phase8_closeout_missing_or_unparseable",
        "mb5_asserted_without_replay_control_evidence",
        "runtime_surface_mismatch",
        "child_basin_state_records_missing",
        "merge_leakage_controls_missing_or_failed_open",
        "producer_audit_missing",
        "unsafe_claim_flag_true",
        "mb6_already_claimed_without_n25_2_gate",
    ],
    "mb5_demotion_effect": [
        "repair_required",
        "n26_consumption_blocked",
        "phase8_evidence_chain_invalid",
    ],
}

PRODUCER_SCHEDULING_ROLE_ENUM = [
    "context_only",
    "compatibility_audit",
    "blocker_if_used_as_native_support",
]

RUNTIME_MUTATION_OWNER_ENUM = [
    "LGRC9V3_runtime_transition",
    "producer_surface",
    "hidden_producer_blocks_row",
    "not_recorded_blocks_row",
]

UNSAFE_CLAIMS = [
    "semantic_learning_claim_allowed",
    "semantic_choice_claim_allowed",
    "agency_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "sentience_claim_allowed",
    "organism_life_claim_allowed",
    "ant_ecology_claim_allowed",
    "phase8_completion_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
]

REQUIRED_CANDIDATE_FIELDS = [
    {"field": "row_id", "type": "string", "required": True},
    {"field": "source_artifact_path", "type": "repo_relative_path", "required": True},
    {"field": "source_artifact_digest", "type": "sha256", "required": True},
    {"field": "source_role", "type": "enum", "enum": SOURCE_ROLE_ENUM},
    {"field": "source_admissibility_decision", "type": "enum", "enum": SOURCE_ADMISSIBILITY_ENUM},
    {"field": "source_evidence_kind", "type": "string", "required": True},
    {"field": "may_consume_as", "type": "list[string]", "required": True},
    {"field": "must_not_consume_as", "type": "list[string]", "required": True},
    {"field": "mb_ladder_input", "type": "string", "required": True},
    {"field": "mb_ladder_candidate", "type": "string", "required": True},
    {"field": "n25_2_closeout_candidate", "type": "string", "required": True},
    {"field": "source_current_inputs", "type": "list[object]", "required": True},
    {"field": "native_runtime_execution_evidence", "type": "object", "required": True},
    {"field": "runtime_execution_trace", "type": "object", "required": True},
    {"field": "runtime_surface_evidence", "type": "object", "required": True},
    {"field": "child_basin_state_records", "type": "object", "required": True},
    {
        "field": "child_basin_state_record_schema",
        "type": "schema_reference",
        "required": True,
    },
    {"field": "multi_basin_substrate_persistence", "type": "object", "required": True},
    {"field": "replay_evidence", "type": "object", "required": True},
    {"field": "control_evidence", "type": "object", "required": True},
    {"field": "producer_audit_evidence", "type": "object", "required": True},
    {"field": "telemetry_example_evidence", "type": "object", "required": True},
    {"field": "artifact_manifest", "type": "list[object]", "required": True},
    {"field": "artifact_role", "type": "enum", "enum": RUNTIME_ARTIFACT_ROLE_ENUM},
    {"field": "implementation_digest_bundle", "type": "object", "required": True},
    {"field": "implementation_no_mutation_proof", "type": "object", "required": True},
    {"field": "mb6_gate_status", "type": "enum", "enum": MB6_GATE_STATUS_ENUM},
    {"field": "mb6_gate_results", "type": "list[object]", "required": True},
    {"field": "mb6_blockers", "type": "list[string]", "required": True},
    {"field": "mb5_demotion_status", "type": "enum", "required": True},
    {
        "field": "n26_consumption_effect",
        "type": "enum",
        "enum": N26_CONSUMPTION_EFFECT_ENUM,
    },
    {"field": "n26_consumption_scope", "type": "object", "required": True},
    {"field": "producer_native_discipline", "type": "object", "required": True},
    {"field": "runtime_mutation_owner", "type": "enum", "enum": RUNTIME_MUTATION_OWNER_ENUM},
    {"field": "runtime_execution_from_closed_implementation", "type": "boolean", "required": True},
    {"field": "defect_fix_attempted", "type": "boolean_false", "required": True},
    {"field": "defect_disposition", "type": "string", "required": True},
    {"field": "visual_evidence_limits", "type": "object", "required": True},
    {"field": "variant_comparability", "type": "object", "required": "I4-A_and_variants"},
    {"field": "unsafe_claim_flags", "type": "object[bool_false]", "required": True},
    {"field": "row_decision", "type": "enum", "required": True},
    {"field": "claim_ceiling", "type": "string", "required": True},
]

MB6_SUPPORT_GATES = [
    {
        "gate_id": "source_inventory_admissible",
        "required_for_mb6": True,
        "required_evidence": "I1 source inventory passed with no failed checks.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "phase8_mb5_chain_validated",
        "required_for_mb6": True,
        "required_evidence": "I3 validates Phase 8 MB5 evidence chain without demotion.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "source_backed_multi_basin_runtime_surfaces",
        "required_for_mb6": True,
        "required_evidence": (
            "source-backed runtime surfaces for multi-basin formation, not "
            "report-only or visual-only evidence"
        ),
        "missing_effect": "blocked",
    },
    {
        "gate_id": "source_backed_child_basin_state_records",
        "required_for_mb6": True,
        "required_evidence": (
            "child-basin records include core ids, membership, boundary edges, "
            "support/coherence margins, and parent/neighbor relations"
        ),
        "missing_effect": "blocked",
    },
    {
        "gate_id": "replay_backed_child_basin_persistence",
        "required_for_mb6": True,
        "required_evidence": "multi-basin state persists across declared replay windows.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "artifact_snapshot_duplicate_replay_clean",
        "required_for_mb6": True,
        "required_evidence": (
            "artifact replay, snapshot/load replay, and duplicate replay all pass"
        ),
        "missing_effect": "blocked",
    },
    {
        "gate_id": "merge_leakage_controls_fail_closed",
        "required_for_mb6": True,
        "required_evidence": "merge, leakage, and old-basin-thickening controls reject false positives.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "producer_native_mutation_ownership_clean",
        "required_for_mb6": True,
        "required_evidence": (
            "producer audit passes, runtime mutation is LGRC9V3-owned, and "
            "producer success is not native support"
        ),
        "missing_effect": "blocked",
    },
    {
        "gate_id": "front_capacity_boundary_birth_provenance_when_used",
        "required_for_mb6": True,
        "required_evidence": (
            "front-capacity or boundary-birth companion evidence is recorded "
            "when used and cannot backfill MB6 by label"
        ),
        "missing_effect": "blocked",
    },
    {
        "gate_id": "hidden_producer_basin_insertion_rejected",
        "required_for_mb6": True,
        "required_evidence": "hidden producer basin insertion control fails closed.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "label_only_basin_formation_rejected",
        "required_for_mb6": True,
        "required_evidence": "label-only basin formation control fails closed.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "old_basin_thickening_relabel_rejected",
        "required_for_mb6": True,
        "required_evidence": "old-basin thickening relabel control fails closed.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "transient_flow_sink_relabel_rejected",
        "required_for_mb6": True,
        "required_evidence": "transient flow-sink relabel control fails closed.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "graph_visual_only_success_rejected",
        "required_for_mb6": True,
        "required_evidence": "graph visual-only success control fails closed.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "visual_evidence_corroboration_only",
        "required_for_mb6": True,
        "required_evidence": "visual examples are corroboration only and cannot satisfy gates.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "n26_consumption_rule_explicit",
        "required_for_mb6": True,
        "required_evidence": "N26 consumption scope is explicit and derived from gate result.",
        "missing_effect": "blocked",
    },
    {
        "gate_id": "unsafe_claim_flags_false",
        "required_for_mb6": True,
        "required_evidence": "all unsafe claim flags remain false.",
        "missing_effect": "blocked",
    },
]

FAIL_CLOSED_CONTROLS = [
    {
        "control_id": "label_only_multi_basin_relabel",
        "blocked_condition": "multi-basin label appears without runtime state records",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "old_basin_thickening_as_new_basin",
        "blocked_condition": "old basin thickens locally but no separable child basin persists",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "transient_flow_sink_as_child_basin",
        "blocked_condition": "one-window flow sink is interpreted as persistent child basin",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "collapse_reabsorption_relabel",
        "blocked_condition": "collapse/reabsorption telemetry is relabeled as independent basin birth",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "graph_visual_only_success",
        "blocked_condition": "visual topology growth is used without source-current replay evidence",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "hidden_producer_basin_insertion",
        "blocked_condition": "producer inserts basin content that runtime transitions do not own",
        "rung_effect": "blocks_MB6_and_N26_substrate_consumption",
    },
    {
        "control_id": "producer_success_as_native_support",
        "blocked_condition": "producer-assisted success is consumed as native support",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "front_capacity_backfill_control",
        "blocked_condition": "front-capacity companion evidence is used to backfill missing MB6 runtime evidence",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "mb5_as_mb6_relabel",
        "blocked_condition": "Phase 8 MB5 is promoted to MB6 without N25.2 gate pass",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "n25_bf5_as_independent_multi_basin",
        "blocked_condition": "N25 scoped BF5 sub-basin is consumed as independent multi-basin evidence",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "n25_1_requirements_as_runtime_evidence",
        "blocked_condition": "N25.1 requirements are consumed as runtime evidence",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "n25_2_c6_as_mb6_support",
        "blocked_condition": "bridge closeout rung is treated as MB6 support by itself",
        "rung_effect": "blocks_MB6",
    },
    {
        "control_id": "phase8_completion_relabel_control",
        "blocked_condition": "Phase 8 completion is claimed from N25.2 validation evidence",
        "rung_effect": "blocks_claim_and_MB6",
    },
    {
        "control_id": "semantic_learning_relabel_control",
        "blocked_condition": "multi-basin evidence is relabeled as semantic learning",
        "rung_effect": "blocks_claim_and_MB6",
    },
    {
        "control_id": "semantic_choice_relabel_control",
        "blocked_condition": "multi-basin evidence is relabeled as semantic choice",
        "rung_effect": "blocks_claim_and_MB6",
    },
    {
        "control_id": "agency_relabel_control",
        "blocked_condition": "multi-basin evidence is relabeled as agency",
        "rung_effect": "blocks_claim_and_MB6",
    },
    {
        "control_id": "native_support_relabel_control",
        "blocked_condition": "multi-basin evidence or producer success is relabeled as native support",
        "rung_effect": "blocks_claim_and_MB6",
    },
    {
        "control_id": "sentience_relabel_control",
        "blocked_condition": "multi-basin evidence is relabeled as sentience",
        "rung_effect": "blocks_claim_and_MB6",
    },
    {
        "control_id": "ant_ecology_relabel_control",
        "blocked_condition": "N25.2 evidence is relabeled as ant ecology implementation",
        "rung_effect": "blocks_claim_and_MB6",
    },
    {
        "control_id": "organism_life_relabel_control",
        "blocked_condition": "multi-basin evidence is relabeled as organism/life",
        "rung_effect": "blocks_claim_and_MB6",
    },
    {
        "control_id": "unrestricted_autonomy_relabel_control",
        "blocked_condition": "multi-basin evidence is relabeled as unrestricted autonomy",
        "rung_effect": "blocks_claim_and_MB6",
    },
]

N26_CONSUMPTION_RULES = {
    "before_mb6_gate": {
        "n26_unscoped_multi_basin_consumption_allowed": False,
        "n26_scoped_context_consumption_allowed": "pending",
        "n26_consumption_effect": "unscoped_consumption_blocked",
        "n26_consumption_blocker": "blocked_pending_mb6_gate",
    },
    "if_mb6_blocked": {
        "n26_unscoped_multi_basin_consumption_allowed": False,
        "n26_scoped_context_consumption_allowed": True,
        "n26_consumption_effect": "scoped_provisional_context_only",
    },
    "if_mb6_supported": {
        "n26_unscoped_multi_basin_consumption_allowed": False,
        "n26_scoped_context_consumption_allowed": True,
        "n26_consumption_effect": "scoped_mb6_substrate_consumption_allowed",
    },
    "if_mb5_demoted": {
        "n26_unscoped_multi_basin_consumption_allowed": False,
        "n26_scoped_context_consumption_allowed": False,
        "n26_consumption_effect": "mb5_demoted_blocks_n26",
    },
    "if_repair_required": {
        "n26_unscoped_multi_basin_consumption_allowed": False,
        "n26_scoped_context_consumption_allowed": False,
        "n26_consumption_effect": "blocked_pending_repair",
    },
}

PRODUCER_NATIVE_DISCIPLINE_SCHEMA = {
    "producer_scheduling_present": "row_local_boolean_required",
    "producer_scheduling_role_enum": PRODUCER_SCHEDULING_ROLE_ENUM,
    "producer_scheduling_may_consume_as": "audit_context_only",
    "producer_scheduling_must_not_consume_as": "native_support",
    "producer_compatibility_audit_required": True,
    "runtime_mutation_owner_enum": RUNTIME_MUTATION_OWNER_ENUM,
    "runtime_mutation_ownership_required": "LGRC9V3_transitions",
    "hidden_producer_basin_insertion_allowed": False,
    "producer_success_can_upgrade_native": False,
    "producer_success_overwrites_native_failure": False,
}

VISUAL_EVIDENCE_LIMIT_SCHEMA = {
    "visual_evidence_role": "corroboration_only",
    "may_consume_as": ["telemetry_or_visual_corroboration_only"],
    "must_not_consume_as": ["runtime_evidence", "replay_evidence", "MB6_support"],
    "visual_graph_growth_supports_mb6": False,
    "examples_support_mb6_without_runtime_replay": False,
    "graph_visual_only_success_allowed": False,
}

RECONSTRUCTION_POLICY = {
    "runtime_execution_required_for_positive_candidate": True,
    "reconstruction_can_validate_runtime_records": True,
    "reconstruction_can_create_original_child_basin_evidence": False,
    "replay_without_runtime_execution_blocks_MB6": True,
}

MB5_RUNTIME_EVIDENCE_SEPARATION_POLICY = {
    "i3_question": "does_closed_phase8_mb5_remain_admissible",
    "i4_question": "can_closed_runtime_emit_new_source_current_multi_basin_candidate_evidence",
    "i8_question": "does_combined_i3_to_i7_evidence_pass_MB6",
    "i4_positive_runtime_evidence_cannot_retroactively_fix_i3_mb5_chain": True,
    "phase8_mb5_chain_defect_with_runtime_probe_support_status": (
        "phase8_mb5_chain_has_defect_but_n25_2_runtime_probe_supports_repair_target"
    ),
}

VARIANT_PROBE_COMPARABILITY_SCHEMA = {
    "variant_probe_is_not_retuned_copy": True,
    "variant_uses_closed_runtime": True,
    "variant_changes_declared_axis_enum": [
        "fixture",
        "seed",
        "topology",
        "front_capacity_boundary_birth",
    ],
    "variant_comparability_digest_required": True,
    "variant_may_support_generalization": "bounded",
    "variant_cannot_backfill_unrelated_MB5_rows": True,
}


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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/")
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    i1_digest = str(i1["output_digest"])
    validation_runtime_policy = {
        "existing_lgrc9v3_runtime_execution_allowed": True,
        "runtime_execution_is_primary_positive_evidence": True,
        "runtime_execution_does_not_open_implementation_tranche": True,
        "runtime_execution_artifact_roles_frozen": True,
        "runtime_execution_required_for_I4_positive_candidate": True,
        "artifact_reconstruction_is_replay_validation_not_replacement": True,
        "replay_reconstructs_or_validates_runtime_records_only": True,
        "replay_cannot_replace_original_runtime_execution": True,
        "implementation_source_modification_allowed": False,
        "src_specs_tests_examples_or_implementation_edits_allowed": False,
        "defect_disposition": "record_as_blocker_or_repair_target_only",
    }

    closeout_ladder = {
        "N25.2-C0": "initialized_validation_bridge_only",
        "N25.2-C1": "source_inventory_and_admissibility_audit_passed",
        "N25.2-C2": "Phase_8_MB5_evidence_chain_validated_or_demotion_recorded",
        "N25.2-C3": "MB6_gate_schema_and_active_blockers_frozen",
        "N25.2-C4": "MB6_support_blocker_matrix_complete",
        "N25.2-C5": "N26_consumption_classification_complete",
        "N25.2-C6": "closeout_and_N26_handoff_complete",
    }
    row_decision_policy = {
        "supported": "local row gates passed within declared scope",
        "partial": "some evidence present but MB6 or N26 substrate gates remain blocked",
        "blocked": "required gate missing or not run",
        "rejected": "false-positive or relabel path failed closed",
        "not_applicable": "outside row scope with explicit reason required",
    }
    schema_sections = {
        "candidate_row_schema": REQUIRED_CANDIDATE_FIELDS,
        "runtime_artifact_role_enum": RUNTIME_ARTIFACT_ROLE_ENUM,
        "implementation_digest_fields": IMPLEMENTATION_DIGEST_FIELDS,
        "implementation_no_mutation_proof_fields": (
            IMPLEMENTATION_NO_MUTATION_PROOF_FIELDS
        ),
        "child_basin_state_record_schema": {
            "required_fields": CHILD_BASIN_STATE_RECORD_REQUIRED_FIELDS,
            "missing_required_field_effect": "blocks_MB6",
        },
        "i3_mb5_chain_status_enum": I3_MB5_CHAIN_STATUS_ENUM,
        "reconstruction_policy": RECONSTRUCTION_POLICY,
        "mb5_runtime_evidence_separation_policy": (
            MB5_RUNTIME_EVIDENCE_SEPARATION_POLICY
        ),
        "variant_probe_comparability_schema": VARIANT_PROBE_COMPARABILITY_SCHEMA,
        "mb6_gate_status_schema": {
            "mb6_gate_status_enum": MB6_GATE_STATUS_ENUM,
            "gate_result_status_enum": GATE_RESULT_STATUS_ENUM,
            "mb6_gate_applied_in_iteration_2": False,
        },
        "mb6_support_gates": MB6_SUPPORT_GATES,
        "mb5_mb6_invariants": MB5_MB6_INVARIANTS,
        "mb5_demotion_policy": MB5_DEMOTION_POLICY,
        "replay_requirements": {
            "required_for_mb6": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
                "multi_window_child_basin_persistence_replay",
            ],
            "child_basin_persistence_requires_replay": True,
            "merge_leakage_controls_required": True,
            "control_failed_open_blocks_mb6": True,
            "control_not_run_blocks_mb6": True,
            "failed_or_not_run_effect": "blocks_MB6",
        },
        "control_requirements": {
            "status_enum": CONTROL_STATUS_ENUM,
            "status_semantics": {
                "failed_closed": "blocker triggered and claim correctly rejected",
                "failed_open": "blocker triggered but claim still passed",
                "not_run": "blocks dependent rung",
                "not_applicable": "requires scope reason",
            },
            "fail_closed_controls": FAIL_CLOSED_CONTROLS,
            "failed_open_effect": "invalidates_row_and_blocks_MB6",
            "not_run_effect": "blocks_dependent_gate",
        },
        "source_admissibility_rules": {
            "source_role_enum": SOURCE_ROLE_ENUM,
            "source_role_consumption_rules": SOURCE_ROLE_CONSUMPTION_RULES,
            "source_admissibility_enum": SOURCE_ADMISSIBILITY_ENUM,
            "blocked_missing_or_unparseable_effect": "blocks_dependent_gate",
            "corroboration_only_cannot_satisfy_mb6": True,
        },
        "producer_native_discipline": PRODUCER_NATIVE_DISCIPLINE_SCHEMA,
        "visual_evidence_limits": VISUAL_EVIDENCE_LIMIT_SCHEMA,
        "validation_runtime_policy": validation_runtime_policy,
        "n26_consumption_rules": N26_CONSUMPTION_RULES,
        "unsafe_claim_flags": unsafe_claim_flags(),
    }

    checks = [
        check(
            "i1_source_inventory_passed",
            i1["status"] == "passed" and i1["failed_checks"] == [],
            {"i1_output_digest": i1_digest},
        ),
        check(
            "i1_ready_for_iteration_2",
            i1["ready_for_iteration_2_mb6_gate_schema"] is True,
            i1["ready_for_iteration_2_mb6_gate_schema"],
        ),
        check(
            "mb6_gate_schema_frozen",
            len(MB6_SUPPORT_GATES) == 17
            and all(gate["required_for_mb6"] for gate in MB6_SUPPORT_GATES),
            [gate["gate_id"] for gate in MB6_SUPPORT_GATES],
        ),
        check(
            "candidate_required_fields_present",
            len(REQUIRED_CANDIDATE_FIELDS) == 42,
            [field["field"] for field in REQUIRED_CANDIDATE_FIELDS],
        ),
        check(
            "n26_consumption_rules_freeze_scope",
            N26_CONSUMPTION_RULES["if_mb6_supported"][
                "n26_unscoped_multi_basin_consumption_allowed"
            ]
            is False
            and N26_CONSUMPTION_RULES["if_mb6_supported"][
                "n26_consumption_effect"
            ]
            == "scoped_mb6_substrate_consumption_allowed",
            N26_CONSUMPTION_RULES,
        ),
        check(
            "fail_closed_controls_frozen",
            len(FAIL_CLOSED_CONTROLS) == 21,
            [control["control_id"] for control in FAIL_CLOSED_CONTROLS],
        ),
        check(
            "mb5_mb6_invariants_frozen",
            all(MB5_MB6_INVARIANTS.values()),
            MB5_MB6_INVARIANTS,
        ),
        check(
            "mb5_demotion_policy_frozen",
            len(MB5_DEMOTION_POLICY["mb5_demoted_if"]) == 8,
            MB5_DEMOTION_POLICY,
        ),
        check(
            "source_role_categories_frozen",
            len(SOURCE_ROLE_ENUM) == 10
            and "visual_corroboration_only" in SOURCE_ROLE_ENUM,
            SOURCE_ROLE_ENUM,
        ),
        check(
            "runtime_artifact_roles_frozen",
            len(RUNTIME_ARTIFACT_ROLE_ENUM) == 15
            and "runtime_execution_trace" in RUNTIME_ARTIFACT_ROLE_ENUM
            and "multi_window_persistence_replay_trace" in RUNTIME_ARTIFACT_ROLE_ENUM,
            RUNTIME_ARTIFACT_ROLE_ENUM,
        ),
        check(
            "implementation_digest_fields_frozen",
            len(IMPLEMENTATION_DIGEST_FIELDS) == 8
            and "lgrc9v3_runtime_file_sha256" in IMPLEMENTATION_DIGEST_FIELDS,
            IMPLEMENTATION_DIGEST_FIELDS,
        ),
        check(
            "implementation_no_mutation_proof_frozen",
            len(IMPLEMENTATION_NO_MUTATION_PROOF_FIELDS) == 10
            and "src_diff_observed" in IMPLEMENTATION_NO_MUTATION_PROOF_FIELDS
            and "defect_fix_attempted" in IMPLEMENTATION_NO_MUTATION_PROOF_FIELDS,
            IMPLEMENTATION_NO_MUTATION_PROOF_FIELDS,
        ),
        check(
            "child_basin_state_record_schema_frozen",
            len(CHILD_BASIN_STATE_RECORD_REQUIRED_FIELDS) == 15
            and "producer_native_mutation_owner"
            in CHILD_BASIN_STATE_RECORD_REQUIRED_FIELDS,
            CHILD_BASIN_STATE_RECORD_REQUIRED_FIELDS,
        ),
        check(
            "reconstruction_policy_subordinate_to_runtime",
            RECONSTRUCTION_POLICY["runtime_execution_required_for_positive_candidate"]
            is True
            and RECONSTRUCTION_POLICY[
                "reconstruction_can_create_original_child_basin_evidence"
            ]
            is False,
            RECONSTRUCTION_POLICY,
        ),
        check(
            "mb5_runtime_evidence_separation_frozen",
            MB5_RUNTIME_EVIDENCE_SEPARATION_POLICY[
                "i4_positive_runtime_evidence_cannot_retroactively_fix_i3_mb5_chain"
            ]
            is True,
            MB5_RUNTIME_EVIDENCE_SEPARATION_POLICY,
        ),
        check(
            "variant_probe_comparability_frozen",
            VARIANT_PROBE_COMPARABILITY_SCHEMA[
                "variant_probe_is_not_retuned_copy"
            ]
            is True
            and VARIANT_PROBE_COMPARABILITY_SCHEMA[
                "variant_cannot_backfill_unrelated_MB5_rows"
            ]
            is True,
            VARIANT_PROBE_COMPARABILITY_SCHEMA,
        ),
        check(
            "producer_native_discipline_frozen",
            PRODUCER_NATIVE_DISCIPLINE_SCHEMA["producer_success_can_upgrade_native"]
            is False
            and PRODUCER_NATIVE_DISCIPLINE_SCHEMA[
                "hidden_producer_basin_insertion_allowed"
            ]
            is False,
            PRODUCER_NATIVE_DISCIPLINE_SCHEMA,
        ),
        check(
            "visual_evidence_limits_frozen",
            VISUAL_EVIDENCE_LIMIT_SCHEMA["graph_visual_only_success_allowed"]
            is False
            and "MB6_support" in VISUAL_EVIDENCE_LIMIT_SCHEMA["must_not_consume_as"],
            VISUAL_EVIDENCE_LIMIT_SCHEMA,
        ),
        check(
            "validation_runtime_policy_frozen",
            validation_runtime_policy["existing_lgrc9v3_runtime_execution_allowed"]
            is True
            and validation_runtime_policy[
                "implementation_source_modification_allowed"
            ]
            is False
            and validation_runtime_policy["defect_disposition"]
            == "record_as_blocker_or_repair_target_only",
            validation_runtime_policy,
        ),
        check(
            "closeout_ladder_frozen_no_closeout_assignment",
            closeout_ladder["N25.2-C3"]
            == "MB6_gate_schema_and_active_blockers_frozen",
            closeout_ladder,
        ),
        check(
            "unsafe_claim_flags_false",
            all(flag is False for flag in unsafe_claim_flags().values()),
            unsafe_claim_flags(),
        ),
    ]

    data_without_digest = {
        "artifact_id": "n25_2_mb6_gate_schema_and_controls",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_mb6_gate_schema_and_controls_frozen_no_mb6_evidence"
        ),
        "experiment": "N25.2",
        "iteration": 2,
        "command": COMMAND,
        "source_inventory": {
            "path": (
                "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/"
                "outputs/n25_2_source_inventory_and_admissibility_audit.json"
            ),
            "sha256": sha256_file(I1_OUTPUT),
            "output_digest": i1_digest,
            "status": i1["status"],
            "acceptance_state": i1["acceptance_state"],
            "all_i1_source_roles_consumed_without_reclassification": True,
        },
        "schema_sections": schema_sections,
        "mb6_gate_status_enum": MB6_GATE_STATUS_ENUM,
        "gate_result_status_enum": GATE_RESULT_STATUS_ENUM,
        "control_status_enum": CONTROL_STATUS_ENUM,
        "row_decision_policy": row_decision_policy,
        "n25_2_closeout_ladder": closeout_ladder,
        "n25_2_closeout_ceiling": (
            "N25.2-C3_MB6_gate_schema_and_active_blockers_frozen"
        ),
        "n25_2_closeout_ladder_rung_assigned": False,
        "mb6_supported": False,
        "mb6_gate_applied": False,
        "mb6_gate_status": "not_applied",
        "mb6_gate_schema_frozen": True,
        "mb6_claim_allowed": False,
        "phase8_mb5_evidence_chain_audited": False,
        "mb6_support_matrix_deferred_to_iteration_4": True,
        "phase8_mb5_chain_audit_deferred_to_iteration_3": True,
        "mb5_demoted": False,
        "n26_unscoped_consumption_allowed": False,
        "n26_consumption_effect": "unscoped_consumption_blocked",
        "n26_consumption_blocker": "blocked_pending_mb6_gate",
        "runtime_implementation_opened": False,
        "existing_lgrc9v3_runtime_execution_allowed": True,
        "runtime_execution_is_primary_positive_evidence": True,
        "implementation_source_modification_allowed": False,
        "defect_disposition": "record_as_blocker_or_repair_target_only",
        "src_diff_expected": False,
        "ready_for_iteration_3_phase8_mb5_evidence_chain_audit": True,
        "claim_boundary": {
            "unsafe_claim_flags": unsafe_claim_flags(),
            "native_support_claim_allowed": False,
            "phase8_completion_claim_allowed": False,
            "agency_claim_allowed": False,
            "sentience_claim_allowed": False,
        },
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    data_without_digest["checks"].append(
        check(
            "no_absolute_paths_in_records",
            not contains_absolute_path(data_without_digest),
            "repo_relative_paths_only",
        )
    )
    data_without_digest["failed_checks"] = [
        item["check_id"] for item in data_without_digest["checks"] if not item["passed"]
    ]
    data_without_digest["output_digest"] = digest_value(data_without_digest)
    return data_without_digest


def write_report(data: dict[str, Any]) -> None:
    gates = [
        "| Gate | Missing Effect |",
        "|---|---|",
    ]
    for gate in data["schema_sections"]["mb6_support_gates"]:
        gates.append(f"| `{gate['gate_id']}` | {gate['missing_effect']} |")

    controls = [
        "| Control | Rung Effect |",
        "|---|---|",
    ]
    for control in data["schema_sections"]["control_requirements"][
        "fail_closed_controls"
    ]:
        controls.append(
            f"| `{control['control_id']}` | {control['rung_effect']} |"
        )

    checks = [
        "| Check | Passed |",
        "|---|---|",
    ]
    for item in data["checks"]:
        checks.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")

    report = f"""# N25.2 Iteration 2 - MB6 Gate Schema And Controls

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

Iteration 2 freezes the MB6 gate and control schema only. It does not audit the
Phase 8 MB5 evidence chain, does not apply the MB6 support matrix, and does not
open N26 unscoped multi-basin substrate consumption.

```text
i1_output_digest = {data['source_inventory']['output_digest']}
mb6_gate_schema_frozen = true
mb6_gate_applied = false
mb6_gate_status = not_applied
mb6_supported = false
phase8_mb5_evidence_chain_audited = false
mb5_demoted = false
n26_unscoped_consumption_allowed = false
n26_consumption_effect = unscoped_consumption_blocked
n26_consumption_blocker = blocked_pending_mb6_gate
runtime_implementation_opened = false
existing_lgrc9v3_runtime_execution_allowed = true
runtime_execution_is_primary_positive_evidence = true
implementation_source_modification_allowed = false
defect_disposition = record_as_blocker_or_repair_target_only
```

## MB6 Gates

{chr(10).join(gates)}

## Fail-Closed Controls

{chr(10).join(controls)}

## N26 Consumption Rule

```text
before MB6 gate: unscoped_consumption_blocked
if MB6 blocked: scoped_provisional_context_only
if MB6 supported: scoped_mb6_substrate_consumption_allowed
if repair required: blocked_pending_repair
if MB5 demoted: mb5_demoted_blocks_n26
unscoped multi-basin consumption: false
```

## Runtime Evidence Policy

```text
runtime_execution_is_primary_positive_evidence = true
runtime_execution_required_for_I4_positive_candidate = true
replay_reconstructs_or_validates_runtime_records_only = true
replay_cannot_replace_original_runtime_execution = true
implementation_source_modification_allowed = false
defect_disposition = record_as_blocker_or_repair_target_only
```

## Runtime Artifact Roles

```text
{chr(10).join(data['schema_sections']['runtime_artifact_role_enum'])}
```

## Claim Boundary

```text
mb6_claim_allowed = false
native_support_claim_allowed = false
phase8_completion_claim_allowed = false
agency_claim_allowed = false
sentience_claim_allowed = false
```

## Checks

{chr(10).join(checks)}

Output digest:

```text
{data['output_digest']}
```
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    data = build_output()
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()
