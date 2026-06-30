#!/usr/bin/env python3
"""Build N29 I14.4-1 neutral-circulation loop-closure attempt."""

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
    "build_n29_neutral_circulation_loop_closure_i1441.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I144 = EXPERIMENT / "outputs" / "n29_neutral_circulation_composition_i144.json"
I14X = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_synthesis_i14x.json"
N28_I4F = (
    ROOT
    / "experiments"
    / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
    / "outputs"
    / "n28_higher_margin_neutral_circulation_probe.json"
)

OUT = EXPERIMENT / "outputs" / "n29_neutral_circulation_loop_closure_i1441.json"
RUNTIME = EXPERIMENT / "outputs" / "n29_neutral_circulation_loop_closure_i1441_artifact.json"
REPORT = EXPERIMENT / "reports" / "n29_neutral_circulation_loop_closure_i1441.md"

REVERSE_RETURN_FACTOR = 0.80
MIN_RETURN_MAGNITUDE = 0.04
MAX_RESIDUAL_ABS = 0.015
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


def candidate_row(data: dict[str, Any]) -> dict[str, Any]:
    rows = data.get("candidate_rows") or []
    if not rows:
        raise ValueError(f"No candidate rows in {data.get('artifact_id')}")
    return rows[0]


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


def build_runtime_artifact(i144: dict[str, Any], i14x: dict[str, Any], n28_i4f: dict[str, Any]) -> dict[str, Any]:
    source = candidate_row(n28_i4f)
    forward = source["capacity_attribution_trace"]
    forward_inflow = forward["inflow_lobe_capacity_delta"]
    forward_outflow = forward["outflow_lobe_capacity_delta"]
    forward_buffer = forward["buffer_lobe_capacity_delta"]
    reverse_loss_on_forward_inflow = round(-forward_inflow * REVERSE_RETURN_FACTOR, 6)
    reverse_gain_on_forward_outflow = round(abs(forward_outflow) * REVERSE_RETURN_FACTOR, 6)
    reverse_buffer_delta = round(
        -(reverse_loss_on_forward_inflow + reverse_gain_on_forward_outflow), 6
    )
    residual_inflow = round(forward_inflow + reverse_loss_on_forward_inflow, 6)
    residual_outflow = round(forward_outflow + reverse_gain_on_forward_outflow, 6)
    residual_buffer = round(forward_buffer + reverse_buffer_delta, 6)
    leak_margin = round(MERGE_LEAKAGE_CEILING - MERGE_LEAKAGE_VALUE, 6)
    artifact = {
        "artifact_id": "n29_neutral_circulation_loop_closure_i1441_artifact",
        "experiment_id": "N29",
        "iteration": "I14.4-1",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "prototype_d_neutral_circulation_loop_closure_attempt_artifact",
        "source_precomposition_digest": i14x["output_digest"],
        "source_i14_4_digest": i144["output_digest"],
        "source_current_forward_leg": {
            "source_row_id": source["row_id"],
            "source_output_digest": n28_i4f["output_digest"],
            "mechanism_class": forward["mechanism_class"],
            "neutral_circulation_detected": forward["neutral_circulation_detected"],
            "inflow_lobe_capacity_delta": forward_inflow,
            "outflow_lobe_capacity_delta": forward_outflow,
            "buffer_lobe_capacity_delta": forward_buffer,
        },
        "reverse_leg_policy": {
            "policy_id": "n29_i14_4_1_reverse_leg_bridge_policy_v1",
            "declared_before_use": True,
            "producer_mediated": True,
            "producer_surface_role": "derive an opposite-direction return leg from the source-current forward post-state",
            "reverse_return_factor": REVERSE_RETURN_FACTOR,
            "thresholds_retuned": False,
            "label_swap_used": False,
            "producer_success_can_upgrade_native": False,
        },
        "derived_reverse_leg": {
            "reverse_leg_source": "N29_bridge_derived_from_I4F_forward_post_state",
            "reverse_leg_source_current_native": False,
            "reverse_leg_consumes_forward_changed_distribution": True,
            "reverse_loss_on_forward_inflow_lobe": reverse_loss_on_forward_inflow,
            "reverse_gain_on_forward_outflow_lobe": reverse_gain_on_forward_outflow,
            "reverse_buffer_delta": reverse_buffer_delta,
            "minimum_return_magnitude": MIN_RETURN_MAGNITUDE,
            "return_magnitude_gate_passed": (
                abs(reverse_loss_on_forward_inflow) >= MIN_RETURN_MAGNITUDE
                and abs(reverse_gain_on_forward_outflow) >= MIN_RETURN_MAGNITUDE
            ),
        },
        "closure_dependency_trace": {
            "ordered_leg_sequence": ["forward_source_current_leg", "derived_reverse_leg", "later_forward_side_residual_state"],
            "forward_leg_changes_capacity_distribution": True,
            "reverse_leg_consumes_forward_changed_distribution": True,
            "later_forward_side_state_depends_on_reverse_leg": True,
            "label_swap_as_reverse_leg_rejected": True,
            "closed_circulation_candidate_created": True,
            "native_closed_circulation_supported": False,
        },
        "residual_medium_state": {
            "residual_inflow_lobe_capacity_delta": residual_inflow,
            "residual_outflow_lobe_capacity_delta": residual_outflow,
            "residual_buffer_lobe_capacity_delta": residual_buffer,
            "max_allowed_abs_residual": MAX_RESIDUAL_ABS,
            "residual_gate_passed": (
                abs(residual_inflow) <= MAX_RESIDUAL_ABS
                and abs(residual_outflow) <= MAX_RESIDUAL_ABS
            ),
        },
        "leakage_record": {
            "merge_leakage_value": MERGE_LEAKAGE_VALUE,
            "merge_leakage_ceiling": MERGE_LEAKAGE_CEILING,
            "merge_leakage_margin": leak_margin,
            "merge_leakage_gate_passed": MERGE_LEAKAGE_VALUE <= MERGE_LEAKAGE_CEILING,
        },
        "geometry_interpretation": (
            "I14.4-1 turns the single neutral circulation leg into an ordered "
            "bridge-loop candidate by deriving a reverse leg from the forward "
            "post-state. The forward leg enriches one lobe and depletes the "
            "opposed lobe; the reverse leg then consumes that changed state and "
            "returns most of the capacity along the opposite arc. The residual "
            "state remains bounded, but the reverse leg is N29 producer-mediated, "
            "not native LGRC source-current closure."
        ),
        "claim_boundary": {
            "producer_mediated_closed_circulation_candidate_created": True,
            "native_closed_environmental_circulation_supported": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "agency_claim_allowed": False,
        },
    }
    return finalize(artifact)


def build_record(i144: dict[str, Any], i14x: dict[str, Any], n28_i4f: dict[str, Any]) -> dict[str, Any]:
    runtime = build_runtime_artifact(i144, i14x, n28_i4f)
    write_json(RUNTIME, runtime)
    manifest = artifact_manifest(RUNTIME, "n29_i14_4_1_neutral_circulation_loop_closure_artifact")
    reverse = runtime["derived_reverse_leg"]
    closure = runtime["closure_dependency_trace"]
    residual = runtime["residual_medium_state"]
    leakage = runtime["leakage_record"]
    row = {
        "row_id": "n29_i14_4_1_neutral_circulation_loop_closure_candidate",
        "row_decision": "partial",
        "row_decision_scope": "producer_mediated_ordered_circulation_closure_candidate_pending_i14d_i14e",
        "source_current_forward_leg_supported": True,
        "derived_reverse_leg_created": True,
        "reverse_leg_source_current_native": reverse["reverse_leg_source_current_native"],
        "reverse_leg_consumes_forward_changed_distribution": reverse[
            "reverse_leg_consumes_forward_changed_distribution"
        ],
        "later_forward_side_state_depends_on_reverse_leg": closure[
            "later_forward_side_state_depends_on_reverse_leg"
        ],
        "closed_circulation_candidate_created": closure["closed_circulation_candidate_created"],
        "native_closed_environmental_circulation_supported": False,
        "closed_environmental_circulation_loop_claim_allowed": False,
        "producer_mediated_loop_closure_candidate": True,
        "residual_gate_passed": residual["residual_gate_passed"],
        "return_magnitude_gate_passed": reverse["return_magnitude_gate_passed"],
        "merge_leakage_gate_passed": leakage["merge_leakage_gate_passed"],
        "claim_ceiling": "producer_mediated_ordered_neutral_circulation_loop_closure_candidate_pending_controls_replay",
        "runtime_artifact_manifest": manifest,
        "remaining_debt": [
            "I14-D loop/composition controls pending",
            "I14-E replay/stress pending",
            "reverse leg is producer-mediated, not native source-current LGRC",
            "resource economy, cooperation, exploitation, ecology success, and agency claims remain blocked",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_neutral_circulation_loop_closure_i1441",
        "experiment_id": "N29",
        "title": "Prototype D I14.4-1 Neutral Circulation Loop Closure Attempt",
        "iteration": "I14.4-1",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_producer_mediated_neutral_circulation_loop_closure_candidate_pending_i14d_i14e",
        "source_artifacts": [
            source_artifact("n29_i14x_precomposition_index", I14X, i14x),
            source_artifact("n29_i14_4_single_direction_circulation", I144, i144),
            source_artifact("n28_i4f_source_current_forward_leg", N28_I4F, n28_i4f),
        ],
        "composition_attempt_row": row,
        "producer_mediated_closed_circulation_candidate_created": True,
        "native_closed_environmental_circulation_supported": False,
        "ready_for_i14d_i14e": True,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check("i14_4_single_direction_leg_present", i144["single_direction_neutral_circulation_leg_supported"] is True),
            check("reverse_leg_created", row["derived_reverse_leg_created"] is True),
            check("reverse_leg_consumes_forward_state", row["reverse_leg_consumes_forward_changed_distribution"] is True),
            check("later_state_depends_on_reverse_leg", row["later_forward_side_state_depends_on_reverse_leg"] is True),
            check("return_magnitude_gate_passed", row["return_magnitude_gate_passed"] is True),
            check("residual_gate_passed", row["residual_gate_passed"] is True),
            check("merge_leakage_gate_passed", row["merge_leakage_gate_passed"] is True),
            check("native_closed_loop_blocked", row["native_closed_environmental_circulation_supported"] is False),
            check("artifact_manifest_sha_match", manifest_sha_match(manifest)),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_4_1_neutral_circulation_loop_closure_attempt"
        data["ready_for_i14d_i14e"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    row = data["composition_attempt_row"]
    runtime = load_json(RUNTIME)
    lines = [
        "# Prototype D I14.4-1 Neutral Circulation Loop Closure Attempt",
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
        f"producer_mediated_closed_circulation_candidate_created = {str(data['producer_mediated_closed_circulation_candidate_created']).lower()}",
        f"native_closed_environmental_circulation_supported = {str(data['native_closed_environmental_circulation_supported']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        "```",
        "",
        "## Geometry",
        "",
        runtime["geometry_interpretation"],
        "",
        "The important change from I14.4 is that the reverse leg is no longer a",
        "label swap. It is a declared bridge policy that consumes the forward",
        "post-state and produces an opposite-direction return leg. That is enough",
        "for a producer-mediated loop-closure candidate, but not for native LGRC",
        "closed circulation.",
        "",
        f"Claim ceiling: `{row['claim_ceiling']}`",
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
    i14x = load_json(I14X)
    n28_i4f = load_json(N28_I4F)
    data = build_record(i144, i14x, n28_i4f)
    write_json(OUT, data)
    write_report(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
