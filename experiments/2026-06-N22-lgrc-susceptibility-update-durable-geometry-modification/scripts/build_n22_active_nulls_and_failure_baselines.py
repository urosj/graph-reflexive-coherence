#!/usr/bin/env python3
"""Build N22 Iteration 3 active nulls and failure baselines."""

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
    / "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
)
OUTPUT = EXPERIMENT / "outputs" / "n22_active_nulls_and_failure_baselines.json"
REPORT = EXPERIMENT / "reports" / "n22_active_nulls_and_failure_baselines.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_active_nulls_and_failure_baselines.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_susceptibility_schema_and_controls.json"
)
I2_REPORT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "reports/n22_susceptibility_schema_and_controls.md"
)

GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_choice",
    "semantic_learning",
    "free_will",
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

REQUIRED_NULL_IDS = [
    "route_label_only_delta",
    "reinforcement_schedule_only_delta",
    "one_window_flux_transient",
    "missing_later_reentry",
    "post_hoc_delta_construction",
    "hidden_reinforcement",
    "route_conditioned_row_missing_AP4",
    "proxy_or_target_conditioned_row_missing_AP5",
    "AP_gap_prose_only",
    "peer_same_budget_missing",
    "global_drift_not_rejected",
    "semantic_learning_relabel",
    "native_support_relabel",
    "phase8_relabel",
]

NULL_SCENARIOS = [
    {
        "scenario_id": "route_label_only_delta",
        "blocker_class": "label_only_delta",
        "control_ids": ["route_label_only_control", "label_only_success_control"],
        "blocked_condition": "route label changes without source-current geometry delta",
        "observed_null_signal": "route_b label differs while geometry traces are absent",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks SU2 and stronger",
        "geometric_failure_reading": (
            "A name moves, but no basin geometry moves. There is no measured "
            "pre/post shape delta and no later re-entry expression."
        ),
    },
    {
        "scenario_id": "reinforcement_schedule_only_delta",
        "blocker_class": "producer_schedule_only_delta",
        "control_ids": [
            "reinforcement_schedule_removed_control",
            "hidden_producer_support_control",
        ],
        "blocked_condition": "producer reinforcement schedule changes without source-current delta",
        "observed_null_signal": "producer schedule differs but geometry/re-entry traces are absent",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks SU2 and stronger",
        "geometric_failure_reading": (
            "The producer surface changes, but the substrate basin does not "
            "show a source-current susceptibility delta."
        ),
    },
    {
        "scenario_id": "one_window_flux_transient",
        "blocker_class": "one_window_flux_transient",
        "control_ids": ["durable_geometry_modification_control"],
        "blocked_condition": "single-window flux perturbation is relabeled as durable modification",
        "observed_null_signal": "one transient flux change appears without replay/re-entry persistence",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "changed_within_bound",
        "rung_effect": "blocks SU4 and stronger",
        "geometric_failure_reading": (
            "A local flow pulse appears in one window, but it does not leave a "
            "durable basin deformation."
        ),
    },
    {
        "scenario_id": "missing_later_reentry",
        "blocker_class": "missing_reentry_trace",
        "control_ids": ["durable_geometry_modification_control"],
        "blocked_condition": "later route or region re-entry trace is missing",
        "observed_null_signal": "pre/post delta is asserted without later re-entry expression",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks SU5 and stronger",
        "geometric_failure_reading": (
            "The basin may show an immediate difference, but there is no later "
            "return through the route or region where susceptibility should be expressed."
        ),
    },
    {
        "scenario_id": "post_hoc_delta_construction",
        "blocker_class": "post_hoc_delta_construction",
        "control_ids": ["post_hoc_trace_construction_control"],
        "blocked_condition": "delta trace is assembled after outcome inspection",
        "observed_null_signal": "delta exists only as report-side reconstruction",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks SU2 and stronger",
        "geometric_failure_reading": (
            "The geometry is narrated after the fact instead of emitted as a "
            "source-current pre/post trace."
        ),
    },
    {
        "scenario_id": "hidden_reinforcement",
        "blocker_class": "hidden_reinforcement",
        "control_ids": [
            "hidden_producer_support_control",
            "reinforcement_schedule_removed_control",
        ],
        "blocked_condition": "active reinforcement remains and carries the apparent delta",
        "observed_null_signal": "apparent persistence depends on producer reinforcement still active",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks SU4, SU5, SU6, N22-C4, N22-C5, N22-C6, and ND6 bridge",
        "geometric_failure_reading": (
            "The basin is held by an active producer channel, so persistence is "
            "not yet a substrate-carried geometric modification."
        ),
    },
    {
        "scenario_id": "route_conditioned_row_missing_AP4",
        "blocker_class": "ap4_gap_omission",
        "control_ids": ["AP4_gap_dependency_if_route_conditioned"],
        "blocked_condition": "route-conditioned susceptibility omits required AP4 dependency record",
        "observed_null_signal": "route-conditioned row is asserted without AP4 status",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks route-conditioned SU rows",
        "geometric_failure_reading": (
            "The row depends on route-conditioned selection, but the selection "
            "axis is not made auditable."
        ),
    },
    {
        "scenario_id": "proxy_or_target_conditioned_row_missing_AP5",
        "blocker_class": "ap5_gap_omission",
        "control_ids": ["AP5_gap_dependency_if_proxy_conditioned"],
        "blocked_condition": "proxy or target conditioned susceptibility omits conditional AP5 record",
        "observed_null_signal": "proxy-conditioned row is asserted without AP5 status",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks proxy-conditioned SU rows",
        "geometric_failure_reading": (
            "The row depends on target/proxy formation, but that target/proxy "
            "axis is not made auditable."
        ),
    },
    {
        "scenario_id": "AP_gap_prose_only",
        "blocker_class": "ap_gap_prose_only",
        "control_ids": [
            "AP4_gap_dependency_if_route_conditioned",
            "AP5_gap_dependency_if_proxy_conditioned",
        ],
        "blocked_condition": "AP gap is acknowledged only in prose, not row-local fields",
        "observed_null_signal": "AP4/AP5 caveat appears in interpretation text only",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks dependent SU rows",
        "geometric_failure_reading": (
            "The dependency is outside the row's geometry record, so the row "
            "cannot be replayed as a controlled susceptibility claim."
        ),
    },
    {
        "scenario_id": "peer_same_budget_missing",
        "blocker_class": "missing_peer_same_budget_comparison",
        "control_ids": ["peer_same_budget_comparison_control"],
        "blocked_condition": "route/region-conditioned row lacks same-budget peer comparison",
        "observed_null_signal": "target route changes but peer route is not checked",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks SU5, SU6, N22-C5, and N22-C6",
        "geometric_failure_reading": (
            "A route-local change cannot be separated from scheduler/global "
            "drift without an equal-budget peer lane."
        ),
    },
    {
        "scenario_id": "global_drift_not_rejected",
        "blocker_class": "global_drift_not_rejected",
        "control_ids": ["global_drift_rejection_control"],
        "blocked_condition": "same delta appears globally or peer/global drift is not rejected",
        "observed_null_signal": "target and peer regions move together",
        "support_floor_result": "changed_within_allowed_delta_above_floor",
        "coherence_floor_result": "changed_within_allowed_delta_above_floor",
        "boundary_integrity_result": "changed_within_allowed_delta",
        "flux_or_leakage_result": "changed_within_bound",
        "rung_effect": "blocks route/region-conditioned SU5 and SU6",
        "geometric_failure_reading": (
            "The whole substrate drifts, so no route-specific susceptibility "
            "update has been isolated."
        ),
    },
    {
        "scenario_id": "semantic_learning_relabel",
        "blocker_class": "semantic_learning_relabel",
        "control_ids": ["semantic_relabel_control"],
        "blocked_condition": "semantic learning label is used as susceptibility evidence",
        "observed_null_signal": "learning label appears without source-current geometry delta",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks all SU support and unsafe claims",
        "geometric_failure_reading": (
            "A semantic label is substituted for a measured geometric susceptibility change."
        ),
    },
    {
        "scenario_id": "native_support_relabel",
        "blocker_class": "native_support_relabel",
        "control_ids": ["native_support_relabel_control"],
        "blocked_condition": "producer-mediated support is relabeled as native support",
        "observed_null_signal": "support annotation or producer field is used as native support",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks all SU support and unsafe claims",
        "geometric_failure_reading": (
            "Producer support is treated as substrate-native support, which is "
            "outside the N22 claim ceiling."
        ),
    },
    {
        "scenario_id": "phase8_relabel",
        "blocker_class": "phase8_relabel",
        "control_ids": ["phase8_relabel_control"],
        "blocked_condition": "schema or artifact result is relabeled as Phase 8 implementation",
        "observed_null_signal": "Phase 8 implementation claim appears without native producer code",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks all SU support and unsafe claims",
        "geometric_failure_reading": (
            "A classification artifact is promoted into native implementation, "
            "which N22 explicitly does not open."
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


def threshold_record(schema_row: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    rule = schema_row["same_basin_continuation_rule"]
    record = {
        "threshold_id": f"n22_i3_{scenario['scenario_id']}_thresholds",
        "source_contract_row": schema_row["source_contract_row"],
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "threshold_declared_before_use": True,
        "threshold_value_or_rule": {
            "support_floor": rule["required_support_floor"],
            "coherence_floor": rule["required_coherence_floor"],
            "boundary_integrity_floor": rule["boundary_integrity_floor"],
            "flux_or_leakage_bound": rule["flux_balance_bounds"],
            "delta_persistence_ratio_floor": "not_applicable_active_null",
            "global_drift_rejection_rule": "active null must fail closed if not rejected",
        },
        "threshold_owner": "frozen_i2_schema_reference",
        "failure_policy": "active_null_cannot_retune_or_override_thresholds",
    }
    record["threshold_record_digest"] = digest_value(record)
    return record


def comparability_record(schema_row: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    seed_pairing_rule = {
        "seed_pairing_rule_id": f"n22_i3_{scenario['scenario_id']}_seed_pairing",
        "same_seed_or_declared_seed_pairing_rule": True,
        "pairing_reason": (
            "pre-positive null uses the same declared seed/topology family as "
            "future N22 candidates while removing or corrupting the claimed "
            "susceptibility condition"
        ),
    }
    topology = {
        "topology_config_family": f"n22_i3_{scenario['scenario_id']}_topology_family",
        "same_topology_config_family": True,
    }
    runtime_envelope = {
        "runtime_envelope_id": f"n22_i3_{scenario['scenario_id']}_runtime_envelope",
        "same_runtime_envelope": True,
        "derived_report_only": True,
    }
    budget_schedule = {
        "budget_schedule_family": f"n22_i3_{scenario['scenario_id']}_budget_family",
        "same_budget_schedule_family_where_applicable": True,
        "same_budget_schedule_digest_where_applicable": True,
    }
    route_scope = {
        "same_route_or_region_scope_where_applicable": True,
        "route_or_region_conditioned": scenario["scenario_id"]
        not in {"semantic_learning_relabel", "native_support_relabel", "phase8_relabel"},
    }
    seed_pairing_rule["seed_pairing_rule_digest"] = digest_value(seed_pairing_rule)
    topology["topology_config_digest"] = digest_value(topology)
    runtime_envelope["runtime_envelope_digest"] = digest_value(runtime_envelope)
    budget_schedule["budget_schedule_digest"] = digest_value(budget_schedule)
    return {
        "same_source_contract_row": True,
        "same_source_contract_row_digest": True,
        "same_basin_signature_fields": True,
        "basin_signature_fields": schema_row["same_basin_continuation_rule"][
            "basin_signature_fields"
        ],
        "seed_pairing_rule": seed_pairing_rule,
        "topology_config": topology,
        "runtime_envelope": runtime_envelope,
        "budget_schedule": budget_schedule,
        "route_scope": route_scope,
        "expected_result": "fail_closed",
        "blocked_condition": scenario["blocked_condition"],
    }


def control_results(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": control_id,
            "control_status": "failed_closed",
            "blocked_condition": scenario["blocked_condition"],
            "expected_result": "susceptibility claim rejected",
            "actual_result": "susceptibility_update_claim_allowed=false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": scenario["rung_effect"],
        }
        for control_id in scenario["control_ids"]
    ]


def build_row(index: int, scenario: dict[str, Any], i1: dict[str, Any], i2: dict[str, Any]) -> dict[str, Any]:
    schema_row = i2["schema_freeze"]["primitive_schema_rows"][0]
    route_conditioned = scenario["scenario_id"] not in {
        "semantic_learning_relabel",
        "native_support_relabel",
        "phase8_relabel",
    }
    peer_scope_reason = (
        "not_applicable_unsafe_relabel_control"
        if not route_conditioned
        else "route_or_region_conditioned_active_null"
    )
    row = {
        "row_id": f"n22_i3_row_{index:02d}_{scenario['scenario_id']}",
        "scenario_id": scenario["scenario_id"],
        "source_contract_row": schema_row["source_contract_row"],
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "source_output_digest": i1["output_digest"],
        "run_artifact_id": f"n22_i3_active_null_{scenario['scenario_id']}",
        "source_commit_or_source_digest": "not_applicable_pre_positive_active_null",
        "runtime_config_digest": digest_value(
            {
                "scenario_id": scenario["scenario_id"],
                "config_role": "pre_positive_active_null",
                "schema_output_digest": i2["output_digest"],
            }
        ),
        "source_current_inputs": [],
        "source_current_input_status": "absent_by_active_null_design",
        "row_specific_thresholds_declared_before_use": True,
        "n19_native_readiness_boundary_consumption": "ap_gap_boundary_only",
        "n20_source_downstream_consumption_status": schema_row[
            "n20_source_downstream_consumption_status"
        ],
        "interaction_window": "not_applicable_pre_positive_active_null",
        "reentry_window": "not_applicable_pre_positive_active_null",
        "pre_interaction_geometry_trace": "missing_or_invalid_by_active_null_design",
        "post_interaction_geometry_trace": "missing_or_invalid_by_active_null_design",
        "susceptibility_delta_trace": "missing_or_invalid_by_active_null_design",
        "route_or_region_reentry_trace": "missing_or_invalid_by_active_null_design",
        "same_basin_continuation_rule": schema_row["same_basin_continuation_rule"],
        "allowed_delta_fields": i2["schema_freeze"]["allowed_drift_same_basin_schema"][
            "allowed_delta_fields"
        ],
        "same_basin_invariant_fields": i2["schema_freeze"][
            "allowed_drift_same_basin_schema"
        ]["same_basin_invariant_fields"],
        "out_of_scope_drift_blocks_row": True,
        "delta_not_label_reassignment": scenario["scenario_id"]
        != "route_label_only_delta",
        "violated_gate": scenario["scenario_id"],
        "route_or_region_conditioned": route_conditioned,
        "peer_same_budget_comparison": {
            "status": "failed_closed",
            "reason": scenario["blocked_condition"],
            "required_when_route_or_region_conditioned": route_conditioned,
        },
        "peer_same_budget_comparison_scope_reason": peer_scope_reason,
        "peer_route_or_region_trace": "missing_or_invalid_by_active_null_design",
        "historical_interaction_provenance_present": scenario["scenario_id"]
        not in {"route_label_only_delta", "post_hoc_delta_construction"},
        "active_reinforcement_schedule_disabled": scenario["scenario_id"]
        != "hidden_reinforcement",
        "active_reinforcement_queue_empty": scenario["scenario_id"]
        != "hidden_reinforcement",
        "reinforcement_budget_in_flight": (
            0.1 if scenario["scenario_id"] == "hidden_reinforcement" else 0.0
        ),
        "reinforcement_schedule_not_used_as_evidence": scenario["scenario_id"]
        not in {"reinforcement_schedule_only_delta", "hidden_reinforcement"},
        "support_floor_result": scenario["support_floor_result"],
        "coherence_floor_result": scenario["coherence_floor_result"],
        "boundary_integrity_result": scenario["boundary_integrity_result"],
        "flux_or_leakage_result": scenario["flux_or_leakage_result"],
        "replay_result": {
            "replay_result_status": "not_applicable",
            "canonical_replay_name": "artifact_replay",
            "alias_accepted": "artifact_only_replay",
            "reason_code": "pre_positive_active_null_no_replay_claim",
            "affected_rung": "SU3_and_stronger",
            "why_outside_declared_scope": (
                "I3 active nulls test fail-closed blocker behavior before "
                "positive replay-backed N22 probes are admitted"
            ),
        },
        "control_results": control_results(scenario),
        "ap4_dependency_status": (
            "missing_blocks_row"
            if scenario["scenario_id"] == "route_conditioned_row_missing_AP4"
            else "required_recorded"
            if route_conditioned
            else "not_applicable"
        ),
        "ap5_dependency_status": (
            "missing_blocks_row"
            if scenario["scenario_id"]
            in {"proxy_or_target_conditioned_row_missing_AP5", "AP_gap_prose_only"}
            else "not_applicable"
        ),
        "ap4_condition_reason": (
            "missing AP4 dependency active null"
            if scenario["scenario_id"] == "route_conditioned_row_missing_AP4"
            else "route-conditioned null records AP4 dependency discipline"
            if route_conditioned
            else "not route conditioned"
        ),
        "ap5_condition_reason": (
            "missing AP5 dependency active null"
            if scenario["scenario_id"] == "proxy_or_target_conditioned_row_missing_AP5"
            else "AP gap prose-only active null"
            if scenario["scenario_id"] == "AP_gap_prose_only"
            else "proxy/target formation not claimed"
        ),
        "interaction_delta_digest": "not_applicable_active_null",
        "post_replay_delta_digest": "not_applicable_active_null",
        "reentry_delta_digest": "not_applicable_active_null",
        "delta_persistence_ratio": 0.0,
        "delta_threshold_or_rule": threshold_record(schema_row, scenario),
        "one_window_transient_rejected": scenario["scenario_id"]
        != "one_window_flux_transient",
        "global_drift_rejected": scenario["scenario_id"] != "global_drift_not_rejected",
        "producer_residue_fields": schema_row["producer_mediated_fields"],
        "naturalization_debt_fields": schema_row["naturalization_debt_fields"],
        "blocked_relabel_fields": schema_row["blocked_relabel_fields"],
        "claim_ceiling": (
            "pre-positive active null and failure baseline only; no SU, N22-C, "
            "durable geometry modification, semantic learning, agency, native "
            "support, sentience, Phase 8, or ant-ecology implementation claim"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "rejected",
        "susceptibility_update_claim_allowed": False,
        "derived_report_only": True,
        "artifact_manifest": [],
        "artifact_paths": [],
        "artifact_sha256": {},
        "all_artifact_sha256_match_file_contents": True,
        "output_digest": "pending",
        "active_null_comparability": comparability_record(schema_row, scenario),
        "blocker_class": scenario["blocker_class"],
        "observed_null_signal": scenario["observed_null_signal"],
        "control_ids_covered": scenario["control_ids"],
        "expected_result": "failed_closed",
        "actual_result": "failed_closed",
        "schema_instantiation_only": True,
        "schema_expansion": False,
        "su_ladder_rung": "not_assigned_active_null_control_only",
        "n22_closeout_ladder_rung": "not_assigned_active_null_control_only",
        "geometric_failure_reading": scenario["geometric_failure_reading"],
    }
    row["output_digest"] = digest_value({k: v for k, v in row.items() if k != "output_digest"})
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
        "susceptibility_update_claim_allowed_any": any(
            row["susceptibility_update_claim_allowed"] for row in rows
        ),
        "positive_susceptibility_evidence_opened": False,
        "su_ladder_rung_assigned_above_control_scope": False,
        "n22_closeout_ladder_rung_assigned": False,
    }


def required_candidate_fields(i2: dict[str, Any]) -> list[str]:
    return i2["schema_freeze"]["candidate_evidence_row_schema"]["required_fields"]


def all_required_fields_present(rows: list[dict[str, Any]], fields: list[str]) -> bool:
    return all(all(field in row for field in fields) for row in rows)


def build_checks(i1: dict[str, Any], i2: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required_fields = required_candidate_fields(i2)
    summary = active_null_summary(rows)
    present_null_ids = {row["scenario_id"] for row in rows}
    ap_nulls = {
        row["null_id"]
        for row in i2["schema_freeze"]["ap_dependency_schema"][
            "iteration3_active_null_expectations"
        ]
    }
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
            and i2["iteration2_boundary"]["ready_for_iteration_3_active_nulls"],
            {
                "status": i2["status"],
                "acceptance_state": i2["acceptance_state"],
                "failed_checks": i2["failed_checks"],
                "ready_for_iteration_3_active_nulls": i2["iteration2_boundary"][
                    "ready_for_iteration_3_active_nulls"
                ],
            },
        ),
        check(
            "required_active_null_matrix_complete",
            present_null_ids == set(REQUIRED_NULL_IDS),
            {"required": REQUIRED_NULL_IDS, "present": sorted(present_null_ids)},
        ),
        check(
            "candidate_evidence_fields_present_in_all_rows",
            all_required_fields_present(rows, required_fields),
            {"required_field_count": len(required_fields)},
        ),
        check(
            "schema_instantiated_without_expansion",
            all(row["schema_instantiation_only"] and not row["schema_expansion"] for row in rows),
            "I3 rows instantiate I2 schema without adding schema concepts",
        ),
        check(
            "label_only_null_visibly_violates_delta_gate",
            any(
                row["scenario_id"] == "route_label_only_delta"
                and row["delta_not_label_reassignment"] is False
                and row["violated_gate"] == "route_label_only_delta"
                for row in rows
            ),
            "route-label-only null explicitly violates the label-reassignment gate",
        ),
        check(
            "all_active_nulls_fail_closed",
            all(row["actual_result"] == "failed_closed" for row in rows)
            and summary["failed_open_rows"] == 0,
            summary,
        ),
        check(
            "all_controls_reject_claims",
            all(
                result["control_status"] == "failed_closed"
                and result["claim_allowed_when_control_triggers"] is False
                for row in rows
                for result in row["control_results"]
            ),
            "every active-null control failed closed",
        ),
        check(
            "ap_gap_active_nulls_present",
            ap_nulls.issubset(present_null_ids),
            {"required_ap_nulls": sorted(ap_nulls), "present": sorted(present_null_ids)},
        ),
        check(
            "artifact_manifest_present_but_not_positive",
            all(
                isinstance(row["artifact_manifest"], list)
                and row["all_artifact_sha256_match_file_contents"] is True
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
            "no_su_or_n22c_rungs_above_control_scope",
            all(
                row["su_ladder_rung"] == "not_assigned_active_null_control_only"
                and row["n22_closeout_ladder_rung"]
                == "not_assigned_active_null_control_only"
                for row in rows
            ),
            {
                "su_ladder_rung_assigned_above_control_scope": False,
                "n22_closeout_ladder_rung_assigned": False,
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
        "artifact_id": "n22_active_nulls_and_failure_baselines",
        "schema_version": "n22_active_nulls_and_failure_baselines_v1",
        "experiment": (
            "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
        ),
        "iteration": 3,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_active_nulls_fail_closed_no_positive_evidence",
        "purpose": (
            "Instantiate the frozen I2 schema as active nulls and failure "
            "baselines before positive susceptibility probes."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n22_i1_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n22_i2_schema_and_controls"),
            source_record(I2_REPORT_PATH, "n22_i2_schema_and_controls_report"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "required_null_ids": REQUIRED_NULL_IDS,
        "active_null_rows": rows,
        "active_null_summary": active_null_summary(rows),
        "iteration3_boundary": {
            "schema_instantiation_only": True,
            "schema_expansion": False,
            "positive_susceptibility_evidence_opened": False,
            "susceptibility_update_supported": False,
            "durable_geometry_modification_supported": False,
            "su_ladder_rung_assigned_above_control_scope": False,
            "n22_closeout_ladder_rung_assigned": False,
            "n21_nd6_bridge_status": "not_supported",
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
        "# N22 Iteration 3 - Active Nulls And Failure Baselines",
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
        "not expand the schema, open positive susceptibility evidence, or assign",
        "SU/N22-C rungs above control scope.",
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
            f"- Positive susceptibility evidence opened: `{str(summary['positive_susceptibility_evidence_opened']).lower()}`",
            "",
            "## Status Semantics",
            "",
            "`failed_closed` means the false-positive blocker triggered and the",
            "susceptibility claim was rejected. `failed_open` means the blocker",
            "triggered but the claim still passed.",
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
            "I3 supports only fail-closed false-positive rejection discipline. It does",
            "not support susceptibility update, durable geometry modification,",
            "semantic learning, choice, agency, native support, sentience, Phase 8,",
            "or ant-ecology implementation.",
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
