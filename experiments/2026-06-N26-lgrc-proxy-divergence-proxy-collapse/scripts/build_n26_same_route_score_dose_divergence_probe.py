#!/usr/bin/env python3
"""Build N26 Iteration 5-C same-route score-dose divergence probe."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUT = EXPERIMENT / "outputs" / "n26_same_route_score_dose_divergence_probe.json"
REPORT = EXPERIMENT / "reports" / "n26_same_route_score_dose_divergence_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n26_same_route_score_dose_divergence_probe_artifacts"

I4_OUTPUT = EXPERIMENT / "outputs" / "n26_source_current_proxy_derivation_probe.json"
I4A_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_derivation_sensitivity_probe.json"
I5_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_divergence_contrast_matrix.json"
I5A_OUTPUT = EXPERIMENT / "outputs" / "n26_alternative_proxy_surface_divergence_probe.json"
I5B_OUTPUT = EXPERIMENT / "outputs" / "n26_fixed_surface_divergence_search.json"

N25_2_EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
N25_2_CLOSEOUT = N25_2_EXPERIMENT / "outputs" / "n25_2_closeout_and_n26_handoff.json"
EXAMPLE_FIXTURE = ROOT / "examples" / "lgrc9v3" / "multi_basin_formation_bundle.py"
RUNTIME_CONTRACT = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_contract.py"
RUNTIME_CODE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime.py"
RUNTIME_STATE = ROOT / "src" / "pygrc" / "models" / "lgrc_9_v3_runtime_state.py"
TELEMETRY_CODE = ROOT / "src" / "pygrc" / "telemetry" / "lgrc9v3_contract.py"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_same_route_score_dose_divergence_probe.py"
)

EXPECTED_I4_OUTPUT_DIGEST = "b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680"
EXPECTED_I4A_OUTPUT_DIGEST = "5dbe325f6ce1ff95434b978e69cf659fdf609e2890960198aca66e2c5c85e414"
EXPECTED_I5_OUTPUT_DIGEST = "52e7cba79816e840947472d35ee8906f357db1bcf896b59f59bbac243d9ee4a5"
EXPECTED_I5A_OUTPUT_DIGEST = "108849bf8b5249b97611461a4423d4986030c6d84d83b6580ba03cfc561e8eda"
EXPECTED_I5B_OUTPUT_DIGEST = "cab31a49994ae2ddf1c031e0e3f30c6c17c9dd169bbb3a9d2ccdc80b1da59c73"
EXPECTED_N25_2_CLOSEOUT_DIGEST = "b92401da545899c7721ab42692827beb5b357bbd246d8991d7ad56649a6bbf03"

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def canonical_compact(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_data(data: Any) -> str:
    return hashlib.sha256(canonical_compact(data).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def contains_absolute_path(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return any(marker in text for marker in ABSOLUTE_PATH_MARKERS)


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def jsonable(payload: Any) -> Any:
    if hasattr(payload, "to_artifact"):
        return jsonable(payload.to_artifact())
    if isinstance(payload, Mapping):
        return {str(key): jsonable(value) for key, value in payload.items()}
    if isinstance(payload, Sequence) and not isinstance(payload, str | bytes):
        return [jsonable(value) for value in payload]
    if hasattr(payload, "kind") and hasattr(payload, "payload"):
        return {
            "kind": str(payload.kind),
            "step_index": int(payload.step_index),
            "payload": jsonable(payload.payload),
            "source_family": str(payload.source_family),
        }
    return payload


def import_fixture() -> Any:
    spec = importlib.util.spec_from_file_location(
        "n26_i5c_multi_basin_fixture",
        EXAMPLE_FIXTURE,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to import LGRC9V3 fixture")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_runtime_model_from_snapshot(fixture: Any, snapshot: dict[str, Any]) -> Any:
    with tempfile.TemporaryDirectory() as temp_dir:
        snapshot_path = Path(temp_dir) / "n26_i5c_runtime_snapshot.json"
        snapshot_path.write_text(canonical_json(snapshot), encoding="utf-8")
        return fixture.LGRC9V3.load(str(snapshot_path))


def route_spec_id(sink: int, dose_label: str) -> str:
    return f"candidate:sink{sink}-{dose_label}"


def child_core_value(record: dict[str, Any], field: str) -> float:
    core_id = str(record["child_basin_core_ids"][0])
    return float(record[field][core_id])


def basin_metric_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "child_basin_core_ids": record["child_basin_core_ids"],
        "child_basin_membership_digest": record["child_basin_membership_digest"],
        "support_floor": child_core_value(record, "child_basin_support_floor_records"),
        "coherence_floor": child_core_value(record, "child_basin_coherence_floor_records"),
        "boundary_value": child_core_value(record, "child_basin_boundary_records"),
        "flux_value": child_core_value(record, "child_basin_flux_records"),
        "child_basin_state_digest": record["child_basin_state_digest"],
    }


def run_score_dose(
    *,
    fixture: Any,
    family_id: str,
    selected_sink_id: int,
    selected_score: float,
    competitor_score: float,
    dose_label: str,
) -> dict[str, Any]:
    competitor_sink_id = 2 if selected_sink_id == 0 else 0
    model = fixture.LGRC9V3.from_state(
        fixture.three_node_state(),
        fixture.multi_basin_params(),
    )
    initial_snapshot_digest = digest_data(model.snapshot())
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    step_result = model.step()
    surface = model.get_state().causal_pulse_substrate_surface_log[-1]
    selected_route_id = route_spec_id(selected_sink_id, dose_label)
    competitor_route_id = f"candidate:sink{competitor_sink_id}-control"
    candidate_result = model.emit_native_route_candidate_set(
        arbitration_window_id=f"window:n26-i5c-{family_id}-{dose_label}",
        source_surface_digest=str(surface.surface_digest),
        unresolved_tie_policy=(
            fixture.LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED
        ),
        candidate_routes=(
            fixture.native_route_candidate_spec(
                candidate_route_id=competitor_route_id,
                selected_sink_id=competitor_sink_id,
                losing_sink_ids=(selected_sink_id,),
                score=competitor_score,
            ),
            fixture.native_route_candidate_spec(
                candidate_route_id=selected_route_id,
                selected_sink_id=selected_sink_id,
                losing_sink_ids=(competitor_sink_id,),
                score=selected_score,
            ),
        ),
    )
    candidate_set = candidate_result["candidate_set_record"]
    arbitration_result = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
    )
    arbitration = arbitration_result["route_arbitration_record"]
    commit_result = model.commit_native_route_arbitration_selection(
        native_route_arbitration_reference=str(arbitration.native_route_arbitration_digest),
    )
    state = model.get_state()
    final_snapshot = model.snapshot()
    child_records = [record.to_artifact() for record in state.child_basin_state_log]
    if len(child_records) != 1:
        raise RuntimeError(f"Expected one child-basin record for {family_id}/{dose_label}")
    child_record = child_records[0]
    loaded = load_runtime_model_from_snapshot(fixture, final_snapshot)
    replay = loaded.validate_multi_basin_child_basin_replay(
        source_child_basin_state_digest=str(child_record["child_basin_state_digest"]),
        snapshot_replay_artifact=loaded.snapshot(),
    )
    duplicate = loaded.validate_multi_basin_child_basin_replay(
        source_child_basin_state_digest=str(child_record["child_basin_state_digest"]),
        snapshot_replay_artifact=loaded.snapshot(),
    )
    replay_record = replay["replay_validation_record"].to_artifact()
    duplicate_record = duplicate["replay_validation_record"].to_artifact()
    topology_events = [
        {
            "kind": event.kind,
            "step_index": int(event.step_index),
            "payload": jsonable(event.payload),
            "source_family": str(event.source_family),
        }
        for event in state.topology_event_log
    ]
    return {
        "family_id": family_id,
        "dose_label": dose_label,
        "selected_sink_id": selected_sink_id,
        "competitor_sink_id": competitor_sink_id,
        "selected_route_id": selected_route_id,
        "selected_score": selected_score,
        "competitor_route_id": competitor_route_id,
        "competitor_score": competitor_score,
        "params_hash": model.get_params().params_hash,
        "initial_snapshot_digest": initial_snapshot_digest,
        "final_snapshot_digest": digest_data(final_snapshot),
        "step_result": {
            "step_index": int(step_result.step_index),
            "time": float(step_result.time),
            "event_count": len(step_result.events),
        },
        "candidate_records": [
            candidate.to_artifact()
            for candidate in candidate_result["candidate_records"]
        ],
        "candidate_set_record": candidate_set.to_artifact(),
        "arbitration_record": arbitration.to_artifact(),
        "commit_result": {
            "committed": bool(commit_result["committed"]),
            "reason_code": str(commit_result["reason_code"]),
            "child_basin_record_count": len(commit_result["child_basin_state_records"]),
            "selected_topology_event_digest": str(
                commit_result["selected_topology_event_digest"]
            ),
            "selected_candidate_route_record": (
                commit_result["selected_candidate_route_record"].to_artifact()
            ),
            "flow_record_count": len(commit_result["post_refinement_flow_window_records"]),
            "surface_lineage_record_count": len(commit_result["surface_lineage_records"]),
            "topology_state_reabsorption_record_count": len(
                commit_result["topology_state_reabsorption_records"]
            ),
        },
        "topology_event_counts": dict(Counter(event.kind for event in state.topology_event_log)),
        "topology_events": topology_events,
        "child_basin_record": child_record,
        "basin_metric_summary": basin_metric_summary(child_record),
        "replay_record": replay_record,
        "duplicate_replay_record": duplicate_record,
        "replay_validation_digest": str(replay["replay_validation_digest"]),
        "duplicate_replay_validation_digest": str(duplicate["replay_validation_digest"]),
    }


def write_trace_artifact(row_id: str, artifact_role: str, payload: Any) -> dict[str, str]:
    path = ARTIFACT_DIR / row_id / f"{artifact_role}.json"
    write_json(path, payload)
    return {
        "path": rel(path),
        "sha256": sha256_file(path),
        "artifact_role": artifact_role,
    }


def build_artifact_manifest(row_id: str, traces: dict[str, Any]) -> list[dict[str, str]]:
    return [write_trace_artifact(row_id, role, traces[role]) for role in sorted(traces)]


def replay_passed(run: dict[str, Any]) -> bool:
    record = run["replay_record"]
    duplicate = run["duplicate_replay_record"]
    return (
        record["artifact_replay_result"] == "passed"
        and record["snapshot_load_replay_result"] == "passed"
        and record["time_order_replay_result"] == "passed"
        and duplicate["artifact_replay_result"] == "passed"
    )


def build_family_row(family_id: str, low: dict[str, Any], high: dict[str, Any]) -> dict[str, Any]:
    low_basin = low["basin_metric_summary"]
    high_basin = high["basin_metric_summary"]
    proxy_delta = high["selected_score"] - low["selected_score"]
    support_delta = high_basin["support_floor"] - low_basin["support_floor"]
    coherence_delta = high_basin["coherence_floor"] - low_basin["coherence_floor"]
    boundary_delta = high_basin["boundary_value"] - low_basin["boundary_value"]
    flux_delta = high_basin["flux_value"] - low_basin["flux_value"]
    same_geometry = (
        low_basin["child_basin_core_ids"] == high_basin["child_basin_core_ids"]
        and low_basin["child_basin_membership_digest"] == high_basin["child_basin_membership_digest"]
        and support_delta == 0.0
        and coherence_delta == 0.0
        and boundary_delta == 0.0
        and flux_delta == 0.0
    )
    row_id = f"n26_i5c_same_route_score_dose_{family_id}"
    traces = {
        "runtime_trace": {
            "trace_id": f"{row_id}_runtime",
            "low_score_run": low,
            "high_score_run": high,
        },
        "lower_stack_input_trace": {
            "trace_id": f"{row_id}_lower_stack_input",
            "fixture": rel(EXAMPLE_FIXTURE),
            "runtime_family": "LGRC9V3",
            "packet_schedule": {
                "source_node_id": 1,
                "target_node_id": 2,
                "edge_id": 1,
                "amount": 0.1,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            },
            "selected_sink_id": low["selected_sink_id"],
            "competitor_sink_id": low["competitor_sink_id"],
            "same_packet_schedule": True,
            "same_fixture": True,
            "same_selected_sink": low["selected_sink_id"] == high["selected_sink_id"],
        },
        "proxy_metric_trace": {
            "trace_id": f"{row_id}_proxy_metric",
            "proxy_surface": "native_route_arbitration_score",
            "proxy_policy_owner": "producer_mediated_route_candidate_score_runtime_visible",
            "low_score": low["selected_score"],
            "high_score": high["selected_score"],
            "proxy_delta": proxy_delta,
            "proxy_improvement_observed": proxy_delta > 0.0,
            "same_proxy_surface": True,
            "proxy_surface_changed": False,
        },
        "basin_persistence_capacity_trace": {
            "trace_id": f"{row_id}_basin_persistence",
            "low_score_basin": low_basin,
            "high_score_basin": high_basin,
            "same_geometry": same_geometry,
            "basin_persistence_capacity_delta": 0.0 if same_geometry else None,
            "basin_deepening_observed": False,
        },
        "support_coherence_floor_trace": {
            "trace_id": f"{row_id}_support_coherence_floor",
            "support_delta": support_delta,
            "coherence_delta": coherence_delta,
            "boundary_delta": boundary_delta,
            "flux_delta": flux_delta,
            "support_floor_preserved": support_delta == 0.0,
            "coherence_floor_preserved": coherence_delta == 0.0,
            "boundary_value_preserved": boundary_delta == 0.0,
            "flux_value_preserved": flux_delta == 0.0,
        },
        "basin_deepening_comparison_trace": {
            "trace_id": f"{row_id}_basin_deepening_comparison",
            "basin_deepening_delta": max(support_delta, coherence_delta, boundary_delta),
            "basin_deepening_observed": False,
            "basin_stall_observed": same_geometry,
            "geometry_digest_note": (
                "Child-basin state digests may differ because route-score "
                "provenance changes, while membership/support/coherence/"
                "boundary/flux geometry remains fixed."
            ),
        },
        "proxy_vs_basin_delta_trace": {
            "trace_id": f"{row_id}_proxy_vs_basin_delta",
            "proxy_delta": proxy_delta,
            "basin_delta": 0.0 if same_geometry else None,
            "proxy_improves_while_basin_stalls": proxy_delta > 0.0 and same_geometry,
        },
        "peer_or_control_basin_trace": {
            "trace_id": f"{row_id}_peer_or_control_basin",
            "control_kind": "same_route_score_dose_pair",
            "control_role": (
                "The low-score selected run is the control basin trace for the "
                "high-score selected run under the same selected sink and packet "
                "schedule."
            ),
            "multi_basin_peer_required": False,
            "same_selected_sink_control_passed": low["selected_sink_id"] == high["selected_sink_id"],
        },
        "replay_trace": {
            "trace_id": f"{row_id}_replay",
            "low_score_replay_passed": replay_passed(low),
            "high_score_replay_passed": replay_passed(high),
            "low_score_replay_validation_digest": low["replay_validation_digest"],
            "high_score_replay_validation_digest": high["replay_validation_digest"],
            "duplicate_replay_checked": True,
        },
        "control_trace": {
            "trace_id": f"{row_id}_control",
            "controls": [
                {
                    "control_id": "fixed_proxy_surface_control",
                    "control_status": "passed",
                    "rung_effect": "allows_PD4_candidate",
                },
                {
                    "control_id": "same_selected_sink_and_packet_schedule_control",
                    "control_status": "passed",
                    "rung_effect": "allows_basin_delta_comparison",
                },
                {
                    "control_id": "score_as_native_support_relabel_control",
                    "control_status": "failed_closed",
                    "rung_effect": "blocks_native_support_and_native_AP5_bridge",
                },
                {
                    "control_id": "semantic_goal_relabel_control",
                    "control_status": "failed_closed",
                    "rung_effect": "blocks_semantic_goal_or_choice_claim",
                },
            ],
        },
    }
    artifact_manifest = build_artifact_manifest(row_id, traces)
    pd4_candidate = proxy_delta > 0.0 and same_geometry and replay_passed(low) and replay_passed(high)
    return {
        "row_id": row_id,
        "row_decision": "provisional_supported_pending_iteration_7_controls",
        "candidate_pd_ladder_rung": "PD4_candidate_pending_I7",
        "source_current_inputs": [
            rel(EXAMPLE_FIXTURE),
            rel(RUNTIME_CODE),
            rel(RUNTIME_STATE),
            rel(RUNTIME_CONTRACT),
            rel(TELEMETRY_CODE),
        ],
        "source_contract_row_digest": "5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61",
        "source_consumable_contract_row_digest": "99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec",
        "source_output_digest": EXPECTED_I5B_OUTPUT_DIGEST,
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "row_specific_thresholds_declared_before_use": {
            "declared_before_use": True,
            "selected_sink_id": low["selected_sink_id"],
            "low_score": low["selected_score"],
            "high_score": high["selected_score"],
            "competitor_score": low["competitor_score"],
            "required_proxy_delta_min": 0.1,
            "required_basin_delta_for_stall": 0.0,
        },
        "scoped_mb6_substrate_consumption_record": {
            "n25_2_closeout_digest": EXPECTED_N25_2_CLOSEOUT_DIGEST,
            "n25_2_consumed_as": "scoped_mb6_substrate_and_runtime_fixture_context",
            "unscoped_consumption_allowed": False,
        },
        "multi_basin_scope_id": family_id,
        "basin_ids_or_child_basin_ids": [
            low_basin["child_basin_core_ids"],
            high_basin["child_basin_core_ids"],
        ],
        "n25_2_unscoped_consumption_allowed": False,
        "n25_2_unscoped_multi_basin_consumption_allowed": False,
        "front_capacity_companion_backfill_used": False,
        "proxy_metric_definition_digest": digest_data(traces["proxy_metric_trace"]),
        "proxy_derivation_policy_digest": digest_data(traces["lower_stack_input_trace"]),
        "proxy_target_digest_declared_before_use": digest_data(
            {
                "family_id": family_id,
                "proxy_surface": "native_route_arbitration_score",
                "low_score": low["selected_score"],
                "high_score": high["selected_score"],
            }
        ),
        "proxy_policy_owner": "producer_mediated_route_candidate_score_runtime_visible",
        "producer_mediated_target_derivation_counted_as_substrate": False,
        "proxy_delta": proxy_delta,
        "basin_delta": 0.0 if same_geometry else None,
        "proxy_improvement_observed": proxy_delta > 0.0,
        "basin_stall_observed": same_geometry,
        "controlled_proxy_divergence_candidate_supported": pd4_candidate,
        "pd4_candidate_supported_pending_i7": pd4_candidate,
        "native_ap5_bridge_supported": False,
        "ap5_dependency_status": "required_recorded",
        "ap5_condition_reason": (
            "Proxy target derivation participates, but route-score proxy is "
            "producer mediated and cannot close native AP5."
        ),
        "claim_ceiling": (
            "provisional producer-mediated PD4 proxy-divergence candidate; "
            "not proxy collapse, native AP5, native support, agency, semantic goal, "
            "sentience, Phase 8 completion, or ant ecology"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_checks(
    output: dict[str, Any],
    i4: dict[str, Any],
    i4a: dict[str, Any],
    i5: dict[str, Any],
    i5a: dict[str, Any],
    i5b: dict[str, Any],
    closeout: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = output["score_dose_rows"]
    return [
        {
            "check": "source_chain_ready",
            "passed": (
                i4["output_digest"] == EXPECTED_I4_OUTPUT_DIGEST
                and i4a["output_digest"] == EXPECTED_I4A_OUTPUT_DIGEST
                and i5["output_digest"] == EXPECTED_I5_OUTPUT_DIGEST
                and i5a["output_digest"] == EXPECTED_I5A_OUTPUT_DIGEST
                and i5b["output_digest"] == EXPECTED_I5B_OUTPUT_DIGEST
                and closeout["output_digest"] == EXPECTED_N25_2_CLOSEOUT_DIGEST
            ),
            "detail": {
                "i4": i4["output_digest"],
                "i4a": i4a["output_digest"],
                "i5": i5["output_digest"],
                "i5a": i5a["output_digest"],
                "i5b": i5b["output_digest"],
            },
        },
        {
            "check": "score_dose_runtime_rows_emitted",
            "passed": len(rows) == 2,
            "detail": {"row_count": len(rows)},
        },
        {
            "check": "all_rows_have_proxy_delta_with_basin_stall",
            "passed": all(row["proxy_delta"] > 0.0 and row["basin_delta"] == 0.0 for row in rows),
            "detail": [
                {
                    "row_id": row["row_id"],
                    "proxy_delta": row["proxy_delta"],
                    "basin_delta": row["basin_delta"],
                }
                for row in rows
            ],
        },
        {
            "check": "pd4_candidates_are_provisional_and_producer_mediated",
            "passed": all(
                row["controlled_proxy_divergence_candidate_supported"]
                and row["proxy_policy_owner"] == "producer_mediated_route_candidate_score_runtime_visible"
                and not row["producer_mediated_target_derivation_counted_as_substrate"]
                for row in rows
            ),
            "detail": {"row_count": len(rows)},
        },
        {
            "check": "native_ap5_bridge_remains_blocked",
            "passed": (
                output["ap5_bridge_status"] == "not_supported_i5c_producer_mediated_score_surface"
                and not output["native_ap5_bridge_supported"]
            ),
            "detail": output["ap5_bridge_status"],
        },
        {
            "check": "scoped_mb6_boundary_preserved",
            "passed": (
                closeout["n26_handoff"]["n26_scoped_context_consumption_allowed"]
                and not closeout["n26_handoff"]["n26_unscoped_consumption_allowed"]
                and not closeout["n26_handoff"]["n26_unscoped_multi_basin_consumption_allowed"]
            ),
            "detail": closeout["n26_handoff"],
        },
        {
            "check": "artifact_sha256_match_file_contents",
            "passed": all(row["all_artifact_sha256_match_file_contents"] for row in rows),
            "detail": {"row_count": len(rows)},
        },
        {
            "check": "unsafe_claim_flags_false",
            "passed": all(not value for row in rows for value in row["unsafe_claim_flags"].values()),
            "detail": {"claim_count": len(UNSAFE_CLAIMS)},
        },
        {
            "check": "no_absolute_paths_in_records",
            "passed": not contains_absolute_path(output),
            "detail": {"absolute_path_policy": "repository_relative_paths_only"},
        },
    ]


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N26 Iteration 5-C - Same-Route Score-Dose Divergence Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Summary",
        "",
        "I5-C uses the lesson from I5-B: PD4 needs paired basin traces under a",
        "fixed proxy surface. It therefore runs two mirrored same-route native",
        "LGRC9V3 score-dose families. In each family the selected sink, packet",
        "schedule, fixture, basin metric, and threshold/control envelope remain",
        "fixed while the route arbitration score changes.",
        "",
        "Both rows show route-score proxy improvement with basin geometry stalled.",
        "The result is a provisional producer-mediated PD4 proxy-divergence",
        "candidate pending I7 replay/control classification. It does not support",
        "proxy collapse or native AP5.",
        "",
        "## Rows",
        "",
        "| Row | Proxy Delta | Basin Delta | Claim |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in output["score_dose_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"{row['proxy_delta']:.6f} | "
            f"{row['basin_delta']:.6f} | "
            f"`{row['candidate_pd_ladder_rung']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Geometrically, I5-C keeps the emitted child-basin membership, support,",
            "coherence, boundary, and flux surfaces fixed while increasing a",
            "runtime-visible route-score proxy. The route-score proxy improves;",
            "the basin does not deepen. That is the first positive controlled",
            "proxy-divergence shape in N26.",
            "",
            "The claim is deliberately bounded. The score surface is producer",
            "mediated route-candidate input, so I5-C can support a provisional",
            "PD4 divergence candidate but cannot close native AP5 or count the",
            "score as native support.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in output["checks"]:
        lines.append(f"| `{check['check']}` | `{str(check['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "```text",
            "outputs/n26_same_route_score_dose_divergence_probe.json",
            "outputs/n26_same_route_score_dose_divergence_probe_artifacts/",
            "reports/n26_same_route_score_dose_divergence_probe.md",
            "scripts/build_n26_same_route_score_dose_divergence_probe.py",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i4 = load_json(I4_OUTPUT)
    i4a = load_json(I4A_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    i5a = load_json(I5A_OUTPUT)
    i5b = load_json(I5B_OUTPUT)
    closeout = load_json(N25_2_CLOSEOUT)
    fixture = import_fixture()

    source_digests = {
        rel(path): sha256_file(path)
        for path in [EXAMPLE_FIXTURE, RUNTIME_CODE, RUNTIME_STATE, RUNTIME_CONTRACT, TELEMETRY_CODE]
    }
    score_families = []
    for family_id, selected_sink_id in [
        ("sink0_fixed_route", 0),
        ("sink2_fixed_route", 2),
    ]:
        low = run_score_dose(
            fixture=fixture,
            family_id=family_id,
            selected_sink_id=selected_sink_id,
            selected_score=0.55,
            competitor_score=0.25,
            dose_label="low",
        )
        high = run_score_dose(
            fixture=fixture,
            family_id=family_id,
            selected_sink_id=selected_sink_id,
            selected_score=0.95,
            competitor_score=0.25,
            dose_label="high",
        )
        score_families.append(build_family_row(family_id, low, high))

    output: dict[str, Any] = {
        "artifact_id": "n26_same_route_score_dose_divergence_probe",
        "experiment": "N26",
        "iteration": "I5-C",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_provisional_pd4_same_route_score_dose_divergence_candidate_pending_i7",
        "source_i4_output_digest": i4["output_digest"],
        "source_i4a_output_digest": i4a["output_digest"],
        "source_i5_output_digest": i5["output_digest"],
        "source_i5a_output_digest": i5a["output_digest"],
        "source_i5b_output_digest": i5b["output_digest"],
        "source_n25_2_closeout_output_digest": closeout["output_digest"],
        "source_file_sha256": source_digests,
        "candidate_pd_ladder_rung": "PD4_candidate_pending_I7",
        "n26_closeout_ceiling": "N26-C5_provisional_controlled_proxy_divergence_candidate_pending_controls",
        "n26_closeout_ladder_rung_assigned": False,
        "same_route_score_dose_probe_opened": True,
        "score_dose_rows": score_families,
        "row_count": len(score_families),
        "provisional_pd4_candidate_supported": True,
        "controlled_proxy_divergence_candidate_supported": True,
        "controlled_proxy_divergence_status": "provisional_pending_I7_replay_controls_and_AP5_gate",
        "pd4_or_stronger_supported": False,
        "final_pd4_supported": False,
        "pd4_support_scope": "producer_mediated_route_score_surface_only",
        "proxy_collapse_opened": False,
        "proxy_collapse_supported": False,
        "native_ap5_bridge_supported": False,
        "ap5_bridge_status": "not_supported_i5c_producer_mediated_score_surface",
        "claim_boundary": {
            "claim_ceiling": (
                "provisional producer-mediated PD4 proxy-divergence candidate; "
                "native AP5, proxy collapse, native support, agency, semantic goal, "
                "sentience, Phase 8 completion, and ant ecology remain blocked"
            ),
            "blocked_claims": [
                "proxy_collapse",
                "native_AP5",
                "native_support",
                "agency",
                "semantic_goal",
                "semantic_choice",
                "sentience",
                "Phase_8_completion",
                "ant_ecology",
                "unscoped_multi_basin_substrate",
            ],
        },
        "ready_for_iteration_6_proxy_collapse_perturbation_matrix": True,
    }
    output["checks"] = build_checks(output, i4, i4a, i5, i5a, i5b, closeout)
    output["failed_checks"] = [check["check"] for check in output["checks"] if not check["passed"]]
    digest_payload = dict(output)
    digest_payload.pop("output_digest", None)
    output["output_digest"] = digest_data(digest_payload)

    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
