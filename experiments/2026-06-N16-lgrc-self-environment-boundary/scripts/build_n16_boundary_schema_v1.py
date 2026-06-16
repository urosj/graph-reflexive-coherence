#!/usr/bin/env python3
"""Build N16 Iteration 2 boundary schema and AP6 gate."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N16-lgrc-self-environment-boundary"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
CONFIGS = EXPERIMENT / "configs"
SCRIPTS = EXPERIMENT / "scripts"

INVENTORY_OUTPUT = OUTPUTS / "n16_boundary_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n16_boundary_source_inventory.md"
OUTPUT_PATH = OUTPUTS / "n16_boundary_schema_v1.json"
REPORT_PATH = REPORTS / "n16_boundary_schema_v1.md"
VALIDATOR_SCRIPT = SCRIPTS / "validate_n16_row.py"

CONFIG_PATHS = {
    "source_registry": CONFIGS / "n16_source_registry.json",
    "boundary_policy": CONFIGS / "n16_boundary_policy_v1.json",
    "budget_limits": CONFIGS / "n16_budget_limits_v1.json",
    "control_variants": CONFIGS / "n16_control_variants_v1.json",
    "replay_policy": CONFIGS / "n16_replay_policy_v1.json",
}

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "scripts/build_n16_boundary_schema_v1.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

BOUNDARY_STATE_VALUES = ["B0", "B1", "B2", "B3", "B4"]
CHALLENGE_CLASS_VALUES = ["C0", "C1", "C2", "C3", "C4", "C5"]
ROW_DECISION_VALUES = ["supported", "blocked", "partial", "rejected", "not_applicable"]
EXTERNAL_STATE_ROLE_VALUES = [
    "background",
    "resource",
    "perturbation",
    "structured_external_state",
    "shared_medium",
    "coupling_channel",
    "mixed",
    "not_applicable",
]
SYNTHESIS_MODE_VALUES = ["partial_mvp", "full"]

AP_LADDER = {
    "AP0": {
        "label": "passive integrated replay",
        "n16_interpretation": "source, null, or boundary blocker row with no AP6 claim",
    },
    "AP1": {
        "label": "runtime-visible trigger produces bounded response",
        "n16_interpretation": "boundary-relevant response context only",
    },
    "AP2": {
        "label": "support-sensitive regulation preserves a declared support condition",
        "n16_interpretation": "support/perturbation context only",
    },
    "AP3": {
        "label": "self-maintenance candidate",
        "n16_interpretation": "N13 support-seeking regulation usable as internal support axis",
    },
    "AP4": {
        "label": "consequence-sensitive selection",
        "n16_interpretation": "N14 route/resource context usable as external state axis",
    },
    "AP5": {
        "label": "endogenous proxy candidate",
        "n16_interpretation": "N15 source-current proxy formation usable as construction substrate",
    },
    "AP6": {
        "label": "self/environment boundary candidate",
        "n16_interpretation": (
            "internal support-relevant state and external resource, "
            "perturbation, structured state, or shared medium are separately "
            "represented, traceable, controlled, and replayable"
        ),
    },
    "AP7": {
        "label": "closed action-perception loop candidate",
        "n16_interpretation": "reserved for N17",
    },
    "AP8": {
        "label": "long-horizon agentic-like closure candidate",
        "n16_interpretation": "reserved for N18",
    },
}

ROW_SCHEMA_FIELDS = [
    "row_id",
    "cell_id",
    "boundary_state",
    "case_id",
    "challenge_class",
    "basin_count",
    "row_decision",
    "boundary_state_lineage_sources",
    "boundary_state_inherited_closed_claims",
    "boundary_state_constructed_support",
    "boundary_state_unsupported_extension",
    "required_n16_boundary_evidence",
    "source_experiment",
    "source_iteration",
    "source_artifact",
    "source_report",
    "source_sha256",
    "source_report_sha256",
    "source_status",
    "mechanism_name",
    "mechanism_role",
    "source_role_classification",
    "role_classification_audit",
    "evidence_strategy",
    "evidence_strategy_class",
    "old_best_claim_inputs",
    "direct_historic_ap6_support_status",
    "direct_historic_support_status",
    "ap5_contribution_status",
    "boundary_state_relevance",
    "challenge_class_relevance",
    "arc_method_mapping",
    "runtime_state_surface_id",
    "state_source_window",
    "source_current",
    "internal_state_descriptor",
    "external_resource_descriptor",
    "external_perturbation_descriptor",
    "external_structured_state_descriptor",
    "external_state_role",
    "basin_descriptor",
    "boundary_policy",
    "case_policy",
    "boundary_condition_evaluated_at",
    "boundary_surface",
    "boundary_side_assignments",
    "self_region_nodes",
    "external_region_nodes",
    "boundary_edges",
    "boundary_crossing_trace",
    "dependency_trace",
    "internal_coherence",
    "external_coherence",
    "coherence_margin",
    "inbound_flux",
    "outbound_flux",
    "retained_flux",
    "leakage_ratio",
    "boundary_stability_score",
    "repair_score",
    "noise_resilience_score",
    "flux_tolerance_score",
    "basin_separation_score",
    "native_boundary_requirements_observed",
    "requirements_satisfied",
    "requirements_failed",
    "budget_cost_surface",
    "budget_units",
    "budget_validity",
    "replay_digest_inputs",
    "replay_digest_algorithm",
    "idempotency_digest_plan",
    "artifact_only_replay_status",
    "snapshot_load_status",
    "order_inversion_replay_status",
    "boundary_claim_allowed",
    "boundary_classification",
    "failure_mode",
    "externally_supplied_boundary_control",
    "post_hoc_boundary_label_control",
    "hidden_external_state_injection_control",
    "resource_relabel_as_self_control",
    "self_support_relabel_as_external_control",
    "untracked_boundary_crossing_control",
    "structured_external_coherence_rejection_control",
    "multi_basin_merge_control",
    "identity_acceptance_relabel_control",
    "selfhood_personhood_relabel_control",
    "semantic_goal_ownership_relabel_control",
    "native_support_relabel_control",
    "provisional_ap_level",
    "provisional_claim_ceiling",
    "claim_ceiling",
    "claim_ceiling_preserved",
    "claim_promotion_allowed",
    "blocked_claims",
    "missing_gates",
    "ap6_required_evidence_still_missing",
    "final_ap6_supported",
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
    "synthesis_mode",
    "included_iterations",
    "deferred_iterations",
    "final_ap6_closeout_allowed",
    "source_artifacts",
    "source_reports",
    "rows",
    "controls",
    "checks",
    "claim_flags",
    "errors",
    "output_digest",
]

TOP_LEVEL_SCHEMA_FREEZE_FIELDS = [
    "experiment",
    "iteration",
    "artifact_id",
    "purpose",
    "schema_version",
    "generated_at",
    "command",
    "status",
    "acceptance_state",
    "target_ap_ceiling",
    "synthesis_mode",
    "included_iterations",
    "deferred_iterations",
    "final_ap6_closeout_allowed",
    "iteration_result",
    "schema_summary",
    "ap_ladder",
    "row_schema_fields",
    "top_level_output_fields",
    "top_level_schema_freeze_fields",
    "ap6_required_gates",
    "boundary_state_axis",
    "challenge_class_axis",
    "selected_interaction_cells",
    "row_decision_policy",
    "external_state_role_policy",
    "boundary_policy",
    "audit_invariants",
    "old_best_claims_composition",
    "budget_limits",
    "dependency_trace_format",
    "replay_digest_policy",
    "native_requirements_synthesis_contract",
    "hypothesis_decision_rubric",
    "control_requirements",
    "config_file_contracts",
    "schema_validation_contract",
    "fail_closed_error_labels",
    "rows",
    "controls",
    "claim_flags",
    "checks",
    "source_artifacts",
    "source_reports",
    "errors",
    "git",
    "output_digest",
]

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "artifact_level_ap6_supported": False,
    "biological_behavior_claim_allowed": False,
    "final_ap6_supported": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "intention_claim_allowed": False,
    "native_support_opened": False,
    "personhood_claim_allowed": False,
    "phase8_opened": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "selfhood_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "selective_uptake_claim_allowed": False,
    "resource_assimilation_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
}

AP6_REQUIRED_GATES = [
    "source_inventory_accepted",
    "source_artifact_report_digest_for_each_row",
    "direct_historic_ap6_support_status_recorded",
    "old_best_claims_construction_inputs_recorded",
    "boundary_state_axis_lineage_frozen",
    "challenge_class_axis_operational_not_environment_taxonomy",
    "row_schema_has_internal_support_state_descriptor",
    "row_schema_has_external_resource_state_descriptor",
    "row_schema_has_external_perturbation_state_descriptor",
    "row_schema_has_external_structured_state_descriptor",
    "external_state_role_enum_frozen",
    "row_decision_enum_frozen",
    "row_decision_boundary_claim_relation_frozen",
    "boundary_side_assignments_present",
    "boundary_crossing_trace_present",
    "dependency_trace_present",
    "budget_validity_present",
    "replay_digest_scope_frozen",
    "artifact_only_replay_requirement_present",
    "snapshot_load_equivalence_requirement_present",
    "order_inversion_replay_requirement_present",
    "structured_external_coherence_rejection_control_present",
    "b0_c3_active_null_rejects_false_boundary",
    "b2_c0_c1_c2_unlock_required_before_b3_repair",
    "b4_c5_shared_medium_separability_required",
    "externally_supplied_boundary_control_fails_closed",
    "post_hoc_boundary_label_control_fails_closed",
    "hidden_external_state_injection_control_fails_closed",
    "resource_relabel_as_self_control_fails_closed",
    "self_support_relabel_as_external_control_fails_closed",
    "untracked_boundary_crossing_control_fails_closed",
    "identity_acceptance_relabel_control_fails_closed",
    "selfhood_personhood_relabel_control_fails_closed",
    "semantic_goal_ownership_relabel_control_fails_closed",
    "native_support_relabel_control_fails_closed",
    "claim_flags_forced_false",
    "native_support_not_opened",
    "phase8_opened_false",
    "src_diff_empty_true",
]

CONTROL_REQUIREMENTS = [
    {
        "control_id": "externally_supplied_boundary_control",
        "expected_status": "blocked",
        "expected_blocker": "externally_supplied_boundary_blocked",
    },
    {
        "control_id": "post_hoc_boundary_label_control",
        "expected_status": "blocked",
        "expected_blocker": "post_hoc_boundary_label_blocked",
    },
    {
        "control_id": "hidden_external_state_injection_control",
        "expected_status": "blocked",
        "expected_blocker": "hidden_external_state_injection_blocked",
    },
    {
        "control_id": "resource_relabel_as_self_control",
        "expected_status": "blocked",
        "expected_blocker": "resource_relabel_as_self_blocked",
    },
    {
        "control_id": "self_support_relabel_as_external_control",
        "expected_status": "blocked",
        "expected_blocker": "self_support_relabel_as_external_blocked",
    },
    {
        "control_id": "untracked_boundary_crossing_control",
        "expected_status": "blocked",
        "expected_blocker": "untracked_boundary_crossing_blocked",
    },
    {
        "control_id": "structured_external_coherence_rejection_control",
        "expected_status": "blocked_or_rejected",
        "expected_blocker": "structured_external_coherence_false_boundary_blocked",
    },
    {
        "control_id": "multi_basin_merge_control",
        "expected_status": "blocked_or_recorded_failure",
        "expected_blocker": "multi_basin_merge_or_leakage_recorded",
    },
    {
        "control_id": "identity_acceptance_relabel_control",
        "expected_status": "blocked",
        "expected_blocker": "identity_acceptance_relabel_blocked",
    },
    {
        "control_id": "selfhood_personhood_relabel_control",
        "expected_status": "blocked",
        "expected_blocker": "selfhood_personhood_relabel_blocked",
    },
    {
        "control_id": "semantic_goal_ownership_relabel_control",
        "expected_status": "blocked",
        "expected_blocker": "semantic_goal_ownership_relabel_blocked",
    },
    {
        "control_id": "native_support_relabel_control",
        "expected_status": "blocked",
        "expected_blocker": "native_support_relabel_blocked",
    },
    {
        "control_id": "stale_internal_state_control",
        "expected_status": "blocked",
        "expected_blocker": "stale_internal_state_blocked",
    },
    {
        "control_id": "stale_external_state_control",
        "expected_status": "blocked",
        "expected_blocker": "stale_external_state_blocked",
    },
    {
        "control_id": "missing_boundary_side_state_control",
        "expected_status": "blocked",
        "expected_blocker": "missing_boundary_side_state_blocked",
    },
    {
        "control_id": "boundary_drift_outside_policy_control",
        "expected_status": "blocked",
        "expected_blocker": "boundary_drift_outside_policy_blocked",
    },
    {
        "control_id": "artifact_only_replay_control",
        "expected_status": "stable",
        "expected_blocker": "artifact_replay_instability_blocks_ap6",
    },
    {
        "control_id": "snapshot_load_replay_control",
        "expected_status": "stable",
        "expected_blocker": "snapshot_load_instability_blocks_ap6",
    },
    {
        "control_id": "order_inversion_replay_control",
        "expected_status": "stable",
        "expected_blocker": "order_inversion_instability_blocks_ap6",
    },
]

ROW_DECISION_POLICY = {
    "values": ROW_DECISION_VALUES,
    "boundary_claim_allowed_rules": {
        "supported": (
            "does not automatically imply boundary_claim_allowed = true; all "
            "AP6 gates, controls, budget, replay, and claim-boundary checks "
            "must also pass"
        ),
        "partial": "keeps final AP6 provisional unless later synthesis closes missing gates",
        "blocked": "forces boundary_claim_allowed = false",
        "rejected": "forces boundary_claim_allowed = false",
        "not_applicable": "forces boundary_claim_allowed = false",
    },
    "final_ap6_rule": "final AP6 closeout is impossible in Iteration 2",
}

EXTERNAL_STATE_ROLE_POLICY = {
    "values": EXTERNAL_STATE_ROLE_VALUES,
    "c3_default_role": "structured_external_state",
    "c3_perturbation_rule": (
        "C3 becomes perturbation only when crossing or disruption is explicitly "
        "recorded in boundary_crossing_trace or failure_mode"
    ),
}

BOUNDARY_POLICY = {
    "policy_id": "n16_boundary_policy_v1",
    "boundary_state_values": BOUNDARY_STATE_VALUES,
    "challenge_class_values": CHALLENGE_CLASS_VALUES,
    "external_state_role_values": EXTERNAL_STATE_ROLE_VALUES,
    "row_decision_values": ROW_DECISION_VALUES,
    "b3_unlock_rule": (
        "B3 repair/reabsorption rows require prior B2 evaluation under C0, "
        "C1, and C2, or explicit blockers for those cells"
    ),
    "b4_primary_target": "B4 x C5 shared-medium multi-basin separability",
    "b4_c2_rule": (
        "B4 x C2 is a flux stress row and remains partial or not_applicable "
        "unless multi-basin substrate evidence is source-backed"
    ),
    "structured_external_coherence_rule": (
        "C3 is an active null for coherent outside structure and must reject "
        "false self-boundary classification"
    ),
    "boundary_claim_allowed_rule": ROW_DECISION_POLICY[
        "boundary_claim_allowed_rules"
    ],
}

AUDIT_INVARIANTS = [
    {
        "audit_id": "n16_i2_audit_01_freeze_rules_before_evidence",
        "rule": "Freeze rules before evidence.",
        "reason": "prevents post-hoc AP6 interpretation",
        "frozen_contracts": [
            "row_schema_fields",
            "ap6_required_gates",
            "boundary_policy",
            "control_requirements",
            "replay_digest_policy",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_02_require_internal_external_separation",
        "rule": "Require internal/external separation in every future evidence row.",
        "reason": "AP6 is boundary separability, not basin existence",
        "frozen_contracts": [
            "internal_state_descriptor",
            "external_resource_descriptor",
            "external_perturbation_descriptor",
            "external_structured_state_descriptor",
            "external_state_role",
            "boundary_side_assignments",
            "boundary_crossing_trace",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_03_prevent_prior_claim_promotion",
        "rule": "Prevent AP5/AP4/AP3/NAT4 promotion.",
        "reason": "N16 must add new boundary evidence, not relabel prior claims",
        "frozen_contracts": [
            "old_best_claims_composition",
            "claim_ceiling",
            "claim_ceiling_preserved",
            "claim_promotion_allowed",
            "blocked_claims",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_04_c3_structured_external_default",
        "rule": "Treat C3 as structured external state by default.",
        "reason": "coherent outside structure is a false-positive pressure, not a self",
        "frozen_contracts": [
            "external_state_role_policy",
            "challenge_class_axis.C3",
            "structured_external_coherence_rejection_control",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_05_b0_active_null",
        "rule": "Keep B0 as an active null.",
        "reason": "external coherence alone must never become boundary support",
        "frozen_contracts": [
            "boundary_state_axis.B0",
            "selected_interaction_cells.B0_C3",
            "b0_c3_active_null_rejects_false_boundary",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_06_gate_b3_behind_b2",
        "rule": "Gate B3 behind B2 evidence.",
        "reason": "repair/reabsorption must not hide an unsupported persistent boundary",
        "frozen_contracts": [
            "boundary_policy.b3_unlock_rule",
            "b2_c0_c1_c2_unlock_required_before_b3_repair",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_07_keep_b4_provisional",
        "rule": "Keep B4 provisional until N16 produces separability evidence.",
        "reason": "multi-basin shared-medium cases are high-risk for overclaiming",
        "frozen_contracts": [
            "boundary_policy.b4_primary_target",
            "boundary_policy.b4_c2_rule",
            "b4_c5_shared_medium_separability_required",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_08_row_decisions_independent_from_ap6",
        "rule": "Define row decisions independently from AP6 support.",
        "reason": "a supported null/control is not a supported boundary claim",
        "frozen_contracts": [
            "row_decision_policy",
            "boundary_claim_allowed",
            "final_ap6_supported",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_09_distinct_fail_closed_blockers",
        "rule": "Make controls fail closed with distinct blockers.",
        "reason": "blocked relabels must be auditable, not vague",
        "frozen_contracts": [
            "control_requirements",
            "fail_closed_error_labels",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_10_replay_digest_admissibility",
        "rule": "Make replay/digest part of admissibility.",
        "reason": "artifact-level AP6 requires reproducible source-backed evidence",
        "frozen_contracts": [
            "replay_digest_policy",
            "artifact_only_replay_status",
            "snapshot_load_status",
            "order_inversion_replay_status",
            "idempotency_digest_plan",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_11_partial_mvp_synthesis",
        "rule": "Mark MVP synthesis as partial if Iterations 5-6 are deferred.",
        "reason": "useful early result must not become premature closeout",
        "frozen_contracts": [
            "synthesis_mode",
            "included_iterations",
            "deferred_iterations",
            "final_ap6_closeout_allowed",
            "native_requirements_synthesis_contract",
        ],
        "status": "frozen",
    },
    {
        "audit_id": "n16_i2_audit_12_force_unsafe_claim_flags_false",
        "rule": "Force unsafe claim flags false.",
        "reason": "AP6 boundary candidate is not selfhood, agency, native support, or life",
        "frozen_contracts": [
            "claim_flags",
            "blocked_claims",
            "claim_boundary",
        ],
        "status": "frozen",
    },
]

SELECTED_INTERACTION_CELLS = [
    {
        "cell_id": "B0_C3",
        "boundary_state": "B0",
        "challenge_class": "C3",
        "purpose": "structured external coherence active null; must reject false boundary",
    },
    {
        "cell_id": "B1_C2",
        "boundary_state": "B1",
        "challenge_class": "C2",
        "purpose": "weak detectable boundary under directional flux",
    },
    {
        "cell_id": "B2_C1",
        "boundary_state": "B2",
        "challenge_class": "C1",
        "purpose": "persistent boundary under unstructured perturbation",
    },
    {
        "cell_id": "B3_C4",
        "boundary_state": "B3",
        "challenge_class": "C4",
        "purpose": "breach and repair / reclosure probe after B2 unlock",
    },
    {
        "cell_id": "B4_C5",
        "boundary_state": "B4",
        "challenge_class": "C5",
        "purpose": "multi-basin exclusivity in shared medium",
    },
]

OLD_BEST_CLAIMS_COMPOSITION = {
    "operator_id": "n16_trace_preserving_old_best_claims_composition_v1",
    "source_axes": {
        "N15_AP5": "endogenous target/proxy formation substrate",
        "N14_AP4": "route/resource and consequence-sensitive selection context",
        "N13_AP3": "internal support-seeking regulation context",
        "N08": "route memory / shared-medium analog context",
        "N09": "bounded perturbation/recovery context",
        "N12_NAT4": "readiness-only context with zero native-support promotion",
    },
    "rules": [
        "source rows are consumed only at closed claim ceilings",
        "AP5 proxy formation is not AP6 boundary separability",
        "AP6 rows must add internal/external side assignment and crossing trace",
        "N12 readiness cannot contribute native support",
        "constructed N14 followout remains constructed followout",
        "result remains AP6_candidate until matrix rows, controls, replay, and claim classification pass",
    ],
}

BUDGET_LIMITS = {
    "policy_id": "n16_budget_limits_v1",
    "units": [
        "source_row_count",
        "matrix_cell_count",
        "transform_count",
        "canonical_json_input_bytes",
        "canonical_json_output_bytes",
        "replay_count",
        "validation_count",
        "wall_clock_seconds",
    ],
    "limits": {
        "source_row_count": 32,
        "matrix_cell_count": 16,
        "transform_count": 64,
        "canonical_json_input_bytes": 524288,
        "canonical_json_output_bytes": 524288,
        "replay_count": 8,
        "validation_count": 128,
        "wall_clock_seconds": 90,
    },
    "validity_rule": "budget is checked before AP6 row acceptance; missing or exceeded limits fail closed",
}

DEPENDENCY_TRACE_FORMAT = {
    "format_id": "n16_dependency_trace_v1",
    "container": "list",
    "required_fields": [
        "row_field",
        "source_row_id",
        "source_artifact",
        "source_sha256",
        "source_field",
        "transform_id",
        "transform_parameters",
        "claim_ceiling_of_source",
        "boundary_side",
    ],
    "completeness_rule": (
        "every emitted boundary descriptor, side assignment, crossing trace, "
        "metric, decision, and requirement requires at least one source row or "
        "case transform with a preserved claim ceiling"
    ),
}

REPLAY_DIGEST_POLICY = {
    "policy_id": "n16_replay_digest_policy_v1",
    "algorithm": "sha256",
    "encoding": "canonical_json_sorted_keys_ascii",
    "include": [
        "source_artifact_digests",
        "selected_source_rows",
        "boundary_policy",
        "old_best_claim_inputs",
        "runtime_state_vector",
        "internal_state_descriptor",
        "external_resource_descriptor",
        "external_perturbation_descriptor",
        "external_structured_state_descriptor",
        "external_state_role",
        "boundary_side_assignments",
        "boundary_crossing_trace",
        "case_id",
        "cell_id",
        "boundary_state",
        "challenge_class",
        "basin_count",
        "boundary_edges",
        "internal_coherence",
        "external_coherence",
        "coherence_margin",
        "inbound_flux",
        "outbound_flux",
        "retained_flux",
        "leakage_ratio",
        "boundary_stability_score",
        "repair_score",
        "noise_resilience_score",
        "flux_tolerance_score",
        "basin_separation_score",
        "row_decision",
        "budget_cost_surface",
        "dependency_trace",
        "claim_flags",
    ],
    "exclude": [
        "generated_at",
        "local_filesystem_paths",
        "git_working_tree_metadata",
        "wall_clock_timestamps",
    ],
}

NATIVE_REQUIREMENTS_SYNTHESIS_CONTRACT = {
    "synthesis_mode_values": SYNTHESIS_MODE_VALUES,
    "top_level_fields": [
        "synthesis_mode",
        "included_iterations",
        "deferred_iterations",
        "final_ap6_closeout_allowed",
    ],
    "partial_mvp_defaults": {
        "synthesis_mode": "partial_mvp",
        "included_iterations": ["1", "2", "3", "4", "7_partial"],
        "deferred_iterations": ["5", "6", "7_full", "8", "9"],
        "final_ap6_closeout_allowed": False,
    },
    "required_synthesis_fields": [
        "native_boundary_requirements_observed",
        "minimum_coherence_margin",
        "minimum_internal_support",
        "maximum_leakage_ratio",
        "repair_reabsorption_requirement",
        "flux_balance_requirement",
        "structured_external_coherence_rejection_requirement",
        "inter_basin_separation_requirement",
    ],
    "claim_boundary": (
        "requirements synthesis may report satisfied and failed artifact "
        "boundary requirements, but final AP6 requires controls and claim "
        "classification in later iterations"
    ),
}

HYPOTHESIS_DECISION_RUBRIC = {
    "supported": "all required gates validated and associated controls/replays pass",
    "partial": "source coverage or row evidence exists but one or more gates remain open",
    "blocked": "required source, unlock, budget, or replay condition prevents interpretation",
    "rejected": "a required gate fails or a negative control passes without a valid blocker",
    "not_applicable": "cell is intentionally outside the supported source or unlock scope",
}

FAIL_CLOSED_ERROR_LABELS = [
    "source_artifact_missing",
    "sha256_mismatch",
    "stale_internal_state",
    "stale_external_state",
    "missing_boundary_side_state",
    "missing_boundary_crossing_trace",
    "trace_incomplete",
    "budget_exceeded",
    "boundary_drift_outside_policy",
    "control_unexpectedly_passed",
    "unsafe_claim_flag_true",
    "absolute_path_recorded",
    "invalid_external_state_role",
    "invalid_row_decision",
    "boundary_claim_allowed_rule_violation",
    "b3_unlock_missing",
    "b4_shared_medium_evidence_missing",
]

CONFIG_FILE_CONTRACTS = {
    "configs/n16_source_registry.json": {
        "status": "materialized_in_iteration2",
        "required_content": ["portable source paths", "expected sha256 values"],
    },
    "configs/n16_boundary_policy_v1.json": {
        "status": "materialized_in_iteration2",
        "required_content": [
            "BOUNDARY_POLICY",
            "ROW_DECISION_POLICY",
            "AUDIT_INVARIANTS",
            "axis values",
        ],
    },
    "configs/n16_budget_limits_v1.json": {
        "status": "materialized_in_iteration2",
        "required_content": ["BUDGET_LIMITS"],
    },
    "configs/n16_control_variants_v1.json": {
        "status": "materialized_in_iteration2",
        "required_content": ["CONTROL_REQUIREMENTS", "claim flags", "fail-closed labels"],
    },
    "configs/n16_replay_policy_v1.json": {
        "status": "materialized_in_iteration2",
        "required_content": ["REPLAY_DIGEST_POLICY", "DEPENDENCY_TRACE_FORMAT"],
    },
}

CONFIG_REQUIRED_KEYS = {
    "configs/n16_source_registry.json": {
        "source_inventory",
        "source_inventory_report",
        "boundary_state_axis",
        "challenge_class_axis",
        "rows",
        "claim_boundary",
    },
    "configs/n16_boundary_policy_v1.json": {
        "boundary_policy",
        "row_decision_policy",
        "external_state_role_policy",
        "boundary_state_axis",
        "challenge_class_axis",
        "selected_interaction_cells",
        "ap6_required_gates",
        "audit_invariants",
        "old_best_claims_composition",
        "native_requirements_synthesis_contract",
    },
    "configs/n16_budget_limits_v1.json": {
        "budget_limits",
    },
    "configs/n16_control_variants_v1.json": {
        "control_requirements",
        "required_controls",
        "claim_flags_forced_false",
        "fail_closed_error_labels",
    },
    "configs/n16_replay_policy_v1.json": {
        "replay_digest_policy",
        "dependency_trace_format",
        "idempotency_digest_plan",
    },
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
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return value


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
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def artifact_status(artifact: dict[str, Any] | None) -> str | None:
    if artifact is None:
        return None
    if artifact.get("status") is not None:
        return artifact.get("status")
    iteration_result = artifact.get("iteration_result")
    if isinstance(iteration_result, dict):
        if iteration_result.get("boundary_source_inventory_passed") is True:
            return "passed"
        if iteration_result.get("schema_freeze_passed") is True:
            return "passed"
    return None


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": artifact_status(artifact),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
    }


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def contains_absolute_path(value: Any) -> bool:
    local_markers = (
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "/" + "Users" + "/",
        "geometric-" + "reflexive-coherence",
        "arc-" + "of-becoming",
    )
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        ) or any(marker in value for marker in local_markers)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def build_config_payloads(inventory: dict[str, Any]) -> dict[Path, dict[str, Any]]:
    source_registry = {
        "experiment": "N16",
        "config_id": "n16_source_registry",
        "generated_at": GENERATED_AT,
        "source_inventory": source_artifact(INVENTORY_OUTPUT, inventory),
        "source_inventory_report": source_report(INVENTORY_REPORT),
        "boundary_state_axis": inventory["boundary_state_lineage"],
        "challenge_class_axis": inventory["challenge_class_records"],
        "rows": [
            {
                "row_id": row["row_id"],
                "source_experiment": row["source_experiment"],
                "source_artifact": row["source_artifact"],
                "source_sha256": row["source_sha256"],
                "source_report": row["source_report"],
                "source_report_sha256": row["source_report_sha256"],
                "source_role_classification": row["source_role_classification"],
                "evidence_strategy": row["evidence_strategy"],
                "evidence_strategy_class": row["evidence_strategy_class"],
                "direct_historic_support_status": row["direct_historic_support_status"],
                "provisional_ap_level": row["provisional_ap_level"],
                "provisional_claim_ceiling": row["provisional_claim_ceiling"],
                "boundary_state_relevance": row["boundary_state_relevance"],
                "challenge_class_relevance": row["challenge_class_relevance"],
            }
            for row in inventory["rows"]
        ],
        "claim_boundary": {
            "final_ap6_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "artifact_level_ap6_supported": False,
        },
    }
    boundary_policy = {
        "experiment": "N16",
        "config_id": "n16_boundary_policy_v1",
        "generated_at": GENERATED_AT,
        "boundary_policy": BOUNDARY_POLICY,
        "row_decision_policy": ROW_DECISION_POLICY,
        "external_state_role_policy": EXTERNAL_STATE_ROLE_POLICY,
        "boundary_state_axis": inventory["boundary_state_lineage"],
        "challenge_class_axis": inventory["challenge_class_records"],
        "selected_interaction_cells": SELECTED_INTERACTION_CELLS,
        "ap6_required_gates": AP6_REQUIRED_GATES,
        "audit_invariants": AUDIT_INVARIANTS,
        "old_best_claims_composition": OLD_BEST_CLAIMS_COMPOSITION,
        "native_requirements_synthesis_contract": NATIVE_REQUIREMENTS_SYNTHESIS_CONTRACT,
    }
    budget_limits = {
        "experiment": "N16",
        "config_id": "n16_budget_limits_v1",
        "generated_at": GENERATED_AT,
        "budget_limits": BUDGET_LIMITS,
    }
    control_variants = {
        "experiment": "N16",
        "config_id": "n16_control_variants_v1",
        "generated_at": GENERATED_AT,
        "control_requirements": CONTROL_REQUIREMENTS,
        "required_controls": {
            control["control_id"]: "required_before_ap6"
            for control in CONTROL_REQUIREMENTS
        },
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "fail_closed_error_labels": FAIL_CLOSED_ERROR_LABELS,
    }
    replay_policy = {
        "experiment": "N16",
        "config_id": "n16_replay_policy_v1",
        "generated_at": GENERATED_AT,
        "replay_digest_policy": REPLAY_DIGEST_POLICY,
        "dependency_trace_format": DEPENDENCY_TRACE_FORMAT,
        "idempotency_digest_plan": {
            "algorithm": "sha256",
            "encoding": "canonical_json_sorted_keys_ascii",
            "same_inputs_same_digest_required": True,
        },
    }
    return {
        CONFIG_PATHS["source_registry"]: source_registry,
        CONFIG_PATHS["boundary_policy"]: boundary_policy,
        CONFIG_PATHS["budget_limits"]: budget_limits,
        CONFIG_PATHS["control_variants"]: control_variants,
        CONFIG_PATHS["replay_policy"]: replay_policy,
    }


def write_config_files(config_payloads: dict[Path, dict[str, Any]]) -> None:
    CONFIGS.mkdir(parents=True, exist_ok=True)
    for path, payload in config_payloads.items():
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def config_missing_required_keys(relative_path: str) -> list[str]:
    required = CONFIG_REQUIRED_KEYS[relative_path]
    path = EXPERIMENT / relative_path
    if not path.exists():
        return sorted(required)
    payload = load_json(path)
    return sorted(required - set(payload))


def materialized_config_contracts() -> dict[str, dict[str, Any]]:
    contracts: dict[str, dict[str, Any]] = {}
    for relative_path, contract in CONFIG_FILE_CONTRACTS.items():
        path = EXPERIMENT / relative_path
        materialized = path.exists()
        missing_keys = config_missing_required_keys(relative_path)
        contracts[relative_path] = {
            **contract,
            "path": relative_path,
            "materialized": materialized,
            "content_valid": materialized and not missing_keys,
            "missing_required_keys": missing_keys,
            "sha256": digest_file(path) if materialized else None,
        }
    return contracts


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    inventory_rows = inventory["rows"]
    inventory_row_fields = set().union(*(row.keys() for row in inventory_rows))
    inventory_row_ids = {row["row_id"] for row in inventory_rows}
    row_schema_fields = set(ROW_SCHEMA_FIELDS)
    source_registry_payload = load_json(CONFIG_PATHS["source_registry"])
    source_registry_row_ids = {
        row["row_id"] for row in source_registry_payload.get("rows", [])
    }
    config_contracts = materialized_config_contracts()
    c3_record = next(
        row for row in inventory["challenge_class_records"] if row["challenge_class"] == "C3"
    )
    b4_record = next(
        row for row in inventory["boundary_state_lineage"] if row["boundary_state"] == "B4"
    )

    checks = {
        "inventory_source_passed": inventory["iteration_result"][
            "boundary_source_inventory_passed"
        ]
        is True,
        "inventory_acceptance_state_valid": inventory["acceptance_state"]
        == "accepted_boundary_source_inventory_only_no_ap6",
        "direct_historic_ap6_absent": inventory["direct_historic_ap6_support"][
            "direct_historic_support_status"
        ]
        == "absent",
        "row_schema_covers_inventory_rows": inventory_row_fields.issubset(
            row_schema_fields
        ),
        "row_schema_has_common_matrix_fields": all(
            field in row_schema_fields
            for field in [
                "cell_id",
                "boundary_state",
                "challenge_class",
                "internal_state_descriptor",
                "external_state_role",
                "boundary_crossing_trace",
                "boundary_claim_allowed",
                "requirements_satisfied",
                "requirements_failed",
            ]
        ),
        "boundary_state_axis_values_frozen": BOUNDARY_STATE_VALUES
        == [row["boundary_state"] for row in inventory["boundary_state_lineage"]],
        "challenge_class_axis_values_frozen": CHALLENGE_CLASS_VALUES
        == [row["challenge_class"] for row in inventory["challenge_class_records"]],
        "external_state_role_values_frozen": EXTERNAL_STATE_ROLE_POLICY["values"]
        == EXTERNAL_STATE_ROLE_VALUES,
        "row_decision_values_frozen": ROW_DECISION_POLICY["values"]
        == ROW_DECISION_VALUES,
        "row_decision_boundary_claim_rules_frozen": (
            ROW_DECISION_POLICY["boundary_claim_allowed_rules"]["blocked"]
            == "forces boundary_claim_allowed = false"
            and ROW_DECISION_POLICY["boundary_claim_allowed_rules"]["rejected"]
            == "forces boundary_claim_allowed = false"
            and ROW_DECISION_POLICY["boundary_claim_allowed_rules"]["not_applicable"]
            == "forces boundary_claim_allowed = false"
        ),
        "synthesis_mode_fields_frozen": all(
            field in TOP_LEVEL_OUTPUT_FIELDS
            for field in [
                "synthesis_mode",
                "included_iterations",
                "deferred_iterations",
                "final_ap6_closeout_allowed",
            ]
        )
        and set(NATIVE_REQUIREMENTS_SYNTHESIS_CONTRACT["synthesis_mode_values"])
        == {"partial_mvp", "full"},
        "c3_structured_external_not_perturbation_by_default": c3_record[
            "external_state_role"
        ]
        == "structured_external_state"
        and c3_record["perturbation_by_default"] is False,
        "b3_unlock_rule_frozen": "B3 repair/reabsorption rows require prior B2"
        in BOUNDARY_POLICY["b3_unlock_rule"],
        "b4_shared_medium_target_frozen": BOUNDARY_POLICY["b4_primary_target"]
        == "B4 x C5 shared-medium multi-basin separability"
        and any(
            "B4 x C5" in requirement
            for requirement in b4_record["required_N16_evidence"]
        ),
        "audit_invariants_recorded": len(AUDIT_INVARIANTS) == 12
        and all(item["status"] == "frozen" for item in AUDIT_INVARIANTS),
        "audit_invariants_cover_user_list": {
            item["audit_id"] for item in AUDIT_INVARIANTS
        }
        == {
            "n16_i2_audit_01_freeze_rules_before_evidence",
            "n16_i2_audit_02_require_internal_external_separation",
            "n16_i2_audit_03_prevent_prior_claim_promotion",
            "n16_i2_audit_04_c3_structured_external_default",
            "n16_i2_audit_05_b0_active_null",
            "n16_i2_audit_06_gate_b3_behind_b2",
            "n16_i2_audit_07_keep_b4_provisional",
            "n16_i2_audit_08_row_decisions_independent_from_ap6",
            "n16_i2_audit_09_distinct_fail_closed_blockers",
            "n16_i2_audit_10_replay_digest_admissibility",
            "n16_i2_audit_11_partial_mvp_synthesis",
            "n16_i2_audit_12_force_unsafe_claim_flags_false",
        },
        "ap6_gate_contains_hidden_external_injection_control": (
            "hidden_external_state_injection_control_fails_closed"
            in AP6_REQUIRED_GATES
        ),
        "ap6_gate_contains_structured_external_rejection": (
            "structured_external_coherence_rejection_control_present"
            in AP6_REQUIRED_GATES
        ),
        "ap6_gate_contains_b3_unlock": (
            "b2_c0_c1_c2_unlock_required_before_b3_repair" in AP6_REQUIRED_GATES
        ),
        "ap6_gate_contains_b4_c5_shared_medium": (
            "b4_c5_shared_medium_separability_required" in AP6_REQUIRED_GATES
        ),
        "budget_units_and_limits_frozen": set(BUDGET_LIMITS["units"])
        == set(BUDGET_LIMITS["limits"]),
        "dependency_trace_format_frozen": DEPENDENCY_TRACE_FORMAT[
            "required_fields"
        ][0]
        == "row_field",
        "replay_digest_policy_frozen": REPLAY_DIGEST_POLICY["algorithm"] == "sha256",
        "control_requirements_count_matches_expected": len(CONTROL_REQUIREMENTS) == 19,
        "config_file_contracts_materialized": all(
            (EXPERIMENT / relative_path).exists()
            for relative_path in CONFIG_FILE_CONTRACTS
        ),
        "config_file_contracts_content_valid": all(
            contract["content_valid"] for contract in config_contracts.values()
        ),
        "schema_validator_script_present": VALIDATOR_SCRIPT.exists(),
        "source_registry_row_count_matches_inventory": len(
            source_registry_payload["rows"]
        )
        == len(inventory_rows),
        "source_registry_row_ids_match_inventory": source_registry_row_ids
        == inventory_row_ids,
        "top_level_runtime_output_shape_frozen": TOP_LEVEL_OUTPUT_FIELDS
        == [
            "experiment",
            "iteration",
            "artifact_id",
            "purpose",
            "schema_version",
            "generated_at",
            "command",
            "status",
            "acceptance_state",
            "synthesis_mode",
            "included_iterations",
            "deferred_iterations",
            "final_ap6_closeout_allowed",
            "source_artifacts",
            "source_reports",
            "rows",
            "controls",
            "checks",
            "claim_flags",
            "errors",
            "output_digest",
        ],
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "phase8_opened_false": inventory["iteration_result"]["phase8_opened"]
        is False,
        "native_support_not_opened": inventory["iteration_result"][
            "native_support_opened"
        ]
        is False,
        "no_final_ap6_assigned": inventory["iteration_result"][
            "final_ap6_supported"
        ]
        is False,
        "src_diff_empty": git_status_short("src") == "",
    }

    schema_summary = {
        "row_schema_field_count": len(ROW_SCHEMA_FIELDS),
        "ap6_required_gate_count": len(AP6_REQUIRED_GATES),
        "control_requirement_count": len(CONTROL_REQUIREMENTS),
        "materialized_config_file_count": len(CONFIG_FILE_CONTRACTS),
        "boundary_state_count": len(BOUNDARY_STATE_VALUES),
        "challenge_class_count": len(CHALLENGE_CLASS_VALUES),
        "fail_closed_error_label_count": len(FAIL_CLOSED_ERROR_LABELS),
        "audit_invariant_count": len(AUDIT_INVARIANTS),
        "final_ap6_rows": 0,
    }
    acceptance_state = (
        "accepted_boundary_schema_freeze_no_row_validation"
        if all(checks.values())
        else "rejected_boundary_schema_freeze"
    )
    output: dict[str, Any] = {
        "experiment": "N16",
        "iteration": 2,
        "artifact_id": "n16_boundary_schema_v1",
        "purpose": "boundary_schema_and_ap6_gate",
        "schema_version": "n16_boundary_schema_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP6",
        "synthesis_mode": "partial_mvp",
        "included_iterations": ["1", "2"],
        "deferred_iterations": [
            "3",
            "4",
            "5",
            "6",
            "7_partial",
            "7_full",
            "8",
            "9",
        ],
        "final_ap6_closeout_allowed": False,
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "schema_freeze_passed": all(checks.values()),
            "row_validation_started": False,
            "matrix_rows_generated": False,
            "final_ap6_supported": False,
            "artifact_level_ap6_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "selfhood_claim_opened": False,
            "semantic_goal_ownership_opened": False,
            "agency_claim_opened": False,
        },
        "schema_summary": schema_summary,
        "ap_ladder": AP_LADDER,
        "row_schema_fields": ROW_SCHEMA_FIELDS,
        "top_level_output_fields": TOP_LEVEL_OUTPUT_FIELDS,
        "top_level_schema_freeze_fields": TOP_LEVEL_SCHEMA_FREEZE_FIELDS,
        "ap6_required_gates": AP6_REQUIRED_GATES,
        "boundary_state_axis": inventory["boundary_state_lineage"],
        "challenge_class_axis": inventory["challenge_class_records"],
        "selected_interaction_cells": SELECTED_INTERACTION_CELLS,
        "row_decision_policy": ROW_DECISION_POLICY,
        "external_state_role_policy": EXTERNAL_STATE_ROLE_POLICY,
        "boundary_policy": BOUNDARY_POLICY,
        "audit_invariants": AUDIT_INVARIANTS,
        "old_best_claims_composition": OLD_BEST_CLAIMS_COMPOSITION,
        "budget_limits": BUDGET_LIMITS,
        "dependency_trace_format": DEPENDENCY_TRACE_FORMAT,
        "replay_digest_policy": REPLAY_DIGEST_POLICY,
        "native_requirements_synthesis_contract": NATIVE_REQUIREMENTS_SYNTHESIS_CONTRACT,
        "hypothesis_decision_rubric": HYPOTHESIS_DECISION_RUBRIC,
        "control_requirements": CONTROL_REQUIREMENTS,
        "config_file_contracts": config_contracts,
        "schema_validation_contract": {
            "validator_kind": "project_local_python_validator",
            "validator_script": rel(VALIDATOR_SCRIPT),
            "required_checks": [
                "required_fields_present",
                "enum_values_valid",
                "c3_external_state_role",
                "b3_unlock_rule",
                "b4_provisional_rule",
                "row_decision_boundary_claim_relation",
                "claim_ceiling_preservation",
                "boundary_crossing_trace_presence",
                "budget_validity",
                "dependency_trace_format",
                "claim_flags_forced_false",
                "control_outcomes_present",
                "source_digest_presence",
                "digest_reproducibility",
                "absolute_path_absence",
            ],
        },
        "fail_closed_error_labels": FAIL_CLOSED_ERROR_LABELS,
        "rows": [],
        "controls": {
            control["control_id"]: "required_before_ap6"
            for control in CONTROL_REQUIREMENTS
        },
        "claim_flags": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory)
        },
        "source_reports": {rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT)},
        "errors": [],
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["checks"]["top_level_schema_freeze_shape_matches_output"] = set(
        TOP_LEVEL_SCHEMA_FREEZE_FIELDS
    ) == set(output) | {"output_digest"}
    output["checks"]["no_absolute_paths_recorded"] = not contains_absolute_path(output)
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "accepted_boundary_schema_freeze_no_row_validation"
        if all(output["checks"].values())
        else "rejected_boundary_schema_freeze"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["schema_freeze_passed"] = output["status"] == "passed"
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N16 Boundary Schema And AP6 Gate",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(output["schema_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 2 freezes the N16 common matrix row schema, AP6 gate,",
        "B0-B4 boundary-state axis, C0-C5 operational challenge-class axis,",
        "external-state role enum, row-decision policy, boundary policy,",
        "budget limits, dependency trace format, replay digest scope, controls,",
        "config-file contracts, output shape, and fail-closed error labels.",
        "It materializes the planned configs and links the local validator.",
        "It does not generate matrix rows, run boundary cases, or assign final `AP6`.",
        "",
        "## Top-Level Contracts",
        "",
        "Runtime row outputs must include these fields:",
        "",
        "```json",
        json.dumps(output["top_level_output_fields"], indent=2),
        "```",
        "",
        "The Iteration 2 schema-freeze artifact includes these fields:",
        "",
        "```json",
        json.dumps(output["top_level_schema_freeze_fields"], indent=2),
        "```",
        "",
        "## Row Decision Policy",
        "",
        "```json",
        json.dumps(output["row_decision_policy"], indent=2, sort_keys=True),
        "```",
        "",
        "## External State Role Policy",
        "",
        "```json",
        json.dumps(output["external_state_role_policy"], indent=2, sort_keys=True),
        "```",
        "",
        "## AP6 Gate",
        "",
        "| Gate |",
        "| --- |",
    ]
    for gate in output["ap6_required_gates"]:
        lines.append(f"| `{gate}` |")
    lines.extend(
        [
            "",
            "## Boundary State Axis",
            "",
            "| State | Name | Claim ceiling | Required N16 evidence |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in output["boundary_state_axis"]:
        lines.append(
            "| "
            f"`{row['boundary_state']}` | {row['name']} | "
            f"`{row['claim_ceiling']}` | {row['required_N16_evidence']} |"
        )
    lines.extend(
        [
            "",
            "## Challenge Class Axis",
            "",
            "| Class | Name | External role | Claim boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in output["challenge_class_axis"]:
        lines.append(
            "| "
            f"`{row['challenge_class']}` | {row['name']} | "
            f"`{row.get('external_state_role', 'not_applicable')}` | "
            f"`{row['claim_boundary']}` |"
        )
    lines.extend(
        [
            "",
            "## Selected Interaction Cells",
            "",
            "| Cell | Boundary state | Challenge class | Purpose |",
            "| --- | --- | --- | --- |",
        ]
    )
    for cell in output["selected_interaction_cells"]:
        lines.append(
            "| "
            f"`{cell['cell_id']}` | `{cell['boundary_state']}` | "
            f"`{cell['challenge_class']}` | {cell['purpose']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary Policy",
            "",
            "```json",
            json.dumps(output["boundary_policy"], indent=2, sort_keys=True),
            "```",
            "",
            "## Old-Best Claims Composition",
            "",
            "```json",
            json.dumps(
                output["old_best_claims_composition"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Audit Invariants",
            "",
            "| Invariant | Rule | Frozen contracts |",
            "| --- | --- | --- |",
        ]
    )
    for invariant in output["audit_invariants"]:
        contracts = ", ".join(f"`{item}`" for item in invariant["frozen_contracts"])
        lines.append(
            "| "
            f"`{invariant['audit_id']}` | {invariant['rule']} "
            f"Reason: {invariant['reason']}. | {contracts} |"
        )
    lines.extend(
        [
            "",
            "## Budget And Replay",
            "",
            "```json",
            json.dumps(
                {
                    "budget_limits": output["budget_limits"],
                    "dependency_trace_format": output["dependency_trace_format"],
                    "replay_digest_policy": output["replay_digest_policy"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Controls",
            "",
            "| Control | Expected status | Blocker |",
            "| --- | --- | --- |",
        ]
    )
    for control in output["control_requirements"]:
        lines.append(
            "| "
            f"`{control['control_id']}` | "
            f"`{control['expected_status']}` | "
            f"`{control['expected_blocker']}` |"
        )
    lines.extend(
        [
            "",
            "## Hypothesis Decision Rubric",
            "",
            "| Decision | Meaning |",
            "| --- | --- |",
        ]
    )
    for decision, meaning in output["hypothesis_decision_rubric"].items():
        lines.append(f"| `{decision}` | {meaning} |")
    lines.extend(
        [
            "",
            "## Fail-Closed Error Labels",
            "",
            "```json",
            json.dumps(output["fail_closed_error_labels"], indent=2),
            "```",
            "",
            "## Native Requirements Synthesis Contract",
            "",
            "```json",
            json.dumps(
                output["native_requirements_synthesis_contract"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Materialized Config Files",
            "",
            "| Config | Content valid | SHA-256 |",
            "| --- | --- | --- |",
        ]
    )
    for path, contract in output["config_file_contracts"].items():
        lines.append(
            f"| `{path}` | `{contract['content_valid']}` | "
            f"`{contract['sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Schema Validator",
            "",
            "```json",
            json.dumps(output["schema_validation_contract"], indent=2, sort_keys=True),
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
            "schema freeze != AP6 support",
            "row schema != boundary demonstration",
            "B/C axes != inherited environment taxonomy",
            "AP5 proxy formation != AP6 boundary separability",
            "external structured coherence != perturbation unless crossing/disruption is recorded",
            "N13 AP3 input != selfhood",
            "N14 AP4 input != intention or goal ownership",
            "N12 readiness-only context != native support",
            "N16 Iteration 2 != selective uptake or resource assimilation",
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
    write_config_files(build_config_payloads(load_json(INVENTORY_OUTPUT)))
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
