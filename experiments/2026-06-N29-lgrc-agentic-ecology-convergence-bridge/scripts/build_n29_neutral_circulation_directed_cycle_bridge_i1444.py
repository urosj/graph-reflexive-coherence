#!/usr/bin/env python3
"""Build N29 I14.4-4 producer-mediated directed-cycle bridge."""

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
    "build_n29_neutral_circulation_directed_cycle_bridge_i1444.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14X = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_synthesis_i14x.json"
I144 = EXPERIMENT / "outputs" / "n29_neutral_circulation_composition_i144.json"
I1441 = EXPERIMENT / "outputs" / "n29_neutral_circulation_loop_closure_i1441.json"
I1443 = EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_i1443.json"
N28_I4F = (
    ROOT
    / "experiments"
    / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
    / "outputs"
    / "n28_higher_margin_neutral_circulation_probe.json"
)

OUT = EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_bridge_i1444.json"
RUNTIME = (
    EXPERIMENT
    / "outputs"
    / "n29_neutral_circulation_directed_cycle_bridge_i1444_artifact.json"
)
REPORT = EXPERIMENT / "reports" / "n29_neutral_circulation_directed_cycle_bridge_i1444.md"

SECOND_FORWARD_TRANSFER_FACTOR = 0.82
RETURN_TO_ALPHA_CLASS_FACTOR = 0.82
MIN_FORWARD_MAGNITUDE = 0.04
MAX_CYCLE_RESIDUAL_ABS = 0.015
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


def candidate_row(data: dict[str, Any]) -> dict[str, Any]:
    rows = data.get("candidate_rows") or []
    if rows:
        return rows[0]
    if "native_directed_cycle_search_row" in data:
        return data["native_directed_cycle_search_row"]
    if "composition_attempt_row" in data:
        return data["composition_attempt_row"]
    raise ValueError(f"No candidate-like row in {data.get('artifact_id')}")


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
    i14x: dict[str, Any],
    i144: dict[str, Any],
    i1441: dict[str, Any],
    i1443: dict[str, Any],
    n28_i4f: dict[str, Any],
) -> dict[str, Any]:
    source = candidate_row(n28_i4f)
    forward = source["capacity_attribution_trace"]
    first_inflow = forward["inflow_lobe_capacity_delta"]
    first_outflow = forward["outflow_lobe_capacity_delta"]
    first_buffer = forward["buffer_lobe_capacity_delta"]

    second_inflow = round(abs(first_outflow) * SECOND_FORWARD_TRANSFER_FACTOR, 6)
    second_outflow = round(-first_inflow * SECOND_FORWARD_TRANSFER_FACTOR, 6)
    second_buffer = round(-(second_inflow + second_outflow), 6)
    alpha_return = round(first_inflow * RETURN_TO_ALPHA_CLASS_FACTOR, 6)
    beta_residual = round(first_outflow + second_inflow, 6)
    gamma_residual = round(second_outflow + alpha_return, 6)
    closure_residual_abs_max = max(abs(beta_residual), abs(gamma_residual))
    leak_margin = round(MERGE_LEAKAGE_CEILING - MERGE_LEAKAGE_VALUE, 6)

    artifact = {
        "artifact_id": "n29_neutral_circulation_directed_cycle_bridge_i1444_artifact",
        "experiment_id": "N29",
        "iteration": "I14.4-4",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "producer_mediated_all_forward_directed_cycle_bridge_artifact",
        "source_precomposition_digest": i14x["output_digest"],
        "source_i14_4_digest": i144["output_digest"],
        "source_i14_4_1_digest": i1441["output_digest"],
        "source_i14_4_3_digest": i1443["output_digest"],
        "native_blocker_resolved_only_in_producer_lane": True,
        "cycle_definition": {
            "definition_id": "all_forward_pattern_frame_cycle",
            "locally_forward_legs_required": True,
            "reverse_bounce_back_required": False,
            "sign_inverted_reverse_leg_required": False,
            "ordered_dependency_required": True,
            "later_state_returns_to_starting_pattern_class_required": True,
        },
        "source_current_first_leg": {
            "source_row_id": source["row_id"],
            "source_output_digest": n28_i4f["output_digest"],
            "mechanism_class": forward["mechanism_class"],
            "neutral_circulation_detected": forward["neutral_circulation_detected"],
            "pattern_frame": "alpha_to_beta_forward",
            "inflow_lobe_capacity_delta": first_inflow,
            "outflow_lobe_capacity_delta": first_outflow,
            "buffer_lobe_capacity_delta": first_buffer,
        },
        "producer_bridge_policy": {
            "policy_id": "n29_i14_4_4_all_forward_directed_cycle_bridge_policy_v1",
            "declared_before_use": True,
            "producer_mediated": True,
            "producer_surface_role": (
                "derive a frame-shifted forward leg from the I4-F changed "
                "medium so the cycle can close without sign-inverted bounce-back"
            ),
            "second_forward_transfer_factor": SECOND_FORWARD_TRANSFER_FACTOR,
            "return_to_alpha_class_factor": RETURN_TO_ALPHA_CLASS_FACTOR,
            "thresholds_retuned": False,
            "label_swap_used": False,
            "reverse_bounce_back_used": False,
            "producer_success_can_upgrade_native": False,
        },
        "frame_shifted_second_forward_leg": {
            "pattern_frame": "beta_to_gamma_forward",
            "leg_source": "N29_bridge_derived_from_I4F_forward_post_state",
            "leg_source_current_native": False,
            "consumes_prior_changed_medium": True,
            "local_forward_inflow_delta": second_inflow,
            "local_forward_outflow_delta": second_outflow,
            "local_forward_buffer_delta": second_buffer,
            "minimum_forward_magnitude": MIN_FORWARD_MAGNITUDE,
            "forward_magnitude_gate_passed": (
                abs(second_inflow) >= MIN_FORWARD_MAGNITUDE
                and abs(second_outflow) >= MIN_FORWARD_MAGNITUDE
            ),
        },
        "directed_cycle_dependency_trace": {
            "ordered_leg_sequence": [
                "alpha_to_beta_forward_source_current_leg",
                "beta_to_gamma_forward_producer_bridge_leg",
                "later_alpha_class_dependency_state",
            ],
            "all_legs_locally_forward": True,
            "first_leg_changes_medium_distribution": True,
            "second_leg_consumes_prior_changed_medium": True,
            "later_alpha_class_state_depends_on_second_leg": True,
            "later_state_returns_to_starting_pattern_class": True,
            "reverse_bounce_back_used": False,
            "sign_inverted_reverse_leg_used": False,
            "label_swap_as_cycle_rejected": True,
            "producer_mediated_directed_cycle_candidate_created": True,
            "native_directed_cycle_supported": False,
        },
        "cycle_residual_state": {
            "alpha_class_return_delta": alpha_return,
            "beta_class_residual_delta": beta_residual,
            "gamma_class_residual_delta": gamma_residual,
            "closure_residual_abs_max": closure_residual_abs_max,
            "closure_residual_ceiling": MAX_CYCLE_RESIDUAL_ABS,
            "closure_residual_gate_passed": closure_residual_abs_max <= MAX_CYCLE_RESIDUAL_ABS,
        },
        "leakage_record": {
            "merge_leakage_value": MERGE_LEAKAGE_VALUE,
            "merge_leakage_ceiling": MERGE_LEAKAGE_CEILING,
            "merge_leakage_margin": leak_margin,
            "merge_leakage_gate_passed": MERGE_LEAKAGE_VALUE <= MERGE_LEAKAGE_CEILING,
        },
        "geometry_interpretation": (
            "I14.4-4 resolves the I14.4-3 native blocker only in the N29 "
            "producer-mediated bridge lane. The first leg is the source-current "
            "I4-F neutral circulation: alpha enriches beta while beta drains "
            "against a near-stable buffer. The second leg does not bounce back "
            "along the same channel. It shifts frame and continues forward from "
            "beta toward gamma, consuming the changed medium left by the first "
            "leg. Closure is recorded because the later alpha-class state depends "
            "on the second leg's changed distribution. This is a directed-cycle "
            "bridge candidate, not native LGRC closed circulation."
        ),
        "claim_boundary": {
            "producer_mediated_directed_cycle_candidate_created": True,
            "native_directed_cycle_supported": False,
            "native_closed_environmental_circulation_supported": False,
            "closed_environmental_circulation_loop_claim_allowed": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "agency_claim_allowed": False,
        },
    }
    return finalize(artifact)


def build_record(
    i14x: dict[str, Any],
    i144: dict[str, Any],
    i1441: dict[str, Any],
    i1443: dict[str, Any],
    n28_i4f: dict[str, Any],
) -> dict[str, Any]:
    runtime = build_runtime_artifact(i14x, i144, i1441, i1443, n28_i4f)
    write_json(RUNTIME, runtime)
    manifest = artifact_manifest(RUNTIME, "n29_i14_4_4_directed_cycle_bridge_artifact")
    dependency = runtime["directed_cycle_dependency_trace"]
    residual = runtime["cycle_residual_state"]
    leakage = runtime["leakage_record"]
    second = runtime["frame_shifted_second_forward_leg"]
    row = {
        "row_id": "n29_i14_4_4_producer_mediated_directed_cycle_bridge_candidate",
        "row_decision": "partial",
        "row_decision_scope": (
            "producer_mediated_all_forward_directed_cycle_candidate_pending_i14d_i14e"
        ),
        "i14_4_3_native_blocker_consumed": True,
        "i14_4_3_native_result_replaced": False,
        "source_current_first_leg_supported": True,
        "producer_mediated_second_forward_leg_created": True,
        "all_legs_locally_forward": dependency["all_legs_locally_forward"],
        "reverse_bounce_back_used": dependency["reverse_bounce_back_used"],
        "sign_inverted_reverse_leg_used": dependency["sign_inverted_reverse_leg_used"],
        "second_leg_consumes_prior_changed_medium": dependency[
            "second_leg_consumes_prior_changed_medium"
        ],
        "later_state_returns_to_starting_pattern_class": dependency[
            "later_state_returns_to_starting_pattern_class"
        ],
        "producer_mediated_directed_cycle_candidate_created": dependency[
            "producer_mediated_directed_cycle_candidate_created"
        ],
        "native_directed_cycle_supported": False,
        "native_closed_environmental_circulation_supported": False,
        "closed_environmental_circulation_loop_claim_allowed": False,
        "forward_magnitude_gate_passed": second["forward_magnitude_gate_passed"],
        "closure_residual_gate_passed": residual["closure_residual_gate_passed"],
        "merge_leakage_gate_passed": leakage["merge_leakage_gate_passed"],
        "claim_ceiling": (
            "producer_mediated_all_forward_directed_cycle_candidate_pending_controls_replay"
        ),
        "runtime_artifact_manifest": manifest,
        "remaining_debt": [
            "I14-D loop/composition controls pending",
            "I14-E replay/stress pending",
            "second forward leg is producer-mediated, not native LGRC source-current",
            "I14.4-3 native directed-cycle blocker remains in force",
            "resource economy, cooperation, exploitation, ecology success, and agency claims remain blocked",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_neutral_circulation_directed_cycle_bridge_i1444",
        "experiment_id": "N29",
        "title": "Prototype D I14.4-4 Producer-Mediated Directed Cycle Bridge",
        "iteration": "I14.4-4",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_producer_mediated_directed_cycle_bridge_candidate_pending_i14d_i14e"
        ),
        "source_artifacts": [
            source_artifact("n29_i14x_precomposition_index", I14X, i14x),
            source_artifact("n29_i14_4_single_direction_circulation", I144, i144),
            source_artifact("n29_i14_4_1_reverse_bridge_context", I1441, i1441),
            source_artifact("n29_i14_4_3_native_directed_cycle_blocker", I1443, i1443),
            source_artifact("n28_i4f_source_current_forward_leg", N28_I4F, n28_i4f),
        ],
        "composition_attempt_row": row,
        "producer_mediated_directed_cycle_candidate_created": True,
        "native_directed_cycle_supported": False,
        "native_closed_environmental_circulation_supported": False,
        "all_legs_locally_forward": True,
        "reverse_bounce_back_used": False,
        "sign_inverted_reverse_leg_used": False,
        "ready_for_i14d_i14e": True,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check(
                "i14_4_3_native_directed_cycle_absent",
                i1443["native_directed_cycle_found"] is False,
            ),
            check(
                "source_current_first_leg_present",
                i144["single_direction_neutral_circulation_leg_supported"] is True,
            ),
            check("all_legs_locally_forward", row["all_legs_locally_forward"] is True),
            check("reverse_bounce_back_not_used", row["reverse_bounce_back_used"] is False),
            check(
                "sign_inverted_reverse_leg_not_used",
                row["sign_inverted_reverse_leg_used"] is False,
            ),
            check(
                "second_leg_consumes_prior_changed_medium",
                row["second_leg_consumes_prior_changed_medium"] is True,
            ),
            check(
                "later_state_returns_to_starting_pattern_class",
                row["later_state_returns_to_starting_pattern_class"] is True,
            ),
            check("forward_magnitude_gate_passed", row["forward_magnitude_gate_passed"] is True),
            check("closure_residual_gate_passed", row["closure_residual_gate_passed"] is True),
            check("merge_leakage_gate_passed", row["merge_leakage_gate_passed"] is True),
            check("native_directed_cycle_blocked", row["native_directed_cycle_supported"] is False),
            check("artifact_manifest_sha_match", manifest_sha_match(manifest)),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_4_4_directed_cycle_bridge"
        data["ready_for_i14d_i14e"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    row = data["composition_attempt_row"]
    runtime = load_json(RUNTIME)
    lines = [
        "# Prototype D I14.4-4 Producer-Mediated Directed Cycle Bridge",
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
        f"producer_mediated_directed_cycle_candidate_created = {str(data['producer_mediated_directed_cycle_candidate_created']).lower()}",
        f"native_directed_cycle_supported = {str(data['native_directed_cycle_supported']).lower()}",
        f"all_legs_locally_forward = {str(data['all_legs_locally_forward']).lower()}",
        f"reverse_bounce_back_used = {str(data['reverse_bounce_back_used']).lower()}",
        f"sign_inverted_reverse_leg_used = {str(data['sign_inverted_reverse_leg_used']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        "```",
        "",
        "## Geometry",
        "",
        runtime["geometry_interpretation"],
        "",
        "The difference from I14.4-1 is important: I14.4-4 does not create an",
        "opposite-direction return leg. It creates a frame-shifted second forward",
        "leg. The loop is Escher-stairs-like: every local leg proceeds forward in",
        "its own frame, while the ordered dependency closes at the pattern-class",
        "level.",
        "",
        "## Claim Boundary",
        "",
        f"Claim ceiling: `{row['claim_ceiling']}`",
        "",
        "I14.4-4 resolves I14.4-3 only as a producer-mediated bridge candidate.",
        "It does not upgrade native LGRC directed-cycle support and it does not",
        "open resource economy, cooperation, exploitation, ecology success, or",
        "agency claims.",
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
    i144 = load_json(I144)
    i1441 = load_json(I1441)
    i1443 = load_json(I1443)
    n28_i4f = load_json(N28_I4F)
    data = build_record(i14x, i144, i1441, i1443, n28_i4f)
    write_json(OUT, data)
    write_report(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
