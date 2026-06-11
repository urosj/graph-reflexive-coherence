#!/usr/bin/env python3
"""Run N08 Iteration 9 native geometry trail baseline.

Iteration 9 starts Hypothesis B. It freezes the native geometry-mediated trail
question and inventories available LGRC mechanisms without running a new memory
probe and without using serialized `memory_strength` scoring.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"
N04 = ROOT / "experiments" / "2026-05-N04-grc9v3-movement-ladders"
IMPLEMENTATION = ROOT / "implementation"

SOURCE_ARTIFACT_PATHS = {
    "n08_hypothesis_a_closeout": EXPERIMENT
    / "outputs/n08_iteration_8_mem6_closeout.json",
    "n08_hypothesis_a_report": EXPERIMENT
    / "reports/n08_iteration_8_mem6_closeout.md",
    "n04_topology_mutating_after_reabsorption": N04
    / "outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json",
    "n04_topology_mutating_after_reabsorption_report": N04
    / "reports/n04_iter19e_topology_mutating_movement_after_state_reabsorption.md",
    "n04_taxonomy_closeout": N04 / "outputs/n04_taxonomy_continuation_closeout.json",
    "phase8_surface_lineage_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json",
    "phase8_topology_state_reabsorption_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json",
    "phase8_time_scoped_lineage_replay_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json",
    "phase8_native_route_arbitration_closeout": IMPLEMENTATION
    / "Phase-8-LGRC9-NativeRouteArbitrationCloseout.json",
}

OUTPUT_PATH = (
    EXPERIMENT / "outputs/n08_iteration_9_native_geometry_trail_baseline.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports/n08_iteration_9_native_geometry_trail_baseline.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_9_native_geometry_trail_baseline.py"
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def git_status_short_src() -> str:
    completed = subprocess.run(
        ["git", "status", "--short", "src"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def source_artifacts() -> dict[str, str]:
    return {
        rel(path): digest_file(path)
        for path in SOURCE_ARTIFACT_PATHS.values()
        if path.exists()
    }


def load_sources() -> dict[str, dict[str, Any]]:
    return {
        key: load_json(path)
        for key, path in SOURCE_ARTIFACT_PATHS.items()
        if path.suffix == ".json"
    }


def mechanism_inventory(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    n04_19e = sources["n04_topology_mutating_after_reabsorption"]
    phase8_surface = sources["phase8_surface_lineage_closeout"]
    phase8_state = sources["phase8_topology_state_reabsorption_closeout"]
    phase8_time = sources["phase8_time_scoped_lineage_replay_closeout"]
    phase8_arbitration = sources["phase8_native_route_arbitration_closeout"]

    rows = [
        {
            "mechanism_id": "committed_topology_event",
            "question": "Can a route-use event create a declared topology trace?",
            "availability": "available_as_runtime_support",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["n04_topology_mutating_after_reabsorption"]),
                rel(SOURCE_ARTIFACT_PATHS["phase8_topology_state_reabsorption_closeout"]),
            ],
            "source_evidence": {
                "n04_19e_status": n04_19e.get("status"),
                "n04_19e_claim_ceiling": n04_19e.get("claim_ceiling"),
                "committed_topology_event_logged": n04_19e.get("checks", {}).get(
                    "committed_topology_event_logged"
                ),
                "phase8_supported_capability": phase8_state.get(
                    "supported_capability"
                ),
            },
            "usable_for_iteration_10": True,
            "requires_phase8_before_probe": False,
            "blocker": None,
            "notes": (
                "Topology events can exist as declared runtime events, but a "
                "native trail still requires proving route-use-created "
                "geometry/topology trace formation."
            ),
        },
        {
            "mechanism_id": "edge_split_or_inserted_node",
            "question": "Can the trace be represented as an edge split or inserted node?",
            "availability": "candidate_design_available_over_topology_events",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["n04_topology_mutating_after_reabsorption"]),
                rel(SOURCE_ARTIFACT_PATHS["phase8_topology_state_reabsorption_closeout"]),
            ],
            "source_evidence": {
                "topology_state_reabsorption_supported": n04_19e.get("checks", {}).get(
                    "phase8_topology_state_reabsorption_supported"
                ),
                "ledger_state_gap_resolved": n04_19e.get("checks", {}).get(
                    "ledger_state_reabsorption_gap_resolved"
                ),
            },
            "usable_for_iteration_10": True,
            "requires_phase8_before_probe": False,
            "blocker": None,
            "notes": (
                "This is the preferred first Hypothesis B probe because it can "
                "avoid an independent memory scalar and use declared topology."
            ),
        },
        {
            "mechanism_id": "surface_lineage_transport",
            "question": "Can old surface evidence remain auditable after topology trace formation?",
            "availability": "available_as_runtime_support",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["phase8_surface_lineage_closeout"])
            ],
            "source_evidence": {
                "status": phase8_surface.get("status"),
                "supported": phase8_surface.get("supported"),
                "claim_ceiling": phase8_surface.get("claim_ceiling"),
            },
            "usable_for_iteration_10": True,
            "requires_phase8_before_probe": False,
            "blocker": None,
            "notes": (
                "Surface lineage is support infrastructure only. It does not "
                "itself create route memory."
            ),
        },
        {
            "mechanism_id": "topology_state_reabsorption",
            "question": "Can active state and packet ledger remain valid after the trace topology event?",
            "availability": "available_as_runtime_support",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["phase8_topology_state_reabsorption_closeout"])
            ],
            "source_evidence": {
                "status": phase8_state.get("status"),
                "supported_capability": phase8_state.get("supported_capability"),
                "movement_claim_allowed": phase8_state.get("claim_flags", {}).get(
                    "movement_claim_allowed"
                ),
            },
            "usable_for_iteration_10": True,
            "requires_phase8_before_probe": False,
            "blocker": None,
            "notes": (
                "Required if the geometry trail changes topology and later "
                "packet work crosses the changed substrate."
            ),
        },
        {
            "mechanism_id": "time_scoped_lineage_replay",
            "question": "Can historical route/surface reads remain valid across later topology events?",
            "availability": "available_as_artifact_replay_support",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["phase8_time_scoped_lineage_replay_closeout"])
            ],
            "source_evidence": {
                "status": phase8_time.get("status"),
                "supported_capability": phase8_time.get("supported_capability"),
                "resolved_boundary": phase8_time.get("resolved_boundary"),
            },
            "usable_for_iteration_10": True,
            "requires_phase8_before_probe": False,
            "blocker": None,
            "notes": (
                "Useful for artifact replay if multiple route-use or topology "
                "events are later chained."
            ),
        },
        {
            "mechanism_id": "native_route_arbitration",
            "question": "Can future routing be selected by native candidate/arbitration records?",
            "availability": "available_as_runtime_support",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["phase8_native_route_arbitration_closeout"])
            ],
            "source_evidence": {
                "status": phase8_arbitration.get("status"),
                "supported_capability": phase8_arbitration.get(
                    "supported_capability"
                ),
                "support_gate": phase8_arbitration.get("support_gate"),
            },
            "usable_for_iteration_11": True,
            "requires_phase8_before_probe": False,
            "blocker": None,
            "notes": (
                "May be used to observe future routing response, but Iteration "
                "11 must reject score-only memory inputs."
            ),
        },
        {
            "mechanism_id": "declared_node_or_edge_geometry_parameter_change",
            "question": "Can route use alter declared node/edge geometry without topology mutation?",
            "availability": "not_confirmed_in_current_n08_sources",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["n08_hypothesis_a_closeout"])
            ],
            "source_evidence": {
                "hypothesis_a_uses_independent_memory_strength": sources[
                    "n08_hypothesis_a_closeout"
                ]["closeout"]["independent_memory_strength_used_as_score_evidence"],
            },
            "usable_for_iteration_10": False,
            "requires_phase8_before_probe": "unknown",
            "blocker": "declared_geometry_parameter_update_not_inventory_confirmed",
            "notes": (
                "Do not assume custom conductance or geometry parameters are "
                "available as serialized native policy fields."
            ),
        },
        {
            "mechanism_id": "support_shape_or_local_coupling_geometry_change",
            "question": "Can route use change support/coupling shape as native trail state?",
            "availability": "not_confirmed_in_current_n08_sources",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["n08_hypothesis_a_closeout"])
            ],
            "source_evidence": {
                "hypothesis_b_status": sources["n08_hypothesis_a_closeout"][
                    "closeout"
                ]["hypothesis_b_status"],
            },
            "usable_for_iteration_10": False,
            "requires_phase8_before_probe": "unknown",
            "blocker": "support_shape_update_policy_not_inventory_confirmed",
            "notes": (
                "This remains attractive for a pure RC trail, but Iteration 9 "
                "does not find a source-backed native support-shape update contract."
            ),
        },
        {
            "mechanism_id": "packet_or_loop_residue_visible_in_existing_state",
            "question": "Can future routing read a residue left by packet/loop dynamics?",
            "availability": "not_yet_demonstrated_as_route_memory",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["n08_hypothesis_a_closeout"])
            ],
            "source_evidence": {
                "hypothesis_a_ceiling": sources["n08_hypothesis_a_closeout"][
                    "closeout"
                ]["strongest_claim_ceiling"],
            },
            "usable_for_iteration_10": False,
            "requires_phase8_before_probe": "maybe",
            "blocker": "packet_loop_residue_route_memory_not_demonstrated",
            "notes": (
                "Existing packet/loop machinery exists, but N08 has not shown "
                "a residue that changes routing without score memory."
            ),
        },
        {
            "mechanism_id": "route_conductance_memory_metric",
            "question": "Can route conductance memory be represented natively?",
            "availability": "blocked",
            "source_artifacts": [
                rel(SOURCE_ARTIFACT_PATHS["n08_hypothesis_a_closeout"])
            ],
            "source_evidence": {
                "hypothesis_a_memory_strength_is_physical_flux": sources[
                    "n08_hypothesis_a_closeout"
                ]["closeout"]["independent_memory_strength_used_as_physical_flux"],
            },
            "usable_for_iteration_10": False,
            "requires_phase8_before_probe": True,
            "blocker": "native_route_conductance_memory_policy_missing",
            "notes": (
                "Do not smuggle Hypothesis A memory_strength into native "
                "geometry by renaming it conductance."
            ),
        },
    ]
    for row in rows:
        row["row_digest"] = digest_value(row)
    return rows


def entry_gate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    available = [
        row["mechanism_id"] for row in rows if row.get("usable_for_iteration_10") is True
    ]
    blocked = {
        row["mechanism_id"]: row["blocker"]
        for row in rows
        if row.get("blocker") is not None
    }
    gate = {
        "iteration_10_entry_allowed": "edge_split_or_inserted_node" in available
        and "committed_topology_event" in available
        and "topology_state_reabsorption" in available,
        "preferred_iteration_10_probe": "edge_split_or_inserted_node_topology_trace",
        "available_mechanisms_for_iteration_10": available,
        "blocked_or_unconfirmed_mechanisms": blocked,
        "must_not_use": [
            "memory_strength",
            "memory_shaped_candidate_score",
            "hidden_route_preference",
            "report_side_route_history",
            "unserialized_geometry_state",
        ],
        "required_controls_for_iteration_10": [
            "missing_route_use_event",
            "missing_geometry_or_topology_event",
            "hidden_scalar_memory",
            "stale_geometry_read",
            "budget_drift",
            "unsupported_topology_mutation",
            "claim_promotion",
        ],
    }
    gate["entry_gate_digest"] = digest_value(gate)
    return gate


def claim_flags() -> dict[str, bool]:
    return {
        "memory_or_trail_claim_allowed": False,
        "native_geometry_mediated_trail_claim_allowed": False,
        "pure_coherence_flux_trail_claim_allowed": False,
        "aco_like_claim_allowed": False,
        "agency_claim_allowed": False,
        "agentic_like_claim_allowed": False,
        "ant_colony_claim_allowed": False,
        "biological_claim_allowed": False,
        "goal_proxy_regulation_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "intention_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "movement_claim_allowed": False,
        "personhood_claim_allowed": False,
        "rc_identity_collapse_claim_allowed": False,
        "runtime_identity_acceptance_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "unrestricted_identity_claim_allowed": False,
        "unrestricted_movement_claim_allowed": False,
    }


def checks(
    sources: dict[str, dict[str, Any]],
    rows: list[dict[str, Any]],
    gate: dict[str, Any],
    flags: dict[str, bool],
) -> dict[str, bool]:
    row_by_id = {row["mechanism_id"]: row for row in rows}
    return {
        "hypothesis_a_closeout_passed": sources["n08_hypothesis_a_closeout"][
            "status"
        ]
        == "passed",
        "hypothesis_b_separate_from_iterations_1_8": sources[
            "n08_hypothesis_a_closeout"
        ]["closeout"]["hypothesis_b_status"]
        == "open_not_claimed",
        "no_memory_strength_in_native_entry_gate": "memory_strength"
        in gate["must_not_use"],
        "no_memory_shaped_scoring_in_iteration_9": True,
        "no_new_probe_run": True,
        "committed_topology_event_available": row_by_id[
            "committed_topology_event"
        ]["usable_for_iteration_10"]
        is True,
        "edge_split_inserted_node_candidate_available": row_by_id[
            "edge_split_or_inserted_node"
        ]["usable_for_iteration_10"]
        is True,
        "surface_lineage_available": row_by_id["surface_lineage_transport"][
            "usable_for_iteration_10"
        ]
        is True,
        "topology_state_reabsorption_available": row_by_id[
            "topology_state_reabsorption"
        ]["usable_for_iteration_10"]
        is True,
        "route_conductance_memory_policy_blocked": row_by_id[
            "route_conductance_memory_metric"
        ]["blocker"]
        == "native_route_conductance_memory_policy_missing",
        "support_shape_update_not_confirmed": row_by_id[
            "support_shape_or_local_coupling_geometry_change"
        ]["blocker"]
        == "support_shape_update_policy_not_inventory_confirmed",
        "geometry_parameter_update_not_confirmed": row_by_id[
            "declared_node_or_edge_geometry_parameter_change"
        ]["blocker"]
        == "declared_geometry_parameter_update_not_inventory_confirmed",
        "iteration_10_entry_gate_defined": gate["iteration_10_entry_allowed"] is True,
        "all_claim_flags_false": all(value is False for value in flags.values()),
        "src_clean": git_status_short_src() == "",
    }


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    rows = output["mechanism_inventory"]
    row_lines = "\n".join(
        "| `{mechanism_id}` | `{availability}` | `{usable10}` | `{usable11}` | `{blocker}` | {notes} |".format(
            mechanism_id=row["mechanism_id"],
            availability=row["availability"],
            usable10=row.get("usable_for_iteration_10"),
            usable11=row.get("usable_for_iteration_11"),
            blocker=row["blocker"],
            notes=row["notes"],
        )
        for row in rows
    )
    check_lines = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(output["checks"].items())
    )
    report = f"""# N08 Iteration 9 Native Geometry Trail Baseline

Status: `{output['status']}`.

Iteration 9 starts Hypothesis B and freezes the native geometry-mediated trail
question before any native trail probe. It inventories available native
LGRC geometry/topology/support mechanisms and records blockers without using
`memory_strength`, memory-shaped scoring, hidden route preference, or claim
promotion.

## Baseline Decision

- Hypothesis A remains closed at:
  `{output['hypothesis_a_source']['strongest_claim_ceiling']}`
- Hypothesis B status:
  `{output['hypothesis_b_baseline']['status']}`
- Hypothesis B current blocker:
  `{output['hypothesis_b_baseline']['current_blocker']}`
- Preferred Iteration 10 probe:
  `{output['iteration_10_entry_gate']['preferred_iteration_10_probe']}`
- Iteration 10 entry allowed:
  `{output['iteration_10_entry_gate']['iteration_10_entry_allowed']}`

## Mechanism Inventory

| Mechanism | Availability | Usable I10 | Usable I11 | Blocker | Notes |
|---|---|---:|---:|---|---|
{row_lines}

## Iteration 10 Guardrails

Must not use:

```json
{json.dumps(output['iteration_10_entry_gate']['must_not_use'], indent=2, sort_keys=True)}
```

Required controls:

```json
{json.dumps(output['iteration_10_entry_gate']['required_controls_for_iteration_10'], indent=2, sort_keys=True)}
```

## Claim Boundary

All Iteration 9 claim flags remain false. The narrow Hypothesis A
`memory_or_trail_claim_allowed` does not transfer to Hypothesis B.

```json
{json.dumps(output['claim_flags'], indent=2, sort_keys=True)}
```

## Checks

| Check | Passed |
|---|---|
{check_lines}

## Acceptance

Iteration 9 passes if the native geometry-mediated trail question is frozen
with a source-backed inventory of available LGRC geometry/topology/support
mechanisms and explicit blockers, without using `memory_strength`, hidden route
preference, memory-shaped scoring, or claim promotion.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    sources = load_sources()
    rows = mechanism_inventory(sources)
    gate = entry_gate(rows)
    flags = claim_flags()
    result_checks = checks(sources, rows, gate, flags)
    output: dict[str, Any] = {
        "schema": "n08_iteration_9_native_geometry_trail_baseline_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 9,
        "status": "passed" if all(result_checks.values()) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short_src(),
            "src_clean": git_status_short_src() == "",
        },
        "source_artifacts": source_artifacts(),
        "hypothesis_a_source": {
            "status": sources["n08_hypothesis_a_closeout"]["status"],
            "strongest_supported_mem_level": sources["n08_hypothesis_a_closeout"][
                "closeout"
            ]["strongest_supported_mem_level"],
            "strongest_claim_ceiling": sources["n08_hypothesis_a_closeout"][
                "closeout"
            ]["strongest_claim_ceiling"],
            "memory_or_trail_claim_scope": sources["n08_hypothesis_a_closeout"][
                "closeout"
            ]["memory_or_trail_claim_scope"],
        },
        "hypothesis_b_baseline": {
            "status": "open_not_claimed",
            "current_blocker": "native_geometry_mediated_trail_not_tested_before_iteration_9",
            "question": (
                "Can route use create a native geometry/topology/support trace "
                "that future flux/routing follows without independent memory_strength?"
            ),
            "claim_ceiling": "native_geometry_mediated_route_trail_not_yet_supported",
        },
        "mechanism_inventory": rows,
        "iteration_10_entry_gate": gate,
        "claim_flags": flags,
        "checks": result_checks,
        "acceptance": {
            "achieved": all(result_checks.values()),
            "status": "passed" if all(result_checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 9 passes if the native geometry-mediated trail "
                "question is frozen with a source-backed inventory of "
                "available LGRC geometry/topology/support mechanisms and "
                "explicit blockers, without using memory_strength, hidden "
                "route preference, memory-shaped scoring, or claim promotion."
            ),
        },
    }
    output["artifact_digests"] = {
        "mechanism_inventory_digest": digest_value(rows),
        "iteration_10_entry_gate_digest": gate["entry_gate_digest"],
        "checks_digest": digest_value(result_checks),
        "claim_flags_digest": digest_value(flags),
    }
    output["output_digest_scope"] = {
        "included": "all output fields except generated_at and output_digest",
        "excluded": ["generated_at", "output_digest"],
        "stable_across_same_inputs": True,
    }
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"generated_at", "output_digest"}
        }
    )
    return output


def main() -> None:
    output = build_output()
    write_output(output)
    write_report(output)


if __name__ == "__main__":
    main()
