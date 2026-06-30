#!/usr/bin/env python3
"""Build N29 I14.6 multi-role phase-coupled loop composition."""

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
    "build_n29_multi_role_phase_loop_i146.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I144 = EXPERIMENT / "outputs" / "n29_neutral_circulation_composition_i144.json"
I1441 = EXPERIMENT / "outputs" / "n29_neutral_circulation_loop_closure_i1441.json"
I1443 = EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_i1443.json"
I1444 = EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_bridge_i1444.json"
I1444_ART = EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_bridge_i1444_artifact.json"
I145 = EXPERIMENT / "outputs" / "n29_phase_coupled_generator_extractor_i145.json"
I1451 = EXPERIMENT / "outputs" / "n29_generator_extractor_feedback_i1451.json"
I1452 = EXPERIMENT / "outputs" / "n29_buffered_generator_extractor_feedback_i1452.json"
I1452_ART = EXPERIMENT / "outputs" / "n29_buffered_generator_extractor_feedback_i1452_artifact.json"

OUT = EXPERIMENT / "outputs" / "n29_multi_role_phase_loop_i146.json"
RUNTIME = EXPERIMENT / "outputs" / "n29_multi_role_phase_loop_i146_artifact.json"
REPORT = EXPERIMENT / "reports" / "n29_multi_role_phase_loop_i146.md"

MIN_CROSS_BRIDGE_DELTA = 0.04
MAX_COMBINED_LOOP_RESIDUAL_ABS = 0.02
PER_LEG_MERGE_LEAKAGE_CEILING = 0.025

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
    i144: dict[str, Any],
    i1441: dict[str, Any],
    i1443: dict[str, Any],
    i1444: dict[str, Any],
    i1444_art: dict[str, Any],
    i145: dict[str, Any],
    i1451: dict[str, Any],
    i1452: dict[str, Any],
    i1452_art: dict[str, Any],
) -> dict[str, Any]:
    phase_residual = i1452_art["phase_residual_record"]
    cycle_residual = i1444_art["cycle_residual_state"]
    later_generator = i1452_art["later_generator_feedback_leg"]["axis_deltas"]
    cycle_return = cycle_residual["alpha_class_return_delta"]
    phase_to_cycle_signal = later_generator["environment"]
    cycle_to_generator_signal = cycle_return
    cross_bridge_residual = round(abs(cycle_to_generator_signal - phase_to_cycle_signal), 6)
    combined_residual = max(
        phase_residual["max_phase_residual_abs"],
        cycle_residual["closure_residual_abs_max"],
        cross_bridge_residual,
    )
    phase_leak = i1452_art["leakage_record"]
    cycle_leak = i1444_art["leakage_record"]
    per_leg_leakage_values = {
        "phase_feedback_leg_merge_leakage": phase_leak["merge_leakage_value"],
        "directed_cycle_leg_merge_leakage": cycle_leak["merge_leakage_value"],
    }
    max_per_leg_leakage = max(per_leg_leakage_values.values())
    artifact = {
        "artifact_id": "n29_multi_role_phase_loop_i146_artifact",
        "experiment_id": "N29",
        "iteration": "I14.6",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "producer_mediated_multi_role_phase_coupled_loop_artifact",
        "composition_target": "multi_role_phase_coupled_loop_candidate",
        "source_i14_4_digest": i144["output_digest"],
        "source_i14_4_1_digest": i1441["output_digest"],
        "source_i14_4_3_digest": i1443["output_digest"],
        "source_i14_4_4_digest": i1444["output_digest"],
        "source_i14_5_digest": i145["output_digest"],
        "source_i14_5_1_digest": i1451["output_digest"],
        "source_i14_5_2_digest": i1452["output_digest"],
        "composition_lane_record": {
            "native_source_current_leg_present": True,
            "producer_mediated_bridge_legs_present": True,
            "producer_mediated_bridge_lane_recorded": True,
            "producer_success_can_upgrade_native": False,
            "native_multi_role_ecology_supported": False,
        },
        "component_roles": [
            {
                "role_id": "generator",
                "source_iteration": "I14.1 via I14.5-2",
                "role_preserved": True,
                "producer_mediated": False,
            },
            {
                "role_id": "extractor",
                "source_iteration": "I14.2-3 via I14.5-2",
                "role_preserved": True,
                "producer_mediated": True,
            },
            {
                "role_id": "processor_buffer",
                "source_iteration": "I14.3 via I14.5-2",
                "role_preserved": True,
                "producer_mediated": False,
            },
            {
                "role_id": "all_forward_circulation",
                "source_iteration": "I14.4-4",
                "role_preserved": True,
                "producer_mediated": True,
            },
        ],
        "ordered_dependency_cycle": {
            "ordered_sequence": [
                "generator_enriches_medium_shell",
                "extractor_consumes_generator_changed_medium",
                "processor_buffers_extractor_changed_medium",
                "later_generator_consumes_buffered_changed_medium",
                "all_forward_circulation_consumes_later_generator_signal",
                "alpha_class_return_closes_to_generator_side",
            ],
            "phase_feedback_input": "I14.5-2",
            "circulation_input": "I14.4-4",
            "i14_5_2_later_generator_signal_used": phase_to_cycle_signal,
            "i14_4_4_alpha_class_return_used": cycle_to_generator_signal,
            "phase_to_cycle_bridge_gate_passed": phase_to_cycle_signal >= MIN_CROSS_BRIDGE_DELTA,
            "cycle_to_generator_bridge_gate_passed": cycle_to_generator_signal >= MIN_CROSS_BRIDGE_DELTA,
            "cross_bridge_residual": cross_bridge_residual,
            "ordered_dependency_cycle_recorded": True,
            "report_only_composition": False,
            "literal_perpetual_runtime_claimed": False,
        },
        "combined_loop_residual_record": {
            "phase_feedback_max_residual_abs": phase_residual["max_phase_residual_abs"],
            "directed_cycle_max_residual_abs": cycle_residual["closure_residual_abs_max"],
            "cross_bridge_residual_abs": cross_bridge_residual,
            "combined_loop_residual_abs": combined_residual,
            "combined_loop_residual_ceiling": MAX_COMBINED_LOOP_RESIDUAL_ABS,
            "combined_loop_residual_gate_passed": combined_residual
            <= MAX_COMBINED_LOOP_RESIDUAL_ABS,
        },
        "leakage_record": {
            "per_leg_leakage_values": per_leg_leakage_values,
            "per_leg_merge_leakage_ceiling": PER_LEG_MERGE_LEAKAGE_CEILING,
            "max_per_leg_merge_leakage": max_per_leg_leakage,
            "per_leg_leakage_gates_passed": max_per_leg_leakage
            <= PER_LEG_MERGE_LEAKAGE_CEILING,
            "multi_leg_leakage_aggregation_supported": False,
            "why_not_aggregate": (
                "I14.6 composes bridge rows across different declared frames; "
                "per-leg leakage gates pass, but no single native shared-medium "
                "leakage aggregation channel is established."
            ),
        },
        "geometry_interpretation": (
            "I14.6 composes the strongest current Prototype D bridge rows into a "
            "multi-role phase-coupled loop candidate. I14.5-2 supplies the "
            "generator -> extractor -> processor/buffer -> later generator path. "
            "I14.4-4 supplies an all-forward circulation bridge that consumes the "
            "later-generator signal and returns dependency toward the generator "
            "side. This is closer to the intended perpetual-like phase loop than "
            "I14.5-2 alone, but it is still producer-mediated bridge evidence, "
            "not a native ecology or literal perpetual runtime claim."
        ),
        "claim_boundary": {
            "multi_role_phase_loop_candidate_created": True,
            "native_multi_role_ecology_supported": False,
            "native_phase_coupled_exchange_supported": False,
            "native_closed_environmental_circulation_supported": False,
            "literal_perpetual_loop_claim_allowed": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "ecology_success_claim_allowed": False,
            "agency_claim_allowed": False,
        },
    }
    return finalize(artifact)


def build_record(
    i144: dict[str, Any],
    i1441: dict[str, Any],
    i1443: dict[str, Any],
    i1444: dict[str, Any],
    i1444_art: dict[str, Any],
    i145: dict[str, Any],
    i1451: dict[str, Any],
    i1452: dict[str, Any],
    i1452_art: dict[str, Any],
) -> dict[str, Any]:
    runtime = build_runtime_artifact(
        i144, i1441, i1443, i1444, i1444_art, i145, i1451, i1452, i1452_art
    )
    write_json(RUNTIME, runtime)
    manifest = artifact_manifest(RUNTIME, "n29_i14_6_multi_role_phase_loop_artifact")
    cycle = runtime["ordered_dependency_cycle"]
    residual = runtime["combined_loop_residual_record"]
    leakage = runtime["leakage_record"]
    lane = runtime["composition_lane_record"]
    row = {
        "row_id": "n29_i14_6_multi_role_phase_coupled_loop_candidate",
        "row_decision": "partial",
        "row_decision_scope": "producer_mediated_multi_role_phase_loop_candidate_pending_i14d_i14e",
        "i14_4_4_consumed": True,
        "i14_5_2_consumed_as_primary_phase_feedback_input": True,
        "i14_5_and_i14_5_1_consumed_as_lineage_context": True,
        "multi_role_phase_loop_candidate_created": True,
        "ordered_dependency_cycle_recorded": cycle["ordered_dependency_cycle_recorded"],
        "report_only_composition": cycle["report_only_composition"],
        "phase_to_cycle_bridge_gate_passed": cycle["phase_to_cycle_bridge_gate_passed"],
        "cycle_to_generator_bridge_gate_passed": cycle["cycle_to_generator_bridge_gate_passed"],
        "combined_loop_residual_gate_passed": residual["combined_loop_residual_gate_passed"],
        "per_leg_leakage_gates_passed": leakage["per_leg_leakage_gates_passed"],
        "multi_leg_leakage_aggregation_supported": leakage[
            "multi_leg_leakage_aggregation_supported"
        ],
        "producer_mediated_bridge_lane_recorded": lane["producer_mediated_bridge_lane_recorded"],
        "native_multi_role_ecology_supported": False,
        "native_phase_coupled_exchange_supported": False,
        "literal_perpetual_runtime_claimed": cycle["literal_perpetual_runtime_claimed"],
        "literal_perpetual_loop_claim_allowed": False,
        "resource_economy_claim_allowed": False,
        "cooperation_claim_allowed": False,
        "exploitation_claim_allowed": False,
        "agency_claim_allowed": False,
        "claim_ceiling": "producer_mediated_multi_role_phase_loop_candidate_pending_controls_replay",
        "runtime_artifact_manifest": manifest,
        "remaining_debt": [
            "I14-D composition controls pending",
            "I14-E replay/stress pending",
            "multi-role loop relies on producer-mediated bridge legs",
            "per-leg leakage gates pass, but native aggregate shared-medium leakage is not established",
            "resource economy, cooperation, exploitation, ecology success, literal perpetual runtime, and agency claims remain blocked",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_multi_role_phase_loop_i146",
        "experiment_id": "N29",
        "title": "Prototype D I14.6 Multi-Role Phase-Coupled Loop Composition",
        "iteration": "I14.6",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_multi_role_phase_loop_bridge_candidate_pending_i14d_i14e",
        "source_artifacts": [
            source_artifact("n29_i14_4_single_direction_circulation", I144, i144),
            source_artifact("n29_i14_4_1_reverse_bridge_context", I1441, i1441),
            source_artifact("n29_i14_4_3_native_directed_cycle_blocker", I1443, i1443),
            source_artifact("n29_i14_4_4_directed_cycle_bridge", I1444, i1444),
            source_artifact("n29_i14_4_4_directed_cycle_artifact", I1444_ART, i1444_art),
            source_artifact("n29_i14_5_one_way_phase_bridge", I145, i145),
            source_artifact("n29_i14_5_1_feedback_bridge", I1451, i1451),
            source_artifact("n29_i14_5_2_buffered_feedback_bridge", I1452, i1452),
            source_artifact("n29_i14_5_2_buffered_feedback_artifact", I1452_ART, i1452_art),
        ],
        "composition_attempt_row": row,
        "multi_role_phase_loop_candidate_created": True,
        "native_multi_role_ecology_supported": False,
        "producer_mediated_bridge_lane_recorded": True,
        "ready_for_i14d_i14e": True,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check("i14_4_4_directed_cycle_bridge_present", i1444["producer_mediated_directed_cycle_candidate_created"] is True),
            check("i14_5_2_buffered_feedback_present", i1452["buffered_phase_feedback_bridge_candidate_created"] is True),
            check("ordered_dependency_cycle_recorded", row["ordered_dependency_cycle_recorded"] is True),
            check("report_only_composition_rejected", row["report_only_composition"] is False),
            check("phase_to_cycle_bridge_gate_passed", row["phase_to_cycle_bridge_gate_passed"] is True),
            check("cycle_to_generator_bridge_gate_passed", row["cycle_to_generator_bridge_gate_passed"] is True),
            check("combined_loop_residual_gate_passed", row["combined_loop_residual_gate_passed"] is True),
            check("per_leg_leakage_gates_passed", row["per_leg_leakage_gates_passed"] is True),
            check("producer_lane_recorded", row["producer_mediated_bridge_lane_recorded"] is True),
            check("native_multi_role_ecology_blocked", row["native_multi_role_ecology_supported"] is False),
            check("literal_perpetual_runtime_not_claimed", row["literal_perpetual_runtime_claimed"] is False),
            check("artifact_manifest_sha_match", manifest_sha_match(manifest)),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_6_multi_role_phase_loop_composition"
        data["ready_for_i14d_i14e"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    row = data["composition_attempt_row"]
    runtime = load_json(RUNTIME)
    residual = runtime["combined_loop_residual_record"]
    leakage = runtime["leakage_record"]
    lines = [
        "# Prototype D I14.6 Multi-Role Phase-Coupled Loop Composition",
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
        f"multi_role_phase_loop_candidate_created = {str(data['multi_role_phase_loop_candidate_created']).lower()}",
        f"native_multi_role_ecology_supported = {str(data['native_multi_role_ecology_supported']).lower()}",
        f"producer_mediated_bridge_lane_recorded = {str(data['producer_mediated_bridge_lane_recorded']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        "```",
        "",
        "## Geometry",
        "",
        runtime["geometry_interpretation"],
        "",
        "The composed sequence is:",
        "",
        "```text",
        "generator -> extractor -> processor/buffer -> later generator -> all-forward circulation -> generator-side return",
        "```",
        "",
        "This is the first Prototype D row that joins the buffered",
        "generator/extractor phase-feedback path with the all-forward directed",
        "circulation path. It is a composition bridge candidate, not native",
        "ecology and not a literal perpetual runtime.",
        "",
        "## Residual And Leakage",
        "",
        "```text",
        f"phase_feedback_max_residual_abs = {residual['phase_feedback_max_residual_abs']}",
        f"directed_cycle_max_residual_abs = {residual['directed_cycle_max_residual_abs']}",
        f"cross_bridge_residual_abs = {residual['cross_bridge_residual_abs']}",
        f"combined_loop_residual_abs = {residual['combined_loop_residual_abs']}",
        f"combined_loop_residual_ceiling = {residual['combined_loop_residual_ceiling']}",
        f"max_per_leg_merge_leakage = {leakage['max_per_leg_merge_leakage']}",
        f"per_leg_merge_leakage_ceiling = {leakage['per_leg_merge_leakage_ceiling']}",
        f"multi_leg_leakage_aggregation_supported = {str(leakage['multi_leg_leakage_aggregation_supported']).lower()}",
        "```",
        "",
        "## Claim Boundary",
        "",
        f"Claim ceiling: `{row['claim_ceiling']}`",
        "",
        "The row does not support native multi-role ecology, resource economy,",
        "cooperation, exploitation, ecology success, literal perpetual runtime,",
        "or agency.",
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
    i144 = load_json(I144)
    i1441 = load_json(I1441)
    i1443 = load_json(I1443)
    i1444 = load_json(I1444)
    i1444_art = load_json(I1444_ART)
    i145 = load_json(I145)
    i1451 = load_json(I1451)
    i1452 = load_json(I1452)
    i1452_art = load_json(I1452_ART)
    data = build_record(i144, i1441, i1443, i1444, i1444_art, i145, i1451, i1452, i1452_art)
    write_json(OUT, data)
    write_report(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
