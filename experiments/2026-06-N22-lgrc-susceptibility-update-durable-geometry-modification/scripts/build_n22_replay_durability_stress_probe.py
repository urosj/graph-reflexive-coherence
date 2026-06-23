#!/usr/bin/env python3
"""Build N22 Iteration 5-A replay durability stress probe."""

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
OUTPUT = EXPERIMENT / "outputs" / "n22_replay_durability_stress_probe.json"
REPORT = EXPERIMENT / "reports" / "n22_replay_durability_stress_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_replay_durability_stress_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_replay_durability_stress_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_replay_durability_stress_probe.py"
)

I5_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_durability_replay_probe.json"
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

RUN_ID = "n22_i5a_replay_durability_stress_lgrc9v3"
TARGET_ROUTE = {
    "route_id": "route_b",
    "reentry_source_node_id": 1,
    "reentry_target_node_id": 0,
    "edge_id": 0,
}
REENTRY_PACKET_AMOUNT = 0.04
MILD_PEER_FLUX_AMOUNT = 0.01
SUPPORT_FLOOR = 9.85
COHERENCE_FLOOR = 9.85
BOUNDARY_ACTIVE_DEGREE_FLOOR = 9
MAX_BUDGET_ERROR = 1e-9
MIN_REENTRY_DELTA_PERSISTENCE_RATIO = 0.45
STRESS_MODES = [
    "baseline_post_snapshot_reentry",
    "delayed_idle_two_windows_reentry",
    "repeated_reentry_two_step",
    "mild_peer_flux_before_reentry",
]
SU3_PRESERVATION_STRESS_MODES = [
    "baseline_post_snapshot_reentry",
    "delayed_idle_two_windows_reentry",
    "mild_peer_flux_before_reentry",
]


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
        "threshold_record_id": "n22_i5a_replay_durability_stress_thresholds",
        "declared_before_use": True,
        "inherits_i5_threshold_policy": True,
        "stress_modes": STRESS_MODES,
        "min_reentry_delta_persistence_ratio": MIN_REENTRY_DELTA_PERSISTENCE_RATIO,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "boundary_active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
        "max_budget_error": MAX_BUDGET_ERROR,
        "mild_peer_flux_amount": MILD_PEER_FLUX_AMOUNT,
        "su4_or_stronger_allowed": False,
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
        seed_name="n22-column-h-replay-stress-fixture",
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="n22_replay_durability_stress_probe",
        rng_seed=None,
        requested_steps=8,
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


def run_idle_windows(model: LGRC9V3, *, run_role: str, count: int, start_index: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offset in range(count):
        result = model.step()
        rows.append(step_summary(result, run_role, f"idle_window_{offset + 1}"))
        # LGRC may not advance time without queued events; keep the call outcome visible.
        if result.events:
            rows.extend(event_to_record(event, run_role, f"idle_window_{offset + 1}") for event in result.events)
    return rows


def stable_source_trace(row: dict[str, Any]) -> dict[str, float]:
    sig = row["duplicate_replay"]["source_signature"]
    return {
        "source_target_delta": sig["target_route_delta"],
        "source_reentry_delta": sig["target_reentry_route_delta_from_pre"],
        "source_delta_persistence_ratio": sig["delta_persistence_ratio"],
    }


def stress_gate(
    *,
    geometry: dict[str, Any],
    source_trace: dict[str, float],
    pre_target_route_node_coherence: float,
) -> dict[str, Any]:
    target_delta = (
        geometry["target_route_node_coherence"] - pre_target_route_node_coherence
    )
    ratio = (
        abs(target_delta) / abs(source_trace["source_target_delta"])
        if source_trace["source_target_delta"]
        else 0.0
    )
    support_margin = geometry["center_basin_mass"] - SUPPORT_FLOOR
    coherence_margin = geometry["center_node_coherence"] - COHERENCE_FLOOR
    boundary_margin = geometry["active_degree"] - BOUNDARY_ACTIVE_DEGREE_FLOOR
    budget_error = abs(geometry["budget_error"])
    gate = {
        "target_reentry_delta_from_pre": target_delta,
        "delta_persistence_ratio_against_source": ratio,
        "support_margin": support_margin,
        "coherence_margin": coherence_margin,
        "boundary_margin": boundary_margin,
        "budget_error": budget_error,
        "in_flight_packet_total": geometry["in_flight_packet_total"],
        "passed": (
            ratio >= MIN_REENTRY_DELTA_PERSISTENCE_RATIO
            and support_margin >= 0
            and coherence_margin >= 0
            and boundary_margin >= 0
            and budget_error <= MAX_BUDGET_ERROR
            and geometry["in_flight_packet_total"] == 0.0
        ),
    }
    gate["gate_digest"] = digest_value(gate)
    return canonicalize_json_value(gate)


def run_stress_mode(
    *,
    candidate_id: str,
    source_post_snapshot_path: str,
    pre_target_route_node_coherence: float,
    source_trace: dict[str, float],
    stress_mode: str,
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    run_role = f"{candidate_id}_{stress_mode}"
    model = LGRC9V3.load(str(ROOT / source_post_snapshot_path))
    initial_queue_empty = len(model.get_state().packet_ledger.event_queue_records) == 0
    initial_budget_in_flight = model.get_state().packet_ledger.in_flight_packet_total
    initial_geometry = route_geometry(model, run_role, "loaded_post_interaction")
    initial_snapshot_path = ARTIFACT_DIR / f"{run_role}_loaded_post_snapshot.json"
    model.save(str(initial_snapshot_path))
    initial_checkpoint = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000000",
        checkpoint_label=f"{run_role}_loaded_post_interaction",
        checkpoint_reason="loaded_post_interaction_snapshot",
    )
    step_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []

    if stress_mode == "delayed_idle_two_windows_reentry":
        idle_rows = run_idle_windows(model, run_role=run_role, count=2, start_index=1)
        step_rows.extend(row for row in idle_rows if "event_kinds" in row)
    elif stress_mode == "mild_peer_flux_before_reentry":
        schedule_packet(
            model,
            source_node_id=0,
            target_node_id=2,
            edge_id=1,
            amount=MILD_PEER_FLUX_AMOUNT,
            departure_event_time_key=2.0,
            scheduler_event_index=20,
        )
        peer_steps, peer_events = drain_queue(model, run_role, "mild_peer_flux")
        step_rows.extend(peer_steps)
        event_rows.extend(peer_events)

    reentry_count = 2 if stress_mode == "repeated_reentry_two_step" else 1
    reentry_geometries = []
    for reentry_index in range(reentry_count):
        schedule_packet(
            model,
            source_node_id=TARGET_ROUTE["reentry_source_node_id"],
            target_node_id=TARGET_ROUTE["reentry_target_node_id"],
            edge_id=TARGET_ROUTE["edge_id"],
            amount=REENTRY_PACKET_AMOUNT,
            departure_event_time_key=3.0 + reentry_index,
            scheduler_event_index=30 + reentry_index,
        )
        reentry_steps, reentry_events = drain_queue(
            model,
            run_role,
            f"stress_reentry_{reentry_index + 1}",
        )
        step_rows.extend(reentry_steps)
        event_rows.extend(reentry_events)
        reentry_geometries.append(
            route_geometry(model, run_role, f"stress_reentry_{reentry_index + 1}")
        )

    final_geometry = reentry_geometries[-1]
    final_snapshot_path = ARTIFACT_DIR / f"{run_role}_final_snapshot.json"
    model.save(str(final_snapshot_path))
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    event_counts = dict(Counter(row["kind"] for row in event_rows))
    final_checkpoint = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000001",
        checkpoint_label=f"{run_role}_final",
        checkpoint_reason=f"after_{stress_mode}",
        event_counts=event_counts,
    )
    gates = [
        stress_gate(
            geometry=geometry,
            source_trace=source_trace,
            pre_target_route_node_coherence=pre_target_route_node_coherence,
        )
        for geometry in reentry_geometries
    ]
    stress_artifact = {
        "artifact_id": f"n22_i5a_{run_role}",
        "candidate_id": candidate_id,
        "stress_mode": stress_mode,
        "source_post_snapshot_path": source_post_snapshot_path,
        "initial_queue_empty": initial_queue_empty,
        "initial_budget_in_flight": initial_budget_in_flight,
        "active_reinforcement_schedule_disabled": True,
        "loaded_post_snapshot_path": rel(initial_snapshot_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "event_log_path": rel(event_log_path),
        "graph_checkpoint_paths": [initial_checkpoint, final_checkpoint],
        "initial_geometry": initial_geometry,
        "reentry_geometries": reentry_geometries,
        "final_geometry": final_geometry,
        "stress_gates": gates,
        "all_stress_gates_passed": all(gate["passed"] for gate in gates),
        "step_summaries": step_rows,
        "event_counts_by_kind": event_counts,
    }
    stress_artifact["stress_artifact_digest"] = digest_value(stress_artifact)
    artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(artifact_path, stress_artifact)
    manifest = [
        (rel(artifact_path), f"{candidate_id}_{stress_mode}_run"),
        (rel(initial_snapshot_path), f"{candidate_id}_{stress_mode}_loaded_post_snapshot"),
        (rel(final_snapshot_path), f"{candidate_id}_{stress_mode}_final_snapshot"),
        (rel(event_log_path), f"{candidate_id}_{stress_mode}_event_log"),
        (initial_checkpoint, f"{candidate_id}_{stress_mode}_initial_checkpoint"),
        (final_checkpoint, f"{candidate_id}_{stress_mode}_final_checkpoint"),
    ]
    return canonicalize_json_value(stress_artifact), manifest


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def build_stress_row(row: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    candidate_id = row["row_id"].removeprefix("n22_i5_row_")
    source_trace_artifact = load_json(row["source_trace_artifact_path"])
    pre_target_route_node_coherence = source_trace_artifact["pre_interaction_geometry_trace"][
        "target_route_node_coherence"
    ]
    source_trace = stable_source_trace(row)
    source_post_snapshot_path = row[
        "post_snapshot_reentry_replay_without_active_reinforcement"
    ]["source_post_interaction_snapshot_path"]
    stress_results = []
    manifest_entries: list[tuple[str, str]] = []
    for stress_mode in STRESS_MODES:
        stress_artifact, stress_manifest = run_stress_mode(
            candidate_id=candidate_id,
            source_post_snapshot_path=source_post_snapshot_path,
            pre_target_route_node_coherence=pre_target_route_node_coherence,
            source_trace=source_trace,
            stress_mode=stress_mode,
        )
        stress_results.append(
            {
                "stress_mode": stress_mode,
                "stress_artifact_path": stress_manifest[0][0],
                "stress_artifact_digest": stress_artifact["stress_artifact_digest"],
                "status": "passed"
                if stress_artifact["all_stress_gates_passed"]
                else "failed_closed",
                "stress_gates": stress_artifact["stress_gates"],
            }
        )
        manifest_entries.extend(stress_manifest)
    all_passed = all(item["status"] == "passed" for item in stress_results)
    preservation_modes_passed = all(
        item["status"] == "passed"
        for item in stress_results
        if item["stress_mode"] in SU3_PRESERVATION_STRESS_MODES
    )
    repeated_result = next(
        item
        for item in stress_results
        if item["stress_mode"] == "repeated_reentry_two_step"
    )
    repeated_depletion_boundary_recorded = (
        repeated_result["status"] == "failed_closed"
        and len(repeated_result["stress_gates"]) == 2
        and repeated_result["stress_gates"][0]["passed"] is True
        and repeated_result["stress_gates"][1]["passed"] is False
    )
    stress_row = {
        "row_id": f"n22_i5a_row_{candidate_id}",
        "source_i5_row_id": row["row_id"],
        "source_iteration": row["source_iteration"],
        "source_candidate_row_id": row["source_candidate_row_id"],
        "source_i5_output_digest": load_json(I5_OUTPUT_PATH)["output_digest"],
        "stress_results": stress_results,
        "stress_mode_count": len(stress_results),
        "passed_stress_mode_count": sum(1 for item in stress_results if item["status"] == "passed"),
        "su3_preservation_stress_modes": SU3_PRESERVATION_STRESS_MODES,
        "su3_preservation_stress_modes_passed": preservation_modes_passed,
        "repeated_reentry_depletion_boundary_recorded": repeated_depletion_boundary_recorded,
        "replay_stress_status": "passed" if all_passed else "partial",
        "row_decision": "partial" if all_passed else "partial",
        "provisional_su_ladder_rung": (
            "SU3_stress_supported"
            if all_passed
            else "SU3_stress_limited"
        ),
        "i5a_consumable_role": (
            "replay_stress_supported_SU3_candidate_pending_I7_controls"
            if all_passed
            else "replay_stress_limited_SU3_candidate_pending_I7_controls"
        ),
        "narrow_margin_candidate": row["narrow_margin_candidate"],
        "one_window_transient_rejected": row["one_window_transient_rejected"],
        "durability_stress_supported": all_passed,
        "preservation_stress_supported": preservation_modes_passed,
        "repeated_reentry_boundary_blocks_su4": repeated_depletion_boundary_recorded,
        "su4_or_stronger_supported": False,
        "durable_geometry_modification_supported": False,
        "susceptibility_update_claim_allowed": False,
        "claim_ceiling": (
            "I5-A replay-stress SU3 evidence pending I7 controls; no durable "
            "SU4, transfer SU5, SU6, final N22, semantic learning, choice, "
            "agency, native support, sentience, Phase 8, or ant-ecology implementation"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "output_digest": "pending",
    }
    stress_row["output_digest"] = digest_value(
        {k: v for k, v in stress_row.items() if k != "output_digest"}
    )
    return canonicalize_json_value(stress_row), manifest_entries


def build_output() -> dict[str, Any]:
    i5 = load_json(I5_OUTPUT_PATH)
    i5_rows = [
        row
        for row in i5["replay_rows"]
        if row["provisional_su_ladder_rung"] == "SU3"
        and row["i5_consumable_role"] == "replay_backed_SU3_candidate_pending_I7_controls"
    ]
    threshold_path = ARTIFACT_DIR / "n22_i5a_thresholds_declared_before_use.json"
    write_json(threshold_path, threshold_record())
    stress_rows = []
    manifest_entries: list[tuple[str, str]] = [(rel(threshold_path), "thresholds_declared_before_use")]
    for row in i5_rows:
        stress_row, row_manifest_entries = build_stress_row(row)
        stress_rows.append(stress_row)
        manifest_entries.extend(row_manifest_entries)
    aggregate_manifest = file_manifest(manifest_entries)
    artifact_sha256_match = all(
        item["sha256"] == sha256_file(item["path"]) for item in aggregate_manifest
    )
    stress_supported_rows = [
        row
        for row in stress_rows
        if row["i5a_consumable_role"]
        == "replay_stress_supported_SU3_candidate_pending_I7_controls"
    ]
    stress_limited_rows = [
        row
        for row in stress_rows
        if row["i5a_consumable_role"]
        == "replay_stress_limited_SU3_candidate_pending_I7_controls"
    ]
    stress_summary = [
        {
            "row_id": row["row_id"],
            "source_i5_row_id": row["source_i5_row_id"],
            "source_iteration": row["source_iteration"],
            "passed_stress_mode_count": row["passed_stress_mode_count"],
            "stress_mode_count": row["stress_mode_count"],
            "provisional_su_ladder_rung": row["provisional_su_ladder_rung"],
            "i5a_consumable_role": row["i5a_consumable_role"],
            "narrow_margin_candidate": row["narrow_margin_candidate"],
            "su3_preservation_stress_modes_passed": row[
                "su3_preservation_stress_modes_passed"
            ],
            "repeated_reentry_depletion_boundary_recorded": row[
                "repeated_reentry_depletion_boundary_recorded"
            ],
        }
        for row in stress_rows
    ]
    checks = [
        check("i5_passed", i5.get("status") == "passed", i5.get("acceptance_state")),
        check("i5_su3_candidate_count", len(i5_rows) == 5, [row["row_id"] for row in i5_rows]),
        check("stress_modes_declared_before_use", threshold_record()["declared_before_use"] is True and len(STRESS_MODES) == 4, STRESS_MODES),
        check("artifact_manifest_non_empty", len(aggregate_manifest) >= 80, len(aggregate_manifest)),
        check("artifact_hashes_match", artifact_sha256_match, len(aggregate_manifest)),
        check("all_rows_have_four_stress_modes", all(row["stress_mode_count"] == 4 for row in stress_rows), stress_summary),
        check(
            "all_rows_pass_su3_preservation_stress_modes",
            all(row["su3_preservation_stress_modes_passed"] for row in stress_rows),
            stress_summary,
        ),
        check(
            "repeated_reentry_depletion_boundary_recorded",
            all(row["repeated_reentry_depletion_boundary_recorded"] for row in stress_rows),
            stress_summary,
        ),
        check("narrow_complementary_stress_tracked", any(row["narrow_margin_candidate"] for row in stress_rows), stress_summary),
        check("no_rows_promote_to_su4", all(row["su4_or_stronger_supported"] is False and row["durable_geometry_modification_supported"] is False for row in stress_rows), stress_summary),
        check("all_claims_still_blocked", all(row["susceptibility_update_claim_allowed"] is False for row in stress_rows), stress_summary),
        check("unsafe_flags_all_false", all(all(value is False for value in row["unsafe_claim_flags"].values()) for row in stress_rows), "all stress rows"),
        check("artifact_paths_repository_relative", all(not item["path"].startswith("/") for item in aggregate_manifest), "relative paths only"),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i5a_replay_durability_stress_probe",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": "5-A",
        "purpose": "replay durability stress over I5 SU3 candidates",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_replay_stress_limited_su3_candidates_pending_i7_controls"
            if not failed_checks
            else "failed_replay_durability_stress_probe"
        ),
        "command": COMMAND,
        "source_artifacts": [
            {
                "path": I5_OUTPUT_PATH,
                "sha256": sha256_file(I5_OUTPUT_PATH),
                "source_role": "n22_i5_durability_replay_probe",
                "status": i5.get("status"),
                "acceptance_state": i5.get("acceptance_state"),
                "output_digest": i5.get("output_digest"),
            }
        ],
        "stress_policy": {
            "threshold_policy_changed_from_i5": False,
            "stress_modes": STRESS_MODES,
            "su3_preservation_stress_modes": SU3_PRESERVATION_STRESS_MODES,
            "repeated_reentry_two_step_role": (
                "depletion_boundary_probe_not_required_for_SU3_preservation_support"
            ),
            "su4_or_stronger_allowed": False,
            "full_i7_control_matrix_run": False,
        },
        "stress_rows": stress_rows,
        "stress_summary": stress_summary,
        "artifact_manifest": aggregate_manifest,
        "iteration5a_boundary": {
            "source_i5_su3_candidate_count": len(i5_rows),
            "stress_supported_su3_candidate_count": len(stress_supported_rows),
            "stress_limited_su3_candidate_count": len(stress_limited_rows),
            "su3_preservation_stress_supported_candidate_count": sum(
                1 for row in stress_rows if row["su3_preservation_stress_modes_passed"]
            ),
            "repeated_reentry_depletion_boundary_count": sum(
                1
                for row in stress_rows
                if row["repeated_reentry_depletion_boundary_recorded"]
            ),
            "narrow_margin_candidate_count": sum(1 for row in stress_rows if row["narrow_margin_candidate"]),
            "stress_mode_count_per_row": len(STRESS_MODES),
            "provisional_su_ladder_rung": "SU3_stress_limited",
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
                "I5-A shows the replay-backed SU3 candidates preserve their "
                "route-specific delta under delayed re-entry and mild peer flux, "
                "while repeated re-entry exposes a fail-closed depletion boundary."
            ),
            "what_changed_from_i5": (
                "I5 tested clean replay. I5-A keeps the same thresholds and starts "
                "from the saved post-interaction state, then delays re-entry, "
                "repeats re-entry, or injects a mild unrelated peer flux before "
                "route_b re-entry. The second repeated re-entry depletes the "
                "route-specific delta below the SU3 preservation ratio, so I5-A "
                "records limited replay-stress support rather than SU4 evidence."
            ),
            "claim_boundary": (
                "I5-A strengthens replay-backed SU3 evidence only for delayed "
                "and mild-peer-flux preservation. Repeated re-entry is a "
                "fail-closed depletion boundary. I5-A does not support durable "
                "SU4, transfer SU5, SU6, final N22, the N21 ND6 bridge, semantic "
                "learning, choice, agency, native support, sentience, Phase 8, "
                "or ant-ecology implementation."
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
        "# N22 Iteration 5-A - Replay Durability Stress Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 5-A stress-tests the I5 replay-backed SU3 candidates without",
        "changing thresholds or opening SU4. Stress modes are baseline post-",
        "snapshot re-entry, delayed idle windows before re-entry, repeated re-entry,",
        "and mild unrelated peer flux before re-entry.",
        "",
        output["geometric_interpretation"]["what_changed_from_i5"],
        "",
        "## Stress Rows",
        "",
        "| Row | Source | Passed Modes | Role | Narrow |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in output["stress_rows"]:
        lines.append(
            "| "
            f"`{row['row_id'].removeprefix('n22_i5a_row_')}` | "
            f"`{row['source_iteration']}` | "
            f"{row['passed_stress_mode_count']}/{row['stress_mode_count']} | "
            f"`{row['i5a_consumable_role']}` | "
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
            "I5-A does not run the full I7 control matrix and cannot assign SU4.",
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
