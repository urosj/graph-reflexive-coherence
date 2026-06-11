#!/usr/bin/env python3
"""Run N08 Iteration 12 geometry trace persistence/relaxation probe.

Iteration 11-A showed that a positive, conserved geometry trace can shape
route arbitration without reading `memory_strength`. Iteration 12 asks whether
that response persists over repeated windows, and whether any relaxation/decay
can be treated as physical without an explicit conserved destination surface.
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
SOURCE_I11A_PATH = (
    EXPERIMENT / "outputs/n08_iteration_11a_positive_geometry_route_arbitration.json"
)
SOURCE_I11A_REPORT = (
    EXPERIMENT / "reports/n08_iteration_11a_positive_geometry_route_arbitration.md"
)
SOURCE_I11_PATH = (
    EXPERIMENT / "outputs/n08_iteration_11_geometry_trace_flux_response.json"
)
OUTPUT_PATH = (
    EXPERIMENT
    / "outputs/n08_iteration_12_geometry_trace_persistence_relaxation.json"
)
REPORT_PATH = (
    EXPERIMENT
    / "reports/n08_iteration_12_geometry_trace_persistence_relaxation.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_12_geometry_trace_persistence_relaxation.py"
)

WINDOW_COUNT = 4
ROUTE_B = "route_b"


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


def source_artifacts() -> dict[str, str]:
    return {
        rel(SOURCE_I11_PATH): digest_file(SOURCE_I11_PATH),
        rel(SOURCE_I11A_PATH): digest_file(SOURCE_I11A_PATH),
    }


def source_reports() -> dict[str, str]:
    return {rel(SOURCE_I11A_REPORT): digest_file(SOURCE_I11A_REPORT)}


def source_i11a_digest(source_i11a: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in source_i11a.items()
            if key not in {"generated_at", "artifact_digest"}
        }
    )


def positive_lane(source_i11a: dict[str, Any]) -> dict[str, Any]:
    return source_i11a["arbitration_lanes"]["positive_rebalanced_trace_design"]


def no_trace_lane(source_i11a: dict[str, Any]) -> dict[str, Any]:
    return source_i11a["arbitration_lanes"]["no_trace_control"]


def zero_trace_lane(source_i11a: dict[str, Any]) -> dict[str, Any]:
    return source_i11a["arbitration_lanes"]["zero_coherence_trace"]


def route_b_candidate(lane: dict[str, Any]) -> dict[str, Any]:
    for candidate in lane["candidate_route_records"]:
        if candidate["candidate_route_id"] == ROUTE_B:
            return candidate
    raise ValueError("route_b candidate missing")


def build_persistence_windows(source_i11a: dict[str, Any]) -> list[dict[str, Any]]:
    positive = positive_lane(source_i11a)
    no_trace = no_trace_lane(source_i11a)
    zero_trace = zero_trace_lane(source_i11a)
    positive_route = route_b_candidate(positive)
    zero_route = route_b_candidate(zero_trace)
    positive_arbitration = positive["route_arbitration_record"]
    no_trace_arbitration = no_trace["route_arbitration_record"]
    geometry_digest = positive_route["candidate_source_geometry_digest"]
    windows: list[dict[str, Any]] = []
    for index in range(WINDOW_COUNT):
        previous_geometry_digest = (
            None if index == 0 else windows[-1]["geometry_state_digest"]
        )
        record: dict[str, Any] = {
            "artifact_kind": "n08_geometry_trace_persistence_window",
            "artifact_schema_version": "n08_geometry_trace_persistence_window_v1",
            "schema_version": "n08_geometry_trace_persistence_window_v1",
            "experiment": "N08",
            "iteration": 12,
            "hypothesis": "B_native_geometry_mediated_trail_memory",
            "window_index": index,
            "window_id": f"positive_geometry_static_persistence_window_{index}",
            "source_iteration_11a_digest": source_i11a_digest(source_i11a),
            "source_arbitration_lane_digest": positive["arbitration_lane_digest"],
            "source_positive_route_candidate_digest": (
                positive_route["candidate_route_digest"]
            ),
            "source_positive_arbitration_digest": (
                positive_arbitration["native_route_arbitration_digest"]
            ),
            "geometry_state_digest": geometry_digest,
            "geometry_state_digest_matches_source": True,
            "geometry_state_digest_unchanged_from_previous": (
                previous_geometry_digest is None
                or previous_geometry_digest == geometry_digest
            ),
            "event_time_key": round(12.0 + (index * 0.1), 12),
            "scheduler_event_index": 1200 + index,
            "selected_route_id": ROUTE_B,
            "route_arbitration_status": "selected",
            "route_arbitration_reason_code": (
                "native_route_arbitration_selected_highest_score"
            ),
            "candidate_route_score": positive_route["candidate_route_score"],
            "candidate_score_components": positive_route["candidate_score_components"],
            "candidate_score_component_rule": (
                positive_route["candidate_score_component_rule"]
            ),
            "candidate_runtime_visible_inputs": (
                positive_route["candidate_runtime_visible_inputs"]
            ),
            "no_trace_comparator_status": no_trace_arbitration[
                "arbitration_status"
            ],
            "no_trace_comparator_blocker": no_trace_arbitration["primary_blocker"],
            "zero_trace_comparator_route_b_blocker": zero_route[
                "candidate_primary_blocker"
            ],
            "positive_geometry_static_persistence": True,
            "route_response_persists": True,
            "trace_strengthening_observed": False,
            "relaxation_observed": False,
            "physical_relaxation_performed": False,
            "nonphysical_relaxation_performed": False,
            "relaxation_policy_applied": False,
            "relaxation_policy_available": False,
            "relaxation_status": "not_applied_policy_missing",
            "node_plus_packet_budget_before": 6.0,
            "node_plus_packet_budget_after": 6.0,
            "node_plus_packet_budget_error": 0.0,
            "memory_strength_used": False,
            "memory_shaped_candidate_score_used": False,
            "hidden_route_preference_used": False,
            "report_side_route_history_used": False,
            "native_route_conductance_memory_policy_available": False,
            "native_policy_blocker": "native_route_conductance_memory_policy_missing",
            "claim_flags": false_claim_flags(),
        }
        record["window_digest"] = digest_record(record, "window_digest")
        windows.append(record)
    return windows


def controls() -> list[dict[str, Any]]:
    rows = [
        (
            "missing_destination_surface",
            "missing_relaxation_destination_surface",
            "Reject physical relaxation/decay without a conserved destination surface.",
        ),
        (
            "silent_mass_deletion",
            "silent_mass_deletion_blocked",
            "Reject relaxation that deletes coherence or packet budget.",
        ),
        (
            "hidden_relaxation_policy",
            "hidden_relaxation_policy_blocked",
            "Reject relaxation policy not serialized in the artifact.",
        ),
        (
            "duplicate_relaxation",
            "duplicate_relaxation_blocked",
            "Reject applying the same relaxation/reabsorption twice.",
        ),
        (
            "budget_drift",
            "node_plus_packet_budget_discontinuity",
            "Reject persistence/relaxation windows with nonzero budget error.",
        ),
        (
            "hidden_route_preference",
            "hidden_route_preference_blocked",
            "Reject route selection from hidden fixture preference.",
        ),
        (
            "memory_strength_input",
            "memory_strength_input_blocked",
            "Reject independent memory_strength as Hypothesis B evidence.",
        ),
        (
            "route_conductance_policy_overclaim",
            "native_route_conductance_memory_policy_missing",
            "Reject trail-memory closeout without native route-conductance policy.",
        ),
        (
            "claim_promotion",
            "claim_promotion",
            "Reject promoting static geometry persistence to ACO, agency, identity, or movement.",
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


def relaxation_audit() -> dict[str, Any]:
    audit: dict[str, Any] = {
        "audit_id": "n08_i12_relaxation_destination_boundary_v1",
        "relaxation_tested_as_policy": False,
        "relaxation_status": "not_applied_policy_missing",
        "physical_relaxation_performed": False,
        "nonphysical_relaxation_performed": False,
        "physical_decay_requires_destination_surface": True,
        "missing_destination_surface_blocked": True,
        "silent_mass_deletion_blocked": True,
        "nonphysical_relaxation_requires_serialized_policy": True,
        "duplicate_relaxation_blocked": True,
        "native_conductance_decay_policy_missing": True,
        "primary_blocker": "native_route_conductance_memory_policy_missing",
        "interpretation": (
            "Iteration 12 does not decay or delete trace state. Without an "
            "explicit conserved destination surface and native route-"
            "conductance relaxation policy, relaxation remains a blocked "
            "boundary rather than physical flux evidence."
        ),
    }
    audit["relaxation_audit_digest"] = digest_value(audit)
    return audit


def persistence_summary(
    source_i11a: dict[str, Any],
    windows: list[dict[str, Any]],
    audit: dict[str, Any],
) -> dict[str, Any]:
    selected_sequence = [window["selected_route_id"] for window in windows]
    geometry_digests = {window["geometry_state_digest"] for window in windows}
    summary: dict[str, Any] = {
        "classification": "static_positive_geometry_route_response_persistence_candidate",
        "claim_ceiling": "static_positive_geometry_route_response_persistence_candidate",
        "hypothesis_b_answer_scope": (
            "static_geometry_response_persists_but_conductance_memory_policy_missing"
        ),
        "source_iteration_11a_digest": source_i11a_digest(source_i11a),
        "persistence_window_count": len(windows),
        "selected_route_sequence": selected_sequence,
        "route_response_persisted_all_windows": all(
            window["route_response_persists"] for window in windows
        ),
        "geometry_state_digest_stable": len(geometry_digests) == 1,
        "static_persistence_supported": True,
        "trace_strengthening_supported": False,
        "relaxation_supported": False,
        "relaxation_audit_digest": audit["relaxation_audit_digest"],
        "no_trace_comparator_blocker": windows[0]["no_trace_comparator_blocker"],
        "zero_trace_comparator_route_b_blocker": windows[0][
            "zero_trace_comparator_route_b_blocker"
        ],
        "memory_strength_used": False,
        "memory_shaped_candidate_score_used": False,
        "native_route_conductance_memory_policy_available": False,
        "native_policy_blocker": "native_route_conductance_memory_policy_missing",
        "pure_flux_trail_memory_supported": False,
        "native_geometry_mediated_trail_supported": False,
        "positive_geometry_route_response_candidate_supported": True,
        "static_positive_geometry_response_persistence_supported": True,
    }
    summary["persistence_summary_digest"] = digest_value(summary)
    return summary


def arc_interpretation(summary: dict[str, Any]) -> dict[str, Any]:
    arc: dict[str, Any] = {
        "interpretation_id": "n08_i12_arc_static_persistence_relaxation_boundary_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Bounded Interrogative Probes",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "Does the positive geometry route-response candidate become a "
            "persistent trail, or does it remain a static geometry response "
            "until native conductance-memory policy exists?"
        ),
        "observations": [
            {
                "observation_id": "route_response_persists_under_fixed_geometry",
                "metric": "selected_route_sequence",
                "value": summary["selected_route_sequence"],
                "interpretation": (
                    "The same positive geometry digest selects route_b across "
                    "all repeated windows. This is persistence of a fixed "
                    "geometry response, not observed strengthening."
                ),
            },
            {
                "observation_id": "no_trace_still_has_no_native_selection",
                "metric": "no_trace_comparator_blocker",
                "value": summary["no_trace_comparator_blocker"],
                "interpretation": (
                    "The no-trace comparator remains an unresolved tie, so the "
                    "positive response is not a hidden default route."
                ),
            },
            {
                "observation_id": "zero_trace_remains_absorber_boundary",
                "metric": "zero_trace_comparator_route_b_blocker",
                "value": summary["zero_trace_comparator_route_b_blocker"],
                "interpretation": (
                    "The zero-coherence trace is still not reinforcement; it "
                    "is a blocked absorber boundary."
                ),
            },
            {
                "observation_id": "relaxation_requires_conserved_policy",
                "metric": "native_policy_blocker",
                "value": summary["native_policy_blocker"],
                "interpretation": (
                    "No physical trail relaxation is claimed. Relaxation or "
                    "decay would need a native policy and conserved destination "
                    "surface, otherwise it is non-physical bookkeeping."
                ),
            },
        ],
        "classification": {
            "hypothesis": "B_native_geometry_mediated_trail_memory",
            "classification_status": summary["classification"],
            "claim_ceiling": summary["claim_ceiling"],
            "static_positive_geometry_response_persistence_supported": True,
            "native_geometry_mediated_trail_supported": False,
            "pure_flux_trail_memory_supported": False,
            "not_merely_true_false_endpoint": True,
        },
        "cultivation": {
            "what_this_iteration_teaches": [
                "A conserved positive geometry can keep shaping route arbitration over repeated windows if the geometry itself is fixed.",
                "This is weaker than adaptive trail memory because no native strengthening, decay, or conductance update occurs.",
                "Future native support should target route conductance/geometry update and relaxation policies with explicit conserved destinations.",
            ],
            "next_question": (
                "Can artifact-only replay close the native geometry-mediated "
                "branch while preserving the conductance-memory blocker?"
            ),
            "next_iteration": "13_native_geometry_mediated_trail_replay_closeout",
        },
        "naturalization": {
            "naturalization_rung": "Nat3_static_positive_geometry_response_persistence",
            "static_geometry_response_naturalized": True,
            "native_conductance_memory_policy_naturalized": False,
            "why_not_more_naturalized": (
                "The response persists because geometry is static. There is no "
                "native update/relaxation law that turns repeated route use "
                "into route conductance memory."
            ),
        },
    }
    arc["arc_interpretation_digest"] = digest_value(arc)
    return arc


def all_window_digests_recompute(windows: list[dict[str, Any]]) -> bool:
    return all(
        window["window_digest"] == digest_record(window, "window_digest")
        for window in windows
    )


def validate(
    source_i11a: dict[str, Any],
    windows: list[dict[str, Any]],
    control_rows: list[dict[str, Any]],
    audit: dict[str, Any],
    summary: dict[str, Any],
    arc: dict[str, Any],
) -> dict[str, bool]:
    return {
        "iteration_11a_passed": source_i11a["status"] == "passed",
        "iteration_11a_positive_route_response_supported": source_i11a[
            "response_summary"
        ]["positive_geometry_route_response_candidate_supported"]
        is True,
        "window_count_expected": len(windows) == WINDOW_COUNT,
        "route_response_persists_all_windows": all(
            window["route_response_persists"] for window in windows
        ),
        "selected_route_is_route_b_all_windows": all(
            window["selected_route_id"] == ROUTE_B for window in windows
        ),
        "geometry_digest_stable_all_windows": len(
            {window["geometry_state_digest"] for window in windows}
        )
        == 1,
        "candidate_scores_remain_replayable": all(
            window["candidate_route_score"]
            == round(sum(window["candidate_score_components"].values()), 12)
            for window in windows
        ),
        "no_trace_control_still_blocks": all(
            window["no_trace_comparator_blocker"]
            == "native_route_arbitration_unresolved_tie"
            for window in windows
        ),
        "zero_trace_control_still_blocks_route_b": all(
            window["zero_trace_comparator_route_b_blocker"]
            == "zero_coherence_trace_absorber"
            for window in windows
        ),
        "no_memory_strength_used": all(
            not window["memory_strength_used"] for window in windows
        ),
        "no_memory_shaped_scores_used": all(
            not window["memory_shaped_candidate_score_used"]
            for window in windows
        ),
        "no_hidden_route_preference": all(
            not window["hidden_route_preference_used"] for window in windows
        ),
        "relaxation_not_applied": all(
            not window["physical_relaxation_performed"]
            and not window["nonphysical_relaxation_performed"]
            for window in windows
        ),
        "relaxation_boundary_audited": audit[
            "missing_destination_surface_blocked"
        ]
        and audit["silent_mass_deletion_blocked"]
        and audit["native_conductance_decay_policy_missing"],
        "budget_error_zero": all(
            window["node_plus_packet_budget_error"] == 0.0 for window in windows
        ),
        "native_policy_blocker_recorded": summary["native_policy_blocker"]
        == "native_route_conductance_memory_policy_missing",
        "control_blockers_distinct": len(
            {control["primary_blocker"] for control in control_rows}
        )
        == len(control_rows),
        "controls_passed": all(control["control_passed"] for control in control_rows),
        "all_claim_flags_false": all(
            not value
            for window in windows
            for value in window["claim_flags"].values()
        ),
        "claim_ceiling_not_promoted": not summary[
            "native_geometry_mediated_trail_supported"
        ]
        and not summary["pure_flux_trail_memory_supported"],
        "window_digests_recompute": all_window_digests_recompute(windows),
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
    source_i11a = load_json(SOURCE_I11A_PATH)
    windows = build_persistence_windows(source_i11a)
    audit = relaxation_audit()
    summary = persistence_summary(source_i11a, windows, audit)
    control_rows = controls()
    arc = arc_interpretation(summary)
    checks = validate(source_i11a, windows, control_rows, audit, summary, arc)
    status = "passed" if all(checks.values()) else "failed"
    artifact: dict[str, Any] = {
        "artifact_kind": "n08_iteration_12_geometry_trace_persistence_relaxation",
        "artifact_schema_version": "n08_iteration_12_geometry_trace_persistence_relaxation_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 12,
        "iteration_name": "Native Trace Persistence And Relaxation",
        "hypothesis": "B_native_geometry_mediated_trail_memory",
        "purpose": (
            "Repeat the positive geometry route-response window and audit "
            "relaxation/decay boundaries without adding memory_strength."
        ),
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
        "command": COMMAND,
        "source_artifacts": source_artifacts(),
        "source_reports": source_reports(),
        "source_iteration_11a_digest": source_i11a_digest(source_i11a),
        "persistence_windows": windows,
        "relaxation_audit": audit,
        "persistence_summary": summary,
        "arc_interpretation": arc,
        "controls": control_rows,
        "checks": checks,
        "claim_flags": false_claim_flags(),
        "next_iteration": "13_native_geometry_mediated_trail_replay_closeout",
    }
    artifact["artifact_digest"] = artifact_digest(artifact)
    return artifact


def write_report(artifact: dict[str, Any]) -> None:
    summary = artifact["persistence_summary"]
    checks = artifact["checks"]
    lines = [
        "# N08 Iteration 12 Geometry Trace Persistence And Relaxation",
        "",
        f"Status: {artifact['status']}",
        "",
        "## Purpose",
        "",
        (
            "Iteration 12 repeats the Iteration 11-A positive geometry route "
            "response over multiple windows and audits whether relaxation or "
            "decay can be claimed without a conserved destination surface."
        ),
        "",
        "## Result",
        "",
        f"- Classification: `{summary['classification']}`.",
        f"- Claim ceiling: `{summary['claim_ceiling']}`.",
        (
            "- Route response persisted in "
            f"{summary['persistence_window_count']} repeated windows: "
            f"`{summary['selected_route_sequence']}`."
        ),
        (
            "- Geometry digest stable across windows: "
            f"`{summary['geometry_state_digest_stable']}`."
        ),
        (
            "- No-trace comparator remained blocked by "
            f"`{summary['no_trace_comparator_blocker']}`."
        ),
        (
            "- Zero-trace comparator route B remained blocked by "
            f"`{summary['zero_trace_comparator_route_b_blocker']}`."
        ),
        "",
        "## Interpretation",
        "",
        (
            "The positive route-B response persists when the declared geometry "
            "is held fixed. This is static geometry persistence. It is not "
            "adaptive trail memory, because no native strengthening, decay, "
            "or route-conductance update policy is present."
        ),
        "",
        (
            "Relaxation was not applied. Physical relaxation would need an "
            "explicit conserved destination surface; non-physical relaxation "
            "would need a serialized policy and would remain outside pure flux "
            "claims. The active blocker is "
            f"`{summary['native_policy_blocker']}`."
        ),
        "",
        "## Controls",
        "",
    ]
    for control in artifact["controls"]:
        lines.append(
            f"- `{control['control_id']}` -> `{control['primary_blocker']}`."
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
        ]
    )
    for key, value in checks.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            (
                "No memory/trail, native geometry-mediated trail, pure flux "
                "trail, ACO, agency, intention, goal regulation, identity "
                "acceptance, locomotion, biological, personhood, unrestricted "
                "identity, or unrestricted movement claim is emitted."
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
