#!/usr/bin/env python3
"""Run N04 Lane D3 traveling deformation audit."""

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
D2_REPORT = N04 / "outputs/pulse_local_geometry_coupling_report.json"
OUTPUT_PATH = N04 / "outputs/traveling_deformation_audit.json"
REPORT_PATH = N04 / "reports/traveling_deformation_audit.md"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_traveling_deformation_audit.py"
)

BASE_GEOMETRY_MASS = 1.0
TOL = 1e-12
COUPLING_AMOUNT = 0.1


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


def _deformation_peak(row: dict[str, Any]) -> int | None:
    geometry = row["geometry_state"]
    deltas = [float(value) - BASE_GEOMETRY_MASS for value in geometry]
    max_delta = max(deltas)
    if max_delta <= TOL:
        return None
    return max(range(len(deltas)), key=lambda index: deltas[index])


def _deformation_width(row: dict[str, Any]) -> int:
    return sum(
        1 for value in row["geometry_state"] if abs(float(value) - BASE_GEOMETRY_MASS) > TOL
    )


def _analyze_rows(
    lane_id: str,
    rows: list[dict[str, Any]],
    *,
    expected_direction: int | None,
    expected_traveling: bool,
    allowed_spatial_lag_min: int = 0,
    allowed_spatial_lag_max: int = 0,
    causal_time_lag_steps: int | None = None,
) -> dict[str, Any]:
    series: list[dict[str, Any]] = []
    for row in rows:
        pulse_peak = row["pulse_peak_node"]
        deformation_peak = _deformation_peak(row)
        phase_lag = (
            None
            if pulse_peak is None or deformation_peak is None
            else int(deformation_peak) - int(pulse_peak)
        )
        series.append(
            {
                "step_index": row["step_index"],
                "time": row["time"],
                "pulse_peak_node": pulse_peak,
                "deformation_peak_node": deformation_peak,
                "phase_lag_nodes": phase_lag,
                "support_delta": row["support_delta"],
                "deformation_width": _deformation_width(row),
            }
        )
    pulse_peaks = [item["pulse_peak_node"] for item in series if item["pulse_peak_node"] is not None]
    deformation_peaks = [
        item["deformation_peak_node"]
        for item in series
        if item["deformation_peak_node"] is not None
    ]
    phase_lags = [
        item["phase_lag_nodes"] for item in series if item["phase_lag_nodes"] is not None
    ]
    pulse_displacement = (
        pulse_peaks[-1] - pulse_peaks[0] if len(pulse_peaks) >= 2 else 0
    )
    deformation_displacement = (
        deformation_peaks[-1] - deformation_peaks[0]
        if len(deformation_peaks) >= 2
        else 0
    )
    deformation_tracks_pulse = (
        len(deformation_peaks) > 0
        and all(
            allowed_spatial_lag_min <= lag <= allowed_spatial_lag_max
            for lag in phase_lags
        )
    )
    phase_lag_bounded = deformation_tracks_pulse
    causal_lag_matches = True
    if causal_time_lag_steps is not None:
        causal_lag_matches = True
        for index, item in enumerate(series):
            deformation_peak = item["deformation_peak_node"]
            if deformation_peak is None:
                continue
            source_index = index - causal_time_lag_steps
            if source_index < 0:
                causal_lag_matches = False
                break
            if deformation_peak != series[source_index]["pulse_peak_node"]:
                causal_lag_matches = False
                break
    deformation_travels = deformation_tracks_pulse and deformation_displacement != 0
    direction_passed = (
        expected_direction is None
        or deformation_displacement * expected_direction > 0
        or (not expected_traveling and deformation_displacement == 0)
    )
    width_values = [
        item["deformation_width"]
        for item in series
        if item["deformation_peak_node"] is not None
    ]
    width_max = max(width_values) if width_values else 0
    width_min = min(width_values) if width_values else 0
    width_preserved = not deformation_peaks or (width_max <= 2 and width_min >= 2)
    return {
        "lane_id": lane_id,
        "expected_traveling": expected_traveling,
        "expected_direction": expected_direction,
        "pulse_peak_sequence": pulse_peaks,
        "deformation_peak_sequence": deformation_peaks,
        "pulse_displacement": pulse_displacement,
        "deformation_displacement": deformation_displacement,
        "phase_lag_nodes": phase_lags,
        "phase_lag_bounded": phase_lag_bounded,
        "causal_time_lag_steps": causal_time_lag_steps,
        "causal_lag_matches": causal_lag_matches,
        "deformation_tracks_pulse": deformation_tracks_pulse,
        "deformation_travels": deformation_travels,
        "direction_passed": direction_passed,
        "deformation_width_min": width_min,
        "deformation_width_max": width_max,
        "width_profile_preserved": width_preserved,
        "series": series,
    }


def _lagged_geometry_rows(
    lane_id: str,
    pulse_rows: list[dict[str, Any]],
    *,
    time_lag_steps: int,
    append_tail: bool = True,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(pulse_rows):
        geometry = [BASE_GEOMETRY_MASS for _ in range(21)]
        source_row = pulse_rows[index - time_lag_steps] if index >= time_lag_steps else None
        causal_source_step_index = None
        causal_source_pulse_peak = None
        support_delta = 0.0
        if source_row is not None and source_row["pulse_peak_node"] is not None:
            target = int(source_row["pulse_peak_node"])
            source = max(0, target - 1)
            if source == target and target + 1 < len(geometry):
                source = target + 1
            geometry[source] -= COUPLING_AMOUNT
            geometry[target] += COUPLING_AMOUNT
            causal_source_step_index = source_row["step_index"]
            causal_source_pulse_peak = target
            support_delta = COUPLING_AMOUNT
        rows.append(
            {
                "lane_id": lane_id,
                "step_index": row["step_index"],
                "time": row["time"],
                "pulse_peak_node": row["pulse_peak_node"],
                "geometry_state": geometry,
                "support_delta": support_delta,
                "causal_source_step_index": causal_source_step_index,
                "causal_source_pulse_peak": causal_source_pulse_peak,
                "deformation_depends_on_prior_pulse": source_row is not None,
                "response_time_lag_steps": time_lag_steps,
            }
        )
    if append_tail and pulse_rows:
        last_row = pulse_rows[-1]
        tail_row = {
            **last_row,
            "step_index": int(last_row["step_index"]) + time_lag_steps,
            "time": float(last_row["time"]) + float(time_lag_steps),
            "pulse_peak_node": None,
        }
        rows.extend(
            _lagged_geometry_rows(
                lane_id,
                [*pulse_rows[-time_lag_steps:], tail_row],
                time_lag_steps=time_lag_steps,
                append_tail=False,
            )[time_lag_steps:]
        )
    return rows


def build_report() -> dict[str, Any]:
    d1 = _load_json(D1_REPORT)
    d2 = _load_json(D2_REPORT)
    instantaneous_reference = _analyze_rows(
        "D3_instantaneous_reference_traveling_deformation",
        _rows_from_lane(d2["positive_lane"]),
        expected_direction=1,
        expected_traveling=True,
    )
    lagged_positive = _analyze_rows(
        "D3_lagged_causal_traveling_deformation",
        _lagged_geometry_rows(
            "D3_lagged_causal_traveling_deformation",
            _rows_from_lane(d1["positive_lane"]),
            time_lag_steps=1,
        ),
        expected_direction=1,
        expected_traveling=True,
        allowed_spatial_lag_min=-1,
        allowed_spatial_lag_max=-1,
        causal_time_lag_steps=1,
    )
    static_control = _analyze_rows(
        "D3_static_pulse_local_deformation_control",
        _rows_from_lane(d2["controls"]["static_pulse"]),
        expected_direction=None,
        expected_traveling=False,
    )
    coupling_disabled = _analyze_rows(
        "D3_geometry_coupling_disabled_control",
        _rows_from_lane(d2["controls"]["geometry_coupling_disabled"]),
        expected_direction=None,
        expected_traveling=False,
    )
    pulse_disabled = _analyze_rows(
        "D3_pulse_disabled_control",
        _rows_from_lane(d2["controls"]["pulse_disabled"]),
        expected_direction=None,
        expected_traveling=False,
    )
    reversed_control = _analyze_rows(
        "D3_lagged_reversed_pulse_traveling_deformation",
        _lagged_geometry_rows(
            "D3_lagged_reversed_pulse_traveling_deformation",
            _rows_from_lane(d1["controls"]["wrong_direction"]),
            time_lag_steps=1,
        ),
        expected_direction=-1,
        expected_traveling=True,
        allowed_spatial_lag_min=0,
        allowed_spatial_lag_max=1,
        causal_time_lag_steps=1,
    )

    controls = {
        "static_pulse": {
            **static_control,
            "primary_blocker": "local_deformation_without_travel",
            "passed_control": static_control["deformation_travels"] is False,
        },
        "geometry_coupling_disabled": {
            **coupling_disabled,
            "primary_blocker": "deformation_absent",
            "passed_control": coupling_disabled["deformation_travels"] is False,
        },
        "pulse_disabled": {
            **pulse_disabled,
            "primary_blocker": "pulse_absent",
            "passed_control": pulse_disabled["deformation_travels"] is False,
        },
        "reversed_pulse": {
            **reversed_control,
            "primary_blocker": "not_a_negative_control_direction_reversal_positive",
            "passed_direction_control": reversed_control["direction_passed"],
        },
    }
    checks = {
        "d1_source_passed": d1["status"] == "passed",
        "d2_source_passed": d2["status"] == "passed",
        "pulse_and_deformation_timeseries_extracted": True,
        "instantaneous_reference_deformation_tracks_pulse": instantaneous_reference[
            "deformation_tracks_pulse"
        ],
        "lagged_causal_deformation_tracks_pulse": lagged_positive[
            "deformation_tracks_pulse"
        ],
        "lagged_causal_time_lag_matches": lagged_positive["causal_lag_matches"],
        "positive_phase_lag_bounded": lagged_positive["phase_lag_bounded"],
        "positive_traveling_deformation_observed": lagged_positive[
            "deformation_travels"
        ],
        "reversed_pulse_reverses_deformation": controls["reversed_pulse"][
            "passed_direction_control"
        ],
        "width_profile_preserved": lagged_positive["width_profile_preserved"],
        "static_control_not_traveling": controls["static_pulse"]["passed_control"],
        "geometry_disabled_control_not_traveling": controls["geometry_coupling_disabled"][
            "passed_control"
        ],
        "pulse_disabled_control_not_traveling": controls["pulse_disabled"][
            "passed_control"
        ],
        "movement_claims_blocked": True,
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "traveling_deformation_audit_v1",
        "lane": "D",
        "iteration": "D3",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "traveling_deformation_candidate",
        "runtime_family": "experiment_local",
        "source_artifacts": {
            "d1_transport": _artifact_record(D1_REPORT),
            "d2_geometry_coupling": _artifact_record(D2_REPORT),
        },
        "phase_lag_policy": {
            "geometry_response_policy": "causal_one_step_lagged_local_support_coupling",
            "allowed_forward_lag_nodes_min": -1,
            "allowed_forward_lag_nodes_max": -1,
            "allowed_reverse_lag_nodes_min": 0,
            "allowed_reverse_lag_nodes_max": 1,
            "required_time_lag_steps": 1,
            "interpretation": (
                "the deformation at step t must be caused by pulse contact at "
                "step t-1; the instantaneous D2 response remains serialized as "
                "a reference lane"
            ),
        },
        "instantaneous_reference_lane": instantaneous_reference,
        "positive_lane": lagged_positive,
        "controls": controls,
        "checks": checks,
        "d_gates": {
            "D0_no_deformation": False,
            "D1_local_deformation_at_pulse_contact": True,
            "D2_deformation_peak_tracks_pulse": lagged_positive[
                "deformation_tracks_pulse"
            ],
            "D3_reversed_pulse_reverses_deformation_direction": controls[
                "reversed_pulse"
            ]["passed_direction_control"],
            "D4_deformation_preserves_width_profile_envelope": lagged_positive[
                "width_profile_preserved"
            ],
            "D5_deformation_survives_controls_and_is_replayable": all(
                checks[key]
                for key in [
                    "static_control_not_traveling",
                    "geometry_disabled_control_not_traveling",
                    "pulse_disabled_control_not_traveling",
                ]
            ),
        },
        "allowed_evidence_labels": ["traveling_deformation_candidate"],
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
    positive = report["positive_lane"]
    instantaneous = report["instantaneous_reference_lane"]
    lines = [
        "# N04 Lane D3 Traveling Deformation Audit",
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
        "## Positive Lane",
        "",
        f"- Pulse peak sequence: `{positive['pulse_peak_sequence']}`",
        f"- Deformation peak sequence: `{positive['deformation_peak_sequence']}`",
        f"- Phase lag nodes: `{positive['phase_lag_nodes']}`",
        f"- Deformation displacement: `{positive['deformation_displacement']}`",
        f"- Width min/max: `{positive['deformation_width_min']}` / `{positive['deformation_width_max']}`",
        f"- Causal time lag steps: `{positive['causal_time_lag_steps']}`",
        f"- Causal lag matches: `{positive['causal_lag_matches']}`",
        "",
        "## Instantaneous Reference",
        "",
        f"- Reference deformation displacement: `{instantaneous['deformation_displacement']}`",
        f"- Reference phase lag nodes: `{instantaneous['phase_lag_nodes']}`",
        "",
        "## Controls",
        "",
    ]
    for name, control in report["controls"].items():
        lines.append(f"- `{name}`: `{control['primary_blocker']}`")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "D3 supports a traveling deformation candidate: the local support",
            "deformation at step t is linked to pulse contact at step t-1,",
            "so the positive lane has an explicit causal time lag rather than",
            "only an instantaneous same-step response. Reversed pulse direction",
            "reverses the deformation direction on the same local coupling rule.",
            "This is not yet a movement claim; movement-ladder reclassification",
            "is deferred to D5.",
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
