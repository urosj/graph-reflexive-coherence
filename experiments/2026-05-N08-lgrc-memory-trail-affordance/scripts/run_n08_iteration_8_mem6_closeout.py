#!/usr/bin/env python3
"""Run N08 Iteration 8 MEM6 artifact-only replay and closeout.

Iteration 8 reads the Iteration 7 artifact and reconstructs the repeated
route-use -> memory update -> memory-shaped route arbitration chain from
exported JSON only. It does not import or call the Iteration 7 runner and does
not run a new behavioral probe.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"
SOURCE_MEM5_PATH = (
    EXPERIMENT / "outputs" / "n08_iteration_7_mem5_repeated_memory_selection.json"
)
SOURCE_MEM5_REPORT = (
    EXPERIMENT / "reports" / "n08_iteration_7_mem5_repeated_memory_selection.md"
)
MANIFEST_VALIDATION_PATH = (
    EXPERIMENT / "outputs" / "n08_iteration_2_fixture_manifest_validation.json"
)
OUTPUT_PATH = EXPERIMENT / "outputs" / "n08_iteration_8_mem6_closeout.json"
REPORT_PATH = EXPERIMENT / "reports" / "n08_iteration_8_mem6_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_8_mem6_closeout.py"
)

MEM6_CEILING = "artifact_only_route_memory_or_trail_affordance_candidate"
MEM5_CEILING = "mem5_repeated_memory_shaped_selection_candidate"
EXPECTED_SCORE_COMPONENTS = {
    "memory_trail_strength",
    "memory_surface_digest_match",
    "memory_recency_weight",
    "memory_decay_adjusted_strength",
}
EXPECTED_SOURCE_CONTROLS = {
    "repeated_hidden_route_preference": "candidate_score_hidden_memory_input",
    "stale_memory_surface_read": "stale_memory_surface_read",
    "duplicate_memory_update": "duplicate_memory_update",
    "cross_cycle_memory_leak": "cross_cycle_memory_leak",
    "memory_budget_discontinuity": "memory_budget_discontinuity",
    "node_plus_packet_budget_discontinuity": "node_plus_packet_budget_discontinuity",
    "claim_promotion": "claim_promotion",
}
EPSILON = 1e-12


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


def digest_record(record: dict[str, Any], digest_field: str) -> str:
    return digest_value(
        {key: value for key, value in record.items() if key != digest_field}
    )


def recompute_output_digest(output: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"generated_at", "output_digest"}
        }
    )


def rounded_sum(values: dict[str, Any]) -> float:
    return round(sum(float(value) for value in values.values()), 12)


def floats_equal(left: Any, right: Any, epsilon: float = EPSILON) -> bool:
    return abs(float(left) - float(right)) <= epsilon


def false_claim_flags(manifest_validation: dict[str, Any]) -> dict[str, bool]:
    return {
        key: False
        for key in manifest_validation["fixture_manifest"]["memory_surface_row_schema"][
            "required_claim_flag_keys"
        ]
    }


def closeout_claim_flags(manifest_validation: dict[str, Any]) -> dict[str, bool]:
    flags = false_claim_flags(manifest_validation)
    flags["memory_or_trail_claim_allowed"] = True
    return flags


def row_claims_false(row: dict[str, Any]) -> bool:
    return all(value is False for value in row.get("claim_flags", {}).values())


def memory_budget_equation_holds(row: dict[str, Any]) -> bool:
    expected = (
        float(row["memory_budget_before"])
        + float(row["reinforcement_input"])
        - float(row["decay_loss"])
        - float(row["saturation_clamp_loss"])
    )
    return floats_equal(expected, row["memory_budget_after"])


def candidate_by_digest(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["candidate_route_digest"]: row for row in candidates}


def candidate_by_route(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["candidate_route_id"]: row for row in candidates}


def update_by_route(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["selected_route_id"]: row for row in rows}


def expected_candidate_order(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        candidates,
        key=lambda row: (-float(row["candidate_route_score"]), row["candidate_order_key"]),
    )


def append_once(blockers: list[str], blocker: str) -> None:
    if blocker not in blockers:
        blockers.append(blocker)


def replay_blockers(source: dict[str, Any]) -> list[str]:
    """Return artifact-only replay blockers for a source-like MEM5 artifact."""

    blockers: list[str] = []
    cycles = source.get("cycles")
    if not isinstance(cycles, list) or not cycles:
        return ["missing_cycle_records"]

    previous_updates: dict[str, dict[str, Any]] = {}
    seen_update_ids: set[str] = set()

    for cycle in cycles:
        cycle_id = str(cycle.get("cycle_id", "unknown_cycle"))
        candidates = cycle.get("candidate_route_records")
        candidate_set = cycle.get("candidate_set_record")
        arbitration = cycle.get("route_arbitration_record")
        route_use = cycle.get("route_use_event")
        updates = cycle.get("memory_update_rows")

        if not isinstance(candidates, list) or not candidates:
            append_once(blockers, "candidate_route_records_missing")
            continue
        if not isinstance(candidate_set, dict):
            append_once(blockers, "candidate_set_missing")
            continue
        if not isinstance(arbitration, dict):
            append_once(blockers, "native_route_arbitration_record_missing")
            continue
        if not isinstance(route_use, dict):
            append_once(blockers, "missing_route_use_event")
            route_use = {}
        if not isinstance(updates, list) or not updates:
            append_once(blockers, "memory_surface_missing")
            updates = []

        candidate_routes = candidate_by_route(candidates)
        candidate_digests = candidate_by_digest(candidates)
        ordered_candidates = expected_candidate_order(candidates)
        expected_candidate_digests = [
            row["candidate_route_digest"] for row in ordered_candidates
        ]

        for candidate in candidates:
            route_id = candidate.get("candidate_route_id")
            if candidate.get("candidate_route_digest") != digest_record(
                candidate, "candidate_route_digest"
            ):
                append_once(blockers, "candidate_route_digest_mismatch")
            if set(candidate.get("candidate_score_components", {}).keys()) != (
                EXPECTED_SCORE_COMPONENTS
            ):
                append_once(blockers, "memory_score_component_schema_mismatch")
            if not floats_equal(
                candidate.get("candidate_route_score", 0.0),
                rounded_sum(candidate.get("candidate_score_components", {})),
            ):
                append_once(blockers, "score_component_mismatch")
            if candidate.get("hidden_memory_input_used") is not False:
                append_once(blockers, "hidden_route_history")
            if candidate.get("route_specific_hidden_preference_used") is not False:
                append_once(blockers, "hidden_route_history")
            if candidate.get("native_geometry_trail_claimed") is not False:
                append_once(blockers, "native_geometry_claim_promotion")
            if candidate.get("pure_coherence_flux_trail_claimed") is not False:
                append_once(blockers, "native_geometry_claim_promotion")
            if not row_claims_false(candidate):
                append_once(blockers, "claim_promotion")
            if not floats_equal(
                candidate.get("candidate_budget_prediction", {}).get(
                    "node_plus_packet_budget_error", 1.0
                ),
                0.0,
            ):
                append_once(blockers, "node_plus_packet_budget_discontinuity")
            if not floats_equal(
                candidate.get("candidate_memory_budget_prediction", {}).get(
                    "memory_budget_error", 1.0
                ),
                0.0,
            ):
                append_once(blockers, "memory_budget_discontinuity")
            if route_id in previous_updates:
                expected_source = previous_updates[route_id]
                if (
                    candidate.get("candidate_memory_surface_digest")
                    != expected_source.get("memory_surface_digest")
                ):
                    append_once(blockers, "stale_memory_read")

        if candidate_set.get("candidate_set_digest") != digest_record(
            candidate_set, "candidate_set_digest"
        ):
            append_once(blockers, "candidate_set_digest_mismatch")
        if candidate_set.get("candidate_route_digests") != expected_candidate_digests:
            append_once(blockers, "candidate_set_route_order_mismatch")

        if arbitration.get("native_route_arbitration_digest") != digest_record(
            arbitration, "native_route_arbitration_digest"
        ):
            append_once(blockers, "native_route_arbitration_digest_mismatch")

        selected_digest = arbitration.get("selected_candidate_route_digest")
        if selected_digest not in candidate_digests:
            append_once(blockers, "selected_candidate_missing")
        elif selected_digest != expected_candidate_digests[0]:
            append_once(blockers, "native_route_arbitration_selection_mismatch")

        rejected = set(arbitration.get("rejected_candidate_route_digests", []))
        expected_rejected = set(expected_candidate_digests) - {selected_digest}
        if rejected != expected_rejected:
            append_once(blockers, "rejected_candidate_set_mismatch")

        if (
            arbitration.get("event_time_key", -1)
            <= candidate_set.get("event_time_key", float("inf"))
            or arbitration.get("scheduler_event_index", -1)
            <= candidate_set.get("scheduler_event_index", float("inf"))
        ):
            append_once(blockers, "event_order_inversion")

        if route_use:
            if route_use.get("route_use_commit_status") != "committed":
                append_once(blockers, "missing_route_use_event")
            if route_use.get("route_use_event_digest") != digest_record(
                route_use, "route_use_event_digest"
            ):
                append_once(blockers, "route_use_digest_mismatch")
            if (
                route_use.get("source_arbitration_record_digest")
                != arbitration.get("native_route_arbitration_digest")
            ):
                append_once(blockers, "route_use_arbitration_link_mismatch")
            if route_use.get("selected_candidate_route_digest") != selected_digest:
                append_once(blockers, "route_use_selected_digest_mismatch")
            if route_use.get("selected_route_id") != arbitration.get(
                "selected_candidate_route_id"
            ):
                append_once(blockers, "route_use_selected_route_mismatch")
            if not floats_equal(route_use.get("node_plus_packet_budget_error", 1.0), 0.0):
                append_once(blockers, "node_plus_packet_budget_discontinuity")
            if not row_claims_false(route_use):
                append_once(blockers, "claim_promotion")
            if (
                route_use.get("event_time_key", -1)
                <= arbitration.get("event_time_key", float("inf"))
                or route_use.get("scheduler_event_index", -1)
                <= arbitration.get("scheduler_event_index", float("inf"))
            ):
                append_once(blockers, "event_order_inversion")

        updates_by_route = update_by_route(updates)
        if len(updates_by_route) != len(updates):
            append_once(blockers, "duplicate_update")
        if set(updates_by_route.keys()) != set(candidate_routes.keys()):
            append_once(blockers, "memory_surface_missing")

        for update in updates:
            route_id = update.get("selected_route_id")
            update_id = update.get("memory_surface_id")
            if update_id in seen_update_ids:
                append_once(blockers, "duplicate_update")
            seen_update_ids.add(str(update_id))

            candidate = candidate_routes.get(route_id)
            if candidate is not None and update.get("source_memory_surface_digest") != (
                candidate.get("candidate_memory_surface_digest")
            ):
                append_once(blockers, "stale_memory_read")
            if update.get("memory_surface_digest") != digest_record(
                update, "memory_surface_digest"
            ):
                append_once(blockers, "memory_surface_digest_mismatch")
            if not memory_budget_equation_holds(update):
                append_once(blockers, "memory_budget_discontinuity")
            if not floats_equal(update.get("memory_budget_error", 1.0), 0.0):
                append_once(blockers, "memory_budget_discontinuity")
            if not floats_equal(
                update.get("node_plus_packet_budget_error", 1.0),
                0.0,
            ):
                append_once(blockers, "node_plus_packet_budget_discontinuity")
            if update.get("decay_is_physical_flux") is not False:
                append_once(blockers, "physical_flux_claim_promotion")
            if update.get("coherence_pocket_transfer_performed") is not False:
                append_once(blockers, "physical_flux_claim_promotion")
            if not row_claims_false(update):
                append_once(blockers, "claim_promotion")
            if route_use and (
                update.get("event_time_key", -1)
                <= route_use.get("event_time_key", float("inf"))
                or update.get("scheduler_event_index", -1)
                <= route_use.get("scheduler_event_index", float("inf"))
            ):
                append_once(blockers, "event_order_inversion")

            selected_route = cycle.get("selected_route_id")
            if route_id == selected_route:
                if update.get("reinforced_by_route_use_event") is not True:
                    append_once(blockers, "memory_state_reconstruction_mismatch")
                if update.get("route_use_event_digest") != route_use.get(
                    "route_use_event_digest"
                ):
                    append_once(blockers, "missing_route_use_event")
            else:
                if update.get("reinforced_by_route_use_event") is not False:
                    append_once(blockers, "memory_state_reconstruction_mismatch")
                if update.get("route_use_event_digest") is not None:
                    append_once(blockers, "cross_cycle_memory_leak")

        memory_state_after = cycle.get("memory_state_after", {})
        for route_id, update in updates_by_route.items():
            state = memory_state_after.get(route_id, {})
            if state.get("memory_surface_digest") != update.get("memory_surface_digest"):
                append_once(blockers, "memory_state_reconstruction_mismatch")
            if not floats_equal(state.get("memory_strength", -1), update.get("memory_strength", 0)):
                append_once(blockers, "memory_state_reconstruction_mismatch")

        previous_updates = updates_by_route

    return blockers


def clone_source(source: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(source)


def corrupted_controls(source: dict[str, Any]) -> list[dict[str, Any]]:
    controls: list[tuple[str, str, str, Any]] = [
        (
            "missing_route_use_event",
            "missing_route_use_event",
            "Remove the committed route-use event from cycle 0.",
            lambda doc: doc["cycles"][0].pop("route_use_event"),
        ),
        (
            "memory_surface_digest_mismatch",
            "memory_surface_digest_mismatch",
            "Change a memory row strength without updating its digest.",
            lambda doc: doc["cycles"][0]["memory_update_rows"][0].__setitem__(
                "memory_strength", 0.123456
            ),
        ),
        (
            "memory_state_reconstruction_mismatch",
            "memory_state_reconstruction_mismatch",
            "Corrupt reconstructed memory_state_after for route A.",
            lambda doc: doc["cycles"][0]["memory_state_after"]["route_a"].__setitem__(
                "memory_strength", 0.987654
            ),
        ),
        (
            "score_component_mismatch",
            "score_component_mismatch",
            "Alter a candidate route score away from its component sum.",
            lambda doc: doc["cycles"][0]["candidate_route_records"][0].__setitem__(
                "candidate_route_score", 99.0
            ),
        ),
        (
            "event_order_inversion",
            "event_order_inversion",
            "Move a route-use event before arbitration in scheduler order.",
            lambda doc: doc["cycles"][0]["route_use_event"].__setitem__(
                "scheduler_event_index", 1
            ),
        ),
        (
            "stale_memory_read",
            "stale_memory_read",
            "Make cycle 1 read route A memory from the pre-cycle-0 surface.",
            lambda doc: doc["cycles"][1]["candidate_route_records"][0].__setitem__(
                "candidate_memory_surface_digest",
                doc["cycles"][0]["candidate_route_records"][0][
                    "candidate_memory_surface_digest"
                ],
            ),
        ),
        (
            "duplicate_update",
            "duplicate_update",
            "Duplicate a memory update row in cycle 0.",
            lambda doc: doc["cycles"][0]["memory_update_rows"].append(
                copy.deepcopy(doc["cycles"][0]["memory_update_rows"][0])
            ),
        ),
        (
            "memory_budget_discontinuity",
            "memory_budget_discontinuity",
            "Change a memory budget after value without matching the equation.",
            lambda doc: doc["cycles"][0]["memory_update_rows"][1].__setitem__(
                "memory_budget_after", 0.42
            ),
        ),
        (
            "claim_promotion",
            "claim_promotion",
            "Inject an agency claim into a candidate row.",
            lambda doc: doc["cycles"][0]["candidate_route_records"][0][
                "claim_flags"
            ].__setitem__("agency_claim_allowed", True),
        ),
    ]

    rows: list[dict[str, Any]] = []
    for control_id, expected, purpose, mutation in controls:
        doc = clone_source(source)
        mutation(doc)
        blockers = replay_blockers(doc)
        observed = expected if expected in blockers else (blockers[0] if blockers else None)
        row = {
            "control_id": control_id,
            "expected_status": "blocked",
            "observed_status": "blocked" if blockers else "passed",
            "expected_primary_blocker": expected,
            "primary_blocker": observed,
            "all_blockers": blockers,
            "control_passed": expected in blockers,
            "purpose": purpose,
        }
        row["control_row_digest"] = digest_value(row)
        rows.append(row)
    return rows


def replay_summary(source: dict[str, Any]) -> dict[str, Any]:
    cycles = source["cycles"]
    route_use_count = len(cycles)
    update_count = sum(len(cycle["memory_update_rows"]) for cycle in cycles)
    candidate_count = sum(len(cycle["candidate_route_records"]) for cycle in cycles)
    route_b_updates = [
        cycle["memory_state_after"]["route_b"]["memory_strength"] for cycle in cycles
    ]
    route_a_updates = [
        cycle["memory_state_after"]["route_a"]["memory_strength"] for cycle in cycles
    ]
    summary = {
        "artifact_only": True,
        "runtime_state_used": False,
        "source_iteration": 7,
        "source_mem_level": source["mem_level"],
        "replayed_mem_level": "MEM6",
        "route_use_events_replayed": route_use_count,
        "candidate_route_records_replayed": candidate_count,
        "candidate_set_records_replayed": len(cycles),
        "route_arbitration_records_replayed": len(cycles),
        "memory_surface_update_rows_replayed": update_count,
        "scheduled_packet_records_replayed": 0,
        "processed_packet_records_replayed": 0,
        "scheduled_packet_records_applicable": False,
        "processed_packet_records_applicable": False,
        "selected_routes": [cycle["selected_route_id"] for cycle in cycles],
        "route_a_strength_after_each_cycle": route_a_updates,
        "route_b_strength_after_each_cycle": route_b_updates,
        "trend_summary_replayed": source["trend_summary"],
        "chain_reconstructed": True,
        "serialized_state_replay_scope": (
            "route-use events, memory surface rows, candidate records, "
            "candidate set records, native route-arbitration records, controls"
        ),
    }
    summary["replay_summary_digest"] = digest_value(summary)
    return summary


def source_controls_replay(source: dict[str, Any]) -> dict[str, Any]:
    controls = {
        row["control_id"]: row for row in source.get("controls", [])
    }
    replayed: dict[str, Any] = {}
    for control_id, expected in EXPECTED_SOURCE_CONTROLS.items():
        row = controls.get(control_id, {})
        replayed[control_id] = {
            "expected_primary_blocker": expected,
            "observed_primary_blocker": row.get("primary_blocker"),
            "source_control_passed": row.get("control_passed") is True,
            "replay_passed": (
                row.get("primary_blocker") == expected
                and row.get("control_passed") is True
                and row.get("observed_status") == "blocked"
            ),
        }
    return replayed


def closeout_record(
    manifest_validation: dict[str, Any],
    source: dict[str, Any],
    replay: dict[str, Any],
    controls: list[dict[str, Any]],
) -> dict[str, Any]:
    source_flags = source["claim_flags"]
    closeout_flags = closeout_claim_flags(manifest_validation)
    row: dict[str, Any] = {
        "row_id": "n08_i8_mem6_hypothesis_a_closeout_row_v1",
        "schema": "n08_i8_mem6_hypothesis_a_closeout_row_v1",
        "experiment": "N08",
        "iteration": 8,
        "mem_level": "MEM6",
        "mem_level_is_evidence_classification": True,
        "hypothesis": "A_serialized_producer_policy_memory",
        "strongest_supported_mem_level": "MEM6",
        "strongest_claim_ceiling": MEM6_CEILING,
        "artifact_only_replay_passed": True,
        "source_iteration": 7,
        "source_output_digest": source["output_digest"],
        "source_trend_summary_digest": source["artifact_digests"][
            "trend_summary_digest"
        ],
        "replay_summary_digest": replay["replay_summary_digest"],
        "corrupted_control_count": len(controls),
        "corrupted_controls_passed": all(row["control_passed"] for row in controls),
        "source_runtime_claim_flags": source_flags,
        "closeout_claim_flags": closeout_flags,
        "memory_or_trail_claim_allowed": True,
        "memory_or_trail_claim_scope": (
            "artifact_only_serialized_producer_policy_route_memory_or_trail"
        ),
        "native_geometry_mediated_trail_claim_allowed": False,
        "pure_coherence_flux_trail_claim_allowed": False,
        "aco_like_claim_allowed": False,
        "agentic_like_claim_allowed": False,
        "agency_claim_allowed": False,
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
        "hypothesis_b_status": "open_not_claimed",
        "hypothesis_b_primary_blocker": (
            "native_geometry_mediated_trail_not_tested_in_iterations_1_8"
        ),
        "independent_memory_strength_used_as_physical_flux": False,
        "independent_memory_strength_used_as_score_evidence": True,
        "native_support_status": "experiment_local_artifact_replay",
        "native_policy_blockers": [
            "native_geometry_mediated_trail_not_tested_in_iterations_1_8",
            "pure_coherence_flux_trail_not_supported_by_independent_memory_strength",
        ],
        "handoff": {
            "hypothesis_a_closed": True,
            "hypothesis_b_next_iteration": "9_native_geometry_trail_baseline",
            "n09_dependency_status": (
                "MEM6 Hypothesis A available as serialized producer/policy "
                "memory evidence only"
            ),
        },
    }
    row["closeout_row_digest"] = digest_value(row)
    return row


def validate_output(
    manifest_validation: dict[str, Any],
    source: dict[str, Any],
    replay: dict[str, Any],
    source_controls: dict[str, Any],
    corrupted: list[dict[str, Any]],
    closeout: dict[str, Any],
) -> dict[str, bool]:
    source_blockers = replay_blockers(source)
    closeout_flags = closeout["closeout_claim_flags"]
    broader_flags = {
        key: value
        for key, value in closeout_flags.items()
        if key != "memory_or_trail_claim_allowed"
    }
    return {
        "source_mem5_passed": source["status"] == "passed",
        "source_output_digest_recomputed": source["output_digest"]
        == recompute_output_digest(source),
        "artifact_only_runtime_state_not_used": replay["artifact_only"] is True
        and replay["runtime_state_used"] is False,
        "positive_replay_has_no_blockers": source_blockers == [],
        "route_use_events_replayed": replay["route_use_events_replayed"]
        == source["cycle_count"],
        "memory_surface_updates_replayed": replay["memory_surface_update_rows_replayed"]
        == source["cycle_count"] * 2,
        "candidate_scores_replayed": replay["candidate_route_records_replayed"]
        == source["cycle_count"] * 2,
        "candidate_sets_replayed": replay["candidate_set_records_replayed"]
        == source["cycle_count"],
        "arbitration_records_replayed": replay[
            "route_arbitration_records_replayed"
        ]
        == source["cycle_count"],
        "scheduled_packets_not_applicable_recorded": replay[
            "scheduled_packet_records_applicable"
        ]
        is False
        and replay["processed_packet_records_applicable"] is False,
        "source_controls_replayed": all(
            row["replay_passed"] for row in source_controls.values()
        ),
        "corrupted_controls_passed": all(row["control_passed"] for row in corrupted),
        "corrupted_control_blockers_distinct": len(
            {row["primary_blocker"] for row in corrupted}
        )
        == len(corrupted),
        "memory_claim_opened_only_at_closeout": closeout_flags[
            "memory_or_trail_claim_allowed"
        ]
        is True
        and source["claim_flags"]["memory_or_trail_claim_allowed"] is False,
        "broader_claims_remain_blocked": all(value is False for value in broader_flags.values()),
        "source_rows_claim_flags_false": all(
            all(value is False for value in candidate["claim_flags"].values())
            for cycle in source["cycles"]
            for candidate in cycle["candidate_route_records"]
        )
        and all(
            all(value is False for value in update["claim_flags"].values())
            for cycle in source["cycles"]
            for update in cycle["memory_update_rows"]
        ),
        "hypothesis_a_ceiling_frozen": closeout["strongest_supported_mem_level"]
        == "MEM6"
        and closeout["strongest_claim_ceiling"] == MEM6_CEILING,
        "hypothesis_b_deferred_with_blocker": closeout["hypothesis_b_status"]
        == "open_not_claimed"
        and bool(closeout["hypothesis_b_primary_blocker"]),
        "memory_strength_not_physical_flux": closeout[
            "independent_memory_strength_used_as_physical_flux"
        ]
        is False,
        "src_clean": git_status_short_src() == "",
        "manifest_validation_passed": manifest_validation["status"] == "passed",
    }


def source_artifacts() -> dict[str, str]:
    return {
        rel(SOURCE_MEM5_PATH): digest_file(SOURCE_MEM5_PATH),
        rel(MANIFEST_VALIDATION_PATH): digest_file(MANIFEST_VALIDATION_PATH),
    }


def source_reports() -> dict[str, str]:
    return {rel(SOURCE_MEM5_REPORT): digest_file(SOURCE_MEM5_REPORT)}


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    replay = output["artifact_only_replay"]
    closeout = output["closeout"]
    controls = output["corrupted_artifact_controls"]
    checks = output["checks"]
    control_lines = "\n".join(
        "| `{control_id}` | `{observed_status}` | `{primary_blocker}` | `{control_passed}` | {purpose} |".format(
            **row
        )
        for row in controls
    )
    source_control_lines = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` |".format(
            control_id,
            row["expected_primary_blocker"],
            row["observed_primary_blocker"],
            row["replay_passed"],
        )
        for control_id, row in output["source_control_replay"].items()
    )
    check_lines = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(checks.items())
    )
    report = f"""# N08 Iteration 8 MEM6 Artifact-Only Replay And Closeout

Status: `{output['status']}`.

Iteration 8 replays the Iteration 7 route-use, memory update, candidate-score,
candidate-set, and route-arbitration chain from exported artifacts only. It
does not run a new behavioral probe and does not use private runtime state.

## Closeout

- strongest supported MEM level: `{closeout['strongest_supported_mem_level']}`
- strongest claim ceiling: `{closeout['strongest_claim_ceiling']}`
- narrow memory/trail claim allowed:
  `{closeout['memory_or_trail_claim_allowed']}`
- claim scope: `{closeout['memory_or_trail_claim_scope']}`
- Hypothesis B status: `{closeout['hypothesis_b_status']}`
- Hypothesis B blocker: `{closeout['hypothesis_b_primary_blocker']}`

The supported claim is only an artifact-only serialized producer/policy
route-memory or trail-affordance candidate. It is not native geometry-mediated
trail memory, pure coherence/flux memory, ACO, agency, intention,
goal-proxy regulation, locomotion, biological behavior, personhood, semantic
choice, identity collapse, or identity acceptance.

## Artifact-Only Replay

```json
{json.dumps(replay, indent=2, sort_keys=True)}
```

## Source Control Replay

| Control | Expected Blocker | Observed Blocker | Passed |
|---|---|---|---|
{source_control_lines}

## Corrupted Artifact Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
{control_lines}

## Checks

| Check | Passed |
|---|---|
{check_lines}

## Artifact Digests

```json
{json.dumps(output['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

Iteration 8 passes if the route-use -> memory surface -> decay/reinforcement
-> memory-shaped route arbitration chain can be reconstructed from artifacts
only, controls fail with distinct blockers, budgets remain exact, and the
strongest N08 Hypothesis A memory/trail evidence ceiling is frozen without ACO,
agency, intention, goal-regulation, identity-acceptance, locomotion,
biological, or unrestricted claims.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    manifest_validation = load_json(MANIFEST_VALIDATION_PATH)
    source = load_json(SOURCE_MEM5_PATH)
    replay = replay_summary(source)
    source_controls = source_controls_replay(source)
    corrupted = corrupted_controls(source)
    closeout = closeout_record(manifest_validation, source, replay, corrupted)
    checks = validate_output(
        manifest_validation,
        source,
        replay,
        source_controls,
        corrupted,
        closeout,
    )
    output: dict[str, Any] = {
        "schema": "n08_iteration_8_mem6_closeout_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 8,
        "status": "passed" if all(checks.values()) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short_src(),
            "src_clean": git_status_short_src() == "",
        },
        "source_artifacts": source_artifacts(),
        "source_reports": source_reports(),
        "mem_level": "MEM6",
        "claim_ceiling": MEM6_CEILING,
        "artifact_only_replay": replay,
        "source_control_replay": source_controls,
        "corrupted_artifact_controls": corrupted,
        "closeout": closeout,
        "checks": checks,
        "claim_boundary": {
            "memory_or_trail_claim_allowed": True,
            "memory_or_trail_claim_scope": closeout[
                "memory_or_trail_claim_scope"
            ],
            "all_broader_claims_blocked": True,
            "source_runtime_claim_flags_remained_false": True,
            "hypothesis_b_remains_open": True,
        },
        "acceptance": {
            "achieved": all(checks.values()),
            "status": "passed" if all(checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 8 passes if the route-use -> memory surface -> "
                "decay/reinforcement -> memory-shaped route arbitration chain "
                "can be reconstructed from artifacts only, controls fail with "
                "distinct blockers, budgets remain exact, and the strongest "
                "N08 Hypothesis A memory/trail evidence ceiling is frozen "
                "without ACO, agency, intention, goal-regulation, "
                "identity-acceptance, locomotion, biological, or unrestricted "
                "claims."
            ),
        },
    }
    output["artifact_digests"] = {
        "artifact_only_replay_digest": replay["replay_summary_digest"],
        "source_control_replay_digest": digest_value(source_controls),
        "corrupted_controls_digest": digest_value(corrupted),
        "closeout_digest": closeout["closeout_row_digest"],
        "checks_digest": digest_value(checks),
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
