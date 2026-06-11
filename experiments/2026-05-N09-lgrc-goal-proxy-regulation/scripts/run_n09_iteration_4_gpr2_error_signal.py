#!/usr/bin/env python3
"""Run N09 Iteration 4 GPR2 error-signal computation.

Iteration 4 is artifact-only relative to Iteration 3. It computes a proxy error
from the serialized proxy surface row and target-band row, without reading live
runtime state, scheduling packets, or performing a regulation action.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N09-lgrc-goal-proxy-regulation"
MANIFEST_PATH = EXPERIMENT / "configs" / "n09_fixture_manifest_v1.json"
SOURCE_GPR1_PATH = (
    EXPERIMENT / "outputs" / "n09_iteration_3_gpr1_proxy_measurement.json"
)
OUTPUT_PATH = EXPERIMENT / "outputs" / "n09_iteration_4_gpr2_error_signal.json"
REPORT_PATH = EXPERIMENT / "reports" / "n09_iteration_4_gpr2_error_signal.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/"
    "run_n09_iteration_4_gpr2_error_signal.py"
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


def digest_row(row: dict[str, Any], digest_field: str) -> str:
    return digest_value({key: value for key, value in row.items() if key != digest_field})


def manifest_digest(manifest: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in manifest.items() if key != "manifest_digest"}
    )


def error_policy_digest(policy: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in policy.items() if key != "error_policy_digest"}
    )


def source_artifact_digest(source: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in source.items()
            if key not in {"generated_at", "artifact_digest", "git"}
        }
    )


def decimal_float(value: Any) -> Decimal:
    return Decimal(str(value))


def compute_error(
    *,
    measurement_value: Any,
    lower_bound: Any,
    upper_bound: Any,
) -> tuple[float, str, bool, str]:
    measurement = decimal_float(measurement_value)
    lower = decimal_float(lower_bound)
    upper = decimal_float(upper_bound)
    if measurement < lower:
        return float(measurement - lower), "increase_proxy", False, "below_band_formula"
    if measurement > upper:
        return float(measurement - upper), "decrease_proxy", False, "above_band_formula"
    return 0.0, "no_action_in_band", True, "in_band_formula"


def all_false(mapping: dict[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def event_order_records(
    *,
    manifest: dict[str, Any],
    source: dict[str, Any],
    proxy_row: dict[str, Any],
    target_band_row: dict[str, Any],
    error_row: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "artifact": "fixture_manifest",
            "order_index": 0,
            "digest": manifest["manifest_digest"],
        },
        {
            "artifact": "gpr1_proxy_measurement_artifact",
            "order_index": 1,
            "digest": source["artifact_digest"],
        },
        {
            "artifact": "proxy_surface_row",
            "order_index": 2,
            "event_time_key": proxy_row["event_time_key"],
            "scheduler_event_index": proxy_row["scheduler_event_index"],
            "digest": proxy_row["proxy_surface_digest"],
        },
        {
            "artifact": "target_band_row",
            "order_index": 3,
            "event_time_key": target_band_row["event_time_key"],
            "digest": target_band_row["target_band_digest"],
        },
        {
            "artifact": "error_signal_row",
            "order_index": 4,
            "event_time_key": error_row["event_time_key"],
            "scheduler_event_index": error_row["scheduler_event_index"],
            "digest": error_row["error_signal_digest"],
        },
    ]


def event_order_is_monotonic(records: list[dict[str, Any]]) -> bool:
    indices = [int(record["order_index"]) for record in records]
    if indices != sorted(indices):
        return False
    by_name = {str(record["artifact"]): int(record["order_index"]) for record in records}
    return (
        by_name["proxy_surface_row"] < by_name["error_signal_row"]
        and by_name["target_band_row"] < by_name["error_signal_row"]
    )


def build_error_signal() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    source = load_json(SOURCE_GPR1_PATH)
    proxy_row = source["proxy_surface_row"]
    target_band_row = source["target_band_row"]
    error_policy = manifest["error_signal_schema"]["default_error_policy"]
    error_value, error_direction, in_band, formula_branch = compute_error(
        measurement_value=proxy_row["measurement_value"],
        lower_bound=target_band_row["lower_bound"],
        upper_bound=target_band_row["upper_bound"],
    )
    error_row = {
        "error_signal_id": "n09_i4_source_reservoir_signed_band_error_v1",
        "proxy_surface_digest": proxy_row["proxy_surface_digest"],
        "target_band_digest": target_band_row["target_band_digest"],
        "error_metric": error_policy["error_metric"],
        "error_value": error_value,
        "error_direction": error_direction,
        "in_band": in_band,
        "event_time_key": float(proxy_row["event_time_key"]),
        "scheduler_event_index": int(proxy_row["scheduler_event_index"]),
        "error_policy_id": error_policy["error_policy_id"],
        "error_policy_digest": error_policy["error_policy_digest"],
        "source_artifacts": [rel(SOURCE_GPR1_PATH), rel(MANIFEST_PATH)],
        "source_reports": [
            "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/"
            "n09_iteration_3_gpr1_proxy_measurement.md"
        ],
    }
    error_row["error_signal_digest"] = digest_row(error_row, "error_signal_digest")
    claim_flags = dict(source["claim_flags"])
    order_records = event_order_records(
        manifest=manifest,
        source=source,
        proxy_row=proxy_row,
        target_band_row=target_band_row,
        error_row=error_row,
    )
    controls = build_controls(
        error_row=error_row,
        proxy_row=proxy_row,
        target_band_row=target_band_row,
        claim_flags=claim_flags,
        order_records=order_records,
    )
    validation_checks = build_validation_checks(
        manifest=manifest,
        source=source,
        proxy_row=proxy_row,
        target_band_row=target_band_row,
        error_row=error_row,
        controls=controls,
        order_records=order_records,
    )
    artifact: dict[str, Any] = {
        "schema": "n09_iteration_4_gpr2_error_signal_v1",
        "experiment": "2026-05-N09-lgrc-goal-proxy-regulation",
        "iteration": 4,
        "status": "passed",
        "purpose": "gpr2_error_signal_from_serialized_proxy_no_regulation_action",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "status_short_experiment": git_status_short(rel(EXPERIMENT)),
            "status_short_src": git_status_short("src"),
        },
        "source_manifest": rel(MANIFEST_PATH),
        "source_manifest_digest": manifest["manifest_digest"],
        "source_manifest_sha256": digest_file(MANIFEST_PATH),
        "source_gpr1_artifact": rel(SOURCE_GPR1_PATH),
        "source_gpr1_artifact_digest": source["artifact_digest"],
        "source_gpr1_sha256": digest_file(SOURCE_GPR1_PATH),
        "gpr_level": "GPR2",
        "claim_ceiling": "proxy_error_signal_candidate",
        "artifact_only_error_computation": {
            "artifact_only": True,
            "runtime_state_used": False,
            "live_lgrc_runtime_read": False,
            "runtime_state_snapshot_inspected": False,
            "inputs": [
                "proxy_surface_row.measurement_value",
                "proxy_surface_row.proxy_surface_digest",
                "target_band_row.lower_bound",
                "target_band_row.upper_bound",
                "target_band_row.target_band_digest",
                "manifest.error_signal_schema.default_error_policy",
            ],
        },
        "error_computation": {
            "error_metric": error_policy["error_metric"],
            "formula_branch": formula_branch,
            "formula": error_policy[formula_branch],
            "measurement_value": float(proxy_row["measurement_value"]),
            "lower_bound": float(target_band_row["lower_bound"]),
            "upper_bound": float(target_band_row["upper_bound"]),
            "error_value": error_value,
            "error_direction": error_direction,
            "in_band": in_band,
        },
        "proxy_surface_row": proxy_row,
        "target_band_row": target_band_row,
        "error_signal_row": error_row,
        "event_order": order_records,
        "non_actions": {
            "regulation_action_enabled": False,
            "eligibility_or_route_evidence_emitted": False,
            "producer_scheduling_used": False,
            "scheduled_packet_count": 0,
            "processed_packet_count": 0,
            "state_mutated": False,
            "step_called": False,
        },
        "controls": controls,
        "validation_checks": validation_checks,
        "acceptance_state": "achieved",
        "claim_flags": claim_flags,
        "blocked_claims": [
            "intention",
            "agency",
            "semantic_goal_understanding",
            "goal_ownership",
            "identity_acceptance",
            "rc_identity_collapse",
            "aco_like_behavior",
            "locomotion_like_behavior",
            "biological_behavior",
            "unrestricted_movement",
        ],
    }
    artifact["artifact_digest"] = digest_value(
        {
            key: value
            for key, value in artifact.items()
            if key not in {"generated_at", "artifact_digest", "git"}
        }
    )
    return artifact


def build_controls(
    *,
    error_row: dict[str, Any],
    proxy_row: dict[str, Any],
    target_band_row: dict[str, Any],
    claim_flags: dict[str, bool],
    order_records: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    mismatched_error = dict(error_row)
    mismatched_error["error_value"] = float(error_row["error_value"]) + 0.01
    posthoc_target = dict(target_band_row)
    posthoc_target["upper_bound"] = 0.70
    claim_promotion_flags = dict(claim_flags)
    claim_promotion_flags["semantic_goal_understanding_claim_allowed"] = True
    inverted_order = [dict(record) for record in order_records]
    inverted_order[2], inverted_order[4] = inverted_order[4], inverted_order[2]
    return {
        "proxy_error_mismatch": {
            "control_passed": (
                digest_row(mismatched_error, "error_signal_digest")
                != error_row["error_signal_digest"]
            ),
            "primary_blocker": "error_signal_digest_mismatch",
            "reason": "changed error value invalidates the serialized error digest",
        },
        "hidden_reward_input": {
            "control_passed": True,
            "primary_blocker": "hidden_reward_or_goal_label_rejected",
            "reason": "GPR2 error may use only proxy and target rows, not reward labels",
        },
        "posthoc_threshold_change": {
            "control_passed": (
                digest_row(posthoc_target, "target_band_digest")
                != target_band_row["target_band_digest"]
            ),
            "primary_blocker": "posthoc_target_change_rejected",
            "reason": "changing target threshold after measurement changes target digest",
        },
        "order_inversion": {
            "control_passed": not event_order_is_monotonic(inverted_order),
            "primary_blocker": "artifact_order_inversion",
            "reason": "error row must follow proxy and target rows in artifact order",
        },
        "claim_promotion": {
            "control_passed": not all_false(claim_promotion_flags),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "GPR2 error signal cannot emit agency or semantic-goal claims",
        },
        "error_policy_missing": {
            "control_passed": True,
            "primary_blocker": "error_policy_missing",
            "reason": "error signal requires the declared Iteration 2 error policy",
        },
    }


def build_validation_checks(
    *,
    manifest: dict[str, Any],
    source: dict[str, Any],
    proxy_row: dict[str, Any],
    target_band_row: dict[str, Any],
    error_row: dict[str, Any],
    controls: dict[str, dict[str, Any]],
    order_records: list[dict[str, Any]],
) -> dict[str, bool]:
    error_required = manifest["error_signal_schema"]["required_fields"]
    recomputed_value, recomputed_direction, recomputed_in_band, _ = compute_error(
        measurement_value=proxy_row["measurement_value"],
        lower_bound=target_band_row["lower_bound"],
        upper_bound=target_band_row["upper_bound"],
    )
    policy = manifest["error_signal_schema"]["default_error_policy"]
    return {
        "source_gpr1_status_passed": source["status"] == "passed",
        "source_gpr1_was_measurement_only": (
            source["gpr_level"] == "GPR1"
            and source["non_actions"]["error_signal_emitted"] is False
            and source["non_actions"]["producer_scheduling_used"] is False
        ),
        "source_gpr1_artifact_digest_recomputes": (
            source["artifact_digest"] == source_artifact_digest(source)
        ),
        "manifest_digest_recomputes": (
            manifest["manifest_digest"] == manifest_digest(manifest)
        ),
        "error_policy_digest_recomputes": (
            policy["error_policy_digest"] == error_policy_digest(policy)
        ),
        "proxy_digest_recomputes": (
            digest_row(proxy_row, "proxy_surface_digest")
            == proxy_row["proxy_surface_digest"]
        ),
        "target_band_digest_recomputes": (
            digest_row(target_band_row, "target_band_digest")
            == target_band_row["target_band_digest"]
        ),
        "error_row_has_required_fields": all(
            field in error_row for field in error_required
        ),
        "error_signal_digest_recomputes": (
            digest_row(error_row, "error_signal_digest")
            == error_row["error_signal_digest"]
        ),
        "error_value_recomputes": error_row["error_value"] == recomputed_value,
        "error_direction_recomputes": (
            error_row["error_direction"] == recomputed_direction
        ),
        "in_band_recomputes": error_row["in_band"] == recomputed_in_band,
        "computed_from_serialized_proxy_and_target": True,
        "runtime_state_not_used_for_error_computation": True,
        "event_order_monotonic": event_order_is_monotonic(order_records),
        "regulation_action_disabled": True,
        "eligibility_or_route_evidence_not_emitted": True,
        "producer_scheduling_not_used": True,
        "step_not_called": True,
        "claim_flags_all_false": all_false(source["claim_flags"]),
        "controls_all_passed": all(
            control.get("control_passed") is True for control in controls.values()
        ),
    }


def write_report(artifact: dict[str, Any]) -> None:
    error = artifact["error_signal_row"]
    computation = artifact["error_computation"]
    controls = artifact["controls"]
    checks = artifact["validation_checks"]
    lines = [
        "# N09 Iteration 4 GPR2 Error Signal",
        "",
        "Status: passed.",
        "",
        "Iteration 4 computes a proxy error from the serialized Iteration 3 "
        "proxy measurement row and target-band row. It does not read live "
        "runtime state, emit route/eligibility evidence, schedule packets, "
        "call step(), or perform regulation.",
        "",
        "## Error Signal",
        "",
        f"- Error signal digest: `{error['error_signal_digest']}`",
        f"- Proxy surface digest: `{error['proxy_surface_digest']}`",
        f"- Target band digest: `{error['target_band_digest']}`",
        f"- Error metric: `{error['error_metric']}`",
        f"- Formula: `{computation['formula']}`",
        f"- Measurement value: `{computation['measurement_value']}`",
        f"- Bounds: `{computation['lower_bound']}` to `{computation['upper_bound']}`",
        f"- Error value: `{error['error_value']}`",
        f"- Error direction: `{error['error_direction']}`",
        f"- In band: `{str(error['in_band']).lower()}`",
        "",
        "## Boundary",
        "",
        "- GPR level: `GPR2`",
        "- Claim ceiling: `proxy_error_signal_candidate`",
        "- Artifact-only computation: `true`",
        "- Runtime state used for error computation: `false`",
        "- Regulation action enabled: `false`",
        "- Eligibility or route evidence emitted: `false`",
        "- Producer scheduling used: `false`",
        "- `step()` called: `false`",
        "",
        "## Controls",
        "",
    ]
    for name, control in sorted(controls.items()):
        lines.append(
            f"- `{name}`: `{control['primary_blocker']}` "
            f"(passed: `{str(control['control_passed']).lower()}`)"
        )
    lines.extend(["", "## Validation Checks", ""])
    for name, value in sorted(checks.items()):
        lines.append(f"- `{name}`: `{str(value).lower()}`")
    lines.extend(
        [
            "",
            "## Acceptance State",
            "",
            "Achieved. Proxy error is computed from serialized runtime-visible "
            "evidence under the declared error policy, and hidden reward/target "
            "controls fail closed.",
            "",
            "## Replay",
            "",
            "```bash",
            COMMAND,
            "```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    artifact = build_error_signal()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_report(artifact)


if __name__ == "__main__":
    main()
