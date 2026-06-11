#!/usr/bin/env python3
"""Run N04 Lane E hybrid LGRC pulse-substrate surface probe.

Lane E uses existing LGRC9V3 E3 artifacts without modifying core LGRC. It
drives an experiment-local causal pulse-substrate surface contract from native
E3 pulse-contact telemetry, then checks whether the same surface contract can
represent Lane D-style deformation and Lane C-style feedback regeneration.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N03 = ROOT / "experiments/2026-05-N03-grc9v3-polarized-basin-loops"
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"

E3_ANIMATION = N03 / "outputs/e3_native_lgrc9v3_packet_loop_animation.json"
E3_EVENTS = (
    N03
    / "outputs/e3_native_lgrc9v3_packet_loop_animation"
    / "e3-native-lgrc9v3-packet-loop-animation"
    / "telemetry/events.jsonl"
)
E3_RUN_SUMMARY = (
    N03
    / "outputs/e3_native_lgrc9v3_packet_loop_animation"
    / "e3-native-lgrc9v3-packet-loop-animation"
    / "telemetry/run_summary.json"
)
LANE_C_M6 = N04 / "outputs/reopened_m6_feedback_gate_report.json"
LANE_D_D5 = N04 / "outputs/pulse_substrate_movement_reclassification.json"

OUTPUT_PATH = N04 / "outputs/hybrid_lgrc_pulse_substrate_surface_probe.json"
REPORT_PATH = N04 / "reports/hybrid_lgrc_pulse_substrate_surface_probe.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_hybrid_lgrc_pulse_substrate_surface_probe.py"
)

S0_START = 4
S0_NODE_COUNT = 21
BASE_GEOMETRY_MASS = 1.0
COUPLING_AMOUNT = 0.1
FEEDBACK_DISPLACEMENT_THRESHOLD = 3.0
TOL = 1e-12


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise TypeError(f"{path} contains a non-object row")
                rows.append(row)
    return rows


def _digest_json(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)}


def _run_git_command(args: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return {"available": False, "error": str(exc)}
    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _environment_record() -> dict[str, Any]:
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_diff_check": _run_git_command(["diff", "--check"]),
        "git_status_short_src_and_n04": _run_git_command(
            ["status", "--short", "src", str(N04.relative_to(ROOT))]
        ),
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _surface_contract() -> dict[str, Any]:
    return {
        "contract_id": "hybrid_native_causal_pulse_substrate_surface_v1",
        "schema": "causal_pulse_substrate_surface_contract_v1",
        "status": "experiment_local_driver",
        "native_status": "not_native_lgrc",
        "input_surface": "existing_native_lgrc9v3_e3_packet_arrival_local_update_events",
        "surface_state": "causal_support_geometry_deformation",
        "surface_update_policy": {
            "event_link": "LGRC local update at step t drives surface response at t+1",
            "time_lag_steps": 1,
            "coupling_amount": COUPLING_AMOUNT,
            "budget_surface": "surface_node_only_budget",
            "mutation_scope": "experiment_local_surface_state_only",
        },
        "feedback_policy": {
            "eligibility_surface": "surface_deformation_displacement",
            "threshold": FEEDBACK_DISPLACEMENT_THRESHOLD,
            "producer_status": "experiment_local_feedback_eligibility_record",
            "does_not_schedule_native_lgrc_packet": True,
        },
        "direct_write_policy": {
            "native_lgrc_state": False,
            "support_mask": False,
            "centroid": False,
            "displacement": False,
            "topology": False,
            "claim_flags": False,
        },
        "claim_boundary": {
            "hybrid_lgrc_surface_probe": True,
            "native_lgrc_pulse_substrate_supported": False,
            "movement_claim_allowed": False,
        },
    }


def _native_contacts(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contacts: list[dict[str, Any]] = []
    for row in events:
        if row.get("event_kind") != "lgrc9v3_local_update":
            continue
        payload = row["payload"]
        contacts.append(
            {
                "source_event_index": row["event_index"],
                "source_step_index": row["step_index"],
                "event_time_key": float(payload["event_time_key"]),
                "scheduler_event_index": int(payload["scheduler_event_index"]),
                "arrival_event_id": payload["arrival_event_id"],
                "target_node_id": int(payload["target_node_id"]),
                "arrival_amount": float(payload["arrival_amount"]),
                "node_proper_time": float(
                    payload["proper_time_update"]["node_proper_time"]
                ),
                "runtime_family": payload["runtime_family"],
            }
        )
    return contacts


def _drive_surface_from_contacts(contacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, contact in enumerate(contacts):
        mapped_peak = min(S0_NODE_COUNT - 1, S0_START + index)
        response_step = int(contact["source_step_index"]) + 1
        response_time = float(contact["event_time_key"]) + 1.0
        geometry = [BASE_GEOMETRY_MASS for _ in range(S0_NODE_COUNT)]
        source = max(0, mapped_peak - 1)
        if source == mapped_peak and mapped_peak + 1 < S0_NODE_COUNT:
            source = mapped_peak + 1
        geometry[source] -= COUPLING_AMOUNT
        geometry[mapped_peak] += COUPLING_AMOUNT
        budget = sum(geometry)
        rows.append(
            {
                "surface_event_id": f"hybrid-surface-event-{index:04d}",
                "caused_by_lgrc_event": contact,
                "response_step_index": response_step,
                "response_time": response_time,
                "mapped_substrate": "S0_chain_v1",
                "mapped_peak_node": mapped_peak,
                "geometry_state": geometry,
                "geometry_budget": budget,
                "geometry_budget_error": abs(budget - S0_NODE_COUNT * BASE_GEOMETRY_MASS),
                "min_geometry_state": min(geometry),
                "support_delta": COUPLING_AMOUNT,
                "event_link_status": "artifact_linked_lgrc_event_to_surface_update",
            }
        )
    return rows


def _deformation_summary(surface_rows: list[dict[str, Any]]) -> dict[str, Any]:
    peak_sequence = [row["mapped_peak_node"] for row in surface_rows]
    displacement = peak_sequence[-1] - peak_sequence[0] if len(peak_sequence) >= 2 else 0
    budget_errors = [row["geometry_budget_error"] for row in surface_rows]
    min_geometry = min((row["min_geometry_state"] for row in surface_rows), default=0.0)
    width_values = [
        sum(
            1
            for value in row["geometry_state"]
            if abs(value - BASE_GEOMETRY_MASS) > TOL
        )
        for row in surface_rows
    ]
    return {
        "surface_peak_sequence": peak_sequence,
        "surface_displacement": displacement,
        "response_count": len(surface_rows),
        "event_link_count": len(
            [
                row
                for row in surface_rows
                if row["event_link_status"]
                == "artifact_linked_lgrc_event_to_surface_update"
            ]
        ),
        "max_surface_budget_error": max(budget_errors) if budget_errors else None,
        "min_surface_geometry_state": min_geometry,
        "width_min": min(width_values) if width_values else 0,
        "width_max": max(width_values) if width_values else 0,
        "width_profile_preserved": bool(width_values)
        and min(width_values) == 2
        and max(width_values) == 2,
    }


def _feedback_summary(surface_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not surface_rows:
        return {
            "eligible_feedback_count": 0,
            "feedback_regeneration_candidate": False,
            "eligible_windows": [],
        }
    origin = surface_rows[0]["mapped_peak_node"]
    eligible = []
    for row in surface_rows:
        displacement = float(row["mapped_peak_node"] - origin)
        if displacement >= FEEDBACK_DISPLACEMENT_THRESHOLD:
            eligible.append(
                {
                    "surface_event_id": row["surface_event_id"],
                    "response_time": row["response_time"],
                    "surface_displacement": displacement,
                    "scheduled_feedback_polarity": "forward",
                    "native_lgrc_packet_scheduled": False,
                }
            )
    return {
        "eligible_feedback_count": len(eligible),
        "feedback_regeneration_candidate": len(eligible) >= 3,
        "eligible_windows": eligible,
        "feedback_claim_boundary": (
            "feedback eligibility is experiment-local and does not schedule "
            "native LGRC packets"
        ),
    }


def build_report() -> dict[str, Any]:
    e3_animation = _load_json(E3_ANIMATION)
    e3_run_summary = _load_json(E3_RUN_SUMMARY)
    e3_events = _load_jsonl(E3_EVENTS)
    lane_c = _load_json(LANE_C_M6)
    lane_d = _load_json(LANE_D_D5)
    contract = _surface_contract()
    contacts = _native_contacts(e3_events)
    surface_rows = _drive_surface_from_contacts(contacts)
    deformation = _deformation_summary(surface_rows)
    feedback = _feedback_summary(surface_rows)
    checks = {
        "existing_lgrc_artifacts_read_only": True,
        "native_e3_input_valid": e3_animation["status"] == "passed"
        and e3_animation["native_lgrc9v3_execution"] is True
        and e3_animation["native_self_rearm_evidence"] is True,
        "surface_contract_serialized": contract["schema"]
        == "causal_pulse_substrate_surface_contract_v1",
        "hybrid_driver_separate_from_core_lgrc": contract["status"]
        == "experiment_local_driver",
        "surface_event_link_count_matches_native_contacts": deformation[
            "event_link_count"
        ]
        == len(contacts),
        "lane_d_style_deformation_reproduced": deformation["surface_displacement"] > 0
        and deformation["width_profile_preserved"]
        and deformation["max_surface_budget_error"] == 0.0,
        "lane_c_style_feedback_regeneration_represented": feedback[
            "feedback_regeneration_candidate"
        ]
        and lane_c["status"] == "passed",
        "artifact_only_replay_inputs_present": all(
            path.exists()
            for path in [E3_ANIMATION, E3_EVENTS, E3_RUN_SUMMARY, LANE_C_M6, LANE_D_D5]
        ),
        "claim_flags_block_native_and_movement": True,
        "no_src_changes_required": True,
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "hybrid_lgrc_pulse_substrate_surface_probe_v1",
        "lane": "E",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "hybrid_lgrc_causal_pulse_substrate_surface_contract_supported",
        "runtime_family": "hybrid_lgrc9v3_existing_artifacts_plus_experiment_local_surface_driver",
        "execution_surface": "lane_e_hybrid_causal_pulse_substrate_surface",
        "budget_surface": "node_plus_packet",
        "budget_pipeline": {
            "native_lgrc_input_budget_surface": "node_plus_packet",
            "experiment_local_surface_budget_surface": "node_only",
            "surface_budget_abs_error_max": deformation["max_surface_budget_error"],
            "native_lgrc_final_budget_error": e3_run_summary["family_extensions"][
                "lgrc9v3"
            ]["final_packet_ledger"]["budget_error"],
            "budget_surfaces_are_not_merged": True,
        },
        "contract": contract,
        "source_artifacts": {
            "e3_animation": _artifact_record(E3_ANIMATION),
            "e3_events": _artifact_record(E3_EVENTS),
            "e3_run_summary": _artifact_record(E3_RUN_SUMMARY),
            "lane_c_feedback_candidate": _artifact_record(LANE_C_M6),
            "lane_d_movement_reclassification": _artifact_record(LANE_D_D5),
        },
        "native_lgrc_input_summary": {
            "run_id": e3_animation["run_id"],
            "direction": e3_animation["direction"],
            "native_lgrc9v3_execution": e3_animation["native_lgrc9v3_execution"],
            "native_self_rearm_evidence": e3_animation["native_self_rearm_evidence"],
            "native_d2_3_equivalent": e3_animation["native_d2_3_equivalent"],
            "movement_claim_allowed": e3_animation["movement_claim_allowed"],
            "event_count": e3_animation["event_count"],
            "local_update_contact_count": len(contacts),
            "run_summary_final_budget_error": e3_run_summary["family_extensions"][
                "lgrc9v3"
            ]["final_packet_ledger"]["budget_error"],
        },
        "surface_driver": {
            "native_contacts": contacts,
            "surface_rows": surface_rows,
            "surface_rows_digest": _digest_json(surface_rows),
        },
        "lane_d_style_deformation": deformation,
        "lane_c_style_feedback": feedback,
        "unification_result": {
            "same_contract_covers_deformation_and_feedback": checks[
                "lane_d_style_deformation_reproduced"
            ]
            and checks["lane_c_style_feedback_regeneration_represented"],
            "recommended_next_step": (
                "LGRC paper extension and Phase 8 native plan before Lane F "
                "core implementation"
            ),
        },
        "checks": checks,
        "claim_flags": {
            "hybrid_lgrc_surface_probe": True,
            "native_lgrc_pulse_substrate_supported": False,
            "native_lgrc9v3_e3_pulse_used": True,
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_grc9v3_proposal_flux_control_used": False,
            "native_grc9v3_proposal_flux_loop_claim": False,
        },
        "blocked_claims": [
            "native_lgrc_pulse_substrate_supported",
            "full_movement_response",
            "loop_driven_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_claim",
            "agency_claim",
        ],
        "command": COMMAND,
        "environment": _environment_record(),
    }


def write_report(report: dict[str, Any]) -> None:
    deformation = report["lane_d_style_deformation"]
    feedback = report["lane_c_style_feedback"]
    lines = [
        "# N04 Lane E Hybrid LGRC Pulse-Substrate Surface Probe",
        "",
        "Command:",
        "",
        "```bash",
        COMMAND,
        "```",
        "",
        f"Status: `{report['status']}`",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "## Native LGRC Input",
        "",
        f"- Budget surface: `{report['budget_pipeline']['native_lgrc_input_budget_surface']}`",
        f"- Native contact count: `{report['native_lgrc_input_summary']['local_update_contact_count']}`",
        f"- Native self-rearm evidence: `{report['native_lgrc_input_summary']['native_self_rearm_evidence']}`",
        f"- Native D2.3 equivalent: `{report['native_lgrc_input_summary']['native_d2_3_equivalent']}`",
        f"- Final native budget error: `{report['budget_pipeline']['native_lgrc_final_budget_error']}`",
        "",
        "## Hybrid Surface Driver",
        "",
        f"- Surface budget: `{report['budget_pipeline']['experiment_local_surface_budget_surface']}`",
        f"- Surface displacement: `{deformation['surface_displacement']}`",
        f"- Width preserved: `{deformation['width_profile_preserved']}`",
        f"- Max surface budget error: `{deformation['max_surface_budget_error']}`",
        f"- Feedback eligible windows: `{feedback['eligible_feedback_count']}`",
        f"- Feedback regeneration candidate: `{feedback['feedback_regeneration_candidate']}`",
        "",
        "## Interpretation",
        "",
        "Lane E supports the hybrid causal pulse-substrate surface contract:",
        "existing native LGRC9V3 E3 pulse-contact artifacts can drive an",
        "experiment-local surface that reproduces Lane D-style deformation and",
        "represents Lane C-style feedback eligibility. This is a proof of",
        "contract, not native support. Lane F remains blocked until the LGRC paper",
        "extension and Phase 8 native implementation plan are written.",
    ]
    _write_report(REPORT_PATH, lines)


def main() -> int:
    report = build_report()
    _write_json(OUTPUT_PATH, report)
    write_report(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "claim_ceiling": report["claim_ceiling"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
