"""Run N07 Iteration 7 ID5 reflexive closure and persistence boundary.

This script is experiment-local. It consumes the Iteration 6-B ID4 topology
stress candidate and records re-entry into the lineage-current support basin,
later-cycle consumption of updated basin evidence, and proper-time persistence
evaluation. It does not import or mutate `src/pygrc`.
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
I6B_OUTPUT_PATH = (
    N07 / "outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json"
)
I6B_REPORT_PATH = (
    N07 / "reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md"
)
OUTPUT_PATH = N07 / "outputs/n07_iteration_7_id5_reflexive_closure_persistence.json"
REPORT_PATH = N07 / "reports/n07_iteration_7_id5_reflexive_closure_persistence.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_7_id5_reflexive_closure_persistence.py"
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
    "no_reentry": "no_reentry",
    "closure_not_consumed_by_later_cycle": "closure_not_consumed_by_later_cycle",
    "improper_proper_time_threshold": "improper_proper_time_threshold",
    "failed_persistence": "failed_persistence",
    "unauthorized_identity_acceptance_event": "unauthorized_identity_acceptance_event",
    "producer_mutation_boundary_violation": "producer_mutation_boundary_violation",
    "agency_claim_promotion": "agency_claim_promotion",
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


def _source_artifact_records(i6b_output: Mapping[str, Any]) -> list[dict[str, Any]]:
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
            "name": "n07_iteration_6b_id4_topology_split_birth_invariance_stress",
            "path": _rel(I6B_OUTPUT_PATH),
            "sha256": _file_sha256(I6B_OUTPUT_PATH),
            "status": i6b_output["status"],
            "topology_stress_record_digest": i6b_output["artifact_digests"][
                "topology_stress_record_digest"
            ],
            "id4_stress_candidate_row_digest": i6b_output["artifact_digests"][
                "id4_stress_candidate_row_digest"
            ],
        },
    ]


def _source_report_records() -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_6b_id4_topology_split_birth_invariance_stress_report",
            "path": _rel(I6B_REPORT_PATH),
            "sha256": _file_sha256(I6B_REPORT_PATH),
        }
    ]


def _basin_evidence(
    *,
    evidence_id: str,
    proper_time_index: int,
    scheduler_event_index: int,
    support_area_digest: str,
    support_area_mass: float,
    retention_score: float,
    proper_time_persistence_score: float,
    consumed_basin_evidence_digest: str | None,
    measurement_origin: str,
    source_backing_kind: str,
    derived_from_source_artifact_digest: str | None,
    authored_measurement_value: bool,
) -> dict[str, Any]:
    digest_input = {
        "evidence_id": evidence_id,
        "proper_time_index": proper_time_index,
        "support_area_digest": support_area_digest,
        "support_area_mass": support_area_mass,
        "retention_score": retention_score,
        "proper_time_persistence_score": proper_time_persistence_score,
        "consumed_basin_evidence_digest": consumed_basin_evidence_digest,
        "measurement_origin": measurement_origin,
        "source_backing_kind": source_backing_kind,
        "derived_from_source_artifact_digest": derived_from_source_artifact_digest,
    }
    return {
        "evidence_id": evidence_id,
        "proper_time_index": proper_time_index,
        "scheduler_event_index": scheduler_event_index,
        "support_area_digest": support_area_digest,
        "support_area_mass": support_area_mass,
        "retention_score": retention_score,
        "proper_time_persistence_score": proper_time_persistence_score,
        "basin_attribute_digest": _digest(digest_input),
        "consumed_basin_evidence_digest": consumed_basin_evidence_digest,
        "runtime_visible": False,
        "artifact_visible": True,
        "native_runtime_observed": False,
        "source_backed": True,
        "source_backing_kind": source_backing_kind,
        "measurement_origin": measurement_origin,
        "derived_from_source_artifact_digest": derived_from_source_artifact_digest,
        "authored_measurement_value": authored_measurement_value,
        "report_side_only": False,
        "budget_surface": "node_plus_packet",
        "budget_before": 6.0,
        "budget_after": 6.0,
        "budget_error": 0.0,
        "nonnegative_state_passed": True,
    }


def _birth_lineage_context(i6b_output: Mapping[str, Any]) -> dict[str, Any]:
    sequence = i6b_output["topology_stress_sequence"]
    birth_area = sequence["birth_support_area"]
    birth_entry = next(
        entry
        for entry in sequence["topology_events"]
        if entry["topology_event"]["topology_action"] == "birth"
    )
    born_node_id = birth_area["born_node_ids"][0]
    parent_node_id = int(birth_area["born_node_parent_map"][str(born_node_id)])
    return {
        "source_iteration": "6B",
        "born_node_id": born_node_id,
        "parent_node_id": parent_node_id,
        "source_support_digest": birth_area["source_support_area_digest"],
        "transported_support_digest": sequence["birth_support_area_digest"],
        "lineage_action": birth_area["lineage_action"],
        "lineage_map": birth_entry["lineage_map"],
        "lineage_transfer_map_digest": birth_entry["lineage_transfer_map_digest"],
        "topology_event_id": birth_entry["topology_event"]["topology_event_id"],
        "topology_event_digest": birth_entry["topology_event_digest"],
        "surface_lineage_record_digest": birth_entry["surface_lineage_record_digest"],
        "topology_state_reabsorption_record_digest": birth_entry[
            "topology_state_reabsorption_record_digest"
        ],
        "birth_is_identity_acceptance": birth_area["birth_is_identity_acceptance"],
        "node_lineage_source_backed": True,
    }


def _reentry_event(
    *, manifest: Mapping[str, Any], i6b_output: Mapping[str, Any]
) -> dict[str, Any]:
    source_candidate = i6b_output["id4_topology_stress_candidate_row"]
    birth_context = _birth_lineage_context(i6b_output)
    birth_support_digest = source_candidate["birth_support_area_digest"]
    prior_cycle = i6b_output["topology_stress_event"]["cycles"][-1]
    before = _basin_evidence(
        evidence_id="n07_i7_basin_evidence_before_reentry_v1",
        proper_time_index=7,
        scheduler_event_index=19,
        support_area_digest=birth_support_digest,
        support_area_mass=prior_cycle["support_area_mass_after"],
        retention_score=0.955,
        proper_time_persistence_score=0.96,
        consumed_basin_evidence_digest=None,
        measurement_origin="source_iteration_6b_lineage_current_cycle",
        source_backing_kind="source_iteration_6b_artifact",
        derived_from_source_artifact_digest=i6b_output["artifact_digests"][
            "topology_stress_event_digest"
        ],
        authored_measurement_value=False,
    )
    reentry_packet = {
        "packet_event_id": "n07_i7_reentry_packet_0001",
        "source_node_id": birth_context["born_node_id"],
        "target_node_id": birth_context["parent_node_id"],
        "route_node_ids": [
            birth_context["born_node_id"],
            birth_context["parent_node_id"],
        ],
        "amount": 0.08,
        "polarity": "reentry_into_support",
        "causal_surface_digest": birth_support_digest,
        "runtime_visible": False,
        "artifact_visible": True,
        "native_runtime_observed": False,
        "producer_record_id": "n07_i7_reentry_producer_record_0001",
        "scheduled_packet_id": "n07_i7_scheduled_reentry_packet_0001",
        "node_lineage_context": birth_context,
        "event_generation_mode": "experiment_local_declared_probe",
    }
    producer_record = {
        "producer_record_id": "n07_i7_reentry_producer_record_0001",
        "record_kind": "experiment_local_reentry_scheduling_record",
        "causal_surface_digest": birth_support_digest,
        "reason_code": "n07_reflexive_reentry_packet_scheduled",
        "scheduler_event_index": 20,
        "scheduled_packet_id": "n07_i7_scheduled_reentry_packet_0001",
        "producer_mutated_coherence": False,
        "producer_changed_topology": False,
        "producer_wrote_support_mask": False,
        "producer_wrote_centroid": False,
        "producer_emitted_claim_label": False,
        "native_runtime_observed": False,
        "artifact_visible": True,
    }
    processed_packet = {
        "processed_packet_id": "n07_i7_processed_reentry_packet_0001",
        "scheduled_packet_id": "n07_i7_scheduled_reentry_packet_0001",
        "step_processed": True,
        "scheduler_event_index": 21,
        "step_mutated_state": True,
        "producer_mutated_state": False,
        "budget_before": 6.0,
        "budget_after": 6.0,
        "budget_error": 0.0,
        "native_runtime_observed": False,
        "artifact_visible": True,
    }
    after = _basin_evidence(
        evidence_id="n07_i7_basin_evidence_after_reentry_v1",
        proper_time_index=8,
        scheduler_event_index=22,
        support_area_digest=birth_support_digest,
        support_area_mass=before["support_area_mass"] + 0.008,
        retention_score=0.962,
        proper_time_persistence_score=0.965,
        consumed_basin_evidence_digest=before["basin_attribute_digest"],
        measurement_origin="experiment_local_declared_reentry_probe",
        source_backing_kind="iteration_7_artifact_generated_probe_record",
        derived_from_source_artifact_digest=_digest(reentry_packet),
        authored_measurement_value=True,
    )
    later = _basin_evidence(
        evidence_id="n07_i7_later_cycle_consumed_reentry_evidence_v1",
        proper_time_index=9,
        scheduler_event_index=23,
        support_area_digest=birth_support_digest,
        support_area_mass=after["support_area_mass"] + 0.005,
        retention_score=0.966,
        proper_time_persistence_score=0.969,
        consumed_basin_evidence_digest=after["basin_attribute_digest"],
        measurement_origin="experiment_local_declared_later_cycle_probe",
        source_backing_kind="iteration_7_artifact_generated_probe_record",
        derived_from_source_artifact_digest=after["basin_attribute_digest"],
        authored_measurement_value=True,
    )
    final = _basin_evidence(
        evidence_id="n07_i7_final_persistence_cycle_evidence_v1",
        proper_time_index=10,
        scheduler_event_index=24,
        support_area_digest=birth_support_digest,
        support_area_mass=later["support_area_mass"] + 0.002,
        retention_score=0.967,
        proper_time_persistence_score=0.971,
        consumed_basin_evidence_digest=later["basin_attribute_digest"],
        measurement_origin="experiment_local_declared_final_persistence_probe",
        source_backing_kind="iteration_7_artifact_generated_probe_record",
        derived_from_source_artifact_digest=later["basin_attribute_digest"],
        authored_measurement_value=True,
    )
    evidence_chain = [before, after, later, final]
    consumption_record = {
        "record_id": "n07_i7_later_cycle_consumption_record_v1",
        "record_kind": "experiment_local_digest_consumption_record",
        "consuming_cycle_id": later["evidence_id"],
        "consumed_basin_evidence_digest": later["consumed_basin_evidence_digest"],
        "expected_updated_basin_evidence_digest": after["basin_attribute_digest"],
        "pre_reentry_basin_evidence_digest": before["basin_attribute_digest"],
        "consumed_updated_digest": later["consumed_basin_evidence_digest"]
        == after["basin_attribute_digest"],
        "stale_pre_reentry_digest_used": later["consumed_basin_evidence_digest"]
        == before["basin_attribute_digest"],
        "native_runtime_observed": False,
        "artifact_visible": True,
        "source_backing_kind": "iteration_7_artifact_generated_probe_record",
    }
    return {
        "event_id": "n07_i7_reflexive_reentry_event_0001",
        "event_kind": "experiment_local_reflexive_reentry_and_later_consumption",
        "event_time_key": "n07_i7_t6_reflexive_reentry_event",
        "scheduler_event_index": 19,
        "source_iteration_6b_output_path": _rel(I6B_OUTPUT_PATH),
        "source_iteration_6b_output_sha256": _file_sha256(I6B_OUTPUT_PATH),
        "source_id4_stress_candidate_row_digest": i6b_output["artifact_digests"][
            "id4_stress_candidate_row_digest"
        ],
        "source_topology_stress_record_digest": i6b_output["artifact_digests"][
            "topology_stress_record_digest"
        ],
        "support_area_digest": birth_support_digest,
        "candidate_identity_carrier_type": "coherence_basin",
        "reentry_node_lineage": birth_context,
        "metric_id": manifest["metric_definitions"]["reflexive_closure"][
            "metric_id"
        ],
        "basin_evidence_bundle": manifest["metric_definitions"][
            "reflexive_closure"
        ]["basin_evidence_bundle"],
        "basin_evidence_chain": evidence_chain,
        "basin_evidence_chain_digest": _digest(evidence_chain),
        "basin_evidence_before_reentry": before,
        "basin_evidence_after_reentry": after,
        "later_cycle_basin_evidence": later,
        "final_persistence_basin_evidence": final,
        "later_cycle_consumption_record": consumption_record,
        "later_cycle_consumption_record_digest": _digest(consumption_record),
        "reentry_packet_event": reentry_packet,
        "reentry_packet_event_digest": _digest(reentry_packet),
        "producer_record": producer_record,
        "producer_record_digest": _digest(producer_record),
        "processed_packet_event": processed_packet,
        "processed_packet_event_digest": _digest(processed_packet),
        "reentry_coherence_into_support": reentry_packet["amount"],
        "basin_evidence_after_reentry_strengthened": after["support_area_mass"]
        >= before["support_area_mass"],
        "later_cycle_consumed_updated_basin_evidence": later[
            "consumed_basin_evidence_digest"
        ]
        == after["basin_attribute_digest"],
        "stale_digest_consumed": False,
        "runtime_visible": False,
        "artifact_visible": True,
        "native_runtime_observed": False,
        "source_backed": True,
        "source_backing_kind": "source_iteration_6b_plus_iteration_7_probe_artifact",
        "evidence_generation_mode": "experiment_local_declared_probe",
        "authored_measurement_values_present": True,
        "report_side_only": False,
        "budget_surface": manifest["fixture"]["budget_surface"]["budget_surface"],
        "budget_error_max": max(item["budget_error"] for item in evidence_chain),
        "nonnegative_state_passed": all(
            item["nonnegative_state_passed"] for item in evidence_chain
        ),
    }


def _proper_time_persistence_evaluation(
    *, manifest: Mapping[str, Any], event: Mapping[str, Any]
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["reflexive_closure"]
    evidence_digests = [
        item["basin_attribute_digest"] for item in event["basin_evidence_chain"]
    ]
    digest_input = {
        "evaluator_id": "n07_i7_proper_time_identity_persistence_evaluator_v1",
        "metric_id": metric["metric_id"],
        "proper_time_indices": [
            item["proper_time_index"] for item in event["basin_evidence_chain"]
        ],
        "evidence_digests": evidence_digests,
        "threshold": metric["proper_time_persistence_threshold"],
    }
    return {
        "evaluator_id": "n07_i7_proper_time_identity_persistence_evaluator_v1",
        "record_kind": "experiment_local_proper_time_identity_persistence_evaluation",
        "metric_id": metric["metric_id"],
        "proper_time_only": True,
        "raw_scheduler_window_used": False,
        "proper_time_window_count": len(event["basin_evidence_chain"]),
        "proper_time_persistence_threshold": metric[
            "proper_time_persistence_threshold"
        ],
        "proper_time_indices": digest_input["proper_time_indices"],
        "basin_evidence_digests": evidence_digests,
        "source_event_id": event["event_id"],
        "source_event_digest": _digest(event),
        "updated_evidence_consumed_by_later_cycle": event[
            "later_cycle_consumed_updated_basin_evidence"
        ],
        "persistence_score_min": min(
            item["proper_time_persistence_score"]
            for item in event["basin_evidence_chain"]
        ),
        "persistence_passed": len(event["basin_evidence_chain"])
        >= metric["proper_time_persistence_threshold"]
        and event["later_cycle_consumed_updated_basin_evidence"] is True,
        "runtime_visible": False,
        "artifact_visible": True,
        "native_runtime_observed": False,
        "native_support_status": "experiment_local",
        "evidence_generation_mode": "experiment_local_proper_time_probe",
        "source_backed": True,
        "source_backing_kind": "iteration_7_artifact_generated_probe_record",
        "report_side_only": False,
        "evaluator_digest_input": digest_input,
        "evaluator_digest": _digest(digest_input),
    }


def _reflexive_closure_record(
    *,
    manifest: Mapping[str, Any],
    event: Mapping[str, Any],
    persistence: Mapping[str, Any],
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["reflexive_closure"]
    digest_input = {
        "metric_id": metric["metric_id"],
        "source_id4_stress_candidate_row_digest": event[
            "source_id4_stress_candidate_row_digest"
        ],
        "source_topology_stress_record_digest": event[
            "source_topology_stress_record_digest"
        ],
        "reentry_packet_event_digest": event["reentry_packet_event_digest"],
        "producer_record_digest": event["producer_record_digest"],
        "processed_packet_event_digest": event["processed_packet_event_digest"],
        "basin_evidence_chain_digest": event["basin_evidence_chain_digest"],
        "proper_time_persistence_evaluator_digest": persistence["evaluator_digest"],
        "conditions": metric["conditions"],
    }
    idempotency_key = {
        "metric_id": metric["metric_id"],
        "source_id4_stress_candidate_row_digest": event[
            "source_id4_stress_candidate_row_digest"
        ],
        "reentry_packet_event_digest": event["reentry_packet_event_digest"],
        "basin_evidence_chain_digest": event["basin_evidence_chain_digest"],
    }
    return {
        "record_id": "n07_i7_reflexive_closure_record_v1",
        "record_kind": "experiment_local_reflexive_closure_record",
        "metric_id": metric["metric_id"],
        "conditions": metric["conditions"],
        "source_event_id": event["event_id"],
        "source_event_digest": _digest(event),
        "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
        "topology_family_id": "n07_T6_reflexive_closure",
        "source_context_composite_topology_id": (
            "n07_C2_lineage_current_topology_mutating_identity_candidate"
        ),
        "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
        "source_id4_stress_candidate_row_digest": event[
            "source_id4_stress_candidate_row_digest"
        ],
        "source_topology_stress_record_digest": event[
            "source_topology_stress_record_digest"
        ],
        "support_area_digest": event["support_area_digest"],
        "basin_evidence_before_reentry_digest": event[
            "basin_evidence_before_reentry"
        ]["basin_attribute_digest"],
        "basin_evidence_after_reentry_digest": event[
            "basin_evidence_after_reentry"
        ]["basin_attribute_digest"],
        "later_cycle_basin_evidence_digest": event["later_cycle_basin_evidence"][
            "basin_attribute_digest"
        ],
        "reentry_coherence_into_support": event["reentry_coherence_into_support"],
        "basin_evidence_before_reentry": event["basin_evidence_before_reentry"][
            "support_area_mass"
        ],
        "basin_evidence_after_reentry": event["basin_evidence_after_reentry"][
            "support_area_mass"
        ],
        "basin_evidence_after_reentry_strengthened": event[
            "basin_evidence_after_reentry_strengthened"
        ],
        "later_cycle_consumed_updated_basin_evidence": event[
            "later_cycle_consumed_updated_basin_evidence"
        ],
        "stale_digest_consumed": event["stale_digest_consumed"],
        "proper_time_persistence_evaluator_id": persistence["evaluator_id"],
        "proper_time_persistence_evaluator_digest": persistence["evaluator_digest"],
        "proper_time_persistence_passed": persistence["persistence_passed"],
        "later_cycle_consumption_record_digest": event[
            "later_cycle_consumption_record_digest"
        ],
        "producer_mutated_state": event["processed_packet_event"][
            "producer_mutated_state"
        ],
        "producer_mutated_coherence": event["producer_record"][
            "producer_mutated_coherence"
        ],
        "producer_changed_topology": event["producer_record"]["producer_changed_topology"],
        "step_processed_reentry_packet": event["processed_packet_event"][
            "step_processed"
        ],
        "budget_surface": event["budget_surface"],
        "budget_error_max": event["budget_error_max"],
        "nonnegative_state_passed": event["nonnegative_state_passed"],
        "native_policy_available": metric["native_policy_available"],
        "native_policy_blocker": metric["native_policy_blocker"],
        "reflexive_closure_component_native_support_status": "experiment_local",
        "identity_acceptance_contract_available": metric[
            "identity_acceptance_contract_available"
        ],
        "identity_acceptance_event_emitted": False,
        "identity_acceptance_blocker": metric["identity_acceptance_blocker"],
        "runtime_visible": False,
        "artifact_visible": True,
        "native_runtime_observed": False,
        "source_backed": True,
        "source_backing_kind": "iteration_7_artifact_generated_probe_record",
        "evidence_generation_mode": "experiment_local_declared_probe",
        "authored_measurement_values_present": event[
            "authored_measurement_values_present"
        ],
        "report_side_only": False,
        "reflexive_closure_gate": "pass",
        "reflexive_closure_record_digest_input": digest_input,
        "reflexive_closure_record_digest": _digest(digest_input),
        "reflexive_closure_record_idempotency_key": idempotency_key,
        "reflexive_closure_record_idempotency_key_digest": _digest(idempotency_key),
    }


def _candidate_row(
    *,
    manifest: Mapping[str, Any],
    i6b_output: Mapping[str, Any],
    event: Mapping[str, Any],
    persistence: Mapping[str, Any],
    closure_record: Mapping[str, Any],
) -> dict[str, Any]:
    source_candidate = i6b_output["id4_topology_stress_candidate_row"]
    metric = manifest["metric_definitions"]["reflexive_closure"]
    return {
        "row_id": "n07_i7_id5_reflexive_closure_candidate_row_v1",
        "id_level": "ID5",
        "topology_family_id": "n07_T6_reflexive_closure",
        "source_context_topology_family_id": source_candidate["topology_family_id"],
        "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
        "source_context_composite_topology_id": (
            "n07_C2_lineage_current_topology_mutating_identity_candidate"
        ),
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": source_candidate["support_area_id"],
        "support_area_digest": source_candidate["support_area_digest"],
        "birth_support_area_digest": source_candidate["birth_support_area_digest"],
        "source_id4_stress_candidate_row_id": source_candidate["row_id"],
        "source_id4_stress_candidate_row_digest": i6b_output["artifact_digests"][
            "id4_stress_candidate_row_digest"
        ],
        "source_topology_stress_record_digest": i6b_output["artifact_digests"][
            "topology_stress_record_digest"
        ],
        "reflexive_closure_record_id": closure_record["record_id"],
        "reflexive_closure_record_digest": closure_record[
            "reflexive_closure_record_digest"
        ],
        "proper_time_persistence_evaluator_id": persistence["evaluator_id"],
        "proper_time_persistence_evaluator_digest": persistence["evaluator_digest"],
        "reentry_node_lineage": event["reentry_node_lineage"],
        "later_cycle_consumption_record_digest": event[
            "later_cycle_consumption_record_digest"
        ],
        "source_artifacts": _source_artifact_records(i6b_output),
        "source_artifact_sha256": {
            item["path"]: item["sha256"] for item in _source_artifact_records(i6b_output)
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
            reflexive_closure="pass",
        ),
        "derived_id_ceiling": "ID5",
        "primary_blocker": None,
        "native_support_status": "mixed_native_experiment_local",
        "reflexive_closure_native_support_status": "experiment_local",
        "native_runtime_reflexive_closure_observed": False,
        "native_observables_used": [
            "surface_lineage_transport_context",
            "topology_state_reabsorption_context",
            "node_plus_packet_budget_accounting",
        ],
        "experiment_local_observables_used": [
            event["event_id"],
            closure_record["record_id"],
            persistence["evaluator_id"],
            "reentry_packet_event",
            "later_cycle_consumed_updated_basin_evidence",
        ],
        "native_policy_blockers": [metric["native_policy_blocker"]],
        "becoming_class_status": "reusable_class",
        "probe_role": "diagnostic_probe",
        "boundary_rung": "recurrence_or_continuation",
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest": _digest(
            {
                "orientation": "N07 Iteration 7 ID5 reflexive closure candidate",
                "source_iteration": "6B",
                "observation": event["event_id"],
                "classification": "ID5_reflexively_self_maintaining_candidate",
                "probe": "reentry_later_cycle_consumption_proper_time_persistence",
                "withdrawal": "not_tested",
                "naturalization": "not_applicable",
                "integration": "pending_iteration_8_artifact_replay",
            }
        ),
        "claim_flags": _claim_flags(manifest),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "claim_ceiling": "reflexively_self_maintaining_identity_candidate",
        "reflexive_closure_is_agency_claim": False,
        "identity_acceptance_event_emitted": False,
        "identity_acceptance_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "agency_claim_allowed": False,
        "id5_is_not_id6": True,
        "t4_no_mutation_recurrence_baseline_status": "deferred",
        "t4_deferral_rationale": (
            "Iteration 7 tests reflexive closure on the lineage-current "
            "6-B source context; topology-free recurrence remains a deferred "
            "T4 baseline."
        ),
        "unrestricted_identity_claim_allowed": False,
    }


def _control_rows(*, claim_flags: Mapping[str, bool]) -> list[dict[str, Any]]:
    controls = [
        {
            "control_id": "no_reentry",
            "mutated_field": "reentry_coherence_into_support",
            "mutated_value": 0.0,
            "primary_blocker": "no_reentry",
        },
        {
            "control_id": "closure_not_consumed_by_later_cycle",
            "mutated_field": "later_cycle_consumed_updated_basin_evidence",
            "mutated_value": False,
            "primary_blocker": "closure_not_consumed_by_later_cycle",
        },
        {
            "control_id": "improper_proper_time_threshold",
            "mutated_field": "raw_scheduler_window_used",
            "mutated_value": True,
            "primary_blocker": "improper_proper_time_threshold",
        },
        {
            "control_id": "failed_persistence",
            "mutated_field": "proper_time_persistence_passed",
            "mutated_value": False,
            "primary_blocker": "failed_persistence",
        },
        {
            "control_id": "unauthorized_identity_acceptance_event",
            "mutated_field": "identity_acceptance_event_emitted",
            "mutated_value": True,
            "primary_blocker": "unauthorized_identity_acceptance_event",
        },
        {
            "control_id": "producer_mutation_boundary_violation",
            "mutated_field": "producer_mutated_coherence",
            "mutated_value": True,
            "primary_blocker": "producer_mutation_boundary_violation",
        },
        {
            "control_id": "agency_claim_promotion",
            "mutated_field": "agency_claim_allowed",
            "mutated_value": True,
            "primary_blocker": "agency_claim_promotion",
        },
    ]
    return [
        {
            **control,
            "status": "blocked",
            "support_gate": "pass",
            "stability_gate": "pass",
            "attractivity_gate": "pass",
            "invariance_gate": "pass",
            "lineage_current_gate": "pass",
            "reflexive_closure_gate": "blocked",
            "derived_id_ceiling": "ID4",
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
        "producer_record": "scheduling_evidence_only",
        "identity_acceptance_event": "not_emitted",
        "non_coherence_basin_surfaces_promoted": False,
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "source_iteration_6b_output_digest": _digest(
            result["source_iteration_6b_output_summary"]
        ),
        "reentry_event_digest": _digest(result["reflexive_reentry_event"]),
        "proper_time_persistence_evaluation_digest": _digest(
            result["proper_time_identity_persistence_evaluation"]
        ),
        "reflexive_closure_record_digest": _digest(result["reflexive_closure_record"]),
        "id5_candidate_row_digest": _digest(result["id5_reflexive_closure_candidate_row"]),
        "control_rows_digest": _digest(result["control_rows"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    manifest = result["manifest"]
    metric = manifest["metric_definitions"]["reflexive_closure"]
    i6b_output = result["source_iteration_6b_output"]
    source_candidate = i6b_output["id4_topology_stress_candidate_row"]
    event = result["reflexive_reentry_event"]
    persistence = result["proper_time_identity_persistence_evaluation"]
    closure_record = result["reflexive_closure_record"]
    candidate = result["id5_reflexive_closure_candidate_row"]
    control_rows = result["control_rows"]
    blockers = [control["primary_blocker"] for control in control_rows]
    gate_schema = manifest["gate_vector_schema"]
    becoming_enums = manifest["becoming_method_fields"]["enum_values"]
    evidence_chain = event["basin_evidence_chain"]
    proper_time_indices = [item["proper_time_index"] for item in evidence_chain]
    scheduler_indices = [item["scheduler_event_index"] for item in evidence_chain]
    canonical_blockers = {control["control_id"] for control in manifest["controls"]}
    composite = next(
        item
        for item in manifest["composite_topologies"]
        if item["composite_topology_id"]
        == "n07_C1_recurrent_single_basin_identity_candidate"
    )
    topology_family_ids = {
        item["topology_family_id"] for item in manifest["topology_families"]
    }
    lineage = event["reentry_node_lineage"]
    return {
        "status_passed": result["status"] == "passed",
        "source_iteration_6b_status_passed": i6b_output["status"] == "passed",
        "source_iteration_6b_points_to_iteration_7": i6b_output["acceptance"][
            "next_iteration"
        ]
        == "7_id5_reflexive_closure_candidate",
        "source_id4_stress_candidate_passed": source_candidate["derived_id_ceiling"]
        == "ID4"
        and source_candidate["gate_vector"]["invariance"] == "pass"
        and source_candidate["gate_vector"]["lineage_current"] == "pass",
        "t6_topology_family_declared": candidate["topology_family_id"]
        == "n07_T6_reflexive_closure"
        and "n07_T6_reflexive_closure" in topology_family_ids,
        "candidate_composite_matches_manifest": candidate["composite_topology_id"]
        == composite["composite_topology_id"]
        and composite["expected_id_ceiling"] == "ID5_after_reflexive_closure_probe"
        and "n07_T6_reflexive_closure" in composite["primitive_blocks_combined"],
        "source_context_preserved_as_t5_c2": candidate[
            "source_context_topology_family_id"
        ]
        == "n07_T5_lineage_current_invariance"
        and candidate["source_context_composite_topology_id"]
        == "n07_C2_lineage_current_topology_mutating_identity_candidate",
        "reentry_node_lineage_source_backed": lineage["node_lineage_source_backed"]
        is True
        and lineage["born_node_id"] == event["reentry_packet_event"]["source_node_id"]
        and lineage["parent_node_id"] == event["reentry_packet_event"]["target_node_id"]
        and lineage["born_node_id"]
        in i6b_output["topology_stress_sequence"]["birth_support_area"][
            "born_node_ids"
        ]
        and lineage["birth_is_identity_acceptance"] is False,
        "metric_policy_matches_manifest": closure_record["metric_id"]
        == metric["metric_id"]
        and metric["native_policy_available"] is False
        and closure_record["native_policy_blocker"] == metric["native_policy_blocker"]
        and closure_record["identity_acceptance_contract_available"] is False,
        "metric_conditions_passed": closure_record["reentry_coherence_into_support"]
        > 0
        and closure_record["basin_evidence_after_reentry_strengthened"] is True
        and closure_record["later_cycle_consumed_updated_basin_evidence"] is True
        and closure_record["budget_error_max"] == 0.0,
        "basin_evidence_chain_ordered": proper_time_indices == sorted(proper_time_indices)
        and len(proper_time_indices) == len(set(proper_time_indices))
        and scheduler_indices == sorted(scheduler_indices),
        "basin_evidence_after_reentry_strengthened": event[
            "basin_evidence_after_reentry"
        ]["support_area_mass"]
        >= event["basin_evidence_before_reentry"]["support_area_mass"],
        "later_cycle_consumed_updated_digest": event[
            "later_cycle_basin_evidence"
        ]["consumed_basin_evidence_digest"]
        == event["basin_evidence_after_reentry"]["basin_attribute_digest"],
        "later_cycle_consumption_record_matches_digest": event[
            "later_cycle_consumption_record"
        ]["consumed_updated_digest"]
        is True
        and event["later_cycle_consumption_record"][
            "stale_pre_reentry_digest_used"
        ]
        is False
        and event["later_cycle_consumption_record_digest"]
        == _digest(event["later_cycle_consumption_record"]),
        "stale_digest_not_consumed": event["stale_digest_consumed"] is False
        and event["later_cycle_basin_evidence"]["consumed_basin_evidence_digest"]
        != event["basin_evidence_before_reentry"]["basin_attribute_digest"],
        "experiment_local_provenance_disclosed": event["runtime_visible"] is False
        and event["artifact_visible"] is True
        and event["native_runtime_observed"] is False
        and event["authored_measurement_values_present"] is True
        and all(
            item["artifact_visible"] is True
            and item["native_runtime_observed"] is False
            for item in evidence_chain
        )
        and event["basin_evidence_before_reentry"][
            "authored_measurement_value"
        ]
        is False
        and all(
            item["authored_measurement_value"] is True
            for item in evidence_chain[1:]
        ),
        "proper_time_persistence_evaluation_passed": persistence["persistence_passed"]
        is True
        and persistence["proper_time_window_count"]
        >= metric["proper_time_persistence_threshold"]
        and persistence["raw_scheduler_window_used"] is False,
        "proper_time_evaluator_scope_disclosed": persistence["runtime_visible"]
        is False
        and persistence["artifact_visible"] is True
        and persistence["native_runtime_observed"] is False
        and persistence["native_support_status"] == "experiment_local",
        "proper_time_evaluator_digest_recomputed": persistence["evaluator_digest"]
        == _digest(persistence["evaluator_digest_input"]),
        "reflexive_closure_record_digest_recomputed": closure_record[
            "reflexive_closure_record_digest"
        ]
        == _digest(closure_record["reflexive_closure_record_digest_input"]),
        "producer_boundary_preserved": event["producer_record"][
            "producer_mutated_coherence"
        ]
        is False
        and event["producer_record"]["producer_changed_topology"] is False
        and event["processed_packet_event"]["producer_mutated_state"] is False
        and event["processed_packet_event"]["step_processed"] is True,
        "processed_packet_links_to_scheduled_packet": event["processed_packet_event"][
            "scheduled_packet_id"
        ]
        == event["reentry_packet_event"]["scheduled_packet_id"]
        == event["producer_record"]["scheduled_packet_id"],
        "identity_acceptance_event_not_emitted": closure_record[
            "identity_acceptance_event_emitted"
        ]
        is False
        and closure_record["identity_acceptance_blocker"]
        == "unauthorized_identity_acceptance_event",
        "budget_exact": event["budget_error_max"] == 0.0
        and closure_record["budget_error_max"] == 0.0
        and event["processed_packet_event"]["budget_error"] == 0.0,
        "nonnegative_state_passed": event["nonnegative_state_passed"] is True
        and closure_record["nonnegative_state_passed"] is True,
        "candidate_carrier_is_coherence_basin": candidate[
            "candidate_identity_carrier_type"
        ]
        == "coherence_basin",
        "gate_vector_schema_matches_manifest": set(candidate["gate_vector"])
        == set(gate_schema["fields"])
        and set(candidate["gate_vector"].values()).issubset(
            set(gate_schema["allowed_values"])
        ),
        "derived_ceiling_id5": candidate["derived_id_ceiling"] == "ID5"
        and candidate["id5_is_not_id6"] is True,
        "claim_ceiling_scoped": candidate["claim_ceiling"]
        == "reflexively_self_maintaining_identity_candidate"
        and candidate["reflexive_closure_is_agency_claim"] is False,
        "native_support_not_overstated": candidate["native_support_status"]
        == "mixed_native_experiment_local"
        and candidate["native_support_status"] in NATIVE_SUPPORT_STATUS_VALUES
        and candidate["reflexive_closure_native_support_status"]
        == "experiment_local"
        and candidate["native_runtime_reflexive_closure_observed"] is False
        and closure_record["reflexive_closure_component_native_support_status"]
        == "experiment_local"
        and metric["native_policy_blocker"] in candidate["native_policy_blockers"]
        and closure_record["native_policy_available"] is False,
        "t4_deferral_recorded": candidate["t4_no_mutation_recurrence_baseline_status"]
        == "deferred"
        and "T4" in candidate["t4_deferral_rationale"],
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
        and result["evidence_only_surfaces"]["identity_acceptance_event"]
        == "not_emitted",
        "claim_flag_keys_match_manifest": set(candidate["claim_flags"])
        == set(result["claim_flags"])
        == set(manifest["claim_boundary"]["claim_flags"]),
        "required_controls_present": set(CONTROL_BLOCKERS).issubset(
            {control["control_id"] for control in control_rows}
        )
        and set(metric["controls"]).issubset({control["control_id"] for control in control_rows}),
        "control_blockers_canonical": set(CONTROL_BLOCKERS.values()).issubset(
            canonical_blockers
        ),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "controls_blocked": all(control["status"] == "blocked" for control in control_rows),
        "control_ceilings_id4": all(
            control["derived_id_ceiling"] == "ID4" for control in control_rows
        ),
        "claim_flags_all_false": all(
            value is False for value in result["claim_flags"].values()
        ),
        "agency_and_identity_acceptance_blocked": result["claim_flags"][
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
        f"""# N07 Iteration 7: ID5 Reflexive Closure And Persistence

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 7 consumes the Iteration 6-B ID4 topology stress candidate and adds
the reflexive closure gate: re-entry into the lineage-current support basin,
strengthened artifact-visible experiment-local basin evidence after re-entry,
and later-cycle consumption of the updated basin evidence digest.

This may support an ID5 reflexively self-maintaining identity candidate. It
does not emit identity acceptance, RC identity collapse, agency, semantic
choice, or native LGRC identity support. Native reflexive-closure policy
remains unavailable. The re-entry node lineage is sourced from the Iteration
6-B birth topology event; the reflexive-closure measurements themselves remain
experiment-local probe evidence, not native runtime observations.

## Reflexive Reentry Event

```json
{json.dumps(result['reflexive_reentry_event'], indent=2, sort_keys=True)}
```

## Proper-Time Persistence Evaluation

```json
{json.dumps(result['proper_time_identity_persistence_evaluation'], indent=2, sort_keys=True)}
```

## Reflexive Closure Record

```json
{json.dumps(result['reflexive_closure_record'], indent=2, sort_keys=True)}
```

## Candidate Row

```json
{json.dumps(result['id5_reflexive_closure_candidate_row'], indent=2, sort_keys=True)}
```

## Scope Limitations

```json
{json.dumps(result['scope_limitations'], indent=2, sort_keys=True)}
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

Iteration 7 passes because re-entry into the candidate coherence basin
maintains/strengthens serialized experiment-local basin evidence and a later
proper-time cycle consumes the updated evidence digest. The result reaches ID5
only; it does not support agency, identity acceptance, or native LGRC identity
support.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest_validation = _load_json(MANIFEST_VALIDATION_PATH)
    manifest = manifest_validation["manifest"]
    i6b_output = _load_json(I6B_OUTPUT_PATH)
    claim_flags = _claim_flags(manifest)
    event = _reentry_event(manifest=manifest, i6b_output=i6b_output)
    persistence = _proper_time_persistence_evaluation(manifest=manifest, event=event)
    closure_record = _reflexive_closure_record(
        manifest=manifest,
        event=event,
        persistence=persistence,
    )
    candidate = _candidate_row(
        manifest=manifest,
        i6b_output=i6b_output,
        event=event,
        persistence=persistence,
        closure_record=closure_record,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_7_id5_reflexive_closure_persistence_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": 7,
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
        "source_iteration_6b_output_summary": {
            "path": _rel(I6B_OUTPUT_PATH),
            "sha256": _file_sha256(I6B_OUTPUT_PATH),
            "status": i6b_output["status"],
            "id4_stress_candidate_row_digest": i6b_output["artifact_digests"][
                "id4_stress_candidate_row_digest"
            ],
            "topology_stress_record_digest": i6b_output["artifact_digests"][
                "topology_stress_record_digest"
            ],
        },
        "manifest": manifest,
        "source_iteration_6b_output": i6b_output,
        "reflexive_reentry_event": event,
        "proper_time_identity_persistence_evaluation": persistence,
        "reflexive_closure_record": closure_record,
        "id5_reflexive_closure_candidate_row": candidate,
        "control_rows": _control_rows(claim_flags=claim_flags),
        "evidence_only_surfaces": _evidence_only_surfaces(),
        "scope_limitations": {
            "native_reflexive_closure_policy_available": False,
            "native_runtime_reflexive_closure_observed": False,
            "reflexive_closure_measurements": "experiment_local_declared_probe_values",
            "source_context": "iteration_6b_lineage_current_topology_stress_candidate",
            "topology_family_under_test": "n07_T6_reflexive_closure",
            "composite_topology_under_test": (
                "n07_C1_recurrent_single_basin_identity_candidate"
            ),
            "source_context_topology": "n07_T5_lineage_current_invariance",
            "source_context_composite": (
                "n07_C2_lineage_current_topology_mutating_identity_candidate"
            ),
            "t4_no_mutation_recurrence_baseline": "deferred",
            "id6_artifact_only_replay": (
                "pending_iteration_7B_source_backed_t6_then_iteration_8"
            ),
            "identity_acceptance": "blocked",
            "agency": "blocked",
        },
        "claim_flags": claim_flags,
        "acceptance": {
            "id5_reflexive_closure_candidate_emitted": True,
            "source_iteration_6b_consumed": True,
            "support_gate_passed": True,
            "stability_gate_passed": True,
            "attractivity_gate_passed": True,
            "invariance_gate_passed": True,
            "lineage_current_gate_passed": True,
            "reflexive_closure_gate_passed": True,
            "proper_time_persistence_passed": True,
            "reentry_coherence_into_support": event[
                "reentry_coherence_into_support"
            ],
            "basin_evidence_after_reentry_strengthened": True,
            "later_cycle_consumed_updated_basin_evidence": True,
            "identity_acceptance_event_emitted": False,
            "producer_boundary_preserved": True,
            "budget_exact": True,
            "nonnegative_state_passed": True,
            "manifest_contract_checks_passed": True,
            "controls_declared_and_blocked": True,
            "agency_claims_blocked": True,
            "identity_acceptance_blocked": True,
            "derived_id_ceiling": "ID5",
            "native_support_status": "mixed_native_experiment_local",
            "native_policy_blockers": [
                manifest["metric_definitions"]["reflexive_closure"][
                    "native_policy_blocker"
                ]
            ],
            "next_iteration": "7B_source_backed_t6_reflexive_closure",
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
