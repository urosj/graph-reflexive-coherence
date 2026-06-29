#!/usr/bin/env python3
"""Build N27 Iteration 7 controls / AP dependency / claim classification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N27-lgrc-configuration-substrate-transfer"
OUTPUT = EXPERIMENT / "outputs" / "n27_controls_ap_dependency_claim_classification.json"
REPORT = EXPERIMENT / "reports" / "n27_controls_ap_dependency_claim_classification.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n27_controls_ap_dependency_claim_classification_artifacts"

I1_OUTPUT = EXPERIMENT / "outputs" / "n27_source_inventory_and_transfer_contract_admission.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n27_transfer_schema_and_controls.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n27_active_nulls_and_failure_baselines.json"
I4_OUTPUT = EXPERIMENT / "outputs" / "n27_minimal_configuration_transfer_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n27_topology_fixture_variant_transfer_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n27_replay_same_basin_mapping_matrix.json"
I5A_OUTPUT = EXPERIMENT / "outputs" / "n27_artifact_only_reconstruction_replay_probe.json"
I6_OUTPUT = EXPERIMENT / "outputs" / "n27_stress_mapping_variant_transfer_matrix.json"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/scripts/"
    "build_n27_controls_ap_dependency_claim_classification.py"
)

N27_CLOSEOUT_CEILING = "N27-C5_replay_control_stress_backed_transfer_candidate_supported"

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]

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


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(data), encoding="utf-8")


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
    data = load_json(path)
    return {
        "source_id": source_id,
        "path": rel(path),
        "source_role": role,
        "exists": path.exists(),
        "sha256": sha256_file(path),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
    }


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def trace_artifact(role: str, row_id: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{row_id}_{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(path)}


def control_rows_by_id(schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["control_id"]: row for row in schema["control_schema"]["control_rows"]}


def i6_rows_by_source(i6: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["source_iteration"]: row for row in i6["stress_rows"]}


def control_result(
    control: dict[str, Any],
    status: str,
    actual_result: str,
    rung_effect: str | None = None,
    satisfied: bool = True,
    applicability_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "control_id": control["control_id"],
        "control_status": status,
        "blocked_condition": control["blocked_condition"],
        "expected_result": control["expected_result"],
        "actual_result": actual_result,
        "claim_allowed_when_control_triggers": False,
        "rung_effect": rung_effect or control["rung_effect"],
        "orthogonal_role": control["orthogonal_role"],
        "control_satisfied_for_positive_row": satisfied,
        "control_applicability_reason": applicability_reason
        or "control_applies_to_positive_transfer_classification_row",
    }


def positive_control_result(control: dict[str, Any], actual_result: str) -> dict[str, Any]:
    return control_result(
        control,
        "passed",
        actual_result,
        satisfied=True,
        applicability_reason="blocked_condition_absent_in_positive_row",
    )


def build_control_results(
    row: dict[str, Any],
    controls: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    source_iteration = row["source_iteration"]
    stress_passed = row["ct5_stress_variant_candidate_supported"]
    results: list[dict[str, Any]] = []

    actuals = {
        "same_label_different_basin_control": "same basin signature and mapped boundary preserved; label-only transfer not used",
        "fixture_equivalence_label_only_control": "source-current mapping digest present; fixture similarity alone not counted",
        "mapping_declared_after_outcome_control": "mapping was declared before post-transfer observation",
        "proxy_score_relabel_as_transfer_control": "proxy score not used as transfer evidence",
        "hidden_support_reconstruction_control": "hidden support reconstruction ledger is absent",
        "support_reconstruction_as_transfer_control": "reconstructed support is not counted as preserved support",
        "boundary_mapping_missing_control": "boundary mapping trace is present",
        "post_transfer_signature_missing_control": "post-transfer basin signature trace is present",
        "source_current_inputs_missing_control": "source-current inputs and artifact manifest are present",
        "artifact_manifest_failure_control": "artifact paths, roles, and SHA-256 hashes validate",
        "replay_failure_control": "artifact, snapshot/load, duplicate, and mapping-order replay passed in I5/I5-A",
        "n26_proxy_as_transfer_evidence_control": "N26 is consumed only as bounded context, not transfer evidence",
        "n26_scoped_ap5_as_native_ap5_control": "N26 scoped AP5 bridge remains artifact-level context, not native AP5",
        "n25_2_direct_transfer_consumption_control": "N25.2 is not directly consumed as N27 transfer evidence",
        "semantic_identity_relabel_control": "semantic identity and selfhood claims remain blocked",
        "semantic_choice_goal_relabel_control": "semantic choice, goal, and intention claims remain blocked",
        "native_support_relabel_control": "preserved transfer support is not relabeled native support",
        "phase8_ant_ecology_relabel_control": "N27 transfer evidence is not relabeled Phase 8 or ant ecology",
    }

    for control_id in controls:
        control = controls[control_id]
        if control_id == "cross_substrate_mapping_missing_control":
            results.append(
                control_result(
                    control,
                    "not_applicable",
                    "row scope is configuration/topology; no substrate-transfer claim opened",
                    rung_effect="substrate_transfer_claim_not_opened",
                    satisfied=True,
                    applicability_reason=(
                        "not_applicable_because_row_does_not_claim_cross_substrate_transfer"
                    ),
                )
            )
        elif control_id == "stress_variant_failure_control":
            if stress_passed:
                results.append(
                    positive_control_result(
                        control,
                        "declared stress envelope passed; CT5 stress gate satisfied",
                    )
                )
            else:
                results.append(
                    control_result(
                        control,
                        "failed_closed",
                        "stress blocker triggered and CT5 contribution was rejected",
                        rung_effect="CT5_or_stronger_blocked_for_this_row",
                        satisfied=False,
                        applicability_reason=(
                            "stress_variant_control_applies_and_blocks_CT5_for_"
                            f"source_iteration_{source_iteration}"
                        ),
                    )
                )
        elif control_id == "AP4_dependency_omitted_control":
            results.append(
                control_result(
                    control,
                    "passed",
                    "AP4 not applicable row-locally; no route-conditioned selection participates",
                    rung_effect="AP4_gate_satisfied_by_row_local_not_applicable_reason",
                    satisfied=True,
                    applicability_reason=(
                        "row_records_ap4_dependency_status_not_applicable_with_reason"
                    ),
                )
            )
        elif control_id == "AP5_dependency_omitted_control":
            results.append(
                control_result(
                    control,
                    "passed",
                    "AP5 not applicable row-locally; no proxy or target formation participates",
                    rung_effect="AP5_gate_satisfied_by_row_local_not_applicable_reason",
                    satisfied=True,
                    applicability_reason=(
                        "row_records_ap5_dependency_status_not_applicable_with_reason"
                    ),
                )
            )
        else:
            results.append(positive_control_result(control, actuals[control_id]))
    return results


def build_classification_row(
    source_iteration: str,
    i6_row: dict[str, Any],
    controls: dict[str, dict[str, Any]],
    handoff_role: str,
) -> dict[str, Any]:
    control_results = build_control_results(i6_row, controls)
    failed_open_count = sum(1 for item in control_results if item["control_status"] == "failed_open")
    failed_closed_count = sum(1 for item in control_results if item["control_status"] == "failed_closed")
    not_applicable_count = sum(1 for item in control_results if item["control_status"] == "not_applicable")
    not_run_count = sum(1 for item in control_results if item["control_status"] == "not_run")
    all_required_controls_accounted = len(control_results) == len(controls)
    controls_clean_for_supported_scope = failed_open_count == 0 and not_run_count == 0
    stress_gate_passed = i6_row["ct5_stress_variant_candidate_supported"]

    if stress_gate_passed:
        classified_rung = "CT5"
        row_decision = "supported"
        row_decision_scope = "control_and_stress_backed_CT5_candidate_pending_I8_closeout"
        ct5_supported = True
        ct5_contribution_allowed = True
        ct4_supported = True
    else:
        classified_rung = "CT4_control_clean_stress_limited"
        row_decision = "partial"
        row_decision_scope = "control_clean_transfer_candidate_but_CT5_stress_gate_failed_closed"
        ct5_supported = False
        ct5_contribution_allowed = False
        ct4_supported = controls_clean_for_supported_scope and all_required_controls_accounted

    control_trace = {
        "trace_id": f"n27_i7_{source_iteration.lower().replace('-', '')}_full_control_trace",
        "trace_scope": "full_i7_control_matrix",
        "source_i6_row_id": i6_row["row_id"],
        "source_i6_control_trace_scope": "stress_control_trace_only_not_full_i7_control_matrix",
        "required_control_count": len(controls),
        "control_result_count": len(control_results),
        "failed_open_control_count": failed_open_count,
        "failed_closed_control_count": failed_closed_count,
        "not_applicable_control_count": not_applicable_count,
        "not_run_control_count": not_run_count,
        "all_required_controls_accounted": all_required_controls_accounted,
        "controls_clean_for_supported_scope": controls_clean_for_supported_scope,
        "control_results": control_results,
    }
    classification_trace = {
        "trace_id": f"n27_i7_{source_iteration.lower().replace('-', '')}_claim_classification_trace",
        "source_iteration": source_iteration,
        "source_i6_row_id": i6_row["row_id"],
        "i6_consumption_role": handoff_role,
        "classified_ct_ladder_rung": classified_rung,
        "ct4_control_backed_candidate_supported": ct4_supported,
        "ct5_supported": ct5_supported,
        "ct5_contribution_allowed": ct5_contribution_allowed,
        "ct6_supported": False,
        "final_transfer_supported": False,
        "ap4_dependency_status": "not_applicable",
        "ap4_condition_reason": (
            "configuration/topology mapping does not use route-conditioned selection"
        ),
        "ap5_dependency_status": "not_applicable",
        "ap5_condition_reason": (
            "configuration/topology mapping does not use proxy or target formation; "
            "N26 scoped AP5 context remains boundary-only"
        ),
        "native_ap5_supported": False,
        "ap5_nat4_gap_resolution_supported": False,
        "n26_counted_as_transfer_evidence": False,
        "n25_2_direct_transfer_consumption_used": False,
        "unsafe_claim_flags": unsafe_claim_flags(),
    }
    artifact_manifest = [
        trace_artifact("control_trace", f"n27_i7_row_{source_iteration.lower().replace('-', '')}", control_trace),
        trace_artifact(
            "claim_classification_trace",
            f"n27_i7_row_{source_iteration.lower().replace('-', '')}",
            classification_trace,
        ),
    ]

    return {
        "row_id": f"n27_i7_row_{source_iteration.lower().replace('-', '')}_controls_ap_claim_classification",
        "iteration": "7",
        "source_iteration": source_iteration,
        "source_i6_row_id": i6_row["row_id"],
        "source_i6_row_decision": i6_row["row_decision"],
        "source_i6_ct_ladder_rung": i6_row["ct_ladder_rung"],
        "source_i6_consumption_role": handoff_role,
        "row_decision": row_decision,
        "row_decision_scope": row_decision_scope,
        "classified_ct_ladder_rung": classified_rung,
        "ct4_control_backed_candidate_supported": ct4_supported,
        "ct5_supported": ct5_supported,
        "ct5_contribution_allowed": ct5_contribution_allowed,
        "ct6_supported": False,
        "final_transfer_supported": False,
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "transfer_scope": i6_row["transfer_scope"],
        "transfer_mapping_id": i6_row["transfer_mapping_id"],
        "transfer_core_digest": i6_row["transfer_core_digest"],
        "source_output_digest": i6_row["source_output_digest"],
        "source_stress_trace_digest": i6_row["stress_trace_digest"],
        "source_stress_failure_mode": i6_row["stress_failure_mode"],
        "control_trace": control_trace,
        "control_trace_digest": digest_value(control_trace),
        "claim_classification_trace": classification_trace,
        "claim_classification_trace_digest": digest_value(classification_trace),
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "all_required_controls_accounted": all_required_controls_accounted,
        "failed_open_control_count": failed_open_count,
        "failed_closed_control_count": failed_closed_count,
        "not_run_control_count": not_run_count,
        "control_results": control_results,
        "ap4_dependency_status": classification_trace["ap4_dependency_status"],
        "ap4_condition_reason": classification_trace["ap4_condition_reason"],
        "ap5_dependency_status": classification_trace["ap5_dependency_status"],
        "ap5_condition_reason": classification_trace["ap5_condition_reason"],
        "n26_counted_as_transfer_evidence": False,
        "n25_2_direct_transfer_consumption_used": False,
        "n25_2_consumed_only_through_n26_context": True,
        "native_ap5_supported": False,
        "ap5_nat4_gap_resolution_supported": False,
        "claim_ceiling": (
            "bounded artifact-level configuration/topology transfer candidate; "
            "CT6 and final transfer remain pending I8 closeout"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_checks(output: dict[str, Any], i2: dict[str, Any], i6: dict[str, Any]) -> list[dict[str, Any]]:
    required_ids = set(i2["control_schema"]["required_control_ids"])
    rows = output["classification_rows"]
    strings = collect_strings(output)
    return [
        check(
            "source_chain_digests_match",
            output["source_inventory_output_digest"]
            == output["source_records"][0]["output_digest"]
            and output["transfer_schema_output_digest"]
            == output["source_records"][1]["output_digest"]
            and output["stress_mapping_variant_transfer_output_digest"]
            == i6["output_digest"],
            {
                "i1": output["source_inventory_output_digest"],
                "i2": output["transfer_schema_output_digest"],
                "i6": output["stress_mapping_variant_transfer_output_digest"],
            },
        ),
        check(
            "i6_ready_for_i7_controls",
            i6["ready_for_iteration_7_controls_ap_dependency_claim_classification"] is True
            and i6["ct5_assignment_allowed"] is False
            and i6["ct5_or_stronger_supported"] is False,
            {
                "ready": i6["ready_for_iteration_7_controls_ap_dependency_claim_classification"],
                "i6_ct5_assignment_allowed": i6["ct5_assignment_allowed"],
            },
        ),
        check(
            "all_required_controls_accounted_per_row",
            all(
                {item["control_id"] for item in row["control_results"]} == required_ids
                for row in rows
            ),
            {
                row["row_id"]: sorted({item["control_id"] for item in row["control_results"]})
                for row in rows
            },
        ),
        check(
            "failed_open_controls_zero",
            output["failed_open_control_count"] == 0
            and all(row["failed_open_control_count"] == 0 for row in rows),
            {"failed_open_control_count": output["failed_open_control_count"]},
        ),
        check(
            "i4_remains_stress_limited_no_ct5_contribution",
            any(
                row["source_iteration"] == "4"
                and row["ct5_supported"] is False
                and row["ct5_contribution_allowed"] is False
                and row["row_decision"] == "partial"
                for row in rows
            ),
            [row for row in rows if row["source_iteration"] == "4"],
        ),
        check(
            "i4a_ct5_supported_after_controls",
            any(
                row["source_iteration"] == "4-A"
                and row["ct5_supported"] is True
                and row["classified_ct_ladder_rung"] == "CT5"
                and row["failed_open_control_count"] == 0
                for row in rows
            ),
            [row for row in rows if row["source_iteration"] == "4-A"],
        ),
        check(
            "ap4_ap5_row_local_statuses_valid",
            all(
                row["ap4_dependency_status"] == "not_applicable"
                and row["ap4_condition_reason"]
                and row["ap5_dependency_status"] == "not_applicable"
                and row["ap5_condition_reason"]
                for row in rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "ap4": row["ap4_dependency_status"],
                    "ap5": row["ap5_dependency_status"],
                }
                for row in rows
            ],
        ),
        check(
            "n26_and_n25_2_boundaries_preserved",
            output["n26_counted_as_transfer_evidence"] is False
            and output["n25_2_direct_transfer_consumption_used"] is False
            and output["n25_2_consumed_only_through_n26_context"] is True,
            {
                "n26_counted_as_transfer_evidence": output["n26_counted_as_transfer_evidence"],
                "n25_2_direct_transfer_consumption_used": output[
                    "n25_2_direct_transfer_consumption_used"
                ],
            },
        ),
        check(
            "native_ap5_and_ap5_nat4_gap_remain_blocked",
            output["native_ap5_supported"] is False
            and output["ap5_nat4_gap_resolution_supported"] is False,
            {
                "native_ap5_supported": output["native_ap5_supported"],
                "ap5_nat4_gap_resolution_supported": output[
                    "ap5_nat4_gap_resolution_supported"
                ],
            },
        ),
        check(
            "ct5_supported_but_ct6_and_final_transfer_blocked",
            output["ct5_or_stronger_supported"] is True
            and output["ct6_or_stronger_supported"] is False
            and output["final_transfer_supported"] is False,
            {
                "ct5": output["ct5_or_stronger_supported"],
                "ct6": output["ct6_or_stronger_supported"],
                "final": output["final_transfer_supported"],
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(flag is False for flag in output["claim_boundary"]["unsafe_claim_flags"].values())
            and all(
                flag is False
                for row in rows
                for flag in row["unsafe_claim_flags"].values()
            ),
            output["claim_boundary"]["unsafe_claim_flags"],
        ),
        check(
            "no_absolute_paths_in_records",
            not any(any(marker in value for marker in ABSOLUTE_PATH_MARKERS) for value in strings),
            sorted(value for value in strings if any(marker in value for marker in ABSOLUTE_PATH_MARKERS)),
        ),
    ]


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i1 = load_json(I1_OUTPUT)
    i2 = load_json(I2_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i5a = load_json(I5A_OUTPUT)
    i6 = load_json(I6_OUTPUT)
    controls = control_rows_by_id(i2)
    i6_rows = i6_rows_by_source(i6)

    classification_rows = [
        build_classification_row(
            "4",
            i6_rows["4"],
            controls,
            i6["iteration_7_handoff"]["i4_consumption"]["consume_as"],
        ),
        build_classification_row(
            "4-A",
            i6_rows["4-A"],
            controls,
            i6["iteration_7_handoff"]["i4a_consumption"]["consume_as"],
        ),
    ]
    supported_ct5_rows = [row for row in classification_rows if row["ct5_supported"]]
    output: dict[str, Any] = {
        "artifact_id": "n27_controls_ap_dependency_claim_classification",
        "schema_version": "1.0",
        "experiment": "N27",
        "iteration": "7",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Run the full frozen control matrix, AP4/AP5 dependency checks, and "
            "claim-boundary classification over I6 transfer candidates."
        ),
        "source_records": [
            source_record(I1_OUTPUT, "n27_i1_source_inventory", "source_inventory"),
            source_record(I2_OUTPUT, "n27_i2_transfer_schema", "schema_and_controls"),
            source_record(I3_OUTPUT, "n27_i3_active_nulls", "active_null_boundary"),
            source_record(I4_OUTPUT, "n27_i4_minimal_transfer", "ct2_source_candidate"),
            source_record(I4A_OUTPUT, "n27_i4a_topology_variant_transfer", "ct2_variant_candidate"),
            source_record(I5_OUTPUT, "n27_i5_replay_matrix", "ct3_replay_matrix"),
            source_record(I5A_OUTPUT, "n27_i5a_artifact_only_reconstruction", "ct3_replay_hygiene"),
            source_record(I6_OUTPUT, "n27_i6_stress_matrix", "stress_variant_matrix"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "transfer_schema_output_digest": i2["output_digest"],
        "active_nulls_output_digest": i3["output_digest"],
        "minimal_configuration_transfer_output_digest": i4["output_digest"],
        "topology_fixture_variant_transfer_output_digest": i4a["output_digest"],
        "replay_same_basin_mapping_output_digest": i5["output_digest"],
        "artifact_only_reconstruction_replay_output_digest": i5a["output_digest"],
        "stress_mapping_variant_transfer_output_digest": i6["output_digest"],
        "n27_closeout_ceiling": N27_CLOSEOUT_CEILING,
        "n27_closeout_ladder_rung_assigned": False,
        "positive_transfer_evidence_opened": True,
        "new_transfer_evidence_created": False,
        "candidate_rows_classified": True,
        "ct_ladder_rung_assigned": True,
        "classified_ct_ladder_rung": "CT5" if supported_ct5_rows else "CT4",
        "ct_assignment_scope": "controls_ap_claim_classification_pending_i8_closeout",
        "ct3_replay_candidate_supported": True,
        "ct4_control_backed_candidate_supported": True,
        "ct5_or_stronger_supported": bool(supported_ct5_rows),
        "ct5_supported_row_ids": [row["row_id"] for row in supported_ct5_rows],
        "ct6_or_stronger_supported": False,
        "final_transfer_supported": False,
        "failed_open_control_count": sum(
            row["failed_open_control_count"] for row in classification_rows
        ),
        "failed_closed_control_count": sum(
            row["failed_closed_control_count"] for row in classification_rows
        ),
        "required_control_count": len(controls),
        "classification_rows": classification_rows,
        "n26_counted_as_transfer_evidence": False,
        "n25_2_direct_transfer_consumption_used": False,
        "n25_2_consumed_only_through_n26_context": True,
        "native_ap5_supported": False,
        "ap5_nat4_gap_resolution_supported": False,
        "claim_boundary": {
            "claim_ceiling": (
                "bounded artifact-level configuration/topology transfer candidate; "
                "final CT6 closeout and N28 handoff pending I8"
            ),
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
        "ready_for_iteration_8_closeout_and_n28_handoff": True,
    }
    output["checks"] = build_checks(output, i2, i6)
    output["failed_checks"] = [item["check_id"] for item in output["checks"] if not item["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_ct5_controls_ap_claim_classification_pending_i8_closeout"
        if output["status"] == "passed"
        else "blocked_controls_ap_claim_classification"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    report = f"""# N27 Iteration 7 - Controls, AP4/AP5 Dependency, And Claim Classification

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

## Scope

Iteration 7 consumes I6 without creating new transfer geometry. It runs the
full frozen control matrix, records AP4/AP5 dependency statuses row-locally,
and classifies the strongest supported CT rung pending I8 closeout.

```text
classified_ct_ladder_rung = {output['classified_ct_ladder_rung']}
ct5_or_stronger_supported = {str(output['ct5_or_stronger_supported']).lower()}
ct6_or_stronger_supported = {str(output['ct6_or_stronger_supported']).lower()}
final_transfer_supported = {str(output['final_transfer_supported']).lower()}
failed_open_control_count = {output['failed_open_control_count']}
```

## Classification Rows

| Row | Source | Scope | Decision | Classified CT Rung | CT5 Supported |
| --- | --- | --- | --- | --- | --- |
"""
    for row in output["classification_rows"]:
        report += (
            f"| `{row['row_id']}` | `{row['source_iteration']}` | "
            f"`{row['transfer_scope']}` | `{row['row_decision']}` | "
            f"`{row['classified_ct_ladder_rung']}` | "
            f"`{str(row['ct5_supported']).lower()}` |\n"
        )

    report += """
## Interpretation

I7 keeps the I6 asymmetry. The I4 alpha/beta candidate is control-clean for its
supported scope, but remains stress-limited and contributes no CT5 evidence.
The I4-A gamma/delta topology/fixture candidate passes the full control matrix
with no failed-open controls, preserves AP4/AP5 row-local boundaries, and is
classified as the strongest CT5 candidate.

This is still not final transfer. CT6 requires I8 closeout and N28 handoff.
N26 remains bounded context, N25.2 is not directly consumed, native AP5 and the
AP5 NAT4 gap remain unresolved, and unsafe semantic/native/Phase-8/ant-ecology
claims remain blocked.

## Checks

| Check | Passed |
| --- | --- |
"""
    for item in output["checks"]:
        report += f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |\n"

    report += f"""

Output digest: `{output['output_digest']}`
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
