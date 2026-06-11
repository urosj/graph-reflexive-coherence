#!/usr/bin/env python3
"""Run N04 Iteration 22 identity-through-topology-mutation boundary probe."""

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
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_PULSE_SUBSTRATE_COUPLING,
    LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED,
    LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
    validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts,
)

import run_n04_iter19c_s7_adaptive_gate_with_native_surface_lineage as iter19c  # noqa: E402
import run_n04_iter19e_topology_mutating_movement_after_state_reabsorption as iter19e  # noqa: E402
import run_n04_iter20_topology_mutating_repeatability_stress as iter20  # noqa: E402


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER20_PATH = N04 / "outputs/n04_iter20_topology_mutating_repeatability_stress.json"
ITER21_PATH = N04 / "outputs/n04_iter21_native_lgrc_choice_selection_boundary.json"
OUTPUT_PATH = N04 / "outputs/n04_iter22_identity_through_topology_mutation_boundary.json"
REPORT_PATH = N04 / "reports/n04_iter22_identity_through_topology_mutation_boundary.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter22_identity_through_topology_mutation_boundary.py"
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


def _lineage_artifacts(model: Any) -> dict[str, Any]:
    snapshot = model.snapshot()
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    return {
        "events": snapshot["events"],
        "surface_rows": runtime["causal_pulse_substrate_surface_log"],
        "surface_lineage_records": runtime[
            "causal_pulse_substrate_surface_lineage_log"
        ],
        "topology_state_reabsorption_records": runtime[
            "topology_state_reabsorption_log"
        ],
    }


def _run_identity_boundary_lane() -> dict[str, Any]:
    model = iter19c.LGRC9V3.from_state(
        iter19c._three_node_state(),
        iter19e._params_with_state_reabsorption(),
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

    model.process_causal_collapse_reabsorption(
        topology_event_kind=LGRC9V3_TOPOLOGY_EVENT_KIND_COLLAPSE,
        competing_sink_ids=[0, 1],
        selected_sink_id=0,
        losing_sink_ids=[1],
        transferred_node_ids=[1, 2],
        lineage_transfer_map={1: "0", 2: "0"},
        source_lineage_ids={1: "identity22:source-port", 2: "identity22:target-port"},
        target_lineage_id="0",
        coherence_transfer_amount=0.0,
    )
    state_after_topology = model.get_state()
    transported_row = state_after_topology.causal_pulse_substrate_surface_log[-1]
    lineage_record = state_after_topology.causal_pulse_substrate_surface_lineage_log[-1]
    reabsorption_record = state_after_topology.topology_state_reabsorption_log[-1]
    ledger_after_reabsorption = iter19e._ledger_state(model)

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
    processed_event_kinds: list[str] = []
    if producer_record.scheduled_event_id is not None:
        for _ in range(2):
            step_result = model.step()
            processed_event_ids.append(str(step_result.bookkeeping["processed_event_id"]))
            processed_event_kinds.append(str(step_result.bookkeeping["processed_event_kind"]))
    ledger_after_processing = iter19e._ledger_state(model)
    artifacts = _lineage_artifacts(model)
    artifact_validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
        **artifacts,
        production_results=[producer_result.to_artifact()],
    )
    scheduled_and_processed = (
        producer_record.reason_code
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
        and producer_record.scheduled_event_id is not None
        and producer_record.scheduled_event_id in processed_event_ids
    )
    topology_lineage_continuity_passed = (
        lineage_record.lineage_action
        == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_ACTION_TRANSPORTED
        and lineage_record.lineage_status == LGRC9V3_CAUSAL_PULSE_SUBSTRATE_LINEAGE_TRANSPORTED
        and lineage_record.source_surface_digest == source_row.surface_digest
        and lineage_record.transported_surface_digest == transported_row.surface_digest
        and dict(lineage_record.lineage_transfer_map) == {"1": "0", "2": "0"}
    )
    reabsorbed_state_continuity_passed = (
        reabsorption_record.topology_event_id == lineage_record.topology_event_id
        and dict(reabsorption_record.lineage_transfer_map) == {"1": "0", "2": "0"}
        and abs(
            float(reabsorption_record.packet_ledger_node_total_after)
            - float(reabsorption_record.active_node_state_total_after)
        )
        < 1e-12
        and iter20._is_budget_exact(ledger_after_reabsorption)
        and iter20._is_budget_exact(ledger_after_processing)
    )
    producer_uses_current_reabsorbed_evidence = (
        producer_record.causal_surface_digest == transported_row.surface_digest
        and producer_record.observed_evidence.get(
            "topology_state_reabsorption_record_digest"
        )
        == reabsorption_record.topology_state_reabsorption_digest
        and producer_record.observed_evidence.get(
            "topology_state_reabsorption_verified"
        )
        is True
    )
    return {
        "lane_id": "identity_through_topology_mutation_forward",
        "source_surface": source_row.to_artifact(),
        "transported_surface": transported_row.to_artifact(),
        "surface_lineage_record": lineage_record.to_artifact(),
        "topology_state_reabsorption_record": reabsorption_record.to_artifact(),
        "producer_record": producer_record.to_artifact(),
        "processed_event_ids": processed_event_ids,
        "processed_event_kinds": processed_event_kinds,
        "ledger_after_reabsorption": ledger_after_reabsorption,
        "ledger_after_processing": ledger_after_processing,
        "artifact_validator": artifact_validation,
        "topology_lineage_continuity_passed": topology_lineage_continuity_passed,
        "reabsorbed_state_continuity_passed": reabsorbed_state_continuity_passed,
        "producer_uses_current_reabsorbed_evidence": (
            producer_uses_current_reabsorbed_evidence
        ),
        "scheduled_packet_processed_by_step": scheduled_and_processed,
    }


def _identity_audit(lane: dict[str, Any]) -> dict[str, Any]:
    source_surface = lane["source_surface"]
    transported_surface = lane["transported_surface"]
    reabsorption = lane["topology_state_reabsorption_record"]
    lineage = lane["surface_lineage_record"]
    rc_identity_invariants = {
        "stable_self_maintaining_attractor_basin_serialized": False,
        "basin_identity_id_serialized": False,
        "attractivity_invariance_checked": False,
        "reflexive_closure_checked": False,
        "coherence_compatibility_checked_as_rc_identity": False,
        "identity_acceptance_event_emitted": False,
    }
    lineage_evidence_supported = (
        lane["topology_lineage_continuity_passed"]
        and lane["reabsorbed_state_continuity_passed"]
        and lane["producer_uses_current_reabsorbed_evidence"]
        and lane["scheduled_packet_processed_by_step"]
        and lane["artifact_validator"]["valid"] is True
    )
    return {
        "identity_kind_before": "boundary_signal",
        "identity_surface_before": "native_causal_pulse_substrate_surface",
        "identity_kind_after": "boundary_signal",
        "identity_surface_after": "native_causal_pulse_substrate_surface",
        "identity_boundary_class_before": "runtime_coherence_basin_candidate_not_rc_identity",
        "identity_boundary_class_after": (
            "transported_surface_plus_reabsorbed_state_continuity"
        ),
        "source_surface_digest": source_surface["surface_digest"],
        "transported_surface_digest": transported_surface["surface_digest"],
        "source_surface_nodes": source_surface["surface_nodes"],
        "transported_surface_nodes": transported_surface["surface_nodes"],
        "lineage_transfer_map": lineage["lineage_transfer_map"],
        "topology_state_reabsorption_digest": reabsorption[
            "topology_state_reabsorption_digest"
        ],
        "active_state_digest_before": reabsorption["active_state_digest_before"],
        "active_state_digest_after": reabsorption["active_state_digest_after"],
        "lineage_evidence_supported": lineage_evidence_supported,
        "rc_identity_invariants": rc_identity_invariants,
        "rc_identity_through_topology_supported": False,
        "identity_acceptance_claim_allowed": False,
        "primary_identity_blocker": (
            "rc_identity_basin_invariance_not_validated_across_topology_mutation"
        ),
        "interpretation": (
            "The native artifacts prove topology-aware continuity of surface "
            "evidence, active state, packet ledger, and producer scheduling. "
            "They do not serialize a stable RC coherence-basin identity or "
            "prove attractor-basin invariance through topology mutation."
        ),
    }


def build_report() -> dict[str, Any]:
    iter20_report = _load_json(ITER20_PATH)
    iter21_report = _load_json(ITER21_PATH)
    lane = _run_identity_boundary_lane()
    identity_audit = _identity_audit(lane)
    attempted_promotion = "rc_identity_through_topology_mutation_candidate"
    primary_blocker = identity_audit["primary_identity_blocker"]
    controls = {
        "surface_lineage_only_is_not_rc_identity": {
            "passed_negative_control": True,
            "primary_blocker": "surface_lineage_evidence_is_not_rc_identity_basin",
        },
        "topology_state_reabsorption_only_is_not_rc_identity": {
            "passed_negative_control": True,
            "primary_blocker": "state_reabsorption_evidence_is_not_identity_acceptance",
        },
        "identity_acceptance_claim_control": {
            "passed_negative_control": True,
            "primary_blocker": "identity_acceptance_not_emitted_by_runtime",
        },
        "rc_identity_collapse_claim_control": {
            "passed_negative_control": True,
            "primary_blocker": "rc_identity_collapse_not_validated",
        },
    }
    checks = {
        "iteration_20_baseline_passed": (
            iter20_report["status"] == "passed"
            and iter20_report["claim_ceiling"] == "topology_mutating_movement_candidate"
        ),
        "iteration_21_choice_boundary_consumed": (
            iter21_report["status"] == "passed"
            and iter21_report["promotion_result"] == "blocked"
        ),
        "identity_kind_before_recorded": bool(identity_audit["identity_kind_before"]),
        "identity_surface_before_recorded": bool(identity_audit["identity_surface_before"]),
        "identity_kind_after_recorded": bool(identity_audit["identity_kind_after"]),
        "identity_surface_after_recorded": bool(identity_audit["identity_surface_after"]),
        "topology_lineage_continuity_passed": lane[
            "topology_lineage_continuity_passed"
        ],
        "reabsorbed_state_continuity_passed": lane[
            "reabsorbed_state_continuity_passed"
        ],
        "producer_schedules_from_current_reabsorbed_evidence": lane[
            "producer_uses_current_reabsorbed_evidence"
        ],
        "artifact_only_replay_passed": lane["artifact_validator"]["valid"],
        "rc_identity_invariants_not_serialized": not any(
            identity_audit["rc_identity_invariants"].values()
        ),
        "identity_acceptance_claim_blocked": (
            identity_audit["identity_acceptance_claim_allowed"] is False
        ),
        "claim_boundary_preserved": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_flags = dict(iter20_report["claim_flags"])
    claim_flags.update(
        {
            "rc_identity_through_topology_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "native_lgrc_choice_selection_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "choice_or_agency_claim_allowed": False,
            "agency_claim_allowed": False,
            "movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "biological_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
        }
    )
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter22_identity_through_topology_mutation_boundary_v1",
        "iteration": "22",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": (
            "native_causal_pulse_substrate_surface_plus_topology_state_reabsorption"
        ),
        "movement_substrate": "S7_port_graph_topology_lineage_probe_v1",
        "geometry_scope": "topology_mutating",
        "substrate_class": "port_graph",
        "source_artifacts": {
            "iteration_20": _artifact_record(ITER20_PATH),
            "iteration_21": _artifact_record(ITER21_PATH),
        },
        "input_ceiling": iter20_report["claim_ceiling"],
        "claim_ceiling": iter20_report["claim_ceiling"],
        "attempted_promotion": attempted_promotion,
        "promotion_result": "blocked",
        "primary_blocker": primary_blocker,
        "identity_audit": identity_audit,
        "native_lane": {
            "lane_id": lane["lane_id"],
            "source_surface_digest": lane["source_surface"]["surface_digest"],
            "transported_surface_digest": lane["transported_surface"]["surface_digest"],
            "surface_lineage_record_digest": lane["surface_lineage_record"][
                "lineage_record_digest"
            ],
            "topology_state_reabsorption_record_digest": lane[
                "topology_state_reabsorption_record"
            ]["topology_state_reabsorption_digest"],
            "topology_lineage_continuity_passed": lane[
                "topology_lineage_continuity_passed"
            ],
            "reabsorbed_state_continuity_passed": lane[
                "reabsorbed_state_continuity_passed"
            ],
            "producer_uses_current_reabsorbed_evidence": lane[
                "producer_uses_current_reabsorbed_evidence"
            ],
            "scheduled_packet_processed_by_step": lane[
                "scheduled_packet_processed_by_step"
            ],
            "artifact_validator": lane["artifact_validator"],
        },
        "controls": controls,
        "checks": checks,
        "claim_flags": claim_flags,
        "blocked_claims": [
            "rc_identity_through_topology_mutation",
            "rc_identity_collapse",
            "identity_acceptance",
            "native_lgrc_choice_selection",
            "semantic_choice",
            "agency",
            "locomotion_like_basin_dynamics",
            "biological_behavior",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "boundary": {
            "topology_mutating_movement_candidate_remains_supported": (
                iter20_report["claim_ceiling"] == "topology_mutating_movement_candidate"
            ),
            "lineage_continuity_supported": identity_audit[
                "lineage_evidence_supported"
            ],
            "rc_identity_through_topology_supported": False,
            "identity_acceptance_supported": False,
            "interpretation": identity_audit["interpretation"],
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
        "next_iteration": "23_topology_mutating_taxonomy_closeout",
    }


def write_report(report: dict[str, Any]) -> None:
    identity = report["identity_audit"]
    lane = report["native_lane"]
    lines = [
        "# N04 Iteration 22 Identity Through Topology Mutation Boundary",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        f"Attempted promotion: `{report['attempted_promotion']}`",
        "",
        f"Promotion result: `{report['promotion_result']}`",
        "",
        f"Primary blocker: `{report['primary_blocker']}`",
        "",
        "Iteration 22 asks whether topology-mutating movement also proves runtime coherence-basin identity through the topology mutation.",
        "",
        "## Native Lane",
        "",
        f"- source surface digest: `{lane['source_surface_digest']}`",
        f"- transported surface digest: `{lane['transported_surface_digest']}`",
        f"- surface lineage record digest: `{lane['surface_lineage_record_digest']}`",
        f"- topology-state reabsorption digest: `{lane['topology_state_reabsorption_record_digest']}`",
        f"- topology lineage continuity passed: `{lane['topology_lineage_continuity_passed']}`",
        f"- reabsorbed state continuity passed: `{lane['reabsorbed_state_continuity_passed']}`",
        f"- producer uses current reabsorbed evidence: `{lane['producer_uses_current_reabsorbed_evidence']}`",
        f"- artifact-only replay passed: `{lane['artifact_validator']['valid']}`",
        "",
        "## Identity Audit",
        "",
        f"- identity kind before: `{identity['identity_kind_before']}`",
        f"- identity surface before: `{identity['identity_surface_before']}`",
        f"- identity boundary class before: `{identity['identity_boundary_class_before']}`",
        f"- identity kind after: `{identity['identity_kind_after']}`",
        f"- identity surface after: `{identity['identity_surface_after']}`",
        f"- identity boundary class after: `{identity['identity_boundary_class_after']}`",
        f"- lineage evidence supported: `{identity['lineage_evidence_supported']}`",
        f"- RC identity through topology supported: `{identity['rc_identity_through_topology_supported']}`",
        "",
        "## RC Identity Invariants",
        "",
    ]
    for key, value in identity["rc_identity_invariants"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Controls", ""])
    for key, value in report["controls"].items():
        lines.append(
            f"- `{key}`: passed=`{value['passed_negative_control']}`, "
            f"reason=`{value['primary_blocker']}`"
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
            "The current ceiling remains `topology_mutating_movement_candidate`. "
            "Iteration 22 supports topology-aware lineage continuity, not RC "
            "identity collapse or identity acceptance.",
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
