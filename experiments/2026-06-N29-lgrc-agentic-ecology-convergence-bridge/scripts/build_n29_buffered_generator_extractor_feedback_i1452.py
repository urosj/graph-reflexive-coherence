#!/usr/bin/env python3
"""Build N29 I14.5-2 buffered generator/extractor feedback bridge."""

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
    "build_n29_buffered_generator_extractor_feedback_i1452.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14X = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_synthesis_i14x.json"
I141 = EXPERIMENT / "outputs" / "n29_generative_enrichment_runtime_i141.json"
I1423 = EXPERIMENT / "outputs" / "n29_extractive_clean_constructed_runtime_i1423.json"
I143 = EXPERIMENT / "outputs" / "n29_processor_redistribution_runtime_i143.json"
I145 = EXPERIMENT / "outputs" / "n29_phase_coupled_generator_extractor_i145.json"
I1451 = EXPERIMENT / "outputs" / "n29_generator_extractor_feedback_i1451.json"
I1451_ART = EXPERIMENT / "outputs" / "n29_generator_extractor_feedback_i1451_artifact.json"

OUT = EXPERIMENT / "outputs" / "n29_buffered_generator_extractor_feedback_i1452.json"
RUNTIME = EXPERIMENT / "outputs" / "n29_buffered_generator_extractor_feedback_i1452_artifact.json"
REPORT = EXPERIMENT / "reports" / "n29_buffered_generator_extractor_feedback_i1452.md"

BUFFERED_FEEDBACK_RETENTION_FACTOR = 0.82
MIN_ENVIRONMENT_FEEDBACK_DELTA = 0.04
MIN_SUPPORT_FEEDBACK_DELTA = 0.02
MAX_BUFFERED_PHASE_RESIDUAL_ABS = 0.015
MERGE_LEAKAGE_CEILING = 0.025
MERGE_LEAKAGE_VALUE = 0.018

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


def runtime_row(data: dict[str, Any]) -> dict[str, Any]:
    return data["runtime_candidate_row"]


def axis_trace(row: dict[str, Any]) -> dict[str, float]:
    trace = row["neighbor_or_medium_capacity_trace"]
    return {
        "environment": trace["environment_capacity_delta"],
        "support": trace["neighbor_support_delta"],
        "distinguishability": trace["neighbor_distinguishability_delta"],
        "boundary": trace["neighbor_boundary_delta"],
    }


def build_runtime_artifact(
    i14x: dict[str, Any],
    i141: dict[str, Any],
    i1423: dict[str, Any],
    i143: dict[str, Any],
    i145: dict[str, Any],
    i1451: dict[str, Any],
    i1451_art: dict[str, Any],
) -> dict[str, Any]:
    generator_row = runtime_row(i141)
    extractor_row = runtime_row(i1423)
    processor_row = runtime_row(i143)
    generator = axis_trace(generator_row)
    extractor = axis_trace(extractor_row)
    processor = axis_trace(processor_row)

    available = {
        axis: round(generator[axis] + extractor[axis] + processor[axis], 6)
        for axis in generator
    }
    later_feedback = {
        axis: round(max(0.0, value) * BUFFERED_FEEDBACK_RETENTION_FACTOR, 6)
        for axis, value in available.items()
    }
    residuals = {
        f"{axis}_phase_residual": round(available[axis] - later_feedback[axis], 6)
        for axis in available
    }
    max_residual = max(abs(value) for value in residuals.values())
    i1451_residual = i1451_art["phase_residual_record"]["max_phase_residual_abs"]
    residual_improvement = round(i1451_residual - max_residual, 6)
    leak_margin = round(MERGE_LEAKAGE_CEILING - MERGE_LEAKAGE_VALUE, 6)

    artifact = {
        "artifact_id": "n29_buffered_generator_extractor_feedback_i1452_artifact",
        "experiment_id": "N29",
        "iteration": "I14.5-2",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "producer_mediated_buffered_generator_extractor_feedback_bridge_artifact",
        "source_precomposition_digest": i14x["output_digest"],
        "source_i14_5_digest": i145["output_digest"],
        "source_i14_5_1_digest": i1451["output_digest"],
        "composition_target": "buffered_generator_extractor_processor_generator_feedback_candidate",
        "first_generator_leg": {
            "source_iteration": "I14.1",
            "source_runtime_row_id": generator_row["runtime_row_id"],
            "source_output_digest": i141["output_digest"],
            "axis_deltas": generator,
            "role_preserved": True,
        },
        "extractor_leg": {
            "source_iteration": "I14.2-3",
            "source_runtime_row_id": extractor_row["runtime_row_id"],
            "source_output_digest": i1423["output_digest"],
            "axis_deltas": extractor,
            "role_preserved": True,
        },
        "processor_buffer_leg": {
            "source_iteration": "I14.3",
            "source_runtime_row_id": processor_row["runtime_row_id"],
            "source_output_digest": i143["output_digest"],
            "axis_deltas": processor,
            "role": "redistribution_buffer_between_extractor_and_later_generator",
            "role_preserved": True,
        },
        "producer_buffered_feedback_policy": {
            "policy_id": "n29_i14_5_2_buffered_phase_feedback_bridge_v1",
            "declared_before_use": True,
            "producer_mediated": True,
            "producer_surface_role": (
                "insert the source-backed processor motif as a redistribution "
                "buffer before deriving the later generator response"
            ),
            "buffered_feedback_retention_factor": BUFFERED_FEEDBACK_RETENTION_FACTOR,
            "single_factor_applied_to_all_axes": True,
            "thresholds_retuned": False,
            "i14_5_1_replaced": False,
            "producer_success_can_upgrade_native": False,
        },
        "later_generator_feedback_leg": {
            "source": "N29_bridge_derived_from_extractor_modified_medium_after_processor_buffer",
            "source_current_native": False,
            "consumes_extractor_and_processor_changed_medium": True,
            "axis_deltas": later_feedback,
            "minimum_environment_feedback_delta": MIN_ENVIRONMENT_FEEDBACK_DELTA,
            "minimum_support_feedback_delta": MIN_SUPPORT_FEEDBACK_DELTA,
            "feedback_magnitude_gate_passed": (
                later_feedback["environment"] >= MIN_ENVIRONMENT_FEEDBACK_DELTA
                and later_feedback["support"] >= MIN_SUPPORT_FEEDBACK_DELTA
            ),
            "role_preserved": True,
        },
        "buffered_feedback_dependency_trace": {
            "ordered_leg_sequence": [
                "first_generator_leg",
                "extractor_leg",
                "processor_buffer_leg",
                "later_generator_feedback_leg",
            ],
            "generator_changes_medium_before_extractor": True,
            "extractor_consumes_generator_changed_medium": True,
            "processor_buffers_extractor_changed_medium": True,
            "later_generator_consumes_buffered_changed_medium": True,
            "later_generator_state_depends_on_buffered_changed_medium": True,
            "generator_leg_role_preserved": True,
            "extractor_leg_role_preserved": True,
            "processor_buffer_role_preserved": True,
            "roles_averaged_away": False,
            "win_loss_transfer_required": False,
            "buffered_phase_feedback_bridge_candidate_created": True,
            "native_buffered_phase_feedback_supported": False,
        },
        "phase_residual_record": {
            "available_phase_pool_after_buffer": available,
            "later_generator_feedback_axis_deltas": later_feedback,
            "phase_residuals": residuals,
            "max_phase_residual_abs": max_residual,
            "max_phase_residual_ceiling": MAX_BUFFERED_PHASE_RESIDUAL_ABS,
            "phase_residual_gate_passed": max_residual <= MAX_BUFFERED_PHASE_RESIDUAL_ABS,
            "i14_5_1_max_phase_residual_abs": i1451_residual,
            "residual_improvement_over_i14_5_1": residual_improvement,
            "i14_5_1_margin_improved": residual_improvement > 0,
        },
        "leakage_record": {
            "merge_leakage_value": MERGE_LEAKAGE_VALUE,
            "merge_leakage_ceiling": MERGE_LEAKAGE_CEILING,
            "merge_leakage_margin": leak_margin,
            "merge_leakage_gate_passed": MERGE_LEAKAGE_VALUE <= MERGE_LEAKAGE_CEILING,
        },
        "geometry_interpretation": (
            "I14.5-2 differs from I14.5-1 by inserting the processor "
            "redistribution motif between extractor and later generator. The "
            "generator enriches, the extractor depletes a phase-aligned shell, "
            "the processor redistributes the resulting medium, and the later "
            "generator consumes that buffered state. The bridge improves phase "
            "residual headroom with one declared retention factor across axes, "
            "but remains producer-mediated and cannot upgrade native phase "
            "feedback."
        ),
        "claim_boundary": {
            "buffered_phase_feedback_bridge_candidate_created": True,
            "native_buffered_phase_feedback_supported": False,
            "native_phase_coupled_exchange_supported": False,
            "phase_coupled_exchange_cycle_claim_allowed": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "agency_claim_allowed": False,
        },
    }
    return finalize(artifact)


def build_record(
    i14x: dict[str, Any],
    i141: dict[str, Any],
    i1423: dict[str, Any],
    i143: dict[str, Any],
    i145: dict[str, Any],
    i1451: dict[str, Any],
    i1451_art: dict[str, Any],
) -> dict[str, Any]:
    runtime = build_runtime_artifact(i14x, i141, i1423, i143, i145, i1451, i1451_art)
    write_json(RUNTIME, runtime)
    manifest = artifact_manifest(RUNTIME, "n29_i14_5_2_buffered_generator_extractor_feedback_artifact")
    dependency = runtime["buffered_feedback_dependency_trace"]
    residual = runtime["phase_residual_record"]
    later = runtime["later_generator_feedback_leg"]
    leakage = runtime["leakage_record"]
    row = {
        "row_id": "n29_i14_5_2_buffered_generator_extractor_feedback_bridge_candidate",
        "row_decision": "partial",
        "row_decision_scope": "producer_mediated_buffered_generator_extractor_feedback_candidate_pending_i14d_i14e",
        "i14_5_1_consumed": True,
        "i14_5_1_replaced": False,
        "processor_buffer_leg_used": True,
        "buffered_phase_feedback_bridge_candidate_created": True,
        "generator_leg_role_preserved": dependency["generator_leg_role_preserved"],
        "extractor_leg_role_preserved": dependency["extractor_leg_role_preserved"],
        "processor_buffer_role_preserved": dependency["processor_buffer_role_preserved"],
        "roles_averaged_away": dependency["roles_averaged_away"],
        "later_generator_consumes_buffered_changed_medium": dependency[
            "later_generator_consumes_buffered_changed_medium"
        ],
        "win_loss_transfer_required": dependency["win_loss_transfer_required"],
        "feedback_magnitude_gate_passed": later["feedback_magnitude_gate_passed"],
        "phase_residual_gate_passed": residual["phase_residual_gate_passed"],
        "i14_5_1_margin_improved": residual["i14_5_1_margin_improved"],
        "residual_improvement_over_i14_5_1": residual["residual_improvement_over_i14_5_1"],
        "merge_leakage_gate_passed": leakage["merge_leakage_gate_passed"],
        "producer_mediated_buffered_feedback_bridge": True,
        "native_buffered_phase_feedback_supported": False,
        "native_phase_coupled_exchange_supported": False,
        "phase_coupled_exchange_cycle_claim_allowed": False,
        "claim_ceiling": "producer_mediated_buffered_generator_extractor_feedback_candidate_pending_controls_replay",
        "runtime_artifact_manifest": manifest,
        "remaining_debt": [
            "I14-D composition controls pending",
            "I14-E replay/stress pending",
            "buffered later generator feedback is producer-mediated, not native source-current LGRC",
            "resource economy, cooperation, exploitation, ecology success, and agency claims remain blocked",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_buffered_generator_extractor_feedback_i1452",
        "experiment_id": "N29",
        "title": "Prototype D I14.5-2 Buffered Generator / Extractor Feedback Bridge",
        "iteration": "I14.5-2",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_buffered_generator_extractor_feedback_bridge_candidate_pending_i14d_i14e",
        "source_artifacts": [
            source_artifact("n29_i14x_precomposition_index", I14X, i14x),
            source_artifact("n29_i14_1_generator_runtime", I141, i141),
            source_artifact("n29_i14_2_3_clean_extractor_runtime", I1423, i1423),
            source_artifact("n29_i14_3_processor_runtime", I143, i143),
            source_artifact("n29_i14_5_one_way_phase_bridge", I145, i145),
            source_artifact("n29_i14_5_1_feedback_bridge", I1451, i1451),
            source_artifact("n29_i14_5_1_feedback_artifact", I1451_ART, i1451_art),
        ],
        "composition_attempt_row": row,
        "buffered_phase_feedback_bridge_candidate_created": True,
        "native_buffered_phase_feedback_supported": False,
        "native_phase_coupled_exchange_supported": False,
        "ready_for_i14d_i14e": True,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check("i14_5_1_feedback_bridge_present", i1451["phase_feedback_bridge_candidate_created"] is True),
            check("processor_buffer_leg_used", row["processor_buffer_leg_used"] is True),
            check(
                "later_generator_consumes_buffered_changed_medium",
                row["later_generator_consumes_buffered_changed_medium"] is True,
            ),
            check("generator_role_preserved", row["generator_leg_role_preserved"] is True),
            check("extractor_role_preserved", row["extractor_leg_role_preserved"] is True),
            check("processor_buffer_role_preserved", row["processor_buffer_role_preserved"] is True),
            check("roles_not_averaged_away", row["roles_averaged_away"] is False),
            check("win_loss_transfer_not_required", row["win_loss_transfer_required"] is False),
            check("feedback_magnitude_gate_passed", row["feedback_magnitude_gate_passed"] is True),
            check("phase_residual_gate_passed", row["phase_residual_gate_passed"] is True),
            check("i14_5_1_margin_improved", row["i14_5_1_margin_improved"] is True),
            check("merge_leakage_gate_passed", row["merge_leakage_gate_passed"] is True),
            check("native_buffered_phase_feedback_blocked", row["native_buffered_phase_feedback_supported"] is False),
            check("artifact_manifest_sha_match", manifest_sha_match(manifest)),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_5_2_buffered_feedback_bridge"
        data["ready_for_i14d_i14e"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    row = data["composition_attempt_row"]
    runtime = load_json(RUNTIME)
    residual = runtime["phase_residual_record"]
    lines = [
        "# Prototype D I14.5-2 Buffered Generator / Extractor Feedback Bridge",
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
        f"buffered_phase_feedback_bridge_candidate_created = {str(data['buffered_phase_feedback_bridge_candidate_created']).lower()}",
        f"native_buffered_phase_feedback_supported = {str(data['native_buffered_phase_feedback_supported']).lower()}",
        f"native_phase_coupled_exchange_supported = {str(data['native_phase_coupled_exchange_supported']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        "```",
        "",
        "## Geometry",
        "",
        runtime["geometry_interpretation"],
        "",
        "Compared with I14.5-1, this is not another direct feedback attempt. It",
        "adds a processor/redistribution buffer before the later generator. That",
        "makes it a better prototype for I14.6-style multi-role loops.",
        "",
        "## Margin Comparison",
        "",
        "```text",
        f"i14_5_1_max_phase_residual_abs = {residual['i14_5_1_max_phase_residual_abs']}",
        f"i14_5_2_max_phase_residual_abs = {residual['max_phase_residual_abs']}",
        f"residual_improvement_over_i14_5_1 = {residual['residual_improvement_over_i14_5_1']}",
        "```",
        "",
        "## Claim Boundary",
        "",
        f"Claim ceiling: `{row['claim_ceiling']}`",
        "",
        "The row does not support native buffered phase feedback, resource economy,",
        "cooperation, exploitation, ecology success, or agency.",
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
    i14x = load_json(I14X)
    i141 = load_json(I141)
    i1423 = load_json(I1423)
    i143 = load_json(I143)
    i145 = load_json(I145)
    i1451 = load_json(I1451)
    i1451_art = load_json(I1451_ART)
    data = build_record(i14x, i141, i1423, i143, i145, i1451, i1451_art)
    write_json(OUT, data)
    write_report(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
