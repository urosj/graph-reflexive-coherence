#!/usr/bin/env python3
"""Build N22 Iteration 5-B residual / non-consumptive durability probe."""

from __future__ import annotations

from collections import Counter
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
OUTPUT = EXPERIMENT / "outputs" / "n22_residual_nonconsumptive_durability_probe.json"
REPORT = EXPERIMENT / "reports" / "n22_residual_nonconsumptive_durability_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_residual_nonconsumptive_durability_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_residual_nonconsumptive_durability_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_residual_nonconsumptive_durability_probe.py"
)

I5_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_durability_replay_probe.json"
)
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_replay_durability_stress_probe.json"
)

GRC9V3_EXAMPLES = ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from pygrc.core import canonicalize_json_value  # noqa: E402
from pygrc.models import LGRC9V3  # noqa: E402
from pygrc.telemetry import RunTelemetryIdentity, build_lgrc9v3_graph_checkpoint  # noqa: E402
from pygrc.telemetry.io import save_graph_checkpoint  # noqa: E402


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

RUN_ID = "n22_i5b_residual_nonconsumptive_lgrc9v3"
TARGET_ROUTE = {
    "route_id": "route_b",
    "reentry_source_node_id": 1,
    "reentry_target_node_id": 0,
    "edge_id": 0,
}
REENTRY_PACKET_AMOUNT = 0.04
SUPPORT_FLOOR = 9.85
COHERENCE_FLOOR = 9.85
BOUNDARY_ACTIVE_DEGREE_FLOOR = 9
MAX_BUDGET_ERROR = 1e-9
MIN_RESIDUAL_DELTA_PERSISTENCE_RATIO = 0.45
MAX_RATIO_LOSS_AFTER_SECOND_READOUT = 0.10


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


def threshold_record() -> dict[str, Any]:
    return {
        "threshold_record_id": "n22_i5b_residual_nonconsumptive_thresholds",
        "declared_before_use": True,
        "inherits_i5_threshold_policy": True,
        "consumes_i5a_repeated_reentry_boundary": True,
        "min_residual_delta_persistence_ratio": MIN_RESIDUAL_DELTA_PERSISTENCE_RATIO,
        "max_ratio_loss_after_second_readout": MAX_RATIO_LOSS_AFTER_SECOND_READOUT,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "boundary_active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
        "max_budget_error": MAX_BUDGET_ERROR,
        "reentry_packet_amount": REENTRY_PACKET_AMOUNT,
        "durable_su4_or_stronger_allowed": False,
    }


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


def step_summary(result: Any, run_role: str, phase: str) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "run_role": run_role,
            "phase": phase,
            "step_index": result.step_index,
            "time": result.time,
            "event_kinds": [event.kind for event in result.events],
            "bookkeeping": dict(result.bookkeeping),
            "observables": dict(result.observables),
        }
    )


def topology_signature(state: Any) -> dict[str, Any]:
    ledger = state.packet_ledger
    assert ledger is not None
    return canonicalize_json_value(ledger.fixed_topology_signature)


def basin_signature(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    topology = topology_signature(state)
    signature = {
        "center_node_id": 0,
        "center_basin_id": center.basin_id,
        "center_depth": center.depth,
        "center_coherence": center.coherence,
        "center_basin_mass": center.basin_mass,
        "incident_edge_ids": list(state.base_state.topology.incident_edge_ids(0)),
        "active_degree": len(state.base_state.topology.incident_edge_ids(0)),
        "node_count": len(state.base_state.nodes),
        "edge_count": len(state.base_state.port_edges),
        "basin_members": sorted(state.base_state.basins.get(0, set())),
        "topology_signature": topology,
    }
    signature["basin_signature_digest"] = digest_value(signature)
    return canonicalize_json_value(signature)


def route_geometry(model: LGRC9V3, run_role: str, phase: str) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    route_node = state.base_state.nodes[TARGET_ROUTE["reentry_source_node_id"]]
    ledger = state.packet_ledger
    assert ledger is not None
    packet_records = [record.to_record() for record in ledger.packet_records]
    event_records = [record.to_record() for record in ledger.packet_event_records]
    geometry = {
        "run_role": run_role,
        "phase": phase,
        "center_node_id": 0,
        "center_node_coherence": center.coherence,
        "center_basin_mass": center.basin_mass,
        "target_route_id": TARGET_ROUTE["route_id"],
        "target_route_node_id": TARGET_ROUTE["reentry_source_node_id"],
        "target_route_node_coherence": route_node.coherence,
        "target_route_basin_mass": route_node.basin_mass,
        "active_degree": len(state.base_state.topology.incident_edge_ids(0)),
        "node_count": len(state.base_state.nodes),
        "edge_count": len(state.base_state.port_edges),
        "event_time_key": state.event_time_key,
        "scheduler_event_index": state.scheduler_event_index,
        "checkpoint_index": state.checkpoint_index,
        "packet_count": len(packet_records),
        "packet_records": packet_records,
        "packet_event_records": event_records,
        "budget_error": ledger.budget_error,
        "in_flight_packet_total": ledger.in_flight_packet_total,
        "queued_packet_count": len(ledger.event_queue_records),
        "conserved_budget_total": ledger.conserved_budget_total,
        "topology_signature": topology_signature(state),
        "basin_signature": basin_signature(model),
        "observables": dict(model.compute_observables()),
    }
    geometry["geometry_digest"] = digest_value(geometry)
    return canonicalize_json_value(geometry)


def save_checkpoint(
    model: LGRC9V3,
    *,
    run_role: str,
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str,
    event_counts: dict[str, int] | None = None,
) -> str:
    identity = RunTelemetryIdentity(
        run_id=f"{RUN_ID}_{run_role}",
        model_family="LGRC9V3",
        params_identity=model.get_params().params_hash,
        seed_name="n22-column-h-residual-durability-fixture",
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="n22_residual_nonconsumptive_durability_probe",
        rng_seed=None,
        requested_steps=10,
    )
    checkpoint = build_lgrc9v3_graph_checkpoint(
        model,
        identity=identity,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        checkpoint_reason=checkpoint_reason,
        event_count_window=0 if event_counts is None else sum(event_counts.values()),
        event_counts_by_kind_window={} if event_counts is None else event_counts,
    )
    path = ARTIFACT_DIR / f"{checkpoint_id}.json"
    save_graph_checkpoint(path, checkpoint)
    return rel(path)


def schedule_packet(
    model: LGRC9V3,
    *,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
    amount: float,
    departure_event_time_key: float,
    scheduler_event_index: int,
) -> None:
    model.schedule_packet_departure(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        edge_id=edge_id,
        amount=amount,
        departure_event_time_key=departure_event_time_key,
        scheduler_event_index=scheduler_event_index,
    )


def drain_queue(
    model: LGRC9V3,
    run_role: str,
    phase: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    step_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        step_rows.append(step_summary(result, run_role, phase))
        event_rows.extend(event_to_record(event, run_role, phase) for event in result.events)
    return step_rows, event_rows


def source_trace_values(row: dict[str, Any]) -> dict[str, float]:
    trace = load_json(row["source_trace_artifact_path"])
    pre = trace["pre_interaction_geometry_trace"]
    source_sig = row["duplicate_replay"]["source_signature"]
    return {
        "pre_target_route_node_coherence": pre["target_route_node_coherence"],
        "source_target_route_delta": source_sig["target_route_delta"],
    }


def residual_ratio(geometry: dict[str, Any], source_values: dict[str, float]) -> float:
    source_delta = source_values["source_target_route_delta"]
    if not source_delta:
        return 0.0
    residual_delta = (
        geometry["target_route_node_coherence"]
        - source_values["pre_target_route_node_coherence"]
    )
    return abs(residual_delta) / abs(source_delta)


def residual_gate(
    *,
    loaded_geometry: dict[str, Any],
    after_first_geometry: dict[str, Any],
    after_idle_geometry: dict[str, Any],
    after_second_geometry: dict[str, Any],
    source_values: dict[str, float],
) -> dict[str, Any]:
    loaded_ratio = residual_ratio(loaded_geometry, source_values)
    after_first_ratio = residual_ratio(after_first_geometry, source_values)
    after_idle_ratio = residual_ratio(after_idle_geometry, source_values)
    after_second_ratio = residual_ratio(after_second_geometry, source_values)
    first_readout_ratio_loss = loaded_ratio - after_first_ratio
    second_readout_ratio_loss = after_first_ratio - after_second_ratio
    support_margin = after_second_geometry["center_basin_mass"] - SUPPORT_FLOOR
    coherence_margin = after_second_geometry["center_node_coherence"] - COHERENCE_FLOOR
    boundary_margin = after_second_geometry["active_degree"] - BOUNDARY_ACTIVE_DEGREE_FLOOR
    budget_error = abs(after_second_geometry["budget_error"])
    first_residual_present = after_first_ratio >= MIN_RESIDUAL_DELTA_PERSISTENCE_RATIO
    idle_residual_stable = abs(after_idle_ratio - after_first_ratio) <= 1e-12
    non_consumptive_after_second = (
        after_second_ratio >= MIN_RESIDUAL_DELTA_PERSISTENCE_RATIO
        and second_readout_ratio_loss <= MAX_RATIO_LOSS_AFTER_SECOND_READOUT
        and support_margin >= 0
        and coherence_margin >= 0
        and boundary_margin >= 0
        and budget_error <= MAX_BUDGET_ERROR
        and after_second_geometry["in_flight_packet_total"] == 0.0
        and after_second_geometry["queued_packet_count"] == 0
    )
    consumptive_readout_detected = (
        first_residual_present
        and idle_residual_stable
        and not non_consumptive_after_second
        and second_readout_ratio_loss > MAX_RATIO_LOSS_AFTER_SECOND_READOUT
    )
    gate = {
        "loaded_residual_ratio": loaded_ratio,
        "after_first_readout_residual_ratio": after_first_ratio,
        "after_idle_residual_ratio": after_idle_ratio,
        "after_second_readout_residual_ratio": after_second_ratio,
        "first_readout_ratio_loss": first_readout_ratio_loss,
        "second_readout_ratio_loss": second_readout_ratio_loss,
        "first_residual_present": first_residual_present,
        "idle_residual_stable": idle_residual_stable,
        "non_consumptive_after_second_readout": non_consumptive_after_second,
        "consumptive_readout_detected": consumptive_readout_detected,
        "support_margin": support_margin,
        "coherence_margin": coherence_margin,
        "boundary_margin": boundary_margin,
        "budget_error": budget_error,
        "in_flight_packet_total": after_second_geometry["in_flight_packet_total"],
        "queued_packet_count": after_second_geometry["queued_packet_count"],
    }
    gate["gate_digest"] = digest_value(gate)
    return canonicalize_json_value(gate)


def run_residual_case(
    *,
    candidate_id: str,
    source_post_snapshot_path: str,
    source_values: dict[str, float],
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    run_role = f"{candidate_id}_residual_nonconsumptive"
    model = LGRC9V3.load(str(ROOT / source_post_snapshot_path))
    initial_queue_empty = len(model.get_state().packet_ledger.event_queue_records) == 0
    initial_budget_in_flight = model.get_state().packet_ledger.in_flight_packet_total
    loaded_geometry = route_geometry(model, run_role, "loaded_post_interaction")
    loaded_snapshot_path = ARTIFACT_DIR / f"{run_role}_loaded_post_snapshot.json"
    model.save(str(loaded_snapshot_path))
    loaded_checkpoint = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000000",
        checkpoint_label=f"{run_role}_loaded_post_interaction",
        checkpoint_reason="loaded_post_interaction_snapshot",
    )
    step_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []

    schedule_packet(
        model,
        source_node_id=TARGET_ROUTE["reentry_source_node_id"],
        target_node_id=TARGET_ROUTE["reentry_target_node_id"],
        edge_id=TARGET_ROUTE["edge_id"],
        amount=REENTRY_PACKET_AMOUNT,
        departure_event_time_key=3.0,
        scheduler_event_index=30,
    )
    first_steps, first_events = drain_queue(model, run_role, "first_readout")
    step_rows.extend(first_steps)
    event_rows.extend(first_events)
    after_first_geometry = route_geometry(model, run_role, "after_first_readout")
    after_first_snapshot_path = ARTIFACT_DIR / f"{run_role}_after_first_readout_snapshot.json"
    model.save(str(after_first_snapshot_path))
    first_checkpoint = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000001",
        checkpoint_label=f"{run_role}_after_first_readout",
        checkpoint_reason="after_first_readout",
        event_counts=dict(Counter(row["kind"] for row in first_events)),
    )

    idle_result = model.step()
    step_rows.append(step_summary(idle_result, run_role, "idle_after_first_readout"))
    event_rows.extend(event_to_record(event, run_role, "idle_after_first_readout") for event in idle_result.events)
    after_idle_geometry = route_geometry(model, run_role, "after_idle")
    after_idle_snapshot_path = ARTIFACT_DIR / f"{run_role}_after_idle_snapshot.json"
    model.save(str(after_idle_snapshot_path))
    idle_checkpoint = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000002",
        checkpoint_label=f"{run_role}_after_idle",
        checkpoint_reason="after_idle_following_first_readout",
    )

    schedule_packet(
        model,
        source_node_id=TARGET_ROUTE["reentry_source_node_id"],
        target_node_id=TARGET_ROUTE["reentry_target_node_id"],
        edge_id=TARGET_ROUTE["edge_id"],
        amount=REENTRY_PACKET_AMOUNT,
        departure_event_time_key=4.0,
        scheduler_event_index=40,
    )
    second_steps, second_events = drain_queue(model, run_role, "second_readout")
    step_rows.extend(second_steps)
    event_rows.extend(second_events)
    after_second_geometry = route_geometry(model, run_role, "after_second_readout")
    after_second_snapshot_path = ARTIFACT_DIR / f"{run_role}_after_second_readout_snapshot.json"
    model.save(str(after_second_snapshot_path))
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    event_counts = dict(Counter(row["kind"] for row in event_rows))
    second_checkpoint = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000003",
        checkpoint_label=f"{run_role}_after_second_readout",
        checkpoint_reason="after_second_readout",
        event_counts=event_counts,
    )
    gate = residual_gate(
        loaded_geometry=loaded_geometry,
        after_first_geometry=after_first_geometry,
        after_idle_geometry=after_idle_geometry,
        after_second_geometry=after_second_geometry,
        source_values=source_values,
    )
    artifact = {
        "artifact_id": f"n22_i5b_{run_role}",
        "candidate_id": candidate_id,
        "source_post_snapshot_path": source_post_snapshot_path,
        "initial_queue_empty": initial_queue_empty,
        "initial_budget_in_flight": initial_budget_in_flight,
        "active_reinforcement_schedule_disabled": True,
        "loaded_post_snapshot_path": rel(loaded_snapshot_path),
        "after_first_readout_snapshot_path": rel(after_first_snapshot_path),
        "after_idle_snapshot_path": rel(after_idle_snapshot_path),
        "after_second_readout_snapshot_path": rel(after_second_snapshot_path),
        "event_log_path": rel(event_log_path),
        "graph_checkpoint_paths": [
            loaded_checkpoint,
            first_checkpoint,
            idle_checkpoint,
            second_checkpoint,
        ],
        "loaded_geometry": loaded_geometry,
        "after_first_readout_geometry": after_first_geometry,
        "after_idle_geometry": after_idle_geometry,
        "after_second_readout_geometry": after_second_geometry,
        "residual_gate": gate,
        "step_summaries": step_rows,
        "event_counts_by_kind": event_counts,
    }
    artifact["residual_artifact_digest"] = digest_value(artifact)
    artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(artifact_path, artifact)
    manifest = [
        (rel(artifact_path), f"{candidate_id}_residual_run"),
        (rel(loaded_snapshot_path), f"{candidate_id}_loaded_post_snapshot"),
        (rel(after_first_snapshot_path), f"{candidate_id}_after_first_readout_snapshot"),
        (rel(after_idle_snapshot_path), f"{candidate_id}_after_idle_snapshot"),
        (rel(after_second_snapshot_path), f"{candidate_id}_after_second_readout_snapshot"),
        (rel(event_log_path), f"{candidate_id}_residual_event_log"),
        (loaded_checkpoint, f"{candidate_id}_loaded_checkpoint"),
        (first_checkpoint, f"{candidate_id}_first_readout_checkpoint"),
        (idle_checkpoint, f"{candidate_id}_idle_checkpoint"),
        (second_checkpoint, f"{candidate_id}_second_readout_checkpoint"),
    ]
    return canonicalize_json_value(artifact), manifest


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def build_residual_row(
    i5_row: dict[str, Any],
    i5a_row: dict[str, Any],
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    candidate_id = i5_row["row_id"].removeprefix("n22_i5_row_")
    source_post_snapshot_path = i5_row[
        "post_snapshot_reentry_replay_without_active_reinforcement"
    ]["source_post_interaction_snapshot_path"]
    source_values = source_trace_values(i5_row)
    residual_artifact, manifest_entries = run_residual_case(
        candidate_id=candidate_id,
        source_post_snapshot_path=source_post_snapshot_path,
        source_values=source_values,
    )
    gate = residual_artifact["residual_gate"]
    non_consumptive = gate["non_consumptive_after_second_readout"]
    consumptive = gate["consumptive_readout_detected"]
    row = {
        "row_id": f"n22_i5b_row_{candidate_id}",
        "source_i5_row_id": i5_row["row_id"],
        "source_i5a_row_id": i5a_row["row_id"],
        "source_iteration": i5_row["source_iteration"],
        "source_candidate_row_id": i5_row["source_candidate_row_id"],
        "source_i5_output_digest": i5_row["source_output_digest"],
        "source_i5a_output_digest": i5a_row["source_i5_output_digest"],
        "source_post_interaction_snapshot_path": source_post_snapshot_path,
        "residual_artifact_path": manifest_entries[0][0],
        "residual_artifact_digest": residual_artifact["residual_artifact_digest"],
        "residual_gate": gate,
        "first_residual_present": gate["first_residual_present"],
        "idle_residual_stable": gate["idle_residual_stable"],
        "non_consumptive_durability_supported": non_consumptive,
        "consumptive_readout_detected": consumptive,
        "repeated_reentry_depletion_boundary_confirmed": (
            i5a_row["repeated_reentry_depletion_boundary_recorded"] is True
            and consumptive
        ),
        "narrow_margin_candidate": i5_row["narrow_margin_candidate"],
        "row_decision": "partial" if consumptive else "blocked",
        "provisional_su_ladder_rung": (
            "SU3_consumptive_readout_limited"
            if consumptive
            else "demoted_before_SU4"
        ),
        "i5b_consumable_role": (
            "consumptive_readout_boundary_for_I6_I7"
            if consumptive
            else "residual_probe_failed_or_demoted"
        ),
        "durable_geometry_modification_supported": False,
        "su4_or_stronger_supported": False,
        "i6_su5_requires_reclassification": consumptive,
        "n21_nd6_bridge_status": "not_supported",
        "susceptibility_update_claim_allowed": False,
        "claim_ceiling": (
            "I5-B confirms consumptive route_b readout: first readout leaves "
            "some residual, but repeated readout spends the residual below the "
            "non-consumptive floor. No durable SU4, transfer SU5, SU6, final "
            "N22, N21 ND6 bridge, semantic learning, choice, agency, native "
            "support, sentience, Phase 8, or ant-ecology implementation."
        )
        if consumptive
        else "residual probe did not support non-consumptive durability",
        "unsafe_claim_flags": unsafe_claim_flags(),
        "output_digest": "pending",
    }
    row["output_digest"] = digest_value({k: v for k, v in row.items() if k != "output_digest"})
    return canonicalize_json_value(row), manifest_entries


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


def build_output() -> dict[str, Any]:
    i5 = load_json(I5_OUTPUT_PATH)
    i5a = load_json(I5A_OUTPUT_PATH)
    i5_rows = [
        row
        for row in i5["replay_rows"]
        if row["provisional_su_ladder_rung"] == "SU3"
        and row["i5_consumable_role"] == "replay_backed_SU3_candidate_pending_I7_controls"
    ]
    i5a_by_i5_row = {row["source_i5_row_id"]: row for row in i5a["stress_rows"]}
    threshold_path = ARTIFACT_DIR / "n22_i5b_thresholds_declared_before_use.json"
    write_json(threshold_path, threshold_record())
    residual_rows = []
    manifest_entries: list[tuple[str, str]] = [(rel(threshold_path), "thresholds_declared_before_use")]
    for i5_row in i5_rows:
        residual_row, row_manifest_entries = build_residual_row(
            i5_row,
            i5a_by_i5_row[i5_row["row_id"]],
        )
        residual_rows.append(residual_row)
        manifest_entries.extend(row_manifest_entries)
    aggregate_manifest = file_manifest(manifest_entries)
    artifact_sha256_match = all(
        item["sha256"] == sha256_file(item["path"]) for item in aggregate_manifest
    )
    consumptive_rows = [
        row for row in residual_rows if row["consumptive_readout_detected"]
    ]
    non_consumptive_rows = [
        row for row in residual_rows if row["non_consumptive_durability_supported"]
    ]
    residual_summary = [
        {
            "row_id": row["row_id"],
            "source_i5_row_id": row["source_i5_row_id"],
            "source_iteration": row["source_iteration"],
            "first_residual_present": row["first_residual_present"],
            "idle_residual_stable": row["idle_residual_stable"],
            "after_first_ratio": row["residual_gate"][
                "after_first_readout_residual_ratio"
            ],
            "after_second_ratio": row["residual_gate"][
                "after_second_readout_residual_ratio"
            ],
            "second_readout_ratio_loss": row["residual_gate"][
                "second_readout_ratio_loss"
            ],
            "consumptive_readout_detected": row["consumptive_readout_detected"],
            "non_consumptive_durability_supported": row[
                "non_consumptive_durability_supported"
            ],
            "provisional_su_ladder_rung": row["provisional_su_ladder_rung"],
            "narrow_margin_candidate": row["narrow_margin_candidate"],
        }
        for row in residual_rows
    ]
    checks = [
        check("i5_passed", i5.get("status") == "passed", i5.get("acceptance_state")),
        check("i5a_passed", i5a.get("status") == "passed", i5a.get("acceptance_state")),
        check("i5_su3_candidate_count", len(i5_rows) == 5, [row["row_id"] for row in i5_rows]),
        check("i5a_rows_cover_i5_rows", all(row["row_id"] in i5a_by_i5_row for row in i5_rows), list(i5a_by_i5_row)),
        check("thresholds_declared_before_use", threshold_record()["declared_before_use"] is True, threshold_record()),
        check("artifact_manifest_non_empty", len(aggregate_manifest) >= 40, len(aggregate_manifest)),
        check("artifact_hashes_match", artifact_sha256_match, len(aggregate_manifest)),
        check("first_residual_present_for_all_rows", all(row["first_residual_present"] for row in residual_rows), residual_summary),
        check("idle_residual_stable_for_all_rows", all(row["idle_residual_stable"] for row in residual_rows), residual_summary),
        check("all_rows_consumptive_readout_detected", len(consumptive_rows) == len(residual_rows), residual_summary),
        check("no_rows_support_non_consumptive_durability", len(non_consumptive_rows) == 0, residual_summary),
        check("all_rows_block_su4_or_stronger", all(row["su4_or_stronger_supported"] is False and row["durable_geometry_modification_supported"] is False for row in residual_rows), residual_summary),
        check("i6_reclassification_required", all(row["i6_su5_requires_reclassification"] for row in residual_rows), residual_summary),
        check("narrow_complementary_row_tracked", any(row["narrow_margin_candidate"] for row in residual_rows), residual_summary),
        check("all_claims_still_blocked", all(row["susceptibility_update_claim_allowed"] is False for row in residual_rows), residual_summary),
        check("unsafe_flags_all_false", all(all(value is False for value in row["unsafe_claim_flags"].values()) for row in residual_rows), "all residual rows"),
        check("artifact_paths_repository_relative", all(not item["path"].startswith("/") for item in aggregate_manifest), "relative paths only"),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i5b_residual_nonconsumptive_durability_probe",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": "5-B",
        "purpose": "residual and non-consumptive durability classification over I5/I5-A rows",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_consumptive_readout_boundary_no_nonconsumptive_durability"
            if not failed_checks
            else "failed_residual_nonconsumptive_durability_probe"
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I5_OUTPUT_PATH, "n22_i5_durability_replay_probe"),
            source_record(I5A_OUTPUT_PATH, "n22_i5a_replay_durability_stress_probe"),
        ],
        "residual_policy": {
            "threshold_policy_changed_from_i5": False,
            "repeated_reentry_boundary_from_i5a_consumed": True,
            "non_consumptive_requires_second_readout_above_floor": True,
            "durable_su4_or_stronger_allowed": False,
        },
        "residual_rows": residual_rows,
        "residual_summary": residual_summary,
        "artifact_manifest": aggregate_manifest,
        "iteration5b_boundary": {
            "source_i5_su3_candidate_count": len(i5_rows),
            "source_i5a_stress_limited_candidate_count": len(i5a["stress_rows"]),
            "first_residual_present_count": sum(1 for row in residual_rows if row["first_residual_present"]),
            "idle_residual_stable_count": sum(1 for row in residual_rows if row["idle_residual_stable"]),
            "consumptive_readout_detected_count": len(consumptive_rows),
            "non_consumptive_durability_supported_count": len(non_consumptive_rows),
            "narrow_margin_candidate_count": sum(1 for row in residual_rows if row["narrow_margin_candidate"]),
            "provisional_su_ladder_rung": "SU3_consumptive_readout_limited",
            "su4_or_stronger_supported": False,
            "durable_geometry_modification_supported": False,
            "i6_su5_requires_reclassification": True,
            "n22_closeout_ladder_rung_assigned": False,
            "n21_nd6_bridge_status": "not_supported",
            "semantic_learning_supported": False,
            "choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ready_for_iteration_6_reclassification": not failed_checks,
            "ready_for_iteration_7_control_matrix": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I5-B shows the I5/I5-A route_b signal is a consumptive readout "
                "boundary, not non-consumptive durable geometry modification."
            ),
            "what_changed_from_i5a": (
                "I5-A recorded repeated re-entry depletion. I5-B makes that "
                "explicit by measuring the residual route_b delta after the "
                "first readout, after an idle window, and after a second readout. "
                "A first residual remains and is idle-stable, but the second "
                "readout spends the residual below the non-consumptive floor."
            ),
            "claim_boundary": (
                "I5-B supports only consumptive-readout-limited SU3 evidence. "
                "It blocks durable SU4, transfer SU5 as durable susceptibility, "
                "SU6, final N22, the N21 ND6 bridge, semantic learning, choice, "
                "agency, native support, sentience, Phase 8, and ant-ecology "
                "implementation."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = digest_value(
        {k: v for k, v in output.items() if k != "output_digest"}
    )
    return canonicalize_json_value(output)


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N22 Iteration 5-B - Residual / Non-Consumptive Durability Probe",
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
        output["geometric_interpretation"]["what_changed_from_i5a"],
        "",
        "## Residual Rows",
        "",
        "| Row | Source | After First | After Second | Consumptive | Rung |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in output["residual_rows"]:
        gate = row["residual_gate"]
        lines.append(
            "| "
            f"`{row['row_id'].removeprefix('n22_i5b_row_')}` | "
            f"`{row['source_iteration']}` | "
            f"{gate['after_first_readout_residual_ratio']:.6f} | "
            f"{gate['after_second_readout_residual_ratio']:.6f} | "
            f"`{str(row['consumptive_readout_detected']).lower()}` | "
            f"`{row['provisional_su_ladder_rung']}` |"
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
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            output["geometric_interpretation"]["claim_boundary"],
            "",
            "I5-B requires I6 to avoid treating transfer/readout expression as "
            "non-consumptive durable susceptibility.",
            "",
        ]
    )
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    output = load_json(rel(OUTPUT))
    write_report(output)


if __name__ == "__main__":
    main()
