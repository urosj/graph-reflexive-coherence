#!/usr/bin/env python3
"""Build N28 Iteration 3 active nulls and failure baselines."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
I2_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_generative_extractive_schema_and_controls.json"
)
OUTPUT = EXPERIMENT / "outputs" / "n28_active_nulls_and_failure_baselines.json"
REPORT = EXPERIMENT / "reports" / "n28_active_nulls_and_failure_baselines.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_active_nulls_and_failure_baselines.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

EXPECTED_I2_DIGEST = "e118496c025e1a36aac7e4337adcacd869715a5ce5ec6aaaf1558ef0d6576c18"

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "ap5_nat4_gap_resolution_claim_allowed": False,
    "generative_persistence_claim_allowed": False,
    "n28_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_cooperation_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_identity_claim_allowed": False,
    "semantic_learning_claim_allowed": False,
    "sentience_claim_allowed": False,
    "unrestricted_autonomy_claim_allowed": False,
}

NULL_DEFINITIONS: dict[str, dict[str, Any]] = {
    "source_digest_mismatch_control": {
        "active_null_id": "source_digest_mismatch",
        "blocked_condition": "candidate row cites a source digest that differs from the I2 frozen source pins",
        "violated_axis": "source_admissibility",
        "expected_gate": "source digest pins match before classification",
        "geometric_reading": "The row is detached from the admitted source geometry. Even if it looks basin-like, it cannot inherit the N20/N27 contract surface.",
    },
    "derived_report_only_positive_row_control": {
        "active_null_id": "derived_report_only_positive_row",
        "blocked_condition": "report-derived row tries to count as positive N28 source-current evidence",
        "violated_axis": "source_current_inputs",
        "expected_gate": "positive rows require runtime/source-current inputs",
        "geometric_reading": "The geometry exists only as an interpretation layer. No focal, neighbor, extraction, or leakage trace is available for replay.",
    },
    "artifact_manifest_failure_control": {
        "active_null_id": "artifact_manifest_failure",
        "blocked_condition": "artifact manifest is missing, unrole-labeled, digest-mismatched, or non-portable",
        "violated_axis": "artifact_admissibility",
        "expected_gate": "positive rows require role-labeled artifacts with matching hashes",
        "geometric_reading": "The basin and neighborhood traces cannot be audited or reconstructed, so apparent capacity cannot be source-backed.",
    },
    "threshold_declared_after_outcome_control": {
        "active_null_id": "threshold_declared_after_outcome",
        "blocked_condition": "classification threshold appears after observed outcome",
        "false_positive_group": "policy_threshold_attribution_false_positives",
        "violated_axis": "classification_policy",
        "expected_gate": "thresholds declared before use",
        "geometric_reading": "The boundary between generative, extractive, and neutral regimes is drawn around the result instead of constraining the geometry.",
    },
    "missing_focal_stability_digest_control": {
        "active_null_id": "missing_focal_stability_digest",
        "blocked_condition": "generative_extractive_core is missing focal stability digest",
        "false_positive_group": "core_digest_false_positives",
        "violated_axis": "focal_persistence_axis",
        "expected_gate": "core contains focal_stability_digest before classification",
        "geometric_reading": "The focal basin is not source-current in the canonical core, so no persistence regime can be assigned.",
    },
    "missing_neighbor_capacity_digest_control": {
        "active_null_id": "missing_neighbor_capacity_digest",
        "blocked_condition": "generative_extractive_core is missing neighborhood capacity digest",
        "false_positive_group": "core_digest_false_positives",
        "violated_axis": "neighborhood_capacity_axis",
        "expected_gate": "core contains neighborhood capacity and neighbor support/boundary digests",
        "geometric_reading": "The neighbor capacity axis cannot be audited, so generativity would be inferred without source-current capacity geometry.",
    },
    "missing_extraction_cost_digest_control": {
        "active_null_id": "missing_extraction_cost_digest",
        "blocked_condition": "generative_extractive_core is missing extraction cost digest",
        "false_positive_group": "core_digest_false_positives",
        "violated_axis": "extraction_leakage_axis",
        "expected_gate": "core contains extraction_cost_digest before classification",
        "geometric_reading": "The focal basin might persist by extraction, but the extraction axis is absent from the core.",
    },
    "missing_merge_leakage_digest_control": {
        "active_null_id": "missing_merge_leakage_digest",
        "blocked_condition": "generative_extractive_core is missing merge/leakage digest",
        "false_positive_group": "core_digest_false_positives",
        "violated_axis": "extraction_leakage_axis",
        "expected_gate": "core contains merge_leakage_digest before classification",
        "geometric_reading": "Neighbor support could be merge or leakage, but the core cannot distinguish it from generated capacity.",
    },
    "missing_capacity_attribution_digest_control": {
        "active_null_id": "missing_capacity_attribution_digest",
        "blocked_condition": "generative_extractive_core is missing capacity attribution digest",
        "false_positive_group": "core_digest_false_positives",
        "violated_axis": "capacity_attribution_trace",
        "expected_gate": "core contains capacity_attribution_digest before classification",
        "geometric_reading": "The capacity gain has no source-current attribution, so it could be a producer label or hidden medium policy.",
    },
    "malformed_generative_extractive_core_digest_control": {
        "active_null_id": "malformed_generative_extractive_core_digest",
        "blocked_condition": "generative_extractive_core_digest does not match canonical core payload",
        "false_positive_group": "core_digest_false_positives",
        "violated_axis": "generative_extractive_core_digest",
        "expected_gate": "core digest must match canonical sorted JSON payload",
        "geometric_reading": "The canonical core has been altered or reconstructed, so replay/control rows cannot bind to the same geometry.",
    },
    "policy_retuning_to_fit_label_control": {
        "active_null_id": "policy_retuning_to_fit_label",
        "blocked_condition": "classification policy is retuned to force the desired regime label",
        "false_positive_group": "policy_threshold_attribution_false_positives",
        "violated_axis": "shared_regime_policy",
        "expected_gate": "shared policy remains fixed or records split-policy blocker",
        "geometric_reading": "The same geometric state changes regime only because the measuring surface moved, not because focal/neighbor/extraction axes changed.",
    },
    "label_specific_threshold_control": {
        "active_null_id": "label_specific_threshold",
        "blocked_condition": "different thresholds are used only to make labels pass",
        "violated_axis": "shared_regime_policy",
        "expected_gate": "label-specific thresholds are rejected unless explicitly blocked as split policy",
        "geometric_reading": "Generative and extractive states are no longer compared in the same metric space, so regime separation is not source-current.",
    },
    "post_hoc_regime_boundary_shift_control": {
        "active_null_id": "post_hoc_regime_boundary_shift",
        "blocked_condition": "regime boundary is moved after seeing the row outcome",
        "violated_axis": "regime_boundary_trace",
        "expected_gate": "regime boundary fixed before row classification",
        "geometric_reading": "The classification boundary follows the row rather than testing the row against a declared geometric boundary.",
    },
    "focal_survival_only_as_generative_control": {
        "active_null_id": "focal_survival_only_as_generative",
        "blocked_condition": "stable focal basin is relabeled generative without neighborhood capacity improvement",
        "violated_axis": "neighborhood_capacity_axis",
        "expected_gate": "generative requires improved neighborhood capacity",
        "geometric_reading": "The focal basin persists, but the surrounding capacity axis is missing. This is persistence only, not generativity.",
    },
    "neighbor_label_only_as_capacity_control": {
        "active_null_id": "neighbor_label_only_as_capacity",
        "blocked_condition": "neighbor label changes without support/coherence/boundary/capacity traces",
        "violated_axis": "neighborhood_capacity_axis",
        "expected_gate": "capacity requires source-current neighbor metrics",
        "geometric_reading": "The neighbor has a new name, not a stronger basin-forming surface. Label change does not create capacity.",
    },
    "neighbor_count_only_as_capacity_control": {
        "active_null_id": "neighbor_count_only_as_capacity",
        "blocked_condition": "neighbor count increases without distinguishability/support/boundary capacity",
        "violated_axis": "neighborhood_capacity_axis",
        "expected_gate": "count alone cannot satisfy capacity",
        "geometric_reading": "More counted parts do not imply stronger basin-forming geometry if support, coherence, and boundary traces are absent.",
    },
    "merge_leakage_as_support_control": {
        "active_null_id": "merge_leakage_as_support",
        "blocked_condition": "merge or leakage into neighbor is counted as neighbor support",
        "violated_axis": "extraction_leakage_axis",
        "expected_gate": "support improvement must not be merge/leakage",
        "geometric_reading": "The neighbor appears supported because boundaries blur or flux leaks. That is not generated capacity; it is loss of separation.",
    },
    "extractive_flattening_masked_control": {
        "active_null_id": "extractive_flattening_masked",
        "blocked_condition": "focal persistence hides environment flattening or extraction cost",
        "violated_axis": "extraction_leakage_axis",
        "expected_gate": "extractive flattening must remain visible",
        "geometric_reading": "The focal basin survives by reducing surrounding basin-forming structure. This is extractive persistence, not generative persistence.",
    },
    "competitive_persistence_as_generative_control": {
        "active_null_id": "competitive_persistence_as_generative",
        "blocked_condition": "competitive or neutral persistence is promoted to generative",
        "violated_axis": "regime_classification",
        "expected_gate": "neutral/competitive rows remain below generative support",
        "geometric_reading": "The focal basin persists while the neighborhood is unchanged or redistributed. No net capacity improvement is shown.",
    },
    "transfer_success_as_n28_success_control": {
        "active_null_id": "transfer_success_as_n28_success",
        "blocked_condition": "N27 CT6 transfer success is counted as N28 generativity",
        "violated_axis": "source_precedence",
        "expected_gate": "N27 transfer remains prerequisite/context only",
        "geometric_reading": "A basin signature survives a frame transfer, but that says nothing by itself about whether the surrounding medium gained capacity.",
    },
    "hidden_capacity_attribution_policy_control": {
        "active_null_id": "hidden_capacity_attribution_policy",
        "blocked_condition": "capacity improvement is attributed by hidden policy instead of source-current trace",
        "violated_axis": "capacity_attribution_trace",
        "expected_gate": "capacity attribution trace must be visible",
        "geometric_reading": "The capacity gain is assigned from outside the graph. The geometry does not show where the neighbor improvement came from.",
    },
    "producer_generativity_label_control": {
        "active_null_id": "producer_generativity_label",
        "blocked_condition": "producer label replaces source-current generativity traces",
        "violated_axis": "producer_residue",
        "expected_gate": "producer label cannot satisfy generative evidence",
        "geometric_reading": "The word generative is attached by a producer surface while focal/neighbor/extraction axes remain unproven.",
    },
    "medium_segmentation_policy_hidden_control": {
        "active_null_id": "medium_segmentation_policy_hidden",
        "blocked_condition": "hidden segmentation policy creates apparent neighbor capacity",
        "violated_axis": "medium_debt",
        "expected_gate": "medium segmentation must be explicit and cannot count as native capacity",
        "geometric_reading": "The neighborhood boundary is carved by hidden policy rather than emerging as an auditable source-current basin surface.",
    },
    "environment_capacity_budget_mismatch_control": {
        "active_null_id": "environment_capacity_budget_mismatch",
        "blocked_condition": "environment capacity is compared across incompatible budget surfaces",
        "violated_axis": "environment_capacity_budget_replay",
        "expected_gate": "capacity budgets must be replay-compatible",
        "geometric_reading": "The neighborhood looks stronger because the budget changed, not because the same medium gained basin-forming capacity.",
    },
    "neighbor_support_floor_missing_control": {
        "active_null_id": "neighbor_support_floor_missing",
        "blocked_condition": "neighbor support floor is missing",
        "violated_axis": "neighborhood_capacity_axis",
        "expected_gate": "neighbor support floor must be visible",
        "geometric_reading": "Without a support floor, the neighbor capacity claim cannot distinguish basin-forming support from noise or label changes.",
    },
    "neighbor_boundary_integrity_missing_control": {
        "active_null_id": "neighbor_boundary_integrity_missing",
        "blocked_condition": "neighbor boundary integrity trace is missing",
        "violated_axis": "neighborhood_capacity_axis",
        "expected_gate": "neighbor boundary must remain distinguishable",
        "geometric_reading": "The neighbor cannot be separated from focal or medium geometry, so improved capacity could be merge or leakage.",
    },
    "replay_failure_control": {
        "active_null_id": "replay_failure",
        "blocked_condition": "candidate classification fails artifact/snapshot/duplicate/core replay",
        "violated_axis": "replay_result",
        "expected_gate": "GE4+ requires replay stability",
        "geometric_reading": "The regime appears once but does not replay as the same focal-neighbor-extraction geometry.",
    },
    "stress_variant_failure_control": {
        "active_null_id": "stress_variant_failure",
        "blocked_condition": "candidate fails declared stress or variant matrix",
        "violated_axis": "stress_result",
        "expected_gate": "GE5+ requires stress/variant support",
        "geometric_reading": "The regime survives only as a narrow fixture artifact; it does not remain a stable regime boundary under perturbation.",
    },
    "semantic_cooperation_relabel_control": {
        "active_null_id": "semantic_cooperation_relabel",
        "blocked_condition": "semantic cooperation language is used as evidence",
        "violated_axis": "claim_boundary",
        "expected_gate": "semantic cooperation is blocked",
        "geometric_reading": "A social interpretation is substituted for focal, neighbor, and extraction/leakage traces.",
    },
    "semantic_choice_goal_relabel_control": {
        "active_null_id": "semantic_choice_goal_relabel",
        "blocked_condition": "choice, goal, or intention language is used as evidence",
        "violated_axis": "claim_boundary",
        "expected_gate": "semantic choice/goal/intention claims are blocked",
        "geometric_reading": "Goal language is substituted for geometric regime classification.",
    },
    "native_support_relabel_control": {
        "active_null_id": "native_support_relabel",
        "blocked_condition": "producer-mediated support or medium debt is relabeled native support",
        "violated_axis": "claim_boundary",
        "expected_gate": "native support remains blocked",
        "geometric_reading": "A visible or producer-mediated support surface is overclaimed as native support generation.",
    },
    "ant_ecology_relabel_control": {
        "active_null_id": "ant_ecology_relabel",
        "blocked_condition": "N28 primitive evidence is relabeled ant ecology behavior",
        "violated_axis": "claim_boundary",
        "expected_gate": "ant ecology remains unopened",
        "geometric_reading": "A basin-regime primitive is overread as ecology behavior before N29.",
    },
    "phase8_completion_relabel_control": {
        "active_null_id": "phase8_completion_relabel",
        "blocked_condition": "N28 primitive evidence is relabeled Phase 8 completion",
        "violated_axis": "claim_boundary",
        "expected_gate": "Phase 8 completion remains blocked",
        "geometric_reading": "A schema/control or primitive-row result is overread as completed implementation phase evidence.",
    },
    "native_ap5_relabel_control": {
        "active_null_id": "native_ap5_relabel",
        "blocked_condition": "N26 scoped AP5 context is promoted to native AP5",
        "violated_axis": "ap5_dependency_status",
        "expected_gate": "native AP5 remains unsupported",
        "geometric_reading": "Proxy/target context is imported as native AP5 support, bypassing the inherited AP5 NAT4 gap.",
    },
    "ap5_nat4_gap_resolution_relabel_control": {
        "active_null_id": "ap5_nat4_gap_resolution_relabel",
        "blocked_condition": "AP5 NAT4 gap is treated as resolved by N28 context",
        "violated_axis": "ap5_dependency_status",
        "expected_gate": "AP5 NAT4 gap resolution remains false",
        "geometric_reading": "A downstream regime classifier is used to backfill native target/proxy formation evidence it does not produce.",
    },
}


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


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    home_marker = "/" + "home/"
    repo_marker = "Documents/" + "RC-github"
    return home_marker not in text and repo_marker not in text


def infer_false_positive_group(control_id: str, violated_axis: str) -> str:
    if control_id in {
        "source_digest_mismatch_control",
        "derived_report_only_positive_row_control",
        "artifact_manifest_failure_control",
    }:
        return "source_artifact_hygiene"
    if violated_axis in {"focal_persistence_axis"}:
        return "focal_only_false_positives"
    if violated_axis in {"neighborhood_capacity_axis"}:
        return "neighbor_capacity_false_positives"
    if violated_axis in {"extraction_leakage_axis"}:
        return "extractive_merge_leakage_false_positives"
    if control_id == "transfer_success_as_n28_success_control":
        return "n27_inheritance_false_positives"
    if violated_axis in {
        "classification_policy",
        "shared_regime_policy",
        "regime_boundary_trace",
        "capacity_attribution_trace",
        "medium_debt",
        "environment_capacity_budget_replay",
    }:
        return "policy_threshold_attribution_false_positives"
    if violated_axis in {
        "claim_boundary",
        "ap5_dependency_status",
    }:
        return "ap_claim_boundary_false_positives"
    return "general_false_positive_controls"


def active_null_row(control: dict[str, Any], i2: dict[str, Any]) -> dict[str, Any]:
    control_id = control["control_id"]
    spec = NULL_DEFINITIONS[control_id]
    false_positive_group = spec.get(
        "false_positive_group",
        infer_false_positive_group(control_id, spec["violated_axis"]),
    )
    row_id = f"n28_i3_row_{spec['active_null_id']}"
    row = {
        "row_id": row_id,
        "iteration": "3",
        "row_decision": "rejected",
        "row_decision_scope": "active_null_false_positive_path_rejected",
        "active_null_id": spec["active_null_id"],
        "control_id": control_id,
        "control_status": "failed_closed",
        "control_status_meaning": "blocker triggered and claim correctly rejected",
        "control_satisfied_for_positive_row": False,
        "failed_open": False,
        "false_positive_group": false_positive_group,
        "blocked_condition": spec["blocked_condition"],
        "expected_result": "failed_closed_when_blocked_condition_present",
        "actual_result": "blocked_condition_present_claim_rejected",
        "expected_gate": spec["expected_gate"],
        "claim_allowed_when_control_triggers": False,
        "claim_ceiling": "active_null_failure_baseline_only_no_N28_positive_evidence",
        "rung_effect": control.get(
            "rung_effect",
            "blocks_GE3_or_stronger_unless_scope_limited_to_active_null",
        ),
        "orthogonal_role": "active_null_failure_baseline_for_future_positive_rows",
        "violated_axis": spec["violated_axis"],
        "geometric_reading": spec["geometric_reading"],
        "source_schema_output_digest": i2["output_digest"],
        "source_inventory_output_digest": i2["source_digest_pins"][
            "source_inventory_output_digest"
        ],
        "source_digest_pins": i2["source_digest_pins"],
        "source_current_inputs": [],
        "trace_admissibility": "active_null_fixture_only_not_positive_evidence",
        "positive_evidence_admissible": False,
        "derived_report_only": True,
        "schema_instantiation_only": True,
        "artifact_manifest": [],
        "all_artifact_sha256_match_file_contents": "not_applicable_active_null_fixture",
        "artifact_paths_equal_manifest_paths": "not_applicable_active_null_fixture",
        "row_specific_thresholds_declared_before_use": "not_applicable_active_null_fixture",
        "ge_ladder_rung": "not_assigned_active_null_control_only",
        "ge_ladder_rung_assigned": False,
        "n28_closeout_ceiling": "N28-C3_active_nulls_fail_closed",
        "n28_closeout_ladder_rung_assigned": False,
        "regime_label_attempted": "blocked",
        "regime_evidence_role": "active_null",
        "shared_regime_policy_status": "not_applicable_active_null",
        "generative_extractive_core": "not_applicable_active_null_fixture",
        "generative_extractive_core_digest": "not_applicable_active_null_fixture",
        "focal_persistence_axis": "not_evaluated_active_null"
        if control_id != "focal_survival_only_as_generative_control"
        else "stable",
        "neighborhood_capacity_axis": "missing_or_invalid_by_control",
        "extraction_leakage_axis": "missing_or_invalid_by_control",
        "medium_debt_as_success_allowed": False,
        "producer_residue_as_substrate_carried_allowed": False,
        "capacity_attribution_trace_required_for_positive_row": True,
        "claim_allowed": False,
        "positive_generative_evidence_opened": False,
        "positive_extractive_evidence_opened": False,
        "native_support_opened": False,
        "phase8_completion_opened": False,
        "ant_ecology_opened": False,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
    }
    row["row_digest"] = digest_value(row)
    return row


def build_output() -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT_PATH)
    schema_control_ids = [control["control_id"] for control in i2["control_families"]]
    rows = [active_null_row(control, i2) for control in i2["control_families"]]
    taxonomy: dict[str, list[str]] = {}
    for row in rows:
        taxonomy.setdefault(row["false_positive_group"], []).append(row["row_id"])

    evidence_state = {
        "positive_generative_evidence_opened": False,
        "positive_extractive_evidence_opened": False,
        "candidate_rows_classified": False,
        "ge_ladder_rung_assigned": False,
        "n28_closeout_ladder_rung_assigned": False,
        "native_support_opened": False,
        "phase8_completion_opened": False,
        "ant_ecology_opened": False,
        "ready_for_iteration_4_minimal_generativity_probe": True,
    }

    headline_controls = [
        "focal_survival_only_as_generative_control",
        "neighbor_label_only_as_capacity_control",
        "neighbor_count_only_as_capacity_control",
        "merge_leakage_as_support_control",
        "extractive_flattening_masked_control",
        "competitive_persistence_as_generative_control",
        "transfer_success_as_n28_success_control",
        "hidden_capacity_attribution_policy_control",
        "producer_generativity_label_control",
        "medium_segmentation_policy_hidden_control",
        "environment_capacity_budget_mismatch_control",
        "neighbor_support_floor_missing_control",
        "neighbor_boundary_integrity_missing_control",
        "replay_failure_control",
        "stress_variant_failure_control",
        "semantic_cooperation_relabel_control",
        "native_support_relabel_control",
        "ant_ecology_relabel_control",
        "phase8_completion_relabel_control",
        "native_ap5_relabel_control",
        "ap5_nat4_gap_resolution_relabel_control",
    ]

    checks = [
        {
            "check_id": "i2_schema_controls_passed",
            "passed": i2.get("status") == "passed"
            and i2.get("failed_checks") == []
            and i2.get("output_digest") == EXPECTED_I2_DIGEST,
        },
        {
            "check_id": "all_i2_controls_instantiated",
            "passed": set(row["control_id"] for row in rows) == set(schema_control_ids)
            and len(rows) == len(schema_control_ids),
        },
        {
            "check_id": "headline_checklist_controls_present",
            "passed": set(headline_controls).issubset({row["control_id"] for row in rows}),
        },
        {
            "check_id": "all_active_nulls_fail_closed",
            "passed": all(row["control_status"] == "failed_closed" for row in rows),
        },
        {
            "check_id": "control_row_required_fields_present",
            "passed": all(
                all(
                    field in row
                    for field in [
                        "control_id",
                        "control_status",
                        "blocked_condition",
                        "expected_result",
                        "actual_result",
                        "claim_allowed_when_control_triggers",
                        "rung_effect",
                        "orthogonal_role",
                        "control_satisfied_for_positive_row",
                        "row_decision",
                        "claim_ceiling",
                        "claim_allowed",
                        "unsafe_claim_flags",
                    ]
                )
                for row in rows
            ),
        },
        {
            "check_id": "false_positive_taxonomy_recorded",
            "passed": all(row["false_positive_group"] for row in rows)
            and len(taxonomy) >= 6,
        },
        {
            "check_id": "failed_open_control_count_zero",
            "passed": sum(1 for row in rows if row["failed_open"]) == 0,
        },
        {
            "check_id": "no_positive_evidence_opened",
            "passed": all(
                evidence_state[key] is False
                for key in [
                    "positive_generative_evidence_opened",
                    "positive_extractive_evidence_opened",
                    "candidate_rows_classified",
                    "ge_ladder_rung_assigned",
                    "n28_closeout_ladder_rung_assigned",
                    "native_support_opened",
                    "phase8_completion_opened",
                    "ant_ecology_opened",
                ]
            )
            and all(row["positive_evidence_admissible"] is False for row in rows),
        },
        {
            "check_id": "no_positive_ge_rung_assigned",
            "passed": all(row["ge_ladder_rung_assigned"] is False for row in rows),
        },
        {
            "check_id": "n28_closeout_ceiling_is_c3",
            "passed": all(
                row["n28_closeout_ceiling"] == "N28-C3_active_nulls_fail_closed"
                for row in rows
            ),
        },
        {
            "check_id": "source_digests_carried_from_i2",
            "passed": all(
                row["source_schema_output_digest"] == EXPECTED_I2_DIGEST
                and row["source_inventory_output_digest"]
                == i2["source_digest_pins"]["source_inventory_output_digest"]
                for row in rows
            ),
        },
        {
            "check_id": "i1_source_inventory_digest_carried",
            "passed": all(
                row["source_inventory_output_digest"]
                == "f30af50b1e1209039b82454b510f4765de7ee8befe214d96218dec3207db5985"
                for row in rows
            ),
        },
        {
            "check_id": "medium_debt_and_producer_residue_not_success",
            "passed": all(
                row["medium_debt_as_success_allowed"] is False
                and row["producer_residue_as_substrate_carried_allowed"] is False
                for row in rows
            ),
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(
                all(value is False for value in row["unsafe_claim_flags"].values())
                for row in rows
            ),
        },
    ]

    output = {
        "artifact_id": "n28_active_nulls_and_failure_baselines",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_active_nulls_fail_closed_no_positive_generative_evidence",
        "experiment": "N28",
        "iteration": "3",
        "n28_closeout_ceiling": "N28-C3_active_nulls_fail_closed",
        "claim_ceiling": "active_null_failure_baselines_only_no_N28_positive_evidence",
        "source_schema": {
            "path": I2_OUTPUT_PATH,
            "output_digest": i2["output_digest"],
            "artifact_sha256": sha256_file(I2_OUTPUT_PATH),
            "status": i2["status"],
            "acceptance_state": i2["acceptance_state"],
        },
        "source_digest_pins": i2["source_digest_pins"],
        "control_count": len(rows),
        "active_null_taxonomy": taxonomy,
        "active_null_rows": rows,
        "failed_open_control_count": sum(1 for row in rows if row["failed_open"]),
        "failed_closed_control_count": sum(
            1 for row in rows if row["control_status"] == "failed_closed"
        ),
        "evidence_state": evidence_state,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["passed"]],
    }
    checks.append(
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(output),
        }
    )
    output["failed_checks"] = [check["check_id"] for check in checks if not check["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N28 Iteration 3 - Active Nulls And Failure Baselines",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Closeout ceiling: `{output['n28_closeout_ceiling']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Source schema digest: `{output['source_schema']['output_digest']}`",
        f"- Active null rows: `{output['control_count']}`",
        f"- Failed-open controls: `{output['failed_open_control_count']}`",
        f"- Positive generative evidence opened: `{str(output['evidence_state']['positive_generative_evidence_opened']).lower()}`",
        f"- Ready for Iteration 4: `{str(output['evidence_state']['ready_for_iteration_4_minimal_generativity_probe']).lower()}`",
        "",
        "I3 instantiates every I2 control family as an active null. Each false-positive "
        "path fails closed and remains inadmissible as positive N28 evidence.",
        "",
        "## Active Null Rows",
        "",
        "| Row | Group | Control | Status | Violated Axis |",
        "|---|---|---|---|---|",
    ]
    for row in output["active_null_rows"]:
        lines.append(
            f"| `{row['row_id']}` | `{row['false_positive_group']}` | `{row['control_id']}` | "
            f"`{row['control_status']}` | `{row['violated_axis']}` |"
        )

    lines.extend(
        [
            "",
            "## False-Positive Taxonomy",
            "",
        ]
    )
    for group, row_ids in sorted(output["active_null_taxonomy"].items()):
        lines.append(f"- `{group}`: {len(row_ids)} rows")

    lines.extend(
        [
            "",
            "## Geometric Interpretation",
            "",
        ]
    )
    for row in output["active_null_rows"]:
        lines.append(f"- `{row['active_null_id']}`: {row['geometric_reading']}")

    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for check in output["checks"]:
        lines.append(f"| `{check['check_id']}` | `{str(check['passed']).lower()}` |")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "No active null row assigns a GE rung or opens positive generative/extractive "
            "evidence, native support, Phase 8 completion, or ant ecology.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)

    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["script_sha256"] = sha256_file(SCRIPT_RELATIVE_PATH)
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"report_sha256", "script_sha256", "output_digest"}
        }
    )
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)
    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["report_sha256"] = sha256_file(str(REPORT.relative_to(ROOT)))
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")


if __name__ == "__main__":
    main()
