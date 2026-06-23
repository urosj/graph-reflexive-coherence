#!/usr/bin/env python3
"""Build N22 Iteration 5 durability replay probe."""

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
OUTPUT = EXPERIMENT / "outputs" / "n22_durability_replay_probe.json"
REPORT = EXPERIMENT / "reports" / "n22_durability_replay_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_durability_replay_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_durability_replay_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_durability_replay_probe.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_susceptibility_schema_and_controls.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_active_nulls_and_failure_baselines.json"
)
I4_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_minimal_susceptibility_update_probe.json"
)
I4A_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_susceptibility_dose_boundary_probe.json"
)
I4B_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_multipath_susceptibility_shape_probe.json"
)

GRC9V3_EXAMPLES = ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_column_h_state, make_config  # noqa: E402
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

RUN_ID = "n22_i5_durability_replay_lgrc9v3"
TARGET_ROUTE = {
    "route_id": "route_b",
    "prior_source_node_id": 0,
    "prior_target_node_id": 1,
    "reentry_source_node_id": 1,
    "reentry_target_node_id": 0,
    "edge_id": 0,
}
DEFAULT_PEER_ROUTE = {
    "route_id": "route_peer_edge_1",
    "prior_source_node_id": 0,
    "prior_target_node_id": 2,
    "edge_id": 1,
}
REENTRY_PACKET_AMOUNT = 0.04
MIN_ROUTE_LOCAL_DELTA = 0.05
MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN = 0.05
MIN_REENTRY_DELTA_PERSISTENCE_RATIO = 0.45
SUPPORT_FLOOR = 9.85
COHERENCE_FLOOR = 9.85
BOUNDARY_ACTIVE_DEGREE_FLOOR = 9
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


def threshold_record() -> dict[str, Any]:
    return {
        "threshold_record_id": "n22_i5_durability_replay_thresholds",
        "declared_before_use": True,
        "inherits_i4_i4a_i4b_threshold_policy": True,
        "min_route_local_delta": MIN_ROUTE_LOCAL_DELTA,
        "min_target_over_peer_route_delta_margin": MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN,
        "min_reentry_delta_persistence_ratio": MIN_REENTRY_DELTA_PERSISTENCE_RATIO,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "boundary_active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
        "max_budget_error": MAX_BUDGET_ERROR,
        "required_replay_modes": [
            "artifact_replay",
            "snapshot_load_replay",
            "duplicate_replay",
            "post_snapshot_reentry_replay_without_active_reinforcement",
        ],
        "supporting_interpretation": (
            "I5 may assign replay-backed provisional SU3 candidates. SU4 and "
            "stronger remain blocked until I7 control matrix."
        ),
    }


def runtime_config(candidate_ids: list[str]) -> dict[str, Any]:
    return {
        "config_id": "n22_i5_durability_replay_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": LANE_B,
        "candidate_ids": candidate_ids,
        "later_reentry": {
            "kind": "route_b_reentry_packet",
            "packet_amount": REENTRY_PACKET_AMOUNT,
            "departure_event_time_key": 3.0,
            "scheduler_event_index": 30,
            "route": "route_b edge 0",
        },
        "thresholds": threshold_record(),
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
    peer_node = state.base_state.nodes[2]
    ledger = state.packet_ledger
    assert ledger is not None
    packet_records = [record.to_record() for record in ledger.packet_records]
    event_records = [record.to_record() for record in ledger.packet_event_records]
    geometry = {
        "run_role": run_role,
        "phase": phase,
        "center_node_id": 0,
        "target_route_id": TARGET_ROUTE["route_id"],
        "target_route_node_id": TARGET_ROUTE["reentry_source_node_id"],
        "target_route_edge_id": TARGET_ROUTE["edge_id"],
        "center_node_coherence": center.coherence,
        "center_basin_mass": center.basin_mass,
        "target_route_node_coherence": route_node.coherence,
        "target_route_basin_mass": route_node.basin_mass,
        "peer_route_node_2_coherence": peer_node.coherence,
        "peer_route_node_2_basin_mass": peer_node.basin_mass,
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
        seed_name="n22-column-h-durability-replay-fixture",
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="n22_durability_replay_probe",
        rng_seed=None,
        requested_steps=6,
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


def drain_queue(model: LGRC9V3, run_role: str, phase: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    step_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        step_rows.append(step_summary(result, run_role, phase))
        event_rows.extend(event_to_record(event, run_role, phase) for event in result.events)
    return step_rows, event_rows


def schedule_segments(model: LGRC9V3, segments: list[dict[str, Any]]) -> None:
    for index, segment in enumerate(segments, start=1):
        schedule_packet(
            model,
            source_node_id=segment["source_node_id"],
            target_node_id=segment["target_node_id"],
            edge_id=segment["edge_id"],
            amount=segment["amount"],
            departure_event_time_key=1.0 + index * 0.01,
            scheduler_event_index=index,
        )


def run_segments_case(
    *,
    run_role: str,
    candidate_id: str,
    segments: list[dict[str, Any]],
) -> dict[str, Any]:
    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    pre_geometry = route_geometry(model, run_role, "pre_interaction")
    pre_snapshot_path = ARTIFACT_DIR / f"{run_role}_pre_interaction_snapshot.json"
    model.save(str(pre_snapshot_path))
    pre_checkpoint_path = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000000",
        checkpoint_label=f"{run_role}_pre_interaction",
        checkpoint_reason="pre_interaction",
    )
    schedule_segments(model, segments)
    prior_steps, prior_events = drain_queue(model, run_role, "prior_interaction_replay")
    post_geometry = route_geometry(model, run_role, "post_interaction")
    post_snapshot_path = ARTIFACT_DIR / f"{run_role}_post_interaction_snapshot.json"
    model.save(str(post_snapshot_path))
    prior_event_counts = dict(Counter(row["kind"] for row in prior_events))
    post_checkpoint_path = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000001",
        checkpoint_label=f"{run_role}_post_interaction",
        checkpoint_reason="after_prior_interaction_queue",
        event_counts=prior_event_counts,
    )
    active_reinforcement_queue_empty_before_reentry = (
        len(model.get_state().packet_ledger.event_queue_records) == 0
    )
    reinforcement_budget_in_flight_before_reentry = (
        model.get_state().packet_ledger.in_flight_packet_total
    )
    schedule_packet(
        model,
        source_node_id=TARGET_ROUTE["reentry_source_node_id"],
        target_node_id=TARGET_ROUTE["reentry_target_node_id"],
        edge_id=TARGET_ROUTE["edge_id"],
        amount=REENTRY_PACKET_AMOUNT,
        departure_event_time_key=3.0,
        scheduler_event_index=30,
    )
    reentry_steps, reentry_events = drain_queue(model, run_role, "later_reentry_replay")
    reentry_geometry = route_geometry(model, run_role, "later_reentry")
    reentry_snapshot_path = ARTIFACT_DIR / f"{run_role}_reentry_snapshot.json"
    model.save(str(reentry_snapshot_path))
    event_rows = prior_events + reentry_events
    event_counts = dict(Counter(row["kind"] for row in event_rows))
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    reentry_checkpoint_path = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000002",
        checkpoint_label=f"{run_role}_later_reentry",
        checkpoint_reason="after_route_b_reentry_queue",
        event_counts=event_counts,
    )
    run_artifact = {
        "artifact_id": f"n22_i5_{run_role}_duplicate_run",
        "candidate_id": candidate_id,
        "run_role": run_role,
        "model_family": "LGRC9V3",
        "producer_policy": "duplicate_prior_segments_then_diagnostic_reentry",
        "segments": segments,
        "total_prior_interaction_budget": sum(segment["amount"] for segment in segments),
        "reentry_packet_amount": REENTRY_PACKET_AMOUNT,
        "active_reinforcement_queue_empty_before_reentry": (
            active_reinforcement_queue_empty_before_reentry
        ),
        "reinforcement_budget_in_flight_before_reentry": (
            reinforcement_budget_in_flight_before_reentry
        ),
        "source_current_inputs_emitted": True,
        "derived_report_only": False,
        "pre_interaction_snapshot_path": rel(pre_snapshot_path),
        "post_interaction_snapshot_path": rel(post_snapshot_path),
        "reentry_snapshot_path": rel(reentry_snapshot_path),
        "event_log_path": rel(event_log_path),
        "graph_checkpoint_paths": [
            pre_checkpoint_path,
            post_checkpoint_path,
            reentry_checkpoint_path,
        ],
        "pre_interaction_geometry": pre_geometry,
        "post_interaction_geometry": post_geometry,
        "reentry_geometry": reentry_geometry,
        "step_summaries": prior_steps + reentry_steps,
        "event_counts_by_kind": event_counts,
        "final_observables": dict(model.compute_observables()),
    }
    run_artifact["run_artifact_digest"] = digest_value(run_artifact)
    run_artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(run_artifact_path, run_artifact)
    return {
        "run_role": run_role,
        "run_artifact": run_artifact,
        "run_artifact_path": rel(run_artifact_path),
        "pre_snapshot_path": rel(pre_snapshot_path),
        "post_snapshot_path": rel(post_snapshot_path),
        "reentry_snapshot_path": rel(reentry_snapshot_path),
        "event_log_path": rel(event_log_path),
    }


def run_post_snapshot_reentry_replay(
    *,
    candidate_id: str,
    source_post_snapshot_path: str,
) -> dict[str, Any]:
    run_role = f"{candidate_id}_post_snapshot_reentry_replay"
    model = LGRC9V3.load(str(ROOT / source_post_snapshot_path))
    queue_empty_before_reentry = len(model.get_state().packet_ledger.event_queue_records) == 0
    budget_in_flight_before_reentry = model.get_state().packet_ledger.in_flight_packet_total
    loaded_post_geometry = route_geometry(model, run_role, "loaded_post_interaction")
    loaded_post_snapshot_path = ARTIFACT_DIR / f"{run_role}_loaded_post_snapshot.json"
    model.save(str(loaded_post_snapshot_path))
    loaded_checkpoint_path = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000000",
        checkpoint_label=f"{run_role}_loaded_post_interaction",
        checkpoint_reason="loaded_post_interaction_snapshot",
    )
    schedule_packet(
        model,
        source_node_id=TARGET_ROUTE["reentry_source_node_id"],
        target_node_id=TARGET_ROUTE["reentry_target_node_id"],
        edge_id=TARGET_ROUTE["edge_id"],
        amount=REENTRY_PACKET_AMOUNT,
        departure_event_time_key=3.0,
        scheduler_event_index=30,
    )
    reentry_steps, reentry_events = drain_queue(model, run_role, "post_snapshot_reentry")
    reentry_geometry = route_geometry(model, run_role, "post_snapshot_reentry")
    reentry_snapshot_path = ARTIFACT_DIR / f"{run_role}_reentry_snapshot.json"
    model.save(str(reentry_snapshot_path))
    event_counts = dict(Counter(row["kind"] for row in reentry_events))
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, reentry_events)
    reentry_checkpoint_path = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000001",
        checkpoint_label=f"{run_role}_post_snapshot_reentry",
        checkpoint_reason="after_post_snapshot_reentry_queue",
        event_counts=event_counts,
    )
    replay_artifact = {
        "artifact_id": f"n22_i5_{run_role}",
        "candidate_id": candidate_id,
        "source_post_snapshot_path": source_post_snapshot_path,
        "queue_empty_before_reentry": queue_empty_before_reentry,
        "budget_in_flight_before_reentry": budget_in_flight_before_reentry,
        "active_reinforcement_schedule_disabled": True,
        "active_reinforcement_queue_empty": queue_empty_before_reentry,
        "reinforcement_budget_in_flight": budget_in_flight_before_reentry,
        "loaded_post_snapshot_path": rel(loaded_post_snapshot_path),
        "reentry_snapshot_path": rel(reentry_snapshot_path),
        "event_log_path": rel(event_log_path),
        "graph_checkpoint_paths": [loaded_checkpoint_path, reentry_checkpoint_path],
        "loaded_post_geometry": loaded_post_geometry,
        "reentry_geometry": reentry_geometry,
        "step_summaries": reentry_steps,
        "event_counts_by_kind": event_counts,
    }
    replay_artifact["replay_artifact_digest"] = digest_value(replay_artifact)
    replay_artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(replay_artifact_path, replay_artifact)
    return {
        "run_role": run_role,
        "replay_artifact": replay_artifact,
        "replay_artifact_path": rel(replay_artifact_path),
        "loaded_post_snapshot_path": rel(loaded_post_snapshot_path),
        "reentry_snapshot_path": rel(reentry_snapshot_path),
        "event_log_path": rel(event_log_path),
    }


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def metric_signature(
    *,
    pre_geometry: dict[str, Any],
    post_geometry: dict[str, Any],
    reentry_geometry: dict[str, Any],
    peer_pre_geometry: dict[str, Any],
    peer_post_geometry: dict[str, Any],
    peer_reentry_geometry: dict[str, Any],
) -> dict[str, Any]:
    target_delta = (
        post_geometry["target_route_node_coherence"]
        - pre_geometry["target_route_node_coherence"]
    )
    peer_delta = (
        peer_post_geometry["target_route_node_coherence"]
        - peer_pre_geometry["target_route_node_coherence"]
    )
    target_reentry_delta = (
        reentry_geometry["target_route_node_coherence"]
        - pre_geometry["target_route_node_coherence"]
    )
    peer_reentry_delta = (
        peer_reentry_geometry["target_route_node_coherence"]
        - peer_pre_geometry["target_route_node_coherence"]
    )
    support_margin = reentry_geometry["center_basin_mass"] - SUPPORT_FLOOR
    coherence_margin = reentry_geometry["center_node_coherence"] - COHERENCE_FLOOR
    boundary_margin = reentry_geometry["active_degree"] - BOUNDARY_ACTIVE_DEGREE_FLOOR
    budget_error = abs(reentry_geometry["budget_error"])
    signature = {
        "target_route_delta": target_delta,
        "peer_route_delta": peer_delta,
        "target_over_peer_route_delta_margin": target_delta - peer_delta,
        "target_reentry_route_delta_from_pre": target_reentry_delta,
        "peer_reentry_route_delta_from_pre": peer_reentry_delta,
        "reentry_target_over_peer_margin": target_reentry_delta - peer_reentry_delta,
        "delta_persistence_ratio": (
            abs(target_reentry_delta) / abs(target_delta) if target_delta else 0.0
        ),
        "support_margin": support_margin,
        "coherence_margin": coherence_margin,
        "boundary_margin": boundary_margin,
        "budget_error": budget_error,
        "in_flight_packet_total": reentry_geometry["in_flight_packet_total"],
        "support_floor_result": "preserved" if support_margin >= 0 else "crossed_floor",
        "coherence_floor_result": (
            "changed_within_allowed_delta_above_floor"
            if coherence_margin >= 0
            else "crossed_floor"
        ),
        "boundary_integrity_result": (
            "preserved"
            if boundary_margin >= 0
            and pre_geometry["topology_signature"] == reentry_geometry["topology_signature"]
            else "missing"
        ),
        "flux_or_leakage_result": (
            "preserved"
            if budget_error <= MAX_BUDGET_ERROR
            and reentry_geometry["in_flight_packet_total"] == 0.0
            else "exceeded_bound"
        ),
    }
    signature["signature_digest"] = digest_value(signature)
    return canonicalize_json_value(signature)


def source_signature(trace: dict[str, Any]) -> dict[str, Any]:
    peer_key = "peer_same_route_delta_under_peer_prior_budget"
    if peer_key not in trace["susceptibility_delta_trace"]:
        peer_key = "peer_same_route_delta_under_peer_path_budget"
    signature = {
        "target_route_delta": trace["susceptibility_delta_trace"]["target_route_delta"],
        "peer_route_delta": trace["susceptibility_delta_trace"][peer_key],
        "target_over_peer_route_delta_margin": trace["susceptibility_delta_trace"][
            "target_over_peer_route_delta_margin"
        ],
        "target_reentry_route_delta_from_pre": trace["route_or_region_reentry_trace"][
            "target_reentry_route_delta_from_pre"
        ],
        "peer_reentry_route_delta_from_pre": trace["route_or_region_reentry_trace"][
            "peer_reentry_route_delta_from_pre"
        ],
        "reentry_target_over_peer_margin": trace["route_or_region_reentry_trace"][
            "reentry_target_over_peer_margin"
        ],
        "delta_persistence_ratio": trace["route_or_region_reentry_trace"][
            "delta_persistence_ratio"
        ],
        "support_margin": trace["support_floor_trace"]["support_margin"],
        "coherence_margin": trace["coherence_floor_trace"]["coherence_margin"],
        "boundary_margin": trace["boundary_integrity_trace"]["boundary_margin"],
        "budget_error": trace["flux_or_leakage_trace"]["budget_error"],
        "in_flight_packet_total": trace["flux_or_leakage_trace"][
            "in_flight_packet_total"
        ],
        "support_floor_result": trace["support_floor_trace"]["status"],
        "coherence_floor_result": trace["coherence_floor_trace"]["status"],
        "boundary_integrity_result": trace["boundary_integrity_trace"]["status"],
        "flux_or_leakage_result": trace["flux_or_leakage_trace"]["status"],
    }
    signature["signature_digest"] = digest_value(signature)
    return canonicalize_json_value(signature)


def signatures_match(left: dict[str, Any], right: dict[str, Any]) -> bool:
    comparable_keys = [
        "target_route_delta",
        "peer_route_delta",
        "target_over_peer_route_delta_margin",
        "target_reentry_route_delta_from_pre",
        "peer_reentry_route_delta_from_pre",
        "reentry_target_over_peer_margin",
        "delta_persistence_ratio",
        "support_floor_result",
        "coherence_floor_result",
        "boundary_integrity_result",
        "flux_or_leakage_result",
    ]
    for key in comparable_keys:
        if isinstance(left[key], float) or isinstance(right[key], float):
            if abs(left[key] - right[key]) > 1e-12:
                return False
        elif left[key] != right[key]:
            return False
    return True


def stable_state_signature(geometry: dict[str, Any]) -> dict[str, Any]:
    peer_coherence = geometry.get(
        "peer_route_node_2_coherence",
        geometry.get("peer_route_node_coherence"),
    )
    peer_basin_mass = geometry.get(
        "peer_route_node_2_basin_mass",
        geometry.get("peer_route_basin_mass"),
    )
    signature = {
        "center_node_id": geometry["center_node_id"],
        "center_node_coherence": geometry["center_node_coherence"],
        "center_basin_mass": geometry["center_basin_mass"],
        "target_route_node_coherence": geometry["target_route_node_coherence"],
        "target_route_basin_mass": geometry["target_route_basin_mass"],
        "peer_route_node_2_coherence": peer_coherence,
        "peer_route_node_2_basin_mass": peer_basin_mass,
        "active_degree": geometry["active_degree"],
        "node_count": geometry["node_count"],
        "edge_count": geometry["edge_count"],
        "packet_count": geometry["packet_count"],
        "budget_error": geometry["budget_error"],
        "in_flight_packet_total": geometry["in_flight_packet_total"],
        "topology_signature": geometry["topology_signature"],
        "center_basin_id": geometry["basin_signature"]["center_basin_id"],
        "basin_members": geometry["basin_signature"]["basin_members"],
    }
    signature["stable_state_signature_digest"] = digest_value(signature)
    return canonicalize_json_value(signature)


def snapshot_load_status(source_run_artifact: dict[str, Any]) -> dict[str, Any]:
    run_role = source_run_artifact["run_role"]
    checks = []
    for phase, snapshot_key, geometry_key in [
        ("pre_interaction", "pre_interaction_snapshot_path", "pre_interaction_geometry"),
        ("post_interaction", "post_interaction_snapshot_path", "post_interaction_geometry"),
        ("later_reentry", "reentry_snapshot_path", "reentry_geometry"),
    ]:
        model = LGRC9V3.load(str(ROOT / source_run_artifact[snapshot_key]))
        loaded = route_geometry(model, run_role, phase)
        expected_signature = stable_state_signature(source_run_artifact[geometry_key])
        loaded_signature = stable_state_signature(loaded)
        checks.append(
            {
                "phase": phase,
                "snapshot_path": source_run_artifact[snapshot_key],
                "expected_geometry_digest": source_run_artifact[geometry_key][
                    "geometry_digest"
                ],
                "loaded_geometry_digest": loaded["geometry_digest"],
                "expected_stable_state_signature_digest": expected_signature[
                    "stable_state_signature_digest"
                ],
                "loaded_stable_state_signature_digest": loaded_signature[
                    "stable_state_signature_digest"
                ],
                "passed": loaded_signature["stable_state_signature_digest"]
                == expected_signature["stable_state_signature_digest"],
            }
        )
    return {
        "status": "passed" if all(item["passed"] for item in checks) else "failed_open",
        "phase_checks": checks,
    }


def source_manifest_status(row: dict[str, Any]) -> dict[str, Any]:
    entries = row["artifact_manifest"]
    checks = [
        {
            "path": item["path"],
            "expected_sha256": item["sha256"],
            "actual_sha256": sha256_file(item["path"]),
            "passed": sha256_file(item["path"]) == item["sha256"],
        }
        for item in entries
    ]
    return {
        "status": "passed" if all(item["passed"] for item in checks) else "failed_open",
        "checked_artifact_count": len(checks),
        "failed_artifacts": [item for item in checks if not item["passed"]],
    }


def collect_candidates(i4: dict[str, Any], i4a: dict[str, Any], i4b: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = []
    i4_row = i4["candidate_rows"][0]
    i4_trace = load_json(i4_row["trace_artifact_path"])
    candidates.append(
        {
            "candidate_id": "i4_minimal_route_b",
            "source_iteration": "I4",
            "source_row": i4_row,
            "source_output_digest": i4["output_digest"],
            "trace": i4_trace,
            "target_segments": [
                {
                    "edge_id": TARGET_ROUTE["edge_id"],
                    "source_node_id": TARGET_ROUTE["prior_source_node_id"],
                    "target_node_id": TARGET_ROUTE["prior_target_node_id"],
                    "amount": i4_row["interaction_window"]["packet_amount"],
                }
            ],
            "peer_segments": [
                {
                    "edge_id": DEFAULT_PEER_ROUTE["edge_id"],
                    "source_node_id": DEFAULT_PEER_ROUTE["prior_source_node_id"],
                    "target_node_id": DEFAULT_PEER_ROUTE["prior_target_node_id"],
                    "amount": i4_row["interaction_window"]["packet_amount"],
                }
            ],
            "source_scope_note": "minimal I4 route_b row",
        }
    )
    for row in i4a["dose_rows"]:
        if row["supporting_su2_candidate"]:
            trace = load_json(row["trace_artifact_path"])
            candidates.append(
                {
                    "candidate_id": row["run_artifact_id"].removeprefix("n22_i4a_"),
                    "source_iteration": "I4-A",
                    "source_row": row,
                    "source_output_digest": i4a["output_digest"],
                    "trace": trace,
                    "target_segments": [
                        {
                            "edge_id": TARGET_ROUTE["edge_id"],
                            "source_node_id": TARGET_ROUTE["prior_source_node_id"],
                            "target_node_id": TARGET_ROUTE["prior_target_node_id"],
                            "amount": row["interaction_window"]["packet_amount"],
                        }
                    ],
                    "peer_segments": [
                        {
                            "edge_id": DEFAULT_PEER_ROUTE["edge_id"],
                            "source_node_id": DEFAULT_PEER_ROUTE["prior_source_node_id"],
                            "target_node_id": DEFAULT_PEER_ROUTE["prior_target_node_id"],
                            "amount": row["interaction_window"]["packet_amount"],
                        }
                    ],
                    "source_scope_note": "I4-A positive dose row",
                }
            )
    for row in i4b["path_rows"]:
        if row["supporting_su2_candidate"]:
            trace = load_json(row["trace_artifact_path"])
            candidates.append(
                {
                    "candidate_id": row["run_artifact_id"].removeprefix("n22_i4b_"),
                    "source_iteration": "I4-B",
                    "source_row": row,
                    "source_output_digest": i4b["output_digest"],
                    "trace": trace,
                    "target_segments": row["interaction_window"]["target_segments"],
                    "peer_segments": row["interaction_window"]["peer_segments"],
                    "source_scope_note": "I4-B positive path-shape row",
                }
            )
    return candidates


def build_replay_row(
    *,
    candidate: dict[str, Any],
    runtime_config_path: str,
    threshold_path: str,
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    row = candidate["source_row"]
    trace = candidate["trace"]
    candidate_id = candidate["candidate_id"]
    source_target_run_artifact = load_json(trace["target_run_artifact_path"])
    source_peer_run_artifact = load_json(trace["peer_run_artifact_path"])
    source_manifest = source_manifest_status(row)
    snapshot_load = snapshot_load_status(source_target_run_artifact)
    duplicate_target = run_segments_case(
        run_role=f"{candidate_id}_duplicate_target",
        candidate_id=candidate_id,
        segments=candidate["target_segments"],
    )
    duplicate_peer = run_segments_case(
        run_role=f"{candidate_id}_duplicate_peer",
        candidate_id=candidate_id,
        segments=candidate["peer_segments"],
    )
    post_snapshot_reentry = run_post_snapshot_reentry_replay(
        candidate_id=candidate_id,
        source_post_snapshot_path=source_target_run_artifact[
            "post_interaction_snapshot_path"
        ],
    )
    source_sig = source_signature(trace)
    duplicate_sig = metric_signature(
        pre_geometry=duplicate_target["run_artifact"]["pre_interaction_geometry"],
        post_geometry=duplicate_target["run_artifact"]["post_interaction_geometry"],
        reentry_geometry=duplicate_target["run_artifact"]["reentry_geometry"],
        peer_pre_geometry=duplicate_peer["run_artifact"]["pre_interaction_geometry"],
        peer_post_geometry=duplicate_peer["run_artifact"]["post_interaction_geometry"],
        peer_reentry_geometry=duplicate_peer["run_artifact"]["reentry_geometry"],
    )
    post_snapshot_reentry_sig = {
        **source_sig,
        "target_reentry_route_delta_from_pre": (
            post_snapshot_reentry["replay_artifact"]["reentry_geometry"][
                "target_route_node_coherence"
            ]
            - trace["pre_interaction_geometry_trace"]["target_route_node_coherence"]
        ),
        "reentry_target_over_peer_margin": (
            post_snapshot_reentry["replay_artifact"]["reentry_geometry"][
                "target_route_node_coherence"
            ]
            - trace["pre_interaction_geometry_trace"]["target_route_node_coherence"]
            - source_sig["peer_reentry_route_delta_from_pre"]
        ),
    }
    post_snapshot_reentry_sig["delta_persistence_ratio"] = (
        abs(post_snapshot_reentry_sig["target_reentry_route_delta_from_pre"])
        / abs(source_sig["target_route_delta"])
        if source_sig["target_route_delta"]
        else 0.0
    )
    post_snapshot_reentry_sig["signature_digest"] = digest_value(
        post_snapshot_reentry_sig
    )
    duplicate_passed = signatures_match(source_sig, duplicate_sig)
    post_snapshot_reentry_passed = (
        abs(
            post_snapshot_reentry_sig["target_reentry_route_delta_from_pre"]
            - source_sig["target_reentry_route_delta_from_pre"]
        )
        <= 1e-12
        and post_snapshot_reentry["replay_artifact"]["active_reinforcement_queue_empty"]
        is True
        and post_snapshot_reentry["replay_artifact"]["reinforcement_budget_in_flight"]
        == 0.0
    )
    support_gates_pass = (
        source_sig["support_floor_result"] == "preserved"
        and source_sig["coherence_floor_result"]
        == "changed_within_allowed_delta_above_floor"
        and source_sig["boundary_integrity_result"] == "preserved"
        and source_sig["flux_or_leakage_result"] == "preserved"
    )
    replay_passed = (
        source_manifest["status"] == "passed"
        and snapshot_load["status"] == "passed"
        and duplicate_passed
        and post_snapshot_reentry_passed
        and support_gates_pass
    )
    artifact_paths_by_role = [
        (duplicate_target["run_artifact_path"], f"{candidate_id}_duplicate_target_run"),
        (duplicate_target["pre_snapshot_path"], f"{candidate_id}_duplicate_target_pre_snapshot"),
        (duplicate_target["post_snapshot_path"], f"{candidate_id}_duplicate_target_post_snapshot"),
        (duplicate_target["reentry_snapshot_path"], f"{candidate_id}_duplicate_target_reentry_snapshot"),
        (duplicate_target["event_log_path"], f"{candidate_id}_duplicate_target_event_log"),
        (duplicate_peer["run_artifact_path"], f"{candidate_id}_duplicate_peer_run"),
        (duplicate_peer["pre_snapshot_path"], f"{candidate_id}_duplicate_peer_pre_snapshot"),
        (duplicate_peer["post_snapshot_path"], f"{candidate_id}_duplicate_peer_post_snapshot"),
        (duplicate_peer["reentry_snapshot_path"], f"{candidate_id}_duplicate_peer_reentry_snapshot"),
        (duplicate_peer["event_log_path"], f"{candidate_id}_duplicate_peer_event_log"),
        (post_snapshot_reentry["replay_artifact_path"], f"{candidate_id}_post_snapshot_reentry_run"),
        (post_snapshot_reentry["loaded_post_snapshot_path"], f"{candidate_id}_loaded_post_snapshot"),
        (post_snapshot_reentry["reentry_snapshot_path"], f"{candidate_id}_post_snapshot_reentry_snapshot"),
        (post_snapshot_reentry["event_log_path"], f"{candidate_id}_post_snapshot_reentry_event_log"),
    ]
    for run in [duplicate_target, duplicate_peer]:
        for checkpoint_path in run["run_artifact"]["graph_checkpoint_paths"]:
            artifact_paths_by_role.append((checkpoint_path, f"{run['run_role']}_graph_checkpoint"))
    for checkpoint_path in post_snapshot_reentry["replay_artifact"]["graph_checkpoint_paths"]:
        artifact_paths_by_role.append((checkpoint_path, f"{post_snapshot_reentry['run_role']}_graph_checkpoint"))
    artifact_manifest = file_manifest(
        [(runtime_config_path, "runtime_config"), (threshold_path, "thresholds_declared_before_use")]
        + artifact_paths_by_role
    )
    replay_row = {
        "row_id": f"n22_i5_row_{candidate_id}",
        "source_iteration": candidate["source_iteration"],
        "source_candidate_row_id": row["row_id"],
        "source_candidate_run_artifact_id": row["run_artifact_id"],
        "source_output_digest": candidate["source_output_digest"],
        "source_trace_artifact_path": row["trace_artifact_path"],
        "source_scope_note": candidate["source_scope_note"],
        "target_segments": candidate["target_segments"],
        "peer_segments": candidate["peer_segments"],
        "artifact_replay": source_manifest,
        "snapshot_load_replay": snapshot_load,
        "duplicate_replay": {
            "status": "passed" if duplicate_passed else "failed_open",
            "source_signature": source_sig,
            "duplicate_signature": duplicate_sig,
            "duplicate_target_run_artifact_path": duplicate_target["run_artifact_path"],
            "duplicate_peer_run_artifact_path": duplicate_peer["run_artifact_path"],
        },
        "post_snapshot_reentry_replay_without_active_reinforcement": {
            "status": "passed" if post_snapshot_reentry_passed else "failed_open",
            "source_post_interaction_snapshot_path": source_target_run_artifact[
                "post_interaction_snapshot_path"
            ],
            "post_snapshot_reentry_run_artifact_path": post_snapshot_reentry[
                "replay_artifact_path"
            ],
            "active_reinforcement_schedule_disabled": True,
            "active_reinforcement_queue_empty": post_snapshot_reentry[
                "replay_artifact"
            ]["active_reinforcement_queue_empty"],
            "reinforcement_budget_in_flight": post_snapshot_reentry[
                "replay_artifact"
            ]["reinforcement_budget_in_flight"],
            "post_snapshot_reentry_signature": post_snapshot_reentry_sig,
        },
        "interaction_delta_digest": source_sig["signature_digest"],
        "post_replay_delta_digest": duplicate_sig["signature_digest"],
        "reentry_delta_digest": post_snapshot_reentry_sig["signature_digest"],
        "delta_persistence_ratio": source_sig["delta_persistence_ratio"],
        "delta_threshold_or_rule": threshold_record(),
        "one_window_transient_rejected": replay_passed,
        "support_floor_result": source_sig["support_floor_result"],
        "coherence_floor_result": source_sig["coherence_floor_result"],
        "boundary_integrity_result": source_sig["boundary_integrity_result"],
        "flux_or_leakage_result": source_sig["flux_or_leakage_result"],
        "row_decision": "partial" if replay_passed else "blocked",
        "provisional_su_ladder_rung": "SU3" if replay_passed else "demoted_before_SU3",
        "i5_consumable_role": (
            "replay_backed_SU3_candidate_pending_I7_controls"
            if replay_passed
            else "replay_failed_or_demoted"
        ),
        "durable_geometry_modification_supported": False,
        "su4_or_stronger_supported": False,
        "susceptibility_update_claim_allowed": False,
        "claim_ceiling": (
            "replay-backed provisional SU3 candidate pending I7 control matrix; "
            "no durable geometry modification, semantic learning, choice, "
            "agency, native support, sentience, Phase 8, or ant-ecology implementation"
        )
        if replay_passed
        else "replay failed or demoted before SU3; no susceptibility support",
        "unsafe_claim_flags": unsafe_claim_flags(),
        "artifact_manifest": artifact_manifest,
        "artifact_paths": [item["path"] for item in artifact_manifest],
        "artifact_sha256": {item["path"]: item["sha256"] for item in artifact_manifest},
        "all_artifact_sha256_match_file_contents": True,
        "narrow_margin_candidate": bool(
            row.get("margin_interpretation", {}).get("narrow_margin_candidate", False)
        ),
        "requires_i7_controls": True,
        "output_digest": "pending",
    }
    replay_row["output_digest"] = digest_value(
        {k: v for k, v in replay_row.items() if k != "output_digest"}
    )
    return canonicalize_json_value(replay_row), artifact_paths_by_role


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    i4a = load_json(I4A_OUTPUT_PATH)
    i4b = load_json(I4B_OUTPUT_PATH)
    candidates = collect_candidates(i4, i4a, i4b)
    runtime_config_path = ARTIFACT_DIR / "n22_i5_runtime_config.json"
    threshold_path = ARTIFACT_DIR / "n22_i5_thresholds_declared_before_use.json"
    write_json(runtime_config_path, runtime_config([candidate["candidate_id"] for candidate in candidates]))
    write_json(threshold_path, threshold_record())
    replay_rows = []
    all_artifact_paths_by_role: list[tuple[str, str]] = [
        (rel(runtime_config_path), "runtime_config"),
        (rel(threshold_path), "thresholds_declared_before_use"),
    ]
    for candidate in candidates:
        replay_row, artifact_paths_by_role = build_replay_row(
            candidate=candidate,
            runtime_config_path=rel(runtime_config_path),
            threshold_path=rel(threshold_path),
        )
        replay_rows.append(replay_row)
        all_artifact_paths_by_role.extend(artifact_paths_by_role)
    aggregate_manifest = file_manifest(all_artifact_paths_by_role)
    artifact_sha256_match = all(
        item["sha256"] == sha256_file(item["path"]) for item in aggregate_manifest
    )
    su3_rows = [
        row
        for row in replay_rows
        if row["provisional_su_ladder_rung"] == "SU3"
        and row["i5_consumable_role"] == "replay_backed_SU3_candidate_pending_I7_controls"
    ]
    demoted_rows = [row for row in replay_rows if row not in su3_rows]
    narrow_rows = [row for row in su3_rows if row["narrow_margin_candidate"]]
    replay_summary = [
        {
            "row_id": row["row_id"],
            "source_iteration": row["source_iteration"],
            "source_candidate_row_id": row["source_candidate_row_id"],
            "row_decision": row["row_decision"],
            "provisional_su_ladder_rung": row["provisional_su_ladder_rung"],
            "i5_consumable_role": row["i5_consumable_role"],
            "artifact_replay": row["artifact_replay"]["status"],
            "snapshot_load_replay": row["snapshot_load_replay"]["status"],
            "duplicate_replay": row["duplicate_replay"]["status"],
            "post_snapshot_reentry_replay": row[
                "post_snapshot_reentry_replay_without_active_reinforcement"
            ]["status"],
            "delta_persistence_ratio": row["delta_persistence_ratio"],
            "narrow_margin_candidate": row["narrow_margin_candidate"],
        }
        for row in replay_rows
    ]
    checks = [
        check("i1_inventory_passed", i1.get("status") == "passed", i1.get("acceptance_state")),
        check("i2_schema_passed", i2.get("status") == "passed", i2.get("acceptance_state")),
        check("i3_active_nulls_passed", i3.get("status") == "passed", i3.get("acceptance_state")),
        check("i4_minimal_probe_passed", i4.get("status") == "passed", i4.get("acceptance_state")),
        check("i4a_dose_probe_passed", i4a.get("status") == "passed", i4a.get("acceptance_state")),
        check("i4b_multipath_probe_passed", i4b.get("status") == "passed", i4b.get("acceptance_state")),
        check("positive_candidate_count", len(candidates) == 5, [candidate["candidate_id"] for candidate in candidates]),
        check("artifact_manifest_non_empty", len(aggregate_manifest) >= 80, len(aggregate_manifest)),
        check("artifact_hashes_match", artifact_sha256_match, len(aggregate_manifest)),
        check("all_candidates_artifact_replay_passed", all(row["artifact_replay"]["status"] == "passed" for row in replay_rows), replay_summary),
        check("all_candidates_snapshot_load_passed", all(row["snapshot_load_replay"]["status"] == "passed" for row in replay_rows), replay_summary),
        check("all_candidates_duplicate_replay_passed", all(row["duplicate_replay"]["status"] == "passed" for row in replay_rows), replay_summary),
        check("all_candidates_post_snapshot_reentry_passed", all(row["post_snapshot_reentry_replay_without_active_reinforcement"]["status"] == "passed" for row in replay_rows), replay_summary),
        check("all_candidates_one_window_transient_rejected", all(row["one_window_transient_rejected"] is True for row in replay_rows), replay_summary),
        check("all_candidates_promoted_only_to_su3", len(su3_rows) == len(replay_rows) and all(row["su4_or_stronger_supported"] is False for row in replay_rows), replay_summary),
        check("narrow_complementary_row_tracked", any("complementary_split" in row["source_candidate_row_id"] and row["narrow_margin_candidate"] for row in replay_rows), replay_summary),
        check("all_claims_still_blocked", all(row["susceptibility_update_claim_allowed"] is False and row["durable_geometry_modification_supported"] is False for row in replay_rows), replay_summary),
        check("unsafe_flags_all_false", all(all(value is False for value in row["unsafe_claim_flags"].values()) for row in replay_rows), "all replay rows"),
        check("artifact_paths_repository_relative", all(not item["path"].startswith("/") for item in aggregate_manifest), "relative paths only"),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i5_durability_replay_probe",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": 5,
        "purpose": "durability replay over provisional SU2 candidates",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_replay_backed_su3_candidates_pending_i7_controls"
            if not failed_checks
            else "failed_durability_replay_probe"
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n22_i1_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n22_i2_schema_control_freeze"),
            source_record(I3_OUTPUT_PATH, "n22_i3_active_nulls"),
            source_record(I4_OUTPUT_PATH, "n22_i4_minimal_probe"),
            source_record(I4A_OUTPUT_PATH, "n22_i4a_dose_boundary_probe"),
            source_record(I4B_OUTPUT_PATH, "n22_i4b_multipath_shape_probe"),
        ],
        "replay_policy": {
            "positive_inputs_consumed": [
                candidate["candidate_id"] for candidate in candidates
            ],
            "required_replay_modes": threshold_record()["required_replay_modes"],
            "threshold_policy_changed_from_i4": False,
            "non_positive_i4a_i4b_rows_consumed_as_controls_only": True,
            "i5_does_not_run_full_i7_control_matrix": True,
        },
        "replay_rows": replay_rows,
        "replay_summary": replay_summary,
        "artifact_manifest": aggregate_manifest,
        "iteration5_boundary": {
            "positive_candidate_count": len(candidates),
            "replay_backed_su3_candidate_count": len(su3_rows),
            "demoted_candidate_count": len(demoted_rows),
            "narrow_margin_candidate_count": len(narrow_rows),
            "one_window_transient_rejected_count": sum(
                1 for row in replay_rows if row["one_window_transient_rejected"]
            ),
            "provisional_su_ladder_rung": "SU3",
            "su4_or_stronger_supported": False,
            "durable_geometry_modification_supported": False,
            "n22_closeout_ladder_rung_assigned": False,
            "n21_nd6_bridge_status": "not_supported",
            "semantic_learning_supported": False,
            "choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ready_for_iteration_6_transfer_reentry_probe": not failed_checks,
            "ready_for_iteration_7_control_matrix": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I5 turns the I4/I4-A/I4-B provisional SU2 inputs into replay-"
                "backed provisional SU3 candidates, but does not close durable "
                "geometry modification."
            ),
            "what_replay_tests": (
                "The source artifact manifests are rehashed, source snapshots are "
                "loaded, duplicate target/peer runs reproduce the source delta "
                "signatures, and later re-entry is rerun from the post-interaction "
                "snapshot with no active prior-interaction queue."
            ),
            "one_window_transient_read": (
                "The route-local delta is not only a single in-memory window: it "
                "survives artifact reconstruction, duplicate replay, and a post-"
                "snapshot re-entry replay. Full control-backed SU4 still waits "
                "for I7."
            ),
            "claim_boundary": (
                "I5 supports replay-backed provisional SU3 candidates only. It "
                "does not support durable SU4, transfer SU5, SU6, final N22, the "
                "N21 ND6 bridge, semantic learning, choice, agency, native support, "
                "sentience, Phase 8, or ant-ecology implementation."
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
        "# N22 Iteration 5 - Durability Replay Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 5 replays the positive provisional SU2 rows from I4, I4-A,",
        "and I4-B. Each row must pass artifact rehashing, snapshot/load replay,",
        "duplicate replay, and post-snapshot route_b re-entry without active",
        "prior-interaction reinforcement.",
        "",
        output["geometric_interpretation"]["one_window_transient_read"],
        "",
        "## Replay Rows",
        "",
        "| Row | Source | Rung | Artifact | Snapshot | Duplicate | Post-Snapshot Re-entry | Ratio | Narrow |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for row in output["replay_rows"]:
        lines.append(
            "| "
            f"`{row['row_id'].removeprefix('n22_i5_row_')}` | "
            f"`{row['source_iteration']}` | "
            f"`{row['provisional_su_ladder_rung']}` | "
            f"`{row['artifact_replay']['status']}` | "
            f"`{row['snapshot_load_replay']['status']}` | "
            f"`{row['duplicate_replay']['status']}` | "
            f"`{row['post_snapshot_reentry_replay_without_active_reinforcement']['status']}` | "
            f"{row['delta_persistence_ratio']:.12f} | "
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
            "I5 does not run the full I7 control matrix. Every row keeps",
            "`susceptibility_update_claim_allowed = false` and",
            "`durable_geometry_modification_supported = false`.",
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
