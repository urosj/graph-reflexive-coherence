#!/usr/bin/env python3
"""Build N11 Iteration 1 baseline and N10 source inventory artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)
N10 = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"

OUTPUT_PATH = EXPERIMENT / "outputs" / "n11_iteration_1_baseline_inventory.json"
REPORT_PATH = EXPERIMENT / "reports" / "n11_iteration_1_baseline_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "build_n11_iteration_1_baseline_inventory.py"
)

SOURCE_FILES = {
    "n10_final_closeout": (
        N10 / "outputs" / "n10_iteration_15_hypothesis_c_closeout_and_handoff.json",
        N10 / "reports" / "n10_iteration_15_hypothesis_c_closeout_and_handoff.md",
    ),
    "n10_hypothesis_a_closeout": (
        N10 / "outputs" / "n10_iteration_9_artifact_only_closeout.json",
        N10 / "reports" / "n10_iteration_9_artifact_only_closeout.md",
    ),
    "n10_hypothesis_b_closeout": (
        N10
        / "outputs"
        / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.json",
        N10
        / "reports"
        / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.md",
    ),
    "n10_hypothesis_c_inventory": (
        N10
        / "outputs"
        / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.json",
        N10
        / "reports"
        / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.md",
    ),
    "n10_hypothesis_c_contract": (
        N10
        / "outputs"
        / "n10_iteration_14_hypothesis_c_native_contract_requirements.json",
        N10
        / "reports"
        / "n10_iteration_14_hypothesis_c_native_contract_requirements.md",
    ),
}

EXPECTED_NATIVE_BLOCKERS = [
    "native_route_conductance_memory_policy_missing",
    "native_response_magnitude_policy_missing_for_unbounded_perturbations",
    "native_identity_acceptance_validator_missing",
    "native_agentic_like_integration_policy_missing",
]

CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
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
    "fully_native_agentic_like_integration_claim_allowed": False,
    "a7_claim_allowed": False,
    "gali7_claim_allowed": False,
}

BLOCKED_CLAIMS = [
    "agency",
    "intention",
    "semantic_goal_ownership",
    "semantic_goal_understanding",
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
    "fully_native_agentic_like_integration",
    "A7_generalization_by_inheritance",
    "GALI7_by_inheritance",
]


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


def nested(data: dict[str, Any], *path: str, default: Any = None) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def output_digest(data: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "validation_digest", "git"}
    return digest_value({key: value for key, value in data.items() if key not in excluded})


def inventory_digest(inventory: dict[str, Any]) -> str:
    excluded = {"generated_at", "inventory_digest", "git"}
    return digest_value(
        {key: value for key, value in inventory.items() if key not in excluded}
    )


def source_artifact_record(path: Path) -> dict[str, Any]:
    data = load_json(path)
    expected = data.get("output_digest") or data.get("validation_digest")
    current = output_digest(data) if expected else None
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": data.get("status"),
        "output_digest": expected,
        "output_digest_valid": True if expected is None else current == expected,
    }


def false_claim_flags(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def native_gap_blockers(gap_inventory: dict[str, Any]) -> list[str]:
    closeout_blockers = nested(
        gap_inventory,
        "hypothesis_c_inventory_closeout",
        "fully_native_agentic_like_integration_primary_blockers",
        default=[],
    )
    row_blockers = [
        row.get("native_policy_gap")
        for row in gap_inventory.get("native_policy_gap_inventory", [])
        if isinstance(row, dict) and row.get("native_policy_gap")
    ]
    return sorted(set(closeout_blockers) | set(row_blockers))


def build_inventory() -> dict[str, Any]:
    loaded = {name: load_json(paths[0]) for name, paths in SOURCE_FILES.items()}
    final = loaded["n10_final_closeout"]
    hyp_a = loaded["n10_hypothesis_a_closeout"]
    hyp_b = loaded["n10_hypothesis_b_closeout"]
    hyp_c_inventory = loaded["n10_hypothesis_c_inventory"]
    hyp_c_contract = loaded["n10_hypothesis_c_contract"]

    final_closeout = final["n10_final_closeout"]
    hyp_a_closeout = hyp_a["closeout"]
    hyp_b_closeout = hyp_b["hypothesis_b_closeout"]
    hyp_c_contract_closeout = hyp_c_contract["hypothesis_c_contract_closeout"]

    source_artifacts = {
        name: source_artifact_record(paths[0]) for name, paths in SOURCE_FILES.items()
    }
    source_reports = {
        name: {"path": rel(paths[1]), "sha256": digest_file(paths[1])}
        for name, paths in SOURCE_FILES.items()
    }

    support_matrix = hyp_b.get("support_state_matrix", [])
    source_inventory = {
        "n10_final_closeout": {
            "artifact_key": "n10_final_closeout",
            "status": final.get("status"),
            "final_n10_ceiling": final_closeout.get("final_n10_ceiling"),
            "integration_level": final_closeout.get("integration_level"),
            "n10_category_level": final_closeout.get("n10_category_level"),
            "n10_final_status": final_closeout.get("n10_final_status"),
            "bounded_artifact_only_agentic_like_integration_supported": (
                final_closeout.get(
                    "bounded_artifact_only_agentic_like_integration_supported"
                )
            ),
            "support_sensitive_integration_supported": final_closeout.get(
                "support_sensitive_integration_supported"
            ),
            "fully_native_agentic_like_integration_supported": final_closeout.get(
                "fully_native_agentic_like_integration_supported"
            ),
            "native_support_flags_opened": final_closeout.get(
                "native_support_flags_opened"
            ),
            "primary_native_blockers": final_closeout.get(
                "primary_native_blockers", []
            ),
            "n11_handoff_ready": nested(
                final, "n11_consumption_handoff", "ready_for_n11"
            ),
            "n11_must_preserve": nested(
                final, "n11_consumption_handoff", "n11_must_preserve", default=[]
            ),
            "n11_must_not_overread": nested(
                final, "n11_consumption_handoff", "n11_must_not_overread", default=[]
            ),
            "claim_flags": final_closeout.get("claim_flags", {}),
        },
        "n10_hypothesis_a_closeout": {
            "artifact_key": "n10_hypothesis_a_closeout",
            "status": hyp_a.get("status"),
            "final_n10_ceiling": hyp_a_closeout.get("final_n10_ceiling"),
            "integration_level": hyp_a_closeout.get("integration_level"),
            "n10_category_level": hyp_a_closeout.get("n10_category_level"),
            "bounded_window_count": hyp_a_closeout.get("bounded_window_count"),
            "artifact_only": hyp_a_closeout.get("artifact_only"),
            "runtime_state_used": nested(hyp_a, "artifact_only_replay", "runtime_state_used"),
            "memory_scope": hyp_a_closeout.get("memory_scope"),
            "support_matrix_deferred_to_hypothesis_b": True,
            "native_policy_gaps_preserved": hyp_a_closeout.get(
                "native_policy_gaps_preserved", []
            ),
            "claim_flags": hyp_a_closeout.get("claim_flags", {}),
        },
        "n10_hypothesis_b_closeout": {
            "artifact_key": "n10_hypothesis_b_closeout",
            "status": hyp_b.get("status"),
            "hypothesis_b_status": hyp_b_closeout.get("hypothesis_b_status"),
            "hypothesis_b_supported": hyp_b_closeout.get("hypothesis_b_supported"),
            "positive_scope": hyp_b_closeout.get("positive_scope"),
            "support_sensitive_rule": hyp_b_closeout.get("support_sensitive_rule"),
            "matrix_states": hyp_b_closeout.get("matrix_states", []),
            "disrupted_support_blocker": hyp_b_closeout.get(
                "disrupted_support_blocker"
            ),
            "restoration_preserves_disruption_history": hyp_b_closeout.get(
                "restoration_preserves_disruption_history"
            ),
            "artifact_only": hyp_b_closeout.get("artifact_only"),
            "runtime_state_used": hyp_b_closeout.get("runtime_state_used"),
            "support_state_matrix": [
                {
                    "matrix_state": row.get("matrix_state"),
                    "integration_allowed": row.get("integration_allowed"),
                    "accepted_integration_level": row.get("accepted_integration_level"),
                    "accepted_n10_category_level": row.get(
                        "accepted_n10_category_level"
                    ),
                    "expected_outcome": row.get("expected_outcome"),
                    "outcome_matches_expectation": row.get(
                        "outcome_matches_expectation"
                    ),
                    "matrix_row_digest": row.get("matrix_row_digest"),
                }
                for row in support_matrix
            ],
            "claim_flags": hyp_b_closeout.get("claim_flags", {}),
        },
        "n10_hypothesis_c_inventory": {
            "artifact_key": "n10_hypothesis_c_inventory",
            "status": hyp_c_inventory.get("status"),
            "purpose": hyp_c_inventory.get("purpose"),
            "primary_native_blockers": native_gap_blockers(hyp_c_inventory),
            "gap_row_count": nested(
                hyp_c_inventory,
                "hypothesis_c_inventory_closeout",
                "gap_row_count",
            ),
            "load_bearing_gap_row_count": nested(
                hyp_c_inventory,
                "hypothesis_c_inventory_closeout",
                "load_bearing_gap_row_count",
            ),
            "classification_counts": nested(
                hyp_c_inventory,
                "hypothesis_c_inventory_closeout",
                "classification_counts",
                default={},
            ),
            "claim_flags": hyp_c_inventory.get("claim_flags", {}),
        },
        "n10_hypothesis_c_contract": {
            "artifact_key": "n10_hypothesis_c_contract",
            "status": hyp_c_contract.get("status"),
            "contract_status": hyp_c_contract_closeout.get("contract_status"),
            "fully_native_agentic_like_integration_supported": (
                hyp_c_contract_closeout.get(
                    "fully_native_agentic_like_integration_supported"
                )
            ),
            "native_support_flags_opened": hyp_c_contract_closeout.get(
                "native_support_flags_opened"
            ),
            "primary_native_blockers": hyp_c_contract_closeout.get(
                "primary_native_blockers", []
            ),
            "required_policy_records": hyp_c_contract_closeout.get(
                "required_policy_records", []
            ),
            "phase_8_absorption_step_count": hyp_c_contract_closeout.get(
                "phase_8_absorption_step_count"
            ),
            "claim_flags": hyp_c_contract_closeout.get("claim_flags", {}),
        },
    }

    n11_baseline = {
        "n11_baseline_row_id": "n11_i1_baseline_inventory_v1",
        "source_boundary": "N10_iteration_15_closeout",
        "n10_final_ceiling": final_closeout.get("final_n10_ceiling"),
        "n10_integration_level": final_closeout.get("integration_level"),
        "n10_category_level": final_closeout.get("n10_category_level"),
        "n11_starting_gali_level": "GALI1",
        "n11_starting_gali_level_reason": (
            "Iteration 1 inventories source-backed transfer inputs only; no "
            "generalization replay row exists yet."
        ),
        "n11_generalization_rows_at_start": 0,
        "a7_supported_at_start": False,
        "gali7_supported_at_start": False,
        "support_sensitive_integration_supported": final_closeout.get(
            "support_sensitive_integration_supported"
        ),
        "fully_native_agentic_like_integration_supported": final_closeout.get(
            "fully_native_agentic_like_integration_supported"
        ),
        "native_support_flags_opened": final_closeout.get(
            "native_support_flags_opened"
        ),
        "primary_native_blockers": final_closeout.get("primary_native_blockers", []),
        "claim_flags": CLAIM_FLAGS,
        "blocked_claims": BLOCKED_CLAIMS,
    }
    n11_baseline["n11_baseline_digest"] = digest_value(n11_baseline)

    checks = {
        "all_required_artifacts_present": all(paths[0].exists() for paths in SOURCE_FILES.values()),
        "all_required_reports_present": all(paths[1].exists() for paths in SOURCE_FILES.values()),
        "all_required_artifacts_passed": all(
            record["status"] == "passed" for record in source_artifacts.values()
        ),
        "prior_output_digests_valid": all(
            record["output_digest_valid"] is True
            for record in source_artifacts.values()
        ),
        "n10_final_ceiling_preserved": final_closeout.get("final_n10_ceiling")
        == "bounded_artifact_only_agentic_like_integration_candidate",
        "n10_integration_level_preserved": final_closeout.get("integration_level")
        == "A6",
        "n10_category_level_preserved": final_closeout.get("n10_category_level")
        == "ALI6",
        "support_sensitive_boundary_preserved": final_closeout.get(
            "support_sensitive_integration_supported"
        )
        is True,
        "fully_native_boundary_preserved": final_closeout.get(
            "fully_native_agentic_like_integration_supported"
        )
        is False,
        "native_support_flags_not_opened": final_closeout.get(
            "native_support_flags_opened"
        )
        is False,
        "expected_native_blockers_preserved": sorted(
            final_closeout.get("primary_native_blockers", [])
        )
        == sorted(EXPECTED_NATIVE_BLOCKERS),
        "hypothesis_a_artifact_only": hyp_a_closeout.get("artifact_only") is True,
        "hypothesis_a_runtime_state_not_used": nested(
            hyp_a, "artifact_only_replay", "runtime_state_used"
        )
        is False,
        "hypothesis_b_supported": hyp_b_closeout.get("hypothesis_b_supported")
        is True,
        "hypothesis_b_disrupted_support_blocks": (
            hyp_b_closeout.get("disrupted_support_blocker")
            == "support_disrupted_but_integration_allowed"
        ),
        "hypothesis_c_contract_complete": hyp_c_contract_closeout.get(
            "contract_status"
        )
        == "native_contract_requirements_complete",
        "hypothesis_c_inventory_blockers_recorded": sorted(
            source_inventory["n10_hypothesis_c_inventory"]["primary_native_blockers"]
        )
        == sorted(EXPECTED_NATIVE_BLOCKERS + ["native_goal_proxy_regulation_policy_missing"]),
        "n11_handoff_ready": nested(
            final, "n11_consumption_handoff", "ready_for_n11"
        )
        is True,
        "no_n11_transfer_probe_run": True,
        "no_n11_generalization_rows_at_start": n11_baseline[
            "n11_generalization_rows_at_start"
        ]
        == 0,
        "a7_not_supported_at_start": n11_baseline["a7_supported_at_start"] is False,
        "gali7_not_supported_at_start": n11_baseline[
            "gali7_supported_at_start"
        ]
        is False,
        "claim_flags_all_false": false_claim_flags(CLAIM_FLAGS),
        "src_clean_for_iteration_1": git_status_short("src") == "",
    }

    controls = {
        "no_n11_transfer_probe": {
            "control_passed": checks["no_n11_transfer_probe_run"],
            "primary_blocker": "n11_transfer_probe_run_during_baseline_inventory",
        },
        "no_a7_or_gali7_by_inheritance": {
            "control_passed": (
                checks["a7_not_supported_at_start"]
                and checks["gali7_not_supported_at_start"]
            ),
            "primary_blocker": "n10_a6_overread_as_n11_a7",
        },
        "fully_native_remains_blocked": {
            "control_passed": checks["fully_native_boundary_preserved"],
            "primary_blocker": "fully_native_agentic_like_integration_overread",
        },
        "source_artifacts_digest_pinned": {
            "control_passed": checks["prior_output_digests_valid"],
            "primary_blocker": "n10_source_artifact_digest_mismatch",
        },
        "claim_flags_all_false": {
            "control_passed": checks["claim_flags_all_false"],
            "primary_blocker": "claim_promotion_blocked",
        },
    }

    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 1 passes if N11 has a source-backed inventory of N10 "
            "closeout artifacts and records exact N10 evidence ceilings, "
            "support-sensitive boundaries, and native blockers without "
            "promoting them into N11 generalization evidence."
        ),
    }

    inventory: dict[str, Any] = {
        "schema": "n11_iteration_1_baseline_inventory_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 1,
        "purpose": "baseline_n10_source_inventory_no_transfer_probe_no_claim_promotion",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "source_inventory": source_inventory,
        "n11_baseline": n11_baseline,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "2_generalization_schema_and_fixture_manifest",
    }
    inventory["inventory_digest"] = inventory_digest(inventory)
    return inventory


def render_report(inventory: dict[str, Any]) -> str:
    baseline = inventory["n11_baseline"]
    sources = inventory["source_inventory"]
    lines = [
        "# N11 Iteration 1 Baseline And N10 Source Inventory",
        "",
        f"Status: `{inventory['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 1 built a source-backed N10 inventory for N11. No N11",
        "transfer probe was run and no N10 evidence was promoted into A7/GALI7.",
        "",
        "Starting boundary:",
        "",
        "```text",
        f"N10 final ceiling = {baseline['n10_final_ceiling']}",
        f"N10 level = {baseline['n10_integration_level']} / {baseline['n10_category_level']}",
        f"N11 starting GALI level = {baseline['n11_starting_gali_level']}",
        "N11 generalization rows = 0",
        "A7 supported at start = false",
        "GALI7 supported at start = false",
        "fully native integration supported = false",
        "```",
        "",
        "## N10 Sources",
        "",
        "N10 final closeout:",
        "",
        f"- status: `{sources['n10_final_closeout']['status']}`",
        f"- final ceiling: `{sources['n10_final_closeout']['final_n10_ceiling']}`",
        f"- support-sensitive integration: `{sources['n10_final_closeout']['support_sensitive_integration_supported']}`",
        f"- fully native support: `{sources['n10_final_closeout']['fully_native_agentic_like_integration_supported']}`",
        f"- native support flags opened: `{sources['n10_final_closeout']['native_support_flags_opened']}`",
        "",
        "Hypothesis A:",
        "",
        f"- final ceiling: `{sources['n10_hypothesis_a_closeout']['final_n10_ceiling']}`",
        f"- level: `{sources['n10_hypothesis_a_closeout']['integration_level']} / {sources['n10_hypothesis_a_closeout']['n10_category_level']}`",
        f"- bounded window count: `{sources['n10_hypothesis_a_closeout']['bounded_window_count']}`",
        f"- artifact-only: `{sources['n10_hypothesis_a_closeout']['artifact_only']}`",
        "",
        "Hypothesis B:",
        "",
        f"- status: `{sources['n10_hypothesis_b_closeout']['hypothesis_b_status']}`",
        f"- supported: `{sources['n10_hypothesis_b_closeout']['hypothesis_b_supported']}`",
        f"- support rule: `{sources['n10_hypothesis_b_closeout']['support_sensitive_rule']}`",
        f"- disrupted-support blocker: `{sources['n10_hypothesis_b_closeout']['disrupted_support_blocker']}`",
        "",
        "Hypothesis C:",
        "",
        f"- contract status: `{sources['n10_hypothesis_c_contract']['contract_status']}`",
        f"- fully native support: `{sources['n10_hypothesis_c_contract']['fully_native_agentic_like_integration_supported']}`",
        f"- native support flags opened: `{sources['n10_hypothesis_c_contract']['native_support_flags_opened']}`",
        "",
        "Primary native blockers:",
        "",
        "```json",
        json.dumps(baseline["primary_native_blockers"], indent=2, sort_keys=True),
        "```",
        "",
        "## N11 Handoff Constraints",
        "",
        "N11 must preserve:",
        "",
        "```json",
        json.dumps(
            sources["n10_final_closeout"]["n11_must_preserve"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "N11 must not overread:",
        "",
        "```json",
        json.dumps(
            sources["n10_final_closeout"]["n11_must_not_overread"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Claim Boundary",
        "",
        "```json",
        json.dumps(baseline["claim_flags"], indent=2, sort_keys=True),
        "```",
        "",
        "## Source Artifacts",
        "",
        "```json",
        json.dumps(inventory["source_artifacts"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(inventory["controls"], indent=2, sort_keys=True),
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
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory()
    OUTPUT_PATH.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(inventory), encoding="utf-8")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {inventory['status']}")
    print(f"inventory_digest {inventory['inventory_digest']}")


if __name__ == "__main__":
    main()
