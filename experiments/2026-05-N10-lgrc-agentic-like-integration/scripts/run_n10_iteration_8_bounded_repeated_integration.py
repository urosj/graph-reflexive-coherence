#!/usr/bin/env python3
"""Run N10 Iteration 8 bounded repeated integration.

Iteration 8 extends the Iteration 7 ALI4 composition across a bounded
four-cycle replay window. It keeps the same claim boundary: this is an ALI5
bounded repeated integration row, not the final A6/ALI6 closeout. Iteration 9
remains responsible for the artifact-only closeout validator.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
BASELINE_PATH = EXPERIMENT / "outputs" / "n10_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n10_integration_fixture_manifest_v1.json"
ITERATION_7_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_7_route_memory_regulation_composition.json"
)
N09_GPR5_PATH = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "outputs"
    / "n09_iteration_7_gpr5_repeated_bounded_regulation.json"
)
N09_GPR5_REPORT_PATH = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "reports"
    / "n09_iteration_7_gpr5_repeated_bounded_regulation.md"
)
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_8_bounded_repeated_integration.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n10_iteration_8_bounded_repeated_integration.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "run_n10_iteration_8_bounded_repeated_integration.py"
)
WINDOW_COUNT = 4


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
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def with_digest(record: dict[str, Any], digest_field: str) -> dict[str, Any]:
    result = dict(record)
    result[digest_field] = digest_value(
        {key: value for key, value in result.items() if key != digest_field}
    )
    return result


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def source_path(baseline: dict[str, Any], key: str) -> Path:
    return ROOT / baseline["source_artifacts"][key]["path"]


def report_path(baseline: dict[str, Any], key: str) -> Path:
    return ROOT / baseline["source_reports"][key]["path"]


def find_lane(rows: list[dict[str, Any]], lane_id: str) -> dict[str, Any]:
    for row in rows:
        if row.get("lane_id") == lane_id:
            return row
    raise KeyError(f"lane not found: {lane_id}")


def source_support_state_tag(manifest: dict[str, Any], support_lane: dict[str, Any]) -> str:
    outcome = support_lane["identity_support_outcome_tag"]
    return manifest["allowed_values"]["source_support_outcome_map"][outcome]


def build_source_records(
    baseline: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_keys = [
        "n06_closeout",
        "n07_withdrawal_baseline",
        "n08_hypothesis_a_closeout",
        "n09_hypothesis_a_closeout",
    ]
    report_keys = [
        "n06_closeout",
        "n07_withdrawal_baseline",
        "n08_hypothesis_a_closeout",
        "n09_hypothesis_a_closeout",
    ]
    source_artifacts = {
        "n10_baseline_inventory": {
            "path": rel(BASELINE_PATH),
            "sha256": digest_file(BASELINE_PATH),
        },
        "n10_fixture_manifest": {
            "path": rel(MANIFEST_PATH),
            "sha256": digest_file(MANIFEST_PATH),
        },
        "n10_iteration_7_route_memory_regulation_composition": {
            "path": rel(ITERATION_7_PATH),
            "sha256": digest_file(ITERATION_7_PATH),
        },
        "n09_gpr5_repeated_bounded_regulation": {
            "path": rel(N09_GPR5_PATH),
            "sha256": digest_file(N09_GPR5_PATH),
        },
    }
    for key in artifact_keys:
        path = source_path(baseline, key)
        current_digest = digest_file(path)
        source_artifacts[key] = {
            "path": rel(path),
            "sha256": current_digest,
            "baseline_sha256": baseline["source_artifacts"][key]["sha256"],
            "matches_baseline": current_digest
            == baseline["source_artifacts"][key]["sha256"],
        }

    source_reports = {
        "n09_gpr5_repeated_bounded_regulation": {
            "path": rel(N09_GPR5_REPORT_PATH),
            "sha256": digest_file(N09_GPR5_REPORT_PATH),
        }
    }
    for key in report_keys:
        path = report_path(baseline, key)
        current_digest = digest_file(path)
        source_reports[key] = {
            "path": rel(path),
            "sha256": current_digest,
            "baseline_sha256": baseline["source_reports"][key]["sha256"],
            "matches_baseline": current_digest
            == baseline["source_reports"][key]["sha256"],
        }
    return source_artifacts, source_reports


def support_summary(
    manifest: dict[str, Any],
    support_lane: dict[str, Any],
    manifest_lane: dict[str, Any],
) -> dict[str, Any]:
    return {
        "source_lane_id": support_lane["lane_id"],
        "support_state_tag": source_support_state_tag(manifest, support_lane),
        "lane_digest": support_lane["lane_digest"],
        "manifest_lane_digest": manifest_lane["lane_digest"],
        "identity_support_outcome_tag": support_lane["identity_support_outcome_tag"],
        "support_survival_passed": support_lane["support_survival_passed"],
        "support_survival_threshold": support_lane["support_survival_threshold"],
        "final_A_support_retention": support_lane["final_A_support_retention"],
        "reference_A_support_retention": support_lane["reference_A_support_retention"],
        "final_basin_separability": support_lane["final_basin_separability"],
        "support_loss_from_reference": support_lane["support_loss_from_reference"],
        "final_budget_error": support_lane["final_budget_error"],
        "withdrawal_depth": support_lane["withdrawal_depth"],
        "withdrawal_kind": support_lane["withdrawal_kind"],
        "restoration_fraction": support_lane["restoration_fraction"],
    }


def bounded_cycle_rows(
    *,
    n06: dict[str, Any],
    n08: dict[str, Any],
    n09_gpr5: dict[str, Any],
    support: dict[str, Any],
    route_context_tag: str,
) -> list[dict[str, Any]]:
    route_cycles = n06["artifact_only_closeout"]["per_cycle"]
    memory_replay = n08["artifact_only_replay"]
    regulation_cycles = n09_gpr5["memory_shaped_lane"]["cycles"]
    rows = []
    for index in range(WINDOW_COUNT):
        route = route_cycles[index]
        regulation = regulation_cycles[index]
        response = regulation["regulation_response"]
        candidate = regulation["cycle_candidate_record"]
        budget = regulation["budget"]
        row = {
            "cycle_index": index + 1,
            "route_cycle_id": route["cycle_id"],
            "route_context_tag": route_context_tag,
            "route_selected_route": route["selected_route"],
            "route_candidate_set_digest": route["candidate_set_digest"],
            "route_selected_candidate_route_digest": route[
                "selected_candidate_route_digest"
            ],
            "route_selected_candidate_route_score": route[
                "selected_candidate_route_score"
            ],
            "route_replay_ok": route["replay_ok"],
            "route_selection_contract_valid_under_pre_topology_scope": route[
                "selection_contract_valid_under_pre_topology_scope"
            ],
            "route_scheduled_processed_packet_applicability": route[
                "scheduled_processed_packet_evidence"
            ]["applicability"],
            "memory_selected_route": memory_replay["selected_routes"][index],
            "memory_route_a_strength_after_cycle": memory_replay[
                "route_a_strength_after_each_cycle"
            ][index],
            "memory_route_b_strength_after_cycle": memory_replay[
                "route_b_strength_after_each_cycle"
            ][index],
            "memory_surface_scope": n08["closeout"][
                "memory_or_trail_claim_scope"
            ],
            "memory_strength_used_as_physical_flux": n08["closeout"][
                "independent_memory_strength_used_as_physical_flux"
            ],
            "regulation_cycle_index": regulation["cycle_index"],
            "regulation_response_digest": response["regulation_response_digest"],
            "regulation_outcome_tag": response["regulation_outcome_tag"],
            "regulation_selected_route": candidate["selected_candidate_route_source_id"],
            "regulation_selected_candidate_route_digest": response[
                "selected_candidate_route_digest"
            ],
            "regulation_top_ranked_is_unique": candidate["top_ranked_is_unique"],
            "regulation_scheduled_packet_id": response["scheduled_packet_id"],
            "regulation_processed_packet_id": response["processed_packet_id"],
            "regulation_error_signal_digest": response["error_signal_digest"],
            "regulation_proxy_surface_digest": response["proxy_surface_digest"],
            "regulation_pre_response_proxy_surface_digest": response[
                "pre_response_proxy_surface_digest"
            ],
            "regulation_post_response_proxy_surface_digest": response[
                "post_response_proxy_surface_digest"
            ],
            "node_plus_packet_budget_before": budget[
                "node_plus_packet_budget_before"
            ],
            "node_plus_packet_budget_after": budget["node_plus_packet_budget_after"],
            "node_plus_packet_budget_error": budget[
                "node_plus_packet_budget_error"
            ],
            "memory_budget_surface": response["memory_budget_surface"],
            "memory_budget_error": response["memory_budget_error"],
            "proxy_budget_surface": response["proxy_budget_surface"],
            "proxy_budget_error": response["proxy_budget_error"],
            "support_lane_id": support["source_lane_id"],
            "support_state_tag": support["support_state_tag"],
            "support_lane_digest": support["lane_digest"],
            "support_retention": support["final_A_support_retention"],
            "support_survival_passed": support["support_survival_passed"],
            "support_budget_error": support["final_budget_error"],
            "route_source_current": route["replay_ok"]
            and route["checks"]["native_selection_replayable_under_selection_only_scope"]
            and route["scheduled_processed_packet_evidence"]["applicability"]
            == "not_applicable_pre_topology_selection_only_scope",
            "memory_source_current": memory_replay["chain_reconstructed"]
            and n08["closeout"]["artifact_only_replay_passed"]
            and not n08["closeout"]["independent_memory_strength_used_as_physical_flux"],
            "support_source_current": support["lane_digest"]
            == support["manifest_lane_digest"]
            and support["support_survival_passed"]
            and support["final_budget_error"] == 0.0,
            "regulation_source_current": response["scheduled_packet_id"] is not None
            and response["processed_packet_id"] is not None
            and response["regulation_outcome_tag"] == "single_cycle_band_return"
            and candidate["top_ranked_is_unique"]
            and budget["node_plus_packet_budget_error"] == 0.0,
            "claim_flags_false": all(
                value is False for value in response["claim_flags"].values()
            ),
        }
        rows.append(with_digest(row, "bounded_cycle_row_digest"))
    return rows


def max_abs(values: list[float]) -> float:
    return max(abs(value) for value in values)


def build_integration_row(
    *,
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    fixture_lane: dict[str, Any],
    support: dict[str, Any],
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
    iteration_7: dict[str, Any],
    cycle_rows: list[dict[str, Any]],
    row_id: str,
    companion: bool,
) -> dict[str, Any]:
    claim_flags = {key: False for key in sorted(manifest["claim_flags"])}
    policy = manifest["integration_policy"]
    all_budget_errors = [row["node_plus_packet_budget_error"] for row in cycle_rows]
    row = {
        "integration_row_id": row_id,
        "integration_level": "A5",
        "attempted_integration_level": "A6",
        "accepted_integration_level": "A5",
        "n10_category_level": "ALI5",
        "integration_policy_id": policy["integration_policy_id"],
        "integration_policy_digest": policy["integration_policy_digest"],
        "event_time_key": f"artifact_replay_n10_i8_{fixture_lane['lane_id']}",
        "scheduler_event_index": None,
        "source_experiment_ids": ["N06", "N07", "N08", "N09", "N10"],
        "source_artifacts": {
            key: value["path"] for key, value in source_artifacts.items()
        },
        "source_reports": {
            key: value["path"] for key, value in source_reports.items()
        },
        "source_artifact_digests": {
            key: value["sha256"] for key, value in source_artifacts.items()
        },
        "route_choice_artifact": "n06_closeout",
        "route_choice_digest": source_artifacts["n06_closeout"]["sha256"],
        "memory_affordance_artifact": "n08_hypothesis_a_closeout",
        "memory_affordance_digest": source_artifacts[
            "n08_hypothesis_a_closeout"
        ]["sha256"],
        "identity_support_artifact": "n07_withdrawal_baseline",
        "identity_support_digest": source_artifacts["n07_withdrawal_baseline"][
            "sha256"
        ],
        "goal_proxy_regulation_artifact": "n09_gpr5_repeated_bounded_regulation",
        "goal_proxy_regulation_digest": source_artifacts[
            "n09_gpr5_repeated_bounded_regulation"
        ]["sha256"],
        "support_state_tag": support["support_state_tag"],
        "route_context_tag": fixture_lane["required_route_context_tag"],
        "memory_scope_tag": "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "regulation_scope_tag": "artifact_only_goal_proxy_regulation_candidate",
        "integration_outcome_tag": "bounded_artifact_only_agentic_like_integration_candidate"
        if not companion
        else "route_memory_regulation_composition_candidate",
        "node_plus_packet_budget_before": cycle_rows[0][
            "node_plus_packet_budget_before"
        ],
        "node_plus_packet_budget_after": cycle_rows[-1][
            "node_plus_packet_budget_after"
        ],
        "node_plus_packet_budget_error": max_abs(all_budget_errors),
        "memory_budget_surface": "n08_source_memory_and_n09_trail_strength_surfaces_separate",
        "proxy_budget_surface": "n09_active_node_coherence_band_proxy_surface",
        "artifact_only": True,
        "runtime_state_used": False,
        "producer_scaffold_used": True,
        "native_policy_gap": baseline["native_policy_gaps"],
        "blocked_claims": baseline["claim_boundary"]["blocked_claims"],
        "claim_flags": claim_flags,
        "bounded_window": {
            "window_count": len(cycle_rows),
            "window_digest": digest_value(cycle_rows),
            "cycle_row_digests": [
                row["bounded_cycle_row_digest"] for row in cycle_rows
            ],
            "all_cycle_rows_source_current": all(
                row["route_source_current"]
                and row["memory_source_current"]
                and row["support_source_current"]
                and row["regulation_source_current"]
                for row in cycle_rows
            ),
            "all_cycle_budgets_exact": all(
                row["node_plus_packet_budget_error"] == 0.0
                and row["memory_budget_error"] == 0.0
                and row["proxy_budget_error"] == 0.0
                and row["support_budget_error"] == 0.0
                for row in cycle_rows
            ),
            "all_cycle_claim_flags_false": all(
                row["claim_flags_false"] for row in cycle_rows
            ),
            "duplicate_cycle_rows_suppressed": len(
                {row["bounded_cycle_row_digest"] for row in cycle_rows}
            )
            == len(cycle_rows),
        },
        "bounded_cycle_rows": cycle_rows,
        "support_evidence": support,
        "iteration_7_precondition": {
            "artifact": "n10_iteration_7_route_memory_regulation_composition",
            "artifact_digest": source_artifacts[
                "n10_iteration_7_route_memory_regulation_composition"
            ]["sha256"],
            "n10_category_level": iteration_7["integration_row"][
                "n10_category_level"
            ],
            "integration_row_digest": iteration_7["integration_row"][
                "integration_row_digest"
            ],
        },
        "fixture_lane": {
            "lane_id": fixture_lane["lane_id"],
            "expected_role": fixture_lane["expected_role"],
            "required_support_state_tag": fixture_lane[
                "required_support_state_tag"
            ],
            "required_route_context_tag": fixture_lane[
                "required_route_context_tag"
            ],
            "route_context_constraint": fixture_lane["route_context_constraint"],
            "source_support_lane_id": fixture_lane["source_support_lane_id"],
        },
        "integration_allowed": True,
        "positive_integration_row_emitted": True,
        "primary_blocker": None,
        "budget_mode": (
            "bounded_replay_uses_n09_same_run_node_plus_packet_budget; "
            "route, memory, support, and proxy surfaces remain separately "
            "audited source-artifact evidence"
        ),
        "category_boundary": (
            "ALI5 records bounded repeated integration across source-current "
            "route, memory, support, and goal-proxy regulation links. It does "
            "not close ALI6/A6 because final artifact-only closeout validation "
            "remains assigned to Iteration 9."
        ),
        "a6_relevance": "bounded_repeated_integration_component_not_a6_closeout",
        "a7_generalization_claim_allowed": False,
        "companion_lane": companion,
        "companion_scope": "mild_withdrawal_same_artifact_window_only"
        if companion
        else None,
    }
    return with_digest(row, "integration_row_digest")


def build_controls(
    *,
    manifest: dict[str, Any],
    main_row: dict[str, Any],
    companion_row: dict[str, Any],
    source_artifacts: dict[str, Any],
    n08: dict[str, Any],
    n09_gpr5: dict[str, Any],
) -> dict[str, Any]:
    blockers = manifest["control_blockers"]
    main_cycles = main_row["bounded_cycle_rows"]
    companion_cycles = companion_row["bounded_cycle_rows"]
    all_cycles = main_cycles + companion_cycles
    return {
        "bounded_window_length": {
            "control_passed": main_row["bounded_window"]["window_count"]
            == WINDOW_COUNT
            and companion_row["bounded_window"]["window_count"] == WINDOW_COUNT,
            "primary_blocker": "bounded_window_incomplete",
            "reason": "Iteration 8 requires four source-backed repeated cycles in the main and companion lanes",
        },
        "source_artifact_digest_mismatch": {
            "control_passed": all(
                value.get("matches_baseline", True) for value in source_artifacts.values()
            ),
            "primary_blocker": blockers["source_artifact_digest_mismatch"],
            "reason": "N06/N07/N08/N09 source artifact digests are rechecked against Iteration 1",
        },
        "stale_route_context": {
            "control_passed": all(
                row["route_source_current"]
                and row["route_context_tag"] == "route_context_selection_only"
                for row in all_cycles
            ),
            "primary_blocker": blockers["stale_route_context"],
            "reason": "each cycle consumes N06 under selection-only pre-topology scope",
        },
        "stale_memory_surface": {
            "control_passed": all(row["memory_source_current"] for row in all_cycles)
            and n08["source_control_replay"]["stale_memory_surface_read"][
                "replay_passed"
            ],
            "primary_blocker": blockers["stale_memory_surface"],
            "reason": "each cycle consumes N08 serialized memory/trail evidence and the stale-memory control remains passed",
        },
        "stale_identity_support_baseline": {
            "control_passed": all(row["support_source_current"] for row in all_cycles),
            "primary_blocker": blockers["stale_identity_support_baseline"],
            "reason": "main and companion support lanes match current N07/manifest digests",
        },
        "stale_regulation_window": {
            "control_passed": all(
                row["regulation_source_current"] for row in all_cycles
            )
            and n09_gpr5["validation_checks"][
                "memory_error_rows_reference_current_proxy_rows"
            ],
            "primary_blocker": "stale_proxy_read_blocked",
            "reason": "each regulation cycle reads its current proxy/error digest",
        },
        "budget_surface_ambiguity": {
            "control_passed": main_row["bounded_window"]["all_cycle_budgets_exact"]
            and companion_row["bounded_window"]["all_cycle_budgets_exact"]
            and n09_gpr5["validation_checks"]["memory_cycles_all_return_to_band"],
            "primary_blocker": blockers["budget_surface_ambiguity"],
            "reason": "node-plus-packet, memory, support, and proxy budget surfaces are audited separately and remain exact",
        },
        "hidden_experiment_side_steering": {
            "control_passed": all(
                row["route_source_current"]
                and row["regulation_top_ranked_is_unique"]
                for row in all_cycles
            )
            and n08["source_control_replay"]["repeated_hidden_route_preference"][
                "replay_passed"
            ],
            "primary_blocker": blockers["hidden_experiment_side_steering"],
            "reason": "route and memory-shaped regulation selections are serialized source evidence, not N10 if/else steering",
        },
        "duplicate_row_suppression": {
            "control_passed": main_row["bounded_window"][
                "duplicate_cycle_rows_suppressed"
            ]
            and companion_row["bounded_window"]["duplicate_cycle_rows_suppressed"]
            and main_row["integration_row_digest"]
            != companion_row["integration_row_digest"],
            "primary_blocker": "duplicate_integration_row",
            "reason": "cycle row digests are unique and main/companion rows have distinct digests",
        },
        "mild_withdrawal_companion_survives": {
            "control_passed": companion_row["support_evidence"][
                "support_survival_passed"
            ]
            and companion_row["support_state_tag"] == "mild_withdrawal_survives",
            "primary_blocker": "mild_withdrawal_companion_failed",
            "reason": "the companion lane remains above the support-survival threshold",
        },
        "artifact_only_replay_missing_link": {
            "control_passed": all(
                main_row[field] is not None
                for field in [
                    "route_choice_digest",
                    "memory_affordance_digest",
                    "identity_support_digest",
                    "goal_proxy_regulation_digest",
                ]
            )
            and main_row["artifact_only"]
            and not main_row["runtime_state_used"],
            "primary_blocker": blockers["artifact_only_replay_missing_link"],
            "reason": "bounded integration rows preserve all source links without private runtime fallback",
        },
        "claim_promotion": {
            "control_passed": all(
                value is False for value in main_row["claim_flags"].values()
            )
            and all(value is False for value in companion_row["claim_flags"].values())
            and all(row["claim_flags_false"] for row in all_cycles),
            "primary_blocker": blockers["claim_promotion"],
            "reason": "ALI5 bounded repetition does not emit ACO, agency, A6, identity acceptance, or goal-ownership claims",
        },
    }


def validate_output(
    *,
    manifest: dict[str, Any],
    main_row: dict[str, Any],
    companion_row: dict[str, Any],
    source_artifacts: dict[str, Any],
    controls: dict[str, Any],
) -> dict[str, bool]:
    required = set(manifest["integration_row_required_fields"])
    return {
        "main_row_required_fields_present": required.issubset(main_row),
        "companion_row_required_fields_present": required.issubset(companion_row),
        "main_row_digest_valid": main_row["integration_row_digest"]
        == digest_value(
            {
                key: value
                for key, value in main_row.items()
                if key != "integration_row_digest"
            }
        ),
        "companion_row_digest_valid": companion_row["integration_row_digest"]
        == digest_value(
            {
                key: value
                for key, value in companion_row.items()
                if key != "integration_row_digest"
            }
        ),
        "main_is_ali5": main_row["n10_category_level"] == "ALI5",
        "main_integration_level_is_a5": main_row["integration_level"] == "A5",
        "companion_is_ali5": companion_row["n10_category_level"] == "ALI5",
        "companion_integration_level_is_a5": companion_row["integration_level"]
        == "A5",
        "attempted_a6_not_accepted": main_row["attempted_integration_level"]
        == "A6"
        and main_row["accepted_integration_level"] == "A5"
        and companion_row["accepted_integration_level"] == "A5",
        "bounded_window_count_is_four": main_row["bounded_window"]["window_count"]
        == WINDOW_COUNT
        and companion_row["bounded_window"]["window_count"] == WINDOW_COUNT,
        "main_all_cycles_source_current": main_row["bounded_window"][
            "all_cycle_rows_source_current"
        ],
        "companion_all_cycles_source_current": companion_row["bounded_window"][
            "all_cycle_rows_source_current"
        ],
        "main_all_budgets_exact": main_row["bounded_window"][
            "all_cycle_budgets_exact"
        ],
        "companion_all_budgets_exact": companion_row["bounded_window"][
            "all_cycle_budgets_exact"
        ],
        "main_all_claim_flags_false": main_row["bounded_window"][
            "all_cycle_claim_flags_false"
        ],
        "companion_all_claim_flags_false": companion_row["bounded_window"][
            "all_cycle_claim_flags_false"
        ],
        "route_context_selection_only_preserved": all(
            row["route_context_tag"] == "route_context_selection_only"
            for row in main_row["bounded_cycle_rows"]
            + companion_row["bounded_cycle_rows"]
        ),
        "memory_scope_artifact_only_preserved": main_row["memory_scope_tag"]
        == "artifact_only_serialized_producer_policy_route_memory_or_trail"
        and companion_row["memory_scope_tag"]
        == "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "support_intact_main_lane": main_row["support_state_tag"]
        == "support_intact_survives",
        "mild_withdrawal_companion_lane": companion_row["support_state_tag"]
        == "mild_withdrawal_survives",
        "source_artifact_digests_match_baseline": all(
            value.get("matches_baseline", True) for value in source_artifacts.values()
        ),
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "a6_not_supported_by_iteration_8": main_row["accepted_integration_level"]
        != "A6"
        and main_row["n10_category_level"] != "ALI6",
        "src_clean_for_iteration_8": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    n06 = load_json(source_path(baseline, "n06_closeout"))
    n07 = load_json(source_path(baseline, "n07_withdrawal_baseline"))
    n08 = load_json(source_path(baseline, "n08_hypothesis_a_closeout"))
    n09_gpr5 = load_json(N09_GPR5_PATH)
    iteration_7 = load_json(ITERATION_7_PATH)
    source_artifacts, source_reports = build_source_records(baseline)

    support_intact = find_lane(n07["withdrawal_lanes"], "support_intact_reference")
    support_mild = find_lane(n07["withdrawal_lanes"], "mild_support_weakening")
    manifest_support_intact = find_lane(
        manifest["source_support_lanes"], "support_intact_reference"
    )
    manifest_support_mild = find_lane(
        manifest["source_support_lanes"], "mild_support_weakening"
    )
    main_fixture = find_lane(manifest["fixture_lanes"], "bounded_repeated_integration")
    companion_fixture = find_lane(
        manifest["fixture_lanes"],
        "bounded_repeated_integration_mild_withdrawal_companion",
    )
    main_support = support_summary(manifest, support_intact, manifest_support_intact)
    companion_support = support_summary(manifest, support_mild, manifest_support_mild)
    main_cycles = bounded_cycle_rows(
        n06=n06,
        n08=n08,
        n09_gpr5=n09_gpr5,
        support=main_support,
        route_context_tag=main_fixture["required_route_context_tag"],
    )
    companion_cycles = bounded_cycle_rows(
        n06=n06,
        n08=n08,
        n09_gpr5=n09_gpr5,
        support=companion_support,
        route_context_tag=companion_fixture["required_route_context_tag"],
    )
    main_row = build_integration_row(
        baseline=baseline,
        manifest=manifest,
        fixture_lane=main_fixture,
        support=main_support,
        source_artifacts=source_artifacts,
        source_reports=source_reports,
        iteration_7=iteration_7,
        cycle_rows=main_cycles,
        row_id="n10_i8_bounded_repeated_integration_row_v1",
        companion=False,
    )
    companion_row = build_integration_row(
        baseline=baseline,
        manifest=manifest,
        fixture_lane=companion_fixture,
        support=companion_support,
        source_artifacts=source_artifacts,
        source_reports=source_reports,
        iteration_7=iteration_7,
        cycle_rows=companion_cycles,
        row_id="n10_i8_bounded_repeated_integration_mild_withdrawal_companion_row_v1",
        companion=True,
    )
    controls = build_controls(
        manifest=manifest,
        main_row=main_row,
        companion_row=companion_row,
        source_artifacts=source_artifacts,
        n08=n08,
        n09_gpr5=n09_gpr5,
    )
    checks = validate_output(
        manifest=manifest,
        main_row=main_row,
        companion_row=companion_row,
        source_artifacts=source_artifacts,
        controls=controls,
    )
    artifact_only_replay = {
        "artifact_only": True,
        "runtime_state_used": False,
        "replay_chain": [
            {
                "step": "load_n10_iteration_7_ali4_composition",
                "artifact": source_artifacts[
                    "n10_iteration_7_route_memory_regulation_composition"
                ]["path"],
                "digest": source_artifacts[
                    "n10_iteration_7_route_memory_regulation_composition"
                ]["sha256"],
            },
            {
                "step": "load_n06_four_cycle_route_choice_replay",
                "artifact": source_artifacts["n06_closeout"]["path"],
                "digest": source_artifacts["n06_closeout"]["sha256"],
                "cycle_count": WINDOW_COUNT,
            },
            {
                "step": "load_n08_four_cycle_memory_trail_replay",
                "artifact": source_artifacts["n08_hypothesis_a_closeout"]["path"],
                "digest": source_artifacts["n08_hypothesis_a_closeout"]["sha256"],
                "cycle_count": WINDOW_COUNT,
            },
            {
                "step": "load_n09_gpr5_repeated_regulation_window",
                "artifact": source_artifacts[
                    "n09_gpr5_repeated_bounded_regulation"
                ]["path"],
                "digest": source_artifacts[
                    "n09_gpr5_repeated_bounded_regulation"
                ]["sha256"],
                "cycle_count": WINDOW_COUNT,
            },
            {
                "step": "load_n07_support_intact_and_mild_withdrawal_lanes",
                "artifact": source_artifacts["n07_withdrawal_baseline"]["path"],
                "support_lane_digests": [
                    main_support["lane_digest"],
                    companion_support["lane_digest"],
                ],
            },
            {
                "step": "emit_ali5_main_and_companion_rows",
                "main_row_digest": main_row["integration_row_digest"],
                "companion_row_digest": companion_row["integration_row_digest"],
                "n10_category_level": "ALI5",
            },
        ],
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 8 passes if the bounded integration chain remains "
            "source-current, budget-safe, replayable, and claim-clean across "
            "repeated cycles, while the mild-withdrawal companion remains "
            "support-aware and A6/ALI6 closeout stays deferred to Iteration 9."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_8_bounded_repeated_integration_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 8,
        "purpose": "bounded_repeated_integration_ali5_no_a6_closeout",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "manifest_digest": manifest["manifest_digest"],
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "main_integration_row": main_row,
        "mild_withdrawal_companion_row": companion_row,
        "artifact_only_replay": artifact_only_replay,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "9_artifact_only_replay_and_closeout",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    main = output["main_integration_row"]
    companion = output["mild_withdrawal_companion_row"]
    lines = [
        "# N10 Iteration 8 Bounded Repeated Integration",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 8 replayed a bounded four-cycle integration window. The main",
        "support-intact row and the mild-withdrawal companion both remain",
        "source-current, budget-safe, artifact-only, and claim-clean.",
        "",
        "This is `ALI5`, not final `ALI6`. Iteration 9 still has to run the",
        "artifact-only closeout validator before N10 can decide its final A6",
        "ceiling.",
        "",
        "```text",
        f"main.integration_level = {main['integration_level']}",
        f"main.n10_category_level = {main['n10_category_level']}",
        f"main.accepted_integration_level = {main['accepted_integration_level']}",
        f"companion.support_state_tag = {companion['support_state_tag']}",
        f"window_count = {main['bounded_window']['window_count']}",
        f"node_plus_packet_budget_error = {main['node_plus_packet_budget_error']}",
        "artifact_only = true",
        "runtime_state_used = false",
        "```",
        "",
        "## Main Row Summary",
        "",
        "```json",
        json.dumps(
            {
                key: main[key]
                for key in [
                    "integration_row_id",
                    "integration_level",
                    "attempted_integration_level",
                    "accepted_integration_level",
                    "n10_category_level",
                    "integration_outcome_tag",
                    "support_state_tag",
                    "route_context_tag",
                    "memory_scope_tag",
                    "regulation_scope_tag",
                    "a6_relevance",
                    "budget_mode",
                    "bounded_window",
                ]
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Mild-Withdrawal Companion",
        "",
        "```json",
        json.dumps(
            {
                key: companion[key]
                for key in [
                    "integration_row_id",
                    "integration_level",
                    "accepted_integration_level",
                    "n10_category_level",
                    "support_state_tag",
                    "companion_scope",
                    "support_evidence",
                    "bounded_window",
                ]
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Cycle Rows",
        "",
        "```json",
        json.dumps(main["bounded_cycle_rows"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(output["controls"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance",
        "",
        output["acceptance"]["acceptance_statement"],
        "",
        f"Acceptance state: `{output['acceptance']['status']}`.",
        "",
        "## Run Record",
        "",
        "```text",
        output["command"],
        "```",
        "",
        "Output digest:",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    if output["status"] != "passed":
        raise SystemExit(f"Iteration 8 bounded integration failed: {output['checks']}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()
