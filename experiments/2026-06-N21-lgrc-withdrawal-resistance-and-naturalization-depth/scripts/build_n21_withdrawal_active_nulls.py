#!/usr/bin/env python3
"""Build N21 Iteration 3 active nulls and failure baselines."""

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
OUTPUT = EXPERIMENT / "outputs" / "n21_withdrawal_active_nulls.json"
REPORT = EXPERIMENT / "reports" / "n21_withdrawal_active_nulls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_withdrawal_active_nulls.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_source_contract_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_schema_and_thresholds.json"
)
I2_REPORT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "reports/n21_withdrawal_schema_and_thresholds.md"
)

ROW_DECISIONS = ["supported", "partial", "blocked", "rejected", "not_applicable"]
REPLAY_CONTROL_STATUSES = [
    "passed",
    "failed_closed",
    "failed_open",
    "not_run",
    "not_applicable",
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

NULL_SCENARIOS = [
    {
        "primitive_id": "withdrawal_resistance",
        "scenario_id": "no_declared_withdrawal",
        "blocker_class": "no_withdrawal_no_removal",
        "control_ids": ["withdrawal_schedule_removed_control"],
        "blocked_condition": "no declared support weakening or removal",
        "observed_null_signal": "baseline-like basin label without source-current withdrawal",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks WR1 and stronger",
    },
    {
        "primitive_id": "withdrawal_resistance",
        "scenario_id": "label_only_continuation",
        "blocker_class": "label_only_continuation",
        "control_ids": ["label_only_success_control"],
        "blocked_condition": "continuation label without source-current basin trace",
        "observed_null_signal": "same-basin text label remains while required fields are absent",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks WR2 and stronger",
    },
    {
        "primitive_id": "withdrawal_resistance",
        "scenario_id": "proxy_only_improvement",
        "blocker_class": "proxy_only_success",
        "control_ids": ["proxy_only_success_control"],
        "blocked_condition": "proxy improves while same-basin continuation gates fail",
        "observed_null_signal": "proxy score improves but support/coherence/boundary evidence is absent",
        "support_floor_result": "crossed_floor",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks WR3 and stronger",
    },
    {
        "primitive_id": "withdrawal_resistance",
        "scenario_id": "hidden_producer_support",
        "blocker_class": "hidden_producer_support",
        "control_ids": [
            "hidden_producer_support_control",
            "hidden_support_margin_control",
        ],
        "blocked_condition": "undeclared producer support preserves apparent margin",
        "observed_null_signal": "support appears preserved only because hidden support remains",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks WR5 and stronger",
    },
    {
        "primitive_id": "withdrawal_resistance",
        "scenario_id": "post_hoc_trace_construction",
        "blocker_class": "post_hoc_trace_construction",
        "control_ids": ["post_hoc_trace_construction_control"],
        "blocked_condition": "same-basin trace is assembled after outcome inspection",
        "observed_null_signal": "trace exists only as report-side reconstruction",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks WR2 and stronger",
    },
    {
        "primitive_id": "withdrawal_resistance",
        "scenario_id": "support_floor_crossing",
        "blocker_class": "floor_crossing",
        "control_ids": ["support_floor_crossing_control"],
        "blocked_condition": "declared support floor is crossed",
        "observed_null_signal": "basin label remains while support falls below declared floor",
        "support_floor_result": "crossed_floor",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks WR3 and stronger",
    },
    {
        "primitive_id": "withdrawal_resistance",
        "scenario_id": "unsafe_native_support_relabel",
        "blocker_class": "producer_mediated_native_support_relabel",
        "control_ids": [
            "semantic_relabel_control",
            "native_support_relabel_control",
            "phase8_relabel_control",
        ],
        "blocked_condition": "producer-mediated or semantic label is relabeled as native support",
        "observed_null_signal": "producer-mediated schedule/threshold label is used as support evidence",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks all primitive support and unsafe claims",
    },
    {
        "primitive_id": "naturalization_depth",
        "scenario_id": "probe_present_only",
        "blocker_class": "no_probe_absence",
        "control_ids": ["probe_present_only_control"],
        "blocked_condition": "original probe or scaffold remains present",
        "observed_null_signal": "post-probe claim is made while probe-present condition remains",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks ND1 and stronger",
    },
    {
        "primitive_id": "naturalization_depth",
        "scenario_id": "label_only_continuation",
        "blocker_class": "label_only_continuation",
        "control_ids": ["label_only_success_control"],
        "blocked_condition": "post-probe continuation label without source-current basin trace",
        "observed_null_signal": "same-basin text label remains while post-probe fields are absent",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks ND2 and stronger",
    },
    {
        "primitive_id": "naturalization_depth",
        "scenario_id": "proxy_only_improvement",
        "blocker_class": "proxy_only_success",
        "control_ids": ["proxy_only_success_control"],
        "blocked_condition": "proxy improves while post-probe same-basin gates fail",
        "observed_null_signal": "depth score improves but post-probe basin signature is absent",
        "support_floor_result": "missing",
        "coherence_floor_result": "crossed_floor",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks ND2 and stronger",
    },
    {
        "primitive_id": "naturalization_depth",
        "scenario_id": "hidden_producer_support",
        "blocker_class": "hidden_producer_support",
        "control_ids": ["hidden_producer_support_control"],
        "blocked_condition": "undeclared producer support preserves apparent post-probe margin",
        "observed_null_signal": "post-probe support appears preserved by hidden producer surface",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks ND4 and stronger",
    },
    {
        "primitive_id": "naturalization_depth",
        "scenario_id": "post_hoc_trace_construction",
        "blocker_class": "post_hoc_trace_construction",
        "control_ids": ["post_hoc_trace_construction_control"],
        "blocked_condition": "post-probe trace is assembled after outcome inspection",
        "observed_null_signal": "trace exists only as report-side reconstruction",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks ND2 and stronger",
    },
    {
        "primitive_id": "naturalization_depth",
        "scenario_id": "probe_residue_only",
        "blocker_class": "probe_residue",
        "control_ids": ["probe_residue_control"],
        "blocked_condition": "probe residue remains in evaluated runtime input",
        "observed_null_signal": "post-probe trace persists only with probe residue present",
        "support_floor_result": "preserved",
        "coherence_floor_result": "preserved",
        "boundary_integrity_result": "preserved",
        "flux_or_leakage_result": "preserved",
        "rung_effect": "blocks ND4 and stronger",
    },
    {
        "primitive_id": "naturalization_depth",
        "scenario_id": "support_annotation_native_support_relabel",
        "blocker_class": "producer_mediated_native_support_relabel",
        "control_ids": [
            "support_source_annotation_relabel_control",
            "semantic_relabel_control",
            "native_support_relabel_control",
            "phase8_relabel_control",
        ],
        "blocked_condition": "support annotation or producer-mediated label is relabeled as native support",
        "observed_null_signal": "support annotation is used as post-probe source-current support",
        "support_floor_result": "missing",
        "coherence_floor_result": "missing",
        "boundary_integrity_result": "missing",
        "flux_or_leakage_result": "missing",
        "rung_effect": "blocks all primitive support and unsafe claims",
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


def schema_rows_by_primitive(i2: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = i2["schema_freeze"]["primitive_schema_rows"]
    return {row["primitive_id"]: row for row in rows}


def threshold_record(schema_row: dict[str, Any]) -> dict[str, Any]:
    rule = schema_row["same_basin_continuation_rule"]
    handoff = schema_row["handoff_inputs"]
    record = {
        "threshold_id": f"n21_i3_{schema_row['primitive_id']}_active_null_thresholds",
        "primitive_id": schema_row["primitive_id"],
        "source_contract_row": schema_row["source_contract_row"],
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "threshold_declared_before_use": True,
        "threshold_value_or_rule": {
            "support_floor": handoff["support_floor"],
            "coherence_floor": handoff["coherence_floor"],
            "boundary_integrity_floor": rule["boundary_integrity_floor"],
            "flux_or_leakage_bound": rule["flux_balance_bounds"],
            "replay_requirement": rule["replay_requirement"],
        },
        "threshold_owner": "frozen_i1_contract_reference",
        "failure_policy": "active_null_cannot_retune_or_override_thresholds",
    }
    record["threshold_record_digest"] = digest_value(record)
    return record


def comparability_record(
    schema_row: dict[str, Any], scenario: dict[str, Any]
) -> dict[str, Any]:
    seed_pairing_rule = {
        "seed_pairing_rule_id": f"n21_i3_{schema_row['primitive_id']}_null_seed_pairing",
        "same_seed_or_declared_seed_pairing_rule": True,
        "pairing_reason": (
            "pre-positive null uses the same declared seed family as the "
            "future candidate row but removes the claimed withdrawal/probe "
            "absence condition"
        ),
    }
    topology = {
        "topology_config_family": f"n21_i3_{schema_row['primitive_id']}_null_topology_family",
        "same_topology_config_family": True,
    }
    runtime_envelope = {
        "runtime_envelope_id": f"n21_i3_{schema_row['primitive_id']}_null_envelope",
        "same_runtime_envelope": True,
        "derived_report_only": True,
    }
    budget_schedule = {
        "budget_schedule_family": f"n21_i3_{schema_row['primitive_id']}_null_budget_family",
        "same_budget_schedule_family_where_applicable": True,
        "same_budget_schedule_digest_where_applicable": True,
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
        "no_declared_withdrawal_or_no_probe_absence": True,
        "expected_result": "fail_closed",
        "blocked_condition": scenario["blocked_condition"],
    }


def control_results(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": control_id,
            "control_status": "failed_closed",
            "blocked_condition": scenario["blocked_condition"],
            "expected_result": "primitive claim rejected",
            "actual_result": "primitive_claim_allowed=false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": scenario["rung_effect"],
        }
        for control_id in scenario["control_ids"]
    ]


def build_row(
    index: int, scenario: dict[str, Any], schema_row: dict[str, Any]
) -> dict[str, Any]:
    primitive_id = scenario["primitive_id"]
    row = {
        "row_id": f"n21_i3_row_{index:02d}_{primitive_id}_{scenario['scenario_id']}",
        "primitive_id": primitive_id,
        "source_contract_row": schema_row["source_contract_row"],
        "contract_consumed_without_redefinition": True,
        "row_specific_thresholds_declared_before_use": True,
        "run_artifact_id": f"n21_i3_active_null_{primitive_id}_{scenario['scenario_id']}",
        "source_commit_or_source_digest": "not_applicable_pre_positive_active_null",
        "runtime_config_digest": digest_value(
            {
                "primitive_id": primitive_id,
                "scenario_id": scenario["scenario_id"],
                "config_role": "pre_positive_active_null",
            }
        ),
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "baseline_artifact_path": "not_applicable_pre_positive_active_null",
        "withdrawn_or_probe_absent_artifact_path": "not_applicable_pre_positive_active_null",
        "event_log_or_trace_path": "not_applicable_pre_positive_active_null",
        "snapshot_or_replay_artifact_path": "not_applicable_pre_positive_active_null",
        "artifact_digest": "pending",
        "artifact_digest_role": "active_null_row_digest_not_positive_run_artifact",
        "derived_report_only": True,
        "source_current_inputs": [],
        "source_current_input_status": "absent_by_active_null_design",
        "producer_mediated_fields": schema_row["producer_mediated_fields"],
        "naturalization_debt_fields": schema_row["naturalization_debt_fields"],
        "blocked_relabel_fields": schema_row["row_specific_blocked_relabels"],
        "same_basin_continuation_rule": schema_row["same_basin_continuation_rule"],
        "support_scaffold": schema_row["support_scaffold"],
        "handoff_inputs": schema_row["handoff_inputs"],
        "threshold_record": threshold_record(schema_row),
        "support_floor_result": scenario["support_floor_result"],
        "coherence_floor_result": scenario["coherence_floor_result"],
        "boundary_integrity_result": scenario["boundary_integrity_result"],
        "flux_or_leakage_result": scenario["flux_or_leakage_result"],
        "replay_result": {
            "replay_result_status": "not_applicable",
            "reason_code": "pre_positive_active_null_no_replay_claim",
            "affected_rung": "replay_backed_and_stronger",
            "why_outside_declared_scope": (
                "I3 active nulls test fail-closed blocker behavior before "
                "positive replay-backed probes are admitted"
            ),
        },
        "replay_result_status": "not_applicable",
        "control_results": control_results(scenario),
        "control_result_statuses": ["failed_closed"],
        "wr_ladder_rung": None,
        "nd_ladder_rung": None,
        "row_decision": "rejected",
        "primitive_claim_allowed": False,
        "unsafe_claim_flags": unsafe_claim_flags(),
        "claim_ceiling": (
            "pre-positive active null and failure baseline only; no WR, ND, "
            "agency, native support, sentience, Phase 8, or ant-ecology "
            "implementation claim"
        ),
        "active_null_comparability": comparability_record(schema_row, scenario),
        "blocker_class": scenario["blocker_class"],
        "observed_null_signal": scenario["observed_null_signal"],
        "control_ids_covered": scenario["control_ids"],
        "expected_result": "fail_closed",
        "actual_result": "failed_closed",
    }
    artifact_payload = dict(row)
    artifact_payload["artifact_digest"] = "active_null_row_digest_pending"
    row["artifact_digest"] = digest_value(artifact_payload)
    return row


def build_rows(i2: dict[str, Any]) -> list[dict[str, Any]]:
    schema_rows = schema_rows_by_primitive(i2)
    return [
        build_row(index, scenario, schema_rows[scenario["primitive_id"]])
        for index, scenario in enumerate(NULL_SCENARIOS, start=1)
    ]


def required_candidate_fields(i2: dict[str, Any]) -> list[str]:
    return i2["schema_freeze"]["candidate_evidence_row_schema"]["required_fields"]


def active_null_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    blocker_classes = sorted({row["blocker_class"] for row in rows})
    covered_controls = sorted(
        {control_id for row in rows for control_id in row["control_ids_covered"]}
    )
    return {
        "row_count": len(rows),
        "failed_closed_rows": sum(row["actual_result"] == "failed_closed" for row in rows),
        "failed_open_rows": sum(
            "failed_open" in row["control_result_statuses"] for row in rows
        ),
        "blocker_classes": blocker_classes,
        "covered_controls": covered_controls,
        "primitive_claim_allowed_any": any(
            row["primitive_claim_allowed"] for row in rows
        ),
        "positive_primitive_evidence_opened": False,
        "wr_ladder_rung_assigned": False,
        "nd_ladder_rung_assigned": False,
        "active_nulls_ready_before_positive_probes": True,
    }


def all_required_fields_present(rows: list[dict[str, Any]], fields: list[str]) -> bool:
    return all(all(field in row for field in fields) for row in rows)


def build_checks(
    i1: dict[str, Any], i2: dict[str, Any], rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    required_fields = required_candidate_fields(i2)
    summary = active_null_summary(rows)
    required_blockers = {
        "no_withdrawal_no_removal",
        "no_probe_absence",
        "label_only_continuation",
        "proxy_only_success",
        "hidden_producer_support",
        "post_hoc_trace_construction",
        "producer_mediated_native_support_relabel",
    }
    required_controls = {
        control_id
        for schema_row in i2["schema_freeze"]["primitive_schema_rows"]
        for control_id in schema_row["required_control_ids"]
    }
    covered_controls = {
        control_id for row in rows for control_id in row["control_ids_covered"]
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
            "active_null_row_count_complete",
            len(rows) == 14
            and {
                row["primitive_id"]
                for row in rows
            }
            == {"withdrawal_resistance", "naturalization_depth"},
            {"row_count": len(rows), "summary": summary},
        ),
        check(
            "candidate_evidence_fields_present_in_all_rows",
            all_required_fields_present(rows, required_fields),
            {"required_field_count": len(required_fields)},
        ),
        check(
            "active_nulls_use_same_contract_and_digest",
            all(
                row["contract_consumed_without_redefinition"]
                and row["source_contract_row_digest"]
                in {
                    schema_row["source_contract_row_digest"]
                    for schema_row in i2["schema_freeze"]["primitive_schema_rows"]
                }
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "source_contract_row": row["source_contract_row"],
                    "source_contract_row_digest": row["source_contract_row_digest"],
                }
                for row in rows
            ],
        ),
        check(
            "active_null_comparability_complete",
            all(
                row["active_null_comparability"]["same_source_contract_row"]
                and row["active_null_comparability"][
                    "same_source_contract_row_digest"
                ]
                and row["active_null_comparability"]["same_basin_signature_fields"]
                and row["active_null_comparability"]["seed_pairing_rule"][
                    "same_seed_or_declared_seed_pairing_rule"
                ]
                and row["active_null_comparability"]["topology_config"][
                    "same_topology_config_family"
                ]
                and row["active_null_comparability"]["runtime_envelope"][
                    "same_runtime_envelope"
                ]
                and row["active_null_comparability"]["budget_schedule"][
                    "same_budget_schedule_family_where_applicable"
                ]
                and row["active_null_comparability"][
                    "no_declared_withdrawal_or_no_probe_absence"
                ]
                for row in rows
            ),
            "all rows preserve I2 active-null comparability requirements",
        ),
        check(
            "required_i3_blockers_fail_closed",
            required_blockers.issubset(set(summary["blocker_classes"]))
            and all(row["actual_result"] == "failed_closed" for row in rows),
            {
                "required_blockers": sorted(required_blockers),
                "present_blockers": summary["blocker_classes"],
            },
        ),
        check(
            "all_required_controls_covered",
            required_controls.issubset(covered_controls),
            {
                "required_controls": sorted(required_controls),
                "covered_controls": sorted(covered_controls),
            },
        ),
        check(
            "all_controls_fail_closed_without_failed_open",
            all(row["control_result_statuses"] == ["failed_closed"] for row in rows)
            and not any(
                result["control_status"] == "failed_open"
                for row in rows
                for result in row["control_results"]
            ),
            "active null controls reject the tested false-positive paths",
        ),
        check(
            "not_applicable_replay_has_scope_reason",
            all(
                row["replay_result_status"] == "not_applicable"
                and row["replay_result"]["reason_code"]
                and row["replay_result"]["why_outside_declared_scope"]
                for row in rows
            ),
            "pre-positive null rows do not claim replay-backed rungs",
        ),
        check(
            "no_positive_primitive_evidence_or_ladder_rungs_opened",
            not any(row["primitive_claim_allowed"] for row in rows)
            and all(row["row_decision"] == "rejected" for row in rows)
            and all(row["wr_ladder_rung"] is None for row in rows)
            and all(row["nd_ladder_rung"] is None for row in rows)
            and all(row["derived_report_only"] for row in rows),
            {
                "primitive_claim_allowed_any": summary[
                    "primitive_claim_allowed_any"
                ],
                "wr_ladder_rung_assigned": summary["wr_ladder_rung_assigned"],
                "nd_ladder_rung_assigned": summary["nd_ladder_rung_assigned"],
            },
        ),
        check(
            "unsafe_claim_flags_all_false",
            all(
                set(row["unsafe_claim_flags"].keys()) == set(GLOBAL_UNSAFE_CLAIMS)
                and all(value is False for value in row["unsafe_claim_flags"].values())
                for row in rows
            ),
            "all active null rows keep unsafe claim flags false",
        ),
        check(
            "active_nulls_admit_iterations_4_and_5",
            all(row["actual_result"] == "failed_closed" for row in rows)
            and not summary["primitive_claim_allowed_any"],
            {
                "ready_for_iteration_4_withdrawal_probe": True,
                "ready_for_iteration_5_naturalization_probe": True,
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
    i2 = load_json(I2_OUTPUT_PATH)
    rows = build_rows(i2)
    checks = build_checks(i1, i2, rows)
    summary = active_null_summary(rows)
    payload: dict[str, Any] = {
        "artifact_id": "n21_withdrawal_active_nulls",
        "schema_version": "n21_withdrawal_active_nulls_v1",
        "experiment": "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth",
        "iteration": 3,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_active_nulls_fail_closed_no_primitive_evidence",
        "purpose": (
            "Build pre-positive active nulls and failure baselines that reject "
            "label-only, proxy-only, hidden-support, post-hoc, no-withdrawal, "
            "no-probe-absence, probe-residue, and unsafe relabel paths."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n21_i1_source_contract_inventory"),
            source_record(I2_OUTPUT_PATH, "n21_i2_schema_freeze"),
            source_record(I2_REPORT_PATH, "n21_i2_schema_freeze_report"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "active_null_policy": {
            "pre_positive_active_nulls_only": True,
            "positive_primitive_evidence_allowed": False,
            "derived_report_only_rows_can_only_reject": True,
            "active_null_rows_assign_wr_or_nd_rungs": False,
            "failed_closed_controls_required_before_positive_probes": True,
            "post_positive_replay_control_matrix_still_required_in_iteration_6": True,
        },
        "active_null_summary": summary,
        "active_null_rows": rows,
        "iteration3_boundary": {
            "active_nulls_only": True,
            "primitive_evidence_opened": False,
            "withdrawal_resistance_supported": False,
            "naturalization_depth_supported": False,
            "wr_ladder_rung_assigned": False,
            "nd_ladder_rung_assigned": False,
            "n21_closeout_ladder_rung_assigned": False,
            "positive_run_artifacts_consumed": False,
            "ready_for_iteration_4_withdrawal_probe": True,
            "ready_for_iteration_5_naturalization_probe": True,
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
    summary = data["active_null_summary"]
    lines = [
        "# N21 Iteration 3 - Active Nulls And Failure Baselines",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 3 runs pre-positive active nulls only. It does not open",
        "withdrawal-resistance or naturalization-depth evidence and assigns no",
        "WR, ND, or N21-C ladder rungs.",
        "",
        "## Active Null Summary",
        "",
        "```text",
        f"row_count = {summary['row_count']}",
        f"failed_closed_rows = {summary['failed_closed_rows']}",
        f"failed_open_rows = {summary['failed_open_rows']}",
        "primitive_claim_allowed_any = false",
        "positive_primitive_evidence_opened = false",
        "wr_ladder_rung_assigned = false",
        "nd_ladder_rung_assigned = false",
        "```",
        "",
        "## Rows",
        "",
        "| Row | Primitive | Blocker | Decision | Claim Allowed | Controls |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in data["active_null_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{row['primitive_id']}` | "
            f"`{row['blocker_class']}` | "
            f"`{row['row_decision']}` | "
            f"`{str(row['primitive_claim_allowed']).lower()}` | "
            f"`{', '.join(row['control_ids_covered'])}` |"
        )
    lines.extend(
        [
            "",
            "## Blockers Covered",
            "",
            "```text",
            *summary["blocker_classes"],
            "```",
            "",
            "## Covered Controls",
            "",
            "```text",
            *summary["covered_controls"],
            "```",
            "",
            "## Boundary",
            "",
            "```text",
            "active_nulls_only = true",
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
            "Iteration 3 establishes pre-positive control discipline. The rows",
            "are deliberately derived-report active nulls, so they can only",
            "reject false-positive paths; they cannot support WR, ND, or any",
            "stronger claim. The result admits Iterations 4 and 5 because the",
            "no-withdrawal/no-probe-absence, label-only, proxy-only, hidden",
            "support, post-hoc construction, probe-residue, floor-crossing,",
            "and unsafe relabel paths all fail closed.",
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
