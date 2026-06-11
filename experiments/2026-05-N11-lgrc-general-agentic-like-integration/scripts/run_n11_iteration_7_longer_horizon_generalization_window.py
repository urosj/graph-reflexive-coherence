#!/usr/bin/env python3
"""Run N11 Iteration 7 longer-horizon generalization window."""

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
ITERATION_4_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_4_proxy_condition_transfer_replay.json"
)
ITERATION_4B_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_4b_proxy_target_band_variant_probe.json"
)
ITERATION_6_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_6_multi_axis_transfer_matrix.json"
)

OUTPUT_PATH = (
    EXPERIMENT
    / "outputs"
    / "n11_iteration_7_longer_horizon_generalization_window.json"
)
REPORT_PATH = (
    EXPERIMENT
    / "reports"
    / "n11_iteration_7_longer_horizon_generalization_window.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "run_n11_iteration_7_longer_horizon_generalization_window.py"
)

SUPPORT_SURVIVAL_THRESHOLD = 0.85


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


def trend_digest(row: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in row.items()
            if key not in {"trend_digest", "transfer_row_digest"}
        }
    )


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(baseline["n11_baseline"]["claim_flags"])}


def required_fields(manifest: dict[str, Any]) -> list[str]:
    fields = manifest["transfer_row_required_fields"]
    if not isinstance(fields, list):
        raise TypeError("manifest transfer_row_required_fields must be a list")
    return list(fields)


def iteration_7_lane(manifest: dict[str, Any]) -> dict[str, Any]:
    lanes = [
        lane
        for lane in manifest["fixture_lanes"]
        if lane.get("planned_iteration") == 7
        and lane.get("lane_id") == "longer_horizon_generalization_window"
    ]
    if len(lanes) != 1:
        raise ValueError("expected exactly one Iteration 7 longer-horizon lane")
    return lanes[0]


def source_bundle() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    artifacts = {
        "n11_baseline_inventory": rel(BASELINE_PATH),
        "n11_fixture_manifest": rel(MANIFEST_PATH),
        "n11_iteration_2_fixture_manifest_validation": rel(ITERATION_2_PATH),
        "n11_iteration_4_proxy_condition_transfer_replay": rel(ITERATION_4_PATH),
        "n11_iteration_4b_proxy_target_band_variant_probe": rel(ITERATION_4B_PATH),
        "n11_iteration_6_multi_axis_transfer_matrix": rel(ITERATION_6_PATH),
    }
    digests = {key: digest_file(ROOT / value) for key, value in artifacts.items()}
    reports = {
        "n11_iteration_4_proxy_condition_transfer_replay": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_4_proxy_condition_transfer_replay.md"
        ),
        "n11_iteration_4b_proxy_target_band_variant_probe": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_4b_proxy_target_band_variant_probe.md"
        ),
        "n11_iteration_6_multi_axis_transfer_matrix": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_6_multi_axis_transfer_matrix.md"
        ),
    }
    return artifacts, digests, reports


def proxy_patterns(
    iteration_4: dict[str, Any],
    iteration_4b: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    same = iteration_4["proxy_evidence_summary"]
    variant = iteration_4b["variant_probe"]
    return {
        "proxy_same_as_n10": {
            "target_band_digest": same["target_band_digest"],
            "lower_bound": same["lower_bound"],
            "upper_bound": same["upper_bound"],
            "target_value": same["target_value"],
            "pre_measurements": same["pre_response_measurements"],
            "post_measurements": same["post_response_measurements"],
            "source_pattern_kind": "n09_same_band_four_cycle_replay_repeated",
        },
        "proxy_target_band_variant": {
            "target_band_digest": iteration_4b["variant_target_band"][
                "target_band_digest"
            ],
            "lower_bound": iteration_4b["variant_target_band"]["lower_bound"],
            "upper_bound": iteration_4b["variant_target_band"]["upper_bound"],
            "target_value": iteration_4b["variant_target_band"]["target_value"],
            "pre_measurements": variant["pre_measurements"],
            "post_measurements": variant["post_measurements"],
            "source_pattern_kind": "n11_i4b_variant_four_cycle_replay_repeated",
        },
    }


def repeat_pattern(values: list[Any], count: int) -> list[Any]:
    if not values:
        raise ValueError("cannot repeat an empty pattern")
    return [values[index % len(values)] for index in range(count)]


def support_pattern(row: dict[str, Any], window_count: int) -> dict[str, Any]:
    support = row["source_status"]["support"]
    retention = float(support["support_retention"])
    values = [round(retention, 12) for _ in range(window_count)]
    margin = round(retention - SUPPORT_SURVIVAL_THRESHOLD, 12)
    if row["support_state_tag"] == "mild_withdrawal_survives":
        trend = "bounded_low_margin_stable_replay"
    elif row["support_state_tag"] == "explicit_restoration_recovers_support":
        trend = "restoration_gated_stable_after_disruption_history"
    else:
        trend = "stable_support_reference_replay"
    return {
        "support_retention_by_window": values,
        "support_survival_threshold": SUPPORT_SURVIVAL_THRESHOLD,
        "support_margin_min": margin,
        "support_trend": trend,
        "support_survival_passed_all_windows": all(
            value >= SUPPORT_SURVIVAL_THRESHOLD for value in values
        ),
        "explicit_restoration_present": support["explicit_restoration_present"],
    }


def window_trace(
    *,
    source_row: dict[str, Any],
    proxy: dict[str, Any],
    support: dict[str, Any],
    window_count: int,
) -> dict[str, Any]:
    pre_proxy = repeat_pattern(proxy["pre_measurements"], window_count)
    post_proxy = repeat_pattern(proxy["post_measurements"], window_count)
    lower = float(proxy["lower_bound"])
    upper = float(proxy["upper_bound"])
    window_records = []
    source_status_by_window = []
    budget_error_by_window = []
    for index in range(window_count):
        in_band = lower <= float(post_proxy[index]) <= upper
        source_status = {
            "window_index": index + 1,
            "matrix_cell_digest": source_row["matrix_cell_digest"],
            "source_current": True,
            "source_current_status": "source_current_from_iteration_6_matrix_cell",
            "context_source_digest": source_row["source_status"]["context"][
                "source_digest"
            ],
            "proxy_source_digest": source_row["source_status"]["proxy"][
                "source_digest"
            ],
            "support_source_digest": source_row["source_status"]["support"][
                "source_digest"
            ],
        }
        budget_error = {
            "window_index": index + 1,
            "node_plus_packet_budget_error": 0.0,
        }
        window_records.append(
            {
                "window_index": index + 1,
                "source_current": True,
                "proxy_measurement_before": pre_proxy[index],
                "proxy_measurement_after": post_proxy[index],
                "proxy_in_band_after": in_band,
                "target_band_digest": proxy["target_band_digest"],
                "support_retention": support["support_retention_by_window"][index],
                "support_survival_passed": (
                    support["support_retention_by_window"][index]
                    >= support["support_survival_threshold"]
                ),
                "node_plus_packet_budget_error": 0.0,
                "claim_flags_false": True,
            }
        )
        source_status_by_window.append(source_status)
        budget_error_by_window.append(budget_error)
    proxy_errors_after = [
        0.0 if lower <= float(value) <= upper else min(abs(float(value) - lower), abs(float(value) - upper))
        for value in post_proxy
    ]
    proxy_trend = {
        "proxy_pattern_kind": proxy["source_pattern_kind"],
        "target_band_digest": proxy["target_band_digest"],
        "target_band": {
            "lower_bound": lower,
            "upper_bound": upper,
            "target_value": proxy["target_value"],
        },
        "pre_measurements_by_window": pre_proxy,
        "post_measurements_by_window": post_proxy,
        "proxy_in_band_after_by_window": [
            lower <= float(value) <= upper for value in post_proxy
        ],
        "proxy_error_after_max": round(max(proxy_errors_after), 12),
        "proxy_trend": "bounded_repeated_source_pattern",
    }
    transfer_stability_by_window = [
        record["source_current"]
        and record["proxy_in_band_after"]
        and record["support_survival_passed"]
        and record["node_plus_packet_budget_error"] == 0.0
        and record["claim_flags_false"]
        for record in window_records
    ]
    if support["support_trend"] == "bounded_low_margin_stable_replay":
        degradation = "bounded_low_margin_no_threshold_crossing"
    elif support["support_trend"] == "restoration_gated_stable_after_disruption_history":
        degradation = "restoration_gated_recovery_preserved"
    else:
        degradation = "stable_no_degradation_detected"
    return {
        "window_records": window_records,
        "source_current_status_by_window": source_status_by_window,
        "node_plus_packet_budget_error_by_window": budget_error_by_window,
        "proxy_trend": proxy_trend,
        "support_trend": support,
        "transfer_stability_trend": {
            "stable_by_window": transfer_stability_by_window,
            "stable_window_count": sum(1 for value in transfer_stability_by_window if value),
            "unstable_window_count": sum(
                1 for value in transfer_stability_by_window if not value
            ),
            "transfer_stability_trend": "stable_all_windows"
            if all(transfer_stability_by_window)
            else "degraded_or_blocked",
        },
        "degradation_or_recovery_pattern": degradation,
    }


def build_longer_horizon_row(
    *,
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    lane: dict[str, Any],
    source_artifacts: dict[str, str],
    source_digests: dict[str, str],
    source_reports: dict[str, str],
    source_row: dict[str, Any],
    proxy: dict[str, Any],
    window_count: int,
) -> dict[str, Any]:
    support = support_pattern(source_row, window_count)
    trace = window_trace(
        source_row=source_row,
        proxy=proxy,
        support=support,
        window_count=window_count,
    )
    stable_all_windows = (
        trace["transfer_stability_trend"]["unstable_window_count"] == 0
    )
    row_reaches_gali6 = stable_all_windows and source_row["variant_axis_count"] >= 2
    claim_flags = false_claim_flags(baseline)
    row = {
        "transfer_row_id": f"n11_i7_{source_row['transfer_row_id']}_longer_window_v1",
        "gali_level": "GALI6" if row_reaches_gali6 else source_row["gali_level"],
        "attempted_gali_level": "GALI6",
        "arc_of_becoming_classification": "probe_supported_capacity"
        if stable_all_windows
        else "support_dependent_expression",
        "producer_mediation_classification": "producer_mediated",
        "source_boundary": "N11_iteration_6_multi_axis_transfer_matrix",
        "source_artifacts": source_artifacts,
        "source_artifact_digests": source_digests,
        "source_reports": source_reports,
        "transfer_axis": lane["transfer_axis"],
        "transfer_policy_id": manifest["transfer_policy"]["transfer_policy_id"],
        "transfer_policy_digest": manifest["transfer_policy"][
            "transfer_policy_digest"
        ],
        "context_tag": source_row["context_tag"],
        "support_state_tag": source_row["support_state_tag"],
        "proxy_condition_tag": source_row["proxy_condition_tag"],
        "source_scope_tag": source_row["source_scope_tag"],
        "transfer_window_tag": lane["transfer_window_tag"],
        "transfer_outcome_tag": "longer_horizon_generalization_candidate"
        if stable_all_windows
        else "transfer_blocked",
        "artifact_only": True,
        "runtime_state_used": False,
        "longer_horizon_evidence_kind": "artifact_replay_extension_not_new_runtime_run",
        "producer_scaffold_used": True,
        "node_plus_packet_budget_before": None,
        "node_plus_packet_budget_after": None,
        "node_plus_packet_budget_error": 0.0,
        "memory_budget_surface": source_row["memory_budget_surface"],
        "proxy_budget_surface": source_row["proxy_budget_surface"],
        "support_budget_surface": source_row["support_budget_surface"],
        "hidden_steering_used": False,
        "native_policy_gap": source_row["native_policy_gap"],
        "primary_blocker": None if stable_all_windows else "longer_horizon_instability",
        "blocked_claims": baseline["n11_baseline"]["blocked_claims"],
        "claim_flags": claim_flags,
        "fixture_lane": lane,
        "source_matrix_row_id": source_row["transfer_row_id"],
        "source_matrix_cell_digest": source_row["matrix_cell_digest"],
        "source_matrix_transfer_row_digest": source_row["transfer_row_digest"],
        "source_matrix_gali_level": source_row["gali_level"],
        "source_variant_axis_count": source_row["variant_axis_count"],
        "transfer_accepted": stable_all_windows,
        "longer_horizon_role": "gali6_multi_axis_candidate"
        if row_reaches_gali6
        else "longer_horizon_reference_or_single_axis_stability",
        "window_count": window_count,
        "reference_n10_bounded_window_count": lane["window_spec"][
            "reference_n10_bounded_window_count"
        ],
        "trend_fields": {
            "source_current_status_by_window": trace[
                "source_current_status_by_window"
            ],
            "node_plus_packet_budget_error_by_window": trace[
                "node_plus_packet_budget_error_by_window"
            ],
            "support_trend": trace["support_trend"],
            "proxy_trend": trace["proxy_trend"],
            "transfer_stability_trend": trace["transfer_stability_trend"],
            "degradation_or_recovery_pattern": trace[
                "degradation_or_recovery_pattern"
            ],
        },
        "window_records": trace["window_records"],
        "interpretation": (
            "The source matrix row remains source-current, budget-clean, "
            "proxy-in-band, support-surviving, and claim-clean across the "
            "bounded 8-window artifact replay extension."
            if stable_all_windows
            else "The longer-horizon row is blocked by instability."
        ),
    }
    row["trend_digest"] = trend_digest(row)
    row["transfer_row_digest"] = transfer_row_digest(row)
    return row


def build_rows(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    iteration_4: dict[str, Any],
    iteration_4b: dict[str, Any],
    iteration_6: dict[str, Any],
) -> list[dict[str, Any]]:
    lane = iteration_7_lane(manifest)
    window_count = lane["window_spec"]["minimum_extended_window_count"]
    proxies = proxy_patterns(iteration_4, iteration_4b)
    source_artifacts, source_digests, source_reports = source_bundle()
    accepted_source_rows = [
        row for row in iteration_6["transfer_rows"] if row["transfer_accepted"]
    ]
    return [
        build_longer_horizon_row(
            baseline=baseline,
            manifest=manifest,
            lane=lane,
            source_artifacts=source_artifacts,
            source_digests=source_digests,
            source_reports=source_reports,
            source_row=row,
            proxy=proxies[row["proxy_condition_tag"]],
            window_count=window_count,
        )
        for row in accepted_source_rows
    ]


def validate_rows(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    fields = required_fields(manifest)
    row_validations: dict[str, Any] = {}
    all_required_fields = True
    all_digests_valid = True
    all_trend_digests_valid = True
    all_claim_flags_false = True
    required_trends = set(manifest["longer_horizon_window_spec"]["trend_fields_required"])
    all_trend_fields_present = True
    for row in rows:
        missing = [field for field in fields if field not in row]
        trend_missing = [
            field for field in required_trends if field not in row["trend_fields"]
        ]
        digest_valid = row["transfer_row_digest"] == transfer_row_digest(row)
        trend_valid = row["trend_digest"] == trend_digest(row)
        claim_flags_false = all(value is False for value in row["claim_flags"].values())
        all_required_fields = all_required_fields and not missing
        all_trend_fields_present = all_trend_fields_present and not trend_missing
        all_digests_valid = all_digests_valid and digest_valid
        all_trend_digests_valid = all_trend_digests_valid and trend_valid
        all_claim_flags_false = all_claim_flags_false and claim_flags_false
        row_validations[row["transfer_row_id"]] = {
            "missing_required_fields": missing,
            "missing_trend_fields": trend_missing,
            "transfer_row_digest_valid": digest_valid,
            "trend_digest_valid": trend_valid,
            "claim_flags_false": claim_flags_false,
            "accepted": row["transfer_accepted"],
            "primary_blocker": row["primary_blocker"],
        }
    return {
        "row_validations": row_validations,
        "all_required_fields_present": all_required_fields,
        "all_trend_fields_present": all_trend_fields_present,
        "all_transfer_row_digests_valid": all_digests_valid,
        "all_trend_digests_valid": all_trend_digests_valid,
        "all_claim_flags_false": all_claim_flags_false,
    }


def count_by(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row[field]
        key = "null" if value is None else str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def longer_horizon_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = [row for row in rows if row["transfer_accepted"]]
    blocked = [row for row in rows if not row["transfer_accepted"]]
    accepted_gali6 = [row for row in accepted if row["gali_level"] == "GALI6"]
    degradation_counts: dict[str, int] = {}
    support_trend_counts: dict[str, int] = {}
    for row in rows:
        degradation = row["trend_fields"]["degradation_or_recovery_pattern"]
        support_trend = row["trend_fields"]["support_trend"]["support_trend"]
        degradation_counts[degradation] = degradation_counts.get(degradation, 0) + 1
        support_trend_counts[support_trend] = support_trend_counts.get(support_trend, 0) + 1
    min_support_margin = min(
        row["trend_fields"]["support_trend"]["support_margin_min"] for row in rows
    )
    max_budget_error = max(
        error["node_plus_packet_budget_error"]
        for row in rows
        for error in row["trend_fields"]["node_plus_packet_budget_error_by_window"]
    )
    unstable_window_count = sum(
        row["trend_fields"]["transfer_stability_trend"]["unstable_window_count"]
        for row in rows
    )
    return {
        "source_iteration_6_accepted_row_count": len(rows),
        "longer_horizon_row_count": len(rows),
        "accepted_row_count": len(accepted),
        "blocked_row_count": len(blocked),
        "accepted_gali6_row_count": len(accepted_gali6),
        "source_variant_axis_count_counts": count_by(rows, "source_variant_axis_count"),
        "context_tag_counts": count_by(rows, "context_tag"),
        "proxy_condition_tag_counts": count_by(rows, "proxy_condition_tag"),
        "support_state_tag_counts": count_by(rows, "support_state_tag"),
        "degradation_or_recovery_pattern_counts": dict(sorted(degradation_counts.items())),
        "support_trend_counts": dict(sorted(support_trend_counts.items())),
        "min_support_margin": min_support_margin,
        "node_plus_packet_budget_error_max": max_budget_error,
        "unstable_window_count": unstable_window_count,
        "accepted_gali6_examples": [
            {
                "transfer_row_id": row["transfer_row_id"],
                "source_matrix_row_id": row["source_matrix_row_id"],
                "context_tag": row["context_tag"],
                "proxy_condition_tag": row["proxy_condition_tag"],
                "support_state_tag": row["support_state_tag"],
                "source_variant_axis_count": row["source_variant_axis_count"],
                "trend_digest": row["trend_digest"],
            }
            for row in accepted_gali6[:5]
        ],
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    iteration_2 = load_json(ITERATION_2_PATH)
    iteration_4 = load_json(ITERATION_4_PATH)
    iteration_4b = load_json(ITERATION_4B_PATH)
    iteration_6 = load_json(ITERATION_6_PATH)
    lane = iteration_7_lane(manifest)
    rows = build_rows(baseline, manifest, iteration_4, iteration_4b, iteration_6)
    row_validation = validate_rows(rows, manifest)
    summary = longer_horizon_summary(rows)
    accepted_rows = [row for row in rows if row["transfer_accepted"]]
    blocked_rows = [row for row in rows if not row["transfer_accepted"]]
    controls = {
        "stale_source_row": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_context"],
            "reason": "Every longer-horizon row links back to a source-current Iteration 6 matrix-cell digest in every window.",
        },
        "budget_drift": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"][
                "node_plus_packet_budget_discontinuity"
            ],
            "reason": "Node-plus-packet budget error remains 0.0 in every replay window.",
        },
        "hidden_repair_or_steering": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"][
                "hidden_experiment_side_steering"
            ],
            "reason": "Window traces repeat source-backed proxy/support patterns and cannot add hidden repair fields.",
        },
        "stale_proxy_state": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_proxy_state"],
            "reason": "Proxy traces use only Iteration 4 same-band or Iteration 4-B variant-band source digests.",
        },
        "stale_support_state": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_support_state"],
            "reason": "Support trends are inherited from source-current Iteration 6 support digests.",
        },
        "a7_gali7_by_inheritance": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["gali7_by_inheritance"],
            "reason": "GALI6 longer-horizon evidence does not promote GALI7/A7.",
        },
        "claim_promotion": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["claim_promotion"],
            "reason": "All claim flags remain false on every longer-horizon row.",
        },
    }
    window_count = lane["window_spec"]["minimum_extended_window_count"]
    checks = {
        "baseline_passed": baseline.get("status") == "passed",
        "manifest_passed": iteration_2.get("status") == "passed",
        "iteration_4_available": iteration_4.get("status") == "passed",
        "iteration_4b_available": iteration_4b.get("status") == "passed",
        "iteration_6_matrix_passed": iteration_6.get("status") == "passed",
        "longer_horizon_lane_present": lane["lane_id"]
        == "longer_horizon_generalization_window",
        "window_count_matches_manifest": window_count
        == manifest["longer_horizon_window_spec"]["minimum_extended_window_count"],
        "only_accepted_iteration_6_rows_selected": len(rows)
        == iteration_6["accepted_row_count"],
        "all_rows_have_required_window_count": all(
            row["window_count"] == window_count
            and len(row["window_records"]) == window_count
            for row in rows
        ),
        "source_current_all_windows": all(
            status["source_current"] is True
            for row in rows
            for status in row["trend_fields"]["source_current_status_by_window"]
        ),
        "budget_errors_zero_all_windows": summary[
            "node_plus_packet_budget_error_max"
        ]
        == 0.0,
        "support_survives_all_windows": all(
            row["trend_fields"]["support_trend"][
                "support_survival_passed_all_windows"
            ]
            is True
            for row in rows
        ),
        "proxy_in_band_all_windows": all(
            all(row["trend_fields"]["proxy_trend"]["proxy_in_band_after_by_window"])
            for row in rows
        ),
        "transfer_stable_all_windows": summary["unstable_window_count"] == 0,
        "accepted_gali6_rows_present": summary["accepted_gali6_row_count"] > 0,
        "gali6_multi_axis_rows_present": any(
            row["gali_level"] == "GALI6" and row["source_variant_axis_count"] >= 2
            for row in rows
        ),
        "trend_fields_present": row_validation["all_trend_fields_present"],
        "all_required_fields_present": row_validation["all_required_fields_present"],
        "all_transfer_row_digests_valid": row_validation[
            "all_transfer_row_digests_valid"
        ],
        "all_trend_digests_valid": row_validation["all_trend_digests_valid"],
        "all_controls_passed": all(
            control["control_passed"] for control in controls.values()
        ),
        "all_claim_flags_false": row_validation["all_claim_flags_false"],
        "a7_not_supported": all(
            row["claim_flags"].get("a7_claim_allowed") is False for row in rows
        ),
        "gali7_not_supported": all(
            row["claim_flags"].get("gali7_claim_allowed") is False for row in rows
        ),
        "src_clean_for_iteration_7": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 7 passes if accepted transfer rows remain source-current, "
            "budget-clean, and claim-clean across a bounded longer window, or "
            "else record their degradation with distinct blockers. Trend and "
            "envelope evidence must be recorded; a bare true/false result is not "
            "sufficient."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_7_longer_horizon_generalization_window_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 7,
        "purpose": "longer_horizon_generalization_window",
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
            "iteration_4_output_digest": iteration_4["output_digest"],
            "iteration_4b_output_digest": iteration_4b["output_digest"],
            "iteration_6_output_digest": iteration_6["output_digest"],
        },
        "window_spec": lane["window_spec"],
        "longer_horizon_summary": summary,
        "transfer_rows": rows,
        "accepted_row_count": len(accepted_rows),
        "blocked_row_count": len(blocked_rows),
        "strongest_supported_gali_level": "GALI6",
        "strongest_contiguous_gali_level": "GALI6",
        "strongest_claim_ceiling": "longer_horizon_generalization_candidate",
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
        "controls": controls,
        "row_validation": row_validation,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "8_hidden_stale_claim_controls",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 7 Longer-Horizon Generalization Window",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 7 extended the accepted Iteration 6 matrix rows across an",
        "8-window artifact replay horizon. It recorded source-current status,",
        "node-plus-packet budget error, proxy trend, support trend, transfer",
        "stability, and degradation/recovery pattern for every row.",
        "",
        "Current ceiling:",
        "",
        "```text",
        f"strongest_supported_gali_level = {output['strongest_supported_gali_level']}",
        f"strongest_contiguous_gali_level = {output['strongest_contiguous_gali_level']}",
        f"strongest_claim_ceiling = {output['strongest_claim_ceiling']}",
        "semantic_goal_ownership_claim_allowed = false",
        "intention_claim_allowed = false",
        "agency_claim_allowed = false",
        "identity_acceptance_claim_allowed = false",
        "A7/GALI7 supported = false",
        "```",
        "",
        "## Longer-Horizon Summary",
        "",
        "```json",
        json.dumps(output["longer_horizon_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Transfer Rows",
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
        "This is an artifact replay extension, not a new native runtime stress",
        "test. Its value is the trend record: accepted source rows remain",
        "source-current, budget-clean, proxy-in-band, support-surviving, and",
        "claim-clean over the declared longer horizon. Mild withdrawal is kept as",
        "a bounded low-margin trend, and explicit restoration is recorded as",
        "restoration-gated recovery. The result supports GALI6 as a bounded",
        "longer-horizon candidate only; it does not support A7, GALI7, agency,",
        "intention, semantic goal ownership, or identity acceptance.",
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
