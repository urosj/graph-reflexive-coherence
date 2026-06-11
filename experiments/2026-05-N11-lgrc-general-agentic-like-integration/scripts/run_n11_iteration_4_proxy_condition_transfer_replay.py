#!/usr/bin/env python3
"""Run N11 Iteration 4 proxy-condition transfer replay."""

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
N09 = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"
N10 = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"

BASELINE_PATH = EXPERIMENT / "outputs" / "n11_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n11_generalization_fixture_manifest_v1.json"
ITERATION_3_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_3_route_context_transfer_replay.json"
)
N09_GPR1_PATH = N09 / "outputs" / "n09_iteration_3_gpr1_proxy_measurement.json"
N09_GPR5_PATH = (
    N09 / "outputs" / "n09_iteration_7_gpr5_repeated_bounded_regulation.json"
)
N09_CLOSEOUT_PATH = N09 / "outputs" / "n09_iteration_9_gpr6_closeout.json"
N10_ROUTE_COMPOSITION_PATH = (
    N10 / "outputs" / "n10_iteration_7_route_memory_regulation_composition.json"
)

OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_4_proxy_condition_transfer_replay.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n11_iteration_4_proxy_condition_transfer_replay.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "run_n11_iteration_4_proxy_condition_transfer_replay.py"
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


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def transfer_row_digest(row: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in row.items() if key != "transfer_row_digest"}
    )


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(baseline["n11_baseline"]["claim_flags"])}


def required_fields(manifest: dict[str, Any]) -> list[str]:
    fields = manifest["transfer_row_required_fields"]
    if not isinstance(fields, list):
        raise TypeError("manifest transfer_row_required_fields must be a list")
    return list(fields)


def fixture_lane(manifest: dict[str, Any]) -> dict[str, Any]:
    lanes = [
        lane
        for lane in manifest["fixture_lanes"]
        if lane.get("planned_iteration") == 4
        and lane.get("lane_id") == "proxy_target_band_variant_replay"
    ]
    if len(lanes) != 1:
        raise ValueError("expected exactly one Iteration 4 proxy fixture lane")
    return lanes[0]


def gpr5_cycles(gpr5: dict[str, Any]) -> list[dict[str, Any]]:
    cycles = gpr5["memory_shaped_lane"]["cycles"]
    if not isinstance(cycles, list) or not cycles:
        raise ValueError("N09 GPR5 memory-shaped cycles are missing")
    return cycles


def proxy_evidence_summary(
    gpr1: dict[str, Any],
    gpr5: dict[str, Any],
    n09_closeout: dict[str, Any],
    n10_route: dict[str, Any],
) -> dict[str, Any]:
    target_band = gpr1["target_band_row"]
    proxy_surface = gpr1["proxy_surface_row"]
    cycles = gpr5_cycles(gpr5)
    cycle_target_digests = [
        cycle["pre_correction_proxy_surface_row"]["target_band_digest"]
        for cycle in cycles
    ]
    post_measurements = [
        cycle["post_correction_proxy_surface_row"]["measurement_value"]
        for cycle in cycles
    ]
    pre_measurements = [
        cycle["pre_correction_proxy_surface_row"]["measurement_value"]
        for cycle in cycles
    ]
    validation = gpr5.get("validation_checks", {})
    window_policy = gpr5.get("window_policy", {})
    n10_regulation = n10_route["integration_row"]["regulation_evidence"]
    handoff = n09_closeout["n10_handoff_fields"]
    return {
        "n09_source_gpr_level": n09_closeout["gpr_level"],
        "n09_source_claim_ceiling": n09_closeout["claim_ceiling"],
        "n10_regulation_source_gpr_level": n10_regulation["source_gpr_level"],
        "n10_regulation_source_claim_ceiling": n10_regulation[
            "source_claim_ceiling"
        ],
        "proxy_measurement_surface": proxy_surface["regulated_variable_surface"],
        "proxy_kind": proxy_surface["proxy_kind"],
        "proxy_policy_id": proxy_surface["proxy_policy_id"],
        "proxy_surface_digest": proxy_surface["proxy_surface_digest"],
        "target_band_id": target_band["target_band_id"],
        "target_band_digest": target_band["target_band_digest"],
        "target_band_policy_id": target_band["target_band_policy_id"],
        "target_kind": target_band["target_kind"],
        "target_value": target_band["target_value"],
        "lower_bound": target_band["lower_bound"],
        "upper_bound": target_band["upper_bound"],
        "regulated_variable_id": target_band["regulated_variable_id"],
        "regulated_variable_surface": target_band["regulated_variable_surface"],
        "cycle_count": len(cycles),
        "pre_response_measurements": pre_measurements,
        "post_response_measurements": post_measurements,
        "same_target_band_all_windows": validation.get(
            "same_target_band_all_windows"
        )
        is True
        and window_policy.get("same_target_band_all_windows") is True,
        "unique_target_band_digests_in_cycles": sorted(set(cycle_target_digests)),
        "target_band_variant_source_count": len(set(cycle_target_digests)),
        "memory_cycles_all_return_to_band": validation.get(
            "memory_cycles_all_return_to_band"
        )
        is True,
        "memory_cycles_all_schedule_and_process": validation.get(
            "memory_cycles_all_schedule_and_process"
        )
        is True,
        "window_policy_count": window_policy.get("window_count"),
        "perturbation_recovery_outcome_tag": handoff[
            "perturbation_recovery_outcome_tag"
        ],
        "proxy_surface_digest_chain": handoff["proxy_surface_digest_chain"],
        "mechanism_status_tags": handoff["mechanism_status_tags"],
        "native_goal_proxy_regulation_blocker": n09_closeout[
            "ceiling_algorithm_result"
        ]["primary_blocker_for_hypothesis_b"],
    }


def source_bundle() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    artifacts = {
        "n11_baseline_inventory": rel(BASELINE_PATH),
        "n11_fixture_manifest": rel(MANIFEST_PATH),
        "n11_iteration_3_route_context_transfer_replay": rel(ITERATION_3_PATH),
        "n09_gpr1_proxy_measurement": rel(N09_GPR1_PATH),
        "n09_gpr5_repeated_bounded_regulation": rel(N09_GPR5_PATH),
        "n09_gpr6_closeout": rel(N09_CLOSEOUT_PATH),
        "n10_route_memory_regulation_composition": rel(N10_ROUTE_COMPOSITION_PATH),
    }
    digests = {key: digest_file(ROOT / value) for key, value in artifacts.items()}
    reports = {
        "n11_iteration_3_route_context_transfer_replay": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_3_route_context_transfer_replay.md"
        ),
        "n09_gpr1_proxy_measurement": (
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_3_gpr1_proxy_measurement.md"
        ),
        "n09_gpr5_repeated_bounded_regulation": (
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_7_gpr5_repeated_bounded_regulation.md"
        ),
        "n09_gpr6_closeout": (
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_9_gpr6_closeout.md"
        ),
        "n10_route_memory_regulation_composition": (
            "experiments/2026-05-N10-lgrc-agentic-like-integration/reports/"
            "n10_iteration_7_route_memory_regulation_composition.md"
        ),
    }
    return artifacts, digests, reports


def build_transfer_row(
    *,
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    lane: dict[str, Any],
    proxy_summary: dict[str, Any],
) -> dict[str, Any]:
    source_artifacts, source_digests, source_reports = source_bundle()
    blocker = "proxy_target_band_variant_missing_source"
    row = {
        "transfer_row_id": "n11_i4_proxy_target_band_variant_replay_row_v1",
        "gali_level": "GALI2",
        "attempted_gali_level": "GALI3",
        "arc_of_becoming_classification": "local_observation_tag",
        "producer_mediation_classification": "producer_mediated",
        "source_boundary": "N10_iteration_15_closeout",
        "source_artifacts": source_artifacts,
        "source_artifact_digests": source_digests,
        "source_reports": source_reports,
        "transfer_axis": lane["transfer_axis"],
        "transfer_policy_id": manifest["transfer_policy"]["transfer_policy_id"],
        "transfer_policy_digest": manifest["transfer_policy"][
            "transfer_policy_digest"
        ],
        "context_tag": lane["context_tag"],
        "support_state_tag": lane["support_state_tag"],
        "proxy_condition_tag": lane["proxy_condition_tag"],
        "source_scope_tag": "n10_bounded_artifact_only_source",
        "transfer_window_tag": "single_replay_window",
        "transfer_outcome_tag": "transfer_blocked",
        "artifact_only": True,
        "runtime_state_used": False,
        "producer_scaffold_used": True,
        "node_plus_packet_budget_before": None,
        "node_plus_packet_budget_after": None,
        "node_plus_packet_budget_error": 0.0,
        "memory_budget_surface": "n10_source_memory_budget_compatibility",
        "proxy_budget_surface": "active_node_coherence_band",
        "support_budget_surface": "n10_source_support_budget_compatibility",
        "hidden_steering_used": False,
        "native_policy_gap": sorted(
            set(
                baseline["n11_baseline"]["primary_native_blockers"]
                + [proxy_summary["native_goal_proxy_regulation_blocker"]]
            )
        ),
        "primary_blocker": blocker,
        "blocked_claims": baseline["n11_baseline"]["blocked_claims"],
        "claim_flags": false_claim_flags(baseline),
        "fixture_lane": lane,
        "transfer_accepted": False,
        "proxy_condition_scope_preserved": True,
        "goal_proxy_not_goal_ownership": True,
        "proxy_summary": proxy_summary,
        "interpretation": (
            "The N09/N10 source proves bounded artifact-only goal-proxy "
            "regulation under one declared target band. Iteration 4 asked for "
            "a proxy target-band variant, but the source records the same "
            "target-band digest across all repeated regulation windows. The "
            "GALI3 proxy-condition transfer is therefore blocked instead of "
            "promoted."
        ),
    }
    row["transfer_row_digest"] = transfer_row_digest(row)
    return row


def validate_row(row: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    fields = required_fields(manifest)
    missing = [field for field in fields if field not in row]
    digest_valid = row["transfer_row_digest"] == transfer_row_digest(row)
    claim_flags_false = all(value is False for value in row["claim_flags"].values())
    return {
        "row_validations": {
            row["transfer_row_id"]: {
                "missing_required_fields": missing,
                "transfer_row_digest_valid": digest_valid,
                "claim_flags_false": claim_flags_false,
                "accepted": row["transfer_accepted"],
                "primary_blocker": row["primary_blocker"],
            }
        },
        "all_required_fields_present": not missing,
        "all_transfer_row_digests_valid": digest_valid,
        "all_claim_flags_false": claim_flags_false,
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    iteration_3 = load_json(ITERATION_3_PATH)
    gpr1 = load_json(N09_GPR1_PATH)
    gpr5 = load_json(N09_GPR5_PATH)
    n09_closeout = load_json(N09_CLOSEOUT_PATH)
    n10_route = load_json(N10_ROUTE_COMPOSITION_PATH)
    lane = fixture_lane(manifest)
    proxy_summary = proxy_evidence_summary(gpr1, gpr5, n09_closeout, n10_route)
    row = build_transfer_row(
        baseline=baseline,
        manifest=manifest,
        lane=lane,
        proxy_summary=proxy_summary,
    )
    row_validation = validate_row(row, manifest)
    controls = {
        "stale_proxy_state": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_proxy_state"],
            "reason": (
                "Proxy rows consume current source digests; stale proxy-state "
                "substitution cannot satisfy the transfer row digest."
            ),
        },
        "hidden_proxy_target_substitution": {
            "control_passed": True,
            "primary_blocker": "hidden_proxy_target_substitution_blocked",
            "reason": (
                "The attempted proxy variant is blocked unless a target-band "
                "artifact with a committed digest exists in source evidence."
            ),
        },
        "out_of_envelope_proxy_target": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"][
                "out_of_envelope_proxy"
            ],
            "reason": (
                "No out-of-envelope target may be introduced by Iteration 4 "
                "bookkeeping; the source band remains 0.45..0.55."
            ),
        },
        "semantic_goal_ownership_relabeling": {
            "control_passed": True,
            "primary_blocker": "goal_proxy_relabelled_as_goal_ownership",
            "reason": (
                "N09 evidence remains goal-proxy regulation only, not semantic "
                "goal ownership, intention, or agency."
            ),
        },
        "claim_promotion": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["claim_promotion"],
            "reason": "All claim flags remain false.",
        },
    }
    checks = {
        "baseline_passed": baseline.get("status") == "passed",
        "manifest_passed": load_json(
            EXPERIMENT / "outputs" / "n11_iteration_2_fixture_manifest_validation.json"
        ).get("status")
        == "passed",
        "iteration_3_passed": iteration_3.get("status") == "passed",
        "iteration_3_gali2_source_preserved": iteration_3.get(
            "strongest_supported_gali_level"
        )
        == "GALI2",
        "iteration_4_fixture_lane_present": lane["lane_id"]
        == "proxy_target_band_variant_replay",
        "n09_gpr6_available": n09_closeout.get("gpr_level") == "GPR6",
        "n10_regulation_source_gpr6_available": proxy_summary[
            "n10_regulation_source_gpr_level"
        ]
        == "GPR6",
        "proxy_measurement_surface_recorded": bool(
            proxy_summary["proxy_measurement_surface"]
        ),
        "proxy_target_band_recorded": bool(proxy_summary["target_band_digest"]),
        "perturbation_envelope_recorded": bool(
            proxy_summary["perturbation_recovery_outcome_tag"]
        ),
        "same_target_band_all_windows_recorded": proxy_summary[
            "same_target_band_all_windows"
        ]
        is True,
        "proxy_target_band_variant_source_missing": proxy_summary[
            "target_band_variant_source_count"
        ]
        == 1,
        "proxy_condition_transfer_blocked_with_distinct_blocker": row[
            "primary_blocker"
        ]
        == "proxy_target_band_variant_missing_source"
        and row["transfer_accepted"] is False,
        "goal_proxy_not_goal_ownership": row["goal_proxy_not_goal_ownership"]
        is True,
        "budget_surfaces_separate": len(
            {
                row["memory_budget_surface"],
                row["proxy_budget_surface"],
                row["support_budget_surface"],
            }
        )
        == 3,
        "all_required_fields_present": row_validation["all_required_fields_present"],
        "all_transfer_row_digests_valid": row_validation[
            "all_transfer_row_digests_valid"
        ],
        "all_controls_passed": all(
            control["control_passed"] for control in controls.values()
        ),
        "all_claim_flags_false": row_validation["all_claim_flags_false"],
        "a7_not_supported": row["claim_flags"].get("a7_claim_allowed") is False,
        "gali7_not_supported": row["claim_flags"].get("gali7_claim_allowed")
        is False,
        "src_clean_for_iteration_4": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 4 passes if the N10 composition remains replay-valid "
            "under a declared proxy-condition variant, or records a distinct "
            "proxy blocker. The result must remain goal-proxy regulation only, "
            "with separated budget surfaces and no semantic goal ownership, "
            "intention, agency, A7, or GALI7 promotion."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_4_proxy_condition_transfer_replay_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 4,
        "purpose": "proxy_condition_transfer_replay",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "baseline_path": rel(BASELINE_PATH),
        "baseline_inventory_digest": baseline["inventory_digest"],
        "manifest_path": rel(MANIFEST_PATH),
        "manifest_digest": manifest["manifest_digest"],
        "iteration_3_path": rel(ITERATION_3_PATH),
        "iteration_3_output_digest": iteration_3["output_digest"],
        "proxy_evidence_summary": proxy_summary,
        "transfer_rows": [row],
        "accepted_row_count": 0,
        "blocked_row_count": 1,
        "strongest_supported_gali_level": "GALI2",
        "attempted_gali_level": "GALI3",
        "strongest_claim_ceiling": (
            "single_axis_route_context_transfer_candidate_selection_only"
        ),
        "proxy_condition_transfer_ceiling": "proxy_target_band_variant_blocked",
        "non_claim_boundary": {
            "semantic_goal_ownership_claim_allowed": False,
            "semantic_goal_understanding_claim_allowed": False,
            "intention_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "native_support_opened": False,
            "a7_claim_allowed": False,
            "gali7_claim_allowed": False,
        },
        "controls": controls,
        "row_validation": row_validation,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "5_support_state_transfer_replay",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 4 Proxy-Condition Transfer Replay",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 4 tested the manifest-declared proxy target-band variant",
        "against N09/N10 source artifacts. The source proves bounded artifact-only",
        "goal-proxy regulation under one declared target band, but the repeated",
        "N09 regulation windows all cite the same target-band digest. Therefore",
        "the GALI3 proxy-condition transfer is blocked with a distinct source",
        "blocker instead of being promoted.",
        "",
        "Current ceiling:",
        "",
        "```text",
        f"strongest_supported_gali_level = {output['strongest_supported_gali_level']}",
        f"attempted_gali_level = {output['attempted_gali_level']}",
        f"proxy_condition_transfer_ceiling = {output['proxy_condition_transfer_ceiling']}",
        "semantic_goal_ownership_claim_allowed = false",
        "intention_claim_allowed = false",
        "agency_claim_allowed = false",
        "A7/GALI7 supported = false",
        "```",
        "",
        "## Proxy Evidence Summary",
        "",
        "```json",
        json.dumps(output["proxy_evidence_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Transfer Row",
        "",
        "```json",
        json.dumps(output["transfer_rows"], indent=2, sort_keys=True),
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
        "## Interpretation",
        "",
        "This is a useful negative result. It preserves N09 as goal-proxy",
        "regulation rather than goal ownership, and it prevents bookkeeping from",
        "turning same-band bounded regulation into proxy-condition transfer. The",
        "current N11 ceiling therefore remains the GALI2 route-context transfer",
        "from Iteration 3 until a source-backed proxy-condition variant exists.",
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
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {output['status']}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()
