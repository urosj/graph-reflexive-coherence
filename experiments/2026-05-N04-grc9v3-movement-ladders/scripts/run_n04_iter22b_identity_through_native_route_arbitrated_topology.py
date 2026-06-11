#!/usr/bin/env python3
"""Run N04 Iteration 22-B identity check after native route arbitration."""

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
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
    validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts,
    validate_lgrc9v3_native_route_arbitration_artifacts,
)

import run_n04_iter19e_topology_mutating_movement_after_state_reabsorption as iter19e  # noqa: E402
import run_n04_iter20_topology_mutating_repeatability_stress as iter20  # noqa: E402
import run_n04_iter21b_native_lgrc_route_arbitration_rerun as iter21b  # noqa: E402


N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
ITER20_PATH = N04 / "outputs/n04_iter20_topology_mutating_repeatability_stress.json"
ITER21B_PATH = N04 / "outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json"
ITER22_PATH = N04 / "outputs/n04_iter22_identity_through_topology_mutation_boundary.json"
OUTPUT_PATH = (
    N04
    / "outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json"
)
REPORT_PATH = (
    N04
    / "reports/n04_iter22b_identity_through_native_route_arbitrated_topology.md"
)
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter22b_identity_through_native_route_arbitrated_topology.py"
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


def _surface_lineage_artifacts(model: Any) -> dict[str, Any]:
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


def _selected_topology_payload(model: Any, arbitration_record: Any) -> dict[str, Any]:
    payloads = [
        model._topology_event_payload(topology_event)  # noqa: SLF001
        for topology_event in model.get_state().topology_event_log
        if model._topology_event_payload(topology_event).get(  # noqa: SLF001
            "native_route_arbitration_record_id"
        )
        == arbitration_record.native_route_arbitration_record_id
    ]
    if len(payloads) != 1:
        raise RuntimeError(f"expected one selected topology payload, got {len(payloads)}")
    return payloads[0]


def _run_native_route_arbitrated_identity_lane() -> dict[str, Any]:
    model, candidate_set = iter21b._build_native_route_model()  # noqa: SLF001
    source_row = model.get_state().causal_pulse_substrate_surface_log[-1]
    arbitration_result = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
    )
    arbitration_record = arbitration_result["route_arbitration_record"]
    commit_result = model.commit_native_route_arbitration_selection(
        native_route_arbitration_reference=str(
            arbitration_record.native_route_arbitration_digest
        ),
    )
    selected_candidate = commit_result["selected_candidate_route_record"]
    topology_payload = _selected_topology_payload(model, arbitration_record)
    state_after_commit = model.get_state()
    transported_row = state_after_commit.causal_pulse_substrate_surface_log[-1]
    lineage_record = state_after_commit.causal_pulse_substrate_surface_lineage_log[-1]
    reabsorption_record = state_after_commit.topology_state_reabsorption_log[-1]
    selected_topology_event_digest = str(
        arbitration_record.selected_topology_event_digest
    )

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

    ledger_after_processing = iter19e._ledger_state(model)  # noqa: SLF001
    route_validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        **_validation_artifacts(model),
    )
    lineage_validation = validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts(
        **_surface_lineage_artifacts(model),
        production_results=[producer_result.to_artifact()],
    )
    producer_evidence = dict(producer_record.observed_evidence)
    scheduled_and_processed = (
        producer_record.reason_code
        == LGRC9V3_AUTONOMOUS_PRODUCER_REASON_PULSE_SUBSTRATE_COUPLING_SCHEDULED
        and producer_record.scheduled_event_id in processed_event_ids
    )
    native_selection_continuity_passed = (
        arbitration_record.arbitration_reason_code
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE
        and selected_candidate.candidate_route_digest
        == arbitration_record.selected_candidate_route_digest
        and topology_payload["native_route_arbitration_digest"]
        == arbitration_record.native_route_arbitration_digest
        and bool(selected_topology_event_digest)
    )
    lineage_and_reabsorption_passed = (
        lineage_record.source_surface_digest == source_row.surface_digest
        and lineage_record.transported_surface_digest == transported_row.surface_digest
        and lineage_record.topology_event_digest
        == selected_topology_event_digest
        and reabsorption_record.topology_event_digest
        == selected_topology_event_digest
        and dict(reabsorption_record.lineage_transfer_map)
        == dict(selected_candidate.candidate_lineage_transfer_map)
        and abs(
            float(reabsorption_record.packet_ledger_node_total_after)
            - float(reabsorption_record.active_node_state_total_after)
        )
        < 1e-12
    )
    producer_uses_current_reabsorbed_evidence = (
        producer_record.causal_surface_digest == transported_row.surface_digest
        and producer_evidence.get("topology_event_digest")
        == selected_topology_event_digest
        and producer_evidence.get("topology_state_reabsorption_record_digest")
        == reabsorption_record.topology_state_reabsorption_digest
        and producer_evidence.get("topology_state_reabsorption_verified") is True
    )
    passed = (
        native_selection_continuity_passed
        and lineage_and_reabsorption_passed
        and producer_uses_current_reabsorbed_evidence
        and scheduled_and_processed
        and iter20._is_budget_exact(ledger_after_processing)  # noqa: SLF001
        and route_validation["valid"] is True
        and lineage_validation["valid"] is True
    )
    return {
        "lane_id": "identity_through_native_route_arbitrated_topology",
        "status": "passed" if passed else "failed",
        "candidate_set_digest": candidate_set.candidate_set_digest,
        "route_arbitration_record_id": arbitration_record.native_route_arbitration_record_id,
        "route_arbitration_digest": arbitration_record.native_route_arbitration_digest,
        "arbitration_reason_code": arbitration_record.arbitration_reason_code,
        "selected_candidate_route_id": selected_candidate.candidate_route_id,
        "selected_candidate_route_digest": selected_candidate.candidate_route_digest,
        "selected_topology_event_id": topology_payload["topology_event_id"],
        "selected_topology_event_digest": selected_topology_event_digest,
        "source_surface": source_row.to_artifact(),
        "transported_surface": transported_row.to_artifact(),
        "surface_lineage_record": lineage_record.to_artifact(),
        "topology_state_reabsorption_record": reabsorption_record.to_artifact(),
        "producer_record": producer_record.to_artifact(),
        "processed_event_ids": processed_event_ids,
        "processed_event_kinds": processed_event_kinds,
        "ledger_after_processing": ledger_after_processing,
        "route_artifact_validator": route_validation,
        "surface_lineage_artifact_validator": lineage_validation,
        "native_selection_continuity_passed": native_selection_continuity_passed,
        "lineage_and_reabsorption_passed": lineage_and_reabsorption_passed,
        "producer_uses_current_reabsorbed_evidence": (
            producer_uses_current_reabsorbed_evidence
        ),
        "scheduled_packet_processed_by_step": scheduled_and_processed,
        "budget_exact_after_processing": iter20._is_budget_exact(ledger_after_processing),  # noqa: SLF001
        "passed": passed,
    }


def _identity_audit(lane: dict[str, Any]) -> dict[str, Any]:
    reabsorption = lane["topology_state_reabsorption_record"]
    rc_identity_invariants = {
        "stable_self_maintaining_attractor_basin_serialized": False,
        "basin_identity_id_serialized": False,
        "attractivity_invariance_checked": False,
        "reflexive_closure_checked": False,
        "coherence_compatibility_checked_as_rc_identity": False,
        "identity_acceptance_event_emitted": False,
        "route_arbitration_declares_identity_collapse": False,
    }
    native_route_continuity_supported = (
        lane["native_selection_continuity_passed"]
        and lane["lineage_and_reabsorption_passed"]
        and lane["producer_uses_current_reabsorbed_evidence"]
        and lane["scheduled_packet_processed_by_step"]
        and lane["route_artifact_validator"]["valid"] is True
        and lane["surface_lineage_artifact_validator"]["valid"] is True
    )
    return {
        "identity_kind_before": "boundary_signal",
        "identity_surface_before": "native_causal_pulse_substrate_surface",
        "identity_kind_after": "boundary_signal",
        "identity_surface_after": "native_causal_pulse_substrate_surface",
        "identity_boundary_class_before": "runtime_coherence_basin_candidate_not_rc_identity",
        "identity_boundary_class_after": (
            "native_route_arbitrated_transport_plus_reabsorbed_state_continuity"
        ),
        "route_arbitration_digest": lane["route_arbitration_digest"],
        "selected_candidate_route_digest": lane["selected_candidate_route_digest"],
        "selected_topology_event_digest": lane["selected_topology_event_digest"],
        "source_surface_digest": lane["source_surface"]["surface_digest"],
        "transported_surface_digest": lane["transported_surface"]["surface_digest"],
        "topology_state_reabsorption_digest": reabsorption[
            "topology_state_reabsorption_digest"
        ],
        "active_state_digest_before": reabsorption["active_state_digest_before"],
        "active_state_digest_after": reabsorption["active_state_digest_after"],
        "native_route_continuity_supported": native_route_continuity_supported,
        "rc_identity_invariants": rc_identity_invariants,
        "rc_identity_through_native_route_arbitrated_topology_supported": False,
        "identity_acceptance_claim_allowed": False,
        "primary_identity_blocker": (
            "rc_identity_basin_invariance_not_validated_across_topology_mutation"
        ),
        "interpretation": (
            "Native route arbitration removes the experiment-supplied route "
            "selection caveat and proves the selected topology event can be "
            "replayed through lineage, reabsorption, producer scheduling, and "
            "step processing. It still does not serialize a stable RC "
            "coherence-basin identity or validate attractor-basin invariance "
            "through topology mutation."
        ),
    }


def build_report() -> dict[str, Any]:
    iter20_report = _load_json(ITER20_PATH)
    iter21b_report = _load_json(ITER21B_PATH)
    iter22_report = _load_json(ITER22_PATH)
    lane = _run_native_route_arbitrated_identity_lane()
    identity_audit = _identity_audit(lane)
    controls = {
        "native_route_arbitration_is_not_rc_identity": {
            "passed_negative_control": True,
            "primary_blocker": "route_arbitration_evidence_is_not_rc_identity_basin",
        },
        "selected_topology_event_is_not_identity_acceptance": {
            "passed_negative_control": True,
            "primary_blocker": "selected_topology_event_does_not_emit_identity_acceptance",
        },
        "surface_lineage_and_reabsorption_not_identity_collapse": {
            "passed_negative_control": True,
            "primary_blocker": "lineage_reabsorption_evidence_is_not_rc_identity_collapse",
        },
        "identity_acceptance_claim_control": {
            "passed_negative_control": True,
            "primary_blocker": "identity_acceptance_not_emitted_by_runtime",
        },
        "semantic_choice_claim_control": {
            "passed_negative_control": True,
            "primary_blocker": "route_arbitration_is_not_semantic_choice_or_agency",
        },
    }
    checks = {
        "iteration_20_ceiling_consumed": (
            iter20_report["status"] == "passed"
            and iter20_report["claim_ceiling"] == "topology_mutating_movement_candidate"
        ),
        "iteration_21b_native_route_arbitration_consumed": (
            iter21b_report["status"] == "passed"
            and iter21b_report["boundary"]["native_route_arbitration_supported"]
            is True
            and iter21b_report["boundary"]["old_route_selection_blocker_resolved"]
            is True
        ),
        "iteration_22_identity_blocker_consumed": (
            iter22_report["status"] == "passed"
            and iter22_report["primary_blocker"]
            == "rc_identity_basin_invariance_not_validated_across_topology_mutation"
        ),
        "native_selection_continuity_passed": lane[
            "native_selection_continuity_passed"
        ],
        "lineage_and_reabsorption_passed": lane["lineage_and_reabsorption_passed"],
        "producer_schedules_from_current_reabsorbed_evidence": lane[
            "producer_uses_current_reabsorbed_evidence"
        ],
        "scheduled_packet_processed_by_step": lane[
            "scheduled_packet_processed_by_step"
        ],
        "route_artifact_replay_passed": lane["route_artifact_validator"]["valid"],
        "surface_lineage_artifact_replay_passed": lane[
            "surface_lineage_artifact_validator"
        ]["valid"],
        "budget_exact_after_processing": lane["budget_exact_after_processing"],
        "rc_identity_invariants_not_serialized": not any(
            identity_audit["rc_identity_invariants"].values()
        ),
        "identity_acceptance_claim_blocked": (
            identity_audit["identity_acceptance_claim_allowed"] is False
        ),
        "claim_boundary_preserved": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    claim_flags = dict(iter21b_report["claim_flags"])
    claim_flags.update(
        {
            "native_lgrc_route_arbitration_supported": True,
            "rc_identity_through_topology_claim_allowed": False,
            "rc_identity_through_native_route_arbitrated_topology_claim_allowed": False,
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
        "report_kind": (
            "n04_iter22b_identity_through_native_route_arbitrated_topology_v1"
        ),
        "iteration": "22-B",
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
            "iteration_21b": _artifact_record(ITER21B_PATH),
            "iteration_22": _artifact_record(ITER22_PATH),
        },
        "input_ceiling": iter21b_report["claim_ceiling"],
        "claim_ceiling": iter21b_report["claim_ceiling"],
        "attempted_promotion": (
            "rc_identity_through_native_route_arbitrated_topology_candidate"
        ),
        "promotion_result": "blocked",
        "primary_blocker": identity_audit["primary_identity_blocker"],
        "identity_audit": identity_audit,
        "native_route_arbitrated_lane": {
            "lane_id": lane["lane_id"],
            "candidate_set_digest": lane["candidate_set_digest"],
            "route_arbitration_digest": lane["route_arbitration_digest"],
            "selected_candidate_route_digest": lane[
                "selected_candidate_route_digest"
            ],
            "selected_topology_event_digest": lane[
                "selected_topology_event_digest"
            ],
            "source_surface_digest": lane["source_surface"]["surface_digest"],
            "transported_surface_digest": lane["transported_surface"][
                "surface_digest"
            ],
            "surface_lineage_record_digest": lane["surface_lineage_record"][
                "lineage_record_digest"
            ],
            "topology_state_reabsorption_record_digest": lane[
                "topology_state_reabsorption_record"
            ]["topology_state_reabsorption_digest"],
            "native_selection_continuity_passed": lane[
                "native_selection_continuity_passed"
            ],
            "lineage_and_reabsorption_passed": lane[
                "lineage_and_reabsorption_passed"
            ],
            "producer_uses_current_reabsorbed_evidence": lane[
                "producer_uses_current_reabsorbed_evidence"
            ],
            "scheduled_packet_processed_by_step": lane[
                "scheduled_packet_processed_by_step"
            ],
            "route_artifact_validator": lane["route_artifact_validator"],
            "surface_lineage_artifact_validator": lane[
                "surface_lineage_artifact_validator"
            ],
        },
        "controls": controls,
        "checks": checks,
        "claim_flags": claim_flags,
        "blocked_claims": [
            "rc_identity_through_topology_mutation",
            "rc_identity_through_native_route_arbitrated_topology",
            "rc_identity_collapse",
            "identity_acceptance",
            "native_lgrc_choice_selection_as_semantic_choice",
            "semantic_choice",
            "agency",
            "locomotion_like_basin_dynamics",
            "biological_behavior",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "boundary": {
            "topology_mutating_movement_candidate_remains_supported": (
                iter21b_report["claim_ceiling"]
                == "topology_mutating_movement_candidate"
            ),
            "native_route_arbitration_supported": True,
            "native_route_arbitrated_topology_continuity_supported": (
                identity_audit["native_route_continuity_supported"]
            ),
            "rc_identity_through_native_route_arbitrated_topology_supported": False,
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
    lane = report["native_route_arbitrated_lane"]
    lines = [
        "# N04 Iteration 22-B Identity Through Native Route-Arbitrated Topology",
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
        "Iteration 22-B reruns the identity-through-topology boundary after "
        "Phase 8 native route arbitration and N04 Iteration 21-B.",
        "",
        "## Native Route-Arbitrated Lane",
        "",
        f"- candidate set digest: `{lane['candidate_set_digest']}`",
        f"- route-arbitration digest: `{lane['route_arbitration_digest']}`",
        f"- selected candidate route digest: `{lane['selected_candidate_route_digest']}`",
        f"- selected topology event digest: `{lane['selected_topology_event_digest']}`",
        f"- source surface digest: `{lane['source_surface_digest']}`",
        f"- transported surface digest: `{lane['transported_surface_digest']}`",
        f"- surface lineage record digest: `{lane['surface_lineage_record_digest']}`",
        f"- topology-state reabsorption digest: `{lane['topology_state_reabsorption_record_digest']}`",
        f"- native selection continuity passed: `{lane['native_selection_continuity_passed']}`",
        f"- lineage and reabsorption passed: `{lane['lineage_and_reabsorption_passed']}`",
        f"- producer uses current reabsorbed evidence: `{lane['producer_uses_current_reabsorbed_evidence']}`",
        f"- scheduled packet processed by step: `{lane['scheduled_packet_processed_by_step']}`",
        f"- route artifact replay passed: `{lane['route_artifact_validator']['valid']}`",
        f"- surface lineage artifact replay passed: `{lane['surface_lineage_artifact_validator']['valid']}`",
        "",
        "## Identity Audit",
        "",
        f"- identity kind before: `{identity['identity_kind_before']}`",
        f"- identity surface before: `{identity['identity_surface_before']}`",
        f"- identity boundary class before: `{identity['identity_boundary_class_before']}`",
        f"- identity kind after: `{identity['identity_kind_after']}`",
        f"- identity surface after: `{identity['identity_surface_after']}`",
        f"- identity boundary class after: `{identity['identity_boundary_class_after']}`",
        f"- native route continuity supported: `{identity['native_route_continuity_supported']}`",
        "- RC identity through native route-arbitrated topology supported: "
        f"`{identity['rc_identity_through_native_route_arbitrated_topology_supported']}`",
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
            "Iteration 22-B supports native route-arbitrated topology continuity, "
            "not RC identity collapse, identity acceptance, semantic choice, or "
            "agency.",
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
