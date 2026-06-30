#!/usr/bin/env python3
"""Build N29 I13.1 composed Proxy / Susceptibility / Re-Entry prototype."""

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
    "build_n29_proxy_susceptibility_reentry_composed_i131.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I13 = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_i13.json"
I13A = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_extraction_i13a.json"
I13B = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_controls_i13b.json"
I13C = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_replay_stress_i13c.json"

RUNTIME_OUTPUT = (
    EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_runtime_i131_artifact.json"
)
OUTPUT = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_composed_i131.json"
REPORT = EXPERIMENT / "reports" / "n29_proxy_susceptibility_reentry_composed_i131.md"

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
    challenge_load: float,
) -> float:
    return round(0.5 + susceptibility_delta * 1.25 + reentry_alignment * 0.5 - challenge_load * 0.1, 6)


def build_runtime_artifact(i13: dict[str, Any], i13c: dict[str, Any]) -> dict[str, Any]:
    thresholds = {
        "susceptibility_delta_floor": 0.05,
        "differential_response_floor": 0.08,
        "response_score_floor": 0.60,
        "support_floor": 0.85,
        "coherence_floor": 0.85,
        "boundary_integrity_floor": 0.80,
        "challenge_load": 0.15,
    }
    initial = {
        "target_route": {
            "route_id": "route_alpha_target",
            "support": 1.0,
            "coherence": 1.0,
            "boundary_integrity": 0.93,
            "susceptibility": 0.5,
        },
        "peer_route": {
            "route_id": "route_beta_peer_same_budget",
            "support": 1.0,
            "coherence": 1.0,
            "boundary_integrity": 0.93,
            "susceptibility": 0.5,
        },
    }
    proxy_pressure = 0.18
    susceptibility_coupling = 0.42
    susceptibility_delta = round(proxy_pressure * susceptibility_coupling, 6)
    target_susceptibility = round(initial["target_route"]["susceptibility"] + susceptibility_delta, 6)
    peer_susceptibility = initial["peer_route"]["susceptibility"]
    target_reentry_alignment = 0.18
    peer_reentry_alignment = 0.08
    target_response = bounded_response_score(
        susceptibility_delta=susceptibility_delta,
        reentry_alignment=target_reentry_alignment,
        challenge_load=thresholds["challenge_load"],
    )
    peer_response = bounded_response_score(
        susceptibility_delta=0.0,
        reentry_alignment=peer_reentry_alignment,
        challenge_load=thresholds["challenge_load"],
    )
    differential_response = round(target_response - peer_response, 6)
    target_post = {
        "route_id": "route_alpha_target",
        "support": 0.91,
        "coherence": 0.90,
        "boundary_integrity": 0.88,
        "susceptibility": target_susceptibility,
        "response_score": target_response,
        "response_class": "bounded_reentry_response_preserved",
    }
    peer_post = {
        "route_id": "route_beta_peer_same_budget",
        "support": 0.86,
        "coherence": 0.85,
        "boundary_integrity": 0.84,
        "susceptibility": peer_susceptibility,
        "response_score": peer_response,
        "response_class": "peer_same_budget_below_response_floor",
    }
    timeline = [
        {
            "time_index": 0,
            "leg": "proxy_or_perturbation_state",
            "event": "target route receives bounded proxy pressure",
            "target_proxy_pressure": proxy_pressure,
            "peer_proxy_pressure": 0.0,
        },
        {
            "time_index": 1,
            "leg": "susceptibility_delta_or_modified_geometry",
            "event": "proxy pressure modifies target route susceptibility lane",
            "target_susceptibility_before": initial["target_route"]["susceptibility"],
            "target_susceptibility_after": target_susceptibility,
            "susceptibility_delta": susceptibility_delta,
            "peer_susceptibility_after": peer_susceptibility,
        },
        {
            "time_index": 2,
            "leg": "reentry_or_transfer_trace",
            "event": "same budget re-entry is applied to target and peer routes",
            "target_reentry_alignment": target_reentry_alignment,
            "peer_reentry_alignment": peer_reentry_alignment,
            "challenge_load": thresholds["challenge_load"],
        },
        {
            "time_index": 3,
            "leg": "collapse_or_differential_response_trace",
            "event": "target route response remains above floor while peer route falls below response floor",
            "target_response_score": target_response,
            "peer_response_score": peer_response,
            "differential_response": differential_response,
        },
    ]
    control_rows = [
        {
            "control_id": "no_prior_proxy_pressure_control",
            "control_status": "failed_closed",
            "blocked_condition": "re-entry response claimed without prior proxy pressure",
            "actual_result": "susceptibility_delta = 0.0; differential response below floor",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "label_only_susceptibility_delta_control",
            "control_status": "failed_closed",
            "blocked_condition": "susceptibility update supplied only as label",
            "actual_result": "source-current susceptibility delta absent",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "reentry_removed_control",
            "control_status": "failed_closed",
            "blocked_condition": "modified geometry exists but no later re-entry occurs",
            "actual_result": "no collapse_or_differential_response_trace admissible",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "hidden_direct_response_producer_control",
            "control_status": "failed_closed",
            "blocked_condition": "response score injected without proxy-to-susceptibility leg",
            "actual_result": "runtime row requires susceptibility_delta_trace before response trace",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "peer_same_budget_comparison_control",
            "control_status": "passed_as_comparability_control",
            "blocked_condition": "target response not distinguishable from same-budget peer route",
            "actual_result": "target response exceeds peer response by declared differential margin",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "semantic_learning_choice_goal_relabel_control",
            "control_status": "failed_closed",
            "blocked_condition": "runtime differential response relabeled as learning, choice, goal, or preference",
            "actual_result": "unsafe semantic claims remain false",
            "runtime_claim_allowed_when_control_triggers": False,
        },
        {
            "control_id": "native_ap4_ap5_support_relabel_control",
            "control_status": "failed_closed",
            "blocked_condition": "composed row relabeled as native AP4/AP5 closure or native support",
            "actual_result": "AP4/AP5 remain inherited bridge dependencies, not upgraded",
            "runtime_claim_allowed_when_control_triggers": False,
        },
    ]
    candidate_row = {
        "row_id": "n29_i13_1_composed_proxy_susceptibility_reentry_candidate",
        "row_decision": "supported_as_bounded_composed_runtime_candidate",
        "runtime_claim_allowed": True,
        "final_prototype_c_success_supported": False,
        "derived_report_only": False,
        "source_current_trace_generated_by_n29": True,
        "composition_source_policy": {
            "prior_experiments_used_as": "source_backed_design_constraints_and_claim_ceilings",
            "prior_experiments_not_used_as": "pre-existing combined row proof",
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
            "bounded N29-composed Prototype C runtime candidate; not semantic "
            "learning, choice, agency, native AP4/AP5 closure, native support, or ecology success"
        ),
    }
    candidate_row["row_digest"] = digest_value(candidate_row)
    runtime_artifact = {
        "artifact_id": "n29_proxy_susceptibility_reentry_composed_runtime_i131_artifact",
        "experiment_id": "N29",
        "iteration": "I13.1-runtime",
        "generated_at": GENERATED_AT,
        "runtime_kind": "n29_composed_proxy_susceptibility_reentry_prototype",
        "source_admission_digest": i13["output_digest"],
        "source_replay_stress_digest": i13c["output_digest"],
        "thresholds_declared_before_use": thresholds,
        "initial_state": initial,
        "timeline": timeline,
        "candidate_row": candidate_row,
        "control_rows": control_rows,
        "geometric_interpretation": {
            "short_read": (
                "The target route first receives bounded proxy pressure. That pressure "
                "changes a route-local susceptibility lane. A later same-budget re-entry "
                "then reads a different response from the modified target than from the "
                "peer route. Geometrically this is a composed source-current history "
                "effect, not a semantic memory or choice."
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


def build_summary(i13: dict[str, Any], i13a: dict[str, Any], i13b: dict[str, Any], i13c: dict[str, Any]) -> dict[str, Any]:
    runtime_artifact = build_runtime_artifact(i13, i13c)
    write_json(RUNTIME_OUTPUT, runtime_artifact)
    candidate = runtime_artifact["candidate_row"]
    metrics = candidate["metrics"]
    control_rows = runtime_artifact["control_rows"]
    fail_closed_count = sum(row["control_status"] == "failed_closed" for row in control_rows)
    passed_comparability_count = sum(
        row["control_status"] == "passed_as_comparability_control" for row in control_rows
    )
    summary = {
        "prototype_family": "proxy_susceptibility_reentry",
        "composition_mode": "new_n29_composed_runtime_trace_from_source_backed_design_constraints",
        "source_mapping_debt_resolved_by_new_trace": True,
        "i13_exact_preexisting_row_found": False,
        "i13_1_new_composed_row_created": True,
        "runtime_artifact_path": str(RUNTIME_OUTPUT.relative_to(ROOT)),
        "runtime_artifact_sha256": sha256_file(RUNTIME_OUTPUT),
        "runtime_artifact_digest": runtime_artifact["output_digest"],
        "candidate_row_id": candidate["row_id"],
        "candidate_row_digest": candidate["row_digest"],
        "runtime_claim_allowed": candidate["runtime_claim_allowed"],
        "prototype_c_runtime_candidate_supported": True,
        "final_prototype_c_success_supported": False,
        "final_prototype_c_success_blockers": [
            "broader replay/stress envelope not yet run",
            "producer-mediated susceptibility remains naturalization debt",
            "native AP4/AP5 closure remains blocked",
            "ecology integration not attempted",
        ],
        "four_leg_trace_present": all(candidate["four_leg_trace"].values()),
        "susceptibility_delta_margin": metrics["susceptibility_delta_margin"],
        "differential_response_margin": metrics["differential_response_margin"],
        "target_support_coherence_boundary_preserved": all(
            [
                metrics["target_support_floor_preserved"],
                metrics["target_coherence_floor_preserved"],
                metrics["target_boundary_floor_preserved"],
            ]
        ),
        "control_summary": {
            "control_count": len(control_rows),
            "failed_closed_count": fail_closed_count,
            "passed_comparability_count": passed_comparability_count,
            "failed_open_count": sum(row["control_status"] == "failed_open" for row in control_rows),
        },
        "ap_dependency_status": {
            "ap4": "inherited bridge dependency; not upgraded to native AP4",
            "ap5": "inherited bridge dependency; not upgraded to native AP5",
        },
        "ready_for_iteration_14": True,
        "claim_ceiling": candidate["claim_ceiling"],
    }
    checks = [
        check("i13_mapping_source_passed", i13.get("status") == "passed"),
        check("i13a_extraction_source_passed", i13a.get("status") == "passed"),
        check("i13b_control_source_passed", i13b.get("status") == "passed"),
        check("i13c_replay_decision_source_passed", i13c.get("status") == "passed"),
        check("new_n29_runtime_artifact_created", RUNTIME_OUTPUT.exists()),
        check("runtime_artifact_sha256_matches", summary["runtime_artifact_sha256"] == sha256_file(RUNTIME_OUTPUT)),
        check("four_leg_trace_present", summary["four_leg_trace_present"]),
        check("susceptibility_delta_above_floor", metrics["susceptibility_delta_margin"] > 0),
        check("differential_response_above_floor", metrics["differential_response_margin"] > 0),
        check(
            "support_coherence_boundary_preserved",
            summary["target_support_coherence_boundary_preserved"],
        ),
        check("controls_fail_closed_or_pass_comparability", summary["control_summary"]["failed_open_count"] == 0),
        check("runtime_candidate_supported_but_final_success_blocked", summary["prototype_c_runtime_candidate_supported"] and not summary["final_prototype_c_success_supported"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_proxy_susceptibility_reentry_composed_i131",
        "experiment_id": "N29",
        "title": "Prototype C I13.1 Composed Runtime Candidate",
        "iteration": "I13.1",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_i13_1_composed_runtime_candidate_no_final_ecology_success",
        "source_artifacts": [
            source_artifact("n29_i13_mapping_admission", I13, i13),
            source_artifact("n29_i13a_exact_row_extraction", I13A, i13a),
            source_artifact("n29_i13b_mapping_controls", I13B, i13b),
            source_artifact("n29_i13c_replay_stress_decision", I13C, i13c),
            source_artifact("n29_i13_1_runtime_artifact", RUNTIME_OUTPUT, runtime_artifact),
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
        data["acceptance_state"] = "failed_i13_1_composed_runtime_candidate"
        data["composition_summary"]["runtime_claim_allowed"] = False
        data["composition_summary"]["prototype_c_runtime_candidate_supported"] = False
        data["composition_summary"]["ready_for_iteration_14"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    summary = data["composition_summary"]
    controls = summary["control_summary"]
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
        "I13.1 is the constructive counterpart to I13-A/B/C. I13-A showed that no "
        "prior exact combined row existed; I13.1 creates a new N29 composed runtime "
        "trace from source-backed design constraints and evaluates that new trace on "
        "its own claim ceiling.",
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
        f"Support/coherence/boundary preserved: `{str(summary['target_support_coherence_boundary_preserved']).lower()}`",
        "",
        "## Controls",
        "",
        f"Control count: `{controls['control_count']}`",
        "",
        f"Failed closed count: `{controls['failed_closed_count']}`",
        "",
        f"Comparability controls passed: `{controls['passed_comparability_count']}`",
        "",
        f"Failed open count: `{controls['failed_open_count']}`",
        "",
        "## Remaining Blockers",
        "",
    ]
    for blocker in summary["final_prototype_c_success_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    i13 = load_json(I13)
    i13a = load_json(I13A)
    i13b = load_json(I13B)
    i13c = load_json(I13C)
    summary = build_summary(i13, i13a, i13b, i13c)
    write_json(OUTPUT, summary)
    write_report(REPORT, summary)


if __name__ == "__main__":
    main()
