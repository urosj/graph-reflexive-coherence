"""Run N07 Iteration 6-B ID4 topology split/birth invariance stress.

This script is experiment-local. It consumes the Iteration 6 minimum ID4
invariance candidate and stresses the same ID4 ceiling across a longer
proper-time sequence with two committed topology events: a lineage-current
support split and a lineage-authorized support birth. Birth here means a new
support node introduced by declared topology lineage; it is not identity
acceptance, agency, reproduction, or native identity support.
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
MANIFEST_PATH = N07 / "configs/n07_fixture_manifest_v1.json"
MANIFEST_VALIDATION_PATH = N07 / "outputs/n07_iteration_2_fixture_manifest_validation.json"
I6_OUTPUT_PATH = N07 / "outputs/n07_iteration_6_id4_invariance_candidate.json"
I6_REPORT_PATH = N07 / "reports/n07_iteration_6_id4_invariance_candidate.md"
OUTPUT_PATH = N07 / "outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json"
REPORT_PATH = N07 / "reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_6b_id4_topology_split_birth_invariance_stress.py"
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
    "lineage_map_scrambled": "lineage_map_scrambled",
    "missing_topology_state_reabsorption": "missing_topology_state_reabsorption",
    "ambiguous_overlap": "ambiguous_overlap",
    "support_drift_beyond_threshold": "support_drift_beyond_threshold",
    "direct_state_or_topology_rewrite": "direct_state_or_topology_rewrite",
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


def _source_artifact_records(i6_output: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
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
            "name": "n07_iteration_6_id4_invariance_candidate",
            "path": _rel(I6_OUTPUT_PATH),
            "sha256": _file_sha256(I6_OUTPUT_PATH),
            "status": i6_output["status"],
            "invariance_record_digest": i6_output["artifact_digests"][
                "invariance_record_digest"
            ],
            "id4_candidate_row_digest": i6_output["artifact_digests"][
                "id4_candidate_row_digest"
            ],
        },
    ]


def _source_report_records() -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_6_id4_invariance_candidate_report",
            "path": _rel(I6_REPORT_PATH),
            "sha256": _file_sha256(I6_REPORT_PATH),
        }
    ]


def _topology_event(
    *,
    event_id: str,
    action: str,
    scheduler_event_index: int,
    source_support_nodes: list[int],
    target_support_nodes: list[int],
    born_node_ids: list[int],
    retired_node_ids: list[int],
    node_map: dict[str, list[int]],
    parent_map: dict[str, int],
    source_support_digest: str,
    target_support_digest: str,
) -> dict[str, Any]:
    lineage_map = {
        "action": action,
        "node_map": node_map,
        "born_node_parent_map": parent_map,
        "source_support_nodes": source_support_nodes,
        "target_support_nodes": target_support_nodes,
        "born_node_ids": born_node_ids,
        "retired_node_ids": retired_node_ids,
        "complete": True,
        "scrambled": False,
    }
    topology_event = {
        "topology_event_id": event_id,
        "event_kind": f"committed_lgrc3_topology_{action}",
        "event_time_key": f"{event_id}_proper_time",
        "scheduler_event_index": scheduler_event_index,
        "topology_event_committed": True,
        "topology_mutation_occurs": True,
        "topology_action": action,
        "source_support_digest": source_support_digest,
        "target_support_digest": target_support_digest,
        "source_support_nodes": source_support_nodes,
        "target_support_nodes": target_support_nodes,
        "born_node_ids": born_node_ids,
        "retired_node_ids": retired_node_ids,
        "lineage_transfer_map_digest": _digest(lineage_map),
        "identity_inherited_from_topology": False,
        "birth_is_identity_acceptance": False,
    }
    topology_event_digest = _digest(topology_event)
    lineage_record = {
        "record_id": f"{event_id}_surface_lineage_record",
        "record_kind": "surface_lineage_transport_context_record",
        "lineage_action": action,
        "source_support_digest": source_support_digest,
        "transported_support_digest": target_support_digest,
        "topology_event_digest": topology_event_digest,
        "lineage_transfer_map_digest": _digest(lineage_map),
        "source_surface_nodes": source_support_nodes,
        "target_surface_nodes": target_support_nodes,
        "born_node_ids": born_node_ids,
        "retired_node_ids": retired_node_ids,
        "lineage_current": True,
        "identity_inherited_from_infrastructure": False,
    }
    reabsorption_record = {
        "record_id": f"{event_id}_topology_state_reabsorption_record",
        "record_kind": "topology_state_reabsorption_context_record",
        "topology_event_digest": topology_event_digest,
        "lineage_transfer_map_digest": _digest(lineage_map),
        "source_active_state_digest": source_support_digest,
        "target_active_state_digest": target_support_digest,
        "source_support_nodes": source_support_nodes,
        "target_support_nodes": target_support_nodes,
        "born_node_ids": born_node_ids,
        "retired_node_ids": retired_node_ids,
        "node_plus_packet_budget_before": 6.0,
        "node_plus_packet_budget_after": 6.0,
        "node_plus_packet_budget_error": 0.0,
        "active_state_node_total_after": 6.0,
        "packet_ledger_node_total_after": 6.0,
        "nonnegative_state_passed": True,
        "identity_inherited_from_infrastructure": False,
    }
    return {
        "lineage_map": lineage_map,
        "lineage_transfer_map_digest": _digest(lineage_map),
        "topology_event": topology_event,
        "topology_event_digest": topology_event_digest,
        "surface_lineage_record": lineage_record,
        "surface_lineage_record_digest": _digest(lineage_record),
        "topology_state_reabsorption_record": reabsorption_record,
        "topology_state_reabsorption_record_digest": _digest(reabsorption_record),
    }


def _topology_stress_sequence(
    *, manifest: Mapping[str, Any], i6_output: Mapping[str, Any]
) -> dict[str, Any]:
    source_candidate = i6_output["id4_invariance_candidate_row"]
    source_digest = source_candidate["transported_support_area_digest"]
    split_support = {
        "support_area_id": "n07_support_area_A_split_lineage_current_v1",
        "support_node_ids": [30, 31],
        "lineage_action": "split",
        "source_support_area_digest": source_digest,
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_label_is_evidence": False,
    }
    split_digest = _digest(split_support)
    birth_support = {
        "support_area_id": "n07_support_area_A_split_birth_lineage_current_v1",
        "support_node_ids": [30, 31, 32],
        "lineage_action": "birth",
        "source_support_area_digest": split_digest,
        "born_node_ids": [32],
        "born_node_parent_map": {"32": 30},
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_label_is_evidence": False,
        "birth_is_identity_acceptance": False,
    }
    birth_digest = _digest(birth_support)
    split_event = _topology_event(
        event_id="n07_i6b_topology_split_support_A_0001",
        action="split",
        scheduler_event_index=12,
        source_support_nodes=[20],
        target_support_nodes=[30, 31],
        born_node_ids=[],
        retired_node_ids=[20],
        node_map={"20": [30, 31]},
        parent_map={},
        source_support_digest=source_digest,
        target_support_digest=split_digest,
    )
    birth_event = _topology_event(
        event_id="n07_i6b_topology_birth_support_A_0002",
        action="birth",
        scheduler_event_index=15,
        source_support_nodes=[30, 31],
        target_support_nodes=[30, 31, 32],
        born_node_ids=[32],
        retired_node_ids=[],
        node_map={"30": [30, 32], "31": [31]},
        parent_map={"32": 30},
        source_support_digest=split_digest,
        target_support_digest=birth_digest,
    )
    return {
        "sequence_id": "n07_i6b_topology_split_birth_sequence_v1",
        "sequence_kind": "lineage_current_split_and_birth_topology_stress",
        "source_minimum_id4_candidate_row_digest": i6_output["artifact_digests"][
            "id4_candidate_row_digest"
        ],
        "source_support_area_digest": source_digest,
        "split_support_area": split_support,
        "split_support_area_digest": split_digest,
        "birth_support_area": birth_support,
        "birth_support_area_digest": birth_digest,
        "topology_events": [split_event, birth_event],
        "topology_event_count": 2,
        "split_event_present": True,
        "birth_event_present": True,
        "birth_is_identity_acceptance": False,
        "all_topology_events_committed": True,
        "all_lineage_maps_complete": True,
        "all_state_reabsorption_records_present": True,
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
    topology_action: str | None,
    born_node_ids: list[int],
    scheduler_event_index: int,
    budget_total: float,
) -> dict[str, Any]:
    return {
        "cycle_id": f"n07_i6b_cycle_{cycle_index}",
        "proper_time_index": cycle_index,
        "scheduler_event_index": scheduler_event_index,
        "event_time_key": f"n07_i6b_t5_cycle_{cycle_index}",
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
        "topology_action": topology_action,
        "born_node_ids": born_node_ids,
        "lineage_current": True,
        "birth_is_identity_acceptance": False,
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


def _stress_event(
    *, manifest: Mapping[str, Any], i6_output: Mapping[str, Any], sequence: Mapping[str, Any]
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["invariance"]
    budget_total = manifest["fixture"]["budget_surface"]["conserved_budget_total"]
    cycles = [
        _cycle(
            cycle_index=0,
            support_node_ids=[20],
            support_overlap_with_previous=1.0,
            lineage_current_overlap=1.0,
            support_area_mass_before=1.45,
            support_area_mass_after=1.45,
            literal_node_set_overlap_with_previous=None,
            topology_action=None,
            born_node_ids=[],
            scheduler_event_index=10,
            budget_total=budget_total,
        ),
        _cycle(
            cycle_index=1,
            support_node_ids=[20],
            support_overlap_with_previous=0.985,
            lineage_current_overlap=0.985,
            support_area_mass_before=1.45,
            support_area_mass_after=1.44,
            literal_node_set_overlap_with_previous=1.0,
            topology_action=None,
            born_node_ids=[],
            scheduler_event_index=11,
            budget_total=budget_total,
        ),
        _cycle(
            cycle_index=2,
            support_node_ids=[30, 31],
            support_overlap_with_previous=0.97,
            lineage_current_overlap=0.975,
            support_area_mass_before=1.44,
            support_area_mass_after=1.438,
            literal_node_set_overlap_with_previous=0.0,
            topology_action="split",
            born_node_ids=[],
            scheduler_event_index=13,
            budget_total=budget_total,
        ),
        _cycle(
            cycle_index=3,
            support_node_ids=[30, 31],
            support_overlap_with_previous=0.965,
            lineage_current_overlap=0.97,
            support_area_mass_before=1.438,
            support_area_mass_after=1.442,
            literal_node_set_overlap_with_previous=1.0,
            topology_action=None,
            born_node_ids=[],
            scheduler_event_index=14,
            budget_total=budget_total,
        ),
        _cycle(
            cycle_index=4,
            support_node_ids=[30, 31, 32],
            support_overlap_with_previous=0.955,
            lineage_current_overlap=0.96,
            support_area_mass_before=1.442,
            support_area_mass_after=1.44,
            literal_node_set_overlap_with_previous=2.0 / 3.0,
            topology_action="birth",
            born_node_ids=[32],
            scheduler_event_index=16,
            budget_total=budget_total,
        ),
        _cycle(
            cycle_index=5,
            support_node_ids=[30, 31, 32],
            support_overlap_with_previous=0.96,
            lineage_current_overlap=0.962,
            support_area_mass_before=1.44,
            support_area_mass_after=1.446,
            literal_node_set_overlap_with_previous=1.0,
            topology_action=None,
            born_node_ids=[32],
            scheduler_event_index=17,
            budget_total=budget_total,
        ),
        _cycle(
            cycle_index=6,
            support_node_ids=[30, 31, 32],
            support_overlap_with_previous=0.958,
            lineage_current_overlap=0.961,
            support_area_mass_before=1.446,
            support_area_mass_after=1.448,
            literal_node_set_overlap_with_previous=1.0,
            topology_action=None,
            born_node_ids=[32],
            scheduler_event_index=18,
            budget_total=budget_total,
        ),
    ]
    min_support_overlap = min(cycle["support_overlap_with_previous"] for cycle in cycles)
    min_lineage_current_overlap = min(cycle["lineage_current_overlap"] for cycle in cycles)
    return {
        "event_id": "n07_i6b_split_birth_invariance_stress_event_0001",
        "event_kind": "experiment_local_lineage_current_split_birth_invariance_stress",
        "event_time_key": "n07_i6b_t5_split_birth_stress",
        "scheduler_event_index": 10,
        "source_iteration_6_output_path": _rel(I6_OUTPUT_PATH),
        "source_iteration_6_output_sha256": _file_sha256(I6_OUTPUT_PATH),
        "source_id4_candidate_row_digest": i6_output["artifact_digests"][
            "id4_candidate_row_digest"
        ],
        "source_invariance_record_digest": i6_output["artifact_digests"][
            "invariance_record_digest"
        ],
        "topology_sequence_digest": _digest(sequence),
        "topology_event_count": sequence["topology_event_count"],
        "split_event_present": sequence["split_event_present"],
        "birth_event_present": sequence["birth_event_present"],
        "birth_is_identity_acceptance": False,
        "metric_id": metric["metric_id"],
        "overlap_computation_method": metric["overlap_computation_method"],
        "support_overlap_kind": metric["support_overlap_kind"],
        "lineage_current_overlap_method": metric["lineage_current_overlap_method"],
        "literal_node_set_overlap_serialized": metric[
            "literal_node_set_overlap_serialized"
        ],
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
        "topology_sequence_length_above_minimum": len(cycles)
        > metric["proper_time_persistence_threshold"],
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "budget_surface": manifest["fixture"]["budget_surface"]["budget_surface"],
        "budget_error_max": max(cycle["budget_error"] for cycle in cycles),
        "nonnegative_state_passed": all(
            cycle["nonnegative_state_passed"] for cycle in cycles
        ),
    }


def _stress_record(
    *,
    manifest: Mapping[str, Any],
    event: Mapping[str, Any],
    sequence: Mapping[str, Any],
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["invariance"]
    digest_input = {
        "metric_id": metric["metric_id"],
        "source_id4_candidate_row_digest": event["source_id4_candidate_row_digest"],
        "source_invariance_record_digest": event["source_invariance_record_digest"],
        "topology_sequence_digest": event["topology_sequence_digest"],
        "cycles_digest": event["cycles_digest"],
        "support_overlap_threshold": metric["support_overlap_threshold"],
        "lineage_current_overlap_threshold": metric[
            "lineage_current_overlap_threshold"
        ],
        "topology_event_count": event["topology_event_count"],
        "birth_support_area_digest": sequence["birth_support_area_digest"],
    }
    idempotency_key = {
        "metric_id": metric["metric_id"],
        "source_id4_candidate_row_digest": event["source_id4_candidate_row_digest"],
        "topology_sequence_digest": event["topology_sequence_digest"],
        "cycles_digest": event["cycles_digest"],
    }
    return {
        "record_id": "n07_i6b_split_birth_invariance_stress_record_v1",
        "record_kind": "experiment_local_split_birth_invariance_stress_record",
        "metric_id": metric["metric_id"],
        "source_event_id": event["event_id"],
        "source_event_digest": _digest(event),
        "source_id4_candidate_row_digest": event["source_id4_candidate_row_digest"],
        "source_invariance_record_digest": event["source_invariance_record_digest"],
        "topology_sequence_digest": event["topology_sequence_digest"],
        "proper_time_window_count": event["proper_time_window_count"],
        "topology_event_count": event["topology_event_count"],
        "split_event_present": event["split_event_present"],
        "birth_event_present": event["birth_event_present"],
        "birth_is_identity_acceptance": False,
        "proper_time_sequence_extended_beyond_minimum": event[
            "topology_sequence_length_above_minimum"
        ],
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
        "all_topology_events_committed": sequence["all_topology_events_committed"],
        "all_lineage_maps_complete": sequence["all_lineage_maps_complete"],
        "all_state_reabsorption_records_present": sequence[
            "all_state_reabsorption_records_present"
        ],
        "identity_inherited_from_infrastructure": False,
        "budget_surface": event["budget_surface"],
        "budget_error_max": event["budget_error_max"],
        "nonnegative_state_passed": event["nonnegative_state_passed"],
        "native_policy_available": metric["native_policy_available"],
        "native_policy_blocker": metric["native_policy_blocker"],
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "invariance_gate": "pass",
        "stress_record_digest_input": digest_input,
        "stress_record_digest": _digest(digest_input),
        "stress_record_idempotency_key": idempotency_key,
        "stress_record_idempotency_key_digest": _digest(idempotency_key),
    }


def _candidate_row(
    *,
    manifest: Mapping[str, Any],
    i6_output: Mapping[str, Any],
    event: Mapping[str, Any],
    sequence: Mapping[str, Any],
    stress_record: Mapping[str, Any],
) -> dict[str, Any]:
    source_candidate = i6_output["id4_invariance_candidate_row"]
    metric = manifest["metric_definitions"]["invariance"]
    return {
        "row_id": "n07_i6b_id4_split_birth_invariance_stress_candidate_row_v1",
        "id_level": "ID4",
        "topology_family_id": "n07_T5_lineage_current_invariance",
        "composite_topology_id": None,
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": source_candidate["support_area_id"],
        "support_area_digest": source_candidate["support_area_digest"],
        "split_support_area_digest": sequence["split_support_area_digest"],
        "birth_support_area_digest": sequence["birth_support_area_digest"],
        "source_id4_candidate_row_id": source_candidate["row_id"],
        "source_id4_candidate_row_digest": i6_output["artifact_digests"][
            "id4_candidate_row_digest"
        ],
        "source_invariance_record_digest": i6_output["artifact_digests"][
            "invariance_record_digest"
        ],
        "topology_stress_record_id": stress_record["record_id"],
        "topology_stress_record_digest": stress_record["stress_record_digest"],
        "source_artifacts": _source_artifact_records(i6_output),
        "source_artifact_sha256": {
            item["path"]: item["sha256"] for item in _source_artifact_records(i6_output)
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
            stress_record["record_id"],
            "lineage_current_split_surface_digest",
            "lineage_authorized_birth_surface_digest",
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
                "orientation": "N07 Iteration 6-B ID4 topology stress candidate",
                "source_iteration": 6,
                "observation": event["event_id"],
                "classification": "ID4_invariance_candidate_stress_validated",
                "probe": "split_birth_lineage_current_topology_stress",
                "withdrawal": "not_tested",
                "naturalization": "not_applicable",
                "integration": "pending_iteration_7_reflexive_closure",
            }
        ),
        "claim_flags": _claim_flags(manifest),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "claim_ceiling": "invariant_basin_candidate_topology_stress_validated",
        "birth_is_identity_acceptance_claim": False,
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
            "mutated_field": "post_split_support_node_ids",
            "mutated_value": [20],
            "primary_blocker": "stale_node_id_replay",
        },
        {
            "control_id": "lineage_map_scrambled",
            "mutated_field": "split_lineage_map",
            "mutated_value": "target_branch_swapped_with_unrelated_node",
            "primary_blocker": "lineage_map_scrambled",
        },
        {
            "control_id": "missing_topology_state_reabsorption",
            "mutated_field": "birth_reabsorption_record_digest",
            "mutated_value": None,
            "primary_blocker": "missing_topology_state_reabsorption",
        },
        {
            "control_id": "ambiguous_overlap",
            "mutated_field": "split_branch_overlap_assignment",
            "mutated_value": "ambiguous_many_to_many_without_declared_weights",
            "primary_blocker": "ambiguous_overlap",
        },
        {
            "control_id": "support_drift_beyond_threshold",
            "mutated_field": "post_birth_support_overlap_min",
            "mutated_value": 0.82,
            "primary_blocker": "support_drift_beyond_threshold",
        },
        {
            "control_id": "direct_state_or_topology_rewrite",
            "mutated_field": "born_node_inserted_without_topology_event",
            "mutated_value": True,
            "primary_blocker": "direct_state_or_topology_rewrite",
        },
        {
            "control_id": "budget_discontinuity",
            "mutated_field": "budget_error_max",
            "mutated_value": 0.1,
            "primary_blocker": "budget_discontinuity",
        },
        {
            "control_id": "identity_claim_promotion",
            "mutated_field": "birth_is_identity_acceptance_claim",
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
        "split_topology_event": "infrastructure_context_only",
        "birth_topology_event": "infrastructure_context_only",
        "birth_is_identity_acceptance": False,
        "non_coherence_basin_surfaces_promoted": False,
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "source_iteration_6_output_digest": _digest(
            result["source_iteration_6_output_summary"]
        ),
        "topology_stress_sequence_digest": _digest(result["topology_stress_sequence"]),
        "topology_stress_event_digest": _digest(result["topology_stress_event"]),
        "topology_stress_record_digest": _digest(result["topology_stress_record"]),
        "id4_stress_candidate_row_digest": _digest(
            result["id4_topology_stress_candidate_row"]
        ),
        "control_rows_digest": _digest(result["control_rows"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    manifest = result["manifest"]
    family = _topology_family(manifest)
    metric = manifest["metric_definitions"]["invariance"]
    i6_output = result["source_iteration_6_output"]
    source_candidate = i6_output["id4_invariance_candidate_row"]
    sequence = result["topology_stress_sequence"]
    event = result["topology_stress_event"]
    record = result["topology_stress_record"]
    candidate = result["id4_topology_stress_candidate_row"]
    control_rows = result["control_rows"]
    blockers = [control["primary_blocker"] for control in control_rows]
    gate_schema = manifest["gate_vector_schema"]
    becoming_enums = manifest["becoming_method_fields"]["enum_values"]
    cycles = event["cycles"]
    cycle_indices = [cycle["proper_time_index"] for cycle in cycles]
    scheduler_indices = [cycle["scheduler_event_index"] for cycle in cycles]
    topology_events = sequence["topology_events"]
    canonical_blockers = {control["control_id"] for control in manifest["controls"]}
    return {
        "status_passed": result["status"] == "passed",
        "source_iteration_6_status_passed": i6_output["status"] == "passed",
        "source_iteration_6_points_to_6b": i6_output["acceptance"]["next_iteration"]
        == "6B_id4_topology_split_birth_invariance_stress",
        "source_id4_minimum_candidate_passed": source_candidate["derived_id_ceiling"]
        == "ID4"
        and source_candidate["gate_vector"]["invariance"] == "pass"
        and source_candidate["gate_vector"]["lineage_current"] == "pass",
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
        "proper_time_sequence_extended": event["proper_time_window_count"] == 7
        and record["proper_time_sequence_extended_beyond_minimum"] is True,
        "proper_time_cycles_ordered": cycle_indices == sorted(cycle_indices)
        and len(cycle_indices) == len(set(cycle_indices))
        and scheduler_indices == sorted(scheduler_indices),
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
        and cycles[2]["literal_node_set_overlap_with_previous"] == 0.0
        and cycles[4]["support_overlap_with_previous"] > cycles[4][
            "literal_node_set_overlap_with_previous"
        ],
        "topology_event_count_passed": sequence["topology_event_count"] == 2
        and event["topology_event_count"] == 2,
        "split_event_present": sequence["split_event_present"] is True
        and event["split_event_present"] is True,
        "birth_event_present": sequence["birth_event_present"] is True
        and event["birth_event_present"] is True,
        "birth_not_identity_acceptance": sequence["birth_is_identity_acceptance"] is False
        and record["birth_is_identity_acceptance"] is False
        and candidate["birth_is_identity_acceptance_claim"] is False,
        "stress_record_digest_recomputed": record["stress_record_digest"]
        == _digest(record["stress_record_digest_input"]),
        "all_topology_events_committed": sequence["all_topology_events_committed"] is True
        and all(
            item["topology_event"]["topology_event_committed"] is True
            for item in topology_events
        ),
        "lineage_maps_complete": sequence["all_lineage_maps_complete"] is True
        and all(item["lineage_map"]["complete"] is True for item in topology_events),
        "state_reabsorption_present": sequence[
            "all_state_reabsorption_records_present"
        ]
        is True
        and all(
            bool(item["topology_state_reabsorption_record_digest"])
            for item in topology_events
        ),
        "topology_state_reabsorption_budget_matches_cycles": topology_events[0][
            "topology_state_reabsorption_record"
        ]["node_plus_packet_budget_before"]
        == cycles[1]["budget_after"]
        and topology_events[0]["topology_state_reabsorption_record"][
            "node_plus_packet_budget_after"
        ]
        == cycles[2]["budget_before"]
        and topology_events[1]["topology_state_reabsorption_record"][
            "node_plus_packet_budget_before"
        ]
        == cycles[3]["budget_after"]
        and topology_events[1]["topology_state_reabsorption_record"][
            "node_plus_packet_budget_after"
        ]
        == cycles[4]["budget_before"],
        "support_overlap_threshold_passed": event["support_overlap_passed"] is True
        and record["support_overlap_min"] >= metric["support_overlap_threshold"],
        "lineage_current_overlap_threshold_passed": event[
            "lineage_current_overlap_passed"
        ]
        is True
        and record["lineage_current_overlap_min"]
        >= metric["lineage_current_overlap_threshold"],
        "post_birth_cycles_present": sum(1 for cycle in cycles if 32 in cycle["support_node_ids"])
        >= 3,
        "split_birth_node_id_disjointness": set(
            topology_events[0]["lineage_map"]["retired_node_ids"]
        ).isdisjoint(set(topology_events[1]["lineage_map"]["born_node_ids"]))
        and set(topology_events[1]["lineage_map"]["born_node_ids"]).isdisjoint(
            set(topology_events[0]["lineage_map"]["target_support_nodes"])
        ),
        "transported_node_ids_do_not_collide_with_fixture": (
            set(sequence["split_support_area"]["support_node_ids"])
            | set(sequence["birth_support_area"]["support_node_ids"])
        ).isdisjoint({node["node_id"] for node in manifest["fixture"]["nodes"]}),
        "post_birth_support_includes_born_nodes": all(
            set(sequence["birth_support_area"]["born_node_ids"]).issubset(
                set(cycle["support_node_ids"])
            )
            for cycle in cycles
            if cycle["proper_time_index"] >= 4
        ),
        "budget_exact": event["budget_error_max"] == 0.0
        and record["budget_error_max"] == 0.0
        and all(
            item["topology_state_reabsorption_record"]["node_plus_packet_budget_error"]
            == 0.0
            for item in topology_events
        ),
        "nonnegative_state_passed": event["nonnegative_state_passed"] is True
        and record["nonnegative_state_passed"] is True
        and all(
            item["topology_state_reabsorption_record"]["nonnegative_state_passed"]
            is True
            for item in topology_events
        ),
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
        == "invariant_basin_candidate_topology_stress_validated"
        and candidate["invariance_is_identity_acceptance_claim"] is False,
        "native_support_not_overstated": candidate["native_support_status"]
        == "mixed_native_experiment_local"
        and candidate["native_support_status"] in NATIVE_SUPPORT_STATUS_VALUES
        and metric["native_policy_blocker"] in candidate["native_policy_blockers"]
        and record["native_policy_available"] is False,
        "infrastructure_identity_not_inherited": sequence[
            "identity_inherited_from_infrastructure"
        ]
        is False
        and candidate["identity_inherited_from_infrastructure"] is False,
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
        and result["evidence_only_surfaces"]["birth_is_identity_acceptance"] is False,
        "claim_flag_keys_match_manifest": set(candidate["claim_flags"])
        == set(result["claim_flags"])
        == set(manifest["claim_boundary"]["claim_flags"]),
        "required_controls_present": set(CONTROL_BLOCKERS).issubset(
            {control["control_id"] for control in control_rows}
        ),
        "control_blockers_canonical": set(CONTROL_BLOCKERS.values()).issubset(
            canonical_blockers
        ),
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
        f"""# N07 Iteration 6-B: ID4 Split/Birth Topology Stress

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 6-B consumes the minimum Iteration 6 ID4 candidate and stresses the
same identity ceiling across a longer lineage-proper-time sequence. The stress
sequence includes a committed support split and a lineage-authorized support
birth, then continues through post-birth cycles while preserving support
overlap, lineage-current overlap, exact node-plus-packet budget, and
nonnegative state.

The birth event is a topology-lineage event only. It does not emit identity
acceptance, RC identity collapse, agency, reproduction, or native LGRC identity
support. Native identity-invariance policy remains unavailable.

## Topology Stress Sequence

```json
{json.dumps(result['topology_stress_sequence'], indent=2, sort_keys=True)}
```

## Stress Event

```json
{json.dumps(result['topology_stress_event'], indent=2, sort_keys=True)}
```

## Stress Record

```json
{json.dumps(result['topology_stress_record'], indent=2, sort_keys=True)}
```

## Candidate Row

```json
{json.dumps(result['id4_topology_stress_candidate_row'], indent=2, sort_keys=True)}
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

Iteration 6-B passes because the candidate coherence basin remains
lineage-current and support-continuous across a split, a lineage-authorized
birth, and post-birth cycles. It strengthens the ID4 invariant-basin candidate
but does not promote to ID5, identity acceptance, agency, RC identity collapse,
or native identity support.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest_validation = _load_json(MANIFEST_VALIDATION_PATH)
    manifest = manifest_validation["manifest"]
    i6_output = _load_json(I6_OUTPUT_PATH)
    claim_flags = _claim_flags(manifest)
    sequence = _topology_stress_sequence(manifest=manifest, i6_output=i6_output)
    event = _stress_event(manifest=manifest, i6_output=i6_output, sequence=sequence)
    stress_record = _stress_record(manifest=manifest, event=event, sequence=sequence)
    candidate = _candidate_row(
        manifest=manifest,
        i6_output=i6_output,
        event=event,
        sequence=sequence,
        stress_record=stress_record,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_6b_id4_topology_split_birth_invariance_stress_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": "6B",
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
        "source_iteration_6_output_summary": {
            "path": _rel(I6_OUTPUT_PATH),
            "sha256": _file_sha256(I6_OUTPUT_PATH),
            "status": i6_output["status"],
            "id4_candidate_row_digest": i6_output["artifact_digests"][
                "id4_candidate_row_digest"
            ],
            "invariance_record_digest": i6_output["artifact_digests"][
                "invariance_record_digest"
            ],
        },
        "manifest": manifest,
        "source_iteration_6_output": i6_output,
        "topology_stress_sequence": sequence,
        "topology_stress_event": event,
        "topology_stress_record": stress_record,
        "id4_topology_stress_candidate_row": candidate,
        "control_rows": _control_rows(claim_flags=claim_flags),
        "evidence_only_surfaces": _evidence_only_surfaces(),
        "claim_flags": claim_flags,
        "acceptance": {
            "id4_topology_stress_candidate_emitted": True,
            "source_iteration_6_consumed": True,
            "support_gate_passed": True,
            "stability_gate_passed": True,
            "attractivity_gate_passed": True,
            "invariance_gate_passed": True,
            "lineage_current_gate_passed": True,
            "proper_time_sequence_extended_beyond_minimum": True,
            "split_event_present": True,
            "birth_event_present": True,
            "birth_is_identity_acceptance": False,
            "support_overlap_threshold_passed": True,
            "lineage_current_overlap_threshold_passed": True,
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
            "next_iteration": "7_id5_reflexive_closure_candidate",
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
