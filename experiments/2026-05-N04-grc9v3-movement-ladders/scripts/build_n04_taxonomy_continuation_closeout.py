#!/usr/bin/env python3
"""Build N04 taxonomy continuation closeout and Phase 8 return record."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
OUTPUT_PATH = N04 / "outputs/n04_taxonomy_continuation_closeout.json"
REPORT_PATH = N04 / "reports/n04_taxonomy_continuation_closeout.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/build_n04_taxonomy_continuation_closeout.py"
)

SOURCE_PATHS = {
    "taxonomy_inventory": N04 / "outputs/n04_taxonomy_inventory_v1.json",
    "taxonomy_tag_schema": N04 / "outputs/n04_taxonomy_tag_schema_v1.json",
    "iteration_19a": N04 / "outputs/n04_iter19a_s7_fixed_port_execution_report.json",
    "iteration_19b": N04 / "outputs/n04_iter19b_topology_lineage_adaptive_gate_report.json",
    "iteration_19c": N04
    / "outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json",
    "iteration_19d": N04 / "outputs/n04_iter19d_topology_mutating_movement_probe.json",
    "iteration_19e": N04
    / "outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json",
    "iteration_20": N04
    / "outputs/n04_iter20_topology_mutating_repeatability_stress.json",
    "iteration_21": N04
    / "outputs/n04_iter21_native_lgrc_choice_selection_boundary.json",
    "iteration_21b": N04
    / "outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json",
    "iteration_22": N04
    / "outputs/n04_iter22_identity_through_topology_mutation_boundary.json",
    "iteration_22b": N04
    / "outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json",
    "phase8_lineage_closeout": ROOT
    / "implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json",
    "phase8_topology_state_reabsorption_closeout": ROOT
    / "implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json",
    "phase8_time_scoped_lineage_replay_closeout": ROOT
    / "implementation/Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json",
    "phase8_native_route_arbitration_closeout": ROOT
    / "implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.json",
}


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


def build_closeout() -> dict[str, Any]:
    inventory = _load_json(SOURCE_PATHS["taxonomy_inventory"])
    schema = _load_json(SOURCE_PATHS["taxonomy_tag_schema"])
    iter19a = _load_json(SOURCE_PATHS["iteration_19a"])
    iter19b = _load_json(SOURCE_PATHS["iteration_19b"])
    iter19c = _load_json(SOURCE_PATHS["iteration_19c"])
    iter19d = _load_json(SOURCE_PATHS["iteration_19d"])
    iter19e = _load_json(SOURCE_PATHS["iteration_19e"])
    iter20 = _load_json(SOURCE_PATHS["iteration_20"])
    iter21 = _load_json(SOURCE_PATHS["iteration_21"])
    iter21b = _load_json(SOURCE_PATHS["iteration_21b"])
    iter22 = _load_json(SOURCE_PATHS["iteration_22"])
    iter22b = _load_json(SOURCE_PATHS["iteration_22b"])
    phase8 = _load_json(SOURCE_PATHS["phase8_lineage_closeout"])
    phase8_reabsorption = _load_json(
        SOURCE_PATHS["phase8_topology_state_reabsorption_closeout"]
    )
    phase8_time_scoped = _load_json(
        SOURCE_PATHS["phase8_time_scoped_lineage_replay_closeout"]
    )
    phase8_route_arbitration = _load_json(
        SOURCE_PATHS["phase8_native_route_arbitration_closeout"]
    )
    rows = inventory["inventory_rows"]
    checks = {
        "taxonomy_inventory_passed": inventory["status"] == "passed",
        "taxonomy_schema_passed": schema["status"] == "passed",
        "iteration_19a_passed": iter19a["status"] == "passed",
        "iteration_19b_fail_closed_boundary_passed": iter19b["status"] == "passed"
        and iter19b["promotion_result"] == "blocked",
        "iteration_19b_ceiling_preserved": (
            iter19b["claim_ceiling"] == "s7_fixed_port_composed_gate_candidate"
        ),
        "iteration_19b_adaptive_topology_blocked": (
            iter19b["claim_flags"]["adaptive_topology_entry_allowed"] is False
            and iter19b["claim_flags"]["topology_mutating_movement_claim_allowed"]
            is False
        ),
        "phase8_blocker_identified": (
            iter19b["primary_blocker"]
            == "causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status"
        ),
        "phase8_lineage_closeout_passed": phase8["status"] == "passed",
        "phase8_blocker_resolved": (
            iter19b.get("primary_blocker_current_status")
            == "resolved_externally_by_phase8_lineage_closeout"
            and phase8["supported"][
                "native_causal_pulse_substrate_surface_lineage_transport"
            ]
            is True
        ),
        "taxonomy_rows_include_19b": any(
            row["row_id"] == "S7_topology_lineage_adaptive_gate_blocked"
            for row in rows
        ),
        "iteration_19c_passed": iter19c["status"] == "passed",
        "adaptive_topology_entry_candidate_supported": (
            iter19c["claim_ceiling"] == "adaptive_topology_entry_candidate"
            and iter19c["claim_flags"]["adaptive_topology_entry_allowed"] is True
        ),
        "topology_mutating_movement_still_blocked_after_19c": (
            iter19c["claim_flags"]["topology_mutating_movement_claim_allowed"]
            is False
            and iter19c["claim_flags"]["movement_claim_allowed"] is False
        ),
        "taxonomy_rows_include_19c": any(
            row["row_id"]
            == "S7_adaptive_topology_entry_candidate_native_surface_lineage"
            for row in rows
        ),
        "iteration_19d_passed_fail_closed": (
            iter19d["status"] == "passed"
            and iter19d["promotion_result"] == "blocked"
            and iter19d["primary_blocker"]
            == "packet_ledger_state_reabsorption_mismatch_after_topology_event"
        ),
        "topology_mutating_movement_still_blocked_after_19d": (
            iter19d["claim_flags"]["topology_mutating_movement_claim_allowed"]
            is False
            and iter19d["claim_flags"]["movement_claim_allowed"] is False
        ),
        "taxonomy_rows_include_19d": any(
            row["row_id"] == "S7_topology_mutating_movement_probe_blocked"
            for row in rows
        ),
        "phase8_topology_state_reabsorption_closeout_passed": (
            phase8_reabsorption["status"] == "closed"
            and phase8_reabsorption["supported_capability"][
                "native_topology_state_reabsorption_supported"
            ]
            is True
        ),
        "iteration_19e_passed": (
            iter19e["status"] == "passed"
            and iter19e["claim_ceiling"] == "topology_mutating_movement_candidate"
        ),
        "topology_mutating_movement_candidate_supported_after_19e": (
            iter19e["claim_flags"]["topology_mutating_movement_claim_allowed"] is True
            and iter19e["claim_flags"]["native_lgrc_choice_selection_claim_allowed"]
            is False
            and iter19e["claim_flags"]["rc_identity_collapse_claim_allowed"] is False
        ),
        "taxonomy_rows_include_19e": any(
            row["row_id"]
            == "S7_topology_mutating_movement_candidate_after_state_reabsorption"
            for row in rows
        ),
        "iteration_20_passed_with_replay_closed": (
            iter20["status"] == "passed"
            and iter20["stress_result"] == "repeatability_stress_supported"
            and iter20["primary_blocker"] is None
            and iter20["checks"]["multiple_committed_topology_events_artifact_replay_passed"]
            is True
        ),
        "iteration_20_repeatability_reversal_perturbation_passed": (
            iter20["checks"]["repeated_topology_mutating_runs_passed"] is True
            and iter20["checks"]["reversed_matched_lane_passed"] is True
            and iter20["checks"]["lineage_accounted_perturbation_lane_passed"]
            is True
        ),
        "phase8_time_scoped_lineage_replay_closeout_passed": (
            phase8_time_scoped["status"] == "closed"
            and phase8_time_scoped["supported_capability"][
                "artifact_only_time_scoped_surface_lineage_replay_supported"
            ]
            is True
        ),
        "taxonomy_rows_include_20": any(
            row["row_id"] == "S7_topology_mutating_repeatability_stress_boundary"
            for row in rows
        ),
        "iteration_21_choice_selection_blocked": (
            iter21["status"] == "passed"
            and iter21["promotion_result"] == "blocked"
            and iter21["primary_blocker"]
            == "native_lgrc_topology_route_selection_not_exposed"
        ),
        "iteration_21_candidate_routes_artifact_valid": (
            iter21["checks"]["both_candidate_routes_executable_when_supplied"]
            is True
            and iter21["checks"]["route_a_artifact_replay_passed"] is True
            and iter21["checks"]["route_b_artifact_replay_passed"] is True
        ),
        "taxonomy_rows_include_21": any(
            row["row_id"] == "S7_native_lgrc_choice_selection_boundary_blocked"
            for row in rows
        ),
        "phase8_native_route_arbitration_closeout_passed": (
            phase8_route_arbitration["status"] == "closed"
            and phase8_route_arbitration["supported_capability"][
                "native_lgrc_route_arbitration_supported"
            ]
            is True
        ),
        "iteration_21b_native_route_arbitration_supported": (
            iter21b["status"] == "passed"
            and iter21b["boundary"]["native_route_arbitration_supported"] is True
            and iter21b["boundary"]["old_route_selection_blocker_resolved"] is True
            and iter21b["checks"]["artifact_only_route_arbitration_replay_passed"]
            is True
            and iter21b["checks"]["unresolved_tie_control_blocks_selection"] is True
            and iter21b["checks"]["hidden_input_control_blocks_selection"] is True
        ),
        "iteration_21b_claim_boundary_preserved": (
            iter21b["claim_flags"]["semantic_choice_claim_allowed"] is False
            and iter21b["claim_flags"]["agency_claim_allowed"] is False
            and iter21b["claim_flags"]["rc_identity_collapse_claim_allowed"] is False
            and iter21b["claim_flags"]["identity_acceptance_claim_allowed"] is False
        ),
        "taxonomy_rows_include_21b": any(
            row["row_id"] == "S7_native_route_arbitration_runtime_support"
            for row in rows
        ),
        "iteration_22_identity_boundary_blocked": (
            iter22["status"] == "passed"
            and iter22["promotion_result"] == "blocked"
            and iter22["primary_blocker"]
            == "rc_identity_basin_invariance_not_validated_across_topology_mutation"
        ),
        "iteration_22_lineage_continuity_artifact_valid": (
            iter22["checks"]["topology_lineage_continuity_passed"] is True
            and iter22["checks"]["reabsorbed_state_continuity_passed"] is True
            and iter22["checks"]["artifact_only_replay_passed"] is True
        ),
        "taxonomy_rows_include_22": any(
            row["row_id"]
            == "S7_identity_through_topology_mutation_boundary_blocked"
            for row in rows
        ),
        "iteration_22b_native_route_arbitrated_identity_boundary_blocked": (
            iter22b["status"] == "passed"
            and iter22b["promotion_result"] == "blocked"
            and iter22b["primary_blocker"]
            == "rc_identity_basin_invariance_not_validated_across_topology_mutation"
            and iter22b["boundary"][
                "native_route_arbitrated_topology_continuity_supported"
            ]
            is True
            and iter22b["boundary"][
                "rc_identity_through_native_route_arbitrated_topology_supported"
            ]
            is False
        ),
        "iteration_22b_artifact_validators_passed": (
            iter22b["checks"]["route_artifact_replay_passed"] is True
            and iter22b["checks"]["surface_lineage_artifact_replay_passed"] is True
            and iter22b["checks"]["rc_identity_invariants_not_serialized"] is True
        ),
        "taxonomy_rows_include_22b": any(
            row["row_id"]
            == "S7_identity_through_native_route_arbitrated_topology_boundary_blocked"
            for row in rows
        ),
    }
    status = "passed" if all(checks.values()) else "failed"
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_taxonomy_continuation_closeout_v1",
        "status": status,
        "purpose": "iteration_23_topology_mutating_taxonomy_closeout",
        "purpose_current_status": "topology_mutating_tranche_closed_after_iteration_22b",
        "source_artifacts": {
            key: _artifact_record(path) for key, path in SOURCE_PATHS.items()
        },
        "current_claim_ceiling": iter22b["claim_ceiling"],
        "strongest_supported_result": {
            "claim_ceiling": iter22b["claim_ceiling"],
            "substrate_class": iter19e["substrate_class"],
            "movement_substrate": iter19e["movement_substrate"],
            "geometry_scope": iter19e["geometry_scope"],
            "achieved_movement_level": "M6",
            "persistence_level": "T5_candidate",
            "supporting_evidence": [
                "19-E_topology_mutating_packet_work_after_state_reabsorption",
                "20_repeatability_reversal_perturbation_stress",
                "21-B_native_route_arbitration_runtime_support",
                "22-B_identity_boundary_rechecked_after_native_route_arbitration",
            ],
        },
        "blocked_boundary": {
            "attempted_promotion": iter19b["attempted_promotion"],
            "promotion_result": iter19b["promotion_result"],
            "primary_blocker": iter19b["primary_blocker"],
            "native_lgrc3_topology_lineage_replay_passed": iter19b["checks"][
                "native_lgrc3_topology_lineage_replay_passed"
            ],
            "surface_v1_rejects_lineage_transport_rows": iter19b["checks"][
                "surface_v1_rejects_lineage_transport_rows"
            ],
            "primary_blocker_current_status": iter19b.get(
                "primary_blocker_current_status",
                "unresolved_in_original_19b_artifact",
            ),
        },
        "phase8_next": {
            "plan_doc": (
                "implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineagePlan.md"
            ),
            "checklist_doc": (
                "implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md"
            ),
            "goal": (
                "implement native causal pulse-substrate surface lineage "
                "transport using LGRC-3 topology/lineage semantics"
            ),
            "not_goal": (
                "do not prove movement, adaptive topology, choice, agency, "
                "or locomotion inside Phase 8"
            ),
            "closeout_doc": (
                "implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md"
            ),
            "status": phase8["status"],
            "supported_claim_ceiling": phase8["claim_ceiling"],
        },
        "phase8_topology_state_reabsorption": {
            "closeout_doc": (
                "implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md"
            ),
            "status": phase8_reabsorption["status"],
            "native_topology_state_reabsorption_supported": (
                phase8_reabsorption["supported_capability"][
                    "native_topology_state_reabsorption_supported"
                ]
            ),
        },
        "phase8_time_scoped_lineage_replay": {
            "closeout_doc": (
                "implementation/Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md"
            ),
            "status": phase8_time_scoped["status"],
            "artifact_only_time_scoped_surface_lineage_replay_supported": (
                phase8_time_scoped["supported_capability"][
                    "artifact_only_time_scoped_surface_lineage_replay_supported"
                ]
            ),
        },
        "phase8_native_route_arbitration": {
            "closeout_doc": (
                "implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.md"
            ),
            "status": phase8_route_arbitration["status"],
            "native_lgrc_route_arbitration_supported": (
                phase8_route_arbitration["supported_capability"][
                    "native_lgrc_route_arbitration_supported"
                ]
            ),
            "support_scope": phase8_route_arbitration["supported_capability"][
                "support_scope"
            ],
        },
        "return_to_n04_after_phase8": {
            "next_probe": "topology_mutating_tranche_closed",
            "probe_goal": (
                "Iteration 23 freezes the topology-mutating movement candidate "
                "after stress, native route arbitration, and identity-boundary "
                "reruns"
            ),
            "entry_ceiling": iter19c["claim_ceiling"],
            "closed_ceiling": "topology_mutating_movement_candidate",
            "strict_probe_result": iter19d["promotion_result"],
            "strict_probe_primary_blocker": iter19d["primary_blocker"],
            "strict_probe_after_reabsorption_result": iter19e["promotion_result"],
            "strict_probe_after_reabsorption_ceiling": iter19e["claim_ceiling"],
            "iteration_20_stress_result": iter20["stress_result"],
            "iteration_20_primary_blocker": iter20["primary_blocker"],
            "iteration_21_promotion_result": iter21["promotion_result"],
            "iteration_21_primary_blocker": iter21["primary_blocker"],
            "iteration_21b_promotion_result": iter21b["promotion_result"],
            "iteration_21b_primary_blocker": iter21b["primary_blocker"],
            "iteration_21b_native_route_arbitration_supported": (
                iter21b["boundary"]["native_route_arbitration_supported"]
            ),
            "iteration_22_promotion_result": iter22["promotion_result"],
            "iteration_22_primary_blocker": iter22["primary_blocker"],
            "iteration_22b_promotion_result": iter22b["promotion_result"],
            "iteration_22b_primary_blocker": iter22b["primary_blocker"],
            "claims_still_blocked_until_revalidated": [
                "native_lgrc_choice_selection_as_semantic_choice",
                "rc_identity_collapse",
                "semantic_choice",
                "agency",
                "locomotion_like_basin_dynamics",
                "biological_behavior",
                "identity_acceptance",
                "unrestricted_movement",
            ],
        },
        "claim_flags": {
            "native_m6": iter19a["claim_flags"]["native_m6"],
            "s7_fixed_port_composed_gate_candidate_passed": iter19a["claim_flags"][
                "s7_fixed_port_composed_gate_candidate_passed"
            ],
            "adaptive_topology_entry_allowed": iter19c["claim_flags"][
                "adaptive_topology_entry_allowed"
            ],
            "topology_mutating_movement_claim_allowed": iter19e["claim_flags"][
                "topology_mutating_movement_claim_allowed"
            ],
            "native_lgrc_route_arbitration_supported": iter21b["claim_flags"][
                "native_lgrc_route_arbitration_supported"
            ],
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "native_lgrc_choice_selection_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "agency_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "unrestricted_movement_claim_allowed": False,
        },
        "blocked_claims": sorted(
            set(iter19e["blocked_claims"])
            | set(iter21b["blocked_claims"])
            | set(iter22b["blocked_claims"])
        ),
        "checks": checks,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "status_short": _run_git(["status", "--short"]),
            "head": _run_git(["rev-parse", "HEAD"]),
        },
        "next_work": "handoff_ready_for_new_tranche",
    }


def write_report(report: dict[str, Any]) -> None:
    strongest = report["strongest_supported_result"]
    boundary = report["blocked_boundary"]
    phase8 = report["phase8_next"]
    ret = report["return_to_n04_after_phase8"]
    phase8_reabsorption = report["phase8_topology_state_reabsorption"]
    phase8_time_scoped = report["phase8_time_scoped_lineage_replay"]
    phase8_route = report["phase8_native_route_arbitration"]
    lines = [
        "# N04 Taxonomy Continuation Closeout",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Current ceiling: `{report['current_claim_ceiling']}`",
        "",
        "This closeout records the N04 topology-mutating tranche through Iteration 23 after Phase 8 closed native surface-lineage, topology-state reabsorption, time-scoped replay, and route-arbitration capability gaps.",
        "",
        "## Strongest Supported Result",
        "",
        f"- claim ceiling: `{strongest['claim_ceiling']}`",
        f"- substrate: `{strongest['movement_substrate']}`",
        f"- movement level: `{strongest['achieved_movement_level']}`",
        f"- persistence level: `{strongest['persistence_level']}`",
        "",
        "## Blocked Boundary",
        "",
        f"- attempted promotion: `{boundary['attempted_promotion']}`",
        f"- promotion result: `{boundary['promotion_result']}`",
        f"- primary blocker: `{boundary['primary_blocker']}`",
        f"- primary blocker current status: `{boundary['primary_blocker_current_status']}`",
        f"- native LGRC-3 topology lineage replay passed: `{boundary['native_lgrc3_topology_lineage_replay_passed']}`",
        f"- surface v1 rejects lineage transport rows: `{boundary['surface_v1_rejects_lineage_transport_rows']}`",
        "",
        "## Phase 8 Closeout",
        "",
        f"- plan: `{phase8['plan_doc']}`",
        f"- checklist: `{phase8['checklist_doc']}`",
        f"- closeout: `{phase8['closeout_doc']}`",
        f"- status: `{phase8['status']}`",
        f"- supported claim ceiling: `{phase8['supported_claim_ceiling']}`",
        f"- topology-state reabsorption closeout: `{phase8_reabsorption['closeout_doc']}`",
        f"- topology-state reabsorption supported: `{phase8_reabsorption['native_topology_state_reabsorption_supported']}`",
        f"- time-scoped lineage replay closeout: `{phase8_time_scoped['closeout_doc']}`",
        f"- time-scoped lineage replay supported: `{phase8_time_scoped['artifact_only_time_scoped_surface_lineage_replay_supported']}`",
        f"- native route-arbitration closeout: `{phase8_route['closeout_doc']}`",
        f"- native route arbitration supported: `{phase8_route['native_lgrc_route_arbitration_supported']}`",
        "",
        "## Iteration 19-C Result",
        "",
        f"- current ceiling: `{ret['entry_ceiling']}`",
        "- adaptive topology entry candidate: `supported`",
        "- topology-mutating movement: `blocked`",
        "",
        "## Iteration 19-D Result",
        "",
        "- attempted promotion: `topology_mutating_movement_candidate`",
        f"- promotion result: `{ret['strict_probe_result']}`",
        f"- primary blocker: `{ret['strict_probe_primary_blocker']}`",
        "- current ceiling remains: `adaptive_topology_entry_candidate`",
        "",
        "## Iteration 19-E Result",
        "",
        "- attempted promotion: `topology_mutating_movement_candidate`",
        f"- promotion result: `{ret['strict_probe_after_reabsorption_result']}`",
        f"- current ceiling: `{ret['strict_probe_after_reabsorption_ceiling']}`",
        "",
        "## Iteration 20 Result",
        "",
        f"- stress result: `{ret['iteration_20_stress_result']}`",
        "- primary blocker: "
        f"`{ret['iteration_20_primary_blocker'] if ret['iteration_20_primary_blocker'] is not None else 'null'}`",
        "- current ceiling remains: `topology_mutating_movement_candidate`",
        "",
        "## Iteration 21 Result",
        "",
        "- attempted promotion: `native_lgrc_choice_selection_candidate`",
        f"- promotion result: `{ret['iteration_21_promotion_result']}`",
        f"- primary blocker: `{ret['iteration_21_primary_blocker']}`",
        "- candidate routes executable when supplied: `true`",
        "- current ceiling remains: `topology_mutating_movement_candidate`",
        "",
        "## Iteration 21-B Result",
        "",
        "- attempted promotion: `native_lgrc_route_arbitration_selection_candidate`",
        f"- promotion result: `{ret['iteration_21b_promotion_result']}`",
        "- primary blocker: "
        f"`{ret['iteration_21b_primary_blocker'] if ret['iteration_21b_primary_blocker'] is not None else 'null'}`",
        f"- native route arbitration supported: `{ret['iteration_21b_native_route_arbitration_supported']}`",
        "- semantic choice and agency: `blocked`",
        "- current ceiling remains: `topology_mutating_movement_candidate`",
        "",
        "## Iteration 22 Result",
        "",
        "- attempted promotion: `rc_identity_through_topology_mutation_candidate`",
        f"- promotion result: `{ret['iteration_22_promotion_result']}`",
        f"- primary blocker: `{ret['iteration_22_primary_blocker']}`",
        "- topology-aware surface/state continuity: `true`",
        "- current ceiling remains: `topology_mutating_movement_candidate`",
        "",
        "## Iteration 22-B Result",
        "",
        "- attempted promotion: `rc_identity_through_native_route_arbitrated_topology_candidate`",
        f"- promotion result: `{ret['iteration_22b_promotion_result']}`",
        f"- primary blocker: `{ret['iteration_22b_primary_blocker']}`",
        "- native route-arbitrated topology continuity: `true`",
        "- RC identity through topology: `blocked`",
        "- current ceiling remains: `topology_mutating_movement_candidate`",
        "",
        "## Return To N04",
        "",
        f"- next probe: `{ret['next_probe']}`",
        f"- goal: {ret['probe_goal']}",
        f"- entry ceiling: `{ret['entry_ceiling']}`",
        f"- closed ceiling: `{ret['closed_ceiling']}`",
        "",
        "## Checks",
        "",
    ]
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The current supported ceiling is `topology_mutating_movement_candidate`. Native LGRC choice selection, RC identity collapse, semantic choice, agency, locomotion-like behavior, biological behavior, identity acceptance, inherited-N03 movement, and unrestricted movement remain blocked.",
            "",
            "## Command",
            "",
            f"```bash\n{COMMAND}\n```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_closeout()
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
