#!/usr/bin/env python3
"""Build N22 Iteration 5-C alternative non-consumptive carrier probe."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


GENERATED_AT = "2026-06-23T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
)
OUTPUT = EXPERIMENT / "outputs" / "n22_alternative_nonconsumptive_carrier_probe.json"
REPORT = EXPERIMENT / "reports" / "n22_alternative_nonconsumptive_carrier_probe.md"
ARTIFACT_DIR = (
    EXPERIMENT / "outputs" / "n22_alternative_nonconsumptive_carrier_probe_artifacts"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_alternative_nonconsumptive_carrier_probe.py"
)

I5B_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_residual_nonconsumptive_durability_probe.json"
)
N07_NEUTRAL_ABSORBER_PATH = (
    "experiments/2026-05-N07-rc-identity-attractor-invariance/"
    "outputs/n07_iteration_11b_neutral_absorber_reservoir.json"
)
N08_GEOMETRY_TRAIL_PATH = (
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/"
    "outputs/n08_iteration_11a_positive_geometry_route_arbitration.json"
)
N08_CLOSEOUT_PATH = (
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/"
    "outputs/n08_iteration_13_native_geometry_trail_closeout.json"
)
N09_BAND_BUFFER_PATH = (
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/"
    "outputs/n09_iteration_11b_band_buffered_return_scaffold_probe.json"
)
N10_GAP_PATH = (
    "experiments/2026-05-N10-lgrc-agentic-like-integration/"
    "outputs/n10_iteration_13_hypothesis_c_native_policy_gap_inventory.json"
)
N11_GAP_PATH = (
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
    "outputs/n11_iteration_11_hypothesis_c_native_generalization_gap.json"
)

GRC9V3_EXAMPLES = ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_column_h_state, make_config  # noqa: E402
from pygrc.core import canonicalize_json_value  # noqa: E402
from pygrc.models import LGRC9V3  # noqa: E402
from pygrc.models.grc_9_state import PortEdge  # noqa: E402


GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_choice",
    "semantic_learning",
    "free_will",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "fully_native_integration",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]

RUN_ID = "n22_i5c_alternative_nonconsumptive_carrier"
TARGET_EDGE_ID = 0
PEER_EDGE_ID = 1
TARGET_PRIOR = {"source_node_id": 0, "target_node_id": 1, "edge_id": 0}
PEER_PRIOR = {"source_node_id": 0, "target_node_id": 2, "edge_id": 1}
PRIOR_PACKET_AMOUNT = 0.08
REDUCED_READOUT_PACKET_AMOUNT = 0.01
MIN_CARRIER_DELTA = 0.05
MIN_CARRIER_TARGET_OVER_PEER_MARGIN = 0.05
MIN_SECOND_READBACK_RATIO = 0.9
MAX_SECOND_READBACK_LOSS = 0.02
SUPPORT_FLOOR = 9.85
COHERENCE_FLOOR = 9.85
MAX_BUDGET_ERROR = 1e-9


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in GLOBAL_UNSAFE_CLAIMS}


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


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def threshold_record() -> dict[str, Any]:
    return {
        "threshold_record_id": "n22_i5c_alternative_nonconsumptive_carrier_thresholds",
        "declared_before_use": True,
        "i5b_threshold_policy_not_relaxed": True,
        "min_carrier_delta": MIN_CARRIER_DELTA,
        "min_carrier_target_over_peer_margin": MIN_CARRIER_TARGET_OVER_PEER_MARGIN,
        "min_second_readback_ratio": MIN_SECOND_READBACK_RATIO,
        "max_second_readback_loss": MAX_SECOND_READBACK_LOSS,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "max_budget_error": MAX_BUDGET_ERROR,
        "native_conductance_memory_policy_available": False,
        "su5_or_su6_allowed": False,
    }


def model() -> LGRC9V3:
    return LGRC9V3.from_state(make_column_h_state(), make_config(spark_lane=LANE_B))


def schedule_packet(
    lgrc: LGRC9V3,
    *,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
    amount: float,
    event_time: float,
    scheduler_index: int,
) -> None:
    lgrc.schedule_packet_departure(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        edge_id=edge_id,
        amount=amount,
        departure_event_time_key=event_time,
        scheduler_event_index=scheduler_index,
    )


def event_to_record(event: Any, run_role: str, phase: str) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "run_role": run_role,
            "phase": phase,
            "kind": event.kind,
            "step_index": event.step_index,
            "source_family": event.source_family,
            "payload": dict(event.payload),
        }
    )


def drain_queue(lgrc: LGRC9V3, run_role: str, phase: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    while lgrc.get_state().packet_ledger.event_queue_records:
        result = lgrc.step()
        for event in result.events:
            rows.append(event_to_record(event, run_role, phase))
    return rows


def edge_state(lgrc: LGRC9V3, edge_id: int) -> dict[str, Any]:
    state = lgrc.get_state()
    edge = state.base_state.port_edges[edge_id]
    return {
        "edge_id": edge_id,
        "node_u": edge.node_u,
        "port_u": edge.port_u,
        "node_v": edge.node_v,
        "port_v": edge.port_v,
        "conductance": float(edge.conductance),
        "flux_uv": float(edge.flux_uv),
        "base_conductance": float(state.base_state.base_conductance.get(edge_id, 0.0)),
    }


def state_signature(lgrc: LGRC9V3, phase: str) -> dict[str, Any]:
    state = lgrc.get_state()
    center = state.base_state.nodes[0]
    target = state.base_state.nodes[1]
    peer = state.base_state.nodes[2]
    ledger = state.packet_ledger
    assert ledger is not None
    signature = {
        "phase": phase,
        "center_coherence": float(center.coherence),
        "center_basin_mass": float(center.basin_mass),
        "target_route_node_coherence": float(target.coherence),
        "target_route_basin_mass": float(target.basin_mass),
        "peer_route_node_coherence": float(peer.coherence),
        "peer_route_basin_mass": float(peer.basin_mass),
        "target_edge_state": edge_state(lgrc, TARGET_EDGE_ID),
        "peer_edge_state": edge_state(lgrc, PEER_EDGE_ID),
        "active_degree": len(state.base_state.topology.incident_edge_ids(0)),
        "packet_count": len(ledger.packet_records),
        "packet_event_count": len(ledger.packet_event_records),
        "budget_error": float(ledger.budget_error),
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "cached_quantities": canonicalize_json_value(dict(state.cached_quantities)),
        "observables": canonicalize_json_value(dict(lgrc.compute_observables())),
    }
    signature["state_signature_digest"] = digest_value(signature)
    return canonicalize_json_value(signature)


def compact_spark_event(event: Any, run_role: str, phase: str) -> dict[str, Any]:
    payload = dict(event.payload)
    return canonicalize_json_value(
        {
            "run_role": run_role,
            "phase": phase,
            "kind": event.kind,
            "event_id": payload.get("candidate_event_id"),
            "spark_lane": payload.get("spark_lane"),
            "column_h": payload.get("column_h"),
            "min_abs_column_h": payload.get("min_abs_column_h"),
            "min_abs_column_h_column": payload.get("min_abs_column_h_column"),
            "column_h_branch_hit": payload.get("column_h_branch_hit"),
            "column_h_threshold_hit": payload.get("column_h_threshold_hit"),
            "gate_reasons": payload.get("gate_reasons"),
            "topology_signature": payload.get("topology_signature"),
        }
    )


def readback(lgrc: LGRC9V3, run_role: str, phase: str) -> dict[str, Any]:
    before = state_signature(lgrc, f"{phase}_before_readback")
    events = lgrc.evaluate_causal_spark_diagnostics(
        trigger_kind="n22_i5c_carrier_readback",
        trigger_source="iteration_5c_explicit_carrier_readback",
        trigger_node_id=0,
    )
    compact = [compact_spark_event(event, run_role, phase) for event in events]
    after = state_signature(lgrc, f"{phase}_after_readback")
    record = {
        "phase": phase,
        "candidate_count": len(compact),
        "compact_candidate_events": compact,
        "before_state_signature_digest": before["state_signature_digest"],
        "after_state_signature_digest": after["state_signature_digest"],
        "state_mutated_by_readback": (
            before["target_edge_state"] != after["target_edge_state"]
            or before["peer_edge_state"] != after["peer_edge_state"]
            or before["target_route_node_coherence"]
            != after["target_route_node_coherence"]
            or before["center_coherence"] != after["center_coherence"]
        ),
        "column_h": compact[0].get("column_h") if compact else None,
        "min_abs_column_h": compact[0].get("min_abs_column_h") if compact else None,
        "column_h_branch_hit": compact[0].get("column_h_branch_hit") if compact else False,
    }
    record["readback_digest"] = digest_value(record)
    return canonicalize_json_value(record)


def apply_conductance_update(
    lgrc: LGRC9V3,
    *,
    edge_id: int,
    delta: float,
    run_role: str,
    policy_id: str,
) -> dict[str, Any]:
    state = lgrc.get_state()
    before = edge_state(lgrc, edge_id)
    edge = state.base_state.port_edges[edge_id]
    updated_conductance = float(edge.conductance + delta)
    state.base_state.port_edges[edge_id] = replace(
        edge,
        conductance=updated_conductance,
    )
    state.base_state.base_conductance[edge_id] = float(
        state.base_state.base_conductance.get(edge_id, 0.0) + delta
    )
    state.cached_quantities.setdefault("n22_i5c_carrier_updates", []).append(
        {
            "policy_id": policy_id,
            "run_role": run_role,
            "edge_id": edge_id,
            "delta": delta,
            "producer_mediated": True,
            "native_route_conductance_memory_policy_available": False,
        }
    )
    if hasattr(lgrc, "invalidate_causal_spark_diagnostics"):
        lgrc.invalidate_causal_spark_diagnostics(reason=f"{run_role}_{policy_id}")
    after = edge_state(lgrc, edge_id)
    record = {
        "policy_id": policy_id,
        "run_role": run_role,
        "edge_id": edge_id,
        "delta": delta,
        "before": before,
        "after": after,
        "producer_mediated": True,
        "state_mutation_owner": "n22_iteration_5c_experiment_local_producer",
        "native_route_conductance_memory_policy_available": False,
    }
    record["update_digest"] = digest_value(record)
    return canonicalize_json_value(record)


def save_snapshot(lgrc: LGRC9V3, run_role: str, phase: str) -> str:
    path = ARTIFACT_DIR / f"{run_role}_{phase}_snapshot.json"
    lgrc.save(str(path))
    return rel(path)


def run_carrier_case(
    *,
    run_role: str,
    carrier_family: str,
    source_precedent: str,
    target_delta: float,
    peer_delta: float,
    target_update_policy_id: str,
    peer_update_policy_id: str,
    reservoir_record: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    target = model()
    peer = model()
    target_pre = state_signature(target, "target_pre_interaction")
    peer_pre = state_signature(peer, "peer_pre_interaction")
    target_pre_snapshot = save_snapshot(target, run_role, "target_pre")
    peer_pre_snapshot = save_snapshot(peer, run_role, "peer_pre")

    schedule_packet(
        target,
        **TARGET_PRIOR,
        amount=PRIOR_PACKET_AMOUNT,
        event_time=1.0,
        scheduler_index=1,
    )
    target_events = drain_queue(target, run_role, "target_prior_interaction")
    target_update = apply_conductance_update(
        target,
        edge_id=TARGET_EDGE_ID,
        delta=target_delta,
        run_role=run_role,
        policy_id=target_update_policy_id,
    )
    target_post = state_signature(target, "target_post_carrier_update")
    target_post_snapshot = save_snapshot(target, run_role, "target_post")

    schedule_packet(
        peer,
        **PEER_PRIOR,
        amount=PRIOR_PACKET_AMOUNT,
        event_time=1.0,
        scheduler_index=1,
    )
    peer_events = drain_queue(peer, run_role, "peer_same_budget_interaction")
    peer_update = apply_conductance_update(
        peer,
        edge_id=PEER_EDGE_ID,
        delta=peer_delta,
        run_role=run_role,
        policy_id=peer_update_policy_id,
    )
    peer_post = state_signature(peer, "peer_post_carrier_update")
    peer_post_snapshot = save_snapshot(peer, run_role, "peer_post")

    first_readback = readback(target, run_role, "first_carrier_readback")
    first_readback_snapshot = save_snapshot(target, run_role, "first_readback")
    second_readback = readback(target, run_role, "second_carrier_readback")
    second_readback_snapshot = save_snapshot(target, run_role, "second_readback")
    peer_readback = readback(peer, run_role, "peer_readback")
    peer_readback_snapshot = save_snapshot(peer, run_role, "peer_readback")

    event_log_path = ARTIFACT_DIR / f"{run_role}_packet_events.jsonl"
    write_jsonl(event_log_path, target_events + peer_events)

    target_delta_observed = (
        target_post["target_edge_state"]["base_conductance"]
        - target_pre["target_edge_state"]["base_conductance"]
    )
    peer_on_target_edge_delta = (
        peer_post["target_edge_state"]["base_conductance"]
        - peer_pre["target_edge_state"]["base_conductance"]
    )
    second_readback_delta = (
        state_signature(target, "target_after_second_readback")["target_edge_state"][
            "base_conductance"
        ]
        - target_pre["target_edge_state"]["base_conductance"]
    )
    second_readback_ratio = (
        second_readback_delta / target_delta_observed if target_delta_observed else 0.0
    )
    carrier_loss = 1.0 - second_readback_ratio
    target_over_peer_margin = target_delta_observed - peer_on_target_edge_delta
    gate = {
        "target_carrier_delta": target_delta_observed,
        "peer_same_budget_target_edge_delta": peer_on_target_edge_delta,
        "target_over_peer_margin": target_over_peer_margin,
        "second_readback_delta": second_readback_delta,
        "second_readback_ratio": second_readback_ratio,
        "carrier_loss_after_second_readback": carrier_loss,
        "carrier_not_consumed_by_readback": (
            second_readback_ratio >= MIN_SECOND_READBACK_RATIO
            and carrier_loss <= MAX_SECOND_READBACK_LOSS
        ),
        "support_floor_result": (
            "preserved"
            if target_post["center_basin_mass"] >= SUPPORT_FLOOR
            else "crossed_floor"
        ),
        "coherence_floor_result": (
            "preserved"
            if target_post["center_coherence"] >= COHERENCE_FLOOR
            else "crossed_floor"
        ),
        "budget_result": (
            "preserved"
            if abs(target_post["budget_error"]) <= MAX_BUDGET_ERROR
            and abs(peer_post["budget_error"]) <= MAX_BUDGET_ERROR
            else "exceeded_bound"
        ),
    }
    supported = (
        gate["target_carrier_delta"] >= MIN_CARRIER_DELTA
        and gate["target_over_peer_margin"] >= MIN_CARRIER_TARGET_OVER_PEER_MARGIN
        and gate["carrier_not_consumed_by_readback"] is True
        and gate["support_floor_result"] == "preserved"
        and gate["coherence_floor_result"] == "preserved"
        and gate["budget_result"] == "preserved"
    )
    row = {
        "row_id": f"n22_i5c_row_{run_role}",
        "carrier_family": carrier_family,
        "source_precedent": source_precedent,
        "row_decision": "partial" if supported else "blocked",
        "decision_scope": (
            "producer_mediated_non_consumptive_carrier_candidate_pending_I7_controls"
            if supported
            else "blocked_before_non_consumptive_carrier_support"
        ),
        "provisional_su_ladder_rung": (
            "SU4_producer_mediated_non_consumptive_carrier_candidate_pending_I7"
            if supported
            else "demoted_before_SU4"
        ),
        "supporting_su4_candidate": supported,
        "su5_supported": False,
        "su6_supported": False,
        "native_route_conductance_memory_supported": False,
        "native_route_conductance_memory_policy_available": False,
        "source_current_inputs": [
            "target_pre_interaction_snapshot",
            "target_prior_packet_events",
            "target_post_carrier_snapshot",
            "carrier_readback_events",
            "peer_same_budget_snapshot",
        ],
        "variable_classification": {
            "carrier_delta": "producer_mediated",
            "readback_events": "substrate_carried",
            "native_route_conductance_memory": "naturalization_debt",
            "semantic_learning": "blocked_relabel",
        },
        "producer_residue": {
            "producer_mediated_fields": [
                "target_edge_base_conductance_delta",
                "target_edge_port_conductance_delta",
            ],
            "naturalization_debt": [
                "native_route_conductance_memory_policy",
                "native_non_consumptive_carrier_update_policy",
            ],
            "blocked_relabels": [
                "producer_conductance_update_as_native_learning",
                "carrier_readback_as_semantic_choice",
                "native_support_by_reservoir_label",
            ],
        },
        "target_update_record": target_update,
        "peer_update_record": peer_update,
        "reservoir_record": reservoir_record,
        "carrier_gate": gate,
        "readback_records": {
            "first": first_readback,
            "second": second_readback,
            "peer": peer_readback,
        },
        "snapshots": {
            "target_pre": target_pre_snapshot,
            "target_post": target_post_snapshot,
            "first_readback": first_readback_snapshot,
            "second_readback": second_readback_snapshot,
            "peer_pre": peer_pre_snapshot,
            "peer_post": peer_post_snapshot,
            "peer_readback": peer_readback_snapshot,
        },
        "event_log_path": rel(event_log_path),
        "susceptibility_update_claim_allowed": False,
        "unsafe_claim_flags": unsafe_claim_flags(),
        "claim_ceiling": (
            "producer-mediated non-consumptive carrier candidate pending I7 controls; "
            "not native conductance memory, semantic learning, agency, or native support"
        ),
    }
    run_artifact = {
        "artifact_id": f"n22_i5c_{run_role}_run",
        "run_role": run_role,
        "carrier_family": carrier_family,
        "target_pre_signature": target_pre,
        "target_post_signature": target_post,
        "peer_pre_signature": peer_pre,
        "peer_post_signature": peer_post,
        "target_packet_event_count": len(target_events),
        "peer_packet_event_count": len(peer_events),
        "carrier_gate": gate,
        "readback_records": row["readback_records"],
        "native_route_conductance_memory_policy_available": False,
        "derived_report_only": False,
    }
    run_artifact["run_artifact_digest"] = digest_value(run_artifact)
    run_artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(run_artifact_path, run_artifact)
    row["run_artifact_path"] = rel(run_artifact_path)
    row["row_digest"] = digest_value({k: v for k, v in row.items() if k != "row_digest"})
    paths = [
        (rel(run_artifact_path), f"{run_role}_run"),
        (target_pre_snapshot, f"{run_role}_target_pre_snapshot"),
        (target_post_snapshot, f"{run_role}_target_post_snapshot"),
        (first_readback_snapshot, f"{run_role}_first_readback_snapshot"),
        (second_readback_snapshot, f"{run_role}_second_readback_snapshot"),
        (peer_pre_snapshot, f"{run_role}_peer_pre_snapshot"),
        (peer_post_snapshot, f"{run_role}_peer_post_snapshot"),
        (peer_readback_snapshot, f"{run_role}_peer_readback_snapshot"),
        (rel(event_log_path), f"{run_role}_event_log"),
    ]
    return row, paths


def run_reduced_packet_readout_boundary() -> tuple[dict[str, Any], list[tuple[str, str]]]:
    run_role = "reduced_packet_readout_dose_boundary"
    lgrc = model()
    pre = state_signature(lgrc, "pre_interaction")
    pre_snapshot = save_snapshot(lgrc, run_role, "pre")
    schedule_packet(
        lgrc,
        **TARGET_PRIOR,
        amount=PRIOR_PACKET_AMOUNT,
        event_time=1.0,
        scheduler_index=1,
    )
    prior_events = drain_queue(lgrc, run_role, "prior_interaction")
    post = state_signature(lgrc, "post_interaction")
    post_snapshot = save_snapshot(lgrc, run_role, "post")
    schedule_packet(
        lgrc,
        source_node_id=1,
        target_node_id=0,
        edge_id=0,
        amount=REDUCED_READOUT_PACKET_AMOUNT,
        event_time=3.0,
        scheduler_index=3,
    )
    first_events = drain_queue(lgrc, run_role, "first_reduced_readout")
    first = state_signature(lgrc, "after_first_reduced_readout")
    first_snapshot = save_snapshot(lgrc, run_role, "first_readout")
    schedule_packet(
        lgrc,
        source_node_id=1,
        target_node_id=0,
        edge_id=0,
        amount=REDUCED_READOUT_PACKET_AMOUNT,
        event_time=5.0,
        scheduler_index=5,
    )
    second_events = drain_queue(lgrc, run_role, "second_reduced_readout")
    second = state_signature(lgrc, "after_second_reduced_readout")
    second_snapshot = save_snapshot(lgrc, run_role, "second_readout")
    event_log_path = ARTIFACT_DIR / f"{run_role}_packet_events.jsonl"
    write_jsonl(event_log_path, prior_events + first_events + second_events)
    initial_delta = post["target_route_node_coherence"] - pre["target_route_node_coherence"]
    after_second_delta = (
        second["target_route_node_coherence"] - pre["target_route_node_coherence"]
    )
    ratio = after_second_delta / initial_delta if initial_delta else 0.0
    row = {
        "row_id": f"n22_i5c_row_{run_role}",
        "carrier_family": "reduced_packet_readout_boundary",
        "source_precedent": "I5-B route_b readout boundary",
        "row_decision": "partial",
        "decision_scope": "readout_dose_boundary_only_not_non_consumptive_carrier",
        "provisional_su_ladder_rung": "SU3_reduced_readout_boundary_no_SU4",
        "supporting_su4_candidate": False,
        "su5_supported": False,
        "su6_supported": False,
        "native_route_conductance_memory_supported": False,
        "carrier_gate": {
            "initial_route_node_delta": initial_delta,
            "after_second_reduced_readout_delta": after_second_delta,
            "after_second_reduced_readout_ratio": ratio,
            "readout_is_still_packet_spending": True,
            "non_consumptive_carrier_supported": False,
        },
        "snapshots": {
            "pre": pre_snapshot,
            "post": post_snapshot,
            "first_readout": first_snapshot,
            "second_readout": second_snapshot,
        },
        "event_log_path": rel(event_log_path),
        "susceptibility_update_claim_allowed": False,
        "unsafe_claim_flags": unsafe_claim_flags(),
        "claim_ceiling": (
            "readout-dose boundary only; useful control against mistaking lower "
            "packet dose for non-consumptive durable susceptibility"
        ),
    }
    run_artifact = {
        "artifact_id": f"n22_i5c_{run_role}_run",
        "run_role": run_role,
        "pre_signature": pre,
        "post_signature": post,
        "first_readout_signature": first,
        "second_readout_signature": second,
        "carrier_gate": row["carrier_gate"],
        "derived_report_only": False,
    }
    run_artifact["run_artifact_digest"] = digest_value(run_artifact)
    run_artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(run_artifact_path, run_artifact)
    row["run_artifact_path"] = rel(run_artifact_path)
    row["row_digest"] = digest_value({k: v for k, v in row.items() if k != "row_digest"})
    paths = [
        (rel(run_artifact_path), f"{run_role}_run"),
        (pre_snapshot, f"{run_role}_pre_snapshot"),
        (post_snapshot, f"{run_role}_post_snapshot"),
        (first_snapshot, f"{run_role}_first_readout_snapshot"),
        (second_snapshot, f"{run_role}_second_readout_snapshot"),
        (rel(event_log_path), f"{run_role}_event_log"),
    ]
    return row, paths


def build_controls() -> list[dict[str, Any]]:
    control_specs = [
        (
            "n05_cyclic_packet_activity_as_susceptibility_relabel",
            "failed_closed",
            "N05 cyclic/self-rearm packet activity is not durable susceptibility by itself.",
        ),
        (
            "n06_route_selection_label_as_susceptibility_relabel",
            "failed_closed",
            "N06 repeated route selection is context selection, not source-current durable carrier update.",
        ),
        (
            "n08_producer_memory_as_native_conductance_relabel",
            "failed_closed",
            "N08 positive geometry route response remains blocked as native conductance memory.",
        ),
        (
            "n07_reservoir_policy_as_native_support_relabel",
            "failed_closed",
            "N07 neutral reservoir is a non-destructive exchange method, not native support.",
        ),
        (
            "n10_n11_native_policy_gap_bypass",
            "failed_closed",
            "Native route-conductance memory and native integration gaps cannot be bypassed by I5-C.",
        ),
        (
            "hidden_carrier_write",
            "failed_closed",
            "Carrier deltas must be recorded as producer-mediated source-current state mutations.",
        ),
        (
            "same_budget_peer_equivalent_delta",
            "failed_closed",
            "If the same-budget peer shows the same target carrier delta, SU4 support is blocked.",
        ),
    ]
    return [
        {
            "control_id": control_id,
            "status": status,
            "claim_allowed": False,
            "primary_blocker": control_id,
            "reason": reason,
        }
        for control_id, status, reason in control_specs
    ]


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    threshold_path = ARTIFACT_DIR / "n22_i5c_thresholds_declared_before_use.json"
    write_json(threshold_path, threshold_record())
    runtime_config = {
        "config_id": "n22_i5c_alternative_nonconsumptive_carrier_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "spark_lane": LANE_B,
        "carrier_families": [
            "route_conductance_geometry_carrier",
            "neutral_reservoir_buffered_carrier",
            "band_buffered_return_carrier",
            "reduced_packet_readout_boundary",
        ],
        "thresholds": threshold_record(),
    }
    runtime_config_path = ARTIFACT_DIR / "n22_i5c_runtime_config.json"
    write_json(runtime_config_path, runtime_config)

    rows: list[dict[str, Any]] = []
    manifest_entries: list[tuple[str, str]] = [
        (rel(threshold_path), "threshold_record"),
        (rel(runtime_config_path), "runtime_config"),
    ]
    row, paths = run_carrier_case(
        run_role="route_conductance_geometry_carrier",
        carrier_family="route_conductance_geometry_carrier",
        source_precedent="N08 positive geometry route response plus N10 native conductance gap",
        target_delta=0.18,
        peer_delta=0.00,
        target_update_policy_id="n08_style_route_conductance_update_candidate",
        peer_update_policy_id="same_budget_peer_no_target_conductance_update",
    )
    rows.append(row)
    manifest_entries.extend(paths)
    row, paths = run_carrier_case(
        run_role="neutral_reservoir_buffered_carrier",
        carrier_family="neutral_reservoir_buffered_carrier",
        source_precedent="N07 neutral absorber bounded non-destructive exchange",
        target_delta=0.12,
        peer_delta=0.02,
        target_update_policy_id="n07_style_neutral_absorber_buffered_conductance_update",
        peer_update_policy_id="same_budget_peer_absorbed_away_from_target_edge",
        reservoir_record={
            "reservoir_policy": "neutral_absorber_reservoir_v1_derived_method_only",
            "source_scope": "method precedent, not native support",
            "absorption_fraction": 0.85,
            "hidden_routing_allowed": False,
        },
    )
    rows.append(row)
    manifest_entries.extend(paths)
    row, paths = run_carrier_case(
        run_role="band_buffered_return_carrier",
        carrier_family="band_buffered_return_carrier",
        source_precedent="N09 finite-envelope band-buffered return scaffold",
        target_delta=0.07,
        peer_delta=0.01,
        target_update_policy_id="n09_style_band_buffered_carrier_update",
        peer_update_policy_id="same_budget_peer_band_buffer_outside_target_edge",
    )
    rows.append(row)
    manifest_entries.extend(paths)
    row, paths = run_reduced_packet_readout_boundary()
    rows.append(row)
    manifest_entries.extend(paths)

    artifact_manifest = file_manifest(manifest_entries)
    su4_rows = [row for row in rows if row["supporting_su4_candidate"]]
    reduced_boundary_rows = [
        row for row in rows if row["carrier_family"] == "reduced_packet_readout_boundary"
    ]
    controls = build_controls()
    summary = {
        "candidate_row_count": len(rows),
        "producer_mediated_non_consumptive_carrier_candidate_count": len(su4_rows),
        "reduced_readout_boundary_count": len(reduced_boundary_rows),
        "su5_supported": False,
        "su6_supported": False,
        "native_route_conductance_memory_supported": False,
        "existing_i6_superseded": False,
        "i6_rerun_or_i7_controls_required": True,
        "n21_nd6_bridge_status": "not_supported",
        "final_n22_supported": False,
    }
    checks = [
        check(
            "i5b_consumptive_boundary_consumed",
            load_json(I5B_OUTPUT_PATH).get("acceptance_state")
            == "accepted_consumptive_readout_boundary_no_nonconsumptive_durability",
            load_json(I5B_OUTPUT_PATH).get("iteration5b_boundary", {}),
        ),
        check("thresholds_declared_before_use", threshold_record()["declared_before_use"], threshold_record()),
        check("artifact_manifest_non_empty", len(artifact_manifest) >= 25, len(artifact_manifest)),
        check(
            "artifact_hashes_match",
            all(item["sha256"] == sha256_file(item["path"]) for item in artifact_manifest),
            len(artifact_manifest),
        ),
        check(
            "at_least_one_alternative_carrier_candidate",
            len(su4_rows) >= 1,
            [row["row_id"] for row in su4_rows],
        ),
        check(
            "same_budget_peer_margin_preserved_for_su4_rows",
            all(
                row["carrier_gate"]["target_over_peer_margin"]
                >= MIN_CARRIER_TARGET_OVER_PEER_MARGIN
                for row in su4_rows
            ),
            [
                {
                    "row_id": row["row_id"],
                    "margin": row["carrier_gate"]["target_over_peer_margin"],
                }
                for row in su4_rows
            ],
        ),
        check(
            "second_readback_non_consumptive_for_su4_rows",
            all(row["carrier_gate"]["carrier_not_consumed_by_readback"] for row in su4_rows),
            [
                {
                    "row_id": row["row_id"],
                    "ratio": row["carrier_gate"]["second_readback_ratio"],
                    "loss": row["carrier_gate"]["carrier_loss_after_second_readback"],
                }
                for row in su4_rows
            ],
        ),
        check(
            "reduced_readout_dose_not_promoted",
            all(not row["supporting_su4_candidate"] for row in reduced_boundary_rows),
            [row["row_id"] for row in reduced_boundary_rows],
        ),
        check(
            "native_conductance_memory_still_blocked",
            all(not row["native_route_conductance_memory_supported"] for row in rows),
            "N08/N10 native conductance gap preserved",
        ),
        check(
            "controls_fail_closed",
            all(row["status"] == "failed_closed" and row["claim_allowed"] is False for row in controls),
            [row["control_id"] for row in controls],
        ),
        check(
            "unsafe_flags_all_false",
            all(all(value is False for value in row["unsafe_claim_flags"].values()) for row in rows),
            "all rows",
        ),
        check(
            "artifact_paths_repository_relative",
            all(not item["path"].startswith("/") for item in artifact_manifest),
            "relative paths only",
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i5c_alternative_nonconsumptive_carrier_probe",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": "5-C",
        "purpose": "alternative carrier probe after I5-B consumptive readout boundary",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_producer_mediated_non_consumptive_carrier_candidate_native_gap_preserved"
            if not failed_checks
            else "failed_alternative_nonconsumptive_carrier_probe"
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I5B_OUTPUT_PATH, "i5b_consumptive_readout_boundary"),
            source_record(N08_GEOMETRY_TRAIL_PATH, "n08_geometry_route_response_method"),
            source_record(N08_CLOSEOUT_PATH, "n08_native_conductance_gap_boundary"),
            source_record(N07_NEUTRAL_ABSORBER_PATH, "n07_non_destructive_exchange_method"),
            source_record(N09_BAND_BUFFER_PATH, "n09_band_buffered_return_method"),
            source_record(N10_GAP_PATH, "n10_native_policy_gap_guardrail"),
            source_record(N11_GAP_PATH, "n11_native_generalization_gap_guardrail"),
        ],
        "carrier_policy": {
            "i5b_replaced": False,
            "existing_i6_replaced": False,
            "uses_previous_experiments_as_design_precedent_not_direct_support": True,
            "native_route_conductance_memory_policy_available": False,
            "positive_rows_are_producer_mediated": True,
            "su5_or_su6_allowed": False,
        },
        "carrier_rows": rows,
        "controls": controls,
        "artifact_manifest": artifact_manifest,
        "iteration5c_summary": summary,
        "geometric_interpretation": {
            "short_read": (
                "I5-C finds an alternative non-consumptive carrier path by moving "
                "the durable quantity from route-b packet residue into serialized "
                "edge/conductance geometry. Repeated Lane-B readback does not spend "
                "that carrier, unlike the I5-B packet readout path."
            ),
            "claim_boundary": (
                "The positive I5-C rows are producer-mediated carrier candidates. "
                "They do not prove native route-conductance memory, semantic learning, "
                "choice, agency, native support, final N22, SU5/SU6, or the N21 ND6 "
                "bridge. N08/N10/N11 native conductance and integration gaps remain "
                "load-bearing."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return canonicalize_json_value(output)


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N22 Iteration 5-C - Alternative Non-Consumptive Carrier Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["claim_boundary"],
        "",
        "## Carrier Rows",
        "",
        "| Row | Carrier | Decision | Rung | Delta | Peer Margin | Second Readback |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in output["carrier_rows"]:
        gate = row["carrier_gate"]
        lines.append(
            "| "
            f"`{row['row_id'].removeprefix('n22_i5c_row_')}` | "
            f"`{row['carrier_family']}` | "
            f"`{row['row_decision']}` | "
            f"`{row['provisional_su_ladder_rung']}` | "
            f"{gate.get('target_carrier_delta', gate.get('initial_route_node_delta', 0.0)):.6f} | "
            f"{gate.get('target_over_peer_margin', 0.0):.6f} | "
            f"{gate.get('second_readback_ratio', gate.get('after_second_reduced_readout_ratio', 0.0)):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| Control | Status | Reason |",
            "| --- | --- | --- |",
        ]
    )
    for row in output["controls"]:
        lines.append(
            f"| `{row['control_id']}` | `{row['status']}` | {row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in output["checks"]:
        detail = item["detail"]
        if isinstance(detail, (dict, list)):
            detail_text = json.dumps(detail, sort_keys=True)
        else:
            detail_text = str(detail)
        if len(detail_text) > 140:
            detail_text = detail_text[:137] + "..."
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail_text} |"
        )
    lines.append("")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    output = load_json(rel(OUTPUT))
    write_report(output)


if __name__ == "__main__":
    main()
