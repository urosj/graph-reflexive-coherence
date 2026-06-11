#!/usr/bin/env python3
"""Run N04 Iteration 16-C high-shock corridor resilience probe."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"
SCRIPT_DIR = N04 / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_n04_iter16_corridor_transfer as iter16  # noqa: E402


ITER16B_PATH = N04 / "outputs/n04_iter16b_corridor_perturbation_probe.json"
OUTPUT_PATH = N04 / "outputs/n04_iter16c_high_shock_corridor_resilience.json"
REPORT_PATH = N04 / "reports/n04_iter16c_high_shock_corridor_resilience.md"
COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_n04_iter16c_high_shock_corridor_resilience.py"
)

PROBE_AMOUNTS = [0.175, 0.20, 0.25, 0.30, 0.35]
WINDOW_VARIANTS = [3, 4, 5]
EPSILON_BUDGET = 1e-12


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, str]:
    return {"path": _rel(path), "sha256": _sha256(path)}


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _run_git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _run_with_window(amount: float, window: int) -> dict[str, Any]:
    original_window = iter16.RECOVERY_WINDOW_CYCLES
    iter16.RECOVERY_WINDOW_CYCLES = window
    try:
        forward = iter16._run_corridor_direction(  # noqa: SLF001
            "forward",
            transfer_amount=amount,
        )
        reversed_ = iter16._run_corridor_direction(  # noqa: SLF001
            "reversed",
            transfer_amount=amount,
        )
    finally:
        iter16.RECOVERY_WINDOW_CYCLES = original_window
    lanes = [forward, reversed_]
    both_m6 = all(lane["m6_transfer_candidate_passed"] for lane in lanes)
    both_m5 = all(lane["m5_direction_control_passed"] for lane in lanes)
    both_m4 = all(lane["m4_boundary_response_passed"] for lane in lanes)
    return {
        "transfer_amount": amount,
        "recovery_window_cycles": window,
        "native_feedback_packet_amount": iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
        "required_boundary_recovery_load": 2.0 * amount,
        "available_recovery_load": (
            window * iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT
        ),
        "minimum_required_cycles_by_budget": math.ceil(
            (2.0 * amount) / iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT
        ),
        "m4_boundary_response_passed": both_m4,
        "m5_direction_control_passed": both_m5,
        "m6_transfer_candidate_passed": both_m6,
        "forward": {
            "recovery_scheduled_cycle_count": forward["recovery_scheduled_cycle_count"],
            "signed_pre_transfer_score": forward["signed_pre_transfer_score"],
            "signed_final_score": forward["signed_final_score"],
            "signed_pre_transfer_centroid_delta": forward[
                "signed_pre_transfer_centroid_delta"
            ],
            "signed_final_centroid_delta": forward["signed_final_centroid_delta"],
            "budget_abs_error": forward["budget_abs_error"],
            "nonnegative_gate_passed": forward["nonnegative_gate_passed"],
            "identity_shape_gates_passed": forward["identity_shape_gates_passed"],
            "reason_codes": [
                cycle["producer_reason_code"] for cycle in forward["recovery_cycles"]
            ],
        },
        "reversed": {
            "recovery_scheduled_cycle_count": reversed_["recovery_scheduled_cycle_count"],
            "signed_pre_transfer_score": reversed_["signed_pre_transfer_score"],
            "signed_final_score": reversed_["signed_final_score"],
            "signed_pre_transfer_centroid_delta": reversed_[
                "signed_pre_transfer_centroid_delta"
            ],
            "signed_final_centroid_delta": reversed_["signed_final_centroid_delta"],
            "budget_abs_error": reversed_["budget_abs_error"],
            "nonnegative_gate_passed": reversed_["nonnegative_gate_passed"],
            "identity_shape_gates_passed": reversed_["identity_shape_gates_passed"],
            "reason_codes": [
                cycle["producer_reason_code"] for cycle in reversed_["recovery_cycles"]
            ],
        },
    }


def _variant_summary(results: list[dict[str, Any]], window: int) -> dict[str, Any]:
    rows = [row for row in results if row["recovery_window_cycles"] == window]
    recoverable = [
        row["transfer_amount"] for row in rows if row["m6_transfer_candidate_passed"]
    ]
    m5 = [row["transfer_amount"] for row in rows if row["m5_direction_control_passed"]]
    m4 = [row["transfer_amount"] for row in rows if row["m4_boundary_response_passed"]]
    return {
        "recovery_window_cycles": window,
        "largest_m6_recoverable_perturbation": max(recoverable) if recoverable else None,
        "largest_m5_recoverable_perturbation": max(m5) if m5 else None,
        "largest_m4_recoverable_perturbation": max(m4) if m4 else None,
        "first_m6_failed_perturbation": next(
            (
                row["transfer_amount"]
                for row in rows
                if not row["m6_transfer_candidate_passed"]
            ),
            None,
        ),
    }


def build_report() -> dict[str, Any]:
    iter16b = _load_json(ITER16B_PATH)
    results = [
        _run_with_window(amount, window)
        for window in WINDOW_VARIANTS
        for amount in PROBE_AMOUNTS
    ]
    summaries = [_variant_summary(results, window) for window in WINDOW_VARIANTS]
    checks = {
        "iteration_16b_available": iter16b["status"] == "passed",
        "capacity_boundary_from_16b_confirmed": (
            iter16b["persistence_axis"][
                "largest_t6_candidate_recoverable_perturbation"
            ]
            == 0.15
        ),
        "window_variants_declared_before_run": True,
        "three_cycle_geometry_only_boundary_preserved": next(
            summary
            for summary in summaries
            if summary["recovery_window_cycles"] == 3
        )["largest_m6_recoverable_perturbation"]
        is None,
        "four_cycle_capacity_recovers_0_20": any(
            row["transfer_amount"] == 0.20
            and row["recovery_window_cycles"] == 4
            and row["m6_transfer_candidate_passed"]
            for row in results
        ),
        "five_cycle_capacity_recovers_0_25": any(
            row["transfer_amount"] == 0.25
            and row["recovery_window_cycles"] == 5
            and row["m6_transfer_candidate_passed"]
            for row in results
        ),
        "all_budget_and_shape_gates_pass": all(
            lane["budget_abs_error"] <= EPSILON_BUDGET
            and lane["nonnegative_gate_passed"]
            and lane["identity_shape_gates_passed"]
            for row in results
            for lane in (row["forward"], row["reversed"])
        ),
        "broader_claims_blocked": True,
    }
    status = "passed" if all(checks.values()) else "failed"
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_iter16c_high_shock_corridor_resilience_v1",
        "iteration": "16-C",
        "status": status,
        "runtime_family": "LGRC9V3",
        "execution_surface": "native_causal_pulse_substrate_surface",
        "movement_substrate": "S4_widened_chain_absorber_corridor_v1",
        "geometry_scope": "transferred_geometry",
        "substrate_class": "corridor",
        "input_iteration_16b": _artifact_record(ITER16B_PATH),
        "claim_ceiling": "s4_corridor_high_shock_capacity_requirement_probe",
        "probe_design": {
            "probe_kind": "capacity_requirement_for_high_shock_corridor_recovery",
            "geometry_only_boundary": "three_cycle_window_preserves_16b_0_15_limit",
            "capacity_variants": WINDOW_VARIANTS,
            "native_feedback_packet_amount": iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT,
            "boundary_recovery_load_model": "required_load = 2 * perturbation_amount",
            "allowed_claim": "capacity_requirement_evidence",
        },
        "discovery_note": {
            "finding": "corridor_high_shock_recovery_is_capacity_limited",
            "rule": "required_boundary_recovery_load = 2 * perturbation_amount",
            "available_capacity": "recovery_window_cycles * native_feedback_packet_amount",
            "default_capacity": (
                f"3 * {iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT} = "
                f"{3 * iter16.iter15b.native_m6.FEEDBACK_PACKET_AMOUNT}"
            ),
            "default_t6_candidate_boundary": 0.15,
            "first_above_boundary_failure": 0.175,
            "interpretation": (
                "The 0.175 failure is expected because it requires 0.35 "
                "boundary recovery load while the default three-cycle window "
                "supplies only 0.30. Larger shocks require declared capacity "
                "extension, not only different fixed corridor geometry."
            ),
        },
        "persistence_axis": {
            "persistence_level": "T6_candidate",
            "persistence_basis": "s4_corridor_high_shock_capacity_requirement",
            "three_cycle_reference_largest_t6_candidate_from_16b": (
                iter16b["persistence_axis"][
                    "largest_t6_candidate_recoverable_perturbation"
                ]
            ),
            "three_cycle_probe_above_boundary_largest_t6_candidate": next(
                summary
                for summary in summaries
                if summary["recovery_window_cycles"] == 3
            )["largest_m6_recoverable_perturbation"],
            "four_cycle_largest_t6_candidate": next(
                summary
                for summary in summaries
                if summary["recovery_window_cycles"] == 4
            )["largest_m6_recoverable_perturbation"],
            "five_cycle_largest_t6_candidate": next(
                summary
                for summary in summaries
                if summary["recovery_window_cycles"] == 5
            )["largest_m6_recoverable_perturbation"],
            "t6_full_claim_allowed": False,
            "t6_full_claim_blocker": "capacity_variants_change_recovery_window_and_are_single_corridor_fixture_only",
        },
        "variant_summaries": summaries,
        "probe_results": results,
        "interpretation": (
            "Iteration 16-C shows the 16-B high-shock boundary is a feedback "
            "capacity boundary under the declared three-cycle, 0.1-packet "
            "native feedback window. Geometry-only corridor changes do not "
            "lift the 0.15 T6-candidate limit. Extending serialized recovery "
            "capacity to four cycles recovers 0.20, and five cycles recovers "
            "0.25. This is capacity-requirement evidence for Iteration 17, not "
            "a full T6 or broad geometry-transfer claim."
        ),
        "go_no_go_for_iteration_17": {
            "iteration_17_allowed": status == "passed",
            "ring_transfer_guidance": (
                "ring transfer should declare whether it keeps the three-cycle "
                "capacity from 16-B or explicitly tests capacity-extended "
                "variants from 16-C"
            ),
        },
        "checks": checks,
        "claim_flags": {
            "native_m6": True,
            "native_m6_candidate_gate_passed": True,
            "movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "biological_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "unrestricted_movement_claim_allowed": False,
            "t6_claim_allowed": False,
            "broad_geometry_transfer_claim_allowed": False,
        },
        "blocked_claims": [
            "full_T6_general_persistence",
            "ring_transfer",
            "grid_transfer",
            "port_graph_transfer",
            "broad_geometry_transfer",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "biological_behavior",
            "agency",
            "identity_acceptance",
            "movement_inherited_from_n03",
            "unrestricted_movement",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "command": COMMAND,
        },
        "git": {
            "status_short": _run_git(["status", "--short"]),
            "head": _run_git(["rev-parse", "HEAD"]),
        },
        "next_iteration": "17_s1_ring_with_explicit_unwrap_policy",
    }


def write_report(report: dict[str, Any]) -> None:
    axis = report["persistence_axis"]
    lines = [
        "# N04 Iteration 16-C High-Shock Corridor Resilience",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Claim ceiling: `{report['claim_ceiling']}`",
        "",
        "Iteration 16-C probes whether the S4 corridor high-shock boundary is geometry-limited or capacity-limited.",
        "",
        "## T-Axis Summary",
        "",
        f"- persistence level: `{axis['persistence_level']}`",
        f"- persistence basis: `{axis['persistence_basis']}`",
        f"- three-cycle reference largest T6-candidate perturbation from 16-B: `{axis['three_cycle_reference_largest_t6_candidate_from_16b']}`",
        f"- three-cycle above-boundary probe largest T6-candidate perturbation: `{axis['three_cycle_probe_above_boundary_largest_t6_candidate']}`",
        f"- four-cycle largest T6-candidate perturbation: `{axis['four_cycle_largest_t6_candidate']}`",
        f"- five-cycle largest T6-candidate perturbation: `{axis['five_cycle_largest_t6_candidate']}`",
        f"- full T6 claim allowed: `{axis['t6_full_claim_allowed']}`",
        f"- full T6 blocker: `{axis['t6_full_claim_blocker']}`",
        "",
        report["interpretation"],
        "",
        "## Discovery Note",
        "",
        f"- finding: `{report['discovery_note']['finding']}`",
        f"- rule: `{report['discovery_note']['rule']}`",
        f"- available capacity: `{report['discovery_note']['available_capacity']}`",
        f"- default capacity: `{report['discovery_note']['default_capacity']}`",
        f"- first above-boundary failure: `{report['discovery_note']['first_above_boundary_failure']}`",
        "",
        report["discovery_note"]["interpretation"],
        "",
        "## Variant Summary",
        "",
        "| recovery cycles | largest M6/T6-candidate | largest M5 | largest M4 | first M6 failure |",
        "|---:|---:|---:|---:|---:|",
    ]
    for summary in report["variant_summaries"]:
        lines.append(
            "| "
            f"{summary['recovery_window_cycles']} | "
            f"{summary['largest_m6_recoverable_perturbation']} | "
            f"{summary['largest_m5_recoverable_perturbation']} | "
            f"{summary['largest_m4_recoverable_perturbation']} | "
            f"{summary['first_m6_failed_perturbation']} |"
        )
    lines.extend(["", "## Checks", ""])
    for key, value in report["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Go/No-Go", ""])
    for key, value in report["go_no_go_for_iteration_17"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Command",
            "",
            f"```bash\n{COMMAND}\n```",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
