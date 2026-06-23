#!/usr/bin/env python3
"""Build N22 Iteration 6 transfer / re-entry probe."""

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
OUTPUT = EXPERIMENT / "outputs" / "n22_transfer_reentry_probe.json"
REPORT = EXPERIMENT / "reports" / "n22_transfer_reentry_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_transfer_reentry_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_transfer_reentry_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_transfer_reentry_probe.py"
)

I5_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_durability_replay_probe.json"
)
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_replay_durability_stress_probe.json"
)
I5B_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_residual_nonconsumptive_durability_probe.json"
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

RUN_ID = "n22_i6_transfer_reentry_lgrc9v3"
TARGET_ROUTE = {
    "route_id": "route_b",
    "reentry_source_node_id": 1,
    "reentry_target_node_id": 0,
    "edge_id": 0,
}
PEER_ROUTE = {
    "route_id": "route_peer_edge_1",
    "reentry_source_node_id": 2,
    "reentry_target_node_id": 0,
    "edge_id": 1,
}
REENTRY_PACKET_AMOUNT = 0.04
MILD_PEER_FLUX_AMOUNT = 0.01
SUPPORT_FLOOR = 9.85
COHERENCE_FLOOR = 9.85
BOUNDARY_ACTIVE_DEGREE_FLOOR = 9
MAX_BUDGET_ERROR = 1e-9
MIN_TRANSFER_DELTA_PERSISTENCE_RATIO = 0.45
MIN_TRANSFER_TARGET_OVER_PEER_MARGIN = 0.03
POSITIVE_TRANSFER_CONTEXTS = [
    "delayed_boundary_reentry",
    "corridor_peer_flux_then_reentry",
]
CONTROL_CONTEXTS = [
    "label_swap_peer_reentry_control",
    "active_schedule_carryover_control",
]
TRANSFER_CONTEXTS = POSITIVE_TRANSFER_CONTEXTS + CONTROL_CONTEXTS


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
        "threshold_record_id": "n22_i6_transfer_reentry_thresholds",
        "declared_before_use": True,
        "inherits_i5_threshold_policy": True,
        "consumes_i5a_depletion_boundary": True,
        "consumes_i5b_consumptive_readout_boundary": True,
        "positive_transfer_contexts": POSITIVE_TRANSFER_CONTEXTS,
        "control_contexts": CONTROL_CONTEXTS,
        "min_transfer_delta_persistence_ratio": MIN_TRANSFER_DELTA_PERSISTENCE_RATIO,
        "min_transfer_target_over_peer_margin": MIN_TRANSFER_TARGET_OVER_PEER_MARGIN,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "boundary_active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
        "max_budget_error": MAX_BUDGET_ERROR,
        "reentry_packet_amount": REENTRY_PACKET_AMOUNT,
        "mild_peer_flux_amount": MILD_PEER_FLUX_AMOUNT,
        "su6_or_stronger_allowed": False,
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
    peer_node = state.base_state.nodes[PEER_ROUTE["reentry_source_node_id"]]
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
        "peer_route_id": PEER_ROUTE["route_id"],
        "peer_route_node_id": PEER_ROUTE["reentry_source_node_id"],
        "peer_route_node_coherence": peer_node.coherence,
        "peer_route_basin_mass": peer_node.basin_mass,
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
        "conserved_budget_total": ledger.conserved_budget_total,
        "queued_packet_count": len(ledger.event_queue_records),
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
        seed_name="n22-column-h-transfer-reentry-fixture",
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="n22_transfer_reentry_probe",
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


def run_idle_windows(model: LGRC9V3, *, run_role: str, count: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offset in range(count):
        result = model.step()
        rows.append(step_summary(result, run_role, f"idle_window_{offset + 1}"))
    return rows


def packet_event_present(
    event_rows: list[dict[str, Any]],
    *,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
) -> bool:
    for row in event_rows:
        processed = row.get("payload", {}).get("processed_event", {})
        if (
            processed.get("source_node_id") == source_node_id
            and processed.get("target_node_id") == target_node_id
            and processed.get("edge_id") == edge_id
            and processed.get("event_kind") == "lgrc9v3_packet_arrival"
        ):
            return True
    return False


def source_trace_values(row: dict[str, Any]) -> dict[str, float]:
    trace = load_json(row["source_trace_artifact_path"])
    pre = trace["pre_interaction_geometry_trace"]
    source_sig = row["duplicate_replay"]["source_signature"]
    return {
        "pre_target_route_node_coherence": pre["target_route_node_coherence"],
        "pre_peer_route_node_coherence": pre.get(
            "peer_route_node_coherence",
            pre.get("peer_route_node_2_coherence", 0.0),
        ),
        "source_target_route_delta": source_sig["target_route_delta"],
        "source_reentry_route_delta_from_pre": source_sig[
            "target_reentry_route_delta_from_pre"
        ],
    }


def transfer_gate(
    *,
    transfer_context: str,
    geometry: dict[str, Any],
    source_values: dict[str, float],
    target_reentry_event_present: bool,
    peer_reentry_event_present: bool,
    initial_queue_empty: bool,
    active_reinforcement_queue_empty_before_reentry: bool,
    control_expected_to_fail_closed: bool,
) -> dict[str, Any]:
    target_delta = (
        geometry["target_route_node_coherence"]
        - source_values["pre_target_route_node_coherence"]
    )
    peer_delta = (
        geometry["peer_route_node_coherence"]
        - source_values["pre_peer_route_node_coherence"]
    )
    ratio = (
        abs(target_delta) / abs(source_values["source_target_route_delta"])
        if source_values["source_target_route_delta"]
        else 0.0
    )
    target_over_peer_margin = target_delta - peer_delta
    support_margin = geometry["center_basin_mass"] - SUPPORT_FLOOR
    coherence_margin = geometry["center_node_coherence"] - COHERENCE_FLOOR
    boundary_margin = geometry["active_degree"] - BOUNDARY_ACTIVE_DEGREE_FLOOR
    budget_error = abs(geometry["budget_error"])
    positive_context_passed = (
        transfer_context in POSITIVE_TRANSFER_CONTEXTS
        and target_reentry_event_present
        and not peer_reentry_event_present
        and ratio >= MIN_TRANSFER_DELTA_PERSISTENCE_RATIO
        and target_over_peer_margin >= MIN_TRANSFER_TARGET_OVER_PEER_MARGIN
        and support_margin >= 0
        and coherence_margin >= 0
        and boundary_margin >= 0
        and budget_error <= MAX_BUDGET_ERROR
        and geometry["in_flight_packet_total"] == 0.0
        and geometry["queued_packet_count"] == 0
        and initial_queue_empty
        and active_reinforcement_queue_empty_before_reentry
    )
    control_failed_closed = (
        control_expected_to_fail_closed
        and (
            not target_reentry_event_present
            or peer_reentry_event_present
            or geometry["queued_packet_count"] > 0
            or not active_reinforcement_queue_empty_before_reentry
        )
    )
    gate = {
        "transfer_context": transfer_context,
        "target_reentry_delta_from_pre": target_delta,
        "peer_reentry_delta_from_pre": peer_delta,
        "delta_persistence_ratio_against_source": ratio,
        "target_over_peer_margin": target_over_peer_margin,
        "support_margin": support_margin,
        "coherence_margin": coherence_margin,
        "boundary_margin": boundary_margin,
        "budget_error": budget_error,
        "in_flight_packet_total": geometry["in_flight_packet_total"],
        "queued_packet_count": geometry["queued_packet_count"],
        "target_reentry_event_present": target_reentry_event_present,
        "peer_reentry_event_present": peer_reentry_event_present,
        "initial_queue_empty": initial_queue_empty,
        "active_reinforcement_queue_empty_before_reentry": (
            active_reinforcement_queue_empty_before_reentry
        ),
        "positive_context_passed": positive_context_passed,
        "control_failed_closed": control_failed_closed,
    }
    gate["gate_digest"] = digest_value(gate)
    return canonicalize_json_value(gate)


def run_transfer_context(
    *,
    candidate_id: str,
    source_post_snapshot_path: str,
    source_values: dict[str, float],
    transfer_context: str,
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    run_role = f"{candidate_id}_{transfer_context}"
    model = LGRC9V3.load(str(ROOT / source_post_snapshot_path))
    initial_queue_empty = len(model.get_state().packet_ledger.event_queue_records) == 0
    initial_budget_in_flight = model.get_state().packet_ledger.in_flight_packet_total
    initial_geometry = route_geometry(model, run_role, "loaded_post_interaction")
    loaded_snapshot_path = ARTIFACT_DIR / f"{run_role}_loaded_post_snapshot.json"
    model.save(str(loaded_snapshot_path))
    initial_checkpoint = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000000",
        checkpoint_label=f"{run_role}_loaded_post_interaction",
        checkpoint_reason="loaded_post_interaction_snapshot",
    )
    step_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    active_reinforcement_queue_empty_before_reentry = initial_queue_empty
    control_expected_to_fail_closed = transfer_context in CONTROL_CONTEXTS

    if transfer_context == "delayed_boundary_reentry":
        step_rows.extend(run_idle_windows(model, run_role=run_role, count=2))
        active_reinforcement_queue_empty_before_reentry = (
            len(model.get_state().packet_ledger.event_queue_records) == 0
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
        reentry_steps, reentry_events = drain_queue(model, run_role, "delayed_boundary_reentry")
        step_rows.extend(reentry_steps)
        event_rows.extend(reentry_events)
    elif transfer_context == "corridor_peer_flux_then_reentry":
        schedule_packet(
            model,
            source_node_id=0,
            target_node_id=PEER_ROUTE["reentry_source_node_id"],
            edge_id=PEER_ROUTE["edge_id"],
            amount=MILD_PEER_FLUX_AMOUNT,
            departure_event_time_key=2.0,
            scheduler_event_index=20,
        )
        peer_steps, peer_events = drain_queue(model, run_role, "mild_peer_corridor_flux")
        step_rows.extend(peer_steps)
        event_rows.extend(peer_events)
        active_reinforcement_queue_empty_before_reentry = (
            len(model.get_state().packet_ledger.event_queue_records) == 0
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
        reentry_steps, reentry_events = drain_queue(model, run_role, "corridor_reentry")
        step_rows.extend(reentry_steps)
        event_rows.extend(reentry_events)
    elif transfer_context == "label_swap_peer_reentry_control":
        schedule_packet(
            model,
            source_node_id=PEER_ROUTE["reentry_source_node_id"],
            target_node_id=PEER_ROUTE["reentry_target_node_id"],
            edge_id=PEER_ROUTE["edge_id"],
            amount=REENTRY_PACKET_AMOUNT,
            departure_event_time_key=4.0,
            scheduler_event_index=40,
        )
        peer_steps, peer_events = drain_queue(model, run_role, "peer_reentry_label_swap")
        step_rows.extend(peer_steps)
        event_rows.extend(peer_events)
    elif transfer_context == "active_schedule_carryover_control":
        schedule_packet(
            model,
            source_node_id=TARGET_ROUTE["reentry_source_node_id"],
            target_node_id=TARGET_ROUTE["reentry_target_node_id"],
            edge_id=TARGET_ROUTE["edge_id"],
            amount=REENTRY_PACKET_AMOUNT,
            departure_event_time_key=4.0,
            scheduler_event_index=40,
        )
        active_reinforcement_queue_empty_before_reentry = False
    else:
        raise ValueError(f"Unknown transfer context: {transfer_context}")

    final_geometry = route_geometry(model, run_role, "final_transfer_context")
    final_snapshot_path = ARTIFACT_DIR / f"{run_role}_final_snapshot.json"
    model.save(str(final_snapshot_path))
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    event_counts = dict(Counter(row["kind"] for row in event_rows))
    final_checkpoint = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000001",
        checkpoint_label=f"{run_role}_final_transfer_context",
        checkpoint_reason=f"after_{transfer_context}",
        event_counts=event_counts,
    )
    target_reentry_present = packet_event_present(
        event_rows,
        source_node_id=TARGET_ROUTE["reentry_source_node_id"],
        target_node_id=TARGET_ROUTE["reentry_target_node_id"],
        edge_id=TARGET_ROUTE["edge_id"],
    )
    peer_reentry_present = packet_event_present(
        event_rows,
        source_node_id=PEER_ROUTE["reentry_source_node_id"],
        target_node_id=PEER_ROUTE["reentry_target_node_id"],
        edge_id=PEER_ROUTE["edge_id"],
    )
    gate = transfer_gate(
        transfer_context=transfer_context,
        geometry=final_geometry,
        source_values=source_values,
        target_reentry_event_present=target_reentry_present,
        peer_reentry_event_present=peer_reentry_present,
        initial_queue_empty=initial_queue_empty,
        active_reinforcement_queue_empty_before_reentry=(
            active_reinforcement_queue_empty_before_reentry
        ),
        control_expected_to_fail_closed=control_expected_to_fail_closed,
    )
    transfer_artifact = {
        "artifact_id": f"n22_i6_{run_role}",
        "candidate_id": candidate_id,
        "transfer_context": transfer_context,
        "source_post_snapshot_path": source_post_snapshot_path,
        "initial_queue_empty": initial_queue_empty,
        "initial_budget_in_flight": initial_budget_in_flight,
        "active_reinforcement_schedule_disabled": True,
        "control_expected_to_fail_closed": control_expected_to_fail_closed,
        "loaded_post_snapshot_path": rel(loaded_snapshot_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "event_log_path": rel(event_log_path),
        "graph_checkpoint_paths": [initial_checkpoint, final_checkpoint],
        "initial_geometry": initial_geometry,
        "final_geometry": final_geometry,
        "transfer_gate": gate,
        "step_summaries": step_rows,
        "event_counts_by_kind": event_counts,
    }
    transfer_artifact["transfer_artifact_digest"] = digest_value(transfer_artifact)
    artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(artifact_path, transfer_artifact)
    manifest = [
        (rel(artifact_path), f"{candidate_id}_{transfer_context}_run"),
        (rel(loaded_snapshot_path), f"{candidate_id}_{transfer_context}_loaded_post_snapshot"),
        (rel(final_snapshot_path), f"{candidate_id}_{transfer_context}_final_snapshot"),
        (rel(event_log_path), f"{candidate_id}_{transfer_context}_event_log"),
        (initial_checkpoint, f"{candidate_id}_{transfer_context}_initial_checkpoint"),
        (final_checkpoint, f"{candidate_id}_{transfer_context}_final_checkpoint"),
    ]
    return canonicalize_json_value(transfer_artifact), manifest


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def build_transfer_row(
    i5_row: dict[str, Any],
    i5a_row: dict[str, Any],
    i5b_row: dict[str, Any],
    i5b_output_digest: str,
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    candidate_id = i5_row["row_id"].removeprefix("n22_i5_row_")
    source_post_snapshot_path = i5_row[
        "post_snapshot_reentry_replay_without_active_reinforcement"
    ]["source_post_interaction_snapshot_path"]
    source_values = source_trace_values(i5_row)
    transfer_results = []
    manifest_entries: list[tuple[str, str]] = []
    for transfer_context in TRANSFER_CONTEXTS:
        transfer_artifact, transfer_manifest = run_transfer_context(
            candidate_id=candidate_id,
            source_post_snapshot_path=source_post_snapshot_path,
            source_values=source_values,
            transfer_context=transfer_context,
        )
        gate = transfer_artifact["transfer_gate"]
        if transfer_context in POSITIVE_TRANSFER_CONTEXTS:
            status = "passed" if gate["positive_context_passed"] else "demoted"
        else:
            status = "failed_closed" if gate["control_failed_closed"] else "failed_open"
        transfer_results.append(
            {
                "transfer_context": transfer_context,
                "status": status,
                "transfer_artifact_path": transfer_manifest[0][0],
                "transfer_artifact_digest": transfer_artifact[
                    "transfer_artifact_digest"
                ],
                "transfer_gate": gate,
            }
        )
        manifest_entries.extend(transfer_manifest)
    positive_passed = all(
        item["status"] == "passed"
        for item in transfer_results
        if item["transfer_context"] in POSITIVE_TRANSFER_CONTEXTS
    )
    controls_failed_closed = all(
        item["status"] == "failed_closed"
        for item in transfer_results
        if item["transfer_context"] in CONTROL_CONTEXTS
    )
    repeated_boundary_preserved = (
        i5a_row["repeated_reentry_depletion_boundary_recorded"] is True
        and i5a_row["repeated_reentry_boundary_blocks_su4"] is True
    )
    consumptive_boundary_preserved = (
        i5b_row["consumptive_readout_detected"] is True
        and i5b_row["non_consumptive_durability_supported"] is False
    )
    transfer_readout_expression = (
        positive_passed
        and controls_failed_closed
        and repeated_boundary_preserved
        and consumptive_boundary_preserved
    )
    su5_candidate = (
        transfer_readout_expression
        and i5b_row["non_consumptive_durability_supported"] is True
    )
    row = {
        "row_id": f"n22_i6_row_{candidate_id}",
        "source_i5_row_id": i5_row["row_id"],
        "source_i5a_row_id": i5a_row["row_id"],
        "source_i5b_row_id": i5b_row["row_id"],
        "source_iteration": i5_row["source_iteration"],
        "source_candidate_row_id": i5_row["source_candidate_row_id"],
        "source_i5_output_digest": i5_row["source_output_digest"],
        "source_i5a_output_digest": i5a_row["source_i5_output_digest"],
        "source_i5b_output_digest": i5b_output_digest,
        "source_post_interaction_snapshot_path": source_post_snapshot_path,
        "source_values": source_values,
        "transfer_results": transfer_results,
        "positive_transfer_context_count": len(POSITIVE_TRANSFER_CONTEXTS),
        "positive_transfer_contexts_passed": positive_passed,
        "positive_transfer_contexts_demoted": [
            item["transfer_context"]
            for item in transfer_results
            if item["transfer_context"] in POSITIVE_TRANSFER_CONTEXTS
            and item["status"] == "demoted"
        ],
        "control_context_count": len(CONTROL_CONTEXTS),
        "control_contexts_failed_closed": controls_failed_closed,
        "repeated_reentry_depletion_boundary_preserved": repeated_boundary_preserved,
        "consumptive_readout_boundary_preserved": consumptive_boundary_preserved,
        "non_consumptive_durability_available": i5b_row[
            "non_consumptive_durability_supported"
        ],
        "transfer_readout_expression": transfer_readout_expression,
        "narrow_margin_candidate": i5_row["narrow_margin_candidate"],
        "row_decision": "partial" if transfer_readout_expression else "blocked",
        "provisional_su_ladder_rung": (
            "SU3_transfer_readout_expression_no_SU5"
            if transfer_readout_expression
            else "demoted_before_SU5"
        ),
        "i6_consumable_role": (
            "transfer_readout_expression_boundary_pending_I7_controls"
            if transfer_readout_expression
            else "transfer_reentry_failed_or_demoted"
        ),
        "su5_candidate_supported_before_i5b": positive_passed
        and controls_failed_closed
        and repeated_boundary_preserved,
        "su5_blocked_by_i5b_consumptive_readout": transfer_readout_expression,
        "durable_geometry_modification_supported": False,
        "su5_supported": su5_candidate,
        "su6_or_stronger_supported": False,
        "final_n22_supported": False,
        "n21_nd6_bridge_status": "not_supported",
        "susceptibility_update_claim_allowed": False,
        "claim_ceiling": (
            "transfer/readout expression of a consumptive SU3-limited route_b "
            "state pending I7 controls; I5-B blocks non-consumptive durable "
            "SU4 and transfer SU5; no SU6, final N22, N21 ND6 bridge, semantic "
            "learning, choice, agency, native support, sentience, Phase 8, or "
            "ant-ecology implementation"
        )
        if transfer_readout_expression
        else "transfer/re-entry probe demoted before SU5; no susceptibility support",
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
    i5b = load_json(I5B_OUTPUT_PATH)
    i5_rows = [
        row
        for row in i5["replay_rows"]
        if row["provisional_su_ladder_rung"] == "SU3"
        and row["i5_consumable_role"] == "replay_backed_SU3_candidate_pending_I7_controls"
    ]
    i5a_by_i5_row = {row["source_i5_row_id"]: row for row in i5a["stress_rows"]}
    i5b_by_i5_row = {row["source_i5_row_id"]: row for row in i5b["residual_rows"]}
    threshold_path = ARTIFACT_DIR / "n22_i6_thresholds_declared_before_use.json"
    write_json(threshold_path, threshold_record())
    transfer_rows = []
    manifest_entries: list[tuple[str, str]] = [(rel(threshold_path), "thresholds_declared_before_use")]
    for i5_row in i5_rows:
        transfer_row, row_manifest_entries = build_transfer_row(
            i5_row,
            i5a_by_i5_row[i5_row["row_id"]],
            i5b_by_i5_row[i5_row["row_id"]],
            i5b["output_digest"],
        )
        transfer_rows.append(transfer_row)
        manifest_entries.extend(row_manifest_entries)
    aggregate_manifest = file_manifest(manifest_entries)
    artifact_sha256_match = all(
        item["sha256"] == sha256_file(item["path"]) for item in aggregate_manifest
    )
    su5_rows = [
        row
        for row in transfer_rows
        if row["su5_supported"] is True
    ]
    transfer_readout_rows = [
        row
        for row in transfer_rows
        if row["i6_consumable_role"]
        == "transfer_readout_expression_boundary_pending_I7_controls"
    ]
    demoted_rows = [
        row
        for row in transfer_rows
        if row["i6_consumable_role"] == "transfer_reentry_failed_or_demoted"
    ]
    transfer_summary = [
        {
            "row_id": row["row_id"],
            "source_i5_row_id": row["source_i5_row_id"],
            "source_iteration": row["source_iteration"],
            "positive_transfer_contexts_passed": row[
                "positive_transfer_contexts_passed"
            ],
            "positive_transfer_contexts_demoted": row[
                "positive_transfer_contexts_demoted"
            ],
            "control_contexts_failed_closed": row["control_contexts_failed_closed"],
            "repeated_reentry_depletion_boundary_preserved": row[
                "repeated_reentry_depletion_boundary_preserved"
            ],
            "consumptive_readout_boundary_preserved": row[
                "consumptive_readout_boundary_preserved"
            ],
            "transfer_readout_expression": row["transfer_readout_expression"],
            "provisional_su_ladder_rung": row["provisional_su_ladder_rung"],
            "i6_consumable_role": row["i6_consumable_role"],
            "narrow_margin_candidate": row["narrow_margin_candidate"],
        }
        for row in transfer_rows
    ]
    checks = [
        check("i5_passed", i5.get("status") == "passed", i5.get("acceptance_state")),
        check("i5a_passed", i5a.get("status") == "passed", i5a.get("acceptance_state")),
        check("i5b_passed", i5b.get("status") == "passed", i5b.get("acceptance_state")),
        check("i5_su3_candidate_count", len(i5_rows) == 5, [row["row_id"] for row in i5_rows]),
        check("i5a_rows_cover_i5_rows", all(row["row_id"] in i5a_by_i5_row for row in i5_rows), list(i5a_by_i5_row)),
        check("i5b_rows_cover_i5_rows", all(row["row_id"] in i5b_by_i5_row for row in i5_rows), list(i5b_by_i5_row)),
        check("thresholds_declared_before_use", threshold_record()["declared_before_use"] is True, threshold_record()),
        check("artifact_manifest_non_empty", len(aggregate_manifest) >= 100, len(aggregate_manifest)),
        check("artifact_hashes_match", artifact_sha256_match, len(aggregate_manifest)),
        check("non_narrow_rows_positive_transfer_contexts_passed", all(row["positive_transfer_contexts_passed"] for row in transfer_rows if not row["narrow_margin_candidate"]), transfer_summary),
        check("narrow_complementary_row_demoted_without_overclaim", len(demoted_rows) == 1 and demoted_rows[0]["narrow_margin_candidate"] is True, transfer_summary),
        check("all_rows_controls_failed_closed", all(row["control_contexts_failed_closed"] for row in transfer_rows), transfer_summary),
        check("repeated_boundary_preserved_for_all_rows", all(row["repeated_reentry_depletion_boundary_preserved"] for row in transfer_rows), transfer_summary),
        check("consumptive_boundary_preserved_for_all_rows", all(row["consumptive_readout_boundary_preserved"] for row in transfer_rows), transfer_summary),
        check("transfer_readout_expression_subset_recorded", len(transfer_readout_rows) == 4 and len(su5_rows) == 0 and all(row["su6_or_stronger_supported"] is False for row in transfer_rows), transfer_summary),
        check("narrow_complementary_row_tracked", any(row["narrow_margin_candidate"] for row in transfer_rows), transfer_summary),
        check("all_claims_still_blocked", all(row["susceptibility_update_claim_allowed"] is False and row["final_n22_supported"] is False for row in transfer_rows), transfer_summary),
        check("unsafe_flags_all_false", all(all(value is False for value in row["unsafe_claim_flags"].values()) for row in transfer_rows), "all transfer rows"),
        check("artifact_paths_repository_relative", all(not item["path"].startswith("/") for item in aggregate_manifest), "relative paths only"),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i6_transfer_reentry_probe",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": "6",
        "purpose": "transfer and later re-entry probe over I5/I5-A SU3 candidates",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_transfer_readout_expression_no_su5_due_consumptive_boundary"
            if not failed_checks
            else "failed_transfer_reentry_probe"
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I5_OUTPUT_PATH, "n22_i5_durability_replay_probe"),
            source_record(I5A_OUTPUT_PATH, "n22_i5a_replay_durability_stress_probe"),
            source_record(I5B_OUTPUT_PATH, "n22_i5b_residual_nonconsumptive_durability_probe"),
        ],
        "transfer_policy": {
            "threshold_policy_changed_from_i5": False,
            "positive_transfer_contexts": POSITIVE_TRANSFER_CONTEXTS,
            "control_contexts": CONTROL_CONTEXTS,
            "repeated_reentry_depletion_boundary_consumed_as_blocker": True,
            "i5b_consumptive_readout_boundary_consumed_as_su5_blocker": True,
            "su6_or_stronger_allowed": False,
            "full_i7_control_matrix_run": False,
        },
        "transfer_rows": transfer_rows,
        "transfer_summary": transfer_summary,
        "artifact_manifest": aggregate_manifest,
        "iteration6_boundary": {
            "source_i5_su3_candidate_count": len(i5_rows),
            "source_i5a_stress_limited_candidate_count": len(i5a["stress_rows"]),
            "source_i5b_consumptive_boundary_count": len(i5b["residual_rows"]),
            "transfer_reentry_su5_candidate_count": len(su5_rows),
            "transfer_readout_expression_count": len(transfer_readout_rows),
            "su5_blocked_by_i5b_consumptive_readout_count": len(transfer_readout_rows),
            "demoted_before_su5_count": len(demoted_rows),
            "demoted_rows": [row["row_id"] for row in demoted_rows],
            "positive_transfer_context_count_per_row": len(POSITIVE_TRANSFER_CONTEXTS),
            "control_context_count_per_row": len(CONTROL_CONTEXTS),
            "repeated_reentry_depletion_boundary_count": sum(
                1
                for row in transfer_rows
                if row["repeated_reentry_depletion_boundary_preserved"]
            ),
            "narrow_margin_candidate_count": sum(1 for row in transfer_rows if row["narrow_margin_candidate"]),
            "provisional_su_ladder_rung": "SU3_transfer_readout_expression_no_SU5",
            "su5_supported": False,
            "su6_or_stronger_supported": False,
            "final_n22_supported": False,
            "n22_closeout_ladder_rung_assigned": False,
            "n21_nd6_bridge_status": "not_supported",
            "semantic_learning_supported": False,
            "choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ready_for_iteration_7_control_matrix": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I6 turns the I5/I5-A replay-backed route_b susceptibility "
                "signal into local transfer/readout expression for four rows, "
                "but I5-B prevents promotion to SU5 because the readout is "
                "consumptive rather than non-consumptive durable geometry. The "
                "narrow complementary split row still demotes on target-over-peer "
                "separation."
            ),
            "what_changed_from_i5a": (
                "I5-A showed stress-limited SU3 preservation and a repeated "
                "re-entry depletion boundary. I6 consumes that boundary, then "
                "asks whether the same source-current route_b delta is expressed "
                "through declared later re-entry contexts rather than only clean "
                "replay. The positive contexts are delayed boundary re-entry and "
                "corridor peer-flux followed by route_b re-entry. The single "
                "route and bounded-dose rows express the readout, but I5-B "
                "shows that repeated readout consumes the residual below the "
                "non-consumptive floor. The complementary split row is demoted "
                "because its adjacent-path component prevents a route_b-specific "
                "transfer margin."
            ),
            "claim_boundary": (
                "I6 supports only transfer/readout expression of consumptive "
                "SU3-limited rows pending I7 controls. It does not support SU5, "
                "SU6, final N22, the N21 ND6 bridge, semantic learning, choice, "
                "agency, native support, sentience, Phase 8, or ant-ecology "
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
        "# N22 Iteration 6 - Transfer / Re-entry Probe",
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
        "## Transfer Rows",
        "",
        "| Row | Source | Rung | Positive Contexts | Controls | Narrow |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in output["transfer_rows"]:
        lines.append(
            "| "
            f"`{row['row_id'].removeprefix('n22_i6_row_')}` | "
            f"`{row['source_iteration']}` | "
            f"`{row['provisional_su_ladder_rung']}` | "
            f"`{str(row['positive_transfer_contexts_passed']).lower()}` | "
            f"`{str(row['control_contexts_failed_closed']).lower()}` | "
            f"`{str(row['narrow_margin_candidate']).lower()}` |"
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
            "I6 does not run the full I7 control matrix and cannot assign SU6.",
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
