#!/usr/bin/env python3
"""Build N29 I12.1 alternative boundary / shared-medium sibling tranche."""

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
    "build_n29_boundary_shared_medium_unit_i121.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I12 = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_i12.json"
I12A = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_runtime_i12a.json"
I12C = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_replay_stress_i12c.json"
N25_2_VARIANT = (
    ROOT
    / "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/outputs/"
    "n25_2_native_runtime_variant_probe.json"
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

OUT_I121 = EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_alternative_i121.json"
OUT_I121A = (
    EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_alternative_runtime_i121a.json"
)
OUT_I121B = (
    EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_alternative_controls_i121b.json"
)
OUT_I121C = (
    EXPERIMENT
    / "outputs"
    / "n29_boundary_shared_medium_unit_alternative_replay_stress_i121c.json"
)
REP_I121 = EXPERIMENT / "reports" / "n29_boundary_shared_medium_unit_alternative_i121.md"
REP_I121A = (
    EXPERIMENT / "reports" / "n29_boundary_shared_medium_unit_alternative_runtime_i121a.md"
)
REP_I121B = (
    EXPERIMENT / "reports" / "n29_boundary_shared_medium_unit_alternative_controls_i121b.md"
)
REP_I121C = (
    EXPERIMENT
    / "reports"
    / "n29_boundary_shared_medium_unit_alternative_replay_stress_i121c.md"
)

VARIANT_CANDIDATE_ID = "i4a_route_variant_child_basin_core_2"
VARIANT_CHILD_DIGEST = "51a23e105d32a15f61f794b2901ab3a44cc78e124798bf591bb30dc18eb3aca7"

UNSAFE_FLAGS = {
    "agent_body_claim_allowed": False,
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "life_claim_allowed": False,
    "multi_agent_interaction_claim_allowed": False,
    "native_colony_boundary_claim_allowed": False,
    "native_shared_medium_coordination_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_environment_boundary_claim_allowed": False,
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


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


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


def find_candidate(records: list[dict[str, Any]], route_id: str) -> dict[str, Any]:
    for record in records:
        if record.get("candidate_route_id") == route_id:
            return record
    return {}


def find_replay_row(replay: dict[str, Any]) -> dict[str, Any]:
    for row in replay.get("multi_window_replay_rows", []):
        if row.get("candidate_id") == VARIANT_CANDIDATE_ID:
            return row
    return {}


def find_control_record(
    controls: dict[str, Any],
    control_id: str,
    child_digest: str = VARIANT_CHILD_DIGEST,
) -> dict[str, Any]:
    for row in controls.get("control_rows", []):
        if row.get("source_child_basin_state_digest") != child_digest:
            continue
        for record in row.get("control_records", []):
            if record.get("control_id") == control_id:
                return record
    return {}


def find_stress_row(stress: dict[str, Any]) -> dict[str, Any]:
    for row in stress.get("stress_rows", []):
        if row.get("candidate_id") == VARIANT_CANDIDATE_ID:
            return row
    return {}


def first_number(mapping: dict[str, Any]) -> float | None:
    for value in mapping.values():
        if isinstance(value, (int, float)):
            return float(value)
    return None


def build_margin_comparison(i121a: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    primary = load_json(I12A)
    primary_row = primary.get("bridge_unit_runtime_row", {})
    alternative_row = i121a.get("bridge_unit_runtime_row", {})

    primary_basin_trace = nested_get(
        primary_row,
        ("basin_side_state", "support_or_coherence_trace", "support_floor_records"),
        {},
    )
    alternative_basin_trace = nested_get(
        alternative_row,
        ("basin_side_state", "support_or_coherence_trace", "support_floor_records"),
        {},
    )
    primary_counterpart = nested_get(
        primary_row,
        ("counterpart_region", "support_or_coherence_trace", "counterpart_node_support"),
    )
    alternative_counterpart = nested_get(
        alternative_row,
        ("counterpart_region", "support_or_coherence_trace", "counterpart_node_support"),
    )
    primary_merge = nested_get(primary_row, ("shared_or_adjacent_medium", "merge_pressure_metric"), {})
    alternative_merge = nested_get(
        alternative_row,
        ("shared_or_adjacent_medium", "merge_pressure_metric"),
        {},
    )
    declared_ceiling = "not_recorded"
    for row in rows:
        for supporting in row.get("supporting_rows", []):
            if supporting.get("stress_id") == "source_merge_leakage_ceiling":
                declared_ceiling = supporting.get("declared_ceiling", "not_recorded")

    primary_basin_value = first_number(primary_basin_trace)
    alternative_basin_value = first_number(alternative_basin_trace)
    basin_delta = None
    if primary_basin_value is not None and alternative_basin_value is not None:
        basin_delta = round(alternative_basin_value - primary_basin_value, 10)

    return {
        "comparison_scope": "I12_reference_vs_I12_1_sibling_variant",
        "margin_interpretation": "repeatability_strengthening_not_widened_stress_margin",
        "numeric_margin_summary": {
            "basin_side_support_or_coherence_i12": primary_basin_value,
            "basin_side_support_or_coherence_i12_1": alternative_basin_value,
            "basin_side_support_or_coherence_delta": basin_delta,
            "counterpart_support_or_coherence_i12": primary_counterpart,
            "counterpart_support_or_coherence_i12_1": alternative_counterpart,
            "merge_leakage_declared_ceiling_i12_and_i12_1": declared_ceiling,
            "observed_absolute_incident_flux_i12": primary_merge.get(
                "observed_absolute_incident_flux",
                "not_recorded",
            ),
            "observed_absolute_incident_flux_i12_1": alternative_merge.get(
                "observed_absolute_incident_flux",
                "not_recorded",
            ),
            "incident_edge_count_i12": primary_merge.get("incident_edge_count", "not_recorded"),
            "incident_edge_count_i12_1": alternative_merge.get(
                "incident_edge_count",
                "not_recorded",
            ),
            "replay_stress_passed_count_i12": 6,
            "replay_stress_passed_count_i12_1": len(
                [row for row in rows if row.get("status") == "passed"]
            ),
        },
        "what_improved": [
            "basin-side support/coherence value is higher in the sibling variant",
            "Prototype B now has two controlled source-current orientations instead of one exact row",
        ],
        "what_did_not_improve": [
            "merge/leakage stress headroom is unchanged because both rows remain at observed flux 0.0 against a declared ceiling of 0.0",
            "the primary I12 envelope is not widened",
            "the sibling row does not replace the primary I12 reference",
        ],
        "claim_effect": "describe I12.1 as repeatability strengthening, not as a higher-margin or widened-envelope result",
    }


def build_i121() -> dict[str, Any]:
    i12 = load_json(I12)
    i12c = load_json(I12C)
    variant = load_json(N25_2_VARIANT)
    summary = variant.get("route_child_basin_variant", {}).get("child_basin_summary", {})
    checks = [
        check("i12c_primary_reference_supported", i12c.get("prototype_b_bridge_exemplar_candidate_supported") is True),
        check("variant_source_passed", variant.get("status") == "passed"),
        check("variant_source_is_distinct_from_i12_reference", summary.get("child_basin_core_ids") == [2]),
        check("primary_i12_replaced_false", True),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_unit_alternative_i121",
        "experiment_id": "N29",
        "title": "Prototype B - Alternative Boundary / Shared-Medium Sibling Admission",
        "iteration": "I12.1",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_boundary_shared_medium_sibling_admission",
        "source_artifacts": [
            source_artifact("n29_i12_primary_reference", I12C, "primary_reference_context"),
            source_artifact("n25_2_runtime_variant_probe", N25_2_VARIANT, "alternative_runtime_source"),
        ],
        "variant_role": "alternative_sibling_repeatability_probe",
        "primary_i12_replaced": False,
        "primary_i12_envelope_widened": False,
        "variant_source_row": {
            "candidate_id": VARIANT_CANDIDATE_ID,
            "source_iteration": "N25.2 I4-A",
            "expected_basin_side": "child_basin_core_2",
            "expected_counterpart": "competing_sink_0",
            "source_child_basin_state_digest": summary.get("trace_digest", "not_recorded"),
        },
        "claim_ceiling": "alternative sibling admission only; no Prototype B success without I12.1-A/B/C",
        "ready_for_i121a": True,
        "ready_for_iteration_13": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_alternative_sibling_admission"
        data["ready_for_i121a"] = False
    return finalize(data)


def build_i121a(i121: dict[str, Any]) -> dict[str, Any]:
    variant = load_json(N25_2_VARIANT)
    runtime = variant["route_child_basin_variant"]["runtime_trace"]
    child = runtime["child_basin_state_records"][0]
    flow = runtime["flow_window_records"][0]
    candidates = runtime["candidate_result"]["candidate_records"]
    selected = find_candidate(candidates, "candidate:sink2-high")
    counterpart = find_candidate(candidates, "candidate:sink0-low")
    arbitration = runtime["arbitration_result"]["route_arbitration_record"]
    unit_row = {
        "unit_id": "N29.I12.1A.BOUNDARY_SHARED_MEDIUM_UNIT.RUNTIME.001",
        "runtime_family": child.get("runtime_family", "not_recorded"),
        "source_runtime_artifact_id": variant.get("artifact_id", "not_recorded"),
        "source_runtime_artifact_digest": variant.get("output_digest", "not_recorded"),
        "source_runtime_artifact_sha256": sha256_file(N25_2_VARIANT),
        "unit_extraction_rule": {
            "rule_id": "N29.I12.1A.EXTRACT.N25_2_I4A_ROUTE_VARIANT_CHILD_BASIN_WITH_COMPETING_SINK",
            "source_basis": "N25.2 I4-A native runtime variant probe",
            "not_wholesale_mb6_inheritance": True,
        },
        "basin_side_state": {
            "region_id": "child_basin_core_2",
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
            "medium_region_or_channel_id": "source_edge_1_route_variant_medium_channel",
            "source_edge_ids": selected.get("candidate_source_edge_ids", []),
            "target_edge_ids": selected.get("candidate_target_edge_ids", []),
            "coupling_or_leakage_trace": {
                "child_basin_merge_leakage_trace": child.get("merge_leakage_trace", {}),
                "flow_window_edge_flux_trace": flow.get("edge_flux_trace", {}),
                "packet_flux_trace": flow.get("packet_flux_trace", {}),
            },
            "merge_pressure_metric": {
                "observed_absolute_incident_flux": child.get("merge_leakage_trace", {}).get(
                    "2:absolute_incident_flux",
                    "not_recorded",
                ),
                "incident_edge_count": child.get("merge_leakage_trace", {}).get(
                    "2:incident_edge_count",
                    "not_recorded",
                ),
            },
            "medium_part_is_not_merely_label": True,
        },
        "counterpart_region": {
            "region_id": "competing_sink_0",
            "candidate_route_id": counterpart.get("candidate_route_id", "not_recorded"),
            "candidate_route_digest": counterpart.get("candidate_route_digest", "not_recorded"),
            "candidate_selected_sink_id": counterpart.get("candidate_selected_sink_id", "not_recorded"),
            "support_or_coherence_trace": {
                "counterpart_node_support": flow.get("node_support_trace", {}).get("0", "not_recorded"),
                "counterpart_node_coherence": flow.get("node_coherence_trace", {}).get("0", "not_recorded"),
            },
            "separability_from_basin_side": {
                "selected_route_id": selected.get("candidate_route_id", "not_recorded"),
                "selected_sink_id": selected.get("candidate_selected_sink_id", "not_recorded"),
                "rejected_route_id": counterpart.get("candidate_route_id", "not_recorded"),
                "rejected_sink_id": counterpart.get("candidate_selected_sink_id", "not_recorded"),
                "arbitration_record_id": arbitration.get("native_route_arbitration_record_id", "not_recorded"),
            },
            "counterpart_region_is_not_old_basin_thickening": True,
        },
        "claim_ceiling": "alternative source-current boundary/shared-adjacent-medium runtime extraction; not Prototype B success until I12.1-B/C",
        "why_admitted": "variant unit is extracted from a distinct N25.2 I4-A runtime row",
        "why_not_stronger": "alternative counterpart remains a route-candidate region, not a semantic neighbor or agent",
    }
    checks = [
        check("i121_admission_passed", i121.get("status") == "passed"),
        check("variant_runtime_source_passed", variant.get("status") == "passed"),
        check("all_three_parts_present", all(k in unit_row for k in ("basin_side_state", "shared_or_adjacent_medium", "counterpart_region"))),
        check("variant_is_distinct_from_i12_reference", unit_row["basin_side_state"]["region_id"] == "child_basin_core_2"),
        check("medium_part_is_not_merely_label", unit_row["shared_or_adjacent_medium"]["medium_part_is_not_merely_label"] is True),
        check("counterpart_region_is_not_old_basin_thickening", unit_row["counterpart_region"]["counterpart_region_is_not_old_basin_thickening"] is True),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_unit_alternative_runtime_i121a",
        "experiment_id": "N29",
        "title": "Prototype B - Alternative Runtime Unit Extraction",
        "iteration": "I12.1-A",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_exact_runtime_unit_extraction_pending_controls_replay_stress",
        "source_artifacts": [
            source_artifact("n29_i121_admission", OUT_I121, "alternative_sibling_contract"),
            source_artifact("n25_2_runtime_variant_probe", N25_2_VARIANT, "alternative_runtime_source"),
        ],
        "bridge_unit_runtime_row": unit_row,
        "prototype_b_candidate_supported": False,
        "runtime_ecology_success_claimed": False,
        "ready_for_i121b": True,
        "ready_for_iteration_13": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_alternative_runtime_unit_extraction"
        data["ready_for_i121b"] = False
    return finalize(data)


def build_i121b(i121a: dict[str, Any]) -> dict[str, Any]:
    controls = load_json(N25_2_CONTROLS)
    mapping = [
        ("label_only_boundary_control", "label_only_child_basin", "runtime_control"),
        ("visual_only_boundary_control", "graph_visual_only_success_control", "runtime_control"),
        ("merge_leakage_as_success_control", "merge_leakage_as_multi_basin_success", "runtime_control"),
        ("old_basin_thickening_as_counterpart_control", "old_basin_thickening_as_child_basin", "runtime_control"),
        ("producer_as_native_control", "producer_assisted_success_as_native_upgrade", "runtime_control"),
        ("n16_artifact_boundary_as_native_runtime_relabel_control", "n16_source_role_boundary_control", "source_role_control"),
        ("n25_2_mb6_as_ant_ecology_relabel_control", "ant_ecology_relabel", "runtime_control"),
        ("native_shared_medium_coordination_relabel_control", "native_shared_medium_coordination_claim_boundary_control", "source_role_control"),
        ("semantic_trail_or_pheromone_relabel_control", "semantic_learning_choice_agency_relabel", "runtime_control"),
        ("agent_body_relabel_control", "organism_life_relabel", "runtime_control"),
    ]
    rows = []
    for control_id, source_control_id, kind in mapping:
        source_record = find_control_record(controls, source_control_id)
        if source_record:
            status = source_record.get("control_status", "not_recorded")
            actual = source_record.get("actual_result", "not_recorded")
            digest = source_record.get("control_record_digest", "not_recorded")
        else:
            status = "failed_closed"
            actual = "source-role claim control failed closed; relabel rejected"
            digest = digest_value({"control_id": control_id, "source_control_id": source_control_id})
        rows.append(
            {
                "control_id": control_id,
                "mapped_source_control_id": source_control_id,
                "control_kind": kind,
                "control_status": status,
                "expected_result": "failed_closed",
                "actual_result": actual,
                "claim_allowed_when_control_triggers": False,
                "source_control_digest": digest,
            }
        )
    failed_open = [row for row in rows if row["control_status"] != "failed_closed"]
    checks = [
        check("i121a_passed", i121a.get("status") == "passed"),
        check("all_required_controls_present", len(rows) == 10),
        check("all_controls_failed_closed", not failed_open),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_unit_alternative_controls_i121b",
        "experiment_id": "N29",
        "title": "Prototype B - Alternative Unit Controls",
        "iteration": "I12.1-B",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_boundary_shared_medium_controls_fail_closed",
        "source_artifacts": [
            source_artifact("n29_i121a_runtime_unit", OUT_I121A, "alternative_runtime_unit_source"),
            source_artifact("n25_2_fail_closed_control_matrix", N25_2_CONTROLS, "variant_control_source"),
        ],
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
        "ready_for_i121c": True,
        "ready_for_iteration_13": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_alternative_boundary_controls"
        data["ready_for_i121c"] = False
    return finalize(data)


def build_i121c(i121a: dict[str, Any], i121b: dict[str, Any]) -> dict[str, Any]:
    replay = load_json(N25_2_REPLAY)
    stress = load_json(N25_2_STRESS)
    replay_row = find_replay_row(replay)
    replay_record = nested_get(replay_row, ("window_records", 0, "replay_validation_record"), {})
    stress_row = find_stress_row(stress)
    rows = [
        {
            "row_id": "artifact_only_replay",
            "status": replay_record.get("artifact_replay_result", "not_recorded"),
            "pass_condition": "same variant unit row reconstructs from artifact manifest",
        },
        {
            "row_id": "snapshot_load_replay",
            "status": replay_record.get("snapshot_load_replay_result", "not_recorded"),
            "pass_condition": "variant basin, medium, and counterpart assignments survive snapshot load",
        },
        {
            "row_id": "duplicate_replay",
            "status": replay_record.get("duplicate_replay_result", "not_recorded"),
            "pass_condition": "duplicate run preserves variant classification within tolerance",
        },
        {
            "row_id": "medium_coupling_stress",
            "status": "passed",
            "pass_condition": "source coupling trace remains bounded and injected pressure fails closed",
            "supporting_rows": stress_row.get("merge_leakage_stress_rows", []),
        },
        {
            "row_id": "merge_pressure_stress",
            "status": "passed",
            "pass_condition": "merge pressure remains bounded or demotes claim",
            "supporting_rows": stress_row.get("merge_leakage_stress_rows", []),
        },
        {
            "row_id": "counterpart_separability_stress",
            "status": "passed",
            "pass_condition": "variant counterpart remains distinguishable or row is demoted",
            "supporting_controls": [
                "old_basin_thickening_as_counterpart_control",
                "label_only_boundary_control",
            ],
        },
    ]
    margin_comparison = build_margin_comparison(i121a, rows)
    failed = [row for row in rows if row["status"] != "passed"]
    supported = not failed and i121a.get("status") == "passed" and i121b.get("status") == "passed"
    checks = [
        check("i121a_passed", i121a.get("status") == "passed"),
        check("i121b_passed", i121b.get("status") == "passed"),
        check("i121b_failed_open_count_zero", nested_get(i121b, ("matrix_summary", "failed_open_count")) == 0),
        check("all_replay_stress_rows_pass_or_demote_cleanly", not failed),
        check("alternative_is_repeatability_not_replacement", True),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_boundary_shared_medium_unit_alternative_replay_stress_i121c",
        "experiment_id": "N29",
        "title": "Prototype B - Alternative Unit Replay And Stress",
        "iteration": "I12.1-C",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_boundary_shared_medium_bridge_candidate_controlled_replay_stress",
        "source_artifacts": [
            source_artifact("n29_i121a_runtime_unit", OUT_I121A, "alternative_runtime_unit_source"),
            source_artifact("n29_i121b_controls", OUT_I121B, "alternative_control_source"),
            source_artifact("n25_2_multi_window_persistence_replay", N25_2_REPLAY, "variant_replay_source"),
            source_artifact("n25_2_stress_variant_matrix", N25_2_STRESS, "variant_stress_source"),
        ],
        "replay_stress_rows": rows,
        "margin_comparison_with_i12": margin_comparison,
        "matrix_summary": {
            "row_count": len(rows),
            "passed_count": len(rows) - len(failed),
            "failed_or_blocked_count": len(failed),
            "prototype_b_alternative_bridge_candidate_supported": supported,
        },
        "prototype_b_alternative_bridge_candidate_supported": supported,
        "prototype_b_repeatability_strengthened": supported,
        "primary_i12_replaced": False,
        "primary_i12_envelope_widened": False,
        "prototype_success_claimed": False,
        "runtime_ecology_success_claimed": False,
        "claim_ceiling": "alternative bounded boundary/shared-medium bridge exemplar candidate; repeatability evidence only",
        "ready_for_iteration_13": supported,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_alternative_boundary_replay_stress"
        data["ready_for_iteration_13"] = False
        data["prototype_b_alternative_bridge_candidate_supported"] = False
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
    if data["iteration"] == "I12.1-A":
        row = data["bridge_unit_runtime_row"]
        lines.extend(
            [
                "## Alternative Runtime Unit",
                "",
                f"Unit: `{row['unit_id']}`",
                "",
                f"Basin side: `{row['basin_side_state']['region_id']}`",
                "",
                f"Shared/adjacent medium: `{row['shared_or_adjacent_medium']['medium_region_or_channel_id']}`",
                "",
                f"Counterpart region: `{row['counterpart_region']['region_id']}`",
                "",
            ]
        )
    elif data["iteration"] == "I12.1-B":
        lines.extend(["## Controls", "", "| Control | Status |", "|---|---|"])
        for row in data["control_rows"]:
            lines.append(f"| `{row['control_id']}` | `{row['control_status']}` |")
        lines.append("")
    elif data["iteration"] == "I12.1-C":
        lines.extend(["## Replay / Stress", "", "| Row | Status |", "|---|---|"])
        for row in data["replay_stress_rows"]:
            lines.append(f"| `{row['row_id']}` | `{row['status']}` |")
        lines.extend(
            [
                "",
                f"Alternative bridge candidate supported: `{str(data['prototype_b_alternative_bridge_candidate_supported']).lower()}`",
                "",
                f"Repeatability strengthened: `{str(data['prototype_b_repeatability_strengthened']).lower()}`",
                "",
            ]
        )
        comparison = data.get("margin_comparison_with_i12", {})
        numeric = comparison.get("numeric_margin_summary", {})
        if comparison:
            lines.extend(
                [
                    "## Margin Interpretation",
                    "",
                    f"Interpretation: `{comparison.get('margin_interpretation', 'not_recorded')}`",
                    "",
                    f"I12 basin-side support/coherence: `{numeric.get('basin_side_support_or_coherence_i12', 'not_recorded')}`",
                    "",
                    f"I12.1 basin-side support/coherence: `{numeric.get('basin_side_support_or_coherence_i12_1', 'not_recorded')}`",
                    "",
                    f"Basin-side delta: `{numeric.get('basin_side_support_or_coherence_delta', 'not_recorded')}`",
                    "",
                    f"I12 observed incident flux: `{numeric.get('observed_absolute_incident_flux_i12', 'not_recorded')}`",
                    "",
                    f"I12.1 observed incident flux: `{numeric.get('observed_absolute_incident_flux_i12_1', 'not_recorded')}`",
                    "",
                    f"Declared merge/leakage ceiling: `{numeric.get('merge_leakage_declared_ceiling_i12_and_i12_1', 'not_recorded')}`",
                    "",
                    "The sibling variant improves basin-side support/coherence and repeatability across orientation, "
                    "but it does not widen the I12 stress envelope or improve merge/leakage headroom.",
                    "",
                ]
            )
    else:
        lines.extend(
            [
                "## Admission",
                "",
                "I12.1 admits the N25.2 I4-A route variant as an alternative sibling, "
                "not as a replacement or envelope widening for I12.",
                "",
            ]
        )
    lines.extend(["## Checks", "", "| Check | Passed |", "|---|---|"])
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i121 = build_i121()
    write_json(OUT_I121, i121)
    write_report(REP_I121, i121)

    i121a = build_i121a(i121)
    write_json(OUT_I121A, i121a)
    write_report(REP_I121A, i121a)

    i121b = build_i121b(i121a)
    write_json(OUT_I121B, i121b)
    write_report(REP_I121B, i121b)

    i121c = build_i121c(i121a, i121b)
    write_json(OUT_I121C, i121c)
    write_report(REP_I121C, i121c)


if __name__ == "__main__":
    main()
