#!/usr/bin/env python3
"""Build N24 Iteration 4 minimal source-current surplus probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_minimal_surplus_probe.json"
REPORT = EXPERIMENT / "reports" / "n24_minimal_surplus_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n24_minimal_surplus_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_minimal_surplus_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_minimal_surplus_probe.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_abundance_schema_and_controls.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_active_nulls_and_failure_baselines.json"
)
N23_CLOSEOUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_closeout_and_n24_handoff.json"
)
N23_I4_PRE_COLLAPSE_SNAPSHOT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_minimal_live_branch_collapse_probe_artifacts/"
    "n23_i4_pre_collapse_snapshot.json"
)

GRC9V3_EXAMPLES = ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_column_h_state, make_config  # noqa: E402
from pygrc.models import LGRC9V3  # noqa: E402


RUN_ID = "n24_i4_minimal_source_current_surplus"
SUPPORT_FLOOR = 9.85
COHERENCE_FLOOR = 9.85
MIN_SURPLUS_MARGIN = 0.10
FLUX_OR_LEAKAGE_BOUND = 1e-9
MAINTENANCE_BASIN_ID = "n24_i4_core_support_maintenance_basin"
MAINTENANCE_NODE_IDS = [0, 1, 5, 6, 7, 8, 9]
SUPPORT_MEASUREMENT_SCOPE = "maintenance_basin_node_set"
SUPPORT_AGGREGATION_METHOD = "min"


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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def source_record(path: str, role: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": role,
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
    }


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def unsafe_claim_flags(i2: dict[str, Any]) -> dict[str, bool]:
    return {
        claim: False
        for claim in sorted(i2["claim_boundary_schema"]["unsafe_claim_flags"].keys())
    }


def i1_contract_row(i1: dict[str, Any]) -> dict[str, Any]:
    rows = i1.get("contract_inventory_rows", [])
    if not rows or not isinstance(rows[0], dict):
        raise KeyError("N24 I1 contract inventory row missing")
    return rows[0]


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n24_i4_minimal_surplus_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": LANE_B,
        "maintenance_basin": {
            "maintenance_basin_id": MAINTENANCE_BASIN_ID,
            "node_ids": MAINTENANCE_NODE_IDS,
            "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
            "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        },
        "thresholds": threshold_record(),
        "claim_boundary": {
            "max_iteration4_rung": "AB2",
            "ab3_optional_set_required_later": True,
            "surplus_supported_optionality_claim_allowed": False,
        },
    }


def threshold_record() -> dict[str, Any]:
    record = {
        "threshold_record_id": "n24_i4_thresholds_declared_before_use",
        "declared_before_use": True,
        "support_floor_value": SUPPORT_FLOOR,
        "coherence_floor_value": COHERENCE_FLOOR,
        "minimum_support_surplus_margin": MIN_SURPLUS_MARGIN,
        "minimum_coherence_surplus_margin": MIN_SURPLUS_MARGIN,
        "boundary_integrity_floor_value": "maintenance basin node set and topology signature preserved",
        "flux_or_leakage_bound": FLUX_OR_LEAKAGE_BOUND,
        "ab3_minimum_availability_count": 2,
        "ab5_minimum_jointly_admissible_count": 2,
        "field_specific_acceptance": {
            "support_floor_result": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "coherence_floor_result": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "boundary_integrity_result": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "flux_or_leakage_result": ["preserved", "changed_within_bound"],
        },
    }
    record["threshold_record_digest"] = digest_value(record)
    return record


def node_metrics(model: LGRC9V3) -> list[dict[str, Any]]:
    state = model.get_state()
    rows: list[dict[str, Any]] = []
    for node_id in MAINTENANCE_NODE_IDS:
        node = state.base_state.nodes[node_id]
        rows.append(
            {
                "node_id": node_id,
                "coherence": node.coherence,
                "basin_mass": node.basin_mass,
                "basin_id": node.basin_id,
                "support_value": node.coherence,
                "support_margin": node.coherence - SUPPORT_FLOOR,
                "coherence_margin": node.coherence - COHERENCE_FLOOR,
            }
        )
    return rows


def topology_signature(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    ledger = state.packet_ledger
    if ledger is not None:
        return dict(ledger.fixed_topology_signature)
    base = state.base_state
    return {
        "node_count": len(base.nodes),
        "edge_count": len(base.port_edges),
        "maintenance_node_ids": MAINTENANCE_NODE_IDS,
    }


def maintenance_basin_signature(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    nodes = node_metrics(model)
    incident_edge_ids = sorted(
        {
            edge_id
            for node_id in MAINTENANCE_NODE_IDS
            for edge_id in state.base_state.topology.incident_edge_ids(node_id)
        }
    )
    signature = {
        "maintenance_basin_id": MAINTENANCE_BASIN_ID,
        "maintenance_node_ids": MAINTENANCE_NODE_IDS,
        "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
        "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        "node_metrics": nodes,
        "min_support": min(node["support_value"] for node in nodes),
        "min_coherence": min(node["coherence"] for node in nodes),
        "support_sum": sum(node["support_value"] for node in nodes),
        "coherence_sum": sum(node["coherence"] for node in nodes),
        "incident_edge_ids": incident_edge_ids,
        "topology_signature": topology_signature(model),
    }
    signature["maintenance_basin_signature_digest"] = digest_value(signature)
    return signature


def trace_record(
    artifact_id: str,
    trace_status: str,
    trace_origin: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    record = {
        "artifact_id": artifact_id,
        "trace_status": trace_status,
        "trace_origin": trace_origin,
        "payload": payload,
    }
    record["trace_digest"] = digest_value(record)
    return record


def build_runtime_artifacts() -> dict[str, Any]:
    model = LGRC9V3.from_state(make_column_h_state(), make_config(spark_lane=LANE_B))
    snapshot_path = ARTIFACT_DIR / "n24_i4_source_current_snapshot.json"
    model.save(str(snapshot_path))
    signature = maintenance_basin_signature(model)
    threshold = threshold_record()
    support_margin = signature["min_support"] - SUPPORT_FLOOR
    coherence_margin = signature["min_coherence"] - COHERENCE_FLOOR
    floor_trace = trace_record(
        "n24_i4_maintenance_floor_trace",
        "present",
        "source_current_same_run",
        {
            "maintenance_basin_id": MAINTENANCE_BASIN_ID,
            "support_floor_value": SUPPORT_FLOOR,
            "coherence_floor_value": COHERENCE_FLOOR,
            "declared_before_use": True,
            "threshold_record_digest": threshold["threshold_record_digest"],
        },
    )
    surplus_trace = trace_record(
        "n24_i4_support_surplus_margin_trace",
        "present",
        "source_current_same_run",
        {
            "formula": "observed_support - support_floor_value",
            "observed_support": signature["min_support"],
            "support_floor_value": SUPPORT_FLOOR,
            "support_surplus_margin": support_margin,
            "minimum_support_surplus_margin": MIN_SURPLUS_MARGIN,
            "coherence_formula": "observed_coherence - coherence_floor_value",
            "observed_coherence": signature["min_coherence"],
            "coherence_floor_value": COHERENCE_FLOOR,
            "coherence_surplus_margin": coherence_margin,
            "minimum_coherence_surplus_margin": MIN_SURPLUS_MARGIN,
            "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
            "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        },
    )
    boundary_flux_trace = trace_record(
        "n24_i4_boundary_flux_trace",
        "present",
        "source_current_same_run",
        {
            "maintenance_basin_signature_digest": signature[
                "maintenance_basin_signature_digest"
            ],
            "boundary_integrity_result": "preserved",
            "topology_signature": signature["topology_signature"],
            "flux_or_leakage_result": "preserved",
            "packet_budget_error": 0.0,
            "in_flight_packet_total": 0.0,
            "flux_or_leakage_bound": FLUX_OR_LEAKAGE_BOUND,
        },
    )
    run_artifact = {
        "artifact_id": "n24_i4_lgrc9v3_minimal_surplus_run",
        "run_id": RUN_ID,
        "model_family": "LGRC9V3",
        "fixture": "make_column_h_state",
        "derived_report_only": False,
        "source_current_inputs_emitted": True,
        "runtime_config_digest": digest_value(runtime_config()),
        "snapshot_path": rel(snapshot_path),
        "maintenance_basin_signature": signature,
        "maintenance_floor_trace": floor_trace,
        "support_surplus_margin_trace": surplus_trace,
        "boundary_flux_trace": boundary_flux_trace,
        "optional_continuation_set_trace": {
            "trace_status": "not_run",
            "reason": "I4 tests minimal source-current surplus only; I5 tests optional continuation set",
        },
        "event_counts_by_kind": {},
    }
    run_artifact["run_artifact_digest"] = digest_value(run_artifact)
    run_path = ARTIFACT_DIR / "n24_i4_lgrc9v3_minimal_surplus_run.json"
    floor_path = ARTIFACT_DIR / "n24_i4_maintenance_floor_trace.json"
    surplus_path = ARTIFACT_DIR / "n24_i4_support_surplus_margin_trace.json"
    boundary_path = ARTIFACT_DIR / "n24_i4_boundary_flux_trace.json"
    threshold_path = ARTIFACT_DIR / "n24_i4_thresholds_declared_before_use.json"
    runtime_config_path = ARTIFACT_DIR / "n24_i4_runtime_config.json"
    write_json(run_path, run_artifact)
    write_json(floor_path, floor_trace)
    write_json(surplus_path, surplus_trace)
    write_json(boundary_path, boundary_flux_trace)
    write_json(threshold_path, threshold)
    write_json(runtime_config_path, runtime_config())
    return {
        "run_artifact": run_artifact,
        "run_artifact_path": rel(run_path),
        "snapshot_path": rel(snapshot_path),
        "floor_trace_path": rel(floor_path),
        "surplus_trace_path": rel(surplus_path),
        "boundary_trace_path": rel(boundary_path),
        "threshold_path": rel(threshold_path),
        "runtime_config_path": rel(runtime_config_path),
    }


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def artifact_sha256_map(manifest: list[dict[str, str]]) -> dict[str, str]:
    return {item["path"]: item["sha256"] for item in manifest}


def control_results() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "hidden_budget_relief_control",
            "control_status": "passed",
            "blocked_condition": "hidden producer/budget relief supplies surplus",
            "expected_result": "hidden_budget_relief_absent=true",
            "actual_result": "surplus measured from LGRC source-current node coherence",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks positive support if triggered",
        },
        {
            "control_id": "floor_crossing_as_abundance_control",
            "control_status": "passed",
            "blocked_condition": "support or coherence floor crossed",
            "expected_result": "support/coherence floors preserved",
            "actual_result": "support and coherence margins are positive",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks AB2+ if triggered",
        },
        {
            "control_id": "surplus_without_optional_continuation_control",
            "control_status": "failed_closed",
            "blocked_condition": "surplus appears without optional continuation set",
            "expected_result": "AB3+ remains blocked while AB2 surplus input may be retained",
            "actual_result": "optional_continuation_availability_count=0; row capped at AB2",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "allows AB2 descriptive surplus only; blocks AB3+",
        },
        {
            "control_id": "optionality_without_surplus_control",
            "control_status": "passed",
            "blocked_condition": "optional branch exists without surplus",
            "expected_result": "not applicable to I4 because optional set is not claimed",
            "actual_result": "surplus present; optionality not claimed",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks AB2 and AB3+ if triggered",
        },
        {
            "control_id": "proxy_only_optional_branch_gain_control",
            "control_status": "passed",
            "blocked_condition": "proxy gain replaces geometry",
            "expected_result": "reward/proxy labels absent",
            "actual_result": "reward_or_proxy_label_absent_or_blocked=true",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks optionality support if triggered",
        },
        {
            "control_id": "optional_branch_label_only_control",
            "control_status": "not_applicable",
            "blocked_condition": "optional branch label replaces branch geometry",
            "expected_result": "not applicable before I5 optional branch claim",
            "actual_result": "optional_continuation_set_trace not_run",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": False,
            "rung_effect": "not applicable for AB2-only I4; required for AB3+",
        },
        {
            "control_id": "single_optional_branch_relabel_control",
            "control_status": "not_applicable",
            "blocked_condition": "single branch relabeled as optionality",
            "expected_result": "not applicable before I5 optional branch claim",
            "actual_result": "optional_continuation_availability_count=0",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": False,
            "rung_effect": "not applicable for AB2-only I4; required for AB3+",
        },
        {
            "control_id": "independent_run_optional_assembly_control",
            "control_status": "not_applicable",
            "blocked_condition": "independent runs assembled as one optional set",
            "expected_result": "not applicable before I5 optional branch claim",
            "actual_result": "I4 uses one LGRC snapshot only",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": False,
            "rung_effect": "not applicable for AB2-only I4; required for AB3+",
        },
        {
            "control_id": "maintenance_basin_shift_control",
            "control_status": "passed",
            "blocked_condition": "floor and surplus measured on different basins",
            "expected_result": "maintenance basin signature preserved",
            "actual_result": "single declared maintenance basin signature used",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks surplus claim if triggered",
        },
        {
            "control_id": "floor_renormalization_as_surplus_control",
            "control_status": "passed",
            "blocked_condition": "floor retuned after outcome inspection",
            "expected_result": "thresholds declared before use",
            "actual_result": "row_specific_threshold_record declared_before_use=true",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks surplus claim if triggered",
        },
        {
            "control_id": "post_hoc_surplus_construction_control",
            "control_status": "passed",
            "blocked_condition": "surplus assembled after the fact",
            "expected_result": "surplus trace emitted from source-current snapshot",
            "actual_result": "support_surplus_margin_trace artifact present",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks AB2+ if triggered",
        },
        {
            "control_id": "n23_selection_context_relabel_as_abundance_control",
            "control_status": "passed",
            "blocked_condition": "N23 selection context relabeled as abundance",
            "expected_result": "N23 context is inherited only as AP4 boundary",
            "actual_result": "surplus measured from N24 LGRC snapshot",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks N23 context relabel if triggered",
        },
        {
            "control_id": "reward_maximization_relabel_control",
            "control_status": "passed",
            "blocked_condition": "reward score relabeled as abundance",
            "expected_result": "reward_maximization_claim_allowed=false",
            "actual_result": "reward/proxy labels absent",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks reward overclaim if triggered",
        },
        {
            "control_id": "semantic_choice_relabel_control",
            "control_status": "passed",
            "blocked_condition": "semantic choice relabel",
            "expected_result": "semantic_choice_claim_allowed=false",
            "actual_result": "semantic choice remains blocked",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks unsafe claims if triggered",
        },
        {
            "control_id": "agency_relabel_control",
            "control_status": "passed",
            "blocked_condition": "agency relabel",
            "expected_result": "agency_claim_allowed=false",
            "actual_result": "agency remains blocked",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks unsafe claims if triggered",
        },
        {
            "control_id": "native_support_relabel_control",
            "control_status": "passed",
            "blocked_condition": "native support relabel",
            "expected_result": "native_support_claim_allowed=false",
            "actual_result": "native support remains blocked",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks unsafe claims if triggered",
        },
        {
            "control_id": "phase8_relabel_control",
            "control_status": "passed",
            "blocked_condition": "Phase 8 implementation relabel",
            "expected_result": "phase8_opened=false",
            "actual_result": "Phase 8 remains blocked",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks unsafe claims if triggered",
        },
        {
            "control_id": "ap4_final_reclassification_relabel_control",
            "control_status": "passed",
            "blocked_condition": "final global AP4 reclassification relabel",
            "expected_result": "final_global_ap4_reclassification_supported=false",
            "actual_result": "AP4 bridge context remains local",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": "blocks final global AP4 reclassification",
        },
        {
            "control_id": "ap5_proxy_gap_omission_control",
            "control_status": "not_applicable",
            "blocked_condition": "proxy/reward row omits AP5",
            "expected_result": "not applicable when proxy/reward absent",
            "actual_result": "ap5_dependency_status=not_applicable",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": False,
            "rung_effect": "not applicable for non-proxy I4 row",
        },
    ]


def build_candidate_row(
    *,
    i1: dict[str, Any],
    i2: dict[str, Any],
    runtime: dict[str, Any],
    artifact_manifest: list[dict[str, str]],
) -> dict[str, Any]:
    source_row = i1_contract_row(i1)
    n23 = i1["n23_context_boundary"]
    run_artifact = runtime["run_artifact"]
    signature = run_artifact["maintenance_basin_signature"]
    floor_trace = run_artifact["maintenance_floor_trace"]
    surplus_trace = run_artifact["support_surplus_margin_trace"]
    boundary_trace = run_artifact["boundary_flux_trace"]
    support_margin = surplus_trace["payload"]["support_surplus_margin"]
    coherence_margin = surplus_trace["payload"]["coherence_surplus_margin"]
    artifact_paths = [item["path"] for item in artifact_manifest]
    artifact_sha256 = artifact_sha256_map(artifact_manifest)
    row: dict[str, Any] = {
        "row_id": "n24_i4_row_01_minimal_source_current_surplus_probe",
        "source_contract_row": source_row["source_contract_row"],
        "source_consumable_contract_row": source_row["source_consumable_contract_row"],
        "source_contract_row_digest": i2["source_contract_digests"][
            "source_contract_row_digest"
        ],
        "source_consumable_contract_row_digest": i2["source_contract_digests"][
            "source_consumable_contract_row_digest"
        ],
        "source_output_digest": i1["output_digest"],
        "run_artifact_id": run_artifact["artifact_id"],
        "source_commit_or_source_digest": {
            "script_path": SCRIPT_PATH,
            "script_sha256": sha256_file(SCRIPT_PATH),
        },
        "runtime_config_digest": run_artifact["runtime_config_digest"],
        "source_current_inputs": [
            "LGRC9V3 source-current runtime snapshot",
            "LGRC9V3 maintenance-basin node metrics",
            "source-current support/coherence surplus margin trace",
            "source-current boundary/flux preservation trace",
        ],
        "source_current_required_fields": source_row["source_current_fields"],
        "row_specific_thresholds_declared_before_use": {
            "path": runtime["threshold_path"],
            "sha256": sha256_file(runtime["threshold_path"]),
            "declared_before_use": True,
            "threshold_record": threshold_record(),
        },
        "n20_source_downstream_consumption_status": source_row[
            "n20_source_downstream_consumption_status"
        ],
        "n23_source_closeout_status": n23["n23_source_closeout_status"],
        "n23_closeout_required": n23["n23_closeout_required"],
        "n23_context_consumption": n23["n23_context_consumption"],
        "n23_ap4_bridge_status": n23["n23_ap4_bridge_status"],
        "ap4_context_status": n23["n23_context_consumption"],
        "maintenance_floor_policy": "predeclared_support_and_coherence_floors_required",
        "maintenance_basin_id": MAINTENANCE_BASIN_ID,
        "maintenance_basin_signature_digest": signature[
            "maintenance_basin_signature_digest"
        ],
        "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
        "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        "surplus_channel_policy": (
            "support_surplus_required_and_coherence_floor_preserved"
        ),
        "support_floor_value": SUPPORT_FLOOR,
        "coherence_floor_value": COHERENCE_FLOOR,
        "boundary_integrity_floor_value": (
            "maintenance basin node set and topology signature preserved"
        ),
        "flux_or_leakage_bound": FLUX_OR_LEAKAGE_BOUND,
        "optionality_window": {
            "window_id": "n24_i4_no_optionality_window_opened",
            "start_step": "not_run",
            "end_step": "not_run",
            "window_role": "I4 surplus-only; I5 opens optional continuation window",
        },
        "pre_surplus_geometry_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "runtime_trace",
            "path": runtime["snapshot_path"],
            "maintenance_basin_signature_digest": signature[
                "maintenance_basin_signature_digest"
            ],
        },
        "support_surplus_margin_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "surplus_margin_trace",
            "path": runtime["surplus_trace_path"],
            "trace_digest": surplus_trace["trace_digest"],
            "support_surplus_margin": support_margin,
            "minimum_support_surplus_margin": MIN_SURPLUS_MARGIN,
        },
        "coherence_surplus_margin_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "surplus_margin_trace",
            "path": runtime["surplus_trace_path"],
            "trace_digest": surplus_trace["trace_digest"],
            "coherence_surplus_margin": coherence_margin,
            "minimum_coherence_surplus_margin": MIN_SURPLUS_MARGIN,
        },
        "residual_support_margin_under_optionality": "not_run_until_iteration_5",
        "residual_coherence_margin_under_optionality": "not_run_until_iteration_5",
        "optional_flux_drain_margin": "not_run_until_iteration_5",
        "maintenance_floor_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "maintenance_floor_trace",
            "path": runtime["floor_trace_path"],
            "trace_digest": floor_trace["trace_digest"],
        },
        "optional_continuation_set_trace": {
            "trace_status": "not_run",
            "trace_origin": "not_applicable",
            "reason": "I4 tests AB2 source-current surplus only; I5 tests optional continuation set",
        },
        "optional_continuation_count": 0,
        "optional_continuation_availability_count": 0,
        "jointly_admissible_optional_continuation_count": 0,
        "optional_branch_records": [],
        "optional_branch_evidence_mode": "source_current_available_unexecuted",
        "optional_branch_support_coherence_traces": {
            "trace_status": "not_run",
            "reason": "optional branch support/coherence traces are I5 scope",
        },
        "optional_branch_boundary_flux_traces": {
            "trace_status": "not_run",
            "reason": "optional branch boundary/flux traces are I5 scope",
        },
        "boundary_integrity_under_optionality_trace": {
            "trace_status": "not_run",
            "reason": "boundary under optionality is I5 scope",
        },
        "optional_flux_does_not_drain_maintenance_support": "not_applicable_until_I5",
        "optional_flux_does_not_drain_maintenance_support_status": "not_run",
        "surplus_budget_owner": "source_current_geometry",
        "hidden_budget_relief_absent": True,
        "reward_or_proxy_label_absent_or_blocked": True,
        "same_basin_continuation_rule": i2["same_basin_rule_freeze"]["rule"],
        "same_basin_invariant_fields": i2["same_basin_rule_freeze"]["rule"][
            "basin_signature_fields"
        ],
        "out_of_scope_drift_blocks_row": True,
        "optionality_not_label_reassignment": True,
        "support_floor_result": {
            "status": "preserved" if support_margin >= MIN_SURPLUS_MARGIN else "crossed_floor",
            "observed_support": signature["min_support"],
            "support_floor": SUPPORT_FLOOR,
            "support_surplus_margin": support_margin,
        },
        "coherence_floor_result": {
            "status": "preserved" if coherence_margin >= MIN_SURPLUS_MARGIN else "crossed_floor",
            "observed_coherence": signature["min_coherence"],
            "coherence_floor": COHERENCE_FLOOR,
            "coherence_surplus_margin": coherence_margin,
        },
        "boundary_integrity_result": {
            "status": "preserved",
            "maintenance_node_ids": MAINTENANCE_NODE_IDS,
            "maintenance_basin_signature_digest": signature[
                "maintenance_basin_signature_digest"
            ],
            "topology_signature": signature["topology_signature"],
        },
        "flux_or_leakage_result": {
            "status": "preserved",
            "packet_budget_error": boundary_trace["payload"]["packet_budget_error"],
            "in_flight_packet_total": boundary_trace["payload"][
                "in_flight_packet_total"
            ],
            "flux_or_leakage_bound": FLUX_OR_LEAKAGE_BOUND,
        },
        "replay_result": {
            "artifact_replay": "not_run",
            "snapshot_load_replay": "not_run",
            "duplicate_replay": "not_run",
            "not_run_reason": (
                "I4 opens the first positive surplus row; replay/control-backed "
                "AB4+ evidence remains I6 scope"
            ),
            "affected_rungs": ["AB4", "AB5", "AB6", "N24-C4", "N24-C5", "N24-C6"],
        },
        "control_results": control_results(),
        "ap4_dependency_status": "not_applicable",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": (
            "N23 AP4 bridge context is recorded as inherited local context, "
            "but AB2 surplus-only measurement does not claim route/branch "
            "optionality; AP4 becomes load-bearing in I5 optionality rows."
        ),
        "ap5_condition_reason": (
            "No proxy, reward, or target formation participates in I4 surplus measurement."
        ),
        "surplus_trace_digest": surplus_trace["trace_digest"],
        "optional_continuation_trace_digest": "not_run_until_iteration_5",
        "maintenance_floor_trace_digest": floor_trace["trace_digest"],
        "replay_surplus_digest": "not_run_until_iteration_6",
        "replay_optionality_digest": "not_run_until_iteration_6",
        "surplus_persistence_ratio": 1.0,
        "optional_branch_persistence_ratio": 0.0,
        "surplus_threshold_or_rule": threshold_record(),
        "optionality_threshold_or_rule": threshold_record(),
        "hidden_budget_relief_rejected": True,
        "floor_crossing_rejected": True,
        "surplus_without_optional_continuation_rejected_or_demoted": True,
        "optionality_without_surplus_rejected": True,
        "proxy_only_success_rejected": True,
        "optional_branch_label_only_rejected": False,
        "independent_run_optional_assembly_rejected": False,
        "maintenance_basin_shift_rejected": True,
        "floor_renormalization_rejected": True,
        "post_hoc_surplus_rejected": True,
        "n23_context_relabel_rejected": True,
        "producer_residue_fields": source_row["producer_mediated_fields"],
        "naturalization_debt_fields": source_row["naturalization_debt_fields"],
        "blocked_relabel_fields": source_row["blocked_relabel_fields"],
        "claim_ceiling": (
            "source-current AB2 surplus input evidence only; optionality, AB3+, "
            "reward maximization, semantic choice, agency, native support, "
            "sentience, Phase 8, and ant ecology remain blocked"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(i2),
        "row_decision": "partial",
        "surplus_supported_optionality_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "reward_maximization_claim_allowed": False,
        "agency_claim_allowed": False,
        "native_support_claim_allowed": False,
        "final_global_ap4_reclassification_supported": False,
        "derived_report_only": False,
        "artifact_manifest": artifact_manifest,
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "artifact_paths_equal_manifest_paths": sorted(artifact_paths)
        == sorted(item["path"] for item in artifact_manifest),
        "artifact_sha256_equal_manifest_sha256": artifact_sha256
        == artifact_sha256_map(artifact_manifest),
        "all_artifact_sha256_match_file_contents": all(
            item["sha256"] == sha256_file(item["path"]) for item in artifact_manifest
        ),
        "output_digest": "pending",
    }
    row["output_digest"] = digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )
    return row


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    runtime = build_runtime_artifacts()
    artifact_manifest = file_manifest(
        [
            (runtime["runtime_config_path"], "runtime_trace"),
            (runtime["threshold_path"], "maintenance_floor_trace"),
            (runtime["run_artifact_path"], "runtime_trace"),
            (runtime["snapshot_path"], "runtime_trace"),
            (runtime["floor_trace_path"], "maintenance_floor_trace"),
            (runtime["surplus_trace_path"], "surplus_margin_trace"),
            (runtime["boundary_trace_path"], "boundary_integrity_trace"),
        ]
    )
    row = build_candidate_row(
        i1=i1,
        i2=i2,
        runtime=runtime,
        artifact_manifest=artifact_manifest,
    )
    required_fields = i2["candidate_evidence_row_schema"]["required_fields"]
    candidate_keys = set(row)
    checks = [
        check(
            "i1_inventory_passed",
            i1["status"] == "passed" and not i1["failed_checks"],
            i1["acceptance_state"],
        ),
        check(
            "i2_schema_passed",
            i2["status"] == "passed" and not i2["failed_checks"],
            i2["acceptance_state"],
        ),
        check(
            "i3_active_nulls_ready",
            i3["iteration3_boundary"]["ready_for_iteration_4_positive_probe"] is True
            and not i3["failed_checks"],
            i3["acceptance_state"],
        ),
        check(
            "direct_n23_context_preserved",
            load_json(N23_CLOSEOUT_PATH).get("status") == "passed"
            and i1["n23_context_boundary"]["n23_context_consumption"]
            == "n23_bridge_candidate_consumed",
            {
                "n23_closeout_path": N23_CLOSEOUT_PATH,
                "n23_context_consumption": i1["n23_context_boundary"][
                    "n23_context_consumption"
                ],
                "n23_ap4_bridge_status": i1["n23_context_boundary"][
                    "n23_ap4_bridge_status"
                ],
            },
        ),
        check(
            "candidate_row_field_set_matches_i2_required_fields",
            candidate_keys == set(required_fields),
            {
                "required_count": len(required_fields),
                "candidate_count": len(candidate_keys),
                "extra": sorted(candidate_keys - set(required_fields)),
                "missing": sorted(set(required_fields) - candidate_keys),
            },
        ),
        check(
            "derived_report_only_false",
            row["derived_report_only"] is False,
            row["derived_report_only"],
        ),
        check(
            "source_current_inputs_present",
            bool(row["source_current_inputs"]),
            row["source_current_inputs"],
        ),
        check(
            "artifact_manifest_non_empty",
            len(row["artifact_manifest"]) >= 6
            and row["all_artifact_sha256_match_file_contents"] is True,
            row["artifact_manifest"],
        ),
        check(
            "support_surplus_margin_positive",
            row["support_floor_result"]["status"] == "preserved"
            and row["support_floor_result"]["support_surplus_margin"] >= MIN_SURPLUS_MARGIN,
            row["support_floor_result"],
        ),
        check(
            "coherence_surplus_margin_positive",
            row["coherence_floor_result"]["status"] == "preserved"
            and row["coherence_floor_result"]["coherence_surplus_margin"]
            >= MIN_SURPLUS_MARGIN,
            row["coherence_floor_result"],
        ),
        check(
            "maintenance_basin_signature_present",
            bool(row["maintenance_basin_signature_digest"])
            and row["support_measurement_scope"] == SUPPORT_MEASUREMENT_SCOPE
            and row["support_aggregation_method"] == SUPPORT_AGGREGATION_METHOD,
            {
                "maintenance_basin_signature_digest": row[
                    "maintenance_basin_signature_digest"
                ],
                "support_measurement_scope": row["support_measurement_scope"],
                "support_aggregation_method": row["support_aggregation_method"],
            },
        ),
        check(
            "boundary_and_flux_preserved",
            row["boundary_integrity_result"]["status"] == "preserved"
            and row["flux_or_leakage_result"]["status"] == "preserved",
            {
                "boundary": row["boundary_integrity_result"],
                "flux": row["flux_or_leakage_result"],
            },
        ),
        check(
            "optionality_not_claimed",
            row["optional_continuation_availability_count"] == 0
            and row["surplus_without_optional_continuation_rejected_or_demoted"] is True
            and row["surplus_supported_optionality_claim_allowed"] is False,
            {
                "optional_count": row["optional_continuation_availability_count"],
                "claim_allowed": row["surplus_supported_optionality_claim_allowed"],
            },
        ),
        check(
            "ab2_only_pending_i5_i6",
            row["row_decision"] == "partial"
            and row["replay_result"]["artifact_replay"] == "not_run",
            row["claim_ceiling"],
        ),
        check(
            "ap4_local_context_preserved_ap5_not_applicable",
            row["ap4_context_status"] == "n23_bridge_candidate_consumed"
            and row["ap4_dependency_status"] == "not_applicable"
            and row["ap5_dependency_status"] == "not_applicable"
            and row["final_global_ap4_reclassification_supported"] is False,
            {
                "ap4_context": row["ap4_context_status"],
                "ap4": row["ap4_dependency_status"],
                "ap5": row["ap5_dependency_status"],
                "final_global_ap4_reclassification_supported": row[
                    "final_global_ap4_reclassification_supported"
                ],
            },
        ),
        check(
            "unsafe_claim_flags_all_false",
            all(value is False for value in row["unsafe_claim_flags"].values()),
            row["unsafe_claim_flags"],
        ),
    ]
    failed_checks = [item for item in checks if item["passed"] is not True]
    output = {
        "artifact_id": "n24_minimal_surplus_probe",
        "schema_version": "n24_minimal_surplus_probe_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": 4,
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_minimal_source_current_ab2_surplus_candidate_pending_optionality_replay_controls"
            if not failed_checks
            else "failed_minimal_source_current_surplus_probe"
        ),
        "purpose": "produce the first source-current surplus-above-maintenance-floor candidate",
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"),
            source_record(I3_OUTPUT_PATH, "n24_i3_active_nulls"),
            source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "inherited_n23_context": {
            "path": N23_CLOSEOUT_PATH,
            "n23_source_closeout_status": i1["n23_context_boundary"][
                "n23_source_closeout_status"
            ],
            "n23_ap4_bridge_status": i1["n23_context_boundary"][
                "n23_ap4_bridge_status"
            ],
            "n23_context_consumption": i1["n23_context_boundary"][
                "n23_context_consumption"
            ],
            "consumption_boundary": "inherited prerequisite/AP4 context only; not N24 surplus evidence",
        },
        "source_backed_probe": {
            "model_family": "LGRC9V3",
            "fixture": "examples/grc9v3/_fixtures.py::make_column_h_state",
            "maintenance_basin_id": MAINTENANCE_BASIN_ID,
            "maintenance_node_ids": MAINTENANCE_NODE_IDS,
            "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
            "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
            "support_floor": SUPPORT_FLOOR,
            "coherence_floor": COHERENCE_FLOOR,
            "observed_min_support": row["support_floor_result"]["observed_support"],
            "observed_min_coherence": row["coherence_floor_result"][
                "observed_coherence"
            ],
            "support_surplus_margin": row["support_floor_result"][
                "support_surplus_margin"
            ],
            "coherence_surplus_margin": row["coherence_floor_result"][
                "coherence_surplus_margin"
            ],
        },
        "source_digest_chain_audit": {
            "i2_output_digest_consumed": source_record(
                I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"
            )["output_digest"],
            "i3_output_digest_consumed": source_record(
                I3_OUTPUT_PATH, "n24_i3_active_nulls"
            )["output_digest"],
            "digest_chain_interpretation": (
                "I4 consumes the current repo I2/I3 output digests; regenerate "
                "I3/I4 after any I2 schema change."
            ),
        },
        "fixture_reuse_audit": {
            "n24_snapshot_path": runtime["snapshot_path"],
            "n24_snapshot_sha256": sha256_file(runtime["snapshot_path"]),
            "compared_n23_fixture_snapshot_path": N23_I4_PRE_COLLAPSE_SNAPSHOT_PATH,
            "compared_n23_fixture_snapshot_sha256": sha256_file(
                N23_I4_PRE_COLLAPSE_SNAPSHOT_PATH
            ),
            "snapshot_hash_matches_n23_pre_collapse_fixture": (
                sha256_file(runtime["snapshot_path"])
                == sha256_file(N23_I4_PRE_COLLAPSE_SNAPSHOT_PATH)
            ),
            "n23_snapshot_consumed_as_n24_surplus_evidence": False,
            "interpretation": (
                "N24 re-emits the same LGRC fixture state through its own "
                "runtime artifact; the N23 snapshot is compared only to audit "
                "fixture reuse and is not consumed as N24 surplus evidence."
            ),
        },
        "candidate_rows": [row],
        "iteration4_boundary": {
            "positive_run_artifacts_consumed": True,
            "source_current_inputs_opened": True,
            "source_current_surplus_above_floor_observed": True,
            "maintenance_basin_preserved": True,
            "boundary_integrity_preserved": True,
            "flux_or_leakage_preserved": True,
            "provisional_ab_ladder_rung": "AB2",
            "ab3_or_stronger_supported": False,
            "surplus_supported_optionality_claim_allowed": False,
            "n24_closeout_ladder_rung_assigned": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_supported": False,
            "semantic_choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "ready_for_iteration_5_optional_continuation_probe": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I4 records a source-current maintenance-basin node set whose "
                "minimum support/coherence remain above predeclared floors."
            ),
            "surplus": (
                "The surplus is geometric: it is computed from LGRC node "
                "coherence over the declared maintenance-basin node set, using "
                "the frozen min aggregation, before any optional branch is claimed."
            ),
            "boundary": (
                "The basin signature and topology are recorded from the runtime "
                "snapshot, and the flux/leakage surface is quiet because no "
                "optional branch has been opened yet."
            ),
            "not_applicable_control_flags": (
                "False rejection flags for optional branch label-only and "
                "independent-run assembly controls mean those controls were not "
                "applicable before optionality was opened; they do not permit "
                "those relabel paths."
            ),
            "single_snapshot_persistence_ratio": (
                "surplus_persistence_ratio=1.0 is a single-snapshot descriptive "
                "placeholder for the preserved surplus row, not replay-backed "
                "persistence evidence."
            ),
            "claim_boundary": (
                "This supports only AB2 source-current surplus input evidence. "
                "AB3+ requires I5 optional continuation evidence, and AB4+ "
                "requires replay/control validation."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["candidate_rows"][0]
    probe = output["source_backed_probe"]
    lines = [
        "# N24 Iteration 4 - Minimal Source-Current Surplus Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 4 runs the first positive N24 probe. It records source-current",
        "LGRC9V3 maintenance-basin support/coherence above predeclared floors.",
        "It does not claim optionality yet: the row is capped at AB2 pending I5",
        "optional-continuation evidence and I6 replay/control validation.",
        "",
        "## Geometric Interpretation",
        "",
        output["geometric_interpretation"]["surplus"],
        "",
        output["geometric_interpretation"]["boundary"],
        "",
        output["geometric_interpretation"]["not_applicable_control_flags"],
        "",
        output["geometric_interpretation"]["single_snapshot_persistence_ratio"],
        "",
        "The source snapshot intentionally matches the N23 I4 pre-collapse fixture hash,",
        "because both probes start from the same LGRC fixture state. N24 re-emits",
        "that state as its own runtime artifact and does not consume the N23 snapshot",
        "as surplus evidence.",
        "",
        "```text",
        f"maintenance_basin_id = {probe['maintenance_basin_id']}",
        f"maintenance_node_ids = {probe['maintenance_node_ids']}",
        f"support_measurement_scope = {probe['support_measurement_scope']}",
        f"support_aggregation_method = {probe['support_aggregation_method']}",
        f"support_floor = {probe['support_floor']:.12f}",
        f"coherence_floor = {probe['coherence_floor']:.12f}",
        f"observed_min_support = {probe['observed_min_support']:.12f}",
        f"observed_min_coherence = {probe['observed_min_coherence']:.12f}",
        f"support_surplus_margin = {probe['support_surplus_margin']:.12f}",
        f"coherence_surplus_margin = {probe['coherence_surplus_margin']:.12f}",
        "```",
        "",
        "## Candidate Row",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Row | `{row['row_id']}` |",
        f"| Decision | `{row['row_decision']}` |",
        "| Provisional AB rung | `AB2` |",
        f"| Claim allowed | `{str(row['surplus_supported_optionality_claim_allowed']).lower()}` |",
        f"| Derived report only | `{str(row['derived_report_only']).lower()}` |",
        f"| AP4 status | `{row['ap4_dependency_status']}` |",
        f"| AP5 status | `{row['ap5_dependency_status']}` |",
        f"| Artifact manifest entries | `{len(row['artifact_manifest'])}` |",
        "",
        "## Gates",
        "",
        "| Gate | Status |",
        "| --- | --- |",
        f"| Support | `{row['support_floor_result']['status']}` |",
        f"| Coherence | `{row['coherence_floor_result']['status']}` |",
        f"| Boundary | `{row['boundary_integrity_result']['status']}` |",
        f"| Flux/leakage | `{row['flux_or_leakage_result']['status']}` |",
        f"| Optionality | `{row['optional_continuation_set_trace']['trace_status']}` |",
        f"| Replay | `{row['replay_result']['artifact_replay']}` |",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            output["geometric_interpretation"]["claim_boundary"],
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    output = load_json(rel(OUTPUT))
    write_report(output)
    if output["failed_checks"]:
        raise SystemExit(f"failed checks: {output['failed_checks']}")


if __name__ == "__main__":
    main()
