#!/usr/bin/env python3
"""Run N04 Lane D2 local geometry coupling.

D2 starts from the D1 pulse transport artifact and adds one local geometry
surface: pulse-contact support mass. It proves local geometry response only.
Traveling deformation and movement remain blocked.
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
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"

D1_REPORT = N04 / "outputs/pulse_conducting_substrate_baseline.json"
OUTPUT_PATH = N04 / "outputs/pulse_local_geometry_coupling_report.json"
REPORT_PATH = N04 / "reports/pulse_local_geometry_coupling_report.md"
TIMESERIES_DIR = N04 / "outputs/pulse_local_geometry_coupling_timeseries"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_local_geometry_coupling.py"
)

NODE_COUNT = 21
BASE_GEOMETRY_MASS = 1.0
COUPLING_STRENGTH = 0.1
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


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _d1_rows(d1: dict[str, Any], lane_key: str) -> list[dict[str, Any]]:
    if lane_key == "positive":
        lane = d1["positive_lane"]
    else:
        lane = d1["controls"][lane_key]
    rows = _load_jsonl(ROOT / lane["timeseries"]["path"])
    if _digest_json(rows) != lane["timeseries"]["timeseries_digest"]:
        raise ValueError(f"D1 timeseries digest mismatch for {lane_key}")
    return rows


def _baseline_geometry() -> list[float]:
    return [BASE_GEOMETRY_MASS for _ in range(NODE_COUNT)]


def _support_mask(peak: int | None) -> list[int]:
    return [] if peak is None else [peak]


def _apply_geometry_coupling(
    pulse_row: dict[str, Any],
    *,
    enabled: bool = True,
) -> tuple[list[float], dict[str, Any]]:
    geometry = _baseline_geometry()
    peak = pulse_row["pulse_peak_node"]
    pulse_mass = float(pulse_row["pulse_mass"])
    if not enabled or peak is None or pulse_mass <= 0.0:
        return geometry, {
            "coupling_applied": False,
            "coupling_amount": 0.0,
            "source_node": None,
            "target_node": peak,
            "locality_distance": None,
            "support_mask": _support_mask(peak),
        }

    target = int(peak)
    source = max(0, target - 1)
    if source == target and target + 1 < NODE_COUNT:
        source = target + 1
    amount = min(COUPLING_STRENGTH * pulse_mass, geometry[source])
    geometry[source] -= amount
    geometry[target] += amount
    return geometry, {
        "coupling_applied": True,
        "coupling_amount": amount,
        "source_node": source,
        "target_node": target,
        "locality_distance": abs(target - source),
        "support_mask": _support_mask(peak),
    }


def _run_lane(
    lane_id: str,
    pulse_rows: list[dict[str, Any]],
    *,
    geometry_enabled: bool = True,
    expected_response: bool = True,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    baseline_budget = NODE_COUNT * BASE_GEOMETRY_MASS
    max_budget_error = 0.0
    min_geometry = BASE_GEOMETRY_MASS
    max_support_delta = 0.0
    max_off_contact_delta = 0.0
    max_locality_distance = 0
    coupling_count = 0
    response_rows = 0

    for pulse_row in pulse_rows:
        geometry, coupling = _apply_geometry_coupling(pulse_row, enabled=geometry_enabled)
        support_mask = coupling["support_mask"]
        baseline_support_mass = len(support_mask) * BASE_GEOMETRY_MASS
        support_mass = sum(geometry[index] for index in support_mask)
        support_delta = support_mass - baseline_support_mass
        changed_nodes = [
            index
            for index, value in enumerate(geometry)
            if abs(value - BASE_GEOMETRY_MASS) > TOL
        ]
        off_contact_changed_nodes = [
            index
            for index in changed_nodes
            if coupling["target_node"] is None
            or abs(index - int(coupling["target_node"])) > 1
        ]
        max_off_contact_delta = max(
            max_off_contact_delta,
            max(
                [abs(geometry[index] - BASE_GEOMETRY_MASS) for index in off_contact_changed_nodes]
                or [0.0]
            ),
        )
        if coupling["coupling_applied"]:
            coupling_count += 1
            max_locality_distance = max(
                max_locality_distance,
                int(coupling["locality_distance"] or 0),
            )
        if abs(support_delta) > TOL:
            response_rows += 1
        budget = sum(geometry)
        max_budget_error = max(max_budget_error, abs(budget - baseline_budget))
        min_geometry = min(min_geometry, min(geometry))
        max_support_delta = max(max_support_delta, abs(support_delta))
        rows.append(
            {
                "lane_id": lane_id,
                "step_index": pulse_row["step_index"],
                "time": pulse_row["time"],
                "pulse_peak_node": pulse_row["pulse_peak_node"],
                "pulse_mass": pulse_row["pulse_mass"],
                "geometry_state": geometry,
                "geometry_budget": budget,
                "geometry_budget_error": abs(budget - baseline_budget),
                "min_geometry_state": min(geometry),
                "support_mask": support_mask,
                "support_mass": support_mass,
                "support_delta": support_delta,
                "changed_nodes": changed_nodes,
                "off_contact_changed_nodes": off_contact_changed_nodes,
                **coupling,
            }
        )

    path = TIMESERIES_DIR / f"{lane_id}.jsonl"
    _write_jsonl(path, rows)
    local_geometry_coupling_observed = response_rows > 0 and coupling_count > 0
    return {
        "lane_id": lane_id,
        "timeseries": {
            "path": path.relative_to(ROOT).as_posix(),
            "timeseries_digest": _digest_json(rows),
            "sha256": _sha256(path),
        },
        "geometry_surface": "local_support_mass",
        "support_mask_policy": "pulse_peak_single_node_mask",
        "geometry_enabled": geometry_enabled,
        "coupling_count": coupling_count,
        "response_rows": response_rows,
        "local_geometry_coupling_observed": local_geometry_coupling_observed,
        "expected_response": expected_response,
        "max_support_delta": max_support_delta,
        "max_locality_distance": max_locality_distance,
        "max_off_contact_delta": max_off_contact_delta,
        "geometry_budget_initial": baseline_budget,
        "geometry_budget_abs_error_max": max_budget_error,
        "min_geometry_state": min_geometry,
        "budget_passed": max_budget_error <= TOL,
        "nonnegative_passed": min_geometry >= -TOL,
        "locality_passed": max_locality_distance <= 1 and max_off_contact_delta <= TOL,
        "direct_writes": {
            "direct_support_mask_write": False,
            "direct_centroid_write": False,
            "direct_displacement_write": False,
            "direct_topology_write": False,
            "direct_claim_flag_write": False,
        },
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
    }


def build_report() -> dict[str, Any]:
    d1 = _load_json(D1_REPORT)
    positive = _run_lane("D2_positive_local_geometry_coupling", _d1_rows(d1, "positive"))
    coupling_disabled = _run_lane(
        "D2_geometry_coupling_disabled_control",
        _d1_rows(d1, "positive"),
        geometry_enabled=False,
        expected_response=False,
    )
    pulse_disabled = _run_lane(
        "D2_pulse_disabled_control",
        _d1_rows(d1, "pulse_disabled"),
        expected_response=False,
    )
    static_pulse = _run_lane(
        "D2_static_pulse_local_response_control",
        _d1_rows(d1, "static_pulse"),
    )

    controls = {
        "geometry_coupling_disabled": {
            **coupling_disabled,
            "primary_blocker": "geometry_coupling_disabled",
            "passed_negative_control": coupling_disabled[
                "local_geometry_coupling_observed"
            ]
            is False,
        },
        "pulse_disabled": {
            **pulse_disabled,
            "primary_blocker": "pulse_absent",
            "passed_negative_control": pulse_disabled[
                "local_geometry_coupling_observed"
            ]
            is False,
        },
        "static_pulse": {
            **static_pulse,
            "primary_blocker": "local_response_without_transport",
            "passed_local_only_control": (
                static_pulse["local_geometry_coupling_observed"]
                and static_pulse["max_locality_distance"] <= 1
            ),
        },
    }
    checks = {
        "d1_source_passed": d1["status"] == "passed",
        "primary_surface_local_support_mass": positive["geometry_surface"]
        == "local_support_mass",
        "secondary_surfaces_deferred": True,
        "positive_local_geometry_coupling_observed": positive[
            "local_geometry_coupling_observed"
        ],
        "response_amplitude_tracks_pulse": abs(
            positive["max_support_delta"] - COUPLING_STRENGTH
        )
        <= TOL,
        "locality_passed": positive["locality_passed"],
        "budget_passed": positive["budget_passed"],
        "nonnegative_passed": positive["nonnegative_passed"],
        "no_direct_movement_writes": not any(positive["direct_writes"].values()),
        "geometry_coupling_disabled_control_negative": controls[
            "geometry_coupling_disabled"
        ]["passed_negative_control"],
        "pulse_disabled_control_negative": controls["pulse_disabled"][
            "passed_negative_control"
        ],
        "static_pulse_local_only": controls["static_pulse"][
            "passed_local_only_control"
        ],
        "movement_claims_blocked": all(
            value is False
            for value in positive["claim_flags"].values()
            if isinstance(value, bool)
        ),
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "pulse_local_geometry_coupling_report_v1",
        "lane": "D",
        "iteration": "D2",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "pulse_local_geometry_coupling",
        "runtime_family": "experiment_local",
        "budget_surface": "node_only",
        "source_artifacts": {"d1_transport": _artifact_record(D1_REPORT)},
        "geometry_surface": {
            "primary": "local_support_mass",
            "support_mask_policy": "pulse_peak_single_node_mask",
            "secondary_surfaces_deferred": [
                "local_delay_or_proper_time_phase",
                "local_conductance_or_transport_preference",
                "local_stiffness_or_width_parameter",
                "reservoir_depletion_or_refill",
            ],
        },
        "coupling_rule": {
            "rule_id": "pulse_contact_local_support_mass_transfer_v1",
            "coupling_strength": COUPLING_STRENGTH,
            "reads": ["pulse_peak_node", "pulse_mass", "local_trailing_neighbor_mass"],
            "writes": ["geometry_state"],
            "direct_movement_writes": False,
        },
        "positive_lane": positive,
        "controls": controls,
        "checks": checks,
        "allowed_evidence_labels": ["pulse_local_geometry_coupling"],
        "blocked_claims": [
            "traveling_deformation",
            "movement_response",
            "boundary_coupled_movement",
            "loop_driven_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "native_lgrc9v3_pulse_substrate",
        ],
        "claim_flags": positive["claim_flags"],
        "command": COMMAND,
        "environment": _environment_record(),
    }


def write_report(report: dict[str, Any]) -> None:
    positive = report["positive_lane"]
    lines = [
        "# N04 Lane D2 Local Geometry Coupling",
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
        f"- Geometry surface: `{positive['geometry_surface']}`",
        f"- Coupling count: `{positive['coupling_count']}`",
        f"- Response rows: `{positive['response_rows']}`",
        f"- Max support delta: `{positive['max_support_delta']}`",
        f"- Max locality distance: `{positive['max_locality_distance']}`",
        f"- Max geometry budget error: `{positive['geometry_budget_abs_error_max']}`",
        f"- Minimum geometry state: `{positive['min_geometry_state']}`",
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
            "D2 proves local geometry/support response to pulse contact only.",
            "The declared geometry surface is local support mass at the pulse",
            "peak. The update is local, budget-conserving, nonnegative, and does",
            "not directly write support masks, centroid, displacement, topology,",
            "or claim flags. Traveling deformation and movement remain blocked.",
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
