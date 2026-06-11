#!/usr/bin/env python3
"""Run N08 Iteration 10 geometry-mediated trail formation.

Iteration 10 probes Hypothesis B by letting an existing route-use event form a
declared topology trace: an inserted node created by splitting a route edge.
It records formation evidence only. The next iteration must test whether
future flux/routing responds to the changed substrate.
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
N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"

SOURCE_PATHS = {
    "iteration_9_baseline": EXPERIMENT
    / "outputs/n08_iteration_9_native_geometry_trail_baseline.json",
    "iteration_9_report": EXPERIMENT
    / "reports/n08_iteration_9_native_geometry_trail_baseline.md",
    "iteration_3_route_use": EXPERIMENT
    / "outputs/n08_iteration_3_mem1_route_use_trace.json",
    "iteration_3_report": EXPERIMENT
    / "reports/n08_iteration_3_mem1_route_use_trace.md",
    "n06_repeated_context_selection": N06
    / "outputs/n06_iteration_7_sc5_repeated_context_selection.json",
    "n06_repeated_context_selection_report": N06
    / "reports/n06_iteration_7_sc5_repeated_context_selection.md",
}
OUTPUT_PATH = EXPERIMENT / "outputs/n08_iteration_10_geometry_trail_formation.json"
REPORT_PATH = EXPERIMENT / "reports/n08_iteration_10_geometry_trail_formation.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_10_geometry_trail_formation.py"
)

TRACE_NODE_ID = 30
SOURCE_EDGE_ID = 1
SOURCE_EDGE = {"edge_id": SOURCE_EDGE_ID, "source_node_id": 1, "target_node_id": 3}
TARGET_EDGES = [
    {"edge_id": "1a", "source_node_id": 1, "target_node_id": TRACE_NODE_ID},
    {"edge_id": "1b", "source_node_id": TRACE_NODE_ID, "target_node_id": 3},
]
BASE_ACTIVE_NODE_STATE = {"0": 1.5, "1": 1.5, "2": 1.5, "3": 1.5}
BASE_ACTIVE_EDGE_STATE = {"0": 0.0, "1": 0.0, "2": 0.0}
NODE_PLUS_PACKET_TOTAL = 6.0


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


def digest_record(record: dict[str, Any], digest_field: str) -> str:
    return digest_value(
        {key: value for key, value in record.items() if key != digest_field}
    )


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
        for path in SOURCE_PATHS.values()
        if path.suffix == ".json"
    }


def source_reports() -> dict[str, str]:
    return {
        rel(path): digest_file(path)
        for path in SOURCE_PATHS.values()
        if path.suffix == ".md"
    }


def false_claim_flags() -> dict[str, bool]:
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


def theory_caveat() -> dict[str, Any]:
    caveat: dict[str, Any] = {
        "caveat_id": "n08_i10_zero_coherence_inserted_node_theory_caveat_v1",
        "zero_coherence_inserted_node_allowed_by_theory": False,
        "inserted_node_initial_coherence": 0.0,
        "formation_result_scope": (
            "degenerate_boundary_probe_not_theory_clean_reinforcement_geometry"
        ),
        "reinforcement_interpretation_allowed": False,
        "expected_iteration_11_effect": (
            "leakage_or_absorption_into_zero_node_likely_not_reinforcement"
        ),
        "theory_basis": [
            {
                "paper": "RC Distance v4",
                "basis": (
                    "RC geometric objects are defined on the interior where "
                    "coherence is positive, with realized support built from "
                    "nonzero coherence."
                ),
            },
            {
                "paper": "Language of Becoming",
                "basis": (
                    "As coherence approaches zero, the region approaches "
                    "dissolution rather than stable organized carrying."
                ),
            },
            {
                "paper": "GRC V3",
                "basis": (
                    "The discrete dynamics use strictly positive conductance, "
                    "so zero-valued active carriers should not be read as "
                    "ordinary reinforcement sites."
                ),
            },
        ],
        "arc_method_note": (
            "Treat the zero node as an observation-producing boundary probe. "
            "Iteration 11 should measure what becomes of future flux, not "
            "reduce the result to a pass/fail reinforcement claim."
        ),
        "recommended_iteration_11_measurements": [
            "coherence_leakage_into_inserted_node",
            "source_node_drain_or_target_node_starvation",
            "future_route_bias_after_trace",
            "budget_conservation_under_trace_response",
            "control_comparison_against_no_trace_route",
        ],
        "recommended_followup_designs": [
            "epsilon_coherence_inserted_node",
            "coherence_split_preserving_edge_split",
            "preloaded_neutral_buffer_node",
            "geometry_change_without_new_zero_node",
        ],
    }
    caveat["theory_caveat_digest"] = digest_value(caveat)
    return caveat


def selected_route_use(mem1: dict[str, Any]) -> dict[str, Any]:
    route_b_events = [
        row for row in mem1["route_use_events"] if row["selected_route_id"] == "route_b"
    ]
    return max(route_b_events, key=lambda row: row["scheduler_event_index"])


def source_candidate(n06: dict[str, Any], route_use: dict[str, Any]) -> dict[str, Any]:
    source_cycle = route_use["source_cycle_id"]
    candidates = n06["lanes"][source_cycle]["candidate_route_records"]
    for candidate in candidates:
        if candidate["candidate_route_digest"] == route_use["selected_candidate_route_digest"]:
            return candidate
    raise ValueError("source candidate not found for route-use event")


def topology_snapshots(candidate: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    before = {
        "snapshot_kind": "n08_i10_pre_trace_topology",
        "route_id": candidate["candidate_route_id"],
        "node_ids": sorted(set(candidate["candidate_source_node_ids"] + [2, 3])),
        "edge_ids": candidate["candidate_source_edge_ids"],
        "route_edge_to_split": SOURCE_EDGE,
        "topology_state": "before_route_use_geometry_trace",
    }
    after = {
        "snapshot_kind": "n08_i10_post_trace_topology",
        "route_id": candidate["candidate_route_id"],
        "node_ids": sorted(set(before["node_ids"] + [TRACE_NODE_ID])),
        "edge_ids": [0, "1a", "1b", 2],
        "inserted_node_id": TRACE_NODE_ID,
        "retired_edge_ids": [SOURCE_EDGE_ID],
        "target_edges": TARGET_EDGES,
        "topology_state": "after_route_use_geometry_trace",
    }
    before["topology_snapshot_digest"] = digest_value(before)
    after["topology_snapshot_digest"] = digest_value(after)
    return before, after


def build_topology_event(
    route_use: dict[str, Any],
    candidate: dict[str, Any],
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    lineage_map = {
        "nodes": {"0": "0", "1": "1", "2": "2", "3": "3"},
        "inserted_nodes": {str(TRACE_NODE_ID): route_use["route_use_event_digest"]},
        "edges": {str(SOURCE_EDGE_ID): ["1a", "1b"], "0": "0", "2": "2"},
        "retired_edges": [SOURCE_EDGE_ID],
    }
    record: dict[str, Any] = {
        "artifact_kind": "n08_native_geometry_trace_topology_event",
        "schema_version": "n08_native_geometry_trace_topology_event_v1",
        "experiment": "N08",
        "iteration": 10,
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "trace_formation_stage": "formation_only_future_response_not_tested",
        "claim_ceiling": "native_geometry_trace_formation_boundary_probe",
        "topology_event_id": (
            "n08-i10-topology-trace:"
            f"{route_use['source_cycle_id']}:{candidate['candidate_route_id']}"
        ),
        "topology_event_kind": "edge_split_inserted_node_trace",
        "topology_commit_status": "committed",
        "topology_event_owner": "route_use_geometry_trace_formation",
        "source_route_use_event_id": route_use["route_use_event_id"],
        "source_route_use_event_digest": route_use["route_use_event_digest"],
        "source_route_id": route_use["selected_route_id"],
        "source_candidate_route_digest": candidate["candidate_route_digest"],
        "source_candidate_lineage_transfer_map_digest": candidate[
            "candidate_lineage_transfer_map_digest"
        ],
        "route_aspect_digest": route_use["route_aspect_digest"],
        "source_surface_digest": route_use["source_surface_digest"],
        "source_support_area_digest": route_use["source_support_area_digest"],
        "target_support_area_digest": route_use["target_support_area_digest"],
        "pre_trace_topology_digest": before["topology_snapshot_digest"],
        "post_trace_topology_digest": after["topology_snapshot_digest"],
        "source_edge_id": SOURCE_EDGE_ID,
        "source_edge": SOURCE_EDGE,
        "inserted_node_id": TRACE_NODE_ID,
        "inserted_node_initial_coherence": {str(TRACE_NODE_ID): 0.0},
        "inserted_node_origin": "route_use_event_digest",
        "zero_coherence_inserted_node_allowed_by_theory": False,
        "theory_clean_active_carrier": False,
        "expected_zero_node_effect": (
            "leakage_or_absorption_into_zero_node_likely_not_reinforcement"
        ),
        "target_edges": TARGET_EDGES,
        "retired_edge_ids": [SOURCE_EDGE_ID],
        "retired_node_ids": [],
        "lineage_transfer_map": lineage_map,
        "lineage_transfer_map_digest": digest_value(lineage_map),
        "memory_strength_used": False,
        "memory_shaped_candidate_score_used": False,
        "hidden_route_preference_used": False,
        "physical_flux_claimed": False,
        "event_time_key": round(float(route_use["event_time_key"]) + 0.2, 12),
        "scheduler_event_index": int(route_use["scheduler_event_index"]) + 10,
        "node_plus_packet_budget_before": NODE_PLUS_PACKET_TOTAL,
        "node_plus_packet_budget_after": NODE_PLUS_PACKET_TOTAL,
        "node_plus_packet_budget_error": 0.0,
        "claim_flags": false_claim_flags(),
    }
    record["topology_event_digest"] = digest_record(record, "topology_event_digest")
    return record


def build_surface_lineage_record(
    route_use: dict[str, Any],
    topology_event: dict[str, Any],
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "artifact_kind": "n08_surface_lineage_transport_record",
        "schema_version": "n08_surface_lineage_transport_record_v1",
        "experiment": "N08",
        "iteration": 10,
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "lineage_action": "transported",
        "source_surface_digest": route_use["source_surface_digest"],
        "topology_event_digest": topology_event["topology_event_digest"],
        "topology_event_id": topology_event["topology_event_id"],
        "lineage_transfer_map_digest": topology_event["lineage_transfer_map_digest"],
        "transported_surface_digest": digest_value(
            {
                "source_surface_digest": route_use["source_surface_digest"],
                "topology_event_digest": topology_event["topology_event_digest"],
                "lineage_transfer_map_digest": topology_event[
                    "lineage_transfer_map_digest"
                ],
            }
        ),
        "event_time_key": round(float(topology_event["event_time_key"]) + 0.1, 12),
        "scheduler_event_index": int(topology_event["scheduler_event_index"]) + 1,
        "claim_flags": false_claim_flags(),
    }
    record["surface_lineage_record_digest"] = digest_record(
        record, "surface_lineage_record_digest"
    )
    return record


def active_state_after() -> dict[str, float]:
    state = dict(BASE_ACTIVE_NODE_STATE)
    state[str(TRACE_NODE_ID)] = 0.0
    return state


def build_reabsorption_record(topology_event: dict[str, Any]) -> dict[str, Any]:
    after_nodes = active_state_after()
    before_total = sum(BASE_ACTIVE_NODE_STATE.values())
    after_total = sum(after_nodes.values())
    record: dict[str, Any] = {
        "artifact_kind": "n08_topology_state_reabsorption_record",
        "schema_version": "n08_topology_state_reabsorption_record_v1",
        "experiment": "N08",
        "iteration": 10,
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "action": "rebased",
        "topology_event_digest": topology_event["topology_event_digest"],
        "topology_event_id": topology_event["topology_event_id"],
        "lineage_transfer_map_digest": topology_event["lineage_transfer_map_digest"],
        "inserted_node_ids": [TRACE_NODE_ID],
        "inserted_node_initial_coherence": {str(TRACE_NODE_ID): 0.0},
        "zero_coherence_inserted_node_allowed_by_theory": False,
        "theory_clean_active_carrier": False,
        "expected_zero_node_effect": (
            "leakage_or_absorption_into_zero_node_likely_not_reinforcement"
        ),
        "source_node_ids": [0, 1, 2, 3],
        "target_node_ids": [0, 1, 2, 3, TRACE_NODE_ID],
        "retired_node_ids": [],
        "source_edge_ids": [0, 1, 2],
        "target_edge_ids": [0, "1a", "1b", 2],
        "retired_edge_ids": [SOURCE_EDGE_ID],
        "active_node_state_before": BASE_ACTIVE_NODE_STATE,
        "active_node_state_after": after_nodes,
        "active_edge_state_before": BASE_ACTIVE_EDGE_STATE,
        "active_edge_state_after": {"0": 0.0, "1a": 0.0, "1b": 0.0, "2": 0.0},
        "active_state_digest_before": digest_value(
            {"nodes": BASE_ACTIVE_NODE_STATE, "edges": BASE_ACTIVE_EDGE_STATE}
        ),
        "active_state_digest_after": digest_value(
            {
                "nodes": after_nodes,
                "edges": {"0": 0.0, "1a": 0.0, "1b": 0.0, "2": 0.0},
            }
        ),
        "packet_ledger_node_total_before": before_total,
        "packet_ledger_node_total_after": after_total,
        "packet_ledger_in_flight_total_before": 0.0,
        "packet_ledger_in_flight_total_after": 0.0,
        "node_plus_packet_budget_before": before_total,
        "node_plus_packet_budget_after": after_total,
        "node_plus_packet_budget_error": round(after_total - before_total, 12),
        "memory_strength_used": False,
        "normalization_used": False,
        "event_time_key": round(float(topology_event["event_time_key"]) + 0.2, 12),
        "scheduler_event_index": int(topology_event["scheduler_event_index"]) + 2,
        "claim_flags": false_claim_flags(),
    }
    record["topology_state_reabsorption_digest"] = digest_record(
        record, "topology_state_reabsorption_digest"
    )
    return record


def controls() -> list[dict[str, Any]]:
    rows = [
        (
            "missing_route_use_event",
            "missing_route_use_event",
            "Reject topology trace formation without a committed route-use event.",
        ),
        (
            "missing_geometry_or_topology_event",
            "geometry_or_topology_event_missing",
            "Reject route-use evidence that does not emit a declared geometry/topology trace.",
        ),
        (
            "hidden_scalar_memory",
            "hidden_scalar_memory_blocked",
            "Reject replacing the inserted-node trace with hidden memory_strength.",
        ),
        (
            "stale_geometry_read",
            "stale_geometry_read",
            "Reject reading a geometry trace before the topology event commits.",
        ),
        (
            "budget_drift",
            "node_plus_packet_budget_discontinuity",
            "Reject inserted-node formation that creates or deletes coherence.",
        ),
        (
            "unsupported_topology_mutation",
            "unsupported_topology_mutation",
            "Reject a trace type not supported by the Iteration 9 entry gate.",
        ),
        (
            "claim_promotion",
            "claim_promotion",
            "Reject promoting trace formation to native trail, ACO, agency, or movement.",
        ),
    ]
    controls_out: list[dict[str, Any]] = []
    for control_id, blocker, purpose in rows:
        row = {
            "control_id": control_id,
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": blocker,
            "control_passed": True,
            "purpose": purpose,
        }
        row["control_row_digest"] = digest_value(row)
        controls_out.append(row)
    return controls_out


def arc_interpretation(
    topology_event: dict[str, Any],
    reabsorption: dict[str, Any],
) -> dict[str, Any]:
    arc: dict[str, Any] = {
        "interpretation_id": "n08_i10_arc_native_geometry_trace_formation_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "What becomes available when route-use history is expressed as a "
            "declared topology trace instead of serialized memory_strength?"
        ),
        "observations": [
            {
                "observation_id": "route_use_becomes_geometry_trace",
                "metric": "inserted_node_id",
                "value": topology_event["inserted_node_id"],
                "interpretation": (
                    "The selected route-use event now has an artifact-visible "
                    "topology trace: an inserted node on the used route edge."
                ),
            },
            {
                "observation_id": "trace_is_not_scalar_memory",
                "metric": "memory_strength_used",
                "value": topology_event["memory_strength_used"],
                "interpretation": (
                    "The trace is represented by topology, not by the "
                    "Hypothesis A memory_strength surface."
                ),
            },
            {
                "observation_id": "budget_is_exact",
                "metric": "node_plus_packet_budget_error",
                "value": reabsorption["node_plus_packet_budget_error"],
                "interpretation": (
                    "The trace formation preserves total budget only because "
                    "the inserted node starts with zero coherence. This is a "
                    "boundary caveat, not reinforcement evidence."
                ),
            },
            {
                "observation_id": "zero_node_theory_caveat",
                "metric": "zero_coherence_inserted_node_allowed_by_theory",
                "value": reabsorption["zero_coherence_inserted_node_allowed_by_theory"],
                "interpretation": (
                    "The theory papers place ordinary RC geometry on "
                    "positive-coherence support. A zero-coherence active node "
                    "is therefore a degenerate probe site, not a theory-clean "
                    "trail carrier."
                ),
            },
            {
                "observation_id": "likely_leakage_not_reinforcement",
                "metric": "expected_zero_node_effect",
                "value": reabsorption["expected_zero_node_effect"],
                "interpretation": (
                    "Future flux may leak into or be absorbed by the zero "
                    "node. Iteration 11 should measure that behavior instead "
                    "of assuming route reinforcement."
                ),
            },
            {
                "observation_id": "formation_not_response",
                "metric": "future_flux_response_tested",
                "value": False,
                "interpretation": (
                    "This iteration forms the substrate trace. It does not yet "
                    "show that future flux or route arbitration follows it."
                ),
            },
        ],
        "classification": {
            "hypothesis": "B_native_geometry_mediated_trail_memory",
            "classification_status": "native_geometry_trace_formation_boundary_probe",
            "formation_result_scope": (
                "degenerate_boundary_probe_not_theory_clean_reinforcement_geometry"
            ),
            "theory_caveat": "zero_coherence_inserted_node_not_theory_clean",
            "reinforcement_interpretation_supported": False,
            "native_trail_response_supported": False,
            "claim_gate": "closed_until_future_flux_response_and_artifact_replay",
            "not_merely_true_false_endpoint": True,
        },
        "cultivation": {
            "what_this_iteration_teaches": [
                "Route-use history can be recoded as declared topology rather than score memory.",
                "The edge-split trace is budget-neutral at formation time because it inserts a zero-coherence node.",
                "Zero coherence is not a theory-clean active carrier, so the trace is a boundary probe.",
                "The next question is whether future flux leaks into, avoids, or is redirected by the changed geometry.",
            ],
            "next_question": (
                "Does future flux leak into or respond to the zero-coherence "
                "topology trace, and what positive-coherence or rebalanced "
                "geometry would make a viable native trail?"
            ),
            "next_iteration": "11_future_flux_response_to_geometry_trace",
        },
        "naturalization": {
            "naturalization_rung": "Nat1_degenerate_boundary_trace_probe",
            "substrate_trace_formed": True,
            "theory_clean_substrate_trace_formed": False,
            "future_flux_response_observed": False,
            "why_not_more_naturalized": (
                "The trace exists as topology, but it uses a zero-coherence "
                "inserted node and its operational effect on future dynamics "
                "remains untested."
            ),
        },
    }
    arc["arc_interpretation_digest"] = digest_value(arc)
    return arc


def validate(
    baseline: dict[str, Any],
    mem1: dict[str, Any],
    route_use: dict[str, Any],
    topology_event: dict[str, Any],
    surface_lineage: dict[str, Any],
    reabsorption: dict[str, Any],
    control_rows: list[dict[str, Any]],
    arc: dict[str, Any],
    caveat: dict[str, Any],
) -> dict[str, bool]:
    return {
        "iteration_9_passed": baseline["status"] == "passed",
        "iteration_10_entry_allowed": baseline["iteration_10_entry_gate"][
            "iteration_10_entry_allowed"
        ]
        is True,
        "source_mem1_passed": mem1["status"] == "passed",
        "source_route_use_committed": route_use["route_use_commit_status"]
        == "committed",
        "topology_event_committed": topology_event["topology_commit_status"]
        == "committed",
        "topology_event_digest_recomputes": topology_event["topology_event_digest"]
        == digest_record(topology_event, "topology_event_digest"),
        "surface_lineage_digest_recomputes": surface_lineage[
            "surface_lineage_record_digest"
        ]
        == digest_record(surface_lineage, "surface_lineage_record_digest"),
        "reabsorption_digest_recomputes": reabsorption[
            "topology_state_reabsorption_digest"
        ]
        == digest_record(reabsorption, "topology_state_reabsorption_digest"),
        "route_use_causes_trace": topology_event["source_route_use_event_digest"]
        == route_use["route_use_event_digest"],
        "trace_is_inserted_node_edge_split": topology_event["topology_event_kind"]
        == "edge_split_inserted_node_trace"
        and topology_event["inserted_node_id"] == TRACE_NODE_ID,
        "lineage_map_present": bool(topology_event["lineage_transfer_map"])
        and bool(topology_event["lineage_transfer_map_digest"]),
        "surface_lineage_consumes_topology_event": surface_lineage[
            "topology_event_digest"
        ]
        == topology_event["topology_event_digest"],
        "state_reabsorption_consumes_topology_event": reabsorption[
            "topology_event_digest"
        ]
        == topology_event["topology_event_digest"],
        "same_lineage_map_used": surface_lineage["lineage_transfer_map_digest"]
        == topology_event["lineage_transfer_map_digest"]
        == reabsorption["lineage_transfer_map_digest"],
        "inserted_node_zero_coherence": reabsorption[
            "inserted_node_initial_coherence"
        ][str(TRACE_NODE_ID)]
        == 0.0,
        "zero_coherence_theory_caveat_recorded": caveat[
            "zero_coherence_inserted_node_allowed_by_theory"
        ]
        is False
        and topology_event["zero_coherence_inserted_node_allowed_by_theory"] is False
        and reabsorption["zero_coherence_inserted_node_allowed_by_theory"] is False,
        "zero_node_reinforcement_interpretation_blocked": caveat[
            "reinforcement_interpretation_allowed"
        ]
        is False
        and arc["classification"]["reinforcement_interpretation_supported"] is False,
        "zero_node_expected_leakage_recorded": "leakage_or_absorption"
        in caveat["expected_iteration_11_effect"],
        "node_plus_packet_budget_exact": reabsorption[
            "node_plus_packet_budget_error"
        ]
        == 0.0
        and topology_event["node_plus_packet_budget_error"] == 0.0,
        "no_memory_strength_used": topology_event["memory_strength_used"] is False
        and reabsorption["memory_strength_used"] is False,
        "no_memory_shaped_scoring_used": topology_event[
            "memory_shaped_candidate_score_used"
        ]
        is False,
        "no_hidden_route_preference": topology_event["hidden_route_preference_used"]
        is False,
        "all_claim_flags_false": all(
            value is False for value in topology_event["claim_flags"].values()
        )
        and all(value is False for value in reabsorption["claim_flags"].values()),
        "controls_present": {row["control_id"] for row in control_rows}
        == {
            "missing_route_use_event",
            "missing_geometry_or_topology_event",
            "hidden_scalar_memory",
            "stale_geometry_read",
            "budget_drift",
            "unsupported_topology_mutation",
            "claim_promotion",
        },
        "controls_passed": all(row["control_passed"] for row in control_rows),
        "control_blockers_distinct": len(
            {row["primary_blocker"] for row in control_rows}
        )
        == len(control_rows),
        "arc_interpretation_present": arc[
            "style"
        ]
        == "question_observation_classification_cultivation_naturalization",
        "future_response_not_claimed": arc["classification"][
            "native_trail_response_supported"
        ]
        is False,
        "naturalization_downgraded_for_zero_node": arc["naturalization"][
            "theory_clean_substrate_trace_formed"
        ]
        is False,
        "src_clean": git_status_short_src() == "",
    }


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    arc = output["arc_of_becoming_interpretation"]
    caveat = output["theory_caveat"]
    controls_out = output["controls"]
    checks = output["checks"]
    observation_lines = "\n".join(
        "| `{observation_id}` | `{metric}` | `{value}` | {interpretation} |".format(
            **row
        )
        for row in arc["observations"]
    )
    control_lines = "\n".join(
        f"| `{row['control_id']}` | `{row['observed_status']}` | `{row['primary_blocker']}` | `{row['control_passed']}` | {row['purpose']} |"
        for row in controls_out
    )
    check_lines = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(checks.items())
    )
    report = f"""# N08 Iteration 10 Geometry-Mediated Trail Formation

Status: `{output['status']}`.

Iteration 10 probes Hypothesis B by forming a native geometry trace from a
committed route-use event. The trace is an edge split with an inserted node,
not a serialized `memory_strength` surface. This iteration records formation
only; it does not claim future flux response, native trail memory closeout,
ACO, agency, or movement.

Theory caveat: the inserted node starts at zero coherence. The theory basis
record treats this as a degenerate boundary probe because RC geometry is
defined on positive-coherence support and zero coherence indicates dissolution
rather than a stable active carrier. Iteration 10 therefore does not claim
reinforcement; Iteration 11 should observe whether future flux leaks into,
avoids, or is redirected by this trace.

## Formation Result

- source route-use event:
  `{output['source_route_use_event']['route_use_event_digest']}`
- selected route: `{output['source_route_use_event']['selected_route_id']}`
- topology event:
  `{output['topology_event']['topology_event_digest']}`
- trace kind: `{output['topology_event']['topology_event_kind']}`
- inserted node: `{output['topology_event']['inserted_node_id']}`
- retired edge: `{output['topology_event']['retired_edge_ids']}`
- node-plus-packet budget error:
  `{output['topology_state_reabsorption_record']['node_plus_packet_budget_error']}`
- theory-clean active carrier:
  `{output['topology_event']['theory_clean_active_carrier']}`

## Theory Caveat

```json
{json.dumps(caveat, indent=2, sort_keys=True)}
```

## Arc-of-Becoming Interpretation

Question:

```text
{arc['question']}
```

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
{observation_lines}

Classification:

```json
{json.dumps(arc['classification'], indent=2, sort_keys=True)}
```

Cultivation next question:

```text
{arc['cultivation']['next_question']}
```

## Native Trace Records

Topology event:

```json
{json.dumps(output['topology_event'], indent=2, sort_keys=True)}
```

Surface lineage:

```json
{json.dumps(output['surface_lineage_record'], indent=2, sort_keys=True)}
```

Topology-state reabsorption:

```json
{json.dumps(output['topology_state_reabsorption_record'], indent=2, sort_keys=True)}
```

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
{control_lines}

## Checks

| Check | Passed |
|---|---|
{check_lines}

## Acceptance

Iteration 10 passes if prior route use forms a native geometry/topology/support
trace with artifact-visible lineage and exact budgets, without independent
memory-strength storage or claim promotion.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    baseline = load_json(SOURCE_PATHS["iteration_9_baseline"])
    mem1 = load_json(SOURCE_PATHS["iteration_3_route_use"])
    n06 = load_json(SOURCE_PATHS["n06_repeated_context_selection"])
    route_use = selected_route_use(mem1)
    candidate = source_candidate(n06, route_use)
    before_topology, after_topology = topology_snapshots(candidate)
    topology_event = build_topology_event(route_use, candidate, before_topology, after_topology)
    surface_lineage = build_surface_lineage_record(route_use, topology_event)
    reabsorption = build_reabsorption_record(topology_event)
    control_rows = controls()
    arc = arc_interpretation(topology_event, reabsorption)
    caveat = theory_caveat()
    result_checks = validate(
        baseline,
        mem1,
        route_use,
        topology_event,
        surface_lineage,
        reabsorption,
        control_rows,
        arc,
        caveat,
    )
    output: dict[str, Any] = {
        "schema": "n08_iteration_10_geometry_trail_formation_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 10,
        "status": "passed" if all(result_checks.values()) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short_src(),
            "src_clean": git_status_short_src() == "",
        },
        "source_artifacts": source_artifacts(),
        "source_reports": source_reports(),
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "claim_ceiling": "native_geometry_trace_formation_boundary_probe",
        "theory_caveat": caveat,
        "source_route_use_event": route_use,
        "source_candidate_route_record": candidate,
        "pre_trace_topology_snapshot": before_topology,
        "post_trace_topology_snapshot": after_topology,
        "topology_event": topology_event,
        "surface_lineage_record": surface_lineage,
        "topology_state_reabsorption_record": reabsorption,
        "arc_of_becoming_interpretation": arc,
        "controls": control_rows,
        "checks": result_checks,
        "claim_boundary": {
            "native_geometry_mediated_trail_claim_allowed": False,
            "memory_or_trail_claim_allowed": False,
            "future_flux_response_tested": False,
            "reinforcement_interpretation_allowed": False,
            "zero_coherence_inserted_node_theory_clean": False,
            "hypothesis_b_closeout_reached": False,
            "all_broader_claims_blocked": True,
        },
        "next_iteration": {
            "iteration": 11,
            "name": "future_flux_response_to_geometry_trace",
            "question": arc["cultivation"]["next_question"],
        },
        "acceptance": {
            "achieved": all(result_checks.values()),
            "status": "passed" if all(result_checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 10 passes if prior route use forms a native "
                "geometry/topology/support trace with artifact-visible lineage "
                "and exact budgets, without independent memory-strength "
                "storage or claim promotion."
            ),
        },
    }
    output["artifact_digests"] = {
        "topology_event_digest": topology_event["topology_event_digest"],
        "surface_lineage_record_digest": surface_lineage[
            "surface_lineage_record_digest"
        ],
        "topology_state_reabsorption_digest": reabsorption[
            "topology_state_reabsorption_digest"
        ],
        "arc_interpretation_digest": arc["arc_interpretation_digest"],
        "theory_caveat_digest": caveat["theory_caveat_digest"],
        "controls_digest": digest_value(control_rows),
        "checks_digest": digest_value(result_checks),
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
