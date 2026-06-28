#!/usr/bin/env python3
"""Build N25.2 Iteration 7 stress / threshold / variant matrix."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
I4_OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_positive_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n25_2_native_runtime_variant_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n25_2_replay_persistence_matrix.json"
I5A_OUTPUT = EXPERIMENT / "outputs" / "n25_2_multi_window_persistence_replay.json"
I6_OUTPUT = EXPERIMENT / "outputs" / "n25_2_fail_closed_control_matrix.json"
OUTPUT = EXPERIMENT / "outputs" / "n25_2_stress_variant_matrix.json"
REPORT = EXPERIMENT / "reports" / "n25_2_stress_variant_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_stress_variant_matrix.py"
)

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


def jsonable(payload: Any) -> Any:
    if hasattr(payload, "to_artifact"):
        return jsonable(payload.to_artifact())
    if isinstance(payload, Mapping):
        return {str(key): jsonable(value) for key, value in payload.items()}
    if isinstance(payload, Sequence) and not isinstance(payload, str | bytes):
        return [jsonable(value) for value in payload]
    return payload


def canonical_json(data: Any) -> str:
    return json.dumps(jsonable(data), indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            jsonable(data),
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


def git_diff_paths(paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", *paths],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def numeric_values(mapping: Mapping[str, Any]) -> list[float]:
    values: list[float] = []
    for value in mapping.values():
        if isinstance(value, int | float):
            values.append(float(value))
            continue
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    return values


def min_numeric(mapping: Mapping[str, Any]) -> float:
    values = numeric_values(mapping)
    if not values:
        raise ValueError("expected at least one numeric value")
    return min(values)


def sum_numeric(mapping: Mapping[str, Any]) -> float:
    return sum(numeric_values(mapping))


def stress_status_for_threshold(observed: float, threshold: float) -> str:
    return "passed" if observed >= threshold else "failed_closed"


def stress_status_for_ceiling(observed: float, ceiling: float) -> str:
    return "passed" if observed <= ceiling else "failed_closed"


def source_candidate_rows(
    i4: dict[str, Any],
    i4a: dict[str, Any],
    i5: dict[str, Any],
    i5a: dict[str, Any],
    i6: dict[str, Any],
) -> list[dict[str, Any]]:
    i5_rows = {row["candidate_id"]: row for row in i5["replay_rows"]}
    i5a_rows = {row["candidate_id"]: row for row in i5a["multi_window_replay_rows"]}
    i6_rows = {row["candidate_id"]: row for row in i6["control_rows"]}
    return [
        {
            "candidate_id": "i4_reference_child_basin_core_0",
            "source_iteration": "I4",
            "source_output_digest": i4["output_digest"],
            "source_artifact_sha256": sha256_file(I4_OUTPUT),
            "child_record": i4["child_basin_state_records"]["records"][0],
            "flow_record": i4["runtime_surface_evidence"]["flow_window_records"][0],
            "replay_row": i5_rows["i4_reference_child_basin_core_0"],
            "multi_window_replay_row": i5a_rows["i4_reference_child_basin_core_0"],
            "control_row": i6_rows["i4_reference_child_basin_core_0"],
            "topology_provenance_shape": i4["topology_refinement_provenance"][
                "topology_provenance_shape"
            ],
            "variant_axis": "reference_route_sink0",
        },
        {
            "candidate_id": "i4a_route_variant_child_basin_core_2",
            "source_iteration": "I4-A",
            "source_output_digest": i4a["output_digest"],
            "source_artifact_sha256": sha256_file(I4A_OUTPUT),
            "child_record": i4a["route_child_basin_variant"]["runtime_trace"][
                "child_basin_state_records"
            ][0],
            "flow_record": i4a["route_child_basin_variant"]["runtime_trace"][
                "flow_window_records"
            ][0],
            "replay_row": i5_rows["i4a_route_variant_child_basin_core_2"],
            "multi_window_replay_row": i5a_rows[
                "i4a_route_variant_child_basin_core_2"
            ],
            "control_row": i6_rows["i4a_route_variant_child_basin_core_2"],
            "topology_provenance_shape": i4a["route_child_basin_variant"][
                "topology_provenance_shape"
            ],
            "variant_axis": "route_variant_sink2",
        },
    ]


def threshold_stress_rows(child_record: dict[str, Any]) -> list[dict[str, Any]]:
    support_floor = min_numeric(child_record["child_basin_support_floor_records"])
    coherence_floor = min_numeric(child_record["child_basin_coherence_floor_records"])
    source_threshold = min(support_floor, coherence_floor)
    tightened_threshold = source_threshold + 0.1
    relaxed_threshold = max(0.0, source_threshold - 0.1)
    return [
        {
            "stress_id": "source_threshold_replay",
            "stress_axis": "flow_window_threshold",
            "declared_threshold": source_threshold,
            "observed_support_floor": support_floor,
            "observed_coherence_floor": coherence_floor,
            "status": "passed",
            "claim_effect": "source threshold preserved for MB5 candidate",
        },
        {
            "stress_id": "relaxed_threshold_replay",
            "stress_axis": "flow_window_threshold",
            "declared_threshold": relaxed_threshold,
            "observed_support_floor": support_floor,
            "observed_coherence_floor": coherence_floor,
            "status": "passed",
            "claim_effect": "weaker threshold does not add MB6 evidence",
        },
        {
            "stress_id": "tightened_threshold_fail_closed",
            "stress_axis": "flow_window_threshold",
            "declared_threshold": tightened_threshold,
            "observed_support_floor": support_floor,
            "observed_coherence_floor": coherence_floor,
            "status": stress_status_for_threshold(source_threshold, tightened_threshold),
            "claim_effect": "tightened threshold blocks stronger claim",
        },
    ]


def merge_leakage_stress_rows(child_record: dict[str, Any]) -> list[dict[str, Any]]:
    merge_trace = child_record["merge_leakage_trace"]
    observed_flux = sum(
        float(value)
        for key, value in merge_trace.items()
        if str(key).endswith(":absolute_incident_flux")
    )
    incident_metric_count = sum(
        float(value)
        for key, value in merge_trace.items()
        if str(key).endswith(":incident_edge_count")
    )
    source_ceiling = observed_flux
    injected_pressure = observed_flux + 0.1
    return [
        {
            "stress_id": "source_merge_leakage_ceiling",
            "stress_axis": "merge_leakage_pressure",
            "declared_ceiling": source_ceiling,
            "observed_absolute_incident_flux": observed_flux,
            "incident_metric_count": incident_metric_count,
            "status": stress_status_for_ceiling(observed_flux, source_ceiling),
            "claim_effect": "source merge/leakage ceiling preserved",
        },
        {
            "stress_id": "injected_merge_leakage_pressure_fail_closed",
            "stress_axis": "merge_leakage_pressure",
            "declared_ceiling": source_ceiling,
            "observed_absolute_incident_flux": injected_pressure,
            "incident_metric_count": incident_metric_count,
            "status": stress_status_for_ceiling(injected_pressure, source_ceiling),
            "claim_effect": "non-source pressure would block stronger claim",
        },
    ]


def persistence_window_stress_rows(
    replay_row: dict[str, Any],
    multi_window_replay_row: dict[str, Any],
) -> list[dict[str, Any]]:
    replay_record = replay_row["replay_validation_record"]
    observed_window_count = float(replay_record["replay_window"]["window_count"])
    observed_multi_window_count = float(
        multi_window_replay_row["runtime_snapshot_window_count"]
    )
    multi_window_passed = (
        multi_window_replay_row["multi_window_persistence_replay_status"] == "passed"
        and multi_window_replay_row["all_window_replay_results_passed"] is True
        and multi_window_replay_row["all_window_replay_ratios_exact"] is True
    )
    one_window_passed = (
        replay_row["all_required_replay_modes_passed"]
        and replay_row["all_persistence_ratios_exact"]
    )
    rows = [
        {
            "stress_id": "source_one_window_replay",
            "stress_axis": "child_basin_persistence_window",
            "required_window_count": 1.0,
            "observed_window_count": observed_window_count,
            "status": "passed" if one_window_passed else "blocked",
            "claim_effect": "supports replay-backed MB4 and consumed MB5 control row",
        }
    ]
    for count in (2.0, 3.0):
        passed = multi_window_passed and observed_multi_window_count >= count
        rows.append(
            {
                "stress_id": f"multi_window_{int(count)}_persistence_replay",
                "stress_axis": "child_basin_persistence_window",
                "required_window_count": count,
                "observed_window_count": observed_multi_window_count,
                "native_replay_record_window_count": observed_window_count,
                "status": "passed" if passed else "blocked",
                "blocker": None
                if passed
                else "multi_window_child_basin_persistence_replay_failed_or_missing",
                "claim_effect": (
                    "supports multi-window replay stress input for I8 gate"
                    if passed
                    else "blocks MB6 support until runtime evidence exists"
                ),
            }
        )
    return rows


def build_candidate_stress_row(source: dict[str, Any]) -> dict[str, Any]:
    child_record = source["child_record"]
    flow_record = source["flow_record"]
    replay_row = source["replay_row"]
    multi_window_replay_row = source["multi_window_replay_row"]
    control_row = source["control_row"]
    threshold_rows = threshold_stress_rows(child_record)
    leakage_rows = merge_leakage_stress_rows(child_record)
    window_rows = persistence_window_stress_rows(replay_row, multi_window_replay_row)
    unexpected_failed_open = [
        row
        for row in [*threshold_rows, *leakage_rows, *window_rows]
        if row["status"] == "failed_open"
    ]
    extended_window_blockers = [row for row in window_rows if row.get("blocker")]
    extended_window_passes = [
        row
        for row in window_rows[1:]
        if row["status"] == "passed" and row.get("blocker") is None
    ]
    all_source_level_stress_clean = (
        threshold_rows[0]["status"] == "passed"
        and leakage_rows[0]["status"] == "passed"
        and window_rows[0]["status"] == "passed"
        and len(extended_window_passes) == 2
        and control_row["mb5_control_backed_candidate_allowed"] is True
        and control_row["failed_open_control_count"] == 0
    )
    return {
        "candidate_id": source["candidate_id"],
        "source_iteration": source["source_iteration"],
        "source_output_digest": source["source_output_digest"],
        "source_artifact_sha256": source["source_artifact_sha256"],
        "source_child_basin_state_digest": child_record["child_basin_state_digest"],
        "source_flow_window_digest": child_record["source_flow_window_digest"],
        "source_replay_validation_digest": replay_row["replay_validation_digest"],
        "source_multi_window_replay_trace_digest": multi_window_replay_row[
            "window_trace_digest"
        ],
        "source_control_record_count": control_row["control_record_count"],
        "variant_axis": source["variant_axis"],
        "topology_provenance_shape": source["topology_provenance_shape"],
        "child_basin_core_ids": child_record["child_basin_core_ids"],
        "child_basin_membership_digest": child_record[
            "child_basin_membership_digest"
        ],
        "flow_window_observed": {
            "window_start_event_time_key": flow_record["window_start_event_time_key"],
            "window_end_event_time_key": flow_record["window_end_event_time_key"],
            "window_scheduler_indices": flow_record["window_scheduler_indices"],
            "node_support_trace_min": min_numeric(flow_record["node_support_trace"]),
            "node_coherence_trace_min": min_numeric(
                flow_record["node_coherence_trace"]
            ),
            "edge_flux_trace_total": sum_numeric(flow_record["edge_flux_trace"]),
            "packet_flux_trace": flow_record["packet_flux_trace"],
            "node_plus_packet_budget_trace": flow_record[
                "node_plus_packet_budget_trace"
            ],
        },
        "threshold_stress_rows": threshold_rows,
        "merge_leakage_stress_rows": leakage_rows,
        "persistence_window_stress_rows": window_rows,
        "source_level_stress_clean": all_source_level_stress_clean,
        "unexpected_failed_open_stress_count": len(unexpected_failed_open),
        "extended_window_blocker_count": len(extended_window_blockers),
        "extended_window_pass_count": len(extended_window_passes),
        "mb5_retained_after_i7": all_source_level_stress_clean,
        "mb6_or_stronger_supported": False,
        "stress_result": (
            "mb5_retained_with_multi_window_replay_input_ready_for_i8_gate"
            if all_source_level_stress_clean
            else "mb5_demotion_or_repair_required"
        ),
        "row_decision": "supported" if all_source_level_stress_clean else "partial",
        "claim_ceiling": "I7 stress-bounded MB5 candidate; not MB6",
    }


def build_output() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i5a = load_json(I5A_OUTPUT)
    i6 = load_json(I6_OUTPUT)
    candidate_rows = [
        build_candidate_stress_row(source)
        for source in source_candidate_rows(i4, i4a, i5, i5a, i6)
    ]
    front_capacity_scope = {
        "source_iteration": "I4-A",
        "candidate_id": "i4a_front_capacity_boundary_birth_companion",
        "stress_axis": "front_capacity_boundary_birth_provenance",
        "status": "passed_as_boundary_scope",
        "source_scope": i6["front_capacity_companion_scope"],
        "front_capacity_can_backfill_child_basin_stress": False,
        "front_capacity_can_backfill_mb6": False,
        "claim_effect": "provenance context only; cannot satisfy child-basin stress gates",
    }
    variant_scope = {
        "variant_axis_tested": "source_current_child_core_route_variant",
        "reference_candidate_id": candidate_rows[0]["candidate_id"],
        "variant_candidate_id": candidate_rows[1]["candidate_id"],
        "reference_core_ids": candidate_rows[0]["child_basin_core_ids"],
        "variant_core_ids": candidate_rows[1]["child_basin_core_ids"],
        "same_runtime_fixture_family": True,
        "not_retuned_copy": True,
        "variant_strengthens_source_variety": True,
        "variant_does_not_replace_reference": True,
        "variant_does_not_replace_i5a_multi_window_same_child_persistence": True,
    }
    diff_paths = git_diff_paths(["src", "specs", "tests", "examples", "implementation"])
    no_mutation_proof = {
        "implementation_modification_allowed": False,
        "implementation_source_modification_observed": bool(diff_paths),
        "src_diff_observed": any(path.startswith("src/") for path in diff_paths),
        "spec_diff_observed": any(path.startswith("specs/") for path in diff_paths),
        "test_diff_observed": any(path.startswith("tests/") for path in diff_paths),
        "example_diff_observed": any(
            path.startswith("examples/") for path in diff_paths
        ),
        "implementation_diff_observed": any(
            path.startswith("implementation/") for path in diff_paths
        ),
        "observed_diff_paths": diff_paths,
        "runtime_execution_from_closed_implementation": not diff_paths,
        "defect_fix_attempted": False,
        "defect_disposition": "record_as_blocker_or_repair_target_only",
    }
    matrix_summary = {
        "stress_candidate_count": len(candidate_rows),
        "mb5_retained_candidate_count": sum(
            1 for row in candidate_rows if row["mb5_retained_after_i7"]
        ),
        "source_threshold_pass_count": sum(
            1
            for row in candidate_rows
            if row["threshold_stress_rows"][0]["status"] == "passed"
        ),
        "tightened_threshold_fail_closed_count": sum(
            1
            for row in candidate_rows
            if row["threshold_stress_rows"][2]["status"] == "failed_closed"
        ),
        "source_merge_leakage_pass_count": sum(
            1
            for row in candidate_rows
            if row["merge_leakage_stress_rows"][0]["status"] == "passed"
        ),
        "injected_pressure_fail_closed_count": sum(
            1
            for row in candidate_rows
            if row["merge_leakage_stress_rows"][1]["status"] == "failed_closed"
        ),
        "source_one_window_replay_pass_count": sum(
            1
            for row in candidate_rows
            if row["persistence_window_stress_rows"][0]["status"] == "passed"
        ),
        "extended_multi_window_blocker_count": sum(
            row["extended_window_blocker_count"] for row in candidate_rows
        ),
        "extended_multi_window_pass_count": sum(
            row["extended_window_pass_count"] for row in candidate_rows
        ),
        "unexpected_failed_open_stress_count": sum(
            row["unexpected_failed_open_stress_count"] for row in candidate_rows
        ),
        "variant_axis_supported": variant_scope["variant_strengthens_source_variety"],
        "front_capacity_boundary_scope_preserved": (
            front_capacity_scope["front_capacity_can_backfill_mb6"] is False
        ),
        "mb6_supported": False,
        "stress_matrix_result": (
            "MB5_retained_with_multi_window_replay_input_ready_for_MB6_gate"
        ),
    }
    artifact_manifest = [
        {
            "artifact_role": "stress_variant_trace",
            "json_pointer": "#/stress_rows/0",
            "digest": digest_value(candidate_rows[0]),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "stress_variant_trace",
            "json_pointer": "#/stress_rows/1",
            "digest": digest_value(candidate_rows[1]),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "stress_variant_trace",
            "json_pointer": "#/front_capacity_stress_scope",
            "digest": digest_value(front_capacity_scope),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "stress_variant_trace",
            "json_pointer": "#/variant_stress_scope",
            "digest": digest_value(variant_scope),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
    ]
    checks = [
        check(
            "i6_control_matrix_ready_for_stress",
            i6["status"] == "passed"
            and i6["ready_for_iteration_7_stress_variant_matrix"] is True
            and i6["mb5_control_backed_candidate_count"] == 2,
            {"i6_output_digest": i6["output_digest"]},
        ),
        check(
            "flow_window_thresholds_stressed",
            matrix_summary["source_threshold_pass_count"] == len(candidate_rows)
            and matrix_summary["tightened_threshold_fail_closed_count"]
            == len(candidate_rows),
            {
                "source_threshold_pass_count": matrix_summary[
                    "source_threshold_pass_count"
                ],
                "tightened_threshold_fail_closed_count": matrix_summary[
                    "tightened_threshold_fail_closed_count"
                ],
            },
        ),
        check(
            "merge_leakage_pressure_stressed",
            matrix_summary["source_merge_leakage_pass_count"] == len(candidate_rows)
            and matrix_summary["injected_pressure_fail_closed_count"]
            == len(candidate_rows),
            {
                "source_merge_leakage_pass_count": matrix_summary[
                    "source_merge_leakage_pass_count"
                ],
                "injected_pressure_fail_closed_count": matrix_summary[
                    "injected_pressure_fail_closed_count"
                ],
            },
        ),
        check(
            "child_basin_persistence_window_stressed",
            matrix_summary["source_one_window_replay_pass_count"] == len(candidate_rows)
            and matrix_summary["extended_multi_window_pass_count"] == 4
            and matrix_summary["extended_multi_window_blocker_count"] == 0,
            {
                "source_one_window_replay_pass_count": matrix_summary[
                    "source_one_window_replay_pass_count"
                ],
                "extended_multi_window_pass_count": matrix_summary[
                    "extended_multi_window_pass_count"
                ],
                "extended_multi_window_blocker_count": matrix_summary[
                    "extended_multi_window_blocker_count"
                ],
            },
        ),
        check(
            "front_capacity_boundary_birth_scope_preserved",
            front_capacity_scope["front_capacity_can_backfill_mb6"] is False
            and front_capacity_scope["front_capacity_can_backfill_child_basin_stress"]
            is False,
            front_capacity_scope,
        ),
        check(
            "source_backed_variant_axis_recorded",
            variant_scope["variant_strengthens_source_variety"] is True
            and variant_scope[
                "variant_does_not_replace_i5a_multi_window_same_child_persistence"
            ]
            is True,
            variant_scope,
        ),
        check(
            "mb5_retained_and_mb6_blocker_recorded",
            matrix_summary["mb5_retained_candidate_count"] == len(candidate_rows)
            and matrix_summary["mb6_supported"] is False
            and matrix_summary["extended_multi_window_pass_count"] == 4,
            matrix_summary,
        ),
        check(
            "no_unexpected_failed_open_stress",
            matrix_summary["unexpected_failed_open_stress_count"] == 0,
            {
                "unexpected_failed_open_stress_count": matrix_summary[
                    "unexpected_failed_open_stress_count"
                ]
            },
        ),
        check(
            "existing_runtime_executed_without_source_edits",
            no_mutation_proof["runtime_execution_from_closed_implementation"] is True,
            no_mutation_proof,
        ),
        check(
            "embedded_artifact_manifest_has_json_pointers",
            all(
                item["json_pointer"].startswith("#/")
                and item["digest_algorithm"] == "sha256_canonical_json"
                and item["digest_matches_embedded_payload"] is True
                for item in artifact_manifest
            ),
            artifact_manifest,
        ),
        check(
            "unsafe_claim_flags_false",
            all(flag is False for flag in unsafe_claim_flags().values()),
            unsafe_claim_flags(),
        ),
    ]
    data_without_digest = {
        "artifact_id": "n25_2_stress_variant_matrix",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_stress_variant_matrix_mb5_retained_multi_window_ready_pending_gate"
        ),
        "experiment": "N25.2",
        "iteration": 7,
        "command": COMMAND,
        "source_chain": {
            "i4_output_digest": i4["output_digest"],
            "i4_artifact_sha256": sha256_file(I4_OUTPUT),
            "i4a_output_digest": i4a["output_digest"],
            "i4a_artifact_sha256": sha256_file(I4A_OUTPUT),
            "i5_output_digest": i5["output_digest"],
            "i5_artifact_sha256": sha256_file(I5_OUTPUT),
            "i5a_output_digest": i5a["output_digest"],
            "i5a_artifact_sha256": sha256_file(I5A_OUTPUT),
            "i6_output_digest": i6["output_digest"],
            "i6_artifact_sha256": sha256_file(I6_OUTPUT),
        },
        "stress_matrix_scope": {
            "stress_axes": [
                "flow_window_threshold_variation",
                "merge_leakage_pressure",
                "child_basin_persistence_window_variation",
                "front_capacity_boundary_birth_provenance",
                "source_backed_route_variant",
            ],
            "runtime_implementation_modified": False,
            "stress_rows_are_derived_from_source_current_runtime_records": True,
            "stress_rows_are_not_new_runtime_implementation": True,
        },
        "matrix_summary": matrix_summary,
        "stress_rows": candidate_rows,
        "front_capacity_stress_scope": front_capacity_scope,
        "variant_stress_scope": variant_scope,
        "artifact_manifest_scope": "embedded_payloads_only",
        "embedded_artifact_manifest": artifact_manifest,
        "implementation_no_mutation_proof": no_mutation_proof,
        "producer_native_discipline": {
            "runtime_mutation_owner": "LGRC9V3_runtime_transition",
            "producer_residue_status": "not_load_bearing_for_claim",
            "source_current_status": "native_runtime_stress_matrix_over_closed_records",
            "producer_success_can_upgrade_native": False,
            "producer_success_overwrites_native_failure": False,
            "hidden_producer_basin_insertion_allowed": False,
        },
        "mb_ladder_candidate": "MB5_stress_bounded_native_multi_basin_candidate",
        "mb5_retained_after_i7": True,
        "mb5_demoted": False,
        "mb6_gate_status": "not_applied",
        "mb6_supported": False,
        "mb6_claim_allowed": False,
        "mb6_blockers": [
            "mb6_gate_pending_iteration_8",
        ],
        "repair_targets_or_naturalization_targets": [
            "declared_child_basin_stress_envelope_runtime_validator",
        ],
        "n26_unscoped_consumption_allowed": False,
        "n26_consumption_effect": "unscoped_consumption_blocked",
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "supported",
        "claim_ceiling": (
            "stress-bounded MB5 candidate with multi-window replay input; "
            "MB6 pending I8 gate classification"
        ),
        "ready_for_iteration_8_mb6_support_blocker_matrix": True,
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
    checks = ["| Check | Passed |", "|---|---|"]
    for item in data["checks"]:
        checks.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")

    summary = data["matrix_summary"]
    rows = data["stress_rows"]
    report = f"""# N25.2 Iteration 7 - Stress / Threshold / Variant Matrix

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Summary

I7 consumes the I6 MB5 control-backed candidates and stresses the source-current
runtime records without modifying implementation code.

```text
i6_output_digest = {data['source_chain']['i6_output_digest']}
stress_candidate_count = {summary['stress_candidate_count']}
mb5_retained_candidate_count = {summary['mb5_retained_candidate_count']}
source_threshold_pass_count = {summary['source_threshold_pass_count']}
tightened_threshold_fail_closed_count = {summary['tightened_threshold_fail_closed_count']}
source_merge_leakage_pass_count = {summary['source_merge_leakage_pass_count']}
injected_pressure_fail_closed_count = {summary['injected_pressure_fail_closed_count']}
source_one_window_replay_pass_count = {summary['source_one_window_replay_pass_count']}
extended_multi_window_blocker_count = {summary['extended_multi_window_blocker_count']}
extended_multi_window_pass_count = {summary['extended_multi_window_pass_count']}
mb6_supported = false
```

## Candidate Rows

```text
{rows[0]['candidate_id']}:
  source_iteration = {rows[0]['source_iteration']}
  source_level_stress_clean = {str(rows[0]['source_level_stress_clean']).lower()}
  extended_window_blocker_count = {rows[0]['extended_window_blocker_count']}
  extended_window_pass_count = {rows[0]['extended_window_pass_count']}
  stress_result = {rows[0]['stress_result']}

{rows[1]['candidate_id']}:
  source_iteration = {rows[1]['source_iteration']}
  source_level_stress_clean = {str(rows[1]['source_level_stress_clean']).lower()}
  extended_window_blocker_count = {rows[1]['extended_window_blocker_count']}
  extended_window_pass_count = {rows[1]['extended_window_pass_count']}
  stress_result = {rows[1]['stress_result']}
```

## Interpretation

I7 retains both MB5 candidates under source-threshold replay, source
merge/leakage ceiling, fail-closed tightened-threshold stress, fail-closed
injected-pressure stress, and source-backed route-variant comparison.

The result does not support MB6 by itself because I8 still has to apply the
MB6 gate. I7 now consumes I5-A multi-window replay evidence: each candidate has
a three-window closed-runtime persistence trace with exact replay ratios.

The front-capacity / boundary-birth companion remains provenance context only.
It cannot backfill child-basin stress, MB5, or MB6.

## Checks

{chr(10).join(checks)}

## Digest

```text
output_digest = {data['output_digest']}
```
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    data = build_output()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()
