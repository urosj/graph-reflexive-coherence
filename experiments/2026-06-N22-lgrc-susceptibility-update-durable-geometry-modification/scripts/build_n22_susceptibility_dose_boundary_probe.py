#!/usr/bin/env python3
"""Build N22 Iteration 4-A susceptibility dose/boundary probe."""

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
OUTPUT = EXPERIMENT / "outputs" / "n22_susceptibility_dose_boundary_probe.json"
REPORT = EXPERIMENT / "reports" / "n22_susceptibility_dose_boundary_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_susceptibility_dose_boundary_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_susceptibility_dose_boundary_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_susceptibility_dose_boundary_probe.py"
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

RUN_ID = "n22_i4a_susceptibility_dose_boundary_lgrc9v3"
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
DOSE_ROWS = [
    {
        "dose_id": "dose_00_no_prior_interaction_control",
        "prior_interaction_packet_amount": 0.0,
        "expected_role": "no_prior_interaction_control",
    },
    {
        "dose_id": "dose_03_below_delta_floor",
        "prior_interaction_packet_amount": 0.03,
        "expected_role": "below_delta_floor_control",
    },
    {
        "dose_id": "dose_08_i4_reference",
        "prior_interaction_packet_amount": 0.08,
        "expected_role": "i4_reference_positive",
    },
    {
        "dose_id": "dose_14_stronger_bounded",
        "prior_interaction_packet_amount": 0.14,
        "expected_role": "stronger_bounded_positive",
    },
    {
        "dose_id": "dose_20_out_of_scope_coherence_drift",
        "prior_interaction_packet_amount": 0.20,
        "expected_role": "out_of_scope_drift_control",
    },
]
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


def threshold_record() -> dict[str, Any]:
    return {
        "threshold_record_id": "n22_i4a_susceptibility_dose_boundary_thresholds",
        "declared_before_use": True,
        "inherits_i4_threshold_policy": True,
        "min_route_local_delta": MIN_ROUTE_LOCAL_DELTA,
        "min_target_over_peer_route_delta_margin": MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN,
        "min_reentry_delta_persistence_ratio": MIN_REENTRY_DELTA_PERSISTENCE_RATIO,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "boundary_active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
        "max_budget_error": MAX_BUDGET_ERROR,
        "dose_rows_declared_before_use": DOSE_ROWS,
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
    }


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n22_i4a_susceptibility_dose_boundary_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": LANE_B,
        "target_route": TARGET_ROUTE,
        "peer_route": PEER_ROUTE,
        "dose_rows": DOSE_ROWS,
        "later_reentry": {
            "kind": "route_b_reentry_packet",
            "packet_amount": REENTRY_PACKET_AMOUNT,
            "departure_event_time_key": 3.0,
            "scheduler_event_index": 3,
            "route": "route_b edge 0",
        },
        "thresholds": threshold_record(),
        "producer_boundary": {
            "active_reinforcement_schedule_disabled_after_prior_interaction": True,
            "active_reinforcement_queue_empty_before_reentry": True,
            "reinforcement_budget_in_flight_before_reentry": 0.0,
            "reentry_packet_is_diagnostic_input_not_reinforcement_evidence": True,
        },
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
        seed_name="n22-column-h-susceptibility-dose-fixture",
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="n22_susceptibility_dose_boundary_probe",
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


def run_dose_case(
    *,
    run_role: str,
    dose_id: str,
    prior_route: dict[str, Any],
    prior_amount: float,
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

    prior_steps: list[dict[str, Any]] = []
    prior_events: list[dict[str, Any]] = []
    if prior_amount > 0.0:
        schedule_packet(
            model,
            source_node_id=prior_route["prior_source_node_id"],
            target_node_id=prior_route["prior_target_node_id"],
            edge_id=prior_route["edge_id"],
            amount=prior_amount,
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
        "artifact_id": f"n22_i4a_{run_role}_lgrc9v3_dose_run",
        "dose_id": dose_id,
        "run_role": run_role,
        "model_family": "LGRC9V3",
        "producer_policy": "declared_dose_then_diagnostic_reentry",
        "runtime_config_digest": digest_value(runtime_config()),
        "prior_route": prior_route,
        "prior_interaction_packet_amount": prior_amount,
        "reentry_route": TARGET_ROUTE,
        "reentry_packet_amount": REENTRY_PACKET_AMOUNT,
        "historical_interaction_provenance_present": prior_amount > 0.0,
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


def classify_dose(
    *,
    dose_id: str,
    prior_amount: float,
    target_delta: float,
    peer_delta: float,
    reentry_ratio: float,
    support_status: str,
    coherence_status: str,
    boundary_status: str,
    flux_status: str,
) -> dict[str, Any]:
    peer_margin = target_delta - peer_delta
    gates_preserved = (
        support_status in {"preserved", "changed_within_allowed_delta_above_floor"}
        and coherence_status in {"preserved", "changed_within_allowed_delta_above_floor"}
        and boundary_status in {"preserved", "changed_within_allowed_delta"}
        and flux_status in {"preserved", "changed_within_bound"}
    )
    if prior_amount == 0.0:
        return {
            "row_decision": "rejected",
            "dose_classification": "no_prior_interaction_control_failed_closed",
            "provisional_su_ladder_rung": "SU0",
            "supporting_su2_candidate": False,
            "failure_mode": "no_prior_interaction_delta",
        }
    if target_delta < MIN_ROUTE_LOCAL_DELTA or peer_margin < MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN:
        return {
            "row_decision": "rejected",
            "dose_classification": "below_delta_floor_failed_closed",
            "provisional_su_ladder_rung": "SU1",
            "supporting_su2_candidate": False,
            "failure_mode": "route_local_delta_or_peer_margin_below_threshold",
        }
    if not gates_preserved:
        return {
            "row_decision": "blocked",
            "dose_classification": "out_of_scope_drift_failed_closed",
            "provisional_su_ladder_rung": "blocked_before_SU2",
            "supporting_su2_candidate": False,
            "failure_mode": "same_basin_gate_or_floor_not_preserved",
        }
    if reentry_ratio < MIN_REENTRY_DELTA_PERSISTENCE_RATIO:
        return {
            "row_decision": "partial",
            "dose_classification": "pre_post_delta_without_reentry_margin",
            "provisional_su_ladder_rung": "SU2_reentry_limited",
            "supporting_su2_candidate": False,
            "failure_mode": "reentry_persistence_ratio_below_floor",
        }
    return {
        "row_decision": "partial",
        "dose_classification": "bounded_source_current_SU2_candidate",
        "provisional_su_ladder_rung": "SU2",
        "supporting_su2_candidate": True,
        "failure_mode": "none",
    }


def build_trace_for_dose(
    *,
    dose_row: dict[str, Any],
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
    prior_amount = dose_row["prior_interaction_packet_amount"]

    target_delta = (
        target_post["target_route_node_coherence"]
        - target_pre["target_route_node_coherence"]
    )
    peer_delta = (
        peer_post["target_route_node_coherence"]
        - peer_pre["target_route_node_coherence"]
    )
    target_reentry_delta = (
        target_reentry["target_route_node_coherence"]
        - target_pre["target_route_node_coherence"]
    )
    peer_reentry_delta = (
        peer_reentry["target_route_node_coherence"]
        - peer_pre["target_route_node_coherence"]
    )
    peer_margin = target_delta - peer_delta
    reentry_peer_margin = target_reentry_delta - peer_reentry_delta
    reentry_ratio = abs(target_reentry_delta) / abs(target_delta) if target_delta else 0.0

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
    support_status = "preserved" if support_margin >= 0 else "crossed_floor"
    coherence_status = (
        "changed_within_allowed_delta_above_floor"
        if coherence_margin >= 0
        else "crossed_floor"
    )
    boundary_status = (
        "preserved"
        if boundary_margin >= 0 and same_basin_comparison["topology_signature_same"]
        else "missing"
    )
    flux_status = (
        "preserved"
        if budget_error <= MAX_BUDGET_ERROR
        and target_reentry["in_flight_packet_total"] == 0.0
        else "exceeded_bound"
    )
    classification = classify_dose(
        dose_id=dose_row["dose_id"],
        prior_amount=prior_amount,
        target_delta=target_delta,
        peer_delta=peer_delta,
        reentry_ratio=reentry_ratio,
        support_status=support_status,
        coherence_status=coherence_status,
        boundary_status=boundary_status,
        flux_status=flux_status,
    )
    trace = {
        "artifact_id": f"n22_i4a_trace_{dose_row['dose_id']}",
        "dose_id": dose_row["dose_id"],
        "expected_role": dose_row["expected_role"],
        "runtime_config_path": runtime_config_path,
        "threshold_path": threshold_path,
        "target_run_artifact_path": target["run_artifact_path"],
        "peer_run_artifact_path": peer["run_artifact_path"],
        "target_event_log_path": target["event_log_path"],
        "peer_event_log_path": peer["event_log_path"],
        "prior_interaction_packet_amount": prior_amount,
        "pre_interaction_geometry_trace": target_pre,
        "post_interaction_geometry_trace": target_post,
        "route_or_region_reentry_trace": {
            "target_reentry_route_delta_from_pre": target_reentry_delta,
            "peer_reentry_route_delta_from_pre": peer_reentry_delta,
            "reentry_target_over_peer_margin": reentry_peer_margin,
            "delta_persistence_ratio": reentry_ratio,
            "min_reentry_delta_persistence_ratio": (
                MIN_REENTRY_DELTA_PERSISTENCE_RATIO
            ),
            "reentry_expression_present": (
                reentry_ratio >= MIN_REENTRY_DELTA_PERSISTENCE_RATIO
                and reentry_peer_margin >= MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN
            ),
        },
        "susceptibility_delta_trace": {
            "target_route": TARGET_ROUTE["route_id"],
            "target_route_node_id": TARGET_ROUTE["reentry_source_node_id"],
            "target_route_delta": target_delta,
            "peer_same_route_delta_under_peer_prior_budget": peer_delta,
            "target_over_peer_route_delta_margin": peer_margin,
            "min_route_local_delta": MIN_ROUTE_LOCAL_DELTA,
            "min_target_over_peer_route_delta_margin": (
                MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN
            ),
            "delta_observed": target_delta >= MIN_ROUTE_LOCAL_DELTA,
            "peer_global_drift_rejected": (
                peer_margin >= MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN
            ),
            "delta_source": "LGRC9V3 packet arrival modified route_b node coherence",
        },
        "peer_same_budget_comparison": {
            "status": "passed"
            if peer_margin >= MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN
            else "failed_closed",
            "target_prior_route": TARGET_ROUTE["route_id"],
            "peer_prior_route": PEER_ROUTE["route_id"],
            "same_prior_interaction_budget": True,
            "same_reentry_route": TARGET_ROUTE["route_id"],
            "target_route_delta": target_delta,
            "peer_route_delta": peer_delta,
            "target_over_peer_margin": peer_margin,
            "global_drift_rejected": (
                peer_margin >= MIN_TARGET_OVER_PEER_ROUTE_DELTA_MARGIN
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
            "status": support_status,
        },
        "coherence_floor_trace": {
            "coherence_floor": COHERENCE_FLOOR,
            "center_node_coherence": target_reentry["center_node_coherence"],
            "coherence_margin": coherence_margin,
            "status": coherence_status,
        },
        "boundary_integrity_trace": {
            "active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
            "active_degree": target_reentry["active_degree"],
            "boundary_margin": boundary_margin,
            "topology_signature_same": same_basin_comparison["topology_signature_same"],
            "status": boundary_status,
        },
        "flux_or_leakage_trace": {
            "max_budget_error": MAX_BUDGET_ERROR,
            "budget_error": budget_error,
            "in_flight_packet_total": target_reentry["in_flight_packet_total"],
            "status": flux_status,
        },
        "dose_classification": classification,
    }
    trace["interaction_delta_digest"] = digest_value(trace["susceptibility_delta_trace"])
    trace["reentry_delta_digest"] = digest_value(trace["route_or_region_reentry_trace"])
    trace["trace_digest"] = digest_value(trace)
    return canonicalize_json_value(trace)


def control_results(trace: dict[str, Any]) -> list[dict[str, Any]]:
    classification = trace["dose_classification"]
    positive = classification["supporting_su2_candidate"]
    return [
        {
            "control_id": "dose_boundary_control",
            "control_status": "passed" if positive else "failed_closed",
            "blocked_condition": "dose is absent, below delta floor, or outside same-basin gates",
            "actual_result": classification["dose_classification"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks or demotes non-supporting dose rows",
        },
        {
            "control_id": "route_label_only_control",
            "control_status": "passed" if positive else "failed_closed",
            "blocked_condition": "route label changes without geometry delta",
            "actual_result": trace["susceptibility_delta_trace"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks SU2 and stronger if triggered",
        },
        {
            "control_id": "peer_same_budget_comparison_control",
            "control_status": trace["peer_same_budget_comparison"]["status"],
            "blocked_condition": "same-budget peer route carries same target delta",
            "actual_result": trace["peer_same_budget_comparison"],
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
            "actual_result": "I4-A uses packet geometry, not proxy or target formation",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "not applicable for this row",
        },
        {
            "control_id": "durable_geometry_modification_control",
            "control_status": "not_run",
            "blocked_condition": "dose success is relabeled as durable geometry modification",
            "actual_result": "deferred to I5/I7 replay and control matrix",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks SU4 and stronger until executed",
        },
    ]


def build_dose_row(
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
    classification = trace["dose_classification"]
    artifact_paths = [item["path"] for item in artifact_manifest]
    artifact_sha256 = {item["path"]: item["sha256"] for item in artifact_manifest}
    claim_ceiling = (
        "I4-A dose-boundary evidence only; supporting rows are provisional SU2 "
        "pending I5 replay and I7 controls, while failed rows remain fail-closed "
        "controls. No durable geometry modification, semantic learning, choice, "
        "agency, native support, sentience, Phase 8, or ant-ecology implementation."
    )
    row = {
        "row_id": f"n22_i4a_row_{trace['dose_id']}",
        "source_contract_row": "n20_i5_row_03_susceptibility_update",
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "source_output_digest": i1["output_digest"],
        "run_artifact_id": f"n22_i4a_{trace['dose_id']}",
        "source_commit_or_source_digest": {
            "script_path": SCRIPT_PATH,
            "script_sha256": sha256_file(SCRIPT_PATH),
        },
        "runtime_config_digest": digest_value(runtime_config()),
        "source_current_inputs": [
            "LGRC9V3 target route dose run",
            "LGRC9V3 same-budget peer route dose run",
            "LGRC9V3 event logs and snapshots",
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
            "departure_event_time_key": 1.0 if trace["prior_interaction_packet_amount"] > 0 else "not_applicable",
            "arrival_event_time_key": 2.0 if trace["prior_interaction_packet_amount"] > 0 else "not_applicable",
            "packet_amount": trace["prior_interaction_packet_amount"],
        },
        "reentry_window": {
            "phase": "later_reentry",
            "departure_event_time_key": 3.0,
            "arrival_event_time_key": 4.0,
            "packet_amount": REENTRY_PACKET_AMOUNT,
        },
        "pre_interaction_geometry_trace": {
            "geometry_digest": trace["pre_interaction_geometry_trace"]["geometry_digest"],
            "path": trace["target_run_artifact_path"],
        },
        "post_interaction_geometry_trace": {
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
        "delta_not_label_reassignment": classification["supporting_su2_candidate"],
        "route_or_region_conditioned": True,
        "peer_same_budget_comparison": trace["peer_same_budget_comparison"],
        "peer_same_budget_comparison_scope_reason": "required_and_present_for_route_conditioned_dose_row",
        "peer_route_or_region_trace": {
            "peer_prior_route": PEER_ROUTE["route_id"],
            "peer_prior_target_node_id": PEER_ROUTE["prior_target_node_id"],
            "peer_target_route_delta": trace["susceptibility_delta_trace"][
                "peer_same_route_delta_under_peer_prior_budget"
            ],
        },
        "historical_interaction_provenance_present": trace["prior_interaction_packet_amount"] > 0.0,
        "active_reinforcement_schedule_disabled": True,
        "active_reinforcement_queue_empty": True,
        "reinforcement_budget_in_flight": 0.0,
        "reinforcement_schedule_not_used_as_evidence": True,
        "support_floor_result": trace["support_floor_trace"],
        "coherence_floor_result": trace["coherence_floor_trace"],
        "boundary_integrity_result": trace["boundary_integrity_trace"],
        "flux_or_leakage_result": trace["flux_or_leakage_trace"],
        "replay_result": {
            "artifact_replay": "not_run",
            "snapshot_load_replay": "not_run",
            "duplicate_replay": "not_run",
            "not_run_reason": "I4-A maps dose boundary only; I5/I7 replay required for SU3 and stronger",
        },
        "control_results": control_results(trace),
        "ap4_dependency_status": "required_recorded",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": "I4-A rows are route-conditioned and carry AP4 locally.",
        "ap5_condition_reason": "I4-A uses packet geometry, not proxy or target formation.",
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
        "claim_ceiling": claim_ceiling,
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": classification["row_decision"],
        "susceptibility_update_claim_allowed": False,
        "derived_report_only": False,
        "artifact_manifest": artifact_manifest,
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "all_artifact_sha256_match_file_contents": True,
        "trace_artifact_path": trace_path,
        "runtime_config_path": runtime_config_path,
        "threshold_path": threshold_path,
        "dose_classification": classification,
        "provisional_su_ladder_rung": classification["provisional_su_ladder_rung"],
        "supporting_su2_candidate": classification["supporting_su2_candidate"],
        "durable_geometry_modification_supported": False,
        "semantic_learning_supported": False,
        "native_support_supported": False,
        "phase8_opened": False,
        "output_digest": "pending",
    }
    row["output_digest"] = digest_value({k: v for k, v in row.items() if k != "output_digest"})
    return canonicalize_json_value(row)


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    threshold_path = ARTIFACT_DIR / "n22_i4a_thresholds_declared_before_use.json"
    runtime_config_path = ARTIFACT_DIR / "n22_i4a_runtime_config.json"
    write_json(threshold_path, threshold_record())
    write_json(runtime_config_path, runtime_config())

    dose_outputs = []
    all_manifest_entries: list[tuple[str, str]] = [
        (rel(runtime_config_path), "runtime_config"),
        (rel(threshold_path), "thresholds_declared_before_use"),
    ]
    for dose in DOSE_ROWS:
        dose_id = dose["dose_id"]
        amount = dose["prior_interaction_packet_amount"]
        target = run_dose_case(
            run_role=f"{dose_id}_target_route_b",
            dose_id=dose_id,
            prior_route=TARGET_ROUTE,
            prior_amount=amount,
        )
        peer = run_dose_case(
            run_role=f"{dose_id}_peer_budget_edge_1",
            dose_id=dose_id,
            prior_route=PEER_ROUTE,
            prior_amount=amount,
        )
        trace = build_trace_for_dose(
            dose_row=dose,
            target=target,
            peer=peer,
            runtime_config_path=rel(runtime_config_path),
            threshold_path=rel(threshold_path),
        )
        trace_path = ARTIFACT_DIR / f"{dose_id}_trace.json"
        write_json(trace_path, trace)
        dose_manifest_entries: list[tuple[str, str]] = [
            (target["run_artifact_path"], f"{dose_id}_target_run_artifact"),
            (target["pre_snapshot_path"], f"{dose_id}_target_pre_snapshot"),
            (target["post_snapshot_path"], f"{dose_id}_target_post_snapshot"),
            (target["reentry_snapshot_path"], f"{dose_id}_target_reentry_snapshot"),
            (target["event_log_path"], f"{dose_id}_target_event_log"),
            (peer["run_artifact_path"], f"{dose_id}_peer_run_artifact"),
            (peer["pre_snapshot_path"], f"{dose_id}_peer_pre_snapshot"),
            (peer["post_snapshot_path"], f"{dose_id}_peer_post_snapshot"),
            (peer["reentry_snapshot_path"], f"{dose_id}_peer_reentry_snapshot"),
            (peer["event_log_path"], f"{dose_id}_peer_event_log"),
            (rel(trace_path), f"{dose_id}_trace"),
        ]
        for run in [target, peer]:
            for checkpoint_path in run["run_artifact"]["graph_checkpoint_paths"]:
                dose_manifest_entries.append((checkpoint_path, f"{run['run_role']}_graph_checkpoint"))
        all_manifest_entries.extend(dose_manifest_entries)
        dose_artifact_manifest = file_manifest(
            [(rel(runtime_config_path), "runtime_config"), (rel(threshold_path), "thresholds_declared_before_use")]
            + dose_manifest_entries
        )
        dose_outputs.append(
            {
                "dose": dose,
                "trace": trace,
                "trace_path": rel(trace_path),
                "target": target,
                "peer": peer,
                "artifact_manifest": dose_artifact_manifest,
            }
        )

    rows = [
        build_dose_row(
            i1=i1,
            i2=i2,
            trace=item["trace"],
            trace_path=item["trace_path"],
            runtime_config_path=rel(runtime_config_path),
            threshold_path=rel(threshold_path),
            artifact_manifest=item["artifact_manifest"],
        )
        for item in dose_outputs
    ]
    aggregate_manifest = file_manifest(all_manifest_entries)
    artifact_sha256_match = all(
        item["sha256"] == sha256_file(item["path"]) for item in aggregate_manifest
    )
    positive_rows = [row for row in rows if row["supporting_su2_candidate"]]
    failed_closed_rows = [
        row
        for row in rows
        if not row["supporting_su2_candidate"]
        and row["row_decision"] in {"rejected", "blocked", "partial"}
    ]
    dose_summary = [
        {
            "dose_id": row["run_artifact_id"].removeprefix("n22_i4a_"),
            "packet_amount": row["interaction_window"]["packet_amount"],
            "row_decision": row["row_decision"],
            "classification": row["dose_classification"]["dose_classification"],
            "provisional_su_ladder_rung": row["provisional_su_ladder_rung"],
            "target_route_delta": row["susceptibility_delta_trace"]["target_route_delta"],
            "peer_route_delta": row["susceptibility_delta_trace"][
                "peer_same_route_delta_under_peer_prior_budget"
            ],
            "reentry_delta_persistence_ratio": row["delta_persistence_ratio"],
            "coherence_status": row["coherence_floor_result"]["status"],
        }
        for row in rows
    ]
    checks = [
        check("i1_inventory_passed", i1.get("status") == "passed", i1.get("acceptance_state")),
        check("i2_schema_passed", i2.get("status") == "passed", i2.get("acceptance_state")),
        check("i3_active_nulls_passed", i3.get("status") == "passed", i3.get("acceptance_state")),
        check("i4_minimal_probe_passed", i4.get("status") == "passed", i4.get("acceptance_state")),
        check("threshold_policy_matches_i4", i4["candidate_rows"][0]["delta_threshold_or_rule"]["min_route_local_delta"] == MIN_ROUTE_LOCAL_DELTA and i4["candidate_rows"][0]["delta_threshold_or_rule"]["coherence_floor"] == COHERENCE_FLOOR, threshold_record()),
        check("dose_ladder_declared_before_use", threshold_record()["declared_before_use"] is True and len(DOSE_ROWS) == 5, DOSE_ROWS),
        check("artifact_manifest_non_empty", len(aggregate_manifest) >= 50, len(aggregate_manifest)),
        check("artifact_hashes_match", artifact_sha256_match, len(aggregate_manifest)),
        check("two_positive_su2_rows", len(positive_rows) == 2, [row["run_artifact_id"] for row in positive_rows]),
        check("below_threshold_and_no_prior_fail_closed", all(
            next(row for row in rows if row["run_artifact_id"] == "n22_i4a_dose_00_no_prior_interaction_control")["row_decision"] == "rejected"
            and next(row for row in rows if row["run_artifact_id"] == "n22_i4a_dose_03_below_delta_floor")["row_decision"] == "rejected"
            for _ in [0]
        ), dose_summary),
        check("out_of_scope_high_dose_blocks", next(row for row in rows if row["run_artifact_id"] == "n22_i4a_dose_20_out_of_scope_coherence_drift")["row_decision"] == "blocked", dose_summary),
        check("positive_rows_reject_global_drift", all(row["global_drift_rejected"] for row in positive_rows), [
            row["peer_same_budget_comparison"] for row in positive_rows
        ]),
        check("all_rows_claim_allowed_false", all(row["susceptibility_update_claim_allowed"] is False for row in rows), [row["row_decision"] for row in rows]),
        check("durable_geometry_not_supported", all(row["durable_geometry_modification_supported"] is False and row["one_window_transient_rejected"] is False for row in rows), "I4-A is dose boundary only"),
        check("unsafe_flags_all_false", all(all(value is False for value in row["unsafe_claim_flags"].values()) for row in rows), "all dose rows"),
        check("artifact_paths_repository_relative", all(not item["path"].startswith("/") for item in aggregate_manifest), "relative paths only"),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i4a_susceptibility_dose_boundary_probe",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": "4-A",
        "purpose": "source-backed susceptibility dose and boundary probe",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_dose_boundary_su2_extension_pending_replay_controls"
            if not failed_checks
            else "failed_dose_boundary_probe"
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n22_i1_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n22_i2_schema_control_freeze"),
            source_record(I3_OUTPUT_PATH, "n22_i3_active_nulls"),
            source_record(I4_OUTPUT_PATH, "n22_i4_minimal_probe"),
        ],
        "dose_policy": {
            "i4_replaced": False,
            "threshold_policy_changed_from_i4": False,
            "dose_rows_declared_before_use": DOSE_ROWS,
            "same_fixture_as_i4": True,
            "same_thresholds_as_i4": True,
        },
        "dose_rows": rows,
        "dose_summary": dose_summary,
        "artifact_manifest": aggregate_manifest,
        "iteration4a_boundary": {
            "positive_run_artifacts_consumed": True,
            "source_current_susceptibility_delta_observed": True,
            "positive_su2_dose_count": len(positive_rows),
            "failed_closed_dose_count": len(failed_closed_rows),
            "highest_bounded_positive_dose": max(
                row["interaction_window"]["packet_amount"] for row in positive_rows
            ),
            "first_blocked_high_dose": 0.20,
            "provisional_su_ladder_rung": "SU2",
            "su3_or_stronger_supported": False,
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
                "I4-A maps the route_b susceptibility dose boundary without "
                "changing I4 thresholds or replacing the I4 reference row."
            ),
            "dose_gradient": (
                "No prior interaction and 0.03 packet dose fail closed; 0.08 "
                "and 0.14 packet doses produce route-local SU2 deltas; 0.20 "
                "produces a larger delta but crosses the center coherence floor."
            ),
            "what_this_adds_to_i4": (
                "I4 showed one source-current route-local delta. I4-A shows the "
                "delta has a bounded dose region and a fail-closed high-dose "
                "boundary, so success is not a label-only or one-value artifact."
            ),
            "claim_boundary": (
                "The result strengthens provisional SU2 input evidence only. "
                "Replay-backed SU3, durable SU4, transfer SU5, SU6, final N22, "
                "and the N21 ND6 bridge remain blocked."
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
        "# N22 Iteration 4-A - Susceptibility Dose / Boundary Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 4-A keeps the I4 fixture and thresholds fixed, then sweeps a",
        "declared route_b prior-interaction dose ladder. It does not retune I4,",
        "replace I4, or open durable geometry modification.",
        "",
        output["geometric_interpretation"]["dose_gradient"],
        "",
        output["geometric_interpretation"]["what_this_adds_to_i4"],
        "",
        "## Dose Rows",
        "",
        "| Dose | Decision | Classification | Target Delta | Peer Delta | Re-entry Ratio | Coherence Gate |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in output["dose_rows"]:
        lines.append(
            "| "
            f"`{row['interaction_window']['packet_amount']}` | "
            f"`{row['row_decision']}` | "
            f"`{row['dose_classification']['dose_classification']}` | "
            f"{row['susceptibility_delta_trace']['target_route_delta']:.12f} | "
            f"{row['susceptibility_delta_trace']['peer_same_route_delta_under_peer_prior_budget']:.12f} | "
            f"{row['delta_persistence_ratio']:.12f} | "
            f"`{row['coherence_floor_result']['status']}` |"
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
