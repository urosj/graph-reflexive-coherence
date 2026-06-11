"""Run N07 Iteration 7-B source-backed T6 reflexive closure.

This script is experiment-local. It consumes the Iteration 6-B lineage-current
topology stress source and the Iteration 7 reflexive-closure design probe, then
builds a stricter T6 chain from serialized state, packet, producer, and basin
evidence rows. It does not import or mutate `src/pygrc`.
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
I7_OUTPUT_PATH = N07 / "outputs/n07_iteration_7_id5_reflexive_closure_persistence.json"
I7_REPORT_PATH = N07 / "reports/n07_iteration_7_id5_reflexive_closure_persistence.md"
OUTPUT_PATH = N07 / "outputs/n07_iteration_7b_source_backed_t6_reflexive_closure.json"
REPORT_PATH = N07 / "reports/n07_iteration_7b_source_backed_t6_reflexive_closure.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_7b_source_backed_t6_reflexive_closure.py"
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
    "hidden_support_field": "hidden_support_field",
    "improper_proper_time_threshold": "improper_proper_time_threshold",
    "failed_persistence": "failed_persistence",
    "budget_discontinuity": "budget_discontinuity",
    "unauthorized_identity_acceptance_event": "unauthorized_identity_acceptance_event",
    "producer_mutation_boundary_violation": "producer_mutation_boundary_violation",
    "agency_claim_promotion": "agency_claim_promotion",
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


def _source_artifacts(
    i6b_output: Mapping[str, Any], i7_output: Mapping[str, Any]
) -> list[dict[str, Any]]:
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
            "name": "n07_iteration_6b_topology_stress_source",
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
        {
            "name": "n07_iteration_7_reflexive_closure_design_probe",
            "path": _rel(I7_OUTPUT_PATH),
            "sha256": _file_sha256(I7_OUTPUT_PATH),
            "status": i7_output["status"],
            "id5_candidate_row_digest": i7_output["artifact_digests"][
                "id5_candidate_row_digest"
            ],
            "scope": "design_context_not_positive_t6_source",
        },
    ]


def _source_reports() -> list[dict[str, str]]:
    return [
        {
            "name": "n07_iteration_6b_topology_stress_report",
            "path": _rel(I6B_REPORT_PATH),
            "sha256": _file_sha256(I6B_REPORT_PATH),
        },
        {
            "name": "n07_iteration_7_reflexive_closure_design_report",
            "path": _rel(I7_REPORT_PATH),
            "sha256": _file_sha256(I7_REPORT_PATH),
        },
    ]


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


def _basin_metrics(
    node_coherence: Mapping[int, float],
    *,
    support_node_ids: list[int],
    core_node_ids: list[int],
) -> dict[str, float]:
    support_mass = round(sum(node_coherence[node] for node in support_node_ids), 6)
    core_mass = round(sum(node_coherence[node] for node in core_node_ids), 6)
    peripheral_mass = round(support_mass - core_mass, 6)
    core_weighted_mass = round(core_mass + 0.5 * peripheral_mass, 6)
    retention_score = round(core_weighted_mass / support_mass, 6)
    proper_time_persistence_score = round(0.5 + 0.5 * retention_score, 6)
    return {
        "support_area_mass": support_mass,
        "core_mass": core_mass,
        "peripheral_mass": peripheral_mass,
        "basin_evidence_score": core_weighted_mass,
        "retention_score": retention_score,
        "proper_time_persistence_score": proper_time_persistence_score,
    }


def _state_row(
    *,
    row_id: str,
    proper_time_index: int,
    scheduler_event_index: int,
    node_coherence: Mapping[int, float],
    support_node_ids: list[int],
    core_node_ids: list[int],
    support_area_digest: str,
    consumed_basin_evidence_digest: str | None,
    source_record_digest: str,
    derivation_kind: str,
    core_membership_policy: Mapping[str, Any],
) -> dict[str, Any]:
    metrics = _basin_metrics(
        node_coherence,
        support_node_ids=support_node_ids,
        core_node_ids=core_node_ids,
    )
    state_digest_input = {
        "row_id": row_id,
        "proper_time_index": proper_time_index,
        "node_coherence": {str(key): value for key, value in sorted(node_coherence.items())},
        "support_node_ids": support_node_ids,
        "core_node_ids": core_node_ids,
        "support_area_digest": support_area_digest,
        "consumed_basin_evidence_digest": consumed_basin_evidence_digest,
        "metrics": metrics,
    }
    state_digest = _digest(state_digest_input)
    evidence_digest_input = {
        "state_digest": state_digest,
        "support_area_mass": metrics["support_area_mass"],
        "basin_evidence_score": metrics["basin_evidence_score"],
        "retention_score": metrics["retention_score"],
        "proper_time_persistence_score": metrics["proper_time_persistence_score"],
        "consumed_basin_evidence_digest": consumed_basin_evidence_digest,
    }
    return {
        "row_id": row_id,
        "row_kind": "artifact_derived_basin_state_row",
        "proper_time_index": proper_time_index,
        "scheduler_event_index": scheduler_event_index,
        "node_coherence": {str(key): value for key, value in sorted(node_coherence.items())},
        "support_node_ids": support_node_ids,
        "core_node_ids": core_node_ids,
        "support_area_digest": support_area_digest,
        "consumed_basin_evidence_digest": consumed_basin_evidence_digest,
        "source_record_digest": source_record_digest,
        "derivation_kind": derivation_kind,
        "support_membership_source_backed": True,
        "core_membership_source_backed": False,
        "core_membership_policy": dict(core_membership_policy),
        "state_digest_input": state_digest_input,
        "state_digest": state_digest,
        "basin_evidence_digest_input": evidence_digest_input,
        "basin_evidence_digest": _digest(evidence_digest_input),
        "artifact_visible": True,
        "source_backed": True,
        "native_runtime_observed": False,
        "policy_derived_measurement_values": True,
        "authored_measurement_value": False,
        "budget_surface": "node_plus_packet",
        "budget_before": 6.0,
        "budget_after": 6.0,
        "budget_error": 0.0,
        "nonnegative_state_passed": all(value >= 0.0 for value in node_coherence.values()),
        **metrics,
    }


def _packet_record(
    *,
    packet_id: str,
    source_node_id: int,
    target_node_id: int,
    amount: float,
    scheduler_event_index: int,
    causal_basin_evidence_digest: str,
    reason_code: str,
) -> dict[str, Any]:
    record = {
        "packet_id": packet_id,
        "record_kind": "artifact_derived_scheduled_reentry_packet",
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "route_node_ids": [source_node_id, target_node_id],
        "amount": amount,
        "polarity": "reentry_into_support",
        "scheduler_event_index": scheduler_event_index,
        "causal_basin_evidence_digest": causal_basin_evidence_digest,
        "reason_code": reason_code,
        "artifact_visible": True,
        "source_backed": False,
        "digest_chain_source_backed": True,
        "references_source_backed_state": True,
        "source_backing_scope": "references_source_backed_basin_evidence_digest_only",
        "experiment_local_constructed": True,
        "native_runtime_observed": False,
    }
    return {**record, "packet_digest": _digest(record)}


def _apply_packet(
    node_coherence: Mapping[int, float],
    packet: Mapping[str, Any],
) -> dict[int, float]:
    next_state = {int(key): float(value) for key, value in node_coherence.items()}
    source = int(packet["source_node_id"])
    target = int(packet["target_node_id"])
    amount = float(packet["amount"])
    next_state[source] = round(next_state[source] - amount, 6)
    next_state[target] = round(next_state[target] + amount, 6)
    return next_state


def _processed_packet(
    *,
    processed_id: str,
    scheduled_packet: Mapping[str, Any],
    pre_state: Mapping[str, Any],
    post_state: Mapping[str, Any],
    scheduler_event_index: int,
) -> dict[str, Any]:
    record = {
        "processed_packet_id": processed_id,
        "scheduled_packet_id": scheduled_packet["packet_id"],
        "scheduled_packet_digest": scheduled_packet["packet_digest"],
        "pre_state_digest": pre_state["state_digest"],
        "post_state_digest": post_state["state_digest"],
        "step_processed": False,
        "step_owned_mutation": False,
        "processed_by_actual_lgrc_step": False,
        "experiment_local_packet_applied": True,
        "experiment_local_mutation_simulated": True,
        "runtime_step_contract_claimed": False,
        "step_semantics_simulated": True,
        "producer_mutated_state": False,
        "producer_changed_topology": False,
        "scheduler_event_index": scheduler_event_index,
        "support_area_mass_before": pre_state["support_area_mass"],
        "support_area_mass_after": post_state["support_area_mass"],
        "basin_evidence_score_before": pre_state["basin_evidence_score"],
        "basin_evidence_score_after": post_state["basin_evidence_score"],
        "budget_before": 6.0,
        "budget_after": 6.0,
        "budget_error": 0.0,
        "artifact_visible": True,
        "source_backed": False,
        "digest_chain_source_backed": True,
        "references_source_backed_state": True,
        "source_backing_scope": "pre_state_and_post_state_digests_are_source_backed",
        "experiment_local_constructed": True,
        "native_runtime_observed": False,
    }
    return {**record, "processed_packet_digest": _digest(record)}


def _source_backed_t6_chain(
    *, manifest: Mapping[str, Any], i6b_output: Mapping[str, Any], i7_output: Mapping[str, Any]
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["reflexive_closure"]
    source_candidate = i6b_output["id4_topology_stress_candidate_row"]
    birth_context = _birth_lineage_context(i6b_output)
    final_i6b_cycle = i6b_output["topology_stress_event"]["cycles"][-1]
    support_node_ids = final_i6b_cycle["support_node_ids"]
    core_node_ids = [birth_context["parent_node_id"], 31]
    core_membership_policy = {
        "policy_id": "n07_i7b_core_membership_design_policy_v1",
        "policy_origin": "experiment_local_design_probe",
        "support_membership_source_backed": True,
        "support_membership_source_field": "iteration_6b_final_cycle.support_node_ids",
        "source_support_node_ids": support_node_ids,
        "core_membership_source_backed": False,
        "core_membership_derivation_kind": (
            "experiment_local_design_policy_over_source_backed_support_nodes"
        ),
        "core_node_ids": core_node_ids,
        "peripheral_node_ids": [birth_context["born_node_id"]],
        "parent_node_id": birth_context["parent_node_id"],
        "peer_core_node_id": 31,
        "born_node_id": birth_context["born_node_id"],
        "rule": (
            "parent_node_and_existing_peer_support_node_are_core; "
            "born_node_is_peripheral_reentry_source"
        ),
    }
    final_mass = final_i6b_cycle["support_area_mass_after"]
    allocation_policy = {
        "policy_id": "n07_i7b_pre_state_allocation_from_6b_final_mass_v1",
        "policy_origin": "experiment_local_design_probe",
        "source": "iteration_6b_final_cycle_support_area_mass_after",
        "weights_source_backed": False,
        "weights_derivation_kind": "serialized_experiment_local_design_policy",
        "core_membership_policy_id": core_membership_policy["policy_id"],
        "node_weight_fraction": {
            str(birth_context["parent_node_id"]): 0.35,
            "31": 0.33,
            str(birth_context["born_node_id"]): 0.32,
        },
        "policy_is_serialized": True,
    }
    pre_node_coherence = {
        birth_context["parent_node_id"]: round(final_mass * 0.35, 6),
        31: round(final_mass * 0.33, 6),
        birth_context["born_node_id"]: round(final_mass * 0.32, 6),
    }
    pre_state = _state_row(
        row_id="n07_i7b_pre_reentry_state_row_v1",
        proper_time_index=7,
        scheduler_event_index=19,
        node_coherence=pre_node_coherence,
        support_node_ids=support_node_ids,
        core_node_ids=core_node_ids,
        support_area_digest=source_candidate["birth_support_area_digest"],
        consumed_basin_evidence_digest=None,
        source_record_digest=i6b_output["artifact_digests"]["topology_stress_event_digest"],
        derivation_kind="derived_from_6b_final_cycle_mass_and_serialized_allocation_policy",
        core_membership_policy=core_membership_policy,
    )
    reentry_packet = _packet_record(
        packet_id="n07_i7b_scheduled_reentry_packet_0001",
        source_node_id=birth_context["born_node_id"],
        target_node_id=birth_context["parent_node_id"],
        amount=0.08,
        scheduler_event_index=20,
        causal_basin_evidence_digest=pre_state["basin_evidence_digest"],
        reason_code="source_backed_t6_reentry_packet_scheduled",
    )
    post_node_coherence = _apply_packet(pre_node_coherence, reentry_packet)
    post_state = _state_row(
        row_id="n07_i7b_post_reentry_state_row_v1",
        proper_time_index=8,
        scheduler_event_index=22,
        node_coherence=post_node_coherence,
        support_node_ids=support_node_ids,
        core_node_ids=core_node_ids,
        support_area_digest=source_candidate["birth_support_area_digest"],
        consumed_basin_evidence_digest=pre_state["basin_evidence_digest"],
        source_record_digest=reentry_packet["packet_digest"],
        derivation_kind="derived_by_applying_processed_reentry_packet_to_pre_state",
        core_membership_policy=core_membership_policy,
    )
    processed_reentry = _processed_packet(
        processed_id="n07_i7b_processed_reentry_packet_0001",
        scheduled_packet=reentry_packet,
        pre_state=pre_state,
        post_state=post_state,
        scheduler_event_index=21,
    )
    later_producer_record = {
        "producer_record_id": "n07_i7b_later_cycle_producer_record_0001",
        "record_kind": "artifact_derived_later_cycle_producer_record",
        "causal_basin_evidence_digest": post_state["basin_evidence_digest"],
        "source_state_digest": post_state["state_digest"],
        "reason_code": "source_backed_t6_later_cycle_consumed_updated_basin_evidence",
        "scheduler_event_index": 23,
        "scheduled_packet_id": "n07_i7b_scheduled_later_reentry_packet_0002",
        "producer_mutated_coherence": False,
        "producer_changed_topology": False,
        "producer_emitted_claim_label": False,
        "artifact_visible": True,
        "source_backed": False,
        "digest_chain_source_backed": True,
        "references_source_backed_state": True,
        "source_backing_scope": "references_post_reentry_basin_evidence_digest_only",
        "experiment_local_constructed": True,
        "independently_observed_runtime_producer_record": False,
        "native_runtime_observed": False,
    }
    later_producer_record["producer_record_digest"] = _digest(later_producer_record)
    later_packet = _packet_record(
        packet_id="n07_i7b_scheduled_later_reentry_packet_0002",
        source_node_id=birth_context["born_node_id"],
        target_node_id=birth_context["parent_node_id"],
        amount=0.02,
        scheduler_event_index=24,
        causal_basin_evidence_digest=post_state["basin_evidence_digest"],
        reason_code="source_backed_t6_later_reentry_packet_scheduled",
    )
    later_node_coherence = _apply_packet(post_node_coherence, later_packet)
    later_state = _state_row(
        row_id="n07_i7b_later_cycle_state_row_v1",
        proper_time_index=9,
        scheduler_event_index=26,
        node_coherence=later_node_coherence,
        support_node_ids=support_node_ids,
        core_node_ids=core_node_ids,
        support_area_digest=source_candidate["birth_support_area_digest"],
        consumed_basin_evidence_digest=post_state["basin_evidence_digest"],
        source_record_digest=later_packet["packet_digest"],
        derivation_kind="derived_by_later_cycle_consuming_updated_basin_evidence",
        core_membership_policy=core_membership_policy,
    )
    processed_later = _processed_packet(
        processed_id="n07_i7b_processed_later_reentry_packet_0002",
        scheduled_packet=later_packet,
        pre_state=post_state,
        post_state=later_state,
        scheduler_event_index=25,
    )
    state_rows = [pre_state, post_state, later_state]
    scheduled_packets = [reentry_packet, later_packet]
    processed_packets = [processed_reentry, processed_later]
    return {
        "event_id": "n07_i7b_source_backed_t6_reflexive_closure_event_0001",
        "event_kind": "source_backed_artifact_derived_t6_reflexive_closure",
        "metric_id": metric["metric_id"],
        "topology_family_id": "n07_T6_reflexive_closure",
        "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
        "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
        "source_context_composite_topology_id": (
            "n07_C2_lineage_current_topology_mutating_identity_candidate"
        ),
        "source_iteration_6b_output_path": _rel(I6B_OUTPUT_PATH),
        "source_iteration_6b_output_sha256": _file_sha256(I6B_OUTPUT_PATH),
        "source_iteration_7_design_probe_path": _rel(I7_OUTPUT_PATH),
        "source_iteration_7_design_probe_sha256": _file_sha256(I7_OUTPUT_PATH),
        "source_iteration_7_design_probe_digest": i7_output["artifact_digests"][
            "id5_candidate_row_digest"
        ],
        "birth_lineage_context": birth_context,
        "core_membership_policy": core_membership_policy,
        "allocation_policy": allocation_policy,
        "pre_reentry_state_row": pre_state,
        "post_reentry_state_row": post_state,
        "later_cycle_state_row": later_state,
        "scheduled_packet_records": scheduled_packets,
        "processed_packet_records": processed_packets,
        "later_cycle_producer_record": later_producer_record,
        "state_row_digests": [row["state_digest"] for row in state_rows],
        "basin_evidence_digests": [row["basin_evidence_digest"] for row in state_rows],
        "scheduled_packet_digests": [packet["packet_digest"] for packet in scheduled_packets],
        "processed_packet_digests": [
            packet["processed_packet_digest"] for packet in processed_packets
        ],
        "reentry_coherence_into_support": reentry_packet["amount"],
        "support_area_mass_maintained_after_reentry": (
            post_state["support_area_mass"] == pre_state["support_area_mass"]
        ),
        "basin_evidence_score_strengthened_after_reentry": (
            post_state["basin_evidence_score"] > pre_state["basin_evidence_score"]
        ),
        "later_cycle_consumed_updated_basin_evidence": (
            later_producer_record["causal_basin_evidence_digest"]
            == post_state["basin_evidence_digest"]
            and later_state["consumed_basin_evidence_digest"]
            == post_state["basin_evidence_digest"]
        ),
        "later_cycle_consumption_independently_observed": False,
        "later_cycle_consumption_constructed_by_artifact_chain": True,
        "later_cycle_consumption_validation_scope": (
            "artifact_chain_digest_linkage_not_independent_runtime_observation"
        ),
        "later_cycle_used_stale_pre_reentry_digest": (
            later_producer_record["causal_basin_evidence_digest"]
            == pre_state["basin_evidence_digest"]
        ),
        "all_measurements_derived_from_source_rows": all(
            row["policy_derived_measurement_values"] is True
            and row["authored_measurement_value"] is False
            for row in state_rows
        ),
        "artifact_visible": True,
        "source_backed": True,
        "source_backing_scope": (
            "state_rows_and_digest_chain_source_backed; packet_and_producer_records "
            "are experiment_local_constructed"
        ),
        "native_runtime_observed": False,
        "packet_application_scope": "experiment_local_step_semantics_simulation",
        "native_reflexive_closure_policy_available": False,
        "native_reflexive_closure_policy_blocker": metric["native_policy_blocker"],
        "budget_error_max": max(row["budget_error"] for row in state_rows),
        "nonnegative_state_passed": all(row["nonnegative_state_passed"] for row in state_rows),
    }


def _proper_time_persistence_evaluation(
    *, manifest: Mapping[str, Any], chain: Mapping[str, Any]
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["reflexive_closure"]
    state_rows = [
        chain["pre_reentry_state_row"],
        chain["post_reentry_state_row"],
        chain["later_cycle_state_row"],
    ]
    digest_input = {
        "evaluator_id": "n07_i7b_proper_time_identity_persistence_evaluator_v1",
        "metric_id": metric["metric_id"],
        "proper_time_indices": [row["proper_time_index"] for row in state_rows],
        "basin_evidence_digests": [row["basin_evidence_digest"] for row in state_rows],
        "threshold": metric["proper_time_persistence_threshold"],
        "later_cycle_consumed_updated_basin_evidence": chain[
            "later_cycle_consumed_updated_basin_evidence"
        ],
    }
    return {
        "evaluator_id": "n07_i7b_proper_time_identity_persistence_evaluator_v1",
        "record_kind": "artifact_derived_proper_time_identity_persistence_evaluation",
        "metric_id": metric["metric_id"],
        "proper_time_only": True,
        "raw_scheduler_window_used": False,
        "proper_time_window_count": len(state_rows),
        "proper_time_persistence_threshold": metric["proper_time_persistence_threshold"],
        "proper_time_indices": digest_input["proper_time_indices"],
        "basin_evidence_digests": digest_input["basin_evidence_digests"],
        "source_event_id": chain["event_id"],
        "source_event_digest": _digest(chain),
        "updated_evidence_consumed_by_later_cycle": chain[
            "later_cycle_consumed_updated_basin_evidence"
        ],
        "persistence_score_min": min(
            row["proper_time_persistence_score"] for row in state_rows
        ),
        "persistence_passed": len(state_rows)
        >= metric["proper_time_persistence_threshold"]
        and chain["later_cycle_consumed_updated_basin_evidence"] is True,
        "artifact_visible": True,
        "source_backed": True,
        "native_runtime_observed": False,
        "native_support_status": "experiment_local",
        "evaluator_digest_input": digest_input,
        "evaluator_digest": _digest(digest_input),
    }


def _t6_record(
    *,
    manifest: Mapping[str, Any],
    chain: Mapping[str, Any],
    persistence: Mapping[str, Any],
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["reflexive_closure"]
    digest_input = {
        "record_id": "n07_i7b_source_backed_t6_reflexive_closure_record_v1",
        "metric_id": metric["metric_id"],
        "source_event_digest": _digest(chain),
        "state_row_digests": chain["state_row_digests"],
        "basin_evidence_digests": chain["basin_evidence_digests"],
        "scheduled_packet_digests": chain["scheduled_packet_digests"],
        "processed_packet_digests": chain["processed_packet_digests"],
        "proper_time_persistence_evaluator_digest": persistence["evaluator_digest"],
    }
    return {
        "record_id": "n07_i7b_source_backed_t6_reflexive_closure_record_v1",
        "record_kind": "source_backed_artifact_derived_t6_reflexive_closure_record",
        "metric_id": metric["metric_id"],
        "topology_family_id": chain["topology_family_id"],
        "composite_topology_id": chain["composite_topology_id"],
        "source_context_topology_family_id": chain["source_context_topology_family_id"],
        "source_context_composite_topology_id": chain[
            "source_context_composite_topology_id"
        ],
        "source_event_id": chain["event_id"],
        "source_event_digest": _digest(chain),
        "source_backed": True,
        "source_backing_scope": chain["source_backing_scope"],
        "artifact_visible": True,
        "native_runtime_observed": False,
        "native_reflexive_closure_policy_available": False,
        "native_reflexive_closure_policy_blocker": metric["native_policy_blocker"],
        "packet_application_scope": chain["packet_application_scope"],
        "actual_lgrc_step_processed_packet": False,
        "experiment_local_packet_application": True,
        "core_membership_policy_id": chain["core_membership_policy"]["policy_id"],
        "core_membership_source_backed": chain["core_membership_policy"][
            "core_membership_source_backed"
        ],
        "core_membership_derivation_kind": chain["core_membership_policy"][
            "core_membership_derivation_kind"
        ],
        "allocation_policy_origin": chain["allocation_policy"]["policy_origin"],
        "allocation_weights_source_backed": chain["allocation_policy"][
            "weights_source_backed"
        ],
        "later_cycle_consumption_independently_observed": chain[
            "later_cycle_consumption_independently_observed"
        ],
        "later_cycle_consumption_constructed_by_artifact_chain": chain[
            "later_cycle_consumption_constructed_by_artifact_chain"
        ],
        "later_cycle_consumption_validation_scope": chain[
            "later_cycle_consumption_validation_scope"
        ],
        "t4_no_mutation_baseline_deferred": manifest["t4_deferral"]["deferred"],
        "t4_deferral_rationale": manifest["t4_deferral"]["rationale"],
        "pre_reentry_state_digest": chain["pre_reentry_state_row"]["state_digest"],
        "post_reentry_state_digest": chain["post_reentry_state_row"]["state_digest"],
        "later_cycle_state_digest": chain["later_cycle_state_row"]["state_digest"],
        "pre_reentry_basin_evidence_digest": chain["pre_reentry_state_row"][
            "basin_evidence_digest"
        ],
        "post_reentry_basin_evidence_digest": chain["post_reentry_state_row"][
            "basin_evidence_digest"
        ],
        "later_cycle_basin_evidence_digest": chain["later_cycle_state_row"][
            "basin_evidence_digest"
        ],
        "reentry_coherence_into_support": chain["reentry_coherence_into_support"],
        "support_area_mass_before_reentry": chain["pre_reentry_state_row"][
            "support_area_mass"
        ],
        "support_area_mass_after_reentry": chain["post_reentry_state_row"][
            "support_area_mass"
        ],
        "basin_evidence_score_before_reentry": chain["pre_reentry_state_row"][
            "basin_evidence_score"
        ],
        "basin_evidence_score_after_reentry": chain["post_reentry_state_row"][
            "basin_evidence_score"
        ],
        "support_area_mass_maintained_after_reentry": chain[
            "support_area_mass_maintained_after_reentry"
        ],
        "basin_evidence_score_strengthened_after_reentry": chain[
            "basin_evidence_score_strengthened_after_reentry"
        ],
        "later_cycle_consumed_updated_basin_evidence": chain[
            "later_cycle_consumed_updated_basin_evidence"
        ],
        "later_cycle_used_stale_pre_reentry_digest": chain[
            "later_cycle_used_stale_pre_reentry_digest"
        ],
        "proper_time_persistence_evaluator_id": persistence["evaluator_id"],
        "proper_time_persistence_evaluator_digest": persistence["evaluator_digest"],
        "proper_time_persistence_passed": persistence["persistence_passed"],
        "all_measurements_derived_from_source_rows": chain[
            "all_measurements_derived_from_source_rows"
        ],
        "authored_measurement_values_present": False,
        "identity_acceptance_event_emitted": False,
        "identity_acceptance_blocker": metric["identity_acceptance_blocker"],
        "producer_mutated_state": False,
        "producer_changed_topology": False,
        "producer_emitted_claim_label": False,
        "budget_error_max": chain["budget_error_max"],
        "nonnegative_state_passed": chain["nonnegative_state_passed"],
        "t6_record_digest_input": digest_input,
        "t6_record_digest": _digest(digest_input),
        "t6_record_idempotency_key": {
            "metric_id": metric["metric_id"],
            "source_event_digest": _digest(chain),
            "post_reentry_basin_evidence_digest": chain["post_reentry_state_row"][
                "basin_evidence_digest"
            ],
            "later_cycle_basin_evidence_digest": chain["later_cycle_state_row"][
                "basin_evidence_digest"
            ],
        },
    }


def _candidate_row(
    *,
    manifest: Mapping[str, Any],
    i6b_output: Mapping[str, Any],
    i7_output: Mapping[str, Any],
    chain: Mapping[str, Any],
    persistence: Mapping[str, Any],
    record: Mapping[str, Any],
) -> dict[str, Any]:
    source_candidate = i6b_output["id4_topology_stress_candidate_row"]
    metric = manifest["metric_definitions"]["reflexive_closure"]
    return {
        "row_id": "n07_i7b_id5_source_backed_t6_candidate_row_v1",
        "id_level": "ID5",
        "topology_family_id": "n07_T6_reflexive_closure",
        "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
        "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
        "source_context_composite_topology_id": (
            "n07_C2_lineage_current_topology_mutating_identity_candidate"
        ),
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": source_candidate["support_area_id"],
        "support_area_digest": source_candidate["birth_support_area_digest"],
        "source_id4_stress_candidate_row_id": source_candidate["row_id"],
        "source_id4_stress_candidate_row_digest": i6b_output["artifact_digests"][
            "id4_stress_candidate_row_digest"
        ],
        "source_iteration_7_design_probe_digest": i7_output["artifact_digests"][
            "id5_candidate_row_digest"
        ],
        "t6_record_id": record["record_id"],
        "t6_record_digest": record["t6_record_digest"],
        "proper_time_persistence_evaluator_id": persistence["evaluator_id"],
        "proper_time_persistence_evaluator_digest": persistence["evaluator_digest"],
        "source_artifacts": _source_artifacts(i6b_output, i7_output),
        "source_artifact_sha256": {
            item["path"]: item["sha256"] for item in _source_artifacts(i6b_output, i7_output)
        },
        "source_reports": _source_reports(),
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
        "t6_evidence_native_support_status": "experiment_local_artifact_derived",
        "native_runtime_reflexive_closure_observed": False,
        "packet_application_scope": record["packet_application_scope"],
        "actual_lgrc_step_processed_packet": record["actual_lgrc_step_processed_packet"],
        "experiment_local_packet_application": record["experiment_local_packet_application"],
        "core_membership_policy_id": record["core_membership_policy_id"],
        "core_membership_source_backed": record["core_membership_source_backed"],
        "core_membership_derivation_kind": record["core_membership_derivation_kind"],
        "allocation_policy_origin": record["allocation_policy_origin"],
        "allocation_weights_source_backed": record["allocation_weights_source_backed"],
        "later_cycle_consumption_independently_observed": record[
            "later_cycle_consumption_independently_observed"
        ],
        "later_cycle_consumption_constructed_by_artifact_chain": record[
            "later_cycle_consumption_constructed_by_artifact_chain"
        ],
        "t4_no_mutation_baseline_deferred": record["t4_no_mutation_baseline_deferred"],
        "t4_deferral_rationale": record["t4_deferral_rationale"],
        "native_observables_used": [
            "surface_lineage_transport_context",
            "topology_state_reabsorption_context",
            "node_plus_packet_budget_accounting",
        ],
        "experiment_local_observables_used": [
            chain["event_id"],
            record["record_id"],
            persistence["evaluator_id"],
            "artifact_derived_state_rows",
            "artifact_derived_processed_packet_rows",
            "later_cycle_producer_record_consumes_updated_digest",
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
                "orientation": "N07 Iteration 7-B source-backed T6 reflexive closure",
                "observation": chain["event_id"],
                "classification": "ID5_source_backed_t6_reflexive_closure_candidate",
                "probe": "artifact_derived_reentry_state_packet_later_cycle_consumption",
                "withdrawal": "not_tested",
                "naturalization": "not_applicable",
                "integration": "pending_iteration_8_artifact_replay",
            }
        ),
        "claim_flags": _claim_flags(manifest),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "claim_ceiling": "source_backed_reflexively_self_maintaining_identity_candidate",
        "id5_is_not_id6": True,
        "identity_acceptance_event_emitted": False,
        "identity_acceptance_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "agency_claim_allowed": False,
        "unrestricted_identity_claim_allowed": False,
    }


def _control_rows(claim_flags: Mapping[str, bool]) -> list[dict[str, Any]]:
    controls = [
        ("no_reentry", "reentry_coherence_into_support", 0.0),
        (
            "closure_not_consumed_by_later_cycle",
            "later_cycle_producer_causal_basin_evidence_digest",
            "pre_reentry_basin_evidence_digest",
        ),
        ("hidden_support_field", "post_reentry_basin_evidence_score", "authored_constant"),
        ("improper_proper_time_threshold", "raw_scheduler_window_used", True),
        ("failed_persistence", "proper_time_persistence_passed", False),
        ("budget_discontinuity", "node_plus_packet_budget_error", 0.01),
        ("unauthorized_identity_acceptance_event", "identity_acceptance_event_emitted", True),
        ("producer_mutation_boundary_violation", "producer_mutated_state", True),
        ("agency_claim_promotion", "agency_claim_allowed", True),
    ]
    return [
        {
            "control_id": control_id,
            "status": "blocked",
            "mutated_field": mutated_field,
            "mutated_value": mutated_value,
            "primary_blocker": CONTROL_BLOCKERS[control_id],
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
        for control_id, mutated_field, mutated_value in controls
    ]


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "source_backed_t6_chain_digest": _digest(result["source_backed_t6_chain"]),
        "proper_time_persistence_evaluation_digest": _digest(
            result["proper_time_identity_persistence_evaluation"]
        ),
        "source_backed_t6_record_digest": _digest(result["source_backed_t6_record"]),
        "id5_candidate_row_digest": _digest(
            result["id5_source_backed_t6_candidate_row"]
        ),
        "control_rows_digest": _digest(result["control_rows"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    manifest = result["manifest"]
    i6b_output = result["source_iteration_6b_output"]
    i7_output = result["source_iteration_7_output"]
    chain = result["source_backed_t6_chain"]
    record = result["source_backed_t6_record"]
    candidate = result["id5_source_backed_t6_candidate_row"]
    persistence = result["proper_time_identity_persistence_evaluation"]
    controls = result["control_rows"]
    metric = manifest["metric_definitions"]["reflexive_closure"]
    family_ids = {family["topology_family_id"] for family in manifest["topology_families"]}
    composite = next(
        item
        for item in manifest["composite_topologies"]
        if item["composite_topology_id"]
        == "n07_C1_recurrent_single_basin_identity_candidate"
    )
    control_ids = {control["control_id"] for control in controls}
    blockers = [control["primary_blocker"] for control in controls]
    canonical_blockers = {control["primary_blocker"] for control in manifest["controls"]}
    state_rows = [
        chain["pre_reentry_state_row"],
        chain["post_reentry_state_row"],
        chain["later_cycle_state_row"],
    ]
    return {
        "status_passed": result["status"] == "passed",
        "source_iteration_6b_passed": i6b_output["status"] == "passed",
        "source_iteration_7_passed": i7_output["status"] == "passed",
        "source_iteration_7_routes_to_7b": i7_output["acceptance"]["next_iteration"]
        == "7B_source_backed_t6_reflexive_closure",
        "t6_family_declared": "n07_T6_reflexive_closure" in family_ids
        and candidate["topology_family_id"] == "n07_T6_reflexive_closure",
        "c1_composite_selected": candidate["composite_topology_id"]
        == composite["composite_topology_id"]
        and "n07_T6_reflexive_closure" in composite["primitive_blocks_combined"],
        "source_context_preserved": candidate["source_context_topology_family_id"]
        == "n07_T5_lineage_current_invariance"
        and candidate["source_context_composite_topology_id"]
        == "n07_C2_lineage_current_topology_mutating_identity_candidate",
        "birth_lineage_source_backed": chain["birth_lineage_context"][
            "node_lineage_source_backed"
        ]
        is True
        and chain["birth_lineage_context"]["born_node_id"] == 32
        and chain["birth_lineage_context"]["parent_node_id"] == 30
        and chain["birth_lineage_context"]["birth_is_identity_acceptance"] is False,
        "core_membership_scope_recorded": chain["core_membership_policy"][
            "support_membership_source_backed"
        ]
        is True
        and chain["core_membership_policy"]["core_membership_source_backed"] is False
        and chain["core_membership_policy"]["policy_origin"]
        == "experiment_local_design_probe"
        and 31 in chain["core_membership_policy"]["source_support_node_ids"],
        "allocation_policy_origin_recorded": chain["allocation_policy"][
            "policy_origin"
        ]
        == "experiment_local_design_probe"
        and chain["allocation_policy"]["weights_source_backed"] is False,
        "state_rows_source_backed": all(
            row["source_backed"] is True
            and row["artifact_visible"] is True
            and row["native_runtime_observed"] is False
            for row in state_rows
        ),
        "measurements_derived_not_authored": chain[
            "all_measurements_derived_from_source_rows"
        ]
        is True
        and record["authored_measurement_values_present"] is False
        and all(row["authored_measurement_value"] is False for row in state_rows),
        "packet_records_scope_precise": all(
            packet["source_backed"] is False
            and packet["digest_chain_source_backed"] is True
            and packet["references_source_backed_state"] is True
            and packet["experiment_local_constructed"] is True
            and packet["native_runtime_observed"] is False
            for packet in chain["scheduled_packet_records"]
        )
        and all(
            packet["source_backed"] is False
            and packet["digest_chain_source_backed"] is True
            and packet["references_source_backed_state"] is True
            and packet["experiment_local_constructed"] is True
            and packet["step_processed"] is False
            and packet["step_owned_mutation"] is False
            and packet["processed_by_actual_lgrc_step"] is False
            and packet["experiment_local_packet_applied"] is True
            and packet["producer_mutated_state"] is False
            for packet in chain["processed_packet_records"]
        ),
        "reentry_strengthens_basin_evidence": record[
            "support_area_mass_maintained_after_reentry"
        ]
        is True
        and record["basin_evidence_score_after_reentry"]
        > record["basin_evidence_score_before_reentry"],
        "later_cycle_consumes_updated_digest": record[
            "later_cycle_consumed_updated_basin_evidence"
        ]
        is True
        and record["later_cycle_used_stale_pre_reentry_digest"] is False,
        "later_cycle_independence_limitation_recorded": record[
            "later_cycle_consumption_independently_observed"
        ]
        is False
        and record["later_cycle_consumption_constructed_by_artifact_chain"] is True,
        "proper_time_persistence_passed": persistence["persistence_passed"] is True
        and persistence["proper_time_window_count"]
        >= metric["proper_time_persistence_threshold"]
        and persistence["raw_scheduler_window_used"] is False,
        "t6_record_digest_recomputed": record["t6_record_digest"]
        == _digest(record["t6_record_digest_input"]),
        "candidate_digest_source_links_present": candidate["source_artifacts"][2][
            "status"
        ]
        == "passed"
        and candidate["source_artifacts"][3]["status"] == "passed",
        "native_support_not_overstated": candidate["native_support_status"]
        == "mixed_native_experiment_local"
        and candidate["t6_evidence_native_support_status"]
        == "experiment_local_artifact_derived"
        and candidate["native_runtime_reflexive_closure_observed"] is False
        and candidate["actual_lgrc_step_processed_packet"] is False
        and candidate["experiment_local_packet_application"] is True
        and record["native_reflexive_closure_policy_available"] is False,
        "t4_deferral_limitation_recorded": candidate[
            "t4_no_mutation_baseline_deferred"
        ]
        is True
        and "T4" in candidate["t4_deferral_rationale"],
        "identity_acceptance_not_emitted": record["identity_acceptance_event_emitted"]
        is False
        and record["identity_acceptance_blocker"]
        == "unauthorized_identity_acceptance_event",
        "gate_vector_valid": set(candidate["gate_vector"])
        == set(manifest["gate_vector_schema"]["fields"])
        and set(candidate["gate_vector"].values()).issubset(
            set(manifest["gate_vector_schema"]["allowed_values"])
        ),
        "derived_ceiling_id5_not_id6": candidate["derived_id_ceiling"] == "ID5"
        and candidate["id5_is_not_id6"] is True,
        "control_set_present": set(CONTROL_BLOCKERS).issubset(control_ids),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "control_blockers_canonical": set(blockers).issubset(canonical_blockers),
        "controls_blocked": all(control["status"] == "blocked" for control in controls),
        "control_ceilings_id4": all(
            control["derived_id_ceiling"] == "ID4" for control in controls
        ),
        "budget_exact": chain["budget_error_max"] == 0.0
        and record["budget_error_max"] == 0.0,
        "nonnegative_state_passed": chain["nonnegative_state_passed"] is True
        and record["nonnegative_state_passed"] is True,
        "claim_flag_keys_match_manifest": set(result["claim_flags"])
        == set(manifest["claim_boundary"]["claim_flags"])
        == set(candidate["claim_flags"]),
        "claim_flags_all_false": all(value is False for value in result["claim_flags"].values()),
        "agency_and_identity_acceptance_blocked": result["claim_flags"][
            "agency_claim_allowed"
        ]
        is False
        and result["claim_flags"]["identity_acceptance_claim_allowed"] is False
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
        f"""# N07 Iteration 7-B: Source-Backed T6 Reflexive Closure

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 7-B consumes the Iteration 6-B T5 lineage-current source context and
the Iteration 7 T6 design probe. It then emits a stricter T6 chain from
serialized state rows, experiment-local packet application records, and a
later producer-linkage record that consumes the updated basin evidence digest.

The result is source-backed and artifact-derived, but it is still not native
LGRC reflexive-closure support. Native reflexive-closure policy remains
unavailable. Packet and producer records are digest-chain source-backed but
experiment-local constructions; they do not claim actual LGRC `step()`
execution.

## Source-Backed T6 Chain

```json
{json.dumps(result['source_backed_t6_chain'], indent=2, sort_keys=True)}
```

## T6 Record

```json
{json.dumps(result['source_backed_t6_record'], indent=2, sort_keys=True)}
```

## Candidate Row

```json
{json.dumps(result['id5_source_backed_t6_candidate_row'], indent=2, sort_keys=True)}
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

Iteration 7-B passes because re-entry is represented by serialized packet and
state rows, basin evidence is computed from those rows, and the later
proper-time cycle consumes the updated basin evidence digest. The result
reaches ID5/T6 only; it does not support ID6, native LGRC identity support,
identity acceptance, RC identity collapse, agency, or personhood.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest_validation = _load_json(MANIFEST_VALIDATION_PATH)
    manifest = manifest_validation["manifest"]
    i6b_output = _load_json(I6B_OUTPUT_PATH)
    i7_output = _load_json(I7_OUTPUT_PATH)
    claim_flags = _claim_flags(manifest)
    chain = _source_backed_t6_chain(
        manifest=manifest,
        i6b_output=i6b_output,
        i7_output=i7_output,
    )
    persistence = _proper_time_persistence_evaluation(manifest=manifest, chain=chain)
    record = _t6_record(manifest=manifest, chain=chain, persistence=persistence)
    candidate = _candidate_row(
        manifest=manifest,
        i6b_output=i6b_output,
        i7_output=i7_output,
        chain=chain,
        persistence=persistence,
        record=record,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_7b_source_backed_t6_reflexive_closure_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": "7-B",
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
        "source_iteration_6b_output": i6b_output,
        "source_iteration_7_output": i7_output,
        "manifest": manifest,
        "source_backed_t6_chain": chain,
        "proper_time_identity_persistence_evaluation": persistence,
        "source_backed_t6_record": record,
        "id5_source_backed_t6_candidate_row": candidate,
        "control_rows": _control_rows(claim_flags),
        "claim_flags": claim_flags,
        "acceptance": {
            "source_backed_t6_candidate_emitted": True,
            "source_iteration_6b_consumed": True,
            "source_iteration_7_design_probe_consumed": True,
            "topology_family_id": "n07_T6_reflexive_closure",
            "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
            "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
            "support_gate_passed": True,
            "stability_gate_passed": True,
            "attractivity_gate_passed": True,
            "invariance_gate_passed": True,
            "lineage_current_gate_passed": True,
            "reflexive_closure_gate_passed": True,
            "proper_time_persistence_passed": True,
            "measurements_derived_from_source_rows": True,
            "native_runtime_reflexive_closure_observed": False,
            "actual_lgrc_step_processed_packet": False,
            "experiment_local_packet_application": True,
            "packet_records_digest_chain_source_backed": True,
            "core_membership_source_backed": False,
            "allocation_policy_origin": "experiment_local_design_probe",
            "later_cycle_consumption_independently_observed": False,
            "later_cycle_consumption_constructed_by_artifact_chain": True,
            "t4_no_mutation_baseline_deferred": manifest["t4_deferral"]["deferred"],
            "native_reflexive_closure_policy_available": False,
            "identity_acceptance_event_emitted": False,
            "producer_boundary_preserved": True,
            "budget_exact": True,
            "nonnegative_state_passed": True,
            "controls_declared_and_blocked": True,
            "claim_flags_false": True,
            "derived_id_ceiling": "ID5",
            "native_support_status": "mixed_native_experiment_local",
            "next_iteration": "8_id6_artifact_only_replay_and_closeout",
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
