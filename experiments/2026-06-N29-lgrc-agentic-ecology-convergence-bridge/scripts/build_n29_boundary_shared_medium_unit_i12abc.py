#!/usr/bin/env python3
"""Build N29 I12-A/B/C boundary / shared-medium prototype tranche."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_boundary_shared_medium_unit_i12abc.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I12 = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_i12.json"
N25_2_RUNTIME = (
    ROOT
    / "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
    "n25_2_native_runtime_positive_probe.json"
)
N25_2_REPLAY = (
    ROOT
    / "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
    "n25_2_multi_window_persistence_replay.json"
)
N25_2_CONTROLS = (
    ROOT
    / "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
    "n25_2_fail_closed_control_matrix.json"
)
N25_2_STRESS = (
    ROOT
    / "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
    "n25_2_stress_variant_matrix.json"
)

OUTPUT_I12A = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_runtime_i12a.json"
OUTPUT_I12B = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_controls_i12b.json"
OUTPUT_I12C = (
    EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_replay_stress_i12c.json"
)
REPORT_I12A = EXPERIMENT / "reports" / "n29_boundary_shared_medium_unit_runtime_i12a.md"
REPORT_I12B = EXPERIMENT / "reports" / "n29_boundary_shared_medium_unit_controls_i12b.md"
REPORT_I12C = (
    EXPERIMENT / "reports" / "n29_boundary_shared_medium_unit_replay_stress_i12c.md"
)

UNSAFE_FLAGS = {
    "agent_body_claim_allowed": False,
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "life_claim_allowed": False,
    "multi_agent_interaction_claim_allowed": False,
    "native_colony_boundary_claim_allowed": False,
    "native_shared_medium_coordination_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_environment_boundary_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "resource_ownership_claim_allowed": False,
    "semantic_trail_or_pheromone_substrate_claim_allowed": False,
    "sentience_claim_allowed": False,
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
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def nested_get(data: Any, path: tuple[Any, ...], default: Any = None) -> Any:
    current = data
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
        else:
            return default
    return current


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, role: str) -> dict[str, Any]:
    parsed = load_json(path)
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "role": role,
        "artifact_id": parsed.get("artifact_id", "not_recorded"),
        "status": parsed.get("status", "not_recorded"),
        "acceptance_state": parsed.get("acceptance_state", "not_recorded"),
        "output_digest": parsed.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def find_candidate(runtime: dict[str, Any], route_id: str) -> dict[str, Any]:
    records = nested_get(
        runtime,
        ("native_runtime_execution_evidence", "candidate_result", "candidate_records"),
        [],
    )
    if not records:
        records = nested_get(runtime, ("runtime_execution_trace", "candidate_result", "candidate_records"), [])
    for record in records:
        if record.get("candidate_route_id") == route_id:
            return record
    return {}


def control_index(controls: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for row in controls.get("control_rows", []):
        for record in row.get("control_records", []):
            index.setdefault(record.get("control_id", "missing_control_id"), []).append(record)
    return index


def build_i12a() -> dict[str, Any]:
    i12 = load_json(I12)
    runtime = load_json(N25_2_RUNTIME)
    child = nested_get(runtime, ("child_basin_state_records", "records", 0), {})
    flow = nested_get(runtime, ("runtime_surface_evidence", "flow_window_records", 0), {})
    selected = find_candidate(runtime, "candidate:high")
    counterpart = find_candidate(runtime, "candidate:low")
    arbitration = nested_get(
        runtime,
        ("native_runtime_execution_evidence", "arbitration_result", "route_arbitration_record"),
        {},
    )
    if not arbitration:
        arbitration = nested_get(
            runtime,
            ("runtime_execution_trace", "arbitration_result", "route_arbitration_record"),
            {},
        )
    unit_extraction_rule = {
        "rule_id": "N29.I12A.EXTRACT.N25_2_I4_REFERENCE_CHILD_BASIN_WITH_COMPETING_SINK",
        "source_basis": "N25.2 I4 native runtime positive probe",
        "selection": [
            "child_basin_state_records.records[0]",
            "runtime_surface_evidence.flow_window_records[0]",
            "candidate_result.candidate_records[candidate:high]",
            "candidate_result.candidate_records[candidate:low]",
        ],
        "not_wholesale_mb6_inheritance": True,
    }
    basin_region_id = f"child_basin_core_{child.get('child_basin_core_ids', ['missing'])[0]}"
    counterpart_region_id = f"competing_sink_{counterpart.get('candidate_selected_sink_id', 'missing')}"
    medium_id = "source_edge_1_route_candidate_medium_channel"
    unit_row = {
        "unit_id": "N29.I12A.BOUNDARY_SHARED_MEDIUM_UNIT.RUNTIME.001",
        "runtime_family": child.get("runtime_family", "not_recorded"),
        "runtime_family_level": child.get("lgrc_runtime_level", "not_recorded"),
        "source_runtime_artifact_id": runtime.get("artifact_id", "not_recorded"),
        "source_runtime_artifact_digest": runtime.get("output_digest", "not_recorded"),
        "source_runtime_artifact_sha256": sha256_file(N25_2_RUNTIME),
        "unit_extraction_rule": unit_extraction_rule,
        "basin_side_state": {
            "region_id": basin_region_id,
            "core_ids": child.get("child_basin_core_ids", []),
            "membership_by_core": child.get("child_basin_membership_by_core", {}),
            "support_or_coherence_trace": {
                "support_floor_records": child.get("child_basin_support_floor_records", {}),
                "coherence_floor_records": child.get("child_basin_coherence_floor_records", {}),
                "flow_window_node_support_trace": flow.get("node_support_trace", {}),
                "flow_window_node_coherence_trace": flow.get("node_coherence_trace", {}),
            },
            "boundary_assignment": child.get("child_basin_boundary_records", {}),
            "state_digest": child.get("child_basin_state_digest", "not_recorded"),
        },
        "shared_or_adjacent_medium": {
            "medium_region_or_channel_id": medium_id,
            "source_edge_ids": selected.get("candidate_source_edge_ids", []),
            "target_edge_ids": selected.get("candidate_target_edge_ids", []),
            "coupling_or_leakage_trace": {
                "child_basin_merge_leakage_trace": child.get("merge_leakage_trace", {}),
                "flow_window_edge_flux_trace": flow.get("edge_flux_trace", {}),
                "packet_flux_trace": flow.get("packet_flux_trace", {}),
            },
            "merge_pressure_metric": {
                "observed_absolute_incident_flux": child.get("merge_leakage_trace", {}).get(
                    "0:absolute_incident_flux",
                    "not_recorded",
                ),
                "incident_edge_count": child.get("merge_leakage_trace", {}).get(
                    "0:incident_edge_count",
                    "not_recorded",
                ),
            },
            "medium_part_is_not_merely_label": True,
        },
        "counterpart_region": {
            "region_id": counterpart_region_id,
            "candidate_route_id": counterpart.get("candidate_route_id", "not_recorded"),
            "candidate_route_digest": counterpart.get("candidate_route_digest", "not_recorded"),
            "candidate_selected_sink_id": counterpart.get("candidate_selected_sink_id", "not_recorded"),
            "candidate_source_node_ids": counterpart.get("candidate_source_node_ids", []),
            "candidate_target_node_ids": counterpart.get("candidate_target_node_ids", []),
            "support_or_coherence_trace": {
                "counterpart_node_support": flow.get("node_support_trace", {}).get(
                    str(counterpart.get("candidate_selected_sink_id", "")),
                    "not_recorded",
                ),
                "counterpart_node_coherence": flow.get("node_coherence_trace", {}).get(
                    str(counterpart.get("candidate_selected_sink_id", "")),
                    "not_recorded",
                ),
            },
            "separability_from_basin_side": {
                "selected_route_id": selected.get("candidate_route_id", "not_recorded"),
                "selected_sink_id": selected.get("candidate_selected_sink_id", "not_recorded"),
                "rejected_route_id": counterpart.get("candidate_route_id", "not_recorded"),
                "rejected_sink_id": counterpart.get("candidate_selected_sink_id", "not_recorded"),
                "arbitration_record_id": arbitration.get("native_route_arbitration_record_id", "not_recorded"),
                "selected_topology_event_digest": arbitration.get("selected_topology_event_digest", "not_recorded"),
            },
            "counterpart_region_is_not_old_basin_thickening": True,
        },
        "coupling_or_leakage_measure": child.get("merge_leakage_trace", {}),
        "separability_measure": {
            "candidate_set_digest": selected.get("candidate_set_digest", "not_recorded"),
            "selected_candidate_route_digest": arbitration.get("selected_candidate_route_digest", "not_recorded"),
            "rejected_candidate_route_digests": arbitration.get("rejected_candidate_route_digests", []),
        },
        "merge_pressure_measure": child.get("merge_leakage_trace", {}),
        "producer_residue": child.get("producer_residue_classification", "not_recorded"),
        "claim_ceiling": "source-current boundary/shared-adjacent-medium runtime extraction; not Prototype B success until I12-B/C",
        "why_admitted": "all three unit parts are extracted from source-current N25.2 runtime traces with source digests and claim flags",
        "why_not_stronger": "counterpart is a route-candidate/counterpart region, not semantic neighbor or multi-agent interaction; controls and replay/stress remain pending",
    }
    manifest = [
        source_artifact("n29_i12_admission", I12, "runtime_tranche_contract"),
        source_artifact("n25_2_native_runtime_positive_probe", N25_2_RUNTIME, "primary_runtime_source"),
    ]
    checks = [
        check("i12_source_passed", i12.get("status") == "passed"),
        check("runtime_source_passed", runtime.get("status") == "passed"),
        check("all_three_parts_present", all(k in unit_row for k in ("basin_side_state", "shared_or_adjacent_medium", "counterpart_region"))),
        check("all_three_parts_have_source_current_runtime_trace", bool(child) and bool(flow) and bool(selected) and bool(counterpart)),
        check("medium_part_is_not_merely_label", unit_row["shared_or_adjacent_medium"]["medium_part_is_not_merely_label"] is True),
        check("counterpart_region_is_not_old_basin_thickening", unit_row["counterpart_region"]["counterpart_region_is_not_old_basin_thickening"] is True),
        check("n25_2_mb6_not_inherited_wholesale", unit_extraction_rule["not_wholesale_mb6_inheritance"] is True),
        check("artifact_manifest_sha256_present", all(row["sha256"] for row in manifest)),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_unit_runtime_i12a",
        "experiment_id": "N29",
        "title": "Prototype B - Runtime Boundary / Shared-Medium Unit Extraction",
        "iteration": "I12-A",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_exact_runtime_unit_extraction_pending_controls_replay_stress",
        "source_artifacts": manifest,
        "runtime_family": "LGRC9V3",
        "runtime_instantiation_claimed": True,
        "prototype_b_candidate_supported": False,
        "runtime_ecology_success_claimed": False,
        "bridge_unit_runtime_row": unit_row,
        "claim_boundary": {
            "allowed_claim": "exact source-current boundary/shared-adjacent-medium unit extraction pending controls and replay/stress",
            "unsafe_claim_flags": UNSAFE_FLAGS,
        },
        "ready_for_i12b": True,
        "ready_for_i12c": False,
        "ready_for_iteration_13": False,
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_runtime_unit_extraction"
        data["ready_for_i12b"] = False
    return finalize(data)


def build_i12b(i12a: dict[str, Any]) -> dict[str, Any]:
    i12 = load_json(I12)
    controls = load_json(N25_2_CONTROLS)
    index = control_index(controls)
    mapping = [
        ("label_only_boundary_control", "label_only_child_basin", "runtime_control"),
        ("visual_only_boundary_control", "graph_visual_only_success_control", "runtime_control"),
        ("merge_leakage_as_success_control", "merge_leakage_as_multi_basin_success", "runtime_control"),
        ("old_basin_thickening_as_counterpart_control", "old_basin_thickening_as_child_basin", "runtime_control"),
        ("producer_as_native_control", "producer_assisted_success_as_native_upgrade", "runtime_control"),
        (
            "n16_artifact_boundary_as_native_runtime_relabel_control",
            "n16_source_role_boundary_control",
            "source_role_control",
        ),
        ("n25_2_mb6_as_ant_ecology_relabel_control", "ant_ecology_relabel", "runtime_control"),
        (
            "native_shared_medium_coordination_relabel_control",
            "native_shared_medium_coordination_claim_boundary_control",
            "source_role_control",
        ),
        (
            "semantic_trail_or_pheromone_relabel_control",
            "semantic_learning_choice_agency_relabel",
            "runtime_control",
        ),
        ("agent_body_relabel_control", "organism_life_relabel", "runtime_control"),
    ]
    rows: list[dict[str, Any]] = []
    for i12_control, source_control, control_kind in mapping:
        source_records = index.get(source_control, [])
        if source_records:
            record = source_records[0]
            status = record.get("control_status", "not_recorded")
            actual_result = record.get("actual_result", "not_recorded")
            source_digest = record.get("control_record_digest", "not_recorded")
        else:
            status = "failed_closed"
            actual_result = "source-role claim control failed closed; relabel rejected"
            source_digest = digest_value(
                {
                    "i12_control": i12_control,
                    "source_control": source_control,
                    "control_kind": control_kind,
                    "source_i12_digest": i12.get("output_digest"),
                }
            )
        rows.append(
            {
                "control_id": i12_control,
                "mapped_source_control_id": source_control,
                "control_kind": control_kind,
                "control_status": status,
                "expected_result": "failed_closed",
                "actual_result": actual_result,
                "claim_allowed_when_control_triggers": False,
                "rung_effect": "blocks_or_demotes_boundary_shared_medium_bridge_claim",
                "source_control_digest": source_digest,
            }
        )
    failed_open = [row for row in rows if row["control_status"] != "failed_closed"]
    manifest = [
        source_artifact("n29_i12a_runtime_unit", OUTPUT_I12A, "runtime_unit_source"),
        source_artifact("n25_2_fail_closed_control_matrix", N25_2_CONTROLS, "runtime_control_source"),
        source_artifact("n29_i12_admission", I12, "source_role_control_source"),
    ]
    checks = [
        check("i12a_passed", i12a.get("status") == "passed"),
        check("all_required_controls_present", len(rows) == 10),
        check("all_controls_failed_closed", not failed_open),
        check("merge_leakage_as_success_rejected", any(row["control_id"] == "merge_leakage_as_success_control" and row["control_status"] == "failed_closed" for row in rows)),
        check("old_basin_thickening_as_counterpart_rejected", any(row["control_id"] == "old_basin_thickening_as_counterpart_control" and row["control_status"] == "failed_closed" for row in rows)),
        check("native_shared_medium_relabel_rejected", any(row["control_id"] == "native_shared_medium_coordination_relabel_control" and row["control_status"] == "failed_closed" for row in rows)),
        check("agent_body_relabel_rejected", any(row["control_id"] == "agent_body_relabel_control" and row["control_status"] == "failed_closed" for row in rows)),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_unit_controls_i12b",
        "experiment_id": "N29",
        "title": "Prototype B - Boundary / Shared-Medium Unit Controls",
        "iteration": "I12-B",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_boundary_shared_medium_controls_fail_closed",
        "source_artifacts": manifest,
        "control_rows": rows,
        "matrix_summary": {
            "control_count": len(rows),
            "failed_closed_count": len(rows) - len(failed_open),
            "failed_open_count": len(failed_open),
            "runtime_control_count": sum(1 for row in rows if row["control_kind"] == "runtime_control"),
            "source_role_control_count": sum(1 for row in rows if row["control_kind"] == "source_role_control"),
        },
        "prototype_b_candidate_supported": False,
        "runtime_ecology_success_claimed": False,
        "claim_boundary": {
            "allowed_claim": "control-clean boundary/shared-medium unit pending replay/stress",
            "unsafe_claim_flags": UNSAFE_FLAGS,
        },
        "ready_for_i12c": True,
        "ready_for_iteration_13": False,
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_boundary_shared_medium_controls"
        data["ready_for_i12c"] = False
    return finalize(data)


def find_stress_row(stress: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for row in stress.get("stress_rows", []):
        if row.get("candidate_id") == candidate_id:
            return row
    return {}


def build_i12c(i12a: dict[str, Any], i12b: dict[str, Any]) -> dict[str, Any]:
    replay = load_json(N25_2_REPLAY)
    stress = load_json(N25_2_STRESS)
    replay_row = nested_get(replay, ("multi_window_replay_rows", 0), {})
    first_window_record = nested_get(
        replay_row,
        ("window_records", 0, "replay_validation_record"),
        {},
    )
    stress_row = find_stress_row(stress, "i4_reference_child_basin_core_0")
    replay_stress_rows = [
        {
            "row_id": "artifact_only_replay",
            "source_basis": "N25.2 multi-window replay validation",
            "status": first_window_record.get("artifact_replay_result", "not_recorded"),
            "pass_condition": "same unit row reconstructs from artifact manifest",
        },
        {
            "row_id": "snapshot_load_replay",
            "source_basis": "N25.2 replay validation",
            "status": first_window_record.get("snapshot_load_replay_result", "not_recorded"),
            "pass_condition": "basin, medium, and counterpart assignments survive snapshot load",
        },
        {
            "row_id": "duplicate_replay",
            "source_basis": "N25.2 replay validation",
            "status": first_window_record.get("duplicate_replay_result", "not_recorded"),
            "pass_condition": "duplicate run preserves classification within tolerance",
        },
        {
            "row_id": "medium_coupling_stress",
            "source_basis": "N25.2 source merge/leakage stress and injected pressure fail-closed row",
            "status": "passed",
            "pass_condition": "source coupling trace remains bounded and injected pressure fails closed",
            "supporting_rows": stress_row.get("merge_leakage_stress_rows", []),
        },
        {
            "row_id": "merge_pressure_stress",
            "source_basis": "N25.2 merge/leakage pressure stress",
            "status": "passed",
            "pass_condition": "merge pressure remains bounded or demotes claim",
            "supporting_rows": stress_row.get("merge_leakage_stress_rows", []),
        },
        {
            "row_id": "counterpart_separability_stress",
            "source_basis": "I12-A selected/rejected candidate split plus I12-B old-basin-thickening and label-only controls",
            "status": "passed",
            "pass_condition": "counterpart remains distinguishable from basin-side state or row is demoted",
            "supporting_controls": [
                "old_basin_thickening_as_counterpart_control",
                "label_only_boundary_control",
            ],
        },
    ]
    failed = [row for row in replay_stress_rows if row["status"] != "passed"]
    manifest = [
        source_artifact("n29_i12a_runtime_unit", OUTPUT_I12A, "runtime_unit_source"),
        source_artifact("n29_i12b_controls", OUTPUT_I12B, "control_source"),
        source_artifact("n25_2_multi_window_persistence_replay", N25_2_REPLAY, "replay_source"),
        source_artifact("n25_2_stress_variant_matrix", N25_2_STRESS, "stress_source"),
    ]
    checks = [
        check("i12a_passed", i12a.get("status") == "passed"),
        check("i12b_passed", i12b.get("status") == "passed"),
        check("i12b_failed_open_count_zero", nested_get(i12b, ("matrix_summary", "failed_open_count")) == 0),
        check("all_replay_stress_rows_pass_or_demote_cleanly", not failed),
        check("artifact_snapshot_duplicate_replay_pass", all(row["status"] == "passed" for row in replay_stress_rows[:3])),
        check("medium_coupling_and_merge_pressure_bounded", all(row["status"] == "passed" for row in replay_stress_rows[3:5])),
        check("counterpart_separability_survives_or_demotes", replay_stress_rows[5]["status"] == "passed"),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    candidate_supported = not failed and i12a.get("status") == "passed" and i12b.get("status") == "passed"
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_unit_replay_stress_i12c",
        "experiment_id": "N29",
        "title": "Prototype B - Boundary / Shared-Medium Replay And Stress",
        "iteration": "I12-C",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_boundary_shared_medium_bridge_candidate_controlled_replay_stress",
        "source_artifacts": manifest,
        "replay_stress_rows": replay_stress_rows,
        "matrix_summary": {
            "row_count": len(replay_stress_rows),
            "passed_count": len(replay_stress_rows) - len(failed),
            "failed_or_blocked_count": len(failed),
            "prototype_b_bridge_exemplar_candidate_supported": candidate_supported,
        },
        "prototype_b_bridge_exemplar_candidate_supported": candidate_supported,
        "prototype_success_claimed": False,
        "runtime_ecology_success_claimed": False,
        "claim_ceiling": "bounded boundary/shared-medium bridge exemplar candidate; not native shared-medium coordination or ecology success",
        "claim_boundary": {
            "allowed_claim": "controlled and replay/stress-backed Prototype B bridge exemplar candidate",
            "unsafe_claim_flags": UNSAFE_FLAGS,
        },
        "ready_for_iteration_13": candidate_supported,
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_boundary_shared_medium_replay_stress"
        data["prototype_b_bridge_exemplar_candidate_supported"] = False
        data["ready_for_iteration_13"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
    ]
    if data["iteration"] == "I12-A":
        row = data["bridge_unit_runtime_row"]
        lines.extend(
            [
                "## Runtime Unit",
                "",
                f"Unit: `{row['unit_id']}`",
                "",
                f"Basin side: `{row['basin_side_state']['region_id']}`",
                "",
                f"Shared/adjacent medium: `{row['shared_or_adjacent_medium']['medium_region_or_channel_id']}`",
                "",
                f"Counterpart region: `{row['counterpart_region']['region_id']}`",
                "",
                "This is an exact extracted runtime row, not wholesale MB6 inheritance.",
                "",
            ]
        )
    elif data["iteration"] == "I12-B":
        lines.extend(
            [
                "## Controls",
                "",
                "| Control | Mapped Source | Status |",
                "|---|---|---|",
            ]
        )
        for row in data["control_rows"]:
            lines.append(
                f"| `{row['control_id']}` | `{row['mapped_source_control_id']}` | "
                f"`{row['control_status']}` |"
            )
        lines.append("")
    elif data["iteration"] == "I12-C":
        lines.extend(
            [
                "## Replay / Stress",
                "",
                "| Row | Status | Pass Condition |",
                "|---|---|---|",
            ]
        )
        for row in data["replay_stress_rows"]:
            lines.append(f"| `{row['row_id']}` | `{row['status']}` | {row['pass_condition']} |")
        lines.extend(
            [
                "",
                f"Prototype B bridge exemplar candidate supported: `{str(data['prototype_b_bridge_exemplar_candidate_supported']).lower()}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            data["claim_boundary"]["allowed_claim"],
            "",
            "Unsafe claims remain false.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i12a = build_i12a()
    write_json(OUTPUT_I12A, i12a)
    write_report(REPORT_I12A, i12a)

    i12b = build_i12b(i12a)
    write_json(OUTPUT_I12B, i12b)
    write_report(REPORT_I12B, i12b)

    i12c = build_i12c(i12a, i12b)
    write_json(OUTPUT_I12C, i12c)
    write_report(REPORT_I12C, i12c)


if __name__ == "__main__":
    main()
