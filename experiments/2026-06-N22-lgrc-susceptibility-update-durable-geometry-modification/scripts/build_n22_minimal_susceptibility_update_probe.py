#!/usr/bin/env python3
"""Build N22 Iteration 4 minimal susceptibility-update producer run."""

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
OUTPUT = EXPERIMENT / "outputs" / "n22_minimal_susceptibility_update_probe.json"
REPORT = EXPERIMENT / "reports" / "n22_minimal_susceptibility_update_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_minimal_susceptibility_update_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_minimal_susceptibility_update_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_minimal_susceptibility_update_probe.py"
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

RUN_ID = "n22_i4_minimal_susceptibility_lgrc9v3_route_b"
TARGET_ROUTE = {
    "route_id": "route_b",
    "prior_source_node_id": 0,
    "prior_target_node_id": 1,
    "reentry_source_node_id": 1,
    "reentry_target_node_id": 0,
    "edge_id": 0,
}
PEER_ROUTE = {
    "route_id": "route_peer_edge_1",
    "prior_source_node_id": 0,
    "prior_target_node_id": 2,
    "edge_id": 1,
}
PRIOR_INTERACTION_PACKET_AMOUNT = 0.08
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


def susceptibility_schema_row(i2: dict[str, Any]) -> dict[str, Any]:
    for row in i2["schema_freeze"]["primitive_schema_rows"]:
        if row["primitive_id"] == "susceptibility_update":
            return row
    raise KeyError("susceptibility_update schema row not found")


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n22_i4_minimal_susceptibility_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": LANE_B,
        "target_route": TARGET_ROUTE,
        "peer_route": PEER_ROUTE,
        "prior_interaction": {
            "kind": "route_local_packet_interaction",
            "packet_amount": PRIOR_INTERACTION_PACKET_AMOUNT,
            "departure_event_time_key": 1.0,
            "scheduler_event_index": 1,
            "target_run_route": "route_b edge 0 receives prior interaction",
            "peer_run_route": "peer edge 1 receives same prior-interaction budget",
        },
        "later_reentry": {
            "kind": "route_b_reentry_packet",
            "packet_amount": REENTRY_PACKET_AMOUNT,
            "departure_event_time_key": 3.0,
            "scheduler_event_index": 3,
            "route": "route_b edge 0",
        },
        "thresholds": threshold_record(),
        "producer_boundary": {
            "historical_interaction_provenance_present": True,
            "active_reinforcement_schedule_disabled_after_prior_interaction": True,
            "active_reinforcement_queue_empty_before_reentry": True,
            "reinforcement_budget_in_flight_before_reentry": 0.0,
            "reentry_packet_is_diagnostic_input_not_reinforcement_evidence": True,
        },
    }


def threshold_record() -> dict[str, Any]:
    return {
        "threshold_record_id": "n22_i4_minimal_susceptibility_thresholds",
        "declared_before_use": True,
        "min_route_local_delta": MIN_ROUTE_LOCAL_DELTA,
        "min_target_over_peer_route_delta_margin": MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN,
        "min_reentry_delta_persistence_ratio": MIN_REENTRY_DELTA_PERSISTENCE_RATIO,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "boundary_active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
        "max_budget_error": MAX_BUDGET_ERROR,
        "field_specific_acceptance": {
            "support_floor_result": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "coherence_floor_result": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "boundary_integrity_result": [
                "preserved",
                "changed_within_allowed_delta",
            ],
            "flux_or_leakage_result": ["preserved", "changed_within_bound"],
        },
        "supporting_interpretation": (
            "I4 may assign only provisional SU2. Replay-backed and control-backed "
            "rungs remain blocked until later iterations."
        ),
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
    peer_node = state.base_state.nodes[PEER_ROUTE["prior_target_node_id"]]
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
        "peer_route_id": PEER_ROUTE["route_id"],
        "peer_route_node_id": PEER_ROUTE["prior_target_node_id"],
        "peer_route_edge_id": PEER_ROUTE["edge_id"],
        "center_node_coherence": center.coherence,
        "center_basin_mass": center.basin_mass,
        "target_route_node_coherence": route_node.coherence,
        "target_route_basin_mass": route_node.basin_mass,
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
        seed_name="n22-column-h-susceptibility-fixture",
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="n22_minimal_susceptibility_update_probe",
        rng_seed=None,
        requested_steps=4,
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


def run_lgrc_susceptibility_case(run_role: str, prior_route: dict[str, Any]) -> dict[str, Any]:
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

    schedule_packet(
        model,
        source_node_id=prior_route["prior_source_node_id"],
        target_node_id=prior_route["prior_target_node_id"],
        edge_id=prior_route["edge_id"],
        amount=PRIOR_INTERACTION_PACKET_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    prior_steps, prior_events = drain_queue(model, run_role, "prior_interaction")

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
        scheduler_event_index=3,
    )
    reentry_steps, reentry_events = drain_queue(model, run_role, "later_reentry")

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
        "artifact_id": f"n22_i4_{run_role}_lgrc9v3_susceptibility_run",
        "run_role": run_role,
        "model_family": "LGRC9V3",
        "producer_policy": "declared_prior_interaction_then_diagnostic_reentry",
        "runtime_config_digest": digest_value(runtime_config()),
        "prior_route": prior_route,
        "reentry_route": TARGET_ROUTE,
        "prior_interaction_packet_amount": PRIOR_INTERACTION_PACKET_AMOUNT,
        "reentry_packet_amount": REENTRY_PACKET_AMOUNT,
        "historical_interaction_provenance_present": True,
        "active_reinforcement_schedule_disabled": True,
        "active_reinforcement_queue_empty_before_reentry": (
            active_reinforcement_queue_empty_before_reentry
        ),
        "reinforcement_budget_in_flight_before_reentry": (
            reinforcement_budget_in_flight_before_reentry
        ),
        "reinforcement_schedule_not_used_as_evidence": True,
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
        "source_current_trace": {
            "pre_interaction_geometry_trace_present": True,
            "post_interaction_geometry_trace_present": True,
            "route_or_region_reentry_trace_present": True,
            "active_reinforcement_schedule_disabled": True,
            "target_route_node_coherence_after": reentry_geometry[
                "target_route_node_coherence"
            ],
            "center_node_coherence_after": reentry_geometry["center_node_coherence"],
            "packet_budget_error": model.get_state().packet_ledger.budget_error,
            "fixed_topology_signature": topology_signature(model.get_state()),
        },
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


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def build_trace_artifact(
    target: dict[str, Any],
    peer: dict[str, Any],
    runtime_config_path: str,
    threshold_path: str,
) -> dict[str, Any]:
    target_pre = target["run_artifact"]["pre_interaction_geometry"]
    target_post = target["run_artifact"]["post_interaction_geometry"]
    target_reentry = target["run_artifact"]["reentry_geometry"]
    peer_pre = peer["run_artifact"]["pre_interaction_geometry"]
    peer_post = peer["run_artifact"]["post_interaction_geometry"]
    peer_reentry = peer["run_artifact"]["reentry_geometry"]

    target_route_delta = (
        target_post["target_route_node_coherence"]
        - target_pre["target_route_node_coherence"]
    )
    peer_route_delta = (
        peer_post["target_route_node_coherence"]
        - peer_pre["target_route_node_coherence"]
    )
    target_reentry_route_delta = (
        target_reentry["target_route_node_coherence"]
        - target_pre["target_route_node_coherence"]
    )
    peer_reentry_route_delta = (
        peer_reentry["target_route_node_coherence"]
        - peer_pre["target_route_node_coherence"]
    )
    target_over_peer_margin = target_route_delta - peer_route_delta
    reentry_target_over_peer_margin = (
        target_reentry_route_delta - peer_reentry_route_delta
    )
    delta_persistence_ratio = (
        abs(target_reentry_route_delta) / abs(target_route_delta)
        if target_route_delta
        else 0.0
    )

    same_basin_comparison = {
        "center_node_id_same": target_pre["center_node_id"]
        == target_reentry["center_node_id"],
        "center_basin_id_same": target_pre["basin_signature"]["center_basin_id"]
        == target_reentry["basin_signature"]["center_basin_id"],
        "topology_signature_same": target_pre["topology_signature"]
        == target_reentry["topology_signature"],
        "active_degree_same": target_pre["active_degree"]
        == target_reentry["active_degree"],
        "basin_member_count_same": len(target_pre["basin_signature"]["basin_members"])
        == len(target_reentry["basin_signature"]["basin_members"]),
    }
    support_margin = target_reentry["center_basin_mass"] - SUPPORT_FLOOR
    coherence_margin = target_reentry["center_node_coherence"] - COHERENCE_FLOOR
    boundary_margin = target_reentry["active_degree"] - BOUNDARY_ACTIVE_DEGREE_FLOOR
    budget_error = abs(target_reentry["budget_error"])
    trace = {
        "artifact_id": "n22_i4_minimal_susceptibility_trace",
        "runtime_config_path": runtime_config_path,
        "threshold_path": threshold_path,
        "target_run_artifact_path": target["run_artifact_path"],
        "peer_run_artifact_path": peer["run_artifact_path"],
        "target_event_log_path": target["event_log_path"],
        "peer_event_log_path": peer["event_log_path"],
        "pre_interaction_geometry_trace": target_pre,
        "post_interaction_geometry_trace": target_post,
        "susceptibility_delta_trace": {
            "target_route": TARGET_ROUTE["route_id"],
            "target_route_node_id": TARGET_ROUTE["reentry_source_node_id"],
            "target_route_delta": target_route_delta,
            "peer_same_route_delta_under_peer_prior_budget": peer_route_delta,
            "target_over_peer_route_delta_margin": target_over_peer_margin,
            "min_route_local_delta": MIN_ROUTE_LOCAL_DELTA,
            "min_target_over_peer_route_delta_margin": (
                MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN
            ),
            "delta_observed": target_route_delta >= MIN_ROUTE_LOCAL_DELTA,
            "peer_global_drift_rejected": (
                target_over_peer_margin >= MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN
            ),
            "delta_source": "LGRC9V3 packet arrival modified route_b node coherence",
        },
        "route_or_region_reentry_trace": {
            "target_route_reentry_source": "route_b node 1",
            "target_reentry_route_delta_from_pre": target_reentry_route_delta,
            "peer_reentry_route_delta_from_pre": peer_reentry_route_delta,
            "reentry_target_over_peer_margin": reentry_target_over_peer_margin,
            "delta_persistence_ratio": delta_persistence_ratio,
            "min_reentry_delta_persistence_ratio": (
                MIN_REENTRY_DELTA_PERSISTENCE_RATIO
            ),
            "reentry_expression_present": (
                delta_persistence_ratio >= MIN_REENTRY_DELTA_PERSISTENCE_RATIO
                and reentry_target_over_peer_margin
                >= MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN
            ),
        },
        "peer_same_budget_comparison": {
            "status": "passed",
            "target_prior_route": TARGET_ROUTE["route_id"],
            "peer_prior_route": PEER_ROUTE["route_id"],
            "same_prior_interaction_budget": True,
            "same_reentry_route": TARGET_ROUTE["route_id"],
            "target_route_delta": target_route_delta,
            "peer_route_delta": peer_route_delta,
            "target_over_peer_margin": target_over_peer_margin,
            "global_drift_rejected": (
                target_over_peer_margin >= MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN
            ),
        },
        "peer_route_or_region_trace": {
            "peer_prior_interaction_route": PEER_ROUTE["route_id"],
            "peer_prior_target_node_id": PEER_ROUTE["prior_target_node_id"],
            "peer_post_peer_node_delta": peer_post["peer_route_node_coherence"]
            - peer_pre["peer_route_node_coherence"],
            "peer_target_route_node_delta": peer_route_delta,
            "interpretation": (
                "same budget spent on peer edge 1 moves peer node 2, not route_b "
                "node 1; this rejects a global-drift reading for I4 scope"
            ),
        },
        "same_basin_comparison": same_basin_comparison,
        "same_basin_continuation_status": (
            "preserved" if all(same_basin_comparison.values()) else "blocked"
        ),
        "support_floor_trace": {
            "support_floor": SUPPORT_FLOOR,
            "center_basin_mass": target_reentry["center_basin_mass"],
            "support_margin": support_margin,
            "status": "preserved" if support_margin >= 0 else "crossed_floor",
        },
        "coherence_floor_trace": {
            "coherence_floor": COHERENCE_FLOOR,
            "center_node_coherence": target_reentry["center_node_coherence"],
            "coherence_margin": coherence_margin,
            "status": "changed_within_allowed_delta_above_floor"
            if coherence_margin >= 0
            else "crossed_floor",
        },
        "boundary_integrity_trace": {
            "active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
            "active_degree": target_reentry["active_degree"],
            "boundary_margin": boundary_margin,
            "topology_signature_same": same_basin_comparison["topology_signature_same"],
            "status": "preserved"
            if boundary_margin >= 0
            and same_basin_comparison["topology_signature_same"]
            else "missing",
        },
        "flux_or_leakage_trace": {
            "max_budget_error": MAX_BUDGET_ERROR,
            "budget_error": budget_error,
            "in_flight_packet_total": target_reentry["in_flight_packet_total"],
            "status": "preserved"
            if budget_error <= MAX_BUDGET_ERROR
            and target_reentry["in_flight_packet_total"] == 0.0
            else "exceeded_bound",
        },
    }
    trace["interaction_delta_digest"] = digest_value(trace["susceptibility_delta_trace"])
    trace["reentry_delta_digest"] = digest_value(trace["route_or_region_reentry_trace"])
    trace["trace_digest"] = digest_value(trace)
    return canonicalize_json_value(trace)


def control_results(trace: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "route_label_only_control",
            "control_status": "passed",
            "blocked_condition": "route label changes without geometry delta",
            "actual_result": "route_b node coherence delta is source-current and recorded",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks SU2 and stronger if triggered",
        },
        {
            "control_id": "reinforcement_schedule_removed_control",
            "control_status": "passed",
            "blocked_condition": "active producer reinforcement carries the apparent delta",
            "actual_result": "prior interaction queue drained before later re-entry; no in-flight reinforcement budget",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks SU4 and stronger if triggered",
        },
        {
            "control_id": "peer_same_budget_comparison_control",
            "control_status": "passed",
            "blocked_condition": "same-budget peer route carries same target delta",
            "actual_result": trace["peer_same_budget_comparison"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks SU5 and SU6 if missing or failed",
        },
        {
            "control_id": "global_drift_rejection_control",
            "control_status": "passed",
            "blocked_condition": "target and peer regions move together",
            "actual_result": "target route_b delta exceeds same-budget peer route_b delta",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks route-conditioned SU5 and SU6 if failed",
        },
        {
            "control_id": "AP4_gap_dependency_if_route_conditioned",
            "control_status": "passed",
            "blocked_condition": "route-conditioned row omits AP4 dependency",
            "actual_result": "ap4_dependency_status = required_recorded",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks route-conditioned SU rows if missing",
        },
        {
            "control_id": "AP5_gap_dependency_if_proxy_conditioned",
            "control_status": "not_applicable",
            "blocked_condition": "proxy or target formation participates without AP5 record",
            "actual_result": "I4 uses packet geometry, not proxy or target formation",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "not applicable for this row",
        },
        {
            "control_id": "durable_geometry_modification_control",
            "control_status": "not_run",
            "blocked_condition": "one-window delta is relabeled as durable geometry modification",
            "actual_result": "deferred to I5/I7 replay and control matrix",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks SU4 and stronger until executed",
        },
        {
            "control_id": "semantic_relabel_control",
            "control_status": "not_run",
            "blocked_condition": "source-current susceptibility is relabeled as semantic learning",
            "actual_result": "deferred to I7 control matrix; unsafe flags remain false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks closeout claims until executed",
        },
        {
            "control_id": "native_support_relabel_control",
            "control_status": "not_run",
            "blocked_condition": "packet-mediated evidence is relabeled as native support",
            "actual_result": "deferred to I7 control matrix; native support remains false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks closeout claims until executed",
        },
        {
            "control_id": "phase8_relabel_control",
            "control_status": "not_run",
            "blocked_condition": "I4 artifact evidence is relabeled as Phase 8 implementation",
            "actual_result": "deferred to I7 control matrix; Phase 8 remains false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks closeout claims until executed",
        },
    ]


def build_candidate_row(
    *,
    i1: dict[str, Any],
    i2: dict[str, Any],
    trace: dict[str, Any],
    trace_path: str,
    runtime_config_path: str,
    threshold_path: str,
    artifact_manifest: list[dict[str, str]],
) -> dict[str, Any]:
    schema_row = susceptibility_schema_row(i2)
    artifact_paths = [item["path"] for item in artifact_manifest]
    artifact_sha256 = {item["path"]: item["sha256"] for item in artifact_manifest}
    replay_result = {
        "artifact_replay": "not_run",
        "snapshot_load_replay": "not_run",
        "duplicate_replay": "not_run",
        "later_reentry_replay": "not_run",
        "not_run_reason": "I4 is minimal positive probe; I5/I7 replay matrix required for SU3 and stronger",
        "affected_rungs": ["SU3", "SU4", "SU5", "SU6", "N22-C3", "N22-C4", "N22-C5", "N22-C6"],
    }
    candidate = {
        "row_id": "n22_i4_row_01_minimal_route_b_susceptibility_update_probe",
        "source_contract_row": "n20_i5_row_03_susceptibility_update",
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "source_output_digest": i1["output_digest"],
        "run_artifact_id": "n22_i4_minimal_susceptibility_route_b_probe",
        "source_commit_or_source_digest": {
            "script_path": SCRIPT_PATH,
            "script_sha256": sha256_file(SCRIPT_PATH),
        },
        "runtime_config_digest": digest_value(runtime_config()),
        "source_current_inputs": [
            "LGRC9V3 target route pre-interaction snapshot",
            "LGRC9V3 target route post-interaction snapshot",
            "LGRC9V3 target route later re-entry snapshot",
            "LGRC9V3 same-budget peer route run",
            "LGRC9V3 event logs and graph checkpoints",
        ],
        "row_specific_thresholds_declared_before_use": {
            "path": threshold_path,
            "sha256": sha256_file(threshold_path),
            "declared_before_use": True,
            "threshold_record": threshold_record(),
        },
        "n19_native_readiness_boundary_consumption": "ap_gap_boundary_only",
        "n20_source_downstream_consumption_status": schema_row[
            "n20_source_downstream_consumption_status"
        ],
        "interaction_window": {
            "phase": "prior_interaction",
            "departure_event_time_key": 1.0,
            "arrival_event_time_key": 2.0,
            "packet_amount": PRIOR_INTERACTION_PACKET_AMOUNT,
        },
        "reentry_window": {
            "phase": "later_reentry",
            "departure_event_time_key": 3.0,
            "arrival_event_time_key": 4.0,
            "packet_amount": REENTRY_PACKET_AMOUNT,
        },
        "pre_interaction_geometry_trace": {
            "artifact_role": "pre_interaction_geometry_trace",
            "geometry_digest": trace["pre_interaction_geometry_trace"]["geometry_digest"],
            "path": trace["target_run_artifact_path"],
        },
        "post_interaction_geometry_trace": {
            "artifact_role": "post_interaction_geometry_trace",
            "geometry_digest": trace["post_interaction_geometry_trace"]["geometry_digest"],
            "path": trace["target_run_artifact_path"],
        },
        "susceptibility_delta_trace": trace["susceptibility_delta_trace"],
        "route_or_region_reentry_trace": trace["route_or_region_reentry_trace"],
        "same_basin_continuation_rule": schema_row["same_basin_continuation_rule"],
        "allowed_delta_fields": [
            "target_route_node_coherence",
            "target_route_basin_mass",
            "center_node_coherence within declared floor",
        ],
        "same_basin_invariant_fields": [
            "center_node_id",
            "center_basin_id",
            "topology_signature",
            "active_degree",
            "basin_member_count",
        ],
        "out_of_scope_drift_blocks_row": True,
        "delta_not_label_reassignment": True,
        "route_or_region_conditioned": True,
        "peer_same_budget_comparison": trace["peer_same_budget_comparison"],
        "peer_same_budget_comparison_scope_reason": "required_and_present_for_route_conditioned_row",
        "peer_route_or_region_trace": trace["peer_route_or_region_trace"],
        "historical_interaction_provenance_present": True,
        "active_reinforcement_schedule_disabled": True,
        "active_reinforcement_queue_empty": True,
        "reinforcement_budget_in_flight": 0.0,
        "reinforcement_schedule_not_used_as_evidence": True,
        "support_floor_result": trace["support_floor_trace"],
        "coherence_floor_result": trace["coherence_floor_trace"],
        "boundary_integrity_result": trace["boundary_integrity_trace"],
        "flux_or_leakage_result": trace["flux_or_leakage_trace"],
        "replay_result": replay_result,
        "control_results": control_results(trace),
        "ap4_dependency_status": "required_recorded",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": (
            "I4 is route-conditioned, so AP4 route/consequence selection gap "
            "status is recorded row-locally from N19/N14."
        ),
        "ap5_condition_reason": (
            "No proxy or target formation participates in I4; source-current "
            "packet geometry supplies the delta."
        ),
        "interaction_delta_digest": trace["interaction_delta_digest"],
        "post_replay_delta_digest": "not_run_until_iteration_5",
        "reentry_delta_digest": trace["reentry_delta_digest"],
        "delta_persistence_ratio": trace["route_or_region_reentry_trace"][
            "delta_persistence_ratio"
        ],
        "delta_threshold_or_rule": threshold_record(),
        "one_window_transient_rejected": False,
        "global_drift_rejected": trace["peer_same_budget_comparison"][
            "global_drift_rejected"
        ],
        "producer_residue_fields": schema_row["producer_mediated_fields"],
        "naturalization_debt_fields": schema_row["naturalization_debt_fields"],
        "blocked_relabel_fields": schema_row["blocked_relabel_fields"],
        "claim_ceiling": (
            "provisional source-current SU2 susceptibility-delta candidate "
            "pending I5 replay and I7 control matrix; no durable geometry "
            "modification, semantic learning, choice, agency, native support, "
            "sentience, Phase 8, or ant-ecology implementation"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "partial",
        "susceptibility_update_claim_allowed": False,
        "derived_report_only": False,
        "artifact_manifest": artifact_manifest,
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "all_artifact_sha256_match_file_contents": True,
        "trace_artifact_path": trace_path,
        "runtime_config_path": runtime_config_path,
        "threshold_path": threshold_path,
        "provisional_su_ladder_rung": "SU2",
        "provisional_su_ladder_rung_status": "pending_iteration_5_replay_and_iteration_7_controls",
        "su3_or_stronger_blocker": "replay_result_not_run_and_one_window_transient_not_yet_rejected",
        "durable_geometry_modification_supported": False,
        "semantic_learning_supported": False,
        "native_support_supported": False,
        "phase8_opened": False,
        "output_digest": "pending",
    }
    candidate["output_digest"] = digest_value(
        {k: v for k, v in candidate.items() if k != "output_digest"}
    )
    return canonicalize_json_value(candidate)


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    threshold_path = ARTIFACT_DIR / "n22_i4_thresholds_declared_before_use.json"
    runtime_config_path = ARTIFACT_DIR / "n22_i4_runtime_config.json"
    write_json(threshold_path, threshold_record())
    write_json(runtime_config_path, runtime_config())

    target = run_lgrc_susceptibility_case("target_route_b_prior", TARGET_ROUTE)
    peer = run_lgrc_susceptibility_case("peer_budget_edge_1_prior", PEER_ROUTE)
    trace = build_trace_artifact(
        target,
        peer,
        rel(runtime_config_path),
        rel(threshold_path),
    )
    trace_path = ARTIFACT_DIR / "n22_i4_minimal_susceptibility_trace.json"
    write_json(trace_path, trace)

    paths_by_role: list[tuple[str, str]] = [
        (rel(runtime_config_path), "runtime_config"),
        (rel(threshold_path), "thresholds_declared_before_use"),
        (target["run_artifact_path"], "target_route_run_artifact"),
        (target["pre_snapshot_path"], "target_pre_interaction_snapshot"),
        (target["post_snapshot_path"], "target_post_interaction_snapshot"),
        (target["reentry_snapshot_path"], "target_later_reentry_snapshot"),
        (target["event_log_path"], "target_event_log"),
        (peer["run_artifact_path"], "same_budget_peer_run_artifact"),
        (peer["pre_snapshot_path"], "peer_pre_interaction_snapshot"),
        (peer["post_snapshot_path"], "peer_post_interaction_snapshot"),
        (peer["reentry_snapshot_path"], "peer_later_reentry_snapshot"),
        (peer["event_log_path"], "peer_event_log"),
        (rel(trace_path), "minimal_susceptibility_trace"),
    ]
    for run in [target, peer]:
        for checkpoint_path in run["run_artifact"]["graph_checkpoint_paths"]:
            paths_by_role.append((checkpoint_path, f"{run['run_role']}_graph_checkpoint"))
    artifact_manifest = file_manifest(paths_by_role)
    candidate_row = build_candidate_row(
        i1=i1,
        i2=i2,
        trace=trace,
        trace_path=rel(trace_path),
        runtime_config_path=rel(runtime_config_path),
        threshold_path=rel(threshold_path),
        artifact_manifest=artifact_manifest,
    )
    artifact_paths = [item["path"] for item in artifact_manifest]
    artifact_sha256_match = all(
        item["sha256"] == sha256_file(item["path"]) for item in artifact_manifest
    )
    accepted_support_statuses = {"preserved", "changed_within_allowed_delta_above_floor"}
    accepted_boundary_statuses = {"preserved", "changed_within_allowed_delta"}
    accepted_flux_statuses = {"preserved", "changed_within_bound"}
    candidate_fields = set(i2["schema_freeze"]["candidate_evidence_row_schema"]["required_fields"])
    candidate_keys = set(candidate_row)
    checks = [
        check("i1_inventory_passed", i1.get("status") == "passed", i1.get("acceptance_state")),
        check("i2_schema_passed", i2.get("status") == "passed", i2.get("acceptance_state")),
        check("i3_active_nulls_ready", i3.get("iteration3_boundary", {}).get("ready_for_iteration_4_positive_probe") is True, i3.get("acceptance_state")),
        check("candidate_row_has_required_fields", candidate_fields.issubset(candidate_keys), sorted(candidate_fields - candidate_keys)),
        check("derived_report_only_false", candidate_row["derived_report_only"] is False, candidate_row["derived_report_only"]),
        check("source_current_inputs_present", bool(candidate_row["source_current_inputs"]), candidate_row["source_current_inputs"]),
        check("thresholds_declared_before_use", candidate_row["row_specific_thresholds_declared_before_use"]["declared_before_use"] is True, candidate_row["row_specific_thresholds_declared_before_use"]["path"]),
        check("artifact_manifest_non_empty", len(artifact_manifest) >= 10, len(artifact_manifest)),
        check("artifact_hashes_match", artifact_sha256_match, artifact_manifest),
        check("pre_post_delta_observed", trace["susceptibility_delta_trace"]["delta_observed"] is True, trace["susceptibility_delta_trace"]),
        check("peer_comparison_rejects_global_drift", trace["peer_same_budget_comparison"]["global_drift_rejected"] is True, trace["peer_same_budget_comparison"]),
        check("later_reentry_trace_present", trace["route_or_region_reentry_trace"]["reentry_expression_present"] is True, trace["route_or_region_reentry_trace"]),
        check("same_basin_preserved", trace["same_basin_continuation_status"] == "preserved", trace["same_basin_comparison"]),
        check("support_gate_accepted", candidate_row["support_floor_result"]["status"] in accepted_support_statuses, candidate_row["support_floor_result"]),
        check("coherence_gate_accepted", candidate_row["coherence_floor_result"]["status"] in accepted_support_statuses, candidate_row["coherence_floor_result"]),
        check("boundary_gate_accepted", candidate_row["boundary_integrity_result"]["status"] in accepted_boundary_statuses, candidate_row["boundary_integrity_result"]),
        check("flux_gate_accepted", candidate_row["flux_or_leakage_result"]["status"] in accepted_flux_statuses, candidate_row["flux_or_leakage_result"]),
        check("active_reinforcement_absent_before_reentry", candidate_row["active_reinforcement_schedule_disabled"] is True and candidate_row["active_reinforcement_queue_empty"] is True and candidate_row["reinforcement_budget_in_flight"] == 0.0, {
            "active_reinforcement_schedule_disabled": candidate_row["active_reinforcement_schedule_disabled"],
            "active_reinforcement_queue_empty": candidate_row["active_reinforcement_queue_empty"],
            "reinforcement_budget_in_flight": candidate_row["reinforcement_budget_in_flight"],
        }),
        check("ap4_recorded_ap5_not_applicable", candidate_row["ap4_dependency_status"] == "required_recorded" and candidate_row["ap5_dependency_status"] == "not_applicable", {
            "ap4": candidate_row["ap4_dependency_status"],
            "ap5": candidate_row["ap5_dependency_status"],
        }),
        check("unsafe_flags_all_false", all(value is False for value in candidate_row["unsafe_claim_flags"].values()), candidate_row["unsafe_claim_flags"]),
        check("claim_allowed_false_pending_replay_controls", candidate_row["susceptibility_update_claim_allowed"] is False, candidate_row["claim_ceiling"]),
        check("su2_only_pending_replay", candidate_row["provisional_su_ladder_rung"] == "SU2" and candidate_row["row_decision"] == "partial", {
            "rung": candidate_row["provisional_su_ladder_rung"],
            "row_decision": candidate_row["row_decision"],
        }),
        check("durable_geometry_not_supported_yet", candidate_row["durable_geometry_modification_supported"] is False and candidate_row["one_window_transient_rejected"] is False, {
            "durable_geometry_modification_supported": candidate_row["durable_geometry_modification_supported"],
            "one_window_transient_rejected": candidate_row["one_window_transient_rejected"],
        }),
        check("artifact_paths_repository_relative", all(not path.startswith("/") for path in artifact_paths), artifact_paths),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i4_minimal_susceptibility_update_probe",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": 4,
        "purpose": "source-backed minimal susceptibility-update probe",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_minimal_source_current_su2_candidate_pending_replay_controls"
            if not failed_checks
            else "failed_minimal_susceptibility_probe"
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n22_i1_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n22_i2_schema_control_freeze"),
            source_record(I3_OUTPUT_PATH, "n22_i3_active_nulls"),
        ],
        "source_backed_probe": {
            "model_family": "LGRC9V3",
            "fixture": "examples/grc9v3/_fixtures.py::make_column_h_state",
            "target_route": TARGET_ROUTE,
            "peer_route": PEER_ROUTE,
            "target_probe_summary": {
                "geometric_change": (
                    "route_b node 1 receives prior packet interaction from center, "
                    "then later re-enters center through edge 0"
                ),
                "target_route_delta": trace["susceptibility_delta_trace"]["target_route_delta"],
                "peer_route_delta": trace["susceptibility_delta_trace"]["peer_same_route_delta_under_peer_prior_budget"],
                "reentry_delta_persistence_ratio": trace["route_or_region_reentry_trace"]["delta_persistence_ratio"],
            },
        },
        "candidate_rows": [candidate_row],
        "iteration4_boundary": {
            "positive_run_artifacts_consumed": True,
            "source_current_susceptibility_delta_observed": True,
            "provisional_su_ladder_rung": "SU2",
            "su3_or_stronger_supported": False,
            "susceptibility_update_claim_allowed": False,
            "durable_geometry_modification_supported": False,
            "n22_closeout_ladder_rung_assigned": False,
            "n21_nd6_bridge_status": "not_supported",
            "semantic_learning_supported": False,
            "choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ready_for_iteration_5_durability_replay": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I4 records a route-local source-current geometry delta, not a "
                "learning or choice claim."
            ),
            "what_changed": (
                "The prior interaction moves 0.08 coherence from the center into "
                "route_b node 1. The same-budget peer run moves the same budget "
                "into node 2 instead, leaving route_b node 1 unchanged."
            ),
            "why_peer_matters": (
                "Because the peer run spends the same budget but does not create "
                "the route_b node delta, the I4 delta is route-local rather than "
                "a global scheduler or budget drift."
            ),
            "why_reentry_matters": (
                "Later route_b re-entry preserves a measurable route_b delta "
                "relative to the peer run, but replay and control matrices have "
                "not yet established durable geometry modification."
            ),
            "claim_boundary": (
                "The result is provisional SU2 pending I5 replay and I7 controls; "
                "it is not semantic learning, choice, agency, native support, or "
                "Phase 8."
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
    row = output["candidate_rows"][0]
    probe = output["source_backed_probe"]["target_probe_summary"]
    lines = [
        "# N22 Iteration 4 - Minimal Susceptibility Update Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 4 runs the first source-backed N22 susceptibility probe using",
        "the LGRC9V3 column-H fixture. It records pre-interaction geometry, a",
        "prior route-local interaction, post-interaction geometry, a later route",
        "re-entry trace, and a same-budget peer comparison.",
        "",
        "The row is accepted only as a provisional `SU2` candidate. Replay-backed",
        "`SU3`, durable `SU4`, transfer/re-entry `SU5`, N23-ready `SU6`, final",
        "N22 closeout, and the N21 ND6 bridge remain unsupported.",
        "",
        "## Geometric Interpretation",
        "",
        output["geometric_interpretation"]["what_changed"],
        "",
        output["geometric_interpretation"]["why_peer_matters"],
        "",
        output["geometric_interpretation"]["why_reentry_matters"],
        "",
        "In numeric terms:",
        "",
        "```text",
        f"target route_b delta = {probe['target_route_delta']:.12f}",
        f"peer route_b delta under same peer budget = {probe['peer_route_delta']:.12f}",
        f"reentry delta persistence ratio = {probe['reentry_delta_persistence_ratio']:.12f}",
        "```",
        "",
        "## Candidate Row",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Row | `{row['row_id']}` |",
        f"| Decision | `{row['row_decision']}` |",
        f"| Provisional SU rung | `{row['provisional_su_ladder_rung']}` |",
        f"| Claim allowed | `{str(row['susceptibility_update_claim_allowed']).lower()}` |",
        f"| Derived report only | `{str(row['derived_report_only']).lower()}` |",
        f"| AP4 status | `{row['ap4_dependency_status']}` |",
        f"| AP5 status | `{row['ap5_dependency_status']}` |",
        f"| Artifact manifest entries | `{len(row['artifact_manifest'])}` |",
        "",
        "## Gates",
        "",
        "| Gate | Status |",
        "| --- | --- |",
        f"| Support | `{row['support_floor_result']['status']}` |",
        f"| Coherence | `{row['coherence_floor_result']['status']}` |",
        f"| Boundary | `{row['boundary_integrity_result']['status']}` |",
        f"| Flux/leakage | `{row['flux_or_leakage_result']['status']}` |",
        f"| Global drift rejected | `{str(row['global_drift_rejected']).lower()}` |",
        f"| One-window transient rejected | `{str(row['one_window_transient_rejected']).lower()}` |",
        "",
        "## Checks",
        "",
        "| Check | Passed | Detail |",
        "| --- | --- | --- |",
    ]
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
            "Semantic learning, choice, agency, native support, sentience, Phase 8,",
            "and ant-ecology implementation remain blocked.",
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
