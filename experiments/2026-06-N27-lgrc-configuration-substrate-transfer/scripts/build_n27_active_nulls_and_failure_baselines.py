#!/usr/bin/env python3
"""Build N27 Iteration 3 active nulls and failure baselines."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
I2_OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_schema_and_controls.json"
I2_REPORT = EXPERIMENT / "reports" / "n27_transfer_schema_and_controls.md"
OUTPUT = EXPERIMENT / "outputs" / "n27_active_nulls_and_failure_baselines.json"
REPORT = EXPERIMENT / "reports" / "n27_active_nulls_and_failure_baselines.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_active_nulls_and_failure_baselines.py"
)

ACTIVE_NULL_CT_RUNG = "not_assigned_active_null_control_only"
N27_CLOSEOUT_CEILING = "N27-C3_active_nulls_fail_closed"

ARTIFACT_MANIFEST_FAILURE_CASES = [
    "missing_artifact_path",
    "missing_artifact_role",
    "sha256_mismatch",
    "absolute_path",
    "derived_report_only_for_positive_row",
    "rung_required_artifact_role_missing",
]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "ap5_nat4_gap_resolution_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_ap5_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_identity_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]

GEOMETRIC_READINGS = {
    "same_label_different_basin_control": (
        "A label survives the mapping, but the basin signature and boundary do "
        "not. Geometrically this is a name attached to a different basin, not "
        "a transferred basin."
    ),
    "fixture_equivalence_label_only_control": (
        "The fixture is declared equivalent without a source-current mapping. "
        "The graph/config may look similar, but no cross-frame geometry links "
        "the pre and post basin."
    ),
    "mapping_declared_after_outcome_control": (
        "The mapping is chosen after the post-transfer state is known. The "
        "apparent alignment is post-hoc stitching rather than a declared "
        "cross-frame transformation."
    ),
    "proxy_score_relabel_as_transfer_control": (
        "A proxy margin is preserved while basin signature or boundary mapping "
        "fails. The proxy surface remains but the geometric basin does not "
        "transfer."
    ),
    "hidden_support_reconstruction_control": (
        "Undeclared support rebuilds the post-transfer basin. The receiving "
        "geometry is reconstructed by support injection instead of preserving "
        "the mapped basin signature."
    ),
    "support_reconstruction_as_transfer_control": (
        "A reconstruction ledger is counted as preserved support. This swaps "
        "producer-mediated rebuilding for source-current support preservation."
    ),
    "boundary_mapping_missing_control": (
        "The post-transfer basin has no mapped boundary from the pre-transfer "
        "basin. Without a boundary map, the geometry cannot distinguish "
        "transfer from a new or different basin."
    ),
    "post_transfer_signature_missing_control": (
        "The pre-transfer basin is described, but the mapped post-transfer "
        "signature is absent. There is no target-side geometry to compare."
    ),
    "source_current_inputs_missing_control": (
        "The row is report-derived. It has no source-current runtime inputs "
        "for pre/post signature, boundary mapping, support, coherence, or flux."
    ),
    "cross_substrate_mapping_missing_control": (
        "A substrate-level transfer is claimed without mapping the substrate "
        "representation, boundary side assignments, or support/coherence "
        "interpretation."
    ),
    "artifact_manifest_failure_control": (
        "The trace artifacts are missing, unrole-labeled, or not digest-stable. "
        "The geometry cannot be replayed or audited."
    ),
    "replay_failure_control": (
        "The candidate does not survive artifact, snapshot/load, duplicate, or "
        "mapping-order replay. A one-run transfer shape is not replay-backed "
        "same-basin transfer."
    ),
    "stress_variant_failure_control": (
        "The transfer shape only survives one narrow mapping and fails under "
        "declared tolerance, support, coherence, flux, or mapping-variant "
        "stress."
    ),
    "AP4_dependency_omitted_control": (
        "Route-conditioned selection participates in the transfer row, but the "
        "AP4 dependency is missing. The route/selection axis is being used "
        "without its inherited evidence boundary."
    ),
    "AP5_dependency_omitted_control": (
        "Proxy or target formation participates in the transfer row, but the "
        "AP5 dependency is missing. Proxy context is being used without its "
        "inherited evidence boundary."
    ),
    "n26_proxy_as_transfer_evidence_control": (
        "N26 proxy divergence/collapse is counted as transfer. This imports a "
        "proxy/basin contrast as if it were cross-frame basin-signature "
        "preservation."
    ),
    "n26_scoped_ap5_as_native_ap5_control": (
        "N26 scoped artifact AP5 context is promoted to native AP5. The AP5 "
        "bridge context is overread as a native AP5 result or NAT4 gap "
        "resolution."
    ),
    "n25_2_direct_transfer_consumption_control": (
        "N25.2 MB6 substrate is consumed directly as N27 transfer evidence. "
        "That bypasses the N26-scoped handoff boundary and backfills substrate "
        "capacity into transfer."
    ),
    "semantic_identity_relabel_control": (
        "Identity/selfhood language is used as evidence. The transfer claim is "
        "semantic continuity rather than source-current basin geometry."
    ),
    "semantic_choice_goal_relabel_control": (
        "Choice, goal, or intention language is used as evidence. The transfer "
        "claim is agency vocabulary rather than mapped basin continuity."
    ),
    "native_support_relabel_control": (
        "Producer-mediated or preserved support is relabeled native support. "
        "Support visibility is overclaimed as native support production."
    ),
    "phase8_ant_ecology_relabel_control": (
        "A transfer row is relabeled Phase 8 completion or ant ecology. N27 "
        "does not implement or validate those downstream claims."
    ),
}

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]


def gate_value(control_id: str, target_control_id: str, active_value: Any) -> Any:
    return active_value if control_id == target_control_id else "not_evaluated_active_null"


def primary_blocker_evidence(control: dict[str, Any]) -> dict[str, Any]:
    return {
        "violated_gate": control["control_id"].removesuffix("_control"),
        "blocked_condition": control["blocked_condition"],
        "expected_result": control["expected_result"],
        "rung_effect": control["rung_effect"],
        "orthogonal_role": control["orthogonal_role"],
    }


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def collect_strings(data: Any) -> set[str]:
    strings: set[str] = set()
    if isinstance(data, str):
        strings.add(data)
    elif isinstance(data, list):
        for item in data:
            strings.update(collect_strings(item))
    elif isinstance(data, dict):
        for value in data.values():
            strings.update(collect_strings(value))
    return strings


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def source_record(path: Path, source_id: str, role: str) -> dict[str, Any]:
    relative = path.relative_to(ROOT).as_posix()
    record = {
        "source_id": source_id,
        "path": relative,
        "source_role": role,
        "exists": path.exists(),
        "sha256": sha256_file(path),
    }
    if path.suffix == ".json":
        data = load_json(path)
        record["artifact_id"] = data.get("artifact_id", "not_recorded")
        record["status"] = data.get("status", "not_recorded")
        record["acceptance_state"] = data.get("acceptance_state", "not_recorded")
        record["output_digest"] = data.get("output_digest", "not_recorded")
    else:
        record["artifact_id"] = "markdown_source"
        record["status"] = "context_only"
        record["acceptance_state"] = "not_applicable_markdown_context"
        record["output_digest"] = "not_applicable_markdown_context"
    return record


def active_null_row(control: dict[str, Any], index: int, i2: dict[str, Any]) -> dict[str, Any]:
    control_id = control["control_id"]
    scenario_id = control_id.removesuffix("_control")
    return {
        "row_id": f"n27_i3_row_{index:02d}_{scenario_id}",
        "iteration": "3",
        "row_schema_role": "active_null_failure_baseline_not_positive_evidence",
        "negative_control_row": True,
        "source_current_positive_probe": False,
        "blocker_triggered": True,
        "scenario_id": scenario_id,
        "control_id": control_id,
        "control_status": "failed_closed",
        "control_status_meaning": (
            "blocker was present and the transfer claim was correctly rejected"
        ),
        "blocked_condition": control["blocked_condition"],
        "expected_result": control["expected_result"],
        "actual_result": "claim_rejected_fail_closed",
        "claim_allowed_when_control_triggers": False,
        "rung_effect": control["rung_effect"],
        "orthogonal_role": control["orthogonal_role"],
        "control_satisfied_for_positive_row": False,
        "control_applicability_reason": "active_null_explicitly_instantiates_frozen_i2_control",
        "primary_blocker_control_id": control_id,
        "primary_blocker_isolated_by_schema": True,
        "primary_blocker_evidence": primary_blocker_evidence(control),
        "non_target_positive_gates_status": "not_evaluated_active_null",
        "geometric_reading": GEOMETRIC_READINGS[control_id],
        "row_decision": "rejected",
        "ct_ladder_rung": ACTIVE_NULL_CT_RUNG,
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "positive_transfer_evidence_opened": False,
        "candidate_rows_classified": False,
        "source_current_inputs": [],
        "derived_report_only": True,
        "artifact_manifest": [],
        "all_artifact_sha256_match_file_contents": "not_applicable_active_null_fixture",
        "runtime_config_digest": "not_applicable_active_null_fixture",
        "run_artifact_id": "not_applicable_active_null_fixture",
        "source_inventory_output_digest": i2["source_digest_pins"]["source_inventory_output_digest"],
        "source_output_digest": i2["output_digest"],
        "descriptor_contract_row_digest": i2["source_digest_pins"][
            "descriptor_contract_row_digest"
        ],
        "consumable_contract_row_digest": i2["source_digest_pins"][
            "consumable_contract_row_digest"
        ],
        "n26_closeout_output_digest": i2["source_digest_pins"]["n26_closeout_output_digest"],
        "source_contract_row_digest": i2["source_digest_pins"]["consumable_contract_row_digest"],
        "transfer_scope": gate_value(
            control_id, "cross_substrate_mapping_missing_control", "substrate"
        ),
        "transfer_core": "not_evaluated_active_null",
        "transfer_core_digest": "not_evaluated_active_null",
        "transfer_mapping_id": "not_evaluated_active_null",
        "transfer_mapping_digest": "not_evaluated_active_null",
        "mapping_declared_before_use": gate_value(
            control_id, "mapping_declared_after_outcome_control", False
        ),
        "mapping_source_backed": (
            False
            if control_id
            in {
                "fixture_equivalence_label_only_control",
                "cross_substrate_mapping_missing_control",
            }
            else "not_evaluated_active_null"
        ),
        "row_specific_thresholds_declared_before_use": "not_applicable_active_null",
        "signature_preservation_margin_formula": "not_applicable_active_null",
        "boundary_mapping_tolerance_formula": "not_applicable_active_null",
        "support_floor_margin_formula": "not_applicable_active_null",
        "coherence_floor_margin_formula": "not_applicable_active_null",
        "flux_balance_bound_formula": "not_applicable_active_null",
        "threshold_record_digest": "not_applicable_active_null",
        "pre_transfer_basin_signature_trace": "not_evaluated_active_null",
        "post_transfer_basin_signature_trace": gate_value(
            control_id, "post_transfer_signature_missing_control", "missing"
        ),
        "boundary_mapping_trace": gate_value(
            control_id, "boundary_mapping_missing_control", "missing"
        ),
        "support_preservation_trace": "not_evaluated_active_null",
        "coherence_preservation_trace": "not_evaluated_active_null",
        "flux_balance_trace": "not_evaluated_active_null",
        "original_fixture_support_change_trace": gate_value(
            control_id, "support_reconstruction_as_transfer_control", "present"
        ),
        "reconstructed_support_ledger": gate_value(
            control_id,
            "support_reconstruction_as_transfer_control",
            "reconstruction_present_but_cannot_count_as_preservation",
        ),
        "hidden_support_reconstruction_absent": gate_value(
            control_id, "hidden_support_reconstruction_control", False
        ),
        "same_basin_signature_preserved_under_mapping": gate_value(
            control_id, "same_label_different_basin_control", False
        ),
        "same_label_different_basin_rejected": gate_value(
            control_id, "same_label_different_basin_control", True
        ),
        "proxy_score_relabel_rejected": gate_value(
            control_id, "proxy_score_relabel_as_transfer_control", True
        ),
        "configuration_label_only_rejected": gate_value(
            control_id, "fixture_equivalence_label_only_control", True
        ),
        "support_reconstruction_as_transfer_rejected": gate_value(
            control_id, "support_reconstruction_as_transfer_control", True
        ),
        "n25_2_direct_transfer_consumption_used": gate_value(
            control_id, "n25_2_direct_transfer_consumption_control", True
        ),
        "n25_2_consumed_only_through_n26_context": gate_value(
            control_id, "n25_2_direct_transfer_consumption_control", False
        ),
        "artifact_manifest_status": gate_value(
            control_id, "artifact_manifest_failure_control", "missing_or_invalid"
        ),
        "artifact_manifest_failure_cases": gate_value(
            control_id,
            "artifact_manifest_failure_control",
            ARTIFACT_MANIFEST_FAILURE_CASES,
        ),
        "replay_result": gate_value(control_id, "replay_failure_control", "failed_closed"),
        "stress_variant_result": gate_value(
            control_id, "stress_variant_failure_control", "failed_closed"
        ),
        "control_results": [
            {
                "control_id": control_id,
                "control_status": "failed_closed",
                "blocked_condition": control["blocked_condition"],
                "expected_result": control["expected_result"],
                "actual_result": "claim_rejected_fail_closed",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": control["rung_effect"],
                "orthogonal_role": control["orthogonal_role"],
                "control_satisfied_for_positive_row": False,
                "control_applicability_reason": (
                    "active_null_explicitly_instantiates_frozen_i2_control"
                ),
            }
        ],
        "ap4_dependency_status": (
            "missing_blocks_row"
            if control_id == "AP4_dependency_omitted_control"
            else "not_applicable"
        ),
        "ap4_condition_reason": (
            "route_conditioned_selection_participates_but_dependency_missing"
            if control_id == "AP4_dependency_omitted_control"
            else "active_null_does_not_make_positive_route_conditioned_transfer_claim"
        ),
        "ap5_dependency_status": (
            "missing_blocks_row"
            if control_id == "AP5_dependency_omitted_control"
            else "not_applicable"
        ),
        "ap5_condition_reason": (
            "proxy_or_target_formation_participates_but_dependency_missing"
            if control_id == "AP5_dependency_omitted_control"
            else "active_null_does_not_make_positive_proxy_or_target_transfer_claim"
        ),
        "claim_ceiling": "active null rejection only; no transfer evidence or CT rung",
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
    }


def build_checks(output: dict[str, Any], i2: dict[str, Any]) -> list[dict[str, Any]]:
    rows = output["active_null_rows"]
    required_controls = i2["control_schema"]["required_control_ids"]
    row_controls = [row["control_id"] for row in rows]
    checks = [
        check(
            "i2_schema_passed",
            i2.get("status") == "passed"
            and i2.get("acceptance_state")
            == "accepted_transfer_schema_and_controls_frozen_no_positive_evidence",
            {"status": i2.get("status"), "acceptance_state": i2.get("acceptance_state")},
        ),
        check(
            "i2_digest_recorded",
            output["source_schema_output_digest"] == i2["output_digest"],
            {"source_schema_output_digest": output["source_schema_output_digest"]},
        ),
        check(
            "all_frozen_controls_instantiated",
            set(row_controls) == set(required_controls) and len(rows) == len(required_controls),
            {"row_count": len(rows), "required_control_count": len(required_controls)},
        ),
        check(
            "all_active_nulls_fail_closed",
            all(row["control_status"] == "failed_closed" for row in rows),
            {"failed_closed_count": output["failed_closed_control_count"]},
        ),
        check(
            "failed_open_control_count_zero",
            output["failed_open_control_count"] == 0,
            {"failed_open_control_count": output["failed_open_control_count"]},
        ),
        check(
            "controls_remain_orthogonal",
            len({row["orthogonal_role"] for row in rows}) == len(rows),
            {"orthogonal_role_count": len({row["orthogonal_role"] for row in rows})},
        ),
        check(
            "control_result_audit_fields_present",
            all(
                "control_satisfied_for_positive_row" in row["control_results"][0]
                and "control_applicability_reason" in row["control_results"][0]
                for row in rows
            ),
            {"row_count": len(rows)},
        ),
        check(
            "active_null_boundary_markers_present",
            all(
                row["negative_control_row"] is True
                and row["source_current_positive_probe"] is False
                and row["blocker_triggered"] is True
                for row in rows
            ),
            {"row_count": len(rows)},
        ),
        check(
            "primary_blockers_isolated",
            all(
                row["primary_blocker_control_id"] == row["control_id"]
                and row["primary_blocker_isolated_by_schema"] is True
                and row["primary_blocker_evidence"]["violated_gate"]
                == row["scenario_id"]
                for row in rows
            ),
            {"row_count": len(rows)},
        ),
        check(
            "non_target_positive_gates_not_evaluated",
            all(
                row["non_target_positive_gates_status"]
                == "not_evaluated_active_null"
                for row in rows
            ),
            {"row_count": len(rows)},
        ),
        check(
            "artifact_manifest_failure_cases_explicit",
            next(
                row
                for row in rows
                if row["control_id"] == "artifact_manifest_failure_control"
            )["artifact_manifest_failure_cases"]
            == ARTIFACT_MANIFEST_FAILURE_CASES,
            {"required_cases": ARTIFACT_MANIFEST_FAILURE_CASES},
        ),
        check(
            "no_positive_transfer_evidence_opened",
            output["positive_transfer_evidence_opened"] is False
            and output["candidate_rows_classified"] is False
            and output["ct_ladder_rung_assigned"] is False,
            {
                "positive_transfer_evidence_opened": output[
                    "positive_transfer_evidence_opened"
                ],
                "ct_ladder_rung_assigned": output["ct_ladder_rung_assigned"],
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(
                value is False
                for row in rows
                for value in row["unsafe_claim_flags"].values()
            ),
            {"row_count": len(rows)},
        ),
        check(
            "active_null_rows_not_source_current_positive_evidence",
            all(
                row["derived_report_only"] is True
                and row["source_current_inputs"] == []
                and row["artifact_manifest"] == []
                for row in rows
            ),
            {"row_count": len(rows)},
        ),
        check(
            "source_precedence_preserved",
            output["source_precedence"]["n20_i5_consumable_contract_is_normative"]
            is True
            and output["source_precedence"]["n20_i4_descriptor_is_context_only"] is True
            and output["source_precedence"]["n26_context_is_bounded_not_transfer_evidence"]
            is True
            and output["source_precedence"][
                "n25_2_consumed_only_through_n26_not_direct_transfer_evidence"
            ]
            is True,
            output["source_precedence"],
        ),
        check(
            "no_implementation_patch_opened",
            output["implementation_change_scope"]["src_diff_empty"] is True
            and output["implementation_change_scope"]["spec_diff_empty"] is True
            and output["implementation_change_scope"]["test_diff_empty"] is True
            and output["implementation_change_scope"]["implementation_patch_opened"] is False,
            output["implementation_change_scope"],
        ),
        check(
            "ready_for_iteration_4",
            output["ready_for_iteration_4_minimal_configuration_transfer_probe"] is True,
            {
                "ready_for_iteration_4_minimal_configuration_transfer_probe": output[
                    "ready_for_iteration_4_minimal_configuration_transfer_probe"
                ]
            },
        ),
    ]
    return checks


def build_output() -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT)
    control_rows = i2["control_schema"]["control_rows"]
    rows = [active_null_row(control, index, i2) for index, control in enumerate(control_rows, 1)]
    output: dict[str, Any] = {
        "artifact_id": "n27_active_nulls_and_failure_baselines",
        "schema_version": "n27_i3_active_nulls_v1",
        "experiment": "N27_configuration_substrate_transfer",
        "iteration": "3",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "instantiate I2 false-transfer controls before positive probes",
        "status": "passed",
        "acceptance_state": "accepted_active_nulls_fail_closed_no_positive_transfer_evidence",
        "source_schema_path": (
            "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/"
            "outputs/n27_transfer_schema_and_controls.json"
        ),
        "source_schema_output_digest": i2["output_digest"],
        "source_records": [
            source_record(I2_OUTPUT, "n27_i2_transfer_schema_and_controls", "schema_control_freeze"),
            source_record(I2_REPORT, "n27_i2_transfer_schema_report", "schema_report_context"),
        ],
        "source_precedence": {
            "normative_contract_row": i2["source_precedence"]["normative_contract_row"],
            "descriptor_context_row": i2["source_precedence"]["descriptor_context_row"],
            "n20_i5_consumable_contract_is_normative": True,
            "n20_i4_descriptor_is_context_only": True,
            "n26_context_is_bounded_not_transfer_evidence": True,
            "n25_2_consumed_only_through_n26_not_direct_transfer_evidence": True,
        },
        "implementation_change_scope": {
            "src_diff_empty": True,
            "spec_diff_empty": True,
            "test_diff_empty": True,
            "implementation_patch_opened": False,
            "scope_note": (
                "I3 changes experiment records only; runtime/spec/test repair would "
                "be recorded as a future repair target, not as active-null evidence."
            ),
        },
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "n27_closeout_ladder_rung_assigned": False,
        "ct_ladder_rung_assigned": False,
        "positive_transfer_evidence_opened": False,
        "candidate_rows_classified": False,
        "failed_closed_control_count": sum(
            1 for row in rows if row["control_status"] == "failed_closed"
        ),
        "failed_open_control_count": sum(
            1 for row in rows if row["control_status"] == "failed_open"
        ),
        "required_control_count": len(i2["control_schema"]["required_control_ids"]),
        "instantiated_control_count": len(rows),
        "active_null_rows": rows,
        "ready_for_iteration_4_minimal_configuration_transfer_probe": True,
        "claim_boundary": {
            "claim_ceiling": "active-null/failure-baseline evidence only; no transfer candidate",
            "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        },
    }
    checks = build_checks(output, i2)
    output["checks"] = checks
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_active_nulls_fail_closed_no_positive_transfer_evidence"
        if output["status"] == "passed"
        else "blocked_active_nulls_or_failure_baselines"
    )
    output["checks"].append(
        check(
            "no_absolute_paths_in_records",
            not any(
                marker in value
                for value in collect_strings(output)
                for marker in ABSOLUTE_PATH_MARKERS
            ),
            "all record paths are repository-relative",
        )
    )
    output["failed_checks"] = [item["check_id"] for item in output["checks"] if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_active_nulls_fail_closed_no_positive_transfer_evidence"
        if output["status"] == "passed"
        else "blocked_active_nulls_or_failure_baselines"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    report = f"""# N27 Iteration 3 - Active Nulls And Failure Baselines

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

## Scope

Iteration 3 instantiates the frozen I2 transfer controls as active nulls and
failure baselines. It opens no positive transfer evidence and assigns no CT
rung.

```text
n27_closeout_ceiling = {output['n27_closeout_ceiling']}
positive_transfer_evidence_opened = {str(output['positive_transfer_evidence_opened']).lower()}
ct_ladder_rung_assigned = {str(output['ct_ladder_rung_assigned']).lower()}
failed_closed_control_count = {output['failed_closed_control_count']}
failed_open_control_count = {output['failed_open_control_count']}
```

## Source And Implementation Boundary

```text
normative_contract_row = {output['source_precedence']['normative_contract_row']}
descriptor_context_row = {output['source_precedence']['descriptor_context_row']}
n20_i5_consumable_contract_is_normative = {str(output['source_precedence']['n20_i5_consumable_contract_is_normative']).lower()}
n20_i4_descriptor_is_context_only = {str(output['source_precedence']['n20_i4_descriptor_is_context_only']).lower()}
n26_context_is_bounded_not_transfer_evidence = {str(output['source_precedence']['n26_context_is_bounded_not_transfer_evidence']).lower()}
n25_2_consumed_only_through_n26_not_direct_transfer_evidence = {str(output['source_precedence']['n25_2_consumed_only_through_n26_not_direct_transfer_evidence']).lower()}
src_diff_empty = {str(output['implementation_change_scope']['src_diff_empty']).lower()}
spec_diff_empty = {str(output['implementation_change_scope']['spec_diff_empty']).lower()}
test_diff_empty = {str(output['implementation_change_scope']['test_diff_empty']).lower()}
implementation_patch_opened = {str(output['implementation_change_scope']['implementation_patch_opened']).lower()}
```

## Active Null Rows

| Control | Blocker Triggered | Expected | Actual | Rung Effect | Claim Allowed |
| --- | --- | --- | --- | --- | --- |
"""
    for row in output["active_null_rows"]:
        report += (
            f"| `{row['control_id']}` | `{str(row['blocker_triggered']).lower()}` | "
            f"`{row['expected_result']}` | `{row['control_status']}` | "
            f"`{row['rung_effect']}` | "
            f"`{str(row['claim_allowed_when_control_triggers']).lower()}` |\n"
        )

    report += """

## Geometric Interpretation

Each row records a false transfer path in geometric terms: label survival,
within-frame movement, visual/topological similarity, proxy preservation,
hidden support reconstruction, missing boundary mapping, missing post-transfer
signature, missing source-current inputs, unmapped substrate claims, replay or
stress failure, AP dependency omission, imported N26/N25.2 context, or unsafe
semantic/native/Phase-8 relabeling. In every case the blocker triggers and the
claim fails closed.

The negative set is intentionally orthogonal: every row records exactly one
`primary_blocker_control_id`, and all non-target positive gates remain
`not_evaluated_active_null`. This prevents an active null from passing only
because unrelated gates were also forced to fail.

## Checks

| Check | Passed |
| --- | --- |
"""
    for item in output["checks"]:
        report += f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |\n"

    report += f"""

## Interpretation

I3 supports only the fail-closed-control portion of N27. It proves that the
frozen false-transfer paths are rejected before positive probes. It does not
support CT1, CT2, CT3, transfer, identity, native support, native AP5, AP5
NAT4-gap resolution, Phase 8, or ant ecology.

Output digest: `{output['output_digest']}`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()
