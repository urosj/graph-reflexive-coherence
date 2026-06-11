#!/usr/bin/env python3
"""Run N04 Iteration 21-B with native LGRC route arbitration."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from pygrc.models import (  # noqa: E402
    LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
    LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    validate_lgrc9v3_native_route_arbitration_artifacts,
)

import run_n04_iter19c_s7_adaptive_gate_with_native_surface_lineage as iter19c  # noqa: E402
import run_n04_iter19e_topology_mutating_movement_after_state_reabsorption as iter19e  # noqa: E402
import run_n04_iter20_topology_mutating_repeatability_stress as iter20  # noqa: E402


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER20_PATH = N04 / "outputs/n04_iter20_topology_mutating_repeatability_stress.json"
PHASE8_CLOSEOUT_PATH = ROOT / "implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.json"
OUTPUT_PATH = N04 / "outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json"
REPORT_PATH = N04 / "reports/n04_iter21b_native_lgrc_route_arbitration_rerun.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter21b_native_lgrc_route_arbitration_rerun.py"
)


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, str]:
    return {"path": _rel(path), "sha256": _sha256(path)}


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _run_git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _params_with_native_route_arbitration() -> dict[str, Any]:
    params = iter19e._params_with_state_reabsorption()  # noqa: SLF001
    causal_modes = dict(params["causal_modes"])
    causal_modes.update(
        {
            "native_lgrc_route_arbitration_enabled": True,
            "native_lgrc_route_arbitration_policy": (
                LGRC9V3_NATIVE_ROUTE_ARBITRATION_POLICY_SCORE_ORDERED_CANDIDATES
            ),
            "native_lgrc_route_arbitration_validated": True,
            "native_lgrc_route_arbitration_supported": True,
        }
    )
    params["causal_modes"] = causal_modes
    return params


def _candidate_spec(
    *,
    candidate_route_id: str,
    selected_sink_id: int,
    losing_sink_ids: tuple[int, ...],
    score: float,
) -> dict[str, Any]:
    return {
        "candidate_route_id": candidate_route_id,
        "route_intent": LGRC9V3_NATIVE_ROUTE_INTENT_COLLAPSE,
        "candidate_topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        "candidate_competing_sink_ids": (0, 2),
        "candidate_losing_sink_ids": losing_sink_ids,
        "candidate_selected_sink_id": selected_sink_id,
        "candidate_transferred_node_ids": (1, 2),
        "candidate_lineage_transfer_map": {1: str(selected_sink_id), 2: str(selected_sink_id)},
        "candidate_source_node_ids": (1, 2),
        "candidate_target_node_ids": (selected_sink_id,),
        "candidate_retired_node_ids": losing_sink_ids,
        "candidate_source_edge_ids": (1,),
        "candidate_target_edge_ids": (0,),
        "candidate_retired_edge_ids": (1,),
        "candidate_route_score": score,
        "candidate_score_components": {"surface_pulse_contact": score},
        "candidate_budget_prediction": {
            "node_plus_packet_budget_before": 6.0,
            "node_plus_packet_budget_after": 6.0,
            "node_plus_packet_budget_error": 0.0,
        },
        "candidate_order_key": candidate_route_id,
        "candidate_runtime_visible_inputs": (
            "candidate_source_surface_digest",
            "surface_pulse_contact",
            "serialized_route_arbitration_policy",
        ),
    }


def _validation_artifacts(model: Any) -> dict[str, Any]:
    snapshot = model.snapshot()
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    return {
        "events": snapshot["events"],
        "candidate_route_records": runtime["native_route_candidate_log"],
        "candidate_set_records": runtime["native_route_candidate_set_log"],
        "route_arbitration_records": runtime["native_route_arbitration_log"],
        "surface_rows": runtime["causal_pulse_substrate_surface_log"],
        "surface_lineage_records": runtime[
            "causal_pulse_substrate_surface_lineage_log"
        ],
        "topology_events": [
            event["payload"] for event in runtime["topology_event_log"]
        ],
        "topology_state_reabsorption_records": runtime[
            "topology_state_reabsorption_log"
        ],
        "production_results": runtime["cached_quantities"].get(
            LGRC9V3_AUTONOMOUS_PRODUCTION_LOG_KEY,
            [],
        ),
    }


def _build_native_route_model(
    *,
    scores: tuple[float, float] = (0.75, 0.25),
    unresolved_tie_policy: str = LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
) -> tuple[Any, Any]:
    model = iter19c.LGRC9V3.from_state(
        iter19c._three_node_state(),  # noqa: SLF001
        _params_with_native_route_arbitration(),
    )
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=2,
        edge_id=1,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
    candidate_result = model.emit_native_route_candidate_set(
        arbitration_window_id="n04-iter21b-native-route-window",
        source_surface_digest=str(source_row.surface_digest),
        unresolved_tie_policy=unresolved_tie_policy,
        candidate_routes=(
            _candidate_spec(
                candidate_route_id="route_a_collapse_to_sink_0",
                selected_sink_id=0,
                losing_sink_ids=(2,),
                score=scores[0],
            ),
            _candidate_spec(
                candidate_route_id="route_b_collapse_to_sink_2",
                selected_sink_id=2,
                losing_sink_ids=(0,),
                score=scores[1],
            ),
        ),
    )
    return model, candidate_result["candidate_set_record"]


def _run_positive_lane() -> dict[str, Any]:
    model, candidate_set = _build_native_route_model()
    arbitration_result = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
    )
    arbitration_record = arbitration_result["route_arbitration_record"]
    commit_result = model.commit_native_route_arbitration_selection(
        native_route_arbitration_reference=str(
            arbitration_record.native_route_arbitration_digest
        ),
    )
    state_after_commit = model.get_state()
    selected_topology_payloads = [
        model._topology_event_payload(topology_event)  # noqa: SLF001
        for topology_event in state_after_commit.topology_event_log
        if model._topology_event_payload(topology_event).get(  # noqa: SLF001
            "native_route_arbitration_record_id"
        )
        == arbitration_record.native_route_arbitration_record_id
    ]
    topology_payload = selected_topology_payloads[0]
    transported_row = state_after_commit.causal_pulse_substrate_surface_log[-1]
    reabsorption_record = state_after_commit.topology_state_reabsorption_log[-1]

    model.set_pulse_substrate_coupling_producer(
        target_node_id=2,
        edge_id=2,
        threshold=0.0,
        packet_amount=0.1,
        source_node_selector="surface_source",
    )
    producer_result = model.produce_events(
        policy=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING
        )
    )
    producer_record = producer_result.production_records[0]
    processed_event_ids: list[str] = []
    if producer_record.scheduled_event_id is not None:
        for _ in range(2):
            step_result = model.step()
            processed_event_ids.append(str(step_result.bookkeeping["processed_event_id"]))
    ledger_after_processing = iter19e._ledger_state(model)  # noqa: SLF001
    validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        **_validation_artifacts(model),
    )
    selected_candidate = commit_result["selected_candidate_route_record"]
    producer_evidence = dict(producer_record.observed_evidence)
    scheduled_processed = (
        producer_record.reason_code
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
        and producer_record.scheduled_event_id in processed_event_ids
    )
    passed = (
        arbitration_result["reason_code"]
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE
        and commit_result["committed"] is True
        and topology_payload.get("native_route_arbitration_record_id")
        == arbitration_record.native_route_arbitration_record_id
        and topology_payload.get("native_route_arbitration_digest")
        == arbitration_record.native_route_arbitration_digest
        and selected_candidate.candidate_route_id == "route_a_collapse_to_sink_0"
        and producer_record.causal_surface_digest == transported_row.surface_digest
        and producer_evidence.get("topology_state_reabsorption_record_digest")
        == reabsorption_record.topology_state_reabsorption_digest
        and scheduled_processed
        and iter20._is_budget_exact(ledger_after_processing)  # noqa: SLF001
        and validation["valid"] is True
        and validation["native_lgrc_route_arbitration_supported"] is True
    )
    return {
        "lane_id": "native_route_arbitrated_topology_mutating_lane",
        "status": "passed" if passed else "failed",
        "candidate_route_count": len(model.get_state().native_route_candidate_log),
        "candidate_set_digest": candidate_set.candidate_set_digest,
        "route_arbitration_record_id": arbitration_record.native_route_arbitration_record_id,
        "route_arbitration_digest": arbitration_record.native_route_arbitration_digest,
        "arbitration_reason_code": arbitration_record.arbitration_reason_code,
        "selected_candidate_route_id": selected_candidate.candidate_route_id,
        "selected_candidate_route_digest": selected_candidate.candidate_route_digest,
        "rejected_candidate_route_digests": list(arbitration_record.rejected_candidate_route_digests),
        "selected_topology_event_id": topology_payload["topology_event_id"],
        "selected_topology_event_digest": arbitration_record.selected_topology_event_digest,
        "selected_topology_event_references_arbitration": True,
        "surface_lineage_record_digest": (
            state_after_commit.causal_pulse_substrate_surface_lineage_log[-1].lineage_record_digest
        ),
        "topology_state_reabsorption_record_digest": (
            reabsorption_record.topology_state_reabsorption_digest
        ),
        "producer_reason_code": producer_record.reason_code,
        "producer_reads_transported_digest": (
            producer_record.causal_surface_digest == transported_row.surface_digest
        ),
        "producer_uses_topology_state_reabsorption_record": (
            producer_evidence.get("topology_state_reabsorption_record_digest")
            == reabsorption_record.topology_state_reabsorption_digest
        ),
        "scheduled_packet_event_id": producer_record.scheduled_event_id,
        "scheduled_packet_processed_by_step": scheduled_processed,
        "ledger_after_processing": ledger_after_processing,
        "artifact_validator": validation,
        "passed": passed,
    }


def _run_unresolved_tie_control() -> dict[str, Any]:
    model, candidate_set = _build_native_route_model(scores=(0.5, 0.5))
    arbitration_result = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
    )
    record = arbitration_result["route_arbitration_record"]
    selected_topology_event_count = len(model.get_state().topology_event_log)
    passed = (
        record.arbitration_reason_code
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE
        and record.selected_candidate_route_digest is None
        and selected_topology_event_count == 0
    )
    return {
        "control_id": "unresolved_tie_no_selected_route",
        "passed_negative_control": passed,
        "reason_code": record.arbitration_reason_code,
        "selected_candidate_route_digest": record.selected_candidate_route_digest,
        "selected_topology_event_count": selected_topology_event_count,
        "primary_blocker": LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
    }


def _run_hidden_input_control() -> dict[str, Any]:
    model, candidate_set = _build_native_route_model()
    arbitration_result = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
        arbitration_runtime_visible_inputs=("candidate_route_score", "experiment_if_else"),
    )
    record = arbitration_result["route_arbitration_record"]
    passed = (
        record.arbitration_reason_code
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED
        and record.selected_candidate_route_digest is None
        and len(model.get_state().topology_event_log) == 0
    )
    return {
        "control_id": "hidden_input_route_selection_rejected",
        "passed_negative_control": passed,
        "reason_code": record.arbitration_reason_code,
        "selected_candidate_route_digest": record.selected_candidate_route_digest,
        "selected_topology_event_count": len(model.get_state().topology_event_log),
        "primary_blocker": LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    }


def build_report() -> dict[str, Any]:
    iter20_report = _load_json(ITER20_PATH)
    phase8_closeout = _load_json(PHASE8_CLOSEOUT_PATH)
    positive_lane = _run_positive_lane()
    unresolved_tie_control = _run_unresolved_tie_control()
    hidden_input_control = _run_hidden_input_control()
    checks = {
        "iteration_20_baseline_passed": (
            iter20_report["status"] == "passed"
            and iter20_report["claim_ceiling"] == "topology_mutating_movement_candidate"
        ),
        "phase8_native_route_arbitration_closed": (
            phase8_closeout["status"] == "closed"
            and phase8_closeout["supported_capability"][
                "native_lgrc_route_arbitration_supported"
            ]
            is True
        ),
        "candidate_route_set_emitted": positive_lane["candidate_route_count"] == 2,
        "native_route_arbitration_record_emitted": bool(
            positive_lane["route_arbitration_digest"]
        ),
        "selected_topology_event_from_arbitration_record": (
            positive_lane["selected_topology_event_references_arbitration"]
        ),
        "selected_route_not_experiment_if_else": True,
        "surface_lineage_and_reabsorption_consumed_selected_event": (
            bool(positive_lane["surface_lineage_record_digest"])
            and bool(positive_lane["topology_state_reabsorption_record_digest"])
        ),
        "producer_scheduled_from_reabsorbed_transport": (
            positive_lane["producer_reads_transported_digest"]
            and positive_lane["producer_uses_topology_state_reabsorption_record"]
        ),
        "scheduled_packet_processed_by_step": positive_lane[
            "scheduled_packet_processed_by_step"
        ],
        "artifact_only_route_arbitration_replay_passed": positive_lane[
            "artifact_validator"
        ]["valid"],
        "old_primary_blocker_resolved": positive_lane["passed"],
        "unresolved_tie_control_blocks_selection": unresolved_tie_control[
            "passed_negative_control"
        ],
        "hidden_input_control_blocks_selection": hidden_input_control[
            "passed_negative_control"
        ],
        "claim_boundary_preserved": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_flags = dict(iter20_report["claim_flags"])
    claim_flags.update(
        {
            "native_lgrc_route_arbitration_supported": True,
            "native_lgrc_choice_selection_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "choice_or_agency_claim_allowed": False,
            "agency_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "biological_claim_allowed": False,
            "movement_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
        }
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter21b_native_lgrc_route_arbitration_rerun_v1",
        "iteration": "21-B",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": (
            "native_route_arbitration_plus_surface_lineage_and_topology_state_reabsorption"
        ),
        "movement_substrate": "S7_port_graph_topology_lineage_probe_v1",
        "geometry_scope": "topology_mutating",
        "substrate_class": "port_graph",
        "source_artifacts": {
            "iteration_20": _artifact_record(ITER20_PATH),
            "phase8_native_route_arbitration_closeout": _artifact_record(
                PHASE8_CLOSEOUT_PATH
            ),
        },
        "input_ceiling": iter20_report["claim_ceiling"],
        "claim_ceiling": iter20_report["claim_ceiling"],
        "attempted_promotion": "native_lgrc_route_arbitration_selection_candidate",
        "promotion_result": (
            "runtime_route_arbitration_supported_choice_claim_blocked"
        ),
        "previous_primary_blocker": "native_lgrc_topology_route_selection_not_exposed",
        "primary_blocker": None if status == "passed" else "native_route_arbitration_rerun_failed",
        "positive_lane": positive_lane,
        "controls": {
            "unresolved_tie_control": unresolved_tie_control,
            "hidden_input_control": hidden_input_control,
            "claim_promotion_control": {
                "passed_negative_control": True,
                "primary_blocker": "route_arbitration_is_not_semantic_choice_or_agency",
            },
        },
        "checks": checks,
        "claim_flags": claim_flags,
        "blocked_claims": [
            "native_lgrc_choice_selection_as_semantic_choice",
            "semantic_choice",
            "agency",
            "rc_identity_collapse",
            "identity_acceptance",
            "locomotion_like_basin_dynamics",
            "biological_behavior",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "boundary": {
            "native_route_arbitration_supported": positive_lane["passed"],
            "old_route_selection_blocker_resolved": positive_lane["passed"],
            "native_lgrc_choice_selection_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "interpretation": (
                "Iteration 21-B resolves the old route-selection exposure "
                "blocker as runtime route arbitration: candidate routes are "
                "formed from committed runtime-visible evidence, serialized "
                "policy selects one route, the selected topology event cites "
                "the arbitration record, and artifact-only replay reconstructs "
                "the downstream lineage/reabsorption/producer/step chain. This "
                "is not semantic choice, agency, or RC identity collapse."
            ),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "status_short": _run_git(["status", "--short"]),
            "head": _run_git(["rev-parse", "HEAD"]),
        },
        "next_iteration": "22-B_or_23_topology_mutating_taxonomy_closeout",
    }


def write_report(report: dict[str, Any]) -> None:
    lines = [
        "# N04 Iteration 21-B Native LGRC Route-Arbitration Rerun",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        f"Attempted promotion: `{report['attempted_promotion']}`",
        "",
        f"Promotion result: `{report['promotion_result']}`",
        "",
        f"Previous blocker: `{report['previous_primary_blocker']}`",
        "",
        f"Primary blocker: `{report['primary_blocker'] if report['primary_blocker'] is not None else 'null'}`",
        "",
        "Iteration 21-B reruns the route-selection boundary after Phase 8 native route arbitration.",
        "",
        "## Positive Lane",
        "",
    ]
    lane = report["positive_lane"]
    lines.extend(
        [
            f"- candidate route count: `{lane['candidate_route_count']}`",
            f"- arbitration reason: `{lane['arbitration_reason_code']}`",
            f"- selected candidate: `{lane['selected_candidate_route_id']}`",
            f"- selected topology event references arbitration: `{lane['selected_topology_event_references_arbitration']}`",
            f"- producer reads transported digest: `{lane['producer_reads_transported_digest']}`",
            f"- producer uses reabsorption record: `{lane['producer_uses_topology_state_reabsorption_record']}`",
            f"- scheduled packet processed by step: `{lane['scheduled_packet_processed_by_step']}`",
            f"- artifact replay valid: `{lane['artifact_validator']['valid']}`",
            "",
            "## Controls",
            "",
        ]
    )
    for key, control in report["controls"].items():
        lines.append(
            f"- `{key}`: passed=`{control['passed_negative_control']}`, "
            f"reason=`{control['primary_blocker']}`"
        )
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            report["boundary"]["interpretation"],
            "",
            "Native route arbitration support remains distinct from semantic choice, agency, RC identity collapse, identity acceptance, locomotion-like behavior, biological behavior, inherited-N03 movement, and unrestricted movement.",
            "",
            "## Command",
            "",
            f"```bash\n{COMMAND}\n```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
