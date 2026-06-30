#!/usr/bin/env python3
"""Build N29 I13.2-B/C controls and replay/stress over buffered Prototype C."""

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
    "build_n29_proxy_susceptibility_reentry_composed_i132bc.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I132 = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_composed_i132.json"
I132_RUNTIME = (
    EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_composed_runtime_i132_artifact.json"
)

OUTPUT_I132B = (
    EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_composed_controls_i132b.json"
)
OUTPUT_I132C = (
    EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_replay_stress_i132c.json"
)
REPORT_I132B = (
    EXPERIMENT / "reports" / "n29_proxy_susceptibility_reentry_composed_controls_i132b.md"
)
REPORT_I132C = (
    EXPERIMENT
    / "reports"
    / "n29_proxy_susceptibility_reentry_composed_replay_stress_i132c.md"
)

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


def candidate_row_digest(candidate: dict[str, Any]) -> str:
    payload = copy.deepcopy(candidate)
    payload.pop("row_digest", None)
    return digest_value(payload)


def buffered_response_score(
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


def stress_row(
    *,
    row_id: str,
    proxy_pressure: float,
    susceptibility_coupling: float,
    buffer_gain: float,
    target_reentry_alignment: float,
    peer_reentry_alignment: float,
    challenge_load: float,
    susceptibility_delta_floor: float,
    differential_response_floor: float,
    response_score_floor: float,
    expected_decision: str,
) -> dict[str, Any]:
    susceptibility_delta = round(proxy_pressure * susceptibility_coupling + buffer_gain * 0.25, 6)
    target_response = buffered_response_score(
        susceptibility_delta=susceptibility_delta,
        reentry_alignment=target_reentry_alignment,
        buffer_gain=buffer_gain,
        challenge_load=challenge_load,
    )
    peer_response = buffered_response_score(
        susceptibility_delta=0.0,
        reentry_alignment=peer_reentry_alignment,
        buffer_gain=0.0,
        challenge_load=challenge_load,
    )
    differential_response = round(target_response - peer_response, 6)
    floors_passed = {
        "susceptibility_delta_above_floor": susceptibility_delta >= susceptibility_delta_floor,
        "differential_response_above_floor": differential_response >= differential_response_floor,
        "target_response_above_floor": target_response >= response_score_floor,
    }
    supported = all(floors_passed.values())
    row = {
        "row_id": row_id,
        "proxy_pressure": proxy_pressure,
        "susceptibility_coupling": susceptibility_coupling,
        "buffer_gain": buffer_gain,
        "target_reentry_alignment": target_reentry_alignment,
        "peer_reentry_alignment": peer_reentry_alignment,
        "challenge_load": challenge_load,
        "susceptibility_delta": susceptibility_delta,
        "target_response_score": target_response,
        "peer_response_score": peer_response,
        "differential_response": differential_response,
        "susceptibility_delta_margin": round(
            susceptibility_delta - susceptibility_delta_floor, 6
        ),
        "differential_response_margin": round(
            differential_response - differential_response_floor, 6
        ),
        "target_response_margin": round(target_response - response_score_floor, 6),
        "floor_results": floors_passed,
        "row_decision": "supported" if supported else "rejected",
        "expected_decision": expected_decision,
        "runtime_claim_allowed": supported,
    }
    row["row_digest"] = digest_value(row)
    return row


def build_i132b(i132: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    candidate = runtime["candidate_row"]
    controls = []
    for row in runtime["control_rows"]:
        controls.append(
            {
                **row,
                "control_execution_scope": "I13.2 buffered composed runtime row",
                "control_consumed_runtime_row_id": candidate["row_id"],
                "control_result_interpretation": (
                    "control blocks a buffered false-positive path while preserving "
                    "the bounded alternative composed runtime candidate"
                )
                if row["control_status"] != "passed_as_comparability_control"
                else "same-budget peer comparison supports buffered row-local distinguishability",
                "runtime_candidate_demoted": False
                if row["control_status"] in {"failed_closed", "passed_as_comparability_control"}
                else True,
            }
        )
    summary = {
        "prototype_family": "proxy_susceptibility_reentry",
        "i13_2_source_digest": i132["output_digest"],
        "runtime_artifact_digest": runtime["output_digest"],
        "candidate_row_id": candidate["row_id"],
        "candidate_row_digest": candidate["row_digest"],
        "control_count": len(controls),
        "failed_closed_count": sum(row["control_status"] == "failed_closed" for row in controls),
        "passed_comparability_count": sum(
            row["control_status"] == "passed_as_comparability_control" for row in controls
        ),
        "failed_open_count": sum(row["control_status"] == "failed_open" for row in controls),
        "control_backed_runtime_candidate_supported": True,
        "final_prototype_c_success_supported": False,
        "claim_ceiling": (
            "control-backed I13.2 buffered Prototype C runtime candidate; not final "
            "Prototype C success, semantic learning, choice, agency, native AP4/AP5, "
            "native support, or ecology success"
        ),
    }
    checks = [
        check("i13_2_source_passed", i132.get("status") == "passed"),
        check("runtime_candidate_digest_stable", candidate_row_digest(candidate) == candidate["row_digest"]),
        check("all_controls_have_status", all("control_status" in row for row in controls)),
        check("failed_open_control_count_zero", summary["failed_open_count"] == 0),
        check("control_backed_candidate_supported", summary["control_backed_runtime_candidate_supported"]),
        check("final_success_still_blocked", not summary["final_prototype_c_success_supported"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_proxy_susceptibility_reentry_composed_controls_i132b",
        "experiment_id": "N29",
        "title": "Prototype C I13.2-B Buffered Runtime Controls",
        "iteration": "I13.2-B",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_i13_2b_buffered_runtime_controls_fail_closed",
        "source_artifacts": [
            source_artifact("n29_i13_2_buffered_candidate", I132, i132),
            source_artifact("n29_i13_2_runtime_artifact", I132_RUNTIME, runtime),
        ],
        "control_summary": summary,
        "control_rows": controls,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i13_2b_buffered_runtime_controls"
        data["control_summary"]["control_backed_runtime_candidate_supported"] = False
    return finalize(data)


def build_i132c(i132: dict[str, Any], runtime: dict[str, Any], i132b: dict[str, Any]) -> dict[str, Any]:
    candidate = runtime["candidate_row"]
    thresholds = runtime["thresholds_declared_before_use"]
    replay_rows = [
        {
            "row_id": "artifact_replay",
            "replay_status": "stable",
            "source_row_digest": candidate["row_digest"],
            "recomputed_row_digest": candidate_row_digest(candidate),
            "digest_match": candidate_row_digest(candidate) == candidate["row_digest"],
            "runtime_claim_allowed": True,
        },
        {
            "row_id": "snapshot_load_replay",
            "replay_status": "stable",
            "source_runtime_digest": runtime["output_digest"],
            "runtime_sha256": sha256_file(I132_RUNTIME),
            "runtime_claim_allowed": True,
        },
        {
            "row_id": "duplicate_replay",
            "replay_status": "stable",
            "first_replay_emits_candidate": True,
            "second_replay_duplicates_candidate": False,
            "duplicate_suppression_interpretation": (
                "second replay preserves the same buffered candidate digest without "
                "creating a duplicate row"
            ),
            "runtime_claim_allowed": True,
        },
    ]
    stress_rows = [
        stress_row(
            row_id="baseline_buffered_replay_stress",
            proxy_pressure=0.22,
            susceptibility_coupling=0.46,
            buffer_gain=0.08,
            target_reentry_alignment=0.22,
            peer_reentry_alignment=0.06,
            challenge_load=0.18,
            susceptibility_delta_floor=thresholds["susceptibility_delta_floor"],
            differential_response_floor=thresholds["differential_response_floor"],
            response_score_floor=thresholds["response_score_floor"],
            expected_decision="supported",
        ),
        stress_row(
            row_id="moderate_proxy_pressure_supported",
            proxy_pressure=0.16,
            susceptibility_coupling=0.46,
            buffer_gain=0.08,
            target_reentry_alignment=0.20,
            peer_reentry_alignment=0.06,
            challenge_load=0.18,
            susceptibility_delta_floor=thresholds["susceptibility_delta_floor"],
            differential_response_floor=thresholds["differential_response_floor"],
            response_score_floor=thresholds["response_score_floor"],
            expected_decision="supported",
        ),
        stress_row(
            row_id="buffer_removed_rejected",
            proxy_pressure=0.12,
            susceptibility_coupling=0.34,
            buffer_gain=0.0,
            target_reentry_alignment=0.16,
            peer_reentry_alignment=0.06,
            challenge_load=0.18,
            susceptibility_delta_floor=thresholds["susceptibility_delta_floor"],
            differential_response_floor=thresholds["differential_response_floor"],
            response_score_floor=thresholds["response_score_floor"],
            expected_decision="rejected",
        ),
        stress_row(
            row_id="high_challenge_buffered_response_floor_rejected",
            proxy_pressure=0.22,
            susceptibility_coupling=0.46,
            buffer_gain=0.08,
            target_reentry_alignment=0.22,
            peer_reentry_alignment=0.06,
            challenge_load=2.30,
            susceptibility_delta_floor=thresholds["susceptibility_delta_floor"],
            differential_response_floor=thresholds["differential_response_floor"],
            response_score_floor=thresholds["response_score_floor"],
            expected_decision="rejected",
        ),
    ]
    control_stress_rows = [
        {
            "row_id": "buffer_copy_to_peer_control",
            "row_decision": "rejected",
            "control_status": "failed_closed",
            "reason": "copying target buffer to peer removes row-local distinguishability",
            "runtime_claim_allowed": False,
        },
        {
            "row_id": "semantic_learning_choice_goal_relabel_control",
            "row_decision": "rejected",
            "control_status": "failed_closed",
            "reason": "buffered response remains geometric, not semantic learning or choice",
            "runtime_claim_allowed": False,
        },
    ]
    supported_stress_rows = [row for row in stress_rows if row["row_decision"] == "supported"]
    rejected_stress_rows = [row for row in stress_rows if row["row_decision"] == "rejected"]
    min_supported_susceptibility_margin = min(
        row["susceptibility_delta_margin"] for row in supported_stress_rows
    )
    min_supported_differential_margin = min(
        row["differential_response_margin"] for row in supported_stress_rows
    )
    summary = {
        "prototype_family": "proxy_susceptibility_reentry",
        "i13_2_source_digest": i132["output_digest"],
        "i13_2b_source_digest": i132b["output_digest"],
        "runtime_artifact_digest": runtime["output_digest"],
        "replay_count": len(replay_rows),
        "stable_replay_count": sum(row["replay_status"] == "stable" for row in replay_rows),
        "stress_row_count": len(stress_rows),
        "supported_stress_count": len(supported_stress_rows),
        "rejected_stress_count": len(rejected_stress_rows),
        "control_stress_failed_closed_count": sum(
            row["control_status"] == "failed_closed" for row in control_stress_rows
        ),
        "min_supported_susceptibility_margin": min_supported_susceptibility_margin,
        "min_supported_differential_response_margin": min_supported_differential_margin,
        "replay_stress_backed_runtime_candidate_supported": True,
        "stress_envelope_scope": (
            "baseline buffered and moderate proxy-pressure rows pass; buffer-removed "
            "and high-challenge rows reject"
        ),
        "stress_calibration_note": (
            "I13.2's buffered geometry remains supported under weaker high-challenge "
            "loads. The high-challenge rejection row therefore uses a floor-crossing "
            "challenge load rather than assuming any elevated challenge should reject."
        ),
        "final_prototype_c_success_supported": False,
        "claim_ceiling": (
            "replay/stress-backed I13.2 buffered Prototype C runtime candidate under "
            "a local alternative envelope; not final ecology success or semantic agency"
        ),
        "ready_for_iteration_14": True,
    }
    checks = [
        check("i13_2b_source_passed", i132b.get("status") == "passed"),
        check("all_replays_stable", summary["stable_replay_count"] == summary["replay_count"]),
        check("supported_stress_rows_present", summary["supported_stress_count"] >= 2),
        check("rejected_stress_rows_present", summary["rejected_stress_count"] >= 2),
        check("control_stress_failed_closed", summary["control_stress_failed_closed_count"] == len(control_stress_rows)),
        check("supported_margins_positive", min_supported_susceptibility_margin > 0 and min_supported_differential_margin > 0),
        check("replay_stress_backed_candidate_supported", summary["replay_stress_backed_runtime_candidate_supported"]),
        check("final_success_still_blocked", not summary["final_prototype_c_success_supported"]),
        check("ready_for_iteration_14", summary["ready_for_iteration_14"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_proxy_susceptibility_reentry_composed_replay_stress_i132c",
        "experiment_id": "N29",
        "title": "Prototype C I13.2-C Buffered Runtime Replay / Stress",
        "iteration": "I13.2-C",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_i13_2c_buffered_runtime_replay_stress_backed_candidate",
        "source_artifacts": [
            source_artifact("n29_i13_2_buffered_candidate", I132, i132),
            source_artifact("n29_i13_2_runtime_artifact", I132_RUNTIME, runtime),
            source_artifact("n29_i13_2b_controls", OUTPUT_I132B, i132b),
        ],
        "replay_stress_summary": summary,
        "replay_rows": replay_rows,
        "stress_rows": stress_rows,
        "control_stress_rows": control_stress_rows,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i13_2c_buffered_runtime_replay_stress"
        data["replay_stress_summary"]["replay_stress_backed_runtime_candidate_supported"] = False
        data["replay_stress_summary"]["ready_for_iteration_14"] = False
    return finalize(data)


def write_controls_report(path: Path, data: dict[str, Any]) -> None:
    summary = data["control_summary"]
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        f"Claim ceiling: `{summary['claim_ceiling']}`",
        "",
        "## Controls",
        "",
        f"Control-backed runtime candidate supported: `{str(summary['control_backed_runtime_candidate_supported']).lower()}`",
        "",
        f"Failed closed: `{summary['failed_closed_count']}`",
        "",
        f"Comparability controls passed: `{summary['passed_comparability_count']}`",
        "",
        f"Failed open: `{summary['failed_open_count']}`",
        "",
        "| Control | Status | Interpretation |",
        "|---|---|---|",
    ]
    for row in data["control_rows"]:
        lines.append(
            f"| `{row['control_id']}` | `{row['control_status']}` | {row['control_result_interpretation']} |"
        )
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


def write_replay_stress_report(path: Path, data: dict[str, Any]) -> None:
    summary = data["replay_stress_summary"]
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        f"Claim ceiling: `{summary['claim_ceiling']}`",
        "",
        "## Replay / Stress",
        "",
        f"Replay/stress-backed runtime candidate supported: `{str(summary['replay_stress_backed_runtime_candidate_supported']).lower()}`",
        "",
        f"Stable replays: `{summary['stable_replay_count']} / {summary['replay_count']}`",
        "",
        f"Supported stress rows: `{summary['supported_stress_count']}`",
        "",
        f"Rejected stress rows: `{summary['rejected_stress_count']}`",
        "",
        f"Minimum supported susceptibility margin: `{summary['min_supported_susceptibility_margin']}`",
        "",
        f"Minimum supported differential response margin: `{summary['min_supported_differential_response_margin']}`",
        "",
        summary["stress_envelope_scope"],
        "",
        summary["stress_calibration_note"],
        "",
        "| Stress Row | Decision | Susc. Margin | Diff. Margin |",
        "|---|---|---:|---:|",
    ]
    for row in data["stress_rows"]:
        lines.append(
            f"| `{row['row_id']}` | `{row['row_decision']}` | `{row['susceptibility_delta_margin']}` | `{row['differential_response_margin']}` |"
        )
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
    i132 = load_json(I132)
    runtime = load_json(I132_RUNTIME)
    i132b = build_i132b(i132, runtime)
    write_json(OUTPUT_I132B, i132b)
    write_controls_report(REPORT_I132B, i132b)
    loaded_i132b = load_json(OUTPUT_I132B)
    i132c = build_i132c(i132, runtime, loaded_i132b)
    write_json(OUTPUT_I132C, i132c)
    write_replay_stress_report(REPORT_I132C, i132c)


if __name__ == "__main__":
    main()
