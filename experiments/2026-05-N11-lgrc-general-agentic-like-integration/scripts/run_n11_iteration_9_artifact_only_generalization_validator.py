#!/usr/bin/env python3
"""Run N11 Iteration 9 artifact-only generalization replay validator."""

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
OUTPUTS = EXPERIMENT / "outputs"

ITERATION_PATHS = {
    "iteration_1": OUTPUTS / "n11_iteration_1_baseline_inventory.json",
    "iteration_2": OUTPUTS / "n11_iteration_2_fixture_manifest_validation.json",
    "iteration_3": OUTPUTS / "n11_iteration_3_route_context_transfer_replay.json",
    "iteration_4": OUTPUTS / "n11_iteration_4_proxy_condition_transfer_replay.json",
    "iteration_4b": OUTPUTS / "n11_iteration_4b_proxy_target_band_variant_probe.json",
    "iteration_5": OUTPUTS / "n11_iteration_5_support_state_transfer_replay.json",
    "iteration_6": OUTPUTS / "n11_iteration_6_multi_axis_transfer_matrix.json",
    "iteration_7": OUTPUTS / "n11_iteration_7_longer_horizon_generalization_window.json",
    "iteration_8": OUTPUTS / "n11_iteration_8_hidden_stale_claim_controls.json",
}

OUTPUT_PATH = OUTPUTS / "n11_iteration_9_artifact_only_generalization_validator.json"
REPORT_PATH = EXPERIMENT / "reports" / "n11_iteration_9_artifact_only_generalization_validator.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "run_n11_iteration_9_artifact_only_generalization_validator.py"
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


def artifact_output_digest(data: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in data.items() if key not in excluded})


def inventory_digest(data: dict[str, Any]) -> str:
    excluded = {"generated_at", "inventory_digest", "git"}
    return digest_value({key: value for key, value in data.items() if key not in excluded})


def validation_digest(data: dict[str, Any]) -> str:
    excluded = {"generated_at", "validation_digest", "git"}
    return digest_value({key: value for key, value in data.items() if key not in excluded})


def transfer_row_digest(row: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in row.items() if key != "transfer_row_digest"})


def matrix_cell_digest(row: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in row.items()
            if key not in {"matrix_cell_digest", "transfer_row_digest"}
        }
    )


def trend_digest(row: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in row.items()
            if key not in {"trend_digest", "transfer_row_digest"}
        }
    )


def control_record_digest(record: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in record.items() if key != "control_record_digest"}
    )


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def all_claim_flags_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def load_artifacts() -> dict[str, dict[str, Any]]:
    return {key: load_json(path) for key, path in ITERATION_PATHS.items()}


def validate_artifact_digests(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows: dict[str, dict[str, Any]] = {}
    for key, path in ITERATION_PATHS.items():
        data = artifacts[key]
        if key == "iteration_1":
            expected = data["inventory_digest"]
            current = inventory_digest(data)
            digest_field = "inventory_digest"
        elif key == "iteration_2":
            expected = data["validation_digest"]
            current = validation_digest(data)
            digest_field = "validation_digest"
        else:
            expected = data["output_digest"]
            current = artifact_output_digest(data)
            digest_field = "output_digest"
        rows[key] = {
            "path": rel(path),
            "sha256": digest_file(path),
            "status": data.get("status"),
            "digest_field": digest_field,
            "expected_digest": expected,
            "recomputed_digest": current,
            "digest_valid": expected == current,
        }
    return {
        "artifact_rows": rows,
        "all_artifacts_present": all(path.exists() for path in ITERATION_PATHS.values()),
        "all_artifact_digests_valid": all(row["digest_valid"] for row in rows.values()),
        "all_artifact_statuses_passed": all(
            artifacts[key].get("status") == "passed" for key in ITERATION_PATHS
        ),
    }


def required_transfer_fields(manifest: dict[str, Any]) -> list[str]:
    fields = manifest.get("transfer_row_required_fields")
    if fields is None:
        fields = manifest["frozen_schema"]["transfer_row_required_fields"]
    if not isinstance(fields, list):
        raise TypeError("transfer_row_required_fields must be a list")
    return list(fields)


def validate_transfer_rows(
    artifacts: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    required = required_transfer_fields(manifest)
    row_sources = [
        "iteration_3",
        "iteration_4",
        "iteration_4b",
        "iteration_5",
        "iteration_6",
        "iteration_7",
    ]
    validations: dict[str, dict[str, Any]] = {}
    all_required = True
    all_digests = True
    all_claims_false = True
    artifact_only_rows = True
    runtime_unused_rows = True
    for source_key in row_sources:
        for row in artifacts[source_key].get("transfer_rows", []):
            row_key = f"{source_key}:{row['transfer_row_id']}"
            missing = [field for field in required if field not in row]
            digest_valid = row["transfer_row_digest"] == transfer_row_digest(row)
            claims_false = all_claim_flags_false(row["claim_flags"])
            artifact_only = row.get("artifact_only") is True
            runtime_unused = row.get("runtime_state_used") is False
            validations[row_key] = {
                "missing_required_fields": missing,
                "transfer_row_digest_valid": digest_valid,
                "claim_flags_false": claims_false,
                "artifact_only": artifact_only,
                "runtime_state_used": row.get("runtime_state_used"),
                "primary_blocker": row.get("primary_blocker"),
                "transfer_accepted": row.get("transfer_accepted"),
                "gali_level": row.get("gali_level"),
            }
            all_required = all_required and not missing
            all_digests = all_digests and digest_valid
            all_claims_false = all_claims_false and claims_false
            artifact_only_rows = artifact_only_rows and artifact_only
            runtime_unused_rows = runtime_unused_rows and runtime_unused
    return {
        "row_validations": validations,
        "row_count": len(validations),
        "all_required_fields_present": all_required,
        "all_transfer_row_digests_valid": all_digests,
        "all_claim_flags_false": all_claims_false,
        "all_rows_artifact_only": artifact_only_rows,
        "all_rows_runtime_state_unused": runtime_unused_rows,
    }


def validate_context_proxy_support_matrix(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    iteration_6 = artifacts["iteration_6"]
    rows = iteration_6["transfer_rows"]
    matrix_summary = iteration_6["matrix_summary"]
    matrix_digest_valid = all(
        row["matrix_cell_digest"] == matrix_cell_digest(row) for row in rows
    )
    accepted = [row for row in rows if row["transfer_accepted"]]
    blocked = [row for row in rows if not row["transfer_accepted"]]
    context_variants = {row["context_tag"] for row in rows}
    proxy_variants = {row["proxy_condition_tag"] for row in rows}
    support_variants = {row["support_state_tag"] for row in rows}
    expected_row_count = artifacts["iteration_2"]["multi_axis_matrix_spec"][
        "expected_minimum_row_count"
    ]
    return {
        "row_count": len(rows),
        "accepted_row_count": len(accepted),
        "blocked_row_count": len(blocked),
        "accepted_gali5_row_count": matrix_summary["accepted_gali5_row_count"],
        "matrix_cell_digests_valid": matrix_digest_valid,
        "row_count_matches_manifest": len(rows) == expected_row_count,
        "context_variant_count": len(context_variants),
        "proxy_variant_count": len(proxy_variants),
        "support_variant_count": len(support_variants),
        "accepted_and_blocked_rows_present": bool(accepted) and bool(blocked),
        "distinct_blockers_present": set(matrix_summary["primary_blocker_counts"]) >= {
            "context_arbitration_policy_variant_missing_source",
            "support_disrupted_but_integration_allowed",
            "null",
        },
        "all_source_status_digest_links_present": all(
            row["source_status"][axis]["source_digest"]
            for row in rows
            for axis in ("context", "proxy", "support")
        ),
        "all_budget_surfaces_separate": all(
            len(
                {
                    row["memory_budget_surface"],
                    row["proxy_budget_surface"],
                    row["support_budget_surface"],
                }
            )
            == 3
            for row in rows
        ),
    }


def validate_longer_horizon(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    iteration_7 = artifacts["iteration_7"]
    rows = iteration_7["transfer_rows"]
    summary = iteration_7["longer_horizon_summary"]
    required_trends = set(
        artifacts["iteration_2"]["longer_horizon_window_spec"][
            "trend_fields_required"
        ]
    )
    trend_fields_present = all(
        required_trends <= set(row["trend_fields"]) for row in rows
    )
    trend_digests_valid = all(row["trend_digest"] == trend_digest(row) for row in rows)
    source_current = all(
        status["source_current"] is True
        for row in rows
        for status in row["trend_fields"]["source_current_status_by_window"]
    )
    order_valid = all(
        [record["window_index"] for record in row["window_records"]]
        == list(range(1, row["window_count"] + 1))
        for row in rows
    )
    budget_zero = all(
        error["node_plus_packet_budget_error"] == 0.0
        for row in rows
        for error in row["trend_fields"]["node_plus_packet_budget_error_by_window"]
    )
    proxy_in_band = all(
        all(row["trend_fields"]["proxy_trend"]["proxy_in_band_after_by_window"])
        for row in rows
    )
    support_survives = all(
        row["trend_fields"]["support_trend"]["support_survival_passed_all_windows"]
        is True
        for row in rows
    )
    stable = all(
        row["trend_fields"]["transfer_stability_trend"]["unstable_window_count"] == 0
        for row in rows
    )
    return {
        "row_count": len(rows),
        "accepted_gali6_row_count": summary["accepted_gali6_row_count"],
        "trend_fields_present": trend_fields_present,
        "trend_digests_valid": trend_digests_valid,
        "source_current_all_windows": source_current,
        "event_window_order_valid": order_valid,
        "budget_zero_all_windows": budget_zero,
        "proxy_in_band_all_windows": proxy_in_band,
        "support_survives_all_windows": support_survives,
        "transfer_stable_all_windows": stable,
        "node_plus_packet_budget_error_max": summary["node_plus_packet_budget_error_max"],
        "unstable_window_count": summary["unstable_window_count"],
    }


def validate_controls(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    iteration_8 = artifacts["iteration_8"]
    records = iteration_8["control_records"]
    digest_valid = all(
        record["control_record_digest"] == control_record_digest(record)
        for record in records
    )
    blockers = [record["observed_primary_blocker"] for record in records]
    all_distinct = len(set(blockers)) == len(blockers)
    all_expected = all(
        record["observed_primary_blocker"] == record["expected_primary_blocker"]
        for record in records
    )
    return {
        "control_count": len(records),
        "control_record_digests_valid": digest_valid,
        "all_controls_passed": all(record["control_passed"] for record in records),
        "all_primary_blockers_distinct": all_distinct,
        "all_observed_blockers_match_expected": all_expected,
        "all_controls_fail_closed": all(record["fail_closed"] for record in records),
        "no_generic_failures": all(not record["generic_failure_used"] for record in records),
        "all_claim_flags_false_after_controls": all(
            record["all_claim_flags_false_after_control"] for record in records
        ),
    }


def validate_source_digest_links(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    path_by_rel = {rel(path): path for path in ITERATION_PATHS.values()}
    checked_links = []
    all_match = True
    for source_key in ("iteration_6", "iteration_7", "iteration_8"):
        records: list[dict[str, Any]]
        if source_key == "iteration_8":
            records = artifacts[source_key]["control_records"]
            artifact_field = "source_positive_artifacts"
            digest_field = "source_positive_artifact_digests"
        else:
            records = artifacts[source_key]["transfer_rows"]
            artifact_field = "source_artifacts"
            digest_field = "source_artifact_digests"
        for record in records:
            for artifact_key, rel_path in record.get(artifact_field, {}).items():
                expected = record.get(digest_field, {}).get(artifact_key)
                path = path_by_rel.get(rel_path) or (ROOT / rel_path)
                exists = path.exists()
                current = digest_file(path) if exists else None
                matches = exists and expected == current
                checked_links.append(
                    {
                        "record_source": source_key,
                        "artifact_key": artifact_key,
                        "path": rel_path,
                        "exists": exists,
                        "expected_sha256": expected,
                        "current_sha256": current,
                        "matches": matches,
                    }
                )
                all_match = all_match and matches
    return {
        "checked_link_count": len(checked_links),
        "all_source_digest_links_match": all_match,
        "checked_links": checked_links[:40],
        "checked_links_truncated": len(checked_links) > 40,
    }


def build_output() -> dict[str, Any]:
    artifacts = load_artifacts()
    manifest = artifacts["iteration_2"]
    manifest_required_passes = manifest["artifact_validator_architecture"][
        "required_passes"
    ]
    artifact_digest_pass = validate_artifact_digests(artifacts)
    transfer_schema_pass = validate_transfer_rows(artifacts, manifest)
    matrix_pass = validate_context_proxy_support_matrix(artifacts)
    longer_horizon_pass = validate_longer_horizon(artifacts)
    control_pass = validate_controls(artifacts)
    source_digest_pass = validate_source_digest_links(artifacts)

    budget_surface_pass = {
        "matrix_budget_surfaces_separate": matrix_pass["all_budget_surfaces_separate"],
        "longer_horizon_budget_zero": longer_horizon_pass["budget_zero_all_windows"],
        "control_budget_discontinuity_rejected": (
            "node_plus_packet_budget_discontinuity"
            in artifacts["iteration_8"]["primary_blocker_counts"]
        ),
        "passed": (
            matrix_pass["all_budget_surfaces_separate"]
            and longer_horizon_pass["budget_zero_all_windows"]
            and "node_plus_packet_budget_discontinuity"
            in artifacts["iteration_8"]["primary_blocker_counts"]
        ),
    }
    claim_boundary_pass = {
        "all_transfer_row_claim_flags_false": transfer_schema_pass[
            "all_claim_flags_false"
        ],
        "all_control_claim_flags_false": control_pass[
            "all_claim_flags_false_after_controls"
        ],
        "gali7_not_supported": all(
            artifact.get("non_claim_boundary", {}).get("gali7_claim_allowed") is False
            for artifact in (artifacts["iteration_6"], artifacts["iteration_7"], artifacts["iteration_8"])
        ),
        "a7_not_supported": all(
            artifact.get("non_claim_boundary", {}).get("a7_claim_allowed") is False
            for artifact in (artifacts["iteration_6"], artifacts["iteration_7"], artifacts["iteration_8"])
        ),
    }
    claim_boundary_pass["passed"] = all(claim_boundary_pass.values())

    validation_passes = {
        "source_artifact_digest_pass": (
            artifact_digest_pass["all_artifacts_present"]
            and artifact_digest_pass["all_artifact_digests_valid"]
            and artifact_digest_pass["all_artifact_statuses_passed"]
            and source_digest_pass["all_source_digest_links_match"]
            and artifacts["iteration_2"]["source_digest_validation"]["all_match"]
            and artifacts["iteration_1"]["checks"]["prior_output_digests_valid"]
        ),
        "transfer_row_schema_pass": (
            transfer_schema_pass["all_required_fields_present"]
            and transfer_schema_pass["all_transfer_row_digests_valid"]
            and transfer_schema_pass["all_rows_artifact_only"]
            and transfer_schema_pass["all_rows_runtime_state_unused"]
        ),
        "context_proxy_support_matrix_pass": (
            matrix_pass["row_count_matches_manifest"]
            and matrix_pass["matrix_cell_digests_valid"]
            and matrix_pass["accepted_and_blocked_rows_present"]
        ),
        "longer_horizon_window_pass": (
            longer_horizon_pass["trend_fields_present"]
            and longer_horizon_pass["trend_digests_valid"]
            and longer_horizon_pass["source_current_all_windows"]
            and longer_horizon_pass["event_window_order_valid"]
            and longer_horizon_pass["budget_zero_all_windows"]
        ),
        "negative_control_pass": (
            control_pass["control_record_digests_valid"]
            and control_pass["all_controls_passed"]
            and control_pass["all_primary_blockers_distinct"]
            and control_pass["all_controls_fail_closed"]
            and control_pass["no_generic_failures"]
        ),
        "budget_surface_pass": budget_surface_pass["passed"],
        "claim_boundary_pass": claim_boundary_pass["passed"],
    }
    undeclared_validation_passes = sorted(
        set(validation_passes) - set(manifest_required_passes)
    )
    missing_manifest_passes = sorted(
        set(manifest_required_passes) - set(validation_passes)
    )
    all_manifest_required_passes_passed = (
        not missing_manifest_passes
        and not undeclared_validation_passes
        and all(validation_passes[name] for name in manifest_required_passes)
    )
    checks = {
        "all_artifacts_present": artifact_digest_pass["all_artifacts_present"],
        "all_artifact_statuses_passed": artifact_digest_pass[
            "all_artifact_statuses_passed"
        ],
        "all_artifact_digests_valid": artifact_digest_pass[
            "all_artifact_digests_valid"
        ],
        "all_source_digest_links_match": source_digest_pass[
            "all_source_digest_links_match"
        ],
        "transfer_rows_validate": validation_passes["transfer_row_schema_pass"],
        "matrix_validates": validation_passes["context_proxy_support_matrix_pass"],
        "longer_horizon_validates": validation_passes["longer_horizon_window_pass"],
        "controls_validate": validation_passes["negative_control_pass"],
        "budget_surfaces_validate": validation_passes["budget_surface_pass"],
        "claim_boundary_validates": validation_passes["claim_boundary_pass"],
        "manifest_required_passes_match": (
            not missing_manifest_passes and not undeclared_validation_passes
        ),
        "all_manifest_required_passes_passed": all_manifest_required_passes_passed,
        "artifact_only": True,
        "runtime_state_not_used": True,
        "src_clean_for_iteration_9": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 9 passes if an artifact-only validator reconstructs the "
            "accepted N11 generalization chain and controls from exported "
            "artifacts, with stable digests, event/window ordering, separated "
            "budget surfaces, source-current status, and no private runtime "
            "fallback."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_9_artifact_only_generalization_validator_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 9,
        "purpose": "artifact_only_generalization_replay_validator",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "artifact_only": True,
        "runtime_state_used": False,
        "private_runtime_state_used": False,
        "runtime_state_fallback_used": False,
        "validator_architecture": artifacts["iteration_2"][
            "artifact_validator_architecture"
        ],
        "manifest_required_passes": manifest_required_passes,
        "missing_manifest_passes": missing_manifest_passes,
        "undeclared_validation_passes": undeclared_validation_passes,
        "artifact_digest_pass": artifact_digest_pass,
        "source_digest_pass": source_digest_pass,
        "transfer_row_schema_pass": transfer_schema_pass,
        "context_proxy_support_matrix_pass": matrix_pass,
        "longer_horizon_window_pass": longer_horizon_pass,
        "negative_control_pass": control_pass,
        "budget_surface_pass": budget_surface_pass,
        "claim_boundary_pass": claim_boundary_pass,
        "validation_passes": validation_passes,
        "strongest_replayed_gali_level": "GALI6",
        "strongest_replayed_claim_ceiling": "longer_horizon_generalization_candidate",
        "gali7_supported": False,
        "a7_supported": False,
        "controls_supported": artifacts["iteration_8"]["control_count"],
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "10_hypothesis_ab_closeout",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 9 Artifact-Only Generalization Validator",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 9 reconstructed the N11 generalization chain from exported",
        "artifacts only. It validated artifact digests, source links, transfer",
        "row schemas, the context/proxy/support matrix, the longer-horizon",
        "window, negative controls, budget-surface separation, and claim",
        "boundaries without private runtime state.",
        "",
        "Current replayed ceiling:",
        "",
        "```text",
        f"strongest_replayed_gali_level = {output['strongest_replayed_gali_level']}",
        f"strongest_replayed_claim_ceiling = {output['strongest_replayed_claim_ceiling']}",
        "artifact_only = true",
        "runtime_state_used = false",
        "A7/GALI7 supported = false",
        "```",
        "",
        "## Validation Passes",
        "",
        "```json",
        json.dumps(output["validation_passes"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Matrix Summary",
        "",
        "```json",
        json.dumps(output["context_proxy_support_matrix_pass"], indent=2, sort_keys=True),
        "```",
        "",
        "## Longer Horizon Summary",
        "",
        "```json",
        json.dumps(output["longer_horizon_window_pass"], indent=2, sort_keys=True),
        "```",
        "",
        "## Control Summary",
        "",
        "```json",
        json.dumps(output["negative_control_pass"], indent=2, sort_keys=True),
        "```",
        "",
        "## Interpretation",
        "",
        "This validator strengthens the artifact-only status of the GALI6 chain.",
        "It does not convert the result into GALI7/A7 or native agency. The",
        "remaining boundary is still broader/general artifact-only integration",
        "and later native absorption, not replayability of the existing GALI6",
        "evidence.",
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
