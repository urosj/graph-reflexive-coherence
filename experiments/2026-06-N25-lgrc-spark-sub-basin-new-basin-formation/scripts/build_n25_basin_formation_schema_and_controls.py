#!/usr/bin/env python3
"""Build N25 Iteration 2 basin-formation schema/control freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_basin_formation_schema_and_controls.json"
REPORT = EXPERIMENT / "reports" / "n25_basin_formation_schema_and_controls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_basin_formation_schema_and_controls.py"
)
I1_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_source_handoff_inventory.json"
)

LANE_VALUES = ["native", "producer_assisted"]
PRODUCER_ASSISTED_RESULT_CLASS_VALUES = [
    "not_applicable",
    "producer_mediated_scaffold_candidate",
    "missing_native_mechanism_probe",
]
FORMATION_CLASS_VALUES = [
    "bifurcation_partial",
    "reinforced_old_basin",
    "reshaped_old_boundary",
    "sub_basin_candidate",
    "new_basin_candidate",
    "transient_fluctuation",
    "merge_leakage_artifact",
    "producer_assisted_scaffold",
]
FORMATION_SOURCE_VALUES = [
    "native_source_current_bifurcation",
    "native_old_basin_thickening",
    "native_merge_leakage",
    "producer_flux_conditioned",
    "hidden_producer_insertion",
    "label_only",
    "report_derived",
]
NATIVE_FLUX_DEBT_STATUS_VALUES = [
    "preserved",
    "violated_blocks_native_row",
    "not_applicable_producer_lane",
]
ROW_DECISION_VALUES = ["supported", "partial", "blocked", "rejected", "not_applicable"]
REPLAY_CONTROL_STATUS_VALUES = [
    "passed",
    "failed_closed",
    "failed_open",
    "not_run",
    "not_applicable",
]
AP4_DEPENDENCY_STATUS_VALUES = ["required_recorded", "not_applicable", "missing_blocks_row"]
AP5_DEPENDENCY_STATUS_VALUES = [
    "conditional_required_recorded",
    "not_applicable",
    "missing_blocks_row",
]
ARTIFACT_ROLE_VALUES = [
    "bifurcation_trace",
    "new_boundary_candidate_trace",
    "new_basin_support_coherence_trace",
    "replayable_distinction_trace",
    "old_basin_relation_trace",
    "merge_leakage_trace",
    "native_flux_debt_trace",
    "producer_intervention_ledger",
    "formation_replay_trace",
    "stress_boundary_trace",
    "negative_control_trace",
    "runtime_trace",
    "threshold_record",
    "active_null_trace",
    "closeout",
    "source_handoff",
    "schema_control_freeze",
    "source_contract",
    "inherited_context",
    "report",
]
POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES = [
    "report",
    "inherited_context",
    "source_contract",
]
BF_LADDER = {
    "BF0": "no source-current basin-formation evidence",
    "BF1": "run artifact with becoming-pressure / N24 optionality context",
    "BF2": "bifurcation or spark trace observed, but distinguishable basin not yet stable",
    "BF3": "source-current distinguishable sub-basin boundary/support candidate",
    "BF4": "replay/control-backed sub-basin differentiation candidate",
    "BF5": "stress/threshold-backed new-basin formation candidate with merge/leakage controls clean",
    "BF6": "N26-ready bounded basin-formation evidence",
}
N25_CLOSEOUT_LADDER = {
    "N25-C0": "contract-only closeout",
    "N25-C1": "active-null/control discipline established",
    "N25-C2": "spark/bifurcation partial",
    "N25-C3": "source-current sub-basin candidate",
    "N25-C4": "replay/control-backed sub-basin differentiation candidate",
    "N25-C5": "stress/threshold-backed basin-formation candidate",
    "N25-C6": "N26-ready bounded basin-formation evidence",
}
CONTROL_IDS = [
    "label_only_new_basin_rejected",
    "single_basin_thickening_relabel_rejected",
    "reshaped_old_boundary_relabel_rejected",
    "merge_leakage_masquerading_as_new_basin_rejected",
    "non_replayable_transient_rejected",
    "hidden_producer_insertion_rejected",
    "n24_optionality_relabel_as_formation_rejected",
    "producer_assisted_success_does_not_overwrite_native_failure",
    "native_flux_debt_remains_row_local",
    "producer_schedule_post_hoc_control",
    "producer_hidden_support_control",
    "producer_threshold_relaxation_control",
    "producer_basin_insertion_without_trace_control",
    "producer_success_as_native_relabel_control",
    "producer_success_overwrites_native_failure_control",
    "native_spark_source_policy_rejected",
    "producer_before_native_spark_path_rejected",
    "ap4_gap_prose_only_rejected",
    "ap5_proxy_target_omission_rejected_when_applicable",
    "semantic_learning_relabel_rejected",
    "semantic_choice_relabel_rejected",
    "agency_relabel_rejected",
    "native_support_relabel_rejected",
    "phase8_relabel_rejected",
    "ant_ecology_relabel_rejected",
]
CONTROL_ALIAS_MAP = {
    "label_only_new_basin_control": "label_only_new_basin_rejected",
    "hidden_producer_insertion_control": "hidden_producer_insertion_rejected",
    "hidden_producer_support_control": "producer_hidden_support_control",
    "semantic_relabel_control": [
        "semantic_choice_relabel_rejected",
        "semantic_learning_relabel_rejected",
    ],
    "native_support_relabel_control": "native_support_relabel_rejected",
    "phase8_relabel_control": "phase8_relabel_rejected",
}
UNSAFE_CLAIMS = [
    "agency",
    "ant_ecology_implementation",
    "consciousness",
    "free_will",
    "fully_native_integration",
    "identity_acceptance",
    "native_ant_agency",
    "native_colony_agency",
    "native_support",
    "organism_life",
    "phase8_implementation",
    "reward_maximization",
    "selfhood",
    "semantic_action",
    "semantic_choice",
    "semantic_goal",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_learning",
    "semantic_perception",
    "sentience",
    "ant_ecology_specification",
    "unrestricted_autonomy",
]
CANDIDATE_EVIDENCE_FIELDS = [
    "row_id",
    "source_iteration",
    "source_contract_row_digest",
    "source_consumable_contract_row_digest",
    "source_output_digest",
    "run_artifact_id",
    "runtime_config_digest",
    "source_commit_or_source_digest",
    "source_current_inputs",
    "artifact_manifest",
    "artifact_paths",
    "artifact_sha256",
    "artifact_paths_equal_manifest_paths",
    "artifact_sha256_equal_manifest_sha256",
    "all_artifact_sha256_match_file_contents",
    "row_digest",
    "output_digest",
    "row_specific_thresholds_declared_before_use",
    "existing_lgrc_spark_sources_considered",
    "native_spark_mechanism_reuse_status",
    "new_producer_code_justification",
    "lane",
    "lane_success_can_upgrade_native",
    "native_lane_failure_overwritten",
    "producer_assisted_result_class",
    "n20_source_contract_row",
    "n20_consumable_contract_row",
    "n24_native_lane_status",
    "n24_producer_lane_status",
    "formation_class",
    "formation_source",
    "bifurcation_trace",
    "new_boundary_candidate_trace",
    "new_basin_support_coherence_trace",
    "replayable_distinction_trace",
    "old_basin_relation_trace",
    "merge_leakage_trace",
    "formation_window",
    "bifurcation_window",
    "boundary_candidate_window",
    "replay_window",
    "old_basin_reference_window",
    "bifurcation_window_order_valid",
    "thresholds_declared_before_bifurcation_window",
    "old_basin_signature_digest",
    "candidate_basin_signature_digest",
    "candidate_boundary_signature_digest",
    "old_to_candidate_separation_digest",
    "boundary_distinguishability_margin",
    "support_floor_margin_new_region",
    "coherence_floor_margin_new_region",
    "old_basin_separation_margin",
    "merge_leakage_margin",
    "replay_distinction_persistence_ratio",
    "old_basin_thickening_rejected",
    "reshaped_old_boundary_rejected",
    "merge_leakage_rejected",
    "transient_rejected",
    "label_only_rejected",
    "native_flux_debt_bound",
    "native_flux_debt_widened",
    "native_flux_debt_status",
    "producer_flux_window_bound",
    "producer_flux_window_declared_before_use",
    "native_flux_debt_not_overwritten",
    "support_floor_result",
    "coherence_floor_result",
    "boundary_integrity_result",
    "flux_or_leakage_result",
    "control_results",
    "producer_residue_classification",
    "naturalization_debt",
    "ap4_dependency_status",
    "ap5_dependency_status",
    "ap4_condition_reason",
    "ap5_condition_reason",
    "bf_ladder_rung",
    "row_decision",
    "basin_formation_claim_allowed",
    "claim_ceiling",
    "n25_closeout_ceiling",
    "n25_closeout_ladder_rung_assigned",
    "unsafe_claim_flags",
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


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i1_status = {
        "path": I1_OUTPUT_PATH,
        "sha256": sha256_file(I1_OUTPUT_PATH),
        "status": i1.get("status", "not_recorded"),
        "acceptance_state": i1.get("acceptance_state", "not_recorded"),
        "output_digest": i1.get("output_digest", "not_recorded"),
    }
    candidate_schema = {
        "required_fields": CANDIDATE_EVIDENCE_FIELDS,
        "lane_values": LANE_VALUES,
        "row_decision_values": ROW_DECISION_VALUES,
        "replay_control_status_values": REPLAY_CONTROL_STATUS_VALUES,
        "artifact_role_values": ARTIFACT_ROLE_VALUES,
        "positive_support_forbidden_if_only_roles": POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES,
        "producer_assisted_result_class_values": PRODUCER_ASSISTED_RESULT_CLASS_VALUES,
        "formation_class_values": FORMATION_CLASS_VALUES,
        "formation_source_values": FORMATION_SOURCE_VALUES,
        "native_flux_debt_status_values": NATIVE_FLUX_DEBT_STATUS_VALUES,
        "ap4_dependency_status_values": AP4_DEPENDENCY_STATUS_VALUES,
        "ap5_dependency_status_values": AP5_DEPENDENCY_STATUS_VALUES,
    }
    lane_ceiling_policy = {
        "required_fields": [
            "lane",
            "lane_success_can_upgrade_native",
            "native_lane_failure_overwritten",
            "producer_assisted_result_class",
        ],
        "native_lane": {
            "may_support_native_bf_rungs_if_all_gates_pass": True,
            "must_preserve_native_flux_debt": True,
            "native_flux_debt_bound": 1e-9,
        },
        "producer_assisted_lane": {
            "may_support_producer_assisted_bf_candidate": True,
            "may_identify_naturalization_target": True,
            "can_upgrade_native_bf": False,
            "can_upgrade_n24_native_lane": False,
            "can_support_native_support": False,
            "can_open_phase8": False,
        },
    }
    lane_cross_field_invariants = {
        "native": {
            "formation_source_required": "native_source_current_bifurcation",
            "producer_assisted_result_class_required": "not_applicable",
            "n24_producer_lane_status_required": "not_used_in_native_row",
            "lane_success_can_upgrade_native_required": False,
            "native_lane_failure_overwritten_required": False,
            "native_flux_debt_bound_required": 1e-9,
            "native_flux_debt_widened_required": False,
            "native_flux_debt_status_required": "preserved",
        },
        "producer_assisted": {
            "formation_source_required": "producer_flux_conditioned",
            "producer_assisted_result_class_allowed": [
                "producer_mediated_scaffold_candidate",
                "missing_native_mechanism_probe",
            ],
            "lane_success_can_upgrade_native_required": False,
            "native_lane_failure_overwritten_required": False,
            "native_flux_debt_not_overwritten_required": True,
        },
    }
    formation_definitions = {
        "bifurcation_partial": {
            "spark_or_bifurcation_trace_observed": True,
            "distinguishable_basin_not_yet_stable": True,
            "bf_ceiling": "BF2",
        },
        "sub_basin_candidate": {
            "boundary_distinguishable_region": "inside_or_attached_to_old_basin",
            "old_basin_relation_required": True,
            "support_coherence_floor_distinct_from_local_thickening": True,
        },
        "new_basin_candidate": {
            "boundary_distinguishable_region_with_replayable_floor": True,
            "not_reducible_to_old_basin_thickening": True,
            "merge_leakage_controls_clean": True,
            "stress_threshold_persistence_required": True,
        },
    }
    native_flux_debt_policy = {
        "native_rows": {
            "native_flux_debt_bound": 1e-9,
            "native_flux_debt_widened_required_value": False,
            "native_flux_debt_status_allowed_values": NATIVE_FLUX_DEBT_STATUS_VALUES,
            "native_flux_debt_violation_effect": "blocks_native_row",
        },
        "producer_assisted_rows": {
            "producer_flux_window_bound_required": True,
            "producer_flux_window_declared_before_use_required": True,
            "native_flux_debt_not_overwritten_required": True,
            "producer_conditioned_flux_bound_max": 1e-8,
            "max_conditioning_windows": 10,
            "producer_threshold_relaxation_rejected_required": True,
        },
    }
    native_spark_source_policy = {
        "existing_lgrc_spark_behavior_expected": True,
        "existing_examples_must_be_considered_before_new_producer_code": True,
        "source_examples": [
            "examples/lgrc9v3/README.md",
            "examples/lgrc9v3/causal_spark_diagnostics.py",
            "examples/lgrc9v3/refinement_packet_transport.py",
        ],
        "native_probe_order": [
            "reuse_existing_lgrc9v3_causal_spark_diagnostics",
            "reuse_existing_grc9v3_lane_b_spark_or_refinement_transport_where_applicable",
            "add_producer_extension_only_if_native_sources_are_insufficient",
        ],
        "new_producer_code_policy": {
            "allowed_only_if_needed": True,
            "must_declare_why_existing_native_spark_path_is_insufficient": True,
            "must_record_naturalization_debt": True,
            "must_not_insert_new_basin_without_source_current_trace": True,
        },
    }
    control_status_policy = {
        "active_null_rows": {
            "expected_status": "failed_closed",
            "meaning": "blocker triggered and the false-positive claim was rejected",
        },
        "positive_candidate_rows": {
            "blocker_absent_status": "passed",
            "failed_closed_role": "may satisfy a negative-control row, not automatically a positive row",
            "failed_open_effect": "blocks row and closeout upgrade",
            "not_run_effect": "blocks dependent rung",
            "not_applicable_requirement": "scope reason required",
        },
    }
    control_result_schema = {
        "required_fields": [
            "control_id",
            "control_status",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "claim_allowed_when_control_triggers",
            "rung_effect",
        ],
        "positive_candidate_rows_require_full_list": True,
        "active_null_rows_may_carry_single_control_status_summary": True,
    }
    active_null_sentinel_policy = {
        "sentinel_values_allowed_only_when": {
            "schema_instantiation_only": True,
            "positive_evidence_admissible": False,
        },
        "positive_row_boolean_fields": [
            "all_artifact_sha256_match_file_contents",
            "artifact_paths_equal_manifest_paths",
            "artifact_sha256_equal_manifest_sha256",
        ],
        "positive_rows_must_use_strict_booleans": True,
    }
    temporal_window_policy = {
        "required_fields": [
            "formation_window",
            "bifurcation_window",
            "boundary_candidate_window",
            "replay_window",
            "old_basin_reference_window",
        ],
        "ordering_rule": "bifurcation_window.end_step <= boundary_candidate_window.start_step",
        "threshold_rule": "thresholds_declared_before_bifurcation_window",
    }
    basin_digest_policy = {
        "bf3_plus_required_digests": [
            "old_basin_signature_digest",
            "candidate_basin_signature_digest",
            "candidate_boundary_signature_digest",
            "old_to_candidate_separation_digest",
        ]
    }
    rung_policy = {
        "BF3_requires": [
            "formation_source is native_source_current_bifurcation for native rows",
            "formation_source is producer_flux_conditioned for producer-assisted rows",
            "boundary_distinguishability_margin recorded",
            "support/coherence floor margins recorded",
            "old-basin thickening, label-only, merge/leakage, and transient controls rejected",
        ],
        "BF4_requires": ["BF3 gates", "replay/control-backed distinction"],
        "BF5_requires": ["BF4 gates", "stress/threshold matrix", "merge/leakage controls clean"],
        "BF6_requires": ["BF5 gates", "N26 handoff ready", "claim boundary clean"],
    }
    controls = [
        {
            "control_id": control_id,
            "active_null_expected_status": "failed_closed",
            "positive_row_blocker_absent_status": "passed",
            "failed_closed_role": "negative_control_satisfied_not_positive_row_success",
            "not_run_effect": "blocks_dependent_rung",
            "not_applicable_requires_scope_reason": True,
            "failed_open_effect": "blocks_row_and_closeout_upgrade",
        }
        for control_id in CONTROL_IDS
    ]
    checks = [
        check("i1_inventory_passed", i1.get("status") == "passed", i1_status),
        check(
            "candidate_schema_has_all_required_fields",
            all(field in candidate_schema["required_fields"] for field in CANDIDATE_EVIDENCE_FIELDS),
            CANDIDATE_EVIDENCE_FIELDS,
        ),
        check("lane_enum_frozen", candidate_schema["lane_values"] == LANE_VALUES, LANE_VALUES),
        check(
            "lane_ceilings_frozen",
            lane_ceiling_policy["producer_assisted_lane"]["can_upgrade_native_bf"] is False
            and lane_ceiling_policy["producer_assisted_lane"]["can_upgrade_n24_native_lane"] is False,
            lane_ceiling_policy,
        ),
        check(
            "formation_class_and_source_frozen",
            "sub_basin_candidate" in FORMATION_CLASS_VALUES
            and "bifurcation_partial" in FORMATION_CLASS_VALUES
            and "new_basin_candidate" in FORMATION_CLASS_VALUES
            and "native_source_current_bifurcation" in FORMATION_SOURCE_VALUES
            and "producer_flux_conditioned" in FORMATION_SOURCE_VALUES,
            {"formation_class": FORMATION_CLASS_VALUES, "formation_source": FORMATION_SOURCE_VALUES},
        ),
        check(
            "distinguishability_metrics_required",
            all(
                field in CANDIDATE_EVIDENCE_FIELDS
                for field in [
                    "boundary_distinguishability_margin",
                    "support_floor_margin_new_region",
                    "coherence_floor_margin_new_region",
                    "old_basin_separation_margin",
                    "merge_leakage_margin",
                    "replay_distinction_persistence_ratio",
                ]
            ),
            "BF3+ distinguishability metrics are required candidate fields.",
        ),
        check(
            "native_flux_debt_policy_frozen",
            native_flux_debt_policy["native_rows"]["native_flux_debt_bound"] == 1e-9
            and native_flux_debt_policy["native_rows"]["native_flux_debt_widened_required_value"] is False,
            native_flux_debt_policy,
        ),
        check(
            "native_spark_source_policy_frozen",
            native_spark_source_policy["existing_lgrc_spark_behavior_expected"] is True
            and native_spark_source_policy["existing_examples_must_be_considered_before_new_producer_code"] is True,
            native_spark_source_policy,
        ),
        check(
            "producer_flux_bounds_frozen",
            native_flux_debt_policy["producer_assisted_rows"]["producer_conditioned_flux_bound_max"] == 1e-8
            and native_flux_debt_policy["producer_assisted_rows"]["max_conditioning_windows"] == 10,
            native_flux_debt_policy["producer_assisted_rows"],
        ),
        check(
            "artifact_roles_frozen",
            all(
                role in ARTIFACT_ROLE_VALUES
                for role in [
                    "bifurcation_trace",
                    "new_boundary_candidate_trace",
                    "new_basin_support_coherence_trace",
                    "replayable_distinction_trace",
                    "native_flux_debt_trace",
                    "producer_intervention_ledger",
                    "runtime_trace",
                    "threshold_record",
                    "active_null_trace",
                ]
            ),
            ARTIFACT_ROLE_VALUES,
        ),
        check(
            "control_status_semantics_frozen",
            control_status_policy["active_null_rows"]["expected_status"] == "failed_closed"
            and control_status_policy["positive_candidate_rows"]["blocker_absent_status"] == "passed",
            control_status_policy,
        ),
        check(
            "control_results_schema_frozen",
            all(
                field in control_result_schema["required_fields"]
                for field in [
                    "control_id",
                    "control_status",
                    "blocked_condition",
                    "expected_result",
                    "actual_result",
                    "claim_allowed_when_control_triggers",
                    "rung_effect",
                ]
            ),
            control_result_schema,
        ),
        check(
            "active_null_sentinel_policy_frozen",
            active_null_sentinel_policy["positive_rows_must_use_strict_booleans"] is True,
            active_null_sentinel_policy,
        ),
        check(
            "i1_i2_control_alias_map_frozen",
            all(
                key in CONTROL_ALIAS_MAP
                for key in [
                    "label_only_new_basin_control",
                    "hidden_producer_insertion_control",
                    "semantic_relabel_control",
                ]
            ),
            CONTROL_ALIAS_MAP,
        ),
        check(
            "lane_cross_field_invariants_frozen",
            lane_cross_field_invariants["native"]["formation_source_required"] == "native_source_current_bifurcation"
            and lane_cross_field_invariants["native"]["n24_producer_lane_status_required"] == "not_used_in_native_row"
            and lane_cross_field_invariants["producer_assisted"]["formation_source_required"] == "producer_flux_conditioned",
            lane_cross_field_invariants,
        ),
        check(
            "temporal_window_fields_required",
            all(field in CANDIDATE_EVIDENCE_FIELDS for field in temporal_window_policy["required_fields"]),
            temporal_window_policy,
        ),
        check(
            "basin_signature_digests_required",
            all(field in CANDIDATE_EVIDENCE_FIELDS for field in basin_digest_policy["bf3_plus_required_digests"]),
            basin_digest_policy,
        ),
        check(
            "producer_controls_frozen",
            all(
                control_id in CONTROL_IDS
                for control_id in [
                    "producer_schedule_post_hoc_control",
                    "producer_hidden_support_control",
                    "producer_threshold_relaxation_control",
                    "producer_basin_insertion_without_trace_control",
                    "producer_success_as_native_relabel_control",
                    "producer_success_overwrites_native_failure_control",
                ]
            ),
            CONTROL_IDS,
        ),
        check(
            "no_positive_n25_evidence_opened",
            True,
            "I2 freezes schema/control rules only; no BF rung is assigned.",
        ),
    ]
    failed = [item for item in checks if not item["passed"]]
    output: dict[str, Any] = {
        "artifact_id": "n25_basin_formation_schema_and_controls",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I2",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_basin_formation_schema_controls_frozen_no_positive_evidence"
            if not failed
            else "failed_basin_formation_schema_controls"
        ),
        "source_inventory": i1_status,
        "source_contract_row": i1["source_contract_row"],
        "source_consumable_contract_row": i1["source_consumable_contract_row"],
        "candidate_evidence_row_schema": candidate_schema,
        "formation_definitions": formation_definitions,
        "lane_ceiling_policy": lane_ceiling_policy,
        "lane_cross_field_invariants": lane_cross_field_invariants,
        "native_flux_debt_policy": native_flux_debt_policy,
        "native_spark_source_policy": native_spark_source_policy,
        "control_status_policy": control_status_policy,
        "control_result_schema": control_result_schema,
        "active_null_sentinel_policy": active_null_sentinel_policy,
        "control_alias_map": CONTROL_ALIAS_MAP,
        "temporal_window_policy": temporal_window_policy,
        "basin_digest_policy": basin_digest_policy,
        "artifact_role_policy": {
            "artifact_role_values": ARTIFACT_ROLE_VALUES,
            "positive_support_forbidden_if_only_roles": POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES,
        },
        "bf_ladder": BF_LADDER,
        "n25_closeout_ladder": N25_CLOSEOUT_LADDER,
        "rung_support_policy": rung_policy,
        "controls": controls,
        "ap_gap_policy": {
            "ap4_dependency_status_values": AP4_DEPENDENCY_STATUS_VALUES,
            "ap5_dependency_status_values": AP5_DEPENDENCY_STATUS_VALUES,
            "ap4_gap_prose_only_blocks_row": True,
            "ap5_required_only_when_proxy_target_or_proxy_valuation_participates": True,
        },
        "claim_boundary": {
            "unsafe_claims": UNSAFE_CLAIMS,
            "unsafe_claim_flags_required_false": True,
            "basin_formation_candidate_is_not_agency_or_native_support": True,
        },
        "bf_ladder_rung_assigned": False,
        "n25_closeout_ladder_rung": "N25-C0_schema_only",
        "basin_formation_evidence_opened": False,
        "ready_for_iteration_3_active_nulls": not failed,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value({k: v for k, v in output.items() if k != "output_digest"})
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N25 Iteration 2 - Basin-Formation Schema And Controls",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Frozen Schema",
        "",
        "- Candidate rows require explicit native or producer-assisted lane.",
        "- Row-level lane ceilings prevent producer-assisted success from upgrading native BF or N24 native C6.",
        "- Formation class and formation source are closed enums.",
        "- Native rows must preserve `native_flux_debt_bound = 1e-9` and `native_flux_debt_widened = false`.",
        "- Native probes must consider existing LGRC/LGRC9V3 spark mechanisms before adding producer code.",
        "- Producer-assisted rows cap conditioned flux at `1e-8` across at most 10 windows.",
        "- Active-null controls expect `failed_closed`; positive candidate controls expect blocker absence as `passed`.",
        "- Positive candidate rows must carry full `control_results`; active-null sentinel values are fixture-only.",
        "- Candidate rows must carry source digests, artifact path/SHA equality, temporal windows, and basin signature digests.",
        "- Artifact manifests must use formation-specific roles, not generic runtime traces.",
        "",
        "## Ladders",
        "",
    ]
    for rung, description in output["bf_ladder"].items():
        lines.append(f"- `{rung}`: {description}")
    lines.extend(["", "## Checks", ""])
    for item in output["checks"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {marker}: `{item['check_id']}`")
    lines.extend(
        [
            "",
            "## Result",
            "",
            "```text",
            f"failed_checks = {output['failed_checks']}",
            f"basin_formation_evidence_opened = {str(output['basin_formation_evidence_opened']).lower()}",
            f"ready_for_iteration_3_active_nulls = {str(output['ready_for_iteration_3_active_nulls']).lower()}",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()
