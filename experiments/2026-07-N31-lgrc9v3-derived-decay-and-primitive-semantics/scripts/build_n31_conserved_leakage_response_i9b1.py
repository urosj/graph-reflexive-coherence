#!/usr/bin/env python3
"""Run N31 Iteration 9-B.1 formation and bounded-export response probe."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import build_n31_conserved_leakage_i9b as base


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i9b1_conserved_leakage_response_artifacts"
I9B_RESULT = OUTPUTS / "n31_conserved_leakage_i9b.json"
I9B_TRACE = OUTPUTS / "n31_i9b_conserved_leakage_source_current_trace.json"
I9B_PREREGISTRATION = (
    OUTPUTS
    / "n31_i9b_conserved_leakage_artifacts"
    / "n31_i9b_preregistration.json"
)
I9B_POLICY_SWEEP = (
    OUTPUTS
    / "n31_i9b_conserved_leakage_artifacts"
    / "n31_i9b_export_policy_sweep.json"
)
I9B_SCRIPT = EXPERIMENT / "scripts" / "build_n31_conserved_leakage_i9b.py"
PREREGISTRATION = ARTIFACT_DIR / "n31_i9b1_preregistration.json"
I9B_LINEAGE = ARTIFACT_DIR / "n31_i9b_revision_lineage_r1.json"
FORMATION_SNAPSHOT = ARTIFACT_DIR / "n31_i9b1_formation_snapshot.json"
PERSISTENCE_SNAPSHOT = ARTIFACT_DIR / "n31_i9b1_persistence_snapshot.json"
PERSISTENCE_RECORD = ARTIFACT_DIR / "n31_i9b1_persistence_checkpoint.json"
RESPONSE_MATRIX = ARTIFACT_DIR / "n31_i9b1_export_response_matrix.json"
READOUT_MATRIX = ARTIFACT_DIR / "n31_i9b1_readout_boundary_matrix.json"
TRACE = OUTPUTS / "n31_i9b1_conserved_leakage_response_trace.json"
OUTPUT = OUTPUTS / "n31_conserved_leakage_response_i9b1.json"
REPORT = REPORTS / "n31_conserved_leakage_response_i9b1.md"
SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_conserved_leakage_response_i9b1.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
SOURCE_IDENTITIES = {
    I9B_RESULT: (
        "4427aa0c5d5d1e864f304873edbe2190ec3e975c0702e4f1ef3ed4ac81adc9b3",
        "0ea586c7bfe23d3c8341fa874b07892ce4274125d58b8a6c77a284f77214d5ac",
    ),
    I9B_TRACE: (
        "65ac1e3a81788fdfc9abdad7ff9398b3308ffc55e9801cce829b249f7238a454",
        "f383d757dbee5cb853ffb78e2d8a1b7df1239ef6efb198c4dd9df17b6dceca90",
    ),
    I9B_PREREGISTRATION: (
        "4a2ceb8862ca8ae4384d20fbbffdef908a8ea33b06ee5f2ef6c094e4c09a0e4c",
        "9896f926960e07536d7a2b0919ca51c9c93df7ab9da0d2f29c23af4c44a7d987",
    ),
    I9B_POLICY_SWEEP: (
        "b8b4f4a9f51b88ba210d1b84601b38807785d38d11302dce536cfd18f7fb35e2",
        "dd650c0eaf545ea04749aa3fce975118fdfbb5615d625ca6ac3b40a433cf4c6f",
    ),
}
I9B_SCRIPT_SHA256 = "61028afea71579e8c4a0dc4d962c40bd24ee2b80d3378313d822c51f1c584210"
SOURCE_C_LEVELS = (0.20, 0.21, 0.22, 0.24)
TARGET_ROUTE_MASS = 0.35
ROBUST_READOUT_OFFSET = 0.005
TOLERANCE = base.TOLERANCE


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


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def write_record(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    record["output_digest"] = digest_value(record)
    path.write_text(canonical_json(record), encoding="utf-8")
    return record


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


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


def build_i9b_revision_lineage() -> dict[str, Any]:
    return write_record(
        I9B_LINEAGE,
        {
            "artifact_kind": "n31_i9b_revision_lineage",
            "artifact_schema_version": "n31_i9b_revision_lineage_r1",
            "generated_at": GENERATED_AT,
            "reviewed_I9B_R0_identity": {
                "output_digest": (
                    "68e3b67d0831b63a94f03443b08d871112bd85e92450c7003cdc502d0281359e"
                ),
                "trace_output_digest": (
                    "43675b9b7afa7e39637f55a364cad8114abbe9398282d927e3b3112dcc864078"
                ),
                "artifact_sha256_status": "not_retained_before_review_correction",
                "role": "reviewed_pre_attribution_correction_identity_not_evidence",
            },
            "corrected_I9B_R1_identity": {
                "output_digest": SOURCE_IDENTITIES[I9B_RESULT][0],
                "artifact_sha256": SOURCE_IDENTITIES[I9B_RESULT][1],
                "trace_output_digest": SOURCE_IDENTITIES[I9B_TRACE][0],
                "trace_sha256": SOURCE_IDENTITIES[I9B_TRACE][1],
                "preregistration_output_digest": SOURCE_IDENTITIES[
                    I9B_PREREGISTRATION
                ][0],
                "preregistration_sha256": SOURCE_IDENTITIES[
                    I9B_PREREGISTRATION
                ][1],
                "role": "exact_corrected_I9B_consumed_by_I9B1_and_I10",
            },
            "corrections": [
                "formation_reclassified_as_strengthening_from_baseline_O_B_0.05",
                "attributable_formation_effect_gate_added",
                "DR2_persistence_scope_made_explicit",
                "composed_receipt_event_mismatch_controls_added",
                "corrected_I9_revision_lineage_retained",
                "unretained_runtime_test_count_removed_from_formal_evidence",
            ],
            "scientific_B_R_DR4_conclusion_changed": False,
            "earlier_identity_consumable_as_evidence": False,
            "corrected_identity_consumable_as_evidence": True,
        },
    )


def build_preregistration() -> dict[str, Any]:
    rows = [
        {
            "row_id": f"source_C_{source_c:.2f}",
            "source_C": source_c,
            "route_mass_before_export": TARGET_ROUTE_MASS,
            "formation_source_C": TARGET_ROUTE_MASS - source_c,
            "expected_q_emit": base.emission_amount(source_c),
        }
        for source_c in SOURCE_C_LEVELS
    ]
    return write_record(
        PREREGISTRATION,
        {
            "experiment": "N31",
            "iteration": "9-B.1",
            "artifact_kind": "formation_and_bounded_export_response_preregistration",
            "artifact_schema_version": "n31_i9b1_preregistration_v1",
            "generated_at": GENERATED_AT,
            "candidate_id": "B_conserved_source_leakage",
            "candidate_policy": {
                "producer_id": "n31_B_registered_route_local_export_policy_v1",
                "equation": (
                    "q_emit = min(q_cap, max(0, C_leakage_source - C_floor))"
                ),
                "C_floor": base.C_FLOOR,
                "q_cap": base.Q_CAP,
                "topology_unchanged_from_I9B": True,
                "second_export_or_decay_producer_added": False,
            },
            "formation_attribution": {
                "expected_baseline_O_B": 0.05,
                "expected_formed_O_B": 0.15,
                "expected_formation_effect_O_B": 0.10,
                "minimum_formation_effect": (
                    base.MINIMUM_ATTRIBUTABLE_FORMATION_EFFECT
                ),
                "gate": (
                    "formed_O_B - baseline_O_B >= minimum_formation_effect"
                ),
            },
            "persistence_progression": {
                "authority": "experiment_scheduled_native_runtime_trial",
                "runtime_operation": "causal_boundary_birth_trial",
                "parent_node_id": 2,
                "outward_flux_pressure": 0.0,
                "rng_sample": 1.0,
                "expected_topology_events": 0,
                "expected_topology_mutation": False,
                "expected_O_B_change": 0.0,
                "candidate_B_export_policy_invoked": False,
            },
            "response_rows": rows,
            "required_positive_q_levels": [0.01, 0.02, 0.04],
            "readout_probe_contract": {
                "robust_offset": ROBUST_READOUT_OFFSET,
                "probe_positions": [
                    "robust_below",
                    "nextafter_below",
                    "exact_boundary",
                    "nextafter_above",
                    "robust_above",
                ],
                "required_robust_behavior": (
                    "below_admitted_and_above_rejected"
                ),
                "floating_boundary_behavior": "record_not_presume",
                "paired_boundary_shift_rule": (
                    "no_export_source_C - post_export_source_C == q_emit"
                ),
            },
            "I10_response_row_diff_whitelist": {
                "diagnostic_preparation_allowed_paths": [
                    "base_state.nodes[0].coherence",
                    "base_state.nodes[1].coherence",
                    "base_state.nodes[2].coherence",
                ],
                "diagnostic_preparation_required_invariants": [
                    "node_3_unchanged",
                    "total_coherence_delta_zero",
                    "route_mass_equals_0.35",
                    "topology_unchanged",
                ],
                "native_export_allowed_paths": [
                    "base_state.nodes[1].coherence",
                    "base_state.nodes[2].coherence",
                    "packet_ledger",
                    "event_queue",
                    "scheduler_event_index",
                    "checkpoint_index",
                    "event_time_key",
                    "observables",
                ],
                "native_export_blocked_paths": [
                    "base_state.nodes[0].coherence",
                    "base_state.nodes[3].coherence",
                    "topology",
                ],
                "closure_allowed_paths": [
                    "producer_call_count",
                    "export_policy_receipt",
                ],
                "closure_reset_rule": (
                    "each response row starts from the exact unconsumed closure "
                    "bound to the same formation receipt"
                ),
            },
            "claim_ceiling": "provisional_producer_mediated_B_R_DR4_shape_support",
            "DR5_supported": False,
            "D0_R_bridge_status": "not_tested",
            "native_upgrade_allowed": False,
        },
    )


def reconstruct_formation() -> dict[str, Any]:
    model, topology_identity = base.build_fixture()
    route_before = base.route_observables(model)
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=base.FORMATION_AMOUNT,
        departure_event_time_key=0.0,
        arrival_event_time_key=1.0,
        scheduler_event_index=1,
        packet_index=0,
        source_lineage_id="n31_B_formation_lineage",
        target_lineage_id="n31_B_leakage_source_lineage",
    )
    departure = base.processing_receipt(model.step())
    arrival = base.processing_receipt(model.step())
    route_after = base.route_observables(model)
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    model.save(str(FORMATION_SNAPSHOT))
    restored = base.LGRC9V3.load(str(FORMATION_SNAPSHOT))
    return {
        "topology_identity": topology_identity,
        "topology_digest": digest_value(topology_identity),
        "route_before_formation": route_before,
        "route_after_formation": route_after,
        "formation_effect_O_B": (
            route_after["route_organization_O_B"]
            - route_before["route_organization_O_B"]
        ),
        "departure_receipt": departure,
        "arrival_receipt": arrival,
        "formation_activity_stopped": (
            len(ledger.event_queue_records) == 0
            and abs(float(ledger.in_flight_packet_total)) <= TOLERANCE
        ),
        "restoration_v1_exact": (
            base.digest_lgrc9v3_restoration_identity_v1(model)
            == base.digest_lgrc9v3_restoration_identity_v1(restored)
        ),
        "restoration_v2_exact": (
            base.digest_lgrc9v3_restoration_identity_v2(model)
            == base.digest_lgrc9v3_restoration_identity_v2(restored)
        ),
    }


def run_persistence_progression(formation: dict[str, Any]) -> dict[str, Any]:
    model = base.LGRC9V3.load(str(FORMATION_SNAPSHOT))
    route_before = base.route_observables(model)
    node_ids_before = sorted(model.get_state().base_state.nodes)
    edge_ids_before = sorted(model.get_state().base_state.port_edges)
    scheduler_before = int(model.get_state().scheduler_event_index)
    checkpoint_before = int(model.get_state().checkpoint_index)
    model.schedule_causal_boundary_birth_trial(
        parent_node_id=2,
        outward_flux_pressure=0.0,
        event_time_key=2.0,
        scheduler_event_index=3,
        rng_sample=1.0,
    )
    result = model.step()
    route_after = base.route_observables(model)
    node_ids_after = sorted(model.get_state().base_state.nodes)
    edge_ids_after = sorted(model.get_state().base_state.port_edges)
    model.save(str(PERSISTENCE_SNAPSHOT))
    restored = base.LGRC9V3.load(str(PERSISTENCE_SNAPSHOT))
    record = {
        "artifact_kind": "n31_i9b1_independent_native_persistence_checkpoint",
        "artifact_schema_version": "n31_i9b1_persistence_checkpoint_v1",
        "generated_at": GENERATED_AT,
        "formation_snapshot": relative(FORMATION_SNAPSHOT),
        "progression_authority": "experiment_scheduled_native_runtime_trial",
        "progression_class": (
            "nonqualifying_nonadmitted_disjoint_causal_boundary_birth_trial"
        ),
        "parent_node_id": 2,
        "parent_node_on_registered_route": False,
        "bookkeeping": result.bookkeeping,
        "emitted_event_kinds": [event.kind for event in result.events],
        "topology_events_routed": result.bookkeeping["topology_events_routed"],
        "route_before": route_before,
        "route_after": route_after,
        "O_B_change": (
            route_after["route_organization_O_B"]
            - route_before["route_organization_O_B"]
        ),
        "node_ids_before": node_ids_before,
        "node_ids_after": node_ids_after,
        "edge_ids_before": edge_ids_before,
        "edge_ids_after": edge_ids_after,
        "topology_unchanged": (
            node_ids_before == node_ids_after and edge_ids_before == edge_ids_after
        ),
        "scheduler_advanced": (
            int(model.get_state().scheduler_event_index) > scheduler_before
        ),
        "checkpoint_advanced": (
            int(model.get_state().checkpoint_index) > checkpoint_before
        ),
        "candidate_B_export_policy_invocation_count": 0,
        "candidate_B_export_packet_count": 0,
        "restoration_v1_exact": (
            base.digest_lgrc9v3_restoration_identity_v1(model)
            == base.digest_lgrc9v3_restoration_identity_v1(restored)
        ),
        "restoration_v2_exact": (
            base.digest_lgrc9v3_restoration_identity_v2(model)
            == base.digest_lgrc9v3_restoration_identity_v2(restored)
        ),
        "persistence_supported": (
            abs(
                route_after["route_organization_O_B"]
                - route_before["route_organization_O_B"]
            )
            <= TOLERANCE
            and result.bookkeeping["processed_event_kind"]
            == "lgrc9v3_causal_boundary_birth_trial"
            and result.bookkeeping["topology_events_routed"] == 0
            and node_ids_before == node_ids_after
            and edge_ids_before == edge_ids_after
        ),
        "autonomous_persistence_claimed": False,
        "persistence_through_ordinary_state_mutating_activity": "not_tested",
        "source_formation_effect_O_B": formation["formation_effect_O_B"],
    }
    return write_record(PERSISTENCE_RECORD, record)


def prepare_response_snapshot(
    source_c: float, pre_path: Path
) -> dict[str, Any]:
    model = base.LGRC9V3.load(str(FORMATION_SNAPSHOT))
    target_c0 = TARGET_ROUTE_MASS - source_c
    current = base.node_coherence(model)
    deltas = {
        0: target_c0 - current["0"],
        1: source_c - current["1"],
    }
    deltas[2] = -sum(deltas.values())
    intervention = base.apply_node_deltas(
        model, deltas, f"i9b1_source_C_{source_c:.2f}"
    )
    model.save(str(pre_path))
    return {
        "intervention": intervention,
        "route": base.route_observables(model),
        "budget": base.runtime_budget(model),
        "restoration_identity_v2": (
            base.digest_lgrc9v3_restoration_identity_v2(model)
        ),
    }


def run_readout_probe(
    snapshot: Path, *, row_id: str, branch: str, probe_id: str, q_probe: float
) -> dict[str, Any]:
    model = base.LGRC9V3.load(str(snapshot))
    source_c = float(model.get_state().base_state.nodes[1].coherence)
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    lineage = f"n31_B_i9b1_readout_{row_id}_{branch}_{probe_id}"
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=3,
        edge_id=2,
        amount=q_probe,
        departure_event_time_key=4.0,
        arrival_event_time_key=5.0,
        scheduler_event_index=5,
        packet_index=len(ledger.packet_records),
        source_lineage_id=lineage,
        target_lineage_id="n31_B_later_readout_target",
    )
    before = base.state_projection(model)
    admitted = False
    rejection_reason = None
    departure = None
    arrival = None
    try:
        departure = base.processing_receipt(model.step())
        admitted = True
        arrival = base.processing_receipt(model.step())
    except base.InvalidStateTransitionError as exc:
        rejection_reason = str(exc)
    after = base.state_projection(model)
    atomic = None
    if not admitted:
        fields = (
            "restoration_identity_v1",
            "restoration_identity_v2",
            "queue_digest",
            "queue_count",
            "packet_ledger_digest",
            "packet_record_count",
            "scheduler_event_index",
            "checkpoint_index",
            "event_time_key",
            "budget",
        )
        atomic = all(before[field] == after[field] for field in fields)
    return {
        "row_id": row_id,
        "branch": branch,
        "probe_id": probe_id,
        "source_C": source_c,
        "q_probe": q_probe,
        "signed_distance_from_source_C": q_probe - source_c,
        "admitted": admitted,
        "rejection_reason": rejection_reason,
        "rejected_state_neutral": atomic,
        "departure_receipt": departure,
        "arrival_receipt": arrival,
    }


def probe_values(source_c: float) -> dict[str, float]:
    return {
        "robust_below": source_c - ROBUST_READOUT_OFFSET,
        "nextafter_below": math.nextafter(source_c, -math.inf),
        "exact_boundary": source_c,
        "nextafter_above": math.nextafter(source_c, math.inf),
        "robust_above": source_c + ROBUST_READOUT_OFFSET,
    }


def build_response_shape(
    formation: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    closure = base.initial_export_closure(formation["arrival_receipt"])
    response_rows: list[dict[str, Any]] = []
    readout_rows: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, Any]] = []
    for source_c in SOURCE_C_LEVELS:
        row_id = f"source_C_{source_c:.2f}"
        pre_path = ARTIFACT_DIR / f"n31_i9b1_{row_id}_pre_export.json"
        post_path = ARTIFACT_DIR / f"n31_i9b1_{row_id}_post_export.json"
        prepared = prepare_response_snapshot(source_c, pre_path)
        export = base.execute_export(
            pre_path,
            closure,
            formation["arrival_receipt"],
            lineage_suffix=f"i9b1_{source_c:.2f}",
            save_final_to=post_path,
        )
        q_emit = float(export["q_emit"])
        route_delta = {
            key: export["route_after"][key] - export["route_before"][key]
            for key in ("route_mass_M_B", "route_organization_O_B")
        }
        in_flight_amount = (
            0.0
            if export["packet_after_departure"] is None
            else float(export["packet_after_departure"]["amount"])
        )
        response_rows.append(
            {
                "row_id": row_id,
                "source_state_authority": "experiment_diagnostic_intervention",
                "source_state": prepared,
                "expected_q_emit": base.emission_amount(source_c),
                "observed_q_emit": q_emit,
                "positive_export": q_emit > TOLERANCE,
                "route_before": export["route_before"],
                "route_after": export["route_after"],
                "delta_route_organization_O_B": route_delta[
                    "route_organization_O_B"
                ],
                "delta_route_mass_M_B": route_delta["route_mass_M_B"],
                "source_debit": export["source_debit"],
                "in_flight_amount": in_flight_amount,
                "destination_credit": export["destination_credit"],
                "q_relation_exact": (
                    abs(q_emit - base.emission_amount(source_c)) <= TOLERANCE
                ),
                "organization_delta_equals_negative_q": (
                    abs(route_delta["route_organization_O_B"] + q_emit)
                    <= TOLERANCE
                ),
                "route_mass_delta_equals_negative_q": (
                    abs(route_delta["route_mass_M_B"] + q_emit) <= TOLERANCE
                ),
                "source_debit_equals_q": (
                    abs(export["source_debit"] - q_emit) <= TOLERANCE
                ),
                "in_flight_equals_q": (
                    abs(in_flight_amount - q_emit) <= TOLERANCE
                ),
                "destination_credit_equals_q": (
                    abs(export["destination_credit"] - q_emit) <= TOLERANCE
                ),
                "diagnostic_diff_whitelist_passed": (
                    set(prepared["intervention"]["node_deltas"])
                    == {"0", "1", "2"}
                    and abs(
                        sum(prepared["intervention"]["node_deltas"].values())
                    )
                    <= TOLERANCE
                    and abs(
                        prepared["route"]["route_mass_M_B"] - TARGET_ROUTE_MASS
                    )
                    <= TOLERANCE
                ),
                "native_export_diff_whitelist_passed": (
                    abs(export["node_C_after"]["0"] - export["node_C_before"]["0"])
                    <= TOLERANCE
                    and abs(
                        export["node_C_after"]["3"]
                        - export["node_C_before"]["3"]
                    )
                    <= TOLERANCE
                ),
                "closure_reinitialized_from_exact_formation_receipt": (
                    export["closure_before"] == closure
                ),
                "closure_one_shot_receipt_consumed": export["closure_after"][
                    "export_policy_receipt"
                ]["one_shot_consumed"],
                "export_packet_created": export["packet_scheduled"],
                "pre_export_native_identity_v2": prepared[
                    "restoration_identity_v2"
                ],
                "post_export_native_identity_v2": (
                    base.digest_lgrc9v3_restoration_identity_v2(
                        base.LGRC9V3.load(str(post_path))
                    )
                ),
                "zero_export_native_identity_unchanged": (
                    q_emit > TOLERANCE
                    or sha256_file(pre_path) == sha256_file(post_path)
                ),
                "zero_export_closure_receipt_consumed": (
                    q_emit > TOLERANCE
                    or export["closure_after"]["export_policy_receipt"][
                        "one_shot_consumed"
                    ]
                ),
                "zero_export_packet_created": (
                    None if q_emit > TOLERANCE else export["packet_scheduled"]
                ),
                "event_queue_empty_after_export": export[
                    "event_queue_empty_after_export"
                ],
                "producer_call": export["producer_call"],
                "pre_export_snapshot": relative(pre_path),
                "post_export_snapshot": relative(post_path),
            }
        )
        snapshot_rows.extend(
            [
                {
                    "path": relative(pre_path),
                    "sha256": sha256_file(pre_path),
                    "artifact_role": f"{row_id}_no_export_native_state",
                },
                {
                    "path": relative(post_path),
                    "sha256": sha256_file(post_path),
                    "artifact_role": f"{row_id}_post_export_native_state",
                },
            ]
        )
        for branch, snapshot in (("no_export", pre_path), ("export", post_path)):
            branch_source_c = float(
                base.LGRC9V3.load(str(snapshot))
                .get_state()
                .base_state.nodes[1]
                .coherence
            )
            for probe_id, q_probe in probe_values(branch_source_c).items():
                readout_rows.append(
                    run_readout_probe(
                        snapshot,
                        row_id=row_id,
                        branch=branch,
                        probe_id=probe_id,
                        q_probe=q_probe,
                    )
                )

    q_values = [row["observed_q_emit"] for row in response_rows]
    response_matrix = write_record(
        RESPONSE_MATRIX,
        {
            "artifact_kind": "n31_i9b1_bounded_export_response_matrix",
            "artifact_schema_version": "n31_i9b1_export_response_matrix_v1",
            "generated_at": GENERATED_AT,
            "policy_identity": "n31_B_registered_route_local_export_policy_v1",
            "topology_unchanged": True,
            "source_state_scope": (
                "constant_route_mass_diagnostic_interventions_not_additional_"
                "formation_trajectories"
            ),
            "rows": response_rows,
            "distinct_positive_q_levels": sorted(
                {row["observed_q_emit"] for row in response_rows if row["positive_export"]}
            ),
            "q_emit_monotonic_non_decreasing": all(
                left <= right + TOLERANCE
                for left, right in zip(q_values, q_values[1:])
            ),
            "all_response_equations_close": all(
                row["q_relation_exact"]
                and row["organization_delta_equals_negative_q"]
                and row["route_mass_delta_equals_negative_q"]
                and row["source_debit_equals_q"]
                and row["in_flight_equals_q"]
                and row["destination_credit_equals_q"]
                and row["event_queue_empty_after_export"]
                for row in response_rows
            ),
            "all_diff_whitelists_pass": all(
                row["diagnostic_diff_whitelist_passed"]
                and row["native_export_diff_whitelist_passed"]
                and row["closure_reinitialized_from_exact_formation_receipt"]
                and row["closure_one_shot_receipt_consumed"]
                for row in response_rows
            ),
            "zero_export_receipt": {
                "row_id": response_rows[0]["row_id"],
                "zero_export_native_identity_unchanged": response_rows[0][
                    "zero_export_native_identity_unchanged"
                ],
                "zero_export_closure_receipt_consumed": response_rows[0][
                    "zero_export_closure_receipt_consumed"
                ],
                "zero_export_packet_created": response_rows[0][
                    "zero_export_packet_created"
                ],
                "pre_export_snapshot_sha256": sha256_file(
                    ROOT / response_rows[0]["pre_export_snapshot"]
                ),
                "post_export_snapshot_sha256": sha256_file(
                    ROOT / response_rows[0]["post_export_snapshot"]
                ),
            },
        },
    )

    branch_profiles: list[dict[str, Any]] = []
    for response in response_rows:
        row_id = response["row_id"]
        profiles: dict[str, dict[str, Any]] = {}
        for branch in ("no_export", "export"):
            rows = [
                row
                for row in readout_rows
                if row["row_id"] == row_id and row["branch"] == branch
            ]
            by_probe = {row["probe_id"]: row for row in rows}
            profiles[branch] = {
                "source_C": by_probe["exact_boundary"]["source_C"],
                "robust_below_admitted": by_probe["robust_below"]["admitted"],
                "exact_boundary_admitted": by_probe["exact_boundary"]["admitted"],
                "robust_above_rejected": not by_probe["robust_above"]["admitted"],
                "nextafter_below_admitted": by_probe["nextafter_below"]["admitted"],
                "nextafter_above_admitted": by_probe["nextafter_above"]["admitted"],
                "rejected_rows_atomic": all(
                    row["admitted"] or row["rejected_state_neutral"] for row in rows
                ),
            }
        boundary_shift = (
            profiles["no_export"]["source_C"] - profiles["export"]["source_C"]
        )
        branch_profiles.append(
            {
                "row_id": row_id,
                "q_emit": response["observed_q_emit"],
                "no_export": profiles["no_export"],
                "export": profiles["export"],
                "paired_admission_boundary_shift": boundary_shift,
                "boundary_shift_equals_q_emit": (
                    abs(boundary_shift - response["observed_q_emit"])
                    <= TOLERANCE
                ),
            }
        )
    shifts = [row["paired_admission_boundary_shift"] for row in branch_profiles]
    readout_matrix = write_record(
        READOUT_MATRIX,
        {
            "artifact_kind": "n31_i9b1_native_readout_boundary_matrix",
            "artifact_schema_version": "n31_i9b1_readout_boundary_matrix_v1",
            "generated_at": GENERATED_AT,
            "probe_rows": readout_rows,
            "branch_profiles": branch_profiles,
            "all_robust_below_admitted": all(
                profile[branch]["robust_below_admitted"]
                for profile in branch_profiles
                for branch in ("no_export", "export")
            ),
            "all_robust_above_rejected": all(
                profile[branch]["robust_above_rejected"]
                for profile in branch_profiles
                for branch in ("no_export", "export")
            ),
            "all_rejected_rows_atomic": all(
                profile[branch]["rejected_rows_atomic"]
                for profile in branch_profiles
                for branch in ("no_export", "export")
            ),
            "all_boundary_shifts_equal_q_emit": all(
                profile["boundary_shift_equals_q_emit"]
                for profile in branch_profiles
            ),
            "paired_boundary_shift_monotonic_non_decreasing": all(
                left <= right + TOLERANCE
                for left, right in zip(shifts, shifts[1:])
            ),
            "floating_boundary_behavior_is_diagnostic": True,
        },
    )
    return response_matrix, readout_matrix, snapshot_rows


def build() -> dict[str, Any]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    sources = [source_record(path) for path in SOURCE_IDENTITIES]
    source_script = {
        "path": relative(I9B_SCRIPT),
        "expected_sha256": I9B_SCRIPT_SHA256,
        "actual_sha256": sha256_file(I9B_SCRIPT),
        "identity_exact": sha256_file(I9B_SCRIPT) == I9B_SCRIPT_SHA256,
        "role": "executed_Candidate_B_producer_and_fixture_implementation",
    }
    lineage = build_i9b_revision_lineage()
    preregistration = build_preregistration()
    formation = reconstruct_formation()
    persistence = run_persistence_progression(formation)
    response, readout, snapshot_rows = build_response_shape(formation)

    artifact_manifest = [
        {
            "path": relative(path),
            "sha256": sha256_file(path),
            "artifact_role": role,
        }
        for path, role in (
            (PREREGISTRATION, "pre_outcome_I9B1_contract"),
            (I9B_LINEAGE, "reviewed_to_corrected_I9B_identity_lineage"),
            (FORMATION_SNAPSHOT, "reconstructed_native_formation_state"),
            (PERSISTENCE_SNAPSHOT, "post_disjoint_native_progression_state"),
            (PERSISTENCE_RECORD, "independent_native_persistence_checkpoint"),
            (RESPONSE_MATRIX, "multi_level_bounded_export_response_shape"),
            (READOUT_MATRIX, "paired_native_admission_boundary_shape"),
        )
    ] + snapshot_rows

    positive_levels = response["distinct_positive_q_levels"]
    inherited_policy_sweep = load_json(I9B_POLICY_SWEEP)
    inherited_plateau_rows = [
        {
            "source_C": row["source_C"],
            "source_excess": row["source_C"] - base.C_FLOOR,
            "observed_q_emit": row["observed_q_emit"],
        }
        for row in inherited_policy_sweep["rows"]
        if row["source_C"] - base.C_FLOOR > base.Q_CAP + TOLERANCE
    ]
    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-B.1",
        "artifact_kind": "formation_and_bounded_export_response_trace",
        "artifact_schema_version": "n31_i9b1_response_trace_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_I9B1_formation_attribution_persistence_and_bounded_"
            "export_response_shape_at_provisional_B_R_DR4"
        ),
        "source_chain": sources + [source_script],
        "derived_report_only": False,
        "source_current_runtime_artifact": True,
        "candidate_id": "B_conserved_source_leakage",
        "producer_policy_unchanged": True,
        "topology_unchanged": True,
        "second_export_or_decay_producer_added": False,
        "preregistration": {
            "path": relative(PREREGISTRATION),
            "sha256": sha256_file(PREREGISTRATION),
            "output_digest": preregistration["output_digest"],
        },
        "I9B_revision_lineage": {
            "path": relative(I9B_LINEAGE),
            "sha256": sha256_file(I9B_LINEAGE),
            "output_digest": lineage["output_digest"],
            "scientific_B_R_DR4_conclusion_changed": lineage[
                "scientific_B_R_DR4_conclusion_changed"
            ],
        },
        "formation_attribution": formation,
        "persistence_checkpoint": {
            "path": relative(PERSISTENCE_RECORD),
            "sha256": sha256_file(PERSISTENCE_RECORD),
            "output_digest": persistence["output_digest"],
            "persistence_supported": persistence["persistence_supported"],
            "progression_authority": persistence["progression_authority"],
            "autonomous_persistence_claimed": False,
            "persistence_through_ordinary_state_mutating_activity": "not_tested",
        },
        "response_shape": {
            "path": relative(RESPONSE_MATRIX),
            "sha256": sha256_file(RESPONSE_MATRIX),
            "output_digest": response["output_digest"],
            "distinct_positive_q_levels": positive_levels,
            "q_emit_monotonic_non_decreasing": response[
                "q_emit_monotonic_non_decreasing"
            ],
            "all_response_equations_close": response[
                "all_response_equations_close"
            ],
            "all_diff_whitelists_pass": response["all_diff_whitelists_pass"],
            "zero_export_receipt": response["zero_export_receipt"],
            "B1_response_shape_scope": "monotonic_linear_through_cap_boundary",
            "B1_independent_above_cap_plateau_tested": False,
            "I9B_inherited_above_cap_plateau_rows": inherited_plateau_rows,
            "I9B_inherited_q_cap_never_exceeded": inherited_policy_sweep[
                "q_cap_never_exceeded"
            ],
        },
        "readout_shape": {
            "path": relative(READOUT_MATRIX),
            "sha256": sha256_file(READOUT_MATRIX),
            "output_digest": readout["output_digest"],
            "all_robust_below_admitted": readout[
                "all_robust_below_admitted"
            ],
            "all_robust_above_rejected": readout[
                "all_robust_above_rejected"
            ],
            "all_rejected_rows_atomic": readout["all_rejected_rows_atomic"],
            "all_boundary_shifts_equal_q_emit": readout[
                "all_boundary_shifts_equal_q_emit"
            ],
            "paired_boundary_shift_monotonic_non_decreasing": readout[
                "paired_boundary_shift_monotonic_non_decreasing"
            ],
            "mediation_strength": "bounded_partial_local_leakage_source_C",
        },
        "I9B_controls_retained": {
            "source_C_clamp_reverses_readout": True,
            "destination_C_clamp_preserves_readout": True,
            "matched_route_mass_loss_preserves_O_B_and_readout": True,
            "producer_omitted_no_export_branch_present": True,
            "composed_receipt_event_mismatches_fail_closed": True,
            "source_identity": sources[0],
        },
        "classification": {
            "semantic_class": "B",
            "semantic_subtype": "B_R_conserved_export_policy",
            "relation_authority": "producer_mediated",
            "transport_authority": "native_LGRC9V3_packet_runtime",
            "current_decay_relation_ladder_rung": "DR4",
            "DR4_supported": True,
            "DR5_supported": False,
            "DR6_supported": False,
            "D0_R_bridge_status": "not_tested",
            "native_decay_classification_unchanged": "D0a_DR2",
            "full_route_distribution_mediation": False,
        },
        "governance": {
            "governance_base_revision": base.GOVERNANCE_BASE_REVISION,
            "src_diff_empty": base.git_diff_empty("src"),
            "protected_runtime_contract_diff_empty": all(
                base.git_diff_empty(path) for path in base.PROTECTED_PATHS
            ),
        },
        "artifact_manifest": artifact_manifest,
    }
    trace["checks"] = [
        check(
            "exact_I9B_sources_and_producer_implementation_consumed",
            all(row["identity_exact"] for row in sources)
            and source_script["identity_exact"],
            trace["source_chain"],
        ),
        check(
            "formation_strengthens_existing_O_B_by_attributable_delta",
            abs(formation["route_before_formation"]["route_organization_O_B"] - 0.05)
            <= TOLERANCE
            and abs(formation["route_after_formation"]["route_organization_O_B"] - 0.15)
            <= TOLERANCE
            and formation["formation_effect_O_B"]
            >= base.MINIMUM_ATTRIBUTABLE_FORMATION_EFFECT - TOLERANCE,
            formation,
        ),
        check(
            "formation_exhausted_and_restores_before_progression",
            formation["formation_activity_stopped"]
            and formation["restoration_v1_exact"]
            and formation["restoration_v2_exact"],
            formation,
        ),
        check(
            "formed_relation_persists_through_disjoint_native_progression",
            persistence["persistence_supported"]
            and persistence["scheduler_advanced"]
            and persistence["checkpoint_advanced"]
            and persistence["restoration_v1_exact"]
            and persistence["restoration_v2_exact"],
            persistence,
        ),
        check(
            "persistence_progression_not_relabelled_autonomous",
            persistence["progression_authority"]
            == "experiment_scheduled_native_runtime_trial"
            and not persistence["autonomous_persistence_claimed"],
            persistence,
        ),
        check(
            "three_distinct_positive_export_levels_observed",
            len(positive_levels) >= 3
            and all(
                any(abs(value - expected) <= TOLERANCE for value in positive_levels)
                for expected in (0.01, 0.02, 0.04)
            ),
            positive_levels,
        ),
        check(
            "bounded_export_response_equations_close",
            response["all_response_equations_close"]
            and response["q_emit_monotonic_non_decreasing"],
            trace["response_shape"],
        ),
        check(
            "response_row_diff_whitelists_and_closure_reset_pass",
            response["all_diff_whitelists_pass"],
            trace["response_shape"],
        ),
        check(
            "zero_export_native_identity_and_closure_transition_separated",
            response["zero_export_receipt"][
                "zero_export_native_identity_unchanged"
            ]
            and response["zero_export_receipt"][
                "zero_export_closure_receipt_consumed"
            ]
            and not response["zero_export_receipt"]["zero_export_packet_created"],
            response["zero_export_receipt"],
        ),
        check(
            "cap_plateau_scoped_to_inherited_I9B_evidence",
            len(inherited_plateau_rows) >= 1
            and inherited_policy_sweep["q_cap_never_exceeded"]
            and not trace["response_shape"][
                "B1_independent_above_cap_plateau_tested"
            ],
            trace["response_shape"],
        ),
        check(
            "paired_native_readout_boundary_shift_equals_export",
            readout["all_boundary_shifts_equal_q_emit"]
            and readout["paired_boundary_shift_monotonic_non_decreasing"],
            trace["readout_shape"],
        ),
        check(
            "robust_readout_sides_and_atomic_refusal_pass",
            readout["all_robust_below_admitted"]
            and readout["all_robust_above_rejected"]
            and readout["all_rejected_rows_atomic"],
            trace["readout_shape"],
        ),
        check(
            "B_R_DR4_ceiling_preserved",
            trace["classification"]["current_decay_relation_ladder_rung"]
            == "DR4"
            and not trace["classification"]["DR5_supported"]
            and trace["classification"]["D0_R_bridge_status"] == "not_tested",
            trace["classification"],
        ),
        check(
            "protected_runtime_contracts_unchanged",
            trace["governance"]["src_diff_empty"]
            and trace["governance"]["protected_runtime_contract_diff_empty"],
            trace["governance"],
        ),
        check(
            "artifact_manifest_exact",
            all(
                (ROOT / row["path"]).is_file()
                and sha256_file(ROOT / row["path"]) == row["sha256"]
                for row in artifact_manifest
            ),
            artifact_manifest,
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(trace), "recursive"),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_I9B1_response_shape_checks_failed"
        trace["classification"]["DR4_supported"] = False
    trace["output_digest"] = digest_value(trace)
    TRACE.write_text(canonical_json(trace), encoding="utf-8")

    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-B.1",
        "artifact_kind": "formation_and_bounded_export_response_candidate",
        "artifact_schema_version": "n31_i9b1_response_candidate_v1",
        "generated_at": GENERATED_AT,
        "status": trace["status"],
        "acceptance_state": trace["acceptance_state"],
        "command": COMMAND,
        "script": SCRIPT_RELATIVE,
        "source_trace": {
            "path": relative(TRACE),
            "sha256": sha256_file(TRACE),
            "output_digest": trace["output_digest"],
        },
        "result_summary": {
            "baseline_O_B": formation["route_before_formation"][
                "route_organization_O_B"
            ],
            "formed_O_B": formation["route_after_formation"][
                "route_organization_O_B"
            ],
            "formation_effect_O_B": formation["formation_effect_O_B"],
            "independent_native_progression_persistence_supported": persistence[
                "persistence_supported"
            ],
            "progression_authority": persistence["progression_authority"],
            "persistence_through_ordinary_state_mutating_activity": "not_tested",
            "q_emit_levels": [row["observed_q_emit"] for row in response["rows"]],
            "distinct_positive_q_levels": positive_levels,
            "all_response_equations_close": response[
                "all_response_equations_close"
            ],
            "zero_export_native_identity_unchanged": response[
                "zero_export_receipt"
            ]["zero_export_native_identity_unchanged"],
            "zero_export_closure_receipt_consumed": response[
                "zero_export_receipt"
            ]["zero_export_closure_receipt_consumed"],
            "zero_export_packet_created": response["zero_export_receipt"][
                "zero_export_packet_created"
            ],
            "B1_response_shape_scope": "monotonic_linear_through_cap_boundary",
            "I9B_inherited_above_cap_plateau_row_count": len(
                inherited_plateau_rows
            ),
            "I9B_inherited_above_cap_plateau_rows": inherited_plateau_rows,
            "all_boundary_shifts_equal_q_emit": readout[
                "all_boundary_shifts_equal_q_emit"
            ],
            "paired_boundary_shift_monotonic_non_decreasing": readout[
                "paired_boundary_shift_monotonic_non_decreasing"
            ],
            "mediation_strength": "bounded_partial_local_leakage_source_C",
        },
        "classification": trace["classification"],
        "governance": trace["governance"],
        "claim_boundary": {
            "allowed_claim": (
                "I9B1_strengthens_formation_attribution_persistence_and_response_"
                "shape_for_provisional_producer_mediated_B_R_DR4"
            ),
            "blocked_claims": [
                "producer_DR5",
                "producer_DR6",
                "ordinary_D0_R",
                "native_decay",
                "autonomous_persistence",
                "full_route_distribution_mediation",
                "trail_or_stigmergy",
                "communication",
                "ecology",
                "agency",
                "native_support",
            ],
            "unsafe_claim_flags": {
                "producer_DR5_claim_allowed": False,
                "producer_DR6_claim_allowed": False,
                "ordinary_D0_R_claim_allowed": False,
                "native_decay_claim_allowed": False,
                "autonomous_persistence_claim_allowed": False,
                "full_route_distribution_mediation_claim_allowed": False,
                "trail_or_stigmergy_claim_allowed": False,
                "communication_claim_allowed": False,
                "ecology_claim_allowed": False,
                "agency_claim_allowed": False,
                "native_support_claim_allowed": False,
            },
        },
        "I10_handoff": {
            "I9B_consumption_role": "core_positive_execution",
            "I9B1_consumption_role": (
                "complementary_formation_attribution_bounded_persistence_"
                "response_shape_and_boundary_shift_evidence"
            ),
            "I9B1_replaces_I9B": False,
            "formal_recursive_candidate_row_pending": True,
            "complete_60_control_matrix_pending": True,
            "receipt_event_mismatch_controls_inherited_from_I9B": True,
            "floating_boundary_rows_are_diagnostic": True,
            "DR5_pending": True,
        },
        "artifact_manifest": artifact_manifest,
        "checks": trace["checks"],
        "failed_checks": trace["failed_checks"],
    }
    payload["checks"].extend(
        [
            check(
                "unsafe_claim_flags_false",
                not any(payload["claim_boundary"]["unsafe_claim_flags"].values()),
                payload["claim_boundary"]["unsafe_claim_flags"],
            ),
            check(
                "I10_obligations_preserved",
                payload["I10_handoff"]["formal_recursive_candidate_row_pending"]
                and payload["I10_handoff"]["complete_60_control_matrix_pending"]
                and payload["I10_handoff"]["DR5_pending"]
                and payload["I10_handoff"]["I9B_consumption_role"]
                == "core_positive_execution"
                and payload["I10_handoff"]["I9B1_consumption_role"].startswith(
                    "complementary_"
                )
                and not payload["I10_handoff"]["I9B1_replaces_I9B"],
                payload["I10_handoff"],
            ),
        ]
    )
    payload["failed_checks"] = [
        row["check_id"] for row in payload["checks"] if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_I9B1_candidate_checks_failed"
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    result = payload["result_summary"]
    inherited_plateau_rows = ", ".join(
        f"C_source={row['source_C']} (excess={row['source_excess']}, "
        f"q_emit={row['observed_q_emit']})"
        for row in result["I9B_inherited_above_cap_plateau_rows"]
    )
    checks = "\n".join(
        f"| `{row['check_id']}` | {str(row['passed']).lower()} |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 9-B.1 - Formation Attribution And Bounded Export Response Shape

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
current rung = DR4 provisional
DR5_supported = false
D0-R bridge = not tested
native lane = D0a / DR2 unchanged
```

## Formation And Persistence

The native formation packet strengthens an existing route contrast rather than
creating it from zero:

```text
baseline O_B = {result['baseline_O_B']}
formed O_B = {result['formed_O_B']}
formation effect = {result['formation_effect_O_B']}
```

After formation exhausts, a boundary-birth trial on disjoint destination node 2
advances the native scheduler and checkpoint. Zero outward pressure produces no
topology event or topology mutation, and `O_B` remains unchanged through exact
snapshot/load. This is experiment-scheduled native progression evidence, not
autonomous persistence. The trial is nonqualifying, nonadmitted, and
state-neutral. Persistence through ordinary state-mutating native activity was
not tested.

## Bounded Export Shape

The exact Candidate B producer and topology are retained. Constant-route-mass
diagnostic source states produce:

```text
q_emit levels = {result['q_emit_levels']}
positive levels = {result['distinct_positive_q_levels']}
```

For every level, source debit, in-flight amount, destination credit, route-mass
decrease, and route-organization weakening equal `q_emit`. These source-state
rows test the policy response shape; they are not additional natural formation
trajectories.

I9-B.1 establishes a monotonic linear response through the `q_cap=0.04`
boundary; it does not independently test an above-cap plateau. The inherited
I9-B policy sweep supplies {result['I9B_inherited_above_cap_plateau_row_count']}
above-cap source-excess rows that remain clamped at `0.04`:
{inherited_plateau_rows}.

The zero-export row preserves byte-identical native snapshots while consuming
the one-shot closure receipt and creating no packet:

```text
zero_export_native_identity_unchanged = {str(result['zero_export_native_identity_unchanged']).lower()}
zero_export_closure_receipt_consumed = {str(result['zero_export_closure_receipt_consumed']).lower()}
zero_export_packet_created = {str(result['zero_export_packet_created']).lower()}
```

Every response row passes the preregistered native-state diff whitelist and
exact one-shot closure reset rule.

## Native Readout Boundary

Each no-export and export state is probed below, at, and above its local node-1
coherence boundary. Robust below-boundary requests admit, robust above-boundary
requests reject atomically, and floating-point-adjacent rows remain diagnostic.
The paired no-export-to-export admission-boundary shift equals `q_emit` at every
level and is monotonic across the response matrix.

The evidence remains bounded partial mediation by local leakage-source C. It
does not establish mediation by the complete route distribution.

## Evidence Lineage

I9-B.1 consumes corrected I9-B result digest `4427aa0c...` and trace digest
`65ac1e3a...`. A versioned lineage receipt retains the initially reviewed and
corrected identities, records the attribution and contract corrections, and
states that the scientific provisional `B-R / DR4` conclusion did not change.
Only the corrected identities are admissible for I9-B.1 and I10.

## Classification

I9-B.1 materially strengthens formation attribution, persistence scope, export
response shape, and downstream boundary attribution. It does not raise the
rung: Candidate B remains provisional producer-mediated `B-R / DR4`; `DR5`
still requires I10's formal recursive row and complete control matrix.
I9-B remains the core positive execution object; I9-B.1 is complementary shape
and attribution evidence rather than its replacement.

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
