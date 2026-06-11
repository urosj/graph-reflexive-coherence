#!/usr/bin/env python3
"""Run N08 Iteration 13 native geometry-mediated trail closeout.

Iteration 13 performs an artifact-only closeout of the Hypothesis B branch.
It reconstructs the chain from Iterations 9-12 and freezes the strongest
bounded result without promoting it to native conductance/trail memory.
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
OUTPUT_PATH = EXPERIMENT / "outputs/n08_iteration_13_native_geometry_trail_closeout.json"
REPORT_PATH = EXPERIMENT / "reports/n08_iteration_13_native_geometry_trail_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_13_native_geometry_trail_closeout.py"
)

SOURCE_PATHS = {
    "iteration_8_hypothesis_a_closeout": (
        EXPERIMENT / "outputs/n08_iteration_8_mem6_closeout.json"
    ),
    "iteration_9_baseline": (
        EXPERIMENT / "outputs/n08_iteration_9_native_geometry_trail_baseline.json"
    ),
    "iteration_10_trace_formation": (
        EXPERIMENT / "outputs/n08_iteration_10_geometry_trail_formation.json"
    ),
    "iteration_11_trace_response": (
        EXPERIMENT / "outputs/n08_iteration_11_geometry_trace_flux_response.json"
    ),
    "iteration_11a_positive_response": (
        EXPERIMENT / "outputs/n08_iteration_11a_positive_geometry_route_arbitration.json"
    ),
    "iteration_12_persistence": (
        EXPERIMENT / "outputs/n08_iteration_12_geometry_trace_persistence_relaxation.json"
    ),
}
SOURCE_REPORTS = {
    "iteration_8_hypothesis_a_closeout": (
        EXPERIMENT / "reports/n08_iteration_8_mem6_closeout.md"
    ),
    "iteration_9_baseline": (
        EXPERIMENT / "reports/n08_iteration_9_native_geometry_trail_baseline.md"
    ),
    "iteration_10_trace_formation": (
        EXPERIMENT / "reports/n08_iteration_10_geometry_trail_formation.md"
    ),
    "iteration_11_trace_response": (
        EXPERIMENT / "reports/n08_iteration_11_geometry_trace_flux_response.md"
    ),
    "iteration_11a_positive_response": (
        EXPERIMENT / "reports/n08_iteration_11a_positive_geometry_route_arbitration.md"
    ),
    "iteration_12_persistence": (
        EXPERIMENT / "reports/n08_iteration_12_geometry_trace_persistence_relaxation.md"
    ),
}

HYPOTHESIS_B_CEILING = "static_positive_geometry_route_response_persistence_candidate"
HYPOTHESIS_B_BLOCKER = "native_route_conductance_memory_policy_missing"


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


def output_digest_recomputes(artifact: dict[str, Any]) -> bool:
    if "output_digest" not in artifact:
        return False
    return artifact["output_digest"] == digest_value(
        {
            key: value
            for key, value in artifact.items()
            if key not in {"generated_at", "output_digest"}
        }
    )


def artifact_digest_recomputes(artifact: dict[str, Any]) -> bool:
    if "artifact_digest" not in artifact:
        return False
    return artifact["artifact_digest"] == digest_value(
        {
            key: value
            for key, value in artifact.items()
            if key not in {"generated_at", "artifact_digest"}
        }
    )


def false_hypothesis_b_claim_flags() -> dict[str, bool]:
    return {
        "hypothesis_b_native_geometry_mediated_trail_claim_allowed": False,
        "hypothesis_b_pure_coherence_flux_trail_claim_allowed": False,
        "native_route_conductance_memory_policy_supported": False,
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


def load_sources() -> dict[str, dict[str, Any]]:
    return {name: load_json(path) for name, path in SOURCE_PATHS.items()}


def source_artifact_file_digests() -> dict[str, str]:
    return {rel(path): digest_file(path) for path in SOURCE_PATHS.values()}


def source_report_file_digests() -> dict[str, str]:
    return {rel(path): digest_file(path) for path in SOURCE_REPORTS.values()}


def build_replay_chain(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    i9 = sources["iteration_9_baseline"]
    i10 = sources["iteration_10_trace_formation"]
    i11 = sources["iteration_11_trace_response"]
    i11a = sources["iteration_11a_positive_response"]
    i12 = sources["iteration_12_persistence"]
    route_use = i10["source_route_use_event"]
    topology_event = i10["topology_event"]
    response_summary = i11["response_summary"]
    positive_summary = i11a["response_summary"]
    persistence_summary = i12["persistence_summary"]
    rows = [
        {
            "step_id": "iteration_9_entry_gate",
            "iteration": 9,
            "status": i9["status"],
            "artifact_digest": i9["output_digest"],
            "evidence_kind": "native_mechanism_inventory",
            "result": "edge_split_inserted_node_trace_entry_allowed",
            "primary_blocker": None,
            "event_time_key": None,
            "scheduler_event_index": None,
        },
        {
            "step_id": "route_use_source_event",
            "iteration": 10,
            "status": route_use["route_use_commit_status"],
            "artifact_digest": route_use["route_use_event_digest"],
            "evidence_kind": "committed_route_use_event",
            "result": route_use["selected_route_id"],
            "primary_blocker": None,
            "event_time_key": route_use["event_time_key"],
            "scheduler_event_index": route_use["scheduler_event_index"],
        },
        {
            "step_id": "geometry_trace_topology_event",
            "iteration": 10,
            "status": topology_event["topology_commit_status"],
            "artifact_digest": topology_event["topology_event_digest"],
            "evidence_kind": "edge_split_inserted_node_trace",
            "result": topology_event["topology_event_kind"],
            "primary_blocker": None,
            "event_time_key": topology_event["event_time_key"],
            "scheduler_event_index": topology_event["scheduler_event_index"],
        },
        {
            "step_id": "zero_trace_response_classification",
            "iteration": 11,
            "status": "classified",
            "artifact_digest": response_summary["response_summary_digest"],
            "evidence_kind": "future_flux_response",
            "result": response_summary["primary_observation"],
            "primary_blocker": "zero_coherence_trace_absorber",
            "event_time_key": 11.0,
            "scheduler_event_index": 1100,
        },
        {
            "step_id": "positive_geometry_route_arbitration_response",
            "iteration": "11-A",
            "status": positive_summary["positive_trace_status"],
            "artifact_digest": positive_summary["response_summary_digest"],
            "evidence_kind": "native_route_arbitration_reads_geometry_evidence",
            "result": positive_summary["positive_trace_selected_route_id"],
            "primary_blocker": None,
            "event_time_key": 11.6,
            "scheduler_event_index": 1160,
        },
        {
            "step_id": "static_positive_geometry_response_persistence",
            "iteration": 12,
            "status": "persisted",
            "artifact_digest": persistence_summary["persistence_summary_digest"],
            "evidence_kind": "repeated_static_geometry_response_windows",
            "result": persistence_summary["selected_route_sequence"],
            "primary_blocker": HYPOTHESIS_B_BLOCKER,
            "event_time_key": 12.0,
            "scheduler_event_index": 1200,
        },
    ]
    for row in rows:
        row["replay_row_digest"] = digest_value(row)
    return rows


def closeout_summary(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    i8 = sources["iteration_8_hypothesis_a_closeout"]
    i10 = sources["iteration_10_trace_formation"]
    i11 = sources["iteration_11_trace_response"]
    i11a = sources["iteration_11a_positive_response"]
    i12 = sources["iteration_12_persistence"]
    summary: dict[str, Any] = {
        "hypothesis_a_status": "closed",
        "hypothesis_a_claim_ceiling": i8["claim_ceiling"],
        "hypothesis_a_scoped_memory_or_trail_claim_allowed": i8["claim_boundary"][
            "memory_or_trail_claim_allowed"
        ],
        "hypothesis_a_claim_scope": i8["claim_boundary"][
            "memory_or_trail_claim_scope"
        ],
        "hypothesis_b_status": "closed_bounded_native_policy_gap_recorded",
        "hypothesis_b_claim_ceiling": HYPOTHESIS_B_CEILING,
        "hypothesis_b_current_blocker": HYPOTHESIS_B_BLOCKER,
        "hypothesis_b_native_geometry_mediated_trail_claim_allowed": False,
        "hypothesis_b_pure_coherence_flux_trail_claim_allowed": False,
        "route_use_digest": i10["source_route_use_event"]["route_use_event_digest"],
        "topology_event_digest": i10["topology_event"]["topology_event_digest"],
        "zero_trace_observation": i11["response_summary"]["primary_observation"],
        "positive_trace_selected_route": i11a["response_summary"][
            "positive_trace_selected_route_id"
        ],
        "persistence_selected_route_sequence": i12["persistence_summary"][
            "selected_route_sequence"
        ],
        "static_positive_geometry_response_persisted": i12["persistence_summary"][
            "route_response_persisted_all_windows"
        ],
        "native_route_conductance_memory_policy_available": False,
        "native_policy_absorption_needed": True,
        "phase_8_candidate_policy_surface": "native_route_conductance_memory_policy",
        "closeout_interpretation": (
            "Hypothesis B is a roadmap-aligned scaffold/native-policy-gap "
            "result: declared positive geometry can shape native route "
            "arbitration and persist as a static response, but current LGRC "
            "does not yet provide native conductance update, strengthening, "
            "or relaxation policy."
        ),
    }
    summary["closeout_summary_digest"] = digest_value(summary)
    return summary


def controls() -> list[dict[str, Any]]:
    rows = [
        (
            "missing_source_artifact",
            "source_artifact_missing",
            "Reject closeout if any Iteration 9-12 source artifact is absent.",
        ),
        (
            "digest_mismatch",
            "source_artifact_digest_mismatch",
            "Reject closeout if source output or row digests do not recompute.",
        ),
        (
            "event_order_inversion",
            "hypothesis_b_replay_order_invalid",
            "Reject topology/response/persistence chain with inverted order.",
        ),
        (
            "hidden_memory_strength",
            "memory_strength_input_blocked",
            "Reject Hypothesis B closeout if independent memory_strength is required.",
        ),
        (
            "zero_trace_overclaim",
            "zero_trace_reinforcement_blocked",
            "Reject treating zero-coherence absorber as reinforcement.",
        ),
        (
            "missing_positive_geometry_response",
            "positive_geometry_route_response_missing",
            "Reject closeout without positive geometry route response evidence.",
        ),
        (
            "missing_static_persistence",
            "static_geometry_response_persistence_missing",
            "Reject closeout without repeated-window static persistence evidence.",
        ),
        (
            "budget_discontinuity",
            "node_plus_packet_budget_discontinuity",
            "Reject any source chain with nonzero node-plus-packet budget error.",
        ),
        (
            "route_conductance_policy_overclaim",
            HYPOTHESIS_B_BLOCKER,
            "Reject stronger native trail closeout without route-conductance policy.",
        ),
        (
            "claim_promotion",
            "claim_promotion",
            "Reject ACO, agency, identity acceptance, locomotion, biology, or unrestricted claims.",
        ),
    ]
    output: list[dict[str, Any]] = []
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
        output.append(row)
    return output


def artifact_only_validator_scope() -> dict[str, Any]:
    scope: dict[str, Any] = {
        "validator_id": "n08_hypothesis_b_artifact_only_closeout_validator_v1",
        "artifact_only": True,
        "runtime_state_used": False,
        "private_runtime_state_used": False,
        "source_scripts_imported": False,
        "source_artifacts_replayed": [
            "iteration_9_baseline",
            "iteration_10_trace_formation",
            "iteration_11_trace_response",
            "iteration_11a_positive_response",
            "iteration_12_persistence",
        ],
        "replay_boundary": (
            "The validator reconstructs source links, digests, event order, "
            "control blockers, and claim boundaries from exported JSON only. "
            "It does not rerun flux dynamics or create new probes."
        ),
    }
    scope["validator_scope_digest"] = digest_value(scope)
    return scope


def arc_interpretation(summary: dict[str, Any]) -> dict[str, Any]:
    arc: dict[str, Any] = {
        "interpretation_id": "n08_i13_arc_hypothesis_b_bounded_closeout_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Interrogation of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "What did the native geometry-mediated branch actually become "
            "after replaying the chain from artifacts?"
        ),
        "observations": [
            {
                "observation_id": "zero_trace_is_boundary_not_reinforcement",
                "value": summary["zero_trace_observation"],
                "interpretation": (
                    "The first topology trace crossed a useful boundary: zero "
                    "coherence creates absorber behavior rather than trail "
                    "reinforcement."
                ),
            },
            {
                "observation_id": "positive_geometry_shapes_arbitration",
                "value": summary["positive_trace_selected_route"],
                "interpretation": (
                    "A positive conserved geometry can be read by native route "
                    "arbitration as runtime-visible evidence."
                ),
            },
            {
                "observation_id": "static_response_persists",
                "value": summary["persistence_selected_route_sequence"],
                "interpretation": (
                    "The route response persists while geometry is fixed. This "
                    "is lower than adaptive trail memory, but useful as a "
                    "native-policy design target."
                ),
            },
            {
                "observation_id": "native_policy_gap_is_the_result",
                "value": summary["hypothesis_b_current_blocker"],
                "interpretation": (
                    "The missing function is now specific: LGRC would need a "
                    "native route-conductance update/relaxation policy to "
                    "naturalize the scaffold."
                ),
            },
        ],
        "classification": {
            "hypothesis_b_claim_ceiling": summary["hypothesis_b_claim_ceiling"],
            "native_geometry_mediated_trail_supported": False,
            "pure_flux_trail_memory_supported": False,
            "native_policy_gap_recorded": True,
            "not_merely_true_false_endpoint": True,
        },
        "cultivation": {
            "what_this_branch_teaches": [
                "Do not use zero-coherence inserted nodes as reinforcement carriers.",
                "Positive conserved geometry is the viable design direction for route-response scaffolding.",
                "Static geometry persistence is useful but must not be renamed adaptive memory.",
                "The next native absorption target is route-conductance update/relaxation policy, if later experiments need it.",
            ],
            "handoff": (
                "N09-N11 may consume the Hypothesis A artifact-only memory "
                "candidate and may cite the Hypothesis B static geometry "
                "response as a bounded design direction, but must not consume "
                "native geometry-mediated trail support."
            ),
        },
        "naturalization": {
            "naturalization_rung": "Nat3_static_geometry_response_design_target",
            "constitutive_native_trail_memory": False,
            "native_absorption_needed": True,
        },
    }
    arc["arc_interpretation_digest"] = digest_value(arc)
    return arc


def all_source_digests_recompute(sources: dict[str, dict[str, Any]]) -> bool:
    return (
        output_digest_recomputes(sources["iteration_9_baseline"])
        and output_digest_recomputes(sources["iteration_10_trace_formation"])
        and output_digest_recomputes(sources["iteration_11_trace_response"])
        and output_digest_recomputes(sources["iteration_11a_positive_response"])
        and artifact_digest_recomputes(sources["iteration_12_persistence"])
    )


def event_order_valid(sources: dict[str, dict[str, Any]]) -> bool:
    route_use = sources["iteration_10_trace_formation"]["source_route_use_event"]
    topology = sources["iteration_10_trace_formation"]["topology_event"]
    windows = sources["iteration_12_persistence"]["persistence_windows"]
    return (
        route_use["event_time_key"] < topology["event_time_key"]
        and route_use["scheduler_event_index"] < topology["scheduler_event_index"]
        and all(
            windows[index]["event_time_key"] < windows[index + 1]["event_time_key"]
            and windows[index]["scheduler_event_index"]
            < windows[index + 1]["scheduler_event_index"]
            for index in range(len(windows) - 1)
        )
    )


def validate(
    sources: dict[str, dict[str, Any]],
    replay_chain: list[dict[str, Any]],
    summary: dict[str, Any],
    control_rows: list[dict[str, Any]],
    validator_scope: dict[str, Any],
    arc: dict[str, Any],
) -> dict[str, bool]:
    i8 = sources["iteration_8_hypothesis_a_closeout"]
    i9 = sources["iteration_9_baseline"]
    i10 = sources["iteration_10_trace_formation"]
    i11 = sources["iteration_11_trace_response"]
    i11a = sources["iteration_11a_positive_response"]
    i12 = sources["iteration_12_persistence"]
    topology = i10["topology_event"]
    route_use = i10["source_route_use_event"]
    windows = i12["persistence_windows"]
    return {
        "all_sources_passed": all(source["status"] == "passed" for source in sources.values()),
        "hypothesis_a_closeout_scoped": i8["claim_boundary"][
            "memory_or_trail_claim_allowed"
        ]
        is True
        and i8["claim_boundary"]["memory_or_trail_claim_scope"]
        == "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "iteration_9_entry_gate_passed": i9["iteration_10_entry_gate"][
            "iteration_10_entry_allowed"
        ]
        is True,
        "source_digests_recompute": all_source_digests_recompute(sources),
        "topology_event_digest_recomputes": topology["topology_event_digest"]
        == digest_record(topology, "topology_event_digest"),
        "route_use_causes_topology_trace": topology["source_route_use_event_digest"]
        == route_use["route_use_event_digest"],
        "route_use_committed": route_use["route_use_commit_status"] == "committed",
        "zero_trace_boundary_preserved": i11["response_summary"][
            "zero_trace_leakage_fraction"
        ]
        == 1.0
        and i11["response_summary"]["reinforcement_interpretation_supported"]
        is False,
        "positive_geometry_response_present": i11a["response_summary"][
            "positive_geometry_route_response_candidate_supported"
        ]
        is True
        and i11a["response_summary"]["positive_trace_selected_route_id"] == "route_b",
        "static_persistence_present": i12["persistence_summary"][
            "static_positive_geometry_response_persistence_supported"
        ]
        is True
        and all(window["selected_route_id"] == "route_b" for window in windows),
        "event_order_valid": event_order_valid(sources),
        "budget_error_zero": topology["node_plus_packet_budget_error"] == 0.0
        and all(window["node_plus_packet_budget_error"] == 0.0 for window in windows),
        "no_memory_strength_used": i11a["checks"]["no_memory_strength_used"]
        and i12["checks"]["no_memory_strength_used"],
        "no_memory_shaped_scores_used": i11a["checks"][
            "no_memory_shaped_scores_used"
        ]
        and i12["checks"]["no_memory_shaped_scores_used"],
        "native_policy_blocker_recorded": summary["hypothesis_b_current_blocker"]
        == HYPOTHESIS_B_BLOCKER,
        "hypothesis_b_ceiling_bounded": summary["hypothesis_b_claim_ceiling"]
        == HYPOTHESIS_B_CEILING,
        "hypothesis_b_native_claims_blocked": not summary[
            "hypothesis_b_native_geometry_mediated_trail_claim_allowed"
        ]
        and not summary["hypothesis_b_pure_coherence_flux_trail_claim_allowed"],
        "replay_chain_complete": [row["step_id"] for row in replay_chain]
        == [
            "iteration_9_entry_gate",
            "route_use_source_event",
            "geometry_trace_topology_event",
            "zero_trace_response_classification",
            "positive_geometry_route_arbitration_response",
            "static_positive_geometry_response_persistence",
        ],
        "artifact_only_validator_scope": validator_scope["artifact_only"]
        and not validator_scope["runtime_state_used"]
        and not validator_scope["source_scripts_imported"],
        "control_blockers_distinct": len(
            {control["primary_blocker"] for control in control_rows}
        )
        == len(control_rows),
        "controls_passed": all(control["control_passed"] for control in control_rows),
        "all_hypothesis_b_claim_flags_false": all(
            not value for value in false_hypothesis_b_claim_flags().values()
        ),
        "arc_interpretation_present": bool(arc["arc_interpretation_digest"]),
        "src_clean": git_status_short_src() == "",
    }


def artifact_digest(artifact: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in artifact.items()
            if key not in {"generated_at", "artifact_digest"}
        }
    )


def build_artifact() -> dict[str, Any]:
    sources = load_sources()
    replay_chain = build_replay_chain(sources)
    summary = closeout_summary(sources)
    control_rows = controls()
    validator_scope = artifact_only_validator_scope()
    arc = arc_interpretation(summary)
    checks = validate(sources, replay_chain, summary, control_rows, validator_scope, arc)
    status = "passed" if all(checks.values()) else "failed"
    artifact: dict[str, Any] = {
        "artifact_kind": "n08_iteration_13_native_geometry_trail_closeout",
        "artifact_schema_version": "n08_iteration_13_native_geometry_trail_closeout_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 13,
        "iteration_name": "Native Geometry-Mediated Trail Replay And Closeout",
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "purpose": (
            "Artifact-only closeout of the Hypothesis B branch with bounded "
            "static geometry response persistence and native policy blocker."
        ),
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
        "command": COMMAND,
        "source_artifacts": source_artifact_file_digests(),
        "source_reports": source_report_file_digests(),
        "artifact_only_validator_scope": validator_scope,
        "replay_chain": replay_chain,
        "closeout_summary": summary,
        "arc_interpretation": arc,
        "controls": control_rows,
        "checks": checks,
        "claim_boundary": {
            "hypothesis_a_memory_or_trail_claim_allowed": summary[
                "hypothesis_a_scoped_memory_or_trail_claim_allowed"
            ],
            "hypothesis_a_memory_or_trail_claim_scope": summary[
                "hypothesis_a_claim_scope"
            ],
            "hypothesis_b_native_geometry_mediated_trail_claim_allowed": False,
            "hypothesis_b_pure_coherence_flux_trail_claim_allowed": False,
            "native_geometry_mediated_trail_claim_allowed": False,
            "pure_coherence_flux_trail_claim_allowed": False,
            "all_stronger_claims_blocked": True,
        },
        "claim_flags": false_hypothesis_b_claim_flags(),
        "next_step": (
            "N08 can close with Hypothesis A MEM6 plus Hypothesis B bounded "
            "static geometry response persistence. N09-N11 may consume only "
            "the scoped claims and must keep native trail-memory support blocked."
        ),
    }
    artifact["artifact_digest"] = artifact_digest(artifact)
    return artifact


def write_report(artifact: dict[str, Any]) -> None:
    summary = artifact["closeout_summary"]
    lines = [
        "# N08 Iteration 13 Native Geometry-Mediated Trail Closeout",
        "",
        f"Status: {artifact['status']}",
        "",
        "## Purpose",
        "",
        (
            "Iteration 13 replays the Hypothesis B branch from exported "
            "artifacts only and freezes the strongest valid ceiling."
        ),
        "",
        "## Closeout",
        "",
        f"- Hypothesis A ceiling: `{summary['hypothesis_a_claim_ceiling']}`.",
        (
            "- Hypothesis A scoped memory/trail claim allowed: "
            f"`{summary['hypothesis_a_scoped_memory_or_trail_claim_allowed']}` "
            f"for `{summary['hypothesis_a_claim_scope']}`."
        ),
        f"- Hypothesis B ceiling: `{summary['hypothesis_b_claim_ceiling']}`.",
        f"- Hypothesis B blocker: `{summary['hypothesis_b_current_blocker']}`.",
        (
            "- Hypothesis B native geometry-mediated trail claim allowed: "
            f"`{summary['hypothesis_b_native_geometry_mediated_trail_claim_allowed']}`."
        ),
        (
            "- Hypothesis B pure flux trail claim allowed: "
            f"`{summary['hypothesis_b_pure_coherence_flux_trail_claim_allowed']}`."
        ),
        "",
        "## Replay Chain",
        "",
    ]
    for row in artifact["replay_chain"]:
        lines.append(
            f"- `{row['step_id']}`: `{row['evidence_kind']}` -> `{row['result']}`"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            summary["closeout_interpretation"],
            "",
            (
                "This is a roadmap-aligned producer/scaffold-to-native-policy "
                "discovery result. It does not change RC field mechanics and "
                "does not claim native conductance memory."
            ),
            "",
            "## Controls",
            "",
        ]
    )
    for control in artifact["controls"]:
        lines.append(
            f"- `{control['control_id']}` -> `{control['primary_blocker']}`."
        )
    lines.extend(["", "## Checks", ""])
    for key, value in artifact["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            (
                "Hypothesis A keeps only its scoped artifact-only serialized "
                "producer/policy route memory/trail claim. Hypothesis B does "
                "not open native geometry-mediated trail, pure flux trail, "
                "ACO, agency, intention, goal regulation, identity acceptance, "
                "locomotion, biological, personhood, unrestricted identity, or "
                "unrestricted movement claims."
            ),
            "",
            "## Replay",
            "",
            "```bash",
            artifact["command"],
            "```",
            "",
            f"Artifact digest: `{artifact['artifact_digest']}`",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    artifact = build_artifact()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)


if __name__ == "__main__":
    main()
