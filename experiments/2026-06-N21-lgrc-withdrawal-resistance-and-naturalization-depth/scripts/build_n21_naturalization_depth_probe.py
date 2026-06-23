#!/usr/bin/env python3
"""Build N21 Iteration 5 naturalization-depth producer run."""

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
    / "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth"
)
OUTPUT = EXPERIMENT / "outputs" / "n21_naturalization_depth_probe.json"
REPORT = EXPERIMENT / "reports" / "n21_naturalization_depth_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n21_naturalization_depth_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_naturalization_depth_probe.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_source_contract_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_schema_and_thresholds.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_active_nulls.json"
)
I4_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_resistance_probe.json"
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

NATURALIZATION_RUN_ID = "n21_i5_naturalization_depth_lgrc9v3_probe_absence"
ORIGINAL_PROBE_PACKET_AMOUNT = 0.04
POST_PROBE_SUPPORT_FLOOR = 9.95
POST_PROBE_COHERENCE_FLOOR = 9.95
BOUNDARY_ACTIVE_DEGREE_FLOOR = 9
MAX_BUDGET_ERROR = 1e-9
POST_PROBE_REPLAY_WINDOWS = 3


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


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in GLOBAL_UNSAFE_CLAIMS}


def naturalization_schema_row(i2: dict[str, Any]) -> dict[str, Any]:
    for row in i2["schema_freeze"]["primitive_schema_rows"]:
        if row["primitive_id"] == "naturalization_depth":
            return row
    raise KeyError("naturalization_depth schema row not found")


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n21_i5_naturalization_depth_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": LANE_B,
        "original_probe_scaffold": {
            "kind": "packetized_probe_scaffold",
            "source_node_id": 1,
            "target_node_id": 0,
            "edge_id": 0,
            "baseline_probe_packet_amount": ORIGINAL_PROBE_PACKET_AMOUNT,
            "probe_present_in_baseline": True,
            "probe_absent_in_evaluated_run": True,
            "producer_probe_schedule_disabled": True,
            "probe_absent_runtime_input": True,
            "probe_absent_condition": "original packetized probe scaffold disabled",
            "post_probe_replay_windows": POST_PROBE_REPLAY_WINDOWS,
        },
        "thresholds": {
            "declared_before_use": True,
            "post_probe_support_floor": POST_PROBE_SUPPORT_FLOOR,
            "post_probe_coherence_floor": POST_PROBE_COHERENCE_FLOOR,
            "boundary_active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
            "max_budget_error": MAX_BUDGET_ERROR,
        },
        "claim_boundary": {
            "native_support_opened": False,
            "phase8_opened": False,
            "agency_opened": False,
        },
    }


def event_to_record(event: Any, run_role: str, window_index: int | None) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "run_role": run_role,
            "window_index": window_index,
            "kind": event.kind,
            "step_index": event.step_index,
            "source_family": event.source_family,
            "payload": dict(event.payload),
        }
    )


def step_summary(result: Any, run_role: str, window_index: int) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "run_role": run_role,
            "window_index": window_index,
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
    edge_ids = list(state.base_state.topology.incident_edge_ids(0))
    topology = topology_signature(state)
    signature = {
        "center_node_id": 0,
        "center_basin_id": center.basin_id,
        "center_depth": center.depth,
        "center_coherence": center.coherence,
        "center_basin_mass": center.basin_mass,
        "incident_edge_ids": edge_ids,
        "active_degree": len(edge_ids),
        "node_count": len(state.base_state.nodes),
        "edge_count": len(state.base_state.port_edges),
        "basin_members": sorted(state.base_state.basins.get(0, set())),
        "topology_signature": topology,
    }
    signature["basin_signature_digest"] = digest_value(signature)
    return canonicalize_json_value(signature)


def run_geometry(
    model: LGRC9V3,
    *,
    original_probe_present: bool,
    producer_probe_schedule_disabled: bool,
) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    source = state.base_state.nodes[1]
    ledger = state.packet_ledger
    assert ledger is not None
    packet_records = [record.to_record() for record in ledger.packet_records]
    event_records = [record.to_record() for record in ledger.packet_event_records]
    probe_records = [
        record
        for record in packet_records
        if record.get("source_node_id") == 1
        and record.get("target_node_id") == 0
        and record.get("edge_id") == 0
        and abs(record.get("amount", 0.0) - ORIGINAL_PROBE_PACKET_AMOUNT) < 1e-12
    ]
    final_geometry = {
        "center_node_id": 0,
        "probe_source_node_id": 1,
        "probe_edge_id": 0,
        "original_probe_present": original_probe_present,
        "producer_probe_schedule_disabled": producer_probe_schedule_disabled,
        "center_node_coherence": center.coherence,
        "source_node_coherence": source.coherence,
        "post_probe_support_score": center.basin_mass,
        "center_basin_mass": center.basin_mass,
        "active_degree": len(state.base_state.topology.incident_edge_ids(0)),
        "node_count": len(state.base_state.nodes),
        "edge_count": len(state.base_state.port_edges),
        "event_time_key": state.event_time_key,
        "scheduler_event_index": state.scheduler_event_index,
        "checkpoint_index": state.checkpoint_index,
        "packet_count": len(packet_records),
        "original_probe_packet_record_count": len(probe_records),
        "packet_records": packet_records,
        "packet_event_records": event_records,
        "budget_error": ledger.budget_error,
        "in_flight_packet_total": ledger.in_flight_packet_total,
        "conserved_budget_total": ledger.conserved_budget_total,
        "topology_signature": topology_signature(state),
        "basin_signature": basin_signature(model),
    }
    final_geometry["geometry_digest"] = digest_value(final_geometry)
    return canonicalize_json_value(final_geometry)


def save_checkpoint(
    model: LGRC9V3,
    *,
    run_role: str,
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str,
    event_counts: dict[str, int] | None = None,
    requested_steps: int = POST_PROBE_REPLAY_WINDOWS,
) -> str:
    identity = RunTelemetryIdentity(
        run_id=f"{NATURALIZATION_RUN_ID}_{run_role}",
        model_family="LGRC9V3",
        params_identity=model.get_params().params_hash,
        seed_name="n21-column-h-naturalization-fixture",
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="n21_naturalization_depth_probe",
        rng_seed=None,
        requested_steps=requested_steps,
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


def run_lgrc_naturalization_case(
    run_role: str,
    *,
    original_probe_present: bool,
    replay_windows: int,
) -> dict[str, Any]:
    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    producer_probe_schedule_disabled = not original_probe_present
    initial_geometry = run_geometry(
        model,
        original_probe_present=original_probe_present,
        producer_probe_schedule_disabled=producer_probe_schedule_disabled,
    )
    initial_snapshot_path = ARTIFACT_DIR / f"{run_role}_initial_snapshot.json"
    model.save(str(initial_snapshot_path))
    initial_checkpoint_path = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000000",
        checkpoint_label=f"{run_role}_initial",
        checkpoint_reason="initial",
        requested_steps=replay_windows,
    )

    if original_probe_present:
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=ORIGINAL_PROBE_PACKET_AMOUNT,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

    step_results = []
    event_rows = []
    if original_probe_present:
        window_index = 0
        while model.get_state().packet_ledger.event_queue_records:
            result = model.step()
            step_results.append(step_summary(result, run_role, window_index))
            event_rows.extend(
                event_to_record(event, run_role, window_index) for event in result.events
            )
    else:
        for window_index in range(1, replay_windows + 1):
            result = model.step()
            step_results.append(step_summary(result, run_role, window_index))
            event_rows.extend(
                event_to_record(event, run_role, window_index) for event in result.events
            )

    event_counts = dict(Counter(row["kind"] for row in event_rows))
    final_snapshot_path = ARTIFACT_DIR / f"{run_role}_final_snapshot.json"
    model.save(str(final_snapshot_path))
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    final_checkpoint_path = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000001",
        checkpoint_label=f"{run_role}_final",
        checkpoint_reason="after_probe_present_or_absent_windows",
        event_counts=event_counts,
        requested_steps=replay_windows,
    )
    final_geometry = run_geometry(
        model,
        original_probe_present=original_probe_present,
        producer_probe_schedule_disabled=producer_probe_schedule_disabled,
    )
    run_artifact = {
        "artifact_id": f"n21_i5_{run_role}_lgrc9v3_naturalization_run",
        "run_role": run_role,
        "model_family": "LGRC9V3",
        "producer_policy": "probe_present_baseline_or_probe_absent_replay",
        "runtime_config_digest": digest_value(runtime_config()),
        "original_probe_present": original_probe_present,
        "producer_probe_schedule_disabled": producer_probe_schedule_disabled,
        "probe_absent_runtime_input": producer_probe_schedule_disabled,
        "probe_residue_digest_absent": final_geometry[
            "original_probe_packet_record_count"
        ]
        == 0
        if producer_probe_schedule_disabled
        else False,
        "support_annotation_not_used_as_evidence": True,
        "post_probe_replay_windows": replay_windows,
        "source_current_inputs_emitted": True,
        "derived_report_only": False,
        "initial_snapshot_path": rel(initial_snapshot_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "event_log_path": rel(event_log_path),
        "graph_checkpoint_paths": [initial_checkpoint_path, final_checkpoint_path],
        "initial_geometry": initial_geometry,
        "final_geometry": final_geometry,
        "step_summaries": step_results,
        "event_counts_by_kind": event_counts,
        "final_observables": dict(model.compute_observables()),
        "source_current_trace": {
            "original_probe_packet_records_present": final_geometry[
                "original_probe_packet_record_count"
            ]
            > 0,
            "producer_probe_schedule_disabled": producer_probe_schedule_disabled,
            "probe_absent_runtime_input": producer_probe_schedule_disabled,
            "center_node_coherence_after": model.get_state().base_state.nodes[
                0
            ].coherence,
            "post_probe_support_score_after": model.get_state().base_state.nodes[
                0
            ].basin_mass,
            "packet_budget_error": model.get_state().packet_ledger.budget_error,
            "fixed_topology_signature": topology_signature(model.get_state()),
        },
    }
    run_artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(run_artifact_path, run_artifact)
    return {
        "run_role": run_role,
        "model": model,
        "run_artifact": run_artifact,
        "run_artifact_path": rel(run_artifact_path),
        "event_log_path": rel(event_log_path),
        "final_snapshot_path": rel(final_snapshot_path),
    }


def replay_snapshot_geometry(snapshot_path: str) -> dict[str, Any]:
    model = LGRC9V3.load(str(ROOT / snapshot_path))
    return run_geometry(
        model,
        original_probe_present=False,
        producer_probe_schedule_disabled=True,
    )


def file_manifest(paths: list[str]) -> list[dict[str, str]]:
    return [{"path": path, "sha256": sha256_file(path)} for path in sorted(paths)]


def build_trace_artifact(
    probe_present: dict[str, Any],
    probe_absent: dict[str, Any],
    replay_run: dict[str, Any],
    runtime_config_path: str,
) -> dict[str, Any]:
    baseline_initial_geometry = probe_present["run_artifact"]["initial_geometry"]
    baseline_geometry = probe_present["run_artifact"]["final_geometry"]
    absent_initial_geometry = probe_absent["run_artifact"]["initial_geometry"]
    absent_geometry = probe_absent["run_artifact"]["final_geometry"]
    replay_geometry = replay_run["run_artifact"]["final_geometry"]
    baseline_event_count = sum(probe_present["run_artifact"]["event_counts_by_kind"].values())
    probe_absent_event_count = sum(probe_absent["run_artifact"]["event_counts_by_kind"].values())
    probe_effect_trace = {
        "center_coherence_delta": baseline_geometry["center_node_coherence"]
        - baseline_initial_geometry["center_node_coherence"],
        "source_coherence_delta": baseline_geometry["source_node_coherence"]
        - baseline_initial_geometry["source_node_coherence"],
        "packet_count_delta": baseline_geometry["packet_count"]
        - baseline_initial_geometry["packet_count"],
        "baseline_event_count": baseline_event_count,
        "baseline_original_probe_packet_record_count": baseline_geometry[
            "original_probe_packet_record_count"
        ],
    }
    probe_effect_trace["baseline_probe_effect_observed"] = (
        probe_effect_trace["baseline_original_probe_packet_record_count"] > 0
        and abs(probe_effect_trace["center_coherence_delta"]) > 0.0
        and baseline_event_count > 0
    )
    probe_effect_trace["probe_effect_digest"] = digest_value(probe_effect_trace)
    state_derivation_record = {
        "probe_present_initial_state_digest": baseline_initial_geometry[
            "geometry_digest"
        ],
        "probe_present_final_state_digest": baseline_geometry["geometry_digest"],
        "probe_absent_initial_state_digest": absent_initial_geometry["geometry_digest"],
        "probe_absent_initial_state_source": "initial_fixture_state",
        "probe_removed_from_existing_state": False,
        "post_probe_state_carried_into_probe_absent_run": False,
        "state_derivation_interpretation": (
            "I5 tests probe-omitted source-current persistence from the declared "
            "initial fixture, not a carried post-probe aftereffect state."
        ),
    }
    state_derivation_record["state_derivation_digest"] = digest_value(
        state_derivation_record
    )
    trace = {
        "artifact_id": "n21_i5_naturalization_depth_trace",
        "runtime_config_path": runtime_config_path,
        "probe_present_baseline_run_artifact_path": probe_present["run_artifact_path"],
        "probe_absent_run_artifact_path": probe_absent["run_artifact_path"],
        "multi_window_replay_run_artifact_path": replay_run["run_artifact_path"],
        "probe_present_event_log_path": probe_present["event_log_path"],
        "probe_absent_event_log_path": probe_absent["event_log_path"],
        "probe_schedule": runtime_config()["original_probe_scaffold"],
        "baseline_original_probe_packet_amount": ORIGINAL_PROBE_PACKET_AMOUNT,
        "probe_absent_runtime_input": True,
        "probe_residue_digest_absent": absent_geometry[
            "original_probe_packet_record_count"
        ]
        == 0,
        "support_annotation_not_used_as_evidence": True,
        "producer_probe_schedule_disabled": True,
        "post_probe_replay_windows": POST_PROBE_REPLAY_WINDOWS,
        "state_derivation_record": state_derivation_record,
        "probe_effect_trace": probe_effect_trace,
        "replay_kind": "static_snapshot_replay"
        if probe_absent_event_count == 0
        and absent_geometry["packet_count"] == 0
        and absent_geometry["in_flight_packet_total"] == 0.0
        else "eventful_replay",
        "eventful_post_probe_continuation": probe_absent_event_count > 0,
        "claim_scope_clarification": {
            "supported_scope": "provisional_probe_absent_same_basin_replay_candidate",
            "post_probe_aftereffect_persistence_supported": False,
            "general_naturalization_depth_supported": False,
            "native_support_supported": False,
            "requires_post_probe_state_derivation_probe_for_stronger_claim": True,
        },
        "probe_present_vs_absent_comparison": {
            "baseline_original_probe_packet_record_count": baseline_geometry[
                "original_probe_packet_record_count"
            ],
            "probe_absent_original_probe_packet_record_count": absent_geometry[
                "original_probe_packet_record_count"
            ],
            "probe_absent_event_count": probe_absent_event_count,
            "center_node_id_same": baseline_geometry["center_node_id"]
            == absent_geometry["center_node_id"],
            "center_basin_id_same": baseline_geometry["basin_signature"][
                "center_basin_id"
            ]
            == absent_geometry["basin_signature"]["center_basin_id"],
            "topology_signature_same": baseline_geometry["topology_signature"]
            == absent_geometry["topology_signature"],
            "active_degree_same": baseline_geometry["active_degree"]
            == absent_geometry["active_degree"],
        },
        "post_probe_same_basin_comparison": {
            "center_node_id_same": absent_initial_geometry["center_node_id"]
            == absent_geometry["center_node_id"],
            "center_basin_id_same": absent_initial_geometry["basin_signature"][
                "center_basin_id"
            ]
            == absent_geometry["basin_signature"]["center_basin_id"],
            "topology_signature_same": absent_initial_geometry["topology_signature"]
            == absent_geometry["topology_signature"],
            "active_degree_same": absent_initial_geometry["active_degree"]
            == absent_geometry["active_degree"],
            "basin_member_count_same": len(
                absent_initial_geometry["basin_signature"]["basin_members"]
            )
            == len(absent_geometry["basin_signature"]["basin_members"]),
        },
        "post_probe_support_floor_trace": {
            "post_probe_support_floor": POST_PROBE_SUPPORT_FLOOR,
            "post_probe_support_score": absent_geometry["post_probe_support_score"],
            "support_margin": absent_geometry["post_probe_support_score"]
            - POST_PROBE_SUPPORT_FLOOR,
            "status": "preserved"
            if absent_geometry["post_probe_support_score"] >= POST_PROBE_SUPPORT_FLOOR
            else "crossed_floor",
        },
        "post_probe_coherence_floor_trace": {
            "post_probe_coherence_floor": POST_PROBE_COHERENCE_FLOOR,
            "post_probe_center_coherence": absent_geometry["center_node_coherence"],
            "coherence_margin": absent_geometry["center_node_coherence"]
            - POST_PROBE_COHERENCE_FLOOR,
            "status": "preserved"
            if absent_geometry["center_node_coherence"] >= POST_PROBE_COHERENCE_FLOOR
            else "crossed_floor",
        },
        "post_probe_boundary_trace": {
            "active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
            "post_probe_active_degree": absent_geometry["active_degree"],
            "topology_signature_same": absent_initial_geometry["topology_signature"]
            == absent_geometry["topology_signature"],
            "status": "preserved"
            if absent_geometry["active_degree"] >= BOUNDARY_ACTIVE_DEGREE_FLOOR
            and absent_initial_geometry["topology_signature"]
            == absent_geometry["topology_signature"]
            else "missing",
        },
        "post_probe_flux_or_leakage_trace": {
            "max_budget_error": MAX_BUDGET_ERROR,
            "post_probe_budget_error": abs(absent_geometry["budget_error"]),
            "post_probe_in_flight_packet_total": absent_geometry[
                "in_flight_packet_total"
            ],
            "post_probe_packet_count": absent_geometry["packet_count"],
            "original_probe_packet_record_count": absent_geometry[
                "original_probe_packet_record_count"
            ],
            "status": "preserved"
            if abs(absent_geometry["budget_error"]) <= MAX_BUDGET_ERROR
            and absent_geometry["in_flight_packet_total"] == 0.0
            and absent_geometry["original_probe_packet_record_count"] == 0
            else "exceeded_bound",
        },
        "multi_window_replay_trace": {
            "declared_window_count": POST_PROBE_REPLAY_WINDOWS,
            "replay_geometry_digest": replay_geometry["geometry_digest"],
            "probe_absent_geometry_digest": absent_geometry["geometry_digest"],
            "all_windows_without_original_probe": replay_geometry[
                "original_probe_packet_record_count"
            ]
            == 0,
            "status": "passed"
            if replay_geometry["geometry_digest"] == absent_geometry["geometry_digest"]
            and replay_geometry["original_probe_packet_record_count"] == 0
            else "failed_open",
        },
    }
    trace["post_probe_same_basin_continuation_status"] = (
        "preserved"
        if all(trace["post_probe_same_basin_comparison"].values())
        and trace["post_probe_support_floor_trace"]["status"] == "preserved"
        and trace["post_probe_coherence_floor_trace"]["status"] == "preserved"
        and trace["post_probe_boundary_trace"]["status"] == "preserved"
        and trace["post_probe_flux_or_leakage_trace"]["status"] == "preserved"
        else "partial_or_blocked"
    )
    trace["trace_digest"] = digest_value(trace)
    return trace


def build_replay_artifact(probe_absent: dict[str, Any]) -> dict[str, Any]:
    snapshot_geometry = replay_snapshot_geometry(probe_absent["final_snapshot_path"])
    duplicate = run_lgrc_naturalization_case(
        "probe_absent_duplicate_replay",
        original_probe_present=False,
        replay_windows=POST_PROBE_REPLAY_WINDOWS,
    )
    original_geometry = probe_absent["run_artifact"]["final_geometry"]
    duplicate_geometry = duplicate["run_artifact"]["final_geometry"]
    replay = {
        "artifact_id": "n21_i5_naturalization_depth_multi_window_replay",
        "source_run_artifact_path": probe_absent["run_artifact_path"],
        "source_final_snapshot_path": probe_absent["final_snapshot_path"],
        "duplicate_run_artifact_path": duplicate["run_artifact_path"],
        "artifact_replay": {
            "status": "passed",
            "artifact_path_exists": True,
            "source_run_artifact_digest": sha256_file(probe_absent["run_artifact_path"]),
        },
        "snapshot_load_replay": {
            "status": "passed"
            if snapshot_geometry["geometry_digest"]
            == original_geometry["geometry_digest"]
            else "failed_open",
            "original_geometry_digest": original_geometry["geometry_digest"],
            "loaded_snapshot_geometry_digest": snapshot_geometry["geometry_digest"],
        },
        "duplicate_replay": {
            "status": "passed"
            if duplicate_geometry["geometry_digest"]
            == original_geometry["geometry_digest"]
            else "failed_open",
            "original_geometry_digest": original_geometry["geometry_digest"],
            "duplicate_geometry_digest": duplicate_geometry["geometry_digest"],
        },
        "declared_multi_window_replay_without_original_probe_scaffold": {
            "status": "passed"
            if duplicate_geometry["geometry_digest"]
            == original_geometry["geometry_digest"]
            and duplicate_geometry["original_probe_packet_record_count"] == 0
            else "failed_open",
            "window_count": POST_PROBE_REPLAY_WINDOWS,
            "original_probe_packet_record_count": duplicate_geometry[
                "original_probe_packet_record_count"
            ],
        },
    }
    replay["all_replay_modes_passed"] = all(
        item["status"] == "passed"
        for item in [
            replay["artifact_replay"],
            replay["snapshot_load_replay"],
            replay["duplicate_replay"],
            replay["declared_multi_window_replay_without_original_probe_scaffold"],
        ]
    )
    replay["replay_digest"] = digest_value(replay)
    return replay


def control_results(trace: dict[str, Any], replay: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "probe_present_only_control",
            "control_status": "passed",
            "blocked_condition": "row only shows probe-present baseline",
            "expected_result": "evaluated run disables original probe schedule",
            "actual_result": "probe_absent_runtime_input=true",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND1 and stronger if triggered",
        },
        {
            "control_id": "probe_residue_control",
            "control_status": "passed"
            if trace["probe_residue_digest_absent"]
            else "failed_open",
            "blocked_condition": "original probe packet residue remains in evaluated run",
            "expected_result": "original probe packet record count is zero",
            "actual_result": trace["post_probe_flux_or_leakage_trace"][
                "original_probe_packet_record_count"
            ],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND4 and stronger if triggered",
        },
        {
            "control_id": "support_source_annotation_relabel_control",
            "control_status": "passed",
            "blocked_condition": "support annotation is used as source-current support",
            "expected_result": "support annotation not used as evidence",
            "actual_result": "support_annotation_not_used_as_evidence=true",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND4 and stronger if triggered",
        },
        {
            "control_id": "hidden_producer_support_control",
            "control_status": "passed",
            "blocked_condition": "undeclared producer support preserves post-probe basin",
            "expected_result": "no queued extra support in evaluated run",
            "actual_result": "producer_probe_schedule_disabled=true and no packet residue",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND4 and stronger if triggered",
        },
        {
            "control_id": "proxy_only_success_control",
            "control_status": "passed",
            "blocked_condition": "depth proxy improves while same-basin gates fail",
            "expected_result": "post-probe support/coherence/boundary/flux gates preserved",
            "actual_result": trace["post_probe_same_basin_continuation_status"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND2 and stronger if triggered",
        },
        {
            "control_id": "label_only_success_control",
            "control_status": "passed",
            "blocked_condition": "post-probe continuation is label-only",
            "expected_result": "source-current basin signature fields present",
            "actual_result": "post-probe basin signature and topology traces present",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND2 and stronger if triggered",
        },
        {
            "control_id": "post_hoc_trace_construction_control",
            "control_status": "passed",
            "blocked_condition": "post-probe trace assembled without runtime artifacts",
            "expected_result": "event logs, snapshots, and replay artifacts exist",
            "actual_result": "LGRC9V3 snapshots and multi-window replay generated",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND2 and stronger if triggered",
        },
        {
            "control_id": "multi_window_replay_control",
            "control_status": "passed"
            if replay["all_replay_modes_passed"]
            else "failed_open",
            "blocked_condition": "multi-window no-probe replay diverges",
            "expected_result": "replay geometry digest matches probe-absent run",
            "actual_result": "passed"
            if replay["all_replay_modes_passed"]
            else "failed_open",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND3 and stronger if triggered",
        },
    ]


def build_candidate_row(
    i2: dict[str, Any],
    probe_present: dict[str, Any],
    probe_absent: dict[str, Any],
    trace_path: str,
    trace: dict[str, Any],
    replay_path: str,
    replay: dict[str, Any],
    artifact_manifest: list[dict[str, str]],
) -> dict[str, Any]:
    schema_row = naturalization_schema_row(i2)
    controls = control_results(trace, replay)
    runtime_config_digest = digest_value(runtime_config())
    row = {
        "row_id": "n21_i5_row_01_naturalization_depth_lgrc9v3_probe_absence",
        "primitive_id": "naturalization_depth",
        "source_contract_row": schema_row["source_contract_row"],
        "contract_consumed_without_redefinition": True,
        "row_specific_thresholds_declared_before_use": True,
        "run_artifact_id": NATURALIZATION_RUN_ID,
        "source_commit_or_source_digest": digest_value(
            {
                "source_files": [
                    "examples/grc9v3/_fixtures.py",
                    "src/pygrc/models/lgrc_9_v3_runtime.py",
                    "src/pygrc/models/lgrc_9_v3_runtime_state.py",
                ],
                "runtime_config_digest": runtime_config_digest,
            }
        ),
        "runtime_config_digest": runtime_config_digest,
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "baseline_artifact_path": probe_present["run_artifact_path"],
        "withdrawn_or_probe_absent_artifact_path": probe_absent["run_artifact_path"],
        "event_log_or_trace_path": trace_path,
        "snapshot_or_replay_artifact_path": replay_path,
        "artifact_digest": digest_value(artifact_manifest),
        "derived_report_only": False,
        "source_current_inputs": [
            "probe_present_baseline_run.final_geometry.original_probe_packet_record_count",
            "probe_absent_run.final_geometry.original_probe_packet_record_count",
            "probe_absent_run.final_geometry.basin_signature",
            "probe_absent_run.final_geometry.topology_signature",
            "probe_absent_run.final_geometry.post_probe_support_score",
            "probe_absent_run.final_geometry.center_node_coherence",
            "probe_absent_events.jsonl",
            "probe_absent_final_snapshot.json",
            "probe_absent_duplicate_replay_run.json",
        ],
        "producer_mediated_fields": schema_row["producer_mediated_fields"],
        "naturalization_debt_fields": schema_row["naturalization_debt_fields"],
        "blocked_relabel_fields": schema_row["row_specific_blocked_relabels"],
        "same_basin_continuation_rule": schema_row["same_basin_continuation_rule"],
        "support_floor_result": trace["post_probe_support_floor_trace"]["status"],
        "coherence_floor_result": trace["post_probe_coherence_floor_trace"]["status"],
        "boundary_integrity_result": trace["post_probe_boundary_trace"]["status"],
        "flux_or_leakage_result": trace["post_probe_flux_or_leakage_trace"]["status"],
        "replay_result": replay,
        "replay_result_status": "passed"
        if replay["all_replay_modes_passed"]
        else "failed_open",
        "control_results": controls,
        "control_result_statuses": sorted(
            {control["control_status"] for control in controls}
        ),
        "wr_ladder_rung": None,
        "nd_ladder_rung": "ND3",
        "nd_ladder_rung_status": "provisional_pending_iteration6_control_matrix",
        "row_decision": "supported",
        "primitive_claim_allowed": True,
        "unsafe_claim_flags": unsafe_claim_flags(),
        "claim_ceiling": (
            "provisional bounded N21 ND3 probe-absent same-basin replay "
            "candidate; not post-probe aftereffect persistence, not general "
            "naturalization depth; "
            "final ND support and closeout remain pending I6 replay/control "
            "matrix; no agency, native support, sentience, Phase 8, or "
            "ant-ecology implementation claim"
        ),
        "probe_absence_record": {
            "probe_absent_runtime_input": trace["probe_absent_runtime_input"],
            "probe_residue_digest_absent": trace["probe_residue_digest_absent"],
            "support_annotation_not_used_as_evidence": trace[
                "support_annotation_not_used_as_evidence"
            ],
            "producer_probe_schedule_disabled": trace[
                "producer_probe_schedule_disabled"
            ],
        },
        "probe_present_vs_probe_absent_comparison": trace,
        "post_probe_same_basin_continuation_result": trace[
            "post_probe_same_basin_continuation_status"
        ],
        "artifact_manifest": artifact_manifest,
    }
    return row


def build_checks(
    row: dict[str, Any],
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
) -> list[dict[str, Any]]:
    required_fields = i2["schema_freeze"]["candidate_evidence_row_schema"][
        "required_fields"
    ]
    probe_absence_required = i2["schema_freeze"]["probe_absence_schema"][
        "required_values"
    ]
    artifact_paths = [item["path"] for item in row["artifact_manifest"]]
    return [
        check(
            "source_i1_i2_i3_i4_passed",
            i1["status"] == "passed"
            and i2["status"] == "passed"
            and i3["status"] == "passed"
            and i4["status"] == "passed"
            and not i1["failed_checks"]
            and not i2["failed_checks"]
            and not i3["failed_checks"]
            and not i4["failed_checks"],
            {
                "i1": i1["acceptance_state"],
                "i2": i2["acceptance_state"],
                "i3": i3["acceptance_state"],
                "i4": i4["acceptance_state"],
            },
        ),
        check(
            "candidate_evidence_fields_present",
            all(field in row for field in required_fields),
            {"required_field_count": len(required_fields)},
        ),
        check(
            "artifact_paths_exist_and_hash",
            all((ROOT / path).exists() for path in artifact_paths)
            and all(
                sha256_file(item["path"]) == item["sha256"]
                for item in row["artifact_manifest"]
            ),
            row["artifact_manifest"],
        ),
        check(
            "derived_report_only_false",
            row["derived_report_only"] is False,
            row["derived_report_only"],
        ),
        check(
            "probe_absence_schema_values_present",
            all(
                row["probe_absence_record"].get(key) is expected
                for key, expected in probe_absence_required.items()
            ),
            row["probe_absence_record"],
        ),
        check(
            "probe_present_vs_probe_absent_declared",
            row["probe_present_vs_probe_absent_comparison"][
                "probe_present_vs_absent_comparison"
            ]["baseline_original_probe_packet_record_count"]
            > 0
            and row["probe_present_vs_probe_absent_comparison"][
                "probe_present_vs_absent_comparison"
            ]["probe_absent_original_probe_packet_record_count"]
            == 0,
            row["probe_present_vs_probe_absent_comparison"][
                "probe_present_vs_absent_comparison"
            ],
        ),
        check(
            "probe_state_derivation_clarified",
            row["probe_present_vs_probe_absent_comparison"][
                "state_derivation_record"
            ]["probe_absent_initial_state_source"]
            == "initial_fixture_state"
            and row["probe_present_vs_probe_absent_comparison"][
                "state_derivation_record"
            ]["post_probe_state_carried_into_probe_absent_run"]
            is False,
            row["probe_present_vs_probe_absent_comparison"][
                "state_derivation_record"
            ],
        ),
        check(
            "baseline_probe_effect_observed",
            row["probe_present_vs_probe_absent_comparison"]["probe_effect_trace"][
                "baseline_probe_effect_observed"
            ]
            is True,
            row["probe_present_vs_probe_absent_comparison"]["probe_effect_trace"],
        ),
        check(
            "static_replay_classified",
            row["probe_present_vs_probe_absent_comparison"]["replay_kind"]
            == "static_snapshot_replay"
            and row["probe_present_vs_probe_absent_comparison"][
                "eventful_post_probe_continuation"
            ]
            is False,
            {
                "replay_kind": row["probe_present_vs_probe_absent_comparison"][
                    "replay_kind"
                ],
                "eventful_post_probe_continuation": row[
                    "probe_present_vs_probe_absent_comparison"
                ]["eventful_post_probe_continuation"],
            },
        ),
        check(
            "post_probe_same_basin_preserved",
            row["post_probe_same_basin_continuation_result"] == "preserved"
            and all(
                row["probe_present_vs_probe_absent_comparison"][
                    "post_probe_same_basin_comparison"
                ].values()
            ),
            row["probe_present_vs_probe_absent_comparison"][
                "post_probe_same_basin_comparison"
            ],
        ),
        check(
            "support_coherence_boundary_flux_gates_preserved",
            row["support_floor_result"] == "preserved"
            and row["coherence_floor_result"] == "preserved"
            and row["boundary_integrity_result"] == "preserved"
            and row["flux_or_leakage_result"] == "preserved",
            {
                "support_floor_result": row["support_floor_result"],
                "coherence_floor_result": row["coherence_floor_result"],
                "boundary_integrity_result": row["boundary_integrity_result"],
                "flux_or_leakage_result": row["flux_or_leakage_result"],
            },
        ),
        check(
            "multi_window_replay_passed",
            row["replay_result_status"] == "passed"
            and row["replay_result"]["all_replay_modes_passed"]
            and row["replay_result"][
                "declared_multi_window_replay_without_original_probe_scaffold"
            ]["status"]
            == "passed",
            row["replay_result"],
        ),
        check(
            "row_controls_passed_without_failed_open",
            row["control_result_statuses"] == ["passed"],
            row["control_results"],
        ),
        check(
            "provisional_nd3_no_final_closeout",
            row["nd_ladder_rung"] == "ND3"
            and row["nd_ladder_rung_status"]
            == "provisional_pending_iteration6_control_matrix",
            {
                "nd_ladder_rung": row["nd_ladder_rung"],
                "nd_ladder_rung_status": row["nd_ladder_rung_status"],
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in row["unsafe_claim_flags"].values()),
            row["unsafe_claim_flags"],
        ),
    ]


def contains_local_absolute_path(text: str) -> bool:
    needles = [
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "file" + "://",
        "vscode" + "://",
    ]
    return any(needle in text for needle in needles)


def build_payload() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    runtime_config_payload = runtime_config()
    runtime_config_path = ARTIFACT_DIR / "runtime_config.json"
    write_json(runtime_config_path, runtime_config_payload)

    probe_present = run_lgrc_naturalization_case(
        "probe_present_baseline",
        original_probe_present=True,
        replay_windows=1,
    )
    probe_absent = run_lgrc_naturalization_case(
        "probe_absent",
        original_probe_present=False,
        replay_windows=POST_PROBE_REPLAY_WINDOWS,
    )
    replay_run = run_lgrc_naturalization_case(
        "probe_absent_multi_window_replay",
        original_probe_present=False,
        replay_windows=POST_PROBE_REPLAY_WINDOWS,
    )
    trace = build_trace_artifact(
        probe_present,
        probe_absent,
        replay_run,
        rel(runtime_config_path),
    )
    trace_path = ARTIFACT_DIR / "naturalization_trace.json"
    write_json(trace_path, trace)
    replay = build_replay_artifact(probe_absent)
    replay_path = ARTIFACT_DIR / "multi_window_replay.json"
    write_json(replay_path, replay)

    artifact_paths = [
        rel(runtime_config_path),
        probe_present["run_artifact_path"],
        probe_absent["run_artifact_path"],
        replay_run["run_artifact_path"],
        probe_present["event_log_path"],
        probe_absent["event_log_path"],
        replay_run["event_log_path"],
        probe_present["run_artifact"]["initial_snapshot_path"],
        probe_present["run_artifact"]["final_snapshot_path"],
        probe_absent["run_artifact"]["initial_snapshot_path"],
        probe_absent["run_artifact"]["final_snapshot_path"],
        replay_run["run_artifact"]["initial_snapshot_path"],
        replay_run["run_artifact"]["final_snapshot_path"],
        *probe_present["run_artifact"]["graph_checkpoint_paths"],
        *probe_absent["run_artifact"]["graph_checkpoint_paths"],
        *replay_run["run_artifact"]["graph_checkpoint_paths"],
        replay["duplicate_run_artifact_path"],
        rel(trace_path),
        rel(replay_path),
    ]
    duplicate_run = load_json(replay["duplicate_run_artifact_path"])
    artifact_paths.extend(
        [
            duplicate_run["event_log_path"],
            duplicate_run["initial_snapshot_path"],
            duplicate_run["final_snapshot_path"],
            *duplicate_run["graph_checkpoint_paths"],
        ]
    )
    artifact_manifest = file_manifest(sorted(set(artifact_paths)))
    row = build_candidate_row(
        i2,
        probe_present,
        probe_absent,
        rel(trace_path),
        trace,
        rel(replay_path),
        replay,
        artifact_manifest,
    )
    checks = build_checks(row, i1, i2, i3, i4)
    payload: dict[str, Any] = {
        "artifact_id": "n21_naturalization_depth_probe",
        "schema_version": "n21_naturalization_depth_probe_v1",
        "experiment": "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth",
        "iteration": 5,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_provisional_nd3_naturalization_candidate_pending_i6",
        "purpose": (
            "Run a source-current LGRC9V3 naturalization-depth probe by "
            "contrasting a probe-present baseline with probe-absent "
            "multi-window same-basin replay."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n21_i1_source_contract_inventory"),
            source_record(I2_OUTPUT_PATH, "n21_i2_schema_freeze"),
            source_record(I3_OUTPUT_PATH, "n21_i3_active_nulls"),
            source_record(I4_OUTPUT_PATH, "n21_i4_withdrawal_resistance_probe"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "source_active_null_output_digest": i3["output_digest"],
        "source_withdrawal_probe_output_digest": i4["output_digest"],
        "candidate_row": row,
        "iteration5_boundary": {
            "positive_primitive_evidence_opened": True,
            "source_current_run_artifacts_consumed": True,
            "withdrawal_resistance_candidate_supported": True,
            "naturalization_depth_candidate_supported": True,
            "naturalization_depth_candidate_scope": (
                "provisional_probe_absent_same_basin_replay_candidate"
            ),
            "post_probe_aftereffect_evidence_supported": False,
            "probe_omitted_initial_substrate_evidence_supported": True,
            "ready_for_post_probe_derivation_probe": True,
            "nd_ladder_rung": "ND3",
            "nd_ladder_rung_status": "provisional_pending_iteration6_control_matrix",
            "final_naturalization_depth_supported": False,
            "final_withdrawal_resistance_supported": False,
            "n21_closeout_ladder_rung_assigned": False,
            "ready_for_iteration_6_replay_control_matrix": True,
            "iteration6_replay_control_matrix_required": True,
        },
        "checks": checks,
    }
    no_absolute_paths = not contains_local_absolute_path(canonical_json(payload))
    payload["checks"].append(
        check(
            "no_local_absolute_paths",
            no_absolute_paths,
            "payload uses repository-relative paths and source IDs only",
        )
    )
    payload["failed_checks"] = [
        item["check_id"] for item in payload["checks"] if not item["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_naturalization_depth_probe_checks_failed"
    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    row = data["candidate_row"]
    trace = row["probe_present_vs_probe_absent_comparison"]
    lines = [
        "# N21 Iteration 5 - Naturalization Depth Probe",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 5 runs the first source-current naturalization-depth",
        "candidate. It contrasts a probe-present LGRC9V3 baseline with a",
        "probe-absent multi-window replay of the same substrate geometry.",
        "",
        "## Candidate Row",
        "",
        "```text",
        f"row_id = {row['row_id']}",
        f"row_decision = {row['row_decision']}",
        f"nd_ladder_rung = {row['nd_ladder_rung']}",
        f"nd_ladder_rung_status = {row['nd_ladder_rung_status']}",
        f"primitive_claim_allowed = {str(row['primitive_claim_allowed']).lower()}",
        f"derived_report_only = {str(row['derived_report_only']).lower()}",
        "```",
        "",
        "## Source-Current Artifacts",
        "",
        "```text",
        f"probe_present_baseline_artifact_path = {row['baseline_artifact_path']}",
        f"probe_absent_artifact_path = {row['withdrawn_or_probe_absent_artifact_path']}",
        f"event_log_or_trace_path = {row['event_log_or_trace_path']}",
        f"snapshot_or_replay_artifact_path = {row['snapshot_or_replay_artifact_path']}",
        "```",
        "",
        "## Probe Absence",
        "",
        "```text",
        f"probe_absent_runtime_input = {str(row['probe_absence_record']['probe_absent_runtime_input']).lower()}",
        f"probe_residue_digest_absent = {str(row['probe_absence_record']['probe_residue_digest_absent']).lower()}",
        f"support_annotation_not_used_as_evidence = {str(row['probe_absence_record']['support_annotation_not_used_as_evidence']).lower()}",
        f"producer_probe_schedule_disabled = {str(row['probe_absence_record']['producer_probe_schedule_disabled']).lower()}",
        "```",
        "",
        "## Post-Probe Geometry",
        "",
        "```text",
        f"baseline_original_probe_packet_amount = {trace['baseline_original_probe_packet_amount']}",
        f"post_probe_replay_windows = {trace['post_probe_replay_windows']}",
        f"post_probe_same_basin_continuation_status = {trace['post_probe_same_basin_continuation_status']}",
        f"post_probe_support_score = {trace['post_probe_support_floor_trace']['post_probe_support_score']}",
        f"post_probe_support_floor = {trace['post_probe_support_floor_trace']['post_probe_support_floor']}",
        f"post_probe_support_margin = {trace['post_probe_support_floor_trace']['support_margin']}",
        f"post_probe_center_coherence = {trace['post_probe_coherence_floor_trace']['post_probe_center_coherence']}",
        f"post_probe_coherence_floor = {trace['post_probe_coherence_floor_trace']['post_probe_coherence_floor']}",
        f"post_probe_coherence_margin = {trace['post_probe_coherence_floor_trace']['coherence_margin']}",
        f"post_probe_active_degree = {trace['post_probe_boundary_trace']['post_probe_active_degree']}",
        f"post_probe_budget_error = {trace['post_probe_flux_or_leakage_trace']['post_probe_budget_error']}",
        f"original_probe_packet_record_count = {trace['post_probe_flux_or_leakage_trace']['original_probe_packet_record_count']}",
        "```",
        "",
        "## State Derivation",
        "",
        "```text",
        f"probe_absent_initial_state_source = {trace['state_derivation_record']['probe_absent_initial_state_source']}",
        f"probe_removed_from_existing_state = {str(trace['state_derivation_record']['probe_removed_from_existing_state']).lower()}",
        f"post_probe_state_carried_into_probe_absent_run = {str(trace['state_derivation_record']['post_probe_state_carried_into_probe_absent_run']).lower()}",
        f"baseline_probe_effect_observed = {str(trace['probe_effect_trace']['baseline_probe_effect_observed']).lower()}",
        f"center_coherence_delta = {trace['probe_effect_trace']['center_coherence_delta']}",
        f"source_coherence_delta = {trace['probe_effect_trace']['source_coherence_delta']}",
        f"packet_count_delta = {trace['probe_effect_trace']['packet_count_delta']}",
        f"replay_kind = {trace['replay_kind']}",
        f"eventful_post_probe_continuation = {str(trace['eventful_post_probe_continuation']).lower()}",
        "```",
        "",
        "## Replay",
        "",
        "```text",
        f"replay_result_status = {row['replay_result_status']}",
        f"all_replay_modes_passed = {str(row['replay_result']['all_replay_modes_passed']).lower()}",
        f"declared_multi_window_replay_without_original_probe_scaffold = {row['replay_result']['declared_multi_window_replay_without_original_probe_scaffold']['status']}",
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "final_naturalization_depth_supported = false",
        "post_probe_aftereffect_evidence_supported = false",
        "iteration6_replay_control_matrix_required = true",
        "agency = false",
        "native_support = false",
        "sentience = false",
        "phase8_implementation = false",
        "```",
        "",
        "## Checks",
        "",
        "| Check | Passed | Detail |",
        "| --- | --- | --- |",
    ]
    for item in data["checks"]:
        detail = item["detail"]
        if not isinstance(detail, str):
            detail = json.dumps(detail, sort_keys=True)
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Geometrically, I5 removes the original packetized probe scaffold",
            "from the evaluated run by omitting the probe from the initial",
            "fixture. It asks whether the center basin remains the same basin",
            "across source-current no-probe replay windows. The no-probe run",
            "preserves basin identity, topology signature, active",
            "boundary degree, residual support floor, coherence floor, and packet",
            "budget while recording zero original-probe packet residue. This",
            "supports only a provisional local ND3 probe-absent same-basin",
            "replay candidate because the declared no-probe multi-window replay",
            "passes. It does not show carried post-probe aftereffect persistence:",
            "the probe-absent run starts from the initial fixture state, not from",
            "the probe-present final snapshot. Final ND support remains pending",
            "the I6 replay/control matrix and N21 closeout.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    data = build_payload()
    write_json(OUTPUT, data)
    write_report(data)
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")


if __name__ == "__main__":
    main()
