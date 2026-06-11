#!/usr/bin/env python3
"""Run N04 Lane D1 pulse transport baseline.

D1 proves only local pulse transport on a simple substrate. Geometry coupling,
traveling deformation, movement, and native LGRC extension claims remain
blocked.
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

CONFIG_PATH = N04 / "configs/pulse_substrate_coupling_manifest_v1.json"
OUTPUT_PATH = N04 / "outputs/pulse_conducting_substrate_baseline.json"
REPORT_PATH = N04 / "reports/pulse_conducting_substrate_baseline.md"
TIMESERIES_DIR = N04 / "outputs/pulse_conducting_substrate_timeseries"

COMMAND = (
    ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/"
    "scripts/run_pulse_transport_baseline.py"
)

NODE_COUNT = 21
PULSE_MASS = 1.0
START_NODE = 4
RUN_STEPS = 10
TOL = 1e-12


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


def _build_config() -> dict[str, Any]:
    return {
        "schema": "pulse_substrate_coupling_manifest_v1",
        "runtime_family": "experiment_local",
        "substrate": {
            "fixture_id": "D1_s0_chain_pulse_transport_v1",
            "base_fixture": "S0_chain_v1",
            "type": "chain",
            "node_count": NODE_COUNT,
            "coordinate_policy": "chain_index",
            "coordinate_periodic": False,
            "edges": [
                {
                    "edge_id": index,
                    "u": index,
                    "v": index + 1,
                    "weight": 1.0,
                    "temporal_delay": 1.0,
                    "proper_time_delay": 1.0,
                }
                for index in range(NODE_COUNT - 1)
            ],
        },
        "pulse_state": {
            "state_surface": "separate_pulse_field",
            "initial_mass": PULSE_MASS,
            "initial_node": START_NODE,
            "initial_width": 1,
            "direction": "positive",
            "direction_vector": [1.0],
        },
        "geometry_state": {
            "enabled": False,
            "status": "unchanged_or_not_enabled",
        },
        "support_state": {
            "enabled": False,
            "status": "unchanged_or_not_enabled",
        },
        "transport_rule": {
            "rule_id": "deterministic_local_neighbor_shift_v1",
            "description": "At each step, pulse mass transfers from node i to i+1 through the local edge if present and unblocked.",
            "max_hop_distance": 1,
            "uses_preauthored_itinerary": False,
            "peak_source": "argmax_post_transfer_pulse_field",
            "transfer_fraction": 1.0,
        },
        "budget": {
            "budget_surface": "node_only",
            "pulse_budget": PULSE_MASS,
            "geometry_budget_mutated": False,
        },
        "claim_boundary": {
            "native_lgrc9v3_e3_pulse_used": False,
            "native_grc9v3_proposal_flux_control_used": False,
            "native_grc9v3_proposal_flux_loop_claim": False,
            "movement_claim_inherited_from_n03": False,
            "movement_claim_allowed": False,
            "boundary_coupled_movement_claim_allowed": False,
            "pulse_local_geometry_coupling_claim_allowed": False,
            "traveling_deformation_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
        },
    }


def _initial_field(*, mass: float = PULSE_MASS, node: int = START_NODE) -> list[float]:
    field = [0.0 for _ in range(NODE_COUNT)]
    if mass != 0.0:
        field[node] = mass
    return field


def _peak(field: list[float]) -> int | None:
    if max(field) <= 0.0:
        return None
    return max(range(len(field)), key=lambda index: field[index])


def _pulse_width(field: list[float]) -> int:
    return sum(1 for value in field if value > TOL)


def _step_transport(
    field: list[float],
    *,
    direction: int = 1,
    blocked_edges: set[tuple[int, int]] | None = None,
    static: bool = False,
) -> tuple[list[float], list[dict[str, Any]]]:
    blocked_edges = blocked_edges or set()
    next_field = [0.0 for _ in field]
    transfers: list[dict[str, Any]] = []
    for source, amount in enumerate(field):
        if amount <= 0.0:
            continue
        target = source if static else source + direction
        if target < 0 or target >= len(field) or (source, target) in blocked_edges:
            target = source
            blocked = True
        else:
            blocked = False
        next_field[target] += amount
        transfers.append(
            {
                "source": source,
                "target": target,
                "amount": amount,
                "hop_distance": abs(target - source),
                "blocked": blocked,
                "local_neighbor_transfer": abs(target - source) <= 1,
            }
        )
    return next_field, transfers


def _run_lane(
    lane_id: str,
    *,
    enabled: bool = True,
    static: bool = False,
    direction: int = 1,
    blocked_edges: set[tuple[int, int]] | None = None,
    budget_violation: bool = False,
) -> dict[str, Any]:
    field = _initial_field(mass=PULSE_MASS if enabled else 0.0)
    initial_budget = sum(field)
    rows: list[dict[str, Any]] = []
    max_hop = 0
    blocked_transfer_count = 0
    local_rule_violations = 0
    min_state = min(field)
    max_budget_error = 0.0

    for step_index in range(RUN_STEPS + 1):
        budget = sum(field)
        if budget_violation and step_index == 2:
            budget += 0.2
        max_budget_error = max(max_budget_error, abs(budget - initial_budget))
        min_state = min(min_state, min(field))
        rows.append(
            {
                "lane_id": lane_id,
                "step_index": step_index,
                "time": float(step_index),
                "pulse_field": field,
                "pulse_peak_node": _peak(field),
                "pulse_peak_source": "argmax_post_transfer_pulse_field",
                "pulse_width": _pulse_width(field),
                "pulse_peak_mass": max(field) if field else 0.0,
                "pulse_mass": sum(field),
                "reported_budget": budget,
                "budget_error": abs(budget - initial_budget),
                "min_pulse_state": min(field),
            }
        )
        if step_index == RUN_STEPS:
            break
        field, transfers = _step_transport(
            field,
            direction=direction,
            blocked_edges=blocked_edges,
            static=static,
        )
        for transfer in transfers:
            max_hop = max(max_hop, int(transfer["hop_distance"]))
            if transfer["blocked"]:
                blocked_transfer_count += 1
            if not transfer["local_neighbor_transfer"]:
                local_rule_violations += 1
    path = TIMESERIES_DIR / f"{lane_id}.jsonl"
    _write_jsonl(path, rows)
    peak_nodes = [row["pulse_peak_node"] for row in rows]
    distinct_peaks = [node for node in peak_nodes if node is not None]
    transported = (
        len(distinct_peaks) >= 2
        and distinct_peaks[-1] != distinct_peaks[0]
        and enabled
        and not static
    )
    expected_final = START_NODE + direction * RUN_STEPS if enabled and not static else START_NODE
    if enabled and not static and blocked_edges:
        expected_final = distinct_peaks[-1] if distinct_peaks else None
    pulse_widths = [int(row["pulse_width"]) for row in rows]
    pulse_peak_masses = [float(row["pulse_peak_mass"]) for row in rows]
    return {
        "lane_id": lane_id,
        "timeseries": {
            "path": path.relative_to(ROOT).as_posix(),
            "timeseries_digest": _digest_json(rows),
            "sha256": _sha256(path),
        },
        "transported": transported,
        "initial_peak_node": distinct_peaks[0] if distinct_peaks else None,
        "final_peak_node": distinct_peaks[-1] if distinct_peaks else None,
        "expected_final_peak_node": expected_final if enabled else None,
        "peak_sequence": peak_nodes,
        "peak_source": "argmax_post_transfer_pulse_field",
        "max_hop_distance": max_hop,
        "nonlocal_jump_detected": max_hop > 1 or local_rule_violations > 0,
        "blocked_transfer_count": blocked_transfer_count,
        "local_rule_violations": local_rule_violations,
        "pulse_budget_initial": initial_budget,
        "pulse_budget_final": sum(field),
        "pulse_budget_abs_error_max": max_budget_error,
        "max_budget_error": max_budget_error,
        "min_pulse_state": min_state,
        "pulse_width_max": max(pulse_widths) if pulse_widths else 0,
        "pulse_peak_mass_min": min(pulse_peak_masses) if pulse_peak_masses else 0.0,
        "pulse_profile_coherence_note": "transport_only_not_shape_claim",
        "nonnegative_passed": min_state >= -TOL,
        "budget_passed": max_budget_error <= TOL,
        "local_transport_passed": local_rule_violations == 0 and max_hop <= 1,
        "uses_preauthored_itinerary": False,
        "pulse_local_geometry_coupling_observed": False,
        "traveling_deformation_observed": False,
        "tracked_basin_identity_moved": False,
        "geometry_state": "unchanged_or_not_enabled",
        "support_state": "unchanged_or_not_enabled",
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
            "pulse_local_geometry_coupling_claim_allowed": False,
            "traveling_deformation_claim_allowed": False,
            "loop_driven_movement_claim_allowed": False,
            "locomotion_like_claim_allowed": False,
            "adaptive_topology_entry_allowed": False,
            "native_lgrc9v3_e3_pulse_used": False,
            "native_grc9v3_proposal_flux_control_used": False,
            "native_grc9v3_proposal_flux_loop_claim": False,
            "movement_claim_inherited_from_n03": False,
        },
    }


def build_report() -> dict[str, Any]:
    config = _build_config()
    _write_json(CONFIG_PATH, config)
    positive = _run_lane("D1_positive_local_transport")
    pulse_disabled = _run_lane("D1_pulse_disabled_control", enabled=False)
    static = _run_lane("D1_static_pulse_control", static=True)
    blocked = _run_lane(
        "D1_blocked_edge_control",
        blocked_edges={(8, 9)},
    )
    wrong_direction = _run_lane(
        "D1_wrong_direction_control",
        direction=-1,
    )
    budget_violation = _run_lane(
        "D1_budget_violating_synthetic_blocker",
        budget_violation=True,
    )
    controls = {
        "pulse_disabled": {
            **pulse_disabled,
            "primary_blocker": "pulse_absent",
            "passed_negative_control": pulse_disabled["transported"] is False,
            "negative_for_transport": pulse_disabled["transported"] is False,
        },
        "static_pulse": {
            **static,
            "primary_blocker": "no_propagation",
            "passed_negative_control": static["transported"] is False,
            "negative_for_transport": static["transported"] is False,
        },
        "blocked_edge": {
            **blocked,
            "primary_blocker": "local_transport_blocked",
            "passed_negative_control": blocked["final_peak_node"] != 14,
            "negative_for_full_path_transport": blocked["final_peak_node"] != 14,
        },
        "wrong_direction": {
            **wrong_direction,
            "primary_blocker": "wrong_direction_for_positive_path",
            "passed_negative_control": wrong_direction["final_peak_node"] != 14,
            "negative_for_positive_path_transport": wrong_direction["final_peak_node"] != 14,
        },
        "budget_violating_synthetic": {
            **budget_violation,
            "primary_blocker": "budget_gate_failed",
            "passed_negative_control": budget_violation["budget_passed"] is False,
            "negative_for_claim": budget_violation["budget_passed"] is False,
        },
    }
    checks = {
        "substrate_and_pulse_state_declared": True,
        "budget_surface_node_only": config["budget"]["budget_surface"] == "node_only",
        "local_transport_rule_declared": True,
        "positive_transport_observed": positive["transported"],
        "positive_final_peak_expected": positive["final_peak_node"] == 14,
        "no_nonlocal_jumps": positive["local_transport_passed"],
        "budget_conserved": positive["budget_passed"],
        "nonnegative": positive["nonnegative_passed"],
        "pulse_disabled_control_negative": controls["pulse_disabled"][
            "negative_for_transport"
        ],
        "static_pulse_control_negative": controls["static_pulse"][
            "negative_for_transport"
        ],
        "blocked_edge_control_negative": controls["blocked_edge"][
            "negative_for_full_path_transport"
        ],
        "wrong_direction_control_negative": controls["wrong_direction"][
            "negative_for_positive_path_transport"
        ],
        "budget_violation_blocked": controls["budget_violating_synthetic"][
            "negative_for_claim"
        ],
        "peak_source_is_field_argmax": positive["peak_source"]
        == "argmax_post_transfer_pulse_field",
        "pulse_state_separate_from_geometry_support": (
            positive["geometry_state"] == "unchanged_or_not_enabled"
            and positive["support_state"] == "unchanged_or_not_enabled"
        ),
        "no_direct_movement_writes": not any(positive["direct_writes"].values()),
        "does_not_update_n04_claim_ceiling": True,
        "native_m6_status_unchanged": True,
        "no_movement_claims": all(
            value is False
            for value in positive["claim_flags"].values()
            if isinstance(value, bool)
        ),
    }
    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "pulse_conducting_substrate_baseline_v1",
        "lane": "D",
        "iteration": "D1",
        "status": "passed" if all(checks.values()) else "failed",
        "claim_ceiling": "pulse_transport_only",
        "runtime_family": "experiment_local",
        "budget_surface": "node_only",
        "config": config,
        "updates_n04_claim_ceiling": False,
        "native_m6_status_changed": False,
        "positive_lane": positive,
        "controls": controls,
        "checks": checks,
        "allowed_evidence_labels": ["pulse_transport_only"],
        "blocked_claims": [
            "pulse_local_geometry_coupling",
            "traveling_deformation",
            "movement_response",
            "boundary_coupled_movement",
            "loop_driven_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "native_lgrc9v3_pulse_substrate",
        ],
        "source_artifacts": {"config": _artifact_record(CONFIG_PATH)},
        "command": COMMAND,
        "environment": _environment_record(),
    }


def write_report(report: dict[str, Any]) -> None:
    positive = report["positive_lane"]
    lines = [
        "# N04 Lane D1 Pulse Transport Baseline",
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
        f"- Peak sequence: `{positive['peak_sequence']}`",
        f"- Peak source: `{positive['peak_source']}`",
        f"- Final peak: `{positive['final_peak_node']}`",
        f"- Max hop distance: `{positive['max_hop_distance']}`",
        f"- Nonlocal jump detected: `{positive['nonlocal_jump_detected']}`",
        f"- Max budget error: `{positive['max_budget_error']}`",
        f"- Minimum pulse state: `{positive['min_pulse_state']}`",
        f"- Pulse width max: `{positive['pulse_width_max']}`",
        f"- Pulse peak mass min: `{positive['pulse_peak_mass_min']}`",
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
            "D1 proves only local pulse transport. The pulse peak advances by",
            "local one-hop transfers on the S0 chain with exact pulse-budget",
            "conservation and nonnegative state. Geometry coupling, traveling",
            "deformation, movement, loop-driven movement, and native LGRC pulse",
            "substrate claims remain blocked.",
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
