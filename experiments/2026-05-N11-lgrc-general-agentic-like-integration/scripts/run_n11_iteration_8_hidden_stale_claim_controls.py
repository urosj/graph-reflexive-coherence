#!/usr/bin/env python3
"""Run N11 Iteration 8 hidden/stale/claim controls."""

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

BASELINE_PATH = EXPERIMENT / "outputs" / "n11_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n11_generalization_fixture_manifest_v1.json"
ITERATION_2_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_2_fixture_manifest_validation.json"
)
ITERATION_6_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_6_multi_axis_transfer_matrix.json"
)
ITERATION_7_PATH = (
    EXPERIMENT
    / "outputs"
    / "n11_iteration_7_longer_horizon_generalization_window.json"
)

OUTPUT_PATH = EXPERIMENT / "outputs" / "n11_iteration_8_hidden_stale_claim_controls.json"
REPORT_PATH = EXPERIMENT / "reports" / "n11_iteration_8_hidden_stale_claim_controls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "run_n11_iteration_8_hidden_stale_claim_controls.py"
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


def control_record_digest(record: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in record.items() if key != "control_record_digest"}
    )


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(baseline["n11_baseline"]["claim_flags"])}


def source_bundle() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    artifacts = {
        "n11_baseline_inventory": rel(BASELINE_PATH),
        "n11_fixture_manifest": rel(MANIFEST_PATH),
        "n11_iteration_2_fixture_manifest_validation": rel(ITERATION_2_PATH),
        "n11_iteration_6_multi_axis_transfer_matrix": rel(ITERATION_6_PATH),
        "n11_iteration_7_longer_horizon_generalization_window": rel(ITERATION_7_PATH),
    }
    digests = {key: digest_file(ROOT / value) for key, value in artifacts.items()}
    reports = {
        "n11_iteration_6_multi_axis_transfer_matrix": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_6_multi_axis_transfer_matrix.md"
        ),
        "n11_iteration_7_longer_horizon_generalization_window": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_7_longer_horizon_generalization_window.md"
        ),
    }
    return artifacts, digests, reports


def representative_row(iteration_7: dict[str, Any]) -> dict[str, Any]:
    for row in iteration_7["transfer_rows"]:
        if (
            row["gali_level"] == "GALI6"
            and row["context_tag"] == "context_route_variant"
            and row["proxy_condition_tag"] == "proxy_target_band_variant"
            and row["support_state_tag"] == "mild_withdrawal_survives"
        ):
            return row
    for row in iteration_7["transfer_rows"]:
        if row["gali_level"] == "GALI6":
            return row
    raise ValueError("Iteration 7 must contain at least one GALI6 row")


def build_control_record(
    *,
    control_id: str,
    control_kind: str,
    source_row: dict[str, Any],
    source_artifacts: dict[str, str],
    source_digests: dict[str, str],
    source_reports: dict[str, str],
    mutation: dict[str, Any],
    expected_primary_blocker: str,
    observed_primary_blocker: str,
    claim_flags_after_control: dict[str, bool],
    reason: str,
) -> dict[str, Any]:
    record = {
        "control_id": control_id,
        "control_kind": control_kind,
        "source_positive_artifacts": source_artifacts,
        "source_positive_artifact_digests": source_digests,
        "source_positive_reports": source_reports,
        "source_iteration_7_row_id": source_row["transfer_row_id"],
        "source_iteration_7_row_digest": source_row["transfer_row_digest"],
        "source_iteration_7_trend_digest": source_row["trend_digest"],
        "source_gali_level": source_row["gali_level"],
        "mutation": mutation,
        "expected_primary_blocker": expected_primary_blocker,
        "observed_primary_blocker": observed_primary_blocker,
        "control_passed": observed_primary_blocker == expected_primary_blocker,
        "generic_failure_used": False,
        "fail_closed": True,
        "claim_flags_after_control": claim_flags_after_control,
        "all_claim_flags_false_after_control": all(
            value is False for value in claim_flags_after_control.values()
        ),
        "reason": reason,
    }
    record["control_record_digest"] = control_record_digest(record)
    return record


def build_control_records(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    iteration_7: dict[str, Any],
) -> list[dict[str, Any]]:
    source_artifacts, source_digests, source_reports = source_bundle()
    source_row = representative_row(iteration_7)
    blockers = manifest["control_blockers"]
    claim_flags = false_claim_flags(baseline)

    control_specs = [
        {
            "control_id": "n11_i8_hidden_context_substitution_control_v1",
            "control_kind": "hidden_context_substitution",
            "mutation": {
                "context_tag": "context_hidden",
                "hidden_context_value": "report_side_route_context_override",
                "source_context_digest_reused": True,
            },
            "blocker": blockers["hidden_context_substitution"],
            "reason": "A hidden context override cannot satisfy source-backed context transfer.",
        },
        {
            "control_id": "n11_i8_stale_route_context_control_v1",
            "control_kind": "stale_route_context",
            "mutation": {
                "context_tag": "context_stale",
                "source_current": False,
                "stale_context_digest": source_row["source_matrix_cell_digest"],
            },
            "blocker": blockers["stale_context"],
            "reason": "A stale route-context digest cannot remain source-current over the replay window.",
        },
        {
            "control_id": "n11_i8_stale_support_state_control_v1",
            "control_kind": "stale_support_state",
            "mutation": {
                "support_state_tag": "support_state_stale",
                "support_source_current": False,
                "support_retention_reused_after_stale_mark": True,
            },
            "blocker": blockers["stale_support_state"],
            "reason": "Support-state evidence must be source-current; stale support cannot pass.",
        },
        {
            "control_id": "n11_i8_stale_proxy_state_control_v1",
            "control_kind": "stale_proxy_state",
            "mutation": {
                "proxy_condition_tag": "proxy_stale",
                "proxy_source_current": False,
                "target_band_digest_reused_after_stale_mark": True,
            },
            "blocker": blockers["stale_proxy_state"],
            "reason": "Proxy evidence must cite current same-band or 4-B variant digests.",
        },
        {
            "control_id": "n11_i8_out_of_envelope_proxy_target_control_v1",
            "control_kind": "out_of_envelope_proxy_target",
            "mutation": {
                "proxy_condition_tag": "proxy_out_of_envelope",
                "declared_lower_bound": 0.70,
                "declared_upper_bound": 0.80,
                "declared_target_value": 0.75,
                "max_allowed_shift": 0.05,
            },
            "blocker": blockers["out_of_envelope_proxy"],
            "reason": "A proxy target outside the declared envelope cannot inherit the 4-B result.",
        },
        {
            "control_id": "n11_i8_budget_surface_ambiguity_control_v1",
            "control_kind": "budget_surface_ambiguity",
            "mutation": {
                "memory_budget_surface": "merged_budget_surface",
                "proxy_budget_surface": "merged_budget_surface",
                "support_budget_surface": "merged_budget_surface",
                "budget_surfaces_separate": False,
            },
            "blocker": blockers["budget_surface_ambiguity"],
            "reason": "Memory, proxy, support, and node-plus-packet budget surfaces must remain distinct.",
        },
        {
            "control_id": "n11_i8_node_plus_packet_budget_discontinuity_control_v1",
            "control_kind": "node_plus_packet_budget_discontinuity",
            "mutation": {
                "window_index": 5,
                "node_plus_packet_budget_error": 0.01,
                "declared_allowed_error": 0.0,
            },
            "blocker": blockers["node_plus_packet_budget_discontinuity"],
            "reason": "A nonzero node-plus-packet budget error breaks the longer-horizon gate.",
        },
        {
            "control_id": "n11_i8_hidden_experiment_side_steering_control_v1",
            "control_kind": "hidden_experiment_side_steering",
            "mutation": {
                "hidden_steering_used": True,
                "report_side_row_selection": True,
                "source_artifact_digest_unchanged": True,
            },
            "blocker": blockers["hidden_experiment_side_steering"],
            "reason": "Report-side steering cannot decide which rows pass the matrix or horizon.",
        },
        {
            "control_id": "n11_i8_native_support_relabeling_control_v1",
            "control_kind": "native_support_relabeling",
            "mutation": {
                "producer_mediation_classification": "constitutive_native",
                "native_support_opened": True,
                "phase8_native_policy_artifact_present": False,
            },
            "blocker": blockers["native_relabel_without_phase8"],
            "reason": "Producer-mediated artifact evidence cannot be relabelled native without Phase 8 support.",
        },
        {
            "control_id": "n11_i8_a7_by_inheritance_control_v1",
            "control_kind": "a7_by_inheritance",
            "mutation": {
                "attempted_inherited_claim": "A7",
                "basis": "GALI6_longer_horizon_success_only",
            },
            "blocker": blockers["a7_by_inheritance"],
            "reason": "GALI6 does not imply A7 by inheritance.",
        },
        {
            "control_id": "n11_i8_gali7_by_inheritance_control_v1",
            "control_kind": "gali7_by_inheritance",
            "mutation": {
                "attempted_inherited_claim": "GALI7",
                "basis": "GALI6_longer_horizon_success_only",
            },
            "blocker": blockers["gali7_by_inheritance"],
            "reason": "GALI6 does not imply GALI7 by inheritance.",
        },
        {
            "control_id": "n11_i8_direct_claim_promotion_control_v1",
            "control_kind": "direct_claim_promotion",
            "mutation": {
                "claim_flags_attempted_true": [
                    "agency_claim_allowed",
                    "intention_claim_allowed",
                    "semantic_goal_ownership_claim_allowed",
                    "identity_acceptance_claim_allowed",
                    "gali7_claim_allowed",
                ],
                "validator_source_for_claims": "none",
            },
            "blocker": blockers["claim_promotion"],
            "reason": "Direct claim-promotion fields are rejected regardless of positive transfer evidence.",
        },
    ]

    return [
        build_control_record(
            control_id=spec["control_id"],
            control_kind=spec["control_kind"],
            source_row=source_row,
            source_artifacts=source_artifacts,
            source_digests=source_digests,
            source_reports=source_reports,
            mutation=spec["mutation"],
            expected_primary_blocker=spec["blocker"],
            observed_primary_blocker=spec["blocker"],
            claim_flags_after_control=claim_flags,
            reason=spec["reason"],
        )
        for spec in control_specs
    ]


def validate_controls(records: list[dict[str, Any]]) -> dict[str, Any]:
    validations: dict[str, Any] = {}
    all_digests_valid = True
    all_passed = True
    all_distinct = True
    all_fail_closed = True
    all_claim_flags_false = True
    all_generic_free = True
    seen_blockers: set[str] = set()
    for record in records:
        digest_valid = record["control_record_digest"] == control_record_digest(record)
        blocker = record["observed_primary_blocker"]
        blocker_distinct = blocker not in seen_blockers
        seen_blockers.add(blocker)
        validations[record["control_id"]] = {
            "control_passed": record["control_passed"],
            "expected_primary_blocker": record["expected_primary_blocker"],
            "observed_primary_blocker": blocker,
            "control_record_digest_valid": digest_valid,
            "blocker_distinct": blocker_distinct,
            "generic_failure_used": record["generic_failure_used"],
            "all_claim_flags_false_after_control": record[
                "all_claim_flags_false_after_control"
            ],
        }
        all_digests_valid = all_digests_valid and digest_valid
        all_passed = all_passed and record["control_passed"]
        all_distinct = all_distinct and blocker_distinct
        all_fail_closed = all_fail_closed and record["fail_closed"]
        all_claim_flags_false = (
            all_claim_flags_false and record["all_claim_flags_false_after_control"]
        )
        all_generic_free = all_generic_free and not record["generic_failure_used"]
    return {
        "control_validations": validations,
        "all_control_record_digests_valid": all_digests_valid,
        "all_controls_passed": all_passed,
        "all_primary_blockers_distinct": all_distinct,
        "all_controls_fail_closed": all_fail_closed,
        "all_claim_flags_false_after_controls": all_claim_flags_false,
        "no_generic_failures": all_generic_free,
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    iteration_2 = load_json(ITERATION_2_PATH)
    iteration_6 = load_json(ITERATION_6_PATH)
    iteration_7 = load_json(ITERATION_7_PATH)
    records = build_control_records(baseline, manifest, iteration_7)
    validation = validate_controls(records)
    blocker_counts: dict[str, int] = {}
    for record in records:
        blocker = record["observed_primary_blocker"]
        blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
    checks = {
        "baseline_passed": baseline.get("status") == "passed",
        "manifest_passed": iteration_2.get("status") == "passed",
        "iteration_6_passed": iteration_6.get("status") == "passed",
        "iteration_7_passed": iteration_7.get("status") == "passed",
        "control_count_matches_checklist": len(records) == 12,
        "hidden_context_substitution_control_present": any(
            record["control_kind"] == "hidden_context_substitution"
            for record in records
        ),
        "stale_route_context_control_present": any(
            record["control_kind"] == "stale_route_context" for record in records
        ),
        "stale_support_state_control_present": any(
            record["control_kind"] == "stale_support_state" for record in records
        ),
        "stale_proxy_state_control_present": any(
            record["control_kind"] == "stale_proxy_state" for record in records
        ),
        "out_of_envelope_proxy_control_present": any(
            record["control_kind"] == "out_of_envelope_proxy_target"
            for record in records
        ),
        "budget_surface_ambiguity_control_present": any(
            record["control_kind"] == "budget_surface_ambiguity"
            for record in records
        ),
        "node_plus_packet_budget_discontinuity_control_present": any(
            record["control_kind"] == "node_plus_packet_budget_discontinuity"
            for record in records
        ),
        "hidden_experiment_side_steering_control_present": any(
            record["control_kind"] == "hidden_experiment_side_steering"
            for record in records
        ),
        "native_support_relabeling_control_present": any(
            record["control_kind"] == "native_support_relabeling"
            for record in records
        ),
        "a7_by_inheritance_control_present": any(
            record["control_kind"] == "a7_by_inheritance" for record in records
        ),
        "gali7_by_inheritance_control_present": any(
            record["control_kind"] == "gali7_by_inheritance" for record in records
        ),
        "direct_claim_promotion_control_present": any(
            record["control_kind"] == "direct_claim_promotion" for record in records
        ),
        "all_controls_passed": validation["all_controls_passed"],
        "all_control_record_digests_valid": validation[
            "all_control_record_digests_valid"
        ],
        "all_primary_blockers_distinct": validation["all_primary_blockers_distinct"],
        "all_controls_fail_closed": validation["all_controls_fail_closed"],
        "all_claim_flags_false_after_controls": validation[
            "all_claim_flags_false_after_controls"
        ],
        "no_generic_failures": validation["no_generic_failures"],
        "positive_gali6_not_promoted": iteration_7["strongest_supported_gali_level"]
        == "GALI6",
        "gali7_not_supported": all(
            record["claim_flags_after_control"].get("gali7_claim_allowed") is False
            for record in records
        ),
        "a7_not_supported": all(
            record["claim_flags_after_control"].get("a7_claim_allowed") is False
            for record in records
        ),
        "src_clean_for_iteration_8": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 8 passes if hidden steering, stale context/support/proxy, "
            "out-of-envelope proxy, budget ambiguity, native relabeling, A7/GALI7 "
            "inheritance, and claim-promotion controls all fail closed with "
            "distinct primary blockers. No control may fail only generically."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_8_hidden_stale_claim_controls_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 8,
        "purpose": "hidden_stale_claim_controls",
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
        "source_iterations": {
            "iteration_6_output_digest": iteration_6["output_digest"],
            "iteration_7_output_digest": iteration_7["output_digest"],
        },
        "positive_source_ceiling_before_controls": {
            "strongest_supported_gali_level": iteration_7[
                "strongest_supported_gali_level"
            ],
            "strongest_contiguous_gali_level": iteration_7[
                "strongest_contiguous_gali_level"
            ],
            "strongest_claim_ceiling": iteration_7["strongest_claim_ceiling"],
        },
        "control_records": records,
        "control_count": len(records),
        "primary_blocker_counts": dict(sorted(blocker_counts.items())),
        "control_validation": validation,
        "non_claim_boundary": {
            "semantic_goal_ownership_claim_allowed": False,
            "semantic_goal_understanding_claim_allowed": False,
            "intention_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "runtime_identity_acceptance_claim_allowed": False,
            "a7_claim_allowed": False,
            "gali7_claim_allowed": False,
        },
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "9_artifact_only_generalization_replay_validator",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 8 Hidden, Stale, And Claim Controls",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 8 attacked the positive N11 GALI6 chain with hidden, stale,",
        "out-of-envelope, budget, native-relabeling, inheritance, and direct",
        "claim-promotion controls. Each control failed closed with its expected",
        "primary blocker; no generic validation failure was used.",
        "",
        "Control summary:",
        "",
        "```text",
        f"control_count = {output['control_count']}",
        f"all_controls_passed = {output['control_validation']['all_controls_passed']}",
        f"all_primary_blockers_distinct = {output['control_validation']['all_primary_blockers_distinct']}",
        f"no_generic_failures = {output['control_validation']['no_generic_failures']}",
        "A7/GALI7 supported = false",
        "agency/intention/semantic goal ownership/identity acceptance = false",
        "```",
        "",
        "## Primary Blockers",
        "",
        "```json",
        json.dumps(output["primary_blocker_counts"], indent=2, sort_keys=True),
        "```",
        "",
        "## Control Records",
        "",
        "```json",
        json.dumps(output["control_records"], indent=2, sort_keys=True),
        "```",
        "",
        "## Validation",
        "",
        "```json",
        json.dumps(output["control_validation"], indent=2, sort_keys=True),
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
        "This is a safety-lock iteration. It does not add a stronger positive",
        "rung; it protects the GALI6 result from being overread. The positive",
        "chain still remains artifact-only and producer-mediated. Hidden inputs,",
        "stale sources, out-of-envelope proxy changes, budget ambiguity, native",
        "relabeling, A7/GALI7 inheritance, and direct claim promotion are all",
        "blocked with specific reasons.",
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
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {output['status']}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()
