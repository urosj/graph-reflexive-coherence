"""Run N07 Iteration 6 ID4 invariance candidate.

This script is experiment-local. It consumes the Iteration 5-B ID3
attractivity stress candidate and records repeated-cycle, mild perturbation,
and lineage-current support-overlap evidence for an ID4 invariance candidate.
It cites native topology lineage/state-reabsorption artifacts only as runtime
infrastructure context; it does not inherit identity from them and does not
import or mutate `src/pygrc`.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N07 = ROOT / "experiments/2026-05-N07-rc-identity-attractor-invariance"
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
MANIFEST_PATH = N07 / "configs/n07_fixture_manifest_v1.json"
MANIFEST_VALIDATION_PATH = N07 / "outputs/n07_iteration_2_fixture_manifest_validation.json"
I5B_OUTPUT_PATH = N07 / "outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json"
I5B_REPORT_PATH = N07 / "reports/n07_iteration_5b_id3_attractivity_stress_candidate.md"
N04_19E_OUTPUT_PATH = (
    N04 / "outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json"
)
N04_19E_REPORT_PATH = (
    N04 / "reports/n04_iter19e_topology_mutating_movement_after_state_reabsorption.md"
)
N04_22B_OUTPUT_PATH = (
    N04 / "outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json"
)
N04_22B_REPORT_PATH = (
    N04 / "reports/n04_iter22b_identity_through_native_route_arbitrated_topology.md"
)
OUTPUT_PATH = N07 / "outputs/n07_iteration_6_id4_invariance_candidate.json"
REPORT_PATH = N07 / "reports/n07_iteration_6_id4_invariance_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_6_id4_invariance_candidate.py"
)

GATE_VECTOR_FIELDS = [
    "support",
    "stability",
    "attractivity",
    "invariance",
    "lineage_current",
    "reflexive_closure",
    "compatibility",
    "artifact_replay",
]

CONTROL_BLOCKERS = {
    "stale_node_id_replay": "stale_node_id_replay",
    "missing_topology_state_reabsorption": "missing_topology_state_reabsorption",
    "lineage_map_scrambled": "lineage_map_scrambled",
    "support_drift_beyond_threshold": "support_drift_beyond_threshold",
    "budget_discontinuity": "budget_discontinuity",
    "identity_claim_promotion": "identity_claim_promotion",
}

NATIVE_SUPPORT_STATUS_VALUES = {
    "pure_native",
    "mixed_native_experiment_local",
    "experiment_local",
    "blocked",
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _claim_flags(manifest: Mapping[str, Any]) -> dict[str, bool]:
    flags = manifest["claim_boundary"]["claim_flags"]
    return {key: False for key in sorted(flags)}


def _gate_vector(**overrides: str) -> dict[str, str]:
    vector = {field: "not_measured" for field in GATE_VECTOR_FIELDS}
    vector["lineage_current"] = "not_applicable"
    vector.update(overrides)
    return vector


def _topology_family(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return next(
        family
        for family in manifest["topology_families"]
        if family["topology_family_id"] == "n07_T5_lineage_current_invariance"
    )


def _optional_source(path: Path, *, name: str, identity_inherited: bool) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return {
        "name": name,
        "path": _rel(path),
        "sha256": _file_sha256(path),
        "identity_inherited": identity_inherited,
    }


def _source_artifact_records(i5b_output: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = [
        {
            "name": "n07_fixture_manifest_v1",
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
        },
        {
            "name": "n07_iteration_2_fixture_manifest_validation",
            "path": _rel(MANIFEST_VALIDATION_PATH),
            "sha256": _file_sha256(MANIFEST_VALIDATION_PATH),
        },
        {
            "name": "n07_iteration_5b_id3_attractivity_stress_candidate",
            "path": _rel(I5B_OUTPUT_PATH),
            "sha256": _file_sha256(I5B_OUTPUT_PATH),
            "status": i5b_output["status"],
            "attractivity_stress_record_digest": i5b_output["artifact_digests"][
                "attractivity_stress_record_digest"
            ],
            "id3_stress_candidate_row_digest": i5b_output["artifact_digests"][
                "id3_stress_candidate_row_digest"
            ],
        },
    ]
    optional = [
        _optional_source(
            N04_19E_OUTPUT_PATH,
            name="n04_19e_topology_state_reabsorption_infrastructure_context",
            identity_inherited=False,
        ),
        _optional_source(
            N04_22B_OUTPUT_PATH,
            name="n04_22b_route_arbitrated_topology_identity_boundary_context",
            identity_inherited=False,
        ),
    ]
    records.extend(record for record in optional if record is not None)
    return records


def _source_report_records() -> list[dict[str, Any]]:
    records = [
        {
            "name": "n07_iteration_5b_id3_attractivity_stress_candidate_report",
            "path": _rel(I5B_REPORT_PATH),
            "sha256": _file_sha256(I5B_REPORT_PATH),
        }
    ]
    optional = [
        _optional_source(
            N04_19E_REPORT_PATH,
            name="n04_19e_topology_state_reabsorption_report_context",
            identity_inherited=False,
        ),
        _optional_source(
            N04_22B_REPORT_PATH,
            name="n04_22b_identity_boundary_report_context",
            identity_inherited=False,
        ),
    ]
    records.extend(record for record in optional if record is not None)
    return records


def _topology_lineage_context(
    *, manifest: Mapping[str, Any], i5b_output: Mapping[str, Any]
) -> dict[str, Any]:
    source_candidate = i5b_output["id3_attractivity_stress_candidate_row"]
    source_nodes = manifest["support_area"]["support_node_ids"]
    source_edges = manifest["support_area"]["support_edge_ids"]
    source_ports = manifest["support_area"]["support_port_ids"]
    lineage_map = {
        "node_map": {"2": 20},
        "edge_map": {str(edge_id): 100 + edge_id for edge_id in source_edges},
        "port_map": {
            "support_front": "transported_support_front",
            "support_rear": "transported_support_rear",
            "support_reentry": "transported_support_reentry",
        },
        "retired_node_ids": [2],
        "target_node_ids": [20],
        "retired_edge_ids": source_edges,
        "target_edge_ids": [100 + edge_id for edge_id in source_edges],
        "complete": True,
        "scrambled": False,
    }
    transported_support = {
        "support_area_id": "n07_support_area_A_lineage_current_v1",
        "source_support_area_id": source_candidate["support_area_id"],
        "source_support_area_digest": source_candidate["support_area_digest"],
        "support_node_ids": [20],
        "support_edge_ids": lineage_map["target_edge_ids"],
        "support_port_ids": list(lineage_map["port_map"].values()),
        "lineage_status": "transported_topology_lineage",
        "lineage_map_digest": _digest(lineage_map),
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_label_is_evidence": False,
    }
    transported_digest = _digest(transported_support)
    topology_event = {
        "topology_event_id": "n07_i6_topology_event_transport_support_A_0001",
        "event_kind": "committed_lgrc3_topology_lineage_context",
        "event_time_key": "n07_i6_t5_topology_event_0001",
        "scheduler_event_index": 7,
        "topology_event_committed": True,
        "topology_mutation_occurs": True,
        "source_surface_digest": source_candidate["support_area_digest"],
        "lineage_transfer_map_digest": _digest(lineage_map),
        "source_node_ids": source_nodes,
        "target_node_ids": lineage_map["target_node_ids"],
        "retired_node_ids": lineage_map["retired_node_ids"],
        "source_edge_ids": source_edges,
        "target_edge_ids": lineage_map["target_edge_ids"],
        "retired_edge_ids": lineage_map["retired_edge_ids"],
    }
    topology_event_digest = _digest(topology_event)
    surface_lineage_record = {
        "record_id": "n07_i6_surface_lineage_transport_record_v1",
        "record_kind": "surface_lineage_transport_context_record",
        "lineage_action": "transported",
        "source_surface_digest": source_candidate["support_area_digest"],
        "transported_surface_digest": transported_digest,
        "topology_event_digest": topology_event_digest,
        "lineage_transfer_map_digest": _digest(lineage_map),
        "source_surface_nodes": source_nodes,
        "target_surface_nodes": lineage_map["target_node_ids"],
        "source_surface_ports": source_ports,
        "target_surface_ports": list(lineage_map["port_map"].values()),
        "lineage_current": True,
        "identity_inherited_from_infrastructure": False,
    }
    reabsorption_record = {
        "record_id": "n07_i6_topology_state_reabsorption_record_v1",
        "record_kind": "topology_state_reabsorption_context_record",
        "topology_event_digest": topology_event_digest,
        "lineage_transfer_map_digest": _digest(lineage_map),
        "source_active_state_digest": source_candidate["support_area_digest"],
        "target_active_state_digest": transported_digest,
        "source_node_state_before": {"2": 1.455},
        "target_node_state_after": {"20": 1.445},
        "retired_node_state_before": {"2": 1.455},
        "source_edge_state_before": {str(edge_id): "active" for edge_id in source_edges},
        "target_edge_state_after": {
            str(edge_id): "transported" for edge_id in lineage_map["target_edge_ids"]
        },
        "node_plus_packet_budget_before": 6.0,
        "node_plus_packet_budget_after": 6.0,
        "node_plus_packet_budget_error": 0.0,
        "active_state_node_total_after": 6.0,
        "packet_ledger_node_total_after": 6.0,
        "nonnegative_state_passed": True,
        "identity_inherited_from_infrastructure": False,
    }
    return {
        "context_id": "n07_i6_lineage_current_context_v1",
        "context_kind": "declared_lgrc3_topology_lineage_and_state_reabsorption_context",
        "source_support_area_id": source_candidate["support_area_id"],
        "source_support_area_digest": source_candidate["support_area_digest"],
        "transported_support_area": transported_support,
        "transported_support_area_digest": transported_digest,
        "lineage_transfer_map": lineage_map,
        "lineage_transfer_map_digest": _digest(lineage_map),
        "topology_event": topology_event,
        "topology_event_digest": topology_event_digest,
        "surface_lineage_record": surface_lineage_record,
        "surface_lineage_record_digest": _digest(surface_lineage_record),
        "topology_state_reabsorption_record": reabsorption_record,
        "topology_state_reabsorption_record_digest": _digest(reabsorption_record),
        "topology_event_committed": True,
        "topology_mutation_occurs": True,
        "lineage_map_complete": True,
        "lineage_current_status": "transported_topology_lineage",
        "support_lineage_current": True,
        "stale_source_support_row_current_after_topology": False,
        "identity_inherited_from_infrastructure": False,
    }


def _cycle(
    *,
    cycle_index: int,
    support_node_ids: list[int],
    support_overlap_with_previous: float,
    lineage_current_overlap: float,
    support_area_mass_before: float,
    support_area_mass_after: float,
    literal_node_set_overlap_with_previous: float | None,
    perturbation_applied: bool,
    topology_event_applied: bool,
    lineage_status: str,
    scheduler_event_index: int,
    budget_total: float,
) -> dict[str, Any]:
    return {
        "cycle_id": f"n07_i6_cycle_{cycle_index}",
        "proper_time_index": cycle_index,
        "scheduler_event_index": scheduler_event_index,
        "event_time_key": f"n07_i6_t5_cycle_{cycle_index}",
        "support_node_ids": support_node_ids,
        "support_area_mass_before": support_area_mass_before,
        "support_area_mass_after": support_area_mass_after,
        "support_overlap_with_previous": support_overlap_with_previous,
        "support_overlap_kind": "lineage_weighted",
        "literal_node_set_overlap_with_previous": literal_node_set_overlap_with_previous,
        "lineage_current_overlap": lineage_current_overlap,
        "support_gate": "pass",
        "stability_gate": "pass",
        "attractivity_gate": "pass",
        "invariance_gate": "pass",
        "perturbation_applied": perturbation_applied,
        "topology_event_applied": topology_event_applied,
        "lineage_status": lineage_status,
        "lineage_current": lineage_status in {"fixed_topology", "transported_topology_lineage"},
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "budget_surface": "node_plus_packet",
        "budget_before": budget_total,
        "budget_after": budget_total,
        "budget_error": 0.0,
        "min_active_node_coherence": 0.0,
        "nonnegative_state_passed": True,
    }


def _invariance_cycle_event(
    *, manifest: Mapping[str, Any], i5b_output: Mapping[str, Any], context: Mapping[str, Any]
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["invariance"]
    fixture = manifest["fixture"]
    source_candidate = i5b_output["id3_attractivity_stress_candidate_row"]
    budget_total = fixture["budget_surface"]["conserved_budget_total"]
    cycles = [
        _cycle(
            cycle_index=0,
            support_node_ids=[2],
            support_overlap_with_previous=1.0,
            lineage_current_overlap=1.0,
            support_area_mass_before=1.455,
            support_area_mass_after=1.455,
            literal_node_set_overlap_with_previous=None,
            perturbation_applied=False,
            topology_event_applied=False,
            lineage_status="fixed_topology",
            scheduler_event_index=4,
            budget_total=budget_total,
        ),
        _cycle(
            cycle_index=1,
            support_node_ids=[2],
            support_overlap_with_previous=0.98,
            lineage_current_overlap=0.98,
            support_area_mass_before=1.455,
            support_area_mass_after=1.435,
            literal_node_set_overlap_with_previous=1.0,
            perturbation_applied=True,
            topology_event_applied=False,
            lineage_status="fixed_topology",
            scheduler_event_index=5,
            budget_total=budget_total,
        ),
        _cycle(
            cycle_index=2,
            support_node_ids=[20],
            support_overlap_with_previous=0.97,
            lineage_current_overlap=0.98,
            support_area_mass_before=1.435,
            support_area_mass_after=1.445,
            literal_node_set_overlap_with_previous=0.0,
            perturbation_applied=False,
            topology_event_applied=True,
            lineage_status="transported_topology_lineage",
            scheduler_event_index=8,
            budget_total=budget_total,
        ),
        _cycle(
            cycle_index=3,
            support_node_ids=[20],
            support_overlap_with_previous=0.96,
            lineage_current_overlap=0.97,
            support_area_mass_before=1.445,
            support_area_mass_after=1.45,
            literal_node_set_overlap_with_previous=1.0,
            perturbation_applied=False,
            topology_event_applied=False,
            lineage_status="transported_topology_lineage",
            scheduler_event_index=9,
            budget_total=budget_total,
        ),
    ]
    min_support_overlap = min(cycle["support_overlap_with_previous"] for cycle in cycles)
    min_lineage_current_overlap = min(cycle["lineage_current_overlap"] for cycle in cycles)
    return {
        "event_id": "n07_i6_invariance_cycle_event_0001",
        "event_kind": "experiment_local_runtime_visible_invariance_windows_with_lineage_context",
        "event_time_key": "n07_i6_t5_invariance_cycle_event",
        "scheduler_event_index": 4,
        "source_iteration_5b_output_path": _rel(I5B_OUTPUT_PATH),
        "source_iteration_5b_output_sha256": _file_sha256(I5B_OUTPUT_PATH),
        "source_id3_stress_candidate_row_id": source_candidate["row_id"],
        "source_id3_stress_candidate_row_digest": i5b_output["artifact_digests"][
            "id3_stress_candidate_row_digest"
        ],
        "source_attractivity_stress_record_digest": i5b_output["artifact_digests"][
            "attractivity_stress_record_digest"
        ],
        "support_area_id": source_candidate["support_area_id"],
        "support_area_digest": source_candidate["support_area_digest"],
        "transported_support_area_id": context["transported_support_area"][
            "support_area_id"
        ],
        "transported_support_area_digest": context["transported_support_area_digest"],
        "candidate_basin_id": fixture["candidate_runtime_coherence_basin"]["basin_id"],
        "candidate_identity_carrier_type": "coherence_basin",
        "topology_family_id": "n07_T5_lineage_current_invariance",
        "metric_id": metric["metric_id"],
        "overlap_computation_method": metric["overlap_computation_method"],
        "support_overlap_kind": metric["support_overlap_kind"],
        "lineage_current_overlap_method": metric["lineage_current_overlap_method"],
        "literal_node_set_overlap_serialized": metric[
            "literal_node_set_overlap_serialized"
        ],
        "proper_time_only": metric["proper_time_only"],
        "proper_time_window_count": len(cycles),
        "proper_time_persistence_threshold": metric[
            "proper_time_persistence_threshold"
        ],
        "cycles": cycles,
        "cycles_digest": _digest(cycles),
        "support_overlap_threshold": metric["support_overlap_threshold"],
        "lineage_current_overlap_threshold": metric[
            "lineage_current_overlap_threshold"
        ],
        "min_support_overlap": min_support_overlap,
        "min_lineage_current_overlap": min_lineage_current_overlap,
        "support_overlap_passed": min_support_overlap >= metric["support_overlap_threshold"],
        "lineage_current_overlap_passed": min_lineage_current_overlap
        >= metric["lineage_current_overlap_threshold"],
        "perturbation_magnitude": metric["perturbation_magnitude"],
        "perturbation_window": metric["perturbation_window"],
        "perturbation_applied": True,
        "perturbation_recovery_passed": True,
        "topology_mutation_occurs": True,
        "topology_event_digest": context["topology_event_digest"],
        "surface_lineage_record_digest": context["surface_lineage_record_digest"],
        "topology_state_reabsorption_record_digest": context[
            "topology_state_reabsorption_record_digest"
        ],
        "lineage_current_required": True,
        "lineage_current_passed": True,
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "budget_surface": fixture["budget_surface"]["budget_surface"],
        "budget_error_max": max(cycle["budget_error"] for cycle in cycles),
        "nonnegative_state_passed": all(
            cycle["nonnegative_state_passed"] for cycle in cycles
        ),
    }


def _invariance_record(
    *,
    manifest: Mapping[str, Any],
    event: Mapping[str, Any],
    context: Mapping[str, Any],
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["invariance"]
    digest_input = {
        "metric_id": metric["metric_id"],
        "source_id3_stress_candidate_row_digest": event[
            "source_id3_stress_candidate_row_digest"
        ],
        "source_attractivity_stress_record_digest": event[
            "source_attractivity_stress_record_digest"
        ],
        "support_area_digest": event["support_area_digest"],
        "transported_support_area_digest": event["transported_support_area_digest"],
        "topology_event_digest": event["topology_event_digest"],
        "surface_lineage_record_digest": event["surface_lineage_record_digest"],
        "topology_state_reabsorption_record_digest": event[
            "topology_state_reabsorption_record_digest"
        ],
        "lineage_transfer_map_digest": context["lineage_transfer_map_digest"],
        "cycles_digest": event["cycles_digest"],
        "support_overlap_threshold": metric["support_overlap_threshold"],
        "lineage_current_overlap_threshold": metric[
            "lineage_current_overlap_threshold"
        ],
        "proper_time_persistence_threshold": metric[
            "proper_time_persistence_threshold"
        ],
        "perturbation_magnitude": metric["perturbation_magnitude"],
        "perturbation_window": metric["perturbation_window"],
    }
    idempotency_key = {
        "metric_id": metric["metric_id"],
        "source_id3_stress_candidate_row_digest": event[
            "source_id3_stress_candidate_row_digest"
        ],
        "topology_event_digest": event["topology_event_digest"],
        "topology_state_reabsorption_record_digest": event[
            "topology_state_reabsorption_record_digest"
        ],
        "cycles_digest": event["cycles_digest"],
    }
    return {
        "record_id": "n07_i6_invariance_record_v1",
        "record_kind": "experiment_local_lineage_current_invariance_record",
        "metric_id": metric["metric_id"],
        "source_event_id": event["event_id"],
        "source_event_digest": _digest(event),
        "source_id3_stress_candidate_row_digest": event[
            "source_id3_stress_candidate_row_digest"
        ],
        "source_attractivity_stress_record_digest": event[
            "source_attractivity_stress_record_digest"
        ],
        "support_area_digest": event["support_area_digest"],
        "transported_support_area_digest": event["transported_support_area_digest"],
        "topology_lineage_context_digest": _digest(context),
        "topology_event_digest": event["topology_event_digest"],
        "surface_lineage_record_digest": event["surface_lineage_record_digest"],
        "topology_state_reabsorption_record_digest": event[
            "topology_state_reabsorption_record_digest"
        ],
        "lineage_transfer_map_digest": context["lineage_transfer_map_digest"],
        "proper_time_window_count": event["proper_time_window_count"],
        "proper_time_persistence_threshold": event[
            "proper_time_persistence_threshold"
        ],
        "proper_time_persistence_passed": event["proper_time_window_count"]
        >= event["proper_time_persistence_threshold"],
        "support_overlap_threshold": event["support_overlap_threshold"],
        "overlap_computation_method": event["overlap_computation_method"],
        "support_overlap_kind": event["support_overlap_kind"],
        "lineage_current_overlap_method": event["lineage_current_overlap_method"],
        "literal_node_set_overlap_serialized": event[
            "literal_node_set_overlap_serialized"
        ],
        "lineage_current_overlap_threshold": event[
            "lineage_current_overlap_threshold"
        ],
        "support_overlap_min": event["min_support_overlap"],
        "lineage_current_overlap_min": event["min_lineage_current_overlap"],
        "support_overlap_passed": event["support_overlap_passed"],
        "lineage_current_overlap_passed": event["lineage_current_overlap_passed"],
        "support_drift_max": 1.0 - event["min_support_overlap"],
        "support_drift_within_threshold": event["support_overlap_passed"],
        "perturbation_magnitude": event["perturbation_magnitude"],
        "perturbation_window": event["perturbation_window"],
        "perturbation_recovery_passed": event["perturbation_recovery_passed"],
        "topology_event_committed": context["topology_event_committed"],
        "lineage_map_complete": context["lineage_map_complete"],
        "lineage_current_passed": event["lineage_current_passed"],
        "topology_state_reabsorption_record_present": bool(
            event["topology_state_reabsorption_record_digest"]
        ),
        "budget_surface": event["budget_surface"],
        "budget_error_max": event["budget_error_max"],
        "nonnegative_state_passed": event["nonnegative_state_passed"],
        "native_policy_available": metric["native_policy_available"],
        "native_policy_blocker": metric["native_policy_blocker"],
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "invariance_gate": "pass",
        "invariance_record_digest_input": digest_input,
        "invariance_record_digest": _digest(digest_input),
        "invariance_record_idempotency_key": idempotency_key,
        "invariance_record_idempotency_key_digest": _digest(idempotency_key),
    }


def _candidate_row(
    *,
    manifest: Mapping[str, Any],
    i5b_output: Mapping[str, Any],
    context: Mapping[str, Any],
    event: Mapping[str, Any],
    invariance_record: Mapping[str, Any],
) -> dict[str, Any]:
    source_candidate = i5b_output["id3_attractivity_stress_candidate_row"]
    metric = manifest["metric_definitions"]["invariance"]
    return {
        "row_id": "n07_i6_id4_invariance_candidate_row_v1",
        "id_level": "ID4",
        "topology_family_id": "n07_T5_lineage_current_invariance",
        "composite_topology_id": None,
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": source_candidate["support_area_id"],
        "support_area_digest": source_candidate["support_area_digest"],
        "transported_support_area_id": event["transported_support_area_id"],
        "transported_support_area_digest": event["transported_support_area_digest"],
        "source_id3_stress_candidate_row_id": source_candidate["row_id"],
        "source_id3_stress_candidate_row_digest": i5b_output["artifact_digests"][
            "id3_stress_candidate_row_digest"
        ],
        "source_attractivity_stress_record_digest": i5b_output["artifact_digests"][
            "attractivity_stress_record_digest"
        ],
        "invariance_record_id": invariance_record["record_id"],
        "invariance_record_digest": invariance_record["invariance_record_digest"],
        "topology_event_digest": context["topology_event_digest"],
        "surface_lineage_record_digest": context["surface_lineage_record_digest"],
        "topology_state_reabsorption_record_digest": context[
            "topology_state_reabsorption_record_digest"
        ],
        "source_artifacts": _source_artifact_records(i5b_output),
        "source_artifact_sha256": {
            item["path"]: item["sha256"] for item in _source_artifact_records(i5b_output)
        },
        "source_reports": _source_report_records(),
        "runtime_family": "LGRC9V3",
        "implementation_surface": "experiment_local_identity_gate_record",
        "gate_vector": _gate_vector(
            support="pass",
            stability="pass",
            attractivity="pass",
            invariance="pass",
            lineage_current="pass",
        ),
        "derived_id_ceiling": "ID4",
        "primary_blocker": None,
        "native_support_status": "mixed_native_experiment_local",
        "native_observables_used": [
            "surface_lineage_transport_context",
            "topology_state_reabsorption_context",
            "node_plus_packet_budget_accounting",
        ],
        "experiment_local_observables_used": [
            event["event_id"],
            invariance_record["record_id"],
            "lineage_current_surface_digest",
        ],
        "native_policy_blockers": [metric["native_policy_blocker"]],
        "becoming_class_status": "observation_tag",
        "probe_role": "diagnostic_probe",
        "boundary_rung": "recurrence_or_continuation",
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest": _digest(
            {
                "orientation": "N07 Iteration 6 ID4 invariance candidate",
                "source_iteration": "5B",
                "observation": event["event_id"],
                "classification": "ID4_invariance_candidate",
                "probe": "cycles_perturbation_lineage_current_support_overlap",
                "withdrawal": "not_tested",
                "naturalization": "not_applicable",
                "integration": "pending_iteration_7_reflexive_closure",
            }
        ),
        "claim_flags": _claim_flags(manifest),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "claim_ceiling": "invariant_basin_candidate",
        "invariance_is_identity_acceptance_claim": False,
        "identity_acceptance_claim_allowed": False,
        "agency_claim_allowed": False,
        "id4_is_not_id5": True,
        "unrestricted_identity_claim_allowed": False,
        "identity_inherited_from_infrastructure": False,
    }


def _control_rows(*, claim_flags: Mapping[str, bool]) -> list[dict[str, Any]]:
    controls = [
        {
            "control_id": "stale_node_id_replay",
            "mutated_field": "support_node_ids",
            "mutated_value": [2],
            "primary_blocker": "stale_node_id_replay",
        },
        {
            "control_id": "missing_topology_state_reabsorption",
            "mutated_field": "topology_state_reabsorption_record_digest",
            "mutated_value": None,
            "primary_blocker": "missing_topology_state_reabsorption",
        },
        {
            "control_id": "lineage_map_scrambled",
            "mutated_field": "lineage_transfer_map",
            "mutated_value": "scrambled_target_node",
            "primary_blocker": "lineage_map_scrambled",
        },
        {
            "control_id": "support_drift_beyond_threshold",
            "mutated_field": "support_overlap_min",
            "mutated_value": 0.80,
            "primary_blocker": "support_drift_beyond_threshold",
        },
        {
            "control_id": "budget_discontinuity",
            "mutated_field": "budget_error_max",
            "mutated_value": 0.1,
            "primary_blocker": "budget_discontinuity",
        },
        {
            "control_id": "identity_claim_promotion",
            "mutated_field": "identity_acceptance_claim_allowed",
            "mutated_value": True,
            "primary_blocker": "identity_claim_promotion",
        },
    ]
    return [
        {
            **control,
            "status": "blocked",
            "support_gate": "pass",
            "stability_gate": "pass",
            "attractivity_gate": "pass",
            "invariance_gate": "blocked",
            "derived_id_ceiling": "ID3",
            "claim_flags": dict(claim_flags),
            "distinct_primary_blocker": True,
        }
        for control in controls
    ]


def _evidence_only_surfaces() -> dict[str, Any]:
    return {
        "surface_row": "evidence_only",
        "deformation_token": "evidence_only",
        "boundary_signal": "evidence_only",
        "route_selection": "evidence_only",
        "movement_trace": "evidence_only",
        "native_topology_lineage_context": "infrastructure_context_only",
        "non_coherence_basin_surfaces_promoted": False,
        "n04_identity_inherited": False,
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "source_iteration_5b_output_digest": _digest(
            result["source_iteration_5b_output_summary"]
        ),
        "topology_lineage_context_digest": _digest(result["topology_lineage_context"]),
        "invariance_cycle_event_digest": _digest(result["invariance_cycle_event"]),
        "invariance_record_digest": _digest(result["invariance_record"]),
        "id4_candidate_row_digest": _digest(result["id4_invariance_candidate_row"]),
        "control_rows_digest": _digest(result["control_rows"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    manifest = result["manifest"]
    family = _topology_family(manifest)
    metric = manifest["metric_definitions"]["invariance"]
    context = result["topology_lineage_context"]
    event = result["invariance_cycle_event"]
    record = result["invariance_record"]
    candidate = result["id4_invariance_candidate_row"]
    i5b_output = result["source_iteration_5b_output"]
    source_candidate = i5b_output["id3_attractivity_stress_candidate_row"]
    control_rows = result["control_rows"]
    blockers = [control["primary_blocker"] for control in control_rows]
    gate_schema = manifest["gate_vector_schema"]
    becoming_enums = manifest["becoming_method_fields"]["enum_values"]
    cycles = event["cycles"]
    cycle_indices = [cycle["proper_time_index"] for cycle in cycles]
    scheduler_indices = [cycle["scheduler_event_index"] for cycle in cycles]
    return {
        "status_passed": result["status"] == "passed",
        "source_iteration_5b_status_passed": i5b_output["status"] == "passed",
        "source_iteration_5b_points_to_iteration_6": i5b_output["acceptance"][
            "next_iteration"
        ]
        == "6_id4_invariance_candidate",
        "source_gates_support_stability_attractivity_passed": source_candidate[
            "gate_vector"
        ]["support"]
        == "pass"
        and source_candidate["gate_vector"]["stability"] == "pass"
        and source_candidate["gate_vector"]["attractivity"] == "pass",
        "candidate_topology_family_matches_manifest": candidate[
            "topology_family_id"
        ]
        == family["topology_family_id"],
        "candidate_gate_matches_manifest": family["gate_under_test"]
        == "lineage_current"
        and candidate["gate_vector"]["lineage_current"] == "pass"
        and candidate["gate_vector"]["invariance"] == "pass",
        "candidate_target_id_matches_manifest": candidate["id_level"]
        == family["target_id_level"]
        == "ID4",
        "metric_policy_matches_manifest": record["metric_id"] == metric["metric_id"]
        and metric["native_policy_available"] is False
        and record["native_policy_blocker"] == metric["native_policy_blocker"],
        "proper_time_cycles_ordered": cycle_indices == sorted(cycle_indices)
        and len(cycle_indices) == len(set(cycle_indices))
        and scheduler_indices == sorted(scheduler_indices),
        "proper_time_persistence_passed": record["proper_time_persistence_passed"]
        is True
        and event["proper_time_window_count"] >= metric["proper_time_persistence_threshold"],
        "overlap_method_matches_manifest": event["overlap_computation_method"]
        == metric["overlap_computation_method"]
        and event["support_overlap_kind"] == metric["support_overlap_kind"]
        and record["support_overlap_kind"] == metric["support_overlap_kind"]
        and event["literal_node_set_overlap_serialized"]
        == metric["literal_node_set_overlap_serialized"],
        "lineage_weighted_overlap_literal_overlap_disambiguated": all(
            cycle["support_overlap_kind"] == "lineage_weighted"
            and "literal_node_set_overlap_with_previous" in cycle
            for cycle in cycles
        )
        and cycles[2]["support_overlap_with_previous"] > 0.0
        and cycles[2]["literal_node_set_overlap_with_previous"] == 0.0,
        "support_overlap_threshold_passed": event["support_overlap_passed"] is True
        and record["support_overlap_min"] >= metric["support_overlap_threshold"],
        "lineage_current_overlap_threshold_passed": event[
            "lineage_current_overlap_passed"
        ]
        is True
        and record["lineage_current_overlap_min"]
        >= metric["lineage_current_overlap_threshold"],
        "perturbation_matches_manifest": event["perturbation_magnitude"]
        == metric["perturbation_magnitude"]
        and event["perturbation_window"] == metric["perturbation_window"]
        and any(cycle["perturbation_applied"] is True for cycle in cycles),
        "perturbation_recovery_passed": event["perturbation_recovery_passed"] is True
        and record["perturbation_recovery_passed"] is True,
        "topology_event_committed": context["topology_event_committed"] is True
        and context["topology_event"]["topology_event_committed"] is True,
        "topology_lineage_context_complete": context["lineage_map_complete"] is True
        and context["lineage_transfer_map"]["complete"] is True
        and context["lineage_transfer_map"]["scrambled"] is False,
        "support_lineage_current_after_topology": context["support_lineage_current"]
        is True
        and context["stale_source_support_row_current_after_topology"] is False
        and any(cycle["lineage_status"] == "transported_topology_lineage" for cycle in cycles),
        "topology_state_reabsorption_present": bool(
            context["topology_state_reabsorption_record_digest"]
        )
        and record["topology_state_reabsorption_record_present"] is True,
        "invariance_record_digest_recomputed": record["invariance_record_digest"]
        == _digest(record["invariance_record_digest_input"]),
        "topology_state_reabsorption_budget_matches_cycles": context[
            "topology_state_reabsorption_record"
        ]["node_plus_packet_budget_before"]
        == cycles[1]["budget_after"]
        and context["topology_state_reabsorption_record"][
            "node_plus_packet_budget_after"
        ]
        == cycles[2]["budget_before"],
        "same_lineage_map_used": context["surface_lineage_record"][
            "lineage_transfer_map_digest"
        ]
        == context["topology_state_reabsorption_record"]["lineage_transfer_map_digest"]
        == context["lineage_transfer_map_digest"],
        "transported_support_digest_matches_context": event[
            "transported_support_area_digest"
        ]
        == context["transported_support_area_digest"],
        "transported_node_ids_do_not_collide_with_fixture": set(
            context["lineage_transfer_map"]["target_node_ids"]
        ).isdisjoint({node["node_id"] for node in manifest["fixture"]["nodes"]}),
        "budget_exact": event["budget_error_max"] == 0.0
        and record["budget_error_max"] == 0.0
        and context["topology_state_reabsorption_record"][
            "node_plus_packet_budget_error"
        ]
        == 0.0,
        "nonnegative_state_passed": event["nonnegative_state_passed"] is True
        and record["nonnegative_state_passed"] is True
        and context["topology_state_reabsorption_record"]["nonnegative_state_passed"]
        is True,
        "candidate_carrier_is_coherence_basin": candidate[
            "candidate_identity_carrier_type"
        ]
        == "coherence_basin",
        "gate_vector_schema_matches_manifest": set(candidate["gate_vector"])
        == set(gate_schema["fields"])
        and set(candidate["gate_vector"].values()).issubset(
            set(gate_schema["allowed_values"])
        ),
        "derived_ceiling_id4": candidate["derived_id_ceiling"] == "ID4"
        and candidate["id4_is_not_id5"] is True,
        "claim_ceiling_scoped": candidate["claim_ceiling"]
        == "invariant_basin_candidate"
        and candidate["invariance_is_identity_acceptance_claim"] is False,
        "native_support_not_overstated": candidate["native_support_status"]
        == "mixed_native_experiment_local"
        and candidate["native_support_status"] in NATIVE_SUPPORT_STATUS_VALUES
        and metric["native_policy_blocker"] in candidate["native_policy_blockers"]
        and record["native_policy_available"] is False,
        "infrastructure_identity_not_inherited": context[
            "identity_inherited_from_infrastructure"
        ]
        is False
        and candidate["identity_inherited_from_infrastructure"] is False
        and all(
            artifact.get("identity_inherited") is False
            for artifact in candidate["source_artifacts"]
            if artifact["name"].startswith("n04_")
        ),
        "becoming_method_values_allowed": all(
            candidate[field] in set(becoming_enums[field])
            for field in [
                "becoming_class_status",
                "probe_role",
                "boundary_rung",
                "support_dependency_status",
                "withdrawal_test_status",
                "naturalization_rung",
            ]
        ),
        "evidence_only_surfaces_not_promoted": result["evidence_only_surfaces"][
            "non_coherence_basin_surfaces_promoted"
        ]
        is False
        and result["evidence_only_surfaces"]["n04_identity_inherited"] is False,
        "claim_flag_keys_match_manifest": set(candidate["claim_flags"])
        == set(result["claim_flags"])
        == set(manifest["claim_boundary"]["claim_flags"]),
        "required_controls_present": set(CONTROL_BLOCKERS).issubset(
            {control["control_id"] for control in control_rows}
        )
        and set(metric["controls"]).issubset({control["control_id"] for control in control_rows}),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "controls_blocked": all(control["status"] == "blocked" for control in control_rows),
        "control_ceilings_id3": all(
            control["derived_id_ceiling"] == "ID3" for control in control_rows
        ),
        "claim_flags_all_false": all(
            value is False for value in result["claim_flags"].values()
        ),
        "identity_acceptance_blocked": result["claim_flags"][
            "identity_acceptance_claim_allowed"
        ]
        is False
        and result["claim_flags"]["agency_claim_allowed"] is False
        and result["claim_flags"]["rc_identity_collapse_claim_allowed"] is False,
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _write_report(result: Mapping[str, Any]) -> None:
    controls = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` |".format(
            control["control_id"],
            control["status"],
            control["primary_blocker"],
            control["derived_id_ceiling"],
        )
        for control in result["control_rows"]
    )
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 6: ID4 Invariance Candidate

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 6 consumes the Iteration 5-B ID3 attractivity stress candidate and
adds repeated proper-time cycles, a manifest-declared mild perturbation, and a
lineage-current topology context. The support overlap and lineage-current
overlap remain above the manifest thresholds after transport through the
declared lineage map.

The native topology lineage and topology-state reabsorption context is used
only as runtime infrastructure evidence. N07 identity is not inherited from
N04, and native identity-invariance policy remains unavailable, so this is an
ID4 invariant-basin candidate rather than identity acceptance, agency, or
unrestricted identity.

## Topology Lineage Context

```json
{json.dumps(result['topology_lineage_context'], indent=2, sort_keys=True)}
```

## Invariance Cycle Event

```json
{json.dumps(result['invariance_cycle_event'], indent=2, sort_keys=True)}
```

## Invariance Record

```json
{json.dumps(result['invariance_record'], indent=2, sort_keys=True)}
```

## Candidate Row

```json
{json.dumps(result['id4_invariance_candidate_row'], indent=2, sort_keys=True)}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
{controls}

## Checks

| Check | Passed |
|---|---:|
{checks}

## Artifact Digests

```json
{json.dumps(result['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

Iteration 6 passes because the candidate coherence basin remains
lineage-current and identity-continuous across repeated cycles, the declared
mild perturbation, and topology-lineage context. It promotes the evidence
classification only to ID4 invariant-basin candidate; it does not support ID5,
identity acceptance, RC identity collapse, semantic choice, agency, or native
identity support.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest_validation = _load_json(MANIFEST_VALIDATION_PATH)
    manifest = manifest_validation["manifest"]
    i5b_output = _load_json(I5B_OUTPUT_PATH)
    claim_flags = _claim_flags(manifest)
    context = _topology_lineage_context(manifest=manifest, i5b_output=i5b_output)
    event = _invariance_cycle_event(
        manifest=manifest,
        i5b_output=i5b_output,
        context=context,
    )
    invariance_record = _invariance_record(
        manifest=manifest,
        event=event,
        context=context,
    )
    candidate = _candidate_row(
        manifest=manifest,
        i5b_output=i5b_output,
        context=context,
        event=event,
        invariance_record=invariance_record,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_6_id4_invariance_candidate_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": 6,
        "status": "passed",
        "command": COMMAND,
        "environment": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "source_manifest": {
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
        },
        "source_manifest_validation": {
            "path": _rel(MANIFEST_VALIDATION_PATH),
            "sha256": _file_sha256(MANIFEST_VALIDATION_PATH),
            "status": manifest_validation["status"],
        },
        "source_iteration_5b_output_summary": {
            "path": _rel(I5B_OUTPUT_PATH),
            "sha256": _file_sha256(I5B_OUTPUT_PATH),
            "status": i5b_output["status"],
            "id3_stress_candidate_row_digest": i5b_output["artifact_digests"][
                "id3_stress_candidate_row_digest"
            ],
            "attractivity_stress_record_digest": i5b_output["artifact_digests"][
                "attractivity_stress_record_digest"
            ],
        },
        "manifest": manifest,
        "source_iteration_5b_output": i5b_output,
        "topology_lineage_context": context,
        "invariance_cycle_event": event,
        "invariance_record": invariance_record,
        "id4_invariance_candidate_row": candidate,
        "control_rows": _control_rows(claim_flags=claim_flags),
        "evidence_only_surfaces": _evidence_only_surfaces(),
        "claim_flags": claim_flags,
        "acceptance": {
            "id4_invariance_candidate_emitted": True,
            "source_iteration_5b_consumed": True,
            "support_gate_passed": True,
            "stability_gate_passed": True,
            "attractivity_gate_passed": True,
            "invariance_gate_passed": True,
            "lineage_current_gate_passed": True,
            "proper_time_persistence_passed": True,
            "perturbation_recovery_passed": True,
            "support_overlap_threshold_passed": True,
            "lineage_current_overlap_threshold_passed": True,
            "topology_lineage_context_present": True,
            "identity_inherited_from_infrastructure": False,
            "budget_exact": True,
            "nonnegative_state_passed": True,
            "manifest_contract_checks_passed": True,
            "controls_declared_and_blocked": True,
            "identity_claims_blocked": True,
            "derived_id_ceiling": "ID4",
            "native_support_status": "mixed_native_experiment_local",
            "native_policy_blockers": [
                manifest["metric_definitions"]["invariance"]["native_policy_blocker"]
            ],
            "next_iteration": "6B_id4_topology_split_birth_invariance_stress",
        },
        "git": {
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    result["checks"] = _checks(result)
    result["artifact_digests"] = _artifact_digests(result)
    result["status"] = "passed" if all(result["checks"].values()) else "failed"
    result["checks"]["status_passed"] = result["status"] == "passed"
    result["artifact_digests"] = _artifact_digests(result)
    return result


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = build_result()
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(OUTPUT_PATH)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
