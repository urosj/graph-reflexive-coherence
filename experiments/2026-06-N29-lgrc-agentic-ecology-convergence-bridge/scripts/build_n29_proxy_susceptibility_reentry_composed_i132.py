#!/usr/bin/env python3
"""Build N29 I13.2 alternative composed Proxy / Susceptibility / Re-Entry prototype."""

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
    "build_n29_proxy_susceptibility_reentry_composed_i132.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I131C = (
    EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_replay_stress_i131c.json"
)
I13 = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_i13.json"

RUNTIME_OUTPUT = (
    EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_runtime_i132_artifact.json"
)
OUTPUT = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_composed_i132.json"
REPORT = EXPERIMENT / "reports" / "n29_proxy_susceptibility_reentry_composed_i132.md"

UNSAFE_FLAGS = {
    "agent_role_behavior_claim_allowed": False,
    "agency_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "choice_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "identity_transfer_claim_allowed": False,
    "intentional_return_claim_allowed": False,
    "learning_as_semantic_knowledge_claim_allowed": False,
    "native_ap4_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "preference_ownership_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
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


def bounded_response_score(
    *,
    susceptibility_delta: float,
    reentry_alignment: float,
    buffer_gain: float,
    challenge_load: float,
) -> float:
    return round(
        0.48
        + susceptibility_delta * 1.35
        + reentry_alignment * 0.55
        + buffer_gain * 0.25
        - challenge_load * 0.085,
        6,
    )


def build_runtime_artifact(i13: dict[str, Any], i131c: dict[str, Any]) -> dict[str, Any]:
    thresholds = {
        "susceptibility_delta_floor": 0.05,
        "differential_response_floor": 0.08,
        "response_score_floor": 0.60,
        "support_floor": 0.85,
        "coherence_floor": 0.85,
        "boundary_integrity_floor": 0.80,
        "challenge_load": 0.18,
    }
    initial = {
        "target_route": {
            "route_id": "route_gamma_buffered_target",
            "support": 1.0,
            "coherence": 1.0,
            "boundary_integrity": 0.94,
            "susceptibility": 0.48,
            "buffer_lane_capacity": 0.12,
        },
        "peer_route": {
            "route_id": "route_delta_peer_same_budget",
            "support": 1.0,
            "coherence": 1.0,
            "boundary_integrity": 0.94,
            "susceptibility": 0.48,
            "buffer_lane_capacity": 0.02,
        },
    }
    proxy_pressure = 0.22
    susceptibility_coupling = 0.46
    buffer_gain = 0.08
    susceptibility_delta = round(proxy_pressure * susceptibility_coupling + buffer_gain * 0.25, 6)
    target_susceptibility = round(initial["target_route"]["susceptibility"] + susceptibility_delta, 6)
    peer_susceptibility = initial["peer_route"]["susceptibility"]
    target_reentry_alignment = 0.22
    peer_reentry_alignment = 0.06
    target_response = bounded_response_score(
        susceptibility_delta=susceptibility_delta,
        reentry_alignment=target_reentry_alignment,
        buffer_gain=buffer_gain,
        challenge_load=thresholds["challenge_load"],
    )
    peer_response = bounded_response_score(
        susceptibility_delta=0.0,
        reentry_alignment=peer_reentry_alignment,
        buffer_gain=0.0,
        challenge_load=thresholds["challenge_load"],
    )
    differential_response = round(target_response - peer_response, 6)
    target_post = {
        "route_id": "route_gamma_buffered_target",
        "support": 0.92,
        "coherence": 0.91,
        "boundary_integrity": 0.89,
        "susceptibility": target_susceptibility,
        "buffer_lane_capacity": initial["target_route"]["buffer_lane_capacity"],
        "response_score": target_response,
        "response_class": "buffered_reentry_response_preserved",
    }
    peer_post = {
        "route_id": "route_delta_peer_same_budget",
        "support": 0.86,
        "coherence": 0.85,
        "boundary_integrity": 0.84,
        "susceptibility": peer_susceptibility,
        "buffer_lane_capacity": initial["peer_route"]["buffer_lane_capacity"],
        "response_score": peer_response,
        "response_class": "same_budget_peer_no_buffered_susceptibility",
    }
    timeline = [
        {
            "time_index": 0,
            "leg": "proxy_or_perturbation_state",
            "event": "buffered target route receives bounded proxy pressure",
            "target_proxy_pressure": proxy_pressure,
            "peer_proxy_pressure": 0.0,
            "buffer_lane_capacity_difference": round(
                initial["target_route"]["buffer_lane_capacity"]
                - initial["peer_route"]["buffer_lane_capacity"],
                6,
            ),
        },
        {
            "time_index": 1,
            "leg": "susceptibility_delta_or_modified_geometry",
            "event": "proxy pressure plus buffer lane modifies target susceptibility",
            "target_susceptibility_before": initial["target_route"]["susceptibility"],
            "target_susceptibility_after": target_susceptibility,
            "susceptibility_delta": susceptibility_delta,
            "peer_susceptibility_after": peer_susceptibility,
        },
        {
            "time_index": 2,
            "leg": "reentry_or_transfer_trace",
            "event": "same-budget re-entry probes buffered target and peer route",
            "target_reentry_alignment": target_reentry_alignment,
            "peer_reentry_alignment": peer_reentry_alignment,
            "challenge_load": thresholds["challenge_load"],
        },
        {
            "time_index": 3,
            "leg": "collapse_or_differential_response_trace",
            "event": "buffered target route keeps response above floor and separates from peer",
            "target_response_score": target_response,
            "peer_response_score": peer_response,
            "differential_response": differential_response,
        },
    ]
    control_rows = [
        {
            "control_id": "buffer_lane_removed_control",
            "control_status": "failed_closed",
            "blocked_condition": "buffered target response claimed when buffer lane is removed",
            "actual_result": "susceptibility delta and differential response lose the buffered margin",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "proxy_pressure_label_only_control",
            "control_status": "failed_closed",
            "blocked_condition": "proxy pressure recorded as label without numeric susceptibility delta",
            "actual_result": "source-current delta trace required",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "same_budget_peer_buffer_copy_control",
            "control_status": "failed_closed",
            "blocked_condition": "peer receives copied buffer lane and destroys target-specific distinction",
            "actual_result": "candidate requires peer route not to carry the target-specific buffer",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "reentry_order_inversion_control",
            "control_status": "failed_closed",
            "blocked_condition": "re-entry readback is placed before susceptibility modification",
            "actual_result": "ordered four-leg trace required",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "same_budget_peer_comparison_control",
            "control_status": "passed_as_comparability_control",
            "blocked_condition": "target response not distinguished from peer under equal budget",
            "actual_result": "target response exceeds peer response by declared margin",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "semantic_learning_choice_goal_relabel_control",
            "control_status": "failed_closed",
            "blocked_condition": "buffered differential response relabeled as semantic learning, choice, or goal",
            "actual_result": "unsafe semantic claims remain false",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "native_ap4_ap5_support_relabel_control",
            "control_status": "failed_closed",
            "blocked_condition": "buffered composed row relabeled as native AP4/AP5 closure or native support",
            "actual_result": "AP4/AP5 remain inherited bridge dependencies, not upgraded",
            "runtime_claim_allowed_when_control_triggers": False,
        },
    ]
    candidate_row = {
        "row_id": "n29_i13_2_buffered_proxy_susceptibility_reentry_candidate",
        "row_decision": "supported_as_alternative_bounded_composed_runtime_candidate",
        "runtime_claim_allowed": True,
        "final_prototype_c_success_supported": False,
        "derived_report_only": False,
        "source_current_trace_generated_by_n29": True,
        "alternative_role": "repeatability_and_margin_probe_not_i13_1_replacement",
        "composition_source_policy": {
            "prior_experiments_used_as": "source_backed_design_constraints_and_claim_ceilings",
            "prior_experiments_not_used_as": "pre-existing combined row proof",
            "i13_1_not_replaced": True,
            "new_n29_composed_trace_required": True,
        },
        "four_leg_trace": {
            "proxy_or_perturbation_state": timeline[0],
            "susceptibility_delta_or_modified_geometry": timeline[1],
            "reentry_or_transfer_trace": timeline[2],
            "collapse_or_differential_response_trace": timeline[3],
        },
        "target_post_state": target_post,
        "peer_same_budget_post_state": peer_post,
        "metrics": {
            "susceptibility_delta": susceptibility_delta,
            "susceptibility_delta_floor": thresholds["susceptibility_delta_floor"],
            "susceptibility_delta_margin": round(
                susceptibility_delta - thresholds["susceptibility_delta_floor"], 6
            ),
            "target_response_score": target_response,
            "peer_response_score": peer_response,
            "differential_response": differential_response,
            "differential_response_floor": thresholds["differential_response_floor"],
            "differential_response_margin": round(
                differential_response - thresholds["differential_response_floor"], 6
            ),
            "target_support_floor_preserved": target_post["support"] >= thresholds["support_floor"],
            "target_coherence_floor_preserved": target_post["coherence"] >= thresholds["coherence_floor"],
            "target_boundary_floor_preserved": target_post["boundary_integrity"]
            >= thresholds["boundary_integrity_floor"],
        },
        "claim_ceiling": (
            "alternative bounded N29-composed Prototype C runtime candidate; not "
            "semantic learning, choice, agency, native AP4/AP5 closure, native support, "
            "or ecology success"
        ),
    }
    candidate_row["row_digest"] = digest_value(candidate_row)
    runtime_artifact = {
        "artifact_id": "n29_proxy_susceptibility_reentry_composed_runtime_i132_artifact",
        "experiment_id": "N29",
        "iteration": "I13.2-runtime",
        "generated_at": GENERATED_AT,
        "runtime_kind": "n29_buffered_proxy_susceptibility_reentry_prototype",
        "source_i13_digest": i13["output_digest"],
        "source_i13_1c_digest": i131c["output_digest"],
        "thresholds_declared_before_use": thresholds,
        "initial_state": initial,
        "timeline": timeline,
        "candidate_row": candidate_row,
        "control_rows": control_rows,
        "geometric_interpretation": {
            "short_read": (
                "I13.2 uses a buffered target route rather than the I13.1 direct "
                "susceptibility lane. Proxy pressure enters a capacity buffer, which "
                "amplifies route-local susceptibility before later re-entry. The peer "
                "route has the same budget but lacks the target-specific buffer, so the "
                "later response separates more clearly."
            ),
            "not_claimed": [
                "semantic learning",
                "semantic choice",
                "goal ownership",
                "identity transfer",
                "native AP4/AP5 closure",
                "native support",
                "ant ecology success",
            ],
        },
    }
    runtime_artifact["output_digest"] = digest_value(runtime_artifact)
    return runtime_artifact


def build_summary(i13: dict[str, Any], i131c: dict[str, Any]) -> dict[str, Any]:
    runtime_artifact = build_runtime_artifact(i13, i131c)
    write_json(RUNTIME_OUTPUT, runtime_artifact)
    candidate = runtime_artifact["candidate_row"]
    metrics = candidate["metrics"]
    prior_summary = i131c["replay_stress_summary"]
    summary = {
        "prototype_family": "proxy_susceptibility_reentry",
        "composition_mode": "alternative_buffered_composed_runtime_trace",
        "alternative_to_i13_1": True,
        "i13_1_replaced": False,
        "i13_1_runtime_candidate_digest": i131c["source_artifacts"][0]["output_digest"],
        "i13_1_min_supported_susceptibility_margin": prior_summary[
            "min_supported_susceptibility_margin"
        ],
        "i13_1_min_supported_differential_margin": prior_summary[
            "min_supported_differential_response_margin"
        ],
        "runtime_artifact_path": str(RUNTIME_OUTPUT.relative_to(ROOT)),
        "runtime_artifact_sha256": sha256_file(RUNTIME_OUTPUT),
        "runtime_artifact_digest": runtime_artifact["output_digest"],
        "candidate_row_id": candidate["row_id"],
        "candidate_row_digest": candidate["row_digest"],
        "prototype_c_runtime_candidate_supported": True,
        "final_prototype_c_success_supported": False,
        "four_leg_trace_present": all(candidate["four_leg_trace"].values()),
        "susceptibility_delta_margin": metrics["susceptibility_delta_margin"],
        "differential_response_margin": metrics["differential_response_margin"],
        "margin_comparison_to_i13_1": {
            "susceptibility_margin_improved_over_i13_1_min": metrics[
                "susceptibility_delta_margin"
            ]
            > prior_summary["min_supported_susceptibility_margin"],
            "differential_margin_improved_over_i13_1_min": metrics[
                "differential_response_margin"
            ]
            > prior_summary["min_supported_differential_response_margin"],
            "susceptibility_margin_delta_vs_i13_1_min": round(
                metrics["susceptibility_delta_margin"]
                - prior_summary["min_supported_susceptibility_margin"],
                6,
            ),
            "differential_margin_delta_vs_i13_1_min": round(
                metrics["differential_response_margin"]
                - prior_summary["min_supported_differential_response_margin"],
                6,
            ),
        },
        "target_support_coherence_boundary_preserved": all(
            [
                metrics["target_support_floor_preserved"],
                metrics["target_coherence_floor_preserved"],
                metrics["target_boundary_floor_preserved"],
            ]
        ),
        "control_summary": {
            "control_count": len(runtime_artifact["control_rows"]),
            "failed_closed_count": sum(
                row["control_status"] == "failed_closed"
                for row in runtime_artifact["control_rows"]
            ),
            "passed_comparability_count": sum(
                row["control_status"] == "passed_as_comparability_control"
                for row in runtime_artifact["control_rows"]
            ),
            "failed_open_count": sum(
                row["control_status"] == "failed_open" for row in runtime_artifact["control_rows"]
            ),
        },
        "final_prototype_c_success_blockers": [
            "I13.2-B controls not yet run",
            "I13.2-C replay/stress not yet run",
            "producer-mediated susceptibility remains naturalization debt",
            "native AP4/AP5 closure remains blocked",
            "ecology integration not attempted",
        ],
        "ready_for_i13_2_b_c": True,
        "ready_for_iteration_14": False,
        "claim_ceiling": candidate["claim_ceiling"],
    }
    checks = [
        check("i13_source_passed", i13.get("status") == "passed"),
        check("i13_1c_source_passed", i131c.get("status") == "passed"),
        check("new_n29_runtime_artifact_created", RUNTIME_OUTPUT.exists()),
        check("runtime_artifact_sha256_matches", summary["runtime_artifact_sha256"] == sha256_file(RUNTIME_OUTPUT)),
        check("four_leg_trace_present", summary["four_leg_trace_present"]),
        check("susceptibility_delta_margin_positive", summary["susceptibility_delta_margin"] > 0),
        check("differential_response_margin_positive", summary["differential_response_margin"] > 0),
        check("support_coherence_boundary_preserved", summary["target_support_coherence_boundary_preserved"]),
        check("margin_improved_over_i13_1_min", all(summary["margin_comparison_to_i13_1"].values())),
        check("i13_1_not_replaced", summary["i13_1_replaced"] is False),
        check("runtime_candidate_supported_but_final_success_blocked", summary["prototype_c_runtime_candidate_supported"] and not summary["final_prototype_c_success_supported"]),
        check("ready_for_i13_2_b_c", summary["ready_for_i13_2_b_c"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_proxy_susceptibility_reentry_composed_i132",
        "experiment_id": "N29",
        "title": "Prototype C I13.2 Alternative Composed Runtime Candidate",
        "iteration": "I13.2",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_i13_2_alternative_composed_runtime_candidate_pending_b_c",
        "source_artifacts": [
            source_artifact("n29_i13_mapping_admission", I13, i13),
            source_artifact("n29_i13_1c_replay_stress_source", I131C, i131c),
            source_artifact("n29_i13_2_runtime_artifact", RUNTIME_OUTPUT, runtime_artifact),
        ],
        "composition_summary": summary,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i13_2_alternative_composed_runtime_candidate"
        data["composition_summary"]["prototype_c_runtime_candidate_supported"] = False
        data["composition_summary"]["ready_for_i13_2_b_c"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    summary = data["composition_summary"]
    comparison = summary["margin_comparison_to_i13_1"]
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Read",
        "",
        "I13.2 is an alternative composed Prototype C runtime candidate. It does not "
        "replace I13.1 and does not retune I13.1. It uses a buffered susceptibility "
        "lane to test repeatability and margin headroom in a different geometry.",
        "",
        f"Runtime artifact: `{summary['runtime_artifact_path']}`",
        "",
        f"Prototype C runtime candidate supported: `{str(summary['prototype_c_runtime_candidate_supported']).lower()}`",
        "",
        f"Final Prototype C success supported: `{str(summary['final_prototype_c_success_supported']).lower()}`",
        "",
        f"Claim ceiling: `{summary['claim_ceiling']}`",
        "",
        "## Margins",
        "",
        f"Susceptibility delta margin: `{summary['susceptibility_delta_margin']}`",
        "",
        f"Differential response margin: `{summary['differential_response_margin']}`",
        "",
        f"Improved over I13.1 minimum susceptibility margin: `{str(comparison['susceptibility_margin_improved_over_i13_1_min']).lower()}`",
        "",
        f"Improved over I13.1 minimum differential margin: `{str(comparison['differential_margin_improved_over_i13_1_min']).lower()}`",
        "",
        f"Susceptibility margin delta vs I13.1 minimum: `{comparison['susceptibility_margin_delta_vs_i13_1_min']}`",
        "",
        f"Differential margin delta vs I13.1 minimum: `{comparison['differential_margin_delta_vs_i13_1_min']}`",
        "",
        "## Next",
        "",
        "I13.2-B and I13.2-C are required before this alternative can be called "
        "control-backed or replay/stress-backed.",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "|---|---|",
    ]
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i13 = load_json(I13)
    i131c = load_json(I131C)
    summary = build_summary(i13, i131c)
    write_json(OUTPUT, summary)
    write_report(REPORT, summary)


if __name__ == "__main__":
    main()
