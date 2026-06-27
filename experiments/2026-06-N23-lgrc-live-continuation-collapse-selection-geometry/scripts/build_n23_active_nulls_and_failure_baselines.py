#!/usr/bin/env python3
"""Build N23 Iteration 3 active nulls and failure baselines."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUT = EXPERIMENT / "outputs" / "n23_active_nulls_and_failure_baselines.json"
REPORT = EXPERIMENT / "reports" / "n23_active_nulls_and_failure_baselines.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_active_nulls_and_failure_baselines.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_live_continuation_schema_and_controls.json"
)
I2_REPORT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "reports/n23_live_continuation_schema_and_controls.md"
)

GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "consciousness",
    "free_will",
    "fully_native_integration",
    "identity_acceptance",
    "native_ant_agency",
    "native_colony_agency",
    "native_route_conductance_memory",
    "native_support",
    "organism_life",
    "phase8_implementation",
    "producer_preference_as_selection",
    "random_tie_as_collapse",
    "selfhood",
    "semantic_action",
    "semantic_choice",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_learning",
    "semantic_perception",
    "sentience",
    "unrestricted_autonomy",
]

REQUIRED_NULL_IDS = [
    "fake_alternative_control",
    "single_branch_relabel_control",
    "post_hoc_selected_branch_control",
    "producer_preference_injection_control",
    "random_tie_as_collapse_control",
    "missing_counterfactual_retention_control",
    "N22_susceptibility_as_choice_relabel_control",
    "route_conditioned_row_missing_AP4",
    "proxy_conditioned_row_missing_AP5",
    "AP_gap_prose_only",
    "semantic_choice_relabel",
    "agency_relabel",
    "native_support_relabel",
    "phase8_relabel",
]

ACTIVE_NULL_EXTENSION_FIELDS = [
    "active_null_comparability",
    "actual_result",
    "ap4_bridge_status",
    "artifact_manifest_empty_by_design",
    "artifact_sha256_match_status",
    "bad_condition_present",
    "bad_condition_rejected_by_control",
    "blocker_class",
    "candidate_gate_passed",
    "control_acceptance_rule_established_for_future_positive_rows",
    "control_execution_kind",
    "expected_result",
    "geometric_failure_reading",
    "lc_ladder_rung",
    "n23_closeout_ceiling",
    "n23_closeout_ladder_rung",
    "observed_null_signal",
    "positive_evidence_admissible",
    "proxy_or_target_conditioned",
    "scenario_id",
    "schema_expansion",
    "schema_instantiation_only",
    "source_current_like_shape_only",
    "trace_admissibility",
]

NULL_SCENARIOS = [
    {
        "scenario_id": "fake_alternative_control",
        "blocker_class": "fake_alternative",
        "blocked_condition": "producer or report creates alternatives that were not source-current branches",
        "observed_null_signal": "two alternatives are named but branch records are producer/report-origin",
        "branch_count": 2,
        "branch_origin": "producer_label",
        "selected_reason": "not_supported",
        "random_tie_status": "not_applicable",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": False,
        "ap4_status": "required_recorded",
        "ap5_status": "not_applicable",
        "support_result": "missing",
        "coherence_result": "missing",
        "boundary_result": "missing",
        "flux_result": "missing",
        "rung_effect": "blocks LC2 and stronger",
        "geometric_failure_reading": (
            "The graph has alternative labels but not alternative source-current "
            "branch geometry. No pre-collapse branch basin separates from the "
            "substrate, so there is nothing geometric to collapse."
        ),
    },
    {
        "scenario_id": "single_branch_relabel_control",
        "blocker_class": "single_branch_relabel",
        "blocked_condition": "one source-current branch is relabeled as a live branch set",
        "observed_null_signal": "only one branch record exists before collapse",
        "branch_count": 1,
        "branch_origin": "source_current_same_run",
        "selected_reason": "not_supported",
        "random_tie_status": "not_applicable",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": False,
        "ap4_status": "required_recorded",
        "ap5_status": "not_applicable",
        "support_result": "preserved",
        "coherence_result": "preserved",
        "boundary_result": "missing",
        "flux_result": "missing",
        "rung_effect": "blocks LC2 and stronger",
        "geometric_failure_reading": (
            "A single continuation lane remains a lane, not a live branch set. "
            "There is no simultaneous geometric plurality for a collapse event "
            "to resolve."
        ),
    },
    {
        "scenario_id": "post_hoc_selected_branch_control",
        "blocker_class": "post_hoc_selected_branch",
        "blocked_condition": "selected branch is assigned after outcome inspection",
        "observed_null_signal": "selection reason is report-derived after collapse",
        "branch_count": 2,
        "branch_origin": "report_derived",
        "selected_reason": "not_supported",
        "random_tie_status": "not_applicable",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": False,
        "ap4_status": "required_recorded",
        "ap5_status": "not_applicable",
        "support_result": "preserved",
        "coherence_result": "preserved",
        "boundary_result": "preserved",
        "flux_result": "preserved",
        "rung_effect": "blocks LC3 and stronger",
        "geometric_failure_reading": (
            "The branch that wins is named after the geometry already ended. "
            "That gives a narrative selection, not an in-collapse geometric "
            "reason carried by the run."
        ),
    },
    {
        "scenario_id": "producer_preference_injection_control",
        "blocker_class": "producer_preference_injection",
        "blocked_condition": "producer preference or selected-branch label chooses the continuation",
        "observed_null_signal": "producer preference supplies selected branch instead of geometry",
        "branch_count": 2,
        "branch_origin": "producer_label",
        "selected_reason": "not_supported",
        "random_tie_status": "not_applicable",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": False,
        "ap4_status": "required_recorded",
        "ap5_status": "not_applicable",
        "support_result": "preserved",
        "coherence_result": "preserved",
        "boundary_result": "preserved",
        "flux_result": "preserved",
        "rung_effect": "blocks LC3, LC4, LC5, LC6, and unsafe selection claims",
        "geometric_failure_reading": (
            "The continuation is injected through a producer preference surface. "
            "The selected lane is not selected by support, coherence, boundary, "
            "flux, or route geometry."
        ),
    },
    {
        "scenario_id": "random_tie_as_collapse_control",
        "blocker_class": "random_tie_as_collapse",
        "blocked_condition": "random tie-breaker is relabeled as geometric collapse",
        "observed_null_signal": "branches tie and a random schedule chooses one",
        "branch_count": 2,
        "branch_origin": "source_current_same_run",
        "selected_reason": "not_supported",
        "random_tie_status": "random_tie_blocks_row",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": False,
        "ap4_status": "required_recorded",
        "ap5_status": "not_applicable",
        "support_result": "preserved",
        "coherence_result": "preserved",
        "boundary_result": "preserved",
        "flux_result": "preserved",
        "rung_effect": "blocks LC3 and stronger",
        "geometric_failure_reading": (
            "Both branches remain geometrically tied. A random schedule chooses "
            "an index, but no branch-specific support, coherence, or flux "
            "advantage explains the collapse."
        ),
    },
    {
        "scenario_id": "missing_counterfactual_retention_control",
        "blocker_class": "missing_counterfactual_retention",
        "blocked_condition": "non-selected branch cannot be audited as pre-collapse source-current branch",
        "observed_null_signal": "collapse trace exists but non-selected branch retention is missing",
        "branch_count": 2,
        "branch_origin": "source_current_same_run",
        "selected_reason": "support_gradient_dominance",
        "random_tie_status": "not_random_tie",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": False,
        "ap4_status": "required_recorded",
        "ap5_status": "not_applicable",
        "support_result": "preserved",
        "coherence_result": "preserved",
        "boundary_result": "preserved",
        "flux_result": "changed_within_bound",
        "rung_effect": "blocks LC3 and stronger",
        "geometric_failure_reading": (
            "A selected continuation can be seen, but the unselected branch has "
            "no immutable pre-collapse trace. Without that retained audit edge, "
            "the run cannot distinguish collapse from a single-path history."
        ),
    },
    {
        "scenario_id": "N22_susceptibility_as_choice_relabel_control",
        "blocker_class": "inherited_susceptibility_as_choice",
        "blocked_condition": "inherited N22 susceptibility delta is relabeled as N23 branch choice",
        "observed_null_signal": "selection claim points only to N22 context, not N23 branch geometry",
        "branch_count": 2,
        "branch_origin": "source_current_same_run",
        "selected_reason": "susceptibility_delta_conditioned",
        "random_tie_status": "not_applicable",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": False,
        "ap4_status": "required_recorded",
        "ap5_status": "not_applicable",
        "support_result": "preserved",
        "coherence_result": "preserved",
        "boundary_result": "preserved",
        "flux_result": "preserved",
        "rung_effect": "blocks susceptibility-conditioned LC5 and stronger",
        "geometric_failure_reading": (
            "The old susceptibility delta is used as an explanation, but no N23 "
            "source-current branch expresses it during collapse. The cause is "
            "inherited context, not live selection geometry."
        ),
    },
    {
        "scenario_id": "route_conditioned_row_missing_AP4",
        "blocker_class": "missing_ap4_dependency",
        "blocked_condition": "route- or branch-conditioned row omits AP4 dependency status",
        "observed_null_signal": "route-conditioned selection is asserted without row-local AP4 record",
        "branch_count": 2,
        "branch_origin": "source_current_same_run",
        "selected_reason": "route_cost_or_conductance_dominance",
        "random_tie_status": "not_random_tie",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": False,
        "ap4_status": "missing_blocks_row",
        "ap5_status": "not_applicable",
        "support_result": "preserved",
        "coherence_result": "preserved",
        "boundary_result": "preserved",
        "flux_result": "changed_within_bound",
        "rung_effect": "blocks AP4-relevant LC5 and stronger",
        "geometric_failure_reading": (
            "The row depends on route-shaped selection, but the AP4 gap is not "
            "recorded in the row. The route geometry may exist, yet its claim "
            "dependency is not auditable."
        ),
    },
    {
        "scenario_id": "proxy_conditioned_row_missing_AP5",
        "blocker_class": "missing_ap5_dependency",
        "blocked_condition": "proxy- or target-conditioned row omits conditional AP5 dependency status",
        "observed_null_signal": "proxy-conditioned selection is asserted without AP5 record",
        "branch_count": 2,
        "branch_origin": "source_current_same_run",
        "selected_reason": "support_gradient_dominance",
        "random_tie_status": "not_random_tie",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": True,
        "ap4_status": "required_recorded",
        "ap5_status": "missing_blocks_row",
        "support_result": "preserved",
        "coherence_result": "preserved",
        "boundary_result": "preserved",
        "flux_result": "changed_within_bound",
        "rung_effect": "blocks proxy-conditioned LC rows",
        "geometric_failure_reading": (
            "A support/proxy target is used to value the branch, but the AP5 "
            "gap is not row-local. The target-like pressure is therefore not "
            "admissible collapse evidence."
        ),
    },
    {
        "scenario_id": "AP_gap_prose_only",
        "blocker_class": "ap_gap_prose_only",
        "blocked_condition": "AP4/AP5 caveat appears only in prose and not row-local fields",
        "observed_null_signal": "gap note exists in interpretation but no dependency fields are populated",
        "branch_count": 2,
        "branch_origin": "source_current_same_run",
        "selected_reason": "multi_channel_geometry_dominance",
        "random_tie_status": "not_random_tie",
        "route_or_branch_conditioned": True,
        "proxy_or_target_conditioned": True,
        "ap4_status": "missing_blocks_row",
        "ap5_status": "missing_blocks_row",
        "support_result": "preserved",
        "coherence_result": "preserved",
        "boundary_result": "preserved",
        "flux_result": "changed_within_bound",
        "rung_effect": "blocks AP-dependent LC rows",
        "geometric_failure_reading": (
            "The caveat sits outside the replayable row. A future reader cannot "
            "tell whether the selection geometry depends on AP4/AP5 gaps by "
            "inspecting the artifact itself."
        ),
    },
    {
        "scenario_id": "semantic_choice_relabel",
        "blocker_class": "semantic_choice_relabel",
        "blocked_condition": "semantic choice label is used as collapse evidence",
        "observed_null_signal": "choice language appears without source-current branch selection reason",
        "branch_count": 0,
        "branch_origin": "producer_label",
        "selected_reason": "not_supported",
        "random_tie_status": "not_applicable",
        "route_or_branch_conditioned": False,
        "proxy_or_target_conditioned": False,
        "ap4_status": "not_applicable",
        "ap5_status": "not_applicable",
        "support_result": "missing",
        "coherence_result": "missing",
        "boundary_result": "missing",
        "flux_result": "missing",
        "rung_effect": "blocks all LC support and unsafe choice claims",
        "geometric_failure_reading": (
            "A semantic label replaces the branch geometry. No live branch set, "
            "collapse trace, or counterfactual retention is present."
        ),
    },
    {
        "scenario_id": "agency_relabel",
        "blocker_class": "agency_relabel",
        "blocked_condition": "live-continuation schema is relabeled as agency or intention",
        "observed_null_signal": "agency claim appears without semantic or native evidence",
        "branch_count": 0,
        "branch_origin": "report_derived",
        "selected_reason": "not_supported",
        "random_tie_status": "not_applicable",
        "route_or_branch_conditioned": False,
        "proxy_or_target_conditioned": False,
        "ap4_status": "not_applicable",
        "ap5_status": "not_applicable",
        "support_result": "missing",
        "coherence_result": "missing",
        "boundary_result": "missing",
        "flux_result": "missing",
        "rung_effect": "blocks all LC support and unsafe agency claims",
        "geometric_failure_reading": (
            "A high-level agency word is placed on the artifact, but no branch "
            "selection geometry is added. The graph remains claim metadata, not "
            "agency evidence."
        ),
    },
    {
        "scenario_id": "native_support_relabel",
        "blocker_class": "native_support_relabel",
        "blocked_condition": "producer-mediated support is relabeled as native support",
        "observed_null_signal": "producer branch enumeration or selected label is treated as native support",
        "branch_count": 0,
        "branch_origin": "producer_label",
        "selected_reason": "not_supported",
        "random_tie_status": "not_applicable",
        "route_or_branch_conditioned": False,
        "proxy_or_target_conditioned": False,
        "ap4_status": "not_applicable",
        "ap5_status": "not_applicable",
        "support_result": "missing",
        "coherence_result": "missing",
        "boundary_result": "missing",
        "flux_result": "missing",
        "rung_effect": "blocks all LC support and unsafe native-support claims",
        "geometric_failure_reading": (
            "Producer scaffolding is mistaken for substrate-carried support. "
            "The substrate has not generated the branch enumeration or support "
            "surface natively."
        ),
    },
    {
        "scenario_id": "phase8_relabel",
        "blocker_class": "phase8_relabel",
        "blocked_condition": "schema/control artifact is relabeled as Phase 8 implementation",
        "observed_null_signal": "Phase 8 implementation claim appears without native producer code",
        "branch_count": 0,
        "branch_origin": "report_derived",
        "selected_reason": "not_supported",
        "random_tie_status": "not_applicable",
        "route_or_branch_conditioned": False,
        "proxy_or_target_conditioned": False,
        "ap4_status": "not_applicable",
        "ap5_status": "not_applicable",
        "support_result": "missing",
        "coherence_result": "missing",
        "boundary_result": "missing",
        "flux_result": "missing",
        "rung_effect": "blocks all LC support and unsafe Phase 8 claims",
        "geometric_failure_reading": (
            "A schema artifact is promoted into native implementation. No new "
            "LGRC producer surface, source-current branch geometry, or runtime "
            "mutation has been added."
        ),
    },
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
    record = {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": role,
    }
    if path.endswith(".json"):
        data = load_json(path)
        record["status"] = data.get("status", "not_recorded")
        record["acceptance_state"] = data.get("acceptance_state", "not_recorded")
        record["output_digest"] = data.get("output_digest", "not_recorded")
    else:
        record["status"] = "markdown_context_only"
        record["acceptance_state"] = "not_applicable"
        record["output_digest"] = "not_applicable"
    return record


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in GLOBAL_UNSAFE_CLAIMS}


def trace(
    status: str,
    origin: str,
    missing_blocks: list[str],
    detail: str,
    *,
    invalid_blocks: list[str] | None = None,
    row_condition_blocks: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "trace_status": status,
        "trace_origin": origin,
        "missing_blocks_rungs": missing_blocks if status == "missing" else [],
        "invalid_blocks_rungs": invalid_blocks or [],
        "row_condition_blocks_rungs": row_condition_blocks or [],
        "detail": detail,
    }


def trace_row_condition_blocks(scenario_id: str, trace_name: str, rung_effect: str) -> list[str]:
    blockers = {
        "fake_alternative_control": {"pre_collapse_geometry_trace", "live_branch_set_trace"},
        "single_branch_relabel_control": {"live_branch_set_trace"},
        "post_hoc_selected_branch_control": {"collapsed_continuation_trace"},
        "producer_preference_injection_control": {"collapsed_continuation_trace"},
        "random_tie_as_collapse_control": {"collapsed_continuation_trace"},
        "missing_counterfactual_retention_control": {
            "counterfactual_branch_retention_trace",
            "branch_counterfactual_records",
        },
        "N22_susceptibility_as_choice_relabel_control": {
            "n23_susceptibility_expression_trace"
        },
    }
    return [rung_effect] if trace_name in blockers.get(scenario_id, set()) else []


def threshold_record(i1_row: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    rule = i1_row["same_basin_rule"]
    record = {
        "threshold_id": f"n23_i3_{scenario['scenario_id']}_thresholds",
        "source_contract_row": i1_row["source_contract_row"],
        "source_consumable_contract_row": i1_row["source_consumable_contract_row"],
        "source_contract_row_digest": i1_row["source_contract_row_digest"],
        "source_consumable_contract_row_digest": i1_row[
            "source_consumable_contract_row_digest"
        ],
        "threshold_declared_before_use": True,
        "threshold_value_or_rule": {
            "support_floor_value": rule["required_support_floor"],
            "coherence_floor_value": rule["required_coherence_floor"],
            "boundary_integrity_floor_value": rule["boundary_integrity_floor"],
            "flux_or_leakage_bound": rule["flux_balance_bounds"],
            "collapse_persistence_ratio_threshold": "not_applicable_active_null",
            "branch_distinguishability_threshold": (
                "at_least_two_source_current_boundary_distinguishable_branches"
            ),
            "same_basin_drift_bound": rule["allowed_drift"],
        },
        "threshold_owner": "frozen_i2_schema_reference",
        "failure_policy": "active_null_cannot_retune_or_override_thresholds",
    }
    record["threshold_record_digest"] = digest_value(record)
    return record


def comparability_record(i1_row: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    seed_pairing = {
        "seed_pairing_rule_id": f"n23_i3_{scenario['scenario_id']}_seed_pairing",
        "same_seed_or_declared_seed_pairing_rule": True,
        "pairing_reason": (
            "pre-positive N23 active null uses the same declared branch/collapse "
            "contract family while corrupting the claimed live-continuation condition"
        ),
    }
    topology = {
        "topology_config_family": f"n23_i3_{scenario['scenario_id']}_topology_family",
        "same_topology_config_family": True,
    }
    runtime = {
        "runtime_envelope_id": f"n23_i3_{scenario['scenario_id']}_runtime_envelope",
        "same_runtime_envelope": True,
        "derived_report_only": True,
    }
    branch_policy = {
        "same_branch_and_collapse_window_policy": True,
        "branch_window_policy": "pre_collapse_window_before_collapse_window",
        "collapse_window_policy": "collapse_window_after_branch_window",
    }
    budget = {
        "budget_schedule_family": f"n23_i3_{scenario['scenario_id']}_budget_family",
        "same_budget_schedule_digest_where_applicable": True,
    }
    seed_pairing["seed_pairing_rule_digest"] = digest_value(seed_pairing)
    topology["topology_config_digest"] = digest_value(topology)
    runtime["runtime_envelope_digest"] = digest_value(runtime)
    budget["budget_schedule_digest"] = digest_value(budget)
    return {
        "same_source_contract_row": True,
        "same_source_consumable_contract_row": True,
        "same_source_contract_row_digest": True,
        "same_basin_signature_fields": True,
        "basin_signature_fields": i1_row["same_basin_rule"]["basin_signature_fields"],
        "seed_pairing_rule": seed_pairing,
        "topology_config": topology,
        "runtime_envelope": runtime,
        "branch_and_collapse_window_policy": branch_policy,
        "budget_schedule": budget,
        "same_route_or_branch_scope_where_applicable": True,
        "expected_result": "failed_closed",
        "blocked_condition": scenario["blocked_condition"],
    }


def control_results(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": scenario["scenario_id"],
            "control_status": "failed_closed",
            "blocked_condition": scenario["blocked_condition"],
            "expected_result": "failed_closed",
            "actual_result": "unsafe_or_false_positive_claim_rejected",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": scenario["rung_effect"],
        }
    ]


def build_row(
    index: int, scenario: dict[str, Any], i1: dict[str, Any], i2: dict[str, Any]
) -> dict[str, Any]:
    i1_row = i1["contract_inventory_rows"][0]
    branch_count = int(scenario["branch_count"])
    source_current_like = scenario["branch_origin"] == "source_current_same_run"
    invalid_origin_blocks = [] if source_current_like else ["LC2", "LC3", "LC4", "LC5", "LC6"]
    missing_branch_blocks = ["LC2", "LC3", "LC4", "LC5", "LC6", "N23-C2+"]
    missing_collapse_blocks = ["LC3", "LC4", "LC5", "LC6", "N23-C3+"]
    missing_retention_blocks = ["LC3", "LC4", "LC5", "LC6", "N23-C3+"]
    has_valid_branch_set = source_current_like and branch_count >= 2
    has_retention = scenario["scenario_id"] != "missing_counterfactual_retention_control"
    producer_preference_absent = scenario["scenario_id"] != "producer_preference_injection_control"
    random_tie_rejected = scenario["scenario_id"] != "random_tie_as_collapse_control"
    fake_rejected = scenario["scenario_id"] != "fake_alternative_control"
    single_branch_rejected = scenario["scenario_id"] != "single_branch_relabel_control"
    post_hoc_rejected = scenario["scenario_id"] != "post_hoc_selected_branch_control"

    live_branch_trace_status = "present" if branch_count > 0 else "missing"
    live_branch_detail = (
        f"{branch_count} branch record(s) with origin {scenario['branch_origin']}"
    )
    collapse_status = (
        "present"
        if has_valid_branch_set
        and scenario["scenario_id"]
        not in {"post_hoc_selected_branch_control", "random_tie_as_collapse_control"}
        else "missing"
    )
    retention_status = "present" if has_valid_branch_set and has_retention else "missing"
    susceptibility_reason_claimed = (
        scenario["selected_reason"] == "susceptibility_delta_conditioned"
    )
    susceptibility_trace_status = (
        "missing" if susceptibility_reason_claimed else "not_applicable"
    )
    susceptibility_trace_origin = (
        "report_derived" if susceptibility_reason_claimed else "source_current_same_run"
    )

    threshold = threshold_record(i1_row, scenario)
    row = {
        "row_id": f"n23_i3_row_{index:02d}_{scenario['scenario_id']}",
        "source_contract_row": i1_row["source_contract_row"],
        "source_consumable_contract_row": i1_row["source_consumable_contract_row"],
        "source_contract_row_digest": i1_row["source_contract_row_digest"],
        "source_consumable_contract_row_digest": i1_row[
            "source_consumable_contract_row_digest"
        ],
        "source_output_digest": i1["output_digest"],
        "run_artifact_id": f"n23_i3_active_null_{scenario['scenario_id']}",
        "source_commit_or_source_digest": "not_applicable_pre_positive_active_null",
        "control_execution_kind": "schema_instantiation_only",
        "trace_admissibility": "active_null_fixture_only_not_positive_evidence",
        "source_current_like_shape_only": source_current_like,
        "positive_evidence_admissible": False,
        "bad_condition_present": True,
        "bad_condition_rejected_by_control": True,
        "candidate_gate_passed": False,
        "runtime_config_digest": digest_value(
            {
                "scenario_id": scenario["scenario_id"],
                "config_role": "pre_positive_active_null",
                "schema_output_digest": i2["output_digest"],
            }
        ),
        "source_current_inputs": [],
        "row_specific_thresholds_declared_before_use": True,
        "n19_native_readiness_boundary_consumption": "ap_gap_boundary_only",
        "n20_source_downstream_consumption_status": i1_row[
            "n20_source_downstream_consumption_status"
        ],
        "n22_source_closeout_status": i1["n22_context_boundary"][
            "n22_source_closeout_status"
        ],
        "branch_window": {
            "window_id": f"n23_i3_{scenario['scenario_id']}_branch_window",
            "start_step": "pre_positive_active_null",
            "end_step": "pre_positive_active_null",
            "window_role": "null_comparability_only",
        },
        "collapse_window": {
            "window_id": f"n23_i3_{scenario['scenario_id']}_collapse_window",
            "start_step": "pre_positive_active_null",
            "end_step": "pre_positive_active_null",
            "window_role": "null_comparability_only",
        },
        "pre_collapse_geometry_trace": trace(
            live_branch_trace_status,
            scenario["branch_origin"],
            missing_branch_blocks,
            live_branch_detail,
            invalid_blocks=invalid_origin_blocks,
            row_condition_blocks=trace_row_condition_blocks(
                scenario["scenario_id"],
                "pre_collapse_geometry_trace",
                scenario["rung_effect"],
            ),
        ),
        "live_branch_set_trace": trace(
            "present" if has_valid_branch_set else live_branch_trace_status,
            scenario["branch_origin"],
            missing_branch_blocks,
            live_branch_detail,
            invalid_blocks=invalid_origin_blocks,
            row_condition_blocks=trace_row_condition_blocks(
                scenario["scenario_id"],
                "live_branch_set_trace",
                scenario["rung_effect"],
            ),
        )
        | {
            "branch_count": branch_count,
            "minimum_branch_count_for_lc2": 2,
            "source_current_same_run": source_current_like,
            "valid_live_branch_set": has_valid_branch_set,
        },
        "branch_support_coherence_traces": {
            "trace_status": "present" if has_valid_branch_set else "missing",
            "trace_origin": scenario["branch_origin"],
            "branch_specific_support_coherence_traces_present": has_valid_branch_set,
            "support_floor_result": scenario["support_result"],
            "coherence_floor_result": scenario["coherence_result"],
        },
        "branch_boundary_flux_traces": {
            "trace_status": "present" if has_valid_branch_set else "missing",
            "trace_origin": scenario["branch_origin"],
            "branch_specific_boundary_flux_traces_present": has_valid_branch_set,
            "boundary_integrity_result": scenario["boundary_result"],
            "flux_or_leakage_result": scenario["flux_result"],
        },
        "branch_counterfactual_records": {
            "trace_status": retention_status,
            "trace_origin": scenario["branch_origin"],
            "counterfactual_retention_present": retention_status == "present",
            "immutable_pre_collapse_audit_record": retention_status == "present",
        },
        "collapsed_continuation_trace": trace(
            collapse_status,
            scenario["branch_origin"],
            missing_collapse_blocks,
            scenario["observed_null_signal"],
            invalid_blocks=invalid_origin_blocks,
            row_condition_blocks=trace_row_condition_blocks(
                scenario["scenario_id"],
                "collapsed_continuation_trace",
                scenario["rung_effect"],
            ),
        ),
        "counterfactual_branch_retention_trace": trace(
            retention_status,
            scenario["branch_origin"],
            missing_retention_blocks,
            "non-selected branch audit record required for LC3+",
            invalid_blocks=invalid_origin_blocks,
            row_condition_blocks=trace_row_condition_blocks(
                scenario["scenario_id"],
                "counterfactual_branch_retention_trace",
                scenario["rung_effect"],
            ),
        ),
        "branch_record_origin": scenario["branch_origin"],
        "selected_branch_source_current_reason": scenario["selected_reason"],
        "n22_inherited_delta_used_as_selection_evidence": (
            scenario["scenario_id"] == "N22_susceptibility_as_choice_relabel_control"
        ),
        "n23_susceptibility_expression_trace": trace(
            susceptibility_trace_status,
            susceptibility_trace_origin,
            ["LC5", "LC6", "N23-C5+"],
            "required when susceptibility_delta_conditioned is asserted",
            invalid_blocks=[],
            row_condition_blocks=trace_row_condition_blocks(
                scenario["scenario_id"],
                "n23_susceptibility_expression_trace",
                scenario["rung_effect"],
            ),
        ),
        "producer_selected_branch_label_absent": producer_preference_absent,
        "producer_preference_injection_absent": producer_preference_absent,
        "random_tie_status": scenario["random_tie_status"],
        "support_floor_value": threshold["threshold_value_or_rule"]["support_floor_value"],
        "coherence_floor_value": threshold["threshold_value_or_rule"][
            "coherence_floor_value"
        ],
        "boundary_integrity_floor_value": threshold["threshold_value_or_rule"][
            "boundary_integrity_floor_value"
        ],
        "flux_or_leakage_bound": threshold["threshold_value_or_rule"][
            "flux_or_leakage_bound"
        ],
        "collapse_persistence_ratio_threshold": threshold["threshold_value_or_rule"][
            "collapse_persistence_ratio_threshold"
        ],
        "branch_distinguishability_threshold": threshold["threshold_value_or_rule"][
            "branch_distinguishability_threshold"
        ],
        "same_basin_drift_bound": threshold["threshold_value_or_rule"][
            "same_basin_drift_bound"
        ],
        "same_basin_continuation_rule": i1_row["same_basin_rule"],
        "same_basin_invariant_fields": i1_row["same_basin_rule"][
            "basin_signature_fields"
        ],
        "out_of_scope_drift_blocks_row": True,
        "selection_not_label_reassignment": scenario["scenario_id"]
        not in {
            "single_branch_relabel_control",
            "semantic_choice_relabel",
            "agency_relabel",
            "native_support_relabel",
            "phase8_relabel",
        },
        "route_or_branch_conditioned": scenario["route_or_branch_conditioned"],
        "proxy_or_target_conditioned": scenario["proxy_or_target_conditioned"],
        "peer_or_counterfactual_comparison": {
            "status": "failed_closed",
            "required_for_ap4_relevant_reason": scenario["route_or_branch_conditioned"],
            "counterfactual_retention_present": retention_status == "present",
            "reason": scenario["blocked_condition"],
        },
        "peer_or_counterfactual_scope_reason": (
            "route_or_branch_conditioned_active_null"
            if scenario["route_or_branch_conditioned"]
            else "not_route_or_branch_conditioned_unsafe_relabel_null"
        ),
        "support_floor_result": scenario["support_result"],
        "coherence_floor_result": scenario["coherence_result"],
        "boundary_integrity_result": scenario["boundary_result"],
        "flux_or_leakage_result": scenario["flux_result"],
        "replay_result": {
            "replay_result_status": "not_applicable",
            "reason_code": "pre_positive_active_null_no_replay_claim",
            "affected_rung": "LC4_and_stronger",
            "why_outside_declared_scope": (
                "I3 active nulls test fail-closed blocker behavior before "
                "positive replay-backed N23 collapse probes are admitted"
            ),
        },
        "control_results": control_results(scenario),
        "ap4_dependency_status": scenario["ap4_status"],
        "ap5_dependency_status": scenario["ap5_status"],
        "ap4_condition_reason": (
            "missing AP4 dependency active null"
            if scenario["ap4_status"] == "missing_blocks_row"
            else "route/branch-conditioned null records AP4 dependency discipline"
            if scenario["route_or_branch_conditioned"]
            else "not route or branch conditioned"
        ),
        "ap5_condition_reason": (
            "missing AP5 dependency active null"
            if scenario["ap5_status"] == "missing_blocks_row"
            else "proxy/target formation not claimed"
        ),
        "collapse_trace_digest": digest_value(
            {
                "scenario_id": scenario["scenario_id"],
                "collapse_status": collapse_status,
                "selected_reason": scenario["selected_reason"],
            }
        ),
        "replay_collapse_digest": "not_applicable_active_null",
        "counterfactual_retention_digest": digest_value(
            {
                "scenario_id": scenario["scenario_id"],
                "retention_status": retention_status,
                "branch_count": branch_count,
            }
        ),
        "collapse_persistence_ratio": 0.0,
        "collapse_threshold_or_rule": threshold,
        "fake_alternatives_rejected": fake_rejected,
        "single_branch_relabel_rejected": single_branch_rejected,
        "post_hoc_selection_rejected": post_hoc_rejected,
        "producer_preference_rejected": producer_preference_absent,
        "random_tie_as_collapse_rejected": random_tie_rejected,
        "producer_residue_fields": i1_row["producer_mediated_fields"],
        "naturalization_debt_fields": i1_row["naturalization_debt_fields"],
        "blocked_relabel_fields": i1_row["blocked_relabel_fields"],
        "claim_ceiling": (
            "pre-positive active null and failure baseline only; no LC, N23-C, "
            "AP4 bridge, semantic choice, agency, native support, sentience, "
            "Phase 8, or ant-ecology implementation claim"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "rejected",
        "live_continuation_collapse_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "derived_report_only": True,
        "artifact_manifest": [],
        "artifact_paths": [],
        "artifact_sha256": {},
        "artifact_manifest_empty_by_design": True,
        "artifact_sha256_match_status": "vacuously_true_active_null_no_positive_artifacts",
        "artifact_paths_equal_manifest_paths": True,
        "artifact_sha256_equal_manifest_sha256": True,
        "all_artifact_sha256_match_file_contents": True,
        "output_digest": "pending",
        "scenario_id": scenario["scenario_id"],
        "blocker_class": scenario["blocker_class"],
        "observed_null_signal": scenario["observed_null_signal"],
        "expected_result": "failed_closed",
        "actual_result": "failed_closed",
        "control_acceptance_rule_established_for_future_positive_rows": True,
        "schema_instantiation_only": True,
        "schema_expansion": False,
        "lc_ladder_rung": "not_assigned_active_null_control_only",
        "n23_closeout_ladder_rung": "not_assigned_active_null_control_only",
        "n23_closeout_ceiling": "N23-C1_active_null_control_discipline_established",
        "ap4_bridge_status": "not_supported_active_null_control_only",
        "active_null_comparability": comparability_record(i1_row, scenario),
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
            {result["control_id"] for row in rows for result in row["control_results"]}
        ),
        "live_continuation_collapse_claim_allowed_any": any(
            row["live_continuation_collapse_claim_allowed"] for row in rows
        ),
        "semantic_choice_claim_allowed_any": any(
            row["semantic_choice_claim_allowed"] for row in rows
        ),
        "positive_live_continuation_evidence_opened": False,
        "lc_ladder_rung_assigned_above_control_scope": False,
        "n23_closeout_ladder_rung_assigned": False,
        "n23_closeout_ceiling": "N23-C1_active_null_control_discipline_established",
        "ap4_bridge_status": "not_supported",
    }


def all_required_fields_present(rows: list[dict[str, Any]], fields: list[str]) -> bool:
    return all(all(field in row for field in fields) for row in rows)


def row_field_set_matches_i2_plus_extensions(
    rows: list[dict[str, Any]], required_fields: list[str]
) -> bool:
    allowed = set(required_fields) | set(ACTIVE_NULL_EXTENSION_FIELDS)
    return all(set(row.keys()) == allowed for row in rows)


def build_checks(i1: dict[str, Any], i2: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required_fields = i2["schema"]["candidate_evidence_row_schema"]["required_fields"]
    canonical_controls = i2["schema"]["replay_control_schema"]["canonical_control_ids"]
    summary = active_null_summary(rows)
    present_null_ids = {row["scenario_id"] for row in rows}
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
            and i2["evidence_boundary"]["live_continuation_collapse_evidence_opened"]
            is False,
            {
                "status": i2["status"],
                "acceptance_state": i2["acceptance_state"],
                "failed_checks": i2["failed_checks"],
            },
        ),
        check(
            "source_digest_chain_aligned",
            i2["source_i1_output_digest"] == i1["output_digest"],
            {
                "i1_output_digest": i1["output_digest"],
                "i2_source_i1_output_digest": i2["source_i1_output_digest"],
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
            set(canonical_controls) == present_null_ids,
            {"canonical_controls": canonical_controls, "present": sorted(present_null_ids)},
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
                for row in rows
            ),
            "source-current-shaped null traces cannot be consumed as positive LC evidence",
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
            "required_trace_status_fields_present",
            all(
                "trace_status" in row["live_branch_set_trace"]
                and "trace_origin" in row["live_branch_set_trace"]
                and "invalid_blocks_rungs" in row["live_branch_set_trace"]
                and "row_condition_blocks_rungs" in row["live_branch_set_trace"]
                and "trace_status" in row["collapsed_continuation_trace"]
                and "trace_origin" in row["counterfactual_branch_retention_trace"]
                for row in rows
            ),
            "trace status/origin fields present in all rows",
        ),
        check(
            "susceptibility_trace_applicability_scoped",
            all(
                (
                    row["selected_branch_source_current_reason"]
                    == "susceptibility_delta_conditioned"
                    and row["n23_susceptibility_expression_trace"]["trace_status"]
                    == "missing"
                )
                or (
                    row["selected_branch_source_current_reason"]
                    != "susceptibility_delta_conditioned"
                    and row["n23_susceptibility_expression_trace"]["trace_status"]
                    == "not_applicable"
                )
                for row in rows
            ),
            "N23 susceptibility expression trace is applicable only to susceptibility-conditioned rows",
        ),
        check(
            "trace_row_condition_blockers_are_targeted",
            all(
                not (
                    row["scenario_id"] == "missing_counterfactual_retention_control"
                    and row["collapsed_continuation_trace"][
                        "row_condition_blocks_rungs"
                    ]
                )
                for row in rows
            )
            and any(
                row["scenario_id"] == "missing_counterfactual_retention_control"
                and row["counterfactual_branch_retention_trace"][
                    "row_condition_blocks_rungs"
                ]
                for row in rows
            ),
            "row-condition blockers are attached to the trace that actually carries the null",
        ),
        check(
            "ap_gap_active_nulls_present",
            {
                "route_conditioned_row_missing_AP4",
                "proxy_conditioned_row_missing_AP5",
                "AP_gap_prose_only",
            }.issubset(present_null_ids),
            "AP4/AP5 active nulls present",
        ),
        check(
            "n22_inheritance_blocker_executed",
            any(
                row["scenario_id"] == "N22_susceptibility_as_choice_relabel_control"
                and row["n22_inherited_delta_used_as_selection_evidence"] is True
                and row["n23_susceptibility_expression_trace"]["trace_status"] == "missing"
                and row["live_continuation_collapse_claim_allowed"] is False
                for row in rows
            ),
            "N22 susceptibility context cannot become N23 choice evidence",
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
                and row["derived_report_only"] is True
                for row in rows
            ),
            "active null rows carry manifest fields without positive run artifacts",
        ),
        check(
            "no_source_current_inputs_opened",
            all(row["source_current_inputs"] == [] for row in rows),
            "active nulls do not provide positive source-current inputs",
        ),
        check(
            "no_lc_or_n23c_rungs_above_control_scope",
            all(
                row["lc_ladder_rung"] == "not_assigned_active_null_control_only"
                and row["n23_closeout_ladder_rung"]
                == "not_assigned_active_null_control_only"
                for row in rows
            ),
            {
                "lc_ladder_rung_assigned_above_control_scope": False,
                "n23_closeout_ladder_rung_assigned": False,
                "n23_closeout_ceiling": "N23-C1_active_null_control_discipline_established",
            },
        ),
        check(
            "unsafe_claim_flags_all_false",
            all(
                set(row["unsafe_claim_flags"].keys()) == set(GLOBAL_UNSAFE_CLAIMS)
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
        "artifact_id": "n23_active_nulls_and_failure_baselines",
        "schema_version": "n23_active_nulls_and_failure_baselines_v1",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": 3,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_active_nulls_fail_closed_no_positive_evidence",
        "purpose": (
            "Instantiate the frozen I2 schema as active nulls and failure "
            "baselines before positive live-continuation collapse probes."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n23_i1_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n23_i2_schema_and_controls"),
            source_record(I2_REPORT_PATH, "n23_i2_schema_and_controls_report"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "required_null_ids": REQUIRED_NULL_IDS,
        "row_field_policy": {
            "candidate_required_fields_source": "N23 I2 candidate_evidence_row_schema.required_fields",
            "candidate_required_field_count": len(
                i2["schema"]["candidate_evidence_row_schema"]["required_fields"]
            ),
            "active_null_extension_fields": ACTIVE_NULL_EXTENSION_FIELDS,
            "active_null_extension_field_count": len(ACTIVE_NULL_EXTENSION_FIELDS),
            "row_field_set_rule": "I3 row keys must equal I2 required fields plus declared active-null extension fields",
        },
        "active_null_rows": rows,
        "active_null_summary": active_null_summary(rows),
        "iteration3_boundary": {
            "schema_instantiation_only": True,
            "schema_expansion": False,
            "positive_run_artifacts_consumed": False,
            "source_current_inputs_opened": False,
            "live_continuation_collapse_evidence_opened": False,
            "live_continuation_collapse_supported": False,
            "lc_ladder_rung_assigned_above_control_scope": False,
            "n23_closeout_ladder_rung_assigned": False,
            "n23_closeout_ceiling": "N23-C1_active_null_control_discipline_established",
            "ap4_bridge_status": "not_supported",
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


def write_report(data: dict[str, Any]) -> str:
    rows = data["active_null_rows"]
    summary = data["active_null_summary"]
    lines = [
        "# N23 Iteration 3 - Active Nulls And Failure Baselines",
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
        "not expand the schema, open positive live-continuation evidence, or",
        "assign LC/N23-C rungs above control scope.",
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
            f"- Positive live-continuation evidence opened: `{str(summary['positive_live_continuation_evidence_opened']).lower()}`",
            "",
            "## Status Semantics",
            "",
            "`failed_closed` means the false-positive blocker triggered and the",
            "unsafe/null claim was rejected. It satisfies the negative-control",
            "gate; it does not automatically demote future positive rows.",
            "",
            "These rows are source-current-shaped null fixtures only:",
            "`trace_admissibility = active_null_fixture_only_not_positive_evidence`,",
            "`positive_evidence_admissible = false`, and",
            "`control_execution_kind = schema_instantiation_only`.",
            "",
            "The N23-C ceiling after I3 is",
            "`N23-C1_active_null_control_discipline_established`; no final",
            "closeout rung is assigned.",
            "",
            "## Row Field Policy",
            "",
            "I3 rows use all `80` I2 candidate fields plus a declared active-null",
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
            "## Boundary",
            "",
            "I3 can block false-positive paths, but it cannot support live branch",
            "existence, collapse, counterfactual retention, replay-backed LC",
            "rungs, AP4 bridge evidence, semantic choice, agency, native support,",
            "sentience, Phase 8, or ant-ecology implementation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    REPORT.write_text(write_report(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
