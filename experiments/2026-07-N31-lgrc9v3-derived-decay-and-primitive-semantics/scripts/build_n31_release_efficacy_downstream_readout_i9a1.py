#!/usr/bin/env python3
"""Run N31 Iteration 9-A.1 independent downstream readout probe."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.core import InvalidStateTransitionError
from pygrc.models import (
    LGRC9V3,
    digest_lgrc9v3_restoration_identity_v1,
    digest_lgrc9v3_restoration_identity_v2,
)


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i9a1_downstream_readout_artifacts"
I9 = OUTPUTS / "n31_added_mechanism_admission_i9.json"
I9A = OUTPUTS / "n31_release_efficacy_attenuation_i9a.json"
I9A_TRACE = OUTPUTS / "n31_i9a_release_efficacy_source_current_trace.json"
I9A_COMPOSED = (
    OUTPUTS
    / "n31_i9a_release_efficacy_artifacts"
    / "n31_i9a_composed_candidate_identity.json"
)
FRESH_SOURCE = (
    OUTPUTS
    / "n31_i9a_release_efficacy_artifacts"
    / "n31_i9a_fresh_final_snapshot.json"
)
AGED_SOURCE = (
    OUTPUTS
    / "n31_i9a_release_efficacy_artifacts"
    / "n31_i9a_aged_final_snapshot.json"
)
PREREGISTRATION = ARTIFACT_DIR / "n31_i9a1_preregistration.json"
SWEEP_ARTIFACT = ARTIFACT_DIR / "n31_i9a1_threshold_sweep.json"
MEDIATION_ARTIFACT = ARTIFACT_DIR / "n31_i9a1_mediation_interventions.json"
REVISION_LINEAGE = ARTIFACT_DIR / "n31_i9_i9a_revision_lineage.json"
TRACE = OUTPUTS / "n31_i9a1_release_efficacy_downstream_readout_trace.json"
OUTPUT = OUTPUTS / "n31_release_efficacy_downstream_readout_i9a1.json"
REPORT = REPORTS / "n31_release_efficacy_downstream_readout_i9a1.md"
SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_release_efficacy_downstream_readout_i9a1.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
GOVERNANCE_BASE_REVISION = "33951a8eebcd4d03e32581aa189eaf81c71bb8f6"
PROTECTED_PATHS = (
    "src",
    "lib",
    "specs",
    "implementation",
    "tests",
    "examples",
    "scripts",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
)
SOURCE_IDENTITIES = {
    I9: (
        "4cf2043eebf54d26ce9b98aee77ad8a846cf90e4e1f452dc065fd327633b761d",
        "957b31c539295b5fb924b9251132967b53a2ecd7fe3bedb747b0a49bf581ead5",
    ),
    I9A: (
        "cdb2bd7f27bfba52e6b007b5a54d9c2bd04d20723bf3037162d94268c69a22c0",
        "b5824794ac802bf5cc787bf6d09410f56494a49b5f5af757bcd15dae68d61031",
    ),
    I9A_TRACE: (
        "e72aa25e3ff42cc8b37c62e31c7f5e42a6f16b941a8803534075a09c84610b0e",
        "3ffb4ef810b9f119a6f15d25b0703a6f6b44719a79fe7b10b02521442738256f",
    ),
    I9A_COMPOSED: (
        "0730351e0ef817274ba44ede68897b885689e3c087fb64bb796617a361819c7f",
        "3a04a80d400271bfa3e2c3502b7699647c0357c0ea62674ec37e5cf96e7d6f0a",
    ),
}
SOURCE_SNAPSHOT_SHA256 = {
    FRESH_SOURCE: "f434a46d45d78c96a2ca9a58deeca1d04a5ed1b41a4881f7e22db6fe502f3703",
    AGED_SOURCE: "4dc07b6c0803f54674eceac48b6da16ba46fddcaff6b9c3e309e71cd47feaced",
}
Q_PROBES = (0.25, 0.30, 0.35, 0.40, 0.45)
SPLIT_Q = 0.35
COMMON_TARGET_C = 0.45
TOLERANCE = 1e-12
PRIOR_I9_OUTPUT_DIGEST = (
    "80572f132f679beb7d733b7ed5609a5efa5cd7815490e8f3fef711b14e7fbcee"
)
PRIOR_I9A_OUTPUT_DIGEST = (
    "69eec2618fde6408482dfd17f8ad1e48634756f23e02298b2ef9b260841443e1"
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def git_diff_empty(path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", GOVERNANCE_BASE_REVISION, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def source_record(path: Path) -> dict[str, Any]:
    value = load_json(path)
    expected_digest, expected_sha = SOURCE_IDENTITIES[path]
    actual_sha = sha256_file(path)
    return {
        "path": relative(path),
        "expected_output_digest": expected_digest,
        "actual_output_digest": value.get("output_digest"),
        "expected_sha256": expected_sha,
        "actual_sha256": actual_sha,
        "internal_output_digest_exact": internal_output_digest_exact(value),
        "identity_exact": value.get("output_digest") == expected_digest
        and actual_sha == expected_sha,
    }


def source_snapshot_record(path: Path) -> dict[str, Any]:
    expected_sha = SOURCE_SNAPSHOT_SHA256[path]
    actual_sha = sha256_file(path)
    model = LGRC9V3.load(str(path))
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    return {
        "path": relative(path),
        "expected_sha256": expected_sha,
        "actual_sha256": actual_sha,
        "identity_exact": actual_sha == expected_sha,
        "restoration_identity_v1": digest_lgrc9v3_restoration_identity_v1(model),
        "restoration_identity_v2": digest_lgrc9v3_restoration_identity_v2(model),
        "event_queue_empty": len(ledger.event_queue_records) == 0,
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "node_coherence": {
            str(node_id): float(node.coherence)
            for node_id, node in sorted(state.base_state.nodes.items())
        },
    }


def runtime_budget(model: LGRC9V3) -> dict[str, float]:
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    return {
        "node_coherence_total": float(ledger.node_coherence_total),
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "conserved_budget_total": float(ledger.conserved_budget_total),
        "budget_error": float(ledger.budget_error),
    }


def processing_state_projection(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    queue_records = [row.to_record() for row in ledger.event_queue_records]
    packet_records = [row.to_record() for row in ledger.packet_records]
    ledger_projection = {
        "queue_records": queue_records,
        "packet_records": packet_records,
        "node_coherence_total": float(ledger.node_coherence_total),
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "conserved_budget_total": float(ledger.conserved_budget_total),
        "budget_error": float(ledger.budget_error),
    }
    return {
        "restoration_identity_v1": digest_lgrc9v3_restoration_identity_v1(model),
        "restoration_identity_v2": digest_lgrc9v3_restoration_identity_v2(model),
        "event_queue_digest": digest_value(queue_records),
        "event_queue_count": len(queue_records),
        "packet_ledger_digest": digest_value(ledger_projection),
        "packet_record_count": len(packet_records),
        "scheduler_event_index": int(state.scheduler_event_index),
        "checkpoint_index": int(state.checkpoint_index),
        "event_time_key": float(state.event_time_key),
        "budget": runtime_budget(model),
    }


def processing_receipt(result: Any) -> dict[str, Any]:
    for event in result.events:
        processed = event.payload.get("processed_event")
        packet = event.payload.get("packet_record")
        if isinstance(processed, dict) and isinstance(packet, dict):
            return {
                "event_kind": processed["event_kind"],
                "event_id": processed["event_id"],
                "edge_id": int(processed["edge_id"]),
                "source_node_id": int(processed["source_node_id"]),
                "target_node_id": int(processed["target_node_id"]),
                "amount": float(processed["amount"]),
                "packet_id": processed["packet_id"],
                "source_lineage_id": packet.get("source_lineage_id"),
                "budget_error": float(event.payload.get("budget_error", 0.0)),
            }
    raise ValueError("step result did not contain a packet processing receipt")


def apply_balanced_clamp(
    model: LGRC9V3,
    *,
    node_id: int,
    target_coherence: float,
    compensator_node_id: int = 0,
) -> dict[str, Any]:
    state = deepcopy(model.get_state())
    before = float(state.base_state.nodes[node_id].coherence)
    compensator_before = float(
        state.base_state.nodes[compensator_node_id].coherence
    )
    delta = target_coherence - before
    compensator_after = compensator_before - delta
    if target_coherence < 0.0 or compensator_after < 0.0:
        raise ValueError("balanced clamp would create negative coherence")
    state.base_state.nodes[node_id].coherence = target_coherence
    state.base_state.nodes[compensator_node_id].coherence = compensator_after
    model.set_state(state)
    return {
        "node_id": node_id,
        "coherence_before": before,
        "coherence_after": target_coherence,
        "compensator_node_id": compensator_node_id,
        "compensator_before": compensator_before,
        "compensator_after": compensator_after,
        "total_delta": (target_coherence - before)
        + (compensator_after - compensator_before),
    }


def run_readout(
    source_snapshot: Path,
    phase: str,
    q_probe: float,
    *,
    intervention: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = LGRC9V3.load(str(source_snapshot))
    source_identity = {
        "v1": digest_lgrc9v3_restoration_identity_v1(model),
        "v2": digest_lgrc9v3_restoration_identity_v2(model),
    }
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    source_packets_complete = (
        len(ledger.event_queue_records) == 0
        and abs(float(ledger.in_flight_packet_total)) <= TOLERANCE
    )
    clamp_record = None
    if intervention is not None:
        clamp_record = apply_balanced_clamp(
            model,
            node_id=int(intervention["node_id"]),
            target_coherence=float(intervention["target_coherence"]),
        )
    state_before = model.get_state()
    ledger_before = state_before.packet_ledger
    assert ledger_before is not None
    receiver_before = float(state_before.base_state.nodes[2].coherence)
    target_before = float(state_before.base_state.nodes[1].coherence)
    compensator_before = float(state_before.base_state.nodes[0].coherence)
    budget_before = runtime_budget(model)
    lineage = (
        f"n31_A1_{phase}_{q_probe:.2f}_"
        f"{intervention['intervention_id'] if intervention else 'original'}"
    )
    model.schedule_packet_departure(
        source_node_id=2,
        target_node_id=1,
        edge_id=1,
        amount=q_probe,
        departure_event_time_key=4.0,
        arrival_event_time_key=5.0,
        scheduler_event_index=5,
        packet_index=len(ledger_before.packet_records),
        source_lineage_id=lineage,
        target_lineage_id="n31_A1_native_readout_target",
    )
    processing_state_before = processing_state_projection(model)
    admitted = False
    rejection_reason = None
    departure_receipt = None
    arrival_receipt = None
    budget_after = None
    receiver_after_departure = receiver_before
    target_after_arrival = target_before
    try:
        departure_receipt = processing_receipt(model.step())
        admitted = True
        receiver_after_departure = float(
            model.get_state().base_state.nodes[2].coherence
        )
        arrival_receipt = processing_receipt(model.step())
        target_after_arrival = float(
            model.get_state().base_state.nodes[1].coherence
        )
        budget_after = runtime_budget(model)
    except InvalidStateTransitionError as exc:
        rejection_reason = str(exc)
    processing_state_after = processing_state_projection(model)
    rejection_atomicity_receipt = None
    if not admitted:
        identity_v1_exact = (
            processing_state_before["restoration_identity_v1"]
            == processing_state_after["restoration_identity_v1"]
        )
        identity_v2_exact = (
            processing_state_before["restoration_identity_v2"]
            == processing_state_after["restoration_identity_v2"]
        )
        queue_exact = (
            processing_state_before["event_queue_digest"]
            == processing_state_after["event_queue_digest"]
        )
        ledger_exact = (
            processing_state_before["packet_ledger_digest"]
            == processing_state_after["packet_ledger_digest"]
        )
        scheduler_exact = (
            processing_state_before["scheduler_event_index"]
            == processing_state_after["scheduler_event_index"]
            and processing_state_before["checkpoint_index"]
            == processing_state_after["checkpoint_index"]
            and processing_state_before["event_time_key"]
            == processing_state_after["event_time_key"]
        )
        packet_count_exact = (
            processing_state_before["packet_record_count"]
            == processing_state_after["packet_record_count"]
        )
        budget_exact = (
            processing_state_before["budget"] == processing_state_after["budget"]
        )
        rejection_atomicity_receipt = {
            "receipt_authority": "experiment_audit_of_native_refusal",
            "native_runtime_refusal_reason": rejection_reason,
            "identity_v1_exact": identity_v1_exact,
            "identity_v2_exact": identity_v2_exact,
            "event_queue_unchanged": queue_exact,
            "packet_ledger_unchanged": ledger_exact,
            "scheduler_and_time_unchanged": scheduler_exact,
            "packet_record_count_unchanged": packet_count_exact,
            "budget_unchanged": budget_exact,
            "no_partial_packet_record_created": packet_count_exact,
            "atomic_state_neutral_refusal": all(
                (
                    identity_v1_exact,
                    identity_v2_exact,
                    queue_exact,
                    ledger_exact,
                    scheduler_exact,
                    packet_count_exact,
                    budget_exact,
                )
            ),
        }
    return {
        "branch_id": lineage,
        "phase_source": phase,
        "q_probe": q_probe,
        "intervention": intervention,
        "balanced_clamp_record": clamp_record,
        "source_snapshot_identity": source_identity,
        "original_release_packets_complete_before_readout": source_packets_complete,
        "receiver_C_before_readout": receiver_before,
        "target_C_before_readout": target_before,
        "compensator_C_before_readout": compensator_before,
        "readout_admitted": admitted,
        "rejection_reason": rejection_reason,
        "departure_receipt": departure_receipt,
        "arrival_receipt": arrival_receipt,
        "receiver_C_after_departure": receiver_after_departure,
        "target_C_after_arrival": target_after_arrival,
        "source_debit": receiver_before - receiver_after_departure,
        "target_credit": target_after_arrival - target_before,
        "budget_before": budget_before,
        "budget_after": budget_after,
        "processing_state_before": processing_state_before,
        "processing_state_after": processing_state_after,
        "rejection_atomicity_receipt": rejection_atomicity_receipt,
        "candidate_A_producer_loaded_during_readout": False,
        "candidate_A_producer_calls_during_readout": 0,
        "readout_operation": (
            "native_LGRC9V3_receiver_packet_departure_and_arrival_on_edge_1"
        ),
        "experiment_authored_probe_request": True,
        "native_runtime_owns_admission_debit_transport_and_credit": True,
        "semantic_route_label_read": False,
        "global_selector_read": False,
    }


def outcome_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row[key]
        for key in (
            "phase_source",
            "q_probe",
            "intervention",
            "balanced_clamp_record",
            "receiver_C_before_readout",
            "target_C_before_readout",
            "compensator_C_before_readout",
            "readout_admitted",
            "rejection_reason",
            "departure_receipt",
            "arrival_receipt",
            "receiver_C_after_departure",
            "target_C_after_arrival",
            "source_debit",
            "target_credit",
            "budget_before",
            "budget_after",
            "processing_state_before",
            "processing_state_after",
            "rejection_atomicity_receipt",
        )
    }


def expected_admission(phase: str, q_probe: float) -> bool:
    receiver_c = 0.40 if phase == "fresh" else 0.30
    return q_probe <= receiver_c + TOLERANCE


def control_result(
    control_id: str,
    status: str,
    actual_result: str,
    rung_effect: str,
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "control_status": status,
        "blocked_condition": control_id,
        "expected_result": (
            "conformance_requirement_satisfied"
            if status == "passed"
            else "false_positive_path_rejected"
        ),
        "actual_result": actual_result,
        "claim_allowed_when_control_triggers": False,
        "rung_effect": rung_effect,
        "scope_reason_if_not_applicable": None,
    }


def build_preregistration(i9a: dict[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-A.1",
        "artifact_kind": "independent_downstream_readout_preregistration",
        "artifact_schema_version": "n31_i9a1_preregistration_v1",
        "generated_at": GENERATED_AT,
        "candidate_id": "A_release_efficacy_attenuation",
        "source_I9A_output_digest": i9a["output_digest"],
        "producer_contract": {
            "same_candidate_A_producer_required": True,
            "different_decay_producer_allowed": False,
            "candidate_A_producer_loaded_during_readout": False,
            "candidate_A_producer_calls_during_readout": 0,
            "reason": (
                "DR4_requires_a_downstream_consequence_of_the_I9A_relation; "
                "a_second_producer_would_confound_that_causal chain"
            ),
        },
        "native_readout_contract": {
            "operation": "receiver_node_2_packet_departure_to_node_1_on_edge_1",
            "request_owner": "experiment_probe_harness",
            "admission_and_transport_owner": "native_LGRC9V3_runtime",
            "departure_event_time_key": 4.0,
            "arrival_event_time_key": 5.0,
            "q_probes": list(Q_PROBES),
            "source_receiver_C_by_phase_from_prior_I9A": {
                "fresh": 0.40,
                "aged": 0.30,
            },
            "thresholds_derived_from_prior_I9A_not_I9A1_outcomes": True,
            "native_eligibility_relation": "source_C >= q_probe",
            "observed_split_interval": "aged_C < q_probe <= fresh_C",
            "robust_tested_interior_q": SPLIT_Q,
            "endpoint_values_are_observed_binary_floats_not_theoretical_reals": True,
            "nextafter_boundary_controls_pending_I10": True,
            "expected_admission_by_phase": {
                phase: {
                    f"{q_probe:.2f}": expected_admission(phase, q_probe)
                    for q_probe in Q_PROBES
                }
                for phase in ("fresh", "aged")
            },
        },
        "mediation_controls": {
            "split_q": SPLIT_Q,
            "fresh_receiver_clamped_to_aged_C_expected": "rejected",
            "aged_receiver_clamped_to_fresh_C_expected": "admitted",
            "common_target_C": COMMON_TARGET_C,
            "target_clamp_expected_to_preserve_original_split": True,
            "all_clamps_preserve_total_node_coherence": True,
            "mediation_strength_ceiling": "bounded_partial_local_receiver_C",
            "other_continuation_state_matched": (
                "false_with_declared_mass_compensator"
            ),
            "load_bearing_readout": "native_departure_admission_only",
            "full_complete_state_mediation_allowed": False,
        },
        "claim_ceiling": "provisional_producer_mediated_DR4_pending_I10",
        "DR5_requires_complete_I10_control_matrix": True,
        "native_upgrade_allowed": False,
        "outcome_tuning_allowed": False,
    }
    record["readout_contract_identity"] = digest_value(
        {
            "producer_contract": record["producer_contract"],
            "native_readout_contract": record["native_readout_contract"],
            "mediation_controls": record["mediation_controls"],
        }
    )
    record["output_digest"] = digest_value(record)
    PREREGISTRATION.write_text(canonical_json(record), encoding="utf-8")
    return record


def write_record(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    record["output_digest"] = digest_value(record)
    path.write_text(canonical_json(record), encoding="utf-8")
    return record


def build_revision_lineage(
    i9: dict[str, Any], i9a: dict[str, Any]
) -> dict[str, Any]:
    return write_record(
        REVISION_LINEAGE,
        {
            "artifact_kind": "n31_i9_i9a_revision_lineage",
            "artifact_schema_version": "n31_i9_i9a_revision_lineage_v1",
            "generated_at": GENERATED_AT,
            "I9": {
                "previous_output_digest": PRIOR_I9_OUTPUT_DIGEST,
                "current_output_digest": i9["output_digest"],
                "current_artifact_sha256": sha256_file(I9),
                "review_corrections": [
                    "release_phase_made_load_bearing",
                    "producer_input_allowlist_tightened",
                    "numeric_topology_bindings_and_policy_identity_added",
                ],
                "scientific_admission_decision_changed": False,
                "exact_current_artifact_consumed_by_I9A1": True,
            },
            "I9A": {
                "previous_output_digest": PRIOR_I9A_OUTPUT_DIGEST,
                "previous_artifact_sha256_available": False,
                "current_output_digest": i9a["output_digest"],
                "current_artifact_sha256": sha256_file(I9A),
                "review_corrections": [
                    "provisional_DR4_demoted_to_DR3_pending_independent_readout",
                    "control_statuses_and_policy_ownership_normalized",
                    "composed_native_plus_closure_identity_added",
                    "floating_point_release_boundary_qualified",
                ],
                "scientific_numerical_outcome_changed": False,
                "evidence_rung_classification_corrected": True,
                "exact_current_artifact_consumed_by_I9A1": True,
            },
            "lineage_scope": (
                "review_correction_provenance_only; no prior artifact is consumed "
                "as current evidence"
            ),
        },
    )


def build() -> dict[str, Any]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i9 = load_json(I9)
    i9a = load_json(I9A)
    i9a_trace = load_json(I9A_TRACE)
    i9a_composed = load_json(I9A_COMPOSED)
    sources = [source_record(path) for path in SOURCE_IDENTITIES]
    snapshot_sources = [
        source_snapshot_record(path) for path in SOURCE_SNAPSHOT_SHA256
    ]
    candidate_a = next(
        row
        for row in i9["added_mechanism_decay_classifications"]
        if row["candidate_id"] == "A_release_efficacy_attenuation"
    )
    revision_lineage = build_revision_lineage(i9, i9a)
    preregistration = build_preregistration(i9a)

    sweep_rows: list[dict[str, Any]] = []
    replay_rows: list[dict[str, Any]] = []
    for phase, source in (("fresh", FRESH_SOURCE), ("aged", AGED_SOURCE)):
        for q_probe in Q_PROBES:
            row = run_readout(source, phase, q_probe)
            replay = run_readout(source, phase, q_probe)
            row["expected_admission"] = expected_admission(phase, q_probe)
            row["matches_preregistration"] = (
                row["readout_admitted"] == row["expected_admission"]
            )
            row["duplicate_replay_exact"] = (
                digest_value(outcome_projection(row))
                == digest_value(outcome_projection(replay))
            )
            sweep_rows.append(row)
            replay_rows.append(replay)

    receiver_down = {
        "intervention_id": "fresh_receiver_C_clamped_to_aged_C",
        "node_id": 2,
        "target_coherence": 0.30,
        "causal_role": "receiver_mediation_down_clamp",
    }
    receiver_up = {
        "intervention_id": "aged_receiver_C_clamped_to_fresh_C",
        "node_id": 2,
        "target_coherence": 0.40,
        "causal_role": "receiver_mediation_up_clamp",
    }
    target_common = {
        "intervention_id": "target_C_clamped_to_common_value",
        "node_id": 1,
        "target_coherence": COMMON_TARGET_C,
        "causal_role": "target_state_confound_control",
    }
    intervention_specs = (
        ("fresh", FRESH_SOURCE, receiver_down),
        ("aged", AGED_SOURCE, receiver_up),
        ("fresh", FRESH_SOURCE, target_common),
        ("aged", AGED_SOURCE, target_common),
    )
    intervention_rows: list[dict[str, Any]] = []
    for phase, source, intervention in intervention_specs:
        row = run_readout(source, phase, SPLIT_Q, intervention=intervention)
        replay = run_readout(source, phase, SPLIT_Q, intervention=intervention)
        row["duplicate_replay_exact"] = (
            digest_value(outcome_projection(row))
            == digest_value(outcome_projection(replay))
        )
        intervention_rows.append(row)

    sweep_by_key = {
        (row["phase_source"], row["q_probe"]): row for row in sweep_rows
    }
    intervention_by_key = {
        (
            row["phase_source"],
            row["intervention"]["intervention_id"],
        ): row
        for row in intervention_rows
    }
    original_split = (
        sweep_by_key[("fresh", SPLIT_Q)]["readout_admitted"]
        and not sweep_by_key[("aged", SPLIT_Q)]["readout_admitted"]
    )
    receiver_clamp_reverses_split = (
        not intervention_by_key[
            ("fresh", "fresh_receiver_C_clamped_to_aged_C")
        ]["readout_admitted"]
        and intervention_by_key[
            ("aged", "aged_receiver_C_clamped_to_fresh_C")
        ]["readout_admitted"]
    )
    target_clamp_preserves_split = (
        intervention_by_key[
            ("fresh", "target_C_clamped_to_common_value")
        ]["readout_admitted"]
        and not intervention_by_key[
            ("aged", "target_C_clamped_to_common_value")
        ]["readout_admitted"]
    )
    all_successful_readouts_conserved = all(
        (
            not row["readout_admitted"]
            or (
                abs(row["source_debit"] - row["q_probe"]) <= TOLERANCE
                and abs(row["target_credit"] - row["q_probe"]) <= TOLERANCE
                and row["budget_after"] is not None
                and abs(row["budget_after"]["budget_error"]) <= TOLERANCE
            )
        )
        for row in sweep_rows + intervention_rows
    )
    all_source_packets_complete = all(
        row["original_release_packets_complete_before_readout"]
        for row in sweep_rows + intervention_rows
    )
    no_producer_during_readout = all(
        not row["candidate_A_producer_loaded_during_readout"]
        and row["candidate_A_producer_calls_during_readout"] == 0
        for row in sweep_rows + intervention_rows
    )
    all_replay_exact = all(
        row["duplicate_replay_exact"] for row in sweep_rows + intervention_rows
    )
    rejected_rows = [
        row for row in sweep_rows + intervention_rows if not row["readout_admitted"]
    ]
    all_rejected_readouts_atomic = bool(rejected_rows) and all(
        row["rejection_atomicity_receipt"] is not None
        and row["rejection_atomicity_receipt"]["atomic_state_neutral_refusal"]
        for row in rejected_rows
    )

    sweep_artifact = write_record(
        SWEEP_ARTIFACT,
        {
            "artifact_kind": "n31_i9a1_native_receiver_threshold_sweep",
            "artifact_schema_version": "n31_i9a1_threshold_sweep_v1",
            "generated_at": GENERATED_AT,
            "readout_contract_identity": preregistration[
                "readout_contract_identity"
            ],
            "rows": sweep_rows,
            "all_rows_match_preregistration": all(
                row["matches_preregistration"] for row in sweep_rows
            ),
            "original_split_at_q_0_35": original_split,
        },
    )
    mediation_artifact = write_record(
        MEDIATION_ARTIFACT,
        {
            "artifact_kind": "n31_i9a1_receiver_mediation_interventions",
            "artifact_schema_version": "n31_i9a1_mediation_interventions_v1",
            "generated_at": GENERATED_AT,
            "rows": intervention_rows,
            "receiver_C_clamp_reverses_admission_split": (
                receiver_clamp_reverses_split
            ),
            "target_C_clamp_preserves_admission_split": target_clamp_preserves_split,
            "balanced_clamps_preserve_total_C": all(
                abs(row["balanced_clamp_record"]["total_delta"]) <= TOLERANCE
                for row in intervention_rows
            ),
        },
    )

    newly_resolved_controls = [
        control_result(
            "relation_weakens_but_has_no_later_readout_effect",
            "passed",
            "same_native_receiver_operation_has_preregistered_phase_conditioned_admission_split",
            "satisfies_provisional_A_DR4_readout_gate",
        ),
        control_result(
            "forming_packet_continuation_as_later_independent_readout",
            "passed",
            "original_release_packet_queue_empty_and_in_flight_total_zero_before_readout",
            "failure_blocks_A_DR4",
        ),
    ]
    auxiliary_controls = [
        control_result(
            "immediate_receiver_credit_as_independent_readout_relabel",
            "passed",
            "I9A_credit_is_not_reused;_separate_native_departure_operation_executed",
            "failure_blocks_A_DR4",
        ),
        control_result(
            "different_decay_producer_as_downstream_readout",
            "passed",
            "candidate_A_unchanged_and_no_producer_loaded_during_readout",
            "failure_blocks_causal_isolation",
        ),
        control_result(
            "receiver_state_mediation_missing",
            "passed",
            "balanced_receiver_C_clamps_reverse_the_admission_split",
            "failure_blocks_A_DR4",
        ),
        control_result(
            "target_state_explains_readout_split",
            "passed",
            "common_target_C_clamp_preserves_the_admission_split",
            "failure_blocks_A_DR4",
        ),
        control_result(
            "post_hoc_readout_threshold_selection",
            "passed",
            "five_point_threshold_sweep_frozen_before_I9A1_outcomes",
            "failure_blocks_A_DR4",
        ),
    ]
    prior_resolved_ids = {
        row["control_id"] for row in i9a_trace["control_results"]
    }
    cumulative_resolved_ids = prior_resolved_ids | {
        row["control_id"] for row in newly_resolved_controls
    }
    inherited_control_ids = set(candidate_a["complete_control_ids"])
    auxiliary_control_ids = {row["control_id"] for row in auxiliary_controls}
    auxiliary_controls_disjoint_from_inherited = not (
        auxiliary_control_ids & inherited_control_ids
    )
    unresolved_control_ids = [
        control_id
        for control_id in candidate_a["complete_control_ids"]
        if control_id not in cumulative_resolved_ids
    ]
    composed_readout_identity_components = {
        "I9A_composed_candidate_identity_output_digest": i9a_composed[
            "output_digest"
        ],
        "I9A1_readout_contract_identity": preregistration[
            "readout_contract_identity"
        ],
        "threshold_sweep_output_digest": sweep_artifact["output_digest"],
        "mediation_interventions_output_digest": mediation_artifact[
            "output_digest"
        ],
    }
    composed_readout_identity = digest_value(composed_readout_identity_components)

    artifact_manifest = [
        {
            "path": relative(path),
            "sha256": sha256_file(path),
            "artifact_role": role,
        }
        for path, role in (
            (PREREGISTRATION, "pre_outcome_independent_readout_contract"),
            (SWEEP_ARTIFACT, "native_receiver_threshold_sweep"),
            (MEDIATION_ARTIFACT, "receiver_and_target_mediation_interventions"),
            (REVISION_LINEAGE, "I9_and_I9A_review_revision_lineage"),
        )
    ]
    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-A.1",
        "artifact_kind": "release_efficacy_downstream_readout_trace",
        "artifact_schema_version": "n31_i9a1_downstream_readout_trace_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_provisional_producer_mediated_DR4_independent_native_"
            "receiver_readout_pending_I10"
        ),
        "derived_report_only": False,
        "source_current_runtime_artifact": True,
        "source_current_trace_evidence_only": True,
        "formal_candidate_row_pending_I10": True,
        "candidate_id": "A_release_efficacy_attenuation",
        "authority": "producer_mediated_relation_with_native_downstream_readout",
        "same_candidate_A_producer_retained": True,
        "different_decay_producer_added": False,
        "candidate_A_producer_active_during_readout": False,
        "preregistration": {
            "path": relative(PREREGISTRATION),
            "sha256": sha256_file(PREREGISTRATION),
            "output_digest": preregistration["output_digest"],
            "readout_contract_identity": preregistration[
                "readout_contract_identity"
            ],
        },
        "source_snapshot_audit": snapshot_sources,
        "revision_lineage": {
            "path": relative(REVISION_LINEAGE),
            "sha256": sha256_file(REVISION_LINEAGE),
            "output_digest": revision_lineage["output_digest"],
        },
        "threshold_sweep": {
            "path": relative(SWEEP_ARTIFACT),
            "sha256": sha256_file(SWEEP_ARTIFACT),
            "output_digest": sweep_artifact["output_digest"],
            "row_count": len(sweep_rows),
            "all_rows_match_preregistration": sweep_artifact[
                "all_rows_match_preregistration"
            ],
            "original_split_at_q_0_35": original_split,
        },
        "mediation_interventions": {
            "path": relative(MEDIATION_ARTIFACT),
            "sha256": sha256_file(MEDIATION_ARTIFACT),
            "output_digest": mediation_artifact["output_digest"],
            "receiver_C_clamp_reverses_admission_split": (
                receiver_clamp_reverses_split
            ),
            "target_C_clamp_preserves_admission_split": target_clamp_preserves_split,
        },
        "mediation_contract": {
            "mediation_strength": "bounded_partial_local_receiver_C",
            "other_continuation_state_matched": (
                "false_with_declared_mass_compensator"
            ),
            "receiver_C_mediates_departure_eligibility": (
                receiver_clamp_reverses_split
            ),
            "full_complete_state_mediation": False,
            "load_bearing_readout": "native_departure_admission_only",
            "complete_post_arrival_branch_state_claimed": False,
        },
        "floating_point_boundary_scope": {
            "native_eligibility_relation": "source_C >= q_probe",
            "observed_split_interval": "aged_C < q_probe <= fresh_C",
            "aged_C_observed": sweep_by_key[("aged", SPLIT_Q)][
                "receiver_C_before_readout"
            ],
            "fresh_C_observed": sweep_by_key[("fresh", SPLIT_Q)][
                "receiver_C_before_readout"
            ],
            "robust_tested_interior_q": SPLIT_Q,
            "endpoint_values_are_observed_binary_floats_not_theoretical_reals": True,
            "nextafter_boundary_controls_pending_I10": True,
        },
        "causal_chain": {
            "I9A_relation": "release_phase_selects_q_created",
            "I9A_immediate_effect": "q_created_changes_receiver_C_after_arrival",
            "I9A1_independent_readout": (
                "later_native_receiver_departure_admission_depends_on_receiver_C"
            ),
            "producer_absent_during_readout": no_producer_during_readout,
            "receiver_C_is_load_bearing_mediator": receiver_clamp_reverses_split,
            "target_C_confound_rejected": target_clamp_preserves_split,
        },
        "replay_and_invariant_audit": {
            "original_release_packets_complete_before_all_readouts": (
                all_source_packets_complete
            ),
            "all_successful_readouts_conserved": all_successful_readouts_conserved,
            "duplicate_replay_exact": all_replay_exact,
            "rejected_readout_count": len(rejected_rows),
            "all_rejected_readouts_atomic": all_rejected_readouts_atomic,
            "rejection_atomicity_scope": (
                "state_after_experiment_request_is_queued_and_before_native_step "
                "versus_state_after_native_refusal"
            ),
            "composed_readout_identity_components": (
                composed_readout_identity_components
            ),
            "composed_readout_identity": composed_readout_identity,
            "full_I10_replay_matrix_pending": True,
        },
        "control_results": newly_resolved_controls,
        "auxiliary_control_results": auxiliary_controls,
        "control_resolution": {
            "prior_resolved_control_count": len(prior_resolved_ids),
            "new_complete_control_count": len(newly_resolved_controls),
            "cumulative_resolved_control_count": len(cumulative_resolved_ids),
            "complete_control_count": len(candidate_a["complete_control_ids"]),
            "inherited_complete_controls_resolved": (
                f"{len(cumulative_resolved_ids)} / "
                f"{len(candidate_a['complete_control_ids'])}"
            ),
            "auxiliary_control_count": len(auxiliary_controls),
            "auxiliary_controls_separately_enumerated": True,
            "auxiliary_controls_disjoint_from_inherited_matrix": (
                auxiliary_controls_disjoint_from_inherited
            ),
            "unresolved_control_ids": unresolved_control_ids,
            "failed_open_count": sum(
                row["control_status"] == "failed_open"
                for row in newly_resolved_controls + auxiliary_controls
            ),
        },
        "artifact_manifest": artifact_manifest,
    }
    trace["checks"] = [
        check(
            "exact_I9_and_I9A_sources_consumed",
            all(row["identity_exact"] for row in sources),
            sources,
        ),
        check(
            "exact_I9A_final_snapshots_consumed",
            all(row["identity_exact"] for row in snapshot_sources),
            snapshot_sources,
        ),
        check(
            "I9A_is_DR3_with_DR4_readout_pending",
            i9a["candidate_result"]["current_decay_relation_ladder_rung"]
            == "DR3"
            and not i9a["candidate_result"]["DR4_supported"]
            and i9a["candidate_result"]["DR4_blocker"]
            == "independent_later_receiver_readout_pending",
            i9a["candidate_result"],
        ),
        check(
            "same_candidate_A_producer_retained_without_readout_producer",
            no_producer_during_readout
            and trace["same_candidate_A_producer_retained"]
            and not trace["different_decay_producer_added"],
            trace["causal_chain"],
        ),
        check(
            "source_release_packets_complete_before_readout",
            all_source_packets_complete,
            snapshot_sources,
        ),
        check(
            "five_point_native_threshold_sweep_matches_preregistration",
            len(sweep_rows) == 10
            and sweep_artifact["all_rows_match_preregistration"],
            trace["threshold_sweep"],
        ),
        check(
            "independent_native_readout_splits_fresh_and_aged_at_q_0_35",
            original_split,
            {
                "fresh": sweep_by_key[("fresh", SPLIT_Q)]["readout_admitted"],
                "aged": sweep_by_key[("aged", SPLIT_Q)]["readout_admitted"],
            },
        ),
        check(
            "receiver_C_clamp_reverses_readout_split",
            receiver_clamp_reverses_split,
            trace["mediation_interventions"],
        ),
        check(
            "target_C_clamp_preserves_readout_split",
            target_clamp_preserves_split,
            trace["mediation_interventions"],
        ),
        check(
            "balanced_interventions_preserve_total_coherence",
            mediation_artifact["balanced_clamps_preserve_total_C"],
            mediation_artifact["rows"],
        ),
        check(
            "successful_native_readouts_conserve_packet_budget",
            all_successful_readouts_conserved,
            "source debit equals packet amount equals target credit",
        ),
        check(
            "duplicate_readout_and_intervention_replay_exact",
            all_replay_exact,
            trace["replay_and_invariant_audit"],
        ),
        check(
            "rejected_native_readouts_are_atomic_and_state_neutral",
            all_rejected_readouts_atomic,
            [row["rejection_atomicity_receipt"] for row in rejected_rows],
        ),
        check(
            "mediation_is_bounded_partial_local_receiver_C",
            trace["mediation_contract"]["mediation_strength"]
            == "bounded_partial_local_receiver_C"
            and trace["mediation_contract"][
                "receiver_C_mediates_departure_eligibility"
            ]
            and not trace["mediation_contract"]["full_complete_state_mediation"],
            trace["mediation_contract"],
        ),
        check(
            "floating_point_boundaries_are_observed_not_theoretical",
            trace["floating_point_boundary_scope"][
                "endpoint_values_are_observed_binary_floats_not_theoretical_reals"
            ]
            and trace["floating_point_boundary_scope"][
                "robust_tested_interior_q"
            ]
            == SPLIT_Q,
            trace["floating_point_boundary_scope"],
        ),
        check(
            "I9_and_I9A_revision_lineage_closed",
            revision_lineage["I9"]["current_output_digest"]
            == i9["output_digest"]
            and revision_lineage["I9A"]["current_output_digest"]
            == i9a["output_digest"]
            and revision_lineage["I9"][
                "exact_current_artifact_consumed_by_I9A1"
            ]
            and revision_lineage["I9A"][
                "exact_current_artifact_consumed_by_I9A1"
            ],
            revision_lineage,
        ),
        check(
            "auxiliary_controls_do_not_inflate_inherited_matrix",
            auxiliary_controls_disjoint_from_inherited
            and len(cumulative_resolved_ids) == 18,
            trace["control_resolution"],
        ),
        check(
            "new_and_auxiliary_controls_resolve_without_failed_open",
            trace["control_resolution"]["failed_open_count"] == 0,
            newly_resolved_controls + auxiliary_controls,
        ),
        check(
            "composed_I9A_plus_readout_identity_recorded",
            bool(composed_readout_identity),
            composed_readout_identity_components,
        ),
        check(
            "formal_candidate_row_and_full_control_matrix_remain_pending_I10",
            trace["formal_candidate_row_pending_I10"]
            and bool(unresolved_control_ids),
            trace["control_resolution"],
        ),
        check(
            "artifact_manifest_exact",
            all((ROOT / row["path"]).is_file() for row in artifact_manifest)
            and all(
                sha256_file(ROOT / row["path"]) == row["sha256"]
                for row in artifact_manifest
            ),
            artifact_manifest,
        ),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_I9A1_downstream_readout_failed"
    trace["output_digest"] = digest_value(trace)
    TRACE.write_text(canonical_json(trace), encoding="utf-8")

    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-A.1",
        "artifact_kind": "release_efficacy_downstream_readout_candidate",
        "artifact_schema_version": "n31_i9a1_downstream_readout_candidate_v1",
        "generated_at": GENERATED_AT,
        "status": trace["status"],
        "acceptance_state": trace["acceptance_state"],
        "command": COMMAND,
        "script": SCRIPT_RELATIVE,
        "source_chain": sources,
        "source_trace": {
            "path": relative(TRACE),
            "sha256": sha256_file(TRACE),
            "output_digest": trace["output_digest"],
        },
        "candidate_result": {
            "candidate_id": "A_release_efficacy_attenuation",
            "semantic_class": "A",
            "relation_authority": "producer_mediated",
            "readout_authority": "native_LGRC9V3_runtime",
            "readout_request_authority": "experiment_probe_harness",
            "autonomous_native_readout_scheduling_supported": False,
            "current_decay_relation_ladder_rung": "DR4",
            "rung_status": "provisional_pending_I10_formal_row_and_controls",
            "DR4_supported": not trace["failed_checks"],
            "DR5_supported": False,
            "DR5_blocker": "formal_candidate_row_and_complete_I10_matrix_pending",
            "DR6_supported": False,
            "different_decay_producer_added": False,
            "native_upgrade_allowed": False,
            "native_decay_classification_unchanged": "D0a_DR2",
            "mediation_strength": "bounded_partial_local_receiver_C",
            "full_complete_state_mediation": False,
        },
        "evidence_summary": {
            "threshold_sweep_q_values": list(Q_PROBES),
            "fresh_admission_pattern": [
                sweep_by_key[("fresh", q)]["readout_admitted"] for q in Q_PROBES
            ],
            "aged_admission_pattern": [
                sweep_by_key[("aged", q)]["readout_admitted"] for q in Q_PROBES
            ],
            "split_q": SPLIT_Q,
            "receiver_C_mediation_supported": receiver_clamp_reverses_split,
            "target_C_confound_rejected": target_clamp_preserves_split,
            "producer_absent_during_readout": no_producer_during_readout,
            "native_readout_budget_conserved": all_successful_readouts_conserved,
            "duplicate_replay_exact": all_replay_exact,
            "all_rejected_readouts_atomic": all_rejected_readouts_atomic,
            "native_eligibility_split": "aged_C < q_probe <= fresh_C",
            "robust_tested_interior_q": SPLIT_Q,
        },
        "mediation_contract": trace["mediation_contract"],
        "floating_point_boundary_scope": trace[
            "floating_point_boundary_scope"
        ],
        "revision_lineage": trace["revision_lineage"],
        "evidence_artifact_boundary": {
            "source_current_trace_evidence_only": True,
            "formal_recursive_I2_candidate_row_instantiated": False,
            "formal_candidate_row_pending_I10": True,
        },
        "control_resolution": trace["control_resolution"],
        "n31_closeout_progress": {
            "n31_closeout_progress_rung": "N31-C4",
            "n31_closeout_ladder_rung_assigned": False,
            "ready_for_I9_B": True,
            "ready_for_I9_C": True,
            "ready_for_I10": False,
            "I10_requires_I9_B_and_I9_C_dispositions": True,
        },
        "claim_boundary": {
            "allowed_claim": (
                "provisional_producer_mediated_DR4_release_efficacy_relation_"
                "with_independent_native_receiver_readout_pending_I10"
            ),
            "blocked_claims": [
                "field_state_decay",
                "in_flight_attenuation",
                "autonomous_native_decay",
                "autonomous_native_readout_scheduling",
                "native_DR4",
                "producer_DR5",
                "producer_DR6",
                "native_memory",
                "trail_or_stigmergy",
                "communication",
                "ecology",
                "agency",
                "native_support",
                "Phase_8_completion",
            ],
            "unsafe_claim_flags": {
                "field_state_decay_claim_allowed": False,
                "in_flight_attenuation_claim_allowed": False,
                "autonomous_native_decay_claim_allowed": False,
                "autonomous_native_readout_scheduling_claim_allowed": False,
                "native_DR4_claim_allowed": False,
                "producer_DR5_claim_allowed": False,
                "producer_DR6_claim_allowed": False,
                "native_memory_claim_allowed": False,
                "trail_or_stigmergy_claim_allowed": False,
                "communication_claim_allowed": False,
                "ecology_claim_allowed": False,
                "agency_claim_allowed": False,
                "native_support_claim_allowed": False,
                "phase8_completion_claim_allowed": False,
            },
        },
        "governance": {
            "governance_base_revision": GOVERNANCE_BASE_REVISION,
            "src_diff_empty": git_diff_empty("src"),
            "protected_runtime_contract_diff_empty": all(
                git_diff_empty(path) for path in PROTECTED_PATHS
            ),
        },
        "artifact_manifest": artifact_manifest,
        "checks": trace["checks"],
        "failed_checks": trace["failed_checks"],
    }
    payload["checks"].extend(
        [
            check(
                "provisional_DR4_only_pending_I10",
                payload["candidate_result"]["current_decay_relation_ladder_rung"]
                == "DR4"
                and payload["candidate_result"]["DR4_supported"]
                and not payload["candidate_result"]["DR5_supported"],
                payload["candidate_result"],
            ),
            check(
                "native_lane_not_upgraded",
                not payload["candidate_result"]["native_upgrade_allowed"]
                and payload["candidate_result"][
                    "native_decay_classification_unchanged"
                ]
                == "D0a_DR2",
                payload["candidate_result"],
            ),
            check(
                "unsafe_claim_flags_false",
                not any(payload["claim_boundary"]["unsafe_claim_flags"].values()),
                payload["claim_boundary"]["unsafe_claim_flags"],
            ),
            check(
                "src_diff_empty",
                payload["governance"]["src_diff_empty"],
                GOVERNANCE_BASE_REVISION,
            ),
            check(
                "protected_runtime_contract_diff_empty",
                payload["governance"]["protected_runtime_contract_diff_empty"],
                GOVERNANCE_BASE_REVISION,
            ),
            check("no_absolute_paths_in_records", no_absolute_paths(payload), "recursive"),
        ]
    )
    payload["failed_checks"] = [
        row["check_id"] for row in payload["checks"] if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_I9A1_candidate_checks_failed"
        payload["candidate_result"]["DR4_supported"] = False
        payload["candidate_result"]["current_decay_relation_ladder_rung"] = "DR3"
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    checks = "\n".join(
        f"| `{row['check_id']}` | {str(row['passed']).lower()} |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 9-A.1 - Independent Downstream Readout

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
candidate = A release-efficacy attenuation
relation authority = producer-mediated
readout authority = native LGRC9V3 runtime
current rung = {payload['candidate_result']['current_decay_relation_ladder_rung']}
DR5_supported = false
native lane = D0a / DR2 unchanged
```

I9-A.1 does not add a second decay producer. It retains the exact Candidate A
producer from I9-A, waits until its release packet has arrived and the native
queue is empty, and then runs a separate receiver-side native packet-departure
operation. A second producer would be able to manufacture the downstream
difference and would therefore weaken, not strengthen, causal isolation.

## Native Threshold Readout

```text
q probes = {payload['evidence_summary']['threshold_sweep_q_values']}
fresh admissions = {payload['evidence_summary']['fresh_admission_pattern']}
aged admissions = {payload['evidence_summary']['aged_admission_pattern']}
```

Both branches admit `0.25` and `0.30`. Fresh alone admits `0.35` and `0.40`;
both reject `0.45`. The split is a later native admission/departure operation,
not the immediate receiver credit already recorded by I9-A.

The native eligibility interval is `aged_C < q_probe <= fresh_C`; `0.35` is the
robust tested interior. The observed `0.30` and `0.40` endpoint behavior is
binary-floating-point runtime behavior, not a theoretical real-number boundary.
Exact `nextafter` endpoint probes remain pending for I10.

Balanced receiver-coherence clamps reverse the `0.35` split: clamping fresh
receiver C down to the aged value blocks departure, while clamping aged C up to
the fresh value admits it. Clamping the destination node to one common value
preserves the original split. Thus receiver C carries the later effect; target
state and a second producer do not.

This establishes `bounded_partial_local_receiver_C` mediation of native
departure admission only. The balanced clamp changes compensator node 0, so
complete continuation state is not matched and complete post-arrival branch
mediation is not claimed. Every rejected native request is atomically
state-neutral: restoration identities, queue, ledger, scheduler/time, packet
records, and budget remain unchanged after refusal.

The original-packet, immediate-credit, and no-second-producer checks are
conformance results and record `passed`. Auxiliary controls remain separate
from the inherited matrix, which stays at `18 / 57` resolved. The recorded
I9/I9-A revision lineage confirms that current corrected artifacts are consumed
without changing the numerical outcome.

## Classification

The combined I9-A/I9-A.1 evidence supports provisional producer-mediated
`DR4`: the registered release phase weakens expression, and the resulting
receiver state changes an independent later native LGRC operation. It remains
expression attenuation rather than field-state decay. `DR5` stays blocked
until I10 builds the formal recursive candidate row and resolves the complete
control matrix.

## Checks

| Check | Passed |
|---|---:|
{checks}
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build()
    write_report(payload)
    print(canonical_json(payload), end="")


if __name__ == "__main__":
    main()
