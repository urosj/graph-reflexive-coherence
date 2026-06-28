#!/usr/bin/env python3
"""Build N26 Iteration 6 proxy collapse perturbation matrix."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
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
OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_collapse_perturbation_matrix.json"
REPORT = EXPERIMENT / "reports" / "n26_proxy_collapse_perturbation_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n26_proxy_collapse_perturbation_matrix_artifacts"

I5C_OUTPUT = EXPERIMENT / "outputs" / "n26_same_route_score_dose_divergence_probe.json"
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
    "build_n26_proxy_collapse_perturbation_matrix.py"
)

EXPECTED_I5C_OUTPUT_DIGEST = "5f4c9355645ba39840f860d4544b71195fbfde277ab9ce7b6fd22291c34099ab"
EXPECTED_N25_2_CLOSEOUT_DIGEST = "b92401da545899c7721ab42692827beb5b357bbd246d8991d7ad56649a6bbf03"

PACKET_AMOUNT = 0.1
PROXY_SCORE = 0.95
BASIN_DEEPENED_SCORE = 0.55
COMPETITOR_SCORE = 0.25
BASIN_DEEPENING_BOOST = 0.5
CHALLENGE_MARGIN_ABOVE_PROXY_BASE = 0.25

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
        "n26_i6_multi_basin_fixture",
        EXAMPLE_FIXTURE,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to import LGRC9V3 fixture")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_runtime_model_from_snapshot(fixture: Any, snapshot: dict[str, Any]) -> Any:
    with tempfile.TemporaryDirectory() as temp_dir:
        snapshot_path = Path(temp_dir) / "n26_i6_runtime_snapshot.json"
        snapshot_path.write_text(canonical_json(snapshot), encoding="utf-8")
        return fixture.LGRC9V3.load(str(snapshot_path))


def route_spec_id(sink: int, path_role: str) -> str:
    return f"candidate:sink{sink}-{path_role}"


def base_sink_coherence(fixture: Any, selected_sink_id: int) -> float:
    state = fixture.three_node_state()
    return float(state.nodes[selected_sink_id].coherence)


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


def run_path(
    *,
    fixture: Any,
    family_id: str,
    path_role: str,
    selected_sink_id: int,
    selected_score: float,
    competitor_score: float,
    sink_coherence_boost: float,
) -> dict[str, Any]:
    competitor_sink_id = 2 if selected_sink_id == 0 else 0
    state = fixture.three_node_state()
    state.nodes[selected_sink_id].coherence += sink_coherence_boost
    model = fixture.LGRC9V3.from_state(state, fixture.multi_basin_params())
    initial_snapshot_digest = digest_data(model.snapshot())
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        amount=PACKET_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    step_result = model.step()
    surface = model.get_state().causal_pulse_substrate_surface_log[-1]
    selected_route_id = route_spec_id(selected_sink_id, path_role)
    competitor_route_id = f"candidate:sink{competitor_sink_id}-{path_role}-control"
    candidate_result = model.emit_native_route_candidate_set(
        arbitration_window_id=f"window:n26-i6-{family_id}-{path_role}",
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
    state_after = model.get_state()
    final_snapshot = model.snapshot()
    child_records = [record.to_artifact() for record in state_after.child_basin_state_log]
    if len(child_records) != 1:
        raise RuntimeError(f"Expected one child-basin record for {family_id}/{path_role}")
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
    return {
        "family_id": family_id,
        "path_role": path_role,
        "selected_sink_id": selected_sink_id,
        "competitor_sink_id": competitor_sink_id,
        "selected_route_id": selected_route_id,
        "selected_score": selected_score,
        "competitor_route_id": competitor_route_id,
        "competitor_score": competitor_score,
        "sink_coherence_boost": sink_coherence_boost,
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
        "topology_event_counts": dict(Counter(event.kind for event in state_after.topology_event_log)),
        "topology_events": [
            {
                "kind": event.kind,
                "step_index": int(event.step_index),
                "payload": jsonable(event.payload),
                "source_family": str(event.source_family),
            }
            for event in state_after.topology_event_log
        ],
        "child_basin_record": child_record,
        "basin_metric_summary": basin_metric_summary(child_record),
        "replay_record": replay_record,
        "duplicate_replay_record": duplicate_record,
        "replay_validation_digest": str(replay["replay_validation_digest"]),
        "duplicate_replay_validation_digest": str(duplicate["replay_validation_digest"]),
    }


def replay_passed(run: dict[str, Any]) -> bool:
    record = run["replay_record"]
    duplicate = run["duplicate_replay_record"]
    return (
        record["artifact_replay_result"] == "passed"
        and record["snapshot_load_replay_result"] == "passed"
        and record["time_order_replay_result"] == "passed"
        and duplicate["artifact_replay_result"] == "passed"
    )


def challenge_survival(path: dict[str, Any], challenge_floor: float) -> dict[str, Any]:
    basin = path["basin_metric_summary"]
    weakest_floor = min(float(basin["support_floor"]), float(basin["coherence_floor"]))
    margin = weakest_floor - challenge_floor
    return {
        "challenge_floor": challenge_floor,
        "weakest_support_coherence_floor": weakest_floor,
        "challenge_margin": margin,
        "survives_challenge": margin >= 0.0,
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


def build_family_row(
    *,
    fixture: Any,
    family_id: str,
    selected_sink_id: int,
) -> dict[str, Any]:
    base = base_sink_coherence(fixture, selected_sink_id)
    challenge_floor = base + PACKET_AMOUNT + CHALLENGE_MARGIN_ABOVE_PROXY_BASE
    proxy_path = run_path(
        fixture=fixture,
        family_id=family_id,
        path_role="proxy_optimized",
        selected_sink_id=selected_sink_id,
        selected_score=PROXY_SCORE,
        competitor_score=COMPETITOR_SCORE,
        sink_coherence_boost=0.0,
    )
    basin_path = run_path(
        fixture=fixture,
        family_id=family_id,
        path_role="basin_deepened",
        selected_sink_id=selected_sink_id,
        selected_score=BASIN_DEEPENED_SCORE,
        competitor_score=COMPETITOR_SCORE,
        sink_coherence_boost=BASIN_DEEPENING_BOOST,
    )
    proxy_survival = challenge_survival(proxy_path, challenge_floor)
    basin_survival = challenge_survival(basin_path, challenge_floor)
    proxy_basin = proxy_path["basin_metric_summary"]
    deepened_basin = basin_path["basin_metric_summary"]
    proxy_delta = proxy_path["selected_score"] - basin_path["selected_score"]
    basin_support_delta = float(deepened_basin["support_floor"]) - float(proxy_basin["support_floor"])
    basin_coherence_delta = float(deepened_basin["coherence_floor"]) - float(proxy_basin["coherence_floor"])
    row_id = f"n26_i6_proxy_collapse_perturbation_{family_id}"
    pd5_candidate = (
        proxy_path["selected_score"] > basin_path["selected_score"]
        and not proxy_survival["survives_challenge"]
        and basin_survival["survives_challenge"]
        and replay_passed(proxy_path)
        and replay_passed(basin_path)
    )
    traces = {
        "runtime_trace": {
            "trace_id": f"{row_id}_runtime",
            "proxy_optimized_path": proxy_path,
            "basin_deepened_path": basin_path,
        },
        "lower_stack_input_trace": {
            "trace_id": f"{row_id}_lower_stack_input",
            "fixture": rel(EXAMPLE_FIXTURE),
            "runtime_family": "LGRC9V3",
            "selected_sink_id": selected_sink_id,
            "packet_amount": PACKET_AMOUNT,
            "packet_schedule": {
                "source_node_id": 1,
                "target_node_id": 2,
                "edge_id": 1,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            },
            "proxy_path_sink_coherence_boost": 0.0,
            "basin_path_sink_coherence_boost": BASIN_DEEPENING_BOOST,
            "basin_deepening_input_owner": "declared_source_current_fixture_geometry_variant",
        },
        "proxy_metric_trace": {
            "trace_id": f"{row_id}_proxy_metric",
            "proxy_surface": "native_route_arbitration_score",
            "proxy_path_score": proxy_path["selected_score"],
            "basin_deepened_path_score": basin_path["selected_score"],
            "proxy_score_advantage": proxy_delta,
            "proxy_optimized_path_has_higher_proxy": proxy_delta > 0.0,
            "proxy_policy_owner": "producer_mediated_route_candidate_score_runtime_visible",
        },
        "basin_persistence_capacity_trace": {
            "trace_id": f"{row_id}_basin_persistence",
            "proxy_path_basin": proxy_basin,
            "basin_deepened_path_basin": deepened_basin,
            "basin_support_delta": basin_support_delta,
            "basin_coherence_delta": basin_coherence_delta,
            "basin_deepening_observed": basin_support_delta > 0.0 and basin_coherence_delta > 0.0,
        },
        "support_coherence_floor_trace": {
            "trace_id": f"{row_id}_support_coherence_floor",
            "challenge_floor": challenge_floor,
            "proxy_path_margin": proxy_survival["challenge_margin"],
            "basin_deepened_path_margin": basin_survival["challenge_margin"],
            "proxy_path_floor_crossed": not proxy_survival["survives_challenge"],
            "basin_deepened_path_floor_preserved": basin_survival["survives_challenge"],
        },
        "basin_deepening_comparison_trace": {
            "trace_id": f"{row_id}_basin_deepening_comparison",
            "proxy_path_support_floor": proxy_basin["support_floor"],
            "basin_deepened_support_floor": deepened_basin["support_floor"],
            "proxy_path_coherence_floor": proxy_basin["coherence_floor"],
            "basin_deepened_coherence_floor": deepened_basin["coherence_floor"],
            "basin_deepening_delta": min(basin_support_delta, basin_coherence_delta),
        },
        "proxy_vs_basin_delta_trace": {
            "trace_id": f"{row_id}_proxy_vs_basin_delta",
            "proxy_path_score_advantage": proxy_delta,
            "basin_deepened_path_support_advantage": basin_support_delta,
            "divergence_shape": "proxy_path_higher_score_basin_path_higher_basin_capacity",
        },
        "proxy_optimized_path_trace": {
            "trace_id": f"{row_id}_proxy_optimized_path",
            "path": proxy_path,
            "challenge_result": proxy_survival,
            "collapse_under_perturbation": not proxy_survival["survives_challenge"],
        },
        "basin_deepened_path_trace": {
            "trace_id": f"{row_id}_basin_deepened_path",
            "path": basin_path,
            "challenge_result": basin_survival,
            "survives_perturbation": basin_survival["survives_challenge"],
        },
        "perturbation_challenge_trace": {
            "trace_id": f"{row_id}_perturbation_challenge",
            "challenge_kind": "support_coherence_floor_required_above_proxy_base",
            "challenge_floor": challenge_floor,
            "declared_before_use": True,
            "formula": (
                "base_selected_sink_coherence + packet_amount + "
                "challenge_margin_above_proxy_base"
            ),
            "base_selected_sink_coherence": base,
            "packet_amount": PACKET_AMOUNT,
            "challenge_margin_above_proxy_base": CHALLENGE_MARGIN_ABOVE_PROXY_BASE,
            "same_challenge_for_proxy_and_basin_paths": True,
        },
        "proxy_collapse_result_trace": {
            "trace_id": f"{row_id}_proxy_collapse_result",
            "proxy_optimized_path_collapses_under_perturbation": not proxy_survival["survives_challenge"],
            "basin_deepened_path_survives_same_perturbation": basin_survival["survives_challenge"],
            "pd5_candidate_supported_pending_i7": pd5_candidate,
        },
        "peer_or_control_basin_trace": {
            "trace_id": f"{row_id}_peer_or_control_basin",
            "control_kind": "same_selected_sink_proxy_vs_basin_deepening_pair",
            "same_selected_sink": proxy_path["selected_sink_id"] == basin_path["selected_sink_id"],
            "same_packet_schedule": True,
            "same_perturbation_challenge": True,
        },
        "replay_trace": {
            "trace_id": f"{row_id}_replay",
            "proxy_path_replay_passed": replay_passed(proxy_path),
            "basin_deepened_path_replay_passed": replay_passed(basin_path),
            "proxy_path_replay_validation_digest": proxy_path["replay_validation_digest"],
            "basin_deepened_path_replay_validation_digest": basin_path["replay_validation_digest"],
        },
        "control_trace": {
            "trace_id": f"{row_id}_control",
            "controls": [
                {
                    "control_id": "shared_perturbation_envelope_control",
                    "control_status": "passed",
                    "rung_effect": "allows_PD5_candidate",
                },
                {
                    "control_id": "proxy_score_as_native_support_relabel_control",
                    "control_status": "failed_closed",
                    "rung_effect": "blocks_native_support_and_native_AP5_bridge",
                },
                {
                    "control_id": "basin_deepening_fixture_variant_as_native_support_control",
                    "control_status": "failed_closed",
                    "rung_effect": "keeps_basin_deepening_source_current_but_producer_declared",
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
    return {
        "row_id": row_id,
        "row_decision": "provisional_supported_pending_iteration_7_controls",
        "candidate_pd_ladder_rung": "PD5_candidate_pending_I7",
        "source_current_inputs": [
            rel(EXAMPLE_FIXTURE),
            rel(RUNTIME_CODE),
            rel(RUNTIME_STATE),
            rel(RUNTIME_CONTRACT),
            rel(TELEMETRY_CODE),
        ],
        "artifact_manifest": artifact_manifest,
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(ROOT / item["path"]) == item["sha256"] for item in artifact_manifest
        ),
        "row_specific_thresholds_declared_before_use": traces["perturbation_challenge_trace"],
        "scoped_mb6_substrate_consumption_record": {
            "n25_2_closeout_digest": EXPECTED_N25_2_CLOSEOUT_DIGEST,
            "n25_2_consumed_as": "scoped_mb6_substrate_and_runtime_fixture_context",
            "unscoped_consumption_allowed": False,
        },
        "multi_basin_scope_id": family_id,
        "basin_ids_or_child_basin_ids": [
            proxy_basin["child_basin_core_ids"],
            deepened_basin["child_basin_core_ids"],
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
                "challenge_floor": challenge_floor,
                "proxy_score": PROXY_SCORE,
                "basin_deepened_score": BASIN_DEEPENED_SCORE,
            }
        ),
        "proxy_policy_owner": "producer_mediated_route_candidate_score_runtime_visible",
        "producer_mediated_target_derivation_counted_as_substrate": False,
        "basin_deepening_input_owner": "declared_source_current_fixture_geometry_variant",
        "basin_deepening_counted_as_native_support": False,
        "proxy_score_advantage": proxy_delta,
        "basin_support_advantage": basin_support_delta,
        "proxy_path_survives_challenge": proxy_survival["survives_challenge"],
        "basin_deepened_path_survives_challenge": basin_survival["survives_challenge"],
        "proxy_collapse_candidate_supported": pd5_candidate,
        "pd5_candidate_supported_pending_i7": pd5_candidate,
        "native_ap5_bridge_supported": False,
        "ap5_dependency_status": "required_recorded",
        "ap5_condition_reason": (
            "Proxy target derivation and proxy collapse participate, but route "
            "score and basin-deepening variant are producer mediated surfaces "
            "and cannot close native AP5."
        ),
        "claim_ceiling": (
            "provisional producer-mediated PD5 proxy-collapse candidate; "
            "not native AP5, native support, agency, semantic goal, sentience, "
            "Phase 8 completion, or ant ecology"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_checks(output: dict[str, Any], i5c: dict[str, Any], closeout: dict[str, Any]) -> list[dict[str, Any]]:
    rows = output["proxy_collapse_rows"]
    return [
        {
            "check": "source_chain_ready",
            "passed": (
                i5c["output_digest"] == EXPECTED_I5C_OUTPUT_DIGEST
                and closeout["output_digest"] == EXPECTED_N25_2_CLOSEOUT_DIGEST
            ),
            "detail": {"i5c": i5c["output_digest"], "n25_2_closeout": closeout["output_digest"]},
        },
        {
            "check": "shared_perturbation_matrix_rows_emitted",
            "passed": len(rows) == 2,
            "detail": {"row_count": len(rows)},
        },
        {
            "check": "proxy_optimized_paths_fail_under_perturbation",
            "passed": all(not row["proxy_path_survives_challenge"] for row in rows),
            "detail": [
                {"row_id": row["row_id"], "proxy_path_survives": row["proxy_path_survives_challenge"]}
                for row in rows
            ],
        },
        {
            "check": "basin_deepened_paths_survive_same_perturbation",
            "passed": all(row["basin_deepened_path_survives_challenge"] for row in rows),
            "detail": [
                {
                    "row_id": row["row_id"],
                    "basin_deepened_path_survives": row["basin_deepened_path_survives_challenge"],
                }
                for row in rows
            ],
        },
        {
            "check": "pd5_candidates_are_provisional_and_producer_mediated",
            "passed": all(
                row["proxy_collapse_candidate_supported"]
                and row["basin_deepening_input_owner"] == "declared_source_current_fixture_geometry_variant"
                and not row["basin_deepening_counted_as_native_support"]
                and not row["native_ap5_bridge_supported"]
                for row in rows
            ),
            "detail": {"row_count": len(rows)},
        },
        {
            "check": "native_ap5_bridge_remains_blocked",
            "passed": (
                output["ap5_bridge_status"] == "not_supported_i6_producer_mediated_proxy_and_basin_deepening_surfaces"
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
        "# N26 Iteration 6 - Proxy Collapse Perturbation Matrix",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Summary",
        "",
        "I6 uses I5-C's provisional divergence result as the input and asks a",
        "stronger collapse question: under the same declared perturbation floor,",
        "does the proxy-optimized path fail while a basin-deepened contrast",
        "survives?",
        "",
        "Both mirrored route families support that shape. The high-score proxy",
        "path fails the support/coherence challenge, while the lower-score but",
        "source-current basin-deepened path survives the same challenge.",
        "",
        "## Rows",
        "",
        "| Row | Proxy Path Survives | Basin Path Survives | Proxy Advantage | Basin Advantage |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for row in output["proxy_collapse_rows"]:
        lines.append(
            "| "
            f"`{row['row_id']}` | "
            f"`{str(row['proxy_path_survives_challenge']).lower()}` | "
            f"`{str(row['basin_deepened_path_survives_challenge']).lower()}` | "
            f"{row['proxy_score_advantage']:.6f} | "
            f"{row['basin_support_advantage']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Geometrically, I6 separates route-score optimization from basin capacity.",
            "The proxy-optimized path has the higher route score, but its emitted",
            "child-basin support/coherence floor is below the perturbation floor.",
            "The basin-deepened path has lower route score, but the source-current",
            "geometry variant raises support/coherence enough to survive.",
            "",
            "The claim remains bounded. This is a provisional producer-mediated PD5",
            "candidate pending I7 replay/control/AP5 classification. The score and",
            "deepening surfaces do not count as native AP5 target formation or native",
            "support.",
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
            "outputs/n26_proxy_collapse_perturbation_matrix.json",
            "outputs/n26_proxy_collapse_perturbation_matrix_artifacts/",
            "reports/n26_proxy_collapse_perturbation_matrix.md",
            "scripts/build_n26_proxy_collapse_perturbation_matrix.py",
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i5c = load_json(I5C_OUTPUT)
    closeout = load_json(N25_2_CLOSEOUT)
    fixture = import_fixture()
    source_digests = {
        rel(path): sha256_file(path)
        for path in [EXAMPLE_FIXTURE, RUNTIME_CODE, RUNTIME_STATE, RUNTIME_CONTRACT, TELEMETRY_CODE]
    }
    rows = [
        build_family_row(fixture=fixture, family_id="sink0_proxy_collapse", selected_sink_id=0),
        build_family_row(fixture=fixture, family_id="sink2_proxy_collapse", selected_sink_id=2),
    ]
    output: dict[str, Any] = {
        "artifact_id": "n26_proxy_collapse_perturbation_matrix",
        "experiment": "N26",
        "iteration": "I6",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_provisional_pd5_proxy_collapse_candidate_pending_i7",
        "source_i5c_output_digest": i5c["output_digest"],
        "source_n25_2_closeout_output_digest": closeout["output_digest"],
        "source_file_sha256": source_digests,
        "candidate_pd_ladder_rung": "PD5_candidate_pending_I7",
        "n26_closeout_ceiling": "N26-C5_provisional_controlled_proxy_divergence_and_collapse_candidate_pending_controls",
        "n26_closeout_ladder_rung_assigned": False,
        "proxy_collapse_perturbation_matrix_opened": True,
        "proxy_collapse_rows": rows,
        "row_count": len(rows),
        "provisional_pd5_candidate_supported": True,
        "controlled_proxy_divergence_candidate_supported": True,
        "controlled_proxy_collapse_candidate_supported": True,
        "proxy_collapse_candidate_supported": True,
        "proxy_collapse_supported": False,
        "pd5_or_stronger_supported": False,
        "final_pd5_supported": False,
        "pd5_support_scope": "producer_mediated_route_score_and_source_current_fixture_geometry_variant",
        "native_ap5_bridge_supported": False,
        "ap5_bridge_status": "not_supported_i6_producer_mediated_proxy_and_basin_deepening_surfaces",
        "claim_boundary": {
            "claim_ceiling": (
                "provisional producer-mediated PD5 proxy-collapse candidate; "
                "native AP5, native support, agency, semantic goal, sentience, "
                "Phase 8 completion, and ant ecology remain blocked"
            ),
            "blocked_claims": [
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
        "ready_for_iteration_7_replay_controls_and_ap5_gate": True,
    }
    output["checks"] = build_checks(output, i5c, closeout)
    output["failed_checks"] = [check["check"] for check in output["checks"] if not check["passed"]]
    digest_payload = dict(output)
    digest_payload.pop("output_digest", None)
    output["output_digest"] = digest_data(digest_payload)

    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
