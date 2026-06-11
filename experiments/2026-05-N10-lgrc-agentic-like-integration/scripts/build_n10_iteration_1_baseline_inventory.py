#!/usr/bin/env python3
"""Build N10 Iteration 1 baseline and source inventory artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n10_iteration_1_baseline_inventory.json"
REPORT_PATH = EXPERIMENT / "reports" / "n10_iteration_1_baseline_inventory.md"

N05 = ROOT / "experiments" / "2026-05-N05-lgrc-coherence-waves-oscillators"
N06 = ROOT / "experiments" / "2026-05-N06-lgrc-semantic-route-choice"
N07 = ROOT / "experiments" / "2026-05-N07-rc-identity-attractor-invariance"
N08 = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"
N09 = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"

SOURCE_FILES = {
    "n05_closeout": (
        N05 / "outputs" / "n05_iteration_8_o6_closeout.json",
        N05 / "reports" / "n05_iteration_8_o6_closeout.md",
    ),
    "n06_closeout": (
        N06 / "outputs" / "n06_iteration_8_sc6_closeout.json",
        N06 / "reports" / "n06_iteration_8_sc6_closeout.md",
    ),
    "n07_closeout": (
        N07 / "outputs" / "n07_iteration_12_long_horizon_compatibility_closeout.json",
        N07 / "reports" / "n07_iteration_12_long_horizon_compatibility_closeout.md",
    ),
    "n07_withdrawal_baseline": (
        N07 / "outputs" / "n07_iteration_13_identity_support_withdrawal_baseline.json",
        N07 / "reports" / "n07_iteration_13_identity_support_withdrawal_baseline.md",
    ),
    "n08_hypothesis_a_closeout": (
        N08 / "outputs" / "n08_iteration_8_mem6_closeout.json",
        N08 / "reports" / "n08_iteration_8_mem6_closeout.md",
    ),
    "n08_hypothesis_b_closeout": (
        N08 / "outputs" / "n08_iteration_13_native_geometry_trail_closeout.json",
        N08 / "reports" / "n08_iteration_13_native_geometry_trail_closeout.md",
    ),
    "n09_hypothesis_a_closeout": (
        N09 / "outputs" / "n09_iteration_9_gpr6_closeout.json",
        N09 / "reports" / "n09_iteration_9_gpr6_closeout.md",
    ),
    "n09_hypothesis_b_closeout": (
        N09 / "outputs" / "n09_iteration_12_hypothesis_b2_native_substrate_closeout.json",
        N09 / "reports" / "n09_iteration_12_hypothesis_b2_native_substrate_closeout.md",
    ),
}


CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "intention_claim_allowed": False,
    "goal_ownership_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_identity_claim_allowed": False,
    "unrestricted_movement_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "agentic_like_claim_allowed": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def artifact_digest(inventory: dict[str, Any]) -> str:
    excluded = {"generated_at", "inventory_digest", "git"}
    return canonical_digest(
        {key: value for key, value in inventory.items() if key not in excluded}
    )


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


def nested(data: dict[str, Any], *path: str, default: Any = None) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def false_claim_flags(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def summarize_lanes(lanes: list[Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for lane in lanes:
        if not isinstance(lane, dict):
            continue
        result.append(
            {
                "lane_id": lane.get("lane_id"),
                "identity_support_outcome_tag": lane.get("identity_support_outcome_tag"),
                "support_survival_passed": lane.get("support_survival_passed"),
                "withdrawal_depth": lane.get("withdrawal_depth"),
                "restoration_fraction": lane.get("restoration_fraction"),
                "final_A_support_retention": lane.get("final_A_support_retention"),
                "final_basin_separability": lane.get("final_basin_separability"),
                "final_budget_error": lane.get("final_budget_error"),
                "lane_digest": lane.get("lane_digest"),
                "n10_consumption_role": lane.get("n10_consumption_role"),
            }
        )
    return result


def build_inventory() -> dict[str, Any]:
    loaded = {name: load_json(paths[0]) for name, paths in SOURCE_FILES.items()}

    n05 = loaded["n05_closeout"]
    n06 = loaded["n06_closeout"]
    n07 = loaded["n07_closeout"]
    n07_i13 = loaded["n07_withdrawal_baseline"]
    n08_a = loaded["n08_hypothesis_a_closeout"]
    n08_b = loaded["n08_hypothesis_b_closeout"]
    n09_a = loaded["n09_hypothesis_a_closeout"]
    n09_b = loaded["n09_hypothesis_b_closeout"]

    n07_closeout = n07.get("long_horizon_closeout_row", {})
    n08_a_closeout = n08_a.get("mem6_closeout") or n08_a.get("closeout", {})
    n08_b_summary = n08_b.get("closeout_summary", {})
    n09_a_ceiling = n09_a.get("ceiling_algorithm_result", {})
    n09_b_hypothesis_a = n09_b.get("hypothesis_a_closeout", {})
    n09_b_hypothesis_b = n09_b.get("hypothesis_b_closeout", {})

    source_artifacts = {
        name: {
            "path": rel(paths[0]),
            "sha256": sha256_file(paths[0]),
        }
        for name, paths in SOURCE_FILES.items()
    }
    source_reports = {
        name: {
            "path": rel(paths[1]),
            "sha256": sha256_file(paths[1]),
        }
        for name, paths in SOURCE_FILES.items()
    }

    source_inventory = {
        "n05": {
            "artifact_key": "n05_closeout",
            "status": n05.get("status"),
            "strongest_supported_o_level": nested(
                n05, "n05_closeout", "strongest_supported_o_level"
            ),
            "claim_ceiling": nested(n05, "n05_closeout", "strongest_claim_ceiling"),
            "o6_supported": nested(n05, "n05_closeout", "o6_supported"),
            "primary_blocker": nested(n05, "n05_closeout", "o6_primary_blocker"),
            "n10_role": "oscillator_and_route_aspect_background_only",
            "claim_flags": n05.get("claim_flags", {}),
        },
        "n06": {
            "artifact_key": "n06_closeout",
            "status": n06.get("status"),
            "strongest_supported_sc_level": nested(
                n06, "closeout", "strongest_supported_sc_level"
            ),
            "claim_ceiling": nested(n06, "closeout", "strongest_claim_ceiling"),
            "selection_scope": nested(
                n06, "closeout", "scheduled_processed_packet_evidence_applicability"
            ),
            "selection_causality_basis": nested(
                n06, "closeout", "selection_causality_basis"
            ),
            "n10_role": "route_choice_source_only_not_agency",
            "claim_flags": n06.get("claim_flags", {}),
        },
        "n07": {
            "artifact_key": "n07_closeout",
            "status": n07.get("status"),
            "id_level": n07_closeout.get("id_level"),
            "derived_id_ceiling": n07_closeout.get("derived_id_ceiling"),
            "claim_ceiling": n07_closeout.get("claim_ceiling"),
            "trajectory_regime": n07_closeout.get("trajectory_regime"),
            "support_area_id": n07_closeout.get("support_area_id"),
            "support_area_digest": n07_closeout.get("support_area_digest"),
            "support_dependency_status": n07_closeout.get("support_dependency_status"),
            "runtime_identity_acceptance": n07_closeout.get(
                "id6_is_runtime_identity_acceptance"
            )
            is True,
            "n10_role": "identity_support_baseline_source_not_identity_acceptance",
            "claim_flags": n07.get("claim_flags", {}),
        },
        "n07_iteration_13": {
            "artifact_key": "n07_withdrawal_baseline",
            "status": n07_i13.get("status"),
            "baseline_available": nested(
                n07_i13, "baseline_summary", "baseline_available"
            ),
            "n10_can_consume": nested(
                n07_i13,
                "baseline_summary",
                "n10_can_consume_identity_support_withdrawal_baseline",
            ),
            "n09_prior_blocker": nested(
                n07_i13, "baseline_summary", "n09_prior_blocker"
            ),
            "n09_prior_blocker_resolved_for_future_consumption": nested(
                n07_i13,
                "baseline_summary",
                "n09_prior_blocker_resolved_for_future_consumption",
            ),
            "support_lanes": summarize_lanes(n07_i13.get("withdrawal_lanes", [])),
            "n10_role": "load_bearing_support_survival_disruption_restoration_baseline",
            "claim_flags": n07_i13.get("claim_flags", {}),
        },
        "n08_hypothesis_a": {
            "artifact_key": "n08_hypothesis_a_closeout",
            "status": n08_a.get("status"),
            "mem_level": n08_a_closeout.get("mem_level"),
            "claim_ceiling": n08_a_closeout.get("strongest_claim_ceiling")
            or n08_a.get("claim_ceiling"),
            "claim_scope": n08_a_closeout.get("memory_or_trail_claim_scope"),
            "native_support_status": n08_a_closeout.get("native_support_status"),
            "n10_role": "memory_trail_affordance_source_scoped_to_artifact_only_serialized_policy",
            "claim_flags": n08_a_closeout.get("closeout_claim_flags", {}),
        },
        "n08_hypothesis_b": {
            "artifact_key": "n08_hypothesis_b_closeout",
            "status": n08_b.get("status"),
            "claim_ceiling": n08_b_summary.get("hypothesis_b_claim_ceiling"),
            "primary_blocker": n08_b_summary.get("hypothesis_b_current_blocker"),
            "native_policy_absorption_needed": n08_b_summary.get(
                "native_policy_absorption_needed"
            ),
            "n10_role": "native_geometry_trail_design_direction_and_policy_gap",
            "claim_flags": n08_b.get("claim_flags", {}),
        },
        "n09_hypothesis_a": {
            "artifact_key": "n09_hypothesis_a_closeout",
            "status": n09_a.get("status"),
            "gpr_level": n09_a_ceiling.get("strongest_passing_gpr_level"),
            "claim_ceiling": n09_a.get("claim_ceiling"),
            "hypothesis_a_status": n09_a_ceiling.get("hypothesis_a_status"),
            "primary_blocker_for_n10_prior_to_i13": n09_a_ceiling.get(
                "primary_blocker_for_n10_identity_support_consumption"
            ),
            "n10_role": "goal_proxy_regulation_source_before_i13_support_update",
            "claim_flags": n09_a.get("claim_flags", {}),
        },
        "n09_hypothesis_b": {
            "artifact_key": "n09_hypothesis_b_closeout",
            "status": n09_b.get("status"),
            "hypothesis_a_claim_ceiling": n09_b_hypothesis_a.get("claim_ceiling"),
            "hypothesis_b_claim_ceiling": n09_b_hypothesis_b.get("claim_ceiling"),
            "hypothesis_b_status": n09_b_hypothesis_b.get("status"),
            "primary_blocker": n09_b_hypothesis_b.get("primary_blocker"),
            "strongest_evidence": n09_b_hypothesis_b.get("strongest_evidence"),
            "general_native_goal_proxy_regulation_supported": n09_b_hypothesis_b.get(
                "general_native_goal_proxy_regulation_supported"
            ),
            "missing_native_policy_surface_count": len(
                n09_b.get("missing_native_policy_surfaces", [])
            ),
            "n10_role": "goal_proxy_regulation_closeout_and_native_policy_gap_record",
            "claim_flags": n09_b.get("claim_flags", {}),
        },
    }

    native_policy_gaps = sorted(
        {
            "native_route_conductance_memory_policy_missing",
            "native_response_magnitude_policy_missing_for_unbounded_perturbations",
            "native_identity_acceptance_validator_missing",
            "native_agentic_like_integration_policy_missing",
            nested(n08_b, "closeout_summary", "hypothesis_b_current_blocker"),
            nested(n09_b, "hypothesis_b_closeout", "primary_blocker"),
        }
        - {None}
    )

    claim_boundary = {
        "integration_level_is_evidence_classification": True,
        "a6_supported_at_start": False,
        "integration_rows_present_at_start": False,
        "claim_flags": CLAIM_FLAGS,
        "blocked_claims": [
            "agency",
            "intention",
            "semantic_goal_ownership",
            "identity_acceptance",
            "runtime_identity_acceptance",
            "rc_identity_collapse",
            "aco_like_behavior",
            "ant_colony_behavior",
            "locomotion_like_behavior",
            "biological_behavior",
            "personhood",
            "unrestricted_identity",
            "unrestricted_movement",
            "unrestricted_agency",
        ],
    }

    checks = {
        "n05_source_present": source_inventory["n05"]["status"] == "passed",
        "n06_source_present": source_inventory["n06"]["status"] == "passed",
        "n07_source_present": source_inventory["n07"]["status"] == "passed",
        "n07_i13_source_present": source_inventory["n07_iteration_13"]["status"]
        == "passed",
        "n08_hypothesis_a_source_present": source_inventory["n08_hypothesis_a"][
            "status"
        ]
        == "passed",
        "n08_hypothesis_b_source_present": source_inventory["n08_hypothesis_b"][
            "status"
        ]
        == "passed",
        "n09_hypothesis_a_source_present": source_inventory["n09_hypothesis_a"][
            "status"
        ]
        == "passed",
        "n09_hypothesis_b_source_present": source_inventory["n09_hypothesis_b"][
            "status"
        ]
        == "passed",
        "n07_i13_baseline_consumable": source_inventory["n07_iteration_13"][
            "n10_can_consume"
        ]
        is True,
        "n07_i13_has_four_support_lanes": len(
            source_inventory["n07_iteration_13"]["support_lanes"]
        )
        == 4,
        "n07_i13_has_disrupted_support_control": any(
            lane["support_survival_passed"] is False
            for lane in source_inventory["n07_iteration_13"]["support_lanes"]
        ),
        "n07_i13_has_explicit_restoration_lane": any(
            lane["restoration_fraction"] and lane["restoration_fraction"] > 0
            for lane in source_inventory["n07_iteration_13"]["support_lanes"]
        ),
        "n08_hypothesis_a_scope_artifact_only": source_inventory["n08_hypothesis_a"][
            "claim_scope"
        ]
        == "artifact_only_serialized_producer_policy_route_memory_or_trail",
        "n09_hypothesis_a_goal_proxy_available": source_inventory["n09_hypothesis_a"][
            "claim_ceiling"
        ]
        == "artifact_only_goal_proxy_regulation_candidate",
        "n09_hypothesis_b_native_general_regulation_blocked": source_inventory[
            "n09_hypothesis_b"
        ]["general_native_goal_proxy_regulation_supported"]
        is False,
        "native_policy_gaps_recorded": bool(native_policy_gaps),
        "claim_flags_all_false": false_claim_flags(CLAIM_FLAGS),
        "no_integration_probe_run": True,
        "no_integration_rows_at_start": True,
        "a6_not_supported_at_start": True,
        "src_clean_for_iteration_1": git_status_short("src") == "",
    }

    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 1 passes if N10 has a source-backed inventory of all "
            "prerequisite N05-N09 artifacts and records the exact evidence "
            "ceilings and blocked claims without promoting them into integration "
            "evidence."
        ),
    }

    inventory: dict[str, Any] = {
        "schema": "n10_iteration_1_baseline_inventory_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 1,
        "purpose": "baseline_source_inventory_no_integration_probe_no_claim_promotion",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": (
            ".venv/bin/python "
            "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
            "build_n10_iteration_1_baseline_inventory.py"
        ),
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "source_inventory": source_inventory,
        "hypothesis_orientation": {
            "iterations_1_to_9_primary_path": "hypothesis_a_bounded_artifact_only_integration",
            "hypothesis_b_role": "required_support_sensitivity_controls",
            "hypothesis_c_role": "tracked_native_policy_gap_not_solved_in_first_tranche",
        },
        "native_policy_gaps": native_policy_gaps,
        "claim_boundary": claim_boundary,
        "baseline_facts": {
            "integration_rows_present_at_start": False,
            "a6_supported_at_start": False,
            "n10_positive_probe_run": False,
        },
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "2_integration_schema_and_fixture_manifest",
    }
    inventory["inventory_digest"] = artifact_digest(inventory)
    return inventory


def render_report(inventory: dict[str, Any]) -> str:
    sources = inventory["source_inventory"]
    lanes = sources["n07_iteration_13"]["support_lanes"]
    lines = [
        "# N10 Iteration 1 Baseline And Source Inventory",
        "",
        f"Status: `{inventory['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 1 built a source-backed inventory from existing N05-N09",
        "artifacts only. No N10 integration probe was run.",
        "",
        "The starting boundary is:",
        "",
        "```text",
        "A6 evidence = not yet produced",
        "integration rows = none",
        "primary first-tranche path = Hypothesis A",
        "required controls = Hypothesis B support sensitivity",
        "native-policy gaps = Hypothesis C tracked, not solved",
        "bounded agentic-like integration claim allowed = false",
        "```",
        "",
        "## Inherited Sources",
        "",
        "N05:",
        "",
        f"- strongest O-level: `{sources['n05']['strongest_supported_o_level']}`",
        f"- claim ceiling: `{sources['n05']['claim_ceiling']}`",
        f"- O6 supported: `{sources['n05']['o6_supported']}`",
        f"- O6 blocker: `{sources['n05']['primary_blocker']}`",
        f"- N10 role: `{sources['n05']['n10_role']}`",
        "",
        "N06:",
        "",
        f"- strongest SC-level: `{sources['n06']['strongest_supported_sc_level']}`",
        f"- claim ceiling: `{sources['n06']['claim_ceiling']}`",
        f"- selection scope: `{sources['n06']['selection_scope']}`",
        f"- N10 role: `{sources['n06']['n10_role']}`",
        "",
        "N07:",
        "",
        f"- ID level: `{sources['n07']['id_level']}`",
        f"- derived ceiling: `{sources['n07']['derived_id_ceiling']}`",
        f"- trajectory regime: `{sources['n07']['trajectory_regime']}`",
        f"- support area digest: `{sources['n07']['support_area_digest']}`",
        f"- runtime identity acceptance: `{sources['n07']['runtime_identity_acceptance']}`",
        "",
        "N07 Iteration 13 withdrawal baseline:",
        "",
        f"- baseline available: `{sources['n07_iteration_13']['baseline_available']}`",
        f"- N10 can consume baseline: `{sources['n07_iteration_13']['n10_can_consume']}`",
        f"- prior N09 blocker: `{sources['n07_iteration_13']['n09_prior_blocker']}`",
        "- support lanes:",
    ]
    for lane in lanes:
        lines.append(
            "  - `{lane_id}`: tag=`{tag}`, survived=`{survived}`, "
            "withdrawal=`{withdrawal}`, restoration=`{restoration}`, "
            "support=`{support}`".format(
                lane_id=lane["lane_id"],
                tag=lane["identity_support_outcome_tag"],
                survived=lane["support_survival_passed"],
                withdrawal=lane["withdrawal_depth"],
                restoration=lane["restoration_fraction"],
                support=lane["final_A_support_retention"],
            )
        )
    lines.extend(
        [
            "",
            "N08:",
            "",
            "- Hypothesis A:",
            f"  - claim ceiling: `{sources['n08_hypothesis_a']['claim_ceiling']}`",
            f"  - claim scope: `{sources['n08_hypothesis_a']['claim_scope']}`",
            f"  - N10 role: `{sources['n08_hypothesis_a']['n10_role']}`",
            "- Hypothesis B:",
            f"  - claim ceiling: `{sources['n08_hypothesis_b']['claim_ceiling']}`",
            f"  - primary blocker: `{sources['n08_hypothesis_b']['primary_blocker']}`",
            f"  - N10 role: `{sources['n08_hypothesis_b']['n10_role']}`",
            "",
            "N09:",
            "",
            "- Hypothesis A:",
            f"  - GPR level: `{sources['n09_hypothesis_a']['gpr_level']}`",
            f"  - claim ceiling: `{sources['n09_hypothesis_a']['claim_ceiling']}`",
            f"  - prior N10 blocker before N07 I13: `{sources['n09_hypothesis_a']['primary_blocker_for_n10_prior_to_i13']}`",
            "- Hypothesis B:",
            f"  - claim ceiling: `{sources['n09_hypothesis_b']['hypothesis_b_claim_ceiling']}`",
            f"  - strongest evidence: `{sources['n09_hypothesis_b']['strongest_evidence']}`",
            f"  - primary blocker: `{sources['n09_hypothesis_b']['primary_blocker']}`",
            f"  - general native regulation supported: `{sources['n09_hypothesis_b']['general_native_goal_proxy_regulation_supported']}`",
            "",
            "## Hypothesis Orientation",
            "",
            "```json",
            json.dumps(inventory["hypothesis_orientation"], indent=2, sort_keys=True),
            "```",
            "",
            "## Native Policy Gaps",
            "",
            "```json",
            json.dumps(inventory["native_policy_gaps"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "All N10 claim flags are false at baseline:",
            "",
            "```json",
            json.dumps(
                inventory["claim_boundary"]["claim_flags"], indent=2, sort_keys=True
            ),
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(inventory["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Acceptance",
            "",
            inventory["acceptance"]["acceptance_statement"],
            "",
            f"Acceptance state: `{inventory['acceptance']['status']}`.",
            "",
            "## Run Record",
            "",
            "```text",
            inventory["command"],
            "```",
            "",
            "Inventory digest:",
            "",
            "```text",
            inventory["inventory_digest"],
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory()
    OUTPUT_PATH.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(inventory), encoding="utf-8")
    if inventory["status"] != "passed":
        raise SystemExit(f"Iteration 1 inventory failed: {inventory['checks']}")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"inventory_digest {inventory['inventory_digest']}")


if __name__ == "__main__":
    main()
