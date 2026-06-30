#!/usr/bin/env python3
"""Build N29 I14.6-1 multi-leg leakage aggregation probe."""

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
    "build_n29_multi_leg_leakage_aggregation_i1461.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I146 = EXPERIMENT / "outputs" / "n29_multi_role_phase_loop_i146.json"
I146_ART = EXPERIMENT / "outputs" / "n29_multi_role_phase_loop_i146_artifact.json"
I1444_ART = EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_bridge_i1444_artifact.json"
I1452_ART = EXPERIMENT / "outputs" / "n29_buffered_generator_extractor_feedback_i1452_artifact.json"

OUT = EXPERIMENT / "outputs" / "n29_multi_leg_leakage_aggregation_i1461.json"
RUNTIME = EXPERIMENT / "outputs" / "n29_multi_leg_leakage_aggregation_i1461_artifact.json"
REPORT = EXPERIMENT / "reports" / "n29_multi_leg_leakage_aggregation_i1461.md"

PER_LEG_MERGE_LEAKAGE_CEILING = 0.025
AGGREGATE_CEILING_RESERVE = 0.010
NARROW_MARGIN_FLOOR = 0.005

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
    i146_art: dict[str, Any],
    i1444_art: dict[str, Any],
    i1452_art: dict[str, Any],
) -> dict[str, Any]:
    phase_leak = i1452_art["leakage_record"]["merge_leakage_value"]
    cycle_leak = i1444_art["leakage_record"]["merge_leakage_value"]
    aggregate_leakage = round(phase_leak + cycle_leak, 6)
    aggregate_ceiling = round(
        (2 * PER_LEG_MERGE_LEAKAGE_CEILING) - AGGREGATE_CEILING_RESERVE, 6
    )
    aggregate_margin = round(aggregate_ceiling - aggregate_leakage, 6)
    narrow_margin = aggregate_margin < NARROW_MARGIN_FLOOR
    artifact = {
        "artifact_id": "n29_multi_leg_leakage_aggregation_i1461_artifact",
        "experiment_id": "N29",
        "iteration": "I14.6-1",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "producer_mediated_multi_leg_leakage_aggregation_artifact",
        "source_i14_6_digest": i146["output_digest"],
        "source_i14_6_artifact_digest": i146_art["output_digest"],
        "source_i14_4_4_artifact_digest": i1444_art["output_digest"],
        "source_i14_5_2_artifact_digest": i1452_art["output_digest"],
        "i14_6_prior_leakage_status": i146_art["leakage_record"],
        "shared_leakage_frame_policy": {
            "policy_id": "n29_i14_6_1_common_bridge_leakage_frame_v1",
            "declared_before_use": True,
            "producer_mediated": True,
            "frame_role": (
                "map the I14.5-2 phase-feedback leakage and I14.4-4 directed-cycle "
                "leakage into one common bridge attribution frame"
            ),
            "native_shared_medium_frame": False,
            "aggregate_ceiling_formula": "2 * per_leg_ceiling - aggregate_reserve",
            "per_leg_ceiling": PER_LEG_MERGE_LEAKAGE_CEILING,
            "aggregate_reserve": AGGREGATE_CEILING_RESERVE,
            "aggregate_ceiling": aggregate_ceiling,
            "thresholds_retuned_after_outcome": False,
            "producer_success_can_upgrade_native": False,
        },
        "leakage_channel_map": [
            {
                "channel_id": "phase_feedback_leg",
                "source_iteration": "I14.5-2",
                "source_role": "generator_extractor_processor_feedback",
                "merge_leakage_value": phase_leak,
                "merge_leakage_ceiling": i1452_art["leakage_record"]["merge_leakage_ceiling"],
                "mapped_to_common_frame": True,
            },
            {
                "channel_id": "directed_cycle_leg",
                "source_iteration": "I14.4-4",
                "source_role": "all_forward_directed_circulation",
                "merge_leakage_value": cycle_leak,
                "merge_leakage_ceiling": i1444_art["leakage_record"]["merge_leakage_ceiling"],
                "mapped_to_common_frame": True,
            },
        ],
        "aggregation_trace": {
            "aggregation_method": "full_sum_no_cancellation",
            "phase_feedback_leg_merge_leakage": phase_leak,
            "directed_cycle_leg_merge_leakage": cycle_leak,
            "aggregate_merge_leakage": aggregate_leakage,
            "aggregate_merge_leakage_ceiling": aggregate_ceiling,
            "aggregate_merge_leakage_margin": aggregate_margin,
            "aggregate_leakage_gate_passed": aggregate_leakage <= aggregate_ceiling,
            "narrow_margin_recorded": narrow_margin,
            "leakage_cancellation_used": False,
            "overlap_credit_used": False,
            "hidden_sink_or_source_used": False,
            "double_counting_discount_used": False,
        },
        "claim_boundary": {
            "multi_leg_leakage_aggregation_supported": True,
            "native_aggregate_shared_medium_leakage_supported": False,
            "native_multi_role_ecology_supported": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "ecology_success_claim_allowed": False,
            "agency_claim_allowed": False,
        },
        "geometry_interpretation": (
            "I14.6-1 puts the I14.5-2 phase-feedback leg and the I14.4-4 "
            "directed-cycle leg into a common producer-mediated leakage frame. "
            "It does not cancel one leakage value against the other and does not "
            "discount overlap. The aggregate leakage is the full sum of both "
            "legs. That supports a narrow bridge-lane aggregate leakage record, "
            "while native shared-medium leakage aggregation remains unsupported."
        ),
    }
    return finalize(artifact)


def build_record(
    i146: dict[str, Any],
    i146_art: dict[str, Any],
    i1444_art: dict[str, Any],
    i1452_art: dict[str, Any],
) -> dict[str, Any]:
    runtime = build_runtime_artifact(i146, i146_art, i1444_art, i1452_art)
    write_json(RUNTIME, runtime)
    manifest = artifact_manifest(RUNTIME, "n29_i14_6_1_multi_leg_leakage_aggregation_artifact")
    trace = runtime["aggregation_trace"]
    policy = runtime["shared_leakage_frame_policy"]
    row = {
        "row_id": "n29_i14_6_1_multi_leg_leakage_aggregation_probe",
        "row_decision": "partial",
        "row_decision_scope": "producer_mediated_multi_leg_leakage_aggregation_candidate_pending_i14d_i14e",
        "i14_6_consumed": True,
        "i14_6_replaced": False,
        "i14_6_per_leg_only_status_resolved_in_bridge_lane": True,
        "shared_leakage_frame_declared": True,
        "native_shared_medium_frame": policy["native_shared_medium_frame"],
        "multi_leg_leakage_aggregation_supported": trace["aggregate_leakage_gate_passed"],
        "native_aggregate_shared_medium_leakage_supported": False,
        "aggregate_merge_leakage": trace["aggregate_merge_leakage"],
        "aggregate_merge_leakage_ceiling": trace["aggregate_merge_leakage_ceiling"],
        "aggregate_merge_leakage_margin": trace["aggregate_merge_leakage_margin"],
        "narrow_margin_recorded": trace["narrow_margin_recorded"],
        "leakage_cancellation_used": trace["leakage_cancellation_used"],
        "overlap_credit_used": trace["overlap_credit_used"],
        "hidden_sink_or_source_used": trace["hidden_sink_or_source_used"],
        "double_counting_discount_used": trace["double_counting_discount_used"],
        "producer_mediated_bridge_lane_recorded": True,
        "native_multi_role_ecology_supported": False,
        "resource_economy_claim_allowed": False,
        "cooperation_claim_allowed": False,
        "exploitation_claim_allowed": False,
        "ecology_success_claim_allowed": False,
        "agency_claim_allowed": False,
        "claim_ceiling": "producer_mediated_multi_leg_leakage_aggregation_candidate_pending_controls_replay",
        "runtime_artifact_manifest": manifest,
        "remaining_debt": [
            "I14-D composition controls pending",
            "I14-E replay/stress pending",
            "aggregate leakage margin is narrow",
            "aggregation frame is producer-mediated, not native shared-medium LGRC",
            "resource economy, cooperation, exploitation, ecology success, and agency claims remain blocked",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_multi_leg_leakage_aggregation_i1461",
        "experiment_id": "N29",
        "title": "Prototype D I14.6-1 Multi-Leg Leakage Aggregation Probe",
        "iteration": "I14.6-1",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_multi_leg_leakage_aggregation_bridge_candidate_pending_i14d_i14e",
        "source_artifacts": [
            source_artifact("n29_i14_6_multi_role_phase_loop", I146, i146),
            source_artifact("n29_i14_6_multi_role_phase_loop_artifact", I146_ART, i146_art),
            source_artifact("n29_i14_4_4_directed_cycle_artifact", I1444_ART, i1444_art),
            source_artifact("n29_i14_5_2_buffered_feedback_artifact", I1452_ART, i1452_art),
        ],
        "leakage_aggregation_row": row,
        "multi_leg_leakage_aggregation_supported": row[
            "multi_leg_leakage_aggregation_supported"
        ],
        "native_aggregate_shared_medium_leakage_supported": False,
        "producer_mediated_bridge_lane_recorded": True,
        "ready_for_i14d_i14e": True,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check(
                "i14_6_prior_per_leg_only",
                i146["composition_attempt_row"]["multi_leg_leakage_aggregation_supported"]
                is False,
            ),
            check("shared_leakage_frame_declared", row["shared_leakage_frame_declared"] is True),
            check("all_channels_mapped", len(runtime["leakage_channel_map"]) == 2),
            check(
                "full_sum_aggregation_passed",
                row["aggregate_merge_leakage"] <= row["aggregate_merge_leakage_ceiling"],
            ),
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
        data["acceptance_state"] = "failed_i14_6_1_multi_leg_leakage_aggregation"
        data["ready_for_i14d_i14e"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    row = data["leakage_aggregation_row"]
    runtime = load_json(RUNTIME)
    trace = runtime["aggregation_trace"]
    lines = [
        "# Prototype D I14.6-1 Multi-Leg Leakage Aggregation Probe",
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
        f"multi_leg_leakage_aggregation_supported = {str(data['multi_leg_leakage_aggregation_supported']).lower()}",
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
        "The aggregation is intentionally conservative: both leg leakages are",
        "summed. No cancellation, overlap credit, hidden sink/source, or",
        "double-counting discount is used.",
        "",
        "## Leakage",
        "",
        "```text",
        f"phase_feedback_leg_merge_leakage = {trace['phase_feedback_leg_merge_leakage']}",
        f"directed_cycle_leg_merge_leakage = {trace['directed_cycle_leg_merge_leakage']}",
        f"aggregate_merge_leakage = {trace['aggregate_merge_leakage']}",
        f"aggregate_merge_leakage_ceiling = {trace['aggregate_merge_leakage_ceiling']}",
        f"aggregate_merge_leakage_margin = {trace['aggregate_merge_leakage_margin']}",
        f"narrow_margin_recorded = {str(trace['narrow_margin_recorded']).lower()}",
        "```",
        "",
        "## Claim Boundary",
        "",
        f"Claim ceiling: `{row['claim_ceiling']}`",
        "",
        "The row supports only producer-mediated aggregate leakage attribution.",
        "Native shared-medium leakage aggregation, resource economy, cooperation,",
        "exploitation, ecology success, and agency remain blocked.",
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
    i146_art = load_json(I146_ART)
    i1444_art = load_json(I1444_ART)
    i1452_art = load_json(I1452_ART)
    data = build_record(i146, i146_art, i1444_art, i1452_art)
    write_json(OUT, data)
    write_report(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
