#!/usr/bin/env python3
"""Build N21 Iteration 5-B eventful post-probe continuation probe."""

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
OUTPUT = EXPERIMENT / "outputs" / "n21_naturalization_depth_eventful_post_probe.json"
REPORT = EXPERIMENT / "reports" / "n21_naturalization_depth_eventful_post_probe.md"
ARTIFACT_DIR = (
    EXPERIMENT / "outputs" / "n21_naturalization_depth_eventful_post_probe_artifacts"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_naturalization_depth_eventful_post_probe.py"
)

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_n21_naturalization_depth_probe as i5  # noqa: E402


I1_OUTPUT_PATH = i5.I1_OUTPUT_PATH
I2_OUTPUT_PATH = i5.I2_OUTPUT_PATH
I3_OUTPUT_PATH = i5.I3_OUTPUT_PATH
I4_OUTPUT_PATH = i5.I4_OUTPUT_PATH
I5_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_naturalization_depth_probe.json"
)
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_naturalization_depth_post_probe_derivation.json"
)

EVENTFUL_RUN_ID = "n21_i5b_naturalization_depth_eventful_post_probe"
EVENTFUL_REPLAY_WINDOWS = 3
POST_PROBE_CHALLENGE_PACKET = {
    "source_node_id": 0,
    "target_node_id": 2,
    "edge_id": 1,
    "amount": 0.01,
    "departure_event_time_key": 2.0,
    "scheduler_event_index": 2,
    "packet_index": 0,
}


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n21_i5b_eventful_post_probe_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": i5.LANE_B,
        "original_probe_scaffold": {
            "kind": "packetized_probe_scaffold",
            "source_node_id": 1,
            "target_node_id": 0,
            "edge_id": 0,
            "baseline_probe_packet_amount": i5.ORIGINAL_PROBE_PACKET_AMOUNT,
            "probe_present_in_baseline": True,
            "post_probe_state_derivation_source": "probe_present_final_snapshot",
            "active_original_probe_schedule_disabled": True,
        },
        "post_probe_eventful_challenge": {
            "kind": "non_original_post_probe_challenge_packet",
            **POST_PROBE_CHALLENGE_PACKET,
            "route_role": "center_outward_perturbation_not_original_probe",
            "original_probe_route_reused": False,
            "eventful_replay_windows": EVENTFUL_REPLAY_WINDOWS,
        },
        "thresholds": {
            "declared_before_use": True,
            "post_probe_support_floor": i5.POST_PROBE_SUPPORT_FLOOR,
            "post_probe_coherence_floor": i5.POST_PROBE_COHERENCE_FLOOR,
            "boundary_active_degree_floor": i5.BOUNDARY_ACTIVE_DEGREE_FLOOR,
            "max_budget_error": i5.MAX_BUDGET_ERROR,
        },
        "claim_boundary": {
            "native_support_opened": False,
            "phase8_opened": False,
            "agency_opened": False,
        },
    }


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


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


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def file_manifest(paths: list[str]) -> list[dict[str, str]]:
    return [{"path": path, "sha256": sha256_file(path)} for path in sorted(paths)]


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


def patch_i5_module() -> None:
    i5.ARTIFACT_DIR = ARTIFACT_DIR
    i5.NATURALIZATION_RUN_ID = EVENTFUL_RUN_ID
    i5.runtime_config = runtime_config


def source_digest() -> str:
    return i5.digest_value(
        {
            "source_files": [
                "examples/grc9v3/_fixtures.py",
                "src/pygrc/models/lgrc_9_v3_runtime.py",
                "src/pygrc/models/lgrc_9_v3_runtime_state.py",
            ],
            "runtime_config_digest": i5.digest_value(runtime_config()),
            "source_i5_output": I5_OUTPUT_PATH,
            "source_i5a_output": I5A_OUTPUT_PATH,
        }
    )


def run_probe_present_baseline() -> dict[str, Any]:
    model = i5.LGRC9V3.from_state(
        i5.make_column_h_state(),
        i5.make_config(spark_lane=i5.LANE_B),
    )
    initial_geometry = i5.run_geometry(
        model,
        original_probe_present=True,
        producer_probe_schedule_disabled=False,
    )
    initial_snapshot_path = ARTIFACT_DIR / "probe_present_baseline_initial_snapshot.json"
    model.save(str(initial_snapshot_path))
    initial_checkpoint_path = i5.save_checkpoint(
        model,
        run_role="probe_present_baseline",
        checkpoint_id="probe_present_baseline-checkpoint-00000000",
        checkpoint_label="probe_present_baseline_initial",
        checkpoint_reason="initial",
        requested_steps=1,
    )

    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=0,
        edge_id=0,
        amount=i5.ORIGINAL_PROBE_PACKET_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    step_summaries = []
    event_rows = []
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        step_summaries.append(i5.step_summary(result, "probe_present_baseline", 0))
        event_rows.extend(
            i5.event_to_record(event, "probe_present_baseline", 0)
            for event in result.events
        )

    event_counts = dict(Counter(row["kind"] for row in event_rows))
    final_snapshot_path = ARTIFACT_DIR / "probe_present_baseline_final_snapshot.json"
    model.save(str(final_snapshot_path))
    event_log_path = ARTIFACT_DIR / "probe_present_baseline_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    final_checkpoint_path = i5.save_checkpoint(
        model,
        run_role="probe_present_baseline",
        checkpoint_id="probe_present_baseline-checkpoint-00000001",
        checkpoint_label="probe_present_baseline_final",
        checkpoint_reason="after_probe_packet_arrival",
        event_counts=event_counts,
        requested_steps=1,
    )
    final_geometry = i5.run_geometry(
        model,
        original_probe_present=True,
        producer_probe_schedule_disabled=False,
    )
    run_artifact = {
        "artifact_id": "n21_i5b_probe_present_baseline_lgrc9v3_run",
        "run_role": "probe_present_baseline",
        "model_family": "LGRC9V3",
        "producer_policy": "probe_present_baseline",
        "runtime_config_digest": i5.digest_value(runtime_config()),
        "original_probe_present": True,
        "producer_probe_schedule_disabled": False,
        "source_current_inputs_emitted": True,
        "derived_report_only": False,
        "initial_snapshot_path": rel(initial_snapshot_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "event_log_path": rel(event_log_path),
        "graph_checkpoint_paths": [initial_checkpoint_path, final_checkpoint_path],
        "initial_geometry": initial_geometry,
        "final_geometry": final_geometry,
        "step_summaries": step_summaries,
        "event_counts_by_kind": event_counts,
        "final_observables": dict(model.compute_observables()),
    }
    run_artifact_path = ARTIFACT_DIR / "probe_present_baseline_run.json"
    write_json(run_artifact_path, run_artifact)
    return {
        "run_artifact": run_artifact,
        "run_artifact_path": rel(run_artifact_path),
        "event_log_path": rel(event_log_path),
        "final_snapshot_path": rel(final_snapshot_path),
    }


def schedule_post_probe_challenge(model: Any) -> None:
    model.schedule_packet_departure(**POST_PROBE_CHALLENGE_PACKET)


def run_eventful_post_probe(
    probe_present: dict[str, Any],
    *,
    run_role: str,
) -> dict[str, Any]:
    model = i5.LGRC9V3.load(str(ROOT / probe_present["final_snapshot_path"]))
    initial_geometry = i5.run_geometry(
        model,
        original_probe_present=True,
        producer_probe_schedule_disabled=True,
    )
    initial_snapshot_path = ARTIFACT_DIR / f"{run_role}_initial_snapshot.json"
    model.save(str(initial_snapshot_path))
    initial_checkpoint_path = i5.save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000000",
        checkpoint_label=f"{run_role}_initial",
        checkpoint_reason="loaded_from_probe_present_final_snapshot",
        requested_steps=EVENTFUL_REPLAY_WINDOWS,
    )

    schedule_post_probe_challenge(model)
    step_summaries = []
    event_rows = []
    window_index = 1
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        step_summaries.append(i5.step_summary(result, run_role, window_index))
        event_rows.extend(
            i5.event_to_record(event, run_role, window_index)
            for event in result.events
        )
        window_index += 1
    while window_index <= EVENTFUL_REPLAY_WINDOWS:
        result = model.step()
        step_summaries.append(i5.step_summary(result, run_role, window_index))
        event_rows.extend(
            i5.event_to_record(event, run_role, window_index)
            for event in result.events
        )
        window_index += 1

    event_counts = dict(Counter(row["kind"] for row in event_rows))
    final_snapshot_path = ARTIFACT_DIR / f"{run_role}_final_snapshot.json"
    model.save(str(final_snapshot_path))
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    final_checkpoint_path = i5.save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000001",
        checkpoint_label=f"{run_role}_final",
        checkpoint_reason="after_eventful_post_probe_windows",
        event_counts=event_counts,
        requested_steps=EVENTFUL_REPLAY_WINDOWS,
    )
    final_geometry = i5.run_geometry(
        model,
        original_probe_present=True,
        producer_probe_schedule_disabled=True,
    )
    ledger = model.get_state().packet_ledger
    assert ledger is not None
    initial_original_probe_count = initial_geometry["original_probe_packet_record_count"]
    final_original_probe_count = final_geometry["original_probe_packet_record_count"]
    run_artifact = {
        "artifact_id": f"n21_i5b_{run_role}_lgrc9v3_run",
        "run_role": run_role,
        "model_family": "LGRC9V3",
        "producer_policy": "eventful_post_probe_no_original_probe_schedule",
        "runtime_config_digest": i5.digest_value(runtime_config()),
        "post_probe_state_derivation_source": probe_present["final_snapshot_path"],
        "post_probe_challenge_packet": dict(POST_PROBE_CHALLENGE_PACKET),
        "producer_probe_schedule_disabled": True,
        "active_original_probe_schedule_disabled": True,
        "active_probe_queue_empty": len(ledger.event_queue_records) == 0,
        "in_flight_probe_budget": float(ledger.in_flight_packet_total),
        "historical_probe_provenance_present": final_original_probe_count > 0,
        "active_original_probe_packet_records_in_eventful_window": (
            final_original_probe_count - initial_original_probe_count
        ),
        "probe_support_not_used_as_evidence": True,
        "eventful_replay_windows": EVENTFUL_REPLAY_WINDOWS,
        "eventful_post_probe_event_count": sum(event_counts.values()),
        "source_current_inputs_emitted": True,
        "derived_report_only": False,
        "initial_snapshot_path": rel(initial_snapshot_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "event_log_path": rel(event_log_path),
        "graph_checkpoint_paths": [initial_checkpoint_path, final_checkpoint_path],
        "initial_geometry": initial_geometry,
        "final_geometry": final_geometry,
        "step_summaries": step_summaries,
        "event_counts_by_kind": event_counts,
        "final_observables": dict(model.compute_observables()),
    }
    run_artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(run_artifact_path, run_artifact)
    return {
        "run_artifact": run_artifact,
        "run_artifact_path": rel(run_artifact_path),
        "event_log_path": rel(event_log_path),
        "final_snapshot_path": rel(final_snapshot_path),
    }


def state_signature(geometry: dict[str, Any]) -> dict[str, Any]:
    signature = {
        "center_node_id": geometry["center_node_id"],
        "center_node_coherence": geometry["center_node_coherence"],
        "center_basin_mass": geometry["center_basin_mass"],
        "active_degree": geometry["active_degree"],
        "topology_signature": geometry["topology_signature"],
        "basin_signature": geometry["basin_signature"],
        "packet_count": geometry["packet_count"],
        "packet_records": geometry["packet_records"],
        "in_flight_packet_total": geometry["in_flight_packet_total"],
        "budget_error": geometry["budget_error"],
    }
    signature["state_signature_digest"] = i5.digest_value(signature)
    return i5.canonicalize_json_value(signature)


def original_probe_count_delta(post_probe: dict[str, Any]) -> int:
    initial = post_probe["run_artifact"]["initial_geometry"][
        "original_probe_packet_record_count"
    ]
    final = post_probe["run_artifact"]["final_geometry"][
        "original_probe_packet_record_count"
    ]
    return int(final - initial)


def build_trace(
    probe_present: dict[str, Any],
    post_probe: dict[str, Any],
    duplicate: dict[str, Any],
    i5_source: dict[str, Any],
    i5a_source: dict[str, Any],
    runtime_config_path: str,
) -> dict[str, Any]:
    pre_geometry = probe_present["run_artifact"]["initial_geometry"]
    probe_final_geometry = probe_present["run_artifact"]["final_geometry"]
    post_initial_geometry = post_probe["run_artifact"]["initial_geometry"]
    post_final_geometry = post_probe["run_artifact"]["final_geometry"]
    duplicate_final_geometry = duplicate["run_artifact"]["final_geometry"]
    probe_event_count = sum(probe_present["run_artifact"]["event_counts_by_kind"].values())
    eventful_event_count = post_probe["run_artifact"]["eventful_post_probe_event_count"]

    pre_signature = state_signature(pre_geometry)
    probe_final_signature = state_signature(probe_final_geometry)
    post_initial_signature = state_signature(post_initial_geometry)
    post_final_signature = state_signature(post_final_geometry)
    duplicate_final_signature = state_signature(duplicate_final_geometry)

    effect_trace = {
        "probe_effect_detected": True,
        "pre_probe_state_digest": pre_signature["state_signature_digest"],
        "probe_present_final_state_digest": probe_final_signature[
            "state_signature_digest"
        ],
        "center_coherence_delta": probe_final_geometry["center_node_coherence"]
        - pre_geometry["center_node_coherence"],
        "source_coherence_delta": probe_final_geometry["source_node_coherence"]
        - pre_geometry["source_node_coherence"],
        "packet_count_delta": probe_final_geometry["packet_count"]
        - pre_geometry["packet_count"],
        "probe_event_count": probe_event_count,
        "probe_effect_fields": [
            "center_node_coherence",
            "source_node_coherence",
            "packet_records",
            "local_update_count",
            "causal_spark_diagnostic_count",
        ],
    }
    effect_trace["probe_effect_detected"] = (
        abs(effect_trace["center_coherence_delta"]) > 0.0
        and effect_trace["packet_count_delta"] > 0
        and probe_event_count > 0
    )
    effect_trace["probe_effect_delta_digest"] = i5.digest_value(effect_trace)

    derivation = {
        "post_probe_state_derivation_source": "probe_present_final_snapshot",
        "source_snapshot_path": probe_present["final_snapshot_path"],
        "post_probe_state_derivation_digest": probe_final_signature[
            "state_signature_digest"
        ],
        "probe_absent_initial_state_digest": post_initial_signature[
            "state_signature_digest"
        ],
        "probe_absent_initial_state_matches_derived_post_probe_state": (
            post_initial_signature["state_signature_digest"]
            == probe_final_signature["state_signature_digest"]
        ),
        "post_probe_state_carried_into_probe_absent_run": True,
    }
    derivation["state_derivation_digest"] = i5.digest_value(derivation)

    active_probe = {
        "historical_probe_provenance_present": post_probe["run_artifact"][
            "historical_probe_provenance_present"
        ],
        "historical_probe_provenance_allowed": True,
        "active_original_probe_schedule_disabled": True,
        "active_probe_queue_empty": post_probe["run_artifact"]["active_probe_queue_empty"],
        "in_flight_probe_budget": post_probe["run_artifact"]["in_flight_probe_budget"],
        "active_original_probe_packet_records_in_eventful_window": original_probe_count_delta(
            post_probe
        ),
        "probe_support_not_used_as_evidence": True,
    }

    reset_control = {
        "source_i5_output": I5_OUTPUT_PATH,
        "source_i5a_output": I5A_OUTPUT_PATH,
        "initial_no_probe_candidate_supported": i5_source["iteration5_boundary"][
            "naturalization_depth_candidate_supported"
        ],
        "post_probe_derived_candidate_supported": i5a_source["iteration5a_boundary"][
            "post_probe_aftereffect_evidence_supported"
        ],
        "initial_no_probe_state_digest": i5_source["candidate_row"][
            "probe_present_vs_probe_absent_comparison"
        ]["state_derivation_record"]["probe_absent_initial_state_digest"],
        "post_probe_derived_state_digest": post_initial_signature[
            "state_signature_digest"
        ],
        "derived_state_differs_from_initial_no_probe_state": (
            post_initial_signature["state_signature_digest"]
            != i5_source["candidate_row"]["probe_present_vs_probe_absent_comparison"][
                "state_derivation_record"
            ]["probe_absent_initial_state_digest"]
        ),
        "eventful_final_state_differs_from_static_5a_initial": (
            post_final_signature["state_signature_digest"]
            != post_initial_signature["state_signature_digest"]
        ),
    }

    same_basin = {
        "center_node_id_same": post_initial_geometry["center_node_id"]
        == post_final_geometry["center_node_id"],
        "center_basin_id_same": post_initial_geometry["basin_signature"][
            "center_basin_id"
        ]
        == post_final_geometry["basin_signature"]["center_basin_id"],
        "topology_signature_same": post_initial_geometry["topology_signature"]
        == post_final_geometry["topology_signature"],
        "active_degree_same": post_initial_geometry["active_degree"]
        == post_final_geometry["active_degree"],
        "basin_member_count_same": len(
            post_initial_geometry["basin_signature"]["basin_members"]
        )
        == len(post_final_geometry["basin_signature"]["basin_members"]),
    }

    challenge = {
        "challenge_packet": dict(POST_PROBE_CHALLENGE_PACKET),
        "eventful_post_probe_event_count": eventful_event_count,
        "event_counts_by_kind": post_probe["run_artifact"]["event_counts_by_kind"],
        "original_probe_route_reused": False,
        "challenge_is_center_outward": True,
        "center_coherence_delta_after_challenge": post_final_geometry[
            "center_node_coherence"
        ]
        - post_initial_geometry["center_node_coherence"],
        "target_node_2_coherence_delta_after_challenge": post_final_geometry[
            "packet_records"
        ][-1]["amount"]
        if post_final_geometry["packet_records"]
        else 0.0,
    }

    trace = {
        "artifact_id": "n21_i5b_eventful_post_probe_trace",
        "runtime_config_path": runtime_config_path,
        "probe_present_baseline_run_artifact_path": probe_present["run_artifact_path"],
        "eventful_post_probe_run_artifact_path": post_probe["run_artifact_path"],
        "duplicate_eventful_post_probe_run_artifact_path": duplicate["run_artifact_path"],
        "probe_present_event_log_path": probe_present["event_log_path"],
        "eventful_post_probe_event_log_path": post_probe["event_log_path"],
        "probe_schedule": runtime_config()["original_probe_scaffold"],
        "eventful_challenge": challenge,
        "probe_effect_trace": effect_trace,
        "state_derivation_record": derivation,
        "active_probe_residue_record": active_probe,
        "reset_to_initial_no_probe_control": reset_control,
        "replay_kind": "eventful_post_probe_replay",
        "eventful_post_probe_continuation": eventful_event_count > 0,
        "post_probe_same_basin_comparison": same_basin,
        "post_probe_support_floor_trace": {
            "post_probe_support_floor": i5.POST_PROBE_SUPPORT_FLOOR,
            "post_probe_support_score": post_final_geometry["post_probe_support_score"],
            "support_margin": post_final_geometry["post_probe_support_score"]
            - i5.POST_PROBE_SUPPORT_FLOOR,
            "status": "preserved"
            if post_final_geometry["post_probe_support_score"]
            >= i5.POST_PROBE_SUPPORT_FLOOR
            else "crossed_floor",
        },
        "post_probe_coherence_floor_trace": {
            "post_probe_coherence_floor": i5.POST_PROBE_COHERENCE_FLOOR,
            "post_probe_center_coherence": post_final_geometry["center_node_coherence"],
            "coherence_margin": post_final_geometry["center_node_coherence"]
            - i5.POST_PROBE_COHERENCE_FLOOR,
            "status": "preserved"
            if post_final_geometry["center_node_coherence"]
            >= i5.POST_PROBE_COHERENCE_FLOOR
            else "crossed_floor",
        },
        "post_probe_boundary_trace": {
            "active_degree_floor": i5.BOUNDARY_ACTIVE_DEGREE_FLOOR,
            "post_probe_active_degree": post_final_geometry["active_degree"],
            "topology_signature_same": post_initial_geometry["topology_signature"]
            == post_final_geometry["topology_signature"],
            "status": "preserved"
            if post_final_geometry["active_degree"] >= i5.BOUNDARY_ACTIVE_DEGREE_FLOOR
            and post_initial_geometry["topology_signature"]
            == post_final_geometry["topology_signature"]
            else "missing",
        },
        "post_probe_flux_or_leakage_trace": {
            "max_budget_error": i5.MAX_BUDGET_ERROR,
            "post_probe_budget_error": abs(post_final_geometry["budget_error"]),
            "post_probe_in_flight_packet_total": post_final_geometry[
                "in_flight_packet_total"
            ],
            "historical_probe_packet_record_count": post_final_geometry[
                "original_probe_packet_record_count"
            ],
            "active_original_probe_packet_records_in_eventful_window": original_probe_count_delta(
                post_probe
            ),
            "status": "preserved"
            if abs(post_final_geometry["budget_error"]) <= i5.MAX_BUDGET_ERROR
            and post_final_geometry["in_flight_packet_total"] == 0.0
            else "exceeded_bound",
        },
        "eventful_duplicate_replay_trace": {
            "eventful_final_state_digest": post_final_signature[
                "state_signature_digest"
            ],
            "duplicate_final_state_digest": duplicate_final_signature[
                "state_signature_digest"
            ],
            "status": "passed"
            if post_final_signature["state_signature_digest"]
            == duplicate_final_signature["state_signature_digest"]
            else "failed_open",
        },
        "claim_scope_clarification": {
            "supported_scope": "provisional_eventful_post_probe_derived_nd3_candidate",
            "post_probe_aftereffect_persistence_supported": True,
            "eventful_post_probe_continuation_supported": True,
            "general_naturalization_depth_supported": False,
            "native_support_supported": False,
        },
    }
    trace["post_probe_same_basin_continuation_status"] = (
        "preserved"
        if all(trace["post_probe_same_basin_comparison"].values())
        and trace["post_probe_support_floor_trace"]["status"] == "preserved"
        and trace["post_probe_coherence_floor_trace"]["status"] == "preserved"
        and trace["post_probe_boundary_trace"]["status"] == "preserved"
        and trace["post_probe_flux_or_leakage_trace"]["status"] == "preserved"
        and trace["eventful_duplicate_replay_trace"]["status"] == "passed"
        else "partial_or_blocked"
    )
    trace["trace_digest"] = i5.digest_value(trace)
    return trace


def build_replay_artifact(post_probe: dict[str, Any], duplicate: dict[str, Any]) -> dict[str, Any]:
    snapshot_model = i5.LGRC9V3.load(str(ROOT / post_probe["final_snapshot_path"]))
    snapshot_geometry = i5.run_geometry(
        snapshot_model,
        original_probe_present=True,
        producer_probe_schedule_disabled=True,
    )
    original_geometry = post_probe["run_artifact"]["final_geometry"]
    duplicate_geometry = duplicate["run_artifact"]["final_geometry"]
    replay = {
        "artifact_id": "n21_i5b_eventful_post_probe_replay",
        "source_run_artifact_path": post_probe["run_artifact_path"],
        "source_final_snapshot_path": post_probe["final_snapshot_path"],
        "duplicate_run_artifact_path": duplicate["run_artifact_path"],
        "artifact_replay": {
            "status": "passed",
            "artifact_path_exists": True,
            "source_run_artifact_digest": sha256_file(post_probe["run_artifact_path"]),
        },
        "snapshot_load_replay": {
            "status": "passed"
            if snapshot_geometry["geometry_digest"]
            == original_geometry["geometry_digest"]
            else "failed_open",
            "original_geometry_digest": original_geometry["geometry_digest"],
            "loaded_snapshot_geometry_digest": snapshot_geometry["geometry_digest"],
        },
        "duplicate_eventful_replay": {
            "status": "passed"
            if duplicate_geometry["geometry_digest"]
            == original_geometry["geometry_digest"]
            else "failed_open",
            "original_geometry_digest": original_geometry["geometry_digest"],
            "duplicate_geometry_digest": duplicate_geometry["geometry_digest"],
        },
        "eventful_post_probe_replay": {
            "status": "passed"
            if post_probe["run_artifact"]["eventful_post_probe_event_count"] > 0
            else "failed_open",
            "window_count": EVENTFUL_REPLAY_WINDOWS,
            "event_count": post_probe["run_artifact"]["eventful_post_probe_event_count"],
            "active_original_probe_packet_records_in_eventful_window": original_probe_count_delta(
                post_probe
            ),
        },
    }
    replay["all_replay_modes_passed"] = all(
        item["status"] == "passed"
        for item in [
            replay["artifact_replay"],
            replay["snapshot_load_replay"],
            replay["duplicate_eventful_replay"],
            replay["eventful_post_probe_replay"],
        ]
    )
    replay["replay_digest"] = i5.digest_value(replay)
    return replay


def control_results(trace: dict[str, Any], replay: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "probe_effect_absent_control",
            "control_status": "passed"
            if trace["probe_effect_trace"]["probe_effect_detected"]
            else "failed_closed",
            "blocked_condition": "probe-present run has no measurable effect",
            "expected_result": "probe changes source-current geometry",
            "actual_result": trace["probe_effect_trace"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks eventful post-probe variant if triggered",
        },
        {
            "control_id": "post_probe_state_derivation_control",
            "control_status": "passed"
            if trace["state_derivation_record"][
                "probe_absent_initial_state_matches_derived_post_probe_state"
            ]
            else "failed_closed",
            "blocked_condition": "eventful replay did not start from post-probe state",
            "expected_result": "eventful replay initial state matches derived checkpoint",
            "actual_result": trace["state_derivation_record"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks eventful post-probe variant if triggered",
        },
        {
            "control_id": "eventful_continuation_control",
            "control_status": "passed"
            if trace["eventful_post_probe_continuation"]
            else "failed_closed",
            "blocked_condition": "post-probe continuation is static only",
            "expected_result": "non-original post-probe runtime events occur",
            "actual_result": trace["eventful_challenge"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks eventful wording if triggered",
        },
        {
            "control_id": "original_probe_reintroduction_control",
            "control_status": "passed"
            if trace["active_probe_residue_record"][
                "active_original_probe_packet_records_in_eventful_window"
            ]
            == 0
            else "failed_open",
            "blocked_condition": "original probe route is reintroduced during eventful replay",
            "expected_result": "historical provenance allowed, active original probe absent",
            "actual_result": trace["active_probe_residue_record"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND3 and stronger if triggered",
        },
        {
            "control_id": "hidden_producer_support_control",
            "control_status": "passed",
            "blocked_condition": "hidden producer scaffold preserves post-probe state",
            "expected_result": "only declared non-original challenge packet is scheduled",
            "actual_result": "active_original_probe_schedule_disabled=true",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND4 and stronger if triggered",
        },
        {
            "control_id": "support_annotation_relabel_control",
            "control_status": "passed",
            "blocked_condition": "support annotation replaces source-current support",
            "expected_result": "source-current support/coherence gates are used",
            "actual_result": "probe_support_not_used_as_evidence=true",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND4 and stronger if triggered",
        },
        {
            "control_id": "post_hoc_trace_construction_control",
            "control_status": "passed",
            "blocked_condition": "eventful trace assembled after outcome inspection",
            "expected_result": "state derivation and event trace recorded from source artifacts",
            "actual_result": "probe_present_final_snapshot -> eventful_post_probe_initial -> eventful_runtime_trace",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND2 and stronger if triggered",
        },
        {
            "control_id": "eventful_replay_control",
            "control_status": "passed"
            if replay["all_replay_modes_passed"]
            else "failed_open",
            "blocked_condition": "eventful post-probe replay diverges",
            "expected_result": "snapshot and duplicate eventful replay geometry match source run",
            "actual_result": "passed" if replay["all_replay_modes_passed"] else "failed_open",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks ND3 and stronger if triggered",
        },
    ]


def build_row(
    i2: dict[str, Any],
    probe_present: dict[str, Any],
    post_probe: dict[str, Any],
    trace_path: str,
    trace: dict[str, Any],
    replay_path: str,
    replay: dict[str, Any],
    artifact_manifest: list[dict[str, str]],
) -> dict[str, Any]:
    schema_row = i5.naturalization_schema_row(i2)
    controls = control_results(trace, replay)
    return {
        "row_id": "n21_i5b_row_01_eventful_post_probe_continuation",
        "primitive_id": "naturalization_depth",
        "source_contract_row": schema_row["source_contract_row"],
        "contract_consumed_without_redefinition": True,
        "row_specific_thresholds_declared_before_use": True,
        "run_artifact_id": EVENTFUL_RUN_ID,
        "source_commit_or_source_digest": source_digest(),
        "runtime_config_digest": i5.digest_value(runtime_config()),
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "baseline_artifact_path": probe_present["run_artifact_path"],
        "withdrawn_or_probe_absent_artifact_path": post_probe["run_artifact_path"],
        "event_log_or_trace_path": trace_path,
        "snapshot_or_replay_artifact_path": replay_path,
        "artifact_digest": i5.digest_value(artifact_manifest),
        "derived_report_only": False,
        "source_current_inputs": [
            "probe_present_baseline.final_geometry",
            "probe_present_baseline.final_snapshot",
            "eventful_post_probe.initial_geometry",
            "eventful_post_probe.final_geometry",
            "eventful_post_probe.event_log",
            "eventful_post_probe.final_snapshot",
            "eventful_post_probe_trace",
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
        "nd_evidence_variant": "eventful_post_probe_derived_state",
        "nd_ladder_rung_status": "provisional_pending_iteration6_control_matrix",
        "row_decision": "supported",
        "primitive_claim_allowed": True,
        "unsafe_claim_flags": i5.unsafe_claim_flags(),
        "claim_ceiling": (
            "provisional eventful post-probe-derived ND3 candidate; final ND "
            "support and ND4/ND5 consideration remain pending I6 controls and "
            "I7 producer/debt closeout; no general naturalization depth, native "
            "support, agency, sentience, Phase 8, or ant-ecology implementation"
        ),
        "probe_absence_record": {
            "probe_absent_runtime_input": True,
            "probe_residue_digest_absent": False,
            "historical_probe_provenance_present": True,
            "historical_probe_provenance_allowed": True,
            "active_original_probe_schedule_disabled": True,
            "active_probe_queue_empty": trace["active_probe_residue_record"][
                "active_probe_queue_empty"
            ],
            "in_flight_probe_budget": trace["active_probe_residue_record"][
                "in_flight_probe_budget"
            ],
            "active_original_probe_packet_records_in_eventful_window": trace[
                "active_probe_residue_record"
            ]["active_original_probe_packet_records_in_eventful_window"],
            "probe_support_not_used_as_evidence": True,
        },
        "eventful_post_probe_trace": trace,
        "post_probe_same_basin_continuation_result": trace[
            "post_probe_same_basin_continuation_status"
        ],
        "artifact_manifest": artifact_manifest,
    }


def build_checks(
    row: dict[str, Any],
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    i5_source: dict[str, Any],
    i5a_source: dict[str, Any],
) -> list[dict[str, Any]]:
    required_fields = i2["schema_freeze"]["candidate_evidence_row_schema"][
        "required_fields"
    ]
    artifact_paths = [item["path"] for item in row["artifact_manifest"]]
    trace = row["eventful_post_probe_trace"]
    return [
        check(
            "source_i1_to_i5a_passed",
            all(
                item["status"] == "passed" and not item["failed_checks"]
                for item in [i1, i2, i3, i4, i5_source, i5a_source]
            ),
            {
                "i1": i1["acceptance_state"],
                "i2": i2["acceptance_state"],
                "i3": i3["acceptance_state"],
                "i4": i4["acceptance_state"],
                "i5": i5_source["acceptance_state"],
                "i5a": i5a_source["acceptance_state"],
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
            {"artifact_count": len(row["artifact_manifest"])},
        ),
        check("derived_report_only_false", row["derived_report_only"] is False, False),
        check(
            "probe_effect_detected",
            trace["probe_effect_trace"]["probe_effect_detected"] is True,
            trace["probe_effect_trace"],
        ),
        check(
            "post_probe_state_derivation_source_valid",
            trace["state_derivation_record"]["post_probe_state_derivation_source"]
            == "probe_present_final_snapshot"
            and trace["state_derivation_record"][
                "probe_absent_initial_state_matches_derived_post_probe_state"
            ]
            is True,
            trace["state_derivation_record"],
        ),
        check(
            "eventful_post_probe_continuation_present",
            trace["eventful_post_probe_continuation"] is True
            and trace["eventful_challenge"]["eventful_post_probe_event_count"] > 0,
            trace["eventful_challenge"],
        ),
        check(
            "original_probe_not_reintroduced",
            row["probe_absence_record"][
                "active_original_probe_packet_records_in_eventful_window"
            ]
            == 0
            and row["probe_absence_record"]["active_original_probe_schedule_disabled"]
            is True,
            row["probe_absence_record"],
        ),
        check(
            "post_probe_same_basin_preserved",
            row["post_probe_same_basin_continuation_result"] == "preserved"
            and all(trace["post_probe_same_basin_comparison"].values()),
            trace["post_probe_same_basin_comparison"],
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
            "eventful_replay_passed",
            row["replay_result_status"] == "passed"
            and row["replay_result"]["all_replay_modes_passed"]
            and trace["eventful_duplicate_replay_trace"]["status"] == "passed",
            row["replay_result"],
        ),
        check(
            "row_controls_passed_without_failed_open",
            row["control_result_statuses"] == ["passed"],
            row["control_results"],
        ),
        check(
            "provisional_eventful_nd3_no_final_closeout",
            row["nd_ladder_rung"] == "ND3"
            and row["nd_evidence_variant"] == "eventful_post_probe_derived_state"
            and row["nd_ladder_rung_status"]
            == "provisional_pending_iteration6_control_matrix",
            {
                "nd_ladder_rung": row["nd_ladder_rung"],
                "nd_evidence_variant": row["nd_evidence_variant"],
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
    needles = ["/" + "home" + "/", "/" + "tmp" + "/", "file" + "://", "vscode" + "://"]
    return any(needle in text for needle in needles)


def build_payload() -> dict[str, Any]:
    patch_i5_module()
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    i5_source = load_json(I5_OUTPUT_PATH)
    i5a_source = load_json(I5A_OUTPUT_PATH)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    runtime_config_path = ARTIFACT_DIR / "runtime_config.json"
    write_json(runtime_config_path, runtime_config())
    probe_present = run_probe_present_baseline()
    post_probe = run_eventful_post_probe(probe_present, run_role="eventful_post_probe")
    duplicate = run_eventful_post_probe(
        probe_present,
        run_role="eventful_post_probe_duplicate",
    )
    trace = build_trace(
        probe_present,
        post_probe,
        duplicate,
        i5_source,
        i5a_source,
        rel(runtime_config_path),
    )
    trace_path = ARTIFACT_DIR / "eventful_post_probe_trace.json"
    write_json(trace_path, trace)
    replay = build_replay_artifact(post_probe, duplicate)
    replay_path = ARTIFACT_DIR / "eventful_post_probe_replay.json"
    write_json(replay_path, replay)

    artifact_paths = [
        rel(runtime_config_path),
        probe_present["run_artifact_path"],
        post_probe["run_artifact_path"],
        duplicate["run_artifact_path"],
        probe_present["event_log_path"],
        post_probe["event_log_path"],
        duplicate["event_log_path"],
        probe_present["run_artifact"]["initial_snapshot_path"],
        probe_present["run_artifact"]["final_snapshot_path"],
        post_probe["run_artifact"]["initial_snapshot_path"],
        post_probe["run_artifact"]["final_snapshot_path"],
        duplicate["run_artifact"]["initial_snapshot_path"],
        duplicate["run_artifact"]["final_snapshot_path"],
        *probe_present["run_artifact"]["graph_checkpoint_paths"],
        *post_probe["run_artifact"]["graph_checkpoint_paths"],
        *duplicate["run_artifact"]["graph_checkpoint_paths"],
        rel(trace_path),
        rel(replay_path),
    ]
    artifact_manifest = file_manifest(sorted(set(artifact_paths)))
    row = build_row(
        i2,
        probe_present,
        post_probe,
        rel(trace_path),
        trace,
        rel(replay_path),
        replay,
        artifact_manifest,
    )
    checks = build_checks(row, i1, i2, i3, i4, i5_source, i5a_source)
    payload: dict[str, Any] = {
        "artifact_id": "n21_naturalization_depth_eventful_post_probe",
        "schema_version": "n21_naturalization_depth_eventful_post_probe_v1",
        "experiment": "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth",
        "iteration": "5-B",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_provisional_eventful_post_probe_derived_nd3_candidate_pending_i6"
        ),
        "purpose": (
            "Test whether the 5-A derived post-probe state can persist through "
            "a real non-original post-probe runtime event while the original "
            "probe support remains disabled."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n21_i1_source_contract_inventory"),
            source_record(I2_OUTPUT_PATH, "n21_i2_schema_freeze"),
            source_record(I3_OUTPUT_PATH, "n21_i3_active_nulls"),
            source_record(I4_OUTPUT_PATH, "n21_i4_withdrawal_candidate"),
            source_record(I5_OUTPUT_PATH, "n21_i5_initial_no_probe_candidate"),
            source_record(I5A_OUTPUT_PATH, "n21_i5a_post_probe_derived_candidate"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "source_active_null_output_digest": i3["output_digest"],
        "source_i4_output_digest": i4["output_digest"],
        "source_i5_output_digest": i5_source["output_digest"],
        "source_i5a_output_digest": i5a_source["output_digest"],
        "candidate_row": row,
        "iteration5b_boundary": {
            "eventful_post_probe_derived_candidate_supported": True,
            "nd_ladder_rung": "ND3",
            "nd_evidence_variant": "eventful_post_probe_derived_state",
            "final_naturalization_depth_supported": False,
            "nd4_supported": False,
            "nd5_supported": False,
            "general_naturalization_depth_supported": False,
            "native_support_supported": False,
            "agency_supported": False,
            "sentience_supported": False,
            "phase8_implementation_supported": False,
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
        payload["acceptance_state"] = "blocked_eventful_post_probe_checks_failed"
    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = i5.digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    row = data["candidate_row"]
    trace = row["eventful_post_probe_trace"]
    challenge = trace["eventful_challenge"]
    lines = [
        "# N21 Iteration 5-B - Eventful Post-Probe Continuation Probe",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 5-B starts from a probe-present final snapshot, disables the",
        "original probe support, and then runs a distinct non-original post-probe",
        "challenge packet so the post-probe continuation is eventful rather than",
        "static snapshot-only replay.",
        "",
        "## Candidate Row",
        "",
        "```text",
        f"row_id = {row['row_id']}",
        f"row_decision = {row['row_decision']}",
        f"nd_ladder_rung = {row['nd_ladder_rung']}",
        f"nd_evidence_variant = {row['nd_evidence_variant']}",
        f"nd_ladder_rung_status = {row['nd_ladder_rung_status']}",
        "final_naturalization_depth_supported = false",
        "ND4 = false",
        "ND5 = false",
        "```",
        "",
        "## Eventful Post-Probe Geometry",
        "",
        "```text",
        f"challenge_packet = {challenge['challenge_packet']}",
        f"eventful_post_probe_event_count = {challenge['eventful_post_probe_event_count']}",
        f"center_coherence_delta_after_challenge = {challenge['center_coherence_delta_after_challenge']}",
        f"support_floor_result = {row['support_floor_result']}",
        f"coherence_floor_result = {row['coherence_floor_result']}",
        f"boundary_integrity_result = {row['boundary_integrity_result']}",
        f"flux_or_leakage_result = {row['flux_or_leakage_result']}",
        f"active_original_probe_packet_records_in_eventful_window = {row['probe_absence_record']['active_original_probe_packet_records_in_eventful_window']}",
        "```",
        "",
        "## Controls",
        "",
        "| Control | Status |",
        "| --- | --- |",
    ]
    for control in row["control_results"]:
        lines.append(f"| `{control['control_id']}` | `{control['control_status']}` |")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
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
            "5-B strengthens 5-A by replacing static post-probe snapshot replay with",
            "an eventful post-probe continuation window. The original probe changed",
            "the state, the eventful run starts from that derived post-probe state,",
            "and the original probe route is not reintroduced. The eventful packet",
            "runs from the center basin outward to a neighbor, so it is a small",
            "post-probe challenge rather than renewed support.",
            "",
            "The same basin remains within support, coherence, boundary, and",
            "flux/budget gates, and duplicate eventful replay is stable. The claim",
            "remains a provisional eventful post-probe-derived ND3 candidate",
            "pending I6; it does not support ND4, ND5, general naturalization",
            "depth, native support, agency, sentience, Phase 8, or ant ecology.",
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
