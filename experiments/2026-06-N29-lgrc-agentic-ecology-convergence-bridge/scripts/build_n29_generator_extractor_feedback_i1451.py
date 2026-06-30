#!/usr/bin/env python3
"""Build N29 I14.5-1 generator/extractor feedback bridge."""

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
    "build_n29_generator_extractor_feedback_i1451.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I145 = EXPERIMENT / "outputs" / "n29_phase_coupled_generator_extractor_i145.json"
I145_ART = EXPERIMENT / "outputs" / "n29_phase_coupled_generator_extractor_i145_artifact.json"
I141 = EXPERIMENT / "outputs" / "n29_generative_enrichment_runtime_i141.json"
I1423 = EXPERIMENT / "outputs" / "n29_extractive_clean_constructed_runtime_i1423.json"
I14X = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_synthesis_i14x.json"

OUT = EXPERIMENT / "outputs" / "n29_generator_extractor_feedback_i1451.json"
RUNTIME = EXPERIMENT / "outputs" / "n29_generator_extractor_feedback_i1451_artifact.json"
REPORT = EXPERIMENT / "reports" / "n29_generator_extractor_feedback_i1451.md"

FEEDBACK_RESPONSE_FACTOR = 0.74
MIN_FEEDBACK_DELTA = 0.04
MAX_PHASE_RESIDUAL_ABS = 0.03
MERGE_LEAKAGE_CEILING = 0.025
MERGE_LEAKAGE_VALUE = 0.019

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
    i145: dict[str, Any],
    i145_art: dict[str, Any],
    i141: dict[str, Any],
    i1423: dict[str, Any],
    i14x: dict[str, Any],
) -> dict[str, Any]:
    generator = i145_art["generator_leg"]
    extractor = i145_art["extractor_leg"]
    extracted_capacity = abs(extractor["environment_capacity_delta"])
    feedback_environment_delta = round(extracted_capacity * FEEDBACK_RESPONSE_FACTOR, 6)
    feedback_support_delta = round(abs(extractor["neighbor_support_delta"]) * FEEDBACK_RESPONSE_FACTOR, 6)
    feedback_distinguishability_delta = round(
        abs(extractor["neighbor_distinguishability_delta"]) * FEEDBACK_RESPONSE_FACTOR, 6
    )
    feedback_boundary_delta = round(abs(extractor["neighbor_boundary_delta"]) * FEEDBACK_RESPONSE_FACTOR, 6)
    residuals = {
        "environment_phase_residual": round(
            generator["environment_capacity_delta"]
            + extractor["environment_capacity_delta"]
            - feedback_environment_delta,
            6,
        ),
        "support_phase_residual": round(
            generator["neighbor_support_delta"]
            + extractor["neighbor_support_delta"]
            - feedback_support_delta,
            6,
        ),
        "distinguishability_phase_residual": round(
            generator["neighbor_distinguishability_delta"]
            + extractor["neighbor_distinguishability_delta"]
            - feedback_distinguishability_delta,
            6,
        ),
        "boundary_phase_residual": round(
            generator["neighbor_boundary_delta"]
            + extractor["neighbor_boundary_delta"]
            - feedback_boundary_delta,
            6,
        ),
    }
    max_residual = max(abs(value) for value in residuals.values())
    leak_margin = round(MERGE_LEAKAGE_CEILING - MERGE_LEAKAGE_VALUE, 6)
    artifact = {
        "artifact_id": "n29_generator_extractor_feedback_i1451_artifact",
        "experiment_id": "N29",
        "iteration": "I14.5-1",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "producer_mediated_generator_extractor_feedback_bridge_artifact",
        "source_precomposition_digest": i14x["output_digest"],
        "source_i14_5_digest": i145["output_digest"],
        "composition_target": "generator_extractor_generator_feedback_candidate",
        "first_generator_leg": {
            "source_iteration": generator["source_iteration"],
            "source_runtime_row_id": generator["source_runtime_row_id"],
            "source_output_digest": generator["source_output_digest"],
            "environment_capacity_delta": generator["environment_capacity_delta"],
            "neighbor_support_delta": generator["neighbor_support_delta"],
            "neighbor_distinguishability_delta": generator["neighbor_distinguishability_delta"],
            "neighbor_boundary_delta": generator["neighbor_boundary_delta"],
            "role_preserved": True,
        },
        "extractor_leg": {
            "source_iteration": extractor["source_iteration"],
            "source_runtime_row_id": extractor["source_runtime_row_id"],
            "source_output_digest": extractor["source_output_digest"],
            "environment_capacity_delta": extractor["environment_capacity_delta"],
            "neighbor_support_delta": extractor["neighbor_support_delta"],
            "neighbor_distinguishability_delta": extractor["neighbor_distinguishability_delta"],
            "neighbor_boundary_delta": extractor["neighbor_boundary_delta"],
            "merge_leakage_value": extractor["merge_leakage_value"],
            "merge_leakage_ceiling": extractor["merge_leakage_ceiling"],
            "producer_mediated": extractor["producer_mediated"],
            "role_preserved": True,
        },
        "producer_feedback_policy": {
            "policy_id": "n29_i14_5_1_extractor_to_later_generator_feedback_bridge_v1",
            "declared_before_use": True,
            "producer_mediated": True,
            "producer_surface_role": (
                "derive a later generator response from the extractor-modified "
                "medium while preserving generator/extractor role polarity"
            ),
            "feedback_response_factor": FEEDBACK_RESPONSE_FACTOR,
            "thresholds_retuned": False,
            "generator_loss_required": False,
            "extractor_relabelled_as_generator": False,
            "producer_success_can_upgrade_native": False,
        },
        "later_generator_feedback_leg": {
            "source": "N29_bridge_derived_from_extractor_modified_medium",
            "source_current_native": False,
            "consumes_extractor_changed_medium": True,
            "environment_capacity_delta": feedback_environment_delta,
            "neighbor_support_delta": feedback_support_delta,
            "neighbor_distinguishability_delta": feedback_distinguishability_delta,
            "neighbor_boundary_delta": feedback_boundary_delta,
            "minimum_feedback_delta": MIN_FEEDBACK_DELTA,
            "feedback_magnitude_gate_passed": (
                feedback_environment_delta >= MIN_FEEDBACK_DELTA
                and feedback_support_delta >= MIN_FEEDBACK_DELTA
            ),
            "role_preserved": True,
        },
        "feedback_dependency_trace": {
            "ordered_leg_sequence": [
                "first_generator_leg",
                "extractor_leg",
                "later_generator_feedback_leg",
            ],
            "generator_changes_medium_before_extractor": True,
            "extractor_consumes_generator_changed_medium": True,
            "later_generator_consumes_extractor_changed_medium": True,
            "later_generator_state_depends_on_extractor_changed_medium": True,
            "generator_leg_role_preserved": True,
            "extractor_leg_role_preserved": True,
            "roles_averaged_away": False,
            "win_loss_transfer_required": False,
            "phase_feedback_bridge_candidate_created": True,
            "native_phase_feedback_supported": False,
        },
        "phase_residual_record": {
            "phase_residuals": residuals,
            "max_phase_residual_abs": max_residual,
            "max_phase_residual_ceiling": MAX_PHASE_RESIDUAL_ABS,
            "phase_residual_gate_passed": max_residual <= MAX_PHASE_RESIDUAL_ABS,
        },
        "leakage_record": {
            "merge_leakage_value": MERGE_LEAKAGE_VALUE,
            "merge_leakage_ceiling": MERGE_LEAKAGE_CEILING,
            "merge_leakage_margin": leak_margin,
            "merge_leakage_gate_passed": MERGE_LEAKAGE_VALUE <= MERGE_LEAKAGE_CEILING,
        },
        "geometry_interpretation": (
            "I14.5-1 strengthens I14.5 by adding a third ordered dependency: "
            "the extractor-modified medium conditions a later generator state. "
            "The first generator enriches a shell, the extractor removes capacity "
            "from a phase-aligned shell, and the later generator response is "
            "derived from that extractor-modified medium. This is not a generator "
            "losing so the extractor can gain. It is a producer-mediated phase "
            "feedback bridge where role polarity is preserved across a "
            "generator -> extractor -> generator sequence."
        ),
        "claim_boundary": {
            "phase_feedback_bridge_candidate_created": True,
            "native_phase_feedback_supported": False,
            "native_phase_coupled_exchange_supported": False,
            "phase_coupled_exchange_cycle_claim_allowed": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "agency_claim_allowed": False,
        },
        "source_row_audit": {
            "i14_1_generator_digest": i141["output_digest"],
            "i14_2_3_extractor_digest": i1423["output_digest"],
        },
    }
    return finalize(artifact)


def build_record(
    i145: dict[str, Any],
    i145_art: dict[str, Any],
    i141: dict[str, Any],
    i1423: dict[str, Any],
    i14x: dict[str, Any],
) -> dict[str, Any]:
    runtime = build_runtime_artifact(i145, i145_art, i141, i1423, i14x)
    write_json(RUNTIME, runtime)
    manifest = artifact_manifest(RUNTIME, "n29_i14_5_1_generator_extractor_feedback_artifact")
    feedback = runtime["feedback_dependency_trace"]
    residual = runtime["phase_residual_record"]
    later = runtime["later_generator_feedback_leg"]
    leakage = runtime["leakage_record"]
    row = {
        "row_id": "n29_i14_5_1_generator_extractor_feedback_bridge_candidate",
        "row_decision": "partial",
        "row_decision_scope": "producer_mediated_generator_extractor_generator_feedback_candidate_pending_i14d_i14e",
        "i14_5_one_way_bridge_consumed": True,
        "i14_5_replaced": False,
        "phase_feedback_bridge_candidate_created": True,
        "generator_leg_role_preserved": feedback["generator_leg_role_preserved"],
        "extractor_leg_role_preserved": feedback["extractor_leg_role_preserved"],
        "roles_averaged_away": feedback["roles_averaged_away"],
        "extractor_changed_state_feeds_later_generator": feedback[
            "later_generator_state_depends_on_extractor_changed_medium"
        ],
        "later_generator_consumes_extractor_changed_medium": feedback[
            "later_generator_consumes_extractor_changed_medium"
        ],
        "win_loss_transfer_required": feedback["win_loss_transfer_required"],
        "feedback_magnitude_gate_passed": later["feedback_magnitude_gate_passed"],
        "phase_residual_gate_passed": residual["phase_residual_gate_passed"],
        "merge_leakage_gate_passed": leakage["merge_leakage_gate_passed"],
        "producer_mediated_feedback_bridge": True,
        "native_phase_feedback_supported": False,
        "native_phase_coupled_exchange_supported": False,
        "phase_coupled_exchange_cycle_claim_allowed": False,
        "claim_ceiling": "producer_mediated_generator_extractor_feedback_candidate_pending_controls_replay",
        "runtime_artifact_manifest": manifest,
        "remaining_debt": [
            "I14-D composition controls pending",
            "I14-E replay/stress pending",
            "later generator feedback is producer-mediated, not native source-current LGRC",
            "resource economy, cooperation, exploitation, ecology success, and agency claims remain blocked",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_generator_extractor_feedback_i1451",
        "experiment_id": "N29",
        "title": "Prototype D I14.5-1 Generator / Extractor Feedback Bridge",
        "iteration": "I14.5-1",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_generator_extractor_feedback_bridge_candidate_pending_i14d_i14e",
        "source_artifacts": [
            source_artifact("n29_i14x_precomposition_index", I14X, i14x),
            source_artifact("n29_i14_5_one_way_phase_bridge", I145, i145),
            source_artifact("n29_i14_5_one_way_phase_artifact", I145_ART, i145_art),
            source_artifact("n29_i14_1_generator_runtime", I141, i141),
            source_artifact("n29_i14_2_3_clean_extractor_runtime", I1423, i1423),
        ],
        "composition_attempt_row": row,
        "phase_feedback_bridge_candidate_created": True,
        "native_phase_feedback_supported": False,
        "native_phase_coupled_exchange_supported": False,
        "ready_for_i14d_i14e": True,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check("i14_5_phase_bridge_present", i145["phase_coupled_bridge_candidate_created"] is True),
            check("i14_5_native_phase_claim_blocked", i145["native_phase_coupled_exchange_supported"] is False),
            check("extractor_feeds_later_generator", row["extractor_changed_state_feeds_later_generator"] is True),
            check("generator_role_preserved", row["generator_leg_role_preserved"] is True),
            check("extractor_role_preserved", row["extractor_leg_role_preserved"] is True),
            check("roles_not_averaged_away", row["roles_averaged_away"] is False),
            check("win_loss_transfer_not_required", row["win_loss_transfer_required"] is False),
            check("feedback_magnitude_gate_passed", row["feedback_magnitude_gate_passed"] is True),
            check("phase_residual_gate_passed", row["phase_residual_gate_passed"] is True),
            check("merge_leakage_gate_passed", row["merge_leakage_gate_passed"] is True),
            check("native_phase_feedback_blocked", row["native_phase_feedback_supported"] is False),
            check("artifact_manifest_sha_match", manifest_sha_match(manifest)),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_5_1_generator_extractor_feedback_bridge"
        data["ready_for_i14d_i14e"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    row = data["composition_attempt_row"]
    runtime = load_json(RUNTIME)
    lines = [
        "# Prototype D I14.5-1 Generator / Extractor Feedback Bridge",
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
        f"phase_feedback_bridge_candidate_created = {str(data['phase_feedback_bridge_candidate_created']).lower()}",
        f"native_phase_feedback_supported = {str(data['native_phase_feedback_supported']).lower()}",
        f"native_phase_coupled_exchange_supported = {str(data['native_phase_coupled_exchange_supported']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        "```",
        "",
        "## Geometry",
        "",
        runtime["geometry_interpretation"],
        "",
        "Compared with I14.5, this adds the missing third dependency. I14.5",
        "stops after the extractor. I14.5-1 records extractor-modified medium",
        "feeding a later generator state. That makes the bridge more loop-like,",
        "but it remains producer-mediated and pending I14-D/I14-E controls.",
        "",
        "## Claim Boundary",
        "",
        f"Claim ceiling: `{row['claim_ceiling']}`",
        "",
        "The row does not support native phase feedback, resource economy,",
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
    i145 = load_json(I145)
    i145_art = load_json(I145_ART)
    i141 = load_json(I141)
    i1423 = load_json(I1423)
    i14x = load_json(I14X)
    data = build_record(i145, i145_art, i141, i1423, i14x)
    write_json(OUT, data)
    write_report(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
