#!/usr/bin/env python3
"""Build N24 Iteration 3 active nulls and failure baselines."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_active_nulls_and_failure_baselines.json"
REPORT = EXPERIMENT / "reports" / "n24_active_nulls_and_failure_baselines.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_active_nulls_and_failure_baselines.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_abundance_schema_and_controls.json"
)
I2_REPORT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "reports/n24_abundance_schema_and_controls.md"
)

REQUIRED_NULL_IDS = [
    "hidden_budget_relief_as_surplus",
    "floor_crossing_as_abundance",
    "surplus_without_optional_continuation",
    "optionality_without_surplus",
    "proxy_only_optional_branch_gain",
    "optional_branch_label_only",
    "single_branch_relabel_as_optionality",
    "independent_run_optional_assembly",
    "maintenance_basin_shift_as_surplus",
    "floor_renormalization_as_surplus",
    "post_hoc_surplus_construction",
    "n23_selection_context_relabel_as_abundance",
    "reward_maximization_relabel",
    "missing_maintenance_floor",
    "missing_boundary_integrity_trace",
    "optional_flux_drains_maintenance_support",
    "ap4_final_reclassification_relabel",
    "ap5_proxy_gap_omission",
    "semantic_choice_agency_native_support_phase8_relabels",
]

ACTIVE_NULL_EXTENSION_FIELDS = [
    "scenario_id",
    "blocker_class",
    "observed_null_signal",
    "control_ids_covered",
    "expected_result",
    "actual_result",
    "control_execution_kind",
    "trace_admissibility",
    "positive_evidence_admissible",
    "bad_condition_present",
    "bad_condition_rejected_by_control",
    "candidate_gate_passed",
    "schema_instantiation_only",
    "schema_expansion",
    "ab_ladder_rung",
    "n24_closeout_ladder_rung",
    "n24_closeout_ceiling",
    "artifact_manifest_empty_by_design",
    "artifact_sha256_match_status",
    "optional_flux_drain_status",
    "active_null_comparability",
    "geometric_failure_reading",
]

CONTROL_ALIAS_MAP = [
    {
        "null_id": "missing_maintenance_floor",
        "canonical_control_id": "floor_crossing_as_abundance_control",
        "control_alias_reason": (
            "missing predeclared floor blocks the same AB2+ gate as a crossed floor"
        ),
    },
    {
        "null_id": "missing_boundary_integrity_trace",
        "canonical_control_id": "optional_branch_label_only_control",
        "control_alias_reason": (
            "without boundary trace the branch is only a label-like optionality claim"
        ),
    },
    {
        "null_id": "optional_flux_drains_maintenance_support",
        "canonical_control_id": "floor_crossing_as_abundance_control",
        "control_alias_reason": (
            "flux drain is treated as maintenance-floor depletion rather than surplus"
        ),
    },
]

NULL_SCENARIOS = [
    {
        "scenario_id": "hidden_budget_relief_as_surplus",
        "blocker_class": "hidden_budget_relief",
        "control_ids": ["hidden_budget_relief_control"],
        "blocked_condition": "producer or hidden budget relief is used as apparent surplus",
        "observed_null_signal": "support margin appears only after undeclared budget relief",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": False,
        "support_surplus_present": True,
        "optional_count": 2,
        "availability_count": 2,
        "joint_count": 0,
        "surplus_owner": "hidden_budget_relief_blocks_row",
        "rung_effect": "blocks all positive AB support",
        "geometric_failure_reading": (
            "The maintenance basin seems to have spare support, but the spare "
            "margin is supplied by an undeclared producer/budget channel rather "
            "than by the source-current basin geometry."
        ),
    },
    {
        "scenario_id": "floor_crossing_as_abundance",
        "blocker_class": "maintenance_floor_crossing",
        "control_ids": ["floor_crossing_as_abundance_control"],
        "blocked_condition": "optional branch opens only by crossing the maintenance floor",
        "observed_null_signal": "surplus label appears while residual support is below floor",
        "support_floor_result": "crossed_floor",
        "coherence_floor_result": "changed_within_allowed_delta_above_floor",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 2,
        "availability_count": 2,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "rung_effect": "blocks AB2 and stronger",
        "geometric_failure_reading": (
            "The apparent optional branch is paid for by eroding the maintenance "
            "basin below its support floor, so it is depletion, not abundance."
        ),
    },
    {
        "scenario_id": "surplus_without_optional_continuation",
        "blocker_class": "surplus_without_optionality",
        "control_ids": ["surplus_without_optional_continuation_control"],
        "blocked_condition": "surplus margin exists but no optional continuation set is present",
        "observed_null_signal": "support remains above floor with zero optional alternatives",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": True,
        "optional_count": 0,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "rung_effect": "may leave AB2 descriptive surplus only; blocks AB3+",
        "geometric_failure_reading": (
            "The basin has spare support above the floor, but the geometry does "
            "not open a second continuation route in the same window."
        ),
    },
    {
        "scenario_id": "optionality_without_surplus",
        "blocker_class": "optionality_without_surplus",
        "control_ids": ["optionality_without_surplus_control"],
        "blocked_condition": "multiple branch labels appear without surplus above floor",
        "observed_null_signal": "optional alternatives are listed while support surplus is absent",
        "support_floor_result": "crossed_floor",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 2,
        "availability_count": 2,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "rung_effect": "blocks AB2 and AB3+",
        "geometric_failure_reading": (
            "The branch fan-out exists only by consuming maintenance support; "
            "the basin is branching under scarcity, not from surplus."
        ),
    },
    {
        "scenario_id": "proxy_only_optional_branch_gain",
        "blocker_class": "proxy_only_gain",
        "control_ids": ["proxy_only_optional_branch_gain_control"],
        "blocked_condition": "proxy or score improves without source-current optional geometry",
        "observed_null_signal": "proxy gain is recorded while branch traces are absent",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 0,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "not_recorded_blocks_row",
        "rung_effect": "blocks optionality support",
        "geometric_failure_reading": (
            "A scalar proxy improves, but no basin support margin or optional "
            "branch geometry is emitted as source-current trace."
        ),
    },
    {
        "scenario_id": "optional_branch_label_only",
        "blocker_class": "optional_branch_label_only",
        "control_ids": ["optional_branch_label_only_control"],
        "blocked_condition": "optional branch exists only as a label",
        "observed_null_signal": "branch id is present but support/coherence/flux traces are missing",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": True,
        "optional_count": 2,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "optionality_not_label_reassignment": False,
        "rung_effect": "blocks AB3+",
        "geometric_failure_reading": (
            "The graph carries branch names, but there are no branch-specific "
            "support, coherence, boundary, or flux traces."
        ),
    },
    {
        "scenario_id": "single_branch_relabel_as_optionality",
        "blocker_class": "single_branch_relabel",
        "control_ids": ["single_optional_branch_relabel_control"],
        "blocked_condition": "one continuation branch is relabeled as optionality",
        "observed_null_signal": "only one same-run continuation is available",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": True,
        "optional_count": 1,
        "availability_count": 1,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "rung_effect": "blocks AB3+",
        "geometric_failure_reading": (
            "The basin continues along a single route; there is no same-window "
            "alternative set, so continuation is not optionality."
        ),
    },
    {
        "scenario_id": "independent_run_optional_assembly",
        "blocker_class": "independent_run_assembly",
        "control_ids": ["independent_run_optional_assembly_control"],
        "blocked_condition": "branches from separate runs are assembled into one optional set",
        "observed_null_signal": "candidate branches share no same source-current optionality window",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": True,
        "optional_count": 2,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "trace_origin": "independent_run_assembly",
        "rung_effect": "blocks original AB3 optional set",
        "geometric_failure_reading": (
            "Two possible routes are observed in different runs, but the basin "
            "never had both available in the same source-current window."
        ),
    },
    {
        "scenario_id": "maintenance_basin_shift_as_surplus",
        "blocker_class": "maintenance_basin_shift",
        "control_ids": ["maintenance_basin_shift_control"],
        "blocked_condition": "surplus appears after changing the maintenance basin identity",
        "observed_null_signal": "maintenance basin signature changes between floor and surplus trace",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": True,
        "optional_count": 2,
        "availability_count": 2,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "maintenance_basin_shift": True,
        "rung_effect": "blocks surplus claim",
        "geometric_failure_reading": (
            "The floor is measured on one basin signature and the surplus on "
            "another, so the apparent margin is a basin-scope swap."
        ),
    },
    {
        "scenario_id": "floor_renormalization_as_surplus",
        "blocker_class": "floor_renormalization",
        "control_ids": ["floor_renormalization_as_surplus_control"],
        "blocked_condition": "maintenance floor is lowered after outcome inspection",
        "observed_null_signal": "surplus exists only under a post-hoc lower floor",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": True,
        "optional_count": 2,
        "availability_count": 2,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "thresholds_declared": False,
        "rung_effect": "blocks surplus claim",
        "geometric_failure_reading": (
            "The same basin state is made to look abundant by moving the floor "
            "after seeing the run, not by preserving a predeclared margin."
        ),
    },
    {
        "scenario_id": "post_hoc_surplus_construction",
        "blocker_class": "post_hoc_surplus_construction",
        "control_ids": ["post_hoc_surplus_construction_control"],
        "blocked_condition": "surplus trace is assembled after outcome inspection",
        "observed_null_signal": "surplus exists only as report-side reconstruction",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 2,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "not_recorded_blocks_row",
        "trace_origin": "report_derived",
        "rung_effect": "blocks AB2 and stronger",
        "geometric_failure_reading": (
            "The surplus margin is narrated after the fact instead of emitted "
            "as a predeclared source-current support/floor trace."
        ),
    },
    {
        "scenario_id": "n23_selection_context_relabel_as_abundance",
        "blocker_class": "n23_context_relabel",
        "control_ids": ["n23_selection_context_relabel_as_abundance_control"],
        "blocked_condition": "N23 selection-collapse context is relabeled as N24 abundance",
        "observed_null_signal": "LC6/N23-C6 context is consumed as surplus evidence",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 0,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "not_recorded_blocks_row",
        "rung_effect": "blocks N23 context relabel",
        "geometric_failure_reading": (
            "A prior collapse/selection artifact is mistaken for a current "
            "surplus margin; no N24 maintenance-floor geometry is present."
        ),
    },
    {
        "scenario_id": "reward_maximization_relabel",
        "blocker_class": "reward_relabel",
        "control_ids": ["reward_maximization_relabel_control"],
        "blocked_condition": "reward or goal-maximization label is used as abundance evidence",
        "observed_null_signal": "reward score changes without surplus-supported optional branches",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 0,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "not_recorded_blocks_row",
        "reward_or_proxy_label_absent_or_blocked": False,
        "rung_effect": "blocks reward/goal overclaim",
        "geometric_failure_reading": (
            "A reward label changes, but the basin does not show surplus and "
            "same-window optional branch geometry."
        ),
    },
    {
        "scenario_id": "missing_maintenance_floor",
        "blocker_class": "missing_maintenance_floor",
        "control_ids": ["floor_crossing_as_abundance_control"],
        "blocked_condition": "maintenance floor is missing or not declared before use",
        "observed_null_signal": "support value is present but no frozen floor exists",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 2,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "thresholds_declared": False,
        "rung_effect": "blocks AB2 and stronger",
        "geometric_failure_reading": (
            "Support cannot be called surplus because no predeclared "
            "maintenance floor anchors the measurement."
        ),
    },
    {
        "scenario_id": "missing_boundary_integrity_trace",
        "blocker_class": "missing_boundary_integrity",
        "control_ids": ["optional_branch_label_only_control"],
        "blocked_condition": "optional branch is asserted without boundary integrity trace",
        "observed_null_signal": "branch support exists but boundary state under optionality is missing",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": True,
        "optional_count": 2,
        "availability_count": 2,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "rung_effect": "blocks AB3+",
        "geometric_failure_reading": (
            "The basin opens branches without showing that its boundary remains "
            "intact while those branches are available."
        ),
    },
    {
        "scenario_id": "optional_flux_drains_maintenance_support",
        "blocker_class": "optional_flux_drain",
        "control_ids": ["floor_crossing_as_abundance_control"],
        "blocked_condition": "optional branch flux drains maintenance support below bound",
        "observed_null_signal": "branch flux cost exceeds leakage/flux bound",
        "support_floor_result": "crossed_floor",
        "coherence_floor_result": "changed_within_allowed_delta_above_floor",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "exceeded_bound",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 2,
        "availability_count": 2,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "optional_flux_does_not_drain_maintenance_support": False,
        "rung_effect": "blocks AB3+",
        "geometric_failure_reading": (
            "The optional route is geometrically expensive: flux leaves the "
            "maintenance basin faster than the surplus margin can sustain."
        ),
    },
    {
        "scenario_id": "ap4_final_reclassification_relabel",
        "blocker_class": "ap4_final_reclassification_relabel",
        "control_ids": ["ap4_final_reclassification_relabel_control"],
        "blocked_condition": "N23 AP4 bridge context is promoted to final global AP4 reclassification",
        "observed_null_signal": "final_global_ap4_reclassification_supported is asserted",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 0,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "not_recorded_blocks_row",
        "ap4_status": "missing_blocks_row",
        "rung_effect": "blocks final global AP4 reclassification",
        "geometric_failure_reading": (
            "A bridge-context classification is promoted into a global AP4 "
            "result without new N24 surplus geometry."
        ),
    },
    {
        "scenario_id": "ap5_proxy_gap_omission",
        "blocker_class": "ap5_gap_omission",
        "control_ids": ["ap5_proxy_gap_omission_control"],
        "blocked_condition": "proxy/reward-conditioned optionality omits AP5 dependency",
        "observed_null_signal": "proxy-conditioned branch row is asserted without AP5 status",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": True,
        "optional_count": 2,
        "availability_count": 2,
        "joint_count": 0,
        "surplus_owner": "source_current_geometry",
        "ap5_status": "missing_blocks_row",
        "reward_or_proxy_label_absent_or_blocked": False,
        "rung_effect": "blocks proxy/reward rows missing AP5 dependency",
        "geometric_failure_reading": (
            "The branch axis is proxy/reward conditioned, but the AP5 target or "
            "proxy dependency is not made row-local and auditable."
        ),
    },
    {
        "scenario_id": "semantic_choice_agency_native_support_phase8_relabels",
        "blocker_class": "unsafe_claim_relabels",
        "control_ids": [
            "semantic_choice_relabel_control",
            "agency_relabel_control",
            "native_support_relabel_control",
            "phase8_relabel_control",
        ],
        "blocked_condition": "artifact-level optionality is relabeled as choice, agency, native support, or Phase 8",
        "observed_null_signal": "unsafe claim label appears without permitted claim boundary",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "hidden_budget_relief_absent": True,
        "support_surplus_present": False,
        "optional_count": 0,
        "availability_count": 0,
        "joint_count": 0,
        "surplus_owner": "not_recorded_blocks_row",
        "rung_effect": "blocks unsafe semantic, agency, native-support, and Phase 8 claims",
        "geometric_failure_reading": (
            "A bounded artifact-level geometry condition is promoted into "
            "semantic choice, agency, native support, or implementation; none "
            "of those are N24 geometric evidence."
        ),
    },
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


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def unsafe_claim_flags(i2: dict[str, Any]) -> dict[str, bool]:
    return {
        claim: False
        for claim in sorted(i2["claim_boundary_schema"]["unsafe_claim_flags"].keys())
    }


def required_candidate_fields(i2: dict[str, Any]) -> list[str]:
    return list(i2["candidate_evidence_row_schema"]["required_fields"])


def i1_contract_row(i1: dict[str, Any]) -> dict[str, Any]:
    rows = i1.get("contract_inventory_rows", [])
    if not rows or not isinstance(rows[0], dict):
        raise KeyError("N24 I1 contract inventory row missing")
    return rows[0]


def trace(
    trace_id: str,
    scenario: dict[str, Any],
    status: str,
    detail: str,
    origin: str | None = None,
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "trace_status": status,
        "trace_origin": origin or scenario.get("trace_origin", "active_null_fixture"),
        "detail": detail,
        "blocked_condition": scenario["blocked_condition"],
        "positive_evidence_admissible": False,
    }


def threshold_record(row: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    declared = scenario.get("thresholds_declared", True)
    record = {
        "threshold_id": f"n24_i3_{scenario['scenario_id']}_thresholds",
        "source_contract_row": row["source_contract_row"],
        "source_consumable_contract_row": row["source_consumable_contract_row"],
        "threshold_declared_before_use": declared,
        "threshold_value_or_rule": {
            "support_floor_value": "N20 I5 required_support_floor",
            "coherence_floor_value": "N20 I5 required_coherence_floor",
            "boundary_integrity_floor_value": "N20 I5 boundary_integrity_floor",
            "flux_or_leakage_bound": "N20 I5 flux_balance_bounds",
            "ab3_minimum_availability_count": 2,
            "ab5_minimum_jointly_admissible_count": 2,
        },
        "failure_policy": "active_null_cannot_retune_or_override_thresholds",
    }
    record["threshold_record_digest"] = digest_value(record)
    return record


def optional_branch_record(
    scenario: dict[str, Any], branch_id: str, admissibility_status: str
) -> dict[str, Any]:
    return {
        "branch_id": branch_id,
        "source_node_id": "n24_i3_null_source_node",
        "target_node_id": f"n24_i3_{branch_id}_target_node",
        "edge_id_or_route_id": f"n24_i3_{branch_id}_route",
        "trace_origin": scenario.get("trace_origin", "active_null_fixture"),
        "trace_status": "present" if scenario["optional_count"] > 0 else "missing",
        "optionality_window_step_range": ["pre_positive_active_null"],
        "support_before": "not_applicable_active_null",
        "support_after_or_projected_after": "not_applicable_active_null",
        "coherence_before": "not_applicable_active_null",
        "coherence_after_or_projected_after": "not_applicable_active_null",
        "support_surplus_margin_before": "not_applicable_active_null",
        "support_surplus_margin_after": "not_applicable_active_null",
        "coherence_surplus_margin_before": "not_applicable_active_null",
        "coherence_surplus_margin_after": "not_applicable_active_null",
        "boundary_integrity_result": scenario["boundary_integrity_result"],
        "flux_or_leakage_result": scenario["flux_or_leakage_result"],
        "optional_flux_cost": "not_applicable_active_null",
        "maintenance_floor_preserved": scenario["support_floor_result"] != "crossed_floor",
        "reward_or_proxy_label_used": not scenario.get(
            "reward_or_proxy_label_absent_or_blocked", True
        ),
        "producer_enumeration_used": scenario.get("trace_origin") == "producer_label",
        "admissibility_status": admissibility_status,
    }


def optional_branch_records(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    if scenario["optional_count"] <= 0:
        return []
    status = (
        "rejected_active_null"
        if scenario["availability_count"] < 2
        or scenario.get("optionality_not_label_reassignment") is False
        else "blocked_before_positive_support"
    )
    return [
        optional_branch_record(scenario, f"branch_{index}", status)
        for index in range(1, scenario["optional_count"] + 1)
    ]


def control_results(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": control_id,
            "control_status": "failed_closed",
            "blocked_condition": scenario["blocked_condition"],
            "expected_result": "surplus-supported optionality claim rejected",
            "actual_result": "surplus_supported_optionality_claim_allowed=false",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": scenario["rung_effect"],
        }
        for control_id in scenario["control_ids"]
    ]


def optional_flux_drain_status(scenario: dict[str, Any]) -> str:
    if scenario["optional_count"] == 0:
        return "not_applicable"
    if scenario["flux_or_leakage_result"] == "missing":
        return "missing"
    if (
        scenario.get("optional_flux_does_not_drain_maintenance_support") is False
        or scenario["flux_or_leakage_result"] == "exceeded_bound"
    ):
        return "failed"
    return "preserved"


def comparability_record(
    source_row: dict[str, Any], i2: dict[str, Any], scenario: dict[str, Any]
) -> dict[str, Any]:
    seed_pairing = {
        "seed_pairing_rule_id": f"n24_i3_{scenario['scenario_id']}_seed_pairing",
        "same_seed_or_declared_seed_pairing_rule": True,
        "pairing_reason": (
            "pre-positive null uses the same declared source contract and "
            "budget/topology family as later N24 candidates while corrupting "
            "one abundance/optionality gate"
        ),
    }
    topology = {
        "topology_config_family": f"n24_i3_{scenario['scenario_id']}_topology_family",
        "same_topology_config_family": True,
    }
    runtime_envelope = {
        "runtime_envelope_id": f"n24_i3_{scenario['scenario_id']}_runtime_envelope",
        "same_runtime_envelope_or_declared_pairing_rule": True,
        "derived_report_only": True,
    }
    budget_schedule = {
        "budget_schedule_family": f"n24_i3_{scenario['scenario_id']}_budget_family",
        "same_budget_schedule_digest_when_applicable": True,
    }
    seed_pairing["seed_pairing_rule_digest"] = digest_value(seed_pairing)
    topology["topology_config_digest"] = digest_value(topology)
    runtime_envelope["runtime_envelope_digest"] = digest_value(runtime_envelope)
    budget_schedule["budget_schedule_digest"] = digest_value(budget_schedule)
    return {
        "same_source_contract_row_digest": True,
        "same_consumable_contract_row_digest": True,
        "same_basin_signature_fields": True,
        "basin_signature_fields": source_row["same_basin_rule"][
            "basin_signature_fields"
        ],
        "same_i2_schema_output_digest": i2["output_digest"],
        "seed_pairing_rule": seed_pairing,
        "topology_config": topology,
        "runtime_envelope": runtime_envelope,
        "budget_schedule": budget_schedule,
        "expected_result": "failed_closed",
        "blocked_condition": scenario["blocked_condition"],
    }


def build_row(
    index: int, scenario: dict[str, Any], i1: dict[str, Any], i2: dict[str, Any]
) -> dict[str, Any]:
    source_row = i1_contract_row(i1)
    n23 = i1["n23_context_boundary"]
    thresholds = threshold_record(source_row, scenario)
    support_surplus_present = scenario["support_surplus_present"]
    optionality_not_label = scenario.get("optionality_not_label_reassignment", True)
    flux_drain_status = optional_flux_drain_status(scenario)
    optional_flux_preserved = flux_drain_status == "preserved"
    reward_proxy_absent = scenario.get("reward_or_proxy_label_absent_or_blocked", True)
    maintenance_basin_id = (
        "n24_i3_shifted_maintenance_basin"
        if scenario.get("maintenance_basin_shift")
        else "n24_i3_declared_maintenance_basin"
    )
    maintenance_basin_signature_digest = digest_value(
        {
            "maintenance_basin_id": maintenance_basin_id,
            "scenario_id": scenario["scenario_id"],
            "shifted": scenario.get("maintenance_basin_shift", False),
        }
    )
    ap4_status = scenario.get(
        "ap4_status",
        "required_recorded"
        if scenario["scenario_id"]
        not in {"semantic_choice_agency_native_support_phase8_relabels"}
        else "not_applicable",
    )
    ap5_status = scenario.get(
        "ap5_status",
        "conditional_required_recorded"
        if not reward_proxy_absent
        else "not_applicable",
    )
    source_current_required_fields = source_row["source_current_fields"]
    row: dict[str, Any] = {
        "row_id": f"n24_i3_row_{index:02d}_{scenario['scenario_id']}",
        "source_contract_row": source_row["source_contract_row"],
        "source_consumable_contract_row": source_row["source_consumable_contract_row"],
        "source_contract_row_digest": i2["source_contract_digests"][
            "source_contract_row_digest"
        ],
        "source_consumable_contract_row_digest": i2["source_contract_digests"][
            "source_consumable_contract_row_digest"
        ],
        "source_output_digest": i1["output_digest"],
        "run_artifact_id": f"n24_i3_active_null_{scenario['scenario_id']}",
        "source_commit_or_source_digest": "not_applicable_pre_positive_active_null",
        "runtime_config_digest": digest_value(
            {
                "scenario_id": scenario["scenario_id"],
                "config_role": "pre_positive_active_null",
                "schema_output_digest": i2["output_digest"],
            }
        ),
        "source_current_inputs": [],
        "source_current_required_fields": source_current_required_fields,
        "row_specific_thresholds_declared_before_use": scenario.get(
            "thresholds_declared", True
        ),
        "n20_source_downstream_consumption_status": source_row[
            "n20_source_downstream_consumption_status"
        ],
        "n23_source_closeout_status": n23["n23_source_closeout_status"],
        "n23_closeout_required": n23["n23_closeout_required"],
        "n23_context_consumption": n23["n23_context_consumption"],
        "n23_ap4_bridge_status": n23["n23_ap4_bridge_status"],
        "ap4_context_status": (
            "missing_blocks_row"
            if scenario["scenario_id"] == "ap4_final_reclassification_relabel"
            else n23["n23_context_consumption"]
        ),
        "maintenance_floor_policy": "predeclared_support_and_coherence_floors_required",
        "maintenance_basin_id": maintenance_basin_id,
        "maintenance_basin_signature_digest": maintenance_basin_signature_digest,
        "support_measurement_scope": "maintenance_basin_node_set",
        "support_aggregation_method": "min",
        "surplus_channel_policy": (
            "support_surplus_required_and_coherence_floor_preserved"
        ),
        "support_floor_value": thresholds["threshold_value_or_rule"][
            "support_floor_value"
        ],
        "coherence_floor_value": thresholds["threshold_value_or_rule"][
            "coherence_floor_value"
        ],
        "boundary_integrity_floor_value": thresholds["threshold_value_or_rule"][
            "boundary_integrity_floor_value"
        ],
        "flux_or_leakage_bound": thresholds["threshold_value_or_rule"][
            "flux_or_leakage_bound"
        ],
        "optionality_window": {
            "window_id": f"n24_i3_{scenario['scenario_id']}_optionality_window",
            "start_step": "pre_positive_active_null",
            "end_step": "pre_positive_active_null",
            "window_role": "null_comparability_only",
        },
        "pre_surplus_geometry_trace": trace(
            f"n24_i3_{scenario['scenario_id']}_pre_surplus_geometry",
            scenario,
            "present" if support_surplus_present else "missing",
            scenario["observed_null_signal"],
        ),
        "support_surplus_margin_trace": trace(
            f"n24_i3_{scenario['scenario_id']}_support_surplus_margin",
            scenario,
            "present" if support_surplus_present else "missing",
            "active-null surplus margin trace rejected by blocker",
        )
        | {
            "formula": "observed_support - support_floor_value",
            "positive_margin_claimed": support_surplus_present,
        },
        "coherence_surplus_margin_trace": trace(
            f"n24_i3_{scenario['scenario_id']}_coherence_surplus_margin",
            scenario,
            "present"
            if scenario["coherence_floor_result"] in {"preserved", "changed_within_allowed_delta_above_floor"}
            else "missing",
            "active-null coherence margin trace rejected by blocker",
        )
        | {"formula": "observed_coherence - coherence_floor_value"},
        "residual_support_margin_under_optionality": (
            "negative_or_invalid_active_null"
            if scenario["support_floor_result"] == "crossed_floor"
            else "not_positive_evidence_active_null"
        ),
        "residual_coherence_margin_under_optionality": (
            "not_positive_evidence_active_null"
        ),
        "optional_flux_drain_margin": (
            "exceeded_bound_active_null"
            if scenario["flux_or_leakage_result"] == "exceeded_bound"
            else "not_positive_evidence_active_null"
        ),
        "maintenance_floor_trace": trace(
            f"n24_i3_{scenario['scenario_id']}_maintenance_floor",
            scenario,
            "present" if scenario.get("thresholds_declared", True) else "missing",
            "predeclared maintenance floor reference for null comparability",
        ),
        "optional_continuation_set_trace": trace(
            f"n24_i3_{scenario['scenario_id']}_optional_set",
            scenario,
            "present" if scenario["optional_count"] > 0 else "missing",
            "active-null optional set rejected or demoted by blocker",
            scenario.get("trace_origin", "active_null_fixture"),
        )
        | {
            "same_source_current_run": scenario.get("trace_origin")
            != "independent_run_assembly",
            "availability_count": scenario["availability_count"],
        },
        "optional_continuation_count": scenario["optional_count"],
        "optional_continuation_availability_count": scenario["availability_count"],
        "jointly_admissible_optional_continuation_count": scenario["joint_count"],
        "optional_branch_records": optional_branch_records(scenario),
        "optional_branch_evidence_mode": "source_current_available_unexecuted",
        "optional_branch_support_coherence_traces": trace(
            f"n24_i3_{scenario['scenario_id']}_branch_support_coherence",
            scenario,
            "present" if scenario["availability_count"] >= 2 else "missing",
            "branch-specific support/coherence trace active-null status",
        ),
        "optional_branch_boundary_flux_traces": trace(
            f"n24_i3_{scenario['scenario_id']}_branch_boundary_flux",
            scenario,
            "present"
            if scenario["boundary_integrity_result"] != "missing"
            and scenario["flux_or_leakage_result"] != "missing"
            else "missing",
            "branch-specific boundary/flux trace active-null status",
        ),
        "boundary_integrity_under_optionality_trace": trace(
            f"n24_i3_{scenario['scenario_id']}_boundary_under_optionality",
            scenario,
            "present" if scenario["boundary_integrity_result"] != "missing" else "missing",
            "boundary integrity under optionality active-null status",
        ),
        "optional_flux_does_not_drain_maintenance_support": optional_flux_preserved,
        "optional_flux_does_not_drain_maintenance_support_status": optional_flux_drain_status(
            scenario
        ),
        "surplus_budget_owner": scenario["surplus_owner"],
        "hidden_budget_relief_absent": scenario["hidden_budget_relief_absent"],
        "reward_or_proxy_label_absent_or_blocked": reward_proxy_absent,
        "same_basin_continuation_rule": i2["same_basin_rule_freeze"]["rule"],
        "same_basin_invariant_fields": i2["same_basin_rule_freeze"]["rule"][
            "basin_signature_fields"
        ],
        "out_of_scope_drift_blocks_row": True,
        "optionality_not_label_reassignment": optionality_not_label,
        "support_floor_result": scenario["support_floor_result"],
        "coherence_floor_result": scenario["coherence_floor_result"],
        "boundary_integrity_result": scenario["boundary_integrity_result"],
        "flux_or_leakage_result": scenario["flux_or_leakage_result"],
        "replay_result": {
            "replay_result_status": "not_applicable",
            "reason_code": "pre_positive_active_null_no_replay_claim",
            "affected_rung": "AB4_and_stronger",
            "why_outside_declared_scope": (
                "I3 active nulls test fail-closed blocker behavior before "
                "positive replay-backed N24 abundance probes are admitted"
            ),
        },
        "control_results": control_results(scenario),
        "ap4_dependency_status": ap4_status,
        "ap5_dependency_status": ap5_status,
        "ap4_condition_reason": (
            "missing AP4 dependency active null"
            if ap4_status == "missing_blocks_row"
            else "route/branch-conditioned optionality carries N23 AP4 bridge context"
            if ap4_status == "required_recorded"
            else "not route/branch conditioned"
        ),
        "ap5_condition_reason": (
            "missing AP5 dependency active null"
            if ap5_status == "missing_blocks_row"
            else "proxy/reward-conditioned row records conditional AP5 dependency"
            if ap5_status == "conditional_required_recorded"
            else "proxy/reward/target formation not used as evidence"
        ),
        "surplus_trace_digest": digest_value(
            {
                "scenario_id": scenario["scenario_id"],
                "support_surplus_present": support_surplus_present,
                "support_floor_result": scenario["support_floor_result"],
            }
        ),
        "optional_continuation_trace_digest": digest_value(
            {
                "scenario_id": scenario["scenario_id"],
                "optional_count": scenario["optional_count"],
                "availability_count": scenario["availability_count"],
            }
        ),
        "maintenance_floor_trace_digest": digest_value(
            {
                "scenario_id": scenario["scenario_id"],
                "thresholds_declared": scenario.get("thresholds_declared", True),
                "support_floor_result": scenario["support_floor_result"],
            }
        ),
        "replay_surplus_digest": "not_applicable_active_null",
        "replay_optionality_digest": "not_applicable_active_null",
        "surplus_persistence_ratio": 0.0,
        "optional_branch_persistence_ratio": 0.0,
        "surplus_threshold_or_rule": thresholds,
        "optionality_threshold_or_rule": thresholds,
        "hidden_budget_relief_rejected": scenario["scenario_id"]
        == "hidden_budget_relief_as_surplus"
        or scenario["hidden_budget_relief_absent"],
        "floor_crossing_rejected": scenario["support_floor_result"] == "crossed_floor",
        "surplus_without_optional_continuation_rejected_or_demoted": scenario[
            "scenario_id"
        ]
        == "surplus_without_optional_continuation",
        "optionality_without_surplus_rejected": scenario["scenario_id"]
        == "optionality_without_surplus",
        "proxy_only_success_rejected": scenario["scenario_id"]
        in {"proxy_only_optional_branch_gain", "reward_maximization_relabel"},
        "optional_branch_label_only_rejected": scenario["scenario_id"]
        in {"optional_branch_label_only", "single_branch_relabel_as_optionality"},
        "independent_run_optional_assembly_rejected": scenario["scenario_id"]
        == "independent_run_optional_assembly",
        "maintenance_basin_shift_rejected": scenario["scenario_id"]
        == "maintenance_basin_shift_as_surplus",
        "floor_renormalization_rejected": scenario["scenario_id"]
        in {"floor_renormalization_as_surplus", "missing_maintenance_floor"},
        "post_hoc_surplus_rejected": scenario["scenario_id"]
        == "post_hoc_surplus_construction",
        "n23_context_relabel_rejected": scenario["scenario_id"]
        == "n23_selection_context_relabel_as_abundance",
        "producer_residue_fields": source_row["producer_mediated_fields"],
        "naturalization_debt_fields": source_row["naturalization_debt_fields"],
        "blocked_relabel_fields": source_row["blocked_relabel_fields"],
        "claim_ceiling": (
            "pre-positive active null and failure baseline only; no AB, N24-C, "
            "surplus-supported optionality, reward maximization, semantic "
            "choice, agency, native support, sentience, Phase 8, or ant-ecology "
            "implementation claim"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(i2),
        "row_decision": "rejected",
        "surplus_supported_optionality_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "reward_maximization_claim_allowed": False,
        "agency_claim_allowed": False,
        "native_support_claim_allowed": False,
        "final_global_ap4_reclassification_supported": False,
        "derived_report_only": True,
        "artifact_manifest": [],
        "artifact_paths": [],
        "artifact_sha256": {},
        "artifact_paths_equal_manifest_paths": True,
        "artifact_sha256_equal_manifest_sha256": True,
        "all_artifact_sha256_match_file_contents": True,
        "output_digest": "pending",
        "scenario_id": scenario["scenario_id"],
        "blocker_class": scenario["blocker_class"],
        "observed_null_signal": scenario["observed_null_signal"],
        "control_ids_covered": scenario["control_ids"],
        "expected_result": "failed_closed",
        "actual_result": "failed_closed",
        "control_execution_kind": "schema_instantiation_only",
        "trace_admissibility": "active_null_fixture_only_not_positive_evidence",
        "positive_evidence_admissible": False,
        "bad_condition_present": True,
        "bad_condition_rejected_by_control": True,
        "candidate_gate_passed": False,
        "schema_instantiation_only": True,
        "schema_expansion": False,
        "ab_ladder_rung": "not_assigned_active_null_control_only",
        "n24_closeout_ladder_rung": "not_assigned_active_null_control_only",
        "n24_closeout_ceiling": "N24-C1_active_null_control_discipline_established",
        "artifact_manifest_empty_by_design": True,
        "artifact_sha256_match_status": (
            "vacuously_true_active_null_no_positive_artifacts"
        ),
        "optional_flux_drain_status": flux_drain_status,
        "active_null_comparability": comparability_record(source_row, i2, scenario),
        "geometric_failure_reading": scenario["geometric_failure_reading"],
    }
    row["output_digest"] = digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )
    return row


def build_rows(i1: dict[str, Any], i2: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        build_row(index, scenario, i1, i2)
        for index, scenario in enumerate(NULL_SCENARIOS, start=1)
    ]


def active_null_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "failed_closed_rows": sum(row["actual_result"] == "failed_closed" for row in rows),
        "failed_open_rows": sum(
            result["control_status"] == "failed_open"
            for row in rows
            for result in row["control_results"]
        ),
        "required_nulls_present": sorted(row["scenario_id"] for row in rows),
        "blocker_classes": sorted({row["blocker_class"] for row in rows}),
        "covered_controls": sorted(
            {control_id for row in rows for control_id in row["control_ids_covered"]}
        ),
        "surplus_supported_optionality_claim_allowed_any": any(
            row["surplus_supported_optionality_claim_allowed"] for row in rows
        ),
        "semantic_choice_claim_allowed_any": any(
            row["semantic_choice_claim_allowed"] for row in rows
        ),
        "reward_maximization_claim_allowed_any": any(
            row["reward_maximization_claim_allowed"] for row in rows
        ),
        "positive_abundance_evidence_opened": False,
        "ab_ladder_rung_assigned_above_control_scope": False,
        "n24_closeout_ladder_rung_assigned": False,
        "n24_closeout_ceiling": "N24-C1_active_null_control_discipline_established",
    }


def grouped_nulls(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    groups = {
        "surplus_blockers": {
            "hidden_budget_relief_as_surplus",
            "floor_crossing_as_abundance",
            "missing_maintenance_floor",
            "maintenance_basin_shift_as_surplus",
            "floor_renormalization_as_surplus",
            "post_hoc_surplus_construction",
            "optional_flux_drains_maintenance_support",
        },
        "optionality_blockers": {
            "surplus_without_optional_continuation",
            "optionality_without_surplus",
            "optional_branch_label_only",
            "single_branch_relabel_as_optionality",
            "independent_run_optional_assembly",
            "missing_boundary_integrity_trace",
        },
        "artifact_or_context_blockers": {
            "proxy_only_optional_branch_gain",
            "n23_selection_context_relabel_as_abundance",
            "reward_maximization_relabel",
        },
        "ap_blockers": {
            "ap4_final_reclassification_relabel",
            "ap5_proxy_gap_omission",
        },
        "unsafe_relabel_blockers": {
            "semantic_choice_agency_native_support_phase8_relabels",
        },
    }
    present = {row["scenario_id"] for row in rows}
    return {
        group: sorted(ids & present)
        for group, ids in groups.items()
    }


def all_required_fields_present(rows: list[dict[str, Any]], fields: list[str]) -> bool:
    return all(all(field in row for field in fields) for row in rows)


def row_field_set_matches_i2_plus_extensions(
    rows: list[dict[str, Any]], required_fields: list[str]
) -> bool:
    allowed = set(required_fields) | set(ACTIVE_NULL_EXTENSION_FIELDS)
    return all(set(row.keys()) == allowed for row in rows)


def build_checks(
    i1: dict[str, Any], i2: dict[str, Any], rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    required_fields = required_candidate_fields(i2)
    required_controls = set(i2["control_matrix_schema"]["required_control_ids"])
    present_null_ids = {row["scenario_id"] for row in rows}
    summary = active_null_summary(rows)
    return [
        check(
            "source_i1_inventory_passed",
            i1["status"] == "passed" and not i1["failed_checks"],
            {
                "status": i1["status"],
                "acceptance_state": i1["acceptance_state"],
                "failed_checks": i1["failed_checks"],
            },
        ),
        check(
            "source_i2_schema_passed",
            i2["status"] == "passed"
            and not i2["failed_checks"]
            and i2["evidence_boundary"]["ready_for_iteration_3_active_nulls"],
            {
                "status": i2["status"],
                "acceptance_state": i2["acceptance_state"],
                "failed_checks": i2["failed_checks"],
                "ready_for_iteration_3_active_nulls": i2["evidence_boundary"][
                    "ready_for_iteration_3_active_nulls"
                ],
            },
        ),
        check(
            "source_digest_chain_aligned",
            i2["i1_inventory_reference"]["output_digest"] == i1["output_digest"],
            {
                "i1_output_digest": i1["output_digest"],
                "i2_i1_reference_digest": i2["i1_inventory_reference"][
                    "output_digest"
                ],
                "i2_output_digest": i2["output_digest"],
            },
        ),
        check(
            "required_active_null_matrix_complete",
            present_null_ids == set(REQUIRED_NULL_IDS),
            {"required": REQUIRED_NULL_IDS, "present": sorted(present_null_ids)},
        ),
        check(
            "canonical_controls_covered",
            required_controls
            == {control for row in rows for control in row["control_ids_covered"]},
            {
                "required_controls": sorted(required_controls),
                "covered_controls": active_null_summary(rows)["covered_controls"],
            },
        ),
        check(
            "control_alias_map_documents_broader_controls",
            {item["null_id"] for item in CONTROL_ALIAS_MAP}
            == {
                "missing_maintenance_floor",
                "missing_boundary_integrity_trace",
                "optional_flux_drains_maintenance_support",
            }
            and all(
                item["canonical_control_id"] in required_controls
                and item["control_alias_reason"]
                for item in CONTROL_ALIAS_MAP
            ),
            CONTROL_ALIAS_MAP,
        ),
        check(
            "candidate_evidence_fields_present_in_all_rows",
            all_required_fields_present(rows, required_fields),
            {"required_field_count": len(required_fields)},
        ),
        check(
            "row_field_set_equals_i2_required_plus_active_null_extensions",
            row_field_set_matches_i2_plus_extensions(rows, required_fields),
            {
                "required_field_count": len(required_fields),
                "active_null_extension_field_count": len(ACTIVE_NULL_EXTENSION_FIELDS),
                "active_null_extension_fields": ACTIVE_NULL_EXTENSION_FIELDS,
            },
        ),
        check(
            "schema_instantiated_without_expansion",
            all(row["schema_instantiation_only"] and not row["schema_expansion"] for row in rows),
            "I3 rows instantiate I2 candidate schema plus declared active-null metadata only",
        ),
        check(
            "active_null_fixtures_not_positive_evidence",
            all(
                row["trace_admissibility"]
                == "active_null_fixture_only_not_positive_evidence"
                and row["positive_evidence_admissible"] is False
                and row["control_execution_kind"] == "schema_instantiation_only"
                and row["derived_report_only"] is True
                for row in rows
            ),
            "active null rows can reject false positives but cannot support AB evidence",
        ),
        check(
            "all_active_nulls_fail_closed",
            all(row["actual_result"] == "failed_closed" for row in rows)
            and summary["failed_open_rows"] == 0,
            summary,
        ),
        check(
            "failed_closed_semantics_are_not_positive_demotions",
            all(
                result["control_status"] == "failed_closed"
                and result["control_satisfied_for_positive_row"] is True
                and result["claim_allowed_when_control_triggers"] is False
                for row in rows
                for result in row["control_results"]
            ),
            "failed_closed satisfies the negative control while rejecting the unsafe/null claim",
        ),
        check(
            "surplus_and_optionality_nulls_are_distinct",
            {
                "surplus_without_optional_continuation",
                "optionality_without_surplus",
            }.issubset(present_null_ids)
            and any(
                row["scenario_id"] == "surplus_without_optional_continuation"
                and row["optional_continuation_availability_count"] == 0
                for row in rows
            )
            and any(
                row["scenario_id"] == "optionality_without_surplus"
                and row["support_floor_result"] == "crossed_floor"
                for row in rows
            ),
            "I3 separately blocks surplus-only and optionality-without-surplus false positives",
        ),
        check(
            "optional_label_and_independent_run_controls_present",
            {
                "optional_branch_label_only",
                "single_branch_relabel_as_optionality",
                "independent_run_optional_assembly",
            }.issubset(present_null_ids),
            "optional branches must be same-run geometry, not labels or cross-run assembly",
        ),
        check(
            "ap_gap_and_final_ap4_relabel_controls_present",
            {
                "ap4_final_reclassification_relabel",
                "ap5_proxy_gap_omission",
            }.issubset(present_null_ids)
            and all(
                row["final_global_ap4_reclassification_supported"] is False
                for row in rows
            ),
            "AP4/AP5 gap controls are row-local and final global AP4 remains false",
        ),
        check(
            "artifact_manifest_fields_present_but_not_positive",
            all(
                row["artifact_manifest"] == []
                and row["artifact_paths"] == []
                and row["artifact_sha256"] == {}
                and row["artifact_manifest_empty_by_design"] is True
                and row["artifact_sha256_match_status"]
                == "vacuously_true_active_null_no_positive_artifacts"
                and row["artifact_paths_equal_manifest_paths"] is True
                and row["artifact_sha256_equal_manifest_sha256"] is True
                and row["all_artifact_sha256_match_file_contents"] is True
                for row in rows
            ),
            "active null rows carry manifest fields without positive run artifacts",
        ),
        check(
            "optional_flux_drain_status_scoped",
            all(
                row["optional_flux_drain_status"] in {"preserved", "failed", "not_applicable", "missing"}
                for row in rows
            )
            and any(
                row["scenario_id"] == "optional_flux_drains_maintenance_support"
                and row["optional_flux_drain_status"] == "failed"
                and row["optional_flux_does_not_drain_maintenance_support"] is False
                for row in rows
            )
            and any(
                row["scenario_id"] == "proxy_only_optional_branch_gain"
                and row["optional_flux_drain_status"] == "not_applicable"
                for row in rows
            ),
            "flux-drain status distinguishes preserved, failed, missing, and not-applicable null rows",
        ),
        check(
            "no_source_current_inputs_opened",
            all(row["source_current_inputs"] == [] for row in rows),
            "active nulls do not provide positive source-current inputs",
        ),
        check(
            "no_ab_or_n24c_rungs_above_control_scope",
            all(
                row["ab_ladder_rung"] == "not_assigned_active_null_control_only"
                and row["n24_closeout_ladder_rung"]
                == "not_assigned_active_null_control_only"
                for row in rows
            ),
            {
                "ab_ladder_rung_assigned_above_control_scope": False,
                "n24_closeout_ladder_rung_assigned": False,
                "n24_closeout_ceiling": "N24-C1_active_null_control_discipline_established",
            },
        ),
        check(
            "unsafe_claim_flags_all_false",
            all(
                set(row["unsafe_claim_flags"].keys())
                == set(i2["claim_boundary_schema"]["unsafe_claim_flags"].keys())
                and all(value is False for value in row["unsafe_claim_flags"].values())
                for row in rows
            ),
            "unsafe claims remain blocked in every active null row",
        ),
        check(
            "geometric_interpretations_present",
            all(row["geometric_failure_reading"] for row in rows),
            "each row records a geometric failure interpretation",
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
    i2 = load_json(I2_OUTPUT_PATH)
    rows = build_rows(i1, i2)
    checks = build_checks(i1, i2, rows)
    payload: dict[str, Any] = {
        "artifact_id": "n24_active_nulls_and_failure_baselines",
        "schema_version": "n24_active_nulls_and_failure_baselines_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": 3,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_active_nulls_fail_closed_no_positive_evidence",
        "purpose": (
            "Instantiate the frozen I2 schema as active nulls and failure "
            "baselines before positive surplus-supported optionality probes."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n24_i2_schema_and_controls"),
            source_record(I2_REPORT_PATH, "n24_i2_schema_and_controls_report"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "required_null_ids": REQUIRED_NULL_IDS,
        "row_field_policy": {
            "candidate_required_fields_source": (
                "N24 I2 candidate_evidence_row_schema.required_fields"
            ),
            "candidate_required_field_count": len(required_candidate_fields(i2)),
            "active_null_extension_fields": ACTIVE_NULL_EXTENSION_FIELDS,
            "active_null_extension_field_count": len(ACTIVE_NULL_EXTENSION_FIELDS),
            "row_field_set_rule": (
                "I3 row keys must equal I2 required fields plus declared "
                "active-null extension fields"
            ),
        },
        "active_null_rows": rows,
        "active_null_summary": active_null_summary(rows),
        "active_null_grouping": grouped_nulls(rows),
        "control_alias_map": CONTROL_ALIAS_MAP,
        "iteration3_boundary": {
            "schema_instantiation_only": True,
            "schema_expansion": False,
            "positive_run_artifacts_consumed": False,
            "source_current_inputs_opened": False,
            "surplus_supported_optionality_evidence_opened": False,
            "surplus_supported_optionality_supported": False,
            "ab_ladder_rung_assigned_above_control_scope": False,
            "n24_closeout_ladder_rung_assigned": False,
            "n24_closeout_ceiling": "N24-C1_active_null_control_discipline_established",
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_supported": False,
            "semantic_choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "ready_for_iteration_4_positive_probe": True,
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
        payload["acceptance_state"] = "blocked_active_null_checks_failed"
    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    rows = data["active_null_rows"]
    summary = data["active_null_summary"]
    lines = [
        "# N24 Iteration 3 - Active Nulls And Failure Baselines",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 3 instantiates the frozen I2 schema as active nulls. It does",
        "not expand the schema, open positive surplus/optionality evidence, or",
        "assign AB/N24-C rungs above control scope.",
        "",
        "## Active Null Matrix",
        "",
        "| Row | Null | Result | Rung Effect |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['row_id']}` | `{row['blocker_class']}` | "
            f"`{row['actual_result']}` | `{row['control_results'][0]['rung_effect']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary Counts",
            "",
            f"- Rows: `{summary['row_count']}`",
            f"- Failed closed rows: `{summary['failed_closed_rows']}`",
            f"- Failed open rows: `{summary['failed_open_rows']}`",
            f"- Positive abundance evidence opened: `{str(summary['positive_abundance_evidence_opened']).lower()}`",
            "",
            "## Blocker Families",
            "",
            "| Family | Nulls |",
            "| --- | --- |",
        ]
    )
    for family, ids in data["active_null_grouping"].items():
        lines.append(f"| `{family}` | `{', '.join(ids)}` |")
    lines.extend(
        [
            "",
            "## Control Alias Map",
            "",
            "| Null | Canonical Control | Reason |",
            "| --- | --- | --- |",
        ]
    )
    for item in data["control_alias_map"]:
        lines.append(
            f"| `{item['null_id']}` | `{item['canonical_control_id']}` | "
            f"{item['control_alias_reason']} |"
        )
    lines.extend(
        [
            "",
            "## Status Semantics",
            "",
            "`failed_closed` means the false-positive blocker triggered and the",
            "unsafe/null claim was rejected. It satisfies the negative-control",
            "gate; it does not automatically demote future positive rows.",
            "",
            "These rows are active-null fixtures only:",
            "`trace_admissibility = active_null_fixture_only_not_positive_evidence`,",
            "`positive_evidence_admissible = false`, and",
            "`control_execution_kind = schema_instantiation_only`.",
            "",
            "The N24-C ceiling after I3 is",
            "`N24-C1_active_null_control_discipline_established`; no final",
            "closeout rung is assigned.",
            "",
            "## Row Field Policy",
            "",
            "I3 rows use all `103` I2 candidate fields plus a declared active-null",
            "metadata extension set. A validation check requires each row's field",
            "set to equal `I2 required fields U active_null_extension_fields`.",
            "",
            "## Geometric Interpretation",
            "",
        ]
    )
    for row in rows:
        lines.append(f"- `{row['scenario_id']}`: {row['geometric_failure_reading']}")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for item in data["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I3 supports only fail-closed false-positive rejection discipline. It",
            "does not support surplus-supported optionality, abundance, reward",
            "maximization, semantic choice, agency, native support, sentience,",
            "Phase 8, or ant-ecology implementation.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    if payload["failed_checks"]:
        raise SystemExit(f"failed checks: {payload['failed_checks']}")


if __name__ == "__main__":
    main()
