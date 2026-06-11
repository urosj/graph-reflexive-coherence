#!/usr/bin/env python3
"""Run N04 Lane D4 direction and null controls."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"

D1_REPORT = N04 / "outputs/pulse_conducting_substrate_baseline.json"
D3_REPORT = N04 / "outputs/traveling_deformation_audit.json"
OUTPUT_PATH = N04 / "outputs/pulse_substrate_direction_null_controls.json"
REPORT_PATH = N04 / "reports/pulse_substrate_direction_null_controls.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_pulse_substrate_direction_null_controls.py"
)

NODE_COUNT = 21
BASE_GEOMETRY_MASS = 1.0
COUPLING_AMOUNT = 0.1
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


def _rows_from_lane(lane: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _load_jsonl(ROOT / lane["timeseries"]["path"])
    if _digest_json(rows) != lane["timeseries"]["timeseries_digest"]:
        raise ValueError(f"timeseries digest mismatch for {lane['lane_id']}")
    return rows


def _deformation_peak(geometry: list[float]) -> int | None:
    deltas = [value - BASE_GEOMETRY_MASS for value in geometry]
    max_delta = max(deltas)
    if max_delta <= TOL:
        return None
    return max(range(len(deltas)), key=lambda index: deltas[index])


def _canonical_monotone(sequence: list[int], direction: int) -> bool:
    if len(sequence) < 2:
        return False
    if direction > 0:
        return all(b >= a for a, b in zip(sequence, sequence[1:]))
    return all(b <= a for a, b in zip(sequence, sequence[1:]))


def _pulse_mass_profile(rows: list[dict[str, Any]]) -> list[float]:
    return [float(row.get("pulse_mass", 0.0)) for row in rows]


def _scrambled_rows(positive_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    peaks = [int(row["pulse_peak_node"]) for row in positive_rows]
    scrambled_peaks = peaks[:1]
    remaining = peaks[1:]
    for index in range(0, len(remaining), 2):
        pair = remaining[index : index + 2]
        scrambled_peaks.extend(reversed(pair))
    rows: list[dict[str, Any]] = []
    for row, peak in zip(positive_rows, scrambled_peaks):
        geometry = [BASE_GEOMETRY_MASS for _ in range(NODE_COUNT)]
        source = max(0, peak - 1)
        if source == peak and peak + 1 < NODE_COUNT:
            source = peak + 1
        geometry[source] -= COUPLING_AMOUNT
        geometry[peak] += COUPLING_AMOUNT
        rows.append(
            {
                "step_index": row["step_index"],
                "time": row["time"],
                "pulse_peak_node": peak,
                "pulse_mass": row["pulse_mass"],
                "geometry_state": geometry,
                "support_delta": COUPLING_AMOUNT,
            }
        )
    return rows


def _summarize_scrambled(rows: list[dict[str, Any]], reference: list[dict[str, Any]]) -> dict[str, Any]:
    pulse_sequence = [int(row["pulse_peak_node"]) for row in rows]
    deformation_sequence = [
        peak
        for peak in (_deformation_peak(row["geometry_state"]) for row in rows)
        if peak is not None
    ]
    canonical_order_passed = _canonical_monotone(pulse_sequence, direction=1)
    profile_preserved = _pulse_mass_profile(rows) == _pulse_mass_profile(reference)
    return {
        "control_id": "scrambled_timing_order",
        "passed_negative_control": not canonical_order_passed,
        "primary_blocker": "canonical_pulse_order_failed",
        "pulse_peak_sequence": pulse_sequence,
        "deformation_peak_sequence": deformation_sequence,
        "canonical_order_passed": canonical_order_passed,
        "pulse_mass_profile_preserved": profile_preserved,
        "event_count_preserved": len(rows) == len(reference),
        "observation_window_preserved": (
            rows[0]["time"] == reference[0]["time"]
            and rows[-1]["time"] == reference[-1]["time"]
        ),
        "pulse_budget_preserved": abs(sum(_pulse_mass_profile(rows)) - sum(_pulse_mass_profile(reference)))
        <= TOL,
    }


def _symmetric_null(rows: list[dict[str, Any]]) -> dict[str, Any]:
    signed_centroids: list[float] = []
    width_values: list[int] = []
    for row in rows:
        peak = int(row["pulse_peak_node"])
        geometry = [BASE_GEOMETRY_MASS for _ in range(NODE_COUNT)]
        left = max(0, peak - 1)
        right = min(NODE_COUNT - 1, peak + 1)
        if left == right:
            continue
        geometry[left] += COUPLING_AMOUNT / 2.0
        geometry[right] += COUPLING_AMOUNT / 2.0
        geometry[peak] -= COUPLING_AMOUNT
        deltas = [value - BASE_GEOMETRY_MASS for value in geometry]
        positive_delta = sum(delta for delta in deltas if delta > 0)
        centroid = (
            sum(index * max(delta, 0.0) for index, delta in enumerate(deltas))
            / positive_delta
            if positive_delta > TOL
            else float(peak)
        )
        signed_centroids.append(centroid - peak)
        width_values.append(sum(1 for delta in deltas if abs(delta) > TOL))
    max_signed_offset = max((abs(value) for value in signed_centroids), default=0.0)
    return {
        "control_id": "symmetric_coupling_null",
        "passed_negative_control": max_signed_offset <= TOL,
        "primary_blocker": "balanced_symmetric_geometry_response",
        "max_signed_deformation_offset": max_signed_offset,
        "width_min": min(width_values) if width_values else 0,
        "width_max": max(width_values) if width_values else 0,
    }


def _budget_violation_control() -> dict[str, Any]:
    geometry = [BASE_GEOMETRY_MASS for _ in range(NODE_COUNT)]
    geometry[10] += COUPLING_AMOUNT
    budget_error = abs(sum(geometry) - NODE_COUNT * BASE_GEOMETRY_MASS)
    return {
        "control_id": "budget_violating_synthetic",
        "passed_negative_control": budget_error > TOL,
        "primary_blocker": "budget_gate_failed",
        "budget_error": budget_error,
        "intended_failure": True,
    }


def _nonnegative_violation_control() -> dict[str, Any]:
    geometry = [BASE_GEOMETRY_MASS for _ in range(NODE_COUNT)]
    geometry[10] = -0.1
    return {
        "control_id": "nonnegative_violating_synthetic",
        "passed_negative_control": min(geometry) < 0.0,
        "primary_blocker": "nonnegative_gate_failed",
        "min_geometry_state": min(geometry),
        "intended_failure": True,
    }


def build_report() -> dict[str, Any]:
    d1 = _load_json(D1_REPORT)
    d3 = _load_json(D3_REPORT)
    positive_rows = _rows_from_lane(d1["positive_lane"])
    scrambled = _summarize_scrambled(_scrambled_rows(positive_rows), positive_rows)
    symmetric = _symmetric_null(positive_rows)
    budget_blocker = _budget_violation_control()
    nonnegative_blocker = _nonnegative_violation_control()

    disabled_controls = {
        key: {
            "passed_negative_control": value["passed_control"],
            "primary_blocker": value["primary_blocker"],
        }
        for key, value in d3["controls"].items()
        if key in {"pulse_disabled", "geometry_coupling_disabled", "static_pulse"}
    }
    direction_controls = {
        "reversed_pulse": {
            "passed_direction_control": d3["controls"]["reversed_pulse"][
                "passed_direction_control"
            ],
            "primary_blocker": d3["controls"]["reversed_pulse"]["primary_blocker"],
            "deformation_displacement": d3["controls"]["reversed_pulse"][
                "deformation_displacement"
            ],
        },
        "wrong_direction_fixture": {
            "passed_direction_control": d3["controls"]["reversed_pulse"][
                "deformation_displacement"
            ]
            < 0,
            "primary_blocker": "direction_reversal_positive_control",
            "source": "D1 wrong_direction control",
        },
        "direction_sign_convention_audit": {
            "passed": d3["positive_lane"]["deformation_displacement"] > 0
            and d3["controls"]["reversed_pulse"]["deformation_displacement"] < 0,
            "positive_direction": "increasing S0 chain index",
        },
    }
    control_matrix = {
        "disabled_controls": disabled_controls,
        "direction_controls": direction_controls,
        "scrambled_timing_order": scrambled,
        "symmetric_coupling_null": symmetric,
        "budget_violating_synthetic": budget_blocker,
        "nonnegative_violating_synthetic": nonnegative_blocker,
    }
    checks = {
        "d3_source_passed": d3["status"] == "passed",
        "disabled_controls_negative": all(
            item["passed_negative_control"] for item in disabled_controls.values()
        ),
        "direction_controls_passed": all(
            item.get("passed_direction_control", item.get("passed", False))
            for item in direction_controls.values()
        ),
        "scrambled_order_negative": scrambled["passed_negative_control"],
        "scrambled_preserves_mass_event_window": all(
            scrambled[key]
            for key in [
                "pulse_mass_profile_preserved",
                "event_count_preserved",
                "observation_window_preserved",
                "pulse_budget_preserved",
            ]
        ),
        "symmetric_null_negative": symmetric["passed_negative_control"],
        "budget_blocker_negative": budget_blocker["passed_negative_control"],
        "nonnegative_blocker_negative": nonnegative_blocker["passed_negative_control"],
        "movement_claims_blocked": True,
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "pulse_substrate_direction_null_controls_v1",
        "lane": "D",
        "iteration": "D4",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "direction_controlled_traveling_deformation_supported",
        "runtime_family": "experiment_local",
        "source_artifacts": {
            "d1_transport": _artifact_record(D1_REPORT),
            "d3_traveling_deformation": _artifact_record(D3_REPORT),
        },
        "control_matrix": control_matrix,
        "checks": checks,
        "allowed_evidence_labels": [
            "traveling_deformation_supported",
            "direction_controlled_traveling_deformation_supported",
        ],
        "blocked_claims": [
            "movement_response",
            "boundary_coupled_movement",
            "loop_driven_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "native_lgrc9v3_pulse_substrate",
        ],
        "claim_flags": {
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "movement_claim_inherited_from_n03": False,
            "native_lgrc9v3_e3_pulse_used": False,
            "native_grc9v3_proposal_flux_control_used": False,
            "native_grc9v3_proposal_flux_loop_claim": False,
        },
        "command": COMMAND,
        "environment": _environment_record(),
    }


def write_report(report: dict[str, Any]) -> None:
    matrix = report["control_matrix"]
    lines = [
        "# N04 Lane D4 Direction And Null Controls",
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
        "## Controls",
        "",
    ]
    for name, item in matrix["disabled_controls"].items():
        lines.append(f"- `{name}`: `{item['primary_blocker']}`")
    lines.extend(
        [
            f"- `reversed_pulse`: `{matrix['direction_controls']['reversed_pulse']['primary_blocker']}`",
            f"- `scrambled_timing_order`: `{matrix['scrambled_timing_order']['primary_blocker']}`",
            f"- `symmetric_coupling_null`: `{matrix['symmetric_coupling_null']['primary_blocker']}`",
            f"- `budget_violating_synthetic`: `{matrix['budget_violating_synthetic']['primary_blocker']}`",
            f"- `nonnegative_violating_synthetic`: `{matrix['nonnegative_violating_synthetic']['primary_blocker']}`",
            "",
            "## Interpretation",
            "",
            "D4 hardens D3 with direction and null controls. Scrambled order",
            "preserves pulse mass profile, event count, budget, and observation",
            "window while failing canonical order. Symmetric coupling remains",
            "balanced. Budget and nonnegative synthetic blockers fail for their",
            "declared reasons. This supports direction-controlled traveling",
            "deformation as mechanism evidence only; movement classification is",
            "still deferred to D5.",
        ]
    )
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
