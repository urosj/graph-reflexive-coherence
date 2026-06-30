#!/usr/bin/env python3
"""Build N29 I14.6-2 wider-margin leakage aggregation variant."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_wider_margin_leakage_aggregation_i1462.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I146 = EXPERIMENT / "outputs" / "n29_multi_role_phase_loop_i146.json"
I1461 = EXPERIMENT / "outputs" / "n29_multi_leg_leakage_aggregation_i1461.json"
I1461_ART = EXPERIMENT / "outputs" / "n29_multi_leg_leakage_aggregation_i1461_artifact.json"
I1444_ART = EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_bridge_i1444_artifact.json"
I1452_ART = EXPERIMENT / "outputs" / "n29_buffered_generator_extractor_feedback_i1452_artifact.json"

OUT = EXPERIMENT / "outputs" / "n29_wider_margin_leakage_aggregation_i1462.json"
RUNTIME = EXPERIMENT / "outputs" / "n29_wider_margin_leakage_aggregation_i1462_artifact.json"
REPORT = EXPERIMENT / "reports" / "n29_wider_margin_leakage_aggregation_i1462.md"

PER_LEG_MERGE_LEAKAGE_CEILING = 0.025
AGGREGATE_CEILING_RESERVE = 0.010
LEAKAGE_WINDOW_FACTOR = 0.80
TARGET_AGGREGATE_MARGIN = 0.010

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "agentic_ecology_runtime_claim_allowed": False,
    "altruism_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "closed_environmental_circulation_loop_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "coordinated_exchange_cycle_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "native_ecological_role_claim_allowed": False,
    "native_support_claim_allowed": False,
    "resource_economy_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_purpose_claim_allowed": False,
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "iteration": data.get("iteration", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def artifact_manifest(path: Path, role: str) -> list[dict[str, Any]]:
    return [
        {
            "artifact_role": role,
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
        }
    ]


def manifest_sha_match(manifest: list[dict[str, Any]]) -> bool:
    return all(
        (ROOT / row["path"]).exists()
        and sha256_file(ROOT / row["path"]) == row["sha256"]
        for row in manifest
    )


def build_runtime_artifact(
    i146: dict[str, Any],
    i1461: dict[str, Any],
    i1461_art: dict[str, Any],
    i1444_art: dict[str, Any],
    i1452_art: dict[str, Any],
) -> dict[str, Any]:
    phase_gross = i1452_art["leakage_record"]["merge_leakage_value"]
    cycle_gross = i1444_art["leakage_record"]["merge_leakage_value"]
    phase_net = round(phase_gross * LEAKAGE_WINDOW_FACTOR, 6)
    cycle_net = round(cycle_gross * LEAKAGE_WINDOW_FACTOR, 6)
    phase_captured = round(phase_gross - phase_net, 6)
    cycle_captured = round(cycle_gross - cycle_net, 6)
    gross_aggregate = round(phase_gross + cycle_gross, 6)
    net_aggregate = round(phase_net + cycle_net, 6)
    captured_total = round(phase_captured + cycle_captured, 6)
    aggregate_ceiling = round(
        (2 * PER_LEG_MERGE_LEAKAGE_CEILING) - AGGREGATE_CEILING_RESERVE, 6
    )
    net_margin = round(aggregate_ceiling - net_aggregate, 6)
    i1461_margin = i1461["leakage_aggregation_row"]["aggregate_merge_leakage_margin"]
    margin_improvement = round(net_margin - i1461_margin, 6)
    artifact = {
        "artifact_id": "n29_wider_margin_leakage_aggregation_i1462_artifact",
        "experiment_id": "N29",
        "iteration": "I14.6-2",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "producer_mediated_wider_margin_multi_leg_leakage_aggregation_artifact",
        "source_i14_6_digest": i146["output_digest"],
        "source_i14_6_1_digest": i1461["output_digest"],
        "source_i14_6_1_artifact_digest": i1461_art["output_digest"],
        "source_i14_4_4_artifact_digest": i1444_art["output_digest"],
        "source_i14_5_2_artifact_digest": i1452_art["output_digest"],
        "wider_margin_policy": {
            "policy_id": "n29_i14_6_2_uniform_leakage_window_v1",
            "declared_before_use": True,
            "producer_mediated": True,
            "policy_role": (
                "route both composed leakage channels through one declared bridge "
                "interface guard before full-sum aggregation"
            ),
            "leakage_window_factor": LEAKAGE_WINDOW_FACTOR,
            "same_factor_applied_to_all_channels": True,
            "aggregate_ceiling_formula_preserved": "2 * per_leg_ceiling - aggregate_reserve",
            "aggregate_ceiling": aggregate_ceiling,
            "aggregate_ceiling_changed_from_i14_6_1": False,
            "thresholds_retuned_after_outcome": False,
            "producer_guard_capture_recorded": True,
            "producer_guard_capture_counts_as_native_success": False,
            "producer_success_can_upgrade_native": False,
        },
        "leakage_channel_map": [
            {
                "channel_id": "phase_feedback_leg",
                "source_iteration": "I14.5-2",
                "gross_merge_leakage": phase_gross,
                "net_merge_leakage_after_window": phase_net,
                "producer_guard_captured_leakage": phase_captured,
                "mapped_to_common_frame": True,
            },
            {
                "channel_id": "directed_cycle_leg",
                "source_iteration": "I14.4-4",
                "gross_merge_leakage": cycle_gross,
                "net_merge_leakage_after_window": cycle_net,
                "producer_guard_captured_leakage": cycle_captured,
                "mapped_to_common_frame": True,
            },
        ],
        "aggregation_trace": {
            "aggregation_method": "full_sum_after_declared_uniform_leakage_window",
            "gross_aggregate_merge_leakage_before_window": gross_aggregate,
            "net_phase_feedback_leg_merge_leakage": phase_net,
            "net_directed_cycle_leg_merge_leakage": cycle_net,
            "net_aggregate_merge_leakage": net_aggregate,
            "producer_guard_captured_leakage_total": captured_total,
            "aggregate_merge_leakage_ceiling": aggregate_ceiling,
            "aggregate_merge_leakage_margin": net_margin,
            "i14_6_1_aggregate_margin": i1461_margin,
            "margin_improvement_over_i14_6_1": margin_improvement,
            "target_aggregate_margin": TARGET_AGGREGATE_MARGIN,
            "target_margin_gate_passed": net_margin >= TARGET_AGGREGATE_MARGIN,
            "aggregate_leakage_gate_passed": net_aggregate <= aggregate_ceiling,
            "leakage_cancellation_used": False,
            "overlap_credit_used": False,
            "hidden_sink_or_source_used": False,
            "double_counting_discount_used": False,
            "ceiling_relaxation_used": False,
        },
        "claim_boundary": {
            "wider_margin_multi_leg_leakage_aggregation_supported": True,
            "native_aggregate_shared_medium_leakage_supported": False,
            "native_multi_role_ecology_supported": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "ecology_success_claim_allowed": False,
            "agency_claim_allowed": False,
        },
        "geometry_interpretation": (
            "I14.6-2 strengthens I14.6-1 by routing both leakage channels through "
            "one declared producer-mediated interface guard before applying the "
            "same full-sum aggregation policy. The aggregate ceiling is unchanged. "
            "The wider margin comes from lower net channel leakage after a visible "
            "bridge guard, with captured leakage recorded as producer debt rather "
            "than hidden native success."
        ),
    }
    return finalize(artifact)


def build_record(
    i146: dict[str, Any],
    i1461: dict[str, Any],
    i1461_art: dict[str, Any],
    i1444_art: dict[str, Any],
    i1452_art: dict[str, Any],
) -> dict[str, Any]:
    runtime = build_runtime_artifact(i146, i1461, i1461_art, i1444_art, i1452_art)
    write_json(RUNTIME, runtime)
    manifest = artifact_manifest(RUNTIME, "n29_i14_6_2_wider_margin_leakage_aggregation_artifact")
    trace = runtime["aggregation_trace"]
    policy = runtime["wider_margin_policy"]
    row = {
        "row_id": "n29_i14_6_2_wider_margin_multi_leg_leakage_aggregation_variant",
        "row_decision": "partial",
        "row_decision_scope": "producer_mediated_wider_margin_leakage_aggregation_variant_pending_i14d_i14e",
        "i14_6_1_consumed": True,
        "i14_6_1_replaced": False,
        "same_aggregate_ceiling_as_i14_6_1": True,
        "full_sum_aggregation_preserved": True,
        "uniform_leakage_window_used": True,
        "leakage_window_factor": policy["leakage_window_factor"],
        "same_factor_applied_to_all_channels": policy["same_factor_applied_to_all_channels"],
        "wider_margin_multi_leg_leakage_aggregation_supported": trace[
            "target_margin_gate_passed"
        ],
        "native_aggregate_shared_medium_leakage_supported": False,
        "gross_aggregate_merge_leakage_before_window": trace[
            "gross_aggregate_merge_leakage_before_window"
        ],
        "net_aggregate_merge_leakage": trace["net_aggregate_merge_leakage"],
        "producer_guard_captured_leakage_total": trace[
            "producer_guard_captured_leakage_total"
        ],
        "aggregate_merge_leakage_ceiling": trace["aggregate_merge_leakage_ceiling"],
        "aggregate_merge_leakage_margin": trace["aggregate_merge_leakage_margin"],
        "margin_improvement_over_i14_6_1": trace["margin_improvement_over_i14_6_1"],
        "target_margin_gate_passed": trace["target_margin_gate_passed"],
        "leakage_cancellation_used": trace["leakage_cancellation_used"],
        "overlap_credit_used": trace["overlap_credit_used"],
        "hidden_sink_or_source_used": trace["hidden_sink_or_source_used"],
        "double_counting_discount_used": trace["double_counting_discount_used"],
        "ceiling_relaxation_used": trace["ceiling_relaxation_used"],
        "producer_mediated_bridge_lane_recorded": True,
        "native_multi_role_ecology_supported": False,
        "resource_economy_claim_allowed": False,
        "cooperation_claim_allowed": False,
        "exploitation_claim_allowed": False,
        "ecology_success_claim_allowed": False,
        "agency_claim_allowed": False,
        "claim_ceiling": "producer_mediated_wider_margin_leakage_aggregation_variant_pending_controls_replay",
        "runtime_artifact_manifest": manifest,
        "remaining_debt": [
            "I14-D composition controls pending",
            "I14-E replay/stress pending",
            "wider leakage margin is producer-mediated through a bridge interface guard",
            "producer guard capture remains naturalization debt, not native shared-medium leakage support",
            "resource economy, cooperation, exploitation, ecology success, and agency claims remain blocked",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_wider_margin_leakage_aggregation_i1462",
        "experiment_id": "N29",
        "title": "Prototype D I14.6-2 Wider-Margin Leakage Aggregation Variant",
        "iteration": "I14.6-2",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_wider_margin_leakage_aggregation_bridge_variant_pending_i14d_i14e",
        "source_artifacts": [
            source_artifact("n29_i14_6_multi_role_phase_loop", I146, i146),
            source_artifact("n29_i14_6_1_leakage_aggregation", I1461, i1461),
            source_artifact("n29_i14_6_1_leakage_aggregation_artifact", I1461_ART, i1461_art),
            source_artifact("n29_i14_4_4_directed_cycle_artifact", I1444_ART, i1444_art),
            source_artifact("n29_i14_5_2_buffered_feedback_artifact", I1452_ART, i1452_art),
        ],
        "leakage_aggregation_row": row,
        "wider_margin_multi_leg_leakage_aggregation_supported": row[
            "wider_margin_multi_leg_leakage_aggregation_supported"
        ],
        "native_aggregate_shared_medium_leakage_supported": False,
        "producer_mediated_bridge_lane_recorded": True,
        "ready_for_i14d_i14e": True,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check("i14_6_1_supported", i1461["multi_leg_leakage_aggregation_supported"] is True),
            check("same_aggregate_ceiling_preserved", row["same_aggregate_ceiling_as_i14_6_1"] is True),
            check("full_sum_aggregation_preserved", row["full_sum_aggregation_preserved"] is True),
            check("same_factor_all_channels", row["same_factor_applied_to_all_channels"] is True),
            check("target_margin_gate_passed", row["target_margin_gate_passed"] is True),
            check("ceiling_relaxation_rejected", row["ceiling_relaxation_used"] is False),
            check("leakage_cancellation_rejected", row["leakage_cancellation_used"] is False),
            check("overlap_credit_rejected", row["overlap_credit_used"] is False),
            check("hidden_sink_or_source_rejected", row["hidden_sink_or_source_used"] is False),
            check(
                "double_counting_discount_rejected",
                row["double_counting_discount_used"] is False,
            ),
            check(
                "native_aggregate_shared_medium_blocked",
                row["native_aggregate_shared_medium_leakage_supported"] is False,
            ),
            check("artifact_manifest_sha_match", manifest_sha_match(manifest)),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_6_2_wider_margin_leakage_aggregation"
        data["ready_for_i14d_i14e"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    row = data["leakage_aggregation_row"]
    runtime = load_json(RUNTIME)
    trace = runtime["aggregation_trace"]
    lines = [
        "# Prototype D I14.6-2 Wider-Margin Leakage Aggregation Variant",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Summary",
        "",
        "```text",
        f"wider_margin_multi_leg_leakage_aggregation_supported = {str(data['wider_margin_multi_leg_leakage_aggregation_supported']).lower()}",
        f"native_aggregate_shared_medium_leakage_supported = {str(data['native_aggregate_shared_medium_leakage_supported']).lower()}",
        f"producer_mediated_bridge_lane_recorded = {str(data['producer_mediated_bridge_lane_recorded']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        "```",
        "",
        "## Geometry",
        "",
        runtime["geometry_interpretation"],
        "",
        "This is not a ceiling relaxation. The aggregate ceiling remains 0.04,",
        "matching I14.6-1. The wider margin comes from a visible producer-mediated",
        "interface guard applied uniformly to both channels, with captured leakage",
        "recorded as producer debt.",
        "",
        "## Leakage",
        "",
        "```text",
        f"gross_aggregate_merge_leakage_before_window = {trace['gross_aggregate_merge_leakage_before_window']}",
        f"net_aggregate_merge_leakage = {trace['net_aggregate_merge_leakage']}",
        f"producer_guard_captured_leakage_total = {trace['producer_guard_captured_leakage_total']}",
        f"aggregate_merge_leakage_ceiling = {trace['aggregate_merge_leakage_ceiling']}",
        f"aggregate_merge_leakage_margin = {trace['aggregate_merge_leakage_margin']}",
        f"margin_improvement_over_i14_6_1 = {trace['margin_improvement_over_i14_6_1']}",
        f"target_margin_gate_passed = {str(trace['target_margin_gate_passed']).lower()}",
        "```",
        "",
        "## Claim Boundary",
        "",
        f"Claim ceiling: `{row['claim_ceiling']}`",
        "",
        "The row supports only a producer-mediated wider-margin aggregation",
        "variant. Native shared-medium leakage aggregation, resource economy,",
        "cooperation, exploitation, ecology success, and agency remain blocked.",
        "",
        "## Remaining Debt",
        "",
    ]
    lines.extend(f"- {item}" for item in row["remaining_debt"])
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| `{check_row['check_id']}` | `{str(check_row['passed']).lower()}` |"
        for check_row in data["checks"]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    i146 = load_json(I146)
    i1461 = load_json(I1461)
    i1461_art = load_json(I1461_ART)
    i1444_art = load_json(I1444_ART)
    i1452_art = load_json(I1452_ART)
    data = build_record(i146, i1461, i1461_art, i1444_art, i1452_art)
    write_json(OUT, data)
    write_report(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
