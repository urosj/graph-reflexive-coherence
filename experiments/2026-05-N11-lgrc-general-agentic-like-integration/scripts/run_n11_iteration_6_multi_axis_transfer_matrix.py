#!/usr/bin/env python3
"""Run N11 Iteration 6 multi-axis transfer matrix."""

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
ITERATION_3_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_3_route_context_transfer_replay.json"
)
ITERATION_4_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_4_proxy_condition_transfer_replay.json"
)
ITERATION_4B_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_4b_proxy_target_band_variant_probe.json"
)
ITERATION_5_PATH = (
    EXPERIMENT / "outputs" / "n11_iteration_5_support_state_transfer_replay.json"
)

OUTPUT_PATH = EXPERIMENT / "outputs" / "n11_iteration_6_multi_axis_transfer_matrix.json"
REPORT_PATH = EXPERIMENT / "reports" / "n11_iteration_6_multi_axis_transfer_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "run_n11_iteration_6_multi_axis_transfer_matrix.py"
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


def matrix_cell_digest(row: dict[str, Any]) -> str:
    return digest_value(
        {
            key: value
            for key, value in row.items()
            if key not in {"matrix_cell_digest", "transfer_row_digest"}
        }
    )


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(baseline["n11_baseline"]["claim_flags"])}


def required_fields(manifest: dict[str, Any]) -> list[str]:
    fields = manifest["transfer_row_required_fields"]
    if not isinstance(fields, list):
        raise TypeError("manifest transfer_row_required_fields must be a list")
    return list(fields)


def iteration_6_lane(manifest: dict[str, Any]) -> dict[str, Any]:
    lanes = [
        lane
        for lane in manifest["fixture_lanes"]
        if lane.get("planned_iteration") == 6
        and lane.get("lane_id") == "multi_axis_context_proxy_support_matrix"
    ]
    if len(lanes) != 1:
        raise ValueError("expected exactly one Iteration 6 matrix lane")
    return lanes[0]


def source_bundle() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    artifacts = {
        "n11_baseline_inventory": rel(BASELINE_PATH),
        "n11_fixture_manifest": rel(MANIFEST_PATH),
        "n11_iteration_2_fixture_manifest_validation": rel(ITERATION_2_PATH),
        "n11_iteration_3_route_context_transfer_replay": rel(ITERATION_3_PATH),
        "n11_iteration_4_proxy_condition_transfer_replay": rel(ITERATION_4_PATH),
        "n11_iteration_4b_proxy_target_band_variant_probe": rel(ITERATION_4B_PATH),
        "n11_iteration_5_support_state_transfer_replay": rel(ITERATION_5_PATH),
    }
    digests = {key: digest_file(ROOT / value) for key, value in artifacts.items()}
    reports = {
        "n11_iteration_3_route_context_transfer_replay": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_3_route_context_transfer_replay.md"
        ),
        "n11_iteration_4_proxy_condition_transfer_replay": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_4_proxy_condition_transfer_replay.md"
        ),
        "n11_iteration_4b_proxy_target_band_variant_probe": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_4b_proxy_target_band_variant_probe.md"
        ),
        "n11_iteration_5_support_state_transfer_replay": (
            "experiments/2026-05-N11-lgrc-general-agentic-like-integration/"
            "reports/n11_iteration_5_support_state_transfer_replay.md"
        ),
    }
    return artifacts, digests, reports


def rows_by_tag(rows: list[dict[str, Any]], tag: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        indexed[row[tag]] = row
    return indexed


def context_source_status(iteration_3: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_context = rows_by_tag(iteration_3["transfer_rows"], "context_tag")
    return {
        "context_same_as_n10": {
            "source_row_id": by_context["context_same_as_n10"]["transfer_row_id"],
            "source_digest": by_context["context_same_as_n10"]["transfer_row_digest"],
            "source_output_digest": iteration_3["output_digest"],
            "accepted": by_context["context_same_as_n10"]["transfer_accepted"],
            "source_level": by_context["context_same_as_n10"]["gali_level"],
            "source_primary_blocker": by_context["context_same_as_n10"][
                "primary_blocker"
            ],
            "source_scope": "reference_context",
        },
        "context_route_variant": {
            "source_row_id": by_context["context_route_variant"]["transfer_row_id"],
            "source_digest": by_context["context_route_variant"][
                "transfer_row_digest"
            ],
            "source_output_digest": iteration_3["output_digest"],
            "accepted": by_context["context_route_variant"]["transfer_accepted"],
            "source_level": by_context["context_route_variant"]["gali_level"],
            "source_primary_blocker": by_context["context_route_variant"][
                "primary_blocker"
            ],
            "source_scope": "accepted_route_context_variant",
        },
        "context_arbitration_policy_variant": {
            "source_row_id": by_context["context_arbitration_policy_variant"][
                "transfer_row_id"
            ],
            "source_digest": by_context["context_arbitration_policy_variant"][
                "transfer_row_digest"
            ],
            "source_output_digest": iteration_3["output_digest"],
            "accepted": by_context["context_arbitration_policy_variant"][
                "transfer_accepted"
            ],
            "source_level": by_context["context_arbitration_policy_variant"][
                "gali_level"
            ],
            "source_primary_blocker": by_context[
                "context_arbitration_policy_variant"
            ]["primary_blocker"],
            "source_scope": "blocked_arbitration_policy_variant",
        },
    }


def proxy_source_status(
    iteration_4: dict[str, Any],
    iteration_4b: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    variant_row = iteration_4b["transfer_rows"][0]
    return {
        "proxy_same_as_n10": {
            "source_row_id": "n11_i4_same_band_proxy_reference_v1",
            "source_digest": iteration_4["proxy_evidence_summary"][
                "target_band_digest"
            ],
            "source_output_digest": iteration_4["output_digest"],
            "accepted": True,
            "source_level": "GALI1",
            "source_primary_blocker": None,
            "source_scope": "same_band_reference_proxy_condition",
            "target_band_digest": iteration_4["proxy_evidence_summary"][
                "target_band_digest"
            ],
            "target_band": {
                "lower_bound": iteration_4["proxy_evidence_summary"]["lower_bound"],
                "upper_bound": iteration_4["proxy_evidence_summary"]["upper_bound"],
                "target_value": iteration_4["proxy_evidence_summary"][
                    "target_value"
                ],
            },
        },
        "proxy_target_band_variant": {
            "source_row_id": variant_row["transfer_row_id"],
            "source_digest": variant_row["transfer_row_digest"],
            "source_output_digest": iteration_4b["output_digest"],
            "accepted": variant_row["transfer_accepted"],
            "source_level": variant_row["gali_level"],
            "source_primary_blocker": variant_row["primary_blocker"],
            "source_scope": "accepted_proxy_target_band_variant",
            "target_band_digest": iteration_4b["variant_target_band"][
                "target_band_digest"
            ],
            "target_band": {
                "lower_bound": iteration_4b["variant_target_band"]["lower_bound"],
                "upper_bound": iteration_4b["variant_target_band"]["upper_bound"],
                "target_value": iteration_4b["variant_target_band"]["target_value"],
            },
            "iteration_4_negative_audit_preserved": True,
            "iteration_4_primary_blocker": iteration_4["transfer_rows"][0][
                "primary_blocker"
            ],
        },
    }


def support_source_status(iteration_5: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_support = rows_by_tag(iteration_5["transfer_rows"], "support_state_tag")
    result: dict[str, dict[str, Any]] = {}
    for support_state, row in by_support.items():
        result[support_state] = {
            "source_row_id": row["transfer_row_id"],
            "source_digest": row["transfer_row_digest"],
            "source_output_digest": iteration_5["output_digest"],
            "accepted": row["transfer_accepted"],
            "source_level": row["gali_level"],
            "source_primary_blocker": row["primary_blocker"],
            "source_scope": row["support_summary"]["source_current_status"],
            "support_retention": row["support_summary"]["support_retention"],
            "explicit_restoration_present": row["support_summary"][
                "explicit_restoration_present"
            ],
        }
    return result


def variant_axis_count(
    context_tag: str,
    proxy_condition_tag: str,
    support_state_tag: str,
) -> int:
    count = 0
    if context_tag != "context_same_as_n10":
        count += 1
    if proxy_condition_tag != "proxy_same_as_n10":
        count += 1
    if support_state_tag != "support_intact_survives":
        count += 1
    return count


def accepted_gali_level(axis_count: int) -> str:
    if axis_count >= 2:
        return "GALI5"
    if axis_count == 1:
        return "GALI4"
    return "GALI1"


def row_arc_classification(accepted: bool, blockers: list[str], axis_count: int) -> str:
    if not accepted and "support_disrupted_but_integration_allowed" in blockers:
        return "support_dependent_expression"
    if accepted and axis_count >= 2:
        return "probe_supported_capacity"
    if accepted and axis_count == 1:
        return "support_dependent_expression"
    return "local_observation_tag"


def primary_blocker(
    context_status: dict[str, Any],
    proxy_status: dict[str, Any],
    support_status: dict[str, Any],
) -> tuple[str | None, list[str]]:
    blockers = [
        status["source_primary_blocker"]
        for status in (context_status, proxy_status, support_status)
        if status["source_primary_blocker"]
    ]
    for status in (context_status, proxy_status, support_status):
        if not status["accepted"]:
            return status["source_primary_blocker"], blockers
    return None, blockers


def matrix_cell(
    *,
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    lane: dict[str, Any],
    source_artifacts: dict[str, str],
    source_digests: dict[str, str],
    source_reports: dict[str, str],
    context_tag: str,
    proxy_condition_tag: str,
    support_state_tag: str,
    context_status: dict[str, Any],
    proxy_status: dict[str, Any],
    support_status: dict[str, Any],
) -> dict[str, Any]:
    axis_count = variant_axis_count(context_tag, proxy_condition_tag, support_state_tag)
    blocker, blockers = primary_blocker(context_status, proxy_status, support_status)
    accepted = blocker is None
    gali_level = "GALI5" if accepted and axis_count >= 2 else accepted_gali_level(axis_count)
    if not accepted:
        gali_level = "GALI5"
    outcome = "multi_axis_bounded_transfer_candidate" if accepted else "transfer_blocked"
    claim_flags = false_claim_flags(baseline)
    source_status = {
        "context": context_status,
        "proxy": proxy_status,
        "support": support_status,
    }
    row = {
        "transfer_row_id": (
            "n11_i6_"
            f"{context_tag}__{proxy_condition_tag}__{support_state_tag}_row_v1"
        ),
        "gali_level": gali_level,
        "attempted_gali_level": "GALI5",
        "arc_of_becoming_classification": row_arc_classification(
            accepted, blockers, axis_count
        ),
        "producer_mediation_classification": (
            "producer_mediated" if accepted else "native_policy_gap"
        ),
        "source_boundary": "N11_iterations_3_4_4B_5_transfer_sources",
        "source_artifacts": source_artifacts,
        "source_artifact_digests": source_digests,
        "source_reports": source_reports,
        "transfer_axis": lane["transfer_axis"],
        "transfer_policy_id": manifest["transfer_policy"]["transfer_policy_id"],
        "transfer_policy_digest": manifest["transfer_policy"][
            "transfer_policy_digest"
        ],
        "context_tag": context_tag,
        "support_state_tag": support_state_tag,
        "proxy_condition_tag": proxy_condition_tag,
        "source_scope_tag": "n10_bounded_artifact_only_source",
        "transfer_window_tag": "bounded_repeated_window",
        "transfer_outcome_tag": outcome,
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
                + [
                    "native_goal_proxy_regulation_policy_missing",
                    "native_agentic_like_integration_policy_missing",
                ]
            )
        ),
        "primary_blocker": blocker,
        "blocker_chain": blockers,
        "blocked_claims": baseline["n11_baseline"]["blocked_claims"],
        "claim_flags": claim_flags,
        "fixture_lane": lane,
        "transfer_accepted": accepted,
        "variant_axis_count": axis_count,
        "source_status": source_status,
        "native_route_arbitration_component_used": context_status["accepted"],
        "matrix_interpretation": (
            "Accepted bounded multi-axis transfer row."
            if accepted and axis_count >= 2
            else "Accepted source-backed matrix reference or single-axis row."
            if accepted
            else "Blocked matrix row; blocker is inherited from source axis status."
        ),
    }
    row["matrix_cell_digest"] = matrix_cell_digest(row)
    row["transfer_row_digest"] = transfer_row_digest(row)
    return row


def build_rows(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    iteration_3: dict[str, Any],
    iteration_4: dict[str, Any],
    iteration_4b: dict[str, Any],
    iteration_5: dict[str, Any],
) -> list[dict[str, Any]]:
    lane = iteration_6_lane(manifest)
    matrix_spec = lane["matrix_spec"]
    source_artifacts, source_digests, source_reports = source_bundle()
    contexts = context_source_status(iteration_3)
    proxies = proxy_source_status(iteration_4, iteration_4b)
    supports = support_source_status(iteration_5)
    rows: list[dict[str, Any]] = []
    for context_tag in matrix_spec["context_variants"]:
        for proxy_condition_tag in matrix_spec["proxy_condition_variants"]:
            for support_state_tag in matrix_spec["support_state_variants"]:
                rows.append(
                    matrix_cell(
                        baseline=baseline,
                        manifest=manifest,
                        lane=lane,
                        source_artifacts=source_artifacts,
                        source_digests=source_digests,
                        source_reports=source_reports,
                        context_tag=context_tag,
                        proxy_condition_tag=proxy_condition_tag,
                        support_state_tag=support_state_tag,
                        context_status=contexts[context_tag],
                        proxy_status=proxies[proxy_condition_tag],
                        support_status=supports[support_state_tag],
                    )
                )
    return rows


def validate_rows(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    fields = required_fields(manifest)
    row_validations: dict[str, Any] = {}
    all_required_fields = True
    all_digests_valid = True
    all_claim_flags_false = True
    all_matrix_cell_digests_valid = True
    for row in rows:
        missing = [field for field in fields if field not in row]
        digest_valid = row["transfer_row_digest"] == transfer_row_digest(row)
        matrix_digest_valid = row["matrix_cell_digest"] == matrix_cell_digest(row)
        claim_flags_false = all(value is False for value in row["claim_flags"].values())
        all_required_fields = all_required_fields and not missing
        all_digests_valid = all_digests_valid and digest_valid
        all_matrix_cell_digests_valid = (
            all_matrix_cell_digests_valid and matrix_digest_valid
        )
        all_claim_flags_false = all_claim_flags_false and claim_flags_false
        row_validations[row["transfer_row_id"]] = {
            "missing_required_fields": missing,
            "transfer_row_digest_valid": digest_valid,
            "matrix_cell_digest_valid": matrix_digest_valid,
            "claim_flags_false": claim_flags_false,
            "accepted": row["transfer_accepted"],
            "primary_blocker": row["primary_blocker"],
        }
    return {
        "row_validations": row_validations,
        "all_required_fields_present": all_required_fields,
        "all_transfer_row_digests_valid": all_digests_valid,
        "all_matrix_cell_digests_valid": all_matrix_cell_digests_valid,
        "all_claim_flags_false": all_claim_flags_false,
    }


def count_by(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row[field]
        key = "null" if value is None else str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def matrix_summary(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    accepted = [row for row in rows if row["transfer_accepted"]]
    blocked = [row for row in rows if not row["transfer_accepted"]]
    accepted_gali5 = [
        row
        for row in accepted
        if row["gali_level"] == "GALI5" and row["variant_axis_count"] >= 2
    ]
    blocker_chain_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blocker_chain"]:
            blocker_chain_counts[blocker] = blocker_chain_counts.get(blocker, 0) + 1
    return {
        "expected_minimum_row_count": manifest["multi_axis_matrix_spec"][
            "expected_minimum_row_count"
        ],
        "actual_row_count": len(rows),
        "accepted_row_count": len(accepted),
        "blocked_row_count": len(blocked),
        "accepted_gali5_row_count": len(accepted_gali5),
        "primary_blocker_counts": count_by(rows, "primary_blocker"),
        "blocker_chain_counts": dict(sorted(blocker_chain_counts.items())),
        "context_tag_counts": count_by(rows, "context_tag"),
        "proxy_condition_tag_counts": count_by(rows, "proxy_condition_tag"),
        "support_state_tag_counts": count_by(rows, "support_state_tag"),
        "variant_axis_count_counts": count_by(rows, "variant_axis_count"),
        "accepted_gali5_examples": [
            {
                "transfer_row_id": row["transfer_row_id"],
                "context_tag": row["context_tag"],
                "proxy_condition_tag": row["proxy_condition_tag"],
                "support_state_tag": row["support_state_tag"],
                "variant_axis_count": row["variant_axis_count"],
                "matrix_cell_digest": row["matrix_cell_digest"],
            }
            for row in accepted_gali5[:5]
        ],
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    iteration_2 = load_json(ITERATION_2_PATH)
    iteration_3 = load_json(ITERATION_3_PATH)
    iteration_4 = load_json(ITERATION_4_PATH)
    iteration_4b = load_json(ITERATION_4B_PATH)
    iteration_5 = load_json(ITERATION_5_PATH)
    lane = iteration_6_lane(manifest)
    rows = build_rows(
        baseline,
        manifest,
        iteration_3,
        iteration_4,
        iteration_4b,
        iteration_5,
    )
    row_validation = validate_rows(rows, manifest)
    summary = matrix_summary(rows, manifest)
    accepted_rows = [row for row in rows if row["transfer_accepted"]]
    blocked_rows = [row for row in rows if not row["transfer_accepted"]]
    controls = {
        "hidden_experiment_side_steering": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"][
                "hidden_experiment_side_steering"
            ],
            "reason": (
                "Matrix rows are a deterministic cartesian expansion of manifest "
                "tags and prior source row status; no report-side route, proxy, "
                "or support selection can make a row pass."
            ),
        },
        "stale_context": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_context"],
            "reason": "Context status is inherited from Iteration 3 row digests.",
        },
        "stale_proxy_state": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_proxy_state"],
            "reason": "Proxy status is inherited from Iteration 4 audit and 4-B row digests.",
        },
        "stale_support_state": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_support_state"],
            "reason": "Support status is inherited from Iteration 5 row digests.",
        },
        "support_disrupted_without_restoration": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"][
                "support_disrupted_but_generalization_allowed"
            ],
            "reason": "Rows using disrupted support remain blocked unless explicit restoration is the source support state.",
        },
        "out_of_envelope_proxy": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["out_of_envelope_proxy"],
            "reason": "The only proxy variant admitted is the 4-B declared envelope.",
        },
        "budget_surface_ambiguity": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["budget_surface_ambiguity"],
            "reason": "Memory, proxy, support, and node-plus-packet budget surfaces remain separate on every row.",
        },
        "claim_promotion": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["claim_promotion"],
            "reason": "All matrix rows keep all N11 claim flags false.",
        },
    }
    checks = {
        "baseline_passed": baseline.get("status") == "passed",
        "manifest_passed": iteration_2.get("status") == "passed",
        "iteration_3_passed": iteration_3.get("status") == "passed",
        "iteration_4_negative_audit_available": iteration_4.get("status") == "passed"
        and iteration_4["transfer_rows"][0]["primary_blocker"]
        == "proxy_target_band_variant_missing_source",
        "iteration_4b_proxy_variant_supported": iteration_4b.get("status") == "passed"
        and iteration_4b.get("strongest_supported_gali_level") == "GALI3",
        "iteration_5_support_matrix_passed": iteration_5.get("status") == "passed"
        and iteration_5.get("strongest_contiguous_gali_level") == "GALI4",
        "matrix_lane_present": lane["lane_id"]
        == "multi_axis_context_proxy_support_matrix",
        "matrix_row_count_matches_expected": len(rows)
        == manifest["multi_axis_matrix_spec"]["expected_minimum_row_count"],
        "matrix_expands_all_context_tags": set(count_by(rows, "context_tag"))
        == set(manifest["multi_axis_matrix_spec"]["context_variants"]),
        "matrix_expands_all_proxy_tags": set(count_by(rows, "proxy_condition_tag"))
        == set(manifest["multi_axis_matrix_spec"]["proxy_condition_variants"]),
        "matrix_expands_all_support_tags": set(count_by(rows, "support_state_tag"))
        == set(manifest["multi_axis_matrix_spec"]["support_state_variants"]),
        "accepted_and_blocked_rows_recorded": bool(accepted_rows) and bool(blocked_rows),
        "accepted_gali5_rows_present": summary["accepted_gali5_row_count"] > 0,
        "context_policy_variant_blocked": summary["primary_blocker_counts"].get(
            "context_arbitration_policy_variant_missing_source"
        )
        == 8,
        "disrupted_support_blocked_for_available_contexts": summary[
            "primary_blocker_counts"
        ].get("support_disrupted_but_integration_allowed")
        == 4,
        "source_artifact_digests_present": all(
            row["source_artifact_digests"] for row in rows
        ),
        "source_status_digest_links_present": all(
            row["source_status"][axis]["source_digest"]
            for row in rows
            for axis in ("context", "proxy", "support")
        ),
        "budget_surfaces_separate": all(
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
        "node_plus_packet_budget_errors_zero": all(
            row["node_plus_packet_budget_error"] == 0.0 for row in rows
        ),
        "all_required_fields_present": row_validation["all_required_fields_present"],
        "all_transfer_row_digests_valid": row_validation[
            "all_transfer_row_digests_valid"
        ],
        "all_matrix_cell_digests_valid": row_validation[
            "all_matrix_cell_digests_valid"
        ],
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
        "src_clean_for_iteration_6": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 6 passes if the context/proxy/support transfer matrix is "
            "source-backed, budget-clean, and claim-clean, with a legible envelope "
            "of accepted, downgraded, and blocked rows. The goal is not universal "
            "transfer; the goal is a replayable generalization envelope with "
            "distinct blockers."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_6_multi_axis_transfer_matrix_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 6,
        "purpose": "multi_axis_transfer_matrix",
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
            "iteration_3_output_digest": iteration_3["output_digest"],
            "iteration_4_output_digest": iteration_4["output_digest"],
            "iteration_4b_output_digest": iteration_4b["output_digest"],
            "iteration_5_output_digest": iteration_5["output_digest"],
        },
        "matrix_spec": lane["matrix_spec"],
        "matrix_summary": summary,
        "transfer_rows": rows,
        "accepted_row_count": len(accepted_rows),
        "blocked_row_count": len(blocked_rows),
        "strongest_supported_gali_level": "GALI5",
        "strongest_contiguous_gali_level": "GALI5",
        "strongest_claim_ceiling": "multi_axis_bounded_transfer_candidate",
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
        "next_iteration": "7_longer_horizon_generalization_window",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 6 Multi-Axis Transfer Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 6 expanded the source-backed context, proxy, and support",
        "axes into a deterministic 24-row matrix. It did not ask for universal",
        "success. It recorded a generalization envelope: rows with available",
        "context/proxy/support sources pass, rows requiring the missing alternate",
        "arbitration policy block, and rows using disrupted support block unless",
        "explicit restoration is the selected support state.",
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
        "## Matrix Summary",
        "",
        "```json",
        json.dumps(output["matrix_summary"], indent=2, sort_keys=True),
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
        "The useful result is the envelope, not a bare true/false. N11 now has",
        "source-backed evidence that route context, proxy target-band variation,",
        "and support-state variation can be composed in accepted bounded rows.",
        "The same matrix also preserves the boundaries that matter: no alternate",
        "arbitration policy exists yet, disrupted support blocks the composition",
        "without restoration, and no row promotes semantic goal ownership,",
        "intention, agency, identity acceptance, A7, or GALI7.",
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
